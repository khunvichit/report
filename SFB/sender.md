# SFB — Sender (channel MECHANICS)

HOW each channel works. Purely mechanical — no recipients, addresses, or IDs (those live in
`sfb-delivery.md`). All channels use the Lark MCP connector.

## Channels in use
- **Email** — `lark_send_email`. Body = contents of `email.html` produced by `fill_template.py`.
  Never write HTML to disk as the deliverable; pass the file contents to the tool.
- **Group message** — `lark_send_message` (receive_id_type = `chat_id`), plain text.
- **Task** — DISABLED for this report. `lark_create_task` / `lark_add_task_members` are not called.

## Rules
- **Idempotency:** before sending email, search sent-mail for the exact Email key subject
  (`sfb-delivery.md`). If found and mode == scheduled → STOP ("already sent"). Skip in manual-* modes.
- **AI disclaimer:** Lark auto-appends its AI disclaimer to messages — do not add your own.
- **Group fallback:** the group has a primary `chat_id` and a fallback owner DM (`OWNER_OPEN_ID`).
  If the primary group send fails, DM the owner instead. Never fail silently.
- **Email retry:** on send failure, retry once; if still failing, DM the owner the HTML body.
- **Env only for identity:** read `OWNER_EMAIL` / `OWNER_OPEN_ID` from the environment; never
  hardcode personal addresses or open_ids in the repo.
- **Timestamps** (if ever needed): `YYYY-MM-DDTHH:MM:SS+07:00` (Asia/Bangkok).

## Console summary (print at end)
mode · report_date · total revenue + WoW · MTD avg + D1-vs-avg · locations · bills ·
severity counts (SURGE/POSITIVE/NEUTRAL/WATCH/HIGH/CRITICAL) · email recipients · group target ·
tasks: disabled.
