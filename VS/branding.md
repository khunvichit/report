# branding.md — CHAW Corporate Identity (shared)

Locked design tokens for every CHAW report. Reports reference these from the template, never inline
custom colours. Cloud routines read this file from the repo; it is NOT in any local skill folder.

---

## Colours (hex)

| Role | Token | Value |
|------|-------|-------|
| Primary indigo | `--chaw-indigo` | `#5551FE` |
| Primary indigo light | `--chaw-indigo-light` | `#7B79FF` |
| Accent coral | `--chaw-coral` | `#F27061` |
| Cream background | `--chaw-cream` | `#F5EDE4` |
| Cream light (card) | `--chaw-cream-light` | `#FFF8F5` |
| Footer dark | `--chaw-footer` | `#2C3E50` |
| Success green | `--chaw-green` | `#2D7A3F` |
| Warning amber | `--chaw-amber` | `#F39C12` |
| Warning amber text | `--chaw-amber-text` | `#856404` |
| Danger red | `--chaw-red` | `#C5453E` |
| Danger red text | `--chaw-red-text` | `#721C24` |
| Text primary | `--chaw-text` | `#2C3E50` |
| Text secondary | `--chaw-text-muted` | `#5F5E5A` |
| Reference line | `--chaw-ref-line` | `#4A5568` |
| Hairline | `--chaw-hairline` | `#F0E5DA` |

### Heatmap 7-step scale (dark green → grey → dark red)

| Step | Background | Text | Triggers when |
|------|-----------|------|---------------|
| `hc-g3` | `#1E6B30` | `#fff`     | Δ ≥ +20% |
| `hc-g2` | `#2D7A3F` | `#fff`     | Δ ≥ +10% |
| `hc-g1` | `#7AB893` | `#1A4A22`  | Δ ≥ +5% |
| `hc-z`  | `#F0E5DA` | `#5F5E5A`  | −3% < Δ < +3% (flat) |
| `hc-r1` | `#F5B6B0` | `#5A1410`  | Δ ≤ −5% |
| `hc-r2` | `#D86158` | `#fff`     | Δ ≤ −10% |
| `hc-r3` | `#7E2A23` | `#fff`     | Δ ≤ −20% |

### Severity badge palette

| Class | Background | Text | Use |
|-------|-----------|------|-----|
| `sev-surge` | `#FBE9E7` | `#F27061` | 🔥 SURGE (WoW ≥ +15% AND DoD ≥ +10%) |
| `sev-positive` | `#E8F5E9` | `#2D7A3F` | ✅ POSITIVE (WoW ≥ 0) |
| `sev-neutral` | `#F0E5DA` | `#5F5E5A` | ─ NEUTRAL (−5% < WoW < 0) |
| `sev-watch` | `#FFF3CD` | `#856404` | ⚠ WATCH (WoW ≤ −5%) |
| `sev-high` | `#FFEFE0` | `#C77818` | 🟠 HIGH (WoW ≤ −10% AND DoD < 0) |
| `sev-critical` | `#FBE9E7` | `#C5453E` | 🚨 CRITICAL (WoW ≤ −20% AND DoD ≤ −10%) |
| `sev-new` | `#E3F2FD` | `#1565C0` | 🆕 NEW (no D8 history) |

---

## Typography

Email-safe font stack:
```
font-family: Poppins, -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
```
Reports never load remote @font-face; the email client picks the closest available. Poppins is the
brand font on web; the system fallbacks are visually close enough for daily emails.

Sizes:
- Page H1 (header title): 24px / 600
- Section H2: 16px / 600
- Body: 13px / 1.55
- Table headers: 11px / 600 / uppercase / letter-spacing 0.5px
- KPI value: 24px / 600
- Footnote / small: 11px / muted colour

---

## Header gradient

```css
background: linear-gradient(135deg, #5551FE 0%, #7B79FF 100%);
```
Always indigo → light-indigo, 135°. Coral is reserved for accent only (insight box border, D1
highlight, "Hot Drinks" / Vendi).

---

## Container metrics

- Outer page bg: `#F5EDE4` (cream)
- Wrapper: `max-width: 920px`, `background: #FFF8F5`, `border-radius: 12px`, `box-shadow: 0 4px 24px rgba(44,62,80,0.08)`
- Section padding: `24px 32px`
- Section divider: `border-bottom: 1px solid #F0E5DA`
- Footer: bg `#2C3E50`, text `#C5BFB0`, accent (`b`) `#fff`

---

## Footer template (every report ends with this)

```html
<div class="footer">
  <div><b>CHAW {entity_long_name}</b> · Sub {sub_id} — {entity_short_name}</div>
  <div>Source: NetSuite Sub {sub_id} <code>transactionline</code> (pre-VAT) · MTD: {mtd_start_short}–{report_date_short} ({mtd_days} days)</div>
  <div>Runbook {runbook_version} · Generated {generated_display} — vichit@chaw.co.th</div>
</div>
```

`runbook_version` = the per-report version (e.g. `v1.0` for Vending, `v2.7` for SFB).

---

## Logo / asset references

CHAW does not embed images in routine emails (image hosting is brittle for cloud routines). Header is
the gradient block with text only. If a future report needs a logo, host the PNG in the GitHub repo
under `assets/` and reference it as a `<img src>` with the raw GitHub URL.

---

## Email-client compatibility notes

- `<style>` in `<head>` is honoured by Gmail, Apple Mail, Lark Mail, Outlook 365. Some older Outlook
  desktop installs need inline styles — the template uses inline-safe classes that double up as
  CSS-named selectors so the dual-coding works.
- No flexbox in critical layout: use HTML tables for KPI rows, bar charts, heatmaps, and the email
  wrapper. Flexbox is used only for the `.kpi` row where degraded fallback is acceptable.
- No SVG charts. Bar charts use stacked `<div>`s inside `<td>` cells (the SFB pattern, verified
  email-safe).
- No web fonts loaded from URLs. Poppins falls back to system fonts in clients that don't have it.
