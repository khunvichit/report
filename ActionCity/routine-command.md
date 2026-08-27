# Routine bootstrap command

Paste ONE of these into the Claude routine's prompt box. It just points at the instruction file —
all real logic lives in `actioncity-routine-prompt.md`, so you never edit the prompt box again.

## If the repo root IS this ActionCity folder
```
Read actioncity-routine-prompt.md from the repo and execute every step in it exactly, in order.
Run unattended — no approval prompts. Use the attached NetSuite and Lark connectors.
```

## If ActionCity is a subfolder of the repo (e.g. repo "report" → report/ActionCity/)  ← your layout
```
Read ActionCity/actioncity-routine-prompt.md from the repo and execute every step in it exactly,
in order. Treat the ActionCity/ folder as the working directory — every file it references
(template, queries, fill_template.py, preflight_check.py, sender/method/branding/contacts) is in
that same folder. Run unattended — no approval prompts. Use the attached NetSuite and Lark connectors.
```

## Routine configuration (set once)
- **Connectors:** attach **NetSuite** (read-only SuiteQL) and **Lark** (mail + messaging) to the routine itself — not just your chat session.
- **Schedule:** daily, **09:00 Asia/Bangkok**, reporting **yesterday** (the fully-settled day).
  - NOT 22:00 same-day: at 22:00 the online/marketplace orders have not settled yet (they invoice when the payment gateway clears, 1–2 days later), so the numbers are provisional and a **correction email** follows. Reporting yesterday at 09:00 = one clean, final send.
- **ONE trigger only.** This routine must have a single schedule. Remove any duplicate cron, and make sure the `data-now-*` / `email-now-*` intraday snapshots are **manual-only (never auto-emailed)** — a second auto-send is the other reason two emails go out per day.
- **Env / mode:**
  - First 1–2 weeks: `MODE=manual-test` → emails the owner only, skips the group. Validate, then switch.
  - Live: `MODE=scheduled`.
  - Back-fill a past day: `MODE=manual-live` and `REPORT_DATE=YYYY-MM-DD`.
- **Before first run:** fill the Lark group `chat_id` in `contacts.md` and confirm the footer in `branding.md`.
- **Validate (manual-test):** Run-now → check the email arrives, dates = **yesterday** (BKK), no `{{tokens}}` left, branch rows fill, group skipped, and a `sent/actioncity-daily-<date>.sent` marker is written. Run it a **second time** and confirm it STOPS at the idempotency guard (no duplicate email). Only then enable the schedule.
