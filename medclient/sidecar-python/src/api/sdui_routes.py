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

    from .pharmacology_controller import handle_pharmacology_evaluation
    return handle_pharmacology_evaluation(
        request=request,
        req_dict=req_dict,
        effective_age=effective_age,
        effective_is_female=effective_is_female,
        effective_serum_creatinine=effective_serum_creatinine,
        effective_serum_potassium=effective_serum_potassium,
        prescribed_drugs_dict=prescribed_drugs_dict,
        effective_genotypes=effective_genotypes,
    )
