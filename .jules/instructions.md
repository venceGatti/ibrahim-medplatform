# Google Labs Jules - Master Autonomous Directives for MedPlatform

This document governs all autonomous audit, refactoring, performance optimization, and quality assurance tasks executed by Google Labs Jules on `venceGatti/ibrahim-medplatform`.

---

## 1. System Architecture & Component Mapping

MedPlatform is a zero-mock, offline-first clinical consultation and simulation system structured into four decoupled layers:

| Layer | Directory | Tech Stack | Primary Responsibilities |
|---|---|---|---|
| **Knowledge Packager** | `medfactory/` | Python 3.12, SQLite, Ed25519, Zstandard | Builds encrypted `.medpack` databases with deterministic schema, custom Zstandard dictionary compression, and cryptographic manifest signing. |
| **Clinical Sidecar** | `medclient/sidecar-python/` | Python 3.12, FastAPI, Polars | Local computational engine on `127.0.0.1:8765`: NEWS2/qSOFA triage, CYP450 multi-drug clearance, CKD-EPI eGFR, HPO symptom matching, and FSRS-4.5. |
| **Host Supervisor** | `medclient/core-rust/` | Rust 2021, Tauri | Win32 Job Object process boundary, `< 300 MB` memory ceiling enforcement, zero-copy `memmap2` asset caching for `med-asset://`. |
| **Frontend SDUI** | `medclient/frontend-react/` | React 19, TypeScript, Vite, TailwindCSS | 60 FPS DOM retention, WAI-ARIA 1.2 accessible comboboxes, Even-Odd Ray-Casting visual canvas feedback, single-broker WebGL 3D views. |

---

## 2. Core Dogma & Invariant Constraints

When performing code audits or refactoring, Jules MUST enforce these non-negotiable rules:

### A. Zero-Mock & Real Execution Policy
- **Absolute ban on placeholders**: Never introduce or retain `pass`, `...`, `return null`, `return {}`, `return []`, `todo!()`, or `throw new NotImplementedException()`.
- **Zero mock frameworks**: No `unittest.mock`, `vi.fn()`, or synthetic dummy payloads in core production flows. All calculations and network sweeps must execute physically or via deterministic algorithmic models.
- **Fail-fast on unknown nodes**: If a component receives an unregistered SDUI block type, it must raise `SDUINodeNotFoundError` immediately. Silent fallbacks to default ping or empty cards are strictly forbidden.

### B. Micro-File Modularization ($\le 350$ Lines)
- Every source file must remain compact ($\le 350$ lines, absolute hard ceiling at 400 lines).
- Structure logic strictly into `interfaces/` (contracts), `base/` (registries, abstract classes, store), and `implementations/` (concrete nodes and engine logic).

### C. Cross-Layer Contract Parity
- **Payload Parity**: Frontend TypeScript interfaces in `src/interfaces/sduiContracts.ts` must maintain 100% field-for-field parity with Python Pydantic models in `medclient/sidecar-python/src/base/sdui_models.py`.
- **HMAC Authentication**: Inter-process communication between Frontend/Rust and Python Sidecar requires the `X-Tauri-IPC-Secret` header verified via constant-time comparison (`hmac.compare_digest`).

---

## 3. UI/UX, Clinical Ergonomics & Visual Quality Focus

When evaluating or improving user-facing components (`medclient/frontend-react/`):
1. **Clinical Callout Theme**:
   - `RED_FLAG`: Border and background in `rose-600/10` with high-contrast emergency red badge.
   - `BLACKBOX`: Border in `amber-500/20` with bold clinical safety directive and alternative CPIC/FDA guidance.
   - `CLINICAL_PEARL`: Border in `sky-600/20` with sapphire clinical evidence badge.
2. **Keyboard Accessibility & WAI-ARIA 1.2**:
   - Combobox inputs must have `aria-haspopup="listbox"`, `aria-expanded`, and support `ArrowDown`/`ArrowUp` navigation, `Escape` closing, and instant selection on `Enter`.
   - Distinguish confirmed symptoms (`PRESENT` in emerald green) from pertinent negatives (`ABSENT` in warning red applying $W^- = -12.0$ diagnostic penalty).
3. **Canvas Geometric Precision**:
   - Normalized coordinates for visual hotspot exams must be strictly clamped to $[0, 1]^2$.
   - Interactive clicks must render a localized tolerance ring ($R_{tol} \le 0.02$) with instantaneous Even-Odd Ray-Casting hit detection feedback.
4. **DOM Retention at 60 FPS**:
   - Tab switching across the 4 clinical views must solely toggle CSS visibility classes (`hidden opacity-0` vs `block opacity-100`) to preserve scroll offsets, 3D WebGL context bindings, and user selections without unmounting.

---

## 4. Verification & Gate Commands

All proposed changes must pass their respective suites with 0 errors before generating a Pull Request:

```bash
# 1. Frontend Build & Vitest (React 19)
cd medclient/frontend-react
npm run build
npx vitest run

# 2. Rust Core Engine
cargo test --manifest-path medclient/core-rust/Cargo.toml

# 3. Python Clinical Sidecar
pytest medclient/sidecar-python/tests -v

# 4. Master E2E Parity Runner
python tests/master_e2e_runner.py
```
