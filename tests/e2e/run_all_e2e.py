"""Master E2E Test Suite Orchestrator."""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tests.e2e_runner import execute_test_suite

def main() -> int:
    """Executes all tiers and benchmark suites."""
    print("[E2E-ORCHESTRATOR] Running complete test suite...")
    exit_code = execute_test_suite()
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
