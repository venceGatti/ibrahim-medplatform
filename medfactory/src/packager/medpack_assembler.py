"""
Backward-compatible adapter for MedPackAssembler.
Delegates directly to 3-tier implementation.
"""
from medfactory.src.packager.implementations.medpack_assembler import MedPackAssembler

__all__ = ["MedPackAssembler"]
