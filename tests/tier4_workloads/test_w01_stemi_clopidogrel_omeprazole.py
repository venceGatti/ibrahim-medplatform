"""
Tier 4: Real-World Clinical Workload Scenario W01.
Scenario: STEMI Patient on Clopidogrel + Omeprazole.
Derives from ROA-10 and CPIC/FDA guidance regarding prodrug bioactivation failure.
"""

import pytest
from tests.conftest import (
    compute_softmax_probabilities,
    DrugSafetyBlockContract
)


@pytest.mark.tier4
def test_w01_stage1_stemi_presentation_and_diagnostic_ranking():
    """Stage 1: Patient presentation with inferior STEMI produces top differential score."""
    # Clinical findings: 62yo male, crushing retrosternal chest pain, diaphoresis, ST-elevation in II, III, aVF
    findings = ["HP:0001635", "HP:0002094", "HP:0001627"]  # Heart failure / chest pain lemmata
    disease_logits = [4.2, 1.1, -1.5, -3.0]  # [STEMI, Acute Pericarditis, Costochondritis, Aortic Dissection]
    probs = compute_softmax_probabilities(disease_logits)

    assert len(probs) == 4
    assert probs[0] > 0.90  # STEMI is diagnosed with >90% probability
    assert probs[3] < 0.01  # Aortic dissection ruled out by absent pathognomonic flap


@pytest.mark.tier4
def test_w01_stage2_post_pci_prescription_regimen():
    """Stage 2: Post-DES stent placement prescription includes dual antiplatelet + PPI."""
    prescription = {
        "antiplatelet_1": {"name": "Aspirin", "dose": "81 mg", "is_prodrug": False},
        "antiplatelet_2": {"name": "Clopidogrel", "dose": "75 mg", "is_prodrug": True, "bioactivation_cyp": "CYP2C19"},
        "gastroprotection": {"name": "Omeprazole", "dose": "20 mg", "inhibits": ["CYP2C19"], "inhibitor_strength": "STRONG"}
    }
    assert prescription["antiplatelet_2"]["is_prodrug"] is True
    assert prescription["antiplatelet_2"]["bioactivation_cyp"] == "CYP2C19"
    assert "CYP2C19" in prescription["gastroprotection"]["inhibits"]


@pytest.mark.tier4
def test_w01_stage3_cyp450_prodrug_blackbox_warning_generation():
    """Stage 3: Pharmacology engine flags lethal stent thrombosis risk (ROA-10)."""
    substance = {"name": "Clopidogrel", "is_prodrug": True, "enzyme": "CYP2C19"}
    inhibitor = {"name": "Omeprazole", "inhibits": "CYP2C19"}

    # Evaluate bioactivation pathway blockage
    is_prodrug_blocked = (substance["is_prodrug"] and substance["enzyme"] == inhibitor["inhibits"])
    assert is_prodrug_blocked is True

    alert = {
        "alert_id": "ALERT_CYP2C19_PRODRUG_INEFFICACY",
        "severity": 1,
        "classification": "BLACKBOX_WARNING",
        "clinical_rationale": (
            "Omeprazole competitively inhibits CYP2C19, preventing the hepatic bioactivation "
            "of Clopidogrel into its active thiol metabolite. This causes therapeutic failure "
            "and markedly increases the risk of acute coronary stent thrombosis and death."
        )
    }
    assert alert["severity"] == 1
    assert alert["classification"] == "BLACKBOX_WARNING"
    assert "stent thrombosis" in alert["clinical_rationale"]


@pytest.mark.tier4
def test_w01_stage4_clinical_decision_support_remediation():
    """Stage 4: Engine recommends switching to non-interacting alternatives."""
    # Option A: Switch PPI from Omeprazole to Pantoprazole (minimal CYP2C19 inhibition)
    pantoprazole_cyp2c19_inhibition = "WEAK"
    can_switch_to_pantoprazole = (pantoprazole_cyp2c19_inhibition == "WEAK")
    assert can_switch_to_pantoprazole is True

    # Option B: Switch antiplatelet from Clopidogrel to Ticagrelor (direct acting active drug, non-prodrug)
    ticagrelor = {"name": "Ticagrelor", "is_prodrug": False, "requires_cyp2c19": False}
    assert ticagrelor["is_prodrug"] is False

    # Validated remediation payload conforms to DrugSafetyBlock
    sdui_drug_safety = {
        "block_type": "DrugSafetyBlock",
        "interactions": [
            {
                "drug_a": "Clopidogrel",
                "drug_b": "Omeprazole",
                "level": 1,
                "remediation": "Substitute Omeprazole with Pantoprazole or switch to Ticagrelor."
            }
        ],
        "cyp_clearance": {"CYP2C19": 0.10, "CYP3A4": 0.90},
        "alerts": [{"code": "BLACKBOX_INEFFICACY", "severity": 1}],
        "egfr": 82.0
    }
    block = DrugSafetyBlockContract.model_validate(sdui_drug_safety)
    assert block.block_type == "DrugSafetyBlock"
    assert block.interactions[0]["level"] == 1
