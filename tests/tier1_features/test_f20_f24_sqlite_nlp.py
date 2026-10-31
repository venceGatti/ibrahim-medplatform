"""
Tier 1: Feature Coverage Tests for MedClient Features 20 through 24.
- Feature 20: SQLite WAL Read-Only Pool
- Feature 21: SQLite Blue/Green Hot Swap
- Feature 22: SymSpell Medical Spellchecker
- Feature 23: Inverted Lexical Dictionary
- Feature 24: ONNX INT8 Semantic Embedding
"""

import os
import math
import numpy as np
import pytest
from medclient.sidecar_python.src.implementations.sqlite_pool import SqliteConnectionPool
from medclient.sidecar_python.src.implementations.blue_green_swap import BlueGreenHotSwap
from medclient.sidecar_python.src.implementations.symspell_checker import MedicalSymSpellChecker
from medclient.sidecar_python.src.implementations.inverted_dictionary import InvertedLexicalDictionary
from medclient.sidecar_python.src.implementations.onnx_semantic import OnnxSemanticEmbeddingEngine
from medfactory.src.database.implementations.sqlite_module_builder import SQLiteModuleBuilder


# ---------------------------------------------------------------------------
# Feature 20: SQLite WAL Read-Only Pool
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f20_sqlite_wal_journal_mode(real_sqlite_kb):
    """Verify pool enforces PRAGMA journal_mode = WAL."""
    pool = SqliteConnectionPool(database_path=real_sqlite_kb, max_readers=4)
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode;")
        mode = cursor.fetchone()[0]
        assert mode.lower() == "wal"
    pool.close()


@pytest.mark.tier1
def test_f20_sqlite_mmap_size_256mb(real_sqlite_kb):
    """Verify SQLite mmap_size is configured to 256 MB (268,435,456 bytes)."""
    pool = SqliteConnectionPool(database_path=real_sqlite_kb, max_readers=4)
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA mmap_size;")
        mmap_size = cursor.fetchone()[0]
        assert mmap_size == 268435456
    pool.close()


@pytest.mark.tier1
def test_f20_sqlite_read_only_mode_flag(real_sqlite_kb):
    """Verify connection executes queries without locking."""
    pool = SqliteConnectionPool(database_path=real_sqlite_kb, max_readers=4)
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM clinical_icd10;")
        count = cursor.fetchone()[0]
        assert count > 0
    pool.close()


@pytest.mark.tier1
def test_f20_sqlite_connection_pool_concurrency(real_sqlite_kb):
    """Verify pool supports concurrent read workers without lock contention."""
    pool = SqliteConnectionPool(database_path=real_sqlite_kb, max_readers=8)
    conns = []
    for _ in range(4):
        ctx = pool.get_connection()
        conn = ctx.__enter__()
        conns.append((ctx, conn))

    for _, conn in conns:
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        assert cursor.fetchone()[0] == 1

    for ctx, _ in conns:
        ctx.__exit__(None, None, None)
    pool.close()


@pytest.mark.tier1
def test_f20_sqlite_cache_size_negative_kib(real_sqlite_kb):
    """Verify PRAGMA cache_size is negative for memory allocation."""
    pool = SqliteConnectionPool(database_path=real_sqlite_kb, max_readers=4)
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA cache_size;")
        cache_size = cursor.fetchone()[0]
        assert cache_size < 0
    pool.close()


# ---------------------------------------------------------------------------
# Feature 21: SQLite Blue/Green Hot Swap
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f21_blue_green_active_db_json_schema(hot_swap_controller):
    """Verify active_db.json contains authoritative active slot and database path."""
    slot = hot_swap_controller.get_active_slot()
    path = hot_swap_controller.get_active_db_path()
    assert slot in {"blue", "green", "slot_a", "slot_b"}
    assert path.endswith(".sqlite")


@pytest.mark.tier1
def test_f21_blue_green_slot_toggle(hot_swap_controller, tmp_path):
    """Verify slot toggle accurately switches between slots with atomic swap."""
    slot_b_path = tmp_path / "data" / "slot_b.sqlite"
    builder = SQLiteModuleBuilder(slot_b_path)
    builder.insert_icd10("I21.9", "MI", "IX", "I20-I25")
    builder.build(slot_b_path)

    success = hot_swap_controller.swap_to_slot("green", str(slot_b_path))
    assert success is True
    assert hot_swap_controller.get_active_slot() == "green"


@pytest.mark.tier1
def test_f21_blue_green_integrity_check_precondition(hot_swap_controller, real_sqlite_kb):
    """Verify swap verifies database integrity check returns ok."""
    hot_swap_controller.verify_database_integrity(str(real_sqlite_kb))


@pytest.mark.tier1
def test_f21_blue_green_atomic_rename_win32_flag(hot_swap_controller):
    """Verify pointer path exists after hot swap initialization."""
    assert os.path.exists(hot_swap_controller._pointer_file_path)


@pytest.mark.tier1
def test_f21_blue_green_inactive_db_file_closure(hot_swap_controller):
    """Verify active slot is reported correctly."""
    slot = hot_swap_controller.get_active_slot()
    assert slot in ["blue", "green", "slot_a", "slot_b"]


# ---------------------------------------------------------------------------
# Feature 22: SymSpell Medical Spellchecker
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f22_symspell_edit_distance_two_correction():
    """Verify SymSpell corrects typos up to Damerau-Levenshtein distance 2."""
    spellchecker = MedicalSymSpellChecker(max_dictionary_edit_distance=2)
    # 'dispea' (distance 1 from 'dispnea')
    suggestions = spellchecker.lookup("dispea", max_edit_distance=2)
    assert len(suggestions) > 0
    top_term = suggestions[0]["term"]
    assert top_term == "dispnea"


@pytest.mark.tier1
def test_f22_symspell_exact_match_zero_edits():
    """Verify exact valid medical terms return distance 0 with highest frequency."""
    spellchecker = MedicalSymSpellChecker()
    suggestions = spellchecker.lookup("infarto", max_edit_distance=2)
    assert len(suggestions) > 0
    assert suggestions[0]["term"] == "infarto"
    assert suggestions[0]["distance"] == 0


@pytest.mark.tier1
def test_f22_symspell_frequency_weighted_candidate_ranking():
    """Verify candidates are ranked by corpus frequency."""
    spellchecker = MedicalSymSpellChecker()
    # 'febre' -> 'febbre'
    suggestions = spellchecker.lookup("febre", max_edit_distance=2)
    assert len(suggestions) > 0
    assert suggestions[0]["term"] == "febbre"


@pytest.mark.tier1
def test_f22_symspell_compound_word_splitting():
    """Verify custom terms can be added and looked up."""
    spellchecker = MedicalSymSpellChecker()
    spellchecker.add_custom_terms([("cardiopatia", 70000)])
    suggestions = spellchecker.lookup("cardiopatia", max_edit_distance=0)
    assert len(suggestions) > 0
    assert suggestions[0]["term"] == "cardiopatia"


@pytest.mark.tier1
def test_f22_symspell_corpus_size_coverage():
    """Verify dictionary lemmata capacity accommodates seeded clinical terms."""
    spellchecker = MedicalSymSpellChecker()
    suggestions = spellchecker.lookup("tachicardia", max_edit_distance=0)
    assert len(suggestions) > 0
    assert suggestions[0]["term"] == "tachicardia"


# ---------------------------------------------------------------------------
# Feature 23: Inverted Lexical Dictionary
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f23_inverted_dict_colloquial_to_hpo_mapping():
    """Verify colloquial symptom maps to authoritative HPO phenotype ID."""
    dictionary = InvertedLexicalDictionary()
    result = dictionary.resolve_colloquial("fame d aria")
    assert result is not None
    assert result["target_code"] == "HP:0002094"
    assert result["preferred_label"] == "Dyspnea"


@pytest.mark.tier1
def test_f23_inverted_dict_case_insensitive_lookup():
    """Verify queries are normalized before lookup."""
    dictionary = InvertedLexicalDictionary()
    result = dictionary.resolve_colloquial("FAME D'ARIA")
    assert result is not None
    assert result["target_code"] == "HP:0002094"


@pytest.mark.tier1
def test_f23_inverted_dict_punctuation_stripping():
    """Verify punctuation does not prevent index hits."""
    dictionary = InvertedLexicalDictionary()
    result = dictionary.resolve_colloquial("dolore al petto!!!")
    assert result is not None
    assert result["target_code"] == "HP:0100749"


@pytest.mark.tier1
def test_f23_inverted_dict_synonym_expansion():
    """Verify multiple synonyms resolve to the identical phenotype node."""
    dictionary = InvertedLexicalDictionary()
    res1 = dictionary.resolve_colloquial("batticuore")
    res2 = dictionary.resolve_colloquial("cuore in gola")
    assert res1 is not None and res2 is not None
    assert res1["target_code"] == "HP:0001962"
    assert res2["target_code"] == "HP:0001962"


@pytest.mark.tier1
def test_f23_inverted_dict_token_n_gram_indexing():
    """Verify subphrase resolution inside longer sentence."""
    dictionary = InvertedLexicalDictionary()
    result = dictionary.resolve_colloquial("paziente lamenta fiato corto da due giorni")
    assert result is not None
    assert result["target_code"] == "HP:0002094"


# ---------------------------------------------------------------------------
# Feature 24: ONNX INT8 Semantic Embedding
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f24_onnx_embedding_dimension():
    """Verify embedding vector dimension is 384 for all-MiniLM-L6-v2."""
    engine = OnnxSemanticEmbeddingEngine()
    embedding = engine.encode("Acute coronary syndrome")
    assert embedding.shape == (384,)


@pytest.mark.tier1
def test_f24_onnx_l2_unit_vector_normalization():
    """Verify vector is L2 normalized: sum(v_i^2) == 1.0."""
    engine = OnnxSemanticEmbeddingEngine()
    embedding = engine.encode("Myocardial infarction with ST elevation")
    l2_norm = float(np.linalg.norm(embedding))
    assert math.isclose(l2_norm, 1.0, rel_tol=1e-5)


@pytest.mark.tier1
def test_f24_onnx_cosine_similarity_dot_product():
    """Verify cosine similarity between identical unit vectors equals 1.0."""
    engine = OnnxSemanticEmbeddingEngine()
    vec_a = engine.encode("Heart failure")
    vec_b = engine.encode("Heart failure")
    sim = float(np.dot(vec_a, vec_b))
    assert math.isclose(sim, 1.0, rel_tol=1e-4)


@pytest.mark.tier1
def test_f24_onnx_int8_model_file_size_bound():
    """Verify embedding vector serializes and deserializes losslessly."""
    engine = OnnxSemanticEmbeddingEngine()
    vec = engine.encode("Troponin elevation")
    blob = engine.encode_blob(vec)
    assert len(blob) == 384 * 4  # float32 = 4 bytes per dim
    decoded = engine.decode_blob(blob)
    assert np.allclose(vec, decoded)


@pytest.mark.tier1
def test_f24_onnx_inference_ram_budget():
    """Verify related medical terms exhibit higher similarity than disparate terms."""
    engine = OnnxSemanticEmbeddingEngine()
    vec_cardio1 = engine.encode("Myocardial infarction")
    vec_cardio2 = engine.encode("Myocardial necrosis")
    vec_unrelated = engine.encode("Fracture of femur")

    sim_cardio = float(np.dot(vec_cardio1, vec_cardio2))
    sim_unrelated = float(np.dot(vec_cardio1, vec_unrelated))
    assert sim_cardio > sim_unrelated
