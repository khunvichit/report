#!/usr/bin/env python3
"""Build data.json for Khiang daily report — REPORT_DATE 2026-06-15"""
import json, math

def fmt_money(v):
    return f"{int(round(v)):,}"

def fmt_pct(p, decimals=1):
    s = f"{p:+.{decimals}f}" if p >= 0 else f"{p:.{decimals}f}"
    return s

def lerp_hex(a_hex, b_hex, t):
    ar, ag, ab = int(a_hex[1:3],16), int(a_hex[3:5],16), int(a_hex[5:7],16)
    br, bg, bb = int(b_hex[1:3],16), int(b_hex[3:5],16), int(b_hex[5:7],16)
    r = round(ar + t*(br-ar))
    g = round(ag + t*(bg-ag))
    b = round(ab + t*(bb-ab))
    return f"#{r:02X}{g:02X}{b:02X}"

def badge(pct):
    if pct is None: return "#D1ECF1","#0C5460","New"
    if pct >= 15:   return "#D4EDDA","#155724",f"+{pct:.1f}%"
    if pct >= -10:  return "#FEF3CD","#856404",f"{pct:+.1f}%"
    return "#F8D7DA","#721C24",f"{pct:.1f}%"

# ── DATES ──────────────────────────────────────────────────────────────────
REPORT_DATE = "2026-06-15"

# ── QUERY A: Segment revenue & bills ─────────────────────────────────────
walk_in_bills    = 124
walk_in_revenue  = 27499.0
staff_bills      = 69
staff_revenue    = 8979.5
credit_notes     = 0.0

net_sales        = walk_in_revenue + staff_revenue - credit_notes  # 36478.5
total_bills      = walk_in_bills + staff_bills                       # 193
avg_ticket       = round(net_sales / total_bills)                    # 189
signed_pct       = round((net_sales - 40000) / 40000 * 100, 1)      # -8.8
walk_in_pct      = round(walk_in_bills / total_bills * 100, 1)       # 64.2
staff_pct        = round(staff_bills  / total_bills * 100, 1)        # 35.8
target_icon      = "🔥" if net_sales >= 50000 else ("✅" if net_sales >= 40000 else "⚠️")

# ── QUERY F: 5-day avg ───────────────────────────────────────────────────
f5_data = [
    ("10/06/2026", 41166.2, 185),
    ("11/06/2026", 29718.7, 161),
    ("12/06/2026", 31185.1, 160),
    ("13/06/2026", 35195.7, 177),
    ("14/06/2026", 31488.6, 172),
]
avg_5d      = round(sum(r[1] for r in f5_data) / len(f5_data))   # 33751
avg_bills   = round(sum(r[2] for r in f5_data) / len(f5_data))   # 171
avg_ticket_bench = round(avg_5d / avg_bills)                       # 197
bills_arrow  = "↑" if total_bills >= avg_bills else "↓"
ticket_arrow = "↑" if avg_ticket >= avg_ticket_bench else "↓"

# ── QUERY I: MTD ──────────────────────────────────────────────────────────
net_mtd_raw  = 532549.7
mtd_days_val = 15
avg_mtd      = round(net_mtd_raw / mtd_days_val)                   # 35503
mtd_signed_pct = round((avg_mtd - 40000) / 40000 * 100, 1)        # -11.2

# ── QUERY H: 35-day data ──────────────────────────────────────────────────
h_raw = [
    ("12/05/2026","Staff",11160.0,78),("12/05/2026","Walk-In",28961.0,116),
    ("13/05/2026","Staff",16067.7,102),("13/05/2026","Walk-In",23957.0,111),
    ("14/05/2026","Staff",12070.7,79),("14/05/2026","Walk-In",23288.0,112),
    ("15/05/2026","Staff",13679.4,74),("15/05/2026","Walk-In",31218.0,139),
    ("16/05/2026","Staff",11144.8,74),("16/05/2026","Walk-In",26853.0,123),
    ("17/05/2026","Staff",12228.9,83),("17/05/2026","Walk-In",28968.0,138),
    ("18/05/2026","Staff",10443.4,75),("18/05/2026","Walk-In",29533.0,132),
    ("19/05/2026","Staff",8242.8,55),("19/05/2026","Walk-In",30575.0,133),
    ("20/05/2026","Staff",11338.7,76),("20/05/2026","Walk-In",24285.0,114),
    ("21/05/2026","Staff",6224.0,47),("21/05/2026","Walk-In",17322.0,86),
    ("22/05/2026","Staff",15109.2,87),("22/05/2026","Walk-In",22623.0,110),
    ("23/05/2026","Staff",10007.0,72),("23/05/2026","Walk-In",25946.0,112),
    ("24/05/2026","Staff",10707.6,74),("24/05/2026","Walk-In",26407.0,117),
    ("25/05/2026","Staff",8525.5,63),("25/05/2026","Walk-In",32494.0,132),
    ("26/05/2026","Staff",10427.6,64),("26/05/2026","Walk-In",31940.0,123),
    ("27/05/2026","Staff",12681.4,85),("27/05/2026","Walk-In",20012.0,107),
    ("28/05/2026","Staff",9930.8,65),("28/05/2026","Walk-In",26573.0,121),
    ("29/05/2026","Staff",10340.5,71),("29/05/2026","Walk-In",37022.0,155),
    ("30/05/2026","Staff",11424.8,75),("30/05/2026","Walk-In",24169.0,108),
    ("31/05/2026","Staff",12473.9,84),("31/05/2026","Walk-In",27497.0,132),
    ("01/06/2026","Staff",13023.7,83),("01/06/2026","Walk-In",27581.0,131),
    ("02/06/2026","Staff",7957.9,54),("02/06/2026","Walk-In",29833.0,131),
    ("03/06/2026","Staff",15291.8,91),("03/06/2026","Walk-In",25339.0,112),
    ("04/06/2026","Staff",10156.6,66),("04/06/2026","Walk-In",21643.0,112),
    ("05/06/2026","Staff",9948.8,67),("05/06/2026","Walk-In",27306.0,123),
    ("06/06/2026","Staff",9763.0,67),("06/06/2026","Walk-In",32572.0,140),
    ("07/06/2026","Staff",10333.6,74),("07/06/2026","Walk-In",27246.0,112),
    ("08/06/2026","Staff",8598.2,64),("08/06/2026","Walk-In",20940.0,104),
    ("09/06/2026","Staff",9678.3,56),("09/06/2026","Walk-In",20105.0,89),
    ("10/06/2026","Staff",7971.2,52),("10/06/2026","Walk-In",33195.0,133),
    ("11/06/2026","Staff",7230.7,49),("11/06/2026","Walk-In",22488.0,112),
    ("12/06/2026","Staff",7677.1,55),("12/06/2026","Walk-In",23508.0,105),
    ("13/06/2026","Staff",8358.7,59),("13/06/2026","Walk-In",26837.0,118),
    ("14/06/2026","Staff",10094.6,75),("14/06/2026","Walk-In",21394.0,97),
    ("15/06/2026","Staff",8979.5,69),("15/06/2026","Walk-In",27499.0,124),
]

# Collapse to per-day totals
from collections import defaultdict
h_day_rev   = defaultdict(float)
h_day_bills = defaultdict(int)
h_day_walk  = defaultdict(int)
h_day_staff = defaultdict(int)
for (d, seg, rev, b) in h_raw:
    h_day_rev[d]   += rev
    h_day_bills[d] += b
    if seg == "Walk-In": h_day_walk[d]  += b
    else:                h_day_staff[d] += b

# 30-day window: D30_START (17/05) to 15/06
d30_dates = []
from datetime import date, timedelta
d30_start = date(2026,5,17)
report_date = date(2026,6,15)
cur = d30_start
while cur <= report_date:
    dk = cur.strftime("%d/%m/%Y")
    d30_dates.append(dk)
    cur += timedelta(days=1)

# 35-day window: W35_START (12/05) to 15/06
w35_start = date(2026,5,12)
w35_dates = []
cur = w35_start
while cur <= report_date:
    w35_dates.append((cur, cur.strftime("%d/%m/%Y")))
    cur += timedelta(days=1)

net_30d     = sum(h_day_rev.get(d,0) for d in d30_dates)
days_30d    = sum(1 for d in d30_dates if h_day_rev.get(d,0) > 0)
avg_30d     = round(net_30d / days_30d) if days_30d > 0 else 0
bills_30d   = sum(h_day_bills.get(d,0) for d in d30_dates)
avg_bills_30d = round(bills_30d / days_30d) if days_30d > 0 else 0

# 5 weeks (oldest → newest) ending REPORT_DATE
# week w=0(oldest) .. w=4(newest)
week_defs = []
for w in range(4, -1, -1):  # w=4..0 produces oldest..newest
    end_d   = report_date - timedelta(days=w*7)
    start_d = end_d - timedelta(days=6)
    week_defs.append((start_d, end_d))
# week_defs[0] = oldest, week_defs[4] = newest

def week_label(s, e):
    th_months = ["","ม.ค.","ก.พ.","มี.ค.","เม.ย.","พ.ค.","มิ.ย.","ก.ค.","ส.ค.","ก.ย.","ต.ค.","พ.ย.","ธ.ค."]
    if s.month == e.month:
        return f"{s.day}–{e.day} {th_months[s.month]}"
    return f"{s.day} {th_months[s.month]}–{e.day} {th_months[e.month]}"

week_walk  = []
week_staff = []
week_total = []
week_labels_str = []
for (s, e) in week_defs:
    wdates = []
    cur = s
    while cur <= e:
        wdates.append(cur.strftime("%d/%m/%Y"))
        cur += timedelta(days=1)
    ww = sum(h_day_walk.get(d,0)  for d in wdates)
    ws = sum(h_day_staff.get(d,0) for d in wdates)
    wt = ww + ws
    week_walk.append(ww)
    week_staff.append(ws)
    week_total.append(wt)
    week_labels_str.append(week_label(s, e))

# Build week_headers repeat
week_headers = []
for i, (s, e) in enumerate(week_defs):
    is_cur = (i == 4)
    week_headers.append({
        "label":    week_labels_str[i],
        "head_color": "#5551FE" if is_cur else "#888",
        "head_bg":    "#EEECFF" if is_cur else "#F8F9FA",
    })

def make_cells(vals, is_cur_list):
    cells = []
    for i, v in enumerate(vals):
        is_cur = is_cur_list[i]
        if i == 0:
            pct, color = "", "#888"
        else:
            prev = vals[i-1]
            if prev == 0:
                pct, color = "", "#888"
            else:
                p = round((v - prev) / prev * 100, 1)
                arrow = "▲" if p >= 0 else "▼"
                sign  = "+" if p >= 0 else ""
                pct   = f"{arrow}{sign}{p:.1f}%"
                color = "#27AE60" if p >= 0 else "#E74C3C"
        cells.append({
            "val":    f"{v:,}",
            "pct":    pct,
            "color":  color,
            "weight": "700" if is_cur else "400",
            "bg":     "#EEECFF" if is_cur else "#FFFFFF",
        })
    return cells

is_cur_list = [False, False, False, False, True]
walk_cells  = make_cells(week_walk,  is_cur_list)
staff_cells = make_cells(week_staff, is_cur_list)
total_cells = make_cells(week_total, is_cur_list)

# ── CHART DAYS (30-day bar chart) ─────────────────────────────────────────
chart_max  = max(h_day_rev.get(d,0) for d in d30_dates)
bar_px_max = 90

# Query I MTD avg is avg_mtd
mtd_line_px = round(min(avg_mtd, chart_max) / chart_max * bar_px_max)

chart_days   = []
chart_labels = []
for dk in d30_dates:
    rev = h_day_rev.get(dk, 0)
    bar_px    = max(2, round(rev / chart_max * bar_px_max))
    bar_color = "#27AE60" if rev >= 40000 else "#E74C3C"
    day_num   = dk[:2].lstrip("0") or "0"
    bar_title = f"฿{fmt_money(rev)} ({dk[:5]})"
    is_rd     = (dk == report_date.strftime("%d/%m/%Y"))
    chart_days.append({"bar_px": bar_px, "bar_color": bar_color, "bar_title": bar_title})
    chart_labels.append({
        "day_label":    day_num,
        "label_color":  "#5551FE" if is_rd else "#AAA",
        "label_weight": "700"     if is_rd else "400",
    })

# ── 7-DAY HEATMAP (Query J) ────────────────────────────────────────────────
j_raw = [
    ("02/06/2026", 37790.9, 185),
    ("03/06/2026", 40630.8, 203),
    ("04/06/2026", 31799.6, 178),
    ("05/06/2026", 37254.8, 190),
    ("06/06/2026", 42335.0, 207),
    ("07/06/2026", 37579.6, 186),
    ("08/06/2026", 29538.2, 168),
    ("09/06/2026", 29783.3, 145),
    ("10/06/2026", 41166.2, 185),
    ("11/06/2026", 29718.7, 161),
    ("12/06/2026", 31185.1, 160),
    ("13/06/2026", 35195.7, 177),
    ("14/06/2026", 31488.6, 172),
    ("15/06/2026", 36478.5, 193),
]
j_map = {d: (r, b) for (d, r, b) in j_raw}
display_7 = []
start7 = date(2026,6,9)
cur = start7
while cur <= report_date:
    dk = cur.strftime("%d/%m/%Y")
    r, b = j_map.get(dk, (0, 0))
    t_val = round(r / b) if b > 0 else 0
    display_7.append((cur, dk, r, b, t_val))
    cur += timedelta(days=1)

revs    = [x[2] for x in display_7]
bills_7 = [x[3] for x in display_7]
tickets = [x[4] for x in display_7]

def shade_col(vals):
    lo, hi = min(vals), max(vals)
    bgs, fgs, weights = [], [], []
    for v in vals:
        t = 0.5 if hi == lo else (v - lo)/(hi - lo)
        bgs.append(lerp_hex('#FBF3EA','#C9C7FF', t))
        fgs.append('#2C3E50')
        weights.append("700" if v == hi else "400")
    return bgs, fgs, weights

rev_bgs,  rev_fgs,  rev_wts  = shade_col(revs)
bill_bgs, bill_fgs, bill_wts = shade_col(bills_7)
tkt_bgs,  tkt_fgs,  tkt_wts = shade_col(tickets)

th_weekday = ["อา.","จ.","อ.","พ.","พฤ.","ศ.","ส."]
th_months  = ["","ม.ค.","ก.พ.","มี.ค.","เม.ย.","พ.ค.","มิ.ย.","ก.ค.","ส.ค.","ก.ย.","ต.ค.","พ.ย.","ธ.ค."]

heatmap_rows = []
for i, (d, dk, r, b, t_val) in enumerate(display_7):
    # WoW: same day last week = d - 7
    prev_dk = (d - timedelta(days=7)).strftime("%d/%m/%Y")
    prev_r, _ = j_map.get(prev_dk, (None, None))
    if prev_r is None or prev_r == 0:
        wow_pct    = "—"
        wow_color  = "#888"
        wow_weight = "400"
    else:
        p = round((r - prev_r) / prev_r * 100, 1)
        sign = "+" if p >= 0 else ""
        wow_pct    = f"{sign}{p:.1f}%"
        wow_color  = "#27AE60" if p >= 0 else "#E74C3C"
        wow_weight = "700" if abs(p) >= 10 else "400"
    wd  = th_weekday[d.weekday()+1 if d.weekday() < 6 else 0]
    # weekday(): Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
    # Thai: อา.=Sun(6), จ.=Mon(0), อ.=Tue(1), พ.=Wed(2), พฤ.=Thu(3), ศ.=Fri(4), ส.=Sat(5)
    wd_map = {0:"จ.",1:"อ.",2:"พ.",3:"พฤ.",4:"ศ.",5:"ส.",6:"อา."}
    wd = wd_map[d.weekday()]
    lbl = f"{wd} {d.day}/{d.month}"
    is_rd = (d == report_date)
    heatmap_rows.append({
        "day_label_th": lbl,
        "day_weight":   "700" if is_rd else "400",
        "rev":          fmt_money(r),
        "rev_bg":       rev_bgs[i],
        "rev_fg":       rev_fgs[i],
        "rev_weight":   rev_wts[i],
        "bills":        str(b),
        "bills_bg":     bill_bgs[i],
        "bills_fg":     bill_fgs[i],
        "bills_weight": bill_wts[i],
        "ticket":       str(t_val),
        "ticket_bg":    tkt_bgs[i],
        "ticket_fg":    tkt_fgs[i],
        "ticket_weight":tkt_wts[i],
        "wow_pct":      wow_pct,
        "wow_color":    wow_color,
        "wow_weight":   wow_weight,
    })

# ── QUERY B: Top items ────────────────────────────────────────────────────
rice_allow = {"K008","K013","K016","K017","K037","K038","K039","K040","K041","K042","K043","K044","K045","K046","K047"}

b_raw = [
    ("K008","ข้าวผัดโบราณ",20),("K013","ข้าวกะเพราไก่คาราเกะ",5),
    ("K014","มาม่าผัดกะเพราไก่",12),("K015","มาม่าต้มยำทรงเครื่อง",8),
    ("K018","แกงจืดเต้าหู้หมูสับ",12),("K019","ต้มยำกุ้ง",7),
    ("K020","หมูยอทอด",13),("K021","กุยช่ายกรอบ",1),
    ("K023","ไข่ดาว",107),("K024","ไข่เจียว",17),
    ("K025","ข้าวสวย",11),("K026","กุนเชียง",4),
    ("K028","โค้ก",67),("K029","โค้ก ซีโร่",7),
    ("K030","ชามะนาว",6),("K031","เก๊กฮวย",3),
    ("K032","ชาไทย (แก้ว)",1),("K035","สละลอยแก้ว",1),
    ("K036","ลูกตาลลอยแก้ว",1),
    ("K037","ข้าวผัดกะเพราหมูสับ",65),("K038","ข้าวผัดกะเพราไก่ชิ้น",23),
    ("K039","ข้าวไก่กระเทียม",4),("K040","ข้าวหมูกระเทียม",10),
    ("K041","ข้าวไข่ยู่ยี่",17),("K042","ข้าวกะเพราดิบเถือน (เนื้อโคขุน)",8),
    ("K043","ข้าวกะเพราเทพหมู",20),("K045","ข้าวกะเพราเปิดยาง",21),
    ("K046","ข้าวไก่ผัดน้ำมันหอย",4),("K047","ข้าวหมูผัดน้ำมันหอย",5),
    ("K056","Minere Mineral Water 600 Ml",29),
]

c_raw = {
    "K008":56,"K013":44,"K014":53,"K015":36,"K016":1,"K017":2,
    "K018":40,"K019":23,"K020":35,"K021":75,"K022":3,"K023":485,
    "K024":78,"K025":40,"K026":11,"K028":317,"K029":82,"K030":4,
    "K031":9,"K032":21,"K035":3,"K036":9,"K037":254,"K038":104,
    "K039":39,"K040":67,"K041":65,"K042":45,"K043":60,"K045":89,
    "K046":24,"K047":39,"K056":126,"K057":36,
}
c_days = {k: 5 for k in c_raw}  # all 5 days
c_days["K016"] = 1; c_days["K017"] = 2; c_days["K022"] = 2
c_days["K026"] = 4; c_days["K030"] = 4; c_days["K035"] = 2
c_days["K036"] = 5

avg5d_map = {k: round(c_raw[k] / c_days.get(k, 5)) for k in c_raw}

b_sorted = sorted(b_raw, key=lambda x: -x[2])

fc_pct_map = {
    "K037":"26.2","K038":"24.3","K039":"23.3","K040":"29.7","K041":"26.1",
    "K042":"23.3","K043":"25.3","K045":"29.9","K046":"22.6","K047":"29.1",
    "K008":"27.2","K013":"26.0",
}

def make_badge(itemid, qty):
    a5 = avg5d_map.get(itemid)
    if a5 is None or a5 == 0:
        return badge(None)
    p = round((qty - a5) / a5 * 100, 1)
    return badge(p)

# Top 10 all
top10_all = []
for rank, (iid, name, qty) in enumerate(b_sorted[:10], 1):
    a5   = avg5d_map.get(iid)
    a5d  = str(a5) if a5 is not None else "—"
    bbg, bfg, blbl = make_badge(iid, qty)
    is_rice = iid in rice_allow
    display_name = ("⭐ " + name) if is_rice else name
    row_bg = "#FFFFFF" if rank % 2 == 1 else "#FAFAFA"
    top10_all.append({
        "rank": rank, "itemid": iid, "name": display_name,
        "qty": qty, "avg5d": a5d,
        "badge_bg": bbg, "badge_fg": bfg, "badge_label": blbl,
        "row_bg": row_bg,
    })

# Top 10 rice
rice_items = [(iid, name, qty) for (iid, name, qty) in b_sorted if iid in rice_allow]
top10_rice = []
for rank, (iid, name, qty) in enumerate(rice_items[:10], 1):
    a5   = avg5d_map.get(iid)
    a5d  = str(a5) if a5 is not None else "—"
    bbg, bfg, blbl = make_badge(iid, qty)
    fc   = fc_pct_map.get(iid, "—")
    row_bg = "#FFFFFF" if rank % 2 == 1 else "#FAFAFA"
    top10_rice.append({
        "rank": rank, "itemid": iid, "name": name,
        "qty": qty, "avg5d": a5d, "fc_pct": fc,
        "badge_bg": bbg, "badge_fg": bfg, "badge_label": blbl,
        "row_bg": row_bg,
    })

# ── HOURLY ROWS ─────────────────────────────────────────────────────────────
# Revenue benchmark per hour
rev_bench = {0:1149,1:763,2:373,3:356,4:240,5:166,6:538,7:1636,8:1910,
             9:3223,10:3827,11:4673,12:5768,13:3631,14:4196,15:3000,
             16:3813,17:2969,18:3641,19:3069,20:3080,21:2162,22:1562,23:553}

# Bill bench derived from rev bench (avg ticket bench ≈ 189)
avg_ticket_bench_hr = 189
bill_bench = {h: max(1, round(rev_bench[h] / avg_ticket_bench_hr)) for h in rev_bench}

d_raw = {
    0:(5,1118.0),1:(1,94.5),2:(4,507.0),3:(7,1353.2),4:(8,1543.0),
    5:(4,716.7),6:(4,429.0),7:(6,637.0),8:(3,824.5),9:(3,465.7),
    10:(7,1635.2),11:(10,2051.1),12:(28,6054.5),13:(16,2432.8),
    14:(9,1605.7),15:(10,2682.5),16:(11,2798.1),17:(8,1777.0),
    18:(14,2425.9),19:(16,2322.6),20:(7,783.7),21:(3,645.0),
    22:(8,1410.8),23:(1,165.0),
}
e_raw = {
    0:(3,605.0),1:(2,404.5),2:(2,134.5),
    6:(3,784.5),7:(8,1126.0),8:(5,545.7),9:(8,1336.7),
    10:(14,1891.2),11:(20,2711.1),12:(19,3800.9),13:(18,3688.5),
    14:(7,1385.0),15:(12,2401.5),16:(5,1658.5),17:(9,1995.7),
    18:(10,1688.7),19:(4,1163.0),20:(8,1262.5),21:(8,1428.7),
    22:(5,1186.4),23:(2,290.0),
}

# E2: top3 per hour (pre-computed strings, decoded from Unicode)
e2_top3 = {
    0:  "โค้ก ×5<br>ไข่ดาว ×3<br>ไข่เจียว ×2",
    1:  "ข้าวผัดกะเพราหมูสับ ×1",
    2:  "ข้าวผัดกะเพราหมูสับ ×2<br>ข้าวผัดโบราณ ×1<br>แกงจืดเต้าหู้หมูสับ ×1",
    3:  "ข้าวผัดโบราณ ×2<br>มาม่าต้มยำทรงเครื่อง ×2<br>ข้าวผัดกะเพราไก่ชิ้น ×2",
    4:  "ชามะนาว ×3<br>เก๊กฮวย ×3<br>ข้าวหมูกระเทียม ×3",
    5:  "ข้าวผัดกะเพราหมูสับ ×4<br>ไข่ดาว ×2<br>Minere Mineral Water… ×2",
    6:  "ข้าวผัดกะเพราหมูสับ ×2<br>ข้าวผัดกะเพราไก่ชิ้น ×1<br>ข้าวไข่ยู่ยี่ ×1",
    7:  "ข้าวผัดกะเพราหมูสับ ×3<br>ข้าวผัดโบราณ ×1<br>ไข่ดาว ×1",
    8:  "ไข่เจียว ×2<br>แกงจืดเต้าหู้หมูสับ ×1<br>ข้าวหมูกระเทียม ×1",
    9:  "ไข่ดาว ×2<br>แกงจืดเต้าหู้หมูสับ ×1<br>โค้ก ×1",
    10: "ไข่ดาว ×4<br>โค้ก ซีโร่ ×2<br>ข้าวผัดกะเพราหมูสับ ×2",
    11: "ไข่ดาว ×6<br>ข้าวผัดโบราณ ×3<br>ข้าวสวย ×3",
    12: "ไข่ดาว ×24<br>โค้ก ×17<br>ข้าวผัดกะเพราไก่ชิ้น ×7",
    13: "ไข่ดาว ×9<br>ข้าวผัดกะเพราหมูสับ ×5<br>ข้าวผัดโบราณ ×4",
    14: "ไข่ดาว ×5<br>ข้าวผัดกะเพราหมูสับ ×5<br>โค้ก ×4",
    15: "ไข่ดาว ×7<br>โค้ก ×4<br>ข้าวผัดกะเพราหมูสับ ×3",
    16: "ไข่ดาว ×9<br>ข้าวผัดกะเพราหมูสับ ×6<br>Minere Mineral Water… ×5",
    17: "ไข่ดาว ×4<br>ข้าวกะเพราเปิดยาง ×3<br>โค้ก ×3",
    18: "ไข่ดาว ×10<br>ข้าวผัดกะเพราหมูสับ ×6<br>โค้ก ×4",
    19: "ไข่ดาว ×10<br>ข้าวผัดกะเพราหมูสับ ×8<br>โค้ก ×6",
    20: "ไข่ดาว ×2<br>โค้ก ×2<br>ข้าวกะเพราไก่คาราเกะ ×1",
    21: "ไข่ดาว ×2<br>โค้ก ×2<br>ข้าวกะเพราเทพหมู ×2",
    22: "ไข่ดาว ×3<br>กุนเชียง ×3<br>โค้ก ×3",
    23: "ไข่ดาว ×1<br>โค้ก ×1<br>ข้าวกะเพราเปิดยาง ×1",
}

# Anomaly detection
anomaly_hours = set()
for h, (bills_h, rev_h) in d_raw.items():
    if bills_h < bill_bench[h] * 0.50:
        anomaly_hours.add(h)
anomaly_count = len(anomaly_hours)

hourly_rows = []
normal_row_idx = 0
for h in range(24):
    if h not in d_raw:
        continue
    cur_bills, cur_rev = d_raw[h]
    prev_bills, prev_rev_h = e_raw.get(h, (0, 0))
    is_anomaly = h in anomaly_hours

    # row background
    if is_anomaly:
        row_bg     = "#FFEBEE"
        hour_color = "#C62828"
        hour_flag  = " 🚨"
    else:
        row_bg     = "#FFFFFF" if normal_row_idx % 2 == 0 else "#FAFAFA"
        hour_color = "#5551FE"
        hour_flag  = ""
        normal_row_idx += 1

    # change pct
    if prev_rev_h == 0:
        change_pct    = "New"
        change_color  = "#888"
        change_weight = "400"
    else:
        p = round((cur_rev - prev_rev_h) / prev_rev_h * 100, 1)
        sign = "+" if p >= 0 else ""
        change_pct    = f"{sign}{p:.1f}%"
        change_color  = "#27AE60" if p >= 0 else "#E74C3C"
        change_weight = "700" if abs(p) >= 10 else "400"

    def fmt_rev(v):
        if v == 0: return "—"
        if v >= 1000: return f"{v:,.0f}"
        return f"{v:.1f}".rstrip('0').rstrip('.')

    hourly_rows.append({
        "hour":         f"{h:02d}:00",
        "hour_flag":    hour_flag,
        "hour_color":   hour_color,
        "prev_rev":     fmt_rev(prev_rev_h),
        "prev_color":   "#888",
        "cur_rev":      fmt_rev(cur_rev),
        "cur_color":    "#2C3E50",
        "change_pct":   change_pct,
        "change_color": change_color,
        "change_weight":change_weight,
        "bench":        f"{rev_bench[h]:,}",
        "top3":         e2_top3.get(h, "—"),
        "row_bg":       row_bg,
    })

# ── QUERY G: Promotions ─────────────────────────────────────────────────
staff10_bills_val = 30
set50_bills_val   = 52

# ── QUERY G2: Promo weekly trend ─────────────────────────────────────────
# Per-day promo data (from G2 extraction)
promo_s10 = {
    "12/05/2026":33,"13/05/2026":44,"14/05/2026":41,"15/05/2026":25,
    "16/05/2026":26,"17/05/2026":39,"18/05/2026":35,"19/05/2026":24,
    "20/05/2026":31,"21/05/2026":20,"22/05/2026":36,"23/05/2026":33,
    "24/05/2026":35,"25/05/2026":32,"26/05/2026":22,"27/05/2026":40,
    "28/05/2026":32,"29/05/2026":32,"30/05/2026":32,"31/05/2026":34,
    "01/06/2026":33,"02/06/2026":19,"03/06/2026":41,"04/06/2026":28,
    "05/06/2026":29,"06/06/2026":37,"07/06/2026":30,"08/06/2026":30,
    "09/06/2026":22,"10/06/2026":25,"11/06/2026":19,"12/06/2026":17,
    "13/06/2026":22,"14/06/2026":28,"15/06/2026":30,
}
promo_s50 = {
    "12/05/2026":18,"13/05/2026":25,"14/05/2026":36,"15/05/2026":59,
    "16/05/2026":52,"17/05/2026":55,"18/05/2026":39,"19/05/2026":58,
    "20/05/2026":51,"21/05/2026":29,"22/05/2026":45,"23/05/2026":50,
    "24/05/2026":39,"25/05/2026":48,"26/05/2026":39,"27/05/2026":36,
    "28/05/2026":50,"29/05/2026":67,"30/05/2026":37,"31/05/2026":24,
    "01/06/2026":40,"02/06/2026":34,"03/06/2026":41,"04/06/2026":36,
    "05/06/2026":27,"06/06/2026":47,"07/06/2026":29,"08/06/2026":27,
    "09/06/2026":28,"10/06/2026":53,"11/06/2026":59,"12/06/2026":54,
    "13/06/2026":52,"14/06/2026":46,"15/06/2026":52,
}

week_s10 = []
week_s50 = []
for (s, e) in week_defs:
    wdates = []
    cur = s
    while cur <= e:
        wdates.append(cur.strftime("%d/%m/%Y"))
        cur += timedelta(days=1)
    week_s10.append(sum(promo_s10.get(d,0) for d in wdates))
    week_s50.append(sum(promo_s50.get(d,0) for d in wdates))

staff10_cells = make_cells(week_s10, is_cur_list)
set50_cells   = make_cells(week_s50, is_cur_list)

# Promo badges
staff10_badge_bg = "#D4EDDA"; staff10_badge_fg = "#155724"; staff10_status = "Active ✅"
set50_badge_bg   = "#D4EDDA"; set50_badge_fg   = "#155724"; set50_status   = "Active ✅"

# ── GROUP MESSAGE: rice_top10_lines ─────────────────────────────────────
rice_lines = []
for r_item in top10_rice:
    iid   = r_item["itemid"]
    name  = r_item["name"]
    qty   = r_item["qty"]
    a5    = avg5d_map.get(iid)
    if a5 and a5 > 0:
        p   = round((qty - a5) / a5 * 100, 1)
        blbl = f"{p:+.1f}%"
    else:
        blbl = "New"
    rice_lines.append(f"{r_item['rank']}. {iid} {name} — {qty} ({blbl})")
rice_top10_lines = "\n".join(rice_lines)

# ── ASSEMBLE data.json ─────────────────────────────────────────────────────
data = {
    "scalars": {
        "report_date_display": "15 June 2026",
        "report_date_short":   "15 มิ.ย.",
        "prev_date_short":     "14 มิ.ย.",
        "report_day_en":       "Monday",
        "report_year":         "2026",
        "generated_date":      "16 June 2026",
        "net_sales":           fmt_money(net_sales),
        "signed_pct":          f"{signed_pct:+.1f}" if signed_pct >= 0 else f"{signed_pct:.1f}",
        "target_icon":         target_icon,
        "total_bills":         str(total_bills),
        "avg_bills":           str(avg_bills),
        "bills_arrow":         bills_arrow,
        "walk_in_bills":       str(walk_in_bills),
        "walk_in_revenue":     fmt_money(walk_in_revenue),
        "walk_in_pct":         str(walk_in_pct),
        "staff_bills":         str(staff_bills),
        "staff_revenue":       fmt_money(round(staff_revenue)),
        "staff_pct":           str(staff_pct),
        "avg_ticket":          str(avg_ticket),
        "avg_ticket_bench":    str(avg_ticket_bench),
        "ticket_arrow":        ticket_arrow,
        "avg_5d":              fmt_money(avg_5d),
        "net_30d":             fmt_money(round(net_30d)),
        "avg_30d":             fmt_money(avg_30d),
        "d30_start":           "17 พ.ค.",
        "net_mtd":             fmt_money(round(net_mtd_raw)),
        "avg_mtd":             fmt_money(avg_mtd),
        "mtd_days":            str(mtd_days_val),
        "mtd_month":           "June 2026",
        "mtd_signed_pct":      f"{mtd_signed_pct:+.1f}" if mtd_signed_pct >= 0 else f"{mtd_signed_pct:.1f}",
        "mtd_line_px":         str(mtd_line_px),
        "avg_bills_30d":       str(avg_bills_30d),
        "anomaly_count":       str(anomaly_count),
        "staff10_bills":       str(staff10_bills_val),
        "set50_bills":         str(set50_bills_val),
        "staff10_badge_bg":    staff10_badge_bg,
        "staff10_badge_fg":    staff10_badge_fg,
        "staff10_status":      staff10_status,
        "set50_badge_bg":      set50_badge_bg,
        "set50_badge_fg":      set50_badge_fg,
        "set50_status":        set50_status,
        "chaw_values":         "Curious · Team · Act Fast · Empowered · Simple",
    },
    "repeats": {
        "chart_days":    chart_days,
        "chart_labels":  chart_labels,
        "week_headers":  week_headers,
        "walk_cells":    walk_cells,
        "staff_cells":   staff_cells,
        "total_cells":   total_cells,
        "staff10_cells": staff10_cells,
        "set50_cells":   set50_cells,
        "heatmap_rows":  heatmap_rows,
        "top10_all":     top10_all,
        "top10_rice":    top10_rice,
        "hourly_rows":   hourly_rows,
    },
    "sections": {
        "alert_banner": anomaly_count > 0,
        "promo":        (staff10_bills_val + set50_bills_val) > 0,
    },
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("data.json written")
print(f"anomaly_count={anomaly_count}, anomaly_hours={sorted(anomaly_hours)}")
print(f"net_sales={fmt_money(net_sales)}, signed_pct={signed_pct}")
print(f"net_30d={fmt_money(round(net_30d))}, avg_30d={fmt_money(avg_30d)}")
print(f"net_mtd={fmt_money(round(net_mtd_raw))}, avg_mtd={fmt_money(avg_mtd)}")
print(f"week_s10={week_s10}, week_s50={week_s50}")
print("rice_top10_lines:")
print(rice_top10_lines)
