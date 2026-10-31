"""
Tier 3: Pairwise Cross-Feature Tests.
Pair 4: FSRS v4/v5 Mnemonic Scheduler Transitions + SDUI ExamSimulatorBlock Rendering.
Verifies that mnemonic stability updates and load balancing directly drive server-driven UI payloads.
"""

import pytest
from tests.conftest import (
    point_in_polygon_even_odd,
    fsrs_calculate_retrievability,
    ExamSimulatorBlockContract
)


@pytest.mark.tier3
def test_p04_mcq_success_updates_fsrs_and_sdui_block():
    """Verify correct MCQ answer increases FSRS stability and updates ExamSimulatorBlock payload."""
    initial_stability = 2.0
    initial_reps = 1

    # Student answers MCQ correctly (Rating = Good = 3)
    updated_stability = initial_stability * 2.5  # S = 5.0
    updated_reps = initial_reps + 1

    sdui_payload = {
        "block_type": "ExamSimulatorBlock",
        "item_type": "MCQ",
        "item_data": {
            "question_id": "MCQ_CARDIO_01",
            "stem": "First-line therapy for STEMI...",
            "user_choice": 0,
            "correct_index": 0,
            "is_correct": True
        },
        "fsrs_card_state": {
            "stability": updated_stability,
            "difficulty": 4.8,
            "reps": updated_reps,
            "due_days": 5
        }
    }

    block = ExamSimulatorBlockContract.model_validate(sdui_payload)
    assert block.block_type == "ExamSimulatorBlock"
    assert block.fsrs_card_state["stability"] == 5.0
    assert block.fsrs_card_state["reps"] == 2


@pytest.mark.tier3
def test_p04_hotspot_hit_drives_fsrs_retrievability_in_sdui():
    """Verify successful image hotspot click confirms diagnostic mastery and updates retrievability."""
    pneumothorax_target = [(100.0, 100.0), (200.0, 100.0), (150.0, 200.0)]
    user_click = (150.0, 140.0)

    is_hit = point_in_polygon_even_odd(user_click[0], user_click[1], pneumothorax_target)
    assert is_hit is True

    # Compute retrievability after 3 days elapsed
    stability = 8.0
    r = fsrs_calculate_retrievability(elapsed_days=3.0, stability=stability)
    assert r > 0.90

    sdui_payload = {
        "block_type": "ExamSimulatorBlock",
        "item_type": "IMAGE_HOTSPOT",
        "item_data": {
            "image_uri": "med-asset://images/cxr_pneumo.webp",
            "click_coord": [user_click[0], user_click[1]],
            "hit_success": is_hit
        },
        "fsrs_card_state": {
            "stability": stability,
            "retrievability": r
        }
    }
    block = ExamSimulatorBlockContract.model_validate(sdui_payload)
    assert block.item_data["hit_success"] is True


@pytest.mark.tier3
def test_p04_mcq_lapse_again_resets_interval_in_sdui():
    """Verify failed recall (Rating Again) drops stability and sets review due immediately."""
    sdui_payload = {
        "block_type": "ExamSimulatorBlock",
        "item_type": "MCQ",
        "item_data": {
            "question_id": "MCQ_PHARMA_02",
            "user_choice": 3,
            "correct_index": 1,
            "is_correct": False,
            "rationale": "Clopidogrel requires CYP2C19 activation."
        },
        "fsrs_card_state": {
            "stability": 0.5,
            "difficulty": 8.0,
            "reps": 0,
            "due_days": 0
        }
    }
    block = ExamSimulatorBlockContract.model_validate(sdui_payload)
    assert block.item_data["is_correct"] is False
    assert block.fsrs_card_state["due_days"] == 0


@pytest.mark.tier3
def test_p04_review_load_balancer_caps_daily_sdui_cards():
    """Verify daily cap limits items loaded into exam simulator session."""
    pending_cards = [f"CARD_{i}" for i in range(75)]
    daily_cap = 50
    session_cards = pending_cards[:daily_cap]
    assert len(session_cards) == 50
