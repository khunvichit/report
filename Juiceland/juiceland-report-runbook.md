# Juiceland Report — Runbook (file #3 of 3)

Orchestration + the **NEW PRODUCTS** definition that feeds Section 4 (New Product Launches)
and the anomaly summary. Pair with: `juiceland-queries.md` (data map) · `juiceland-template.html`
(format) · `juiceland-routine-prompt.md` (run order).

> WHY THIS FILE EXISTS: Section 4 broke once because the new-product list was a hand-typed
> registry that got lost. This version defines new products as a **rule** (first sold in the
> trailing 30 days), so Query C is self-selecting and the section can never go stale again.

---

## 1. What counts as a "new product"

**Rule:** a product is *new* if its **first-ever sale** (across all Juiceland history) falls
within the **trailing 30 days** of `report_date`. No manual memo list to maintain.

Normalization (critical — kills duplicate/typo noise):
- Collapse whitespace variants by `UPPER(TRIM(REPLACE(REPLACE(memo, CHR(10),''), CHR(13),'')))`.
  This merges e.g. `S5 MANGO SMOOTHIE 16OZ` and `S5 MANGO SMOOTHIE 16OZ\n` so an old product
  doesn't look "new" just because a trailing-newline variant of its memo appeared recently.
- A product is new only if its **normalized** name has *no* sale older than 30 days.
- This automatically excludes the late-March POS/NetSuite go-live items (they're >30 days old).

**Exclusions (drop these rows even if they pass the rule):**
- Memos in `('VAT','CREDIT DEDUCT')` (already filtered in SQL).
- Malformed concatenated memos containing an embedded newline + second product
  (e.g. `DRAGON FRUIT 400G.\n3 kinds of fruit...`).
- Generic/uncategorizable memos (e.g. the bare Thai string `อาหารและเครื่องดื่ม` = "food & beverage").
- Optional hygiene floor: if `total_qty < 1` over the window, skip.

---

## 2. Auto-categorization → the 3 template buckets

Section 4 has a fixed 3-cell strip + grouped tables in this order: **Drinks · Seasonal Fruits · New Category.**
Assign each new product by keyword (first match wins, top to bottom):

| Type token | Bucket (label / icon) | Matches memo containing (case-insensitive) |
|-----------|------------------------|---------------------------------------------|
| `fruit`   | 🍉 SEASONAL FRUITS     | a fruit-pack pattern — `400G`, `400 G`, `(PACK)`, or `LYCHEE / MANGOSTEEN / ROSE APPLE / CANTALOUPE / DRAGON FRUIT` |
| `new_cat` | ⭐ NEW CATEGORY        | `OVERNIGHT OAT`, `GREEK YOGURT`, `GRANOLA`, `HONEY TOPPING`, `MANGO TOPPING`, `CROISSANT`, `SALAD`, `SANDWICH`, `WRAP`, `ONIGIRI`, `RICE BALL` |
| `drinks`  | 🥤 DRINKS (default)    | everything else — smoothies, cold-pressed, `OZ`, `ML`, `(BOTTLE)`, Pride Parrot, Hot Chocolate/Mocha, Fanta/Sprite/Coke, espresso/latte/tea |

Type-cell colours (already in the template): Drinks `#E3F2FD`/`#1976D2` · Fruit `#FCE4EC`/`#AD1457` ·
New Category `#E8F5E9`/`#2E7D32`. Only render a type table if that bucket has ≥1 SKU.

> Categorization is keyword-based and editable. To re-assign a product, adjust the keyword lists
> above — do NOT hard-code a per-product table (that's what went stale before).

---

## 3. Query C — self-selecting (replaces the old `{NEW_PRODUCT_MEMO_LIST}` version)

This is the live daily query (it also lives in `juiceland-queries.md` as Query C). It returns the
per-day / per-branch history for every product that is new under the rule above.

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

Roll location 169 into MW1 in code (same as Query A). Drop excluded memos (§1) after fetch.

---

## 4. Status logic (per SKU → `{{status_badge}}`)

Compute from the Query C rows for each product (all branches combined):

```
days_live   = report_date - first_sold + 1
yest_units  = qty at report_date
velocity_7d = sum(qty over last 7 days incl. report_date) / 7
gap_days    = report_date - last_sold_date   (0 if sold yesterday)
target/day  = Drinks 3 · Seasonal Fruit 1 · New Category 2   (tunable defaults)
```

Badge (first match wins), per the template legend:
- ⚪ **made-to-order / no sales yet** — total_units == 0, or product is clearly MTO.
- 🟠 **stock-out suspect** — gap_days ≥ 2 (sold before, then nothing for 2+ days).
- 🟢 **on target** — velocity_7d ≥ target.
- 🟡 **below target** — 0.5×target ≤ velocity_7d < target.
- 🔴 **waste risk** — velocity_7d < 0.5×target.

Per-row fields: `{{launch}}` = first_sold (`D Mon`), `{{notes}}` = `"{days_live}d live"` (+ `"MTO"` if applicable),
`{{branch_split}}` = `"MW1 {n} · SE3 {n} · PKT {n}"` (units, report-date or to-date — keep consistent;
default = to-date), `{{total_units}}`/`{{total_rev}}` = sums over the window, `{{yest_units}}` = report-date units.

---

## 5. Section-4 aggregate tokens

| Token | From |
|-------|------|
| `{{np_total_units}}` `{{np_total_rev}}` | sum of all new-product units / revenue over the window |
| `{{np_summary_line}}` | e.g. `"{N} SKUs live · {new_in_7d} launched this week"` |
| `{{drinks_n}}` `{{fruit_n}}` `{{new_cat_n}}` | SKU count per bucket |
| `{{drinks_todate_units/rev}}` etc. | per-bucket sums over the window |
| `{{drinks_yest}}` `{{drinks_yest_rev}}` etc. | per-bucket units / revenue at report_date (Lark group msg) |

`sections.newproduct` is implicitly always on (the template block is not SECTION-gated). If the rule
returns **zero** new products, set `np_total_units=0`, render each bucket as `—`, and put
`np_summary_line = "No launches in the trailing 30 days."` — never leave the tokens unresolved.

---

## 6. Maintenance / discovery (NOT a daily query)

To eyeball the current new-product set (e.g. when sanity-checking categorization), run the
discovery query below ad-hoc. **Do not** add it to `juiceland-queries.md` — it is not part of the
daily run and must not bloat the queries file.

```sql
WITH norm AS (
  SELECT t.trandate AS trandate, tl.memo AS memo,
         UPPER(TRIM(REPLACE(REPLACE(tl.memo, CHR(10), ''), CHR(13), ''))) AS nmemo,
         tl.quantity AS quantity, tl.netamount AS netamount
  FROM transaction t JOIN transactionline tl ON t.id = tl.transaction
  WHERE t.type = 'CustInvc' AND tl.mainline = 'F'
    AND tl.location IN (33,105,109,169) AND tl.class = 3 AND tl.netamount < 0
    AND tl.memo IS NOT NULL AND UPPER(TRIM(tl.memo)) NOT IN ('VAT','CREDIT DEDUCT')
)
SELECT MIN(memo) AS memo, MIN(trandate) AS first_sold,
       SUM(ABS(quantity)) AS total_qty, SUM(ABS(netamount)) AS total_rev,
       COUNT(DISTINCT trandate) AS days_sold
FROM norm
GROUP BY nmemo
HAVING MIN(trandate) >= TO_DATE('{REPORT_DATE}','YYYY-MM-DD') - 30
ORDER BY total_qty DESC
```

---

## 7. Fixed parameters (mirror of queries.md — do not let these drift)

Subsidiary 12 (SFB) · Class 3 (Food : Juice Land) · Locations 33 (MW1) / 105 (SE3) / 109 (PKT) /
169→roll into MW1 · Branch order MW1, SE3, PKT · TZ Asia/Bangkok · net = `-SUM(netamount)`, ex-VAT.

---

## Reference: latest discovery snapshot (report_date 2026-06-09, 30-day window)

For sanity only — the live run recomputes this every day. Genuine launches detected:

- 🥤 Drinks: PRIDE PARROT RED (77u/฿14,374), PRIDE PARROT YELLOW (45u/฿8,393),
  HOT CHOCOLATE 8 oz (40u/฿4,860), Fanta Strawberry/Orange/Fruit Punch (Bottle), Sprite 500ml,
  HOT MOCHA 8 oz, Iced Espresso Coconut/Orange 12oz, Pride Parrot Red/Yellow Smoothie 22oz.
- 🍉 Seasonal Fruits: LYCHEE 400G. (15u), MANGOSTEEN 400g. (3u), ROSE APPLE 400G. (3u), Cantaloupe 400g.
- ⭐ New Category: Overnight Oat Mango (32u/฿8,045) & Berry, Vanilla Bean / Blueberry / Raspberry
  Greek Yogurt, Chicken Club Croissant, Caesar Salad, Japanese Salad, Granola/Honey/Mango toppings.
- Excluded as noise: `DRAGON FRUIT 400G.\n3 kinds of fruit...` (malformed), `อาหารและเครื่องดื่ม` (generic).
