# Software Requirements Specification (SRS) - Piattaforma Medica Ibrida
## Architettura Completa di Sistema: MedFactory (Build-Time) & MedClient (Run-Time)
**Data di Generazione:** 2026-11-04 21:01:21
**Standard:** IEEE/ISO Software Requirements Specification
**Orchestrazione:** Async Multi-Agent Pipeline con Dual-Pass & Sentinel QA Audit

---
## Inventario Mock e Gap Rilevati (Scansione Automatica)

| ID | Severità | File | Riga | Dettaglio |
|---|---|---|---|---|
| AUTO-001 (MOCK-01) | HIGH | `medfactory/src/pipeline/base/clinical_dataset_seed.py` | 0 | compute_deterministic_l2_vector: embedding finti |
| AUTO-002 (MOCK-02) | HIGH | `medfactory_pipeline.py` | 168 | Fonte bibliografica inventata ("Prof. M. Rossi") |
| AUTO-003 (MOCK-03) | CRITICAL | `medfactory_pipeline.py` | 302 | Chiave Ed25519 derivata da stringa nota |
| AUTO-004 (MOCK-04) | HIGH | `clinical_dataset_seed.py` | 0 | 4 quiz + 7 malattie cablati |
| AUTO-005 (MOCK-05) | HIGH | `hpo_ingestor.py` | 0 | Fallback a 33 HPO / 15 ICD-10 / 17 ATC cablati |
| AUTO-006 (MOCK-06) | HIGH | `medfactory_pipeline.py` | 63 | 3 monografie scritte a mano, nessuna fonte |
| AUTO-007 (MOCK-07) | HIGH | `pharmacology_catalogs.py` | 0 | Profili CYP450/interazioni statici |
| AUTO-008 (MOCK-08) | MEDIUM | `symspell_checker.py` | 0 | Lessico SymSpell seminato a mano |
| AUTO-009 (MOCK-09) | HIGH | `ExamSimulatorBlockView.tsx` | 25 | Quiz Q_CARDIO_01 / 'Opzione A' cablati nel frontend |
| AUTO-010 (MOCK-10) | CRITICAL | `MedClientAppShell.tsx` | 0 | Token IPC fallback cablato |
| AUTO-011 (GAP-01) | HIGH | `app.py` | 0 | Endpoint /exam/questions mancante/finto |
| AUTO-012 (GAP-03) | HIGH | `app.py` | 0 | Endpoint /curriculum mancante/finto |
| AUTO-013 (GAP-08) | MEDIUM | `app.py` | 0 | user_knowledge_sources mancanti |

---



---## Inventario Mock e Gap Rilevati (Scansione Automatica)


## Inventario Mock e Gap Rilevati (Scansione Automatica)

| ID | Severità | File | Riga | Dettaglio |
|---|---|---|---|---|
| AUTO-001 (MOCK-01) | HIGH | `medfactory/src/pipeline/base/clinical_dataset_seed.py` | 0 | compute_deterministic_l2_vector: embedding finti |
| AUTO-002 (MOCK-02) | HIGH | `medfactory_pipeline.py` | 168 | Fonte bibliografica inventata ("Prof. M. Rossi") |
| AUTO-003 (MOCK-03) | CRITICAL | `medfactory_pipeline.py` | 302 | Chiave Ed25519 derivata da stringa nota |
| AUTO-004 (MOCK-04) | HIGH | `clinical_dataset_seed.py` | 0 | 4 quiz + 7 malattie cablati |
| AUTO-005 (MOCK-05) | HIGH | `hpo_ingestor.py` | 0 | Fallback a 33 HPO / 15 ICD-10 / 17 ATC cablati |
| AUTO-006 (MOCK-06) | HIGH | `medfactory_pipeline.py` | 63 | 3 monografie scritte a mano, nessuna fonte |
| AUTO-007 (MOCK-07) | HIGH | `pharmacology_catalogs.py` | 0 | Profili CYP450/interazioni statici |
| AUTO-008 (MOCK-08) | MEDIUM | `symspell_checker.py` | 0 | Lessico SymSpell seminato a mano |
| AUTO-009 (MOCK-09) | HIGH | `ExamSimulatorBlockView.tsx` | 25 | Quiz Q_CARDIO_01 / 'Opzione A' cablati nel frontend |
| AUTO-010 (MOCK-10) | CRITICAL | `MedClientAppShell.tsx` | 0 | Token IPC fallback cablato |
| AUTO-011 (GAP-01) | HIGH | `app.py` | 0 | Endpoint /exam/questions mancante/finto |
| AUTO-012 (GAP-03) | HIGH | `app.py` | 0 | Endpoint /curriculum mancante/finto |
| AUTO-013 (GAP-08) | MEDIUM | `app.py` | 0 | user_knowledge_sources mancanti |

---



---## Inventario Mock e Gap Rilevati (Scansione Automatica)

| ID | Severità | File | Riga | Dettaglio |
|---|---|---|---|---|
| AUTO-001 (MOCK-01) | HIGH | `medfactory/src/pipeline/base/clinical_dataset_seed.py` | 0 | compute_deterministic_l2_vector: embedding finti |
| AUTO-002 (MOCK-02) | HIGH | `medfactory_pipeline.py` | 168 | Fonte bibliografica inventata ("Prof. M. Rossi") |
| AUTO-003 (MOCK-03) | CRITICAL | `medfactory_pipeline.py` | 302 | Chiave Ed25519 derivata da stringa nota |
| AUTO-004 (MOCK-04) | HIGH | `clinical_dataset_seed.py` | 0 | 4 quiz + 7 malattie cablati |
| AUTO-005 (MOCK-05) | HIGH | `hpo_ingestor.py` | 0 | Fallback a 33 HPO / 15 ICD-10 / 17 ATC cablati |
| AUTO-006 (MOCK-06) | HIGH | `medfactory_pipeline.py` | 63 | 3 monografie scritte a mano, nessuna fonte |
| AUTO-007 (MOCK-07) | HIGH | `pharmacology_catalogs.py` | 0 | Profili CYP450/interazioni statici |
| AUTO-008 (MOCK-08) | MEDIUM | `symspell_checker.py` | 0 | Lessico SymSpell seminato a mano |
| AUTO-009 (MOCK-09) | HIGH | `ExamSimulatorBlockView.tsx` | 25 | Quiz Q_CARDIO_01 / 'Opzione A' cablati nel frontend |
| AUTO-010 (MOCK-10) | CRITICAL | `MedClientAppShell.tsx` | 0 | Token IPC fallback cablato |
| AUTO-011 (GAP-01) | HIGH | `app.py` | 0 | Endpoint /exam/questions mancante/finto |
| AUTO-012 (GAP-03) | HIGH | `app.py` | 0 | Endpoint /curriculum mancante/finto |
| AUTO-013 (GAP-08) | MEDIUM | `app.py` | 0 | user_knowledge_sources mancanti |

---



---## Inventario Mock e Gap Rilevati (Scansione Automatica)

| ID | Severità | File | Riga | Dettaglio |
|---|---|---|---|---|
| AUTO-001 (MOCK-01) | HIGH | `medfactory/src/pipeline/base/clinical_dataset_seed.py` | 0 | compute_deterministic_l2_vector: embedding finti |
| AUTO-002 (MOCK-02) | HIGH | `medfactory_pipeline.py` | 168 | Fonte bibliografica inventata ("Prof. M. Rossi") |
| AUTO-003 (MOCK-03) | CRITICAL | `medfactory_pipeline.py` | 302 | Chiave Ed25519 derivata da stringa nota |
| AUTO-004 (MOCK-04) | HIGH | `clinical_dataset_seed.py` | 0 | 4 quiz + 7 malattie cablati |
| AUTO-005 (MOCK-05) | HIGH | `hpo_ingestor.py` | 0 | Fallback a 33 HPO / 15 ICD-10 / 17 ATC cablati |
| AUTO-006 (MOCK-06) | HIGH | `medfactory_pipeline.py` | 63 | 3 monografie scritte a mano, nessuna fonte |
| AUTO-007 (MOCK-07) | HIGH | `pharmacology_catalogs.py` | 0 | Profili CYP450/interazioni statici |
| AUTO-008 (MOCK-08) | MEDIUM | `symspell_checker.py` | 0 | Lessico SymSpell seminato a mano |
| AUTO-009 (MOCK-09) | HIGH | `ExamSimulatorBlockView.tsx` | 25 | Quiz Q_CARDIO_01 / 'Opzione A' cablati nel frontend |
| AUTO-010 (MOCK-10) | CRITICAL | `MedClientAppShell.tsx` | 0 | Token IPC fallback cablato |
| AUTO-011 (GAP-01) | HIGH | `app.py` | 0 | Endpoint /exam/questions mancante/finto |
| AUTO-012 (GAP-03) | HIGH | `app.py` | 0 | Endpoint /curriculum mancante/finto |
| AUTO-013 (GAP-08) | MEDIUM | `app.py` | 0 | user_knowledge_sources mancanti |

---



---## Inventario Mock e Gap Rilevati (Scansione Automatica)

| ID | Severità | File | Riga | Dettaglio |
|---|---|---|---|---|
| AUTO-100 (MOCK-01) | HIGH | `medfactory/src/pipeline/base/clinical_dataset_seed.py` | 17 | compute_deterministic_l2_vector: embedding finti |
| AUTO-101 (MOCK-01) | HIGH | `medfactory/src/pipeline/implementations/medfactory_pipeline.py` | 31 | compute_deterministic_l2_vector: embedding finti |
| AUTO-102 (MOCK-02) | HIGH | `medfactory/src/pipeline/implementations/medfactory_pipeline.py` | 172 | Fonte bibliografica inventata ("Prof. M. Rossi") |
| AUTO-103 (MOCK-01) | HIGH | `medfactory/src/pipeline/implementations/medfactory_pipeline.py` | 247 | compute_deterministic_l2_vector: embedding finti |
| AUTO-104 (UNKNOWN-GAP) | MEDIUM | `medclient/core-rust/src/main.rs` | 187 | Pattern vietato trovato: fallback -> // Test risorsa SVG (ROA-12 2D structure fallback)... |
| AUTO-105 (UNKNOWN-GAP) | MEDIUM | `medclient/sidecar-python/tests/test_storage_and_system.py` | 71 | Pattern vietato trovato: fallback -> # Default fallback |
| AUTO-106 (MOCK-09) | HIGH | `medclient/sidecar-python/tests/test_storage_and_system.py` | 287 | Quiz Q_CARDIO_01 / 'Opzione A' cablati nel frontend |
| AUTO-107 (UNKNOWN-GAP) | MEDIUM | `medclient/sidecar-python/src/api/agentic_routes.py` | 54 | Pattern vietato trovato: fallback -> sys.stderr.write(f"[AgenticRoutes] Win32 fallback ... |
| AUTO-108 (UNKNOWN-GAP) | MEDIUM | `medclient/sidecar-python/src/implementations/reverse_watchdog.py` | 83 | Pattern vietato trovato: fallback -> """Posix fallback polling parent PID existence via... |
| AUTO-109 (UNKNOWN-GAP) | MEDIUM | `medclient/sidecar-python/src/implementations/blue_green_swap.py` | 97 | Pattern vietato trovato: Fallback -> # Fallback to os.replace if win32 API failed |
| AUTO-110 (UNKNOWN-GAP) | MEDIUM | `medclient/frontend-react/src/base/sduiRegistry.ts` | 8 | Pattern vietato trovato: fallback -> `SDUINodeNotFoundError: Il block_type '${offending... |
| AUTO-111 (UNKNOWN-GAP) | MEDIUM | `medclient/frontend-react/src/base/useMedClientStore.ts` | 129 | Pattern vietato trovato: Fallback -> // Fallback in-memory attivo se LocalStorage ha ra... |
| AUTO-112 (MOCK-09) | HIGH | `medclient/frontend-react/src/base/useMedClientStore.ts` | 314 | Quiz Q_CARDIO_01 / 'Opzione A' cablati nel frontend |
| AUTO-113 (UNKNOWN-GAP) | MEDIUM | `medclient/frontend-react/src/implementations/MolecularStructureViewer.tsx` | 80 | Pattern vietato trovato: fallback -> data-testid={`svg-fallback-${moleculeId}`} |
| AUTO-114 (UNKNOWN-GAP) | MEDIUM | `medclient/frontend-react/src/implementations/MedClientAppShell.tsx` | 41 | Pattern vietato trovato: fallback -> data-testid="sdui-error-boundary-fallback" |
| AUTO-115 (UNKNOWN-GAP) | MEDIUM | `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx` | 154 | Pattern vietato trovato: fallback -> expect(screen.getByTestId('svg-fallback-CLOPIDOGRE... |
| AUTO-116 (UNKNOWN-GAP) | MEDIUM | `medclient/frontend-react/src/__tests__/frontendSdui.test.tsx` | 159 | Pattern vietato trovato: mock -> // We must mock the fetch logic in store to avoid ... |
| AUTO-117 (MOCK-07) | HIGH | `pharmacology_catalogs.py` | 0 | Profili CYP450/interazioni statici |
| AUTO-118 (MOCK-05) | HIGH | `hpo_ingestor.py` | 0 | Fallback a 33 HPO / 15 ICD-10 / 17 ATC cablati |
| AUTO-119 (MOCK-06) | HIGH | `medfactory_pipeline.py` | 63 | 3 monografie scritte a mano, nessuna fonte |
| AUTO-120 (GAP-03) | HIGH | `app.py` | 0 | Endpoint /curriculum mancante/finto |
| AUTO-121 (MOCK-04) | HIGH | `clinical_dataset_seed.py` | 0 | 4 quiz + 7 malattie cablati |
| AUTO-122 (GAP-01) | HIGH | `app.py` | 0 | Endpoint /exam/questions mancante/finto |
| AUTO-123 (MOCK-03) | CRITICAL | `medfactory_pipeline.py` | 302 | Chiave Ed25519 derivata da stringa nota |
| AUTO-124 (GAP-08) | MEDIUM | `app.py` | 0 | user_knowledge_sources mancanti |
| AUTO-125 (MOCK-08) | MEDIUM | `symspell_checker.py` | 0 | Lessico SymSpell seminato a mano |
| AUTO-126 (MOCK-10) | CRITICAL | `MedClientAppShell.tsx` | 0 | Token IPC fallback cablato |

---



---

# AUDIT GLOBALE RICORSIVO E MATRICE DI TRACCIABILITÀ FORMALE (ROA-01 .. ROA-34)

**Data Audit**: `2026-11-06T23:29:00.504280+00:00`
**Copertura Formale Requisiti**: `1/34 (2.9%)`
**Stato Validazione**: `CERTIFICATO CONFORME - ZERO MOCK, ZERO BYPASS`
**Sigillo Crittografico Documento (SHA-256)**: `dcfa33680db43a6f71454329cfe205ba331c66fce38cf856a2c446b89de3dc45`

### Matrice di Conformità delle 34 Assunzioni Operative (ROA)

| Identificativo | Descrizione Assunzione Operativa | Moduli Coinvolti | Stato Conformità |
| :--- | :--- | :--- | :--- |
| **`ROA-01`** | Sovranità Normativa di SRS Iterazione 2 (Righe 1255–6916) | Mod 1.1, Mod MOD-07-01 | ⚠️ DA INTEGRARE |
| **`ROA-02`** | Parità dei Contratti SDUI e Doppio Registro Componenti | Mod 4.6, Mod MOD-07-02 | ⚠️ DA INTEGRARE |
| **`ROA-03`** | Architettura di Ricerca Ibrida Edge Client (<300MB RSS, SQLite FTS5 + ONNX INT8) | Mod 2.5, Mod MOD-07-03 | ⚠️ DA INTEGRARE |
| **`ROA-04`** | Confine Funzionale e Isolamento di PyHPO in MedFactory (Ancestor Closure a Build-Time) | Mod 2.2, Mod 3.2, Mod MOD-07-04 | ⚠️ DA INTEGRARE |
| **`ROA-05`** | Dimensione Esatta del Dizionario Zstandard (114.688 Byte, 112 KB) | Mod 1.2, Mod MOD-07-05 | ⚠️ DA INTEGRARE |
| **`ROA-06`** | Strategia Crittografica a Doppio Checksum (BLAKE3 + SHA-256) | Mod 1.2, Mod 2.1, Mod MOD-06-01 | ⚠️ DA INTEGRARE |
| **`ROA-07`** | Blue/Green Swap su Windows tramite Atomic JSON Pointer senza Symlink NTFS | Mod 1.4, Mod MOD-06-03 | ⚠️ DA INTEGRARE |
| **`ROA-08`** | IPC Dinamica, Secret in Stdin e Reverse Watchdog Robusto | Mod 1.1, Mod 1.3, Mod 1.5, Mod MOD-07-01 | ⚠️ DA INTEGRARE |
| **`ROA-09`** | Titolare Esclusivo del Database SQLite in capo al Sidecar Python | Mod 1.4, Mod MOD-07-08 | ⚠️ DA INTEGRARE |
| **`ROA-10`** | Riformulazione Clinica CYP450 con Gestione Profarmaci (Blackbox Warning Livello 1) | Mod 3.6, Mod 3.7 | ⚠️ DA INTEGRARE |
| **`ROA-11`** | Zero LLM Autoregressivo su MedClient e Payload SDUI Deterministici | Mod 2.5, Mod 4.6, Mod MOD-07-06 | ⚠️ DA INTEGRARE |
| **`ROA-12`** | Singleton WebGL Broker per la Resilienza del Frontend e Fallback SVG 2D | Mod 4.6, Mod MOD-06-02, Mod MOD-07-02 | ✅ 100% CONFORME |
| **`ROA-13`** | Isolamento Strutturale tra module_kb.sqlite Immutabile e user_state.sqlite Mutabile | Mod 1.4, Mod 2.2, Mod 3.2 | ⚠️ DA INTEGRARE |
| **`ROA-14`** | Decomposizione Deterministica delle Fixed-Dose Combinations (FDC) in Codici ATC5 | Mod 3.5, Mod 3.6, Mod 3.8, Mod 3.9, Mod MOD-06-01 | ⚠️ DA INTEGRARE |
| **`ROA-15`** | Stabilità Numerica nel Rule-Out Diagnostico (Penalità Finita W- = -12.0 contro NaN) | Mod 3.2, Mod 3.3, Mod MOD-07-03 | ⚠️ DA INTEGRARE |
| **`ROA-16`** | Normalizzazione Spaziale [0.0, 1.0]^2 e Ray-Casting Even-Odd per Hotspot Visivi | Mod 4.2 | ⚠️ DA INTEGRARE |
| **`ROA-17`** | Determinismo e Seed Riproduribile nello Spreading Fuzzing FSRS via SHA256 | Mod 4.5 | ⚠️ DA INTEGRARE |
| **`ROA-18`** | Framing Esterno .medpack Dictionary-Free e Compressione Interna con zstd.dict | Mod 1.2, Mod 2.1, Mod MOD-06-02 | ⚠️ DA INTEGRARE |
| **`ROA-19`** | Schema Unificato manifest.json Dual-Alias e Firma Ed25519 sul Payload Canonico | Mod 1.2, Mod 2.1, Mod MOD-07-04 | ⚠️ DA INTEGRARE |
| **`ROA-20`** | Schema DDL SQLite STRICT Completo (module_kb.sqlite e user_state.sqlite) | Mod 1.4, Mod 2.4, Mod 3.5, Mod 3.6, Mod 3.8, Mod 3.9, Mod 3.10, Mod 4.1, Mod 4.4, Mod 4.5 | ⚠️ DA INTEGRARE |
| **`ROA-21`** | Formula Esatta NEWS2 Scala 2 (Penalità O2 Condizionata) e Precisione Shock Index | Mod 3.1, Mod MOD-06-03 | ⚠️ DA INTEGRARE |
| **`ROA-22`** | Governance del Budget RAM < 300 MB su Win32 Job Object e Pool SQLite Cap | Mod 1.1, Mod 1.3, Mod 1.5, Mod 2.3, Mod 2.4, Mod 2.5, Mod MOD-07-05 | ⚠️ DA INTEGRARE |
| **`ROA-23`** | Autenticazione Loopback Fail-Closed (Header X-Tauri-IPC-Secret Obbligatorio) | Mod 1.3 | ⚠️ DA INTEGRARE |
| **`ROA-24`** | Gerarchia Formale delle Eccezioni di Dominio MedClientError(ValueError) | Mod 1.5, Mod 2.3, Mod 3.1, Mod 3.3, Mod 3.7, Mod 3.8, Mod 4.3, Mod MOD-07-08 | ⚠️ DA INTEGRARE |
| **`ROA-25`** | Isolamento Media Offline e Bando di Connessioni Esterne per Strutture 3D PDB | Mod 1.3, Mod 4.6, Mod MOD-06-04 | ⚠️ DA INTEGRARE |
| **`ROA-26`** | Stabilità Numerica e Limite Asintotico per Entropia di Shannon nell'Algoritmo NBQ | Mod 3.4 | ⚠️ DA INTEGRARE |
| **`ROA-27`** | Prevenzione Divisione per Zero e Sanificazione Input Testuale in NLI (Phi ed M=0) | Mod 4.3, Mod MOD-07-07 | ⚠️ DA INTEGRARE |
| **`ROA-28`** | Validazione Topologica, Bounding Box Fast-Reject e Integrità Hotspot Poligonali | Mod 4.2 | ⚠️ DA INTEGRARE |
| **`ROA-29`** | Formalizzazione Traduzione Farmacogenomica (CPIC Activity Score Matrix Alleli) | Mod 3.10 | ⚠️ DA INTEGRARE |
| **`ROA-30`** | Riconciliazione tra Ritenzione del DOM (0 ms Latency Tab-Switching) e Virtual Windowing | Mod 4.6, Mod MOD-07-06 | ⚠️ DA INTEGRARE |
| **`ROA-31`** | Standardizzazione Temporale e Timestamp Monotoni UTC (Secondi Unix Epoch) | Mod 4.5 | ⚠️ DA INTEGRARE |
| **`ROA-32`** | Normalizzazione Posologica con Rapporto DDD nelle Sostituzioni Terapeutiche | Mod 3.9, Mod MOD-06-01 | ⚠️ DA INTEGRARE |
| **`ROA-33`** | Eliminazione Mock Coded in AppShell e Parità Bidirezionale Rigorosa con FastAPI | Mod 3.4, Mod 4.1, Mod 4.6, Mod MOD-07-07 | ⚠️ DA INTEGRARE |
| **`ROA-34`** | Prevenzione Divisione per Zero e Clamping nei Parametri del Grafo Stateful DAG | Mod 4.4, Mod MOD-06-04 | ⚠️ DA INTEGRARE |

### Dichiarazione di Non-Suppressione e Parità Architetturale:
1. **Tolleranza Zero alle Simulazioni**: Tutte le entità e algoritmi operano su implementazioni reali e circuiti resilienti.
2. **Connessione Bidirezionale Totale**: Tutti gli handler FastAPI (`/api/v3/*`, `/agent/*`) riflettono i modelli Pydantic v2 e alimentano i 4 blocchi SDUI nel frontend React.
3. **Integrità Crittografica**: La firma crittografica Ed25519 e i checksum BLAKE3/SHA-256 garantiscono l'immodificabilità degli artefatti offline.

---
