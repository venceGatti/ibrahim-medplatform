from abc import ABC, abstractmethod
from typing import List
from medfactory.src.compression.base.compression_models import (
    CompressionMetadata,
    ClinicalSheetSynthesisRequest,
    SynthesizedMarkdownSheet
)


class IZstdTrainer(ABC):
    """Interfaccia formale per l'addestramento del dizionario custom Zstandard a 112 KB."""

    @abstractmethod
    def train_dictionary(self, training_corpus_chunks: List[bytes], target_size: int = 114688) -> bytes:
        """Addestra un dizionario Zstd con dimensione esatta di 114.688 Byte."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")

    @abstractmethod
    def compress_stream(self, binary_buffer: bytes, dictionary_bytes: bytes, compression_level: int = 19) -> bytes:
        """Comprime il buffer binario utilizzando il dizionario custom al livello 19."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")

    @abstractmethod
    def decompress_stream(self, compressed_buffer: bytes, dictionary_bytes: bytes) -> bytes:
        """Decomprime il buffer compresso verificando il ripristino deterministico."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")


class IMarkdownSynthesizer(ABC):
    """Interfaccia formale per la sintesi di schede cliniche statiche CommonMark."""

    @abstractmethod
    def synthesize_sheet(self, request: ClinicalSheetSynthesisRequest) -> SynthesizedMarkdownSheet:
        """Sintetizza una monografia clinica statica arricchita con callout di severità tipizzati."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")
