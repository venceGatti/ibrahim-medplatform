"""Interfaces for SQLite WAL Connection Pool and Blue/Green Hot Swap."""
from abc import ABC, abstractmethod
import sqlite3
from typing import ContextManager, Dict, Any, Optional


class ISqliteConnectionPool(ABC):
    """High-concurrency read-only SQLite connection pool."""

    @abstractmethod
    def acquire(self) -> ContextManager[sqlite3.Connection]:
        """Acquire a read-only connection configured with WAL and mmap."""
        raise NotImplementedError("Subclasses must implement acquire")

    @abstractmethod
    def close_all(self) -> None:
        """Close all pooled connections and drain."""
        raise NotImplementedError("Subclasses must implement close_all")

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Return pool telemetry metrics (active, idle, path)."""
        raise NotImplementedError("Subclasses must implement get_stats")


class IBlueGreenHotSwap(ABC):
    """Atomic database hot swap controller."""

    @abstractmethod
    def get_active_slot(self) -> str:
        """Return current active slot name ('blue' or 'green')."""
        raise NotImplementedError("Subclasses must implement get_active_slot")

    @abstractmethod
    def get_active_db_path(self) -> str:
        """Return absolute path to current active database."""
        raise NotImplementedError("Subclasses must implement get_active_db_path")

    @abstractmethod
    def swap_to_slot(self, target_slot: str, target_db_path: str) -> bool:
        """Atomically swap active slot and repoint active_db.json."""
        raise NotImplementedError("Subclasses must implement swap_to_slot")


class IUserStateStore(ABC):
    """Manages student state, review logs, and bookmarks in user_state.sqlite (ROA-13)."""

    @abstractmethod
    def upsert_card(self, card_dict: Dict[str, Any]) -> None:
        """Insert or update FSRS card state."""
        raise NotImplementedError("Subclasses must implement upsert_card")

    @abstractmethod
    def get_card(self, concept_uid: str) -> Optional[Dict[str, Any]]:
        """Retrieve single FSRS card by concept identifier."""
        raise NotImplementedError("Subclasses must implement get_card")

    @abstractmethod
    def record_review_log(self, log_dict: Dict[str, Any]) -> None:
        """Record review outcome log entry."""
        raise NotImplementedError("Subclasses must implement record_review_log")

    @abstractmethod
    def save_exam_session(self, session_dict: Dict[str, Any]) -> None:
        """Persist completed or ongoing exam session."""
        raise NotImplementedError("Subclasses must implement save_exam_session")

    @abstractmethod
    def add_bookmark(self, bookmark_id: str, sheet_id: str, notes: Optional[str] = None) -> None:
        """Create or update a user bookmark for a clinical sheet."""
        raise NotImplementedError("Subclasses must implement add_bookmark")

    @abstractmethod
    def close(self) -> None:
        """Close connection to user_state.sqlite."""
        raise NotImplementedError("Subclasses must implement close")
