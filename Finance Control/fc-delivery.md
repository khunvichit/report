# fc-delivery.md — Finance Control delivery choice + content

Declares which channels fire and the recipients/text. References shared IDs from `contacts.md`.
Mechanics live in `sender.md`; routing/gating in `method.md`. **Deliverable is HTML (no Excel.)**

```
Delivery:
  Channels: email + group           # full HTML report by email; short text recap to the group
  Fire email: always (weekly)        # control report — send even when "all green"
  Fire group: always
  Email key: [Finance Control] Weekly — {{date_str}}     # idempotency: search sent mail for this first
```

## Two HTML renders from the same `render.json`
- **`fc-report.html`** ← `fc-template.html` — STACKED, email-safe (inline styles, UTF-8, Thai font
  fallback). Renders inline in a Lark email. This is the email body.
- **`fc-report-tabbed.html`** ← `fc-tabbed-template.html` — TABBED standalone (pure-CSS tabs, one tab per
  section) for easy on-screen reading. Email clients strip CSS tabs, so this is a file to open/attach,
  NOT the email body.

## EMAIL — primary deliverable
- to: **owner** = `vichit@sfb.co.th` (see contacts.md); add management recipients as confirmed.
- subject: `[Finance Control] Weekly Finance Control — {{date_str}}`
- html_body: contents of **`fc-report.html`** (stacked) → `lark_send_email`. Renders inline in Lark.
- attachment (optional, recommended): **`fc-report-tabbed.html`** so recipients can open the tab view.

## GROUP (Lark) — short recap
- chat_id: **Accounting** = `oc_d8f1a40598c6c31ef7124c3755fc6cf7` (see contacts.md).
- message: render `fc-lark-summary.txt` via `fill_template.py` → send with `lark_send_message`.
- Optional: include a line "Full report emailed to <owner/management>." (the report itself is the email).

## Not used
- No task channel. (The tabbed HTML rides along as an email attachment, not a separate channel.)

## Modes (from method.md)
- `manual-test`: email the HTML report to the owner ONLY; skip the group recap. Use for first runs.
- `scheduled`: email (all recipients) + group recap. Weekly, Monday 08:00 Asia/Bangkok.
- `manual-live`: full delivery, for back-fills with `REPORT_DATE` override.
