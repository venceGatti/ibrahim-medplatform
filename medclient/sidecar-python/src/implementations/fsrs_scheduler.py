"""Feature 39: FSRS v4/v5 Spaced Repetition Mnemonic Scheduler."""
import math
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from ..interfaces.educational import IFSRSScheduler
from ..base.educational_models import (
    FSRSCardBase,
    FSRSReviewGrade,
    FSRSStateEnum,
    FSRSReviewInput,
    FSRSReviewOutput,
)


DEFAULT_FSRS_WEIGHTS: List[float] = [
    0.40255, 1.18385, 3.173, 15.69105,  # w0-w3: Initial Stability (Again, Hard, Good, Easy)
    7.1949, 0.5345,                      # w4-w5: Initial Difficulty
    1.4604, 0.0046,                      # w6-w7: Difficulty Updates
    1.5457, 0.1532, 1.015,               # w8-w10: Stability Updates on Recall
    1.9395, 0.11, 0.296, 0.2269,         # w11-w14: Lapse Stability Updates
    0.2315, 2.9898,                      # w15-w16: Hard and Easy Modifiers
]

FACTOR: float = 19.0 / 81.0


class ReviewResultDict(dict):
    """Dictionary supporting dot-attribute access for FSRS results."""
    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            if "card_state" in self and isinstance(self["card_state"], dict) and name in self["card_state"]:
                return self["card_state"][name]
            raise AttributeError(f"'ReviewResultDict' object has no attribute '{name}'")


class FSRSScheduler(IFSRSScheduler):
    """Spaced repetition engine implementing the Free Spaced Repetition Scheduler model."""

    def __init__(self, weights: Optional[List[float]] = None) -> None:
        self.w = weights if weights is not None else DEFAULT_FSRS_WEIGHTS

    def step(self, review_input: Any, card_state: Optional[Dict[str, Any]] = None) -> Any:
        """Compatibility adapter executing review_card from an FSRSReviewInput model or dict."""
        if hasattr(review_input, "rating"):
            grade_val = int(review_input.rating)
            review_time_val = getattr(review_input, "review_time", None)
            target_exam_val = getattr(review_input, "target_exam_date", None)
            desired_ret_val = getattr(review_input, "desired_retention", 0.90)
            concept_uid_val = getattr(review_input, "concept_uid", "concept_card")
            card_dict = card_state or {
                "concept_uid": concept_uid_val,
                "stability": getattr(review_input, "stability", 2.0) if hasattr(review_input, "stability") else 2.0,
                "difficulty": getattr(review_input, "difficulty", 5.0) if hasattr(review_input, "difficulty") else 5.0,
                "elapsed_days": getattr(review_input, "elapsed_days", 0.0) if hasattr(review_input, "elapsed_days") else 0.0,
                "reps": getattr(review_input, "reps", 0) if hasattr(review_input, "reps") else 0,
                "lapses": getattr(review_input, "lapses", 0) if hasattr(review_input, "lapses") else 0,
            }
        elif isinstance(review_input, dict):
            grade_val = int(review_input.get("rating", 3))
            review_time_val = review_input.get("review_time")
            target_exam_val = review_input.get("target_exam_date")
            desired_ret_val = float(review_input.get("desired_retention", 0.90))
            card_dict = card_state or dict(review_input)
        else:
            grade_val = 3
            review_time_val = None
            target_exam_val = None
            desired_ret_val = 0.90
            card_dict = card_state or {}

        return self.review_card(
            card_state=card_dict,
            rating=grade_val,
            review_time=review_time_val,
            desired_retention=desired_ret_val,
            target_exam_date=target_exam_val,
        )

    def process_step(self, review_input: FSRSReviewInput) -> Any:
        """Compatibility adapter executing review_card from an FSRSReviewInput model."""
        card_instance = FSRSCardBase(
            concept_uid="concept_card",
            stability=review_input.stability,
            difficulty=review_input.difficulty,
            elapsed_days=review_input.elapsed_days,
            scheduled_days=0.0,
            reps=review_input.reps,
            lapses=review_input.lapses,
            state=FSRSStateEnum.REVIEW,
            last_review=datetime.now(timezone.utc),
            due_date=datetime.now(timezone.utc),
            retrievability=1.0,
            criticality_weight=1.0,
        )
        grade_enum = FSRSReviewGrade(review_input.rating)
        return self.review_card(card_instance, grade_enum)

    def calculate_retrievability(self, elapsed_days: float, stability: float) -> float:
        """Calculate memory retrievability probability R(t, S)."""
        if stability <= 0.0:
            return 0.0
        return math.pow(1.0 + FACTOR * (max(0.0, elapsed_days) / stability), -0.5)

    def calculate_interval(self, stability: float, target_retention: float) -> float:
        """Invert forgetting curve to calculate nominal interval for target retention."""
        target_retention = max(0.01, min(0.99, target_retention))
        return (81.0 / 19.0) * stability * (math.pow(target_retention, -2.0) - 1.0)

    def apply_fuzz(
        self,
        interval: float,
        target_exam_delta: Optional[float] = None,
        concept_uid: str = "",
        reps: int = 0,
    ) -> float:
        """Apply deterministic SHA256 fuzzing (ROA-17) when interval >= 2.5 days."""
        if interval < 2.5:
            return interval

        import hashlib
        raw_seed = f"{concept_uid}{reps}".encode("utf-8")
        hash_hex = hashlib.sha256(raw_seed).hexdigest()[:8]
        hash_val = int(hash_hex, 16) % 1000

        fuzz_factor = 0.05 if interval < 7.0 else (0.10 if interval < 30.0 else 0.15)
        # Scaled deterministic dispersion
        fuzzed = interval * (1.0 + fuzz_factor * (float(hash_val - 500) / 500.0))

        if target_exam_delta is not None and fuzzed > target_exam_delta:
            return max(1.0, target_exam_delta)
        return max(1.0, fuzzed)

    def review_card(
        self,
        card_state: Dict[str, Any],
        rating: int,
        review_time: Optional[datetime] = None,
        desired_retention: float = 0.90,
        target_exam_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Process card review interaction and return updated FSRS state."""
        card = FSRSCardBase(**card_state) if isinstance(card_state, dict) else card_state
        grade = FSRSReviewGrade(rating)
        now = (review_time or datetime.now(timezone.utc)).astimezone(timezone.utc)

        # 1. Elapsed days
        if card.last_review:
            elapsed_days = max(0.0, (now - card.last_review.astimezone(timezone.utc)).total_seconds() / 86400.0)
        else:
            elapsed_days = 0.0

        current_r = self.calculate_retrievability(elapsed_days, card.stability)

        # 2. Update Difficulty
        d_raw = (
            self.w[4] - (grade.value - 3) * self.w[5]
            if card.reps == 0
            else card.difficulty - self.w[7] * (grade.value - 3)
        )
        mean_rev_d = self.w[6] * (self.w[4] - (3 - 3) * self.w[5]) + (1.0 - self.w[6]) * d_raw
        new_difficulty = max(1.0, min(10.0, mean_rev_d))

        # 3. Update Stability
        relearning_flag = False
        if card.reps == 0:
            new_stability = self.w[grade.value - 1]
            new_state = FSRSStateEnum.REVIEW if grade > FSRSReviewGrade.AGAIN else FSRSStateEnum.LEARNING
        else:
            if grade == FSRSReviewGrade.AGAIN:
                new_stability = (
                    self.w[11]
                    * math.pow(card.difficulty, -self.w[12])
                    * (math.pow(card.stability + 1.0, self.w[13]) - 1.0)
                    * math.exp((1.0 - current_r) * self.w[14])
                )
                new_stability = min(card.stability, max(0.1, new_stability))
                new_state = FSRSStateEnum.RELEARNING
                relearning_flag = True
            else:
                grade_scaling_factor = (
                    self.w[15]
                    if grade == FSRSReviewGrade.HARD
                    else (1.0 if grade == FSRSReviewGrade.GOOD else self.w[16])
                )
                new_stability = card.stability * (
                    1.0
                    + math.exp(self.w[8])
                    * (11.0 - card.difficulty)
                    * math.pow(card.stability, -self.w[9])
                    * (math.exp((1.0 - current_r) * self.w[10]) - 1.0)
                    * grade_scaling_factor
                )
                new_state = FSRSStateEnum.REVIEW

        # 4. Calculate Interval
        nominal_interval = self.calculate_interval(new_stability, desired_retention)

        # 5. Exam-date compression
        exam_compressed = False
        target_exam_delta = None
        if target_exam_date:
            target_exam_delta = (target_exam_date.astimezone(timezone.utc) - now).total_seconds() / 86400.0
            if target_exam_delta > 0:
                if nominal_interval > target_exam_delta:
                    nominal_interval = max(1.0, target_exam_delta)
                    exam_compressed = True
            else:
                nominal_interval = 1.0

        final_interval = max(
            1,
            round(
                self.apply_fuzz(
                    nominal_interval,
                    target_exam_delta,
                    concept_uid=card.concept_uid,
                    reps=card.reps,
                )
            ),
        )
        due_date = now + timedelta(days=final_interval)

        updated_card = FSRSCardBase(
            concept_uid=card.concept_uid,
            stability=round(new_stability, 4),
            difficulty=round(new_difficulty, 4),
            elapsed_days=round(elapsed_days, 2),
            scheduled_days=float(final_interval),
            reps=card.reps + 1,
            lapses=card.lapses + (1 if grade == FSRSReviewGrade.AGAIN else 0),
            state=new_state,
            last_review=now,
            due_date=due_date,
            retrievability=1.0,
            criticality_weight=card.criticality_weight,
        )

        output = FSRSReviewOutput(
            card_state=updated_card,
            interval_days=final_interval,
            projected_retention=round(self.calculate_retrievability(float(final_interval), new_stability), 4),
            is_exam_compressed=exam_compressed,
            relearning_priority=relearning_flag,
        )
        res_dict = output.model_dump()
        res_dict["stability"] = updated_card.stability
        res_dict["difficulty"] = updated_card.difficulty
        res_dict["state"] = updated_card.state
        return ReviewResultDict(res_dict)
