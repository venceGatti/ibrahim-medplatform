# AUDIT ARCHITETTURALE CRITICO E REGISTRO FORMALE DELLE ASSUNZIONI OPERATIVE (R1)
## Piattaforma Medica Ibrida Asimmetrica MedPlatform (MedFactory + MedClient)

**Data**: 2026-10-30  
**Autori**: Teamwork Orchestration Hierarchy (`orchestrator`, `critic_survey_1`, `explorer_audit_1`, `spec_miner_1`)  
**Stato**: Convalidato e Vincolante per tutte le Milestone Costruttive  
**Percorso Documento**: `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\AUDIT_AND_ASSUMPTIONS.md`

---

## 1. Executive Summary & Risultati dell'Audit Triangolato

In ottemperanza al requisito **R1**, è stato condotto un audit sistematico incrociato e privo di assunzioni non verificate su:
1. `c:\Users\vence\Downloads\projects\ibrahim\SRS_MedClient_Architettura_Completa.md` (6.916 righe)
2. `c:\Users\vence\Downloads\projects\ibrahim\Pianificazione App Medica Ibrida.pdf` (64 pagine)
3. `C:\Users\vence\.gemini\antigravity\brain\3aa6efc6-1a77-4cff-b774-120f18a304fb\piano_costruzione_autonoma_medplatform.md`
4. Codebase reale in `c:\Users\vence\Downloads\projects\ibrahim` (`medclient/`, `medfactory/`, script e dipendenze)

### Esito dell'Audit:
- **Analisi Spec & Critica**: Rilevate 6 incongruenze primarie, duplicazione massiva nel capitolato SRS (prime 1.254 righe), allucinazioni di token streaming LLM nel runtime client (Modulo 4.3), conflitto di titolarità del database SQLite tra Rust e FastAPI, grave falla clinica nell'interazione enzimatica CYP450 per i profarmaci, e incompatibilità strutturale dei symlink NTFS su Windows.
- **Audit del Codice Esistente**: Il motore Rust non compila (`*mut c_void` vs `usize` in `supervisor.rs`), `med-asset://` viola lo zero-copy riallocando con `mmap.to_vec()`, TOCTOU race condition su porta sidecar, 60% dell'architettura client assente (`medclient/sidecar-python/` e `medclient/frontend-react/` inesistenti, 0 file), assenza di ontologie in `medfactory/src/ontologies/`, e presenza di anti-pattern vietati (`Field(...)` x17, `compressed_bytes=1`, identificatori vietati, assenza di cartelle `interfaces/base/implementations`).

Per garantire l'avanzamento autonomo e la costruzione ineccepibile del sistema, il team ha formalizzato 24 Assunzioni Operative Vincolanti (**ROA-01** – **ROA-24**).

---

## 2. Inventario Dettagliato delle Discrepanze e Punti Deboli Rilevati

### 2.1 Discrepanze Normative e di Capitolato
1. **Duplicazione Strutturale dell'SRS**: Le prime 1.254 righe dell'SRS contengono una bozza parziale dei Moduli 1.1-1.3 generata nei primi cicli. A riga 1.255 il capitolato riparte integralmente da Modulo 1.1 fino a 4.3.
2. **Contraddizione LLM Client**: Il Modulo 1.1 e 2.2 vietano categoricamente qualsiasi modello autoregressivo nel client (dimostrando OOM a 4.94GB e latenza 71s); il Modulo 4.3 introduce invece nel diagramma un task di inferenza LLM con streaming SSE di token diff (`summary_token_stream_active`, `rationale_token_stream_id`).
3. **Contesa Proprietaria di SQLite**: Il Piano Autonomo assegna le query a FastAPI; l'SRS Modulo 1.4 implementa un router Rust `arc-swap` + `r2d2_sqlite`; il Modulo 4.1 fa leggere i quiz direttamente a Rust da SQLite; il Modulo 3.2 introduce un DB separato `file:pharma.db`.
4. **Disallineamento IPC**: Modulo 1.3 specifica HTTP REST/SSE su porta loopback effimera con token via stdin e header `X-Tauri-IPC-Secret`; Modulo 3.1 menziona invece Named Pipe / Protobuf Serialization.
5. **Nomenclatura Blocchi SDUI**: Il Piano elenca `MarkdownBlock`, `DifferentialDiagnosisBlock`, `InteractiveFlowchartBlock`, `ClinicalExamBlock`; l'SRS Modulo 4.3 elenca `ClinicalSheetBlock`, `SymptomMatcherBlock`, `DrugSafetyBlock`, `ExamSimulatorBlock`.

### 2.2 Gravi Lacune di Dominio Clinico e Matematico
1. **Falla Clinica CYP450 (Il Paradosso dei Profarmaci)**: Il modello originario somma gli inibitori considerando ogni interazione come "accumulo tossico". Per farmaci salvavita che sono **profarmaci inattivi** (es. **Clopidogrel** su CYP2C19, **Codeina** su CYP2D6), l'inibizione dell'enzima ne impedisce l'attivazione epatica, provocando **inefficacia terapeutica letale** (es. trombosi acuta dello stent coronarico, mancata analgesia) anziché tossicità da accumulo.
2. **Assenza di Ancestor Closure nell'Ontologia HPO**: L'ontologia HPO è un DAG `is_a`. Un matching esatto su codice stringa (`HP:XXXXXXX`) produce falsi negativi totali se lo studente inserisce un fenotipo più generico (es. *Dispnea*) rispetto a quello specifico associato alla patologia (es. *Dispnea parossistica notturna*).
3. **Mancanza di Formalizzazione eGFR**: Mancava la formalizzazione rigorosa della formula CKD-EPI 2021 (senza coefficiente di razza) per l'insufficienza renale.

### 2.3 Difetti di Sistema Operativo e Risorse (Windows x86_64)
1. **Incompatibilità Symlink Windows**: La creazione di link simbolici per il Blue/Green swap (`master_knowledge.current`) su Windows NTFS non elevato fallisce sistematicamente con Win32 Error 1314 (`ERROR_PRIVILEGE_NOT_HELD`).
2. **Violazione Zero-Copy in `med-asset://`**: `medclient/core-rust/src/protocols/asset_protocol.rs` chiamava `mmap[..].to_vec()`, allocando nell'heap ed eseguendo una copia completa dei byte ad ogni visualizzazione d'immagine.
3. **Saturazione RAM con ChromaDB Client**: Eseguire un demone ChromaDB embedded su MedClient consuma da solo oltre 250MB di RAM per 50.000 chunk, violando irrimediabilmente il limite di 300MB RSS dell'intera applicazione desktop.
4. **Esaurimento Contesti WebGL in WebView2**: WebView2 limita i contesti WebGL attivi a 8-16. Rendering multipli di molecole 3D portano a `webglcontextlost`.
5. **TOCTOU Race Condition su Porta Sidecar**: Rust faceva `drop(listener)` prima di avviare il processo child, consentendo a terzi processi di occupare la porta prima del `bind()` di FastAPI.

### 2.4 Difetti di Codice e Standard (Explorer Audit)
1. **Compilazione Rust Fallita**: `medclient/core-rust/src/supervisor.rs` (righe 20, 68) fallisce il type check con `expected *mut c_void, found usize`.
2. **Subsystem Mancanti al 100%**: `medclient/sidecar-python/` (0 file), `medclient/frontend-react/` (0 file), `medfactory/src/ontologies/` (0 file).
3. **Dipendenze Mancanti in `agent_env`**: `fastapi`, `docling`, `pyhpo`, `polars` non installate nell'ambiente Python.
4. **Marcatori e Anti-Pattern Vietati**: 17 occorrenze di `Field(...)` in `manifest_models.py`, sentinel dummy `compressed_bytes=1` in `medpack_assembler.py`, identificatori non semantici (`samples`, `temp_db_path`, `payload`, `res`, `data`, `val`), assenza di cartelle `interfaces/base/implementations`.

---

## 3. Registro Formale delle Assunzioni Operative (ROA)

Le seguenti 24 assunzioni (Passate 1, 2 e 3) costituiscono il contratto ingegneristico autorevole per colmare ogni lacuna e governare la costruzione autonoma:

### ROA-01: Sovranità Normativa di SRS Iterazione 2 (Righe 1255–6916)
- **Assunzione**: Le righe 1255–6916 di `SRS_MedClient_Architettura_Completa.md` costituiscono la specifica formale definitiva ed esclusiva per modelli matematici, schemi DDL, contratti Pydantic v2 e lifecycle di sistema. Le righe 1–1254 sono trattate come bozza storica superata.

### ROA-02: Parità dei Contratti SDUI e Doppio Registro Componenti
- **Assunzione**: Il backend FastAPI sidecar serializza i 4 blocchi SDUI con i nomi canonici definiti nell'SRS: `ClinicalSheetBlock`, `SymptomMatcherBlock`, `DrugSafetyBlock`, `ExamSimulatorBlock`. Il frontend React registra nel proprio registry i nomi canonici e gli alias del piano (`MarkdownBlock` $\to$ `ClinicalSheetBlock`, `DifferentialDiagnosisBlock` $\to$ `SymptomMatcherBlock`, `InteractiveFlowchartBlock` $\to$ `ExamSimulatorBlock`, `ClinicalExamBlock` $\to$ `ExamSimulatorBlock`), garantendo totale parità ed eliminando qualsiasi `DAGNodeNotFoundError`.

### ROA-03: Architettura di Ricerca Ibrida Edge Client (<300MB RSS)
- **Assunzione**: ChromaDB è bandito dal runtime MedClient. MedFactory calcola gli embedding a build-time. MedClient esegue la ricerca testuale tramite SQLite FTS5 ($< 5\text{ ms}$) e la ricerca semantica tramite inferenza ONNX Runtime INT8 (`all-MiniLM-L6-v2`, $< 25\text{ MB}$ disco, $< 48\text{ MB}$ RAM) confrontando il vettore con BLOB vettoriali SQLite tramite dot-product/cosine similarity vettorializzata, garantendo RSS client totale $< 300\text{ MB}$ e latenze query $< 50\text{ ms}$.

### ROA-04: Confine Funzionale e Isolamento di PyHPO in MedFactory
- **Assunzione**: `pyhpo` opera esclusivamente all'interno di `medfactory` a build-time per processare l'ontologia HPO (`hp.obo`, `phenotype.hpoa`), calcolare l'Information Content (IC) e la chiusura transitiva degli antenati (Ancestor Closure). MedClient non ha dipendenze runtime su `pyhpo`; interroga unicamente le tabelle relazionali e la matrice CSR pre-compilata in `module_kb.sqlite`.

### ROA-05: Dimensione Esatta del Dizionario Zstandard (114.688 Byte)
- **Assunzione**: Il dizionario Zstandard è addestrato su un campione stratificato del 10% del corpus medico per una dimensione binaria esatta di $112 \times 1024 = 114.688\text{ Byte}$. Compresso a Level 19 in MedFactory e decompresso in MedClient a velocità $\ge 1.2\text{ GB/s}$ senza picchi di allocazione heap.

### ROA-06: Strategia Crittografica a Doppio Checksum (BLAKE3 + SHA-256)
- **Assunzione**: MedFactory calcola sia l'hash BLAKE3 (per streaming e integrità ad altissima velocità degli archivi `.medpack`) sia l'hash crittografico SHA-256 (per record SQL e requisiti di conformità). Entrambi gli hash sono registrati in `manifest.json`, firmato con Ed25519.

### ROA-07: Blue/Green Swap su Windows tramite Atomic JSON Pointer
- **Assunzione**: È bandito l'uso di symlink su Windows. Il meccanismo Blue/Green opera tramite un puntatore JSON `active_db.json` in `%LOCALAPPDATA%/MedPlatform/config/`. L'aggiornamento avviene scaricando o decomprimendo sul database inattivo (es. `module_kb_green.sqlite`), convalidando con `PRAGMA integrity_check;`, e sostituendo atomicamente `active_db.json` tramite `ReplaceFileW` / `MoveFileExW(..., MOVEFILE_REPLACE_EXISTING)`.

### ROA-08: IPC Dinamica, Secret in Stdin e Handshake Robusto
- **Assunzione**: Il core Rust alloca una porta effimera (`127.0.0.1:0`), avvia il processo Python sidecar passando `--port <porta>` e inviando un token crittografico UUIDv4 sulla prima riga di `stdin`. Tutte le richieste HTTP includono l'header `X-Tauri-IPC-Secret: <token>`. Python implementa un thread di reverse-watchdog che invoca `kernel32.WaitForSingleObject` sul PID di Tauri per auto-terminarsi istantaneamente se Tauri crolla.

### ROA-09: Titolare Esclusivo del Database SQLite e dei Flussi Dati
- **Assunzione**: Il sidecar Python (`medclient/sidecar-python/database/`) è l'UNICO proprietario e gestore del pool di connessioni SQLite in lettura su `master_knowledge.sqlite`. Il core Rust NON apre connessioni SQL concorrenti, evitando `SQLITE_BUSY` ed `ERROR_SHARING_VIOLATION`. Rust funge unicamente da host applicativo, supervisore di processo (Job Object) e gestore dello streaming asset `med-asset://`.

### ROA-10: Riformulazione Clinica CYP450 con Gestione Profarmaci
- **Assunzione**: La tabella `substances` include il campo `is_prodrug BOOLEAN NOT NULL DEFAULT 0`. Il motore delle interazioni valuta:
  - Substrato attivo + Inibitore $\implies$ Alert Severità 1 o 2 (Tossicità / Accumulo).
  - Profarmaco inattivo (`is_prodrug = 1`) + Inibitore $\implies$ **Blackbox Warning Livello 1 (Inefficacia Terapeutica Letale / Rischio Trombotico o Fallimento)**.
  - Profarmaco inattivo + Induttore $\implies$ Alert Livello 1 (Rischio Sovradosaggio Iperacuto).

### ROA-11: Zero LLM Autoregressivo su MedClient e Streaming Deterministico
- **Assunzione**: MedClient è totalmente privo di modelli linguistici generativi locali. Le schede cliniche sono al 100% Markdown statico SSG pre-compilato con callout severità tipizzati. Il diagramma con `LLM Inference Task` del Modulo 4.3 è espunto: il backend emette i payload dei 4 blocchi SDUI come JSON atomico tipizzato conforme Pydantic v2.

### ROA-12: Singleton WebGL Broker per la Resilienza del Frontend
- **Assunzione**: Il frontend React implementa il pattern Singleton WebGL Broker per impedire l'errore `webglcontextlost` in WebView2. Le formule molecolari sono renderizzate di default come grafica 2D vettoriale SVG; l'istanza WebGL 3D viene attivata on-demand solo sul blocco interattivo selezionato dall'utente e rilasciata al cambio di focus.

### ROA-13: Isolamento Strutturale tra Knowledge Base Immutabile (`module_kb.sqlite`) e Stato Utente Mutabile (`user_state.sqlite`)
- **Assunzione**: Tutti i contenuti clinici statici compilati da MedFactory (monografie, schede Markdown, ontologie HPO, codici ICD-10 e ATC, matrici di interazione farmaco, profili CYP450, regole drug-disease, quesiti ed hotspot) sono unificati nel database di sola lettura `database/module_kb.sqlite` all'interno del `.medpack`, gestito con rotazione Blue/Green. Lo stato dinamico e mutabile dell'utente didattico (schede FSRS, log delle risposte, appelli d'esame, note) risiede tassativamente in un database dedicato e separato: `%LOCALAPPDATA%/MedPlatform/data/user_state.sqlite`. Durante qualsiasi aggiornamento o Blue/Green swap, `user_state.sqlite` non viene mai alterato né sovrascritto.

### ROA-14: Decomposizione Deterministica dei Farmaci a Dose Fissa Combinata (Fixed-Dose Combinations, FDC)
- **Assunzione**: `module_kb.sqlite` include la tabella di associazione `atc_combinations(composite_atc, component_atc, component_mg)`. In Fase 0 del motore di sicurezza farmacologica, qualsiasi codice ATC composito presente nella prescrizione viene deterministicamente esploso nei suoi $K$ codici ATC5 componenti. Le matrici di interazione a 2-Way, il carico CYP450 e il detector "Triple Whammy" operano sull'insieme unificato di tutti i principi attivi componenti.

### ROA-15: Gestione della Stabilità Numerica nel Rule-Out Diagnostico (Prevenzione Underflow / NaN)
- **Assunzione**: È vietata l'assegnazione di `float('-inf')` ai logit o pesi diagnostici per evitare generazioni di `NaN` in IEEE 754 durante la normalizzazione Softmax Log-Sum-Exp ($\text{LSE}$). Per i sintomi confutati con sensibilità validata $>99\%$, il sidecar applica una penalità finita e limitata $W_{ji}^- = -\tau_{\max} = -12.0$ (odds ratio $\approx 6.14 \times 10^{-6}$), registrando l'evidenza in `rule_out_penalties` ed escludendo la patologia dalla top-K del differenziale attivo.

### ROA-16: Normalizzazione Spaziale $[0.0, 1.0]$ e Algoritmo Ray-Casting Even-Odd per Hotspot Visivi
- **Assunzione**: Tutte le coordinate dei poligoni hotspot sono memorizzate come vettori bidimensionali normalizzati $[(x_1, y_1), \dots, (x_n, y_n)] \in [0.0, 1.0]^2$. Il frontend React calcola le coordinate relative tramite `GetBoundingClientRect(canvas)` convertendo in $(x_{norm}, y_{norm})$. Il controllo geometrico adotta formalmente l'algoritmo **Even-Odd Ray-Casting** (teorema della curva di Jordan) con tolleranza radiale normalizzata $R_{tol} \le 0.02$ della diagonale del canvas.

### ROA-17: Determinismo e Seed Riproducibile nello Spreading Fuzzing FSRS
- **Assunzione**: La dispersione stocastica degli intervalli di ripasso per mitigare il "Review Hell" non adotta generatori casuali non controllati. Essa è derivata deterministicamente tramite funzione hash crittografica dello stato della scheda: $\text{hash\_val} = \text{SHA256}(\text{concept\_uid} + \text{str}(reps)) \pmod{1000}$, garantendo perfetta uniformità di dispersione e simultaneamente il 100% di riproducibilità e testabilità nei test di regressione.

### ROA-18: Framing Esterno `.medpack` Dictionary-Free e Compressione Interna con `zstd.dict` (114.688 Byte)
- **Assunzione**: Per eliminare qualsiasi dipendenza circolare (deadlock di estrazione in cui `zstd.dict` è necessario per decomprimere l'archivio `.tar.zst` che contiene `zstd.dict` stesso), il framing esterno `.medpack` è un archivio `.tar.zst` compresso con Zstandard Livello 19 **senza dizionario esterno** (dictionary-free), oppure decompattabile direttamente dallo stream standard. All'interno del TAR risiedono in chiaro `manifest.json`, `manifest.sig`, `zstd.dict` (esattamente $114.688\text{ Byte}$), `database/module_kb.sqlite` (e `module_kb.sqlite`), `vector_index/index.bin`, `vector_index/meta.bin`, `media/{sha256}.webp` e `media/{sha256}.svg`, mentre le schede cliniche statiche (`assets/schede_statiche/*.md.zst`) e i chunk testuali sono compressi al Livello 19 mediante il dizionario custom `zstd.dict` da $114.688\text{ Byte}$.

### ROA-19: Schema Unificato `manifest.json` Dual-Alias e Firma Ed25519 sul Payload Canonico Intero
- **Assunzione**: Il modello `MedPackManifest` espone sia i campi canonici (`pack_id`, `schema_version`, `build_epoch_timestamp`, `checksums`, `checksums_sha256`) sia gli alias formali (`module_id`, `pack_version`, `build_timestamp`, `dla_engine_version`, `checksums_blake3`). La firma crittografica `Ed25519` (`signature_ed25519` e `manifest.sig`) è calcolata sui byte JSON canonici (`json.dumps(..., sort_keys=True, separators=(",", ":"))`) dell'intero `manifest.json` (con `signature_ed25519=""` al momento della firma), coprendo tutti i digest BLAKE3 e SHA-256 di ogni singolo file dell'archivio. La verifica `verify_medpack` è fail-closed e valida matematicamente sia la firma Ed25519 sia tutti i checksum BLAKE3/SHA-256.

### ROA-20: Schema DDL SQLite `STRICT` Completo (`module_kb.sqlite` e `user_state.sqlite`)
- **Assunzione**: Tutte le tabelle relazionali in `module_kb.sqlite` adottano obbligatoriamente la clausola `STRICT` (inclusa `vector_metadata STRICT`, `substance_cyp_profiles STRICT`, `substance_organ_risks STRICT`, `atc_combinations STRICT`, `cpic_guidelines STRICT`, `exam_items STRICT`, `medical_lexicon STRICT`, `colloquial_synonyms STRICT`), con chiusura esplicita della transazione (`self.conn.commit()`) prima di `VACUUM INTO` e rilascio deterministico del descrittore file (`try ... finally: self.close()`). Il database utente `user_state.sqlite` implementa in modalità `STRICT` e `WAL` le tabelle `fsrs_cards`, `review_logs`, `exam_sessions` e `user_bookmarks`.

### ROA-21: Formula Esatta NEWS2 Scala 2 (Penalità Iperossia Condizionata a $O_2$) e Precisione Shock Index
- **Assunzione**: Nella valutazione deterministica dei Red Flags (Fase 0), la Scala 2 di NEWS2 (paziente ipercapnico/BPCO) applica la penalità per iperossia ($\text{SpO}_2 \ge 93\% \implies 1\text{–}3\text{ pt}$) **esclusivamente se `supplemental_o2 == True`**; in aria ambiente (`supplemental_o2 == False`) qualsiasi $\text{SpO}_2 \ge 93\%$ assegna esattamente $0\text{ punti}$. Inoltre, il flag di emergenza `has_single_param_three` viene valutato sui punteggi dei singoli parametri individuali ($\exists p_k = 3$) e mai sullo score aggregato cumulativo. Lo Shock Index è calcolato e normalizzato a 3 cifre decimali esatte: $\text{shock\_index} = \text{round}(\text{HR} / \text{SBP}, 3)$.

### ROA-22: Governance del Budget RAM $< 300\text{ MB}$ su Win32 Job Object e Pool SQLite
- **Assunzione**: Il budget complessivo di memoria $\text{RSS} < 300\text{ MB}$ è governato a livello di sistema operativo tramite Win32 Job Object (`QueryInformationJobObject` / somma del Working Set di tutti i processi figli associati al job), con `mmap_size = 64 MB` (`67108864` byte) o cap controllato sul pool SQLite e dizionario SymSpell pre-filtrato sui soli lemmi clinici canonici per azzerare il memory bloat in avvio.

### ROA-23: Autenticazione Loopback Fail-Closed (`X-Tauri-IPC-Secret`)
- **Assunzione**: Il middleware di sicurezza del sidecar FastAPI opera in modalità rigorosamente **Fail-Closed**: l'header `X-Tauri-IPC-Secret` è obbligatorio e convalidato in tempo costante (`hmac.compare_digest`) su tutte le route `/api/v3/*` e `/agent/*`. Nessun token vuoto, nullo o mancante è mai accettato come bypass.

### ROA-24: Gerarchia Formale delle Eccezioni di Dominio `MedClientError(ValueError)`
- **Assunzione**: Tutte le eccezioni specifiche di dominio nel sidecar e nella pipeline (`MedClientError` e relative sottoclassi per input clinici fuori scala, violazioni contrattuali, corruzione archivi o mancata convergenza) ereditano da `ValueError` (`class MedClientError(ValueError)`), garantendo piena interoperabilità sia con i gestori di validazione standard e i contratti Pydantic v2 sia con gli handler specifici di dominio.

---

## 4. Requisiti di Struttura e Standard di Produzione (Regola Aurea)

Tutti i componenti implementati nelle milestone costruttive devono conformarsi ai seguenti parametri inderogabili:
1. **Modularità e Dimensione File**: Nessun file sorgente deve superare 300-450 righe.
2. **Architettura a 3 Livelli**: Ogni modulo deve essere organizzato nelle cartelle:
   - `interfaces/`: definizioni formali, protocolli astratti, interfacce tipizzate.
   - `base/`: logica comune, validatori di contratto, modelli base.
   - `implementations/`: implementazioni concrete, connettori fisici, algoritmi.
3. **Zero Mocks & Zero Fallback Silenziosi**: Proibiti `pass`, `...`, `TODO`, `mock`, `stub`, `fake`, `dummy`, e identificatori privi di semantica (`data`, `payload`, `res`, `samples`, `val`).
4. **Dipendenze Rigorosamente Pinned**: Tutte le versioni in `requirements.txt`, `Cargo.toml` e `package.json` devono essere bloccate a versioni esatte (es. `package==1.2.3` o `package = "=1.2.3"`).
5. **Agentic API su Loopback**: Esposizione obbligatoria degli endpoint `/agent/health`, `/agent/state`, `/agent/execute`, `/agent/schema` protetti da token effimero su `127.0.0.1`.
6. **Sicurezza Windows DPAPI**: Gestione dei segreti e credenziali persistite protetta tramite DPAPI Windows (`CryptProtectData`).

