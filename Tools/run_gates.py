#!/usr/bin/env python3
"""run_gates.py -- Verification Gates Runner for AirboxVIP_Coffeenet.
Silent on full pass (exit 0). Prints diagnostic and exits non-zero on failure.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATES = [
    ("check_workflow_safety", [sys.executable, os.path.join(ROOT, "Tools", "check_workflow_safety.py")]),
    ("check_python_syntax",   [sys.executable, os.path.join(ROOT, "Tools", "check_python_syntax.py")]),
    ("run_tests",             [sys.executable, os.path.join(ROOT, "Tools", "run_tests.py")]),
]


def main():
    failed = []
    for name, cmd in GATES:
        res = subprocess.run(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if res.returncode != 0:
            failed.append((name, res.stdout.strip()))

    if not failed:
        sys.exit(0)  # Zero output = zero token consumption

    sys.stderr.write("GATES FAILED in AirboxVIP_Coffeenet:\n")
    for name, output in failed:
        sys.stderr.write(f"\n--- Gate: {name} ---\n")
        sys.stderr.write(output + "\n")
    sys.exit(1)


if __name__ == "__main__":
    main()
