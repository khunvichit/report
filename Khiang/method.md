# method.md — routing engine (shared, does not change per report)

Reads each report's `Delivery:` declaration and runs the channels in fixed order under its gates.

## Channel menu
`email` · `task` · `group` (optionally `archive` = write a Lark Base record; not used by Khiang).

## Fixed order of operations
```
read files → dates(BKK) → idempotency → run queries → completeness(HARD STOP) →
prediction/anomaly → build data.json → fill_template.py → send EMAIL → TASK(gated) →
GROUP(gated) → console
```

## Gating
- `email` usually ALWAYS fires (after completeness passes).
- `task` and `group` fire only when the report's gate condition is true.
- Distinguish **not listed** (channel never used by this report) from **gated** (used only when there
  is something worth sending).

## Modes
- `scheduled` — full delivery (email + gated task/group). Default.
- `manual-test` — email to OWNER ONLY; skip task + group. Use for first runs / after any change.
- `manual-live` — full delivery, for back-fills with a manual REPORT_DATE override.

## Failure handling
- A single channel failing does NOT abort the others.
- Idempotency hit and completeness failure are HARD STOPS (no send).
- On hard failure: fail loud — DM the owner / post to the failure group with which step failed and why.
  Never fail silently on a CFO-facing report. No auto-retry of the whole routine.
