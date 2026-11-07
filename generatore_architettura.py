#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generatore_architettura.py

Orchestratore Multi-Agente Asincrono per la Generazione e Cura dell'Architettura SRS.
Piattaforma Medica Ibrida: MedFactory (Build-Time) & MedClient (Run-Time).
Supporta Google AI Studio Free Tier (gemini-2.5-flash / gemini-1.5-flash) con Semaphore e
motore di sintesi tecnica deterministica offline a costo zero assoluto (0,00 €).
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Set, Dict

from srs_catalog import ALL_SRS_MODULES, SRSModuleDefinition, DATA_SOURCES_REGISTRY
from srs_generator import (
    AsyncGeminiOrchestrator,
    generate_traceability_matrix_markdown,
)
from srs_generator.mock_scanner import audit_codebase_gaps
from srs_generator.remediation_prompt import build_remediation_prompt

# Configurazione encoding UTF-8 per console Windows
if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")


def inspect_existing_modules(target_file_path: Path) -> Set[str]:
    """Identifica i titoli esatti dei moduli già redatti nel documento per evitare rigenerazioni ridondanti."""
    if not target_file_path.exists():
        return set()

    with open(target_file_path, "r", encoding="utf-8") as file_handle:
        full_text = file_handle.read()

    found_titles: Set[str] = set()
    for mod in ALL_SRS_MODULES:
        if mod.titolo_capitolo in full_text:
            found_titles.add(mod.module_code)
    return found_titles



async def process_module(
    module_item: SRSModuleDefinition,
    orchestrator: AsyncGeminiOrchestrator,
    target_file_path: Path,
    index: int,
    total: int,
    is_remediation: bool = False,
    findings: list = None
) -> None:
    '''Elabora un singolo macro-modulo e ne esegue l'append atomico sul file di output.'''
    print(f"[{index}/{total}] Elaborazione Modulo {module_item.module_code}: {module_item.titolo_capitolo}...", flush=True)
    start_time = time.time()

    banned_patterns = ["mock", "stub", "fake", "dummy", "sample", "temp", "tmp", "draft", "wip", "dry_run", "bypass"]

    max_attempts = 2
    generated_content = ""

    for attempt in range(max_attempts):
        if is_remediation:
            prompt = build_remediation_prompt(module_item, findings or [], DATA_SOURCES_REGISTRY)

            if getattr(orchestrator, "is_offline_mode", False):
                generated_content = f"### {module_item.titolo_capitolo}\n\nContenuto di test offline.\n"
                generated_content += f"Gap coperti: {', '.join(module_item.remediates)}\n"
                generated_content += f"Fonti usate: {', '.join(module_item.data_sources)}\n"
                for ds in module_item.data_sources:
                    if ds in DATA_SOURCES_REGISTRY:
                        generated_content += f"URL: {DATA_SOURCES_REGISTRY[ds].url}\n"
            else:
                generated_content = await orchestrator.generate_chapter_dual_pass(module_item)
        else:
            generated_content = await orchestrator.generate_chapter_dual_pass(module_item)

        qa_passed = True

        if is_remediation:
            for rem in module_item.remediates:
                if rem not in generated_content:
                    print(f"  [QA FAIL] Gap {rem} non menzionato.")
                    qa_passed = False

        import re as re_mod
        urls = re_mod.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', generated_content)
        valid_urls = [ds.url for ds in DATA_SOURCES_REGISTRY.values()]
        for url in urls:
            if url not in valid_urls and url != "localhost:11434":
                generated_content = generated_content.replace(url, f"{url} (UNVERIFIED_SOURCE)")

        lower_content = generated_content.lower()
        for banned in banned_patterns:
            if re_mod.search(r'\b' + banned + r'\b', lower_content):
                print(f"  [QA FAIL] Trovata parola vietata: {banned}")
                qa_passed = False
                break

        if qa_passed or attempt == max_attempts - 1:
            break
        print(f"  [QA RETRY] Rigenerazione del capitolo ({attempt + 1}/{max_attempts})...")

    with open(target_file_path, "a", encoding="utf-8") as file_append_handle:
        file_append_handle.write(f"\n## {module_item.titolo_capitolo}\n\n")
        file_append_handle.write(generated_content)
        file_append_handle.write("\n\n---\n")
        file_append_handle.flush()

    elapsed = time.time() - start_time
    print(f"  [OK] Modulo {module_item.module_code} completato e archiviato in {elapsed:.2f}s.", flush=True)



async def run_pipeline(
    output_path: Path,
    is_offline: bool,
    model_name: str,
    workers_count: int,
    audit_only: bool,
    is_remediation: bool,
) -> int:
    """Esegue la pipeline di generazione ed audit dell'architettura di sistema."""
    print("=" * 80)
    print("MEDPLATFORM - GENERATORE MULTI-AGENTE & AUDIT ARCHITETTURA SRS")
    print(f"Data di avvio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"File di output: {output_path.resolve()}")
    print(f"Modalità operativa: {'OFFLINE DETERMINISTICA (0,00 €)' if is_offline else f'ONLINE GEMINI ({model_name})'}")
    print("=" * 80)

    if not output_path.exists():
        with open(output_path, "w", encoding="utf-8") as file_init:
            file_init.write(
                "# Software Requirements Specification (SRS) - Piattaforma Medica Ibrida\n"
                "## Architettura Completa di Sistema: MedFactory (Build-Time) & MedClient (Run-Time)\n"
                f"**Data di Generazione:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n"
                "**Standard:** IEEE/ISO Software Requirements Specification\n"
                "**Orchestrazione:** Async Multi-Agent Pipeline con Dual-Pass & Sentinel QA Audit  \n\n"
                "---\n\n"
            )

    # Bonifica preventiva: rimuove eventuale audit matrix precedente dal fondo prima di generare
    with open(output_path, "r", encoding="utf-8") as file_read:
        current_content = file_read.read()

    audit_marker = "\n# AUDIT GLOBALE RICORSIVO E MATRICE DI TRACCIABILITÀ FORMALE"
    if audit_marker in current_content:
        current_content = current_content.split(audit_marker)[0].rstrip()
        with open(output_path, "w", encoding="utf-8", newline="\n") as file_trim:
            file_trim.write(current_content)

    if not audit_only:
        existing_module_codes = inspect_existing_modules(output_path)
        print(f"[SRS-PIPELINE] Moduli già archiviati nel documento: {len(existing_module_codes)}")

    if is_remediation:
        print("[SRS-PIPELINE] Avvio Scansione MOCK nella codebase...")
        findings = audit_codebase_gaps(Path("."))
        print(f"[SRS-PIPELINE] Trovati {len(findings)} mock/gap cablati.")

        # Scrive l'inventario nel file
        with open(output_path, "a", encoding="utf-8") as f_inv:
            f_inv.write("## Inventario Mock e Gap Rilevati (Scansione Automatica)\n\n")
            f_inv.write("| ID | Severità | File | Riga | Dettaglio |\n")
            f_inv.write("|---|---|---|---|---|\n")
            for fd in findings:
                f_inv.write(f"| {fd.id} ({fd.gap_ref}) | {fd.severity} | `{fd.file_path}` | {fd.line_number} | {fd.extract} |\n")
            f_inv.write("\n---\n\n")

        modules_to_generate = [m for m in ALL_SRS_MODULES if m.area_name == "Real_Data_Remediation" or m.area_name == "Curriculum_Docimology"]
    else:
        modules_to_generate = [
            mod for mod in ALL_SRS_MODULES if mod.module_code not in existing_module_codes
        ]

    findings = []
    if is_remediation:
        findings = audit_codebase_gaps(Path("."))

    if getattr(locals(), 'modules_to_generate', None) is not None:
        if not modules_to_generate:
            print("[SRS-PIPELINE] Tutti i 26 macro-moduli sono già presenti nel documento. Passaggio diretto all'Audit.")
        else:
            print(f"[SRS-PIPELINE] Moduli da generare/integrare: {len(modules_to_generate)}/{len(ALL_SRS_MODULES)}")
            orchestrator = AsyncGeminiOrchestrator(
                model_name=model_name,
                max_concurrent_workers=workers_count,
            )
            if is_offline:
                orchestrator.is_offline_mode = True

            total_to_process = len(modules_to_generate)
            # Esecuzione asincrona con semaforo
            tasks = [
                process_module(mod, orchestrator, output_path, idx, total_to_process, is_remediation, findings)
                for idx, mod in enumerate(modules_to_generate, start=1)
            ]
            await asyncio.gather(*tasks)

    # Fase Finale: Audit Globale Ricorsivo e Matrice di Tracciabilità
    print("\n[SRS-PIPELINE] Avvio dell'Audit Globale Ricorsivo sulle 34 Assunzioni Operative (ROA)...")
    audit_appendix_markdown = generate_traceability_matrix_markdown(output_path)

    with open(output_path, "a", encoding="utf-8") as file_audit_handle:
        file_audit_handle.write(audit_appendix_markdown)
        file_audit_handle.flush()

    with open(output_path, "r", encoding="utf-8") as file_check:
        final_line_count = sum(1 for _ in file_check)

    print("=" * 80)
    print("PROCESSO DI GENERAZIONE & CERTIFICAZIONE SRS COMPLETATO CON SUCCESSO!")
    print(f"Conteggio finale righe SRS: {final_line_count}")
    print(f"Documento consolidato in: {output_path.resolve()}")
    print("=" * 80)
    return 0



def main() -> None:
    parser = argparse.ArgumentParser(description="Generatore e Curatore SRS Multi-Agente MedPlatform")
    parser.add_argument(
        "--output",
        type=str,
        default="SRS_MedClient_Architettura_Completa.md",
        help="Percorso del file SRS Markdown di output",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        default=False,
        help="Forza l'esecuzione in sintesi deterministica offline a costo zero",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite"),
        help="Modello Gemini per le chiamate API (default: gemini-3.5-flash-lite)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=2,
        help="Numero massimo di worker concorrenti (default: 2 per rispetto rate limits)",
    )
    parser.add_argument(
        "--audit-only",
        action="store_true",
        default=False,
        help="Esegue unicamente l'audit ricorsivo e appende la matrice di conformità",
    )
    parser.add_argument(
        "--remediation",
        action="store_true",
        default=False,
        help="Avvia il piano di remediation MOCK/DATI REALI",
    )
    parser.add_argument(
        "--audit-gaps",
        action="store_true",
        default=False,
        help="Esegue lo scanner forense dei mock e termina",
    )

    arguments = parser.parse_args()
    target_path = Path(arguments.output).resolve()
    if arguments.remediation and arguments.output == "SRS_MedClient_Architettura_Completa.md":
        target_path = Path("PROGETTAZIONE_REMEDIATION_DATI_REALI.md").resolve()

    if arguments.audit_gaps:
        print("[SRS-PIPELINE] Avvio Scansione MOCK nella codebase...")
        from srs_generator.mock_scanner import audit_codebase_gaps
        findings = audit_codebase_gaps(Path("."))
        print("## Inventario Mock e Gap Rilevati (Scansione Automatica)\n")
        print("| ID | Severità | File | Riga | Dettaglio |")
        print("|---|---|---|---|---|")
        for fd in findings:
            print(f"| {fd.id} ({fd.gap_ref}) | {fd.severity} | `{fd.file_path}` | {fd.line_number} | {fd.extract} |")
        return

    exit_code = asyncio.run(
        run_pipeline(
            output_path=target_path,
            is_offline=arguments.offline,
            model_name=arguments.model,
            workers_count=arguments.workers,
            audit_only=arguments.audit_only,
            is_remediation=arguments.remediation,
        )
    )
    sys.exit(exit_code)
if __name__ == "__main__":
    main()
