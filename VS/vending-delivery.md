# vending-delivery.md — Channels + recipients + content for the Vending Daily report

The mechanics live in `../sender.md`; the routing engine lives in `../method.md`; the people IDs
live in `../contacts.md`. This file is just this report's *choices* and *content*.

---

## Delivery declaration

```
Delivery:
  Channels: email + task + group
  Fire task only if: problem_machine_count > 0
  Fire group only if: total_rev_d1 > 0
  Email key: [Vending] Daily Sales — {report_date_display}
```

- **`email`** — always fires (subject to idempotency + completeness gates from method.md).
- **`task`** — only fires if at least one machine landed in the Problem table.
- **`group`** — only fires on a real-data day. Silent on a no-sale day (idempotency would've caught
  most of those already, but the gate is a belt-and-braces check).

---

## Email content

```yaml
EMAIL:
  to:
    - management@chaw.co.th        # contacts.management_email
    - vendi@chaw.co.th             # contacts.vendi_email
  to_test:
    - vichit@chaw.co.th            # contacts.vichit_email — used when RUN_MODE=manual-test
  cc: []
  subject_pattern: "{status_emoji} Vending Daily — {report_date_display} | ฿{total_k}K (WoW {wow_signed}%) | {service_ticket_count} service tickets"
  body_source: out.html             # produced by fill_template.py
  body_type: html
```

### Subject status emoji logic

| Condition | Emoji |
|---|---|
| any machine severity = `CRITICAL` OR (≥ 2 machines with `NEW LOW` mtd_flag) | 🚨 |
| total WoW < −5% | ⚠️ |
| total WoW ≥ −5% AND total WoW ≤ +10% | ✅ |
| total WoW > +10% AND no critical flags | 🔥 |

The emoji is computed in step 7 (data.json build) and emitted as the `status_emoji` scalar.

---

## Task content

One **service ticket per Problem machine** (the per-machine consolidation rule from runbook §10). All
tickets share the same assignee + follower configuration.

```yaml
TASK:
  per_machine: true                # one task per Problem machine
  assignees:
    - contacts.qt_sarun
    - contacts.qt_ploynaphat
    - contacts.qt_surachai
  followers:                       # added in separate lark_add_task_members calls
    - contacts.vichit
    - contacts.aekkaphop
  due_pattern: "{D1_plus_1}T17:00:00+07:00"   # next-business-day 5pm ICT
  summary_pattern: "🔧 Service — {machine_id} ({airport}) · {trigger_label} · {report_date_display}"
  description_template: |
    Machine: {machine_id} ({airport}) — {bu}
    D1 total: ฿{d1:,.0f}  ·  D8 baseline: ฿{d8:,.0f}  ·  MTD avg: ฿{mtd_avg:,.0f}
    Flag: {severity} · {mtd_flag}

    Trigger(s) on this machine ({n_triggers}):
    {trigger_lines}

    What to check on-site:
    • Machine power + display status (any error code on screen?)
    • Cash / cashless payment terminal — print test receipt
    • Stock level per shelf — note any SKU at zero
    • Coin / note mech jam, bill validator status
    • Telemetry / DEX last-sync timestamp
    • Surrounding foot traffic (closure, construction, event nearby?)

    Deliverable: brief findings + photos, reply on this task by EOD.
    If restock needed, log SKUs + qty.

    Source: Vending Daily Report v1.0 · {report_date_display}
```

### Trigger label decision tree (used to fill `trigger_label` in `summary_pattern`)

In order of priority (first match wins, single label per task title):

1. `D1_bills == 0 AND D8_bills ≥ MIN_BILLS_m` → `"Zero-sale day"`
2. `wow_pct ≤ -50%` → `"−{wow}% WoW"` (e.g. `"−65% WoW"`)
3. `mtd_flag == "🚨 NEW LOW"` → `"MTD new low"`
4. `wow_pct ≤ -10%` → `"−{wow}% WoW"`
5. `mtd_flag == "🚨 <80% avg"` → `"<80% MTD avg"`
6. else (only WATCH-level fired) → `"Monitor"`

### Trigger-lines builder (fills `{trigger_lines}` in the description, one bullet per applicable trigger)

```
• ZERO-SALE DAY — D1 0 vends vs D8 baseline {d8_bills} vends. Machine likely offline / unplugged / jammed.
• MAJOR DROP — D1 ฿{d1} vs D8 ฿{d8} (−{drop_pct}%). Partial outage, stockout, or terminal fault.
• STOCKOUT SUSPECT — D1 ฿{d1} vs MTD avg ฿{mtd_avg} ({pct_of_avg}%) for {streak} consecutive days.
• MTD NEW LOW — D1 ฿{d1} is the worst day of this month.
```

Only include bullets for triggers that fired on this machine. If no triggers fired but the machine
is still in the Problem list (WATCH from −5% < WoW < −10% with DoD positive), emit one fallback line:
`• WATCH — WoW {wow_signed}% but no acute trigger fired; verify in next 24h.`

---

## Group content

```yaml
GROUP:
  chat_id: contacts.food_operation_core      # oc_f25274999f6561e6f1e484102ee198e7
  fallback_chat_id: null                     # no fallback configured yet
  msg_type: text
  message_template: |
    🥤 Vending Daily Report — {report_date_weekday_th} {report_date_display}
    💰 Total Revenue: ฿{total_rev_d1:,.0f} (WoW {wow_signed}% · vs MTD avg {mtd_vs_signed}%)
    🏆 Top BU: {hero_bu} {hero_bu_wow_signed}% WoW · {hero_bu_reason}
    🚨 Crisis BUs: {crisis_bu_list_or_none}
    🔧 Machines flagged: {problem_machine_count}
       • Zero-sale day: {zero_sale_count}
       • Major drop: {major_drop_count}
       • MTD new low: {new_low_count}
    📨 Full report → emailed to management@chaw.co.th + vendi@chaw.co.th

    ━━━━ Service Tickets ({service_ticket_count}) ━━━━
    {for each task created in Channel 2 step:}
    {severity_emoji} {task_summary}
      👤 Quality Team (Sarun + Ploynaphat + Surachai) | Due {task_due_display}
      🔗 {task_url}

    CC: @vichit + @aekkaphop (universal followers on all Vending tickets)
```

**Build order**: this message is assembled AFTER Channel 2 (tasks) finishes — it embeds the
`task_url` returned by each `lark_create_task` call. If tasks fired but the group post fails, the
URLs are still in the email body's Next Actions table; nothing is lost.

---

## Mode behaviour summary

| Mode | Email | Tasks | Group |
|---|---|---|---|
| `scheduled` (default) | full `to` list | gated (yes if problems) | gated (yes if non-zero) |
| `manual-test` | `to_test` only | NOT created (rendered in email body as preview) | NOT posted |
| `manual-live` | full `to` list | gated (yes if problems) | gated (yes if non-zero) |

---

## Subject line examples

- `🔥 Vending Daily — 25 May 2026 | ฿355K (WoW +11.4%) | 7 service tickets`
- `⚠️ Vending Daily — 12 May 2026 | ฿293K (WoW −5.4%) | 3 service tickets`
- `✅ Vending Daily — 03 May 2026 | ฿440K (WoW +2.1%) | 0 service tickets`
- `🚨 Vending Daily — 18 Apr 2026 | ฿180K (WoW −24.1%) | 4 service tickets`
