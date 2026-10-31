# Handoff Report: Specification Mining & Operational Assumptions Register

**Agent:** `spec_miner_1` (Role: Spec Miner & Assumptions Lead)  
**Parent Orchestrator:** `123b80e3-ef7e-4eee-9c78-b41caaecc724`  
**Working Directory:** `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\spec_miner_1\`  
**Date:** 2026-10-30  
**Handoff Type:** Hard (Task complete)

---

## 1. Observation

Direct observations and evidence extracted from the reference documents and environment:

1. **Source Documents Inspected:**
   * `SRS_MedClient_Architettura_Completa.md` (Total Lines: 6,916, Total Bytes: 394,408).
   * `Pianificazione App Medica Ibrida.pdf` (Total Pages: 64, Text Dump: 355,498 characters extracted into `.agents/teamwork/spec_miner_1/pdf_text_dump.txt`).
   * `C:\Users\vence\.gemini\antigravity\brain\3aa6efc6-1a77-4cff-b774-120f18a304fb\piano_costruzione_autonoma_medplatform.md` (Total Lines: 140, Total Bytes: 9,490).
   * `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\ORIGINAL_REQUEST.md` (Total Lines: 73).

2. **Dual-Generation Structure in SRS Document:**
   * In `SRS_MedClient_Architettura_Completa.md`, lines 1 to 1254 contain an initial draft of modules (Modulo 1.1, Modulo 1.2, Modulo 1.3).
   * Starting at line 1255, a second, complete and exhaustive generation begins:
     * Line 1255: `## Modulo 1.1: Profilazione Hardware Target, Asimmetria MedFactory/MedClient e Limiti di Risorse`
     * Line 1606: `## Modulo 1.2: Architettura e Creazione dei .medpack (Docling DLA, Chunking Gerarchico e Compressione Zstd)`
     * Line 2155: `## Modulo 1.3: Canale IPC Tauri-FastAPI e Protocollo di Streaming Zero-Copy per i Media Clinici`
     * Line 2638: `## Modulo 1.4: Struttura SQLite Resiliente (Isolamento Fisico, Blue/Green Swap e WAL Recovery)`
     * Line 3269: `## Modulo 2.1: Pipeline NLP Locale a Latenza Zero (SymSpell, Dizionario Inverso e ONNX SQ8)`
     * Line 3664: `## Modulo 2.2: Generazione Schede Statiche Markdown vs Ricerca Vettoriale HNSW su ChromaDB`
     * Line 4118: `## Modulo 3.1: Motore Diagnostico a Stadi (Log-Odds, Rule-Out e Guadagno Informativo)`
     * Line 4558: `## Modulo 3.2: Motore di Sicurezza Farmacologica (Tassonomia a 4 Livelli, Carico CYP450 ed $N$-Way Interactions)`
     * Line 5146: `## Modulo 4.1: Simulatore d'Esame Avanzato (MCQ a 4 Scelte, Hotspot Visivi, NLI Cross-Encoder e Stateful DAG)`
     * Line 5765: `## Modulo 4.2: Algoritmo FSRS e Gestione della Memoria a Lungo Termine (Curva dell'Oblio e Target Retention)`
     * Line 6334: `## Modulo 4.3: Architettura Frontend Server-Driven UI (SDUI), Virtual Windowing e Bounded WebGL`

3. **Discrepancies in SDUI 4-Block Naming:**
   * In `piano_costruzione_autonoma_medplatform.md` (Task 4.3):
     `1. MarkdownBlock, 2. DifferentialDiagnosisBlock, 3. InteractiveFlowchartBlock, 4. ClinicalExamBlock`.
   * In `SRS_MedClient_Architettura_Completa.md` (Modulo 4.3, lines 6430–6520):
     `ClinicalSheetBlock`, `SymptomMatcherBlock`, `DrugSafetyBlock`, `ExamSimulatorBlock`.
   * In `Pianificazione App Medica Ibrida.pdf` (Page 10, Page 52): both sets of nomenclatures are used interchangeably in conversational design sketches.

4. **Vector Search vs SQLite Memory Footprint:**
   * SRS Modulo 2.2 (line 3683) mentions a `ChromaDB Segment (HNSW SQ8)` for deep semantic search.
   * SRS Modulo 2.1 (line 3309) and the Plan specify a 3-stage pipeline: `SymSpell -> Inverted Lexical Dict -> ONNX SQ8 (all-MiniLM-L6)`.
   * User Directives require MedClient total RSS $< 300\text{ MB}$ and query latency $< 50\text{ ms}$ on CPU without GPU. Running an active ChromaDB server in the client sidecar would consume $> 200\text{ MB}$ RSS alone.

5. **PyHPO Presence and Boundaries:**
   * `PyHPO` is mentioned 4 times in `Pianificazione App Medica Ibrida.pdf` (Pages 31, 32, 64) as the library used in MedFactory to query the HPO ontology and generate the relational database.
   * `PyHPO` is not referenced in the body of `SRS_MedClient_Architettura_Completa.md`, which instead defines direct SQL tables (`clinical_hpo`, `rel_icd10_hpo`) and CSR matrices.
   * `PyHPO` is explicitly mandated in `ORIGINAL_REQUEST.md` (R2) and `piano_costruzione_autonoma_medplatform.md` (Task 1.1).

6. **Zstandard Dictionary Size:**
   * In SRS Modulo 1.2 (line 420, line 1650) and Modulo 1.3: explicitly specified as `114.688 Byte (112 KB)`.
   * In `ORIGINAL_REQUEST.md`: "dizionario Zstandard 112KB".

7. **Security and Lifecycle Mechanisms:**
   * Tauri Host: Win32 Job Object with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` (SRS lines 1580, 2200).
   * Python Sidecar: Token received via `stdin` at launch; authenticated header `X-Tauri-IPC-Secret`; reverse watchdog calling `kernel32.WaitForSingleObject` on parent PID.
   * Custom Asset Protocol: `med-asset://` implemented in Rust via `memmap2::Mmap` (`MapViewOfFile` Win32) for zero-copy streaming.
   * Agentic API: Endpoints `/agent/health`, `/agent/state`, `/agent/execute`, `/agent/schema` on loopback `127.0.0.1`.

---

## 2. Logic Chain

1. **Hierarchy of Sources:**
   * User directives in `ORIGINAL_REQUEST.md` override any relaxing phrasing (e.g. "Integrity mode: demo"). Production rigor is absolute (no mocks, no stubs, exact pinned dependencies, strict performance limits).
   * Between the early draft (lines 1–1254) and the full specification (lines 1255–6916) in `SRS_MedClient_Architettura_Completa.md`, the second iteration contains the finalized mathematical models, Pydantic v2 schemas, and DDL tables. Therefore, Iteration 2 is the authoritative implementation reference.

2. **Reconciliation of SDUI Block Schemas:**
   * The front-end needs to render 4 fundamental blocks: Clinical Sheet, Differential Diagnosis/Symptom Matcher, Drug Safety/Interactions, and Exam Simulator/Flowcharts.
   * Emitting the canonical names from SRS Modulo 4.3 (`ClinicalSheetBlock`, `SymptomMatcherBlock`, `DrugSafetyBlock`, `ExamSimulatorBlock`) while allowing the React component registry to map the Plan's names as aliases (`MarkdownBlock`, `DifferentialDiagnosisBlock`, `InteractiveFlowchartBlock`, `ClinicalExamBlock`) guarantees complete contract parity and prevents any `DAGNodeNotFoundError` or unhandled component exceptions.

3. **Reconciliation of Client Memory & Search Architecture:**
   * MedClient has a rigid physical RAM budget of $< 300\text{ MB}$ RSS. Tauri/Rust allocates 25 MB, WebView2 allocates 90 MB, SQLite mmap allocates 64 MB, leaving at most 60 MB for ONNX inference and 45 MB for FastAPI sidecar.
   * A full Python ChromaDB daemon exceeds this budget. MedFactory compiles the embeddings during build-time. MedClient executes fast lexical seeks on SQLite FTS5 ($< 5\text{ ms}$) and semantic vector searches using an embedded ONNX INT8 runtime (`all-MiniLM-L6-v2`, $\approx 23\text{ MB}$ disk footprint, $\le 45\text{ ms}$ CPU latency) over pre-indexed SQLite BLOBs or an in-memory NumPy/SciPy array.

4. **Reconciliation of PyHPO Scope:**
   * Because PyHPO is designed for graph traversal and OBO parsing, its computational weight belongs in `medfactory` at build-time.
   * MedFactory uses PyHPO to ingest `hp.obo`, calculate phenotypic similarities, and compile `clinical_hpo` / `rel_icd10_hpo` into `module_kb.sqlite`.
   * MedClient reads the resulting SQLite tables and loads the CSR matrices directly into memory, achieving $< 1\text{ ms}$ query times with zero runtime dependency on PyHPO.

5. **Operational Assumptions Register Formulation:**
   * 10 explicit Operational Assumptions (ROA-01 through ROA-10) were formulated in `spec_inventory.md` to resolve all potential ambiguities before coding begins, ensuring the autonomous pipeline can proceed without blocking.

---

## 3. Caveats

1. **Network Access for Build-Time Artifacts:** In accordance with R4, network access is required during the initial environment build to download official ontologies (HPO OBO files, ICD-10, ATC datasets) and ONNX model weights (`all-MiniLM-L6-v2` / `docling` DLA weights). Once compiled into `.medpack`, MedClient operates 100% offline.
2. **Windows Platform Specifics:** Certain Win32 APIs (`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, `MapViewOfFile`, `WaitForSingleObject`, `CryptProtectData`) are Windows-specific. The architecture isolates them in platform abstraction layers with standard POSIX fallbacks for portable testing if needed.

---

## 4. Conclusion

1. **Exhaustive Feature Specification Completed:** A complete inventory of 48 features across MedFactory and MedClient has been extracted, covering all mathematical models, DDL schemas, Pydantic contracts, and protocol definitions.
2. **Systematic Discrepancies Resolved:** All discrepancies between the SRS, the PDF planning document, and the autonomous construction plan have been identified and formally reconciled.
3. **Operational Assumptions Established:** 10 binding operational assumptions (ROA-01 to ROA-10) have been documented in `spec_inventory.md` to guide the builder and architect agents without ambiguity.
4. **Zero-Mock & Production Rigor Guaranteed:** The specification inventory enforces real physical implementations for all components, strict memory capping ($< 300\text{ MB}$ RSS), $< 50\text{ ms}$ query latency, zero-copy mmap, and loopback Agentic API.

---

## 5. Verification Method

To independently verify the findings and specifications:

1. **Verify Deliverable Artifacts:**
   * Inspect `spec_inventory.md`:
     ```powershell
     Get-Item "c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\spec_miner_1\spec_inventory.md"
     ```
   * Confirm line count and sections (should contain Executive Summary, MedFactory Inventory, MedClient Inventory, Cross-Comparison Matrix, Register of Operational Assumptions, Feature Inventory Table with 48 items, and Edge Cases Register).

2. **Verify Document Concordance:**
   * Run cross-check script:
     ```powershell
     python "c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\spec_miner_1\analyze_discrepancies.py"
     ```
   * Verify that all 10 ROAs in `spec_inventory.md` map to the respective module lines in `SRS_MedClient_Architettura_Completa.md` and `piano_costruzione_autonoma_medplatform.md`.
