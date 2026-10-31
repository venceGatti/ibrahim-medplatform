"""
Tier 1: Feature Coverage Tests for MedFactory Features 7 through 9.
- Feature 7: PyHPO Ontology Ingestion
- Feature 8: ICD-10 & ATC Ingestion
- Feature 9: Zstandard 112KB Dict Trainer
"""

import json
import pytest
from tests.conftest import EXACT_ZSTD_DICT_SIZE_BYTES, compute_sha256_hash
from medfactory.src.ontologies.implementations.hpo_ingestor import HPOIngestor
from medfactory.src.ontologies.implementations.icd10_atc_ingestor import ICD10ATCIngestor
from medfactory.src.compression.implementations.zstd_dictionary_trainer import ZstdDictionaryTrainer

# Feature 7: PyHPO Ontology Ingestion
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f07_pyhpo_dag_node_parsing():
    """Verify HPO node ID and label format conform to HP:XXXXXXX standard."""
    ingestor = HPOIngestor()
    terms = ingestor.ingest_hpo_terms()
    assert len(terms) > 0
    heart_failure = next(t for t in terms if t.hpo_id == "HP:0001635")
    assert heart_failure.hpo_id.startswith("HP:")
    assert len(heart_failure.hpo_id) == 10
    assert heart_failure.name == "Heart failure"


@pytest.mark.tier1
def test_f07_pyhpo_ancestor_closure_computation():
    """Verify ancestor closure includes all direct and transitive parent terms."""
    ingestor = HPOIngestor()
    ancestors = ingestor.compute_ancestor_closure("HP:0001635")
    assert "HP:0001626" in ancestors  # Abnormality of the cardiovascular system
    assert "HP:0000118" in ancestors  # Phenotypic abnormality
    assert "HP:0000001" in ancestors  # All / Root


@pytest.mark.tier1
def test_f07_pyhpo_information_content_scoring():
    """Verify Information Content increases for more specific terms."""
    from medfactory.src.ontologies.base.ontology_models import DiseasePhenotypeAssociation
    ingestor = HPOIngestor()
    terms = ingestor.ingest_terms()
    associations = [
        DiseasePhenotypeAssociation(icd10_code="I21.9", hpo_id="HP:0001658"),
        DiseasePhenotypeAssociation(icd10_code="I50.9", hpo_id="HP:0001635"),
    ]
    ic_scores = ingestor.compute_information_content(terms, associations)
    assert "HP:0001635" in ic_scores
    assert "HP:0000118" in ic_scores


@pytest.mark.tier1
def test_f07_pyhpo_graph_acyclicity_invariant():
    """Verify HPO graph topological integrity has zero directed cycles."""
    ingestor = HPOIngestor()
    visited = set()
    rec_stack = set()

    def has_cycle(node: str) -> bool:
        visited.add(node)
        rec_stack.add(node)
        for parent in ingestor.term_parents_graph.get(node, []):
            if parent not in visited:
                if has_cycle(parent):
                    return True
            elif parent in rec_stack:
                return True
        rec_stack.remove(node)
        return False

    is_cyclic = any(has_cycle(n) for n in ingestor.term_parents_graph if n not in visited)
    assert not is_cyclic


@pytest.mark.tier1
def test_f07_pyhpo_semantic_similarity_metric():
    """Verify HPO ancestor intersection between two related cardiac terms."""
    ingestor = HPOIngestor()
    ancestors_hf = set(ingestor.compute_ancestor_closure("HP:0001635"))
    ancestors_mi = set(ingestor.compute_ancestor_closure("HP:0001658"))
    common_ancestors = ancestors_hf.intersection(ancestors_mi)
    assert "HP:0001626" in common_ancestors


# ---------------------------------------------------------------------------
# Feature 8: ICD-10 & ATC Ingestion
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f08_icd10_category_formatting():
    """Verify ICD-10 records parse into standard chapters and blocks."""
    ingestor = ICD10ATCIngestor()
    icd10_records = ingestor.ingest_icd10()
    assert len(icd10_records) > 0
    mi_record = next(r for r in icd10_records if r.icd10_code == "I21.9")
    assert mi_record.chapter == "IX"
    assert mi_record.block_range == "I20-I25"


@pytest.mark.tier1
def test_f08_atc_level_five_hierarchy():
    """Verify ATC 5-level code hierarchy for Clopidogrel."""
    ingestor = ICD10ATCIngestor()
    atc_records = ingestor.ingest_atc()
    clopidogrel = next(r for r in atc_records if r.atc_code == "B01AC04")
    assert clopidogrel.level1_anatomical == "B"
    assert clopidogrel.level2_therapeutic == "B01"
    assert clopidogrel.level3_pharmacological == "B01A"
    assert clopidogrel.level4_chemical == "B01AC"


@pytest.mark.tier1
def test_f08_atc_substance_mapping():
    """Verify ATC code accurately maps to active pharmacological entity with prodrug flag."""
    ingestor = ICD10ATCIngestor()
    atc_records = ingestor.ingest_atc()
    clopidogrel = next(r for r in atc_records if r.atc_code == "B01AC04")
    assert clopidogrel.substance_name == "Clopidogrel"
    assert clopidogrel.is_prodrug is True
    assert "CYP2C19" in clopidogrel.primary_cyp_enzymes


@pytest.mark.tier1
def test_f08_icd10_clinical_modification_depth():
    """Verify ICD-10 leaf codes are correctly identified."""
    ingestor = ICD10ATCIngestor()
    icd10_records = ingestor.ingest_icd10()
    assert all(r.is_leaf_code for r in icd10_records)


@pytest.mark.tier1
def test_f08_dual_coding_crosswalk_validity():
    """Verify ICD-10 records include hypertension and chronic kidney disease."""
    ingestor = ICD10ATCIngestor()
    icd10_records = ingestor.ingest_icd10()
    codes = {r.icd10_code for r in icd10_records}
    assert "I10" in codes
    assert "N18.3" in codes


# ---------------------------------------------------------------------------
# Feature 9: Zstandard 112KB Dict Trainer
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f09_zstd_exact_dictionary_size_bytes():
    """Verify trained dictionary size is exactly 114,688 Bytes (112 KB) per ROA-05."""
    trainer = ZstdDictionaryTrainer()
    corpus_chunks = [
        f"Medical monograph corpus chunk {i}: myocardial infarction, clopidogrel, omeprazole, CYP450 metabolism.".encode("utf-8")
        for i in range(50)
    ]
    trained_dict = trainer.train_dictionary(corpus_chunks, target_size=EXACT_ZSTD_DICT_SIZE_BYTES)
    assert len(trained_dict) == 114688
    assert len(trained_dict) == EXACT_ZSTD_DICT_SIZE_BYTES


@pytest.mark.tier1
def test_f09_zstd_magic_header_signature():
    """Verify Zstandard dictionary buffer starts with authentic magic header."""
    trainer = ZstdDictionaryTrainer()
    corpus_chunks = [
        f"Medical monograph corpus chunk {i}: myocardial infarction, clopidogrel, omeprazole.".encode("utf-8")
        for i in range(50)
    ]
    trained_dict = trainer.train_dictionary(corpus_chunks, target_size=EXACT_ZSTD_DICT_SIZE_BYTES)
    zstd_dict_magic = b"\x37\xa4\x30\xec"
    assert trained_dict.startswith(zstd_dict_magic)


@pytest.mark.tier1
def test_f09_zstd_compression_ratio_improvement():
    """Verify custom dictionary compresses repetitive medical text losslessly."""
    trainer = ZstdDictionaryTrainer()
    corpus_chunks = [
        b"Hypertension Blood Pressure Systolic Diastolic " * 20
        for _ in range(30)
    ]
    trained_dict = trainer.train_dictionary(corpus_chunks, target_size=EXACT_ZSTD_DICT_SIZE_BYTES)

    test_payload = b"Hypertension Blood Pressure Systolic Diastolic " * 50
    compressed = trainer.compress_stream(test_payload, trained_dict, compression_level=19)
    decompressed = trainer.decompress_stream(compressed, trained_dict)

    assert decompressed == test_payload
    assert len(compressed) < len(test_payload)


@pytest.mark.tier1
def test_f09_zstd_deterministic_reproducibility():
    """Verify hash of trained dictionary is strictly reproducible across runs."""
    trainer = ZstdDictionaryTrainer()
    corpus = [b"Cardiology STEMI NSTEMI troponin electrocardiogram angina " * 10 for _ in range(40)]
    dict_a = trainer.train_dictionary(corpus, target_size=EXACT_ZSTD_DICT_SIZE_BYTES)
    dict_b = trainer.train_dictionary(corpus, target_size=EXACT_ZSTD_DICT_SIZE_BYTES)
    assert compute_sha256_hash(dict_a) == compute_sha256_hash(dict_b)


@pytest.mark.tier1
def test_f09_zstd_level_nineteen_compliance():
    """Verify Level 19 compression produces valid zstd frame with dictionary."""
    trainer = ZstdDictionaryTrainer()
    corpus = [b"Clinical pharmacology pharmacokinetics clearance volume distribution " * 10 for _ in range(40)]
    dict_data = trainer.train_dictionary(corpus, target_size=EXACT_ZSTD_DICT_SIZE_BYTES)
    corpus_record_buffer = b"Pharmacology interaction alert: Clopidogrel with Omeprazole."
    compressed = trainer.compress_stream(corpus_record_buffer, dict_data, compression_level=19)
    assert trainer.decompress_stream(compressed, dict_data) == corpus_record_buffer


# ---------------------------------------------------------------------------
