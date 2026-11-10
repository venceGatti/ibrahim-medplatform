import os
import sys
import json
import math
import hashlib
import sqlite3
import tempfile
from pathlib import Path
from typing import List, Tuple
from datetime import datetime, timezone
import blake3
from cryptography.hazmat.primitives.asymmetric import ed25519
import numpy as np
import pytest

# Core Project Root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Constants
EXACT_ZSTD_DICT_SIZE_BYTES = 114688

# Re-exported SDUI Contracts and Sidecar Services
from medclient.sidecar_python.src.base.sdui_models import (
    ClinicalSheetBlock as ClinicalSheetBlockContract,
    SymptomMatcherBlock as SymptomMatcherBlockContract,
    DrugSafetyBlock as DrugSafetyBlockContract,
    ExamSimulatorBlock as ExamSimulatorBlockContract,
)
from medclient.sidecar_python.src.implementations.hotspot_evaluator import (
    point_in_polygon_even_odd,
)
from medclient.sidecar_python.src.implementations.sqlite_pool import (
    SqliteConnectionPool,
)
from medclient.sidecar_python.src.implementations.blue_green_swap import (
    BlueGreenHotSwap,
)
from medclient.sidecar_python.src.api.server import create_app
from medclient.sidecar_python.src.implementations.softmax_normalizer import (
    LogSumExpNormalizer,
)


def compute_blake3_hash(data: bytes) -> str:
    """Compute 64-char hex BLAKE3 hash for bytes."""
    return blake3.blake3(data).hexdigest()


def compute_sha256_hash(data: bytes) -> str:
    """Compute 64-char hex SHA256 hash for bytes."""
    return hashlib.sha256(data).hexdigest()


def generate_ed25519_keypair() -> Tuple[ed25519.Ed25519PrivateKey, ed25519.Ed25519PublicKey]:
    """Generate Ed25519 keypair for cryptographic testing."""
    private_key = ed25519.Ed25519PrivateKey.generate()
    return private_key, private_key.public_key()


def compute_shock_index(heart_rate: float, systolic_blood_pressure: float) -> float:
    """Compute shock index (HR / SBP) rounded to 3 decimal places."""
    if systolic_blood_pressure <= 0:
        raise ValueError("Systolic blood pressure must be positive")
    return round(heart_rate / systolic_blood_pressure, 3)


def compute_qsofa_score(
    respiratory_rate: float, systolic_blood_pressure: float, altered_mentation: bool
) -> int:
    """Compute quick SOFA score (0-3)."""
    score = 0
    if respiratory_rate >= 22:
        score += 1
    if systolic_blood_pressure <= 100:
        score += 1
    if altered_mentation:
        score += 1
    return score


def compute_ckd_epi_2021(
    serum_creatinine: float, age_years: float, is_female: bool
) -> float:
    """Compute race-free CKD-EPI 2021 eGFR in mL/min/1.73m2."""
    if serum_creatinine <= 0.0:
        raise ValueError("Serum creatinine must be strictly positive")
    if age_years <= 0.0:
        raise ValueError("Patient age must be strictly positive")

    scr = float(serum_creatinine)
    age = float(age_years)
    kappa = 0.7 if is_female else 0.9
    alpha = -0.241 if is_female else -0.302
    female_factor = 1.012 if is_female else 1.0

    scr_over_kappa = scr / kappa
    min_factor = min(scr_over_kappa, 1.0) ** alpha
    max_factor = max(scr_over_kappa, 1.0) ** (-1.200)
    age_factor = 0.9938 ** age

    egfr = 142.0 * min_factor * max_factor * age_factor * female_factor
    return round(egfr, 2)


def fsrs_calculate_retrievability(elapsed_days: float, stability: float) -> float:
    """Compute FSRS retrievability probability R(t, S)."""
    if stability <= 0.0:
        raise ValueError("Stability must be strictly positive")
    factor = 19.0 / 81.0
    return math.pow(1.0 + factor * (max(0.0, elapsed_days) / stability), -0.5)


def log_sum_exp(logits: List[float]) -> float:
    """Compute numerically stable log-sum-exp."""
    if len(logits) == 0:
        raise ValueError("empty vector")
    z = np.asarray(logits, dtype=np.float64)
    finite_mask = np.isfinite(z)
    if not np.any(finite_mask):
        return -math.inf
    c = np.max(z[finite_mask])
    shifted = z - c
    exp_vals = np.zeros_like(shifted)
    exp_vals[finite_mask] = np.exp(shifted[finite_mask])
    sum_exp = np.sum(exp_vals)
    if sum_exp <= 0.0:
        return -math.inf
    return float(c + math.log(sum_exp))


def compute_softmax_probabilities(logits: List[float]) -> np.ndarray:
    """Compute softmax probabilities using LogSumExpNormalizer."""
    return LogSumExpNormalizer().normalize_logits(logits)


@pytest.fixture(scope="session")
def real_sqlite_kb():
    """Create a temporary real SQLite database fixture with test schemas."""
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clinical_icd10 (
            icd10_code TEXT PRIMARY KEY,
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

    try:
        os.close(fd)
    except OSError:
        pass
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def hot_swap_controller(tmp_path):
    """Fixture providing an active BlueGreenHotSwap instance."""
    pointer_path = tmp_path / "active_db.json"
    dummy_db = tmp_path / "slot_a.sqlite"
    conn = sqlite3.connect(str(dummy_db))
    conn.execute("CREATE TABLE t1 (id INTEGER PRIMARY KEY);")
    conn.commit()
    conn.close()

    initial_content = {
        "active_slot": "blue",
        "active_path": str(dummy_db),
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    pointer_path.write_text(json.dumps(initial_content), encoding="utf-8")
    return BlueGreenHotSwap(str(pointer_path))


@pytest.fixture
def real_sqlite_pool(real_sqlite_kb):
    """Fixture providing a read-only SqliteConnectionPool."""
    pool = SqliteConnectionPool(database_path=real_sqlite_kb, max_readers=2)
    yield pool
    pool.close()
