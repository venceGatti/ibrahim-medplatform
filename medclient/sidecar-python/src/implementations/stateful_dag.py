"""Feature 38: Stateful DAG Clinical Scenario Stepper Engine."""
from typing import Dict, Any, List, Optional
from ..interfaces.educational import IStatefulDAGScenario
from ..base.educational_models import (
    StatefulDAGPayload,
    DAGNode,
    DAGTransition,
    PatientVitals,
)
from ..base.exceptions import InvalidDAGTransitionError


class StatefulDAGScenarioEngine(IStatefulDAGScenario):
    """Executes stateful branching clinical scenarios with dynamic patient vitals and cost/risk tracking."""

    def __init__(self, dag_specification: Dict[str, Any]) -> None:
        self._scenario_definition = StatefulDAGPayload(**dag_specification)
        self._current_node_id = self._scenario_definition.initial_node_id
        self._elapsed_time_min = 0.0
        self._accumulated_cost_eur = 0.0
        self._accumulated_risk = 0.0
        self._action_history: List[str] = []

    def get_current_node(self) -> DAGNode:
        """Return active DAG node."""
        return self._scenario_definition.nodes[self._current_node_id]

    def transition(
        self,
        current_node_id: str,
        action_id: str,
        current_vitals: Dict[str, float],
    ) -> Dict[str, Any]:
        """Apply clinical action, update vitals with deltas, and transition state."""
        node = self._scenario_definition.nodes.get(current_node_id)
        if not node:
            raise InvalidDAGTransitionError(f"Node {current_node_id} does not exist in DAG.")

        matching_trans: Optional[DAGTransition] = None
        for trans in node.available_transitions:
            if trans.action_id == action_id:
                matching_trans = trans
                break

        if not matching_trans:
            raise InvalidDAGTransitionError(
                f"Action '{action_id}' is not an available transition from node '{current_node_id}'."
            )

        dest_node = self._scenario_definition.nodes.get(matching_trans.destination_node_id)
        if not dest_node:
            raise InvalidDAGTransitionError(
                f"Destination node '{matching_trans.destination_node_id}' not found in DAG."
            )

        # Update vitals
        updated_vitals = dict(current_vitals)
        if matching_trans.vitals_delta:
            for k, delta in matching_trans.vitals_delta.items():
                if k in updated_vitals:
                    updated_vitals[k] = round(updated_vitals[k] + delta, 2)

        # Update tracking metrics
        self._elapsed_time_min += matching_trans.time_cost_min
        self._accumulated_cost_eur += matching_trans.financial_cost_eur
        self._accumulated_risk = min(1.0, self._accumulated_risk + matching_trans.risk_severity)
        self._action_history.append(action_id)
        self._current_node_id = dest_node.node_id

        # Terminal evaluation
        is_terminal = dest_node.is_terminal
        terminal_grade = dest_node.terminal_grade

        return {
            "previous_node_id": current_node_id,
            "next_node_id": dest_node.node_id,
            "narrative_state": dest_node.narrative_state,
            "updated_vitals": updated_vitals,
            "action_id": action_id,
            "clinical_consequence": matching_trans.clinical_consequence,
            "elapsed_time_min": self._elapsed_time_min,
            "accumulated_cost_eur": self._accumulated_cost_eur,
            "total_cost_eur": self._accumulated_cost_eur,
            "accumulated_risk": round(self._accumulated_risk, 3),
            "is_terminal": is_terminal,
            "terminal_grade": terminal_grade,
            "final_score": terminal_grade,
            "available_transitions": [t.model_dump() for t in dest_node.available_transitions],
        }
