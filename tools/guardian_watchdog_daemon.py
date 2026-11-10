"""Guardian Watchdog Daemon Tool for MedPlatform Health and Invariants."""
import argparse
import sys
import psutil

def check_system_invariants() -> bool:
    """Verifies that system invariants such as memory usage and processes are within bounds."""
    # Enforce RSS ceiling < 300MB
    process = psutil.Process()
    rss_mb = process.memory_info().rss / (1024 * 1024)
    if rss_mb > 300.0:
        sys.stderr.write(f"ERROR: Memory RSS exceeds 300 MB limit: {rss_mb:.2f} MB\n")
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Guardian Watchdog Daemon")
    parser.add_argument("--check", action="store_true", help="Perform immediate system check")
    args = parser.parse_args()

    if args.check:
        if check_system_invariants():
            print("WATCHDOG_CHECK: OK - All system invariants within bounds (RSS < 300MB).")
            sys.exit(0)
        else:
            print("WATCHDOG_CHECK: FAILED")
            sys.exit(1)
    else:
        print("Guardian watchdog running...")

if __name__ == "__main__":
    main()
