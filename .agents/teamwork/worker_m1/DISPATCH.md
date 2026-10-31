## 2026-10-30T22:06:36Z
You are `worker_m1` (Role: MedFactory Build Engineer).

Your working directory is:
`c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\worker_m1\`

You MUST read the original request before starting:
`c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\ORIGINAL_REQUEST.md`

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Scope & Write Ownership:
You own `medfactory/` exclusively. You must NOT edit any files in `medclient/` or `tests/`.

Key References to read:
1. `c:\Users\vence\Downloads\projects\ibrahim\PROJECT.md`
2. `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\AUDIT_AND_ASSUMPTIONS.md`
3. `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\explorer_audit_1\code_audit.md`
4. `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\spec_miner_1\spec_inventory.md`

Python Virtual Environment:
`c:\Users\vence\Downloads\projects\ibrahim\agent_env\Scripts\python.exe`
Pip installer:
`c:\Users\vence\Downloads\projects\ibrahim\agent_env\Scripts\pip.exe`

Your Objectives (Milestone M1 - Features 1–12):
1. Install any missing packages in `agent_env` as authorized by R4 (`fastapi`, `docling`, `pyhpo`, `polars`) with exact pinned versions.
2. Restructure and implement `medfactory/src/` to strictly comply with production dogmas:
   - Max 300-450 lines per file.
   - Strict 3-tier hierarchy: `interfaces/`, `base/`, `implementations/` in each package.
   - Pinned exact dependencies in `medfactory/pyproject.toml` and `requirements.txt`.
   - Zero-mock / zero-dummy: eliminate all 17 occurrences of `Field(...)`, eliminate dummy `compressed_bytes=1` and calculate real compressed size, eliminate in-memory `io.BytesIO()` TAR buffering and stream to disk, eliminate banned identifiers (`samples` -> `corpus_samples`, `temp_db_path` -> `staging_database_path`, `data` -> `binary_buffer`, `val` -> `cell_content`).
3. Fully implement Features 1 through 12:
   - Feature 1: Docling DLA pipeline.
   - Feature 2: Multi-column anti-cross-talk topological slicing.
   - Feature 3: Complex table normalizer (rowspan/colspan to GFM).
   - Feature 4: Medical unit scale guard (mcg <-> mg, dL <-> L).
   - Feature 5: Parent-child hierarchical chunker (800-1200 / 150-250 tokens).
   - Feature 6: Breadcrumb context injection `# {Discipline} > ...`.
   - Feature 7: PyHPO ontology ingestion (`hp.obo`, `phenotype.hpoa`) computing ancestor closure and Information Content (IC).
   - Feature 8: ICD-10-CM and WHO/AIFA ATC Level 5 classification ingestion.
   - Feature 9: Zstandard 112KB custom dictionary trainer (exactly 114,688 Bytes at Level 19).
   - Feature 10: Static Markdown synthesizer with typed callouts (`RED_FLAG`, `CONTRAINDICATION`, etc.).
   - Feature 11: SQLite KB builder (`module_kb.sqlite`) with saturated B-Tree, FTS5, and vector blobs.
   - Feature 12: `.medpack` packaging (`.tar.zst`) with `manifest.json`, dual BLAKE3 + SHA-256 hashes, and Ed25519 signature.
4. Execute tests and real sample document build to verify that a genuine `.medpack` archive is generated and passes verification.
5. Write your detailed report in `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\worker_m1\changes.md` and complete handoff report in `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\worker_m1\handoff.md`.
6. Send a message to your caller when finished. Remember you MUST use send_message.
