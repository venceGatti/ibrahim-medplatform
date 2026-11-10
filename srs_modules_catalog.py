#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
srs_modules_catalog.py

Catalogo dei Moduli Architetturali e Direttive Iper-Tecniche per la Generazione SRS.
Architettura modulare: importa e unifica i 38 macro-moduli distribuiti nel package `srs_catalog`.
Garantisce la piena conformità alle 34 Assunzioni Operative (ROA-01 .. ROA-34) e al vincolo dei micro-file.
"""

from __future__ import annotations

from typing import Dict, List
import argparse
import sys
from pathlib import Path
from srs_catalog import (
    ALL_SRS_MODULES,
    MASTER_PLAN_MODULES,
    SRSModuleDefinition,
    DATA_SOURCES_REGISTRY,
)
from srs_generator.mock_scanner import audit_codebase_gaps

__all__ = [
    "ALL_SRS_MODULES",
    "MASTER_PLAN_MODULES",
    "SRSModuleDefinition",
    "DATA_SOURCES_REGISTRY",
]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SRS Modules Catalog CLI")
    parser.add_argument("--list", action="store_true", help="Elenca tutti i moduli")
    parser.add_argument("--sources", action="store_true", help="Elenca il registro fonti")
    parser.add_argument("--coverage", action="store_true", help="Matrice di copertura")
    parser.add_argument("--curriculum", action="store_true", help="Elenca moduli e obiettivi del curriculum clinico LM-41")

    args = parser.parse_args()

    if args.curriculum:
        print("[SRS-CATALOG] Moduli del Curriculum e Docimologia Medica LM-41 (Area 6):")
        curriculum_modules = [m for m in ALL_SRS_MODULES if m.area_name == "Curriculum_Docimology"]
        for mod in curriculum_modules:
            print(f"  - [{mod.module_code}] {mod.titolo_capitolo}")
            print(f"      Fonti: {', '.join(mod.data_sources) if mod.data_sources else 'N/A'}")
            print(f"      Target: {', '.join(mod.target_paths)}")
            print(f"      Remediates: {', '.join(mod.remediates)}")
        sys.exit(0)

    if args.list:
        print(f"[SRS-CATALOG] Totale macro-moduli registrati nel catalogo: {len(ALL_SRS_MODULES)}")
        for module_item in ALL_SRS_MODULES:
            print(f"  - [{module_item.module_code}] {module_item.titolo_capitolo} ({len(module_item.applicable_roas)} ROAs)")
        sys.exit(0)

    if args.sources:
        print(f"[SRS-CATALOG] Totale fonti certificate nel registro: {len(DATA_SOURCES_REGISTRY)}")
        for key, spec in DATA_SOURCES_REGISTRY.items():
            print(f"  - [{key}] {spec.name} (Licenza: {spec.license})")
        sys.exit(0)

    if args.coverage:
        print(f"[SRS-CATALOG] Generazione matrice di copertura...")
        gaps_covered = set()
        for mod in ALL_SRS_MODULES:
            for rem in mod.remediates:
                gaps_covered.add(rem)

        findings = audit_codebase_gaps(Path("."))
        all_detected_gaps = {f.gap_ref for f in findings if f.gap_ref != "UNKNOWN-GAP"}

        print(f"  Gap e Mock coperti ({len(gaps_covered)}): {', '.join(sorted(gaps_covered))}")
        print(f"  Gap rilevati dal mock_scanner ({len(all_detected_gaps)}): {', '.join(sorted(all_detected_gaps))}")

        uncovered_gaps = all_detected_gaps - gaps_covered
        if uncovered_gaps:
            print(f"[ERRORE] Sono stati rilevati GAP non coperti da alcun modulo: {', '.join(uncovered_gaps)}")
            sys.exit(1)

        print("[OK] Tutti i gap rilevati sono coperti dai moduli.")
        sys.exit(0)

    # Default behavior if no args passed
    print(f"[SRS-CATALOG] Totale macro-moduli registrati nel catalogo: {len(ALL_SRS_MODULES)}")
    for module_item in ALL_SRS_MODULES:
        print(f"  - [{module_item.module_code}] {module_item.titolo_capitolo} ({len(module_item.applicable_roas)} ROAs)")
