"""
srs_catalog/area2_ingestion_nlp.py

Area 2: Knowledge Ingestion, Ontologie Cliniche & NLP Edge Pipeline (Moduli 2.1 - 2.5).
Copertura vincolante: ROA-03, ROA-04, ROA-06, ROA-11, ROA-13, ROA-18, ROA-19, ROA-20, ROA-22, ROA-24.
"""

from __future__ import annotations

from typing import List
from srs_catalog.models import SRSModuleDefinition


AREA2_MODULES: List[SRSModuleDefinition] = [
    SRSModuleDefinition(
        module_code="2.1",
        titolo_capitolo="Modulo 2.1: Ingestione Documentale DLA (Docling/Marker), Decomposizione Tabelle Cellulari e Chunking Parent-Child",
        area_name="Area 2: Knowledge Ingestion & NLP Edge Pipeline",
        applicable_roas=["ROA-06", "ROA-18", "ROA-19"],
        direttive="""
Redigere la specifica tecnica per il Modulo 2.1: Ingestione Documentale DLA e Decomposizione Gerarchica dei Testi Medici.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Pipeline di estrazione in MedFactory basata su Document Layout Analysis (DLA) avanzata (IBM Docling / Marker) per trattati di medicina interna, farmacologia e patologia.
   - Tracciamento della provenienza bibliografica immutabile: associazione di ogni blocco a ISBN, titolo accademico, edizione, capitolo, pagina e DOI/PMID.
   - Architettura di Chunking Gerarchico Parent-Child: Blocchi Padre da 800-1200 token archiviati in SQLite per il rendering integrale, e Micro-blocchi Figlio da 150-250 token per l'indice vettoriale con iniezione di Breadcrumb Context.
2. Medical AI Specialist:
   - Preservazione topologica delle tabelle cliniche: isolamento cellulare di dosaggi, intervalli terapeutici, controindicazioni senza appiattimento in testo grezzo.
   - Riconoscimento ed estrazione di elenchi diagnostici differenziali e criteri di inclusione/esclusione patologica.
3. QA Critic:
   - Analisi delle anomalie OCR: confusione tra microgrammi (mcg/ug) e milligrammi (mg), celle fuse (rowspan/colspan), e frammenti testuali decontestualizzati.
   - Validazione a doppio checksum BLAKE3 + SHA-256 su tutti i file estratti prima dell'impacchettamento (ROA-06).
4. Technical Writer:
   - Fornire gli schemi JSON/Pydantic per i blocchi gerarchici e il diagramma di flusso della pipeline di parsing DLA.
""",
    ),
    SRSModuleDefinition(
        module_code="2.2",
        titolo_capitolo="Modulo 2.2: Isolamento di PyHPO in MedFactory, Ancestor Closure Transitivo e Calcolo dell'Information Content",
        area_name="Area 2: Knowledge Ingestion & NLP Edge Pipeline",
        applicable_roas=["ROA-04", "ROA-13"],
        direttive="""
Redigere la specifica tecnica per il Modulo 2.2: Elaborazione dell'Ontologia HPO e Ancestor Closure a Build-Time.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Confine funzionale assoluto di `pyhpo` in MedFactory (ROA-04): isolamento offline nel generatore di build. MedClient e totalmente privo della libreria `pyhpo` e non carica DAG ontologici in memoria a runtime.
   - Generazione di tabelle relazionali piatte e matrici sparse pre-calcolate in `module_kb.sqlite` per un accesso $O(1)$ a latenza zero.
2. Medical AI Specialist:
   - Algoritmo di Ancestor Closure Transitivo: per ogni fenotipo HPO presente in una patologia, espansione ricorsiva di tutti i nodi antenati tramite le relazioni `is_a`.
   - Prevenzione dei falsi negativi clinici: consentire il matching positivo se lo studente inserisce un termine sovraordinato o affine.
   - Calcolo dell'Information Content (IC) per ciascun nodo HPO basato sulla frequenza inversa di annotazione nel corpus patologico: $IC(t) = -\\log_2(freq(t))$.
3. QA Critic:
   - Verifica di consistenza: prevenzione di cicli nel DAG ontologico e controllo dell'integrita referenziale tra codici HPO e malattie ICD-10.
   - Benchmark di memoria: dimostrare che l'esclusione di `pyhpo` dal runtime client risparmia oltre 120 MB di heap RAM.
4. Technical Writer:
   - Includere le formule matematiche dell'Information Content, la struttura DDL della tabella `hpo_ancestor_closure` e grafi dimostrativi.
""",
    ),
    SRSModuleDefinition(
        module_code="2.3",
        titolo_capitolo="Modulo 2.3: Pipeline NLP Edge a Latenza Zero: Correzione SymSpell Damerau-Levenshtein <= 2 con Lemmi Clinici Canonici",
        area_name="Area 2: Knowledge Ingestion & NLP Edge Pipeline",
        applicable_roas=["ROA-22", "ROA-24"],
        direttive="""
Redigere la specifica tecnica per il Modulo 2.3: Typo-Tolerance e Normalizzazione Ortotipografica Edge.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Budget di esecuzione su MedClient: elaborazione in meno di 5 millisecondi e consumo RAM heap < 25 MB per il dizionario dei lemmi.
   - Adozione dell'algoritmo SymSpell con distanza di Damerau-Levenshtein $\\le 2$ (cancellazioni, inserimenti, sostituzioni e trasposizioni adiacenti).
   - Pre-filtro selettivo del dizionario sui soli lemmi clinici canonici (ROA-22) per scongiurare il bloat di memoria tipico dei vocabolari linguistici generici.
2. Medical AI Specialist:
   - Gestione degli errori di digitazione comuni degli studenti nei nomi dei farmaci (es. 'paracetamolo' -> 'parcetamolo') e nei termini nosologici (es. 'splenomegalia' -> 'splenomeglaia').
   - Ponderazione della frequenza d'uso dei lemmi medici per massimizzare la precisione del primo suggerimento.
3. QA Critic:
   - Prevenzione di correzioni pericolose: evitare che farmaci con nomi simili ma indicazioni opposte (es. 'idralazina' vs 'idrossizina') vengano convertiti erroneamente.
   - Sollevamento di eccezioni tipizzate `MedClientError(ValueError)` in caso di input non conformi o caratteri di controllo malformati (ROA-24).
4. Technical Writer:
   - Riportare algoritmi in pseudocodice formale, tabelle di test con matrici di confusione e contratti di interfaccia TypeScript/Python.
""",
    ),
    SRSModuleDefinition(
        module_code="2.4",
        titolo_capitolo="Modulo 2.4: Dizionario Lessicale Inverso, Lookup Table Bilingue e Normalizzazione del Gergo Medico Colloquiale",
        area_name="Area 2: Knowledge Ingestion & NLP Edge Pipeline",
        applicable_roas=["ROA-20", "ROA-22"],
        direttive="""
Redigere la specifica tecnica per il Modulo 2.4: Mappatura Semantica del Gergo Medico e Dizionario Inverso Bilingue.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Architettura della lookup table su SQLite STRICT (`colloquial_synonyms STRICT`, `medical_lexicon STRICT`, ROA-20) con indici B-Tree compositi per lookup in < 1 ms.
   - Gestione trasparente di stringhe bilingue (Italiano accademico / Inglese USMLE / Espressioni colloquiali del paziente).
2. Medical AI Specialist:
   - Mappatura semantica tra descrizioni sintomatologiche popolari e codici ontologici HPO (es. 'fame d'aria' -> HP:0002094 Dyspnea; 'occhi gialli' -> HP:0000952 Jaundice; 'cuore in gola' -> HP:0001962 Palpitations).
   - Gestione delle varianti regionali e dei termini gergali riferiti dagli studenti o nelle anamnesi dei casi clinici.
3. QA Critic:
   - Verifica di unicita delle corrispondenze ed eliminazione di ambiguità cliniche pericolose (es. 'dolore al petto' che puo implicare angor, pleurite o reflusso).
   - Audit del working set: dimostrare che la lookup table relazionale non alloca strutture dati dinamiche ridondanti in RAM (ROA-22).
4. Technical Writer:
   - Specificare lo schema DDL completo delle tabelle del dizionario inverso, con esempi reali di mapping e contratti Pydantic v2.
""",
    ),
    SRSModuleDefinition(
        module_code="2.5",
        titolo_capitolo="Modulo 2.5: Ricerca Ibrida Edge Client: SQLite FTS5 Lexical Search e Inferenza Vettoriale ONNX Runtime INT8",
        area_name="Area 2: Knowledge Ingestion & NLP Edge Pipeline",
        applicable_roas=["ROA-03", "ROA-11", "ROA-22"],
        direttive="""
Redigere la specifica tecnica per il Modulo 2.5: Motore di Ricerca Ibrido Edge (Lessicale FTS5 + Semantico ONNX INT8).
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Eliminazione categorica di ChromaDB e di qualsiasi vettore-database esterno sul client (ROA-03): divieto di allocazione di 250MB di demone embedded.
   - Integrazione di SQLite FTS5 per la ricerca lessicale su trigrammi e BM25 (< 5 ms).
   - Inferenza semantica edge tramite ONNX Runtime quantizzato INT8 (modello `all-MiniLM-L6-v2`, < 25 MB footprint su disco, < 48 MB RAM heap).
   - Esecuzione del dot-product vettoriale contro i vettori float memorizzati come BLOB in SQLite tramite array compatti in C/Rust o Polars a latenza < 15 ms.
2. Medical AI Specialist:
   - Rifiuto assoluto di modelli generativi LLM client-side (ROA-11): l'AI edge funge puramente da encoder semantico discriminativo.
   - Fusione dei ranking tramite Reciprocal Rank Fusion (RRF): $RRF(d) = \\frac{1}{k + rank_{FTS5}(d)} + \\frac{1}{k + rank_{ONNX}(d)}$ con $k=60$.
3. QA Critic:
   - Stress test di memoria: verifica rigorosa del ceiling di 300 MB RSS durante query parallele di ricerca complessa (ROA-22).
   - Benchmark comparativi di recupero semantico per query parafrasate (es. 'fitte lancinanti retrosternali sotto sforzo').
4. Technical Writer:
   - Includere la formula RRF, lo schema della tabella FTS5 SQLite, il codice del loader ONNX INT8 e le tabelle di latenza.
""",
    ),
]
