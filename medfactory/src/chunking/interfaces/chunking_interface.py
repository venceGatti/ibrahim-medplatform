from abc import ABC, abstractmethod
from typing import List, Optional
from medfactory.src.chunking.base.chunk_models import ParentChunk, ChildChunk


class IChunker(ABC):
    """Interfaccia formale per il chunking gerarchico a due livelli."""

    @abstractmethod
    def count_tokens(self, text_content: str) -> int:
        """Calcola deterministicamente il numero di token nel testo."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")

    @abstractmethod
    def generate_breadcrumb(self, section_hierarchy: List[str]) -> str:
        """Genera l'intestazione breadcrumb dalla tassonomia della sezione."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")

    @abstractmethod
    def split_into_children(
        self,
        parent: ParentChunk,
        section_hierarchy: List[str],
        global_vector_start_id: int,
        hpo_terms: Optional[List[str]] = None,
        atc_codes: Optional[List[str]] = None,
        icd10_codes: Optional[List[str]] = None
    ) -> List[ChildChunk]:
        """Suddivide un ParentChunk in una sequenza di ChildChunk con breadcrumb iniettata."""
        raise NotImplementedError("Implementazione richiesta nella classe concreta.")
