# CHAW Weekly Finance Control — automated HTML report

Built the CHAW way: single-purpose files the routine **reads and fills with code**, never regenerates.
Pulls from NetSuite, classifies risk deterministically, and emails a **full 7-section HTML report**
(plus a short Lark group recap). Runs unattended weekly (Monday 08:00 Asia/Bangkok). **Deliverable is
HTML — no Excel.** Styled to CHAW CI (Poppins, #5551FE / #F27061 / #F5EDE4) with a UTF-8 + Thai font
stack so Thai vendor/customer names render correctly. Two views: stacked (email) and tabbed (easy read).

## What it checks
Cash position · AR aging + credit-term cross-check · bank reconciliation · cash-deposit verification
(T+2 / T+3 automated-JV) · undue-VAT staff-reversal (by vendor) · memorized-transaction health
(overdue / pending approval) · duplicate vendor bills (exact + same-day heuristic).

## Pipeline
```
NetSuite queries ──▶ data.json (raw, small, model-produced)
        │
        ▼  fc_build_data.py   (deterministic classifier — applies fc-prediction.md thresholds)
   render.json (scalars / repeats / sections)
        │
        ▼  fill_template.py   (string substitution — no model output)
   fc-report.html        ──▶ lark_send_email   (stacked, email body — renders inline in Lark)
   fc-report-tabbed.html ──▶ email attachment  (tabbed, one tab per section — easy reading)
   lark_summary.txt      ──▶ lark_send_message (group recap)
```
The model never emits the HTML — it writes the small `data.json`; the scripts assemble everything
(avoids the 32K output-token crash).

## Files
| File | Role | Changes when |
|------|------|--------------|
| `fc-queries.md` | NetSuite SuiteQL, fixed params, date logic, completeness checks | NetSuite changes |
| `fc-prediction.md` | Risk-classification thresholds + commentary guardrails | Thresholds/policy change |
| `fc_build_data.py` | Deterministic classifier: raw `data.json` → `render.json` | Classification logic change |
| `fc-template.html` | Locked STACKED report — email-safe body (UTF-8, Thai-safe, inline styles) | Layout change |
| `fc-tabbed-template.html` | Locked TABBED standalone view — pure-CSS tabs, one per section (browser/attachment) | Layout change |
| `fc-lark-summary.txt` | Locked Lark group recap (tokens) | Layout change |
| `fill_template.py` | Assembles HTML/text from template + `render.json` | — (shared, tested) |
| `fc-delivery.md` | Channels (email HTML + group recap), recipients, subject | Recipients/text change |
| `fc-routine-prompt.md` | The full instruction set the routine executes | Orchestration change |
| `data.sample.json` | Raw shape the routine must produce (real 22 Jun 2026 run) | — (reference) |
| `render.json` | Example classifier output (the fill contract) | — (reference) |
| `fc-report.sample.html` | Example rendered stacked (email) report | — (reference) |
| `fc-report-tabbed.sample.html` | Example rendered tabbed report | — (reference) |
| `sender.md` `method.md` `branding.md` `contacts.md` | Shared delivery mechanics / routing / CI / IDs | Rarely |

> Started all-in-folder. To scale to more reports, lift `sender/method/branding/contacts.md` to the repo
> root and keep per-report files in their own `<Brand>/` folder.

## Run locally / test
```
python3 fc_build_data.py data.sample.json render.json
python3 fill_template.py fc-template.html        render.json > fc-report.html         # email body (stacked)
python3 fill_template.py fc-tabbed-template.html render.json > fc-report-tabbed.html  # tabbed (easy reading)
python3 fill_template.py fc-lark-summary.txt     render.json > lark_summary.txt
# open either .html in a browser to preview
```

## Deploy as a cloud routine
1. Push this folder to the GitHub repo (connectors: NetSuite + Lark attached to the routine).
2. Routine prompt box (one line):
   `Read Finance Control/fc-routine-prompt.md from the repo and execute every step in it exactly, in order. Run unattended — no approval prompts. Use the attached NetSuite and Lark connectors.`
3. Run-now in **manual-test** mode (HTML emailed to owner only). Verify: files read, `report_date` =
   today-BKK, queries return + completeness passes, `fill_template.py` reports no leftover `{{tokens}}`,
   the email renders all 7 sections.
4. Switch to **scheduled**, weekly Monday 08:00 Asia/Bangkok.

## Non-negotiables (prevent specific failures)
- Model never outputs the HTML — it writes `data.json`; scripts assemble (32K token-crash guard).
- Dates always Asia/Bangkok at runtime; never hardcoded, never server-UTC.
- Completeness checks gate the send — never send a partial/zero report.
- Fail loud (DM owner / post to group); no auto-retry.
- Branding lives in this repo, not the local skill path.
