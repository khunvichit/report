#!/usr/bin/env python3
"""Build data.json for khiang-template.html from pre-computed values."""
import json, math

def fmt(n, decimals=0):
    """Format number with commas."""
    if decimals == 0:
        return f"{round(n):,}"
    return f"{n:,.{decimals}f}"

def lerp_hex(a, b, t):
    """Linear interpolate between two hex colours."""
    ar,ag,ab = int(a[1:3],16),int(a[3:5],16),int(a[5:7],16)
    br,bg,bb = int(b[1:3],16),int(b[3:5],16),int(b[5:7],16)
    r = round(ar + t*(br-ar))
    g = round(ag + t*(bg-ag))
    bv = round(ab + t*(bb-ab))
    return f"#{r:02X}{g:02X}{bv:02X}"

def badge_colors(pct, is_new=False):
    if is_new:
        return "#D1ECF1","#0C5460"
    if pct >= 15:
        return "#D4EDDA","#155724"
    if pct <= -10:
        return "#F8D7DA","#721C24"
    return "#FEF3CD","#856404"

def signed(v, decimals=1):
    s = f"{v:.{decimals}f}"
    return ("+"+s) if v >= 0 else s

# ── DATES ──
REPORT_DATE_DISPLAY = "27 June 2026"
REPORT_DATE_SHORT   = "27 มิ.ย."
PREV_DATE_SHORT     = "26 มิ.ย."
REPORT_DAY_EN       = "Saturday"
REPORT_YEAR         = "2026"
GENERATED_DATE      = "28 June 2026"
MTD_MONTH           = "June 2026"
D30_START           = "29 พ.ค."
MTD_DAYS            = 27

# ── QUERY A — Segment Revenue & Bills ──
walk_in_bills   = 126
walk_in_revenue = 26969.0
staff_bills     = 70
staff_revenue   = 10896.6
credit_notes    = 0.0

net_sales    = walk_in_revenue + staff_revenue - credit_notes   # 37865.6
total_bills  = walk_in_bills + staff_bills                       # 196
avg_ticket   = round(net_sales / total_bills)                    # 193
signed_pct   = round((net_sales - 40000) / 40000 * 100, 1)      # -5.3
walk_in_pct  = round(walk_in_bills / total_bills * 100, 1)       # 64.3
staff_pct    = round(staff_bills  / total_bills * 100, 1)        # 35.7
target_icon  = "⚠️"  # <40000

# ── QUERY F — 5-day avg (for benchmarks) ──
avg_5d_net   = 33490   # round(167451.1/5)
avg_bills_5d = 169     # round(844/5)
avg_ticket_bench = 198 # round(33490/169)
bills_arrow  = "↑"     # 196 >= 169
ticket_arrow = "↓"     # 193 < 198

# ── QUERY I — MTD ──
net_mtd    = 951777.8
mtd_days_q = 27
avg_mtd    = round(net_mtd / mtd_days_q)   # 35252
mtd_signed_pct = round((avg_mtd - 40000) / 40000 * 100, 1)  # -11.9

# ── 30d from Query H ──
# May days (29,30,31) + all June days from Query I
may_net = 47362.5 + 35593.8 + 39970.9   # 122927.2
net_30d = may_net + net_mtd              # 1074705.0
days_30d = 30
avg_30d  = round(net_30d / days_30d)    # 35824

# Total 30d bills (May 29-31 + June)
may_bills_30d = 226 + 183 + 216         # 625
jun_bills_30d = (214+185+203+178+190+207+186+168+145+185+161+160+
                 177+172+193+158+163+225+218+164+171+163+158+184+149+190+196)
total_bills_30d = may_bills_30d + jun_bills_30d  # 5488
avg_bills_30d = round(total_bills_30d / days_30d)  # 183

# ── QUERY G — Promos ──
staff10_bills = 30
set50_bills   = 46

# ── ANOMALY — using revenue bench pro-rata ──
REV_BENCH = {
    0:1149,1:763,2:373,3:356,4:240,5:166,6:538,7:1636,8:1910,9:3223,
    10:3827,11:4673,12:5768,13:3631,14:4196,15:3000,16:3813,17:2969,
    18:3641,19:3069,20:3080,21:2162,22:1562,23:553
}
DAILY_REV_BENCH = sum(REV_BENCH.values())  # 56298
DAILY_BILL_BENCH = 298
AVG_TICKET_BENCH_REF = DAILY_REV_BENCH / DAILY_BILL_BENCH  # 188.9

def bill_bench(h):
    return REV_BENCH.get(h, 0) / AVG_TICKET_BENCH_REF

# Query D (June 27) hourly
qD = {
    0:(6,769.4),1:(9,1126.4),2:(2,300.0),3:(2,356.0),4:(2,320.0),
    5:(2,463.0),6:(3,347.2),7:(10,1728.3),8:(4,1260.9),9:(7,1036.4),
    10:(12,2258.9),11:(14,2460.4),12:(24,5367.4),13:(12,2652.7),
    14:(6,1115.5),15:(10,2209.5),16:(15,3049.6),17:(10,2265.0),
    18:(7,1141.2),19:(18,3162.6),20:(10,1766.0),21:(9,2388.5),
    22:(2,320.7)
}
# Query E (June 26) hourly
qE = {
    0:(3,330.5),2:(4,560.0),3:(2,218.0),5:(1,123.0),6:(1,40.0),
    7:(5,2045.0),8:(4,505.7),9:(7,1136.7),10:(7,1433.7),11:(25,4701.5),
    12:(16,2661.6),13:(14,2196.0),14:(9,2448.7),15:(9,1967.4),
    16:(13,3055.1),17:(6,1292.7),18:(13,2528.9),19:(20,3518.3),
    20:(11,1751.2),21:(12,2427.7),22:(6,1559.5),23:(2,190.0)
}

anomaly_hours = set()
for h, (bills, rev) in qD.items():
    if bills < bill_bench(h) * 0.50:
        anomaly_hours.add(h)
anomaly_count = len(anomaly_hours)  # should be 5: 8,9,14,18,22

# ── Top-3 per hour from Query E2 ──
top3_by_hour = {
    0:  "ไข่ดาว ×4<br>ข้าวผัดกะเพราหมูสับ ×4<br>มาม่าผัดกะเพราไก่ ×1",
    1:  "มาม่าผัดกะเพราไก่ ×3<br>กุยช่ายกรอบ ×3<br>ข้าวกะเพราเป็ดย่าง ×3",
    2:  "ไข่ดาว ×1<br>ข้าวผัดกะเพราหมูสับ ×1<br>ข้าวผัดกะเพราไก่ชิ้น ×1",
    3:  "ไข่ดาว ×2<br>ข้าวผัดกะเพราหมูสับ ×2<br>ข้าวหมูผัดน้ำมันหอย ×1",
    4:  "ข้าวผัดโบราณ ×1<br>ข้าวไข่ยู่ยี่ ×1<br>ข้าวกะเพราเป็ดย่าง ×1",
    5:  "โค้ก ×2<br>ข้าวผัดโบราณ ×1<br>แกงจืดเต้าหู้หมูสับ ×1",
    6:  "แกงจืดเต้าหู้หมูสับ ×1<br>หมูยอทอด ×1<br>ไข่ดาว ×1",
    7:  "ไข่ดาว ×5<br>ข้าวผัดกะเพราหมูสับ ×5<br>โค้ก ×2",
    8:  "ไข่ดาว ×8<br>โค้ก ×6<br>ข้าวผัดกะเพราหมูสับ ×3",
    9:  "Minere Mineral Water 6…×3<br>ข้าวผัดโบราณ ×2<br>ข้าวกะเพราเทพหมู ×2",
    10: "ไข่ดาว ×7<br>ข้าวผัดกะเพราหมูสับ ×6<br>โค้ก ×5",
    11: "ไข่ดาว ×4<br>ข้าวผัดโบราณ ×3<br>ข้าวสวย ×3",
    12: "ไข่ดาว ×20<br>โค้ก ×11<br>ข้าวผัดกะเพราหมูสับ ×10",
    13: "ไข่ดาว ×10<br>โค้ก ×8<br>ข้าวผัดกะเพราหมูสับ ×5",
    14: "โค้ก ×4<br>ไข่ดาว ×2<br>มาม่าผัดกะเพราไก่ ×1",
    15: "ไข่ดาว ×4<br>โค้ก ×4<br>ข้าวกะเพราเทพหมู ×3",
    16: "ไข่ดาว ×10<br>โค้ก ×9<br>มาม่าผัดกะเพราไก่ ×3",
    17: "ไข่ดาว ×4<br>โค้ก ×4<br>ข้าวผัดกะเพราหมูสับ ×4",
    18: "ไข่ดาว ×5<br>โค้ก ×5<br>มาม่าผัดกะเพราไก่ ×2",
    19: "ไข่ดาว ×7<br>ข้าวผัดกะเพราหมูสับ ×5<br>Minere Mineral Water 6…×4",
    20: "ไข่ดาว ×6<br>โค้ก ×6<br>Minere Mineral Water 6…×3",
    21: "ไข่ดาว ×7<br>โค้ก ×7<br>Minere Mineral Water 6…×4",
    22: "ไข่ดาว ×2<br>โค้ก ×1<br>ข้าวผัดกะเพราไก่ชิ้น ×1",
}

# ── HOURLY ROWS ──
hourly_rows = []
for idx, h in enumerate(sorted(qD.keys())):
    bills_d, rev_d = qD[h]
    bench_rev = REV_BENCH.get(h, 0)
    is_anom = h in anomaly_hours

    if h in qE:
        bills_e, rev_e = qE[h]
        prev_rev_str = fmt(rev_e)
        if rev_e > 0:
            chg = (rev_d - rev_e) / rev_e * 100
            chg_str = signed(round(chg, 1)) + "%"
            chg_color = "#27AE60" if chg >= 0 else "#E74C3C"
            chg_weight = 700 if abs(chg) >= 10 else 400
        else:
            chg_str = "—"; chg_color = "#888"; chg_weight = 400
    else:
        prev_rev_str = "—"; chg_str = "—"; chg_color = "#888"; chg_weight = 400

    if is_anom:
        row_bg = "#FFEBEE"; hour_color = "#C62828"; cur_color = "#C62828"
        hour_flag = " 🚨"
    else:
        row_bg = "#FFFFFF" if idx % 2 == 0 else "#FAFAFA"
        hour_color = "#2C3E50"; cur_color = "#2C3E50"; hour_flag = ""

    hourly_rows.append({
        "row_bg":       row_bg,
        "hour":         f"{h:02d}:00",
        "hour_color":   hour_color,
        "hour_flag":    hour_flag,
        "prev_color":   "#888",
        "prev_rev":     prev_rev_str,
        "cur_color":    cur_color,
        "cur_rev":      fmt(rev_d),
        "change_color": chg_color,
        "change_weight":str(chg_weight),
        "change_pct":   chg_str,
        "bench":        fmt(bench_rev),
        "top3":         top3_by_hour.get(h, "—"),
    })

# ── TOP 10 ALL MENU ──
# Sorted by qty desc, then itemid asc for ties
rice_allow = {"K008","K013","K016","K017","K037","K038","K039",
              "K040","K041","K042","K043","K044","K045","K046","K047"}
qB_items = [
    ("K023","ไข่ดาว",113),("K028","โค้ก",80),("K037","ข้าวผัดกะเพราหมูสับ",59),
    ("K021","กุยช่ายกรอบ",22),("K014","มาม่าผัดกะเพราไก่",21),("K045","ข้าวกะเพราเป็ดย่าง",21),
    ("K024","ไข่เจียว",17),("K041","ข้าวไข่ยู่ยี่",17),("K015","มาม่าต้มยำทรงเครื่อง",13),
    ("K057","กุยช่ายแซ่บ",13),("K018","แกงจืดเต้าหู้หมูสับ",13),("K020","หมูยอทอด",7),
    ("K040","ข้าวหมูกระเทียม",7),("K043","ข้าวกะเพราเทพหมู",16),("K042","ข้าวกะเพราดิบเถื่อน (เนื้อโคขุน)",9),
    ("K047","ข้าวหมูผัดน้ำมันหอย",9),("K025","ข้าวสวย",8),("K038","ข้าวผัดกะเพราไก่ชิ้น",14),
    ("K039","ข้าวไก่กระเทียม",4),("K046","ข้าวไก่ผัดน้ำมันหอย",2),("K013","ข้าวกะเพราไก่คาราเกะ",5),
    ("K019","ต้มยำกุ้ง",5),("K008","ข้าวผัดโบราณ",15),("K056","Minere Mineral Water 600 Ml",30),
    ("K031","เก๊กฮวย",2),("K035","สละลอยแก้ว",1),("K029","โค้ก ซีโร่",1),
]
all_sorted = sorted(qB_items, key=lambda x: (-x[2], x[0]))
top10_all_items = all_sorted[:10]

avg5d_map = {
    "K023":102,"K028":68,"K037":52,"K021":16,"K014":12,"K045":15,
    "K024":11,"K041":10,"K015":8,"K057":9,"K043":19,"K008":11,
    "K038":18,"K042":11,"K047":7,"K040":10,"K013":8,"K046":4,
    "K039":8,"K018":7,"K020":7,
}

top10_all = []
for i,(iid,name,qty) in enumerate(top10_all_items):
    is_rice = iid in rice_allow
    display_name = ("⭐ " if is_rice else "") + name
    a5 = avg5d_map.get(iid)
    if a5 is None:
        pct = 100.0; bg,fg = "#D1ECF1","#0C5460"; lbl = "New"
    else:
        pct = round((qty - a5) / a5 * 100, 1)
        bg,fg = badge_colors(pct)
        lbl = signed(pct, 1) + "%"
    row_bg = "#FFFFFF" if i % 2 == 0 else "#FAFAFA"
    top10_all.append({
        "rank":str(i+1),"row_bg":row_bg,"itemid":iid,"name":display_name,
        "qty":str(qty),"avg5d":str(a5) if a5 else "—",
        "badge_bg":bg,"badge_fg":fg,"badge_label":lbl,
    })

# ── TOP 10 RICE MENU ──
FC_PCT = {
    "K037":"26.2%","K038":"24.3%","K039":"23.3%","K040":"29.7%","K041":"26.1%",
    "K042":"23.3%","K043":"25.3%","K045":"29.9%","K046":"22.6%","K047":"29.1%",
    "K008":"27.2%","K013":"26.0%",
}
rice_raw = [(iid,name,qty) for iid,name,qty in qB_items if iid in rice_allow]
rice_sorted = sorted(rice_raw, key=lambda x: (-x[2], x[0]))
top10_rice_items = rice_sorted[:10]

top10_rice = []
for i,(iid,name,qty) in enumerate(top10_rice_items):
    a5 = avg5d_map.get(iid)
    if a5 is None:
        pct = 100.0; bg,fg = "#D1ECF1","#0C5460"; lbl = "New"
    else:
        pct = round((qty - a5) / a5 * 100, 1)
        bg,fg = badge_colors(pct)
        lbl = signed(pct, 1) + "%"
    row_bg = "#FFFFFF" if i % 2 == 0 else "#FAFAFA"
    top10_rice.append({
        "rank":str(i+1),"row_bg":row_bg,"itemid":iid,"name":name,
        "qty":str(qty),"avg5d":str(a5) if a5 else "—",
        "fc_pct":FC_PCT.get(iid,"—"),
        "badge_bg":bg,"badge_fg":fg,"badge_label":lbl,
    })

# ── 30-DAY CHART ──
# 30 days: May 29–Jun 27
chart_data_raw = [
    ("2026-05-29","29",47362.5),("2026-05-30","30",35593.8),("2026-05-31","31",39970.9),
    ("2026-06-01","01",40604.7),("2026-06-02","02",37790.9),("2026-06-03","03",40630.8),
    ("2026-06-04","04",31799.6),("2026-06-05","05",37254.8),("2026-06-06","06",42335.0),
    ("2026-06-07","07",37579.6),("2026-06-08","08",29538.2),("2026-06-09","09",29783.3),
    ("2026-06-10","10",41166.2),("2026-06-11","11",29718.7),("2026-06-12","12",31185.1),
    ("2026-06-13","13",35195.7),("2026-06-14","14",31488.6),("2026-06-15","15",36478.5),
    ("2026-06-16","16",27716.8),("2026-06-17","17",34525.6),("2026-06-18","18",43790.5),
    ("2026-06-19","19",43361.7),("2026-06-20","20",33632.8),("2026-06-21","21",30884.0),
    ("2026-06-22","22",30653.3),("2026-06-23","23",33531.1),("2026-06-24","24",39150.9),
    ("2026-06-25","25",27424.6),("2026-06-26","26",36691.2),("2026-06-27","27",37865.6),
]
chart_max = max(x[2] for x in chart_data_raw)   # 47362.5
bar_px_max = 90
mtd_line_px = round(min(avg_mtd, chart_max) / chart_max * bar_px_max)  # 67

chart_days = []
chart_labels = []
for dt, lbl, ns in chart_data_raw:
    bp = max(2, round(ns / chart_max * bar_px_max))
    color = "#27AE60" if ns >= 40000 else "#E74C3C"
    is_rd = (dt == "2026-06-27")
    # Thai month abbreviations for bar_title
    mon_th = {"01":"ม.ค.","02":"ก.พ.","03":"มี.ค.","04":"เม.ย.","05":"พ.ค.",
              "06":"มิ.ย.","07":"ก.ค.","08":"ส.ค.","09":"ก.ย.","10":"ต.ค.",
              "11":"พ.ย.","12":"ธ.ค."}
    mm = dt[5:7]
    dd = dt[8:10].lstrip("0")
    title = f"{dd} {mon_th[mm]} · ฿{fmt(ns)}"
    chart_days.append({"bar_px":str(bp),"bar_color":color,"bar_title":title})
    chart_labels.append({
        "day_label":lbl,
        "label_color":"#5551FE" if is_rd else "#AAA",
        "label_weight":"700" if is_rd else "400",
    })

# ── 5-WEEK CUSTOMER TREND (week_headers, walk_cells, staff_cells, total_cells) ──
# Weeks oldest→newest. Week covers 7 days ending REPORT_DATE - (w-1)*7
# w5=oldest: ends Jun 27-28=May 30, covers May 24-30
# w4: ends Jun 6, covers May 31-Jun 6
# w3: ends Jun 13, covers Jun 7-13
# w2: ends Jun 20, covers Jun 14-20
# w1=current: ends Jun 27, covers Jun 21-27
weeks = [
    # (label, walk, staff, total, is_current)
    ("24–30 พ.ค.",    863, 497, 1360, False),
    ("31 พ.ค.–6 มิ.ย.", 881, 512, 1393, False),
    ("7–13 มิ.ย.",    773, 409, 1182, False),
    ("14–20 มิ.ย.",   811, 482, 1293, False),
    ("21–27 มิ.ย.",   800, 411, 1211, True),
]

week_headers = []
walk_cells   = []
staff_cells  = []
total_cells  = []

def wow_cell(cur, prev, is_current, is_total=False):
    weight_base = 700 if is_current else 400
    bg = "#EEECFF" if is_current else "#FFFFFF"
    if prev is None or prev == 0:
        pct_str = ""; color = "#888"
    else:
        p = round((cur - prev) / prev * 100, 1)
        pct_str = ("▲" if p >= 0 else "▼") + signed(p,1) + "%"
        color = "#27AE60" if p >= 0 else "#E74C3C"
    return {"val":fmt(cur),"pct":pct_str,"color":color,"weight":str(weight_base),"bg":bg}

for i,(label, walk, staff, total, is_cur) in enumerate(weeks):
    head_color = "#5551FE" if is_cur else "#888"
    head_bg    = "#EEECFF" if is_cur else "#F8F9FA"
    week_headers.append({"label":label,"head_color":head_color,"head_bg":head_bg})

    prev_walk  = weeks[i-1][1] if i > 0 else None
    prev_staff = weeks[i-1][2] if i > 0 else None
    prev_total = weeks[i-1][3] if i > 0 else None

    walk_cells.append(wow_cell(walk, prev_walk, is_cur))
    staff_cells.append(wow_cell(staff, prev_staff, is_cur))
    total_cells.append(wow_cell(total, prev_total, is_cur, is_total=True))

# ── 7-DAY HEATMAP (Jun 21–27) ──
heatmap_raw = [
    # date, bills, net_sales
    ("2026-06-21","อา 21/6", 171, 30884.0),
    ("2026-06-22","จ 22/6",  163, 30653.3),
    ("2026-06-23","อ 23/6",  158, 33531.1),
    ("2026-06-24","พ 24/6",  184, 39150.9),
    ("2026-06-25","พฤ 25/6", 149, 27424.6),
    ("2026-06-26","ศ 26/6",  190, 36691.2),
    ("2026-06-27","ส 27/6",  196, 37865.6),  # REPORT_DATE
]
# Prior-week WoW baselines (Jun 14–20)
wow_baseline = {
    "2026-06-21": 31488.6,   # Jun 14
    "2026-06-22": 36478.5,   # Jun 15
    "2026-06-23": 27716.8,   # Jun 16
    "2026-06-24": 34525.6,   # Jun 17
    "2026-06-25": 43790.5,   # Jun 18
    "2026-06-26": 43361.7,   # Jun 19
    "2026-06-27": 33632.8,   # Jun 20
}

avg_tickets_7d = [round(r[3]/r[2]) for r in heatmap_raw]  # [181,188,212,213,184,193,193]

ns_7 = [r[3] for r in heatmap_raw]
bi_7 = [r[2] for r in heatmap_raw]
at_7 = avg_tickets_7d

def shade(vals):
    lo, hi = min(vals), max(vals)
    out = []
    for v in vals:
        t = 0.5 if hi == lo else (v - lo) / (hi - lo)
        bg = lerp_hex("#FBF3EA","#C9C7FF", t)
        out.append((bg, t))
    return out

ns_shades = shade(ns_7)
bi_shades = shade(bi_7)
at_shades = shade(at_7)

ns_max_idx = ns_7.index(max(ns_7))
bi_max_idx = bi_7.index(max(bi_7))
at_max_idx = at_7.index(max(at_7))

heatmap_rows = []
for i,(dt, label_th, bills, ns) in enumerate(heatmap_raw):
    at = avg_tickets_7d[i]
    is_rd = (dt == "2026-06-27")
    day_weight = "700" if is_rd else "400"

    rev_bg, _ = ns_shades[i]; rev_weight = "700" if i == ns_max_idx else "400"
    bi_bg,  _ = bi_shades[i]; bi_weight  = "700" if i == bi_max_idx else "400"
    at_bg,  _ = at_shades[i]; at_weight  = "700" if i == at_max_idx else "400"

    prev = wow_baseline.get(dt)
    if prev is None or prev == 0:
        wow_pct = "—"; wow_color = "#888"; wow_weight = "400"
    else:
        wp = round((ns - prev) / prev * 100, 1)
        wow_pct = ("+" if wp >= 0 else "") + f"{wp:.1f}%"
        wow_color = "#27AE60" if wp >= 0 else "#E74C3C"
        wow_weight = "700" if abs(wp) >= 10 else "400"

    heatmap_rows.append({
        "day_label_th": label_th, "day_weight": day_weight,
        "rev":    fmt(ns), "rev_weight":  rev_weight, "rev_fg":"#2C3E50", "rev_bg":rev_bg,
        "bills":  str(bills), "bills_weight":bi_weight, "bills_fg":"#2C3E50","bills_bg":bi_bg,
        "ticket": fmt(at),  "ticket_weight":at_weight,"ticket_fg":"#2C3E50","ticket_bg":at_bg,
        "wow_pct":wow_pct, "wow_color":wow_color, "wow_weight":wow_weight,
    })

# ── PROMO WEEKLY TREND ──
# staff10 per week (oldest→newest)
staff10_weeks = [225, 221, 165, 191, 185]
set50_weeks   = [316, 249, 302, 338, 324]

staff10_cells = []
set50_cells   = []
for i in range(5):
    is_cur = (i == 4)
    bg     = "#EEECFF" if is_cur else "#FFFFFF"
    wt     = "700" if is_cur else "400"

    prev_s10 = staff10_weeks[i-1] if i > 0 else None
    prev_s50 = set50_weeks[i-1]   if i > 0 else None

    if prev_s10 is None or prev_s10 == 0:
        s10_pct = ""; s10_color = "#888"
    else:
        p = round((staff10_weeks[i]-prev_s10)/prev_s10*100,1)
        s10_pct = ("▲" if p>=0 else "▼") + signed(p,1) + "%"
        s10_color = "#27AE60" if p>=0 else "#E74C3C"

    if prev_s50 is None or prev_s50 == 0:
        s50_pct = ""; s50_color = "#888"
    else:
        p = round((set50_weeks[i]-prev_s50)/prev_s50*100,1)
        s50_pct = ("▲" if p>=0 else "▼") + signed(p,1) + "%"
        s50_color = "#27AE60" if p>=0 else "#E74C3C"

    staff10_cells.append({"val":str(staff10_weeks[i]),"pct":s10_pct,"color":s10_color,"weight":wt,"bg":bg})
    set50_cells.append(  {"val":str(set50_weeks[i]),  "pct":s50_pct,"color":s50_color,"weight":wt,"bg":bg})

# ── ASSEMBLE data.json ──
data = {
    "scalars": {
        "report_date_display": REPORT_DATE_DISPLAY,
        "report_day_en":       REPORT_DAY_EN,
        "report_date_short":   REPORT_DATE_SHORT,
        "prev_date_short":     PREV_DATE_SHORT,
        "report_year":         REPORT_YEAR,
        "generated_date":      GENERATED_DATE,
        "net_sales":           fmt(net_sales),
        "signed_pct":          signed(signed_pct,1),
        "target_icon":         target_icon,
        "total_bills":         str(total_bills),
        "avg_bills":           str(avg_bills_5d),
        "bills_arrow":         bills_arrow,
        "walk_in_bills":       str(walk_in_bills),
        "walk_in_revenue":     fmt(walk_in_revenue),
        "walk_in_pct":         str(walk_in_pct),
        "staff_bills":         str(staff_bills),
        "staff_revenue":       fmt(staff_revenue),
        "staff_pct":           str(staff_pct),
        "avg_ticket":          fmt(avg_ticket),
        "avg_ticket_bench":    str(avg_ticket_bench),
        "ticket_arrow":        ticket_arrow,
        "avg_5d":              fmt(avg_5d_net),
        "net_30d":             fmt(net_30d),
        "avg_30d":             fmt(avg_30d),
        "d30_start":           D30_START,
        "net_mtd":             fmt(net_mtd),
        "avg_mtd":             fmt(avg_mtd),
        "mtd_days":            str(MTD_DAYS),
        "mtd_month":           MTD_MONTH,
        "mtd_signed_pct":      signed(mtd_signed_pct,1),
        "mtd_line_px":         str(mtd_line_px),
        "avg_bills_30d":       str(avg_bills_30d),
        "anomaly_count":       str(anomaly_count),
        "staff10_bills":       str(staff10_bills),
        "staff10_badge_bg":    "#D4EDDA",
        "staff10_badge_fg":    "#155724",
        "staff10_status":      "Active",
        "set50_bills":         str(set50_bills),
        "set50_badge_bg":      "#D4EDDA",
        "set50_badge_fg":      "#155724",
        "set50_status":        "Active",
        "chaw_values":         "Curious · Team · Act Fast · Empowered · Simple",
    },
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

out_path = "/home/user/report/Khiang/data.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"data.json written — {anomaly_count} anomalies, {len(hourly_rows)} hourly rows")
print(f"net_sales={fmt(net_sales)}  total_bills={total_bills}  anomaly_count={anomaly_count}")
print(f"avg_mtd={fmt(avg_mtd)}  avg_30d={fmt(avg_30d)}  mtd_line_px={mtd_line_px}")
print(f"sections: alert_banner={anomaly_count>0}  promo=True")
