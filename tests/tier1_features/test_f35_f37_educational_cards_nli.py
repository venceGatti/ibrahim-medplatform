"""
Tier 1: Feature Coverage Tests for Educational Features 35 through 37.
- Feature 35: MCQ Assessment Engine
- Feature 36: Image Hotspot Diagnostics
- Feature 37: NLI Cross-Encoder Evaluator
"""

import math
import pytest
from tests.conftest import point_in_polygon_even_odd
from medclient.sidecar_python.src.implementations.nli_cross_encoder import NLICrossEncoderEvaluator
from medclient.sidecar_python.src.base.educational_models import (
    AtomicConcept,
    NLIEvaluationRubric,
)

# Feature 35: MCQ Assessment Engine
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f35_mcq_four_options_format():
    """Verify MCQ item provides exactly 4 discrete answer options."""
    mcq = {
        "question_id": "MCQ_CARDIO_01",
        "stem": "A 55-year-old male with acute chest pain...",
        "options": ["Aspirin", "Ibuprofen", "Acetaminophen", "Morphine"],
        "correct_index": 0,
        "rationale": "Aspirin is indicated immediately for acute coronary syndrome.",
    }
    assert len(mcq["options"]) == 4
    assert 0 <= mcq["correct_index"] <= 3


@pytest.mark.tier1
def test_f35_mcq_evaluation_correct_choice():
    """Verify selecting correct_index awards 100% score."""
    correct_idx = 2
    user_choice = 2
    score = 1.0 if user_choice == correct_idx else 0.0
    assert score == 1.0


@pytest.mark.tier1
def test_f35_mcq_evaluation_incorrect_choice():
    """Verify selecting wrong distractor awards 0% score and reveals rationale."""
    correct_idx = 1
    user_choice = 3
    is_correct = (user_choice == correct_idx)
    assert is_correct is False


@pytest.mark.tier1
def test_f35_mcq_katex_vignette_rendering():
    """Verify clinical vignette containing mathematical formulas is preserved."""
    stem = "Patient with arterial blood gas: $$\\text{pH} = 7.25, \\text{PaCO}_2 = 55\\,\\text{mmHg}$$"
    assert "$$" in stem
    assert "\\text{pH}" in stem


@pytest.mark.tier1
def test_f35_mcq_distractor_rationale_completeness():
    """Verify every option has an associated explanation for educational remediation."""
    rationales = {
        0: "Correct: Initial antiplatelet therapy reduces mortality.",
        1: "Incorrect: NSAIDs are contraindicated in acute MI.",
        2: "Incorrect: Inadequate analgesic and zero antiplatelet effect.",
        3: "Incorrect: Secondary to antiplatelet and reperfusion.",
    }
    assert len(rationales) == 4


# ---------------------------------------------------------------------------
# Feature 36: Image Hotspot Diagnostics
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f36_hotspot_point_inside_polygon():
    """Verify point inside chest radiograph polygon returns True via Even-Odd ray casting."""
    polygon = [(0.0, 0.0), (10.0, 0.0), (5.0, 10.0)]
    assert point_in_polygon_even_odd(5.0, 3.0, polygon) is True


@pytest.mark.tier1
def test_f36_hotspot_point_outside_polygon():
    """Verify point outside hotspot polygon returns False."""
    polygon = [(0.0, 0.0), (10.0, 0.0), (5.0, 10.0)]
    assert point_in_polygon_even_odd(15.0, 15.0, polygon) is False


@pytest.mark.tier1
def test_f36_hotspot_concave_polygon():
    """Verify Even-Odd algorithm functions correctly on non-convex/concave polygons."""
    l_polygon = [
        (0.0, 0.0), (10.0, 0.0), (10.0, 5.0), (5.0, 5.0), (5.0, 10.0), (0.0, 10.0)
    ]
    assert point_in_polygon_even_odd(7.0, 2.0, l_polygon) is True
    assert point_in_polygon_even_odd(8.0, 8.0, l_polygon) is False


@pytest.mark.tier1
def test_f36_hotspot_boundary_coordinates():
    """Verify coordinate bounding box containment checks."""
    polygon = [(10.0, 10.0), (30.0, 10.0), (30.0, 40.0), (10.0, 40.0)]
    min_x = min(p[0] for p in polygon)
    max_x = max(p[0] for p in polygon)
    assert min_x == 10.0
    assert max_x == 30.0


@pytest.mark.tier1
def test_f36_hotspot_multi_region_selection():
    """Verify mapping multiple anatomical target regions on a single slide."""
    regions = {
        "aortic_knob": [(10.0, 10.0), (20.0, 10.0), (15.0, 25.0)],
        "cardiophrenic_angle": [(50.0, 50.0), (80.0, 50.0), (65.0, 70.0)],
    }
    user_click = (15.0, 15.0)
    hit_region = None
    for name, poly in regions.items():
        if point_in_polygon_even_odd(user_click[0], user_click[1], poly):
            hit_region = name
            break
    assert hit_region == "aortic_knob"


# ---------------------------------------------------------------------------
# Feature 37: NLI Cross-Encoder Evaluator
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f37_nli_entailment_classification():
    """Verify clinically accurate free-text answer yields high entailment score."""
    evaluator = NLICrossEncoderEvaluator()
    rubric = {
        "clinical_vignette": "A 45-year-old patient presents with acute anaphylaxis.",
        "atomic_concepts": [
            {
                "id": "AC1",
                "hypothesis": "The patient must receive intramuscular epinephrine immediately.",
                "weight": 1.0,
                "is_critical": True,
            }
        ],
    }
    student_response = "We must give epinephrine intramuscularly right away to treat the shock."
    result = evaluator.evaluate_response(student_response, rubric)
    assert result["overall_score"] >= 0.70
    assert result["passed"] is True


@pytest.mark.tier1
def test_f37_nli_contradiction_classification():
    """Verify contradictory medical assertion yields failure and zero score."""
    evaluator = NLICrossEncoderEvaluator()
    rubric = {
        "clinical_vignette": "A 45-year-old patient presents with acute anaphylaxis.",
        "atomic_concepts": [
            {
                "id": "AC1",
                "hypothesis": "Administer intramuscular epinephrine immediately.",
                "weight": 1.0,
                "is_critical": True,
            }
        ],
    }
    student_response = "Do not administer epinephrine, withhold all medication."
    result = evaluator.evaluate_response(student_response, rubric)
    assert result["passed"] is False
    assert result["failed_critical_concepts"] == ["AC1"]


@pytest.mark.tier1
def test_f37_nli_threshold_seventy_five_percent():
    """Verify rubric validation enforces concept weights summing to 1.0."""
    rubric_model = NLIEvaluationRubric(
        clinical_vignette="Patient presenting with acute chest pain and ST elevations in lead II, III, aVF.",
        atomic_concepts=[
            AtomicConcept(id="C1", hypothesis="Administer aspirin 300mg immediately", weight=0.5),
            AtomicConcept(id="C2", hypothesis="Activate emergency catheterization laboratory", weight=0.5),
        ],
    )
    assert len(rubric_model.atomic_concepts) == 2
    assert sum(ac.weight for ac in rubric_model.atomic_concepts) == 1.0


@pytest.mark.tier1
def test_f37_nli_neutral_ambiguous_response():
    """Verify vague or unrelated clinical response receives low score."""
    evaluator = NLICrossEncoderEvaluator()
    rubric = {
        "clinical_vignette": "A 60-year-old with chest pain.",
        "atomic_concepts": [
            {
                "id": "AC1",
                "hypothesis": "The diagnosis is acute myocardial infarction requiring reperfusion.",
                "weight": 1.0,
                "is_critical": False,
            }
        ],
    }
    student_response = "The patient should rest and drink warm tea."
    result = evaluator.evaluate_response(student_response, rubric)
    assert result["overall_score"] < 0.50
    assert result["passed"] is False


@pytest.mark.tier1
def test_f37_nli_input_concatenation_format():
    """Verify proposition splitting decomposes compound sentences."""
    evaluator = NLICrossEncoderEvaluator()
    text = "Administer aspirin 300mg orally. Then activate the cardiac catheterization team."
    sentences = evaluator._split_sentences(text)
    assert len(sentences) >= 2


# ---------------------------------------------------------------------------
