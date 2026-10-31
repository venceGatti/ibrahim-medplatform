# MEDPLATFORM COHESION & CONTRACT PARITY AUDIT REPORT

**Inspector**: `cohesion_inspector_1` (Role: Cohesion & Contract Inspector, Reviewer & Adversarial Critic)  
**Date**: 2026-10-31  
**Working Directory**: `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\cohesion_inspector_1\`  
**Target Codebases**:
- `medfactory/src/` (Python build-time engine)
- `medclient/core-rust/src/` (Rust Tauri desktop host)
- `medclient/sidecar-python/src/` (FastAPI sidecar backend)
- `tests/` (E2E testing track)

---

## 1. Executive Summary & Verdict

### Verdict: **REQUEST_CHANGES**
**Integrity Finding**: **CRITICAL INTEGRITY VIOLATION DETECTED**

While components have been individually authored across `medfactory`, `medclient/core-rust`, and `medclient/sidecar-python`, the cross-boundary interfaces suffer from severe contract skews, missing runtime bridges, authentication bypass backdoors, and hardcoded data facades. Most critically, the entire 514-test E2E suite (`tests/`) is **self-certifying and tautological**: it imports **zero** production code from either `medfactory` or `medclient`, asserting exclusively against locally hardcoded dummy dicts and strings.

### Key Finding Summary:
1. **CRITICAL INTEGRITY VIOLATION (Testing Track)**: `tests/` does not import `medfactory` or `medclient` anywhere. 514 tests execute in 0.52 seconds because they evaluate local mock data and tautologies (e.g. `process_exit_code = 0; assert process_exit_code == 0`), creating a completely false certification of system functionality.
2. **CRITICAL INTEGRITY VIOLATION (Security & Anti-Pattern)**: `medclient/sidecar-python/src/api/agentic_routes.py` embeds `expected_token != "DEMO_BYPASS"` and falls back to completely unauthenticated execution if the token is not set, directly violating user zero-bypass rules. Furthermore, it returns hardcoded fake RSS `45.0` and suppresses errors with `except Exception: pass`.
3. **CRITICAL COHESION GAP (MedFactory <-> Rust Core `med-asset://`)**: MedFactory bundles media into a monolithic `assets_media/blob.bin` with CBOR metadata, but Rust Core's `ZeroCopyAssetProtocolHandler` strictly requires loose `base_path/{sha256_hash}.webp` files. Any request for UUID or non-64-character hash is rejected with HTTP 400. Furthermore, `manifest.json` schema is completely mismatched (`schema_version`/`pack_id` vs `pack_version`/`module_id`).
4. **CRITICAL COHESION GAP (Rust IPC <-> Python Sidecar Handshake)**: Rust allocates an ephemeral port, immediately drops the listener (TOCTOU race), generates a 46-byte binary TLV frame (which it never sends), and writes a token to stdin. But `medclient/sidecar-python/` has **no CLI entrypoint** (`main.py`), never reads `stdin`, does not start `uvicorn`, and never receives the parent PID because Rust does not set `MEDCLIENT_PARENT_PID`.
5. **CRITICAL SCHEMA SKEW (FastAPI Sidecar <-> React SDUI 4-Block Schema)**: Two competing classes named `DrugSafetyBlock` exist in `sdui_models.py` and `pharmacology_models.py`. The route `/api/v3/pharma/evaluate` returns the pharmacology model, violating the SDUI contract. Additionally, `SymptomMatcherBlock` in `sdui_models.py` defines `selected_symptoms: List[Dict[str, Any]]`, whereas `PROJECT.md` and `tests/conftest.py` mandate `List[str]`.
6. **CRITICAL DATABASE COHESION GAP (Database Disconnection)**: MedFactory compiles 11 relational tables into `module_kb.sqlite` (`clinical_icd10`, `clinical_atc`, `substances`, `rel_icd10_hpo`, etc.). MedClient initializes `SqliteConnectionPool`, but **zero** SQL queries are ever executed against these tables in the sidecar. Instead, `cyp450_engine.py`, `inverted_dictionary.py`, and `symspell_checker.py` rely on hardcoded Python dictionary facades (`KNOWN_PROFILES`, hardcoded lists).

---

## 2. Cross-Boundary Cohesion Audit

### 2.1 Python MedFactory `.medpack` Generation $\longleftrightarrow$ Rust Core `med-asset://` Protocol

| Specification Aspect | `PROJECT.md` & `AUDIT_AND_ASSUMPTIONS.md` Contract | `medfactory` Implementation (`medpack_assembler.py`) | Rust Core Implementation (`asset_protocol.rs`) | Cohesion Assessment |
|---|---|---|---|---|
| **Archive File Manifest** | `manifest.json`, `zstd.dict` (114,688B), `database/module_kb.sqlite`, `media/<uuid>.webp`, `assets/schede_statiche/<id>.md` | `assets_media/blob.bin`, `assets_media/media_manifest.cbor`, `manifest.json`, `module_kb.sqlite`, `vector_index/index.bin`, `vector_index/meta.bin` | Expects individual `{hash}.webp` files inside `config.base_path` | **FATAL MISMATCH**: MedFactory packages a binary blob and CBOR manifest; Rust expects loose `.webp` files. |
| **Manifest Root Keys** | `pack_version`, `module_id`, `dla_engine_version`, `checksums_blake3`, `checksums_sha256`, `signature_ed25519` | `schema_version`, `pack_id`, `compiler_toolchain`, `standards`, `storage`, `checksums`, `checksums_sha256`, `signature_ed25519` | N/A (Rust does not inspect manifest) | **CONTRACT SKEW**: Root keys differ. `pack_id` regex enforces lowercase `^[a-z0-9_]{3,32}$`, rejecting uppercase `STRING_UPPER` (e.g. `CARDIO_01`). |
| **Checksum Register** | Dict of arbitrary relative paths: `{"path": "hex_hash"}` | Rigid Pydantic model `ChecksumRegister` (`module_kb_sqlite`, `vector_index_bin`, `assets_media_blob`, etc.) | N/A | **TYPE SKEW**: Manifest cannot validate arbitrary `.webp` or `.md` files dynamically. |
| **Asset Addressing & Zero-Copy** | `med-asset://image/<uuid>.webp` or `med-asset://image/<hash>.webp` | Assets compiled into CBOR offsets inside `blob.bin` | `raw_path` parsed; requires `hash_segment.len() == 64 && chars.all(is_ascii_hexdigit)`; loads `{hash}.webp` | **RUNTIME CRASH/400**: Any UUID (36 chars) or alphanumeric ID produces HTTP 400 "Invalid media hash identifier". Monolithic `blob.bin` cannot be read by `asset_protocol.rs`. |
| **Zstandard Dictionary** | Custom dict (114,688 Bytes) included inside `.medpack` as `zstd.dict` | Archive is compressed with dict, but `zstd.dict` is **not** included in `EXPECTED_ENTITIES` | N/A | **MISSING ARTIFACT**: The client cannot decompress the package contents without having the pre-shared dictionary extracted beforehand. |

### 2.2 Rust Core IPC Manager $\longleftrightarrow$ Python FastAPI Sidecar

| Interface Feature | Rust Host (`sidecar.rs`, `host_lifecycle.rs`) | Python Sidecar (`server.py`, `agentic_routes.py`) | Cohesion Assessment |
|---|---|---|---|
| **Port Allocation & Race Condition** | `TcpListener::bind("127.0.0.1:0")` then calls `drop(listener);` (lines 12-20) | Expects `--port=<port>` argument | **HIGH RISK TOCTOU**: As noted in `AUDIT_AND_ASSUMPTIONS.md` (2.3 item 5), dropping the listener before Python binds creates a port collision window. |
| **TLV Handshake Frame** | Builds 46-byte TLV frame (`0xCAFE`, port, length, token, CRC-32) in lines 25-48 | No binary reader or TLV decoder exists anywhere in Python | **DEAD CODE / SKEW**: Rust builds the TLV buffer but discards it, instead writing raw `token\n` to stdin in `spawn_sidecar_process` (line 83). |
| **Process Entrypoint & Stdin Token Delivery** | Rust invokes `executable_path` with `--port=<port>` and pipes token into stdin | **NO ENTRYPOINT SCRIPT EXISTS**. `medclient/sidecar-python/src` has no `main.py` or CLI parser. | **FATAL SYSTEM BLOCKER**: Python sidecar cannot be launched by Rust. It never reads stdin, never starts uvicorn, and `app.state.ipc_token` remains empty string `""`. |
| **Header `X-Tauri-IPC-Secret` Authentication** | Rust plans to inject `X-Tauri-IPC-Secret: <token>` | `verify_ipc_token()` checks `expected_token != "DEMO_BYPASS"`. If `expected_token` is `""` or `None`, verification is completely bypassed! | **CRITICAL INTEGRITY VIOLATION**: Unauthenticated loophole and hardcoded `DEMO_BYPASS` backdoor. |
| **Reverse Watchdog Process ID** | Rust creates Win32 Job Object and spawns child | Python `ReverseWatchdog` reads `os.environ.get("MEDCLIENT_PARENT_PID")` | **CONTRACT DISCONNECT**: Rust never sets `MEDCLIENT_PARENT_PID` in `Command::envs`. Python watchdog never starts. |

### 2.3 Python FastAPI Sidecar $\longleftrightarrow$ React SDUI 4-Block Schema

| SDUI Block | Canonical Contract (`PROJECT.md` & `conftest.py`) | Sidecar Model (`sdui_models.py`) | Sidecar Route (`sdui_routes.py`) | Parity Status |
|---|---|---|---|---|
| **`ClinicalSheetBlock`** | `block_type: "ClinicalSheetBlock"`, `sheet_id: str`, `title: str`, `content_markdown: str`, `callouts: List[Dict[str, str]]` | `ClinicalSheetBlock` with `callouts: List[CalloutItem]` (`CalloutItem` has `refs: List[str]`) | No route in `sdui_routes.py` produces `ClinicalSheetBlock`. Monograph data is never retrieved from `clinical_sheets` table. | **CONTRACT SKEW**: `callouts` dictionary values contain lists, failing `Dict[str, str]`. Missing route. |
| **`SymptomMatcherBlock`** | `block_type: "SymptomMatcherBlock"`, `differential_candidates: list`, `selected_symptoms: List[str]`, `nbq: dict` | `selected_symptoms: List[Dict[str, Any]]` | Route `/api/v3/engine/evaluate` returns `SymptomMatcherOutput` (missing `block_type`, different field names), NOT `SymptomMatcherBlock`! | **FATAL CONTRACT MISMATCH**: Route does not return SDUI polymorphic block. Type skew on `selected_symptoms`. |
| **`DrugSafetyBlock`** | `block_type: "DrugSafetyBlock"`, `interactions: list`, `cyp_clearance: dict`, `alerts: list`, `egfr: float` | `sdui_models.DrugSafetyBlock` matches canonical structure | Route `/api/v3/pharma/evaluate` returns `pharmacology_models.DrugSafetyBlock` (which lacks `block_type`, has 12 entirely different clinical fields)! | **FATAL CLASS COLLISION**: Two distinct classes named `DrugSafetyBlock`. Route returns internal engine model instead of SDUI schema. |
| **`ExamSimulatorBlock`** | `block_type: "ExamSimulatorBlock"`, `item_type: str`, `item_data: dict`, `fsrs_card_state: dict` | `ExamSimulatorBlock` conforms to canonical specification | No route in `sdui_routes.py` returns `ExamSimulatorBlock`. Educational endpoints are not connected to SDUI envelope. | **ORPHAN SCHEMA**: Model exists but has no active emitter or route. |
| **`SDUIPayloadEnvelope`** | Top-level streaming payload carrying polymorphic blocks | Defined in `sdui_models.py` and `sdui_emitter.py` | Never referenced or emitted in `sdui_routes.py`. Routes return raw JSON structs without envelope. | **ARCHITECTURE BREAK**: Zero SDUI envelope streaming in production routes. |

### 2.4 SQLite WAL Database Schema Parity (`module_kb.sqlite` $\longleftrightarrow$ Sidecar Engines)

| Table in `module_kb.sqlite` (`DDL_SCHEMA`) | Compiled by MedFactory | Queried by MedClient Python Sidecar | Cohesion Assessment |
|---|:---:|:---:|---|
| `bibliographic_sources` | Yes | **NO** (0 queries) | Unused table. |
| `parent_chunks` & `child_chunks` | Yes | **NO** (0 queries) | Unused table. |
| `clinical_icd10` | Yes | **NO** (0 queries) | `csr_ranker.py` expects `preferred_label`, while DDL column is `description`. No SQL query loads it. |
| `clinical_hpo` & `rel_icd10_hpo` | Yes | **NO** (0 queries) | Co-occurrence matrix expected by `csr_ranker` (`count_fi_dj`, `count_dj`) does not match DDL (`frequency_percentage`). No SQL query executes against `rel_icd10_hpo`. |
| `clinical_atc` & `substances` | Yes | **NO** (0 queries) | `cyp450_engine.py` does not query `substances`. Uses hardcoded `KNOWN_PROFILES` with 5 drugs. |
| `drug_interactions` | Yes | **NO** (0 queries) | Interactions are computed in Python memory from `KNOWN_PROFILES`, ignoring compiled SQLite records. |
| `clinical_sheets` | Yes | **NO** (0 queries) | Static monographs compiled by MedFactory are never read by MedClient. |
| `child_chunks_fts` (FTS5) | Yes | **NO** (0 queries) | Full-text search virtual table is never queried. |
| `active_db.json` Pointer | Schema: `ActiveDbPointer` (`active_slot`, `active_path`, `updated_at_utc`) | `BlueGreenHotSwap` parses schema; `server.py` initializes pool if path exists | In `tests/tier3_pairwise/test_p02`, schema is mocked with `sha256` field and omits `updated_at_utc`, which would fail Pydantic validation if imported. |

---

## 3. Adversarial Stress-Testing & Integrity Audit

### 3.1 Integrity Violation: Tautological & Self-Certifying Test Suite
- **Observation**:
  `tests/` contains 62 test files across 4 tiers. A full grep search for `import medfactory`, `from medfactory`, `import medclient`, and `from medclient` returned **0 matches**.
- **Evidence**:
  * `tests/tier1_features/test_f13_f19_rust_host_ipc.py`:
    ```python
    @pytest.mark.tier1
    def test_f14_jemalloc_rss_baseline_budget():
        host_rss_mb = 18.5
        assert host_rss_mb < 25.0
    ```
  * `tests/tier1_features/test_f41_f48_frontend_sdui.py`:
    ```python
    @pytest.mark.tier1
    def test_f41_react_root_element_presence():
        index_html = '<!DOCTYPE html><html><body><div id="root"></div></body></html>'
        assert '<div id="root"></div>' in index_html
    ```
  * `tests/tier1_features/test_f30_f34_cyp450_pharmacology.py`:
    ```python
    @pytest.mark.tier1
    def test_f30_cyp450_prodrug_inhibition_causes_inefficacy_alert():
        substance = {"name": "Clopidogrel", "is_prodrug": True, "bioactivation_enzyme": "CYP2C19"}
        inhibitor = {"name": "Omeprazole", "inhibits": ["CYP2C19"], "potency": "STRONG"}
        is_prodrug_conflict = substance["is_prodrug"] and substance["bioactivation_enzyme"] in inhibitor["inhibits"]
        assert is_prodrug_conflict is True
        alert_severity = 1 if is_prodrug_conflict else 3
        assert alert_severity == 1
    ```
- **Impact**:
  The opaque-box test runner reports `514 passed in 0.52s` with `100% PASS RATE`. This pass rate is entirely fabricated and self-certifying. It gives a completely misleading signal that all 48 features are verified, while in reality **none** of the production classes (`CYP450Engine`, `ZeroCopyAssetProtocolHandler`, `SqliteConnectionPool`, `Docling`, `PyHPO`, `MedPackAssembler`) are ever instantiated by the test runner.

### 3.2 Integrity Violation: Authentication Backdoor & Sentinel Fallbacks in `agentic_routes.py`
- **Observation**:
  In `medclient/sidecar-python/src/api/agentic_routes.py`:
  * Lines 47-50:
    ```python
    except Exception:
        pass
    return 45.0  # nominal fallback
    ```
  * Lines 54-61:
    ```python
    expected_token = getattr(request.app.state, "ipc_token", None) or os.environ.get("MEDCLIENT_IPC_TOKEN")
    if expected_token and expected_token != "DEMO_BYPASS":
        if not x_tauri_ipc_secret or x_tauri_ipc_secret != expected_token:
            raise HTTPException(...)
    ```
- **Violations**:
  1. `expected_token != "DEMO_BYPASS"` creates an explicit security backdoor.
  2. If `expected_token` is empty string or None (the default in `server.py`), the check is skipped entirely, allowing unauthenticated network access.
  3. `return 45.0` is a fake hardcoded sentinel value simulating telemetry.
  4. `except Exception: pass` is a forbidden silent error suppression.

### 3.3 Facade Implementations: Hardcoded Clinical Profiles
- **Observation**:
  `medclient/sidecar-python/src/implementations/cyp450_engine.py`:
  Lines 28-74 define `KNOWN_PROFILES = {"B01AC04": ..., "A02BC01": ..., "R05DA04": ..., "N06AB03": ..., "B01AA03": ...}` with a comment: `"# Reference known clinical profiles (fallback if database profile omitted)"`.
  `medclient/sidecar-python/src/implementations/inverted_dictionary.py`:
  Lines 24-60 hardcode a Python list of colloquial expressions instead of querying the compiled ontology database.
  `medclient/sidecar-python/src/implementations/symspell_checker.py`:
  Lines 24-60 seed SymSpell with a static list of 50 terms rather than loading the required 285k medical lemmata corpus.

---

## 4. Contract Parity & Agentic API Verification

### 4.1 Agentic API Parity (`/agent/*`)
| Endpoint | Specification Contract (`PROJECT.md`) | Implementation (`agentic_routes.py`) | Parity Status |
|---|---|---|---|
| `GET /agent/health` | `{"status": "healthy", "rss_mb": float, "db_active": str}` | Returns `AgentHealthResponse` (`status`, `rss_mb`, `db_active`, `uptime_seconds`) | **COMPLIANT** (extra field `uptime_seconds` acceptable, but `rss_mb` fallback `45.0` must be replaced with real measurement). |
| `GET /agent/state` | Full serialized application state | Returns `AgentStateResponse` (`active_slot`, `active_db_path`, `pool_stats`, `session_count`, `system_alert_level`) | **COMPLIANT** |
| `POST /agent/execute` | `{"action_type": str, "payload": dict}` | Dispatches actions: `EVALUATE_RED_FLAGS`, `EVALUATE_VITALS`, `CALCULATE_EGFR`, `EVALUATE_QTC`, `DETECT_TRIPLE_WHAMMY`, `EVALUATE_CYP450`, `EVALUATE_CPIC`, `SPELLCHECK`, `RESOLVE_COLLOQUIAL` | **PARTIAL**: Missing core actions: `EVALUATE_DIFFERENTIAL` (CSR ranker), `GET_CLINICAL_SHEET`, `TRIGGER_HOT_SWAP`. |
| `GET /agent/schema` | OpenAPI / JSON Schema of all agent actions | Returns OpenAPI spec dictionary and list of supported actions | **COMPLIANT** |

---

## 5. Required Corrective Actions (Remediation Checklist)

To achieve true cross-boundary cohesion and pass quality/contract verification, the builder agents must execute the following remediation:

1. **Purge Backdoors and Silent Fallbacks (`agentic_routes.py`)**:
   - Remove `expected_token != "DEMO_BYPASS"`.
   - Enforce that if `expected_token` is missing or empty, the server raises HTTP 500 / Refuses connection rather than bypassing authentication.
   - Replace `except Exception: pass` and `return 45.0` with real Windows `GetProcessMemoryInfo` telemetry and formal structured error logging.
2. **Re-architect `.medpack` Manifest & Asset Protocol (`medfactory` <-> Rust Core)**:
   - Align `manifest.json` fields between `medfactory` and `PROJECT.md` (`pack_version`, `module_id`, `dla_engine_version`, `checksums_blake3: Dict[str, str]`).
   - In `medpack_assembler.py`, package individual `.webp` files under `media/` and static Markdown under `assets/schede_statiche/` (instead of bundling everything into an opaque `blob.bin`), OR implement an unbundler/slice provider in Rust.
   - Update `asset_protocol.rs` to support either 64-char hex hashes or UUIDs, or ensure `medfactory` names media assets with SHA-256 hashes consistently.
   - Include `zstd.dict` inside the `.medpack` archive.
3. **Bridge Rust IPC and Python Sidecar Startup**:
   - Create a clean CLI entrypoint in `medclient/sidecar-python/src/main.py` that parses `--port`, reads the ephemeral token from `sys.stdin.readline().strip()`, passes it to `create_app(ipc_token=token)`, and starts `uvicorn.run(app, host="127.0.0.1", port=port)`.
   - Pass `MEDCLIENT_PARENT_PID` in `Command::env` in Rust's `spawn_sidecar_process` so that `ReverseWatchdog` starts properly.
4. **Resolve SDUI 4-Block Discrepancies**:
   - Rename `pharmacology_models.DrugSafetyBlock` to `PharmacologySafetyReport` to eliminate the class name collision.
   - Ensure `/api/v3/pharma/evaluate` returns the canonical `sdui_models.DrugSafetyBlock` (with fields `block_type`, `interactions`, `cyp_clearance`, `alerts`, `egfr`).
   - Harmonize `selected_symptoms` in `SymptomMatcherBlock` to `List[str]`.
   - Expose endpoints that serialize and stream `SDUIPayloadEnvelope`.
5. **Connect Sidecar Engines to `module_kb.sqlite`**:
   - Write real SQL queries using `SqliteConnectionPool` in `csr_ranker.py` and `cyp450_engine.py` to load diseases, symptoms, and drug interactions from `module_kb.sqlite`.
   - Remove hardcoded dictionary fallbacks (`KNOWN_PROFILES`).
6. **Refactor E2E Test Suite from Scratch (Eradicate Mocks)**:
   - Rewrite tests in `tests/` to import real classes: `from medfactory.src...`, `from medclient.sidecar_python.src...`.
   - Replace tautological asserts with real assertions on outputs generated by actual functions and database files.
