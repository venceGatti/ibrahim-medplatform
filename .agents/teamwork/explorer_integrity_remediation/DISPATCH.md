# Dispatch: Explorer Integrity Remediation

## Task
You are the Forensic Integrity Remediation Explorer (`explorer_integrity_remediation`).
A forensic audit conducted by `curative_enforcer_1` resulted in an **INTEGRITY VIOLATION** under User Global Rules (Zero Mock, Zero Dummy, Banned Token List, Non-Suppression Rule).

Your role is strictly READ-ONLY exploration. Do NOT edit or write code files. Formulate a surgical, file-by-file remediation plan and write your structured report to `.agents/teamwork/explorer_integrity_remediation/analysis.md` and `handoff.md`.

## Mandatory Reading
1. `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\ORIGINAL_REQUEST.md` (Verbatim user requests)
2. `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\curative_enforcer_1\curative_audit.md` (Full Forensic Audit Evidence)
3. `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\curative_enforcer_1\handoff.md`
4. `c:\Users\vence\Downloads\projects\ibrahim\PROJECT.md`
5. `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\AUDIT_AND_ASSUMPTIONS.md`

## Violations to Map and Provide Exact Surgical Fixes For:
1. **Bypass Token**:
   - `medclient/sidecar-python/src/api/agentic_routes.py:55`: `"DEMO_BYPASS"`. Plan the strict removal of `"DEMO_BYPASS"` and replacement with unconditional cryptographic comparison against `request.app.state.ipc_token`.
2. **Ellipsis `...` in Pydantic `Field`**:
   - 34 occurrences of `Field(...)` across `medclient/sidecar-python/src/base/educational_models.py`, `diagnostic_models.py`, `database_models.py`, `agentic_models.py`. Plan replacement with explicit default values or Pydantic `Field(default=...)` / `Field(description=...)` without Ellipsis.
3. **Empty statements & Aseptic Error Suppression**:
   - `medclient/sidecar-python/src/api/server.py:29-30`, `api/agentic_routes.py:47-49`, `implementations/sqlite_pool.py:57-58`: `except Exception: pass` and silent fallback `return 45.0`. Plan formal structured logging via Python standard logging or re-raising, and computing real RSS via `psutil.Process().memory_info().rss / (1024 * 1024)`.
   - `medclient/sidecar-python/src/base/exceptions.py`: 11 `pass` statements. Plan replacing `pass` with descriptive docstrings or constructor `super().__init__(message)`.
4. **Banned Identifiers**:
   - `temp_db_path` in `medfactory/src/database/` -> replace with `staging_sqlite_database_path`.
   - `samples` / `sample` in `medfactory/src/compression/` -> replace with `training_corpus_chunks` / `training_chunk`.
   - `payload` across `medclient/sidecar-python/src/` -> replace with specific domain entity names (`request_body`, `dispatch_envelope`, `sdui_block_data`).
   - `res`, `cyp_res`, `qtc_res`, `tw_res` in routes -> replace with `endpoint_response`, `cyp450_evaluation_outcome`, `qtc_risk_outcome`, `triple_whammy_outcome`.
   - `data`, `val` in `blue_green_swap.py`, `fsrs_scheduler.py`, `icd10_atc_ingestor.py` -> replace with semantic domain identifiers (`active_db_manifest`, `fused_hpo_weight`).

## Deliverables
- Detailed file-by-file replacement mapping in `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\explorer_integrity_remediation\analysis.md`
- 5-Component Handoff Report in `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\explorer_integrity_remediation\handoff.md`


## 2026-10-30T23:17:38Z
[Message from parent (123b80e3-ef7e-4eee-9c78-b41caaecc724)]
You are the Forensic Integrity Remediation Explorer (explorer_integrity_remediation).
Working directory: c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\explorer_integrity_remediation\
Original Request: c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\ORIGINAL_REQUEST.md
Dispatch Instructions: c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\explorer_integrity_remediation\DISPATCH.md
Forensic Audit Report: c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\curative_enforcer_1\curative_audit.md
Curative Enforcer Handoff: c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\curative_enforcer_1\handoff.md
Project Index: c:\Users\vence\Downloads\projects\ibrahim\PROJECT.md

Investigate the exact locations of all forensic integrity violations (DEMO_BYPASS, 34 Field(...) ellipsis, 14 pass statements, aseptic error suppression, fake return fallbacks, and banned identifiers: temp_db_path, samples, payload, res, data, val).
Formulate a surgical file-by-file replacement strategy. Do NOT edit code files. Write your analysis to c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\explorer_integrity_remediation\analysis.md and deliver a 5-component handoff in handoff.md. Send a completion message when done.


## 2026-10-30T23:33:19Z
[Message from parent (123b80e3-ef7e-4eee-9c78-b41caaecc724)]
**Context**: Status check on Forensic Integrity Remediation Strategy
**Content**: Both `explorer_cohesion_remediation` and `explorer_test_remediation_and_m4_plan` have completed and delivered their handoffs. Please report your progress on mapping the surgical replacements for `DEMO_BYPASS`, `Field(...)` ellipsis, `pass`, and banned identifiers.
**Action**: Update your progress.md and finalize your analysis.md and handoff.md.
