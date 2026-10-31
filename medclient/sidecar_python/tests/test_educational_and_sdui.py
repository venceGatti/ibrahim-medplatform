"""Tests for Educational Engine (NLI, Stateful DAG, FSRS) and SDUI Serialization."""
from datetime import datetime, timezone, timedelta
import pytest

from src.implementations.nli_cross_encoder import NLICrossEncoderEvaluator
from src.implementations.stateful_dag import StatefulDAGScenarioEngine
from src.implementations.fsrs_scheduler import FSRSScheduler
from src.implementations.review_balancer import ReviewLoadBalancer
from src.implementations.sdui_emitter import SDUISerializer


def test_nli_cross_encoder_scoring():
    """Verify NLI scoring on entailed vs contradicted atomic concepts."""
    evaluator = NLICrossEncoderEvaluator()
    atomic_concepts = [
        {
            "id": "AC_01",
            "hypothesis": "La diagnosi principale è polmonite acquisita in comunità.",
            "weight": 0.50,
            "is_critical": True,
        },
        {
            "id": "AC_02",
            "hypothesis": "Il paziente riceve terapia antibiotica appropriata.",
            "weight": 0.50,
            "is_critical": False,
        },
    ]

    # Student answer entails both
    good_text = "Il paziente presenta polmonite acquisita in comunità (CAP). Si raccomanda terapia antibiotica mirata."
    res_good = evaluator.evaluate_response(good_text, atomic_concepts)
    assert res_good["final_score"] >= 0.70
    assert res_good["critical_contradiction_triggered"] is False

    # Student answer explicitly contradicts critical concept
    bad_text = "Il paziente non ha assolutamente polmonite. Nessuna terapia antibiotica."
    res_bad = evaluator.evaluate_response(bad_text, atomic_concepts)
    assert res_bad["final_score"] == 0.0
    assert res_bad["critical_contradiction_triggered"] is True


def test_stateful_dag_scenario_transitions():
    """Verify state transitions, vitals deltas, and terminal node resolution."""
    dag_payload = {
        "initial_node_id": "S0_ER",
        "optimal_time_min": 60.0,
        "critical_time_min": 120.0,
        "max_budget_eur": 500.0,
        "optimal_cost_eur": 150.0,
        "nodes": {
            "S0_ER": {
                "node_id": "S0_ER",
                "narrative_state": "Paziente in shock al Pronto Soccorso.",
                "is_terminal": False,
                "current_vitals": {
                    "map_mmHg": 55.0,
                    "hr_bpm": 125.0,
                    "rr_bpm": 26.0,
                    "spo2_percent": 91.0,
                    "gcs": 13,
                },
                "available_transitions": [
                    {
                        "action_id": "A1_FLUIDS",
                        "action_label": "Infusione cristalloidi 30ml/kg",
                        "destination_node_id": "S1_RESUSCITATED",
                        "time_cost_min": 30.0,
                        "financial_cost_eur": 45.0,
                        "risk_severity": 0.1,
                        "vitals_delta": {"map_mmHg": 15.0, "hr_bpm": -20.0},
                        "clinical_consequence": "Pressione arteriosa in netto miglioramento.",
                    }
                ],
            },
            "S1_RESUSCITATED": {
                "node_id": "S1_RESUSCITATED",
                "narrative_state": "Stabilizzazione emodinamica ottenuta.",
                "is_terminal": True,
                "terminal_grade": 1.0,
                "current_vitals": {
                    "map_mmHg": 70.0,
                    "hr_bpm": 105.0,
                    "rr_bpm": 22.0,
                    "spo2_percent": 95.0,
                    "gcs": 15,
                },
                "available_transitions": [],
            },
        },
    }

    engine = StatefulDAGScenarioEngine(dag_payload)
    init_node = engine.get_current_node()
    assert init_node.node_id == "S0_ER"

    step_res = engine.transition("S0_ER", "A1_FLUIDS", init_node.current_vitals.model_dump())
    assert step_res["next_node_id"] == "S1_RESUSCITATED"
    assert step_res["is_terminal"] is True
    assert step_res["terminal_grade"] == 1.0
    assert step_res["updated_vitals"]["map_mmHg"] == 70.0


def test_fsrs_spaced_repetition_scheduler():
    """Verify FSRS stability, difficulty, and review interval calculations."""
    scheduler = FSRSScheduler()
    now = datetime.now(timezone.utc)

    card = {
        "concept_uid": "card_001",
        "stability": 2.5,
        "difficulty": 5.0,
        "elapsed_days": 2.0,
        "scheduled_days": 2.0,
        "reps": 1,
        "lapses": 0,
        "state": 2,
        "last_review": now - timedelta(days=2),
        "due_date": now,
        "retrievability": 0.90,
        "criticality_weight": 1.5,
    }

    # Review with Good rating (G=3)
    res_good = scheduler.review_card(
        card_state=card,
        rating=3,
        review_time=now,
        desired_retention=0.90,
    )
    assert res_good["card_state"]["stability"] > 2.5
    assert res_good["interval_days"] >= 3
    assert res_good["relearning_priority"] is False

    # Review with Again rating (G=1, Lapse)
    res_lapse = scheduler.review_card(
        card_state=card,
        rating=1,
        review_time=now,
        desired_retention=0.90,
    )
    assert res_lapse["card_state"]["stability"] < 2.5
    assert res_lapse["relearning_priority"] is True
    assert res_lapse["card_state"]["lapses"] == 1


def test_review_load_balancer():
    """Verify daily batch capacity capping and backlog smoothing."""
    balancer = ReviewLoadBalancer()
    now = datetime.now(timezone.utc)

    cards = [
        {
            "concept_uid": f"c_{i}",
            "stability": 3.0 + i * 0.5,
            "difficulty": 5.0,
            "elapsed_days": 4.0,
            "scheduled_days": 3.0,
            "reps": 2,
            "lapses": 0,
            "due_date": now,
            "last_review": now - timedelta(days=4),
            "criticality_weight": 1.0,
        }
        for i in range(10)
    ]

    res = balancer.balance_daily_batch(cards=cards, current_date=now, daily_capacity=6)
    assert res["capacity_limit"] == 6
    assert res["batch_size"] == 6
    assert res["excess_count"] == 4
    assert len(res["postponed_cards"]) + len(res["advanced_cards"]) == 4


def test_sdui_serialization_emitter():
    """Verify serialization of all 4 polymorphic SDUI blocks into envelope."""
    emitter = SDUISerializer()

    b1 = emitter.build_clinical_sheet_block(
        sheet_id="sheet_101",
        title="STEMI Protocol",
        content_markdown="# STEMI\nPrimary PCI within 120min.",
        callouts=[{"title": "Red Flag", "severity": "RED_FLAG", "body_markdown": "Shock"}],
    )
    b2 = emitter.build_symptom_matcher_block(
        differential_candidates=[{"icd10": "I21.0", "name": "STEMI"}],
        selected_symptoms=[{"hpo": "HP:0100749", "state": "PRESENT"}],
    )
    b3 = emitter.build_drug_safety_block(
        interactions=[],
        cyp_clearance={"CYP3A4": 1.0},
        alerts=[],
        egfr=85.5,
    )
    b4 = emitter.build_exam_simulator_block(
        item_type="MCQ_4",
        item_data={"question": "Immediate action in STEMI?"},
    )

    envelope = emitter.serialize_envelope(
        session_id="session_test",
        sequence_number=1,
        blocks=[b1, b2, b3, b4],
    )
    assert envelope["session_id"] == "session_test"
    assert len(envelope["blocks"]) == 4
    assert envelope["blocks"][0]["block_type"] == "ClinicalSheetBlock"
    assert envelope["blocks"][1]["block_type"] == "SymptomMatcherBlock"
    assert envelope["blocks"][2]["block_type"] == "DrugSafetyBlock"
    assert envelope["blocks"][3]["block_type"] == "ExamSimulatorBlock"
