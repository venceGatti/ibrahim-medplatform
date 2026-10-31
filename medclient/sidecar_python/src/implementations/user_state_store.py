"""Feature 13: Physical Isolation of user_state.sqlite with STRICT Tables (ROA-13, ROA-20)."""
import os
import json
import sqlite3
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from ..interfaces.database import IUserStateStore


def parse_timestamp_to_epoch(timestamp_value: Any) -> int:
    """Normalize datetime, ISO 8601 string, or numeric epoch to integer seconds."""
    if timestamp_value is None:
        return int(datetime.now(timezone.utc).timestamp())
    if isinstance(timestamp_value, (int, float)):
        return int(timestamp_value)
    if isinstance(timestamp_value, datetime):
        return int(timestamp_value.astimezone(timezone.utc).timestamp())
    if isinstance(timestamp_value, str):
        try:
            return int(float(timestamp_value))
        except ValueError:
            parsed = datetime.fromisoformat(timestamp_value.replace("Z", "+00:00"))
            return int(parsed.astimezone(timezone.utc).timestamp())
    return int(datetime.now(timezone.utc).timestamp())


def parse_state_to_integer(state_value: Any) -> int:
    """Map state representation to integer in range 0..3."""
    if isinstance(state_value, int) and 0 <= state_value <= 3:
        return state_value
    state_str = str(state_value).upper()
    return 1 if "LEARN" in state_str else (3 if "RELEARN" in state_str else (2 if "REVIEW" in state_str else 0))


class UserStateStore(IUserStateStore):
    """Manages mutable user progress in user_state.sqlite isolated from read-only module_kb."""

    def __init__(self, database_path: str, timeout_seconds: float = 10.0) -> None:
        self.database_path = str(database_path)
        self.timeout_seconds = timeout_seconds
        parent_directory = os.path.dirname(os.path.abspath(self.database_path))
        if parent_directory and not os.path.exists(parent_directory):
            os.makedirs(parent_directory, exist_ok=True)
        self._conn = sqlite3.connect(self.database_path, timeout=self.timeout_seconds, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize WAL mode and create four strictly-typed user state tables per ROA-20."""
        cursor = self._conn.cursor()
        cursor.execute("PRAGMA journal_mode = WAL;")
        cursor.execute("PRAGMA synchronous = NORMAL;")
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS fsrs_cards (
                card_id TEXT PRIMARY KEY NOT NULL, concept_uid TEXT NOT NULL UNIQUE,
                state INTEGER NOT NULL DEFAULT 0 CHECK (state IN (0, 1, 2, 3)), stability REAL NOT NULL DEFAULT 0.0,
                difficulty REAL NOT NULL DEFAULT 5.0 CHECK (difficulty >= 1.0 AND difficulty <= 10.0),
                elapsed_days REAL NOT NULL DEFAULT 0.0, scheduled_days INTEGER NOT NULL DEFAULT 0,
                reps INTEGER NOT NULL DEFAULT 0, lapses INTEGER NOT NULL DEFAULT 0,
                due_timestamp INTEGER NOT NULL, last_review_timestamp INTEGER
            ) STRICT;
            CREATE TABLE IF NOT EXISTS review_logs (
                log_id TEXT PRIMARY KEY NOT NULL, card_id TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK (rating IN (1, 2, 3, 4)), review_timestamp INTEGER NOT NULL,
                elapsed_days REAL NOT NULL, scheduled_days INTEGER NOT NULL,
                state_before INTEGER NOT NULL, stability_after REAL NOT NULL, difficulty_after REAL NOT NULL,
                FOREIGN KEY (card_id) REFERENCES fsrs_cards(card_id) ON DELETE CASCADE
            ) STRICT;
            CREATE TABLE IF NOT EXISTS exam_sessions (
                session_id TEXT PRIMARY KEY NOT NULL, started_at_utc TEXT NOT NULL, completed_at_utc TEXT,
                item_type TEXT NOT NULL, score_thirtieths REAL NOT NULL CHECK (score_thirtieths >= 0.0 AND score_thirtieths <= 30.0),
                is_lethal_short_circuit INTEGER NOT NULL DEFAULT 0, telemetry_json TEXT NOT NULL
            ) STRICT;
            CREATE TABLE IF NOT EXISTS user_bookmarks (
                bookmark_id TEXT PRIMARY KEY NOT NULL, sheet_id TEXT NOT NULL,
                created_at_utc TEXT NOT NULL, annotation_markdown TEXT NOT NULL DEFAULT ''
            ) STRICT;
            """
        )
        self._conn.commit()
        cursor.close()

    def upsert_card(self, card_dict: Dict[str, Any]) -> None:
        """Insert or replace an FSRS card record adhering strictly to ROA-20."""
        target_uid = str(card_dict.get("concept_uid", ""))
        card_id = str(card_dict.get("card_id") or f"card_{target_uid}")
        state_int = parse_state_to_integer(card_dict.get("state", 0))
        stability_val = max(0.0, float(card_dict.get("stability", 0.0)))
        difficulty_val = max(1.0, min(10.0, float(card_dict.get("difficulty", 5.0))))
        elapsed_val = max(0.0, float(card_dict.get("elapsed_days", 0.0)))
        scheduled_int = max(0, int(round(float(card_dict.get("scheduled_days", 0)))))
        reps_int = max(0, int(card_dict.get("reps", 0)))
        lapses_int = max(0, int(card_dict.get("lapses", 0)))
        due_epoch = parse_timestamp_to_epoch(card_dict.get("due_timestamp") or card_dict.get("due_date"))
        last_rev_raw = card_dict.get("last_review_timestamp") or card_dict.get("last_review")
        last_rev_epoch = parse_timestamp_to_epoch(last_rev_raw) if last_rev_raw else None

        cursor = self._conn.cursor()
        cursor.execute(
            """
            INSERT INTO fsrs_cards (
                card_id, concept_uid, state, stability, difficulty,
                elapsed_days, scheduled_days, reps, lapses, due_timestamp, last_review_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(card_id) DO UPDATE SET
                concept_uid=excluded.concept_uid, state=excluded.state, stability=excluded.stability,
                difficulty=excluded.difficulty, elapsed_days=excluded.elapsed_days, scheduled_days=excluded.scheduled_days,
                reps=excluded.reps, lapses=excluded.lapses, due_timestamp=excluded.due_timestamp,
                last_review_timestamp=excluded.last_review_timestamp;
            """,
            (card_id, target_uid, state_int, stability_val, difficulty_val, elapsed_val, scheduled_int, reps_int, lapses_int, due_epoch, last_rev_epoch),
        )
        self._conn.commit()
        cursor.close()

    def get_card(self, concept_uid: str) -> Optional[Dict[str, Any]]:
        """Retrieve single FSRS card state by concept UID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM fsrs_cards WHERE concept_uid = ?;", (concept_uid,))
        row = cursor.fetchone()
        cursor.close()
        if not row:
            return None
        rec = dict(row)
        rec["due_date"] = datetime.fromtimestamp(rec["due_timestamp"], tz=timezone.utc).isoformat()
        rec["last_review"] = datetime.fromtimestamp(rec["last_review_timestamp"], tz=timezone.utc).isoformat() if rec["last_review_timestamp"] else None
        return rec

    def get_due_cards(self, cutoff_timestamp: Optional[int] = None) -> List[Dict[str, Any]]:
        """Query cards scheduled for review before cutoff timestamp."""
        effective_cutoff = cutoff_timestamp if cutoff_timestamp is not None else int(datetime.now(timezone.utc).timestamp())
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM fsrs_cards WHERE due_timestamp <= ? ORDER BY due_timestamp ASC;", (effective_cutoff,))
        rows = cursor.fetchall()
        cursor.close()
        results: List[Dict[str, Any]] = []
        for r in rows:
            rec = dict(r)
            rec["due_date"] = datetime.fromtimestamp(rec["due_timestamp"], tz=timezone.utc).isoformat()
            rec["last_review"] = datetime.fromtimestamp(rec["last_review_timestamp"], tz=timezone.utc).isoformat() if rec["last_review_timestamp"] else None
            results.append(rec)
        return results

    def record_review_log(self, log_dict: Dict[str, Any]) -> None:
        """Append review log for docimological analytics."""
        target_card_id = str(log_dict.get("card_id", "")) or f"card_{log_dict.get('concept_uid', '')}"
        cursor = self._conn.cursor()
        cursor.execute(
            """
            INSERT INTO review_logs (
                log_id, card_id, rating, review_timestamp, elapsed_days, scheduled_days, state_before, stability_after, difficulty_after
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                str(log_dict["log_id"]), target_card_id, int(log_dict["rating"]),
                parse_timestamp_to_epoch(log_dict.get("review_timestamp") or log_dict.get("review_time")),
                float(log_dict.get("elapsed_days", 0.0)), int(round(float(log_dict.get("scheduled_days", 0)))),
                parse_state_to_integer(log_dict.get("state_before", 0)), float(log_dict.get("stability_after", 0.0)),
                float(log_dict.get("difficulty_after", 5.0)),
            ),
        )
        self._conn.commit()
        cursor.close()

    def save_exam_session(self, session_dict: Dict[str, Any]) -> None:
        """Persist finished or ongoing clinical exam session."""
        started_utc = str(session_dict.get("started_at_utc") or session_dict.get("started_at") or datetime.now(timezone.utc).isoformat())
        completed_raw = session_dict.get("completed_at_utc") or session_dict.get("completed_at")
        item_type = str(session_dict.get("item_type", "DAG_SCENARIO"))
        raw_score = float(session_dict.get("score_thirtieths", session_dict.get("score", 0.0)))
        score_thirtieths = max(0.0, min(30.0, raw_score))
        is_lethal = 1 if session_dict.get("is_lethal_short_circuit", False) else 0
        raw_telemetry = session_dict.get("telemetry_json") or session_dict.get("telemetry") or {}
        telemetry_str = raw_telemetry if isinstance(raw_telemetry, str) else json.dumps(raw_telemetry)

        cursor = self._conn.cursor()
        cursor.execute(
            """
            INSERT INTO exam_sessions (
                session_id, started_at_utc, completed_at_utc, item_type, score_thirtieths, is_lethal_short_circuit, telemetry_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                started_at_utc=excluded.started_at_utc, completed_at_utc=excluded.completed_at_utc, item_type=excluded.item_type,
                score_thirtieths=excluded.score_thirtieths, is_lethal_short_circuit=excluded.is_lethal_short_circuit,
                telemetry_json=excluded.telemetry_json;
            """,
            (str(session_dict["session_id"]), started_utc, str(completed_raw) if completed_raw else None, item_type, score_thirtieths, is_lethal, telemetry_str),
        )
        self._conn.commit()
        cursor.close()

    def add_bookmark(self, bookmark_id: str, sheet_id: str, notes: Optional[str] = None, annotation_markdown: Optional[str] = None) -> None:
        """Bookmark a clinical sheet for fast user access."""
        cursor = self._conn.cursor()
        now_iso = datetime.now(timezone.utc).isoformat()
        annotation_text = str(annotation_markdown if annotation_markdown is not None else (notes or ""))
        cursor.execute(
            """
            INSERT INTO user_bookmarks (bookmark_id, sheet_id, created_at_utc, annotation_markdown) VALUES (?, ?, ?, ?)
            ON CONFLICT(bookmark_id) DO UPDATE SET
                sheet_id=excluded.sheet_id, created_at_utc=excluded.created_at_utc, annotation_markdown=excluded.annotation_markdown;
            """,
            (bookmark_id, sheet_id, now_iso, annotation_text),
        )
        self._conn.commit()
        cursor.close()

    def get_bookmarks(self) -> List[Dict[str, Any]]:
        """Retrieve all active bookmarks."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM user_bookmarks ORDER BY created_at_utc DESC;")
        rows = cursor.fetchall()
        cursor.close()
        return [dict(r) for r in rows]

    def close(self) -> None:
        """Close connection to user_state database."""
        self._conn.close()


