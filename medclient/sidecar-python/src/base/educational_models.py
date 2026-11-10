"""Pydantic V2 models for Educational Engine (NLI, Stateful DAG, FSRS)."""
from datetime import datetime
from enum import IntEnum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict, model_validator


# ==============================================================================
# TIPOLOGIA 3: VALUTAZIONE AUTOMATICA APERTA (NLI)
# ==============================================================================

class AtomicConcept(BaseModel):
    """Rubric concept with clinical criticality flag."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    hypothesis: str = Field(min_length=5, description="Atomic concept sentence")
    weight: float = Field(gt=0.0, le=1.0)
    is_critical: bool = Field(default=False)
    icd10_code: Optional[str] = None
    hpo_code: Optional[str] = None
    atc_codes: List[str] = Field(default_factory=list)


class NLIEvaluationRubric(BaseModel):
    """Rubric set for evaluating free-text student clinical answers."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    clinical_vignette: str = Field(min_length=20)
    atomic_concepts: List[AtomicConcept] = Field(min_length=1)

    @field_validator("atomic_concepts")
    @classmethod
    def check_weights_sum(cls, concepts_list: List[AtomicConcept]) -> List[AtomicConcept]:
        total_weight = sum(ac.weight for ac in concepts_list)
        if not (0.98 <= total_weight <= 1.02):
            raise ValueError(f"Sum of atomic concept weights must equal 1.0, got {total_weight:.4f}")
        return concepts_list


# ==============================================================================
# TIPOLOGIA 4: CASO CLINICO SEQUENZIALE (STATEFUL DAG)
# ==============================================================================

class PatientVitals(BaseModel):
    """Hemodynamic state vector for scenario execution."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    map_mmHg: float = Field(ge=0.0, le=300.0, description="Mean Arterial Pressure")
    hr_bpm: float = Field(ge=0.0, le=300.0, description="Heart Rate")
    rr_bpm: float = Field(ge=0.0, le=80.0, description="Respiratory Rate")
    spo2_percent: float = Field(ge=0.0, le=100.0)
    gcs: int = Field(ge=3, le=15, description="Glasgow Coma Scale")


class DAGTransition(BaseModel):
    """Directed action transition from current state to target state."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    action_id: str
    action_label: str
    destination_node_id: str
    time_cost_min: float = Field(ge=0.0)
    financial_cost_eur: float = Field(ge=0.0)
    risk_severity: float = Field(ge=0.0, le=1.0)
    vitals_delta: Optional[Dict[str, float]] = None
    clinical_consequence: str


class DAGNode(BaseModel):
    """Single clinical decision point in stateful scenario graph."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    node_id: str
    narrative_state: str
    is_terminal: bool = False
    terminal_grade: Optional[float] = Field(None, ge=0.0, le=1.0)
    current_vitals: PatientVitals
    available_transitions: List[DAGTransition] = Field(default_factory=list)


class StatefulDAGDefinition(BaseModel):
    """Complete clinical case graph definition."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    initial_node_id: str
    nodes: Dict[str, DAGNode] = Field(min_length=2)
    optimal_time_min: float = Field(gt=0.0)
    critical_time_min: float = Field(gt=0.0)
    max_budget_eur: float = Field(gt=0.0)
    optimal_cost_eur: float = Field(gt=0.0)


StatefulDAGPayload = StatefulDAGDefinition


# ==============================================================================
# FSRS SPACING REPETITION MODELS
# ==============================================================================

class FSRSReviewGrade(IntEnum):
    """Four-grade review evaluation."""
    AGAIN = 1
    HARD = 2
    GOOD = 3
    EASY = 4


class FSRSStateEnum(IntEnum):
    """Memory lifecycle card state."""
    NEW = 0
    LEARNING = 1
    REVIEW = 2
    RELEARNING = 3


class FSRSCardBase(BaseModel):
    """Persisted memory state of an ontological clinical card."""
    model_config = ConfigDict(from_attributes=True, strict=False)

    concept_uid: str = Field(default="")
    stability: float = Field(default=2.0, ge=0.01)
    difficulty: float = Field(default=5.0, ge=1.0, le=10.0)
    elapsed_days: float = Field(default=0.0, ge=0.0)
    scheduled_days: float = Field(default=0.0, ge=0.0)
    reps: int = Field(default=0, ge=0)
    lapses: int = Field(default=0, ge=0)
    state: FSRSStateEnum = Field(default=FSRSStateEnum.NEW)
    last_review: Optional[datetime] = None
    due_date: Optional[datetime] = None
    retrievability: float = Field(default=1.0, ge=0.0, le=1.0)
    criticality_weight: float = Field(default=1.0, ge=0.0, le=5.0)

    @model_validator(mode="before")
    @classmethod
    def handle_card_id(cls, raw_input: Any) -> Any:
        if isinstance(raw_input, dict):
            if "concept_uid" not in raw_input and "card_id" in raw_input:
                updated_input = dict(raw_input)
                updated_input["concept_uid"] = updated_input["card_id"]
                return updated_input
        return raw_input

    @property
    def card_id(self) -> str:
        return self.concept_uid


class FSRSReviewInput(BaseModel):
    """User review submission specification."""
    model_config = ConfigDict(strict=False)

    concept_uid: str
    rating: FSRSReviewGrade
    review_time: datetime
    time_taken_ms: int = Field(ge=0)
    target_exam_date: Optional[datetime] = None
    desired_retention: float = Field(0.90, ge=0.70, le=0.98)


class FSRSReviewOutput(BaseModel):
    """Scheduler output with updated stability and next due interval."""
    model_config = ConfigDict(strict=False)

    card_state: FSRSCardBase
    interval_days: int
    projected_retention: float
    is_exam_compressed: bool
    relearning_priority: bool


class FSRSDailyBatchRequest(BaseModel):
    """Daily batch query parameters."""
    model_config = ConfigDict(strict=False)

    current_date: datetime
    limit: int = Field(default=350, ge=1, le=1000)
    include_relearning: bool = True


class FSRSDailyBatchResponse(BaseModel):
    """Daily due card batch with backlog metrics."""
    model_config = ConfigDict(strict=False)

    queue_size: int
    overdue_count: int
    relearning_count: int
    cards: List[FSRSCardBase]
