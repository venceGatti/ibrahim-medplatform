## 2026-10-30T22:52:04Z

From: 123b80e3-ef7e-4eee-9c78-b41caaecc724 (parent orchestrator)
Priority: MESSAGE_PRIORITY_HIGH

You are `cohesion_inspector_1` (Role: Cohesion & Contract Inspector) in the MedPlatform multi-agent pyramid.

Your working directory is:
`c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\cohesion_inspector_1\`

You MUST read the original request before starting:
`c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\ORIGINAL_REQUEST.md`

Key References:
1. `c:\Users\vence\Downloads\projects\ibrahim\PROJECT.md`
2. `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\AUDIT_AND_ASSUMPTIONS.md`
3. Codebases:
   - `medfactory/src/` (Python build-time engine)
   - `medclient/core-rust/src/` (Rust Tauri desktop host)
   - `medclient/sidecar-python/src/` (FastAPI sidecar)
   - `tests/` (E2E contracts and test runner)

Your Objectives:
1. Audit Cross-Boundary Cohesion between different languages and components:
   - Python MedFactory `.medpack` generation <-> Rust Core `med-asset://` protocol.
   - Rust Core IPC manager <-> Python FastAPI sidecar (`X-Tauri-IPC-Secret`, dynamic port, stdin token).
   - Python FastAPI sidecar <-> React SDUI 4-block schema (`ClinicalSheetBlock`, `SymptomMatcherBlock`, `DrugSafetyBlock`, `ExamSimulatorBlock`).
   - SQLite WAL database schema parity between MedFactory database compiler and MedClient SQLite connection pool (`active_db.json`, `module_kb.sqlite`).
2. Verify Contract Parity:
   - Verify signatures, types, preconditions, and return structures across language boundaries (Rust structs vs Python Pydantic models vs JSON).
   - Confirm that client requests and server responses match 100% on both sides with zero silent field mismatches.
   - Verify Agentic API contract parity (`/agent/health`, `/agent/state`, `/agent/execute`, `/agent/schema`).
3. Report any cohesion gap, type skew, or contract mismatch:
   - Write your detailed report in `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\cohesion_inspector_1\cohesion_report.md`.
   - Write your handoff in `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\cohesion_inspector_1\handoff.md`.
   - Send completion message to parent orchestrator. Remember you MUST use send_message. You are read-only regarding codebase source files.
