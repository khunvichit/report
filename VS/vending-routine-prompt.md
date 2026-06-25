# vending-routine-prompt.md — Vending Services Daily Sales Report

> **THIS FILE IS THE FULL INSTRUCTION SET.** The Claude routine that runs this report has a one-line
> bootstrap in its prompt-box that says `Read vending-routine-prompt.md from the repo and
> execute every step in it exactly, in order. Run unattended — no approval prompts. Use the attached
> NetSuite and Lark connectors.` Everything below IS what the routine does. Do not skip steps. Do not
> ask the user for confirmation between steps.

Brand: **Vending Services Company Limited** · NetSuite Sub **13** · Report version **v1.0**
Repo path convention: all files live in the **same folder** (this report's working directory). The routine should `cd` into that folder once, then reference everything by bare filename.

---

## Step 0 — Determine mode

Read environment variable / routine input `RUN_MODE`. Default to `scheduled` if unset.
Allowed: `scheduled`, `manual-test`, `manual-live`.
Read optional `REPORT_DATE_OVERRIDE` (`YYYY-MM-DD`) for back-fills.

## Step 1 — Read files

Read these files from the repo (cloud routine clones fresh each run):
- `sender.md` (channel mechanics)
- `method.md` (routing engine)
- `branding.md` (CHAW CI)
- `contacts.md` (people + groups)
- `vending-template.html` (locked HTML template)
- `vending-queries.md` (SuiteQL + thresholds)
- `vending-prediction.md` (executive insight rules)
- `vending-delivery.md` (channels + recipients)
- `fill_template.py` (HTML assembler script)

If any file fails to read → STOP, post failure DM to Vichit (`contacts.vichit.open_id`), exit.

## Step 2 — Compute dates (Asia/Bangkok)

Per `vending-queries.md` date logic:
```python
report_date = REPORT_DATE_OVERRIDE or (datetime.now(ZoneInfo("Asia/Bangkok")).date() - timedelta(days=1))
D1 = report_date
D2 = D1 - timedelta(days=1)
D8 = D1 - timedelta(days=7)
MTD_START = D1.replace(day=1)
THIRTY_D_START = D1 - timedelta(days=29)
```
Compute all display tokens (`report_date_display`, `report_date_weekday_th`, etc.) per queries §"Derived display tokens".

## Step 3 — Idempotency check

Per `sender.md` Channel 1 rule:
Search Lark sent-mail for any subject containing `[Vending] Daily Sales — {report_date_display}`.
If a match exists → print `✅ Already sent for {report_date_display} — skipping entire run.` and **STOP**.

## Step 4 — Run NetSuite queries

Run Q1, Q2, Q3 from `vending-queries.md` against
`mcp__9ffe807f-86e2-4035-bda1-ad1a624d35ef__ns_runCustomSuiteQL` with fixed params (Sub 13, BU filter,
exclude `Vending HQ`). Substitute the date tokens computed in Step 2.

Retry each query ONCE on rate-limit / 5xx (wait 30s). Do NOT restart the routine on transient errors.
On a second failure → STOP, post failure DM, exit.

## Step 5 — Completeness checks

Run all 6 checks listed in `vending-queries.md` §"Completeness checks". Any failure → STOP, post DM
with the specific failed check, exit. NEVER send a partial / zero-row report.

## Step 6 — Compute derived metrics

From the query rows:
- Aggregate per (BU, day), (airport via `airport_of()`, day), (machine, day).
- Per-machine MTD baselines (`mtd_avg_rev_m`, `mtd_avg_bills_m`, `mtd_high_m`, `mtd_low_m`).
- Per-machine D1 vs D2 vs D8 deltas → `dod_pct`, `wow_pct`.
- Per-machine severity via `severity(...)` function in queries file.
- Per-machine `mtd_flag` per runbook §6 Pillar 1.
- Split machines into Problem vs OK lists.
- For each Problem machine, evaluate the 4 service-ticket triggers per delivery file.
- Per-BU heatmap deltas (revenue/bills/ticket WoW) + signal per 3×3 matrix.

## Step 7 — Build data.json

Per `vending-prediction.md` rules, generate `repeats.insight_bullets` (4–6 bullets max).
Then assemble the full `data.json` containing:
- `scalars` — every `{{token}}` in the template (header values, KPIs, totals, MTD figures).
- `repeats` — `insight_bullets`, `chart_days_bu`, `chart_days_airport`, `bu_legend_rows`,
  `airport_legend_rows`, `heatmap_rows`, `problem_machine_rows`, `ok_machine_rows`,
  `next_action_rows`.
- `sections` — `draft_banner` (true if `manual-test`), `data_quality_banner` (true if any silent
  machines or new locations detected).

Write `data.json` to the routine's working directory.

## Step 8 — Run fill_template.py

Execute:
```bash
python3 fill_template.py vending-template.html data.json > out.html
```
- If stderr contains `WARNING unresolved placeholders:` → STOP, post DM with the leftover token names,
  exit. Never send a report with unfilled `{{tokens}}`.
- Otherwise `out.html` is now the final email body.

## Step 9 — Channel 1: Email

Per `method.md` mode table:
- `scheduled` / `manual-live` → `to = [management@chaw.co.th, vendi@chaw.co.th]`
- `manual-test` → `to = [vichit@chaw.co.th]` only

Build subject from `vending-delivery.md` subject pattern using the scalars from Step 7.

Call `mcp__7de72e5f-3664-41c0-9775-5d13bd8722f1__lark_send_email`:
- `to`: per mode
- `subject`: built above
- `body`: contents of `out.html` (read from disk — do NOT pass through model output)
- `body_type`: `"html"`

Capture and log the email response. On failure → log to console summary, continue (Step 10).

## Step 10 — Channel 2: Tasks (gated)

Skip this step if:
- `RUN_MODE == "manual-test"` (test mode never creates real tasks), OR
- Gate `problem_machine_count == 0`.

For each Problem machine:
1. Build the task `summary`, `description`, `due` per `vending-delivery.md` templates.
2. Call `mcp__7de72e5f-3664-41c0-9775-5d13bd8722f1__lark_create_task` with assignees =
   `[qt_sarun.open_id, qt_ploynaphat.open_id, qt_surachai.open_id]` per `contacts.md`.
3. Capture the returned `task_guid` and `task_url`.
4. For each follower in `[vichit.open_id, aekkaphop.open_id]`, call
   `mcp__7de72e5f-3664-41c0-9775-5d13bd8722f1__lark_add_task_members(task_guid, [open_id], role="follower")`
   in a SEPARATE call (per `sender.md` Channel 2 rule).

Collect `(task_summary, task_url, severity)` for each task — used by Step 11.

## Step 11 — Channel 3: Group post (gated)

Skip this step if:
- `RUN_MODE == "manual-test"`, OR
- Gate `total_rev_d1 == 0`.

Build the group text message per `vending-delivery.md` `message_template`, embedding the `task_url`s
from Step 10. Call `mcp__7de72e5f-3664-41c0-9775-5d13bd8722f1__lark_send_message`:
- `receive_id_type`: `"chat_id"`
- `receive_id`: `oc_f25274999f6561e6f1e484102ee198e7` (Food Operation Core, from contacts.md)
- `msg_type`: `"text"`
- `content`: `{"text": "<the message>"}` JSON-stringified

On failure → retry once against the fallback `chat_id` if declared (none configured yet), else log
and continue to Step 12.

## Step 12 — Console summary

Print exactly the format from `sender.md` §"Console summary":
```
✅ Vending Daily Report — {report_date_display}
   Total: ฿{total_rev_d1:,.0f} · WoW {wow_signed}% · DoD {dod_signed}%
   Mode: {RUN_MODE}
   Channels fired: email={Y/N} · task={n}/{problem_machine_count} · group={Y/N/gated-off}
   📧 Email → {to_list}
   📋 Tasks created: {n_tasks} · Follower calls: {n_tasks × 2}
   💬 Group → Food Operation Core
```

## Step 13 — Failure-notification

If any step in 4–11 raised a hard error and was not silently recovered, post a Lark DM to Vichit
(`contacts.vichit.open_id`) with:
```
❌ Vending Daily failed at Step {n} — {step_name}
   Reason: {error_message}
   Mode: {RUN_MODE} · D1={report_date_display}
```

Do not auto-retry. The next scheduled run handles it.

---

## Manual back-fill usage

To re-run for a specific past day:
```
RUN_MODE=manual-live
REPORT_DATE_OVERRIDE=2026-05-20
```
The idempotency check (Step 3) will still skip if a previous run already sent for that date. To
force-resend after a fix, manually delete the sent-mail thread for that subject first, then re-run.

## First-run validation checklist (Mode = `manual-test`)

1. Files read cleanly from repo. HTML template not Drive-mangled.
2. `report_date` resolves to yesterday Asia/Bangkok (not UTC).
3. Q1/Q2/Q3 return data; all 6 completeness checks pass.
4. `fill_template.py` produces `out.html` with no `WARNING unresolved placeholders:` line.
5. Stacked-bar nested cells fill (30 day columns, no empty bars).
6. Email arrives at `vichit@chaw.co.th` only. No real tasks created. No group post.

Then flip `RUN_MODE` to `scheduled` and enable the 07:30 Asia/Bangkok daily trigger.
