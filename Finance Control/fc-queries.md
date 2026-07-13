# fc-queries.md — Finance Control data layer (NetSuite)

Maps every value in the report to its NetSuite source. The routine runs these, then writes the
results into `data.json` (it never hardcodes numbers). Changes here when NetSuite changes.

> Tool: `ns_runCustomSuiteQL` (read-only SuiteQL). Parameter name is `query`.
> Reports API `ns_runReport` (Bank Total 412, AR Aging 273) is the *preferred* source for cash and AR;
> if the Reports API tool is unavailable in the routine, fall back to the SuiteQL below (validated).
> Rate-limited: wait 20–90s between retries; run one subsidiary at a time; retry a failed query ONCE,
> never restart the whole routine.

## Fixed params (pin these — they silently wander)

- Subsidiaries: **SFB = 12, Vending = 13, ActionCity = 22**. Others seen in memorized txns:
  CHAW Mgmt 2, CHAW 5, Inbox 6, TOYzINBOX 7, CRT 19.
- Bank parent accounts: **SFB 257 (KBANK), 260 (SCB), 261 (KTB); Vending 263 (KBANK); ActionCity 984 (KBANK)**.
- Undue VAT accounts: **11101003 (Input VAT Undue, internal id 218)**, **21026002 (Output VAT Undue)**.
- Cash-Sales sub-account suffix: **A** for parents 257/260/261/263; **F** for parent 984.
- Subsidiary filter goes on `transactionline.subsidiary`, never the transaction header.

## Date logic — Asia/Bangkok, computed at runtime

- `report_date = now(Asia/Bangkok).date()` on the scheduled Monday run (weekly). Honour a manual
  `REPORT_DATE` override for back-fills. Never hardcode; never use server UTC.
- All "days since / days overdue / age" are measured against `report_date`.
- `date_str = report_date "%d %b %Y"`. Deliverable is HTML (the email body) — no filename needed.

## 1a. Cash position — bank + sub-account balances
```sql
SELECT a.id, a.acctnumber, a.accountsearchdisplayname, a.parent, NVL(a.balance,0) AS balance, a.accttype
FROM account a
WHERE a.id IN (257,260,261,263,984) OR a.parent IN (257,260,261,263,984)
ORDER BY a.parent NULLS FIRST, a.acctnumber
```
→ `data.banks` (parents) + `data.subs` (children). Subsidiary of each parent via `parent_sub`.

## 1b. AR aging + credit-term cross-check (run per subsidiary 12, 13, 22)
```sql
SELECT c.entityid, c.companyname, tm.name AS termName, tm.daysuntilnetdue AS termDays,
 SUM(t.foreignamountunpaid) AS openBal,
 SUM(CASE WHEN t.duedate >= TO_DATE('<report_date>','YYYY-MM-DD') THEN t.foreignamountunpaid ELSE 0 END) AS curAmt,
 SUM(CASE WHEN t.duedate <  TO_DATE('<report_date>','YYYY-MM-DD') THEN t.foreignamountunpaid ELSE 0 END) AS overdueAmt,
 MIN(t.duedate) AS oldestDue
FROM transaction t
JOIN customer c ON t.entity = c.id
LEFT JOIN term tm ON c.terms = tm.id
WHERE t.type='CustInvc' AND t.foreignamountunpaid > 0 AND c.subsidiary = <sub>
GROUP BY c.entityid, c.companyname, tm.name, tm.daysuntilnetdue
```
→ `data.AR[<sub>]`. For ActionCity, roll the many small current retail invoices into one
`ACT_other_count` / `ACT_other_amt` summary row to keep the sheet readable.

## 1d. Bank reconciliation (main accounts)
```sql
SELECT a.acctnumber, a.accountsearchdisplayname, MAX(tl.clearedDate) AS lastReconDate
FROM transactionline tl JOIN account a ON tl.account = a.id
WHERE tl.cleared = 'T' AND a.id IN (257,260,261,263,984)
GROUP BY a.acctnumber, a.accountsearchdisplayname
```
→ `data.recon`. Flag any account not reconciled within **30 days** of report_date as OVERDUE.

## 1e. Cash deposit verification — last automated-JV transfer per sub-account (run per parent set)
```sql
SELECT a.acctnumber, MAX(t.trandate) AS lastTransferDate
FROM transactionline tl
JOIN account a ON tl.account = a.id
JOIN transaction t ON tl.transaction = t.id
WHERE a.parent IN (<257 | 260,261 | 263 | 984>) AND tl.amount < 0
GROUP BY a.acctnumber
```
→ `data.transfer`. Benchmark: **Cash Sales = T+2, all other channels = T+3**. The sub-account balance
should only hold deposits inside the benchmark window. Verdict per sub-account (computed in
`fc_build_data.py`): OK / LATE (1–2d past) / OVERDUE (3–14d) / CRITICAL (14d+) / NEGATIVE / INACTIVE.
> NOTE: SFB parents 260/261 sub-account transfer query can time out — split or accept N/A; 261B (KTB Cash)
> may have a balance with no transfer date → mark "verify".

## 1f. Undue VAT — vendor reversal check (run per subsidiary, use account internal id 218)
Account balances:
```sql
SELECT a.acctnumber, a.accountsearchdisplayname, NVL(a.balance,0) AS balance
FROM account a WHERE a.acctnumber IN ('11101003','21026002')
```
Open balance by vendor:
```sql
SELECT e.entityid, SUM(tl.amount) AS openBalance, COUNT(*) AS txnCount,
       MIN(t.trandate) AS oldestDate, MAX(t.trandate) AS newestDate
FROM transaction t JOIN transactionline tl ON t.id = tl.transaction
LEFT JOIN entity e ON tl.entity = e.id
WHERE tl.account = 218 AND tl.subsidiary = <sub>
GROUP BY e.entityid HAVING SUM(tl.amount) != 0
```
Then look up vendor names: `SELECT entityid, companyname FROM vendor WHERE entityid IN (...)`.
**EXCLUDE** `Default Tax Agency TH` entries and NULL-entity rows. **Annotate** V-00313 (กรมสรรพากร /
Revenue Dept) as a VAT-clearing vendor — verify before treating as a staff error.
→ `data.VAT[<sub>]` (+ `vat_acct`, `vname`). Positive = NOT reversed; Negative = OVER-reversed.

## 1g. Memorized transactions — health check
```sql
SELECT md.id, md.name, md.nextDate, md.numberRemaining, md.repeatEvery,
       tt.abbrevType, tt.total, tt.subsidiary, tt.approvalStatus, tt.memo
FROM MemDoc md
LEFT JOIN memDocTransactionTemplate tt ON md.transactionTemplate = tt.id
WHERE md.isInactive='F' AND md.hasRemaining='T' AND md.nextDate IS NOT NULL
ORDER BY md.nextDate
```
→ `data.MEMO`. approvalStatus: 1 = Pending Approval, 2 = Approved. Group King Power (V-00040) overdue
entries into one summary row if 30+.

## 1h. Duplicate transactions (vendor bills, posted on/after 01 Jan of prior year)
Test 1 — exact (audit-grade):
```sql
SELECT tl.subsidiary, t.entity, ABS(t.foreigntotal) AS amt, t.otherrefnum AS ref, COUNT(*) AS cnt
FROM transaction t JOIN transactionline tl ON tl.transaction = t.id
WHERE t.type='VendBill' AND tl.mainline='T' AND tl.subsidiary IN (12,13,22)
AND t.otherrefnum IS NOT NULL AND t.foreigntotal IS NOT NULL
GROUP BY tl.subsidiary, t.entity, ABS(t.foreigntotal), t.otherrefnum HAVING COUNT(*) > 1
```
Test 2 — heuristic (same vendor + amount + date, amount ≥ 5,000):
```sql
SELECT tl.subsidiary, t.entity, ABS(t.foreigntotal) AS amt, t.trandate AS td, COUNT(*) AS cnt
FROM transaction t JOIN transactionline tl ON tl.transaction = t.id
WHERE t.type='VendBill' AND tl.mainline='T' AND tl.subsidiary IN (12,13,22)
AND t.foreigntotal IS NOT NULL AND ABS(t.foreigntotal) >= 5000
GROUP BY tl.subsidiary, t.entity, ABS(t.foreigntotal), t.trandate HAVING COUNT(*) > 1
```
> `ORDER BY` on a GROUP BY query 400s — sort client-side. Test 2 is noisy (recurring/multi-branch
> vendors): curate to the genuinely anomalous before writing `data.duplicates.review`.
→ `data.duplicates = {exact_count, cluster_count, review[]}`.

**Bill numbers (for traceability).** The GROUP BY tests give clusters, not document numbers. For each
flagged cluster, fetch the actual bill numbers so staff can open them directly:
```sql
SELECT tl.subsidiary, t.entity, t.tranid AS billno, t.trandate, ABS(t.foreigntotal) AS amt
FROM transaction t JOIN transactionline tl ON tl.transaction = t.id
WHERE t.type='VendBill' AND tl.mainline='T'
AND t.entity = <entityId> AND t.trandate = TO_DATE('<cluster_date>','YYYY-MM-DD')
ORDER BY t.tranid
```
Filter client-side to the cluster amount. Each `review[]` row carries a 9th field, `bills` — a short
list of the cluster's `tranid`s (e.g. `03022025, 03022025.` or `IR2025/0350-0361`). Near-identical bill
numbers (a trailing dot, consecutive numbers) are the strongest duplicate signal.

`data.duplicates.review[]` row shape:
`[sub, vendorId, vendorName, amount, date, count, assessment, priority, bills]`.

## Completeness checks — gate the send (HARD STOP on failure)
1. Cash query returned all 5 parent accounts + their sub-accounts.
2. AR query returned for each of subs 12/13/22 (zero rows for a sub is allowed → render 0).
3. Undue VAT + memorized + duplicate queries each returned (0 rows allowed, query error not allowed).
4. `report_date` resolved to today Asia/Bangkok (timezone guard).
5. On any query hard-failure after one retry → STOP, do not send, trigger the failure path.
