"""
srs_catalog/__init__.py

Package di definizione dei Macro-Moduli Architetturali SRS di MedPlatform.
Esporta l'elenco completo dei 26 macro-moduli e la lista di compatibilità retroattiva.
"""

from __future__ import annotations

from typing import Dict, List
from srs_catalog.models import SRSModuleDefinition
from srs_catalog.area1_core_hardware import AREA1_MODULES
from srs_catalog.area2_ingestion_nlp import AREA2_MODULES
from srs_catalog.area3_diagnostic_emergency import AREA3_MODULES
from srs_catalog.area4_pharmacology_safety import AREA4_MODULES
from srs_catalog.area5_simulation_sdui import AREA5_MODULES

ALL_SRS_MODULES: List[SRSModuleDefinition] = (
    AREA1_MODULES +
    AREA2_MODULES +
    AREA3_MODULES +
    AREA4_MODULES +
    AREA5_MODULES
)

MASTER_PLAN_MODULES: List[Dict[str, str]] = [
    module_def.to_legacy_dict() for module_def in ALL_SRS_MODULES
]

__all__ = [
    "SRSModuleDefinition",
    "ALL_SRS_MODULES",
    "MASTER_PLAN_MODULES",
    "AREA1_MODULES",
    "AREA2_MODULES",
    "AREA3_MODULES",
    "AREA4_MODULES",
    "AREA5_MODULES",
]
