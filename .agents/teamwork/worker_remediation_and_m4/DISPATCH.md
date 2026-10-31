# Dispatch: Worker Remediation & Milestone M4 Frontend Construction

## Task
You are `worker_remediation_and_m4` (Role: Lead Remediation & Frontend Construction Engineer).
You have exclusive write ownership to execute the complete Iteration 2 Remediation and Milestone M4 Frontend Construction based on the analyses delivered by `explorer_integrity_remediation`, `explorer_cohesion_remediation`, and `explorer_test_remediation_and_m4_plan`.

## MANDATORY INTEGRITY WARNING (VERBATIM):
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Mandatory Reading Before Modifying Code:
1. `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\ORIGINAL_REQUEST.md` (Verbatim user requests)
2. `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\explorer_integrity_remediation\analysis.md` (Integrity remediation blueprint)
3. `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\explorer_cohesion_remediation\analysis.md` (Cohesion, packaging & wiring blueprint)
4. `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\explorer_test_remediation_and_m4_plan\analysis.md` (Real tests blueprint & M4 frontend architecture)
5. `c:\Users\vence\Downloads\projects\ibrahim\PROJECT.md`
6. `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\AUDIT_AND_ASSUMPTIONS.md`

## Four Operational Workstreams:

### Workstream 1: Forensic Integrity Remediation
1. In `medclient/sidecar-python/src/api/agentic_routes.py`:
   - Purge `"DEMO_BYPASS"` completely. Authenticate strictly against `request.app.state.ipc_token`.
   - Remove fake nominal fallback `return 45.0` and empty `except Exception: pass`. Compute real RSS using `psutil.Process().memory_info().rss / (1024 * 1024)`.
2. In `medclient/sidecar-python/src/base/` (`educational_models.py`, `diagnostic_models.py`, `database_models.py`, `agentic_models.py`):
   - Replace all 34 occurrences of `Field(...)` ellipsis with standard Pydantic v2 required field syntax.
3. In `medclient/sidecar-python/src/base/exceptions.py`:
   - Replace all 11 `pass` statements with descriptive exception docstrings or `super().__init__(message)`.
4. In `medclient/sidecar-python/src/api/server.py` and `implementations/sqlite_pool.py`:
   - Remove `except Exception: pass` and replace with formal structured diagnostic logging.
5. Systematic Identifier Renaming (Zero banned tokens):
   - In `medfactory/src/database/`: rename `temp_db_path` to `staging_database_path`.
   - In `medfactory/src/compression/`: rename `samples`/`sample` to `corpus_record_stream`/`training_record`.
   - In `medclient/sidecar-python/`: rename `payload` to specific domain names (`action_parameter_map`, `vignette_evaluation_request`, `sdui_envelope`).
   - In routes: rename `res`, `cyp_res`, `qtc_res`, `tw_res` to `qtc_evaluation_summary`, `cyp_clearance_summary`, `triple_whammy_report`.
   - In `blue_green_swap.py` and `fsrs_scheduler.py`: rename `data`, `val` to `active_db_manifest`, `stability_history_delta`.

### Workstream 2: Cross-Boundary Cohesion & Runtime Wiring
1. In `medfactory/src/packager/implementations/medpack_assembler.py` and `manifest_models.py`:
   - Package loose `media/{sha256}.webp` files directly in the archive and include `zstd.dict` (114,688 Bytes) at archive root. Remove `blob.bin` and CBOR packaging.
2. In `medclient/sidecar-python/src/main.py`:
   - Create entrypoint parsing `--port` (default 8000), reading ephemeral token from `sys.stdin.readline().strip()`, initializing `create_app(ipc_token=...)`, and running `uvicorn.run(app, host="127.0.0.1", port=port)`.
3. In `medclient/core-rust/src/implementations/sidecar.rs`:
   - Add `command_builder.env("MEDCLIENT_PARENT_PID", std::process::id().to_string());` so `ReverseWatchdog` monitors parent.
4. SDUI Parity & Schema Skew:
   - In `medclient/sidecar-python/src/base/pharmacology_models.py`: rename internal model to `DrugSafetyEvaluationResult`.
   - In `medclient/sidecar-python/src/api/sdui_routes.py`: return canonical `sdui_models.DrugSafetyBlock`.
   - In `medclient/sidecar-python/src/base/sdui_models.py`: set `selected_symptoms: List[str]`.
5. Direct SQLite KB Connection:
   - Eradicate `KNOWN_PROFILES` from `cyp450_engine.py` and query `clinical_atc` and `substances` via `db_pool`.
   - Wire `csr_ranker.py` to query `module_kb.sqlite` directly.

### Workstream 3: Real Test Suite Remediation in `tests/`
1. In `tests/conftest.py`:
   - Provide authentic fixtures importing and creating real SQLite test KB, real `SqliteConnectionPool`, and real FastAPI `TestClient`.
2. Rewrite test files across `tests/tier1_features/`, `tests/tier2_boundaries/`, `tests/tier3_cross_features/`, `tests/tier4_real_world/`:
   - Import real classes from `medfactory` and `medclient.sidecar_python`.
   - Execute genuine layout slicing, table normalization, ontology queries, SQLite WAL queries, log-odds calculations, CYP450 prodrug evaluation, and FSRS intervals.
   - Eliminate 100% of tautologies and local dummy dictionaries.

### Workstream 4: Milestone M4 React 19 SDUI Frontend & Tauri Integration
1. Directory: `medclient/frontend-react/`
2. Pinned `package.json`: `react@19.0.0`, `vite@6.0.7`, `typescript@5.7.2`, `tailwindcss@3.4.17`, `zustand@5.0.2`, `@tauri-apps/api@2.2.0`, `katex@0.16.21`.
3. Architecture & Micro-Files (all files <= 300-450 lines in `interfaces/`, `base/`, `implementations/`):
   - F41: Tauri IPC client wrapper (`interfaces/IpcClient.ts`, `implementations/TauriIpcClient.ts`).
   - F42: Zustand persistent store preserving DOM & state across tabs (`store/useMedStore.ts`).
   - F43: Polymorphic SDUI 4-block engine with Dual Registry Aliasing (`components/sdui/SduiBlockRenderer.tsx`, `ClinicalSheetBlockComponent`, `SymptomMatcherBlockComponent`, `DrugSafetyBlockComponent`, `ExamSimulatorBlockComponent`).
   - F44: Virtual windowing maintaining <30 mounted DOM nodes for large symptom trees (`components/virtual/VirtualList.tsx`).
   - F45: Zero-copy `med-asset://` custom protocol integration (`<img src="med-asset://...">`).
   - F46: Singleton WebGL broker with `MAX_ACTIVE_CONTEXTS = 1` and automatic context loss recovery (`services/WebGLBroker.ts`).
   - F47: Agentic API client exposing UI state (`services/AgenticClient.ts`).
   - F48: High-DPI physical coordinate normalization for Even-Odd raycasting hotspots (`utils/raycasting.ts`).

## Verification Requirements:
1. Run `cargo check`, `cargo clippy`, and `cargo test` on `medclient/core-rust/` (must pass with 0 warnings).
2. Run pytest on `medclient/sidecar-python/tests` (must pass 100%).
3. Run pytest on `medfactory/tests` (must pass 100%).
4. Run master test suite `python tests/e2e_runner.py --tier all` (must pass 100% against real production imports).
5. Verify absence of banned tokens (`DEMO_BYPASS`, `Field(\.\.\.`, `pass`, `temp_db_path`, `samples`, `payload`, `res`) via ripgrep.
6. Deliver detailed report in `changes.md` and 5-component `handoff.md`.

## 2026-10-30T23:38:20Z
You are worker_remediation_and_m4 (Role: Lead Remediation & Frontend Construction Engineer).
Working directory: c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\worker_remediation_and_m4\
Original Request: c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\ORIGINAL_REQUEST.md
Dispatch Instructions: c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\worker_remediation_and_m4\DISPATCH.md
Integrity Blueprint: c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\explorer_integrity_remediation\analysis.md
Cohesion Blueprint: c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\explorer_cohesion_remediation\analysis.md
Real Tests & M4 Blueprint: c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\explorer_test_remediation_and_m4_plan\analysis.md
Project Index: c:\Users\vence\Downloads\projects\ibrahim\PROJECT.md
Audit & Assumptions: c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\AUDIT_AND_ASSUMPTIONS.md

Execute the four workstreams specified in DISPATCH.md:
1. Workstream 1: Forensic Integrity Remediation (remove DEMO_BYPASS, replace 34 Field(...) ellipsis, remove pass, rename banned identifiers: temp_db_path, samples, payload, res, data, val).
2. Workstream 2: Cross-Boundary Cohesion & Wiring (package loose media/{sha256}.webp and zstd.dict in .medpack, implement sidecar main.py CLI, inject MEDCLIENT_PARENT_PID in Rust sidecar.rs, resolve SDUI class collision to DrugSafetyEvaluationResult, connect SQLite pool directly to cyp450_engine and csr_ranker).
3. Workstream 3: Real Test Suite Remediation in tests/ (transform tests/conftest.py and test files to import real classes from medfactory and medclient.sidecar_python and execute authentic calculations).
4. Workstream 4: Milestone M4 Frontend Construction (create medclient/frontend-react/ with Vite, React 19, TypeScript, TailwindCSS, Zustand persistent store, polymorphic SDUI 4-block engine, virtual windowing, WebGL broker, and raycasting).

MANDATORY INTEGRITY WARNING: DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Run all builds and tests to verify:
- cargo check/clippy/test on medclient/core-rust/
- pytest on medclient/sidecar-python/tests
- pytest on medfactory/tests
- e2e runner python tests/e2e_runner.py --tier all
- verify 0 banned markers remain

Record all file changes in changes.md and deliver a complete 5-component handoff report in handoff.md. Send a completion message when done.
