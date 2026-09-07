#!/usr/bin/env python3
"""run_tests.py -- Gate: run pytest on tests/ directory.

Silent on pass. Prints output on failure.
Skips gracefully if pytest is not installed.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS_DIR = os.path.join(ROOT, "tests")


def main():
    if not os.path.isdir(TESTS_DIR):
        sys.exit(0)  # No tests dir - skip

    # Check if pytest available
    check = subprocess.run(
        [sys.executable, "-m", "pytest", "--version"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    if check.returncode != 0:
        # pytest not installed - skip gate
        sys.exit(0)

    res = subprocess.run(
        [sys.executable, "-m", "pytest", TESTS_DIR, "-q", "--tb=short"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    if res.returncode != 0:
        sys.stdout.write("run_tests: FAILED\n")
        sys.stdout.write(res.stdout)
        sys.exit(1)

    sys.exit(0)  # Silent on pass


if __name__ == "__main__":
    main()
