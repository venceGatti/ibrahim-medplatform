"""Pharmacology Evaluation Service Handler for SDUI Routes."""
from typing import Dict, Any, List, Optional, Union
from fastapi import Request
from ..base.pharmacology_models import (
    PrescribedDrugItem,
    SeverityLevel,
    PharmaEvaluationRequest,
)
from ..base.sdui_models import DrugSafetyBlock
from ..implementations.cyp450_engine import CYP450Engine
from ..implementations.qtc_calculator import QTcCalculator
from ..implementations.triple_whammy import TripleWhammyDetector
from ..implementations.ckd_epi import CKDEPI2021Calculator
from ..implementations.cpic_engine import CPICPharmacogenomicsEngine


def execute_pharma_evaluation(
    request: Request,
    evaluation_payload: Union[PharmaEvaluationRequest, List[PrescribedDrugItem], Dict[str, Any]],
    patient_id: Optional[str] = None,
    age: Optional[int] = None,
    is_female: Optional[bool] = None,
    serum_creatinine_mg_dl: Optional[float] = None,
    serum_potassium_meq_l: Optional[float] = None,
) -> DrugSafetyBlock:
    """Comprehensive pharmacology safety scan returning canonical SDUI Block 3."""
    req_dict = (
        evaluation_payload.model_dump()
        if hasattr(evaluation_payload, "model_dump")
        else ({"prescribed_drugs": evaluation_payload} if isinstance(evaluation_payload, list) else dict(evaluation_payload))
    )
    effective_age = age if age is not None else int(req_dict.get("age", 50))
    effective_is_female = is_female if is_female is not None else bool(req_dict.get("is_female", False))
    effective_serum_creatinine = (
        serum_creatinine_mg_dl if serum_creatinine_mg_dl is not None else float(req_dict.get("serum_creatinine_mg_dl", 1.0))
    )
    effective_serum_potassium = (
        serum_potassium_meq_l if serum_potassium_meq_l is not None else float(req_dict.get("serum_potassium_meq_l", 4.2))
    )
    effective_genotypes = req_dict.get("patient_genotypes") or {}

    raw_items = req_dict.get("prescribed_drugs")
    if raw_items:
        prescribed_drugs_dict = [d.model_dump() if hasattr(d, "model_dump") else dict(d) for d in raw_items]
    elif req_dict.get("prescribed_atc_codes"):
        prescribed_drugs_dict = [
            {"atc_code": code, "inn_name": code, "single_dose_mg": 100.0, "daily_dose_mg": 100.0}
            for code in req_dict["prescribed_atc_codes"]
        ]
    else:
        prescribed_drugs_dict = []

    # 1. CKD-EPI eGFR
    renal_calculator = CKDEPI2021Calculator()
    calculated_egfr = renal_calculator.compute_egfr(
        age=effective_age,
        is_female=effective_is_female,
        serum_creatinine_mg_dl=effective_serum_creatinine,
    )

    # 2. CYP450 multi-way clearance & prodrug bioactivation
    cyp_engine = getattr(request.app.state, "cyp_engine", None) if request and hasattr(request, "app") else None
    if not cyp_engine:
        pool = getattr(request.app.state, "db_pool", None) if request and hasattr(request, "app") else None
        cyp_engine = CYP450Engine(db_pool=pool)
    cyp_clearance_summary = cyp_engine.evaluate_clearance(prescribed_drugs_dict)

    # 3. QTc cardiac prolongation risk
    qtc_calculator = QTcCalculator()
    qtc_evaluation_summary = qtc_calculator.evaluate_qtc(
        prescribed_drugs=prescribed_drugs_dict,
        auc_ratios=cyp_clearance_summary["auc_ratios"],
        serum_potassium_meq_l=effective_serum_potassium,
    )

    # 4. Triple Whammy acute kidney injury detector
    triple_whammy_detector = TripleWhammyDetector()
    triple_whammy_report = triple_whammy_detector.detect_triple_whammy(
        prescribed_drugs=prescribed_drugs_dict,
        egfr=calculated_egfr,
    )

    # 5. CPIC Level 1A pharmacogenomics
    cpic_engine = CPICPharmacogenomicsEngine()
    pgx_alerts = cpic_engine.evaluate_genetics(
        prescribed_drugs=prescribed_drugs_dict,
        patient_genotypes=effective_genotypes,
    )

    # Compile structured UI alerts and enriched interactions with frontend parity
    compiled_alerts: List[Dict[str, Any]] = []
    enriched_interactions: List[Dict[str, Any]] = []
    for detected_interaction in cyp_clearance_summary["detected_interactions"]:
        single_inter = dict(detected_interaction)
        source_atc = single_inter.get("source_atc", "")
        target_atc = single_inter.get("target_atc", "")
        severity_val = single_inter.get("severity", SeverityLevel.LEVEL_1)
        severity_num = int(severity_val) if hasattr(severity_val, "value") else int(severity_val)
        mechanism_text = single_inter.get("mechanism", "")

        single_inter["drug_a"] = source_atc
        single_inter["drug_b"] = target_atc
        single_inter["level"] = severity_num
        single_inter["is_prodrug_bioactivation_block"] = (
            "prodrug" in mechanism_text.lower() or "bioactivation" in mechanism_text.lower()
        )
        enriched_interactions.append(single_inter)

        compiled_alerts.append({
            "alert_type": "DRUG_INTERACTION",
            "code": "DRUG_INTERACTION",
            "severity": severity_num,
            "title": f"Interaction: {source_atc} + {target_atc}",
            "description": mechanism_text,
            "message": f"Interaction: {source_atc} + {target_atc}: {mechanism_text}",
            "guideline": single_inter.get("management_guideline", ""),
        })

    if triple_whammy_report["triple_whammy_detected"]:
        compiled_alerts.append({
            "alert_type": "TRIPLE_WHAMMY",
            "code": "TRIPLE_WHAMMY",
            "severity": int(triple_whammy_report["severity_level"]),
            "title": "Triple Whammy Nephrotoxicity Alert",
            "description": triple_whammy_report["clinical_warning"],
            "message": triple_whammy_report["clinical_warning"],
            "guideline": "Discontinue NSAID and recalculate renal dosage.",
        })

    if qtc_evaluation_summary["qtc_prolongation_score"] >= 6.0:
        compiled_alerts.append({
            "alert_type": "QTC_PROLONGATION",
            "code": "QTC_PROLONGATION",
            "severity": int(SeverityLevel.LEVEL_1),
            "title": "Severe QTc Prolongation Risk (Torsades de Pointes)",
            "description": f"Cumulative QTc score {qtc_evaluation_summary['qtc_prolongation_score']:.1f} exceeds safety threshold 6.0.",
            "message": f"Cumulative QTc score {qtc_evaluation_summary['qtc_prolongation_score']:.1f} exceeds safety threshold 6.0.",
            "guideline": "Continuous ECG telemetry monitoring required.",
        })

    for pharmacogenomic_alert in pgx_alerts:
        sev = int(SeverityLevel.LEVEL_1 if pharmacogenomic_alert.get("is_absolute_contraindication") else SeverityLevel.LEVEL_2)
        compiled_alerts.append({
            "alert_type": "PHARMACOGENOMICS",
            "code": "PHARMACOGENOMICS",
            "severity": sev,
            "title": f"CPIC Alert: {pharmacogenomic_alert.get('gene_symbol')}",
            "description": pharmacogenomic_alert.get("recommendation", ""),
            "message": pharmacogenomic_alert.get("recommendation", ""),
            "guideline": "Select alternative agent as per CPIC guidelines.",
        })

    cyp_clearance_map: Dict[str, Any] = {
        isoform_name: float(state_descriptor["computed_clearance"])
        for isoform_name, state_descriptor in cyp_clearance_summary["cyp_profile_states"].items()
    }

    return DrugSafetyBlock(
        block_type="DrugSafetyBlock",
        component_type="DrugSafetyBlock",
        interactions=enriched_interactions,
        cyp_clearance=cyp_clearance_map,
        alerts=compiled_alerts,
        egfr=round(calculated_egfr, 2),
        qtc_tisdale_score=round(float(qtc_evaluation_summary["qtc_prolongation_score"]), 2),
        triple_whammy_detected=bool(triple_whammy_report["triple_whammy_detected"]),
    )
