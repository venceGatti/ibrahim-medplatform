"""
Modulo base per l'inserimento specializzato dei record clinici, ontologici,
farmacologici e docimologici in module_kb.sqlite (ROA-20).
"""

import json
import sqlite3
from typing import List, Optional, Sequence, Tuple, Union, Dict, Any


from .sqlite_pharma_inserter import SQLitePharmaInserterMixin


class SQLiteDomainInserterMixin(SQLitePharmaInserterMixin):
    """
    Mixin di persistenza per entità cliniche, ontologiche e farmacologiche.
    Fornisce metodi atomici di scrittura relazionale con schema STRICT.
    """

    conn: sqlite3.Connection

    def insert_icd10(
        self,
        code: str,
        description: str,
        chapter: str,
        block: str,
        is_leaf: bool = True,
        prior_probability: float = 0.01
    ) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO clinical_icd10 (
                icd10_code, description, chapter, block_range, is_leaf, prior_probability
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (code, description, chapter, block, 1 if is_leaf else 0, float(prior_probability))
        )
        self.conn.commit()

    def insert_atc(
        self,
        atc_code: str,
        name: str,
        l1: str,
        l2: str,
        l3: str,
        l4: str,
        is_prodrug: bool = False,
        cyp_enzymes: Optional[List[str]] = None,
        ddd: Optional[float] = None,
        unit: Optional[str] = None
    ) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO clinical_atc (
                atc_code, substance_name, level1_anatomical, level2_therapeutic,
                level3_pharmacological, level4_chemical, is_prodrug, primary_cyp_enzymes,
                defined_daily_dose, ddd_unit
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                atc_code, name, l1, l2, l3, l4,
                1 if is_prodrug else 0,
                json.dumps(cyp_enzymes or []),
                float(ddd) if ddd is not None else None,
                unit
            )
        )
        self.conn.commit()

    def insert_hpo(
        self,
        hpo_id: str,
        name: str,
        definition: str,
        ancestors: List[str],
        ic_score: float = 0.0,
        cluster_id: str = "GENERAL",
        cluster_gamma: float = 0.50,
        cost_weight: float = 1.0
    ) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO clinical_hpo (
                hpo_id, name, definition, ancestors_json, information_content,
                cluster_id, cluster_gamma, cost_weight
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                hpo_id, name, definition, json.dumps(ancestors),
                float(ic_score), cluster_id, float(cluster_gamma), float(cost_weight)
            )
        )
        self.conn.commit()

    def insert_rel_icd10_hpo(
        self,
        icd10_code_or_records: Union[str, Sequence[Tuple[Any, ...]]],
        hpo_id: Optional[str] = None,
        frequency: float = 100.0,
        is_mandatory: bool = False,
        is_pathognomonic: bool = False,
        lambda_multiplier: float = 1.0,
        weight_pos: float = 1.0,
        weight_neg: float = -0.5
    ) -> None:
        """Inserisce una singola relazione ICD10-HPO oppure un batch di tuple."""
        cursor = self.conn.cursor()
        sql_stmt = """
            INSERT OR REPLACE INTO rel_icd10_hpo (
                icd10_code, hpo_id, frequency_percentage, is_mandatory,
                is_pathognomonic, lambda_multiplier, weight_pos, weight_neg
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        if isinstance(icd10_code_or_records, str):
            if hpo_id is None:
                raise ValueError("hpo_id obbligatorio per inserimento singolo rel_icd10_hpo.")
            cursor.execute(
                sql_stmt,
                (
                    icd10_code_or_records, hpo_id, float(frequency),
                    1 if is_mandatory else 0, 1 if is_pathognomonic else 0,
                    float(lambda_multiplier), float(weight_pos), float(weight_neg)
                )
            )
        else:
            normalized_rows = []
            for row in icd10_code_or_records:
                if len(row) == 4:
                    c_icd, c_hpo, freq, mand = row
                    normalized_rows.append((c_icd, c_hpo, float(freq), int(bool(mand)), 0, 1.0, 1.0, -0.5))
                elif len(row) == 6:
                    c_icd, c_hpo, freq, mand, w_pos, w_neg = row
                    normalized_rows.append((c_icd, c_hpo, float(freq), int(bool(mand)), 0, 1.0, float(w_pos), float(w_neg)))
                else:
                    c_icd, c_hpo, freq, mand, patho, lam, w_pos, w_neg = row[:8]
                    normalized_rows.append((
                        c_icd, c_hpo, float(freq), int(bool(mand)),
                        int(bool(patho)), float(lam), float(w_pos), float(w_neg)
                    ))
            cursor.executemany(sql_stmt, normalized_rows)
        self.conn.commit()

    def insert_clinical_sheet(
        self,
        sheet_id: str,
        icd10_code: str,
        title: str,
        markdown: str,
        callouts: Optional[List[dict]] = None
    ) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO clinical_sheets (sheet_id, icd10_code, title, content_markdown, callouts_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (sheet_id, icd10_code, title, markdown, json.dumps(callouts or []))
        )
        self.conn.commit()

    def insert_substance(
        self,
        substance_id: str,
        substance_name: str,
        atc_code: Optional[str] = None,
        is_prodrug: bool = False,
        active_metabolite: Optional[str] = None,
    ) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO substances (
                substance_id, substance_name, atc_code, is_prodrug, active_metabolite
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (substance_id, substance_name, atc_code, 1 if is_prodrug else 0, active_metabolite),
        )
        self.conn.commit()

    def insert_substances(self, substance_records: Sequence[Tuple[str, str, Optional[str], int, Optional[str]]]) -> None:
        cursor = self.conn.cursor()
        cursor.executemany(
            """
            INSERT OR REPLACE INTO substances (
                substance_id, substance_name, atc_code, is_prodrug, active_metabolite
            ) VALUES (?, ?, ?, ?, ?)
            """,
            [(s_id, s_name, atc, int(bool(prodrug)), metab) for s_id, s_name, atc, prodrug, metab in substance_records]
        )
        self.conn.commit()

    def insert_drug_interaction(
        self,
        interaction_id: str,
        substance_a: str,
        substance_b: str,
        severity_level: int,
        mechanism_description: str,
        clinical_alert_text: str,
    ) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO drug_interactions (
                interaction_id, substance_a, substance_b, severity_level,
                mechanism_description, clinical_alert_text
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (interaction_id, substance_a, substance_b, int(severity_level), mechanism_description, clinical_alert_text),
        )
        self.conn.commit()

    def insert_drug_interactions(
        self,
        interaction_records: Sequence[Tuple[str, str, str, int, str, str]]
    ) -> None:
        cursor = self.conn.cursor()
        cursor.executemany(
            """
            INSERT OR REPLACE INTO drug_interactions (
                interaction_id, substance_a, substance_b, severity_level,
                mechanism_description, clinical_alert_text
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            [(i_id, sa, sb, int(sev), mech, alert) for i_id, sa, sb, sev, mech, alert in interaction_records]
        )
        self.conn.commit()

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
