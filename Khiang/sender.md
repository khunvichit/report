# sender.md — channel mechanics (shared, never per-BU)

HOW each Lark channel works. Purely mechanical — no recipients/IDs (those live in delivery files).
All three channels use the Lark MCP server (prefix `mcp__7de72e5f-3664-41c0-9775-5d13bd8722f1__`).

## Email — `lark_send_email`
- `body` accepts full inline HTML; JS is stripped by clients — never rely on scripts.
- **THE TOOL CANNOT READ FILES.** `body` must contain the LITERAL FULL CONTENTS of `email.html`:
  READ the file first, then paste the entire HTML string into the `body` argument of the tool
  call. Tool-call arguments do NOT count against the output-token limit — only assistant text
  does. The "never output the full HTML" rule means: don't print it as chat/text output; passing
  it inside a tool argument is required and correct.
- **NEVER put a file path, `FILE:...`, or any placeholder in `body`.** (This bug shipped 3 days
  in a row: recipients got an email whose entire body was `FILE_CONTENT_PLACEHOLDER`, followed
  by a CORRECTION email.)
- **Pre-send check (hard):** the `body` string must start with `<!DOCTYPE` or `<html` and be
  >20,000 characters. If not, DO NOT send — re-read `email.html` and rebuild the call.
- Send EXACTLY ONCE. Never send a broken email "to fix later" and never follow up with a
  CORRECTION email — a failed pre-send check means fix first, then send the one good email.
- Lark auto-appends an AI disclaimer — do not add your own.

## Task — `lark_create_task` (+ `lark_add_task_members`)
- Omit `tasklist_guid` to create in the default workspace (listing tasklists returns empty unless
  Claude's account is a member).
- Add each assignee/follower in a SEPARATE `lark_add_task_members` call (one per person).
- Due time format: `YYYY-MM-DDTHH:MM:SS+07:00` (ICT). Due dates returned as epoch ms UTC → convert
  to UTC+7 when reading.

## Group message — `lark_send_message`
- `receive_id_type: "chat_id"`, `msg_type: "text"`.
- Each report supplies a primary chat_id + a fallback; on send failure to primary, try fallback.

## Idempotency (shared)
Before sending email, search sent mail for the exact Email-key subject for REPORT_DATE. If found →
STOP (already sent today). Run the whole routine EXACTLY ONCE per day.

## Console summary (shared shape)
```
✅ <Brand> Daily Report — {report_date_display}
   Net Sales: ฿{net_sales} ({signed_pct}%)  Bills: {total_bills}  Anomalies: {anomaly_count}
   📧 email → {recipients}   💬 group → {chat_id}   (task channel off)
```
