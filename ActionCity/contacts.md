# contacts.md — recurring people / groups (shared)

Resolve each once; delivery files reference by name. Edit here to update everywhere.

## Owner
- **vichit@sfb.co.th** — report owner / failure DM target / manual-test recipient.

## actioncity_daily (email recipients)
- management@actioncity.co.th
- may@chaw.co.th
- panu@chaw.co.th

## actioncity_ops_group (Lark group for the daily card + failure notices)
- **chat_id:** `oc_4dabe0f3436e1201813c8cea6e38dbb1` — "ActionCity TH" (resolved via `lark_list_chats` on 24 Jul 2026).
  Note: the bot currently lacks `im:message.group_msg` read scope, so it can post but cannot read this
  chat's history (relevant if group history is ever used as an idempotency proxy).
- **fallback chat_id:** `<TO RESOLVE>` — a second group or owner DM as backup.

## Notes
- Open IDs / chat IDs are resolved with `lark_batch_get_user_id` (email→open_id) and `lark_list_chats`.
  Do this ONCE during deploy and hardcode the resolved IDs here.
- Secrets (connector tokens) are NEVER in this file — they come from the routine's attached connectors.
