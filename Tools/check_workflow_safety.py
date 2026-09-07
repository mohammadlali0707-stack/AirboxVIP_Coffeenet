#!/usr/bin/env python3
"""
Tools/check_workflow_safety.py
Gate: Static analysis of GitHub Actions workflow files.

Checks (no AI tokens consumed, agent-agnostic):
  1. Double-quotes inside printf content strings
  2. Python inline code with insufficient YAML block indentation
  3. YAML syntax validity of all workflow files

Exception: lines with tr/sed (character-class args, not prompt content)
"""

import sys
import re
import os
import glob

C_FAIL = "\033[91m\u2717\033[0m"

_CHAR_CLASS_PATTERNS = ("tr -d", "tr -", "sed ", "| tr", "| sed")


def check_1_double_quotes_in_printf(filepath, lines):
    errors = []
    for i, raw_line in enumerate(lines, 1):
        line = raw_line.strip()
        if "printf" not in line:
            continue
        if any(p in line for p in _CHAR_CLASS_PATTERNS):
            continue
        if "$(printf" in line and "|" in line:
            continue
        sq_parts = re.findall(r"'([^']*)'" , line)
        for part in sq_parts[1:]:
            if '"' in part:
                errors.append(
                    (i, "[CHECK-1] double-quote in printf content string",
                     line[:100])
                )
    return errors


def check_2_python_inline_yaml_indent(filepath, lines):
    errors = []
    for i, raw_line in enumerate(lines, 1):
        line = raw_line.rstrip()
        if 'python3 -c "' not in line and "python3 -c '" not in line:
            continue
        py_cmd_indent = len(line) - len(line.lstrip())
        j = i
        while j < len(lines):
            next_raw = lines[j]
            next_stripped = next_raw.strip()
            if next_stripped in ('"', "'", '" 2>/dev/null', "' 2>/dev/null"):
                break
            if not next_stripped:
                j += 1
                continue
            next_indent = len(next_raw) - len(next_raw.lstrip())
            if next_indent < py_cmd_indent and next_stripped:
                errors.append(
                    (j + 1,
                     f"[CHECK-2] Python inline code at col {next_indent} "
                     f"(need >={py_cmd_indent} to stay in YAML block)",
                     next_stripped[:80])
                )
            j += 1
    return errors


def check_3_yaml_syntax(filepath, content):
    errors = []
    try:
        import yaml
        try:
            yaml.safe_load(content)
        except yaml.YAMLError as e:
            errors.append((0, f"[CHECK-3] YAML parse error", str(e)[:160]))
    except ImportError:
        pass
    return errors


def check_file(filepath):
    errors = []
    try:
        with open(filepath, encoding="utf-8", errors="replace") as f:
            content = f.read()
    except OSError as e:
        return [(0, "cannot read file", str(e))]

    lines = content.splitlines()
    errors += check_1_double_quotes_in_printf(filepath, lines)
    errors += check_2_python_inline_yaml_indent(filepath, lines)
    errors += check_3_yaml_syntax(filepath, content)
    return errors


def main():
    search_dir = sys.argv[1] if len(sys.argv) > 1 else ".github/workflows"
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    wf_dir = os.path.join(root, search_dir)

    files = sorted(
        glob.glob(os.path.join(wf_dir, "*.yml")) +
        glob.glob(os.path.join(wf_dir, "*.yaml"))
    )

    if not files:
        sys.exit(0)

    all_errors = []
    for fp in files:
        rel = os.path.relpath(fp, root)
        for lineno, msg, snippet in check_file(fp):
            loc = f"{rel}:{lineno}" if lineno else rel
            all_errors.append(f"{loc}: {msg}\n        snippet: {snippet}")

    if all_errors:
        sys.stdout.write(
            f"check_workflow_safety: FAILED ({len(all_errors)} issue(s))\n"
        )
        for e in all_errors:
            sys.stdout.write(f"  {C_FAIL} {e}\n")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
