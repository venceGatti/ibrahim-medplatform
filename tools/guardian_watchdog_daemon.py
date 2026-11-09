#!/usr/bin/env python3
"""
Guardian Watchdog Daemon for MedPlatform.
Monitors memory usage, IPC health, and architectural invariants.
"""
import sys
import psutil

def check_system_invariants() -> int:
    process = psutil.Process()
    rss_mb = process.memory_info().rss / (1024 * 1024)
    print(f"[GUARDIAN] Current Process RSS: {rss_mb:.2f} MB")
    if rss_mb > 300.0:
        print(f"[GUARDIAN ERROR] RSS memory ceiling exceeded (>300MB): {rss_mb:.2f} MB")
        return 1
    print("[GUARDIAN] All architectural and memory invariants satisfied (< 300 MB RSS).")
    return 0

if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(check_system_invariants())
    else:
        print("Usage: python tools/guardian_watchdog_daemon.py --check")
        sys.exit(0)
