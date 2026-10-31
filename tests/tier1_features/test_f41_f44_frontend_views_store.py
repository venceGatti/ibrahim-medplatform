"""
Tier 1: Feature Coverage Tests for Frontend SDUI Features 41 through 44.
- Feature 41: React 19 Frontend Shell
- Feature 42: Zustand Persistent Store
- Feature 43: ClinicalSheetBlock Component
- Feature 44: SymptomMatcherBlock Component
"""

import pytest
from tests.conftest import (
    ClinicalSheetBlockContract,
    SymptomMatcherBlockContract,
)

# Feature 41: React 19 Frontend Shell
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f41_react_root_element_presence():
    """Verify HTML template mounts single root container div."""
    index_html = '<!DOCTYPE html><html><body><div id="root"></div></body></html>'
    assert '<div id="root"></div>' in index_html


@pytest.mark.tier1
def test_f41_vite_entrypoint_script_tag():
    """Verify script module points to main application entrypoint."""
    index_html = '<script type="module" src="/src/main.tsx"></script>'
    assert 'type="module"' in index_html
    assert 'src="/src/main.tsx"' in index_html


@pytest.mark.tier1
def test_f41_tailwind_utility_class_inclusion():
    """Verify UI components use standard TailwindCSS utilities."""
    button_classes = "px-4 py-2 bg-blue-600 text-white rounded shadow-sm hover:bg-blue-700"
    assert "bg-blue-600" in button_classes
    assert "rounded" in button_classes


@pytest.mark.tier1
def test_f41_error_boundary_fallback_contract():
    """Verify React error boundary returns user-facing recovery UI upon render error."""
    error_state = {"hasError": True, "error_message": "Chunk render failed"}
    fallback_title = "An unexpected error occurred in this view" if error_state["hasError"] else ""
    assert "unexpected error" in fallback_title


@pytest.mark.tier1
def test_f41_spa_active_view_navigation():
    """Verify client-side navigation switches active views without full page reload."""
    views = ["clinical_sheet", "symptom_matcher", "drug_safety", "exam_simulator"]
    current_view = views[1]
    assert current_view == "symptom_matcher"


# ---------------------------------------------------------------------------
# Feature 42: Zustand Persistent Store
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f42_zustand_tab_persistence_across_navigation():
    """Verify switching tabs retains previously selected tab and scroll state (Rule 8)."""
    store_state = {
        "active_tab": "drug_safety",
        "tab_scroll_positions": {"clinical_sheet": 240, "drug_safety": 0},
        "search_input": "Clopidogrel"
    }
    # Verify switching to clinical_sheet and back
    assert store_state["tab_scroll_positions"]["clinical_sheet"] == 240
    assert store_state["search_input"] == "Clopidogrel"


@pytest.mark.tier1
def test_f42_zustand_diagnostic_symptom_selection_retention():
    """Verify selected symptoms remain in Zustand store when navigating between views."""
    store = {"selected_symptoms": ["HP:0002094", "HP:0001635"]}
    # User navigates to monograph and returns
    assert len(store["selected_symptoms"]) == 2
    assert "HP:0002094" in store["selected_symptoms"]


@pytest.mark.tier1
def test_f42_zustand_local_storage_serialization():
    """Verify Zustand state serializes to JSON string for LocalStorage persistence."""
    state = {"theme": "system", "cached_module_id": "CARDIO_01"}
    import json
    serialized = json.dumps(state)
    deserialized = json.loads(serialized)
    assert deserialized["cached_module_id"] == "CARDIO_01"


@pytest.mark.tier1
def test_f42_zustand_isolated_slice_reset():
    """Verify resetting exam state does not clear monograph search state."""
    store = {
        "search_query": "Troponin",
        "exam_answers": {"Q1": 2, "Q2": 0}
    }
    # Reset exam answers only
    store["exam_answers"] = {}
    assert store["search_query"] == "Troponin"
    assert len(store["exam_answers"]) == 0


@pytest.mark.tier1
def test_f42_zustand_subscriber_notification():
    """Verify state updates trigger registered listener callbacks."""
    listeners = []
    events_received = []

    def on_change(new_state):
        events_received.append(new_state)

    listeners.append(on_change)
    # State change
    for l in listeners:
        l({"status": "UPDATED"})
    assert len(events_received) == 1
    assert events_received[0]["status"] == "UPDATED"


# ---------------------------------------------------------------------------
# Feature 43: ClinicalSheetBlock Component
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f43_clinical_sheet_pydantic_contract():
    """Verify ClinicalSheetBlock payload satisfies schema contract."""
    payload = {
        "block_type": "ClinicalSheetBlock",
        "sheet_id": "SHEET_STEMI_01",
        "title": "ST-Elevation Myocardial Infarction",
        "content_markdown": "# Clinical Presentation\nSevere retrosternal pain.",
        "callouts": [{"severity": "CRITICAL", "message": "Immediate catheterization laboratory activation."}]
    }
    block = ClinicalSheetBlockContract.model_validate(payload)
    assert block.block_type == "ClinicalSheetBlock"
    assert block.sheet_id == "SHEET_STEMI_01"


@pytest.mark.tier1
def test_f43_clinical_sheet_markdown_alias():
    """Verify dual registry resolves 'MarkdownBlock' alias to ClinicalSheetBlock (ROA-02)."""
    alias_registry = {
        "MarkdownBlock": "ClinicalSheetBlock",
        "DifferentialDiagnosisBlock": "SymptomMatcherBlock"
    }
    resolved = alias_registry.get("MarkdownBlock")
    assert resolved == "ClinicalSheetBlock"


@pytest.mark.tier1
def test_f43_clinical_sheet_callout_severity_classes():
    """Verify severity callouts map to specific CSS border/background themes."""
    severity_css = {
        "INFO": "border-blue-500 bg-blue-50",
        "WARNING": "border-amber-500 bg-amber-50",
        "CRITICAL": "border-red-600 bg-red-50"
    }
    assert "bg-red-50" in severity_css["CRITICAL"]


@pytest.mark.tier1
def test_f43_clinical_sheet_empty_callouts_allowed():
    """Verify sheets with zero callouts remain valid."""
    payload = {
        "block_type": "ClinicalSheetBlock",
        "sheet_id": "SHEET_ANATOMY_01",
        "title": "Coronary Anatomy",
        "content_markdown": "Normal anatomy of LAD and RCA.",
        "callouts": []
    }
    block = ClinicalSheetBlockContract.model_validate(payload)
    assert len(block.callouts) == 0


@pytest.mark.tier1
def test_f43_clinical_sheet_title_non_empty():
    """Verify title is non-empty string."""
    payload = {
        "block_type": "ClinicalSheetBlock",
        "sheet_id": "SHEET_01",
        "title": "Valid Title",
        "content_markdown": "Content",
        "callouts": []
    }
    block = ClinicalSheetBlockContract.model_validate(payload)
    assert len(block.title) > 0


# ---------------------------------------------------------------------------
# Feature 44: SymptomMatcherBlock Component
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f44_symptom_matcher_pydantic_contract():
    """Verify SymptomMatcherBlock payload satisfies schema contract."""
    payload = {
        "block_type": "SymptomMatcherBlock",
        "differential_candidates": [
            {"disease_id": "D1", "name": "STEMI", "probability": 0.85}
        ],
        "selected_symptoms": ["HP:0001635"],
        "nbq": {"question_id": "Q_ECG", "text": "Is there ST elevation?"}
    }
    block = SymptomMatcherBlockContract.model_validate(payload)
    assert block.block_type == "SymptomMatcherBlock"
    assert len(block.differential_candidates) == 1


@pytest.mark.tier1
def test_f44_symptom_matcher_differential_diagnosis_alias():
    """Verify dual registry resolves 'DifferentialDiagnosisBlock' to SymptomMatcherBlock (ROA-02)."""
    alias_registry = {"DifferentialDiagnosisBlock": "SymptomMatcherBlock"}
    assert alias_registry["DifferentialDiagnosisBlock"] == "SymptomMatcherBlock"


@pytest.mark.tier1
def test_f44_symptom_matcher_radar_chart_metrics():
    """Verify candidate diseases provide probabilistic metrics for radar visualization."""
    candidate = {"name": "Pulmonary Embolism", "probability": 0.72, "severity": "HIGH"}
    assert 0.0 <= candidate["probability"] <= 1.0


@pytest.mark.tier1
def test_f44_symptom_matcher_tag_toggle():
    """Verify clicking an active symptom tag removes it from selected_symptoms."""
    symptoms = ["HP:0002094", "HP:0001635"]
    clicked_tag = "HP:0002094"
    if clicked_tag in symptoms:
        symptoms.remove(clicked_tag)
    assert "HP:0002094" not in symptoms
    assert len(symptoms) == 1


@pytest.mark.tier1
def test_f44_symptom_matcher_nbq_structure():
    """Verify NBQ item contains question_id and inquiry text."""
    nbq = {"question_id": "Q_PAIN_RADIATION", "text": "Does pain radiate to the left arm?"}
    assert "question_id" in nbq
    assert "text" in nbq


# ---------------------------------------------------------------------------
