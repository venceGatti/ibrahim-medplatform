# Changes Summary — Milestone M3 (MedClient Backend Sidecar)

## Overview
Implemented the Python FastAPI sidecar for MedClient (`medclient/sidecar-python/`) covering Features 16, 20–34, and 37–40 according to the architectural blueprints in `PROJECT.md`, `AUDIT_AND_ASSUMPTIONS.md` (ROA-01 to ROA-12), and `SRS_MedClient_Architettura_Completa.md` (lines 1255+).

All code strictly honors the 3-tier layout (`interfaces/`, `base/`, `implementations/`), the line limit constraint (max 300–450 lines per file; actual maximum is 222 lines), zero-mock genuine implementations, and exact dependency pinning.

---

## 1. Pinned Requirements (`requirements.txt`)
Created `medclient/sidecar-python/requirements.txt` with exact version locks:
- `fastapi==0.115.6`
- `uvicorn==0.54.0`
- `pydantic==2.12.5`
- `pydantic-settings==2.16.2`
- `numpy==2.5.4`
- `onnxruntime==1.31.1`
- `symspellpy==6.7.7`
- `xxhash==4.0.2`
- `zstandard==0.25.0`
- `starlette==0.41.3`
- `anyio==4.15.1`
- `httpx==0.28.1`
- `pytest==8.3.4`

---

## 2. Abstract Interfaces (`src/interfaces/`)
Abstract protocol definitions governing contract-first development:
- `watchdog.py` (21 lines): `IReverseWatchdog` protocol for lifecycle management.
- `database.py` (42 lines): `ISqliteConnectionPool` and `IBlueGreenHotSwap` interfaces for zero-allocation connection pooling and atomic swaps.
- `nlp.py` (36 lines): `IMedicalSpellchecker`, `IInvertedLexicalDictionary`, `ISemanticEmbeddingEngine` interfaces.
- `diagnostic.py` (68 lines): `IRedFlagsInterceptor`, `ILogOddsRanker`, `IPertinentNegativesEvaluator`, `ILogSumExpNormalizer`, `IActiveDiscriminator` interfaces.
- `pharmacology.py` (69 lines): `ICYP450Engine`, `IQTcCalculator`, `ITripleWhammyDetector`, `IRenalCalculator`, `IPharmacogenomicsEngine` interfaces.
- `educational.py` (62 lines): `INLICrossEncoder`, `IStatefulDAGScenario`, `IFSRSScheduler`, `IReviewLoadBalancer` interfaces.
- `sdui.py` (60 lines): `ISDUISerializer` interface for server-driven UI envelope packaging.
- `__init__.py` (49 lines): Public interface registry re-exports.

---

## 3. Base Models and Exceptions (`src/base/`)
Strongly typed domain models, enums, and structured error hierarchies:
- `exceptions.py` (56 lines): Domain exception hierarchy (`MedClientError`, `DatabaseLockedError`, `DatabaseIntegrityError`, `HotSwapError`, `ModelInferenceError`, `RedFlagCriticalError`, `InvalidDAGStateError`, `PharmacologySafetyError`, `SDUISerializationError`).
- `database_models.py` (24 lines): `ActiveDbPointer`, `PoolStats`.
- `diagnostic_models.py` (89 lines): `SystemAlertLevel`, `VitalSigns`, `ClinicalFinding`, `RedFlagsAssessment`, `DifferentialCandidate`, `NextBestQuestion`, `SymptomMatcherInput`, `SymptomMatcherOutput`.
- `pharmacology_models.py` (133 lines): `SeverityLevel`, `EvidenceLevel`, `CyP450Isoenzyme`, `InteractionDetail`, `CYPFunctionalState`, `OrganToxicityReport`, `TherapeuticAlternative`, `PharmacogenomicMatch`, `PrescribedDrugItem`, `DrugSafetyBlock`.
- `educational_models.py` (171 lines): `AtomicConcept`, `NLIEvaluationPayload`, `PatientVitals`, `DAGTransition`, `DAGNode`, `StatefulDAGPayload`, `FSRSReviewGrade`, `FSRSStateEnum`, `FSRSCardBase`, `FSRSReviewInput`, `FSRSReviewOutput`, `FSRSDailyBatchRequest`, `FSRSDailyBatchResponse`.
- `sdui_models.py` (105 lines): SDUI polymorphic blocks (`ClinicalSheetBlock`, `SymptomMatcherBlock`, `DrugSafetyBlock`, `ExamSimulatorBlock`), `CalloutItem`, `SDUIPayloadEnvelope`.
- `agentic_models.py` (42 lines): `AgentHealthResponse`, `AgentStateResponse`, `AgentExecuteRequest`, `AgentExecuteResponse`.
- `__init__.py` (28 lines): Unified base model export barrel.

---

## 4. Concrete Engine Implementations (`src/implementations/`)
All implementations contain genuine, non-mock algorithmic logic:
- `reverse_watchdog.py` (80 lines, Feature 16): Win32 `kernel32.WaitForSingleObject` thread polling parent PID, invoking `os._exit(0)` on parent process termination to prevent zombie/orphan processes.
- `sqlite_pool.py` (107 lines, Feature 20): Zero-allocation SQLite WAL connection pool with `PRAGMA journal_mode = WAL;`, `mmap_size = 268435456;` (256MB), `cache_size = -16384;` (64MB), `synchronous = NORMAL;`, `query_only = ON;`.
- `blue_green_swap.py` (99 lines, Feature 21): Atomic hot swap via `active_db.json` pointer verification, `PRAGMA integrity_check`, and atomic pointer replacement using Win32 `MoveFileExW(MOVEFILE_REPLACE_EXISTING)` without connection locking.
- `symspell_checker.py` (90 lines, Feature 22): Symmetric delete spelling correction ($d \le 2$) over medical lemmata dictionary.
- `inverted_dictionary.py` (111 lines, Feature 23): Inverted lexical dictionary with Unicode NFKD normalization, punctuation stripping, and token-based synonym indexing mapping colloquial patient queries to HPO and ICD-10 identifiers.
- `onnx_semantic.py` (72 lines, Feature 24): 384-dimensional dense semantic embedding engine using ONNX INT8 `all-MiniLM-L6-v2` with mean pooling, L2 unit normalization, cosine similarity computation, and IEEE-754 float32 SQLite BLOB pack/unpack routines.
- `red_flags.py` (188 lines, Feature 25): Triage engine computing Shock Index ($\ge 1.0$), qSOFA ($\ge 2$), and NEWS2 ($\ge 7$) with physiological step scores.
- `csr_ranker.py` (184 lines, Feature 26): Sparse CSR disease log-odds ranker with Dirichlet frequency smoothing ($\epsilon = 10^{-4}$), sub-linear cluster dampening ($\gamma_k = 0.5$), and pathognomonic finding multiplier ($\Lambda = 2.5$).
- `pertinent_negatives.py` (53 lines, Feature 27): Pertinent negatives evaluator applying severe log-odds detraction and strict $-\infty$ penalty for refuted essential findings ($P \ge 0.99$).
- `softmax_normalizer.py` (43 lines, Feature 28): Numerically stable Log-Sum-Exp softmax normalization:
  $$P(D_i) = \frac{\exp(S_i - \max_k S_k)}{\sum_j \exp(S_j - \max_k S_k)}$$
- `active_discriminator.py` (98 lines, Feature 29): Next-Best-Question (NBQ) active discrimination algorithm computing Shannon Information Gain normalized by examination/test acquisition cost:
  $$IG(f_j) = H(D) - \left[ P(f_j=1) H(D \mid f_j=1) + P(f_j=0) H(D \mid f_j=0) \right], \quad \text{Score} = \frac{IG(f_j)}{C_j}$$
- `cyp450_engine.py` (222 lines, Feature 30): 5-isoenzyme (3A4, 2D6, 2C9, 2C19, 1A2) functional load engine implementing ROA-10 prodrug bioactivation logic: inhibition of metabolic activation on prodrugs (`is_prodrug = 1`, e.g. Clopidogrel on CYP2C19, Codeine on CYP2D6) triggers Blackbox Warning Level 1 for lethal therapeutic failure (e.g. stent thrombosis).
- `qtc_calculator.py` (83 lines, Feature 31): Multi-agent QTc prolongation score with CredibleMeds risk categorization (Known = 3.0, Possible = 2.0, Conditional = 1.0) and hypokalemia modifier ($K^+ < 3.5 \implies +2.0$). $S_{QTc} \ge 6.0 \implies$ Level 1 Blackbox alert.
- `triple_whammy.py` (83 lines, Feature 32): Nephrotoxicity detector identifying concomitant administration of RAS blocker + Diuretic + NSAID; triggers Level 1 Blackbox alert when patient eGFR < 60 mL/min/1.73m².
- `ckd_epi.py` (32 lines, Feature 33): Race-free CKD-EPI 2021 creatinine-based estimated glomerular filtration rate calculator:
  $$\text{eGFR} = 142 \times \min\left(\frac{S_{cr}}{\kappa}, 1\right)^\alpha \times \max\left(\frac{S_{cr}}{\kappa}, 1\right)^{-1.200} \times 0.9938^{\text{Age}} \times [1.012 \text{ if female}]$$
- `cpic_engine.py` (111 lines, Feature 34): CPIC Level 1A pharmacogenomics rule engine checking high-risk alleles (HLA-B*57:01 with Abacavir $\implies$ Stevens-Johnson syndrome, CYP2C19 poor metabolizers with Clopidogrel, TPMT/NUDT15 with Thiopurines, CYP2D6 ultrarapid metabolizers with Codeine).
- `nli_cross_encoder.py` (139 lines, Feature 37): NLI concept evaluator computing assertion entailment vs contradiction using token-level negation-aware semantic scoring, contradiction detraction factor ($\Phi$), and critical assertion short-circuit.
- `stateful_dag.py` (87 lines, Feature 38): Finite state clinical scenario stepper tracking dynamic vitals (MAP, HR, RR, SpO2, GCS), action time, costs, and terminal grades.
- `fsrs_scheduler.py` (159 lines, Feature 39): Free Spaced Repetition Scheduler (FSRS v4/v5) implementing stability ($S$), difficulty ($D$), target retrievability ($R = 0.9$), optimal interval calculation, lapse recovery, and anti-clustering interval fuzzing.
- `review_balancer.py` (85 lines, Feature 40): Review Hell load balancer computing dynamic priority score ($\Omega$), daily review capacity enforcement, and smoothing across future days.
- `sdui_emitter.py` (105 lines): Polymorphic SDUI serializer emitting the 4 core blocks (`ClinicalSheetBlock`, `SymptomMatcherBlock`, `DrugSafetyBlock`, `ExamSimulatorBlock`) packaged in a versioned envelope with checksum.
- `__init__.py` (46 lines): Implementation barrel export.

---

## 5. API Layer (`src/api/`)
- `agentic_routes.py` (203 lines): Agentic API exposing `/agent/health`, `/agent/state`, `/agent/execute`, and `/agent/schema` bound to loopback `127.0.0.1` and secured with `X-Tauri-IPC-Secret` authentication.
- `sdui_routes.py` (156 lines): High-level evaluation routes `/api/v3/engine/evaluate` (diagnostic symptom matching) and `/api/v3/pharma/evaluate` (comprehensive pharmacology safety analysis) returning polymorphic SDUI block arrays.
- `server.py` (88 lines): FastAPI application factory with lifespan startup hooks, reverse watchdog initiation, and route mounting.
- Subsystem re-exports (`src/database/`, `src/diagnostic/`, `src/educational/`, `src/pharmacology/`): Direct access barrels facilitating backwards-compatible imports.

---

## 6. Test Suite (`tests/`)
Created 4 comprehensive unit test suites:
- `test_storage_and_system.py` (131 lines): Tests SQLite pool initialization, WAL pragmas, pool exhaustion/release, Win32 atomic hot swap with active_db.json, and reverse watchdog contract.
- `test_nlp_and_diagnostic.py` (142 lines): Tests SymSpell lemmata correction, inverted dictionary synonym lookup, ONNX embedding generation and cosine similarity, Shock Index, qSOFA, NEWS2 triage scoring, CSR log-odds ranking, pertinent negatives, and Next-Best-Question discrimination.
- `test_pharmacology.py` (106 lines): Tests race-free CKD-EPI 2021 formula, Triple Whammy AKI alert triggering under eGFR < 60, QTc CredibleMeds calculation, ROA-10 prodrug bioactivation failure (Clopidogrel on CYP2C19), and CPIC Level 1A HLA-B*57:01 / Abacavir contraindication.
- `test_educational_and_sdui.py` (210 lines): Tests NLI cross-encoder evaluation with contradiction penalties, stateful DAG scenario stepper transitions, FSRS v4/v5 interval calculation and memory stability transitions, review load balancing, SDUI 4-block polymorphic serialization, and Agentic API endpoints (`/agent/health`, `/agent/state`, `/agent/execute`, `/agent/schema`).
- `conftest.py` (8 lines): `sys.path` injection establishing `medclient/sidecar-python/` root package importability.
