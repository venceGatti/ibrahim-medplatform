"""
srs_generator/__init__.py

Package di orchestrazione asincrona e sintesi tecnica dell'SRS.
"""

from __future__ import annotations

from srs_generator.audit_matrix import (
    ROA_CATALOG,
    audit_document_roas,
    calculate_sha256_digest,
    generate_traceability_matrix_markdown,
)
from srs_generator.gemini_client import AsyncGeminiOrchestrator
from srs_generator.synthesis_engine import DeterministicSynthesisEngine

__all__ = [
    "AsyncGeminiOrchestrator",
    "DeterministicSynthesisEngine",
    "ROA_CATALOG",
    "audit_document_roas",
    "calculate_sha256_digest",
    "generate_traceability_matrix_markdown",
]
