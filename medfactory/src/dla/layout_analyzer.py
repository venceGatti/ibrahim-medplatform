"""
Backward-compatible adapter for DocumentLayoutAnalyzer and BoundingBox.
Delegates directly to 3-tier implementations.
"""
from medfactory.src.dla.base.dla_models import DocumentBoundingBox as BoundingBox
from medfactory.src.dla.implementations.document_layout_analyzer import DocumentLayoutAnalyzer

__all__ = ["BoundingBox", "DocumentLayoutAnalyzer"]
