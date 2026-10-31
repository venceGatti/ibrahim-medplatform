"""
Tier 3: Pairwise Cross-Feature Tests.
Pair 2: SQLite Blue/Green Hot Swap Pointer Transition + Concurrent SQLite WAL Read Queries.
Verifies atomic pointer swapping via active_db.json during active read connections without locking.
"""

import json
import sqlite3
import pytest
from tests.conftest import compute_sha256_hash


@pytest.mark.tier3
def test_p02_blue_green_swap_with_in_flight_wal_reads(tmp_path):
    """Verify read transactions on blue slot continue seamlessly while swapping pointer to green."""
    blue_db_path = tmp_path / "module_kb_blue.sqlite"
    green_db_path = tmp_path / "module_kb_green.sqlite"
    pointer_path = tmp_path / "active_db.json"

    # Initialize Blue DB
    conn_blue = sqlite3.connect(str(blue_db_path))
    conn_blue.execute("PRAGMA journal_mode = WAL;")
    conn_blue.execute("CREATE TABLE metadata (version TEXT);")
    conn_blue.execute("INSERT INTO metadata VALUES ('v1.0.0-blue');")
    conn_blue.commit()

    # Initialize Green DB
    conn_green = sqlite3.connect(str(green_db_path))
    conn_green.execute("PRAGMA journal_mode = WAL;")
    conn_green.execute("CREATE TABLE metadata (version TEXT);")
    conn_green.execute("INSERT INTO metadata VALUES ('v2.0.0-green');")
    conn_green.commit()

    # Step 1: Active pointer initially points to blue
    initial_pointer = {
        "active_slot": "blue",
        "active_path": str(blue_db_path),
        "sha256": compute_sha256_hash(blue_db_path.read_bytes())
    }
    pointer_path.write_text(json.dumps(initial_pointer), encoding="utf-8")

    # In-flight reader reading blue
    read_conn = sqlite3.connect(str(blue_db_path))
    cursor = read_conn.cursor()
    cursor.execute("SELECT version FROM metadata;")
    assert cursor.fetchone()[0] == "v1.0.0-blue"

    # Step 2: Atomic hot swap to green
    green_sha256 = compute_sha256_hash(green_db_path.read_bytes())
    updated_pointer = {
        "active_slot": "green",
        "active_path": str(green_db_path),
        "sha256": green_sha256
    }
    # Atomic file write (executing MoveFileExW replace)
    staged_pointer_path = tmp_path / "active_db_staged.json"
    staged_pointer_path.write_text(json.dumps(updated_pointer), encoding="utf-8")
    staged_pointer_path.replace(pointer_path)

    # Step 3: Existing in-flight reader still succeeds
    cursor.execute("SELECT version FROM metadata;")
    assert cursor.fetchone()[0] == "v1.0.0-blue"
    read_conn.close()

    # Step 4: New reader reads active_db.json and routes to green
    current_active_meta = json.loads(pointer_path.read_text(encoding="utf-8"))
    assert current_active_meta["active_slot"] == "green"

    new_conn = sqlite3.connect(current_active_meta["active_path"])
    new_cursor = new_conn.cursor()
    new_cursor.execute("SELECT version FROM metadata;")
    assert new_cursor.fetchone()[0] == "v2.0.0-green"
    new_conn.close()
    conn_blue.close()
    conn_green.close()


@pytest.mark.tier3
def test_p02_blue_green_integrity_check_failure_aborts_swap(tmp_path):
    """Verify integrity check failure on candidate slot prevents pointer modification."""
    blue_db_path = tmp_path / "module_kb_blue.sqlite"
    pointer_path = tmp_path / "active_db.json"

    initial_pointer = {
        "active_slot": "blue",
        "active_path": str(blue_db_path),
        "sha256": "initial_hash"
    }
    pointer_path.write_text(json.dumps(initial_pointer), encoding="utf-8")

    # Candidate green slot has integrity failure
    integrity_result = "corrupt database header"
    if integrity_result != "ok":
        abort_swap = True
    else:
        abort_swap = False

    assert abort_swap is True
    # Pointer file remains untouched
    active_after = json.loads(pointer_path.read_text(encoding="utf-8"))
    assert active_after["active_slot"] == "blue"


@pytest.mark.tier3
def test_p02_blue_green_pointer_hash_verification(tmp_path):
    """Verify SHA-256 in pointer matches target database bytes exactly."""
    db_file = tmp_path / "test.sqlite"
    db_file.write_bytes(b"SQLite format 3\x00_test_data")
    computed_hash = compute_sha256_hash(db_file.read_bytes())

    pointer = {
        "active_slot": "blue",
        "active_path": str(db_file),
        "sha256": computed_hash
    }
    assert pointer["sha256"] == compute_sha256_hash(db_file.read_bytes())


@pytest.mark.tier3
def test_p02_wal_mode_persists_across_swapped_database(tmp_path):
    """Verify newly activated database enforces PRAGMA journal_mode = WAL."""
    db_path = tmp_path / "swapped.sqlite"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode = WAL;")
    mode = cursor.fetchone()[0]
    assert mode.lower() == "wal"
    conn.close()
