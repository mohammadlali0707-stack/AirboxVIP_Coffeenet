import unittest
import os
import tempfile
from Tools.generate_morning_report import (
    get_recent_commits,
    get_tracked_project_status,
    run_gates_diagnostic,
    run_safety_checks,
    generate_morning_report,
    ROOT,
)


class TestMorningReport(unittest.TestCase):
    def test_get_recent_commits(self):
        commits, is_fallback, count = get_recent_commits(root=ROOT, hours=24, fallback_limit=5)
        self.assertIsInstance(commits, list)
        self.assertGreater(len(commits), 0)
        self.assertIn("hash", commits[0])
        self.assertIn("subject", commits[0])
        self.assertIn("author", commits[0])

    def test_get_tracked_project_status(self):
        status = get_tracked_project_status(root=ROOT)
        self.assertIn("tracked_issues", status)
        self.assertIn("stack_info", status)
        self.assertGreater(len(status["tracked_issues"]), 0)
        # Verify tracked issue #2
        issue_nums = [i["num"] for i in status["tracked_issues"]]
        self.assertIn("#2", issue_nums)

    def test_run_gates_diagnostic(self):
        diag = run_gates_diagnostic(root=ROOT)
        self.assertEqual(diag["status"], "pass")
        self.assertGreaterEqual(diag["passed"], 15)
        self.assertEqual(diag["failed"], 0)

    def test_run_safety_checks(self):
        safety = run_safety_checks(root=ROOT)
        self.assertIn("Workflow Safety (check_workflow_safety.py)", safety)
        self.assertEqual(safety["Workflow Safety (check_workflow_safety.py)"], "PASS")
        self.assertEqual(safety["Python Syntax (check_python_syntax.py)"], "PASS")

    def test_generate_morning_report(self):
        report = generate_morning_report(repo="momonakikugava-pixel/AirboxVIP_Coffeenet", root=ROOT)
        self.assertIn("# 🌅 AirboxVIP-Coffeenet Daily Morning Report", report)
        self.assertIn("## 📊 Executive Overview", report)
        self.assertIn("## 🔄 Recent Git Activity", report)
        self.assertIn("## 📌 Open Issues & Pull Requests", report)
        self.assertIn("## 📋 Project Status & Roadmap Items", report)
        self.assertIn("## 🛡️ Verification Gates & Static Safety Diagnostics", report)


if __name__ == "__main__":
    unittest.main()
