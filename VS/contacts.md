# contacts.md — Recurring people & groups (shared)

Resolve each open_id / chat_id / email once. Per-report delivery files reference these by name
(e.g. `${contacts.vichit.open_id}`) instead of hard-coding the ID. Editing this file updates every
report that mentions a person.

BU-specific people who appear in only one report stay inline in that report's delivery file.

---

## Standing email recipients

| Key | Value | Purpose |
|---|---|---|
| `management_email` | `management@chaw.co.th` | CHAW exec distribution — all daily reports |
| `vichit_email` | `vichit@chaw.co.th` | Owner / CC oversight / `manual-test` recipient |
| `vendi_email` | `vendi@chaw.co.th` | Vending Services daily report recipient |
| `operationsfb_email` | `operationsfb@chaw.co.th` | SFB Food Operations daily report recipient |

---

## Quality Team (CCTV / service ticket assignees — shared across SFB + Vending)

The same three people review CCTV / service tickets for every CHAW BU report.

| Key | Name | Email | open_id |
|---|---|---|---|
| `qt_sarun` | Sarun | sarun@chaw.co.th | `ou_e521461e04d698168412f3c4f9a199d4` |
| `qt_ploynaphat` | Ploynaphat | ploynapat@chaw.co.th | `ou_dffd3de6811a4bad31d2f5398dd277b9` |
| `qt_surachai` | Surachai | surachai@chaw.co.th | `ou_bde920ede39cc83312cd0dd85ad0473c` |

When a report needs to co-assign all three to a task, declare assignees as `[qt_sarun, qt_ploynaphat, qt_surachai]`.

---

## Owners & cross-BU followers

| Key | Name | Email | open_id | Role |
|---|---|---|---|---|
| `vichit` | Vichit | vichit@chaw.co.th | `ou_434e5b57a3d9250d73110111104add49` | Universal follower (every report) |
| `tippawan` | Tippawan | — | `ou_e172ea0113db05470a44aa25b9931474` | SFB-only follower (Sub 12 reports) |
| `aekkaphop` | Aekkaphop | aekkaphop@chaw.co.th | `ou_96f0924ec4ff77e0874469cba58c42a5` | Vending follower + SVB Area Mgr |
| `siraphop` | Siraphop | siraphop@chaw.co.th | `ou_6b3dcef3a0fbd00d4b27fa828c882915` | DMK Area Mgr (Vending) |
| `sarinprapa` | Sarinprapa | sarinprapa@chaw.co.th | `ou_855578c2b2f96a2fecade148559cdbb5` | SFB Area Mgr BKK/PKT |
| `rodsukhon` | Rodsukhon | rodsukhon@chaw.co.th | `ou_12e4f2103b0b349b019075e8cffde1bc` | SFB Area Mgr DMK |

---

## Lark group chat IDs

| Key | Name | chat_id | Used by |
|---|---|---|---|
| `food_operation_core` | Food Operation Core | `oc_f25274999f6561e6f1e484102ee198e7` | SFB daily, Vending daily |

---

## Per-report follower convention

| Report | Universal followers |
|---|---|
| SFB (Sub 12) | `tippawan` + `vichit` |
| Vending (Sub 13) | `vichit` + `aekkaphop` |

This is the only difference in follower routing between reports. Delivery files declare which pair
to use; `sender.md` does the actual `lark_add_task_members` calls.
