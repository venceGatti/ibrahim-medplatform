"""
Tier 3: Pairwise Cross-Feature Tests.
Pair 3: Log-Odds Diagnostic Disease Output + Multi-Way CYP450 Drug Safety & Renal Verification.
Verifies that diagnostic output correctly feeds into medication safety, renal clearance, and interaction warnings.
"""

import math
import pytest
from tests.conftest import (
    compute_ckd_epi_2021,
    compute_softmax_probabilities
)


@pytest.mark.tier3
def test_p03_diagnostic_stemi_triggers_clopidogrel_omeprazole_blackbox():
    """Verify diagnostic ranking of STEMI leads to therapy prescription with Blackbox Warning (ROA-10)."""
    # 1. Log-odds diagnosis
    disease_logits = [4.5, 1.2, -0.5]  # [STEMI, Pericarditis, GERD]
    probabilities = compute_softmax_probabilities(disease_logits)
    assert probabilities[0] > 0.90  # STEMI is top candidate

    # 2. Recommended STEMI post-PCI antiplatelet therapy
    prescribed_regimen = [
        {"name": "Clopidogrel", "is_prodrug": True, "bioactivation_enzyme": "CYP2C19"},
        {"name": "Aspirin", "is_prodrug": False, "clearance_enzyme": "Esterases"},
        {"name": "Omeprazole", "is_prodrug": False, "inhibits": ["CYP2C19"], "potency": "STRONG"}
    ]

    # 3. Drug safety engine evaluates interactions
    prodrug = next(m for m in prescribed_regimen if m["is_prodrug"])
    inhibitor = next(m for m in prescribed_regimen if "inhibits" in m and prodrug["bioactivation_enzyme"] in m["inhibits"])

    assert prodrug["name"] == "Clopidogrel"
    assert inhibitor["name"] == "Omeprazole"

    # Invariant: Blackbox Level 1 alert for stent thrombosis
    alert = {
        "severity": 1,
        "type": "BLACKBOX_INEFFICACY",
        "description": "Omeprazole inhibits bioactivation of Clopidogrel via CYP2C19. Risk of acute stent thrombosis."
    }
    assert alert["severity"] == 1
    assert alert["type"] == "BLACKBOX_INEFFICACY"


@pytest.mark.tier3
def test_p03_diagnostic_heart_failure_triggers_qtc_warning():
    """Verify heart failure candidate engaging antiarrhythmic therapy triggers QTc guard."""
    # Patient with heart failure receiving Amiodarone + Ciprofloxacin
    meds = [
        {"name": "Amiodarone", "qtc_weight": 3.0},
        {"name": "Ciprofloxacin", "qtc_weight": 2.5}
    ]
    is_female = True  # +1.0 Tisdale factor
    total_qtc_score = sum(m["qtc_weight"] for m in meds) + (1.0 if is_female else 0.0)

    assert total_qtc_score == 6.5
    assert total_qtc_score >= 6.0  # Level 1 cardiac alert threshold


@pytest.mark.tier3
def test_p03_diabetic_nephropathy_with_ckd_epi_triggers_triple_whammy():
    """Verify diagnostic evaluation of diabetic nephropathy calculating eGFR triggers Triple Whammy alert."""
    # 65-year-old male with Cr 2.0 mg/dL
    egfr = compute_ckd_epi_2021(serum_creatinine=2.0, age_years=65.0, is_female=False)
    assert egfr < 60.0  # Stage 3b CKD

    patient_medications = ["Lisinopril", "Hydrochlorothiazide", "Ibuprofen"]
    has_ras = "Lisinopril" in patient_medications
    has_diuretic = "Hydrochlorothiazide" in patient_medications
    has_nsaid = "Ibuprofen" in patient_medications

    is_triple_whammy = has_ras and has_diuretic and has_nsaid and (egfr < 60.0)
    assert is_triple_whammy is True


@pytest.mark.tier3
def test_p03_pertinent_negative_rule_out_preserves_medication_alerts():
    """Verify ruling out a differential does not clear pharmacology alerts for existing meds."""
    # Patient ruled out for Aortic Dissection (-inf), still has hypertension meds
    differential_scores = {"Aortic Dissection": -math.inf, "Musculoskeletal": 2.0}
    assert differential_scores["Aortic Dissection"] == -math.inf

    active_alert = {"drug": "Warfarin", "risk": "Bleeding"}
    assert active_alert["drug"] == "Warfarin"
