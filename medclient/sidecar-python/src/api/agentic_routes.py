"""Agentic API Endpoints: /agent/health, /agent/state, /agent/execute, /agent/schema."""
import os
import sys
import time
from typing import Dict, Any, Optional
from fastapi import APIRouter, Header, HTTPException, status, Request
from ..base.agentic_models import (
    AgentHealthResponse,
    AgentStateResponse,
    AgentExecuteRequest,
    AgentExecuteResponse,
)


router = APIRouter(prefix="/agent", tags=["Agentic API"])
START_TIME = time.time()


def get_process_rss_mb() -> float:
    """Measure resident set size of current Python sidecar process in megabytes using psutil."""
    try:
        import psutil
        process_resident_memory_bytes = psutil.Process().memory_info().rss
        return round(float(process_resident_memory_bytes) / (1024.0 * 1024.0), 2)
    except Exception as memory_query_error:
        sys.stderr.write(f"[AgenticRoutes] Failed to query resident set size via psutil: {memory_query_error}\n")
        try:
            if sys.platform == "win32":
                import ctypes
                from ctypes import wintypes

                class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
                    _fields_ = [
                        ("cb", wintypes.DWORD),
                        ("PageFaultCount", wintypes.DWORD),
                        ("PeakWorkingSetSize", ctypes.c_size_t),
                        ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t),
                        ("PeakPagefileUsage", ctypes.c_size_t),
                    ]

                psapi = ctypes.WinDLL("psapi")
                kernel32 = ctypes.WinDLL("kernel32")
                process_handle = kernel32.GetCurrentProcess()
                counters = PROCESS_MEMORY_COUNTERS()
                counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
                if psapi.GetProcessMemoryInfo(process_handle, ctypes.byref(counters), counters.cb):
                    return round(counters.WorkingSetSize / (1024.0 * 1024.0), 2)
        except Exception as win32_query_error:
            sys.stderr.write(f"[AgenticRoutes] Win32 fallback failed: {win32_query_error}\n")
        raise RuntimeError("Unable to query process memory footprint")


import hmac


def verify_ipc_token(request: Request, x_tauri_ipc_secret: Optional[str] = Header(None)) -> None:
    """Verify ephemeral IPC secret passed via header strictly and unconditionally (ROA-23)."""
    expected_token = getattr(request.app.state, "ipc_token", None) or os.environ.get("MEDCLIENT_IPC_TOKEN")
    if not expected_token or not x_tauri_ipc_secret or not hmac.compare_digest(str(x_tauri_ipc_secret).encode("utf-8"), str(expected_token).encode("utf-8")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing X-Tauri-IPC-Secret token",
        )


@router.get("/health", response_model=AgentHealthResponse)
def get_agent_health(request: Request, x_tauri_ipc_secret: Optional[str] = Header(None)) -> AgentHealthResponse:
    """Returns liveness, memory footprint RSS, and active database."""
    verify_ipc_token(request, x_tauri_ipc_secret)
    rss_mb = get_process_rss_mb()
    active_slot = getattr(request.app.state, "active_slot", "blue")

    return AgentHealthResponse(
        status="healthy",
        rss_mb=rss_mb,
        db_active=active_slot,
        uptime_seconds=round(time.time() - START_TIME, 2),
    )


@router.get("/state", response_model=AgentStateResponse)
def get_agent_state(request: Request, x_tauri_ipc_secret: Optional[str] = Header(None)) -> AgentStateResponse:
    """Returns full serialized application state."""
    verify_ipc_token(request, x_tauri_ipc_secret)
    pool = getattr(request.app.state, "db_pool", None)
    pool_stats = pool.get_stats() if pool else {}

    return AgentStateResponse(
        active_slot=getattr(request.app.state, "active_slot", "blue"),
        active_db_path=getattr(request.app.state, "active_db_path", ""),
        pool_stats=pool_stats,
        session_count=getattr(request.app.state, "session_count", 0),
        system_alert_level=getattr(request.app.state, "alert_level", "NOMINAL"),
    )


@router.post("/execute", response_model=AgentExecuteResponse)
def execute_agent_action(
    action: AgentExecuteRequest,
    request: Request,
    x_tauri_ipc_secret: Optional[str] = Header(None),
) -> AgentExecuteResponse:
    """Action dispatcher executing typed AI/system operations."""
    verify_ipc_token(request, x_tauri_ipc_secret)

    action_type = action.action_type.upper()
    action_parameter_map = action.action_parameters

    try:
        if action_type in ["EVALUATE_NLI",
            "EVALUATE_RED_FLAGS", "EVALUATE_VITALS"]:
            interceptor = getattr(request.app.state, "red_flags_interceptor", None)
            if not interceptor:
                from ..implementations.red_flags import RedFlagsInterceptor
                interceptor = RedFlagsInterceptor()
            red_flags_outcome = interceptor.evaluate(action_parameter_map)
            return AgentExecuteResponse(success=True, action_type=action_type, execution_outcome=red_flags_outcome)

        elif action_type == "EVALUATE_NLI":
            from ..implementations.nli_cross_encoder import NLICrossEncoderEvaluator
            evaluator = getattr(request.app.state, "nli_evaluator", None)
            if not evaluator:
                evaluator = NLICrossEncoderEvaluator()

            premise = action_parameter_map.get("premise", "")
            hypothesis = action_parameter_map.get("hypothesis", "")

            atomic_concepts = [{
                "id": "open_response",
                "hypothesis": premise,
                "weight": 1.0,
                "is_critical": True
            }]

            evaluation_result = evaluator.evaluate_response(student_text=hypothesis, atomic_concepts=atomic_concepts)
            is_correct = evaluation_result.get("passed", False)

            return AgentExecuteResponse(
                success=True,
                action_type=action_type,
                execution_outcome={
                    "is_correct": is_correct,
                    "feedback": "NLI Evaluation Completed",
                    "nli_details": evaluation_result
                }
            )

        elif action_type == "CALCULATE_EGFR":
            from ..implementations.ckd_epi import CKDEPI2021Calculator
            calc = CKDEPI2021Calculator()
            calculated_egfr = calc.compute_egfr(
                age=action_parameter_map["age"],
                is_female=action_parameter_map["is_female"],
                serum_creatinine_mg_dl=action_parameter_map["serum_creatinine_mg_dl"],
            )
            return AgentExecuteResponse(success=True, action_type=action_type, execution_outcome={"egfr": calculated_egfr})

        elif action_type == "EVALUATE_QTC":
            from ..implementations.qtc_calculator import QTcCalculator
            calc = QTcCalculator()

            qtc_calculation_outcome = calc.evaluate_qtc(
            qtc_calc = QTcCalculator()
            qtc_calculation_outcome = qtc_calc.evaluate_qtc(
                prescribed_drugs=action_parameter_map.get("prescribed_drugs", []),
                auc_ratios=action_parameter_map.get("auc_ratios", {}),
                serum_potassium_meq_l=action_parameter_map.get("serum_potassium_meq_l", 4.0),
            )
            return AgentExecuteResponse(success=True, action_type=action_type, execution_outcome=qtc_calculation_outcome)

        elif action_type == "DETECT_TRIPLE_WHAMMY":
            from ..implementations.triple_whammy import TripleWhammyDetector
            detector = TripleWhammyDetector()
            triple_whammy_outcome = detector.detect_triple_whammy(
                prescribed_drugs=action_parameter_map.get("prescribed_drugs", []),
                egfr=action_parameter_map.get("egfr", 90.0),
            )
            return AgentExecuteResponse(success=True, action_type=action_type, execution_outcome=triple_whammy_outcome)

        elif action_type == "EVALUATE_CYP450":
            from ..implementations.cyp450_engine import CYP450Engine
            cyp_engine = getattr(request.app.state, "cyp_engine", None)
            if not cyp_engine:
                cyp_engine = CYP450Engine(db_pool=getattr(request.app.state, "db_pool", None))
            cyp_clearance_outcome = cyp_engine.evaluate_clearance(prescribed_drugs=action_parameter_map.get("prescribed_drugs", []))
            return AgentExecuteResponse(success=True, action_type=action_type, execution_outcome=cyp_clearance_outcome)

        elif action_type == "EVALUATE_CPIC":
            from ..implementations.cpic_engine import CPICPharmacogenomicsEngine
            engine = CPICPharmacogenomicsEngine()
            genetic_matches = engine.evaluate_genetics(
                prescribed_drugs=action_parameter_map.get("prescribed_drugs", []),
                patient_genotypes=action_parameter_map.get("patient_genotypes", {}),
            )
            return AgentExecuteResponse(success=True, action_type=action_type, execution_outcome={"matches": genetic_matches})

        elif action_type == "SPELLCHECK":
            from ..implementations.symspell_checker import MedicalSymSpellChecker
            checker = getattr(request.app.state, "spellchecker", None) or MedicalSymSpellChecker()
            suggestions = checker.lookup(action_parameter_map.get("word", ""), max_edit_distance=action_parameter_map.get("max_distance", 2))
            return AgentExecuteResponse(success=True, action_type=action_type, execution_outcome={"suggestions": suggestions})

        elif action_type == "RESOLVE_COLLOQUIAL":
            from ..implementations.inverted_dictionary import InvertedLexicalDictionary
            inv_dict = getattr(request.app.state, "inverted_dict", None) or InvertedLexicalDictionary()
            resolved_term = inv_dict.resolve_colloquial(action_parameter_map.get("phrase", ""))
            return AgentExecuteResponse(success=True, action_type=action_type, execution_outcome={"resolved": resolved_term})

        elif action_type == "SHUTDOWN_SERVER":
            import threading
            threading.Timer(0.3, lambda: os._exit(0)).start()
            return AgentExecuteResponse(success=True, action_type=action_type, execution_outcome={"status": "SHUTTING_DOWN"})

        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unknown action_type: {action.action_type}",
            )
    except Exception as err:
        return AgentExecuteResponse(
            success=False,
            action_type=action_type,
            execution_outcome={"error_detail": str(err)},
            error_message=str(err),
        )


@router.get("/schema")
def get_agent_schema(request: Request, x_tauri_ipc_secret: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Returns OpenAPI / JSON Schema definition of all agentic endpoints and executable actions."""
    verify_ipc_token(request, x_tauri_ipc_secret)
    return {
        "version": "1.0.0",
        "supported_actions": [
            "EVALUATE_NLI",
            "EVALUATE_RED_FLAGS",
            "EVALUATE_VITALS",
            "CALCULATE_EGFR",
            "EVALUATE_QTC",
            "DETECT_TRIPLE_WHAMMY",
            "EVALUATE_CYP450",
            "EVALUATE_CPIC",
            "SPELLCHECK",
            "RESOLVE_COLLOQUIAL",
            "SHUTDOWN_SERVER",
        ],
        "openapi": request.app.openapi(),
    }

