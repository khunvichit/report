# method.md — ROUTING engine (shared)

Reads each report's `delivery.md` declaration and routes accordingly. Does NOT change per report.

## Channel menu
`email`, `task`, `group` (and optional `archive` = write a Lark Base record). A report's
`Delivery: Channels:` line picks any subset.

## Fixed order of operations
`dates → idempotency → completeness → prediction → build data.json → fill_template → email → task → group → console`

## Gating
- **email** usually always fires (after completeness passes).
- **task / group** fire on the report's gate (e.g. `always`, or `only if exceptions>0`).
- Distinguish **not listed** (channel never used by this report) from **gated** (used, only when warranted).

## Modes
- `scheduled` — full delivery (default).
- `manual-test` — email to OWNER ONLY, skip task+group. Use for first 1–2 weeks / after any change.
- `manual-live` — full delivery, for back-fills (with REPORT_DATE override).

## Hard stops vs soft fails
- **Hard stops** (abort the send): failed completeness check, idempotency hit (already sent), timezone guard.
- **Soft fails** (continue other channels, then fail-loud note): one channel erroring, one empty section.
- **No auto-retry** of the whole run. On hard failure, post to the report's failure channel.
