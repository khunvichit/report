# sender.md — channel mechanics (shared, never per-BU)

HOW each Lark channel works. Purely mechanical — no recipients/IDs (those live in delivery files).
All three channels use the Lark MCP server (prefix `mcp__7de72e5f-3664-41c0-9775-5d13bd8722f1__`).

## Email — `lark_send_email`
- `body` accepts full inline HTML; JS is stripped by clients — never rely on scripts.
- HTML comes from a FILE (`email.html` produced by `fill_template.py`), never from model output.
- Do NOT write the HTML to disk as a *deliverable*; the file is an intermediate the routine reads.
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
