# SFB Daily — Commentary & Classification METHOD (generative layer)

This file holds the REASONING rules for the Executive Insight bullets, branch severity, MTD overlay
flags, and the BU heatmap signal. These vary run-to-run, so they live apart from the deterministic
queries. **Describe what the data shows; never invent a cause not present in the data.** Compute these
AFTER actuals are in; they display at the top of the email.

## A. Branch severity (6-tier) — from D1, D2, D8

```
dod = (d1-d2)/d2 ; wow = (d1-d8)/d8   (0 if denominator 0)
wow>=+15% AND dod>=+10%   -> 🔥 SURGE     sev-surge
wow>=0                    -> ✅ POSITIVE  sev-positive
wow>-5%                   -> ─ NEUTRAL    sev-neutral
wow<=-20% AND dod<=-10%   -> 🚨 CRITICAL  sev-critical
wow<=-10% AND dod<0       -> 🟠 HIGH      sev-high
wow<=-5%                  -> ⚠ WATCH      sev-watch
else                     -> ─ NEUTRAL    sev-neutral
```

## B. MTD overlay flags (extra badges, vs branch's own MTD stats from Q3)

- D1 ≤ branch MTD low  → 🚨 NEW LOW
- D1 ≥ branch MTD high → 🔥 NEW HIGH
- D1 < branch MTD avg × 0.80 → `<80% avg`
- < 3 days of MTD history → 🆕 NEW LOCATION

## C. Problem vs OK split (classification only — no branch table / hourly / surge section for now)

`problem = severity in {CRITICAL, HIGH, WATCH} OR mtd_flag in {NEW LOW, <80% avg}`.
The branch tables, Hourly Drill, and the Replicate—SURGE section are all currently REMOVED from the
email. Severity is still computed because the SURGE/POSITIVE/etc. tiers feed (a) the location×BU
heatmap signal, (b) the subject-line problem count + exec insight, and (c) the ranking of top/weakest
movers in the Lark group message. No per-branch table, hourly block, or surge table is rendered.

## D. Location×BU heatmap — grouping, signal, and continuous color gradient

One row per LOCATION × BU pair (Q1 already groups this way), so a multi-BU site like 26-T1MW1-03+04
or 27-T1SE3-05 appears as one line per BU it hosts.

### Grouping & ordering
- Group all rows of the same location together. Order the GROUPS by the location's total D1 revenue,
  highest first. Within a group, order BUs by their own D1 revenue desc.
- Merge the Location cell across its group via rowspan. Build the `loc_cell` token per row:
  - First row of a group: `loc_cell = '<td class="heat-bu" rowspan="{N}"><b>{location}</b></td>'`
    where N = number of BU rows in that location, and set `row_class = "grp-start"` (draws the indigo
    divider above the group).
  - Other rows of the group: `loc_cell = ''` (empty — the merged cell spans down) and `row_class = ""`.

### Signal (3×3, bands at ±3% on Bills × Ticket WoW) — computed per location×BU
|              | Ticket ↑        | Ticket flat       | Ticket ↓          |
|--------------|-----------------|-------------------|-------------------|
| **Bills ↑**  | ⭐ BEST          | 🚶 Traffic-driven | ⚠️ Mixed          |
| **Bills flat**| ✅ Pure upsell   | ─ Stable          | 📉 Quality slip   |
| **Bills ↓**  | 🤔 Premium mix   | ↘ Soft decline    | 🚨 CRISIS         |

### Continuous color gradient (replaces the old 7-step bands)
Each Δ cell (rev / bills / ticket WoW) gets a smoothly interpolated background. Clamp the pct to
[−25, +25], then interpolate in RGB between three anchors:
```
RED  #C5453E (-25%)  →  GREY #F0E5DA (0%)  →  GREEN #1E6B30 (+25%)
def grad(pct):
    p = max(-25.0, min(25.0, pct))
    if p >= 0:
        t = p/25.0
        bg = lerp((240,229,218), (30,107,48), t)     # grey → green
    else:
        t = -p/25.0
        bg = lerp((240,229,218), (197,69,62), t)      # grey → red
    fg = '#ffffff' if abs(p) >= 13 else '#2C3E50'     # white text on saturated cells
    return rgb_to_hex(bg), fg
# lerp(a,b,t) = tuple(round(a_i + (b_i-a_i)*t) for each channel)
```
Apply `grad()` to rev_delta → (rev_bg, rev_fg), bills_delta → (bills_bg, bills_fg),
ticket_delta → (ticket_bg, ticket_fg). Zero/flat lands on the cream-grey midpoint, so the eye reads
intensity = magnitude and hue = direction.

## E. Executive Insight — 4–6 bullets (describe, don't diagnose)

Detect the dominant pattern, then write bullets:
- `hero_save`: 1 BU >+20% WoW masks broad decline · `broad_decline`: 3+ BUs down · `broad_growth`:
  3+ BUs up · `premium_shift`: total bills↓ ticket↑ · `traffic_surge`: bills↑ ticket flat · else `balanced`.

Always include: (1) D1 revenue + WoW% + DoD% + vs-MTD-avg% + bills + avg ticket;
(2) the dominant-pattern sentence; (3) hero BU + its WoW/bills/ticket; (4) the most material MTD-flag
branch (e.g. NEW LOW); (5) top-3 location×BU movers by rev WoW; (6) weakest-3 location×BU by rev WoW.
Movers (5)+(6) use the same location×BU rows as the heatmap so the email stays self-consistent — there
is no branch table, hourly drill, or problem-branch count in this build, so do NOT cite branch-level
detail the email doesn't show (e.g. avoid "monitor at location level" / "see Hourly Drill").
State facts only — e.g. "23-T1CE4-13 hit NEW MTD LOW", not a guessed reason.

## F. Guardrails

- No causal claims ("because the flight schedule changed") unless that data is in-hand.
- This report has no numeric forecast section; if one is added later, make it a RANGE with a
  confidence flag and suppress when same-weekday history < 3 points.
