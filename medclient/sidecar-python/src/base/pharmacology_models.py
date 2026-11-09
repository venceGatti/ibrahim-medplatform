"""Pydantic V2 models for Pharmacology and Drug Safety Engine."""
from enum import Enum, IntEnum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict, computed_field, model_validator
from .exceptions import InvalidATCFormatError


class SeverityLevel(IntEnum):
    """Four-tier pharmacological interaction severity."""
    LEVEL_1 = 1  # Absolute Contraindication / Lethal failure / Critical toxicity
    LEVEL_2 = 2  # Major Interaction (Mandatory clinical intervention / dose adjustment)
    LEVEL_3 = 3  # Moderate Interaction (Monitoring / non-urgent adjustment)
    LEVEL_4 = 4  # Minor Interaction (Optional monitoring)


class EvidenceLevel(str, Enum):
    """Scientific evidence grade."""
    A = "A"  # Randomized clinical trials / meta-analyses
    B = "B"  # Well-controlled cohort studies
    C = "C"  # Case series or consensus panels
    D = "D"  # Pre-clinical / in vitro pharmacokinetic models


class CyP450Isoenzyme(str, Enum):
    """Core hepatic CYP450 isoenzymes."""
    CYP3A4 = "CYP3A4"
    CYP2D6 = "CYP2D6"
    CYP2C9 = "CYP2C9"
    CYP2C19 = "CYP2C19"
    CYP1A2 = "CYP1A2"


class InteractionDetail(BaseModel):
    """Details of an identified drug-drug or drug-enzyme interaction."""
    model_config = ConfigDict(frozen=True)

    interaction_id: int
    source_atc: str
    target_atc: str
    severity: SeverityLevel
    evidence_level: EvidenceLevel
    mechanism: str
    clinical_consequence: str
    management_guideline: str

    @model_validator(mode="before")
    @classmethod
    def populate_aliases(cls, values: Any) -> Any:
        if isinstance(values, dict):
            new_vals = dict(values)
            if "drug_a" in new_vals and "source_atc" not in new_vals:
                new_vals["source_atc"] = new_vals["drug_a"]
            if "drug_b" in new_vals and "target_atc" not in new_vals:
                new_vals["target_atc"] = new_vals["drug_b"]
            if "level" in new_vals and "severity" not in new_vals:
                new_vals["severity"] = new_vals["level"]
            return new_vals
        return values

    @computed_field  # type: ignore
    @property
    def drug_a(self) -> str:
        return self.source_atc

    @computed_field  # type: ignore
    @property
    def drug_b(self) -> str:
        return self.target_atc

    @computed_field  # type: ignore
    @property
    def level(self) -> int:
        return int(self.severity)

    @computed_field  # type: ignore
    @property
    def is_prodrug_bioactivation_block(self) -> bool:
        mech = self.mechanism.lower()
        return "prodrug" in mech or "bioactivation" in mech


DrugInteractionRecord = InteractionDetail
DrugInteractionDetail = InteractionDetail


class CYPFunctionalState(BaseModel):
    """Net residual metabolic clearance for a specific CYP450 isoenzyme."""
    model_config = ConfigDict(frozen=True)

    isoenzyme: CyP450Isoenzyme
    baseline_capacity: float = 1.0
    computed_clearance: float = Field(ge=0.05, le=5.0)
    primary_inhibitors: List[str] = Field(default_factory=list)
    primary_inducers: List[str] = Field(default_factory=list)


class OrganToxicityReport(BaseModel):
    """Aggregated organ toxicity scores across cardiac, renal, and central nervous systems."""
    model_config = ConfigDict(frozen=True)

    qtc_prolongation_score: float = Field(ge=0.0)
    torsades_de_pointes_risk: SeverityLevel
    renal_load_score: float = Field(ge=0.0)
    triple_whammy_detected: bool
    cns_depression_index: float = Field(ge=0.0)
    organ_contraindications: List[str] = Field(default_factory=list)


class TherapeuticAlternative(BaseModel):
    """Recommended safer therapeutic substitution minimizing clinical cost."""
    model_config = ConfigDict(frozen=True)

    original_atc: str
    suggested_atc: str
    suggested_inn_name: str
    hierarchy_distance: int
    cost_index: float
    clinical_rationale: str


class PharmacogenomicMatch(BaseModel):
    """CPIC actionable pharmacogenomic rule alert."""
    model_config = ConfigDict(frozen=True)

    gene_symbol: str
    patient_phenotype: str
    detected_atc: str
    recommendation: str
    is_absolute_contraindication: bool


class PrescribedDrugEntry(BaseModel):
    """Prescription entry representing active substance or prodrug."""
    model_config = ConfigDict(frozen=True)

    atc_code: str
    inn_name: str = ""
    single_dose_mg: float = Field(default=100.0, gt=0.0)
    daily_dose_mg: float = Field(default=100.0, gt=0.0)
    route: str = "oral"
    is_prodrug: bool = Field(default=False, description="ROA-10 prodrug bioactivation flag")
    is_narrow_therapeutic_index: bool = Field(default=False)
    qtc_base_risk: float = Field(default=0.0, ge=0.0, le=3.0)
    is_ras_blocker: bool = Field(default=False)
    is_diuretic: bool = Field(default=False)
    is_nsaid: bool = Field(default=False)
    fm_cyp: Dict[str, float] = Field(default_factory=dict, description="Fraction metabolized by isoenzyme")

    @field_validator("atc_code")
    @classmethod
    def validate_atc(cls, raw_atc_code: str) -> str:
        clean = raw_atc_code.strip().upper()
        if len(clean) != 7:
            raise InvalidATCFormatError(f"ATC code must be strictly 7 characters, got {raw_atc_code}")
        return clean


class DrugSafetyEvaluationReport(BaseModel):
    """Internal analytical execution output for the pharmacology engine."""
    model_config = ConfigDict(frozen=True)

    transaction_id: str
    patient_id: str
    engine_version: str = "3.2.0-deterministic-sqlite"
    processing_time_ms: float
    execution_verdict: str  # PASSED, REVIEW_REQUIRED, REJECTED
    max_severity: SeverityLevel
    posology_violations: List[str] = Field(default_factory=list)
    detected_interactions: List[InteractionDetail] = Field(default_factory=list)
    cyp_profile_states: Dict[str, CYPFunctionalState] = Field(default_factory=dict)
    organ_toxicities: OrganToxicityReport
    pgx_alerts: List[PharmacogenomicMatch] = Field(default_factory=list)
    recommended_alternatives: List[TherapeuticAlternative] = Field(default_factory=list)


DrugSafetyEvaluationBlock = DrugSafetyEvaluationReport
DrugSafetyEvaluationResult = DrugSafetyEvaluationReport
PrescribedDrugItem = PrescribedDrugEntry


class PharmaEvaluationRequest(BaseModel):
    """Specification for pharmacology safety evaluation."""
    model_config = ConfigDict(strict=False, extra="ignore")

    patient_id: str = "PATIENT_LOCAL_01"
    prescribed_drugs: Optional[List[PrescribedDrugEntry]] = None
    prescribed_atc_codes: Optional[List[str]] = None
    age: int = 50
    is_female: bool = False
    serum_creatinine_mg_dl: float = 1.0
    serum_potassium_meq_l: float = 4.2
    patient_genotypes: Optional[Dict[str, str]] = None

