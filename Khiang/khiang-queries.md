# Khiang — Queries (data layer)

Data source for every `{{token}}` in `khiang-template.html`. Deterministic only — no commentary
or forecasting here (that lives in `khiang-prediction.md`).

## Tool & rules
- Tool: `mcp__9ffe807f-86e2-4035-bda1-ad1a624d35ef__ns_runCustomSuiteQL`, param name `query`.
- Retry a failed query ONCE (wait 20–90s). Never restart the routine.
- Revenue stored negative → net = `-SUM(netamount)` or `SUM(ABS(netamount))`.
- `mainline='T'` = header/totals; `'F'` = item lines.
- No `ORDER BY` on `GROUP BY` queries (400 error) — sort client-side in the routine.
- Amounts are ex-VAT. Display ex-VAT (the rendered email shows ex-VAT figures).

## Fixed params (pinned — do not let these wander)
| Param | Value |
|-------|-------|
| Subsidiary | **12** (SFB) — filter on `tl.subsidiary` |
| Location (Khiang) | **27** — filter on `tl.location` |
| Airport Staff entity | **51407** |
| Walk-In entity | **48709** (everything not 51407 = Walk-In) |
| Rice menu allow-list | `K008, K013, K016, K017, K037, K038, K039, K040, K041, K042, K043, K044, K045, K046, K047` |
| POS discount item | `POS_DISCOUNT` |
| Staff-10% promo rate | `-9.81` (rice) ; egg add-on `-1.68` |
| ฿50 drink-set promo rate | `-16.20` (drink) ; egg add-on `-5.30` |
| Target | ฿40,000 / day |

## Date tokens (computed at runtime — NEVER queried, NEVER hardcoded)
Compute in **Asia/Bangkok**, then format. Honour a manual `REPORT_DATE` override for back-fills.
```
REPORT_DATE        = now(Asia/Bangkok).date() − 1
PREV_DATE          = REPORT_DATE − 1
5D_START           = REPORT_DATE − 5         # 5-day window: 5D_START .. PREV_DATE inclusive
7D_START           = REPORT_DATE − 6         # 7-day window: 7D_START .. REPORT_DATE inclusive (heatmap)
D30_START          = REPORT_DATE − 29        # 30-day window: D30_START .. REPORT_DATE inclusive
MTD_START          = first day of REPORT_DATE's month (e.g. 2026-05-01)
mtd_days           = REPORT_DATE.day          # number of days elapsed in month incl. REPORT_DATE
mtd_month          = "May 2026"               # Mon YYYY of REPORT_DATE
d30_start          = "14 เม.ย."               # DD Mon (Thai) of D30_START, for the strip caption
report_date_display= "13 May 2026"           # DD Mon YYYY
report_date_short  = "13 พ.ค."               # for hourly + CCTV headers
prev_date_short    = "12 พ.ค."
report_day_en      = "Wednesday"
report_year        = "2026"
generated_date     = now(Asia/Bangkok).date()  # DD Mon YYYY
```
> Off-by-one guard: if REPORT_DATE ≠ (yesterday in Asia/Bangkok), STOP. This is the bug that
> server-UTC date logic caused in v3.1 — never use UTC.

---

## Query A — Segment Revenue & Bills (KPI cards, net sales)
```sql
SELECT
  t.type,
  CASE WHEN t.entity = 51407 THEN 'Airport Staff' ELSE 'Walk-In' END AS segment,
  COUNT(DISTINCT t.id) AS bills,
  SUM(ABS(tl.netamount)) AS revenue
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction AND tl.mainline = 'T'
WHERE t.trandate = TO_DATE('{REPORT_DATE}','YYYY-MM-DD')
  AND t.type IN ('CustInvc','CustCred')
  AND tl.subsidiary = 12
  AND EXISTS (
    SELECT 1 FROM transactionline tl2
    WHERE tl2.transaction = t.id AND tl2.location = 27 AND tl2.mainline = 'F'
  )
GROUP BY t.type, CASE WHEN t.entity = 51407 THEN 'Airport Staff' ELSE 'Walk-In' END
```
Derive: `walk_in_bills/revenue`, `staff_bills/revenue`, `credit_notes` (CustCred rows).

## Query B — Top Items Sold yesterday (Top 10 All Menu)
```sql
SELECT i.itemid, i.displayname, SUM(ABS(tl.quantity)) AS qty
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction
JOIN item i ON tl.item = i.id
WHERE t.trandate = TO_DATE('{REPORT_DATE}','YYYY-MM-DD')
  AND t.type = 'CustInvc'
  AND tl.mainline = 'F'
  AND tl.location = 27
  AND tl.subsidiary = 12
  AND tl.netamount < 0
  AND i.itemid LIKE 'K%'
GROUP BY i.itemid, i.displayname
```
Sort by qty desc client-side; take top 10. Mark rice-menu items (in allow-list) with ⭐ on `name`.

## Query C — 5-Day Rolling Average (all K-items, for Δ% badges)
```sql
SELECT i.itemid, SUM(ABS(tl.quantity)) AS total_qty, COUNT(DISTINCT t.trandate) AS days
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction
JOIN item i ON tl.item = i.id
WHERE t.trandate >= TO_DATE('{5D_START}','YYYY-MM-DD')
  AND t.trandate <  TO_DATE('{REPORT_DATE}','YYYY-MM-DD')
  AND t.type = 'CustInvc'
  AND tl.mainline = 'F'
  AND tl.location = 27
  AND tl.subsidiary = 12
  AND tl.netamount < 0
  AND i.itemid LIKE 'K%'
GROUP BY i.itemid
```
Parse: `avg5d = round(total_qty / days)`. Item with no 5d history → `avg5d = "—"`, badge = New.

## Query D — Hourly Breakdown yesterday (revenue display + bills for anomaly)
> Uses `t.createddate` for the hour, NOT `t.trandate`.
```sql
SELECT TO_CHAR(t.createddate,'HH24') AS hour,
  COUNT(DISTINCT t.id) AS bills,
  SUM(ABS(tl.netamount)) AS revenue
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction AND tl.mainline = 'T'
WHERE t.trandate = TO_DATE('{REPORT_DATE}','YYYY-MM-DD')
  AND t.type = 'CustInvc'
  AND tl.subsidiary = 12
  AND EXISTS (SELECT 1 FROM transactionline tl2 WHERE tl2.transaction = t.id AND tl2.location = 27 AND tl2.mainline = 'F')
GROUP BY TO_CHAR(t.createddate,'HH24')
```

## Query E — Hourly Breakdown day-before
Same as D with `t.trandate = TO_DATE('{PREV_DATE}','YYYY-MM-DD')`.

## Query E2 — Top 3 Items per Hour (yesterday)
> Item qty per hour for REPORT_DATE. Hour from `t.createddate` (matches Queries D/E).
```sql
SELECT TO_CHAR(t.createddate,'HH24') AS hour,
  i.itemid, i.displayname,
  SUM(ABS(tl.quantity)) AS qty
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction
JOIN item i ON tl.item = i.id
WHERE t.trandate = TO_DATE('{REPORT_DATE}','YYYY-MM-DD')
  AND t.type = 'CustInvc'
  AND tl.mainline = 'F'
  AND tl.location = 27
  AND tl.subsidiary = 12
  AND tl.netamount < 0
  AND i.itemid LIKE 'K%'
GROUP BY TO_CHAR(t.createddate,'HH24'), i.itemid, i.displayname
```
Build `top3` per hour in the routine: group rows by `hour`, sort by `qty` desc client-side, take the
first 3, and format as a compact string for the hourly row's Top-3 column, e.g.:
```
top3 = "K037 ×12 · K023 ×9 · K038 ×7"   # itemid ×qty, top 3, separated by " · "
```
If an hour has < 3 items, list what exists. If an hour has 0 item rows (e.g. a totals-only hour) →
`top3 = "—"`. Keep it to itemid+qty (not Thai names) so the column stays narrow and email-safe.

## Query F — 5-Day Net Sales (avg_5d KPI + optional trend)
```sql
SELECT t.trandate,
  SUM(CASE WHEN t.type='CustInvc' THEN ABS(tl.netamount) ELSE 0 END) -
  SUM(CASE WHEN t.type='CustCred' THEN ABS(tl.netamount) ELSE 0 END) AS net_sales,
  COUNT(DISTINCT CASE WHEN t.type='CustInvc' THEN t.id END) AS bills
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction AND tl.mainline = 'T'
WHERE t.trandate BETWEEN TO_DATE('{5D_START}','YYYY-MM-DD') AND TO_DATE('{PREV_DATE}','YYYY-MM-DD')
  AND t.type IN ('CustInvc','CustCred')
  AND tl.subsidiary = 12
  AND EXISTS (SELECT 1 FROM transactionline tl2 WHERE tl2.transaction = t.id AND tl2.location = 27 AND tl2.mainline = 'F')
GROUP BY t.trandate
```
Derive: `avg_5d = round(mean(net_sales))`, `avg_bills`, `avg_ticket_bench`.

## Query J — 7-Day Per-Day Revenue + Bills (heatmap table)
> One row per day for the trailing 7 days (incl. REPORT_DATE). Avg ticket derived per row.
```sql
SELECT t.trandate,
  SUM(CASE WHEN t.type='CustInvc' THEN ABS(tl.netamount) ELSE 0 END) -
  SUM(CASE WHEN t.type='CustCred' THEN ABS(tl.netamount) ELSE 0 END) AS net_sales,
  COUNT(DISTINCT CASE WHEN t.type='CustInvc' THEN t.id END) AS bills
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction AND tl.mainline = 'T'
WHERE t.trandate BETWEEN TO_DATE('{7D_START}','YYYY-MM-DD') AND TO_DATE('{REPORT_DATE}','YYYY-MM-DD')
  AND t.type IN ('CustInvc','CustCred')
  AND tl.subsidiary = 12
  AND EXISTS (SELECT 1 FROM transactionline tl2 WHERE tl2.transaction = t.id AND tl2.location = 27 AND tl2.mainline = 'F')
GROUP BY t.trandate
```
Sort by `trandate` ascending client-side. Per row derive `avg_ticket = round(net_sales / bills)`
(if `bills = 0` → avg_ticket = 0). This feeds the `heatmap_rows` repeat (see derivation below).

### Heatmap derivation (7 rows × 3 metric columns, shaded within each column)
Each metric column (revenue, bills, avg_ticket) is shaded against ITS OWN 7-day min→max.
```
for metric m in [net_sales, bills, avg_ticket]:
    lo = min(m over 7 rows); hi = max(m over 7 rows)
    for each day row r:
        t = 0.5 if hi == lo else (r[m] − lo) / (hi − lo)   # 0..1 within this column
        # shade: light cream (low) → CHAW indigo tint (high), text stays readable
        r[m_bg] = lerp_hex('#FBF3EA', '#C9C7FF', t)         # bg per cell
        r[m_fg] = '#2C3E50'                                  # ink; keep dark for contrast
    # mark the column's max cell bold (the week's best day for that metric)
day_label_th = trandate as "พ 13/5" (Thai weekday abbr + D/M); bold if trandate == REPORT_DATE
```
> Shade only — no green/red target logic here (that lives in the 30-day chart). The point of the
> heatmap is relative intensity across the week, per metric. Provide `lerp_hex(a,b,t)` in the routine
> (linear interpolate each RGB channel, return `#RRGGBB`).

## Query G — Promotion Detection
```sql
SELECT ROUND(tl.rate,2) AS discount_rate, COUNT(DISTINCT t.id) AS bills
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction
JOIN item i ON tl.item = i.id
WHERE t.trandate = TO_DATE('{REPORT_DATE}','YYYY-MM-DD')
  AND t.type = 'CustInvc'
  AND tl.mainline = 'F'
  AND tl.location = 27
  AND tl.subsidiary = 12
  AND i.itemid = 'POS_DISCOUNT'
  AND tl.rate < 0
GROUP BY ROUND(tl.rate,2)
```
Parse: `staff10_bills` = bills at rate `-9.81`; `set50_bills` = bills at rate `-16.20`.

---

## Query H — Last-30-Day Net Sales PER DAY (period strip + bar chart)
> Returns one row per trading day. Feeds both the 30d strip totals AND the daily bar chart.
> Single window; narrow to the month boundary if rate-limited. Inclusive of REPORT_DATE.
```sql
SELECT t.trandate,
  SUM(CASE WHEN t.type='CustInvc' THEN ABS(tl.netamount) ELSE 0 END) -
  SUM(CASE WHEN t.type='CustCred' THEN ABS(tl.netamount) ELSE 0 END) AS net_sales
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction AND tl.mainline = 'T'
WHERE t.trandate BETWEEN TO_DATE('{D30_START}','YYYY-MM-DD') AND TO_DATE('{REPORT_DATE}','YYYY-MM-DD')
  AND t.type IN ('CustInvc','CustCred')
  AND tl.subsidiary = 12
  AND EXISTS (SELECT 1 FROM transactionline tl2 WHERE tl2.transaction = t.id AND tl2.location = 27 AND tl2.mainline = 'F')
GROUP BY t.trandate
```
Sort rows by `trandate` ascending client-side (no ORDER BY on GROUP BY).
Derive for the strip: `days = count(rows)`; `net_30d = sum(net_sales)`; `avg_30d = round(net_30d / days)`.
Build the chart `chart_days` list from these rows (see "Chart derivation" below).

### Chart derivation (30-day daily bar chart with MTD-average line)
For the bar chart `chart_days` repeat block, from the sorted Query H rows:
```
chart_max     = max(net_sales over the 30 rows)           # tallest bar = 100% height
bar_px_max    = 90                                         # max bar height in px (matches template)
mtd_avg       = avg_mtd (from Query I) — the horizontal reference line
mtd_line_px   = round(min(mtd_avg, chart_max) / chart_max * bar_px_max)   # line offset from baseline
for each day d:
    bar_px    = max(2, round(d.net_sales / chart_max * bar_px_max))   # ≥2px so zero-ish days show
    bar_color = '#27AE60' if d.net_sales >= 40000 else '#E74C3C'      # green ≥target / red below
    day_label = d.trandate day-of-month as 2 chars (e.g. '14','15'… )
    is_report_day = (d.trandate == REPORT_DATE)            # bold/marker the latest day
```
> The MTD-average line is drawn as a thin absolutely-positioned rule at `mtd_line_px` from the
> baseline, spanning the plot width, labelled `MTD avg ฿{avg_mtd}`. Bars shorter than the line read
> as below-month-average days at a glance; colour still encodes vs-target.

## Query I — Month-to-Date Net Sales (period strip)
```sql
SELECT
  SUM(CASE WHEN t.type='CustInvc' THEN ABS(tl.netamount) ELSE 0 END) -
  SUM(CASE WHEN t.type='CustCred' THEN ABS(tl.netamount) ELSE 0 END) AS net_sales,
  COUNT(DISTINCT t.trandate) AS days
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction AND tl.mainline = 'T'
WHERE t.trandate BETWEEN TO_DATE('{MTD_START}','YYYY-MM-DD') AND TO_DATE('{REPORT_DATE}','YYYY-MM-DD')
  AND t.type IN ('CustInvc','CustCred')
  AND tl.subsidiary = 12
  AND EXISTS (SELECT 1 FROM transactionline tl2 WHERE tl2.transaction = t.id AND tl2.location = 27 AND tl2.mainline = 'F')
```
Derive: `net_mtd = net_sales`; `mtd_days = days` (actual trading days MTD);
`avg_mtd = round(net_sales / days)`; `mtd_signed_pct = round((avg_mtd − 40000)/40000 × 100, 1)`
(prefix '+' if ≥ 0). If MTD has 0 trading days (1st of month before close) → render all three as `—`.

---

## KPI derivations (in the routine, after queries)
```
net_sales        = walk_in_revenue + staff_revenue − credit_notes
total_bills      = walk_in_bills + staff_bills
avg_ticket       = round(net_sales / total_bills)
signed_pct       = round((net_sales − 40000) / 40000 × 100, 1)   # prefix '+' if ≥ 0
walk_in_pct      = round(walk_in_bills / total_bills × 100, 1)
staff_pct        = round(staff_bills  / total_bills × 100, 1)
target_icon      = 🔥 if net≥50000 | ✅ if 40000–50000 | ⚠️ if <40000
bills_arrow / ticket_arrow = ↑ if ≥ benchmark else ↓
```

## Food Cost % (static, for rice table FC% column)
K037 26.2 · K038 24.3 · K039 23.3 · K040 29.7 · K041 26.1 · K042 23.3 · K043 25.3
· K045 29.9 · K046 22.6 · K047 29.1 · K008 27.2 · K013 26.0
(Items without a listed FC% → render "—".)

## Completeness checks — HARD STOP before building/sending
1. Query A returned ≥ 1 row for REPORT_DATE (else likely no-data day → fail loud, don't send zeros).
2. `total_bills > 0` and `net_sales > 0`.
3. Query D returned ≥ 1 hour row.
4. REPORT_DATE == yesterday Asia/Bangkok (timezone guard).
5. A section query with 0 rows (e.g. no promos) → render `—` / omit its SECTION, do NOT fail.
On any hard-stop failure: do not send the report; trigger the failure path in the routine prompt.
