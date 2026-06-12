# ActionCity Daily Report — routine files

Automated **daily end-of-day** (~22:00 Asia/Bangkok) sales & stock dashboard for ActionCity
(NetSuite Sub 22), delivered by **Lark email + group**. Built the CHAW way: single-purpose files the
routine reads and fills with code — never regenerates from prose.

## What's here

```
actioncity_report_routine/
  sender.md          ← shared: 3-channel mechanics
  method.md          ← shared: routing / gating / modes
  branding.md        ← shared: CHAW/ActionCity CI (confirm vs chaw-branding skill)
  contacts.md        ← shared: recipients + group chat_id (RESOLVE chat_ids before go-live)
  ActionCity/
    actioncity-template.html     ← LOCKED layout (tokens / REPEAT / SECTION) — never regenerate
    actioncity-queries.md        ← SuiteQL per token, fixed params, BKK dates, completeness checks
    actioncity-prediction.md     ← exec-insight method + rule-based flags/colours (guardrailed)
    actioncity-delivery.md       ← channels (email+group), recipients, subject, group card
    actioncity-routine-prompt.md ← THE FULL INSTRUCTION SET the routine executes
    fill_template.py             ← assembles HTML from template + data.json (no model HTML output)
    sample-data.json             ← example data.json (real W23 numbers) for testing
    sample-email.html            ← example rendered output (from the sample)
```

## Why it can't go stale (always live data)

Freshness is structural, then guarded:
1. **The template has no numbers** — only `{{tokens}}`. `preflight_check.py lint` fails the run if any money literal is baked in.
2. **`data.json` is rebuilt every run** from live SuiteQL, and the routine deletes any leftover data.json/email.html first — it never reuses yesterday's. No committed data file in the repo.
3. **Dates are computed at runtime** (Asia/Bangkok), so windows always roll forward.
4. **Freshness self-check before send:** `preflight_check.py fresh data.json <today>` asserts `report_date_display == today` and that key data loaded; then a **control-total recheck** re-queries today's net and asserts it equals `data.json`'s value. Mismatch → hard stop.
5. **Completeness gates** stop a zero/partial day instead of sending stale-looking zeros.
6. **The report stamps `generated_at` + trading day** in the footer, so any reader can see the data date at a glance.

The "static carrying" you saw earlier only happened because I hand-assembled a one-off render and reused some numbers. The scheduled routine re-queries **every** section in the same run, so all sections share one `generated_at` and nothing is carried.

## The one rule that fixes the drift you saw

**Net sales = `-SUM(tl.netamount)`** (invoices − returns). The old `SUM(ABS(netamount))` *added*
returns back — that's why W22 read ฿452.9K instead of the true ฿356.9K (it had ฿48K of returns).
Plus `netamount<>0` to drop the vending/marketplace cost-wash lines. Both are pinned in `queries.md`.

## Deploy (produce-files-only → you wire it up)

1. **Create a private GitHub repo** (e.g. `chaw/report-routines`). Copy these files in, keeping the
   structure above (shared at root, `ActionCity/` folder). Shared files are reused by future BU reports.
2. **Resolve IDs once** and paste into `contacts.md`: run `lark_list_chats` for the ActionCity ops
   group `chat_id` (+ a fallback). Confirm the CCHAW footer wording from the `chaw-branding` skill into `branding.md`.
3. **Create the Claude routine.** Attach the **NetSuite + Lark connectors to the routine itself**.
   Set the prompt box to the one-line bootstrap:
   ```
   Read ActionCity/actioncity-routine-prompt.md from the repo and execute every step in it exactly,
   in order. Run unattended — no approval prompts. Use the attached NetSuite and Lark connectors.
   ```
4. **Validate in `manual-test` first** (set env `MODE=manual-test`): Run-now. Confirm — files read,
   `report_date` = today Asia/Bangkok, queries return data, completeness passes, `fill_template.py`
   gives clean HTML (no `{{tokens}}`), per-branch rows fill, **email arrives to owner only, group skipped**.
5. **Schedule** once a manual-test run is clean: daily trigger **22:00 Asia/Bangkok**, `MODE=scheduled`.
   Keep watching the first ~1–2 weeks before widening recipients.

## Test it locally (already verified)
```
cd ActionCity
python3 fill_template.py actioncity-template.html sample-data.json > sample-email.html
# 0 unresolved tokens; open sample-email.html to preview the layout.
```

## Notes / open items
- **EOD timing:** this routine reports TODAY (the closing day), not yesterday. The completeness check
  hard-stops if today has no posted rows yet (POS lag) — so a too-early run won't send zeros. If the
  POS feed regularly lags past 22:00, either move the trigger later or switch `report_date` to
  yesterday in `queries.md` (one line, documented there).
- **Connectors expire:** cloud OAuth can drop — that's why the routine fails loud (posts to the group /
  DMs the owner) rather than retrying silently.
- **Adding more BU reports later:** new `<Brand>/` folder with its 5–6 files; the 4 shared root files
  are reused unchanged.
