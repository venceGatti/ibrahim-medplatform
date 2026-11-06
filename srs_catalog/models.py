"""
srs_catalog/models.py

Definizione delle strutture dati tipizzate per i macro-moduli architetturali dell'SRS.
Rispetta rigorosamente i contratti formali e la separazione dei compiti.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class SRSModuleDefinition:
    """Rappresentazione immutabile e tipizzata di un macro-modulo architetturale SRS."""

    module_code: str
    titolo_capitolo: str
    area_name: str
    applicable_roas: List[str] = field(default_factory=list)
    direttive: str = ""
    remediates: List[str] = field(default_factory=list)
    data_sources: List[str] = field(default_factory=list)
    target_paths: List[str] = field(default_factory=list)
    acceptance_tests: List[str] = field(default_factory=list)
    remediates: List[str] = field(default_factory=list)
    data_sources: List[str] = field(default_factory=list)
    target_paths: List[str] = field(default_factory=list)
    acceptance_tests: List[str] = field(default_factory=list)

    def to_legacy_dict(self) -> Dict[str, str]:
        """Converte la definizione nel formato dizionario compatibile con i runner storici."""
        return {
            "titolo_capitolo": self.titolo_capitolo,
            "direttive": self.direttive.strip(),
            "module_code": self.module_code,
            "area_name": self.area_name,
            "applicable_roas": ", ".join(self.applicable_roas),
        }



@dataclass(frozen=True)
class DataSourceSpec:
    key: str
    name: str
    url: str
    license: str
    format: str
    auth: str
    rate_limit: str
    update_cadence: str
    sha256_policy: str
    target_tables: List[str] = field(default_factory=list)
    offline_strategy: str = ""
    license_risk: bool = False
