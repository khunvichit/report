# vending-prediction.md — Executive Insight method + guardrails

The Vending Daily report has **no forward forecast** in v1.0 — the only generative section is the
🎯 Executive Insight bullet list at the top of the email. This file defines exactly how those
bullets are computed so the routine produces consistent narrative day-to-day.

**Compute LAST, display FIRST**: the insight bullets are written *after* all numbers, severities,
and ranks are known, then placed in the email's top section.

---

## Inputs (already in scope after queries + classification)

- `total_rev_d1`, `total_rev_d2`, `total_rev_d8` — full-Sub totals (excl General class + HQ).
- `bu_rev_d1[bu]`, `bu_rev_d8[bu]`, `bu_bills_d1[bu]`, `bu_bills_d8[bu]`, `bu_ticket_d1[bu]`, `bu_ticket_d8[bu]`
- `airport_rev_d1[airport]`, `airport_rev_d8[airport]`
- `machine_severity[machine]` — one of `CRITICAL / HIGH / WATCH / NEUTRAL / POSITIVE / SURGE / NEW`
- `machine_mtd_flag[machine]` — one of `🔥 NEW HIGH / 🚨 NEW LOW / 🚨 <80% avg / ✅ above avg / ⚠ below avg`
- `problem_count` — count of machines flagged as Problem
- `top_machine_by_wow` — highest WoW% machine on D1
- `worst_machine_by_wow` — lowest WoW% machine on D1
- `mtd_avg_total` — MTD daily average total revenue

---

## Bullet generation rules

Produce **4–6 bullets**. Order them as below; only emit a bullet if its rule fires.

### Bullet 1 — Headline (ALWAYS)
```
D1 Vending revenue ฿{total_rev_d1} ({wow_signed}% WoW · {dod_signed}% DoD · vs MTD avg ฿{mtd_avg_k}K {mtd_vs_signed}%),
{total_bills_d1} vends, avg ticket ฿{avg_ticket} — {tone_phrase}.
```
- `tone_phrase` rule:
  - `wow_pct >= +10` → "strong day, above month pace"
  - `+5 <= wow_pct < +10` → "solid day"
  - `-5 < wow_pct < +5` → "in line with last week"
  - `-10 < wow_pct <= -5` → "soft day, watch the trend"
  - `wow_pct <= -10` → "weak day, multiple machines flagged"

### Bullet 2 — BU split story (ALWAYS)
- If one BU is positive and the other negative → call it out as a split story:
  ```
  Split story: {positive_bu} up {x}% WoW (...) · {negative_bu} down {y}% WoW (...). {dominant_bu_share}% of mix from {dominant_bu}.
  ```
- If both same direction → describe the move uniformly:
  ```
  Both BUs {direction}: Vendi {x}% / Vending {y}% WoW. {dominant_signal}.
  ```

### Bullet 3 — BU CRISIS or BU BEST (only one fires, prefer CRISIS)
- If any BU has signal `🚨 CRISIS` per 3×3 matrix → emit a CRISIS bullet pointing to the heatmap:
  ```
  🚨 {bu} BU in CRISIS — Revenue {Δrev}%, Vends {Δbills}%, Ticket {Δticket}%. {likely_cause_hint}.
  ```
  `likely_cause_hint` for Vending: "Likely machine outages on a route." For Vendi: "Possible staffing or merchandise gap."
- Else if any BU has signal `⭐ BEST` → emit a positive bullet:
  ```
  ⭐ {bu} BU leading: WoW {x}% (Bills {y}% · Ticket {z}%).
  ```

### Bullet 4 — Worst machine callout (only if `worst_machine.wow_pct <= -10`)
```
🟠 Worst: {machine_id} ({bu} · {airport}) D1 ฿{d1} vs D8 ฿{d8} — {wow_signed}% WoW, {d1_bills} vends vs {d8_bills} baseline. {plausible_cause}.
```
- `plausible_cause`:
  - Vending BU + `d1_bills == 0` → "Likely machine offline."
  - Vending BU + `d1_bills > 0` → "Likely machine fault or stockout."
  - Vendi BU → "Investigate kiosk operations / staffing."

### Bullet 5 — Hero machine callout (only if `top_machine.wow_pct >= +15`)
```
🔥 Hero: {machine_id} ({bu} · {airport}) D1 ฿{d1} · WoW {wow_signed}% · DoD {dod_signed}% — {hero_phrase}.
```
- `hero_phrase`:
  - If `machine_mtd_flag == '🔥 NEW HIGH'` → "biggest single-day at any {bu} location this month."
  - Else → "strongest mover on D1."

### Bullet 6 — Airport split (only if airport WoW deltas differ by ≥ 5 pts)
```
{leading_airport} {wow_leading}% WoW {direction} {trailing_airport} ({wow_trailing}%). {airport_context}.
```
- `airport_context`:
  - If DMK ahead → "DMK piers ({dmk_loc_list}) running ahead this week."
  - If SVB ahead → "SVB Terminal 1 carrying the rebound."

### Bullet 7 — Problem-count summary (ALWAYS if `problem_count > 0`)
```
{problem_count} machine{s_or_blank} flagged — see Sales by Machine + Next Actions for service queue.
```

---

## Anti-hallucination guardrails

1. **Only assert what's in the data.** Never invent causes that aren't tied to a concrete row.
   "Suspect freezer outage" is OK if a Frozen-category WoW drop fired. "Customer satisfaction issues"
   is NOT OK — we have no CSAT data.
2. **No forward predictions.** v1.0 has no forecast section. Do not write "expect to rebound
   tomorrow" or similar.
3. **Use machine codes from the data, not invented codes.** If `01-T1AE3-09A+B` is the top mover,
   use that exact string — don't paraphrase as "the big BKK kiosk".
4. **AI estimate flag**: not applicable in v1.0 (no model-projected numbers in the email).
5. **Suppress thin baselines.** Skip a "machine X dropped Y%" bullet if D8 was < ฿200 (matches the
   `DROP_THRESHOLD`); the percentage is meaningless on tiny baselines.

---

## Output

The model computes a small `scalars` dict for the insight bullets and a `repeats.insight_bullets`
list of `{html: "..."}` items. The template wraps `<!-- REPEAT:insight_bullets -->...<!-- /REPEAT --> `
to render whichever bullets fire. The order above is preserved by appending to the list in that
order; non-firing rules simply don't append.

```json
"repeats": {
  "insight_bullets": [
    { "html": "<li>D1 Vending revenue <b>฿354,580</b> (+11.4% WoW ... — strong day, above month pace.</li>" },
    { "html": "<li><b>Split story</b>: Vendi up 15.2% WoW ...</li>" },
    ...
  ]
}
```
