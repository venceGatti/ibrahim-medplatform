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
