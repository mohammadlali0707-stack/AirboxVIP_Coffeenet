#!/usr/bin/env python3
"""run_gates.py -- Verification Gates Runner for AirboxVIP_Coffeenet.
Silent on full pass (exit 0). Prints diagnostic and exits non-zero on failure.

Supports the ##TBS## marker protocol: if a gate exits non-zero but its
last ##TBS## line reports status='unmeasured', it is counted as unmeasured
rather than failed (e.g. check_working_branch on a detached HEAD).
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MARKER = "##TBS##"
_MARKER_RE = re.compile(r"^" + re.escape(MARKER) + r"(.+)$", re.MULTILINE)

GATES = [
    ("check_working_branch",  [sys.executable, os.path.join(ROOT, "Tools", "check_working_branch.py")]),
    ("check_workflow_safety", [sys.executable, os.path.join(ROOT, "Tools", "check_workflow_safety.py")]),
    ("check_python_syntax",   [sys.executable, os.path.join(ROOT, "Tools", "check_python_syntax.py")]),
    ("run_tests",             [sys.executable, os.path.join(ROOT, "Tools", "run_tests.py")]),
]


def digest_status(output):
    """Extract the reported status from the last ##TBS## line, or None."""
    for m in reversed(list(_MARKER_RE.finditer(output))):
        try:
            return json.loads(m.group(1)).get("status")
        except (ValueError, AttributeError):
            continue
    return None


def run_one(name, cmd):
    """Run one gate. Returns (status, output)."""
    tool_path = cmd[1] if len(cmd) > 1 else None
    if tool_path and not os.path.isfile(tool_path):
        return "unmeasured", "{0} does not exist.\n".format(tool_path)
    try:
        res = subprocess.run(cmd, cwd=ROOT, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return "unmeasured", "timed out after 300s -- nothing was measured.\n"
    except OSError as exc:
        return "unmeasured", str(exc) + "\n"

    out = res.stdout
    if res.returncode != 0:
        marker_status = digest_status(out)
        if marker_status == "unmeasured":
            return "unmeasured", out
        return "fail", out
    return "pass", out


def main():
    tally = {"pass": 0, "fail": 0, "unmeasured": 0}
    failures = []

    for name, cmd in GATES:
        status, output = run_one(name, cmd)
        tally[status] += 1
        if status != "pass":
            failures.append((name, status, output))

    if tally["fail"] == 0 and tally["unmeasured"] == 0:
        sys.exit(0)  # Zero output on pass - saves tokens completely

    sys.stderr.write("GATES RESULT in AirboxVIP_Coffeenet: {pass} pass, {fail} fail, {unmeasured} unmeasured\n".format(**tally))
    for name, status, output in failures:
        sys.stderr.write("\n--- Gate: {0} [{1}] ---\n".format(name, status))
        sys.stderr.write(output + "\n")
    sys.exit(1)


if __name__ == "__main__":
    main()
