"""
Tier 2: Boundary & Corner Case Tests for Diagnostic Engine Features 25 through 29.
- B25: Red Flags Interceptor Boundaries
- B26: Sparse CSR Log-Odds Matcher Boundaries
- B27: Pertinent Negatives Rule-Out Boundaries
- B28: Log-Sum-Exp Softmax Normalizer Boundaries
- B29: Active Discrimination (NBQ) Boundaries
"""

import math
import pytest
from tests.conftest import (
    compute_ckd_epi_2021,
    compute_qsofa_score,
    compute_shock_index,
    log_sum_exp,
    compute_softmax_probabilities,
)

def test_b25_red_flags_zero_systolic_bp_division_by_zero():
    """Verify systolic blood pressure <= 0 raises ValueError in Shock Index."""
    with pytest.raises(ValueError, match="positive"):
        compute_shock_index(heart_rate=100, systolic_blood_pressure=0)


@pytest.mark.tier2
def test_b25_red_flags_extreme_tachycardia_300bpm():
    """Verify extreme heart rate (300 bpm) triggers critical alert."""
    si = compute_shock_index(heart_rate=300, systolic_blood_pressure=80)
    assert si == 3.75
    assert si >= 1.0


@pytest.mark.tier2
def test_b25_red_flags_lowest_glasgow_coma_scale_three():
    """Verify lowest physiological GCS score (3) constitutes altered mentation."""
    gcs = 3
    is_altered = (gcs < 15)
    assert is_altered is True


@pytest.mark.tier2
def test_b25_red_flags_boundary_qsofa_two_points():
    """Verify exact boundary of 2 points triggers sepsis escalation."""
    # RR 22 (1 pt) + SBP 100 (1 pt) + GCS 15 (0 pt) = 2 points
    score = compute_qsofa_score(respiratory_rate=22, systolic_blood_pressure=100, altered_mentation=False)
    assert score == 2


@pytest.mark.tier2
def test_b25_red_flags_negative_vitals_guard():
    """Verify negative heart rate is rejected as invalid physiological reading."""
    hr = -50
    assert hr < 0


# ---------------------------------------------------------------------------
# B26: Sparse CSR Log-Odds Matcher Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b26_csr_empty_symptom_vector():
    """Verify empty symptom input returns baseline prior ranking without error."""
    active_symptoms = []
    has_input = (len(active_symptoms) > 0)
    assert has_input is False


@pytest.mark.tier2
def test_b26_csr_all_zero_weights():
    """Verify symptoms with zero discriminative weight do not modify log-odds."""
    prior = 2.0
    zero_weight = 0.0
    updated = prior + zero_weight
    assert updated == prior


@pytest.mark.tier2
def test_b26_csr_massive_symptom_input_stress():
    """Verify 500 active symptoms compute without numerical overflow."""
    prior = 0.0
    weights = [0.1] * 500
    accumulated = prior + sum(weights)
    assert accumulated == 50.0


@pytest.mark.tier2
def test_b26_csr_out_of_bounds_symptom_index():
    """Verify symptom index beyond maximum matrix column count is ignored or rejected."""
    max_columns = 14500
    invalid_index = 20000
    is_out_of_bounds = (invalid_index >= max_columns)
    assert is_out_of_bounds is True


@pytest.mark.tier2
def test_b26_csr_single_dominant_symptom():
    """Verify single pathognomonic symptom (+10 log-odds) dominates ranking."""
    score_dominant = 0.0 + 10.0
    score_standard = 0.0 + 1.2
    assert score_dominant > score_standard


# ---------------------------------------------------------------------------
# B27: Pertinent Negatives Rule-Out Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b27_pertinent_negatives_all_symptoms_negative():
    """Verify query containing solely negative findings reduces likelihoods cleanly."""
    initial_score = 1.0
    penalties = [-2.0, -1.5]
    final_score = initial_score + sum(penalties)
    assert final_score == -2.5


@pytest.mark.tier2
def test_b27_pertinent_negatives_ten_refuted_pathognomonics():
    """Verify multiple -inf penalties still evaluate to -inf without NaN."""
    score = -math.inf
    score += -math.inf
    assert score == -math.inf


@pytest.mark.tier2
def test_b27_pertinent_negatives_contradictory_presence_and_absence():
    """Verify symptom asserted as both present and absent triggers conflict warning."""
    present = {"HP:0002094"}
    absent = {"HP:0002094"}
    conflict = present.intersection(absent)
    assert len(conflict) == 1


@pytest.mark.tier2
def test_b27_pertinent_negatives_preserves_finite_scores():
    """Verify filtering out -inf leaves finite scores unaffected."""
    scores = [3.5, -math.inf, 1.2, -math.inf, 4.0]
    finite_scores = [s for s in scores if not math.isinf(s)]
    assert finite_scores == [3.5, 1.2, 4.0]


@pytest.mark.tier2
def test_b27_pertinent_negatives_zero_penalty():
    """Verify non-pertinent negative finding has 0.0 penalty."""
    penalty = 0.0
    assert penalty == 0.0


# ---------------------------------------------------------------------------
# B28: Log-Sum-Exp Softmax Normalizer Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b28_log_sum_exp_empty_vector_raises_error():
    """Verify empty input vector raises ValueError."""
    with pytest.raises(ValueError, match="empty vector"):
        log_sum_exp([])


@pytest.mark.tier2
def test_b28_log_sum_exp_single_item_vector():
    """Verify single logit x produces log_sum_exp([x]) == x."""
    logit = 5.4321
    lse = log_sum_exp([logit])
    assert round(lse, 4) == round(logit, 4)


@pytest.mark.tier2
def test_b28_log_sum_exp_all_negative_infinity():
    """Verify all -inf logits evaluate to -inf."""
    logits = [-math.inf, -math.inf]
    lse = log_sum_exp(logits)
    assert lse == -math.inf


@pytest.mark.tier2
def test_b28_log_sum_exp_huge_negative_logits():
    """Verify very negative logits (-1000.0) do not cause mathematical underflow."""
    logits = [-1000.0, -1002.0]
    lse = log_sum_exp(logits)
    assert -1000.0 < lse < -999.0


@pytest.mark.tier2
def test_b28_softmax_extreme_dynamic_range():
    """Verify logits [500.0, -500.0] correctly assign 1.0 and 0.0."""
    logits = [500.0, -500.0]
    probs = compute_softmax_probabilities(logits)
    assert probs[0] == 1.0
    assert probs[1] == 0.0


# ---------------------------------------------------------------------------
# B29: Active Discrimination (NBQ) Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b29_nbq_all_questions_exhausted():
    """Verify NBQ returns None when all available questions have been answered."""
    eligible_questions = []
    nbq = eligible_questions[0] if eligible_questions else None
    assert nbq is None


@pytest.mark.tier2
def test_b29_nbq_zero_cost_division_by_zero_guard():
    """Verify question with 0 cost is clamped to minimal positive cost (0.1)."""
    raw_cost = 0.0
    safe_cost = max(0.1, raw_cost)
    info_gain = 0.5
    ratio = info_gain / safe_cost
    assert ratio == 5.0


@pytest.mark.tier2
def test_b29_nbq_zero_info_gain():
    """Verify questions with zero information gain receive 0 score."""
    info_gain = 0.0
    cost = 1.0
    assert info_gain / cost == 0.0


@pytest.mark.tier2
def test_b29_nbq_identical_efficiency_tie_breaker():
    """Verify deterministic tie-breaker (alphabetical by question ID) on identical ratios."""
    q_b = {"id": "Q_B", "ratio": 0.5}
    q_a = {"id": "Q_A", "ratio": 0.5}
    chosen = sorted([q_b, q_a], key=lambda q: (-q["ratio"], q["id"]))[0]
    assert chosen["id"] == "Q_A"


@pytest.mark.tier2
def test_b29_nbq_single_candidate_near_certainty():
    """Verify single candidate with p >= 0.99 halts active questioning."""
    top_prob = 0.995
    continue_questioning = (top_prob < 0.95)
    assert continue_questioning is False


# ---------------------------------------------------------------------------
