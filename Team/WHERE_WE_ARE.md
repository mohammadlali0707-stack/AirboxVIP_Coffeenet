# AirboxVIP_Coffeenet - Where We Are

Last updated: 2026-09-13

## Frontend
- Live at coffeenet.airboxvip.top (Vercel + SSL)

## Telegram Bot
- Commands and admin management implemented (/start, /wifi, /status, /help, /vouchers, /revoke, /stats)
- Issues #2-6 in progress

## Automation & Reporting
- Daily Morning Status Report workflow active (.github/workflows/tbs-morning.yml)
- Master verification gates (15/15) + workflow safety checks
- Issue #12 completed: AGY discussion responder timeout audited & remediated (.github/workflows/agy-discussion.yml)
- Issue #16 completed: Project identity and role aligned to "کافینت ایرباکس وی آی پی" (replacing legacy/misnamed "ربات ووچر قهوه‌نت" in status feeds); audit report compiled in `docs/AUDIT_ISSUE_16_PROJECT_STATUS_ROLE_ALIGNMENT.md`.
- Issue #17 completed: Fixed (no output) in agy-issue-bot.yml result-collection step by capturing CALLBACK_ID and reading Reports/agy/${CALLBACK_ID}.txt via GitHub Contents API.
- `@agy` <-> `@claude` handoff loop completed (`97a9051`): agy-issue-bot.yml now accepts `claude[bot]` comments as a trigger (not just a human OWNER), and each bot ends its final message with a mention of the other only when the task is genuinely, completely done -- so the two bots can hand work back and forth without a human relaying between them. The worker-URL footer was also reordered to come before agy's own output so a trailing `@claude` marker survives truncation on long outputs.

## Next Steps
1. Issue #2: Real Telegram + SQLite
2. Issue #3: Bot commands
3. Issue #4: Admin commands
4. Issue #5: MikroTik API
5. Issue #6: Deployment
