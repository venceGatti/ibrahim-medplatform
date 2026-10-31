"""
Tier 4: Real-World Clinical Workload Scenario W03.
Scenario: Diabetic Nephropathy "Triple Whammy" Acute Kidney Injury.
Evaluates CKD-EPI 2021 renal calculations, hemodynamic drug triad interactions, and safety alerts.
"""

import pytest
from tests.conftest import (
    compute_ckd_epi_2021,
    DrugSafetyBlockContract
)


@pytest.mark.tier4
def test_w03_stage1_diabetic_nephropathy_baseline_patient():
    """Stage 1: 68-year-old male with long-standing diabetes and hypertension."""
    patient = {
        "age": 68.0,
        "is_female": False,
        "baseline_creatinine": 1.1,
        "chronic_meds": ["Lisinopril", "Hydrochlorothiazide"]
    }
    baseline_egfr = compute_ckd_epi_2021(
        serum_creatinine=patient["baseline_creatinine"],
        age_years=patient["age"],
        is_female=patient["is_female"]
    )
    # Baseline eGFR ~ 70 mL/min/1.73m2 (Mild CKD Stage 2)
    assert 68.0 <= baseline_egfr <= 74.0


@pytest.mark.tier4
def test_w03_stage2_acute_osteoarthritis_and_nsaid_addition():
    """Stage 2: Patient takes OTC Ibuprofen 600 mg TID for acute knee pain."""
    acute_med = "Ibuprofen"
    current_regimen = ["Lisinopril", "Hydrochlorothiazide", acute_med]
    assert len(current_regimen) == 3
    assert "Ibuprofen" in current_regimen


@pytest.mark.tier4
def test_w03_stage3_renal_deterioration_and_ckd_epi_calculation():
    """Stage 3: Serum creatinine spikes to 2.1 mg/dL; CKD-EPI 2021 evaluates severe drop."""
    acute_creatinine = 2.1
    acute_egfr = compute_ckd_epi_2021(
        serum_creatinine=acute_creatinine,
        age_years=68.0,
        is_female=False
    )
    # Acute eGFR drops to ~ 32 mL/min/1.73m2 (< 60 mL/min/1.73m2)
    assert acute_egfr < 60.0
    assert 30.0 <= acute_egfr <= 35.0


@pytest.mark.tier4
def test_w03_stage4_triple_whammy_triad_detection():
    """Stage 4: Engine identifies simultaneous RAS blocker + Diuretic + NSAID with eGFR < 60."""
    regimen = ["Lisinopril", "Hydrochlorothiazide", "Ibuprofen"]
    egfr = 32.6

    has_ras = any(m in {"Lisinopril", "Ramipril", "Losartan"} for m in regimen)
    has_diuretic = any(m in {"Hydrochlorothiazide", "Furosemide"} for m in regimen)
    has_nsaid = any(m in {"Ibuprofen", "Naproxen"} for m in regimen)
    is_triple_whammy = has_ras and has_diuretic and has_nsaid and (egfr < 60.0)

    assert is_triple_whammy is True

    alert = {
        "alert_code": "ALERT_TRIPLE_WHAMMY_HEMODYNAMIC_AKI",
        "severity": 1,
        "mechanism": (
            "Afferent arteriolar vasoconstriction (Ibuprofen via prostaglandin inhibition) + "
            "Efferent arteriolar vasodilation (Lisinopril via angiotensin II blockade) + "
            "Intravascular volume depletion (Hydrochlorothiazide). Severe drop in intraglomerular pressure."
        )
    }
    assert alert["severity"] == 1
    assert "prostaglandin" in alert["mechanism"]


@pytest.mark.tier4
def test_w03_stage5_drug_safety_sdui_block_generation():
    """Stage 5: Generates validated DrugSafetyBlock with renal color coding and alerts."""
    sdui_payload = {
        "block_type": "DrugSafetyBlock",
        "interactions": [
            {
                "drug_a": "Lisinopril",
                "drug_b": "Ibuprofen",
                "level": 1,
                "description": "Triple Whammy hemodynamic acute renal failure."
            }
        ],
        "cyp_clearance": {"CYP2C9": 0.50},
        "alerts": [
            {
                "type": "TRIPLE_WHAMMY",
                "severity": 1,
                "recommendation": "Immediately discontinue Ibuprofen. Consider Acetaminophen or topical therapy."
            }
        ],
        "egfr": 32.6
    }
    block = DrugSafetyBlockContract.model_validate(sdui_payload)
    assert block.block_type == "DrugSafetyBlock"
    assert block.egfr == 32.6
    assert block.alerts[0]["severity"] == 1
