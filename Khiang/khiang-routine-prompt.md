# khiang-routine-prompt.md — THIS FILE IS THE FULL INSTRUCTION SET

The routine reads this and executes every step in order, unattended, no approval prompts.
File references are **bare filenames** — the routine reads from inside the `Khiang/` folder.
Use the attached NetSuite + Lark connectors. Default Mode = `scheduled` (override to `manual-test`
or `manual-live` via the run config).

> CORE RULE: **The model never outputs the full HTML.** It computes `data.json` only and lets
> `fill_template.py` assemble the email. Emitting the ~400-line template as output crashes the
> 32K token limit. Keep model output to small data + short status lines.

## 0. Read config
Read: `branding.md`, `sender.md`, `method.md`, `khiang-queries.md`, `khiang-prediction.md`,
`khiang-delivery.md`. Take `chaw_values` from `branding.md` (never hardcode).

## 1. Dates (Asia/Bangkok)
Compute REPORT_DATE = now(Asia/Bangkok).date() − 1 and all derived date tokens per `khiang-queries.md`.
Honour a manual `REPORT_DATE` override (manual-live back-fills).
**Timezone guard:** if REPORT_DATE ≠ yesterday-BKK (and no manual override) → STOP, fail loud.

## 2. Idempotency
Search sent mail for the Email-key subject (`khiang-delivery.md`) for REPORT_DATE.
If already sent today → STOP. Run exactly once per day.

## 3. Queries
Run Queries A–I (`khiang-queries.md`) with the read-only NetSuite tool, param `query`.
Retry a failed query ONCE (wait 20–90s); do not restart. Pin Sub 12 / loc 27 / entities.
Queries H (30-day per-day) and I (month-to-date) feed the period strip + bar chart;
Query J (14-day per-day) feeds the heatmap table — last 7 days displayed, prior 7 = WoW baseline;
Query E2 feeds the Top-3-items-per-hour column in the hourly comparison;
Query G2 (35-day daily promo bills) feeds the Promotion Trend by Week table;
Queries K1–K3 (28-day benchmarks) feed the Price Watch strip — yesterday's values come from A/D/E2;
Queries L1–L4 (location 452) feed the Liberty data (header COMBINED box, paired chart bars,
Last-7-days branch table, LIB branch card) — soft-fail: if Liberty data is missing/zero, render
zeros/"— ไม่มีข้อมูล" and continue (never hard-stop the airport report).

## 4. Completeness — HARD STOP
Run the 5 checks in `khiang-queries.md`. Any hard-stop failure → do NOT send; go to step 10 (fail loud).

## 5. Compute KPIs & prediction
- **VAT conversion FIRST:** every revenue figure from a mainline-T query (A, F, H, I, J, K1, K2,
  and the hourly D/E revenue) is INC-VAT — divide by 1.07 after aggregation, before any KPI math
  or display. Item-line figures (B, C, E2, G, G2) are already ex-VAT. Target = ฿40,000/day ex-VAT.
- KPI derivations per `khiang-queries.md` (net_sales, total_bills, avg_ticket, pcts, target_icon, arrows).
- Period metrics: `net_30d` / `avg_30d` (Query H) and `net_mtd` / `avg_mtd` / `mtd_days` /
  `mtd_signed_pct` (Query I). Use ACTUAL trading days for the averages, not calendar days.
- Anomalies per `khiang-prediction.md` using **bill count** vs HOURLY_BILL_BENCH × 0.50.
  Set `anomaly_count`. (CCTV section removed — anomalies now drive ONLY the email alert banner +
  hourly-table styling. The Khiang group message is a plain daily digest, NOT anomaly-gated.)
- For each hourly row, build `top3` from Query E2 (menu NAME `displayname` ×qty, top 3,
  "<br>"-separated one per line; strip code prefixes, truncate ~22 chars, fallback itemid; "—" if none).
- Build `rice_top10_lines` for the group digest from the same `top10_rice` data (see `khiang-delivery.md`).
- Price Watch: compute the 11 `pw_*` scalars per the Price-Watch derivation in `khiang-queries.md`
  (yesterday's segment tickets from Query A, night 22:00–06:00 from Query D buckets, 12:00 mains
  from Query E2; benchmarks from K1–K3). These monitor the price change: Walk-In ticket
  (downtrade detector), Staff ticket (discount check), night window (night-shift viability),
  noon plates (staffing trigger ≥35).
- Sections: `alert_banner = (anomaly_count > 0)`; `promo = (staff10_bills + set50_bills > 0)`.
- Liberty scalars per `khiang-queries.md` L1–L4: `lib_net_sales`, `lib_bills`, `lib_avg_ticket`,
  `lib_avg_7d`, `lib_signed_pct`, `lib_pct_color`, `comb_net_sales`, `apt_7d_total`, `lib_7d_total`,
  `comb_7d_total`, `comb_7d_avg` + repeats `lib_top5`, `apt_top5` (rank/itemid/name/qty/row_bg),
  `last7_headers`, `last7_apt`, `last7_lib`, `last7_comb` (Juiceland-style branch table).
  All Liberty revenue from mainline-T is INC-VAT → ÷1.07 like the airport numbers.

## 6. Build data.json (NOT html)
Write `data.json` with `scalars`, `repeats` (`top10_all`, `top10_rice`, `hourly_rows`,
`chart_days`, `chart_labels`, `week_headers`, `walk_cells`, `staff_cells`, `total_cells`,
`staff10_cells`, `set50_cells`, `heatmap_rows`, `lib_top5`, `apt_top5`, `last7_headers`,
`last7_apt`, `last7_lib`, `last7_comb`), and `sections`. Each `chart_days` item now ALSO carries
`lib_bar_px`/`lib_bar_title` (paired branch bars; 0 before 2026-08-20; chart_max spans both branches). `week_headers` renders above
BOTH weekly tables (customer + promotion) — same 5 weeks. Every scalar token in the template must
have a key —
including the period-strip tokens `net_30d`, `avg_30d`, `d30_start`, `net_mtd`, `avg_mtd`, `mtd_days`,
`mtd_month`, `mtd_signed_pct`, and the chart line offset `mtd_line_px`. Each `hourly_rows` item now
carries a `top3` token (from Query E2). The `cctv_tasks` repeat and `cctv_followup`/`task_guid`
scalars are GONE (CCTV section removed). Badge colours per template:
≥+15% green `#D4EDDA/#155724` · −10%..+15% amber `#FEF3CD/#856404` · ≤−10% red `#F8D7DA/#721C24` ·
New blue `#D1ECF1/#0C5460`. Alternate `row_bg` `#FFFFFF`/`#FAFAFA`; hourly anomaly rows `#FFEBEE`.
**30-day chart:** build `chart_days` (one item per trading day: `bar_px`, `bar_color`, `bar_title`)
and `chart_labels` (matching order: `day_label`, plus `label_color`/`label_weight` = `#5551FE`/`700`
for the REPORT_DATE day, else `#AAA`/`400`) per the Chart derivation in `khiang-queries.md`. The two
lists MUST be the same length and order so bars line up with labels.
**Customer trend by week (transposed table):** build the four 5-item lists `week_headers`
(`label`/`head_color`/`head_bg`) and `walk_cells`/`staff_cells`/`total_cells`
(`val`/`pct`/`color`/`weight`/`bg`), oldest→newest week, per the Customer-trend WEEKLY table
derivation in `khiang-queries.md` (Query H segment split over 35 days = 5 weeks ending
REPORT_DATE; current week highlighted), plus scalar `avg_bills_30d`. The `cust_weeks`/
`cust_points`/`cust7_*` tokens are retired; `chart_labels` renders only under the sales chart.
**7-day heatmap:** build `heatmap_rows` (7 items, oldest→newest) per the Heatmap derivation in
`khiang-queries.md` (Query J): each row carries `day_label_th`, `rev`/`bills`/`ticket` values, a
pre-computed `*_bg`/`*_fg`/`*_weight` per cell (shaded within each column's own 7-day min→max),
plus the WoW tokens `wow_pct`/`wow_color`/`wow_weight` (vs same weekday last week, from the first
half of the 14-day Query J window; "—" grey if no baseline).

## 7. Assemble HTML
Run: `python3 fill_template.py khiang-template.html data.json > email.html`
If stderr prints `WARNING unresolved placeholders` for money/date tokens → fix data.json, re-run.
Do NOT send with unresolved tokens.

## 8. Send
- EMAIL: always (after completeness). manual-test → owner only. **Body = the LITERAL contents of
  `email.html` — READ the file and paste the whole HTML into the tool's `body` argument. The send
  tool cannot read files; never pass a path or placeholder (see `sender.md`). Pre-send check: body
  starts with `<!DOCTYPE`/`<html` and >20k chars, else fix before sending. Send exactly once — no
  CORRECTION emails.** (Tool arguments don't count toward the 32K output limit; the no-HTML-output
  rule applies to assistant text only.)
- GROUP: fires DAILY (not anomaly-gated), scheduled mode only. Primary chat_id (Khiang), fallback
  (Quality) on failure. Daily sales digest: net sales, avg ticket, MTD avg, 30d avg, **Top 10 rice
  menu — MANDATORY section, rice list INCLUDES soup bundles K064–K077** (per `khiang-delivery.md`
  hard rule: verify the 🍚 block exists with ≥1 line before sending; never send the digest without it).

## 9. Failure path (fail loud)
On any hard stop or channel hard-failure: DM owner (vichit@chaw.co.th) / post failure group with which
step failed + why. No silent failure. No whole-routine auto-retry.

## 10. Console
Print the shared console summary (`sender.md` shape) with net_sales, bills, anomalies, MTD/30d avg,
and which channels fired vs skipped (task = not used).
