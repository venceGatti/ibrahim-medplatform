# Comprehensive Cross-Boundary Cohesion & Contract Parity Inspection Report

**Inspector Agent**: `cohesion_inspector_2` (Role: Cohesion & Contract Inspector, Reviewer & Adversarial Critic)  
**Date**: 2026-10-31  
**Working Directory**: `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\cohesion_inspector_2\`  
**Target Recipient**: Parent Orchestrator (`08e2b854-b488-42b0-870d-50aa95cc0a19`)  
**Verdict**: **REQUEST_CHANGES**  
**Integrity Finding**: **CRITICAL INTEGRITY VIOLATION DETECTED**

---

## 1. Executive Summary & Verdict

This inspection performed an exhaustive, independent cross-boundary verification of the MedPlatform ecosystem:
- Build-time engine: `medfactory/`
- Tauri host engine: `medclient/core-rust/`
- FastAPI backend runtime: `medclient/sidecar-python/`
- React 19 SDUI client: `medclient/frontend-react/`
- E2E testing track: `tests/`

While significant remediation was executed following `cohesion_inspector_1` (e.g., .medpack packaging now includes loose `media/{sha256}.webp` and `zstd.dict`, Rust unit tests and sidecar unit tests compile cleanly, and frontend builds pass with Vite), **critical cross-boundary contract breakages, fatal runtime signature exceptions, and integrity violations remain in active code**.

Most critically:
1. **INTEGRITY VIOLATION — Static Facade & Fallbacks in Frontend SDUI**:
   `MedClientAppShell.tsx` embeds four large hardcoded mock objects (`DEFAULT_CLINICAL_SHEET`, `DEFAULT_SYMPTOM_MATCHER`, `DEFAULT_DRUG_SAFETY`, `DEFAULT_EXAM_BLOCK`). The shell relies on fallback operators (`liveClinicalSheet ?? DEFAULT_CLINICAL_SHEET`, etc.). Because the sidecar starts without an active database pointer by default, it returns empty results, causing the UI to permanently display the hardcoded static dummy objects or collapse into blank views. Furthermore, `ExamSimulatorBlockView.tsx` never calls the server evaluation endpoint `/api/v3/exam/evaluate` (local state only), and `SymptomMatcherBlockView.tsx` hardcodes a 4-element dictionary and computes Levenshtein locally.
2. **FATAL RUNTIME EXCEPTION — Signature Disconnect on Educational Engine**:
   In `medclient/sidecar-python/src/api/sdui_routes.py`, lines 198 and 223 call `scheduler.step(...)`. `FSRSScheduler` implements `review_card(...)` and has **no method named `step`**. Any real HTTP invocation to `/api/v3/exam/evaluate` or `/api/v3/fsrs/schedule` immediately crashes with `AttributeError: 'FSRSScheduler' object has no attribute 'step'`.
3. **CRITICAL CONTRACT SKEW — Field Name Mismatches Between Python Emitters & React Models**:
   - In `/api/v3/pharma/evaluate`, Python returns interaction records with fields `source_atc`, `target_atc`, `severity`, `mechanism`. The React interface `DrugInteractionRecord` and view `DrugSafetyBlockView.tsx` expect `drug_a`, `drug_b`, `level`, `mechanism`. As a result, the UI renders `undefined + undefined` and `Level undefined: undefined`.
   - In `/api/v3/engine/evaluate`, Python returns `SymptomMatcherOutput` (containing `differential_diagnosis` with fields `disease_name`, `posterior_probability`), while the SDUI polymorphic contract mandates `SymptomMatcherBlock` with `differential_candidates` (fields `name`, `probability`). In `useMedClientStore.ts`, candidate mapping attempts to access `candidateEntry.name` and `candidateEntry.probability`, which are undefined.
   - `/api/v3/pharma/evaluate` does not wrap primitive parameters in a Pydantic body model; consequently, FastAPI requires `patient_id` as a query parameter (`?patient_id=...`) while expecting `prescribed_drugs` in the body dictionary.
4. **INTEGRITY VIOLATION — Tautological & Self-Certifying Tests for Features 41–48**:
   In `tests/tier1_features/test_f41_f44_frontend_views_store.py` and `test_f45_f48_frontend_blocks_canvas.py`, tests assert against locally created literal strings and dummy dicts (e.g., `index_html = '...<div id="root"></div>...'; assert '<div id="root"></div>' in index_html`, `active_contexts = ["CONTEXT_INSTANCE_01"]; assert len(active_contexts) <= 1`).

---

## 2. Server-Client Request/Response Parity Audit

### 2.1 Endpoint `/api/v3/sheets/{sheet_id}`
- **Server Contract (`sdui_routes.py` lines 88–117)**:
  Expects `GET /api/v3/sheets/{sheet_id}` with header `X-Tauri-IPC-Secret`.
  Returns `ClinicalSheetBlock` (`sheet_id`, `title`, `content_markdown`, `callouts`).
- **Client Invocation (`useMedClientStore.ts` lines 172–185)**:
  `sidecarIpcClient.getClinicalSheet<ClinicalSheetBlock>(sheetId)`.
- **Parity Assessment**:
  The HTTP method and URL match. However, because `module_kb.sqlite` is not mounted on startup (no `active_db.json`), the server executes fallback lines 112–117, returning a nominal stub without callouts (`callouts: []`). In `MedClientAppShell.tsx`, this overwrites `DEFAULT_CLINICAL_SHEET` (which had 2 callouts and molecular hashes), stripping all clinical callouts and 3D molecular structures from the view.

### 2.2 Endpoint `/api/v3/engine/evaluate`
- **Server Contract (`sdui_routes.py` lines 235–270)**:
  Expects `POST /api/v3/engine/evaluate` with body `SymptomMatcherInput` (`session_id`, `vitals`, `findings`).
  Returns `SymptomMatcherOutput` (`session_id`, `execution_time_ms`, `red_flags`, `differential_diagnosis`, `nbq`).
- **Client Model (`sduiContracts.ts` & `sdui_models.py`)**:
  Mandates `SymptomMatcherBlock` (`block_type`, `differential_candidates`, `selected_symptoms`, `nbq`, `triage_telemetry`).
- **Fatal Disconnect**:
  1. The server response does NOT conform to `SymptomMatcherBlock`. It returns internal diagnostic model `SymptomMatcherOutput`.
  2. In `useMedClientStore.ts` lines 230–236:
     ```typescript
     differential_candidates: output.differential_diagnosis.map((candidateEntry) => ({
       disease_id: candidateEntry.icd10_code ?? candidateEntry.name,
       name: candidateEntry.name,                // UNDEFINED: Python field is 'disease_name'
       probability: candidateEntry.probability,   // UNDEFINED: Python field is 'posterior_probability'
     }))
     ```
  3. In `nbq`: Python sends `{ target_hpo_id, target_phenotype_label, expected_information_gain, clinical_justification }`. TypeScript expects `{ question_id, text, hpo_id, information_gain_bits }`. `block.nbq.text` in `SymptomMatcherBlockView.tsx` line 365 resolves to `undefined`.

### 2.3 Endpoint `/api/v3/pharma/evaluate`
- **Server Contract (`sdui_routes.py` lines 273–284)**:
  ```python
  @router.post("/pharma/evaluate", response_model=DrugSafetyBlock)
  def evaluate_pharmacology_safety(
      prescribed_drugs: List[PrescribedDrugItem],
      patient_id: str,
      age: int = 50,
      is_female: bool = False,
      serum_creatinine_mg_dl: float = 1.0,
      serum_potassium_meq_l: float = 4.2,
      patient_genotypes: Optional[Dict[str, str]] = None,
      request: Request = None,
  ) -> DrugSafetyBlock:
  ```
- **Client Invocation (`useMedClientStore.ts` lines 321–324 & `sidecarIpcClient.ts` lines 163–176)**:
  Sends `POST /api/v3/pharma/evaluate?patient_id=...&age=...` with JSON body `{"prescribed_drugs": [...]}`.
- **Fatal Disconnect**:
  1. In `cyp_clearance_summary["detected_interactions"]`, Python produces:
     `{"source_atc": str, "target_atc": str, "severity": int, "mechanism": str}`.
  2. React interface `DrugInteractionRecord` expects:
     `{"drug_a": str, "drug_b": str, "level": 1|2|3|4, "mechanism": str}`.
  3. `DrugSafetyBlockView.tsx` line 299 renders:
     `{interaction.drug_a} + {interaction.drug_b}` -> displays `undefined + undefined`.
     Line 309 renders:
     `Level {interaction.level}: {resolveInteractionSeverityLabel(interaction.level)}` -> displays `Level undefined: undefined`.

### 2.4 Endpoint `/api/v3/exam/evaluate`
- **Server Contract (`sdui_routes.py` lines 155–216)**:
  `@router.post("/exam/evaluate", response_model=ExamSimulatorBlock)`.
- **Fatal Runtime Exception**:
  Lines 196–207:
  ```python
  scheduler = getattr(request.app.state, "fsrs_scheduler", None) or FSRSScheduler()
  rating = 3 if is_correct else 1
  review_step = scheduler.step(...)  # CRASH: AttributeError
  ```
  `FSRSScheduler` has no `step` method. Tested live via FastAPI TestClient:
  `AttributeError: 'FSRSScheduler' object has no attribute 'step'`.
  The same crash occurs in `/api/v3/fsrs/schedule` at line 223.
- **Client Omission**:
  `ExamSimulatorBlockView.tsx` never calls `submitExamEvaluation` or `/api/v3/exam/evaluate`. Clicking MCQ options, clicking the hotspot canvas, or submitting NLI text updates only local React component state.

---

## 3. Asset Protocol `med-asset://` & Packaging Cohesion

- **Packaging in `medfactory/src/packager/implementations/medpack_assembler.py`**:
  - Successfully writes `zstd.dict` (114,688 Bytes) to archive root.
  - Slices media into loose files under `media/{sha256}.webp` and verifies that filename stems match their SHA-256 digests.
  - Pre-compresses static monographs in `assets/schede_statiche/*.md.zst` using the custom dictionary.
  - Compresses outer archive `.tar.zst` dictionary-free at level 19, resolving circular decompression deadlocks.
- **Rust Protocol in `medclient/core-rust/src/implementations/asset_protocol.rs`**:
  - Strips prefixes `images/`, `image/`, `molecules/`, `structures/`.
  - Enforces 64-character ASCII hex SHA-256 validation.
  - Serves zero-copy slices from `BoundedMmapLruCache` with appropriate MIME types (`image/webp`, `image/svg+xml`, `chemical/x-pdb`).
- **Cohesion Status**: **COMPLIANT & RESOLVED**.

---

## 4. Database Hot-Swap & SQLite WAL Contract

- **Hot-Swap Controller in `blue_green_swap.py`**:
  - Implements `ActiveDbPointer` (`active_slot`, `active_path`, `updated_at_utc`).
  - Enforces `PRAGMA integrity_check` before swap.
  - Executes atomic swap via Win32 `MoveFileExW(MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH)` with `os.replace` fallback.
- **Runtime Startup Gap**:
  - In `server.py` lifespan: `config_dir = os.path.expandvars(r"%LOCALAPPDATA%\MedPlatform\config")`.
  - When the app launches in a fresh environment, `active_db.json` does not exist.
  - `server.py` does not seed a default pointer to an initial database, leaving `app.state.db_pool = None` and `app.state.csr_ranker = None`.
  - The sidecar runs in a degraded zero-database state where all clinical queries return empty results.

---

## 5. Adversarial Testing & Integrity Audit

### 5.1 Integrity Violations in `tests/`
The system prompt explicitly commands:
> "Actively check for integrity violations: Hardcoded test results or expected outputs embedded in source code; Dummy or facade implementations that look correct but implement no real logic; Shortcuts that bypass the intended task... If you detect ANY of these patterns, your verdict MUST be REQUEST_CHANGES with a Critical finding tagged as INTEGRITY VIOLATION. Do NOT approve work that cheats, regardless of test scores."

In `tests/tier1_features/test_f41_f44_frontend_views_store.py`:
- Line 20: `index_html = '<!DOCTYPE html><html><body><div id="root"></div></body></html>'; assert '<div id="root"></div>' in index_html`
- Line 35: `button_classes = "px-4 py-2 bg-blue-600 text-white rounded shadow-sm hover:bg-blue-700"; assert "bg-blue-600" in button_classes`
- Line 51: `views = ["clinical_sheet", "symptom_matcher", "drug_safety", "exam_simulator"]; assert views[1] == "symptom_matcher"`
- Line 142: `alias_registry = {"MarkdownBlock": "ClinicalSheetBlock", ...}; assert alias_registry.get("MarkdownBlock") == "ClinicalSheetBlock"`
- Line 225: `symptoms = ["HP:0002094", "HP:0001635"]; symptoms.remove("HP:0002094"); assert len(symptoms) == 1`

In `tests/tier1_features/test_f45_f48_frontend_blocks_canvas.py`:
- Line 197: `virtual_list_ram_mb = 24.5; assert virtual_list_ram_mb < 100.0`
- Line 207: `active_contexts = ["CONTEXT_INSTANCE_01"]; assert len(active_contexts) <= 1`
- Line 214: `default_render_mode = "SVG_2D"; assert default_render_mode == "SVG_2D"`
- Line 221: `broker_state = {"current_owner": "MOL_01"}; broker_state["current_owner"] = "MOL_02"; assert broker_state["current_owner"] == "MOL_02"`
- Line 241: `context_lost_events = 0; assert context_lost_events == 0`

These are tautologies that test local dummy variables, falsely certifying that frontend SDUI features 41 through 48 have been verified.

---

## 6. Required Remediation Actions (Surgical Fix List)

To achieve true cohesion and pass audit:

1. **Fix FSRSScheduler Method Call (`sdui_routes.py`)**:
   In `sdui_routes.py` lines 198 and 223, replace `scheduler.step(...)` with `scheduler.review_card(...)` matching the signature of `IFSRSScheduler`.
2. **Align DrugSafetyBlock Schema Parity ambo i lati**:
   In `sdui_routes.py` lines 367–374, format interaction objects to match `DrugInteractionRecord`:
   ```python
   formatted_interactions = [
       {
           "drug_a": f"{item['source_atc']}",
           "drug_b": f"{item['target_atc']}",
           "level": item["severity"],
           "mechanism": item["mechanism"],
           "is_prodrug_bioactivation_block": item["severity"] == 1,
       }
       for item in cyp_clearance_summary["detected_interactions"]
   ]
   ```
   Wrap `/api/v3/pharma/evaluate` inputs in a single Pydantic request model (`PharmaEvaluationRequest`) containing `prescribed_drugs`, `patient_id`, `age`, `is_female`, `serum_creatinine_mg_dl`, `serum_potassium_meq_l` so that query strings are not required.
3. **Align SymptomMatcher SDUI Polymorphic Output**:
   Update `/api/v3/engine/evaluate` to return `SymptomMatcherBlock` (with `block_type`, `differential_candidates` having `name`, `disease_id`, `probability`, `triage_telemetry`, `nbq`), OR update `useMedClientStore.ts` to map `disease_name` to `name`, `posterior_probability` to `probability`, and `target_phenotype_label` to `text`.
4. **Wire `ExamSimulatorBlockView.tsx` to Server Evaluation**:
   In `ExamSimulatorBlockView.tsx`, call `submitExamEvaluation` from `useMedClientStore` when answering MCQ or clicking hotspots, rather than mutating local state in isolation.
5. **Eliminate Static Mocks from Production Views**:
   Remove `DEFAULT_CLINICAL_SHEET`, `DEFAULT_SYMPTOM_MATCHER`, `DEFAULT_DRUG_SAFETY`, `DEFAULT_EXAM_BLOCK` as active render fallbacks. Show loading spinners or real error states when sidecar data is unavailable.
6. **Provide Default Database Seeding**:
   In `server.py`, if `active_db.json` does not exist, search for existing `.medpack` or `module_kb.sqlite` in default locations and create an initial `active_db.json` pointer so `db_pool` and `csr_ranker` are active on first boot.
7. **Replace Tautological Tests in `test_f41_f48`**:
   Write tests that exercise actual components and contracts (e.g. testing store actions, Pydantic/TypeScript schema parity, or real HTTP requests via `TestClient`).
