from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from medfactory.src.ontologies.base.ontology_models import (
    HPOTermRecord,
    ICD10Record,
    ATCSubstanceRecord,
    DiseasePhenotypeAssociation
)


class IHPONodeIngestor(ABC):
    """Interfaccia formale per l'ingestione e analisi dell'ontologia HPO."""

    @abstractmethod
    def ingest_terms(self, source_obo_path: Optional[str] = None) -> List[HPOTermRecord]:
        """Ingerisce i termini HPO e ne calcola la chiusura transitiva degli antenati."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")

    @abstractmethod
    def compute_information_content(self, terms: List[HPOTermRecord], associations: List[DiseasePhenotypeAssociation]) -> Dict[str, float]:
        """Calcola l'Information Content (IC) per ciascun termine fenotipico."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")


class IClassificationIngestor(ABC):
    """Interfaccia formale per l'ingestione delle classificazioni cliniche ICD-10 e ATC."""

    @abstractmethod
    def ingest_icd10_catalog(self, source_file_path: Optional[str] = None) -> List[ICD10Record]:
        """Ingerisce la nosologia WHO ICD-10-CM."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")

    @abstractmethod
    def ingest_atc_catalog(self, source_file_path: Optional[str] = None) -> List[ATCSubstanceRecord]:
        """Ingerisce la classificazione farmaceutica WHO/AIFA ATC fino al Livello 5."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")
