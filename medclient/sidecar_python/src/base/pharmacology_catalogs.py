import json
import sqlite3
from typing import Dict, List, Any, Optional

def decompose_fdc_prescriptions(
    prescribed_drugs: List[Dict[str, Any]],
    db_connection: Optional[sqlite3.Connection] = None,
) -> List[Dict[str, Any]]:
    """Phase 0 FDC Decomposition (ROA-14): expand combined ATC codes into active constituents."""
    expanded_prescriptions: List[Dict[str, Any]] = []
    for drug_entry in prescribed_drugs:
        atc_code = str(drug_entry.get("atc_code", "")).strip().upper()
        constituents: Optional[List[Dict[str, Any]]] = None

        if db_connection is not None and atc_code:
            cursor = db_connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='atc_combinations'")
            if cursor.fetchone():
                cursor.execute("PRAGMA table_info(atc_combinations)")
                col_names = [col[1] for col in cursor.fetchall()]
                if "combo_atc_code" in col_names and "component_atc_code" in col_names:
                    cursor.execute(
                        "SELECT component_atc_code, component_inn_name FROM atc_combinations WHERE combo_atc_code = ?",
                        (atc_code,),
                    )
                    comb_rows = cursor.fetchall()
                    if comb_rows:
                        constituents = [{"atc_code": r[0], "inn_name": r[1]} for r in comb_rows]
                elif "fdc_atc_code" in col_names and "component_atc_codes" in col_names:
                    cursor.execute(
                        "SELECT component_atc_codes FROM atc_combinations WHERE fdc_atc_code = ?",
                        (atc_code,),
                    )
                    comb_row = cursor.fetchone()
                    if comb_row and comb_row[0]:
                        parsed_codes = json.loads(comb_row[0])
                        constituents = [{"atc_code": c, "inn_name": c} for c in parsed_codes]

        if constituents is None and atc_code in FDC_CONSTITUENT_CATALOG:
            constituents = FDC_CONSTITUENT_CATALOG[atc_code]

        if constituents:
            for constituent_spec in constituents:
                merged_entry = dict(drug_entry)
                merged_entry.update(constituent_spec)
                merged_entry["parent_fdc_atc"] = atc_code
                expanded_prescriptions.append(merged_entry)
        else:
            expanded_prescriptions.append(drug_entry)

    return expanded_prescriptions


FDC_CONSTITUENT_CATALOG: Dict[str, List[Dict[str, Any]]] = {
    "C09BA02": [
        {"atc_code": "C09AA02", "inn_name": "Enalapril", "is_ras_blocker": True},
        {"atc_code": "C03AA03", "inn_name": "Hydrochlorothiazide", "is_diuretic": True},
    ],
    "C09BA03": [
        {"atc_code": "C09AA03", "inn_name": "Lisinopril", "is_ras_blocker": True},
        {"atc_code": "C03AA03", "inn_name": "Hydrochlorothiazide", "is_diuretic": True},
    ],
    "C09BA05": [
        {"atc_code": "C09AA05", "inn_name": "Ramipril", "is_ras_blocker": True},
        {"atc_code": "C03AA03", "inn_name": "Hydrochlorothiazide", "is_diuretic": True},
    ],
    "C09DA01": [
        {"atc_code": "C09CA01", "inn_name": "Losartan", "is_ras_blocker": True},
        {"atc_code": "C03AA03", "inn_name": "Hydrochlorothiazide", "is_diuretic": True},
    ],
    "C09DA03": [
        {"atc_code": "C09CA03", "inn_name": "Valsartan", "is_ras_blocker": True},
        {"atc_code": "C03AA03", "inn_name": "Hydrochlorothiazide", "is_diuretic": True},
    ],
    "C09DA04": [
        {"atc_code": "C09CA04", "inn_name": "Irbesartan", "is_ras_blocker": True},
        {"atc_code": "C03AA03", "inn_name": "Hydrochlorothiazide", "is_diuretic": True},
    ],
    "N02AJ06": [
        {"atc_code": "R05DA04", "inn_name": "Codeine", "is_prodrug": True},
        {"atc_code": "N02BE01", "inn_name": "Paracetamol", "is_prodrug": False},
    ],
    "N02AJ13": [
        {"atc_code": "N02AX02", "inn_name": "Tramadol", "is_prodrug": True},
        {"atc_code": "N02BE01", "inn_name": "Paracetamol", "is_prodrug": False},
    ],
}

VERIFIED_PHARMACOKINETIC_PROFILES: Dict[str, Dict[str, Any]] = {
    "B01AC04": {
        "name": "Clopidogrel",
        "is_prodrug": True,
        "is_narrow_therapeutic_index": True,
        "substrates": {"CYP2C19": 0.85, "CYP3A4": 0.15},
        "inhibitors": {},
        "inducers": {},
    },
    "R05DA04": {
        "name": "Codeine",
        "is_prodrug": True,
        "is_narrow_therapeutic_index": False,
        "substrates": {"CYP2D6": 0.80, "CYP3A4": 0.20},
        "inhibitors": {},
        "inducers": {},
    },
    "N02AA05": {
        "name": "Codeine",
        "is_prodrug": True,
        "is_narrow_therapeutic_index": False,
        "substrates": {"CYP2D6": 0.80, "CYP3A4": 0.20},
        "inhibitors": {},
        "inducers": {},
    },
    "A02BC01": {
        "name": "Omeprazole",
        "is_prodrug": False,
        "is_narrow_therapeutic_index": False,
        "substrates": {"CYP2C19": 0.70, "CYP3A4": 0.30},
        "inhibitors": {"CYP2C19": "STRONG"},
        "inducers": {},
    },
    "N06AB03": {
        "name": "Fluoxetine",
        "is_prodrug": False,
        "is_narrow_therapeutic_index": False,
        "substrates": {"CYP2D6": 0.80},
        "inhibitors": {"CYP2D6": "STRONG", "CYP2C19": "MODERATE"},
        "inducers": {},
    },
    "B01AA03": {
        "name": "Warfarin",
        "is_prodrug": False,
        "is_narrow_therapeutic_index": True,
        "substrates": {"CYP2C9": 0.85, "CYP3A4": 0.15},
        "inhibitors": {},
        "inducers": {},
    },
    "C10AA01": {
        "name": "Simvastatin",
        "is_prodrug": False,
        "is_narrow_therapeutic_index": False,
        "substrates": {"CYP3A4": 0.90},
        "inhibitors": {},
        "inducers": {},
    },
    "J01FA09": {
        "name": "Clarithromycin",
        "is_prodrug": False,
        "is_narrow_therapeutic_index": False,
        "substrates": {"CYP3A4": 0.70},
        "inhibitors": {"CYP3A4": "STRONG"},
        "inducers": {},
    },
    "J01MA02": {
        "name": "Ciprofloxacin",
        "is_prodrug": False,
        "is_narrow_therapeutic_index": False,
        "substrates": {},
        "inhibitors": {"CYP1A2": "STRONG"},
        "inducers": {},
    },
    "J04AB02": {
        "name": "Rifampicin",
        "is_prodrug": False,
        "is_narrow_therapeutic_index": False,
        "substrates": {},
        "inhibitors": {},
        "inducers": {"CYP3A4": "STRONG", "CYP2C9": "STRONG", "CYP2C19": "STRONG"},
    },
    "N03AF01": {
        "name": "Carbamazepine",
        "is_prodrug": False,
        "is_narrow_therapeutic_index": True,
        "substrates": {"CYP3A4": 0.75},
        "inhibitors": {},
        "inducers": {"CYP3A4": "STRONG", "CYP2C9": "MODERATE"},
    },
}
