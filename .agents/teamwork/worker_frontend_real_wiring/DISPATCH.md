# Task Assignment: Frontend Real SDUI & Sidecar IPC Wiring Worker

**Agent Name**: `worker_frontend_real_wiring`
**Role**: Frontend Real SDUI Wiring Worker
**Working Directory**: `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\worker_frontend_real_wiring\`
**Parent Conversation ID**: `08e2b854-b488-42b0-870d-50aa95cc0a19`

## MANDATORY INTEGRITY WARNING
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Exclusive Write Ownership:
You EXCLUSIVELY own all files under:
`medclient/frontend-react/`

## Primary Mandates:
1. **Purge ALL Mock/Default Fallback States**:
   - In `medclient/frontend-react/src/implementations/MedClientAppShell.tsx` and `medclient/frontend-react/src/store/useMedClientStore.ts`, purge all static placeholder blocks (`DEFAULT_CLINICAL_SHEET`, `DEFAULT_SYMPTOM_MATCHER`, `DEFAULT_DRUG_SAFETY`, `DEFAULT_EXAM_BLOCK`).
2. **Real Sidecar IPC Fetch Wiring**:
   - Implement authentic HTTP REST calls via `SidecarIpcClient.ts` to `http://127.0.0.1:8765`:
     - `/api/v3/engine/evaluate` (differential diagnostic ranking $\to$ updates `SymptomMatcherBlock`).
     - `/api/v3/pharma/evaluate` (CYP450, QTc, Triple Whammy, CKD-EPI $\to$ updates `DrugSafetyBlock`).
     - `/api/v3/sheets/{sheet_id}` (retrieves real clinical Markdown $\to$ updates `ClinicalSheetBlock`).
     - `/api/v3/exam/evaluate` (MCQ, DAG scenarios, raycast hotspots $\to$ updates `ExamSimulatorBlock`).
   - Strictly include header `X-Tauri-IPC-Secret` (ROA-23) obtained from Tauri store or runtime environment.
   - Implement resilient error handling (logging to stderr / UI alert state, but ZERO fake mock data).
3. **Verify Build**:
   - In `medclient/frontend-react/`, verify compilation: `npm run build` (or `npx vitest run`).
4. **Output Requirements**:
   - Write `changes.md` and structured `handoff.md` with build logs in your working directory. Use `send_message` to notify your parent when complete.


## 2026-10-31T17:44:11Z
You are worker_frontend_real_wiring, operating in c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\worker_frontend_real_wiring\.
Your parent conversation ID is 08e2b854-b488-42b0-870d-50aa95cc0a19.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

You MUST read c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\ORIGINAL_REQUEST.md before starting work.
Also read:
- c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\worker_frontend_real_wiring\DISPATCH.md
- c:\Users\vence\Downloads\projects\ibrahim\PROJECT.md
- c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\AUDIT_AND_ASSUMPTIONS.md (ROA-01 to ROA-24)
- Existing frontend files in c:\Users\vence\Downloads\projects\ibrahim\medclient\frontend-react\

Exclusive Write Ownership:
You EXCLUSIVELY own all files under medclient/frontend-react/.

Your task:
1. In medclient/frontend-react/src/implementations/MedClientAppShell.tsx and medclient/frontend-react/src/store/useMedClientStore.ts: purge all static placeholder blocks (DEFAULT_CLINICAL_SHEET, DEFAULT_SYMPTOM_MATCHER, DEFAULT_DRUG_SAFETY, DEFAULT_EXAM_BLOCK).
2. Real Sidecar IPC Fetch Wiring:
   Implement authentic HTTP REST calls via SidecarIpcClient.ts to http://127.0.0.1:8765:
   - /api/v3/engine/evaluate
   - /api/v3/pharma/evaluate
   - /api/v3/sheets/{sheet_id}
   - /api/v3/exam/evaluate
   Strictly include header X-Tauri-IPC-Secret (ROA-23). Zero fake mock fallback: if backend is unreachable, set state to error/connecting with proper UI indicators.
3. Build Verification:
   Run npm run build in medclient/frontend-react/ and ensure zero TypeScript or bundling errors.
4. Write changes.md and structured handoff.md in your working directory and use send_message to notify your parent when complete.


## 2026-10-31T18:01:34Z
**Context**: Risultati dell'Audit Forense (`curative_enforcer_2`) specifici per il Frontend React.

**Content**:
L'auditor forense ha rilevato 3 violazioni specifiche nel frontend da correggere immediatamente:
1. **`MedClientAppShell.tsx`**: Rimuovere definitivamente gli oggetti `DEFAULT_CLINICAL_SHEET`, `DEFAULT_SYMPTOM_MATCHER`, `DEFAULT_DRUG_SAFETY`, `DEFAULT_EXAM_BLOCK` e connettere lo store e la vista alle chiamate reali via `SidecarIpcClient.ts`.
2. **`ExamSimulatorBlockView.tsx` (righe 87-96)**: VIOLAZIONE DI SIMULAZIONE - Rimuovere il controllo NLI locale basato su sottostringhe (`trimmedHypothesis.includes(referencePremise)`). La valutazione della risposta aperta dello studente DEVE effettuare una chiamata HTTP reale al backend verso `/api/v3/exam/evaluate` che esegue l'autentico Cross-Encoder NLI ONNX INT8.
3. **`SymptomMatcherBlockView.tsx` (righe 11-32, 65-87)**: VIOLAZIONE DI DATI CABLATI - Rimuovere il dizionario fisso `COLLOQUIAL_HPO_DICTIONARY` e la ricerca Levenshtein locale. La ricerca dei sintomi e il ranking differenziale DEVONO interrogare fisicamente l'endpoint `/api/v3/engine/evaluate` del sidecar.

Verifica che `npm run build` e `npx vitest run` abbiano esito positivo (exit code 0).

**Action**: Implementa queste correzioni nel codice frontend per sanare i rilievi forensi.
