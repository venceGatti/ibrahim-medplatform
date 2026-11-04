import pytest
from srs_catalog.models import SRSModuleDefinition, DataSourceSpec
from srs_catalog.data_sources_registry import DATA_SOURCES_REGISTRY
from srs_generator.mock_scanner import audit_codebase_gaps
from srs_generator.remediation_prompt import build_remediation_prompt
from pathlib import Path

def test_registry_has_required_sources():
    assert "medqa_usmle" in DATA_SOURCES_REGISTRY
    assert "medmcqa" in DATA_SOURCES_REGISTRY
    assert "pubmedqa" in DATA_SOURCES_REGISTRY

def test_mock_scanner():
    findings = audit_codebase_gaps(Path("."))
    assert len(findings) >= 13
    assert any(f.gap_ref == "MOCK-01" for f in findings)
    assert any(f.gap_ref == "GAP-01" for f in findings)

def test_remediation_prompt():
    mod = SRSModuleDefinition(
        module_code="MOD-07-01",
        titolo_capitolo="Test Mod",
        area_name="Test",
        direttive="Test directives",
        remediates=["MOCK-01"],
        data_sources=["medqa_usmle"]
    )
    findings = audit_codebase_gaps(Path("."))
    prompt = build_remediation_prompt(mod, findings, DATA_SOURCES_REGISTRY)
    assert "MOCK-01" in prompt
    assert "MedQA-USMLE" in prompt
    assert "Test directives" in prompt

def test_all_modules_loaded():
    from srs_catalog import ALL_SRS_MODULES
    assert len(ALL_SRS_MODULES) == 38
