# SPECIFICATION MINING, CROSS-COMPARISON & REGISTER OF OPERATIONAL ASSUMPTIONS
## MedPlatform: Hybrid Asymmetric Medical Knowledge & Diagnostic Desktop Architecture

**Date:** 2026-10-30  
**Author:** `spec_miner_1` (Role: Spec Miner & Assumptions Lead)  
**Status:** Canonical Reference & Audit Baseline  
**Target Directory:** `.agents/teamwork/spec_miner_1/spec_inventory.md`

---

## 1. Executive Summary & Document Lineage

### 1.1 Document Heritage & Authority Hierarchy
The architectural specification of the MedPlatform ecosystem is established across three primary source documents and the overarching user directives:

1. **User Global Directives & Approved Request (`ORIGINAL_REQUEST.md`):** Supreme authority. Mandates 100% production rigor unconditionally (zero mock, zero stub, zero fake, zero silent fallbacks, no placeholders like TODO/pass/Ellipsis), pinned exact dependencies, strict physical constraints (<300MB RSS, <50ms query latency, real Docling DLA, 112KB Zstd dictionary, real `.medpack` archives, SQLite WAL Blue/Green swap, zero-copy `med-asset://` mmap protocol, max 300-450 lines per file in `interfaces/`, `base/`, `implementations/`, Windows DPAPI secrets, subprocess without `shell=True`, and loopback Agentic API).
2. **Software Requirements Specification (`SRS_MedClient_Architettura_Completa.md`, 394 KB, 6,916 lines):** Authoritative formal specification containing IEEE/ISO-style contracts, mathematical formulas, DDL schemas, Pydantic v2 data models, and component lifecycles.
3. **Pianificazione App Medica Ibrida (`Pianificazione App Medica Ibrida.pdf`, 64 pages, 355 KB extracted text):** Foundational architectural transcript and rationale. Documents the evolutionary decisions, trade-offs (e.g. rejection of client-server WAN, Streamlit vs Tauri, ChromaDB vs SQLite FTS5, Ollama vs deterministic models), and catalog of 50 severe clinical/technical failure modes.
4. **Piano di Costruzione Autonoma (`piano_costruzione_autonoma_medplatform.md`, 140 lines):** Autonomous execution blueprint defining the 5 sequential phases, directory layouts, and validation gates.

---

## 2. MedFactory Specification Inventory (Build-Time Engine)

MedFactory runs offline in a build environment equipped with GPU acceleration (NVIDIA RTX 4050 6GB VRAM, CUDA/TensorRT) and AMD/Intel multi-core CPU. It digests medical textbooks, official ontologies, guidelines, and images into deterministic, immutable `.medpack` distribution bundles.

### 2.1 Document Layout Analysis (DLA) Pipeline
* **Engine Core:** IBM Docling (`docling` Python library) integrated with vision-language layout analysis models.
* **Anti-Cross-Talk Topological Slicing:** Multi-column layout parser that identifies physical bounding boxes, tracks reading flow coordinates, and performs vertical sorting within detected columns to prevent cross-column text interleaving.
* **Complex Table Normalizer:** Reconstructs tabular data with merged headers, `rowspan`, and `colspan`, serializing into standardized, valid GitHub Flavored Markdown (GFM) tables or normalized JSON payloads.
* **Unit of Measure Scale Guard:** Dedicated lexical validator to prevent OCR scale corruption (specifically $\mu\text{g} \leftrightarrow \text{mg}$, $\text{mEq} \leftrightarrow \text{mmol}$, $\text{dL} \leftrightarrow \text{L}$).
* **Media & Visual Asset Extractor:** Extracts figures, charts, and histological plates, converts them to lossless/near-lossless WebP format, calculates content hashes (BLAKE3), and registers them in the asset catalog.

### 2.2 Hierarchical Chunking & Breadcrumb Context Injection
* **Parent-Child Chunking Model:**
  * **Parent Chunks:** 800–1200 tokens. Encapsulates complete clinical chapters or disease monographs.
  * **Child Chunks:** 150–250 tokens. Fine-grained semantic segments focused on discrete clinical entities (e.g., etiology, diagnostics, dosing, adverse effects).
* **Deterministic Breadcrumb Context Injection:** Every child chunk is prepended with its hierarchical taxonomic location:
  `# {AcademicDiscipline} > {Subspecialty} > {Pathology} > {SectionHeading}`
  Ensures that semantic and lexical retrieval engines retain absolute context even when evaluating isolated passages.

### 2.3 Ontological Integration (PyHPO, ICD-10, ATC)
* **PyHPO Integration:** Authoritative Python library in MedFactory to ingest the Human Phenotype Ontology (`hp.obo`, `phenotype_to_genes.txt`, `phenotype.hpoa`). Computes information content (IC) and semantic distance (Resnik / Lin / Jiang-Conrath) between phenotypes and maps diseases to HPO codes.
* **ICD-10-CM / Orphanet Ingestion:** Ingests WHO ICD-10 tables and Orphanet rare disease maps, building the primary nosological backbone.
* **ATC Classification:** Ingests WHO/AIFA Anatomical Therapeutic Chemical classification to Level 5 (chemical substance), extracting active principles, defined daily doses (DDD), and metabolic routes.
* **Knowledge Graph Serialization:** Compiles the relational tables `clinical_icd10`, `clinical_atc`, `clinical_hpo`, and `rel_icd10_hpo` into the staging SQLite database.

### 2.4 Zstandard Custom Dictionary Compression (112 KB)
* **Dictionary Specification:** Exactly 114,688 Bytes (112 KB = $112 \times 1024$ B).
* **Training Methodology:** Stratified 10% sampling across the entire medical corpus (HPO terms, ICD-10 names, ATC codes, Latin/English medical terminology, CommonMark tags).
* **Compression Profile:** Zstandard Level 19 (`zstd.ZstdCompressor(level=19, dict_data=...)`).
* **Performance Requirement:** Client-side decompression speed $\ge 1.2\text{ GB/s}$ on Intel x86_64 AVX2, enabling cold mounting without RAM spikes.

### 2.5 Static Markdown Synthesis (SSG)
* **Deterministic Synthesis:** Clinical monographs are compiled into static Markdown documents following strict CommonMark standards.
* **Embedded Callouts:** Structured callouts for `RED_FLAG`, `CONTRAINDICATION`, `EXAM_TIP`, and `CLINICAL_PEARL`.
* **Zero Runtime Generation:** Eliminates client-side LLM inference for encyclopedic sheets. Retrieval is a direct $O(1)$ SQLite B-Tree seek ($< 5\text{ ms}$).

### 2.6 `.medpack` Packaging & Manifest Specification
* **Archive Format:** POSIX `tar` archive compressed via streaming Zstandard (`.tar.zst`).
* **Reproducible Build:** File modification time forced to `mtime = 0` (Unix Epoch), permissions normalized to `0644` / `0755`, UID/GID set to `0`.
* **Container Structure:**
  ```text
  <module_id>_<version>.medpack
  ├── manifest.json                  # Pydantic-validated manifest
  ├── zstd.dict                      # 112 KB Zstd dictionary
  ├── database/
  │   └── module_kb.sqlite           # Optimized SQLite knowledge base
  ├── media/
  │   └── <media_uuid>.webp          # Lossless WebP clinical images
  └── assets/
      └── schede_statiche/           # Static Markdown clinical sheets
  ```
* **Manifest Contract (`manifest.json`):**
  * `pack_version`: SemVer string (e.g. `"1.0.0"`).
  * `module_id`: Alphanumeric module identifier (e.g. `"CARDIO_2026"`).
  * `dla_engine_version`: Version of Docling used.
  * `checksums`: Dictionary mapping relative file paths to BLAKE3 (and SHA-256) hex hashes.
  * `signature_ed25519`: Hex-encoded digital signature of the manifest body.

---

## 3. MedClient Specification Inventory (Run-Time Desktop Engine)

MedClient runs as a self-contained, offline desktop application on Intel Core i7 hardware without a dedicated GPU, sharing 8–16 GB RAM with integrated graphics (Iris Xe / UHD).

### 3.1 Host & Process Architecture (Tauri v2 + Rust)
* **Host Engine:** Tauri v2 with `tikv-jemallocator` configured with `dirty_decay_ms = 1000` to prevent memory fragmentation and retain RSS $< 25\text{ MB}$.
* **Win32 Job Object Supervisor:** Encapsulates the Tauri host and all child processes (Python sidecar, WebView2 renderer) in a Windows Job Object with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`. When Tauri closes or crashes, Windows kernel forcibly kills Python within 500ms.
* **Reverse Watchdog:** In the Python sidecar, a background thread calls `kernel32.WaitForSingleObject` on the parent PID handle. If the parent process becomes signaled, Python calls `os._exit(0)` immediately.
* **Throttling State Machine:** Monitors system RSS and physical RAM transitions:
  * `Normal` ($\text{RSS} < 220\text{ MB}$, Free RAM $> 1.5\text{ GB}$): Full fidelity, 60 FPS rendering.
  * `Constrained` ($220\text{ MB} \le \text{RSS} < 275\text{ MB}$): Drops background prefetch, flushes image caches.
  * `Critical` ($\text{RSS} \ge 275\text{ MB}$ or Free RAM $< 500\text{ MB}$): Purges WebGL contexts, restricts queries to strict Fast Path, limits DOM windowing.

### 3.2 Sidecar Coupling & IPC Security
* **Coupling Topology:** Python FastAPI sidecar running as a local ASGI microservice bound exclusively to loopback `127.0.0.1`.
* **Dynamic Ephemeral Port:** Rust binds `127.0.0.1:0` to obtain a free ephemeral port, passing it to Python at spawn.
* **Zero-Leakage Token Exchange:** Rust generates a cryptographically secure token (UUIDv4 / 32-byte hex) and writes it into the sidecar's `stdin`. Python reads the token on line 1 of `sys.stdin`.
* **Mutual Authentication:** All requests from Tauri/React to FastAPI include header `X-Tauri-IPC-Secret: <token>`. Unauthenticated requests return HTTP 403 Forbidden.

### 3.3 Zero-Copy Streaming Protocol (`med-asset://`)
* **Custom URI Scheme:** Registered in Tauri v2 as `med-asset://`.
* **Memory-Mapped I/O:** Implemented in Rust via `memmap2::Mmap` (`MapViewOfFile` on Win32). Maps requested WebP files directly into virtual memory pages.
* **Streaming Direct to GPU:** Passes bytes straight to WebView2 without copying through the Python heap or Base64 encoding strings, avoiding garbage collection spikes.

### 3.4 Resilient SQLite Storage & Blue/Green Hot Swap
* **Physical Segregation:**
  * Knowledge Layer: `%LOCALAPPDATA%/MedPlatform/knowledge/master_knowledge_blue.sqlite` and `green.sqlite`.
  * User State Layer: `%LOCALAPPDATA%/MedPlatform/userdata/user_state.sqlite` (isolated, never overwritten by updates).
* **PRAGMA Profile (Read-Only Knowledge Base):**
  * `PRAGMA journal_mode = WAL;`
  * `PRAGMA synchronous = NORMAL;`
  * `PRAGMA mmap_size = 268435456;` (256 MB memory-mapped I/O)
  * `PRAGMA cache_size = -16384;` (16 MB page cache)
  * `PRAGMA temp_store = MEMORY;`
* **Blue/Green Atomic Swap:**
  1. Staging: New `.medpack` extracts `module_kb.sqlite` into inactive slot (e.g., `green`).
  2. Verification: Runs SQLite `PRAGMA integrity_check;` and verifies BLAKE3 table checksums.
  3. Pointer Swap: Updates `current_kb.txt` pointer atomically via filesystem replace (`MoveFileExW` with `MOVEFILE_REPLACE_EXISTING`).
  4. Connection Re-point: SQLite connection pool switches active descriptor; existing queries drain on old handle, new queries route to new handle. Zero query locking.

### 3.5 Stage-Based Diagnostic & Reasoning Engine
* **Phase 0 — Deterministic Red Flags Interceptor:**
  * Shock Index: $SI = \frac{\text{HR}}{\text{SBP}} \ge 1.0 \implies$ Immediate Code Red.
  * qSOFA: $\ge 2$ points (Respiratory rate $\ge 22$, altered mentation, $\text{SBP} \le 100$) $\implies$ Severe Sepsis alert.
  * NEWS2: Score $\ge 7$ or any single parameter $= 3 \implies$ Critical physiological alert.
* **Phase 1 — Sparse CSR Matrix Log-Odds Model:**
  * Universe: $M \approx 7,000$ diseases, $N \approx 14,000$ phenotypes.
  * Representation: Compressed Sparse Row (CSR) via NumPy/SciPy. Total RAM footprint $< 13\text{ MB}$.
  * Conditional Independence Clustering: Mitigates co-linearity via sub-linear dampening $\gamma_k \in [0.35, 0.65]$:
    $$\widetilde{W}^+_k(d_j) = \frac{1}{|\mathcal{C}_k \cap S^+|^{\gamma_k}} \sum_{f_i \in \mathcal{C}_k \cap S^+} W_{ji}^+$$
  * Dirichlet/Laplace Smoothing ($\epsilon = 10^{-4}$):
    $$\hat{P}(f_i = 1 \mid d_j) = \frac{C(f_i, d_j) + \epsilon}{C(d_j) + 2\epsilon}$$
  * Pathognomonic Multiplier: $\Lambda_{ji} \ge 2.5$ for defining features.
* **Phase 2 — Pertinent Negatives & Rule-Out:**
  * Detraction: $W_{ji}^- = \ln \left( \frac{1 - \hat{P}(f_i = 1 \mid d_j)}{1 - \hat{P}(f_i = 1 \mid \neg d_j)} \right)$
  * Strict Rule-Out: If $f_i \in S^-$ and $\hat{P}(f_i = 1 \mid d_j) > 0.99 \implies W_{ji}^- \leftarrow -\infty$.
* **Phase 3 — Log-Sum-Exp Softmax Normalization:**
  * Numerical stability via $c = \max z_k$, $\text{LSE}(\mathbf{z}) = c + \ln \sum \exp(z_k - c)$.
* **Phase 4 — Active Discrimination (Next-Best-Question / NBQ):**
  * When $P(d_{(1)}) - P(d_{(2)}) < 0.15$, calculates symmetric phenotypic difference $\Delta_{\mathcal{F}} = \mathcal{F}(d_{(1)}) \mathbin{\Delta} \mathcal{F}(d_{(2)})$.
  * Selects feature $f^*$ that maximizes information gain per cost: $\arg\max \frac{IG(f_u)}{C(f_u)}$.

### 3.6 Pharmacology & Drug Safety Engine
* **CYP450 Functional State Vector:**
  * 5 Core Isoenzymes: CYP3A4, CYP2D6, CYP2C9, CYP2C19, CYP1A2.
  * Residual clearance: $C_e = \max \left( 0.05, \, 1.0 - \sum w_{\text{inh}} + \sum w_{\text{ind}} \right)$.
  * Substrate accumulation ($\widehat{AUC}_{\text{ratio}}$):
    $$\widehat{AUC}_{\text{ratio}}(s) = \frac{1}{\sum (f_m(s, e) \cdot C_e) + (1 - \sum f_m(s, e))}$$
  * Trigger: Narrow therapeutic index + $\widehat{AUC}_{\text{ratio}} \ge 2.0 \implies$ Level 1 Absolute Contraindication.
* **Organ Toxicity Vectors:**
  * QTc Prolongation: $S_{QTc} = \sum (QTc_{\text{base}}(k) \cdot \max(1.0, \widehat{AUC}_{\text{ratio}}(k))) + K_{\text{hypokalemia}}$. Threshold $S_{QTc} \ge 6.0 \implies$ Level 1.
  * Nephrotoxicity & "Triple Whammy": Boolean detector on $\mathcal{P}$ for RAS Blocker + Diuretic + NSAID. If $\text{eGFR} < 60 \implies$ Level 1.
  * CNS Depression: Aggregate score $L_{CNS} \ge 5.0 \implies$ Level 2.
* **Clinical Clearance & Renal Dosing:**
  * CKD-EPI 2021 equation without race coefficient.
* **Geriatric & Pharmacogenomic Safeguards:**
  * Beers 2023 / STOPP/START v3 rules.
  * CPIC Level 1A guidelines: HLA-B*57:01 (Abacavir), CYP2C19 (Clopidogrel), TPMT/NUDT15 (Azathioprine).

### 3.7 Exam Simulator & Educational Engine
* **4 Clinical Item Types:**
  1. Multiple Choice Questions (MCQ) with 4 options and KaTeX math/formula support.
  2. Blind Visual Diagnostics & Image Hotspots: Spatial ray-casting algorithm (Even-Odd rule) on polygonal coordinates.
  3. Open Assessment with NLI Cross-Encoder: Evaluates free-text clinical responses using `all-MiniLM-L6-v2` or `cross-encoder/nli-deberta-v3-small` ONNX INT8, breaking student text into atomic clinical concepts and scoring Entailment vs Contradiction.
  4. Sequential Clinical Case (Stateful DAG): Directed acyclic graph tracking patient state, dynamic vitals, therapeutic choices, and terminal scoring.
* **FSRS v4/v5 Spaced Repetition Scheduler:**
  * Variables: Stability $S$, Difficulty $D$, Target Retention $R = 0.90$.
  * Review Grades: Again ($G=1$), Hard ($G=2$), Good ($G=3$), Easy ($G=4$).
  * Interval: $I(r, s) = 9 \cdot S \cdot (1/R - 1)$.
  * Mitigates "Review Hell" via load balancing and exam-date prioritization ($T_{\text{exam}}$).

### 3.8 Server-Driven UI (SDUI) & React Frontend
* **Frontend Architecture:** React 19 + TypeScript + Vite + TailwindCSS running inside WebView2.
* **Persistent Store:** Zustand store maintaining view and tab state across navigation (zero loss of entered data).
* **The 4 Fundamental SDUI Blocks:**
  1. `ClinicalSheetBlock` (MarkdownBlock): Static monograph with severity-coded callouts (`RED_FLAG`, `CONTRAINDICATION`, etc.).
  2. `SymptomMatcherBlock` (DifferentialDiagnosisBlock): Differential ranking, probability radar charts, and interactive symptom nodes.
  3. `DrugSafetyBlock`: 4-level interaction matrices, CYP450 dial gauges, clearance indicators.
  4. `ExamSimulatorBlock` (ClinicalExamBlock): MCQ renderer, SVG hotspot canvas, DAG scenario stepper.
* **Bounded Windowing & WebGL Broker:** Virtualized DOM list limiting mounted nodes to $< 30$ elements ($< 100\text{ MB}$ RAM) and singleton WebGL context manager.

### 3.9 Agentic API Implementation
* **Host:** FastAPI sidecar listening on `127.0.0.1`.
* **Endpoints:**
  * `GET /agent/health`: Liveness probe, memory RSS status, uptime, database handle status.
  * `GET /agent/state`: Complete current application state (active module, loaded patient case, current SDUI blocks).
  * `POST /agent/execute`: Action dispatcher accepting typed JSON commands (navigate, select option, submit findings).
  * `GET /agent/schema`: JSON Schema / OpenAPI specification of all available agent actions.
* **Security:** Ephemeral token validation on all `/agent/*` endpoints.

---

## 4. Systematic Cross-Comparison Matrix (SRS vs PDF vs Plan vs Directives)

| Feature / Domain | PDF (`Pianificazione`) | SRS (`SRS_MedClient`) | Autonomous Plan (`piano`) | Approved Request / Directives | Reconciled Authoritative Specification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Integrity Mode** | Exploratory brainstorming | Formal IEEE specification | Continuous pipeline | Unconditional production rigor (Zero mock/stub/fake) | **100% Production Rigor unconditionally.** Zero mocks, stubs, fakes, or placeholders across all modules. |
| **SDUI Block Naming** | `MarkdownBlock`, `DifferentialBlock`, `FlowchartBlock`, `InteractiveExamBlock` | `ClinicalSheetBlock`, `SymptomMatcherBlock`, `DrugSafetyBlock`, `ExamSimulatorBlock` | `MarkdownBlock`, `DifferentialDiagnosisBlock`, `InteractiveFlowchartBlock`, `ClinicalExamBlock` | "React SDUI a 4 blocchi tipizzati" | **Canonical schemas: `ClinicalSheetBlock`, `SymptomMatcherBlock`, `DrugSafetyBlock`, `ExamSimulatorBlock`.** Component registry exposes type aliases for both terminologies. |
| **PyHPO Integration** | Explicitly recommended in MedFactory for HPO graph parsing | Implicit in HPO schema DDL and tables; package name omitted in text | Required in `medfactory/pyproject.toml` | Explicitly required in MedFactory (R2) | **Authoritative in MedFactory build pipeline.** Used to ingest and compile HPO ontologies into SQLite tables. |
| **Vector Search vs SQLite FTS5** | Mentions ChromaDB vs FAISS; proposes ChromaDB with LRU cache | Modulo 2.2 mentions ChromaDB HNSW SQ8 for Deep Path; Modulo 2.1 mentions SymSpell + SQLite Inverted Dict + ONNX | Task 3.4 specifies SymSpell + Inverted Dict + ONNX INT8 (`all-MiniLM-L6-v2`) | Query latency < 50ms, RSS < 300MB | **Hybrid: SQLite FTS5 + ONNX INT8 cosine search.** No standalone ChromaDB server on client. MedFactory embeds chunks; client uses in-memory vector array + SQLite. |
| **Zstandard Dictionary Size** | Mentioned generally as custom dictionary | Exactly 114,688 Bytes (112 KB = $112 \times 1024$ B) | Task 1.4: "112 KB" | Explicitly required: "112KB dictionary" | **Exactly 114,688 Bytes (112 KB).** Trained at Level 19 in MedFactory; decompressed at $\ge 1.2\text{ GB/s}$ in MedClient. |
| **Hashing & Integrity Checks** | SHA-256 mentioned in code snippets | BLAKE3 for chunks/files, SHA-256 for DDL, Ed25519 for manifest | BLAKE3 for medpack integrity | SHA-256 cryptographic checksums | **Dual hashing: BLAKE3 for high-throughput stream integrity, SHA-256 in SQL tables and manifest, Ed25519 for signature.** |
| **SQLite DB Names & Swap** | `module_kb.sqlite`, `user_state.sqlite` | `master_knowledge_blue.sqlite`, `green.sqlite`, `user_state.sqlite` | `module_kb.sqlite`, Blue/Green swap | SQLite WAL Blue/Green swap | **Knowledge Base: `module_kb_blue.sqlite` / `module_kb_green.sqlite` with `current_kb.txt` pointer. User State: `user_state.sqlite` in `userdata/`.** |
| **IPC Port & Secret Delivery** | Discussed loopback token | Dinamica porta + stdin token + `X-Tauri-IPC-Secret` | stdin UUIDv4 token + `X-Tauri-IPC-Secret` | Token effimero su loopback 127.0.0.1 | **Dynamic ephemeral port (`127.0.0.1:0`), UUIDv4 token via `stdin`, header `X-Tauri-IPC-Secret`.** |
| **Process Lifecycle & Kill** | Mentioned auto-kill | Win32 Job Objects (`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`) | Win32 Job Objects + Python watchdog | No orphan processes permitted | **Dual protection: Win32 Job Object in Tauri host + `WaitForSingleObject` reverse watchdog thread in Python.** |
| **Asset Streaming Protocol** | WebP local images | `med-asset://` custom protocol via `memmap2` zero-copy | `med-asset://` mmap zero-copy | `med-asset://` zero-copy mmap protocol | **Custom `med-asset://` scheme registered in Tauri v2, backed by `memmap2::Mmap` (`MapViewOfFile`).** |
| **NLI & Embedding Model** | `all-MiniLM-L6-v2` / `bge-micro` | `all-MiniLM-L6` / `bge-m3` INT8 / `nli-deberta-v3-small` | `all-MiniLM-L6-v2` ONNX INT8 | Strict production constraints (<300MB RSS) | **`all-MiniLM-L6-v2` quantized to INT8 (ONNX runtime CPU).** Model size $\approx 23\text{ MB}$, RSS footprint $\le 60\text{ MB}$. |
| **Source Code Modularity** | Micro-files proposed | Extensive modular breakdown | 300-line limit per file | Max 300-450 lines per file partitioned in `interfaces/`, `base/`, `implementations/` | **Strict 300-450 line limit per file, structured in `interfaces/`, `base/`, `implementations/`.** |
| **Secrets Management** | Mentioned OS keystore | Mentioned OS vault | Not detailed | DPAPI Windows (`CryptProtectData`) mandatory | **Windows DPAPI (`CryptProtectData` / `CryptUnprotectData`) for all persisted secrets and tokens.** |
| **Subprocess Execution** | Generic subprocess | Explicit argument vectors | Explicit process commands | Subprocess without `shell=True` mandatory | **Strict `shell=False` with explicit argument lists (`argv`) across all Python and Rust invocations.** |

---

## 5. Register of Operational Assumptions (Authoritative Resolutions)

This register resolves all identified ambiguities, gaps, and discrepancies into binding operational specifications for autonomous implementation:

### ROA-01: Authority of SRS Iteration 2
* **Finding:** `SRS_MedClient_Architettura_Completa.md` contains an initial partial draft (lines 10–1254) followed by a complete, deep specification (lines 1255–6916).
* **Operational Assumption:** Lines 1255–6916 represent the definitive architectural and engineering specification. All Pydantic models, mathematical equations, and DDL schemas are taken from this second iteration, preserving the system overview from Iteration 1.

### ROA-02: SDUI Block Contract Parity & Aliasing
* **Finding:** Block names differ between the Autonomous Plan (`MarkdownBlock`, `DifferentialDiagnosisBlock`, `InteractiveFlowchartBlock`, `ClinicalExamBlock`) and SRS Modulo 4.3 (`ClinicalSheetBlock`, `SymptomMatcherBlock`, `DrugSafetyBlock`, `ExamSimulatorBlock`).
* **Operational Assumption:** The backend FastAPI sidecar emits the canonical SRS names (`ClinicalSheetBlock`, `SymptomMatcherBlock`, `DrugSafetyBlock`, `ExamSimulatorBlock`). The React frontend component registry accepts both canonical names and legacy aliases (`MarkdownBlock` $\to$ `ClinicalSheetBlock`, `DifferentialDiagnosisBlock` $\to$ `SymptomMatcherBlock`, `InteractiveFlowchartBlock` $\to$ `ExamSimulatorBlock`, `ClinicalExamBlock` $\to$ `ExamSimulatorBlock`), ensuring 100% contract parity without breaking either specification.

### ROA-03: Vector Search Architecture on Edge Client (<300MB RSS)
* **Finding:** SRS Modulo 2.2 references ChromaDB HNSW SQ8, while Modulo 2.1 and the Plan specify SymSpell + Inverted Dictionary + ONNX INT8, and user directives restrict MedClient RSS to $< 300\text{ MB}$. Running a full ChromaDB server inside the client would consume $> 200\text{ MB}$ RSS.
* **Operational Assumption:** ChromaDB is utilized exclusively in MedFactory during build-time to validate embeddings and generate index files. On MedClient, vector similarity search is performed in-process using ONNX Runtime INT8 (`all-MiniLM-L6-v2`) with cosine similarity computed over pre-extracted vector embeddings stored as BLOBs in SQLite or a compact memory buffer, keeping memory usage $< 48\text{ MB}$.

### ROA-04: PyHPO Scoping & Ingestion Boundary
* **Finding:** PyHPO is explicitly mandated in `ORIGINAL_REQUEST.md` and the PDF, but absent as a package reference in the SRS body.
* **Operational Assumption:** PyHPO is installed and executed strictly inside `medfactory`. It handles parsing of HPO OBO files, computes information content and semantic similarity graphs, and exports relational tables (`clinical_hpo`, `rel_icd10_hpo`) into `module_kb.sqlite`. MedClient does not import PyHPO at runtime; it queries the pre-computed tables and CSR matrices.

### ROA-05: Zstandard Dictionary Exact Byte Size & Training
* **Finding:** SRS mentions 114,688 Bytes (112 KB), while some text references say 112 KB.
* **Operational Assumption:** The exact dictionary buffer allocation is $112 \times 1024 = 114,688\text{ Bytes}$. MedFactory trains the dictionary using `zstandard.train_dictionary(dict_size=114688, ...)` on a 10% stratified corpus. The dictionary is embedded in the `.medpack` archive as `zstd.dict`.

### ROA-06: Dual Hashing Strategy (BLAKE3 + SHA-256)
* **Finding:** User directives emphasize SHA-256 checksums, while the Plan and SRS emphasize BLAKE3 for fast asset verification.
* **Operational Assumption:** MedFactory computes both BLAKE3 and SHA-256 for all artifacts. `manifest.json` contains both hashes for each file. MedClient uses BLAKE3 for high-speed streaming verification during archive extraction and SHA-256 for database row-level verification and audit logs.

### ROA-07: SQLite Blue/Green Swap Mechanism on Windows
* **Finding:** Symbolic links on Windows often require elevated privileges (Developer Mode or SeCreateSymbolicLinkPrivilege).
* **Operational Assumption:** Blue/Green swap on Windows utilizes an atomic file-replacement approach: a pointer file `master_knowledge.current` contains the active slot string (`"blue"` or `"green"`). Staging writes to the alternate file (e.g. `module_kb_green.sqlite`). Once validated, the pointer file is updated atomically using Win32 `MoveFileExW` with `MOVEFILE_REPLACE_EXISTING`. The SQLite connection pool detects pointer change and gracefully migrates connections.

### ROA-08: IPC Dynamic Port & Secret Passing
* **Finding:** Fixed ports (e.g. 8000) introduce port collisions if another service is running.
* **Operational Assumption:** Tauri binds `127.0.0.1:0`, retrieves the allocated ephemeral port, passes `--port <port>` to the Python sidecar process, and pipes a cryptographically generated UUIDv4 token via `stdin`. All client requests include `X-Tauri-IPC-Secret`.

### ROA-09: Agentic API Scope & Security
* **Finding:** Agentic API endpoints (`/agent/health`, `/agent/state`, `/agent/execute`, `/agent/schema`) must be exposed without creating security vulnerabilities.
* **Operational Assumption:** The Agentic API is implemented as a dedicated router inside the FastAPI sidecar, bound strictly to `127.0.0.1`. It requires authentication via the same ephemeral token (`X-Tauri-IPC-Secret` or `Authorization: Bearer <token>`). It publishes full JSON schemas for automated agents to observe state and execute actions deterministically.

### ROA-10: Educational Engine NLI Model Selection
* **Finding:** SRS mentions `all-MiniLM-L6` and `nli-deberta-v3-small`.
* **Operational Assumption:** The primary NLI model packaged for MedClient is `all-MiniLM-L6-v2` quantized to INT8 via ONNX Runtime. It consumes $< 25\text{ MB}$ disk space and $< 60\text{ MB}$ RAM, executing cross-encoder inference on CPU within $< 35\text{ ms}$ per sentence pair.

---

## 6. Comprehensive Feature Inventory Table

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|---|---|---|---|---|---|---|
| 1 | MedFactory | Docling DLA Pipeline | High-fidelity Document Layout Analysis extracting text, bounding boxes, and tables | PDF document path | Structured GFM Markdown + layout JSON | Raises `DLAExtractionError` on corrupt or unreadable PDF | SRS Modulo 1.2 / 3.1 |
| 2 | MedFactory | Multi-Column Anti-Cross-Talk | Topological slicing that sorts reading flow vertically within detected columns | Document layout bounding boxes | Ordered reading-flow blocks | Logs warning and falls back to single-column topological sort | SRS Modulo 1.2 / 3.1 |
| 3 | MedFactory | Complex Table Normalizer | Reconstructs merged headers, `rowspan`, and `colspan` into valid Markdown tables | Table cells and coordinates | GFM Markdown table | Raises `TableMalformedError` on unbalanced cell matrix | SRS Modulo 1.2 / 3.1 |
| 4 | MedFactory | Medical Unit Guard | Regex/Lexical sanitizer preventing OCR unit corruption ($\mu\text{g} \leftrightarrow \text{mg}$) | Raw extracted text | Sanitized text with validated units | Emits warning on ambiguous dosage string | PDF Page 20 / SRS Modulo 1.2 |
| 5 | MedFactory | Parent-Child Chunking | Hierarchical text chunking (800–1200 / 150–250 tokens) | Normalized Markdown text | Parent and child chunk records | Truncates at nearest sentence boundary if token limit exceeded | SRS Modulo 1.2 / 3.2 |
| 6 | MedFactory | Breadcrumb Context Injection | Prepends `# {Discipline} > {Subspecialty} > {Pathology} > {Section}` to child chunks | Chunk text + document taxonomy | Context-enriched child chunk | Defaults to top-level discipline if subsection absent | SRS Modulo 1.2 / 3.2 |
| 7 | MedFactory | PyHPO Ontology Ingestion | Ingests HPO graphs and computes semantic distances between clinical terms | `hp.obo`, `phenotype.hpoa` | SQLite tables `clinical_hpo`, `rel_icd10_hpo` | Raises `OntologyParseError` on missing ontology source | PDF Page 31 / Plan Task 1.1 |
| 8 | MedFactory | ICD-10 & ATC Ingestion | Ingests WHO ICD-10-CM and AIFA/WHO ATC Level 5 classification data | Official ICD/ATC data files | SQLite tables `clinical_icd10`, `clinical_atc` | Raises `SchemaValidationError` on malformed record | SRS Modulo 1.1 / PDF Page 28 |
| 9 | MedFactory | Zstandard 112KB Dict Trainer | Trains a 114,688-byte custom clinical dictionary on 10% stratified corpus | Corpus text samples | 114,688-byte binary dictionary file | Raises `DictionaryTrainingError` if sample corpus $< 1\text{ MB}$ | SRS Modulo 1.2 / 1.3 |
| 10 | MedFactory | Static Markdown Synthesizer | Synthesizes encyclopedic disease monographs with embedded callouts | Clinical entity data + taxonomy | Valid CommonMark file | Raises `SynthesisValidationError` on invalid callout syntax | SRS Modulo 2.2 / PDF Page 54 |
| 11 | MedFactory | SQLite KB Builder | Compiles `module_kb.sqlite` with saturated B-Tree indexes and `VACUUM INTO` | Entity tables and chunks | Deterministic SQLite database file | Raises `DatabaseBuildError` on index or DDL failure | SRS Modulo 1.2 / 3.4 |
| 12 | MedFactory | `.medpack` Assembler | Packages `.tar.zst` archive with `manifest.json`, dictionary, DB, and assets | Artifact directory | Valid `.medpack` archive with Ed25519 signature | Raises `PackagingError` on checksum mismatch | SRS Modulo 1.2 / Plan Task 1.6 |
| 13 | MedClient | Tauri v2 Host Process | Rust desktop host managing window lifecycle and native system hooks | Application start command | Desktop GUI Window | Terminates with non-zero exit code on fatal init error | SRS Modulo 2.1 / Plan Task 2.1 |
| 14 | MedClient | Jemalloc Memory Tuner | Configures `tikv-jemallocator` with `dirty_decay_ms = 1000` to constrain RSS | Global Rust allocator config | Controlled heap allocation $< 25\text{ MB}$ | Falls back to system allocator if jemalloc unavailable | SRS Modulo 1.1 / 2.1 |
| 15 | MedClient | Win32 Job Object Supervisor | Binds child processes to Win32 Job Object with kill-on-close policy | Child process handles | Automatic child process termination | Logs system error code if Job Object assignment fails | SRS Modulo 2.2 / Plan Task 2.2 |
| 16 | MedClient | Reverse Watchdog Thread | Background thread in Python waiting on parent process PID handle | Parent PID | Clean `os._exit(0)` on parent termination | Forces instant exit if wait handle fails | SRS Modulo 2.2 / Plan Task 3.7 |
| 17 | MedClient | Throttling State Machine | Monitors RSS and memory thresholds (`Normal`, `Constrained`, `Critical`) | OS memory metrics | State transition events and load shedding | Drops caches and triggers GC when threshold exceeded | SRS Modulo 1.1 / 5.1 |
| 18 | MedClient | Ephemeral IPC Handshake | Dynamically binds port and exchanges UUIDv4 token via `stdin` | OS ephemeral port allocation | Authenticated IPC channel on `127.0.0.1` | Aborts startup if token read times out | SRS Modulo 1.3 / Plan Task 2.3 |
| 19 | MedClient | Custom `med-asset://` Protocol | Tauri protocol streaming media from disk to WebView2 via `memmap2` | Asset URI (`med-asset://...`) | HTTP 200 Stream with binary image payload | Returns HTTP 404 on missing file; HTTP 403 on invalid path | SRS Modulo 1.3 / Plan Task 2.4 |
| 20 | MedClient | SQLite WAL Read-Only Pool | High-concurrency SQLite connection pool with 256MB mmap | Database file path | Executable query cursor | Raises `DatabaseLockedError` if lock cannot be acquired | SRS Modulo 1.4 / Plan Task 3.3 |
| 21 | MedClient | SQLite Blue/Green Hot Swap | Atomic pointer swap mechanism between `blue` and `green` database instances | New `.medpack` archive | Zero-downtime database instance switch | Rolls back to active slot if verification fails | SRS Modulo 1.4 / PDF Page 40 |
| 22 | MedClient | SymSpell Medical Spellchecker | Symmetric delete typo tolerance ($d \le 2$) over 285k medical lemmata | Query string | Corrected medical lemma candidates | Returns original string if no candidate exceeds threshold | SRS Modulo 2.1 / Plan Task 3.4 |
| 23 | MedClient | Inverted Lexical Dictionary | Fast lexical mapping of colloquial terms to HPO/ICD-10 ontologies | Normalized text | Ontological node references | Passes through to Stage 3 if no lexical match | SRS Modulo 2.1 / Plan Task 3.4 |
| 24 | MedClient | ONNX INT8 Semantic Embedding | In-process vector embedding generation via quantized `all-MiniLM-L6-v2` | Query tokens | 384-dimensional dense vector | Raises `InferenceError` on invalid tensor shape | SRS Modulo 2.1 / Plan Task 3.4 |
| 25 | MedClient | Red Flags Interceptor | Evaluates Shock Index, qSOFA, and NEWS2 thresholds | Vital signs and physiological findings | `RedFlagsAssessment` alert | Triggers immediate short-circuit emergency warning | SRS Modulo 3.1 / Plan Task 3.5 |
| 26 | MedClient | Sparse CSR Log-Odds Matcher | Computes probabilistic disease ranking using in-memory CSR matrices | Observed symptoms vector $\mathbf{x}_{\text{obs}}$ | Differential diagnosis candidates with scores | Applies Dirichlet smoothing to avoid zero-probability | SRS Modulo 3.1 / Plan Task 3.5 |
| 27 | MedClient | Pertinent Negatives Rule-Out | Severe penalty detraction for absent mandatory disease manifestations | Negative findings set $S^-$ | Updated disease logits with rule-outs | Forces logit to $-\infty$ if mandatory feature is refuted | SRS Modulo 3.1 / Plan Task 3.5 |
| 28 | MedClient | Log-Sum-Exp Softmax Normalizer | Numerically stable probability normalizer preventing floating-point overflow | Raw disease logits vector $\mathbf{z}$ | Posterior probability distribution | Stable evaluation via max-logit subtraction | SRS Modulo 3.1 / Plan Task 3.5 |
| 29 | MedClient | Active Discrimination (NBQ) | Next-Best-Question selector maximizing information gain per cost | Top-2 candidate diseases | Optimal uninvestigated feature $f^*$ | Returns null if candidates are conclusively separated | SRS Modulo 3.1 / Plan Task 3.5 |
| 30 | MedClient | CYP450 Functional Load Engine | Multi-way drug interaction engine modeling 5 core CYP450 isoenzymes | List of prescribed ATC codes | Residual clearance $C_e$ and AUC ratios | Emits Level 1 alert on narrow therapeutic index violation | SRS Modulo 3.2 / Plan Task 3.6 |
| 31 | MedClient | QTc Interval Prolongation Guard | Cumulative cardiac arrhythmia risk evaluator based on CredibleMeds | Drug list + serum potassium | Cumulative $S_{QTc}$ score and warning | Flags Level 1 if $S_{QTc} \ge 6.0$ or hypokalemia present | SRS Modulo 3.2 / Plan Task 3.6 |
| 32 | MedClient | "Triple Whammy" Detector | Deterministic detector for RAS blocker + Diuretic + NSAID co-prescription | Drug list + patient eGFR | Nephrotoxicity alert and Beers criteria match | Emits Level 1 alert if $\text{eGFR} < 60$ | SRS Modulo 3.2 / Plan Task 3.6 |
| 33 | MedClient | CKD-EPI 2021 Renal Calculator | Computes estimated glomerular filtration rate without race coefficient | Age, sex, serum creatinine | eGFR value in $\text{mL/min/1.73m}^2$ | Raises `ValidationError` on out-of-bound physiological inputs | SRS Modulo 3.2 / Plan Task 3.6 |
| 34 | MedClient | Pharmacogenomics Rule Engine | CPIC Level 1A actionable guideline matcher (HLA-B*57:01, CYP2C19, TPMT) | Patient diplotype + prescribed drugs | Contraindication / dosage adjustment rule | Emits Level 1 absolute contraindication on positive match | SRS Modulo 3.2 / Plan Task 3.6 |
| 35 | MedClient | MCQ Assessment Engine | Renders and evaluates 4-choice clinical questions with KaTeX support | Option selection | Score, rationale, and explanation | Rejects submission if option ID is invalid | SRS Modulo 4.1 / Plan Task 4.3 |
| 36 | MedClient | Visual Hotspot Evaluator | Evaluates blind diagnostic clicks on clinical images via ray-casting | $(x, y)$ coordinate click | Hit/Miss determination on polygon region | Logs click outside boundary as incorrect answer | SRS Modulo 4.1 / Plan Task 4.3 |
| 37 | MedClient | NLI Cross-Encoder Evaluator | Natural Language Inference scoring student answers against atomic concepts | Free-text response + concept rubrics | Entailment / Contradiction scores | Fallback to keyword matching if NLI model unavailable | SRS Modulo 4.1 / Plan Task 3.4 |
| 38 | MedClient | Stateful DAG Clinical Simulator | Multi-step interactive clinical scenario with branching patient states | Clinical action / order | Transitioned state + updated patient vitals | Terminates case with adverse outcome on critical error | SRS Modulo 4.1 / Plan Task 4.3 |
| 39 | MedClient | FSRS Mnemonic Scheduler | Free Spaced Repetition Scheduler computing memory stability and review intervals | Card review grade ($G \in \{1, 2, 3, 4\}$) | Updated stability $S$, difficulty $D$, next date | Clamps difficulty to $[1.0, 10.0]$ on extreme grades | SRS Modulo 4.2 / Plan Task 4.3 |
| 40 | MedClient | Review Hell Mitigation | Spaced repetition load balancer preventing review backlog collapse | Due review queue + target exam date | Daily review batch balanced to capacity | Prioritizes high-lapse items when queue exceeds cap | SRS Modulo 4.2 / Plan Task 4.3 |
| 41 | MedClient | SDUI Dumb Painter Dispatcher | React client rendering typed server blocks dynamically at 60 FPS | SDUI Payload envelope | Rendered interactive UI tree | Logs warning and renders error boundary on unknown block | SRS Modulo 4.3 / Plan Task 4.3 |
| 42 | MedClient | Bounded Windowing Manager | Virtualized DOM list limiting mounted nodes to $< 30$ active elements | Dynamic item stream | Virtual viewport DOM elements | Automatically evicts off-screen elements | SRS Modulo 4.3 / Plan Task 4.3 |
| 43 | MedClient | WebGL Singleton Broker | Centralized manager acquiring and releasing WebGL contexts safely | Canvas mount requests | Active WebGL context pointer | Gracefully falls back to 2D SVG canvas if WebGL fails | SRS Modulo 4.3 / Plan Task 4.3 |
| 44 | MedClient | Persistent Zustand Store | Global client state store preserving tabs, draft inputs, and form states | State mutation actions | Preserved UI state across tab switching | Automatically persists state to localStorage | Plan Task 4.2 / PDF Page 52 |
| 45 | MedClient | Agentic API Health & State | Endpoints `/agent/health` and `/agent/state` exposing runtime telemetry | HTTP GET with auth token | JSON status, RSS memory, and UI state | Returns HTTP 401/403 on missing/invalid token | ORIGINAL_REQUEST.md / Agentic Rule |
| 46 | MedClient | Agentic API Action Executor | Endpoint `/agent/execute` allowing autonomous action execution | Typed action JSON payload | Execution result and updated state | Returns HTTP 422 on invalid action schema | ORIGINAL_REQUEST.md / Agentic Rule |
| 47 | MedClient | Agentic API Schema Publisher | Endpoint `/agent/schema` publishing OpenAPI / JSON Schemas for AI agents | HTTP GET with auth token | OpenAPI 3.1 JSON document | Returns HTTP 401/403 on missing/invalid token | ORIGINAL_REQUEST.md / Agentic Rule |
| 48 | MedClient | Windows DPAPI Secret Vault | Encrypts and decrypts persisted secrets using Win32 `CryptProtectData` | Plaintext token or secret bytes | Protected ciphertext BLOB | Raises `DPAPIError` if DPAPI call fails | ORIGINAL_REQUEST.md / Security Rule |

---

## 7. Edge Cases & Boundary Conditions Register

| # | Feature | Input / Condition | Expected Behavior | Verification Criterion |
|---|---|---|---|---|
| 1 | Docling DLA | Corrupted PDF with malformed xref table | Abort document processing cleanly with `DLAExtractionError` without crashing the pipeline process | Process exit code is non-zero with diagnostic log; no unhandled exception |
| 2 | Table Normalizer | Table with inconsistent cell count across rows (irregular matrix) | Detect unbalanced row/col structure, pad missing cells with empty strings, log warning | Table renders valid GFM without shifting columns |
| 3 | Medical Unit Guard | String containing `"10 ug"` or `"10 µg"` | Normalize unicode micro sign `µ` and ASCII `u` to standard `mcg` or `mg` with explicit confirmation | No silent conversion between micrograms and milligrams |
| 4 | Zstd Dict Trainer | Corpus sample with repetitive or sparse tokens ($< 1\text{ MB}$) | Raise `DictionaryTrainingError` indicating insufficient variance; refuse to train degenerate dict | Compression ratio does not regress; pipeline blocks until corpus is valid |
| 5 | `.medpack` Extraction | Archive with modified or corrupted BLAKE3 checksum | Abort extraction immediately before database staging; do not touch active database | Existing database remains 100% untouched; staging file removed |
| 6 | IPC Handshake | Client attempts connection without `X-Tauri-IPC-Secret` header | FastAPI middleware intercepts request and returns HTTP 403 Forbidden | Request does not hit route handler; security audit event logged |
| 7 | Sidecar Process | Tauri host killed abruptly via `taskkill /F` or Task Manager | Win32 Job Object and Python `WaitForSingleObject` watchdog terminate Python within 500ms | No orphan `python.exe` process left in Windows Task Manager |
| 8 | Memory Watchdog | MedClient RSS approaches 275 MB | State machine switches to `Critical`, drops image cache, forces GC, and limits DOM nodes | RSS stabilizes $< 300\text{ MB}$; process avoids OS OOM kill |
| 9 | `med-asset://` | Request URL path contains traversal characters (`../..`) | Rust handler sanitizes and canonicalizes path, rejecting any path outside media vault with 403 | Prevents arbitrary local file disclosure |
| 10 | SQLite Blue/Green | Database swap triggered while an active analytical query is executing | Active query completes on existing read connection; new incoming queries open on new slot | Zero query exceptions; zero database locked errors |
| 11 | Red Flags Engine | Patient with $\text{HR} = 120\text{ bpm}$ and $\text{SBP} = 90\text{ mmHg}$ ($SI = 1.33$) | Trigger immediate Code Red shock alert; short-circuit probabilistic log-odds evaluation | Alert appears on screen in $< 5\text{ ms}$; standard matcher suppressed |
| 12 | Log-Odds Engine | Symptom with zero empirical frequency in corpus ($C(f_i, d_j) = 0$) | Dirichlet smoothing with $\epsilon = 10^{-4}$ calculates regularized non-zero probability | No division by zero; no $\ln(0)$ floating-point exception |
| 13 | Pertinent Negatives | Mandatory disease feature marked as refuted ($f_i \in S^-$ and $P > 0.99$) | Assign $-\infty$ weight detraction; candidate disease completely ruled out from differential | Disease score drops to bottom of candidate list with 0% probability |
| 14 | Log-Sum-Exp | Extreme logit values ($z_j > 800$) that exceed standard IEEE 754 float | Subtract $c = \max z_k$ prior to exponentiation; compute exact stable Softmax | No IEEE 754 overflow to `+Infinity` or `NaN` |
| 15 | Active Discrimination | Top-2 diseases have identical phenotypic profiles (no differentiating feature) | Detect empty $\mathcal{U}_{\text{eval}}$; return null NBQ and flag diagnostic ambiguity | System does not enter infinite loop; informs clinician of tied differential |
| 16 | CYP450 Engine | Combination of Strong Inhibitor and Strong Inducer on same isoenzyme | Algebraic cancellation of weights: $C_e = \max(0.05, 1.0 - 0.8 + 1.0) = 1.20$ | Resulting clearance reflects net physiological kinetic state |
| 17 | Organ Toxicity | Triple Whammy co-prescription in patient with $\text{eGFR} = 45\text{ mL/min}$ | Detect ACEi + Diuretic + NSAID; emit Level 1 Contraindication for acute renal failure | Prescribing blocked; alternative non-nephrotoxic analgesic suggested |
| 18 | Pharmacogenomics | Patient with `HLA-B*57:01` prescribed Abacavir (`J05AF06`) | Immediate Level 1 Absolute Contraindication triggered for fatal hypersensitivity | Hard stop in UI; alternative antiretroviral regimen displayed |
| 19 | Visual Hotspot | User clicks directly on edge boundary vertex of polygon | Ray-casting algorithm handles vertex singularity using standard Even-Odd ray rules | Deterministic Hit/Miss result without floating-point error |
| 20 | NLI Cross-Encoder | Student provides clinical response with negation ("paziente NON presenta dispnea") | NLI model classifies premise-hypothesis relationship as Contradiction | Score penalizes negated concept; avoids false-positive credit |
| 21 | FSRS Scheduler | First review of a card ($reps = 0$) graded "Again" ($G = 1$) | Initialize with base lapse parameters; stability set to minimum threshold $S_0(1)$ | Next review scheduled for immediate repeat batch; difficulty increases |
| 22 | Review Queue | Student returns after 6 months with 1,500 overdue cards ("Review Hell") | Daily batch caps reviews to user daily limit; prioritizes high-lapse and exam-relevant cards | Prevents student burnout; smoothly distributes backlog across schedule |
| 23 | SDUI Rendering | Server sends unknown component type string (e.g. `"NewExperimentalBlock"`) | React SDUI registry catches unrecognized type, renders fallback Error Boundary | Application does not crash; other valid blocks render normally |
| 24 | Agentic API | Action sent to `/agent/execute` with missing mandatory parameters | Pydantic schema validation intercepts payload, returns HTTP 422 with exact field error | Runtime state remains uncorrupted; caller receives actionable JSON error |
