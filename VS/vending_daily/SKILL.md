---
name: vendingdailysalesreportoverview
description: Generate the Vending Services Daily Sales Report (Sub 13, Vending Services Company Limited) — pulls NetSuite sales data for yesterday (D1), computes DoD/WoW/MTD comparisons, identifies problem machines, builds the v1.0 HTML email with 10 sections (Executive Insight, KPI, 30-Day BU/Airport stacked bars with MTD avg line, BU heatmap, Sales by Machine Problem vs OK split, Next Actions), creates Lark service tickets for the Quality Team (Sarun + Ploynaphat + Surachai · same team as SFB), sends to management@chaw.co.th + vendi@chaw.co.th, posts group summary to Food Operation Core Lark chat. MANDATORY TRIGGERS: "Run Vending daily report", "Vending Services daily", "vending sales yesterday", "daily vending report", "ยอดขายตู้เมื่อวาน", "รายงานขายตู้", "create Vending report", "send daily vending report to management", "draft daily vending sales email", "make me draft email for yesterday's vending sale", "vending daily report v1.0", or any request to produce/send the Vending Services daily sales summary for management/operations. Also trigger when staff asks for "yesterday's vending sales" with no other context — they almost always mean this report. NEVER trigger for non-Vending or non-daily contexts (use the SFB skill for Sub 12 Food Operations instead).
---

# Vending Services Daily Sales Report — `vendingdailysalesreportoverview`

Generates the production daily sales report for **Sub 13 / Vending Services**. NetSuite-primary architecture. Adapted from the SFB Food Operations Core v2.7 skill, with the **hourly drill + CCTV task workflow removed** (vending machines are unattended assets — anomalies become service/restock tickets, not CCTV reviews). Current version: **v1.0**.

> **🚧 PLACEHOLDER NOTICE** — Anything wrapped in «TBD_…» is a deliberate placeholder. Fill these in before going live:
> - 13 — NetSuite subsidiary internal ID for Vending Services
> - ~~«TBD_TO_RECIPIENTS»~~ — resolved: **management@chaw.co.th, vendi@chaw.co.th**
> - ~~«TBD_LARK_GROUP»~~ — resolved: **Food Operation Core** (`oc_f25274999f6561e6f1e484102ee198e7`) — shared with SFB Sub 12
> - ~~«TBD_SERVICE_TEAM_*»~~ — resolved: **Quality Team (Sarun + Ploynaphat + Surachai)** — same team as SFB
> - ~~«TBD_AREA_MGR_*»~~ — resolved: **Aekkaphop (SVB)** + **Siraphop (DMK)**
> - ~~«TBD_MACHINE_MASTER»~~ — resolved: see §8 (23 active + 1 pop-up + 1 admin · verified against NS 2026-05-26)

---

## TL;DR

When the user asks for "yesterday's vending sales", "Vending daily", or any equivalent:

1. Compute dates (Asia/Bangkok)
2. Run 3 NS queries (D1/D2/D8 per machine × category · 30-day category · 30-day zone)
3. Identify problem machines
4. Build the 8-section HTML email (template in §3)
5. Create one Lark service ticket per problem machine (Quality Team assignees — Sarun + Ploynaphat + Surachai, same as SFB; followers Vichit + Aekkaphop)
6. Send email to production recipients
7. Post text summary to Vending Operations chat

The full step-by-step lives in `runbook.md` next to this file. Always read that before executing.

---

## 1. Date parameters

```
D1        = today(Asia/Bangkok) − 1 day        # yesterday — report date
D2        = D1 − 1 day                         # DoD baseline
D8        = D1 − 7 days                        # WoW baseline (same weekday)
MTD_START = first day of D1's calendar month
30D_START = D1 − 29 days
```

NEVER use server UTC. Always `now(Asia/Bangkok).date() − 1 day`.

---

## 2. Data sources

**Primary: NetSuite (Sub 13)** — covers ALL vending product categories. Use `tl.subsidiary = 13`, `t.type IN ('CustInvc','CustCred')`, `tl.mainline='F'`, `tl.taxline='F'`, `tl.item IS NOT NULL`, `tl.account IS NOT NULL`. Revenue = `SUM(-tl.netamount)` (pre-VAT). Bills = `COUNT(DISTINCT t.id WHERE type='CustInvc')` (vend events / receipts, not line items).

**No hourly drill in v1.0**: Vending machines are unattended, so the hour-by-hour CCTV forensic pattern from SFB doesn't apply. Machine-level anomalies (zero-sale days, abrupt WoW drops) become **service tickets** for the Quality Team to inspect the unit, restock, or troubleshoot telemetry.

**Optional secondary (future)**: vending telemetry / DEX data, if available, can be plugged in for stockout detection (TBD — not in v1.0 scope).

Architecture rationale (why NS not POS as primary): mirrors SFB v2.0 reasoning — NS is the financial system of record, contains all records natively, and counts receipts so Avg Ticket is meaningful.

---

## 3. Email structure — 8 sections (v1.0)

| # | Section | Format |
|---|---|---|
| 1 | DRAFT/PROD banner | Coral or green strip with mode label |
| 2 | Header | Gradient indigo with title + date + status emoji badge |
| 3 | 🎯 Executive Insight | Coral-bordered box, auto-narrative bullets (D1 total, hero category, problem callouts, MTD comparison) |
| 4 | 📊 KPI Headline | 3 cards: Revenue (WoW+DoD+vs MTD), Vends (WoW), Avg Ticket (WoW) |
| 5 | 📈 30-Day Revenue by BU | Stacked bar chart (Vendi indigo + Vending light-indigo) + MTD avg line + holiday markers + D1 highlight |
| 6 | 🌏 30-Day Revenue by Airport | Stacked bar (SVB indigo + DMK light-indigo) shared `PIXEL_PER_BAHT` scale with §5 |
| 7 | 🏢 Category Performance | **Heatmap matrix** N category × 3 metric (Revenue Δ / Vends Δ / Ticket Δ WoW). 7-step color scale dark-green → grey → dark-red. INCLUDES sub-header explaining Vends vs Avg Ticket vs Revenue. |
| 8 | 🏪 Sales by Machine | **Two-table split**: ⚠ Problem machines (worst WoW first) + ✅ OK machines (best WoW first). Per-row: D1/D2/D8/DoD/WoW/Severity + MTD flag badge. |
| 9 | 📋 Next Actions | Table with priority + task + owner + due + Lark task URL. Only CRITICAL+HIGH+LOW+LOW80 become real tasks. FYI shown but no task. |
| 10 | Footer | Source citations + runbook version |

> **No Section 9 Hourly Drill** (intentionally removed vs. SFB v2.7). The Next Actions section directly references service tickets created for problem machines.

### Subject pattern
`{emoji} Vending Daily — {D1_DISPLAY} | ฿{total_k}K (WoW {wow:+.1f}%) | {n_problem} service tickets`

Emoji rules:
- 🚨 = any CRITICAL severity in §8 OR ≥2 NEW LOW
- ⚠️ = WoW < −5%
- ✅ = WoW ≥ −5% AND ≤ +10%
- 🔥 = WoW > +10% AND no critical flags

---

## 4. Severity classifications

### Per-machine severity (§8)
- 🚨 CRITICAL — WoW ≤ −20% AND DoD ≤ −10% (or zero-sale day AND D8 ≥ ZERO_SALE_THRESHOLD_m · see §5)
- 🟠 HIGH — WoW ≤ −10% AND DoD < 0
- ⚠ WATCH — WoW ≤ −5%
- ─ NEUTRAL — WoW < 0 and > −5%
- ✅ POSITIVE — WoW ≥ 0
- 🔥 SURGE — WoW ≥ +15% AND DoD ≥ +10%
- 🆕 NEW — no D8 history

### Per-machine MTD flag
- 🔥 NEW HIGH — D1 ≥ mtd_high
- 🚨 NEW LOW — D1 ≤ mtd_low
- 🚨 <80% avg — D1 < mtd_avg × 0.80
- ✅ above avg — D1 ≥ mtd_avg
- ⚠ below avg — otherwise

### Problem machine definition (for service ticket creation)
`severity ∈ {CRITICAL, HIGH, WATCH}` OR `mtd_flag ∈ {NEW LOW, <80% avg}` OR `D1_bills = 0 AND D8_bills ≥ MIN_BILLS_m` (per-machine MTD baseline, see §5).

### Category performance signal (3×3 from Vends × Ticket WoW)
Bands: ↑ ≥+3% · · −3% to +3% · ↓ ≤−3%

|   | Ticket ↑ | Ticket · | Ticket ↓ |
|---|---|---|---|
| Vends ↑ | ⭐ BEST | 🚶 Traffic-driven | ⚠️ Mixed |
| Vends · | ✅ Pure upsell | ─ Stable | 📉 Quality slip |
| Vends ↓ | 🤔 Premium mix | ↘ Soft decline | 🚨 CRISIS |

---

## 5. Service-ticket triggers (replaces SFB §5 Critical-hour rules)

For each machine flagged as a problem (definition above), create ONE service ticket describing what needs to be inspected on-site.

**Per-machine dynamic benchmarks** (from MTD daily totals — auto-computed):
- `MIN_BILLS_m = max(3, mtd_avg_bills_m × 0.30)`
- `ZERO_SALE_THRESHOLD_m = max(฿200, mtd_avg_rev_m × 0.30)`

**Static thresholds (= SFB §5 values):**
- `DROP_THRESHOLD = ฿200`
- `SURGE_THRESHOLD = ฿500`

| Trigger | Rule | Priority |
|---|---|---|
| **ZERO-SALE DAY** | `D1_bills = 0` AND `D8_bills ≥ MIN_BILLS_m` AND `D8_rev ≥ ZERO_SALE_THRESHOLD_m` | 🚨 CRITICAL |
| **MAJOR DROP** | `D1_rev ≤ 0.5 × D8_rev` AND `|D8_rev − D1_rev| ≥ ฿200` | 🟠 HIGH |
| **STOCKOUT SUSPECT** | `D1_rev < mtd_avg_rev_m × 0.80` for 2+ consecutive days | 🟠 HIGH |
| **MTD NEW LOW** | `D1_rev ≤ mtd_low_m` | 🟠 HIGH |
| **SURGE** (FYI) | `D1_rev ≥ 1.5 × D8_rev` AND `|D1_rev − D8_rev| ≥ ฿500` | 🟢 FYI |

Per-machine service ticket consolidates all applicable triggers into one ticket (one machine = one ticket per day). Full rationale: see `runbook.md` §10.

---

## 6. Lark task creation rules

### Recipients
- **Co-assignees (every service ticket)**: Sarun · Ploynaphat · Surachai (**Quality Team — same team as SFB**)
- **Followers (every service ticket)**: Vichit + Aekkaphop
- **Due**: D1 + 1 day at 17:00 ICT (i.e., next-business-day EOD)

### Open IDs (memorized)
| Name | Role | open_id |
|---|---|---|
| Sarun | **Quality Team** · on-site CCTV / service | `ou_e521461e04d698168412f3c4f9a199d4` |
| Ploynaphat | **Quality Team** | `ou_dffd3de6811a4bad31d2f5398dd277b9` |
| Surachai | **Quality Team** | `ou_bde920ede39cc83312cd0dd85ad0473c` |
| Vichit | Universal follower (CC oversight) | `ou_434e5b57a3d9250d73110111104add49` |
| Aekkaphop | Universal follower + **Area Mgr SVB** | `ou_96f0924ec4ff77e0874469cba58c42a5` |
| Siraphop | **Area Mgr DMK** | `ou_6b3dcef3a0fbd00d4b27fa828c882915` |

### Task title format
`🔧 Service — {machine_id} ({zone}) · {trigger_summary} · {D1_DISPLAY}`

Examples:
- `🔧 Service — VM-018 (BKK-Centralwd) · Zero-sale day (D8 ฿3.2K) · 26 May 2026`
- `🔧 Service — VM-104 (PROV-NKR) · −62% WoW · 26 May 2026`

### Task description template
```
Machine: {machine_id} ({zone}) — {site_name}
D1 total: ฿{d1:,.0f}  ·  D8 baseline: ฿{d8:,.0f}  ·  MTD avg: ฿{mtd_avg:,.0f}
Flag: {sev} · {mtd_flag}

Trigger(s) on this machine ({n_triggers}):
• {ZERO-SALE|MAJOR DROP|STOCKOUT SUSPECT|MTD NEW LOW} — {msg}
...

What to check on-site:
• Machine power + display status (any error code on screen?)
• Cash / cashless payment terminal — print test receipt
• Stock level per shelf — note any SKU at zero
• Coin / note mech jam, bill validator status
• Telemetry / DEX last-sync timestamp
• Surrounding foot traffic (closure, construction, event nearby?)

Deliverable: brief findings + photos, reply on this task by EOD. If restock needed, log SKUs + qty.

Source: Vending Daily Report v1.0 · {D1_DISPLAY}
```

### After creation
For each task call `lark_add_task_members(task_guid, [Vichit_id, Aekkaphop_id], role="follower")`.

### NOT a service ticket (display in email only)
- Category-level CRISIS across all machines — product/route strategy issue, escalate to Category Manager instead
- 🔥 SURGE / NEW HIGH machines — FYI only, document for restock-frequency tuning
- 🆕 NEW machine (just deployed) — DATA task for Vichit to update machine master, NOT a service ticket

---

## 7. Recipients

### Production
- **Email To**: `management@chaw.co.th`, `vendi@chaw.co.th`
- **Email CC**: none
- **Lark group**: `oc_f25274999f6561e6f1e484102ee198e7` (Food Operation Core — shared with SFB)

### Test
- **Email To**: `vichit@chaw.co.th` only
- **No group post, no real task creation** (dry-run task list shown in email body only)

---

## 8. Machine master (v1.0) — verified 2026-05-26

23 active sales locations + 1 pop-up + 1 admin. Full details in `runbook.md` §3.

### SVB — Suvarnabhumi T1 (17 locations · 88.6% of D1 revenue)
**Vendi kiosks (BU=Vendi · class 104):** 01-T1AE3-09A+B · 02-T1AE3-06+07 · 03-T1BE3-03+04 · 04-T1CE3-01+02 · 05-T1DE3-01+02 · 06-T1DW3-02+03 · 07-T1EW3-01+02 · 08-T1ME4-13+14 · 10-T1BE1-02
**Vending machines (BU=Vending · class 14):** T1AE3-05 · T1BE1-01 · T1BE3-02 · T1CE3-03 · T1FW3-02 · T1GW2-08 · T1GW4-05 · T1MW4-14¹ · T1MW4-18¹ · T1MW4-19¹

¹ Silent on recent D1/D2/D8 — DATA task open to verify.

### DMK — Don Mueang (3 locations · 11.4% of D1 revenue)
**Vendi kiosks:** 09-321+322
**Vending machines:** 05-317 · 05-318

### Pop-up / Event
- **Crucible Event** (Vendi · loc 450) — BKK pop-up, no current sales. Same physical event SFB Sub 12 tracks for Juice Land.

### Admin (excluded from sales analytics)
- **Vending HQ** (loc 79) — General class adjustments + credit memos only.

### Airport derivation (verified)
```python
def airport_of(loc_name):
    if loc_name == 'Crucible Event': return 'BKK'
    if loc_name == 'Vending HQ':     return 'HQ'
    if 'T1' in loc_name:             return 'SVB'
    if loc_name.startswith(('05-', '09-')): return 'DMK'
    return 'SVB'
```

### NetSuite filter
Add to every Section 4 query:
```sql
AND c.name IN ('Vendi','Vending')   -- exclude General class
AND l.name != 'Vending HQ'           -- exclude admin location
```

---

## 9. Execution mandate

When invoked, **do not ask for confirmation between steps**. Run Sections 1–12 from `runbook.md` sequentially. Only stop if:
- (a) NetSuite API returns hard error after retry
- (b) Idempotency check finds a prior email for the same D1 already sent

Default to **TEST mode** if the user hasn't explicitly said "production" or "send to management". Test mode = vichit@chaw.co.th only, no real task creation, no group post.

---

## 10. Trigger phrases (any of these → invoke this skill)

- "Run Vending daily report" / "Vending daily"
- "Create me draft email for yesterday's vending sale" / "draft daily vending sales email"
- "Yesterday's vending sales" / "ยอดขายตู้เมื่อวาน"
- "Vending daily report for D1=YYYY-MM-DD" (back-fill mode)
- "Send vending daily report to management"
- "รายงานขายตู้" / "Vending Services ยอดขายวันนี้/เมื่อวาน"

For back-fill, use the date the user specified as D1 instead of `today − 1`.

---

## 11. Reference files

- `runbook.md` — full v1.0 runbook (next to this file). Always read before executing — it has the exact SuiteQL queries, chart implementation specs, MTD calculations, and all edge cases.

---

## 12. Version history

| Version | Key change |
|---|---|
| **v1.0** | **Initial Vending Services report.** Forked from SFB v2.7. NetSuite-primary architecture for Sub 13. Removed hourly drill section + CCTV task workflow (vending = unattended, no CCTV). Replaced with service-ticket flow keyed on machine-level zero-sale / major-drop / MTD-low triggers, assigned to Quality Team. Email shrinks to 8 content sections (vs. SFB's 11). Same heatmap matrix, Problem/OK split, Executive Insight, and 30-day stacked bars as SFB. |
