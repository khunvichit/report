# method.md — delivery routing (shared engine)

WHICH channels fire, in what order, under what gate. Reports declare choices into this; this file does
not change per report.

## Channel menu
`email`, `group`, `file`, `task` (and optionally `archive` = write a Lark Base record).

## How a report declares
A `Delivery:` block (see each report's `*-delivery.md`) with:
- `Channels:` — the subset this report uses.
- gate line(s) — condition under which a channel fires (control reports usually fire always).
- `Email key:` — the idempotency subject.

## Fixed order of operations
dates (BKK) → idempotency → run queries → completeness → classify/predict → build `data.json` →
assemble (fc_build_data.py + fill_template.py) → email (HTML) → group recap → console.

## Gating
- A channel may fire **always** or be **gated** on a report-supplied condition.
- Distinguish **not listed** (channel never used by this report) from **gated** (used only when there's
  something worth sending). Finance Control fires group+file+email always — it is a control report.

## Modes
- `scheduled` — full delivery (default; weekly Monday 08:00 Asia/Bangkok).
- `manual-test` — email to owner ONLY, skip group/file/task — for validation.
- `manual-live` — full delivery, for back-fills (`REPORT_DATE` override).

## Failure handling
- A single channel failing does NOT abort the others.
- Idempotency and completeness checks are the only HARD STOPS.
- No auto-retry on a failed run; on hard failure, fail loud (DM owner / post to group).
