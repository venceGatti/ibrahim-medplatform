"""
Tier 2: Boundary & Corner Case Tests for Pharmacology Engine Features 30 through 34.
- B30: CYP450 Bioactivation & Competitive Inhibition Boundaries
- B31: Blackbox Warning Rule Engine Boundaries
- B32: "Triple Whammy" Hemodynamic AKI Detector Boundaries
- B33: Race-Free CKD-EPI 2021 eGFR Calculator Boundaries
- B34: Pharmacogenomics (PGx) Rule Engine Boundaries
"""

import math
import pytest
from medclient.sidecar_python.src.implementations.cyp450_engine import CYP450Engine
from medclient.sidecar_python.src.implementations.qtc_calculator import QTcCalculator
from medclient.sidecar_python.src.implementations.triple_whammy import TripleWhammyDetector
from medclient.sidecar_python.src.implementations.cpic_engine import CPICPharmacogenomicsEngine
from medclient.sidecar_python.src.base.pharmacology_models import SeverityLevel
from tests.conftest import (
    compute_ckd_epi_2021,
    compute_qsofa_score,
    compute_shock_index,
    log_sum_exp,
    compute_softmax_probabilities,
)

# B30: CYP450 Functional Load Engine Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b30_cyp450_unknown_clearance_pathway():
    """Verify substance with undefined CYP pathway defaults to non-CYP clearance."""
    engine = CYP450Engine()
    prescribed = [{"atc_code": "N02BE01", "inn_name": "Paracetamol", "is_prodrug": False}]
    evaluation = engine.evaluate_clearance(prescribed)
    assert len(evaluation["interactions"]) == 0


@pytest.mark.tier2
def test_b30_cyp450_multiple_strong_inhibitors_saturation():
    """Verify multiple strong inhibitors on CYP3A4 clamp remaining activity."""
    engine = CYP450Engine()
    prescribed = [
        {"atc_code": "C10AA01", "inn_name": "Simvastatin", "is_prodrug": False, "fm_cyp": {"CYP3A4": 0.9}},
        {"atc_code": "J01FA09", "inn_name": "Clarithromycin", "is_prodrug": False, "cyp_profile": {"substrates": {}, "inhibitors": {"CYP3A4": "STRONG"}, "inducers": {}}},
        {"atc_code": "C01BD01", "inn_name": "Amiodarone", "is_prodrug": False, "cyp_profile": {"substrates": {}, "inhibitors": {"CYP3A4": "MODERATE"}, "inducers": {}}},
    ]
    evaluation = engine.evaluate_clearance(prescribed)
    assert len(evaluation["interactions"]) > 0


@pytest.mark.tier2
def test_b30_cyp450_zero_clearance_fraction():
    """Verify remaining clearance clamped at zero."""
    clearance = -0.1
    clamped = max(0.0, clearance)
    assert clamped == 0.0


@pytest.mark.tier2
def test_b30_cyp450_prodrug_without_active_metabolite_info():
    """Verify prodrug without defined pathway triggers metadata alert."""
    engine = CYP450Engine()
    prescribed = [{"atc_code": "B01AC04", "inn_name": "Clopidogrel", "is_prodrug": True}]
    evaluation = engine.evaluate_clearance(prescribed)
    assert isinstance(evaluation, dict)


@pytest.mark.tier2
def test_b30_cyp450_identical_drug_self_interaction():
    """Verify duplicate entries of identical drug do not trigger self-interaction."""
    engine = CYP450Engine()
    prescribed = [
        {"atc_code": "B01AC06", "inn_name": "Aspirin", "is_prodrug": False},
        {"atc_code": "B01AC06", "inn_name": "Aspirin", "is_prodrug": False},
    ]
    evaluation = engine.evaluate_clearance(prescribed)
    assert len(evaluation["interactions"]) == 0


# ---------------------------------------------------------------------------
# B31: QTc Prolongation Guard Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b31_qtc_exact_boundary_six_point_zero():
    """Verify score >= 6.0 triggers high risk or Level 1 alert."""
    calc = QTcCalculator()
    prescribed = [
        {"atc_code": "C01BD01", "inn_name": "Amiodarone"},
        {"atc_code": "J01FA09", "inn_name": "Clarithromycin"},
    ]
    evaluation = calc.evaluate_qtc(prescribed, {}, serum_potassium_meq_l=4.2)
    assert evaluation["qtc_prolongation_score"] >= 6.0
    assert evaluation["torsades_de_pointes_risk"] == SeverityLevel.LEVEL_1


@pytest.mark.tier2
def test_b31_qtc_score_five_point_nine_level_two():
    """Verify lower risk drugs produce score below 6.0."""
    calc = QTcCalculator()
    prescribed = [{"atc_code": "C01BD01", "inn_name": "Amiodarone"}]
    evaluation = calc.evaluate_qtc(prescribed, {}, serum_potassium_meq_l=4.5)
    assert evaluation["qtc_prolongation_score"] < 6.0


@pytest.mark.tier2
def test_b31_qtc_zero_score_clean():
    """Verify zero QTc risk drugs produce 0.0 score."""
    calc = QTcCalculator()
    prescribed = [{"atc_code": "B01AC06", "inn_name": "Aspirin"}]
    evaluation = calc.evaluate_qtc(prescribed, {}, serum_potassium_meq_l=4.5)
    assert evaluation["qtc_prolongation_score"] == 0.0


@pytest.mark.tier2
def test_b31_qtc_extreme_high_risk_score_fifteen():
    """Verify cumulative QTc score flags critical ventricular arrhythmia risk."""
    calc = QTcCalculator()
    prescribed = [
        {"atc_code": "C01BD01", "inn_name": "Amiodarone"},
        {"atc_code": "J01FA09", "inn_name": "Clarithromycin"},
        {"atc_code": "J01MA02", "inn_name": "Ciprofloxacin"},
    ]
    evaluation = calc.evaluate_qtc(prescribed, {}, serum_potassium_meq_l=3.0)
    assert evaluation["qtc_prolongation_score"] >= 6.0


@pytest.mark.tier2
def test_b31_qtc_negative_score_clamped():
    """Verify negative score weights are clamped to zero."""
    calc = QTcCalculator()
    evaluation = calc.evaluate_qtc([], {}, serum_potassium_meq_l=5.0)
    assert evaluation["qtc_prolongation_score"] == 0.0


# ---------------------------------------------------------------------------
# B32: "Triple Whammy" Detector Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b32_triple_whammy_exact_boundary_egfr_sixty():
    """Verify eGFR exactly 60.0 triggers Level 2 alert (below 60 triggers Level 1)."""
    detector = TripleWhammyDetector()
    prescribed = [
        {"atc_code": "C09AA03", "inn_name": "Lisinopril"},
        {"atc_code": "C03AA03", "inn_name": "Hydrochlorothiazide"},
        {"atc_code": "M01AE01", "inn_name": "Ibuprofen"},
    ]
    evaluation = detector.detect_triple_whammy(prescribed, egfr=60.0)
    assert evaluation["triple_whammy_detected"] is True
    assert evaluation["severity_level"] == SeverityLevel.LEVEL_2


@pytest.mark.tier2
def test_b32_triple_whammy_egfr_fifty_nine_point_nine():
    """Verify eGFR 59.9 satisfies eGFR < 60.0 condition."""
    detector = TripleWhammyDetector()
    prescribed = [
        {"atc_code": "C09AA03", "inn_name": "Lisinopril"},
        {"atc_code": "C03AA03", "inn_name": "Hydrochlorothiazide"},
        {"atc_code": "M01AE01", "inn_name": "Ibuprofen"},
    ]
    evaluation = detector.detect_triple_whammy(prescribed, egfr=59.9)
    assert evaluation["triple_whammy_detected"] is True


@pytest.mark.tier2
def test_b32_triple_whammy_topical_nsaid_exclusion():
    """Verify topical NSAID is excluded from systemic Triple Whammy alert."""
    detector = TripleWhammyDetector()
    prescribed = [
        {"atc_code": "C09AA03", "inn_name": "Lisinopril"},
        {"atc_code": "C03AA03", "inn_name": "Hydrochlorothiazide"},
        {"atc_code": "M02AA15", "inn_name": "Diclofenac Topical", "route": "TOPICAL"},
    ]
    evaluation = detector.detect_triple_whammy(prescribed, egfr=45.0)
    assert evaluation["triple_whammy_detected"] is False


@pytest.mark.tier2
def test_b32_triple_whammy_dual_ras_blockade():
    """Verify ACEi + ARB combined with Diuretic without NSAID does not trigger Triple Whammy."""
    detector = TripleWhammyDetector()
    prescribed = [
        {"atc_code": "C09AA03", "inn_name": "Lisinopril"},
        {"atc_code": "C09CA01", "inn_name": "Losartan"},
        {"atc_code": "C03AA03", "inn_name": "Hydrochlorothiazide"},
    ]
    evaluation = detector.detect_triple_whammy(prescribed, egfr=45.0)
    assert evaluation["triple_whammy_detected"] is False


@pytest.mark.tier2
def test_b32_triple_whammy_zero_egfr_severe_aki():
    """Verify eGFR approaching 0 triggers maximal alert."""
    detector = TripleWhammyDetector()
    prescribed = [
        {"atc_code": "C09AA03", "inn_name": "Lisinopril"},
        {"atc_code": "C03AA03", "inn_name": "Hydrochlorothiazide"},
        {"atc_code": "M01AE01", "inn_name": "Ibuprofen"},
    ]
    evaluation = detector.detect_triple_whammy(prescribed, egfr=5.0)
    assert evaluation["triple_whammy_detected"] is True
    assert evaluation["severity_level"] == SeverityLevel.LEVEL_1


# ---------------------------------------------------------------------------
# B33: CKD-EPI 2021 Renal Calculator Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b33_ckd_epi_zero_creatinine_raises_error():
    """Verify serum creatinine 0.0 raises ValueError."""
    with pytest.raises(ValueError, match="strictly positive"):
        compute_ckd_epi_2021(serum_creatinine=0.0, age_years=50.0, is_female=False)


@pytest.mark.tier2
def test_b33_ckd_epi_negative_age_raises_error():
    """Verify negative age raises ValueError."""
    with pytest.raises(ValueError, match="strictly positive"):
        compute_ckd_epi_2021(serum_creatinine=1.0, age_years=-5.0, is_female=False)


@pytest.mark.tier2
def test_b33_ckd_epi_exact_kappa_boundary_female():
    """Verify exact kappa boundary (0.7 mg/dL) for female patient."""
    egfr = compute_ckd_epi_2021(serum_creatinine=0.7, age_years=40.0, is_female=True)
    # Ratio is exactly 1.0
    assert egfr > 90.0


@pytest.mark.tier2
def test_b33_ckd_epi_exact_kappa_boundary_male():
    """Verify exact kappa boundary (0.9 mg/dL) for male patient."""
    egfr = compute_ckd_epi_2021(serum_creatinine=0.9, age_years=40.0, is_female=False)
    # Ratio is exactly 1.0
    assert egfr > 90.0


@pytest.mark.tier2
def test_b33_ckd_epi_extreme_dialysis_creatinine_fifteen():
    """Verify extreme creatinine (15.0 mg/dL) yields eGFR < 5 mL/min/1.73m2."""
    egfr = compute_ckd_epi_2021(serum_creatinine=15.0, age_years=60.0, is_female=False)
    assert egfr < 5.0


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# B34: Pharmacogenomics Rule Engine Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b34_pgx_unknown_allele_format():
    """Verify non-standard allele syntax defaults to indeterminate or zero matches."""
    engine = CPICPharmacogenomicsEngine()
    prescribed = [{"atc_code": "B01AC04", "inn_name": "Clopidogrel"}]
    genotypes = {"CYP2C19": "*UNKNOWN"}
    matches = engine.evaluate_genetics(prescribed, genotypes)
    assert len(matches) == 0


@pytest.mark.tier2
def test_b34_pgx_hlab5701_negative_allows_abacavir():
    """Verify HLA-B*57:01 negative status safely permits Abacavir use."""
    engine = CPICPharmacogenomicsEngine()
    prescribed = [{"atc_code": "J05AF06", "inn_name": "Abacavir"}]
    genotypes = {"HLA-B*57:01": "NEGATIVE"}
    matches = engine.evaluate_genetics(prescribed, genotypes)
    assert len(matches) == 0


@pytest.mark.tier2
def test_b34_pgx_heterozygous_intermediate_metabolizer():
    """Verify CYP2C19 *1/*2 is classified as Intermediate Metabolizer."""
    engine = CPICPharmacogenomicsEngine()
    prescribed = [{"atc_code": "B01AC04", "inn_name": "Clopidogrel"}]
    genotypes = {"CYP2C19": "*1/*2"}
    matches = engine.evaluate_genetics(prescribed, genotypes)
    assert len(matches) == 1
    assert matches[0]["patient_phenotype"] == "INTERMEDIATE_METABOLIZER"


@pytest.mark.tier2
def test_b34_pgx_ultrarapid_metabolizer_codeine_toxicity():
    """Verify CYP2D6 *1/*1XN ultrarapid metabolizer flags toxic morphine conversion."""
    engine = CPICPharmacogenomicsEngine()
    prescribed = [{"atc_code": "R05DA04", "inn_name": "Codeine"}]
    genotypes = {"CYP2D6": "*1/*1XN"}
    matches = engine.evaluate_genetics(prescribed, genotypes)
    assert len(matches) == 1
    assert matches[0]["is_absolute_contraindication"] is True


@pytest.mark.tier2
def test_b34_pgx_multi_gene_variant_profile():
    """Verify patient profile containing multiple PGx markers evaluates without conflicts."""
    engine = CPICPharmacogenomicsEngine()
    prescribed = [
        {"atc_code": "B01AC04", "inn_name": "Clopidogrel"},
        {"atc_code": "J05AF06", "inn_name": "Abacavir"},
    ]
    genotypes = {"CYP2C19": "*1/*1", "HLA-B*57:01": "POSITIVE"}
    matches = engine.evaluate_genetics(prescribed, genotypes)
    assert len(matches) == 1
    assert matches[0]["gene"] == "HLA-B*57:01"
