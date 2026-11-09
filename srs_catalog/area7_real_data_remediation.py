"""
srs_catalog/area7_real_data_remediation.py

Definizione dei Macro-Moduli Architetturali per l'Area 7: Remediation Dati Reali.
"""

from typing import List
from srs_catalog.models import SRSModuleDefinition

AREA7_MODULES: List[SRSModuleDefinition] = [
    SRSModuleDefinition(
        module_code="MOD-07-01",
        titolo_capitolo="7.1. Framework di Ingestion e Resilienza",
        area_name="Real_Data_Remediation",
        applicable_roas=["ROA-01", "ROA-08"],
        direttive="Progettare il framework IDatasetConnector con cache basata su SHA-256, Dead Letter Queue (DLQ), retry con exponential backoff e circuit breaker pattern.",
        remediates=["MOCK-04", "GAP-01"],
        data_sources=[],
        target_paths=["medfactory/src/pipeline/ingestion_framework.py"],
        acceptance_tests=["test_dlq_routing", "test_circuit_breaker"]
    ),
    SRSModuleDefinition(
        module_code="MOD-07-02",
        titolo_capitolo="7.2. Integrazione Banca Quiz Reale",
        area_name="Real_Data_Remediation",
        applicable_roas=["ROA-02", "ROA-12"],
        direttive="Definire l'ETL per importare MedQA, MedMCQA e PubMedQA. Includere la deduplicazione e la mappatura materia/anno.",
        remediates=["MOCK-04", "MOCK-09"],
        data_sources=["medqa_usmle", "medmcqa", "pubmedqa"],
        target_paths=["medfactory/src/pipeline/quiz_ingestor.py"],
        acceptance_tests=["test_quiz_deduplication", "test_subject_mapping"]
    ),
    SRSModuleDefinition(
        module_code="MOD-07-03",
        titolo_capitolo="7.3. Ontologie Mediche Complete",
        area_name="Real_Data_Remediation",
        applicable_roas=["ROA-03", "ROA-15"],
        direttive="Progettare l'ingestion completa di HPO, Orphanet, ICD-10-CM e MeSH, rimuovendo i fallback cablati.",
        remediates=["MOCK-05"],
        data_sources=["hpo", "orphanet", "icd10cm", "mesh"],
        target_paths=["medfactory/src/pipeline/ontology_ingestor.py"],
        acceptance_tests=["test_full_ontology_load", "test_no_fallback_used"]
    ),
    SRSModuleDefinition(
        module_code="MOD-07-04",
        titolo_capitolo="7.4. Farmacologia Reale e Interazioni",
        area_name="Real_Data_Remediation",
        applicable_roas=["ROA-04", "ROA-19"],
        direttive="Definire l'integrazione di OpenFDA, DailyMed, RxNorm, AIFA, CPIC e ChEMBL per profili CYP450 reali.",
        remediates=["MOCK-07"],
        data_sources=["openfda_label", "dailymed", "rxnorm", "aifa", "cpic", "chembl"],
        target_paths=["medfactory/src/pipeline/pharmacology_ingestor.py"],
        acceptance_tests=["test_cyp450_profiles", "test_drug_interactions"]
    ),
    SRSModuleDefinition(
        module_code="MOD-07-05",
        titolo_capitolo="7.5. Monografie con Provenienza Reale",
        area_name="Real_Data_Remediation",
        applicable_roas=["ROA-05", "ROA-22"],
        direttive="Progettare la sintesi di monografie basate su fonti citate (PubMed/Europe PMC) con conservazione della provenienza.",
        remediates=["MOCK-02", "MOCK-06"],
        data_sources=["pubmed_eutils", "europepmc"],
        target_paths=["medfactory/src/pipeline/monograph_generator.py"],
        acceptance_tests=["test_provenance_tracking", "test_literature_synthesis"]
    ),
    SRSModuleDefinition(
        module_code="MOD-07-06",
        titolo_capitolo="7.6. Embedding Reali e Traduzione Offline",
        area_name="Real_Data_Remediation",
        applicable_roas=["ROA-11", "ROA-30"],
        direttive="Sostituire gli embedding finti con MiniLM multilingue locale e definire il sistema di traduzione offline via Ollama con caching.",
        remediates=["MOCK-01"],
        data_sources=["st_minilm_multi", "ollama_translate"],
        target_paths=["medfactory/src/pipeline/embedding_engine.py"],
        acceptance_tests=["test_real_embeddings", "test_ollama_translation"]
    ),
    SRSModuleDefinition(
        module_code="MOD-07-07",
        titolo_capitolo="7.7. Sicurezza Crittografica Forte",
        area_name="Real_Data_Remediation",
        applicable_roas=["ROA-27", "ROA-33"],
        direttive="Progettare l'uso di chiavi Ed25519 reali protette da DPAPI per la firma dei medpack e token IPC effimeri per il backend sidecar.",
        remediates=["MOCK-03", "MOCK-10"],
        data_sources=[],
        target_paths=["medclient/core-rust/security.rs", "medclient/sidecar-python/auth.py"],
        acceptance_tests=["test_ed25519_signature", "test_ephemeral_ipc"]
    ),
    SRSModuleDefinition(
        module_code="MOD-07-08",
        titolo_capitolo="7.8. Fonti Utente e Lessico Reale",
        area_name="Real_Data_Remediation",
        applicable_roas=["ROA-09", "ROA-24"],
        direttive="Definire il supporto per fonti personalizzate dell'utente e la semina del lessico SymSpell basato su un corpus clinico reale.",
        remediates=["GAP-08", "MOCK-08"],
        data_sources=["user_custom"],
        target_paths=["medclient/sidecar-python/custom_ingestor.py", "medfactory/src/pipeline/symspell_builder.py"],
        acceptance_tests=["test_custom_source_import", "test_real_symspell_corpus"]
    )
]
