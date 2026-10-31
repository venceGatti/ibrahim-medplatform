# Task Assignment: Cross-Boundary Cohesion & Contract Parity Inspector

**Agent Name**: `cohesion_inspector_2`
**Role**: High-Reliability Reviewer & Cross-Boundary Cohesion Inspector
**Working Directory**: `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\cohesion_inspector_2\`
**Parent Conversation ID**: `08e2b854-b488-42b0-870d-50aa95cc0a19`

## Primary Mandates:
1. **End-to-End Cohesion & Signature Verification**:
   - Inspect cross-boundary code interactions between:
     - MedFactory (`medfactory/`)
     - MedClient Core Rust (`medclient/core-rust/`)
     - MedClient Sidecar Python (`medclient/sidecar-python/`)
     - MedClient Frontend React (`medclient/frontend-react/`)
     - E2E Tests (`tests/`)
   - Verify that whenever a method/function requires specific input parameters, the calling code provides them with exact type and semantic adherence.
2. **Server-Client Request/Response Parity**:
   - Verify that HTTP requests, headers (`X-Tauri-IPC-Secret`), endpoint URLs, and payload formats match 100% on both sides.
   - Verify SDUI 4-block polymorphism: `ClinicalSheetBlock`, `SymptomMatcherBlock`, `DrugSafetyBlock`, `ExamSimulatorBlock`. Check that field names and types match between Python emitters, Pydantic schemas, and TypeScript interfaces.
   - Verify asset requests via `med-asset://`: loose WebP images in `media/{sha256}.webp` and root `zstd.dict` (114,688 Bytes).
   - Verify database hot-swap contract: `active_db.json` pointer format and SQLite WAL connections.
3. **Architectural Plan & Critical Analysis Conformance**:
   - Verify that the architectural plan in `PROJECT.md` and the curative solutions in `AUDIT_AND_ASSUMPTIONS.md` (ROA-01 to ROA-24) are faithfully executed in the new implementations.
4. **Output Requirements**:
   - Write comprehensive review findings to `analysis.md` in your working directory.
   - Write structured `handoff.md` with: Observation, Logic Chain, Caveats, Conclusion, Verification Method, and an explicit **APPROVE** or **REQUEST_CHANGES** verdict.


## 2026-10-31T17:38:49Z
You are cohesion_inspector_2, operating in c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\cohesion_inspector_2\.
Your parent conversation ID is 08e2b854-b488-42b0-870d-50aa95cc0a19.

You MUST read c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\ORIGINAL_REQUEST.md before starting work.
Also read:
- c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\cohesion_inspector_2\DISPATCH.md
- c:\Users\vence\Downloads\projects\ibrahim\PROJECT.md
- c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\AUDIT_AND_ASSUMPTIONS.md (ROA-01 to ROA-24)
- Previous inspection: c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\cohesion_inspector_1\handoff.md and analysis.md
- Codebases: medfactory/, medclient/core-rust/, medclient/sidecar-python/, medclient/frontend-react/, tests/

Your task:
1. End-to-end cohesion & signature verification: inspect cross-boundary interactions between all subsystems. If a method requires specific inputs, verify callers supply them with matching types.
2. Server-client request/response parity:
   - Check headers (X-Tauri-IPC-Secret), endpoint URLs, and payload formats.
   - Check SDUI 4-block polymorphism: ClinicalSheetBlock, SymptomMatcherBlock, DrugSafetyBlock, ExamSimulatorBlock. Check field names and types match between Python emitters, Pydantic schemas, and TypeScript interfaces in React.
   - Check asset requests via med-asset://: loose WebP images in media/{sha256}.webp and root zstd.dict (114,688 Bytes).
   - Check database hot-swap contract: active_db.json pointer format and SQLite WAL connections.
3. Verify adherence to PROJECT.md and AUDIT_AND_ASSUMPTIONS.md.
4. Write your review in analysis.md and structured handoff.md (Observation, Logic Chain, Caveats, Conclusion, Verification Method) in your working directory with an explicit APPROVE or REQUEST_CHANGES verdict. Use send_message to notify your parent when complete.


## 2026-10-31T17:43:08Z
**Context**: Focus Prioritario Bloccante su Coesione e Parità Contrattuale Frontend SDUI <-> FastAPI Sidecar.

**Content**:
Verifica con la massima priorità il collegamento reale tra il frontend React SDUI (`MedClientAppShell.tsx`, `useMedClientStore.ts`, `SidecarIpcClient.ts`) e gli endpoint FastAPI (`/api/v3/engine/evaluate`, `/api/v3/pharma/evaluate`, `/api/v3/sheets/{sheet_id}`, `/api/v3/exam/evaluate`).
Accertati che:
1. Non vi siano fallback su stati statici o finti (`DEFAULT_CLINICAL_SHEET`, `DEFAULT_SYMPTOM_MATCHER`, `DEFAULT_DRUG_SAFETY`, `DEFAULT_EXAM_BLOCK`) nel flusso reale.
2. I parametri passati dalle chiamate fetch corrispondano esattamente ai modelli Pydantic attesi dagli endpoint del server (inclusi tipi, nomi dei campi, e header `X-Tauri-IPC-Secret`).
3. La risposta serializzata dal server venga parsata e visualizzata fedelmente dallo store e dai componenti SDUI.

**Action**: Includi questa verifica nel tuo report di analisi (`analysis.md`) e nel verdetto finale in `handoff.md`.
