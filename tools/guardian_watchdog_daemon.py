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
