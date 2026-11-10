"""Dedicated extra inserter methods for SQLiteModuleBuilder (keeps files under 350 lines)."""
import json
import sqlite3
from typing import Sequence, Tuple, Union, Dict, Any

class SQLiteExtraInserterMixin:
    """Extension mixin for organ risks, combinations, CPIC, exams, and lexicon."""
    conn: sqlite3.Connection

    def insert_substance_organ_risks(
        self,
        organ_risk_records: Sequence[Tuple[str, str, int, float, float, int, int, int]]
    ) -> None:
        cursor = self.conn.cursor()
        cursor.executemany(
            """
            INSERT OR REPLACE INTO substance_organ_risks (
                atc_code, inn_name, is_nti, qtc_risk_weight, nephro_risk_weight,
                is_ras_blocker, is_diuretic, is_nsaid
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (atc, inn, int(bool(nti)), float(qtc), float(nephro), int(bool(ras)), int(bool(diur)), int(bool(nsaid)))
                for atc, inn, nti, qtc, nephro, ras, diur, nsaid in organ_risk_records
            ]
        )
        self.conn.commit()

    def insert_atc_combinations(
        self,
        combination_records: Sequence[Tuple[str, str, str, str, float]]
    ) -> None:
        cursor = self.conn.cursor()
        cursor.executemany(
            """
            INSERT OR REPLACE INTO atc_combinations (
                combo_atc_code, combo_inn_name, component_atc_code, component_inn_name, stoichiometric_ratio
            ) VALUES (?, ?, ?, ?, ?)
            """,
            [(c_atc, c_inn, comp_atc, comp_inn, float(ratio)) for c_atc, c_inn, comp_atc, comp_inn, ratio in combination_records]
        )
        self.conn.commit()

    def insert_cpic_guidelines(
        self,
        cpic_records: Sequence[Tuple[str, str, str, str, str, str, int, str]]
    ) -> None:
        cursor = self.conn.cursor()
        cursor.executemany(
            """
            INSERT OR REPLACE INTO cpic_guidelines (
                gene_symbol, atc_code, inn_name, diplotype_phenotype,
                activity_score_range, recommendation_markdown, is_absolute_contraindication, alternative_guideline
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (gene, atc, inn, pheno, act, rec, int(bool(contra)), alt)
                for gene, atc, inn, pheno, act, rec, contra, alt in cpic_records
            ]
        )
        self.conn.commit()

    def insert_exam_items(
        self,
        exam_items: Sequence[Tuple[str, str, str, str, Union[str, Dict[str, Any]]]]
    ) -> None:
        cursor = self.conn.cursor()
        cursor.executemany(
            """
            INSERT OR REPLACE INTO exam_items (
                question_id, course_id, item_type, clinical_vignette, interactive_item_payload
            ) VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    q_id, c_id, i_type, vignette,
                    json.dumps(payload, ensure_ascii=False) if isinstance(payload, dict) else payload
                )
                for q_id, c_id, i_type, vignette, payload in exam_items
            ]
        )
        self.conn.commit()

    def insert_medical_lexicon(
        self,
        lexicon_terms: Sequence[Tuple[str, int, str]]
    ) -> None:
        cursor = self.conn.cursor()
        cursor.executemany(
            """
            INSERT OR REPLACE INTO medical_lexicon (
                term, corpus_frequency, semantic_category
            ) VALUES (?, ?, ?)
            """,
            [(term.strip().lower(), int(freq), cat) for term, freq, cat in lexicon_terms]
        )
        self.conn.commit()

    def insert_colloquial_synonyms(
        self,
        colloquial_records: Sequence[Tuple[str, str, float]]
    ) -> None:
        cursor = self.conn.cursor()
        cursor.executemany(
            """
            INSERT OR REPLACE INTO colloquial_synonyms (
                colloquial_term, canonical_concept_id, confidence_weight
            ) VALUES (?, ?, ?)
            """,
            [(lay.strip().lower(), canonical, float(conf)) for lay, canonical, conf in colloquial_records]
        )
        self.conn.commit()

    def insert_vector_metadata(
        self,
        vector_metadata_records: Sequence[Tuple[int, str, str, str]]
    ) -> None:
        cursor = self.conn.cursor()
        cursor.executemany(
            """
            INSERT OR REPLACE INTO vector_metadata (
                vector_id, child_chunk_id, parent_chunk_id, section_hierarchy
            ) VALUES (?, ?, ?, ?)
            """,
            vector_metadata_records
        )
        self.conn.commit()
