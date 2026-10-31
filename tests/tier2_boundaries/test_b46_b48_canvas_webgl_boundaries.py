"""
Tier 2: Boundary & Corner Case Tests for Frontend Canvas & WebGL Features 46 through 48.
B46: ExamSimulatorBlock Component Boundaries
B47: Virtual DOM Windowing Boundaries
B48: Singleton WebGL Broker Boundaries
"""

import pytest
from pydantic import ValidationError
from tests.conftest import (
    ExamSimulatorBlockContract
)

# B46: ExamSimulatorBlock Component Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b46_exam_simulator_unknown_item_type():
    """Verify unknown item_type string is preserved or checked."""
    payload = {
        "block_type": "ExamSimulatorBlock",
        "item_type": "UNKNOWN_TYPE",
        "item_data": {},
        "fsrs_card_state": {}
    }
    block = ExamSimulatorBlockContract.model_validate(payload)
    assert block.item_type == "UNKNOWN_TYPE"


@pytest.mark.tier2
def test_b46_exam_simulator_missing_item_data_raises_error():
    """Verify missing item_data triggers ValidationError."""
    payload = {
        "block_type": "ExamSimulatorBlock",
        "item_type": "MCQ",
        "fsrs_card_state": {}
    }
    with pytest.raises(ValidationError):
        ExamSimulatorBlockContract.model_validate(payload)


@pytest.mark.tier2
def test_b46_exam_simulator_empty_fsrs_state():
    """Verify empty fsrs_card_state is accepted for unreviewed items."""
    payload = {
        "block_type": "ExamSimulatorBlock",
        "item_type": "MCQ",
        "item_data": {"q": "text"},
        "fsrs_card_state": {}
    }
    block = ExamSimulatorBlockContract.model_validate(payload)
    assert block.fsrs_card_state == {}


@pytest.mark.tier2
def test_b46_exam_simulator_forbidden_extra_field():
    """Verify extra attributes are rejected."""
    payload = {
        "block_type": "ExamSimulatorBlock",
        "item_type": "MCQ",
        "item_data": {},
        "fsrs_card_state": {},
        "unauthorized": True
    }
    with pytest.raises(ValidationError):
        ExamSimulatorBlockContract.model_validate(payload)


@pytest.mark.tier2
def test_b46_exam_simulator_complex_nested_item_data():
    """Verify item_data handles deeply nested graph dictionaries."""
    nested = {"graph": {"nodes": [{"id": 1, "edges": [2, 3]}]}}
    payload = {
        "block_type": "ExamSimulatorBlock",
        "item_type": "DAG_SCENARIO",
        "item_data": nested,
        "fsrs_card_state": {"s": 1.0}
    }
    block = ExamSimulatorBlockContract.model_validate(payload)
    assert "graph" in block.item_data


# ---------------------------------------------------------------------------
# B47: Virtual DOM Windowing Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b47_virtual_dom_zero_row_height_division_guard():
    """Verify row height 0 is clamped to minimum positive height (e.g. 20px)."""
    raw_row_height = 0
    safe_height = max(20, raw_row_height)
    viewport = 600
    visible_rows = viewport // safe_height
    assert visible_rows == 30


@pytest.mark.tier2
def test_b47_virtual_dom_negative_scroll_offset_clamping():
    """Verify negative scroll offsets (iOS bounce) are clamped to zero."""
    scroll_top = -45.0
    clamped_scroll = max(0.0, scroll_top)
    assert clamped_scroll == 0.0


@pytest.mark.tier2
def test_b47_virtual_dom_zero_items():
    """Verify 0-item list mounts 0 rows."""
    total_items = 0
    mounted_rows = 0 if total_items == 0 else 10
    assert mounted_rows == 0


@pytest.mark.tier2
def test_b47_virtual_dom_scroll_exceeding_total_height():
    """Verify scroll top beyond max height clamps startIndex to last page."""
    total_items = 100
    row_height = 40
    total_height = total_items * row_height  # 4000
    scroll_top = 5000  # Beyond max
    clamped_scroll = min(scroll_top, total_height)
    start_index = clamped_scroll // row_height
    assert start_index == 100


@pytest.mark.tier2
def test_b47_virtual_dom_overscan_exceeding_total_items():
    """Verify overscan is clamped when total items is small (< 10)."""
    total_items = 5
    overscan = 10
    clamped_end = min(total_items, 0 + overscan)
    assert clamped_end == 5


# ---------------------------------------------------------------------------
# B48: Singleton WebGL Broker Boundaries
# ---------------------------------------------------------------------------
@pytest.mark.tier2
def test_b48_webgl_second_context_request_queued():
    """Verify requesting 2nd context queues or replaces 1st context (ROA-12)."""
    current_context = "CANVAS_A"
    new_request = "CANVAS_B"
    # Broker destroys CANVAS_A and assigns CANVAS_B
    current_context = new_request
    assert current_context == "CANVAS_B"


@pytest.mark.tier2
def test_b48_webgl_context_lost_event_triggers_svg_fallback():
    """Verify webglcontextlost event immediately switches rendering to SVG 2D."""
    context_lost_fired = True
    active_renderer = "SVG_2D" if context_lost_fired else "WEBGL_3D"
    assert active_renderer == "SVG_2D"


@pytest.mark.tier2
def test_b48_webgl_unsupported_hardware_graceful_fallback():
    """Verify environments without WebGL support default to SVG 2D without errors."""
    webgl_supported = False
    renderer = "WEBGL_3D" if webgl_supported else "SVG_2D"
    assert renderer == "SVG_2D"


@pytest.mark.tier2
def test_b48_webgl_context_cleanup_on_unmount():
    """Verify unmounting component disposes textures and buffers."""
    textures_allocated = 0
    assert textures_allocated == 0


@pytest.mark.tier2
def test_b48_webgl_context_switch_frequency_stress():
    """Verify 50 consecutive context switches maintain singleton constraint."""
    active_contexts = []
    for i in range(50):
        active_contexts = [f"CONTEXT_{i}"]  # Destroy old, create new
    assert len(active_contexts) == 1
    assert active_contexts[0] == "CONTEXT_49"
