# ActionCity — Queries (data layer)

Defines the NetSuite source for every `{{token}}` in `actioncity-template.html`. Deterministic only.
Tool: `mcp__9ffe807f-86e2-4035-bda1-ad1a624d35ef__ns_runCustomSuiteQL` (param name `query`). Read-only.

---

## Fixed params (PIN — these silently wander)

- **Subsidiary:** 22 (ACTIONCITY THAILAND) — filter on `tl.subsidiary`, NOT the header.
- **Store locations:** 172 Warehouse HQ (Liberty), 174 Fashion Island, 176 Siam Square One, 198 Central Ladprao, 235 ACT Westgate, 177 E-Commerce.
- **Vending machines:** 194 Rama 9, 196 Bangkapi 1, 197 Bangkapi 2, 210 IconSiam 6F, 347 ActionCityHQ.
- **All on-hand locations (stock):** 172,174,176,177,194,196,197,198,210,235,347.
- **BU classes:** 8 Retails, 10 Vending, 126 Shopee, 127 Lazada, 128 TikTok, 107 E-Commerce, 12 Wholesale.
- **Channel customers:** intercompany ACTIONCITY PTE = 14186; wholesale Siam Specialty = 132. Retail velocity filter: `t.entity NOT IN (14186,132)`.
- **Consignment vendors (return, no cost):** Big Box International (V-00698), ACTIONCITY PTE; MNT-series SKUs (`itemid LIKE 'MNT%'`, via V-00654).
- **Intercompany purchase vendors:** Pony on Wheel TH 5735, Toysinbox 3655, Chaw Retailing 43623, ActionCity TH interco 12380.

## Universal line filters (apply to ALL sales queries)

```
t.type IN ('CustInvc','CustCred') AND t.posting='T'
AND tl.subsidiary=22 AND tl.mainline='F' AND tl.itemtype='InvtPart'
AND tl.netamount <> 0      -- excludes the +1/-1 cost-wash pair on vending/marketplace lines
```

## CRITICAL number rules (these are the drift-fixers)

1. **Net sales = `-SUM(tl.netamount)`** (revenue stored negative; credit memos positive → returns net out automatically). **Never `SUM(ABS(netamount))`** — that ADDS returns back (the W22 bug: ฿48k of returns made ABS read ฿452.9k vs true net ฿356.9k).
2. **Units = `SUM(ABS(tl.quantity))`** with the `netamount<>0` filter (wash lines removed) — clean unit counts.
3. **GP = `-SUM(tl.netamount) - SUM(ABS(tl.quantity)*item.averagecost)`**; `averagecost` is THB base, do NOT FX-convert. GP% = GP / net.
4. **PO/receipt value IS foreign currency** → `tl.netamount * exchangerate`. Currency ids: 1 THB, 3 USD(~32.76), 7 CNY(~4.8), SGD(~25.7). Verify currency by vendor country (a CNY buy booked USD inflates ~6.8×).
5. **Collectables** = `REGEXP_LIKE(item.displayname,'[0-9]00%')` (100/200/300/400/1000% premium figures).
6. `ORDER BY` on a `GROUP BY` query can 400 — sort client-side when it does. Retry a failed query once (wait 20–90s); do not restart the routine.

---

## Date logic — Asia/Bangkok, computed at runtime

This routine runs at the **end of the trading day (~22:00 BKK)**, so it reports the day that just closed:

- `report_date = now(Asia/Bangkok).date()`  (TODAY — the closing day). Honour a manual `REPORT_DATE=YYYY-MM-DD` override for back-fills.
- `iso_week` = ISO week of report_date; `w_minus1..w_minus4` = the 4 prior ISO week numbers.
- `wtd_start` = Monday of report_date's ISO week. `wtd_days` = days elapsed Mon→report_date inclusive.
- Week windows (Mon–Sun): build from `TO_CHAR(t.trandate,'IYYY-IW')`. Full prior weeks W(iso-1)…W(iso-6) are complete; the current ISO week is week-to-date.
- Display tokens derived from report_date: `report_date_display` ("8 Jun 2026"), `report_weekday` ("Mon"), `generated_at`.

> Timezone guard differs from the morning-report default: here report_date = TODAY-BKK (not yesterday). If the host clock is UTC, `now(BKK)` may still read the previous calendar day before 17:00 UTC — compute with an explicit Asia/Bangkok tz, never bare server time.

---

## Token → query map

### A. Today (KPI headline + best sellers) — `day_net, day_units, day_bills, day_bills_split, day_ticket, day_wow_pct, day_wow_arrow/color, best_today_list`
```sql
-- Today totals + RETAIL split (retail excludes wholesale 132 and intercompany 14186)
SELECT -SUM(tl.netamount) AS net, SUM(ABS(tl.quantity)) AS units, COUNT(DISTINCT t.id) AS bills,
  -SUM(CASE WHEN t.entity NOT IN (132,14186) THEN tl.netamount ELSE 0 END) AS retail_net,
  COUNT(DISTINCT CASE WHEN t.entity NOT IN (132,14186) THEN t.id END) AS retail_bills
FROM transaction t JOIN transactionline tl ON tl.transaction=t.id
WHERE <universal filters> AND t.trandate = TO_DATE(:report_date,'YYYY-MM-DD');
-- day_net = net (all channels, reconciles to NetSuite day total).
-- **day_ticket = retail_net / retail_bills**  ← AVG TICKET EXCLUDES WHOLESALE/INTERCO (bulk B2B distorts it).
-- day_bills = total bills; day_bills_split = "{retail_bills} retail + {bills-retail_bills} wholesale · {units} units".
-- Same-day-last-week for WoW: t.trandate = report_date - 7 → day_wow_pct = net/net_lw - 1.
-- Best sellers today (>=5 units, RETAIL only — exclude 132,14186): GROUP BY item, HAVING SUM(ABS(quantity))>=5, top 6.
```

### A2. Daily sales by branch (today) — `today_branch_rows[] (tb_name, tb_net, tb_bills, tb_ticket, tb_flag, tb_bg, tb_color)`
```sql
SELECT tl.location AS loc, -SUM(tl.netamount) AS net, COUNT(DISTINCT t.id) AS bills,
  -SUM(CASE WHEN t.entity NOT IN (132,14186) THEN tl.netamount ELSE 0 END) AS retail_net,
  COUNT(DISTINCT CASE WHEN t.entity NOT IN (132,14186) THEN t.id END) AS retail_bills
FROM transaction t JOIN transactionline tl ON tl.transaction=t.id
WHERE <universal filters> AND t.trandate = TO_DATE(:report_date,'YYYY-MM-DD')
GROUP BY tl.location;   -- order by net desc client-side
-- tb_net = total net (so a wholesale drop is visible); tb_ticket = retail_net/retail_bills (excl wholesale).
-- tb_flag = "WHOLESALE" pill when net >> retail_net (a B2B order booked to that location); else blank.
-- Branches with no rows today → omit (or list under today_branch_note as "no sales posted yet").
```

### B. Net sales by week — `week_rows[] (wk_label, wk_net, wk_bar_pct, wk_bar_color, ...)`
```sql
SELECT TO_CHAR(t.trandate,'IYYY-IW') AS isowk, -SUM(tl.netamount) AS net, SUM(ABS(tl.quantity)) AS units
FROM transaction t JOIN transactionline tl ON tl.transaction=t.id
WHERE <universal filters> AND t.trandate >= TO_DATE(:wk_window_start,'YYYY-MM-DD')   -- 7 ISO weeks back
GROUP BY TO_CHAR(t.trandate,'IYYY-IW');
-- 6 full prior weeks + current WTD. bar_pct = net / max(net)*100. Current week label "W{iso} (WTD)".
```

### C. Revenue by BU — `bu_rows[]`
```sql
SELECT tl.class AS cls,
  SUM(CASE WHEN t.trandate BETWEEN :wprev_start AND :wprev_end THEN -tl.netamount ELSE 0 END) AS prev,
  SUM(CASE WHEN t.trandate BETWEEN :wtd_start  AND :report_date THEN -tl.netamount ELSE 0 END) AS wtd
FROM transaction t JOIN transactionline tl ON tl.transaction=t.id
WHERE <universal filters> AND t.trandate >= :wprev_start
GROUP BY tl.class;
-- Map class id→name (8 Retails,10 Vending,126 Shopee,127 Lazada,128 TikTok,107 E-Com,12 Wholesale).
-- bu_share = wtd / SUM(wtd). bu_wow = wtd/prev-1.
```

### D. Revenue by branch — `branch_rows[]`  — **3-WEEK TREND** (br_w2, br_w1, br_w0, trend, flag)
Show the **last 3 COMPLETE weeks** of net revenue per branch (not a single WTD-vs-prior compare — that
was confusing with partial weeks and the wholesale spike). A 3-week trend makes declines (e.g. Central
Ladprao) and dark stores (Westgate) obvious. Column labels via `br_w2_label`/`br_w1_label`/`br_w0_label`.
```sql
SELECT tl.location AS loc,
  SUM(CASE WHEN t.trandate BETWEEN :w2s AND :w2e THEN -tl.netamount ELSE 0 END) AS w2,   -- 3rd-newest full wk
  SUM(CASE WHEN t.trandate BETWEEN :w1s AND :w1e THEN -tl.netamount ELSE 0 END) AS w1,   -- 2nd-newest full wk
  SUM(CASE WHEN t.trandate BETWEEN :w0s AND :w0e THEN -tl.netamount ELSE 0 END) AS w0    -- newest full wk
FROM transaction t JOIN transactionline tl ON tl.transaction=t.id
WHERE <universal filters> AND t.trandate BETWEEN :w2s AND :w0e
GROUP BY tl.location;   -- sort by w0 desc client-side
-- Map loc→name. br_w0_color: green if w0>=w1 else red. br_trend ▲/▼ on w0 vs w1.
-- DARK flag (red pill) when w0=0 AND (w1>0 OR w2>0) → store/POS dark. WHOLESALE flag when a B2B
--   order is booked to a location (e.g. Warehouse HQ) — note it inflates that week's bar.
-- Current week's live (WTD) per-branch sits in the Daily-sales-by-branch section, not here.
```

### E. Category mix (4-wk) — `cat_rows[]`
```sql
SELECT CASE WHEN REGEXP_LIKE(i.displayname,'[0-9]00%') THEN 'Collectable' ELSE 'Rest' END AS cat,
  COUNT(DISTINCT tl.item) AS skus, SUM(ABS(tl.quantity)) AS units, -SUM(tl.netamount) AS net,
  ROUND(-SUM(tl.netamount)/SUM(ABS(tl.quantity)),0) AS asp,
  ROUND(100*(-SUM(tl.netamount)-SUM(ABS(tl.quantity)*i.averagecost))/(-SUM(tl.netamount)),1) AS gp
FROM transaction t JOIN transactionline tl ON tl.transaction=t.id JOIN item i ON i.id=tl.item
WHERE <universal filters> AND t.trandate >= :trailing_4wk_start
GROUP BY CASE WHEN REGEXP_LIKE(i.displayname,'[0-9]00%') THEN 'Collectable' ELSE 'Rest' END;
-- cat_share = net/total. gp_color red (#c43b27) if <50 else green (#1f7a55).
```

### F. Reorder — `reorder_rows[]`  (retail velocity W-4..W0, stock, cover, action)
```sql
WITH oh AS (SELECT iil.item itm, SUM(iil.quantityonhand) stock FROM inventoryitemlocations iil
            WHERE iil.location IN (<all on-hand locs>) GROUP BY iil.item),
s AS (SELECT tl.item itm,
        SUM(CASE WHEN t.trandate BETWEEN :w4s AND :w4e THEN ABS(tl.quantity) ELSE 0 END) w4,
        ... w3, w2, w1,
        SUM(CASE WHEN t.trandate BETWEEN :wtd_start AND :report_date THEN ABS(tl.quantity) ELSE 0 END) w0
      FROM transaction t JOIN transactionline tl ON tl.transaction=t.id
      WHERE <universal filters> AND t.entity NOT IN (14186,132) AND t.trandate >= :w4s GROUP BY tl.item)
SELECT i.displayname, s.w4,s.w3,s.w2,s.w1,s.w0, NVL(oh.stock,0) stock,
       ROUND(NVL(oh.stock,0)/((s.w3+s.w2+s.w1+s.w0)/4.0),1) cover
FROM s JOIN item i ON i.id=s.itm LEFT JOIN oh ON oh.itm=s.itm
WHERE (s.w1+s.w0)>=20 AND NVL(oh.stock,0)<90 AND (s.w3+s.w2+s.w1+s.w0)>0
      AND NVL(oh.stock,0)/((s.w3+s.w2+s.w1+s.w0)/4.0) < 3;   -- sort by w0 desc client-side
-- Action: cover<0.7 & selling most wks → REORDER↑ ; cover<2 → REORDER ; <2.5 → SMALL BUY ; faded → WATCH.
```

### G. Top 20 — `top_rows[]`  (W-1 + W0, stock, net, GP, GP%) — **RETAIL ONLY**
**Exclude wholesale (132) and intercompany (14186)** so a lumpy B2B drop never skews the ranking
(the 10 Jun Siam Specialty order inflated Opandee S4 +60, Upset Duck Status +48, Oyo +48). Header
labels use independent tokens `top_w1_label` / `top_w0_label` (e.g. "W23"/"W24"), NOT the current
ISO week — so the Monday week-rollover never mislabels the two columns. Wholesale is shown separately
(query G2) in `top_note`.
```sql
WITH oh AS (...), s AS (
  SELECT tl.item itm, SUM(ABS(tl.quantity)) u2,
    SUM(CASE WHEN t.trandate BETWEEN :w1s AND :w1e THEN ABS(tl.quantity) ELSE 0 END) uw1,
    SUM(CASE WHEN t.trandate BETWEEN :w0s AND :w0e THEN ABS(tl.quantity) ELSE 0 END) uw0,
    -SUM(tl.netamount) net, (-SUM(tl.netamount)-SUM(ABS(tl.quantity)*i.averagecost)) gp
  FROM transaction t JOIN transactionline tl ON tl.transaction=t.id JOIN item i ON i.id=tl.item
  WHERE <universal filters> AND t.entity NOT IN (132,14186)        -- RETAIL ONLY
    AND t.trandate BETWEEN :w1s AND :w0e GROUP BY tl.item)
SELECT i.displayname, NVL(oh.stock,0) stock, s.uw1, s.uw0, s.u2,
  ROUND(s.u2/:two_wk_days,1) perday, ROUND(s.net,0) net, ROUND(s.gp,0) gp, ROUND(100*s.gp/s.net,1) gp_pct
FROM s JOIN item i ON i.id=s.itm LEFT JOIN oh ON oh.itm=s.itm;  -- top 20 by u2 client-side
-- gp_pct red (#c43b27) if <50. :two_wk_days = the two complete weeks' day count.
-- top_w1_label / top_w0_label = the two week labels covered (e.g. "W23" / "W24").
```

### G2. Wholesale this period (shown separately under Top 20) — for `top_note`
```sql
SELECT -SUM(tl.netamount) net, SUM(ABS(tl.quantity)) units, COUNT(DISTINCT tl.item) skus, COUNT(DISTINCT t.id) orders
FROM transaction t JOIN transactionline tl ON tl.transaction=t.id
WHERE <universal filters> AND t.entity = 132 AND t.trandate BETWEEN :w1s AND :w0e;
-- Render one line: "Wholesale (Siam Specialty): ฿{net} / {units} u across {skus} SKUs ({orders} orders) — excluded above."
```

### H. New arrivals — `arrival_rows[]`
```sql
-- Launch week from SKU code YYYYWWW-NNNNN. Recent launches (SKU LIKE '2026W%').
-- Recvd = SUM received via PreviousTransactionLineLink (previoustype='PurchOrd', quantity>0).
-- Sold = -... units since launch ; On hand = oh.stock. Read = JUST IN/HOT/SELLING/SLOW/OVERSTOCK by on-hand vs sold.
```

### I. Purchasing open POs — `po_rows[]`  (APPROVED POs ONLY)
**Only show approved POs.** `transaction.approvalstatus` codes: **1 = Pending Approval, 2 = Approved, 3 = Rejected.**
Require `po.approvalstatus = 2` — never list pending-approval or rejected POs (they are not committed orders).
```sql
-- NOTE: there is NO `quantityremaining` column — it 400s. Open qty = quantity - quantityshiprecv (per line).
SELECT po.tranid, i.displayname,
       SUM(ABS(ptl.quantity) - NVL(ptl.quantityshiprecv,0)) AS open_qty,
       SUM((ABS(ptl.netamount)*po.exchangerate) * (ABS(ptl.quantity)-NVL(ptl.quantityshiprecv,0))/NULLIF(ABS(ptl.quantity),0)) AS open_thb
FROM transaction po JOIN transactionline ptl ON ptl.transaction=po.id JOIN item i ON i.id=ptl.item
WHERE po.type='PurchOrd' AND po.approvalstatus = 2          -- APPROVED ONLY (exclude appr 1 pending / 3 rejected)
  AND ptl.mainline='F' AND ptl.subsidiary=22
  AND (ABS(ptl.quantity) - NVL(ptl.quantityshiprecv,0)) > 0  -- still open (not fully received)
GROUP BY po.tranid, i.displayname;   -- sort by open_thb client-side; flags per prediction.md
```
> `po.approvalstatus`: 1 = Pending Approval, 2 = Approved, 3 = Rejected. **Always require = 2.**
> Many old POs leave a 1-unit residual open — if that noise appears, raise the threshold to `> 1`.
> Same `approvalstatus = 2` rule applies to any "raised this period" / "received" PO cuts.

### J. Dead stock — `dead_owned_rows[]`, `dead_consign_rows[]`, scalars `dead_owned_skus/value`
```sql
-- dead set: oh.stock>0 AND item NOT IN (sold with netamount<>0 since report_date-28).
-- Classify by PO vendor: consignment (Big Box / ACTIONCITY PTE / MNT prefix), intercompany (Pony/Toysinbox/Chaw/12380), else OWNED.
-- Owned rows: on_hand/averagecost/price, ORDER BY on_hand DESC (sort client-side; highest units first).
-- Consignment summary: per supplier SKUs + units (MNT, Big Box, ACTIONCITY PTE, Pony/Toysinbox).
```

---

## Completeness checks — gate the send (HARD-STOP on fail)

1. **Today has rows:** Query A returns net>0 / bills>0 for report_date. If zero → likely POS not yet posted (the ~1-day lag) → **STOP, do not send a zero report**; post a "data-not-ready" note to the failure channel.
2. **Week series present:** Query B returns ≥6 weeks; current-week WTD present.
3. **Branches present:** Query D returns rows for the staffed stores (172,174,176,198). A store at 0 is allowed but sets its DARK flag (don't fail).
4. **Net definition sanity:** for any week, `net (-SUM)` ≤ `invoices (-SUM where type=CustInvc)`; if net > invoices, a sign error crept in → STOP.
5. **Timezone guard:** report_date == today Asia/Bangkok (this is an EOD routine). If it resolved to a different day → STOP and report.
6. Per-section empty list → render `—` / omit its SECTION; never fail the whole run on one empty table.
