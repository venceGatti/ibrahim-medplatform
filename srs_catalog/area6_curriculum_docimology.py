"""
srs_catalog/area6_curriculum_docimology.py

Definizione dei Macro-Moduli Architetturali per l'Area 6: Curriculum e Docimologia Medica.
"""

from typing import List
from srs_catalog.models import SRSModuleDefinition

AREA6_MODULES: List[SRSModuleDefinition] = [
    SRSModuleDefinition(
        module_code="MOD-06-01",
        titolo_capitolo="6.1. Motore Docimologico e Adattivo (Rasch Model)",
        area_name="Curriculum_Docimology",
        applicable_roas=["ROA-06", "ROA-14", "ROA-32"],
        direttive="Definire il motore di Item Response Theory (IRT) e Modello di Rasch per la calibrazione adattiva della difficoltà dei quesiti. Specificare gli algoritmi di stima di abilità theta.",
        remediates=["GAP-01"],
        data_sources=["medqa_usmle", "medmcqa"],
        target_paths=["medclient/sidecar-python/exam_engine.py"],
        acceptance_tests=["test_irt_calibration", "test_adaptive_routing"]
    ),
    SRSModuleDefinition(
        module_code="MOD-06-02",
        titolo_capitolo="6.2. Generazione Dinamica di Scenari Clinici",
        area_name="Curriculum_Docimology",
        applicable_roas=["ROA-12", "ROA-18"],
        direttive="Progettare l'architettura per la generazione procedurale di casi clinici (vignette). Il sistema deve variare parametri demografici, parametri vitali e reperti di laboratorio mantenendo la coerenza fisiopatologica.",
        remediates=["GAP-02", "MOCK-09"],
        data_sources=["hpo", "orphanet"],
        target_paths=["medfactory/src/pipeline/scenario_generator.py"],
        acceptance_tests=["test_vignette_consistency", "test_parameter_variation"]
    ),
    SRSModuleDefinition(
        module_code="MOD-06-03",
        titolo_capitolo="6.3. Tracciamento Competenze (Core Curriculum)",
        area_name="Curriculum_Docimology",
        applicable_roas=["ROA-07", "ROA-21"],
        direttive="Specificare il sistema di mapping tra le performance docimologiche e gli obiettivi formativi (Core Curriculum). Progettare lo schema dati per il tracciamento longitudinale delle competenze (radar chart data).",
        remediates=["GAP-03"],
        data_sources=["icd10cm", "mesh"],
        target_paths=["medclient/core-rust/competency_tracker.rs", "medclient/frontend-react/src/components/CurriculumBlock.tsx"],
        acceptance_tests=["test_competency_mapping", "test_longitudinal_tracking"]
    ),
    SRSModuleDefinition(
        module_code="MOD-06-04",
        titolo_capitolo="6.4. Analitiche di Apprendimento (Learning Analytics)",
        area_name="Curriculum_Docimology",
        applicable_roas=["ROA-25", "ROA-34"],
        direttive="Definire la pipeline di aggregazione dati per fornire feedback formativo allo studente. Dettagliare le metriche di tempo di risposta, tasso di confidenza e analisi dei distrattori scelti.",
        remediates=["GAP-04"],
        data_sources=[],
        target_paths=["medclient/sidecar-python/analytics_engine.py"],
        acceptance_tests=["test_analytics_aggregation", "test_distractor_analysis"]
    )
]
