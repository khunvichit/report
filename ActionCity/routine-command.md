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
- **Schedule:** daily, **22:00 Asia/Bangkok** (end-of-day close).
- **Env / mode:**
  - First 1–2 weeks: `MODE=manual-test` → emails the owner only, skips the group. Validate, then switch.
  - Live: `MODE=scheduled`.
  - Back-fill a past day: `MODE=manual-live` and `REPORT_DATE=YYYY-MM-DD`.
- **Before first run:** fill the Lark group `chat_id` in `contacts.md` and confirm the footer in `branding.md`.
- **Validate (manual-test):** Run-now → check the email arrives, dates = today (BKK), no `{{tokens}}` left, branch rows fill, group skipped. Only then enable the schedule.
