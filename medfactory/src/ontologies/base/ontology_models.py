from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class HPOTermRecord:
    """Record strutturato per un termine della Human Phenotype Ontology."""
    hpo_id: str
    name: str
    definition: str
    ancestor_ids: List[str] = field(default_factory=list)
    information_content: float = 0.0

    def __post_init__(self) -> None:
        if not self.hpo_id.startswith("HP:"):
            raise ValueError(f"Identificatore HPO non valido (atteso prefisso 'HP:'): {self.hpo_id}")


@dataclass(frozen=True)
class ICD10Record:
    """Record strutturato per un codice nosologico ICD-10-CM."""
    icd10_code: str
    description: str
    chapter: str
    block_range: str
    is_leaf_code: bool = True

    def __post_init__(self) -> None:
        if not self.icd10_code:
            raise ValueError("icd10_code non puo' essere vuoto.")


@dataclass(frozen=True)
class ATCSubstanceRecord:
    """Record per una sostanza attiva classificata secondo ATC Livello 5."""
    atc_code: str
    substance_name: str
    level1_anatomical: str
    level2_therapeutic: str
    level3_pharmacological: str
    level4_chemical: str
    is_prodrug: bool = False
    primary_cyp_enzymes: List[str] = field(default_factory=list)
    defined_daily_dose: Optional[float] = None
    ddd_unit: Optional[str] = None

    def __post_init__(self) -> None:
        if len(self.atc_code) != 7:
            raise ValueError(f"Codice ATC Livello 5 deve essere di esattamente 7 caratteri: {self.atc_code}")


@dataclass(frozen=True)
class DiseasePhenotypeAssociation:
    """Associazione tra patologia (ICD-10) e manifestazioni fenotipiche (HPO)."""
    icd10_code: str
    hpo_id: str
    frequency_percentage: float = 100.0
    is_mandatory_feature: bool = False

    def __post_init__(self) -> None:
        if self.frequency_percentage < 0.0 or self.frequency_percentage > 100.0:
            raise ValueError(f"Frequenza non valida: {self.frequency_percentage}")
