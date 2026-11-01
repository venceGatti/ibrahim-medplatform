"""
srs_catalog/area3_diagnostic_emergency.py

Area 3: Motori Diagnostici, Emergenze Cliniche & Teoria dell'Informazione (Moduli 3.1 - 3.4).
Copertura vincolante: ROA-04, ROA-13, ROA-15, ROA-21, ROA-24, ROA-26, ROA-33.
"""

from __future__ import annotations

from typing import List
from srs_catalog.models import SRSModuleDefinition


AREA3_MODULES: List[SRSModuleDefinition] = [
    SRSModuleDefinition(
        module_code="3.1",
        titolo_capitolo="Modulo 3.1: Pre-filtro Deterministico Emergenze Cliniche: NEWS2 Scala 2 Condizionata a O2, Shock Index e qSOFA",
        area_name="Area 3: Motori Diagnostici & Emergenze Cliniche",
        applicable_roas=["ROA-21", "ROA-24"],
        direttive="""
Redigere la specifica tecnica per il Modulo 3.1: Pre-Filtro Deterministico dei Segnali di Allarme Vitale e Red Flags.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Posizionamento in 'Fase 0' della pipeline clinica: esecuzione obbligatoria e prioritaria prima di qualsiasi calcolo probabilistico o differenziale.
   - Circuit Breaker di emergenza: se un paziente presenta parametri vitali critici, il sistema blocca l'ordinaria consultazione e attiva l'Allerta Rossa immediata.
2. Medical AI Specialist:
   - Formula esatta NEWS2 Scala 2 per insufficienza respiratoria ipercapnica / BPCO (ROA-21): penalita per iperossia ($SpO_2 \\ge 93\\% \\implies 1\\text{-}3\\text{ pt}$) APPLICATA ESCLUSIVAMENTE se `supplemental_o2 == True`. In aria ambiente (`supplemental_o2 == False`), qualsiasi $SpO_2 \\ge 93\\%$ assegna esattamente 0 punti.
   - Valutazione del flag `has_single_param_three` sui punteggi individuali dei parametri (FR, FC, PA, Temperatura, Coscienza AVPU) e non sul cumulativo totale.
   - Calcolo dello Shock Index con arrotondamento esatto a 3 decimali: $SI = \\text{round}(HR / SBP, 3)$ con soglia di emergenza $SI \\ge 1.0 \\lor SBP \\le 90\\text{ mmHg}$.
   - Criteri qSOFA per sepsi (GCS < 15, FR $\\ge 22$, PAS $\\le 100\\text{ mmHg}$).
3. QA Critic:
   - Analisi di sicurezza clinica: prevenire falsi allarmi o mancate segnalazioni di arresto imminente.
   - Sollevamento di eccezioni tipizzate `MedClientError(ValueError)` in caso di valori vitali biologicamente incompatibili con la vita o fuori scala (ROA-24).
4. Technical Writer:
   - Riportare la funzione a tratti completa di NEWS2 Scala 2 in sintassi KaTeX formale, la tabella di scoring e i contratti Pydantic v2 dei parametri vitali.
""",
    ),
    SRSModuleDefinition(
        module_code="3.2",
        titolo_capitolo="Modulo 3.2: Motore Diagnostico Probabilistico a Matrici Sparse CSR Log-Odds con Laplace Smoothing",
        area_name="Area 3: Motori Diagnostici & Emergenze Cliniche",
        applicable_roas=["ROA-04", "ROA-13", "ROA-15"],
        direttive="""
Redigere la specifica tecnica per il Modulo 3.2: Motore Diagnostico Probabilistico a Matrici Sparse CSR.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Rappresentazione del grafo fenotipo-malattia tramite Compressed Sparse Row (CSR) pre-compilata da MedFactory e memorizzata in `module_kb.sqlite` (ROA-04, ROA-13).
   - Esecuzione di moltiplicazioni matrice-vettore a latenza sub-millisecondo (< 1 ms) in memoria contigua priva di lock del runtime.
2. Medical AI Specialist:
   - Formulazione probabilistica bayesiana nello spazio dei Log-Odds: calcolo delle probabilita a posteriori combinando prevalenza a priori e frequenze sintomatiche HPO.
   - Applicazione del Laplace Smoothing con costante $\\epsilon = 10^{-4}$ per prevenire divisioni per zero e probabilita nulle su sintomi rari.
   - Integrazione dell'Ancestor Closure (ROA-04): propagazione dei pesi fenotipici lungo la gerarchia dell'ontologia.
3. QA Critic:
   - Stabilità numerica: prevenzione di underflow/overflow IEEE 754 nel calcolo della normalizzazione esponenziale (Softmax Log-Sum-Exp).
   - Verifica di coerenza nosologica: confronto delle probabilita differenziali su scenari clinici benchmark noti.
4. Technical Writer:
   - Dettagliare le equazioni dei Log-Odds, la struttura dei buffer CSR (indptr, indices, data) e i contratti API del calcolatore diagnostico.
""",
    ),
    SRSModuleDefinition(
        module_code="3.3",
        titolo_capitolo="Modulo 3.3: Motore di Rule-Out sui Negativi Pertinenti con Penalita Finita Vincolata (W- = -12.0) e Prevenzione Divergenze IEEE 754",
        area_name="Area 3: Motori Diagnostici & Emergenze Cliniche",
        applicable_roas=["ROA-15", "ROA-24"],
        direttive="""
Redigere la specifica tecnica per il Modulo 3.3: Motore di Rule-Out Deterministico per Sintomi Negativi Pertinenti.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Gestione differenziata tra sintomi positivi osservati ($S^+$) e sintomi negativi confutati ($S^-$) durante l'anamnesi medica.
   - Prevenzione del NaN: divieto assoluto di assegnare pesi infiniti negativi (`float('-inf')`) che corrompono il calcolo della Softmax Log-Sum-Exp (ROA-15).
2. Medical AI Specialist:
   - Applicazione della penalità finita e limitata: per sintomi la cui assenza confuta la malattia con sensibilita validata $> 99\\%$, assegnazione di un peso vincolato $W_{ji}^- = -\\tau_{\\max} = -12.0$ (odds ratio $\\approx 6.14 \\times 10^{-6}$, ROA-15).
   - Esclusione trasparente delle patologie confutate dalla Top-K del differenziale attivo, registrando l'evidenza in `rule_out_penalties`.
   - Esempi clinici vincolanti: assenza di dolore toracico nella dissezione aortica acuta tipo A, assenza di cefalea improvvisa nell'emorragia subaracnoidea.
3. QA Critic:
   - Fuzz testing matematico con sequenze arbitrarie di negativi pertinenti e verifica dell'assenza totale di valori `NaN` o crash a virgola mobile.
   - Sollevamento di `MedClientError(ValueError)` in caso di incoerenza tra riscontri clinici contrapposti (ROA-24).
4. Technical Writer:
   - Includere la dimostrazione formale della stabilità della Softmax vincolata a $W^- = -12.0$ e i contratti Pydantic del payload differenziale.
""",
    ),
    SRSModuleDefinition(
        module_code="3.4",
        titolo_capitolo="Modulo 3.4: Algoritmo Next-Best-Question (NBQ) a Massimizzazione del Guadagno Informativo ed Entropia di Shannon con Limiti Asintotici",
        area_name="Area 3: Motori Diagnostici & Emergenze Cliniche",
        applicable_roas=["ROA-26", "ROA-33"],
        direttive="""
Redigere la specifica tecnica per il Modulo 3.4: Algoritmo Next-Best-Question (NBQ) e Ottimizzazione della Raccolta Anamnestica.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Budget prestazionale: calcolo della domanda successiva a piu alto potere discriminante in meno di 10 millisecondi.
   - Eliminazione categorica di ritorni costanti o mock: il sidecar invoca sempre il motore analitico `ActiveDiscriminator` (ROA-33).
2. Medical AI Specialist:
   - Formulazione dell'Entropia di Shannon sul vettore delle probabilità differenziali: $H(D) = -\\sum_{k} p_k \\log_2 p_k$.
   - Calcolo del Guadagno Informativo atteso per ciascun sintomo non ancora indagato: $IG(S_i) = H(D) - \\mathbb{E}[H(D \\mid S_i)]$.
   - Limite asintotico di stabilità numerica (ROA-26): per $p \\le 10^{-12}$ oppure $p \\ge 1.0 - 10^{-12}$, il termine $p \\log_2 p$ restituisce esattamente $0.0$, eliminando la generazione di `-inf` e la propagazione di `0.0 * (-inf) = NaN`.
3. QA Critic:
   - Analisi di efficacia didattica: garantire che la domanda consigliata guidi lo studente verso la discriminazione diagnostica ottimale senza porre domande ridondanti o banali.
   - Verifica di monotonicita della riduzione di entropia al progredire dell'indagine clinica.
4. Technical Writer:
   - Fornire la derivazione matematica del Guadagno Informativo, il grafo decisionale ad albero e le strutture dati TypeScript/Python del suggeritore.
""",
    ),
]
