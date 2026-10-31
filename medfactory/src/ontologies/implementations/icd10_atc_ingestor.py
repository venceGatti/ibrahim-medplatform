import json
from pathlib import Path
from typing import List, Optional
from medfactory.src.ontologies.interfaces.ontology_interface import IClassificationIngestor
from medfactory.src.ontologies.base.ontology_models import ICD10Record, ATCSubstanceRecord


class ClassificationIngestor(IClassificationIngestor):
    """
    Ingestore formale per le classificazioni WHO ICD-10-CM e WHO/AIFA ATC Livello 5.
    Include l'attributo essenziale is_prodrug per il supporto clinico al motore CYP450 (ROA-10).
    """

    AUTHORITATIVE_ICD10_CATALOG: List[dict] = [
        {"code": "I21.0", "desc": "Infarto miocardico acuto transmurale della parete anteriore (STEMI)", "ch": "IX", "block": "I20-I25"},
        {"code": "I21.9", "desc": "Infarto miocardico acuto non specificato", "ch": "IX", "block": "I20-I25"},
        {"code": "I20.0", "desc": "Angina instabile (Sindrome coronarica acuta NSTE)", "ch": "IX", "block": "I20-I25"},
        {"code": "I26.9", "desc": "Embolia polmonare senza menzione di cuore polmonare acuto", "ch": "IX", "block": "I26-I28"},
        {"code": "I35.0", "desc": "Stenosi della valvola aortica non reumatica", "ch": "IX", "block": "I30-I52"},
        {"code": "I35.1", "desc": "Insufficienza della valvola aortica non reumatica", "ch": "IX", "block": "I30-I52"},
        {"code": "I50.9", "desc": "Insufficienza cardiaca congestizia", "ch": "IX", "block": "I30-I52"},
        {"code": "I10", "desc": "Ipertensione essenziale (primaria)", "ch": "IX", "block": "I10-I15"},
        {"code": "R57.0", "desc": "Shock cardiogeno", "ch": "XVIII", "block": "R50-R69"},
        {"code": "A41.9", "desc": "Sepsi e shock settico non specificato", "ch": "I", "block": "A30-A49"},
        {"code": "J18.9", "desc": "Polmonite comunitaria lobare non specificata", "ch": "X", "block": "J09-J18"},
        {"code": "N17.9", "desc": "Insufficienza renale acuta (AKI) non specificata", "ch": "XIV", "block": "N17-N19"},
        {"code": "N18.3", "desc": "Malattia renale cronica stadio 3", "ch": "XIV", "block": "N17-N19"},
        {"code": "E11.9", "desc": "Diabete mellito di tipo 2 senza complicanze", "ch": "IV", "block": "E10-E14"},
        {"code": "K21.9", "desc": "Malattia da reflusso gastroesofageo senza esofagite", "ch": "XI", "block": "K20-K31"}
    ]

    AUTHORITATIVE_ATC_CATALOG: List[dict] = [
        {
            "atc": "B01AC04", "name": "Clopidogrel", "l1": "B", "l2": "B01", "l3": "B01A", "l4": "B01AC",
            "prodrug": True, "cyp": ["CYP2C19", "CYP3A4"], "ddd": 75.0, "unit": "mg"
        },
        {
            "atc": "A02BC01", "name": "Omeprazolo", "l1": "A", "l2": "A02", "l3": "A02B", "l4": "A02BC",
            "prodrug": False, "cyp": ["CYP2C19", "CYP3A4"], "ddd": 20.0, "unit": "mg"
        },
        {
            "atc": "B01AC06", "name": "Acido Acetilsalicilico", "l1": "B", "l2": "B01", "l3": "B01A", "l4": "B01AC",
            "prodrug": False, "cyp": ["CYP2C9"], "ddd": 100.0, "unit": "mg"
        },
        {
            "atc": "B01AA03", "name": "Warfarin", "l1": "B", "l2": "B01", "l3": "B01A", "l4": "B01AA",
            "prodrug": False, "cyp": ["CYP2C9", "CYP3A4", "CYP1A2"], "ddd": 7.5, "unit": "mg"
        },
        {
            "atc": "B01AF01", "name": "Rivaroxaban", "l1": "B", "l2": "B01", "l3": "B01A", "l4": "B01AF",
            "prodrug": False, "cyp": ["CYP3A4"], "ddd": 20.0, "unit": "mg"
        },
        {
            "atc": "C01BD01", "name": "Amiodarone", "l1": "C", "l2": "C01", "l3": "C01B", "l4": "C01BD",
            "prodrug": False, "cyp": ["CYP3A4", "CYP2C9", "CYP2D6"], "ddd": 200.0, "unit": "mg"
        },
        {
            "atc": "N02AA01", "name": "Morfina", "l1": "N", "l2": "N02", "l3": "N02A", "l4": "N02AA",
            "prodrug": False, "cyp": ["UGT2B7"], "ddd": 30.0, "unit": "mg"
        },
        {
            "atc": "N02AA59", "name": "Codeina", "l1": "N", "l2": "N02", "l3": "N02A", "l4": "N02AA",
            "prodrug": True, "cyp": ["CYP2D6"], "ddd": 100.0, "unit": "mg"
        },
        {
            "atc": "N02AJ13", "name": "Tramadolo", "l1": "N", "l2": "N02", "l3": "N02A", "l4": "N02AJ",
            "prodrug": True, "cyp": ["CYP2D6", "CYP3A4"], "ddd": 200.0, "unit": "mg"
        },
        {
            "atc": "C09AA02", "name": "Enalapril", "l1": "C", "l2": "C09", "l3": "C09A", "l4": "C09AA",
            "prodrug": True, "cyp": [], "ddd": 10.0, "unit": "mg"
        },
        {
            "atc": "C09AA03", "name": "Lisinopril", "l1": "C", "l2": "C09", "l3": "C09A", "l4": "C09AA",
            "prodrug": False, "cyp": [], "ddd": 10.0, "unit": "mg"
        },
        {
            "atc": "C09AA05", "name": "Ramipril", "l1": "C", "l2": "C09", "l3": "C09A", "l4": "C09AA",
            "prodrug": True, "cyp": [], "ddd": 2.5, "unit": "mg"
        },
        {
            "atc": "C09CA01", "name": "Losartan", "l1": "C", "l2": "C09", "l3": "C09C", "l4": "C09CA",
            "prodrug": True, "cyp": ["CYP2C9", "CYP3A4"], "ddd": 50.0, "unit": "mg"
        },
        {
            "atc": "C07AB02", "name": "Metoprololo", "l1": "C", "l2": "C07", "l3": "C07A", "l4": "C07AB",
            "prodrug": False, "cyp": ["CYP2D6"], "ddd": 150.0, "unit": "mg"
        },
        {
            "atc": "C08CA01", "name": "Amlodipina", "l1": "C", "l2": "C08", "l3": "C08C", "l4": "C08CA",
            "prodrug": False, "cyp": ["CYP3A4"], "ddd": 5.0, "unit": "mg"
        },
        {
            "atc": "C10AA01", "name": "Simvastatina", "l1": "C", "l2": "C10", "l3": "C10A", "l4": "C10AA",
            "prodrug": True, "cyp": ["CYP3A4"], "ddd": 30.0, "unit": "mg"
        },
        {
            "atc": "A10BA02", "name": "Metformina", "l1": "A", "l2": "A10", "l3": "A10B", "l4": "A10BA",
            "prodrug": False, "cyp": [], "ddd": 2000.0, "unit": "mg"
        },
        {
            "atc": "J01FA09", "name": "Claritromicina", "l1": "J", "l2": "J01", "l3": "J01F", "l4": "J01FA",
            "prodrug": False, "cyp": ["CYP3A4"], "ddd": 500.0, "unit": "mg"
        },
        {
            "atc": "J01MA02", "name": "Ciprofloxacina", "l1": "J", "l2": "J01", "l3": "J01M", "l4": "J01MA",
            "prodrug": False, "cyp": ["CYP1A2"], "ddd": 1000.0, "unit": "mg"
        },
        {
            "atc": "J01MA12", "name": "Levofloxacina", "l1": "J", "l2": "J01", "l3": "J01M", "l4": "J01MA",
            "prodrug": False, "cyp": [], "ddd": 500.0, "unit": "mg"
        },
        {
            "atc": "J05AF06", "name": "Abacavir", "l1": "J", "l2": "J05", "l3": "J05A", "l4": "J05AF",
            "prodrug": False, "cyp": [], "ddd": 600.0, "unit": "mg"
        },
        {
            "atc": "L02BA01", "name": "Tamoxifene", "l1": "L", "l2": "L02", "l3": "L02B", "l4": "L02BA",
            "prodrug": True, "cyp": ["CYP2D6", "CYP3A4"], "ddd": 20.0, "unit": "mg"
        },
        {
            "atc": "H02AB07", "name": "Prednisone", "l1": "H", "l2": "H02", "l3": "H02A", "l4": "H02AB",
            "prodrug": True, "cyp": [], "ddd": 10.0, "unit": "mg"
        },
        {
            "atc": "M01AE01", "name": "Ibuprofene", "l1": "M", "l2": "M01", "l3": "M01A", "l4": "M01AE",
            "prodrug": False, "cyp": ["CYP2C9"], "ddd": 1200.0, "unit": "mg"
        },
        {
            "atc": "C03CA01", "name": "Furosemide", "l1": "C", "l2": "C03", "l3": "C03C", "l4": "C03CA",
            "prodrug": False, "cyp": [], "ddd": 40.0, "unit": "mg"
        },
        {
            "atc": "C03AA03", "name": "Idroclorotiazide", "l1": "C", "l2": "C03", "l3": "C03A", "l4": "C03AA",
            "prodrug": False, "cyp": [], "ddd": 25.0, "unit": "mg"
        }
    ]

    def ingest_icd10_catalog(self, source_file_path: Optional[str] = None) -> List[ICD10Record]:
        """
        Ingerisce la nosologia ICD-10. Se specificato un file JSON/CSV esistente, ne fa il parsing.
        """
        if source_file_path and Path(source_file_path).exists():
            records: List[ICD10Record] = []
            with open(source_file_path, "r", encoding="utf-8") as f_in:
                raw_icd10_entries = json.load(f_in)
                for icd10_entry in raw_icd10_entries:
                    records.append(
                        ICD10Record(
                            icd10_code=icd10_entry["code"],
                            description=icd10_entry["desc"],
                            chapter=icd10_entry.get("ch", ""),
                            block_range=icd10_entry.get("block", ""),
                            is_leaf_code=icd10_entry.get("is_leaf", True)
                        )
                    )
            return records

        return [
            ICD10Record(
                icd10_code=entry["code"],
                description=entry["desc"],
                chapter=entry["ch"],
                block_range=entry["block"],
                is_leaf_code=True
            )
            for entry in self.AUTHORITATIVE_ICD10_CATALOG
        ]

    def ingest_atc_catalog(self, source_file_path: Optional[str] = None) -> List[ATCSubstanceRecord]:
        """
        Ingerisce il catalogo ATC Livello 5 con metadati completi dei profarmaci e delle vie CYP450.
        """
        if source_file_path and Path(source_file_path).exists():
            records: List[ATCSubstanceRecord] = []
            with open(source_file_path, "r", encoding="utf-8") as f_in:
                raw_atc_entries = json.load(f_in)
                for atc_entry in raw_atc_entries:
                    records.append(
                        ATCSubstanceRecord(
                            atc_code=atc_entry["atc"],
                            substance_name=atc_entry["name"],
                            level1_anatomical=atc_entry.get("l1", ""),
                            level2_therapeutic=atc_entry.get("l2", ""),
                            level3_pharmacological=atc_entry.get("l3", ""),
                            level4_chemical=atc_entry.get("l4", ""),
                            is_prodrug=atc_entry.get("prodrug", False),
                            primary_cyp_enzymes=atc_entry.get("cyp", []),
                            defined_daily_dose=atc_entry.get("ddd"),
                            ddd_unit=atc_entry.get("unit")
                        )
                    )
            return records

        return [
            ATCSubstanceRecord(
                atc_code=entry["atc"],
                substance_name=entry["name"],
                level1_anatomical=entry["l1"],
                level2_therapeutic=entry["l2"],
                level3_pharmacological=entry["l3"],
                level4_chemical=entry["l4"],
                is_prodrug=entry["prodrug"],
                primary_cyp_enzymes=entry["cyp"],
                defined_daily_dose=entry["ddd"],
                ddd_unit=entry["unit"]
            )
            for entry in self.AUTHORITATIVE_ATC_CATALOG
        ]

    ingest_icd10 = ingest_icd10_catalog
    ingest_atc = ingest_atc_catalog


ICD10ATCIngestor = ClassificationIngestor
