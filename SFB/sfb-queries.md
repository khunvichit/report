# SFB Daily — Data Layer (NetSuite SuiteQL + Odoo hourly)

Tool: `mcp__9ffe807f-86e2-4035-bda1-ad1a624d35ef__ns_runCustomSuiteQL` · param name `query`.
Rate-limited: wait 20–90s between retries; retry a failed query ONCE; never restart the routine.

## Fixed params (pin — these silently wander)

- **Subsidiary:** 12 (SFB) — always filter `tl.subsidiary = 12` (transactionline, NOT header).
- **Revenue:** stored negative; net sales = `-SUM(tl.netamount)`.
- **Item lines:** `tl.mainline = 'F'` and `tl.taxline = 'F'`, `tl.item IS NOT NULL`, `tl.account IS NOT NULL`.
- **Branch:** `tl.location` (Sub 12). **Business Unit:** `classification` via `tl.class`.
- **Khiang:** location id **27**, class **231** (only BU that posts true sale time to NS).
- **Tx types:** `CustInvc`, `CustCred`.
- No `ORDER BY` on `GROUP BY` queries (400 error) — sort client-side.
- Date filtering: `TO_DATE('YYYY-MM-DD','YYYY-MM-DD')`.

## Date tokens (computed at runtime, Asia/Bangkok — never hardcode, never server-UTC)

- `D1` = now(Asia/Bangkok).date() − 1  (report date; honor manual `REPORT_DATE` override for back-fills)
- `D2` = D1 − 1   ·   `D8` = D1 − 7
- `MTD_START` = D1 first-of-month   ·   `TREND_START` = D1 − 29 (30-day window)
- Display tokens derived from D1: `report_date_display` ("25 May 2026"), `weekday_en`, `weekday_th`
  (วันจันทร์…), `window_label`, `mtd_label`, `d8_display`.

---

## Q1 — Daily totals per (location × BU) for D1, D2, D8

```sql
SELECT TO_CHAR(t.trandate,'YYYY-MM-DD') AS d, l.name AS location, c.name AS bu,
       COUNT(DISTINCT CASE WHEN t.type='CustInvc' THEN t.id END) AS bills,
       SUM(-tl.netamount) AS revenue
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction
LEFT JOIN classification c ON tl.class = c.id
LEFT JOIN location l ON tl.location = l.id
WHERE t.trandate IN (TO_DATE('{D1}','YYYY-MM-DD'),TO_DATE('{D2}','YYYY-MM-DD'),TO_DATE('{D8}','YYYY-MM-DD'))
  AND tl.subsidiary = 12 AND t.type IN ('CustInvc','CustCred')
  AND tl.mainline = 'F' AND tl.taxline = 'F'
  AND tl.item IS NOT NULL AND tl.account IS NOT NULL
GROUP BY t.trandate, l.name, c.name
```
Feeds: KPI headline, branch tables (D1/D2/D8/DoD/WoW), BU + airport legends, location×BU heatmap
(one row per location×BU pair; rev/bills/ticket Δ WoW = D1 vs D8). ~60 rows.

## Q2 — 30-day trend by BU (BU stacked chart)

```sql
SELECT TO_CHAR(t.trandate,'YYYY-MM-DD') AS d, c.name AS bu,
       SUM(-tl.netamount) AS revenue,
       COUNT(DISTINCT CASE WHEN t.type='CustInvc' THEN t.id END) AS bills
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction
LEFT JOIN classification c ON tl.class = c.id
WHERE t.trandate BETWEEN TO_DATE('{TREND_START}','YYYY-MM-DD') AND TO_DATE('{D1}','YYYY-MM-DD')
  AND tl.subsidiary = 12 AND t.type IN ('CustInvc','CustCred')
  AND tl.mainline = 'F' AND tl.taxline = 'F'
  AND tl.item IS NOT NULL AND tl.account IS NOT NULL
GROUP BY TO_CHAR(t.trandate,'YYYY-MM-DD'), c.name
```
~150 rows (30 days × 5 BUs). Also source of MTD avg/high/low (filter d in MTD window).

## Q3 — 30-day trend by location (airport rollup chart + per-branch MTD flags)

```sql
SELECT TO_CHAR(t.trandate,'YYYY-MM-DD') AS d, l.name AS location,
       SUM(-tl.netamount) AS revenue,
       COUNT(DISTINCT CASE WHEN t.type='CustInvc' THEN t.id END) AS bills
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction
LEFT JOIN location l ON tl.location = l.id
WHERE t.trandate BETWEEN TO_DATE('{TREND_START}','YYYY-MM-DD') AND TO_DATE('{D1}','YYYY-MM-DD')
  AND tl.subsidiary = 12 AND t.type IN ('CustInvc','CustCred')
  AND tl.mainline = 'F' AND tl.taxline = 'F'
  AND tl.item IS NOT NULL AND tl.account IS NOT NULL
GROUP BY TO_CHAR(t.trandate,'YYYY-MM-DD'), l.name
```

## Q4 & Q5 — Hourly queries — DISABLED (Hourly Drill section removed this build)

The Hourly Drill section is currently taken out of the email, so **do not run Q4 or Q5**. They are
kept here verbatim for easy restore when the section returns (re-add the SECTION:hourly_drill block to
the template, set `sections.hourly_drill`, and re-enable these). No `hourly_blocks` repeat is built.

<details><summary>Q4 — Hourly drill (Khiang only, NS direct true sale time) — DO NOT RUN</summary>

```sql
SELECT TO_CHAR(t.createddate,'HH24') AS hr, TO_CHAR(t.trandate,'YYYY-MM-DD') AS d,
       l.name AS location, COUNT(DISTINCT t.id) AS bills, SUM(-tl.netamount) AS revenue
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction
LEFT JOIN location l ON tl.location = l.id
WHERE t.trandate IN (TO_DATE('{D1}','YYYY-MM-DD'),TO_DATE('{D8}','YYYY-MM-DD'))
  AND tl.subsidiary = 12 AND tl.location = 27 AND tl.class = 231
  AND t.type IN ('CustInvc','CustCred')
  AND tl.mainline = 'F' AND tl.taxline = 'F'
  AND tl.item IS NOT NULL AND tl.account IS NOT NULL
GROUP BY TO_CHAR(t.createddate,'HH24'), TO_CHAR(t.trandate,'YYYY-MM-DD'), l.name
```
NOTE: Khiang `trandate` rolls to next day for late-night sales — use `createddate` for the hourly bucket.
</details>

<details><summary>Q5 — Odoo hourly (non-Khiang problem branches; run AFTER severity flagging) — DO NOT RUN</summary>

Skip entirely if no non-Khiang problem branches. For each flagged branch:
```python
domain = [["date_order_date","in",[D1, D8]], ["x_location","=", branch_code]]
fields = ["date_order","amount_subtotal","x_location","x_business_unit"]
# paginate limit=100 offset+=100 while has_more; order "date_order asc"
```
**Scale Odoo shape to NS truth** (v2.4 fix): `scale = ns_daily_total / odoo_d1_total` (1.0 if odoo 0);
multiply each hour's Odoo revenue by `scale`. Odoo gives distribution shape (true sale time),
NS gives the daily total (system of record). Label src "Odoo (scaled to NS)".
</details>

---

## Completeness checks — GATE the send (HARD-STOP on failure; never send zeros/partials)

1. Q1 returned rows for D1 across expected branches (≈16 active locations).
2. D1 itself has revenue rows for ≥1 branch (else likely no-data day — flag, do NOT send zeros).
3. Q2/Q3 window covers expected ~30 day-count.
4. A branch with 0 rows in a section → render `—`/`·`, do NOT fail the run.
5. **Timezone guard:** resolved report_date ≠ yesterday-BKK → STOP and report (the off-by-one bug).
6. Zero revenue across ALL branches → almost certainly a data issue → abort with diagnostic.

## Accrual caution

Daily sales are pre-VAT transactionline revenue and do NOT depend on month-end accruals, so the daily
number is safe to send intra-period. (Accrual caveat applies to P&L/EBIT reports, not this one.)
