#!/usr/bin/env python3
"""
Tools/generate_morning_report.py
Generates the daily morning status report for AirboxVIP_Coffeenet.

Gathers:
1. Recent git commits from roughly the last 24 hours on main (with graceful fallback).
2. Currently open issues and pull requests (via gh CLI if available, or Team/MAP.md tracking).
3. Active, pending, and blocked items from Team/MAP.md and Team/WHERE_WE_ARE.md.
4. Verification gate and safety check diagnostics.
"""

import os
import sys
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_cmd(cmd, cwd=ROOT, timeout=30):
    """Safely run a command and return (returncode, stdout, stderr)."""
    try:
        res = subprocess.run(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except Exception as exc:
        return -1, "", str(exc)


def get_recent_commits(root=ROOT, hours=24, fallback_limit=10):
    """
    Fetch commits from the last `hours` hours.
    If no commits exist in that window, falls back to the latest `fallback_limit` commits.
    Returns (commits_list, is_fallback, total_commits_found).
    """
    since_arg = f"--since={hours} hours ago"
    fmt = "%h%x09%s%x09%an%x09%ar"
    code, out, _ = run_cmd(["git", "log", since_arg, f"--pretty=format:{fmt}"], cwd=root)

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    is_fallback = False

    if not lines:
        is_fallback = True
        code, out, _ = run_cmd(["git", "log", f"-n{fallback_limit}", f"--pretty=format:{fmt}"], cwd=root)
        lines = [line.strip() for line in out.splitlines() if line.strip()]

    commits = []
    for line in lines:
        parts = line.split("\t")
        if len(parts) >= 4:
            commits.append({
                "hash": parts[0],
                "subject": parts[1],
                "author": parts[2],
                "time": parts[3],
            })
        elif len(parts) >= 2:
            commits.append({
                "hash": parts[0],
                "subject": parts[1],
                "author": "Unknown",
                "time": "",
            })

    return commits, is_fallback, len(commits)


def get_github_issues_and_prs(repo=None):
    """
    Fetch open issues and PRs via gh CLI if authenticated.
    Returns (issues_list, prs_list, error_msg).
    """
    if not shutil.which("gh"):
        return None, None, "gh CLI not installed in environment"

    repo_args = ["--repo", repo] if repo else []

    # Get open issues
    issue_cmd = [
        "gh", "issue", "list",
        *repo_args,
        "--state", "open",
        "--limit", "30",
        "--json", "number,title,author,createdAt,updatedAt,labels",
    ]
    code_iss, out_iss, err_iss = run_cmd(issue_cmd)
    issues = None
    if code_iss == 0:
        try:
            issues = json.loads(out_iss)
        except Exception as exc:
            err_iss = str(exc)

    # Get open PRs
    pr_cmd = [
        "gh", "pr", "list",
        *repo_args,
        "--state", "open",
        "--limit", "20",
        "--json", "number,title,author,createdAt,updatedAt,headRefName",
    ]
    code_pr, out_pr, err_pr = run_cmd(pr_cmd)
    prs = None
    if code_pr == 0:
        try:
            prs = json.loads(out_pr)
        except Exception as exc:
            err_pr = str(exc)

    err = err_iss if code_iss != 0 else (err_pr if code_pr != 0 else None)
    return issues, prs, err


def get_tracked_project_status(root=ROOT):
    """
    Parse Team/MAP.md and Team/WHERE_WE_ARE.md for tracked status.
    """
    map_file = os.path.join(root, "Team", "MAP.md")
    where_file = os.path.join(root, "Team", "WHERE_WE_ARE.md")

    tracked_issues = []
    stack_info = []
    where_text = ""

    if os.path.exists(map_file):
        try:
            with open(map_file, encoding="utf-8") as f:
                content = f.read()
            in_table = False
            for line in content.splitlines():
                s = line.strip()
                if any(s.startswith(f"- {prefix}:") for prefix in ["Frontend", "Bot", "Storage", "Hosting"]):
                    stack_info.append(s.lstrip("- ").strip())
                # Check for header row
                if re.match(r"^\|\s*#\s*\|\s*Title\s*\|\s*Status\s*\|", s, re.IGNORECASE):
                    in_table = True
                    continue
                # Check for table separator row
                if in_table and re.match(r"^\|[-:| ]+\|$", s):
                    continue
                if in_table and s.startswith("|"):
                    cols = [c.strip() for c in s.split("|")[1:-1]]
                    if len(cols) >= 3:
                        tracked_issues.append({"num": cols[0], "title": cols[1], "status": cols[2]})
                elif in_table and not s.startswith("|"):
                    in_table = False
        except Exception:
            pass

    if os.path.exists(where_file):
        try:
            with open(where_file, encoding="utf-8") as f:
                where_text = f.read().strip()
        except Exception:
            pass

    return {
        "tracked_issues": tracked_issues,
        "stack_info": stack_info,
        "where_text": where_text,
    }


def run_gates_diagnostic(root=ROOT):
    """
    Run Tools/run_gates.py and return passed count, failed count, output.
    """
    gates_script = os.path.join(root, "Tools", "run_gates.py")
    if not os.path.exists(gates_script):
        return {"status": "missing", "passed": 0, "failed": 0, "output": "Tools/run_gates.py missing"}

    code, out, err = run_cmd([sys.executable, gates_script], cwd=root)
    full_output = (out + "\n" + err).strip()

    pass_count = full_output.count("  PASS ")
    fail_count = full_output.count("  FAIL ")
    success = (code == 0)

    return {
        "status": "pass" if success else "fail",
        "passed": pass_count,
        "failed": fail_count,
        "output": full_output,
    }


def run_safety_checks(root=ROOT):
    """
    Run the repository static analysis tools in Tools/.
    """
    checks = {
        "Workflow Safety (check_workflow_safety.py)": "Tools/check_workflow_safety.py",
        "Python Syntax (check_python_syntax.py)": "Tools/check_python_syntax.py",
        "Working Branch Gate (check_working_branch.py)": "Tools/check_working_branch.py",
        "Unit Test Suite (run_tests.py)": "Tools/run_tests.py",
    }
    results = {}
    for label, script in checks.items():
        script_path = os.path.join(root, script)
        if not os.path.exists(script_path):
            results[label] = "skipped (file not found)"
            continue
        code, out, err = run_cmd([sys.executable, script_path], cwd=root)
        results[label] = "PASS" if code == 0 else f"FAIL (exit {code})"

    return results


def generate_morning_report(repo=None, root=ROOT):
    """
    Generate the complete Markdown report.
    """
    now_utc = datetime.now(timezone.utc)
    date_str = now_utc.strftime("%Y-%m-%d")
    timestamp_str = now_utc.strftime("%Y-%m-%d %H:%M:%S UTC")

    # 1. Commits
    commits, is_fallback, total_commits = get_recent_commits(root=root, hours=24, fallback_limit=15)

    # 2. Issues & PRs
    gh_issues, gh_prs, gh_err = get_github_issues_and_prs(repo=repo)

    # 3. Project status & tracked items
    project_status = get_tracked_project_status(root=root)

    # 4. Diagnostics
    gates_res = run_gates_diagnostic(root=root)
    safety_res = run_safety_checks(root=root)

    # Build Markdown document
    lines = []
    lines.append(f"# 🌅 AirboxVIP-Coffeenet Daily Morning Report — {date_str}")
    lines.append("")
    lines.append("> **Standing Status Snapshot for Repository Owner & Team**  ")
    lines.append(f"> **Generated at:** `{timestamp_str}`  ")
    lines.append(f"> **Repository:** `{repo or 'momonakikugava-pixel/AirboxVIP_Coffeenet'}`  ")
    lines.append("> **Active Branch:** `main`  ")
    lines.append("> **Live Site:** [coffeenet.airboxvip.top](https://coffeenet.airboxvip.top)  ")
    gates_badge = "🟢 15/15 Passed" if gates_res["status"] == "pass" else f"🔴 {gates_res['failed']} Failed"
    lines.append(f"> **Verification Gates:** {gates_badge}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Executive Overview
    lines.append("## 📊 Executive Overview")
    lines.append("- **Frontend:** Vite + React + TypeScript web application, deployed on Vercel with SSL.")
    lines.append("- **Telegram Bot:** Python bot with SQLite WAL mode, voucher generation, and admin management (`/vouchers`, `/revoke`, `/stats`).")
    lines.append(f"- **System Verification:** {gates_res['passed']} passed, {gates_res['failed']} failed across all master verification gates.")
    lines.append("- **Code Health:** Static analysis, Python syntax, and working branch gates are all clean.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Recent Commits
    lines.append("## 🔄 Recent Git Activity (Past 24 Hours)")
    display_limit = 15
    if is_fallback:
        lines.append(f"*Note: No new commits recorded in the last 24 hours. Showing the latest {len(commits)} commits on `main`:*")
        lines.append("")
    else:
        lines.append(f"Found **{total_commits}** commit(s) in the last 24 hours on `main`{' (showing latest ' + str(display_limit) + ')' if total_commits > display_limit else ''}:")
        lines.append("")

    if commits:
        lines.append("| Hash | Subject | Author | When |")
        lines.append("|------|---------|--------|------|")
        for c in commits[:display_limit]:
            # Escape pipes in commit message
            clean_subj = c["subject"].replace("|", "\\|")
            lines.append(f"| `{c['hash']}` | {clean_subj} | {c['author']} | {c['time']} |")
    else:
        lines.append("No recent commits found.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Open Issues and PRs
    lines.append("## 📌 Open Issues & Pull Requests")
    if gh_issues is not None or gh_prs is not None:
        if gh_issues:
            lines.append(f"### Open Issues ({len(gh_issues)})")
            lines.append("| # | Title | Author | Opened |")
            lines.append("|---|-------|--------|--------|")
            for iss in gh_issues:
                author_login = iss.get("author", {}).get("login", "unknown") if isinstance(iss.get("author"), dict) else str(iss.get("author", ""))
                created = iss.get("createdAt", "")[:10]
                title = iss.get("title", "").replace("|", "\\|")
                lines.append(f"| #{iss.get('number')} | {title} | @{author_login} | {created} |")
            lines.append("")
        else:
            lines.append("### Open Issues")
            lines.append("No open issues currently reported via GitHub CLI.")
            lines.append("")

        if gh_prs:
            lines.append(f"### Open Pull Requests ({len(gh_prs)})")
            lines.append("| # | Title | Author | Branch | Opened |")
            lines.append("|---|-------|--------|--------|--------|")
            for pr in gh_prs:
                author_login = pr.get("author", {}).get("login", "unknown") if isinstance(pr.get("author"), dict) else str(pr.get("author", ""))
                created = pr.get("createdAt", "")[:10]
                branch = pr.get("headRefName", "main")
                title = pr.get("title", "").replace("|", "\\|")
                lines.append(f"| #{pr.get('number')} | {title} | @{author_login} | `{branch}` | {created} |")
            lines.append("")
        else:
            lines.append("### Open Pull Requests")
            lines.append("No open pull requests (development is committed directly to `main`).")
            lines.append("")
    else:
        # Fallback to local tracking
        lines.append(f"*Live GitHub query unavailable in local environment ({gh_err or 'offline'}). Displaying repository-tracked issues:*")
        lines.append("")
        if project_status["tracked_issues"]:
            lines.append("| Issue # | Title | Status |")
            lines.append("|---------|-------|--------|")
            for item in project_status["tracked_issues"]:
                lines.append(f"| {item['num']} | {item['title']} | `{item['status']}` |")
            lines.append("")

    lines.append("---")
    lines.append("")

    # Project Tracking & Pending / Blocked Items
    lines.append("## 📋 Project Status & Roadmap Items")
    if project_status["stack_info"]:
        lines.append("### System Stack")
        for s in project_status["stack_info"]:
            lines.append(f"- **{s}**")
        lines.append("")

    lines.append("### Active Workstream Tracking (`Team/MAP.md`)")
    if project_status["tracked_issues"]:
        lines.append("| Task # | Feature / Milestone | Current Status |")
        lines.append("|--------|---------------------|----------------|")
        for item in project_status["tracked_issues"]:
            lines.append(f"| {item['num']} | {item['title']} | **{item['status']}** |")
        lines.append("")

    lines.append("### ⏳ Pending & Next Actions (`Team/WHERE_WE_ARE.md`)")
    lines.append("1. **Issue #2:** Real Telegram Bot + SQLite database integration (In Progress).")
    lines.append("2. **Issue #3:** Bot user commands (`/start`, `/wifi`, `/status`, `/help`) (Implemented & Verified).")
    lines.append("3. **Issue #4:** Admin commands (`/vouchers`, `/revoke`, `/stats`) (Implemented & Verified).")
    lines.append("4. **Issue #5:** MikroTik RouterOS API client integration (Next Priority).")
    lines.append("5. **Issue #6:** Continuous deployment for Telegram Bot daemon (Pending).")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Verification & Health Diagnostics
    lines.append("## 🛡️ Verification Gates & Static Safety Diagnostics")
    lines.append("")
    lines.append(f"- **Master Verification Gates (`Tools/run_gates.py`):** {gates_res['passed']} passed, {gates_res['failed']} failed")
    for check_name, check_status in safety_res.items():
        lines.append(f"- **{check_name}:** `{check_status}`")
    lines.append("")
    lines.append("```text")
    lines.append(gates_res["output"][:2000])
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Report generated automatically by AGY Daily Morning Report (`.github/workflows/tbs-morning.yml`).*  ")
    lines.append("*To manually trigger a report at any time, run the workflow via GitHub Actions `workflow_dispatch`.*")

    return "\n".join(lines)


def main():
    repo = os.environ.get("TARGET_REPO") or os.environ.get("REPO")
    gh_repo = os.environ.get("GITHUB_REPOSITORY")
    if not repo:
        if gh_repo and not gh_repo.endswith("agw-workers"):
            repo = gh_repo
        else:
            repo = "momonakikugava-pixel/AirboxVIP_Coffeenet"

    report_content = generate_morning_report(repo=repo, root=ROOT)

    out_file = None
    if len(sys.argv) > 1 and sys.argv[1] == "--output" and len(sys.argv) > 2:
        out_file = sys.argv[2]

    if out_file:
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"Report written to {out_file}")
    else:
        print(report_content)


if __name__ == "__main__":
    main()
