"""
Pytest configuration, authoritative reference algorithms, and shared test fixtures
for the MedPlatform End-to-End Test Suite.

All algorithms and fixtures implement formal mathematical, pharmacological,
and cryptographic specifications from PROJECT.md and AUDIT_AND_ASSUMPTIONS.md,
directly integrating production domain classes.
"""

import sys
import math
import json
import hashlib
from pathlib import Path
from typing import List, Tuple, Dict, Any
import pytest
from pydantic import BaseModel, Field, ConfigDict
from cryptography.hazmat.primitives.asymmetric import ed25519
import blake3
from starlette.testclient import TestClient

# Ensure workspace packages are on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SIDECAR_DIR = PROJECT_ROOT / "medclient" / "sidecar-python"
FACTORY_DIR = PROJECT_ROOT / "medfactory"

for directory_path in [PROJECT_ROOT, SIDECAR_DIR, FACTORY_DIR]:
    if str(directory_path) not in sys.path:
        sys.path.insert(0, str(directory_path))

# Production Class Imports
from medclient.sidecar_python.src.implementations.ckd_epi import CKDEPI2021Calculator
from medclient.sidecar_python.src.implementations.red_flags import RedFlagsInterceptor
from medclient.sidecar_python.src.implementations.softmax_normalizer import LogSumExpNormalizer
from medclient.sidecar_python.src.implementations.fsrs_scheduler import FSRSScheduler
from medclient.sidecar_python.src.implementations.sqlite_pool import SqliteConnectionPool
from medclient.sidecar_python.src.implementations.blue_green_swap import BlueGreenHotSwap
from medclient.sidecar_python.src.api.server import create_app
from medfactory.src.database.implementations.sqlite_module_builder import SQLiteModuleBuilder


def pytest_configure(config):
    """Register custom markers for test tiers."""
    config.addinivalue_line("markers", "tier1: Tier 1 Feature Coverage tests")
    config.addinivalue_line("markers", "tier2: Tier 2 Boundary & Corner Case tests")
    config.addinivalue_line("markers", "tier3: Tier 3 Pairwise Integration tests")
    config.addinivalue_line("markers", "tier4: Tier 4 Clinical Workload tests")
    config.addinivalue_line("markers", "benchmark: Production SLA Benchmark tests")


# ---------------------------------------------------------------------------
# Cryptographic & Compression Constants
# ---------------------------------------------------------------------------
EXACT_ZSTD_DICT_SIZE_BYTES: int = 114688  # 112 KB exactly (ROA-05)


def generate_ed25519_keypair() -> Tuple[ed25519.Ed25519PrivateKey, ed25519.Ed25519PublicKey]:
    """Generates an authentic Ed25519 keypair for cryptographic signature verification."""
    private_key = ed25519.Ed25519PrivateKey.generate()
    return private_key, private_key.public_key()


def compute_blake3_hash(buffer_bytes: bytes) -> str:
    """Computes the authoritative BLAKE3 hexadecimal digest of a buffer."""
    hasher = blake3.blake3()
    hasher.update(buffer_bytes)
    return hasher.hexdigest()


def compute_sha256_hash(buffer_bytes: bytes) -> str:
    """Computes the authoritative SHA-256 hexadecimal digest of a buffer."""
    return hashlib.sha256(buffer_bytes).hexdigest()


# ---------------------------------------------------------------------------
# Clinical Reference Equations Delegating to Production Engines
# ---------------------------------------------------------------------------
_EGFR_CALCULATOR = CKDEPI2021Calculator()
_RED_FLAGS_INTERCEPTOR = RedFlagsInterceptor()
_NORMALIZER = LogSumExpNormalizer()
_FSRS_SCHEDULER = FSRSScheduler()


def compute_ckd_epi_2021(serum_creatinine: float, age_years: float, is_female: bool) -> float:
    """Computes race-free eGFR using production CKDEPI2021Calculator."""
    return _EGFR_CALCULATOR.compute_egfr(int(age_years), is_female, serum_creatinine)


def compute_qsofa_score(respiratory_rate: int, systolic_blood_pressure: int, altered_mentation: bool) -> int:
    """Computes qSOFA score according to Sepsis-3 consensus definitions."""
    vitals = {
        "heart_rate_bpm": 80.0,
        "systolic_bp_mmhg": float(systolic_blood_pressure),
        "respiratory_rate_bpm": float(respiratory_rate),
        "spo2_percent": 98.0,
        "temperature_celsius": 37.0,
        "avpu_scale": "V" if altered_mentation else "A",
        "gcs_score": 14 if altered_mentation else 15,
    }
    outcome = _RED_FLAGS_INTERCEPTOR.evaluate(vitals)
    return outcome["qsofa_score"]


def compute_shock_index(heart_rate: int, systolic_blood_pressure: int) -> float:
    """Computes Shock Index = Heart Rate / Systolic Blood Pressure via RedFlagsInterceptor."""
    if systolic_blood_pressure <= 0:
        raise ValueError("Systolic blood pressure must be positive to avoid division by zero")
    vitals = {
        "heart_rate_bpm": float(heart_rate),
        "systolic_bp_mmhg": float(systolic_blood_pressure),
        "respiratory_rate_bpm": 16.0,
        "spo2_percent": 98.0,
        "temperature_celsius": 37.0,
    }
    outcome = _RED_FLAGS_INTERCEPTOR.evaluate(vitals)
    return outcome["shock_index"]


def log_sum_exp(log_odds_vector: List[float]) -> float:
    """Computes numerically stable Log-Sum-Exp to prevent floating point overflow."""
    if not log_odds_vector:
        raise ValueError("Cannot compute Log-Sum-Exp of empty vector")
    max_value = max(log_odds_vector)
    if math.isinf(max_value) and max_value < 0:
        return -math.inf
    sum_exponentials = sum(math.exp(val - max_value) for val in log_odds_vector)
    return max_value + math.log(sum_exponentials)


def compute_softmax_probabilities(log_odds_vector: List[float]) -> List[float]:
    """Computes normalized probabilities from log-odds scores using LogSumExpNormalizer."""
    if not log_odds_vector:
        return []
    probabilities = _NORMALIZER.normalize_logits(log_odds_vector)
    return [round(float(p), 6) for p in probabilities]


def point_in_polygon_even_odd(point_x: float, point_y: float, polygon_vertices: List[Tuple[float, float]]) -> bool:
    """
    Authoritative Ray-Casting Even-Odd algorithm for spatial image hotspot testing.
    Validates whether (point_x, point_y) lies inside polygon_vertices.
    """
    vertex_count = len(polygon_vertices)
    if vertex_count < 3:
        return False

    is_inside = False
    j = vertex_count - 1
    for i in range(vertex_count):
        xi, yi = polygon_vertices[i]
        xj, yj = polygon_vertices[j]
        intersect = ((yi > point_y) != (yj > point_y)) and (
            point_x < (xj - xi) * (point_y - yi) / (yj - yi) + xi
        )
        if intersect:
            is_inside = not is_inside
        j = i

    return is_inside


def fsrs_calculate_retrievability(elapsed_days: float, stability: float) -> float:
    """Calculates FSRS v4 retrievability probability R = (1 + factor * t / S)^decay."""
    if stability <= 0.0:
        raise ValueError("Stability must be strictly positive")
    return round(_FSRS_SCHEDULER.calculate_retrievability(elapsed_days, stability), 4)


# ---------------------------------------------------------------------------
# SDUI Pydantic Schema Contracts (Authoritative Dual-Registry Models)
# ---------------------------------------------------------------------------
from medclient.sidecar_python.src.base.sdui_models import (
    ClinicalSheetBlock,
    SymptomMatcherBlock,
    DrugSafetyBlock,
    ExamSimulatorBlock,
    SDUIMessageEnvelope,
    CalloutEntry,
    CalloutSeverity,
)

ClinicalSheetBlockContract = ClinicalSheetBlock
SymptomMatcherBlockContract = SymptomMatcherBlock
DrugSafetyBlockContract = DrugSafetyBlock
ExamSimulatorBlockContract = ExamSimulatorBlock


# ---------------------------------------------------------------------------
# Shared Authentic Pytest Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def authoritative_keypair():
    """Provides a fresh, non-reused cryptographic Ed25519 keypair."""
    return generate_ed25519_keypair()


@pytest.fixture
def app_client():
    """Provides an authenticated TestClient instance wired to FastAPI sidecar."""
    token = "TEST_IPC_SECRET_128BIT"
    fastapi_application = create_app(ipc_token=token)
    test_client = TestClient(fastapi_application)
    test_client.headers.update({"X-Tauri-IPC-Secret": token})
    return test_client


@pytest.fixture(scope="session")
def real_sqlite_kb(tmp_path_factory):
    """Builds an authentic SQLite module_kb.sqlite with real clinical data."""
    staging_directory = tmp_path_factory.mktemp("real_sqlite_kb")
    database_file_path = staging_directory / "module_kb.sqlite"

    builder = SQLiteModuleBuilder(database_file_path)

    # Insert 10 real ICD-10 conditions
    icd10_records = [
        ("I21.0", "ST elevation myocardial infarction of anterior wall", "IX", "I20-I25"),
        ("I21.1", "ST elevation myocardial infarction of inferior wall", "IX", "I20-I25"),
        ("I30.0", "Acute nonspecific pericarditis", "IX", "I30-I32"),
        ("I46.9", "Cardiac arrest, cause unspecified", "IX", "I46"),
        ("N18.3", "Chronic kidney disease, stage 3", "XIV", "N18"),
        ("E11.9", "Type 2 diabetes mellitus without complications", "IV", "E10-E14"),
        ("A41.9", "Sepsis, unspecified organism", "I", "A40-A41"),
        ("J18.9", "Pneumonia, unspecified organism", "X", "J12-J18"),
        ("J44.1", "Chronic obstructive pulmonary disease with acute exacerbation", "X", "J44"),
        ("I20.0", "Unstable angina", "IX", "I20-I25"),
    ]
    for code, desc, chap, blk in icd10_records:
        builder.insert_icd10(code, desc, chap, blk, is_leaf=True)

    # Insert 15 real ATC substances
    atc_records = [
        ("B01AC04", "Clopidogrel", "B", "B01", "B01A", "B01AC", True, ["CYP2C19"]),
        ("A02BC01", "Omeprazole", "A", "A02", "A02B", "A02BC", False, ["CYP2C19"]),
        ("C09AA03", "Lisinopril", "C", "C09", "C09A", "C09AA", False, []),
        ("C03AA03", "Hydrochlorothiazide", "C", "C03", "C03A", "C03AA", False, []),
        ("M01AE01", "Ibuprofen", "M", "M01", "M01A", "M01AE", False, ["CYP2C9"]),
        ("C01BD01", "Amiodarone", "C", "C01", "C01B", "C01BD", False, ["CYP3A4", "CYP2C8"]),
        ("J01MA02", "Ciprofloxacin", "J", "J01", "J01M", "J01MA", False, ["CYP1A2"]),
        ("C10AA01", "Simvastatin", "C", "C10", "C10A", "C10AA", False, ["CYP3A4"]),
        ("J01FA09", "Clarithromycin", "J", "J01", "J01F", "J01FA", False, ["CYP3A4"]),
        ("J05AF06", "Abacavir", "J", "J05", "J05A", "J05AF", False, []),
        ("B01AC06", "Aspirin", "B", "B01", "B01A", "B01AC", False, []),
        ("B01AC22", "Prasugrel", "B", "B01", "B01A", "B01AC", True, ["CYP3A4", "CYP2B6"]),
        ("A02BC02", "Pantoprazole", "A", "A02", "A02B", "A02BC", False, ["CYP2C19"]),
        ("L01BA01", "Methotrexate", "L", "L01", "L01B", "L01BA", False, []),
        ("N02BE01", "Paracetamol", "N", "N02", "N02B", "N02BE", False, ["CYP2E1"]),
    ]
    for atc_code, name, l1, l2, l3, l4, is_pro, enzymes in atc_records:
        builder.insert_atc(atc_code, name, l1, l2, l3, l4, is_prodrug=is_pro, cyp_enzymes=enzymes)
        builder.insert_substance(
            substance_id=atc_code,
            substance_name=name,
            atc_code=atc_code,
            is_prodrug=is_pro,
        )

    # Insert Clopidogrel + Omeprazole interaction
    builder.insert_drug_interaction(
        interaction_id="INT_CLOP_OMEP_01",
        substance_a="B01AC04",
        substance_b="A02BC01",
        severity_level=1,
        mechanism_description="Omeprazole inhibits CYP2C19 bioactivation of Clopidogrel.",
        clinical_alert_text="Blackbox Warning: Omeprazole reduces antiplatelet effect of Clopidogrel.",
    )

    # Insert HPO terms
    hpo_records = [
        ("HP:0001635", "Heart failure", "Inability of heart to pump blood", ["HP:0001626"], 4.2),
        ("HP:0001658", "Myocardial infarction", "Ischemic necrosis of heart muscle", ["HP:0001635"], 5.1),
        ("HP:0002094", "Dyspnea", "Shortness of breath", ["HP:0002086"], 3.5),
        ("HP:0001649", "Angina pectoris", "Chest pain due to ischemia", ["HP:0001635"], 4.8),
    ]
    for hpo_id, name, definition, ancestors, ic in hpo_records:
        builder.insert_hpo(hpo_id, name, definition, ancestors, ic)

    builder.build(database_file_path)
    return database_file_path


@pytest.fixture
def real_sqlite_pool(real_sqlite_kb):
    """Provides a real SqliteConnectionPool connected to real_sqlite_kb."""
    pool = SqliteConnectionPool(database_path=real_sqlite_kb, max_readers=8)
    yield pool
    pool.close()


@pytest.fixture
def hot_swap_controller(tmp_path):
    """Provides an authentic BlueGreenHotSwap instance."""
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    slot_a = data_dir / "slot_a.sqlite"
    slot_b = data_dir / "slot_b.sqlite"

    # Initialize empty databases for slots
    for slot_path in [slot_a, slot_b]:
        builder = SQLiteModuleBuilder(slot_path)
        builder.build(slot_path)

    pointer_file = data_dir / "active_db.json"
    manifest = {
        "active_slot": "blue",
        "active_path": str(slot_a),
        "updated_at_utc": "2026-10-31T00:00:00Z"
    }
    pointer_file.write_text(json.dumps(manifest), encoding="utf-8")

    return BlueGreenHotSwap(pointer_file_path=str(pointer_file))
