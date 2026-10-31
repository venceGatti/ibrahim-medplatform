"""Feature 23: Inverted Lexical Dictionary for colloquial terms to HPO/ICD-10 nodes."""
import unicodedata
import re
from typing import Dict, Any, Optional, List
from ..interfaces.nlp import IInvertedLexicalDictionary


class InvertedLexicalDictionary(IInvertedLexicalDictionary):
    """Normalizes colloquial phrases and maps them to canonical clinical ontologies."""

    def __init__(self) -> None:
        self._synonym_map: Dict[str, Dict[str, Any]] = {}
        self._load_standard_mappings()

    def _normalize(self, text: str) -> str:
        """Strip accents, lowercase, and remove special characters."""
        nfkd = unicodedata.normalize("NFKD", text)
        ascii_text = "".join(c for c in nfkd if not unicodedata.combining(c))
        cleaned = re.sub(r"[^\w\s]", " ", ascii_text.lower())
        return " ".join(cleaned.split())

    def _load_standard_mappings(self) -> None:
        """Load common Italian and English colloquial expressions to HPO/ICD-10."""
        mappings = [
            # Dyspnea
            ("fame d aria", "HP:0002094", "HPO", "Dyspnea", "Dispnea", "R06.0"),
            ("fiato corto", "HP:0002094", "HPO", "Dyspnea", "Dispnea", "R06.0"),
            ("affanno", "HP:0002094", "HPO", "Dyspnea", "Dispnea", "R06.0"),
            ("respiro corto", "HP:0002094", "HPO", "Dyspnea", "Dispnea", "R06.0"),
            ("shortness of breath", "HP:0002094", "HPO", "Dyspnea", "Dispnea", "R06.0"),
            # Chest pain
            ("dolore al petto", "HP:0100749", "HPO", "Chest pain", "Dolore toracico", "R07.9"),
            ("fitte al torace", "HP:0100749", "HPO", "Chest pain", "Dolore toracico", "R07.9"),
            ("bruciore al petto", "HP:0100749", "HPO", "Chest pain", "Dolore toracico", "R07.9"),
            ("peso sul petto", "HP:0100749", "HPO", "Chest pain", "Dolore toracico", "R07.9"),
            # Headache
            ("mal di testa", "HP:0002315", "HPO", "Headache", "Cefalea", "R51"),
            ("cerchio alla testa", "HP:0002315", "HPO", "Headache", "Cefalea", "R51"),
            ("pulsazioni alla testa", "HP:0002315", "HPO", "Headache", "Cefalea", "R51"),
            # Palpitations
            ("batticuore", "HP:0001962", "HPO", "Palpitations", "Palpitazioni", "R00.2"),
            ("cuore in gola", "HP:0001962", "HPO", "Palpitations", "Palpitazioni", "R00.2"),
            ("tuffo al cuore", "HP:0001962", "HPO", "Palpitations", "Palpitazioni", "R00.2"),
            # Nausea / Vomiting
            ("nausea", "HP:0002018", "HPO", "Nausea", "Nausea", "R11.0"),
            ("vomito", "HP:0002013", "HPO", "Vomiting", "Vomito", "R11.1"),
            ("rigetto", "HP:0002013", "HPO", "Vomiting", "Vomito", "R11.1"),
            # Fever
            ("febbre", "HP:0001945", "HPO", "Fever", "Febbre", "R50.9"),
            ("temperatura alta", "HP:0001945", "HPO", "Fever", "Febbre", "R50.9"),
            ("linee di febbre", "HP:0001945", "HPO", "Fever", "Febbre", "R50.9"),
            # Fatigue
            ("stanchezza", "HP:0012378", "HPO", "Fatigue", "Astenia", "R53.83"),
            ("spossatezza", "HP:0012378", "HPO", "Fatigue", "Astenia", "R53.83"),
            ("mancanza di forze", "HP:0012378", "HPO", "Fatigue", "Astenia", "R53.83"),
            # Syncope / Dizziness
            ("svenimento", "HP:0001279", "HPO", "Syncope", "Sincope", "R55"),
            ("giramento di testa", "HP:0002321", "HPO", "Vertigo", "Vertigine", "R42"),
            ("capogiro", "HP:0002321", "HPO", "Vertigo", "Vertigine", "R42"),
            # Cough
            ("tosse", "HP:0012735", "HPO", "Cough", "Tosse", "R05"),
            ("tosse stizzosa", "HP:0012735", "HPO", "Cough", "Tosse", "R05"),
            ("tosse grassa", "HP:0012735", "HPO", "Cough", "Tosse", "R05"),
        ]

        for phrase, target_code, source, pref_en, pref_it, icd_ref in mappings:
            normalized = self._normalize(phrase)
            self._synonym_map[normalized] = {
                "target_code": target_code,
                "ontology_source": source,
                "preferred_label": pref_en,
                "preferred_label_it": pref_it,
                "semantic_type": "Symptom",
                "icd10_cross_ref": icd_ref,
            }

    def register_synonym(
        self,
        colloquial_phrase: str,
        target_code: str,
        ontology_source: str,
        preferred_label: str,
        preferred_label_it: str,
        icd10_cross_ref: Optional[str] = None,
    ) -> None:
        """Register custom colloquial expression into dictionary."""
        normalized = self._normalize(colloquial_phrase)
        self._synonym_map[normalized] = {
            "target_code": target_code,
            "ontology_source": ontology_source,
            "preferred_label": preferred_label,
            "preferred_label_it": preferred_label_it,
            "semantic_type": "Symptom",
            "icd10_cross_ref": icd10_cross_ref,
        }

    def resolve_colloquial(self, phrase: str) -> Optional[Dict[str, Any]]:
        """Look up colloquial phrase, checking full string and n-gram subphrases."""
        normalized = self._normalize(phrase)
        if normalized in self._synonym_map:
            return self._synonym_map[normalized]

        # Sub-phrase matching
        words = normalized.split()
        for length in range(min(4, len(words)), 1, -1):
            for i in range(len(words) - length + 1):
                subphrase = " ".join(words[i : i + length])
                if subphrase in self._synonym_map:
                    return self._synonym_map[subphrase]

        return None
