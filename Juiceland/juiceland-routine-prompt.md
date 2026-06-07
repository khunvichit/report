# Juiceland Daily Report — Routine Prompt (v2, code-assembled HTML)

Paste this as the routine prompt. Key change from v1: **the model never outputs the HTML email.**
It computes data only, writes it to `data.json`, and a script assembles the HTML. This avoids the
32K output-token limit that was crashing the run on the full email.

Repo: `khunvichit/report`. Files at repo root (adjust paths if you use folders).

---

Generate and send the Juiceland Daily Sales Report for **yesterday (Asia/Bangkok)**.

Read first, in order: `juiceland-queries.md`, `juiceland-prediction.md`, `juiceland-delivery.md`,
`sender.md`, `method.md`, `branding.md`. Do NOT read the full HTML template into context to
re-emit it — the script handles the template.

Then execute:

1. DATES — report_date = yesterday in Asia/Bangkok (UTC+7). Honour a manual REPORT_DATE override.

2. IDEMPOTENCY — search Lark sent-mail for subject containing
   "[Juiceland] Daily Sales Report — {report_date_display}". If found, print
   "Already sent for {report_date_display} — skipping." and STOP.

3. QUERY — run Queries A-E from `juiceland-queries.md` (read-only SuiteQL tool, param "query").
   Roll location 169 into MW1. Retry a failed query once.

4. COMPLETENESS — run the checks in `juiceland-queries.md`. If any hard check fails, STOP and
   report via the failure path (step 9). Do NOT send a partial report.

5. PREDICTION — compute forecast/commentary/anomaly per `juiceland-prediction.md`
   (AFTER actuals are known; obey guardrails — ranges + confidence, describe-don't-diagnose).

6. BUILD DATA, NOT HTML — assemble a single `data.json` describing every value the email needs.
   Do this INSTEAD of writing any HTML. Structure:

       {
         "scalars":  { "comb_net":"68,545", "signed_pct":"-3.8", "report_date_display":"5 June 2026", ... },
         "repeats":  { "chart_days":[...], "last7_mw1":[...], "top20_branches":[...], "dormant_branches":[...] },
         "sections": { "am_review":false, "seasonal":true, "dormant":true,
                       "forecast_shown":true, "forecast_suppressed":false, "anomaly_shown":true }
       }

   - scalars: every single-value {{token}} in the template.
   - repeats: each REPEAT block name -> list of objects, one per row, keys = that block's tokens.
     For nested repeats (e.g. dormant_rows inside dormant_branches), compute the inner rows' HTML
     string and place it under the parent item as the token it occupies, OR keep the script's
     nesting convention. Prefer structured lists; pre-render inner HTML only if needed.
   - sections: boolean per SECTION name — true = keep, false = omit. Set per the gates
     (am_review = am_queue_count > 0; forecast_suppressed = confidence is low/insufficient; etc).
   Write data.json to disk. Keep visible output SMALL — do not echo the full json or any HTML.

7. ASSEMBLE + SEND — run:

       python3 fill_template.py juiceland-template.html data.json > email.html

   This produces the final HTML by substituting scalars, expanding REPEAT blocks, and keeping/
   dropping SECTIONs. The HTML lives in a file — it never passes through your output. If the script
   prints "WARNING unresolved placeholders" to stderr, add those tokens to data.json and re-run;
   do not send with unresolved money/date tokens.
   Then send via `lark_send_email` (per `sender.md`) to juiceland@chaw.co.th + management@chaw.co.th,
   reading the body from email.html. Subject per `juiceland-delivery.md`. Email only.

8. (folded into 7)

9. DELIVER GROUP — per `juiceland-delivery.md` and `method.md`, gated on
   (am_queue_count + dormant_count > 0). Send the summary to the Juiceland Lark group
   (chat_id in delivery file; fallback Food Operation Core). NO Lark task is created (task channel off).
   Skip the group message if the gate is 0.

10. FAILURE PATH — if any step hard-fails (query error after retry, completeness stop, script error,
    send error), post a short message to the CHAW Finance group (oc_a834e976f4c5a57474d2e022e765dc1f)
    or DM Vichit via Lark stating which step failed and why. Never fail silently.

11. CONSOLE — print a compact summary (per-branch net, alerts, what fired). Keep it short.

Mode: if Mode=manual-test is passed, send email to vichit@chaw.co.th ONLY and skip task + group
(for validation runs). Default Mode = scheduled.

Note: fill_template.py must be committed to the repo alongside the template.
