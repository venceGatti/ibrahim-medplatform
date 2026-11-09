"""Shared test fixtures, cryptographic helpers, and clinical contracts for MedPlatform."""
import os
import sys
import math
import hashlib
import sqlite3
import tempfile
from pathlib import Path
from typing import List, Tuple, Dict, Any, Union, Optional

import pytest
import numpy as np
import blake3
from cryptography.hazmat.primitives.asymmetric import ed25519

# Path configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Constant definitions
EXACT_ZSTD_DICT_SIZE_BYTES = 114688

# Cryptographic and Hash Helpers
def compute_blake3_hash(data: bytes) -> str:
    """Calculate 64-character hexadecimal BLAKE3 hash."""
    return blake3.blake3(data).hexdigest()

def compute_sha256_hash(data: bytes) -> str:
    """Calculate 64-character hexadecimal SHA-256 hash."""
    return hashlib.sha256(data).hexdigest()

def generate_ed25519_keypair():
    """Generate Ed25519 private and public key pair for manifest signing."""
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key

# Clinical Utility Functions
def compute_shock_index(heart_rate: float, systolic_blood_pressure: float) -> float:
    """Compute Shock Index = HR / SBP."""
    if systolic_blood_pressure <= 0:
        raise ValueError("Systolic blood pressure must be strictly positive")
    if heart_rate <= 0:
        raise ValueError("Heart rate must be strictly positive")
    return round(float(heart_rate) / float(systolic_blood_pressure), 3)

def compute_qsofa_score(respiratory_rate: float, systolic_blood_pressure: float, altered_mentation: bool) -> int:
    """Compute quick SOFA score for sepsis screening (0-3 points)."""
    score = 0
    if respiratory_rate >= 22.0:
        score += 1
    if systolic_blood_pressure <= 100.0:
        score += 1
    if altered_mentation:
        score += 1
    return score

def compute_ckd_epi_2021(serum_creatinine: float, age_years: float, is_female: bool) -> float:
    """Compute race-free CKD-EPI 2021 eGFR."""
    from medclient.sidecar_python.src.implementations.ckd_epi import CKDEPI2021Calculator
    calculator = CKDEPI2021Calculator()
    return calculator.compute_egfr(
        age=int(age_years),
        is_female=is_female,
        serum_creatinine_mg_dl=serum_creatinine,
    )

def log_sum_exp(logits: Union[np.ndarray, List[float]]) -> float:
    """Compute numerically stable Log-Sum-Exp over logits."""
    z = np.asarray(logits, dtype=np.float64)
    if z.size == 0:
        raise ValueError("empty vector of logits provided")
    finite_mask = np.isfinite(z)
    if not np.any(finite_mask):
        return -float("inf")
    c = np.max(z[finite_mask])
    return float(c + np.log(np.sum(np.exp(z[finite_mask] - c))))

def compute_softmax_probabilities(logits: Union[np.ndarray, List[float]]) -> np.ndarray:
    """Convert logits into normalized probabilities summing to 1.0."""
    from medclient.sidecar_python.src.implementations.softmax_normalizer import LogSumExpNormalizer
    normalizer = LogSumExpNormalizer()
    return normalizer.normalize_logits(logits)

def point_in_polygon_even_odd(
    point_u: float,
    point_v: float,
    polygon_vertices: List[Tuple[float, float]],
) -> bool:
    """Evaluate point containment within polygon using Jordan curve Even-Odd Ray-Casting."""
    from medclient.sidecar_python.src.implementations.hotspot_evaluator import point_in_polygon_even_odd as pip
    return pip(point_u, point_v, polygon_vertices)

def fsrs_calculate_retrievability(elapsed_days: float, stability: float) -> float:
    """Calculate FSRS memory retrievability probability R(t, S)."""
    if stability <= 0.0:
        raise ValueError("Stability parameter must be strictly positive")
    from medclient.sidecar_python.src.implementations.fsrs_scheduler import FSRSScheduler
    scheduler = FSRSScheduler()
    return scheduler.calculate_retrievability(elapsed_days, stability)

# Host & Storage Engine Exports
from medclient.sidecar_python.src.implementations.sqlite_pool import SqliteConnectionPool
from medclient.sidecar_python.src.implementations.blue_green_swap import BlueGreenHotSwap
from medclient.sidecar_python.src.api.server import create_app

# SDUI Block Contract Classes
from medclient.sidecar_python.src.base.sdui_models import (
    ClinicalSheetBlock as ClinicalSheetBlockContract,
    SymptomMatcherBlock as SymptomMatcherBlockContract,
    DrugSafetyBlock as DrugSafetyBlockContract,
    ExamSimulatorBlock as ExamSimulatorBlockContract,
)

@pytest.fixture(scope="session")
def real_sqlite_kb():
    """Create a temporary database for SLA tests."""
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clinical_icd10 (
            icd10_code TEXT,
            description TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS polypharmacy_ddi (
            atc_a TEXT,
            atc_b TEXT,
            description TEXT,
            severity TEXT
        )
    ''')
    cursor.executemany('''
        INSERT INTO clinical_icd10 (icd10_code, description) VALUES (?, ?)
    ''', [
        ("I21.0", "Acute transmural myocardial infarction of anterior wall"),
        ("I20.0", "Unstable angina"),
        ("I30.0", "Acute nonspecific idiopathic pericarditis"),
        ("J18.9", "Pneumonia, unspecified organism"),
    ])
    cursor.executemany('''
        INSERT INTO polypharmacy_ddi (atc_a, atc_b, description, severity) VALUES (?, ?, ?, ?)
    ''', [
        ("B01AC04", "A02BC01", "Clopidogrel and Omeprazole interaction", "WARNING"),
    ])
    conn.commit()
    conn.close()

    yield path

    try:
        os.close(fd)
    except OSError:
        pass
    if os.path.exists(path):
        os.remove(path)

@pytest.fixture
def real_sqlite_pool(real_sqlite_kb):
    """Fixture providing a read-only SqliteConnectionPool."""
    pool = SqliteConnectionPool(database_path=real_sqlite_kb, max_readers=4)
    yield pool
    pool.close()

@pytest.fixture
def hot_swap_controller(tmp_path, real_sqlite_kb):
    """Fixture providing a configured BlueGreenHotSwap controller."""
    pointer_file = tmp_path / "active_db.json"
    controller = BlueGreenHotSwap(pointer_file_path=str(pointer_file))
    controller.swap_to_slot("blue", real_sqlite_kb)
    return controller
