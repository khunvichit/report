# sender.md — Channel mechanics (shared, never per-BU)

All three delivery channels use the **Lark MCP server**. This file is purely mechanical — recipients,
chat_ids, and copy live in the per-report `<brand>-delivery.md`. Editing this file changes how *every*
report sends; editing a delivery file changes only one report.

---

## Channel 1 — Email

**Tool**: `lark_send_email`

**Rule of thumb**: send the HTML body as the **contents of a file**, never as a string assembled in
model output. `fill_template.py` writes `out.html` to disk; the routine reads that file and passes
its contents to `lark_send_email`. This is the only thing that keeps the routine under the 32K
output-token ceiling.

**Parameters**:
- `to` — list of email addresses (see per-report delivery file).
- `cc` — list, optional.
- `subject` — built from the email-key pattern declared in the delivery file.
- `body` — full HTML string read from `out.html`.
- `body_type` — `"html"`.

**Idempotency check** — BEFORE calling `lark_send_email`, search Lark sent-mail for any subject
containing the exact email-key prefix (e.g. `[Vending] Daily Sales — 25 May 2026`). If found,
log "✅ already sent for {report_date_display} — skipping" and SKIP the email step (and group / task
steps too — the whole run is idempotent). This prevents double-sends if a routine fires twice.

**Lark AI disclaimer** — Lark appends its own AI disclaimer to outgoing email. Do NOT add another one
in the email body.

---

## Channel 2 — Task

**Tools**: `lark_create_task` + `lark_add_task_members` (called separately, per follower).

**Why separate calls**: `lark_create_task` accepts `members` as assignees, but followers cannot be
attached at creation. They must be added one-by-one with `lark_add_task_members(task_guid, [open_id],
role="follower")` after the task exists. Loop through the follower list; one MCP call per follower.

**Parameters for `lark_create_task`**:
- `summary` — task title (per-report delivery file supplies the pattern).
- `due` — `YYYY-MM-DDTHH:MM:SS+07:00` format (Asia/Bangkok offset).
- `description` — multi-line text body. Newlines are honoured.
- `members` — list of `{user_open_id, role:"assignee"}` for each Quality Team / area-manager assignee.
- Do NOT set `tasklist_guid` (cloud API returns empty for `lark_list_tasklists` — leave default).

**After creation**: capture the returned `task_guid` and call
`lark_add_task_members(task_guid, [follower_open_id], role="follower")` once per follower listed in
the delivery file.

**Capture `task_url`** from the create response so the email's Next Actions section can hyperlink it.

---

## Channel 3 — Group message

**Tool**: `lark_send_message`

**Parameters**:
- `receive_id_type` — `"chat_id"`.
- `receive_id` — the chat_id from the per-report delivery file.
- `msg_type` — `"text"` (HTML is not allowed in group messages; use plain text).
- `content` — JSON-stringified `{"text": "..."}`. Multi-line text is OK; use `\n` inside the string.

**Fallback chat_id** — if the primary chat_id returns an error (group removed, bot kicked), retry once
against the fallback chat_id declared in the delivery file. Don't loop.

---

## Order of channel calls

Always: **email → task → group**. Reasons:
1. Email subject is the idempotency key — if email skips, everything skips.
2. Tasks return URLs that the group message references — tasks must exist before the group post.
3. Group is the noisiest channel; sending it last means a partial failure is at least quiet.

---

## Console summary (printed by every routine after delivery)

```
✅ <Brand> Daily Report — {report_date_display}
   Total: ฿{total:,.0f} · WoW {wow:+.1f}% · DoD {dod:+.1f}%
   Mode: {scheduled | manual-test | manual-live}
   Channels fired: email={Y/N/skipped} · task={count}/{N} · group={Y/N/gated-off}
   📧 Email → {to_list}
   📋 Tasks created: {n_tasks} · Followers added: {n_follower_calls}
   💬 Group → {chat_id_label}
```

The console summary is the routine's only authoritative log line. If a step failed, include the
failure message inside the summary so the failure-notification step can re-post it.
