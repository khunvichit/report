# Juiceland Daily Report — Routine Prompt (file #3 of 3)

Paste this as the routine/scheduled-task prompt. Keep it short — the detail lives in the two files it points to.

---

Generate the Juiceland Daily Sales Report for **yesterday (Asia/Bangkok)**.

Files (read both first, in this order):
1. `juiceland-queries.md` — data map: every NetSuite query + fixed params + date logic + completeness checks.
2. `juiceland-template.html` — the LOCKED HTML format. Reproduce it verbatim and only substitute values.

Steps, in order:
1. Compute dates per the queries file (timezone Asia/Bangkok, report_date = yesterday). If a `REPORT_DATE` override is passed, use it.
2. **Idempotency:** check Lark sent-mail for subject containing `[Juiceland] Daily Sales Report — {report_date_display}`. If found, print `✅ Already sent for {report_date_display} — skipping.` and STOP.
3. Run Queries A–E (read-only SuiteQL tool, param `query`). Roll loc 169 into MW1.
4. Run the completeness checks in the queries file. If any hard check fails (wrong date, no data for report_date), STOP and report — do not send.
5. Build the HTML by filling `juiceland-template.html`:
   - Substitute every `{{token}}`.
   - For each `<!-- REPEAT:name -->` block, render once per item, then remove the markers.
   - For each `<!-- SECTION:name -->`, omit the whole block per its stated condition (e.g. no AM items → omit banner).
   - Do not alter any colours, px sizes, inline styles, or section order.
6. Send via `lark_send_email` to juiceland@chaw.co.th + management@chaw.co.th. Subject per template. **Email only — do not write HTML to disk.**
7. Create the consolidated Lark task and post the Quality-group summary per the runbook (skip each if am_queue_count == 0 AND dormant_count == 0).
8. Print the Step 8 console summary.

Schedule: daily, early morning Asia/Bangkok (after midnight close).
