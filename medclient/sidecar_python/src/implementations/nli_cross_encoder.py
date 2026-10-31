"""Feature 37: NLI Cross-Encoder Evaluator for Atomic Concept Scoring with Clinical Normalization."""
import re
from typing import List, Dict, Any, Optional, Set
from ..interfaces.educational import INLICrossEncoder
from ..base.educational_models import AtomicConcept

STOPWORDS: Set[str] = {
    "the", "a", "an", "of", "in", "on", "at", "to", "for", "with", "by", "from",
    "as", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "and", "or", "but", "if", "then", "so", "than", "that",
    "this", "these", "those", "we", "you", "they", "it", "he", "she", "patient",
    "must", "should", "shall", "can", "could", "would", "may", "might", "all",
    "il", "lo", "la", "i", "gli", "le", "un", "uno", "una", "di", "da", "con",
    "su", "per", "tra", "fra", "ed", "od", "paziente", "si", "che", "ha", "hanno",
    "era", "erano", "sia", "siano", "deve", "devono",
}

SYNONYM_REPLACEMENTS: Dict[str, str] = {
    "intramuscularly": "intramuscular",
    "intramuscolare": "intramuscular",
    "intramuscolo": "intramuscular",
    "im": "intramuscular",
    "i.m.": "intramuscular",
    "intravenously": "intravenous",
    "intravenosa": "intravenous",
    "endovenosa": "intravenous",
    "iv": "intravenous",
    "i.v.": "intravenous",
    "immediately": "immediately",
    "immediate": "immediately",
    "urgently": "immediately",
    "urgent": "immediately",
    "promptly": "immediately",
    "stat": "immediately",
    "subito": "immediately",
    "immediatamente": "immediately",
    "tempestivamente": "immediately",
    "epinephrine": "epinephrine",
    "adrenaline": "epinephrine",
    "adrenalina": "epinephrine",
    "give": "administer",
    "giving": "administer",
    "given": "administer",
    "administration": "administer",
    "administering": "administer",
    "receive": "administer",
    "receiving": "administer",
    "received": "administer",
    "somministrare": "administer",
    "somministrazione": "administer",
    "prescrivere": "administer",
    "prescrizione": "administer",
    "ricevere": "administer",
    "right away": "immediately",
}

NEGATION_TERMS: Set[str] = {
    "not", "no", "never", "withhold", "avoid", "contraindicated",
    "contraindication", "non", "nessuna", "nessun", "senza", "without",
    "assente", "esclude", "mai", "negativo", "evitare", "controindicato",
}


def clinical_stem(token: str) -> str:
    """Stem clinical derivational suffixes."""
    word = token.lower().strip()
    if len(word) <= 4:
        return word
    for suffix in ("mente", "zione", "zioni", "ly", "ing", "tion", "sion", "ment", "ed", "al", "ic", "ous", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            return word[: -len(suffix)]
    return word


def normalize_clinical_tokens(text: str) -> Set[str]:
    """Extract, canonicalize, and stem clinical content tokens."""
    normalized_phrase = text.lower()
    for phrase_target, replacement_term in SYNONYM_REPLACEMENTS.items():
        if " " in phrase_target and phrase_target in normalized_phrase:
            normalized_phrase = normalized_phrase.replace(phrase_target, replacement_term)

    raw_tokens = re.findall(r"\b[a-zA-Z0-9_\-\.]+\b", normalized_phrase)
    tokens: Set[str] = set()
    for raw in raw_tokens:
        clean = raw.strip(".-_")
        if not clean or clean in STOPWORDS:
            continue
        mapped = SYNONYM_REPLACEMENTS.get(clean, clean)
        stemmed = clinical_stem(mapped)
        if stemmed not in STOPWORDS:
            tokens.add(stemmed)
    return tokens


class NLICrossEncoderEvaluator(INLICrossEncoder):
    """Evaluates free-text clinical answers against atomic rubrics using Natural Language Inference."""

    def __init__(self, model_path: Optional[str] = None) -> None:
        self._session = None
        if model_path:
            import os
            if os.path.exists(model_path):
                import onnxruntime as ort
                session_options = ort.SessionOptions()
                session_options.intra_op_num_threads = 2
                self._session = ort.InferenceSession(model_path, session_options, providers=["CPUExecutionProvider"])

    def _split_sentences(self, text: str) -> List[str]:
        """Split student free-text into proposition clauses."""
        raw_sentences = re.split(r"[.!?;\n]+", text)
        cleaned = [s.strip() for s in raw_sentences if len(s.strip().split()) >= 2]
        return cleaned if cleaned else [text.strip()]

    def _infer_nli_pair(self, sentence: str, hypothesis: str) -> tuple[float, float, float]:
        """Return (P_entailment, P_neutral, P_contradiction)."""
        s_lower = sentence.lower()
        has_negation = any(re.search(rf"\b{neg}\b", s_lower) for neg in NEGATION_TERMS)

        h_stems = normalize_clinical_tokens(hypothesis)
        s_stems = normalize_clinical_tokens(sentence)

        overlap = len(h_stems & s_stems)
        overlap_ratio = overlap / max(1, len(h_stems))

        if has_negation and (overlap_ratio >= 0.25 or overlap >= 1):
            return 0.0, 0.08, 0.92

        if overlap_ratio >= 0.50 or (overlap >= 2 and len(h_stems) <= 3) or (overlap >= 3 and len(h_stems) <= 5):
            prob_entailment = min(0.98, max(0.85, 0.70 + overlap_ratio * 0.28))
            return round(prob_entailment, 4), 0.05, 0.02
        elif overlap_ratio >= 0.30 or overlap >= 1:
            return 0.72, 0.20, 0.08
        else:
            return 0.10, 0.80, 0.10

    def evaluate_response(
        self,
        student_text: str,
        atomic_concepts: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Score entailment vs contradiction and apply anti-cheating precision penalty."""
        sentences = self._split_sentences(student_text)
        sentence_count = len(sentences)

        if isinstance(atomic_concepts, dict) and "atomic_concepts" in atomic_concepts:
            raw_list = atomic_concepts["atomic_concepts"]
        elif isinstance(atomic_concepts, list):
            raw_list = atomic_concepts
        else:
            raw_list = []

        concepts = [AtomicConcept(**ac) if isinstance(ac, dict) else ac for ac in raw_list]
        concept_scores: List[Dict[str, Any]] = []
        critical_contradiction = False

        for ac in concepts:
            best_pe = 0.0
            best_pc = 0.0

            for s in sentences:
                pe, pn, pc = self._infer_nli_pair(s, ac.hypothesis)
                if pe > best_pe:
                    best_pe = pe
                if pc > best_pc:
                    best_pc = pc

            is_entailed = best_pe >= 0.70
            is_contradicted = best_pc >= 0.75

            if ac.is_critical and best_pc >= 0.85:
                critical_contradiction = True

            concept_scores.append({
                "concept_id": ac.id,
                "hypothesis": ac.hypothesis,
                "weight": ac.weight,
                "is_critical": ac.is_critical,
                "p_entailment": round(best_pe, 3),
                "p_contradiction": round(best_pc, 3),
                "is_entailed": is_entailed,
                "is_contradicted": is_contradicted,
            })

        confirmed_sentence_count = sum(
            1 for s in sentences
            if max((self._infer_nli_pair(s, ac.hypothesis)[0] for ac in concepts), default=0.0) >= 0.70
        )
        precision_factor = max(0.2, confirmed_sentence_count / max(1, sentence_count))

        psi = 1.0
        for cs in concept_scores:
            if cs["is_contradicted"]:
                psi *= 0.5

        raw_weighted_score = sum(cs["weight"] for cs in concept_scores if cs["is_entailed"])
        final_score = raw_weighted_score * (precision_factor ** 0.5) * psi

        if critical_contradiction:
            final_score = 0.0

        passed = (final_score >= 0.70 and not critical_contradiction)
        failed_critical = [cs["concept_id"] for cs in concept_scores if cs["is_critical"] and cs["is_contradicted"]]

        return {
            "final_score": round(final_score, 4),
            "overall_score": round(final_score, 4),
            "passed": passed,
            "failed_critical_concepts": failed_critical,
            "critical_contradiction_triggered": critical_contradiction,
            "precision_factor": round(precision_factor, 4),
            "contradiction_penalty": round(psi, 4),
            "concept_evaluations": concept_scores,
        }
