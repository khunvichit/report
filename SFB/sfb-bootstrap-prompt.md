# SFB Daily Report — Routine Bootstrap Prompt

> Paste this (the block below) into the routine config prompt box once, then never touch it again.
> All real logic lives in `SFB/sfb-routine-prompt.md`.

```
Read SFB/sfb-routine-prompt.md from the repo and execute every step in it exactly, in order.
Run unattended — no approval prompts. Use the attached Chaw Netsuite (Read-only) and Lark connectors.
Default mode: scheduled (report date = yesterday, Asia/Bangkok).
```

## Trigger-line variants (optional)

- `Run SFB daily report` → scheduled, report date = yesterday (BKK).
- `Run SFB daily report for D1=YYYY-MM-DD` → manual-live back-fill.
- `Run SFB daily report in TEST mode` → manual-test (email owner only, skip group).

## Notes

- Connectors (NetSuite + Lark) must be attached to the **routine itself**, not just your session.
- First run in `manual-test` mode; only switch to `scheduled` after a clean run.
