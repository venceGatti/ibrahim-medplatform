"""
MedFactory: Build-time engine and .medpack archive compiler.
Strict 3-tier production architecture adhering to deterministic execution.
"""

from medfactory.src.dla import DocumentLayoutAnalyzer, ComplexTableNormalizer, MedicalUnitScaleGuard
from medfactory.src.chunking import HierarchicalChunker, ParentChunk, ChildChunk, BreadcrumbInjector
from medfactory.src.ontologies import HPOIngestor, ClassificationIngestor
from medfactory.src.compression import ZstdDictionaryTrainer, ZstdDictionaryCompressor, StaticMarkdownSynthesizer
from medfactory.src.database import SQLiteModuleBuilder
from medfactory.src.packager import MedPackAssembler, MedPackManifest, MedPackVerifier
from medfactory.src.pipeline import MedFactoryPipeline, PipelineBuildConfig

__all__ = [
    "DocumentLayoutAnalyzer",
    "ComplexTableNormalizer",
    "MedicalUnitScaleGuard",
    "HierarchicalChunker",
    "ParentChunk",
    "ChildChunk",
    "BreadcrumbInjector",
    "HPOIngestor",
    "ClassificationIngestor",
    "ZstdDictionaryTrainer",
    "ZstdDictionaryCompressor",
    "StaticMarkdownSynthesizer",
    "SQLiteModuleBuilder",
    "MedPackAssembler",
    "MedPackVerifier",
    "MedPackManifest",
    "MedFactoryPipeline",
    "PipelineBuildConfig"
]
