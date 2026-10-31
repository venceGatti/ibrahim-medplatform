# Google Labs Jules Instructions for MedPlatform

This repository contains the production code for the MedPlatform offline clinical workstation.

## Repository Setup
- **Python**: Version 3.12+ (dependencies in `medfactory/pyproject.toml` and `medclient/sidecar-python/requirements.txt`).
- **Rust**: Stable edition 2021 (`medclient/core-rust`).
- **Node.js**: Node 20+, React 19 (`medclient/frontend-react`).

## Workflow Directives
1. Never commit stubs, mock data, or incomplete placeholders. All implementations must be functional, strongly typed, and thoroughly tested.
2. Ensure all newly added or modified files adhere to modular architecture ($\le 350$ lines per file).
3. If modifying React SDUI blocks, ensure 100% passing tests via `npm run build` and `npx vitest run`.
4. If modifying Python sidecar scoring or drug interaction engines, verify parity with the formal specifications in `SRS_MedClient_Architettura_Completa.md`.
