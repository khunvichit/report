# Proposed additions to the `chaw-report-builder` skill

Two fixes found while debugging the SFB daily report (2026-06). Apply both in
Settings → Capabilities (or the skill's GitHub repo). Then DEPLOY the corrected
template + fill_template.py to the repo the routine runs from — a partial edit
(e.g. removing flexbox but keeping the fixed stack height) re-introduces the bug.

---

## EDIT 1 — Chart bars must NOT use flexbox (add to `references/template-format.md`)

### Chart bars must NOT use flexbox (email-safe stacking)

Stacked bar charts must render the same in every email client. Do NOT use
`display:flex; flex-direction:column-reverse`. Outlook and some Gmail/mobile clients
ignore flexbox, so bars hang from the top in reversed order ("inverted" chart).

The fix has THREE parts — all required, or it half-applies and still breaks:

1. **Remove the fixed stack height.** `.bar-stack { font-size:0; line-height:0; }`
   — no `display:flex`, no `flex-direction`, no `height`. (Keeping a fixed height
   makes block segments fill from the top of the box and hang downward.)
2. **Anchor to the baseline on the cell.** The bar `<td>` keeps
   `vertical-align:bottom` in CSS AND carries the HTML attribute `valign="bottom"`.
   The HTML attribute is honored even by clients that ignore the CSS — belt and
   suspenders. Segment class: `.seg { display:block; width:100%; font-size:0; line-height:0; }`
3. **List segments largest/top-first in the markup.** Without flex, source order =
   top-to-bottom visual order. e.g. Subway, Khiang, JL, SE, Vendi; airports BKK, DMK, PKT.

Always preview in Outlook or an email tester, not just a browser. Browsers are
forgiving; the target email client is not.

---

## EDIT 2 — Color each delta by its OWN sign (add to `references/template-format.md` + `assets/fill_template.py`)

### Per-value sign coloring for KPI deltas

A KPI card that stacks several signed values (e.g. Revenue showing WoW / DoD / vs-MTD)
must NOT share one color class — a negative value then renders green. Color each value
by its own sign.

`fill_template.py` auto-derives a `<key>_cls` for every signed scalar
(`+x%` → `delta-up`, `-x%` → `delta-down`, `0`/`—` → `delta-neutral`):

```python
scalars = data.setdefault("scalars", {})
for key in list(scalars.keys()):
    cls_key = key + "_cls"
    if cls_key in scalars:
        continue
    val = str(scalars[key]).strip()
    if val.startswith("+"):
        scalars[cls_key] = "delta-up"
    elif val.startswith("-") or val.startswith("−"):
        scalars[cls_key] = "delta-down"
    elif val in ("0", "0%", "0.0%", "0.00%", "—", "-", "n/a", "N/A", ""):
        scalars[cls_key] = "delta-neutral"
```

Template then colors each line independently, e.g.:

```html
<div class="delta">
  <span class="{{wow_signed_cls}}">WoW {{wow_signed}}</span><br>
  <span class="{{dod_signed_cls}}">DoD {{dod_signed}}</span><br>
  <span class="{{mtd_signed_cls}}">vs MTD avg {{mtd_signed}}</span>
</div>
```

No data-layer change needed — the routine keeps emitting the same signed strings.

---

## EDIT 3 — Add to `SKILL.md` "Non-negotiables"

- **No flexbox in chart bars.** Stacked bars use block segments with NO fixed stack
  height, anchored by the cell's `vertical-align:bottom` + HTML `valign="bottom"`,
  listed top-first in markup. Flexbox (or a leftover fixed height) renders "inverted".
- **Color each signed delta by its own sign.** Never share one color class across
  mixed-sign values; `fill_template.py` auto-emits `<key>_cls` for this.
