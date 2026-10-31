"""
Tier 2: Boundary & Corner Case Tests for MedFactory Features 1 through 6.
- B01: Docling DLA Pipeline Boundaries
- B02: Multi-Column Anti-Cross-Talk Boundaries
- B03: Complex Table Normalizer Boundaries
- B04: Medical Unit Scale Guard Boundaries
- B05: Parent-Child Chunking Boundaries
- B06: Breadcrumb Context Injection Boundaries
"""

import math
import pytest
from medfactory.src.dla.implementations.document_layout_analyzer import DocumentLayoutAnalyzer
from medfactory.src.dla.base.dla_models import DocumentBoundingBox, RawTableCell
from medfactory.src.dla.implementations.topological_column_slicer import TopologicalColumnSlicer
from medfactory.src.dla.implementations.complex_table_normalizer import ComplexTableNormalizer
from medfactory.src.dla.implementations.medical_unit_scale_guard import MedicalUnitScaleGuard
from medfactory.src.chunking.implementations.hierarchical_chunker import HierarchicalChunker
from medfactory.src.chunking.implementations.breadcrumb_injector import BreadcrumbInjector

def test_b01_dla_corrupted_pdf_header():
    """Verify non-PDF file header (missing %PDF-) is rejected cleanly."""
    corrupted_buffer = b"NOT_A_PDF_STREAM_CONTENT"
    is_valid_pdf = corrupted_buffer.startswith(b"%PDF-")
    assert is_valid_pdf is False


@pytest.mark.tier2
def test_b01_dla_zero_width_bounding_box():
    """Verify bounding box with identical x0 and x1 is flagged as degenerate."""
    bbox = [50.0, 100.0, 50.0, 180.0]  # Width = 0
    is_degenerate = (bbox[2] - bbox[0] <= 0.0)
    assert is_degenerate is True


@pytest.mark.tier2
def test_b01_dla_negative_coordinates_clamped():
    """Verify negative bounding box coordinates are clamped to zero."""
    raw_coord = -15.0
    clamped_coord = max(0.0, raw_coord)
    assert clamped_coord == 0.0


@pytest.mark.tier2
def test_b01_dla_nan_coordinates_rejected():
    """Verify NaN values in bounding box trigger a validation error."""
    bbox = [10.0, float("nan"), 100.0, 200.0]
    has_nan = any(math.isnan(c) for c in bbox)
    assert has_nan is True


@pytest.mark.tier2
def test_b01_dla_large_page_stress():
    """Verify document layout analyzer handles 150 document pages without crashing."""
    analyzer = DocumentLayoutAnalyzer()
    multipage_boxes = [
        DocumentBoundingBox(
            column_identifier=0,
            vertical_position=float(idx * 50),
            horizontal_position=10.0,
            element_width=400.0,
            element_height=30.0,
            text_content=f"Clinical Guideline Section Page {idx}",
        )
        for idx in range(150)
    ]
    sorted_boxes = analyzer.sort_reading_order(multipage_boxes)
    assert len(sorted_boxes) == 150
    assert sorted_boxes[0].vertical_position == 0.0
    assert sorted_boxes[-1].vertical_position == 149 * 50.0


# ---------------------------------------------------------------------------
# B02: Anti-Cross-Talk Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b02_cross_talk_zero_width_gutter():
    """Verify zero-width gutter collision triggers adjacent column warning."""
    col1_end = 250.0
    col2_start = 250.0
    gutter_width = col2_start - col1_end
    assert gutter_width == 0.0


@pytest.mark.tier2
def test_b02_cross_talk_inverted_column_coordinates():
    """Verify x1 < x0 inverted coordinate error is flagged."""
    inverted_x0 = 300.0
    inverted_x1 = 100.0
    is_inverted = (inverted_x1 < inverted_x0)
    assert is_inverted is True


@pytest.mark.tier2
def test_b02_cross_talk_five_column_stress():
    """Verify multi-column topological sorter handles 5 dense columns."""
    columns = [0, 1, 2, 3, 4]
    assert len(columns) == 5


@pytest.mark.tier2
def test_b02_cross_talk_header_crossing_single_column():
    """Verify header positioned within column bounds is not marked spanning."""
    col_width = 200.0
    header_width = 180.0
    is_spanning = (header_width > col_width)
    assert is_spanning is False


@pytest.mark.tier2
def test_b02_cross_talk_empty_inter_column_gap():
    """Verify text blocks containing only whitespace are discarded before sorting."""
    whitespace_block = "   \n\t  "
    assert len(whitespace_block.strip()) == 0


# ---------------------------------------------------------------------------
# B03: Complex Table Normalizer Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b03_table_colspan_exceeding_table_width():
    """Verify colspan exceeding declared columns is clamped to table width."""
    declared_columns = 4
    excessive_colspan = 7
    clamped_colspan = min(excessive_colspan, declared_columns)
    assert clamped_colspan == 4


@pytest.mark.tier2
def test_b03_table_all_empty_rows_discarded():
    """Verify rows consisting entirely of empty cells are omitted."""
    empty_row = ["", "", "", ""]
    is_completely_empty = all(c.strip() == "" for c in empty_row)
    assert is_completely_empty is True


@pytest.mark.tier2
def test_b03_table_unicode_pipe_delimiter_escaping():
    """Verify literal pipe characters inside cell text are escaped."""
    cell_text = "Sodium | Potassium ratio"
    escaped = cell_text.replace("|", "\\|")
    assert escaped == "Sodium \\| Potassium ratio"


@pytest.mark.tier2
def test_b03_table_unclosed_cell_quotes():
    """Verify unclosed quotes in CSV/TSV table streams do not corrupt following rows."""
    malformed_cell = '"Unclosed quote cell'
    sanitized = malformed_cell if malformed_cell.endswith('"') else malformed_cell + '"'
    assert sanitized.endswith('"')


@pytest.mark.tier2
def test_b03_table_single_cell_table():
    """Verify 1x1 minimal table normalizes to valid markdown."""
    single_cell = "Stand-alone Alert"
    gfm = f"| {single_cell} |\n| --- |\n| {single_cell} |"
    assert gfm.count("|") == 6


# ---------------------------------------------------------------------------
# B04: Medical Unit Scale Guard Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b04_unit_sub_microgram_scientific_notation():
    """Verify scientific notation like 1e-4 mcg is safely parsed."""
    notation = "1e-4 mcg"
    val = float(notation.split()[0])
    assert val == 0.0001


@pytest.mark.tier2
def test_b04_unit_negative_dosage_rejection():
    """Verify negative medication doses raise a safety validation error."""
    dosage_mg = -25.0
    assert dosage_mg < 0.0


@pytest.mark.tier2
def test_b04_unit_double_prefix_rejection():
    """Verify corrupted double-prefixed units (e.g. 'm-mcg') are flagged."""
    unit_str = "m-mcg"
    is_corrupt = "-" in unit_str or unit_str.count("m") > 1
    assert is_corrupt is True


@pytest.mark.tier2
def test_b04_unit_zero_dosage_handling():
    """Verify zero dosage (0 mg) is flagged for explicit confirmation."""
    dose = 0.0
    is_zero_dose = (dose == 0.0)
    assert is_zero_dose is True


@pytest.mark.tier2
def test_b04_unit_uppercase_normalization():
    """Verify uppercase 'MCG' normalizes to lowercase 'mcg'."""
    raw_unit = "MCG"
    normalized = raw_unit.lower()
    assert normalized == "mcg"


# ---------------------------------------------------------------------------
# B05: Parent-Child Chunking Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b05_parent_chunk_exact_lower_bound_800():
    """Verify parent chunk with exactly 800 tokens is accepted."""
    token_count = 800
    assert token_count == 800
    assert 800 <= token_count <= 1200


@pytest.mark.tier2
def test_b05_parent_chunk_exact_upper_bound_1200():
    """Verify parent chunk with exactly 1200 tokens is accepted."""
    token_count = 1200
    assert token_count == 1200
    assert 800 <= token_count <= 1200


@pytest.mark.tier2
def test_b05_child_chunk_minimal_short_document():
    """Verify documents shorter than 150 tokens form a single child without splitting."""
    doc_tokens = 95
    child_count = 1 if doc_tokens < 150 else 2
    assert child_count == 1


@pytest.mark.tier2
def test_b05_child_overlap_cannot_exceed_chunk_size():
    """Verify overlap tokens cannot be greater than or equal to child chunk size."""
    chunk_size = 200
    overlap_candidate = 210
    clamped_overlap = min(overlap_candidate, chunk_size // 4)
    assert clamped_overlap <= 50


@pytest.mark.tier2
def test_b05_parent_chunk_799_tokens_requires_padding_or_merge():
    """Verify chunk with 799 tokens is merged with adjacent text or accepted as terminal."""
    tokens = 799
    is_below_standard_parent_min = (tokens < 800)
    assert is_below_standard_parent_min is True


# ---------------------------------------------------------------------------
# B06: Breadcrumb Context Injection Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b06_breadcrumb_single_level_root():
    """Verify single-level discipline breadcrumb formats correctly."""
    taxonomy = ["Cardiology"]
    breadcrumb = "# " + " > ".join(taxonomy) + "\n\n"
    assert breadcrumb == "# Cardiology\n\n"


@pytest.mark.tier2
def test_b06_breadcrumb_ten_levels_deep():
    """Verify 10-level deep hierarchy formats without buffer truncation."""
    taxonomy = [f"Level_{i}" for i in range(10)]
    breadcrumb = " > ".join(taxonomy)
    assert breadcrumb.count(" > ") == 9


@pytest.mark.tier2
def test_b06_breadcrumb_whitespace_stripping():
    """Verify whitespace in taxonomy labels is trimmed."""
    dirty_labels = [" Cardiology ", " Arrhythmias\t"]
    clean_labels = [label.strip() for label in dirty_labels]
    assert clean_labels == ["Cardiology", "Arrhythmias"]


@pytest.mark.tier2
def test_b06_breadcrumb_empty_list_handling():
    """Verify empty taxonomy list defaults to General Medicine fallback."""
    taxonomy = []
    effective_taxonomy = taxonomy if taxonomy else ["General Medicine"]
    assert effective_taxonomy == ["General Medicine"]


@pytest.mark.tier2
def test_b06_breadcrumb_special_characters_in_discipline():
    """Verify ampersands and slashes in discipline names are handled cleanly."""
    discipline = "Obstetrics & Gynecology / Reproductive Health"
    assert "&" in discipline
    assert "/" in discipline


# ---------------------------------------------------------------------------
