# CHAW Reporting — BRANDING (shared)

The brand facts every report needs at runtime. Lives at the repo root so a cloud routine
can read it from the clone — it does NOT depend on the local `chaw-branding` skill path
(that path is not visible to cloud routines).

> Source of truth: the `chaw-branding` skill. This file is the report-scoped extract.
> If you rebrand, update here AND re-check each report's locked HTML template.

---

## Colours

| Role | Hex | Use |
|------|-----|-----|
| Primary | `#5551FE` | purple-blue — dominant (~50%): headers, key UI, MW1 series |
| Secondary | `#F27061` | coral — accents (~25%): badges, CTA, SE3 series |
| Tertiary | `#F5EDE4` | warm cream — backgrounds / table header rows |
| Footer dark | `#2C3E50` | CHAW values footer band |

Report-specific extras (kept here so all report files agree):
- PKT branch series colour: `#2E7D32` (forest green)
- Header gradient: `#5551FE → #7B79FF`
- Yesterday-highlight cell: `#FFF3E0`
- Alert/amber: `#FFA000` · gap orange `#E65100` · gap red `#C62828`

## Fonts

- **Primary: Poppins** — all headings and body. Embed via Google Fonts:
  `https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap`
- Numeric / monospace displays: monospace (chart axis day labels, etc.)

## CHAW core values (footer strip — exact order and labels)

| Letter | Value |
|:------:|-------|
| C | Continuous Improvement |
| C | Customer Orientation |
| H | Humorous |
| A | Attention to Communication |
| W | Work-Life Balance |

Footer band: background `#2C3E50`, white text, each letter in `#F27061`, label beneath.

## Tone (for any written copy in reports)

Professional but approachable. Clear and complete (the "A"). Warm, improvement-focused.

---

## Usage in reports

- The locked HTML templates already embed these colours and the footer values — that is the
  reliability fallback. This file is the shared source so all reports stay consistent and a
  rebrand is a one-place edit.
- A report's runbook Step 0 should read `branding.md` (this file) — NOT the skill path.
  If unreachable, fall back to the values already baked into the report's HTML template.
