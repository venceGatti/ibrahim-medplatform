"""Tests for Storage, Reverse Watchdog, Blue/Green Swap, and Agentic API."""
import os
import tempfile
import sqlite3
import pytest
from fastapi.testclient import TestClient

from src.implementations.reverse_watchdog import ReverseWatchdog
from src.implementations.sqlite_pool import SqliteConnectionPool
from src.implementations.blue_green_swap import BlueGreenHotSwap
from src.api.server import create_app


def test_reverse_watchdog_lifecycle():
    """Verify watchdog starts, reports status, and stops cleanly."""
    watchdog = ReverseWatchdog(poll_interval_ms=100)
    # Using current PID for non-terminating safe lifecycle check
    watchdog.start(os.getpid())
    assert watchdog.is_alive() is True
    watchdog.stop()
    assert watchdog.is_alive() is False


def test_sqlite_wal_pool():
    """Verify connection pool acquires WAL connections and maintains stats."""
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as sqlite_file_descriptor:
        db_path = sqlite_file_descriptor.name

    try:
        # Initialize schema
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT);")
        conn.execute("INSERT INTO test VALUES (1, 'alpha');")
        conn.commit()
        conn.close()

        pool = SqliteConnectionPool(db_path, max_size=3)
        stats = pool.get_stats()
        assert stats["max_size"] == 3
        assert stats["idle_connections"] == 3

        with pool.acquire() as c:
            row = c.execute("SELECT name FROM test WHERE id = 1;").fetchone()
            assert row["name"] == "alpha"
            # Verify PRAGMA journal_mode is WAL
            wal_mode = c.execute("PRAGMA journal_mode;").fetchone()[0]
            assert wal_mode.lower() == "wal"

        pool.close_all()
        assert pool.get_stats()["is_closed"] is True
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_blue_green_atomic_swap():
    """Verify atomic pointer swap between blue and green database slots."""
    with tempfile.TemporaryDirectory() as sandbox_directory:
        pointer_path = os.path.join(sandbox_directory, "active_db.json")
        blue_db = os.path.join(sandbox_directory, "master_blue.sqlite")
        green_db = os.path.join(sandbox_directory, "master_green.sqlite")

        # Create both databases with tables
        for db in [blue_db, green_db]:
            conn = sqlite3.connect(db)
            conn.execute("CREATE TABLE status (slot TEXT);")
            conn.commit()
            conn.close()

        hotswap = BlueGreenHotSwap(pointer_path)
        # Default fallback
        assert hotswap.get_active_slot() == "blue"

        # Swap to green
        success = hotswap.swap_to_slot("green", green_db)
        assert success is True
        assert hotswap.get_active_slot() == "green"
        assert hotswap.get_active_db_path() == os.path.abspath(green_db)

        # Swap back to blue
        success2 = hotswap.swap_to_slot("blue", blue_db)
        assert success2 is True
        assert hotswap.get_active_slot() == "blue"


def test_agentic_api_endpoints():
    """Verify /agent/health, /agent/state, /agent/execute, and /agent/schema with authentication."""
    token = "test-token-uuid-1234"
    app = create_app(ipc_token=token)
    client = TestClient(app)

    # 1. Without auth header -> 403 Forbidden
    res = client.get("/agent/health")
    assert res.status_code == 403

    # 2. With valid auth header -> 200 OK
    headers = {"X-Tauri-IPC-Secret": token}
    res_health = client.get("/agent/health", headers=headers)
    assert res_health.status_code == 200
    data = res_health.json()
    assert data["status"] == "healthy"
    assert "rss_mb" in data

    # 3. /agent/state
    res_state = client.get("/agent/state", headers=headers)
    assert res_state.status_code == 200
    state_data = res_state.json()
    assert "active_slot" in state_data

    # 4. /agent/schema
    res_schema = client.get("/agent/schema", headers=headers)
    assert res_schema.status_code == 200
    schema_data = res_schema.json()
    assert "supported_actions" in schema_data
    assert "EVALUATE_RED_FLAGS" in schema_data["supported_actions"]

    # 5. /agent/execute
    exec_payload = {
        "action_type": "CALCULATE_EGFR",
        "payload": {
            "age": 60,
            "is_female": False,
            "serum_creatinine_mg_dl": 1.2,
        },
    }
    res_exec = client.post("/agent/execute", json=exec_payload, headers=headers)
    assert res_exec.status_code == 200
    exec_data = res_exec.json()
    assert exec_data["success"] is True
    assert "egfr" in exec_data["result"]
    assert exec_data["result"]["egfr"] > 0


def test_user_state_store_strict_schema_and_operations():
    """Verify UserStateStore creates strictly typed tables in WAL mode and supports complete lifecycle (ROA-13, ROA-20)."""
    from src.implementations.user_state_store import UserStateStore

    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as sqlite_file_descriptor:
        db_path = sqlite_file_descriptor.name

    try:
        store = UserStateStore(db_path)
        with store._conn as conn:
            mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
            assert mode.lower() == "wal"

        # 1. Upsert card & retrieve
        store.upsert_card({
            "card_id": "card_angina_01",
            "concept_uid": "uid_angina_01",
            "state": "REVIEW",
            "stability": 3.5,
            "difficulty": 4.5,
            "elapsed_days": 1.0,
            "scheduled_days": 4,
            "reps": 2,
            "lapses": 0,
            "due_timestamp": 1770000000,
            "last_review_timestamp": 1769900000,
        })
        card = store.get_card("uid_angina_01")
        assert card is not None
        assert card["card_id"] == "card_angina_01"
        assert card["state"] == 2
        assert card["difficulty"] == 4.5

        # 2. Due cards
        due_cards = store.get_due_cards(cutoff_timestamp=1770000001)
        assert len(due_cards) == 1
        assert due_cards[0]["concept_uid"] == "uid_angina_01"

        # 3. Review log with foreign key
        store.record_review_log({
            "log_id": "log_001",
            "card_id": "card_angina_01",
            "rating": 3,
            "review_timestamp": 1769900000,
            "elapsed_days": 1.0,
            "scheduled_days": 4,
            "state_before": 1,
            "stability_after": 3.5,
            "difficulty_after": 4.5,
        })

        # 4. Exam session
        store.save_exam_session({
            "session_id": "session_stemi_01",
            "started_at_utc": "2026-10-31T10:00:00Z",
            "completed_at_utc": "2026-10-31T10:15:00Z",
            "item_type": "MCQ",
            "score_thirtieths": 28.5,
            "is_lethal_short_circuit": False,
            "telemetry_json": {"time_spent_sec": 900},
        })

        # 5. Bookmarks
        store.add_bookmark("bm_01", "sheet_angina", notes="Important pearls")
        bookmarks = store.get_bookmarks()
        assert len(bookmarks) == 1
        assert bookmarks[0]["sheet_id"] == "sheet_angina"
        assert bookmarks[0]["annotation_markdown"] == "Important pearls"

        store.close()
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)

