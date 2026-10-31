"""
Opaque-Box Test Runner for MedPlatform End-to-End Test Suite.

Provides CLI execution of the multi-tier test suite with structured
executive reporting and exit code propagation.
"""

import sys
import time
import argparse
from pathlib import Path
from typing import List
import pytest

# Ensure project root is at the head of sys.path for absolute package imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def parse_runner_arguments() -> argparse.Namespace:
    """Parses command-line arguments for test execution."""
    parser = argparse.ArgumentParser(description="MedPlatform End-to-End Opaque-Box Test Runner")
    parser.add_argument(
        "--tier",
        type=str,
        choices=["all", "tier1", "tier2", "tier3", "tier4", "benchmarks"],
        default="all",
        help="Target test tier to execute (default: all)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose pytest output"
    )
    return parser.parse_args()


TIER_FOLDER_MAP = {
    "all": "tests",
    "tier1": "tests/tier1_features",
    "tier2": "tests/tier2_boundaries",
    "tier3": "tests/tier3_pairwise",
    "tier4": "tests/tier4_workloads",
    "benchmarks": "tests/benchmarks",
}


def construct_pytest_invocation_args(tier: str, verbose: bool) -> List[str]:
    """Constructs argument vector for pytest execution."""
    args = []
    if verbose:
        args.append("-v")
    else:
        args.append("-q")

    target_path = TIER_FOLDER_MAP.get(tier, "tests")
    args.append(target_path)
    return args


def execute_test_suite() -> int:
    """Executes the test suite and displays a formatted summary banner."""
    options = parse_runner_arguments()
    pytest_args = construct_pytest_invocation_args(options.tier, options.verbose)

    print("=" * 72)
    print("MEDPLATFORM END-TO-END OPAQUE-BOX TEST RUNNER")
    print(f"Target Selection: {options.tier.upper()}")
    print("=" * 72)

    start_timestamp = time.perf_counter()
    exit_code = pytest.main(pytest_args)
    elapsed_duration_sec = time.perf_counter() - start_timestamp

    print("-" * 72)
    print(f"Execution completed in {elapsed_duration_sec:.2f} seconds.")
    if exit_code == 0:
        print("RESULT: SUCCESS - ALL TEST INVARIANTS PASSED (100% PASS RATE)")
    else:
        print(f"RESULT: FAILED - PyTest exited with status code {exit_code}")
    print("=" * 72)

    return int(exit_code)


if __name__ == "__main__":
    sys.exit(execute_test_suite())
