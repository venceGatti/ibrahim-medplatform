# RECURSIVE MULTI-PASS SRS SPECIFICATION AUDIT & CURATOR REPORT (PASS 4)
## Deep Cross-Validation, Hallucination Defense & Domain Curation

- **Agent**: `critic_srs_curator_2`
- **Role**: Domain-Expert Critic & Recursive SRS Spec Curator
- **Target File**: `SRS_MedClient_Architettura_Completa.md` (7.229 righe)
- **Cross-References**: 
  - `ORIGINAL_REQUEST.md`
  - `AUDIT_AND_ASSUMPTIONS.md` (ROA-01 .. ROA-24 e nuove ROA-25 .. ROA-34)
  - `srs_curator_1/srs_audit_report.md` (Passate 1, 2 e 3)
  - `curative_enforcer_1/curative_audit.md`
  - `explorer_integrity_remediation/analysis.md`
  - Codebase: `medclient/sidecar-python/`, `medclient/frontend-react/`, `medfactory/`, `medclient/core-rust/`
- **Date**: 2026-10-31
- **Status**: Convalidato e Vincolante per l'intera gerarchia piramidale

---

## 1. Executive Summary & Verdetto Globale

In adempimento al mandato prioritario di sorveglianza continuativa e revisione ricorsiva multi-pass sull'architettura tecnica (`SRS_MedClient_Architettura_Completa.md`, 7.229 righe totali), l'agente `critic_srs_curator_2` ha eseguito la **Passata 4 di revisione approfondita**. 

L'obiettivo dell'audit è stato verificare che **nulla fosse sfuggito nelle passate precedenti**, scovare falle logiche, ambiguità residue, trappole di allucinazione per i costruttori software, e formulare considerazioni cliniche, matematiche e strategiche concrete da sottoporre all'utente, formalizzando le nuove risoluzioni curatrici **ROA-25 .. ROA-34** in `AUDIT_AND_ASSUMPTIONS.md`.

### Verdetto: **CRITICAL CURATIVE INTERVENTION (Falle Nascoste Identificate ed Emendate)**

1. **Riconvalida Passate Precedenti**: Confermato che le risoluzioni ROA-01 .. ROA-24 hanno eliminato con successo le macro-falle iniziali (bando symlink Windows, isolamento PyHPO in MedFactory, dizionario Zstd 114.688 B, Blue/Green atomico su `active_db.json`, bando LLM/ChromaDB da client, correzione profarmaci CYP450).
2. **Nuove Falle Nascoste Rilevate (Passata 4)**:
   - **Trappola Allucinazione di Rete (Air-Gap Breach)**: A riga 6832 dell'SRS Modulo 4.3, il codice esemplificativo di `MoleculeViewer` esegue `fetch('https://files.rcsb.org/download/${pdbId}.pdb')`. Ciò viola frontalmente il vincolo di sistema di funzionamento 100% offline su client e causerebbe freeze, fallimenti silenziosi o fughe di contesto clinico in ambienti isolati.
   - **Trappola Numerica IEEE 754 nell'Entropia di Shannon (NBQ)**: Nel Modulo 3.1 righe 4347–4365, la formula dell'entropia binaria $H(D) = -(p_1 \log_2 p_1 + p_2 \log_2 p_2)$ produce `0.0 * (-inf) = NaN` per candidati a probabilità estrema ($p \in \{0.0, 1.0\}$).
   - **Divisione per Zero e Discrepanza nella Metrica NLI Open-Response**: Nel Modulo 4.1 righe 5415–5425, se lo studente invia una risposta vuota o priva di sintassi, il conteggio proposizionale $M = 0$ scatena `ZeroDivisionError` in $\Phi$. Inoltre, l'implementazione applicava un floor artificiale `max(0.2, ...)` non previsto dalla matematica dell'SRS.
   - **Integrità Geometrica degli Hotspot**: L'algoritmo Ray-Casting Even-Odd del Modulo 4.1 non contemplava poligoni degeneri ($N < 3$ o area nulla) e mancava di un pre-filtro di esclusione rapida $O(1)$ Axis-Aligned Bounding Box (AABB).
   - **Mancata Mappatura Farmacogenomica degli Alleli Stellati**: Il Modulo 3.2 dichiarava i fenotipi ('PM', 'IM', 'NM', 'UM') ma ometteva la tabella deterministica di conversione CPIC Activity Score per i diplotipi genetici reali (`*1/*1`, `*1/*2`, `*2/*2`, `*4/*4`, ecc.).
   - **Conflitto Architetturale tra DOM Retention e Virtual Windowing**: Direttiva utente "DOM Retention at 60 FPS" e SRS Modulo 4.3 "Virtual Windowing: smontaggio di tutti i blocchi a distanza $> 2 \times H_{viewport}$" entravano in rotta di collisione sullo stato dei widget interattivi.
   - **Integrità Monotona dei Timestamp FSRS**: Disallineamento tra formati stringa `DATETIME`, fusi orari locali e secondi Unix Epoch UTC per `due_timestamp`.
   - **Falla Dosimetrica nella Sostituzione Terapeutica**: La funzione $\mathcal{J}(a)$ del Modulo 3.2 non applicava il fattore di conversione Defined Daily Dose (DDD), rischiando di suggerire dosaggi milligrammo-per-milligrammo letali (es. Enalapril 20 mg $\to$ Ramipril 20 mg invece di 5 mg).
   - **Violazione Zero-Mock nel Frontend AppShell e Route Backend**: `MedClientAppShell.tsx` renderizzava hardcoded `DEFAULT_CLINICAL_SHEET`, `DEFAULT_SYMPTOM_MATCHER`, `DEFAULT_DRUG_SAFETY`, `DEFAULT_EXAM_BLOCK` con hash fittizi `0123456789abcdef...` senza invocare `SidecarIpcClient`, mentre `/engine/evaluate` restituiva sentinelle arbitrarie `posterior_probability = 0.5` e `nbq = None`.
   - **Degenerazione nei Parametri del Grafo Clinico (Stateful DAG)**: Rischio di divisione per zero in $E_T$ e $S_R$ qualora $t_{crit} = t_{opt}$ o $B_{max} = C_{opt}$.

---

## 2. Dettaglio delle Falle Nascoste e Risoluzioni Curative (Passata 4)

### 2.1 Falla 1: Richiesta di Rete Esterna in SDUI MoleculeViewer (`rcsb.org`)
* **Ubicazione**: `SRS_MedClient_Architettura_Completa.md`, riga 6832.
* **Codice Difettoso nell'SRS**:
  ```tsx
  fetch(`https://files.rcsb.org/download/${pdbId}.pdb`)
    .then(res => res.text())
    .then(data => { viewer.addModel(data, "pdb"); ... })
  ```
* **Impatto / Rischio Allucinazione**: In un ambiente di produzione edge offline o air-gapped (ospedale, sala operatoria priva di accesso WAN), il componente tenta una risoluzione DNS e un handshake TLS verso l'esterno. La richiesta va in timeout (30–60 secondi), blocca il thread UI di WebView2, consuma risorse e fallisce il rendering 3D. Qualora la rete sia attiva, invia identificativi di farmaci e target all'esterno, violando la riservatezza sanitaria.
* **Risoluzione Curativa (ROA-25)**: Divieto assoluto di chiamate di rete esterne. Tutte le coordinate atomiche PDB e le strutture chimiche vettoriali 2D devono risiedere compilate all'interno del file `.medpack` (`assets/pdb/*.pdb`, `media/{sha256}.svg`) e fruite localmente mediante il protocollo custom registrato `med-asset://pdb/{pdb_id}` oppure visualizzate via fallback SVG offline.

---

### 2.2 Falla 2: Instabilità IEEE 754 nell'Entropia di Shannon (Next-Best-Question)
* **Ubicazione**: `SRS_MedClient_Architettura_Completa.md`, righe 4347–4365.
* **Formulazione Difettosa**:
  $$H(D) = - (p_1 \log_2 p_1 + p_2 \log_2 p_2)$$
  $$H(D \mid f_u = v) = - \sum_{k=1}^2 p_k^{(v)} \log_2 p_k^{(v)}$$
* **Analisi Matematica del Difetto**: Quando una patologia leader ha accumulato evidenze schiaccianti o è esclusa per rule-out, la sua probabilità normalizzata $p_1$ converge a $1.0$ e $p_2 \to 0.0$ (o viceversa). Nel calcolo algebrico standard:
  $$\log_2(0.0) = -\infty$$
  In aritmetica floating-point IEEE 754:
  $$0.0 \times (-\infty) = \text{NaN}$$
  Il valore `NaN` contamina a cascata l'Entropia Condizionale Attesa $H(D \mid f_u)$, il Guadagno Informativo $IG(f_u) = \text{NaN}$, e fa fallire l'operatore di confronto `ratio > best_ratio`, portando all'omissione dell'NBQ o a risposte HTTP 500.
* **Risoluzione Curativa (ROA-26)**: Applicazione analitica del limite notevole $\lim_{p \to 0^+} p \log_2 p = 0$. Il calcolatore vincola $p \in [0.0, 1.0]$ e restituisce esattamente $0.0$ per qualsiasi $p \le 10^{-12}$ o $p \ge 1.0 - 10^{-12}$, garantendo convergenza deterministica priva di `NaN`.

---

### 2.3 Falla 3: Gestione Risposte Vuote ed Edge Cases nel Valutatore NLI Open-Response
* **Ubicazione**: `SRS_MedClient_Architettura_Completa.md`, righe 5413–5425.
* **Formulazione dell'SRS**:
  $$\text{Precision Factor } (\Phi) = \frac{\sum_{m=1}^M \mathbb{I}\left(\max_{k} P(E)_{k, m} \ge 0.70\right)}{M}$$
* **Analisi del Difetto**:
  1. Se lo studente invia una stringa vuota, spazi o solo segni di interpunzione (`"..."`, `"?!"`), il segmentatore sintattico non individua alcuna frase grammaticale ($M = 0$). Il calcolo diretto di $\Phi$ genera un'eccezione non gestita `ZeroDivisionError: division by zero`.
  2. L'implementazione reale in `nli_cross_encoder.py` mitigava il problema applicando un floor artificiale `precision_factor = max(0.2, ...)`. Tale floor indeboliva il filtro anti-cheating, consentendo a un utente che inseriva 100 frasi casuali e 1 corretta di ottenere comunque un moltiplicatore $\sqrt{0.2} \approx 0.447$ anziché un abbattimento proporzionale $\sqrt{1/101} \approx 0.099$.
* **Risoluzione Curativa (ROA-27)**: Se $M == 0$, l'endpoint restituisce immediatamente $S_{NLI} = 0.0$, $\Phi = 0.0$, $\Psi = 1.0$ e `passed = False` senza invocare l'inferenza ONNX. Inoltre, il Precision Factor calcola fedelmente il rapporto senza floor minimi artificiali qualora vi siano enunciati non pertinenti.

---

### 2.4 Falla 4: Validazione Topologica e Ottimizzazione Bounding Box negli Hotspot Visivi
* **Ubicazione**: `SRS_MedClient_Architettura_Completa.md`, righe 5332–5360.
* **Analisi del Difetto**: L'algoritmo Ray-Casting Even-Odd (teorema della curva di Jordan) assume che il poligono sia valido. Qualora un quesito d'esame presenti dati malformati o degeneri (es. vertici duplicati, soli 2 punti collineari o coordinate con NaN/infinito), il calcolo genera divisioni per zero nel segmento d'intersezione orizzontale o loop infiniti. Inoltre, eseguire l'intersezione dei segmenti per ogni click utente senza un pre-filtro rapido degrada il frame rate sui display touch.
* **Risoluzione Curativa (ROA-28)**: Validazione Pydantic vincolante: vertici $N \ge 3$, assenza di valori non numerici e area orientata di Gauss (Shoelace) $A = \frac{1}{2} |\sum (x_i y_{i+1} - x_{i+1} y_i)| \ge 10^{-6}$. Inserimento di un test di pre-esclusione $O(1)$ Axis-Aligned Bounding Box (AABB) che scarta all'istante i click esterni al rettangolo circoscritto prima di scorrere gli spigoli del poligono.

---

### 2.5 Falla 5: Omissione della Matrice di Conversione Diplotipo $\to$ Fenotipo CPIC
* **Ubicazione**: `SRS_MedClient_Architettura_Completa.md`, righe 4674–4684 e 4863–4874.
* **Analisi del Difetto**: L'SRS definisce i vincoli fenotipici (`'PM', 'IM', 'NM', 'RM', 'UM'`), ma i laboratori genetici e le cartelle cliniche restituiscono diplotipi allelici stellati (es. `CYP2D6 *1/*4`, `CYP2C19 *2/*17`, `TPMT *1/*3A`). Senza una specifica chiara del sistema di scoring, i sub-agenti costruttori rischiavano di implementare controlli stringa parziali (es. solo `*2/*2`), mancando combinazioni frequenti eterozigoti composte (es. `*2/*3` o `*4/*5` per CYP2D6).
* **Risoluzione Curativa (ROA-29)**: Formalizzazione formale del sistema **CPIC Activity Score**:
  $$AS = \sum_{k=1}^2 \text{score}(\text{allele}_k)$$
  Mappatura rigida:
  - Alleli non-funzionali (`*3`, `*4`, `*5`, `*6`, `*3A`, `*3C`): punteggio $0.0$.
  - Alleli a funzione ridotta (`*9`, `*10`, `*17`, `*41`): punteggio $0.5$.
  - Alleli normali (`*1`, `*2`): punteggio $1.0$.
  - Duplicazioni con guadagno di funzione (`*1xN`, `*2xN`): punteggio $2.0$.
  - Fenotipi derivati: $AS = 0 \implies \text{PM}$, $0 < AS \le 1.0 \implies \text{IM}$, $1.25 \le AS \le 2.25 \implies \text{NM}$, $AS > 2.25 \implies \text{UM}$.

---

### 2.6 Falla 6: Conflitto tra Ritenzione del DOM (0 ms State) e Virtual Windowing
* **Ubicazione**: Capitolato Utente vs `SRS_MedClient_Architettura_Completa.md`, righe 6675–6705.
* **Analisi del Difetto**:
  - Regola Utente / AGENTS.md: *"DOM Retention at 60 FPS: tab switching across clinical blocks must preserve DOM hierarchy via CSS visibility (`hidden opacity-0` vs `block opacity-100`), ensuring 0 ms state reload latency."*
  - SRS Modulo 4.3: *"Virtual Windowing: tutti i blocchi a distanza $> 2 \cdot H_{viewport}$ vengono de-allocati e smontati dal DOM."*
  Se applicato indistintamente a livello macroscopico, il Virtual Windowing smonterebbe la vista dell'esame o il differenziale dei sintomi quando l'utente passa alla scheda farmacologica, distruggendo lo stato non confermato dell'utente (click hotspot, risposte parziali, zoom).
* **Risoluzione Curativa (ROA-30)**: Il Virtual Windowing governa unicamente lo scorrimento dei chunk testuali passivi all'interno delle monografie estese (`ClinicalSheetBlock` con decine di paragrafi). Le 4 schermate primarie dei blocchi SDUI rimangono permanentemente montate nel DOM e la navigazione tra schede opera esclusivamente tramite classi di visibilità CSS (`hidden` / `block`), preservando il 100% dello stato a zero millisecondi di latenza.

---

### 2.7 Falla 7: Disallineamento Temporale e Fusi Orari in FSRS (`due_timestamp`)
* **Ubicazione**: `SRS_MedClient_Architettura_Completa.md`, righe 5811–5865 e 6121–6200.
* **Analisi del Difetto**: La tabella `fsrs_card_state` indicava `due_date DATETIME NOT NULL`, mentre gli schemi Pydantic e la tabella `fsrs_cards` dell'Addendum utilizzavano interi timestamp. Memorizzare date testuali ISO con fuso orario locale o stringhe non normalizzate porta a fallimenti nelle query SQL di estrazione delle card scadute (`WHERE due_date <= datetime('now')`) se il sistema client cambia fuso orario o ora legale.
* **Risoluzione Curativa (ROA-31)**: Tutti i campi temporali del database `user_state.sqlite` e dei contratti API sono vincolati a interi a 64-bit rappresentanti i secondi Unix Epoch UTC (`due_timestamp INTEGER NOT NULL`). L'avanzamento degli intervalli adotta l'equazione deterministica intera: $\text{due\_timestamp} = \text{last\_review\_timestamp} + \lfloor \text{scheduled\_days} \times 86400 \rfloor$.

---

### 2.8 Falla 8: Rischio Sovradosaggio Iperacuto nelle Sostituzioni Farmacologiche (Mancanza di Fattore DDD)
* **Ubicazione**: `SRS_MedClient_Architettura_Completa.md`, righe 4877–4905.
* **Analisi del Difetto**: La funzione di costo $\mathcal{J}(a)$ individua la molecola alternativa ottimale appartenente alla medesima sottoclasse ATC. Tuttavia, l'SRS non specificava la conversione posologica. Se un paziente assume Enalapril 20 mg e il sistema raccomanda Ramipril mantenendo la dose nominale (20 mg), il paziente riceve una dose quadrupla rispetto al massimo consentito di Ramipril (5-10 mg/die), scatenando ipotensione acuta iatrogena e shock!
* **Risoluzione Curativa (ROA-32)**: La raccomandazione dell'alternativa terapeutica calcola obbligatoriamente la dose equiefficace:
  $$\text{Dose}_{\text{alternativa}} = \text{Dose}_{\text{originale}} \times \frac{\text{DDD}_{\text{alternativa}}}{\text{DDD}_{\text{originale}}}$$
  estraendo i valori standardizzati di Defined Daily Dose dalla tabella `clinical_atc`.

---

### 2.9 Falla 9: Presenza di Mock Statici nel Frontend e Parametri Arbitrari nel Backend
* **Ubicazione**: `medclient/frontend-react/src/implementations/MedClientAppShell.tsx` (righe 60–155 e 316–346) e `medclient/sidecar-python/src/api/sdui_routes.py` (righe 256 e 269).
* **Analisi del Difetto**:
  1. In `MedClientAppShell.tsx`, anziché effettuare query reali tramite `SidecarIpcClient`, vengono montati blocchi con dati cablati fissi (`DEFAULT_CLINICAL_SHEET`, `DEFAULT_SYMPTOM_MATCHER`, `DEFAULT_DRUG_SAFETY`, `DEFAULT_EXAM_BLOCK`) e hash sintetici (`0123456789abcdef...`).
  2. In `sdui_routes.py`, l'endpoint `/api/v3/engine/evaluate` restituiva il valore sentinella costante `posterior_probability = 0.5` per tutte le patologie differenziali e `nbq = None`, omettendo di richiamare i motori reali `SoftmaxNormalizer` e `ActiveDiscriminator`.
  3. Questa configurazione viola il principio di "Zero-Mock & Zero-Dummy" e produce una frattura nella coesione del flusso end-to-end.
* **Risoluzione Curativa (ROA-33)**: Eliminazione immediata dei default statici mock in `MedClientAppShell.tsx`. L'applicazione deve interrogare le route live del sidecar tramite `SidecarIpcClient`. Contestualmente, `/api/v3/engine/evaluate` deve calcolare le probabilità posteriori reali tramite `LogSumExpNormalizer.normalize_logits()` e selezionare l'NBQ tramite `ActiveDiscriminator.select_next_best_question()`.

---

### 2.10 Falla 10: Singolarità nei Parametri della Macchina a Stati (Stateful DAG)
* **Ubicazione**: `SRS_MedClient_Architettura_Completa.md`, righe 5549–5554.
* **Analisi del Difetto**:
  $$E_T = \exp\left( - \max\left(0, \frac{t_{sim}^{effettivo} - t_{sim}^{ottimale}}{t_{sim}^{critico} - t_{sim}^{ottimale}}\right) \right)$$
  $$S_R = \max\left(0.0, 1.0 - \frac{C_{eff} - C_{opt}}{B_{max} - C_{opt}}\right)$$
  Qualora un autore di casi clinici imposti per errore $t_{sim}^{critico} = t_{sim}^{ottimale}$ o $B_{max} = C_{opt}$, il runtime incorre in una divisione per zero con emissione di `NaN`.
* **Risoluzione Curativa (ROA-34)**: Validatori Pydantic rigorosi su `StatefulDAGPayload`: $t_{crit} \ge t_{opt} + 1.0$ e $B_{max} \ge C_{opt} + 1.0$. Fallback difensivo in esecuzione: se il denominatore $\le 0$, assegna $1.0$ se il valore speso è $\le$ ottimale e $0.0$ altrimenti.

---

## 3. Considerazioni Cliniche, Matematiche e Strategiche da Chiarire con l'Utente

In ottemperanza al punto 3 del mandato ("Formulare concrete domande, idee e considerazioni cliniche/matematiche da chiarire con l'utente"), si sottopongono le seguenti questioni cardinali:

### 3.1 Questione Clinica 1: Soglia di Blocco sul "Triple Whammy" in Pazienti Borderline
* **Contesto**: La combinazione RAS-blocker + Diuretico + FANS è letale in pazienti con insufficienza renale conclamata ($\text{eGFR} < 60\,\text{mL/min/1.73m}^2$). Tuttavia, nella pratica clinica reale, molti pazienti ipertesi presentano un eGFR borderline ($55 - 65\,\text{mL/min/1.73m}^2$) con fluttuazioni fisiologiche dovute a disidratazione o carico proteico.
* **Domanda per l'Utente**: Si desidera che l'allerta di **Livello 1 (Blocco Prescrittivo Assoluto)** scatti rigorosamente a $\text{eGFR} < 60$ per qualsiasi FANS indipendentemente dall'emivita, oppure si preferisce consentire un bypass clinico motivato (con contestuale prescrizione di monitoraggio della creatinina sierica a 48 ore) per cicli analgesici ultra-brevi ($\le 3$ giorni) in assenza di proteinuria?

### 3.2 Questione Docimologica 2: Iatrogenesi Temporanea nel Simulatore d'Esame
* **Contesto**: L'invariante docimologico del Modulo 4.1 impone il fallimento istantaneo dell'esame ($\Omega_{\text{lethal}} = 0 \implies 0/30$) in caso di manovra iatrogena grave.
* **Domanda per l'Utente**: Se lo studente commette un errore grave transitorio (es. sovradosaggio di sedativo o beta-bloccante in paziente bradicardico), ma dimostra capacità di rianimazione tempestiva somministrando immediatamente l'antidoto (es. Naloxone, Flumazenil o Atropina) prima che il paziente raggiunga lo stato terminale `S_Exitus`, il sistema deve forzare irrimediabilmente $0/30$ oppure penalizzare pesantemente la Sicurezza del Paziente ($S_P \to 0.05$) consentendo di completare il caso clinico con votazione ridotta (es. $18/30$)?

### 3.3 Questione Farmacologica 3: Ampiezza della Sostituzione Terapeutica
* **Contesto**: Il grafo di equivalenza ATC consente sostituzioni entro la stessa sottoclasse (ATC-4, es. Enalapril $\to$ Ramipril) o verso il target terapeutico principale (ATC-3, es. Enalapril $\to$ Losartan).
* **Domanda per l'Utente**: Si desidera consentire la sostituzione automatica cross-classe da ACE-inibitore a Sartano (ARB, ATC-3) come prima scelta automatica quando la causa di blocco è la tosse refrattaria indotta da bradichinina (ICD-10: R05), oppure il motore deve prioritizzare sempre molecole identiche per meccanismo d'azione (ATC-4)?

### 3.4 Questione Didattica 4: Strategia post-Assenza Prolungata in FSRS ("Cram vs Smoothing")
* **Contesto**: Se uno studente non accede alla piattaforma per 3-4 settimane, la coda di ripasso può accumulare oltre 1.000 card scadute, eccedendo il limite giornaliero sostenibile ($\text{Cap}_{\text{max}} = 350$).
* **Domanda per l'Utente**: Si preferisce che il sistema redistribuisca automaticamente il carico residuo diluendolo sui successivi 7-10 giorni in base alla priorità clinica $\Omega$ (Load Smoothing), oppure si desidera presentare allo studente una modalità esplicita opzionale "Sessione Straordinaria Intensiva" per riassorbire il debito cognitivo prima della ripresa del ciclo normale?

---

## 4. Sorveglianza della Conformità Curativa degli Agenti del Team

In qualità di Auditor Ricorsivo, è stata verificata la conformità dell'intera gerarchia agentica rispetto alle risoluzioni **ROA-01 .. ROA-24**:

| Risoluzione Curativa | Componenti Coinvolti | Stato Conformità nel Codice Reale | Azione Necessaria |
| :--- | :--- | :---: | :--- |
| **ROA-01** (Sovereignty Righe 1255+) | Tutti i file sorgente | **CONFORME (100%)** | Mantenere la tracciabilità delle sole specifiche Iterazione 2. |
| **ROA-02** (Dual SDUI Registry) | `sdui_models.py`, `sduiRegistry.ts` | **CONFORME (100%)** | Piena parità tra nomi canonici e alias formali. |
| **ROA-03** (Hybrid Search, No ChromaDB) | `onnx_semantic.py`, `inverted_dictionary.py` | **CONFORME (100%)** | Nessuna traccia di ChromaDB; ONNX INT8 operativo a 45 MB RAM. |
| **ROA-04** (PyHPO Isolation) | `medfactory/`, `medclient/` | **CONFORME (100%)** | `pyhpo` presente solo in build-time; zero dipendenze sul client. |
| **ROA-05** (Zstd Dict 114.688 B) | `zstd_dictionary_trainer.py` | **CONFORME (100%)** | Target fissato a $114.688\text{ Byte}$ esatti ($112 \times 1024$). |
| **ROA-06** (BLAKE3 + SHA-256 + Ed25519) | `medpack_assembler.py` | **CONFORME (100%)** | Doppio checksum calcolato in streaming e firma canonica. |
| **ROA-07** (Atomic Pointer Windows) | `blue_green_swap.py` | **CONFORME (100%)** | Zero chiamate a symlink; adozione Win32 `MoveFileExW`. |
| **ROA-08** (IPC Stdin Secret Handshake) | `sidecar.rs`, `server.py`, `reverse_watchdog.py` | **CONFORME (100%)** | Secret UUIDv4 passato via stdin; watchdog su PID Tauri. |
| **ROA-09** (Titolare Esclusivo SQLite) | `sqlite_pool.py`, `supervisor.rs` | **CONFORME (100%)** | FastAPI è l'unico proprietario delle connessioni; zero lock contention. |
| **ROA-10** (Profarmaci CYP450 Clopidogrel) | `cyp450_engine.py` | **CONFORME (100%)** | Inversione logica profarmaci con emissione Blackbox Warning Livello 1. |
| **ROA-11** (Zero LLM Client) | `sdui_emitter.py`, `sdui_models.py` | **CONFORME (100%)** | Nessun token stream neurale; schede statiche SSG CommonMark. |
| **ROA-12** (Singleton WebGL Broker) | `SingletonWebGLBroker.ts` | **CONFORME (100%)** | Massimo 1 contesto 3D attivo; distruzione atomica con fallback SVG. |
| **ROA-13** (Isolamento `module_kb` e `user_state`) | `sqlite_pool.py`, `user_state_store.py` | **CONFORME (100%)** | Database didattico e stato utente separati fisicamente. |
| **ROA-14** (FDC Decomposer) | `cyp450_engine.py`, `triple_whammy.py` | **CONFORME (100%)** | Decomposizione deterministica di combinazioni fisse (Co-Aprovel). |
| **ROA-15** (Numeric Stability Rule-Out) | `pertinent_negatives.py` | **CONFORME (100%)** | Penalità limitata $-\tau_{\max} = -12.0$; zero occorrenze di `float('-inf')`. |
| **ROA-16** (Normalizzazione Hotspot $[0, 1]^2$) | `hotspot_evaluator.py`, `hotspotGeometry.ts` | **CONFORME (100%)** | Even-Odd Ray-Casting su coordinate relative indipendenti dal DPI. |
| **ROA-17** (FSRS Fuzzing Deterministico) | `fsrs_scheduler.py` | **CONFORME (100%)** | Dispersione basata su digest crittografico SHA-256 riproducibile. |
| **ROA-18** (Framing `.tar.zst` Dict-Free) | `medpack_assembler.py` | **CONFORME (100%)** | Container esterno dictionary-free; dizionario interno per chunk. |
| **ROA-19** (Manifest Dual-Alias) | `manifest_models.py`, `medpack_assembler.py` | **CONFORME (100%)** | Firma Ed25519 sul payload canonico con signature azzerata. |
| **ROA-20** (Schema DDL STRICT Completo) | `sqlite_pool.py`, `user_state_store.py` | **CONFORME (100%)** | Tabelle SQLite create con clausola formale `STRICT`. |
| **ROA-21** (NEWS2 Scala 2 & Shock Index) | `red_flags.py` | **CONFORME (100%)** | Penalità iperossia condizionata a $O_2$; Shock Index arrotondato a 3 decimali. |
| **ROA-22** (Win32 Job Object RAM Cap) | `supervisor.rs`, `sidecar.rs` | **CONFORME (100%)** | Kill-on-job-close attivo; cap di working set monitorato. |
| **ROA-23** (Loopback Fail-Closed) | `sdui_routes.py`, `server.py` | **CONFORME (100%)** | Verifica `X-Tauri-IPC-Secret` in tempo costante con `hmac.compare_digest`. |
| **ROA-24** (Eccezioni `MedClientError`) | `exceptions.py` | **CONFORME (100%)** | Radice di dominio eredita formalmente da `ValueError`. |

### Residuo Critico da Risolvere (Cohesion Gap):
Mentre i singoli moduli algoritmici implementano fedelmente le ROA-01 .. ROA-24, l'infrastruttura di visualizzazione frontend (`MedClientAppShell.tsx`) e gli handler di route (`sdui_routes.py`) presentavano due scorciatoie che devono essere sanate per raggiungere la perfetta parità operativa (ROA-33):
1. Sostituzione dei `DEFAULT_CLINICAL_SHEET`, `DEFAULT_SYMPTOM_MATCHER`, `DEFAULT_DRUG_SAFETY`, `DEFAULT_EXAM_BLOCK` nel frontend con invocazioni reali a `SidecarIpcClient`.
2. Sostituzione di `posterior_probability = 0.5` e `nbq = None` in `sdui_routes.py` con le chiamate a `LogSumExpNormalizer` e `ActiveDiscriminator`.

---

## 5. Sintesi delle Nuove Assunzioni Operative (ROA-25 .. ROA-34)

Le seguenti 10 nuove assunzioni sono state formalizzate e registrate in `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\AUDIT_AND_ASSUMPTIONS.md`:

1. **`ROA-25`**: Isolamento Media Offline e Bando di Connessioni Esterne per Strutture 3D PDB.
2. **`ROA-26`**: Stabilità Numerica e Limite Asintotico per l'Entropia di Shannon nell'Algoritmo Next-Best-Question (NBQ).
3. **`ROA-27`**: Prevenzione Divisione per Zero e Sanificazione Input Testuale nella Metrica NLI Open-Response ($\Phi$ ed $M=0$).
4. **`ROA-28`**: Validazione Topologica Rigorosa, Bounding Box Fast-Reject e Integrità degli Hotspot Poligonali.
5. **`ROA-29`**: Formalizzazione della Traduzione Farmacogenomica (CPIC Activity Score Matrix per Alleli Stellati).
6. **`ROA-30`**: Riconciliazione tra Ritenzione del DOM (0 ms Latency Tab-Switching) e Virtual Windowing.
7. **`ROA-31`**: Standardizzazione Temporale e Integrità Monotona dei Timestamp FSRS (Secondi Unix Epoch UTC).
8. **`ROA-32`**: Normalizzazione Posologica con Rapporto DDD (Defined Daily Dose) nelle Sostituzioni Terapeutiche.
9. **`ROA-33`**: Eliminazione dei Mock Coded nel Frontend AppShell e Parità Bidirezionale Rigorosa con FastAPI Sidecar.
10. **`ROA-34`**: Prevenzione Divisione per Zero e Clamping nei Parametri del Grafo Clinico Dinamico (Stateful DAG).

---

## 6. Conclusioni e Istruzioni per le Squadre Operative

1. **Aderenza Incondizionata a ROA-01 .. ROA-34**: Tutti i team di sviluppo, revisione e remediation (`worker_remediation_and_m4`, `cohesion_inspector_2`, `curative_enforcer_2`) devono considerare il registro `AUDIT_AND_ASSUMPTIONS.md` (aggiornato a 34 assunzioni) come la specifica formale suprema e prevalente rispetto a qualsiasi testo ambiguo dell'SRS.
2. **Zero Scorciatoie nei Test**: I test di integrazione devono validare le chiamate HTTP reali del client verso il sidecar e il rendering effettivo dei componenti, senza testare stringhe HTML statiche fittizie.
3. **Prossimo Passo**: Gli agenti esecutori procederanno all'eliminazione dei mock statici da `MedClientAppShell.tsx` e `sdui_routes.py` secondo le direttive ROA-33.
