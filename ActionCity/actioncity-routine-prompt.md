# ActionCity Daily Report — Routine Prompt

> **THIS FILE IS THE FULL INSTRUCTION SET.** The routine executes every step below, in order,
> unattended (no approval prompts). All files are in this single folder — reference them by bare
> filename. Use the attached NetSuite + Lark connectors. Do not improvise beyond these steps.

## Inputs / files to read first
- `actioncity-queries.md` — data layer (SuiteQL, fixed params, date logic, completeness).
- `actioncity-prediction.md` — insight bullets + rule-based flags/colours.
- `actioncity-delivery.md` — channels, recipients, subject, group message.
- `actioncity-template.html` — locked layout (DO NOT regenerate).
- `method.md`, `sender.md`, `branding.md`, `contacts.md` — shared engine + IDs.
- `fill_template.py` — HTML assembler.

## Steps

0. **Freshness preflight (no stale data).**
   - **Delete** any `data.json` and `email.html` left in the working dir from a previous run. Never reuse them.
   - The repo must NOT contain a committed `data.json`/`email.html` (only the template + sample). If one is present, ignore it.
   - Lint the template: `python3 preflight_check.py lint actioncity-template.html`. It must pass (the template holds only `{{tokens}}`, no baked-in numbers). If it fails → fail loud, do not run.
1. **Mode.** Read `MODE` env (default `scheduled`). Read optional `REPORT_DATE` override.
2. **Dates (Asia/Bangkok).** This is a **NEXT-MORNING** routine that reports the day that just
   **finished and fully settled**: `report_date = now(Asia/Bangkok).date() − 1 day` (yesterday),
   or `REPORT_DATE` override. Reporting *yesterday* (not today) is deliberate — online/marketplace
   orders settle overnight, so the numbers are final and there is **no provisional data and no
   correction email**. Also compute `report_date_iso` = report_date as `YYYY-MM-DD` (the idempotency
   key). Derive `iso_week`, `w_minus1..w_minus4`, `wtd_start`, `wtd_days`, week windows, display
   tokens. NEVER use bare server/UTC time.
3. **Idempotency (date-keyed, two guards — EITHER one STOPS the run; one report_date → at most one email).**
   - **Sent-flag (primary):** if `sent/actioncity-daily-{report_date_iso}.sent` exists → already sent, log and STOP. (Does not depend on mail search working.)
   - **Sent-mail search (secondary):** search sent mail for the **EXACT full subject that will be sent**, i.e. `[ActionCity] Daily Sales & Stock — {report_date_display} ({report_weekday})` — the whole string, weekday suffix included (the previous key omitted the weekday, so the match failed and it re-sent). If found → STOP.
   - Key on `report_date_iso` (YYYY-MM-DD), never the display string. **Never send a second / "correction" email for a report_date already sent.**
4. **Queries.** Run sections A–J from `actioncity-queries.md`. Net sales = `-SUM(tl.netamount)`
   (NOT ABS). Apply universal filters + `netamount<>0`. Retry a failed query once (wait 20–90s).
5. **Completeness (HARD-STOP on fail).** Run all checks in the queries file:
   report_date has rows; ≥6 weeks present; staffed stores present; net ≤ invoices (sign sanity);
   report_date == (today-BKK − 1 day). On any hard fail → go to step 9 (fail loud), do NOT send.
6. **Prediction.** Compute `insight_rows[]`, `group_flag_line`, and all rule-based flags/colours
   per `actioncity-prediction.md`. Describe-don't-diagnose; only cite figures in the data.
7. **Build `data.json`** — `{scalars, repeats, sections}` keyed to every template token, ALL from
   this run's query results. **Do NOT emit the HTML in model output** (32K-token crash). **Do NOT
   copy numbers from the sample, a prior run, or this prompt** — every value must trace to a step-4 query.
   Write data.json to disk. Then **freshness self-check (hard gate):**
   - `python3 preflight_check.py fresh data.json <report_date>` must pass (report_date_display = today; day_net non-zero; week_rows present).
   - **Control-total recheck:** re-run the today-total query once; assert its net == `scalars.day_net`. If they differ, the data.json is stale/mismatched → STOP, fail loud.
8. **Assemble + send.**
   - `python3 fill_template.py actioncity-template.html data.json > email.html`
   - If stderr lists unresolved `{{tokens}}` → fix data.json and re-run; never send unresolved money/date tokens.
   - Per `method.md` order: email (always) → group (gated by mode). `manual-test`: email to owner only, skip group.
   - Email body = contents of `email.html` via `lark_send_email`. Group via `lark_send_message` with the short card from delivery.md.
   - **On a successful email send, immediately write the idempotency marker `sent/actioncity-daily-{report_date_iso}.sent`** (contents: ISO timestamp + the exact subject sent). This is what prevents any re-run from producing a duplicate / correction email.
9. **Fail loud.** On hard failure (query/completeness/send): do NOT auto-retry the run; post to the
   `actioncity_ops_group` (or DM owner vichit@sfb.co.th) which step failed and why. Silent failure is the worst outcome.
10. **Console summary.** Print: mode, report_date, weeks loaded, completeness pass/fail, channels fired, email key, any flags.

## Guardrails (do not violate)
- Model never outputs the full HTML — only small `data.json` + short status.
- Net sales = invoices − returns (`-SUM(netamount)`); wash lines excluded (`netamount<>0`). Never `SUM(ABS(netamount))`.
- Dates Asia/Bangkok at runtime; this routine reports **YESTERDAY** (next-morning, fully settled), guarded.
- Completeness gates the send; a zero/partial day is a STOP, not a send.
- **Exactly ONE email per report_date.** A re-run for an already-sent date MUST stop at the idempotency guard (sent-flag). Never send a "correction" email — the settled prior-day report is final on first send.
- **ONE schedule only.** This routine must have a single trigger. The `data-now-*` / `email-now-*` intraday snapshots are MANUAL-only and must never be scheduled to email — a second auto-send is the other cause of two emails/day.
- Connectors (NetSuite + Lark) must be attached to the routine itself.
