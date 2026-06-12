# ActionCity Daily Report — Routine Prompt

> **THIS FILE IS THE FULL INSTRUCTION SET.** The routine executes every step below, in order,
> unattended (no approval prompts). All paths are relative to the repo root. Use the attached
> NetSuite + Lark connectors. Do not improvise beyond these steps.

## Inputs / files to read first
- `ActionCity/actioncity-queries.md` — data layer (SuiteQL, fixed params, date logic, completeness).
- `ActionCity/actioncity-prediction.md` — insight bullets + rule-based flags/colours.
- `ActionCity/actioncity-delivery.md` — channels, recipients, subject, group message.
- `ActionCity/actioncity-template.html` — locked layout (DO NOT regenerate).
- `method.md`, `sender.md`, `branding.md`, `contacts.md` — shared engine + IDs.
- `ActionCity/fill_template.py` — HTML assembler.

## Steps

0. **Freshness preflight (no stale data).**
   - **Delete** any `data.json` and `email.html` left in the working dir from a previous run. Never reuse them.
   - The repo must NOT contain a committed `data.json`/`email.html` (only the template + sample). If one is present, ignore it.
   - Lint the template: `python3 ActionCity/preflight_check.py lint ActionCity/actioncity-template.html`. It must pass (the template holds only `{{tokens}}`, no baked-in numbers). If it fails → fail loud, do not run.
1. **Mode.** Read `MODE` env (default `scheduled`). Read optional `REPORT_DATE` override.
2. **Dates (Asia/Bangkok).** This is an END-OF-DAY routine: `report_date = now(Asia/Bangkok).date()`
   (or REPORT_DATE). Derive `iso_week`, `w_minus1..w_minus4`, `wtd_start`, `wtd_days`, week windows,
   and display tokens. NEVER use bare server/UTC time.
3. **Idempotency.** Search sent mail for the Email key subject for report_date. If already sent → log and STOP.
4. **Queries.** Run sections A–J from `actioncity-queries.md`. Net sales = `-SUM(tl.netamount)`
   (NOT ABS). Apply universal filters + `netamount<>0`. Retry a failed query once (wait 20–90s).
5. **Completeness (HARD-STOP on fail).** Run all checks in the queries file:
   today has rows; ≥6 weeks present; staffed stores present; net ≤ invoices (sign sanity);
   report_date == today-BKK. On any hard fail → go to step 9 (fail loud), do NOT send.
6. **Prediction.** Compute `insight_rows[]`, `group_flag_line`, and all rule-based flags/colours
   per `actioncity-prediction.md`. Describe-don't-diagnose; only cite figures in the data.
7. **Build `data.json`** — `{scalars, repeats, sections}` keyed to every template token, ALL from
   this run's query results. **Do NOT emit the HTML in model output** (32K-token crash). **Do NOT
   copy numbers from the sample, a prior run, or this prompt** — every value must trace to a step-4 query.
   Write data.json to disk. Then **freshness self-check (hard gate):**
   - `python3 ActionCity/preflight_check.py fresh data.json <report_date>` must pass (report_date_display = today; day_net non-zero; week_rows present).
   - **Control-total recheck:** re-run the today-total query once; assert its net == `scalars.day_net`. If they differ, the data.json is stale/mismatched → STOP, fail loud.
8. **Assemble + send.**
   - `python3 ActionCity/fill_template.py ActionCity/actioncity-template.html data.json > email.html`
   - If stderr lists unresolved `{{tokens}}` → fix data.json and re-run; never send unresolved money/date tokens.
   - Per `method.md` order: email (always) → group (gated by mode). `manual-test`: email to owner only, skip group.
   - Email body = contents of `email.html` via `lark_send_email`. Group via `lark_send_message` with the short card from delivery.md.
9. **Fail loud.** On hard failure (query/completeness/send): do NOT auto-retry the run; post to the
   `actioncity_ops_group` (or DM owner vichit@sfb.co.th) which step failed and why. Silent failure is the worst outcome.
10. **Console summary.** Print: mode, report_date, weeks loaded, completeness pass/fail, channels fired, email key, any flags.

## Guardrails (do not violate)
- Model never outputs the full HTML — only small `data.json` + short status.
- Net sales = invoices − returns (`-SUM(netamount)`); wash lines excluded (`netamount<>0`). Never `SUM(ABS(netamount))`.
- Dates Asia/Bangkok at runtime; this routine reports TODAY (EOD), guarded.
- Completeness gates the send; a zero/partial day is a STOP, not a send.
- Connectors (NetSuite + Lark) must be attached to the routine itself.
