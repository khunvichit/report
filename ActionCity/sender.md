# sender.md — channel MECHANICS (shared, never per-BU)

How each of the 3 Lark channels works. Recipients/IDs do NOT live here (see delivery.md / contacts.md).

## Tools (Lark MCP)
- **Email:** `lark_send_email` — pass `to[]`, `subject`, and the HTML body STRING (read from `email.html`).
  Do not write the HTML to disk as a deliverable; it is only an intermediate for the email body.
- **Task:** `lark_create_task` to create, then `lark_add_task_members` in SEPARATE calls (one per person).
  Due time format `YYYY-MM-DDTHH:MM:SS+07:00`.
- **Group:** `lark_send_message` with `chat_id`. Each report supplies a primary + fallback chat_id.

## Rules
- **Idempotency:** before email, search sent mail for the exact Email-key subject; if present, skip the send.
- **Add task members one per call** (batched calls fail silently).
- **Lark auto-appends an AI disclaimer** to messages — do not add your own.
- **Group fallback:** if the primary chat_id send fails, try the fallback chat_id once, then fail loud.
- **Console summary** after every run: mode, report_date, channels fired, email key, failures.

> Keep this file purely mechanical. If you're tempted to write an email address or chat_id here, it
> belongs in `contacts.md` or the report's `delivery.md` instead.
