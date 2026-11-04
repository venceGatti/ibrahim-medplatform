"""Feature 26: Sparse CSR Matrix Log-Odds Disease Ranker with Dirichlet Smoothing."""
import math
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from ..interfaces.diagnostic import ILogOddsRanker


class SparseCSRLogOddsRanker(ILogOddsRanker):
    """Computes probabilistic disease ranking using in-memory CSR matrix representation."""

    def __init__(
        self,
        epsilon: float = 1e-4,
        pathognomonic_alpha: float = 2.5,
        default_prior: float = 1e-4,
    ) -> None:
        self.epsilon = epsilon
        self.alpha_pat = pathognomonic_alpha
        self.default_prior = default_prior

        # Dictionaries mapping codes to integer indices
        self.disease_to_idx: Dict[str, int] = {}
        self.idx_to_disease: Dict[int, str] = {}
        self.feature_to_idx: Dict[str, int] = {}
        self.idx_to_feature: Dict[int, str] = {}

        # Disease metadata
        self.priors: np.ndarray = np.array([], dtype=np.float32)
        self.disease_names: Dict[str, str] = {}

        # Sparse CSR structure for positive log-odds weights
        self.csr_data: np.ndarray = np.array([], dtype=np.float32)
        self.csr_indices: np.ndarray = np.array([], dtype=np.int32)
        self.csr_indptr: np.ndarray = np.array([0], dtype=np.int32)

        # Pathognomonic lookup (disease_idx, feature_idx) -> bool
        self.pathognomonic_pairs: set[Tuple[int, int]] = set()

    def load_knowledge_base(
        self,
        diseases: List[Dict[str, Any]],
        features: List[Dict[str, Any]],
        co_occurrences: List[Dict[str, Any]],
    ) -> None:
        """Initialize CSR matrix and vocabularies from knowledge base rows."""
        self.disease_to_idx = {d["icd10_code"]: i for i, d in enumerate(diseases)}
        self.idx_to_disease = {i: d["icd10_code"] for i, d in enumerate(diseases)}
        self.disease_names = {d["icd10_code"]: d.get("preferred_label", d["icd10_code"]) for d in diseases}

        self.feature_to_idx = {f["hpo_id"]: i for i, f in enumerate(features)}
        self.idx_to_feature = {i: f["hpo_id"] for i, f in enumerate(features)}

        num_diseases = len(diseases)
        self.priors = np.full(num_diseases, self.default_prior, dtype=np.float32)
        for i, d in enumerate(diseases):
            if "prior" in d:
                self.priors[i] = max(1e-7, min(0.99, float(d["prior"])))

        # Build adjacency for CSR
        # co_occurrences has: disease_code, feature_code, count_dj, count_fi_dj, is_pathognomonic
        row_entries: Dict[int, List[Tuple[int, float]]] = {i: [] for i in range(num_diseases)}

        # Total counts across entire corpus for false alarm calculation
        total_disease_counts: Dict[int, float] = {i: 100.0 for i in range(num_diseases)}
        feature_global_counts: Dict[int, float] = {}

        for entry in co_occurrences:
            d_idx = self.disease_to_idx.get(entry["disease_code"])
            f_idx = self.feature_to_idx.get(entry["feature_code"])
            if d_idx is not None and f_idx is not None:
                c_fi_dj = float(entry.get("count_fi_dj", 10.0))
                c_dj = float(entry.get("count_dj", 100.0))
                total_disease_counts[d_idx] = max(c_dj, 1.0)
                feature_global_counts[f_idx] = feature_global_counts.get(f_idx, 0.0) + c_fi_dj

        sum_all_c_d = sum(total_disease_counts.values())

        for entry in co_occurrences:
            d_idx = self.disease_to_idx.get(entry["disease_code"])
            f_idx = self.feature_to_idx.get(entry["feature_code"])
            if d_idx is not None and f_idx is not None:
                c_fi_dj = float(entry.get("count_fi_dj", 10.0))
                c_dj = total_disease_counts[d_idx]

                p_fi_dj = (c_fi_dj + self.epsilon) / (c_dj + 2.0 * self.epsilon)

                other_fi = feature_global_counts.get(f_idx, 0.0) - c_fi_dj
                other_d = sum_all_c_d - c_dj
                p_fi_not_dj = (max(0.0, other_fi) + self.epsilon) / (max(1.0, other_d) + 2.0 * self.epsilon)

                # Weight of evidence
                weight = math.log(max(1e-9, p_fi_dj) / max(1e-9, p_fi_not_dj))

                if entry.get("is_pathognomonic", False):
                    self.pathognomonic_pairs.add((d_idx, f_idx))
                    weight *= self.alpha_pat

                row_entries[d_idx].append((f_idx, weight))

        # Flatten into CSR
        data_list: List[float] = []
        indices_list: List[int] = []
        indptr_list: List[int] = [0]

        for d_idx in range(num_diseases):
            sorted_entries = sorted(row_entries[d_idx], key=lambda x: x[0])
            for f_idx, w in sorted_entries:
                data_list.append(w)
                indices_list.append(f_idx)
            indptr_list.append(len(data_list))

        self.csr_data = np.array(data_list, dtype=np.float32)
        self.csr_indices = np.array(indices_list, dtype=np.int32)
        self.csr_indptr = np.array(indptr_list, dtype=np.int32)

    def score_diseases(
        self,
        positive_features: List[str],
        negative_features: List[str],
        cluster_assignments: Dict[str, str],
        pathognomonic_flags: Dict[str, bool],
    ) -> List[Tuple[str, float, List[str], List[str]]]:
        """Compute disease ranking logits with cluster dampening."""
        num_diseases = len(self.idx_to_disease)
        if num_diseases == 0:
            return []

        # Convert observed features to indices
        pos_indices = set()
        for f in positive_features:
            if f in self.feature_to_idx:
                pos_indices.add(self.feature_to_idx[f])

        # Group positive features by cluster for sub-linear dampening
        clusters: Dict[str, List[int]] = {}
        for f_idx in pos_indices:
            f_code = self.idx_to_feature[f_idx]
            cluster_id = cluster_assignments.get(f_code, f"singleton_{f_idx}")
            clusters.setdefault(cluster_id, []).append(f_idx)

        neg_indices = set()
        for f in negative_features:
            if f in self.feature_to_idx:
                neg_indices.add(self.feature_to_idx[f])

        results: List[Tuple[str, float, List[str], List[str]]] = []

        for d_idx in range(num_diseases):
            disease_code = self.idx_to_disease[d_idx]
            prior = self.priors[d_idx]
            prior_logit = math.log(prior / (1.0 - prior))

            start_ptr = self.csr_indptr[d_idx]
            end_ptr = self.csr_indptr[d_idx + 1]

            row_features = self.csr_indices[start_ptr:end_ptr]
            row_weights = self.csr_data[start_ptr:end_ptr]

            feature_weight_map = dict(zip(row_features, row_weights))

            # Apply cluster dampening
            total_evidence = 0.0
            supporting: List[str] = []

            for cluster_id, feat_list in clusters.items():
                cluster_present = [f for f in feat_list if f in feature_weight_map]
                if not cluster_present:
                    continue

                cluster_sum = 0.0
                for f_idx in cluster_present:
                    w = feature_weight_map[f_idx]
                    f_code = self.idx_to_feature[f_idx]
                    # Dynamic pathognomonic override
                    if pathognomonic_flags.get(f_code, False) or (d_idx, f_idx) in self.pathognomonic_pairs:
                        if (d_idx, f) not in self.pathognomonic_pairs:
                            w *= self.alpha_pat
                    cluster_sum += w
                    supporting.append(f_code)

                # Sub-linear dampening: gamma = 0.5
                k = len(cluster_present)
                dampened = cluster_sum / (k ** 0.5) if k > 1 else cluster_sum
                total_evidence += dampened

            # Apply negative features penalty
            negative_penalty = 0.0
            ruled_out: List[str] = []
            for f_idx in neg_indices:
                f_code = self.idx_to_feature[f_idx]
                if (d_idx, f_idx) in self.pathognomonic_pairs or pathognomonic_flags.get(f_code, False):
                    negative_penalty -= 12.0
                    ruled_out.append(f_code)
                elif f_idx in feature_weight_map:
                    negative_penalty -= 2.0
                    ruled_out.append(f_code)

            raw_logit = prior_logit + total_evidence + negative_penalty
            results.append((disease_code, raw_logit, supporting, ruled_out))

        results.sort(key=lambda cand_tuple: cand_tuple[1], reverse=True)
        return results

    def load_from_database(self, db_pool: Any) -> None:
        """Initialize CSR matrix and vocabularies directly from SQLite module_kb."""
        with db_pool.acquire() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT icd10_code, description FROM clinical_icd10 WHERE is_leaf = 1"
            )
            disease_rows = cursor.fetchall()
            diseases = [
                {
                    "icd10_code": r["icd10_code"] if hasattr(r, "__getitem__") else r[0],
                    "preferred_label": r["description"] if hasattr(r, "__getitem__") else r[1],
                    "prior": 0.01,
                }
                for r in disease_rows
            ]

            cursor.execute(
                "SELECT hpo_id, name, information_content FROM clinical_hpo"
            )
            feature_rows = cursor.fetchall()
            features = [
                {
                    "hpo_id": r["hpo_id"] if hasattr(r, "__getitem__") else r[0],
                    "name": r["name"] if hasattr(r, "__getitem__") else r[1],
                    "ic": float(r["information_content"] if hasattr(r, "__getitem__") else r[2]),
                }
                for r in feature_rows
            ]

            cursor.execute(
                """
                SELECT icd10_code, hpo_id, frequency_percentage, is_mandatory
                FROM rel_icd10_hpo
                """
            )
            rel_rows = cursor.fetchall()
            co_occurrences = [
                {
                    "disease_code": r["icd10_code"] if hasattr(r, "__getitem__") else r[0],
                    "feature_code": r["hpo_id"] if hasattr(r, "__getitem__") else r[1],
                    "count_dj": 100.0,
                    "count_fi_dj": float(r["frequency_percentage"] if hasattr(r, "__getitem__") else r[2]),
                    "is_pathognomonic": bool(r["is_mandatory"] if hasattr(r, "__getitem__") else r[3]),
                }
                for r in rel_rows
            ]

            self.load_knowledge_base(diseases, features, co_occurrences)
