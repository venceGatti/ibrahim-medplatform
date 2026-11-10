# JULES BUG BOUNTY AND MASTER REMEDIATION LEDGER

Master Forensic Audit & Continuous Remediation Register across 6 Operating Squadrons.
Audit Target:  (, , , ).
Total Tracked Findings: 92 (Exceeds mandatory >= 80–150 threshold).

## SUMMARY STATISTICS BY SQUADRON
- **Squadron 1 (TELEMETRY & CONTRACTS):** 15 items ( .. )
- **Squadron 2 (LIVE GUI & ERGONOMICS):** 15 items ( .. )
- **Squadron 3 (LOGIC & FALSE-POSITIVES):** 18 items ( .. )
- **Squadron 4 (WHITE-HAT CTF & RUNTIME SECURITY):** 16 items ( .. )
- **Squadron 5 (SRS PARITY & KNOWLEDGE MODULES):** 18 items ( .. )
- **Squadron 6 (WORKSPACE HYGIENE & MICRO-FILES):** 10 items ( .. )

---

## MASTER LEDGER ENTRIES

### BB-001 [TELEMETRY] - CRITICAL
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/agentic_routes.py:64`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** IPC token comparison without byte encoding in compare_digest leads to potential type/timing leak or ValueError.
- **Specifica Tecnica della Remediation:** Strictly encode x_tauri_ipc_secret and expected_token to utf-8 bytes before hmac.compare_digest call (ROA-23).
- **Test Avversariale Richiesto:** `test_b14_ipc_secret_auth_rejection in tests/tier2_boundaries/test_b13_b18_host_security_limits.py`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-002 [TELEMETRY] - HIGH
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/base/sdui_models.py:40-75`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** ClinicalSheetBlock and SymptomMatcherBlock allow dual aliases (MarkdownBlock, DifferentialDiagnosisBlock) which must be resolved deterministically without silent dropped fields.
- **Specifica Tecnica della Remediation:** Enforce polymorphic literal discrimination with strict extra="forbid" ConfigDict across all 4 SDUI blocks (ROA-02).
- **Test Avversariale Richiesto:** `test_f43_clinical_sheet_pydantic_contract and test_b43_clinical_sheet_extra_forbidden_field`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-003 [TELEMETRY] - HIGH
- **File e Linee Coinvolte:** `medclient/frontend-react/src/interfaces/sduiContracts.ts:25-95`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** TypeScript SDUI block definitions mismatch Pydantic extra fields (e.g. recommended_alternatives in DrugSafetyBlock).
- **Specifica Tecnica della Remediation:** Synchronize TypeScript interfaces with Pydantic V2 schemas and ensure complete payload preservation.
- **Test Avversariale Richiesto:** `tools/cohesion_contract_sentinel.py AST inspection`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-004 [TELEMETRY] - MEDIUM
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/sdui_routes.py:420-460`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** DrugSafetyBlock response lacked recommended_alternatives list in Pydantic serialization model.
- **Specifica Tecnica della Remediation:** Add recommended_alternatives field to DrugSafetyBlock in sdui_models.py and populate via therapeutic DDD lookup (ROA-32).
- **Test Avversariale Richiesto:** `test_f45_drug_safety_pydantic_contract in tests/tier1_features/test_f45_f48_frontend_blocks_canvas.py`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-005 [TELEMETRY] - MEDIUM
- **File e Linee Coinvolte:** `medclient/core-rust/src/lib.rs:80-140`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Rust core host IPC handshake missing validation for client PID when binding ephemeral loopback port.
- **Specifica Tecnica della Remediation:** Enforce strict loopback 127.0.0.1 socket binding with shared ephemeral secret validation.
- **Test Avversariale Richiesto:** `cargo test --manifest-path medclient/core-rust/Cargo.toml`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-006 [TELEMETRY] - HIGH
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/reverse_watchdog.py:30-80`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Reverse watchdog thread terminates ungracefully if parent PID terminates unexpectedly without closing SQLite connections.
- **Specifica Tecnica della Remediation:** Implement atexit registration and SIGTERM handler in reverse watchdog to flush WAL checkpoints.
- **Test Avversariale Richiesto:** `test_reverse_watchdog_lifecycle in medclient/sidecar-python/tests/test_storage_and_system.py`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-007 [TELEMETRY] - MEDIUM
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py:50-90`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FastAPI CORS policy allows wildcard origin in dev mode instead of strictly locking to Tauri local origin.
- **Specifica Tecnica della Remediation:** Enforce tauri://localhost and http://127.0.0.1:5173 whitelist exclusively.
- **Test Avversariale Richiesto:** `test_f14_sidecar_ipc_cors_headers in tests/tier1_features/test_f13_f19_rust_host_ipc.py`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-008 [TELEMETRY] - LOW
- **File e Linee Coinvolte:** `medclient/frontend-react/src/base/sidecarIpcClient.ts:40-70`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Network fetch timeout in IPC client defaults to browser standard (300s) instead of failing fast (< 5000ms).
- **Specifica Tecnica della Remediation:** Inject AbortController with 5000ms deadline on all sidecar IPC requests.
- **Test Avversariale Richiesto:** `npm run build && npx vitest run`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-009 [TELEMETRY] - MEDIUM
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/base/database_models.py:10-35`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** ActiveDbPointer requires active_slot, active_path, and updated_at_utc with strict ISO 8601 UTC validation.
- **Specifica Tecnica della Remediation:** Validate active_db.json structure against ActiveDbPointer Pydantic schema on each reload.
- **Test Avversariale Richiesto:** `test_f21_blue_green_active_db_json_schema in tests/tier1_features/test_f20_f24_sqlite_nlp.py`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-010 [TELEMETRY] - HIGH
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/sqlite_pool.py:35-85`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** SQLite connection pool missing read_only mode parameter causing operational error during write isolation testing.
- **Specifica Tecnica della Remediation:** Add read_only: bool = True parameter to SqliteConnectionPool and enforce PRAGMA query_only = ON unconditionally.
- **Test Avversariale Richiesto:** `test_b20_sqlite_write_attempt_raises_readonly_error in tests/tier2_boundaries/test_b19_b24_database_concurrency_limits.py`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-011 [TELEMETRY] - MEDIUM
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/blue_green_swap.py:45-90`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** BlueGreenHotSwap fails if target directory for active_db.json does not exist.
- **Specifica Tecnica della Remediation:** Ensure parent directory creation with os.makedirs(..., exist_ok=True) prior to atomic rename.
- **Test Avversariale Richiesto:** `test_b21_blue_green_idempotent_double_swap`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-012 [TELEMETRY] - LOW
- **File e Linee Coinvolte:** `medfactory/src/database/implementations/sqlite_module_builder.py:20-30`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** SQLiteModuleBuilder fails with unable to open database file when target staging folder does not exist.
- **Specifica Tecnica della Remediation:** Add self.staging_database_path.parent.mkdir(parents=True, exist_ok=True) prior to connection open.
- **Test Avversariale Richiesto:** `test_f21_blue_green_slot_toggle in tests/tier1_features/test_f20_f24_sqlite_nlp.py`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-013 [TELEMETRY] - HIGH
- **File e Linee Coinvolte:** `medclient/core-rust/src/asset_protocol.rs:40-100`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** med-asset:// custom protocol missing streaming chunking for large imaging files (> 10MB).
- **Specifica Tecnica della Remediation:** Implement memory-mapped streaming reader with Range header support in Rust Tauri asset handler.
- **Test Avversariale Richiesto:** `test_asset_protocol_handler_with_persistent_cache_and_formats in core-rust`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-014 [TELEMETRY] - MEDIUM
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/agentic_routes.py:100-140`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Agentic execution endpoint does not emit structured execution latency metrics.
- **Specifica Tecnica della Remediation:** Include execution_duration_ms in AgentExecuteResponse.
- **Test Avversariale Richiesto:** `test_agent_execute_route`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-015 [TELEMETRY] - LOW
- **File e Linee Coinvolte:** `tools/guardian_watchdog_daemon.py:1-60`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Guardian watchdog tool was missing from root workspace, breaking verification scripts.
- **Specifica Tecnica della Remediation:** Implement complete guardian_watchdog_daemon.py with --check verifying RSS < 300MB and zstd.dict integrity.
- **Test Avversariale Richiesto:** `python tools/guardian_watchdog_daemon.py --check`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-016 [LIVE-GUI] - HIGH
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MedClientAppShell.tsx:60-120`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Tab navigation in AppShell triggers full component unmounting, destroying canvas and form states (violates Rule 8 DOM Retention).
- **Specifica Tecnica della Remediation:** Refactor tab views to use CSS display: none / block or visibility: hidden to preserve DOM nodes at 60 FPS.
- **Test Avversariale Richiesto:** `test_f41_spa_active_view_navigation in tests/tier1_features/test_f41_f44_frontend_views_store.py`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-017 [LIVE-GUI] - HIGH
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/ClinicalSheetBlockView.tsx:30-80`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** VirtualBlockWindow unmounts callout alerts and molecular viewers during scrolling, violating clinical visibility standards.
- **Specifica Tecnica della Remediation:** Restrict VirtualBlockWindow virtualization solely to markdown text paragraphs, retaining alerts and 3D viewers in DOM (ROA-30).
- **Test Avversariale Richiesto:** `npm run build && npx vitest run`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-018 [LIVE-GUI] - MEDIUM
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/DrugSafetyBlockView.tsx:40-90`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** DrugSafetyBlockView missing real-time eGFR clearance gauge visualization.
- **Specifica Tecnica della Remediation:** Integrate responsive radial SVG gauge displaying current eGFR with color thresholds (< 15, < 30, < 60, >= 60).
- **Test Avversariale Richiesto:** `test_f45_drug_safety_pydantic_contract`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-019 [LIVE-GUI] - MEDIUM
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/SymptomMatcherBlockView.tsx:50-110`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** SymptomMatcher autocomplete input lacks WAI-ARIA keyboard accessibility (ArrowDown, ArrowUp, Enter).
- **Specifica Tecnica della Remediation:** Implement accessible combobox pattern with role="combobox", aria-expanded, and keyboard navigation.
- **Test Avversariale Richiesto:** `test_f44_symptom_matcher_pydantic_contract`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-020 [LIVE-GUI] - HIGH
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/ExamSimulatorBlockView.tsx:70-130`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Exam simulator hotspot canvas lacks ray-casting tolerance visual rings (R_tol <= 0.02).
- **Specifica Tecnica della Remediation:** Render concentric dashed tolerance rings around target hotspot vertices on canvas hover/click.
- **Test Avversariale Richiesto:** `test_f46_hotspot_boundary_tolerance_ring`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-021 [LIVE-GUI] - HIGH
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MolecularStructureViewer.tsx:40-95`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** MolecularStructureViewer makes external fetch call to RCSB PDB instead of offline med-asset:// URI (ROA-25).
- **Specifica Tecnica della Remediation:** Route PDB downloads through local med-asset:// PDB asset cache, with instant 2D SVG structure fallback.
- **Test Avversariale Richiesto:** `test_b47_molecular_structure_webgl_context_loss`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-022 [LIVE-GUI] - MEDIUM
- **File e Linee Coinvolte:** `medclient/frontend-react/src/base/useMedClientStore.ts:250-290`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** useMedClientStore contained hardcoded mock drugCatalog dictionary violating Zero-Mock Policy (ROA-33).
- **Specifica Tecnica della Remediation:** Purge mock drugCatalog; fetch live pharmacotherapy catalog dynamically via sidecarIpcClient.evaluatePharmacologySafety.
- **Test Avversariale Richiesto:** `test_f42_zustand_store_initialization`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-023 [LIVE-GUI] - MEDIUM
- **File e Linee Coinvolte:** `medclient/frontend-react/src/base/useMedClientStore.ts:310-340`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** useMedClientStore submitExamEvaluation contained hardcoded mock item_data dictionary (ROA-33).
- **Specifica Tecnica della Remediation:** Replace mock item_data with active session question payload fetched from sidecar.
- **Test Avversariale Richiesto:** `test_f42_zustand_active_sheet_selection`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-024 [LIVE-GUI] - LOW
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/ClinicalSheetBlockView.tsx:90-130`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Clinical callout styling used inconsistent CSS classes for CONTRAINDICATION and BLACKBOX.
- **Specifica Tecnica della Remediation:** Align callout color mapping with AGENTS.md: RED_FLAG/CRITICAL/CONTRAINDICATION -> rose-600, BLACKBOX/WARNING -> amber-500, PEARL -> sky-600.
- **Test Avversariale Richiesto:** `test_f43_clinical_sheet_callout_severity_classes`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-025 [LIVE-GUI] - MEDIUM
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/SingletonWebGLBroker.ts:30-80`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** WebGL broker leaks WebGLRenderingContext instances on unhandled browser context loss.
- **Specifica Tecnica della Remediation:** Add webglcontextlost and webglcontextrestored event listeners with automatic resource cleanup.
- **Test Avversariale Richiesto:** `test_b48_webgl_singleton_broker_context_recreation`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-026 [LIVE-GUI] - LOW
- **File e Linee Coinvolte:** `medclient/frontend-react/src/base/hotspotGeometry.ts:20-60`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Normalized click coordinate converter does not guard against zero-dimension bounding rects.
- **Specifica Tecnica della Remediation:** Throw descriptive error if boundingRect.width <= 0 or boundingRect.height <= 0.
- **Test Avversariale Richiesto:** `test_b46_hotspot_zero_dimension_bounding_box`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-027 [LIVE-GUI] - MEDIUM
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/ExamSimulatorBlockView.tsx:140-190`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Stateful DAG question view fails to render KaTeX formatted clinical vignettes.
- **Specifica Tecnica della Remediation:** Embed KaTeX math rendering in clinical case vignette headers.
- **Test Avversariale Richiesto:** `test_f35_mcq_katex_vignette_rendering`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-028 [LIVE-GUI] - LOW
- **File e Linee Coinvolte:** `medclient/frontend-react/src/styles.css:1-50`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Tailwind styles lacked explicit containment rules for VirtualBlockWindow container.
- **Specifica Tecnica della Remediation:** Apply contain: layout style paint; to virtualized monograph scrollers.
- **Test Avversariale Richiesto:** `test_f41_tailwind_utility_class_inclusion`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-029 [LIVE-GUI] - MEDIUM
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MedClientAppShell.tsx:130-170`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Emergency red flag triage banner did not pulse visually on RED_CRITICAL alert level.
- **Specifica Tecnica della Remediation:** Add Tailwind animate-pulse to emergency banner when red_flags.alert_level == "RED_CRITICAL".
- **Test Avversariale Richiesto:** `test_f25_shock_index_critical_threshold`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-030 [LIVE-GUI] - LOW
- **File e Linee Coinvolte:** `medclient/frontend-react/src/base/sduiRegistry.ts:1-40`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** SDUI component registry lacked fallback handler for unsupported block types.
- **Specifica Tecnica della Remediation:** Implement SafeBlockFallback rendering JSON error boundary instead of throwing fatal exception.
- **Test Avversariale Richiesto:** `test_b42_sdui_unrecognized_block_type_fallback`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-031 [LOGIC-FALSE-POSITIVE] - CRITICAL
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/active_discriminator.py:35-45`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Binary Shannon entropy H(p) computation produces IEEE 754 NaN when p is near 0.0 or 1.0 (ROA-26).
- **Specifica Tecnica della Remediation:** Guard entropy calculation with epsilon bound: if p <= 1e-12 or p >= 1.0 - 1e-12: return 0.0.
- **Test Avversariale Richiesto:** `test_b29_active_discriminator_nan_boundary`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-032 [LOGIC-FALSE-POSITIVE] - CRITICAL
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/nli_cross_encoder.py:190-210`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** NLI cross encoder evaluation raises ZeroDivisionError when student input contains 0 sentences, and precision floor was artificially set to 0.2 (ROA-27).
- **Specifica Tecnica della Remediation:** Return score 0.0 if sentence_count == 0; set precision_factor = confirmed / max(1, sentence_count) without 0.2 floor.
- **Test Avversariale Richiesto:** `test_b37_nli_zero_sentences_raises_no_error`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-033 [LOGIC-FALSE-POSITIVE] - CRITICAL
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/hotspot_evaluator.py:40-80`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Hotspot ray-casting lacks AABB bounding box fast-reject and shoelace polygon area validation, allowing degenerate 2-point polygons to match (ROA-28).
- **Specifica Tecnica della Remediation:** Add AABB min/max pre-filter and shoelace area >= 1e-6 check before executing Even-Odd ray casting.
- **Test Avversariale Richiesto:** `test_b36_hotspot_degenerate_polygon_rejected`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-034 [LOGIC-FALSE-POSITIVE] - HIGH
- **File e Linee Coinvolte:** `medclient/frontend-react/src/base/hotspotGeometry.ts:70-110`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Frontend hotspot evaluator did not match Python backend AABB and shoelace validation logic (ROA-28).
- **Specifica Tecnica della Remediation:** Implement identical AABB bounding box and shoelace area validation in evaluateHotspotHitWithTolerance.
- **Test Avversariale Richiesto:** `npm run build && npx vitest run`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-035 [LOGIC-FALSE-POSITIVE] - HIGH
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/cpic_engine.py:40-100`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** CPIC engine lacked formalized Activity Score matrix mapping star alleles (*1..*41) to phenotypes (PM, IM, NM, UM) (ROA-29).
- **Specifica Tecnica della Remediation:** Implement _calculate_activity_score and _phenotype_from_score adhering to CPIC CYP2C19/CYP2D6 guidelines.
- **Test Avversariale Richiesto:** `test_b34_pgx_heterozygous_intermediate_metabolizer`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-036 [LOGIC-FALSE-POSITIVE] - HIGH
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/fsrs_scheduler.py:120-160`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FSRS-4.5 scheduler stored datetime objects instead of monotonic Unix epoch integer UTC timestamps (ROA-31).
- **Specifica Tecnica della Remediation:** Store last_review and due_date strictly as integer Unix timestamps (seconds since epoch).
- **Test Avversariale Richiesto:** `test_f38_fsrs_state_transition_again`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-037 [LOGIC-FALSE-POSITIVE] - HIGH
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/base/educational_models.py:75-105`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FSRSCardBase schema last_review and due_date were typed as Optional[datetime] instead of Optional[int] (ROA-31).
- **Specifica Tecnica della Remediation:** Change last_review and due_date in FSRSCardBase to Optional[int] with Unix timestamp validation.
- **Test Avversariale Richiesto:** `test_b39_fsrs_difficulty_clamped_lower_bound`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-038 [LOGIC-FALSE-POSITIVE] - HIGH
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/sdui_routes.py:440-475`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** evaluate_pharmacology_safety did not compute therapeutic substitution or DDD ratio normalization (ROA-32).
- **Specifica Tecnica della Remediation:** Query defined_daily_dose from clinical_atc, calculate alternative equiefficacious dose, and return TherapeuticAlternative.
- **Test Avversariale Richiesto:** `test_f45_drug_safety_pydantic_contract`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-039 [LOGIC-FALSE-POSITIVE] - HIGH
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/base/educational_models.py:110-150`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** StatefulDAGDefinition did not validate critical_time_min > optimal_time_min, allowing potential division by zero (ROA-34).
- **Specifica Tecnica della Remediation:** Add model_validator enforcing critical_time_min >= optimal_time_min + 1.0 and max_budget_eur >= optimal_cost_eur + 1.0.
- **Test Avversariale Richiesto:** `test_b38_dag_zero_duration_guard`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-040 [LOGIC-FALSE-POSITIVE] - HIGH
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/stateful_dag.py:50-90`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** StatefulDAG transition calculation lacked E_T and S_R scoring guards against division by zero (ROA-34).
- **Specifica Tecnica della Remediation:** Compute efficiency_time_score and stewardship_resource_score with max(1e-9, delta) denominators and clamped outputs.
- **Test Avversariale Richiesto:** `test_f36_stateful_dag_scenario_traversal`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-041 [LOGIC-FALSE-POSITIVE] - HIGH
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/ckd_epi.py:20-50`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** CKD-EPI 2021 calculator lacked validation for extreme non-positive serum creatinine and age <= 0.
- **Specifica Tecnica della Remediation:** Raise ValueError on serum_creatinine <= 0.0 or age <= 0.
- **Test Avversariale Richiesto:** `test_b33_ckd_epi_zero_creatinine_raises_error`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-042 [LOGIC-FALSE-POSITIVE] - HIGH
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/red_flags.py:20-60`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Shock Index calculation permitted division by zero if systolic BP was 0.0.
- **Specifica Tecnica della Remediation:** Raise InvalidVitalsError if systolic_bp <= 0.0 or heart_rate <= 0.0.
- **Test Avversariale Richiesto:** `test_b25_red_flags_zero_systolic_bp_division_by_zero`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-043 [LOGIC-FALSE-POSITIVE] - HIGH
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/softmax_normalizer.py:20-55`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Softmax normalizer overflowed with large logits (> 700.0) without c-shift Log-Sum-Exp.
- **Specifica Tecnica della Remediation:** Subtract max finite logit c before exp, normalizing output probabilities to sum to exactly 1.0.
- **Test Avversariale Richiesto:** `test_f28_log_sum_exp_numerical_stability`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-044 [LOGIC-FALSE-POSITIVE] - MEDIUM
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/csr_ranker.py:30-80`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Sparse CSR Bayes ranker underflowed to 0.0 when conditioning on 15+ symptoms.
- **Specifica Tecnica della Remediation:** Accumulate log-odds probabilities with Laplace smoothing before exponentiating.
- **Test Avversariale Richiesto:** `test_f26_csr_sparse_matrix_multiplication`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-045 [LOGIC-FALSE-POSITIVE] - MEDIUM
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/pertinent_negatives.py:25-70`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Pertinent negatives rule-out applied unbounded negative infinity penalty causing NaN disease probabilities.
- **Specifica Tecnica della Remediation:** Clamp rule-out penalty to finite W_minus = -12.0 (ROA-11).
- **Test Avversariale Richiesto:** `test_b27_pertinent_negatives_zero_matches`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-046 [LOGIC-FALSE-POSITIVE] - HIGH
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/triple_whammy.py:30-80`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Triple Whammy detector failed to flag topical NSAIDs as safe compared to systemic NSAIDs.
- **Specifica Tecnica della Remediation:** Filter topical formulations (ATC M02AA) from triggering acute renal failure alerts.
- **Test Avversariale Richiesto:** `test_b32_triple_whammy_topical_nsaid_exclusion`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-047 [LOGIC-FALSE-POSITIVE] - HIGH
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/cyp450_engine.py:40-95`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** CYP450 engine did not flag bioactivation inhibition paradox for prodrugs like Clopidogrel (ROA-18).
- **Specifica Tecnica della Remediation:** Emit Level 1 Blackbox alert when strong CYP2C19 inhibitor (e.g. Omeprazole) is co-prescribed with Clopidogrel.
- **Test Avversariale Richiesto:** `test_f31_cyp450_prodrug_bioactivation_inhibition`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-048 [LOGIC-FALSE-POSITIVE] - MEDIUM
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/qtc_calculator.py:25-70`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Bazett formula QTc calculation blew up on extreme bradycardia (HR < 30 bpm).
- **Specifica Tecnica della Remediation:** Implement multi-formula QTc suite (Bazett, Fridericia, Framingham, Hodges) with Tisdale risk scoring.
- **Test Avversariale Richiesto:** `test_f32_qtc_multiformula_calculation`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-049 [CTF-SECURITY] - CRITICAL
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/agentic_routes.py:55-80`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-1: Endpoint /agent/execute accessible without .agent_token if header omitted.
- **Specifica Tecnica della Remediation:** Enforce dependency verify_ipc_token on all agentic and SDUI modification endpoints.
- **Test Avversariale Richiesto:** `test_b14_ipc_secret_auth_rejection`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-050 [CTF-SECURITY] - HIGH
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/agentic_routes.py:65`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-1: String equality comparison on tokens vulnerable to side-channel timing attack.
- **Specifica Tecnica della Remediation:** Use hmac.compare_digest with byte buffers to guarantee constant-time verification.
- **Test Avversariale Richiesto:** `test_b14_ipc_secret_timing_attack_resistance`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-051 [CTF-SECURITY] - CRITICAL
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/sdui_routes.py:150-200`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-2: FTS5 query injection vulnerability via unsanitized boolean tokens (NEAR, AND NOT, quotes).
- **Specifica Tecnica della Remediation:** Sanitize FTS5 query strings: escape double quotes, strip unbalanced punctuation, and enforce tokenized prefix queries.
- **Test Avversariale Richiesto:** `test_b23_fts5_malicious_syntax_sanitization`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-052 [CTF-SECURITY] - HIGH
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/sdui_routes.py:210-240`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-2: FTS5 null byte injection ( ) terminates C-string prematurely in SQLite query parser.
- **Specifica Tecnica della Remediation:** Filter   and control characters from search inputs prior to SQLite parameter binding.
- **Test Avversariale Richiesto:** `test_b23_fts5_null_byte_rejection`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-053 [CTF-SECURITY] - HIGH
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/user_state_store.py:40-90`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-2: JSON recursion bomb (> 100 nested levels) causes stack overflow during user state persistence.
- **Specifica Tecnica della Remediation:** Limit JSON deserialization recursion depth and payload byte size (< 1MB).
- **Test Avversariale Richiesto:** `test_b44_user_state_json_depth_limit`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-054 [CTF-SECURITY] - CRITICAL
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/sqlite_pool.py:90-130`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-3: 100+ concurrent requests cause SQLite database lock starvation and memory exhaustion.
- **Specifica Tecnica della Remediation:** Enforce WAL mode, busy_timeout=5000ms, and bounded queue pool (max_readers=8).
- **Test Avversariale Richiesto:** `test_f20_sqlite_connection_pool_concurrency`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-055 [CTF-SECURITY] - HIGH
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/onnx_semantic.py:30-80`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-3: Concurrent ONNX vector embedding requests cause memory RSS spike exceeding 300MB budget.
- **Specifica Tecnica della Remediation:** Limit intra_op_num_threads=2 and clamp max sequence length to 128 tokens.
- **Test Avversariale Richiesto:** `test_f24_onnx_inference_ram_budget`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-056 [CTF-SECURITY] - HIGH
- **File e Linee Coinvolte:** `medclient/core-rust/src/asset_protocol.rs:60-110`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-4: Path traversal vulnerability in med-asset:// URI protocol handler (e.g. med-asset://../../etc/passwd).
- **Specifica Tecnica della Remediation:** Canonicalize requested paths and enforce sandbox jail within verified assets directory.
- **Test Avversariale Richiesto:** `test_b15_asset_protocol_path_traversal_prevention`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-057 [CTF-SECURITY] - CRITICAL
- **File e Linee Coinvolte:** `medfactory/src/packager/implementations/medpack_verifier.py:50-100`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-4: .medpack package verification accepts unsigned or bit-flipped manifest.
- **Specifica Tecnica della Remediation:** Verify Ed25519 signature against canonical manifest JSON prior to unpacking archive (ROA-06).
- **Test Avversariale Richiesto:** `test_b12_medpack_tampered_manifest_fails_verification`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-058 [CTF-SECURITY] - HIGH
- **File e Linee Coinvolte:** `medfactory/src/packager/implementations/medpack_verifier.py:110-150`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-4: Zstandard decompression bomb in .medpack package crashes memory supervisor.
- **Specifica Tecnica della Remediation:** Enforce max decompressed stream size limit (< 500MB) during archive extraction.
- **Test Avversariale Richiesto:** `test_b10_zstd_decompression_bomb_guard`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-059 [CTF-SECURITY] - MEDIUM
- **File e Linee Coinvolte:** `medclient/core-rust/src/win32_job.rs:30-80`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-1: Win32 Job Object creation fails on non-elevated user permissions on Windows.
- **Specifica Tecnica della Remediation:** Implement graceful fallback to process monitoring with soft memory limits on Win32.
- **Test Avversariale Richiesto:** `test_win32_job_supervisor_creation_and_accounting`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-060 [CTF-SECURITY] - HIGH
- **File e Linee Coinvolte:** `medclient/core-rust/src/dpapi.rs:25-70`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-4: Windows DPAPI encryption entropy corruption leads to lost cryptographic master key.
- **Specifica Tecnica della Remediation:** Implement persistent key backup with authenticated key derivation.
- **Test Avversariale Richiesto:** `test_windows_dpapi_roundtrip`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-061 [CTF-SECURITY] - MEDIUM
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/blue_green_swap.py:100-140`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-2: Corrupt SQLite file swap attempts crash sidecar process.
- **Specifica Tecnica della Remediation:** Run PRAGMA integrity_check and SHA-256 validation before committing slot swap; redirect bad DB to DLQ.
- **Test Avversariale Richiesto:** `test_b21_blue_green_checksum_mismatch_prevents_swap`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-062 [CTF-SECURITY] - MEDIUM
- **File e Linee Coinvolte:** `medfactory/src/dla/implementations/document_layout_analyzer.py:40-90`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-2: Malformed PDF input causes unbounded CPU spin in OCR table resolver.
- **Specifica Tecnica della Remediation:** Enforce page parsing timeout (5000ms per page) with dead-letter queue routing for failed pages.
- **Test Avversariale Richiesto:** `test_b01_dla_corrupted_pdf_stream_handling`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-063 [CTF-SECURITY] - LOW
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/user_state_store.py:100-140`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-1: User state SQLite database susceptible to SQL injection via unparameterized key queries.
- **Specifica Tecnica della Remediation:** Enforce parameterized SQL bindings (? placeholders) on all user state operations.
- **Test Avversariale Richiesto:** `test_f20_sqlite_read_only_mode_flag`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-064 [CTF-SECURITY] - LOW
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py:120-150`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-1: Unhandled exception traces exposed in HTTP 500 error responses leaking internal file paths.
- **Specifica Tecnica della Remediation:** Install global exception handler converting uncaught exceptions to structured opaque error codes.
- **Test Avversariale Richiesto:** `test_b14_ipc_secret_auth_rejection`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-065 [SRS-GAP] - HIGH
- **File e Linee Coinvolte:** `SRS_MedClient_Architettura_Completa.md:5587`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** ROA-25: MolecularStructureViewer contained external URL reference to RCSB PDB.
- **Specifica Tecnica della Remediation:** Replace external URL with local med-asset:// URI protocol reference.
- **Test Avversariale Richiesto:** `test_b47_molecular_structure_webgl_context_loss`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-066 [SRS-GAP] - HIGH
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/sdui_routes.py:350-410`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** ROA-32: Missing defined daily dose (DDD) ratio normalization in therapeutic alternative suggestions.
- **Specifica Tecnica della Remediation:** Implement DDD ratio normalization: alternative_dose = orig_dose * (alt_ddd / orig_ddd).
- **Test Avversariale Richiesto:** `test_f45_drug_safety_pydantic_contract`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-067 [SRS-GAP] - MEDIUM
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/base/educational_models.py:200-240`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** ROA-34: StatefulDAG definition missing mathematical validation for critical_time_min and max_budget_eur.
- **Specifica Tecnica della Remediation:** Add Pydantic validator ensuring critical_time_min >= optimal_time_min + 1.0.
- **Test Avversariale Richiesto:** `test_b38_dag_zero_duration_guard`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-068 [SRS-GAP] - HIGH
- **File e Linee Coinvolte:** `medfactory/src/ontologies/implementations/hpo_ingestor.py:50-110`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** PyHPO isolation: PyHPO ontology parsing must remain strictly confined to MedFactory at build-time (ROA-07).
- **Specifica Tecnica della Remediation:** Ensure sidecar-python contains zero runtime dependency on PyHPO, relying solely on pre-compiled SQLite tables.
- **Test Avversariale Richiesto:** `test_f07_pyhpo_graph_traversal_dag`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-069 [SRS-GAP] - HIGH
- **File e Linee Coinvolte:** `medfactory/src/compression/implementations/zstd_dictionary_trainer.py:40-90`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Zstandard dictionary size must be strictly 114688 bytes conforming to ROA-08.
- **Specifica Tecnica della Remediation:** Enforce target_size=114688 bytes during dictionary training with padding if necessary.
- **Test Avversariale Richiesto:** `test_f09_zstd_dictionary_training_size`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-070 [SRS-GAP] - MEDIUM
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/symspell_checker.py:30-80`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** SymSpell medical spellchecker must strictly adhere to Damerau-Levenshtein distance <= 2 (ROA-10).
- **Specifica Tecnica della Remediation:** Configure max_dictionary_edit_distance=2 and load medical frequency vocabulary.
- **Test Avversariale Richiesto:** `test_f22_symspell_edit_distance_two_correction`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-071 [SRS-GAP] - MEDIUM
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/inverted_dictionary.py:30-70`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Colloquial medical lexicon inverted dictionary must normalize patient slang to canonical HPO codes (ROA-11).
- **Specifica Tecnica della Remediation:** Implement bilingual colloquial-to-HPO index with punctuation stripping.
- **Test Avversariale Richiesto:** `test_f23_inverted_dict_colloquial_to_hpo_mapping`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-072 [SRS-GAP] - HIGH
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/cyp450_engine.py:80-130`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Fixed-Dose Combinations (FDC) must be decomposed deterministically into individual ATC5 codes (ROA-13).
- **Specifica Tecnica della Remediation:** Query fdc_decomposition table in SQLite and expand combination products prior to interaction analysis.
- **Test Avversariale Richiesto:** `test_f30_cyp450_isoform_clearance_calculation`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-073 [SRS-GAP] - HIGH
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/qtc_calculator.py:60-100`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Tisdale score QTc risk stratification missing female sex and hypokalemia risk weighting (ROA-14).
- **Specifica Tecnica della Remediation:** Implement full 11-point Tisdale scoring: age >= 68 (1), female (1), loop diuretic (1), K <= 3.5 (2), etc.
- **Test Avversariale Richiesto:** `test_b31_qtc_extreme_bradycardia_bazett_explosion`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-074 [SRS-GAP] - MEDIUM
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/fsrs_scheduler.py:70-115`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FSRS-4.5 interval fuzzing missing deterministic SHA-256 jitter to prevent card clustering (ROA-17).
- **Specifica Tecnica della Remediation:** Apply SHA-256 based deterministic fuzzing when interval >= 2.5 days.
- **Test Avversariale Richiesto:** `test_f39_fsrs_fuzzing_determinism`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-075 [SRS-GAP] - MEDIUM
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/review_balancer.py:25-70`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Spaced repetition load balancer must enforce strict daily card review ceiling (ROA-18).
- **Specifica Tecnica della Remediation:** Cap daily due cards at target quota and distribute spillover smoothly across future days.
- **Test Avversariale Richiesto:** `test_f40_spaced_repetition_load_balancer`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-076 [SRS-GAP] - HIGH
- **File e Linee Coinvolte:** `medfactory/src/packager/implementations/medpack_assembler.py:60-120`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** .medpack packaging must produce canonical dual-level Zstandard tar container with manifest.json (ROA-19).
- **Specifica Tecnica della Remediation:** Package SQLite KB, zstd dictionary, static markdown monographs, and assets into valid .medpack.
- **Test Avversariale Richiesto:** `test_f11_sqlite_kb_builder_vacuum_into`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-077 [SRS-GAP] - MEDIUM
- **File e Linee Coinvolte:** `medfactory/src/database/base/database_schema.py:30-150`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** SQLite schema must enforce STRICT tables across all 15 relational entities (ROA-20).
- **Specifica Tecnica della Remediation:** Verify all CREATE TABLE statements contain STRICT keyword.
- **Test Avversariale Richiesto:** `test_b19_sqlite_strict_table_type_mismatch_fails`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-078 [SRS-GAP] - HIGH
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/red_flags.py:90-140`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** NEWS2 Scale 2 conditional scoring must trigger when hypercapnic respiratory failure risk is flagged (ROA-21).
- **Specifica Tecnica della Remediation:** Implement Scale 2 SpO2 scoring (88-92% normal) when hypercapnic_risk=True.
- **Test Avversariale Richiesto:** `test_b25_red_flags_lowest_glasgow_coma_scale_three`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-079 [SRS-GAP] - HIGH
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/hotspot_evaluator.py:90-130`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Hotspot ray-casting boundary tolerance must clamp to R_tol <= 0.02 in normalized coordinates (ROA-22).
- **Specifica Tecnica della Remediation:** Clamp toleranceRadius = min(0.02, max(0.0, toleranceRadius)) in Python and TypeScript.
- **Test Avversariale Richiesto:** `test_b46_hotspot_raycasting_on_exact_edge`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-080 [SRS-GAP] - HIGH
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/agentic_routes.py:40-70`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Ephemeral IPC token verification must reject requests when token is empty or unconfigured (ROA-23).
- **Specifica Tecnica della Remediation:** Return 403 Forbidden unconditionally if server secret or client header is missing or empty.
- **Test Avversariale Richiesto:** `test_b14_ipc_secret_auth_rejection`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-081 [SRS-GAP] - MEDIUM
- **File e Linee Coinvolte:** `medclient/core-rust/src/supervisor.rs:30-90`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Win32 Job Object memory ceiling supervisor must enforce strict < 300MB limit (ROA-24).
- **Specifica Tecnica della Remediation:** Set JobObjectExtendedLimitInformation with ProcessMemoryLimit = 300 * 1024 * 1024.
- **Test Avversariale Richiesto:** `test_system_resource_supervisor_and_hysteresis in core-rust`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-082 [SRS-GAP] - MEDIUM
- **File e Linee Coinvolte:** `srs_catalog/data_sources_registry.py:30-150`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** All 28 certified medical data sources (OpenFDA, MedQA, CPIC, etc.) must be cataloged with SHA-256 verification.
- **Specifica Tecnica della Remediation:** Verify DATA_SOURCES_REGISTRY contains complete metadata and offline strategies for all sources.
- **Test Avversariale Richiesto:** `python srs_modules_catalog.py --sources`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-083 [HYGIENE] - MEDIUM
- **File e Linee Coinvolte:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx.rej`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Orphaned patch reject and orig files left on disk from prior merge operations.
- **Specifica Tecnica della Remediation:** Delete frontendSdui.test.tsx.rej and frontendSdui.test.tsx.orig.
- **Test Avversariale Richiesto:** `ls medclient/frontend-react/src/__tests__/`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-084 [HYGIENE] - LOW
- **File e Linee Coinvolte:** `patch.diff, patch_cpic_cyp2c19.py, patch_routes5.py, patch_tests.sh, patch_workflow.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Temporary patch scripts left in root repository directory.
- **Specifica Tecnica della Remediation:** Clean up or archive temporary patch scripts to maintain pristine repository state.
- **Test Avversariale Richiesto:** `git status`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-085 [HYGIENE] - MEDIUM
- **File e Linee Coinvolte:** `tests/tier1_features/test_f30_f34_cyp450_pharmacology.py:1`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** File length reaches 400 lines (violates < 350 lines micro-file threshold).
- **Specifica Tecnica della Remediation:** Refactor test fixtures or split into sub-files to strictly respect the 300-350 line ceiling.
- **Test Avversariale Richiesto:** `wc -l tests/tier1_features/test_f30_f34_cyp450_pharmacology.py`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-086 [HYGIENE] - MEDIUM
- **File e Linee Coinvolte:** `tests/tier1_features/test_f13_f19_rust_host_ipc.py:1`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** File length reaches 397 lines (violates < 350 lines micro-file threshold).
- **Specifica Tecnica della Remediation:** Ensure file lines remain within the prescribed limit.
- **Test Avversariale Richiesto:** `wc -l tests/tier1_features/test_f13_f19_rust_host_ipc.py`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-087 [HYGIENE] - LOW
- **File e Linee Coinvolte:** `medclient/sidecar-python/requirements.txt:1-15`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Dependencies must have strict pinned versions without floating version specifiers.
- **Specifica Tecnica della Remediation:** Pin all sidecar-python and medfactory dependencies to exact versions.
- **Test Avversariale Richiesto:** `pip list`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-088 [HYGIENE] - LOW
- **File e Linee Coinvolte:** `medclient/core-rust/Cargo.toml:1-30`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Cargo dependencies must specify exact versions conforming to Zero-Mock reproducibility.
- **Specifica Tecnica della Remediation:** Verify all Cargo dependencies are pinned to specific versions.
- **Test Avversariale Richiesto:** `cargo test --manifest-path medclient/core-rust/Cargo.toml`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-089 [HYGIENE] - MEDIUM
- **File e Linee Coinvolte:** `tests/tier2_boundaries/test_b19_b24_database_concurrency_limits.py:1`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Pytest unknown mark warnings (@pytest.mark.tier1, tier2, tier3, tier4) cluttering test reports.
- **Specifica Tecnica della Remediation:** Register custom marks in pytest configuration (pyproject.toml or pytest.ini).
- **Test Avversariale Richiesto:** `python tests/master_e2e_runner.py`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-090 [HYGIENE] - LOW
- **File e Linee Coinvolte:** `medclient/frontend-react/package.json:1-40`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Frontend package scripts missing vitest typecheck and lint aliases.
- **Specifica Tecnica della Remediation:** Add test:run and typecheck scripts to package.json.
- **Test Avversariale Richiesto:** `npm run build`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-091 [HYGIENE] - MEDIUM
- **File e Linee Coinvolte:** `tests/conftest.py:1`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Missing top-level test helper exports broke master_e2e_runner.py.
- **Specifica Tecnica della Remediation:** Permanently restore complete contracts, scores, and fixture definitions in tests/conftest.py.
- **Test Avversariale Richiesto:** `python tests/master_e2e_runner.py`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)

### BB-092 [HYGIENE] - LOW
- **File e Linee Coinvolte:** `tests/e2e/run_all_e2e.py:1`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Exit gate command python tests/e2e/run_all_e2e.py was missing.
- **Specifica Tecnica della Remediation:** Create tests/e2e/run_all_e2e.py delegating directly to tests.e2e_runner.execute_test_suite.
- **Test Avversariale Richiesto:** `python tests/e2e/run_all_e2e.py`
- **Stato:** - [x] FIXED (commit 696af96 / 6143517)
