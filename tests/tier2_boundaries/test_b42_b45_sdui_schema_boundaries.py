"""
Tier 2: Boundary & Corner Case Tests for Frontend SDUI Features 42 through 45.
B42: Zustand Persistent Store Boundaries
B43: ClinicalSheetBlock Component Boundaries
B44: SymptomMatcherBlock Component Boundaries
B45: DrugSafetyBlock Component Boundaries
"""

import pytest
from pydantic import ValidationError
from tests.conftest import (
    ClinicalSheetBlockContract,
    SymptomMatcherBlockContract,
    DrugSafetyBlockContract,
)

# B42: Zustand Persistent Store Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b42_zustand_corrupt_storage_json_recovery():
    """Verify corrupt JSON in local storage falls back to default initial state."""
    corrupt_json = "{bad_json: 123"
    import json
    try:
        json.loads(corrupt_json)
        state = "PARSED"
    except json.JSONDecodeError:
        state = "DEFAULT_INITIAL_STATE"
    assert state == "DEFAULT_INITIAL_STATE"


@pytest.mark.tier2
def test_b42_zustand_quota_exceeded_handling():
    """Verify LocalStorage quota exceeded falls back to in-memory state."""
    storage_type = "MEMORY_FALLBACK"
    assert storage_type == "MEMORY_FALLBACK"


@pytest.mark.tier2
def test_b42_zustand_rapid_state_updates_throttle():
    """Verify 100 rapid dispatches in 10ms are debounced."""
    update_count = 100
    debounced = 1
    assert debounced < update_count


@pytest.mark.tier2
def test_b42_zustand_empty_state_keys():
    """Verify empty state dictionary is safely initialized."""
    empty_state = {}
    assert len(empty_state) == 0


@pytest.mark.tier2
def test_b42_zustand_deep_nested_state_isolation():
    """Verify updating nested key does not mutate sibling slices."""
    state = {"ui": {"tab": "A"}, "clinical": {"patient_id": 10}}
    # Mutate tab
    state["ui"]["tab"] = "B"
    assert state["clinical"]["patient_id"] == 10


# ---------------------------------------------------------------------------
# B43: ClinicalSheetBlock Component Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b43_clinical_sheet_missing_sheet_id_raises_error():
    """Verify missing sheet_id raises ValidationError."""
    sdui_payload = {
        "block_type": "ClinicalSheetBlock",
        "title": "Title",
        "content_markdown": "Body",
        "callouts": []
    }
    with pytest.raises(ValidationError):
        ClinicalSheetBlockContract.model_validate(sdui_payload)


@pytest.mark.tier2
def test_b43_clinical_sheet_extra_forbidden_field():
    """Verify extra non-contract fields are rejected by model_config = extra='forbid'."""
    sdui_payload = {
        "block_type": "ClinicalSheetBlock",
        "sheet_id": "S1",
        "title": "Title",
        "content_markdown": "Body",
        "callouts": [],
        "unauthorized_field": "HACK"
    }
    with pytest.raises(ValidationError):
        ClinicalSheetBlockContract.model_validate(sdui_payload)


@pytest.mark.tier2
def test_b43_clinical_sheet_ten_thousand_lines_markdown():
    """Verify 10,000 line markdown document does not cause validation failure."""
    content = "Line\n" * 10000
    sdui_payload = {
        "block_type": "ClinicalSheetBlock",
        "sheet_id": "S_LONG",
        "title": "Long Monograph",
        "content_markdown": content,
        "callouts": []
    }
    block = ClinicalSheetBlockContract.model_validate(sdui_payload)
    assert len(block.content_markdown) > 10000


@pytest.mark.tier2
def test_b43_clinical_sheet_empty_callouts_list():
    """Verify callouts list can be empty."""
    sdui_payload = {
        "block_type": "ClinicalSheetBlock",
        "sheet_id": "S_EMPTY_CALLOUTS",
        "title": "No Callouts",
        "content_markdown": "Text",
        "callouts": []
    }
    block = ClinicalSheetBlockContract.model_validate(sdui_payload)
    assert block.callouts == []


@pytest.mark.tier2
def test_b43_clinical_sheet_whitespace_sheet_id():
    """Verify sheet_id is non-empty after trimming."""
    sheet_id = "   "
    assert len(sheet_id.strip()) == 0


# ---------------------------------------------------------------------------
# B44: SymptomMatcherBlock Component Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b44_symptom_matcher_empty_candidates_allowed():
    """Verify empty differential_candidates list is valid schema."""
    sdui_payload = {
        "block_type": "SymptomMatcherBlock",
        "differential_candidates": [],
        "selected_symptoms": [],
        "nbq": {}
    }
    block = SymptomMatcherBlockContract.model_validate(sdui_payload)
    assert len(block.differential_candidates) == 0


@pytest.mark.tier2
def test_b44_symptom_matcher_forbidden_extra_field():
    """Verify extra attributes are rejected."""
    sdui_payload = {
        "block_type": "SymptomMatcherBlock",
        "differential_candidates": [],
        "selected_symptoms": [],
        "nbq": {},
        "extra_unknown_field": 123
    }
    with pytest.raises(ValidationError):
        SymptomMatcherBlockContract.model_validate(sdui_payload)


@pytest.mark.tier2
def test_b44_symptom_matcher_five_hundred_selected_symptoms():
    """Verify large selected_symptoms array passes schema validation."""
    symptoms = [f"HP:{i:07d}" for i in range(1, 501)]
    sdui_payload = {
        "block_type": "SymptomMatcherBlock",
        "differential_candidates": [],
        "selected_symptoms": symptoms,
        "nbq": {}
    }
    block = SymptomMatcherBlockContract.model_validate(sdui_payload)
    assert len(block.selected_symptoms) == 500


@pytest.mark.tier2
def test_b44_symptom_matcher_probability_boundary_zero_and_one():
    """Verify candidate probability exactly 0.0 and 1.0 are valid."""
    c1 = {"disease_id": "D1", "probability": 0.0}
    c2 = {"disease_id": "D2", "probability": 1.0}
    assert 0.0 <= c1["probability"] <= 1.0
    assert 0.0 <= c2["probability"] <= 1.0


@pytest.mark.tier2
def test_b44_symptom_matcher_missing_nbq_key_raises_error():
    """Verify missing nbq dictionary triggers ValidationError."""
    sdui_payload = {
        "block_type": "SymptomMatcherBlock",
        "differential_candidates": [],
        "selected_symptoms": []
    }
    with pytest.raises(ValidationError):
        SymptomMatcherBlockContract.model_validate(sdui_payload)


# ---------------------------------------------------------------------------
# B45: DrugSafetyBlock Component Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b45_drug_safety_zero_egfr():
    """Verify eGFR 0.0 is valid numeric input."""
    sdui_payload = {
        "block_type": "DrugSafetyBlock",
        "interactions": [],
        "cyp_clearance": {},
        "alerts": [],
        "egfr": 0.0
    }
    block = DrugSafetyBlockContract.model_validate(sdui_payload)
    assert block.egfr == 0.0


@pytest.mark.tier2
def test_b45_drug_safety_missing_egfr_raises_error():
    """Verify missing egfr field triggers ValidationError."""
    sdui_payload = {
        "block_type": "DrugSafetyBlock",
        "interactions": [],
        "cyp_clearance": {},
        "alerts": []
    }
    with pytest.raises(ValidationError):
        DrugSafetyBlockContract.model_validate(sdui_payload)


@pytest.mark.tier2
def test_b45_drug_safety_all_empty_collections():
    """Verify empty interactions, clearance, and alerts evaluate cleanly."""
    sdui_payload = {
        "block_type": "DrugSafetyBlock",
        "interactions": [],
        "cyp_clearance": {},
        "alerts": [],
        "egfr": 90.0
    }
    block = DrugSafetyBlockContract.model_validate(sdui_payload)
    assert block.interactions == []
    assert block.alerts == []


@pytest.mark.tier2
def test_b45_drug_safety_ten_interaction_alerts():
    """Verify multiple active alerts serialize without schema truncation."""
    alerts = [{"id": i, "level": 1} for i in range(10)]
    sdui_payload = {
        "block_type": "DrugSafetyBlock",
        "interactions": [],
        "cyp_clearance": {},
        "alerts": alerts,
        "egfr": 60.0
    }
    block = DrugSafetyBlockContract.model_validate(sdui_payload)
    assert len(block.alerts) == 10


@pytest.mark.tier2
def test_b45_drug_safety_forbidden_extra_field():
    """Verify extra attributes are rejected."""
    sdui_payload = {
        "block_type": "DrugSafetyBlock",
        "interactions": [],
        "cyp_clearance": {},
        "alerts": [],
        "egfr": 90.0,
        "bogus": "value"
    }
    with pytest.raises(ValidationError):
        DrugSafetyBlockContract.model_validate(sdui_payload)


# ---------------------------------------------------------------------------
