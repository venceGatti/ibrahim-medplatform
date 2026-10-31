1. **Sync Callout models (`sdui_models.py` with `sduiContracts.ts`):**
   - Update `CalloutSeverity` in `sdui_models.py` to `RED_FLAG`, `BLACKBOX`, `CLINICAL_PEARL`, `INFO`, `WARNING`, `CRITICAL`.
   - Update `CalloutEntry` in `sdui_models.py` to match `ClinicalCallout`: keep `severity`, `message`, `title` (removing `body_markdown`, `icd10_refs`, `hpo_refs`, `atc_refs` and updating required fields).

2. **Sync Clinical and Symptom blocks (`sdui_models.py` with `sduiContracts.ts`):**
   - Update `ClinicalSheetBlock` in `sdui_models.py`: Add `media_sha256_hashes`, `molecule_sha256_svg`, `molecule_sha256_pdb`. Remove `vitals_snapshot`, `differential_diagnoses`, `component_type`.
   - Update `SymptomMatcherBlock` in `sdui_models.py`: Add `pertinent_negatives`, `triage_telemetry`. Remove `symptoms_tree`, `component_type`.

3. **Sync Drug and Exam blocks (`sdui_models.py` with `sduiContracts.ts`):**
   - Update `DrugSafetyBlock` in `sdui_models.py`: Add `qtc_tisdale_score`, `triple_whammy_detected`, `fdc_decompositions`. Remove `component_type`.
   - Update `ExamSimulatorBlock` in `sdui_models.py`: Add `question_spec`. Remove `item_data`, `scenario_katex`, `options`, `component_type`.

4. **Sync Payload Envelope (`sdui_models.py` with `sduiContracts.ts`):**
   - Update `SDUIMessageEnvelope` to `SDUIPayloadEnvelope` with `schema_version`, `active_slot`, `system_alert_level`, and `blocks` (removing `session_id`, `sequence_number`).

5. **Verify Python changes:**
   - Use `read_file` to verify the modified `sdui_models.py` was correctly saved.

6. **Update `ClinicalSheetBlockView.tsx`:**
   - Modify `resolveCalloutThemeClasses` and `resolveCalloutBadgeClasses` to use exactly the requested Tailwind palettes (`rose-600`, `amber-500`, `sky-600`) for the clinical callouts (`RED_FLAG`, `BLACKBOX`, `CLINICAL_PEARL`). For example, replacing `amber-500/20 bg-amber-950/40 text-amber-200 ring-1 ring-amber-500/20` with `border-amber-500 bg-amber-500 text-amber-50` or standardizing it with `sky-600` for `CLINICAL_PEARL`. The instructions specifically say: "high-contrast, accessible medical palettes (Tailwind rose-600, amber-500, sky-600) with legible typography".

7. **Update `VirtualBlockWindow.tsx`:**
   - Add `contain: 'layout style paint'` to the inline styles of virtual rows (`.sdui-virtual-row`) to ensure smooth 60 FPS scrolling and bounding DOM updates.

8. **Update `SymptomMatcherBlockView.tsx`:**
   - Update the `ArrowUp` logic in `handleInputKeyDown` to prevent jumping to `-1` or index out of bounds. Example fix: `setHighlightedIndex((previousIndex) => previousIndex <= 0 ? rawSuggestions.length - 1 : previousIndex - 1)`.

9. **Run tests:**
   - Run the frontend tests via `cd medclient/frontend-react && npm run test`.
   - Run the backend tests via `cd medclient/sidecar-python && python -m pytest tests/`.

10. **Pre-Commit step:**
    - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
