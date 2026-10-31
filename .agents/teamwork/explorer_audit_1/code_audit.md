# MedPlatform Codebase & Error Hunting Audit Report

**Auditor:** `explorer_audit_1` (Role: Codebase & Error Hunter)  
**Date:** 2026-10-30  
**Target:** MedPlatform Hybrid Medical Platform (`c:\Users\vence\Downloads\projects\ibrahim`)  
**Reference Documents:**
- `SRS_MedClient_Architettura_Completa.md`
- `Pianificazione App Medica Ibrida.pdf`
- `piano_costruzione_autonoma_medplatform.md`
- `ORIGINAL_REQUEST.md` (and Parent Priority Directives)

---

## 1. Executive Summary

A comprehensive, zero-assumption audit was conducted on the entire production codebase and project configuration of MedPlatform. Regardless of any label mentioning "Integrity mode: demo", the audit applied **100% production rigor** as mandated by the global dogmas and parent priority directives: zero-mock, zero-stub, zero-dummy, zero silent fallbacks, strict dependency pinning, memory bounds (<300MB RSS), latency bounds (<50ms), 300-450 line file limits in `interfaces/`, `base/`, `implementations/`, Windows DPAPI secret protection, and Agentic API compliance.

### High-Level Verdict:
1. **MedClient Core Rust is Broken**: `cargo check` fails with fatal type mismatch errors (`*mut c_void` vs `usize` in `src/supervisor.rs`). Tauri is completely absent from `Cargo.toml` and code. The custom protocol `med-asset://` violates zero-copy requirements by performing an explicit heap copy (`mmap[..].to_vec()`).
2. **MedClient Sidecar Python is 0% Implemented**: The entire directory `medclient/sidecar-python/` is non-existent. No FastAPI app, no Log-Odds diagnostic engine, no CYP450 multi-way pharmacological matrix, no SymSpell/ONNX pipeline, and no FSRS scheduler exist.
3. **MedClient Frontend React is 0% Implemented**: The entire directory `medclient/frontend-react/` is non-existent. No Vite project, no Zustand store, and none of the 4 SDUI blocks exist.
4. **MedFactory is Incomplete and Stub-like**: The modules present in `medfactory/src/` are isolated primitives:
   - No Docling DLA integration (layout analyzer is a toy heuristic on synthetic bounding boxes).
   - `medfactory/src/ontologies/` is an empty directory (zero code for ICD-10, ATC, HPO / PyHPO).
   - Packager manifest contains a hardcoded placeholder (`compressed_bytes=1, # Calcolato dopo`).
   - SQLite builder enforces rigid check constraints that crash on short text sections.
   - Archive creation buffers entire TAR archives in memory (`io.BytesIO()`), creating massive OOM risks.
5. **Universal Rule Violations**:
   - **Zero Modular Separation**: Neither MedFactory nor MedClient adheres to the required `interfaces/`, `base/`, `implementations/` directory layout.
   - **Forbidden Patterns**: Multiple violations of banned identifiers (`samples`, `temp_db_path`, `payload`, `res`, `data`, `val`), 17 occurrences of Ellipsis (`...`) in Pydantic `Field(...)`, and sentinels/dummies.
   - **Agentic API**: 0% implemented (`/agent/health`, `/agent/state`, `/agent/execute`, `/agent/schema` do not exist).
   - **Security**: No Windows DPAPI encryption is implemented.
   - **Dependency Pinning**: `Cargo.toml` uses floating semver ranges (`"0.9.5"` instead of `"=0.9.5"`). Missing `pyproject.toml` and `package.json`. Key packages (`fastapi`, `docling`, `pyhpo`, `polars`) are not installed in `agent_env`.

---

## 2. Compilation Errors, Syntax & Compiler Warnings

### 2.1 MedClient Core Rust Compilation Failure (`cargo check`)
The Rust crate `medclient/core-rust` fails compilation under `rustc 1.95.0` / MSVC toolchain:

```text
error[E0308]: mismatched types
  --> src\supervisor.rs:20:23
   |
20 |             if job == 0 || job == INVALID_HANDLE_VALUE {
   |                ---    ^ expected `*mut c_void`, found `usize`
   = note: expected raw pointer `*mut c_void`
                     found type `usize`

error[E0308]: mismatched types
  --> src\supervisor.rs:68:35
   |
68 |             if self.job_handle != 0 && self.job_handle != INVALID_HANDLE_VALUE {
   |                ---------------    ^ expected `*mut c_void`, found `usize`
   = note: expected raw pointer `*mut c_void`
                     found type `usize`
```

**Root Cause**: In `windows-sys = "0.59.0"`, `HANDLE` is defined as `*mut core::ffi::c_void`. The author wrote integer comparisons `job == 0` and `self.job_handle != 0`.  
**Remediation**: Use `std::ptr::null_mut()` for null pointer checks:
```rust
if job.is_null() || job == INVALID_HANDLE_VALUE as HANDLE { ... }
```

### 2.2 Compiler Warnings (Zero-Warning Policy Violation)
User rules state: *"Pulizia dei Warning di Compilazione: Nessun codice deve essere rilasciato con warning di compilazione TypeScript (tsc), Rust (cargo clippy) o Python (flake8, bandit)."*
Currently emitted:
1. `warning: unused import: Path` in `medclient/core-rust/src/protocols/asset_protocol.rs:1:17`
2. `warning: unused variable: job_supervisor` in `medclient/core-rust/src/main.rs:14:9`

---

## 3. Runtime Bugs & Critical Architectural Flaws

### 3.1 Violation of Zero-Copy Memory-Mapped Protocol
**File**: `medclient/core-rust/src/protocols/asset_protocol.rs:52`  
```rust
    Ok(AssetResponse {
        status_code: 200,
        content_type: "image/webp",
        body: mmap[..].to_vec(),
    })
```
- **Flaw**: `mmap[..].to_vec()` copies the entire memory-mapped file into a newly allocated `Vec<u8>` on the heap for every single asset request. This completely defeats the purpose of memory-mapped zero-copy I/O.
- **SRS Requirement**: The raw OS memory-mapped buffer must be streamed directly via `tauri::http::ResponseBuilder` without heap reallocation.
- **Flaw**: Hardcoded extension: `config.base_path.join(format!("{}.webp", hash))`. If medical assets are PNG, JPEG, SVG, or DICOM derivatives, lookup returns 404.

### 3.2 TOCTOU Race Condition in Port Allocation
**File**: `medclient/core-rust/src/sidecar.rs:13-18`  
```rust
    let listener = TcpListener::bind("127.0.0.1:0")?;
    let ephemeral_port = listener.local_addr()?.port();
    drop(listener);
```
- **Flaw**: Dropping the socket listener before the child sidecar binds introduces a Time-Of-Check to Time-Of-Use (TOCTOU) race condition. Another background task or application on the host can claim the ephemeral port before Python launches.
- **SRS Requirement**: The Rust supervisor should pass an inherited socket handle or use a strict retry loop with dynamic binding and port confirmation.

### 3.3 Missing Child Process Management & Win32 Job Attachment
**File**: `medclient/core-rust/src/main.rs` & `src/sidecar.rs`  
- **Flaw**: `allocate_ephemeral_port_and_token()` only constructs a byte buffer. There is zero code to spawn the Python process (`std::process::Command`), pass the token via stdin, or call `assign_process()` on `Win32JobSupervisor`. The sidecar process is never started.

### 3.4 In-Memory Archive Buffering & Out-Of-Memory (OOM) Vulnerability
**File**: `medfactory/src/packager/medpack_assembler.py:101-128`  
```python
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode="w", format=tarfile.PAX_FORMAT) as tar:
        ...
    uncompressed_tar_bytes = tar_buffer.getvalue()
    compressed_tar_zst = compressor.compress(uncompressed_tar_bytes)
```
- **Flaw**: The packager reads every file (including large SQLite databases and media binary blobs) into a single in-memory `io.BytesIO()` buffer, and then calls `compressor.compress(...)` in one shot. For multi-hundred megabyte medical packs, this causes violent memory spikes, violating the deterministic stream compression architecture.

### 3.5 Fragile SQLite Table Constraints
**File**: `medfactory/src/database/sqlite_builder.py:41, 55`  
```sql
CHECK (token_count >= 800 AND token_count <= 1200)
...
CHECK (token_count >= 150 AND token_count <= 250)
```
- **Flaw**: Real medical documents frequently have concluding sections, chapter intros, or remainder chunks shorter than 800 or 150 tokens. Any insertion with token counts outside these hard intervals throws an unhandled `sqlite3.IntegrityError: CHECK constraint failed`.

### 3.6 Incomplete SQLite Schema in MedFactory
**File**: `medfactory/src/database/sqlite_builder.py`  
- **Flaw**: `DDL_SCHEMA` only defines tables for bibliographic sources, parent chunks, and child chunks. It is completely missing tables for:
  - HPO terms and ontology graph edges
  - ICD-10 diagnostic classifications and symptom log-odds priors
  - Drug ATC classifications, CYP450 interaction matrices, and Blackbox warnings
  - Media vault index and static Markdown registry

---

## 4. Architectural Layout & Modular Decomposition Audit

### 4.1 Mandatory Directory Structure (`interfaces/`, `base/`, `implementations/`)
User dogmas and original requests mandate:
> *"Decomposizione della gerarchia in sottocartelle per ruoli architetturali: interfacce (interfaces/), strutture base (base/) e implementazioni concrete (implementations/)."*

**Current Workspace Adherence**: **0%**.
- `medclient/core-rust/src/`: Flat structure (`main.rs`, `sidecar.rs`, `state.rs`, `supervisor.rs`, `protocols/asset_protocol.rs`). No `interfaces/`, `base/`, or `implementations/`.
- `medfactory/src/`: Subdirectories (`chunking/`, `compression/`, `database/`, `dla/`, `packager/`) contain files placed directly inside without role segregation.
- `medfactory/src/ontologies/`: Empty directory.
- `medclient/sidecar-python/`: Entire tree missing.
- `medclient/frontend-react/`: Entire tree missing.

### 4.2 File Length Limits (300-450 Lines Max)
User rules mandate:
> *"Limite di 300–450 righe per singolo file sorgente."*

| File | Line Count | Conformance Status | Notes |
| :--- | :--- | :--- | :--- |
| `generatore_architettura.py` | **503 lines** | **VIOLATION** | Exceeds 450 lines limit |
| `medfactory/src/database/sqlite_builder.py` | 144 lines | OK (<450) | Missing architectural decomposition |
| `medfactory/src/packager/medpack_assembler.py` | 137 lines | OK (<450) | Missing architectural decomposition |
| `medfactory/src/chunking/hierarchical_chunker.py` | 108 lines | OK (<450) | Missing architectural decomposition |
| `medfactory/src/dla/table_resolver.py` | 80 lines | OK (<450) | Missing architectural decomposition |
| `medclient/core-rust/src/main.rs` | 77 lines | OK (<450) | Contains tests in main |
| `medclient/core-rust/src/supervisor.rs` | 74 lines | OK (<450) | Broken compilation |
| `medfactory/src/dla/layout_analyzer.py` | 56 lines | OK (<450) | Toy implementation |
| `medclient/core-rust/src/protocols/asset_protocol.rs` | 55 lines | OK (<450) | Zero-copy violation |
| `medfactory/src/compression/zstd_compressor.py` | 54 lines | OK (<450) | Generic identifiers |
| `medclient/core-rust/src/sidecar.rs` | 48 lines | OK (<450) | TOCTOU bug, generic identifiers |
| `medfactory/src/packager/manifest_models.py` | 41 lines | OK (<450) | 17 Ellipsis violations |
| `medclient/core-rust/src/state.rs` | 34 lines | OK (<450) | Stub-like heuristic |
| `medclient/core-rust/Cargo.toml` | 24 lines | OK | Unpinned dependencies |
| `requirements.txt` | 7 lines | OK | Missing production packages |

---

## 5. Catalog of Forbidden Patterns, Markers & Anti-Patterns

### 5.1 Ellipsis (`...`) Violations
The global dogma strictly forbids `...` (Ellipsis).
- **`medfactory/src/packager/manifest_models.py`**:
  - Line 8: `hpo_release: str = Field(...)`
  - Line 9: `icd10_version: str = Field(...)`
  - Line 10: `atc_index_year: int = Field(...)`
  - Line 15: `module_kb_sqlite: str = Field(...)`
  - Line 16: `vector_index_bin: str = Field(...)`
  - Line 17: `vector_meta_bin: str = Field(...)`
  - Line 18: `assets_media_blob: str = Field(...)`
  - Line 19: `assets_media_manifest: str = Field(...)`
  - Line 24: `uncompressed_bytes: int = Field(...)`
  - Line 25: `compressed_bytes: int = Field(...)`
  - Line 26: `total_parent_chunks: int = Field(...)`
  - Line 27: `total_child_chunks: int = Field(...)`
  - Line 28: `total_vectors: int = Field(...)`
  - Line 34: `pack_id: str = Field(...)`
  - Line 35: `display_title: str = Field(...)`
  - Line 37: `compiler_toolchain: str = Field(...)`
- **`medfactory/src/chunking/hierarchical_chunker.py`**:
  - Line 51: Docstring contains `B(c) = "[h_1 > h_2 > ... > h_k]\n\n"`

### 5.2 Banned Lexical Identifiers & Semantics
The global dogma prohibits markers: `*mock*`, `*stub*`, `*fake*`, `*dummy*`, `*sample*`, `*fixture*`, `*placeholder*`, `*temp*`, `*tmp*`, `*draft*`, `*wip*`, `*dry_run*`, `*bypass*` and generic non-domain identifiers: `data`, `obj`, `item`, `val`, `res`, `result`, `payload`, `foo`, `bar`, `baz`.

1. **`*sample*` Pattern**:
   - `medfactory/src/compression/zstd_compressor.py:14, 18, 24`: Parameter `samples: List[bytes]` in `train_dictionary`. Must be renamed to `training_records` or `corpus_entries`.
2. **`*temp*` Pattern**:
   - `medfactory/src/database/sqlite_builder.py:63, 64, 65, 66, 67`: Parameter `temp_db_path` and attribute `self.temp_db_path`. Must be renamed to `working_database_path` or `transitional_database_path`.
3. **`payload` Generic Identifier**:
   - `medclient/core-rust/src/sidecar.rs:8, 29, 45`: Identifier `payload` and struct field `tlv_payload`. Must be domain-specific: `handshake_frame_buffer` or `tlv_encoded_bytes`.
4. **`res` Generic Identifier**:
   - `medclient/core-rust/src/supervisor.rs:27, 50`: `let res = SetInformationJobObject(...)` and `let res = AssignProcessToJobObject(...)`. Must be `set_info_status` and `assign_status`.
5. **`data` Generic Identifier**:
   - `medfactory/src/compression/zstd_compressor.py:32, 45, 47, 53`: `data: bytes` and `compressed_data: bytes`. Must be `uncompressed_stream` and `compressed_payload_stream`.
6. **`val` Generic Identifier**:
   - `medfactory/src/dla/table_resolver.py:63`: `[val if val is not None else "" for val in r_row]`. Must be `cell_text`.
7. **`item` Generic Identifier**:
   - `medfactory/src/packager/medpack_assembler.py:103-104`: `item_rel_path`, `item_full_path`. Must be `entity_relative_path`, `entity_absolute_path`.

### 5.3 Dummy / Placeholder Data Sentinels
- **`medfactory/src/packager/medpack_assembler.py:74`**:
  ```python
  compressed_bytes=1, # Calcolato dopo
  ```
  `compressed_bytes` is hardcoded to `1`, written into `manifest.json`, and never recalculated before packaging.

---

## 6. Dependency Management & Environment Audit

### 6.1 Strict Exact Pinning Violation in `Cargo.toml`
User rules mandate:
> *"È severamente proibito installare dipendenze floating (senza versione precisa)... Bloccare sempre le versioni a release esatte (es. axios==1.2.0 o axios@1.2.0)"*

In Rust Cargo, specifying `memmap2 = "0.9.5"` is equivalent to `^0.9.5` (floating semver range).
- **Violation in `medclient/core-rust/Cargo.toml`**:
  - `memmap2 = "0.9.5"` -> must be `memmap2 = "=0.9.5"`
  - `uuid = { version = "1.11.0", ... }` -> must be `uuid = { version = "=1.11.0", ... }`
  - `crc32fast = "1.4.2"` -> must be `crc32fast = "=1.4.2"`
  - `serde = { version = "1.0.217", ... }` -> must be `serde = { version = "=1.0.217", ... }`
  - `serde_json = "1.0.138"` -> must be `serde_json = "=1.0.138"`
  - `windows-sys = { version = "0.59.0", ... }` -> must be `windows-sys = { version = "=0.59.0", ... }`
  - `tikv-jemallocator = "0.6.0"` -> must be `tikv-jemallocator = "=0.6.0"`
  - `tempfile = "3.16.0"` -> must be `tempfile = "=3.16.0"`

### 6.2 Missing Dependency Manifests
1. **`medfactory/pyproject.toml`**: Does not exist. MedFactory has no formal dependency specification.
2. **`medclient/sidecar-python/pyproject.toml`**: Does not exist.
3. **`medclient/frontend-react/package.json`**: Does not exist.
4. **Root `requirements.txt`**: Contains only LLM documentation tooling (`crewai==1.15.33`, `google-genai==2.34.0`, `langchain-google-genai==4.4.2`, etc.) and zero production dependencies.

### 6.3 Missing Installed Packages in `agent_env`
Verification via python execution in `agent_env` revealed:
- `fastapi`: **MISSING** (`No module named 'fastapi'`)
- `docling`: **MISSING** (`No module named 'docling'`)
- `pyhpo`: **MISSING** (`No module named 'pyhpo'`)
- `polars`: **MISSING** (`No module named 'polars'`)
- Installed & operational: `onnxruntime` (1.31.1), `symspellpy` (6.7.7), `zstandard` (0.25.0), `blake3` (1.0.4), `pydantic` (2.12.5), `uvicorn` (0.54.0), `pytest` (8.3.4).

---

## 7. Agentic API & Security Audit

### 7.1 Agentic API Readiness: 0%
Global rules mandate that every application/server must expose an Agentic API for real-time AI inspection:
- `/agent/health`
- `/agent/state`
- `/agent/execute`
- `/agent/schema`
- Authenticated via ephemeral `.agent_token` UUID on loopback `127.0.0.1`.

**Finding**: No Agentic API endpoints exist in either the Rust core or any Python script in the repository.

### 7.2 Windows DPAPI Secret Management: 0%
Global rules mandate:
> *"Deploy Sicuro e DPAPI: Vietato hardcodare chiavi in chiaro. Le credenziali e API keys in Windows DEVONO essere crittografate localmente con CryptProtectData (DPAPI)."*

**Finding**: Windows DPAPI (`CryptProtectData` / `win32crypt`) is not used anywhere in the codebase. In `generatore_architettura.py:26`, API keys are fetched directly as plain environment strings without DPAPI protection.

---

## 8. Complete Implementation Matrix: MedFactory vs MedClient

| Subsystem | Component / Module | Expected Functionality | Current Status | Issues Identified |
| :--- | :--- | :--- | :--- | :--- |
| **MedFactory** | DLA Layout Analyzer | Docling integration, column isolation, ISMP units | **Partial / Toy** | 56 lines; no Docling; synthetic col_id; no PDF extraction. |
| **MedFactory** | Table Span Resolver | 2D OTSL table expansion, Markdown generation | **Primitive** | 80 lines; works on dataclass cells; not connected to Docling. |
| **MedFactory** | Hierarchical Chunker | Parent (800-1200) & Child (150-250) + Breadcrumb | **Partial** | 108 lines; no Parent chunker; whitespace split; docstring `...`. |
| **MedFactory** | Zstd Compressor | Dictionary trainer (112KB), level 19 compression | **Primitive** | 54 lines; banned identifier `samples`; in-memory decompression. |
| **MedFactory** | SQLite Module Builder | STRICT SQLite DDL, VACUUM INTO, clinical tables | **Incomplete** | 144 lines; missing ontologies/diagnostics tables; fragile CHECK. |
| **MedFactory** | MedPack Assembler | Bit-for-bit tar.zst, BLAKE3, manifest generation | **Broken** | 137 lines; dummy `compressed_bytes=1`; in-memory BytesIO buffering. |
| **MedFactory** | Ontologies Ingestion | ICD-10, ATC, HPO / PyHPO graph compiler | **MISSING (0%)** | `medfactory/src/ontologies/` is an empty folder. |
| **MedFactory** | Vector Index Builder | Bounded vector embedding generation & index.bin | **MISSING (0%)** | No code for vector indexing or HNSW/LanceDB. |
| **MedFactory** | Media Vault Assembler| CBOR manifest & blob.bin packing | **MISSING (0%)** | No code to pack media blob or generate CBOR manifest. |
| **MedClient** | Core Rust Tauri Host | Tauri v2 windowing, desktop lifecycle, IPC | **MISSING (0%)** | No Tauri dependency in `Cargo.toml`; no UI host code. |
| **MedClient** | Win32 Job Supervisor | Win32 Job Object, kill on parent close | **BROKEN** | Compilation failure (`*mut c_void` vs `usize`). |
| **MedClient** | Sidecar Handshake | Ephemeral port & UUID token generation | **Incomplete** | 48 lines; TOCTOU bug (`drop(listener)`); no process spawn. |
| **MedClient** | Asset Protocol | Zero-copy mmap streaming via `med-asset://` | **Defective** | Heap reallocation via `mmap.to_vec()`; hardcoded `.webp`. |
| **MedClient** | State Machine | Throttling supervisor (<300MB RSS limit) | **Stub** | 34 lines; no actual memory querying (GetProcessMemoryInfo). |
| **MedClient** | Sidecar FastAPI Python| Clinical sidecar ASGI server on 127.0.0.1 | **MISSING (0%)** | Directory does not exist. |
| **MedClient** | NLP Pipeline | SymSpell + Inverted Index + ONNX INT8 Embeddings | **MISSING (0%)** | Not implemented. |
| **MedClient** | Diagnostic Engine | Log-Odds symptom matcher + Rule-Out gating | **MISSING (0%)** | Not implemented. |
| **MedClient** | Pharmacology Engine | CYP450 multi-way interaction matrix & Blackbox | **MISSING (0%)** | Not implemented. |
| **MedClient** | Educational / FSRS | NLI Cross-Encoder + FSRS spaced repetition | **MISSING (0%)** | Not implemented. |
| **MedClient** | Frontend React SDUI | Vite + React + TS, 4 typed SDUI blocks, Zustand | **MISSING (0%)** | Directory does not exist. |
| **Cross-Cutting**| Agentic API | `/agent/health`, `/agent/state`, `/agent/execute` | **MISSING (0%)** | Not implemented. |
| **Cross-Cutting**| DPAPI Secret Manager | Local cryptographic protection of keys/tokens | **MISSING (0%)** | Not implemented. |

---

## 9. Discrepancies Across Reference Documents

During the audit, cross-referencing `SRS_MedClient_Architettura_Completa.md`, `Pianificazione App Medica Ibrida.pdf`, and `piano_costruzione_autonoma_medplatform.md` revealed key discrepancies:

1. **SDUI Block Typology Mismatch**:
   - **`SRS_MedClient_Architettura_Completa.md` (lines 6431-6508)**: Defines the 4 blocks as:
     1. `ClinicalSheetBlock` (ICD-10, vitals snapshot, callouts)
     2. `SymptomMatcherBlock` (HPO symptom tree, relevance score)
     3. `DrugSafetyBlock` (ATC codes, CYP450 interactions, clearance indices)
     4. `ExamSimulatorBlock` (MCQ options, KaTeX scenario, rationale stream)
   - **`piano_costruzione_autonoma_medplatform.md` (line 51 & 115-119)**: Defines the 4 blocks as:
     1. `MarkdownBlock`
     2. `DifferentialDiagnosisBlock`
     3. `InteractiveFlowchartBlock`
     4. `ClinicalExamBlock`
   - *Resolution Required*: Unify the block schemas into polymorphic Pydantic v2 discriminated union models that support both the domain-specific data blocks (`ClinicalSheet`, `SymptomMatcher`, `DrugSafety`, `ExamSimulator`) and their presentation renderers (`Markdown`, `Differential`, `Flowchart`, `ExamForm`).

2. **Repetition and Draft Headers in the SRS Document**:
   - In `SRS_MedClient_Architettura_Completa.md`, lines 1 to 1254 contain an initial draft of Modulo 1.1, 1.2, and 1.3, which is then repeated starting at line 1255 with different numbering. Downstream implementation must use the consolidated modules starting from line 1255.

3. **WAN / RPC Obsoleted from Early Planning**:
   - `Pianificazione App Medica Ibrida.pdf` (pages 4-9) explored Tailscale P2P VPN, Redis Cloud casella postale, and llama.cpp RPC. The SRS formally rejected this in favor of completely offline build-time `.medpack` delivery and CPU-only deterministic inference.

---

## 10. Prioritized Actionable Remediation Checklist

To achieve full compliance with all architectural requirements and user rules, the following concrete actions must be executed:

### Immediate Fixes (Compilation & Standards):
- [ ] Fix `medclient/core-rust/src/supervisor.rs`: replace `0` with `std::ptr::null_mut()` and handle `INVALID_HANDLE_VALUE`.
- [ ] Eliminate compiler warnings in Rust (`unused import`, `unused variable`).
- [ ] Enforce exact version pinning in `Cargo.toml` (`=0.9.5`, `=1.11.0`, etc.).
- [ ] Eliminate 17 Ellipsis (`Field(...)`) occurrences in `medfactory/src/packager/manifest_models.py`.
- [ ] Rename banned identifiers: `samples` -> `corpus_entries`, `temp_db_path` -> `working_database_path`, `payload` -> `tlv_handshake_bytes`, `res` -> `assign_status`, `data` -> `raw_stream`.
- [ ] Fix dummy sentinel `compressed_bytes=1` in `medpack_assembler.py` to reflect actual compressed size.
- [ ] Fix zero-copy violation in `asset_protocol.rs`: return raw slice/pointer without `.to_vec()` heap copy.

### Architectural Restructuring:
- [ ] Decompose `medfactory/src/` into `interfaces/`, `base/`, and `implementations/`.
- [ ] Decompose `medclient/core-rust/src/` into `interfaces/`, `base/`, and `implementations/`.
- [ ] Split `generatore_architettura.py` (503 lines) to stay strictly under the 450-line maximum limit.

### Missing Module Construction:
- [ ] **MedFactory**: Implement Docling DLA parser, PyHPO ontology ingestor in `medfactory/src/ontologies/`, vector index generator, media vault packager, and stream-based tar.zst compressor.
- [ ] **MedClient Sidecar Python**: Scaffold `medclient/sidecar-python/` (`interfaces/`, `base/`, `implementations/`), implement FastAPI app on loopback with stdin token authentication, SymSpell + ONNX embedding pipeline, Log-Odds symptom matcher, CYP450 multi-way interaction engine, and FSRS scheduler.
- [ ] **MedClient Frontend React**: Scaffold `medclient/frontend-react/`, install TailwindCSS/Vite/TS, implement Zustand persistent state store, and create the 4 typed SDUI block renderers.
- [ ] **Agentic API**: Implement `/agent/health`, `/agent/state`, `/agent/execute`, and `/agent/schema` with loopback ephemeral token.
- [ ] **DPAPI**: Implement Windows DPAPI wrapper (`CryptProtectData`) for secure local secret persistence.
