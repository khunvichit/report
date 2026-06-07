# CHAW Reporting — METHOD (shared)

The **routing logic**: which of the 3 channels fire for a given run, in what order, and under what condition.
This answers *"which channels fire and when?"* It is the common framework; reports only declare their choice.

Pair with: `sender.md` (how each channel works) · each report's runbook (the content + the declaration).

---

## How a report declares its method

Each report's runbook includes a **Delivery** block, e.g.:

```
Delivery:
  Channels: email + task + group        # any subset of: email, task, group
  Fire task + group only if: {condition} # optional gate; default = always
  Email key: [Juiceland] Daily Sales Report — {report_date_display}
```

Common patterns:
- `Channels: email` — email-only report (no task, no group).
- `Channels: email + task` — email plus a follow-up task.
- `Channels: email + task + group` — full report (Juiceland, ActionCity, etc.).

---

## Order of operations (fixed)

1. **Dates** — compute per the report (Asia/Bangkok). Honour any manual override.
2. **Idempotency** — run the email-key check from `sender.md`. If already sent → STOP.
3. **Completeness** — run the report's data checks. If a hard check fails → STOP, report, do not send.
4. **EMAIL** — if `email` in Channels, build HTML and send (Channel 1).
5. **LARK TASK** — if `task` in Channels AND its gate passes, create task + add members (Channel 2).
   Capture `task_guid` for the group message.
6. **LARK GROUP** — if `group` in Channels AND its gate passes, post message (Channel 3),
   including the task link if a task was created.
7. **CONSOLE** — print the summary from `sender.md`.

---

## Gating (the "sometimes" logic)

- **Email** almost always fires unconditionally (it's the record). Default: always.
- **Task** and **Group** are the conditional ones. A report sets a single gate, e.g.
  `am_queue_count + dormant_count > 0`. If the gate is false:
  - skip the task → print `skipped: no items needing review`
  - skip the group → print `skipped: no anomalies`
- A channel not listed in `Channels` is simply never attempted (different from "gated off").

> Distinction: **not listed** = this report doesn't use that channel at all.
> **Gated** = this report uses it, but only when there's something worth sending.

---

## Failure handling

- A channel failing does NOT abort the others. Send what you can; report the failure in the console line.
- Email idempotency hit or completeness failure DO abort the whole run (steps 2–3 are hard stops).
- Tool auth errors → report clearly; do not silently skip.
