"""
srs_catalog/area5_simulation_sdui.py

Area 5: Didattica Medica, Simulazione d'Esame, SDUI & Resilienza Frontend (Moduli 4.1 - 4.6).
Copertura vincolante: ROA-02, ROA-11, ROA-12, ROA-16, ROA-17, ROA-20, ROA-24, ROA-25, ROA-27, ROA-28, ROA-30, ROA-31, ROA-33, ROA-34.
"""

from __future__ import annotations

from typing import List
from srs_catalog.models import SRSModuleDefinition


AREA5_MODULES: List[SRSModuleDefinition] = [
    SRSModuleDefinition(
        module_code="4.1",
        titolo_capitolo="Modulo 4.1: Simulatore Esami MCQ a 4 Scelte con Razionali Didattici ed Esplicazione Analitica dei Distrattori",
        area_name="Area 5: Didattica, Simulazione, SDUI & Resilienza Frontend",
        applicable_roas=["ROA-20", "ROA-33"],
        direttive="""
Redigere la specifica tecnica per il Modulo 4.1: Simulatore Esami MCQ con Banche Dati Mediche Reali (MedQA/USMLE) e Importazione Personalizzata.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Architettura del motore d'esame in FastAPI sidecar con risposte in tempo reale: `/api/v3/exam/evaluate` (ROA-33).
   - Ingestione massiva da banche dati aperte certificate:
     * Dataset accademico pubblico MedQA (USMLE 4-options, ~12.000 quesiti clinici reali con 4 scelte, casistiche cliniche e razionali dettagliati).
     * Dataset aperti MedMCQA e PubMedQA per le discipline specialistiche (Cardiologia, Pneumologia, Farmacologia, Infettivologia).
   - Modulo di Importazione Personalizzata dello Studente (User Custom Quiz Importer):
     * Parser per flashcard/quiz Anki (.apkg/.tsv) e file JSONL per consentire allo studente di importare le prove d'esame della propria università.
     * Memorizzazione relazionale in `user_state.sqlite` e `module_kb.sqlite` (`exam_items STRICT`, `exam_distractors STRICT`, ROA-20).
2. Medical AI Specialist:
   - Struttura del quesito MCQ a 4 scelte (1 corretta, 3 distrattori plausibili conformi agli standard National Board of Medical Examiners NBME / USMLE).
   - Esplicazione analitica obbligatoria: per ogni opzione, razionale didattico dettagliato che spiega non solo perché l'opzione corretta e esatta, ma perché ciascun distrattore e clinicamente errato o fuorviante.
   - Punteggio standard: $+1.0$ per risposta corretta, $0.0$ per risposta non data, $-0.25$ per penalità di risposta errata (prevenzione guessing casuale).
3. QA Critic:
   - Eliminazione categorica di mock o quiz cablati nel frontend (ROA-33): ogni quesito deve essere validato ed emesso dal backend relazionale.
   - Tracciamento della conformità pedagogica: assenza di trabocchetti grammaticali o indizi involontari nella formulazione del quesito.
4. Technical Writer:
   - Includere lo schema JSON completo del blocco `ExamSimulatorBlock`, il modello DDL SQL normalizzato delle tabelle d'esame e le specifiche del parser Anki/JSONL.
""",
    ),
    SRSModuleDefinition(
        module_code="4.2",
        titolo_capitolo="Modulo 4.2: Diagnostica Visiva Cieca: Hotspot Poligonali Normalizzati [0.0, 1.0]^2, Bounding Box Fast-Reject e Ray-Casting Even-Odd",
        area_name="Area 5: Didattica, Simulazione, SDUI & Resilienza Frontend",
        applicable_roas=["ROA-16", "ROA-28"],
        direttive="""
Redigere la specifica tecnica per il Modulo 4.2: Diagnostica per Immagini Cieca e Hit Detection su Hotspot Poligonali.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Gestione delle coordinate spaziali normalizzate: memorizzazione di vertici poligonali su $[0.0, 1.0]^2$ per renderli indipendenti dalla risoluzione dello schermo e dal fattore di zoom (ROA-16).
   - Conversione client React: acquisizione click con `GetBoundingClientRect(canvas)` e mappatura $(x_{norm}, y_{norm})$.
2. Medical AI Specialist:
   - Requisiti geometrici dei poligoni lesionali (istopatologia, radiologia, dermatologia): almeno $N \\ge 3$ vertici non collineari e area orientata di Gauss/Shoelace non degenere $A \\ge 10^{-6}$ (ROA-28).
   - Test in due fasi:
     1. Filtro $O(1)$ di Axis-Aligned Bounding Box (AABB) Fast-Reject (scarto immediato click esterni).
     2. Algoritmo Even-Odd Ray-Casting (Teorema della Curva di Jordan) con raggio di tolleranza $R_{tol} \\le 0.02$ della diagonale.
   - Mascheramento visivo cieco: la lesione rimane invisibile all'utente fino alla formulazione della risposta, con rivelazione post-click dell'overlay colorato (verde se colpita, rosso se mancata con indicazione della sede corretta).
3. QA Critic:
   - Stress test di click sui bordi (edge vertices) e forme concave complesse (es. margini infiltranti di melanoma o contorni di lesione tubercolare).
   - Garanzia di accuratezza geometrica e assenza di falsi positivi su display ad alta densità (HiDPI / Retina).
4. Technical Writer:
   - Riportare l'algoritmo Ray-Casting completo in pseudocodice TypeScript/Rust, le equazioni di Shoelace e i contratti SDUI degli hotspot.
""",
    ),
    SRSModuleDefinition(
        module_code="4.3",
        titolo_capitolo="Modulo 4.3: Valutatore NLI Cross-Encoder per Risposte Aperte con Penalità di Precisione Phi e Gestione Enunciati Nulli (M=0)",
        area_name="Area 5: Didattica, Simulazione, SDUI & Resilienza Frontend",
        applicable_roas=["ROA-24", "ROA-27"],
        direttive="""
Redigere la specifica tecnica per il Modulo 4.3: Valutatore Semantico NLI Cross-Encoder per Domande Cliniche Aperte.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Inferenza edge con modello Cross-Encoder compatto compilato in ONNX Runtime INT8 sul sidecar Python (< 30 MB RAM).
   - Pipeline di valutazione end-to-end completata in < 40 ms senza invocare API cloud esterne.
2. Medical AI Specialist:
   - Decomposizione della risposta dello studente in $M$ proposizioni atomiche e confronto contro $K$ proposizioni chiave attese della scheda clinica.
   - Punteggio NLI congiunto con fattore di precisione $\\Phi$:
     $$Score_{NLI} = \\left( \\frac{1}{K} \\sum_{j=1}^K \\max_{i} P(Entailment_{i,j}) \\right) \\times \\Phi$$
   - Mitigazione del Keyword Stuffing tramite Precision Factor $\\Phi = \\frac{E_{confermati}}{M}$.
   - Gestione rigorosa del caso limite di testo privo di enunciati clinici validi ($M = 0$, ROA-27): prevenzione divisione per zero con assegnazione deterministica di $Score_{NLI} = 0.0$, $\\Phi = 0.0$ e $\\Psi = 1.0$.
3. QA Critic:
   - Resistenza ad attacchi avversariali: iniezione di parole chiave non strutturate o tentativi di jailbreak accademico.
   - Sollevamento di `MedClientError(ValueError)` in caso di payload con codifica non UTF-8 o stringhe corrotte (ROA-24).
4. Technical Writer:
   - Documentare la formulazione matematica completa della metrica NLI, la matrice di entailment/neutral/contradiction e gli schemi Pydantic del correttore.
""",
    ),
    SRSModuleDefinition(
        module_code="4.4",
        titolo_capitolo="Modulo 4.4: Casi Clinici Sequenziali a Bivi come Stateful DAG con Prevenzione Divisione per Zero e Clamping dei Punteggi",
        area_name="Area 5: Didattica, Simulazione, SDUI & Resilienza Frontend",
        applicable_roas=["ROA-20", "ROA-34"],
        direttive="""
Redigere la specifica tecnica per il Modulo 4.4: Casi Clinici Interattivi a Bivi come Macchine a Stati Finiti a Grafo Orientato (Stateful DAG).
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Formalizzazione del caso clinico come Stateful DAG: $\\mathcal{M} = (V, E, S_0, T, \\mathbf{x}(t))$, dove $V$ sono i nodi decisionali, $E$ gli archi orientati con transizioni condizionate e $\\mathbf{x}(t)$ lo stato fisiopatologico del paziente virtuale.
   - Persistenza dello stato della sessione in `user_state.sqlite` (`exam_sessions STRICT`, ROA-20).
2. Medical AI Specialist:
   - Valutazione multidimensionale della performance clinica:
     * Accuratezza Diagnostica $A_D \\in [0, 1]$.
     * Efficienza Temporale: $E_T = \\exp\\left( - \\max\\left(0, \\frac{t_{eff} - t_{opt}}{t_{crit} - t_{opt}}\\right) \\right)$.
     * Stewardship delle Risorse / Appropriatezza Prescrittiva: $S_R = \\max\\left(0.0, 1.0 - \\frac{C_{eff} - C_{opt}}{B_{max} - C_{opt}}\\right)$.
   - Prevenzione divisione per zero e clamping numerico (ROA-34): precondizione $t_{crit} \\ge t_{opt} + 1.0$ e $B_{max} \\ge C_{opt} + 1.0$. In caso di denominatore degenere, assegnazione deterministica di 1.0 (se effettivo $\\le$ ottimale) o 0.0, eliminando `ZeroDivisionError` e valori `NaN`.
   - Nodi di Cortocircuito Letale (es. somministrazione errata di beta-bloccante in shock cardiogeno scompensato) che terminano la simulazione con fallimento immediato.
3. QA Critic:
   - Validazione di raggiungibilita del grafo: verifica assenza di vicoli ciechi non terminali o cicli infiniti non fisiologici.
   - Test di integrità sullo stato del paziente (PA, FC, pH, lattati) ad ogni transizione di nodo.
4. Technical Writer:
   - Fornire il diagramma a stati finiti (Mermaid/ASCII), lo schema JSON del grafo e le equazioni formali della rubrica di valutazione.
""",
    ),
    SRSModuleDefinition(
        module_code="4.5",
        titolo_capitolo="Modulo 4.5: Algoritmo Mnemonico FSRS-4.5 con Jitter Deterministico SHA256, Target Retention e Timestamp Monotoni UTC",
        area_name="Area 5: Didattica, Simulazione, SDUI & Resilienza Frontend",
        applicable_roas=["ROA-17", "ROA-20", "ROA-31"],
        direttive="""
Redigere la specifica tecnica per il Modulo 4.5: Ripetizione Spaziata Ottimizzata (FSRS-4.5) e Gestione della Memoria a Lungo Termine.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Standardizzazione temporale assoluta in `user_state.sqlite` (ROA-20, ROA-31): tutti i timestamp (`due_timestamp`, `last_review_timestamp`) sono interi a 64-bit rappresentanti i secondi trascorsi dall'Unix Epoch UTC.
   - Calcolo scadenza con aritmetica intera: $due\\_timestamp = last\\_review\\_timestamp + \\lfloor scheduled\\_days \\times 86400 \\rfloor$.
2. Medical AI Specialist:
   - Algoritmo Free Spaced Repetition Scheduler (FSRS-4.5): modellazione bidimensionale dello stato mnemonico tramite Stabilita $S$ (giorni per cui la ritenzione decade al 90%) e Difficolta $D \\in [1, 10]$.
   - Curva dell'oblio: $R(t) = (1 + \\text{FACTOR} \\times t / S)^{\\text{DECAY}}$ con Target Retention parametrabile ($R_{target} = 0.90$).
   - Jittering deterministico con funzione hash crittografica (ROA-17): per evitare picchi di ripasso concentrati ('Review Hell') senza ricorrere a numeri casuali non riproducibili:
     $$Jitter = \\text{SHA256}(concept\\_uid + \\text{str}(reps)) \\pmod{1000}$$
   - Algoritmo di targeting con vincolo rigido della data dell'esame universitario (Exam Date Countdown).
3. QA Critic:
   - Dimostrazione di riproducibilita al 100% dei piani di studio nei test di regressione (determinismo del seed crittografico).
   - Verifica di monotonicita della stabilità a fronte di voti di ripasso positivi (`Good`, `Easy`).
4. Technical Writer:
   - Includere le equazioni complete di aggiornamento di $S$ e $D$, lo schema DDL di `fsrs_cards` e `review_logs`, e il diagramma della curva di ritenzione.
""",
    ),
    SRSModuleDefinition(
        module_code="4.6",
        titolo_capitolo="Modulo 4.6: Architettura React 19 SDUI: Ritenzione DOM a 60 FPS, WebGL Singleton Broker con Fallback SVG e Parità con FastAPI",
        area_name="Area 5: Didattica, Simulazione, SDUI & Resilienza Frontend",
        applicable_roas=["ROA-02", "ROA-11", "ROA-12", "ROA-25", "ROA-30", "ROA-33"],
        direttive="""
Redigere la specifica tecnica per il Modulo 4.6: Frontend Server-Driven UI (SDUI), Prestazioni e Resilienza Grafica.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Parita assoluta dei contratti tra FastAPI e React (ROA-02, ROA-33): registrazione nel registry dei 4 blocchi tipizzati (`ClinicalSheetBlock`, `SymptomMatcherBlock`, `DrugSafetyBlock`, `ExamSimulatorBlock`) con alias backward-compatible.
   - Eliminazione categorica di mock cablati in `MedClientAppShell.tsx`: consumo esclusivo di payload emessi dal sidecar (ROA-33).
   - Zero LLM generativo nel frontend: rendering di payload deterministici strutturati (ROA-11).
   - Sezione Pannello Impostazioni Sorgenti e Connettori (`SettingsSourcesView`): interfaccia utente per la gestione delle chiavi API personali (NCBI, FDA), link a repository GitHub/Anki esterni, e monitoraggio dello stato di sincronizzazione del database locale.
2. Medical AI Specialist:
   - Ritenzione integrale del DOM a 60 FPS e latenza 0 ms al cambio scheda (ROA-30): le schermate rimangono montate stabilmente nel DOM e commutate via classi CSS (`block opacity-100` vs `hidden opacity-0 pointer-events-none`).
   - Applicazione selettiva del Virtual Windowing (TanStack Virtual) esclusivamente alle liste estese di paragrafi all'interno delle monografie (`ClinicalSheetBlock` con oltre 20 paragrafi), senza impattare lo stato globale.
   - Pattern Singleton WebGL Broker per la visualizzazione di molecole 3D (ROA-12): prevenzione dell'errore `webglcontextlost` in WebView2, con rendering 2D vettoriale SVG come fallback primario a consumo 0 MB VRAM e isolamento offline (ROA-25).
3. QA Critic:
   - Accessibilità e contrasto clinico: conformità WAI-ARIA 1.2 su tutti i controlli interattivi e scala cromatica ad alto contrasto per alert medici (Rosso Red-600, Blackbox Amber-500, Perla Clinica Sky-600).
   - Benchmark di fluidità a 60 FPS durante la transizione rapida tra schede diagnostiche.
4. Technical Writer:
   - Fornire l'albero dei componenti React, la specifica dell'interfaccia TypeScript `SidecarIpcClient`, il diagramma di stato del WebGL Broker e le classi CSS di ritenzione del DOM.
""",
    ),
]

