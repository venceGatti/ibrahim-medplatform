"""Feature 40: Review Load Balancer & Review Hell Mitigation Engine."""
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from ..interfaces.educational import IReviewLoadBalancer
from ..base.educational_models import FSRSCardBase
from .fsrs_scheduler import FSRSScheduler


class ReviewLoadBalancer(IReviewLoadBalancer):
    """Mitigates review overload and backlog collapse through priority scheduling and smoothing."""

    def __init__(self, scheduler: Optional[FSRSScheduler] = None) -> None:
        self._scheduler = scheduler or FSRSScheduler()

    def calculate_priority_score(
        self,
        card: FSRSCardBase,
        current_date: datetime,
        target_exam_date: Optional[datetime] = None,
    ) -> float:
        """Compute priority score Omega."""
        now = current_date.astimezone(timezone.utc)
        elapsed_days = (now - card.last_review.astimezone(timezone.utc)).total_seconds() / 86400.0 if card.last_review else 0.0
        r = self._scheduler.calculate_retrievability(elapsed_days, card.stability)

        exam_delta = 100.0
        if target_exam_date:
            exam_delta = max(1.0, (target_exam_date.astimezone(timezone.utc) - now).total_seconds() / 86400.0)

        omega = (
            (1.0 - r) * 0.4
            + (card.difficulty / 10.0) * 0.2
            + (card.criticality_weight) * 0.3
            + (1.0 / exam_delta) * 0.1
        )
        return omega

    def balance_daily_batch(
        self,
        cards: List[Dict[str, Any]],
        current_date: datetime,
        daily_capacity: int = 350,
        target_exam_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Rank and smooth daily card batch to prevent review hell."""
        card_objs = [FSRSCardBase(**c) if isinstance(c, dict) else c for c in cards]

        scored_cards = [
            (c, self.calculate_priority_score(c, current_date, target_exam_date))
            for c in card_objs
        ]
        # Sort descending by priority score Omega
        scored_cards.sort(key=lambda x: x[1], reverse=True)

        accepted_batch = scored_cards[:daily_capacity]
        excess_cards = scored_cards[daily_capacity:]

        reallocated_postponed: List[Dict[str, Any]] = []
        reallocated_advanced: List[Dict[str, Any]] = []

        now = current_date.astimezone(timezone.utc)

        for card, _ in excess_cards:
            elapsed_days = (now - card.last_review.astimezone(timezone.utc)).total_seconds() / 86400.0 if card.last_review else 0.0
            r_tomorrow = self._scheduler.calculate_retrievability(elapsed_days + 1.0, card.stability)

            card_dict = card.model_dump()
            if r_tomorrow >= 0.85:
                # Postpone by +2 days
                card_dict["due_date"] = (now + timedelta(days=2)).isoformat()
                card_dict["postponed_to_days"] = 2
                reallocated_postponed.append(card_dict)
            else:
                # Postpone to next day (+1 day), never into the past
                card_dict["due_date"] = (now + timedelta(days=1)).isoformat()
                card_dict["postponed_to_days"] = 1
                reallocated_postponed.append(card_dict)

        return {
            "capacity_limit": daily_capacity,
            "total_due_count": len(card_objs),
            "batch_size": len(accepted_batch),
            "accepted_count": len(accepted_batch),
            "excess_count": len(excess_cards),
            "daily_batch": [c.model_dump() for c, _ in accepted_batch],
            "postponed_cards": reallocated_postponed,
            "advanced_cards": reallocated_advanced,
        }
