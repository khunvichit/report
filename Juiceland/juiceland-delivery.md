# Juiceland Daily Sales Report — Delivery section

Replaces old Steps 5–7. Steps 0–4 (branding, dates, queries, KPIs) and console step unchanged.
Mechanics live in the shared files — this section declares channels + supplies content.

References: `sender.md` · `method.md`

---

## Delivery

```
Channels: email + group          # Lark TASK disabled for now
Fire group only if: am_queue_count + dormant_count > 0
Email key: [Juiceland] Daily Sales Report — {report_date_display}
```

> NOTE: Lark task channel intentionally OFF. To re-enable later, add `task` back to Channels
> and restore the TASK content block (kept below, commented, so it's ready).

Follow `method.md` for order of operations and gating; `sender.md` for each channel's mechanics.

---

### EMAIL content  (always fires)

- **to:**
  - `juiceland@chaw.co.th` — Juiceland Team
  - `management@chaw.co.th` — CHAW Management
- **subject:** `{subject_prefix} [Juiceland] Daily Sales Report — {report_date_display} | ฿{comb_net} ({signed_pct}%)`
- **html_body:** built from `juiceland-template.html` via `fill_template.py` + query data.

---

### LARK GROUP content  (gated: am+dormant > 0)

- **group:** Juiceland  →  chat_id `__JUICELAND_CHAT_ID__`   ← REPLACE with real id
  - fallback: Food Operation Core `oc_f25274999f6561e6f1e484102ee198e7`
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

กรุณาตรวจสอบและ reply ภายใน 24 ชม. ขอบคุณครับ 🙏
```
> Note: task deep-link line removed (no task created while task channel is off).

---

### LARK TASK content  — DISABLED (kept for easy re-enable)

<!--
Channel: task  (gated: am+dormant > 0)
- summary: 📋 [Juiceland {DD MMM}] AM Review — {am_queue_count} items + {dormant_count} dormant SKUs
- due: {report_date + 1} 17:00 +07:00
- assignees: Sarun, Ploynapat   (open_ids in sender.md)
- followers: Vichit
- description: (full Thai task block — restore from git history / prior version)
-->
