"""SDUI Serialization Emitter for 4 Polymorphic Blocks."""
from typing import List, Dict, Any, Optional
from ..interfaces.sdui import ISDUISerializer
from ..base.exceptions import SDUINodeNotFoundError
from ..base.sdui_models import (
    ClinicalSheetBlock,
    SymptomMatcherBlock,
    DrugSafetyBlock,
    ExamSimulatorBlock,
    CalloutItem,
    CalloutSeverity,
    SDUIPayloadEnvelope,
)

SDUI_BLOCK_REGISTRY: Dict[str, str] = {
    "ClinicalSheetBlock": "ClinicalSheetBlock",
    "SymptomMatcherBlock": "SymptomMatcherBlock",
    "DrugSafetyBlock": "DrugSafetyBlock",
    "ExamSimulatorBlock": "ExamSimulatorBlock",
    "MarkdownBlock": "ClinicalSheetBlock",
    "DifferentialDiagnosisBlock": "SymptomMatcherBlock",
    "ClinicalExamBlock": "ExamSimulatorBlock",
    "InteractiveFlowchartBlock": "ExamSimulatorBlock",
    "AnatomicalHotspotBlock": "ExamSimulatorBlock",
}


class SDUISerializer(ISDUISerializer):
    """Constructs validated SDUI payloads conforming to the 4-block polymorphic schema."""

    def build_clinical_sheet_block(
        self,
        sheet_id: str,
        title: str,
        content_markdown: str,
        callouts: List[Dict[str, Any]],
        vitals_snapshot: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Build ClinicalSheetBlock payload."""
        typed_callouts = [
            CalloutItem(
                id=c.get("id", f"callout_{idx}"),
                severity=CalloutSeverity(c.get("severity", "CLINICAL_PEARL")),
                title=c.get("title", ""),
                body_markdown=c.get("body_markdown", ""),
                icd10_refs=c.get("icd10_refs", []),
                hpo_refs=c.get("hpo_refs", []),
                atc_refs=c.get("atc_refs", []),
            )
            for idx, c in enumerate(callouts)
        ]

        block = ClinicalSheetBlock(
            sheet_id=sheet_id,
            title=title,
            content_markdown=content_markdown,
            callouts=typed_callouts,
            vitals_snapshot=vitals_snapshot,
        )
        return block.model_dump()

    def build_symptom_matcher_block(
        self,
        differential_candidates: List[Dict[str, Any]],
        selected_symptoms: List[Any],
        nbq: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Build SymptomMatcherBlock definition."""
        normalized_symptoms: List[str] = [
            s if isinstance(s, str) else str(s.get("hpo_id", s.get("name", str(s))))
            for s in selected_symptoms
        ]
        block = SymptomMatcherBlock(
            differential_candidates=differential_candidates,
            selected_symptoms=normalized_symptoms,
            nbq=nbq if nbq is not None else {},
        )
        return block.model_dump()

    def build_drug_safety_block(
        self,
        interactions: List[Dict[str, Any]],
        cyp_clearance: Dict[str, Any],
        alerts: List[Dict[str, Any]],
        egfr: float = 90.0,
    ) -> Dict[str, Any]:
        """Build DrugSafetyBlock definition."""
        block = DrugSafetyBlock(
            interactions=interactions,
            cyp_clearance=cyp_clearance,
            alerts=alerts,
            egfr=round(egfr, 2),
        )
        return block.model_dump()

    def build_exam_simulator_block(
        self,
        item_type: str,
        item_data: Dict[str, Any],
        fsrs_card_state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Build ExamSimulatorBlock definition."""
        block = ExamSimulatorBlock(
            item_type=item_type,
            item_data=item_data,
            fsrs_card_state=fsrs_card_state,
        )
        return block.model_dump()

    def serialize_envelope(
        self,
        session_id: str,
        sequence_number: int,
        blocks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Package blocks into SDUIMessageEnvelope."""
        envelope = SDUIPayloadEnvelope(
            session_id=session_id,
            sequence_number=sequence_number,
            blocks=blocks,
        )
        return envelope.model_dump()

    @classmethod
    def resolve_block_type(cls, block_type_name: str) -> str:
        """Resolve canonical or alias block type name using Dual Registry (ROA-02)."""
        canonical_name = SDUI_BLOCK_REGISTRY.get(block_type_name)
        if not canonical_name:
            raise SDUINodeNotFoundError(
                f"Requested SDUI block type '{block_type_name}' is not registered in Dual Registry"
            )
        return canonical_name

    def parse_polymorphic_block(self, block_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize a polymorphic SDUI block according to the Dual Registry."""
        raw_type = block_data.get("block_type") or block_data.get("component_type")
        if not raw_type:
            raise SDUINodeNotFoundError("SDUI block payload is missing 'block_type' or 'component_type'")

        canonical_type = self.resolve_block_type(str(raw_type))
        if canonical_type == "ClinicalSheetBlock":
            return ClinicalSheetBlock.model_validate(block_data).model_dump()
        elif canonical_type == "SymptomMatcherBlock":
            return SymptomMatcherBlock.model_validate(block_data).model_dump()
        elif canonical_type == "DrugSafetyBlock":
            return DrugSafetyBlock.model_validate(block_data).model_dump()
        elif canonical_type == "ExamSimulatorBlock":
            return ExamSimulatorBlock.model_validate(block_data).model_dump()
        raise SDUINodeNotFoundError(f"Unhandled canonical block type '{canonical_type}'")
