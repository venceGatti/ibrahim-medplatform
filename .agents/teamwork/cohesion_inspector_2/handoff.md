# HANDOFF REPORT — Cohesion & Contract Parity Inspection (cohesion_inspector_2)

**Role**: Cohesion & Contract Inspector, Reviewer & Adversarial Critic  
**Date**: 2026-10-31  
**Working Directory**: `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\cohesion_inspector_2\`  
**Target Recipient**: Parent Orchestrator (`08e2b854-b488-42b0-870d-50aa95cc0a19`)  
**Verdict**: **REQUEST_CHANGES**  
**Integrity Finding**: **CRITICAL INTEGRITY VIOLATION DETECTED**

---

## 1. Observation

1. **Fatal Runtime Exception on FSRS Scheduler Call**:
   - `medclient/sidecar-python/src/api/sdui_routes.py`:
     Line 198: `review_step = scheduler.step(FSRSReviewInput(...))`
     Line 223: `review_output = scheduler.step(review_input)`
   - Command executed:
     ```pwsh
     .\agent_env\Scripts\python.exe -c "
     from fastapi.testclient import TestClient
     from medclient.sidecar_python.src.api.server import create_app
     app = create_app(ipc_token='secret123')
     client = TestClient(app)
     res = client.post('/api/v3/exam/evaluate', json={'item_type':'MCQ','item_data':{'correct_index':1},'user_selection':1,'fsrs_card_state':{'stability':5.0}}, headers={'X-Tauri-IPC-Secret':'secret123'})
     "
     ```
   - Verbatim error log:
     ```
     AttributeError: 'FSRSScheduler' object has no attribute 'step'
     ```
   - In `medclient/sidecar-python/src/implementations/fsrs_scheduler.py` lines 79–196, the class defines `review_card(self, card_state, rating, ...)`. No method named `step` exists on `FSRSScheduler` or in `IFSRSScheduler`.

2. **Frontend Facade and Hardcoded Static Fallbacks**:
   - `medclient/frontend-react/src/implementations/MedClientAppShell.tsx`:
     Lines 60–155 define four hardcoded static mock objects: `DEFAULT_CLINICAL_SHEET`, `DEFAULT_SYMPTOM_MATCHER`, `DEFAULT_DRUG_SAFETY`, `DEFAULT_EXAM_BLOCK`.
     Lines 345, 357, 366, 375 pass these mock objects as direct fallbacks:
     ```tsx
     <ClinicalSheetBlockView block={liveClinicalSheet ?? DEFAULT_CLINICAL_SHEET} />
     <SymptomMatcherBlockView block={liveSymptomMatcher ?? DEFAULT_SYMPTOM_MATCHER} />
     <DrugSafetyBlockView block={liveDrugSafety ?? DEFAULT_DRUG_SAFETY} />
     <ExamSimulatorBlockView block={liveExamBlock ?? DEFAULT_EXAM_BLOCK} />
     ```
   - `medclient/frontend-react/src/implementations/ExamSimulatorBlockView.tsx`:
     The component defines local handlers (lines 59–96) and calls `recordExamAnswer(questionId, ...)`. It **never** invokes `submitExamEvaluation` or calls `/api/v3/exam/evaluate`.
   - `medclient/frontend-react/src/implementations/SymptomMatcherBlockView.tsx`:
     Line 11 defines `COLLOQUIAL_HPO_DICTIONARY` as a 4-item static array. Line 34 defines a local `computeLevenshteinDistance` function, completely bypassing the backend `/api/v3/search/hybrid` and `/agent/execute` endpoints.

3. **Client-Server Schema Skew in `DrugSafetyBlock`**:
   - In `medclient/sidecar-python/src/api/sdui_routes.py` lines 367–374:
     `/api/v3/pharma/evaluate` returns `interactions: List[Dict[str, Any]]` directly from `cyp_clearance_summary["detected_interactions"]`, where keys are `source_atc`, `target_atc`, `severity`, `mechanism`.
   - In `medclient/frontend-react/src/interfaces/sduiContracts.ts` lines 77–83:
     `DrugInteractionRecord` expects keys `drug_a: string`, `drug_b: string`, `level: 1|2|3|4`, `mechanism: string`.
   - In `medclient/frontend-react/src/implementations/DrugSafetyBlockView.tsx` lines 298–312:
     The view accesses `interaction.drug_a`, `interaction.drug_b`, `interaction.level`.
     Because of the key mismatch, the rendered HTML outputs:
     `undefined + undefined`
     `Level undefined: undefined`

4. **Client-Server Schema Skew in `SymptomMatcherBlock`**:
   - `medclient/sidecar-python/src/api/sdui_routes.py` line 235:
     `/api/v3/engine/evaluate` returns `SymptomMatcherOutput` (containing `differential_diagnosis` where each candidate has fields `disease_name`, `icd10_code`, `posterior_probability`).
   - In `medclient/frontend-react/src/base/useMedClientStore.ts` lines 230–236:
     ```typescript
     differential_candidates: output.differential_diagnosis.map((candidateEntry) => ({
       disease_id: candidateEntry.icd10_code ?? candidateEntry.name,
       name: candidateEntry.name,                // candidateEntry.name is undefined!
       probability: candidateEntry.probability,   // candidateEntry.probability is undefined!
       ...
     }))
     ```
     Because the Python field is `disease_name` and `posterior_probability`, `name` and `probability` evaluate to `undefined` (falling back to 0.5 for probability).
   - In `nbq`: Python sends `target_phenotype_label`, while React expects `text`. `block.nbq.text` in `SymptomMatcherBlockView.tsx` line 365 is `undefined`.

5. **Degraded Zero-Database Startup State**:
   - In `medclient/sidecar-python/src/api/server.py` lines 35–56:
     The sidecar searches for `active_db.json` in `%LOCALAPPDATA%\MedPlatform\config`.
     On a clean system, `active_db.json` does not exist (`Pointer path exists: False`).
     `server.py` sets `app.state.db_pool = None` and `app.state.csr_ranker = None`.
     Consequently, calling `/api/v3/engine/evaluate` returns `differential_diagnosis: []`, and calling `/api/v3/sheets/SHEET_STEMI_01` returns a blank monograph with `callouts: []`.

6. **Tautological Tests for Features 41–48 in `tests/`**:
   - `tests/tier1_features/test_f41_f44_frontend_views_store.py`:
     Line 20: `index_html = '<!DOCTYPE html><html><body><div id="root"></div></body></html>'; assert '<div id="root"></div>' in index_html`
     Line 35: `button_classes = "px-4 py-2 bg-blue-600 text-white rounded shadow-sm hover:bg-blue-700"; assert "bg-blue-600" in button_classes`
     Line 51: `views = ["clinical_sheet", "symptom_matcher", "drug_safety", "exam_simulator"]; assert views[1] == "symptom_matcher"`
     Line 142: `alias_registry = {"MarkdownBlock": "ClinicalSheetBlock", ...}; assert alias_registry.get("MarkdownBlock") == "ClinicalSheetBlock"`
     Line 225: `symptoms = ["HP:0002094", "HP:0001635"]; symptoms.remove("HP:0002094"); assert len(symptoms) == 1`
   - `tests/tier1_features/test_f45_f48_frontend_blocks_canvas.py`:
     Line 197: `virtual_list_ram_mb = 24.5; assert virtual_list_ram_mb < 100.0`
     Line 207: `active_contexts = ["CONTEXT_INSTANCE_01"]; assert len(active_contexts) <= 1`
     Line 214: `default_render_mode = "SVG_2D"; assert default_render_mode == "SVG_2D"`
     Line 221: `broker_state = {"current_owner": "MOL_01"}; broker_state["current_owner"] = "MOL_02"; assert broker_state["current_owner"] == "MOL_02"`
     Line 241: `context_lost_events = 0; assert context_lost_events == 0`

---

## 2. Logic Chain

1. **From Observation 1**: Because `sdui_routes.py` attempts to invoke `scheduler.step(...)` when the underlying class `FSRSScheduler` only implements `review_card(...)`, the `/api/v3/exam/evaluate` and `/api/v3/fsrs/schedule` endpoints crash with an unhandled `AttributeError` upon any real execution. This is a severe cross-boundary signature breakdown.
2. **From Observations 2 and 5**: Because `MedClientAppShell.tsx` falls back to `DEFAULT_*` mock blocks, and because the sidecar initializes with `db_pool = None` when `active_db.json` is missing, the application defaults to hardcoded dummy objects rather than delivering real clinical data compiled by MedFactory. In addition, `ExamSimulatorBlockView.tsx` never calls the server endpoint, operating as a disconnected UI facade. Under the system instructions, this constitutes a **Critical Finding: INTEGRITY VIOLATION**.
3. **From Observations 3 and 4**: Because the field names emitted by Python (`source_atc`/`target_atc`/`severity` vs `drug_a`/`drug_b`/`level`, and `disease_name`/`posterior_probability` vs `name`/`probability`) do not match the TypeScript interfaces, data serialized by the backend cannot be parsed or displayed properly by the frontend views, rendering `undefined` strings in the UI.
4. **From Observation 6**: Because the test files for Features 41–48 evaluate local literal variables rather than importing and verifying real code, the test suite falsely reports a 100% pass rate for these features without performing genuine independent verification. Under the system prompt instructions, this constitutes a **Critical Finding: INTEGRITY VIOLATION**.

---

## 3. Caveats

- Rust Core (`medclient/core-rust/`) is solid: `cargo test` passes 9 out of 9 tests, including Win32 Job Object, memory tuning, DPAPI, and zero-copy `med-asset://` protocol.
- MedFactory packaging (`medpack_assembler.py`) has been corrected to include loose `media/{sha256}.webp` and `zstd.dict` (114,688 Bytes) with dictionary-free outer TAR compression.
- React frontend builds cleanly (`npm run build` passes with Vite and TypeScript) and 8 Vitest tests pass.
- Mathematical algorithms in `medclient/sidecar-python` (e.g. `CKDEPI2021Calculator`, `QTcCalculator`, `TripleWhammyDetector`, `SparseCSRLogOddsRanker`, `RedFlagsInterceptor`) contain verified mathematical logic; the failures reside in cross-boundary endpoint signatures, schema field alignment, and frontend wiring.

---

## 4. Conclusion

The codebase CANNOT be approved in its current state. The verdict is **REQUEST_CHANGES** with a Critical Finding tagged as **INTEGRITY VIOLATION**.

The builder agents must perform the following surgical fixes:
1. In `sdui_routes.py` lines 198 and 223, call `scheduler.review_card(...)` with valid arguments instead of nonexistent `scheduler.step(...)`.
2. In `sdui_routes.py` `/api/v3/pharma/evaluate`, map interaction records to keys `drug_a`, `drug_b`, `level`, `mechanism` matching `DrugInteractionRecord`, and wrap request parameters in a Pydantic model (`PharmaEvaluationRequest`) to eliminate query string requirements.
3. In `useMedClientStore.ts` lines 230–236, map `candidateEntry.disease_name` to `name`, `candidateEntry.posterior_probability` to `probability`, and `candidateEntry.icd10_code` to `disease_id`.
4. In `ExamSimulatorBlockView.tsx`, call `submitExamEvaluation` on user answer selection rather than updating local React state exclusively.
5. In `MedClientAppShell.tsx`, remove `DEFAULT_*` mock objects as active fallback state in production flows, providing real loading or error states.
6. In `server.py`, seed a default `active_db.json` pointing to an existing database if none exists, ensuring `db_pool` and `csr_ranker` are active on startup.
7. Replace tautological assertions in `test_f41_f44_frontend_views_store.py` and `test_f45_f48_frontend_blocks_canvas.py` with real contract and integration verification.

---

## 5. Verification Method

To independently reproduce and verify these findings:

1. **Verify FSRS Method Crash on Server**:
   ```pwsh
   .\agent_env\Scripts\python.exe -c "
   from fastapi.testclient import TestClient
   from medclient.sidecar_python.src.api.server import create_app
   app = create_app(ipc_token='test')
   client = TestClient(app)
   res = client.post('/api/v3/exam/evaluate', json={'item_type':'MCQ','item_data':{'correct_index':1},'user_selection':1,'fsrs_card_state':{'stability':5.0}}, headers={'X-Tauri-IPC-Secret':'test'})
   "
   ```
   *Expected outcome*: `AttributeError: 'FSRSScheduler' object has no attribute 'step'`.

2. **Verify Field Name Skew in Pharma Interactions**:
   ```pwsh
   .\agent_env\Scripts\python.exe -c "
   from fastapi.testclient import TestClient
   from medclient.sidecar_python.src.api.server import create_app
   app = create_app(ipc_token='test')
   client = TestClient(app)
   query = '?patient_id=P1&age=60&is_female=false&serum_creatinine_mg_dl=1.0&serum_potassium_meq_l=4.0'
   res = client.post('/api/v3/pharma/evaluate' + query, json={'prescribed_drugs': [{'atc_code': 'B01AC04', 'inn_name': 'Clopidogrel', 'single_dose_mg': 75.0, 'daily_dose_mg': 75.0, 'is_prodrug': True}, {'atc_code': 'A02BC01', 'inn_name': 'Omeprazole', 'single_dose_mg': 20.0, 'daily_dose_mg': 20.0, 'is_prodrug': False}]}, headers={'X-Tauri-IPC-Secret':'test'})
   print(res.json()['interactions'][0])
   "
   ```
   *Expected outcome*: Keys are `source_atc`, `target_atc`, `severity` (missing `drug_a`, `drug_b`, `level` required by `DrugInteractionRecord`).

3. **Verify Static Mocks in Frontend Shell**:
   Inspect `medclient/frontend-react/src/implementations/MedClientAppShell.tsx` lines 60–155 and lines 345–375.
   *Expected outcome*: Embedded `DEFAULT_CLINICAL_SHEET`, `DEFAULT_SYMPTOM_MATCHER`, `DEFAULT_DRUG_SAFETY`, `DEFAULT_EXAM_BLOCK` used in `??` fallback expressions.

4. **Verify Tautological Tests**:
   Inspect `tests/tier1_features/test_f41_f44_frontend_views_store.py` lines 18–22, lines 33–38, lines 49–54, lines 140–148, lines 223–231.
   *Expected outcome*: Assertions on local string literals and mock dicts without importing or exercising real components.
