# AirboxVIP_Coffeenet Changelog

## 2026-09-09
- Issue #12: Audit agy discussion responder workflow timeout (.github/workflows/agy-discussion.yml) against Claud-Cloud-Project standards (docs/AUDIT_ISSUE_12_AGY_DISCUSSION_TIMEOUT.md)
- Increase agy-discussion job timeout to 35m and extend polling loop to 60 iterations (1800s) to align with AGW worker 1700s/1680s timeouts
- Implement 9-account worker dispatch rotation and 1-indexed acc_index in agy-discussion.yml per SECURITY_RULES.md Rule 5
- Issue #11: Add daily morning status report workflow (.github/workflows/tbs-morning.yml)
- Add report generator script (Tools/generate_morning_report.py) and test suite (tests/test_morning_report.py)

## 2026-09-08
- Add AGENTS.md with cross-account PAT mapping
- Add Tools/run_gates.py verification script
- Migrate files to repo root for Vercel
- Update Cloudflare DNS to Vercel CNAME
- Issue SSL certificate for coffeenet.airboxvip.top