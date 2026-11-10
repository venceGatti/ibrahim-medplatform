"""Feature 29: Active Discrimination (Next-Best-Question / NBQ)."""
import math
from typing import List, Dict, Any, Optional
from ..interfaces.diagnostic import IActiveDiscriminator
from ..base.diagnostic_models import NextBestQuestion


class ActiveDiscriminator(IActiveDiscriminator):
    """Calculates information gain per cost across uninvestigated symptoms to separate top differential candidates."""

    def __init__(self, probability_gap_threshold: float = 0.15) -> None:
        self.gap_threshold = probability_gap_threshold

    def select_next_best_question(
        self,
        candidate_a: str,
        prob_a: float,
        candidate_b: str,
        prob_b: float,
        uninvestigated_features: List[str],
        feature_costs: Dict[str, float],
        feature_labels: Optional[Dict[str, str]] = None,
        feature_probs_a: Optional[Dict[str, float]] = None,
        feature_probs_b: Optional[Dict[str, float]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Identify feature maximizing information gain per unit cost."""
        if abs(prob_a - prob_b) >= self.gap_threshold:
            # Candidates are already conclusively separated
            return None

        total_pair_prob = prob_a + prob_b
        if total_pair_prob <= 0.0:
            return None

        p1 = prob_a / total_pair_prob
        p2 = prob_b / total_pair_prob

        # Shannon entropy
        h_d = self._binary_entropy(p1)

        f_probs_a = feature_probs_a or {}
        f_probs_b = feature_probs_b or {}
        labels = feature_labels or {}

        best_feature: Optional[str] = None
        best_ratio = -1.0
        best_ig = 0.0

        for f in uninvestigated_features:
            p_f_d1 = f_probs_a.get(f, 0.5)
            p_f_d2 = f_probs_b.get(f, 0.5)

            # Check if feature has discriminative value
            if abs(p_f_d1 - p_f_d2) < 0.01:
                continue

            # Marginal probability P(f = 1)
            p_f_1 = p1 * p_f_d1 + p2 * p_f_d2
            p_f_0 = 1.0 - p_f_1

            if p_f_1 <= 1e-6 or p_f_0 <= 1e-6:
                continue

            # Conditional posteriors
            p1_given_1 = (p1 * p_f_d1) / p_f_1
            p1_given_0 = (p1 * (1.0 - p_f_d1)) / p_f_0

            h_given_1 = self._binary_entropy(p1_given_1)
            h_given_0 = self._binary_entropy(p1_given_0)

            expected_h = p_f_1 * h_given_1 + p_f_0 * h_given_0
            ig = max(0.0, h_d - expected_h)

            cost = max(1.0, feature_costs.get(f, 1.0))
            ratio = ig / cost

            if ratio > best_ratio:
                best_ratio = ratio
                best_ig = ig
                best_feature = f

        if best_feature is None:
            return None

        label = labels.get(best_feature, best_feature)
        nbq = NextBestQuestion(
            target_hpo_id=best_feature,
            target_phenotype_label=label,
            expected_information_gain=round(best_ig, 4),
            clinical_justification=f"Differentiates {candidate_a} from {candidate_b} with max information gain per cost.",
        )
        return nbq.model_dump()

    def _binary_entropy(self, p: float) -> float:
        """Compute binary Shannon entropy H(p) with asymptotic epsilon guards (ROA-26)."""
        if p <= 1e-12 or p >= 1.0 - 1e-12:
            return 0.0
        return -(p * math.log2(p) + (1.0 - p) * math.log2(1.0 - p))
