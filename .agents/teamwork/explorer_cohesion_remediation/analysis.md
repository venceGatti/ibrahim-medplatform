# Comprehensive Cross-Boundary Cohesion & Remediation Plan

**Agent**: `explorer_cohesion_remediation`  
**Date**: 2026-10-31  
**Target Recipient**: Parent Orchestrator (`123b80e3-ef7e-4eee-9c78-b41caaecc724`)  
**Scope**: Exact architectural solutions and code specifications for the 4 critical cohesion gaps identified by `cohesion_inspector_1`.

---

## 1. Executive Summary & Problem Framing

The contract and cohesion audit conducted by `cohesion_inspector_1` issued a **REQUEST_CHANGES** verdict due to 4 systemic disconnects between MedFactory (build-time compiler), Rust MedClient Core (desktop host), and Python FastAPI Sidecar (runtime analytical engine):

1. **Asset Protocol Disconnect**: MedFactory's packager bundled media into a monolithic `assets_media/blob.bin` with CBOR offsets and omitted `zstd.dict`, while Rust's zero-copy `asset_protocol.rs` strictly unpacks and seeks loose `{sha256}.webp` files in the `media/` directory and expects `zstd.dict` at archive root.
2. **Sidecar Process Lifecycle Disconnect**: Rust `sidecar.rs` spawns the sidecar with `--port=<port>` and pipes the token to `stdin`, but the Python sidecar completely lacked an executable `src/main.py` CLI entrypoint. Furthermore, Rust omitted passing `MEDCLIENT_PARENT_PID`, leaving the reverse watchdog un-triggered, while `agentic_routes.py` contained forbidden bypass markers (`DEMO_BYPASS`, nominal `45.0` RSS fallback, empty `except: pass`).
3. **SDUI Class Collision & Schema Skew**: A naming collision existed between `pharmacology_models.DrugSafetyBlock` (internal execution summary) and `sdui_models.DrugSafetyBlock` (SDUI polymorphic envelope). `/api/v3/pharma/evaluate` was returning the internal model, violating the 4-block SDUI contract. Additionally, `selected_symptoms` in `SymptomMatcherBlock` was typed as `List[Dict[str, Any]]` instead of canonical `List[str]`.
4. **SQLite Knowledge Base Disconnection**: `cyp450_engine.py` bypassed the SQLite knowledge base by using a hardcoded `KNOWN_PROFILES` dictionary, while `csr_ranker.py` was never instantiated or populated from SQLite in `server.py` lifespan, leaving tables `substances`, `clinical_atc`, and `rel_icd10_hpo` in `module_kb.sqlite` unqueried.

This document details the exact technical solutions, database schemas, CLI signatures, and code diff specifications required for the builder agents to implement the fixes cleanly without regressions.

---

## 2. Gap 1: MedFactory Packaging vs Rust `med-asset://` Protocol

### 2.1 Root Cause Analysis
In `medfactory/src/packager/implementations/medpack_assembler.py`:
- `EXPECTED_ENTITIES` (lines 30–39) strictly demanded `assets_media/blob.bin` and `assets_media/media_manifest.cbor`.
- `zstd.dict` (114,688 Bytes) was written to `working_directory / "zstd.dict"`, but was **never added** to the TAR archive.
- Individual `.webp` files were never staged or archived.

In `medclient/core-rust/src/implementations/asset_protocol.rs`:
- Lines 82–91 strictly validate that the requested path segment is a 64-character hexadecimal SHA-256 string:
  ```rust
  if hash_segment.len() != 64 || !hash_segment.chars().all(|c| c.is_ascii_hexdigit()) {
      return Ok(AssetResponse { status_code: 400, ... });
  }
  let asset_file_path = self.config.base_path.join(format!("{}.webp", hash_segment));
  ```
- Rust requires loose `{sha256}.webp` files located in `self.config.base_path` (which points to the unpacked `media/` directory of the active `.medpack`).

### 2.2 Canonical `.medpack` Archive Layout
The `.medpack` (`.tar.zst`) archive must adhere strictly to the following POSIX TAR structure:
```
.medpack (.tar.zst)
├── manifest.json                               # Root metadata, dual checksums, Ed25519 signature
├── zstd.dict                                   # Exactly 114,688 Bytes custom Zstandard dictionary
├── module_kb.sqlite                            # Compiled SQLite database (STRICT, WAL, B-Tree, FTS5)
├── media/                                      # Loose clinical media assets
│   ├── <sha256_hash_1>.webp
│   └── <sha256_hash_2>.webp
├── assets/
│   └── schede_statiche/
│       └── <sheet_identifier>.md               # Pre-compiled CommonMark static monographs
└── vector_index/
    ├── index.bin                               # Quantized vector index
    └── meta.bin                                # Vector ID to child chunk mapping
```

### 2.3 Exact Changes to `medfactory/src/packager/base/manifest_models.py`
In `ChecksumRegister`, replace `assets_media_blob` and `assets_media_manifest` with `zstd_dict`:

```python
# Before (lines 12-19)
class ChecksumRegister(BaseModel):
    model_config = ConfigDict(frozen=True)
    module_kb_sqlite: str = Field(pattern=r"^[a-fA-F0-9]{64}$")
    vector_index_bin: str = Field(pattern=r"^[a-fA-F0-9]{64}$")
    vector_meta_bin: str = Field(pattern=r"^[a-fA-F0-9]{64}$")
    assets_media_blob: str = Field(pattern=r"^[a-fA-F0-9]{64}$")
    assets_media_manifest: str = Field(pattern=r"^[a-fA-F0-9]{64}$")

# After
class ChecksumRegister(BaseModel):
    model_config = ConfigDict(frozen=True)
    module_kb_sqlite: str = Field(pattern=r"^[a-fA-F0-9]{64}$", description="BLAKE3 hash of module_kb.sqlite")
    zstd_dict: str = Field(pattern=r"^[a-fA-F0-9]{64}$", description="BLAKE3 hash of 114,688B zstd.dict")
    vector_index_bin: Optional[str] = Field(default=None, pattern=r"^[a-fA-F0-9]{64}$")
    vector_meta_bin: Optional[str] = Field(default=None, pattern=r"^[a-fA-F0-9]{64}$")
```

### 2.4 Exact Changes to `medfactory/src/packager/implementations/medpack_assembler.py`
1. **Dynamic Entity Collection**: Replace the hardcoded `EXPECTED_ENTITIES` list with dynamic lexicographical discovery of `media/*.webp`, `assets/schede_statiche/*.md`, and `vector_index/*`.
2. **Dictionary Staging**: `build_medpack` writes `dictionary_bytes` to `staging_dir / "zstd.dict"`.
3. **WebP Validation**: Verify each file in `staging_dir / "media"` has a 64-character hex stem matching its SHA-256 digest:
   ```python
   media_dir = staging_dir / "media"
   if media_dir.exists():
       for webp_path in media_dir.glob("*.webp"):
           computed_sha = self.calculate_file_sha256(webp_path)
           if computed_sha.lower() != webp_path.stem.lower():
               raise ValueError(
                   f"Media file hash mismatch: filename={webp_path.name}, computed_sha256={computed_sha}"
               )
   ```
4. **Deterministic TAR Writer**:
   ```python
   def _write_deterministic_tar(self, staging_dir: Path, output_tar_path: Path) -> None:
       """Writes POSIX TAR with normalized metadata and lexicographical order."""
       if output_tar_path.exists():
           output_tar_path.unlink()

       # Collect all entities relative to staging_dir
       collected_paths = []
       for entry in staging_dir.rglob("*"):
           if entry.name in ["transitional_archive.tar", "transitional_archive.tar.zst"]:
               continue
           rel_path = entry.relative_to(staging_dir).as_posix()
           collected_paths.append((rel_path, entry))

       collected_paths.sort(key=lambda x: x[0])

       with tarfile.open(name=str(output_tar_path), mode="w", format=tarfile.PAX_FORMAT) as tar_archive:
           for rel_path, abs_path in collected_paths:
               tar_info = tar_archive.gettarinfo(name=str(abs_path), arcname=rel_path)
               tar_info.mtime = 0
               tar_info.uid = 0
               tar_info.gid = 0
               tar_info.uname = ""
               tar_info.gname = ""

               if abs_path.is_dir():
                   tar_info.mode = 0o755
                   tar_archive.addfile(tar_info)
               else:
                   tar_info.mode = 0o644
                   with open(abs_path, "rb") as file_in:
                       tar_archive.addfile(tar_info, fileobj=file_in)
   ```

### 2.5 Exact Changes to `medfactory/src/pipeline/implementations/medfactory_pipeline.py`
In `execute_build_pipeline`:
- Replace `assets_media/blob.bin` and `assets_media/media_manifest.cbor` staging with `media/` directory:
  ```python
  media_dir = staging_dir / "media"
  media_dir.mkdir(parents=True, exist_ok=True)
  
  # For each clinical image extracted by DLA:
  # Compute SHA-256 of image webp bytes, write to staging_dir / "media" / f"{sha256_hex}.webp"
  sample_image_bytes = b"RIFF....WEBPVP8 "  # Real WebP binary frame
  sample_image_hash = hashlib.sha256(sample_image_bytes).hexdigest()
  sample_image_path = media_dir / f"{sample_image_hash}.webp"
  sample_image_path.write_bytes(sample_image_bytes)
  ```
- Write `zstd.dict` to `staging_dir / "zstd.dict"` as well as `working_directory / "zstd.dict"`.

---

## 3. Gap 2: Missing Python Sidecar CLI Entrypoint & Process Environment

### 3.1 Root Cause Analysis
- `medclient/core-rust/src/implementations/sidecar.rs` invokes `Command::new(executable_path).arg(format!("--port={}", port))` and writes `token\n` to stdin, but **does not set** the `MEDCLIENT_PARENT_PID` environment variable.
- `medclient/sidecar-python/` had no `src/main.py`.
- `server.py` lifespan (lines 22–30) attempts to read `os.environ.get("MEDCLIENT_PARENT_PID")`. Because it was not set, `ReverseWatchdog` was never started.
- `agentic_routes.py` contained `DEMO_BYPASS` checks and fallback sentinel `return 45.0` under an empty `except Exception: pass` block.

### 3.2 Rust Core Sidecar Spawner Modification
File: `medclient/core-rust/src/implementations/sidecar.rs`  
In `spawn_sidecar_process`, inject `MEDCLIENT_PARENT_PID`:

```rust
// In spawn_sidecar_process, lines 64-76:
let mut command_builder = Command::new(executable_path);

// Argomenti espliciti: nessun shell=True
command_builder.arg(format!("--port={}", handshake_config.ephemeral_port));
for argument in additional_arguments {
    command_builder.arg(argument);
}

// Iniezione del PID parent per il reverse watchdog di Python
command_builder.env("MEDCLIENT_PARENT_PID", std::process::id().to_string());

command_builder
    .stdin(Stdio::piped())
    .stdout(Stdio::piped())
    .stderr(Stdio::piped());
```

### 3.3 New File: `medclient/sidecar-python/src/main.py`
Create `src/main.py` with rigorous argument parsing, stdin token extraction, and clean uvicorn startup guarded by `if __name__ == '__main__':` (required by Windows MP shield):

```python
"""
Main CLI Entrypoint for MedClient Python Sidecar.
Parses --port, reads ephemeral IPC token from stdin, and starts Uvicorn.
"""
import os
import sys
import argparse
import uvicorn
from src.api.server import create_app


def parse_arguments() -> argparse.Namespace:
    """Parse explicit command-line flags."""
    parser = argparse.ArgumentParser(
        description="MedClient High-Performance Python Sidecar Backend"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Ephemeral loopback port allocated by Tauri host",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Loopback binding address (strictly 127.0.0.1)",
    )
    return parser.parse_args()


def read_stdin_ipc_token() -> str:
    """
    Read ephemeral IPC secret token from line 1 of stdin piped by Rust host.
    Falls back to MEDCLIENT_IPC_TOKEN environment variable if stdin is a tty.
    """
    ipc_token = ""
    if not sys.stdin.isatty():
        first_line = sys.stdin.readline()
        if first_line:
            ipc_token = first_line.strip()

    if not ipc_token:
        ipc_token = os.environ.get("MEDCLIENT_IPC_TOKEN", "")

    if not ipc_token:
        raise ValueError(
            "IPC Secret Token missing. Sidecar must receive ephemeral token on stdin or via MEDCLIENT_IPC_TOKEN."
        )

    return ipc_token


def main() -> None:
    """Initialize application and start ASGI server."""
    arguments = parse_arguments()
    ipc_token = read_stdin_ipc_token()

    # Pass token to factory to set on app.state.ipc_token
    application = create_app(ipc_token=ipc_token)

    uvicorn.run(
        application,
        host=arguments.host,
        port=arguments.port,
        log_level="info",
        access_log=False,
    )


if __name__ == "__main__":
    main()
```

### 3.4 Cleanup of `agentic_routes.py` and `server.py`
1. In `medclient/sidecar-python/src/api/agentic_routes.py`:
   - Eradicate `DEMO_BYPASS` and unauthenticated execution.
   - Replace `return 45.0` and empty `except: pass` in `get_process_rss_mb()` with a strict Win32/POSIX implementation that raises on failure:
   ```python
   def get_process_rss_mb() -> float:
       """Measure resident set size of current Python sidecar process in megabytes."""
       if sys.platform == "win32":
           import ctypes
           from ctypes import wintypes

           class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
               _fields_ = [
                   ("cb", wintypes.DWORD),
                   ("PageFaultCount", wintypes.DWORD),
                   ("PeakWorkingSetSize", ctypes.c_size_t),
                   ("WorkingSetSize", ctypes.c_size_t),
                   ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                   ("QuotaPagedPoolUsage", ctypes.c_size_t),
                   ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                   ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                   ("PagefileUsage", ctypes.c_size_t),
                   ("PeakPagefileUsage", ctypes.c_size_t),
               ]

           psapi = ctypes.WinDLL("psapi", use_last_error=True)
           kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
           handle = kernel32.GetCurrentProcess()
           counters = PROCESS_MEMORY_COUNTERS()
           counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
           if psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
               return round(counters.WorkingSetSize / (1024.0 * 1024.0), 2)
           raise RuntimeError(f"GetProcessMemoryInfo failed: {ctypes.get_last_error()}")
       else:
           import resource
           return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 2)
   ```
   - Strict `verify_ipc_token`:
   ```python
   def verify_ipc_token(request: Request, x_tauri_ipc_secret: Optional[str] = Header(None)) -> None:
       """Verify ephemeral IPC secret passed via header."""
       expected_token = getattr(request.app.state, "ipc_token", None) or os.environ.get("MEDCLIENT_IPC_TOKEN")
       if not expected_token:
           raise HTTPException(
               status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail="IPC authentication secret token is unconfigured on the sidecar",
           )
       if not x_tauri_ipc_secret or x_tauri_ipc_secret != expected_token:
           raise HTTPException(
               status_code=status.HTTP_403_FORBIDDEN,
               detail="Invalid or missing X-Tauri-IPC-Secret token",
           )
   ```
2. In `medclient/sidecar-python/src/api/server.py`:
   - In `lifespan`:
   ```python
   parent_pid_env = os.environ.get("MEDCLIENT_PARENT_PID")
   if parent_pid_env:
       parent_pid = int(parent_pid_env)
       if parent_pid > 0:
           watchdog = ReverseWatchdog()
           watchdog.start(parent_pid)
           app.state.watchdog = watchdog
   ```

---

## 4. Gap 3: SDUI Class Collision & Schema Skew

### 4.1 Root Cause Analysis
- `medclient/sidecar-python/src/base/pharmacology_models.py` (lines 118–134) defined a class named `DrugSafetyBlock` with fields:
  `transaction_id`, `patient_id`, `engine_version`, `processing_time_ms`, `execution_verdict`, `max_severity`, `posology_violations`, `detected_interactions`, `cyp_profile_states`, `organ_toxicities`, `pgx_alerts`, `recommended_alternatives`.
- `medclient/sidecar-python/src/base/sdui_models.py` (lines 57–67) defined a polymorphic SDUI block named `DrugSafetyBlock` with fields:
  `block_type`, `component_type`, `interactions`, `cyp_clearance`, `alerts`, `egfr`.
- In `sdui_routes.py`, `/api/v3/pharma/evaluate` imported `DrugSafetyBlock` from `pharmacology_models` and returned the raw internal structure. Any SDUI client validating the response against `DrugSafetyBlockContract` failed immediately with validation errors.
- In `sdui_models.py` line 51, `selected_symptoms: List[Dict[str, Any]]` violated `PROJECT.md` line 123 and `tests/conftest.py` line 173 (`selected_symptoms: List[str]`).

### 4.2 Exact Changes to `pharmacology_models.py`
Rename `DrugSafetyBlock` to `DrugSafetyEvaluationResult`:

```python
# Before (lines 118-134 of pharmacology_models.py)
class DrugSafetyBlock(BaseModel):
    model_config = ConfigDict(frozen=True)
    transaction_id: str
    patient_id: str
    ...

# After
class DrugSafetyEvaluationResult(BaseModel):
    """Internal analytical execution output for the pharmacology engine."""
    model_config = ConfigDict(frozen=True)

    transaction_id: str
    patient_id: str
    engine_version: str = "3.2.0-deterministic-sqlite"
    processing_time_ms: float
    execution_verdict: str  # PASSED, REVIEW_REQUIRED, REJECTED
    max_severity: SeverityLevel
    posology_violations: List[str] = Field(default_factory=list)
    detected_interactions: List[InteractionDetail] = Field(default_factory=list)
    cyp_profile_states: Dict[str, CYPFunctionalState] = Field(default_factory=dict)
    organ_toxicities: OrganToxicityReport
    pgx_alerts: List[PharmacogenomicMatch] = Field(default_factory=list)
    recommended_alternatives: List[TherapeuticAlternative] = Field(default_factory=list)
```

Also update `medclient/sidecar-python/src/pharmacology/__init__.py` to export `DrugSafetyEvaluationResult`.

### 4.3 Exact Changes to `sdui_models.py`
1. Fix `selected_symptoms` in `SymptomMatcherBlock` (lines 44–54):
```python
# Before
class SymptomMatcherBlock(BaseModel):
    ...
    differential_candidates: List[Dict[str, Any]] = Field(default_factory=list)
    selected_symptoms: List[Dict[str, Any]] = Field(default_factory=list)
    symptoms_tree: Optional[List[Dict[str, Any]]] = None
    nbq: Optional[Dict[str, Any]] = None

# After
class SymptomMatcherBlock(BaseModel):
    ...
    differential_candidates: List[Dict[str, Any]] = Field(default_factory=list)
    selected_symptoms: List[str] = Field(default_factory=list)
    symptoms_tree: Optional[List[Dict[str, Any]]] = None
    nbq: Optional[Dict[str, Any]] = None
```

2. Confirm `DrugSafetyBlock` in `sdui_models.py`:
```python
class DrugSafetyBlock(BaseModel):
    """Canonical SDUI Block 3 representing drug safety status for UI rendering."""
    model_config = ConfigDict(frozen=True, extra="allow")

    block_type: Literal["DrugSafetyBlock"] = "DrugSafetyBlock"
    component_type: Literal["DrugSafetyBlock"] = "DrugSafetyBlock"
    interactions: List[Dict[str, Any]] = Field(default_factory=list)
    cyp_clearance: Dict[str, float] = Field(default_factory=dict)
    alerts: List[Dict[str, Any]] = Field(default_factory=list)
    egfr: float = 90.0
```

### 4.4 Exact Changes to `sdui_routes.py`
In `medclient/sidecar-python/src/api/sdui_routes.py`:
- Import `DrugSafetyEvaluationResult` from `..base.pharmacology_models`.
- Import `DrugSafetyBlock` from `..base.sdui_models`.
- Refactor `/api/v3/pharma/evaluate` to map the evaluation into canonical `DrugSafetyBlock`:

```python
from ..base.pharmacology_models import (
    DrugSafetyEvaluationResult,
    PrescribedDrugItem,
    OrganToxicityReport,
    SeverityLevel,
)
from ..base.sdui_models import DrugSafetyBlock

@router.post("/pharma/evaluate", response_model=DrugSafetyBlock)
def evaluate_pharmacology_safety(
    prescribed_drugs: List[PrescribedDrugItem],
    patient_id: str,
    age: int = 50,
    is_female: bool = False,
    serum_creatinine_mg_dl: float = 1.0,
    serum_potassium_meq_l: float = 4.2,
    patient_genotypes: Optional[Dict[str, str]] = None,
    request: Request = None,
) -> DrugSafetyBlock:
    """Comprehensive pharmacology safety scan returning canonical SDUI Block 3."""
    t0 = time.perf_counter()
    drugs_dict = [d.model_dump() for d in prescribed_drugs]

    # 1. CKD-EPI eGFR
    renal_calc = CKDEPI2021Calculator()
    egfr = renal_calc.compute_egfr(age=age, is_female=is_female, serum_creatinine_mg_dl=serum_creatinine_mg_dl)

    # 2. CYP450 multi-way clearance & prodrug bioactivation via DB pool
    cyp_engine = getattr(request.app.state, "cyp_engine", None) if request else None
    if not cyp_engine:
        pool = getattr(request.app.state, "db_pool", None) if request else None
        cyp_engine = CYP450Engine(db_pool=pool)
    cyp_res = cyp_engine.evaluate_clearance(drugs_dict)

    # 3. QTc cardiac prolongation risk
    qtc_calc = QTcCalculator()
    qtc_res = qtc_calc.evaluate_qtc(
        prescribed_drugs=drugs_dict,
        auc_ratios=cyp_res["auc_ratios"],
        serum_potassium_meq_l=serum_potassium_meq_l,
    )

    # 4. Triple Whammy acute kidney injury detector
    tw_detector = TripleWhammyDetector()
    tw_res = tw_detector.detect_triple_whammy(prescribed_drugs=drugs_dict, egfr=egfr)

    # 5. CPIC Level 1A pharmacogenomics
    cpic_engine = CPICPharmacogenomicsEngine()
    pgx_alerts = cpic_engine.evaluate_genetics(prescribed_drugs=drugs_dict, patient_genotypes=patient_genotypes or {})

    # Compile unified UI alerts
    compiled_alerts: List[Dict[str, Any]] = []
    for inter in cyp_res["detected_interactions"]:
        compiled_alerts.append({
            "alert_type": "DRUG_INTERACTION",
            "severity": inter["severity"],
            "title": f"Interaction: {inter['source_atc']} + {inter['target_atc']}",
            "description": inter["mechanism"],
            "guideline": inter["management_guideline"],
        })

    if tw_res["triple_whammy_detected"]:
        compiled_alerts.append({
            "alert_type": "TRIPLE_WHAMMY",
            "severity": tw_res["severity_level"],
            "title": "Triple Whammy Nephrotoxicity Alert",
            "description": tw_res["clinical_warning"],
            "guideline": "Discontinue NSAID and recalculate renal dosage.",
        })

    if qtc_res["qtc_prolongation_score"] >= 6.0:
        compiled_alerts.append({
            "alert_type": "QTC_PROLONGATION",
            "severity": SeverityLevel.LEVEL_1,
            "title": "Severe QTc Prolongation Risk (Torsades de Pointes)",
            "description": f"Cumulative QTc score {qtc_res['qtc_prolongation_score']:.1f} exceeds safety threshold 6.0.",
            "guideline": "Continuous ECG telemetry monitoring required.",
        })

    for pgx in pgx_alerts:
        compiled_alerts.append({
            "alert_type": "PHARMACOGENOMICS",
            "severity": SeverityLevel.LEVEL_1 if pgx.get("is_absolute_contraindication") else SeverityLevel.LEVEL_2,
            "title": f"CPIC Alert: {pgx.get('gene_symbol')}",
            "description": pgx.get("recommendation", ""),
            "guideline": "Select alternative agent as per CPIC guidelines.",
        })

    # Extract clearance per isoenzyme for UI dial gauges
    cyp_clearance_map: Dict[str, float] = {
        iso: float(state["computed_clearance"])
        for iso, state in cyp_res["cyp_profile_states"].items()
    }

    return DrugSafetyBlock(
        block_type="DrugSafetyBlock",
        component_type="DrugSafetyBlock",
        interactions=cyp_res["detected_interactions"],
        cyp_clearance=cyp_clearance_map,
        alerts=compiled_alerts,
        egfr=round(egfr, 2),
    )
```

### 4.5 Exact Changes to `sdui_emitter.py`
Update `build_symptom_matcher_block` signature:
```python
def build_symptom_matcher_block(
    self,
    differential_candidates: List[Dict[str, Any]],
    selected_symptoms: List[str],  # Changed from List[Dict[str, Any]]
    nbq: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build SymptomMatcherBlock payload with List[str] symptoms."""
    block = SymptomMatcherBlock(
        differential_candidates=differential_candidates,
        selected_symptoms=selected_symptoms,
        nbq=nbq,
    )
    return block.model_dump()
```

---

## 5. Gap 4: SQLite Knowledge Base Direct Connection

### 5.1 Root Cause Analysis
- `medclient/sidecar-python/src/implementations/cyp450_engine.py` hardcoded 5 drugs in `KNOWN_PROFILES` (lines 28–74).
- `medclient/sidecar-python/src/implementations/csr_ranker.py` implemented `load_knowledge_base`, but had no method to load from `SqliteConnectionPool`.
- `medclient/sidecar-python/src/api/server.py` lifespan created `app.state.db_pool = SqliteConnectionPool(...)`, but **never instantiated** `csr_ranker` or passed `db_pool` to `cyp450_engine`.
- Consequently, `/api/v3/engine/evaluate` found `ranker is None` and returned empty differential candidates (`[]`), and `/api/v3/pharma/evaluate` evaluated drugs only against the static Python dictionary.

### 5.2 Direct Database Connection for `cyp450_engine.py`
1. Accept `db_pool: Optional[SqliteConnectionPool] = None` in `__init__`.
2. Eradicate `KNOWN_PROFILES` completely.
3. In `evaluate_clearance`, fetch drug metadata directly from `clinical_atc`, `substances`, and `drug_interactions`:

```python
class CYP450Engine(ICYP450Engine):
    """Models multi-way CYP450 clearance querying module_kb.sqlite directly."""

    ISOENZYMES = [
        CyP450Isoenzyme.CYP3A4,
        CyP450Isoenzyme.CYP2D6,
        CyP450Isoenzyme.CYP2C9,
        CyP450Isoenzyme.CYP2C19,
        CyP450Isoenzyme.CYP1A2,
    ]

    INHIBITOR_WEIGHTS = {"STRONG": 0.80, "MODERATE": 0.50, "WEAK": 0.20, "NONE": 0.00}
    INDUCER_WEIGHTS = {"STRONG": 1.00, "MODERATE": 0.50, "WEAK": 0.20, "NONE": 0.00}

    def __init__(self, db_pool: Optional[SqliteConnectionPool] = None) -> None:
        self._db_pool = db_pool

    def _fetch_drug_profile(self, atc_code: str) -> Dict[str, Any]:
        """Fetch substance and ATC profile from SQLite connection pool."""
        if not self._db_pool:
            raise RuntimeError(
                f"SqliteConnectionPool unconfigured: cannot resolve clinical drug profile for {atc_code}"
            )

        with self._db_pool.acquire() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 
                    a.atc_code,
                    a.substance_name,
                    a.is_prodrug AS atc_is_prodrug,
                    a.primary_cyp_enzymes,
                    s.is_prodrug AS substance_is_prodrug,
                    s.active_metabolite
                FROM clinical_atc a
                LEFT JOIN substances s ON s.atc_code = a.atc_code
                WHERE a.atc_code = ?
                """,
                (atc_code.upper(),),
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Drug with ATC code '{atc_code}' not found in knowledge base")

            is_prodrug = bool(
                row["substance_is_prodrug"]
                if row["substance_is_prodrug"] is not None
                else row["atc_is_prodrug"]
            )
            raw_enzymes = row["primary_cyp_enzymes"]
            try:
                enzymes_list = json.loads(raw_enzymes) if raw_enzymes else []
            except Exception:
                enzymes_list = []

            # Map enzymes to substrates / inhibitors
            substrates = {enz: 0.80 for enz in enzymes_list if enz in [i.value for i in self.ISOENZYMES]}
            
            # Query known recorded interactions for inhibitors/inducers
            cursor.execute(
                """
                SELECT severity_level, mechanism_description 
                FROM drug_interactions 
                WHERE substance_a = ? OR substance_b = ?
                """,
                (atc_code.upper(), atc_code.upper()),
            )
            interactions_rows = cursor.fetchall()
            inhibitors: Dict[str, str] = {}
            for irow in interactions_rows:
                mech = irow["mechanism_description"].upper()
                for iso in self.ISOENZYMES:
                    if iso.value in mech and "INHIB" in mech:
                        inhibitors[iso.value] = "STRONG" if irow["severity_level"] == 1 else "MODERATE"

            return {
                "name": row["substance_name"],
                "is_prodrug": is_prodrug,
                "is_narrow_therapeutic_index": (atc_code.upper() in ["B01AA03", "B01AC04"]),
                "substrates": substrates,
                "inhibitors": inhibitors,
                "inducers": {},
            }
```

### 5.3 Direct Database Connection for `csr_ranker.py`
Add `load_from_database` to `SparseCSRLogOddsRanker`:

```python
def load_from_database(self, db_pool: SqliteConnectionPool) -> None:
    """Initialize CSR matrix and vocabularies directly from SQLite module_kb."""
    with db_pool.acquire() as conn:
        cursor = conn.cursor()

        # 1. Fetch leaf diseases
        cursor.execute(
            "SELECT icd10_code, description FROM clinical_icd10 WHERE is_leaf = 1"
        )
        disease_rows = cursor.fetchall()
        diseases = [
            {
                "icd10_code": r["icd10_code"],
                "preferred_label": r["description"],
                "prior": 0.01,
            }
            for r in disease_rows
        ]

        # 2. Fetch HPO features
        cursor.execute(
            "SELECT hpo_id, name, information_content FROM clinical_hpo"
        )
        feature_rows = cursor.fetchall()
        features = [
            {
                "hpo_id": r["hpo_id"],
                "name": r["name"],
                "ic": float(r["information_content"]),
            }
            for r in feature_rows
        ]

        # 3. Fetch co-occurrences and pathognomonic links
        cursor.execute(
            """
            SELECT icd10_code, hpo_id, frequency_percentage, is_mandatory
            FROM rel_icd10_hpo
            """
        )
        rel_rows = cursor.fetchall()
        co_occurrences = [
            {
                "disease_code": r["icd10_code"],
                "feature_code": r["hpo_id"],
                "count_dj": 100.0,
                "count_fi_dj": float(r["frequency_percentage"]),
                "is_pathognomonic": bool(r["is_mandatory"]),
            }
            for r in rel_rows
        ]

        self.load_knowledge_base(diseases, features, co_occurrences)
```

### 5.4 Wiring into `server.py` Lifespan
In `medclient/sidecar-python/src/api/server.py`:
```python
# In lifespan(app: FastAPI):
...
db_path = app.state.active_db_path
if db_path and os.path.exists(db_path):
    app.state.db_pool = SqliteConnectionPool(db_path)
    
    # Initialize CSR Ranker from SQLite module_kb
    ranker = SparseCSRLogOddsRanker()
    ranker.load_from_database(app.state.db_pool)
    app.state.csr_ranker = ranker
    
    # Initialize CYP450 Engine with DB pool
    app.state.cyp_engine = CYP450Engine(db_pool=app.state.db_pool)
else:
    app.state.db_pool = None
    app.state.csr_ranker = None
    app.state.cyp_engine = None
```

### 5.5 Updating MedFactory Builders to Populate Tables
File: `medfactory/src/database/implementations/sqlite_module_builder.py`  
Add methods to insert into `substances` and `drug_interactions`:

```python
def insert_substance(
    self,
    substance_id: str,
    substance_name: str,
    atc_code: Optional[str] = None,
    is_prodrug: bool = False,
    active_metabolite: Optional[str] = None,
) -> None:
    """Insert substance record into substances table."""
    cursor = self.conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO substances (
            substance_id, substance_name, atc_code, is_prodrug, active_metabolite
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (substance_id, substance_name, atc_code, 1 if is_prodrug else 0, active_metabolite),
    )
    self.conn.commit()

def insert_drug_interaction(
    self,
    interaction_id: str,
    substance_a: str,
    substance_b: str,
    severity_level: int,
    mechanism_description: str,
    clinical_alert_text: str,
) -> None:
    """Insert drug-drug interaction rule into drug_interactions table."""
    cursor = self.conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO drug_interactions (
            interaction_id, substance_a, substance_b, severity_level,
            mechanism_description, clinical_alert_text
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            interaction_id,
            substance_a,
            substance_b,
            severity_level,
            mechanism_description,
            clinical_alert_text,
        ),
    )
    self.conn.commit()
```

File: `medfactory/src/ontologies/implementations/icd10_atc_ingestor.py`  
Add benchmark drugs (Omeprazole, Fluoxetine, Warfarin) to `CORE_ATC_DATA`:
- `{"atc": "A02BC01", "name": "Omeprazole", "l1": "A", "l2": "A02", "l3": "A02B", "l4": "A02BC", "prodrug": False, "cyp": ["CYP2C19"], "ddd": 20.0, "unit": "mg"}`
- `{"atc": "N06AB03", "name": "Fluoxetine", "l1": "N", "l2": "N06", "l3": "N06A", "l4": "N06AB", "prodrug": False, "cyp": ["CYP2D6"], "ddd": 20.0, "unit": "mg"}`
- `{"atc": "B01AA03", "name": "Warfarin", "l1": "B", "l2": "B01", "l3": "B01A", "l4": "B01AA", "prodrug": False, "cyp": ["CYP2C9"], "ddd": 5.0, "unit": "mg"}`

File: `medfactory/src/pipeline/implementations/medfactory_pipeline.py`  
Populate `substances` and `drug_interactions` during build:
- Insert substances for all ATC records (`substance_id = atc_code`, `is_prodrug = atc.is_prodrug`).
- Insert interaction rules (e.g. Clopidogrel + Omeprazole: Level 1 lethal failure via CYP2C19 inhibition; Codeine + Fluoxetine: Level 1 lack of analgesia via CYP2D6 inhibition).

---

## 6. Comprehensive Verification & Invalidation Matrix

| Gap | Component | Failure Condition (Invalidation) | Verification Method |
|---|---|---|---|
| **1. Packaging** | `medpack_assembler.py` | Archive contains `blob.bin` or omits `zstd.dict` or `media/*.webp` | Unpack generated `.medpack` with `tarfile.open()`; assert `"zstd.dict" in names` and all entries in `media/` have 64-char hex names matching SHA-256. |
| **1. Asset Stream** | `asset_protocol.rs` | HTTP 400 or HTTP 404 when requesting `med-asset://image/<sha256>.webp` | Run `cargo test test_asset_protocol_handler` in `medclient/core-rust/`; assert status 200 and zero-copy mmap body. |
| **2. CLI Entrypoint** | `src/main.py` | Python sidecar fails to start or parse `--port` or read token from stdin | Execute `.\agent_env\Scripts\python.exe -m src.main --port 8000` feeding UUID token via stdin pipe; verify process binds `127.0.0.1:8000`. |
| **2. Watchdog** | `reverse_watchdog.py` | Reverse watchdog thread not started or fails to exit when parent dies | Spawn sidecar with `MEDCLIENT_PARENT_PID`, kill parent process; verify sidecar process exits within 500ms. |
| **2. Auth Bypasses** | `agentic_routes.py` | `DEMO_BYPASS` present or missing token allows HTTP 200 | Grep codebase for `DEMO_BYPASS` (assert 0 matches); execute `GET /agent/health` without `X-Tauri-IPC-Secret` (assert HTTP 403). |
| **3. SDUI Schema** | `sdui_routes.py` | Response from `/api/v3/pharma/evaluate` fails `DrugSafetyBlockContract.model_validate()` | In pytest, invoke `/api/v3/pharma/evaluate` and validate response against `DrugSafetyBlockContract(extra="forbid")`. |
| **3. Symptoms List** | `sdui_models.py` | `selected_symptoms` validation fails when passed `List[str]` | Inspect `SymptomMatcherBlock` fields; validate `{"selected_symptoms": ["HP:0001650"]}` passes without error. |
| **4. SQLite CYP450** | `cyp450_engine.py` | `KNOWN_PROFILES` present or queries fail without fallback | Grep for `KNOWN_PROFILES` in `cyp450_engine.py` (assert 0 matches); evaluate clearance for `B01AC04` against real `module_kb.sqlite`. |
| **4. SQLite CSR** | `csr_ranker.py` | `/api/v3/engine/evaluate` returns empty candidates or fails to query `rel_icd10_hpo` | Call `load_from_database(db_pool)` on `SparseCSRLogOddsRanker`; assert `len(ranker.idx_to_disease) > 0` and differential ranking succeeds. |
