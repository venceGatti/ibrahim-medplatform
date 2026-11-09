#!/usr/bin/env python3
"""
E2E Master Runner Wrapper for MedPlatform.
Executes test suite and master E2E runner.
"""
import subprocess
import sys

def main() -> int:
    cmd = [sys.executable, "tests/master_e2e_runner.py"]
    res = subprocess.run(cmd)
    return res.returncode

if __name__ == "__main__":
    sys.exit(main())
