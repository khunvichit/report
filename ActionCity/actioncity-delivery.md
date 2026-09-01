# ActionCity — Delivery (channel choice + content)

Declares this report's channels and content into the shared `method.md` / `sender.md` engine.

```
Delivery:
  Channels: email + group
  Fire group: always (daily close summary)
  Email key (idempotency): actioncity-daily-{report_date_iso}    # report_date_iso = YYYY-MM-DD (date-keyed, format/timezone-proof)
  Full subject: [ActionCity] Daily Sales & Stock — {report_date_display} ({report_weekday})
  Mode default: scheduled   (first 1–2 weeks: manual-test)
```

## EMAIL
- **to:** see `contacts.md` → `actioncity_daily` recipients
  - management@actioncity.co.th
  - may@chaw.co.th
  - panu@chaw.co.th
  - jakkraphan@chaw.co.th
- **subject:** `[ActionCity] Daily Sales & Stock — {report_date_display} ({report_weekday})`
- **html_body:** contents of `email.html` (produced by `fill_template.py`; never model output)
- **idempotency (two guards — EITHER one stops the send; one report_date → at most one email, ever):**
  1. **Sent-flag file (primary, no mail-search dependency):** before sending, check for `sent/actioncity-daily-{report_date_iso}.sent`. If it exists → already sent, STOP. **After a successful send, write that file** (timestamp + subject). Keyed on `report_date_iso` (YYYY-MM-DD) — never the display date/weekday, so formatting or a timezone edge can't produce a false "not sent".
  2. **Sent-mail search (secondary):** search sent mail for the **EXACT full subject string that is actually sent** — including the ` ({report_weekday})` suffix. (The old key omitted the weekday, so the exact search never matched the real subject and the guard never fired — that was the duplicate-send bug.) If found → STOP.
- **no correction emails:** a re-run for a report_date that was already sent MUST stop at the guard above — never send a second/"corrected" email for the same day. (Because we report the *settled* prior day, the first send is already final.)
- **manual-test mode:** send ONLY to the owner (vichit@sfb.co.th); skip group.

## GROUP (Lark)
- **chat_id:** see `contacts.md` → `actioncity_ops_group` (primary + fallback).
- **message** (short text card, NOT the full HTML — the email carries detail):
  ```
  📊 ActionCity Daily — {report_date_display} ({report_weekday})
  Net ฿{day_net} ({day_wow_arrow}{day_wow_pct} vs same day last wk) · {day_bills} bills · ฿{day_ticket} ticket
  WTD W{iso_week}: ฿{wtd_net} ({wtd_days}d)
  {group_flag_line}        ← e.g. "⚠ Westgate dark · Reorder: Lulu Scented 0.4w" or "✅ no exceptions"
  Full dashboard in email.
  ```
- `group_flag_line` is built in prediction step: join the DARK-branch alert + tightest reorder; if none, "✅ no exceptions".

## TASK
- Not used by this report. (Kept here, disabled, for easy future enable.)

## Gates
- email: always (after completeness passes).
- group: always in `scheduled`/`manual-live`; **skipped in `manual-test`**.
- A channel failing does NOT abort the others; completeness + idempotency are the only hard stops.
