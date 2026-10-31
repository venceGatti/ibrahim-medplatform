"""Tests for Pharmacology Engine (CYP450, QTc, Triple Whammy, CKD-EPI, CPIC)."""
import pytest

from src.implementations.cyp450_engine import CYP450Engine
from src.implementations.qtc_calculator import QTcCalculator
from src.implementations.triple_whammy import TripleWhammyDetector
from src.implementations.ckd_epi import CKDEPI2021Calculator
from src.implementations.cpic_engine import CPICPharmacogenomicsEngine
from src.base.pharmacology_models import SeverityLevel


def test_roa10_cyp450_prodrug_blackbox_warning():
    """Verify ROA-10: Clopidogrel (prodrug) + Omeprazole (CYP2C19 inhibitor) triggers Blackbox Level 1."""
    engine = CYP450Engine()
    prescribed = [
        {
            "atc_code": "B01AC04",
            "inn_name": "Clopidogrel",
            "is_prodrug": True,
            "single_dose_mg": 75.0,
            "daily_dose_mg": 75.0,
        },
        {
            "atc_code": "A02BC01",
            "inn_name": "Omeprazole",
            "is_prodrug": False,
            "single_dose_mg": 20.0,
            "daily_dose_mg": 20.0,
        },
    ]

    res = engine.evaluate_clearance(prescribed)
    interactions = res["detected_interactions"]
    assert len(interactions) > 0

    # Must contain Level 1 warning for bioactivation block
    stent_warning = any(
        i["severity"] == SeverityLevel.LEVEL_1 and "B01AC04" in i["target_atc"]
        for i in interactions
    )
    assert stent_warning is True


def test_qtc_prolongation_score():
    """Verify cumulative QTc >= 6.0 triggers Level 1 arrhythmia alert."""
    calculator = QTcCalculator()
    # Amiodarone (3.0) + Ciprofloxacin (3.0) + Hypokalemia (1.5) = 7.5 >= 6.0
    prescribed = [
        {"atc_code": "C01BD01", "qtc_base_risk": 3.0},
        {"atc_code": "J01MA02", "qtc_base_risk": 3.0},
    ]
    res = calculator.evaluate_qtc(
        prescribed_drugs=prescribed,
        auc_ratios={"C01BD01": 1.0, "J01MA02": 1.0},
        serum_potassium_meq_l=3.2,  # Hypokalemia
    )
    assert res["qtc_prolongation_score"] >= 6.0
    assert res["torsades_de_pointes_risk"] == SeverityLevel.LEVEL_1


def test_triple_whammy_aki_detector():
    """Verify RAS blocker + Diuretic + NSAID when eGFR < 60 triggers Level 1."""
    detector = TripleWhammyDetector()
    prescribed = [
        {"atc_code": "C09AA02", "is_ras_blocker": True},  # Lisinopril
        {"atc_code": "C03AA03", "is_diuretic": True},     # Hydrochlorothiazide
        {"atc_code": "M01AE01", "is_nsaid": True},        # Ibuprofen
    ]
    res = detector.detect_triple_whammy(prescribed, egfr=45.0)
    assert res["triple_whammy_detected"] is True
    assert res["severity_level"] == SeverityLevel.LEVEL_1
    assert "CRITICAL" in res["clinical_warning"]


def test_ckd_epi_2021_renal_calculator():
    """Verify race-free CKD-EPI 2021 formula calculations."""
    calc = CKDEPI2021Calculator()

    # 60 yo male, creatinine 1.0 mg/dL
    egfr_male = calc.compute_egfr(age=60, is_female=False, serum_creatinine_mg_dl=1.0)
    assert 80.0 <= egfr_male <= 95.0

    # 60 yo female, creatinine 1.0 mg/dL
    egfr_female = calc.compute_egfr(age=60, is_female=True, serum_creatinine_mg_dl=1.0)
    assert 60.0 <= egfr_female <= 75.0


def test_cpic_level_1a_pharmacogenomics():
    """Verify CPIC Level 1A guidelines for HLA-B*57:01, CYP2C19, and TPMT."""
    engine = CPICPharmacogenomicsEngine()

    # 1. HLA-B*57:01 + Abacavir -> Absolute contraindication
    res_abacavir = engine.evaluate_genetics(
        prescribed_drugs=[{"atc_code": "J05AF06", "inn_name": "Abacavir"}],
        patient_genotypes={"HLA-B*57:01": "POSITIVE"},
    )
    assert len(res_abacavir) == 1
    assert res_abacavir[0]["is_absolute_contraindication"] is True

    # 2. CYP2C19 PM + Clopidogrel -> Absolute contraindication (Inefficacy)
    res_clopidogrel = engine.evaluate_genetics(
        prescribed_drugs=[{"atc_code": "B01AC04", "inn_name": "Clopidogrel"}],
        patient_genotypes={"CYP2C19": "*2/*2 (POOR_METABOLIZER)"},
    )
    assert len(res_clopidogrel) == 1
    assert res_clopidogrel[0]["is_absolute_contraindication"] is True
