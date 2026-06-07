# khiang-delivery.md — delivery choice + content

Declares which channels fire and supplies the per-report recipients/text. Mechanics in `sender.md`,
routing in `method.md`.

```
Delivery:
  Channels: email + group          # NO task channel (not yet enabled for Khiang)
  Fire group only if: anomaly_count > 0
  Email key: [Khiang] Daily Sales Report — {report_date_display}
  Owner (manual-test recipient): vichit@sfb.co.th
```

> Task channel is intentionally OFF, and the in-email CCTV action plan was removed. Anomaly hours are
> flagged in the hourly table and a CCTV-investigation request goes to the Khiang group. When the
> task channel is later enabled, add `task` to `Channels:` and restore the TASK block (kept commented
> at the bottom of this file).

## EMAIL
- html_body source: `email.html` (output of `fill_template.py khiang-template.html data.json`).
- `to`:
  ```json
  [ {"address":"management@chaw.co.th","name":"CHAW Management"},
    {"address":"khiang@chaw.co.th","name":"Khiang Team"} ]
  ```
  > manual-test mode overrides `to` → owner only (vichit@sfb.co.th).
- Subject: `{target_icon} [Khiang] Daily Sales Report — {report_date_display} | ฿{net_sales} ({signed_pct}%)`
  - target_icon: 🔥 ≥฿50,000 · ✅ ฿40,000–50,000 · ⚠️ <฿40,000

## GROUP  (gated: anomaly_count > 0)
- chat_id (primary): Khiang `oc_98ff051dc62904235c4743f69d9e4dba`
- chat_id (fallback): Quality `oc_1720a4005f44033a8ad78aa60a63216b`
- message (text):
```
📹 CCTV Investigation Required — Khiang {report_date_display} ({report_day_th})

สวัสดีทีม Khiang 🙏

📊 ยอดขาย: ฿{net_sales} ({signed_pct}% vs target)
📈 MTD avg: ฿{avg_mtd}/day  ·  30d avg: ฿{avg_30d}/day
🚨 ชั่วโมงผิดปกติ: {anomaly_count} ชม. ({critical_n} critical, {high_n} high)

Anomalies:
{per-hour lines: 🔴/🟠 [{hour}] {issue_type} (bills {actual} vs bench {bench}, {pct}%)}

กรุณาตรวจสอบ CCTV และแจ้งผลกลับในกลุ่มนี้ภายใน 24 ชม. ขอบคุณครับ 🙏
```
- If `anomaly_count == 0`: skip; console `"✅ No hourly anomalies — Khiang group not notified."`

> NOTE: `report_day_th` (Thai weekday) is derived from REPORT_DATE in the routine.
> The group message no longer references a Lark task or owners-by-name, since no task is created.

---

## TASK block (DISABLED — kept for easy re-enable)
<!--
## TASK  (gated: anomaly_count > 0)
- summary: 📹 CCTV Investigation — Khiang {report_date_display} ({anomaly_count} hrs: {critical_n} critical, {high_n} high)
- description: all flagged hours, one block each — [hour] issue_type · bills {actual} vs bench {bench} ({pct}%) · cameras · questions.
- due: {REPORT_DATE +1 day}T18:00:00+07:00  (report back within 24h)
- assignees (add each separately): Sarun, Ploynapat
- follower: Vichit
- Capture returned task_guid → set the {{task_guid}} scalar so the email CCTV link + group message resolve.
- To re-enable: add `task` to Channels:, create the task BEFORE building data.json when anomalies exist.
-->
