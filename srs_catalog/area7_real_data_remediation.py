from typing import List
from srs_catalog.models import SRSModuleDefinition

AREA7_MODULES: List[SRSModuleDefinition] = [
    SRSModuleDefinition(
        module_code="MOD-07-01",
        titolo_capitolo="7.1. Framework di Ingestion e Resilienza",
        area_name="Real_Data_Remediation",
        applicable_roas=["ROA-01", "ROA-08"],
        direttive="Implementare un framework IDatasetConnector con caching SHA-256, Dead Letter Queue (DLQ), backoff esponenziale e circuit breaker.",
        remediates=["MOCK-04", "GAP-01"],
        data_sources=[],
        target_paths=["medfactory/src/pipeline/ingestion.py"],
        acceptance_tests=["test_dlq", "test_circuit_breaker"]
    ),
    SRSModuleDefinition(
        module_code="MOD-07-02",
        titolo_capitolo="7.2. Integrazione Banca Quiz Reale",
        area_name="Real_Data_Remediation",
        applicable_roas=["ROA-02", "ROA-12"],
        direttive="Integrazione con fonti reali per i quiz (MedQA, MedMCQA, PubMedQA) includendo deduplica e mappatura materia/anno.",
        remediates=["MOCK-04", "MOCK-09"],
        data_sources=["medqa_usmle", "medmcqa", "pubmedqa"],
        target_paths=["medfactory/src/pipeline/quiz_ingestor.py"],
        acceptance_tests=["test_quiz_deduplication", "test_materia_mapping"]
    ),
    SRSModuleDefinition(
        module_code="MOD-07-03",
        titolo_capitolo="7.3. Ontologie Mediche Complete",
        area_name="Real_Data_Remediation",
        applicable_roas=["ROA-03", "ROA-15"],
        direttive="Rimuovere i fallback cablati per HPO, ICD-10, Orphanet, MeSH e utilizzare i dataset reali completi.",
        remediates=["MOCK-05"],
        data_sources=["hpo", "orphanet", "icd10cm", "mesh"],
        target_paths=["medfactory/src/ontologies/implementations/hpo_ingestor.py"],
        acceptance_tests=["test_full_ontology_load"]
    ),
    SRSModuleDefinition(
        module_code="MOD-07-04",
        titolo_capitolo="7.4. Farmacologia Reale e Interazioni",
        area_name="Real_Data_Remediation",
        applicable_roas=["ROA-04", "ROA-19"],
        direttive="Integrazione con OpenFDA, DailyMed, RxNorm, AIFA, CPIC, ChEMBL per sostituire i profili statici di interazioni farmacologiche e CYP450.",
        remediates=["MOCK-07"],
        data_sources=["openfda_label", "dailymed", "rxnorm", "aifa", "cpic", "chembl"],
        target_paths=["medclient/sidecar-python/src/implementations/cyp450_engine.py"],
        acceptance_tests=["test_real_interactions", "test_cyp450_profiles"]
    ),
    SRSModuleDefinition(
        module_code="MOD-07-05",
        titolo_capitolo="7.5. Monografie con Provenienza Reale",
        area_name="Real_Data_Remediation",
        applicable_roas=["ROA-05", "ROA-22"],
        direttive="Sostituire le monografie e citazioni fittizie (Prof. M. Rossi) con fonti certificate da PubMed e Europe PMC.",
        remediates=["MOCK-02", "MOCK-06"],
        data_sources=["pubmed_eutils", "europepmc"],
        target_paths=["medfactory/medfactory_pipeline.py"],
        acceptance_tests=["test_real_citations"]
    ),
    SRSModuleDefinition(
        module_code="MOD-07-06",
        titolo_capitolo="7.6. Embedding Reali e Traduzione Offline",
        area_name="Real_Data_Remediation",
        applicable_roas=["ROA-11", "ROA-30"],
        direttive="Rimuovere embedding finti derivati da hash. Utilizzare MiniLM multilingue e traduzione offline Ollama.",
        remediates=["MOCK-01"],
        data_sources=["st_minilm_multi", "ollama_translate"],
        target_paths=["medfactory/src/pipeline/base/clinical_dataset_seed.py"],
        acceptance_tests=["test_real_embeddings", "test_offline_translation"]
    ),
    SRSModuleDefinition(
        module_code="MOD-07-07",
        titolo_capitolo="7.7. Sicurezza Crittografica Forte",
        area_name="Real_Data_Remediation",
        applicable_roas=["ROA-27", "ROA-33"],
        direttive="Sostituire chiave Ed25519 derivata da stringa nota e token IPC fallback con implementazioni sicure DPAPI e token IPC effimero.",
        remediates=["MOCK-03", "MOCK-10"],
        data_sources=[],
        target_paths=["medfactory/medfactory_pipeline.py", "medclient/frontend-react/src/MedClientAppShell.tsx"],
        acceptance_tests=["test_ephemeral_ipc", "test_secure_ed25519"]
    ),
    SRSModuleDefinition(
        module_code="MOD-07-08",
        titolo_capitolo="7.8. Fonti Utente e Lessico Reale",
        area_name="Real_Data_Remediation",
        applicable_roas=["ROA-09", "ROA-24"],
        direttive="Implementare supporto per user_knowledge_sources personalizzate e sostituire il lessico SymSpell seminato a mano con un corpus reale.",
        remediates=["GAP-08", "MOCK-08"],
        data_sources=["user_custom"],
        target_paths=["medclient/sidecar-python/src/implementations/symspell_checker.py"],
        acceptance_tests=["test_user_sources", "test_real_symspell"]
    )
]
