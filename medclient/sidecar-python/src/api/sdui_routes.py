"""SDUI and Core Clinical Evaluation Routes (ROA-02, ROA-16, ROA-17, ROA-21, ROA-23)."""
import os
import sys
import time
from typing import Dict, Any, List, Optional, Union
from fastapi import APIRouter, HTTPException, Request, Header, Depends, status, Body, Query
from pydantic import BaseModel, ConfigDict
from ..base.diagnostic_models import (
    SymptomMatcherInput,
    SymptomMatcherOutput,
    DifferentialCandidate,
    NextBestQuestion,
)
from ..base.pharmacology_models import (
    PrescribedDrugItem,
    SeverityLevel,
    PharmaEvaluationRequest,
)
from ..base.sdui_models import (
    ClinicalSheetBlock,
    DrugSafetyBlock,
    ExamSimulatorBlock,
    HybridSearchRequest,
    SearchMatchEntry,
    HybridSearchResponse,
    ExamEvaluationRequest,
)
from ..base.educational_models import (
    FSRSReviewInput,
    FSRSReviewOutput,
)
from ..implementations.red_flags import RedFlagsInterceptor
from ..implementations.cyp450_engine import CYP450Engine
from ..implementations.qtc_calculator import QTcCalculator
from ..implementations.triple_whammy import TripleWhammyDetector
from ..implementations.ckd_epi import CKDEPI2021Calculator
from ..implementations.cpic_engine import CPICPharmacogenomicsEngine
from ..implementations.fsrs_scheduler import FSRSScheduler
from ..implementations.hotspot_evaluator import HotspotEvaluator
from ..implementations.softmax_normalizer import LogSumExpNormalizer
from ..implementations.active_discriminator import ActiveDiscriminator
import hmac


def verify_tauri_ipc_secret(request: Request, x_tauri_ipc_secret: Optional[str] = Header(None)) -> None:
    """Fail-closed verification of ephemeral IPC secret token passed via request header (ROA-23)."""
    if request.method == "OPTIONS":
        return
    expected_token = getattr(request.app.state, "ipc_token", None) or os.environ.get("MEDCLIENT_IPC_TOKEN")
    if not expected_token or not x_tauri_ipc_secret or not hmac.compare_digest(str(x_tauri_ipc_secret).encode("utf-8"), str(expected_token).encode("utf-8")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing X-Tauri-IPC-Secret header token",
        )


router = APIRouter(
    prefix="/api/v3",
    tags=["Clinical Engines & SDUI"],
    dependencies=[Depends(verify_tauri_ipc_secret)],
)


@router.get("/sheets/{sheet_id}", response_model=ClinicalSheetBlock)
def get_clinical_sheet(sheet_id: str, request: Request) -> ClinicalSheetBlock:
    """Fetch clinical sheet monograph formatted as canonical SDUI Block 1."""
    pool = getattr(request.app.state, "db_pool", None)
    if pool:
        try:
            with pool.acquire() as sqlite_connection:
                query_cursor = sqlite_connection.cursor()
                query_cursor.execute(
                    "SELECT sheet_id, title, content_markdown FROM clinical_sheets WHERE sheet_id = ?",
                    (sheet_id,),
                )
                sheet_record = query_cursor.fetchone()
                if sheet_record:
                    found_sheet_id, title_text, markdown_body = sheet_record
                    return ClinicalSheetBlock(
                        sheet_id=found_sheet_id,
                        title=title_text,
                        content_markdown=markdown_body,
                        callouts=[],
                    )
        except Exception as sheet_query_error:
            sys.stderr.write(f"[SDUIRoutes] Error retrieving sheet '{sheet_id}': {sheet_query_error}\n")

    return ClinicalSheetBlock(
        sheet_id=sheet_id,
        title=f"Clinical Monograph: {sheet_id}",
        content_markdown=f"# {sheet_id}\n\nClinical documentation monograph.",
        callouts=[],
    )


@router.post("/search/hybrid", response_model=HybridSearchResponse)
def hybrid_search(search_request: HybridSearchRequest, request: Request) -> HybridSearchResponse:
    """Perform hybrid lexical and approximate spelling search across clinical knowledge."""
    query_string = search_request.query_text.strip()
    inverted_dict = getattr(request.app.state, "inverted_dict", None)

    matched_results: List[SearchMatchEntry] = []
    if inverted_dict and query_string:
        postings = inverted_dict.lookup_phrase(query_string)
        for matched_concept_id, relevance_score in postings[:search_request.limit]:
            matched_results.append(
                SearchMatchEntry(
                    concept_id=matched_concept_id,
                    title=matched_concept_id.replace("_", " ").title(),
                    match_score=round(float(relevance_score), 3),
                    source="lexical_inverted_index",
                )
            )

    if not matched_results and query_string:
        matched_results.append(
            SearchMatchEntry(
                concept_id=query_string.lower().replace(" ", "_"),
                title=query_string.title(),
                match_score=1.0,
                source="exact_query",
            )
        )

    return HybridSearchResponse(
        query=query_string,
        matches=matched_results[:search_request.limit],
    )


@router.post("/exam/evaluate", response_model=ExamSimulatorBlock)
def evaluate_exam_item(evaluation_request: ExamEvaluationRequest, request: Request) -> ExamSimulatorBlock:
    """Evaluate candidate exam interaction and format response as SDUI Block 4."""
    evaluation_type = evaluation_request.item_type
    interactive_item_payload = dict(evaluation_request.item_data)
    user_choice = evaluation_request.user_selection

    is_correct = False
    feedback_message = ""

    if evaluation_type in ("MCQ", "MCQ_4", "MCQ_5"):
        correct_answer = interactive_item_payload.get("correct_index", interactive_item_payload.get("correct_answer"))
        is_correct = (user_choice == correct_answer)
        feedback_message = "Correct answer selected." if is_correct else "Incorrect answer selected."
    elif evaluation_type == "IMAGE_HOTSPOT":
        evaluator = HotspotEvaluator()
        polygons = interactive_item_payload.get("target_polygons", [])
        if isinstance(user_choice, dict) and "u" in user_choice and "v" in user_choice:
            click_u = float(user_choice["u"])
            click_v = float(user_choice["v"])
        elif isinstance(user_choice, (list, tuple)) and len(user_choice) >= 2:
            click_u = float(user_choice[0])
            click_v = float(user_choice[1])
        else:
            click_u = 0.0
            click_v = 0.0

        is_correct = any(evaluator.evaluate_hit(click_u, click_v, poly) for poly in polygons)
        feedback_message = "Target anatomical region verified." if is_correct else "Clicked outside target region."
    elif evaluation_type == "DAG_SCENARIO":
        valid_transitions = interactive_item_payload.get("allowed_transitions", {})
        is_correct = (str(user_choice) in valid_transitions)
        feedback_message = "Action validated." if is_correct else "Contraindicated clinical step."

    interactive_item_payload["evaluation_outcome"] = {
        "is_correct": is_correct,
        "feedback": feedback_message,
    }

    updated_fsrs = evaluation_request.fsrs_card_state
    if updated_fsrs and ("stability" in updated_fsrs or "concept_uid" in updated_fsrs):
        scheduler = getattr(request.app.state, "fsrs_scheduler", None) or FSRSScheduler()
        rating = 3 if is_correct else 1
        review_step = scheduler.review_card(
            card_state=dict(updated_fsrs),
            rating=rating,
        )
        updated_fsrs = dict(review_step)

    return ExamSimulatorBlock(
        block_type="ExamSimulatorBlock",
        component_type="ExamSimulatorBlock",
        item_type=evaluation_type,
        item_data=interactive_item_payload,
        fsrs_card_state=updated_fsrs,
    )


@router.post("/fsrs/schedule", response_model=FSRSReviewOutput)
def schedule_fsrs_review(review_input: FSRSReviewInput, request: Request) -> FSRSReviewOutput:
    """Schedule next review using deterministic FSRS scheduler (ROA-17)."""
    scheduler = getattr(request.app.state, "fsrs_scheduler", None) or FSRSScheduler()
    user_state = getattr(request.app.state, "user_state_store", None)
    initial_card_state = {"concept_uid": review_input.concept_uid}
    if user_state:
        existing = user_state.get_card(review_input.concept_uid)
        if existing:
            initial_card_state = existing

    review_dict = scheduler.review_card(
        card_state=initial_card_state,
        rating=int(review_input.rating),
        review_time=review_input.review_time,
        desired_retention=review_input.desired_retention,
        target_exam_date=review_input.target_exam_date,
    )
    review_output = FSRSReviewOutput(**review_dict)

    if user_state:
        try:
            user_state.upsert_card(review_output.model_dump())
        except Exception as state_persist_error:
            sys.stderr.write(f"[SDUIRoutes] Failed to persist card state: {state_persist_error}\n")

    return review_output


@router.post("/engine/evaluate", response_model=SymptomMatcherOutput)
def evaluate_symptom_matcher(symptom_matcher_request: SymptomMatcherInput, request: Request) -> SymptomMatcherOutput:
    """Evaluate vitals with RedFlagsInterceptor and compute differential candidates."""
    start_time = time.perf_counter()
    interceptor = getattr(request.app.state, "red_flags_interceptor", None) or RedFlagsInterceptor()
    red_flags_dict = interceptor.evaluate(symptom_matcher_request.vitals.model_dump())

    positive_findings = [f.hpo_id for f in symptom_matcher_request.findings if f.state == "PRESENT"]
    negative_findings = [f.hpo_id for f in symptom_matcher_request.findings if f.state == "ABSENT"]

    ranker = getattr(request.app.state, "csr_ranker", None)
    candidates: List[DifferentialCandidate] = []
    nbq_result: Optional[NextBestQuestion] = None

    if ranker:
        pathognomonic_flags = {f.hpo_id: f.is_pathognomonic for f in symptom_matcher_request.findings}
        scored_diseases = ranker.score_diseases(positive_findings, negative_findings, {}, pathognomonic_flags)
        top_slice = scored_diseases[:5]
        if top_slice:
            normalizer = LogSumExpNormalizer()
            logits = [candidate_item[1] for candidate_item in top_slice]
            posterior_probabilities = normalizer.normalize_logits(logits)

            for idx, (icd_code, log_odds, support_symptoms, rule_out_penalties) in enumerate(top_slice):
                candidates.append(
                    DifferentialCandidate(
                        icd10_code=icd_code,
                        disease_name=ranker.disease_names.get(icd_code, icd_code),
                        posterior_probability=round(float(posterior_probabilities[idx]), 4),
                        raw_log_odds=round(log_odds, 3),
                        supporting_symptoms=support_symptoms,
                        rule_out_penalties=rule_out_penalties,
                    )
                )

            if len(candidates) >= 2:
                investigated_findings = set(positive_findings) | set(negative_findings)
                uninvestigated_features = [
                    feature_code for feature_code in ranker.idx_to_feature.values()
                    if feature_code not in investigated_findings
                ]
                if uninvestigated_features:
                    active_discriminator = ActiveDiscriminator()
                    selected_nbq = active_discriminator.select_next_best_question(
                        candidate_a=candidates[0].disease_name,
                        prob_a=candidates[0].posterior_probability,
                        candidate_b=candidates[1].disease_name,
                        prob_b=candidates[1].posterior_probability,
                        uninvestigated_features=uninvestigated_features[:50],
                        feature_costs={f: 1.0 for f in uninvestigated_features[:50]},
                    )
                    if selected_nbq:
                        nbq_result = NextBestQuestion(**selected_nbq)

    execution_time_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
    return SymptomMatcherOutput(
        session_id=symptom_matcher_request.session_id,
        execution_time_ms=execution_time_ms,
        red_flags=red_flags_dict,
        differential_diagnosis=candidates,
        nbq=nbq_result,
    )


@router.post("/pharma/evaluate", response_model=DrugSafetyBlock)
def evaluate_pharmacology_safety(
    request: Request,
    evaluation_payload: Union[PharmaEvaluationRequest, List[PrescribedDrugItem], Dict[str, Any]] = Body(...),
    patient_id: Optional[str] = Query(None),
    age: Optional[int] = Query(None),
    is_female: Optional[bool] = Query(None),
    serum_creatinine_mg_dl: Optional[float] = Query(None),
    serum_potassium_meq_l: Optional[float] = Query(None),
) -> DrugSafetyBlock:
    """Comprehensive pharmacology safety scan returning canonical SDUI Block 3."""
    req_dict = (
        evaluation_payload.model_dump()
        if hasattr(evaluation_payload, "model_dump")
        else ({"prescribed_drugs": evaluation_payload} if isinstance(evaluation_payload, list) else dict(evaluation_payload))
    )
    effective_patient_id = patient_id or str(req_dict.get("patient_id", "PATIENT_LOCAL_01"))
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

    # Calculate DDD substitution for recommended alternatives
    from ..base.pharmacology_models import TherapeuticAlternative
    recommended_alternatives_models = []
    # Mocking standard DDD dictionary since we don't have the full DB table here
    ddd_mock_catalog = {
        "C09AA02": 10.0, # Enalapril
        "C09AA05": 5.0,  # Ramipril
        "C09CA01": 50.0, # Losartan
    }
    for interaction in enriched_interactions:
        if interaction.get("level") == SeverityLevel.LEVEL_1:
            source_atc = interaction.get("drug_a")
            # Example DDD normalization logic for alternative recommendation
            if source_atc == "C09AA02":
                orig_dose = 20.0
                for d in prescribed_drugs_dict:
                    if d.get("atc_code") == source_atc:
                        orig_dose = d.get("daily_dose_mg", 20.0)
                alt_atc = "C09AA05" # Ramipril
                orig_ddd = ddd_mock_catalog.get(source_atc, 1.0)
                alt_ddd = ddd_mock_catalog.get(alt_atc, 1.0)
                substitute_dose = orig_dose * (alt_ddd / orig_ddd)

                recommended_alternatives_models.append(
                    TherapeuticAlternative(
                        original_atc=source_atc,
                        suggested_atc=alt_atc,
                        suggested_inn_name="Ramipril",
                        hierarchy_distance=1,
                        cost_index=1.0,
                        clinical_rationale="Alternative within same ATC subclass with safe profile.",
                        original_dose_mg=orig_dose,
                        calculated_substitute_dose=substitute_dose
                    )
                )

    return DrugSafetyBlock(
        block_type="DrugSafetyBlock",
        component_type="DrugSafetyBlock",
        interactions=enriched_interactions,
        cyp_clearance=cyp_clearance_map,
        alerts=compiled_alerts,
        egfr=round(calculated_egfr, 2),
        qtc_tisdale_score=round(float(qtc_evaluation_summary["qtc_prolongation_score"]), 2),
        triple_whammy_detected=bool(triple_whammy_report["triple_whammy_detected"]),
        recommended_alternatives=recommended_alternatives_models
    )
