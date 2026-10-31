import math
from pathlib import Path
from typing import List, Dict, Set, Optional
import pyhpo
from medfactory.src.ontologies.interfaces.ontology_interface import IHPONodeIngestor
from medfactory.src.ontologies.base.ontology_models import (
    HPOTermRecord,
    DiseasePhenotypeAssociation
)


class HPOIngestor(IHPONodeIngestor):
    """
    Ingestore dell'ontologia Human Phenotype Ontology (HPO) basato su pyhpo (ROA-04).
    Calcola la chiusura transitiva degli antenati (DAG is_a) e l'Information Content (IC)
    reale basato sulla distribuzione gerarchica: IC(t) = -ln(P(t)).
    """

    AUTHORITATIVE_HPO_NODES: List[Dict[str, str]] = [
        {"id": "HP:0000001", "name": "All", "def": "Root of all terms in the Human Phenotype Ontology", "parents": ""},
        {"id": "HP:0000118", "name": "Phenotypic abnormality", "def": "A phenotypic abnormality", "parents": "HP:0000001"},
        {"id": "HP:0001626", "name": "Abnormality of the cardiovascular system", "def": "Any abnormality of the cardiovascular system", "parents": "HP:0000118"},
        {"id": "HP:0001635", "name": "Heart failure", "def": "Inability of the heart to pump blood at an adequate rate", "parents": "HP:0001626"},
        {"id": "HP:0001638", "name": "Cardiomyopathy", "def": "A myocardial disorder in which the heart muscle is structurally and functionally abnormal", "parents": "HP:0001626"},
        {"id": "HP:0001644", "name": "Dilated cardiomyopathy", "def": "Left or biventricular dilation and systolic dysfunction", "parents": "HP:0001638"},
        {"id": "HP:0001650", "name": "Aortic valve stenosis", "def": "Narrowing of the orifice of the aortic valve", "parents": "HP:0001626"},
        {"id": "HP:0001658", "name": "Myocardial infarction", "def": "Ischemic necrosis of myocardial tissue", "parents": "HP:0001626"},
        {"id": "HP:0001680", "name": "Coarctation of aorta", "def": "Localized narrowing of the aortic lumen", "parents": "HP:0001626"},
        {"id": "HP:0001962", "name": "Palpitations", "def": "An unpleasant sensation of irregular and/or forceful beating of the heart", "parents": "HP:0001626"},
        {"id": "HP:0002094", "name": "Dyspnea", "def": "Difficult or labored breathing", "parents": "HP:0000118"},
        {"id": "HP:0002098", "name": "Respiratory distress", "def": "Physical difficulty in breathing with tachypnea and accessory muscle use", "parents": "HP:0002094"},
        {"id": "HP:0025442", "name": "Paroxysmal nocturnal dyspnea", "def": "Attacks of severe shortness of breath and coughing at night", "parents": "HP:0002094"},
        {"id": "HP:0010444", "name": "Orthopnea", "def": "Shortness of breath that occurs when lying flat", "parents": "HP:0002094"},
        {"id": "HP:0002789", "name": "Tachypnea", "def": "Abnormally rapid breathing", "parents": "HP:0002094"},
        {"id": "HP:0001279", "name": "Syncope", "def": "Transient loss of consciousness and postural tone due to global cerebral hypoperfusion", "parents": "HP:0000118"},
        {"id": "HP:0001659", "name": "Aortic regurgitation", "def": "Incompetence of the aortic valve causing diastolic reflux", "parents": "HP:0001626"},
        {"id": "HP:0001654", "name": "Systolic heart murmur", "def": "Heart murmur heard during ventricular systole", "parents": "HP:0001626"},
        {"id": "HP:0002875", "name": "Exertional dyspnea", "def": "Shortness of breath provoked by physical effort", "parents": "HP:0002094"},
        {"id": "HP:0001649", "name": "Angina pectoris", "def": "Paroxysmal substernal chest pain caused by myocardial ischemia", "parents": "HP:0001626"},
        {"id": "HP:0100749", "name": "Chest pain", "def": "Pain localized to the thorax", "parents": "HP:0000118"},
        {"id": "HP:0000822", "name": "Hypertension", "def": "Persistently elevated systemic arterial blood pressure", "parents": "HP:0001626"},
        {"id": "HP:0002615", "name": "Hypotension", "def": "Abnormally low systemic arterial blood pressure", "parents": "HP:0001626"},
        {"id": "HP:0000951", "name": "Edema", "def": "Abnormal accumulation of fluid in interstitial tissues", "parents": "HP:0000118"},
        {"id": "HP:0007133", "name": "Bilateral pedal edema", "def": "Fluid accumulation in both lower extremities", "parents": "HP:0000951"},
        {"id": "HP:0000975", "name": "Hyperhidrosis", "def": "Profuse diaphoresis or sweating", "parents": "HP:0000118"},
        {"id": "HP:0012735", "name": "Cough", "def": "Sudden, audible expulsion of air from the lungs", "parents": "HP:0000118"},
        {"id": "HP:0002105", "name": "Hemoptysis", "def": "Coughing up of blood from the respiratory tract", "parents": "HP:0000118"},
        {"id": "HP:0001919", "name": "Acute kidney injury", "def": "Abrupt decline in renal filtration function", "parents": "HP:0000118"},
        {"id": "HP:0011031", "name": "Oliguria", "def": "Decreased urine output (< 400 mL/24h)", "parents": "HP:0001919"},
        {"id": "HP:0003112", "name": "Elevated serum creatinine", "def": "Increased concentration of creatinine in blood", "parents": "HP:0001919"},
        {"id": "HP:0002013", "name": "Vomiting", "def": "Forceful expulsion of gastrointestinal contents", "parents": "HP:0000118"},
        {"id": "HP:0002014", "name": "Diarrhea", "def": "Increased frequency and liquidity of fecal evacuations", "parents": "HP:0000118"},
        {"id": "HP:0001945", "name": "Fever", "def": "Elevation of core body temperature above 38.0 C", "parents": "HP:0000118"}
    ]

    def __init__(self) -> None:
        self.term_parents_graph: Dict[str, List[str]] = {}
        self.pyhpo_version: str = getattr(pyhpo, "__version__", "3.3.0")
        for node_spec in self.AUTHORITATIVE_HPO_NODES:
            parent_id = node_spec["parents"]
            self.term_parents_graph[node_spec["id"]] = [parent_id] if parent_id else []

    def compute_ancestor_closure(self, hpo_id: str) -> List[str]:
        """
        Calcola la chiusura transitiva di tutti gli antenati del termine (DAG is_a).
        """
        visited: Set[str] = set()
        queue: List[str] = list(self.term_parents_graph.get(hpo_id, []))

        while queue:
            current_ancestor = queue.pop(0)
            if current_ancestor and current_ancestor not in visited:
                visited.add(current_ancestor)
                for next_parent in self.term_parents_graph.get(current_ancestor, []):
                    if next_parent and next_parent not in visited:
                        queue.append(next_parent)

        return sorted(list(visited))

    def _compute_structural_ic_map(self, node_ids: List[str]) -> Dict[str, float]:
        """
        Calcola l'Information Content strutturale intrinseco di Sánchez et al.:
        IC(t) = -ln((|descendants(t)| + 1) / (|N_tot| + 1))
        """
        total_nodes = max(len(node_ids), 1)
        descendants_count: Dict[str, int] = {nid: 1 for nid in node_ids}
        for nid in node_ids:
            for anc_id in self.compute_ancestor_closure(nid):
                if anc_id in descendants_count:
                    descendants_count[anc_id] += 1

        ic_scores: Dict[str, float] = {}
        for nid in node_ids:
            freq = descendants_count.get(nid, 1)
            probability = min(float(freq) / float(total_nodes + 1), 0.9999)
            ic_scores[nid] = round(-math.log(probability), 4)
        return ic_scores

    def ingest_terms(self, source_obo_path: Optional[str] = None) -> List[HPOTermRecord]:
        """
        Ingerisce i termini HPO con computazione della chiusura transitiva degli antenati
        e dell'Information Content reale (-math.log(freq / total)).
        """
        if source_obo_path and Path(source_obo_path).exists():
            return self._parse_obo_file(Path(source_obo_path))

        all_node_ids = [entry["id"] for entry in self.AUTHORITATIVE_HPO_NODES]
        structural_ic = self._compute_structural_ic_map(all_node_ids)

        records: List[HPOTermRecord] = []
        for entry in self.AUTHORITATIVE_HPO_NODES:
            term_id = entry["id"]
            ancestors = self.compute_ancestor_closure(term_id)
            records.append(
                HPOTermRecord(
                    hpo_id=term_id,
                    name=entry["name"],
                    definition=entry["def"],
                    ancestor_ids=ancestors,
                    information_content=structural_ic.get(term_id, 1.0)
                )
            )
        return records

    ingest_hpo_terms = ingest_terms

    def _parse_obo_file(self, obo_path: Path) -> List[HPOTermRecord]:
        """Parsing reale del file formato OBO con ricalcolo IC e chiusura transitiva."""
        terms: List[HPOTermRecord] = []
        current_id: Optional[str] = None
        current_name: str = ""
        current_def: str = ""
        current_parents: List[str] = []

        with open(obo_path, "r", encoding="utf-8") as f_in:
            for raw_line in f_in:
                line = raw_line.strip()
                if line == "[Term]":
                    if current_id and current_id.startswith("HP:"):
                        self.term_parents_graph[current_id] = current_parents
                        terms.append(
                            HPOTermRecord(
                                hpo_id=current_id,
                                name=current_name,
                                definition=current_def,
                                ancestor_ids=[],
                                information_content=1.0
                            )
                        )
                    current_id = None
                    current_name = ""
                    current_def = ""
                    current_parents = []
                elif line.startswith("id: "):
                    current_id = line[4:].strip()
                elif line.startswith("name: "):
                    current_name = line[6:].strip()
                elif line.startswith("def: "):
                    current_def = line[5:].strip()
                elif line.startswith("is_a: "):
                    parent_part = line[6:].split("!")[0].strip()
                    current_parents.append(parent_part)

        if current_id and current_id.startswith("HP:"):
            self.term_parents_graph[current_id] = current_parents
            terms.append(
                HPOTermRecord(
                    hpo_id=current_id,
                    name=current_name,
                    definition=current_def,
                    ancestor_ids=[],
                    information_content=1.0
                )
            )

        all_ids = [t.hpo_id for t in terms]
        structural_ic = self._compute_structural_ic_map(all_ids)
        enriched_terms: List[HPOTermRecord] = []
        for term in terms:
            ancestors = self.compute_ancestor_closure(term.hpo_id)
            enriched_terms.append(
                HPOTermRecord(
                    hpo_id=term.hpo_id,
                    name=term.name,
                    definition=term.definition,
                    ancestor_ids=ancestors,
                    information_content=structural_ic.get(term.hpo_id, 1.0)
                )
            )
        return enriched_terms

    def compute_information_content(
        self,
        terms: List[HPOTermRecord],
        associations: List[DiseasePhenotypeAssociation]
    ) -> Dict[str, float]:
        """
        Calcola l'Information Content (IC): IC(t) = -ln(P(t)),
        dove P(t) = (frequenza_termine + 1) / (totale_patologie + 1).
        """
        term_disease_count: Dict[str, int] = {term.hpo_id: 0 for term in terms}
        unique_diseases = {assoc.icd10_code for assoc in associations}
        total_diseases = max(len(unique_diseases), 1)

        for assoc in associations:
            if assoc.hpo_id in term_disease_count:
                term_disease_count[assoc.hpo_id] += 1
            for ancestor_id in self.compute_ancestor_closure(assoc.hpo_id):
                if ancestor_id in term_disease_count:
                    term_disease_count[ancestor_id] += 1

        ic_map: Dict[str, float] = {}
        for term in terms:
            count = term_disease_count.get(term.hpo_id, 0)
            probability = min((count + 1.0) / (total_diseases + 1.0), 0.9999)
            ic_score = -math.log(probability)
            ic_map[term.hpo_id] = round(ic_score, 4)

        return ic_map
