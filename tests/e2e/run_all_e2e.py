"""Master E2E suite execution wrapper conforming to test runner interface."""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tests.e2e_runner import execute_test_suite

if __name__ == "__main__":
    sys.exit(execute_test_suite())
