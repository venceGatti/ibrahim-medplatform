"""Interfaces for Pharmacology and Drug Safety Engine."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class ICYP450Engine(ABC):
    """Calculates multi-way CYP450 clearance with active drug vs prodrug logic."""

    @abstractmethod
    def evaluate_clearance(
        self,
        prescribed_drugs: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Compute residual clearance Ce, substrate AUC ratios, and safety alerts."""
        raise NotImplementedError("Subclasses must implement evaluate_clearance")


class IQTcCalculator(ABC):
    """Computes cumulative QTc prolongation risk score."""

    @abstractmethod
    def evaluate_qtc(
        self,
        prescribed_drugs: List[Dict[str, Any]],
        auc_ratios: Dict[str, float],
        serum_potassium_meq_l: float,
    ) -> Dict[str, Any]:
        """Compute QTc score and torsades de pointes risk classification."""
        raise NotImplementedError("Subclasses must implement evaluate_qtc")


class ITripleWhammyDetector(ABC):
    """Detects acute kidney injury triad (RAS blocker + Diuretic + NSAID)."""

    @abstractmethod
    def detect_triple_whammy(
        self,
        prescribed_drugs: List[Dict[str, Any]],
        egfr: float,
    ) -> Dict[str, Any]:
        """Check for Triple Whammy co-prescription and evaluate severity."""
        raise NotImplementedError("Subclasses must implement detect_triple_whammy")


class IRenalCalculator(ABC):
    """Computes race-free CKD-EPI 2021 estimated glomerular filtration rate."""

    @abstractmethod
    def compute_egfr(
        self,
        age: int,
        is_female: bool,
        serum_creatinine_mg_dl: float,
    ) -> float:
        """Calculate eGFR in mL/min/1.73m2 without race coefficient."""
        raise NotImplementedError("Subclasses must implement compute_egfr")


class IPharmacogenomicsEngine(ABC):
    """Matches CPIC Level 1A guidelines against patient genotype."""

    @abstractmethod
    def evaluate_genetics(
        self,
        prescribed_drugs: List[Dict[str, Any]],
        patient_genotypes: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        """Return actionable pharmacogenomic contraindications and guidance."""
        raise NotImplementedError("Subclasses must implement evaluate_genetics")
