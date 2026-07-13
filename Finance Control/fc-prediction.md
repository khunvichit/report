# fc-prediction.md — Finance Control classification & commentary

This report has no statistical forecast; its "generative" layer is **risk classification, ranking and
commentary**. Kept separate from queries because it reasons and can vary — debug it here, not in the
data layer. Compute it AFTER the actuals, display it at the top (Executive Summary).

## Guardrails (non-negotiable)

- **Describe, don't diagnose.** State what the numbers show ("435,487 overdue, 55 days past a 30-day
  term"). Never invent a cause ("customer is in financial trouble") that isn't in the data.
- **Deterministic thresholds, not vibes.** Every severity below is a fixed rule on a number/date, so two
  runs on the same data classify identically.
- **Label any narrative line as report commentary**, not fact about intent.
- **Govt/clearing caveat.** V-00313 (Revenue Dept) and tax/landlord vendors (King Power, Customs) can
  show large undue-VAT swings that are systematic, not staff error — always annotate, never headline as
  fraud.

## Classification rules (applied in `fc_build_data.py`, sourced here)

**AR credit cross-check** (per customer, vs term days, measured at report_date):
- CRITICAL: days overdue > 2× term · PAST TERMS: > term · WATCH: within 5 days of term · OK: within term.

**Bank reconciliation:** OVERDUE if last recon > 30 days before report_date, else OK.

**Cash deposit (T+2 Cash Sales / T+3 others):** OK ≤ benchmark · LATE 1–2d past · OVERDUE 3–14d past ·
CRITICAL 14d+ (automated JV stopped) · NEGATIVE (over-transferred) · INACTIVE (no balance/activity).

**Undue VAT urgency** — positive (not reversed): CRITICAL >365d · HIGH 181–365 · MEDIUM 91–180 · LOW ≤90.
Negative (over-reversed): HIGH >50k · MEDIUM 5k–50k · LOW <5k.

**Memorized txns:** OVERDUE (nextDate < report_date) graded CRITICAL >90d / HIGH 30–90 / MEDIUM 7–30 /
LOW 1–7 · PENDING APPROVAL (status=1) flagged regardless of date · DUE THIS WEEK (Mon–Sun, approved) ·
ON TRACK (future, approved).

**Prepayment (30-day):** a Prepayment-terms open bill must have its deposit APPLIED within 30 days of the bill date; open >30 days = BREACH (flag red, KPI counts breaches). Sort oldest-first.

**Duplicates:** HIGH = exact match OR a "do-not-use / one-time" vendor billed twice · REVIEW = same
vendor+amount+date cluster on a normal vendor · LOW = known recurring/multi-branch vendor. Always carry the
cluster's bill numbers (`tranid`s) on the row so the issue is directly traceable to documents.

## Top-10 risk ranking (Executive Summary → `data.exec_risks`)

Rank by money-at-risk × severity, mixing control areas. Each row: area, item, one-line detail, amount,
severity. Include undue-VAT and memorized-txn items when material. → also drives `data.priority_actions`
(URGENT / CRITICAL / ACTION) and `data.deposit_actions`.
