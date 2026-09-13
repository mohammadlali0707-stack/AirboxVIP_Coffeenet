# Agent Rules for AirboxVIP_Coffeenet (momonakikugava-pixel)

## 1. Branch and Delivery
- Work on main branch directly.
- A delivery is complete only when git push succeeds and verified.

## 2. Repository Structure
- src/ — Vite/React frontend
- 	elegram_bot/ — Python Telegram bot
- Tools/run_gates.py — Verification gates

## 3. Cross-Account Repository Access

All 9 GitHub accounts and their PATs are pre-stored as secrets. Use the correct ACC{N}_PAT for each repo.

**Corrected 2026-09-13: Control-Room and Claud-Cloud-Project (TBS) both
live on ACC6 -- ACC0 hosts neither, only its own `agw-workers` fleet.**
This table was written when Control-Room still lived on ACC0; see
`Mohammadlali/Control-Room`'s own retirement (that repo's
`Team/COMPANY_SCOPE.md`, "What changed 2026-09-13").

| Target Repo Owner | Secret to Use | Notes |
|---|---|---|
| Mohammadlali | `ACC0_PAT` | agw-workers only (ACC0 hosts no project as of 2026-09-13) |
| momonakikugava-pixel | `ACC1_PAT` | This repo (AirboxVIP_Coffeenet) |
| lali94m-max | `ACC2_PAT` | Worker acc2 |
| ngocgminh5-debug | `ACC3_PAT` | Worker acc3 |
| hmmletssee7-design | `ACC4_PAT` | Worker acc4 |
| kidding602 | `ACC5_PAT` | Worker acc5 |
| mohammadlali0707-stack | `ACC6_PAT` | Control-Room AND Claud-Cloud-Project (TBS) |
| mohammad97okk | `ACC7_PAT` | Worker acc7 |
| moradzahra85-png | `ACC8_PAT` | Worker acc8 |

### Usage Pattern
```bash
# Clone this repo with write access:
git clone https://x-access-token:${ACC1_PAT}@github.com/momonakikugava-pixel/AirboxVIP_Coffeenet.git
cd AirboxVIP_Coffeenet
git config user.email "agent@agy.dev"
git config user.name "AGY Agent"
# ... make changes ...
git add -A && git commit -m "feat: ..." && git push
```

**NEVER create new account-specific secrets. All 9 are already available as ACC0-ACC8_PAT.**