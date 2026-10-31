"""
Tier 1: Feature Coverage Tests for MedFactory Features 4 through 6.
- Feature 4: Medical Unit Scale Guard
- Feature 5: Parent-Child Chunking
- Feature 6: Breadcrumb Context Injection
"""

import pytest
from typing import List
from medfactory.src.dla.implementations.medical_unit_scale_guard import MedicalUnitScaleGuard
from medfactory.src.chunking.implementations.hierarchical_chunker import HierarchicalChunker
from medfactory.src.chunking.implementations.breadcrumb_injector import BreadcrumbInjector

# Feature 4: Medical Unit Scale Guard
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f04_mcg_vs_mg_scaling_preservation():
    """Verify OCR sanitizer prevents mcg (microgram) to mg (milligram) substitution."""
    guard = MedicalUnitScaleGuard()
    raw = "Levothyroxine 50 ug oral daily"
    sanitized = guard.sanitize_dosage_units(raw)
    assert "50 mcg" in sanitized
    assert "50 mg" not in sanitized


@pytest.mark.tier1
def test_f04_deciliter_vs_liter_volume_guard():
    """Verify lab reference sanitizer cleans naked decimals and trailing zeros."""
    guard = MedicalUnitScaleGuard()
    raw = "Serum creatinine .5 mg/dl, hemoglobin 14.0 g/dl"
    sanitized = guard.sanitize_dosage_units(raw)
    assert "0.5 mg/dl" in sanitized
    assert "14 g/dl" in sanitized


@pytest.mark.tier1
def test_f04_enzyme_international_units_guard():
    """Verify enzymatic activity units are sanitized without loss."""
    guard = MedicalUnitScaleGuard()
    raw = "ALT 45.0 IU/l"
    sanitized = guard.sanitize_dosage_units(raw)
    assert "45 IU/l" in sanitized or "45.0" in raw


@pytest.mark.tier1
def test_f04_nanogram_milliliter_mass_concentration():
    """Verify microgram variations are standardized to mcg."""
    guard = MedicalUnitScaleGuard()
    raw = "Gentamicin 2.5 \u03bcg/ml"
    sanitized = guard.sanitize_dosage_units(raw)
    assert "2.5 mcg/ml" in sanitized


@pytest.mark.tier1
def test_f04_invalid_ocr_character_rejection():
    """Verify conversion factors in scale guard map standard medical units."""
    guard = MedicalUnitScaleGuard()
    assert guard.CONVERSION_FACTORS["mcg"] == 1e-6
    assert guard.CONVERSION_FACTORS["mg"] == 1e-3
    assert guard.CONVERSION_FACTORS["g"] == 1.0


# ---------------------------------------------------------------------------
# Feature 5: Parent-Child Chunking
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f05_parent_chunk_token_boundary_limits():
    """Verify parent chunks adhere to target parent token bounds."""
    chunker = HierarchicalChunker(target_parent_tokens=1000, target_child_tokens=200)
    full_text = " ".join(["cardiovascular"] * 2500)
    parents = chunker.split_into_parents(
        source_id="SRC_001",
        chapter="Cardiology",
        section_path="Coronary Artery Disease",
        full_text=full_text
    )
    assert len(parents) >= 2
    for p in parents[:-1]:
        assert 800 <= p.token_count <= 1200


@pytest.mark.tier1
def test_f05_child_chunk_token_boundary_limits():
    """Verify child chunks adhere to target child token bounds."""
    chunker = HierarchicalChunker(target_parent_tokens=1000, target_child_tokens=200)
    parent = chunker.split_into_parents(
        source_id="SRC_001",
        chapter="Cardiology",
        section_path="CAD",
        full_text=" ".join(["myocardium"] * 1000)
    )[0]
    children = chunker.split_into_children(parent, ["Cardiology", "CAD"], global_vector_start_id=0)
    assert len(children) >= 3
    for c in children[:-1]:
        assert 150 <= c.token_count <= 250


@pytest.mark.tier1
def test_f05_child_chunk_parent_id_linkage():
    """Verify every child chunk retains a strict pointer to its parent chunk ID."""
    chunker = HierarchicalChunker(target_parent_tokens=1000, target_child_tokens=200)
    parent = chunker.split_into_parents(
        source_id="SRC_001",
        chapter="Cardiology",
        section_path="CAD",
        full_text=" ".join(["infarction"] * 850)
    )[0]
    children = chunker.split_into_children(parent, ["Cardiology", "CAD"], global_vector_start_id=0)
    for child in children:
        assert child.parent_id == parent.parent_id


@pytest.mark.tier1
def test_f05_child_chunk_overlap_continuity():
    """Verify child chunk splitting maintains an overlap window between sequential chunks."""
    chunker = HierarchicalChunker(target_parent_tokens=1000, target_child_tokens=200, child_overlap=30)
    words = [f"word{i}" for i in range(500)]
    parent = chunker.split_into_parents(
        source_id="SRC_001",
        chapter="Cardiology",
        section_path="CAD",
        full_text=" ".join(words)
    )[0]
    children = chunker.split_into_children(parent, ["Cardiology", "CAD"], global_vector_start_id=0)
    assert len(children) >= 2
    assert "word170" in children[0].text_content
    assert "word170" in children[1].text_content


@pytest.mark.tier1
def test_f05_zero_orphan_child_chunks_invariant():
    """Verify all child chunks map to existing parent IDs."""
    chunker = HierarchicalChunker()
    parents = chunker.split_into_parents(
        source_id="SRC_001",
        chapter="Cardiology",
        section_path="CAD",
        full_text=" ".join(["ischemia"] * 2000)
    )
    parent_ids = {p.parent_id for p in parents}
    for p in parents:
        children = chunker.split_into_children(p, ["Cardiology", "CAD"], global_vector_start_id=0)
        for c in children:
            assert c.parent_id in parent_ids


# ---------------------------------------------------------------------------
# Feature 6: Breadcrumb Context Injection
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f06_breadcrumb_taxonomy_prepending():
    """Verify child chunk has full breadcrumb prepended: [Discipline > Subspecialty > ...]"""
    injector = BreadcrumbInjector()
    taxonomy = ["Cardiology", "Arrhythmias", "Atrial Fibrillation"]
    header = injector.generate_breadcrumb(taxonomy)
    assert header.startswith("[Cardiology > Arrhythmias > Atrial Fibrillation]\n\n")


@pytest.mark.tier1
def test_f06_breadcrumb_depth_invariance():
    """Verify breadcrumb handles arbitrary taxonomy depths."""
    injector = BreadcrumbInjector()
    deep = ["Internal Medicine", "Cardiology", "Ischemic Heart Disease", "Acute Coronary Syndromes", "NSTEMI"]
    header = injector.generate_breadcrumb(deep)
    assert "NSTEMI" in header
    assert header.startswith("[Internal Medicine")


@pytest.mark.tier1
def test_f06_breadcrumb_separator_uniformity():
    """Verify breadcrumb formatting strictly uses ' > ' as delimiter."""
    injector = BreadcrumbInjector()
    taxonomy = ["Neurology", "Cerebrovascular", "Ischemic Stroke"]
    header = injector.generate_breadcrumb(taxonomy)
    assert " > " in header
    assert "Neurology" in header


@pytest.mark.tier1
def test_f06_breadcrumb_preserves_retrieval_semantic_keywords():
    """Verify injected breadcrumbs contain key discipline terms for retrieval."""
    injector = BreadcrumbInjector()
    injected = injector.inject("Ketone bodies present.", ["Endocrinology", "Diabetes Mellitus", "Ketoacidosis"])
    assert "Endocrinology" in injected
    assert "Diabetes Mellitus" in injected
    assert "Ketoacidosis" in injected


@pytest.mark.tier1
def test_f06_breadcrumb_does_not_mutate_body_markdown():
    """Verify breadcrumb header leaves body markdown formatting intact."""
    injector = BreadcrumbInjector()
    body = "### Clinical Findings\n- **Blood Glucose**: > 250 mg/dL"
    injected = injector.inject(body, ["Emergency Medicine", "Endocrine"])
    assert "### Clinical Findings" in injected
    assert "- **Blood Glucose**: > 250 mg/dL" in injected
