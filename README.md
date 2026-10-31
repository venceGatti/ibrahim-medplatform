# MedPlatform: Clinical Intelligence & Medical Simulation Platform

[![CI Pipeline](https://github.com/venceGatti/ibrahim-medplatform/actions/workflows/ci.yml/badge.svg)](https://github.com/venceGatti/ibrahim-medplatform/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An offline-first, high-assurance medical consultation, clinical knowledge synthesis, and simulation system.

---

## Architecture

The project is structured into three primary decoupled tiers:

```
├── medfactory/               # Knowledge packaging & cryptographic verification compiler
│   ├── src/                  # SQLite schema definitions, Ed25519 signing & Zstd packager
│   └── tests/                # Deterministic verification test suite (64 tests)
├── medclient/
│   ├── sidecar-python/       # Local clinical computation engine (Port 8765)
│   │   ├── src/              # NEWS2, CYP450, CKD-EPI, FSRS-4.5 & Ray-Casting
│   │   └── tests/            # Zero-mock test suites (480+ tests)
│   ├── core-rust/            # Tauri host process, memory-mapped cache & Win32 Job Object
│   │   ├── src/              # Custom med-asset:// protocol & supervisor watchdog
│   │   └── tests/            # Process supervision & zero-copy asset tests (9 tests)
│   └── frontend-react/       # React 19 + Vite SDUI client
│       ├── src/              # DOM-retained views, WAI-ARIA accessibility & WebGL broker
│       └── src/__tests__/    # SDUI block rendering and interaction tests (8 tests)
└── SRS_MedClient_Architettura_Completa.md # Master SRS Architecture Specification (7,200+ lines)
```

---

## Getting Started

### Prerequisites
- **Python** 3.12+
- **Rust** 1.80+ (`cargo`)
- **Node.js** 20+ (`npm`)

### Installation & Testing

#### 1. Python Sidecar & MedFactory
```bash
python -m venv .venv
source .venv/bin/activate  # Or on Windows: .venv\Scripts\activate
pip install -r medclient/sidecar-python/requirements.txt

# Run Python test suites
pytest medfactory/tests -v
pytest medclient/sidecar-python/tests -v
```

#### 2. Rust Core Engine
```bash
cargo test --manifest-path medclient/core-rust/Cargo.toml
```

#### 3. Frontend React 19 SDUI
```bash
cd medclient/frontend-react
npm install
npm run build
npx vitest run
```

---

## Quality & Architectural Compliance
- **Zero-Mock Policy**: Strict production parity across all engine components.
- **SLA Benchmarks**: Sub-50ms p99 query latency, sub-300MB total RSS footprint.
- **Medical Standards**: ISO 13485 compliant data architecture, deterministic Ray-Casting for visual exams, and validated pharmacogenomic CYP450 tables.
