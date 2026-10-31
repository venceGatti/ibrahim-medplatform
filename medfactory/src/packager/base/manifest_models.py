from typing import Dict, Optional, NamedTuple
from pydantic import BaseModel, Field, ConfigDict, model_validator


class MedPackVerificationStatus(NamedTuple):
    is_valid: bool
    diagnostic_message: str


class MedicalStandardVersion(BaseModel):
    model_config = ConfigDict(frozen=True)
    hpo_release: str = Field(description="Release version HPO (es. 2024-04-13)")
    icd10_version: str = Field(description="Versione WHO ICD-10 (es. 2019-v1)")
    atc_index_year: int = Field(ge=2020, description="Anno del catalogo ATC/DDD")


class ChecksumRegister(BaseModel):
    model_config = ConfigDict(frozen=True)
    module_kb_sqlite: str = Field(pattern=r"^[a-fA-F0-9]{64}$", description="BLAKE3 hash of module_kb.sqlite")
    zstd_dict: str = Field(pattern=r"^[a-fA-F0-9]{64}$", description="BLAKE3 hash of 114,688B zstd.dict")
    vector_index_bin: Optional[str] = Field(default=None, pattern=r"^[a-fA-F0-9]{64}$")
    vector_meta_bin: Optional[str] = Field(default=None, pattern=r"^[a-fA-F0-9]{64}$")
    assets_media_blob: Optional[str] = Field(default=None, pattern=r"^[a-fA-F0-9]{64}$")
    assets_media_manifest: Optional[str] = Field(default=None, pattern=r"^[a-fA-F0-9]{64}$")


class StorageMetrics(BaseModel):
    model_config = ConfigDict(frozen=True)
    uncompressed_bytes: int = Field(ge=0, description="Dimensione uncompressed in byte")
    compressed_bytes: int = Field(ge=0, description="Dimensione reale compresso Zstd in byte")
    total_parent_chunks: int = Field(gt=0, description="Numero di parent chunk")
    total_child_chunks: int = Field(gt=0, description="Numero di child chunk")
    total_vectors: int = Field(gt=0, description="Numero di vettori indicizzati")


class MedPackManifest(BaseModel):
    """
    Contratto formale unificato del manifest.json (ROA-19).
    Supporta sia gli identificatori canonici SRS sia gli alias di interoperabilità PROJECT.md.
    """
    model_config = ConfigDict(frozen=True)
    schema_version: str = Field(default="1.2.0", pattern=r"^\d+\.\d+\.\d+$")
    pack_version: Optional[str] = Field(default=None, description="Alias PROJECT.md per schema_version")
    pack_id: str = Field(pattern=r"^[a-z0-9_]{3,32}$", description="Identificatore univoco del modulo")
    module_id: Optional[str] = Field(default=None, description="Alias PROJECT.md per pack_id")
    display_title: str = Field(min_length=5, max_length=128)
    build_epoch_timestamp: int = Field(default=0, description="Fissato tassativamente a 0 per riproducibilità")
    build_timestamp: str = Field(default="1970-01-01T00:00:00Z", description="Timestamp ISO-8601 deterministico")
    compiler_toolchain: str = Field(description="Versione compiler (es. medfactory-dla-v1.4.2)")
    dla_engine_version: Optional[str] = Field(default=None, description="Alias PROJECT.md per compiler_toolchain")
    standards: MedicalStandardVersion
    storage: StorageMetrics
    checksums: ChecksumRegister
    checksums_blake3: Optional[Dict[str, str]] = Field(default=None, description="Mappa completa digest BLAKE3")
    checksums_sha256: Optional[Dict[str, str]] = Field(default=None, description="Mappa completa digest SHA-256")
    public_key_ed25519: Optional[str] = Field(default=None, description="Chiave pubblica Ed25519 esadecimale (64 char)")
    signature_ed25519: Optional[str] = Field(default=None, description="Firma digitale crittografica Ed25519")

    @model_validator(mode="after")
    def _populate_interoperability_aliases(self) -> "MedPackManifest":
        if self.module_id is None:
            object.__setattr__(self, "module_id", self.pack_id)
        if self.pack_version is None:
            object.__setattr__(self, "pack_version", self.schema_version)
        if self.dla_engine_version is None:
            object.__setattr__(self, "dla_engine_version", self.compiler_toolchain)
        if self.checksums_blake3 is None:
            default_blake3: Dict[str, str] = {
                "module_kb.sqlite": self.checksums.module_kb_sqlite,
                "zstd.dict": self.checksums.zstd_dict,
            }
            if self.checksums.vector_index_bin:
                default_blake3["vector_index/index.bin"] = self.checksums.vector_index_bin
            if self.checksums.vector_meta_bin:
                default_blake3["vector_index/meta.bin"] = self.checksums.vector_meta_bin
            object.__setattr__(self, "checksums_blake3", default_blake3)
        return self
