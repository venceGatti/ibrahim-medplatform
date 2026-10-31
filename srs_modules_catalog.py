#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Catalogo dei Moduli Architetturali e Direttive Iper-Tecniche per la Generazione SRS.
Estratto da generatore_architettura.py per il rispetto rigoroso del limite di micro-file (<= 300 righe).
"""

from typing import List, Dict

MASTER_PLAN_MODULES: List[Dict[str, str]] = [
    {
        "titolo_capitolo": "Modulo 1.1: Profilazione Hardware Target, Asimmetria MedFactory/MedClient e Limiti di Risorse",
        "direttive": """
Redigere la specifica tecnica ingegneristica per il Modulo 1.1: Profilazione Hardware e Asimmetria del Sistema.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Definire i profili hardware asimmetrici: MedFactory (Build-Time su GPU NVIDIA RTX 4050 6GB VRAM, CPU AMD Ryzen 7) e MedClient (Run-Time su CPU Intel Core i7, 8-16 GB RAM condivisa, NESSUNA GPU dedicata).
   - Fissare i vincoli operativi rigidi sul MedClient: budget RAM resident set size (RSS) < 300 MB complessivi, latenza di risposta alle query < 50 ms.
   - Spiegare perché il paradigma client-server domestico asincrono (WAN tra PC personali) è stato scartato a favore della totale disconnessione runtime con distribuzione a pacchetti statici.
2. Medical AI Specialist:
   - Dimostrare l'incompatibilità dei modelli LLM generativi locali sul client per la generazione di schede cliniche (collasso RAM, lentezza >15s, allucinazioni posologiche).
   - Definire il ruolo dell'AI sul client: inferenza deterministica, ricerca semantica ultraleggera e modelli discriminativi NLI compilati in ONNX Runtime.
3. QA Critic:
   - Analizzare i punti di rottura hardware: scenari di esaurimento memoria (RAM bloat) su macchine con 8 GB condivisi con grafica integrata.
   - Definire i protocolli di throttling automatico e le policy di degradazione delle prestazioni in caso di esecuzione su batteria o carico di sistema > 80%.
4. Technical Writer:
   - Redigere in Markdown formale con tabelle comparative hardware, vincoli prestazionali e requisiti funzionali/non-funzionali misurabili.
""",
    },
    {
        "titolo_capitolo": "Modulo 1.2: Architettura e Creazione dei .medpack (Docling DLA, Chunking Gerarchico e Compressione Zstd)",
        "direttive": """
Redigere la specifica tecnica ingegneristica per il Modulo 1.2: Pipeline di Packaging e Compressione della MedFactory.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Definire l'anatomia interna del file archivio `.medpack`: archivio compresso Zstandard (.tar.zst) contenente `manifest.json`, `module_kb.sqlite`, `vector_index/` e `assets_media/`.
   - Specificare la pipeline di build deterministica e riproducibile (normalizzazione timestamp a Unix Epoch 0, ordinamento lessicografico dei file, deframmentazione SQLite con VACUUM INTO).
   - Descrivere l'addestramento preventivo del dizionario di compressione Zstd da 112 KB specializzato su terminologia medica per raggiungere un throughput di decompressione > 1.2 GB/s sul client.
2. Medical AI Specialist:
   - Dettagliare la Document Layout Analysis (DLA) tramite IBM Docling / Marker: decomposizione visiva, lettura multi-colonna senza fusione, isolamento topologico delle tabelle cliniche senza appiattimento cellulare.
   - Formalizzare il Chunking Gerarchico Parent-Child: Blocchi Padre da 800-1200 token salvati su SQLite e Micro-blocchi Figlio da 150-250 token per l'indice vettoriale, integrati con Breadcrumb Context Injection gerarchico.
   - Tracciamento obbligatorio e immutabile delle fonti bibliografiche (ISBN, titolo accademico, edizione, capitolo, pagina esatta, identificativo PMID/DOI).
3. QA Critic:
   - Evidenziare i rischi di corruzione: tabelle con celle fuse (rowspan/colspan), fraintendimenti di unità di misura mediche (microgrammi vs milligrammi per difetti OCR), frammenti orfani senza contesto terapeutico.
   - Definire la checklist di validazione crittografica SHA-256 e i controlli di integrità prima della chiusura del pacchetto.
4. Technical Writer:
   - Includere lo schema JSON completo del `manifest.json`, il diagramma di flusso della pipeline ETL e le tabelle delle metriche di compressione.
""",
    },
    {
        "titolo_capitolo": "Modulo 1.3: Canale IPC Tauri-FastAPI e Protocollo di Streaming Zero-Copy per i Media Clinici",
        "direttive": """
Redigere la specifica tecnica per il Modulo 1.3: Comunicazione Inter-Processo (IPC) e Gestione Media.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Dettagliare l'accoppiamento tra il core Rust (Tauri), il frontend React/TypeScript e il sidecar logico Python (FastAPI).
   - Architettura Zero-Copy per i file multimediali ad altissima risoluzione (vetrini istologici, foto dermatologiche, radiografie): divieto assoluto di trasporto Base64 e bypass dell'heap Python.
   - Implementazione del Custom Asset Protocol nativo in Rust (`med-asset://`): mappatura della memoria virtuale via chiamate di sistema (`mmap`) direttamente dallo storage su disco alla texture GPU della WebView2.
   - Allocazione dinamica della porta TCP su loopback locale (127.0.0.1) e generazione all'avvio di un token crittografico effimero UUIDv4 passato via stdin, con validazione dell'header `X-Tauri-IPC-Secret` per prevenire attacchi CSRF locali.
2. Medical AI Specialist:
   - Definizione degli standard iconografici: conversione delle immagini in WebP near-lossless con profilo colore sRGB bloccato per preservare le sfumature cromatiche cellulari (basofilia vs eosinofilia).
   - Indicizzazione dei media tramite hash crittografico SHA-256 e legame indissolubile con didascalia clinica e fonte bibliografica.
3. QA Critic:
   - Analisi delle race condition IPC durante l'avvio asincrono dei processi.
   - Prevenzione dei processi zombie su Windows: implementazione del doppio Watchdog (Rust che sorveglia FastAPI con SIGTERM forzato dopo 500ms di grace period; thread Python in background che monitora il PID padre e si auto-termina se Tauri scompare).
4. Technical Writer:
   - Fornire il diagramma di sequenza IPC dell'avvio e del caricamento media, con specifiche formali dei contratti di rete locale.
""",
    },
    {
        "titolo_capitolo": "Modulo 1.4: Struttura SQLite Resiliente (Isolamento Fisico, Blue/Green Swap e WAL Recovery)",
        "direttive": """
Redigere la specifica tecnica per il Modulo 1.4: Architettura di Persistenza Relazionale e Resilienza Database.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Separazione fisica assoluta dei due database locali: `master_knowledge.sqlite` (Knowledge Layer, sola lettura, aggiornato via .medpack con PRAGMA query_only = ON) e `user_state.sqlite` (User Layer, lettura e scrittura esclusiva del client per metriche FSRS, note personali e storico esami).
   - Configurazione PRAGMA di sicurezza e concorrenza: PRAGMA journal_mode = WAL;, PRAGMA synchronous = NORMAL;, PRAGMA busy_timeout = 5000;.
   - Procedura di Hot-Swapping Atomico (Blue/Green Database Switch): transazione ombra nell'istanza Green, verifica vincoli referenziali via PRAGMA foreign_key_check, drenaggio del pool connessioni entro 250ms e commutazione atomica del puntatore driver.
2. Medical AI Specialist:
   - Schema DDL SQL delle tabelle fondamentali: `diseases` (ICD-10, Orphanet), `symptoms` (codici HPO), `disease_symptoms` (grafo pesato), `drugs` (codici ATC), `drug_interactions` (matrice di severità) e `exam_quizzes`.
   - Vincoli di integrità relazionale: divieto di chiavi orfane e indicizzazione composita B-Tree su `(symptom_id, disease_id, frequency_weight)` per abilitare l'Index-Only Scan a costo computazionale nullo.
3. QA Critic:
   - Gestione delle corruzioni da spegnimento improvviso (Self-Healing Boot): scansione diagnostica con PRAGMA quick_check all'avvio, ripristino automatico del WAL e fallback all'istantanea di backup `.bak` generata a ogni chiusura pulita.
   - Eliminazione dei rischi di lock di scrittura (`SQLITE_BUSY`) grazie al single-writer serializzato per `user_state.sqlite`.
4. Technical Writer:
   - Includere gli script DDL SQL completi e normalizzati e il diagramma ER relazionale.
""",
    },
    {
        "titolo_capitolo": "Modulo 2.1: Pipeline NLP Locale a Latenza Zero (SymSpell, Dizionario Inverso e ONNX SQ8)",
        "direttive": r"""
Redigere la specifica tecnica per il Modulo 2.1: Pipeline di Normalizzazione Linguistica e Comprensione Query.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Budget prestazionale dell'Omnibar: elaborazione della stringa utente in meno di 15 millisecondi e allocazione di memoria heap inferiore a 50 MB.
   - Struttura a 3 stadi seriali concatenati a complessità crescente, interrompibili al primo riscontro positivo.
2. Medical AI Specialist:
   - Stadio 1 (Typo-Tolerance e Correzione): algoritmo SymSpell basato su distanza di Damerau-Levenshtein $\le 2$ con dizionario specializzato di lemmi medici italiani.
   - Stadio 2 (Matching Lessicale Esatto e Sinonimi): tabella di lookup SQLite con dizionario bilingue dei sinonimi clinici UMLS/HPO per mappare istantaneamente il gergo colloquiale (es. 'fame d'aria' -> HP:0002094 Dispnea) in < 1ms.
   - Stadio 3 (Rappresentazione Semantica Vettoriale): micro-modello Sentence Transformers (all-MiniLM-L6-v2) quantizzato in formato ONNX SQ8 (8-bit) per frasi sintomatologiche complesse ('fitte lancinanti al torace durante gli atti respiratori'). Calcolo del Cosine Similarity rispetto ai soli vettori dei sintomi HPO e restituzione delle prime 3 ipotesi disambiguate.
3. QA Critic:
   - Analisi dei fallimenti su acronimi medici italiani ambigui (es. IRA: insufficienza renale acuta vs infezione respiratoria acuta) ed eponimi clinici.
   - Definizione del modulo di Acronym Expansion preventivo e gestione del timeout hardware con fallback su ricerca per prefisso.
4. Technical Writer:
   - Fornire il diagramma di flusso decisionale del tokenizer e le strutture dati dei payload di richiesta/risposta.
""",
    },
    {
        "titolo_capitolo": "Modulo 2.2: Generazione Schede Statiche Markdown vs Ricerca Vettoriale HNSW su ChromaDB",
        "direttive": """
Redigere la specifica tecnica per il Modulo 2.2: Dualismo tra Contenuto Statico Pre-Compilato e Deep Search Vettoriale.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Architettura Static Site Generation (SSG) clinica: le schede complete delle patologie d'esame sono pre-sintetizzate nella MedFactory e risiedono su SQLite nella colonna `clinical_sheet_md`. Rendering React istantaneo via SELECT (<5ms).
   - Ruolo di ChromaDB sul client: confinato esclusivamente alla Deep Semantic Search (ricerca approfondita per concetti puntuali o fisiopatologici non coperti dalle schede statiche standard).
   - Strategia contro il Vector Index Bloat: partizione fisica dell'indice per singolo modulo d'esame e quantizzazione scalare a 8-bit (SQ8), riducendo l'uso di memoria dell'algoritmo HNSW del 75%.
2. Medical AI Specialist:
   - Pipeline di sintesi nella MedFactory: generazione guidata da LLM locale pesante (Qwen 2.5 Coder 7B/14B) con Structured Outputs Pydantic.
   - Divieto di Forced Schema Hallucination: tutti i campi opzionali devono valorizzarsi a null in assenza di evidenza testuale, con iniezione del campo obbligatorio `exact_quote_from_text` per ancorare le asserzioni cliniche alle fonti.
   - Iniezione nel Markdown di tag dichiarativi per i media (es. `<AssetViewer hash='sha256_hash_digest' />`).
3. QA Critic:
   - Rischio di Embedding Drift: disallineamento dello spazio latente se la MedFactory usa un modello e il client ne usa un altro. Imposizione dello stesso identico modello (eseguito in FP16/CUDA sul server e quantizzato INT8/ONNX sul client).
   - Politica di Eviction LRU: scaricamento dalla RAM dell'indice ChromaDB dell'esame precedente non appena l'utente passa a una nuova materia, liberando 200-400 MB di memoria heap.
4. Technical Writer:
   - Strutturare il capitolo con schemi di allocazione di memoria e standard di redazione del Markdown clinico.
""",
    },
    {
        "titolo_capitolo": "Modulo 3.1: Motore Diagnostico a Stadi (Log-Odds, Rule-Out e Guadagno Informativo)",
        "direttive": r"""
Redigere la specifica tecnica per il Modulo 3.1: Motore di Inferenza Diagnostica Multi-Sintomo.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Gestione dell'input $N$-dimensionale: superamento del limite dei 5 sintomi per accettare un numero arbitrario di entità (sintomi manifesti, reperti negativi, segni obiettivi, alterazioni laboratoristiche).
   - Eliminazione dell'esplosione combinatoria delle query SQL: impiego di matrici sparse CSR (Compressed Sparse Row) caricate in RAM (<10 MB) con calcolo del prodotto vettore-matrice via NumPy/SciPy in <1 ms.
2. Medical AI Specialist:
   - Formalizzazione del modello matematico a Somma di Pesi di Evidenza Logaritmica (Log-Odds Scoring) con Laplace/Dirichlet smoothing ($\epsilon = 10^{-4}$) per scongiurare il Floating-Point Underflow e il Zero-Frequency Problem.
   - Coefficiente moltiplicativo per segni patognomonici ($\alpha_{pat} \ge 2.5$).
   - Motore di Rule-Out sui Negativi Pertinenti ($S^-$): detrazione proporzionale e severa sul punteggio per patologie che presentano incompatibilità clinica con i sintomi marcati come assenti.
   - Normalizzazione percentuale tramite funzione Softmax stabilizzata con Log-Sum-Exp (LSE).
   - Algoritmo di Massimizzazione del Guadagno Informativo (Information Gain): estrazione della differenza simmetrica fenotipica tra le prime due diagnosi e generazione automatica della Next-Best-Question ('Per discriminare tra A e B, verificare se è presente il segno X').
3. QA Critic:
   - Superamento dell'assunzione di indipendenza bayesiana (sintomi fisiologicamente correlati): raggruppamento in cluster fisiopatologici per evitare la distorsione ipertrofica dei punteggi.
   - Pre-filtro deterministico per emergenze (Red Flags Interceptor): calcolo automatico dei criteri di shock, qSOFA e NEWS2 prima del calcolo diagnostico, con priorità assoluta di visualizzazione.
4. Technical Writer:
   - Includere la trattazione matematica formale, le equazioni KaTeX, i grafi decisionali e la struttura del JSON di output del `SymptomMatcherBlock`.
""",
    },
    {
        "titolo_capitolo": "Modulo 3.2: Motore di Sicurezza Farmacologica (Tassonomia a 4 Livelli, Carico CYP450 ed $N$-Way Interactions)",
        "direttive": r"""
Redigere la specifica tecnica per il Modulo 3.2: Motore Deterministico di Sicurezza Farmacologica e Tossicologia Clinica.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Architettura ad inferenza simbolica pura su SQLite (zero AI generativa, latenza <5ms, accuratezza 100%).
   - Scansione ottimizzata a cascata: conversione dei principi attivi in codici ATC a 5 livelli, scansione della matrice di co-occorrenza per interazioni a coppie (2-way).
2. Medical AI Specialist:
   - Tassonomia a 4 livelli di gravità clinica: Livello 1 (Controindicazione Assoluta / Letale), Livello 2 (Interazione Maggiore), Livello 3 (Interazione Moderata / Aggiustamento Posologico), Livello 4 (Interazione Minore).
   - Risoluzione delle interazioni di ordine superiore ($N$-Way) tramite Vettore di Carico Funzionale Cumulativo: competizione sugli isoenzimi del citocromo epatico ({CYP3A4, CYP2D6, CYP2C9, CYP2C19, CYP1A2}) sommando algebricamente substrati, inibitori e induttori.
   - Monitoraggio delle tossicità d'organo cumulative: prolungamento intervallo QTc (rischio torsione di punta), carico nefrotossico (sindrome 'Triple Whammy': ACEI/Sartano + Diuretico + FANS) e depressione del SNC.
   - Matrice Farmaco-Patologia (Drug-Disease): controindicazioni su patologie pregresse (beta-bloccanti in asma, FANS in ulcera peptica o insufficienza renale) e aggiustamento del dosaggio in base alla funzione renale stimata (eGFR) e criteri di Beers/STOPP-START.
   - Algoritmo di sostituzione terapeutica intelligente: identificazione automatica di farmaci di seconda linea compatibili con il profilo del paziente.
3. QA Critic:
   - Attacco alle allucinazioni posologiche: sanitizzazione rigida dei dosaggi massimi consentiti da prontuario AIFA/FDA.
   - Segnalazione obbligatoria dei marcatori farmacogenomici critici (es. CYP2C19 per clopidogrel, HLA-B*5701 per abacavir).
4. Technical Writer:
   - Specificare le tabelle DDL della farmacologia, le strutture vettoriali dei citocromi e lo schema JSON del `DrugSafetyBlock`.
""",
    },
    {
        "titolo_capitolo": "Modulo 4.1: Simulatore d'Esame Avanzato (MCQ a 4 Scelte, Hotspot Visivi, NLI Cross-Encoder e Stateful DAG)",
        "direttive": r"""
Redigere la specifica tecnica per il Modulo 4.1: Motore Esecutivo del Simulatore d'Esame Clinico.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Architettura del banco di prova pre-compilato nella MedFactory e distribuito su `module_kb.sqlite`.
   - Latenza di sblocco delle domande istantanea (<2ms) con inclusione nel payload JSON delle spiegazioni pre-calcolate per azzerare le chiamate al backend durante la sessione.
2. Medical AI Specialist:
   - Tipologia 1: Quiz a Scelta Multipla (MCQ a 4 opzioni) con razionale dettagliato per l'opzione corretta e analisi analitica di ciascuno dei 3 distrattori plausibili (diagnosi differenziali affini o controindicazioni specifiche).
   - Tipologia 2: Diagnostica Visiva Cieca e Image Hotspot: verifica spaziale del click utente su coordinate normalizzate relative $[0.0, 1.0]$ all'interno di poligoni patologici annotati su preparati istologici o radiografie.
   - Tipologia 3: Valutazione Automatica Risposte Aperte via NLI Locale: modello Cross-Encoder (mDeBERTa-v3-base-mnli quantizzato INT8 su CPU in <200ms) che confronta le frasi dello studente con una Griglia di Concetti Atomici pesati (Atomic Concept Grid), classificando ogni asserzione in Entailment (acquisito), Neutral (omesso) o Contradiction (errore clinico).
   - Tipologia 4: Casi Clinici Sequenziali a Bivi come Macchine a Stati Finiti a Grafo Orientato con Memoria (Stateful DAG $M=(V, E, S_0, T, x(t))$): parametri vitali dinamici (MAP, HR, RR, SpO2, GCS), orologio biologico e finestre terapeutiche tempo-dipendenti ($\Delta t_{sim}$), budget diagnostico (penalità per 'shotgun approach') e rubrica di valutazione oggettiva in trentesimi su 4 vettori ortogonali.
3. QA Critic:
   - Protezione da Keyword Stuffing nelle risposte aperte: metrica di Precision Penalty per decurtare punti a testi contenenti elenchi disordinati di termini o contraddizioni cliniche.
   - Gestione dell'errore di parallasse/risoluzione negli hotspot grafici grazie all'uso rigoroso di coordinate normalizzate indipendenti dal fattore di scala DPI del monitor.
4. Technical Writer:
   - Fornire gli schemi JSON dei 4 sottotipi di quesito, la formula matematica della rubrica del caso clinico e il diagramma a stati finiti del DAG.
""",
    },
    {
        "titolo_capitolo": "Modulo 4.2: Algoritmo FSRS e Gestione della Memoria a Lungo Termine (Curva dell'Oblio e Target Retention)",
        "direttive": r"""
Redigere la specifica tecnica per il Modulo 4.2: Algoritmo di Schedulazione Mnemonica FSRS.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Isolamento dei dati di progresso nel database `user_state.sqlite` (immuni dagli aggiornamenti dei pacchetti didattici).
   - Tracciamento della cronologia di ritenzione per ciascun concetto atomico o quesito clinico con accesso concorrente WAL.
2. Medical AI Specialist:
   - Fondamenti matematici dell'algoritmo Free Spaced Repetition Scheduler (FSRS) rispetto all'obsoleto SM-2: superamento dei vincoli di facilità rigidi tramite equazioni differenziali del consolidamento mnemonico.
   - Variabili di stato: Stabilità ($S$, intervallo in giorni per cui la ritenzione scende al 90%) e Difficoltà ($D$, scala normalizzata 1-10).
   - Scala di valutazione a 4 gradi (Again, Hard, Good, Easy) e matrice di transizione per il ricalcolo dinamico di $S'$ e $D'$.
   - Gestione degli eventi di oblio (Lapse) con reinserimento prioritario nella coda di ripasso a breve termine.
   - Schedulazione mirata all'obiettivo d'esame universitario: ottimizzazione degli intervalli in funzione della data reale dell'appello (Target Retention $\ge 90\%$ al giorno dell'esame).
3. QA Critic:
   - Analisi del sovraccarico di ripasso (Review Hell): meccanismi di capping giornaliero per prevenire l'abbandono dello studente e redistribuzione intelligente del carico di studio.
4. Technical Writer:
   - Redigere la formulazione matematica completa dell'algoritmo FSRS, le tabelle di transizione di stato e la struttura dei record su SQLite.
""",
    },
    {
        "titolo_capitolo": "Modulo 4.3: Architettura Frontend Server-Driven UI (SDUI), Virtual Windowing e Bounded WebGL",
        "direttive": """
Redigere la specifica tecnica per il Modulo 4.3: Interfaccia Utente Reattiva e Rendering Ottimizzato.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Architettura Server-Driven UI (SDUI): il backend FastAPI restituisce payload JSON tipizzati e validati tramite Pydantic; il frontend React agisce come puro renderer passivo ('pittore stupido').
   - I 4 blocchi grafici essenziali: `ClinicalSheetBlock`, `SymptomMatcherBlock`, `DrugSafetyBlock`, `ExamSimulatorBlock`.
   - Streaming incrementale Server-Sent Events (SSE) / NDJSON per idratazione progressiva: visualizzazione immediata dei dati deterministici SQLite (<10ms) seguita dall'idratazione dei contenuti testuali.
2. Medical AI Specialist:
   - Standardizzazione dei componenti per l'espressività multidisciplinare: rendering dichiarativo per formule chimiche/farmacologiche (SmilesDrawer), visualizzatori molecolari 3D (3Dmol.js da file PDB), formule matematico-fisiche (KaTeX) e grafi metabolici orientati (Cytoscape/Mermaid).
   - Interazione visiva ad alta densità informativa: navigazione orizzontale a tab, gerarchia semantica dei callout (Red Flag, Controindicazione, Tip d'Esame).
3. QA Critic:
   - Virtualizzazione dell'albero dei componenti (Virtual Windowing): smontaggio dal Virtual DOM dei blocchi oltre 2 schermate dal viewport per mantenere costante l'occupazione di memoria RAM (<100MB per la WebView).
   - Prevenzione del crash del browser per esaurimento contesti WebGL (`CONTEXT_LOST_WEBGL`): limite rigido a 1 solo contesto WebGL attivo contemporaneamente; rendering statico predefinito in SVG 2D leggero con attivazione interattiva su click ('Click-to-Interact') e distruzione atomica al cambio di focus.
4. Technical Writer:
   - Definire i contratti JSON/Pydantic per ciascun blocco e l'architettura gerarchica dei componenti React.
""",
    },
]
