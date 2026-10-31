import json
import shutil
import tarfile
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from cryptography.hazmat.primitives.asymmetric import ed25519
import zstandard as zstd

from medfactory.src.packager.interfaces.packager_interface import IMedPackAssembler
from medfactory.src.packager.base.manifest_models import (
    MedPackManifest,
    ChecksumRegister,
    StorageMetrics,
    MedicalStandardVersion,
    MedPackVerificationStatus
)
from medfactory.src.packager.base.medpack_hasher import (
    compute_file_blake3_hash,
    compute_file_sha256_hash,
    serialize_canonical_manifest_for_signing
)
from medfactory.src.packager.implementations.medpack_verifier import MedPackVerifier


class MedPackAssembler(IMedPackAssembler):
    """
    Assemblatore deterministico di archivi .medpack (ROA-18, ROA-19).
    Caratteristiche:
    - Normalizzazione metadati TAR (mtime=0, uid=0, gid=0, mode=0644/0755, uname='', gname='')
    - Ordinamento lessicografico dei membri
    - Compressione interna delle schede .md.zst tramite zstd.dict addestrato
    - Archivio TAR esterno compresso a Level 19 dictionary-free per eliminare deadlock circolari
    - Checksum completi BLAKE3 + SHA-256 su ogni singolo file
    - Firma digitale Ed25519 calcolata sui byte JSON canonici (sort_keys=True) dell'intero manifest.json
    """

    TRANSIENT_FILENAMES = {
        "transitional_archive.tar",
        "transitional_archive.tar.zst",
        "staging_tar_archive.tar",
    }

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calcola l'hash BLAKE3 a 64 caratteri esadecimali in streaming."""
        return compute_file_blake3_hash(file_path)

    def calculate_file_sha256(self, file_path: Path) -> str:
        """Calcola l'hash SHA-256 a 64 caratteri esadecimali in streaming."""
        return compute_file_sha256_hash(file_path)

    @staticmethod
    def serialize_canonical_manifest_for_signing(manifest_dictionary: Dict[str, Any]) -> bytes:
        """
        Restituisce i byte UTF-8 del JSON canonico (sort_keys=True, separatori compatti)
        con signature_ed25519 impostato a stringa vuota "".
        """
        return serialize_canonical_manifest_for_signing(manifest_dictionary)

    def _prepare_staging_hierarchy(self, staging_dir: Path, dictionary_bytes: bytes) -> Path:
        """Prepara zstd.dict, sincronizza database/module_kb.sqlite e comprime le schede .md.zst."""
        zstd_dict_file = staging_dir / "zstd.dict"
        zstd_dict_file.write_bytes(dictionary_bytes)

        root_sqlite = staging_dir / "module_kb.sqlite"
        nested_sqlite = staging_dir / "database" / "module_kb.sqlite"
        if root_sqlite.exists() and not nested_sqlite.exists():
            nested_sqlite.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root_sqlite, nested_sqlite)
        elif nested_sqlite.exists() and not root_sqlite.exists():
            shutil.copy2(nested_sqlite, root_sqlite)
        elif not root_sqlite.exists() and not nested_sqlite.exists():
            raise FileNotFoundError(f"Database SQLite richiesto mancante in: {staging_dir}")

        media_dir = staging_dir / "media"
        if media_dir.exists():
            for media_file in list(media_dir.glob("*.webp")) + list(media_dir.glob("*.svg")):
                computed_sha = self.calculate_file_sha256(media_file)
                if computed_sha.lower() != media_file.stem.lower():
                    raise ValueError(
                        f"Media file hash mismatch: filename={media_file.name}, computed_sha256={computed_sha}"
                    )

        assets_schede = staging_dir / "assets" / "schede_statiche"
        if assets_schede.exists():
            zstd_dict = zstd.ZstdCompressionDict(dictionary_bytes)
            comp_params = zstd.ZstdCompressionParameters.from_level(19, window_log=22)
            dict_compressor = zstd.ZstdCompressor(dict_data=zstd_dict, compression_params=comp_params)
            for md_path in sorted(assets_schede.glob("*.md")):
                compressed_md = dict_compressor.compress(md_path.read_bytes())
                md_zst_path = md_path.with_suffix(".md.zst")
                md_zst_path.write_bytes(compressed_md)

        return root_sqlite

    def _collect_all_file_hashes(
        self,
        staging_dir: Path
    ) -> Tuple[Dict[str, str], Dict[str, str], int]:
        """Calcola BLAKE3 e SHA-256 per ogni singolo file dell'archivio (esclusi manifest.json e manifest.sig)."""
        blake3_map: Dict[str, str] = {}
        sha256_map: Dict[str, str] = {}
        uncompressed_total = 0

        for entry_path in sorted(staging_dir.rglob("*"), key=lambda p: p.relative_to(staging_dir).as_posix()):
            if not entry_path.is_file():
                continue
            if entry_path.name in self.TRANSIENT_FILENAMES or entry_path.name in {"manifest.json", "manifest.sig"}:
                continue
            rel_key = entry_path.relative_to(staging_dir).as_posix()
            blake3_map[rel_key] = self.calculate_file_hash(entry_path)
            sha256_map[rel_key] = self.calculate_file_sha256(entry_path)
            uncompressed_total += entry_path.stat().st_size

        return blake3_map, sha256_map, uncompressed_total

    def build_medpack(
        self,
        staging_dir: Path,
        output_medpack_path: Path,
        dictionary_bytes: bytes,
        manifest_meta: Dict[str, Any],
        signing_private_key: Optional[ed25519.Ed25519PrivateKey] = None,
        private_key_ed25519: Optional[ed25519.Ed25519PrivateKey] = None
    ) -> MedPackManifest:
        """Costruisce e firma l'archivio .medpack in streaming (ROA-18, ROA-19)."""
        staging_dir = Path(staging_dir)
        output_medpack_path = Path(output_medpack_path)
        output_medpack_path.parent.mkdir(parents=True, exist_ok=True)

        signing_key = private_key_ed25519 or signing_private_key or ed25519.Ed25519PrivateKey.generate()
        public_key_hex = signing_key.public_key().public_bytes_raw().hex()

        self._prepare_staging_hierarchy(staging_dir, dictionary_bytes)

        manifest_file = staging_dir / "manifest.json"
        manifest_sig_file = staging_dir / "manifest.sig"

        empty_initial_manifest = MedPackManifest(
            schema_version="1.2.0",
            pack_id=manifest_meta["pack_id"],
            display_title=manifest_meta["display_title"],
            build_epoch_timestamp=0,
            compiler_toolchain="medfactory-dla-v1.4.2",
            standards=MedicalStandardVersion(
                hpo_release="2024-04-13",
                icd10_version="2019-v1",
                atc_index_year=2024
            ),
            storage=StorageMetrics(
                uncompressed_bytes=0,
                compressed_bytes=0,
                total_parent_chunks=manifest_meta.get("total_parent_chunks", 1),
                total_child_chunks=manifest_meta.get("total_child_chunks", 1),
                total_vectors=manifest_meta.get("total_vectors", 1)
            ),
            checksums=ChecksumRegister(
                module_kb_sqlite="0" * 64,
                zstd_dict="0" * 64
            ),
            checksums_blake3={},
            checksums_sha256={},
            public_key_ed25519=public_key_hex,
            signature_ed25519=""
        )
        manifest_file.write_text(empty_initial_manifest.model_dump_json(indent=2), encoding="utf-8")
        manifest_sig_file.write_text("0" * 128, encoding="utf-8")

        blake3_map, sha256_map, uncompressed_total = self._collect_all_file_hashes(staging_dir)

        checksum_register = ChecksumRegister(
            module_kb_sqlite=blake3_map.get("module_kb.sqlite") or blake3_map.get("database/module_kb.sqlite") or "0" * 64,
            zstd_dict=blake3_map.get("zstd.dict", "0" * 64),
            vector_index_bin=blake3_map.get("vector_index/index.bin"),
            vector_index_meta=blake3_map.get("vector_index/meta.bin"),
            media_manifest_cbor=blake3_map.get("media/media_manifest.cbor") or blake3_map.get("assets_media/media_manifest.cbor")
        )

        transitional_tar_path = staging_dir / "transitional_archive.tar"
        transitional_zst_path = staging_dir / "transitional_archive.tar.zst"

        try:
            self._write_deterministic_tar(staging_dir, transitional_tar_path)
            self._compress_tar_stream_outer(transitional_tar_path, transitional_zst_path)
            compressed_total = transitional_zst_path.stat().st_size

            final_storage = StorageMetrics(
                uncompressed_bytes=uncompressed_total,
                compressed_bytes=compressed_total,
                total_parent_chunks=manifest_meta.get("total_parent_chunks", 1),
                total_child_chunks=manifest_meta.get("total_child_chunks", 1),
                total_vectors=manifest_meta.get("total_vectors", 1)
            )

            unsigned_final_manifest = MedPackManifest(
                schema_version="1.2.0",
                pack_id=manifest_meta["pack_id"],
                display_title=manifest_meta["display_title"],
                build_epoch_timestamp=0,
                compiler_toolchain="medfactory-dla-v1.4.2",
                standards=MedicalStandardVersion(
                    hpo_release="2024-04-13",
                    icd10_version="2019-v1",
                    atc_index_year=2024
                ),
                storage=final_storage,
                checksums=checksum_register,
                checksums_blake3=blake3_map,
                checksums_sha256=sha256_map,
                public_key_ed25519=public_key_hex,
                signature_ed25519=""
            )

            canonical_bytes = self.serialize_canonical_manifest_for_signing(unsigned_final_manifest.model_dump())
            signature_hex = signing_key.sign(canonical_bytes).hex()

            final_manifest = MedPackManifest(
                schema_version="1.2.0",
                pack_id=manifest_meta["pack_id"],
                display_title=manifest_meta["display_title"],
                build_epoch_timestamp=0,
                compiler_toolchain="medfactory-dla-v1.4.2",
                standards=MedicalStandardVersion(
                    hpo_release="2024-04-13",
                    icd10_version="2019-v1",
                    atc_index_year=2024
                ),
                storage=final_storage,
                checksums=checksum_register,
                checksums_blake3=blake3_map,
                checksums_sha256=sha256_map,
                public_key_ed25519=public_key_hex,
                signature_ed25519=signature_hex
            )

            manifest_file.write_text(final_manifest.model_dump_json(indent=2), encoding="utf-8")
            manifest_sig_file.write_text(signature_hex, encoding="utf-8")

            self._write_deterministic_tar(staging_dir, transitional_tar_path)
            self._compress_tar_stream_outer(transitional_tar_path, output_medpack_path)
        finally:
            if transitional_tar_path.exists():
                transitional_tar_path.unlink()
            if transitional_zst_path.exists():
                transitional_zst_path.unlink()

        return final_manifest

    def _write_deterministic_tar(self, staging_dir: Path, output_tar_path: Path) -> None:
        """Scrive l'archivio TAR direttamente su file con metadati normalizzati e ordinamento lessicografico."""
        if output_tar_path.exists():
            output_tar_path.unlink()

        collected_entities: List[Tuple[str, Path]] = []
        for entry in staging_dir.rglob("*"):
            if entry.name in self.TRANSIENT_FILENAMES:
                continue
            rel_path = entry.relative_to(staging_dir).as_posix()
            collected_entities.append((rel_path, entry))

        collected_entities.sort(key=lambda pair: pair[0])

        with tarfile.open(name=str(output_tar_path), mode="w", format=tarfile.PAX_FORMAT) as tar_archive:
            for rel_path, abs_path in collected_entities:
                tar_info = tar_archive.gettarinfo(name=str(abs_path), arcname=rel_path)
                tar_info.mtime = 0
                tar_info.uid = 0
                tar_info.gid = 0
                tar_info.uname = ""
                tar_info.gname = ""

                if abs_path.is_dir():
                    tar_info.mode = 0o755
                    tar_archive.addfile(tar_info)
                else:
                    tar_info.mode = 0o644
                    with open(abs_path, "rb") as file_in:
                        tar_archive.addfile(tar_info, fileobj=file_in)

    def _compress_tar_stream_outer(self, input_tar_path: Path, output_zst_path: Path) -> None:
        """Comprime il TAR esterno a Level 19 dictionary-free per prevenire deadlock circolare (ROA-18)."""
        if output_zst_path.exists():
            output_zst_path.unlink()

        compression_parameters = zstd.ZstdCompressionParameters.from_level(19, window_log=22)
        compressor = zstd.ZstdCompressor(compression_params=compression_parameters)

        with open(input_tar_path, "rb") as f_tar, open(output_zst_path, "wb") as f_zst:
            compressor.copy_stream(f_tar, f_zst)

    def verify_medpack(
        self,
        medpack_path: Path,
        dictionary_bytes: Optional[bytes] = None,
        public_key_hex: Optional[str] = None
    ) -> MedPackVerificationStatus:
        """Delega la verifica al MedPackVerifier dedicato."""
        verifier = MedPackVerifier()
        return verifier.verify_medpack(
            medpack_path=medpack_path,
            dictionary_bytes=dictionary_bytes,
            public_key_hex=public_key_hex
        )
