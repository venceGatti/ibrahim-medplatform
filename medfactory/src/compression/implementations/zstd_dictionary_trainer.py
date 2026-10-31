import hashlib
from typing import List
import zstandard as zstd
from medfactory.src.compression.interfaces.compression_interface import IZstdTrainer


class ZstdDictionaryTrainer(IZstdTrainer):
    """
    Gestione compressione Zstandard con dizionario custom da esattamente 112 KB (114.688 Byte).
    Compressione ad alto livello (Level 19) e finestra rolling deterministica (ROA-05).
    """

    TARGET_DICT_SIZE: int = 114688  # 112 KB = 112 * 1024 Byte esatti
    ZSTD_DICT_MAGIC_LE: bytes = b"\x37\xa4\x30\xec"

    def _build_expanded_training_slices(
        self,
        training_corpus_chunks: List[bytes],
        target_size: int
    ) -> List[bytes]:
        """
        Espande deterministicamente i frammenti del corpus affinché l'algoritmo FastCover
        di Zstandard disponga di entropia e volume sufficienti (>= 100 frammenti e >= 4x target_size).
        """
        expanded_chunks: List[bytes] = []
        minimum_total_bytes = max(target_size * 4, 524288)
        accumulated_bytes = 0
        cycle_index = 0

        while len(expanded_chunks) < 128 or accumulated_bytes < minimum_total_bytes:
            for chunk_index, base_chunk in enumerate(training_corpus_chunks):
                if not base_chunk:
                    continue
                suffix_tag = f" [MED_CORPUS_SEG_{cycle_index}_{chunk_index}] ".encode("utf-8")
                enriched_slice = base_chunk + suffix_tag + base_chunk
                expanded_chunks.append(enriched_slice)
                accumulated_bytes += len(enriched_slice)
                if len(expanded_chunks) >= 128 and accumulated_bytes >= minimum_total_bytes:
                    break
            cycle_index += 1

        return expanded_chunks

    def train_dictionary(self, training_corpus_chunks: List[bytes], target_size: int = TARGET_DICT_SIZE) -> bytes:
        """
        Addestra un dizionario Zstandard dai frammenti del corpus medico forniti.
        Garantisce che il buffer binario risultante sia di dimensione esattamente pari a target_size
        (114.688 Byte), inizi con l'header magic 0xEC30A437 senza mai duplicarlo nel contenuto,
        e sia valido al 100% quando caricato con zstd.ZstdCompressionDict.
        """
        if not training_corpus_chunks:
            raise ValueError("I frammenti del corpus per l'addestramento non possono essere vuoti.")

        total_corpus_bytes = sum(len(chunk) for chunk in training_corpus_chunks)
        if total_corpus_bytes < 100:
            raise ValueError("La dimensione complessiva del corpus per l'addestramento è insufficiente.")

        expanded_slices = self._build_expanded_training_slices(training_corpus_chunks, target_size)

        trained_zstd_dictionary = zstd.train_dictionary(
            target_size,
            expanded_slices,
            k=64,
            d=8,
            steps=32,
            threads=1
        )
        raw_dict_bytes = trained_zstd_dictionary.as_bytes()

        current_len = len(raw_dict_bytes)
        if current_len == target_size:
            final_dict_bytes = raw_dict_bytes
        elif current_len < target_size:
            # Estende esclusivamente la sezione Content finale del dizionario Zstd (RFC 8878 Sec 5)
            # utilizzando byte lessicali del corpus privi del magic header 0xEC30A437
            missing_bytes = target_size - current_len
            corpus_content_stream = b"\n".join(training_corpus_chunks).replace(self.ZSTD_DICT_MAGIC_LE, b"MED_")
            if not corpus_content_stream:
                corpus_content_stream = hashlib.sha512(raw_dict_bytes[8:]).digest()
            repetitions = (missing_bytes // len(corpus_content_stream)) + 2
            content_extension = (corpus_content_stream * repetitions)[:missing_bytes]
            final_dict_bytes = raw_dict_bytes + content_extension
        else:
            final_dict_bytes = raw_dict_bytes[:target_size]

        if len(final_dict_bytes) != target_size:
            raise RuntimeError(
                f"Errore nella generazione del dizionario Zstd: attesi {target_size} byte, "
                f"ottenuti {len(final_dict_bytes)}"
            )

        # Verifica formale che il dizionario sia caricabile da ZstdCompressionDict
        validated_dict = zstd.ZstdCompressionDict(final_dict_bytes)
        if validated_dict.dict_id() == 0:
            raise RuntimeError("Il dizionario Zstandard generato presenta dict_id nullo non valido.")

        return final_dict_bytes

    def compress_stream(
        self,
        binary_buffer: bytes,
        dictionary_bytes: bytes,
        compression_level: int = 19
    ) -> bytes:
        """
        Comprime un flusso binario impiegando il dizionario custom al livello 19
        e windowLog limitata a 22 (4MB).
        """
        effective_level = min(max(int(compression_level), 1), 19)
        zstd_dict = zstd.ZstdCompressionDict(dictionary_bytes)
        compression_parameters = zstd.ZstdCompressionParameters.from_level(
            effective_level,
            window_log=22
        )
        compressor = zstd.ZstdCompressor(
            dict_data=zstd_dict,
            compression_params=compression_parameters
        )
        return compressor.compress(binary_buffer)

    def decompress_stream(self, compressed_buffer: bytes, dictionary_bytes: bytes) -> bytes:
        """
        Decomprime un flusso compresso verificando il ripristino deterministico.
        """
        zstd_dict = zstd.ZstdCompressionDict(dictionary_bytes)
        decompressor = zstd.ZstdDecompressor(dict_data=zstd_dict)
        return decompressor.decompress(compressed_buffer)
