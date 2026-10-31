from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class ParentChunk:
    """Chunk genitore di granularità macro (800 - 1200 token)."""
    parent_id: str
    source_id: str
    chapter: str
    section_path: str
    page_start: int
    page_end: int
    raw_content: str
    token_count: int

    def __post_init__(self) -> None:
        if not self.parent_id:
            raise ValueError("parent_id non puo' essere vuoto.")
        if self.token_count < 1:
            raise ValueError(f"token_count deve essere >= 1, ricevuto {self.token_count}")


@dataclass(frozen=True)
class ChildChunk:
    """Chunk figlio di granularità micro (150 - 250 token) con breadcrumb iniettata."""
    child_id: str
    parent_id: str
    vector_id: int
    breadcrumb_header: str
    text_content: str
    token_count: int
    hpo_terms: List[str] = field(default_factory=list)
    atc_codes: List[str] = field(default_factory=list)
    icd10_codes: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.child_id:
            raise ValueError("child_id non puo' essere vuoto.")
        if not self.parent_id:
            raise ValueError("parent_id non puo' essere vuoto.")
        if self.token_count < 1:
            raise ValueError(f"token_count deve essere >= 1, ricevuto {self.token_count}")
