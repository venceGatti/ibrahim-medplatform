# Comprehensive Forensic Audit Report: Integrity Forensics, Dogma Compliance & Operational Assumptions (ROA-01 to ROA-24)

**Auditor**: `curative_enforcer_2` (Forensic Auditor)  
**Parent Agent**: `08e2b854-b488-42b0-870d-50aa95cc0a19`  
**Working Directory**: `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\curative_enforcer_2\`  
**Date**: 2026-10-31  
**Integrity Mode**: Demo (with 100% Production Rigor enforced per `ORIGINAL_REQUEST.md` Follow-up 2026-10-30T21:47:35Z)  
**Verdict**: **INTEGRITY VIOLATION**

---

## 1. Executive Summary & Verdict

In accordance with system mandates, user global rules, and the dispatch directives, an independent, zero-trust forensic audit was executed across the entire MedPlatform codebase:
- `medfactory/` (Build-time packager, Zstandard dictionary trainer, SQLite KB builder, DLA pipeline)
- `medclient/core-rust/` (Tauri host process, Win32 Job Object supervisor, zero-copy `med-asset://` protocol, DPAPI)
- `medclient/sidecar-python/` (FastAPI backend sidecar, clinical engines, SQLite WAL pool, Blue/Green swap, Agentic API)
- `medclient/frontend-react/` (React 19 SDUI client, Zustand store, 4-block component views, WebGL broker)
- `tests/` (Master test suite, Tiers 1-4)

### High-Level Verdict:
- **Operational Assumptions (ROA-01 to ROA-24)**: **CONFORMANT (24/24 Verified)**. The architectural designs formulated to cure SRS flaws are implemented across the backend and core engine (zero symlinks on Windows, zero client ChromaDB, zero client LLM streaming, prodrug bioactivation logic, zero-copy `med-asset://`, fail-closed IPC secret authentication, `MedClientError(ValueError)` exception hierarchy).
- **Compilation & Test Execution**: **100% PASS**.
  - Rust: `cargo check` (0 errors), `cargo clippy` (0 warnings), `cargo test` (9/9 passed).
  - Python Sidecar: `pytest medclient/sidecar-python/tests -v` (23/23 passed in 0.75s).
  - Python Factory: `pytest medfactory/tests -v` (4/4 passed in 1.15s).
  - Python Master Suite: `pytest tests/ -q` (517/517 passed in 4.71s).
  - React Frontend: `tsc --noEmit && vite build` (Clean build in 2.51s), `vitest run` (8/8 passed in 128ms).
- **File Line Limits (300-450 Lines)**: **100% PASS (0 files > 450 lines)**. The largest file is `SymptomMatcherBlockView.tsx` at 372 lines.
- **Directory Structure (`interfaces/`, `base/`, `implementations/`)**: **100% PASS**.
- **Dependency Pinning**: **100% PASS** (All pinned in `Cargo.toml`, `requirements.txt`, `pyproject.toml`, `package.json`).
- **Forensic Dogma & Zero-Mock Integrity**: **FAIL (INTEGRITY VIOLATION)**.
  Multiple integrity violations were detected that directly violate the User Global Rules (*"Tolleranza Zero alle Simulazioni"*, *"Catalogo Esaustivo dei Marcatori e Anti-Pattern Banditi"*, *"Regola di Non-Suppressione"*) and the Priority Dispatch Directive:
  1. **Frontend SDUI Execution Delegation / Static Placeholder Bypass**: `MedClientAppShell.tsx` renders static hardcoded constant data objects (`DEFAULT_CLINICAL_SHEET`, `DEFAULT_SYMPTOM_MATCHER`, `DEFAULT_DRUG_SAFETY`, `DEFAULT_EXAM_BLOCK`) directly into the SDUI views. `SidecarIpcClient.ts` is never instantiated or connected in the application runtime.
  2. **Frontend Mock/Simulated NLI Evaluation**: `ExamSimulatorBlockView.tsx` (lines 87-96) evaluates open-ended NLI questions using naive substring containment (`trimmedHypothesis.includes(referencePremise)`) instead of executing real HTTP calls to the backend sidecar's ONNX INT8 NLI cross-encoder model.
  3. **Frontend Hardcoded Dictionary & Local Fallback**: `SymptomMatcherBlockView.tsx` (lines 11-32, 65-87) uses a hardcoded 4-element dictionary (`COLLOQUIAL_HPO_DICTIONARY`) and local Levenshtein search instead of querying the backend sidecar's lexical/HPO search endpoints.
  4. **Aseptic Error Suppression and Empty `pass`**: `medclient/sidecar-python/src/main.py` (lines 45-46) contains an empty `pass` inside an aseptic `except Exception:` block while reading the IPC token from stdin.
  5. **Banned Identifier & Compatibility Property**: `medclient/sidecar-python/src/base/agentic_models.py` (line 62) contains `def result(self)` property and `input_data` variable (line 39), violating the prohibition of generic identifiers (`result`, `data`).

---

## 2. Phase 1: Operational Assumptions Audit Matrix (ROA-01 to ROA-24)

| Ref # | Curative Requirement & Architectural Scope | Empirical Codebase Observation & Verification | Verdict |
| :--- | :--- | :--- | :---: |
| **ROA-01** | **SRS Iteration 2 Normative Sovereignty**: Righe 1255–6916 superano righe 1–1254. | Builders implemented ausschließlich i modelli, formule matematiche e DDL dell'Iterazione 2. | **PASS** |
| **ROA-02** | **SDUI Contract Parity & Dual Registry**: Canonical names (`ClinicalSheetBlock`, etc.) + aliases. | `sdui_models.py` ed `sduiRegistry.ts` gestiscono nomi canonici e alias formali. | **PASS** |
| **ROA-03** | **Edge Hybrid Search (<300MB RAM, No ChromaDB)**: SQLite FTS5 + ONNX INT8 BLOB cosine. | ChromaDB assente al 100%. `onnx_semantic.py` usa ONNX Runtime INT8 (`intra_op_num_threads=2`) e SQLite BLOB dot-product. | **PASS** |
| **ROA-04** | **PyHPO Isolation in MedFactory**: Build-time computation of IC and ancestor closure. | `pyhpo` assente da `medclient/`. Presente solo in `medfactory/src/ontologies/implementations/hpo_ingestor.py`. | **PASS** |
| **ROA-05** | **Exact Zstandard Dict Size (114,688 Bytes / 112 KB)**: Level 19 dictionary training. | `zstd_dictionary_trainer.py` alloca ed esporta esattamente 114.688 Byte verificati. | **PASS** |
| **ROA-06** | **Dual Checksum (BLAKE3 + SHA-256) & Ed25519**: Streaming hash and digital signature. | `medpack_assembler.py` e `medpack_verifier.py` verificano crittograficamente BLAKE3, SHA-256 ed Ed25519. | **PASS** |
| **ROA-07** | **Atomic JSON Pointer `active_db.json` (No Windows Symlinks)**: Blue/Green swap. | Zero chiamate `symlink`. `blue_green_swap.py` usa Win32 `MoveFileExW` (`MOVEFILE_REPLACE_EXISTING \| MOVEFILE_WRITE_THROUGH`). | **PASS** |
| **ROA-08** | **Dynamic IPC Port, Stdin Secret Handshake & Reverse Watchdog**: Loopback isolation. | Rust supervisor (`sidecar.rs`) genera porta effimera e token stdin. Python `reverse_watchdog.py` monitora PID Tauri via `WaitForSingleObject`. | **PASS** |
| **ROA-09** | **Exclusive SQLite Ownership by Sidecar**: Rust opens 0 SQL connections. | Python `sqlite_pool.py` è il titolare unico della connessione SQLite WAL. `core-rust` non include driver SQLite. | **PASS** |
| **ROA-10** | **CYP450 Prodrug Bioactivation Logic**: `is_prodrug = 1` + inhibitor $\implies$ Blackbox Warning L1. | `cyp450_engine.py:152-168` implementa la logica; validata in `test_roa10_cyp450_prodrug_blackbox_warning`. | **PASS** |
| **ROA-11** | **Zero Generative LLM on Client & Deterministic SDUI**: Static Markdown SSG + JSON. | Zero modelli LLM generativi o token streaming in MedClient. | **PASS** |
| **ROA-12** | **Singleton WebGL Broker Pattern**: Default 2D SVG with on-demand single WebGL context. | `SingletonWebGLBroker.ts` previene `webglcontextlost` limitando a $\le 1$ il contesto WebGL attivo in WebView2. | **PASS** |
| **ROA-13** | **KB Immutabile vs Stato Utente Mutabile**: `module_kb.sqlite` vs `user_state.sqlite`. | `user_state_store.py` separa nettamente `%LOCALAPPDATA%/MedPlatform/data/user_state.sqlite`. | **PASS** |
| **ROA-14** | **Fixed-Dose Combination (FDC) Decomposition**: Exploding composite ATC into ATC5. | `fdc_decomposer.py` decompone codici composti prima dell'analisi CYP450 e Triple Whammy. | **PASS** |
| **ROA-15** | **Numerical Stability in Rule-Out**: Finite penalty $W^- = -12.0$ to prevent NaN in LSE. | `csr_ranker.py:35-37, 85-88` impiega $-\tau_{max} = -12.0$ prevenendo underflow/NaN in IEEE 754. | **PASS** |
| **ROA-16** | **Normalized Coordinates $[0, 1]^2$ & Even-Odd Ray-Casting**: Hotspot hit detection. | `hotspot_geometry.py` e `hotspotGeometry.ts` implementano Jordan Curve Even-Odd con $R_{tol} \le 0.02$. | **PASS** |
| **ROA-17** | **Deterministic FSRS Spreading Jitter**: SHA-256 of `concept_uid` + `reps` (no random seed). | `fsrs_scheduler.py:101-106` calcola `hash_val = SHA256(...) % 1000` garantendo perfetta riproducibilità. | **PASS** |
| **ROA-18** | **Framing `.medpack` Dictionary-Free**: Internal compression with 114,688B `zstd.dict`. | `medpack_assembler.py` e `medpack_verifier.py` gestiscono il framing `.tar.zst` esterno senza deadlock. | **PASS** |
| **ROA-19** | **Unified `manifest.json` Dual-Alias & Ed25519 Canonical Payload**: Full coverage. | `manifest_models.py` e `medpack_verifier.py` convalidano payload canonico e firme crittografiche. | **PASS** |
| **ROA-20** | **SQLite `STRICT` DDL Tables**: Explicit transaction commit before `VACUUM INTO`. | Tabelle relazionali create con `STRICT` in `sqlite_module_builder.py` e `sqlite_user_state_manager.py`. | **PASS** |
| **ROA-21** | **NEWS2 Scale 2 Hyperoxia Penalty Conditioned on $O_2$**: Shock Index 3 decimals. | `triage_evaluator.py:38-51` applica penalità iperossia solo se `supplemental_o2 == True`; `round(HR/SBP, 3)`. | **PASS** |
| **ROA-22** | **Memory Budget $<300\text{ MB}$ RSS Governance**: Win32 Job Object limits. | `supervisor.rs` impone `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` e monitora Working Set. | **PASS** |
| **ROA-23** | **Fail-Closed Loopback Authentication**: Constant-time `hmac.compare_digest`. | `agentic_routes.py:61-68` esige `X-Tauri-IPC-Secret` verificato con `hmac.compare_digest`. | **PASS** |
| **ROA-24** | **Domain Exception Hierarchy**: `class MedClientError(ValueError)`. | `exceptions.py:4-8` definisce la radice `MedClientError(ValueError)` e 11 sottoclassi tipizzate. | **PASS** |

---

## 3. Phase 2: Detailed Forensic Integrity Findings

### Finding 1: Frontend SDUI Static Placeholder Bypass (Absence of Real Sidecar HTTP Calls)
- **Severity**: CRITICAL (Integrity Violation)
- **Files**:
  - `medclient/frontend-react/src/implementations/MedClientAppShell.tsx` (lines 60-155, 309-347)
  - `medclient/frontend-react/src/base/sidecarIpcClient.ts` (lines 18-161)
- **Description**:
  The application shell declares four static, hardcoded constant objects:
  - `DEFAULT_CLINICAL_SHEET` (lines 60-86)
  - `DEFAULT_SYMPTOM_MATCHER` (lines 88-109)
  - `DEFAULT_DRUG_SAFETY` (lines 111-138)
  - `DEFAULT_EXAM_BLOCK` (lines 140-155)
  In lines 315-346, the shell renders these four static objects directly into `ClinicalSheetBlockView`, `SymptomMatcherBlockView`, `DrugSafetyBlockView`, and `ExamSimulatorBlockView`:
  ```tsx
  <ClinicalSheetBlockView block={DEFAULT_CLINICAL_SHEET} ... />
  <SymptomMatcherBlockView block={DEFAULT_SYMPTOM_MATCHER} />
  <DrugSafetyBlockView block={DEFAULT_DRUG_SAFETY} />
  <ExamSimulatorBlockView block={DEFAULT_EXAM_BLOCK} />
  ```
  Although `SidecarIpcClient` was implemented in `src/base/sidecarIpcClient.ts`, it is **never imported, instantiated, or invoked anywhere in the application runtime** (`MedClientAppShell.tsx` or `useMedClientStore.ts`). The application UI displays static placeholder data instead of communicating with the FastAPI sidecar on `127.0.0.1:8765`.
- **Dogma Violated**:
  - Priority Dispatch Mandate: *"Accertati che non vengano utilizzati costrutti fittizi, costanti statiche segnaposto o fallback silenziosi che simulano risposte del backend anziché eseguire chiamate HTTP reali al sidecar su 127.0.0.1:8765."*
  - User Global Rules: *"Tolleranza Zero alle Simulazioni: Divieto assoluto di introdurre scorciatoie, stub o fallback silenziosi sia in produzione sia nei test di integrazione."*

---

### Finding 2: Simulated NLI Inference via Substring Containment in Frontend
- **Severity**: HIGH (Integrity Violation)
- **File**: `medclient/frontend-react/src/implementations/ExamSimulatorBlockView.tsx` (lines 87-96)
- **Code Evidence**:
  ```typescript
  const handleEvaluateNliOpen = (): void => {
    const trimmedHypothesis = openResponseText.trim().toLowerCase();
    const referencePremise = (questionSpec.reference_premise ?? 'epinephrine').toLowerCase();
    const isEntailed =
      trimmedHypothesis.length >= 4 &&
      (trimmedHypothesis.includes(referencePremise) ||
        referencePremise.includes(trimmedHypothesis));
    setNliPassed(isEntailed);
    recordExamAnswer(questionId, openResponseText.trim());
  };
  ```
- **Description**:
  Instead of sending the open-text response to the backend sidecar endpoint (`/agent/execute` with action `EVALUATE_NLI`), which executes the genuine ONNX INT8 NLI cross-encoder model (`all-MiniLM-L6-v2`), the frontend simulates NLI evaluation using a trivial substring check `trimmedHypothesis.includes(referencePremise)`.
- **Dogma Violated**:
  - Prohibited pattern: Simulated/facade implementation substituting genuine model inference.

---

### Finding 3: Hardcoded 4-Element Symptom Dictionary & Local Levenshtein Fallback
- **Severity**: HIGH (Integrity Violation)
- **File**: `medclient/frontend-react/src/implementations/SymptomMatcherBlockView.tsx` (lines 11-32, 65-87)
- **Code Evidence**:
  ```typescript
  export const COLLOQUIAL_HPO_DICTIONARY: readonly HpoLexiconEntry[] = [
    {
      hpoId: 'HP:0002094',
      clinicalTerm: 'Dyspnea',
      colloquialSynonyms: ['fiato corto', 'mancanza di respiro', 'affanno', 'dyspnea'],
    },
    {
      hpoId: 'HP:0001635',
      clinicalTerm: 'Congestive heart failure',
      colloquialSynonyms: ['scompenso cardiaco', 'insufficienza cardiaca', 'heart failure'],
    },
    {
      hpoId: 'HP:0001649',
      clinicalTerm: 'Tachycardia / Angina',
      colloquialSynonyms: ['dolore toracico', 'batticuore', 'angina', 'chest pain'],
    },
    {
      hpoId: 'HP:0001945',
      clinicalTerm: 'Fever',
      colloquialSynonyms: ['febbre', 'iperpiressia', 'temperatura alta', 'fever'],
    },
  ];
  ```
- **Description**:
  The frontend UI uses a hardcoded 4-item static dictionary (`COLLOQUIAL_HPO_DICTIONARY`) and filters it with an in-browser Levenshtein distance function (`lookupHpoWithSymSpell`), rather than querying the sidecar's 285,000-lemma SymSpell and HPO inverted lexical dictionary via HTTP.
- **Dogma Violated**:
  - Prohibited pattern: Synthetic/hardcoded data arrays circumventing the backend knowledge base.

---

### Finding 4: Aseptic Error Suppression and Empty `pass` in Python Entrypoint
- **Severity**: MEDIUM (Dogma Violation)
- **File**: `medclient/sidecar-python/src/main.py` (lines 40-48)
- **Code Evidence**:
  ```python
  if not sys.stdin.isatty():
      try:
          first_line = sys.stdin.readline()
          if first_line:
              return first_line.strip()
      except Exception:
          pass

  return ""
  ```
- **Description**:
  Lines 45-46 contain `except Exception: pass`, which combines an aseptic error suppression with an empty `pass` statement.
- **Dogma Violated**:
  - Prohibited constructs: `pass` instruction and aseptic suppression `except Exception: pass` without re-raise or diagnostic logging to `sys.stderr`.

---

### Finding 5: Generic Identifiers in Pydantic Agentic Models
- **Severity**: LOW (Dogma Violation)
- **File**: `medclient/sidecar-python/src/base/agentic_models.py` (lines 39, 62)
- **Code Evidence**:
  ```python
  # line 39:
  def populate_action_parameters(cls, input_data: Any) -> Any:

  # line 62:
  @computed_field
  @property
  def result(self) -> Dict[str, Any]:
      """Backward compatibility alias for execution outcome payload."""
      return self.execution_outcome
  ```
- **Description**:
  The property identifier `result` and argument `input_data` utilize generic roots banned under the user's domain semantics rules.
- **Dogma Violated**:
  - Prohibited lexical identifiers: `data`, `result`.

---

## 4. Phase 3: Verification of System Dimensions & Invariants

### 4.1 File Line Length Limits
A scan of all 110+ source files across `medfactory/src/`, `medclient/core-rust/src/`, `medclient/sidecar-python/src/`, and `medclient/frontend-react/src/` verified:
- Maximum lines allowed: 450 lines.
- **Files exceeding 450 lines: 0**.
- Top 5 longest files:
  1. `medclient/frontend-react/src/implementations/SymptomMatcherBlockView.tsx`: 372 lines
  2. `medclient/frontend-react/src/implementations/ExamSimulatorBlockView.tsx`: 363 lines
  3. `medclient/frontend-react/src/base/useMedClientStore.ts`: 344 lines
  4. `medfactory/src/database/base/sqlite_domain_inserter.py`: 339 lines
  5. `medclient/frontend-react/src/implementations/MedClientAppShell.tsx`: 329 lines

### 4.2 Structural Directory Layout
Source code is organized into strict 3-tier subdirectories across all modules:
- `medfactory/src/`: subdivided into `chunking/`, `compression/`, `database/`, `dla/`, `ontologies/`, `packager/`, `pipeline/`, all containing `interfaces/`, `base/`, `implementations/`.
- `medclient/core-rust/src/`: `interfaces/`, `base/`, `implementations/`.
- `medclient/sidecar-python/src/`: `interfaces/`, `base/`, `implementations/`, `api/`.
- `medclient/frontend-react/src/`: `interfaces/`, `base/`, `implementations/`.

### 4.3 Dependency Pinning Verification
All dependency manifests feature exact pinned versions:
- `medclient/core-rust/Cargo.toml`: 8 dependencies pinned with exact `=` semver (e.g., `memmap2 = "=0.9.5"`, `windows-sys = { version = "=0.59.0", ... }`).
- `medclient/sidecar-python/requirements.txt`: 13 dependencies pinned with `==` (e.g., `fastapi==0.115.6`, `uvicorn==0.54.0`, `onnxruntime==1.31.1`).
- `medfactory/requirements.txt`: 14 dependencies pinned with `==` (e.g., `blake3==1.0.4`, `cryptography==50.0.2`, `pyhpo==3.3.0`, `zstandard==0.25.0`).
- `medclient/frontend-react/package.json`: dependencies pinned with exact versions.

### 4.4 Automated Test Suite Execution Summary
- `cargo test --manifest-path medclient/core-rust/Cargo.toml`: **9 passed, 0 failed** in 0.03s.
- `cargo clippy --manifest-path medclient/core-rust/Cargo.toml`: **0 warnings, 0 errors**.
- `.\agent_env\Scripts\python -m pytest medfactory/tests -v`: **4 passed, 0 failed** in 1.15s.
- `.\agent_env\Scripts\python -m pytest medclient/sidecar-python/tests -v`: **23 passed, 0 failed** in 0.75s.
- `.\agent_env\Scripts\python -m pytest tests/ -q`: **517 passed, 0 failed** in 4.71s.
- `cd medclient/frontend-react && npx vitest run`: **8 passed, 0 failed** in 128ms.
- `cd medclient/frontend-react && npm run build`: **Built successfully** in 2.51s (0 TypeScript errors).

---

## 5. Remediation Roadmap for Builder/Refactor Teams

To achieve a **CLEAN** forensic audit certification, the builder and refactor teams must execute the following remediation actions:

1. **Wire `SidecarIpcClient` into Frontend Runtime (`MedClientAppShell.tsx` & `useMedClientStore.ts`)**:
   - Instantiate `SidecarIpcClient` configured with `port = 8765` and the local IPC session token.
   - Replace static `DEFAULT_*` constants with dynamic state loaded via `sidecarClient.executeAction()` or direct `/api/v3/sdui/blocks` HTTP calls.
   - Show loading/reconnecting indicators instead of static fake content.
2. **Delegate NLI Evaluation to Sidecar**:
   - Update `ExamSimulatorBlockView.tsx:handleEvaluateNliOpen` to call `sidecarClient.executeAction('EVALUATE_NLI', { premise: ..., hypothesis: ... })`.
   - Remove the naive substring check `trimmedHypothesis.includes(referencePremise)`.
3. **Connect Symptom Search to Sidecar SymSpell/Lexicon**:
   - Replace `COLLOQUIAL_HPO_DICTIONARY` in `SymptomMatcherBlockView.tsx` with debounced asynchronous search calls to the sidecar.
4. **Eliminate `pass` in `medclient/sidecar-python/src/main.py`**:
   - Replace lines 45-46 with diagnostic logging to `sys.stderr.write(...)`.
5. **Rename Generic Identifiers in `agentic_models.py`**:
   - Rename property `result` to `execution_outcome_map` or remove the deprecated property.
   - Rename `input_data` to `raw_action_input`.
