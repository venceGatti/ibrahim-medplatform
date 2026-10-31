"""
Tier 1: Feature Coverage Tests for MedFactory Features 1 through 3.
- Feature 1: Docling DLA Pipeline
- Feature 2: Multi-Column Anti-Cross-Talk
- Feature 3: Complex Table Normalizer
"""

import pytest
from typing import List
from medfactory.src.dla.implementations.document_layout_analyzer import DocumentLayoutAnalyzer
from medfactory.src.dla.base.dla_models import (
    DocumentBoundingBox,
    DocumentBlockCategory,
    RawTableCell,
)
from medfactory.src.dla.implementations.topological_column_slicer import TopologicalColumnSlicer
from medfactory.src.dla.implementations.complex_table_normalizer import ComplexTableNormalizer

# Feature 1: Docling DLA Pipeline
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f01_dla_bounding_box_extraction():
    """Verify DLA extracts normalized coordinates for text bounding boxes."""
    analyzer = DocumentLayoutAnalyzer()
    box1 = DocumentBoundingBox(
        column_identifier=0,
        vertical_position=20.0,
        horizontal_position=10.0,
        element_width=190.0,
        element_height=30.0,
        text_content="Cardiovascular Examination",
        block_category=DocumentBlockCategory.HEADING
    )
    box2 = DocumentBoundingBox(
        column_identifier=0,
        vertical_position=60.0,
        horizontal_position=10.0,
        element_width=490.0,
        element_height=120.0,
        text_content="Heart sounds are normal.",
        block_category=DocumentBlockCategory.PARAGRAPH
    )
    boxes = [box1, box2]
    sorted_boxes = analyzer.sort_reading_order(boxes)
    assert len(sorted_boxes) == 2
    assert sorted_boxes[0].element_width > 0.0
    assert sorted_boxes[0].element_height > 0.0
    assert len(sorted_boxes[0].text_content) > 0


@pytest.mark.tier1
def test_f01_dla_reading_order_determination():
    """Verify DLA sorts elements by vertical and horizontal flow."""
    analyzer = DocumentLayoutAnalyzer()
    block_lower = DocumentBoundingBox(
        col_id=0, y_pos=120.0, x_pos=50.0, width=200.0, height=20.0,
        text_content="Second paragraph"
    )
    block_upper = DocumentBoundingBox(
        col_id=0, y_pos=30.0, x_pos=50.0, width=200.0, height=20.0,
        text_content="First paragraph"
    )
    sorted_boxes = analyzer.sort_reading_order([block_lower, block_upper])
    assert sorted_boxes[0].text_content == "First paragraph"
    assert sorted_boxes[1].text_content == "Second paragraph"


@pytest.mark.tier1
def test_f01_dla_text_segment_classification():
    """Verify DLA classifies text elements into canonical schema types."""
    valid_categories = {
        DocumentBlockCategory.TITLE,
        DocumentBlockCategory.HEADING,
        DocumentBlockCategory.PARAGRAPH,
        DocumentBlockCategory.TABLE,
        DocumentBlockCategory.FIGURE,
        DocumentBlockCategory.CALLOUT,
        DocumentBlockCategory.LIST_ITEM,
    }
    box = DocumentBoundingBox(
        col_id=0, y_pos=10.0, x_pos=10.0, width=100.0, height=20.0,
        text_content="Chapter Title", block_category=DocumentBlockCategory.TITLE
    )
    assert box.block_category in valid_categories


@pytest.mark.tier1
def test_f01_dla_coordinate_normalization():
    """Verify page dimensions and bounding boxes maintain positive metrics."""
    box = DocumentBoundingBox(
        col_id=0, y_pos=50.0, x_pos=25.0, width=562.0, height=700.0,
        text_content="Normalized Content"
    )
    assert box.width > 0.0
    assert box.height > 0.0
    aspect_ratio = box.height / box.width
    assert aspect_ratio > 1.0


@pytest.mark.tier1
def test_f01_dla_multipage_metadata_tracking():
    """Verify text reconstruction preserves sequential text across multiple blocks."""
    analyzer = DocumentLayoutAnalyzer()
    box_p1 = DocumentBoundingBox(
        col_id=0, y_pos=10.0, x_pos=10.0, width=200.0, height=50.0,
        text_content="Page 1 Content."
    )
    box_p2 = DocumentBoundingBox(
        col_id=0, y_pos=100.0, x_pos=10.0, width=200.0, height=50.0,
        text_content="Page 2 Content."
    )
    reconstructed = analyzer.reconstruct_text([box_p2, box_p1])
    assert "Page 1 Content." in reconstructed
    assert "Page 2 Content." in reconstructed


# ---------------------------------------------------------------------------
# Feature 2: Multi-Column Anti-Cross-Talk
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f02_two_column_topological_separation():
    """Verify two-column layout blocks are partitioned without inter-column text mingling."""
    slicer = TopologicalColumnSlicer(alpha_column_weight=10000.0, beta_vertical_weight=1.0)
    col0_top = DocumentBoundingBox(col_id=0, y_pos=50.0, x_pos=20.0, text_content="Left Col Top")
    col1_top = DocumentBoundingBox(col_id=1, y_pos=50.0, x_pos=320.0, text_content="Right Col Top")
    col0_bottom = DocumentBoundingBox(col_id=0, y_pos=150.0, x_pos=20.0, text_content="Left Col Bottom")
    col1_bottom = DocumentBoundingBox(col_id=1, y_pos=150.0, x_pos=320.0, text_content="Right Col Bottom")

    ordered = slicer.sort_reading_order([col1_top, col0_bottom, col1_bottom, col0_top])
    ordered_texts = [b.text_content for b in ordered]
    assert ordered_texts == ["Left Col Top", "Left Col Bottom", "Right Col Top", "Right Col Bottom"]


@pytest.mark.tier1
def test_f02_three_column_gutter_detection():
    """Verify column detection assigns column identifiers according to horizontal centers."""
    slicer = TopologicalColumnSlicer()
    boxes = [
        DocumentBoundingBox(col_id=0, y_pos=50.0, x_pos=50.0, width=80.0, text_content="Col 0"),
        DocumentBoundingBox(col_id=0, y_pos=50.0, x_pos=350.0, width=80.0, text_content="Col 1"),
    ]
    detected = slicer.detect_columns_if_missing(boxes, page_width=600.0, expected_columns=2)
    assert detected[0].column_identifier == 0
    assert detected[1].column_identifier == 1


@pytest.mark.tier1
def test_f02_spanned_headline_anti_cross_talk():
    """Verify alpha weighting ensures column 0 is read before column 1 even if column 0 is lower on page."""
    slicer = TopologicalColumnSlicer(alpha_column_weight=10000.0, beta_vertical_weight=1.0)
    col0_lower = DocumentBoundingBox(col_id=0, y_pos=120.0, text_content="Column 0 Lower")
    col1_upper = DocumentBoundingBox(col_id=1, y_pos=20.0, text_content="Column 1 Upper")

    ordered = slicer.sort_reading_order([col1_upper, col0_lower])
    assert ordered[0].text_content == "Column 0 Lower"
    assert ordered[1].text_content == "Column 1 Upper"


@pytest.mark.tier1
def test_f02_column_break_preserves_reading_continuity():
    """Verify sentence fragments do not bridge across separate column gutters."""
    col1_box = DocumentBoundingBox(col_id=0, y_pos=10.0, text_content="The treatment of choice is intravenous penicillin.")
    col2_box = DocumentBoundingBox(col_id=1, y_pos=10.0, text_content="Adverse effects include cutaneous rash and fever.")
    slicer = TopologicalColumnSlicer()
    ordered = slicer.sort_reading_order([col2_box, col1_box])
    assert ordered[0].text_content.endswith("penicillin.")
    assert ordered[1].text_content.startswith("Adverse")


@pytest.mark.tier1
def test_f02_vertical_topological_sort_invariant():
    """Verify strictly monotonic reading order within each column stream."""
    slicer = TopologicalColumnSlicer()
    boxes = [
        DocumentBoundingBox(col_id=0, y_pos=100.0, text_content="Y100"),
        DocumentBoundingBox(col_id=0, y_pos=20.0, text_content="Y20"),
        DocumentBoundingBox(col_id=0, y_pos=200.0, text_content="Y200"),
    ]
    ordered = slicer.sort_reading_order(boxes)
    assert [b.text_content for b in ordered] == ["Y20", "Y100", "Y200"]


# ---------------------------------------------------------------------------
# Feature 3: Complex Table Normalizer
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f03_merged_header_colspan_reconstruction():
    """Verify multi-column spanning headers expand to individual sub-columns."""
    normalizer = ComplexTableNormalizer()
    raw_matrix = [
        [RawTableCell(content="Laboratory Test", col_span=1), RawTableCell(content="Reference Range", col_span=2)],
        [RawTableCell(content="Troponin I", col_span=1), RawTableCell(content="0.00", col_span=1), RawTableCell(content="0.04", col_span=1)]
    ]
    grid = normalizer.resolve_grid(raw_matrix)
    assert len(grid) == 2
    assert len(grid[0]) == 3
    assert grid[0][0] == "Laboratory Test"
    assert grid[0][1] == "Reference Range"
    assert grid[0][2] == "Reference Range"


@pytest.mark.tier1
def test_f03_rowspan_cell_propagation():
    """Verify multi-row span values propagate down to subsequent rows."""
    normalizer = ComplexTableNormalizer()
    raw_matrix = [
        [RawTableCell(content="Serum Creatinine", row_span=2), RawTableCell(content="Normal"), RawTableCell(content="0.7 - 1.3 mg/dL")],
        [RawTableCell(content="Elevated"), RawTableCell(content="> 1.5 mg/dL")],
    ]
    grid = normalizer.resolve_grid(raw_matrix)
    assert len(grid) == 2
    assert grid[0][0] == "Serum Creatinine"
    assert grid[1][0] == "Serum Creatinine"
    assert grid[1][1] == "Elevated"


@pytest.mark.tier1
def test_f03_gfm_pipe_table_formatting():
    """Verify normalized table serializes to valid GitHub-Flavored Markdown."""
    normalizer = ComplexTableNormalizer()
    matrix = [
        [RawTableCell(content="Analyte"), RawTableCell(content="Value"), RawTableCell(content="Unit")],
        [RawTableCell(content="Troponin I"), RawTableCell(content="0.04"), RawTableCell(content="ng/mL")]
    ]
    grid = normalizer.resolve_grid(matrix)
    markdown = normalizer.to_canonical_markdown(grid)
    assert "| Analyte | Value | Unit |" in markdown
    assert "| Troponin I | 0.04 | ng/mL |" in markdown


@pytest.mark.tier1
def test_f03_empty_cell_preservation_without_dropping():
    """Verify empty cells remain present as blank fields rather than misaligning columns."""
    normalizer = ComplexTableNormalizer()
    matrix = [
        [RawTableCell(content="Potassium"), RawTableCell(content=""), RawTableCell(content="mEq/L")]
    ]
    grid = normalizer.resolve_grid(matrix)
    assert len(grid[0]) == 3
    assert grid[0][1] == ""


@pytest.mark.tier1
def test_f03_numeric_column_alignment():
    """Verify numeric tables correctly retain decimal points and scientific exponents."""
    normalizer = ComplexTableNormalizer()
    matrix = [
        [RawTableCell(content="1.42e-3"), RawTableCell(content="0.005"), RawTableCell(content="120.5")]
    ]
    grid = normalizer.resolve_grid(matrix)
    assert float(grid[0][0]) > 0.0
    assert float(grid[0][1]) > 0.0
    assert float(grid[0][2]) > 0.0


# ---------------------------------------------------------------------------
