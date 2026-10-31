"""Feature 21: Blue/Green atomic database hot swap controller."""
import json
import os
import sys
import sqlite3
from datetime import datetime, timezone
from typing import Optional
from ..interfaces.database import IBlueGreenHotSwap
from ..base.database_models import ActiveDbPointer
from ..base.exceptions import HotSwapVerificationError, DatabaseIntegrityError


class BlueGreenHotSwap(IBlueGreenHotSwap):
    """Manages atomic pointer swap between Blue and Green database slots."""

    def __init__(self, pointer_file_path: str) -> None:
        self._pointer_file_path = os.path.abspath(pointer_file_path)
        os.makedirs(os.path.dirname(self._pointer_file_path), exist_ok=True)
        self._cached_pointer: Optional[ActiveDbPointer] = None
        self._load_pointer()

    def _load_pointer(self) -> None:
        """Read and cache current active_db.json."""
        if os.path.exists(self._pointer_file_path):
            try:
                with open(self._pointer_file_path, "r", encoding="utf-8") as f:
                    active_db_manifest = json.load(f)
                    self._cached_pointer = ActiveDbPointer(**active_db_manifest)
            except Exception as load_error:
                sys.stderr.write(f"[BlueGreenHotSwap] Warning: Failed to parse pointer file: {load_error}. Falling back to default slot.\n")
                self._cached_pointer = None

    def get_active_slot(self) -> str:
        """Return active slot name ('blue' or 'green')."""
        if not self._cached_pointer:
            self._load_pointer()
        return self._cached_pointer.active_slot if self._cached_pointer else "blue"

    def get_active_db_path(self) -> str:
        """Return path to active database."""
        if not self._cached_pointer:
            self._load_pointer()
        return self._cached_pointer.active_path if self._cached_pointer else ""

    def verify_database_integrity(self, target_db_path: str) -> None:
        """Validate database using PRAGMA integrity_check."""
        if not os.path.exists(target_db_path):
            raise HotSwapVerificationError(f"Target database file not found: {target_db_path}")

        try:
            conn = sqlite3.connect(target_db_path, timeout=5.0)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check;")
            row = cursor.fetchone()
            conn.close()
            if not row or row[0].lower() != "ok":
                raise DatabaseIntegrityError(f"Integrity check failed: {row}")
        except Exception as err:
            raise HotSwapVerificationError(f"Database verification failed: {err}") from err

    def swap_to_slot(self, target_slot: str, target_db_path: str) -> bool:
        """Atomically swap active slot via atomic file replacement."""
        normalized_target_path = os.path.abspath(target_db_path)
        self.verify_database_integrity(normalized_target_path)

        now_utc = datetime.now(timezone.utc).isoformat()
        new_pointer = ActiveDbPointer(
            active_slot=target_slot,
            active_path=normalized_target_path,
            updated_at_utc=now_utc,
        )

        staging_pointer_path = f"{self._pointer_file_path}.staging_{os.getpid()}"
        with open(staging_pointer_path, "w", encoding="utf-8") as f:
            json.dump(new_pointer.model_dump(), f, indent=2)

        self._atomic_replace_file(staging_pointer_path, self._pointer_file_path)
        self._cached_pointer = new_pointer
        return True

    def _atomic_replace_file(self, source_path: str, destination_path: str) -> None:
        """Perform atomic replace on Windows via MoveFileExW or os.replace."""
        if sys.platform == "win32":
            import ctypes

            MOVEFILE_REPLACE_EXISTING = 0x00000001
            MOVEFILE_WRITE_THROUGH = 0x00000008
            flags = MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH

            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel32.MoveFileExW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32]
            kernel32.MoveFileExW.restype = ctypes.c_bool

            success = kernel32.MoveFileExW(source_path, destination_path, flags)
            if not success:
                err_code = ctypes.get_last_error()
                # Fallback to os.replace if win32 API failed
                try:
                    os.replace(source_path, destination_path)
                except Exception as fallback_err:
                    raise OSError(f"MoveFileExW failed (code {err_code}): {fallback_err}") from fallback_err
        else:
            os.replace(source_path, destination_path)
