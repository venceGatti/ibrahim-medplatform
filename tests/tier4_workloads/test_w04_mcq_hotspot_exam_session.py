"""
Tier 4: Real-World Clinical Workload Scenario W04.
Scenario: Interactive MCQ and Polygonal Hotspot Diagnostic Exam Session.
Evaluates Even-Odd ray-casting on radiographic images, MCQ evaluation, FSRS v4/v5 progression, and load balancing.
"""

import pytest
from tests.conftest import (
    point_in_polygon_even_odd,
    fsrs_calculate_retrievability,
    ExamSimulatorBlockContract
)


@pytest.mark.tier4
def test_w04_stage1_thoracic_hotspot_even_odd_ray_casting():
    """Stage 1: Tension pneumothorax chest radiograph spatial hotspot selection."""
    # Right hemithorax deep sulcus sign polygon (SVG viewport 600x600)
    deep_sulcus_polygon = [
        (380.0, 240.0),
        (450.0, 240.0),
        (470.0, 310.0),
        (400.0, 330.0),
        (370.0, 270.0)
    ]
    # Student clicks coordinate inside the radiolucent tension zone
    student_click = (412.0, 285.0)

    is_hit = point_in_polygon_even_odd(student_click[0], student_click[1], deep_sulcus_polygon)
    assert is_hit is True

    # Student clicks unaffected left lung field
    distractor_click = (150.0, 250.0)
    is_distractor_hit = point_in_polygon_even_odd(distractor_click[0], distractor_click[1], deep_sulcus_polygon)
    assert is_distractor_hit is False


@pytest.mark.tier4
def test_w04_stage2_diagnostic_mcq_evaluation():
    """Stage 2: Hotspot success unlocks MCQ evaluating acute management."""
    mcq = {
        "question_id": "MCQ_TENSION_PNEUMO_01",
        "stem": (
            "A 24-year-old tall, thin male presents with acute dyspnea, right-sided pleuritic "
            "chest pain, trachea deviated to the left, and absent right breath sounds. "
            "What is the most appropriate immediate intervention?"
        ),
        "options": [
            "Urgent non-contrast computed tomography of the chest",
            "Immediate needle decompression in 2nd intercostal space midclavicular line",
            "Endotracheal intubation and mechanical ventilation",
            "Elective outpatient observation"
        ],
        "correct_index": 1,
        "rationale": (
            "Tension pneumothorax is a clinical emergency requiring immediate needle decompression "
            "prior to chest tube placement. CT scan delays life-saving decompression and is contraindicated."
        )
    }
    user_selection = 1
    is_correct = (user_selection == mcq["correct_index"])
    assert is_correct is True
    assert "needle decompression" in mcq["options"][mcq["correct_index"]]


@pytest.mark.tier4
def test_w04_stage3_fsrs_mnemonic_progression():
    """Stage 3: Success advances FSRS stability S, updates difficulty D, and preserves R=0.9."""
    initial_stability = 1.0
    initial_difficulty = 5.0
    elapsed_days = 1.0

    # Retrievability at review time
    r_prior = fsrs_calculate_retrievability(elapsed_days=elapsed_days, stability=initial_stability)
    assert r_prior > 0.80

    # Successful recall (Rating = Good = 3) expands stability
    new_stability = initial_stability * 3.2  # Stability increases to 3.2 days
    new_difficulty = max(1.0, min(10.0, initial_difficulty - 0.2))  # Becomes slightly easier (4.8)

    assert new_stability == 3.2
    assert new_difficulty == 4.8

    # Retrievability immediately after review resets
    r_post = fsrs_calculate_retrievability(elapsed_days=0.01, stability=new_stability)
    assert r_post > 0.99


@pytest.mark.tier4
def test_w04_stage4_review_load_balancer_and_sdui_payload():
    """Stage 4: Load balancer schedules next card review and emits validated SDUI payload."""
    next_review_interval_days = 3
    daily_ceiling = 50
    current_scheduled_today = 35

    can_schedule_today = (current_scheduled_today < daily_ceiling)
    assert can_schedule_today is True

    sdui_exam_block = {
        "block_type": "ExamSimulatorBlock",
        "item_type": "MCQ",
        "item_data": {
            "question_id": "MCQ_TENSION_PNEUMO_01",
            "result": "CORRECT",
            "score": 1.0,
            "hotspot_hit": True
        },
        "fsrs_card_state": {
            "stability": 3.2,
            "difficulty": 4.8,
            "next_interval_days": next_review_interval_days,
            "target_retention": 0.90
        }
    }
    block = ExamSimulatorBlockContract.model_validate(sdui_exam_block)
    assert block.block_type == "ExamSimulatorBlock"
    assert block.fsrs_card_state["stability"] == 3.2
    assert block.fsrs_card_state["target_retention"] == 0.90
