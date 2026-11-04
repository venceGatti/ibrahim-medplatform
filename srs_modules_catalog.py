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
from srs_catalog import (
    ALL_SRS_MODULES,
    MASTER_PLAN_MODULES,
    SRSModuleDefinition,
    DATA_SOURCES_REGISTRY,
)

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

    args = parser.parse_args()

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
        print(f"  Gap e Mock coperti ({len(gaps_covered)}): {', '.join(sorted(gaps_covered))}")
        # Simplistic check for mock completeness - in real scenario, cross-reference with scanner
        sys.exit(0)

    # Default behavior if no args passed
    print(f"[SRS-CATALOG] Totale macro-moduli registrati nel catalogo: {len(ALL_SRS_MODULES)}")
    for module_item in ALL_SRS_MODULES:
        print(f"  - [{module_item.module_code}] {module_item.titolo_capitolo} ({len(module_item.applicable_roas)} ROAs)")
