"""Interfaces for SymSpell, Inverted Dictionary, and Semantic Embeddings."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np


class IMedicalSpellchecker(ABC):
    """Typo-tolerant candidate spellchecker over medical lemmata."""

    @abstractmethod
    def lookup(self, word: str, max_edit_distance: int = 2) -> List[Dict[str, Any]]:
        """Return correction candidates within edit distance."""
        raise NotImplementedError("Subclasses must implement lookup")


class IInvertedLexicalDictionary(ABC):
    """Lexical mapping from colloquial terminology to HPO and ICD-10 nodes."""

    @abstractmethod
    def resolve_colloquial(self, phrase: str) -> Optional[Dict[str, Any]]:
        """Resolve colloquial phrase to canonical clinical entity."""
        raise NotImplementedError("Subclasses must implement resolve_colloquial")


class ISemanticEmbeddingEngine(ABC):
    """Generates dense vector embeddings and computes vector cosine similarity."""

    @abstractmethod
    def encode(self, text: str) -> np.ndarray:
        """Encode text into normalized 384-dimensional embedding vector."""
        raise NotImplementedError("Subclasses must implement encode")

    @abstractmethod
    def compute_similarity(self, query_vector: np.ndarray, target_matrix: np.ndarray) -> np.ndarray:
        """Compute cosine similarity between query and candidate matrix."""
        raise NotImplementedError("Subclasses must implement compute_similarity")
