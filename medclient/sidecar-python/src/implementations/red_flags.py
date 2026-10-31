"""Feature 25: Deterministic Red Flags Interceptor (Shock Index, qSOFA, NEWS2 - ROA-21)."""
from typing import Dict, Any, List
from ..interfaces.diagnostic import IRedFlagsInterceptor
from ..base.diagnostic_models import SystemAlertLevel, RedFlagsAssessment, VitalSigns
from ..base.exceptions import InvalidVitalsError


class RedFlagsInterceptor(IRedFlagsInterceptor):
    """Evaluates patient vital signs against emergency resuscitation thresholds."""

    def evaluate(self, vitals: Dict[str, Any]) -> Dict[str, Any]:
        """Compute Shock Index (3 decimals), qSOFA, and NEWS2, determining triage level."""
        if isinstance(vitals, dict):
            raw_sbp = float(vitals.get("systolic_bp_mmhg", 120.0))
            raw_hr = float(vitals.get("heart_rate_bpm", 80.0))
            if raw_sbp <= 0.0 or raw_hr <= 0.0:
                raise InvalidVitalsError("Systolic blood pressure and heart rate must be strictly positive")
            v = VitalSigns(**vitals)
        else:
            v = vitals

        hr = v.heart_rate_bpm
        sbp = v.systolic_bp_mmhg
        rr = v.respiratory_rate_bpm
        spo2 = v.spo2_percent
        body_temperature_celsius = v.temperature_celsius
        avpu = v.avpu_scale.upper()
        gcs = v.gcs_score
        supp_o2 = v.supplemental_o2
        hypercapnic = v.hypercapnic_risk

        critical_triggers: List[str] = []

        # 1. Shock Index (SI = HR / SBP) rounded to 3 decimal places
        shock_index = round(hr / max(1.0, sbp), 3)
        if shock_index >= 1.0 or sbp <= 90.0:
            critical_triggers.append("CRITICAL_SHOCK_INDEX_GE_1")

        # 2. qSOFA (Respiratory rate >= 22, Altered mentation, SBP <= 100)
        qsofa_score = 0
        if rr >= 22.0:
            qsofa_score += 1
        if gcs < 15 or avpu != "A":
            qsofa_score += 1
        if sbp <= 100.0:
            qsofa_score += 1

        if qsofa_score >= 2:
            critical_triggers.append("QSOFA_SCORE_GE_2")

        # 3. NEWS2
        news2_score, has_param_three = self._calculate_news2(
            rr=rr,
            spo2=spo2,
            hypercapnic=hypercapnic,
            supp_o2=supp_o2,
            sbp=sbp,
            hr=hr,
            avpu=avpu,
            body_temperature_celsius=body_temperature_celsius,
        )

        if news2_score >= 7 or has_param_three:
            critical_triggers.append("NEWS2_HIGH_RISK_TIER")

        # Determine Alert Level
        if len(critical_triggers) > 0:
            alert_level = SystemAlertLevel.RED_CRITICAL
        elif news2_score >= 5:
            alert_level = SystemAlertLevel.YELLOW_ATTENTION
        else:
            alert_level = SystemAlertLevel.NOMINAL

        assessment = RedFlagsAssessment(
            alert_level=alert_level,
            shock_index=shock_index,
            qsofa_score=qsofa_score,
            news2_score=news2_score,
            critical_triggers=critical_triggers,
        )
        return assessment.model_dump()

    def _calculate_news2(
        self,
        rr: float,
        spo2: float,
        hypercapnic: bool,
        supp_o2: bool,
        sbp: float,
        hr: float,
        avpu: str,
        body_temperature_celsius: float,
    ) -> tuple[int, bool]:
        """Compute Royal College of Physicians NEWS2 score (Scale 1 & Scale 2 ROA-21)."""
        score = 0
        has_three = False

        # Respiration rate
        if rr <= 8:
            score += 3
            has_three = True
        elif 9 <= rr <= 11:
            score += 1
        elif 12 <= rr <= 20:
            score += 0
        elif 21 <= rr <= 24:
            score += 2
        else:  # >= 25
            score += 3
            has_three = True

        # SpO2 single-parameter points
        spo2_points = 0
        if not hypercapnic:
            # Scale 1
            if spo2 <= 91:
                spo2_points = 3
            elif 92 <= spo2 <= 93:
                spo2_points = 2
            elif 94 <= spo2 <= 95:
                spo2_points = 1
            else:
                spo2_points = 0
        else:
            # Scale 2 (Hypercapnic respiratory failure risk - Royal College of Physicians)
            if spo2 <= 83:
                spo2_points = 3
            elif 84 <= spo2 <= 85:
                spo2_points = 2
            elif 86 <= spo2 <= 87:
                spo2_points = 1
            elif 88 <= spo2 <= 92:
                spo2_points = 0
            elif 93 <= spo2 <= 94:
                spo2_points = 1 if supp_o2 else 0
            elif 95 <= spo2 <= 96:
                spo2_points = 2 if supp_o2 else 0
            else:  # >= 97
                spo2_points = 3 if supp_o2 else 0

        score += spo2_points
        if spo2_points == 3:
            has_three = True

        # Supplemental O2
        if supp_o2:
            score += 2

        # Systolic BP
        if sbp <= 90:
            score += 3
            has_three = True
        elif 91 <= sbp <= 100:
            score += 2
        elif 101 <= sbp <= 110:
            score += 1
        elif 111 <= sbp <= 219:
            score += 0
        else:  # >= 220
            score += 3
            has_three = True

        # Heart rate
        if hr <= 40:
            score += 3
            has_three = True
        elif 41 <= hr <= 50:
            score += 1
        elif 51 <= hr <= 90:
            score += 0
        elif 91 <= hr <= 110:
            score += 1
        elif 111 <= hr <= 130:
            score += 2
        else:  # >= 131
            score += 3
            has_three = True

        # Consciousness
        if avpu != "A":
            score += 3
            has_three = True

        # Temperature
        if body_temperature_celsius <= 35.0:
            score += 3
            has_three = True
        elif 35.1 <= body_temperature_celsius <= 36.0:
            score += 1
        elif 36.1 <= body_temperature_celsius <= 38.0:
            score += 0
        elif 38.1 <= body_temperature_celsius <= 39.0:
            score += 1
        else:  # >= 39.1
            score += 2

        return score, has_three
