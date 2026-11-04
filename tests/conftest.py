import pytest
import sqlite3
import tempfile
import os

@pytest.fixture(scope="session")
def real_sqlite_kb():
    # Creazione di un database temporaneo per i test SLA
    fd, path = tempfile.mkstemp()
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

    os.close(fd)
    os.remove(path)
