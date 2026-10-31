"""Ontologies Package for MedFactory."""
from medfactory.src.ontologies.base.ontology_models import (
    HPOTermRecord,
    ICD10Record,
    ATCSubstanceRecord,
    DiseasePhenotypeAssociation
)
from medfactory.src.ontologies.interfaces.ontology_interface import (
    IHPONodeIngestor,
    IClassificationIngestor
)
from medfactory.src.ontologies.implementations.hpo_ingestor import HPOIngestor
from medfactory.src.ontologies.implementations.icd10_atc_ingestor import ClassificationIngestor

__all__ = [
    "HPOTermRecord",
    "ICD10Record",
    "ATCSubstanceRecord",
    "DiseasePhenotypeAssociation",
    "IHPONodeIngestor",
    "IClassificationIngestor",
    "HPOIngestor",
    "ClassificationIngestor"
]
