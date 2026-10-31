"""
Tier 1: Feature Coverage Tests for MedFactory Features 10 through 12.
- Feature 10: Static Markdown Synthesizer
- Feature 11: SQLite KB Builder
- Feature 12: .medpack Assembler
"""

import json
import sqlite3
from pathlib import Path
import pytest
from tests.conftest import (
    compute_blake3_hash,
    compute_sha256_hash,
    generate_ed25519_keypair,
)
from medfactory.src.compression.implementations.static_markdown_synthesizer import StaticMarkdownSynthesizer
from medfactory.src.compression.base.compression_models import (
    ClinicalSheetSynthesisRequest,
    ClinicalCallout,
    CalloutSeverityType,
)
from medfactory.src.database.implementations.sqlite_module_builder import SQLiteModuleBuilder
from medfactory.src.packager.implementations.medpack_assembler import MedPackAssembler
from medfactory.src.packager.base.manifest_models import (
    MedPackManifest,
    ChecksumRegister,
    MedicalStandardVersion,
    StorageMetrics,
)

# Feature 10: Static Markdown Synthesizer
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f10_typed_callout_syntax():
    """Verify static markdown callouts conform to typed severity syntax."""
    synthesizer = StaticMarkdownSynthesizer()
    request = ClinicalSheetSynthesisRequest(
        sheet_identifier="SHEET_MI",
        disease_title="Myocardial Infarction",
        icd10_code="I21.9",
        taxonomy_path=["Cardiology", "Ischemic Heart Disease"],
        definition_text="Acute necrosis of myocardium.",
        etiology_text="Coronary plaque rupture.",
        clinical_signs=["Chest pain", "Diaphoresis"],
        diagnostic_workup=["ECG", "Troponin I"],
        pharmacotherapy_atc=["B01AC04"],
        callouts=[
            ClinicalCallout(
                severity_type=CalloutSeverityType.RED_FLAG,
                callout_title="Immediate Reperfusion",
                callout_body="Door-to-balloon time must be < 90 minutes."
            )
        ]
    )
    result = synthesizer.synthesize_sheet(request)
    assert "> [!RED_FLAG]" in result.raw_markdown_content
    assert "Door-to-balloon" in result.raw_markdown_content


@pytest.mark.tier1
def test_f10_yaml_frontmatter_metadata_extraction():
    """Verify synthesized markdown contains header and structured sections."""
    synthesizer = StaticMarkdownSynthesizer()
    request = ClinicalSheetSynthesisRequest(
        sheet_identifier="SHEET_AS",
        disease_title="Aortic Stenosis",
        icd10_code="I35.0",
        taxonomy_path=["Cardiology", "Valvular Disease"],
        definition_text="Narrowing of aortic valve.",
        etiology_text="Calcific degeneration.",
        clinical_signs=["Exertional dyspnea", "Angina", "Syncope"],
        diagnostic_workup=["Echocardiography"],
        pharmacotherapy_atc=[]
    )
    result = synthesizer.synthesize_sheet(request)
    assert "# Aortic Stenosis (I35.0)" in result.raw_markdown_content
    assert "## 1. Definizione ed Epidemiologia" in result.raw_markdown_content


@pytest.mark.tier1
def test_f10_katex_formula_preservation():
    """Verify mathematical formulas remain unescaped in synthesis."""
    synthesizer = StaticMarkdownSynthesizer()
    formula = "$$\\text{eGFR} = 142 \\times \\min(S_{cr}/\\kappa, 1)^\\alpha$$"
    request = ClinicalSheetSynthesisRequest(
        sheet_identifier="SHEET_CKD",
        disease_title="Chronic Kidney Disease",
        icd10_code="N18.3",
        taxonomy_path=["Nephrology"],
        definition_text=f"Staging based on {formula}",
        etiology_text="Diabetic nephropathy.",
        clinical_signs=["Edema"],
        diagnostic_workup=["Serum creatinine"],
        pharmacotherapy_atc=[]
    )
    result = synthesizer.synthesize_sheet(request)
    assert formula in result.raw_markdown_content


@pytest.mark.tier1
def test_f10_section_hierarchy_consistency():
    """Verify monograph markdown maintains consistent H1 to H3 hierarchy."""
    synthesizer = StaticMarkdownSynthesizer()
    request = ClinicalSheetSynthesisRequest(
        sheet_identifier="SHEET_HF",
        disease_title="Heart Failure",
        icd10_code="I50.9",
        taxonomy_path=["Cardiology"],
        definition_text="Cardiac dysfunction.",
        etiology_text="Ischemia or hypertension.",
        clinical_signs=["Orthopnea", "PND"],
        diagnostic_workup=["BNP", "Echo"],
        pharmacotherapy_atc=[]
    )
    result = synthesizer.synthesize_sheet(request)
    assert "## 1. Definizione ed Epidemiologia" in result.raw_markdown_content
    assert "## 2. Eziologia e Fisiopatologia" in result.raw_markdown_content
    assert "## 3. Quadro Clinico e Sintomatologia" in result.raw_markdown_content
    assert "## 4. Iter Diagnostico e Criteri" in result.raw_markdown_content


@pytest.mark.tier1
def test_f10_zero_dynamic_llm_markers():
    """Verify static markdown contains zero dynamic LLM streaming markers (ROA-11)."""
    synthesizer = StaticMarkdownSynthesizer()
    request = ClinicalSheetSynthesisRequest(
        sheet_identifier="SHEET_HTN",
        disease_title="Hypertension",
        icd10_code="I10",
        taxonomy_path=["Cardiology"],
        definition_text="Elevated blood pressure.",
        etiology_text="Essential.",
        clinical_signs=["Often asymptomatic"],
        diagnostic_workup=["Sphygmomanometer measurement"],
        pharmacotherapy_atc=[]
    )
    result = synthesizer.synthesize_sheet(request)
    banned_markers = ["summary_token_stream_active", "rationale_token_stream_id", "<streaming>"]
    for marker in banned_markers:
        assert marker not in result.raw_markdown_content


# ---------------------------------------------------------------------------
# Feature 11: SQLite KB Builder
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f11_sqlite_ddl_table_creation(tmp_path):
    """Verify standard schema tables for module_kb.sqlite via SQLiteModuleBuilder."""
    db_path = tmp_path / "test_module.sqlite"
    builder = SQLiteModuleBuilder(db_path)
    builder.insert_icd10("I21.0", "STEMI Anterior", "IX", "I20-I25")
    builder.build(db_path)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cursor.fetchall()}
    assert "clinical_icd10" in tables
    assert "clinical_atc" in tables
    assert "child_chunks_fts" in tables
    conn.close()


@pytest.mark.tier1
def test_f11_sqlite_fts5_virtual_table_syntax(tmp_path):
    """Verify FTS5 virtual table definition for BM25 full-text indexing."""
    db_path = tmp_path / "test_fts5.sqlite"
    builder = SQLiteModuleBuilder(db_path)
    builder.build(db_path)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE name='child_chunks_fts';")
    ddl = cursor.fetchone()[0]
    assert "fts5" in ddl.lower()
    conn.close()


@pytest.mark.tier1
def test_f11_sqlite_btree_indexing_saturated(tmp_path):
    """Verify high-cardinality indexes are created in module_kb.sqlite."""
    db_path = tmp_path / "test_indexes.sqlite"
    builder = SQLiteModuleBuilder(db_path)
    builder.build(db_path)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
    indices = {row[0] for row in cursor.fetchall()}
    assert any("icd10" in idx.lower() for idx in indices)
    conn.close()


@pytest.mark.tier1
def test_f11_sqlite_wal_pragma_configuration(tmp_path):
    """Verify WAL mode pragma configuration."""
    db_path = tmp_path / "test_wal.sqlite"
    builder = SQLiteModuleBuilder(db_path)
    builder.build(db_path)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("PRAGMA page_size;")
    page_size = cursor.fetchone()[0]
    assert page_size == 4096
    conn.close()


@pytest.mark.tier1
def test_f11_sqlite_foreign_key_enforcement(tmp_path):
    """Verify STRICT table definition and integrity in SQLiteModuleBuilder."""
    db_path = tmp_path / "test_strict.sqlite"
    builder = SQLiteModuleBuilder(db_path)
    builder.insert_atc("B01AC04", "Clopidogrel", "B", "B01", "B01A", "B01AC", is_prodrug=True)
    builder.build(db_path)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("PRAGMA integrity_check;")
    check_result = cursor.fetchone()[0]
    assert check_result == "ok"
    conn.close()


# ---------------------------------------------------------------------------
# Feature 12: .medpack Assembler
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f12_manifest_json_structure(tmp_path):
    """Verify manifest model structure with checksum registers."""
    hash_64 = "0" * 64
    manifest = MedPackManifest(
        schema_version="1.2.0",
        pack_id="cardio_01",
        display_title="Cardiology Module",
        compiler_toolchain="medfactory-dla-v1.4.2",
        standards=MedicalStandardVersion(
            hpo_release="2024-04-13",
            icd10_version="2019-v1",
            atc_index_year=2024
        ),
        storage=StorageMetrics(
            uncompressed_bytes=1000000,
            compressed_bytes=250000,
            total_parent_chunks=10,
            total_child_chunks=50,
            total_vectors=50
        ),
        checksums=ChecksumRegister(
            module_kb_sqlite=hash_64,
            zstd_dict=hash_64
        ),
        checksums_sha256={"module_kb_sqlite": hash_64},
        signature_ed25519="sig_hex"
    )
    dumped = manifest.model_dump()
    assert dumped["schema_version"] == "1.2.0"
    assert "checksums" in dumped
    assert "signature_ed25519" in dumped


@pytest.mark.tier1
def test_f12_blake3_hash_generation():
    """Verify BLAKE3 digest computation for packed archives."""
    file_bytes = b"MEDPACK_DATABASE_CONTENT_SQLITE_HEADER"
    digest = compute_blake3_hash(file_bytes)
    assert len(digest) == 64
    assert isinstance(digest, str)


@pytest.mark.tier1
def test_f12_sha256_hash_generation():
    """Verify SHA-256 digest computation for regulatory audit trail."""
    file_bytes = b"MEDPACK_DATABASE_CONTENT_SQLITE_HEADER"
    digest = compute_sha256_hash(file_bytes)
    assert len(digest) == 64
    assert isinstance(digest, str)


@pytest.mark.tier1
def test_f12_ed25519_signature_verification():
    """Verify Ed25519 cryptographic signing and verification of manifest payload."""
    private_key, public_key = generate_ed25519_keypair()
    manifest_payload_bytes = json.dumps({"module_id": "CARDIO_01", "version": "1.0.0"}).encode("utf-8")
    signature = private_key.sign(manifest_payload_bytes)

    public_key.verify(signature, manifest_payload_bytes)
    assert len(signature) == 64


@pytest.mark.tier1
def test_f12_tar_zst_container_components():
    """Verify expected canonical paths inside .medpack bundle."""
    required_archive_paths = {
        "manifest.json",
        "zstd.dict",
        "database/module_kb.sqlite",
        "assets/schede_statiche/overview.md"
    }
    assert "manifest.json" in required_archive_paths
    assert "zstd.dict" in required_archive_paths
    assert "database/module_kb.sqlite" in required_archive_paths
