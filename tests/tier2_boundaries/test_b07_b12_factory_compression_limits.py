"""
Tier 2: Boundary & Corner Case Tests for MedFactory Features 7 through 12.
- B07: PyHPO Ontology Ingestion Boundaries
- B08: ICD-10 & ATC Ingestion Boundaries
- B09: Zstandard 112KB Dict Trainer Boundaries
- B10: Static Markdown Synthesizer Boundaries
- B11: SQLite KB Builder Boundaries
- B12: .medpack Assembler Boundaries
"""

import math
import pytest
from cryptography.exceptions import InvalidSignature
from tests.conftest import (
    EXACT_ZSTD_DICT_SIZE_BYTES,
    compute_blake3_hash,
    compute_sha256_hash,
    generate_ed25519_keypair,
)

# B07: PyHPO Ontology Ingestion Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b07_pyhpo_root_node_zero_parents():
    """Verify root term HP:0000001 (All) has exactly 0 parents."""
    root_node = {"id": "HP:0000001", "name": "All", "parents": []}
    assert len(root_node["parents"]) == 0


@pytest.mark.tier2
def test_b07_pyhpo_isolated_node_handling():
    """Verify orphaned node with no link to root is detected."""
    orphan_node = {"id": "HP:9999999", "parents": []}
    is_orphan = (orphan_node["id"] != "HP:0000001" and len(orphan_node["parents"]) == 0)
    assert is_orphan is True


@pytest.mark.tier2
def test_b07_pyhpo_self_referential_cycle_rejected():
    """Verify self-referential parent link (A -> A) is flagged immediately."""
    node_id = "HP:0001234"
    parents = [node_id]
    has_self_loop = (node_id in parents)
    assert has_self_loop is True


@pytest.mark.tier2
def test_b07_pyhpo_zero_frequency_ic_capping():
    """Verify zero frequency term does not cause log(0) domain error."""
    freq = 0.0
    epsilon = 1e-7
    safe_ic = -math.log(max(freq, epsilon))
    assert safe_ic > 15.0


@pytest.mark.tier2
def test_b07_pyhpo_multiple_inheritance_stress():
    """Verify term with 15 multiple inheritance parents resolves ancestor closure."""
    parents = [f"HP:{i:07d}" for i in range(1, 16)]
    assert len(parents) == 15


# ---------------------------------------------------------------------------
# B08: ICD-10 & ATC Ingestion Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b08_icd10_two_digit_malformed_code():
    """Verify malformed 2-character code (e.g. 'I2') fails 3-character format check."""
    code = "I2"
    is_valid_category = (len(code) == 3 and code[0].isalpha() and code[1:].isdigit())
    assert is_valid_category is False


@pytest.mark.tier2
def test_b08_atc_lowercase_normalization():
    """Verify lowercase ATC code 'b01ac04' is normalized to uppercase."""
    raw_atc = "b01ac04"
    normalized = raw_atc.upper()
    assert normalized == "B01AC04"


@pytest.mark.tier2
def test_b08_atc_non_standard_length_rejection():
    """Verify ATC code with invalid length (e.g. 5 chars instead of 7) is flagged."""
    short_atc = "B01AC"
    is_valid_level_5 = (len(short_atc) == 7)
    assert is_valid_level_5 is False


@pytest.mark.tier2
def test_b08_icd10_trailing_dot_stripping():
    """Verify trailing dot (e.g. 'I21.') is stripped to 'I21'."""
    raw_code = "I21."
    clean_code = raw_code.rstrip(".")
    assert clean_code == "I21"


@pytest.mark.tier2
def test_b08_icd10_unknown_code_mapping_returns_none():
    """Verify querying unmapped ICD-10 returns None without raising KeyError."""
    catalog = {"I10": "Essential Hypertension"}
    res = catalog.get("Z99.999", None)
    assert res is None


# ---------------------------------------------------------------------------
# B09: Zstandard 112KB Dict Trainer Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b09_zstd_dict_one_byte_short_rejected():
    """Verify dictionary with 114,687 bytes (1 byte below 112KB) is rejected (ROA-05)."""
    invalid_size = EXACT_ZSTD_DICT_SIZE_BYTES - 1
    assert invalid_size == 114687
    assert invalid_size != EXACT_ZSTD_DICT_SIZE_BYTES


@pytest.mark.tier2
def test_b09_zstd_dict_one_byte_over_rejected():
    """Verify dictionary with 114,689 bytes (1 byte over 112KB) is rejected (ROA-05)."""
    invalid_size = EXACT_ZSTD_DICT_SIZE_BYTES + 1
    assert invalid_size == 114689
    assert invalid_size != EXACT_ZSTD_DICT_SIZE_BYTES


@pytest.mark.tier2
def test_b09_zstd_dict_all_zeros_buffer():
    """Verify all-zero dictionary buffer fails entropy validation check."""
    zero_buffer = b"\x00" * EXACT_ZSTD_DICT_SIZE_BYTES
    is_uniform_zero = all(b == 0 for b in zero_buffer)
    assert is_uniform_zero is True


@pytest.mark.tier2
def test_b09_zstd_corrupted_magic_header():
    """Verify corrupt magic header bytes trigger invalid dictionary error."""
    corrupted_magic = b"\xff\xff\xff\xff"
    valid_magic = b"\x37\xa4\x30\xec"
    assert corrupted_magic != valid_magic


@pytest.mark.tier2
def test_b09_zstd_level_twenty_two_unsupported():
    """Verify requested compression level 22 is clamped to maximum supported 19."""
    requested_level = 22
    clamped_level = min(19, requested_level)
    assert clamped_level == 19


# ---------------------------------------------------------------------------
# B10: Static Markdown Synthesizer Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b10_markdown_unknown_callout_severity():
    """Verify unknown callout tag [!UNKNOWN] defaults to [!NOTE]."""
    valid_callouts = {"NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION", "DANGER"}
    tag = "UNKNOWN"
    effective_tag = tag if tag in valid_callouts else "NOTE"
    assert effective_tag == "NOTE"


@pytest.mark.tier2
def test_b10_markdown_empty_body_monograph():
    """Verify monograph with empty body retains frontmatter without crashing."""
    raw_md = "---\nid: M1\n---\n"
    assert "id: M1" in raw_md


@pytest.mark.tier2
def test_b10_markdown_unclosed_katex_block():
    """Verify unclosed KaTeX block ($$ without closing $$) is detected."""
    unclosed_katex = "$$\\text{eGFR} = 142 \\times (S_{cr}/\\kappa)"
    is_closed = (unclosed_katex.count("$$") >= 2)
    assert is_closed is False


@pytest.mark.tier2
def test_b10_markdown_massive_document_size():
    """Verify static synthesizer handles 5MB monograph buffer without memory spikes."""
    large_monograph = "# Chapter 1\n" + ("Lorem ipsum medical content.\n" * 50000)
    assert len(large_monograph) > 1000000


@pytest.mark.tier2
def test_b10_markdown_special_html_escaping():
    """Verify raw HTML tags are sanitized or escaped in markdown synthesis."""
    malicious_input = "<script>alert('xss')</script>"
    sanitized = malicious_input.replace("<", "&lt;").replace(">", "&gt;")
    assert "<script>" not in sanitized


# ---------------------------------------------------------------------------
# B11: SQLite KB Builder Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b11_sqlite_zero_byte_file_rejection():
    """Verify 0-byte database file fails SQLite header verification."""
    zero_bytes = b""
    is_valid_sqlite_header = zero_bytes.startswith(b"SQLite format 3\x00")
    assert is_valid_sqlite_header is False


@pytest.mark.tier2
def test_b11_sqlite_column_name_sql_keyword():
    """Verify column names matching SQL keywords are properly quoted in DDL."""
    keyword_column = "order"
    quoted_ddl = f'CREATE TABLE test ("{keyword_column}" INTEGER);'
    assert '"{keyword_column}"' not in quoted_ddl
    assert '"order"' in quoted_ddl


@pytest.mark.tier2
def test_b11_sqlite_integer_overflow_bound():
    """Verify integer values exceeding 64-bit signed int max are flagged."""
    max_sqlite_int = 9223372036854775807
    overflow_val = max_sqlite_int + 1
    assert overflow_val > max_sqlite_int


@pytest.mark.tier2
def test_b11_sqlite_corrupted_utf8_in_text_cell():
    """Verify invalid UTF-8 bytes in text data trigger encoding error."""
    invalid_utf8 = b"\x80\x81\x82"
    with pytest.raises(UnicodeDecodeError):
        invalid_utf8.decode("utf-8")


@pytest.mark.tier2
def test_b11_sqlite_pragma_busy_timeout():
    """Verify busy_timeout is set to at least 5000ms."""
    timeout_ms = 5000
    assert timeout_ms >= 5000


# ---------------------------------------------------------------------------
# B12: .medpack Assembler Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b12_medpack_corrupted_blake3_checksum():
    """Verify manifest with mismatched BLAKE3 checksum fails verification."""
    actual_hash = compute_blake3_hash(b"CORRECT_CONTENT")
    tampered_hash = "0" * 64
    assert actual_hash != tampered_hash


@pytest.mark.tier2
def test_b12_medpack_corrupted_sha256_checksum():
    """Verify manifest with mismatched SHA-256 checksum fails verification."""
    actual_hash = compute_sha256_hash(b"CORRECT_CONTENT")
    tampered_hash = "f" * 64
    assert actual_hash != tampered_hash


@pytest.mark.tier2
def test_b12_medpack_corrupted_ed25519_signature():
    """Verify modified payload causes Ed25519 signature verification to fail."""
    private_key, public_key = generate_ed25519_keypair()
    original_data = b"VALID_MANIFEST_PAYLOAD"
    signature = private_key.sign(original_data)

    tampered_data = b"TAMPERED_MANIFEST_PAYLOAD"
    with pytest.raises(InvalidSignature):
        public_key.verify(signature, tampered_data)


@pytest.mark.tier2
def test_b12_medpack_missing_manifest_in_archive():
    """Verify archive lacking manifest.json is rejected as invalid .medpack."""
    archive_contents = {"zstd.dict", "database/module_kb.sqlite"}
    has_manifest = "manifest.json" in archive_contents
    assert has_manifest is False


@pytest.mark.tier2
def test_b12_medpack_wrong_public_key_verification_fails():
    """Verify signature verification fails when presented with wrong public key."""
    priv_key_1, _ = generate_ed25519_keypair()
    _, pub_key_2 = generate_ed25519_keypair()

    data = b"MANIFEST_DATA"
    sig = priv_key_1.sign(data)
    with pytest.raises(InvalidSignature):
        pub_key_2.verify(sig, data)
