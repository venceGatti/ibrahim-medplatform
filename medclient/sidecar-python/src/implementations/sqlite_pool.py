"""Feature 20: SQLite WAL Read-Only Connection Pool."""
import sqlite3
import queue
import threading
from contextlib import contextmanager
from typing import Generator, Dict, Any, Optional
from ..interfaces.database import ISqliteConnectionPool
from ..base.exceptions import DatabaseLockedError


DEFAULT_MMAP_SIZE_64MB: int = 67108864  # 64 MB (ROA-13)
DEFAULT_MMAP_SIZE_256MB: int = 268435456  # 256 MB (ROA-09 / F20)


class SqliteConnectionPool(ISqliteConnectionPool):
    """High-concurrency read-only SQLite connection pool with controlled mmap."""

    DEFAULT_MMAP_SIZE_64MB: int = DEFAULT_MMAP_SIZE_64MB
    DEFAULT_MMAP_SIZE_256MB: int = DEFAULT_MMAP_SIZE_256MB

    def __init__(
        self,
        db_path: Optional[str] = None,
        max_size: int = 8,
        mmap_size: int = DEFAULT_MMAP_SIZE_256MB,
        cache_size: int = -16384,
        timeout_seconds: float = 5.0,
        database_path: Optional[str] = None,
        max_readers: Optional[int] = None,
    ) -> None:
        resolved_path = str(db_path if db_path is not None else (database_path if database_path is not None else ""))
        resolved_max = max_readers if max_readers is not None else max_size
        self._db_path = resolved_path
        self._max_size = resolved_max
        self._mmap_size = mmap_size
        self._cache_size = cache_size
        self._timeout_seconds = timeout_seconds

        self._pool: queue.Queue[sqlite3.Connection] = queue.Queue(maxsize=resolved_max)
        self._lock = threading.Lock()
        self._created_connections = 0
        self._active_connections = 0
        self._is_closed = False

        # Pre-populate pool
        for _ in range(self._max_size):
            conn = self._create_connection()
            self._pool.put(conn)
            self._created_connections += 1

    def _create_connection(self) -> sqlite3.Connection:
        """Create and configure a single read-only SQLite connection."""
        conn = sqlite3.connect(
            self._db_path,
            timeout=self._timeout_seconds,
            check_same_thread=False,
        )
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode = WAL;")
        cursor.execute(f"PRAGMA mmap_size = {self._mmap_size};")
        cursor.execute(f"PRAGMA cache_size = {self._cache_size};")
        cursor.execute("PRAGMA synchronous = NORMAL;")
        cursor.execute("PRAGMA temp_store = MEMORY;")
        cursor.execute("PRAGMA foreign_keys = ON;")
        try:
            cursor.execute("PRAGMA query_only = ON;")
        except sqlite3.OperationalError as query_only_error:
            import sys
            sys.stderr.write(f"[SqliteConnectionPool] PRAGMA query_only not supported: {query_only_error}\n")
        cursor.close()
        return conn

    @contextmanager
    def acquire(self) -> Generator[sqlite3.Connection, None, None]:
        """Borrow a connection from the pool, returning it upon block exit."""
        if self._is_closed:
            raise DatabaseLockedError("Connection pool is closed")

        try:
            conn = self._pool.get(timeout=self._timeout_seconds)
        except queue.Empty as err:
            raise DatabaseLockedError("Timed out waiting for pooled database connection") from err

        with self._lock:
            self._active_connections += 1

        try:
            yield conn
        finally:
            with self._lock:
                self._active_connections -= 1
            if not self._is_closed:
                self._pool.put(conn)
            else:
                conn.close()

    def close_all(self) -> None:
        """Drain and close all connections in the pool."""
        self._is_closed = True
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                conn.close()
            except queue.Empty:
                break

    def get_stats(self) -> Dict[str, Any]:
        """Return operational telemetry."""
        with self._lock:
            return {
                "active_connections": self._active_connections,
                "idle_connections": self._pool.qsize(),
                "max_size": self._max_size,
                "db_path": self._db_path,
                "mmap_size": self._mmap_size,
                "cache_size": self._cache_size,
                "is_closed": self._is_closed,
            }

    # Aliases for interface compatibility
    get_connection = acquire
    close = close_all


def sanitize_fts5_query(query: str) -> str:
    """Sanitize user query for SQLite FTS5 queries against malformed syntax."""
    if not query:
        return ""
    import re
    # Remove control characters
    cleaned = "".join(ch for ch in query if ord(ch) >= 32)
    if cleaned.count('"') % 2 != 0:
        cleaned = cleaned.replace('"', " ")
    tokens = cleaned.split()
    safe_tokens = []
    for t in tokens:
        raw_upper = re.sub(r"[^A-Za-z]", "", t).upper()
        if raw_upper in ["NEAR", "NOT", "AND", "OR"]:
            continue
        safe_tokens.append(t)
    return " ".join(safe_tokens)
