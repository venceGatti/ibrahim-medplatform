#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
srs_modules_catalog.py

Catalogo dei Moduli Architetturali e Direttive Iper-Tecniche per la Generazione SRS.
Architettura modulare: importa e unifica i 26 macro-moduli distribuiti nel package `srs_catalog`.
Garantisce la piena conformità alle 34 Assunzioni Operative (ROA-01 .. ROA-34) e al vincolo dei micro-file.
"""

from __future__ import annotations

from typing import Dict, List
from srs_catalog import (
    ALL_SRS_MODULES,
    MASTER_PLAN_MODULES,
    SRSModuleDefinition,
)

__all__ = [
    "ALL_SRS_MODULES",
    "MASTER_PLAN_MODULES",
    "SRSModuleDefinition",
]

if __name__ == "__main__":
    print(f"[SRS-CATALOG] Totale macro-moduli registrati nel catalogo: {len(ALL_SRS_MODULES)}")
    for module_item in ALL_SRS_MODULES:
        print(f"  - [{module_item.module_code}] {module_item.titolo_capitolo} ({len(module_item.applicable_roas)} ROAs)")
