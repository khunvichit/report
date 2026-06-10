# Juiceland Report — Data Map (file #2 of 3)

This file tells the routine **where every `{{placeholder}}` in `juiceland-template.html` comes from**.
Pair with: `juiceland-template.html` (format) · `juiceland-report-runbook.md` (orchestration).

Tool: `mcp__9ffe807f-86e2-4035-bda1-ad1a624d35ef__ns_runCustomSuiteQL` · param name is `query`.
Read-only. Retry the same query if it fails; never restart the routine.

---

## Fixed parameters (never let these wander)

| Param | Value |
|-------|-------|
| Subsidiary | 12 (SFB) |
| Class | 3 (`Food : Juice Land`) — applies to all 3 branches |
| Locations | 33 (MW1) · 105 (SE3) · 109 (PKT) · **169 → roll up into MW1** |
| Branch order (always) | MW1, SE3, PKT |
| Timezone | Asia/Bangkok (UTC+7) — all date math |
| netamount sign | sale lines negative, discount lines positive → net = `-SUM(netamount)` |
| VAT | excluded at netamount level (figures are ex-VAT) |

---

## Date tokens (computed at runtime, NOT queried)

| Token | Derivation |
|-------|-----------|
| `{{report_date}}` | `now(Asia/Bangkok).date() − 1` (or manual `REPORT_DATE` override) |
| `{{report_date_display}}` | report_date as `D Month YYYY` |
| `{{report_day_th}}` | Thai weekday of report_date (e.g. วันศุกร์) |
| `{{window_30d_start}}` | report_date − 29 days |
| `{{generated_timestamp}}` | now(Asia/Bangkok) `YYYY-MM-DD HH:MM` |
| `{{subject_prefix}}` | 🔥 if comb vs 30d ≥ +10% · ✅ if −10%…+10% · ⚠️ if ≤ −10% |
| `{{signed_pct}}` | comb_vs_30d, signed (e.g. -3.8) |

---

## Query A — Daily totals per branch (30-day window)
Feeds: header, chart, last-7 table, 30-day KPI cards.

```sql
SELECT t.trandate, tl.location,
  COUNT(DISTINCT t.id) AS bills,
  -SUM(tl.netamount)   AS net_sales
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction
WHERE t.trandate BETWEEN TO_DATE('{WINDOW_30D_START}','YYYY-MM-DD') AND TO_DATE('{REPORT_DATE}','YYYY-MM-DD')
  AND t.type IN ('CustInvc','CustCred')
  AND tl.mainline = 'F' AND tl.location IN (33,105,109,169) AND tl.class = 3
GROUP BY t.trandate, tl.location
ORDER BY t.trandate, tl.location
```
Roll loc 169 into MW1 in code.

| Token group | From |
|-------------|------|
| `{{comb_net}}`, `{{signed_pct}}` | report_date row, summed; vs 30-day avg |
| `{{mw1_net}}` `{{se3_net}}` `{{pkt_net}}` (chart) | each day/branch |
| `{{*_bar_px}}` | `round(net / chart_max * 220)`; chart_max = max single-branch day in window |
| `{{last7_*}}` | slice last 7 dates ending report_date; yesterday cell highlighted |
| `{{*_avg_30d}}` `{{*_min_30d}}` `{{*_max_30d}}` | per branch across 30 days (avg = sum÷30) |
| `{{comb_monthly_runrate}}` | comb_avg_30d × 30, in thousands (e.g. 2,138.1K) |

## Query B — Top 20 product memos per branch (yesterday)
Feeds: Section 5. Take top 20 per branch by qty after fetch.

```sql
SELECT tl.memo, tl.location,
  SUM(ABS(tl.quantity)) AS qty, SUM(ABS(tl.netamount)) AS revenue,
  COUNT(DISTINCT t.id) AS bills
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction
WHERE t.trandate = TO_DATE('{REPORT_DATE}','YYYY-MM-DD')
  AND t.type = 'CustInvc' AND tl.mainline = 'F'
  AND tl.location IN (33,105,109,169) AND tl.class = 3
  AND tl.netamount < 0 AND tl.memo IS NOT NULL
  AND UPPER(tl.memo) NOT IN ('VAT','CREDIT DEDUCT')
GROUP BY tl.memo, tl.location
ORDER BY tl.location, qty DESC
```
`{{memo_display}}` = truncate ~34 chars + …, full in `{{memo_full}}`. PKT memos differ from BKK — don't unify.

## Query C — New-product daily history (self-selecting, 30-day rule)
Feeds: Section 4. A product is "new" if its first-ever (normalized) sale is within the trailing
30 days of report_date — see `juiceland-report-runbook.md` §1–4 for the rule, categorization, and
status logic. No manual registry: the query selects new products itself, so Section 4 can't go stale.

```sql
WITH norm AS (
  SELECT t.trandate AS trandate, tl.location AS location, tl.memo AS memo,
         UPPER(TRIM(REPLACE(REPLACE(tl.memo, CHR(10), ''), CHR(13), ''))) AS nmemo,
         tl.quantity AS quantity, tl.netamount AS netamount, t.id AS tid
  FROM transaction t
  JOIN transactionline tl ON t.id = tl.transaction
  WHERE t.type = 'CustInvc' AND tl.mainline = 'F'
    AND tl.location IN (33,105,109,169) AND tl.class = 3 AND tl.netamount < 0
    AND tl.memo IS NOT NULL
    AND UPPER(TRIM(tl.memo)) NOT IN ('VAT','CREDIT DEDUCT')
),
firstsale AS (
  SELECT nmemo, MIN(trandate) AS first_sold
  FROM norm
  GROUP BY nmemo
  HAVING MIN(trandate) >= TO_DATE('{REPORT_DATE}','YYYY-MM-DD') - 30
)
SELECT n.trandate, n.location, MIN(n.memo) AS memo, fs.first_sold,
       SUM(ABS(n.quantity)) AS qty, SUM(ABS(n.netamount)) AS revenue,
       COUNT(DISTINCT n.tid) AS bills
FROM norm n
JOIN firstsale fs ON fs.nmemo = n.nmemo
GROUP BY n.trandate, n.location, n.nmemo, fs.first_sold
ORDER BY n.nmemo, n.trandate, n.location
```
Roll loc 169 into MW1 in code. Drop excluded/noise memos per runbook §1 after fetch.

| Token | From |
|-------|------|
| `{{*_todate_units/rev}}`, `{{np_total_*}}` | per-type and overall sums |
| `{{velocity_7d}}` `{{gap_days}}` `{{status_badge}}` | per runbook status logic |
| `{{yest_units}}` | qty at report_date |

## Query D — Dormant SKUs (no sale 7+ days)
Feeds: Section 7. Client filter: `qty_30d ≥ 3`, drop malformed/`\n` memos, sort by qty_30d desc.

```sql
SELECT tl.location, tl.memo, MAX(t.trandate) AS last_sold,
  SUM(ABS(tl.quantity)) AS qty_30d, COUNT(DISTINCT t.trandate) AS days_sold_30d,
  SUM(ABS(tl.netamount)) AS rev_30d
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction
WHERE t.trandate BETWEEN TO_DATE('{WINDOW_30D_START}','YYYY-MM-DD') AND TO_DATE('{REPORT_DATE}','YYYY-MM-DD')
  AND t.type = 'CustInvc' AND tl.mainline = 'F'
  AND tl.location IN (33,105,109,169) AND tl.class = 3
  AND tl.netamount < 0 AND tl.memo IS NOT NULL
  AND UPPER(tl.memo) NOT IN ('VAT','CREDIT DEDUCT')
GROUP BY tl.location, tl.memo
HAVING MAX(t.trandate) <= TO_DATE('{REPORT_DATE}','YYYY-MM-DD') - 7
ORDER BY tl.location, qty_30d DESC
```
`{{gap_color}}`: 7–13d `#E65100`, 14d+ `#C62828`.

## Query E — Grape baseline (seasonal tracker)
Feeds: Section 6. Replacement = NEW_PRODUCTS where type=fruit (from Query C).

```sql
SELECT tl.location, tl.memo, MIN(t.trandate) AS first_sold, MAX(t.trandate) AS last_sold,
  SUM(ABS(tl.quantity)) AS total_qty, SUM(ABS(tl.netamount)) AS total_revenue
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction
WHERE t.type = 'CustInvc' AND tl.mainline = 'F'
  AND tl.location IN (33,105,109,169) AND tl.class = 3 AND tl.netamount < 0
  AND UPPER(tl.memo) LIKE '%GRAPE%'
GROUP BY tl.location, tl.memo
```
Baselines (peak window, hardcoded reference): MW1 ฿339/d · SE3 ฿251/d · PKT n/a.
`{{coverage_pct}}` = new_fruit_per_day ÷ grape_baseline × 100. Colour/badge: <70% red, 70–99% amber, ≥100% green.

---

## Completeness checks (run before building HTML)

1. Query A returned rows for all 3 branches across the window (no branch wholly missing).
2. report_date itself has rows for ≥1 branch (else likely a no-data day — flag, don't send silent zeros).
3. 30-day window has the expected day count (30).
4. If a branch has 0 rows for a section → render `—`, never fail the run.
5. If timezone/date looks off (report_date ≠ yesterday BKK), STOP and report — do not send.
