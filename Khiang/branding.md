# branding.md — CHAW CI (repo copy, routine-safe)

Single source of truth for CHAW brand values in reports. Lives in the repo (NOT `/mnt/skills/...`),
because a cloud routine cannot see the local skill path. Edit here to update every report's footer.

## Colours
| Role | Hex | Use |
|------|-----|-----|
| Primary (CHAW Indigo) | `#5551FE` | headers, key UI — ~50% |
| Secondary (CHAW Coral) | `#F27061` | accents/CTAs — ~25% |
| Tertiary (CHAW Cream) | `#F5EDE4` | backgrounds — ~25% |
| Ink | `#2C3E50` | body text |

## Fonts
- Primary: **Poppins** (headings + body). Email clients fall back to Arial/Helvetica (already set in
  the template's `<body>` font-family) — do not rely on web fonts rendering in email.
- Numerics elsewhere (non-email): JetBrains Mono.

## Footer values strip — `chaw_values`
The template footer renders `{{chaw_values}}`. CURRENT canonical set is the **CHAWS** framework:
```
Curious · Team · Act Fast · Empowered · Simple
```
> If CHAWS is superseded, change this ONE line; every report's footer updates. Do NOT hardcode values
> into the template or copy them from old emails (v3.1's mistake was reading them from a local path).
