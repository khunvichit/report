# SFB — Method (routing / gating / modes)

The delivery engine. Reads this report's choices from `sfb-delivery.md` and runs them in a fixed
order. This file does not change per run.

## Channel menu
email · group · ~~task~~ (task disabled for SFB per owner request 2026-06).

## Fixed order of operations
dates (Asia/Bangkok) → idempotency check → NetSuite responsiveness → queries (Q1–Q3) →
completeness gate → aggregate/classify → build `data.json` → assemble `email.html` →
send email → group post → console summary.

## Gating
- **Email:** always fires (daily heartbeat).
- **Group:** always fires in `scheduled` / `manual-live` (SFB posts daily); skipped in `manual-test`.
- **Task:** not used.
- Distinguish *not listed* (task — never used here) from *gated* (group — used, but skipped in test mode).

## Modes
- `scheduled` (default) — full delivery: email to recipients + group post. Report date = yesterday (BKK).
- `manual-test` — email to `OWNER_EMAIL` only; skip the group post. Use to validate before scheduling.
- `manual-live` — full delivery; for back-fills with an explicit `REPORT_DATE` (D1) override.

## Hard stops (abort the run, fail loud)
- Timezone guard: resolved report date ≠ yesterday-BKK with no D1 override.
- Completeness check failure (any check in `sfb-queries.md`).
- NetSuite unresponsive after one retry.
- Email send failing after one retry (→ DM owner the HTML body).

On any hard stop: post the failed step + reason to the Food Operation Core group (or DM owner).
No whole-routine auto-retry. A single channel failing does not abort the others.
