#!/usr/bin/env python3
"""check_python_syntax.py -- Gate: validate all Python files compile cleanly."""
import ast
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXCLUDE_DIRS = {"node_modules", ".git", "__pycache__", ".venv", "venv", "dist"}


def check_file(path: str):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            source = f.read()
        ast.parse(source, filename=path)
        return None
    except SyntaxError as e:
        rel = os.path.relpath(path, ROOT)
        return f"{rel}:{e.lineno}: SyntaxError: {e.msg}"


def main():
    errors = []
    for py_file in glob.glob(os.path.join(ROOT, "**", "*.py"), recursive=True):
        # Skip excluded dirs
        parts = py_file.replace("\\", "/").split("/")
        if any(p in EXCLUDE_DIRS for p in parts):
            continue
        err = check_file(py_file)
        if err:
            errors.append(err)

    if errors:
        sys.stdout.write(f"check_python_syntax: FAILED ({len(errors)} file(s))\n")
        for e in errors:
            sys.stdout.write(f"  \u2717 {e}\n")
        sys.exit(1)

    sys.exit(0)  # Silent on pass


if __name__ == "__main__":
    main()
