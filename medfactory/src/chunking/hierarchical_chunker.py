"""
Backward-compatible adapter for HierarchicalChunker, ParentChunk, ChildChunk.
Delegates directly to 3-tier implementations.
"""
from medfactory.src.chunking.base.chunk_models import ParentChunk, ChildChunk
from medfactory.src.chunking.implementations.hierarchical_chunker import HierarchicalChunker
from medfactory.src.chunking.implementations.breadcrumb_injector import BreadcrumbInjector

__all__ = ["ParentChunk", "ChildChunk", "HierarchicalChunker", "BreadcrumbInjector"]
