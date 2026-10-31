# Original User Request

## Approved Task Prompt — 2026-10-30T21:44:34Z

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

## Follow-up — 2026-10-30T21:46:51Z

Domanda dell'utente: cosa significa "Integrity mode: demo" nel prompt approvato? Nei file .agents/teamwork compare solo come etichetta, senza definizione. Per favore: (1) spiega cosa comporta questa modalità sul comportamento del team; (2) ribadisci che le regole globali dell'utente restano vincolanti in ogni caso: zero mock/stub/fallback silenziosi, nessun placeholder, test reali, dipendenze pinned, requisiti di produzione (<300MB RSS, query <50ms). Se "demo" allenta uno qualunque di questi vincoli, ignora quella modalità e applica il livello di rigore di produzione. Poi dai all'utente uno stato di avanzamento.


## Follow-up — 2026-10-30T21:47:35Z

Direttiva prioritaria dell'utente per l'Orchestratore e tutti i sub-agenti:
Qualsiasi riferimento a 'Integrity mode: demo' non deve in alcun modo allentare i vincoli di produzione. Le regole globali dell'utente restano tassative e vincolanti al 100%:
- Zero mock, zero stub, zero fake, zero fallback silenziosi, nessun placeholder (niente TODO, pass vuoti o ellissi).
- Test reali e robusti su componenti reali.
- Dipendenze pinned a versioni esatte (requirements.txt, Cargo.toml, package.json).
- Requisiti di produzione stringenti (<300MB RSS, tempi di risposta query <50ms, estrazione reale Docling DLA, dizionario Zstandard 112KB, archivi .medpack reali, SQLite WAL con Blue/Green swap, zero-copy mmap, protocollo med-asset://).
- File sorgente di 300-450 righe max suddivisi rigorosamente in interfaces/, base/, implementations/.
- Gestione segreti con DPAPI, subprocess senza shell=True, Agentic API con token effimero su loopback.
Applicare il massimo livello di rigore di produzione a ogni milestone.

## Follow-up — 2026-10-30T22:49:34Z

DIRETTIVA ESPANSIONE ORGANIZZAZIONE PIRAMIDALE MULTI-AGENTE DALL'UTENTE:
"continua e ricorda di implementare un agente che sorveglia e monitora che il codice sia coeso in tutte le sue parti, quindi verifica che tipo se un metodo richiede un qualche valore in input la funzione che lo richiama lo rispetti, oppure se il server richiede che il file o la richiesta da parte del client sia in un certo modo verifica che venga realmente rispettata ambo i lati, e verifica che il piano architetturale e l'analisi dei punti critici del progetto vengano analizzati e seguiti, corretti e usati la nuova implementazione, in aggiunta aggiungi anche un altro agente che ogni tanto verifica che effettivamente nel file architetturale da 6600 righee non ci siano più logiche manacati o punti deboli o errori o mancate definizioni o segmenti che rischiano di portare ad allucinazioni l'agente a causa di specifiche ambigue e non definiteed altro, poi ogni tanto che controlla che non ci sia più nessun errore nel file e che siano stat tutti più volte risolti e convalidati,(questa operazione deve essere eseguita ogni tantum quando finisce il primo compito, passa a controllare che effettivamente nella passata precedente non aveva dimenticato nulla e che aveva scovato tutti gli errori altrimenti li segnala e li aggiunge in coda al file) poi verifica che tutti gli agenti del team stiano seguendo e rispettanto le implementazioni richieste e dovute e volte dal megafile da 6600 ma ache i punti deboli e fallaci vengano sostituiti e corretti con le implementazoni suggerite dall'agente nel suo file di analisicurativa, e molti altri agenti che si occupano di revisione costante, correzione, supervizione, aggiornamento e correzione, analisi, e moltissimi altri per scrittura del codice ecc... deve essere come letteralmente una aziendo di altissimo livello/multinazionale, come google che ha persone /agenti specializzai per qualsiasi cosa che eseguino il lavoro come una sorta di catena prodruttrice piramidale"

Ruoli e Azioni Cardine:
1. Struttura Piramidale Stile Enterprise/Google: Orchestratore -> Supervisori Coesione e Conformità -> Auditor Multi-Pass -> Squadre di Scrittura, Revisione e Bug-Hunting.
2. Agente di Coesione Cross-Boundary & Parità Contrattuale (`cohesion_contract_inspector`): verifica coesione chiamate/metodi/firme e corrispondenza contrattuale client-server ambo i lati (FastAPI <-> Tauri/Rust <-> React SDUI <-> .medpack).
3. Agente Auditor Ricorsivo Multi-Pass sull'SRS (`srs_multipass_curator`): scansione ricorsiva multi-pass su `SRS_MedClient_Architettura_Completa.md` (~6900 righe) per eliminare logiche mancanti, ambiguità o allucinazioni, appendendo errata corrige e addendum validati.
4. Agente Garante dell'Analisi Curativa (`curative_compliance_enforcer`): verifica che ogni agente applichi le correzioni e le soluzioni migliorative da `critic_survey_1/analysis.md`, `explorer_audit_1/code_audit.md` e `AUDIT_AND_ASSUMPTIONS.md`.
5. Squadre Parallele di Scrittura, Code Review e Correzione Rigorosa (zero-mock, 300-450 righe, interfaces/base/implementations, pinned dependencies).



## Follow-up — 2026-10-30T22:50:32Z

DIRETTIVA ESPANSIONE ORGANIZZAZIONE PIRAMIDALE MULTI-AGENTE DALL'UTENTE (PRIORITÀ MASSIMA — PRESA IN CARICO IMMEDIATA):

L'utente richiede l'espansione e strutturazione piramidale dell'organizzazione multi-agente in stile multinazionale/Google, introducendo ruoli di sorveglianza continuativa e revisione ricorsiva:

1. Struttura Piramidale Stile Enterprise/Google: Organizzare il lavoro su livelli gerarchici (Orchestratore Centrale -> Supervisori di Coesione & Conformità -> Auditor Multi-Pass -> Squadre Specializzate di Sviluppo, Revisione e Bug-Hunting).
2. Agente di Coesione Cross-Boundary & Parità Contrattuale (`cohesion_contract_inspector`):
   - Monitorare che tutto il codice sia perfettamente coeso tra moduli e linguaggi diversi (Python MedFactory <-> `.medpack` <-> Rust Core `medclient-core` <-> FastAPI Sidecar <-> TypeScript/React SDUI).
   - Verificare rigorosamente che ogni funzione/metodo richiamato rispetti firme, tipi e pre-condizioni.
   - Verificare che le richieste client e le risposte server coincidano al 100% ambo i lati (header `X-Tauri-IPC-Secret`, URI `med-asset://`, schemi JSON/Pydantic/TS per i 4 blocchi SDUI, formato `active_db.json`, SQLite WAL).
3. Agente Auditor Ricorsivo Multi-Pass sull'SRS (`srs_multipass_curator`):
   - Eseguire passate periodiche ricorsive sul file `SRS_MedClient_Architettura_Completa.md` (~6900 righe).
   - Verificare che non vi siano logiche mancanti, punti deboli, errori o specifiche ambigue che possano indurre allucinazioni negli agenti.
   - A ogni nuova passata verificare che nulla sia sfuggito alla passata precedente, validando più volte le risoluzioni e appendendo formalmente in coda al file eventuali addendum/errata corrige validati e aggiornando `AUDIT_AND_ASSUMPTIONS.md`.
4. Agente Garante dell'Analisi Curativa (`curative_compliance_enforcer`):
   - Verificare che ogni agente costruttore rispetti il capitolato, ma sostituendo tassativamente i punti deboli e le falle dell'SRS con le soluzioni migliorative formalizzate in `.agents/teamwork/critic_survey_1/analysis.md`, `.agents/teamwork/explorer_audit_1/code_audit.md` e `.agents/teamwork/AUDIT_AND_ASSUMPTIONS.md`.
5. Divisioni Parallele di Scrittura, Revisione Continua e Refactoring:
   - Mantenere e scalare agenti dedicati per la scrittura del codice, la revisione riga per riga (zero-mock, 300-450 righe, `interfaces/base/implementations`, dependency pinning) e il bug-hunting.
