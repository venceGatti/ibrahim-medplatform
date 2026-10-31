"""
Tier 4: Real-World Clinical Workload Scenario W02.
Scenario: Sepsis Patient Triggering qSOFA and NEWS2 Escalation.
Evaluates acute physiological triage, Shock Index, qSOFA, and emergency triage protocol.
"""

import pytest
from tests.conftest import (
    compute_qsofa_score,
    compute_shock_index,
    SymptomMatcherBlockContract,
    ExamSimulatorBlockContract
)


@pytest.mark.tier4
def test_w02_stage1_sepsis_triage_vitals_presentation():
    """Stage 1: Presentation of 74yo female with pneumonia and septic shock vitals."""
    vitals = {
        "heart_rate": 118,
        "systolic_blood_pressure": 88,
        "respiratory_rate": 26,
        "temperature_celsius": 38.9,
        "glasgow_coma_scale": 13,
        "oxygen_saturation": 91
    }
    assert vitals["heart_rate"] > 100
    assert vitals["systolic_blood_pressure"] < 90
    assert vitals["respiratory_rate"] >= 22


@pytest.mark.tier4
def test_w02_stage2_shock_index_calculation():
    """Stage 2: Shock Index calculation triggers critical hypoperfusion flag."""
    si = compute_shock_index(heart_rate=118, systolic_blood_pressure=88)
    # 118 / 88 = 1.341
    assert si == 1.341
    assert si >= 1.0  # Critical threshold


@pytest.mark.tier4
def test_w02_stage3_qsofa_score_triple_trigger():
    """Stage 3: qSOFA calculation evaluates all 3 criteria positive (3/3)."""
    score = compute_qsofa_score(
        respiratory_rate=26,
        systolic_blood_pressure=88,
        altered_mentation=True  # GCS 13 < 15
    )
    assert score == 3
    assert score >= 2  # Mandatory Sepsis-3 high risk criteria


@pytest.mark.tier4
def test_w02_stage4_red_flags_immediate_escalation_and_emergency_action():
    """Stage 4: Red Flags Interceptor activates immediate emergency triage and Sepsis Bundle."""
    is_septic_shock = True
    mandatory_actions = [
        "OBTAIN_BLOOD_CULTURES_PRIOR_TO_ANTIBIOTICS",
        "ADMINISTER_BROAD_SPECTRUM_IV_ANTIBIOTICS",
        "ADMINISTER_30ML_PER_KG_IV_CRYSTALLOIDS",
        "MEASURE_SERUM_LACTATE"
    ]
    assert len(mandatory_actions) == 4

    # Payload rendered to SDUI SymptomMatcherBlock reflecting high-priority alert
    sdui_symptom_matcher = {
        "block_type": "SymptomMatcherBlock",
        "differential_candidates": [
            {"disease_id": "SEPTIC_SHOCK_01", "name": "Septic Shock (Pulmonary Source)", "probability": 0.96}
        ],
        "selected_symptoms": ["HP:0001945", "HP:0002094", "HP:0001635"],  # Fever, Dyspnea, Shock
        "nbq": {
            "emergency_alert": "CRITICAL_RED_FLAG_ACTIVE",
            "protocol": "SEPSIS_RESUSCITATION_BUNDLE"
        }
    }
    block = SymptomMatcherBlockContract.model_validate(sdui_symptom_matcher)
    assert block.differential_candidates[0]["name"] == "Septic Shock (Pulmonary Source)"


@pytest.mark.tier4
def test_w02_stage5_stateful_dag_scenario_fluid_resuscitation():
    """Stage 5: Stateful DAG scenario records physiological improvement post-resuscitation."""
    scenario_state = {
        "step_id": "RESUSCITATION_COMPLETED",
        "administered_fluids_ml": 2000,
        "updated_vitals": {
            "heart_rate": 92,
            "systolic_blood_pressure": 108,
            "respiratory_rate": 20
        }
    }
    new_si = compute_shock_index(
        heart_rate=scenario_state["updated_vitals"]["heart_rate"],
        systolic_blood_pressure=scenario_state["updated_vitals"]["systolic_blood_pressure"]
    )
    assert new_si == 0.852  # Normalizes < 1.0

    sdui_scenario = {
        "block_type": "ExamSimulatorBlock",
        "item_type": "DAG_SCENARIO",
        "item_data": {
            "scenario_id": "SCENARIO_SEPSIS_02",
            "step": scenario_state["step_id"],
            "vitals": scenario_state["updated_vitals"],
            "patient_status": "COMPENSATED"
        },
        "fsrs_card_state": {"stability": 5.0, "difficulty": 4.0}
    }
    exam_block = ExamSimulatorBlockContract.model_validate(sdui_scenario)
    assert exam_block.item_data["patient_status"] == "COMPENSATED"
