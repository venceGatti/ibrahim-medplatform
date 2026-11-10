"""
Specialized inserter mixin for exam items, medical lexicon, synonyms, and vector metadata.
"""
import json
import sqlite3
from typing import Optional, Sequence, Tuple, Any


class SQLiteExamAndLexiconInserterMixin:
    """Mixin for exam items, medical lexicon, synonyms, and vector metadata."""

    conn: sqlite3.Connection

    def insert_exam_items(
        self,
        exam_question_records: Sequence[Tuple[str, str, str, Any]]
    ) -> None:
        cursor = self.conn.cursor()
        cursor.executemany(
            """
            INSERT OR REPLACE INTO exam_items (
                item_id, item_type, domain_icd10, payload_json
            ) VALUES (?, ?, ?, ?)
            """,
            [
                (q_id, q_type, dom, json.dumps(q_content) if isinstance(q_content, dict) else str(q_content))
                for q_id, q_type, dom, q_content in exam_question_records
            ]
        )
        self.conn.commit()

    def insert_medical_lexicon(
        self,
        lexicon_records: Sequence[Tuple[str, int, Optional[str], Optional[str]]]
    ) -> None:
        cursor = self.conn.cursor()
        cursor.executemany(
            """
            INSERT OR REPLACE INTO medical_lexicon (term, frequency, hpo_id, icd10_code)
            VALUES (?, ?, ?, ?)
            """,
            [(term, int(freq), hpo, icd) for term, freq, hpo, icd in lexicon_records]
        )
        self.conn.commit()

    def insert_colloquial_synonyms(
        self,
        synonym_records: Sequence[Tuple[str, str, str]]
    ) -> None:
        cursor = self.conn.cursor()
        cursor.executemany(
            """
            INSERT OR REPLACE INTO colloquial_synonyms (colloquial_phrase, hpo_id, canonical_label)
            VALUES (?, ?, ?)
            """,
            [(phrase, hpo, label) for phrase, hpo, label in synonym_records]
        )
        self.conn.commit()

    def insert_vector_metadata(
        self,
        vector_records: Sequence[Tuple[int, str, int, bytes]]
    ) -> None:
        cursor = self.conn.cursor()
        cursor.executemany(
            """
            INSERT OR REPLACE INTO vector_metadata (vector_id, child_id, embedding_dimension, embedding_blob)
            VALUES (?, ?, ?, ?)
            """,
            [(int(v_id), c_id, int(dim), bytes(blob)) for v_id, c_id, dim, blob in vector_records]
        )
        self.conn.commit()
