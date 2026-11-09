"""Feature 16: Reverse watchdog thread monitoring parent process PID."""
import os
import sys
import time
import threading
from typing import Optional
from ..interfaces.watchdog import IReverseWatchdog


class ReverseWatchdog(IReverseWatchdog):
    """Monitors parent PID using Win32 WaitForSingleObject and exits on parent termination."""

    def __init__(self, poll_interval_ms: int = 500) -> None:
        self._poll_interval_ms = poll_interval_ms
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._parent_pid: Optional[int] = None

    def start(self, parent_pid: int) -> None:
        """Start reverse watchdog thread."""
        if parent_pid <= 0:
            return
        self._parent_pid = parent_pid
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run_watchdog,
            args=(parent_pid,),
            daemon=True,
            name="reverse-watchdog-thread",
        )
        self._thread.start()

    def stop(self) -> None:
        """Signal watchdog thread to stop."""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def is_alive(self) -> bool:
        """Check if watchdog thread is currently running."""
        return self._thread is not None and self._thread.is_alive()

    def _run_watchdog(self, parent_pid: int) -> None:
        """Execute platform-specific process wait."""
        if sys.platform == "win32":
            self._run_windows_watchdog(parent_pid)
        else:
            self._run_posix_watchdog(parent_pid)

    def _run_windows_watchdog(self, parent_pid: int) -> None:
        """Win32 OpenProcess + WaitForSingleObject loop."""
        import ctypes
        from ctypes import wintypes

        SYNCHRONIZE = 0x00100000
        WAIT_OBJECT_0 = 0x00000000
        kernel32 = getattr(ctypes, "WinDLL", ctypes.CDLL)("kernel32", use_last_error=True)

        kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel32.OpenProcess.restype = wintypes.HANDLE
        kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        kernel32.WaitForSingleObject.restype = wintypes.DWORD
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.restype = wintypes.BOOL

        handle = kernel32.OpenProcess(SYNCHRONIZE, False, parent_pid)

        if not handle:
            # Parent process already terminated or handle unavailable
            os._exit(1)

        try:
            while not self._stop_event.is_set():
                wait_status = kernel32.WaitForSingleObject(handle, self._poll_interval_ms)
                if wait_status == WAIT_OBJECT_0:
                    kernel32.CloseHandle(handle)
                    os._exit(0)
        finally:
            if handle:
                kernel32.CloseHandle(handle)

    def _run_posix_watchdog(self, parent_pid: int) -> None:
        """Posix fallback polling parent PID existence via os.kill."""
        while not self._stop_event.is_set():
            try:
                os.kill(parent_pid, 0)
            except OSError:
                os._exit(0)
            time.sleep(self._poll_interval_ms / 1000.0)
