# Task Assignment: Master Construction, Remediation & Test Verification Worker

**Agent Name**: `worker_lead_remediation`
**Role**: Versatile Lead Worker
**Working Directory**: `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\worker_lead_remediation\`
**Parent Conversation ID**: `08e2b854-b488-42b0-870d-50aa95cc0a19`

## MANDATORY INTEGRITY WARNING
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Primary Mandates:
1. **Review Detailed Surgical Blueprints**:
   - Read `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\explorer_integrity_remediation\analysis.md` (Integrity remediation: purge `DEMO_BYPASS`, `return 45.0`, `Field(...)` ellipsis, `pass`, banned identifiers).
   - Read `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\explorer_cohesion_remediation\analysis.md` (Cohesion wiring: .medpack loose webp, sidecar `src/main.py` CLI, Rust `MEDCLIENT_PARENT_PID`, SDUI block naming parity, SQLite pool wiring).
   - Read `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\explorer_test_remediation_and_m4_plan\analysis.md` (Real test suite rewrite in `tests/`, Milestone M4 React 19 SDUI frontend).
2. **Implementation & Refactoring Execution**:
   - Workstream 1: Purge all remaining banned tokens, ellipsis, empty pass statements, and generic identifiers.
   - Workstream 2: Complete cross-boundary runtime wiring (sidecar CLI, reverse watchdog, zero-copy med-asset WebP, SDUI parity).
   - Workstream 3: Transform tests in `tests/` from tautological checks into real tests that import production modules from `medfactory` and `medclient.sidecar_python`.
   - Workstream 4: Verify and complete `medclient/frontend-react/` implementation (React 19, TypeScript, Tailwind, Zustand, SDUI blocks, WebGL broker, raycasting).
3. **Build & Test Verification**:
   - Execute all build and test commands:
     - `cargo check --manifest-path medclient/core-rust/Cargo.toml`
     - `cargo test --manifest-path medclient/core-rust/Cargo.toml`
     - `pytest medfactory/tests -v`
     - `pytest medclient/sidecar-python/tests -v`
     - `python tests/e2e_runner.py --tier all` (or pytest tests/)
     - Frontend build: `npm run build` in `medclient/frontend-react`
4. **Output Requirements**:
   - Document all changes in `changes.md` in your working directory.
   - Document passing build/test command logs and verification in `handoff.md`.


## 2026-10-31T17:39:02Z
You are worker_lead_remediation, operating in c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\worker_lead_remediation\.
Your parent conversation ID is 08e2b854-b488-42b0-870d-50aa95cc0a19.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

You MUST read c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\ORIGINAL_REQUEST.md before starting work.
Also read:
- c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\worker_lead_remediation\DISPATCH.md
- c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\explorer_integrity_remediation\analysis.md
- c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\explorer_cohesion_remediation\analysis.md
- c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\explorer_test_remediation_and_m4_plan\analysis.md
- c:\Users\vence\Downloads\projects\ibrahim\PROJECT.md
- c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\AUDIT_AND_ASSUMPTIONS.md (ROA-01 to ROA-24)

Your task:
1. Workstream 1: Purge any remaining banned tokens (DEMO_BYPASS, return 45.0, Field(...) ellipsis, pass, generic identifiers like payload, res, data, val, temp, samples, etc.).
2. Workstream 2: Complete cross-boundary runtime wiring: sidecar src/main.py CLI parsing --port and stdin token, reverse watchdog, zero-copy med-asset WebP, SDUI block naming parity (ClinicalSheetBlock, SymptomMatcherBlock, DrugSafetyBlock, ExamSimulatorBlock), SQLite pool wiring for CYP450 and CSR Ranker.
3. Workstream 3: Transform test suite in tests/ into real tests that import production modules from medfactory and medclient.sidecar_python, exercising real layout slicing, ontologies, SQLite WAL queries, log-odds diagnostics, and CYP450 prodrug evaluation.
4. Workstream 4: Verify and complete medclient/frontend-react/ implementation (React 19, TypeScript, Tailwind, Zustand, SDUI blocks, WebGL broker, raycasting).
5. Build & Test Verification:
   Run all required builds and tests:
   - pytest medfactory/tests -v
   - pytest medclient/sidecar-python/tests -v
   - cargo test --manifest-path medclient/core-rust/Cargo.toml
   - python tests/e2e_runner.py --tier all (or pytest tests/)
   - cd medclient/frontend-react && npm run build
6. Write changes.md and structured handoff.md with full verifiable logs in your working directory. Use send_message to notify your parent when complete.


## 2026-10-31T17:42:54Z
**Context**: Priorità Critica Bloccante dall'Utente - Collegamento Reale Frontend React SDUI <-> Backend FastAPI Sidecar.

**Content**:
L'utente ha riscontrato e ordinato formalmente quanto segue:
Il frontend React SDUI (`medclient/frontend-react/src/implementations/MedClientAppShell.tsx` e `medclient/frontend-react/src/store/useMedClientStore.ts`) NON deve mostrare stati cablati/mock (`DEFAULT_CLINICAL_SHEET`, `DEFAULT_SYMPTOM_MATCHER`, `DEFAULT_DRUG_SAFETY`, `DEFAULT_EXAM_BLOCK`).
Tutti i flussi devono essere REALMENTE e IMMEDIATAMENTE collegati agli endpoint HTTP reali del sidecar FastAPI su `http://127.0.0.1:8765`:
1. `/api/v3/engine/evaluate` per il differential ranking diagnostico (`SymptomMatcherBlock`).
2. `/api/v3/pharma/evaluate` per la sicurezza farmacologica, CYP450, QTc, Triple Whammy (`DrugSafetyBlock`).
3. `/api/v3/sheets/{sheet_id}` per le monografie cliniche statiche (`ClinicalSheetBlock`).
4. `/api/v3/exam/evaluate` per quesiti MCQ, scenari DAG ed hotspot (`ExamSimulatorBlock`).

Tutte le richieste fetch devono transitare via `SidecarIpcClient` con l'header di sicurezza `X-Tauri-IPC-Secret` (ROA-23). Nessun dato fittizio o stub nel flusso runtime: il frontend deve interrogare fisicamente il sidecar locale e aggiornare lo stato Zustand in tempo reale.

**Action**: Implementa immediatamente il collegamento reale del frontend con `SidecarIpcClient` ed elimina qualsiasi mockup/stato fittizio cablato nel flusso applicativo.


## 2026-10-31T17:44:34Z
**Context**: Aggiornamento Assegnazione File e Separazione Task Force.

**Content**:
È stato assegnato un worker dedicato in parallelo (`worker_frontend_real_wiring`) che ha la titolarità esclusiva di scrittura su tutti i file di `medclient/frontend-react/` per implementare il cablaggio reale delle chiamate fetch SDUI via `SidecarIpcClient` ed eliminare gli stati mock.

Di conseguenza, tu (`worker_lead_remediation`) hai titolarità esclusiva di scrittura su:
- `medclient/sidecar-python/` (rimozione token vietati, endpoint API, main.py CLI, SQLite pool)
- `medfactory/` (rimozione identificatori vietati, loose webp, zstd.dict)
- `tests/` (riscrittura test reali Tiers 1-4 con import reali da `medfactory` e `medclient.sidecar_python`)
NON modificare file in `medclient/frontend-react/` per evitare conflitti di scrittura. Esegui la suite di test per certificare il passaggio del 100% dei test.

**Action**: Procedi a implementare i tuoi moduli e a verificare `pytest` e `cargo test`.


## 2026-10-31T18:01:49Z
**Context**: Risultati dell'Audit Forense e Curativo (ROA-25..34) per il Backend Sidecar Python.

**Content**:
Gli audit di `curative_enforcer_2` e `critic_srs_curator_2` hanno evidenziato i seguenti punti da sanare nel backend:
1. **`medclient/sidecar-python/src/main.py` (righe 41-46)**: Rimuovere il blocco asettico `except Exception: pass` nella lettura di stdin, sostituendolo con logging diagnostico esplicito su `sys.stderr` o sollevamento di `SystemExit`.
2. **`medclient/sidecar-python/src/base/agentic_models.py`**:
   - Ridenominare l'identificatore generico `input_data` (linea 39) in `action_parameters` (mantenendo `validation_alias=AliasChoices(...)`).
   - Ridenominare la property `def result(self)` (linea 62) in `def execution_outcome(self)`.
3. **`medclient/sidecar-python/src/api/sdui_routes.py` (ROA-33)**: Assicurarsi che in `/api/v3/engine/evaluate` il calcolo delle probabilità a posteriori utilizzi il `LogSumExpNormalizer` (o `csr_ranker`) e che l'oggetto `nbq` (Next-Best-Question) utilizzi `ActiveDiscriminator` anziché restituire valori sentinella fissi.

Esegui la suite `pytest medclient/sidecar-python/tests -v` per confermare che tutti i test passino senza regressioni.

**Action**: Applica queste rifiniture nei file backend.


## 2026-10-31T18:09:12Z
**Context**: Rilievi Critici di Coesione e Runtime Crash da `cohesion_inspector_2`.

**Content**:
L'ispettore di coesione ha rilevato errori fatali e disallineamenti di schema nel backend da risolvere immediatamente:

1. **FATAL RUNTIME CRASH in `medclient/sidecar-python/src/api/sdui_routes.py` (righe 198 e 223)**:
   Gli endpoint `/api/v3/exam/evaluate` e `/api/v3/fsrs/schedule` invocano `scheduler.step(...)`. La classe `FSRSScheduler` NON possiede il metodo `step`, bensì `review_card(...)`. Entrambi gli endpoint vanno in crash con `AttributeError: 'FSRSScheduler' object has no attribute 'step'`.
   -> Correggi immediatamente la chiamata in `scheduler.review_card(...)` con la corretta firma dei parametri.

2. **Disallineamento Firme e Schemi SDUI**:
   - In `/api/v3/pharma/evaluate`: attualmente `patient_id` è un parametro di query string anziché far parte del body JSON. Crea/usa un modello Pydantic rigido di request body:
     `class PharmaEvaluationRequest(BaseModel): patient_id: str; prescribed_atc_codes: List[str]; ...`
   - In `DrugInteractionRecord`: il backend emette `source_atc`, `target_atc`, `severity`, `mechanism`. Fai sì che emetta anche o supporti `drug_a`, `drug_b`, `level`, `mechanism` (o alias) per allinearsi al frontend React.
   - In `DifferentialCandidate`: il backend emette `disease_name` e `posterior_probability`. Aggiungi o supporta anche `name` e `probability` per evitare che il frontend legga `undefined`.

3. **Riscrittura Test F41-F48 in `tests/`**:
   Riscrivi `test_f41_f44_frontend_views_store.py` e `test_f45_f48_frontend_blocks_canvas.py` affinché importino i modelli ed esecutori reali (`SDUISerializer`, `sdui_models`, ecc.) eliminando asserzioni tautologiche su stringhe fittizie.

**Action**: Implementa queste correzioni nel backend sidecar e nei test e verifica che la test suite passi al 100%.
