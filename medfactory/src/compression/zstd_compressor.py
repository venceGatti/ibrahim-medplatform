"""
Backward-compatible adapter for ZstdDictionaryCompressor.
Delegates directly to 3-tier ZstdDictionaryTrainer implementation.
"""
from typing import List, Optional
from medfactory.src.compression.implementations.zstd_dictionary_trainer import ZstdDictionaryTrainer


class ZstdDictionaryCompressor:
    """
    Adapter compatibile con l'interfaccia legacy ZstdDictionaryCompressor.
    Utilizza ZstdDictionaryTrainer per garantire il rispetto del target a 114.688 Byte.
    """

    TARGET_DICT_SIZE: int = 114688

    def __init__(self) -> None:
        self.trainer = ZstdDictionaryTrainer()

    def train_dictionary(
        self,
        training_corpus_chunks: Optional[List[bytes]] = None,
        dict_size: int = TARGET_DICT_SIZE,
        corpus_record_stream: Optional[List[bytes]] = None,
    ) -> bytes:
        training_records = corpus_record_stream if corpus_record_stream is not None else training_corpus_chunks
        if training_records is None:
            raise ValueError("I campioni del corpus per l'addestramento non possono essere vuoti.")
        return self.trainer.train_dictionary(training_corpus_chunks=training_records, target_size=dict_size)

    def compress_stream(self, uncompressed_bytes: bytes, dictionary_bytes: bytes, compression_level: int = 19) -> bytes:
        return self.trainer.compress_stream(binary_buffer=uncompressed_bytes, dictionary_bytes=dictionary_bytes, compression_level=compression_level)

    def decompress_stream(self, compressed_bytes: bytes, dictionary_bytes: bytes) -> bytes:
        return self.trainer.decompress_stream(compressed_buffer=compressed_bytes, dictionary_bytes=dictionary_bytes)


__all__ = ["ZstdDictionaryCompressor", "ZstdDictionaryTrainer"]
