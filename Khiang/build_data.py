#!/usr/bin/env python3
"""Build data.json for Khiang daily report — 2026-06-28."""
import json, math

def fmt_thb(v):
    return f"{round(v):,}"

def lerp_hex(a, b, t):
    ar,ag,ab = int(a[1:3],16),int(a[3:5],16),int(a[5:7],16)
    br,bg,bb = int(b[1:3],16),int(b[3:5],16),int(b[5:7],16)
    r=round(ar+t*(br-ar)); g=round(ag+t*(bg-ag)); bl=round(ab+t*(bb-ab))
    return f"#{r:02X}{g:02X}{bl:02X}"

def badge(today, avg5d):
    if avg5d is None: return ("#D1ECF1","#0C5460","New")
    pct = (today-avg5d)/avg5d*100
    label = (f"+{pct:.1f}%" if pct>=0 else f"{pct:.1f}%")
    if pct >= 15:  return ("#D4EDDA","#155724",label)
    if pct > -10:  return ("#FEF3CD","#856404",label)
    return         ("#F8D7DA","#721C24",label)

# ── Date tokens ──────────────────────────────────────────────────────────────
REPORT_DATE = "2026-06-28"
scalars = {
    "report_date_display": "28 June 2026",
    "report_day_en": "Sunday",
    "prev_date_short": "27 มิ.ย.",
    "report_date_short": "28 มิ.ย.",
    "d30_start": "30 พ.ค.",
    "mtd_month": "June 2026",
    "generated_date": "29 June 2026",
    "chaw_values": "Curious · Team · Act Fast · Empowered · Simple",
}

# ── Query A ───────────────────────────────────────────────────────────────────
walk_in_bills, walk_in_revenue = 139, 34757.0
staff_bills, staff_revenue = 65, 10409.2
credit_notes = 0
net_sales = walk_in_revenue + staff_revenue - credit_notes  # 45166.2
total_bills = walk_in_bills + staff_bills  # 204
avg_ticket = round(net_sales / total_bills)  # 221
signed_pct = round((net_sales-40000)/40000*100,1)  # +12.9
walk_in_pct = round(walk_in_bills/total_bills*100,1)
staff_pct   = round(staff_bills/total_bills*100,1)
target_icon = "🔥" if net_sales>=50000 else ("✅" if net_sales>=40000 else "⚠️")

# ── Query F (5-day rolling) ───────────────────────────────────────────────────
avg_5d_val = 34932.68
avg_bills_5d = 175.4
avg_ticket_bench = round(avg_5d_val / avg_bills_5d)  # 199

# ── Query I (MTD) ─────────────────────────────────────────────────────────────
net_mtd = 996944
mtd_days_actual = 28
avg_mtd = round(net_mtd / mtd_days_actual)  # 35605
mtd_signed_pct = round((avg_mtd-40000)/40000*100,1)  # -11.0

# ── Query H 30d derived ───────────────────────────────────────────────────────
net_30d = 1072508.7
avg_30d = round(net_30d/30)  # 35750
avg_bills_30d = 182

# chart
chart_max = 45166.2
bar_px_max = 90
mtd_line_px = round(min(avg_mtd, chart_max)/chart_max*bar_px_max)  # 71

bills_arrow  = "↑" if total_bills >= avg_bills_30d else "↓"
ticket_arrow = "↑" if avg_ticket >= avg_ticket_bench else "↓"

scalars.update({
    "net_sales": fmt_thb(net_sales),
    "signed_pct": (f"+{signed_pct}" if signed_pct>=0 else str(signed_pct)),
    "target_icon": target_icon,
    "avg_5d": fmt_thb(avg_5d_val),
    "anomaly_count": "7",
    "total_bills": str(total_bills),
    "avg_bills": str(avg_bills_30d),
    "bills_arrow": bills_arrow,
    "walk_in_bills": str(walk_in_bills),
    "walk_in_revenue": fmt_thb(walk_in_revenue),
    "walk_in_pct": str(walk_in_pct),
    "staff_bills": str(staff_bills),
    "staff_revenue": fmt_thb(staff_revenue),
    "staff_pct": str(staff_pct),
    "avg_ticket": str(avg_ticket),
    "avg_ticket_bench": str(avg_ticket_bench),
    "ticket_arrow": ticket_arrow,
    "net_30d": fmt_thb(net_30d),
    "avg_30d": fmt_thb(avg_30d),
    "avg_mtd": fmt_thb(avg_mtd),
    "net_mtd": fmt_thb(net_mtd),
    "mtd_days": str(mtd_days_actual),
    "mtd_signed_pct": (f"+{mtd_signed_pct}" if mtd_signed_pct>=0 else str(mtd_signed_pct)),
    "mtd_line_px": str(mtd_line_px),
    "avg_bills_30d": str(avg_bills_30d),
    "staff10_bills": "29",
    "staff10_status": "Active",
    "staff10_badge_bg": "#D4EDDA",
    "staff10_badge_fg": "#155724",
    "set50_bills": "50",
    "set50_status": "Active",
    "set50_badge_bg": "#D4EDDA",
    "set50_badge_fg": "#155724",
})

# ── Query B — top 10 all (sorted by qty desc, then itemid asc) ────────────────
RICE_ALLOW = {"K008","K013","K016","K017","K037","K038","K039","K040","K041","K042","K043","K044","K045","K046","K047"}

raw_b = [
    ("K008","ข้าวผัดโบราณ",8),("K013","ข้าวกะเพราไก่คาราเกะ",10),
    ("K014","มาม่าผัดกะเพราไก่",21),("K015","มาม่าต้มยำทรงเครื่อง",17),
    ("K018","แกงจืดเต้าหู้หมูสับ",9),("K019","ต้มยำกุ้ง",7),
    ("K020","หมูยอทอด",4),("K021","กุยช่ายกรอบ",23),
    ("K022","ไก่คาราเกะทอด",1),("K023","ไข่ดาว",124),
    ("K024","ไข่เจียว",17),("K025","ข้าวสวย",6),
    ("K028","โค้ก",80),("K029","โค้ก ซีโร่",2),
    ("K030","ชามะนาว",3),("K031","เก๊กฮวย",1),
    ("K032","ชาไทย (แก้ว)",3),("K035","สละลอยแก้ว",1),
    ("K036","ลูกตาลลอยแก้ว",2),("K037","ข้าวผัดกะเพราหมูสับ",73),
    ("K038","ข้าวผัดกะเพราไก่ชิ้น",27),("K039","ข้าวไก่กระเทียม",5),
    ("K040","ข้าวหมูกระเทียม",6),("K041","ข้าวไข่ยู่ยี่",13),
    ("K042","ข้าวกะเพราดิบเถือน…",15),("K043","ข้าวกะเพราเทพหมู",27),
    ("K045","ข้าวกะเพราเปิดย่าง",17),("K046","ข้าวไก่ผัดน้ำมันหอย",4),
    ("K047","ข้าวหมูผัดน้ำมันหอย",9),("K056","Minere Mineral Water…",34),
    ("K057","กุยช่ายแซ่บ",12),
]
raw_b.sort(key=lambda x: (-x[2], x[0]))

# Query C avg5d map
avg5d_map = {
    "K008":round(59/5),"K013":round(34/5),"K014":round(74/5),"K015":round(50/5),
    "K017":round(4/2),"K018":round(37/5),"K019":round(16/4),"K020":round(35/5),
    "K021":round(79/5),"K022":None,"K023":round(544/5),"K024":round(65/5),
    "K025":round(25/5),"K028":round(388/5),"K029":round(23/3),"K030":round(4/2),
    "K031":round(8/4),"K032":round(10/2),"K035":round(4/3),"K036":round(2/2),
    "K037":round(283/5),"K038":round(86/5),"K039":round(35/5),"K040":round(42/5),
    "K041":round(61/5),"K042":round(55/5),"K043":round(89/5),"K045":round(72/5),
    "K046":round(22/5),"K047":round(38/5),"K056":round(120/5),"K057":round(49/5),
}

top10_all = []
for i,(iid,name,qty) in enumerate(raw_b[:10]):
    a5 = avg5d_map.get(iid)
    bbg,bfg,blabel = badge(qty,a5)
    star = "⭐ " if iid in RICE_ALLOW else ""
    row_bg = "#FFFFFF" if i%2==0 else "#FAFAFA"
    top10_all.append({
        "rank": str(i+1),
        "itemid": iid,
        "name": f"{star}{name}",
        "qty": str(qty),
        "avg5d": str(a5) if a5 is not None else "—",
        "badge_bg": bbg, "badge_fg": bfg, "badge_label": blabel,
        "row_bg": row_bg,
    })

# ── Query B — top 10 rice ─────────────────────────────────────────────────────
FC_PCT = {"K037":"26.2%","K038":"24.3%","K039":"23.3%","K040":"29.7%",
          "K041":"26.1%","K042":"23.3%","K043":"25.3%","K045":"29.9%",
          "K046":"22.6%","K047":"29.1%","K008":"27.2%","K013":"26.0%"}

rice_items = [(iid,name,qty) for iid,name,qty in raw_b if iid in RICE_ALLOW]
rice_items.sort(key=lambda x:(-x[2],x[0]))

top10_rice = []
for i,(iid,name,qty) in enumerate(rice_items[:10]):
    a5 = avg5d_map.get(iid)
    bbg,bfg,blabel = badge(qty,a5)
    row_bg = "#FFFFFF" if i%2==0 else "#FAFAFA"
    top10_rice.append({
        "rank": str(i+1),
        "itemid": iid,
        "name": name,
        "qty": str(qty),
        "avg5d": str(a5) if a5 is not None else "—",
        "fc_pct": FC_PCT.get(iid,"—"),
        "badge_bg": bbg, "badge_fg": bfg, "badge_label": blabel,
        "row_bg": row_bg,
    })

# ── 30-day chart from Query H ─────────────────────────────────────────────────
days_30_data = [
    ("30/05",35593.8),("31/05",39970.9),("01/06",40604.7),("02/06",37790.9),
    ("03/06",40630.8),("04/06",31799.6),("05/06",37254.8),("06/06",42335.0),
    ("07/06",37579.6),("08/06",29538.2),("09/06",29783.3),("10/06",41166.2),
    ("11/06",29718.7),("12/06",31185.1),("13/06",35195.7),("14/06",31488.6),
    ("15/06",36478.5),("16/06",27716.8),("17/06",34525.6),("18/06",43790.5),
    ("19/06",43361.7),("20/06",33632.8),("21/06",30884.0),("22/06",30653.3),
    ("23/06",33531.1),("24/06",39150.9),("25/06",27424.6),("26/06",36691.2),
    ("27/06",37865.6),("28/06",45166.2),
]
chart_days, chart_labels = [], []
for (dstr, ns) in days_30_data:
    day_num = dstr[:2].lstrip("0")
    bar_px = max(2, round(ns/chart_max*bar_px_max))
    bar_color = "#27AE60" if ns>=40000 else "#E74C3C"
    is_report = (dstr=="28/06")
    chart_days.append({"bar_px":str(bar_px),"bar_color":bar_color,
                        "bar_title":f"{dstr} ฿{round(ns):,}"})
    chart_labels.append({"day_label":day_num,
                          "label_color":"#5551FE" if is_report else "#AAA",
                          "label_weight":"700" if is_report else "400"})

# ── Weekly table (5 weeks, oldest→newest) ────────────────────────────────────
# week_headers shared; walk_cells/staff_cells/total_cells per repeat

# Walk-In bills per week (from Query H per segment)
walk_w = [878, 861, 758, 817, 836]  # W5..W1 (oldest→newest)
staff_w = [507, 502, 410, 475, 408]
total_w = [w+s for w,s in zip(walk_w, staff_w)]

labels = ["25–31 พ.ค.", "1–7 มิ.ย.", "8–14 มิ.ย.", "15–21 มิ.ย.", "22–28 มิ.ย."]
is_cur = [False,False,False,False,True]

week_headers = []
for i in range(5):
    week_headers.append({
        "label": labels[i],
        "head_color": "#5551FE" if is_cur[i] else "#888",
        "head_bg": "#EEECFF" if is_cur[i] else "#F8F9FA",
    })

def build_cells(vals, is_current_flags):
    cells = []
    for i,v in enumerate(vals):
        prev = vals[i-1] if i>0 else None
        if prev is None or prev==0:
            pct_str, col = "", "#888"
        else:
            p = round((v-prev)/prev*100,1)
            arrow = "▲" if p>=0 else "▼"
            sign = "+" if p>=0 else ""
            pct_str = f"{arrow}{sign}{p}%"
            col = "#27AE60" if p>=0 else "#E74C3C"
        cells.append({
            "val": f"{v:,}",
            "pct": pct_str,
            "color": col,
            "weight": "700" if is_current_flags[i] else "400",
            "bg": "#EEECFF" if is_current_flags[i] else "#FFFFFF",
        })
    return cells

walk_cells  = build_cells(walk_w,  is_cur)
staff_cells = build_cells(staff_w, is_cur)
total_cells = build_cells(total_w, is_cur)

# ── 7-day heatmap ────────────────────────────────────────────────────────────
heatmap_raw = [
    ("22/06","จ",163,30653.3),("23/06","อ",158,33531.1),("24/06","พ",184,39150.9),
    ("25/06","พฤ",149,27424.6),("26/06","ศ",190,36691.2),("27/06","ส",196,37865.6),
    ("28/06","อา",204,45166.2),
]
# WoW baselines (7 days prior, same weekday)
wow_prev = {
    "22/06":36478.5,"23/06":27716.8,"24/06":34525.6,
    "25/06":43790.5,"26/06":43361.7,"27/06":33632.8,"28/06":30884.0,
}
rev_vals    = [x[3] for x in heatmap_raw]
bills_vals  = [x[2] for x in heatmap_raw]
ticket_vals = [round(x[3]/x[2]) for x in heatmap_raw]
rev_lo,rev_hi     = min(rev_vals),max(rev_vals)
bills_lo,bills_hi = min(bills_vals),max(bills_vals)
tick_lo,tick_hi   = min(ticket_vals),max(ticket_vals)

def shade(lo,hi,v): return 0.5 if hi==lo else (v-lo)/(hi-lo)
def col_weight(lo,hi,v): return "700" if v==hi else "400"

heatmap_rows = []
for i,(dstr,wd,bills,ns) in enumerate(heatmap_raw):
    ticket = round(ns/bills)
    tr = shade(rev_lo,rev_hi,ns);   tb = shade(bills_lo,bills_hi,bills); tt = shade(tick_lo,tick_hi,ticket)
    rev_bg   = lerp_hex("#FBF3EA","#C9C7FF",tr)
    bills_bg = lerp_hex("#FBF3EA","#C9C7FF",tb)
    tick_bg  = lerp_hex("#FBF3EA","#C9C7FF",tt)
    is_report = (dstr=="28/06")
    day_label_th = f"{'**' if is_report else ''}{wd} {dstr[:2].lstrip('0')}/{dstr[3:5].lstrip('0')}{'**' if is_report else ''}"
    day_label_th = f"{wd} {dstr[:2].lstrip('0')}/{dstr[3:5].lstrip('0')}"
    # WoW
    prev_ns = wow_prev.get(dstr,0)
    if prev_ns==0:
        wow_pct,wow_color,wow_weight_v = "—","#888","400"
    else:
        p = round((ns-prev_ns)/prev_ns*100,1)
        sign = "+" if p>=0 else ""
        wow_pct = f"{sign}{p}%"
        wow_color = "#27AE60" if p>=0 else "#E74C3C"
        wow_weight_v = "700" if abs(p)>=10 else "400"
    heatmap_rows.append({
        "day_label_th": day_label_th,
        "day_weight": "700" if is_report else "400",
        "rev": f"{round(ns):,}",
        "rev_bg": rev_bg, "rev_fg": "#2C3E50",
        "rev_weight": col_weight(rev_lo,rev_hi,ns),
        "bills": str(bills),
        "bills_bg": bills_bg, "bills_fg": "#2C3E50",
        "bills_weight": col_weight(bills_lo,bills_hi,bills),
        "ticket": str(ticket),
        "ticket_bg": tick_bg, "ticket_fg": "#2C3E50",
        "ticket_weight": col_weight(tick_lo,tick_hi,ticket),
        "wow_pct": wow_pct, "wow_color": wow_color, "wow_weight": wow_weight_v,
    })

# ── Hourly rows ───────────────────────────────────────────────────────────────
HOURLY_REV_BENCH = {0:1149,1:763,2:373,3:356,4:240,5:166,6:538,7:1636,8:1910,
                    9:3223,10:3827,11:4673,12:5768,13:3631,14:4196,15:3000,
                    16:3813,17:2969,18:3641,19:3069,20:3080,21:2162,22:1562,23:553}
TOTAL_REV_BENCH = sum(HOURLY_REV_BENCH.values())  # 56298
AVG_TICKET_BENCH_HOURLY = TOTAL_REV_BENCH / 298  # 188.9
HOURLY_BILL_BENCH = {h:HOURLY_REV_BENCH[h]/AVG_TICKET_BENCH_HOURLY for h in range(24)}
FLAGGED = {5,7,8,9,14,16,20}

D_map = {0:(7,1261.4),1:(2,355),2:(1,85),3:(4,648),4:(2,270),5:(0,0),
         6:(4,787.5),7:(4,968),8:(4,461.9),9:(6,1061.7),10:(12,2361.3),
         11:(16,3117.6),12:(16,3567.1),13:(14,3311.9),14:(9,1870.9),
         15:(23,4048.1),16:(9,3743.5),17:(10,1570.2),18:(11,4042.8),
         19:(14,3671.7),20:(7,1658.2),21:(15,3190.7),22:(10,2135.7),23:(4,978)}
E_map = {0:(6,769.4),1:(9,1126.4),2:(2,300),3:(2,356),4:(2,320),5:(2,463),
         6:(3,347.2),7:(10,1728.3),8:(4,1260.9),9:(7,1036.4),10:(12,2258.9),
         11:(14,2460.4),12:(24,5367.4),13:(12,2652.7),14:(6,1115.5),
         15:(10,2209.5),16:(15,3049.6),17:(10,2265),18:(7,1141.2),
         19:(18,3162.6),20:(10,1766),21:(9,2388.5),22:(2,320.7),23:(0,0)}

top3_map = {
    0:"ไข่ดาว ×5<br>โค้ก ×3<br>ข้าวผัดกะเพราหมูสับ ×2",
    1:"มาม่าผัดกะเพราไก่ ×2<br>ไข่ดาว ×1<br>โค้ก ×1",
    2:"กุยช่ายกรอบ ×1",
    3:"ไข่ดาว ×2<br>โค้ก ×2<br>ข้าวกะเพราไก่คาราเกะ ×1",
    4:"ข้าวกะเพราเทพหมู ×1<br>ข้าวไก่ผัดน้ำมันหอย ×1",
    5:"—",
    6:"ไข่ดาว ×2<br>ข้าวไข่ยู่ยี่ ×2<br>กุยช่ายกรอบ ×1",
    7:"ไข่ดาว ×3<br>โค้ก ×3<br>ข้าวผัดกะเพราหมูสับ ×2",
    8:"ไข่ดาว ×3<br>ข้าวผัดกะเพราหมูสับ ×3<br>โค้ก ×1",
    9:"ไข่ดาว ×4<br>Minere Mineral Water… ×2<br>ข้าวผัดกะเพราหมูสับ ×1",
    10:"ไข่ดาว ×8<br>Minere Mineral Water… ×3<br>ข้าวผัดกะเพราหมูสับ ×3",
    11:"ไข่ดาว ×9<br>โค้ก ×4<br>ข้าวผัดกะเพราหมูสับ ×4",
    12:"ไข่ดาว ×11<br>โค้ก ×6<br>ข้าวผัดกะเพราหมูสับ ×5",
    13:"ไข่ดาว ×9<br>โค้ก ×9<br>มาม่าต้มยำทรงเครื่อง ×3",
    14:"ไข่ดาว ×5<br>โค้ก ×5<br>ไข่เจียว ×3",
    15:"ไข่ดาว ×7<br>ข้าวผัดกะเพราหมูสับ ×7<br>โค้ก ×6",
    16:"ไข่ดาว ×8<br>โค้ก ×8<br>มาม่าต้มยำทรงเครื่อง ×6",
    17:"กุยช่ายกรอบ ×3<br>ข้าวผัดกะเพราหมูสับ ×3<br>ข้าวกะเพราเปิดย่าง ×3",
    18:"ไข่ดาว ×13<br>ข้าวผัดกะเพราหมูสับ ×8<br>โค้ก ×6",
    19:"Minere Mineral Water… ×8<br>ไข่ดาว ×6<br>โค้ก ×5",
    20:"ข้าวผัดกะเพราหมูสับ ×4<br>ไข่ดาว ×3<br>Minere Mineral Water… ×3",
    21:"ไข่ดาว ×9<br>กุยช่ายกรอบ ×6<br>โค้ก ×6",
    22:"ไข่ดาว ×10<br>โค้ก ×7<br>ข้าวผัดกะเพราหมูสับ ×5",
    23:"ไข่ดาว ×4<br>โค้ก ×3<br>ข้าวผัดกะเพราหมูสับ ×3",
}

hourly_rows = []
for h in range(24):
    cur_bills, cur_rev = D_map.get(h,(0,0))
    prev_bills, prev_rev = E_map.get(h,(0,0))
    flagged = h in FLAGGED
    if flagged:
        row_bg = "#FFEBEE"
        hour_color = "#C62828"
        hour_flag = " 🚨"
    else:
        row_bg = "#FFFFFF" if h%2==0 else "#FAFAFA"
        hour_color = "#2C3E50"
        hour_flag = ""
    # change
    if prev_rev==0:
        change_pct = "—"; change_color = "#888"; change_weight = "400"
    else:
        p = (cur_rev-prev_rev)/prev_rev*100
        sign = "+" if p>=0 else ""
        change_pct = f"{sign}{p:.1f}%"
        change_color = "#27AE60" if p>=0 else "#E74C3C"
        change_weight = "700" if abs(p)>=20 else "400"
    hourly_rows.append({
        "hour": f"{h:02d}:00",
        "hour_flag": hour_flag,
        "hour_color": hour_color,
        "prev_rev": f"{round(prev_rev):,}",
        "cur_rev": f"{round(cur_rev):,}",
        "prev_color": "#2C3E50",
        "cur_color": "#2C3E50",
        "change_pct": change_pct,
        "change_color": change_color,
        "change_weight": change_weight,
        "bench": f"{HOURLY_REV_BENCH[h]:,}",
        "top3": top3_map.get(h,"—"),
        "row_bg": row_bg,
    })

# ── Promo weekly table (G2) ───────────────────────────────────────────────────
# Staff10 and Set50 weekly bills (oldest W5→newest W1)
staff10_w = [224, 217, 163, 199, 178]
set50_w   = [301, 254, 319, 334, 332]

def build_promo_cells(vals, is_current_flags):
    cells = []
    for i,v in enumerate(vals):
        prev = vals[i-1] if i>0 else None
        if prev is None or prev==0:
            pct_str, col = "", "#888"
        else:
            p = round((v-prev)/prev*100,1)
            arrow = "▲" if p>=0 else "▼"
            sign = "+" if p>=0 else ""
            pct_str = f"{arrow}{sign}{p}%"
            col = "#27AE60" if p>=0 else "#E74C3C"
        cells.append({
            "val": f"{v:,}",
            "pct": pct_str,
            "color": col,
            "weight": "700" if is_current_flags[i] else "400",
            "bg": "#EEECFF" if is_current_flags[i] else "#FFFFFF",
        })
    return cells

staff10_cells = build_promo_cells(staff10_w, is_cur)
set50_cells   = build_promo_cells(set50_w,   is_cur)

# ── Sections ─────────────────────────────────────────────────────────────────
sections = {
    "alert_banner": True,   # anomaly_count=7 > 0
    "promo": True,          # staff10+set50 > 0
}

# ── Assemble ──────────────────────────────────────────────────────────────────
data = {
    "scalars": scalars,
    "repeats": {
        "top10_all": top10_all,
        "top10_rice": top10_rice,
        "chart_days": chart_days,
        "chart_labels": chart_labels,
        "week_headers": week_headers,
        "walk_cells": walk_cells,
        "staff_cells": staff_cells,
        "total_cells": total_cells,
        "heatmap_rows": heatmap_rows,
        "hourly_rows": hourly_rows,
        "staff10_cells": staff10_cells,
        "set50_cells": set50_cells,
    },
    "sections": sections,
}

with open("/home/user/report/Khiang/data.json","w",encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("data.json written OK")
