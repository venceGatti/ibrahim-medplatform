"""Feature 31: Cumulative QTc Interval Prolongation and TdP Arrhythmia Guard."""
from typing import List, Dict, Any
from ..interfaces.pharmacology import IQTcCalculator
from ..base.pharmacology_models import SeverityLevel


class QTcCalculator(IQTcCalculator):
    """Calculates non-linear cumulative QTc score and evaluates ventricular arrhythmia risk."""

    # Baseline CredibleMeds scores: 3.0 (Known), 2.0 (Possible), 1.0 (Conditional)
    KNOWN_QTC_RISK = {
        "J01MA02": 3.0,  # Ciprofloxacin
        "J01MA12": 3.0,  # Levofloxacin
        "J01FA09": 3.0,  # Clarithromycin
        "J01FA10": 3.0,  # Azithromycin
        "C01BD01": 3.0,  # Amiodarone
        "C01BC04": 3.0,  # Flecainide
        "C01EB18": 3.0,  # Ranolazine
        "N05AA01": 3.0,  # Chlorpromazine
        "N05AD01": 3.0,  # Haloperidol
        "N05AX08": 3.0,  # Risperidone
        "N06AB04": 2.0,  # Citalopram
        "N06AB10": 2.0,  # Escitalopram
        "N06AA09": 2.0,  # Amitriptyline
        "A03FA01": 1.0,  # Metoclopramide
        "A02BC02": 1.0,  # Pantoprazole
    }

    def evaluate_qtc(
        self,
        prescribed_drugs: List[Dict[str, Any]],
        auc_ratios: Dict[str, float],
        serum_potassium_meq_l: float,
    ) -> Dict[str, Any]:
        """Compute cumulative QTc score and risk classification."""
        s_qtc = 0.0
        alerts: List[str] = []

        # 1. Sum up baseline QTc scores multiplied by substrate accumulation
        for drug in prescribed_drugs:
            atc = drug.get("atc_code", "")
            base_score = float(drug.get("qtc_base_risk") or self.KNOWN_QTC_RISK.get(atc, 0.0))
            auc = max(1.0, float(auc_ratios.get(atc, 1.0)))

            if base_score > 0.0:
                weighted_contribution = base_score * auc
                s_qtc += weighted_contribution
                if base_score >= 3.0:
                    alerts.append(f"{atc} has Known TdP Risk (base={base_score}, AUC={auc:.2f}x)")

        # 2. Check for hypokalemia or loop diuretic without potassium sparing
        has_hypokalemia = serum_potassium_meq_l < 3.5
        has_loop_diuretic = any(
            drug.get("is_diuretic", False) or drug.get("atc_code", "").startswith("C03C")
            for drug in prescribed_drugs
        )

        k_hypokalemia = 0.0
        if has_hypokalemia or (has_loop_diuretic and serum_potassium_meq_l < 4.0):
            k_hypokalemia = 1.5
            s_qtc += k_hypokalemia
            alerts.append(f"Hypokalemia / loop diuretic modifier applied (+{k_hypokalemia})")

        s_qtc = round(s_qtc, 2)

        # 3. Decision Thresholds
        if s_qtc >= 6.0:
            severity = SeverityLevel.LEVEL_1
            alerts.append("CRITICAL: S_QTc >= 6.0. Imminent Torsades de Pointes risk.")
        elif s_qtc >= 4.0:
            severity = SeverityLevel.LEVEL_2
            alerts.append("MAJOR: S_QTc >= 4.0. Continuous ECG monitoring required.")
        elif s_qtc >= 2.0:
            severity = SeverityLevel.LEVEL_3
            alerts.append("MODERATE: S_QTc >= 2.0. Electrolyte monitoring required.")
        else:
            severity = SeverityLevel.LEVEL_4

        return {
            "qtc_prolongation_score": s_qtc,
            "torsades_de_pointes_risk": severity,
            "alerts": alerts,
        }

    def calculate_qtc_intervals(
        self,
        raw_qt_ms: float,
        heart_rate_bpm: float,
    ) -> Dict[str, float]:
        """Calculate QTc using Bazett, Fridericia, Framingham, and Hodges formulas (ROA-11)."""
        if heart_rate_bpm <= 0.0 or raw_qt_ms <= 0.0:
            raise ValueError("Heart rate and QT interval must be strictly positive")
        rr_sec = 60.0 / heart_rate_bpm
        bazett = raw_qt_ms / (rr_sec ** 0.5)
        fridericia = raw_qt_ms / (rr_sec ** (1.0 / 3.0))
        framingham = raw_qt_ms + 154.0 * (1.0 - rr_sec)
        hodges = raw_qt_ms + 1.75 * (heart_rate_bpm - 60.0)
        return {
            "bazett_ms": round(bazett, 1),
            "fridericia_ms": round(fridericia, 1),
            "framingham_ms": round(framingham, 1),
            "hodges_ms": round(hodges, 1),
        }
