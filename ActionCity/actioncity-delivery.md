# ActionCity — Delivery (channel choice + content)

Declares this report's channels and content into the shared `method.md` / `sender.md` engine.

```
Delivery:
  Channels: email + group
  Fire group: always (daily close summary)
  Email key: [ActionCity] Daily Sales & Stock — {report_date_display}
  Mode default: scheduled   (first 1–2 weeks: manual-test)
```

## EMAIL
- **to:** see `contacts.md` → `actioncity_daily` recipients
  - management@actioncity.co.th
  - may@chaw.co.th
  - panu@chaw.co.th
- **subject:** `[ActionCity] Daily Sales & Stock — {report_date_display} ({report_weekday})`
- **html_body:** contents of `email.html` (produced by `fill_template.py`; never model output)
- **idempotency:** before sending, search sent mail for the exact Email key subject; if found, skip (no double-send).
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
