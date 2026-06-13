#!/usr/bin/env python3
"""Build data.json for khiang-template.html from queried NetSuite data."""
import json, math

# ── DATES ──────────────────────────────────────────────────────────────────
REPORT_DATE = "2026-06-12"
scalars = {
    "report_date_display": "12 Jun 2026",
    "report_date_short":   "12 มิ.ย.",
    "prev_date_short":     "11 มิ.ย.",
    "report_day_en":       "Friday",
    "report_year":         "2026",
    "generated_date":      "13 Jun 2026",
    "d30_start":           "14 พ.ค.",
    "chaw_values":         "Curious · Team · Act Fast · Empowered · Simple",
}

def fmt(n):
    """Format number with thousands separator, 0 decimal places."""
    return f"{round(n):,}"

def lerp_hex(a, b, t):
    """Linear interpolate between two hex colours."""
    ar, ag, ab_ = int(a[1:3],16), int(a[3:5],16), int(a[5:7],16)
    br, bg, bb_ = int(b[1:3],16), int(b[3:5],16), int(b[5:7],16)
    r = round(ar + t*(br-ar))
    g = round(ag + t*(bg-ag))
    b_ = round(ab_ + t*(bb_-ab_))
    return f"#{r:02X}{g:02X}{b_:02X}"

# ── QUERY A: SEGMENT REVENUE & BILLS ──────────────────────────────────────
walk_in_bills    = 105
walk_in_revenue  = 23508.0
staff_bills      = 55
staff_revenue    = 7677.1
credit_notes     = 0.0

net_sales    = walk_in_revenue + staff_revenue - credit_notes   # 31185.1
total_bills  = walk_in_bills + staff_bills                       # 160
avg_ticket   = round(net_sales / total_bills)                    # 195
signed_pct   = round((net_sales - 40000) / 40000 * 100, 1)      # -22.0
walk_in_pct  = round(walk_in_bills / total_bills * 100, 1)       # 65.6
staff_pct    = round(staff_bills  / total_bills * 100, 1)        # 34.4
target_icon  = "🔥" if net_sales>=50000 else ("✅" if net_sales>=40000 else "⚠️")

scalars.update({
    "net_sales":       fmt(net_sales),
    "signed_pct":      f"{signed_pct:+.1f}".replace("+","") if signed_pct<0 else f"+{signed_pct}",
    "target_icon":     target_icon,
    "total_bills":     str(total_bills),
    "walk_in_bills":   str(walk_in_bills),
    "walk_in_revenue": fmt(walk_in_revenue),
    "walk_in_pct":     str(walk_in_pct),
    "staff_bills":     str(staff_bills),
    "staff_revenue":   fmt(staff_revenue),
    "staff_pct":       str(staff_pct),
    "avg_ticket":      str(avg_ticket),
})

# ── QUERY F: 5-DAY ROLLING (avg_5d, avg_bills, avg_ticket_bench) ─────────
qf = [
    {"net_sales":37579.6, "bills":186},
    {"net_sales":29538.2, "bills":168},
    {"net_sales":29783.3, "bills":145},
    {"net_sales":41166.2, "bills":185},
    {"net_sales":29718.7, "bills":161},
]
avg_5d         = round(sum(r["net_sales"] for r in qf) / len(qf))   # 33557
avg_bills_5d   = round(sum(r["bills"]     for r in qf) / len(qf))   # 169
avg_ticket_bench = round(avg_5d / avg_bills_5d)                       # 199
bills_arrow    = "↑" if total_bills >= avg_bills_5d else "↓"
ticket_arrow   = "↑" if avg_ticket >= avg_ticket_bench else "↓"

scalars.update({
    "avg_5d":           fmt(avg_5d),
    "avg_bills":        str(avg_bills_5d),
    "avg_ticket_bench": str(avg_ticket_bench),
    "bills_arrow":      bills_arrow,
    "ticket_arrow":     ticket_arrow,
})

# ── QUERY I: MTD ──────────────────────────────────────────────────────────
net_mtd  = 429386.9
mtd_days_val = 12
avg_mtd  = round(net_mtd / mtd_days_val)  # 35782
mtd_signed_pct = round((avg_mtd - 40000) / 40000 * 100, 1)  # -10.5

scalars.update({
    "net_mtd":       fmt(net_mtd),
    "avg_mtd":       fmt(avg_mtd),
    "mtd_days":      str(mtd_days_val),
    "mtd_month":     "June 2026",
    "mtd_signed_pct": f"{mtd_signed_pct:+.1f}".lstrip("+") if mtd_signed_pct<0 else f"+{mtd_signed_pct}",
})

# ── QUERY H: 35-DAY PER-DAY PER-SEGMENT → 30-day strip + chart + weekly ──
qh_raw = [
    # (date_str, segment, net_sales, bills)
    ("2026-05-09","Staff",  11821.46, 73),  ("2026-05-09","Walk-In",32736.0,142),
    ("2026-05-10","Staff",  13392.2,  94),  ("2026-05-10","Walk-In",35064.0,158),
    ("2026-05-11","Staff",  10858.86, 76),  ("2026-05-11","Walk-In",22266.0,104),
    ("2026-05-12","Staff",  11160.0,  78),  ("2026-05-12","Walk-In",28961.0,116),
    ("2026-05-13","Staff",  16067.7, 102),  ("2026-05-13","Walk-In",23957.0,111),
    ("2026-05-14","Staff",  12070.7,  79),  ("2026-05-14","Walk-In",23288.0,112),
    ("2026-05-15","Staff",  13679.4,  74),  ("2026-05-15","Walk-In",31218.0,139),
    ("2026-05-16","Staff",  11144.8,  74),  ("2026-05-16","Walk-In",26853.0,123),
    ("2026-05-17","Staff",  12228.9,  83),  ("2026-05-17","Walk-In",28968.0,138),
    ("2026-05-18","Staff",  10443.4,  75),  ("2026-05-18","Walk-In",29533.0,132),
    ("2026-05-19","Staff",   8242.8,  55),  ("2026-05-19","Walk-In",30575.0,133),
    ("2026-05-20","Staff",  11338.7,  76),  ("2026-05-20","Walk-In",24285.0,114),
    ("2026-05-21","Staff",   6224.0,  47),  ("2026-05-21","Walk-In",17322.0, 86),
    ("2026-05-22","Staff",  15109.2,  87),  ("2026-05-22","Walk-In",22623.0,110),
    ("2026-05-23","Staff",  10007.0,  72),  ("2026-05-23","Walk-In",25946.0,112),
    ("2026-05-24","Staff",  10707.6,  74),  ("2026-05-24","Walk-In",26407.0,117),
    ("2026-05-25","Staff",   8525.5,  63),  ("2026-05-25","Walk-In",32494.0,132),
    ("2026-05-26","Staff",  10427.6,  64),  ("2026-05-26","Walk-In",31940.0,123),
    ("2026-05-27","Staff",  12681.4,  85),  ("2026-05-27","Walk-In",20012.0,107),
    ("2026-05-28","Staff",   9930.8,  65),  ("2026-05-28","Walk-In",26573.0,121),
    ("2026-05-29","Staff",  10340.5,  71),  ("2026-05-29","Walk-In",37022.0,155),
    ("2026-05-30","Staff",  11424.8,  75),  ("2026-05-30","Walk-In",24169.0,108),
    ("2026-05-31","Staff",  12473.9,  84),  ("2026-05-31","Walk-In",27497.0,132),
    ("2026-06-01","Staff",  13023.7,  83),  ("2026-06-01","Walk-In",27581.0,131),
    ("2026-06-02","Staff",   7957.9,  54),  ("2026-06-02","Walk-In",29833.0,131),
    ("2026-06-03","Staff",  15291.8,  91),  ("2026-06-03","Walk-In",25339.0,112),
    ("2026-06-04","Staff",  10156.6,  66),  ("2026-06-04","Walk-In",21643.0,112),
    ("2026-06-05","Staff",   9948.8,  67),  ("2026-06-05","Walk-In",27306.0,123),
    ("2026-06-06","Staff",   9763.0,  67),  ("2026-06-06","Walk-In",32572.0,140),
    ("2026-06-07","Staff",  10333.6,  74),  ("2026-06-07","Walk-In",27246.0,112),
    ("2026-06-08","Staff",   8598.2,  64),  ("2026-06-08","Walk-In",20940.0,104),
    ("2026-06-09","Staff",   9678.3,  56),  ("2026-06-09","Walk-In",20105.0, 89),
    ("2026-06-10","Staff",   7971.2,  52),  ("2026-06-10","Walk-In",33195.0,133),
    ("2026-06-11","Staff",   7230.7,  49),  ("2026-06-11","Walk-In",22488.0,112),
    ("2026-06-12","Staff",   7677.1,  55),  ("2026-06-12","Walk-In",23508.0,105),
]

from collections import defaultdict
day_net = defaultdict(float)
day_walk = defaultdict(int)
day_staff = defaultdict(int)
for (d, seg, ns, b) in qh_raw:
    day_net[d] += ns
    if seg=="Walk-In": day_walk[d] += b
    else:              day_staff[d] += b

all_days_35 = sorted(day_net.keys())  # 35 days from 2026-05-09

# 30-day window: 2026-05-14 to 2026-06-12
days_30 = [d for d in all_days_35 if d >= "2026-05-14"]  # 30 days

net_30d   = sum(day_net[d] for d in days_30)   # 1,113,112.9
avg_30d   = round(net_30d / len(days_30))       # 37104
chart_max = max(day_net[d] for d in days_30)

# MTD avg line
mtd_line_px = round(min(avg_mtd, chart_max) / chart_max * 90)

scalars.update({
    "net_30d":      fmt(net_30d),
    "avg_30d":      fmt(avg_30d),
    "mtd_line_px":  str(mtd_line_px),
})

# Monthly abbr helpers
TH_MONTH = ["","ม.ค.","ก.พ.","มี.ค.","เม.ย.","พ.ค.","มิ.ย.","ก.ค.","ส.ค.","ก.ย.","ต.ค.","พ.ย.","ธ.ค."]
EN_MONTH  = ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

def bar_title_str(d, ns):
    y,m,day = d.split("-")
    return f"{int(day)} {EN_MONTH[int(m)]}: ฿{fmt(ns)}"

chart_days = []
chart_labels = []
for d in days_30:
    ns   = day_net[d]
    bpx  = max(2, round(ns / chart_max * 90))
    bc   = "#27AE60" if ns >= 40000 else "#E74C3C"
    y,m,day = d.split("-")
    lbl  = f"{int(day):02d}"
    is_report = (d == REPORT_DATE)
    chart_days.append({"bar_px": str(bpx), "bar_color": bc, "bar_title": bar_title_str(d, ns)})
    chart_labels.append({
        "day_label":    lbl,
        "label_color":  "#5551FE" if is_report else "#AAA",
        "label_weight": "700"     if is_report else "400",
    })

# avg_bills_30d
bills_30d_total = sum(day_walk[d]+day_staff[d] for d in days_30)
avg_bills_30d = round(bills_30d_total / len(days_30))
scalars["avg_bills_30d"] = str(avg_bills_30d)

# ── 5-WEEK CUSTOMER TREND ─────────────────────────────────────────────────
# weeks: newest w=1 (06/06-12/06) ... oldest w=5 (09/05-15/05)
week_bounds = []  # (start_date, end_date) oldest→newest
for w in range(5, 0, -1):
    end   = "2026-06-12"
    # end of week w (w=1 is today, w=5 is oldest)
    from datetime import date, timedelta
    ed = date(2026,6,12) - timedelta(days=(w-1)*7)
    sd = ed - timedelta(days=6)
    week_bounds.append((str(sd), str(ed)))

def week_label(sd, ed):
    """Format week label, cross-month aware."""
    sy,sm,sday = sd.split("-"); ey,em,eday = ed.split("-")
    if sm == em:
        return f"{int(sday)}–{int(eday)} {TH_MONTH[int(sm)]}"
    else:
        return f"{int(sday)} {TH_MONTH[int(sm)]}–{int(eday)} {TH_MONTH[int(em)]}"

CURRENT_WEEK = week_bounds[-1]  # newest (w=1)

week_headers_list = []
walk_cells_list   = []
staff_cells_list  = []
total_cells_list  = []

prev_walk = prev_staff = prev_total = None
for (sd, ed) in week_bounds:
    wdays = [d for d in all_days_35 if sd <= d <= ed]
    w_walk  = sum(day_walk[d]  for d in wdays)
    w_staff = sum(day_staff[d] for d in wdays)
    w_total = w_walk + w_staff
    is_cur  = (sd, ed) == CURRENT_WEEK
    lbl     = week_label(sd, ed)
    week_headers_list.append({
        "label":      lbl,
        "head_color": "#5551FE" if is_cur else "#888",
        "head_bg":    "#EEECFF" if is_cur else "#F8F9FA",
    })
    def cell(cur_val, prev_val):
        bg  = "#EEECFF" if is_cur else "#FFFFFF"
        wt  = "700" if is_cur else "400"
        if prev_val is None or prev_val == 0:
            return {"val": fmt(cur_val), "pct": "", "color": "#888", "weight": wt, "bg": bg}
        p = round((cur_val - prev_val) / prev_val * 100, 1)
        pct_str = f"▲+{p}%" if p >= 0 else f"▼{p}%"
        col = "#27AE60" if p >= 0 else "#E74C3C"
        return {"val": fmt(cur_val), "pct": pct_str, "color": col, "weight": wt, "bg": bg}

    walk_cells_list.append(cell(w_walk,  prev_walk))
    staff_cells_list.append(cell(w_staff, prev_staff))
    # total row is always 700 per template
    tc = cell(w_total, prev_total)
    tc["weight"] = "700"
    total_cells_list.append(tc)
    prev_walk = w_walk; prev_staff = w_staff; prev_total = w_total

# ── QUERY J: 14-DAY HEATMAP ──────────────────────────────────────────────
qj = [
    {"d":"2026-05-30","net":35593.8, "bills":183},
    {"d":"2026-05-31","net":39970.9, "bills":216},
    {"d":"2026-06-01","net":40604.7, "bills":214},
    {"d":"2026-06-02","net":37790.9, "bills":185},
    {"d":"2026-06-03","net":40630.8, "bills":203},
    {"d":"2026-06-04","net":31799.6, "bills":178},
    {"d":"2026-06-05","net":37254.8, "bills":190},
    {"d":"2026-06-06","net":42335.0, "bills":207},
    {"d":"2026-06-07","net":37579.6, "bills":186},
    {"d":"2026-06-08","net":29538.2, "bills":168},
    {"d":"2026-06-09","net":29783.3, "bills":145},
    {"d":"2026-06-10","net":41166.2, "bills":185},
    {"d":"2026-06-11","net":29718.7, "bills":161},
    {"d":"2026-06-12","net":31185.1, "bills":160},
]
j_by_date = {r["d"]: r for r in qj}

# last 7 days for display
from datetime import date, timedelta
display_7 = [(date(2026,6,12)-timedelta(days=6-i)).isoformat() for i in range(7)]

TH_WEEKDAY = ["จ.","อ.","พ.","พฤ.","ศ.","ส.","อา."]  # Mon=0..Sun=6

def shade(vals):
    lo, hi = min(vals), max(vals)
    out = []
    for v in vals:
        t = 0.5 if hi==lo else (v-lo)/(hi-lo)
        out.append(t)
    return out

rev_vals  = [j_by_date[d]["net"]   if d in j_by_date else 0 for d in display_7]
bill_vals = [j_by_date[d]["bills"] if d in j_by_date else 0 for d in display_7]
tick_vals = [round(j_by_date[d]["net"]/j_by_date[d]["bills"]) if d in j_by_date and j_by_date[d]["bills"]>0 else 0 for d in display_7]

rev_t   = shade(rev_vals)
bill_t  = shade(bill_vals)
tick_t  = shade(tick_vals)

rev_max_i  = rev_vals.index(max(rev_vals))
bill_max_i = bill_vals.index(max(bill_vals))
tick_max_i = tick_vals.index(max(tick_vals))

heatmap_rows = []
for i, d in enumerate(display_7):
    dt = date.fromisoformat(d)
    th_wd  = TH_WEEKDAY[dt.weekday()]
    day_th = f"{th_wd} {dt.day}/{dt.month}"
    day_wt = "700" if d == REPORT_DATE else "400"

    rev_bg  = lerp_hex("#FBF3EA","#C9C7FF", rev_t[i])
    bill_bg = lerp_hex("#FBF3EA","#C9C7FF", bill_t[i])
    tick_bg = lerp_hex("#FBF3EA","#C9C7FF", tick_t[i])

    # WoW vs same weekday last week
    prev_d = (dt - timedelta(days=7)).isoformat()
    prev_r = j_by_date.get(prev_d)
    if prev_r is None or prev_r["net"]==0:
        wow_pct="—"; wow_color="#888"; wow_weight="400"
    else:
        p = round((j_by_date[d]["net"] - prev_r["net"]) / prev_r["net"] * 100, 1) if d in j_by_date else 0
        wow_pct = f"+{p}%" if p>=0 else f"{p}%"
        wow_color = "#27AE60" if p>=0 else "#E74C3C"
        wow_weight = "700" if abs(p)>=10 else "400"

    row = {
        "day_label_th": day_th,
        "day_weight":   day_wt,
        "rev":          fmt(j_by_date[d]["net"]) if d in j_by_date else "0",
        "rev_bg":       rev_bg,
        "rev_fg":       "#2C3E50",
        "rev_weight":   "700" if i==rev_max_i else "400",
        "bills":        str(bill_vals[i]),
        "bills_bg":     bill_bg,
        "bills_fg":     "#2C3E50",
        "bills_weight": "700" if i==bill_max_i else "400",
        "ticket":       str(tick_vals[i]),
        "ticket_bg":    tick_bg,
        "ticket_fg":    "#2C3E50",
        "ticket_weight":"700" if i==tick_max_i else "400",
        "wow_pct":      wow_pct,
        "wow_color":    wow_color,
        "wow_weight":   wow_weight,
    }
    heatmap_rows.append(row)

# ── QUERY B & C: TOP-10 ───────────────────────────────────────────────────
RICE_ALLOW = {"K008","K013","K016","K017","K037","K038","K039","K040","K041","K042","K043","K044","K045","K046","K047"}
FC_PCT = {
    "K037":"26.2","K038":"24.3","K039":"23.3","K040":"29.7","K041":"26.1",
    "K042":"23.3","K043":"25.3","K045":"29.9","K046":"22.6","K047":"29.1",
    "K008":"27.2","K013":"26.0",
}

qb = [
    ("K008","ข้าวผัดโบราณ",7),("K013","ข้าวกะเพราไก่คาราเกะ",5),
    ("K014","มาม่าผัดกะเพราไก่",10),("K015","มาม่าต้มยำทรงเครื่อง",11),
    ("K017","ข้าวผัดอเมริกัน",1),("K018","แกงจืดเต้าหู้หมูสับ",5),
    ("K019","ต้มยำกุ้ง",4),("K020","หมูยอทอด",3),
    ("K021","กุยช่ายกรอบ",12),("K023","ไข่ดาว",102),
    ("K024","ไข่เจียว",16),("K025","ข้าวสวย",7),
    ("K026","กุนเชียง",2),("K028","โค้ก",59),
    ("K029","โค้ก ซีโร่",17),("K030","ชามะนาว",1),
    ("K031","เก๊กฮวย",1),("K032","ชาไทย (แก้ว)",2),
    ("K036","ลูกตาลลอยแก้ว Toddy Palm In Syrup",2),
    ("K037","ข้าวผัดกะเพราหมูสับ",44),("K038","ข้าวผัดกะเพราไก่ชิ้น",21),
    ("K039","ข้าวไก่กระเทียม",6),("K040","ข้าวหมูกระเทียม",13),
    ("K041","ข้าวไข่ยู่ยี่",12),("K042","ข้าวกะเพราดิบเถื่อน (เนื้อโคขุน)",8),
    ("K043","ข้าวกะเพราเทพหมู",10),("K045","ข้าวกะเพราเปลือย",19),
    ("K046","ข้าวไก่ผัดน้ำมันหอย",6),("K047","ข้าวหมูผัดน้ำมันหอย",6),
    ("K056","Minere Mineral Water 600 Ml",19),("K057","กุยช่ายแซ่บ",10),
]
qc = {  # itemid → (total_qty, days)
    "K008":(59,5),"K013":(56,5),"K014":(51,5),"K015":(39,5),
    "K016":(2,2), "K017":(2,2), "K018":(48,5),"K019":(21,5),
    "K020":(43,5),"K021":(84,5),"K023":(445,5),"K024":(66,5),
    "K025":(29,5),"K026":(9,4), "K028":(238,5),"K029":(57,5),
    "K030":(17,5),"K031":(16,5),"K032":(19,5),"K036":(6,3),
    "K037":(249,5),"K038":(110,5),"K039":(29,5),"K040":(53,5),
    "K041":(49,5),"K042":(48,5),"K043":(71,5),"K045":(93,5),
    "K046":(21,5),"K047":(38,5),"K056":(144,5),"K057":(31,5),
}

def avg5d_val(itemid):
    if itemid not in qc: return None  # New
    tq, d = qc[itemid]
    return round(tq / d)

def badge(qty, itemid):
    a = avg5d_val(itemid)
    if a is None:
        return "#D1ECF1","#0C5460","New"
    if a == 0:
        return "#D4EDDA","#155724","+∞%"
    p = round((qty - a) / a * 100, 1)
    lbl = f"+{p}%" if p>=0 else f"{p}%"
    if p >= 15:   return "#D4EDDA","#155724",lbl
    if p <= -10:  return "#F8D7DA","#721C24",lbl
    return "#FEF3CD","#856404",lbl

def trunc(name, maxlen=22):
    if len(name) > maxlen: return name[:maxlen-1]+"…"
    return name

# sort by qty desc then itemid
qb_sorted = sorted(qb, key=lambda x: (-x[2], x[0]))
top10_all_raw  = qb_sorted[:10]
top10_rice_raw = [x for x in qb_sorted if x[0] in RICE_ALLOW][:10]

def make_top10_rows(items):
    rows = []
    for rank, (iid, name, qty) in enumerate(items, 1):
        bbg, bfg, blbl = badge(qty, iid)
        is_rice = iid in RICE_ALLOW
        disp = ("⭐ " if is_rice else "") + trunc(name)
        row_bg = "#FFFFFF" if rank%2==1 else "#FAFAFA"
        a = avg5d_val(iid)
        rows.append({
            "rank": str(rank),
            "itemid": iid,
            "name": disp,
            "qty": str(qty),
            "avg5d": str(a) if a is not None else "—",
            "badge_bg": bbg,
            "badge_fg": bfg,
            "badge_label": blbl,
            "row_bg": row_bg,
        })
    return rows

def make_rice_rows(items):
    rows = []
    for rank, (iid, name, qty) in enumerate(items, 1):
        bbg, bfg, blbl = badge(qty, iid)
        disp = trunc(name)
        row_bg = "#FFFFFF" if rank%2==1 else "#FAFAFA"
        a = avg5d_val(iid)
        rows.append({
            "rank": str(rank),
            "itemid": iid,
            "name": disp,
            "qty": str(qty),
            "avg5d": str(a) if a is not None else "—",
            "fc_pct": FC_PCT.get(iid,"—"),
            "badge_bg": bbg,
            "badge_fg": bfg,
            "badge_label": blbl,
            "row_bg": row_bg,
        })
    return rows

top10_all  = make_top10_rows(top10_all_raw)
top10_rice = make_rice_rows(top10_rice_raw)

# ── GROUP rice_top10_lines ─────────────────────────────────────────────────
rice_lines = []
for rank, (iid, name, qty) in enumerate(top10_rice_raw, 1):
    a = avg5d_val(iid)
    if a is None or a==0: blbl="New"
    else:
        p=round((qty-a)/a*100,1); blbl=f"+{p}%" if p>=0 else f"{p}%"
    rice_lines.append(f"{rank}. {iid} {trunc(name,25)} — {qty} ({blbl})")
rice_top10_lines = "\n".join(rice_lines)

# ── QUERY D: HOURLY + ANOMALY ─────────────────────────────────────────────
qd = {  # hour → (bills, revenue)
    "01":(7,1219.0),"02":(2,620.0),"03":(1,55.0),"05":(2,216.9),
    "06":(6,974.0),"07":(3,453.5),"08":(3,593.4),"09":(4,741.0),
    "10":(8,1386.5),"11":(15,3482.6),"12":(12,2142.5),"13":(15,2198.6),
    "14":(8,1861.2),"15":(5,1455.0),"16":(7,2486.5),"17":(10,1888.2),
    "18":(13,2596.1),"19":(15,2406.7),"20":(10,1578.4),"21":(7,1232.0),
    "22":(4,903.0),"23":(3,695.0),
}
qe = {  # hour → (bills, revenue) for prev day
    "00":(4,670.0),"01":(9,1224.0),"02":(3,439.0),"03":(2,205.2),
    "06":(4,774.0),"07":(4,683.5),"08":(3,364.7),"09":(5,968.2),
    "10":(4,940.2),"11":(10,2884.4),"12":(14,2645.9),"13":(10,2549.1),
    "14":(12,1730.2),"15":(12,2257.0),"16":(9,1594.0),"17":(10,2329.7),
    "18":(7,1152.0),"19":(11,2262.4),"20":(18,2585.0),"21":(4,585.0),
    "22":(6,875.2),
}

# Revenue benchmark (used for bench column)
HOURLY_REV_BENCH = {
    "00":1149,"01":763,"02":373,"03":356,"04":240,"05":166,"06":538,"07":1636,
    "08":1910,"09":3223,"10":3827,"11":4673,"12":5768,"13":3631,"14":4196,
    "15":3000,"16":3813,"17":2969,"18":3641,"19":3069,"20":3080,"21":2162,
    "22":1562,"23":553,
}
# Bill benchmark (derived: rev_bench / historical_avg_ticket = rev_bench/189, rounded)
HOURLY_BILL_BENCH = {h: max(1, round(v/189)) for h,v in HOURLY_REV_BENCH.items()}

def is_anomaly(h):
    actual = qd.get(h,(0,0))[0]
    bench  = HOURLY_BILL_BENCH[h]
    return actual < bench * 0.50

ANOMALY_HOURS = [f"{h:02d}" for h in range(24) if is_anomaly(f"{h:02d}")]
anomaly_count = len(ANOMALY_HOURS)
scalars["anomaly_count"] = str(anomaly_count)

# top3 data from Query E2
e2_top3 = {
    "01": "ไข่ดาว ×4<br>ข้าวผัดกะเพราหมูสับ ×3<br>กุยช่ายกรอบ ×2",
    "02": "มาม่าต้มยำทรงเครื่อง ×1<br>กุยช่ายกรอบ ×1<br>ไข่ดาว ×1",
    "03": "โค้ก ×1",
    "05": "ไข่ดาว ×2<br>มาม่าผัดกะเพราไก่ ×1<br>ข้าวผัดกะเพราหมูสับ ×1",
    "06": "ข้าวผัดโบราณ ×1<br>แกงจืดเต้าหู้หมูสับ ×1<br>กุยช่ายกรอบ ×1",
    "07": "ไข่ดาว ×2<br>ข้าวผัดกะเพราหมูสับ ×2<br>ข้าวผัดอเมริกัน ×1",
    "08": "ไข่ดาว ×4<br>ข้าวหมูกระเทียม ×2<br>โค้ก ×1",
    "09": "ข้าวผัดกะเพราหมูสับ ×3<br>ไข่ดาว ×2<br>ต้มยำกุ้ง ×1",
    "10": "โค้ก ×6<br>ไข่ดาว ×5<br>ข้าวผัดกะเพราหมูสับ ×3",
    "11": "ไข่ดาว ×18<br>โค้ก ×8<br>ข้าวผัดกะเพราหมูสับ ×7",
    "12": "ไข่ดาว ×11<br>โค้ก ×7<br>ข้าวผัดกะเพราหมูสับ ×3",
    "13": "ไข่ดาว ×4<br>ข้าวผัดกะเพราหมูสับ ×3<br>ข้าวผัดกะเพราไก่ชิ้น ×3",
    "14": "ไข่ดาว ×6<br>โค้ก ×3<br>โค้ก ซีโร่ ×3",
    "15": "ไข่ดาว ×7<br>โค้ก ×5<br>ข้าวผัดกะเพราไก่ชิ้น ×3",
    "16": "ไข่ดาว ×9<br>โค้ก ×9<br>ข้าวผัดกะเพราหมูสับ ×5",
    "17": "โค้ก ซีโร่ ×6<br>ไข่ดาว ×4<br>ไข่เจียว ×4",
    "18": "ไข่ดาว ×6<br>ข้าวกะเพราเปลือย ×4<br>ข้าวกะเพราไก่คาราเกะ ×2",
    "19": "ข้าวผัดกะเพราไก่ชิ้น ×5<br>ไข่ดาว ×4<br>Minere Mineral Water… ×4",
    "20": "ไข่ดาว ×7<br>โค้ก ×4<br>ข้าวไข่ยู่ยี่ ×3",
    "21": "ไข่ดาว ×2<br>โค้ก ×2<br>Minere Mineral Water… ×2",
    "22": "ข้าวผัดโบราณ ×1<br>กุยช่ายกรอบ ×1<br>ไข่ดาว ×1",
    "23": "มาม่าผัดกะเพราไก่ ×2<br>ไข่ดาว ×2<br>โค้ก ×2",
}

def anom_note(h):
    bills = qd.get(h,(0,0))[0]
    bench = HOURLY_BILL_BENCH[h]
    if bills < bench * 0.05:
        return "🔴 near-zero"
    hi = int(h)
    if 11<=hi<=13: return "🔴 collapsed"
    if hi in [9,10]: return "⚠️ Low (pre-peak)"
    if 17<=hi<=20:   return "⚠️ Low (evening)"
    if 21<=hi<=23:   return "⚠️ Low (late)"
    return "⚠️ Low"

normal_row_idx = 0
hourly_rows = []
for h_int in range(24):
    h = f"{h_int:02d}"
    anom   = h in ANOMALY_HOURS
    d_b, d_r = qd.get(h,(0,0))
    e_b, e_r = qe.get(h,(0,0))
    if anom:
        row_bg = "#FFEBEE"
    else:
        row_bg = "#FFFFFF" if normal_row_idx%2==0 else "#FAFAFA"
        normal_row_idx += 1
    hour_color = "#C62828" if anom else "#2C3E50"
    cur_color  = "#C62828" if anom else "#2C3E50"
    prev_color = "#888888"
    cur_rev_str  = fmt(d_r) if d_r>0 else "—"
    prev_rev_str = fmt(e_r) if e_r>0 else "—"
    if e_r > 0:
        pct_raw = round((d_r - e_r) / e_r * 100)
        change_pct    = f"+{pct_raw}%" if pct_raw>=0 else f"{pct_raw}%"
        change_color  = "#27AE60" if pct_raw>=0 else "#E74C3C"
        change_weight = "700" if abs(pct_raw)>=10 else "400"
    else:
        change_pct="—"; change_color="#888"; change_weight="400"
    hour_flag = " 🚨" if anom else ""
    top3 = e2_top3.get(h, "—")
    if anom and h not in e2_top3: top3 = "—"
    bench_rev = HOURLY_REV_BENCH[h]
    note = anom_note(h) if anom else ""
    hourly_rows.append({
        "hour": f"{h_int:02d}:00",
        "hour_flag":    hour_flag,
        "row_bg":       row_bg,
        "hour_color":   hour_color,
        "prev_rev":     prev_rev_str,
        "prev_color":   prev_color,
        "cur_rev":      cur_rev_str,
        "cur_color":    cur_color,
        "change_pct":   change_pct,
        "change_color": change_color,
        "change_weight":change_weight,
        "bench":        fmt(bench_rev),
        "top3":         top3,
    })

# ── PROMO STATUS ───────────────────────────────────────────────────────────
staff10_bills = 17; set50_bills = 54
scalars.update({
    "staff10_bills":   str(staff10_bills),
    "staff10_badge_bg":"#D4EDDA",
    "staff10_badge_fg":"#155724",
    "staff10_status":  "Active",
    "set50_bills":     str(set50_bills),
    "set50_badge_bg":  "#D4EDDA",
    "set50_badge_fg":  "#155724",
    "set50_status":    "Active",
})

# ── QUERY G2: PROMO WEEKLY TREND ──────────────────────────────────────────
staff10_by_date = {
    "2026-05-09":38,"2026-05-10":45,"2026-05-11":28,"2026-05-12":33,"2026-05-13":44,
    "2026-05-14":41,"2026-05-15":25,"2026-05-16":26,"2026-05-17":39,"2026-05-18":35,
    "2026-05-19":24,"2026-05-20":31,"2026-05-21":20,"2026-05-22":36,"2026-05-23":33,
    "2026-05-24":35,"2026-05-25":32,"2026-05-26":22,"2026-05-27":40,"2026-05-28":32,
    "2026-05-29":32,"2026-05-30":32,"2026-05-31":34,"2026-06-01":33,"2026-06-02":19,
    "2026-06-03":41,"2026-06-04":28,"2026-06-05":29,"2026-06-06":37,"2026-06-07":30,
    "2026-06-08":30,"2026-06-09":22,"2026-06-10":25,"2026-06-11":19,"2026-06-12":17,
}
set50_by_date = {
    "2026-05-09":40,"2026-05-10":45,"2026-05-11":26,"2026-05-12":18,"2026-05-13":25,
    "2026-05-14":36,"2026-05-15":59,"2026-05-16":52,"2026-05-17":55,"2026-05-18":39,
    "2026-05-19":58,"2026-05-20":51,"2026-05-21":29,"2026-05-22":45,"2026-05-23":50,
    "2026-05-24":39,"2026-05-25":48,"2026-05-26":39,"2026-05-27":36,"2026-05-28":50,
    "2026-05-29":67,"2026-05-30":37,"2026-05-31":24,"2026-06-01":40,"2026-06-02":34,
    "2026-06-03":41,"2026-06-04":36,"2026-06-05":27,"2026-06-06":47,"2026-06-07":29,
    "2026-06-08":27,"2026-06-09":28,"2026-06-10":53,"2026-06-11":59,"2026-06-12":54,
}

staff10_cells_list = []
set50_cells_list   = []
prev_s10 = prev_s50 = None
for (sd, ed) in week_bounds:
    wdays = [d for d in sorted(staff10_by_date.keys()) if sd <= d <= ed]
    w_s10 = sum(staff10_by_date.get(d,0) for d in wdays)
    w_s50 = sum(set50_by_date.get(d,0)   for d in wdays)
    is_cur = (sd, ed) == CURRENT_WEEK

    def promo_cell(cur_val, prev_val):
        bg  = "#EEECFF" if is_cur else "#FFFFFF"
        wt  = "700" if is_cur else "400"
        if prev_val is None or prev_val==0:
            return {"val":fmt(cur_val),"pct":"","color":"#888","weight":wt,"bg":bg}
        p = round((cur_val - prev_val) / prev_val * 100, 1)
        pct_str = f"▲+{p}%" if p>=0 else f"▼{p}%"
        col = "#27AE60" if p>=0 else "#E74C3C"
        wt2 = "700" if abs(p)>=10 else "400"
        if is_cur: wt2 = "700"
        return {"val":fmt(cur_val),"pct":pct_str,"color":col,"weight":wt2,"bg":bg}

    staff10_cells_list.append(promo_cell(w_s10, prev_s10))
    set50_cells_list.append(promo_cell(w_s50, prev_s50))
    prev_s10 = w_s10; prev_s50 = w_s50

# ── ASSEMBLE & WRITE ───────────────────────────────────────────────────────
data = {
    "scalars": scalars,
    "repeats": {
        "chart_days":    chart_days,
        "chart_labels":  chart_labels,
        "week_headers":  week_headers_list,
        "walk_cells":    walk_cells_list,
        "staff_cells":   staff_cells_list,
        "total_cells":   total_cells_list,
        "heatmap_rows":  heatmap_rows,
        "top10_all":     top10_all,
        "top10_rice":    top10_rice,
        "hourly_rows":   hourly_rows,
        "staff10_cells": staff10_cells_list,
        "set50_cells":   set50_cells_list,
    },
    "sections": {
        "alert_banner": anomaly_count > 0,
        "promo":        (staff10_bills + set50_bills) > 0,
    },
}

with open("data.json","w",encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"data.json written. anomaly_count={anomaly_count}, net_sales={fmt(net_sales)}, bills={total_bills}")
print(f"  avg_mtd={fmt(avg_mtd)}, avg_30d={fmt(avg_30d)}, mtd_line_px={mtd_line_px}")
print(f"  rice_top10_lines:\n{rice_top10_lines}")
