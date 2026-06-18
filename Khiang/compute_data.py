#!/usr/bin/env python3
"""
compute_data.py — computes data.json for Khiang Daily Report 2026-06-17.
All source values are pinned from the NetSuite query results.
"""
import json, math

def lerp_hex(a, b, t):
    ar,ag,ab = int(a[1:3],16),int(a[3:5],16),int(a[5:7],16)
    br,bg,bb = int(b[1:3],16),int(b[3:5],16),int(b[5:7],16)
    r = round(ar + (br-ar)*t)
    g = round(ag + (bg-ag)*t)
    bv = round(ab + (bb-ab)*t)
    return f"#{r:02X}{g:02X}{bv:02X}"

def fmt_int(v):
    return f"{round(v):,}"

def signed(v, dec=1):
    s = round(v, dec)
    return f"+{s}" if s >= 0 else f"{s}"

# ── Query A ─────────────────────────────────────────────────────────────────
walk_in_bills = 103
walk_in_revenue = 25675.0
staff_bills = 60
staff_revenue = 8850.6
credit_notes = 0

net_sales = walk_in_revenue + staff_revenue - credit_notes  # 34525.6
total_bills = walk_in_bills + staff_bills  # 163
avg_ticket = round(net_sales / total_bills)  # 212
signed_pct = round((net_sales - 40000) / 40000 * 100, 1)  # -13.7
walk_in_pct = round(walk_in_bills / total_bills * 100, 1)  # 63.2
staff_pct   = round(staff_bills  / total_bills * 100, 1)   # 36.8
target_icon = "⚠️"  # < 40000

# ── Query F (5-day rolling) ──────────────────────────────────────────────────
qf = [
    ("2026-06-12", 31185.10, 160),
    ("2026-06-13", 35195.70, 177),
    ("2026-06-14", 31488.60, 172),
    ("2026-06-15", 36478.50, 193),
    ("2026-06-16", 27716.80, 158),
]
avg_5d_raw   = sum(r[1] for r in qf) / len(qf)   # 32412.94
avg_bills_5d = round(sum(r[2] for r in qf) / len(qf))  # 172
avg_ticket_bench = round(avg_5d_raw / avg_bills_5d)  # 188
bills_arrow  = "↓" if total_bills < avg_bills_5d else "↑"
ticket_arrow = "↑" if avg_ticket > avg_ticket_bench else "↓"

# ── Query I (MTD) ────────────────────────────────────────────────────────────
net_mtd  = 594792.1
mtd_days_trading = 17
avg_mtd  = round(net_mtd / mtd_days_trading)  # 34988
mtd_signed_pct = round((avg_mtd - 40000) / 40000 * 100, 1)  # -12.5

# ── Query H (35-day, all days) ───────────────────────────────────────────────
# Each entry: (date, walk_rev, staff_rev, walk_bills, staff_bills)
qh_raw = [
    ("2026-05-14", 23288, 12070.7, 112, 79),
    ("2026-05-15", 31218, 13679.4, 139, 74),
    ("2026-05-16", 26853, 11144.8, 123, 74),
    ("2026-05-17", 28968, 12228.9, 138, 83),
    ("2026-05-18", 29533, 10443.4, 132, 75),
    ("2026-05-19", 30575, 8242.8,  133, 55),   # D30_START
    ("2026-05-20", 24285, 11338.7, 114, 76),
    ("2026-05-21", 17322, 6224,    86,  47),
    ("2026-05-22", 22623, 15109.2, 110, 87),
    ("2026-05-23", 25946, 10007,   112, 72),
    ("2026-05-24", 26407, 10707.6, 117, 74),
    ("2026-05-25", 32494, 8525.5,  132, 63),
    ("2026-05-26", 31940, 10427.6, 123, 64),
    ("2026-05-27", 20012, 12681.4, 107, 85),
    ("2026-05-28", 26573, 9930.8,  121, 65),
    ("2026-05-29", 37022, 10340.5, 155, 71),
    ("2026-05-30", 24169, 11424.8, 108, 75),
    ("2026-05-31", 27497, 12473.9, 132, 84),
    ("2026-06-01", 27581, 13023.7, 131, 83),
    ("2026-06-02", 29833, 7957.9,  131, 54),
    ("2026-06-03", 25339, 15291.8, 112, 91),
    ("2026-06-04", 21643, 10156.6, 112, 66),
    ("2026-06-05", 27306, 9948.8,  123, 67),
    ("2026-06-06", 32572, 9763,    140, 67),
    ("2026-06-07", 27246, 10333.6, 112, 74),
    ("2026-06-08", 20940, 8598.2,  104, 64),
    ("2026-06-09", 20105, 9678.3,  89,  56),
    ("2026-06-10", 33195, 7971.2,  133, 52),
    ("2026-06-11", 22488, 7230.7,  112, 49),
    ("2026-06-12", 23508, 7677.1,  105, 55),
    ("2026-06-13", 26837, 8358.7,  118, 59),
    ("2026-06-14", 21394, 10094.6, 97,  75),
    ("2026-06-15", 27499, 8979.5,  124, 69),
    ("2026-06-16", 16611, 11105.8, 89,  69),
    ("2026-06-17", 25675, 8850.6,  103, 60),
]

# Collapse per day totals
qh = {}
for (d, wr, sr, wb, sb) in qh_raw:
    qh[d] = {"net_sales": wr+sr, "walk_bills": wb, "staff_bills": sb, "total_bills": wb+sb}

# 30-day window: May 19 - June 17
d30_days = sorted([d for d in qh if d >= "2026-05-19"])  # 30 days
net_30d   = sum(qh[d]["net_sales"] for d in d30_days)    # 1,079,090.9
days_30d  = len(d30_days)  # 30
avg_30d   = round(net_30d / days_30d)  # 35970

total_bills_30d = sum(qh[d]["total_bills"] for d in d30_days)
avg_bills_30d   = round(total_bills_30d / days_30d)  # 184

# MTD line position
chart_max = max(qh[d]["net_sales"] for d in d30_days)  # 47362.5 (May 29)
bar_px_max = 90
mtd_line_px = round(min(avg_mtd, chart_max) / chart_max * bar_px_max)

# 5-week customer trend (W35_START = May 14)
# Weeks: W5=May14-20, W4=May21-27, W3=May28-Jun3, W2=Jun4-10, W1=Jun11-17
def week_slice(start, end):
    return [d for d in qh if start <= d <= end]

week_ranges = [
    ("2026-05-14","2026-05-20","14–20 พ.ค."),
    ("2026-05-21","2026-05-27","21–27 พ.ค."),
    ("2026-05-28","2026-06-03","28 พ.ค.–3 มิ.ย."),
    ("2026-06-04","2026-06-10","4–10 มิ.ย."),
    ("2026-06-11","2026-06-17","11–17 มิ.ย."),
]
weeks = []
for (s,e,lbl) in week_ranges:
    ds = week_slice(s,e)
    w  = sum(qh[d]["walk_bills"]  for d in ds)
    st = sum(qh[d]["staff_bills"] for d in ds)
    tot= sum(qh[d]["total_bills"] for d in ds)
    weeks.append({"label":lbl,"walk":w,"staff":st,"total":tot})

def pct_str(cur, prev):
    if prev == 0: return ("", "#888")
    p = round((cur - prev) / prev * 100, 1)
    s = f"▲+{p}%" if p >= 0 else f"▼{p}%"
    c = "#27AE60" if p >= 0 else "#E74C3C"
    return (s, c)

week_headers = []
walk_cells, staff_cells, total_cells = [], [], []
for i, wk in enumerate(weeks):
    is_cur = (i == 4)
    week_headers.append({
        "label":     wk["label"],
        "head_color":"#5551FE" if is_cur else "#888",
        "head_bg":   "#EEECFF" if is_cur else "#F8F9FA",
    })
    bg  = "#EEECFF" if is_cur else "#FFFFFF"
    wt  = 700 if is_cur else 400
    prev_wk = weeks[i-1] if i > 0 else None

    for seg, cells in [("walk",walk_cells),("staff",staff_cells),("total",total_cells)]:
        cur_v  = wk[seg]
        prev_v = prev_wk[seg] if prev_wk else 0
        pc, cc = pct_str(cur_v, prev_v) if prev_wk else ("","#888")
        cells.append({"val": f"{cur_v:,}", "pct": pc, "color": cc, "weight": wt, "bg": bg})

# Promo weekly (G2 — main rates only: -9.81 and -16.20)
g2_staff10 = {
    "2026-05-14":41,"2026-05-15":25,"2026-05-16":26,"2026-05-17":39,"2026-05-18":35,"2026-05-19":24,"2026-05-20":31,
    "2026-05-21":20,"2026-05-22":36,"2026-05-23":33,"2026-05-24":35,"2026-05-25":32,"2026-05-26":22,"2026-05-27":40,
    "2026-05-28":32,"2026-05-29":32,"2026-05-30":32,"2026-05-31":34,
    "2026-06-01":33,"2026-06-02":19,"2026-06-03":41,
    "2026-06-04":28,"2026-06-05":29,"2026-06-06":37,"2026-06-07":30,"2026-06-08":30,"2026-06-09":22,"2026-06-10":25,
    "2026-06-11":19,"2026-06-12":17,"2026-06-13":22,"2026-06-14":28,"2026-06-15":30,"2026-06-16":19,"2026-06-17":25,
}
g2_set50 = {
    "2026-05-14":36,"2026-05-15":59,"2026-05-16":52,"2026-05-17":55,"2026-05-18":39,"2026-05-19":58,"2026-05-20":51,
    "2026-05-21":29,"2026-05-22":45,"2026-05-23":50,"2026-05-24":39,"2026-05-25":48,"2026-05-26":39,"2026-05-27":36,
    "2026-05-28":50,"2026-05-29":67,"2026-05-30":37,"2026-05-31":24,
    "2026-06-01":40,"2026-06-02":34,"2026-06-03":41,
    "2026-06-04":36,"2026-06-05":27,"2026-06-06":47,"2026-06-07":29,"2026-06-08":27,"2026-06-09":28,"2026-06-10":53,
    "2026-06-11":59,"2026-06-12":54,"2026-06-13":52,"2026-06-14":46,"2026-06-15":52,"2026-06-16":40,"2026-06-17":40,
}

staff10_cells, set50_cells = [], []
for i, (s,e,lbl) in enumerate(week_ranges):
    is_cur = (i == 4)
    bg = "#EEECFF" if is_cur else "#FFFFFF"
    wt = 700 if is_cur else 400
    ds = week_slice(s,e)
    vs10 = sum(g2_staff10.get(d,0) for d in ds)
    vs50 = sum(g2_set50.get(d,0)   for d in ds)
    if i == 0:
        pc10,cc10 = "","#888"
        pc50,cc50 = "","#888"
    else:
        prev_ds = week_slice(week_ranges[i-1][0], week_ranges[i-1][1])
        p10 = sum(g2_staff10.get(d,0) for d in prev_ds)
        p50 = sum(g2_set50.get(d,0)   for d in prev_ds)
        pc10,cc10 = pct_str(vs10, p10)
        pc50,cc50 = pct_str(vs50, p50)
    staff10_cells.append({"val":f"{vs10:,}","pct":pc10,"color":cc10,"weight":wt,"bg":bg})
    set50_cells.append(  {"val":f"{vs50:,}","pct":pc50,"color":cc50,"weight":wt,"bg":bg})

# ── Query J (14-day heatmap) ──────────────────────────────────────────────────
# 14-day window Jun 4-17; display last 7 (Jun 11-17)
qj = {
    "2026-06-04": (178,  31799.6),
    "2026-06-05": (190,  37254.8),
    "2026-06-06": (207,  42335.0),
    "2026-06-07": (186,  37579.6),
    "2026-06-08": (168,  29538.2),
    "2026-06-09": (145,  29783.3),
    "2026-06-10": (185,  41166.2),
    "2026-06-11": (161,  29718.7),
    "2026-06-12": (160,  31185.1),
    "2026-06-13": (177,  35195.7),
    "2026-06-14": (172,  31488.6),
    "2026-06-15": (193,  36478.5),
    "2026-06-16": (158,  27716.8),
    "2026-06-17": (163,  34525.6),
}
display_days = ["2026-06-11","2026-06-12","2026-06-13","2026-06-14","2026-06-15","2026-06-16","2026-06-17"]
HM_LO = '#FBF3EA'; HM_HI = '#C9C7FF'
th_weekdays = {0:"จ",1:"อ",2:"พ",3:"พฤ",4:"ศ",5:"ส",6:"อา"}

def date_wd(d_str):
    from datetime import date
    y,m,day = map(int, d_str.split("-"))
    return date(y,m,day).weekday()  # 0=Mon

# Collect metrics for 7 display rows
rev_vals    = [qj[d][1] for d in display_days]
bills_vals  = [qj[d][0] for d in display_days]
ticket_vals = [round(qj[d][1]/qj[d][0]) for d in display_days]

def shade(vals, v):
    lo, hi = min(vals), max(vals)
    t = 0.5 if hi == lo else (v - lo) / (hi - lo)
    return lerp_hex(HM_LO, HM_HI, t)

rev_max    = max(rev_vals);    rev_max_i    = rev_vals.index(rev_max)
bills_max  = max(bills_vals);  bills_max_i  = bills_vals.index(bills_max)
ticket_max = max(ticket_vals); ticket_max_i = ticket_vals.index(ticket_max)

heatmap_rows = []
for i, d in enumerate(display_days):
    bills_v  = bills_vals[i]
    rev_v    = rev_vals[i]
    ticket_v = ticket_vals[i]
    wd = date_wd(d)
    day_num = d.split("-")[2].lstrip("0")
    month_num = d.split("-")[1].lstrip("0")
    day_th = f"{th_weekdays[wd]} {day_num}/{month_num}"
    is_report = (d == "2026-06-17")

    prev_d = f"2026-{d[5:7]}-{int(d[8:10])-7:02d}"  # roughly 7 days back
    # Actually need exact prev date from qj:
    from datetime import date, timedelta
    dt = date(*map(int, d.split("-")))
    prev_dt = dt - timedelta(days=7)
    prev_key = prev_dt.isoformat()
    if prev_key in qj and qj[prev_key][1] > 0:
        pv = qj[prev_key][1]
        p  = round((rev_v - pv) / pv * 100, 1)
        wow_pct = f"+{p}%" if p >= 0 else f"{p}%"
        wow_color = "#27AE60" if p >= 0 else "#E74C3C"
        wow_weight = 700 if abs(p) >= 10 else 400
    else:
        wow_pct, wow_color, wow_weight = "—", "#888", 400

    heatmap_rows.append({
        "day_label_th": day_th,
        "day_weight":   700 if is_report else 400,
        "rev":          fmt_int(rev_v),
        "rev_bg":       shade(rev_vals, rev_v),
        "rev_fg":       "#2C3E50",
        "rev_weight":   700 if i == rev_max_i else 400,
        "bills":        str(bills_v),
        "bills_bg":     shade(bills_vals, bills_v),
        "bills_fg":     "#2C3E50",
        "bills_weight": 700 if i == bills_max_i else 400,
        "ticket":       fmt_int(ticket_v),
        "ticket_bg":    shade(ticket_vals, ticket_v),
        "ticket_fg":    "#2C3E50",
        "ticket_weight":700 if i == ticket_max_i else 400,
        "wow_pct":      wow_pct,
        "wow_color":    wow_color,
        "wow_weight":   wow_weight,
    })

# ── 30-day chart ──────────────────────────────────────────────────────────────
chart_days_list, chart_labels_list = [], []
for d in d30_days:
    ns  = qh[d]["net_sales"]
    bp  = max(2, round(ns / chart_max * bar_px_max))
    bc  = "#27AE60" if ns >= 40000 else "#E74C3C"
    dl  = d.split("-")[2].lstrip("0")   # day of month
    is_rd = (d == "2026-06-17")
    chart_days_list.append({
        "bar_px":    str(bp),
        "bar_color": bc,
        "bar_title": f"฿{fmt_int(ns)} ({d})",
    })
    chart_labels_list.append({
        "day_label":    dl,
        "label_color":  "#5551FE" if is_rd else "#AAA",
        "label_weight": "700" if is_rd else "400",
    })

# ── Top 10 All Menu ───────────────────────────────────────────────────────────
rice_allow = {"K008","K013","K016","K017","K037","K038","K039","K040",
              "K041","K042","K043","K044","K045","K046","K047"}
fc_pct_map = {
    "K037":26.2,"K038":24.3,"K039":23.3,"K040":29.7,"K041":26.1,"K042":23.3,
    "K043":25.3,"K045":29.9,"K046":22.6,"K047":29.1,"K008":27.2,"K013":26.0,
}

qb = [
    ("K008","ข้าวผัดโบราณ",7),("K013","ข้าวกะเพราไก่คาราเกะ",6),("K014","มาม่าผัดกะเพราไก่",12),
    ("K015","มาม่าต้มยำทรงเครื่อง",11),("K017","ข้าวผัดอเมริกัน",1),("K018","แกงจืดเต้าหู้หมูสับ",5),
    ("K019","ต้มยำกุ้ง",6),("K020","หมูยอทอด",3),("K021","กุยช่ายกรอบ",12),
    ("K023","ไข่ดาว",109),("K024","ไข่เจียว",8),("K025","ข้าวสวย",4),
    ("K026","กุนเชียง",1),("K028","โค้ก",61),("K032","ชาไทย (แก้ว)",2),
    ("K035","สละลอยแก้ว",1),("K036","ลูกตาลลอยแก้ว",1),
    ("K037","ข้าวผัดกะเพราหมูสับ",65),("K038","ข้าวผัดกะเพราไก่ชิ้น",16),
    ("K039","ข้าวไก่กระเทียม",12),("K040","ข้าวหมูกระเทียม",11),
    ("K041","ข้าวไข่ยู่ยี่",15),("K042","ข้าวกะเพราดิบเถื่อน",15),
    ("K043","ข้าวกะเพราเทพหมู",19),("K045","ข้าวกะเพราเป็ดย่าง",12),
    ("K046","ข้าวไก่ผัดน้ำมันหอย",3),("K047","ข้าวหมูผัดน้ำมันหอย",4),
    ("K056","Minere Water 600ml",19),("K057","กุยช่ายแซ่บ",4),
]
qc = {
    "K008":12,"K013":7,"K014":12,"K015":7,"K017":1,"K018":9,"K019":5,"K020":9,
    "K021":10,"K023":98,"K024":15,"K025":9,"K026":3,"K028":62,"K032":3,"K035":2,
    "K036":1,"K037":50,"K038":21,"K039":9,"K040":13,"K041":14,"K042":7,"K043":13,
    "K045":19,"K046":5,"K047":5,"K056":22,"K057":7,
}

def badge(qty, avg5d):
    if avg5d is None: return ("New","#D1ECF1","#0C5460")
    pct = round((qty - avg5d) / avg5d * 100, 1)
    label = f"+{pct}%" if pct >= 0 else f"{pct}%"
    if pct >= 15:   return (label,"#D4EDDA","#155724")
    if pct <= -10:  return (label,"#F8D7DA","#721C24")
    return (label,"#FEF3CD","#856404")

sorted_all = sorted(qb, key=lambda x: -x[2])[:10]
top10_all = []
for rk, (iid, nm, qty) in enumerate(sorted_all):
    a5 = qc.get(iid)
    lbl, bbg, bfg = badge(qty, a5)
    is_rice = iid in rice_allow
    row_bg = "#FFFFFF" if rk%2==0 else "#FAFAFA"
    top10_all.append({
        "rank": str(rk+1), "itemid": iid,
        "name": ("⭐ " if is_rice else "") + nm,
        "qty":  str(qty), "avg5d": str(a5) if a5 else "—",
        "badge_label": lbl, "badge_bg": bbg, "badge_fg": bfg,
        "row_bg": row_bg,
    })

rice_sorted = sorted([(iid,nm,qty) for (iid,nm,qty) in qb if iid in rice_allow], key=lambda x:-x[2])[:10]
top10_rice = []
for rk, (iid, nm, qty) in enumerate(rice_sorted):
    a5 = qc.get(iid)
    lbl, bbg, bfg = badge(qty, a5)
    row_bg = "#FFFFFF" if rk%2==0 else "#FAFAFA"
    fc = fc_pct_map.get(iid, None)
    top10_rice.append({
        "rank": str(rk+1), "itemid": iid, "name": nm,
        "qty":  str(qty), "avg5d": str(a5) if a5 else "—",
        "fc_pct": f"{fc}%" if fc else "—",
        "badge_label": lbl, "badge_bg": bbg, "badge_fg": bfg,
        "row_bg": row_bg,
    })

# ── Hourly rows ───────────────────────────────────────────────────────────────
# Query D (today) and E (yesterday) dictionaries
qd = {
    "01":(5,998.5),"02":(1,50),"03":(1,230),"04":(1,95),"05":(1,94.5),
    "06":(2,263.5),"07":(4,566.5),"08":(10,2276.9),"09":(2,460),"10":(9,1551.7),
    "11":(12,2787.4),"12":(15,2785.2),"13":(12,4044.6),"14":(8,1829.3),
    "15":(8,2474.2),"16":(10,1763.5),"17":(20,3715.9),"18":(15,3097.4),
    "19":(2,388),"20":(12,2548.9),"21":(7,1305.4),"22":(4,771.2),"23":(2,428),
}
qe = {
    "01":(7,724),"02":(2,284),"03":(2,355),"05":(3,480.2),"06":(8,1103.7),
    "07":(1,99),"08":(2,150.7),"09":(2,175),"10":(6,1026),"11":(12,1930.9),
    "12":(20,4902.9),"13":(23,4758.6),"14":(8,1707.1),"15":(5,799.7),
    "16":(7,928.5),"17":(13,1780.4),"18":(11,2095.9),"19":(9,980.2),
    "20":(7,1177),"21":(7,1798),"22":(3,460),
}

# Revenue benchmark per hour
rev_bench = {
    "00":1149,"01":763,"02":373,"03":356,"04":240,"05":166,"06":538,"07":1636,
    "08":1910,"09":3223,"10":3827,"11":4673,"12":5768,"13":3631,"14":4196,
    "15":3000,"16":3813,"17":2969,"18":3641,"19":3069,"20":3080,"21":2162,
    "22":1562,"23":553,
}
bill_bench = {h: round(rev_bench[h] / avg_ticket_bench) for h in rev_bench}

# Anomaly flagged hours
anomaly_hours = {"07","09","10","11","12","14","19"}

# Top3 per hour from Q E2
top3_map = {
    "01": "ข้าวผัดกะเพราหมูสับ ×4<br>ข้าวผัดโบราณ ×1<br>กุยช่ายกรอบ ×1",
    "02": "สละลอยแก้ว ×1",
    "03": "ต้มยำกุ้ง ×1",
    "04": "ข้าวผัดกะเพราหมูสับ ×1",
    "05": "ข้าวผัดกะเพราหมูสับ ×1",
    "06": "ไข่ดาว ×1<br>ข้าวไข่ยู่ยี่ ×1<br>ข้าวกะเพราเทพหมู ×1",
    "07": "ไข่ดาว ×2<br>โค้ก ×2<br>ข้าวผัดกะเพราหมูสับ ×2",
    "08": "ไข่ดาว ×7<br>โค้ก ×7<br>ข้าวผัดกะเพราหมูสับ ×3",
    "09": "ข้าวไก่กระเทียม ×2<br>ไข่ดาว ×1<br>โค้ก ×1",
    "10": "ไข่ดาว ×5<br>ข้าวผัดกะเพราหมูสับ ×4<br>โค้ก ×1",
    "11": "ไข่ดาว ×8<br>โค้ก ×6<br>ข้าวกะเพราเทพหมู ×4",
    "12": "ไข่ดาว ×8<br>โค้ก ×7<br>ข้าวผัดกะเพราหมูสับ ×7",
    "13": "โค้ก ×9<br>ไข่ดาว ×7<br>ข้าวผัดกะเพราหมูสับ ×4",
    "14": "ไข่ดาว ×8<br>โค้ก ×3<br>ข้าวผัดกะเพราหมูสับ ×3",
    "15": "ไข่ดาว ×9<br>Minere Water ×4<br>กุยช่ายกรอบ ×3",
    "16": "ไข่ดาว ×6<br>โค้ก ×4<br>ข้าวผัดกะเพราหมูสับ ×3",
    "17": "ไข่ดาว ×9<br>ข้าวผัดกะเพราหมูสับ ×7<br>มาม่าผัดกะเพราไก่ ×3",
    "18": "ไข่ดาว ×15<br>โค้ก ×8<br>ข้าวผัดกะเพราหมูสับ ×6",
    "19": "ไข่ดาว ×2<br>โค้ก ×1<br>ข้าวผัดกะเพราหมูสับ ×1",
    "20": "ไข่ดาว ×10<br>ข้าวผัดกะเพราหมูสับ ×6<br>Minere Water ×3",
    "21": "ข้าวผัดกะเพราหมูสับ ×5<br>ไข่ดาว ×4<br>โค้ก ×2",
    "22": "ไข่ดาว ×4<br>โค้ก ×3<br>ข้าวผัดกะเพราหมูสับ ×1",
    "23": "ไข่ดาว ×2<br>ข้าวผัดกะเพราหมูสับ ×2<br>โค้ก ×1",
}

all_hours = sorted(set(list(qd.keys()) + list(qe.keys())))
hourly_rows = []
for i, h in enumerate(all_hours):
    is_anom = h in anomaly_hours
    d_bills, d_rev = qd.get(h, (0,0))
    e_bills, e_rev = qe.get(h, (0,0))

    if e_rev > 0:
        pct = round((d_rev - e_rev)/e_rev*100, 1)
        cp  = f"+{pct}%" if pct >= 0 else f"{pct}%"
        cc  = "#27AE60" if pct >= 0 else "#E74C3C"
        cw  = 700 if abs(pct) >= 10 else 400
    else:
        cp, cc, cw = "—", "#888", 400

    if is_anom:
        row_bg = "#FFEBEE"
        hour_color = "#C62828"
        cur_color  = "#C62828"
    else:
        row_bg = "#FFFFFF" if i%2==0 else "#FAFAFA"
        hour_color = "#2C3E50"
        cur_color  = "#2C3E50"

    hourly_rows.append({
        "hour":         f"{h}:00",
        "hour_flag":    " 🚨" if is_anom else "",
        "hour_color":   hour_color,
        "prev_rev":     fmt_int(e_rev) if e_rev else "—",
        "prev_color":   "#888",
        "cur_rev":      fmt_int(d_rev),
        "cur_color":    cur_color,
        "change_pct":   cp,
        "change_color": cc,
        "change_weight":str(cw),
        "bench":        fmt_int(rev_bench[h]),
        "top3":         top3_map.get(h,"—"),
        "row_bg":       row_bg,
    })

# ── Assemble data.json ────────────────────────────────────────────────────────
data = {
  "scalars": {
    "report_date_display":  "17 June 2026",
    "report_day_en":        "Wednesday",
    "net_sales":            fmt_int(net_sales),
    "signed_pct":           f"{signed_pct:+.1f}",
    "target_icon":          target_icon,
    "avg_5d":               fmt_int(avg_5d_raw),
    "anomaly_count":        "7",
    "total_bills":          str(total_bills),
    "avg_bills":            str(avg_bills_5d),
    "bills_arrow":          bills_arrow,
    "walk_in_bills":        str(walk_in_bills),
    "walk_in_revenue":      fmt_int(walk_in_revenue),
    "walk_in_pct":          str(walk_in_pct),
    "staff_bills":          str(staff_bills),
    "staff_revenue":        fmt_int(staff_revenue),
    "staff_pct":            str(staff_pct),
    "avg_ticket":           str(avg_ticket),
    "avg_ticket_bench":     str(avg_ticket_bench),
    "ticket_arrow":         ticket_arrow,
    "net_30d":              fmt_int(net_30d),
    "d30_start":            "19 พ.ค.",
    "report_date_short":    "17 มิ.ย.",
    "avg_30d":              fmt_int(avg_30d),
    "mtd_month":            "June 2026",
    "avg_mtd":              fmt_int(avg_mtd),
    "net_mtd":              fmt_int(net_mtd),
    "mtd_days":             str(mtd_days_trading),
    "mtd_signed_pct":       f"{mtd_signed_pct:+.1f}",
    "mtd_line_px":          str(mtd_line_px),
    "prev_date_short":      "16 มิ.ย.",
    "staff10_bills":        "25",
    "set50_bills":          "40",
    "staff10_badge_bg":     "#D4EDDA",
    "staff10_badge_fg":     "#155724",
    "staff10_status":       "Active",
    "set50_badge_bg":       "#D4EDDA",
    "set50_badge_fg":       "#155724",
    "set50_status":         "Active",
    "avg_bills_30d":        str(avg_bills_30d),
    "chaw_values":          "Curious · Team · Act Fast · Empowered · Simple",
    "generated_date":       "18 June 2026",
  },
  "repeats": {
    "top10_all":    top10_all,
    "top10_rice":   top10_rice,
    "hourly_rows":  hourly_rows,
    "chart_days":   chart_days_list,
    "chart_labels": chart_labels_list,
    "week_headers": week_headers,
    "walk_cells":   walk_cells,
    "staff_cells":  staff_cells,
    "total_cells":  total_cells,
    "staff10_cells":staff10_cells,
    "set50_cells":  set50_cells,
    "heatmap_rows": heatmap_rows,
  },
  "sections": {
    "alert_banner": True,
    "promo":        True,
  }
}

with open("data.json","w",encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("=== SUMMARY ===")
print(f"net_sales: ฿{fmt_int(net_sales)}")
print(f"total_bills: {total_bills}, avg_ticket: ฿{avg_ticket}")
print(f"signed_pct: {signed_pct:+.1f}%  target_icon: {target_icon}")
print(f"avg_5d: ฿{fmt_int(avg_5d_raw)}, avg_mtd: ฿{fmt_int(avg_mtd)}, avg_30d: ฿{fmt_int(avg_30d)}")
print(f"net_30d: ฿{fmt_int(net_30d)}, net_mtd: ฿{fmt_int(net_mtd)}")
print(f"mtd_signed_pct: {mtd_signed_pct:+.1f}%")
print(f"anomaly_count: 7 (hrs: 07,09,10,11,12,14,19)")
print(f"staff10_bills: 25, set50_bills: 40")
print(f"mtd_line_px: {mtd_line_px}")
print(f"avg_bills_30d: {avg_bills_30d}")
print("data.json written OK")

# Build rice_top10_lines for group message
lines = []
for rk, (iid,nm,qty) in enumerate(rice_sorted):
    a5 = qc.get(iid)
    lbl,_,_ = badge(qty,a5)
    lines.append(f"{rk+1}. {iid} {nm} — {qty} ({lbl})")
rice_top10_lines = "\n".join(lines)
print("\nrice_top10_lines:\n" + rice_top10_lines)
