import pytest
import sqlite3
import tempfile
import os
import hashlib
import math
from pathlib import Path
from typing import List, Tuple, Union, Dict, Any
from cryptography.hazmat.primitives.asymmetric import ed25519

PROJECT_ROOT = Path(__file__).resolve().parent.parent

EXACT_ZSTD_DICT_SIZE_BYTES: int = 114688


def compute_sha256_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compute_blake3_hash(data: bytes) -> str:
    import blake3
    return blake3.blake3(data).hexdigest()


def generate_ed25519_keypair():
    priv = ed25519.Ed25519PrivateKey.generate()
    return priv, priv.public_key()


from medclient.sidecar_python.src.implementations.hotspot_evaluator import point_in_polygon_even_odd
from medclient.sidecar_python.src.api.server import create_app
from medclient.sidecar_python.src.implementations.sqlite_pool import SqliteConnectionPool
from medclient.sidecar_python.src.implementations.blue_green_swap import BlueGreenHotSwap
from medclient.sidecar_python.src.base.sdui_models import (
    ClinicalSheetBlock as ClinicalSheetBlockContract,
    SymptomMatcherBlock as SymptomMatcherBlockContract,
    DrugSafetyBlock as DrugSafetyBlockContract,
    ExamSimulatorBlock as ExamSimulatorBlockContract,
)
from medclient.sidecar_python.src.implementations.ckd_epi import CKDEPI2021Calculator


def compute_ckd_epi_2021(serum_creatinine: float, age_years: float, is_female: bool) -> float:
    return CKDEPI2021Calculator().compute_egfr(int(age_years), is_female, serum_creatinine)


def compute_qsofa_score(respiratory_rate: float, systolic_blood_pressure: float, altered_mentation: bool) -> int:
    score = 0
    if respiratory_rate >= 22.0:
        score += 1
    if systolic_blood_pressure <= 100.0:
        score += 1
    if altered_mentation:
        score += 1
    return score


def compute_shock_index(heart_rate: float, systolic_blood_pressure: float) -> float:
    if systolic_blood_pressure <= 0:
        raise ValueError("Systolic blood pressure must be positive")
    return round(float(heart_rate) / float(systolic_blood_pressure), 3)


def log_sum_exp(logits: List[float]) -> float:
    if not logits:
        raise ValueError("Cannot compute log_sum_exp on empty vector")
    max_val = max(logits)
    if math.isinf(max_val) and max_val < 0:
        return -math.inf
    return max_val + math.log(sum(math.exp(x - max_val) for x in logits))


def compute_softmax_probabilities(logits: List[float]) -> List[float]:
    if not logits:
        return []
    lse = log_sum_exp(logits)
    if math.isinf(lse) and lse < 0:
        return [1.0 / len(logits)] * len(logits)
    return [math.exp(x - lse) for x in logits]


def fsrs_calculate_retrievability(elapsed_days: float, stability: float) -> float:
    if stability <= 0.0:
        raise ValueError("Stability must be strictly positive")
    from medclient.sidecar_python.src.implementations.fsrs_scheduler import FSRSScheduler
    return FSRSScheduler().calculate_retrievability(elapsed_days, stability)


@pytest.fixture(scope="session")
def real_sqlite_kb():
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clinical_icd10 (
            icd10_code TEXT,
            description TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS polypharmacy_ddi (
            atc_a TEXT,
            atc_b TEXT,
            description TEXT,
            severity TEXT
        )
    """)
    cursor.executemany("""
        INSERT INTO clinical_icd10 (icd10_code, description) VALUES (?, ?)
    """, [
        ("I21.0", "Acute transmural myocardial infarction of anterior wall"),
        ("I20.0", "Unstable angina"),
        ("I30.0", "Acute nonspecific idiopathic pericarditis"),
        ("J18.9", "Pneumonia, unspecified organism"),
    ])
    cursor.executemany("""
        INSERT INTO polypharmacy_ddi (atc_a, atc_b, description, severity) VALUES (?, ?, ?, ?)
    """, [
        ("B01AC04", "A02BC01", "Clopidogrel and Omeprazole interaction", "WARNING"),
    ])
    conn.commit()
    conn.close()

    yield path

    os.close(fd)
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def real_sqlite_pool(real_sqlite_kb):
    pool = SqliteConnectionPool(database_path=real_sqlite_kb, max_readers=4)
    yield pool
    pool.close()


@pytest.fixture
def hot_swap_controller(tmp_path, real_sqlite_kb):
    import json
    pointer_file = tmp_path / "active_db.json"
    manifest = {
        "active_slot": "blue",
        "active_path": str(real_sqlite_kb),
        "sha256": compute_sha256_hash(Path(real_sqlite_kb).read_bytes()),
        "schema_version": 3,
        "updated_at_utc": "2026-03-30T00:00:00Z"
    }
    pointer_file.write_text(json.dumps(manifest), encoding="utf-8")
    controller = BlueGreenHotSwap(pointer_file_path=str(pointer_file))
    return controller
