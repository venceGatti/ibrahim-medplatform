# Dispatch: Explorer Test Remediation & Milestone M4 Architecture

## Task
You are the Test Remediation and Frontend Architecture Explorer (`explorer_test_remediation_and_m4_plan`).
`cohesion_inspector_1` reported that `tests/` contains 514 tests which currently test standalone local mock variables rather than importing and verifying the real modules from `medfactory` and `medclient/sidecar-python`. In addition, Milestone M4 (React SDUI Frontend & Tauri Desktop Integration) needs a comprehensive architectural specification before implementation.

Your role is strictly READ-ONLY exploration. Do NOT edit or write code files. Formulate a technical remediation and design plan and write your report to `.agents/teamwork/explorer_test_remediation_and_m4_plan/analysis.md` and `handoff.md`.

## Mandatory Reading
1. `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\ORIGINAL_REQUEST.md` (Verbatim user requests)
2. `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\cohesion_inspector_1\handoff.md` (Section 1.1 item 1 regarding tests/)
3. `c:\Users\vence\Downloads\projects\ibrahim\PROJECT.md` (Features 41-48, Milestone M4)
4. `c:\Users\vence\Downloads\projects\ibrahim\TEST_INFRA.md`
5. `c:\Users\vence\Downloads\projects\ibrahim\tests\e2e_runner.py` and test suites in `tests/tier1_features/`, `tests/tier2_boundaries/`, `tests/tier3_cross_features/`, `tests/tier4_real_world/`
6. `c:\Users\vence\Downloads\projects\ibrahim\SRS_MedClient_Architettura_Completa.md` (Modulo 1.3 & 2.1)

## Objectives to Address:
1. **Real Test Suite Remediation in `tests/`**:
   - Plan the transformation of the 514 test files in `tests/` so that every test imports the actual classes and functions from `medfactory` (e.g., `ZstdCompressionService`, `SqliteModuleBuilder`, `PyHpoGraphService`, `MedpackAssembler`) and `medclient.sidecar_python` (e.g., `CsrLogOddsRanker`, `Cyp450Engine`, `QtcProlongationService`, `TripleWhammyDetector`, `CkdEpiCalculator`, `FsrsScheduler`, `CrossEncoderEngine`).
   - Eliminate all local tautologies and synthetic dummy variables.
   - Ensure `tests/e2e_runner.py` runs authentic end-to-end assertions against the actual production codebase.
2. **Milestone M4 Architecture (React SDUI Frontend & Tauri Desktop Integration)**:
   - Directory: `medclient/frontend-react/`
   - Technology Stack: Vite, React 19, TypeScript, TailwindCSS. Pinned exact package versions in `package.json`.
   - Layout: `interfaces/`, `base/`, `implementations/` (or `types/`, `components/`, `services/`) with all source files strictly under 300–450 lines.
   - Core Features to Map:
     - Feature 41: Tauri v2 desktop shell invoking Rust commands via `@tauri-apps/api`.
     - Feature 42: Zustand persistent store preserving DOM & state across tabs with zero data loss.
     - Feature 43: Polymorphic SDUI 4-block engine rendering `ClinicalSheetBlock`, `SymptomMatcherBlock`, `DrugSafetyBlock`, and `ExamSimulatorBlock` with Dual Registry Aliasing.
     - Feature 44: Virtual windowing (<30 DOM nodes) for massive symptom trees and monograph sections.
     - Feature 45: Zero-copy `med-asset://` custom protocol integration in `<img src="med-asset://...">`.
     - Feature 46: Singleton WebGL broker for 3D anatomical viewer with context loss auto-recovery.
     - Feature 47: Agentic API client exposing UI state to `/agent/*`.
     - Feature 48: High-DPI physical coordinate normalization for Even-Odd raycasting hotspots.

## Deliverables
- Detailed remediation and design report in `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\explorer_test_remediation_and_m4_plan\analysis.md`
- 5-Component Handoff Report in `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\explorer_test_remediation_and_m4_plan\handoff.md`


## 2026-10-30T23:17:38Z
Priority: MESSAGE_PRIORITY_HIGH
Sender: 123b80e3-ef7e-4eee-9c78-b41caaecc724
Content:
You are the Test Remediation and Frontend Architecture Explorer (explorer_test_remediation_and_m4_plan).
Working directory: c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\explorer_test_remediation_and_m4_plan\
Original Request: c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\ORIGINAL_REQUEST.md
Dispatch Instructions: c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\explorer_test_remediation_and_m4_plan\DISPATCH.md
Cohesion Inspector Handoff: c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\cohesion_inspector_1\handoff.md
Project Index: c:\Users\vence\Downloads\projects\ibrahim\PROJECT.md
Test Infrastructure: c:\Users\vence\Downloads\projects\ibrahim\TEST_INFRA.md

Investigate and design:
1. Complete remediation plan for tests/: transform the 514 tests into authentic integration and unit tests that import real classes from medfactory and medclient/sidecar-python and execute real verification without tautologies or mock variables.
2. Milestone M4 Architecture & Implementation Plan: React 19, TypeScript, TailwindCSS, Vite frontend in medclient/frontend-react/ with Zustand persistent store, polymorphic 4-block SDUI engine, virtual windowing (<30 DOM nodes), zero-copy med-asset:// integration, singleton WebGL broker, Agentic API client, and normalized coordinate hotspots. All files <= 300-450 lines in interfaces/, base/, implementations/.

Do NOT edit code files. Write your analysis to c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\explorer_test_remediation_and_m4_plan\analysis.md and deliver a 5-component handoff in handoff.md. Send a completion message when done.
