#!/usr/bin/env python3
"""fc_build_data.py — deterministic classifier: raw query data -> render.json.

Reads the raw NetSuite data the routine pulled (data.json shape == data.sample.json),
applies the fc-prediction.md thresholds in CODE (so two runs classify identically),
and writes render.json = { scalars, repeats, sections } for fill_template.py.

Usage:
    python3 fc_build_data.py data.json render.json
"""
import sys, json
from datetime import date

RAW = sys.argv[1] if len(sys.argv) > 1 else "data.json"
OUT = sys.argv[2] if len(sys.argv) > 2 else "render.json"
D = json.load(open(RAW, encoding="utf-8"))

TODAY = date.fromisoformat(D["meta"]["report_date"])
def dp(s):
    dd, mm, yy = s.split('/'); return date(int(yy), int(mm), int(dd))
def dsince(s): return (TODAY - dp(s)).days
def money(x): return f"{x:,.0f}"
def money2(x): return f"{x:,.2f}"

# palette (hex with #)
# CHAW-harmonised status tints (chrome colours live in fc-template.html)
NAVY="#5551FE"; BLUE="#5551FE"; LIGHT="#F5EDE4"; GRAY="#F5F5F5"
RED="#FBE4E0"; AMBER="#FFF3E0"; GREEN="#E8F5E9"; ORANGE="#F8C8C0"; WHITE="#FFFFFF"
SUB = {12:"SFB",13:"Vending",22:"ActionCity"}
SUBORDER = {"SFB":0,"Vending":1,"ActionCity":2}
AR_RANK = {"CRITICAL":0,"PAST TERMS":1,"WATCH":2,"OK":3}
VRANK = {"CRITICAL":0,"NEGATIVE":1,"OVERDUE":2,"LATE":3,"INACTIVE":4,"OK":5}
SEV_RANK = {"URGENT":0,"CRITICAL":0,"HIGH":1,"PAST TERMS":2,"WATCH":3,"MEDIUM":2,"LOW":4,"OK":5,"ACTION":2}
PRI_RANK = {"HIGH":0,"REVIEW":1,"LOW":2}
MEMO_SUB = {2:"CHAW Mgmt",5:"CHAW",6:"Inbox",7:"TOYzINBOX",12:"SFB",13:"Vending",19:"CRT",22:"ActionCity"}

parent_sub = {int(k):v for k,v in D["parent_sub"].items()}
banks = D["banks"]                       # [id, acctno, name, bal]
subs  = [tuple(s) for s in D["subs"]]    # [acctno, channel, parent, bal]
transfer = D["transfer"]
recon = D["recon"]; recon_oldest = {int(k):v for k,v in D["recon_oldest"].items()}
recon_sub = {k:int(v) for k,v in D["recon_sub"].items()}
AR = {int(s):[tuple(r) for r in rows] for s,rows in D["AR"].items()}
ACT_other_count = D["ACT_other_count"]; ACT_other_amt = D["ACT_other_amt"]
vat_acct = {k:tuple(v) for k,v in D["vat_acct"].items()}
vname = D["vname"]
def vn(e): return vname.get(e, e) if e else "(no entity)"
VAT = {int(s):[tuple(r) for r in rows] for s,rows in D["VAT"].items()}
MEMO = [tuple(m) for m in D["MEMO"]]
DUP = D["duplicates"]

scalars={}; repeats={}; sections={}

# ---------- CASH + AR overview ----------
cash={s:0.0 for s in SUB}; subbal={s:0.0 for s in SUB}
for b in banks: cash[parent_sub[b[0]]]+=b[3]
for an,ch,pid,bal in subs:
    cash[parent_sub[pid]]+=bal; subbal[parent_sub[pid]]+=bal
def ar_tot(s): return sum(r[4] for r in AR[s]) + (ACT_other_amt if s==22 else 0)
def ar_cur(s): return sum(r[5] for r in AR[s]) + (ACT_other_amt if s==22 else 0)
def ar_over(s): return sum(r[6] for r in AR[s])
ar_total_all=sum(ar_tot(s) for s in SUB); ar_cur_all=sum(ar_cur(s) for s in SUB); ar_over_all=sum(ar_over(s) for s in SUB)

overview=[]
for s in SUB:
    rd=recon_oldest[s]; rds=dsince(rd); rbg=RED if rds>30 else GREEN
    overview.append({"sub_name":SUB[s],"cash":money(cash[s]),"ar_total":money(ar_tot(s)),
        "ar_current":money(ar_cur(s)),"ar_overdue":money(ar_over(s)),
        "pct":f"{(ar_over(s)/ar_tot(s)*100 if ar_tot(s) else 0):.1f}",
        "subacct":money(subbal[s]),"recon_txt":f"{rd} ({rds}d)","recon_bg":rbg})
repeats["overview_rows"]=overview
scalars.update(cash_total=money(sum(cash.values())), subacct_total=money(sum(subbal.values())),
    ar_total_all=money(ar_total_all), ar_current_all=money(ar_cur_all), ar_overdue_all=money(ar_over_all),
    cash_sfb=money(cash[12]), cash_ven=money(cash[13]), cash_act=money(cash[22]),
    ar_total=money(ar_total_all), ar_overdue=money(ar_over_all),
    ar_pct=f"{ar_over_all/ar_total_all*100:.1f}")

# ---------- Undue VAT account balances ----------
repeats["vat_acct_rows"]=[{"acct":k,"desc":v[0],"bal":money2(v[1])} for k,v in vat_acct.items()]

# ---------- recon alert ----------
worst=max(dsince(recon_oldest[s]) for s in SUB)
sections["recon_alert"]=worst>=20
scalars["recon_note"]=("Bank recon OK (SFB KBANK/SCB at %dd, monitor)"%max(dsince(recon_oldest[12]),0)
    if worst<=30 else "Bank recon OVERDUE on one or more accounts (>30d)")

# ---------- Top risks + actions ----------
SEVBG={"CRITICAL":RED,"HIGH":ORANGE,"PAST TERMS":AMBER,"WATCH":AMBER,"ACTION":LIGHT,"URGENT":RED}
_risks=sorted(D["exec_risks"],key=lambda r:SEV_RANK.get(r[4],9))[:10]
repeats["risk_rows"]=[{"n":str(i+1),"area":r[0],"item":r[1],"detail":r[2],
    "amount":money(abs(r[3])) if r[3] else "—","severity":r[4],"sev_bg":SEVBG.get(r[4],GRAY)}
    for i,r in enumerate(_risks)]
acts=D["priority_actions"]
repeats["action_rows"]=[{"sev":a[0],"sev_bg":SEVBG.get(a[0],LIGHT),"text":a[1]} for a in sorted(acts,key=lambda a:SEV_RANK.get(a[0],9))]
for i in range(3):
    scalars["action%d"%(i+1)]=acts[i][1] if i<len(acts) else ""

# ---------- AR detail (overdue rows + per-sub subtotal + ACT current summary) ----------
def days_overdue(odue): return max(0,(TODAY-dp(odue)).days)
def credit_status(td,odue,ov):
    if ov<=0: return ("OK",GREEN)
    od=days_overdue(odue)
    if od>2*td: return ("CRITICAL",RED)
    if od>td: return ("PAST TERMS",ORANGE)
    if od>=td-5: return ("WATCH",AMBER)
    return ("OK",GREEN)
ar_rows=[]
for s in SUB:
    rows=sorted(AR[s],key=lambda x:(AR_RANK[credit_status(x[3],x[7],x[6])[0]], -x[6], -x[4]))
    for eid,nm,term,td,ob,cu,ov,odue in rows:
        st,bg=credit_status(td,odue,ov)
        ar_rows.append({"sub_name":SUB[s],"customer":nm,"term_days":str(td),"open":money(ob),
            "current":money(cu),"overdue":money(ov),"days_od":str(days_overdue(odue) if ov>0 else 0),
            "status":st,"status_bg":bg,"row_bg":WHITE,"weight":"normal"})
    if s==22:
        ar_rows.append({"sub_name":"ActionCity","customer":f"(+{ACT_other_count} current retail invoices, due Jul)",
            "term_days":"30","open":money(ACT_other_amt),"current":money(ACT_other_amt),"overdue":money(0),
            "days_od":"0","status":"OK","status_bg":GREEN,"row_bg":WHITE,"weight":"normal"})
    ar_rows.append({"sub_name":SUB[s]+" TOTAL","customer":"","term_days":"","open":money(ar_tot(s)),
        "current":money(ar_cur(s)),"overdue":money(ar_over(s)),"days_od":"","status":"","status_bg":LIGHT,
        "row_bg":LIGHT,"weight":"bold"})
repeats["ar_rows"]=ar_rows

# ---------- Bank reconciliation ----------
recon_rows=[]; unverified=0.0
for b in banks:
    an=b[1]; rd=recon.get(an); rds=dsince(rd) if rd else None
    st="OVERDUE" if (rds is None or rds>30) else "OK"
    if st=="OVERDUE": unverified+=b[3]
    recon_rows.append({"acctno":an,"name":b[2],"sub_name":SUB[recon_sub[an]],"balance":money2(b[3]),
        "last_recon":rd or "—","days_since":str(rds) if rds is not None else "—",
        "status":st,"status_bg":RED if st=="OVERDUE" else GREEN})
recon_rows.sort(key=lambda r:0 if r["status"]=="OVERDUE" else 1)
repeats["recon_rows"]=recon_rows
scalars["recon_unverified"]=money2(unverified)

# ---------- Cash deposit verification ----------
def cash_sales(an,pid): return an[-1]==('F' if pid==984 else 'A')
VBG={"OK":GREEN,"LATE":AMBER,"OVERDUE":RED,"CRITICAL":RED,"NEGATIVE":RED,"INACTIVE":GRAY}
counts={"OK":0,"LATE":0,"OVERDUE":0,"CRITICAL":0,"NEGATIVE":0,"INACTIVE":0}
dep_rows=[]; crit_list=[]
for s in SUB:
    for an,ch,pid,bal in subs:
        if parent_sub[pid]!=s: continue
        bench=2 if cash_sales(an,pid) else 3
        td=transfer.get(an); ds=dsince(td) if td else None
        if abs(bal)<0.005:
            if td is None or ds>14:   # zero balance, no recent activity -> skip
                continue
            v="OK"
        elif bal<0: v="NEGATIVE"
        elif td is None: v="CRITICAL"
        else:
            over=ds-bench
            v="OK" if over<=0 else "LATE" if over<=2 else "OVERDUE" if over<=14 else "CRITICAL"
        counts[v]+=1
        if v=="CRITICAL": crit_list.append(f"{SUB[s]} {ch}")
        dep_rows.append({"acctno":an,"channel":ch,"sub_name":SUB[s],"balance":money2(bal),
            "last_jv":td or "—","days_since":str(ds) if ds is not None else "—",
            "benchmark":f"T+{bench}","verdict":v,"verdict_bg":VBG[v]})
dep_rows.sort(key=lambda r:(SUBORDER[r["sub_name"]], VRANK[r["verdict"]]))
repeats["deposit_rows"]=dep_rows
scalars.update(dep_counts=" · ".join(f"{k}:{v}" for k,v in counts.items() if v),
    dep_critical=str(counts["CRITICAL"]), dep_critical_list=", ".join(crit_list[:5])+(" …" if len(crit_list)>5 else ""))

# ---------- Undue VAT vendor rows ----------
def urg(bal,old):
    age=dsince(old)
    if bal>0: return "CRITICAL" if age>365 else "HIGH" if age>180 else "MEDIUM" if age>90 else "LOW"
    a=abs(bal); return "HIGH" if a>50000 else "MEDIUM" if a>=5000 else "LOW"
UBG={"CRITICAL":RED,"HIGH":ORANGE,"MEDIUM":AMBER,"LOW":GREEN}
def vat_pos(s): return sum(r[1] for r in VAT[s] if r[1]>0)
def vat_neg(s): return sum(r[1] for r in VAT[s] if r[1]<0)
pos_rows=[]; neg_rows=[]
for s in SUB:
    for eid,bal,cnt,old,new in sorted([x for x in VAT[s] if x[1]>0],key=lambda x:-x[1]):
        e=eid.replace('b',''); u=urg(bal,old)
        pos_rows.append({"sub_name":SUB[s],"vendor_id":e,"vendor_name":vn(e),"balance":money2(bal),
            "oldest":old,"newest":new,"age":str(dsince(old)),"urgency":u,"urg_bg":UBG[u],
            "action":"Post reversal JV" if dsince(old)>180 else "Monitor"})
    for eid,bal,cnt,old,new in sorted([x for x in VAT[s] if x[1]<0],key=lambda x:x[1]):
        e=eid.replace('b',''); u=urg(bal,old)
        neg_rows.append({"sub_name":SUB[s],"vendor_id":e,"vendor_name":vn(e),"balance":money2(bal),
            "oldest":old,"newest":new,"age":str(dsince(old)),"urgency":u,"urg_bg":UBG[u],
            "action":"Review double JV" if abs(bal)>50000 else "Review"})
pos_rows.sort(key=lambda r:dp(r["oldest"]))
neg_rows.sort(key=lambda r:dp(r["oldest"]))
repeats["vat_pos_rows"]=pos_rows; repeats["vat_neg_rows"]=neg_rows
vp=sum(vat_pos(s) for s in SUB); vneg=sum(vat_neg(s) for s in SUB)
np_=sum(1 for s in SUB for r in VAT[s] if r[1]>0); nn=sum(1 for s in SUB for r in VAT[s] if r[1]<0)
scalars.update(vat_notrev_n=str(np_),vat_notrev_amt=money(vp),vat_overrev_n=str(nn),vat_overrev_amt=money(vneg),
    vat_acct_input=money2(vat_acct["11101003"][1]),vat_acct_output=money2(vat_acct["21026002"][1]))
allneg=sorted([(r[0],r[1]) for s in SUB for r in VAT[s] if r[1]<0],key=lambda x:x[1])
scalars["vat_top"]=f"{vn(allneg[0][0]).split('(')[0].strip()} {money(abs(allneg[0][1]))} (over-reversed)"

# ---------- Memorized transactions ----------
def mweek(nd): return date(2026,6,22)<=dp(nd)<=date(2026,6,28)  # report week (Mon-Sun)
over=[]; pend=[]; week=[]; ontrack=0
for m in MEMO:
    _id,nm,nd,rem,ab,tot,subid,appr=m
    if dp(nd)<TODAY: over.append(m)
    if appr==1: pend.append(m)
    if dp(nd)>=TODAY and appr==2 and mweek(nd): week.append(m)
    if dp(nd)>=TODAY and appr==2 and not mweek(nd): ontrack+=1
def memrow(m,extra=None):
    _id,nm,nd,rem,ab,tot,subid,appr=m
    d={"id":str(_id),"name":nm,"sub_name":MEMO_SUB.get(subid,str(subid)),"type":ab or "—",
       "next_date":nd,"amount":money2(tot) if tot else "—","remaining":str(rem) if rem else "indef"}
    if extra: d.update(extra)
    return d
repeats["memo_overdue_rows"]=[memrow(m,{"days_overdue":str((TODAY-dp(m[2])).days),
    "row_bg":RED if (TODAY-dp(m[2])).days>90 else AMBER}) for m in sorted(over,key=lambda m:dp(m[2]))]
repeats["memo_pending_rows"]=[memrow(m) for m in sorted(pend,key=lambda m:dp(m[2]))]
repeats["memo_dueweek_rows"]=[memrow(m) for m in sorted(week,key=lambda m:dp(m[2]))]
scalars.update(memo_total=str(len(MEMO)),memo_overdue=str(len(over)),memo_pending=str(len(pend)),
    memo_dueweek=str(len(week)),memo_ontrack=str(ontrack),
    memo_top="[VEN] Mgmt fee 1.2M overdue 21d; 2× CHAW INV @1.73M await approval")

# ---------- Duplicates ----------
PBG={"HIGH":RED,"REVIEW":AMBER,"LOW":GREEN}
repeats["dup_rows"]=[{"sub_name":SUB[x[0]],"vendor_id":x[1],"vendor_name":x[2],"amount":money2(x[3]),
    "date":x[4],"count":str(x[5]),"bills":(x[8] if len(x)>8 else ""),"assessment":x[6],"priority":x[7],"pri_bg":PBG.get(x[7],GRAY)}
    for x in sorted(DUP["review"],key=lambda x:PRI_RANK.get(x[7],9))]
scalars.update(dup_exact=str(DUP["exact_count"]),dup_clusters=str(DUP["cluster_count"]),
    dup_line=f"{DUP['exact_count']} exact (PASS); {DUP['cluster_count']} same-day clusters; top: One Time Vendor billed twice (500K+50K)")

# ---------- AR top (lark) ----------
top=None
for s in SUB:
    for r in AR[s]:
        if r[6]>0 and (top is None or r[6]>top[1]): top=(r[1],r[6],days_overdue(r[7]),r[3],SUB[s])
scalars["ar_top"]=f"{top[0]} ({top[4]}) {money(top[1])} — {top[2]}d past {top[3]}d term" if top else "none"

# ---------- KPI meter (issues per section) ----------
KGREEN="#27AE60"; KAMBER="#E6A23C"; KRED="#F27061"
recon_od=sum(1 for r in recon_rows if r["status"]=="OVERDUE")
ar_od_cust=sum(1 for s in SUB for r in AR[s] if r[6]>0)
dep_off=counts["LATE"]+counts["OVERDUE"]+counts["CRITICAL"]+counts["NEGATIVE"]
dep_crit=counts["CRITICAL"]+counts["NEGATIVE"]
memo_iss=len(over)+len(pend)
dup_n=len(DUP["review"])
vat_flag=np_+nn
def _card(label,value,detail,color):
    bg={KGREEN:"#E8F5E9",KAMBER:"#FFF3E0",KRED:"#FBE4E0"}[color]
    return {"label":label,"value":str(value),"detail":detail,"color":color,"bg":bg}
repeats["kpi_cards"]=[
 _card("Bank Recon",recon_od,"acct >30d", KRED if recon_od else KGREEN),
 _card("AR Overdue",ar_od_cust,"customers", KRED if ar_od_cust else KGREEN),
 _card("Cash Deposit",dep_off,"off-benchmark", KRED if dep_crit else (KAMBER if dep_off else KGREEN)),
 _card("Undue VAT",vat_flag,str(np_)+"+ / "+str(nn)+"-", KRED if vat_flag else KGREEN),
 _card("Memorized",memo_iss,str(len(over))+" od / "+str(len(pend))+" pend", KRED if len(over) else (KAMBER if len(pend) else KGREEN)),
 _card("Duplicates",dup_n,"to review", KAMBER if dup_n else KGREEN),
]
scalars["kpi_total"]=str(recon_od+ar_od_cust+dep_off+memo_iss+dup_n)

# ---------- Section 8: Approvals & Workflow ----------
A=D["approvals"]
appr_txn=sum(r[1] for r in A["txn_summary"])
appr_master=A["master_vendor_pending"]+A["master_cust_pending"]
appr_total=appr_txn+appr_master
repeats["kpi_cards"].append(_card("Approvals",appr_total,str(appr_txn)+" txn / "+str(appr_master)+" mstr", KRED if appr_total else KGREEN))
for _c in repeats["kpi_cards"]:
    _c["cardw"]="%.1f%%" % (100.0/len(repeats["kpi_cards"]))
repeats["appr_txn_rows"]=[{"type":r[0],"count":str(r[1]),"oldest":r[2],"note":r[3],
    "bg":(RED if r[1]>0 else GREEN)} for r in A["txn_summary"]]
repeats["appr_pymt_rows"]=[{"sub":r[0],"count":str(r[1]),"oldest":r[2]} for r in A["pymt_by_sub"]]
repeats["appr_top_rows"]=[{"sub":r[0],"date":r[1],"amt":money(r[2])} for r in A["pymt_top"]]
repeats["appr_master_rows"]=[{"kind":r[4],"id":r[0],"name":r[1],"status":r[2],"since":r[3],
    "bg":(AMBER if r[4]=="Customer" else RED)} for r in A["master_detail"]]
scalars.update(appr_txn_total=str(appr_txn),appr_master_pending=str(appr_master),
    appr_cust_rejected=str(A["master_cust_rejected"]),bills_open=str(A["bills_open"]),
    bills_open_oldest=A["bills_open_oldest"],appr_root_cause=A["root_cause"])
# Approved + Open but NO DUE DATE (skipped by KBank payment run)
ND=A.get("nodue")
if ND:
    repeats["appr_nodue_rows"]=[{"vendor":r[0],"term":r[1],"bills":str(r[2]),"amt":money(r[3]),
        "action":"Set due date"} for r in ND["vendors"]]
    scalars.update(nodue_bills=str(ND["total_bills"]),nodue_amt=money(ND["total_amt"]),
        nodue_fix_bills=str(ND["fix_bills"]),nodue_fix_amt=money(ND["fix_amt"]),
        nodue_prepay_bills=str(ND["prepay_bills"]),nodue_prepay_amt=money(ND["prepay_amt"]),
        nodue_residual_bills=str(ND["residual_bills"]),nodue_residual_amt=money(ND["residual_amt"]),
        nodue_note=ND["note"])
else:
    repeats["appr_nodue_rows"]=[]
    scalars.update(nodue_bills="0",nodue_amt="0.00",nodue_fix_bills="0",nodue_fix_amt="0.00",
        nodue_prepay_bills="0",nodue_prepay_amt="0.00",nodue_residual_bills="0",
        nodue_residual_amt="0.00",nodue_note="No approved bills missing a due date.")

# ---------- Section 9: Prepayment Bills Control (30-day) ----------
P9=D["prepayment"]; BENCH=P9.get("benchmark_days",30)
def _pp(r):
    o=r[4] if len(r)>4 else 0
    st=("BREACH >%dd"%BENCH) if o>0 else ("OK <=%dd"%BENCH)
    return {"vendor":r[0],"bills":str(r[1]),"amt":money(r[2]),"oldest":r[3],
            "over30":str(o),"status":st,"row_bg":(RED if o>0 else WHITE),
            "action":("Apply deposit NOW" if o>0 else "Apply within %dd"%BENCH)}
repeats["prepay_rows"]=[_pp(r) for r in sorted(P9["vendors"], key=lambda r: dp(r[3]))]
scalars.update(prepay_bills=str(P9["total_bills"]),prepay_amt=money(P9["total_amt"]),prepay_note=P9["note"],
    prepay_over30_bills=str(P9["over30_bills"]),prepay_over30_amt=money(P9["over30_amt"]),prepay_bench=str(BENCH))
_ob=P9["over30_bills"]
repeats["kpi_cards"].append(_card("Prepayment >%dd"%BENCH,_ob,money(P9["over30_amt"])+" to clear",KRED if _ob else KGREEN))
for _c in repeats["kpi_cards"]:
    _c["cardw"]="%.1f%%"%(100.0/len(repeats["kpi_cards"]))

# ---------- Section 9b: Bills PAID BY PREPAYMENT (deposit module) ----------
PM=D.get("prepay_module")
if PM:
    repeats["prepay_mod_rows"]=[{"ref":r[0],"vendor":r[1],"dt":r[2],"amt":money(r[3]),
        "how":r[4],"sub":r[5]} for r in PM["top"]]
    scalars.update(pm_total_bills=str(PM["total_bills"]),pm_total_amt=money(PM["total_amt"]),
        pm_netted_bills=str(PM["netted_bills"]),pm_netted_amt=money(PM["netted_amt"]),
        pm_jv_bills=str(PM["jv_bills"]),pm_jv_amt=money(PM["jv_amt"]),
        pm_window=PM["window"],pm_note=PM["note"])
else:
    repeats["prepay_mod_rows"]=[]
    scalars.update(pm_total_bills="0",pm_total_amt="0.00",pm_netted_bills="0",pm_netted_amt="0.00",
        pm_jv_bills="0",pm_jv_amt="0.00",pm_window="",pm_note="No prepayment-module data.")

# ---------- week-over-week deltas on KPI cards ----------
PRIOR=D.get("kpi_prior",{})
GREY="#777777"; DRED="#F27061"; DGRN="#2E9E5B"
for c in repeats["kpi_cards"]:
    p=PRIOR.get(c["label"])
    try: cur=int(str(c["value"]).replace(",",""))
    except Exception: cur=None
    if p=="carried":
        c["wow"]="≈ last wk (not re-pulled)"; c["wcolor"]=GREY
    elif p is None or cur is None:
        c["wow"]="baseline"; c["wcolor"]=GREY
    else:
        dlt=cur-int(p)
        if dlt>0:   c["wow"]="last wk %d ▲%d"%(int(p),dlt);      c["wcolor"]=DRED
        elif dlt<0: c["wow"]="last wk %d ▼%d"%(int(p),abs(dlt)); c["wcolor"]=DGRN
        else:       c["wow"]="last wk %d –"%int(p);              c["wcolor"]=GREY
scalars["kpi_prior_asof"]=PRIOR.get("_asof","")

# ---------- meta ----------
scalars.update(date_str=D["meta"]["date_str"], source=D["meta"]["source"])

json.dump({"scalars":scalars,"repeats":repeats,"sections":sections},
          open(OUT,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("wrote",OUT,"| scalars",len(scalars),"| repeats",{k:len(v) for k,v in repeats.items()},"| sections",sections)
