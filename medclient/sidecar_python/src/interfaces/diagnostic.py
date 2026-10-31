"""Interfaces for the multi-stage diagnostic engine."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
import numpy as np


class IRedFlagsInterceptor(ABC):
    """Evaluates Shock Index, qSOFA, and NEWS2 vital thresholds."""

    @abstractmethod
    def evaluate(self, vitals: Dict[str, Any]) -> Dict[str, Any]:
        """Compute physiological risk and return triage assessment."""
        raise NotImplementedError("Subclasses must implement evaluate")


class ILogOddsRanker(ABC):
    """Computes disease ranking logits using sparse CSR log-odds and Dirichlet smoothing."""

    @abstractmethod
    def score_diseases(
        self,
        positive_features: List[str],
        negative_features: List[str],
        cluster_assignments: Dict[str, str],
        pathognomonic_flags: Dict[str, bool],
    ) -> List[Tuple[str, float, List[str], List[str]]]:
        """Return scored candidates: (disease_id, raw_logit, supporting_symptoms, refutations)."""
        raise NotImplementedError("Subclasses must implement score_diseases")


class IPertinentNegativesEvaluator(ABC):
    """Applies negative penalty detraction and strict rule-out (-inf)."""

    @abstractmethod
    def apply_rule_outs(
        self,
        candidate_scores: Dict[str, float],
        refuted_features: List[str],
        feature_probs: Dict[Tuple[str, str], float],
    ) -> Dict[str, float]:
        """Update candidate logits with negative penalties and strict exclusions."""
        raise NotImplementedError("Subclasses must implement apply_rule_outs")


class ILogSumExpNormalizer(ABC):
    """Numerically stable softmax normalization using Log-Sum-Exp."""

    @abstractmethod
    def normalize_logits(self, logits: np.ndarray) -> np.ndarray:
        """Compute stable posterior probabilities from raw logits."""
        raise NotImplementedError("Subclasses must implement normalize_logits")


class IActiveDiscriminator(ABC):
    """Next-Best-Question selector maximizing information gain per cost."""

    @abstractmethod
    def select_next_best_question(
        self,
        candidate_a: str,
        prob_a: float,
        candidate_b: str,
        prob_b: float,
        uninvestigated_features: List[str],
        feature_costs: Dict[str, float],
    ) -> Dict[str, Any]:
        """Identify feature maximizing information gain per unit cost."""
        raise NotImplementedError("Subclasses must implement select_next_best_question")
