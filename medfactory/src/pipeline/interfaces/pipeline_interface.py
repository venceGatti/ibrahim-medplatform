from abc import ABC, abstractmethod
from pathlib import Path
from medfactory.src.packager.base.manifest_models import MedPackManifest


class IMedFactoryPipeline(ABC):
    """Interfaccia dell'orchestratore di build MedFactory."""

    @abstractmethod
    def build_module_pack(self, working_directory: Path, output_file_path: Path) -> MedPackManifest:
        """Esegue l'intera pipeline di build generando il pacchetto .medpack definitivo."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")
