# contacts.md — recurring people / groups (shared)

Resolve each once; delivery files reference by name. Edit here to update everywhere.

## Owner
- **vichit@sfb.co.th** — report owner / failure DM target / manual-test recipient.

## actioncity_daily (email recipients)
- management@actioncity.co.th
- may@chaw.co.th
- panu@chaw.co.th

## actioncity_ops_group (Lark group for the daily card + failure notices)
- **chat_id:** `<TO RESOLVE>` — run `lark_list_chats`, find the ActionCity ops/management group, paste the `chat_id`.
- **fallback chat_id:** `<TO RESOLVE>` — a second group or owner DM as backup.

## Notes
- Open IDs / chat IDs are resolved with `lark_batch_get_user_id` (email→open_id) and `lark_list_chats`.
  Do this ONCE during deploy and hardcode the resolved IDs here.
- Secrets (connector tokens) are NEVER in this file — they come from the routine's attached connectors.
