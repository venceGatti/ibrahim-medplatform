"""Feature 22: SymSpell medical typo-tolerant candidate spellchecker (d <= 2)."""
from typing import List, Dict, Any, Optional
from symspellpy import SymSpell, Verbosity
from ..interfaces.nlp import IMedicalSpellchecker


class MedicalSymSpellChecker(IMedicalSpellchecker):
    """Symmetric Delete spellchecker initialized for clinical and medical terms."""

    def __init__(
        self,
        max_dictionary_edit_distance: int = 2,
        prefix_length: int = 7,
    ) -> None:
        self._max_distance = max_dictionary_edit_distance
        self._sym_spell = SymSpell(
            max_dictionary_edit_distance=max_dictionary_edit_distance,
            prefix_length=prefix_length,
        )
        self._load_default_medical_vocabulary()

    def _load_default_medical_vocabulary(self) -> None:
        """Seed SymSpell with foundational medical terms and common variants."""
        canonical_terms = [
            ("dispnea", 50000),
            ("tachicardia", 45000),
            ("bradicardia", 30000),
            ("ipotensione", 40000),
            ("ipertensione", 55000),
            ("ipercapnia", 25000),
            ("ipossiemia", 35000),
            ("cianosi", 20000),
            ("febbre", 60000),
            ("brivido", 22000),
            ("emottisi", 18000),
            ("dolore", 80000),
            ("precordiale", 15000),
            ("cefalea", 48000),
            ("astenia", 32000),
            ("edema", 37000),
            ("tosse", 52000),
            ("vomito", 41000),
            ("nausea", 43000),
            ("oliguria", 19000),
            ("anuria", 12000),
            ("ittero", 21000),
            ("pallore", 26000),
            ("sudorazione", 29000),
            ("toracico", 38000),
            ("polmonite", 35000),
            ("infarto", 42000),
            ("miocardico", 39000),
            ("sepsi", 36000),
            ("shock", 34000),
            ("crepitii", 17000),
            ("rantoli", 23000),
            ("broncospasmo", 19000),
            ("emottisi", 16000),
            ("epistassi", 14000),
            ("artralgia", 25000),
            ("mialgia", 27000),
            ("diarrea", 33000),
            ("vertigine", 28000),
            ("sincope", 24000),
            ("presincope", 13000),
        ]
        for term, freq in canonical_terms:
            self._sym_spell.create_dictionary_entry(term, freq)

    def add_custom_terms(self, terms_with_frequency: List[tuple[str, int]]) -> None:
        """Add additional clinical terms into the SymSpell index."""
        for term, freq in terms_with_frequency:
            self._sym_spell.create_dictionary_entry(term.lower().strip(), freq)

    def lookup(self, word: str, max_edit_distance: int = 2) -> List[Dict[str, Any]]:
        """Look up typo-tolerant corrections for a given medical word."""
        clean_word = word.lower().strip()
        suggestions = self._sym_spell.lookup(
            clean_word,
            Verbosity.CLOSEST,
            max_edit_distance=min(max_edit_distance, self._max_distance),
        )
        return [
            {
                "term": suggestion.term,
                "distance": suggestion.distance,
                "frequency": suggestion.count,
            }
            for suggestion in suggestions
        ]
