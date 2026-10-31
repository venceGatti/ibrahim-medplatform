"""
Backward-compatible adapter for MedPackManifest and related models.
Re-exports clean models from medfactory.src.packager.base.manifest_models without Ellipsis.
"""
from medfactory.src.packager.base.manifest_models import (
    MedicalStandardVersion,
    ChecksumRegister,
    StorageMetrics,
    MedPackManifest
)

__all__ = [
    "MedicalStandardVersion",
    "ChecksumRegister",
    "StorageMetrics",
    "MedPackManifest"
]
