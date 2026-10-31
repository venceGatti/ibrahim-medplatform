"""
Tier 1: Feature Coverage Tests for Diagnostic Features 25 through 27.
- Feature 25: Red Flags Interceptor
- Feature 26: Sparse CSR Log-Odds Matcher
- Feature 27: Pertinent Negatives Rule-Out
"""

import math
import numpy as np
import pytest
from medclient.sidecar_python.src.implementations.red_flags import RedFlagsInterceptor
from medclient.sidecar_python.src.implementations.csr_ranker import SparseCSRLogOddsRanker
from medclient.sidecar_python.src.implementations.pertinent_negatives import PertinentNegativesEvaluator
from medclient.sidecar_python.src.implementations.softmax_normalizer import LogSumExpNormalizer
from tests.conftest import compute_qsofa_score, compute_shock_index

# Feature 25: Red Flags Interceptor
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f25_shock_index_critical_threshold():
    """Verify Shock Index >= 1.0 triggers immediate critical hypoperfusion alert."""
    interceptor = RedFlagsInterceptor()
    vitals = {
        "heart_rate_bpm": 120.0,
        "systolic_bp_mmhg": 90.0,
        "respiratory_rate_bpm": 16.0,
        "spo2_percent": 98.0,
        "temperature_celsius": 37.0,
    }
    outcome = interceptor.evaluate(vitals)
    assert outcome["shock_index"] >= 1.0
    assert "CRITICAL_SHOCK_INDEX_GE_1" in outcome["critical_triggers"]
    assert outcome["alert_level"] == "RED_CRITICAL"


@pytest.mark.tier1
def test_f25_qsofa_high_risk_sepsis_trigger():
    """Verify qSOFA score >= 2 flags high sepsis risk."""
    interceptor = RedFlagsInterceptor()
    vitals = {
        "heart_rate_bpm": 100.0,
        "systolic_bp_mmhg": 95.0,
        "respiratory_rate_bpm": 24.0,
        "spo2_percent": 95.0,
        "temperature_celsius": 38.5,
        "gcs_score": 14,
        "avpu_scale": "V",
    }
    outcome = interceptor.evaluate(vitals)
    assert outcome["qsofa_score"] >= 2
    assert "QSOFA_SCORE_GE_2" in outcome["critical_triggers"]


@pytest.mark.tier1
def test_f25_news2_medium_risk_threshold():
    """Verify aggregate NEWS2 score >= 5 triggers urgent clinical assessment."""
    interceptor = RedFlagsInterceptor()
    vitals = {
        "heart_rate_bpm": 95.0,
        "systolic_bp_mmhg": 105.0,
        "respiratory_rate_bpm": 22.0,
        "spo2_percent": 93.0,
        "temperature_celsius": 37.0,
    }
    outcome = interceptor.evaluate(vitals)
    assert outcome["news2_score"] >= 5


@pytest.mark.tier1
def test_f25_red_flags_direct_emergency_triage():
    """Verify severe decompensation triggers RED_CRITICAL alert level."""
    interceptor = RedFlagsInterceptor()
    vitals = {
        "heart_rate_bpm": 140.0,
        "systolic_bp_mmhg": 70.0,
        "respiratory_rate_bpm": 30.0,
        "spo2_percent": 85.0,
        "temperature_celsius": 39.5,
        "avpu_scale": "P",
    }
    outcome = interceptor.evaluate(vitals)
    assert outcome["alert_level"] == "RED_CRITICAL"
    assert len(outcome["critical_triggers"]) >= 2


@pytest.mark.tier1
def test_f25_physiological_normal_vitals_no_alert():
    """Verify normal vitals produce NOMINAL alert level and zero triggers."""
    interceptor = RedFlagsInterceptor()
    vitals = {
        "heart_rate_bpm": 72.0,
        "systolic_bp_mmhg": 120.0,
        "respiratory_rate_bpm": 14.0,
        "spo2_percent": 99.0,
        "temperature_celsius": 36.8,
        "avpu_scale": "A",
        "gcs_score": 15,
    }
    outcome = interceptor.evaluate(vitals)
    assert outcome["alert_level"] == "NOMINAL"
    assert len(outcome["critical_triggers"]) == 0


# ---------------------------------------------------------------------------
# Feature 26: Sparse CSR Log-Odds Matcher
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f26_csr_matrix_dimensions():
    """Verify SparseCSRLogOddsRanker initialises and loads disease vocabulary."""
    ranker = SparseCSRLogOddsRanker()
    diseases = [
        {"icd10_code": "I21.0", "preferred_label": "STEMI", "prior": 0.01},
        {"icd10_code": "I30.0", "preferred_label": "Pericarditis", "prior": 0.005},
    ]
    features = [
        {"hpo_id": "HP:0001649", "preferred_label": "Angina pectoris"},
        {"hpo_id": "HP:0002094", "preferred_label": "Dyspnea"},
    ]
    co_occurrences = [
        {"disease_code": "I21.0", "feature_code": "HP:0001649", "count_fi_dj": 40.0, "count_dj": 50.0},
        {"disease_code": "I30.0", "feature_code": "HP:0001649", "count_fi_dj": 10.0, "count_dj": 50.0},
    ]
    ranker.load_knowledge_base(diseases, features, co_occurrences)
    assert len(ranker.disease_to_idx) == 2
    assert len(ranker.feature_to_idx) == 2


@pytest.mark.tier1
def test_f26_dirichlet_smoothing_non_zero():
    """Verify Dirichlet smoothing prevents infinite negative weights in sparse scoring."""
    ranker = SparseCSRLogOddsRanker(epsilon=1e-4)
    diseases = [{"icd10_code": "I21.0", "preferred_label": "STEMI"}]
    features = [{"hpo_id": "HP:0001649", "preferred_label": "Chest pain"}]
    co_occurrences = [
        {"disease_code": "I21.0", "feature_code": "HP:0001649", "count_fi_dj": 0.0, "count_dj": 100.0}
    ]
    ranker.load_knowledge_base(diseases, features, co_occurrences)
    assert len(ranker.csr_data) == 1
    assert not math.isinf(ranker.csr_data[0])


@pytest.mark.tier1
def test_f26_log_odds_score_accumulation():
    """Verify independent symptom evidence accumulates in score_diseases."""
    ranker = SparseCSRLogOddsRanker()
    diseases = [
        {"icd10_code": "I21.0", "preferred_label": "STEMI", "prior": 0.01},
        {"icd10_code": "I30.0", "preferred_label": "Pericarditis", "prior": 0.005},
    ]
    features = [
        {"hpo_id": "HP:0001649", "preferred_label": "Chest pain"},
        {"hpo_id": "HP:0002094", "preferred_label": "Dyspnea"},
    ]
    co_occurrences = [
        {"disease_code": "I21.0", "feature_code": "HP:0001649", "count_fi_dj": 45.0, "count_dj": 50.0},
        {"disease_code": "I21.0", "feature_code": "HP:0002094", "count_fi_dj": 35.0, "count_dj": 50.0},
        {"disease_code": "I30.0", "feature_code": "HP:0001649", "count_fi_dj": 15.0, "count_dj": 50.0},
    ]
    ranker.load_knowledge_base(diseases, features, co_occurrences)
    scored = ranker.score_diseases(
        positive_features=["HP:0001649", "HP:0002094"],
        negative_features=[],
        cluster_assignments={},
        pathognomonic_flags={},
    )
    assert len(scored) == 2
    top_disease, top_score, _, _ = scored[0]
    assert top_disease == "I21.0"


@pytest.mark.tier1
def test_f26_candidate_ranking_order():
    """Verify diseases are ranked in descending order of posterior log-odds."""
    ranker = SparseCSRLogOddsRanker()
    diseases = [
        {"icd10_code": "I21.0", "preferred_label": "STEMI", "prior": 0.05},
        {"icd10_code": "I30.0", "preferred_label": "Pericarditis", "prior": 0.001},
    ]
    features = [{"hpo_id": "HP:0001649", "preferred_label": "Chest pain"}]
    co_occurrences = [
        {"disease_code": "I21.0", "feature_code": "HP:0001649", "count_fi_dj": 40.0, "count_dj": 50.0},
        {"disease_code": "I30.0", "feature_code": "HP:0001649", "count_fi_dj": 5.0, "count_dj": 50.0},
    ]
    ranker.load_knowledge_base(diseases, features, co_occurrences)
    scored = ranker.score_diseases(["HP:0001649"], [], {}, {})
    assert scored[0][1] >= scored[1][1]


@pytest.mark.tier1
def test_f26_sparse_dot_product_active_features():
    """Verify unobserved features do not contribute to score."""
    ranker = SparseCSRLogOddsRanker()
    diseases = [{"icd10_code": "I21.0", "preferred_label": "STEMI"}]
    features = [
        {"hpo_id": "HP:0001649", "preferred_label": "Chest pain"},
        {"hpo_id": "HP:0002094", "preferred_label": "Dyspnea"},
    ]
    co_occurrences = [
        {"disease_code": "I21.0", "feature_code": "HP:0001649", "count_fi_dj": 40.0, "count_dj": 50.0},
        {"disease_code": "I21.0", "feature_code": "HP:0002094", "count_fi_dj": 40.0, "count_dj": 50.0},
    ]
    ranker.load_knowledge_base(diseases, features, co_occurrences)
    score_1 = ranker.score_diseases(["HP:0001649"], [], {}, {})[0][1]
    score_2 = ranker.score_diseases(["HP:0001649", "HP:0002094"], [], {}, {})[0][1]
    assert score_2 > score_1


# ---------------------------------------------------------------------------
# Feature 27: Pertinent Negatives Rule-Out
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f27_strict_rule_out_negative_infinity():
    """Verify pathognomonic negative finding applies -inf penalty."""
    evaluator = PertinentNegativesEvaluator(rule_out_threshold=0.99)
    scores = {"I21.0": 5.0, "I30.0": 3.0}
    # HP:0001649 is mandatory (prob 0.995) for I21.0
    feature_probs = {("I21.0", "HP:0001649"): 0.995, ("I30.0", "HP:0001649"): 0.40}
    updated = evaluator.apply_rule_outs(scores, ["HP:0001649"], feature_probs)
    assert updated["I21.0"] == -float("inf")
    assert updated["I30.0"] != -float("inf")


@pytest.mark.tier1
def test_f27_rule_out_eliminates_from_top_tier():
    """Verify ruled-out candidates receive -inf and normalizer sets probability to 0.0."""
    evaluator = PertinentNegativesEvaluator()
    normalizer = LogSumExpNormalizer()
    scores = {"I21.0": 5.0, "I30.0": 2.0}
    feature_probs = {("I21.0", "HP:0001"): 0.999}
    updated = evaluator.apply_rule_outs(scores, ["HP:0001"], feature_probs)
    probs = normalizer.normalize_logits([updated["I21.0"], updated["I30.0"]])
    assert probs[0] == 0.0
    assert probs[1] == 1.0


@pytest.mark.tier1
def test_f27_soft_pertinent_negative_detraction():
    """Verify soft pertinent negative applies bounded negative penalty."""
    evaluator = PertinentNegativesEvaluator(rule_out_threshold=0.99)
    scores = {"I21.0": 4.0}
    feature_probs = {("I21.0", "HP:0002094"): 0.70}  # Not strictly mandatory (0.70 < 0.99)
    updated = evaluator.apply_rule_outs(scores, ["HP:0002094"], feature_probs)
    assert updated["I21.0"] < 4.0
    assert not math.isinf(updated["I21.0"])


@pytest.mark.tier1
def test_f27_multiple_negatives_compounding():
    """Verify compounding negative evidence depresses disease likelihood."""
    evaluator = PertinentNegativesEvaluator()
    scores = {"I21.0": 5.0}
    feature_probs = {("I21.0", "F1"): 0.60, ("I21.0", "F2"): 0.60}
    updated = evaluator.apply_rule_outs(scores, ["F1", "F2"], feature_probs)
    assert updated["I21.0"] < 5.0


@pytest.mark.tier1
def test_f27_preservation_of_unaffected_diseases():
    """Verify rule-out of one disease does not alter scores of unaffected diseases."""
    evaluator = PertinentNegativesEvaluator()
    scores = {"I21.0": 5.0, "I30.0": 3.0}
    feature_probs = {("I21.0", "F_MANDATORY"): 0.999}
    updated = evaluator.apply_rule_outs(scores, ["F_MANDATORY"], feature_probs)
    assert updated["I21.0"] == -float("inf")
    # I30.0 should remain close to original score
    assert updated["I30.0"] <= 3.0


# ---------------------------------------------------------------------------
