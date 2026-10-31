"""
Backward-compatible adapter for TableSpanResolver and TableCell.
Delegates directly to 3-tier implementations.
"""
from medfactory.src.dla.base.dla_models import RawTableCell as TableCell
from medfactory.src.dla.implementations.complex_table_normalizer import ComplexTableNormalizer as TableSpanResolver
from medfactory.src.dla.implementations.complex_table_normalizer import ComplexTableNormalizer

__all__ = ["TableCell", "TableSpanResolver", "ComplexTableNormalizer"]
