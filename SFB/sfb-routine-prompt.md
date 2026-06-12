# SFB Daily Sales Report — Routine Prompt

> **THIS FILE IS THE FULL INSTRUCTION SET.** Execute every step below in order, unattended, with no
> approval prompts. Read the referenced files from the repo; do not reconstruct their contents from
> memory. Use the attached **Chaw Netsuite (Read-only)** and **Lark** connectors. Paths below are
> relative to the repo root.

## Invocation (what the trigger line means)
- `Run SFB daily report` → mode `scheduled`, report date = yesterday (Asia/Bangkok).
- `Run SFB daily report for D1=YYYY-MM-DD` → mode `manual-live` back-fill (REPORT_DATE override).
- `Run SFB daily report in TEST mode` → mode `manual-test` (email OWNER_EMAIL only, skip group post).
Default when unspecified: `scheduled`. No further confirmation is requested in any mode.

## Hard rules (non-negotiable)
1. **Timezone:** compute all dates in Asia/Bangkok; never server UTC. If the resolved report date
   is not yesterday-BKK (and no explicit D1 override), STOP and report.
2. **Completeness gate:** run the checks in sfb-queries.md; HARD-STOP on any failure. Never send
   zeros or a partial day.
3. **Never emit HTML:** build `data.json` and run `fill_template.py` to assemble the email. If its
   stderr lists unresolved tokens, fix `data.json` and re-run before sending — never hand-write HTML.
4. **Delivery from files:** recipients, subject, and the Food Operation Core group message come from
   sfb-delivery.md. **Lark tasks are disabled.**
5. **Fail loud:** on any hard stop (NS down after retry, completeness fail, email+retry fail), post
   the failed step + reason to the group (or DM the owner). Never exit silently. No whole-routine retry.
6. **Env:** read `OWNER_EMAIL` and `OWNER_OPEN_ID` from the environment; never hardcode personal addresses.

## Files this routine reads
- `SFB/sfb-template.html`  — locked HTML (never regenerate; fill with code)
- `SFB/sfb-queries.md`     — NetSuite SuiteQL + Odoo hourly + completeness checks
- `SFB/sfb-prediction.md`  — severity / MTD flags / heatmap / insight method
- `SFB/sfb-delivery.md`    — channels (email + group; task OFF), recipients, subject, group message
- `SFB/fill_template.py`   — HTML assembler
- root `sender.md`, `method.md`, `branding.md` — shared mechanics/routing/CI

## Modes (from method.md)
`scheduled` (default; email to recipients + group), `manual-test` (email to OWNER_EMAIL only, skip
group), `manual-live` (full; for back-fills with REPORT_DATE override). Read mode from invocation;
default `scheduled`.

## Steps

1. **Read files.** Load the 6 files above + shared files. Confirm the template loaded intact.
2. **Dates (Asia/Bangkok, at runtime).** Per sfb-queries.md: D1 = yesterday-BKK (or REPORT_DATE
   override), derive D2, D8, MTD_START, TREND_START, and all display tokens.
3. **Idempotency.** Search Lark sent-mail for Email key `[SFB] Daily — {report_date_display}`.
   If found and mode == scheduled → print "already sent" and STOP. Skip this check in manual-* modes.
4. **NetSuite responsiveness.** `SELECT id FROM transaction WHERE rownum = 1`. Empty/error → wait 5s,
   retry once. Still failing → go to Failure path.
5. **Queries.** Run Q1–Q3 only. (Q4 Khiang hourly and Q5 Odoo hourly are DISABLED this build — the
   Hourly Drill section was removed; do not run them.) Honor rate limits (20–90s between retries; one
   retry each). Then flag severity (prediction.md A–C). Severity feeds the heatmap signal and ranks
   location×BU rows by rev WoW for the group message's top/weakest movers.
6. **Completeness checks (HARD GATE).** Run all checks in sfb-queries.md. Any failure → do NOT build
   or send; go to Failure path with the specific failed check. Timezone guard (report_date ≠
   yesterday-BKK) is a hard stop.
7. **Aggregate + classify.** Build per-BU, per-airport, per-location×BU rollups; MTD avg/high/low;
   heatmap signals; executive-insight bullets (prediction.md D–E, describe-don't-diagnose).
8. **Build `data.json` — NOT HTML.** Compute scalars, repeats (chart days+axis, BU+airport legends,
   loc_heatmap_rows). For loc_heatmap_rows: group by location, order groups by location total D1 rev
   desc, merge the Location cell via the `loc_cell`/`row_class` tokens, and color every Δ cell with the
   continuous `grad()` gradient (all per prediction.md D). No `sections` are needed — the
   Sales-by-Branch tables, Hourly Drill, and the Replicate—SURGE section are all removed, so do NOT
   build `problem_branch_rows`, `ok_branch_rows`, `hourly_blocks`, or `surge_rows`, and do not set
   `hourly_drill` or `surge_fyi`. Chart bar heights are
   PIXELS: `HEIGHT=240`, leave 20px header, `PIXEL_PER_BAHT=(HEIGHT-20)/MAX_DAILY` — use the SAME
   factor for BU and Airport charts. **The model must not emit the HTML (32K token crash).**
9. **Assemble HTML.** `python3 SFB/fill_template.py SFB/sfb-template.html data.json > email.html`.
   If stderr reports unresolved placeholders, add them to data.json and re-run; do NOT send with
   unresolved money/date tokens.
10. **Send email** (sender.md mechanics; recipients/subject from sfb-delivery.md per mode). Pass
    `email.html` contents to `lark_send_email`. Failure → retry once → else post HTML body to owner DM.
11. **Group post (gated).** In scheduled/manual-live: build `top_movers_block` / `bottom_movers_block`
    (top/bottom 3 location×BU rows by rev WoW, format in sfb-delivery.md), then post the group message
    to `oc_f25274999f6561e6f1e484102ee198e7` (Food Operation Core); on failure, DM owner. Skip in
    manual-test. The message carries location×BU movers only — no BU aggregate, problem count, or
    replicate list. **No Lark tasks** — task channel is disabled.
12. **Failure path (fail loud).** On any hard stop (NS down, completeness fail, email+retry fail):
    do NOT silently exit — post to Food Operation Core (or DM owner) naming the failed step and reason.
    No auto-retry of the whole routine.
13. **Console summary.** Print: mode, report_date, total revenue + WoW, MTD avg + D1-vs-avg, locations,
    bills, severity counts (SURGE/POSITIVE/NEUTRAL/WATCH/HIGH/CRITICAL), problem-branch count,
    email recipients, group target. (Tasks: disabled.)
