# AGENTS.md - MedPlatform Autonomous Agent Directives

Welcome to **MedPlatform** (`ibrahim-medplatform`). This document provides formal directives and instructions for autonomous AI agents (including Google Labs Jules, Antigravity, and CI agents) operating on this repository.

## 1. System Architecture Overview

MedPlatform is an offline-first, high-performance medical consultation and clinical simulation platform:
- **`medfactory/`**: Knowledge base compiler and packager. Generates signed, encrypted SQLite packages (`.medpack`) with Zstandard compression and Ed25519 cryptographic signatures.
- **`medclient/sidecar-python/`**: Local Python sidecar runtime running on `127.0.0.1:8765`. Provides clinical scoring (NEWS2, Shock Index), drug safety (CYP450, CKD-EPI eGFR, Blackbox warnings), HPO symptom matching, and FSRS-4.5 spaced repetition.
- **`medclient/core-rust/`**: High-performance Tauri host engine. Manages sidecar processes via Win32 Job Objects, serves custom asset protocol `med-asset://` with zero-copy memory mapping (`memmap2`), and enforces strict memory ceilings (< 300 MB).
- **`medclient/frontend-react/`**: React 19 + TypeScript SDUI client. Features DOM retention across navigation tabs, clinical high-contrast themes, WAI-ARIA 1.2 accessibility, and a WebGL Singleton Broker.

## 2. Strict Architectural Constraints

All modifications MUST adhere to these non-negotiable rules:
1. **Zero-Mock Policy**: Absolutely NO synthetic placeholder returns (`return null`, `return {}`, empty stubs), no mock frameworks in production flows, and no bypassing exceptions.
2. **Micro-File Modularization**: Keep source code files under 300–400 lines. Structure modules into `interfaces/`, `base/`, and `implementations/`.
3. **Strict Domain Semantics**: Avoid generic identifiers (`data`, `obj`, `item`, `val`, `res`). Use explicit domain-specific naming (`clinicalSafetyAlert`, `symptomEntity`, `patientBiomarker`).
4. **Offline Resilience**: All clinical algorithms and validation routines MUST execute 100% locally without external cloud dependencies.

## 3. Standard Verification Commands

Before submitting any Pull Request or committing changes, execute the corresponding test suites:

### Python (MedFactory & Sidecar)
```bash
# Run MedFactory verification
pytest medfactory/tests -v

# Run Python Sidecar verification
pytest medclient/sidecar-python/tests -v

# Run Master E2E integration runner
python tests/master_e2e_runner.py
```

### Rust (Core Host Engine)
```bash
cargo test --manifest-path medclient/core-rust/Cargo.toml
```

### React (Frontend SDUI)
```bash
cd medclient/frontend-react
npm run build
npx vitest run
```
