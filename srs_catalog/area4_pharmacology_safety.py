"""
srs_catalog/area4_pharmacology_safety.py

Area 4: Farmacotossicologia, Citocromi, Paradosso dei Profarmaci & Tossicita d'Organo (Moduli 3.5 - 3.10).
Copertura vincolante: ROA-10, ROA-14, ROA-20, ROA-24, ROA-29, ROA-32.
"""

from __future__ import annotations

from typing import List
from srs_catalog.models import SRSModuleDefinition


AREA4_MODULES: List[SRSModuleDefinition] = [
    SRSModuleDefinition(
        module_code="3.5",
        titolo_capitolo="Modulo 3.5: Decomposizione Deterministica delle Fixed-Dose Combinations (FDC) in Codici ATC5 Individuali",
        area_name="Area 4: Farmacotossicologia, Citocromi & Tossicità d'Organo",
        applicable_roas=["ROA-14", "ROA-20"],
        direttive="""
Redigere la specifica tecnica per il Modulo 3.5: Decomposizione delle Associazioni Precotte e Farmaci a Dose Fissa (FDC).
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Integrazione in 'Fase 0' della pipeline farmacologica: qualsiasi codice ATC composito inserito dal clinico/studente viene esploso prima di qualsiasi controllo.
   - Struttura tabellare relazionale in `module_kb.sqlite`: `atc_combinations(composite_atc, component_atc, component_mg) STRICT` (ROA-14, ROA-20).
2. Medical AI Specialist:
   - Algoritmo di esplosione ricorsiva deterministica: mappatura di associazioni farmacologiche diffuse (es. Amoxicillina/Acido Clavulanico -> J01CA04 + J01CR02; Ramipril/Idroclorotiazide -> C09AA05 + C03AA03).
   - Unificazione dell'elenco dei principi attivi individuali per i successivi controlli di interazione binaria, carico CYP450 e tossicità renale/cardiaca.
3. QA Critic:
   - Prevenzione delle omissioni tossiche: dimostrare che l'analisi di una FDC non trascuri interazioni letali portate dal secondo o terzo principio attivo dell'associazione.
   - Tracciamento della provenienza dei componenti per la segnalazione chiara nella Server-Driven UI.
4. Technical Writer:
   - Includere lo schema DDL di `atc_combinations`, la tabella delle combinazioni salvavita critiche e il diagramma di flusso della decompressione posologica.
""",
    ),
    SRSModuleDefinition(
        module_code="3.6",
        titolo_capitolo="Modulo 3.6: Tassonomia delle Interazioni a 4 Livelli e Vettore di Carico Funzionale Cumulativo per Isoenzimi CYP450",
        area_name="Area 4: Farmacotossicologia, Citocromi & Tossicità d'Organo",
        applicable_roas=["ROA-10", "ROA-14", "ROA-20"],
        direttive="""
Redigere la specifica tecnica per il Modulo 3.6: Tassonomia a 4 Livelli e Modello di Carico Enzimatico CYP450.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Esecuzione vettoriale ad alte prestazioni per le combinazioni $N$-Way di farmaci co-somministrati.
   - Tabelle SQLite relazionali STRICT: `substances`, `substance_cyp_profiles`, `substance_interactions` (ROA-20).
2. Medical AI Specialist:
   - Tassonomia delle interazioni su 4 classi di severita: Livello 1 (Controindicazione Assoluta / Blackbox), Livello 2 (Interazione Maggiore / Monitoraggio Stretto), Livello 3 (Interazione Moderata / Aggiustamento Posologico), Livello 4 (Interazione Minore).
   - Vettore di Carico Funzionale Cumulativo sui 5 isoenzimi epatici primari: $\\mathcal{E} = \\{3A4, 2D6, 2C9, 2C19, 1A2\\}$.
   - Calcolo del coefficiente di carico cumulativo per ciascun enzima: $L_{enz} = \\sum w_{inibitori} - \\sum w_{induttori}$, con soglie di allarme per inibizione massiva e tossicita da accumulo su farmaci a basso indice terapeutico (es. Warfarin, Digossina, Ciclosporina).
3. QA Critic:
   - Eliminazione dei falsi negativi dovuti a interazioni a catena a 3 o 4 vie non catturate dai test a coppie (2-Way).
   - Verifica di coerenza posologica tra interazioni farmacocinetiche (CYP450) e farmacodinamiche (sinergismo tossico).
4. Technical Writer:
   - Riportare la matrice matematica dei pesi enzimatici, le strutture dati JSON dei payload e la tabella di classificazione delle severità cliniche.
""",
    ),
    SRSModuleDefinition(
        module_code="3.7",
        titolo_capitolo="Modulo 3.7: Risoluzione del Paradosso dei Profarmaci: Allerta Imperativa Blackbox Livello 1 per Inibizione della Bioattivazione",
        area_name="Area 4: Farmacotossicologia, Citocromi & Tossicità d'Organo",
        applicable_roas=["ROA-10", "ROA-24"],
        direttive="""
Redigere la specifica tecnica per il Modulo 3.7: Risoluzione del Paradosso dei Profarmaci e Rilevamento Fallimento Terapeutico Letale.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Riformulazione completa del motore enzimatico: superamento della logica monodirezionale che associa l'inibizione esclusivamente ad 'accumulo tossico'.
   - Campo booleano obbligatorio nella tabella `substances`: `is_prodrug BOOLEAN NOT NULL DEFAULT 0` (ROA-10).
2. Medical AI Specialist:
   - Definizione del Paradosso dei Profarmaci: per molecole inattive che richiedono bioattivazione epatica da parte di un isoenzima (es. Clopidogrel metabolizzato da CYP2C19; Codeina metabolizzata da CYP2D6; Tamoxifene metabolizzato da CYP2D6):
     * Profarmaco + Inibitore enzimatico (es. Clopidogrel + Omeprazolo) $\\implies$ **ALLERTA IMPERATIVA BLACKBOX LIVELLO 1**: mancata conversione nel metabolita attivo, inefficacia terapeutica letale, trombosi acuta dello stent coronarico o mancata analgesia (ROA-10).
     * Profarmaco + Induttore enzimatico $\\implies$ Allerta Livello 1 per sovradosaggio iperacuto e tossicita precoce.
     * Substrato attivo + Inibitore $\\implies$ Allerta Livello 1/2 per accumulo e sovradosaggio.
3. QA Critic:
   - Audit di sicurezza paranoico: verificare che non esista alcun percorso nel codice in cui la combinazione Clopidogrel + PPI inibitore produca un alert lieve o venga ignorata.
   - Sollevamento di allarmi bloccanti e generazione del razionale clinico salvavita nel payload SDUI.
4. Technical Writer:
   - Documentare la tavola di verita formale dello stato del farmaco (Attivo vs Profarmaco $\\times$ Inibitore vs Induttore) e le linee guida FDA/EMA corrispondenti.
""",
    ),
    SRSModuleDefinition(
        module_code="3.8",
        titolo_capitolo="Modulo 3.8: Valutazione della Tossicità d'Organo: QTc Tisdale Score (Torsione di Punta) e Rilevamento Sindrome Triple Whammy",
        area_name="Area 4: Farmacotossicologia, Citocromi & Tossicità d'Organo",
        applicable_roas=["ROA-14", "ROA-20", "ROA-24"],
        direttive="""
Redigere la specifica tecnica per il Modulo 3.8: Tossicita Cardiaca (Allungamento QTc) e Renale ('Triple Whammy').
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Valutazione in 'Fase 2' della sicurezza farmacologica: motori euristici e predittivi a regole deterministiche su `module_kb.sqlite`.
   - Integrazione con la tabella `substance_organ_risks STRICT` (ROA-20).
2. Medical AI Specialist:
   - Tisdale Risk Score per allungamento del tratto QTc e rischio di Torsione di Punta: calcolo dei fattori di rischio clinici (eta $\\ge 68$, sesso femminile, infarto pregresso, ipokaliemia $\\le 3.5\\text{ mEq/L}$, farmaci allungatori QTc multipli, QTc basale $\\ge 450\\text{ ms}$). Soglie: $\\le 6$ Basso Rischio, $7-10$ Medio Rischio, $\\ge 11$ Alto Rischio.
   - Detector della Sindrome 'Triple Whammy' (Triplice Colpo Renale): rilevamento dell'associazione nefrotossica letale:
     $$\\text{ACE-Inibitore / Sartano (RAAS Block)} + \\text{Diuretico (Tiazidico/Ansa)} + \\text{FANS (Inibitore COX)}$$
     che induce insufficienza renale acuta emodinamica (vasocostrizione afferente + vasodilatazione efferente + ipovolemia).
3. QA Critic:
   - Collaudo con regimi terapeutici polifarmacologici complessi in pazienti geriatrici: garanzia di attivazione immediata dell'allerta 'Triple Whammy'.
   - Sollevamento di allarmi di emergenza nel blocco SDUI `DrugSafetyBlock`.
4. Technical Writer:
   - Riportare la tabella a punti del Tisdale Score, la fisiopatologia renale del Triple Whammy e i contratti Pydantic v2 degli alert di tossicità d'organo.
""",
    ),
    SRSModuleDefinition(
        module_code="3.9",
        titolo_capitolo="Modulo 3.9: Funzione Renale CKD-EPI 2021, Criteri di Beers / STOPP-START e Sostituzione Terapeutica con Rapporto DDD",
        area_name="Area 4: Farmacotossicologia, Citocromi & Tossicità d'Organo",
        applicable_roas=["ROA-14", "ROA-20", "ROA-32"],
        direttive="""
Redigere la specifica tecnica per il Modulo 3.9: Aggiustamento Posologico Renale e Sostituzione Terapeutica Elettronica.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Pipeline di validazione della funzione renale del paziente prima dell'emissione della ricetta virtuale.
   - Modulo di raccomandazione automatica di alternative terapeutiche $\\mathcal{J}(a)$ a parità di classe clinica.
2. Medical AI Specialist:
   - Equazione CKD-EPI 2021 per eGFR basata su creatinina sierica senza correttore di razza:
     $$eGFR = 142 \\times \\min(S_{cr}/\\kappa, 1)^\\alpha \\times \\max(S_{cr}/\\kappa, 1)^{-1.200} \\times 0.9938^{Age} \\times [1.012\\text{ if Female}]$$
   - Filtro di sicurezza geriatrico basato sui criteri di Beers (American Geriatrics Society) e STOPP/START (farmaci inappropriati nell'anziano).
   - Calcolo della dose equivalente nelle sostituzioni terapeutiche basato sul rapporto DDD (Defined Daily Dose, ROA-32):
     $$\\text{Dose}_a = \\text{Dose}_k \\times \\frac{\\text{DDD}_a}{\\text{DDD}_k}$$
     con divieto assoluto di mantenere il dosaggio in mg invariato tra molecole a diversa potenza.
3. QA Critic:
   - Verifica di sicurezza: blocco di molecole nefrotossiche a eGFR $< 30\\text{ mL/min/1.73m}^2$ (es. Metformina per acidosi lattica, FANS, Aminoglicosidi).
   - Validazione dei valori DDD estratti dal database ufficiale OMS/ATC.
4. Technical Writer:
   - Includere la formula analitica CKD-EPI 2021 con tabella dei parametri $\\kappa$ e $\\alpha$, e gli schemi Pydantic per il calcolo posologico personalizzato.
""",
    ),
    SRSModuleDefinition(
        module_code="3.10",
        titolo_capitolo="Modulo 3.10: Matrice CPIC Activity Score per Alleli Stellati Farmacogenomici (PM, IM, NM, UM)",
        area_name="Area 4: Farmacotossicologia, Citocromi & Tossicità d'Organo",
        applicable_roas=["ROA-20", "ROA-29"],
        direttive="""
Redigere la specifica tecnica per il Modulo 3.10: Guida Farmacogenomica e Matrice CPIC Activity Score.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Database delle linee guida farmacogenomiche CPIC Livello 1A integrato in `module_kb.sqlite` (`cpic_guidelines STRICT`, ROA-20).
   - Risoluzione genotipo-fenotipo a latenza sub-millisecondo in base agli alleli stellati del profilo paziente.
2. Medical AI Specialist:
   - Calcolo del CPIC Activity Score ($AS = \\sum \\text{score}(\\text{allele}_k)$) per CYP2D6 e CYP2C19 (ROA-29):
     * Alleli nulli privi di funzione (`*3`, `*4`, `*5`, `*6`): score 0.0.
     * Alleli a funzione ridotta (`*9`, `*10`, `*17`, `*41`): score 0.5.
     * Alleli normali funzionali (`*1`, `*2`): score 1.0.
     * Duplicazioni geniche funzionali (`*1xN`, `*2xN`): score 2.0.
   - Categorizzazione fenotipica formale:
     $$AS = 0 \\implies PM,\\quad 0 < AS \\le 1.0 \\implies IM,\\quad 1.25 \\le AS \\le 2.25 \\implies NM,\\quad AS > 2.25 \\implies UM$$
   - Raccomandazioni prescrittive per farmaci indice (es. Codeina in UM -> intossicazione letale da morfina; Clopidogrel in PM -> mancata protezione antiaggregante).
3. QA Critic:
   - Gestione delle varianti alleliche non determinate o rare (VUS) con fallback prudenziale a monitoraggio stretto.
   - Prevenzione di prescrizioni letali in pazienti pediatrici o allattanti con fenotipo CYP2D6 UM.
4. Technical Writer:
   - Riportare la matrice di conversione allelica CPIC, le raccomandazioni terapeutiche vincolanti e gli schemi JSON di risposta dell'API.
""",
    ),
]

