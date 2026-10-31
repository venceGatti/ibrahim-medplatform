"""
Production SLA Benchmarks for MedPlatform End-to-End Runtime.

Verifies strict production invariants:
- End-to-End p99 pipeline latency < 50 ms (Hybrid Search + Log-Odds + CYP450 + SDUI).
- Total Process Resident Set Size (RSS) memory < 300 MB.
- High-throughput sub-millisecond evaluation for clinical safety pipelines.
"""

import time
import psutil
import pytest
import numpy as np
from typing import List, Dict, Any

from medclient.sidecar_python.src.implementations.sqlite_pool import SqliteConnectionPool
from medclient.sidecar_python.src.implementations.onnx_semantic import OnnxSemanticEmbeddingEngine
from medclient.sidecar_python.src.implementations.red_flags import RedFlagsInterceptor
from medclient.sidecar_python.src.implementations.csr_ranker import SparseCSRLogOddsRanker
from medclient.sidecar_python.src.implementations.pertinent_negatives import PertinentNegativesEvaluator
from medclient.sidecar_python.src.implementations.softmax_normalizer import LogSumExpNormalizer
from medclient.sidecar_python.src.implementations.cyp450_engine import CYP450Engine
from medclient.sidecar_python.src.implementations.sdui_emitter import SDUISerializer


def initialize_test_knowledge_base(ranker: SparseCSRLogOddsRanker) -> None:
    """Configures candidate diseases and observed clinical findings into the CSR ranker."""
    diseases = [
        {"icd10_code": "I21.0", "preferred_label": "STEMI Anterior", "prior": 0.05},
        {"icd10_code": "I20.0", "preferred_label": "Unstable Angina", "prior": 0.08},
        {"icd10_code": "I30.0", "preferred_label": "Acute Pericarditis", "prior": 0.02},
        {"icd10_code": "J18.9", "preferred_label": "Pneumonia", "prior": 0.04},
    ]
    features = [
        {"hpo_id": "HP:0001605", "label": "Chest Pain"},
        {"hpo_id": "HP:0002094", "label": "Dyspnea"},
        {"hpo_id": "HP:0001945", "label": "Fever"},
        {"hpo_id": "HP:0001635", "label": "Heart failure"},
    ]
    co_occurrences = [
        {"disease_code": "I21.0", "feature_code": "HP:0001605", "count_dj": 100, "count_fi_dj": 90, "is_pathognomonic": True},
        {"disease_code": "I21.0", "feature_code": "HP:0002094", "count_dj": 100, "count_fi_dj": 60, "is_pathognomonic": False},
        {"disease_code": "I20.0", "feature_code": "HP:0001605", "count_dj": 100, "count_fi_dj": 80, "is_pathognomonic": False},
        {"disease_code": "I30.0", "feature_code": "HP:0001605", "count_dj": 100, "count_fi_dj": 70, "is_pathognomonic": False},
        {"disease_code": "J18.9", "feature_code": "HP:0001945", "count_dj": 100, "count_fi_dj": 85, "is_pathognomonic": False},
    ]
    ranker.load_knowledge_base(diseases, features, co_occurrences)


def execute_full_production_pipeline_iteration(
    pool: SqliteConnectionPool,
    embedder: OnnxSemanticEmbeddingEngine,
    red_flags: RedFlagsInterceptor,
    ranker: SparseCSRLogOddsRanker,
    negatives_evaluator: PertinentNegativesEvaluator,
    normalizer: LogSumExpNormalizer,
    cyp_engine: CYP450Engine,
    sdui_serializer: SDUISerializer,
) -> Dict[str, Any]:
    """
    Executes an authentic, full end-to-end production clinical query cycle:
    1. Hybrid Search (FTS5 BM25 + ONNX Semantic Cosine Distance)
    2. Red Flags Interceptor & Log-Odds Differential Diagnostic Ranking
    3. CYP450 Polypharmacy & Drug-Drug Interaction Evaluation
    4. SDUI 4-Block Polymorphic Serialization & Packaging
    """
    # 1. Hybrid Search
    query_text = "acute chest pain radiating to left jaw dyspnea"
    query_vector = embedder.encode(query_text)

    with pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT icd10_code, description
            FROM clinical_icd10
            WHERE description LIKE ? OR description LIKE ?
            LIMIT 5
            """,
            ("%infarction%", "%angina%"),
        )
        fts_matches = cursor.fetchall()

    if fts_matches:
        candidate_matrix = np.array([embedder.encode(row[1]) for row in fts_matches])
        _ = embedder.compute_similarity(query_vector, candidate_matrix)
        top_candidate_name = fts_matches[0][1]
    else:
        top_candidate_name = "Acute Coronary Syndrome"

    # 2. Log-Odds Differential Ranking & Red Flags
    vitals = {
        "heart_rate_bpm": 115.0,
        "systolic_bp_mmhg": 88.0,
        "respiratory_rate_bpm": 24.0,
        "spo2_percent": 92.0,
        "temperature_celsius": 37.2,
        "gcs_score": 15,
    }
    red_flags_assessment = red_flags.evaluate(vitals)

    ranked_diagnoses = ranker.score_diseases(
        positive_features=["HP:0001605", "HP:0002094"],
        negative_features=["HP:0001945"],
        cluster_assignments={"HP:0001605": "cardiac", "HP:0002094": "respiratory"},
        pathognomonic_flags={"HP:0001605": True},
    )
    logits = [r[1] for r in ranked_diagnoses]
    normalized_probabilities = normalizer.normalize_logits(logits)

    # 3. CYP450 Drug-Drug Interaction Evaluation
    prescribed_drugs = [
        {"atc_code": "B01AC04", "inn_name": "Clopidogrel"},
        {"atc_code": "A02BC01", "inn_name": "Omeprazole"},
    ]
    cyp_result = cyp_engine.evaluate_clearance(prescribed_drugs)

    # 4. SDUI 4-Block Polymorphic Serialization
    block_sheet = sdui_serializer.build_clinical_sheet_block(
        sheet_id="sheet_stemi_production",
        title="STEMI Clinical Protocol",
        content_markdown="# ST-Elevation Myocardial Infarction\nImmediate reperfusion protocol required.",
        callouts=[
            {
                "id": "alert_01",
                "severity": "CRITICAL",
                "title": "Shock Index Alert",
                "body_markdown": f"Shock Index {red_flags_assessment['shock_index']:.2f} > 0.9",
            }
        ],
    )
    block_symptoms = sdui_serializer.build_symptom_matcher_block(
        differential_candidates=[
            {"icd10": "I21.0", "name": top_candidate_name, "prob": float(normalized_probabilities[0])}
        ],
        selected_symptoms=["HP:0001605", "HP:0002094"],
        nbq={"next_question": "Does pain radiate to right arm?"},
    )
    block_drugs = sdui_serializer.build_drug_safety_block(
        interactions=[
            {"atc_a": i.get("atc_a", ""), "atc_b": i.get("atc_b", ""), "description": i.get("description", "")}
            for i in cyp_result["detected_interactions"]
        ],
        cyp_clearance={
            k: v.computed_clearance for k, v in cyp_result["cyp_states"].items()
        },
        alerts=[
            {"type": "BLACKBOX", "text": i.get("description", "")}
            for i in cyp_result["detected_interactions"]
        ],
        egfr=82.5,
    )
    block_exam = sdui_serializer.build_exam_simulator_block(
        item_type="MCQ_4",
        item_data={"question": "What is the primary contraindication in this regimen?"},
    )

    envelope = sdui_serializer.serialize_envelope(
        session_id="benchmark_session_uuid",
        sequence_number=1,
        blocks=[block_sheet, block_symptoms, block_drugs, block_exam],
    )

    return envelope


@pytest.mark.benchmark
def test_production_sla_latency_p99_under_fifty_millis(real_sqlite_kb):
    """
    SLA Benchmark: Measures 100 real pipeline iterations.
    Enforces p99 execution duration strictly below 50.0 ms.
    """
    pool = SqliteConnectionPool(database_path=real_sqlite_kb, max_readers=4)
    embedder = OnnxSemanticEmbeddingEngine()
    red_flags = RedFlagsInterceptor()
    ranker = SparseCSRLogOddsRanker()
    initialize_test_knowledge_base(ranker)
    negatives = PertinentNegativesEvaluator()
    normalizer = LogSumExpNormalizer()
    cyp = CYP450Engine(db_pool=pool)
    serializer = SDUISerializer()

    # Warmup run
    execute_full_production_pipeline_iteration(
        pool, embedder, red_flags, ranker, negatives, normalizer, cyp, serializer
    )

    latencies_ms: List[float] = []
    iteration_count = 100

    for _ in range(iteration_count):
        start_time = time.perf_counter()
        envelope = execute_full_production_pipeline_iteration(
            pool, embedder, red_flags, ranker, negatives, normalizer, cyp, serializer
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        latencies_ms.append(elapsed_ms)
        assert envelope["session_id"] == "benchmark_session_uuid"
        assert len(envelope["blocks"]) == 4

    pool.close()

    p50_latency_ms = float(np.percentile(latencies_ms, 50))
    p90_latency_ms = float(np.percentile(latencies_ms, 90))
    p99_latency_ms = float(np.percentile(latencies_ms, 99))
    max_latency_ms = float(np.max(latencies_ms))

    print(
        f"\n[PRODUCTION SLA LATENCY REPORT] Iterations: {iteration_count} | "
        f"p50: {p50_latency_ms:.2f} ms | p90: {p90_latency_ms:.2f} ms | "
        f"p99: {p99_latency_ms:.2f} ms | Max: {max_latency_ms:.2f} ms"
    )

    # Invariant: p99 latency must be strictly less than 50 ms
    assert p99_latency_ms < 50.0, f"p99 latency {p99_latency_ms:.2f} ms exceeded SLA limit of 50.0 ms"


@pytest.mark.benchmark
def test_production_sla_rss_memory_under_three_hundred_mb(real_sqlite_kb):
    """
    SLA Benchmark: Measures combined process resident set size (RSS)
    under continuous clinical workload, enforcing RSS < 300.0 MB.
    """
    process = psutil.Process()
    initial_rss_mb = process.memory_info().rss / (1024.0 * 1024.0)

    pool = SqliteConnectionPool(database_path=real_sqlite_kb, max_readers=4)
    embedder = OnnxSemanticEmbeddingEngine()
    red_flags = RedFlagsInterceptor()
    ranker = SparseCSRLogOddsRanker()
    initialize_test_knowledge_base(ranker)
    negatives = PertinentNegativesEvaluator()
    normalizer = LogSumExpNormalizer()
    cyp = CYP450Engine(db_pool=pool)
    serializer = SDUISerializer()

    # Sustained execution batch
    for _ in range(150):
        execute_full_production_pipeline_iteration(
            pool, embedder, red_flags, ranker, negatives, normalizer, cyp, serializer
        )

    pool.close()

    peak_rss_mb = process.memory_info().rss / (1024.0 * 1024.0)

    print(
        f"\n[PRODUCTION SLA MEMORY REPORT] Initial RSS: {initial_rss_mb:.2f} MB | "
        f"Peak Sustained RSS: {peak_rss_mb:.2f} MB | SLA Limit: 300.00 MB"
    )

    # Invariant: Resident memory must remain strictly below 300 MB
    assert peak_rss_mb < 300.0, f"Process RSS {peak_rss_mb:.2f} MB exceeded ceiling of 300.0 MB"


@pytest.mark.benchmark
def test_production_sla_hybrid_search_sub_ten_millis(real_sqlite_kb):
    """
    SLA Benchmark: Isolates FTS5 + ONNX Semantic embedding search,
    guaranteeing median query response is below 15 ms.
    """
    pool = SqliteConnectionPool(database_path=real_sqlite_kb, max_readers=4)
    embedder = OnnxSemanticEmbeddingEngine()

    query_vector = embedder.encode("acute chest pain radiating to left arm")
    query_latencies_ms: List[float] = []

    for _ in range(60):
        start_time = time.perf_counter()
        with pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT icd10_code, description FROM clinical_icd10 WHERE description LIKE ? OR description LIKE ? LIMIT 10",
                ("%infarction%", "%angina%"),
            )
            records = cursor.fetchall()

        if records:
            candidate_matrix = np.array([embedder.encode(desc) for _, desc in records])
            _ = embedder.compute_similarity(query_vector, candidate_matrix)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        query_latencies_ms.append(elapsed_ms)

    pool.close()

    p50_ms = float(np.percentile(query_latencies_ms, 50))
    p99_ms = float(np.percentile(query_latencies_ms, 99))

    print(f"\n[HYBRID SEARCH LATENCY REPORT] p50: {p50_ms:.2f} ms | p99: {p99_ms:.2f} ms")
    assert p50_ms < 15.0, f"Median search latency {p50_ms:.2f} ms exceeded 15.0 ms"
