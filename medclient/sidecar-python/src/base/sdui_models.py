"""Pydantic V2 models for Server-Driven UI (SDUI) 4-block polymorphic architecture (ROA-02)."""
from enum import Enum
from typing import List, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field, ConfigDict


class CalloutSeverity(str, Enum):
    """Clinical callout visual severity tier."""
    RED_FLAG = "RED_FLAG"
    CONTRAINDICATION = "CONTRAINDICATION"
    EXAM_TIP = "EXAM_TIP"
    CLINICAL_PEARL = "CLINICAL_PEARL"
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


class CalloutEntry(BaseModel):
    """Structured clinical alert callout."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = "callout_entry"
    severity: CalloutSeverity
    title: str = ""
    body_markdown: str = ""
    message: Optional[str] = None
    icd10_refs: List[str] = Field(default_factory=list)
    hpo_refs: List[str] = Field(default_factory=list)
    atc_refs: List[str] = Field(default_factory=list)


CalloutItem = CalloutEntry


# 1. ClinicalSheetBlock (aliased to MarkdownBlock)
class ClinicalSheetBlock(BaseModel):
    """Encyclopedic medical monograph block with typed severity callouts."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    block_type: Literal["ClinicalSheetBlock", "MarkdownBlock"] = "ClinicalSheetBlock"
    component_type: Literal["ClinicalSheetBlock", "MarkdownBlock"] = "ClinicalSheetBlock"
    sheet_id: str
    title: str = ""
    content_markdown: str = ""
    callouts: List[CalloutEntry] = Field(default_factory=list)
    vitals_snapshot: Optional[Dict[str, float]] = None
    differential_diagnoses: Optional[List[Dict[str, Any]]] = None


# 2. SymptomMatcherBlock (aliased to DifferentialDiagnosisBlock)
class SymptomMatcherBlock(BaseModel):
    """Interactive symptom selection, radar chart, and NBQ block."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    block_type: Literal["SymptomMatcherBlock", "DifferentialDiagnosisBlock"] = "SymptomMatcherBlock"
    component_type: Literal["SymptomMatcherBlock", "DifferentialDiagnosisBlock"] = "SymptomMatcherBlock"
    differential_candidates: List[Dict[str, Any]] = Field(default_factory=list)
    selected_symptoms: List[str] = Field(default_factory=list)
    symptoms_tree: Optional[List[Dict[str, Any]]] = None
    nbq: Dict[str, Any]


# 3. DrugSafetyBlock
class DrugSafetyBlock(BaseModel):
    """Drug-drug interaction matrix, CYP450 gauges, and toxicity warnings."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    block_type: Literal["DrugSafetyBlock"] = "DrugSafetyBlock"
    component_type: Literal["DrugSafetyBlock"] = "DrugSafetyBlock"
    interactions: List[Dict[str, Any]] = Field(default_factory=list)
    cyp_clearance: Dict[str, Any] = Field(default_factory=dict)
    alerts: List[Dict[str, Any]] = Field(default_factory=list)
    egfr: float
    qtc_tisdale_score: Optional[float] = None
    triple_whammy_detected: Optional[bool] = None
    fdc_decompositions: Optional[List[Dict[str, Any]]] = None


# 4. ExamSimulatorBlock (aliased to ClinicalExamBlock / InteractiveFlowchartBlock / AnatomicalHotspotBlock)
class ExamSimulatorBlock(BaseModel):
    """Exam assessment block: MCQ, SVG hotspot, or DAG scenario stepper."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    block_type: Literal[
        "ExamSimulatorBlock",
        "ClinicalExamBlock",
        "InteractiveFlowchartBlock",
        "AnatomicalHotspotBlock",
    ] = "ExamSimulatorBlock"
    component_type: Literal[
        "ExamSimulatorBlock",
        "ClinicalExamBlock",
        "InteractiveFlowchartBlock",
        "AnatomicalHotspotBlock",
    ] = "ExamSimulatorBlock"
    item_type: str = "MCQ_4"
    item_data: Dict[str, Any]
    fsrs_card_state: Optional[Dict[str, Any]] = None
    scenario_katex: Optional[str] = None
    options: Optional[List[Dict[str, Any]]] = None


SDUIBlock = Union[
    ClinicalSheetBlock,
    SymptomMatcherBlock,
    DrugSafetyBlock,
    ExamSimulatorBlock,
]


class SDUIMessageEnvelope(BaseModel):
    """Top-level streaming envelope carrying polymorphic blocks."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    session_id: str
    sequence_number: int
    blocks: List[SDUIBlock]


SDUIPayloadEnvelope = SDUIMessageEnvelope
