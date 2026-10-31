# 5-Component Handoff Report: Forensic Integrity Audit & Curative Enforcement

**Agent**: `curative_enforcer_2` (Forensic Auditor)  
**Parent Agent**: `08e2b854-b488-42b0-870d-50aa95cc0a19`  
**Date**: 2026-10-31  
**Handoff Type**: Hard (Audit Task Complete)  
**Verdict**: **INTEGRITY VIOLATION**

---

## 1. Observation

Direct empirical observations made across the codebase:

1. **Curative Architectural Solutions (ROA-01 to ROA-24)**:
   - **ROA-07 (No Symlinks on Windows)**: `grep_search` across `medclient/` and `medfactory/` returned 0 matches for `symlink`. `medclient/sidecar-python/src/implementations/blue_green_swap.py` lines 80-97 uses Win32 `MoveFileExW` (`MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH`) targeting `%LOCALAPPDATA%\MedPlatform\config\active_db.json`.
   - **ROA-03 (No ChromaDB on Client)**: `grep_search` across `medclient/` returned 0 matches for `chromadb`. `medclient/sidecar-python/src/implementations/onnx_semantic.py` lines 18-21 implements ONNX Runtime INT8 (`providers=["CPUExecutionProvider"]`, `intra_op_num_threads=2`) and SQLite BLOB dot-product cosine similarity.
   - **ROA-10 (CYP450 Prodrug Bioactivation)**: `medclient/sidecar-python/src/implementations/cyp450_engine.py` lines 152-168 evaluates `is_prodrug = 1`. Inactive prodrug + inhibitor yields Blackbox Warning Level 1 (*"Lethal therapeutic failure"*).
   - **ROA-12 (Singleton WebGL Broker)**: `medclient/frontend-react/src/implementations/SingletonWebGLBroker.ts` lines 22-56 limits active WebGL context to $\le 1$ with forced preemption `forceLoseActiveContext()`.
   - **ROA-24 (Domain Exception Hierarchy)**: `medclient/sidecar-python/src/base/exceptions.py` lines 4-8 defines `class MedClientError(ValueError)`.
   - **All 24 Assumptions (ROA-01 to ROA-24)**: 100% verified present in implementation code.

2. **Test & Build Verification**:
   - `cargo clippy --manifest-path medclient/core-rust/Cargo.toml`: Exit code 0, 0 warnings.
   - `cargo test --manifest-path medclient/core-rust/Cargo.toml`: 9 passed, 0 failed in 0.03s.
   - `.\agent_env\Scripts\python -m pytest medfactory/tests -v`: 4 passed, 0 failed in 1.15s.
   - `.\agent_env\Scripts\python -m pytest medclient/sidecar-python/tests -v`: 23 passed, 0 failed in 0.75s.
   - `.\agent_env\Scripts\python -m pytest tests/ -q`: 517 passed, 0 failed in 4.71s.
   - `cd medclient/frontend-react; npx vitest run`: 8 passed, 0 failed in 128ms.
   - `cd medclient/frontend-react; npm run build`: Built successfully in 2.51s, 0 TypeScript errors.

3. **Micro-File Line Limits & Organization**:
   - Total source files scanned in `medfactory/src/`, `medclient/core-rust/src/`, `medclient/sidecar-python/src/`, and `medclient/frontend-react/src/`: 110+ files.
   - Files exceeding 450 lines: **0**. Max lines: `SymptomMatcherBlockView.tsx` (372 lines).
   - Directory hierarchy adheres strictly to `interfaces/`, `base/`, `implementations/`.

4. **Integrity Violations Directly Observed**:
   - **Violation A (Frontend Static Placeholder Bypass)**: In `medclient/frontend-react/src/implementations/MedClientAppShell.tsx` lines 60-155, four hardcoded constant objects are declared: `DEFAULT_CLINICAL_SHEET`, `DEFAULT_SYMPTOM_MATCHER`, `DEFAULT_DRUG_SAFETY`, and `DEFAULT_EXAM_BLOCK`. In lines 309-347, these static objects are passed directly as props to the 4 SDUI block views. `SidecarIpcClient` is never instantiated or imported in `MedClientAppShell.tsx` or `useMedClientStore.ts`.
   - **Violation B (Simulated NLI Evaluation)**: In `medclient/frontend-react/src/implementations/ExamSimulatorBlockView.tsx` lines 87-96:
     ```typescript
     const isEntailed =
       trimmedHypothesis.length >= 4 &&
       (trimmedHypothesis.includes(referencePremise) ||
         referencePremise.includes(trimmedHypothesis));
     setNliPassed(isEntailed);
     ```
     Substrings are matched locally rather than invoking the sidecar's ONNX INT8 NLI cross-encoder.
   - **Violation C (Hardcoded Symptom Lexicon)**: In `medclient/frontend-react/src/implementations/SymptomMatcherBlockView.tsx` lines 11-32, `COLLOQUIAL_HPO_DICTIONARY` defines 4 hardcoded entries, searched locally via Levenshtein distance rather than querying the backend sidecar.
   - **Violation D (Empty `pass` and Aseptic Suppression)**: In `medclient/sidecar-python/src/main.py` lines 41-46:
     ```python
     if not sys.stdin.isatty():
         try:
             first_line = sys.stdin.readline()
             if first_line:
                 return first_line.strip()
         except Exception:
             pass
     ```
   - **Violation E (Generic Identifiers)**: In `medclient/sidecar-python/src/base/agentic_models.py` line 62 (`def result(self)`) and line 39 (`input_data`).

---

## 2. Logic Chain

1. **Step 1 (Architectural Verification)**: Observations 1.1–1.3 confirm that all 24 operational assumptions (ROA-01 to ROA-24) have been faithfully integrated into the core engine and backend sidecar. Micro-file line limits (<=450 lines), structural tiers (`interfaces/base/implementations`), and exact dependency pinning are fully satisfied.
2. **Step 2 (Compilation & Execution Verification)**: Observation 1.2 demonstrates that the entire multi-lingual stack (Rust, Python, TypeScript/React) compiles cleanly without warnings and passes all 561 automated tests (9 Rust + 4 Factory + 23 Sidecar + 517 Master + 8 Vitest).
3. **Step 3 (Forensic Dogma Application)**: The User Global Rules (*"Tolleranza Zero alle Simulazioni"*, *"Catalogo Esaustivo dei Marcatori e Anti-Pattern Banditi"*, and *"Regola di Non-Suppressione"*) and the Priority Dispatch message strictly prohibit:
   - Dummy/facade implementations and static placeholder data that simulate system behavior.
   - Bypass constructs: `pass`, empty blocks, aseptic error suppressions `except Exception: pass`.
   - Generic identifiers: `result`, `data`.
4. **Step 4 (Evidence Synthesis)**:
   - Observation 4.A demonstrates that `MedClientAppShell.tsx` renders static placeholder constants instead of executing real HTTP calls to the sidecar via `SidecarIpcClient.ts`.
   - Observation 4.B demonstrates that `ExamSimulatorBlockView.tsx` simulates NLI evaluation using naive substring containment instead of calling the sidecar's ONNX NLI model.
   - Observation 4.C demonstrates that `SymptomMatcherBlockView.tsx` relies on a 4-item hardcoded dictionary instead of querying the backend sidecar.
   - Observation 4.D demonstrates that `medclient/sidecar-python/src/main.py:46` contains an empty `pass` in an aseptic `except Exception:` block.
   - Observation 4.E demonstrates banned generic identifiers in `agentic_models.py`.
5. **Step 5 (Verdict Formulation)**: Because the forensic mandate dictates that a single integrity violation requires rejection of the work product, the final verdict is unambiguously **INTEGRITY VIOLATION**.

---

## 3. Caveats

- The auditor operated in strict read-only mode, recording observations and executing tests without altering any production code.
- Functional business logic and algorithmic correctness in the Python sidecar and Rust core are verified and robust; the system compiles and all 561 tests pass.
- The rejection is based on the forensic zero-tolerance dogma regarding static placeholder data in the frontend, simulated NLI evaluation, empty `pass` suppression, and generic identifier rules.

---

## 4. Conclusion

- **Operational Assumptions Status**: **100% CONFORMANT (ROA-01 to ROA-24 Validated)**.
- **Compilation & Test Suite Status**: **100% PASS (561/561 Tests Passed)**.
- **Forensic Audit Verdict**: **INTEGRITY VIOLATION**.
- **Action Required**: The development/refactoring team must execute the 5-point remediation plan documented in Section 5 of `analysis.md` (connect `SidecarIpcClient` to `MedClientAppShell`, delegate NLI evaluation to the sidecar, connect symptom search to sidecar endpoints, eliminate `pass` in `main.py`, and rename generic identifiers in `agentic_models.py`).

---

## 5. Verification Method

To independently verify all observations, findings, and test results:

1. **Verify Static Placeholders in Frontend Shell**:
   `grep_search` for `DEFAULT_` in `medclient/frontend-react/src/implementations/MedClientAppShell.tsx` lines 60-155.
2. **Verify Simulated NLI Substring Check**:
   `view_file` on `medclient/frontend-react/src/implementations/ExamSimulatorBlockView.tsx` lines 87-96.
3. **Verify Empty `pass` in Python Entrypoint**:
   `view_file` on `medclient/sidecar-python/src/main.py` lines 41-48.
4. **Execute Full Test Suites**:
   - `cargo test --manifest-path medclient/core-rust/Cargo.toml`
   - `.\agent_env\Scripts\python -m pytest medclient/sidecar-python/tests medfactory/tests tests/`
   - `cd medclient/frontend-react && npx vitest run`
   - `cd medclient/frontend-react && npm run build`
