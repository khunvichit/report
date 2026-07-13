# branding.md — CHAW CI for Finance Control (repo copy, routine-safe)

> A cloud routine can't see the local `chaw-branding` skill path. This repo copy is the source of truth
> at runtime. Official CHAW CI assets (logos, typefaces, swatches) live in the **Chaw CI** Google Drive
> (202412_CHAW MATERIAL FILE). Sync the values below if they change.

## Brand palette (CHAW CI)
| Token | Hex | Role / ratio |
|-------|-----|--------------|
| PRIMARY (purple-blue) | `#5551FE` | ~50% — title band, section headers, table header rows, totals |
| SECONDARY (coral) | `#F27061` | ~25% — accents, alert/critical bands, overdue figures |
| TERTIARY (cream) | `#F5EDE4` | ~25% — page background, breathing space, highlight rows |
| INK | `#1B2A4A` | body text |
| WHITE | `#FFFFFF` | card / header text |
| BORDER | `#E0DCD3` | cell borders on cream |

Status tints (kept as soft traffic-lights for the finance controls, harmonised to CI):
`RED_BG #FBE4E0` (critical/overdue) · `AMBER_BG #FFF3E0` (late/watch/pending) ·
`GREEN_BG #E8F5E9` (ok/within terms) · `CORAL_BG #F8C8C0` (high) · `CREAM #F5EDE4` (subtotal/highlight) ·
`GRAY #F5F5F5` (inactive). Used by `fc_build_data.py`; chrome colours live in `fc-template.html`.

## Typography
- **Poppins** for all Latin text (CHAW primary font).
- **Thai must stay readable:** the email/report uses a per-glyph fallback stack —
  `'Poppins','Noto Sans Thai','Sarabun',Tahoma,Arial,sans-serif`. Latin renders in Poppins; Thai falls
  to Noto Sans Thai / Sarabun (web preview) or **Tahoma** (email clients, always present). The HTML
  declares `<meta charset="UTF-8">` so Thai company/vendor names render correctly.

## Footer
- "CHAW Management · Finance Control · automated weekly routine."
- All amounts THB. Source line: NetSuite (Reports API 412/273 preferred; SuiteQL fallback).

## Tone (CHAW values: Continuous improvement · Customer · Humorous · Attention to communication · Work-life)
- Professional but approachable; communicate clearly and completely.
