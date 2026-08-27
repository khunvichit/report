# Khiang — Queries (data layer)

Data source for every `{{token}}` in `khiang-template.html`. Deterministic only — no commentary
or forecasting here (that lives in `khiang-prediction.md`).

## Tool & rules
- Tool: `mcp__9ffe807f-86e2-4035-bda1-ad1a624d35ef__ns_runCustomSuiteQL`, param name `query`.
- Retry a failed query ONCE (wait 20–90s). Never restart the routine.
- Revenue stored negative → net = `-SUM(netamount)` or `SUM(ABS(netamount))`.
- `mainline='T'` = header/totals; `'F'` = item lines.
- No `ORDER BY` on `GROUP BY` queries (400 error) — sort client-side in the routine.
- **VAT rule (verified 2026-07-30):** `mainline='T'` header totals are **INC-VAT** — exactly
  item net + 7% tax lines. The routine MUST divide every revenue figure that comes from a
  mainline-T query by **1.07** (after aggregation) before display. The rendered email shows
  **ex-VAT** figures and says so in the footer.
- Item-line (`mainline='F'`) netamounts are already ex-VAT AND net of discounts — POS_DISCOUNT
  lines carry the promo `rate` only with `netamount = 0`; the discount value is embedded in the
  item lines' prices. Never "deduct discounts" a second time.

## Fixed params (pinned — do not let these wander)
| Param | Value |
|-------|-------|
| Subsidiary | **12** (SFB) — filter on `tl.subsidiary` |
| Location (Khiang) | **27** — filter on `tl.location` |
| Airport Staff entity | **51407** |
| Walk-In entity | **48709** (everything not 51407 = Walk-In) |
| Rice menu allow-list | **ONE list, use ALL of it everywhere "rice" is filtered (incl. top10_rice + group digest):** `K008, K013, K016, K017, K037, K038, K039, K040, K041, K042, K043, K044, K045, K046, K047, K064, K065, K066, K067, K068, K069, K070, K071, K072, K073, K074, K075, K076, K077` (K064–K077 = soup bundles, live 2026-08-16 — these are now the MAIN sellers) |
| Noodle mains | `K014, K015, K062` + bundles `K078, K079` |
| New snacks (Aug-16 menu) | `K057, K060, K061` |
| POS discount item | `POS_DISCOUNT` |
| Staff-10% promo rate | `-9.81` (OLD-price rice) ; egg add-on `-1.68` — **new bundle prices produce NEW rate values; until re-pinned, classify staff-discount as: any negative POS_DISCOUNT rate NOT in the set family** |
| ฿50 drink-set promo rate | `-16.20` (drink) ; egg add-on `-5.30` ; multi-set `-32.39/-48.59/...` — **re-verify against bundle pricing after 2026-08-16** |
| Target | **฿40,000 / day ex-VAT** (confirmed 2026-07-30 — VAT excluded, discounts already net) |

## Date tokens (computed at runtime — NEVER queried, NEVER hardcoded)
Compute in **Asia/Bangkok**, then format. Honour a manual `REPORT_DATE` override for back-fills.
```
REPORT_DATE        = now(Asia/Bangkok).date() − 1
PREV_DATE          = REPORT_DATE − 1
5D_START           = REPORT_DATE − 5         # 5-day window: 5D_START .. PREV_DATE inclusive
7D_START           = REPORT_DATE − 6         # 7-day window: 7D_START .. REPORT_DATE inclusive (heatmap)
14D_START          = REPORT_DATE − 13        # 14-day window: feeds Query J (prior week = WoW baseline)
D30_START          = REPORT_DATE − 29        # 30-day window: D30_START .. REPORT_DATE inclusive
W35_START          = REPORT_DATE − 34        # 35-day window: Query H (5 full weeks for the weekly table)
PW_START           = REPORT_DATE − 28        # 28-day benchmark window for Price Watch (ends PREV_DATE)
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
first 3, and format using the MENU NAME (`displayname`), one item per line, e.g.:
```
top3 = "ข้าวกะเพราหมูสับ ×12<br>ข้าวผัดกุ้ง ×9<br>ข้าวกะเพราไก่ ×7"   # name ×qty, top 3, "<br>"-separated
```
Name rules: use `displayname`; strip any leading itemid/code prefix if present (e.g. "K037 - ข้าว…" →
"ข้าว…"); truncate to ~22 chars with "…" if longer; fallback to `itemid` if displayname is empty.
If an hour has < 3 items, list what exists. If an hour has 0 item rows (e.g. a totals-only hour) →
`top3 = "—"`.

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

## Query J — 14-Day Per-Day Revenue + Bills (heatmap table + WoW baseline)
> One row per day for the trailing 14 days (incl. REPORT_DATE). Only the last 7 days are DISPLAYED
> as heatmap rows; days 8–14 back exist solely as the week-on-week comparison baseline.
```sql
SELECT t.trandate,
  SUM(CASE WHEN t.type='CustInvc' THEN ABS(tl.netamount) ELSE 0 END) -
  SUM(CASE WHEN t.type='CustCred' THEN ABS(tl.netamount) ELSE 0 END) AS net_sales,
  COUNT(DISTINCT CASE WHEN t.type='CustInvc' THEN t.id END) AS bills
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction AND tl.mainline = 'T'
WHERE t.trandate BETWEEN TO_DATE('{14D_START}','YYYY-MM-DD') AND TO_DATE('{REPORT_DATE}','YYYY-MM-DD')
  AND t.type IN ('CustInvc','CustCred')
  AND tl.subsidiary = 12
  AND EXISTS (SELECT 1 FROM transactionline tl2 WHERE tl2.transaction = t.id AND tl2.location = 27 AND tl2.mainline = 'F')
GROUP BY t.trandate
```
Sort by `trandate` ascending client-side. Per row derive `avg_ticket = round(net_sales / bills)`
(if `bills = 0` → avg_ticket = 0). Display rows = the 7 days `7D_START..REPORT_DATE`; this feeds
the `heatmap_rows` repeat (see derivation below).

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

### WoW column (week-on-week net sales, same weekday last week)
For each of the 7 displayed days, the baseline is `trandate − 7` from the same Query J result set:
```
prev = net_sales of (r.trandate − 7 days)        # row from the first half of the 14-day window
if prev missing or prev == 0:
    wow_pct = "—"; wow_color = '#888'; wow_weight = 400
else:
    pct        = round((r.net_sales − prev) / prev × 100, 1)
    wow_pct    = signed string, e.g. "+12.4%" / "-8.0%"    # prefix '+' if ≥ 0
    wow_color  = '#27AE60' if pct >= 0 else '#E74C3C'      # green up / red down
    wow_weight = 700 if abs(pct) >= 10 else 400            # bold the big swings
```
> WoW compares revenue only (not bills/ticket) and is NOT shaded — it sits outside the
> per-column min→max shading scheme.
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

## Query G2 — Promotion bills PER DAY, last 35 days (promo weekly trend table)
> Same detection as Query G but per trandate over the 5-week window.
```sql
SELECT t.trandate, ROUND(tl.rate,2) AS discount_rate, COUNT(DISTINCT t.id) AS bills
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction
JOIN item i ON tl.item = i.id
WHERE t.trandate BETWEEN TO_DATE('{W35_START}','YYYY-MM-DD') AND TO_DATE('{REPORT_DATE}','YYYY-MM-DD')
  AND t.type = 'CustInvc'
  AND tl.mainline = 'F'
  AND tl.location = 27
  AND tl.subsidiary = 12
  AND i.itemid = 'POS_DISCOUNT'
  AND tl.rate < 0
GROUP BY t.trandate, ROUND(tl.rate,2)
```
Parse per day: `staff10(day)` = bills at rate `-9.81`; `set50(day)` = bills at rate `-16.20`
(main rates only — egg add-on rates `-1.68`/`-5.30` are NOT counted, they'd double-count bills).
Missing day/rate → 0.

### Promotion weekly trend derivation (`staff10_cells` / `set50_cells` — 5 items each)
Aggregate Query G2 into the SAME 5 week buckets as the customer weekly table (week w covers the
7 days ending `REPORT_DATE − (w−1)×7`; the `week_headers` repeat is shared — rendered above both
tables). Per week, per promo: `val` = sum of that promo's bills (thousands-separated), then the
same cell tokens as the customer table: WoW `pct` ("▲+5.2%" / "▼-3.1%"; blank for the oldest
week or prev = 0), `color` (`#27AE60` up / `#E74C3C` down / `#888` blank), `weight` 700 and
`bg` `#EEECFF` for the current week else 400/`#FFFFFF`. A week with no promo bills renders
val "0" (and pct blank if prev = 0).

---

## Query H — Last-35-Day Net Sales + Bills PER DAY × SEGMENT (strip, sales chart, weekly table)
> Returns one row per trading day per segment (Walk-In / Airport Staff) over 35 days = 5 full
> weeks. Feeds the 30d strip totals + daily sales bar chart (most recent 30 days, segments
> summed) AND the weekly customer table (all 35 days, segments kept apart). Single window;
> narrow if rate-limited. Inclusive of REPORT_DATE.
```sql
SELECT t.trandate,
  CASE WHEN t.entity = 51407 THEN 'Staff' ELSE 'Walk-In' END AS segment,
  SUM(CASE WHEN t.type='CustInvc' THEN ABS(tl.netamount) ELSE 0 END) -
  SUM(CASE WHEN t.type='CustCred' THEN ABS(tl.netamount) ELSE 0 END) AS net_sales,
  COUNT(DISTINCT CASE WHEN t.type='CustInvc' THEN t.id END) AS bills
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction AND tl.mainline = 'T'
WHERE t.trandate BETWEEN TO_DATE('{W35_START}','YYYY-MM-DD') AND TO_DATE('{REPORT_DATE}','YYYY-MM-DD')
  AND t.type IN ('CustInvc','CustCred')
  AND tl.subsidiary = 12
  AND EXISTS (SELECT 1 FROM transactionline tl2 WHERE tl2.transaction = t.id AND tl2.location = 27 AND tl2.mainline = 'F')
GROUP BY t.trandate, CASE WHEN t.entity = 51407 THEN 'Staff' ELSE 'Walk-In' END
```
Sort rows by `trandate` ascending client-side (no ORDER BY on GROUP BY). Collapse per day:
`net_sales(day) = sum over segments`; `walk_bills(day)` / `staff_bills(day)` = segment bills
(missing segment → 0); `bills(day) = walk_bills + staff_bills`.
Strip + sales chart use ONLY the most recent 30 days (`D30_START..REPORT_DATE`):
`days = count(distinct trandate in 30d)`; `net_30d = sum(net_sales over 30d)`;
`avg_30d = round(net_30d / days)`.
Build the chart `chart_days` list from those 30 per-day totals (see "Chart derivation" below);
the weekly table uses the full 35 days (see "Weekly table derivation").

### Chart derivation (30-day daily bar chart with MTD-average line)
For the bar chart `chart_days` repeat block, from the sorted Query H rows:
```
chart_max     = max(net_sales over the 30 rows)           # tallest bar = 100% height
bar_px_max    = 90                                         # max bar height in px (matches template)
mtd_avg       = avg_mtd (from Query I) — the horizontal reference line
mtd_line_px   = round(min(mtd_avg, chart_max) / chart_max * bar_px_max)   # line offset from baseline
for each day d:
    bar_px    = max(2, round(d.net_sales / chart_max * bar_px_max))   # ≥2px so zero-ish days show
    bar_color = '#27AE60' if d.net_sales >= 40000 else '#E74C3C'      # green ≥target / red below (ex-VAT)
    day_label = d.trandate day-of-month as 2 chars (e.g. '14','15'… )
    is_report_day = (d.trandate == REPORT_DATE)            # bold/marker the latest day
```
> The MTD-average line is drawn as a thin absolutely-positioned rule at `mtd_line_px` from the
> baseline, spanning the plot width, labelled `MTD avg ฿{avg_mtd}`. Bars shorter than the line read
> as below-month-average days at a glance; colour still encodes vs-target.

### Customer-trend WEEKLY table derivation (TRANSPOSED: columns = 5 weeks, rows = segments)
From Query H's per-day SEGMENT data (full 35 days), aggregate into 5 trailing weeks aligned to
REPORT_DATE: week w (w = 5 oldest .. 1 newest) covers the 7 days ending `REPORT_DATE − (w−1)×7`.
The template has FOUR repeats, each a list of 5 items ordered oldest→newest week:
`week_headers` (header cells) and `walk_cells` / `staff_cells` / `total_cells` (one data cell
per week for each row).
```
for each week w (oldest first):
    walk / staff = sum of segment bills over the week's 7 days; total = walk + staff
    label        = "D–D Mon (Thai)", e.g. "5–11 มิ.ย." (cross-month: "29 พ.ค.–4 มิ.ย.")
    is_current   = (w == 1, the week ending REPORT_DATE)
week_headers item: label;  head_color = '#5551FE' if is_current else '#888';
                   head_bg = '#EEECFF' if is_current else '#F8F9FA'
per cell (each of walk/staff/total for that week):
    val    = the count, thousands-separated
    weight = 700 if is_current else 400              # (total row is always 700 in the template)
    bg     = '#EEECFF' if is_current else '#FFFFFF'
    # WoW vs the PREVIOUS week's same figure:
    prev = previous week's value; oldest week or prev == 0 → pct = ""; color = '#888'
    else: p = round((cur − prev)/prev × 100, 1);
          pct   = arrow + signed %, e.g. "▲+5.2%" / "▼-3.1%"
          color = '#27AE60' if p >= 0 else '#E74C3C'
avg_bills_30d = round(sum(total bills over the most recent 30 days) / days)   # caption scalar
```
Tokens: `week_headers` → `label`/`head_color`/`head_bg`; each `*_cells` item →
`val`/`pct`/`color`/`weight`/`bg`. All four lists MUST be length 5, same week order.
> RETIRED: `cust_weeks`, `cust_points`/`cust_days`, `cust7_*`, `cust_line_px`. `chart_labels`
> renders only under the 30-day sales chart.

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

## Query K1 — Price-Watch benchmark: 28-day segment tickets
```sql
SELECT CASE WHEN t.entity = 51407 THEN 'Staff' ELSE 'Walk-In' END AS segment,
  SUM(CASE WHEN t.type='CustInvc' THEN ABS(tl.netamount) ELSE 0 END) -
  SUM(CASE WHEN t.type='CustCred' THEN ABS(tl.netamount) ELSE 0 END) AS net_sales,
  COUNT(DISTINCT CASE WHEN t.type='CustInvc' THEN t.id END) AS bills
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction AND tl.mainline = 'T'
WHERE t.trandate BETWEEN TO_DATE('{PW_START}','YYYY-MM-DD') AND TO_DATE('{PREV_DATE}','YYYY-MM-DD')
  AND t.type IN ('CustInvc','CustCred')
  AND tl.subsidiary = 12
  AND EXISTS (SELECT 1 FROM transactionline tl2 WHERE tl2.transaction = t.id AND tl2.location = 27 AND tl2.mainline = 'F')
GROUP BY CASE WHEN t.entity = 51407 THEN 'Staff' ELSE 'Walk-In' END
```
Derive: `pw_walk_bench = round(walk net/bills)`; `pw_staff_bench = round(staff net/bills)`.

## Query K2 — Price-Watch benchmark: 28-day night window (22:00–06:00)
```sql
SELECT COUNT(DISTINCT t.trandate) AS days, SUM(ABS(tl.netamount)) AS night_rev
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction AND tl.mainline = 'T'
WHERE t.trandate BETWEEN TO_DATE('{PW_START}','YYYY-MM-DD') AND TO_DATE('{PREV_DATE}','YYYY-MM-DD')
  AND t.type = 'CustInvc'
  AND tl.subsidiary = 12
  AND TO_CHAR(t.createddate,'HH24') IN ('22','23','00','01','02','03','04','05')
  AND EXISTS (SELECT 1 FROM transactionline tl2 WHERE tl2.transaction = t.id AND tl2.location = 27 AND tl2.mainline = 'F')
```
Derive: `pw_night_bench = round(night_rev / days)`.

## Query K3 — Price-Watch benchmark: 28-day mains sold at 12:00
```sql
SELECT COUNT(DISTINCT t.trandate) AS days, SUM(ABS(tl.quantity)) AS noon_qty
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction
JOIN item i ON tl.item = i.id
WHERE t.trandate BETWEEN TO_DATE('{PW_START}','YYYY-MM-DD') AND TO_DATE('{PREV_DATE}','YYYY-MM-DD')
  AND t.type = 'CustInvc' AND tl.mainline = 'F' AND tl.location = 27 AND tl.subsidiary = 12
  AND tl.netamount < 0
  AND TO_CHAR(t.createddate,'HH24') = '12'
  AND i.itemid IN ('K008','K013','K014','K015','K016','K017','K018','K019','K037','K038','K039','K040','K041','K042','K043','K044','K045','K046','K047','K062','K064','K065','K066','K067','K068','K069','K070','K071','K072','K073','K074','K075','K076','K077','K078','K079')
```
Derive: `pw_noon_bench = round(noon_qty / days)`. Same mains list applies to the yesterday value
from Query E2 (E2 uses LIKE 'K%' so bundles are already included — filter to this list client-side).
> NOTE 2026-08-16: soup-bundle SKUs K064–K079 went live (price increase packaged as
> "dish + clear soup"). Old codes still sell in parallel (mostly staff). FC% static table does not
> yet cover bundles — treat FC as TBC until bundle costs (dish + ~฿4 soup portion) are added.

### Price-Watch derivation (yesterday values — NO new queries, reuse A / D / E2)
```
pw_walk_ticket  = round(walk_in_revenue / walk_in_bills)          # from Query A
pw_staff_ticket = round(staff_revenue / staff_bills)              # from Query A
pw_night_rev    = sum of Query D revenue for hours 22,23,00–05    # thousands-separated
pw_noon_plates  = sum of Query E2 qty at hour '12' for the mains allow-list (same list as K3)
for each pair (value, bench) in [walk, staff, night]:
    pct   = (value − bench)/bench × 100
    arrow = "▲ +x.x%" if pct >= 0 else "▼ -x.x%"                  → pw_*_arrow
    color = '#27AE60' if pct >= 0 else '#E74C3C'                  → pw_*_color
pw_noon_color = '#E74C3C' if pw_noon_plates >= 35 else '#2C3E50'  # 35 = add-8th-staff trigger
```
Tokens (11 scalars): `pw_walk_ticket/bench/arrow/color`, `pw_staff_ticket/bench/arrow/color`,
`pw_night_rev/bench/arrow/color`, `pw_noon_plates/bench/color`.

## Query L1 — Khiang LIBERTY SQUARE daily header (loc 452 — mainline-T = INC-VAT, ÷1.07)
```sql
SELECT COUNT(DISTINCT t.id) AS lib_bills, SUM(ABS(tl.netamount)) AS lib_gross_inc
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction
WHERE t.trandate = TO_DATE('{REPORT_DATE}','YYYY-MM-DD')
  AND t.type = 'CustInvc' AND tl.mainline = 'T' AND tl.location = 452
  AND NVL(t.memo,'x') != 'VOID'
```
Derive: `lib_net_sales = round(lib_gross_inc / 1.07)` · `lib_avg_ticket = round(lib_net_sales / lib_bills)`.

## Query L2 — Liberty Top 5 items yesterday (item lines = ex-VAT; exclude ฿0 add-on markers)
```sql
SELECT i.itemid, i.displayname, SUM(ABS(tl.quantity)) AS qty
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction
JOIN item i ON tl.item = i.id
WHERE t.trandate = TO_DATE('{REPORT_DATE}','YYYY-MM-DD')
  AND t.type = 'CustInvc' AND tl.mainline = 'F' AND tl.location = 452
  AND tl.netamount < 0
  AND i.itemid LIKE 'K%' AND i.itemid NOT LIKE 'K-AO%'
  AND i.itemid NOT IN ('K027','K135','K136','K137','K138','K056')  -- exclude water/coke/glass
GROUP BY i.itemid, i.displayname ORDER BY qty DESC
```
Take top 5 → `lib_top5` repeat ({rank},{itemid},{name},{qty},{row_bg} alternating #FFFFFF/#FAFAFA).
Truncate name ~28 chars.

## Query L3 — Liberty 7-day average (for lib_signed_pct)
```sql
SELECT COUNT(DISTINCT t.trandate) AS days, SUM(ABS(tl.netamount)) AS gross_inc
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction
WHERE t.trandate BETWEEN TO_DATE('{REPORT_DATE}','YYYY-MM-DD') - 7 AND TO_DATE('{REPORT_DATE}','YYYY-MM-DD') - 1
  AND t.type = 'CustInvc' AND tl.mainline = 'T' AND tl.location = 452
  AND NVL(t.memo,'x') != 'VOID'
```
Derive: `lib_avg_7d = round(gross_inc / 1.07 / days)` (use ACTUAL trading days — store opened
2026-08-20). `lib_signed_pct = round((lib_net_sales − lib_avg_7d)/lib_avg_7d × 100, 1)` prefixed
'+' if ≥0. `lib_pct_color = '#27AE60'` if ≥0 else `'#E74C3C'`.
> Liberty has NO daily target yet (new store, ramping) — compare vs its own 7-day average only.
> If L1 returns 0 bills → lib_net_sales "0", lib_top5 = one row "— ไม่มีข้อมูล", DO NOT hard-stop
> (Liberty missing must never block the airport report).

## KPI derivations (in the routine, after queries)
```
net_sales        = walk_in_revenue + staff_revenue − credit_notes
total_bills      = walk_in_bills + staff_bills
avg_ticket       = round(net_sales / total_bills)
signed_pct       = round((net_sales − 40000) / 40000 × 100, 1)   # prefix '+' if ≥ 0 (net_sales already ÷1.07)
walk_in_pct      = round(walk_in_bills / total_bills × 100, 1)
staff_pct        = round(staff_bills  / total_bills × 100, 1)
target_icon      = 🔥 if net≥50000 | ✅ if 40000–50000 | ⚠️ if <40000   # ex-VAT thresholds
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
