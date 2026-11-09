"""
Tier 1: Feature Coverage Tests for Educational Features 38 through 40.
- Feature 38: Stateful DAG Scenario Engine
- Feature 39: FSRS v4/v5 Mnemonic Scheduler
- Feature 40: Review Load Balancer
"""

import math
from datetime import datetime, timezone, timedelta
import pytest
from medclient.sidecar_python.src.implementations.stateful_dag import StatefulDAGScenarioEngine
from medclient.sidecar_python.src.implementations.fsrs_scheduler import FSRSScheduler
from medclient.sidecar_python.src.implementations.review_balancer import ReviewLoadBalancer
from medclient.sidecar_python.src.base.educational_models import (
    PatientVitals,
    DAGTransition,
    DAGNode,
    StatefulDAGDefinition,
    FSRSCardBase,
    FSRSReviewGrade,
    FSRSStateEnum,
)
from medclient.sidecar_python.src.base.exceptions import InvalidDAGTransitionError

# Feature 38: Stateful DAG Scenario Engine
# ---------------------------------------------------------------------------
@pytest.fixture
def scenario_dag_payload():
    return {
        "initial_node_id": "NODE_INIT",
        "optimal_time_min": 15.0,
        "critical_time_min": 45.0,
        "max_budget_eur": 500.0,
        "optimal_cost_eur": 120.0,
        "nodes": {
            "NODE_INIT": {
                "node_id": "NODE_INIT",
                "narrative_state": "Patient presents with diaphoresis and hypotension.",
                "is_terminal": False,
                "current_vitals": {
                    "map_mmHg": 55.0,
                    "hr_bpm": 125.0,
                    "rr_bpm": 24.0,
                    "spo2_percent": 90.0,
                    "gcs": 14,
                },
                "available_transitions": [
                    {
                        "action_id": "ACTION_IV_FLUIDS",
                        "action_label": "Administer 1000mL IV Saline",
                        "destination_node_id": "NODE_STABILIZED",
                        "time_cost_min": 10.0,
                        "financial_cost_eur": 25.0,
                        "risk_severity": 0.05,
                        "vitals_delta": {"map_mmHg": 20.0, "hr_bpm": -30.0},
                        "clinical_consequence": "Blood pressure normalizes and tachycardia resolves.",
                    },
                    {
                        "action_id": "ACTION_INCORRECT",
                        "action_label": "Administer High-Dose Beta Blocker",
                        "destination_node_id": "NODE_COLLAPSE",
                        "time_cost_min": 5.0,
                        "financial_cost_eur": 15.0,
                        "risk_severity": 0.95,
                        "vitals_delta": {"map_mmHg": -25.0, "hr_bpm": -50.0},
                        "clinical_consequence": "Acute hemodynamic collapse into cardiogenic shock.",
                    },
                ],
            },
            "NODE_STABILIZED": {
                "node_id": "NODE_STABILIZED",
                "narrative_state": "Patient stabilized successfully.",
                "is_terminal": True,
                "terminal_grade": 1.0,
                "current_vitals": {
                    "map_mmHg": 75.0,
                    "hr_bpm": 95.0,
                    "rr_bpm": 18.0,
                    "spo2_percent": 96.0,
                    "gcs": 15,
                },
                "available_transitions": [],
            },
            "NODE_COLLAPSE": {
                "node_id": "NODE_COLLAPSE",
                "narrative_state": "Patient collapsed.",
                "is_terminal": True,
                "terminal_grade": 0.0,
                "current_vitals": {
                    "map_mmHg": 30.0,
                    "hr_bpm": 40.0,
                    "rr_bpm": 8.0,
                    "spo2_percent": 75.0,
                    "gcs": 6,
                },
                "available_transitions": [],
            },
        },
    }


@pytest.mark.tier1
def test_f38_dag_initial_state_vitals(scenario_dag_payload):
    """Verify initial scenario state contains baseline vital signs."""
    engine = StatefulDAGScenarioEngine(scenario_dag_payload)
    current_node = engine.get_current_node()
    assert current_node.node_id == "NODE_INIT"
    assert current_node.current_vitals.map_mmHg == 55.0
    assert current_node.current_vitals.hr_bpm == 125.0


@pytest.mark.tier1
def test_f38_dag_action_transition(scenario_dag_payload):
    """Verify therapeutic action triggers transition to improved physiological state."""
    engine = StatefulDAGScenarioEngine(scenario_dag_payload)
    current_vitals = {"map_mmHg": 55.0, "hr_bpm": 125.0, "rr_bpm": 24.0, "spo2_percent": 90.0, "gcs": 14}
    res = engine.transition("NODE_INIT", "ACTION_IV_FLUIDS", current_vitals)
    assert res["next_node_id"] == "NODE_STABILIZED"
    assert res["updated_vitals"]["map_mmHg"] == 75.0
    assert res["updated_vitals"]["hr_bpm"] == 95.0
    assert res["is_terminal"] is True


@pytest.mark.tier1
def test_f38_dag_terminal_scoring(scenario_dag_payload):
    """Verify terminal node completes scenario with grade and cost metrics."""
    engine = StatefulDAGScenarioEngine(scenario_dag_payload)
    current_vitals = {"map_mmHg": 55.0, "hr_bpm": 125.0, "rr_bpm": 24.0, "spo2_percent": 90.0, "gcs": 14}
    res = engine.transition("NODE_INIT", "ACTION_IV_FLUIDS", current_vitals)
    assert res["final_score"] == 1.0
    assert res["elapsed_time_min"] == 10.0
    assert res["total_cost_eur"] == 25.0


@pytest.mark.tier1
def test_f38_dag_invalid_action_raises(scenario_dag_payload):
    """Verify attempting invalid action raises InvalidDAGTransitionError."""
    engine = StatefulDAGScenarioEngine(scenario_dag_payload)
    current_vitals = {"map_mmHg": 55.0, "hr_bpm": 125.0, "rr_bpm": 24.0, "spo2_percent": 90.0, "gcs": 14}
    with pytest.raises(InvalidDAGTransitionError):
        engine.transition("NODE_INIT", "ACTION_NONEXISTENT", current_vitals)


@pytest.mark.tier1
def test_f38_dag_lethal_transition(scenario_dag_payload):
    """Verify dangerous action causes collapse node transition with zero terminal grade."""
    engine = StatefulDAGScenarioEngine(scenario_dag_payload)
    current_vitals = {"map_mmHg": 55.0, "hr_bpm": 125.0, "rr_bpm": 24.0, "spo2_percent": 90.0, "gcs": 14}
    res = engine.transition("NODE_INIT", "ACTION_INCORRECT", current_vitals)
    assert res["next_node_id"] == "NODE_COLLAPSE"
    assert res["final_score"] == 0.0
    assert res["is_terminal"] is True


# ---------------------------------------------------------------------------
# Feature 39: FSRS v4/v5 Mnemonic Scheduler
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f39_fsrs_retrievability_decay():
    """Verify memory retrievability decays over time according to power law."""
    scheduler = FSRSScheduler()
    r_day_1 = scheduler.calculate_retrievability(elapsed_days=1.0, stability=5.0)
    r_day_10 = scheduler.calculate_retrievability(elapsed_days=10.0, stability=5.0)
    assert r_day_1 > r_day_10
    assert r_day_10 > 0.0


@pytest.mark.tier1
def test_f39_fsrs_stability_increase_on_success():
    """Verify successful recall increases card stability S."""
    scheduler = FSRSScheduler()
    card_dict = {
        "card_id": "CARD_001",
        "stability": 3.0,
        "difficulty": 5.0,
        "state": FSRSStateEnum.REVIEW,
        "reps": 2,
        "lapses": 0,
        "last_review": datetime.now(timezone.utc) - timedelta(days=3),
    }
    output = scheduler.review_card(card_dict, rating=int(FSRSReviewGrade.GOOD))
    assert output.stability > card_dict["stability"]
    assert output.interval_days >= 3.0


@pytest.mark.tier1
def test_f39_fsrs_lapse_resets_interval():
    """Verify rating 1 (Again) sets card to lapse state and resets interval."""
    scheduler = FSRSScheduler()
    card_dict = {
        "card_id": "CARD_002",
        "stability": 10.0,
        "difficulty": 4.0,
        "state": FSRSStateEnum.REVIEW,
        "reps": 5,
        "lapses": 0,
        "last_review": datetime.now(timezone.utc) - timedelta(days=10),
    }
    output = scheduler.review_card(card_dict, rating=int(FSRSReviewGrade.AGAIN))
    assert output.state == FSRSStateEnum.RELEARNING
    assert output.interval_days <= 3.0


@pytest.mark.tier1
def test_f39_fsrs_interval_calculation_target_retention():
    """Verify calculate_interval targets configured retention rate."""
    scheduler = FSRSScheduler()
    interval_90 = scheduler.calculate_interval(stability=10.0, target_retention=0.90)
    interval_80 = scheduler.calculate_interval(stability=10.0, target_retention=0.80)
    assert interval_80 > interval_90 > 0.0


@pytest.mark.tier1
def test_f39_fsrs_difficulty_bounds():
    """Verify item difficulty D is clamped within [1.0, 10.0]."""
    scheduler = FSRSScheduler()
    card_dict = {
        "card_id": "CARD_003",
        "stability": 2.0,
        "difficulty": 9.8,
        "state": FSRSStateEnum.LEARNING,
        "reps": 1,
        "lapses": 0,
        "last_review": datetime.now(timezone.utc) - timedelta(days=1),
    }
    output = scheduler.review_card(card_dict, rating=int(FSRSReviewGrade.AGAIN))
    assert output.difficulty <= 10.0


# ---------------------------------------------------------------------------
# Feature 40: Review Load Balancer
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f40_load_balancer_daily_review_cap():
    """Verify daily scheduled reviews do not exceed configured ceiling."""
    balancer = ReviewLoadBalancer()
    now = datetime.now(timezone.utc)
    cards = [
        {
            "card_id": f"C_{i}",
            "stability": 2.0 + (i % 5),
            "difficulty": 5.0,
            "criticality_weight": 0.5,
            "last_review": now - timedelta(days=5),
        }
        for i in range(25)
    ]
    batch = balancer.balance_daily_batch(cards, current_date=now, daily_capacity=10)
    assert batch["accepted_count"] == 10
    assert batch["excess_count"] == 15


@pytest.mark.tier1
def test_f40_load_balancer_priority_score_ordering():
    """Verify high criticality cards receive higher priority scores."""
    balancer = ReviewLoadBalancer()
    now = datetime.now(timezone.utc)
    card_high_crit = FSRSCardBase(
        card_id="CRIT_01",
        stability=3.0,
        difficulty=5.0,
        criticality_weight=1.0,
        last_review=now - timedelta(days=3),
    )
    card_low_crit = FSRSCardBase(
        card_id="LOW_01",
        stability=3.0,
        difficulty=5.0,
        criticality_weight=0.1,
        last_review=now - timedelta(days=3),
    )
    p_high = balancer.calculate_priority_score(card_high_crit, now)
    p_low = balancer.calculate_priority_score(card_low_crit, now)
    assert p_high > p_low


@pytest.mark.tier1
def test_f40_load_balancer_reallocation_distribution():
    """Verify postponed cards are distributed across future days."""
    balancer = ReviewLoadBalancer()
    now = datetime.now(timezone.utc)
    cards = [
        {
            "card_id": f"CARD_{i}",
            "stability": 25.0,
            "difficulty": 5.0,
            "criticality_weight": 0.5,
            "last_review": now - timedelta(days=2),
        }
        for i in range(15)
    ]
    batch = balancer.balance_daily_batch(cards, current_date=now, daily_capacity=5)
    postponed = batch["postponed_cards"]
    assert len(postponed) == 10
    assert all("postponed_to_days" in p for p in postponed)


@pytest.mark.tier1
def test_f40_load_balancer_due_date_fuzzing():
    """Verify deterministic interval fuzzing prevents review clustering."""
    scheduler = FSRSScheduler()
    interval = 30.0
    fuzzed = scheduler.apply_fuzz(interval)
    assert fuzzed > 0


@pytest.mark.tier1
def test_f40_load_balancer_zero_cards_due_idle_state():
    """Verify system remains in clean idle state when zero cards are provided."""
    balancer = ReviewLoadBalancer()
    now = datetime.now(timezone.utc)
    batch = balancer.balance_daily_batch([], current_date=now, daily_capacity=20)
    assert batch["accepted_count"] == 0
    assert batch["excess_count"] == 0
