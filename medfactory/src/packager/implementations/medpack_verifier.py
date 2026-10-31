"""
Modulo di verifica crittografica formale per archivi .medpack (ROA-18, ROA-19).
Verifica streaming TAR dictionary-free, firma Ed25519, digest BLAKE3/SHA-256 e decompressibilità zstd.
"""

import json
import shutil
import tarfile
from pathlib import Path
from typing import Optional, Dict, Any
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature
import zstandard as zstd

from medfactory.src.packager.base.manifest_models import MedPackVerificationStatus
from medfactory.src.packager.base.medpack_hasher import (
    compute_file_blake3_hash,
    compute_file_sha256_hash,
    serialize_canonical_manifest_for_signing
)


class MedPackVerifier:
    """Verificatore di integrità e autenticità crittografica di archivi .medpack."""

    def verify_medpack(
        self,
        medpack_path: Path,
        dictionary_bytes: Optional[bytes] = None,
        public_key_hex: Optional[str] = None
    ) -> MedPackVerificationStatus:
        """
        Verifica crittograficamente l'archivio .medpack (ROA-18, ROA-19):
        1. Decompressione del contenitore esterno .tar.zst senza dipendenza circolare
        2. Validazione della firma Ed25519 sul payload JSON canonico di manifest.json
        3. Validazione di tutti i digest BLAKE3 e SHA-256 per ciascun file estratto
        4. Verifica della decompressione delle schede .md.zst tramite il dizionario zstd.dict interno
        """
        if not medpack_path.exists():
            return MedPackVerificationStatus(False, f"File archivio non trovato: {medpack_path}")

        staging_tar_archive_path = medpack_path.with_suffix(".verification_staging.tar")
        verification_extract_dir = medpack_path.parent / f".verify_{medpack_path.stem}"

        try:
            # 1. Decompressione dello stream Zstandard esterno
            try:
                outer_decompressor = zstd.ZstdDecompressor()
                with open(medpack_path, "rb") as f_in, open(staging_tar_archive_path, "wb") as f_out:
                    outer_decompressor.copy_stream(f_in, f_out)
            except zstd.ZstdError as zstd_err:
                if dictionary_bytes is not None:
                    try:
                        dict_decompressor = zstd.ZstdDecompressor(
                            dict_data=zstd.ZstdCompressionDict(dictionary_bytes)
                        )
                        with open(medpack_path, "rb") as f_in, open(staging_tar_archive_path, "wb") as f_out:
                            dict_decompressor.copy_stream(f_in, f_out)
                    except zstd.ZstdError as fallback_err:
                        return MedPackVerificationStatus(False, f"Decompressione Zstd fallita: {fallback_err}")
                else:
                    return MedPackVerificationStatus(False, f"Decompressione Zstd fallita: {zstd_err}")

            if verification_extract_dir.exists():
                shutil.rmtree(verification_extract_dir)
            verification_extract_dir.mkdir(parents=True, exist_ok=True)

            # 2. Estrazione sicura dell'archivio TAR
            try:
                with tarfile.open(name=str(staging_tar_archive_path), mode="r") as tar_handle:
                    archive_names = tar_handle.getnames()
                    if "manifest.json" not in archive_names:
                        return MedPackVerificationStatus(False, "manifest.json mancante nell'archivio.")
                    if "zstd.dict" not in archive_names:
                        return MedPackVerificationStatus(False, "zstd.dict mancante nell'archivio.")
                    for member in tar_handle.getmembers():
                        if ".." in Path(member.name).parts or member.name.startswith("/"):
                            return MedPackVerificationStatus(False, f"Percorso non sicuro nel TAR: {member.name}")
                    tar_handle.extractall(path=str(verification_extract_dir), filter="data")
            except (tarfile.TarError, OSError) as tar_err:
                return MedPackVerificationStatus(False, f"Archivio TAR corrotto: {tar_err}")

            # 3. Controllo coerenza zstd.dict
            extracted_dict_bytes = (verification_extract_dir / "zstd.dict").read_bytes()
            if dictionary_bytes is not None and extracted_dict_bytes != dictionary_bytes:
                return MedPackVerificationStatus(False, "Dizionario zstd.dict estratto non corrisponde a quello atteso.")

            # 4. Parsing manifest.json e verifica firma digitale Ed25519
            try:
                manifest_raw_bytes = (verification_extract_dir / "manifest.json").read_bytes()
                manifest_raw_text = manifest_raw_bytes.decode("utf-8")
                manifest_dict: Dict[str, Any] = json.loads(manifest_raw_text)
            except (UnicodeDecodeError, json.JSONDecodeError, OSError) as manifest_parse_err:
                return MedPackVerificationStatus(False, f"manifest.json non valido o corrotto: {manifest_parse_err}")

            signature_hex = manifest_dict.get("signature_ed25519") or ""
            if not signature_hex:
                return MedPackVerificationStatus(False, "Firma Ed25519 assente in manifest.json.")

            manifest_sig_path = verification_extract_dir / "manifest.sig"
            if manifest_sig_path.exists():
                try:
                    sig_file_content = manifest_sig_path.read_text(encoding="utf-8").strip()
                    if sig_file_content != signature_hex:
                        return MedPackVerificationStatus(False, "Discrepanza tra manifest.sig e signature_ed25519.")
                except (UnicodeDecodeError, OSError) as sig_read_err:
                    return MedPackVerificationStatus(False, f"manifest.sig illeggibile o corrotto: {sig_read_err}")

            effective_pub_key_hex = (
                public_key_hex if public_key_hex is not None else manifest_dict.get("public_key_ed25519")
            )
            if not effective_pub_key_hex:
                return MedPackVerificationStatus(False, "Chiave pubblica Ed25519 mancante per la verifica.")

            try:
                verifier_key = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(effective_pub_key_hex))
                canonical_bytes = serialize_canonical_manifest_for_signing(manifest_dict)
                verifier_key.verify(bytes.fromhex(signature_hex), canonical_bytes)
            except (InvalidSignature, ValueError, TypeError) as sig_err:
                return MedPackVerificationStatus(False, f"Verifica firma crittografica Ed25519 fallita: {sig_err}")

            # 5. Verifica integrità BLAKE3 e SHA-256 di ogni singolo file
            blake3_map: Dict[str, str] = manifest_dict.get("checksums_blake3") or {}
            sha256_map: Dict[str, str] = manifest_dict.get("checksums_sha256") or {}

            for rel_path, expected_blake3 in blake3_map.items():
                target_file = verification_extract_dir / rel_path
                if not target_file.exists():
                    return MedPackVerificationStatus(False, f"File mancante per verifica BLAKE3: {rel_path}")
                actual_blake3 = compute_file_blake3_hash(target_file)
                if actual_blake3.lower() != expected_blake3.lower():
                    return MedPackVerificationStatus(
                        False, f"BLAKE3 mismatch su {rel_path}: atteso {expected_blake3}, calcolato {actual_blake3}"
                    )

            for rel_path, expected_sha256 in sha256_map.items():
                target_file = verification_extract_dir / rel_path
                if not target_file.exists():
                    return MedPackVerificationStatus(False, f"File mancante per verifica SHA-256: {rel_path}")
                actual_sha256 = compute_file_sha256_hash(target_file)
                if actual_sha256.lower() != expected_sha256.lower():
                    return MedPackVerificationStatus(
                        False, f"SHA-256 mismatch su {rel_path}: atteso {expected_sha256}, calcolato {actual_sha256}"
                    )

            # 6. Verifica decompressione interna delle schede .md.zst con zstd.dict estratto
            schede_dir = verification_extract_dir / "assets" / "schede_statiche"
            if schede_dir.exists():
                inner_decompressor = zstd.ZstdDecompressor(
                    dict_data=zstd.ZstdCompressionDict(extracted_dict_bytes)
                )
                for zst_sheet in schede_dir.glob("*.md.zst"):
                    try:
                        decompressed_sheet = inner_decompressor.decompress(zst_sheet.read_bytes())
                        if not decompressed_sheet:
                            return MedPackVerificationStatus(
                                False, f"Scheda {zst_sheet.name} decompressa vuota non valida."
                            )
                        plain_sheet = zst_sheet.with_suffix("")
                        if plain_sheet.exists() and plain_sheet.read_bytes() != decompressed_sheet:
                            return MedPackVerificationStatus(
                                False, f"Contenuto decompresso non coincidente per {zst_sheet.name}"
                            )
                    except zstd.ZstdError as inner_err:
                        return MedPackVerificationStatus(
                            False, f"Fallita decompressione scheda interna {zst_sheet.name}: {inner_err}"
                        )

            return MedPackVerificationStatus(True, "Verifica crittografica .medpack completata con successo.")
        finally:
            if staging_tar_archive_path.exists():
                staging_tar_archive_path.unlink()
            if verification_extract_dir.exists():
                shutil.rmtree(verification_extract_dir)
