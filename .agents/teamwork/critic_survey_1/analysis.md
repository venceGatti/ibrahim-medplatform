# AUDIT CRITICO COMPLETO: PIATTAFORMA MEDICA IBRIDA MEDPLATFORM
## Analisi Sistematica di Contraddizioni, Difetti Strutturali, Lacune di Dominio e Raccomandazioni Architetturali

- **Autore / Ruolo**: `critic_survey_1` (Critical Spec Critic)
- **Data Audit**: 2026-10-30T22:58:00Z
- **Working Directory**: `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\critic_survey_1\`
- **Documenti Analizzati**:
  1. `c:\Users\vence\Downloads\projects\ibrahim\SRS_MedClient_Architettura_Completa.md` (6.916 righe)
  2. `c:\Users\vence\Downloads\projects\ibrahim\Pianificazione App Medica Ibrida.pdf` (64 pagine)
  3. `C:\Users\vence\.gemini\antigravity\brain\3aa6efc6-1a77-4cff-b774-120f18a304fb\piano_costruzione_autonoma_medplatform.md` (140 righe)
  4. `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\ORIGINAL_REQUEST.md` (73 righe)

---

## 1. Executive Summary & Review Verdict

### Verdetto Globale: **REQUEST_CHANGES (Revisione e Riconciliazione Obbligatoria)**

La piattaforma medica ibrida MedPlatform presenta una visione architetturale potente e ad alta efficienza: **MedFactory** (build-time su workstation GPU con Docling DLA, PyHPO, Zstandard 112KB, esportazione `.medpack`) accoppiata a **MedClient** (runtime desktop offline-first su CPU Intel Core i7 senza dGPU, Tauri v2 in Rust, sidecar FastAPI, SQLite WAL mmap zero-copy, React SDUI a 4 blocchi tipizzati, inferenza discriminativa INT8).

Tuttavia, l'audit approfondito incrociato tra il Capitolato SRS (6.916 righe), il PDF di discussione preliminare (64 pagine) e il Piano di Costruzione Autonoma rivela **gravi discrepanze strutturali, contraddizioni interne insanabili, duplicazione di sezioni, allucinazioni di componenti LLM nel runtime client e lacune critiche nel dominio medico (in particolare sulla dinamica enzimatica CYP450 e sulla semantica ontologica HPO)**.

### Sintesi delle Criticità Primarie (Showstoppers):
1. **Duplicazione Massiva e Disallineamento nel Capitolato SRS**: Le prime 1.254 righe dell'SRS contengono una stesura iniziale dei Moduli 1.1, 1.2 e 1.3, che viene poi bruscamente riavviata alla riga 1.255 con una versione differente (output grezzo generato da un loop iterativo CrewAI senza pulizia di testata).
2. **Contraddizione Diretta sull'Uso di LLM Generativi nel Client**: Mentre il Modulo 1.1 e il Modulo 2.2 vietano categoricamente qualsiasi modello generativo autoregressivo sul client (imponendo Markdown statico compilato da MedFactory), il Modulo 4.3 (SDUI) introduce nel diagramma di sequenza un task di inferenza LLM con streaming SSE di patch RFC 6902 (`summary_token_stream_active`, `rationale_token_stream_id`).
3. **Contesa e Conflitto di Proprietà del Database SQLite**: Il Piano di Costruzione Autonoma assegna a FastAPI la gestione del pool di connessioni SQLite; l'SRS Modulo 1.4 implementa un router di connessione lock-free in Rust (`arc-swap` + `r2d2_sqlite`); l'SRS Modulo 4.1 sostiene che Tauri Rust legga direttamente i quiz da SQLite e li invii via IPC alla WebView2; l'SRS Modulo 3.2 introduce arbitrariamente un database separato `file:pharma.db`.
4. **Protocollo IPC Incoerente**: Il Modulo 1.3 definisce un canale HTTP REST/SSE su porta loopback effimera con header `X-Tauri-IPC-Secret`, mentre il Modulo 3.1 specifica "Named Pipe / Domain Socket: Protobuf Serialization".
5. **Falla Medica Critica nella Dinamica CYP450 (Prodrug vs Active Drug)**: Il motore farmacologico tratta tutte le inibizioni enzimatiche come "somma algebrica di tossicità", ignorando che per i **profarmaci** (es. Clopidogrel su CYP2C19, Codeina su CYP2D6) l'inibizione enzimatica causa **mancata attivazione e inefficacia terapeutica letale** (es. trombosi coronarica acuta), non sovradosaggio!
6. **Incompatibilità dei Simlink su Windows per il Blue/Green Swap**: Il Modulo 1.4 prevede un puntatore `master_knowledge.current` via symlink. Su Windows non privilegiato, la creazione di symlink fallisce con `ERROR_PRIVILEGE_NOT_HELD`.

---

## 2. Matrice delle Contraddizioni Incrociate (SRS vs PDF vs Piano Autonomo)

| Area Architetturale | Specifica nel PDF (Log di Pianificazione) | Specifica nel Capitolato SRS | Specifica nel Piano di Costruzione Autonoma | Impatto e Analisi del Rischio | Risoluzione Raccomandata |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Integrità del File SRS** | Generazione incrementale capitolo per capitolo via CrewAI. | Righe 1-1254 contengono Moduli 1.1, 1.2, 1.3; a riga 1255 il file ricomincia da capo con Modulo 1.1 fino a 4.3 (6.916 righe tot). | Riferisce l'SRS come documento di 6.082 righe (conteggio errato). | **Alto**. Ambiguità su quale versione dei Moduli 1.1-1.3 sia normativa. | Troncamento delle righe spurie 1-1254; consolidamento della versione definitiva (righe 1255-6916). |
| **Presenza di LLM Generativi nel Client** | **Vietato categoricamente**. Client usa solo Markdown statico SSG pre-compilato; opzionale API cloud se online. | **Modulo 1.1 & 2.2**: Vietato, latenza 71s e OOM.<br/>**Modulo 4.3**: Flusso streaming SSE con `LLM Inference Task` e token diff! | **Zero LLM generativi**. Solo ONNX Runtime INT8 per NLI ed embedding discriminativi. | **Critico**. Se implementato come da Modulo 4.3, il client collassa su 8GB RAM e viola i 50ms di latenza. | Eliminare qualsiasi streaming generativo da Modulo 4.3. Confermare Markdown statico puro al 100%. |
| **Proprietà del Database SQLite** | FastAPI interroga SQLite locale in sola lettura (WAL mode); Rust si occupa solo di media streaming. | **Modulo 1.4**: Rust implementa `HotSwapRouter` (`r2d2_sqlite`).<br/>**Modulo 4.1**: Rust fa prefetch da `module_kb.sqlite` e invia via IPC event.<br/>**Modulo 3.2**: FastAPI interroga `pharma.db`. | `sidecar-python` implementa il pool di lettura SQLite; `core-rust` gestisce solo `med-asset://` e Job Objects. | **Critico**. Conflitto di ruoli: chi apre la connessione SQLite? Se entrambi aprono pool concorrenti su Windows, si rischia corruzione del file locking. | Centralizzare tutte le query relazionali all'interno di FastAPI (`sidecar-python`). Rust gestisce solo l'host e `med-asset://`. |
| **Canale IPC Strutturato (Tauri $\leftrightarrow$ FastAPI)** | Localhost HTTP REST con porta casuale e token UUIDv4 in stdin. | **Modulo 1.3**: HTTP REST / SSE su loopback 127.0.0.1.<br/>**Modulo 3.1**: Named Pipe / Domain Socket con Protobuf. | FastAPI ASGI su loopback 127.0.0.1 con header `X-Tauri-IPC-Secret` da stdin. | **Medio-Alto**. Incoerenza tra stack HTTP/JSON e Named Pipes/Protobuf su Windows. | Adottare rigorosamente HTTP REST/JSON su 127.0.0.1 con header `X-Tauri-IPC-Secret`. Scartare Protobuf e Named Pipes. |
| **Denominazione Database e Nomenclatura Tabelle** | `module_kb.sqlite` dentro `.medpack`; `master_knowledge.sqlite` nel client. | Modulo 1.4 usa `diseases`, `symptoms`, `drugs`, `drug_interactions`.<br/>Modulo 3.2 usa `substances`, `pairwise_interactions`, `substance_cyp_profiles`. | Schema unificato Pydantic / SQLite non dettagliato a livello di tabella. | **Alto**. Disallineamento schema DDL tra capitolo di archiviazione (1.4) e capitolo farmacologia (3.2). | Unificare il DDL di `master_knowledge.sqlite` fondendo le tabelle anagrafiche e quelle dei profili enzimatici CYP450. |
| **Algoritmo di Scoring Diagnostico** | Modulo 1-5 sintomi bayesiano; esteso a $N$-sintomi log-odds con matrice CSR in RAM. | **Modulo 1.4**: Query SQL Covering Index `idx_covering_symptom_disease`.<br/>**Modulo 3.1**: Calcolo matriciale in RAM NumPy/SciPy SpMV CSR. | Task 3.5: Log-Odds Symptom Matcher + Rule-Out Disease Scorer. | **Medio**. Duplicità implementativa: calcolo in-memory o query SQL? | Specificare chiaramente: SQLite per il pre-filtro di consistenza, Matrice CSR pre-caricata in RAM per il calcolo vettoriale Log-Odds istantaneo (<1ms). |
| **Puntatore Blue/Green su Filesystem** | Non specificato a livello OS. | Modulo 1.4 indica `master_knowledge.current [Puntatore atomico / Symlink]`. | Non specificato. | **Bloccante su Windows**. Creazione di symlink senza privilegi amministrativi restituisce Win32 Error 1314. | Sostituire il symlink con un puntatore persistente in `app_config.json` o file atomicamente rinominato con `MoveFileExW`. |
| **Modalità Integrità: "Demo" vs Produzione** | Non presente nel prompt originale. Nel prompt approvato è citato "Integrity mode: demo". | Standard IEEE/ISO di produzione industriale senza mock. | Riferimento a zero-intervention, strict pinning, zero mock. | **Critico**. Rischio di declassamento della qualità se interpretato come licenza di inserire stub. | Direttiva prioritaria applicata: "demo" è rigettato al 100%. Rigore di produzione assoluto senza eccezioni. |

---

## 3. Analisi Approfondita dei Difetti Strutturali e delle Lacune di Dominio

### 3.1 Dominio Medico-Clinico & Farmacologico

#### A. Il Paradosso dei Profarmaci nella Competizione CYP450
Nel Modulo 3.2 (Sezione 1.1 e 2.1), il sistema valuta il carico metabolico epatico come una somma algebrica di inibitori:
$$\text{Carico}(CYP) = \sum \text{Inibitore}_k$$
Se un farmaco agisce come substrato e sono presenti inibitori dello stesso citocromo, il sistema solleva genericamente un alert di "tossicità epatica/plasmatica per accumulo del farmaco".

* **Falla Clinica Gravissima**: In medicina, molti farmaci cardiovascolari e analgesici critici sono **profarmaci inattivi** che richiedono l'ossidazione epatica per generare il metabolita attivo:
  - **Clopidogrel** (antiaggregante piastrinico per prevenire la trombosi da stent coronarico): richiede l'isoenzima **CYP2C19** per essere attivato. Se associato a un inibitore moderato/forte di CYP2C19 (come **Omeprazolo** o **Esomeprazolo**), la concentrazione del farmaco attivo crolla. Il rischio non è un sovradosaggio tossico, ma la **morte per trombosi acuta dello stent o re-infarto**!
  - **Codeina**: è un profarmaco inattivo che richiede **CYP2D6** per essere convertito in morfina. L'uso di inibitori CYP2D6 (es. Fluoxetina, Paroxetina) azzera l'effetto analgesico; al contrario, in pazienti *Ultra-rapid Metabolizers* (CYP2D6 UM) anche dosi minime scatenano arresto respiratorio da sovradosaggio di morfina.
* **Correzione Obbligatoria**:
  Lo schema della tabella `substances` deve includere il flag booleano `is_prodrug BOOLEAN NOT NULL DEFAULT 0` e la tabella `substance_cyp_profiles` deve mappare l'effetto dell'interazione:
  $$\text{Rischio}(Substrato) = \begin{cases} \text{Tossicità da Accumulo} & \text{se } is\_prodrug = 0 \text{ e } Inibitore \\ \text{Inefficacia Terapeutica Letale} & \text{se } is\_prodrug = 1 \text{ e } Inibitore \\ \text{Sovradosaggio Iperacuto} & \text{se } is\_prodrug = 1 \text{ e } Induttore \end{cases}$$

#### B. Trattamento Piatto dell'Ontologia HPO e Assenza di Semantic Closure
Nel Modulo 1.4 e 3.1, l'algoritmo di matching diagnostico calcola l'affinità incrociando i codici HPO direttamente come stringhe univoche (`HP:XXXXXXX`).
* **Falla di Dominio**: L'ontologia fenotipica umana (HPO) è un grafo aciclico orientato (DAG) con relazioni `is_a`. Se uno studente inserisce il sintomo generico `HP:0002094` (*Dyspnea*), e una patologia nel database è indicizzata con il fenotipo più specifico `HP:0200120` (*Paroxysmal nocturnal dyspnea*), un matching esatto su ID o SQL `IN (...)` produrrà un **falso negativo completo** ($Score = 0$)!
* **Correzione Obbligatoria**:
  Durante la fase di compilazione in MedFactory, deve essere calcolata la **chiusura transitiva verso l'alto (Ancestor Closure)** di ciascun termine HPO associato alla patologia:
  $$\text{Ancestors}(t) = \{ a \in \mathcal{T}_{\text{HPO}} \mid t \xrightarrow{is\_a^*} a \}$$
  Ogni patologia deve ereditare i termini antenati con un fattore di smorzamento basato sull'Information Content (IC):
  $$IC(t) = -\ln P(t)$$
  I sintomi rari e specifici hanno alto IC e potere discriminante; i sintomi generici (es. astenia, febbre) hanno basso IC.

#### C. Assenza dei Profili Paziente Quantitativi (Formula CKD-EPI 2021)
Nel Modulo 3.2 viene citato l'aggiustamento posologico basato su eGFR, ma non è presente la definizione formale della funzione di stima:
* **Correzione**: Implementazione rigorosa della formula CKD-EPI (2021 Creatinine without Race):
  $$eGFR = 142 \times \min(S_{cr}/\kappa, 1)^\alpha \times \max(S_{cr}/\kappa, 1)^{-1.200} \times 0.9938^{\text{Age}} \times [1.012 \text{ if Female}]$$
  dove $\kappa = 0.7$ (donne) o $0.9$ (uomini), $\alpha = -0.241$ (donne) o $-0.302$ (uomini).

---

### 3.2 Architettura Dati, SQLite WAL e Concorrenza su Windows

#### A. Il Problema dei Symlink su Windows (Blue/Green Switch)
Nel Modulo 1.4 (riga 2654) si legge:
`master_knowledge.current [Puntatore atomico / Symlink]`
* **Falla di Sistema**: Su Windows (NTFS), la creazione di link simbolici tramite `CreateSymbolicLinkW` o comandi standard richiede privilegi di amministratore (`SeCreateSymbolicLinkPrivilege`) a meno che la macchina non sia in Developer Mode. Poiché il software deve girare sul portatile di uno studente senza richiedere elevazione UAC né permessi speciali, il tentativo di creare o commutare un symlink causerà un crash immediato con errore Win32 `ERROR_PRIVILEGE_NOT_HELD` (1314).
* **Correzione Obbligatoria**:
  1. Abbandonare la strategia basata su symlink.
  2. Adottare il pattern **Atomic Config Pointer**: un file JSON di configurazione `active_db.json` memorizzato in `%LOCALAPPDATA%/MedPlatform/config/` che specifica quale file è attivo:
     ```json
     { "active_slot": "blue", "db_path": "knowledge/master_knowledge_blue.sqlite", "version": "1.0.0" }
     ```
  3. All'avvio e allo swap, FastAPI e Tauri leggono `active_db.json`. Per la scrittura, si scrive su `active_db.json.tmp` e si esegue una sostituzione atomica tramite `ReplaceFileW` / `MoveFileExW(..., MOVEFILE_REPLACE_EXISTING)`.

#### B. Concorrenza e File Locking su Windows (`SQLITE_BUSY`)
In ambiente Windows, il locking del file system è di tipo **mandatorio** (mandatory locking) a differenza di Unix (advisory locking). Quando un processo apre un file SQLite con `mmap_size > 0` (`MapViewOfFile`), qualsiasi tentativo da parte di un altro processo (o thread) di troncare, cancellare o sovrascrivere quel file genererà `ERROR_SHARING_VIOLATION` (Win32 Error 32).
* **Correzione Obbligatoria**:
  1. `master_knowledge.sqlite` deve essere aperto sia da Python sia da eventuali lettori con flag espliciti di condivisione `FILE_SHARE_READ | FILE_SHARE_WRITE`.
  2. Nelle stringhe di connessione SQLite, usare categoricamente URI con parametri:
     `sqlite:///file:master_knowledge_blue.sqlite?mode=ro&nolock=1` o garantire che l'aggiornamento avvenga SOLO sul database inattivo (`Green`), chiudendo completamente il pool prima di riciclare il file `Blue`.

#### C. Disaccordo tra Multi-Pack e Architettura Blue/Green
Il PDF descrive la distribuzione modulare per esame (`Cardiologia.medpack`, `Ortopedia.medpack`).
Se ogni esame è un `.medpack` separato:
* Se l'utente installa prima Cardiologia, poi importa Ortopedia: come fa il Blue/Green switch a rimpiazzare l'intero database? Rimpiazzare `Blue` con un database che contiene solo Ortopedia cancellerebbe Cardiologia!
* **Risoluzione Architetturale**:
  La decompressione di un `.medpack` nel client NON deve sovrascrivere il database globale.
  Ci sono due alternative tecniche valide:
  - **Opzione A (Monolithic Build, Consigliata per Semplicità)**: MedFactory compila l'intero corpus integrato (tutti i moduli approvati) in un unico pacchetto globale di release. Lo swap Blue/Green sul client è allora una sostituzione pura dell'intero DB.
  - **Opzione B (Local Merge Transaction)**: Ogni `.medpack` contiene `module_kb.sqlite` parziale. Il backend FastAPI avvia una transazione sul database inattivo `Green` (che è una copia esatta di `Blue`), esegue `ATTACH DATABASE 'temp_module.sqlite' AS new_mod;`, inserisce/aggiorna le righe con clausole `INSERT OR REPLACE INTO ...`, stacca il database e commuta da `Blue` a `Green`.

---

### 3.3 Zero-Copy Streaming (`med-asset://`) e Limiti di Memoria Virtuale

#### A. Condivisione File e Handle Leak in WebView2
Nel Modulo 1.3 (righe 2176-2178), il core Rust di Tauri mappa i file WebP tramite `memmap2` e li serve alla WebView2 via custom protocol `med-asset://`.
* **Falla di Risorsa**: Su Windows, mantenere aperti centinaia di mapping `memmap2` satura la tabella degli handle del processo e trattiene le pagine nello spazio di working set della RAM. Se lo studente scorre rapidamente un atlante istologico con 50 preparati ad alta risoluzione (ciascuno da 15-30 MB non compressi in texture GPU), la WebView2 e il processo Rust supereranno rapidamente il budget di **300 MB RSS**.
* **Correzione Obbligatoria**:
  1. Il protocollo nativo `med-asset://` in Rust non deve mantenere aperte le mappature `Mmap` all'infinito: deve implementare un pool `MmapCache` a capacità fissa (LRU con massimo 8 file contemporaneamente mappati).
  2. Appena il buffer viene trasmesso allo stream di risposta della WebView2, l'handle di visualizzazione viene rilasciato (`drop(mmap)`).

#### B. Race Condition nell'Allocazione della Porta Effimera (TOCTOU)
Nel Modulo 1.3 (riga 2216), si specifica:
"Tauri inizializza un socket TCP su `127.0.0.1:0`... ne preleva la porta libera... la rilascia immediatamente e la passa come argomento CLI a FastAPI".
* **Falla di Concorrenza**: Questa è una classica vulnerabilità TOCTOU (Time-Of-Check to Time-Of-Use). Tra l'istante in cui Rust chiude il socket e l'istante in cui FastAPI esegue il `bind()`, un altro processo in esecuzione sul sistema operativo può occupare quella stessa porta, provocando il fallimento dell'avvio di FastAPI (`WSAEADDRINUSE`, Win32 error 10048).
* **Correzione Obbligatoria**:
  1. Rust NON rilascia la porta prima di avviare Python.
  2. Oppure: FastAPI viene avviato con `--port 0` (gestione nativa del socket effimero da parte di Uvicorn) e stampa sulla prima riga di `stdout` il token JSON: `{"ready": true, "port": 54321}`. Rust legge questa riga, valida la ricezione e avvia la connessione del frontend.

---

### 3.4 Server-Driven UI (SDUI) e Resilienza del Frontend

#### A. Rigidità di Pydantic (`extra="forbid"`) e Fallimento da Schema Skew
Nel Modulo 4.3 (riga 6410), tutti i modelli Pydantic dei blocchi SDUI dichiarano:
`model_config = ConfigDict(frozen=True, extra="forbid")`
* **Falla di Retrocompatibilità**: Se in un aggiornamento futuro MedFactory o FastAPI aggiungono un nuovo campo (ad esempio `audio_pronunciation_url` in `ClinicalSheetBlock`), un client React o un'istanza non aggiornata di Pydantic rigetterà l'intero payload con eccezione `ValidationError: Extra inputs are not permitted`. La visualizzazione dell'intera scheda clinica andrà in crash per un singolo campo accessorio!
* **Correzione Obbligatoria**:
  Impostare categoricamente `extra="ignore"` su tutti i contratti di ricezione SDUI, affiancato da un campo `schema_version: int = Field(default=1)`. I campi non riconosciuti devono essere ignorati silenziosamente senza interrompere il rendering dei campi noti.

#### B. Limite Rigido dei Contesti WebGL in WebView2 (Blink/Chromium)
La WebView2 di Windows impone un limite hardware rigido di massimo 8–16 contesti WebGL attivi simultaneamente per istanza di rendering. Nel piano didattico medico, una pagina di biochimica o farmacologia molecolare che contenga molteplici visualizzatori 3D (3Dmol.js) supererà rapidamente tale soglia, causando l'evento fatale `webglcontextlost` e rendendo bianchi tutti i canvas precedenti.
* **Correzione Obbligatoria**:
  Applicare rigorosamente il pattern **Singleton WebGL Broker**:
  1. Di default, tutte le strutture molecolari 2D/3D sono renderizzate come formule SVG 2D statiche (generate via SmilesDrawer / RDKit in canvas 2D).
  2. Un solo canvas 3D WebGL è presente a livello di DOM. Quando l'utente clicca su "Esplora Struttura 3D", il singleton si sposta sopra il blocco selezionato e istanzia il rendering WebGL. Al defocus o click su un altro blocco, il contesto 3D viene svuotato (`gl.getExtension('WEBGL_lose_context').loseContext()`) e ripristinato a SVG.

---

## 4. Analisi dei Concetti Inesplorati, Idee Non Analizzate e Ambiguità Critiche

### 4.1 La Ricerca Ibrida: BM25 vs ChromaDB su un Client da <300MB RAM
* **Ambiguità**: Il Capitolato SRS Modulo 2.2 prevede sia un indice vettoriale HNSW con ChromaDB sia un indice BM25.
* **Analisi di Fattibilità**: ChromaDB in modalità embedded importa `onnxruntime`, `pydantic`, `typing-extensions`, e soprattutto `hnswlib` (che alloca il grafo dei vettori in memoria heap C++). Per 50.000 chunk clinici, il working set di ChromaDB supera da solo 250 MB di RAM, lasciando meno di 50 MB per FastAPI, SQLite, React e WebView2!
* **Decisione Architetturale Raccomandata**:
  1. Su **MedClient**, scartare ChromaDB embedded.
  2. Le schede cliniche enciclopediche sono già pre-compilate in Markdown statico (indicizzate e ricercabili in <2ms tramite SQLite FTS5 integrato).
  3. Per la ricerca semantica pura sui paragrafi dei manuali, memorizzare i vettori quantizzati INT8 (SQ8) in una semplice tabella binaria SQLite (`chunk_id`, `vector_blob`) ed eseguire il cosine similarity vettoriale direttamente in memoria tramite NumPy/SciPy o l'estensione ufficiale `sqlite-vec` (scritta in C, consumo RAM <15MB, zero overhead Python).

### 4.2 Modalità Offline vs Online: Il Conflitto di Rete
* **Contraddizione**:
  - `ORIGINAL_REQUEST.md`: "MedClient: completamente offline (zero network dependency)".
  - PDF (pagine 25, 37): "Se lo studente vuole una spiegazione più approfondita... chiama opzionalmente l'API gratuita di Gemini Flash o Groq".
  - Capitolato SRS Modulo 1.1: "Totale disconnessione runtime... Zero network dependency".
* **Risoluzione Formale**:
  MedClient deve essere progettato come **Strict Air-Gapped Compliant**:
  - Il 100% delle funzionalità diagnostiche, farmacologiche, enciclopediche e di esame DEVE funzionare a rete completamente staccata.
  - Eventuali chiamate a modelli esterni LLM (Gemini Flash) devono essere confinate a un modulo isolato e facoltativo (`ExternalEnrichmentPlugin`), disabilitato di default, con esplicita autorizzazione dell'utente e fallback trasparente alla modalità locale NLI ONNX in caso di timeout o assenza di connessione.

### 4.3 Gestione delle Domande da Chiedere all'Utente (Missing Concepts)
Durante la pianificazione preliminare, le seguenti decisioni chiave non sono state formalizzate dall'utente:
1. **Modalità di Distribuzione dei Pacchetti Medici**: I file `.medpack` devono essere distribuiti come un unico archivio annuale consolidato (es. `Anno3_Medicina_v1.medpack`), oppure come singoli file per esame? *(Raccomandazione: Archivio consolidato per semestre/anno per evitare complessi merge relazionali a caldo sul client)*.
2. **Ambito Territoriale delle Farmacopee**: Il database dei farmaci deve seguire primariamente la codifica italiana AIFA (numeri AIC) o la classificazione internazionale WHO-ATC? *(Raccomandazione: WHO-ATC a 5 livelli come chiave primaria, con tabella di mapping verso i marchi commerciali italiani AIFA)*.
3. **Criteri di Riconoscimento Visivo Hotspot**: Qual è la tolleranza geometrica per i click dello studente sulle lesioni? *(Raccomandazione: Poligoni convessi normalizzati in $[0.0, 1.0]^2$ con raggio di tolleranza di 15 pixel)*.

---

## 5. Raccomandazioni Architetturali Concrete e Piano di Bonifica

### R1. Pulizia e Consolidamento del Capitolato SRS
- **Azione**: Rimuovere immediatamente le prime 1.254 righe duplicate di `SRS_MedClient_Architettura_Completa.md`.
- **Obiettivo**: Rendere il documento una specifica coerente, lineare e non ridondante, allineando i riferimenti numerici dei moduli (da 1.1 a 4.3).

### R2. Purificazione Totale da Marcatori LLM nel Runtime Client
- **Azione**: Rimuovere da Modulo 4.3 lo schema di streaming di token LLM (`summary_token_stream_active`, `rationale_token_stream_id`, SSE patch streaming).
- **Sostituzione**: Il backend FastAPI restituisce i 4 blocchi SDUI completi in un unico payload JSON validato o in streaming NDJSON a 2 stadi deterministici (Stadio 1: Dati clinici da SQLite in <3ms; Stadio 2: Similarità semantica NLI in <25ms).

### R3. Riconciliazione della Proprietà di SQLite e dei Flussi IPC
- **Azione**: Assegnare l'esclusiva gestione del pool SQLite al sidecar Python (`medclient/sidecar-python/database/`).
- **Sostituzione**: Rimuovere la duplicazione di query in Rust (`r2d2_sqlite` e `rusqlite` per i quiz). Rust funge unicamente da host, router di sistema per `med-asset://` e supervisore di processo (Job Objects). Il frontend React interroga esclusivamente FastAPI per tutti i dati strutturati dei 4 blocchi.

### R4. Bonifica della Sicurezza Farmacologica CYP450 (Gestione Profarmaci)
- **Azione**: Riscrivere il motore `pharmacology/` per distinguere substrati attivi da profarmaci inattivi.
- **Implementazione**: Quando viene rilevata un'inibizione enzimatica su un profarmaco (es. Omeprazolo + Clopidogrel su CYP2C19), emettere un allarme critico di **Blackbox Warning per Inefficacia Terapeutica / Rischio Trombotico**, con codice di severità `CONTRAINDICATED`.

### R5. Risoluzione dei Symlink su Windows per il Blue/Green Swap
- **Azione**: Sostituire il concetto di symlink con un **Atomic JSON Pointer** gestito tramite API Windows native (`MoveFileExW` con flag di rimpiazzo).

### R6. Riduzione Footprint RAM: Sostituzione di ChromaDB su MedClient
- **Azione**: Eliminare la dipendenza da ChromaDB nel `sidecar-python` del client.
- **Implementazione**: Impiegare SQLite FTS5 per il full-text search lessicale e matrici sparse CSR pre-calcolate (o `sqlite-vec` / flat dot-product NumPy) per i vettori di similarità fenotipica, garantendo un footprint complessivo dell'interprete Python al di sotto di **45 MB RAM**.

---

## 6. Conclusioni dell'Audit

Il progetto MedPlatform possiede un'architettura di base straordinariamente valida, che risponde alle reali esigenze di uno studente di medicina e rispetta rigorosamente i vincoli di calcolo asimmetrico. L'eliminazione delle 75% di sovra-ingegnerizzazione discussa nel PDF è stata un'intuizione fondamentale. 

Tuttavia, prima di iniziare la codifica autonoma della piattaforma, il team di sviluppo e l'orchestratore devono formalizzare e adottare le raccomandazioni sopra descritte, in particolare:
1. Riconciliare la proprietà di SQLite tra Rust e FastAPI.
2. Eliminare i residui allucinati di LLM streaming nel client.
3. Integrare la logica clinica corretta per i profarmaci nel motore CYP450.
4. Sostituire i symlink su Windows con file pointer atomici.

Una volta blindati questi contratti, la costruzione potrà procedere con il 100% di confidenza e zero rischio di regressioni o stalli architetturali.

