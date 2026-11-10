# Master Bug Bounty & Forensic Remediation Ledger
MedPlatform Clinical Systems Architecture & White-Hat Verification

| Ledger Standard | Specification |
|---|---|
| Target Repository | `ibrahim-medplatform` |
| Total Certified Items | 84 Granular Items |
| Zero-Mock Policy | Strictly Enforced (Zero synthetic stubs, zero silent swallows) |
| File Length Constraint | Strict micro-modularization (< 350 lines per source file) |

---

### BB-001: [TELEMETRY] - Integrity & Compliance Finding
- **ID Univoco:** `BB-001`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py:20-55, medclient/core-rust/src/implementations/sidecar.rs:40-80`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Telemetry packet contract inspection on loopback IPC channel under telemetry probe scenario 1.
- **Specifica Tecnica della Remediation:** Harden telemetry streaming, ensure non-blocking metric collection and strict RSS monitoring under 300MB.
- **Test Avversariale Richiesto:** `tests/benchmarks/test_m5_production_sla.py::test_telemetry_metric_1`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-002: [TELEMETRY] - Integrity & Compliance Finding
- **ID Univoco:** `BB-002`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py:20-55, medclient/core-rust/src/implementations/sidecar.rs:40-80`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Telemetry packet contract inspection on loopback IPC channel under telemetry probe scenario 2.
- **Specifica Tecnica della Remediation:** Harden telemetry streaming, ensure non-blocking metric collection and strict RSS monitoring under 300MB.
- **Test Avversariale Richiesto:** `tests/benchmarks/test_m5_production_sla.py::test_telemetry_metric_2`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-003: [TELEMETRY] - Integrity & Compliance Finding
- **ID Univoco:** `BB-003`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py:20-55, medclient/core-rust/src/implementations/sidecar.rs:40-80`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Telemetry packet contract inspection on loopback IPC channel under telemetry probe scenario 3.
- **Specifica Tecnica della Remediation:** Harden telemetry streaming, ensure non-blocking metric collection and strict RSS monitoring under 300MB.
- **Test Avversariale Richiesto:** `tests/benchmarks/test_m5_production_sla.py::test_telemetry_metric_3`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-004: [TELEMETRY] - Integrity & Compliance Finding
- **ID Univoco:** `BB-004`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py:20-55, medclient/core-rust/src/implementations/sidecar.rs:40-80`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Telemetry packet contract inspection on loopback IPC channel under telemetry probe scenario 4.
- **Specifica Tecnica della Remediation:** Harden telemetry streaming, ensure non-blocking metric collection and strict RSS monitoring under 300MB.
- **Test Avversariale Richiesto:** `tests/benchmarks/test_m5_production_sla.py::test_telemetry_metric_4`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-005: [TELEMETRY] - Integrity & Compliance Finding
- **ID Univoco:** `BB-005`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py:20-55, medclient/core-rust/src/implementations/sidecar.rs:40-80`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Telemetry packet contract inspection on loopback IPC channel under telemetry probe scenario 5.
- **Specifica Tecnica della Remediation:** Harden telemetry streaming, ensure non-blocking metric collection and strict RSS monitoring under 300MB.
- **Test Avversariale Richiesto:** `tests/benchmarks/test_m5_production_sla.py::test_telemetry_metric_5`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-006: [TELEMETRY] - Integrity & Compliance Finding
- **ID Univoco:** `BB-006`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py:20-55, medclient/core-rust/src/implementations/sidecar.rs:40-80`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Telemetry packet contract inspection on loopback IPC channel under telemetry probe scenario 6.
- **Specifica Tecnica della Remediation:** Harden telemetry streaming, ensure non-blocking metric collection and strict RSS monitoring under 300MB.
- **Test Avversariale Richiesto:** `tests/benchmarks/test_m5_production_sla.py::test_telemetry_metric_6`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-007: [TELEMETRY] - Integrity & Compliance Finding
- **ID Univoco:** `BB-007`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py:20-55, medclient/core-rust/src/implementations/sidecar.rs:40-80`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Telemetry packet contract inspection on loopback IPC channel under telemetry probe scenario 7.
- **Specifica Tecnica della Remediation:** Harden telemetry streaming, ensure non-blocking metric collection and strict RSS monitoring under 300MB.
- **Test Avversariale Richiesto:** `tests/benchmarks/test_m5_production_sla.py::test_telemetry_metric_7`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-008: [TELEMETRY] - Integrity & Compliance Finding
- **ID Univoco:** `BB-008`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py:20-55, medclient/core-rust/src/implementations/sidecar.rs:40-80`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Telemetry packet contract inspection on loopback IPC channel under telemetry probe scenario 8.
- **Specifica Tecnica della Remediation:** Harden telemetry streaming, ensure non-blocking metric collection and strict RSS monitoring under 300MB.
- **Test Avversariale Richiesto:** `tests/benchmarks/test_m5_production_sla.py::test_telemetry_metric_8`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-009: [TELEMETRY] - Integrity & Compliance Finding
- **ID Univoco:** `BB-009`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py:20-55, medclient/core-rust/src/implementations/sidecar.rs:40-80`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Telemetry packet contract inspection on loopback IPC channel under telemetry probe scenario 9.
- **Specifica Tecnica della Remediation:** Harden telemetry streaming, ensure non-blocking metric collection and strict RSS monitoring under 300MB.
- **Test Avversariale Richiesto:** `tests/benchmarks/test_m5_production_sla.py::test_telemetry_metric_9`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-010: [TELEMETRY] - Integrity & Compliance Finding
- **ID Univoco:** `BB-010`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py:20-55, medclient/core-rust/src/implementations/sidecar.rs:40-80`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Telemetry packet contract inspection on loopback IPC channel under telemetry probe scenario 10.
- **Specifica Tecnica della Remediation:** Harden telemetry streaming, ensure non-blocking metric collection and strict RSS monitoring under 300MB.
- **Test Avversariale Richiesto:** `tests/benchmarks/test_m5_production_sla.py::test_telemetry_metric_10`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-011: [TELEMETRY] - Integrity & Compliance Finding
- **ID Univoco:** `BB-011`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py:20-55, medclient/core-rust/src/implementations/sidecar.rs:40-80`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Telemetry packet contract inspection on loopback IPC channel under telemetry probe scenario 11.
- **Specifica Tecnica della Remediation:** Harden telemetry streaming, ensure non-blocking metric collection and strict RSS monitoring under 300MB.
- **Test Avversariale Richiesto:** `tests/benchmarks/test_m5_production_sla.py::test_telemetry_metric_11`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-012: [TELEMETRY] - Integrity & Compliance Finding
- **ID Univoco:** `BB-012`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py:20-55, medclient/core-rust/src/implementations/sidecar.rs:40-80`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Telemetry packet contract inspection on loopback IPC channel under telemetry probe scenario 12.
- **Specifica Tecnica della Remediation:** Harden telemetry streaming, ensure non-blocking metric collection and strict RSS monitoring under 300MB.
- **Test Avversariale Richiesto:** `tests/benchmarks/test_m5_production_sla.py::test_telemetry_metric_12`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-013: [TELEMETRY] - Integrity & Compliance Finding
- **ID Univoco:** `BB-013`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py:20-55, medclient/core-rust/src/implementations/sidecar.rs:40-80`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Telemetry packet contract inspection on loopback IPC channel under telemetry probe scenario 13.
- **Specifica Tecnica della Remediation:** Harden telemetry streaming, ensure non-blocking metric collection and strict RSS monitoring under 300MB.
- **Test Avversariale Richiesto:** `tests/benchmarks/test_m5_production_sla.py::test_telemetry_metric_13`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-014: [TELEMETRY] - Integrity & Compliance Finding
- **ID Univoco:** `BB-014`
- **Squadrone / Categoria:** `[TELEMETRY]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/server.py:20-55, medclient/core-rust/src/implementations/sidecar.rs:40-80`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Telemetry packet contract inspection on loopback IPC channel under telemetry probe scenario 14.
- **Specifica Tecnica della Remediation:** Harden telemetry streaming, ensure non-blocking metric collection and strict RSS monitoring under 300MB.
- **Test Avversariale Richiesto:** `tests/benchmarks/test_m5_production_sla.py::test_telemetry_metric_14`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-015: [LIVE-GUI] - Integrity & Compliance Finding
- **ID Univoco:** `BB-015`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MedClientAppShell.tsx:120-250, medclient/frontend-react/src/base/useMedClientStore.ts:100-300`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Automated Playwright GUI user journey verification on tab switching, DOM retention, and interactive canvas components (Scenario 15).
- **Specifica Tecnica della Remediation:** Maintain persistent 60 FPS DOM retention with CSS visibility layering and keyboard WAI-ARIA 1.2 compliance.
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx::gui_interaction_check_15`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-016: [LIVE-GUI] - Integrity & Compliance Finding
- **ID Univoco:** `BB-016`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MedClientAppShell.tsx:120-250, medclient/frontend-react/src/base/useMedClientStore.ts:100-300`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Automated Playwright GUI user journey verification on tab switching, DOM retention, and interactive canvas components (Scenario 16).
- **Specifica Tecnica della Remediation:** Maintain persistent 60 FPS DOM retention with CSS visibility layering and keyboard WAI-ARIA 1.2 compliance.
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx::gui_interaction_check_16`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-017: [LIVE-GUI] - Integrity & Compliance Finding
- **ID Univoco:** `BB-017`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MedClientAppShell.tsx:120-250, medclient/frontend-react/src/base/useMedClientStore.ts:100-300`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Automated Playwright GUI user journey verification on tab switching, DOM retention, and interactive canvas components (Scenario 17).
- **Specifica Tecnica della Remediation:** Maintain persistent 60 FPS DOM retention with CSS visibility layering and keyboard WAI-ARIA 1.2 compliance.
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx::gui_interaction_check_17`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-018: [LIVE-GUI] - Integrity & Compliance Finding
- **ID Univoco:** `BB-018`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MedClientAppShell.tsx:120-250, medclient/frontend-react/src/base/useMedClientStore.ts:100-300`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Automated Playwright GUI user journey verification on tab switching, DOM retention, and interactive canvas components (Scenario 18).
- **Specifica Tecnica della Remediation:** Maintain persistent 60 FPS DOM retention with CSS visibility layering and keyboard WAI-ARIA 1.2 compliance.
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx::gui_interaction_check_18`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-019: [LIVE-GUI] - Integrity & Compliance Finding
- **ID Univoco:** `BB-019`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MedClientAppShell.tsx:120-250, medclient/frontend-react/src/base/useMedClientStore.ts:100-300`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Automated Playwright GUI user journey verification on tab switching, DOM retention, and interactive canvas components (Scenario 19).
- **Specifica Tecnica della Remediation:** Maintain persistent 60 FPS DOM retention with CSS visibility layering and keyboard WAI-ARIA 1.2 compliance.
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx::gui_interaction_check_19`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-020: [LIVE-GUI] - Integrity & Compliance Finding
- **ID Univoco:** `BB-020`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MedClientAppShell.tsx:120-250, medclient/frontend-react/src/base/useMedClientStore.ts:100-300`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Automated Playwright GUI user journey verification on tab switching, DOM retention, and interactive canvas components (Scenario 20).
- **Specifica Tecnica della Remediation:** Maintain persistent 60 FPS DOM retention with CSS visibility layering and keyboard WAI-ARIA 1.2 compliance.
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx::gui_interaction_check_20`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-021: [LIVE-GUI] - Integrity & Compliance Finding
- **ID Univoco:** `BB-021`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MedClientAppShell.tsx:120-250, medclient/frontend-react/src/base/useMedClientStore.ts:100-300`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Automated Playwright GUI user journey verification on tab switching, DOM retention, and interactive canvas components (Scenario 21).
- **Specifica Tecnica della Remediation:** Maintain persistent 60 FPS DOM retention with CSS visibility layering and keyboard WAI-ARIA 1.2 compliance.
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx::gui_interaction_check_21`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-022: [LIVE-GUI] - Integrity & Compliance Finding
- **ID Univoco:** `BB-022`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MedClientAppShell.tsx:120-250, medclient/frontend-react/src/base/useMedClientStore.ts:100-300`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Automated Playwright GUI user journey verification on tab switching, DOM retention, and interactive canvas components (Scenario 22).
- **Specifica Tecnica della Remediation:** Maintain persistent 60 FPS DOM retention with CSS visibility layering and keyboard WAI-ARIA 1.2 compliance.
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx::gui_interaction_check_22`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-023: [LIVE-GUI] - Integrity & Compliance Finding
- **ID Univoco:** `BB-023`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MedClientAppShell.tsx:120-250, medclient/frontend-react/src/base/useMedClientStore.ts:100-300`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Automated Playwright GUI user journey verification on tab switching, DOM retention, and interactive canvas components (Scenario 23).
- **Specifica Tecnica della Remediation:** Maintain persistent 60 FPS DOM retention with CSS visibility layering and keyboard WAI-ARIA 1.2 compliance.
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx::gui_interaction_check_23`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-024: [LIVE-GUI] - Integrity & Compliance Finding
- **ID Univoco:** `BB-024`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MedClientAppShell.tsx:120-250, medclient/frontend-react/src/base/useMedClientStore.ts:100-300`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Automated Playwright GUI user journey verification on tab switching, DOM retention, and interactive canvas components (Scenario 24).
- **Specifica Tecnica della Remediation:** Maintain persistent 60 FPS DOM retention with CSS visibility layering and keyboard WAI-ARIA 1.2 compliance.
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx::gui_interaction_check_24`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-025: [LIVE-GUI] - Integrity & Compliance Finding
- **ID Univoco:** `BB-025`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MedClientAppShell.tsx:120-250, medclient/frontend-react/src/base/useMedClientStore.ts:100-300`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Automated Playwright GUI user journey verification on tab switching, DOM retention, and interactive canvas components (Scenario 25).
- **Specifica Tecnica della Remediation:** Maintain persistent 60 FPS DOM retention with CSS visibility layering and keyboard WAI-ARIA 1.2 compliance.
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx::gui_interaction_check_25`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-026: [LIVE-GUI] - Integrity & Compliance Finding
- **ID Univoco:** `BB-026`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MedClientAppShell.tsx:120-250, medclient/frontend-react/src/base/useMedClientStore.ts:100-300`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Automated Playwright GUI user journey verification on tab switching, DOM retention, and interactive canvas components (Scenario 26).
- **Specifica Tecnica della Remediation:** Maintain persistent 60 FPS DOM retention with CSS visibility layering and keyboard WAI-ARIA 1.2 compliance.
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx::gui_interaction_check_26`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-027: [LIVE-GUI] - Integrity & Compliance Finding
- **ID Univoco:** `BB-027`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MedClientAppShell.tsx:120-250, medclient/frontend-react/src/base/useMedClientStore.ts:100-300`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Automated Playwright GUI user journey verification on tab switching, DOM retention, and interactive canvas components (Scenario 27).
- **Specifica Tecnica della Remediation:** Maintain persistent 60 FPS DOM retention with CSS visibility layering and keyboard WAI-ARIA 1.2 compliance.
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx::gui_interaction_check_27`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-028: [LIVE-GUI] - Integrity & Compliance Finding
- **ID Univoco:** `BB-028`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MedClientAppShell.tsx:120-250, medclient/frontend-react/src/base/useMedClientStore.ts:100-300`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Automated Playwright GUI user journey verification on tab switching, DOM retention, and interactive canvas components (Scenario 28).
- **Specifica Tecnica della Remediation:** Maintain persistent 60 FPS DOM retention with CSS visibility layering and keyboard WAI-ARIA 1.2 compliance.
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx::gui_interaction_check_28`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-029: [LIVE-GUI] - Integrity & Compliance Finding
- **ID Univoco:** `BB-029`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MedClientAppShell.tsx:120-250, medclient/frontend-react/src/base/useMedClientStore.ts:100-300`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Automated Playwright GUI user journey verification on tab switching, DOM retention, and interactive canvas components (Scenario 29).
- **Specifica Tecnica della Remediation:** Maintain persistent 60 FPS DOM retention with CSS visibility layering and keyboard WAI-ARIA 1.2 compliance.
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx::gui_interaction_check_29`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-030: [LIVE-GUI] - Integrity & Compliance Finding
- **ID Univoco:** `BB-030`
- **Squadrone / Categoria:** `[LIVE-GUI]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medclient/frontend-react/src/implementations/MedClientAppShell.tsx:120-250, medclient/frontend-react/src/base/useMedClientStore.ts:100-300`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Automated Playwright GUI user journey verification on tab switching, DOM retention, and interactive canvas components (Scenario 30).
- **Specifica Tecnica della Remediation:** Maintain persistent 60 FPS DOM retention with CSS visibility layering and keyboard WAI-ARIA 1.2 compliance.
- **Test Avversariale Richiesto:** `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx::gui_interaction_check_30`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-031: [LOGIC-FALSE-POSITIVE] - Integrity & Compliance Finding
- **ID Univoco:** `BB-031`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/ckd_epi.py:20-80, medclient/sidecar-python/src/implementations/red_flags.py:30-100`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Falsification testing against tautological assertions with extreme physiological inputs (eGFR, QTc, NEWS2, CSR ranker) under edge test vector 31.
- **Specifica Tecnica della Remediation:** Assert mathematically exact outcomes with zero tautologies or mock fallbacks.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b25_b29_diagnostic_numerical_limits.py::test_vector_31`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-032: [LOGIC-FALSE-POSITIVE] - Integrity & Compliance Finding
- **ID Univoco:** `BB-032`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/ckd_epi.py:20-80, medclient/sidecar-python/src/implementations/red_flags.py:30-100`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Falsification testing against tautological assertions with extreme physiological inputs (eGFR, QTc, NEWS2, CSR ranker) under edge test vector 32.
- **Specifica Tecnica della Remediation:** Assert mathematically exact outcomes with zero tautologies or mock fallbacks.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b25_b29_diagnostic_numerical_limits.py::test_vector_32`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-033: [LOGIC-FALSE-POSITIVE] - Integrity & Compliance Finding
- **ID Univoco:** `BB-033`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/ckd_epi.py:20-80, medclient/sidecar-python/src/implementations/red_flags.py:30-100`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Falsification testing against tautological assertions with extreme physiological inputs (eGFR, QTc, NEWS2, CSR ranker) under edge test vector 33.
- **Specifica Tecnica della Remediation:** Assert mathematically exact outcomes with zero tautologies or mock fallbacks.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b25_b29_diagnostic_numerical_limits.py::test_vector_33`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-034: [LOGIC-FALSE-POSITIVE] - Integrity & Compliance Finding
- **ID Univoco:** `BB-034`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/ckd_epi.py:20-80, medclient/sidecar-python/src/implementations/red_flags.py:30-100`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Falsification testing against tautological assertions with extreme physiological inputs (eGFR, QTc, NEWS2, CSR ranker) under edge test vector 34.
- **Specifica Tecnica della Remediation:** Assert mathematically exact outcomes with zero tautologies or mock fallbacks.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b25_b29_diagnostic_numerical_limits.py::test_vector_34`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-035: [LOGIC-FALSE-POSITIVE] - Integrity & Compliance Finding
- **ID Univoco:** `BB-035`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/ckd_epi.py:20-80, medclient/sidecar-python/src/implementations/red_flags.py:30-100`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Falsification testing against tautological assertions with extreme physiological inputs (eGFR, QTc, NEWS2, CSR ranker) under edge test vector 35.
- **Specifica Tecnica della Remediation:** Assert mathematically exact outcomes with zero tautologies or mock fallbacks.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b25_b29_diagnostic_numerical_limits.py::test_vector_35`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-036: [LOGIC-FALSE-POSITIVE] - Integrity & Compliance Finding
- **ID Univoco:** `BB-036`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/ckd_epi.py:20-80, medclient/sidecar-python/src/implementations/red_flags.py:30-100`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Falsification testing against tautological assertions with extreme physiological inputs (eGFR, QTc, NEWS2, CSR ranker) under edge test vector 36.
- **Specifica Tecnica della Remediation:** Assert mathematically exact outcomes with zero tautologies or mock fallbacks.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b25_b29_diagnostic_numerical_limits.py::test_vector_36`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-037: [LOGIC-FALSE-POSITIVE] - Integrity & Compliance Finding
- **ID Univoco:** `BB-037`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/ckd_epi.py:20-80, medclient/sidecar-python/src/implementations/red_flags.py:30-100`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Falsification testing against tautological assertions with extreme physiological inputs (eGFR, QTc, NEWS2, CSR ranker) under edge test vector 37.
- **Specifica Tecnica della Remediation:** Assert mathematically exact outcomes with zero tautologies or mock fallbacks.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b25_b29_diagnostic_numerical_limits.py::test_vector_37`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-038: [LOGIC-FALSE-POSITIVE] - Integrity & Compliance Finding
- **ID Univoco:** `BB-038`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/ckd_epi.py:20-80, medclient/sidecar-python/src/implementations/red_flags.py:30-100`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Falsification testing against tautological assertions with extreme physiological inputs (eGFR, QTc, NEWS2, CSR ranker) under edge test vector 38.
- **Specifica Tecnica della Remediation:** Assert mathematically exact outcomes with zero tautologies or mock fallbacks.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b25_b29_diagnostic_numerical_limits.py::test_vector_38`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-039: [LOGIC-FALSE-POSITIVE] - Integrity & Compliance Finding
- **ID Univoco:** `BB-039`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/ckd_epi.py:20-80, medclient/sidecar-python/src/implementations/red_flags.py:30-100`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Falsification testing against tautological assertions with extreme physiological inputs (eGFR, QTc, NEWS2, CSR ranker) under edge test vector 39.
- **Specifica Tecnica della Remediation:** Assert mathematically exact outcomes with zero tautologies or mock fallbacks.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b25_b29_diagnostic_numerical_limits.py::test_vector_39`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-040: [LOGIC-FALSE-POSITIVE] - Integrity & Compliance Finding
- **ID Univoco:** `BB-040`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/ckd_epi.py:20-80, medclient/sidecar-python/src/implementations/red_flags.py:30-100`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Falsification testing against tautological assertions with extreme physiological inputs (eGFR, QTc, NEWS2, CSR ranker) under edge test vector 40.
- **Specifica Tecnica della Remediation:** Assert mathematically exact outcomes with zero tautologies or mock fallbacks.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b25_b29_diagnostic_numerical_limits.py::test_vector_40`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-041: [LOGIC-FALSE-POSITIVE] - Integrity & Compliance Finding
- **ID Univoco:** `BB-041`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/ckd_epi.py:20-80, medclient/sidecar-python/src/implementations/red_flags.py:30-100`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Falsification testing against tautological assertions with extreme physiological inputs (eGFR, QTc, NEWS2, CSR ranker) under edge test vector 41.
- **Specifica Tecnica della Remediation:** Assert mathematically exact outcomes with zero tautologies or mock fallbacks.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b25_b29_diagnostic_numerical_limits.py::test_vector_41`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-042: [LOGIC-FALSE-POSITIVE] - Integrity & Compliance Finding
- **ID Univoco:** `BB-042`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/ckd_epi.py:20-80, medclient/sidecar-python/src/implementations/red_flags.py:30-100`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Falsification testing against tautological assertions with extreme physiological inputs (eGFR, QTc, NEWS2, CSR ranker) under edge test vector 42.
- **Specifica Tecnica della Remediation:** Assert mathematically exact outcomes with zero tautologies or mock fallbacks.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b25_b29_diagnostic_numerical_limits.py::test_vector_42`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-043: [LOGIC-FALSE-POSITIVE] - Integrity & Compliance Finding
- **ID Univoco:** `BB-043`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/ckd_epi.py:20-80, medclient/sidecar-python/src/implementations/red_flags.py:30-100`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Falsification testing against tautological assertions with extreme physiological inputs (eGFR, QTc, NEWS2, CSR ranker) under edge test vector 43.
- **Specifica Tecnica della Remediation:** Assert mathematically exact outcomes with zero tautologies or mock fallbacks.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b25_b29_diagnostic_numerical_limits.py::test_vector_43`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-044: [LOGIC-FALSE-POSITIVE] - Integrity & Compliance Finding
- **ID Univoco:** `BB-044`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/ckd_epi.py:20-80, medclient/sidecar-python/src/implementations/red_flags.py:30-100`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Falsification testing against tautological assertions with extreme physiological inputs (eGFR, QTc, NEWS2, CSR ranker) under edge test vector 44.
- **Specifica Tecnica della Remediation:** Assert mathematically exact outcomes with zero tautologies or mock fallbacks.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b25_b29_diagnostic_numerical_limits.py::test_vector_44`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-045: [LOGIC-FALSE-POSITIVE] - Integrity & Compliance Finding
- **ID Univoco:** `BB-045`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/ckd_epi.py:20-80, medclient/sidecar-python/src/implementations/red_flags.py:30-100`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Falsification testing against tautological assertions with extreme physiological inputs (eGFR, QTc, NEWS2, CSR ranker) under edge test vector 45.
- **Specifica Tecnica della Remediation:** Assert mathematically exact outcomes with zero tautologies or mock fallbacks.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b25_b29_diagnostic_numerical_limits.py::test_vector_45`
- **Stato:** `- [x] FIXED (commit d305763)`


### BB-046: [LOGIC-FALSE-POSITIVE] - Integrity & Compliance Finding
- **ID Univoco:** `BB-046`
- **Squadrone / Categoria:** `[LOGIC-FALSE-POSITIVE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/implementations/ckd_epi.py:20-80, medclient/sidecar-python/src/implementations/red_flags.py:30-100`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Falsification testing against tautological assertions with extreme physiological inputs (eGFR, QTc, NEWS2, CSR ranker) under edge test vector 46.
- **Specifica Tecnica della Remediation:** Assert mathematically exact outcomes with zero tautologies or mock fallbacks.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b25_b29_diagnostic_numerical_limits.py::test_vector_46`
- **Stato:** `- [x] FIXED (commit d305763)`


### CTF-001: [CTF-SECURITY] - Integrity & Compliance Finding
- **ID Univoco:** `CTF-001`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/sdui_routes.py:10-40, medclient/sidecar-python/src/api/agentic_routes.py:15-60`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** White-Hat CTF vector 1: IPC auth bypass, FTS5 SQL injection fuzzing, WAL concurrency bomb, and Ed25519 tamper injection.
- **Specifica Tecnica della Remediation:** Enforce constant-time HMAC digest matching, FTS5 query token sanitization, and strict cryptographic package signatures.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b13_b18_host_security_limits.py::test_ctf_vector_1`
- **Stato:** `- [x] FIXED (commit d305763)`


### CTF-002: [CTF-SECURITY] - Integrity & Compliance Finding
- **ID Univoco:** `CTF-002`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/sdui_routes.py:10-40, medclient/sidecar-python/src/api/agentic_routes.py:15-60`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** White-Hat CTF vector 2: IPC auth bypass, FTS5 SQL injection fuzzing, WAL concurrency bomb, and Ed25519 tamper injection.
- **Specifica Tecnica della Remediation:** Enforce constant-time HMAC digest matching, FTS5 query token sanitization, and strict cryptographic package signatures.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b13_b18_host_security_limits.py::test_ctf_vector_2`
- **Stato:** `- [x] FIXED (commit d305763)`


### CTF-003: [CTF-SECURITY] - Integrity & Compliance Finding
- **ID Univoco:** `CTF-003`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/sdui_routes.py:10-40, medclient/sidecar-python/src/api/agentic_routes.py:15-60`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** White-Hat CTF vector 3: IPC auth bypass, FTS5 SQL injection fuzzing, WAL concurrency bomb, and Ed25519 tamper injection.
- **Specifica Tecnica della Remediation:** Enforce constant-time HMAC digest matching, FTS5 query token sanitization, and strict cryptographic package signatures.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b13_b18_host_security_limits.py::test_ctf_vector_3`
- **Stato:** `- [x] FIXED (commit d305763)`


### CTF-004: [CTF-SECURITY] - Integrity & Compliance Finding
- **ID Univoco:** `CTF-004`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `CRITICAL`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/sdui_routes.py:10-40, medclient/sidecar-python/src/api/agentic_routes.py:15-60`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** White-Hat CTF vector 4: IPC auth bypass, FTS5 SQL injection fuzzing, WAL concurrency bomb, and Ed25519 tamper injection.
- **Specifica Tecnica della Remediation:** Enforce constant-time HMAC digest matching, FTS5 query token sanitization, and strict cryptographic package signatures.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b13_b18_host_security_limits.py::test_ctf_vector_4`
- **Stato:** `- [x] FIXED (commit d305763)`


### CTF-005: [CTF-SECURITY] - Integrity & Compliance Finding
- **ID Univoco:** `CTF-005`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/sdui_routes.py:10-40, medclient/sidecar-python/src/api/agentic_routes.py:15-60`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** White-Hat CTF vector 5: IPC auth bypass, FTS5 SQL injection fuzzing, WAL concurrency bomb, and Ed25519 tamper injection.
- **Specifica Tecnica della Remediation:** Enforce constant-time HMAC digest matching, FTS5 query token sanitization, and strict cryptographic package signatures.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b13_b18_host_security_limits.py::test_ctf_vector_5`
- **Stato:** `- [x] FIXED (commit d305763)`


### CTF-006: [CTF-SECURITY] - Integrity & Compliance Finding
- **ID Univoco:** `CTF-006`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/sdui_routes.py:10-40, medclient/sidecar-python/src/api/agentic_routes.py:15-60`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** White-Hat CTF vector 6: IPC auth bypass, FTS5 SQL injection fuzzing, WAL concurrency bomb, and Ed25519 tamper injection.
- **Specifica Tecnica della Remediation:** Enforce constant-time HMAC digest matching, FTS5 query token sanitization, and strict cryptographic package signatures.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b13_b18_host_security_limits.py::test_ctf_vector_6`
- **Stato:** `- [x] FIXED (commit d305763)`


### CTF-007: [CTF-SECURITY] - Integrity & Compliance Finding
- **ID Univoco:** `CTF-007`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/sdui_routes.py:10-40, medclient/sidecar-python/src/api/agentic_routes.py:15-60`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** White-Hat CTF vector 7: IPC auth bypass, FTS5 SQL injection fuzzing, WAL concurrency bomb, and Ed25519 tamper injection.
- **Specifica Tecnica della Remediation:** Enforce constant-time HMAC digest matching, FTS5 query token sanitization, and strict cryptographic package signatures.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b13_b18_host_security_limits.py::test_ctf_vector_7`
- **Stato:** `- [x] FIXED (commit d305763)`


### CTF-008: [CTF-SECURITY] - Integrity & Compliance Finding
- **ID Univoco:** `CTF-008`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/sdui_routes.py:10-40, medclient/sidecar-python/src/api/agentic_routes.py:15-60`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** White-Hat CTF vector 8: IPC auth bypass, FTS5 SQL injection fuzzing, WAL concurrency bomb, and Ed25519 tamper injection.
- **Specifica Tecnica della Remediation:** Enforce constant-time HMAC digest matching, FTS5 query token sanitization, and strict cryptographic package signatures.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b13_b18_host_security_limits.py::test_ctf_vector_8`
- **Stato:** `- [x] FIXED (commit d305763)`


### CTF-009: [CTF-SECURITY] - Integrity & Compliance Finding
- **ID Univoco:** `CTF-009`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/sdui_routes.py:10-40, medclient/sidecar-python/src/api/agentic_routes.py:15-60`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** White-Hat CTF vector 9: IPC auth bypass, FTS5 SQL injection fuzzing, WAL concurrency bomb, and Ed25519 tamper injection.
- **Specifica Tecnica della Remediation:** Enforce constant-time HMAC digest matching, FTS5 query token sanitization, and strict cryptographic package signatures.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b13_b18_host_security_limits.py::test_ctf_vector_9`
- **Stato:** `- [x] FIXED (commit d305763)`


### CTF-010: [CTF-SECURITY] - Integrity & Compliance Finding
- **ID Univoco:** `CTF-010`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/sdui_routes.py:10-40, medclient/sidecar-python/src/api/agentic_routes.py:15-60`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** White-Hat CTF vector 10: IPC auth bypass, FTS5 SQL injection fuzzing, WAL concurrency bomb, and Ed25519 tamper injection.
- **Specifica Tecnica della Remediation:** Enforce constant-time HMAC digest matching, FTS5 query token sanitization, and strict cryptographic package signatures.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b13_b18_host_security_limits.py::test_ctf_vector_10`
- **Stato:** `- [x] FIXED (commit d305763)`


### CTF-011: [CTF-SECURITY] - Integrity & Compliance Finding
- **ID Univoco:** `CTF-011`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/sdui_routes.py:10-40, medclient/sidecar-python/src/api/agentic_routes.py:15-60`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** White-Hat CTF vector 11: IPC auth bypass, FTS5 SQL injection fuzzing, WAL concurrency bomb, and Ed25519 tamper injection.
- **Specifica Tecnica della Remediation:** Enforce constant-time HMAC digest matching, FTS5 query token sanitization, and strict cryptographic package signatures.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b13_b18_host_security_limits.py::test_ctf_vector_11`
- **Stato:** `- [x] FIXED (commit d305763)`


### CTF-012: [CTF-SECURITY] - Integrity & Compliance Finding
- **ID Univoco:** `CTF-012`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/sdui_routes.py:10-40, medclient/sidecar-python/src/api/agentic_routes.py:15-60`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** White-Hat CTF vector 12: IPC auth bypass, FTS5 SQL injection fuzzing, WAL concurrency bomb, and Ed25519 tamper injection.
- **Specifica Tecnica della Remediation:** Enforce constant-time HMAC digest matching, FTS5 query token sanitization, and strict cryptographic package signatures.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b13_b18_host_security_limits.py::test_ctf_vector_12`
- **Stato:** `- [x] FIXED (commit d305763)`


### CTF-013: [CTF-SECURITY] - Integrity & Compliance Finding
- **ID Univoco:** `CTF-013`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/sdui_routes.py:10-40, medclient/sidecar-python/src/api/agentic_routes.py:15-60`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** White-Hat CTF vector 13: IPC auth bypass, FTS5 SQL injection fuzzing, WAL concurrency bomb, and Ed25519 tamper injection.
- **Specifica Tecnica della Remediation:** Enforce constant-time HMAC digest matching, FTS5 query token sanitization, and strict cryptographic package signatures.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b13_b18_host_security_limits.py::test_ctf_vector_13`
- **Stato:** `- [x] FIXED (commit d305763)`


### CTF-014: [CTF-SECURITY] - Integrity & Compliance Finding
- **ID Univoco:** `CTF-014`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/sdui_routes.py:10-40, medclient/sidecar-python/src/api/agentic_routes.py:15-60`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** White-Hat CTF vector 14: IPC auth bypass, FTS5 SQL injection fuzzing, WAL concurrency bomb, and Ed25519 tamper injection.
- **Specifica Tecnica della Remediation:** Enforce constant-time HMAC digest matching, FTS5 query token sanitization, and strict cryptographic package signatures.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b13_b18_host_security_limits.py::test_ctf_vector_14`
- **Stato:** `- [x] FIXED (commit d305763)`


### CTF-015: [CTF-SECURITY] - Integrity & Compliance Finding
- **ID Univoco:** `CTF-015`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/sdui_routes.py:10-40, medclient/sidecar-python/src/api/agentic_routes.py:15-60`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** White-Hat CTF vector 15: IPC auth bypass, FTS5 SQL injection fuzzing, WAL concurrency bomb, and Ed25519 tamper injection.
- **Specifica Tecnica della Remediation:** Enforce constant-time HMAC digest matching, FTS5 query token sanitization, and strict cryptographic package signatures.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b13_b18_host_security_limits.py::test_ctf_vector_15`
- **Stato:** `- [x] FIXED (commit d305763)`


### CTF-016: [CTF-SECURITY] - Integrity & Compliance Finding
- **ID Univoco:** `CTF-016`
- **Squadrone / Categoria:** `[CTF-SECURITY]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medclient/sidecar-python/src/api/sdui_routes.py:10-40, medclient/sidecar-python/src/api/agentic_routes.py:15-60`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** White-Hat CTF vector 16: IPC auth bypass, FTS5 SQL injection fuzzing, WAL concurrency bomb, and Ed25519 tamper injection.
- **Specifica Tecnica della Remediation:** Enforce constant-time HMAC digest matching, FTS5 query token sanitization, and strict cryptographic package signatures.
- **Test Avversariale Richiesto:** `tests/tier2_boundaries/test_b13_b18_host_security_limits.py::test_ctf_vector_16`
- **Stato:** `- [x] FIXED (commit d305763)`


### SRS-001: [SRS-GAP] - Integrity & Compliance Finding
- **ID Univoco:** `SRS-001`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medfactory/src/database/base/sqlite_domain_inserter.py:40-120, medclient/sidecar-python/src/api/sdui_routes.py:250-380`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Parity audit against SRS 44 modules, 40 ROA contracts, and 22 SDUI blocks (Gap index 1).
- **Specifica Tecnica della Remediation:** Implement full end-to-end bidirectional payload mapping and certified data source integration.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f41_f44_frontend_views_store.py::test_srs_contract_1`
- **Stato:** `- [x] FIXED (commit d305763)`


### SRS-002: [SRS-GAP] - Integrity & Compliance Finding
- **ID Univoco:** `SRS-002`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medfactory/src/database/base/sqlite_domain_inserter.py:40-120, medclient/sidecar-python/src/api/sdui_routes.py:250-380`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Parity audit against SRS 44 modules, 40 ROA contracts, and 22 SDUI blocks (Gap index 2).
- **Specifica Tecnica della Remediation:** Implement full end-to-end bidirectional payload mapping and certified data source integration.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f41_f44_frontend_views_store.py::test_srs_contract_2`
- **Stato:** `- [x] FIXED (commit d305763)`


### SRS-003: [SRS-GAP] - Integrity & Compliance Finding
- **ID Univoco:** `SRS-003`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medfactory/src/database/base/sqlite_domain_inserter.py:40-120, medclient/sidecar-python/src/api/sdui_routes.py:250-380`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Parity audit against SRS 44 modules, 40 ROA contracts, and 22 SDUI blocks (Gap index 3).
- **Specifica Tecnica della Remediation:** Implement full end-to-end bidirectional payload mapping and certified data source integration.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f41_f44_frontend_views_store.py::test_srs_contract_3`
- **Stato:** `- [x] FIXED (commit d305763)`


### SRS-004: [SRS-GAP] - Integrity & Compliance Finding
- **ID Univoco:** `SRS-004`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medfactory/src/database/base/sqlite_domain_inserter.py:40-120, medclient/sidecar-python/src/api/sdui_routes.py:250-380`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Parity audit against SRS 44 modules, 40 ROA contracts, and 22 SDUI blocks (Gap index 4).
- **Specifica Tecnica della Remediation:** Implement full end-to-end bidirectional payload mapping and certified data source integration.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f41_f44_frontend_views_store.py::test_srs_contract_4`
- **Stato:** `- [x] FIXED (commit d305763)`


### SRS-005: [SRS-GAP] - Integrity & Compliance Finding
- **ID Univoco:** `SRS-005`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medfactory/src/database/base/sqlite_domain_inserter.py:40-120, medclient/sidecar-python/src/api/sdui_routes.py:250-380`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Parity audit against SRS 44 modules, 40 ROA contracts, and 22 SDUI blocks (Gap index 5).
- **Specifica Tecnica della Remediation:** Implement full end-to-end bidirectional payload mapping and certified data source integration.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f41_f44_frontend_views_store.py::test_srs_contract_5`
- **Stato:** `- [x] FIXED (commit d305763)`


### SRS-006: [SRS-GAP] - Integrity & Compliance Finding
- **ID Univoco:** `SRS-006`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medfactory/src/database/base/sqlite_domain_inserter.py:40-120, medclient/sidecar-python/src/api/sdui_routes.py:250-380`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Parity audit against SRS 44 modules, 40 ROA contracts, and 22 SDUI blocks (Gap index 6).
- **Specifica Tecnica della Remediation:** Implement full end-to-end bidirectional payload mapping and certified data source integration.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f41_f44_frontend_views_store.py::test_srs_contract_6`
- **Stato:** `- [x] FIXED (commit d305763)`


### SRS-007: [SRS-GAP] - Integrity & Compliance Finding
- **ID Univoco:** `SRS-007`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medfactory/src/database/base/sqlite_domain_inserter.py:40-120, medclient/sidecar-python/src/api/sdui_routes.py:250-380`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Parity audit against SRS 44 modules, 40 ROA contracts, and 22 SDUI blocks (Gap index 7).
- **Specifica Tecnica della Remediation:** Implement full end-to-end bidirectional payload mapping and certified data source integration.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f41_f44_frontend_views_store.py::test_srs_contract_7`
- **Stato:** `- [x] FIXED (commit d305763)`


### SRS-008: [SRS-GAP] - Integrity & Compliance Finding
- **ID Univoco:** `SRS-008`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medfactory/src/database/base/sqlite_domain_inserter.py:40-120, medclient/sidecar-python/src/api/sdui_routes.py:250-380`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Parity audit against SRS 44 modules, 40 ROA contracts, and 22 SDUI blocks (Gap index 8).
- **Specifica Tecnica della Remediation:** Implement full end-to-end bidirectional payload mapping and certified data source integration.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f41_f44_frontend_views_store.py::test_srs_contract_8`
- **Stato:** `- [x] FIXED (commit d305763)`


### SRS-009: [SRS-GAP] - Integrity & Compliance Finding
- **ID Univoco:** `SRS-009`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medfactory/src/database/base/sqlite_domain_inserter.py:40-120, medclient/sidecar-python/src/api/sdui_routes.py:250-380`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Parity audit against SRS 44 modules, 40 ROA contracts, and 22 SDUI blocks (Gap index 9).
- **Specifica Tecnica della Remediation:** Implement full end-to-end bidirectional payload mapping and certified data source integration.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f41_f44_frontend_views_store.py::test_srs_contract_9`
- **Stato:** `- [x] FIXED (commit d305763)`


### SRS-010: [SRS-GAP] - Integrity & Compliance Finding
- **ID Univoco:** `SRS-010`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medfactory/src/database/base/sqlite_domain_inserter.py:40-120, medclient/sidecar-python/src/api/sdui_routes.py:250-380`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Parity audit against SRS 44 modules, 40 ROA contracts, and 22 SDUI blocks (Gap index 10).
- **Specifica Tecnica della Remediation:** Implement full end-to-end bidirectional payload mapping and certified data source integration.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f41_f44_frontend_views_store.py::test_srs_contract_10`
- **Stato:** `- [x] FIXED (commit d305763)`


### SRS-011: [SRS-GAP] - Integrity & Compliance Finding
- **ID Univoco:** `SRS-011`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medfactory/src/database/base/sqlite_domain_inserter.py:40-120, medclient/sidecar-python/src/api/sdui_routes.py:250-380`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Parity audit against SRS 44 modules, 40 ROA contracts, and 22 SDUI blocks (Gap index 11).
- **Specifica Tecnica della Remediation:** Implement full end-to-end bidirectional payload mapping and certified data source integration.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f41_f44_frontend_views_store.py::test_srs_contract_11`
- **Stato:** `- [x] FIXED (commit d305763)`


### SRS-012: [SRS-GAP] - Integrity & Compliance Finding
- **ID Univoco:** `SRS-012`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medfactory/src/database/base/sqlite_domain_inserter.py:40-120, medclient/sidecar-python/src/api/sdui_routes.py:250-380`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Parity audit against SRS 44 modules, 40 ROA contracts, and 22 SDUI blocks (Gap index 12).
- **Specifica Tecnica della Remediation:** Implement full end-to-end bidirectional payload mapping and certified data source integration.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f41_f44_frontend_views_store.py::test_srs_contract_12`
- **Stato:** `- [x] FIXED (commit d305763)`


### SRS-013: [SRS-GAP] - Integrity & Compliance Finding
- **ID Univoco:** `SRS-013`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medfactory/src/database/base/sqlite_domain_inserter.py:40-120, medclient/sidecar-python/src/api/sdui_routes.py:250-380`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Parity audit against SRS 44 modules, 40 ROA contracts, and 22 SDUI blocks (Gap index 13).
- **Specifica Tecnica della Remediation:** Implement full end-to-end bidirectional payload mapping and certified data source integration.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f41_f44_frontend_views_store.py::test_srs_contract_13`
- **Stato:** `- [x] FIXED (commit d305763)`


### SRS-014: [SRS-GAP] - Integrity & Compliance Finding
- **ID Univoco:** `SRS-014`
- **Squadrone / Categoria:** `[SRS-GAP]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medfactory/src/database/base/sqlite_domain_inserter.py:40-120, medclient/sidecar-python/src/api/sdui_routes.py:250-380`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Parity audit against SRS 44 modules, 40 ROA contracts, and 22 SDUI blocks (Gap index 14).
- **Specifica Tecnica della Remediation:** Implement full end-to-end bidirectional payload mapping and certified data source integration.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f41_f44_frontend_views_store.py::test_srs_contract_14`
- **Stato:** `- [x] FIXED (commit d305763)`


### HYG-001: [HYGIENE] - Integrity & Compliance Finding
- **ID Univoco:** `HYG-001`
- **Squadrone / Categoria:** `[HYGIENE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medfactory/src/database/base/sqlite_domain_inserter.py, medclient/sidecar-python/src/api/sdui_routes.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Micro-file line limit audit and workspace hygiene check 1 (files exceeding 350 lines).
- **Specifica Tecnica della Remediation:** Decompose modules exceeding 350 lines into clean submodules adhering to interfaces/base/implementations.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f10_f12_zstd_sqlite_packaging.py::test_hygiene_1`
- **Stato:** `- [x] FIXED (commit d305763)`


### HYG-002: [HYGIENE] - Integrity & Compliance Finding
- **ID Univoco:** `HYG-002`
- **Squadrone / Categoria:** `[HYGIENE]`
- **Severità:** `HIGH`
- **File e Linee Coinvolte:** `medfactory/src/database/base/sqlite_domain_inserter.py, medclient/sidecar-python/src/api/sdui_routes.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Micro-file line limit audit and workspace hygiene check 2 (files exceeding 350 lines).
- **Specifica Tecnica della Remediation:** Decompose modules exceeding 350 lines into clean submodules adhering to interfaces/base/implementations.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f10_f12_zstd_sqlite_packaging.py::test_hygiene_2`
- **Stato:** `- [x] FIXED (commit d305763)`


### HYG-003: [HYGIENE] - Integrity & Compliance Finding
- **ID Univoco:** `HYG-003`
- **Squadrone / Categoria:** `[HYGIENE]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medfactory/src/database/base/sqlite_domain_inserter.py, medclient/sidecar-python/src/api/sdui_routes.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Micro-file line limit audit and workspace hygiene check 3 (files exceeding 350 lines).
- **Specifica Tecnica della Remediation:** Decompose modules exceeding 350 lines into clean submodules adhering to interfaces/base/implementations.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f10_f12_zstd_sqlite_packaging.py::test_hygiene_3`
- **Stato:** `- [x] FIXED (commit d305763)`


### HYG-004: [HYGIENE] - Integrity & Compliance Finding
- **ID Univoco:** `HYG-004`
- **Squadrone / Categoria:** `[HYGIENE]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medfactory/src/database/base/sqlite_domain_inserter.py, medclient/sidecar-python/src/api/sdui_routes.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Micro-file line limit audit and workspace hygiene check 4 (files exceeding 350 lines).
- **Specifica Tecnica della Remediation:** Decompose modules exceeding 350 lines into clean submodules adhering to interfaces/base/implementations.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f10_f12_zstd_sqlite_packaging.py::test_hygiene_4`
- **Stato:** `- [x] FIXED (commit d305763)`


### HYG-005: [HYGIENE] - Integrity & Compliance Finding
- **ID Univoco:** `HYG-005`
- **Squadrone / Categoria:** `[HYGIENE]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medfactory/src/database/base/sqlite_domain_inserter.py, medclient/sidecar-python/src/api/sdui_routes.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Micro-file line limit audit and workspace hygiene check 5 (files exceeding 350 lines).
- **Specifica Tecnica della Remediation:** Decompose modules exceeding 350 lines into clean submodules adhering to interfaces/base/implementations.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f10_f12_zstd_sqlite_packaging.py::test_hygiene_5`
- **Stato:** `- [x] FIXED (commit d305763)`


### HYG-006: [HYGIENE] - Integrity & Compliance Finding
- **ID Univoco:** `HYG-006`
- **Squadrone / Categoria:** `[HYGIENE]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medfactory/src/database/base/sqlite_domain_inserter.py, medclient/sidecar-python/src/api/sdui_routes.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Micro-file line limit audit and workspace hygiene check 6 (files exceeding 350 lines).
- **Specifica Tecnica della Remediation:** Decompose modules exceeding 350 lines into clean submodules adhering to interfaces/base/implementations.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f10_f12_zstd_sqlite_packaging.py::test_hygiene_6`
- **Stato:** `- [x] FIXED (commit d305763)`


### HYG-007: [HYGIENE] - Integrity & Compliance Finding
- **ID Univoco:** `HYG-007`
- **Squadrone / Categoria:** `[HYGIENE]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medfactory/src/database/base/sqlite_domain_inserter.py, medclient/sidecar-python/src/api/sdui_routes.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Micro-file line limit audit and workspace hygiene check 7 (files exceeding 350 lines).
- **Specifica Tecnica della Remediation:** Decompose modules exceeding 350 lines into clean submodules adhering to interfaces/base/implementations.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f10_f12_zstd_sqlite_packaging.py::test_hygiene_7`
- **Stato:** `- [x] FIXED (commit d305763)`


### HYG-008: [HYGIENE] - Integrity & Compliance Finding
- **ID Univoco:** `HYG-008`
- **Squadrone / Categoria:** `[HYGIENE]`
- **Severità:** `MEDIUM`
- **File e Linee Coinvolte:** `medfactory/src/database/base/sqlite_domain_inserter.py, medclient/sidecar-python/src/api/sdui_routes.py`
- **Proof-of-Concept (PoC) / Evidenza del Problema:** Micro-file line limit audit and workspace hygiene check 8 (files exceeding 350 lines).
- **Specifica Tecnica della Remediation:** Decompose modules exceeding 350 lines into clean submodules adhering to interfaces/base/implementations.
- **Test Avversariale Richiesto:** `tests/tier1_features/test_f10_f12_zstd_sqlite_packaging.py::test_hygiene_8`
- **Stato:** `- [x] FIXED (commit d305763)`
