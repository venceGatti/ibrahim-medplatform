# Dispatch: Explorer Cohesion Remediation

## Task
You are the Cross-Boundary Cohesion & Runtime Wiring Explorer (`explorer_cohesion_remediation`).
A contract and cohesion audit conducted by `cohesion_inspector_1` resulted in a **REQUEST_CHANGES** verdict due to gaps between MedFactory, Rust MedClient Core, and the Python Sidecar.

Your role is strictly READ-ONLY exploration. Do NOT edit or write code files. Formulate an exact technical remediation plan and write your structured report to `.agents/teamwork/explorer_cohesion_remediation/analysis.md` and `handoff.md`.

## Mandatory Reading
1. `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\ORIGINAL_REQUEST.md` (Verbatim user requests)
2. `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\cohesion_inspector_1\handoff.md` (Cross-Boundary Cohesion Audit)
3. `c:\Users\vence\Downloads\projects\ibrahim\PROJECT.md`
4. `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\AUDIT_AND_ASSUMPTIONS.md` (especially ROA-05, ROA-07, ROA-13, ROA-14)
5. `c:\Users\vence\Downloads\projects\ibrahim\medclient\core-rust\src\implementations\asset_protocol.rs`
6. `c:\Users\vence\Downloads\projects\ibrahim\medclient\core-rust\src\implementations\sidecar.rs`

## Gaps to Map and Provide Exact Architectural Solutions For:
1. **MedFactory Packaging vs Rust Zero-Copy `med-asset://`**:
   - `medpack_assembler.py` was bundling images into a single `blob.bin` with CBOR offsets, while Rust's `asset_protocol.rs` strictly unpacks and seeks loose `{sha256}.webp` files in the `media/` directory inside the `.medpack` ZIP archive, and expects `zstd.dict` at the root of the `.medpack`.
   - Provide the exact specification for `medpack_assembler.py` to archive loose `media/{sha256}.webp` files and `zstd.dict`.
2. **Missing Python Sidecar CLI Entrypoint & Process Environment**:
   - Rust `sidecar.rs` spawns the Python sidecar process with command-line flag `--port=<port>` and pipes the ephemeral IPC token to `stdin`.
   - `medclient/sidecar-python/` currently lacks `src/main.py` entrypoint.
   - Plan `src/main.py`: parse `--port` (default 8000), read the token from `sys.stdin.readline().strip()`, store it into `app.state.ipc_token`, and start `uvicorn.run(app, host="127.0.0.1", port=port)`.
   - Note in Rust `sidecar.rs`: pass `MEDCLIENT_PARENT_PID` environment variable so the reverse watchdog in `parent_watchdog.py` monitors the parent process.
3. **SDUI Class Collision & Schema Skew**:
   - There are two distinct classes named `DrugSafetyBlock`: one in `base/sdui_models.py` (polymorphic SDUI block) and one in `base/pharmacology_models.py` (internal engine result).
   - `/api/v3/pharma/evaluate` returns the internal model instead of the SDUI envelope.
   - Plan: rename internal pharmacology model to `DrugSafetyEvaluationResult` in `pharmacology_models.py`, and map it into `base/sdui_models.py` `DrugSafetyBlock` with `block_type="DrugSafetyBlock"`.
   - Fix `selected_symptoms` in `SymptomMatcherBlock` to be `List[str]`.
4. **SQLite Knowledge Base Direct Connection**:
   - `cyp450_engine.py` and `csr_ranker.py` contain hardcoded Python dictionary fallbacks (`KNOWN_PROFILES`).
   - Plan how both engines should query `SqliteConnectionPool` directly against `substances`, `clinical_atc`, and `rel_icd10_hpo` in `module_kb.sqlite`.

## Deliverables
- Detailed architectural analysis and file changes in `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\explorer_cohesion_remediation\analysis.md`
- 5-Component Handoff Report in `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\explorer_cohesion_remediation\handoff.md`
