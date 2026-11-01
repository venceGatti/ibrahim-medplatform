"""Feature 30: CYP450 Multi-Way Clearance Engine with Prodrug Bioactivation (ROA-10) and FDC Decomposition (ROA-14)."""
import json
import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, Generator
from ..interfaces.pharmacology import ICYP450Engine
from ..base.pharmacology_models import (
    CyP450Isoenzyme,
    CYPFunctionalState,
    SeverityLevel,
    EvidenceLevel,
    InteractionDetail,
)
from ..base.pharmacology_catalogs import (
    FDC_CONSTITUENT_CATALOG,
    VERIFIED_PHARMACOKINETIC_PROFILES,
    decompose_fdc_prescriptions,
)


class CYP450Engine(ICYP450Engine):
    """Models multi-way CYP450 clearance with explicit active drug vs prodrug distinction via SQLite."""

    ISOENZYMES = [
        CyP450Isoenzyme.CYP3A4,
        CyP450Isoenzyme.CYP2D6,
        CyP450Isoenzyme.CYP2C9,
        CyP450Isoenzyme.CYP2C19,
        CyP450Isoenzyme.CYP1A2,
    ]

    INHIBITOR_WEIGHTS = {"STRONG": 0.80, "MODERATE": 0.50, "WEAK": 0.20, "NONE": 0.00}
    INDUCER_WEIGHTS = {"STRONG": 1.00, "MODERATE": 0.50, "WEAK": 0.20, "NONE": 0.00}

    def __init__(self, db_pool: Optional[Any] = None) -> None:
        self._db_pool = db_pool
        self._standalone_kb_conn: Optional[sqlite3.Connection] = None

    @contextmanager
    def _acquire_connection(self) -> Generator[sqlite3.Connection, None, None]:
        if self._db_pool:
            with self._db_pool.acquire() as conn:
                yield conn
        else:
            if self._standalone_kb_conn is None:
                self._standalone_kb_conn = self._init_standalone_kb()
            yield self._standalone_kb_conn

    def _init_standalone_kb(self) -> sqlite3.Connection:
        """Initialize standalone in-memory SQLite schema for clinical drug profiles."""
        conn = sqlite3.connect(":memory:", check_same_thread=False)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE substance_cyp_profiles (
                atc_code TEXT NOT NULL, isoenzyme TEXT NOT NULL,
                metabolic_role TEXT NOT NULL, potency_or_fraction TEXT NOT NULL,
                PRIMARY KEY (atc_code, isoenzyme, metabolic_role)
            );
            """
        )
        for atc_k, prof in VERIFIED_PHARMACOKINETIC_PROFILES.items():
            for iso, frac in prof["substrates"].items():
                cur.execute("INSERT INTO substance_cyp_profiles VALUES (?, ?, 'SUBSTRATE', ?)", (atc_k, iso, str(frac)))
            for iso, pot in prof["inhibitors"].items():
                cur.execute("INSERT INTO substance_cyp_profiles VALUES (?, ?, 'INHIBITOR', ?)", (atc_k, iso, pot))
            for iso, pot in prof["inducers"].items():
                cur.execute("INSERT INTO substance_cyp_profiles VALUES (?, ?, 'INDUCER', ?)", (atc_k, iso, pot))
        conn.commit()
        return conn

    def _fetch_drug_profile(self, atc_code: str) -> Dict[str, Any]:
        """Fetch substance and CYP role profile from SQLite or verified catalog."""
        clean_atc = atc_code.strip().upper()
        empty_profile: Dict[str, Any] = {
            "name": clean_atc, "is_prodrug": False, "is_narrow_therapeutic_index": False,
            "substrates": {}, "inhibitors": {}, "inducers": {},
        }
        if not clean_atc:
            return empty_profile
        if clean_atc in VERIFIED_PHARMACOKINETIC_PROFILES:
            verified = VERIFIED_PHARMACOKINETIC_PROFILES[clean_atc]
            return {
                "name": verified["name"], "is_prodrug": verified["is_prodrug"],
                "is_narrow_therapeutic_index": verified["is_narrow_therapeutic_index"],
                "substrates": dict(verified["substrates"]), "inhibitors": dict(verified["inhibitors"]),
                "inducers": dict(verified["inducers"]),
            }

        with self._acquire_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clinical_atc'")
            if not cur.fetchone():
                return empty_profile

            cur.execute(
                """
                SELECT a.substance_name, a.is_prodrug AS atc_is_prodrug, a.primary_cyp_enzymes,
                       s.is_prodrug AS substance_is_prodrug
                FROM clinical_atc a LEFT JOIN substances s ON s.atc_code = a.atc_code
                WHERE a.atc_code = ?
                """,
                (clean_atc,),
            )
            row = cur.fetchone()
            if not row:
                return empty_profile

            is_prodrug = bool(row["substance_is_prodrug"] if row["substance_is_prodrug"] is not None else row["atc_is_prodrug"])
            raw_enz = row["primary_cyp_enzymes"]
            enz_list = json.loads(raw_enz) if raw_enz and raw_enz.startswith("[") else []
            valid_iso = {i.value for i in self.ISOENZYMES}
            filt_enz = [e for e in enz_list if e in valid_iso]
            share = round(1.0 / len(filt_enz), 4) if filt_enz else 0.0
            return {
                "name": row["substance_name"], "is_prodrug": is_prodrug, "is_narrow_therapeutic_index": False,
                "substrates": {enz: share for enz in filt_enz}, "inhibitors": {}, "inducers": {},
            }

    def evaluate_clearance(self, prescribed_drugs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute residual clearance Ce, substrate AUC ratios, and safety alerts."""
        with self._acquire_connection() as conn:
            expanded_drugs = decompose_fdc_prescriptions(prescribed_drugs, conn)

        cyp_states: Dict[str, CYPFunctionalState] = {}
        detected_interactions: List[InteractionDetail] = []
        auc_ratios: Dict[str, float] = {}

        for iso in self.ISOENZYMES:
            iso_key = iso.value
            total_inh, total_ind = 0.0, 0.0
            primary_inh, primary_ind = [], []

            for drug in expanded_drugs:
                atc = str(drug.get("atc_code", "")).strip().upper()
                profile = drug.get("cyp_profile") or self._fetch_drug_profile(atc)
                inh_pot = profile.get("inhibitors", {}).get(iso_key)
                if inh_pot:
                    total_inh += self.INHIBITOR_WEIGHTS.get(inh_pot.upper(), 0.0)
                    primary_inh.append(f"{atc}:{inh_pot}")
                ind_pot = profile.get("inducers", {}).get(iso_key)
                if ind_pot:
                    total_ind += self.INDUCER_WEIGHTS.get(ind_pot.upper(), 0.0)
                    primary_ind.append(f"{atc}:{ind_pot}")

            # Check if this is monotherapy and the drug inhibits/induces itself
            # We skip auto-inhibition and auto-induction for monotherapy
            if len(expanded_drugs) == 1 and expanded_drugs[0].get("atc_code", "").strip().upper() == atc:
                total_inh, total_ind = 0.0, 0.0
                primary_inh, primary_ind = [], []

            ce_val = max(0.05, 1.0 - total_inh + total_ind)
            cyp_states[iso_key] = CYPFunctionalState(
                isoenzyme=iso, baseline_capacity=1.0, computed_clearance=round(ce_val, 4),
                primary_inhibitors=primary_inh, primary_inducers=primary_ind,
            )

        interaction_counter = 1000
        for drug in expanded_drugs:
            atc = str(drug.get("atc_code", "")).strip().upper()
            inn_name = drug.get("inn_name", atc)
            profile = drug.get("cyp_profile") or self._fetch_drug_profile(atc)
            is_prodrug = bool(drug.get("is_prodrug", profile.get("is_prodrug", False)))
            is_nti = bool(drug.get("is_narrow_therapeutic_index", profile.get("is_narrow_therapeutic_index", False)))

            raw_fm: Dict[str, float] = dict(drug.get("fm_cyp") or profile.get("substrates", {}))
            if not raw_fm:
                auc_ratios[atc] = 1.0
                continue

            raw_sum_fm = sum(max(0.0, float(v)) for v in raw_fm.values())
            fm_dict = {k: (float(v) / raw_sum_fm if raw_sum_fm > 1.0 else float(v)) for k, v in raw_fm.items()}

            denom = sum(fm * cyp_states[iso].computed_clearance for iso, fm in fm_dict.items() if iso in cyp_states)
            denom += max(0.0, 1.0 - sum(fm_dict.values()))
            auc_ratio = 1.0 / max(0.05, denom)
            auc_ratios[atc] = round(auc_ratio, 4)

            for iso_name in fm_dict:
                if iso_name not in cyp_states:
                    continue
                ce = cyp_states[iso_name].computed_clearance
                ext_inh = [e.split(":")[0] for e in cyp_states[iso_name].primary_inhibitors if e.split(":")[0] != atc]
                ext_ind = [e.split(":")[0] for e in cyp_states[iso_name].primary_inducers if e.split(":")[0] != atc]

                if is_prodrug:
                    if ce < 0.90 and ext_inh:
                        source_atc = ext_inh[0]
                        if source_atc == atc:
                            continue
                        interaction_counter += 1
                        detected_interactions.append(
                            InteractionDetail(
                                interaction_id=interaction_counter,
                                source_atc=source_atc,
                                target_atc=atc,
                                severity=SeverityLevel.LEVEL_1,
                                evidence_level=EvidenceLevel.A,
                                mechanism=f"{source_atc} inhibits {iso_name}, blocking metabolic bioactivation of prodrug {inn_name}.",
                                clinical_consequence=f"Lethal therapeutic failure of {inn_name} (acute stent thrombosis / lack of efficacy).",
                                management_guideline="Absolute contraindication. Switch to alternative drug or non-inhibiting therapeutic class.",
                            )
                        )
                    elif ce > 1.20 and ext_ind:
                        source_atc = ext_ind[0]
                        if source_atc == atc:
                            continue
                        interaction_counter += 1
                        detected_interactions.append(
                            InteractionDetail(
                                interaction_id=interaction_counter,
                                source_atc=source_atc,
                                target_atc=atc,
                                severity=SeverityLevel.LEVEL_1,
                                evidence_level=EvidenceLevel.B,
                                mechanism=f"{source_atc} induces {iso_name}, accelerating bioactivation of {inn_name}.",
                                clinical_consequence="Hyperacute metabolite overdose / acute toxic accumulation.",
                                management_guideline="Avoid combination or drastically reduce dose under strict therapeutic monitoring.",
                            )
                        )
                else:
                    if is_nti and auc_ratio >= 2.0 and ext_inh:
                        source_atc = ext_inh[0]
                        if source_atc == atc:
                            continue
                        interaction_counter += 1
                        detected_interactions.append(
                            InteractionDetail(
                                interaction_id=interaction_counter,
                                source_atc=source_atc,
                                target_atc=atc,
                                severity=SeverityLevel.LEVEL_1,
                                evidence_level=EvidenceLevel.A,
                                mechanism=f"Multi-way inhibition of {iso_name} causes critical accumulation of narrow therapeutic index drug {inn_name}.",
                                clinical_consequence=f"Severe toxic accumulation (AUC ratio = {auc_ratio:.2f}x).",
                                management_guideline="Absolute contraindication or mandatory 75% dose reduction.",
                            )
                        )
                    elif auc_ratio >= 1.35 and ext_inh:
                        source_atc = ext_inh[0]
                        if source_atc == atc:
                            continue
                        interaction_counter += 1
                        detected_interactions.append(
                            InteractionDetail(
                                interaction_id=interaction_counter,
                                source_atc=source_atc,
                                target_atc=atc,
                                severity=SeverityLevel.LEVEL_2,
                                evidence_level=EvidenceLevel.B,
                                mechanism=f"Moderate inhibition of {iso_name} elevates {inn_name} exposure.",
                                clinical_consequence=f"Elevated plasma concentration (AUC ratio = {auc_ratio:.2f}x).",
                                management_guideline="Reduce dose or monitor serum concentrations closely.",
                            )
                        )

        return {
            "cyp_profile_states": {k: v.model_dump() for k, v in cyp_states.items()},
            "cyp_states": cyp_states,
            "auc_ratios": auc_ratios,
            "detected_interactions": [i.model_dump() for i in detected_interactions],
            "interactions": detected_interactions,
        }
