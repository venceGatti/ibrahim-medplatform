"""Feature 28: Numerically Stable Log-Sum-Exp Softmax Normalizer."""
import math
from typing import Union, List
import numpy as np
from ..interfaces.diagnostic import ILogSumExpNormalizer


class LogSumExpNormalizer(ILogSumExpNormalizer):
    """Numerically stable softmax normalization preventing floating-point overflow."""

    def normalize_logits(self, logits: Union[np.ndarray, List[float]]) -> np.ndarray:
        """Convert arbitrary unnormalized logits to probabilities summing to 1.0."""
        z = np.asarray(logits, dtype=np.float64)
        if z.size == 0:
            return np.array([], dtype=np.float64)

        # Filter out -inf to find max finite logit
        finite_mask = np.isfinite(z)
        if not np.any(finite_mask):
            # All logits are -inf: uniform 0 distribution
            return np.zeros_like(z)

        c = np.max(z[finite_mask])

        # Shift by c and compute exponents safely
        shifted = z - c
        exp_vals = np.zeros_like(shifted)
        exp_vals[finite_mask] = np.exp(shifted[finite_mask])

        sum_exp = np.sum(exp_vals)
        if sum_exp <= 0.0 or not np.isfinite(sum_exp):
            return np.zeros_like(z)

        lse = c + math.log(sum_exp)
        probs = np.zeros_like(z)
        probs[finite_mask] = np.exp(z[finite_mask] - lse)

        # Normalize sum to exactly 1.0 across finite entries
        total_p = np.sum(probs)
        if total_p > 0.0:
            probs = probs / total_p

        return probs
