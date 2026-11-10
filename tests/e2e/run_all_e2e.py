"""E2E Test Suite Runner Proxy."""
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from tests.e2e_runner import execute_test_suite

if __name__ == "__main__":
    sys.exit(execute_test_suite())
