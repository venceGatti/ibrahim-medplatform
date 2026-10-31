from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
from medfactory.src.dla.base.dla_models import (
    DocumentBoundingBox,
    ExtractedDocumentLayout,
    NormalizedTableMatrix,
    RawTableCell
)


class IDocumentLayoutAnalyzer(ABC):
    """Interfaccia formale per l'analisi del layout di documenti clinici."""

    @abstractmethod
    def sort_reading_order(self, text_boxes: List[DocumentBoundingBox]) -> List[DocumentBoundingBox]:
        """Ordina i blocchi testuali secondo la traiettoria topologica anti-cross-talk."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")

    @abstractmethod
    def normalize_ismp_units(self, text_content: str) -> str:
        """Normalizza le unità di misura critiche secondo gli standard ISMP."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")

    @abstractmethod
    def reconstruct_text(self, text_boxes: List[DocumentBoundingBox]) -> str:
        """Ricostruisce il testo ordinato e sanificato dai blocchi geometrici."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")


class ITableResolver(ABC):
    """Interfaccia formale per la risoluzione topologica di tabelle complesse."""

    @abstractmethod
    def resolve_grid(self, raw_matrix: List[List[RawTableCell]]) -> List[List[str]]:
        """Espande celle con rowspan/colspan in una matrice bidimensionale densa."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")

    @abstractmethod
    def to_canonical_markdown(self, resolved_matrix: List[List[str]], has_header: bool = True) -> str:
        """Converte la matrice densa in tabella conforme GitHub Flavored Markdown."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")


class IMedicalUnitScaleGuard(ABC):
    """Interfaccia per la validazione e sanificazione di unità posologiche critiche."""

    @abstractmethod
    def sanitize_dosage_units(self, raw_text: str) -> str:
        """Applica le regole ISMP per prevenire errori di dosaggio 1000x."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")

    @abstractmethod
    def validate_concentration_scale(self, metric_value: float, source_unit: str, target_unit: str) -> float:
        """Converte e valida la scalatura di concentrazione con controllo dei limiti fisiologici."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")
