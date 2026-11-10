"""Specialized Mixin for Pharmacology, CYP450, and CPIC database insertions."""
import sqlite3
from typing import Sequence, Tuple, Any


class SQLitePharmaInserterMixin:
    """Methods for inserting pharmacology and interaction tables into SQLite KB."""

    conn: sqlite3.Connection

    def insert_substance_cyp_profiles(
        self,
        cyp_profile_records: Sequence[Tuple[str, str, int, str, str, float, str]],
    ) -> None:
        """Insert substance CYP450 metabolism profiles."""
        cursor = self.conn.cursor()
        cursor.executemany(
            """
            INSERT OR REPLACE INTO substance_cyp_profiles (
                atc_code, inn_name, is_prodrug, isoenzyme, role, fm_fraction, potency_tier
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (atc, inn, int(bool(prodrug)), iso, role, float(fm), tier)
                for atc, inn, prodrug, iso, role, fm, tier in cyp_profile_records
            ],
        )
        self.conn.commit()

    def insert_substance_organ_risks(
        self,
        organ_risk_records: Sequence[Tuple[str, str, int, float, float, int, int, int]],
    ) -> None:
        """Insert organ toxicity risks for active pharmaceutical ingredients."""
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
            ],
        )
        self.conn.commit()

    def insert_atc_combinations(
        self,
        combination_records: Sequence[Tuple[str, str, str, str, float]],
    ) -> None:
        """Insert multi-ingredient FDC combinations."""
        cursor = self.conn.cursor()
        cursor.executemany(
            """
            INSERT OR REPLACE INTO atc_combinations (
                combo_atc_code, combo_inn_name, component_atc_code, component_inn_name, stoichiometric_ratio
            ) VALUES (?, ?, ?, ?, ?)
            """,
            [(c_atc, c_inn, comp_atc, comp_inn, float(ratio)) for c_atc, c_inn, comp_atc, comp_inn, ratio in combination_records],
        )
        self.conn.commit()

    def insert_cpic_guidelines(
        self,
        guideline_records: Sequence[Tuple[str, str, str, str, str, int, str]],
    ) -> None:
        """Insert CPIC pharmacogenomics level 1A dosing recommendations."""
        cursor = self.conn.cursor()
        cursor.executemany(
            """
            INSERT OR REPLACE INTO cpic_guidelines (
                guideline_id, atc_code, gene_symbol, diplotype_phenotype,
                clinical_recommendation, is_absolute_contraindication, evidence_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (g_id, atc, gene, pheno, rec, int(bool(contra)), ev)
                for g_id, atc, gene, pheno, rec, contra, ev in guideline_records
            ],
        )
        self.conn.commit()
