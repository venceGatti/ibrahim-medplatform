## 2026-10-30T22:38:44Z
You are `worker_m3` (Role: MedClient Backend Sidecar Engineer).

Your working directory is:
`c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\worker_m3\`

You MUST read the original request before starting:
`c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\ORIGINAL_REQUEST.md`

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Scope & Write Ownership:
You own `medclient/sidecar-python/` exclusively. You must NOT edit files in `medfactory/`, `medclient/core-rust/`, or `tests/`.

Key References to read:
1. `c:\Users\vence\Downloads\projects\ibrahim\PROJECT.md`
2. `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\AUDIT_AND_ASSUMPTIONS.md` (ROA-01 to ROA-12)
3. `c:\Users\vence\Downloads\projects\ibrahim\TEST_INFRA.md` and `c:\Users\vence\Downloads\projects\ibrahim\TEST_READY.md`
4. `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\spec_miner_1\spec_inventory.md`

Python Virtual Environment:
`c:\Users\vence\Downloads\projects\ibrahim\agent_env\Scripts\python.exe`
Pip installer:
`c:\Users\vence\Downloads\projects\ibrahim\agent_env\Scripts\pip.exe`

Your Objectives (Milestone M3 - Features 16, 20–34, 37–40):
1. Create `medclient/sidecar-python/` structured in strict 3-tier hierarchy: `interfaces/`, `base/`, and `implementations/` with strict max 300-450 line limit per file.
2. Create `medclient/sidecar-python/requirements.txt` with exact pinned versions.
3. Fully implement Features 16, 20–34, 37–40 with 100% genuine logic:
   - Feature 16: Reverse watchdog thread (`kernel32.WaitForSingleObject` on parent PID) calling `os._exit(0)` on parent termination.
   - Feature 20: SQLite WAL read-only connection pool (`PRAGMA journal_mode = WAL;`, `mmap_size = 256MB;`, `cache_size = -16384;`).
   - Feature 21: Blue/Green atomic hot swap via `active_db.json` pointer and Win32 `MoveFileExW(MOVEFILE_REPLACE_EXISTING)` without connection locking.
   - Feature 22: SymSpell medical spellchecker ($d \le 2$) over medical lemmata.
   - Feature 23: Inverted lexical dictionary for colloquial terms to HPO/ICD-10 mapping.
   - Feature 24: ONNX INT8 semantic embedding generator (`all-MiniLM-L6-v2`) and cosine similarity over SQLite BLOBs.
   - Feature 25: Red Flags Interceptor evaluating Shock Index ($\ge 1.0$), qSOFA ($\ge 2$), and NEWS2 ($\ge 7$).
   - Feature 26: Sparse CSR Log-Odds disease ranker ($M \approx 7000, N \approx 14000$) with Dirichlet smoothing and pathognomonic multiplier.
   - Feature 27: Pertinent Negatives rule-out with strict $-\infty$ penalty for refutations.
   - Feature 28: Numerically stable Log-Sum-Exp softmax normalization.
   - Feature 29: Active Discrimination (Next-Best-Question / NBQ) maximizing information gain per cost.
   - Feature 30: CYP450 functional load engine (3A4, 2D6, 2C9, 2C19, 1A2) with strict prodrug distinction (ROA-10): inihibitor on prodrug (`is_prodrug = 1`, e.g. Clopidogrel on CYP2C19, Codeine on CYP2D6) $\implies$ Blackbox Warning Level 1 for lethal therapeutic failure.
   - Feature 31: QTc prolongation score ($S_{QTc} \ge 6.0 \implies$ Level 1).
   - Feature 32: "Triple Whammy" acute kidney injury detector (RAS blocker + Diuretic + NSAID when eGFR < 60 $\implies$ Level 1).
   - Feature 33: Race-free CKD-EPI 2021 renal calculator.
   - Feature 34: CPIC Level 1A pharmacogenomics rule engine (HLA-B*57:01, CYP2C19, TPMT/NUDT15).
   - Feature 37: NLI Cross-Encoder evaluator with ONNX INT8 DeBERTa/MiniLM for concept entailment vs contradiction.
   - Feature 38: Stateful DAG clinical scenario stepper tracking dynamic vitals, therapeutic choices, and scoring.
   - Feature 39: FSRS v4/v5 spaced repetition scheduler ($S, D, R=0.9$, review intervals).
   - Feature 40: Review load balancer mitigating Review Hell with exam-date prioritization.
   - Agentic API endpoints (`/agent/health`, `/agent/state`, `/agent/execute`, `/agent/schema`) bound to `127.0.0.1` and protected by `X-Tauri-IPC-Secret`.
   - SDUI serialization emitting the 4 polymorphic blocks (`ClinicalSheetBlock`, `SymptomMatcherBlock`, `DrugSafetyBlock`, `ExamSimulatorBlock`).
4. Execute tests and verify clean pass with pytest in `agent_env`.
5. Write `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\worker_m3\changes.md` and `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\worker_m3\handoff.md`.
6. Send a message to your caller when finished. Remember you MUST use send_message.

## 2026-10-30T22:42:12Z
**Context**: Mandatory Integrity Constraint Reminder
**Content**: Reminder: In accordance with `ORIGINAL_REQUEST.md` and user integrity rules: "The team must NOT: read test source code to understand expected behaviour before implementing". 
You must derive all implementations, schemas, algorithms, and interfaces strictly from `PROJECT.md`, `AUDIT_AND_ASSUMPTIONS.md`, `SRS_MedClient_Architettura_Completa.md` (lines 1255+), and `spec_inventory.md`. 
Do NOT inspect test source files in `tests/`. Your implementation must be genuine and specification-driven.
**Action**: Update your checklist and ensure compliance.
