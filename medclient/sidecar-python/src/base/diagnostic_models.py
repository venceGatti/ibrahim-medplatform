"""Pydantic V2 models for Diagnostic Engine (Red Flags, Log-Odds, NBQ)."""
from enum import Enum
from typing import List, Optional, Literal, Any
from pydantic import BaseModel, Field, ConfigDict, computed_field, model_validator


class SystemAlertLevel(str, Enum):
    """Physiological alert tiers."""
    NOMINAL = "NOMINAL"
    YELLOW_ATTENTION = "YELLOW_ATTENTION"
    RED_CRITICAL = "RED_CRITICAL"


class ClinicalFinding(BaseModel):
    """Single clinical observation or symptom presence/absence."""
    model_config = ConfigDict(frozen=True)

    hpo_id: str = Field(description="HPO identifier or symptom token")
    state: Literal["PRESENT", "ABSENT"] = Field(description="Clinical observation state")
    is_pathognomonic: bool = Field(default=False, description="Manual pathognomonic override flag")


class VitalSigns(BaseModel):
    """Patient vital signs and consciousness evaluation."""
    model_config = ConfigDict(frozen=True)

    heart_rate_bpm: float = Field(ge=10.0, le=300.0)
    systolic_bp_mmhg: float = Field(ge=30.0, le=300.0)
    respiratory_rate_bpm: float = Field(ge=2.0, le=80.0)
    spo2_percent: float = Field(ge=30.0, le=100.0)
    temperature_celsius: float = Field(ge=25.0, le=45.0)
    avpu_scale: Literal["A", "V", "P", "U"] = Field(default="A")
    gcs_score: int = Field(default=15, ge=3, le=15)
    supplemental_o2: bool = Field(default=False)
    hypercapnic_risk: bool = Field(default=False)


class RedFlagsAssessment(BaseModel):
    """Deterministic triage output evaluating Shock Index, qSOFA, and NEWS2."""
    model_config = ConfigDict(frozen=True)

    alert_level: SystemAlertLevel
    shock_index: float
    qsofa_score: int
    news2_score: int
    critical_triggers: List[str]


class DifferentialCandidate(BaseModel):
    """Ranked disease candidate produced by Log-Odds CSR engine."""
    model_config = ConfigDict(frozen=True)

    icd10_code: str
    disease_name: str
    posterior_probability: float = Field(ge=0.0, le=1.0)
    raw_log_odds: float
    supporting_symptoms: List[str]
    rule_out_penalties: List[str]

    @model_validator(mode="before")
    @classmethod
    def populate_aliases(cls, values: Any) -> Any:
        if isinstance(values, dict):
            new_vals = dict(values)
            if "name" in new_vals and "disease_name" not in new_vals:
                new_vals["disease_name"] = new_vals["name"]
            if "disease_id" in new_vals and "icd10_code" not in new_vals:
                new_vals["icd10_code"] = new_vals["disease_id"]
            if "probability" in new_vals and "posterior_probability" not in new_vals:
                new_vals["posterior_probability"] = new_vals["probability"]
            return new_vals
        return values

    @computed_field  # type: ignore
    @property
    def disease_id(self) -> str:
        return self.icd10_code

    @computed_field  # type: ignore
    @property
    def name(self) -> str:
        return self.disease_name

    @computed_field  # type: ignore
    @property
    def probability(self) -> float:
        return self.posterior_probability


class NextBestQuestion(BaseModel):
    """Optimal differentiating question selected by Active Discrimination."""
    model_config = ConfigDict(frozen=True)

    target_hpo_id: str
    target_phenotype_label: str
    target_loinc_code: Optional[str] = None
    expected_information_gain: float
    clinical_justification: str

    @computed_field  # type: ignore
    @property
    def feature_code(self) -> str:
        return self.target_hpo_id

    @computed_field  # type: ignore
    @property
    def question_id(self) -> str:
        return self.target_hpo_id

    @computed_field  # type: ignore
    @property
    def text(self) -> str:
        return self.target_phenotype_label

    @computed_field  # type: ignore
    @property
    def hpo_id(self) -> str:
        return self.target_hpo_id

    @computed_field  # type: ignore
    @property
    def information_gain_bits(self) -> float:
        return self.expected_information_gain


class SymptomMatcherInput(BaseModel):
    """Request envelope for diagnostic engine evaluation."""
    model_config = ConfigDict(frozen=True)

    session_id: str
    vitals: VitalSigns
    findings: List[ClinicalFinding] = Field(min_length=1)


class SymptomMatcherOutput(BaseModel):
    """Complete diagnostic output with triage, differential list, and NBQ."""
    model_config = ConfigDict(frozen=True)

    session_id: str
    execution_time_ms: float
    red_flags: RedFlagsAssessment
    differential_diagnosis: List[DifferentialCandidate]
    nbq: Optional[NextBestQuestion] = None
