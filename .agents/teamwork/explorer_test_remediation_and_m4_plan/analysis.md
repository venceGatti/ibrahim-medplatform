# Deep Technical Analysis: Test Suite Remediation & Milestone M4 SDUI Architecture

**Author**: Explorer for Test Remediation & Frontend Architecture (`explorer_test_remediation_and_m4_plan`)  
**Target Recipient**: Parent Orchestrator (`123b80e3-ef7e-4eee-9c78-b41caaecc724`)  
**Status**: Completed Architectural Specification & Remediation Blueprint  
**Date**: 2026-10-31  

---

## 1. Executive Summary

An exhaustive audit of the MedPlatform codebase reveals two mission-critical imperatives:

1. **Test Suite Disconnection in `tests/`**: The existing 514 tests distributed across 20 files in `tests/` (Tiers 1–4) are self-certifying tautologies. Across all 20 test files, there are zero imports of `medfactory` or `medclient`. Instead, tests evaluate synthetic dictionaries and local constants created within test bodies (e.g., `process_exit_code = 0; assert process_exit_code == 0`, `host_rss_mb = 18.5; assert host_rss_mb < 25.0`, `exit_method = "os._exit"; assert exit_method == "os._exit"`). In contrast, `medclient/sidecar-python/tests/` and `medfactory/tests/` contain authentic tests that directly instantiate production classes (`CYP450Engine`, `QTcCalculator`, `TripleWhammyDetector`, `CKDEPI2021Calculator`, `CPICPharmacogenomicsEngine`). Part I of this document defines the complete remediation plan to convert `tests/` into an authentic end-to-end and integration test suite executing real production code without mocks or synthetic variables.
2. **Milestone M4 SDUI Frontend & Tauri Desktop Architecture (`medclient/frontend-react/`)**: Milestone M4 remains to be implemented. The specification requires a React 19 + TypeScript 5.7 + Vite 6 + TailwindCSS 3.4 single-page application embedded in Tauri v2 WebView2. Part II of this document provides a complete architectural blueprint adhering strictly to:
   - File length limits ($\le 300\text{--}450$ lines per file) structured across `interfaces/`, `base/`, `implementations/`.
   - Exact pinned dependency versions in `package.json` (zero floating `^` or `~`).
   - The 8 core features: Feature 41 (Tauri shell IPC), Feature 42 (Zustand persistent store preserving state across tabs), Feature 43 (Polymorphic SDUI 4-block engine with Dual Registry Aliasing), Feature 44 (Virtual windowing maintaining $<30$ mounted DOM nodes), Feature 45 (Zero-copy `med-asset://` protocol integration), Feature 46 (Singleton WebGL broker with context loss auto-recovery), Feature 47 (Agentic API client), and Feature 48 (High-DPI physical coordinate raycasting).

---

## 2. Part I: Complete Remediation Plan for `tests/`

### 2.1 Root-Cause Audit of the Existing 514 Tests in `tests/`

The test suite in `tests/` was constructed with an opaque-box philosophy that mistakenly substituted local synthetic dictionaries for black-box invocations of the platform's public APIs.

#### Catalog of Identified Anti-Patterns:
1. **Local Dictionary Tautologies**: Rather than passing input to a domain engine, test functions declare local Python dictionaries and evaluate assertions against those same dictionaries.
   - *Example (`tests/tier1_features/test_f30_f34_cyp450_pharmacology.py:20-29`)*:
     ```python
     substance = {"name": "Clopidogrel", "is_prodrug": True, "bioactivation_enzyme": "CYP2C19"}
     inhibitor = {"name": "Omeprazole", "inhibits": ["CYP2C19"], "potency": "STRONG"}
     is_prodrug_conflict = (substance["is_prodrug"] and substance["bioactivation_enzyme"] in inhibitor["inhibits"])
     assert is_prodrug_conflict is True
     ```
     *Defect*: Bypasses `medclient.sidecar_python.src.implementations.cyp450_engine.CYP450Engine.evaluate_clearance()`.
2. **Hardcoded State Assertions**: Tests declare static variables representing hypothetical system state and assert against them.
   - *Example (`tests/tier1_features/test_f13_f19_rust_host_ipc.py:61-63, 79-81, 181-182`)*:
     ```python
     process_exit_code = 0; assert process_exit_code == 0
     host_rss_mb = 18.5; assert host_rss_mb < 25.0
     exit_method = "os._exit"; assert exit_method == "os._exit"
     ```
     *Defect*: Tests Python variable assignment rather than process management, jemalloc configuration, or reverse watchdog mechanics.
3. **HTML String Inspection without Rendering**: Frontend tests inspect raw string literals.
   - *Example (`tests/tier1_features/test_f41_f48_frontend_sdui.py:28-29`)*:
     ```python
     index_html = '<!DOCTYPE html><html><body><div id="root"></div></body></html>'
     assert '<div id="root"></div>' in index_html
     ```
     *Defect*: Does not test the SDUI component serialization, AST reconciliation, or DOM rendering engine.
4. **Duplicated Reference Math in `conftest.py`**: `tests/conftest.py` implements redundant copies of CKD-EPI, qSOFA, Shock Index, and Log-Sum-Exp calculations. Tests call these test-local helpers rather than the production implementations in `medclient.sidecar_python.src.implementations`.

---

### 2.2 Production Class & Module Registry for Remediation

Every test in `tests/` must import and execute real classes from the production codebase. Below is the authoritative mapping:

| Feature # | Feature Name | Production Module & Class to Import | Public Method to Invoke | Expected Invariant / Output |
|---|---|---|---|---|
| **F01** | Docling DLA Pipeline | `medfactory.src.dla.implementations.document_layout_analyzer.DocumentLayoutAnalyzer` | `sort_reading_order(boxes)` | Orders blocks by reading flow, resolves bounding boxes |
| **F02** | Multi-Column Anti-Cross-Talk | `medfactory.src.dla.implementations.topological_column_slicer.TopologicalColumnSlicer` | `sort_reading_order(boxes)` | Evaluates $Pos_i = \alpha \cdot Col + \beta \cdot y$; Column 0 precedes Column 1 |
| **F03** | Complex Table Normalizer | `medfactory.src.dla.implementations.complex_table_normalizer.ComplexTableNormalizer` | `resolve_grid(raw_matrix)` | Expands `row_span` and `col_span` into dense 2D grid matrix |
| **F04** | Medical Unit Scale Guard | `medfactory.src.dla.implementations.medical_unit_scale_guard.MedicalUnitScaleGuard` | `sanitize_dosage_units(text)` | Normalizes `ug`, `\u03bcg` $\to$ `mcg`; strips trailing zeros (`5.0 mg` $\to$ `5 mg`); fixes naked decimals (`.5 mg` $\to$ `0.5 mg`) |
| **F05** | Parent-Child Chunking | `medfactory.src.chunking.implementations.hierarchical_chunker.HierarchicalChunker` | `split_into_parents()` & `split_into_children()` | Parent chunks: 800–1200 tokens; Child chunks: 150–250 tokens |
| **F06** | Breadcrumb Context Injection | `medfactory.src.chunking.implementations.breadcrumb_injector.BreadcrumbInjector` | `generate_breadcrumb(hierarchy)` | Generates `# Discipline > System > Condition` context prefix |
| **F07** | PyHPO Ontology Ingestion | `medfactory.src.ontologies.implementations.hpo_ingestor.HPOIngestor` | `compute_ancestor_closure()` & `compute_information_content()` | Computes transitive DAG ancestor closure and Information Content (IC) |
| **F08** | ICD-10 & ATC Ingestion | `medfactory.src.ontologies.implementations.icd10_atc_ingestor.ICD10ATCIngestor` | `ingest_icd10()` & `ingest_atc()` | Parses WHO ICD-10-CM and AIFA ATC Level 5 tree into structured entities |
| **F09** | Zstandard 112KB Dict Trainer | `medfactory.src.compression.implementations.zstd_dictionary_trainer.ZstdDictionaryTrainer` & `medfactory.src.compression.zstd_compressor.ZstdCompressor` | `train_dictionary()` & `compress_with_dictionary()` | Produces exact 114,688-byte dictionary; compresses at Level 19 |
| **F10** | Static Markdown Synthesizer | `medfactory.src.compression.implementations.static_markdown_synthesizer.StaticMarkdownSynthesizer` | `synthesize_monograph()` | Emits encyclopedic monographs with typed callouts (`RED_FLAG`, `CONTRAINDICATION`, `EXAM_TIP`) |
| **F11** | SQLite KB Builder | `medfactory.src.database.implementations.sqlite_module_builder.SQLiteModuleBuilder` | `insert_source()`, `insert_chunk()`, `build()` | Compiles `module_kb.sqlite` with STRICT schema, FTS5 index, B-tree indexes |
| **F12** | `.medpack` Assembler | `medfactory.src.packager.implementations.medpack_assembler.MedPackAssembler` | `assemble_package()` | Builds deterministic `.tar.zst` with BLAKE3 + SHA-256 hashes and Ed25519 signature |
| **F13** | Tauri Host Process | `medclient.sidecar_python.src.api.server.create_app` | `TestClient(app).get("/agent/health")` | FastAPI loopback integration with host lifecycle hooks |
| **F14** | Jemalloc Memory Tuner | `medclient.sidecar_python.src.api.agentic_routes.get_agent_health` | Execution via TestClient | Verifies `rss_mb < 300.0` reported by live memory telemetry |
| **F15** | Win32 Job Object Supervisor | Subprocess test in Python | `subprocess.Popen` / Win32 API check | Verifies Job Object limit `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` |
| **F16** | Reverse Watchdog Thread | `medclient.sidecar_python.src.implementations.reverse_watchdog.ReverseWatchdog` | `start(parent_pid)`, `stop()`, `is_alive()` | Starts real daemon thread with Win32 `WaitForSingleObject`; terminates cleanly |
| **F17** | Throttling State Machine | `medclient.sidecar_python.src.base.agentic_models.AgenticStateResponse` | State calculation via `server.py` | State transitions (`NOMINAL`, `CONSTRAINED`, `CRITICAL`) based on RSS |
| **F18** | Ephemeral IPC Handshake | `medclient.sidecar_python.src.api.server.create_app` | `TestClient` with `X-Tauri-IPC-Secret` | Valid token $\to$ HTTP 200; invalid/missing token $\to$ HTTP 403 Forbidden |
| **F19** | Custom `med-asset://` Protocol | Protocol asset path resolver | Hash-to-disk verification | Resolves 64-char hex SHA-256 to disk asset path for zero-copy mmap |
| **F20** | SQLite WAL Read-Only Pool | `medclient.sidecar_python.src.implementations.sqlite_pool.SqliteConnectionPool` | `get_connection()` context manager | Concurrent multi-threaded reads; verifies `PRAGMA journal_mode = WAL` and `mmap_size = 268435456` |
| **F21** | SQLite Blue/Green Hot Swap | `medclient.sidecar_python.src.implementations.blue_green_swap.BlueGreenHotSwap` | `swap_to_slot()`, `get_active_slot()`, `verify_database_integrity()` | Atomic swap of `active_db.json`, validates schema integrity via `PRAGMA integrity_check` |
| **F22** | SymSpell Medical Spellchecker | `medclient.sidecar_python.src.implementations.symspell_checker.MedicalSymSpellChecker` | `correct_query(text)` & `lookup_term(term)` | Typo-tolerant candidate retrieval ($d \le 2$) over clinical terminology |
| **F23** | Inverted Lexical Dictionary | `medclient.sidecar_python.src.implementations.inverted_dictionary.InvertedLexicalDictionary` | `lookup_colloquial(query)` | Maps colloquial queries to canonical HPO and ICD-10 IDs |
| **F24** | ONNX INT8 Semantic Embedding | `medclient.sidecar_python.src.implementations.onnx_semantic.OnnxSemanticEngine` | `embed_text(text)` | Generates 384-dimensional normalized INT8 embeddings |
| **F25** | Red Flags Interceptor | `medclient.sidecar_python.src.implementations.red_flags.RedFlagsInterceptor` | `evaluate(vitals)` | Computes Shock Index ($HR/SBP > 1.0$), qSOFA ($\ge 2$), NEWS2 ($\ge 7$) alerts |
| **F26** | Sparse CSR Log-Odds Matcher | `medclient.sidecar_python.src.implementations.csr_ranker.SparseCSRLogOddsRanker` | `score_diseases(present, absent)` | In-memory CSR matrix multiplication with Dirichlet smoothing |
| **F27** | Pertinent Negatives Rule-Out | `medclient.sidecar_python.src.implementations.pertinent_negatives.PertinentNegativesEvaluator` | `apply_rule_outs(scores, refuted, probs)` | Applies log-odds detractions and strict exclusion ($-\infty$) for refuting symptoms |
| **F28** | Log-Sum-Exp Softmax Normalizer | `medclient.sidecar_python.src.implementations.softmax_normalizer.LogSumExpNormalizer` | `normalize_logits(logits)` | Numerically stable softmax with exponent shift; ensures $\sum p_i = 1.0$ and handles $-\infty$ |
| **F29** | Active Discrimination (NBQ) | `medclient.sidecar_python.src.implementations.active_discriminator.ActiveDiscriminator` | `select_next_best_question()` | Computes Information Gain per unit cost across uninvestigated symptoms |
| **F30** | CYP450 Functional Load Engine | `medclient.sidecar_python.src.implementations.cyp450_engine.CYP450Engine` | `evaluate_clearance(drugs)` | Multi-way clearance load; prodrug bioactivation block (Clopidogrel + Omeprazole $\to$ Level 1) |
| **F31** | QTc Prolongation Guard | `medclient.sidecar_python.src.implementations.qtc_calculator.QTcCalculator` | `evaluate_qtc(drugs, auc_ratios, serum_k)` | Cumulative cardiac arrhythmia score; $S_{QTc} \ge 6.0 \to$ Level 1 Torsades de Pointes warning |
| **F32** | "Triple Whammy" Detector | `medclient.sidecar_python.src.implementations.triple_whammy.TripleWhammyDetector` | `detect_triple_whammy(drugs, egfr)` | Detects ACEi/ARB + Diuretic + NSAID; triggers Level 1 AKI alert when eGFR $< 60$ |
| **F33** | CKD-EPI 2021 Renal Calculator | `medclient.sidecar_python.src.implementations.ckd_epi.CKDEPI2021Calculator` | `compute_egfr(age, is_female, serum_cr)` | Race-free 2021 formula: verifies Inker et al. NEJM benchmark values |
| **F34** | Pharmacogenomics Rule Engine | `medclient.sidecar_python.src.implementations.cpic_engine.CPICPharmacogenomicsEngine` | `evaluate_pgx(drugs, genotypes)` | CPIC Level 1A guidelines: HLA-B*57:01 (Abacavir), CYP2C19 (Clopidogrel), TPMT (Azathioprine) |
| **F35** | MCQ Assessment Engine | `medclient.sidecar_python.src.implementations.stateful_dag.StatefulDAGScenarioEngine` | `transition()` | Evaluates 4-option clinical items, validates LaTeX equations, records student score |
| **F36** | Image Hotspot Diagnostics | `medclient.sidecar_python.src.implementations.stateful_dag` & spatial raycasting | Ray-casting Even-Odd algorithm | Tests point $(x, y)$ inside SVG polygon coordinates with high-DPI scaling |
| **F37** | NLI Cross-Encoder Evaluator | `medclient.sidecar_python.src.implementations.nli_cross_encoder.NLICrossEncoderEvaluator` | `evaluate_free_text(answer, rubrics)` | Evaluates student free-text against atomic concepts (Entailment / Neutral / Contradiction) |
| **F38** | Stateful DAG Scenario Engine | `medclient.sidecar_python.src.implementations.stateful_dag.StatefulDAGScenarioEngine` | `transition(node_id, action_id, vitals)` | Advances clinical scenario state, applies delta vitals, computes cumulative risk/cost |
| **F39** | FSRS v4/v5 Mnemonic Scheduler | `medclient.sidecar_python.src.implementations.fsrs_scheduler.FSRSScheduler` | `calculate_retrievability()`, `calculate_interval()` | Evaluates memory retrievability $R = (1 + \text{factor} \cdot t / S)^{-0.5}$, target retention $R=0.9$ |
| **F40** | Review Load Balancer | `medclient.sidecar_python.src.implementations.review_balancer.ReviewLoadBalancer` | `balance_daily_reviews(cards, max_daily)` | Smooths review spikes to mitigate "Review Hell" before exam dates |
| **F41** | React 19 Frontend Shell | `medclient.sidecar_python.src.api.sdui_routes.router` | TestClient `/api/v3/engine/evaluate` | Verifies backend JSON contract feeding React shell |
| **F42** | Zustand Persistent Store | `medclient.sidecar_python.src.base.agentic_models.AgenticStateResponse` | State synchronization via `/agent/state` | Verifies full state serialization for client store hydration |
| **F43** | `ClinicalSheetBlock` Component | `medclient.sidecar_python.src.implementations.sdui_emitter.SDUISerializer` | `build_clinical_sheet_block()` | Produces schema-compliant block with Dual Registry alias `MarkdownBlock` |
| **F44** | `SymptomMatcherBlock` Component | `medclient.sidecar_python.src.implementations.sdui_emitter.SDUISerializer` | `build_symptom_matcher_block()` | Produces schema-compliant block with Dual Registry alias `DifferentialDiagnosisBlock` |
| **F45** | `DrugSafetyBlock` Component | `medclient.sidecar_python.src.implementations.sdui_emitter.SDUISerializer` | `build_drug_safety_block()` | Produces schema-compliant block with interactions, CYP clearance, alerts, eGFR |
| **F46** | `ExamSimulatorBlock` Component | `medclient.sidecar_python.src.implementations.sdui_emitter.SDUISerializer` | `build_exam_simulator_block()` | Produces schema-compliant block with Dual Registry alias `ClinicalExamBlock` |
| **F47** | Virtual DOM Windowing | Virtual Windowing contract validator | Payload slicing verification | Verifies windowed block list generation for $<30$ DOM nodes |
| **F48** | Singleton WebGL Broker | WebGL Broker contract validator | Context allocation & eviction schema | Verifies single-context token lifecycle and fallback SVG payload |

---

### 2.3 Shared Fixtures & Authentic Data Strategy (`tests/conftest.py` Overhaul)

`tests/conftest.py` must be refactored to remove redundant local mathematical functions and instead provide authentic system fixtures:

1. **`app_client` Fixture**: Instantiates `create_app(ipc_token="TEST_IPC_SECRET_128BIT")` and returns a `fastapi.testclient.TestClient` configured with the `X-Tauri-IPC-Secret` authentication header.
2. **`real_sqlite_kb` Fixture**: Uses `SQLiteModuleBuilder` in a `pytest.fixture(scope="session")` to build a temporary, fully structured `module_kb.sqlite` containing:
   - 10 real ICD-10 disease records (e.g., `I21.0` STEMI, `I30.0` Acute Pericarditis, `I46.9` Cardiac Arrest, `N18.3` CKD Stage 3).
   - 25 real HPO phenotype terms (e.g., `HP:0001635` Heart Failure, `HP:0002094` Dyspnea, `HP:0001649` Angina Pectoris).
   - 15 real ATC Level 5 substances (e.g., `B01AC04` Clopidogrel, `A02BC01` Omeprazole, `C09AA03` Lisinopril, `C03AA03` Hydrochlorothiazide, `M01AE01` Ibuprofen, `C01BD01` Amiodarone, `J01MA02` Ciprofloxacin).
   - Saturated B-Tree indexes and FTS5 full-text search index.
3. **`real_sqlite_pool` Fixture**: Instantiates `SqliteConnectionPool` pointing to the database generated by `real_sqlite_kb`, verifying WAL mode and mmap allocation.
4. **`hot_swap_controller` Fixture**: Instantiates `BlueGreenHotSwap` with an isolated temporary directory containing a valid `active_db.json` pointer file.
5. **`ed25519_keypair` Fixture**: Generates authentic cryptographic keys via `cryptography.hazmat.primitives.asymmetric.ed25519`.
6. **Elimination of Duplicated Math**: The local functions `compute_ckd_epi_2021`, `compute_qsofa_score`, `compute_shock_index`, `log_sum_exp`, `compute_softmax_probabilities`, and `fsrs_calculate_retrievability` in `conftest.py` must be replaced by direct re-exports or invocations of the production classes:
   ```python
   from medclient.sidecar_python.src.implementations.ckd_epi import CKDEPI2021Calculator
   from medclient.sidecar_python.src.implementations.red_flags import RedFlagsInterceptor
   from medclient.sidecar_python.src.implementations.softmax_normalizer import LogSumExpNormalizer
   from medclient.sidecar_python.src.implementations.fsrs_scheduler import FSRSScheduler
   ```

---

### 2.4 File-by-File Remediation Plan for All 20 Test Files

Below is the concrete transformation specification for each test file in the `tests/` directory:

#### 1. `tests/tier1_features/test_f01_f06_dla_chunking.py` (Features 1–6)
- **Current State**: Declares raw dicts `raw_document_elements`, `unsorted_blocks`, and runs Python `sorted()`.
- **Remediation**:
  - Import: `DocumentLayoutAnalyzer`, `TopologicalColumnSlicer`, `ComplexTableNormalizer`, `MedicalUnitScaleGuard`, `HierarchicalChunker`, `BreadcrumbInjector`, `DocumentBoundingBox`, `DocumentBlockCategory`, `RawTableCell`.
  - Feature 1: Pass real `DocumentBoundingBox` instances to `DocumentLayoutAnalyzer.sort_reading_order()`, verifying reading order resolution.
  - Feature 2: Instantiate `TopologicalColumnSlicer(alpha=10000.0, beta=1.0)`. Provide two-column boxes with Column 0 at $y=120$ and Column 1 at $y=20$. Assert Column 0 box precedes Column 1 box, proving anti-cross-talk formula $Pos = \alpha \cdot Col + \beta \cdot y$.
  - Feature 3: Construct a 2D matrix of `RawTableCell` with `row_span=2` and `col_span=2`. Invoke `ComplexTableNormalizer.resolve_grid()`. Assert the resulting 2D grid contains duplicated cell references at all spanned coordinates.
  - Feature 4: Pass medical text strings containing `.5 mg`, `5.0 mg`, `10 ug/ml`, `2.50 mcg` to `MedicalUnitScaleGuard.sanitize_dosage_units()`. Assert sanitized output is `0.5 mg`, `5 mg`, `10 mcg/ml`, `2.5 mcg`.
  - Feature 5: Feed 2500-token medical markdown to `HierarchicalChunker.split_into_parents()` and `split_into_children()`. Assert parent chunk token counts are in $[800, 1200]$ and child chunk token counts are in $[150, 250]$.
  - Feature 6: Call `BreadcrumbInjector.generate_breadcrumb(["Cardiology", "Coronary Artery Disease", "STEMI"])`. Assert breadcrumb header `# Cardiology > Coronary Artery Disease > STEMI` is produced and within the 50-token budget.

#### 2. `tests/tier1_features/test_f07_f12_ontologies_packaging.py` (Features 7–12)
- **Current State**: Evaluates synthetic dictionaries `hpo_dag`, `icd10_tree`, mock compression ratios, and manual hashlib calls.
- **Remediation**:
  - Import: `HPOIngestor`, `ICD10ATCIngestor`, `ZstdDictionaryTrainer`, `ZstdCompressor`, `StaticMarkdownSynthesizer`, `SQLiteModuleBuilder`, `MedPackAssembler`.
  - Feature 7: Instantiate `HPOIngestor()`. Call `compute_ancestor_closure("HP:0001635")` (Heart failure). Assert ancestors include `HP:0001626` (Cardiovascular abnormality), `HP:0000118` (Phenotypic abnormality), and root `HP:0000001`. Call `compute_information_content()`, asserting $IC > 0.0$ and leaf nodes have higher $IC$ than root nodes.
  - Feature 8: Instantiate `ICD10ATCIngestor()`. Query ICD-10 `I21` (Acute myocardial infarction) and ATC `B01AC04` (Clopidogrel). Verify hierarchical parent/child navigation.
  - Feature 9: Instantiate `ZstdDictionaryTrainer` with medical training samples. Verify trained dictionary length is exactly 114,688 bytes (112 KB). Use `ZstdCompressor(dict_data)` to compress a clinical monograph at Level 19; assert decompressed output matches original bit-for-bit.
  - Feature 10: Instantiate `StaticMarkdownSynthesizer`. Pass structured monograph data. Assert generated Markdown contains formal callout blocks: `> [!RED_FLAG]`, `> [!CONTRAINDICATION]`, `> [!EXAM_TIP]`.
  - Feature 11: Instantiate `SQLiteModuleBuilder(temp_path)`. Call `insert_source()`, `insert_chunk()`. Commit and query via `sqlite3`. Verify `module_kb.sqlite` has `STRICT` tables, `fts5` virtual table, and valid indices.
  - Feature 12: Instantiate `MedPackAssembler()`. Package the test database, media, and manifest into a `.medpack` archive. Sign with Ed25519. Assert BLAKE3 and SHA-256 match and signature verifies successfully.

#### 3. `tests/tier1_features/test_f13_f19_rust_host_ipc.py` (Features 13–19)
- **Current State**: Asserts `process_exit_code = 0; assert process_exit_code == 0`, `exit_method = "os._exit"; assert exit_method == "os._exit"`.
- **Remediation**:
  - Import: `ReverseWatchdog`, `create_app`, `TestClient`.
  - Feature 13: Test FastAPI application startup with `create_app()`. Query `/agent/health` via `TestClient`. Verify response code 200 and schema validity.
  - Feature 14: Query `/agent/health` and verify `rss_mb` is a positive float strictly $< 300.0\text{ MB}$.
  - Feature 15: Execute real Win32 Job Object check or subprocess execution asserting child process containment.
  - Feature 16: Instantiate `ReverseWatchdog(poll_interval_ms=50)`. Start with `os.getpid()`. Assert `watchdog.is_alive() is True` and `watchdog._thread.daemon is True`. Stop watchdog and assert `watchdog.is_alive() is False`.
  - Feature 17: Query `/agent/state`. Verify health metrics and system status reporting (`alert_level` transitions based on telemetry thresholds).
  - Feature 18: Send requests with and without `X-Tauri-IPC-Secret` header to `create_app(ipc_token="SEC_TOKEN_42")`. Assert 403 Forbidden on missing/wrong token, 200 OK on correct token.
  - Feature 19: Test media path resolution: given a SHA-256 hash, verify deterministic resolution to `.webp` file path.

#### 4. `tests/tier1_features/test_f20_f24_sqlite_nlp.py` (Features 20–24)
- **Current State**: Tests local mock SQLite connections and synthetic dictionaries.
- **Remediation**:
  - Import: `SqliteConnectionPool`, `BlueGreenHotSwap`, `MedicalSymSpellChecker`, `InvertedLexicalDictionary`, `OnnxSemanticEngine`.
  - Feature 20: Instantiate `SqliteConnectionPool` against `real_sqlite_kb`. Spawn 8 concurrent threads executing reads. Verify zero database lock errors, `PRAGMA journal_mode` returns `wal`, and `PRAGMA mmap_size` is 256MB.
  - Feature 21: Instantiate `BlueGreenHotSwap`. Execute `swap_to_slot("green", green_db_path)`. Verify `get_active_slot() == "green"`, pointer file is atomically rewritten, and `verify_database_integrity()` passes.
  - Feature 22: Instantiate `MedicalSymSpellChecker()`. Pass misspelled queries (e.g. `"miocardial infarxion"`, `"disfpnea"`). Assert corrections resolve to `"myocardial infarction"` and `"dyspnea"`.
  - Feature 23: Instantiate `InvertedLexicalDictionary()`. Lookup colloquial query `"heart attack"`. Assert resolution to `I21` (ICD-10) and `HP:0001658` (Myocardial infarction).
  - Feature 24: Instantiate `OnnxSemanticEngine()`. Compute embedding vector for `"acute coronary syndrome"`. Assert shape is `(384,)`, $L_2$ norm is $1.0 \pm 10^{-5}$, and cosine similarity with `"myocardial infarction"` is $> 0.60$.

#### 5. `tests/tier1_features/test_f25_f29_log_odds_diagnostic.py` (Features 25–29)
- **Current State**: Evaluates hardcoded arrays of logits.
- **Remediation**:
  - Import: `RedFlagsInterceptor`, `SparseCSRLogOddsRanker`, `PertinentNegativesEvaluator`, `LogSumExpNormalizer`, `ActiveDiscriminator`.
  - Feature 25: Call `RedFlagsInterceptor.evaluate()` with septic shock vitals ($HR=125, SBP=85, RR=24$). Assert Shock Index $1.47 > 1.0$, qSOFA $= 2 \ge 2$, and priority emergency trigger is generated.
  - Feature 26: Instantiate `SparseCSRLogOddsRanker`. Load disease feature matrix. Pass findings `["HP:0001658", "HP:0002094"]`. Assert disease ranking returns STEMI as top candidate with log-odds score.
  - Feature 27: Instantiate `PertinentNegativesEvaluator`. Refute pathognomonic finding (e.g., absent chest pain for angina). Assert candidate score is detracted or assigned $-\infty$ (strict rule-out).
  - Feature 28: Instantiate `LogSumExpNormalizer`. Pass logits `[1000.0, 999.0, 990.0, -math.inf]`. Assert calculation does not overflow/NaN, $-\infty$ receives $0.0$ probability, and finite probabilities sum to exactly $1.0$.
  - Feature 29: Instantiate `ActiveDiscriminator`. Pass top two ambiguous candidates with close probabilities. Assert algorithm selects the symptom that maximizes Information Gain per unit cost.

#### 6. `tests/tier1_features/test_f30_f34_cyp450_pharmacology.py` (Features 30–34)
- **Current State**: Synthetic local dictionaries for prodrugs and inhibitors.
- **Remediation**:
  - Import: `CYP450Engine`, `QTcCalculator`, `TripleWhammyDetector`, `CKDEPI2021Calculator`, `CPICPharmacogenomicsEngine`, `SeverityLevel`.
  - Feature 30: Instantiate `CYP450Engine`. Pass Clopidogrel (prodrug) + Omeprazole (CYP2C19 inhibitor). Assert `detected_interactions` contains Blackbox Warning Severity Level 1 for bioactivation failure. Pass Simvastatin + Clarithromycin (CYP3A4 inhibitor); assert accumulation toxicity warning.
  - Feature 31: Instantiate `QTcCalculator`. Pass Amiodarone ($3.0$) + Ciprofloxacin ($3.0$) + hypokalemia ($K^+ = 3.1\text{ mEq/L}$). Assert $S_{QTc} \ge 6.0$ and Torsades de Pointes risk is Severity Level 1.
  - Feature 32: Instantiate `TripleWhammyDetector`. Pass Lisinopril (ACEi) + Hydrochlorothiazide (Diuretic) + Ibuprofen (NSAID) with eGFR $= 48.0$. Assert Triple Whammy is detected with Level 1 AKI alert and recommendation to cease NSAID.
  - Feature 33: Instantiate `CKDEPI2021Calculator`. Call `compute_egfr()` with NEJM reference cases:
    - 60yo female, Serum Cr $= 1.2\text{ mg/dL} \to \text{eGFR} \approx 52\text{ mL/min/1.73m}^2$.
    - 50yo male, Serum Cr $= 0.9\text{ mg/dL} \to \text{eGFR} \approx 98\text{ mL/min/1.73m}^2$.
  - Feature 34: Instantiate `CPICPharmacogenomicsEngine`. Pass Abacavir with genotype `HLA-B*57:01 positive`. Assert Level 1A fatal hypersensitivity contraindication.

#### 7. `tests/tier1_features/test_f35_f40_educational_fsrs.py` (Features 35–40)
- **Current State**: Tests local mock FSRS intervals and dummy dictionaries.
- **Remediation**:
  - Import: `StatefulDAGScenarioEngine`, `NLICrossEncoderEvaluator`, `FSRSScheduler`, `ReviewLoadBalancer`.
  - Feature 35 & 38: Instantiate `StatefulDAGScenarioEngine` with clinical trauma scenario. Execute transition with action `"administer_iv_fluids"`. Assert patient vitals update, mean arterial pressure increases, and state transitions to `"fluid_resuscitated"`.
  - Feature 36: Test spatial ray-casting: define chest radiograph tension pneumothorax SVG polygon. Test point inside polygon $\to$ `True`; test point outside $\to$ `False`.
  - Feature 37: Instantiate `NLICrossEncoderEvaluator`. Pass student answer `"Patient requires immediate needle thoracostomy"` against rubric `"Perform emergency needle decompression"`. Assert high Entailment probability ($> 0.80$). Pass `"Administer high-dose steroids"`; assert Contradiction / Neutral.
  - Feature 39: Instantiate `FSRSScheduler`. Pass review grade `Good` (3). Compute next interval and retrievability after $t$ days. Assert retention follows $R = (1 + \text{factor} \cdot t / S)^{-0.5}$.
  - Feature 40: Instantiate `ReviewLoadBalancer`. Pass batch of cards with identical due dates. Assert scheduler spreads reviews evenly across window before target exam date.

#### 8. `tests/tier1_features/test_f41_f48_frontend_sdui.py` (Features 41–48)
- **Current State**: String assertions on `index_html`, local mock Zustand dictionaries.
- **Remediation**:
  - Import: `SDUISerializer`, `create_app`, `TestClient`, `ClinicalSheetBlock`, `SymptomMatcherBlock`, `DrugSafetyBlock`, `ExamSimulatorBlock`.
  - Feature 41: Query FastAPI server via `TestClient` for SDUI endpoints. Assert response status 200 and schema compliance.
  - Feature 42: Validate full application state schema exported by `/agent/state`, verifying all necessary fields for Zustand store hydration are present.
  - Feature 43: Use `SDUISerializer` to emit `ClinicalSheetBlock`. Validate JSON against `ClinicalSheetBlock` schema and verify Dual Registry alias `MarkdownBlock`.
  - Feature 44: Use `SDUISerializer` to emit `SymptomMatcherBlock`. Validate JSON against `SymptomMatcherBlock` schema and verify Dual Registry alias `DifferentialDiagnosisBlock`.
  - Feature 45: Use `SDUISerializer` to emit `DrugSafetyBlock`. Validate JSON against `DrugSafetyBlock` schema (interactions, CYP clearance, alerts, eGFR).
  - Feature 46: Use `SDUISerializer` to emit `ExamSimulatorBlock`. Validate JSON against `ExamSimulatorBlock` schema and verify Dual Registry aliases `ClinicalExamBlock` and `InteractiveFlowchartBlock`.
  - Feature 47: Virtual Windowing contract: serialize an envelope of 50 SDUI blocks. Execute windowing slicer function ($|V_{\text{active}}| \le 8$); assert mounted DOM nodes stay $< 30$.
  - Feature 48: Singleton WebGL Broker contract: verify component contract emits fallback SVG URL when WebGL context is not active, and registers cleanup callback upon eviction.

#### 9–12. `tests/tier2_boundaries/` (Boundary & Corner Cases)
- **`test_b01_b12_factory_boundaries.py`**:
  - Test `MedicalUnitScaleGuard` on malformed inputs (empty strings, zero division, strings with multiple conflicting units).
  - Test `ComplexTableNormalizer` on 0-column tables, negative spans, and recursive merges.
  - Test `ZstdDictionaryTrainer` on degenerate corpora (<100KB); assert proper exception or padding.
  - Test `SQLiteModuleBuilder` on duplicate primary keys, null constraint violations, and SQL injection payloads in metadata.
- **`test_b13_b24_host_database_boundaries.py`**:
  - Test `SqliteConnectionPool` exhaust pool capacity ($N > 8$ connections) with timeout; assert `DatabaseLockedError`.
  - Test `BlueGreenHotSwap` corrupted `active_db.json` and missing slot database; assert `HotSwapVerificationError`.
  - Test `MedicalSymSpellChecker` with empty query, Unicode emojis, and strings $> 1000$ characters.
  - Test `ReverseWatchdog` with invalid parent PID (-1, 0, non-existent PID).
- **`test_b25_b34_diagnostic_pharma_boundaries.py`**:
  - Test `LogSumExpNormalizer` with all $-\infty$ logits; assert uniform zero array returned without crash.
  - Test `CKDEPI2021Calculator` with extreme serum creatinine ($0.1\text{ mg/dL}$ and $20.0\text{ mg/dL}$), age $100$.
  - Test `CYP450Engine` with 10 concurrent competing drugs; assert no heap overflow or deadlock.
  - Test `QTcCalculator` with normal potassium ($4.5\text{ mEq/L}$) vs extreme hyperkalemia / hypokalemia.
- **`test_b35_b48_edu_sdui_boundaries.py`**:
  - Test `FSRSScheduler` with extreme elapsed days ($1000$ days) and minimum stability ($0.01$).
  - Test `StatefulDAGScenarioEngine` invalid transition edge not present in DAG; assert `InvalidDAGTransitionError`.
  - Test SDUI polymorphic deserializer on unknown `component_type`; assert graceful handling or rejection.

#### 13–16. `tests/tier3_pairwise/` (Cross-Feature Pairwise Interactions)
- **`test_p01_dla_table_zstd_compression.py`**:
  - Extract complex table via `ComplexTableNormalizer`, synthesize Markdown with `StaticMarkdownSynthesizer`, and compress with `ZstdCompressor(112KB dict)`. Assert compression ratio $> 3.5\times$ and bit-for-bit reconstruction.
- **`test_p02_blue_green_wal_concurrency.py`**:
  - While 4 threads read from active slot via `SqliteConnectionPool`, trigger `BlueGreenHotSwap.swap_to_slot()`. Assert zero thread crashes, zero locked database exceptions, and seamless transition to new slot.
- **`test_p03_log_odds_cyp450_safety.py`**:
  - Run `SparseCSRLogOddsRanker` to identify suspected disease (STEMI) $\to$ extract indicated treatment (Clopidogrel) $\to$ evaluate patient's current medications (Omeprazole) via `CYP450Engine`. Assert diagnostic engine output seamlessly feeds pharmacology safety engine and triggers Level 1 alert.
- **`test_p04_fsrs_sdui_rendering.py`**:
  - Execute review in `FSRSScheduler` $\to$ emit updated card state into `ExamSimulatorBlock` via `SDUISerializer`. Assert resulting JSON payload validates against `ExamSimulatorBlock` schema.

#### 17–20. `tests/tier4_workloads/` (Real-World Clinical Workloads)
- **`test_w01_stemi_clopidogrel_omeprazole.py`**:
  - Stage 1: Feed STEMI findings to `SparseCSRLogOddsRanker`. Assert STEMI is top differential candidate.
  - Stage 2: Prescribe Aspirin + Clopidogrel + Omeprazole.
  - Stage 3: Pass prescription to `CYP450Engine`. Assert Blackbox Warning Severity Level 1 for CYP2C19 bioactivation inhibition and stent thrombosis risk.
  - Stage 4: Recommend switching to Pantoprazole or Prasugrel. Re-evaluate with `CYP450Engine`; assert alert is cleared (Severity Level 3 or NOMINAL).
- **`test_w02_sepsis_qsofa_escalation.py`**:
  - Stage 1: Present septic vitals ($RR=26, SBP=88, HR=118$, altered mentation).
  - Stage 2: Evaluate with `RedFlagsInterceptor`. Assert Shock Index $1.34 > 1.0$ and qSOFA $= 3/3$, triggering immediate emergency escalation before diagnostic matrix traversal.
- **`test_w03_diabetic_nephropathy_triple_whammy.py`**:
  - Stage 1: Patient on Lisinopril + Hydrochlorothiazide + OTC Ibuprofen with serum Cr $2.1\text{ mg/dL}$.
  - Stage 2: Compute eGFR with `CKDEPI2021Calculator` ($\text{eGFR} < 60$).
  - Stage 3: Pass to `TripleWhammyDetector`. Assert Level 1 Acute Kidney Injury alert and mandatory NSAID cessation recommendation.
- **`test_w04_mcq_hotspot_exam_session.py`**:
  - Stage 1: Display tension pneumothorax radiograph hotspot. Evaluate student click coordinate via point-in-polygon Even-Odd raycasting. Assert hit detected.
  - Stage 2: Answer 4-option MCQ for immediate needle decompression. Assert correct.
  - Stage 3: Pass response to `FSRSScheduler`. Assert card transitions from Learning to Review with updated stability $S$ and retention $R = 0.9$.

---

### 2.5 Remediation of `tests/e2e_runner.py`

`tests/e2e_runner.py` must execute authentic tests and enforce runtime verification gates:
1. **PyTest Execution**: Run pytest across `tests/` with `-v -s --tb=short`.
2. **Process Gate**: Assert exit code is exactly `0` (zero failures, zero skipped tests).
3. **Telemetry RSS Check**: Capture process memory using `psutil.Process().memory_info().rss`. Assert total RSS $< 300\text{ MB}$.
4. **Latency Micro-Benchmark**: Measure execution time for core diagnostic ranking and pharmacology evaluation. Assert P99 latency $< 50\text{ ms}$.

---

## 3. Part II: Milestone M4 Architecture & Implementation Plan (`medclient/frontend-react/`)

### 3.1 Architectural Paradigm & Hardware Constraints

MedClient runs on client machines (Intel Core i7 without dedicated GPU, shared UMA memory). The frontend must operate as a deterministic **"Dumb Painter"**:
- **Zero Business Logic in UI**: The frontend does not calculate clinical scores, does not parse ontologies, and does not maintain independent mutable medical state.
- **Strict Memory Budget**: WebView2 resident memory must stay strictly $< 100\text{ MB}$ ($M_{\text{Base}} \approx 42\text{ MB}$, $V_{\text{active}} \le 32\text{ MB}$, $M_{\text{WebGL}} \le 24\text{ MB}$).
- **Frame Budget (60 FPS / 16.6ms)**:
  - $\Delta T_{\text{IPC}} < 3.0\text{ ms}$
  - $\Delta T_{\text{AST\_Parse}} < 2.5\text{ ms}$
  - $\Delta T_{\text{VDOM\_Diff}} < 4.0\text{ ms}$
  - $\Delta T_{\text{Paint}} < 6.0\text{ ms}$

---

### 3.2 Exact Pinned Dependency Specification (`package.json`)

To guarantee reproducible builds and satisfy the absolute prohibition against floating dependencies, `medclient/frontend-react/package.json` must pin every dependency to an exact release without `^` or `~`:

```json
{
  "name": "medclient-frontend-react",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "dependencies": {
    "react": "19.0.0",
    "react-dom": "19.0.0",
    "zustand": "5.0.2",
    "@tauri-apps/api": "2.2.0",
    "lucide-react": "0.469.0",
    "katex": "0.16.11",
    "clsx": "2.1.1",
    "tailwind-merge": "2.6.0"
  },
  "devDependencies": {
    "@types/react": "19.0.2",
    "@types/react-dom": "19.0.2",
    "@types/katex": "0.16.7",
    "@vitejs/plugin-react": "4.3.4",
    "typescript": "5.7.2",
    "vite": "6.0.7",
    "tailwindcss": "3.4.17",
    "postcss": "8.4.49",
    "autoprefixer": "10.4.20",
    "vitest": "2.1.8",
    "@testing-library/react": "16.1.0",
    "@testing-library/jest-dom": "6.6.3",
    "jsdom": "25.0.1"
  }
}
```

---

### 3.3 Modular File Hierarchy (All Files $\le 300\text{--}450$ Lines)

To satisfy the micro-file rule and separation of concerns, `medclient/frontend-react/src/` is organized into `interfaces/`, `base/`, and `implementations/` (along with `store/` and `components/`):

```
medclient/frontend-react/
├── package.json                    # Exact pinned dependencies
├── tsconfig.json                   # Strict TypeScript compiler options
├── tsconfig.node.json
├── vite.config.ts                  # Vite 6 config with React 19 plugin
├── tailwind.config.js              # Medical UI color tokens & typography
├── postcss.config.js
├── index.html                      # HTML5 entrypoint mounting <div id="root">
└── src/
    ├── main.tsx                    # React 19 root bootstrap & error boundary (<100 lines)
    ├── App.tsx                     # Top-level layout, persistent tabs, IPC status (<200 lines)
    ├── vite-env.d.ts
    │
    ├── interfaces/                 # Formal contracts & TypeScript definitions
    │   ├── sdui.types.ts           # SDUI 4-block types, Callouts, Dual Aliases (<250 lines)
    │   ├── store.types.ts          # Zustand state slices & actions contracts (<200 lines)
    │   ├── tauri.types.ts          # Tauri IPC invoke & event interfaces (<150 lines)
    │   ├── webgl.types.ts          # WebGL Broker context manager contracts (<120 lines)
    │   └── agentic.types.ts        # Agentic API state & execute payload types (<150 lines)
    │
    ├── base/                       # Shared foundational components & utilities
    │   ├── ErrorBoundary.tsx       # Component error boundary with recovery UI (<180 lines)
    │   ├── BlockSkeleton.tsx       # Shimmer placeholder for loading blocks (<100 lines)
    │   ├── CalloutBadge.tsx        # Typed medical callout renderer (<220 lines)
    │   ├── KatexMath.tsx           # KaTeX mathematical formula renderer (<120 lines)
    │   └── ChemicalDrawer.tsx      # SmilesDrawer 2D canvas structure renderer (<200 lines)
    │
    ├── implementations/            # Concrete functional engines & components
    │   ├── sdui/
    │   │   ├── SDUIBlockDispatcher.tsx    # Polymorphic dispatcher & dual aliasing (<220 lines)
    │   │   ├── ClinicalSheetBlock.tsx     # Monograph renderer with callouts (<280 lines)
    │   │   ├── SymptomMatcherBlock.tsx    # Differential ranking & symptom tags (<300 lines)
    │   │   ├── DrugSafetyBlock.tsx        # Interaction matrix, gauges & warnings (<320 lines)
    │   │   └── ExamSimulatorBlock.tsx     # MCQ, SVG hotspot & DAG scenario (<340 lines)
    │   │
    │   ├── virtual/
    │   │   └── VirtualWindowList.tsx      # Viewport sliding window (<30 DOM nodes) (<250 lines)
    │   │
    │   ├── webgl/
    │   │   ├── WebGLContextBroker.ts      # Singleton broker with WEBGL_lose_context (<180 lines)
    │   │   └── Molecule3DViewer.tsx       # Click-to-interact PDB viewer with fallback (<280 lines)
    │   │
    │   ├── spatial/
    │   │   ├── RaycastingAlgorithm.ts     # High-DPI physical coordinate Even-Odd rule (<160 lines)
    │   │   └── HotspotCanvas.tsx          # SVG polygon canvas with coordinate mapping (<260 lines)
    │   │
    │   ├── ipc/
    │   │   ├── TauriClient.ts             # Typed wrapper around @tauri-apps/api (<200 lines)
    │   │   └── AssetProtocolBridge.ts     # med-asset:// URL resolver & cache (<140 lines)
    │   │
    │   └── agent/
    │       └── AgenticApiClient.ts        # Exposes UI state & actions to /agent/* (<220 lines)
    │
    └── store/                      # Zustand Persistent Store with Zero Data Loss
        ├── useAppStore.ts          # Root combined store with persist middleware (<180 lines)
        ├── slices/
        │   ├── clinicalSheetSlice.ts  # Active monograph & search query state (<150 lines)
        │   ├── symptomMatcherSlice.ts # Selected symptoms & differential state (<180 lines)
        │   ├── drugSafetySlice.ts     # Prescribed drug list & interaction state (<160 lines)
        │   ├── examSimulatorSlice.ts  # Current question, answers, DAG history (<200 lines)
        │   └── navigationSlice.ts     # Active tab, sidebar collapse, IPC tokens (<120 lines)
```

---

### 3.4 Feature-by-Feature Implementation Specification

#### Feature 41: Tauri v2 Desktop Shell & IPC Client (`@tauri-apps/api`)
- **Location**: `src/implementations/ipc/TauriClient.ts` ($\le 200$ lines)
- **Mechanism**:
  - Wraps `@tauri-apps/api/core` `invoke()`.
  - Reads ephemeral loopback port and token passed from Tauri via initial window state or bootstrap invoke `get_sidecar_credentials()`.
  - Injects `X-Tauri-IPC-Secret: <token>` into all HTTP requests made to `http://127.0.0.1:<port>`.
  - Captures native window lifecycle events (`tauri://close-requested`, `tauri://resize`).
  - Implements exponential backoff retry ($100\text{ms}, 200\text{ms}, 400\text{ms}, \dots, 2000\text{ms}$) if the sidecar connection drops during startup.

#### Feature 42: Zustand Persistent Store with Zero Data Loss Across Tabs
- **Location**: `src/store/useAppStore.ts` and `src/store/slices/*.ts` (each $\le 200$ lines)
- **Mechanism**:
  - Implements slice pattern: `clinicalSheetSlice`, `symptomMatcherSlice`, `drugSafetySlice`, `examSimulatorSlice`, `navigationSlice`.
  - **DOM & Store Retention (Rule 8 Compliance)**: When the user navigates between tabs (e.g. from Symptom Matcher to Exam Simulator), views are NOT unmounted from the DOM. Instead, `App.tsx` preserves all tab containers using CSS visibility toggling (`display: block` vs `display: none` / `invisible absolute`).
  - Form inputs, selected symptoms, active MCQ selections, and diagnostic sliders persist indefinitely in the Zustand store memory. Zero user data is lost upon tab switching.

#### Feature 43: Polymorphic SDUI 4-Block Engine with Dual Registry Aliasing
- **Location**: `src/implementations/sdui/SDUIBlockDispatcher.tsx` ($\le 220$ lines)
- **Contract & Aliasing**:
  - Resolves blocks using a **Dual Registry Aliasing Map**:
    ```typescript
    const BLOCK_REGISTRY: Record<string, React.ComponentType<any>> = {
      // Canonical names
      ClinicalSheetBlock: ClinicalSheetBlockComponent,
      SymptomMatcherBlock: SymptomMatcherBlockComponent,
      DrugSafetyBlock: DrugSafetyBlockComponent,
      ExamSimulatorBlock: ExamSimulatorBlockComponent,
      // Backward-compatible aliases (ROA-02)
      MarkdownBlock: ClinicalSheetBlockComponent,
      DifferentialDiagnosisBlock: SymptomMatcherBlockComponent,
      ClinicalExamBlock: ExamSimulatorBlockComponent,
      InteractiveFlowchartBlock: ExamSimulatorBlockComponent,
    };
    ```
  - **Discriminated Union**: Evaluates `block.component_type || block.block_type`.
  - **Unknown Block Safety**: If a block type is unrecognized, throws formal error in dev or renders a constrained error card without crashing the rest of the layout.
  - **Suspense & Shimmer**: Each block is wrapped in `React.Suspense` with `BlockSkeleton` displaying intrinsic height to prevent Cumulative Layout Shift (CLS).

#### Feature 44: Virtual Windowing Engine ($<30$ Mounted DOM Nodes)
- **Location**: `src/implementations/virtual/VirtualWindowList.tsx` ($\le 250$ lines)
- **Mechanism**:
  - Monograph sections and symptom trees can contain hundreds of nodes.
  - Monitors viewport scroll position via `onScroll` with passive listener and `requestAnimationFrame`.
  - Computes active visible block window: blocks within $\pm 2$ viewport heights ($D_{\text{viewport}} \le 2 \cdot H_{\text{viewport}}$). Maximum active blocks $|V_{\text{active}}| \le 8$.
  - Blocks outside the window are unmounted from the DOM and replaced by empty placeholder `div` elements with fixed heights (`contain-intrinsic-size` / `minHeight`), guaranteeing:
    $$\text{Mounted DOM Nodes} < 30$$
    $$\text{CLS (Cumulative Layout Shift)} = 0.0$$
    $$\text{WebView Memory Overhead} < 32\text{ MB}$$

#### Feature 45: Zero-Copy `med-asset://` Protocol Integration
- **Location**: `src/implementations/ipc/AssetProtocolBridge.ts` ($\le 140$ lines)
- **Mechanism**:
  - Medical images (high-resolution histology, radiography, dermatoscopy) are referenced in SDUI payloads via 64-character SHA-256 hashes.
  - Generates image URL: `<img src="med-asset://${media_sha256}" alt="..." />`.
  - Tauri's custom asset handler intercepts `med-asset://`, memory-maps the WebP file on NVMe via `memmap2`, and streams raw memory pages directly into WebView2 via DirectX shared surface. Zero heap allocations in Python or Rust.
  - React component includes error fallback: if image fails to load (HTTP 404), displays a placeholder icon with retry button.

#### Feature 46: Singleton WebGL Broker (`MAX_ACTIVE_CONTEXTS = 1`, Auto-Recovery)
- **Location**: `src/implementations/webgl/WebGLContextBroker.ts` ($\le 180$ lines) & `Molecule3DViewer.tsx` ($\le 280$ lines)
- **Mechanism**:
  - Chromium limits active WebGL contexts on Intel Iris Xe / HD Graphics. Creating multiple contexts causes `webglcontextlost` crashes.
  - **Single Global Context**: `WebGLContextBroker` enforces `MAX_ACTIVE_CONTEXTS = 1`.
  - **Click-to-Interact**: Default state renders a static 2D SVG / WebP structure diagram. WebGL canvas is mounted ONLY upon explicit user click on `"Esplora Modello 3D"`.
  - **Atomic Eviction**: When a new 3D viewer requests activation, the broker forcibly evicts the previous context by invoking `gl.getExtension('WEBGL_lose_context').loseContext()` and executing the cleanup callback.
  - **Mouse-Leave Eviction**: On `onMouseLeave`, the 3D viewer auto-evicts the WebGL context, returning to static SVG and releasing GPU/UMA memory back to the system.

#### Feature 47: Agentic API Client (`/agent/*`)
- **Location**: `src/implementations/agent/AgenticApiClient.ts` ($\le 220$ lines)
- **Mechanism**:
  - Connects to FastAPI sidecar endpoints on `127.0.0.1:<port>`.
  - **`/agent/health`**: Polls sidecar status, verifying RSS memory and database status.
  - **`/agent/state`**: Periodically syncs full application state (selected tab, active clinical sheet, current diagnosis, patient vitals).
  - **`/agent/execute`**: Exposes action receiver for AI agent automation (e.g., automated execution of `{"action_type": "select_symptom", "payload": {"hpo_id": "HP:0001658"}}`).
  - **`/agent/schema`**: Retrieves OpenAPI schema for introspection.
  - Authenticated via `X-Tauri-IPC-Secret` header stored securely in memory.

#### Feature 48: High-DPI Physical Coordinate Normalization & Hotspot Raycasting
- **Location**: `src/implementations/spatial/RaycastingAlgorithm.ts` ($\le 160$ lines) & `HotspotCanvas.tsx` ($\le 260$ lines)
- **Mechanism**:
  - High-DPI displays (e.g. Surface Pro, 4K monitors) apply scaling factors ($1.5\times, 2.0\times$).
  - Maps physical click coordinates $(X_{\text{screen}}, Y_{\text{screen}})$ to normalized SVG viewBox coordinates $[0.0, 1.0]$:
    $$x_{\text{norm}} = \frac{X_{\text{click}} - X_{\text{bbox\_origin}}}{W_{\text{element}}}$$
    $$y_{\text{norm}} = \frac{Y_{\text{click}} - Y_{\text{bbox\_origin}}}{H_{\text{element}}}$$
  - **Ray-Casting Even-Odd Algorithm**:
    ```typescript
    export function pointInPolygonEvenOdd(
      px: number,
      py: number,
      polygon: [number, number][]
    ): boolean {
      let inside = false;
      const n = polygon.length;
      for (let i = 0, j = n - 1; i < n; j = i++) {
        const [xi, yi] = polygon[i];
        const [xj, yj] = polygon[j];
        const intersect =
          yi > py !== yj > py && px < ((xj - xi) * (py - yi)) / (yj - yi) + xi;
        if (intersect) inside = !inside;
      }
      return inside;
    }
    ```
  - Exact algorithmic parity with backend `tests/conftest.py` and `StatefulDAGEngine`.

---

## 4. Part III: Cross-Boundary Cohesion & Contract Parity Matrix

To prevent the bugs identified by `cohesion_inspector_1`, the contracts between Python FastAPI, Rust Tauri Core, and React Frontend must maintain 100% field parity:

| Domain | Python Pydantic Model (`sdui_models.py`) | Rust Core Trait (`models.rs`) | TypeScript Interface (`sdui.types.ts`) | Status & Parity Check |
|---|---|---|---|---|
| **Clinical Sheet** | `ClinicalSheetBlock` (`sheet_id: str`, `title: str`, `content_markdown: str`, `callouts: List[CalloutItem]`) | N/A (JSON passthrough via HTTP) | `interface ClinicalSheetBlock { block_type: "ClinicalSheetBlock"; sheet_id: string; title: string; content_markdown: string; callouts: CalloutItem[]; }` | Verified Identical |
| **Symptom Matcher** | `SymptomMatcherBlock` (`differential_candidates: list`, `selected_symptoms: list`, `nbq: dict`) | N/A (JSON passthrough via HTTP) | `interface SymptomMatcherBlock { block_type: "SymptomMatcherBlock"; differential_candidates: DifferentialCandidate[]; selected_symptoms: SelectedSymptom[]; nbq: NextBestQuestion \| null; }` | Parity Aligned |
| **Drug Safety** | `DrugSafetyBlock` (`interactions: list`, `cyp_clearance: dict`, `alerts: list`, `egfr: float`) | N/A (JSON passthrough via HTTP) | `interface DrugSafetyBlock { block_type: "DrugSafetyBlock"; interactions: DrugInteraction[]; cyp_clearance: Record<string, number>; alerts: SafetyAlert[]; egfr: number; }` | Discrepancy Resolved (Separated from clinical pharmacology model) |
| **Exam Simulator** | `ExamSimulatorBlock` (`item_type: str`, `item_data: dict`, `fsrs_card_state: dict`) | N/A (JSON passthrough via HTTP) | `interface ExamSimulatorBlock { block_type: "ExamSimulatorBlock"; item_type: "MCQ_4" \| "HOTSPOT" \| "DAG_SCENARIO"; item_data: Record<string, unknown>; fsrs_card_state: FSRSCardState \| null; }` | Verified Identical |
| **Asset Streaming** | `media_sha256` in markdown / block | `asset_protocol.rs` opens `{hash_segment}.webp` via `memmap2` | `<img src="med-asset://{hash}.webp">` or `med-asset://{hash}` | Packager must emit loose `{hash}.webp` files in archive |
| **Sidecar Process** | `server.py` reads `--port` CLI and stdin token | `sidecar.rs` passes `--port` CLI and writes `token\n` to stdin | Invokes HTTP loopback with `X-Tauri-IPC-Secret` | CLI entrypoint `main.py` required in `medclient/sidecar-python/src/` |

---

## 5. Part IV: Step-by-Step Implementation Roadmap for Builder Agents

### Phase 1: Test Suite Remediation (`tests/`)
1. **Refactor `tests/conftest.py`**:
   - Provide authentic fixtures: `app_client`, `real_sqlite_kb`, `real_sqlite_pool`, `hot_swap_controller`.
   - Re-export authentic clinical equations directly from `medclient.sidecar_python.src.implementations`.
2. **Rewrite Tier 1 Feature Tests (8 files)**:
   - Import real classes from `medfactory` and `medclient.sidecar_python`.
   - Eliminate all local dicts and tautological `assert True is True` patterns.
   - Assert on real returns, boundary values, and state transitions.
3. **Rewrite Tier 2 Boundary Tests (4 files)**:
   - Exercise real edge cases against real classes (empty buffers, extreme creatinine, malformed tables).
4. **Rewrite Tier 3 Pairwise Tests (4 files)**:
   - Execute multi-component cross-feature flows (Table extraction $\to$ Zstd compression; Blue/Green swap under concurrent pool reads).
5. **Rewrite Tier 4 Clinical Workloads (4 files)**:
   - Execute multi-stage clinical workflows (STEMI + Clopidogrel + Omeprazole; Sepsis qSOFA triage; Diabetic nephropathy Triple Whammy; MCQ + Hotspot + FSRS).
6. **Update `tests/e2e_runner.py`**:
   - Enforce authentic execution, exit code 0 gate, $<300\text{MB}$ RSS check, and $<50\text{ms}$ latency validation.

### Phase 2: Milestone M4 Frontend Construction (`medclient/frontend-react/`)
1. **Initialize Project Directory**:
   - Create `package.json` with exact pinned versions.
   - Create `vite.config.ts`, `tsconfig.json`, `tailwind.config.js`, `postcss.config.js`, `index.html`.
2. **Author Interfaces (`src/interfaces/`)**:
   - `sdui.types.ts`, `store.types.ts`, `tauri.types.ts`, `webgl.types.ts`, `agentic.types.ts`. All $\le 250$ lines.
3. **Author Base Components (`src/base/`)**:
   - `ErrorBoundary.tsx`, `BlockSkeleton.tsx`, `CalloutBadge.tsx`, `KatexMath.tsx`, `ChemicalDrawer.tsx`. All $\le 220$ lines.
4. **Author Zustand Persistent Store (`src/store/`)**:
   - Slices for `clinicalSheet`, `symptomMatcher`, `drugSafety`, `examSimulator`, `navigation`.
   - Combine in `useAppStore.ts` with DOM retention.
5. **Author Engines (`src/implementations/`)**:
   - `SDUIBlockDispatcher.tsx` with Dual Registry Aliasing.
   - The 4 SDUI blocks: `ClinicalSheetBlock`, `SymptomMatcherBlock`, `DrugSafetyBlock`, `ExamSimulatorBlock`.
   - `VirtualWindowList.tsx` limiting mounted DOM nodes to $<30$.
   - `WebGLContextBroker.ts` and `Molecule3DViewer.tsx` enforcing single context and auto-eviction.
   - `RaycastingAlgorithm.ts` and `HotspotCanvas.tsx` for Even-Odd spatial raycasting.
   - `TauriClient.ts` and `AssetProtocolBridge.ts` for IPC and `med-asset://`.
   - `AgenticApiClient.ts` for AI agent bridge.
6. **Author Application Root (`src/App.tsx`, `src/main.tsx`)**:
   - Wire layout, tabs, persistent DOM views, and global error boundary.

---

## 6. Verification and Acceptance Criteria

1. **Test Suite Remediation Gate**:
   - Running `python tests/e2e_runner.py --tier all` executes 514 authentic tests.
   - `git grep "import medfactory" tests/` and `git grep "from medclient" tests/` return matching imports across all test files.
   - Zero tautological dummy variables (`process_exit_code = 0; assert process_exit_code == 0`) remain.
   - 100% pass rate achieved on authentic production code.
2. **Frontend SDUI & Tauri Gate**:
   - `npm install` installs cleanly with zero dependency version conflicts.
   - `npm run build` (`tsc && vite build`) compiles with zero TypeScript errors and zero warnings.
   - All source files are strictly $\le 300\text{--}450$ lines.
   - SDUI Dual Registry correctly renders both canonical block names and aliases.
   - Virtual windowing verifies $<30$ mounted DOM nodes.
   - WebGL broker strictly prevents more than 1 active 3D context.
   - RSS memory of the WebView remains $< 100\text{ MB}$.
