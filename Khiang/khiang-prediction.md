# Khiang — Prediction & Anomaly (generative layer)

This is the ONLY file allowed to reason/vary. Queries return fixed numbers; this turns the hourly
data into anomaly flags + CCTV task content. Compute LAST (after actuals), display in the email.

## Signal: BILL COUNT, not revenue
Anomaly detection uses **bill count** vs benchmark — bills reflect customer flow / kitchen throughput;
revenue is skewed by a few large or small orders. The email *displays* revenue per hour (that is what
the rendered layout shows), but the flag/note on each hour is driven by bills.

### Hourly BILL-count benchmark (avg 9–19 Apr 2026; ~298 bills/day)
Provide the per-hour bill benchmark `HOURLY_BILL_BENCH` in the routine. If a calibrated per-hour bill
table is not available, derive it from the revenue benchmark below pro-rata to the day's avg ticket —
and label the anomaly note "(est. bench)" so a derived benchmark is never mistaken for measured.

### Hourly REVENUE benchmark (display only, avg 9–19 Apr 2026)
```
{0:1149,1:763,2:373,3:356,4:240,5:166,6:538,7:1636,8:1910,9:3223,10:3827,
 11:4673,12:5768,13:3631,14:4196,15:3000,16:3813,17:2969,18:3641,19:3069,
 20:3080,21:2162,22:1562,23:553}
```

## Flagging rule
For each hour h present in yesterday's data:
```
if actual_bills[h] < HOURLY_BILL_BENCH[h] * 0.50:   # >50% drop in customer flow
    flag h as anomaly
anomaly_count = number of flagged hours
```
`sections.alert_banner = anomaly_count > 0`
(The in-email CCTV action plan was removed AND the group message is now a plain daily digest.
Anomalies feed ONLY the email: the alert banner + the hourly table's `hour_flag`/`note` styling.
No `cctv_tasks` repeat is built, and the Khiang group message does NOT list anomalies.)

## Priority & issue type (bill-count based) — drives the hourly table's flag/note styling only
| Condition | Issue type | Priority | hourly note tag |
|-----------|-----------|----------|-----------------|
| bills < 5% of bench | Near-zero traffic | 🔴 Critical | 🔴 near-zero |
| 11–13h bills < 50% bench | Lunch peak collapse | 🔴 Critical | 🔴 collapsed |
| 09–10h bills < 50% bench | Pre-peak slowdown | 🟠 High | ⚠️ Low |
| 17–20h bills < 50% bench | Evening traffic dip | 🟠 High | ⚠️ Low |
| 21–23h bills < 50% bench | Early-closing suspected | 🟠 High | ⚠️ Low |
| any other hour < 50% bench | Low customer flow | 🟠 High | ⚠️ Low |

For each flagged hour: set `hour_flag = " 🚨"`, `row_bg = #FFEBEE`, and a short factual `note`.
`anomaly_count` (count of flagged hours) drives the alert banner only.

## GUARDRAILS (non-negotiable)
- **Describe, don't diagnose.** State what the data shows ("bills 88% below benchmark at 10:00").
  NEVER assert an unobserved cause ("staff left early", "ran out of pork") in the report — anomalies
  are flagged factually.
- **No invented numbers.** Every figure traces to a query result or a stated benchmark.
- The hourly table `note` is a short factual tag (✅ Normal / ⚠️ Low / 🔴 collapsed), bill-driven.
- If `anomaly_count == 0`: alert_banner section OFF. (The Khiang group digest still fires daily.)
