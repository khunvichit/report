# khiang-delivery.md — delivery choice + content

Declares which channels fire and supplies the per-report recipients/text. Mechanics in `sender.md`,
routing in `method.md`.

```
Delivery:
  Channels: email + group          # NO task channel (not yet enabled for Khiang)
  Fire group: ALWAYS (daily digest — no longer gated on anomalies)
  Email key: [Khiang] Daily Sales Report — {report_date_display}
  Owner (manual-test recipient): vichit@chaw.co.th
```

> Task channel is intentionally OFF, and the in-email CCTV action plan was removed. Anomaly hours are
> still flagged in the hourly table + alert banner, but the Khiang group now gets a plain DAILY SALES
> DIGEST (not a CCTV alert). When the task channel is later enabled, add `task` to `Channels:` and
> restore the TASK block (kept commented at the bottom of this file).

## EMAIL
- html_body source: `email.html` (output of `fill_template.py khiang-template.html data.json`).
  **READ the file and paste its FULL contents into the send tool's `body` argument** — the tool
  cannot open files; a path or placeholder string gets sent to recipients verbatim. Verify the
  body starts with `<!DOCTYPE`/`<html` and is >20k chars BEFORE sending. One email only — no
  CORRECTION follow-ups (see `sender.md` Email rules).
- `to`:
  ```json
  [ {"address":"management@chaw.co.th","name":"CHAW Management"},
    {"address":"khiang@chaw.co.th","name":"Khiang Team"},
    {"address":"Franchisebusiness.div@zengroup.co.th","name":"Franchise Business Division"} ]
  ```
  > manual-test mode overrides `to` → owner only (vichit@chaw.co.th).
- Subject: `{target_icon} [Khiang] Daily Sales Report — {report_date_display} | ฿{net_sales} ({signed_pct}%)`
  - target_icon: 🔥 ≥฿50,000 · ✅ ฿40,000–50,000 · ⚠️ <฿40,000

## GROUP  (fires daily — sales digest)
- chat_id (primary): Khiang `oc_98ff051dc62904235c4743f69d9e4dba`
- chat_id (fallback): Quality `oc_1720a4005f44033a8ad78aa60a63216b`
- message (text):
```
📊 Khiang Daily Sales — {report_date_display} ({report_day_th})

สวัสดีทีม Khiang 🙏

ยอดขาย: ฿{net_sales} ({signed_pct}% vs target)
Avg ticket: ฿{avg_ticket} ({total_bills} bills)
MTD avg: ฿{avg_mtd}/day  ·  30d avg: ฿{avg_30d}/day

🍚 Top 10 เมนูข้าว (วาน):
{rice_top10_lines}

ขอบคุณครับ 🙏
```
- `rice_top10_lines`: one line per rice-menu item from the Top-10 Rice list, e.g.
  `1. K064 ข้าวกะเพราหมูสับ+ซุปใส — 37 (+12%)` → `{rank}. {itemid} {name} — {qty} ({badge_label})`.
  Build from the SAME data as the email's `top10_rice` repeat: Query B filtered to the FULL rice
  allow-list in `khiang-queries.md` — which INCLUDES the soup bundles K064–K077 (the main sellers
  since 2026-08-16) — ranked by qty. If fewer than 10 rice items sold, list what exists; if none,
  `"— ไม่มีข้อมูล"`.
- **HARD RULE: the 🍚 Top 10 block is REQUIRED in every group message.** Never omit the section.
  Before sending, verify the message contains the `🍚 Top 10 เมนูข้าว` header AND at least 1 line
  under it (or the explicit `— ไม่มีข้อมูล`). If `rice_top10_lines` came out empty while `top10_rice`
  in the email has rows, the filter list is wrong — rebuild from the full allow-list, do not send
  the digest without it.
- Fires every day regardless of `anomaly_count`. If the digest send fails on primary, retry fallback.

### GROUP message 2 — Liberty digest (send as a SEPARATE second message, same chat, right after msg 1)
```
🏙 Khiang Liberty Square — {report_date_display} ({report_day_th})

ยอดขาย: ฿{lib_net_sales} ({lib_signed_pct}% vs 7d avg ฿{lib_avg_7d})
Avg ticket: ฿{lib_avg_ticket} ({lib_bills} bills)
Peak 11–14: ฿{lw_peak_rev}  ·  Evening 17–21: ฿{lw_eve_rev}
ไข่ add-on: {lw_egg_attach}% ของบิล

🍽 Top 5 เมนู (วาน):
{lib_top5_lines}

ขอบคุณครับ 🙏
```
- `lib_top5_lines`: same format as rice_top10_lines, built from the `lib_top5` repeat
  (`{rank}. {itemid} {name} — {qty}`). If none, `"— ไม่มีข้อมูล"`.
- Both group messages are REQUIRED daily. If Liberty has zero data, still send message 2 with
  "— ไม่มีข้อมูล" (soft-fail rule) — never skip silently.

> NOTE: `report_day_th` (Thai weekday) is derived from REPORT_DATE in the routine.
> Anomalies are NOT mentioned in this message anymore — they live in the email (alert banner + hourly
> table). The group message is a clean daily sales digest.

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
