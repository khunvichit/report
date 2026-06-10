# Juiceland Report — PREDICTION (method)

The logic for the **🔮 AI Estimate** section at the top of the report. This file defines *how* the
forecast, commentary, and anomaly summary are produced — NOT the data (see `juiceland-queries.md`)
and NOT the layout (see the prediction section in `juiceland-template.html`).

> CORE RULE: this section is **inferential**, unlike the rest of the report which is deterministic.
> It is computed LAST (after all actuals are known) but DISPLAYED FIRST. It must never assert a
> cause the data doesn't support, and every number carries a range, not a bare point estimate.

---

## Inputs (reuse existing queries — add only if noted)

- Query A (30-day daily net per branch) — primary basis for forecast + commentary.
- New-product (Query C), dormant (Query D), seasonal (Query E) — feed the anomaly summary.
- **Optional added query** for forecast only: same-weekday history beyond 30 days
  (e.g. last 8 occurrences of this weekday per branch) if 30 days proves too short for stable bands.
  Add to `juiceland-queries.md` as Query F if adopted; until then use the 30-day window.

---

## Part 1 — FORECAST (today's expected sales)

Method (deterministic basis, stated so it's auditable — not a black box):
```
For each branch:
  base      = average net_sales of the SAME WEEKDAY over the trailing 4 weeks
  trend_adj = blend base with the 7-day average (weight 0.5/0.5) to catch recent drift
  forecast  = trend_adj
  band      = ± (stdev of those same-weekday values, min ±8%)   → low / high range
Combined forecast = sum of branch forecasts; band = combined stdev.
```

Guardrails:
- **Always a range, never a single number.** Display `฿{low}–฿{high}`, with the midpoint optional.
- **Bound it:** if forecast > ±35% from the 30-day average, cap at the bound and mark `wide variance`.
- **Confidence flag:**
  - 🟢 High — same-weekday stdev < 12% of mean
  - 🟡 Medium — 12–25%
  - 🔴 Low — > 25%, OR fewer than 3 valid same-weekday data points → **suppress the number**, show
    "insufficient history for a reliable estimate" instead of a figure.
- Forecast is for the **current day** (the day the report is sent), i.e. the day AFTER report_date.

## Part 2 — COMMENTARY (on yesterday's actuals)

Method: 2–4 short sentences describing what the actuals show, grounded ONLY in the computed figures.

Guardrails — the most important rules in this file:
- **Describe, do not diagnose.** State movements ("PKT net was ฿X, down 18% vs its 30-day average"),
  never invent causes ("because of fewer flights / weather / staffing") unless that cause is itself
  a data point in the report.
- **Only cite numbers that exist in this report.** No figures from memory or outside the queries.
- **No superlatives without basis.** "Best day this month" only if the 30-day data confirms it.
- **Neutral tone.** No reassurance, no alarm — just what changed and by how much.
- If nothing notable moved, say so plainly ("All three branches within normal range vs 30-day average.")

## Part 3 — ANOMALY SUMMARY (what to watch, top-of-report)

Method: surface the highest-priority items already computed elsewhere, as a short bullet list.
- Pull from existing logic: AM-review queue (stock-out suspects + waste-risk), dormant SKUs,
  any branch > ±25% vs its 30-day average, seasonal coverage < 70%.
- Rank by materiality (฿ impact, then recency). Show top 3–5 only; link "see sections below" for detail.
- This is a *pointer*, not a re-listing — the detailed sections (AM banner, dormant, seasonal) still own the full data.

---

## Labeling & placement (because this sits FIRST)

- Section header MUST read as an estimate, e.g. `🔮 AI Estimate — forecast & read · see actuals below`.
- Forecast numbers always show range + confidence colour.
- Compute order: run AFTER Steps 2–3 (queries + KPIs) so commentary/anomaly are grounded in real figures.
  Render this block at the TOP of the HTML body regardless of compute order.
- If data completeness checks failed upstream, DO NOT generate a prediction — the run should have
  already stopped. Never forecast on incomplete data.

## Validation note

Because this section is generative and high-visibility (top of a management email), run it in
`manual-test` mode (email to Vichit only) for ~1–2 weeks. Check specifically: forecast ranges are
plausible, confidence flags behave, and commentary NEVER states an unsupported cause. Promote to the
full recipient list only after it holds up.
