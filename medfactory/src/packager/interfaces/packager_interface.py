from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from medfactory.src.packager.base.manifest_models import MedPackManifest


class IMedPackAssembler(ABC):
    """Interfaccia formale per l'assemblaggio di archivi distributivi .medpack."""

    @abstractmethod
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calcola l'hash BLAKE3 a 64 caratteri esadecimali per il file specificato."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")

    @abstractmethod
    def calculate_file_sha256(self, file_path: Path) -> str:
        """Calcola l'hash crittografico SHA-256 a 64 caratteri esadecimali."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")

    @abstractmethod
    def build_medpack(
        self,
        staging_dir: Path,
        output_medpack_path: Path,
        dictionary_bytes: bytes,
        manifest_meta: Dict[str, Any]
    ) -> MedPackManifest:
        """Assembla, firma con Ed25519 e comprime lo streaming dell'archivio .medpack."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")

    @abstractmethod
    def verify_medpack(
        self,
        medpack_path: Path,
        dictionary_bytes: bytes,
        public_key_hex: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Verifica l'integrità crittografica, la decompressione e la firma dell'archivio."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")
