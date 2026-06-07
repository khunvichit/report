# Juiceland Daily Sales Report — Delivery section (rewritten)

This replaces the old **Steps 5, 6, 7** in the Juiceland runbook.
Steps 0–4 (branding, dates, queries, KPIs) and Step 8 (console) are unchanged.
Mechanics now live in the shared files — this section only declares channels + supplies content.

References: `sender.md` · `method.md`

---

## Delivery

```
Channels: email + task + group
Fire task + group only if: am_queue_count + dormant_count > 0
Email key: [Juiceland] Daily Sales Report — {report_date_display}
```

Follow `method.md` for order of operations and gating; `sender.md` for each channel's mechanics.

---

### EMAIL content

- **to:**
  - `juiceland@chaw.co.th` — Juiceland Team
  - `management@chaw.co.th` — CHAW Management
- **subject:** `{subject_prefix} [Juiceland] Daily Sales Report — {report_date_display} | ฿{comb_net} ({signed_pct}%)`
- **html_body:** built from `juiceland-template.html` + query data (per `juiceland-queries.md`).

---

### LARK TASK content  *(gated: am+dormant > 0)*

- **summary:** `📋 [Juiceland {DD MMM}] AM Review — {am_queue_count} new-product items + {dormant_count} dormant SKUs`
- **due:** standard rule (`{report_date + 1} 17:00 +07:00`)
- **assignees:** Sarun, Ploynapat  *(open_ids in sender.md)*
- **followers:** Vichit
- **description:**
```
สรุปยอดขาย Juiceland วันที่ {report_date_display} ({report_day_th})

📊 ยอดขายรวม 3 สาขา: ฿{comb_net} ex-VAT ({signed_pct}% vs 30d avg)
- MW1: ฿{mw1_net} · {mw1_bills} bills · {mw1_vs_30d}%
- SE3: ฿{se3_net} · {se3_bills} bills · {se3_vs_30d}%
- PKT: ฿{pkt_net} · {pkt_bills} bills · {pkt_vs_30d}%

🚨 AM Review Required ({am_queue_count} items):
{for each AM-review item}
- [ ] {memo} — {system_hypothesis}
  Last sold {last_sold} ({gap}d ago) · 7d avg {velocity:.1f}/day vs target {target}
  ☐ Stock-out  ☐ Low demand  ☐ Reduced batch  ☐ Other: ____

🚫 Dormant SKUs ({dormant_count} items, no sales in 7+ days):
{for each dormant item, grouped by branch}
- {branch}: {memo} — last {last_sold} ({gap}d) · was {qty_30d}u/{days_sold_30d}d (฿{rev_30d})

📋 Please reply within 24 h.
Data source: NetSuite POS · Class 3 (Juice Land) · Locations 33, 105, 109
```

---

### LARK GROUP content  *(gated: am+dormant > 0)*

- **chat_id:** Quality (primary) → Food Operation Core (fallback)  *(ids in sender.md)*
- **message:**
```
🧃 Juiceland Daily Summary — {report_date_display} ({report_day_th})

📊 ยอดขายรวม: ฿{comb_net} ex-VAT ({signed_pct}% vs 30d avg)
- MW1: ฿{mw1_net} ({mw1_vs_30d}%)
- SE3: ฿{se3_net} ({se3_vs_30d}%)
- PKT: ฿{pkt_net} ({pkt_vs_30d}%)

🆕 New Product Launches:
- 🥤 Drinks ({drinks_n} SKUs): {drinks_yest}u / ฿{drinks_yest_rev} yest
- 🍉 Seasonal Fruits ({fruit_n} SKUs): {fruit_yest}u / ฿{fruit_yest_rev} yest
- ⭐ New Category ({new_cat_n} SKUs): {new_cat_yest}u / ฿{new_cat_yest_rev} yest

🚨 AM Review: {am_queue_count} items · 🚫 Dormant SKUs: {dormant_count} items

📋 Lark Task: https://applink.larksuite.com/client/todo/detail?guid={task_guid}

กรุณาตรวจสอบและ reply ภายใน 24 ชม. ขอบคุณครับ 🙏
```

---

### Example: a different report's Delivery block

An email-only report (no task, no group) would declare just:
```
Delivery:
  Channels: email
  Email key: [ActionCity] Weekly Sales — {week_label}
```
and supply only the EMAIL content block. Same sender.md / method.md, no changes.
