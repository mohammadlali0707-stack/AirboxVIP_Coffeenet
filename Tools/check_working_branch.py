#!/usr/bin/env python3
"""check_working_branch.py -- HEAD must be on the repo's working branch.

Prevents commits from landing on a stray branch (e.g. detached HEAD
from a SHA checkout, or an accidental new branch) instead of main.

A DETACHED HEAD OR AN UNREADABLE GIT MUST NOT READ AS A PASS.
`git rev-parse --abbrev-ref HEAD` prints the literal string `HEAD` when
detached, and the command can fail outright with no repository at all.
Both report `unmeasured`.

Usage:
  python Tools/check_working_branch.py
  python Tools/check_working_branch.py --expected some-other-branch

ASCII only. Exit 0 pass, 1 fail or unmeasured.
"""

import argparse
import json
import os
import subprocess
import sys

MARKER = "##TBS##"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_BRANCH = "main"


def emit(status, data):
    print(MARKER + json.dumps({"v": 1, "probe": "working_branch",
                               "status": status, "data": data},
                              ensure_ascii=True, sort_keys=True))


def expected_branch():
    return os.environ.get("TBS_BRANCH") or DEFAULT_BRANCH


def current_branch(root):
    """The checked-out branch name, or (None, reason) if it could not be
    read -- covers a detached HEAD (git prints the literal string 'HEAD')
    and a repository git itself could not read."""
    try:
        p = subprocess.run(["git", "-C", root, "rev-parse",
                            "--abbrev-ref", "HEAD"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError as exc:
        return None, str(exc)
    if p.returncode != 0:
        return None, p.stderr.decode("utf-8", "replace").strip()
    name = p.stdout.decode("utf-8", "replace").strip()
    if name == "HEAD":
        return None, "detached HEAD"
    if not name:
        return None, "git printed an empty branch name"
    return name, None


def verdict(branch, expected):
    """Pure function: 'pass'/'fail'/'unmeasured' for a (branch, expected) pair."""
    if branch is None:
        return "unmeasured"
    return "pass" if branch == expected else "fail"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--expected", default=None,
                    help=("override the expected branch (default: "
                         "$TBS_BRANCH or " + DEFAULT_BRANCH))
    ap.add_argument("--root", default=ROOT)
    args = ap.parse_args(argv)

    expected = args.expected or expected_branch()
    branch, err = current_branch(args.root)
    status = verdict(branch, expected)

    if status == "unmeasured":
        emit("unmeasured", {"reason": err, "expected": expected})
        sys.stderr.write(
            "UNMEASURED: could not read the current branch ({0}) -- this "
            "gate measured NOTHING, which is not a pass.\n".format(err))
        return 1

    emit(status, {"branch": branch, "expected": expected})

    if status == "pass":
        sys.stderr.write(
            "HEAD is on {0}, the working branch.\n".format(branch))
        return 0

    sys.stderr.write(
        "FAIL: HEAD is on '{0}', not the working branch '{1}'.\n"
        .format(branch, expected))
    sys.stderr.write(
        "      Rule: commit directly to {0}, no side branch, no PR.\n"
        "      Fix: git checkout {0}\n".format(expected))
    return 1


if __name__ == "__main__":
    sys.exit(main())
