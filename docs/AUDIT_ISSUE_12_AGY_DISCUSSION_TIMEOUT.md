# Audit Report — Issue #12: AGY Discussion Responder Workflow Timeout

**Target Repository:** `momonakikugava-pixel/AirboxVIP_Coffeenet`  
**Target Workflow:** `.github/workflows/agy-discussion.yml`  
**Reference Standards:** Claud-Cloud-Project (CCP) / AGW Worker Fleet (`Mohammadlali/agw-workers`)  
**Date:** 2026-09-09  
**Auditor:** AGY Software Engineer Bot  

---

## 1. Executive Summary

An audit was conducted on `.github/workflows/agy-discussion.yml` to evaluate its timeout configurations (inner and outer timeouts on `agy` CLI calls) against the standards established in **Claud-Cloud-Project (CCP)** and the shared **AGW Worker Fleet (`Mohammadlali/agw-workers`)**.

### Primary Findings
1. **Architectural Delegation vs Direct Execution:**  
   `.github/workflows/agy-discussion.yml` does **not** call the `agy` CLI binary directly on the local runner. Instead, it dispatches tasks asynchronously via GitHub Actions workflow dispatch (`gh workflow run agw-worker.yml`) to the AGW worker fleet. The actual `agy` CLI execution happens on the worker runner.
2. **Inner & Outer CLI Timeout Standard in CCP:**  
   In Claud-Cloud-Project / AGW workers (`agw-worker.yml`), the standard `agy` CLI invocation is:
   ```bash
   OUTPUT=$(timeout 1700 agy --dangerously-skip-permissions --print-timeout 1680s -p "$PROMPT" 2>&1) || true
   ```
   - **Inner Timeout:** `--print-timeout 1680s` (28 minutes). Restored from CCP standards (historical `Gateway/gateway_win.py` where `--print-timeout` was passed, and CCP Issue #87 where dropping this flag caused premature `"Error: timeout waiting for response"`).
   - **Outer Shell Timeout:** `timeout 1700` (28.33 minutes) acting as a shell process backstop just above `--print-timeout 1680s`.
3. **Critical Timeout Mismatch in Dispatcher Polling Loop:**  
   In `.github/workflows/agy-discussion.yml`, the worker wait loop was configured as:
   ```bash
   for i in $(seq 1 40); do ... sleep 30; done
   ```
   This wait loop terminated after **1200 seconds (20 minutes)**. Because worker jobs can run for up to 1700 seconds (~28.3 minutes), any discussion response requiring >20 minutes caused the caller workflow to prematurely exit the wait loop, fail artifact download, and falsely post `*(AGY produced no output)*` to the discussion comment.
4. **Job Timeout Headroom:**  
   The job outer timeout in `.github/workflows/agy-discussion.yml` was set to `timeout-minutes: 30`. If the polling loop is extended to accommodate the full 1700s worker timeout plus queue/dispatch/download overhead (~30 min), a 30-minute job timeout risks cutting off the job before posting the reply.
5. **Multi-Account Dispatch Violation (`SECURITY_RULES.md` Rule 5):**  
   `.github/workflows/agy-discussion.yml` computed `DISC_IDX=$(( DISCUSSION_NUM % 9 ))`, but hardcoded dispatch to `Mohammadlali/agw-workers`, secret `MOHAMMADLALI_PAT`, and `--field "acc_index=0"`. This violated Rule 5 (`CORRECT: --field "acc_index=$(( ACC_IDX + 1 ))"` and `WRONG: --field "acc_index=0"`) and overloaded account 0 rather than rotating across all 9 accounts (`ACC0_PAT` through `ACC8_PAT`), unlike `agy-issue-bot.yml`.

---

## 2. Standards Comparison Matrix

| Dimension | Claud-Cloud-Project (CCP) / AGW Fleet Standard | AirboxVIP `.github/workflows/agy-discussion.yml` (Pre-Audit) | AirboxVIP Remediation (Post-Audit) | Status / Alignment |
|---|---|---|---|---|
| **CLI Execution Model** | Delegated to `agw-worker.yml` (centralized OAuth credential management). | Delegated to `agw-worker.yml`. | Delegated to `agw-worker.yml`. | **Aligned** |
| **Inner Timeout (`agy` CLI)** | `--print-timeout 1680s` (28 min) passed directly to `agy`. | Configured inside worker (`agw-worker.yml`). | Configured inside worker (`agw-worker.yml`). | **Aligned** (caller respects worker budget) |
| **Outer Timeout (Shell)** | `timeout 1700` (28.33 min) wrapping `agy` invocation. | Configured inside worker (`agw-worker.yml`). | Configured inside worker (`agw-worker.yml`). | **Aligned** |
| **Caller Polling Wait Loop** | Polling must span full worker lifecycle: >= 1800s (30 min). | `seq 1 40` (40 * 30s = 1200s = 20 min). | `seq 1 60` (60 * 30s = 1800s = 30 min). | **Remediated** (Defect resolved) |
| **Workflow Job Timeout** | 35 to 45 minutes (`timeout-minutes: 35` to `45`). | `timeout-minutes: 30`. | `timeout-minutes: 35`. | **Remediated** (Headroom provided) |
| **Multi-Account Dispatch** | Rotates through 9 worker accounts (`ACC0_PAT`..`ACC8_PAT`), 1-indexed `acc_index`. | Hardcoded `acc_index=0`, `Mohammadlali/agw-workers`, `MOHAMMADLALI_PAT`. | Full 9-account rotation (`ACC0_PAT`..`ACC8_PAT`), 1-indexed `acc_index=$(( DISC_IDX + 1 ))`. | **Remediated** (Complies with Rule 5) |
| **Artifact Collection Token** | Uses the dispatch account's PAT to download run artifact. | Hardcoded `MOHAMMADLALI_PAT`. | Uses `DISPATCH_TOKEN` dynamically matching target worker repo. | **Remediated** |

---

## 3. Detailed Technical Analysis

### 3.1 The `agy` CLI Timeout Hierarchy

In the Claud-Cloud-Project / AGW architecture, timeout handling exists across four tiers:

1. **Tier 1: `agy` Internal Timeout (`--print-timeout`):**  
   The Antigravity CLI implements its own internal wait ceiling for model responses. When omitted, `agy` falls back to an internal short default. In CCP Issue #87, live runs failed with `Error: timeout waiting for response` because `--print-timeout` was omitted. Setting `--print-timeout 1680s` ensures `agy` does not prematurely kill its internal turn before the model completes complex multi-step reasoning.
2. **Tier 2: Worker Process Timeout (`timeout 1700`):**  
   The Linux shell `timeout` command wraps the `agy` process in `agw-worker.yml`. At 1700 seconds (20 seconds after 1680s), it provides a clean external backstop in case the process hangs.
3. **Tier 3: Dispatcher Polling Loop (`seq 1 60` * 30s):**  
   The calling workflow (`agy-discussion.yml` / `agy-issue-bot.yml`) polls GitHub Actions run status using `gh run view`. Setting 60 iterations with 30s sleep allows up to 1800 seconds (30 minutes) of total polling time. This covers:
   - Runner allocation & queue time: ~30s
   - Target checkout & setup: ~30s
   - AGY execution: up to 1700s
   - Push & artifact upload: ~40s
4. **Tier 4: Workflow Job Timeout (`timeout-minutes: 35`):**  
   The outer GitHub Actions runner timeout prevents abandoned workflow jobs from consuming runner capacity indefinitely. 35 minutes provides 5 minutes of overhead beyond the 30-minute polling budget.

### 3.2 Dispatch and Security Alignment

In `.github/workflows/agy-discussion.yml`:
- Pre-audit implementation:
  ```bash
  DISC_IDX=$(( DISCUSSION_NUM % 9 ))
  echo "acc_index=$DISC_IDX" >> "$GITHUB_OUTPUT"
  ...
  gh workflow run agw-worker.yml \
    --repo Mohammadlali/agw-workers \
    --field "prompt=$PROMPT" \
    --field "acc_index=0" \
    ...
  ```
- Post-audit remediation:
  A unified `Dispatch, wait and collect` step maps `DISC_IDX` to `DISPATCH_REPO` and `DISPATCH_TOKEN` across all 9 accounts (`Mohammadlali`, `momonakikugava-pixel`, `lali94m-max`, `ngocgminh5-debug`, `hmmletssee7-design`, `kidding602`, `mohammadlali0707-stack`, `mohammad97okk`, `moradzahra85-png`).
  The field is set to `acc_index=$(( DISC_IDX + 1 ))` per `SECURITY_RULES.md` Rule 5.

---

## 4. Verification & Validation

1. **Static Analysis & Safety Gate (`Tools/check_workflow_safety.py`):**  
   All checks (printf quote escaping, python inline indentation, YAML syntax) pass with 0 errors.
2. **Master Verification Gates (`Tools/run_gates.py`):**  
   All 15 master gates pass cleanly.
3. **Working Branch Gate (`Tools/check_working_branch.py`):**  
   Verified on `main`.

---

## 5. Conclusion & Recommendations

The audit and remediation successfully align `.github/workflows/agy-discussion.yml` with Claud-Cloud-Project standards. Discussion responder runs will no longer prematurely time out on tasks requiring between 20 and 28 minutes, and load is balanced across the 9 worker accounts with correct 1-indexed account reporting.
