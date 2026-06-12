# ActionCity — Prediction / Commentary / Anomaly method (generative layer)

Generative, NOT deterministic. Runs AFTER all actuals are computed; fills `insight_rows[]` and the
rule-based flag/colour tokens. Keep separate from queries so the deterministic numbers are never
re-reasoned. Everything here must be traceable to a number already in `data.json`.

## Executive Insight — `insight_rows[]` (3–6 bullets, top of email)

Method: describe what the data shows; **never invent a cause not present in the data**. Each bullet
ties to a computed figure. Order by materiality. Suggested template (include a bullet only if its
trigger fires):

1. **Headline** — always: today's net `฿{day_net}` ({day_wow_pct} vs same day last week); WTD `฿{wtd_net}` over {wtd_days} days. State plainly whether the day is above/below the same-weekday norm.
2. **Mix driver** — the BU with the biggest WoW swing: e.g. "Retails {bu_wow}; online offsetting — Shopee {..}, Vending {..}." Use only BU rows present.
3. **Branch leader / laggard** — top branch by net and any branch with WoW < −10%.
4. **DARK branch alert** — if any branch has the DARK flag (wtd=0 & prev>0): "⚠ <branch> recorded zero sales — check store status / POS feed." High priority, place near top.
5. **Reorder** — name the tightest-cover reorder row (cover < 0.7).
6. **Dead-stock** — the largest return opportunity (Big Box consignment value) + owned-to-clear total.

Guardrails:
- Describe-don't-diagnose. "Central Ladprao −13%" ✓. "Central Ladprao down because of weather" ✗ (not in data).
- No invented promotions, holidays, or competitor effects.
- Returns/credits: if a week's net is depressed by a large return, say "net reduced by ฿X of returns booked" only if the credits figure was queried; otherwise omit.
- Label the block as an AI summary (template already says "AI summary of the numbers below").

## Forecast (optional, off by default)

If a same-weekday forecast is wanted later: basis = trailing 4 same-weekday net, show as a RANGE
(min–max of the 4) with a confidence flag; suppress when fewer than 3 same-weekdays of history.
Always label "AI estimate". Not enabled in v1.

## Rule-based flags & colours (deterministic dressing, computed here for tidiness)

- **WoW colour:** ≥0 → green `#1f9d57`; <0 → red `#d6453a`. Arrow ▲ (`&#9650;`) up / ▼ (`&#9660;`) down.
- **GP% colour:** <50 → red `#c43b27`; else green `#1f7a55`.
- **Stock colour (Top/reorder):** low (≤ ~1 wk cover or <15) → red `#c43b27`; heavy (>600) → amber `#b5740a`.
- **Reorder action:** cover<0.7 & sells ≥3 of last 4 wks → `REORDER↑` (green); cover<1.7 → `REORDER` (green); cover<2.5 → `SMALL BUY` (amber); velocity faded (w0 ≤ ¼ of peak) → `WATCH` (amber).
- **New-arrival Read:** sold/recvd & on-hand → JUST IN / HOT / SELLING / SLOW / OVERSTOCK (overstock = on-hand high AND >8 wks cover).
- **Open-PO flag:** vendor currency ≠ vendor country → `FX + CANCEL?` (red); SKU series >6 months old & consignment → `OLD·CONSIGN` (red); 0 lifetime sales → `0 SOLD` (red); else `OK` (green) / `NEW` (amber).
- **Dead-stock tag:** Big Box/ACTIONCITY PTE/MNT → `CONSIGN`; Pony/Toysinbox/Chaw → `INTERCO`; action always `RETURN`.

## Mode badge — `mode_badge`, `mode_badge_color`

- `manual-test` → badge "TEST" colour `#b5740a`.
- `scheduled` / `manual-live` → badge "DAILY" colour `#F27061`.
