"""Compression Package for MedFactory."""
from medfactory.src.compression.base.compression_models import (
    CalloutSeverityType,
    ClinicalCallout,
    ClinicalSheetSynthesisRequest,
    SynthesizedMarkdownSheet,
    CompressionMetadata
)
from medfactory.src.compression.interfaces.compression_interface import (
    IZstdTrainer,
    IMarkdownSynthesizer
)
from medfactory.src.compression.implementations.zstd_dictionary_trainer import ZstdDictionaryTrainer
from medfactory.src.compression.implementations.static_markdown_synthesizer import StaticMarkdownSynthesizer
from medfactory.src.compression.zstd_compressor import ZstdDictionaryCompressor

__all__ = [
    "CalloutSeverityType",
    "ClinicalCallout",
    "ClinicalSheetSynthesisRequest",
    "SynthesizedMarkdownSheet",
    "CompressionMetadata",
    "IZstdTrainer",
    "IMarkdownSynthesizer",
    "ZstdDictionaryTrainer",
    "StaticMarkdownSynthesizer",
    "ZstdDictionaryCompressor"
]
