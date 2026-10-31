"""Interface for Server-Driven UI (SDUI) serialization."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class ISDUISerializer(ABC):
    """Serializes platform states into the 4 polymorphic SDUI blocks."""

    @abstractmethod
    def build_clinical_sheet_block(
        self,
        sheet_id: str,
        title: str,
        content_markdown: str,
        callouts: List[Dict[str, Any]],
        vitals_snapshot: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Build a typed ClinicalSheetBlock definition."""
        raise NotImplementedError("Subclasses must implement build_clinical_sheet_block")

    @abstractmethod
    def build_symptom_matcher_block(
        self,
        differential_candidates: List[Dict[str, Any]],
        selected_symptoms: List[str],
        nbq: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Build a typed SymptomMatcherBlock definition."""
        raise NotImplementedError("Subclasses must implement build_symptom_matcher_block")

    @abstractmethod
    def build_drug_safety_block(
        self,
        interactions: List[Dict[str, Any]],
        cyp_clearance: Dict[str, Any],
        alerts: List[Dict[str, Any]],
        egfr: float,
    ) -> Dict[str, Any]:
        """Build a typed DrugSafetyBlock definition."""
        raise NotImplementedError("Subclasses must implement build_drug_safety_block")

    @abstractmethod
    def build_exam_simulator_block(
        self,
        item_type: str,
        item_data: Dict[str, Any],
        fsrs_card_state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Build a typed ExamSimulatorBlock definition."""
        raise NotImplementedError("Subclasses must implement build_exam_simulator_block")

    @abstractmethod
    def serialize_envelope(
        self,
        session_id: str,
        sequence_number: int,
        blocks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Package blocks into a validated SDUI envelope."""
        raise NotImplementedError("Subclasses must implement serialize_envelope")
