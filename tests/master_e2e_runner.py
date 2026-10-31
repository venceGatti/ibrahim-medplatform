"""Master E2E Integration Runner conforming to AGENTS.md."""
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.e2e_runner import execute_test_suite

if __name__ == "__main__":
    sys.exit(execute_test_suite())
