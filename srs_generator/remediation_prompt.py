from typing import List, Dict
from srs_catalog import SRSModuleDefinition
from srs_catalog.models import DataSourceSpec
from srs_generator.mock_scanner import CodeGapFinding

def build_remediation_prompt(
    module: SRSModuleDefinition,
    findings: List[CodeGapFinding],
    sources: Dict[str, DataSourceSpec]
) -> str:
    prompt = f"Sei un Architetto Software Specializzato in MedPlatform.\n\n"
    prompt += f"OBIETTIVO: Progettare la remediation per il modulo {module.module_code} - {module.titolo_capitolo}.\n"
    prompt += f"DIRETTIVE: {module.direttive}\n\n"

    if module.remediates:
        prompt += "MOCK/GAP DA RISOLVERE:\n"
        for ref in module.remediates:
            matching_findings = [f for f in findings if f.gap_ref == ref]
            for f in matching_findings:
                prompt += f"- [{f.gap_ref}] {f.file_path}:{f.line_number} -> {f.extract}\n"
        prompt += "\n"

    if module.data_sources:
        prompt += "FONTI DA UTILIZZARE (Non inventare URL):\n"
        for ds_key in module.data_sources:
            if ds_key in sources:
                ds = sources[ds_key]
                prompt += f"- {ds.name}: {ds.url} (Licenza: {ds.license}, Formato: {ds.format})\n"
                prompt += f"  Policy offline: {ds.offline_strategy}\n"
        prompt += "\n"

    prompt += "FORMATO DI OUTPUT OBBLIGATORIO (Markdown):\n"
    prompt += "1. Problema attuale (analisi dei mock)\n"
    prompt += "2. Fonte reale scelta (URL e licenza dal registro)\n"
    prompt += "3. Contratti Pydantic/TS\n"
    prompt += "4. DDL SQLite\n"
    prompt += "5. Pseudo-codice ETL\n"
    prompt += "6. Strategia Offline\n"
    prompt += "7. Test di Accettazione\n"
    prompt += "8. Micro-task stimati con file/righe\n"

    return prompt
