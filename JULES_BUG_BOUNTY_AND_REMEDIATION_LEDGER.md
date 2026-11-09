# JULES BUG BOUNTY AND REMEDIATION MASTER LEDGER

> Master forensic audit register, security testing proof-of-concepts, anti-false-positive validations, and architectural remediation checklist covering MedPlatform (Rust host, Python sidecar, React frontend, MedFactory packager).

## LEDGER SUMMARY
- **Total Discovered & Audited Items:** 88
- **Status:** 100% Fully Remediated & Certified
- **Coverage:** 6 Forensic Squadrons (Telemetry, Live GUI, Clinical False-Positive, White-Hat CTF, SRS/ROA Gaps, Workspace Hygiene)

---

### Item BB-001: [TELEMETRY]
- **Squadrone / Categoria:** `TELEMETRY`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/main.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Launching sidecar without MEDCLIENT_IPC_TOKEN environment variable or stdin piped token allowed unbound or crashing execution.
- **Specifica Tecnica della Remediation:** Enforce strict read_stdin_ipc_token() with immediate non-zero exit and explicit error when token is missing.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f13_f19_rust_host_ipc.py::test_sidecar_argument_ordering`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-002: [TELEMETRY]
- **Squadrone / Categoria:** `TELEMETRY`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Incoming HTTP requests with mismatched or spoofed X-Tauri-IPC-Secret header previously returned generic 500 error instead of strict 403 Forbidden.
- **Specifica Tecnica della Remediation:** Add IPCTokenMiddleware with constant-time hmac.compare_digest checking against app.state.ipc_token.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f13_f19_rust_host_ipc.py::test_ipc_authentication_handshake`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-003: [TELEMETRY]
- **Squadrone / Categoria:** `TELEMETRY`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/agentic_routes.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** GET /agent/health endpoint exposed unauthenticated telemetry if middleware path exclusions were too permissive.
- **Specifica Tecnica della Remediation:** Require authentication header on /agent/health, /agent/state, /agent/execute, and /agent/schema.
- **Test Avversariale Richiesto:** `medclient/sidecar-python/tests/test_storage_and_system.py::test_agentic_api_endpoints`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-004: [TELEMETRY]
- **Squadrone / Categoria:** `TELEMETRY`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/reverse_watchdog.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Reverse watchdog process polling parent PID did not handle POSIX vs Win32 platform branch gracefully during rapid shutdown.
- **Specifica Tecnica della Remediation:** Implement dual-mode watchdog using psutil.pid_exists() on POSIX and Win32 Job Object lifecycle signals.
- **Test Avversariale Richiesto:** `medclient/sidecar-python/tests/test_storage_and_system.py::test_reverse_watchdog_lifecycle`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-005: [TELEMETRY]
- **Squadrone / Categoria:** `TELEMETRY`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/core-rust/src/resource_monitor.rs`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Process RSS memory accounting lacked hysteresis thresholding, causing rapid threshold flapping near 300MB ceiling.
- **Specifica Tecnica della Remediation:** Implement high/low watermark hysteresis (warning at 250MB, critical termination at 300MB).
- **Test Avversariale Richiesto:** `medclient/core-rust/src/lib.rs::tests::test_system_resource_supervisor_and_hysteresis`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-006: [TELEMETRY]
- **Squadrone / Categoria:** `TELEMETRY`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/core-rust/src/asset_handler.rs`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Custom med-asset:// protocol did not set Content-Type header on WebP and SVG asset streams.
- **Specifica Tecnica della Remediation:** Map URI mime types explicitly: .svg -> image/svg+xml, .webp -> image/webp, .bin -> application/octet-stream.
- **Test Avversariale Richiesto:** `medclient/core-rust/src/lib.rs::tests::test_asset_protocol_handler_with_persistent_cache_and_formats`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-007: [TELEMETRY]
- **Squadrone / Categoria:** `TELEMETRY`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/core-rust/src/process_guard.rs`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Win32 Job Object creation failed silently on non-Windows test runners without mock bypasses.
- **Specifica Tecnica della Remediation:** Implement cfg-conditional platform compilation with authentic POSIX process supervisor fallback.
- **Test Avversariale Richiesto:** `medclient/core-rust/src/lib.rs::tests::test_win32_job_supervisor_creation_and_accounting`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-008: [TELEMETRY]
- **Squadrone / Categoria:** `TELEMETRY`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/core-rust/src/dpapi.rs`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** DPAPI entropy byte vector roundtrip was susceptible to length truncation under arbitrary entropy buffers.
- **Specifica Tecnica della Remediation:** Enforce length validation and deterministic byte roundtrip encoding in DPAPI storage module.
- **Test Avversariale Richiesto:** `medclient/core-rust/src/lib.rs::tests::test_windows_dpapi_roundtrip`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-009: [TELEMETRY]
- **Squadrone / Categoria:** `TELEMETRY`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `tools/cohesion_contract_sentinel.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** New endpoint responses lacked automated parity checks against frontend TypeScript models.
- **Specifica Tecnica della Remediation:** Integrate AST scanner parsing FastAPI route response_model annotations and matching with TypeScript interfaces.
- **Test Avversariale Richiesto:** `tools/cohesion_contract_sentinel.py`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-010: [TELEMETRY]
- **Squadrone / Categoria:** `TELEMETRY`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/base/agentic_models.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Agentic health and state models contained unvalidated string types for uptime and memory telemetry.
- **Specifica Tecnica della Remediation:** Enforce strict float typing with Ge(0.0) constraint for uptime_seconds and rss_mb.
- **Test Avversariale Richiesto:** `medclient/sidecar-python/tests/test_storage_and_system.py::test_agentic_api_endpoints`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-011: [TELEMETRY]
- **Squadrone / Categoria:** `TELEMETRY`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/core-rust/src/lib.rs`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Mmap LRU cache eviction policy did not release unmapped pages under high memory pressure.
- **Specifica Tecnica della Remediation:** Add BoundedMmapLruCache with capacity tracking and explicit munmap / file handle drop.
- **Test Avversariale Richiesto:** `medclient/core-rust/src/lib.rs::tests::test_bounded_mmap_lru_cache_eviction`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-012: [TELEMETRY]
- **Squadrone / Categoria:** `TELEMETRY`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/core-rust/src/lib.rs`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Jemalloc background thread profiling configuration was inactive on release targets.
- **Specifica Tecnica della Remediation:** Configure jemalloc dirty decay and background purging flags in memory tuner config.
- **Test Avversariale Richiesto:** `medclient/core-rust/src/lib.rs::tests::test_jemalloc_memory_tuner_config`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-013: [TELEMETRY]
- **Squadrone / Categoria:** `TELEMETRY`
- **Severità:** `LOW`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** CORS configuration on loopback permitted wildcard origin headers on agent routes.
- **Specifica Tecnica della Remediation:** Restrict allow_origins strictly to ['http://localhost:5173', 'http://127.0.0.1:5173', 'tauri://localhost'].
- **Test Avversariale Richiesto:** `medclient/sidecar-python/tests/test_storage_and_system.py::test_agentic_api_endpoints`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-014: [TELEMETRY]
- **Squadrone / Categoria:** `TELEMETRY`
- **Severità:** `LOW`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Uvicorn access logger created disk I/O overhead during high-frequency telemetry polling.
- **Specifica Tecnica della Remediation:** Set access_log=False and forward structured audit logs through internal memory queue.
- **Test Avversariale Richiesto:** `tests/benchmarks/test_m5_production_sla.py`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-015: [TELEMETRY]
- **Squadrone / Categoria:** `TELEMETRY`
- **Severità:** `LOW`
- **File e Linee Coinvolte:** `tools/guardian_watchdog_daemon.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Watchdog script lacked automated exit code propagation when RSS exceeded 300MB limit.
- **Specifica Tecnica della Remediation:** Add sys.exit(1) on threshold breach with human-readable diagnostic output.
- **Test Avversariale Richiesto:** `tools/guardian_watchdog_daemon.py --check`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-016: [LIVE-GUI]
- **Squadrone / Categoria:** `LIVE-GUI`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MedClientAppShell.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Tab switching unmounted inactive components from the DOM, losing canvas states and scroll positions.
- **Specifica Tecnica della Remediation:** Implement Rule 8 DOM retention using CSS visibility classes (block opacity-100 vs hidden opacity-0).
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-017: [LIVE-GUI]
- **Squadrone / Categoria:** `LIVE-GUI`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/ClinicalSheetBlockView.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Clinical callout severity tags lacked high-contrast styling for EXAM_TIP and CONTRAINDICATION.
- **Specifica Tecnica della Remediation:** Map CONTRAINDICATION to rose-600 border/text and EXAM_TIP to sky-600 styling.
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-018: [LIVE-GUI]
- **Squadrone / Categoria:** `LIVE-GUI`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/VirtualBlockWindow.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** VirtualBlockWindow allowed mounting > 50 DOM nodes simultaneously during deep scrolling lists.
- **Specifica Tecnica della Remediation:** Enforce strict window slicing: mount max 30-50 nodes with contain: layout style paint.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b46_b48_canvas_webgl_boundaries.py::test_b47_virtual_dom_zero_row_height_division_guard`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-019: [LIVE-GUI]
- **Squadrone / Categoria:** `LIVE-GUI`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/ExamSimulatorBlockView.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Hotspot canvas coordinate clicks lacked normalized bounding box clamping on [0.0, 1.0]^2.
- **Specifica Tecnica della Remediation:** Clamp click coordinates (Math.max(0, Math.min(1, x))) and render feedback ring with R_tol <= 0.02.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b46_b48_canvas_webgl_boundaries.py::test_b46_exam_simulator_complex_nested_item_data`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-020: [LIVE-GUI]
- **Squadrone / Categoria:** `LIVE-GUI`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/DrugSafetyBlockView.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Real-time eGFR gauge did not recalculate dynamically when age or serum creatinine inputs changed.
- **Specifica Tecnica della Remediation:** Bind controlled inputs to local state and trigger automatic eGFR recalculation with debounce.
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-021: [LIVE-GUI]
- **Squadrone / Categoria:** `LIVE-GUI`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/SymptomMatcherBlockView.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Emergency critical red flag banner was invisible when shock index exceeded 1.0 without active triage telemetry.
- **Specifica Tecnica della Remediation:** Render emergency critical alert banner immediately upon active red flag trigger.
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-022: [LIVE-GUI]
- **Squadrone / Categoria:** `LIVE-GUI`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MolecularStructureViewer.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** 3D WebGL viewer attempted WebGL context initialization before SVG 2D fallback was rendered.
- **Specifica Tecnica della Remediation:** Render instant 2D SVG fallback before asynchronously requesting WebGL Singleton broker context.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b46_b48_canvas_webgl_boundaries.py::test_b48_webgl_context_cleanup_on_unmount`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-023: [LIVE-GUI]
- **Squadrone / Categoria:** `LIVE-GUI`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/SymptomMatcherBlockView.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** SymSpell HPO autocomplete dropdown lacked keyboard accessibility (ArrowDown, ArrowUp, Enter).
- **Specifica Tecnica della Remediation:** Implement WAI-ARIA 1.2 compliant keyboard navigation for symptom suggestions.
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-024: [LIVE-GUI]
- **Squadrone / Categoria:** `LIVE-GUI`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/ExamSimulatorBlockView.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FSRS spaced repetition rating buttons (Again, Hard, Good, Easy) lacked visual distinction of grade weights.
- **Specifica Tecnica della Remediation:** Apply color coding: Again (red), Hard (amber), Good (sky), Easy (emerald).
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-025: [LIVE-GUI]
- **Squadrone / Categoria:** `LIVE-GUI`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/DrugSafetyBlockView.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Triple Whammy warning lacked explanation of hemodynamic mechanism (afferent arteriole + efferent arteriole).
- **Specifica Tecnica della Remediation:** Include clear physiological breakdown explaining ACEi/ARB efferent dilation + NSAID afferent constriction.
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-026: [LIVE-GUI]
- **Squadrone / Categoria:** `LIVE-GUI`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/ClinicalSheetBlockView.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Callout entries with markdown body failed to render lists and bold tokens properly in plain text mode.
- **Specifica Tecnica della Remediation:** Sanitize and format callout content with typography helper classes.
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-027: [LIVE-GUI]
- **Squadrone / Categoria:** `LIVE-GUI`
- **Severità:** `LOW`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MedClientAppShell.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** IPC connection badge remained grey even when backend was active if sidecar status was healthy.
- **Specifica Tecnica della Remediation:** Bind badge status color to useMedClientStore ipcConnected boolean flag.
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-028: [LIVE-GUI]
- **Squadrone / Categoria:** `LIVE-GUI`
- **Severità:** `LOW`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/ExamSimulatorBlockView.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Exam mode switch between MCQ, Hotspot, and NLI reset answered state unexpectedly.
- **Specifica Tecnica della Remediation:** Preserve active answered state in exam simulator view across mode switching.
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-029: [LIVE-GUI]
- **Squadrone / Categoria:** `LIVE-GUI`
- **Severità:** `LOW`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/SymptomMatcherBlockView.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Differential radar chart SVG threw NaN attribute warnings when candidate probability vector was empty.
- **Specifica Tecnica della Remediation:** Guard radar chart rendering with fallback empty polygon path when candidates array is empty.
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-030: [LIVE-GUI]
- **Squadrone / Categoria:** `LIVE-GUI`
- **Severità:** `LOW`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/styles.css`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Tailwind utility containment classes were missing from default stylesheet.
- **Specifica Tecnica della Remediation:** Add contain-layout, contain-paint, and contain-style CSS classes in styles.css.
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-031: [LOGIC-FALSE-POSITIVE]
- **Squadrone / Categoria:** `LOGIC-FALSE-POSITIVE`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/red_flags.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Systolic blood pressure <= 0 resulted in ZeroDivisionError instead of raising ValueError or handling shock index.
- **Specifica Tecnica della Remediation:** Validate systolic BP strictly > 0 before division, clamping shock index gracefully.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b25_b29_diagnostic_numerical_limits.py::test_b25_shock_index_zero_division`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-032: [LOGIC-FALSE-POSITIVE]
- **Squadrone / Categoria:** `LOGIC-FALSE-POSITIVE`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/ckd_epi.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Serum creatinine values <= 0 caused log(0) domain error in CKD-EPI 2021 race-free equation.
- **Specifica Tecnica della Remediation:** Enforce serum creatinine clamping: minimum 0.1 mg/dL to prevent math domain error.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b30_b34_pharma_interaction_limits.py::test_b32_ckd_epi_extreme_creatinine_bounds`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-033: [LOGIC-FALSE-POSITIVE]
- **Squadrone / Categoria:** `LOGIC-FALSE-POSITIVE`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/cyp450_engine.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Clopidogrel + Omeprazole co-administration failed to trigger Blackbox Level 1 warning if listed in reverse order.
- **Specifica Tecnica della Remediation:** Normalize substance pairs bidirectionally in interaction matrix lookup.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f30_f34_cyp450_pharmacology.py::test_f30_clopidogrel_omeprazole_blackbox`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-034: [LOGIC-FALSE-POSITIVE]
- **Squadrone / Categoria:** `LOGIC-FALSE-POSITIVE`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/softmax_normalizer.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Log-odds vectors with values exceeding +709 caused floating-point overflow in naive softmax math.exp().
- **Specifica Tecnica della Remediation:** Implement Log-Sum-Exp subtract-max trick ensuring numerically stable normalization.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b25_b29_diagnostic_numerical_limits.py::test_b28_log_sum_exp_underflow_overflow`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-035: [LOGIC-FALSE-POSITIVE]
- **Squadrone / Categoria:** `LOGIC-FALSE-POSITIVE`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/fsrs_scheduler.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Zero elapsed days (same-day review) caused negative or zero stability recalculation in FSRS v4.
- **Specifica Tecnica della Remediation:** Enforce minimum elapsed days floor (delta_t >= 0.0) and monotonic stability growth on grade >= 3.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b35_b41_edu_fsrs_boundaries.py::test_b38_fsrs_monotonic_stability`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-036: [LOGIC-FALSE-POSITIVE]
- **Squadrone / Categoria:** `LOGIC-FALSE-POSITIVE`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/csr_ranker.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Sparse CSR matrix multiplication produced non-normalized probability sums (< 0.999 or > 1.001).
- **Specifica Tecnica della Remediation:** Normalize posterior score distribution using stable softmax after log-odds accumulation.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f25_f27_log_odds_ranking.py::test_f25_log_odds_ranking_posterior_sum`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-037: [LOGIC-FALSE-POSITIVE]
- **Squadrone / Categoria:** `LOGIC-FALSE-POSITIVE`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/qtc_calculator.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Heart rate < 30 bpm or > 220 bpm caused extreme artifactual QTc values in Bazett's square root formula.
- **Specifica Tecnica della Remediation:** Compute Fridericia (cube-root), Framingham, and Hodges alongside Bazett with physiological warnings.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b30_b34_pharma_interaction_limits.py::test_b31_qtc_extreme_heart_rate`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-038: [LOGIC-FALSE-POSITIVE]
- **Squadrone / Categoria:** `LOGIC-FALSE-POSITIVE`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/triple_whammy.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** ACE inhibitors, ARBs, and Direct Renin Inhibitors were not unified under single RAS blocker classification.
- **Specifica Tecnica della Remediation:** Expand RAS blocker category matching to include ACEi (C09A), ARB (C09C), and Aliskiren (C09X).
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f30_f34_cyp450_pharmacology.py::test_f32_triple_whammy_identification`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-039: [LOGIC-FALSE-POSITIVE]
- **Squadrone / Categoria:** `LOGIC-FALSE-POSITIVE`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/red_flags.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** qSOFA calculation counted altered mentation when GCS was 15 and AVPU was 'A'.
- **Specifica Tecnica della Remediation:** Strictly score altered mentation only when GCS < 15 or AVPU is in ('V', 'P', 'U').
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f28_f29_emergency_red_flags.py::test_f28_qsofa_altered_mentation`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-040: [LOGIC-FALSE-POSITIVE]
- **Squadrone / Categoria:** `LOGIC-FALSE-POSITIVE`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/pertinent_negatives.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Pertinent negative downweighting used unbound negative penalties leading to -Infinity logits.
- **Specifica Tecnica della Remediation:** Bound penalty weight to finite range: W_negative = -12.0 maximum downweight.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f25_f27_log_odds_ranking.py::test_f26_pertinent_negatives_downweight`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-041: [LOGIC-FALSE-POSITIVE]
- **Squadrone / Categoria:** `LOGIC-FALSE-POSITIVE`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/cpic_engine.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** CYP2D6 ultrarapid metabolizer phenotype (*1/*1xN) did not trigger codeine toxic morphine alert.
- **Specifica Tecnica della Remediation:** Implement CPIC Level 1A recommendation alerting codeine contraindication in CYP2D6 UM patients.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f30_f34_cyp450_pharmacology.py::test_f34_cpic_guideline_mapping`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-042: [LOGIC-FALSE-POSITIVE]
- **Squadrone / Categoria:** `LOGIC-FALSE-POSITIVE`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/active_discriminator.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Next Best Question selection returned identical symptom when top two candidates shared features.
- **Specifica Tecnica della Remediation:** Maximize information gain H(D) - H(D|f) selecting features that discriminate top-ranking hypotheses.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f25_f27_log_odds_ranking.py::test_f27_next_best_question_information_gain`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-043: [LOGIC-FALSE-POSITIVE]
- **Squadrone / Categoria:** `LOGIC-FALSE-POSITIVE`
- **Severità:** `LOW`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/hotspot_evaluator.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Point-in-polygon ray-casting algorithm failed on edge vertices due to strict inequality in y-bounds.
- **Specifica Tecnica della Remediation:** Use authoritative Even-Odd ray-casting test handling boundary ray tangency correctly.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f35_f37_educational_cards_nli.py::test_f36_hotspot_ray_casting`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-044: [LOGIC-FALSE-POSITIVE]
- **Squadrone / Categoria:** `LOGIC-FALSE-POSITIVE`
- **Severità:** `LOW`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/review_balancer.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Review balancer exceeded daily card limit during backlog spikes, accelerating cognitive fatigue.
- **Specifica Tecnica della Remediation:** Enforce strict daily maximum cap on new and review cards per study session.
- **Test Avversariale Richiesto:** `medclient/sidecar-python/tests/test_educational_and_sdui.py::test_review_load_balancer`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item BB-045: [LOGIC-FALSE-POSITIVE]
- **Squadrone / Categoria:** `LOGIC-FALSE-POSITIVE`
- **Severità:** `LOW`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/nli_cross_encoder.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Cross-encoder rationale score evaluated empty student answer strings with non-zero similarity.
- **Specifica Tecnica della Remediation:** Return 0.0 rationale score immediately when answer input string is empty or whitespace.
- **Test Avversariale Richiesto:** `medclient/sidecar-python/tests/test_educational_and_sdui.py::test_nli_cross_encoder_scoring`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item CTF-001: [CTF-SECURITY]
- **Squadrone / Categoria:** `CTF-SECURITY`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-1: Forged or truncated IPC secret tokens tested via timing attacks.
- **Specifica Tecnica della Remediation:** Use hmac.compare_digest for all token comparisons preventing timing side-channel leaks.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b13_b18_host_security_limits.py::test_b13_ipc_token_tampering`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item CTF-002: [CTF-SECURITY]
- **Squadrone / Categoria:** `CTF-SECURITY`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/sdui_routes.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-2: SQLite FTS5 injection using malformed boolean operators (NEAR, AND NOT) or unclosed quotes.
- **Specifica Tecnica della Remediation:** Sanitize and escape all user search queries before passing to FTS5 MATCH clause.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b19_b24_database_concurrency_limits.py::test_b20_fts5_syntax_injection`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item CTF-003: [CTF-SECURITY]
- **Squadrone / Categoria:** `CTF-SECURITY`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medfactory/src/packager/implementations/medpack_verifier.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-4: Bit-flipping attack on compressed .medpack payloads passing verification.
- **Specifica Tecnica della Remediation:** Verify Ed25519 digital signature over full manifest hash before attempting archive decompression.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f10_f12_zstd_sqlite_packaging.py::test_f12_medpack_signature_verification`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item CTF-004: [CTF-SECURITY]
- **Squadrone / Categoria:** `CTF-SECURITY`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/sqlite_pool.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-3: Concurrency torture with 100+ simultaneous readers causing database locked errors.
- **Specifica Tecnica della Remediation:** Enable PRAGMA journal_mode=WAL and PRAGMA busy_timeout=5000 with connection pooling.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b19_b24_database_concurrency_limits.py::test_b19_wal_concurrency_stress`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item CTF-005: [CTF-SECURITY]
- **Squadrone / Categoria:** `CTF-SECURITY`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/core-rust/src/asset_handler.rs`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-4: Path traversal exploit in med-asset:// URI (e.g., med-asset://../../etc/passwd).
- **Specifica Tecnica della Remediation:** Enforce canonical path resolution and restrict asset root directory with sandboxed boundaries.
- **Test Avversariale Richiesto:** `medclient/core-rust/src/lib.rs::tests::test_asset_protocol_handler_with_persistent_cache_and_formats`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item CTF-006: [CTF-SECURITY]
- **Squadrone / Categoria:** `CTF-SECURITY`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medfactory/src/packager/implementations/medpack_assembler.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-4: Hardcoded Ed25519 private key seed detected in package builder.
- **Specifica Tecnica della Remediation:** Generate cryptographically secure Ed25519 keypair dynamically with os.urandom(32).
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f10_f12_zstd_sqlite_packaging.py::test_f11_ed25519_key_generation`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item CTF-007: [CTF-SECURITY]
- **Squadrone / Categoria:** `CTF-SECURITY`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-1: Replay attack using captured expired IPC tokens across sidecar restarts.
- **Specifica Tecnica della Remediation:** Generate fresh ephemeral 128-bit IPC token per sidecar process spawn; invalidate old tokens on exit.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b13_b18_host_security_limits.py::test_b14_ephemeral_token_rotation`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item CTF-008: [CTF-SECURITY]
- **Squadrone / Categoria:** `CTF-SECURITY`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/sdui_routes.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-2: Deeply nested JSON payload (100+ levels) causing recursion stack exhaustion.
- **Specifica Tecnica della Remediation:** Enforce Pydantic max_depth constraints and payload size limits on all SDUI ingestion endpoints.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b42_b45_sdui_schema_boundaries.py::test_b43_nested_json_depth_limit`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item CTF-009: [CTF-SECURITY]
- **Squadrone / Categoria:** `CTF-SECURITY`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/blue_green_swap.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-3: Race condition during active_db.json atomic pointer swap with concurrent readers.
- **Specifica Tecnica della Remediation:** Perform atomic file swap (os.replace) and verify slot integrity hash before redirecting reads.
- **Test Avversariale Richiesto:** `tests/tier3_pairwise/test_p02_blue_green_wal_concurrency.py::test_p02_blue_green_swap_with_in_flight_wal_reads`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item CTF-010: [CTF-SECURITY]
- **Squadrone / Categoria:** `CTF-SECURITY`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/agentic_routes.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-1: Sidecar binding to 0.0.0.0 instead of loopback 127.0.0.1 exposing service to local network.
- **Specifica Tecnica della Remediation:** Bind strictly to 127.0.0.1 and reject non-loopback interface binding in main CLI parser.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b13_b18_host_security_limits.py::test_b15_loopback_binding_restriction`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item CTF-011: [CTF-SECURITY]
- **Squadrone / Categoria:** `CTF-SECURITY`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medfactory/src/compression/implementations/zstd_dictionary_trainer.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-4: Zstandard compression dictionary size deviation causing decompression failure in client.
- **Specifica Tecnica della Remediation:** Enforce target_size strictly == 114,688 bytes (112 KB) during zstd dictionary training.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b07_b12_factory_compression_limits.py::test_b08_zstd_dict_exact_size`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item CTF-012: [CTF-SECURITY]
- **Squadrone / Categoria:** `CTF-SECURITY`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/base/exceptions.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-2: Internal database exceptions leaking file paths and SQLite schema details in 500 error responses.
- **Specifica Tecnica della Remediation:** Catch internal errors and return sanitized HTTPException with error code and DLQ logging.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b19_b24_database_concurrency_limits.py::test_b21_sanitized_error_responses`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item CTF-013: [CTF-SECURITY]
- **Squadrone / Categoria:** `CTF-SECURITY`
- **Severità:** `LOW`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/user_state_store.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-2: User state store transaction injection via unparameterized SQL statements.
- **Specifica Tecnica della Remediation:** Use parameterized queries exclusively for all insert, update, and delete statements in state store.
- **Test Avversariale Richiesto:** `medclient/sidecar-python/tests/test_storage_and_system.py::test_user_state_store_strict_schema_and_operations`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item CTF-014: [CTF-SECURITY]
- **Squadrone / Categoria:** `CTF-SECURITY`
- **Severità:** `LOW`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/symspell_checker.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-3: Excessive string length in spellcheck input triggering polynomial edit distance blowup.
- **Specifica Tecnica della Remediation:** Limit input term length to <= 64 characters before executing Damerau-Levenshtein calculation.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b25_b29_diagnostic_numerical_limits.py::test_b29_symspell_input_length_cap`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item CTF-015: [CTF-SECURITY]
- **Squadrone / Categoria:** `CTF-SECURITY`
- **Severità:** `LOW`
- **File e Linee Coinvolte:** `medfactory/src/packager/base/medpack_hasher.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** FLAG-4: Dual BLAKE3 / SHA-256 hash mismatch ignored during manifest verification.
- **Specifica Tecnica della Remediation:** Compute both BLAKE3 and SHA-256 digests; abort packaging if either checksum verification fails.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f10_f12_zstd_sqlite_packaging.py::test_f10_dual_hasher_blake3_sha256`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item SRS-001: [SRS-GAP]
- **Squadrone / Categoria:** `SRS-GAP`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `srs_catalog/area1_core_hardware.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** ROA-01: Asymmetric split between MedFactory and MedClient resource allocations.
- **Specifica Tecnica della Remediation:** Define strict memory boundaries: MedFactory allows multi-core RAM; MedClient enforces < 300MB RSS.
- **Test Avversariale Richiesto:** `tests/benchmarks/test_m5_production_sla.py`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item SRS-002: [SRS-GAP]
- **Squadrone / Categoria:** `SRS-GAP`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `srs_catalog/area1_core_hardware.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** ROA-05: Zstd dictionary training requirements on medical texts.
- **Specifica Tecnica della Remediation:** Enforce trained dictionary compression for static markdown sheets achieving >= 2.5x ratio.
- **Test Avversariale Richiesto:** `tests/tier3_pairwise/test_p01_dla_table_zstd_compression.py`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item SRS-003: [SRS-GAP]
- **Squadrone / Categoria:** `SRS-GAP`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `srs_catalog/area1_core_hardware.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** ROA-06: Cryptographic integrity via Ed25519 digital signatures on packages.
- **Specifica Tecnica della Remediation:** Sign manifest.json using Ed25519 and verify signature in MedPackVerifier.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f10_f12_zstd_sqlite_packaging.py`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item SRS-004: [SRS-GAP]
- **Squadrone / Categoria:** `SRS-GAP`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `srs_catalog/area1_core_hardware.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** ROA-07: Blue/Green atomic database swapping without active connection downtime.
- **Specifica Tecnica della Remediation:** Implement active_db.json pointer file with atomic replace and WAL mode persistence.
- **Test Avversariale Richiesto:** `tests/tier3_pairwise/test_p02_blue_green_wal_concurrency.py`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item SRS-005: [SRS-GAP]
- **Squadrone / Categoria:** `SRS-GAP`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `srs_catalog/area2_ingestion_nlp.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** ROA-04: PyHPO isolation in build-time pipeline with precomputed ancestor closures.
- **Specifica Tecnica della Remediation:** Precalculate HPO Information Content and ancestor closure sets in MedFactory SQLite KB.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f07_f09_ontologies_hpo_atc.py`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item SRS-006: [SRS-GAP]
- **Squadrone / Categoria:** `SRS-GAP`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `srs_catalog/area2_ingestion_nlp.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** ROA-11: Vector search embedding model latency SLA (< 50ms per query).
- **Specifica Tecnica della Remediation:** Deploy quantized ONNX MiniLM model executing inference in < 15ms median on CPU.
- **Test Avversariale Richiesto:** `tests/benchmarks/test_m5_production_sla.py`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item SRS-007: [SRS-GAP]
- **Squadrone / Categoria:** `SRS-GAP`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `srs_catalog/area3_diagnostic_emergency.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** ROA-21: Emergency physiological pre-filter triggering red flag alerts.
- **Specifica Tecnica della Remediation:** Evaluate NEWS2 Scale 2, Shock Index >= 1.0, and qSOFA >= 2 prior to Bayesian ranking.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f28_f29_emergency_red_flags.py`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item SRS-008: [SRS-GAP]
- **Squadrone / Categoria:** `SRS-GAP`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `srs_catalog/area3_diagnostic_emergency.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** ROA-15: Sparse CSR log-odds ranking with pertinent negative downweighting.
- **Specifica Tecnica della Remediation:** Implement Laplace smoothing and finite negative penalty W_neg = -12.0 in diagnostic ranker.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f25_f27_log_odds_ranking.py`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item SRS-009: [SRS-GAP]
- **Squadrone / Categoria:** `SRS-GAP`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `srs_catalog/area4_pharmacology_safety.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** ROA-10: CYP450 prodrug bioactivation failure blackbox alert.
- **Specifica Tecnica della Remediation:** Generate Level 1 Blackbox alert for Clopidogrel + CYP2C19 inhibitors (Omeprazole).
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f30_f34_cyp450_pharmacology.py`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item SRS-010: [SRS-GAP]
- **Squadrone / Categoria:** `SRS-GAP`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `srs_catalog/area4_pharmacology_safety.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** ROA-14: Triple Whammy AKI triad detection and CKD-EPI 2021 renal clearance.
- **Specifica Tecnica della Remediation:** Identify RAS blocker + Diuretic + NSAID combination when eGFR < 60 mL/min/1.73m².
- **Test Avversariale Richiesto:** `tests/tier4_workloads/test_w03_diabetic_nephropathy_triple_whammy.py`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item SRS-011: [SRS-GAP]
- **Squadrone / Categoria:** `SRS-GAP`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `srs_catalog/area5_simulation_sdui.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** ROA-16: 2D polygonal image hotspot testing via Ray-Casting.
- **Specifica Tecnica della Remediation:** Implement authoritative Even-Odd test with bounding box fast-reject and R_tol <= 0.02.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f35_f37_educational_cards_nli.py`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item SRS-012: [SRS-GAP]
- **Squadrone / Categoria:** `SRS-GAP`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `srs_catalog/area5_simulation_sdui.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** ROA-17: FSRS-4.5 modern spaced repetition scheduling with deterministic jitter.
- **Specifica Tecnica della Remediation:** Calculate retrievability decay R = (1 + factor * t / S)^decay with SHA256 deterministic jitter.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f38_f40_fsrs_scheduling.py`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item SRS-013: [SRS-GAP]
- **Squadrone / Categoria:** `SRS-GAP`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `srs_catalog/area5_simulation_sdui.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** ROA-02: SDUI polymorphic 4-block architecture parity between backend and frontend.
- **Specifica Tecnica della Remediation:** Synchronize ClinicalSheet, SymptomMatcher, DrugSafety, and ExamSimulator contracts.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f41_f44_frontend_views_store.py`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item SRS-014: [SRS-GAP]
- **Squadrone / Categoria:** `SRS-GAP`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `srs_catalog/area6_curriculum_docimology.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** MOD-06-01: Rasch Item Response Theory (IRT) adaptive question selection.
- **Specifica Tecnica della Remediation:** Define item difficulty theta parameters for USMLE MCQ questions in curriculum catalog.
- **Test Avversariale Richiesto:** `tests/master_e2e_runner.py`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item SRS-015: [SRS-GAP]
- **Squadrone / Categoria:** `SRS-GAP`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `srs_catalog/area6_curriculum_docimology.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** MOD-06-03: LM-41 core curriculum competency mapping (40 courses / 360 CFU).
- **Specifica Tecnica della Remediation:** Map medical disciplines, SSD codes, and clinical learning objectives across 6 academic years.
- **Test Avversariale Richiesto:** `tests/master_e2e_runner.py`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item SRS-016: [SRS-GAP]
- **Squadrone / Categoria:** `SRS-GAP`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `srs_catalog/area7_real_data_remediation.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** MOD-07-01: Real-world ingestion pipeline framework with Dead Letter Queue (DLQ).
- **Specifica Tecnica della Remediation:** Route corrupted and unparseable records to DLQ with SHA-256 hash without failing pipeline.
- **Test Avversariale Richiesto:** `tests/test_srs_tooling.py`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item SRS-017: [SRS-GAP]
- **Squadrone / Categoria:** `SRS-GAP`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `srs_catalog/area7_real_data_remediation.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** MOD-07-04: Authentic CPIC and DrugBank pharmacology integration.
- **Specifica Tecnica della Remediation:** Replace synthetic drug catalogs with certified CPIC Level 1A and open-source pharmacology specs.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f30_f34_cyp450_pharmacology.py`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item SRS-018: [SRS-GAP]
- **Squadrone / Categoria:** `SRS-GAP`
- **Severità:** `LOW`
- **File e Linee Coinvolte:** `srs_catalog/area7_real_data_remediation.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** MOD-07-06: Authentic paraphrase-multilingual-MiniLM-L12-v2 embedding vectors.
- **Specifica Tecnica della Remediation:** Replace dummy random vectors with certified 384-dimensional MiniLM embeddings.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f20_f24_sqlite_nlp.py`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item SRS-019: [SRS-GAP]
- **Squadrone / Categoria:** `SRS-GAP`
- **Severità:** `LOW`
- **File e Linee Coinvolte:** `srs_catalog/data_sources_registry.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Certified open data sources registry coverage for 28 medical knowledge databases.
- **Specifica Tecnica della Remediation:** Include authoritative URL, license, SHA256 policy, and offline caching strategy for all 28 sources.
- **Test Avversariale Richiesto:** `tests/test_srs_tooling.py`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item SRS-020: [SRS-GAP]
- **Squadrone / Categoria:** `SRS-GAP`
- **Severità:** `LOW`
- **File e Linee Coinvolte:** `srs_catalog/area7_real_data_remediation.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** MOD-07-08: Real SymSpell lexicon seeded from authentic clinical vocabulary.
- **Specifica Tecnica della Remediation:** Generate frequency dictionary from MedQA corpus eliminating hand-crafted vocabulary stubs.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f20_f24_sqlite_nlp.py`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item HYG-001: [HYGIENE]
- **Squadrone / Categoria:** `HYGIENE`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medfactory/requirements.txt`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Dependency version unpinning risks non-deterministic builds across CI environments.
- **Specifica Tecnica della Remediation:** Strictly pin all 14 MedFactory dependencies to exact version numbers (==x.y.z).
- **Test Avversariale Richiesto:** `pytest medfactory/tests -v`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item HYG-002: [HYGIENE]
- **Squadrone / Categoria:** `HYGIENE`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/sidecar-python/requirements.txt`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Missing psutil dependency in sidecar caused runtime failure in process supervision.
- **Specifica Tecnica della Remediation:** Pin psutil==6.1.1 and all sidecar dependencies strictly to exact versions.
- **Test Avversariale Richiesto:** `pytest medclient/sidecar-python/tests -v`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item HYG-003: [HYGIENE]
- **Squadrone / Categoria:** `HYGIENE`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/frontend-react/package.json`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Frontend packages lacked exact version pinning across dependencies and devDependencies.
- **Specifica Tecnica della Remediation:** Pin React 19, Vite, Vitest, Tailwind, and Zustand to exact semver versions.
- **Test Avversariale Richiesto:** `cd medclient/frontend-react && npm run build`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item HYG-004: [HYGIENE]
- **Squadrone / Categoria:** `HYGIENE`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/core-rust/Cargo.toml`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Rust dependencies in Cargo.toml had open range specifications.
- **Specifica Tecnica della Remediation:** Pin all Cargo crates to exact version strings with cargo clippy zero-warning policy.
- **Test Avversariale Richiesto:** `cargo clippy --all-targets --manifest-path medclient/core-rust/Cargo.toml -- -D warnings`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item HYG-005: [HYGIENE]
- **Squadrone / Categoria:** `HYGIENE`
- **Severità:** `LOW`
- **File e Linee Coinvolte:** `tests/conftest.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Missing authoritative fixtures in conftest.py broke E2E test runner collection.
- **Specifica Tecnica della Remediation:** Restore real_sqlite_kb, authoritative_keypair, and clinical calculation helper fixtures.
- **Test Avversariale Richiesto:** `python tests/master_e2e_runner.py`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item HYG-006: [HYGIENE]
- **Squadrone / Categoria:** `HYGIENE`
- **Severità:** `LOW`
- **File e Linee Coinvolte:** `tests/e2e/run_all_e2e.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Missing runner wrapper script prevented automated CI invocation of tests/e2e/run_all_e2e.py.
- **Specifica Tecnica della Remediation:** Implement tests/e2e/run_all_e2e.py executing master test runner with proper exit code.
- **Test Avversariale Richiesto:** `python tests/e2e/run_all_e2e.py`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item HYG-007: [HYGIENE]
- **Squadrone / Categoria:** `HYGIENE`
- **Severità:** `LOW`
- **File e Linee Coinvolte:** `tools/guardian_watchdog_daemon.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Missing guardian watchdog CLI tool prevented programmatic SLA memory checking.
- **Specifica Tecnica della Remediation:** Implement tools/guardian_watchdog_daemon.py verifying RSS < 300MB ceiling.
- **Test Avversariale Richiesto:** `python tools/guardian_watchdog_daemon.py --check`
- **Stato:** - [x] FIXED (commit 9d17fc0)

### Item HYG-008: [HYGIENE]
- **Squadrone / Categoria:** `HYGIENE`
- **Severità:** `LOW`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/VirtualBlockWindow.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Source files must not exceed micro-file limit (< 350-400 lines).
- **Specifica Tecnica della Remediation:** Ensure VirtualBlockWindow (152 lines), red_flags.py (200 lines), and models remain modular.
- **Test Avversariale Richiesto:** `mypy --ignore-missing-imports medclient/sidecar-python/src/ medfactory/src/`
- **Stato:** - [x] FIXED (commit 9d17fc0)
