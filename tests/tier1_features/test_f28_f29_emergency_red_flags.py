"""
Tier 1: Feature Coverage Tests for Diagnostic Features 28 through 29.
- Feature 28: Log-Sum-Exp Softmax Normalizer
- Feature 29: Active Discrimination (NBQ)
"""

import math
import numpy as np
import pytest
from medclient.sidecar_python.src.implementations.softmax_normalizer import LogSumExpNormalizer
from medclient.sidecar_python.src.implementations.active_discriminator import ActiveDiscriminator
from tests.conftest import log_sum_exp, compute_softmax_probabilities

# Feature 28: Log-Sum-Exp Softmax Normalizer
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f28_log_sum_exp_numerical_stability():
    """Verify Log-Sum-Exp avoids overflow on large logits (>700)."""
    normalizer = LogSumExpNormalizer()
    large_logits = [1000.0, 1002.0, 999.0]
    probs = normalizer.normalize_logits(large_logits)
    assert len(probs) == 3
    assert not np.any(np.isnan(probs))
    assert math.isclose(float(np.sum(probs)), 1.0, rel_tol=1e-5)


@pytest.mark.tier1
def test_f28_softmax_probabilities_sum_to_one():
    """Verify normalized probabilities sum to 1.0 within floating tolerance."""
    normalizer = LogSumExpNormalizer()
    logits = [2.0, 1.0, 0.1, -1.0]
    probs = normalizer.normalize_logits(logits)
    assert math.isclose(float(np.sum(probs)), 1.0, rel_tol=1e-5)


@pytest.mark.tier1
def test_f28_softmax_zero_probability_for_negative_infinity():
    """Verify -inf logit produces exactly 0.0 probability."""
    normalizer = LogSumExpNormalizer()
    logits = [3.0, 1.0, -float("inf")]
    probs = normalizer.normalize_logits(logits)
    assert probs[2] == 0.0
    assert math.isclose(float(np.sum(probs[:2])), 1.0, rel_tol=1e-5)


@pytest.mark.tier1
def test_f28_softmax_monotonicity():
    """Verify higher logits produce strictly higher probabilities."""
    normalizer = LogSumExpNormalizer()
    logits = [1.0, 2.5, 4.0]
    probs = normalizer.normalize_logits(logits)
    assert probs[0] < probs[1] < probs[2]


@pytest.mark.tier1
def test_f28_uniform_probabilities_on_identical_logits():
    """Verify identical logits yield equal probabilities."""
    normalizer = LogSumExpNormalizer()
    logits = [2.0, 2.0, 2.0, 2.0]
    probs = normalizer.normalize_logits(logits)
    assert math.isclose(probs[0], 0.25, rel_tol=1e-5)
    assert math.isclose(probs[1], 0.25, rel_tol=1e-5)


# ---------------------------------------------------------------------------
# Feature 29: Active Discrimination (NBQ)
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f29_nbq_information_gain_ranking():
    """Verify NBQ selects question that maximizes information gain per cost."""
    discriminator = ActiveDiscriminator(probability_gap_threshold=0.20)
    result = discriminator.select_next_best_question(
        candidate_a="I21.0",
        prob_a=0.52,
        candidate_b="I30.0",
        prob_b=0.48,
        uninvestigated_features=["HP:0001", "HP:0002"],
        feature_costs={"HP:0001": 1.0, "HP:0002": 1.0},
        feature_labels={"HP:0001": "Feature 1", "HP:0002": "Feature 2"},
        feature_probs_a={"HP:0001": 0.90, "HP:0002": 0.50},
        feature_probs_b={"HP:0001": 0.10, "HP:0002": 0.50},
    )
    assert result is not None
    assert result["feature_code"] == "HP:0001"


@pytest.mark.tier1
def test_f29_nbq_cost_weighting_tradeoff():
    """Verify high-cost test is deprioritized over cheaper test with comparable gain."""
    discriminator = ActiveDiscriminator(probability_gap_threshold=0.20)
    result = discriminator.select_next_best_question(
        candidate_a="I21.0",
        prob_a=0.51,
        candidate_b="I30.0",
        prob_b=0.49,
        uninvestigated_features=["F_EXPENSIVE", "F_CHEAP"],
        feature_costs={"F_EXPENSIVE": 100.0, "F_CHEAP": 1.0},
        feature_labels={"F_EXPENSIVE": "CT Scan", "F_CHEAP": "Physical Sign"},
        feature_probs_a={"F_EXPENSIVE": 0.95, "F_CHEAP": 0.85},
        feature_probs_b={"F_EXPENSIVE": 0.05, "F_CHEAP": 0.15},
    )
    assert result is not None
    assert result["feature_code"] == "F_CHEAP"


@pytest.mark.tier1
def test_f29_nbq_excludes_already_answered_questions():
    """Verify already answered or irrelevant features are skipped."""
    discriminator = ActiveDiscriminator(probability_gap_threshold=0.20)
    result = discriminator.select_next_best_question(
        candidate_a="I21.0",
        prob_a=0.50,
        candidate_b="I30.0",
        prob_b=0.50,
        uninvestigated_features=["F_NEUTRAL"],
        feature_costs={"F_NEUTRAL": 1.0},
        feature_probs_a={"F_NEUTRAL": 0.50},
        feature_probs_b={"F_NEUTRAL": 0.50},
    )
    # Neutral feature with no discriminative power yields None
    assert result is None


@pytest.mark.tier1
def test_f29_nbq_shannon_entropy_calculation():
    """Verify binary entropy calculation in discriminator."""
    discriminator = ActiveDiscriminator()
    entropy = discriminator._binary_entropy(0.5)
    assert math.isclose(entropy, 1.0, rel_tol=1e-5)


@pytest.mark.tier1
def test_f29_nbq_empty_candidates_returns_null_recommendation():
    """Verify separated candidates (gap >= threshold) return None."""
    discriminator = ActiveDiscriminator(probability_gap_threshold=0.15)
    result = discriminator.select_next_best_question(
        candidate_a="I21.0",
        prob_a=0.90,
        candidate_b="I30.0",
        prob_b=0.10,
        uninvestigated_features=["F1"],
        feature_costs={"F1": 1.0},
    )
    assert result is None
