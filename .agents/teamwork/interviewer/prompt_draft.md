Delega più agenti 3/4 e separali in più ruoli, incluso quello di coordinatore, di analisi critica, di caccia agli errori, logiche mancanti, strutture errate, concetti mancanti da chiedere all'utente e idee di questo genere mancanti e non analizzate, oppure se il codice scritto non è del tutto corretto o non conforme alle richieste. Piattaforma medica ibrida asimmetrica per la produzione composta da MedFactory (build-time con GPU per estrazione e impacchettamento archivi .medpack) e MedClient (run-time su CPU senza GPU per consultazione diagnostica, sicurezza farmacologica ed esecuzione SDUI).

Working directory: c:\Users\vence\Downloads\projects\ibrahim
Integrity mode: demo
The team must NOT: read test source code to understand expected behaviour before implementing

Riferimenti:
- c:\Users\vence\Downloads\projects\ibrahim\SRS_MedClient_Architettura_Completa.md
- c:\Users\vence\Downloads\projects\ibrahim\Pianificazione App Medica Ibrida.pdf
- C:\Users\vence\.gemini\antigravity\brain\3aa6efc6-1a77-4cff-b774-120f18a304fb\piano_costruzione_autonoma_medplatform.md

## Requirements

### R1. Analisi critica dei documenti, rilevamento anomalie e formalizzazione assunzioni
Il team deve analizzare criticamente il capitolato SRS, il PDF di pianificazione e il piano di costruzione, cacciando errori, logiche mancanti, strutture errate, concetti non analizzati e incoerenze tra capitoli. Il team redige un documento di audit e formalizza in modo esplicito le assunzioni operative per colmare le lacune identificate, consentendo la prosecuzione autonoma senza blocchi.

### R2. Costruzione autonoma dei sistemi MedFactory e MedClient
Il team deve implementare in modo completamente autonomo:
- MedFactory: pipeline Docling DLA, integrazione PyHPO, compressione Zstandard con dizionario a 112KB, esportazione Markdown statico e generazione archivi .medpack.
- MedClient: applicazione desktop basata su Tauri/Rust e React SDUI a 4 blocchi tipizzati, affiancata da sidecar FastAPI Python; gestione database SQLite WAL con swap Blue/Green; protocollo custom med-asset:// con mapping zero-copy (mmap); motore diagnostico basato su log-odds con filtraggio rule-out; motore di sicurezza farmacologica per interazioni CYP450 N-way; NLI Cross-Encoder e scheduler mnemonico FSRS.
È incoraggiato l'uso di librerie/framework pre-costruiti e progetti open-source esistenti ad alte prestazioni e sicuri per evitare di reinventare la ruota, sottoponendo ogni modulo a rigoroso testing e debugging.

### R3. Rispetto dei vincoli architetturali e di sistema
Tutto il codice prodotto deve soddisfare i requisiti di produzione: assenza totale di mock, stub, fallback silenziosi o placeholder fittizi; suddivisione modulare in file sorgente di massimo 300-450 righe distribuiti nelle cartelle interfaces/, base/ e implementations/; versioni delle dipendenze tassativamente bloccate (pinned dependencies); design by contract; gestione dei segreti protetta tramite DPAPI Windows; esecuzione di subprocess solo con liste di argomenti esplicite (senza shell=True); esposizione dell'Agentic API (/agent/health, /agent/state, /agent/execute, /agent/schema) protetta da token effimero su loopback 127.0.0.1; rispetto dei vincoli di runtime (<300MB RSS, tempo di risposta query <50ms su hardware client senza GPU).

### R4. Infrastruttura e accesso di rete
È consentito l'accesso alla rete durante la fase di build e configurazione dell'ambiente agent_env per scaricare le librerie necessarie, i pesi dei modelli (Docling DLA) e le ontologie pubbliche.

## Acceptance Criteria

### Analisi critica e formalizzazione
- [ ] Documento di audit completato con l'inventario delle discrepanze, incongruenze e punti deboli rilevati tra SRS, PDF e piano di costruzione.
- [ ] Registro formale delle assunzioni architetturali adottate per risolvere autonomamente ciascuna lacuna identificata.

### Funzionalità MedFactory
- [ ] Pipeline di estrazione documenti e serializzazione in archivi .medpack verificata su documenti campione reali, con dizionario Zstandard a 112KB operativo.
- [ ] Script di compilazione e validazione dei dati ontologici PyHPO eseguiti con successo senza simulazioni o dati fittizi.

### Funzionalità e vincoli prestazionali MedClient
- [ ] Interfaccia Tauri/Rust e frontend React SDUI a 4 blocchi tipizzati avviabili e comunicanti con il sidecar FastAPI.
- [ ] Protocollo med-asset:// con zero-copy mmap operativo per il caricamento degli asset medici.
- [ ] Meccanismo SQLite Blue/Green swap funzionante in modalità WAL senza corruzione né blocco delle query concorrenti.
- [ ] Algoritmo log-odds diagnostico con rule-out e validatore delle interazioni CYP450 N-way verificati con suite di test analitici.
- [ ] Consumo di memoria MedClient verificato al di sotto di 300MB RSS su CPU senza accelerazione GPU e tempi di risposta delle query inferiori a 50ms.

### Conformità del codice e Agentic API
- [ ] Assenza totale nel codice sorgente di marcatori vietati (TODO, mock, stub, fake, pass vuoti, Ellipsis).
- [ ] Tutti i file sorgente rispettano il limite di 300-450 righe e sono organizzati secondo la struttura interfaces/, base/, implementations/.
- [ ] Tutte le dipendenze in requirements.txt, Cargo.toml e package.json sono pinned a versioni fisse esatte.
- [ ] Endpoint /agent/health, /agent/state, /agent/execute, /agent/schema attivi e protetti da token effimero su 127.0.0.1.
- [ ] Suite di test automatizzati creata da zero ed eseguita con esito positivo al 100% senza alcuna lettura preventiva dei test durante l'implementazione.

