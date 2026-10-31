"""Feature 32: Deterministic Triple Whammy Acute Kidney Injury Detector with FDC Decomposition (ROA-14)."""
from typing import List, Dict, Any
from ..interfaces.pharmacology import ITripleWhammyDetector
from ..base.pharmacology_models import SeverityLevel
from ..base.pharmacology_catalogs import decompose_fdc_prescriptions


class TripleWhammyDetector(ITripleWhammyDetector):
    """Detects concomitant prescription of RAS Blocker, Diuretic, and systemic NSAID."""

    def _is_ras_blocker(self, drug: Dict[str, Any]) -> bool:
        """Check if drug is an ACE-inhibitor (C09A*/C09B*) or ARB (C09C*/C09D*)."""
        if drug.get("is_ras_blocker", False):
            return True
        atc = str(drug.get("atc_code", "")).strip().upper()
        return atc.startswith(("C09A", "C09B", "C09C", "C09D"))

    def _is_diuretic(self, drug: Dict[str, Any]) -> bool:
        """Check if drug is a diuretic (C03* or combined C09BA*/C09DA*)."""
        if drug.get("is_diuretic", False):
            return True
        atc = str(drug.get("atc_code", "")).strip().upper()
        return atc.startswith(("C03", "C09BA", "C09DA"))

    def _is_nsaid(self, drug: Dict[str, Any]) -> bool:
        """Check if drug is a systemic NSAID (M01A*), excluding topical routes."""
        route = str(drug.get("route", "oral")).strip().upper()
        if route in ("TOPICAL", "CUTANEOUS", "OPHTHALMIC"):
            return False
        if drug.get("is_nsaid", False):
            return True
        atc = str(drug.get("atc_code", "")).strip().upper()
        return atc.startswith("M01A")

    def detect_triple_whammy(
        self,
        prescribed_drugs: List[Dict[str, Any]],
        egfr: float,
    ) -> Dict[str, Any]:
        """Decompose FDCs (ROA-14), detect Triple Whammy triad, and compute nephrotoxicity score."""
        expanded_drugs = decompose_fdc_prescriptions(prescribed_drugs)

        ras_blockers = [d for d in expanded_drugs if self._is_ras_blocker(d)]
        diuretics = [d for d in expanded_drugs if self._is_diuretic(d)]
        nsaids = [d for d in expanded_drugs if self._is_nsaid(d)]

        has_triple_whammy = (len(ras_blockers) > 0) and (len(diuretics) > 0) and (len(nsaids) > 0)

        base_nephro_score = 0.0
        for drug_entry in expanded_drugs:
            weight = float(drug_entry.get("nephrotoxicity_weight", 0.0))
            if weight == 0.0:
                if self._is_nsaid(drug_entry):
                    weight = 2.0
                elif self._is_diuretic(drug_entry):
                    weight = 1.0
                elif self._is_ras_blocker(drug_entry):
                    weight = 1.0
            base_nephro_score += weight

        if has_triple_whammy:
            renal_load_score = base_nephro_score + 3.0
            if egfr < 60.0:
                severity = SeverityLevel.LEVEL_1
                message = (
                    f"CRITICAL: Triple Whammy detected in patient with impaired renal function (eGFR={egfr:.1f} mL/min). "
                    "Profound risk of acute tubular necrosis. Immediate cessation of NSAID required."
                )
            else:
                severity = SeverityLevel.LEVEL_2
                message = (
                    f"MAJOR: Triple Whammy co-prescription (eGFR={egfr:.1f} mL/min). "
                    "Renal function and serum electrolytes must be closely monitored."
                )
        else:
            renal_load_score = base_nephro_score
            severity = SeverityLevel.LEVEL_4
            message = "No Triple Whammy triad detected."

        return {
            "triple_whammy_detected": has_triple_whammy,
            "has_triple_whammy": has_triple_whammy,
            "renal_load_score": round(renal_load_score, 2),
            "severity_level": severity,
            "severity": severity,
            "clinical_warning": message,
            "involved_ras_blockers": [d.get("atc_code") for d in ras_blockers],
            "involved_diuretics": [d.get("atc_code") for d in diuretics],
            "involved_nsaids": [d.get("atc_code") for d in nsaids],
        }
