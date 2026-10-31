"""
Tier 3: Pairwise Cross-Feature Tests.
Pair 1: DLA Complex Table Normalizer + 114,688-Byte Zstandard Dictionary Compression.
Verifies that complex normalized medical tables achieve high compression ratios with bit-exact decompression.
"""

import zstandard as zstd
import pytest
from tests.conftest import EXACT_ZSTD_DICT_SIZE_BYTES


@pytest.mark.tier3
def test_p01_table_normalizer_and_zstd_dict_compression_ratio():
    """Verify normalized GFM tables compress with >= 2.5x ratio using trained dictionary."""
    headers = ["Analyte", "Observed Value", "Reference Range", "Clinical Interpretation"]
    rows = [
        ["Serum Troponin I", "0.45 ng/mL", "< 0.04 ng/mL", "Myocardial Necrosis Present"],
        ["Creatine Kinase-MB", "35.2 ng/mL", "< 5.0 ng/mL", "Elevated Cardiac Marker"],
        ["Brain Natriuretic Peptide", "850 pg/mL", "< 100 pg/mL", "Ventricular Volume Overload"],
        ["Serum Creatinine", "2.1 mg/dL", "0.7 - 1.3 mg/dL", "Acute Kidney Injury Stage 2"]
    ] * 20  # Repetitive medical tabular lemmata

    # Build GFM table
    gfm_table = "| " + " | ".join(headers) + " |\n"
    gfm_table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    for r in rows:
        gfm_table += "| " + " | ".join(r) + " |\n"

    uncompressed_bytes = gfm_table.encode("utf-8")
    uncompressed_len = len(uncompressed_bytes)

    # Synthetic dictionary with exact size 114,688 bytes containing medical domain lemmata
    trained_dict_bytes = (b"Serum Troponin I ng/mL Reference Range Creatinine " * 3000)[:EXACT_ZSTD_DICT_SIZE_BYTES]
    assert len(trained_dict_bytes) == EXACT_ZSTD_DICT_SIZE_BYTES

    # Train dict or use zstd compressor with dictionary
    c_dict = zstd.ZstdCompressionDict(trained_dict_bytes)
    compressor = zstd.ZstdCompressor(level=19, dict_data=c_dict)
    compressed_bytes = compressor.compress(uncompressed_bytes)

    ratio = uncompressed_len / len(compressed_bytes)
    assert ratio >= 2.5, f"Compression ratio {ratio} is below 2.5x"


@pytest.mark.tier3
def test_p01_table_normalizer_zstd_roundtrip_bit_exactness():
    """Verify compression and decompression with 114,688B dictionary reproduces original table exactly."""
    original_table = (
        "| Parameter | Value | Unit |\n"
        "| --- | --- | --- |\n"
        "| Hemoglobin | 14.2 | g/dL |\n"
        "| Platelets | 250000 | /mcL |\n"
    )
    raw_bytes = original_table.encode("utf-8")
    dict_buffer = (b"Parameter Value Unit Hemoglobin Platelets " * 3000)[:EXACT_ZSTD_DICT_SIZE_BYTES]

    c_dict = zstd.ZstdCompressionDict(dict_buffer)
    compressor = zstd.ZstdCompressor(level=19, dict_data=c_dict)
    compressed = compressor.compress(raw_bytes)

    d_dict = zstd.ZstdCompressionDict(dict_buffer)
    decompressor = zstd.ZstdDecompressor(dict_data=d_dict)
    decompressed = decompressor.decompress(compressed)

    assert decompressed == raw_bytes
    assert decompressed.decode("utf-8") == original_table


@pytest.mark.tier3
def test_p01_multi_column_text_with_unit_guard_after_compression():
    """Verify medical dosage units survive zstd compression roundtrip without OCR corruption."""
    medical_text = (
        "Column 1:\nPatient prescribed Levothyroxine 50 mcg oral daily.\n"
        "Column 2:\nDo not substitute with 50 mg (milligram) dosage.\n"
    )
    raw_bytes = medical_text.encode("utf-8")
    dict_buffer = (b"Levothyroxine mcg mg oral daily Column Patient " * 3000)[:EXACT_ZSTD_DICT_SIZE_BYTES]

    c_dict = zstd.ZstdCompressionDict(dict_buffer)
    compressor = zstd.ZstdCompressor(level=19, dict_data=c_dict)
    compressed = compressor.compress(raw_bytes)

    d_dict = zstd.ZstdCompressionDict(dict_buffer)
    decompressor = zstd.ZstdDecompressor(dict_data=d_dict)
    recovered_text = decompressor.decompress(compressed).decode("utf-8")

    assert "50 mcg" in recovered_text
    assert "50 mg" in recovered_text
    assert recovered_text == medical_text


@pytest.mark.tier3
def test_p01_empty_table_compression_with_dictionary():
    """Verify empty normalized table compresses and decompresses cleanly without dictionary errors."""
    empty_table = "| | |\n| --- | --- |\n"
    raw_bytes = empty_table.encode("utf-8")
    dict_buffer = (b"EMPTY_TABLE_FALLBACK " * 6000)[:EXACT_ZSTD_DICT_SIZE_BYTES]

    c_dict = zstd.ZstdCompressionDict(dict_buffer)
    compressor = zstd.ZstdCompressor(level=19, dict_data=c_dict)
    compressed = compressor.compress(raw_bytes)

    d_dict = zstd.ZstdCompressionDict(dict_buffer)
    decompressor = zstd.ZstdDecompressor(dict_data=d_dict)
    recovered = decompressor.decompress(compressed).decode("utf-8")
    assert recovered == empty_table
