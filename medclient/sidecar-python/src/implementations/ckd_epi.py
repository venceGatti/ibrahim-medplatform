"""Feature 33: Race-Free CKD-EPI 2021 Estimated Glomerular Filtration Rate Calculator."""
from ..interfaces.pharmacology import IRenalCalculator
from ..base.exceptions import InvalidRenalParameterError


class CKDEPI2021Calculator(IRenalCalculator):
    """Calculates eGFR using the 2021 Chronic Kidney Disease Epidemiology Collaboration equation."""

    def compute_egfr(
        self,
        age: int,
        is_female: bool,
        serum_creatinine_mg_dl: float,
    ) -> float:
        """Calculate eGFR without race modifier in mL/min/1.73m^2."""
        if serum_creatinine_mg_dl <= 0.0:
            raise InvalidRenalParameterError(
                f"Serum creatinine must be strictly positive, got {serum_creatinine_mg_dl}"
            )
        if age <= 0:
            raise InvalidRenalParameterError(
                f"Patient age must be strictly positive, got {age}"
            )
        if age < 18:
            raise InvalidRenalParameterError(
                f"CKD-EPI 2021 equation requires strictly positive adult age >= 18, got {age}"
            )

        scr = float(serum_creatinine_mg_dl)
        kappa = 0.7 if is_female else 0.9
        alpha = -0.241 if is_female else -0.302
        female_factor = 1.012 if is_female else 1.0

        scr_over_kappa = scr / kappa
        min_factor = min(scr_over_kappa, 1.0) ** alpha
        max_factor = max(scr_over_kappa, 1.0) ** (-1.200)
        age_factor = 0.9938 ** float(age)

        egfr = 142.0 * min_factor * max_factor * age_factor * female_factor
        return round(egfr, 2)
