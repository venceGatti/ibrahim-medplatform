"""Shared helpers and fixtures for the MedPlatform test suite."""

import hashlib
import math
import os
import sys
from pathlib import Path
from typing import List, Tuple, Union

import blake3
import numpy as np
import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519
from starlette.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SIDECAR_DIR = PROJECT_ROOT / "medclient" / "sidecar-python"
FACTORY_DIR = PROJECT_ROOT / "medfactory"

for directory in (PROJECT_ROOT, SIDECAR_DIR, FACTORY_DIR):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from medclient.sidecar_python.src.api.server import create_app
from medclient.sidecar_python.src.base.sdui_models import (
    ClinicalSheetBlock as ClinicalSheetBlockContract,
    DrugSafetyBlock as DrugSafetyBlockContract,
    ExamSimulatorBlock as ExamSimulatorBlockContract,
    SymptomMatcherBlock as SymptomMatcherBlockContract,
)
from medclient.sidecar_python.src.implementations.blue_green_swap import BlueGreenHotSwap
from medclient.sidecar_python.src.implementations.sqlite_pool import SqliteConnectionPool
from medfactory.src.database.implementations.sqlite_module_builder import SQLiteModuleBuilder

EXACT_ZSTD_DICT_SIZE_BYTES = 114688


def compute_blake3_hash(data: bytes) -> str:
    """Return the BLAKE3 digest of the supplied bytes."""
    return blake3.blake3(data).hexdigest()


def compute_sha256_hash(data: bytes) -> str:
    """Return the SHA-256 digest of the supplied bytes."""
    return hashlib.sha256(data).hexdigest()


def generate_ed25519_keypair():
    """Generate a fresh Ed25519 key pair."""
    private_key = ed25519.Ed25519PrivateKey.generate()
    return private_key, private_key.public_key()


def compute_shock_index(heart_rate: float, systolic_blood_pressure: float) -> float:
    """Compute Shock Index = heart rate / systolic blood pressure."""
    if systolic_blood_pressure <= 0:
        raise ValueError("Systolic blood pressure must be strictly positive")
    if heart_rate <= 0:
        raise ValueError("Heart rate must be strictly positive")
    return round(float(heart_rate) / float(systolic_blood_pressure), 3)


def compute_qsofa_score(
    respiratory_rate: float,
    systolic_blood_pressure: float,
    altered_mentation: bool,
) -> int:
    """Compute the qSOFA score from its three criteria."""
    return (
        int(respiratory_rate >= 22.0)
        + int(systolic_blood_pressure <= 100.0)
        + int(bool(altered_mentation))
    )


def compute_ckd_epi_2021(
    serum_creatinine: float, age_years: float, is_female: bool
) -> float:
    """Delegate eGFR calculation to the production CKD-EPI implementation."""
    from medclient.sidecar_python.src.implementations.ckd_epi import CKDEPI2021Calculator

    return CKDEPI2021Calculator().compute_egfr(
        age=int(age_years),
        is_female=is_female,
        serum_creatinine_mg_dl=serum_creatinine,
    )


def log_sum_exp(logits: Union[np.ndarray, List[float]]) -> float:
    """Compute a numerically stable log-sum-exp."""
    values = np.asarray(logits, dtype=np.float64)
    if values.size == 0:
        raise ValueError("empty vector of logits provided")
    finite = np.isfinite(values)
    if not np.any(finite):
        return -float("inf")
    maximum = np.max(values[finite])
    return float(maximum + np.log(np.sum(np.exp(values[finite] - maximum))))


def compute_softmax_probabilities(logits: Union[np.ndarray, List[float]]) -> np.ndarray:
    """Normalize logits using the production softmax implementation."""
    from medclient.sidecar_python.src.implementations.softmax_normalizer import LogSumExpNormalizer

    return LogSumExpNormalizer().normalize_logits(logits)


def point_in_polygon_even_odd(
    point_u: float,
    point_v: float,
    polygon_vertices: List[Tuple[float, float]],
) -> bool:
    """Delegate point containment to the production hotspot implementation."""
    from medclient.sidecar_python.src.implementations.hotspot_evaluator import (
        point_in_polygon_even_odd as production_point_in_polygon,
    )

    return production_point_in_polygon(point_u, point_v, polygon_vertices)


def fsrs_calculate_retrievability(elapsed_days: float, stability: float) -> float:
    """Delegate retrievability calculation to the production FSRS scheduler."""
    if stability <= 0.0:
        raise ValueError("Stability parameter must be strictly positive")
    from medclient.sidecar_python.src.implementations.fsrs_scheduler import FSRSScheduler

    return FSRSScheduler().calculate_retrievability(elapsed_days, stability)


def pytest_configure(config):
    """Register test-suite markers."""
    for marker in (
        "tier1: Tier 1 feature coverage tests",
        "tier2: Tier 2 boundary and corner case tests",
        "tier3: Tier 3 pairwise integration tests",
        "tier4: Tier 4 clinical workload tests",
        "benchmark: Production SLA benchmarks",
    ):
        config.addinivalue_line("markers", marker)


@pytest.fixture
def authoritative_keypair():
    """Provide a newly generated Ed25519 key pair."""
    return generate_ed25519_keypair()


@pytest.fixture
def ed25519_keypair(authoritative_keypair):
    """Compatibility alias for tests that request an Ed25519 key-pair fixture."""
    return authoritative_keypair


@pytest.fixture
def app_client():
    """Provide an authenticated FastAPI test client."""
    token = "TEST_IPC_SECRET_128BIT"
    client = TestClient(create_app(ipc_token=token))
    client.headers.update({"X-Tauri-IPC-Secret": token})
    return client


@pytest.fixture(scope="session")
def real_sqlite_kb(tmp_path_factory):
    """Build a temporary production-schema SQLite database with representative data."""
    database_path = tmp_path_factory.mktemp("real_sqlite_kb") / "module_kb.sqlite"
    builder = SQLiteModuleBuilder(database_path)
    try:
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
        for code, description, chapter, block in icd10_records:
            builder.insert_icd10(code, description, chapter, block, is_leaf=True)

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
        for code, name, l1, l2, l3, l4, is_prodrug, enzymes in atc_records:
            builder.insert_atc(code, name, l1, l2, l3, l4, is_prodrug=is_prodrug, cyp_enzymes=enzymes)
            builder.insert_substance(code, name, atc_code=code, is_prodrug=is_prodrug)

        hpo_records = [
            ("HP:0001635", "Heart failure", "Inability of heart to pump blood", ["HP:0001626"], 4.2),
            ("HP:0001658", "Myocardial infarction", "Ischemic necrosis of heart muscle", ["HP:0001635"], 5.1),
            ("HP:0002094", "Dyspnea", "Shortness of breath", ["HP:0002086"], 3.5),
            ("HP:0001649", "Angina pectoris", "Chest pain due to ischemia", ["HP:0001635"], 4.8),
        ]
        for hpo_id, name, definition, ancestors, information_content in hpo_records:
            builder.insert_hpo(hpo_id, name, definition, ancestors, information_content)

        builder.insert_drug_interaction(
            interaction_id="INT_CLOP_OMEP_01",
            substance_a="B01AC04",
            substance_b="A02BC01",
            severity_level=1,
            mechanism_description="Omeprazole inhibits CYP2C19 bioactivation of Clopidogrel.",
            clinical_alert_text="Omeprazole may reduce the antiplatelet effect of Clopidogrel.",
        )
        builder.build(database_path)
    finally:
        # build() closes the builder on success; close() is safe after a build failure too.
        if not getattr(builder, "_is_closed", True):
            builder.close()

    return str(database_path)


@pytest.fixture
def real_sqlite_pool(real_sqlite_kb):
    """Provide a connection pool for the generated clinical knowledge base."""
    pool = SqliteConnectionPool(database_path=real_sqlite_kb, max_readers=8)
    try:
        yield pool
    finally:
        pool.close()


@pytest.fixture
def hot_swap_controller(tmp_path):
    """Provide a blue/green controller initialized with two valid SQLite slots."""
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    slot_a = data_dir / "slot_a.sqlite"
    slot_b = data_dir / "slot_b.sqlite"

    for slot_path in (slot_a, slot_b):
        builder = SQLiteModuleBuilder(slot_path)
        builder.build(slot_path)

    pointer_file = data_dir / "active_db.json"
    pointer_file.write_text(
        __import__("json").dumps(
            {
                "active_slot": "blue",
                "active_path": str(slot_a),
                "updated_at_utc": "2026-10-31T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    return BlueGreenHotSwap(pointer_file_path=str(pointer_file))
