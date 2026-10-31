"""Interfaces for educational examination, NLI evaluation, and FSRS."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime


class INLICrossEncoder(ABC):
    """Evaluates free-text answers against atomic concepts using NLI Cross-Encoder."""

    @abstractmethod
    def evaluate_response(
        self,
        student_text: str,
        atomic_concepts: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Score entailment vs contradiction and apply anti-cheating penalties."""
        raise NotImplementedError("Subclasses must implement evaluate_response")


class IStatefulDAGScenario(ABC):
    """Executes stateful clinical scenario DAG transitions and updates vitals."""

    @abstractmethod
    def transition(
        self,
        current_node_id: str,
        action_id: str,
        current_vitals: Dict[str, float],
    ) -> Dict[str, Any]:
        """Apply transition action, compute vitals delta, and return new state."""
        raise NotImplementedError("Subclasses must implement transition")


class IFSRSScheduler(ABC):
    """Spaced repetition scheduler computing stability, difficulty, and intervals."""

    @abstractmethod
    def review_card(
        self,
        card_state: Dict[str, Any],
        rating: int,
        review_time: datetime,
        desired_retention: float = 0.90,
        target_exam_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Calculate updated memory stability S, difficulty D, and review interval."""
        raise NotImplementedError("Subclasses must implement review_card")


class IReviewLoadBalancer(ABC):
    """Mitigates Review Hell by balancing daily load and prioritizing exam dates."""

    @abstractmethod
    def balance_daily_batch(
        self,
        cards: List[Dict[str, Any]],
        current_date: datetime,
        daily_capacity: int = 350,
        target_exam_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Distribute due cards respecting capacity limits and retention priority."""
        raise NotImplementedError("Subclasses must implement balance_daily_batch")
