"""Tests for NLP, Red Flags, Log-Odds, Rule-Out, Softmax, and NBQ."""
import numpy as np
import pytest

from src.implementations.symspell_checker import MedicalSymSpellChecker
from src.implementations.inverted_dictionary import InvertedLexicalDictionary
from src.implementations.onnx_semantic import OnnxSemanticEmbeddingEngine
from src.implementations.red_flags import RedFlagsInterceptor
from src.implementations.csr_ranker import SparseCSRLogOddsRanker
from src.implementations.pertinent_negatives import PertinentNegativesEvaluator
from src.implementations.softmax_normalizer import LogSumExpNormalizer
from src.implementations.active_discriminator import ActiveDiscriminator


def test_symspell_medical_spellchecker():
    """Verify typo correction within edit distance 2 for medical terms."""
    checker = MedicalSymSpellChecker()
    # Typo: 'dispneaa' -> 'dispnea'
    suggestions = checker.lookup("dispneaa", max_edit_distance=2)
    assert len(suggestions) > 0
    assert suggestions[0]["term"] == "dispnea"
    assert suggestions[0]["distance"] == 1


def test_inverted_lexical_dictionary():
    """Verify colloquial expressions resolve to HPO and ICD-10 nodes."""
    inv_dict = InvertedLexicalDictionary()
    res = inv_dict.resolve_colloquial("fame d'aria continua")
    assert res is not None
    assert res["target_code"] == "HP:0002094"
    assert res["preferred_label"] == "Dyspnea"


def test_semantic_embedding_and_cosine_similarity():
    """Verify 384-dimensional normalized vector and dot product similarity."""
    engine = OnnxSemanticEmbeddingEngine()
    v1 = engine.encode("infarto miocardico acuto")
    assert v1.shape == (384,)
    norm = np.linalg.norm(v1)
    assert abs(norm - 1.0) < 1e-4

    # Matrix similarity
    matrix = np.vstack([v1, engine.encode("polmonite lobare")])
    sims = engine.compute_similarity(v1, matrix)
    assert len(sims) == 2
    assert abs(sims[0] - 1.0) < 1e-4  # Identical vector has similarity 1.0


def test_red_flags_shock_index_and_qsofa():
    """Verify immediate critical triage on Shock Index >= 1.0 and qSOFA >= 2."""
    interceptor = RedFlagsInterceptor()
    # Shock Index: HR=120, SBP=85 -> SI=1.41 >= 1.0
    vitals = {
        "heart_rate_bpm": 120.0,
        "systolic_bp_mmhg": 85.0,
        "respiratory_rate_bpm": 24.0,
        "spo2_percent": 90.0,
        "temperature_celsius": 38.5,
        "avpu_scale": "V",
        "gcs_score": 13,
        "supplemental_o2": False,
        "hypercapnic_risk": False,
    }
    assessment = interceptor.evaluate(vitals)
    assert assessment["alert_level"] == "RED_CRITICAL"
    assert "CRITICAL_SHOCK_INDEX_GE_1" in assessment["critical_triggers"]
    assert "QSOFA_SCORE_GE_2" in assessment["critical_triggers"]


def test_sparse_csr_log_odds_ranker():
    """Verify CSR log-odds scoring with pathognomonic multiplier and smoothing."""
    ranker = SparseCSRLogOddsRanker()
    diseases = [
        {"icd10_code": "I21.0", "preferred_label": "STEMI", "prior": 0.01},
        {"icd10_code": "J18.9", "preferred_label": "Pneumonia", "prior": 0.05},
    ]
    features = [
        {"hpo_id": "HP:0001945", "name": "Fever"},
        {"hpo_id": "HP:0100749", "name": "Chest Pain"},
    ]
    co_occurrences = [
        {"disease_code": "I21.0", "feature_code": "HP:0100749", "count_dj": 100, "count_fi_dj": 90, "is_pathognomonic": True},
        {"disease_code": "J18.9", "feature_code": "HP:0001945", "count_dj": 100, "count_fi_dj": 80, "is_pathognomonic": False},
    ]
    ranker.load_knowledge_base(diseases, features, co_occurrences)

    scores = ranker.score_diseases(
        positive_features=["HP:0100749"],
        negative_features=[],
        cluster_assignments={},
        pathognomonic_flags={},
    )
    assert len(scores) == 2
    # I21.0 should have high positive log-odds due to pathognomonic chest pain
    score_map = {icd: logit for icd, logit, _, _ in scores}
    assert score_map["I21.0"] > score_map["J18.9"]


def test_pertinent_negatives_rule_out():
    """Verify strict -inf exclusion when mandatory feature (P >= 0.99) is refuted."""
    evaluator = PertinentNegativesEvaluator()
    candidates = {"I21.0": 8.0, "J18.9": 5.0}
    # Mandatory symptom HP:0100749 for I21.0
    feature_probs = {("I21.0", "HP:0100749"): 0.995}

    updated = evaluator.apply_rule_outs(
        candidate_scores=candidates,
        refuted_features=["HP:0100749"],
        feature_probs=feature_probs,
    )
    assert updated["I21.0"] == -float("inf")
    assert updated["J18.9"] == 5.0


def test_log_sum_exp_softmax_normalizer():
    """Verify stable softmax sums to 1.0 and properly handles -inf."""
    normalizer = LogSumExpNormalizer()
    logits = [10.0, 5.0, -float("inf")]
    probs = normalizer.normalize_logits(logits)
    assert len(probs) == 3
    assert abs(sum(probs) - 1.0) < 1e-6
    assert probs[2] == 0.0
    assert probs[0] > probs[1]


def test_active_discriminator_nbq():
    """Verify NBQ selects feature maximizing information gain per cost."""
    discriminator = ActiveDiscriminator(probability_gap_threshold=0.15)
    nbq = discriminator.select_next_best_question(
        candidate_a="I21.0",
        prob_a=0.52,
        candidate_b="J18.9",
        prob_b=0.48,
        uninvestigated_features=["HP:0001945", "HP:0002094"],
        feature_costs={"HP:0001945": 1.0, "HP:0002094": 2.0},
        feature_labels={"HP:0001945": "Fever", "HP:0002094": "Dyspnea"},
        feature_probs_a={"HP:0001945": 0.05, "HP:0002094": 0.50},
        feature_probs_b={"HP:0001945": 0.90, "HP:0002094": 0.55},
    )
    assert nbq is not None
    assert nbq["target_hpo_id"] == "HP:0001945"
    assert nbq["expected_information_gain"] > 0
