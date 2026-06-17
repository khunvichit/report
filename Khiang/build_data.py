#!/usr/bin/env python3
"""Build data.json for Khiang Daily Report — 2026-06-16."""
import json, math

def fmt(n, decimals=0):
    """Format number with commas."""
    if decimals == 0:
        return f"{int(round(n)):,}"
    return f"{round(n, decimals):,.{decimals}f}"

def lerp_hex(a, b, t):
    """Linear interpolate between two #RRGGBB colours."""
    t = max(0.0, min(1.0, t))
    ar, ag, ab = int(a[1:3],16), int(a[3:5],16), int(a[5:7],16)
    br, bg, bb = int(b[1:3],16), int(b[3:5],16), int(b[5:7],16)
    rr = int(ar + (br-ar)*t)
    rg = int(ag + (bg-ag)*t)
    rb = int(ab + (bb-ab)*t)
    return f"#{rr:02X}{rg:02X}{rb:02X}"

def badge(pct):
    """Badge colours based on % vs 5d avg."""
    if pct == "NEW":
        return ("#D1ECF1", "#0C5460", "New")
    p = float(pct)
    if p >= 15:
        return ("#D4EDDA", "#155724", f"+{p:.1f}%")
    elif p <= -10:
        return ("#F8D7DA", "#721C24", f"{p:.1f}%")
    else:
        s = f"+{p:.1f}%" if p >= 0 else f"{p:.1f}%"
        return ("#FEF3CD", "#856404", s)

def signed(p):
    return f"+{p:.1f}%" if p >= 0 else f"{p:.1f}%"

# ── SCALARS ──────────────────────────────────────────────────────────────────
net_sales_raw       = 27716.8
walk_in_bills       = 89
walk_in_revenue     = 16611.0
staff_bills         = 69
staff_revenue       = 11105.8
credit_notes        = 0.0
total_bills         = 158
avg_ticket_raw      = round(net_sales_raw / total_bills)   # 175
signed_pct_raw      = round((net_sales_raw - 40000) / 40000 * 100, 1)  # -30.7
walk_in_pct_raw     = round(walk_in_bills / total_bills * 100, 1)       # 56.3
staff_pct_raw       = round(staff_bills  / total_bills * 100, 1)        # 43.7
avg_5d_raw          = 32813
avg_bills_5d        = 173  # round(mean(161,160,177,172,193))
avg_ticket_bench_raw= 190  # round(32813/173)
net_30d_raw         = 1084541.7
avg_30d_raw         = 36151
net_mtd_raw         = 560266.5
avg_mtd_raw         = 35017
mtd_days            = 16
mtd_signed_pct_raw  = round((avg_mtd_raw - 40000) / 40000 * 100, 1)  # -12.5
staff10_bills       = 19
set50_bills         = 40
anomaly_count       = 10
avg_bills_30d       = 185

chart_max = 47362.5
bar_px_max = 90
mtd_line_px = round(min(avg_mtd_raw, chart_max) / chart_max * bar_px_max)  # 67

target_icon = "⚠️"   # net_sales < 40000
bills_arrow = "↓"    # 158 < 173
ticket_arrow= "↓"    # 175 < 190

scalars = {
    "report_date_display": "16 June 2026",
    "report_date_short":   "16 มิ.ย.",
    "prev_date_short":     "15 มิ.ย.",
    "report_day_en":       "Monday",
    "report_day_th":       "จันทร์",
    "report_year":         "2026",
    "generated_date":      "17 June 2026",
    "net_sales":           fmt(net_sales_raw),
    "signed_pct":          f"{signed_pct_raw:+.1f}",
    "target_icon":         target_icon,
    "avg_5d":              fmt(avg_5d_raw),
    "anomaly_count":       str(anomaly_count),
    "total_bills":         str(total_bills),
    "avg_bills":           str(avg_bills_5d),
    "bills_arrow":         bills_arrow,
    "walk_in_bills":       str(walk_in_bills),
    "walk_in_revenue":     fmt(walk_in_revenue),
    "walk_in_pct":         f"{walk_in_pct_raw:.1f}",
    "staff_bills":         str(staff_bills),
    "staff_revenue":       fmt(staff_revenue),
    "staff_pct":           f"{staff_pct_raw:.1f}",
    "avg_ticket":          fmt(avg_ticket_raw),
    "avg_ticket_bench":    fmt(avg_ticket_bench_raw),
    "ticket_arrow":        ticket_arrow,
    "net_30d":             fmt(net_30d_raw),
    "d30_start":           "18 พ.ค.",
    "avg_30d":             fmt(avg_30d_raw),
    "mtd_month":           "June 2026",
    "avg_mtd":             fmt(avg_mtd_raw),
    "net_mtd":             fmt(net_mtd_raw),
    "mtd_days":            str(mtd_days),
    "mtd_signed_pct":      f"{mtd_signed_pct_raw:+.1f}",
    "mtd_line_px":         str(mtd_line_px),
    "avg_bills_30d":       str(avg_bills_30d),
    "staff10_bills":       str(staff10_bills),
    "staff10_badge_bg":    "#D4EDDA",
    "staff10_badge_fg":    "#155724",
    "staff10_status":      "Active",
    "set50_bills":         str(set50_bills),
    "set50_badge_bg":      "#D4EDDA",
    "set50_badge_fg":      "#155724",
    "set50_status":        "Active",
    "chaw_values":         "Curious · Team · Act Fast · Empowered · Simple",
}

# ── CHART (30-day bar chart) ──────────────────────────────────────────────────
chart_data_30d = [
    ("2026-05-18", 39976.4), ("2026-05-19", 38817.8), ("2026-05-20", 35623.7),
    ("2026-05-21", 23546.0), ("2026-05-22", 37732.2), ("2026-05-23", 35953.0),
    ("2026-05-24", 37114.6), ("2026-05-25", 41019.5), ("2026-05-26", 42367.6),
    ("2026-05-27", 32693.4), ("2026-05-28", 36503.8), ("2026-05-29", 47362.5),
    ("2026-05-30", 35593.8), ("2026-05-31", 39970.9), ("2026-06-01", 40604.7),
    ("2026-06-02", 37790.9), ("2026-06-03", 40630.8), ("2026-06-04", 31799.6),
    ("2026-06-05", 37254.8), ("2026-06-06", 42335.0), ("2026-06-07", 37579.6),
    ("2026-06-08", 29538.2), ("2026-06-09", 29783.3), ("2026-06-10", 41166.2),
    ("2026-06-11", 29718.7), ("2026-06-12", 31185.1), ("2026-06-13", 35195.7),
    ("2026-06-14", 31488.6), ("2026-06-15", 36478.5), ("2026-06-16", 27716.8),
]

chart_days = []
chart_labels = []
for date, ns in chart_data_30d:
    bp = max(2, round(ns / chart_max * bar_px_max))
    bc = "#27AE60" if ns >= 40000 else "#E74C3C"
    day = date.split("-")[2]  # "18","19",...
    is_report = (date == "2026-06-16")
    chart_days.append({
        "bar_px":    str(bp),
        "bar_color": bc,
        "bar_title": f"฿{fmt(ns)} ({date})",
    })
    chart_labels.append({
        "day_label":    day,
        "label_color":  "#5551FE" if is_report else "#AAA",
        "label_weight": "700" if is_report else "400",
    })

# ── WEEK HEADERS (shared for customer trend + promo trend tables) ────────────
week_defs = [
    # (w, start, end, label, is_current)
    (5, "2026-05-13", "2026-05-19", "13–19 พ.ค.",        False),
    (4, "2026-05-20", "2026-05-26", "20–26 พ.ค.",        False),
    (3, "2026-05-27", "2026-06-02", "27 พ.ค.–2 มิ.ย.",  False),
    (2, "2026-06-03", "2026-06-09", "3–9 มิ.ย.",          False),
    (1, "2026-06-10", "2026-06-16", "10–16 มิ.ย.",        True),
]

week_headers = []
for w, s, e, label, is_cur in week_defs:
    week_headers.append({
        "label":     label,
        "head_color": "#5551FE" if is_cur else "#888",
        "head_bg":    "#EEECFF" if is_cur else "#F8F9FA",
    })

# ── CUSTOMER WEEKLY TABLE ─────────────────────────────────────────────────────
# Bills per week (Walk-In / Staff / Total) — oldest first
cust_weeks = [
    {"walk": 888, "staff": 542},  # w5
    {"walk": 794, "staff": 483},  # w4
    {"walk": 885, "staff": 517},  # w3
    {"walk": 792, "staff": 485},  # w2
    {"walk": 778, "staff": 428},  # w1 current
]

def wow_pct_str(cur, prev):
    if prev == 0:
        return ("", "#888", "400")
    p = round((cur - prev) / prev * 100, 1)
    s = f"▲+{p:.1f}%" if p >= 0 else f"▼{p:.1f}%"
    col = "#27AE60" if p >= 0 else "#E74C3C"
    return (s, col, "400")

def make_cells(vals, is_current_flags, always_bold=False):
    cells = []
    for i, (val, is_cur) in enumerate(zip(vals, is_current_flags)):
        pct, col, _ = wow_pct_str(val, vals[i-1]) if i > 0 else ("", "#888", "400")
        w = "700" if is_cur or always_bold else "400"
        bg = "#EEECFF" if is_cur else "#FFFFFF"
        cells.append({
            "val":    f"{val:,}",
            "pct":    pct,
            "color":  col,
            "weight": w,
            "bg":     bg,
        })
    return cells

is_cur_flags = [False, False, False, False, True]
walk_vals  = [w["walk"]  for w in cust_weeks]
staff_vals = [w["staff"] for w in cust_weeks]
total_vals = [w["walk"]+w["staff"] for w in cust_weeks]

walk_cells  = make_cells(walk_vals,  is_cur_flags)
staff_cells = make_cells(staff_vals, is_cur_flags)
total_cells = make_cells(total_vals, is_cur_flags, always_bold=True)

# ── HEATMAP (7 days, oldest→newest) ──────────────────────────────────────────
# Days 2026-06-10..2026-06-16 with data from Query J
heatmap_data = [
    ("2026-06-10", "อ 10/6", 41166.2, 185, 223),
    ("2026-06-11", "พ 11/6", 29718.7, 161, 185),
    ("2026-06-12", "พฤ 12/6", 31185.1, 160, 195),
    ("2026-06-13", "ศ 13/6", 35195.7, 177, 199),
    ("2026-06-14", "ส 14/6", 31488.6, 172, 183),
    ("2026-06-15", "อา 15/6", 36478.5, 193, 189),
    ("2026-06-16", "จ 16/6", 27716.8, 158, 175),
]
wow_prev = {
    "2026-06-10": 40630.8, "2026-06-11": 31799.6, "2026-06-12": 37254.8,
    "2026-06-13": 42335.0, "2026-06-14": 37579.6, "2026-06-15": 29538.2,
    "2026-06-16": 29783.3,
}

revs  = [r for _,_,r,_,_ in heatmap_data]
bills_h = [b for _,_,_,b,_ in heatmap_data]
tickets = [t for _,_,_,_,t in heatmap_data]

lo_r, hi_r = min(revs),    max(revs)
lo_b, hi_b = min(bills_h), max(bills_h)
lo_t, hi_t = min(tickets),  max(tickets)

def shade(val, lo, hi):
    t = 0.5 if hi == lo else (val - lo) / (hi - lo)
    return lerp_hex("#FBF3EA", "#C9C7FF", t)

heatmap_rows = []
for date, label, rev, bills_v, ticket in heatmap_data:
    is_rd = (date == "2026-06-16")
    rev_bg  = shade(rev, lo_r, hi_r)
    bill_bg = shade(bills_v, lo_b, hi_b)
    tick_bg = shade(ticket, lo_t, hi_t)
    # bold the max in each column
    rev_w   = "700" if rev    == hi_r else "400"
    bill_w  = "700" if bills_v == hi_b else "400"
    tick_w  = "700" if ticket  == hi_t else "400"
    # WoW
    prev = wow_prev.get(date, 0)
    if prev == 0:
        wpc, wcol, ww = "—", "#888", "400"
    else:
        p = round((rev - prev) / prev * 100, 1)
        wpc = f"+{p:.1f}%" if p >= 0 else f"{p:.1f}%"
        wcol = "#27AE60" if p >= 0 else "#E74C3C"
        ww   = "700" if abs(p) >= 10 else "400"
    heatmap_rows.append({
        "day_label_th": label,
        "day_weight":   "700" if is_rd else "400",
        "rev":          fmt(rev),
        "rev_bg":       rev_bg,
        "rev_fg":       "#2C3E50",
        "rev_weight":   rev_w,
        "bills":        str(bills_v),
        "bills_bg":     bill_bg,
        "bills_fg":     "#2C3E50",
        "bills_weight": bill_w,
        "ticket":       fmt(ticket),
        "ticket_bg":    tick_bg,
        "ticket_fg":    "#2C3E50",
        "ticket_weight":tick_w,
        "wow_pct":      wpc,
        "wow_color":    wcol,
        "wow_weight":   ww,
    })

# ── TOP 10 ALL MENU ───────────────────────────────────────────────────────────
RICE_ALLOW = {"K008","K013","K016","K017","K037","K038","K039","K040","K041","K042","K043","K044","K045","K046","K047"}
FC = {"K037":26.2,"K038":24.3,"K039":23.3,"K040":29.7,"K041":26.1,"K042":23.3,"K043":25.3,"K045":29.9,"K046":22.6,"K047":29.1,"K008":27.2,"K013":26.0}

# Query B items sorted by qty desc
qb = [
    ("K023","ไข่ดาว",89),
    ("K028","โค้ก",49),
    ("K037","ข้าวผัดกะเพราหมูสับ",30),
    ("K045","ข้าวกะเพราเปัดย่าง",25),
    ("K038","ข้าวผัดกะเพราไก่ชิ้น",19),
    ("K043","ข้าวกะเพราเทพหมู",16),
    ("K039","ข้าวไก่กระเทียม",15),
    ("K056","Minere Mineral Water 600 Ml",15),
    ("K024","ไข่เจียว",13),
    ("K008","ข้าวผัดโบราณ",11),
    ("K014","มาม่าผัดกะเพราไก่",11),
    ("K040","ข้าวหมูกระเทียม",11),
    ("K041","ข้าวไข่ยู่ยี่",10),
    ("K013","ข้าวกะเพราไก่คาราเกะ",10),
    ("K020","หมูยอทอด",9),
    ("K018","แกงจืดเต้าหู้หมูสับ",9),
    ("K029","โค้ก ซีโร่",9),
    ("K025","ข้าวสวย",7),
    ("K021","กุยช่ายกรอบ",6),
    ("K015","มาม่าต้มยำทรงเครื่อง",5),
    ("K042","ข้าวกะเพราดิบเถื่อน (เนื้อโคขุน)",5),
    ("K057","กุยช่ายแซ่บ",5),
    ("K047","ข้าวหมูผัดน้ำมันหอย",4),
    ("K019","ต้มยำกุ้ง",2),
    ("K030","ชามะนาว",2),
    ("K032","ชาไทย (แก้ว)",2),
    ("K036","ลูกตาลลอยแก้ว Toddy Palm In Syrup",2),
    ("K026","กุนเชียง",1),
]

# 5d avg from Query C
qc_avg = {
    "K008":round(59/5),"K013":round(34/5),"K014":round(56/5),"K015":round(34/5),
    "K017":round(1/1),"K018":round(42/5),"K019":round(25/5),"K020":round(39/5),
    "K021":round(62/5),"K022":round(3/2),"K023":round(488/5),"K024":round(80/5),
    "K025":round(46/5),"K026":round(13/4),"K028":round(314/5),"K029":round(70/5),
    "K030":round(9/4),"K031":round(11/5),"K032":round(18/5),"K035":round(3/2),
    "K036":round(9/5),"K037":round(257/5),"K038":round(108/5),"K039":round(34/5),
    "K040":round(66/5),"K041":round(67/5),"K042":round(38/5),"K043":round(61/5),
    "K045":round(90/5),"K046":round(21/5),"K047":round(35/5),"K056":round(118/5),
    "K057":round(29/4),
}

top10_all = []
for i, (iid, name, qty) in enumerate(qb[:10]):
    avg5d = qc_avg.get(iid, None)
    is_rice = iid in RICE_ALLOW
    display_name = ("⭐ " if is_rice else "") + name
    if avg5d is None:
        bg, fg, bl = badge("NEW")
    else:
        pct_val = (qty - avg5d) / avg5d * 100
        bg, fg, bl = badge(pct_val)
    row_bg = "#FFFFFF" if i % 2 == 0 else "#FAFAFA"
    top10_all.append({
        "rank":        str(i+1),
        "itemid":      iid,
        "name":        display_name,
        "qty":         str(qty),
        "avg5d":       str(avg5d) if avg5d else "—",
        "badge_bg":    bg,
        "badge_fg":    fg,
        "badge_label": bl,
        "row_bg":      row_bg,
    })

# ── TOP 10 RICE MENU ──────────────────────────────────────────────────────────
rice_items_sorted = [
    ("K037","ข้าวผัดกะเพราหมูสับ",30),
    ("K045","ข้าวกะเพราเปัดย่าง",25),
    ("K038","ข้าวผัดกะเพราไก่ชิ้น",19),
    ("K043","ข้าวกะเพราเทพหมู",16),
    ("K039","ข้าวไก่กระเทียม",15),
    ("K040","ข้าวหมูกระเทียม",11),
    ("K008","ข้าวผัดโบราณ",11),
    ("K041","ข้าวไข่ยู่ยี่",10),
    ("K013","ข้าวกะเพราไก่คาราเกะ",10),
    ("K042","ข้าวกะเพราดิบเถื่อน (เนื้อโคขุน)",5),
]

top10_rice = []
for i, (iid, name, qty) in enumerate(rice_items_sorted):
    avg5d = qc_avg.get(iid, None)
    fc_pct = f"{FC.get(iid, '')}%" if iid in FC else "—"
    if avg5d is None:
        bg, fg, bl = badge("NEW")
    else:
        pct_val = (qty - avg5d) / avg5d * 100
        bg, fg, bl = badge(pct_val)
    row_bg = "#FFFFFF" if i % 2 == 0 else "#FAFAFA"
    top10_rice.append({
        "rank":        str(i+1),
        "itemid":      iid,
        "name":        name,
        "qty":         str(qty),
        "avg5d":       str(avg5d) if avg5d else "—",
        "fc_pct":      fc_pct,
        "badge_bg":    bg,
        "badge_fg":    fg,
        "badge_label": bl,
        "row_bg":      row_bg,
    })

# ── HOURLY ROWS ───────────────────────────────────────────────────────────────
HOURLY_REV_BENCH = {
    0:1149,1:763,2:373,3:356,4:240,5:166,6:538,7:1636,8:1910,9:3223,10:3827,
    11:4673,12:5768,13:3631,14:4196,15:3000,16:3813,17:2969,18:3641,19:3069,
    20:3080,21:2162,22:1562,23:553
}

today_d = {
    1:(7,724.0), 2:(2,284.0), 3:(2,355.0), 5:(3,480.2), 6:(8,1103.7),
    7:(1,99.0), 8:(2,150.7), 9:(2,175.0), 10:(6,1026.0), 11:(12,1930.9),
    12:(20,4902.9), 13:(23,4758.6), 14:(8,1707.1), 15:(5,799.7),
    16:(7,928.5), 17:(13,1780.4), 18:(11,2095.9), 19:(9,980.2),
    20:(7,1177.0), 21:(7,1798.0), 22:(3,460.0),
}

prev_e = {
    0:(5,1118.0), 1:(1,94.5), 2:(4,507.0), 3:(7,1353.2), 4:(8,1543.0),
    5:(4,716.7), 6:(4,429.0), 7:(6,637.0), 8:(3,824.5), 9:(3,465.7),
    10:(7,1635.2), 11:(10,2051.1), 12:(28,6054.5), 13:(16,2432.8),
    14:(9,1605.7), 15:(10,2682.5), 16:(11,2798.1), 17:(8,1777.0),
    18:(14,2425.9), 19:(16,2322.6), 20:(7,783.7), 21:(3,645.0),
    22:(8,1410.8), 23:(1,165.0),
}

# Anomaly hours flagged
ANOMALY_HOURS = {7, 8, 9, 10, 11, 14, 15, 16, 20, 22}

top3_map = {
    1:  "ข้าวกะเพราเปัดย่าง ×3<br>ข้าวกะเพราไก่คาราเกะ ×1<br>มาม่าผัดกะเพราไก่ ×1",
    2:  "หมูยอทอด ×2<br>ข้าวสวย ×2<br>แกงจืดเต้าหู้หมูสับ ×1",
    3:  "ไข่ดาว ×1<br>โค้ก ×1<br>ข้าวไก่กระเทียม ×1",
    5:  "ไข่ดาว ×2<br>มาม่าผัดกะเพราไก่ ×1<br>โค้ก ×1",
    6:  "ข้าวผัดกะเพราหมูสับ ×4<br>ข้าวผัดโบราณ ×3<br>ไข่ดาว ×1",
    7:  "ข้าวผัดโบราณ ×1",
    8:  "ไข่ดาว ×1<br>ข้าวผัดกะเพราหมูสับ ×1<br>Minere Mineral Water 6… ×1",
    9:  "Minere Mineral Water 6… ×2<br>ข้าวผัดโบราณ ×1",
    10: "มาม่าผัดกะเพราไก่ ×2<br>ไข่ดาว ×2<br>โค้ก ×2",
    11: "ไข่ดาว ×7<br>โค้ก ×5<br>ข้าวกะเพราเปัดย่าง ×3",
    12: "ไข่ดาว ×22<br>โค้ก ×12<br>ข้าวกะเพราเทพหมู ×6",
    13: "ไข่ดาว ×18<br>โค้ก ×8<br>ข้าวกะเพราเปัดย่าง ×7",
    14: "ไข่ดาว ×6<br>แกงจืดเต้าหู้หมูสับ ×2<br>ข้าวสวย ×2",
    15: "ไข่ดาว ×2<br>โค้ก ×2<br>ชามะนาว ×2",
    16: "ข้าวผัดกะเพราหมูสับ ×3<br>ไข่เจียว ×2<br>มาม่าผัดกะเพราไก่ ×1",
    17: "ไข่ดาว ×5<br>ข้าวผัดกะเพราไก่ชิ้น ×4<br>โค้ก ×3",
    18: "ไข่ดาว ×5<br>โค้ก ×5<br>ข้าวกะเพราเปัดย่าง ×4",
    19: "ไข่ดาว ×2<br>โค้ก ×2<br>ข้าวไข่ยู่ยี่ ×2",
    20: "ไข่ดาว ×5<br>โค้ก ×4<br>มาม่าผัดกะเพราไก่ ×2",
    21: "ไข่ดาว ×8<br>Minere Mineral Water 6… ×3<br>โค้ก ×2",
    22: "ข้าวกะเพราไก่คาราเกะ ×1<br>ข้าวผัดกะเพราหมูสับ ×1<br>ข้าวไก่กระเทียม ×1",
}

hourly_rows = []
row_idx = 0
for h in sorted(today_d.keys()):
    is_anom = h in ANOMALY_HOURS
    cur_bills, cur_rev = today_d[h]
    prev_bills, prev_rev = prev_e.get(h, (0, 0.0))
    bench_rev = HOURLY_REV_BENCH.get(h, 0)

    if prev_rev > 0:
        chg = round((cur_rev - prev_rev) / prev_rev * 100, 1)
        chg_str = f"+{chg:.1f}%" if chg >= 0 else f"{chg:.1f}%"
        chg_col = "#27AE60" if chg >= 0 else "#E74C3C"
        chg_w   = "700" if abs(chg) >= 10 else "400"
    else:
        chg_str, chg_col, chg_w = "—", "#888", "400"

    if is_anom:
        row_bg = "#FFEBEE"
        hour_color = "#C62828"
        cur_color  = "#C62828"
    else:
        row_bg = "#FFFFFF" if row_idx % 2 == 0 else "#FAFAFA"
        hour_color = "#2C3E50"
        cur_color  = "#2C3E50"
        row_idx += 1

    hourly_rows.append({
        "hour":          f"{h:02d}:00",
        "hour_flag":     " 🚨" if is_anom else "",
        "hour_color":    hour_color,
        "prev_rev":      f"฿{fmt(prev_rev)}",
        "prev_color":    "#2C3E50",
        "cur_rev":       f"฿{fmt(cur_rev)}",
        "cur_color":     cur_color,
        "change_pct":    chg_str,
        "change_color":  chg_col,
        "change_weight": chg_w,
        "bench":         fmt(bench_rev),
        "top3":          top3_map.get(h, "—"),
        "row_bg":        row_bg,
    })

# ── PROMOTION WEEKLY TREND (from Q G2 file) ───────────────────────────────────
import ast, re as _re

# Read raw G2 items from saved file
g2_file = "/root/.claude/projects/-home-user-report/748e258c-8dc3-5b0b-8ba4-0db95b1b28aa/tool-results/mcp-Chaw-Netsuite--Read-only--ns_runCustomSuiteQL-1781655432994.txt"
with open(g2_file) as f:
    raw = f.read()
data_g2 = json.loads(raw)
g2_items = data_g2["items"]

# Build per-day promo totals: filter rate -9.81 (staff10) and -16.20 (set50)
from datetime import datetime, timedelta
def parse_date(s):
    return datetime.strptime(s, "%d/%m/%Y").date()

promo_by_day = {}  # date -> {"staff10": bills, "set50": bills}
for item in g2_items:
    rate = float(item["discount_rate"])
    bills_v = int(item["bills"])
    d = parse_date(item["trandate"])
    if d not in promo_by_day:
        promo_by_day[d] = {"staff10": 0, "set50": 0}
    if abs(rate - (-9.81)) < 0.001:
        promo_by_day[d]["staff10"] += bills_v
    elif abs(rate - (-16.20)) < 0.001:
        promo_by_day[d]["set50"] += bills_v

# Aggregate by 5 weeks
from datetime import date as ddate
REPORT_DATE = ddate(2026, 6, 16)

def week_range(w):
    end = REPORT_DATE - timedelta(days=(w-1)*7)
    start = end - timedelta(days=6)
    return start, end

staff10_by_week = []
set50_by_week   = []
for w in range(5, 0, -1):  # oldest first: w=5,4,3,2,1
    start, end = week_range(w)
    s10, s50 = 0, 0
    cur = start
    while cur <= end:
        if cur in promo_by_day:
            s10 += promo_by_day[cur]["staff10"]
            s50 += promo_by_day[cur]["set50"]
        cur += timedelta(days=1)
    staff10_by_week.append(s10)
    set50_by_week.append(s50)

def make_promo_cells(vals, is_cur_f):
    cells = []
    for i, (val, is_cur) in enumerate(zip(vals, is_cur_f)):
        if i == 0 or vals[i-1] == 0:
            pct, col = "", "#888"
        else:
            p = round((val - vals[i-1]) / vals[i-1] * 100, 1)
            pct = f"▲+{p:.1f}%" if p >= 0 else f"▼{p:.1f}%"
            col = "#27AE60" if p >= 0 else "#E74C3C"
        w = "700" if is_cur else "400"
        bg = "#EEECFF" if is_cur else "#FFFFFF"
        cells.append({"val": str(val), "pct": pct, "color": col, "weight": w, "bg": bg})
    return cells

staff10_cells = make_promo_cells(staff10_by_week, is_cur_flags)
set50_cells   = make_promo_cells(set50_by_week,   is_cur_flags)

# ── RICE TOP10 LINES (for group message, not in data.json but computed here) ──
rice_top10_lines = "\n".join(
    f"{i+1}. {iid} {name} — {qty} ({badge(((qty - qc_avg.get(iid,qty)) / qc_avg.get(iid,qty) * 100) if qc_avg.get(iid) else 'NEW')[2]})"
    for i, (iid, name, qty) in enumerate(rice_items_sorted)
)
print("=== rice_top10_lines ===")
print(rice_top10_lines)
print("=== staff10_by_week:", staff10_by_week)
print("=== set50_by_week:  ", set50_by_week)
print("=== mtd_line_px:", mtd_line_px)

# ── ASSEMBLE data.json ────────────────────────────────────────────────────────
data = {
    "scalars": scalars,
    "repeats": {
        "chart_days":    chart_days,
        "chart_labels":  chart_labels,
        "week_headers":  week_headers,
        "walk_cells":    walk_cells,
        "staff_cells":   staff_cells,
        "total_cells":   total_cells,
        "heatmap_rows":  heatmap_rows,
        "top10_all":     top10_all,
        "top10_rice":    top10_rice,
        "hourly_rows":   hourly_rows,
        "staff10_cells": staff10_cells,
        "set50_cells":   set50_cells,
    },
    "sections": {
        "alert_banner": anomaly_count > 0,
        "promo":        (staff10_bills + set50_bills) > 0,
    },
}

with open("/home/user/report/Khiang/data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ data.json written successfully")
print(f"   Scalars: {len(scalars)}")
print(f"   chart_days: {len(chart_days)}, chart_labels: {len(chart_labels)}")
print(f"   heatmap_rows: {len(heatmap_rows)}, hourly_rows: {len(hourly_rows)}")
print(f"   top10_all: {len(top10_all)}, top10_rice: {len(top10_rice)}")
print(f"   staff10_cells: {len(staff10_cells)}, set50_cells: {len(set50_cells)}")
