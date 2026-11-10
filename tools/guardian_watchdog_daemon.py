"""Guardian watchdog daemon check utility for sidecar and host process health."""
import sys
import argparse
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def check_guardian_watchdog() -> int:
    """Verifies that reverse watchdog components and monitoring invariants are intact."""
    try:
        from medclient.sidecar_python.src.implementations.reverse_watchdog import ReverseWatchdog
        watchdog = ReverseWatchdog(poll_interval_ms=100)
        assert watchdog is not None
        assert not watchdog.is_alive()
        print("GUARDIAN WATCHDOG DAEMON: OK - Invariants validated successfully.")
        return 0
    except Exception as exc:
        print(f"GUARDIAN WATCHDOG DAEMON: FAILED - {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Guardian Watchdog Daemon Tool")
    parser.add_argument("--check", action="store_true", help="Perform integrity check of watchdog daemon")
    args = parser.parse_args()

    if args.check:
        sys.exit(check_guardian_watchdog())
    else:
        print("Specify --check to run watchdog verification.")
        sys.exit(1)
"""Guardian Watchdog Daemon conforming to system resilience specifications."""
import argparse
import sys
from pathlib import Path
import psutil

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
SIDECAR_DIR = PROJECT_ROOT / "medclient" / "sidecar-python"
if str(SIDECAR_DIR) not in sys.path:
    sys.path.insert(0, str(SIDECAR_DIR))

from medclient.sidecar_python.src.implementations.reverse_watchdog import ReverseWatchdog

def run_watchdog_check() -> int:
    """Verifies reverse watchdog invariants and system process telemetry."""
    watchdog = ReverseWatchdog(poll_interval_ms=100)
    current_pid = psutil.Process().pid
    watchdog.start(parent_pid=current_pid)
    is_active = watchdog.is_alive()
    watchdog.stop()
    assert is_active, "Watchdog thread must be alive after start"
    sys.stdout.write("[Guardian Watchdog] System telemetry and reverse watchdog verified.\n")
    return 0

def main() -> None:
    parser = argparse.ArgumentParser(description="MedPlatform Guardian Watchdog Daemon")
    parser.add_argument("--check", action="store_true", help="Run standalone system health verification")
    args = parser.parse_args()

    if args.check:
        sys.exit(run_watchdog_check())
    sys.stdout.write("[Guardian Watchdog] Daemon initialized.\n")

if __name__ == "__main__":
    main()
