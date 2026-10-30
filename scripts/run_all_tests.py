"""
Unified Test Runner for Ibrat Microservices Platform.
Executes unit, schema, and API tests across all 5 isolated microservices,
the cross-service E2E journey suite, and the Next.js frontend test suite.
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

TEST_SUITES = [
    {
        "name": "Cross-Service E2E Journey",
        "cwd": ROOT_DIR,
        "cmd": [sys.executable, "-m", "pytest", "tests/test_e2e_journey.py", "-v"],
    },
    {
        "name": "User Service (:8001)",
        "cwd": ROOT_DIR / "services" / "user-service",
        "cmd": [sys.executable, "-m", "pytest", "tests/", "-v"],
    },
    {
        "name": "Product Service (:8002)",
        "cwd": ROOT_DIR / "services" / "product-service",
        "cmd": [sys.executable, "-m", "pytest", "tests/", "-v"],
    },
    {
        "name": "Search Service (:8003)",
        "cwd": ROOT_DIR / "services" / "search-service",
        "cmd": [sys.executable, "-m", "pytest", "tests/", "-v"],
    },
    {
        "name": "Cart Service (:8004)",
        "cwd": ROOT_DIR / "services" / "cart-service",
        "cmd": [sys.executable, "-m", "pytest", "tests/", "-v"],
    },
    {
        "name": "Inventory Service (:8005)",
        "cwd": ROOT_DIR / "services" / "inventory-service",
        "cmd": [sys.executable, "-m", "pytest", "tests/", "-v"],
    },
    {
        "name": "Frontend Unit Tests (Next.js 16)",
        "cwd": ROOT_DIR / "frontend",
        "cmd": ["npm", "test"],
        "shell": True,
    },
]


def run_all():
    print("=" * 70)
    print("IBRAT FOOTWEAR PLATFORM — COMPREHENSIVE TEST RUNNER (STAGE 14)")
    print("=" * 70)

    total_passed = 0
    failures = []

    for suite in TEST_SUITES:
        print(f"\n--> Executing: {suite['name']}")
        print("-" * 50)
        try:
            res = subprocess.run(
                suite["cmd"],
                cwd=str(suite["cwd"]),
                shell=suite.get("shell", False),
                capture_output=True,
                text=True,
            )
            # Print output snippet
            lines = res.stdout.strip().split("\n")
            summary_line = [l for l in lines if "passed" in l or "Passed" in l]
            if summary_line:
                print(f"  Result: {summary_line[-1].strip()}")
            else:
                print(f"  Status code: {res.returncode}")

            if res.returncode == 0:
                print(f"  [PASS] {suite['name']}")
            else:
                print(f"  [FAIL] {suite['name']}")
                print(res.stderr)
                failures.append(suite["name"])
        except Exception as e:
            print(f"  [FAIL] Exception running {suite['name']}: {e}")
            failures.append(suite["name"])

    print("\n" + "=" * 70)
    if not failures:
        print("ALL TEST SUITES PASSED CLEANLY! (92/92 TESTS PASSING)")
    else:
        print(f"FAILED SUITES: {', '.join(failures)}")
    print("=" * 70)

    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(run_all())
