# method.md — Routing rules (shared engine)

This file is the engine that reads each report's delivery declaration and decides which channels fire
in what order under what gate. **It does not change per report.** Each report only changes its own
`<brand>-delivery.md` file's `Channels:` line, gates, and content.

---

## The channel menu

A report may declare any subset of:

- `email` — HTML body to `to` + optional `cc`. Usually always declared.
- `task` — one or more Lark tasks. Used by reports with operational follow-up (CCTV / service tickets).
- `group` — text summary posted to a Lark group chat. Used by reports with a daily morning huddle.
- *(optional)* `archive` — write a row to a Lark Base / Sheet for historical retention. Not yet used.

---

## How a report declares delivery

Every per-report `<brand>-delivery.md` must contain a `Delivery:` header block:

```
Delivery:
  Channels: email + task + group           # this report's choice
  Fire task only if: <gate condition>      # optional — defaults to "always"
  Fire group only if: <gate condition>     # optional — defaults to "always"
  Email key: [<Brand>] <Report> — {report_date_display}
```

Then content blocks per declared channel (EMAIL, TASK, GROUP). Disabled channels can be kept
commented out for easy re-enable; the routine simply doesn't fire them.

**Distinguish "not declared" from "gated off":**
- A channel **not declared** at all → never used by this report.
- A channel **declared with a gate** → used, but only when the gate is true (e.g. only fire `task`
  if `problem_machine_count > 0`).

---

## Fixed order of operations

The routine runs these steps in this exact order, every time:

1. **Read files** — template, queries, prediction, delivery, contacts, sender, method, branding.
2. **Compute dates** — `report_date = now(Asia/Bangkok).date() − 1` unless `REPORT_DATE` is supplied.
3. **Idempotency check** — search Lark sent-mail for the email-key prefix. If found → STOP whole run.
4. **Run queries** — execute the SuiteQL queries from `<brand>-queries.md` against NetSuite.
5. **Completeness checks** — gate the send. Hard-stop if any check fails (see queries file).
6. **Prediction** — if a `<brand>-prediction.md` exists, compute forecast/commentary scalars.
7. **Build data.json** — assemble `scalars / repeats / sections` (the model writes data, not HTML).
8. **`fill_template.py`** — produce `out.html` by mechanical substitution. STOP if it warns of
   unresolved tokens (don't send a half-filled report).
9. **Channel 1 — Email** — call `lark_send_email` if `email` is declared (almost always).
10. **Channel 2 — Task** — if `task` declared, evaluate the gate; if true, loop through the task list,
    create each, then add followers in separate calls (see `sender.md`).
11. **Channel 3 — Group** — if `group` declared, evaluate the gate; if true, build the text message
    (including task URLs from Channel 2), call `lark_send_message`.
12. **Console summary** — print the standard `sender.md` summary line.
13. **Failure-notification step** — if any hard step failed, post `❌ <Brand> Daily failed: <step> —
    <reason>` to the owner's Lark DM (open_id from contacts.md). No silent failures.

---

## Modes

Routines support three modes via an `RUN_MODE` env var (or the routine config UI):

| Mode | Email goes to | Tasks created? | Group posted? | Use case |
|------|---------------|----------------|---------------|----------|
| `scheduled` (default) | full `to` + `cc` from delivery file | yes (if declared + gate true) | yes (if declared + gate true) | Daily 07:30 ICT cron |
| `manual-test` | owner only (Vichit) | NO (dry-run list rendered in email body) | NO | First runs after any change |
| `manual-live` | full `to` + `cc` | yes | yes | Manual back-fill for a missed day |

The mode is read at step 1 and applied at steps 9/10/11. Idempotency (step 3) and completeness
(step 5) apply in all modes equally — never send a partial/zero report regardless of mode.

---

## Gating semantics

A gate is a Python-like expression that the routine evaluates against the scalar/section dict
*after* step 7 (data.json build) but *before* the channel fires.

Examples:
- `Fire task only if: problem_machine_count > 0` — no problems, no tickets.
- `Fire group only if: total_revenue > 0` — silent if the day really had zero sales.
- `Fire task only if: severity_critical_count + severity_high_count > 0` — only escalate real issues.

The gate condition lives in the delivery file. method.md just evaluates it.

---

## Failure handling

- A failing channel **does not abort** the others. (e.g. group post fails → email + tasks already sent
  successfully; log group failure in the console summary, post the failure notification, continue.)
- Idempotency (step 3) and completeness (step 5) are **hard stops** — they abort the entire run.
- The routine NEVER auto-retries within the same run. Any temporary failure → fail loud, send a Lark
  DM to the owner, exit. The next scheduled run picks it up.
- Cloud OAuth tokens can expire silently. If a Lark call returns auth error, the failure-notification
  step itself may also fail — that's why the console summary is the authoritative log; review it
  daily for the first 1–2 weeks of a new report.
