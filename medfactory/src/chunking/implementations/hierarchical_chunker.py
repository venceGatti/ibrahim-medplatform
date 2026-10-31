import hashlib
from typing import List, Optional
from medfactory.src.chunking.interfaces.chunking_interface import IChunker
from medfactory.src.chunking.base.chunk_models import ParentChunk, ChildChunk
from medfactory.src.chunking.implementations.breadcrumb_injector import BreadcrumbInjector


class HierarchicalChunker(IChunker):
    """
    Chunking gerarchico a due livelli:
    Parent: 800 - 1200 token
    Child: 150 - 250 token
    Breadcrumb Context Injection su Child (<= 20% dei token child, <= 50 token).
    """

    def __init__(
        self,
        target_parent_tokens: int = 1000,
        target_child_tokens: int = 200,
        child_overlap: int = 30
    ):
        self.target_parent_tokens = target_parent_tokens
        self.target_child_tokens = target_child_tokens
        self.child_overlap = child_overlap
        self.breadcrumb_injector = BreadcrumbInjector()

    def count_tokens(self, text_content: str) -> int:
        """Calcola deterministica stima dei token basata sui lemmi separati da spazi."""
        token_list = text_content.split()
        return len(token_list)

    def generate_breadcrumb(self, section_hierarchy: List[str]) -> str:
        """Genera l'intestazione breadcrumb delegando a BreadcrumbInjector."""
        return self.breadcrumb_injector.generate_breadcrumb(section_hierarchy)

    def split_into_parents(
        self,
        source_id: str,
        chapter: str,
        section_path: str,
        full_text: str,
        page_start: int = 1,
        page_end: int = 1
    ) -> List[ParentChunk]:
        """
        Suddivide il testo complessivo di un capitolo o sezione in una lista di ParentChunk
        con granularità orientata a 800-1200 token.
        """
        words = full_text.split()
        total_words = len(words)
        if total_words == 0:
            return []

        parent_chunks: List[ParentChunk] = []
        start_index = 0
        parent_sequence = 0

        while start_index < total_words:
            end_index = min(start_index + self.target_parent_tokens, total_words)
            chunk_words = words[start_index:end_index]
            chunk_content = " ".join(chunk_words)
            chunk_tokens = len(chunk_words)

            parent_seed = f"{source_id}_{chapter}_{section_path}_{parent_sequence}"
            parent_id = f"p_{hashlib.sha256(parent_seed.encode('utf-8')).hexdigest()[:16]}"

            parent = ParentChunk(
                parent_id=parent_id,
                source_id=source_id,
                chapter=chapter,
                section_path=section_path,
                page_start=page_start,
                page_end=page_end,
                raw_content=chunk_content,
                token_count=chunk_tokens
            )
            parent_chunks.append(parent)
            parent_sequence += 1

            if end_index >= total_words:
                break
            start_index = end_index

        return parent_chunks

    def split_into_children(
        self,
        parent: ParentChunk,
        section_hierarchy: List[str],
        global_vector_start_id: int,
        hpo_terms: Optional[List[str]] = None,
        atc_codes: Optional[List[str]] = None,
        icd10_codes: Optional[List[str]] = None
    ) -> List[ChildChunk]:
        """
        Suddivide un ParentChunk in una lista di ChildChunk (150-250 token)
        con iniezione deterministica della breadcrumb e attribuzione dei vettori.
        """
        breadcrumb = self.generate_breadcrumb(section_hierarchy)
        words = parent.raw_content.split()
        total_words = len(words)

        if total_words == 0:
            return []

        children: List[ChildChunk] = []
        start_index = 0
        child_sequence = 0
        current_vector_id = global_vector_start_id
        step = max(self.target_child_tokens - self.child_overlap, 50)

        while start_index < total_words:
            end_index = min(start_index + self.target_child_tokens, total_words)
            child_body = " ".join(words[start_index:end_index])
            child_tokens = len(words[start_index:end_index])

            child_seed = f"{parent.parent_id}_{child_sequence}"
            child_id = f"c_{hashlib.sha256(child_seed.encode('utf-8')).hexdigest()[:16]}"

            children.append(
                ChildChunk(
                    child_id=child_id,
                    parent_id=parent.parent_id,
                    vector_id=current_vector_id,
                    breadcrumb_header=breadcrumb,
                    text_content=child_body,
                    token_count=child_tokens,
                    hpo_terms=hpo_terms or [],
                    atc_codes=atc_codes or [],
                    icd10_codes=icd10_codes or []
                )
            )

            current_vector_id += 1
            child_sequence += 1
            if end_index >= total_words:
                break
            start_index += step

        return children
