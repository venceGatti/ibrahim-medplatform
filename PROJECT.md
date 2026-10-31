# Project: MedPlatform (Hybrid Asymmetric Medical System)

## Architecture
MedPlatform is a hybrid asymmetric medical knowledge and diagnostic desktop platform:
1. **MedFactory (Build-Time / GPU)**:
   - High-fidelity Docling Document Layout Analysis (DLA) with anti-cross-talk topological sorting and table normalization.
   - Ontological integration: PyHPO (ancestor closure, information content scoring) + ICD-10 + ATC Level 5 classification.
   - Deterministic custom Zstandard dictionary compression (exactly 114,688 Bytes / 112 KB at Level 19).
   - Static Markdown Synthesis (SSG) with typed medical callouts.
   - Deterministic SQLite Knowledge Base builder (`module_kb.sqlite`) with saturated B-Tree and FTS5 indexes.
   - Digital packaging into immutable `.medpack` bundles (`.tar.zst`) with BLAKE3 + SHA-256 checksums and Ed25519 signature.
2. **MedClient (Run-Time / CPU-Only Desktop, RSS < 300MB, Query Latency < 50ms)**:
   - Host Engine: Tauri v2 in Rust with `tikv-jemallocator` (`dirty_decay_ms = 1000`) and Win32 Job Object supervisor (`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`).
   - Native Media Protocol: Custom `med-asset://` scheme streaming images directly to WebView2 via `memmap2` zero-copy with LRU cache.
   - IPC Security: Dynamic loopback port (`127.0.0.1:0`), UUIDv4 token delivered via stdin, `X-Tauri-IPC-Secret` header, Windows DPAPI for secrets.
   - Backend Sidecar (FastAPI on Python 3.13):
     - Single owner of SQLite connection pool (`PRAGMA journal_mode = WAL;`, `PRAGMA mmap_size = 256MB;`).
     - Blue/Green atomic database hot-swap via `active_db.json` pointer and Win32 `MoveFileExW(MOVEFILE_REPLACE_EXISTING)`.
     - Multi-stage Log-Odds Diagnostic Engine: Phase 0 Red Flags (Shock Index, qSOFA, NEWS2), Phase 1 Sparse CSR matrix ($M \approx 7000, N \approx 14000$) with Dirichlet smoothing, Phase 2 Pertinent Negatives with strict rule-out ($-\infty$), Phase 3 Log-Sum-Exp softmax normalization, Phase 4 Active Discrimination (Next-Best-Question / NBQ).
     - CYP450 Drug Safety Engine: Multi-way isoenzyme clearance with explicit active drug vs prodrug distinction (ROA-10), QTc prolongation score ($S_{QTc} \ge 6.0$), "Triple Whammy" acute kidney injury detector, CKD-EPI 2021 renal calculator, CPIC Level 1A pharmacogenomics.
     - NLP & Mnemonic Engine: SymSpell typo correction, inverted lexical dictionary, in-process ONNX INT8 (`all-MiniLM-L6-v2`) semantic search & NLI cross-encoder, FSRS v4/v5 spaced repetition scheduler.
     - Agentic API (`/agent/health`, `/agent/state`, `/agent/execute`, `/agent/schema`).
   - Frontend SDUI: React 19 + TypeScript + Vite + TailwindCSS in WebView2. Server-Driven UI rendering 4 fundamental blocks (`ClinicalSheetBlock`, `SymptomMatcherBlock`, `DrugSafetyBlock`, `ExamSimulatorBlock`) with dual registry aliasing, Zustand persistent state, virtual DOM windowing (<30 nodes), and Singleton WebGL Broker.

---

## Feature Inventory
| # | Category | Feature | Description | Milestone | Source |
|---|---|---|---|:---:|---|
| 1 | MedFactory | Docling DLA Pipeline | DLA extracting text, bounding boxes, tables from medical PDFs | M1 | SRS Modulo 1.2 / 3.1 |
| 2 | MedFactory | Multi-Column Anti-Cross-Talk | Topological slicing preventing multi-column text interleaving | M1 | SRS Modulo 1.2 / 3.1 |
| 3 | MedFactory | Complex Table Normalizer | Reconstructs merged headers/rowspan/colspan into GFM tables | M1 | SRS Modulo 1.2 / 3.1 |
| 4 | MedFactory | Medical Unit Scale Guard | Lexical sanitizer preventing OCR scale errors (mcg vs mg, dL vs L) | M1 | PDF Page 20 / SRS Modulo 1.2 |
| 5 | MedFactory | Parent-Child Chunking | Hierarchical chunking (800–1200 parent / 150–250 child tokens) | M1 | SRS Modulo 1.2 / 3.2 |
| 6 | MedFactory | Breadcrumb Context Injection | Prepends full taxonomy path `# {Discipline} > ...` to child chunks | M1 | SRS Modulo 1.2 / 3.2 |
| 7 | MedFactory | PyHPO Ontology Ingestion | Ingests HPO graphs, computes ancestor closure & Information Content | M1 | PDF Page 31 / Plan Task 1.1 |
| 8 | MedFactory | ICD-10 & ATC Ingestion | Ingests WHO ICD-10-CM and AIFA/WHO ATC Level 5 classification | M1 | SRS Modulo 1.1 / PDF Page 28 |
| 9 | MedFactory | Zstandard 112KB Dict Trainer | Trains 114,688-byte custom dictionary on 10% stratified corpus (L19) | M1 | SRS Modulo 1.2 / 1.3 |
| 10 | MedFactory | Static Markdown Synthesizer | Compiles encyclopedic monographs with typed severity callouts | M1 | SRS Modulo 2.2 / PDF Page 54 |
| 11 | MedFactory | SQLite KB Builder | Compiles `module_kb.sqlite` with saturated B-Tree & FTS5 indexes | M1 | SRS Modulo 1.2 / 3.4 |
| 12 | MedFactory | `.medpack` Assembler | Bundles `.tar.zst` with manifest, 114,688B dict, DB, media, and Ed25519 sig | M1 | SRS Modulo 1.2 / Plan Task 1.6 |
| 13 | MedClient | Tauri v2 Host Process | Rust desktop host managing application lifecycle and native hooks | M2 | SRS Modulo 2.1 / Plan Task 2.1 |
| 14 | MedClient | Jemalloc Memory Tuner | Configures `tikv-jemallocator` (`dirty_decay_ms = 1000`) for RSS < 25MB | M2 | SRS Modulo 1.1 / 2.1 |
| 15 | MedClient | Win32 Job Object Supervisor | Binds child processes to Job Object with kill-on-close policy | M2 | SRS Modulo 2.2 / Plan Task 2.2 |
| 16 | MedClient | Reverse Watchdog Thread | Python thread invoking `kernel32.WaitForSingleObject` on parent PID | M3 | SRS Modulo 2.2 / Plan Task 3.7 |
| 17 | MedClient | Throttling State Machine | Monitors RSS thresholds (`Normal`, `Constrained`, `Critical`) | M2 | SRS Modulo 1.1 / 5.1 |
| 18 | MedClient | Ephemeral IPC Handshake | Binds `127.0.0.1:0` and delivers UUIDv4 token via stdin without TOCTOU | M2 | SRS Modulo 1.3 / Plan Task 2.3 |
| 19 | MedClient | Custom `med-asset://` Protocol | Tauri protocol streaming WebP directly to WebView2 via `memmap2` zero-copy | M2 | SRS Modulo 1.3 / Plan Task 2.4 |
| 20 | MedClient | SQLite WAL Read-Only Pool | High-concurrency connection pool with 256MB mmap and cache -16384 | M3 | SRS Modulo 1.4 / Plan Task 3.3 |
| 21 | MedClient | SQLite Blue/Green Hot Swap | Atomic pointer swap via `active_db.json` and Win32 `MoveFileExW` | M3 | SRS Modulo 1.4 / PDF Page 40 |
| 22 | MedClient | SymSpell Medical Spellchecker | Typo-tolerant candidate matcher ($d \le 2$) over 285k medical lemmata | M3 | SRS Modulo 2.1 / Plan Task 3.4 |
| 23 | MedClient | Inverted Lexical Dictionary | Fast lexical mapping of colloquial terms to HPO/ICD-10 nodes | M3 | SRS Modulo 2.1 / Plan Task 3.4 |
| 24 | MedClient | ONNX INT8 Semantic Embedding | In-process vector embedding generation via quantized `all-MiniLM-L6-v2` | M3 | SRS Modulo 2.1 / Plan Task 3.4 |
| 25 | MedClient | Red Flags Interceptor | Evaluates Shock Index, qSOFA, and NEWS2 thresholds immediately | M3 | SRS Modulo 3.1 / Plan Task 3.5 |
| 26 | MedClient | Sparse CSR Log-Odds Matcher | Computes probabilistic disease ranking using in-memory CSR matrices | M3 | SRS Modulo 3.1 / Plan Task 3.5 |
| 27 | MedClient | Pertinent Negatives Rule-Out | Severe penalty detraction with strict rule-out ($-\infty$) for refutations | M3 | SRS Modulo 3.1 / Plan Task 3.5 |
| 28 | MedClient | Log-Sum-Exp Softmax Normalizer | Numerically stable probability normalizer preventing floating-point overflow | M3 | SRS Modulo 3.1 / Plan Task 3.5 |
| 29 | MedClient | Active Discrimination (NBQ) | Next-Best-Question selector maximizing information gain per cost | M3 | SRS Modulo 3.1 / Plan Task 3.5 |
| 30 | MedClient | CYP450 Functional Load Engine | Multi-way drug interaction engine with active drug vs prodrug logic | M3 | SRS Modulo 3.2 / Plan Task 3.6 |
| 31 | MedClient | QTc Prolongation Guard | Cumulative cardiac arrhythmia risk score ($S_{QTc} \ge 6.0 \implies$ Level 1) | M3 | SRS Modulo 3.2 / Plan Task 3.6 |
| 32 | MedClient | "Triple Whammy" Detector | Deterministic detector for RAS blocker + Diuretic + NSAID (eGFR < 60) | M3 | SRS Modulo 3.2 / Plan Task 3.6 |
| 33 | MedClient | CKD-EPI 2021 Renal Calculator | eGFR calculation without race coefficient for renal dose adjustment | M3 | SRS Modulo 3.2 / Plan Task 3.6 |
| 34 | MedClient | Pharmacogenomics Rule Engine | CPIC Level 1A actionable guideline matcher (HLA-B*57:01, CYP2C19, TPMT) | M3 | SRS Modulo 3.2 / Plan Task 3.6 |
| 35 | MedClient | MCQ Assessment Engine | Renders and evaluates 4-choice clinical questions with KaTeX support | M4 | SRS Modulo 4.1 / Plan Task 4.3 |
| 36 | MedClient | Image Hotspot Diagnostics | Spatial ray-casting algorithm (Even-Odd rule) on polygonal coordinates | M4 | SRS Modulo 4.1 / Plan Task 4.3 |
| 37 | MedClient | NLI Cross-Encoder Evaluator | Evaluates free-text clinical responses with ONNX INT8 DeBERTa/MiniLM | M3 | SRS Modulo 4.1 / Plan Task 4.3 |
| 38 | MedClient | Stateful DAG Scenario Engine | Directed acyclic graph tracking patient vitals, actions, and terminal score | M3 | SRS Modulo 4.1 / Plan Task 4.3 |
| 39 | MedClient | FSRS v4/v5 Mnemonic Scheduler | Spaced repetition scheduler calculating stability $S$, difficulty $D$, $R=0.9$ | M3 | SRS Modulo 4.2 / Plan Task 4.4 |
| 40 | MedClient | Review Load Balancer | Mitigates "Review Hell" via load balancing and exam-date prioritization | M3 | SRS Modulo 4.2 / Plan Task 4.4 |
| 41 | MedClient | React 19 Frontend Shell | Desktop SPA in WebView2 with Vite, TypeScript, and TailwindCSS | M4 | SRS Modulo 4.3 / Plan Task 4.1 |
| 42 | MedClient | Zustand Persistent Store | Persistent UI store maintaining DOM, tab, and input state across views | M4 | SRS Modulo 4.3 / Plan Task 4.2 |
| 43 | MedClient | `ClinicalSheetBlock` Component | Static monograph renderer with severity-coded callouts | M4 | SRS Modulo 4.3 / Plan Task 4.3 |
| 44 | MedClient | `SymptomMatcherBlock` Component | Differential ranking, radar charts, and interactive symptom nodes | M4 | SRS Modulo 4.3 / Plan Task 4.3 |
| 45 | MedClient | `DrugSafetyBlock` Component | 4-level interaction matrices, CYP450 dial gauges, clearance indicators | M4 | SRS Modulo 4.3 / Plan Task 4.3 |
| 46 | MedClient | `ExamSimulatorBlock` Component | MCQ renderer, SVG hotspot canvas, DAG scenario stepper | M4 | SRS Modulo 4.3 / Plan Task 4.3 |
| 47 | MedClient | Virtual DOM Windowing | Virtualized list limiting mounted DOM nodes to <30 elements (<100MB RAM) | M4 | SRS Modulo 4.3 / Plan Task 4.3 |
| 48 | MedClient | Singleton WebGL Broker | Singleton 3D WebGL context manager preventing `webglcontextlost` | M4 | SRS Modulo 4.3 / Plan Task 4.3 |

---

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | MedFactory Build Pipeline & .medpack Generator | Docling DLA, PyHPO, 114,688B Zstd dict, SQLite KB builder, static MD, .medpack packaging (Features 1–12) | none | DONE |
| M2 | MedClient Core Rust Engine & Zero-Copy IPC | Fix Rust compilation, Win32 Job Object, true zero-copy `med-asset://`, ephemeral port handshake, Windows DPAPI (Features 13–15, 17–19) | none | DONE |
| M3 | MedClient Backend Sidecar & Core Engines | FastAPI sidecar, Agentic API, SQLite WAL Blue/Green swap, Log-Odds + Rule-Out, CYP450 with prodrugs, ONNX INT8 NLI, FSRS (Features 16, 20–34, 37–40) | M1, M2 | IN_PROGRESS |
| M4 | MedClient SDUI Frontend & Tauri Desktop Integration | React SDUI 4-block schema with dual aliasing, Zustand persistent store, virtual windowing, Singleton WebGL broker, end-to-end client wiring (Features 35, 36, 41–48) | M2, M3 | PLANNED |
| M5 | Final Integration, 100% E2E Pass & Adversarial Hardening | End-to-end system verification, passing 100% E2E test suite (Tiers 1–4), performance validation (<300MB RSS, <50ms query), and Tier 5 adversarial coverage hardening | M1, M2, M3, M4, TEST_READY | PLANNED |
| E2E | E2E Testing Track (Parallel) | Requirement-driven opaque-box test infrastructure and Tiers 1–4 test suite generation deriving from ORIGINAL_REQUEST | none | DONE |

---

## Interface Contracts

### MedFactory $\leftrightarrow$ MedClient (`.medpack` Archive Contract)
- **Container Format**: POSIX `.tar` compressed with Zstandard (`.tar.zst`) using 114,688-byte custom dictionary.
- **Manifest (`manifest.json`)**:
  ```json
  {
    "pack_version": "1.0.0",
    "module_id": "STRING_UPPER",
    "dla_engine_version": "1.0.0",
    "checksums_blake3": { "relative_path": "hex_hash" },
    "checksums_sha256": { "relative_path": "hex_hash" },
    "signature_ed25519": "hex_signature"
  }
  ```
- **Files inside archive**: `manifest.json`, `zstd.dict` (114,688B), `database/module_kb.sqlite`, `media/<uuid>.webp`, `assets/schede_statiche/<id>.md`.

### MedClient Core Rust $\leftrightarrow$ FastAPI Sidecar (IPC Contract)
- **Transport**: HTTP REST / SSE bound strictly to `127.0.0.1:<ephemeral_port>`.
- **Authentication**: Header `X-Tauri-IPC-Secret: <uuidv4_token>` passed to Python via line 1 of stdin.
- **Reverse Watchdog**: Python background thread calls `kernel32.WaitForSingleObject` on parent PID handle; calls `os._exit(0)` within 500ms of parent termination.
- **Agentic API Endpoints**:
  - `GET /agent/health`: returns `{"status": "healthy", "rss_mb": float, "db_active": str}`.
  - `GET /agent/state`: returns full serialized application state.
  - `POST /agent/execute`: executes typed action `{"action_type": str, "payload": dict}`.
  - `GET /agent/schema`: returns OpenAPI/JSON Schema of all agent actions.

### MedClient Sidecar $\leftrightarrow$ React Frontend (SDUI 4-Block Contract)
- **Response Format**: Validated JSON payload containing an array of polymorphic blocks:
  1. `ClinicalSheetBlock`: `{"block_type": "ClinicalSheetBlock", "sheet_id": str, "title": str, "content_markdown": str, "callouts": list}` (aliased to `MarkdownBlock`).
  2. `SymptomMatcherBlock`: `{"block_type": "SymptomMatcherBlock", "differential_candidates": list, "selected_symptoms": list, "nbq": dict}` (aliased to `DifferentialDiagnosisBlock`).
  3. `DrugSafetyBlock`: `{"block_type": "DrugSafetyBlock", "interactions": list, "cyp_clearance": dict, "alerts": list, "egfr": float}`.
  4. `ExamSimulatorBlock`: `{"block_type": "ExamSimulatorBlock", "item_type": str, "item_data": dict, "fsrs_card_state": dict}` (aliased to `ClinicalExamBlock` / `InteractiveFlowchartBlock`).

---

## Code Layout
Strict adherence to the 300-450 line limit per file and modular hierarchy:
```
c:\Users\vence\Downloads\projects\ibrahim\
├── medfactory\
│   ├── pyproject.toml              # Pinned build-time dependencies
│   └── src\
│       ├── dla\                    # Document Layout Analysis (Docling)
│       │   ├── interfaces\
│       │   ├── base\
│       │   └── implementations\
│       ├── ontologies\             # PyHPO, ICD-10, ATC Ingestion
│       │   ├── interfaces\
│       │   ├── base\
│       │   └── implementations\
│       ├── compression\            # Zstd 114,688B dict & SSG Markdown
│       │   ├── interfaces\
│       │   ├── base\
│       │   └── implementations\
│       ├── database\               # SQLite module_kb.sqlite compiler
│       │   ├── interfaces\
│       │   ├── base\
│       │   └── implementations\
│       └── packager\               # .medpack packaging & Ed25519 signing
│           ├── interfaces\
│           ├── base\
│           └── implementations\
├── medclient\
│   ├── core-rust\                  # Tauri v2 Desktop Host & Supervision
│   │   ├── Cargo.toml              # Pinned Rust dependencies (=x.y.z)
│   │   └── src\
│   │       ├── interfaces\
│   │       ├── base\
│   │       ├── supervisor\         # Win32 Job Objects & Jemalloc
│   │       ├── protocols\          # med-asset:// zero-copy mmap streaming
│   │       ├── sidecar\            # Process spawning & stdin secret delivery
│   │       └── security\           # Windows DPAPI implementation
│   ├── sidecar-python\             # FastAPI ASGI Backend & Engines
│   │   ├── requirements.txt        # Pinned runtime dependencies
│   │   └── src\
│   │       ├── interfaces\
│   │       ├── base\
│   │       ├── api\                # FastAPI routes & Agentic API (/agent/*)
│   │       ├── database\           # SQLite WAL pool & Blue/Green swap
│   │       ├── diagnostic\         # Log-Odds & Rule-Out CSR Engine
│   │       ├── pharmacology\       # CYP450 (prodrug-aware) & Toxicity
│   │       └── educational\        # ONNX INT8 NLI & FSRS Scheduler
│   └── frontend-react\             # React 19 + TypeScript + Tailwind SDUI
│       ├── package.json            # Pinned frontend dependencies
│       └── src\
│           ├── interfaces\
│           ├── base\
│           ├── sdui\               # 4-block component registry & aliasing
│           ├── store\              # Zustand persistent state
│           └── webgl\              # Singleton WebGL Broker
└── tests\                          # E2E & Adversarial Testing Track
    ├── e2e_runner.py               # Opaque-box test runner
    ├── tier1_features\
    ├── tier2_boundaries\
    ├── tier3_pairwise\
    ├── tier4_workloads\
    └── tier5_adversarial\
```
