#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestratore Multi-Agente CrewAI per la Generazione Iterativa del Documento SRS.
Piattaforma Medica Ibrida: MedFactory (Build-Time) & MedClient (Run-Time).
Modello LLM: Google Gemini via CrewAI / langchain-google-genai.
"""

import os
import sys
import time
from datetime import datetime
from typing import List, Dict

from srs_modules_catalog import MASTER_PLAN_MODULES

# Configurazione encoding UTF-8 per console Windows (prevenzione UnicodeEncodeError)
if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")


def _initialize_llm_orchestrator():
    """Verifica la presenza di GEMINI_API_KEY e inizializza il client LLM di orchestrazione."""
    api_key_env_var: str = "GEMINI_API_KEY"
    gemini_api_key: str = os.environ.get(api_key_env_var, "").strip()

    if not gemini_api_key:
        sys.stderr.write(
            f"[ERRORE CRITICO] La variabile d'ambiente '{api_key_env_var}' non è configurata o è vuota.\n"
            "Imposta la variabile da terminale PowerShell prima di eseguire lo script:\n"
            '  $env:GEMINI_API_KEY = "la_tua_chiave_google_ai_studio"\n'
            "oppure in Bash:\n"
            '  export GEMINI_API_KEY="la_tua_chiave_google_ai_studio"\n'
        )
        sys.exit(1)

    try:
        from google.api_core.exceptions import ResourceExhausted
        from crewai import Agent, Task, Crew, Process, LLM
    except ImportError:
        try:
            from google.api_core.exceptions import ResourceExhausted
            from langchain_google_genai import ChatGoogleGenerativeAI
            from crewai import Agent, Task, Crew, Process
            LLM = None
        except ImportError as import_err:
            sys.stderr.write(
                f"[ERRORE DIPENDENZE] Modulo mancante: {import_err}.\n"
                "Installa le dipendenze richieste eseguendo:\n"
                "  pip install -r requirements.txt\n"
            )
            sys.exit(1)

    default_model = os.environ.get("GEMINI_MODEL", "gemini-flash-latest").strip()
    crewai_model_name = default_model if default_model.startswith("gemini/") else f"gemini/{default_model}"
    langchain_model_name = default_model.replace("gemini/", "")

    if LLM is not None:
        llm_orchestrator = LLM(
            model=crewai_model_name,
            temperature=0.1,
            api_key=gemini_api_key,
        )
    else:
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm_orchestrator = ChatGoogleGenerativeAI(
            model=langchain_model_name,
            temperature=0.1,
            max_retries=5,
            google_api_key=gemini_api_key,
        )
    return llm_orchestrator, Agent, Task, Crew, Process, ResourceExhausted


master_plan: List[Dict[str, str]] = MASTER_PLAN_MODULES


def is_rate_limit_exception(exc: Exception, resource_exhausted_cls: type) -> bool:
    """Rileva se un'eccezione è dovuta a saturazione di quota, rate-limit (HTTP 429) o sovraccarico (HTTP 503)."""
    if isinstance(exc, resource_exhausted_cls):
        return True
    if hasattr(exc, "code") and getattr(exc, "code") in (429, 503):
        return True
    messaggio_diagnostico = str(exc).lower()
    marcatori_rate_limit = (
        "429", "resource_exhausted", "quota", "rate limit",
        "too many requests", "503", "overloaded", "unavailable"
    )
    return any(marcatore in messaggio_diagnostico for marcatore in marcatori_rate_limit)


def esegui_con_backoff(crew_instance, resource_exhausted_cls: type, tentativo: int = 1) -> str:
    """
    Esegue l'istanza CrewAI catturando le eccezioni di Rate Limit (HTTP 429 / ResourceExhausted) o 503.
    In caso di saturazione, applica un backoff forzato di 60 secondi prima di rieseguire ricorsivamente.
    """
    try:
        crew_output = crew_instance.kickoff()
        if hasattr(crew_output, "raw"):
            return str(crew_output.raw)
        return str(crew_output)
    except Exception as exc:
        if is_rate_limit_exception(exc, resource_exhausted_cls):
            tempo_attesa = 60
            timestamp_attuale = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sys.stderr.write(
                f"\n[{timestamp_attuale}] [BACKOFF / RATE LIMIT] Quota o saturazione API Gemini rilevata ({exc}).\n"
                f"Tentativo #{tentativo}: pausa forzata di {tempo_attesa} secondi (Self-Healing in corso).\n"
            )
            time.sleep(tempo_attesa)
            return esegui_con_backoff(crew_instance, resource_exhausted_cls, tentativo=tentativo + 1)
        timestamp_attuale = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sys.stderr.write(
            f"\n[{timestamp_attuale}] [ERRORE IMPREVISTO] Eccezione durante l'esecuzione del modulo: {exc}\n"
        )
        raise exc


def build_agents(llm_orchestrator, agent_cls):
    """Costruisce i quattro agenti specializzati CrewAI."""
    systems_architect = agent_cls(
        role="Lead Systems Architect & Backend Engineer",
        goal=(
            "Progettare l'architettura tecnica desktop, l'infrastruttura IPC a bassa latenza (<50ms), "
            "la gestione SQLite WAL concorrente, il protocollo Zero-Copy memory-mapped per i media "
            "e i limiti di memoria fisica (<300MB RAM) per PC client Intel Core i7 senza GPU."
        ),
        backstory=(
            "Sei un Senior Principal Architect specializzato in ingegneria di sistemi critici, desktop computing "
            "con Tauri/Rust, sidecar FastAPI, basi di dati relazionali ACID e ottimizzazioni memory-mapped I/O. "
            "Rifiuti categoricamente qualsiasi spreco di memoria, lock bloccanti e serializzazioni inefficienti."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm_orchestrator,
    )

    medical_ai_specialist = agent_cls(
        role="Applied Medical AI & NLP Specialist",
        goal=(
            "Garantire la purezza deterministica delle conoscenze cliniche, formalizzare l'uso di ontologie ufficiali "
            "(HPO per fenotipi, ATC per farmacologia), definire la pipeline NLP client-side senza LLM generativi, "
            "progettare la correzione NLI Cross-Encoder per le risposte aperte e l'algoritmo mnemonico FSRS."
        ),
        backstory=(
            "Sei un Ingegnere Informatico Medico ed esperto di NLP computazionale applicato all'educazione clinica. "
            "Conosci a fondo la medicina interna, la farmacologia e le metodologie d'esame universitarie. "
            "Rifiuti categoricamente il RAG generativo client-side e i pesi inventati dagli LLM, imponendo ontologie certificate."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm_orchestrator,
    )

    qa_critic = agent_cls(
        role="Aggressive QA & Edge-Case Auditor",
        goal=(
            "Attaccare e demolire preventivamente ogni soluzione architetturale, identificando scenari di memory bloat, "
            "race-condition, deadlock SQLite, floating-point underflow, conflitti IPC, processi zombie e "
            "violazioni dei requisiti di confidenzialità e conformità normativa."
        ),
        backstory=(
            "Sei un auditor di qualità e sicurezza paranoico e spietato. Il tuo obiettivo primario è scovare il "
            "punto esatto di rottura del software prima che arrivi all'utente finale. Blocchi sul nascere qualsiasi "
            "proposta che rischi di superare i 300MB di RAM allocata sul client o corrompere i dati dello studente."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm_orchestrator,
    )

    technical_writer = agent_cls(
        role="Senior Medical Technical Documentation Engineer",
        goal=(
            "Sintetizzare il dibattito e redigere formalmente i requisiti ingegneristici in un documento Markdown SRS "
            "rigoroso, privo di convenevoli, ricco di specifiche DDL, schemi architetturali testuali, contratti Pydantic, "
            "formule matematiche e matrici decisionali."
        ),
        backstory=(
            "Sei uno scrittore tecnico d'élite con decenni di esperienza nella stesura di specifiche Software Requirements "
            "Specification (SRS standard IEEE/ISO). Produci documentazione tecnica asciutta, densa, iper-strutturata "
            "e direttamente pronta per guidare l'implementazione del software senza margini di interpretazione soggettiva."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm_orchestrator,
    )
    return systems_architect, medical_ai_specialist, qa_critic, technical_writer


def main() -> None:
    llm_orchestrator, Agent, Task, Crew, Process, ResourceExhausted = _initialize_llm_orchestrator()
    systems_architect, medical_ai_specialist, qa_critic, technical_writer = build_agents(llm_orchestrator, Agent)

    nome_file_output: str = "SRS_MedClient_Architettura_Completa.md"
    totale_capitoli: int = len(master_plan)

    print("=" * 80)
    print("PIATTAFORMA MEDICA IBRIDA - GENERATORE SRS MULTI-AGENTE (CREWAI & GEMINI)")
    print(f"Data di avvio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Totale moduli da elaborare: {totale_capitoli}")
    print(f"File di output: {nome_file_output}")
    print("=" * 80)

    if not os.path.exists(nome_file_output):
        with open(nome_file_output, "w", encoding="utf-8") as f_init:
            f_init.write(
                "# Software Requirements Specification (SRS) - Piattaforma Medica Ibrida\n"
                "## Architettura Completa di Sistema: MedFactory (Build-Time) & MedClient (Run-Time)\n"
                f"**Data di Generazione:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n"
                "**Standard:** IEEE/ISO Software Requirements Specification  \n"
                "**Orchestrazione:** CrewAI Multi-Agent Pipeline con Google Gemini 1.5 Pro  \n\n"
                "---\n\n"
            )

    for indice, modulo in enumerate(master_plan, start=1):
        titolo = modulo["titolo_capitolo"]
        direttive = modulo["direttive"]

        print(f"\n[{indice}/{totale_capitoli}] Inizio elaborazione: {titolo}")
        inizio_modulo = time.time()

        task_modulo = Task(
            description=(
                f"Sei incaricato di redigere formalmente la specifica tecnica per: '{titolo}'.\n"
                f"Direttive dettagliate da implementare:\n{direttive}\n\n"
                "Vincoli di Stile e Formato:\n"
                "- Linguaggio: Italiano tecnico formale con nomenclatura medica standard e codici HPO/ATC/ICD-10.\n"
                "- Nessuna introduzione generica, convenevoli, o formule di cortesia.\n"
                "- Solo specifiche ingegneristiche asciutte, strutture dati, equazioni matematiche, tabelle e contratti."
            ),
            expected_output=(
                "Trattazione esaustiva in formato Markdown GitHub-Flavored, con sezioni di livello 2, 3 e 4, "
                "blocchi di codice per schemi DDL/JSON/Pydantic, formule matematiche formali e analisi dei rischi."
            ),
            agent=systems_architect,
        )

        crew_modulo = Crew(
            agents=[systems_architect, medical_ai_specialist, qa_critic, technical_writer],
            tasks=[task_modulo],
            process=Process.sequential,
            verbose=False,
        )

        contenuto_generato: str = esegui_con_backoff(crew_modulo, ResourceExhausted)

        with open(nome_file_output, "a", encoding="utf-8") as f_out:
            f_out.write(f"\n## {titolo}\n\n")
            f_out.write(contenuto_generato)
            f_out.write("\n\n---\n")
            f_out.flush()

        durata = time.time() - inizio_modulo
        print(f"[OK] {titolo} completato e salvato in {durata:.1f} secondi.")

        if indice < totale_capitoli:
            pausa_fisiologica = 10
            print(f"Pausa fisiologica di {pausa_fisiologica}s per la quota API.")
            time.sleep(pausa_fisiologica)

    print("\n" + "=" * 80)
    print("PROCESSO DI GENERAZIONE SRS COMPLETATO CON SUCCESSO!")
    print(f"Documento finale generato in: {os.path.abspath(nome_file_output)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
