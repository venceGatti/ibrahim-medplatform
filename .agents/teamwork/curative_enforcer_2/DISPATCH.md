# Task Assignment: Forensic Integrity & Dogma Auditor

**Agent Name**: `curative_enforcer_2`
**Role**: Forensic Auditor
**Working Directory**: `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\curative_enforcer_2\`
**Parent Conversation ID**: `08e2b854-b488-42b0-870d-50aa95cc0a19`

## Primary Mandates:
1. **Zero-Mock & Lexical Pattern Forensic Inspection**:
   - Perform recursive static analysis across the entire codebase (`medfactory/`, `medclient/`, `tests/`).
   - Scan for forbidden markers and anti-patterns:
     - Costrutti di bypass: `pass`, `...` (Ellipsis), `noop()`, blocchi vuoti `{}`.
     - Valori sentinella arbitrari: `return null`, `return undefined`, `return None`, `return {}`, `return []`, `return 0`, `return true`, `return 45.0`.
     - Placeholder: `todo!()`, `unimplemented!()`, `unreachable!()`, `throw new Error("TODO")`.
     - Pattern lessicali vietati: `*mock*`, `*stub*`, `*fake*`, `*dummy*`, `*spy*`, `*simul*`, `*sample*`, `*placeholder*`, `*temp*`, `*tmp*`, `*draft*`, `*wip*`, `*dry_run*`, `*bypass*`, `DEMO_BYPASS`.
     - Identificatori privi di semantica di dominio: `data`, `obj`, `item`, `val`, `res`, `result`, `payload`, `foo`, `bar`, `baz`, `temp_db_path`, `samples`.
     - Soppressioni asettiche dell'errore: `except: pass`, `except Exception: pass`, `catch (...) {}`.
     - Mock framework nei flussi core: `@patch`, `@mock`, `@unittest.mock`, `jest.fn()`.
2. **Curative Assumptions Verification (ROA-01 to ROA-24)**:
   - Verify that all operational assumptions in `AUDIT_AND_ASSUMPTIONS.md` are genuinely implemented and respected in production code.
3. **Micro-File & Production Standards**:
   - Check file lengths: maximum 300–450 lines per source file.
   - Check directory hierarchy: `interfaces/`, `base/`, `implementations/`.
   - Check dependency pinning: exact pinned versions in `pyproject.toml`, `requirements.txt`, `Cargo.toml`, and `package.json`.
4. **Output Requirements**:
   - Write comprehensive forensic audit report in `analysis.md` in your working directory.
   - Write structured `handoff.md` with: Observation, Logic Chain, Caveats, Conclusion, Verification Method, and an explicit **CLEAN** or **INTEGRITY VIOLATION** verdict.


## 2026-10-31T17:39:21Z
You are curative_enforcer_2, operating in c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\curative_enforcer_2\.
Your parent conversation ID is 08e2b854-b488-42b0-870d-50aa95cc0a19.

You MUST read c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\ORIGINAL_REQUEST.md before starting work.
Also read:
- c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\curative_enforcer_2\DISPATCH.md
- Previous audit: c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\curative_enforcer_1\handoff.md and analysis.md
- c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\AUDIT_AND_ASSUMPTIONS.md (ROA-01 to ROA-24)
- c:\Users\vence\Downloads\projects\ibrahim\PROJECT.md
- Codebases: medfactory/, medclient/core-rust/, medclient/sidecar-python/, medclient/frontend-react/, tests/

Your task:
1. Forensic integrity verification: scan all files for banned tokens:
   - DEMO_BYPASS, return 45.0
   - ... (Ellipsis) inside Field(...)
   - empty pass statements or except Exception: pass
   - generic identifiers: temp_db_path, samples, payload, res, val, data, item, result
   - placeholder tokens: todo!(), unimplemented!(), unreachable!(), throw new Error("TODO")
   - mock/dummy/stub markers or test double frameworks in production code
2. Verify that all 24 operational assumptions (ROA-01 to ROA-24) are faithfully honored.
3. Verify file line limits (<=300-450 lines) and directory structure (interfaces/, base/, implementations/).
4. Write your comprehensive forensic report in analysis.md and structured handoff.md (Observation, Logic Chain, Caveats, Conclusion, Verification Method) in your working directory with an explicit CLEAN or INTEGRITY VIOLATION verdict. Use send_message to notify your parent when complete.


## 2026-10-31T17:43:24Z
[Message] timestamp=2026-10-31T17:43:24Z sender=08e2b854-b488-42b0-870d-50aa95cc0a19 priority=MESSAGE_PRIORITY_HIGH content=**Context**: Audit Forense prioritario su assenza di mock/dati fittizi nel Frontend React SDUI.

**Content**:
Verifica con attenzione forense i file del frontend React:
`medclient/frontend-react/src/implementations/MedClientAppShell.tsx`
`medclient/frontend-react/src/store/useMedClientStore.ts`
`medclient/frontend-react/src/implementations/SidecarIpcClient.ts`
e tutti i componenti SDUI.
Accertati che non vengano utilizzati costrutti fittizi, costanti statiche segnaposto o fallback silenziosi che simulano risposte del backend anziché eseguire chiamate HTTP reali al sidecar su `127.0.0.1:8765`.
Qualsiasi presenza di mock o bypass nel runtime del frontend costituisce violazione di integrità da segnalare in `handoff.md`.

**Action**: Esegui scansione statica e di flusso su questi file e certifica l'autenticità dei flussi dati.
