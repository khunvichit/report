# Vending Services Daily Sales Report — Runbook v1.0
**Sub 13 · Vending Services**
Last updated: 2026-05-26 | Author: Vichit | Forked from: SFB v2.7

> **⚡ EXECUTION MANDATE** — When this runbook is invoked, execute Sections 2–12 sequentially
> **without further user confirmation**. Do not ask for date input. Do not ask whether to send
> email. Do not ask whether to create tasks. Only stop if (a) NetSuite API returns a hard
> error after retry, or (b) idempotency check in Step 1 finds a prior email for the same `D1`.

> **📦 DATA SOURCE POLICY (v1.0)** — **NetSuite Sub 13 is the PRIMARY source for all Vending categories**.
> NS contains all records natively and counts receipts (vend events) rather than line items, so Avg Ticket
> is meaningful. Optional secondary source — vending telemetry / DEX feed — is reserved for a future
> v1.1+ stockout-detection layer and is **not used in v1.0**.

> **🔧 NO HOURLY DRILL** — Unlike SFB (Sub 12), Vending Services has no CCTV / on-shift staff to
> investigate hourly anomalies. Instead, machine-level flags become **service tickets** for the
> Quality Team to inspect the unit on-site (see §10 + §11).

> **🚧 PLACEHOLDER NOTICE** — Any `«TBD_…»` is a deliberate placeholder; fill it in before going
> live. Search the file for `«TBD_` to find all of them.

---

## 1. Schedule & Triggers

| Parameter | Value |
|-----------|-------|
| Trigger A | Manual chat: "Run Vending daily report" |
| Trigger B | Scheduled Lark workflow at **07:30 ICT** (D+0) — 30 min after SFB to space NS load |
| Trigger C | Manual back-fill: "Run Vending daily report for D1=YYYY-MM-DD" |
| Executor | Claude Code via Lark MCP |
| Expected runtime | ~30–45 seconds (faster than SFB because no hourly drill query) |
| Idempotency | Check Lark sent-mail before sending; skip if duplicate |

---

## 2. Date Parameters — Auto-Calculated

```
D1       = today(Asia/Bangkok) − 1 day      # yesterday (report date)
D2       = D1 − 1 day                       # DoD baseline
D8       = D1 − 7 days                      # WoW baseline
MTD_START = first day of D1's calendar month
30D_START = D1 − 29 days                    # for 30-day trend chart
```

### Display variables
| Variable | Format | Example (D1=2026-05-25) |
|----------|--------|------------------------|
| `D1_DISPLAY` | DD Month YYYY | `25 May 2026` |
| `D1_WEEKDAY` | Thai weekday | `วันจันทร์` |
| `MTD_START_DISPLAY` | DD Month | `1 May` |

### Timezone rule (MANDATORY)
- ✅ Use `now(Asia/Bangkok).date() − 1 day`
- ❌ Never use server UTC `today() − 1 day`

---

## 3. Machine Master (Sub 13) — verified against NetSuite 2026-05-26

Pulled live from NS: 11 Vendi (kiosk) locations + 12 Vending (machine) locations + 1 admin
(Vending HQ, excluded from sales). One pop-up location (Crucible Event) — no recent sales.

### SVB — Suvarnabhumi (Terminal 1) — 17 active sales locations

**Vendi kiosks (BU = Vendi · class_id 104):**
| Code | NS Location ID | Notes |
|---|---|---|
| 01-T1AE3-09A+B | 78 | Largest kiosk · D1 ฿87.5K (60.6% WoW) |
| 02-T1AE3-06+07 | 114 | |
| 03-T1BE3-03+04 | 116 | |
| 04-T1CE3-01+02 | 117 | |
| 05-T1DE3-01+02 | 118 | |
| 06-T1DW3-02+03 | 119 | |
| 07-T1EW3-01+02 | 120 | |
| 08-T1ME4-13+14 | 121 | |
| 10-T1BE1-02 | 231 | |

**Vending machines (BU = Vending · class_id 14):**
| Code | NS Location ID | Notes |
|---|---|---|
| T1AE3-05 | 213 | |
| T1BE1-01 | 227 | |
| T1BE3-02 | 214 | |
| T1CE3-03 | 215 | |
| T1FW3-02 | 216 | |
| T1GW2-08 | 342 | Smallest machine — low daily volume (~฿700/day) |
| T1GW4-05 | 217 | |
| T1MW4-14 | 222 | ⚠ Silent on recent D1/D2/D8 — verify status |
| T1MW4-18 | 220 | ⚠ Silent on recent D1/D2/D8 — verify status |
| T1MW4-19 | 223 | ⚠ Silent on recent D1/D2/D8 — verify status |

### DMK — Don Mueang — 3 active sales locations

**Vendi kiosks:**
| Code | NS Location ID | Notes |
|---|---|---|
| 09-321+322 | 122 | The single DMK Vendi kiosk |

**Vending machines:**
| Code | NS Location ID | Notes |
|---|---|---|
| 05-317 | 228 | |
| 05-318 | 236 | |

### Pop-up / Event (transient)
| Code | NS Location ID | BU | Notes |
|---|---|---|---|
| Crucible Event | 450 | Vendi | BKK pop-up — no sales in current 30-day window. Same physical event tracked by SFB Sub 12 Juice Land. Flag as NEW LOCATION when re-activates. |

### Admin / non-airport (EXCLUDE from sales analytics)
| Code | NS Location ID | BU | Notes |
|---|---|---|---|
| Vending HQ | 79 | General (class 102) AND Vending (class 14) | Headquarters — bookkeeping adjustments and credit memos only. **Excluded** from §6 Pillar 1/2 and §8 KPIs. |

### Airport derivation (from NS `location.name`)
```python
def airport_of(loc_name):
    if loc_name == 'Crucible Event': return 'BKK'   # pop-up, BKK default
    if loc_name == 'Vending HQ':     return 'HQ'    # admin — drop from sales
    if 'T1' in loc_name:             return 'SVB'   # any code containing T1 = Suvarnabhumi T1
    if loc_name.startswith(('05-', '09-')): return 'DMK'  # DMK pier codes (numeric prefix, no T1)
    return 'SVB'  # safe default
```

> **NetSuite filter — exclude General class and HQ**:
> Add `AND c.name IN ('Vendi','Vending')` and `AND l.name != 'Vending HQ'` to every Section 4 query.
> The `General` classification at HQ only contains credit-memo adjustments (small negative numbers
> like −฿868) which would pollute revenue totals.

> **New-machine protocol**: If a location appears in NS that isn't in this list, flag in the
> Executive Insight section AND create a DATA task to add it to the master.

---

## 4. NetSuite Configuration (PRIMARY — all categories)

### 4.1 D1 + D2 + D8 daily per (location × category)
```sql
SELECT
  TO_CHAR(t.trandate, 'YYYY-MM-DD') AS d,
  l.name AS location,
  c.name AS category,
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
GROUP BY t.trandate, l.name, c.name
ORDER BY t.trandate, revenue DESC
```

Returns ~3 dates × N machines × M categories rows. One round-trip.

> **NOTE** — confirm with NS admin whether Vending Services encodes product category on
> `classification` (like SFB encodes BU) or on `item.class` / `department`. Adjust the
> `LEFT JOIN classification c ON tl.class = c.id` clause accordingly.

### 4.2 30-day trend (Day × Category)
```sql
SELECT
  TO_CHAR(t.trandate, 'YYYY-MM-DD') AS d,
  c.name AS category,
  SUM(-tl.netamount) AS revenue,
  COUNT(DISTINCT CASE WHEN t.type='CustInvc' THEN t.id END) AS bills
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction
LEFT JOIN classification c ON tl.class = c.id
WHERE t.trandate BETWEEN TO_DATE('{30D_START}','YYYY-MM-DD') AND TO_DATE('{D1}','YYYY-MM-DD')
  AND tl.subsidiary = 13
  AND t.type IN ('CustInvc','CustCred')
  AND tl.mainline = 'F' AND tl.taxline = 'F'
  AND tl.item IS NOT NULL
  AND tl.account IS NOT NULL
GROUP BY TO_CHAR(t.trandate, 'YYYY-MM-DD'), c.name
ORDER BY d, revenue DESC
```

Returns ~30 days × N categories rows.

### 4.3 30-day trend (Day × Zone)
```sql
SELECT
  TO_CHAR(t.trandate, 'YYYY-MM-DD') AS d,
  l.name AS location,
  SUM(-tl.netamount) AS revenue,
  COUNT(DISTINCT CASE WHEN t.type='CustInvc' THEN t.id END) AS bills
FROM transaction t
JOIN transactionline tl ON t.id = tl.transaction
LEFT JOIN location l ON tl.location = l.id
WHERE t.trandate BETWEEN TO_DATE('{30D_START}','YYYY-MM-DD') AND TO_DATE('{D1}','YYYY-MM-DD')
  AND tl.subsidiary = 13
  AND t.type IN ('CustInvc','CustCred')
  AND tl.mainline = 'F' AND tl.taxline = 'F'
  AND tl.item IS NOT NULL AND tl.account IS NOT NULL
GROUP BY TO_CHAR(t.trandate, 'YYYY-MM-DD'), l.name
```

Aggregate offline via `zone_of()` (§3) to roll machines into BKK/PROV/MALL.

### 4.4 ~~Hourly drill~~ — **REMOVED in v1.0**
Vending Services is unattended and has no CCTV — there is no operational use for an hour-by-hour
breakdown. If a future version (v1.1+) plugs in DEX/telemetry data, the hourly query may be
re-introduced as a separate optional appendix.

### 4.5 Field semantics
| Concept | Field | Notes |
|---|---|---|
| Revenue (primary) | `SUM(-tl.netamount)` | Pre-VAT. Includes service charges if any. |
| Bills (real vends) | `COUNT(DISTINCT t.id WHERE type='CustInvc')` | One per vend event — use for Avg Ticket |
| Date | `t.trandate` | Posting date in NS |
| Location | `l.name` from `location` table | One row per physical machine |
| Category | «TBD — `c.name` from `classification` OR `item.department` OR similar» | Snacks / Drinks / Hot / Other (TBD) |

---

## 5. ~~Odoo Configuration~~ — **N/A in v1.0**

Vending Services does not use Odoo POS the way the food BUs do. If a separate telemetry source is
added in v1.1+, document it here.

---

## 6. Three-Pillar Analysis Thresholds (reduced from SFB's four)

> SFB had 4 pillars: Sales by Branch (range), DoD×WoW table, Discipline (hourly), Spike.
> Vending v1.0 collapses to **3 pillars**: Sales by Machine + DoD×WoW + Spike. No discipline
> pillar because there's no human-shift behavior to police.

### Pillar 1 — Sales by Machine (MTD-relative)
Shows each machine's D1 sales vs its own MTD statistics — high, low, average.

**Per-machine KPI** (NS daily totals, MTD_START → D1):
- `d1_rev` — current sales
- `mtd_high` / `mtd_low` / `mtd_avg`
- `d1_vs_avg` — `(d1_rev − mtd_avg) / mtd_avg × 100`
- `position_pct` — `(d1_rev − mtd_low) / (mtd_high − mtd_low) × 100`

**Flag rules**:
- D1 ≤ mtd_low → 🚨 NEW LOW (CRITICAL service ticket)
- D1 ≥ mtd_high → 🔥 NEW HIGH (FYI, document for restock-frequency tuning)
- D1 < mtd_avg × 0.80 → ⚠ Below 80% of avg (HIGH service ticket)
- D1 ≥ mtd_avg → ✅ At/above avg
- Machine with mtd_days_present < 3 → 🆕 NEW MACHINE (DATA task)

### Pillar 2 — Machine DoD × WoW Table
Show **every machine** with D1 / D2 / D8 / DoD% / WoW% / Severity. Sorted by WoW DESC.

**Severity** (same scheme as SFB):
- 🔥 SURGE — WoW ≥ +15% AND DoD ≥ +10%
- ✅ POSITIVE — WoW ≥ 0
- ─ NEUTRAL — −5% < WoW < 0
- ⚠ WATCH — WoW ≤ −5% AND (DoD < 0 OR WoW ≤ −10%)
- 🟠 HIGH — WoW ≤ −10% AND DoD < 0
- 🚨 CRITICAL — WoW ≤ −20% AND DoD ≤ −10% OR (D1_bills = 0 AND D8_bills ≥ MIN_BILLS_m AND D8_rev ≥ ZERO_SALE_THRESHOLD_m) — see §10 for per-machine threshold formula

**Color-code each delta cell**: green if Δ ≥ +5%, red if Δ ≤ −5%, neutral grey if |Δ| < 5%.

### Pillar 3 — Spike-Up FYI
Both `(D1−D2)/D2 > +20%` AND `(D1−D8)/D8 > +20%` → FYI task (replicate route / stock pattern).

### ~~Pillar 4 — Discipline (hourly)~~
**Removed** — N/A for unattended machines.

---

## 7. Category Performance Matrix (3×3 Signal Framework)

Per category (across all machines):
- `cat_revenue_D1`, `cat_revenue_D8`
- `cat_bills_D1`, `cat_bills_D8`
- `cat_ticket_D1` = `cat_revenue_D1 / cat_bills_D1`
- `cat_ticket_D8` = `cat_revenue_D8 / cat_bills_D8`
- `Δ_rev%`, `Δ_bills%`, `Δ_ticket%`

### 3×3 Signal Matrix (Vends × Ticket deltas)
Bands: ↑ = ≥+3% · flat = −2% to +2% · ↓ = ≤−3%

| | **Ticket ↑** | **Ticket flat** | **Ticket ↓** |
|---|---|---|---|
| **Vends ↑** | ⭐ **BEST** | 🚶 Traffic-driven | ⚠️ Mixed |
| **Vends flat** | ✅ Pure upsell | ─ Stable | 📉 Quality slip |
| **Vends ↓** | 🤔 Premium mix | ↘ Soft decline | 🚨 **CRISIS** |

### Signal-to-task mapping
| Signal | Task? | Priority | Owner |
|---|---|---|---|
| 🚨 CRISIS | Yes | 🔴 CRITICAL | Category Mgr + Service Team lead |
| 📉 Quality slip | Yes | 🟠 HIGH | Category Mgr |
| ⚠️ Mixed | Optional | 🟠 HIGH | Category Mgr |
| ↘ Soft decline | Monitor only | — | — |
| 🤔 Premium mix | If rev↓ → review | 🟡 DATA | Category Mgr |
| 🚶 Traffic-driven | FYI only | — | — |
| ✅ / ⭐ | Document & share | 🟢 FYI | Category Mgr |

---

## 8. MTD Calculations

```
MTD_TOTAL    = sum(daily_rev) for days where date >= MTD_START AND date <= D1
MTD_DAYS     = day_of_month(D1)
MTD_AVG      = MTD_TOTAL / MTD_DAYS
MTD_BILLS    = sum(daily_bills) for same range
MTD_TICKET   = MTD_TOTAL / MTD_BILLS
D1_VS_MTD    = (D1_revenue − MTD_AVG) / MTD_AVG × 100
```

Show in chart: **single horizontal reference line at `MTD_AVG`**.
Show in KPI card: D1 vs MTD avg delta.

---

## 9. Pre-Resolved Open IDs

| Name | Role | Email | open_id |
|------|------|-------|---------|
| Sarun | **Quality Team** · on-site CCTV / service | sarun@chaw.co.th | `ou_e521461e04d698168412f3c4f9a199d4` |
| Ploynaphat | **Quality Team** | ploynapat@chaw.co.th | `ou_dffd3de6811a4bad31d2f5398dd277b9` |
| Surachai | **Quality Team** | surachai@chaw.co.th | `ou_bde920ede39cc83312cd0dd85ad0473c` |
| Vichit | Universal follower (CC oversight) | vichit@chaw.co.th | `ou_434e5b57a3d9250d73110111104add49` |
| Aekkaphop | Universal follower (Vending oversight) **AND Area Mgr SVB** | aekkaphop@chaw.co.th | `ou_96f0924ec4ff77e0874469cba58c42a5` |
| Siraphop | Area Mgr DMK | siraphop@chaw.co.th | `ou_6b3dcef3a0fbd00d4b27fa828c882915` |

### Quality Team (CRITICAL + HIGH + WATCH task assignees) — same team as SFB
- Sarun · `ou_e521461e04d698168412f3c4f9a199d4`
- Ploynaphat · `ou_dffd3de6811a4bad31d2f5398dd277b9`
- Surachai · `ou_bde920ede39cc83312cd0dd85ad0473c`

All 3 are co-assigned on every CRITICAL/HIGH/WATCH service ticket. Vichit + Aekkaphop are added as followers (per Vending Services universal-follower rule — Tippawan is NOT a follower on Vending tasks; Tippawan is the SFB Sub-12 follower).

### Area Manager Routing
| Airport | Area Manager | open_id |
|---------|---|---|
| SVB | Aekkaphop | `ou_96f0924ec4ff77e0874469cba58c42a5` |
| DMK | Siraphop | `ou_6b3dcef3a0fbd00d4b27fa828c882915` |

> **Note**: Aekkaphop is BOTH the universal follower on every task AND the SVB Area Manager — so any SVB-specific FYI/replication task can be assigned directly to Aekkaphop without an additional follower call. Confirm split with Vichit if Aekkaphop and Siraphop have a different airport ownership.

### Universal Follower Rule (Vending Services / Sub 13)
**Every task** MUST add the following as followers via `lark_add_task_members(role="follower")` after `lark_create_task`:
- **Vichit** · `ou_434e5b57a3d9250d73110111104add49`
- **Aekkaphop** · `ou_96f0924ec4ff77e0874469cba58c42a5`

(Note: this differs from SFB Sub 12 where the follower pair is Tippawan + Vichit.)

---

## 10. Service-Ticket Triggers (per problem machine)

Replaces SFB's critical-hour rules. For each problem machine, evaluate all five triggers and
combine into ONE consolidated service ticket per machine per day.

**Per-machine dynamic benchmarks** (computed from MTD daily totals):
```
mtd_avg_rev_m   = sum(daily_rev[machine])   / mtd_days_present[machine]
mtd_avg_bills_m = sum(daily_bills[machine]) / mtd_days_present[machine]
MIN_BILLS_m            = max(3,    mtd_avg_bills_m × 0.30)
ZERO_SALE_THRESHOLD_m  = max(฿200, mtd_avg_rev_m   × 0.30)
```

**Static thresholds (matched to SFB §5):**
```
DROP_THRESHOLD   = ฿200   # absolute baht floor for a >50% drop to be flagged
SURGE_THRESHOLD  = ฿500   # absolute baht floor for a >50% surge to be flagged
```

| Trigger | Rule | Priority | Description in ticket |
|---|---|---|---|
| **ZERO-SALE DAY** | `D1_bills = 0` AND `D8_bills ≥ MIN_BILLS_m` AND `D8_rev ≥ ZERO_SALE_THRESHOLD_m` | 🚨 CRITICAL | Machine likely offline / unplugged / jammed |
| **MAJOR DROP** | `D1_rev ≤ 0.5 × D8_rev` AND `|D8_rev − D1_rev| ≥ ฿200` | 🟠 HIGH | Partial outage, stockout of hero SKUs, payment terminal fault |
| **STOCKOUT SUSPECT** | `D1_rev < mtd_avg_rev_m × 0.80` for 2+ consecutive days | 🟠 HIGH | Restock route audit needed |
| **MTD NEW LOW** | `D1_rev ≤ mtd_low_m` (and not already covered above) | 🟠 HIGH | Worst day of month — diagnostic visit |
| **SURGE** | `D1_rev ≥ 1.5 × D8_rev` AND `|D1_rev − D8_rev| ≥ ฿500` | 🟢 FYI (no ticket) | Document for restock-frequency tuning |

> **Why per-machine benchmarks for ZERO-SALE / MIN_BILLS**: Vendi kiosks (e.g. 01-T1AE3-09A+B,
> avg ~฿60K/day) and small Vending machines (e.g. T1GW2-08, avg ~฿700/day) differ by 80×.
> A flat ฿200 floor would either flood the queue with tiny-machine false alarms or miss real
> outages at big kiosks. Scaling to each machine's own MTD average normalises both ends.

> **Why static thresholds for DROP / SURGE**: ฿200 / ฿500 are SFB's proven values (runbook §5)
> and align Vending with SFB for cross-report consistency. They act as absolute-magnitude floors
> on top of the %-based 50% / 150% multiplicative rule.

Per-machine consolidation: if a machine fires both ZERO-SALE and STOCKOUT SUSPECT, the ticket
description lists both, but only ONE ticket is created.

---

## 11. Lark Task Creation

### Task title format
`🔧 Service — {machine_id} ({zone}) · {trigger_summary} · {D1_DISPLAY}`

Examples:
- `🔧 Service — VM-BKK-018 (BKK) · Zero-sale day · 26 May 2026`
- `🔧 Service — VM-PROV-104 (PROV) · −62% WoW · 26 May 2026`

### Description template
```
Machine: {machine_id} ({zone}) — {site_name}
D1 total: ฿{d1:,.0f}  ·  D8 baseline: ฿{d8:,.0f}  ·  MTD avg: ฿{mtd_avg:,.0f}
Flag: {sev} · {mtd_flag}

Trigger(s) on this machine ({n_triggers}):
• {trigger_name} — {msg}
...

What to check on-site:
• Machine power + display status (any error code on screen?)
• Cash / cashless payment terminal — print test receipt
• Stock level per shelf — note any SKU at zero
• Coin / note mech jam, bill validator status
• Telemetry / DEX last-sync timestamp
• Surrounding foot traffic (closure, construction, event nearby?)

Deliverable: brief findings + photos, reply on this task by EOD.
If restock needed, log SKUs + qty.

Source: Vending Daily Report v1.0 · {D1_DISPLAY}
```

### Due date
D1 + 1 day at 17:00 ICT.

### Assignees / followers
- Assignees: Sarun + Ploynaphat + Surachai (Quality Team — same as SFB)
- Followers: Vichit + Aekkaphop (always — Vending Services pair)

---

## 12. Email Configuration

| Field | Value |
|-------|-------|
| **To (production)** | `management@chaw.co.th`, `vendi@chaw.co.th` |
| **To (test runs)** | vichit@chaw.co.th only |
| **Subject pattern** | `{emoji} Vending Daily — {D1_DISPLAY} \| ฿{total_k}K (WoW {wow:+.1f}%) \| {n_problem} service tickets` |
| **Format** | HTML with CHAW CI styling |

### Subject status emoji logic
| Condition | Emoji |
|---|---|
| Any CRITICAL flag in §6 Pillar 1 OR Pillar 2 | 🚨 |
| WoW < −5% | ⚠️ |
| WoW ≥ −5% AND ≤ +10% | ✅ |
| WoW > +10% AND no flags | 🔥 |

### CHAW Brand Tokens (unchanged from SFB)
```
Primary (Indigo):      #5551FE
Primary light:         #7B79FF
Accent (Coral):        #F27061
Background (Cream):    #F5EDE4
Cream light:           #FFF8F5
Footer dark:           #2C3E50
Success green:         #2D7A3F
Warning amber:         #F39C12 / #856404
Danger red:            #C5453E / #721C24
Text primary:          #2C3E50
Text secondary:        #5F5E5A
Reference line gray:   #4A5568
Font:                  Poppins, -apple-system, BlinkMacSystemFont, sans-serif
```

### Email Section Order (v1.0 — 10 sections)
| # | Section | Format |
|---|---|---|
| 1 | DRAFT banner (test runs only) | Amber strip |
| 2 | Header (gradient + badge) | Gradient block |
| 3 | 🎯 **Executive Insight** | Coral-bordered box, auto-narrative |
| 4 | 📊 KPI Headline | 3-card grid (Revenue + WoW + DoD + vs MTD · Vends · Avg Ticket) |
| 5 | 📈 30-Day Revenue by Category | Stacked bar + MTD avg line |
| 6 | 🌏 30-Day Revenue by Zone | Stacked bar + MTD avg line |
| 7 | 🏢 Category Performance | **Heatmap matrix**: N category × 3 metric (Revenue Δ / Vends Δ / Ticket Δ), color-graded cells + D1 revenue + signal badge |
| 8 | 🏪 **Sales by Machine** | **Two tables**: ⚠ Problem machines (CRITICAL/HIGH/WATCH/LOW/LOW80, sorted by worst WoW first) + ✅ OK machines (SURGE/POSITIVE/NEUTRAL/NEW, sorted by best WoW first) |
| 9 | 📋 Next Actions | Service-ticket table with URLs + priority colors |
| 10 | Footer (CHAW values + sources) | Dark navy |

> **No Hourly Drill** (vs. SFB §9) — Vending = unattended; anomalies route to service tickets.

### 🔒 Idempotency Check (BEFORE sending)
Search Lark sent-mail for subject containing `[Vending Daily — {D1_DISPLAY}]`.
If found → print `"✅ Already sent for {D1_DISPLAY} — skipping"` and **stop entire routine**.

### Data-quality warning banner
If NS reconciliation flags any issue (new machine, missing day, etc.), insert amber banner under header:
```
⚠ Data quality: {message}. See "Next Actions" for DATA tasks.
```

---

## 13. Chart Implementation Specs

### 13.1 30-Day Stacked Bar — Revenue by Category
HTML table-based (NOT SVG — email-safe). 30 cells, height 240px. Each cell stacks N category
segments (color list TBD — define once category list is known: e.g., Snacks indigo / Drinks
light-indigo / Hot coral / Other amber).

Pixel scale: `PIXEL_PER_BAHT = 220 / MAX_DAILY_TOTAL_30D`. MTD avg line via linear-gradient at
`220 − (MTD_AVG × PIXEL_PER_BAHT)`.

Holiday markers: coral underline on date label for Labor Day, Songkran, NY (vending often spikes
on long weekends because office sites empty out — useful to flag).

D1 highlight: coral inset shadow on rightmost cell.

Legend below: Category · 30-day total · share% · D1 vs avg.

### 13.2 30-Day Stacked Bar — Revenue by Zone
Same template, 3 segments (BKK indigo / PROV light-indigo / MALL coral). Shared
`PIXEL_PER_BAHT` with §13.1 so the two charts are visually comparable.

### 13.3 Category Heatmap (replaces SFB scatterplot)
N rows × 3 columns. Each cell is one of `Δ Revenue`, `Δ Vends`, `Δ Ticket` (WoW).
7-step color gradient dark-green → grey → dark-red. Show the % delta inside the cell.
Append D1 revenue + signal badge (⭐ / 🚨 / 📉 / etc.) on the right.

### 13.4 Sales by Machine table (Problem vs OK split)
**Problem block** — flagged machines, sorted by worst WoW first. Columns: `Machine · Zone · D1 ·
D2 · D8 · DoD% · WoW% · Severity · MTD flag · Service ticket URL`.

**OK block** — everything else, sorted by best WoW first. Same columns, no ticket URL column.

Color-code DoD/WoW cells: green ≥ +5%, red ≤ −5%, grey otherwise.

### ~~13.5 Hourly Drill Table~~
**Removed** in v1.0.

---

## 14. Lark Group Summary

- **Chat ID**: `oc_f25274999f6561e6f1e484102ee198e7` (**Food Operation Core** — same group as SFB Sub 12)
- **Receive ID type**: `chat_id`
- **Message type**: `text`

> Vending Services posts into the same Food Operation Core group as SFB. Subject prefix
> `🥤 Vending Daily Report` keeps it distinguishable from the SFB report (which uses `📊 SFB Daily Report`).

### Template
```
🥤 Vending Daily Report — {D1_WEEKDAY} {D1_DISPLAY}
💰 Total Revenue: ฿{total:,.0f} (WoW {wow:+.1f}% · vs MTD avg {mtd_diff:+.1f}%)
🏆 Top Category: {hero_cat} {hero_wow:+.1f}% WoW · {hero_reason}
🚨 Crisis Categories: {crisis_cat_list_or_"none"}
🔧 Machines flagged: {n_problem}
   • Zero-sale day: {n_zero}
   • Major drop: {n_drop}
   • MTD new low: {n_new_low}
📨 Full report → emailed to management@chaw.co.th + vendi@chaw.co.th

━━━━ Service Tickets ({task_count}) ━━━━
{for each ticket:}
{emoji} {title}
  👤 {owners} | Due {due}
  🔗 {lark_task_url}

CC: @vichit + @aekkaphop (universal followers on all Vending Services tickets)
```

---

## 15. Execution Flow (Imperative — DO NOT DEVIATE)

**Step 0 — Compute dates** (D1, D2, D8, MTD_START, 30D_START)

**Step 1 — Idempotency check**
- Search Lark sent-mail for `[Vending Daily — {D1_DISPLAY}]`
- If found → stop entire routine

**Step 2 — NetSuite responsiveness check**
- `SELECT id FROM transaction WHERE rownum=1` → must return
- Fails → retry once. Still fails → log and stop.

**Step 3 — NS query bundle** (3 SuiteQL queries, in parallel)
- §4.1: D1+D2+D8 per (location, category)
- §4.2: 30-day per (day, category)
- §4.3: 30-day per (day, location)

> Note: only 3 queries, vs. 4 for SFB — no hourly drill query.

**Step 4 — Aggregate**
- Per category (D1, D2, D8) — for heatmap
- Per zone (D1, D2, D8) — for stacked bar
- Per machine (D1, D2, D8) — for §6 Pillar 1 + 2
- Per (Day × Category) — for chart 5
- Per (Day × Zone) — for chart 6
- Compute MTD: total, avg, days_above_avg, per-machine high/low/avg
- Compute `MAX_DAILY_TOTAL_30D` for chart scale

**Step 5 — Apply 3-pillar analysis**
- Pillar 1 machine MTD flags
- Pillar 2 machine DoD×WoW severity
- Pillar 3 spike FYI list
- Apply 3×3 signal matrix per category

**Step 6 — Generate Executive Insight (auto-narrative)**
- Detect dominant pattern: `hero_save` / `broad_decline` / `broad_growth` / `premium_shift` /
  `traffic_surge` / `balanced`
- Find hero_category, crisis_category_list, ticket_anomaly_category
- Compute counterfactual (without hero category)
- Format 4-6 bullets

**Step 7 — Create Lark service tickets**
- For each problem machine: build consolidated trigger list → `lark_create_task(summary, due, description, assignee_ids=[sarun, ploynaphat, surachai])`
- For each task: `lark_add_task_members(task_guid, [vichit_id, aekkaphop_id], role="follower")`
- Capture `task_url` for each (embed in email + group msg)

**Step 8 — Build & send HTML email**
- Determine subject emoji
- Render 10 sections in §12 order
- Embed task URLs in Next Actions
- Insert data-quality banner if needed
- `lark_send_email(to=['management@chaw.co.th','vendi@chaw.co.th'] OR [vichit if test], subject, body)`

**Step 9 — Post Lark group summary**
- `lark_send_message(receive_id=oc_f25274999f6561e6f1e484102ee198e7 (Food Operation Core), msg_type="text", content)`

**Step 10 — Console summary**
```
✅ Vending Daily Report v1.0 — {D1_DISPLAY}
   Total Revenue: ฿{total:,.0f} (WoW {wow:+.1f}%)
   Sub 13 NS-primary: {bills} vends across {n_machines} machines
   MTD avg: ฿{mtd_avg:,.0f} · D1 vs avg: {d1_vs_mtd:+.1f}%
   Flags — P1: {p1}, P2: {p2}, P3: {p3}
   Service tickets created: {task_count}
   📧 Email → {to_list}
   💬 Group → oc_f25274999f6561e6f1e484102ee198e7 (Food Operation Core)
```

---

## 16. Known Issues & Open Questions (v1.0)

| Issue | Status |
|-------|-----|
| **Subsidiary ID unknown** | TODO — call `ns_getSubsidiaries`, find "Vending Services", record ID |
| **Category encoding (class vs department vs item.class)** | TODO — verify with NS admin |
| **Machine master incomplete** | TODO — generate full list via NS location query filtered by subsidiary |
| **Zone naming convention** | TODO — confirm whether to use BKK / PROV / MALL or another scheme |
| **Service Team open_ids** | TODO — Vichit to provide once team confirmed |
| **Recipient emails** | TODO — Vichit to provide |
| **Lark group chat_id** | TODO — Vichit to provide |
| **Holiday calendar reuse** | Decide whether to reuse SFB holiday markers or build a vending-specific calendar (vending may peak on different holidays than airport food) |
| **Telemetry feed** | Future v1.1+ — add DEX / IoT data source for stockout detection |
| **NS posting lag** | Schedule 07:30 ICT (vs. SFB's 07:00) to space NS load |

---

## 17. State Files

| File | Purpose |
|------|---------|
| `machine_master.json` | Canonical machine list (mirrors §3) |
| `mtd_baseline.json` | Daily MTD avg snapshot for back-testing |
| `service_history.json` | Service-ticket history — track if a machine repeatedly fires |

---

## 18. Quick-Start Scheduling Instructions

### Option A — Lark Scheduled Message Trigger (recommended)
Create a Lark workflow that sends `"Run Vending daily report"` to Claude Code at **07:30 ICT** daily.

### Option B — Cron Job
```bash
30 0 * * * /path/to/claude-cli "Run Vending daily report" >> /var/log/vending-daily.log 2>&1
```

### Option C — Back-fill
```
Run Vending daily report for D1=2026-05-20
```

---

## 19. Version History

| Version | Date | Change |
|---------|------|--------|
| **v1.0** | **2026-05-26** | **Initial Vending Services report.** Forked from SFB v2.7. NetSuite-primary architecture for Sub 13. **Removed**: Section 9 Hourly Drill + CCTV task workflow (vending = unattended, no CCTV). **Replaced** with §10 service-ticket flow keyed on machine-level zero-sale / major-drop / STOCKOUT / MTD-low triggers, assigned to the Quality Team. Email shrinks to 10 sections (vs. SFB's 11). Kept SFB's heatmap matrix, Problem/OK split, Executive Insight, and 30-day stacked bars. Placeholders flagged with `«TBD_…»` markers throughout — search for `«TBD_` to find them all. |
