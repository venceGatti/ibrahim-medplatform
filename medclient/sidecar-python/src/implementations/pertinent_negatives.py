"""Feature 27: Pertinent Negatives Rule-Out Engine with Bounded/Strict Exclusion (ROA-15)."""
import math
from typing import List, Dict, Tuple, Any, Optional
from ..interfaces.diagnostic import IPertinentNegativesEvaluator

RULE_OUT_PENALTY: float = -12.0


class PertinentNegativesEvaluator(IPertinentNegativesEvaluator):
    """Calculates biological penalties and exclusions for refuted symptoms."""

    def __init__(
        self,
        rule_out_threshold: float = 0.99,
        epsilon: float = 1e-4,
        default_rule_out_penalty: float = -float("inf"),
    ) -> None:
        self.rule_out_threshold = rule_out_threshold
        self.epsilon = epsilon
        self.default_rule_out_penalty = default_rule_out_penalty
        self.last_rule_out_penalties: Dict[str, float] = {}

    def apply_rule_outs(
        self,
        candidate_scores: Dict[str, float],
        refuted_features: List[str],
        feature_probs: Dict[Tuple[str, str], float],
        rule_out_penalty: Optional[float] = None,
    ) -> Dict[str, float]:
        """Apply negative penalty detraction and rule-out penalty."""
        updated_scores = dict(candidate_scores)
        self.last_rule_out_penalties.clear()
        target_penalty = rule_out_penalty if rule_out_penalty is not None else self.default_rule_out_penalty

        for disease_code, current_logit in candidate_scores.items():
            if math.isinf(current_logit) and current_logit < 0:
                continue

            total_penalty = 0.0
            is_ruled_out = False

            for f_code in refuted_features:
                p_fi_dj = feature_probs.get((disease_code, f_code), self.epsilon)

                # Rule-Out Trigger
                if p_fi_dj >= self.rule_out_threshold:
                    is_ruled_out = True
                    break

                # Negative Weight of Evidence calculation
                p_fi_not_dj = max(self.epsilon, min(0.5, p_fi_dj * 0.3))
                num = max(1e-9, 1.0 - p_fi_dj)
                den = max(1e-9, 1.0 - p_fi_not_dj)
                neg_weight = math.log(num / den)
                total_penalty += neg_weight

            if is_ruled_out:
                updated_scores[disease_code] = target_penalty
                self.last_rule_out_penalties[disease_code] = target_penalty
            else:
                updated_scores[disease_code] = current_logit + total_penalty

        return updated_scores
