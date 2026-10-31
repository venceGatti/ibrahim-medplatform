"""
Tier 1: Feature Coverage Tests for MedClient Features 30 through 34.
- Feature 30: CYP450 Functional Load Engine
- Feature 31: QTc Prolongation Guard
- Feature 32: "Triple Whammy" Detector
- Feature 33: CKD-EPI 2021 Renal Calculator
- Feature 34: Pharmacogenomics Rule Engine
"""

import pytest
from medclient.sidecar_python.src.implementations.cyp450_engine import CYP450Engine
from medclient.sidecar_python.src.implementations.qtc_calculator import QTcCalculator
from medclient.sidecar_python.src.implementations.triple_whammy import TripleWhammyDetector
from medclient.sidecar_python.src.implementations.ckd_epi import CKDEPI2021Calculator
from medclient.sidecar_python.src.implementations.cpic_engine import CPICPharmacogenomicsEngine
from medclient.sidecar_python.src.base.pharmacology_models import SeverityLevel


# ---------------------------------------------------------------------------
# Feature 30: CYP450 Functional Load Engine
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f30_cyp450_prodrug_inhibition_causes_inefficacy_alert():
    """Verify inhibiting bioactivating enzyme of a prodrug raises Blackbox Level 1 alert (ROA-10)."""
    engine = CYP450Engine()
    prescribed = [
        {
            "atc_code": "B01AC04",
            "inn_name": "Clopidogrel",
            "is_prodrug": True,
            "fm_cyp": {"CYP2C19": 0.85, "CYP3A4": 0.15},
        },
        {
            "atc_code": "A02BC01",
            "inn_name": "Omeprazole",
            "is_prodrug": False,
            "cyp_profile": {
                "substrates": {},
                "inhibitors": {"CYP2C19": "STRONG"},
                "inducers": {},
            },
        },
    ]

    evaluation = engine.evaluate_clearance(prescribed)
    interactions = evaluation["interactions"]
    assert len(interactions) > 0
    level1_interactions = [i for i in interactions if i.severity == SeverityLevel.LEVEL_1]
    assert len(level1_interactions) >= 1
    target_alert = level1_interactions[0]
    assert target_alert.target_atc == "B01AC04"
    assert "blocking metabolic bioactivation of prodrug" in target_alert.mechanism


@pytest.mark.tier1
def test_f30_cyp450_active_substrate_inhibition_causes_toxicity_alert():
    """Verify inhibiting clearance enzyme of an active drug raises accumulation toxicity alert."""
    engine = CYP450Engine()
    prescribed = [
        {
            "atc_code": "C10AA01",
            "inn_name": "Simvastatin",
            "is_prodrug": False,
            "is_narrow_therapeutic_index": False,
            "fm_cyp": {"CYP3A4": 0.90},
        },
        {
            "atc_code": "J01FA09",
            "inn_name": "Clarithromycin",
            "is_prodrug": False,
            "cyp_profile": {
                "substrates": {},
                "inhibitors": {"CYP3A4": "STRONG"},
                "inducers": {},
            },
        },
    ]

    evaluation = engine.evaluate_clearance(prescribed)
    interactions = evaluation["interactions"]
    assert len(interactions) > 0
    assert evaluation["auc_ratios"]["C10AA01"] > 2.0


@pytest.mark.tier1
def test_f30_cyp450_inducer_accelerates_clearance():
    """Verify strong enzyme inducer reduces exposure of active drug substrate (AUC ratio < 1.0)."""
    engine = CYP450Engine()
    prescribed = [
        {
            "atc_code": "G03AA07",
            "inn_name": "Ethinylestradiol",
            "is_prodrug": False,
            "fm_cyp": {"CYP3A4": 0.80},
        },
        {
            "atc_code": "J04AB02",
            "inn_name": "Rifampicin",
            "is_prodrug": False,
            "cyp_profile": {
                "substrates": {},
                "inhibitors": {},
                "inducers": {"CYP3A4": "STRONG"},
            },
        },
    ]

    evaluation = engine.evaluate_clearance(prescribed)
    auc_ratio = evaluation["auc_ratios"]["G03AA07"]
    assert auc_ratio < 1.0
    assert evaluation["cyp_states"]["CYP3A4"].computed_clearance > 1.5


@pytest.mark.tier1
def test_f30_cyp450_multiway_competitive_load_sum():
    """Verify clearance load sums fractional clearance contributions across multiple substrates."""
    engine = CYP450Engine()
    prescribed = [
        {
            "atc_code": "N06AB04",
            "inn_name": "Citalopram",
            "fm_cyp": {"CYP2C19": 0.40, "CYP3A4": 0.30},
        },
        {
            "atc_code": "A02BC01",
            "inn_name": "Omeprazole",
            "cyp_profile": {"substrates": {}, "inhibitors": {"CYP2C19": "STRONG"}, "inducers": {}},
        },
    ]

    evaluation = engine.evaluate_clearance(prescribed)
    assert "CYP2C19" in evaluation["cyp_states"]
    assert evaluation["cyp_states"]["CYP2C19"].computed_clearance <= 0.25


@pytest.mark.tier1
def test_f30_cyp450_unrelated_isoenzymes_do_not_interact():
    """Verify substrate on CYP1A2 is unaffected by isolated CYP2E1 inhibitor."""
    engine = CYP450Engine()
    prescribed = [
        {
            "atc_code": "R03DA04",
            "inn_name": "Theophylline",
            "fm_cyp": {"CYP1A2": 0.90},
        },
        {
            "atc_code": "N07BB01",
            "inn_name": "Disulfiram",
            "cyp_profile": {"substrates": {}, "inhibitors": {"CYP2E1": "STRONG"}, "inducers": {}},
        },
    ]

    evaluation = engine.evaluate_clearance(prescribed)
    assert evaluation["auc_ratios"]["R03DA04"] == 1.0


# ---------------------------------------------------------------------------
# Feature 31: QTc Prolongation Guard
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f31_qtc_linear_score_summation():
    """Verify QTc risk scores accumulate from drug risk weights and AUC multipliers."""
    calc = QTcCalculator()
    prescribed = [
        {"atc_code": "C01BD01", "inn_name": "Amiodarone", "qtc_base_risk": 3.0},
        {"atc_code": "J01MA12", "inn_name": "Levofloxacin", "qtc_base_risk": 2.5},
        {"atc_code": "A04AA01", "inn_name": "Ondansetron", "qtc_base_risk": 1.5},
    ]
    auc_ratios = {"C01BD01": 1.0, "J01MA12": 1.0, "A04AA01": 1.0}
    result = calc.evaluate_qtc(prescribed, auc_ratios, serum_potassium_meq_l=4.2)
    assert result["qtc_prolongation_score"] == 7.0


@pytest.mark.tier1
def test_f31_qtc_threshold_six_triggers_level_one_alert():
    """Verify cumulative QTc risk score >= 6.0 triggers Level 1 cardiac alert."""
    calc = QTcCalculator()
    prescribed = [
        {"atc_code": "C01BD01", "inn_name": "Amiodarone", "qtc_base_risk": 3.5},
        {"atc_code": "J01MA12", "inn_name": "Levofloxacin", "qtc_base_risk": 3.0},
    ]
    result = calc.evaluate_qtc(prescribed, {}, serum_potassium_meq_l=4.5)
    assert result["qtc_prolongation_score"] >= 6.0
    assert result["torsades_de_pointes_risk"] == SeverityLevel.LEVEL_1


@pytest.mark.tier1
def test_f31_qtc_additive_moderate_prolongers():
    """Verify two moderate prolongers (3.0 each) combine to hit the 6.0 threshold."""
    calc = QTcCalculator()
    prescribed = [
        {"atc_code": "C01BD01", "inn_name": "Amiodarone", "qtc_base_risk": 3.0},
        {"atc_code": "J01MA02", "inn_name": "Ciprofloxacin", "qtc_base_risk": 3.0},
    ]
    result = calc.evaluate_qtc(prescribed, {}, serum_potassium_meq_l=4.0)
    assert result["qtc_prolongation_score"] == 6.0
    assert result["torsades_de_pointes_risk"] == SeverityLevel.LEVEL_1


@pytest.mark.tier1
def test_f31_qtc_hypokalemia_weight_factor():
    """Verify hypokalemia (<3.5 mEq/L) adds 1.5 risk penalty to cumulative QTc."""
    calc = QTcCalculator()
    prescribed = [
        {"atc_code": "C01BD01", "inn_name": "Amiodarone", "qtc_base_risk": 3.0},
    ]
    normal_k = calc.evaluate_qtc(prescribed, {}, serum_potassium_meq_l=4.2)
    low_k = calc.evaluate_qtc(prescribed, {}, serum_potassium_meq_l=3.1)
    assert low_k["qtc_prolongation_score"] == normal_k["qtc_prolongation_score"] + 1.5


@pytest.mark.tier1
def test_f31_qtc_sub_threshold_score_generates_advisory():
    """Verify scores below 4.0 generate Level 3 moderate alert rather than Level 1."""
    calc = QTcCalculator()
    prescribed = [
        {"atc_code": "N06AB04", "inn_name": "Citalopram", "qtc_base_risk": 2.0},
    ]
    result = calc.evaluate_qtc(prescribed, {}, serum_potassium_meq_l=4.2)
    assert result["qtc_prolongation_score"] == 2.0
    assert result["torsades_de_pointes_risk"] == SeverityLevel.LEVEL_3


# ---------------------------------------------------------------------------
# Feature 32: "Triple Whammy" Detector
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f32_triple_whammy_full_combination_detection():
    """Verify ACEi + Diuretic + NSAID with eGFR < 60 triggers Triple Whammy Level 1 alert."""
    detector = TripleWhammyDetector()
    prescribed = [
        {"atc_code": "C09AA03", "inn_name": "Lisinopril"},
        {"atc_code": "C03AA03", "inn_name": "Hydrochlorothiazide"},
        {"atc_code": "M01AE01", "inn_name": "Ibuprofen"},
    ]
    result = detector.detect_triple_whammy(prescribed, egfr=45.0)
    assert result["has_triple_whammy"] is True
    assert result["severity"] == SeverityLevel.LEVEL_1


@pytest.mark.tier1
def test_f32_triple_whammy_absent_nsaid_no_trigger():
    """Verify ACEi + Diuretic without NSAID does not trigger Triple Whammy."""
    detector = TripleWhammyDetector()
    prescribed = [
        {"atc_code": "C09AA03", "inn_name": "Lisinopril"},
        {"atc_code": "C03AA03", "inn_name": "Hydrochlorothiazide"},
    ]
    result = detector.detect_triple_whammy(prescribed, egfr=45.0)
    assert result["has_triple_whammy"] is False


@pytest.mark.tier1
def test_f32_triple_whammy_normal_egfr_warning_only():
    """Verify presence of Triple Whammy drugs with normal eGFR (>=60) gives Level 2 caution."""
    detector = TripleWhammyDetector()
    prescribed = [
        {"atc_code": "C09AA03", "inn_name": "Lisinopril"},
        {"atc_code": "C03AA03", "inn_name": "Hydrochlorothiazide"},
        {"atc_code": "M01AE01", "inn_name": "Ibuprofen"},
    ]
    result = detector.detect_triple_whammy(prescribed, egfr=95.0)
    assert result["has_triple_whammy"] is True
    assert result["severity"] == SeverityLevel.LEVEL_2


@pytest.mark.tier1
def test_f32_triple_whammy_arb_equivalent_to_acei():
    """Verify Angiotensin Receptor Blockers (ARBs like Losartan C09CA01) satisfy RAS blocker criteria."""
    detector = TripleWhammyDetector()
    prescribed = [
        {"atc_code": "C09CA01", "inn_name": "Losartan"},
        {"atc_code": "C03CA01", "inn_name": "Furosemide"},
        {"atc_code": "M01AE02", "inn_name": "Naproxen"},
    ]
    result = detector.detect_triple_whammy(prescribed, egfr=38.0)
    assert result["has_triple_whammy"] is True
    assert result["severity"] == SeverityLevel.LEVEL_1


@pytest.mark.tier1
def test_f32_triple_whammy_selective_cox2_trigger():
    """Verify selective COX-2 inhibitors (Celecoxib M01AH01) also trigger hemodynamic AKI risk."""
    detector = TripleWhammyDetector()
    prescribed = [
        {"atc_code": "C09AA02", "inn_name": "Enalapril"},
        {"atc_code": "C03AA03", "inn_name": "Hydrochlorothiazide"},
        {"atc_code": "M01AH01", "inn_name": "Celecoxib"},
    ]
    result = detector.detect_triple_whammy(prescribed, egfr=50.0)
    assert result["has_triple_whammy"] is True
    assert result["severity"] == SeverityLevel.LEVEL_1


# ---------------------------------------------------------------------------
# Feature 33: CKD-EPI 2021 Renal Calculator
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f33_ckd_epi_female_baseline_calculation():
    """Verify CKD-EPI 2021 for standard female patient: Cr 0.9 mg/dL, Age 60."""
    calc = CKDEPI2021Calculator()
    egfr = calc.compute_egfr(age=60, is_female=True, serum_creatinine_mg_dl=0.9)
    assert 70.0 <= egfr <= 78.0


@pytest.mark.tier1
def test_f33_ckd_epi_male_baseline_calculation():
    """Verify CKD-EPI 2021 for standard male patient: Cr 1.1 mg/dL, Age 60."""
    calc = CKDEPI2021Calculator()
    egfr = calc.compute_egfr(age=60, is_female=False, serum_creatinine_mg_dl=1.1)
    assert 70.0 <= egfr <= 78.0


@pytest.mark.tier1
def test_f33_ckd_epi_race_free_invariant():
    """Verify formula contains zero race coefficients (ROA-03 / ROA-10)."""
    calc = CKDEPI2021Calculator()
    egfr_run1 = calc.compute_egfr(age=65, is_female=False, serum_creatinine_mg_dl=1.4)
    egfr_run2 = calc.compute_egfr(age=65, is_female=False, serum_creatinine_mg_dl=1.4)
    assert egfr_run1 == egfr_run2
    assert egfr_run1 < 60.0


@pytest.mark.tier1
def test_f33_ckd_epi_creatinine_inverse_relationship():
    """Verify rising serum creatinine strictly decreases eGFR."""
    calc = CKDEPI2021Calculator()
    egfr_low_cr = calc.compute_egfr(age=50, is_female=False, serum_creatinine_mg_dl=0.8)
    egfr_high_cr = calc.compute_egfr(age=50, is_female=False, serum_creatinine_mg_dl=2.5)
    assert egfr_low_cr > egfr_high_cr


@pytest.mark.tier1
def test_f33_ckd_epi_age_inverse_relationship():
    """Verify advancing age strictly decreases eGFR for constant creatinine."""
    calc = CKDEPI2021Calculator()
    egfr_young = calc.compute_egfr(age=25, is_female=False, serum_creatinine_mg_dl=1.0)
    egfr_elderly = calc.compute_egfr(age=85, is_female=False, serum_creatinine_mg_dl=1.0)
    assert egfr_young > egfr_elderly


# ---------------------------------------------------------------------------
# Feature 34: Pharmacogenomics Rule Engine
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f34_pgx_hlab5701_abacavir_contraindication():
    """Verify HLA-B*57:01 positive status triggers absolute Abacavir contraindication."""
    engine = CPICPharmacogenomicsEngine()
    prescribed = [{"atc_code": "J05AF06", "inn_name": "Abacavir"}]
    genotypes = {"HLA-B*57:01": "POSITIVE"}
    matches = engine.evaluate_genetics(prescribed, genotypes)
    assert len(matches) == 1
    assert matches[0]["is_absolute_contraindication"] is True
    assert "ABSOLUTE CONTRAINDICATION" in matches[0]["recommendation"]


@pytest.mark.tier1
def test_f34_pgx_cyp2c19_poor_metabolizer_clopidogrel():
    """Verify CYP2C19 *2/*2 poor metabolizer recommends alternative antiplatelet."""
    engine = CPICPharmacogenomicsEngine()
    prescribed = [{"atc_code": "B01AC04", "inn_name": "Clopidogrel"}]
    genotypes = {"CYP2C19": "*2/*2"}
    matches = engine.evaluate_genetics(prescribed, genotypes)
    assert len(matches) == 1
    assert matches[0]["patient_phenotype"] == "POOR_METABOLIZER"
    assert "Prasugrel or Ticagrelor" in matches[0]["recommendation"]


@pytest.mark.tier1
def test_f34_pgx_tpmt_azathioprine_myelosuppression():
    """Verify TPMT intermediate/poor metabolizer mandates Azathioprine dose reduction."""
    engine = CPICPharmacogenomicsEngine()
    prescribed = [{"atc_code": "L01BB02", "inn_name": "Azathioprine"}]
    genotypes = {"TPMT": "*3A/*3A"}
    matches = engine.evaluate_genetics(prescribed, genotypes)
    assert len(matches) == 1
    assert "MYELOSUPPRESSION" in matches[0]["recommendation"]


@pytest.mark.tier1
def test_f34_pgx_codeine_ultra_rapid_metabolizer_toxicity():
    """Verify CYP2D6 ultra-rapid metabolizer generates respiratory depression contraindication."""
    engine = CPICPharmacogenomicsEngine()
    prescribed = [{"atc_code": "R05DA04", "inn_name": "Codeine"}]
    genotypes = {"CYP2D6": "*1/*1XN"}
    matches = engine.evaluate_genetics(prescribed, genotypes)
    assert len(matches) == 1
    assert matches[0]["is_absolute_contraindication"] is True
    assert "RESPIRATORY DEPRESSION" in matches[0]["recommendation"]


@pytest.mark.tier1
def test_f34_pgx_cyp2d6_poor_metabolizer_tamoxifen():
    """Verify CYP2D6 poor metabolizer alerts for reduced endoxifen conversion."""
    engine = CPICPharmacogenomicsEngine()
    prescribed = [{"atc_code": "L02BA01", "inn_name": "Tamoxifen"}]
    genotypes = {"CYP2D6": "*4/*4"}
    matches = engine.evaluate_genetics(prescribed, genotypes)
    assert len(matches) == 1
    assert "REDUCED EFFICACY" in matches[0]["recommendation"]
