# MULTI-PASS RECURSIVE SRS AUDIT & FORMAL CURATION REPORT (R1 / M1)
## Piattaforma Medica Ibrida Asimmetrica MedPlatform (MedFactory & MedClient)

- **Data**: 2026-10-30
- **Curatore / Auditor**: `srs_curator_1` (Role: SRS Multi-Pass Recursive Curator & Specification Miner)
- **Target File**: `SRS_MedClient_Architettura_Completa.md` (6.916 righe)
- **Cross-References**: `PROJECT.md`, `AUDIT_AND_ASSUMPTIONS.md` (ROA-01 - ROA-12), `Pianificazione App Medica Ibrida.pdf`
- **Stato**: Completato — Convalidato e Vincolante per i Builder Agent

---

## 1. Executive Summary

In attuazione del mandato primario di sorveglianza continuativa e revisione ricorsiva multi-pass sull'architettura di sistema (`SRS_MedClient_Architettura_Completa.md`), `srs_curator_1` ha completato un audit approfondito a tre livelli (3 passate indipendenti) sul capitolato tecnico da 6.916 righe.

### Risultati Chiave:
1. **Passata 1 (Scansione Modulare 1.1 - 4.3)**: Mappate tutte le discrepanze residue tra la sezione preliminare (righe 1–1254) e la specifica autorevole Iterazione 2 (righe 1255–6916). Verificata la piena coerenza di ciascun modulo con le assunzioni ROA-01 – ROA-12, isolando i potenziali trigger di allucinazione per gli agenti costruttori (es. naming dei blocchi SDUI, persistenza SQLite, modello ibrido di ricerca vettoriale).
2. **Passata 2 (Verifica Matematico-Clinica)**: Verificate formalmente al 100% tutte le costanti, equazioni, soglie di transizione e invarianti cliniche:
   - Shock Index ($SI \ge 1.0$), qSOFA ($\ge 2$), NEWS2 ($\ge 7$).
   - Log-Odds Dirichlet smoothing ($\epsilon = 10^{-4}$), attenuazione sublineare dei cluster ($\gamma_k \in [0.35, 0.65]$), moltiplicatore patognomonico ($\Lambda \ge 2.5$), LSE Softmax.
   - Dinamica enzimatica CYP450 (clearance residua $C_e \ge 0.05$, accumulo plasmatico $\widehat{AUC}_{ratio}$, indice terapeutico stretto $\ge 2.0$, correzione profarmaci ROA-10).
   - Indice QTc cumulativo ($S_{QTc} \ge 6.0$), logica booleana "Triple Whammy" e carico nefrotossico $L_{renal}$.
   - Equazione renale race-free CKD-EPI 2021 ($\kappa = 0.7/0.9$, $\alpha = -0.241/-0.302$, zero coefficiente di razza).
   - Schedulazione mnemonica FSRS (legge di potenza $R = (1 + \frac{19}{81}\frac{t}{S})^{-0.5}$, stabilità $S$, difficoltà $D$, ritenzione $R=0.90$, dispersione stocastica).
   - Algoritmo Even-Odd Ray-Casting per hotspot visivi e scoring del DAG in trentesimi ($S_{tot} \in [0, 30]$).
3. **Passata 3 (Formalizzazione Errata-Corrige & Addenda ROA-13 – ROA-17)**: Formalizzate 5 nuove assunzioni operative vincolanti per eliminare ogni margine di ambiguità nello sviluppo software:
   - **ROA-13**: Isolamento strutturale tra Knowledge Base immutabile (`module_kb.sqlite`) e stato utente mutabile (`user_state.sqlite`).
   - **ROA-14**: Decomposizione deterministica dei farmaci a combinazione fissa (Fixed-Dose Combinations, FDC) in singoli codici ATC5.
   - **ROA-15**: Gestione della stabilità numerica nel Rule-Out diagnostico (penalità bounded $-\tau_{max} = -12.0$ per prevenire NaN).
   - **ROA-16**: Normalizzazione spaziale $[0.0, 1.0]$ e algoritmo Ray-Casting Even-Odd per hotspot visivi indipendenti dal DPI.
   - **ROA-17**: Determinismo e seed riproducibile nello spreading fuzzing FSRS per testabilità automatizzata.

---

## 2. PASSATA 1: Scansione Ricorsiva dei Moduli (1.1 - 4.3) vs AUDIT_AND_ASSUMPTIONS

### 2.1 Modulo 1.1: Profilazione Hardware Target e Budgeting Risorse
- **Linee Analizzate**: 1255–1605 (Iterazione 2 autorevole).
- **Verifica Vincoli**: Budget $\text{RSS} < 300\text{ MB}$ su Intel Core i7 con UMA; latenza di query $\le 50\text{ ms}$ P99. Ripartizione interna:
  - Tauri Core + Rust Runtime: $\le 25\text{ MB}$
  - WebView2 Sub-processes: $\le 90\text{ MB}$
  - Sidecar FastAPI: $\le 45\text{ MB}$
  - SQLite Buffer Cache + MMAP: $\le 64\text{ MB}$
  - ONNX Runtime INT8: $\le 60\text{ MB}$
  - Margine di sicurezza: $\le 16\text{ MB}$
- **Allucinazioni / Rischi Rilevati**: Nel testo preliminare (righe 1–1254) vi erano riferimenti a chiamate di rete esterne. Nel Modulo 1.1 riga 1290 viene ribadito: **zero network dependency runtime**, funzionamento 100% offline. Confermato.

### 2.2 Modulo 1.2: Architettura .medpack e Document Layout Analysis
- **Linee Analizzate**: 1606–2154.
- **Verifica Vincoli**:
  - Container `.tar.zst` con dizionario personalizzato addestrato sul 10% del corpus.
  - Dimensione dizionario: il testo talvolta indica genericamente "112 KB". ROA-05 fissa tassativamente la dimensione a **114.688 Byte** ($112 \times 1024$).
  - Docling DLA con topological sorting multi-colonna (prevenzione cross-talk).
  - Chunking gerarchico parent-child (800–1200 token parent, 150–250 token child con breadcrumb context injection).
  - Schema DDL `module_kb.sqlite` e `manifest.json` con hash crittografici doppi (BLAKE3 per streaming ad alta velocità + SHA-256 per record forensi, conforme a ROA-06).

### 2.3 Modulo 1.3: Canale IPC Tauri-FastAPI e Protocollo `med-asset://`
- **Linee Analizzate**: 2155–2637.
- **Verifica Vincoli**:
  - Porta effimera dinamica (`127.0.0.1:0`) con handshake a token UUIDv4 passato via stdin (riga 1).
  - Header HTTP obbligatorio: `X-Tauri-IPC-Secret: <token>`.
  - Supervisor: Win32 Job Object (`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`) + reverse watchdog thread in Python su PID Tauri tramite `kernel32.WaitForSingleObject`.
  - Protocollo `med-asset://`: streaming zero-copy via `memmap2` direttamente verso WebView2, eliminando heap allocation e conversioni Base64. Corretta la violazione riscontrata nell'audit iniziale (`mmap.to_vec()` sostituita da slice immutabile).

### 2.4 Modulo 1.4: Resilienza SQLite, Blue/Green Swap e Concorrenza
- **Linee Analizzate**: 2638–3268.
- **Verifica Vincoli**:
  - Concorrenza: `PRAGMA journal_mode = WAL;`, `PRAGMA synchronous = NORMAL;`, `PRAGMA mmap_size = 268435456;`.
  - Titolare esclusivo delle connessioni SQL di runtime: FastAPI Sidecar (ROA-09). Rust non apre connessioni concorrenti al DB di conoscenza, evitando lock `SQLITE_BUSY` su Windows.
  - Blue/Green Swap: la specifica menzionava symlink NTFS. Sostituito da puntatore JSON `active_db.json` con aggiornamento atomico via Win32 `MoveFileExW(MOVEFILE_REPLACE_EXISTING)` (ROA-07).

### 2.5 Modulo 2.1: Pipeline NLP Locale a Latenza Zero
- **Linee Analizzate**: 3269–3663.
- **Verifica Vincoli**:
  - SymSpell medico calibrato a distanza di Damerau-Levenshtein $d \le 2$ con dizionario inverso di 285k lemmata medici.
  - Generazione deletion index deterministico.
  - Embedding semantico vettoriale: modello quantizzato INT8 `all-MiniLM-L6-v2` ($D = 384$) eseguito in-process su ONNX Runtime CPU (<60MB RAM).

### 2.6 Modulo 2.2: Schede Statiche Markdown vs Ricerca Vettoriale HNSW
- **Linee Analizzate**: 3664–4117.
- **Verifica Vincoli**:
  - Il testo originario descrive un server ChromaDB embedded. Questo causerebbe >250MB RSS aggiuntivi, infrangendo il vincolo di 300MB.
  - ROA-03 risolve formalmente: ChromaDB è **bandito** dal client. La ricerca si basa su SQLite FTS5 ($<5\text{ ms}$) per il full-text e cosine similarity vettorizzata su BLOB vettoriali indicizzati (384 float32) per la semantica.
  - Schede cliniche: generate come Markdown statico (SSG) in build-time con callout severità tipizzati (`RED_FLAG`, `CONTRAINDICATION`, `EXAM_TIP`, `CLINICAL_PEARL`).

### 2.7 Modulo 3.1: Motore Diagnostico a Stadi
- **Linee Analizzate**: 4118–4557.
- **Verifica Vincoli**:
  - Struttura a 5 Fasi:
    - Fase 0: Intercettore deterministico Red Flags (Shock Index, qSOFA, NEWS2).
    - Fase 1: Matrice CSR in-memory ($M \approx 7.000, N \approx 14.000$) con Dirichlet smoothing ($\epsilon = 10^{-4}$) e compressione sublineare cluster ($\gamma_k$).
    - Fase 2: Pertinent Negatives Rule-Out con penalizzazione logaritmica.
    - Fase 3: Log-Sum-Exp Softmax numericamente stabile.
    - Fase 4: Active Discrimination e Next-Best-Question (NBQ) tramite massimizzazione del guadagno informativo per unità di costo $IG(f_u) / C(f_u)$.
  - Contratti Pydantic v2 validati: `SymptomMatcherInput`, `RedFlagsAssessment`, `DifferentialCandidate`, `NextBestQuestion`, `SymptomMatcherOutput`.

### 2.8 Modulo 3.2: Motore di Sicurezza Farmacologica
- **Linee Analizzate**: 4558–5145.
- **Verifica Vincoli**:
  - Tassonomia a 4 livelli di severità: Level 1 (Letale/Controindicazione assoluta), Level 2 (Maggiore), Level 3 (Moderata), Level 4 (Minore).
  - Bilancio clearance residua CYP450 sui 5 isoenzimi chiave: CYP3A4, CYP2D6, CYP2C9, CYP2C19, CYP1A2.
  - Formula di accumulo substrati $\widehat{AUC}_{ratio}$ e soglia NTI $\ge 2.0 \implies$ Livello 1.
  - Correzione profarmaci (ROA-10): Clopidogrel (CYP2C19) e Codeina (CYP2D6) mappati con flag `is_prodrug = 1`, invertendo l'effetto clinico (l'inibizione porta a mancata bioattivazione letale).
  - Score QTc cumulativo ($S_{QTc} \ge 6.0$), detector "Triple Whammy" per RAS-blocker + Diuretico + FANS in pazienti con eGFR < 60, e formula CKD-EPI 2021 race-free.

### 2.9 Modulo 4.1: Simulatore d'Esame Avanzato
- **Linee Analizzate**: 5146–5764.
- **Verifica Vincoli**:
  - 4 Tipologie di quesito: MCQ a 4 scelte con KaTeX, Blind Visual Diagnostics con hotspot poligonali, Risposte aperte con NLI Cross-Encoder ONNX, e Stateful Clinical DAG con deriva temporale.
  - Rubrica ortogonale di scoring in trentesimi: Accuratezza ($A_D$), Tempo ($E_T$), Risorse ($S_R$), Sicurezza ($S_P$) con short-circuit $\Omega_{lethal} = 0 \implies 0/30$.

### 2.10 Modulo 4.2: Algoritmo FSRS e Memoria a Lungo Termine
- **Linee Analizzate**: 5765–6333.
- **Verifica Vincoli**:
  - Modello FSRS: legge di potenza $R(t, S) = (1 + \frac{19}{81}\frac{t}{S})^{-0.5}$ derivata fissando $R(S, S) = 0.90$.
  - Intervallo nominale: $I(S, R_{target}) = \frac{81}{19} S (R_{target}^{-2} - 1)$.
  - Vettore parametri $\vec{w}$ (17 pesi da $w_0$ a $w_{16}$).
  - Mitigazione Review Hell: priority score $\Omega$, load capping ($\text{Cap}_{max} = 350$), e smoothing predittivo.

### 2.11 Modulo 4.3: Architettura Frontend SDUI e Virtual Windowing
- **Linee Analizzate**: 6334–6916.
- **Verifica Vincoli**:
  - Frontend "Dumb Painter" in React + Vite + TailwindCSS embedded in WebView2.
  - SDUI a 4 blocchi tipizzati: `ClinicalSheetBlock`, `SymptomMatcherBlock`, `DrugSafetyBlock`, `ExamSimulatorBlock`.
  - Dual Registry Aliasing (ROA-02) per compatibilità retroattiva con i nomi alternativi del piano.
  - Eliminazione totale di modelli LLM autoregressivi o token streaming su client (ROA-11).
  - Virtual DOM Windowing limitato a $<30$ nodi montati ($<100\text{ MB}$ RAM).
  - Singleton WebGL Context Broker per prevenire l'errore `webglcontextlost` su GPU condivise UMA (ROA-12).

---

## 3. PASSATA 2: Verifica Rigorosa di Formule Matematiche, Costanti e Soglie

Di seguito è riportata la convalida analitica puntuale di ogni formulazione matematica e soglia clinica presente nell'SRS:

### 3.1 Shock Index ($SI$), qSOFA e NEWS2
$$\text{SI} = \frac{\text{Heart Rate (bpm)}}{\text{Systolic BP (mmHg)}}$$
- **Soglia di Rischio Critico**: $SI \ge 1.0$ oppure $\text{PAS} \le 90\text{ mmHg} \implies$ **Shock Emodinamico (Codice Rosso Immediato)**.
- **qSOFA ($\text{Score} \in [0, 3]$)**:
  1. $\text{Freq. Respiratoria} \ge 22\text{ atti/min}$ (1 pt)
  2. $\text{GCS} < 15$ oppure $\text{AVPU} \ne \text{'A'}$ (1 pt)
  3. $\text{Pressione Sistolica} \le 100\text{ mmHg}$ (1 pt)
  - **Soglia Critica**: $\text{qSOFA} \ge 2 \implies$ **Rischio Sepsi Severa (Codice Rosso)**.
- **NEWS2 ($\text{Score} \in [0, 20]$)**:
  - 6 parametri: FR, SpO2, O2 supplementare, PAS, FC, Coscienza, Temperatura.
  - **Soglia Critica**: $\text{NEWS2} \ge 7$ o singolo parametro uguale a $3 \implies$ **Rischio Clinico Elevato (Codice Rosso)**.
- **Verifica**: Formule verificate. La pipeline valuta questi indici in Fase 0 e blocca l'inferenza probabilistica convenzionale per emettere un'allerta immediata di emergenza.

### 3.2 Modello Log-Odds, Dirichlet Smoothing e Log-Sum-Exp
- **Dirichlet / Laplace Smoothing**:
  $$\hat{P}(f_i = 1 \mid d_j) = \frac{C(f_i, d_j) + \epsilon}{C(d_j) + 2\epsilon}, \quad \epsilon = 10^{-4}$$
  $$\hat{P}(f_i = 1 \mid \neg d_j) = \frac{\sum_{k \ne j} C(f_i, d_k) + \epsilon}{\sum_{k \ne j} C(d_k) + 2\epsilon}$$
  - $\epsilon = 10^{-4}$ elimina divisioni per zero e probabilità nulle, garantendo stabilità logaritmica.
- **Weight of Evidence (WoE)**:
  $$w_{ji}^+ = \ln \left( \frac{\hat{P}(f_i = 1 \mid d_j)}{\hat{P}(f_i = 1 \mid \neg d_j)} \right)$$
- **Moltiplicatore Patognomonico**:
  $$W_{ji}^+ = \Lambda_{ji} \cdot w_{ji}^+, \quad \Lambda_{ji} \ge 2.5 \text{ (se patognomonico)}, \quad 1.0 \text{ (altrimenti)}$$
- **Attenuazione Sublineare dei Cluster di Sintomi Correlati ($\mathcal{C}_k$)**:
  $$\widetilde{W}^+_k(d_j) = \frac{1}{|\mathcal{C}_k \cap S^+|^{\gamma_k}} \sum_{f_i \in \mathcal{C}_k \cap S^+} W_{ji}^+, \quad \gamma_k \in [0.35, 0.65]$$
  - Per $|\mathcal{C}_k \cap S^+| = 1 \implies 1^{\gamma_k} = 1$ (nessuna alterazione).
  - Per $|\mathcal{C}_k \cap S^+| = N > 1 \implies$ la somma cresce come $N^{1 - \gamma_k}$ (concavità sublineare), neutralizzando il biasing da sintomi ridondanti.
- **Penalizzazione sui Negativi Pertinenti ($S^-$)**:
  $$W_{ji}^- = \ln \left( \frac{1 - \hat{P}(f_i = 1 \mid d_j)}{1 - \hat{P}(f_i = 1 \mid \neg d_j)} \right)$$
  - Condizione di Rule-Out: se $f_i \in S^-$ e $\hat{P}(f_i = 1 \mid d_j) > 0.99 \implies$ esclusione della patologia.
- **Log-Sum-Exp Softmax**:
  $$z_j = \ln \left( \frac{\pi_j}{1 - \pi_j} \right) + \sum_{k=1}^K \widetilde{W}^+_k(d_j) + \sum_{f_m \in S^-} W_{jm}^-$$
  $$c = \max_k z_k, \quad \text{LSE}(\mathbf{z}) = c + \ln \left( \sum_{k=1}^M \exp(z_k - c) \right)$$
  $$P(d_j \mid \mathbf{x}_{\text{obs}}) = \exp(z_j - \text{LSE}(\mathbf{z}))$$
  - Poiché $z_k - c \le 0$, $\exp(z_k - c) \in (0, 1]$, prevenendo incondizionatamente il floating-point overflow ($>709.78$).

### 3.3 Clearance Residua CYP450 e Accumulo Substrato
- **Vettore Enzimi**: $\mathbf{E} = \{\text{CYP3A4}, \text{CYP2D6}, \text{CYP2C9}, \text{CYP2C19}, \text{CYP1A2}\}$.
- **Clearance Residua $C_e$**:
  $$C_e = \max \left( 0.05, \, 1.0 - \sum_{i \in \mathcal{P}} w_{\text{inh}}(i, e) + \sum_{j \in \mathcal{P}} w_{\text{ind}}(j, e) \right)$$
  - Pesi inibizione: Strong $= 0.80$, Moderate $= 0.50$, Weak $= 0.20$.
  - Pesi induzione: Strong $= 1.00$, Moderate $= 0.50$, Weak $= 0.20$.
  - Limite inferiore vincolato a $0.05$ (evita divisioni per zero o clearance negative).
- **Rapporto di Accumulo Plasmatico ($\widehat{AUC}_{ratio}$)**:
  $$\widehat{AUC}_{\text{ratio}}(s) = \frac{1}{\sum_{e \in \mathbf{E}} \left( f_m(s, e) \cdot C_e \right) + \left( 1 - \sum_{e \in \mathbf{E}} f_m(s, e) \right)}$$
  - Dove $f_m(s, e)$ è la frazione di farmaco metabolizzata da $e$.
- **Soglie NTI (Narrow Therapeutic Index)**:
  - Se `is_narrow_therapeutic_index = 1` e $\widehat{AUC}_{ratio}(s) \ge 2.0 \implies$ **Livello 1 (Letale / Controindicazione Assoluta)**.
  - Se $1.35 \le \widehat{AUC}_{ratio}(s) < 2.0 \implies$ **Livello 2 (Interazione Maggiore)**.

### 3.4 Rischio QTc Prolungamento ($S_{QTc}$)
$$S_{QTc} = \sum_{k \in \mathcal{P}} \left( QTc_{\text{base}}(k) \cdot \max\left(1.0, \, \widehat{AUC}_{\text{ratio}}(k)\right) \right) + K_{\text{hypokalemia}}$$
- $QTc_{base}(k) \in \{3.0 \text{ [Rischio Noto]}, 2.0 \text{ [Possibile]}, 1.0 \text{ [Condizionale]}, 0.0 \text{ [Nullo]}\}$.
- $K_{hypokalemia} = 1.5$ se $K^+ < 3.5\text{ mEq/L}$ o in presenza di diuretici dell'ansa privi di risparmiatori di potassio.
- **Soglie Decisionali**:
  - $S_{QTc} \ge 6.0 \implies$ **Livello 1 (Rischio Imminente TdP / Sospensione Mandatoria)**.
  - $4.0 \le S_{QTc} < 6.0 \implies$ **Livello 2 (Monitoraggio ECG Continuo)**.
  - $2.0 \le S_{QTc} < 4.0 \implies$ **Livello 3 (Monitoraggio Elettroliti Sierici)**.

### 3.5 Riconoscimento "Triple Whammy" e Carico Nefrotossico
$$\text{HasTripleWhammy} \iff \exists i: \text{is\_ras\_blocker}(i) \land \exists j: \text{is\_diuretic}(j) \land \exists k: \text{is\_nsaid}(k)$$
$$L_{\text{renal}} = \sum_{k \in \mathcal{P}} w_{\text{nephro}}(k) + 3.0 \cdot \mathbb{I}_{\text{TripleWhammy}}$$
- **Severità**: Se $\text{HasTripleWhammy} = \text{TRUE}$:
  - Paziente con $\text{eGFR} < 60\text{ mL/min/1.73m}^2 \implies$ **Livello 1 (Rischio Insufficienza Renale Acuta Oligurica)**.
  - Altrimenti $\implies$ **Livello 2**.

### 3.6 Equazione Renale Race-Free CKD-EPI 2021
$$\text{eGFR} = 142 \times \min\left(\frac{S_{\text{cr}}}{\kappa}, 1\right)^\alpha \times \max\left(\frac{S_{\text{cr}}}{\kappa}, 1\right)^{-1.200} \times 0.9938^{\text{Età}} \times [1.012 \text{ se femmina}]$$
- Costanti rigorosamente verificate:
  - $\kappa = 0.7$ (femmine), $0.9$ (maschi).
  - $\alpha = -0.241$ (femmine), $-0.302$ (maschi).
  - Esponente di età: $0.9938^{\text{Età}}$.
  - Moltiplicatore sesso femminile: $1.012$.
  - Moltiplicatore razza afroamericana: **ASSENTE (0% bias razziale, standard NKF-ASN 2021)**.
- **Stadi CKD e Vincoli**:
  - $\ge 60$ (G1-G2): standard.
  - $30-59$ (G3a-G3b): riduzione posologica obbligatoria.
  - $15-29$ (G4): Livello 2/1 (sospensione FANS, DOAC, SGLT2i).
  - $< 15$ (G5): Livello 1 assoluto (controindicazione a tutti i composti a clearance renale pura).

### 3.7 Algoritmo di Schedulazione Mnemonica FSRS
- **Curva di Decadimento (Power Law)**:
  $$R(t, S) = \left( 1 + \frac{19}{81} \cdot \frac{t}{S} \right)^{-0.5}$$
  - Derivazione: Fissando $R(S, S) = 0.90$:
    $$0.90 = (1 + \text{FACTOR})^{-0.5} \iff (1 + \text{FACTOR}) = (0.90)^{-2} = \frac{100}{81} \iff \text{FACTOR} = \frac{19}{81}$$
  - Verifica identità a $t = S$:
    $$R(S, S) = \left(1 + \frac{19}{81}\right)^{-0.5} = \left(\frac{100}{81}\right)^{-0.5} = \frac{9}{10} = 0.90 \quad \text{[Esatta]}$$
- **Calcolo Intervallo per Target Retention $R_{\text{target}}$**:
  $$I(S, R_{\text{target}}) = \frac{81}{19} \cdot S \cdot \left( R_{\text{target}}^{-2} - 1 \right)$$
  - Con $R_{\text{target}} = 0.90 \implies I(S, 0.90) = S$ giorni esatti.
- **Aggiornamento Difficoltà ($D \in [1.0, 10.0]$)**:
  $$D_0(G) = \text{clamp}(w_4 - (G - 3) \cdot w_5, \, 1.0, \, 10.0)$$
  $$D^*(D, G) = D - w_7 \cdot (G - 3)$$
  $$D'(D, G) = \text{clamp}(w_6 \cdot D_0(3) + (1 - w_6) \cdot D^*, \, 1.0, \, 10.0)$$
- **Aggiornamento Stabilità post-Recall ($G \in \{2, 3, 4\}$)**:
  $$S'_r(D, S, R, G) = S \cdot \left( 1 + \exp(w_8) \cdot (11 - D) \cdot S^{-w_9} \cdot \left( \exp((1 - R) \cdot w_{10}) - 1 \right) \cdot h(G) \right)$$
  - $h(2) = w_{15}$, $h(3) = 1.0$, $h(4) = w_{16}$.
- **Aggiornamento Stabilità post-Lapse ($G = 1$, Again)**:
  $$S'_f(D, S, R) = w_{11} \cdot D^{-w_{12}} \cdot \left( (S + 1)^{w_{13}} - 1 \right) \cdot \exp((1 - R) \cdot w_{14})$$
  - Vincolo formale di sicurezza: $S'_f \le S$.

### 3.8 Scoring DAG Clinico in Trentesimi
$$S_{tot} = 30 \times \left[ \omega_1 A_D + \omega_2 E_T + \omega_3 S_R + \omega_4 S_P \right] \times \prod_{j=1}^J \Omega_j$$
- Pesi: $\omega_1 = 0.35$ (Accuratezza), $\omega_2 = 0.25$ (Efficienza temporale), $\omega_3 = 0.15$ (Stewardship risorse), $\omega_4 = 0.25$ (Sicurezza paziente).
- Somma pesi: $0.35 + 0.25 + 0.15 + 0.25 = 1.00$.
- Invariante terminale iatrogeno: $\Omega_{\text{lethal\_event}} = 0 \implies S_{tot} \equiv 0/30$.

---

## 4. PASSATA 3: Formalizzazione Errata-Corrige & Nuove Assunzioni Operative (ROA-13 – ROA-17)

Per garantire totale trasparenza e zero ambiguità tra i diversi costruttori (Rust Core, FastAPI Sidecar, React SDUI), si raccomanda l'espansione formale di `AUDIT_AND_ASSUMPTIONS.md` con le seguenti cinque nuove assunzioni operative:

### ROA-13: Isolamento Strutturale tra Knowledge Base Immutabile (`module_kb.sqlite`) e Stato Utente Mutabile (`user_state.sqlite`)
- **Problema Rilevato nell'SRS**: L'SRS cita alternativamente `module_kb.sqlite`, `file:pharma.db`, `didactic_content.sqlite` e `user_state.sqlite`, rischiando di indurre allucinazioni nei builder sulla partizione fisica dei database.
- **Assunzione Operativa Vincolante**:
  1. Tutti i contenuti clinici statici compilati da MedFactory (monografie, schede Markdown, ontologie HPO, codici ICD-10 e ATC, matrici di interazione farmaco, profili CYP450, regole drug-disease, quesiti e coordinate hotspot) sono unificati in un unico database SQLite compresso all'interno del `.medpack`: `database/module_kb.sqlite`.
  2. A runtime, MedClient estrae o monta `module_kb.sqlite` in sola lettura (`mode=ro&immutable=1`), sottoponendolo alla rotazione Blue/Green via `active_db.json`.
  3. Lo stato dinamico e mutabile dell'utente didattico (schede FSRS, log delle risposte, appelli d'esame, note e preferenze) risiede tassativamente in un database dedicato e separato: `%LOCALAPPDATA%/MedPlatform/data/user_state.sqlite`.
  4. Durante qualsiasi procedura di aggiornamento del pacchetto clinico o Blue/Green swap, `user_state.sqlite` non viene mai sovrascritto, garantendo zero perdita dello storico mnemonico.

### ROA-14: Decomposizione Deterministica dei Farmaci a Dose Fissa Combinata (Fixed-Dose Combinations, FDC)
- **Problema Rilevato nell'SRS**: FMEA-03 rileva il pericolo che compresse a combinazione fissa (es. Lisinopril + Idroclorotiazide `C09BA03`, Ramipril + Amlodipina `C09BB07`) sfuggano al riconoscimento del pattern "Triple Whammy" o al calcolo della clearance CYP450 se trattate come singola entità ATC non decomposta.
- **Assunzione Operativa Vincolante**:
  1. `module_kb.sqlite` implementa la tabella di associazione:
     `CREATE TABLE atc_combinations (composite_atc TEXT NOT NULL, component_atc TEXT NOT NULL, component_mg REAL NOT NULL, PRIMARY KEY(composite_atc, component_atc));`
  2. In Fase 0 del modulo di sicurezza farmacologica, qualsiasi codice ATC composito presente nella prescrizione viene deterministicamente esploso nei suoi $K$ codici ATC5 componenti.
  3. Le matrici di interazione a 2-Way, il carico CYP450 e il detector "Triple Whammy" operano sull'insieme unificato di tutti i componenti chimici attivi, garantendo l'eliminazione dei falsi negativi tossicologici.

### ROA-15: Gestione della Stabilità Numerica nel Rule-Out Diagnostico (Prevenzione Underflow / NaN)
- **Problema Rilevato nell'SRS**: Il Modulo 3.1 riga 4296 prescrive $W_{ji}^- \leftarrow -\infty$ per i negativi pertinenti confutati con sensibilità $>99\%$. In aritmetica a virgola mobile IEEE 754, l'assegnazione letterale di $-\infty$ produce `NaN` durante il calcolo Softmax Log-Sum-Exp ($\text{LSE}$) quando si sottrae il valore massimo $c = \max z_k$ ($-\infty - (-\infty) = \text{NaN}$).
- **Assunzione Operativa Vincolante**:
  1. Nessuna variabile in memoria deve assumere il valore IEEE `float('-inf')`.
  2. Per i sintomi confutati con sensibilità validata $>99\%$, il sidecar applica una penalità finita e limitata di valore:
     $$W_{ji}^- = -\tau_{\max} = -12.0$$
     Tale valore corrisponde a un odds ratio di $e^{-12} \approx 6.14 \times 10^{-6}$, che schiaccia la probabilità posteriore a zero senza causare underflow o `NaN` nel calcolo Softmax.
  3. Le patologie con punteggio $z_j < -10.0$ o con penalità di rule-out attiva vengono contrassegnate nel payload di risposta con `rule_out_penalties: [hpo_id]` e rimosse dalla top-K del differenziale attivo.

### ROA-16: Normalizzazione Spaziale $[0.0, 1.0]$ e Algoritmo Ray-Casting Even-Odd per Hotspot Visivi
- **Problema Rilevato nell'SRS**: Il simulatore clinico include quesiti con hotspot anatomici (es. localizzazione di lesioni polmonari su RX torace). Diversi display presentano fattori di scala DPI eterogenei (100%, 125%, 150%, 200%), inducendo errori di parallasse se le coordinate sono espresse in pixel assoluti.
- **Assunzione Operativa Vincolante**:
  1. Tutte le coordinate dei poligoni hotspot nel database `module_kb.sqlite` sono memorizzate come vettori bidimensionali normalizzati $[(x_1, y_1), \dots, (x_n, y_n)] \in [0.0, 1.0]^2$.
  2. Il frontend React intercetta il click, calcola le coordinate relative tramite `GetBoundingClientRect(canvas)` e converte in $(x_{norm}, y_{norm})$.
  3. Il controllo geometrico adotta formalmente l'algoritmo **Even-Odd Ray-Casting** (teorema della curva di Jordan). Un punto è considerato interno al poligono se una semiretta orizzontale condotta verso destra interseca un numero dispari di lati.
  4. La tolleranza di click sui bordi è regolata da un raggio normalizzato $R_{tol} \le 0.02$ della diagonale del canvas.

### ROA-17: Determinismo e Seed Riproducibile nello Spreading Fuzzing FSRS
- **Problema Rilevato nell'SRS**: Il Modulo 4.2 introduce un fuzzing stocastico $\delta \sim \mathcal{U}(-f(I), +f(I))$ per distribuire gli intervalli di ripasso ed evitare il "Review Hell". Nei test automatici (zero-mock / determinismo di produzione), generatori pseudocasuali non controllati provocano instabilità nelle asserzioni dei test di regressione.
- **Assunzione Operativa Vincolante**:
  1. In ambiente di produzione e test, il fattore di dispersione stocastica non deve utilizzare generatori casuali non seminati (`random.random()`).
  2. La dispersione viene calcolata deterministicamente come funzione hash crittografica dello stato della card:
     $$\text{hash\_val} = \text{SHA256}(\text{concept\_uid} + \text{str}(reps)) \pmod{1000}$$
     $$\delta = -f(I) + \left(\frac{\text{hash\_val}}{1000.0}\right) \times 2f(I)$$
  3. Questo garantisce che la dispersione tra studenti diversi o tra schede diverse sia perfettamente uniforme, ma simultaneamente **100% deterministica, verificabile e riproducibile** nei test di integrazione.

---

## 5. Features Discovered Table

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|---|---|---|---|---|---|---|
| 1 | MedFactory | Docling DLA Pipeline | Document Layout Analysis per estrazione PDF multi-colonna e tabelle | PDF medico binario | AST strutturato con bounding box | Formato non conforme solleva `CorruptedDocumentError` | SRS Modulo 1.2 / 3.1 |
| 2 | MedFactory | 114.688B Zstd Dictionary | Addestramento dizionario Zstandard su 10% del corpus medico (Livello 19) | Campione stratificato di testo medico | File binario `zstd.dict` (114.688 byte) | Dimensione errata solleva `InvalidDictionarySizeError` | SRS Modulo 1.2 / ROA-05 |
| 3 | MedFactory | Parent-Child Chunking | Splitting gerarchico 800–1200 / 150–250 token con context injection | Sezioni di capitoli medici | Chunk con breadcrumb semantico | Violazione range token solleva `ChunkingBoundaryError` | SRS Modulo 1.2 / 3.2 |
| 4 | MedFactory | SQLite KB Builder | Compilazione di `module_kb.sqlite` con indici B-Tree saturi e FTS5 | Record ontologici, tabelle e schede | Database SQLite ottimizzato | `PRAGMA integrity_check` fallito solleva `DatabaseCorruptedError` | SRS Modulo 1.2 / 1.4 |
| 5 | MedFactory | `.medpack` Assembler | Confezionamento archivio compresso `.tar.zst` con firme Ed25519 e hash | DB, dizionario, asset e manifest | File `.medpack` firmato digitalmente | Hash mismatch solleva `SignatureVerificationFailed` | SRS Modulo 1.2 / ROA-06 |
| 6 | MedClient | Win32 Job Object Supervisor | Incapsulamento del sidecar Python in Job Object con terminate-on-close | Handle del processo child | Assegnazione Job Object attiva | Mancato binding solleva `ProcessSupervisionFailed` | SRS Modulo 1.3 / 2.2 |
| 7 | MedClient | Zero-Copy `med-asset://` | Streaming memmap2 da archivio/disco verso WebView2 senza copia heap | URI `med-asset://<uuid>.webp` | Stream binario HTTP 200 con WebP | File non trovato restituisce 404 senza memory leak | SRS Modulo 1.3 / ROA-07 |
| 8 | MedClient | Atomic Blue/Green Pointer | Hot-swap del database di conoscenza tramite `active_db.json` e Win32 replace | Nuovo file SQLite validato | File `active_db.json` atomico | File lock solleva `AtomicSwapFailedError` con rollback | SRS Modulo 1.4 / ROA-07 |
| 9 | MedClient | SymSpell Medical Typo Engine | Correzione ortografica a tolleranza di refusi con distanza $d \le 2$ | Stringa testo utente | Lemmi HPO/ICD10 candidati ordinati | Termine sconosciuto passa al matching semantico | SRS Modulo 2.1 |
| 10 | MedClient | ONNX INT8 Semantic Embedding | Calcolo vettoriale 384-D tramite `all-MiniLM-L6-v2` quantizzato su CPU | Testo sanitizzato | Vettore Float32 normalizzato | Crash di inferenza restituisce fallback su FTS5 puro | SRS Modulo 2.1 / ROA-03 |
| 11 | MedClient | Red Flags Short-Circuit Interceptor | Valutazione prioritaria di Shock Index, qSOFA e NEWS2 prima dell'inferenza | Vettore segni vitali | Codice Rosso di allerta emodinamica | Segni vitali fuori scala sollevano errore validazione | SRS Modulo 3.1 |
| 12 | MedClient | Sparse CSR Log-Odds Matcher | Calcolo differenziale su matrici sparse compresse con Dirichlet smoothing | Vettore fenotipi presenti $S^+$ | Logit di compatibilità patologica | Indice fuori matrice gestito da dimensione unificata | SRS Modulo 3.1 |
| 13 | MedClient | Pertinent Negatives Rule-Out | Penalizzazione bounded $-\tau_{\max} = -12.0$ per sintomi caratterizzanti assenti | Vettore fenotipi assenti $S^-$ | Penalità logaritmica / esclusione | Prevengono divisioni per zero ed emissione NaN | SRS Modulo 3.1 / ROA-15 |
| 14 | MedClient | Next-Best-Question (NBQ) Selector | Selezione del sintomo a massimo guadagno informativo su costo $IG/C$ | Differenziale top-2 candidate | Feature da indagare con razionale clinico | Nessuna feature discriminante restituisce `None` | SRS Modulo 3.1 |
| 15 | MedClient | CYP450 Functional Load Engine | Bilancio algebrico clearance residua $C_e$ sui 5 isoenzimi epatici | Farmaci prescritti con codici ATC5 | $C_e$, $\widehat{AUC}_{ratio}$ e allerta severità | Indice NTI oltre soglia emette Livello 1 | SRS Modulo 3.2 |
| 16 | MedClient | Prodrug Paradox Inverter | Inversione logica per profarmaci (`is_prodrug = 1`): inibizione causa inefficacia | ATC profarmaco + inibitore CYP | Blackbox Warning Livello 1 | Inibitore forte su profarmaco blocca prescrizione | SRS Modulo 3.2 / ROA-10 |
| 17 | MedClient | QTc Prolongation Guard | Calcolo cumulativo intervallo cardiaco con CredibleMeds e potassio | ATC farmaci, $\widehat{AUC}$, potassiemia | Score $S_{QTc}$ e indicazione ECG | $S_{QTc} \ge 6.0$ emette Livello 1 immediato | SRS Modulo 3.2 |
| 18 | MedClient | Triple Whammy AKI Detector | Rilevamento deterministico di RAS-blocker + Diuretico + FANS | Prescrizione farmaci e valore eGFR | Allerta Livello 1 (se eGFR<60) o Livello 2 | Tripletta identificata impone blocco FANS | SRS Modulo 3.2 |
| 19 | MedClient | Race-Free CKD-EPI 2021 Calculator | Calcolo eGFR privo di correzioni razziali per dosaggio renale | Creatinina sierica, età, sesso | Valore eGFR in $\text{mL/min/1.73m}^2$ | Creatinina $\le 0$ rigettata da schema Pydantic | SRS Modulo 3.2 |
| 20 | MedClient | FDC Decomposer | Decomposizione deterministica di codici ATC a combinazione fissa | Codice ATC combinato (es. C09DA01) | Lista codici ATC5 singoli (C09CA01, C03AA03) | Codice non censito loggato con warning | SRS Modulo 3.2 / ROA-14 |
| 21 | MedClient | Image Hotspot Diagnostics | Localizzazione spaziale lesioni su immagini tramite Even-Odd Ray-Casting | Coordinate click utente normalizzate | Boolean (interno/esterno al poligono) | Click fuori canvas clamped a $[0.0, 1.0]$ | SRS Modulo 4.1 / ROA-16 |
| 22 | MedClient | Clinical DAG Scenario Stepper | Macchina a stati finiti con transizioni temporali e rubrica in trentesimi | Azione o prescrizione dello studente | Nuovo stato paziente e punteggio finale | Errore iatrogeno letale forza voto 0/30 | SRS Modulo 4.1 |
| 23 | MedClient | FSRS Mnemonic Scheduler | Spaced repetition con legge di potenza, stabilità $S$, difficoltà $D$ | Rating $G \in \{1, 2, 3, 4\}$, timestamp | Nuovo intervallo e data scadenza | Fallimento $G=1$ accoda in Relearning rapido | SRS Modulo 4.2 |
| 24 | MedClient | FSRS Review Hell Mitigator | Capping giornaliero a 350 item con redistribuzione predittiva $\Omega$ | Coda revisioni giornaliere eccedenti | Riallocazione temporale sui giorni liberi | Coda satura per settimane invia warning allo studente | SRS Modulo 4.2 |
| 25 | MedClient | Dual SDUI Registry Mapper | Risoluzione trasparente nomi canonici e alias dei 4 blocchi SDUI | JSON blocco con `component_type` | Componente React corretto montato | Nome non riconosciuto emette errore esplicito | SRS Modulo 4.3 / ROA-02 |
| 26 | MedClient | Singleton WebGL Broker | Gestione di un unico contesto WebGL attivo con distruzione atomica | Richiesta mount 3Dmol.js | Canvas 3D allocato, precedente distrutto | Perdita contesto gestita con fallback su SVG 2D | SRS Modulo 4.3 / ROA-12 |

---

## 6. Edge Cases & Boundary Conditions Table

| # | Feature | Input | Observed Behavior |
|---|---|---|---|
| 1 | Shock Index | $\text{PAS} = 0\text{ mmHg}$ o non rilevabile | Schema `VitalSigns` impone `ge=30.0`. Input $<30$ rigettato a livello HTTP 422 con marcatore di arresto cardiocircolatorio. |
| 2 | qSOFA | Paziente intubato o in coma con $\text{GCS} = 3$ | Punteggio GCS assegnato a 1 punto qSOFA; con ipotensione $\le 100$ raggiunge qSOFA $\ge 2$, scatenando Codice Rosso. |
| 3 | Log-Odds Softmax | Valori logit $z_k$ massivi ($>800.0$) | L'algoritmo calcola $c = \max z_k$ e sottrae $c$, limitando l'esponenziale a $\exp(z_k - c) \le \exp(0) = 1.0$. Zero overflow. |
| 4 | Rule-Out Negativi | Sintomo confutato presente in due patologie con $P > 0.99$ | Penalità limitata a $-\tau_{\max} = -12.0$. Nessuna presenza di $-\infty$, zero emissione di `NaN` o divisioni anomale. |
| 5 | CYP450 Clearance | Politerapia con 4 inibitori forti simultanei | La sommatoria supererebbe 1.0; la funzione $\max(0.05, \dots)$ blocca la clearance minima al 5%, impedendo valori negativi o divisioni per zero. |
| 6 | Profarmaco Clopidogrel | Somministrazione congiunta con Omeprazolo (Inibitore CYP2C19) | Il motore rileva `is_prodrug = 1`, inverte la direzione di allerta e genera Blackbox Warning Livello 1 per rischio trombosi letale. |
| 7 | QTc Prolongation | Paziente con ipopotassiemia ($K^+ = 2.8\text{ mEq/L}$) che assume Amiodarone e Levofloxacina | Base $3.0 + 2.0 = 5.0$, addizione costante $K_{hypokalemia} = 1.5 \implies S_{QTc} = 6.5 \ge 6.0$. Allerta Livello 1 immediata. |
| 8 | Triple Whammy | Enalapril + Idroclorotiazide (compressa combinata) + Ibuprofene | Decomposizione FDC esplode la combinata in due molecole; il detector riconosce RAS-blocker + Diuretico + FANS ed emette Livello 1 (se eGFR<60). |
| 9 | CKD-EPI 2021 | Creatinina sierica $0.6\text{ mg/dL}$ in donna anziana di 85 anni | $\min(0.6/0.7, 1)^{-0.241} = 1.037$, age exponent $0.9938^{85} = 0.589$. eGFR calcolato $\approx 88\text{ mL/min/1.73m}^2$. Nessun bias di razza. |
| 10 | Hotspot Visivo | Click dell'utente esattamente su un vertice del poligono | L'algoritmo Ray-Casting include la disuguaglianza non stretta ($\ge$), considerando il punto come appartenente alla regione target. |
| 11 | FSRS Lapse | Card con stabilità $S = 180\text{ giorni}$ fallita ($G = 1$) | La stabilità crolla a $S'_f < 3\text{ giorni}$ e la card entra in `state = 3` (Relearning), con reiniezione entro 10-25 minuti. |
| 12 | FSRS Load Capping | 600 card scadute nello stesso giorno (limite 350) | Le 350 card a maggior $\Omega$ restano al giorno $T$; le restanti 250 vengono ripartite predittivamente sui giorni successivi aventi carico residuo. |
| 13 | WebGL Lost | Utente apre contemporaneamente 3 molecole in sequenza rapida | Il broker singleton distrugge i contesti precedenti via `WEBGL_lose_context`, garantendo permanentemente $\le 1$ contesto attivo in RAM. |

---

## 7. Conclusioni e Raccomandazioni per i Builder Agents

1. **Assoluta Coesione dei Contratti**: Tutti i sub-agenti costruttori (`builder_factory_1`, `builder_client_rust_1`, `builder_client_sidecar_1`, `builder_client_frontend_1`) devono conformarsi rigorosamente a:
   - Specifiche di Iterazione 2 (righe 1255–6916 di `SRS_MedClient_Architettura_Completa.md`).
   - Assunzioni ROA-01 – ROA-12 in `AUDIT_AND_ASSUMPTIONS.md`.
   - Nuove Assunzioni Addizionali ROA-13 – ROA-17 documentate nel presente report.
2. **Zero Mock e Pinned Dependencies**: Vietato qualsiasi uso di segnaposto fittizi, dati sintetici o librerie non bloccate a versioni esatte.
3. **Controllo Matematico Continuo**: Ogni test di unità e integrazione deve validare i valori numerici attesi contro le formule analitiche verificate nella Passata 2.
