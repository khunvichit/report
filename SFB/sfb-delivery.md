# SFB Daily — Delivery (this report's channel CHOICE + CONTENT)

Mechanics live in shared `sender.md`; routing/gating/Modes in shared `method.md`. This file only
declares what THIS report sends. **Lark TASKS are disabled** (owner request 2026-06) — no task channel.

```
Delivery:
  Channels: email + group         # task channel intentionally OFF
  Fire group only if: always       # daily heartbeat; group always posts in scheduled mode
  Email key: [SFB] Daily — {report_date_display}    # idempotency: search sent-mail for this before send
```

## EMAIL

- **to (scheduled / manual-live):**
  - management@chaw.co.th
  - operationsfb@chaw.co.th
- **to (manual-test):** owner only — set the owner address as a routine env var `OWNER_EMAIL`
  (do NOT hardcode a personal address in the repo).
- **subject** (computed):
  ```
  {status_emoji} SFB Daily — {report_date_display} | {rev_K} (WoW {wow_signed}) | {loc_count} locations
  ```
  status_emoji: 🚨 if any CRITICAL severity · ⚠️ if total WoW < −5% · 🔥 if WoW > +10% and no CRITICAL · else ✅
  ({loc_count} = distinct selling locations on D1; severity is still computed internally for status_emoji
  and the heatmap, just not surfaced as a "problem branches" count now that the branch table is gone.)
- **body:** contents of `email.html` produced by `fill_template.py sfb-template.html data.json`.
  The model never emits the HTML; it passes the file contents to `lark_send_email`.

## GROUP

- **chat_id (primary):** `oc_f25274999f6561e6f1e484102ee198e7`  — Food Operation Core
- **fallback:** owner DM (env `OWNER_OPEN_ID`) if the group send fails.
- **message** (plain text; Lark auto-appends its AI disclaimer — don't duplicate it):
  ```
  📊 SFB Daily Report — {weekday_th} {report_date_display}
  💰 Total Revenue: {rev_baht} (WoW {wow_signed} · vs MTD avg {mtd_signed})
  📈 Bills {bills_total} · Avg ticket {ticket}
  🏆 Top movers (location × BU):
  {top_movers_block}
  🔻 Weakest (location × BU):
  {bottom_movers_block}
  📨 Full report → emailed to management@chaw.co.th + operationsfb@chaw.co.th
  ```

  Movers are taken from the same location×BU rows as the email heatmap (rev Δ WoW = D1 vs D8).
  - `top_movers_block`: top 3 location×BU rows by rev WoW, each line:
    `  • {location} · {bu_name} {rev_delta} ({d1_rev})`
  - `bottom_movers_block`: bottom 3 by rev WoW, same line format.
  - If fewer than 3 rows exist on a side, list what there is. No BU-level aggregate, no
    problem-branch count, no replicate list (those have no backing detail in the current email).

## TASK — DISABLED

Task channel is OFF. The old per-branch CCTV Lark tasks are not created. Location×BU performance is
conveyed in the email heatmap and the group message's top/weakest movers. To re-enable later, add
`task` to the Channels line and restore a TASK block here (assignees/followers + open_ids).
