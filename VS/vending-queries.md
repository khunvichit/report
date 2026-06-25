# vending-queries.md — Data sources for every `{{token}}` in vending-template.html

Everything in `vending-template.html` traces back to a value computed from one of these queries plus
runtime date logic. The routine runs the queries, validates with completeness checks, then builds
the `data.json` that `fill_template.py` consumes.

---

## Fixed params (pinned — they silently wander otherwise)

| Param | Value | Verified via |
|---|---|---|
| Subsidiary | `13` (Vending Services Company Limited) | `ns_getSubsidiaries` 2026-05-26 |
| Classifications (BUs) | `Vendi` (class_id 104) + `Vending` (class_id 14) | Live NS query |
| Excluded class | `General` (class_id 102, HQ adjustments only) | Excluded by name |
| Excluded location | `Vending HQ` (loc_id 79, admin) | Excluded by name |
| Transaction types | `'CustInvc', 'CustCred'` | — |
| Line filter | `mainline='F' AND taxline='F' AND item IS NOT NULL AND account IS NOT NULL` | — |

---

## Date logic — Asia/Bangkok, computed at runtime

```python
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta

bkk = ZoneInfo("Asia/Bangkok")
report_date = REPORT_DATE_OVERRIDE or (datetime.now(bkk).date() - timedelta(days=1))

D1 = report_date                            # yesterday
D2 = D1 - timedelta(days=1)                 # DoD baseline
D8 = D1 - timedelta(days=7)                 # WoW baseline (same weekday)
MTD_START = D1.replace(day=1)
THIRTY_D_START = D1 - timedelta(days=29)
```

NEVER use server UTC. NEVER hardcode dates. Honour `REPORT_DATE_OVERRIDE` for back-fills.

### Derived display tokens (scalars in data.json)

| Token | Format | Example |
|---|---|---|
| `report_date_display` | `DD Month YYYY` | `25 May 2026` |
| `report_date_short` | `DD Mon` | `25 May` |
| `report_date_weekday_th` | Thai weekday | `วันจันทร์` |
| `mtd_start_short` | `DD Mon` | `1 May` |
| `mtd_days` | int | `25` |
| `generated_display` | `DD Month YYYY` | `26 May 2026` |

---

## Q1 — D1 + D2 + D8 daily per (location × BU)

Drives: per-machine table (§8 Sales by Machine), KPI cards (§4), BU heatmap (§7), Executive Insight totals.

```sql
SELECT
  TO_CHAR(t.trandate, 'YYYY-MM-DD') AS d,
  l.name AS location,
  c.name AS bu,
  COUNT(DISTINCT CASE WHEN t.type='CustInvc' THEN t.id END) AS bills,
  SUM(-tl.netamount) AS revenue
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction
LEFT JOIN classification c ON tl.class = c.id
LEFT JOIN location     l ON tl.location = l.id
WHERE t.trandate IN (TO_DATE('{D1}','YYYY-MM-DD'),
                     TO_DATE('{D2}','YYYY-MM-DD'),
                     TO_DATE('{D8}','YYYY-MM-DD'))
  AND tl.subsidiary = 13
  AND t.type IN ('CustInvc','CustCred')
  AND tl.mainline = 'F' AND tl.taxline = 'F'
  AND tl.item IS NOT NULL
  AND tl.account IS NOT NULL
  AND c.name IN ('Vendi','Vending')
  AND l.name != 'Vending HQ'
GROUP BY t.trandate, l.name, c.name
```

**Expected**: ~3 dates × ~20 active (location, BU) pairs = ~60 rows.

---

## Q2 — 30-day total per (day × BU)

Drives: §5 30-Day Revenue by BU stacked bar + legend.

```sql
SELECT
  TO_CHAR(t.trandate, 'YYYY-MM-DD') AS d,
  c.name AS bu,
  SUM(-tl.netamount) AS revenue,
  COUNT(DISTINCT CASE WHEN t.type='CustInvc' THEN t.id END) AS bills
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction
LEFT JOIN classification c ON tl.class = c.id
WHERE t.trandate BETWEEN TO_DATE('{THIRTY_D_START}','YYYY-MM-DD') AND TO_DATE('{D1}','YYYY-MM-DD')
  AND tl.subsidiary = 13
  AND t.type IN ('CustInvc','CustCred')
  AND tl.mainline = 'F' AND tl.taxline = 'F'
  AND tl.item IS NOT NULL
  AND tl.account IS NOT NULL
  AND c.name IN ('Vendi','Vending')
GROUP BY TO_CHAR(t.trandate, 'YYYY-MM-DD'), c.name
```

**Expected**: 30 days × 2 BUs = ~60 rows.

---

## Q3 — 30-day total per (day × location) — for airport rollup

Drives: §6 30-Day Revenue by Airport stacked bar + legend.

```sql
SELECT
  TO_CHAR(t.trandate, 'YYYY-MM-DD') AS d,
  l.name AS location,
  SUM(-tl.netamount) AS revenue,
  COUNT(DISTINCT CASE WHEN t.type='CustInvc' THEN t.id END) AS bills
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction
LEFT JOIN location l ON tl.location = l.id
LEFT JOIN classification c ON tl.class = c.id
WHERE t.trandate BETWEEN TO_DATE('{THIRTY_D_START}','YYYY-MM-DD') AND TO_DATE('{D1}','YYYY-MM-DD')
  AND tl.subsidiary = 13
  AND t.type IN ('CustInvc','CustCred')
  AND tl.mainline = 'F' AND tl.taxline = 'F'
  AND tl.item IS NOT NULL AND tl.account IS NOT NULL
  AND c.name IN ('Vendi','Vending')
  AND l.name != 'Vending HQ'
GROUP BY TO_CHAR(t.trandate, 'YYYY-MM-DD'), l.name
```

Aggregate offline via `airport_of()` (see below) to roll into SVB / DMK.

**Expected**: 30 days × ~20 locations = ~600 rows.

---

## `airport_of()` — Python helper applied to query results

```python
def airport_of(loc_name):
    if loc_name == 'Crucible Event':       return 'BKK'   # pop-up; SFB convention
    if loc_name == 'Vending HQ':           return 'HQ'    # admin — excluded upstream anyway
    if 'T1' in loc_name:                   return 'SVB'   # any code containing T1 = Suvarnabhumi T1
    if loc_name.startswith(('05-', '09-')): return 'DMK'  # DMK pier codes (no T1)
    return 'SVB'  # safe default
```

---

## Per-machine MTD baseline — computed offline from Q2/Q3 raw rows

For each machine `m` (location), aggregate from the 30-day Q3 result over `MTD_START → D1`:

```python
mtd_avg_rev_m        = sum(daily_rev[m])   / mtd_days_present[m]
mtd_avg_bills_m      = sum(daily_bills[m]) / mtd_days_present[m]
mtd_high_m           = max(daily_rev[m])
mtd_low_m            = min(daily_rev[m])
mtd_days_present[m]  = count of distinct dates with revenue > 0 for that machine
```

Per-machine dynamic thresholds (per runbook §10):
```python
MIN_BILLS_m           = max(3,    mtd_avg_bills_m * 0.30)
ZERO_SALE_THRESHOLD_m = max(200,  mtd_avg_rev_m   * 0.30)
DROP_THRESHOLD        = 200    # static, matches SFB
SURGE_THRESHOLD       = 500    # static, matches SFB
```

---

## Severity classification (per runbook §6 Pillar 2)

```python
def severity(wow_pct, dod_pct, d1_bills, d8_bills, d8_rev, mtd_avg_bills_m, mtd_avg_rev_m):
    min_bills  = max(3,   mtd_avg_bills_m * 0.30)
    zero_thresh = max(200, mtd_avg_rev_m  * 0.30)
    # zero-sale day on a non-trivial baseline
    if d1_bills == 0 and d8_bills >= min_bills and d8_rev >= zero_thresh:
        return 'CRITICAL'   # 🚨
    if wow_pct <= -20 and dod_pct <= -10:
        return 'CRITICAL'   # 🚨
    if wow_pct <= -10 and dod_pct < 0:
        return 'HIGH'       # 🟠
    if wow_pct <= -5:
        return 'WATCH'      # ⚠
    if wow_pct >= 15 and dod_pct >= 10:
        return 'SURGE'      # 🔥
    if wow_pct >= 0:
        return 'POSITIVE'   # ✅
    return 'NEUTRAL'        # ─
```

A machine is **Problem** if severity ∈ {CRITICAL, HIGH, WATCH} OR `mtd_flag ∈ {NEW LOW, <80% avg}`.

---

## Completeness checks — gate the send

Run after queries, before building data.json. Hard-stop and notify on failure.

1. **Sub 13 returned rows.** Q1 must return ≥ 1 row for D1. If 0 → STOP (no-data day or NS sync issue).
2. **Both BUs present.** Q1 D1 must include at least one row each for `bu='Vendi'` and `bu='Vending'`.
   If a BU is missing entirely → STOP (likely class-id drift).
3. **Window length.** Q2/Q3 must contain exactly 30 distinct `d` values. If < 30 → STOP (period gap).
4. **Report date is yesterday-BKK.** Compute `expected = now(BKK).date() − 1`; assert `D1 == expected`
   unless `REPORT_DATE_OVERRIDE` is set. If mismatch → STOP (timezone guard).
5. **Per-branch missing-row handling** — a machine with 0 rows in a section renders `—`, not failure.
   The 3 known-silent machines (`T1MW4-14/18/19`) should appear as DATA-task rows, not as errors.
6. **General class is fully excluded.** If Q1/Q2/Q3 returns any row with `bu='General'` → STOP (the
   `c.name IN ('Vendi','Vending')` filter dropped somewhere — fix before sending).

---

## NetSuite tool reminders

- Use `mcp__9ffe807f-86e2-4035-bda1-ad1a624d35ef__ns_runCustomSuiteQL`. Parameter name is `query`.
- One retry on rate-limit (wait 20–60s). Do not restart the routine.
- Never `ORDER BY` on a `GROUP BY` query — sort the result in Python instead.
- Date format always `'YYYY-MM-DD'` inside `TO_DATE('...', 'YYYY-MM-DD')`.
