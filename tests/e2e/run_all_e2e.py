"""E2E Test Suite Runner for MedPlatform."""
import sys
import subprocess

def main():
    cmd = [sys.executable, "tests/master_e2e_runner.py"]
    res = subprocess.run(cmd)
    sys.exit(res.returncode)

if __name__ == "__main__":
    main()
