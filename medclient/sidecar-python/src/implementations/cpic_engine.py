"""Feature 34: CPIC Level 1A Pharmacogenomics Rule Engine."""
from typing import List, Dict, Any
from ..interfaces.pharmacology import IPharmacogenomicsEngine
from ..base.pharmacology_models import PharmacogenomicMatch


class CPICPharmacogenomicsEngine(IPharmacogenomicsEngine):
    """Evaluates actionable CPIC Level 1A guidelines against patient genotype."""

    def evaluate_genetics(
        self,
        prescribed_drugs: List[Dict[str, Any]],
        patient_genotypes: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        """Match prescribed drugs against CPIC Level 1A pharmacogenomic rules."""
        matches: List[PharmacogenomicMatch] = []

        # Normalize genotypes: gene -> diplotype/phenotype
        norm_geno = {k.strip().upper(): v.strip().upper() for k, v in patient_genotypes.items()}

        for drug in prescribed_drugs:
            atc = drug.get("atc_code", "").upper()
            inn = drug.get("inn_name", atc)

            # 1. HLA-B*57:01 + Abacavir (J05AF06)
            if atc == "J05AF06" or "ABACAVIR" in inn.upper():
                hla = norm_geno.get("HLA-B*57:01") or norm_geno.get("HLA-B") or ""
                if "POSITIVE" in hla or "*57:01" in hla or "CARRIER" in hla:
                    matches.append(
                        PharmacogenomicMatch(
                            gene_symbol="HLA-B*57:01",
                            patient_phenotype="POSITIVE",
                            detected_atc=atc,
                            recommendation="ABSOLUTE CONTRAINDICATION: High risk of life-threatening hypersensitivity reaction. Select alternative antiretroviral.",
                            is_absolute_contraindication=True,
                        )
                    )

            # 2. CYP2C19 Poor Metabolizer + Clopidogrel (B01AC04)
            if atc == "B01AC04" or "CLOPIDOGREL" in inn.upper():
                cyp2c19 = norm_geno.get("CYP2C19", "")
                if "POOR" in cyp2c19 or any(d in cyp2c19 for d in ["*2/*2", "*2/*3", "*3/*3", "PM"]):
                    matches.append(
                        PharmacogenomicMatch(
                            gene_symbol="CYP2C19",
                            patient_phenotype="POOR_METABOLIZER",
                            detected_atc=atc,
                            recommendation="THERAPEUTIC INEFFECTIVENESS: Inability to bioactivate clopidogrel. High risk of stent thrombosis. Switch to Prasugrel or Ticagrelor.",
                            is_absolute_contraindication=True,
                        )
                    )

            # 3. TPMT / NUDT15 + Azathioprine (L01BB02) / Mercaptopurine (L01BB03)
            if atc in ["L01BB02", "L01BB03"] or any(name in inn.upper() for name in ["AZATHIOPRINE", "MERCAPTOPURINE"]):
                tpmt = norm_geno.get("TPMT", "")
                nudt15 = norm_geno.get("NUDT15", "")
                if (
                    "POOR" in tpmt
                    or "POOR" in nudt15
                    or any(v in tpmt for v in ["*3A/*3A", "*2/*3A", "*3C/*3C", "PM"])
                    or any(v in nudt15 for v in ["*3/*3", "PM"])
                ):
                    matches.append(
                        PharmacogenomicMatch(
                            gene_symbol="TPMT/NUDT15",
                            patient_phenotype="POOR_METABOLIZER",
                            detected_atc=atc,
                            recommendation="SEVERE MYELOSUPPRESSION RISK: Drastically reduce dose by 90% or substitute with non-thiopurine immunosuppressant.",
                            is_absolute_contraindication=True,
                        )
                    )

            # 4. CYP2D6 Ultra-Rapid Metabolizer + Codeine (R05DA04)
            if atc == "R05DA04" or "CODEINE" in inn.upper():
                cyp2d6 = norm_geno.get("CYP2D6", "")
                if "ULTRA" in cyp2d6 or any(v in cyp2d6 for v in ["*1/*1XN", "*2/*2XN", "UM"]):
                    matches.append(
                        PharmacogenomicMatch(
                            gene_symbol="CYP2D6",
                            patient_phenotype="ULTRA_RAPID_METABOLIZER",
                            detected_atc=atc,
                            recommendation="FATAL RESPIRATORY DEPRESSION RISK: Rapid massive bioactivation to morphine. Absolute contraindication.",
                            is_absolute_contraindication=True,
                        )
                    )
                elif "POOR" in cyp2d6 or any(v in cyp2d6 for v in ["*4/*4", "*5/*5", "PM"]):
                    matches.append(
                        PharmacogenomicMatch(
                            gene_symbol="CYP2D6",
                            patient_phenotype="POOR_METABOLIZER",
                            detected_atc=atc,
                            recommendation="LACK OF ANALGESIC EFFICACY: Insufficient conversion to active morphine. Select non-CYP2D6 analgesic.",
                            is_absolute_contraindication=False,
                        )
                    )

            # 5. CYP2D6 Poor Metabolizer + Tamoxifen (L02BA01)
            if atc == "L02BA01" or "TAMOXIFEN" in inn.upper():
                cyp2d6 = norm_geno.get("CYP2D6", "")
                if "POOR" in cyp2d6 or any(v in cyp2d6 for v in ["*4/*4", "*5/*5", "PM"]):
                    matches.append(
                        PharmacogenomicMatch(
                            gene_symbol="CYP2D6",
                            patient_phenotype="POOR_METABOLIZER",
                            detected_atc=atc,
                            recommendation="REDUCED EFFICACY: Impaired endoxifen production. Recommend aromatase inhibitor in postmenopausal women.",
                            is_absolute_contraindication=False,
                        )
                    )

        return [m.model_dump() for m in matches]
