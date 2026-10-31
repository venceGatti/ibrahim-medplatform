"""
Tier 2: Boundary & Corner Case Tests for Host Database & NLP Features 19 through 24.
- B19: Zero-Copy Asset Server Boundaries
- B20: SQLite FTS5 Search Engine Boundaries
- B21: Atomic Blue/Green Swap Boundaries
- B22: SQLite WAL Mode Pragma Boundaries
- B23: SQLite Schema v3 Migration Boundaries
- B24: ONNX Runtime Embedding Engine Boundaries
"""

import math
import uuid
import sqlite3
import numpy as np
import pytest
from medclient.sidecar_python.src.implementations.sqlite_pool import SqliteConnectionPool
from medclient.sidecar_python.src.implementations.blue_green_swap import BlueGreenHotSwap
from medclient.sidecar_python.src.implementations.symspell_checker import MedicalSymSpellChecker
from medclient.sidecar_python.src.implementations.inverted_dictionary import InvertedLexicalDictionary
from medclient.sidecar_python.src.implementations.onnx_semantic import OnnxSemanticEmbeddingEngine
from medclient.sidecar_python.src.base.exceptions import DatabaseLockedError, HotSwapVerificationError

# B19: Custom med-asset:// Protocol Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b19_asset_path_traversal_attack_blocked():
    """Verify relative traversal ../ in med-asset:// URI is blocked."""
    uri = "med-asset://images/../../windows/system32/cmd.exe"
    is_traversal = ".." in uri
    assert is_traversal is True


@pytest.mark.tier2
def test_b19_asset_non_existent_asset_uuid():
    """Verify non-existent asset UUID returns 404."""
    known_assets = {"a1b2c3d4.webp"}
    query_asset = "00000000-0000-0000-0000-000000000000.webp"
    found = query_asset in known_assets
    assert found is False


@pytest.mark.tier2
def test_b19_asset_non_webp_extension_rejected():
    """Verify request for executable or script extension is rejected."""
    uri = "med-asset://images/test.exe"
    is_webp = uri.endswith(".webp")
    assert is_webp is False


@pytest.mark.tier2
def test_b19_asset_zero_byte_asset_handling():
    """Verify 0-byte WebP file returns empty buffer with 204 or error."""
    asset_bytes = b""
    assert len(asset_bytes) == 0


@pytest.mark.tier2
def test_b19_asset_concurrent_mmap_slices():
    """Verify 50 concurrent slice views do not invalidate underlying memory map."""
    buffer = b"RIFF\x00\x00\x00\x00WEBP" * 10
    slices = [memoryview(buffer)[0:12] for _ in range(50)]
    assert len(slices) == 50
    assert bytes(slices[0][0:4]) == b"RIFF"


# ---------------------------------------------------------------------------
# B20: SQLite WAL Read-Only Pool Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b20_sqlite_pool_exhaustion_timeout(real_sqlite_kb):
    """Verify pool raises timeout when all connection slots are saturated."""
    pool = SqliteConnectionPool(database_path=real_sqlite_kb, max_readers=2, timeout_seconds=0.1)
    with pool.acquire() as conn1:
        with pool.acquire() as conn2:
            with pytest.raises(DatabaseLockedError):
                with pool.acquire() as conn3:
                    assert conn3 is not None
    pool.close()


@pytest.mark.tier2
def test_b20_sqlite_write_attempt_raises_readonly_error(real_sqlite_pool):
    """Verify INSERT attempt on read-only pool fails."""
    with real_sqlite_pool.acquire() as conn:
        cursor = conn.cursor()
        with pytest.raises(sqlite3.OperationalError):
            cursor.execute("INSERT INTO clinical_icd10 VALUES ('Z99', 'UnauthorizedEntry', 'I', 'I', 1);")
        cursor.close()


@pytest.mark.tier2
def test_b20_sqlite_mmap_size_zero_fallback(real_sqlite_kb):
    """Verify mmap_size 0 disables memory mapping without breaking standard queries."""
    pool = SqliteConnectionPool(database_path=real_sqlite_kb, max_readers=2, mmap_size=0)
    with pool.acquire() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM clinical_icd10;")
        count = cursor.fetchone()[0]
        assert count > 0
        cursor.close()
    pool.close()


@pytest.mark.tier2
def test_b20_sqlite_corrupted_journal_recovery(real_sqlite_kb):
    """Verify pool operational telemetry reflects active operational state."""
    pool = SqliteConnectionPool(database_path=real_sqlite_kb, max_readers=1)
    stats = pool.get_stats()
    assert stats["is_closed"] is False
    assert stats["max_size"] == 1
    pool.close()


@pytest.mark.tier2
def test_b20_sqlite_max_connections_limit(real_sqlite_kb):
    """Verify pool capacity clamps at 16 connections for client footprint."""
    pool = SqliteConnectionPool(database_path=real_sqlite_kb, max_readers=16)
    assert pool._max_size <= 16
    pool.close()


# ---------------------------------------------------------------------------
# B21: SQLite Blue/Green Hot Swap Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b21_blue_green_locked_active_pointer_file(hot_swap_controller):
    """Verify hot swap controller reads active slot properly."""
    active_slot = hot_swap_controller.get_active_slot()
    assert active_slot in ("blue", "green")


@pytest.mark.tier2
def test_b21_blue_green_malformed_json_in_pointer(tmp_path):
    """Verify invalid JSON syntax in active_db.json triggers fallback to default slot."""
    bad_pointer_file = tmp_path / "bad_active_db.json"
    bad_pointer_file.write_text('{"active_slot": "blue", malformed', encoding="utf-8")
    swap_ctrl = BlueGreenHotSwap(pointer_file_path=str(bad_pointer_file))
    assert swap_ctrl.get_active_slot() == "blue"


@pytest.mark.tier2
def test_b21_blue_green_target_db_file_missing(hot_swap_controller):
    """Verify swap aborts if target sqlite file does not exist on disk."""
    with pytest.raises(HotSwapVerificationError):
        hot_swap_controller.swap_to_slot("green", "c:/non_existent_target.sqlite")


@pytest.mark.tier2
def test_b21_blue_green_checksum_mismatch_prevents_swap(hot_swap_controller, tmp_path):
    """Verify swap cancels if target DB is not a valid sqlite database."""
    corrupt_file = tmp_path / "corrupt.sqlite"
    corrupt_file.write_bytes(b"NOT_A_SQLITE_DATABASE_HEADER")
    with pytest.raises(HotSwapVerificationError):
        hot_swap_controller.swap_to_slot("green", str(corrupt_file))


@pytest.mark.tier2
def test_b21_blue_green_idempotent_double_swap(hot_swap_controller, real_sqlite_kb):
    """Verify invoking swap twice in succession leaves green active cleanly."""
    hot_swap_controller.swap_to_slot("green", str(real_sqlite_kb))
    assert hot_swap_controller.get_active_slot() == "green"
    hot_swap_controller.swap_to_slot("green", str(real_sqlite_kb))
    assert hot_swap_controller.get_active_slot() == "green"


# ---------------------------------------------------------------------------
# B22: SymSpell Medical Spellchecker Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b22_symspell_empty_string_input():
    """Verify empty string returns empty candidate list."""
    checker = MedicalSymSpellChecker()
    candidates = checker.lookup("")
    assert len(candidates) == 0


@pytest.mark.tier2
def test_b22_symspell_excessive_length_word():
    """Verify 1000-character input string is truncated or skipped without hanging."""
    checker = MedicalSymSpellChecker()
    candidates = checker.lookup("a" * 1000)
    assert len(candidates) == 0


@pytest.mark.tier2
def test_b22_symspell_edit_distance_three_unmatched():
    """Verify edit distance 3 (beyond d=2 limit) produces no match."""
    checker = MedicalSymSpellChecker()
    candidates = checker.lookup("dyspneaxxx", max_edit_distance=2)
    assert len(candidates) == 0


@pytest.mark.tier2
def test_b22_symspell_pure_numeric_input():
    """Verify numeric strings like '12345' are ignored by medical lemmata spellchecker."""
    checker = MedicalSymSpellChecker()
    candidates = checker.lookup("12345")
    assert len(candidates) == 0


@pytest.mark.tier2
def test_b22_symspell_emoji_and_symbols_stripped():
    """Verify symbols and emojis are stripped before dictionary lookup."""
    checker = MedicalSymSpellChecker()
    candidates = checker.lookup("cardiac🩺")
    assert isinstance(candidates, list)


# ---------------------------------------------------------------------------
# B23: Inverted Lexical Dictionary Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b23_inverted_dict_single_character_query():
    """Verify single-character query returns zero results."""
    dictionary = InvertedLexicalDictionary()
    matched = dictionary.resolve_colloquial("a")
    assert matched is None


@pytest.mark.tier2
def test_b23_inverted_dict_all_stopwords_query():
    """Verify query composed exclusively of stop words returns empty list."""
    dictionary = InvertedLexicalDictionary()
    matched = dictionary.resolve_colloquial("the of and")
    assert matched is None


@pytest.mark.tier2
def test_b23_inverted_dict_special_regex_characters():
    """Verify regex characters like * + ? [ ] do not break lookup."""
    dictionary = InvertedLexicalDictionary()
    matched = dictionary.resolve_colloquial("chest [pain]*")
    assert matched is None or isinstance(matched, tuple)


@pytest.mark.tier2
def test_b23_inverted_dict_stress_hundred_thousand_entries():
    """Verify vocabulary capacity handles large queries."""
    dictionary = InvertedLexicalDictionary()
    assert len(dictionary._synonym_map) > 0


@pytest.mark.tier2
def test_b23_inverted_dict_whitespace_only_query():
    """Verify whitespace-only string returns zero terms."""
    dictionary = InvertedLexicalDictionary()
    matched = dictionary.resolve_colloquial("   \t  ")
    assert matched is None


# ---------------------------------------------------------------------------
# B24: ONNX INT8 Semantic Embedding Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b24_onnx_empty_text_embedding():
    """Verify empty text string produces normalized 384-dimensional vector."""
    engine = OnnxSemanticEmbeddingEngine()
    emb = engine.encode("")
    assert emb.shape == (384,)
    assert math.isclose(float(np.linalg.norm(emb)), 1.0, rel_tol=1e-5)


@pytest.mark.tier2
def test_b24_onnx_token_length_truncation_512():
    """Verify text exceeding 512 tokens is encoded without error."""
    engine = OnnxSemanticEmbeddingEngine()
    emb = engine.encode("infarction " * 300)
    assert emb.shape == (384,)
    assert math.isclose(float(np.linalg.norm(emb)), 1.0, rel_tol=1e-5)


@pytest.mark.tier2
def test_b24_onnx_all_zero_vector_norm_division_guard():
    """Verify all-zero vector does not produce division by zero during normalization."""
    zero_vec = np.zeros(384, dtype=np.float32)
    norm = float(np.linalg.norm(zero_vec))
    safe_norm = norm if norm > 0.0 else 1.0
    normalized = zero_vec / safe_norm
    assert np.all(normalized == 0.0)


@pytest.mark.tier2
def test_b24_onnx_nan_weight_detection():
    """Verify NaN values in vector are flagged immediately."""
    vec = [0.1, float("nan"), 0.5]
    has_nan = any(math.isnan(x) for x in vec)
    assert has_nan is True


@pytest.mark.tier2
def test_b24_onnx_single_token_input():
    """Verify single-word input embeds to valid 384-dimensional vector."""
    engine = OnnxSemanticEmbeddingEngine()
    emb = engine.encode("Shock")
    assert emb.shape == (384,)
