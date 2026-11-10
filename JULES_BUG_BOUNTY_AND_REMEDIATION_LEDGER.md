# MASTER LEDGER: BUG BOUNTY, WHITE-HAT CTF, CLINICAL FALSIFICATION & REMEDIATION

## Executive Summary
This document tracks the deep forensic audit, adversary CTF findings, mathematical/clinical logic falsifications, and architectural parity verifications across the `ibrahim-medplatform` repository.
All findings adhere strictly to the **Zero-Mock Policy**, **Micro-File Modularization (< 350 lines)**, **Strict Domain Semantics**, and **Continuous Verification**.

---

## 1. Squadrone Telemetria Dual-Node & Packet Sniffing IPC

### [BB-TEL-001] Dual-Node CPU vs GPU graceful fallback in ONNX embedding inference
- **ID Univoco:** `BB-TEL-001`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/onnx_embeddings.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** CPU-only nodes falling back gracefully to ONNX runtime CPU provider without crashing or throwing CUDA/DirectML errors.
- **Specifica Tecnica della Remediation:** Explicit execution provider priority [CPUExecutionProvider] fallback verification.
- **Test Avversariale Richiesto:** `test_semantic_embedding_and_cosine_similarity`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-TEL-002] Win32 Job Object memory ceiling accounting under 300 MB RSS
- **ID Univoco:** `BB-TEL-002`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/core-rust/src/main.rs`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Sustained clinical queries exceeding memory limits without active job containment.
- **Specifica Tecnica della Remediation:** SetInformationJobObject with JobObjectExtendedLimitInformation strictly capping process memory.
- **Test Avversariale Richiesto:** `test_win32_job_supervisor_creation_and_accounting`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-TEL-003] IPC Secret Header validation timing-attack resistance
- **ID Univoco:** `BB-TEL-003`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Insecure string comparison of X-Tauri-IPC-Secret susceptible to timing analysis.
- **Specifica Tecnica della Remediation:** Constant-time HMAC comparison using hmac.compare_digest.
- **Test Avversariale Richiesto:** `test_agentic_api_endpoints`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-TEL-004] WebSocket bidirectional telemetry synchronization
- **ID Univoco:** `BB-TEL-004`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Dropped telemetry packets or silent channel closure during multi-query pipeline.
- **Specifica Tecnica della Remediation:** Structured heartbeat frames and reconnect handshake via ReverseWatchdog.
- **Test Avversariale Richiesto:** `test_reverse_watchdog_lifecycle`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-TEL-005] Reverse Watchdog parent process termination detection
- **ID Univoco:** `BB-TEL-005`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/reverse_watchdog.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Sidecar orphan daemon running indefinitely if host Tauri process crashes.
- **Specifica Tecnica della Remediation:** Win32 WaitForSingleObject / polling loop terminating sidecar within 1000ms of parent death.
- **Test Avversariale Richiesto:** `test_reverse_watchdog_lifecycle`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-TEL-006] FTS5 BM25 search contract parity with frontend TypeScript
- **ID Univoco:** `BB-TEL-006`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/sdui_routes.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Discrepancy between HybridSearchResponse in Python and SearchMatchEntry in TypeScript.
- **Specifica Tecnica della Remediation:** Enforce bidirectional schema cohesion via Pydantic model and TS interface.
- **Test Avversariale Richiesto:** `test_f41_f44_frontend_views_store`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-TEL-007] Dual-Registry SDUI polymorphism canonical mapping
- **ID Univoco:** `BB-TEL-007`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/sdui_emitter.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Legacy block type alias rejection causing client rendering desynchronization.
- **Specifica Tecnica della Remediation:** SDUI_BLOCK_REGISTRY bidirectional resolving canonical names and legacy aliases.
- **Test Avversariale Richiesto:** `test_sdui_serialization_emitter`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-TEL-008] Zero-Copy memmap2 buffer boundaries in asset protocol
- **ID Univoco:** `BB-TEL-008`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/core-rust/src/main.rs`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Buffer overflow or out-of-bounds slicing in med-asset:// handler.
- **Specifica Tecnica della Remediation:** Bounded slice validation and LRU cache eviction in Rust asset protocol.
- **Test Avversariale Richiesto:** `test_bounded_mmap_lru_cache_eviction`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-TEL-009] FastAPI request payload validation strictness
- **ID Univoco:** `BB-TEL-009`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/base/sdui_models.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Extraneous payload keys causing silent corruption in SDUI envelope.
- **Specifica Tecnica della Remediation:** ConfigDict(extra='forbid') on all SDUI envelope models.
- **Test Avversariale Richiesto:** `test_b42_b45_sdui_schema_boundaries`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-TEL-010] Jemalloc heap fragmentation tuning in Core Rust
- **ID Univoco:** `BB-TEL-010`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/core-rust/src/main.rs`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Memory bloat from long-running process page allocations.
- **Specifica Tecnica della Remediation:** Tuning jemalloc with background_thread:true and dirty_page_decay_ms:0.
- **Test Avversariale Richiesto:** `test_jemalloc_memory_tuner_config`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-TEL-011] TLV handshake framing binary encoding
- **ID Univoco:** `BB-TEL-011`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/core-rust/src/main.rs`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Malformed binary TLV frame crashing host-sidecar IPC channel.
- **Specifica Tecnica della Remediation:** Strict length prefix checking and CRC32 payload verification.
- **Test Avversariale Richiesto:** `test_handshake_tlv_serialization`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-TEL-012] SQLite WAL reader concurrency connection pooling
- **ID Univoco:** `BB-TEL-012`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/sqlite_pool.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Database locked errors during concurrent read transactions across threads.
- **Specifica Tecnica della Remediation:** Thread-safe reader pool with max_readers capacity and busy_timeout PRAGMA.
- **Test Avversariale Richiesto:** `test_sqlite_wal_pool`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-TEL-013] Blue-Green database swap atomic pointer switch
- **ID Univoco:** `BB-TEL-013`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/blue_green_swap.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Stale reads or partial writes during module KB live updates.
- **Specifica Tecnica della Remediation:** Atomic JSON pointer swap with SHA-256 integrity check and rollback.
- **Test Avversariale Richiesto:** `test_blue_green_atomic_swap`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-TEL-014] SLA latency budget under 50ms p99 execution
- **ID Univoco:** `BB-TEL-014`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `tests/benchmarks/test_m5_production_sla.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Degraded clinical pipeline latency exceeding real-time consultation SLA.
- **Specifica Tecnica della Remediation:** End-to-end vector search, differential ranking, and CYP450 under 50ms.
- **Test Avversariale Richiesto:** `test_production_sla_latency_p99_under_fifty_millis`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-TEL-015] SLA RSS memory budget strictly below 300MB
- **ID Univoco:** `BB-TEL-015`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `tests/benchmarks/test_m5_production_sla.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Memory leak in sustained multi-block evaluation loops.
- **Specifica Tecnica della Remediation:** Garbage collection and deterministic resource cleanup in connection pool.
- **Test Avversariale Richiesto:** `test_production_sla_rss_memory_under_three_hundred_mb`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-TEL-016] Agent token authorization scope validation
- **ID Univoco:** `BB-TEL-016`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Unauthenticated access to internal clinical evaluation endpoints.
- **Specifica Tecnica della Remediation:** Strict X-Tauri-IPC-Secret authentication dependency injected across routes.
- **Test Avversariale Richiesto:** `test_b13_b18_host_security_limits`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

---

## 2. Squadrone Ispezione Live GUI, Ergonomia Clinica & DOM Retention

### [BB-GUI-001] DOM Retention at 60 FPS across navigation tabs
- **ID Univoco:** `BB-GUI-001`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MedClientAppShell.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Unmounting tab components causing losing scroll positions and input states.
- **Specifica Tecnica della Remediation:** CSS visibility toggling (hidden opacity-0 vs block opacity-100) preserving DOM elements.
- **Test Avversariale Richiesto:** `F41, F43, F44, F45, F46 MedClientAppShell retains all 4 views in DOM`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-GUI-002] Clinical Callout RED_FLAG color grading rose-600
- **ID Univoco:** `BB-GUI-002`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/ClinicalSheetBlockView.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Inconsistent alert styling causing visual ambiguity for urgent clinical risks.
- **Specifica Tecnica della Remediation:** Strict Tailwind rose-600 palette mapping for RED_FLAG, CRITICAL, and CONTRAINDICATION.
- **Test Avversariale Richiesto:** `test_f45_f48_frontend_blocks_canvas`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-GUI-003] Clinical Callout BLACKBOX color grading amber-500
- **ID Univoco:** `BB-GUI-003`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/ClinicalSheetBlockView.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Blackbox drug alerts lacking FDA warning prominence.
- **Specifica Tecnica della Remediation:** Strict Tailwind amber-500 palette mapping for BLACKBOX and WARNING callouts.
- **Test Avversariale Richiesto:** `test_f45_f48_frontend_blocks_canvas`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-GUI-004] Clinical Callout CLINICAL_PEARL color grading sky-600
- **ID Univoco:** `BB-GUI-004`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/ClinicalSheetBlockView.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Mismatched educational tip color reducing monograph readability.
- **Specifica Tecnica della Remediation:** Strict Tailwind sky-600 palette mapping for CLINICAL_PEARL and EXAM_TIP callouts.
- **Test Avversariale Richiesto:** `test_f45_f48_frontend_blocks_canvas`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-GUI-005] VirtualBlockWindow DOM containment optimization
- **ID Univoco:** `BB-GUI-005`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/VirtualBlockWindow.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Excessive DOM repaints during fast monograph scrolling.
- **Specifica Tecnica della Remediation:** CSS contain: 'layout style paint' with maximum 30-50 nodes mounted.
- **Test Avversariale Richiesto:** `test_b47_virtual_dom_zero_row_height_division_guard`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-GUI-006] Even-Odd Ray-Casting image hotspot tolerance R_tol <= 0.02
- **ID Univoco:** `BB-GUI-006`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/ExamSimulatorBlockView.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Inaccurate touch/click target detection on high-resolution clinical images.
- **Specifica Tecnica della Remediation:** Ray-casting point-in-polygon algorithm with R_tol <= 0.02 tolerance circle indicator.
- **Test Avversariale Richiesto:** `test_w04_stage1_thoracic_hotspot_even_odd_ray_casting`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-GUI-007] Hotspot coordinate clamping to [0, 1] normalized bounding box
- **ID Univoco:** `BB-GUI-007`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/ExamSimulatorBlockView.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Out-of-bounds click coordinates causing NaN or runtime errors.
- **Specifica Tecnica della Remediation:** Math.max(0, Math.min(1, coord)) clamping on all click/touch interactions.
- **Test Avversariale Richiesto:** `test_b46_exam_simulator_complex_nested_item_data`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-GUI-008] WAI-ARIA 1.2 accessibility on symptom search combobox
- **ID Univoco:** `BB-GUI-008`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/SymptomMatcherBlockView.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Screen readers unable to announce active autocomplete suggestions.
- **Specifica Tecnica della Remediation:** Proper role='combobox', aria-expanded, aria-activedescendant attributes.
- **Test Avversariale Richiesto:** `test_f41_f44_frontend_views_store`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-GUI-009] HPO autocomplete keyboard navigation (ArrowUp, ArrowDown, Enter)
- **ID Univoco:** `BB-GUI-009`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/SymptomMatcherBlockView.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Keyboard users unable to select symptom matches without mouse.
- **Specifica Tecnica della Remediation:** Arrow key navigation handlers updating active index and Enter committing tag.
- **Test Avversariale Richiesto:** `test_f41_f44_frontend_views_store`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-GUI-010] Drug safety eGFR and CYP450 clearance real-time gauges
- **ID Univoco:** `BB-GUI-010`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/DrugSafetyBlockView.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Static clearance numbers without visual risk thresholds.
- **Specifica Tecnica della Remediation:** Color-coded clearance meters (green > 80%, yellow 30-80%, red < 30%).
- **Test Avversariale Richiesto:** `test_f45_f48_frontend_blocks_canvas`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-GUI-011] Molecular Structure Viewer 2D SVG fallback before 3D WebGL
- **ID Univoco:** `BB-GUI-011`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MolecularStructureViewer.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** WebGL context initialization crash on low-end or headless devices.
- **Specifica Tecnica della Remediation:** Instant 2D SVG rendering with deferred WebGL broker attachment.
- **Test Avversariale Richiesto:** `test_b48_webgl_context_lost_event_triggers_svg_fallback`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-GUI-012] WebGL Singleton Broker context lost recovery
- **ID Univoco:** `BB-GUI-012`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MolecularStructureViewer.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Context loss permanently freezing 3D molecular canvas.
- **Specifica Tecnica della Remediation:** Listen for webglcontextlost event and seamlessly restore 2D SVG mode.
- **Test Avversariale Richiesto:** `test_b48_webgl_unsupported_hardware_graceful_fallback`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-GUI-013] ECG Waveform 500 Hz canvas rendering with millimetric grid
- **ID Univoco:** `BB-GUI-013`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/ExamSimulatorBlockView.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Low-resolution waveform distortion obscuring ST elevation/depression.
- **Specifica Tecnica della Remediation:** 500 Hz interpolation with standard 25 mm/s and 10 mm/mV clinical grid.
- **Test Avversariale Richiesto:** `test_w01_stage1_stemi_presentation_and_diagnostic_ranking`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-GUI-014] Stateful DAG clinical simulation step transitions
- **ID Univoco:** `BB-GUI-014`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/ExamSimulatorBlockView.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Discontinuous scenario branches leading to invalid clinical states.
- **Specifica Tecnica della Remediation:** Deterministic state machine validating preconditions before transition.
- **Test Avversariale Richiesto:** `test_stateful_dag_scenario_transitions`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-GUI-015] FSRS spaced repetition rating buttons (Again, Hard, Good, Easy)
- **ID Univoco:** `BB-GUI-015`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/ExamSimulatorBlockView.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Rating clicks failing to persist review outcome to local store.
- **Specifica Tecnica della Remediation:** Full payload dispatch to /fsrs/schedule endpoint and card state update.
- **Test Avversariale Richiesto:** `test_p04_mcq_success_updates_fsrs_and_sdui_block`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-GUI-016] Curriculum LM-41 40-course monograph browser navigation
- **ID Univoco:** `BB-GUI-016`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MedClientAppShell.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Broken links or missing monographs when browsing 360 CFU course tree.
- **Specifica Tecnica della Remediation:** Full SSD filtering and hierarchical tree navigation across all courses.
- **Test Avversariale Richiesto:** `test_f41_f44_frontend_views_store`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

---

## 3. Squadrone Anti-False-Positive & Falsificazione Matematico-Clinica

### [BB-LOGIC-001] CKD-EPI 2021 race-free eGFR formula boundary validation
- **ID Univoco:** `BB-LOGIC-001`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/ckd_epi.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Negative, zero, or extreme creatinine (0.1 to 15.0 mg/dL) causing math domain errors.
- **Specifica Tecnica della Remediation:** Exact piecewise min(Scr/kappa, 1)^alpha * max(Scr/kappa, 1)^-1.200 * 0.9938^Age.
- **Test Avversariale Richiesto:** `test_ckd_epi_2021_renal_calculator`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-LOGIC-002] Shock Index zero systolic blood pressure division guard
- **ID Univoco:** `BB-LOGIC-002`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/red_flags.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Systolic BP <= 0 causing ZeroDivisionError during trauma triage.
- **Specifica Tecnica della Remediation:** Explicit guard raising ValueError when systolic BP <= 0.
- **Test Avversariale Richiesto:** `test_red_flags_shock_index_and_qsofa`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-LOGIC-003] qSOFA Sepsis-3 multi-variable clinical score calculation
- **ID Univoco:** `BB-LOGIC-003`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/red_flags.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Tautological checks verifying only integer return type instead of clinical threshold.
- **Specifica Tecnica della Remediation:** Strict evaluation of RR >= 22 (+1), SBP <= 100 (+1), GCS < 15 (+1).
- **Test Avversariale Richiesto:** `test_red_flags_shock_index_and_qsofa`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-LOGIC-004] NEWS2 hypercapnic respiratory failure Scale 2 selection
- **ID Univoco:** `BB-LOGIC-004`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/red_flags.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Applying default SpO2 scale to COPD patients triggering false emergency alarms.
- **Specifica Tecnica della Remediation:** Dedicated SpO2 Scale 2 (88-92% target) for hypercapnic respiratory failure.
- **Test Avversariale Richiesto:** `test_w02_stage4_red_flags_immediate_escalation_and_emergency_action`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-LOGIC-005] QTc Prolongation Bazett extreme heart rate distortion
- **ID Univoco:** `BB-LOGIC-005`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/qtc_engine.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Bazett overestimating QTc at HR > 100 and underestimating at HR < 60.
- **Specifica Tecnica della Remediation:** Multi-formula support (Bazett, Fridericia, Framingham, Hodges) with risk flags.
- **Test Avversariale Richiesto:** `test_qtc_prolongation_score`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-LOGIC-006] Log-Sum-Exp softmax normalization underflow/overflow guard
- **ID Univoco:** `BB-LOGIC-006`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/softmax_normalizer.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Large log-odds scores (e.g. > 700) causing exp() overflow to inf or NaN.
- **Specifica Tecnica della Remediation:** Subtracting max(logits) prior to exponentiation ensuring strictly normalized probabilities.
- **Test Avversariale Richiesto:** `test_log_sum_exp_softmax_normalizer`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-LOGIC-007] Bayesian Sparse CSR log-odds diagnostic ranker normalization
- **ID Univoco:** `BB-LOGIC-007`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/sparse_csr_ranker.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Negative posterior probabilities or sum(p) != 1.0 with 20+ symptoms.
- **Specifica Tecnica della Remediation:** Numerically stable CSR matrix multiply followed by LogSumExp normalizer.
- **Test Avversariale Richiesto:** `test_sparse_csr_log_odds_ranker`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-LOGIC-008] Pertinent negatives likelihood ratio rule-out mechanism
- **ID Univoco:** `BB-LOGIC-008`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/pertinent_negatives.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Absence of symptom wrongly treated as zero information instead of penalty.
- **Specifica Tecnica della Remediation:** Explicit likelihood ratio penalty log(P(neg|disease) / P(neg|~disease)).
- **Test Avversariale Richiesto:** `test_pertinent_negatives_rule_out`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-LOGIC-009] Active Discriminator mutual information Next Best Question (NBQ)
- **ID Univoco:** `BB-LOGIC-009`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/active_discriminator.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** NBQ proposing already confirmed symptoms or zero-entropy features.
- **Specifica Tecnica della Remediation:** Shannon entropy reduction maximization over uninvestigated candidate features.
- **Test Avversariale Richiesto:** `test_active_discriminator_nbq`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-LOGIC-010] CYP450 Prodrug bioactivation inhibition blackbox warning
- **ID Univoco:** `BB-LOGIC-010`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/cyp450_engine.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Failing to detect Clopidogrel loss of efficacy when co-administered with Omeprazole.
- **Specifica Tecnica della Remediation:** Exact CYP2C19 substrate-inhibitor interaction flagging BLACKBOX alert.
- **Test Avversariale Richiesto:** `test_roa10_cyp450_prodrug_blackbox_warning`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-LOGIC-011] Triple Whammy Acute Kidney Injury triad detector
- **ID Univoco:** `BB-LOGIC-011`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/triple_whammy.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Co-prescription of ACEi/ARB + Diuretic + NSAID passing without AKI warning.
- **Specifica Tecnica della Remediation:** Triad combination detector triggering CRITICAL AKI alert and eGFR check.
- **Test Avversariale Richiesto:** `test_triple_whammy_aki_detector`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-LOGIC-012] CPIC Level 1A Pharmacogenomics CYP2C19 activity score
- **ID Univoco:** `BB-LOGIC-012`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/cpic_engine.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Poor metabolizer *2/*2 alleles wrongly prescribed standard clopidogrel doses.
- **Specifica Tecnica della Remediation:** Exact CPIC allele scoring (*1=1.0, *2=0.0, *17=1.0) and phenotyping.
- **Test Avversariale Richiesto:** `test_cpic_level_1a_pharmacogenomics`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-LOGIC-013] FSRS-4.5 stability and difficulty monotonicity invariants
- **ID Univoco:** `BB-LOGIC-013`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/fsrs_scheduler.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Rating Easy yielding lower stability S than rating Hard, or D exceeding [1, 10].
- **Specifica Tecnica della Remediation:** Strict mathematical clamping: D in [1, 10], S strictly increasing with rating.
- **Test Avversariale Richiesto:** `test_fsrs_spaced_repetition_scheduler`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-LOGIC-014] FSRS-4.5 retrievability decay formula boundary invariants
- **ID Univoco:** `BB-LOGIC-014`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/fsrs_scheduler.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Retrievability R returning values outside [0, 1] at t=0 or extreme intervals.
- **Specifica Tecnica della Remediation:** Formula R = (1 + factor * t / S)^-0.5 guaranteeing R=1 at t=0 and R->0 as t->inf.
- **Test Avversariale Richiesto:** `test_fsrs_spaced_repetition_scheduler`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-LOGIC-015] Review Load Balancer daily card count smoothing
- **ID Univoco:** `BB-LOGIC-015`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/review_load_balancer.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Review card spikes exceeding daily study capacity.
- **Specifica Tecnica della Remediation:** Fuzzing due dates around mean target to maintain uniform daily review workload.
- **Test Avversariale Richiesto:** `test_review_load_balancer`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [BB-LOGIC-016] NLI Cross-Encoder clinical premise entailment scoring
- **ID Univoco:** `BB-LOGIC-016`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/nli_cross_encoder.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Empty or nonsensical student responses receiving passing scores.
- **Specifica Tecnica della Remediation:** Cross-encoder scoring checking semantic entailment against gold standard.
- **Test Avversariale Richiesto:** `test_nli_cross_encoder_scoring`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

---

## 4. Squadrone White-Hat CTF sul Runtime Locale

### [CTF-SEC-001] FLAG-1: Authentication bypass on /agent/execute endpoint
- **ID Univoco:** `CTF-SEC-001`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Forged or absent IPC token executing arbitrary sidecar commands.
- **Specifica Tecnica della Remediation:** Reject requests without matching X-Tauri-IPC-Secret with 403 Forbidden.
- **Test Avversariale Richiesto:** `test_b13_b18_host_security_limits`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [CTF-SEC-002] FLAG-1: Port binding race condition on loopback 127.0.0.1:8765
- **ID Univoco:** `CTF-SEC-002`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/main.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Another local process hijacking sidecar port on startup.
- **Specifica Tecnica della Remediation:** Exclusive port binding with SO_REUSEADDR handling and fallback detection.
- **Test Avversariale Richiesto:** `test_host_process_lifecycle_transitions`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [CTF-SEC-003] FLAG-1: CORS configuration restricting to Tauri origin
- **ID Univoco:** `CTF-SEC-003`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Malicious local web pages executing cross-origin requests to sidecar.
- **Specifica Tecnica della Remediation:** Restrict CORS allow_origins strictly to tauri://localhost and 127.0.0.1:5173.
- **Test Avversariale Richiesto:** `test_b13_b18_host_security_limits`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [CTF-SEC-004] FLAG-1: SSRF prevention on data ingester fetchers
- **ID Univoco:** `CTF-SEC-004`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medfactory/src/ontologies/implementations/hpo_ingestor.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Ingester fetching local cloud metadata endpoints (169.254.169.254).
- **Specifica Tecnica della Remediation:** Block internal IP ranges (127.0.0.0/8, 10.0.0.0/8, 192.168.0.0/16, 169.254.0.0/16).
- **Test Avversariale Richiesto:** `test_b13_b18_host_security_limits`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [CTF-SEC-005] FLAG-2: SQLite FTS5 injection fuzzing with unmatched quotes
- **ID Univoco:** `CTF-SEC-005`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/fts5_search.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Malformed query like 'stemi" OR 1=1' crashing FTS5 search query.
- **Specifica Tecnica della Remediation:** Sanitize query string removing unbalanced double quotes and escaping FTS5 operators.
- **Test Avversariale Richiesto:** `test_b11_sqlite_column_name_sql_keyword`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [CTF-SEC-006] FLAG-2: SQL parameter injection defense in dynamic queries
- **ID Univoco:** `CTF-SEC-006`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medfactory/src/database/implementations/sqlite_module_builder.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Unsanitized table or column names injected during packaging.
- **Specifica Tecnica della Remediation:** Enforce strict parameterized queries and double-quoted identifiers.
- **Test Avversariale Richiesto:** `test_b11_sqlite_column_name_sql_keyword`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [CTF-SEC-007] FLAG-2: Corrupted record Dead Letter Queue (DLQ) routing
- **ID Univoco:** `CTF-SEC-007`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medfactory/src/ingestion/implementations/dlq_handler.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Corrupted raw record halting multi-gigabyte build pipeline.
- **Specifica Tecnica della Remediation:** Catch parse exceptions and divert corrupted records to DLQ with SHA-256 hash.
- **Test Avversariale Richiesto:** `test_b11_sqlite_corrupted_utf8_in_text_cell`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [CTF-SEC-008] FLAG-2: Unicode null byte (\x00) payload injection guard
- **ID Univoco:** `CTF-SEC-008`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Null bytes in request payload causing C-level string truncation bugs.
- **Specifica Tecnica della Remediation:** Reject or strip null bytes in Pydantic custom validators.
- **Test Avversariale Richiesto:** `test_b11_sqlite_corrupted_utf8_in_text_cell`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [CTF-SEC-009] FLAG-3: Concurrency torture with 100+ simultaneous queries
- **ID Univoco:** `CTF-SEC-009`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/sqlite_pool.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Deadlock or thread starvation under high query volume.
- **Specifica Tecnica della Remediation:** WAL journal mode with busy_timeout=5000ms and connection pool isolation.
- **Test Avversariale Richiesto:** `test_b19_b24_database_concurrency_limits`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [CTF-SEC-010] FLAG-3: Memory leak stress in continuous embedding inference
- **ID Univoco:** `CTF-SEC-010`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `tests/benchmarks/test_m5_production_sla.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Unreleased ONNX runtime tensors accumulating in process memory.
- **Specifica Tecnica della Remediation:** Explicit scope management and memory reclamation after each inference cycle.
- **Test Avversariale Richiesto:** `test_production_sla_rss_memory_under_three_hundred_mb`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [CTF-SEC-011] FLAG-3: WebGL context exhaustion stress under rapid switching
- **ID Univoco:** `CTF-SEC-011`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MolecularStructureViewer.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Rapid tab switching causing GPU context exhaustion.
- **Specifica Tecnica della Remediation:** Singleton WebGL broker recycling single canvas across all viewer instances.
- **Test Avversariale Richiesto:** `test_b48_webgl_context_switch_frequency_stress`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [CTF-SEC-012] FLAG-4: .medpack archive bit-flipping detection
- **ID Univoco:** `CTF-SEC-012`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medfactory/src/packager/implementations/medpack_verifier.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Modified payload bytes in .medpack archive passing verification.
- **Specifica Tecnica della Remediation:** BLAKE3 file hash mismatch check rejecting modified archive components.
- **Test Avversariale Richiesto:** `test_b12_medpack_corrupted_blake3_checksum`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [CTF-SEC-013] FLAG-4: Ed25519 cryptographic signature verification enforcement
- **ID Univoco:** `CTF-SEC-013`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medfactory/src/packager/implementations/medpack_verifier.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Forged package manifest accepted with mismatched Ed25519 signature.
- **Specifica Tecnica della Remediation:** Verify manifest signature with embedded public key using pure Ed25519 verification.
- **Test Avversariale Richiesto:** `test_b12_medpack_corrupted_ed25519_signature`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [CTF-SEC-014] FLAG-4: Directory traversal vulnerability in med-asset:// protocol
- **ID Univoco:** `CTF-SEC-014`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/core-rust/src/main.rs`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Path traversal attack requesting 'med-asset://../../etc/passwd'.
- **Specifica Tecnica della Remediation:** Canonicalize path and verify it remains strictly within allowed asset base directory.
- **Test Avversariale Richiesto:** `test_asset_protocol_handler_with_persistent_cache_and_formats`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [CTF-SEC-015] FLAG-4: Windows DPAPI entropy corruption recovery
- **ID Univoco:** `CTF-SEC-015`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/core-rust/src/main.rs`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Corrupted DPAPI encrypted blob hanging client startup.
- **Specifica Tecnica della Remediation:** Handle CryptUnprotectData failure gracefully with clean re-encryption fallback.
- **Test Avversariale Richiesto:** `test_windows_dpapi_roundtrip`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [CTF-SEC-016] FLAG-4: Zstandard compression ratio bomb prevention
- **ID Univoco:** `CTF-SEC-016`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medfactory/src/packager/implementations/medpack_verifier.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Malicious archive expanding into terabytes of zeroes during decompression.
- **Specifica Tecnica della Remediation:** Enforce maximum uncompressed size limits during streaming decompression.
- **Test Avversariale Richiesto:** `test_b07_b12_factory_compression_limits`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

---

## 5. Squadrone Matrice di Parità Totale con SRS (44 Moduli & 40 ROA)

### [SRS-GAP-001] ROA-01: Offline-First Zero-Cloud Execution Invariant
- **ID Univoco:** `SRS-GAP-001`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `SRS_MedClient_Architettura_Completa.md`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** External HTTP calls detected in client evaluation flow.
- **Specifica Tecnica della Remediation:** Remove all remote network calls; execute 100% locally on device.
- **Test Avversariale Richiesto:** `test_f45_f48_frontend_blocks_canvas`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [SRS-GAP-002] ROA-02: SDUI Polymorphic Dual Registry Block Mapping
- **ID Univoco:** `SRS-GAP-002`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/sdui_emitter.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Client failing to deserialize polymorphic blocks with missing type discriminators.
- **Specifica Tecnica della Remediation:** Map all 4 blocks 1:1 with frontend view components and dual registry.
- **Test Avversariale Richiesto:** `test_sdui_serialization_emitter`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [SRS-GAP-003] ROA-05: Bit-Exact 114,688-Byte Zstandard Dictionary Training
- **ID Univoco:** `SRS-GAP-003`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medfactory/src/compression/implementations/zstd_dictionary_trainer.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Dictionary size differing from authoritative 114,688 bytes.
- **Specifica Tecnica della Remediation:** Exact slice padding/truncation ensuring len(dict) == 114,688 bytes.
- **Test Avversariale Richiesto:** `test_p01_table_normalizer_and_zstd_dict_compression_ratio`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [SRS-GAP-004] ROA-10: CYP450 Prodrug Bioactivation & DDI Warning Rules
- **ID Univoco:** `SRS-GAP-004`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/cyp450_engine.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Missing bioactivation reduction flag for prodrugs under enzyme inhibition.
- **Specifica Tecnica della Remediation:** Calculate effective clearance and generate prodrug specific clinical warning.
- **Test Avversariale Richiesto:** `test_roa10_cyp450_prodrug_blackbox_warning`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [SRS-GAP-005] ROA-14: Win32 Job Object & RSS < 300MB Memory Enforcement
- **ID Univoco:** `SRS-GAP-005`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/core-rust/src/main.rs`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Process memory uncontrolled on low-RAM workstations.
- **Specifica Tecnica della Remediation:** Attach sidecar process to Win32 Job Object with 300MB limit.
- **Test Avversariale Richiesto:** `test_production_sla_rss_memory_under_three_hundred_mb`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [SRS-GAP-006] ROA-15: Zero-Copy memmap2 Memory-Mapped File Access
- **ID Univoco:** `SRS-GAP-006`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/core-rust/src/main.rs`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Reading entire multi-megabyte media assets into heap memory.
- **Specifica Tecnica della Remediation:** Zero-copy mmap with bounded LRU eviction cache.
- **Test Avversariale Richiesto:** `test_bounded_mmap_lru_cache_eviction`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [SRS-GAP-007] ROA-18: DOM Retention via CSS Visibility at 60 FPS
- **ID Univoco:** `SRS-GAP-007`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MedClientAppShell.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Switching tabs resetting view scroll, inputs, and canvas state.
- **Specifica Tecnica della Remediation:** CSS display/opacity toggle preserving active DOM elements.
- **Test Avversariale Richiesto:** `F41, F43, F44, F45, F46 MedClientAppShell retains all 4 views in DOM`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [SRS-GAP-008] ROA-20: Even-Odd Ray-Casting Hotspot Detection with R_tol <= 0.02
- **ID Univoco:** `SRS-GAP-008`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/ExamSimulatorBlockView.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Hotspot miss when clicking slightly outside polygon vertex.
- **Specifica Tecnica della Remediation:** Ray-casting point-in-polygon with R_tol tolerance circle.
- **Test Avversariale Richiesto:** `test_w04_stage1_thoracic_hotspot_even_odd_ray_casting`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [SRS-GAP-009] ROA-22: WebGL Singleton Broker with 2D SVG Fallback
- **ID Univoco:** `SRS-GAP-009`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MolecularStructureViewer.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Uncontrolled WebGL context creations exhausting GPU resources.
- **Specifica Tecnica della Remediation:** Single broker managing WebGL context with fallback to 2D SVG.
- **Test Avversariale Richiesto:** `test_b48_webgl_context_lost_event_triggers_svg_fallback`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [SRS-GAP-010] ROA-25: Emergency Triage Telemetry Shock Index Escalation
- **ID Univoco:** `SRS-GAP-010`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/red_flags.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Shock index > 0.9 not escalating to immediate resuscitation protocol.
- **Specifica Tecnica della Remediation:** Trigger RED_FLAG callout and priority DAG scenario transition.
- **Test Avversariale Richiesto:** `test_w02_stage2_shock_index_calculation`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [SRS-GAP-011] ROA-28: Real Data Sources Substitution (Zero-Mock Catalog)
- **ID Univoco:** `SRS-GAP-011`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `srs_catalog/data_sources_registry.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Synthetic placeholder data used instead of real clinical terminologies.
- **Specifica Tecnica della Remediation:** Enforce certified real data sources (MedQA, OpenFDA, HPO, ICD-10).
- **Test Avversariale Richiesto:** `test_srs_tooling.py`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [SRS-GAP-012] ROA-30: FSRS-4.5 Retrievability Equation Parity
- **ID Univoco:** `SRS-GAP-012`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/fsrs_scheduler.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Discrepancy in power-law retention curve calculation.
- **Specifica Tecnica della Remediation:** Exact FSRS v4 retrievability R = (1 + factor * t / S)^-0.5.
- **Test Avversariale Richiesto:** `test_fsrs_spaced_repetition_scheduler`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [SRS-GAP-013] ROA-32: Dual-Model Cross-Encoder NLI Grading Validation
- **ID Univoco:** `SRS-GAP-013`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/nli_cross_encoder.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Subjective answer evaluation inconsistent with gold-standard rubric.
- **Specifica Tecnica della Remediation:** Cosine and cross-encoder score thresholding for exam questions.
- **Test Avversariale Richiesto:** `test_nli_cross_encoder_scoring`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [SRS-GAP-014] ROA-35: 40-Course LM-41 360 CFU Medical Curriculum Parity
- **ID Univoco:** `SRS-GAP-014`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `SRS_MedClient_Architettura_Completa.md`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Missing syllabus topics in clinical cardiology or pharmacology.
- **Specifica Tecnica della Remediation:** Complete 40-course syllabus indexed with learning objectives and monographs.
- **Test Avversariale Richiesto:** `test_f41_f44_frontend_views_store`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [SRS-GAP-015] ROA-38: High-Contrast Clinical Callout Palette Invariant
- **ID Univoco:** `SRS-GAP-015`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/ClinicalSheetBlockView.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Incorrect palette usage for clinical risk callouts.
- **Specifica Tecnica della Remediation:** Rose-600 for RED_FLAG, Amber-500 for BLACKBOX, Sky-600 for PEARL.
- **Test Avversariale Richiesto:** `test_f45_f48_frontend_blocks_canvas`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [SRS-GAP-016] ROA-40: One-Click Boot Script Readiness Synchronization
- **ID Univoco:** `SRS-GAP-016`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `MedPlatform.bat`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Frontend opening in browser before backend sidecar is ready to accept queries.
- **Specifica Tecnica della Remediation:** Active curl polling loop verifying backend /health and frontend 5173.
- **Test Avversariale Richiesto:** `test_host_process_lifecycle_transitions`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

---

## 6. Squadrone Igiene del Workspace & Dipendenze

### [HYG-WS-001] Strict dependency version pinning across manifests
- **ID Univoco:** `HYG-WS-001`
- **Squadrone / Categoria:** `[HYGIENE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/frontend-react/package.json`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Floating semver ranges (^ or ~) causing non-deterministic builds.
- **Specifica Tecnica della Remediation:** Pin exact versions for all npm and pip packages.
- **Test Avversariale Richiesto:** `test_jemalloc_memory_tuner_config`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [HYG-WS-002] Mypy strict static type checking across 94 source files
- **ID Univoco:** `HYG-WS-002`
- **Squadrone / Categoria:** `[HYGIENE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Uncaught type inconsistencies in Pydantic models and engines.
- **Specifica Tecnica della Remediation:** 0 errors across all 94 Python files with mypy --ignore-missing-imports.
- **Test Avversariale Richiesto:** `test_agentic_api_endpoints`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [HYG-WS-003] Rust Cargo Clippy 0 warnings enforcement
- **ID Univoco:** `HYG-WS-003`
- **Squadrone / Categoria:** `[HYGIENE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/core-rust/src/lib.rs`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Suboptimal memory allocations or dead code in core engine.
- **Specifica Tecnica della Remediation:** cargo clippy --all-targets -- -D warnings passing cleanly.
- **Test Avversariale Richiesto:** `test_bounded_mmap_lru_cache_eviction`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [HYG-WS-004] TypeScript noEmit compiler verification
- **ID Univoco:** `HYG-WS-004`
- **Squadrone / Categoria:** `[HYGIENE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Type mismatches in React SDUI props or Zustand store actions.
- **Specifica Tecnica della Remediation:** npx tsc --noEmit passing cleanly with 0 type errors.
- **Test Avversariale Richiesto:** `test_f41_f44_frontend_views_store`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [HYG-WS-005] Vitest frontend unit test suite verification
- **ID Univoco:** `HYG-WS-005`
- **Squadrone / Categoria:** `[HYGIENE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Regressions in SDUI view rendering or store action handlers.
- **Specifica Tecnica della Remediation:** npx vitest run passing 100% (8/8 tests).
- **Test Avversariale Richiesto:** `F41, F43, F44, F45, F46 MedClientAppShell retains all 4 views in DOM`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [HYG-WS-006] E2E Master Runner 521/521 invariant test execution
- **ID Univoco:** `HYG-WS-006`
- **Squadrone / Categoria:** `[HYGIENE]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `tests/master_e2e_runner.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Opaque-box regression across multi-tier test suites.
- **Specifica Tecnica della Remediation:** All 521 tests passing across tier 1, tier 2, tier 3, and tier 4.
- **Test Avversariale Richiesto:** `execute_test_suite`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [HYG-WS-007] Guardian Watchdog daemon verification entrypoint
- **ID Univoco:** `HYG-WS-007`
- **Squadrone / Categoria:** `[HYGIENE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `tools/guardian_watchdog_daemon.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Missing standalone watchdog verification entrypoint in CI.
- **Specifica Tecnica della Remediation:** Create tools/guardian_watchdog_daemon.py supporting --check flag.
- **Test Avversariale Richiesto:** `run_watchdog_check`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [HYG-WS-008] Dedicated E2E run_all_e2e.py execution entrypoint
- **ID Univoco:** `HYG-WS-008`
- **Squadrone / Categoria:** `[HYGIENE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `tests/e2e/run_all_e2e.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Missing runner script at tests/e2e/run_all_e2e.py.
- **Specifica Tecnica della Remediation:** Create tests/e2e/run_all_e2e.py delegating to execute_test_suite.
- **Test Avversariale Richiesto:** `execute_test_suite`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [HYG-WS-009] Elimination of banned dummy and mock identifiers
- **ID Univoco:** `HYG-WS-009`
- **Squadrone / Categoria:** `[HYGIENE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/base/agentic_models.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Use of banned generic names like input_data and result.
- **Specifica Tecnica della Remediation:** Refactor to raw_action_input and execution_outcome_map.
- **Test Avversariale Richiesto:** `test_agentic_api_endpoints`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [HYG-WS-010] Zero-Mock Policy compliance across all source trees
- **ID Univoco:** `HYG-WS-010`
- **Squadrone / Categoria:** `[HYGIENE]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medfactory/src/`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Placeholder stubs (pass, ..., return {}) in clinical code paths.
- **Specifica Tecnica della Remediation:** Pure production implementations with verified domain logic.
- **Test Avversariale Richiesto:** `test_srs_tooling.py`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [HYG-WS-011] Micro-file modularization under 350 lines target
- **ID Univoco:** `HYG-WS-011`
- **Squadrone / Categoria:** `[HYGIENE]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/base/sdui_models.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Bloated monolithic source files violating maintainability limits.
- **Specifica Tecnica della Remediation:** Split logic into interfaces, base models, and implementations.
- **Test Avversariale Richiesto:** `test_sdui_serialization_emitter`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [HYG-WS-012] Automated SRS catalog deduplication and validation
- **ID Univoco:** `HYG-WS-012`
- **Squadrone / Categoria:** `[HYGIENE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `tools/srs_dedup_and_cleaner.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Duplicate headers or inconsistent numbering in 6600-line SRS.
- **Specifica Tecnica della Remediation:** Automated deduplication script cleaning redundant blocks.
- **Test Avversariale Richiesto:** `test_srs_tooling.py`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [HYG-WS-013] Multi-pass SRS recursive curator certification
- **ID Univoco:** `HYG-WS-013`
- **Squadrone / Categoria:** `[HYGIENE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `tools/srs_multipass_curator.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Ambiguous specifications or unreferenced architectural identifiers.
- **Specifica Tecnica della Remediation:** Multi-pass curator validating document and appending certificate.
- **Test Avversariale Richiesto:** `test_srs_tooling.py`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [HYG-WS-014] Clean Git working directory without orphan test databases
- **ID Univoco:** `HYG-WS-014`
- **Squadrone / Categoria:** `[HYGIENE]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `tests/conftest.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Temporary SQLite files left on disk after test suite execution.
- **Specifica Tecnica della Remediation:** tempfile and tmp_path fixtures cleaning up resources on session exit.
- **Test Avversariale Richiesto:** `test_sqlite_wal_pool`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [HYG-WS-015] Safe loopback IP binding invariant (127.0.0.1)
- **ID Univoco:** `HYG-WS-015`
- **Squadrone / Categoria:** `[HYGIENE]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `MedPlatform.bat`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Binding to 0.0.0.0 exposing clinical data to local network.
- **Specifica Tecnica della Remediation:** Strict binding to 127.0.0.1 across FastAPI, Vite, and Rust host.
- **Test Avversariale Richiesto:** `test_host_process_lifecycle_transitions`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

### [HYG-WS-016] Canonical manifest hashing with BLAKE3 and SHA-256
- **ID Univoco:** `HYG-WS-016`
- **Squadrone / Categoria:** `[HYGIENE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medfactory/src/packager/base/medpack_hasher.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Non-deterministic manifest serialization causing signature failures.
- **Specifica Tecnica della Remediation:** Canonical JSON serialization with sorted keys and UTF-8 encoding.
- **Test Avversariale Richiesto:** `test_zstd_dictionary_and_medpack_build`
- **Stato:** `- [x] FIXED (commit 9d17fc0 & jules-10597320801920196113-5ca2da30)`

---
