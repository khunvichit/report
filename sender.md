# CHAW Reporting — SENDER (shared)

The **mechanics** of the three delivery channels. This answers *"how do I operate each channel?"*
It never changes between reports. Reports do not redefine these — they reference this file and supply only content.

Pair with: `method.md` (which channels fire, and when) · each report's runbook (the content).

> All three channels use the Lark MCP server.
> Server prefix used below: `mcp__7de72e5f-3664-41c0-9775-5d13bd8722f1__`

---

## Channel 1 — EMAIL

**Tool:** `mcp__7de72e5f-3664-41c0-9775-5d13bd8722f1__lark_send_email`

Rules:
- **Email only. Do NOT write the HTML to disk in production.** Pass the built HTML body straight to the tool.
- Lark auto-appends an AI disclaimer — do not add your own.
- HTML body is built by the report (its template + data). The sender just transmits it.

**Idempotency (always run before sending):**
Search Lark sent-mail for a subject containing the report's unique key
(e.g. `[Juiceland] Daily Sales Report — {report_date_display}`).
If found → print `✅ Already sent for {key} — skipping.` and STOP the whole routine.

Report supplies: `to[]` (address + name), `subject`, `html_body`.

---

## Channel 2 — LARK TASK

**Tool:** `mcp__7de72e5f-3664-41c0-9775-5d13bd8722f1__lark_create_task`
**Members tool:** `mcp__7de72e5f-3664-41c0-9775-5d13bd8722f1__lark_add_task_members`

Rules:
- Create the task first, then add members with **separate `lark_add_task_members` calls** — one per person (assignees + followers). Do not batch.
- Due time format: `YYYY-MM-DDTHH:MM:SS+07:00` (Asia/Bangkok).
- Typical due rule: `{report_date + 1} 17:00 +07:00` (next-day end of business) unless the report overrides.

**Standing user open_ids (reuse — do not re-resolve):**

| Person | Email | open_id | Usual role |
|--------|-------|---------|------------|
| Vichit | vichit@chaw.co.th | `ou_434e5b57a3d9250d73110111104add49` | Follower (most reports) |
| Sarun | sarun@chaw.co.th | `ou_e521461e04d698168412f3c4f9a199d4` | Assignee |
| Ploynapat | ploynapat@chaw.co.th | `ou_dffd3de6811a4bad31d2f5398dd277b9` | Assignee |

> Add more people here as reports need them, so they're resolved once and reused everywhere.

Report supplies: `summary`, `due` (or "use standard rule"), `assignees[]`, `followers[]`, `description`.

---

## Channel 3 — LARK GROUP NOTIFICATION

**Tool:** `mcp__7de72e5f-3664-41c0-9775-5d13bd8722f1__lark_send_message`

Rules:
- Post to the report's primary group. If it fails, retry once on the fallback group.
- If the report links a Lark task, include the task deep link:
  `https://applink.larksuite.com/client/todo/detail?guid={task_guid}`

**Standing group chat_ids (reuse):**

| Group | chat_id | Note |
|-------|---------|------|
| Quality (primary) | `oc_1720a4005f44033a8ad78aa60a63216b` | F&B quality/ops |
| Food Operation Core (fallback) | `oc_f25274999f6561e6f1e484102ee198e7` | fallback for Quality |

> Add other groups here as reports need them.

Report supplies: `chat_id` (+ fallback), `message`.

---

## Console output (after all selected channels run)

Print a compact summary of what fired:
```
📧 Email sent    → {recipients}            (or "skipped: {reason}")
📋 Lark task     → {task_guid}             (or "skipped: {reason}")
💬 Group msg     → {chat_id}               (or "skipped: {reason}")
```
