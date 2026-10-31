from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
from medfactory.src.chunking.base.chunk_models import ParentChunk, ChildChunk


class ISQLiteBuilder(ABC):
    """Interfaccia formale per la compilazione del database SQLite module_kb.sqlite."""

    @abstractmethod
    def insert_source(
        self,
        source_id: str,
        academic_title: str,
        publication_year: int,
        authors: List[str],
        publisher: str,
        isbn: Optional[str] = None,
        doi: Optional[str] = None,
        pmid: Optional[str] = None,
        edition: Optional[int] = None,
        volume: Optional[int] = None
    ) -> None:
        """Inserisce una sorgente bibliografica certificata."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")

    @abstractmethod
    def insert_parent_chunk(self, chunk: ParentChunk) -> None:
        """Inserisce un chunk genitore nel database."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")

    @abstractmethod
    def insert_child_chunk(self, chunk: ChildChunk) -> None:
        """Inserisce un chunk figlio e aggiorna l'indice FTS5."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")

    @abstractmethod
    def vacuum_into(self, target_path: Path) -> None:
        """Esegue VACUUM INTO verso il percorso target deterministico."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")
