# Handoff Report — critic_survey_1 (Critical Spec Critic)

## 1. Observation

### Documenti e File Ispezionati
1. `c:\Users\vence\Downloads\projects\ibrahim\SRS_MedClient_Architettura_Completa.md` (6.916 righe totali, 394.408 byte)
2. `c:\Users\vence\Downloads\projects\ibrahim\Pianificazione App Medica Ibrida.pdf` (64 pagine)
3. `C:\Users\vence\.gemini\antigravity\brain\3aa6efc6-1a77-4cff-b774-120f18a304fb\piano_costruzione_autonoma_medplatform.md` (140 righe)
4. `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\ORIGINAL_REQUEST.md` (73 righe)

### Evidenze Testuali e Riscontri Verificati
- **Duplicazione Moduli 1.1 - 1.3**:
  - In `SRS_MedClient_Architettura_Completa.md`:
    - Riga 10: `## Modulo 1.1: Profilazione Hardware Target, Asimmetria MedFactory/MedClient e Limiti di Risorse`
    - Riga 388: `## Modulo 1.2: Architettura e Creazione dei .medpack...`
    - Riga 835: `## Modulo 1.3: Canale IPC Tauri-FastAPI e Protocollo di Streaming Zero-Copy...`
    - Riga 1255: `## Modulo 1.1: Profilazione Hardware Target, Asimmetria MedFactory/MedClient e Limiti di Risorse` (Riavvio integrale del capitolato)
    - Riga 1606: `## Modulo 1.2: Architettura e Creazione dei .medpack...`
    - Riga 2155: `## Modulo 1.3: Canale IPC Tauri-FastAPI e Protocollo di Streaming Zero-Copy...`
    - Riga 2638: `## Modulo 1.4: Struttura SQLite Resiliente...`
- **Contraddizione LLM Client**:
  - In `SRS_MedClient_Architettura_Completa.md`, riga 112: `### 3.1 Dimostrazione dell'Incompatibilità dei Modelli LLM Generativi Locali` (dimostra OOM con 4.94 GB e latenza inaccettabile di 71.6s).
  - In `SRS_MedClient_Architettura_Completa.md`, riga 6388 (Modulo 4.3): `Frontend (React) --- GET /session/stream ---> Sidecar (FastAPI) --- LLM Inference Task ----> Engine (SQLite WAL)` ed emissione di `Event: patch` (RFC 6902), con campi `summary_token_stream_active` (riga 6440) e `rationale_token_stream_id` (riga 6489).
- **Contesa Architetturale Database SQLite**:
  - In `piano_costruzione_autonoma_medplatform.md`, righe 45 e 103 (Task 3.3): FastAPI gestisce il "Connettore SQLite ottimizzato per sola lettura (`PRAGMA journal_mode = WAL`, `PRAGMA mmap_size = 256MB`, `cache_size = -7680`)".
  - In `SRS_MedClient_Architettura_Completa.md`, righe 2977-3026 (Modulo 1.4): viene presentata un'implementazione Rust del pool con `arc_swap::ArcSwap` e `r2d2_sqlite::SqliteConnectionManager`.
  - In `SRS_MedClient_Architettura_Completa.md`, righe 5233-5246 (Modulo 4.1): viene specificato che Tauri Desktop (Rust) esegue direttamente letture su `module_kb.sqlite` e invia eventi IPC alla WebView per i quiz MCQ e Hotspot senza transitare da FastAPI.
  - In `SRS_MedClient_Architettura_Completa.md`, riga 4612 (Modulo 3.2): viene referenziato `file:pharma.db?mode=ro&immutable=1`.
- **Contraddizione Canale IPC**:
  - In `SRS_MedClient_Architettura_Completa.md`, riga 2191 (Modulo 1.3): `Canale JSON IPC (Local HTTP REST / SSE)`.
  - In `SRS_MedClient_Architettura_Completa.md`, riga 4144 (Modulo 3.1): `IPC Channel (Named Pipe / Domain Socket: Protobuf Serialization)`.
- **Falla Medica su Dinamica CYP450**:
  - In `SRS_MedClient_Architettura_Completa.md`, righe 4581-4586 e 4662-4671: la competizione enzimatica su CYP3A4, CYP2D6, CYP2C19 calcola il carico metabolico come somma algebrica di inibitori. Non è contemplata la distinzione tra farmaco attivo e profarmaco inattivo (es. Clopidogrel, Codeina), dove l'inibizione dell'enzima provoca assenza di metabolita attivo e fallimento terapeutico mortale anziché tossicità da accumulo.
- **Incompatibilità Symlink Windows**:
  - In `SRS_MedClient_Architettura_Completa.md`, riga 2654: `master_knowledge.current [Puntatore atomico / Symlink]`. Su Windows standard, `CreateSymbolicLink` fallisce senza privilegi amministrativi (`ERROR_PRIVILEGE_NOT_HELD`, 1314).

---

## 2. Logic Chain

1. **Premessa Hardware e Requisiti di Produzione (dall'Osservazione)**:
   MedClient deve operare su un laptop studente con CPU Intel Core i7, 8–16 GB di RAM condivisa con iGPU, senza dGPU, con consumo rigoroso $< 300\,\text{MB}$ RSS e latenza di risposta $< 50\,\text{ms}$. Le regole utente vietano tassativamente mock, stub e fallback silenziosi.
2. **Dall'Osservazione della Duplicazione SRS**:
   Le righe 1-1254 rappresentano una bozza incompleta generata dai primi cicli della CrewAI. L'esistenza di due versioni dei Moduli 1.1-1.3 crea disallineamento nei riferimenti numerici e introduce definizioni contrastanti di latenze e flussi di processo.
3. **Dall'Osservazione della Falla LLM nel Modulo 4.3**:
   L'introduzione di un `LLM Inference Task` con streaming SSE in Modulo 4.3 contraddice apertamente il vincolo dimostrato nel Modulo 1.1 (OOM a 4.94 GB e latenza a 71s). Se uno sviluppatore implementa il Modulo 4.3 come scritto, l'applicazione desktop tenterà di avviare un modello linguistico locale o cercherà endpoint di streaming inesistenti, provocando crash e violazione dei requisiti operativi.
4. **Dall'Osservazione della Concorrenza e Proprietà di SQLite**:
   Se sia il core Rust (Tauri) sia il sidecar Python (FastAPI) mantengono pool di connessione aperti contemporaneamente su Windows con memory mapping attivo (`mmap_size = 256MB`), il sistema incorre in blocchi `SQLITE_BUSY` o violazioni di condivisione (`ERROR_SHARING_VIOLATION`) durante gli aggiornamenti di modulo e rende impossibile eseguire l'hot-swap atomico. La responsabilità delle query deve essere assegnata unicamente a uno dei due layer.
5. **Dall'Osservazione della Falla Clinica CYP450**:
   Trattare tutte le interazioni enzimatiche come "accumulo tossico" è clinicamente scorretto e inaccettabile per uno strumento didattico universitario: gli studenti imparerebbero che associare Omeprazolo e Clopidogrel causa tossicità, mentre nella realtà clinica causa trombosi da stent per mancata trasformazione del profarmaco nel suo principio attivo.

---

## 3. Caveats

- L'analisi si è basata sulla lettura approfondita della specifica tecnica formale (SRS), dei verbali di progettazione (PDF OCR integrale) e del piano di costruzione autonoma. Non sono stati eseguiti test dinamici di compilazione dell'app finale poiché i file sorgente del core (`medclient/core-rust`, `medclient/sidecar-python`, `medclient/frontend-react`) non sono ancora stati implementati (la fase attuale è di spec survey e audit preliminare).
- I modelli di quantizzazione ONNX menzionati (`all-MiniLM-L6-v2` INT8 e `mDeBERTa-v3-base-mnli` INT8) richiedono una validazione sul campo con dataset di test clinici reali per confermare la latenza $< 25\,\text{ms}$ sul processore target.
- Nessun caveat ulteriore.

---

## 4. Conclusion

L'audit emette un verdetto di **REQUEST_CHANGES**. Prima che l'orchestratore o gli agenti di sviluppo avviino la codifica fisica, è imperativo formalizzare e adottare le seguenti risoluzioni architetturali:
1. **Consolidamento del Capitolato SRS**: Eliminare le righe 1-1254 duplicate e allineare gli indici.
2. **Eliminazione dei Residui LLM in Modulo 4.3**: Riconfermare che MedClient è 100% Zero-Generative-LLM in locale; le schede cliniche sono Markdown statico pre-compilato.
3. **Centralizzazione delle Query in FastAPI**: Assegnare l'apertura e gestione del pool SQLite solo a FastAPI. Rust gestisce esclusivamente `med-asset://` e la supervisione dei processi (Job Objects).
4. **Armonizzazione IPC**: Riconfermare l'adozione esclusiva di HTTP REST / SSE su loopback 127.0.0.1 con header di sicurezza `X-Tauri-IPC-Secret`, respingendo l'ipotesi Named Pipe / Protobuf.
5. **Riforma Dinamica CYP450**: Introdurre la logica clinica corretta dei profarmaci (`is_prodrug`) per intercettare l'inefficacia terapeutica oltre alla tossicità cumulativa.
6. **Sostituzione Symlink con Atomic File Pointer**: Gestire il puntatore del database attivo tramite file JSON atomico (`active_db.json`), aggirando le restrizioni di privilegio di Windows NTFS.

---

## 5. Verification Method

Come verificare in modo indipendente le evidenze e le conclusioni riportate:

1. **Verifica della duplicazione SRS**:
   Eseguire su PowerShell:
   ```powershell
   Select-String -Path "c:\Users\vence\Downloads\projects\ibrahim\SRS_MedClient_Architettura_Completa.md" -Pattern "^## Modulo 1.1:"
   ```
   *Esito atteso*: Vengono restituite due occorrenze esatte (riga 10 e riga 1255).

2. **Verifica della contraddizione LLM in Modulo 4.3**:
   Ispezionare le righe 6380-6395 di `SRS_MedClient_Architettura_Completa.md`.
   *Esito atteso*: Presenza esplicita di `--- LLM Inference Task ---->` ed `Event: patch` nel diagramma di sequenza e dei campi `summary_token_stream_active` a riga 6440.

3. **Verifica della discrepanza IPC**:
   Ispezionare la riga 2191 (Modulo 1.3) a confronto con la riga 4144 (Modulo 3.1).
   *Esito atteso*: Modulo 1.3 definisce HTTP REST/SSE, Modulo 3.1 definisce Named Pipe/Protobuf.

4. **Verifica del blocco symlink su Windows**:
   Testare la creazione di un symlink da console PowerShell non elevata:
   ```powershell
   New-Item -ItemType SymbolicLink -Path "test_symlink.sqlite" -Target "c:\Users\vence\Downloads\projects\ibrahim\SRS_MedClient_Architettura_Completa.md"
   ```
   *Esito atteso*: Fallimento con eccezione di privilegio insufficiente (`A required privilege is not held by the client`).

5. **Report Completo**:
   Consultare `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\critic_survey_1\analysis.md` per l'analisi tecnica esaustiva.

