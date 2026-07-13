# sender.md — channel mechanics (shared, never per-BU)

HOW each delivery channel works. All three use the Lark MCP server. Keep this file purely mechanical —
recipients/IDs live in `contacts.md` / the per-report delivery file, NOT here.

## Channels & tools
- **Email** — `lark_send_email`. Pass the rendered HTML (from `fill_template.py` → `fc-report.html`) as the
  body. This is the full report; no attachment. Don't keep the HTML as a deliverable beyond the temp file.
- **Group message** — `lark_send_message` with `receive_id_type=chat_id`, `msg_type=text`. Body = the
  rendered `lark_summary.txt`.
- **File** — `lark_send_file` attaches a file to a chat (generic mechanic; not used by Finance Control, which is HTML-only).
- **Task** (if a report uses it) — `lark_create_task`, then `lark_add_task_members` in SEPARATE calls,
  one per person. Due-time format `YYYY-MM-DDTHH:MM:SS+07:00`.

## Rules
- **Idempotency:** before sending, search sent mail for the report's Email-key subject; if found for this
  `report_date`, skip (prevents double-sends on re-runs).
- **AI disclaimer:** Lark auto-appends one — do not add your own.
- **Connectors on the routine:** NetSuite + Lark must be enabled on the routine itself (cloud OAuth can
  expire — another reason to fail loud).
- **Lark server prefix** (interactive): `mcp__7de72e5f-3664-41c0-9775-5d13bd8722f1__lark_*`.
- **NetSuite SuiteQL** (interactive): `mcp__9ffe807f-86e2-4035-bda1-ad1a624d35ef__ns_runCustomSuiteQL`
  (param `query`). In a routine, use whatever NetSuite connector is attached.

## Console summary format
`<report> <report_date> mode=<mode> | sent: <channels> | skipped: <channels+reason> | <key metrics>`
