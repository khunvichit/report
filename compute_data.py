#!/usr/bin/env python3
"""Compute data.json for Juiceland 2026-06-06 report."""
import json, math
from collections import defaultdict

REPORT_DATE = "2026-06-06"
WINDOW_START = "2026-05-08"
GENERATED_TS = "2026-06-07 07:15"

# ── Query A data ──────────────────────────────────────────────────────────────
qa_raw = [
    ("08/05/2026","33",75,25013),("08/05/2026","105",62,22859),("08/05/2026","109",49,13659),
    ("09/05/2026","33",90,27290),("09/05/2026","105",70,22575),("09/05/2026","109",45,9516),
    ("10/05/2026","33",101,36901),("10/05/2026","105",78,26350),("10/05/2026","109",46,10994),
    ("11/05/2026","33",102,33927.5),("11/05/2026","105",71,25400),("11/05/2026","109",40,9884),
    ("12/05/2026","33",82,31386),("12/05/2026","105",58,18990),("12/05/2026","109",46,11704),
    ("13/05/2026","33",102,34122),("13/05/2026","105",70,25085),("13/05/2026","109",56,13897),
    ("14/05/2026","33",109,40908),("14/05/2026","105",64,21800),("14/05/2026","109",36,7820),
    ("15/05/2026","33",98,35787),("15/05/2026","105",64,19010),("15/05/2026","109",37,10244),
    ("16/05/2026","33",85,30765.5),("16/05/2026","105",73,25470),("16/05/2026","109",47,9920),
    ("17/05/2026","33",100,34754),("17/05/2026","105",85,35410),("17/05/2026","109",55,13484),
    ("18/05/2026","33",88,25913),("18/05/2026","105",77,22700),("18/05/2026","109",43,12484),
    ("19/05/2026","33",99,33034.5),("19/05/2026","105",72,25820),("19/05/2026","109",43,7867),
    ("20/05/2026","33",91,31093),("20/05/2026","105",63,17307.5),("20/05/2026","109",44,10311),
    ("21/05/2026","33",103,36940.5),("21/05/2026","105",80,29297),("21/05/2026","109",46,9611),
    ("22/05/2026","33",115,40088),("22/05/2026","105",79,26689),("22/05/2026","109",45,10358),
    ("23/05/2026","33",109,38639.5),("23/05/2026","105",94,39492),("23/05/2026","109",49,12698),
    ("24/05/2026","33",114,45429.5),("24/05/2026","105",80,28328),("24/05/2026","109",49,12933),
    ("25/05/2026","33",100,38221),("25/05/2026","105",83,31983.5),("25/05/2026","109",40,10502),
    ("26/05/2026","33",94,36852.5),("26/05/2026","105",68,24575.5),("26/05/2026","109",31,7039),
    ("27/05/2026","33",96,33877),("27/05/2026","105",84,26502),("27/05/2026","109",56,16234),
    ("28/05/2026","33",85,33415),("28/05/2026","105",91,31121),("28/05/2026","109",44,12474),
    ("29/05/2026","33",108,42210.5),("29/05/2026","105",70,22568),("29/05/2026","109",58,13844),
    ("30/05/2026","33",104,34788),("30/05/2026","105",63,26883),("30/05/2026","109",60,14605),
    ("31/05/2026","33",88,28583),("31/05/2026","105",79,32544),("31/05/2026","109",54,14052),
    ("01/06/2026","33",101,32133),("01/06/2026","105",79,24075),("01/06/2026","109",56,13940),
    ("02/06/2026","33",94,36476),("02/06/2026","105",49,15959),("02/06/2026","109",41,9920),
    ("03/06/2026","33",104,40024),("03/06/2026","105",61,19497),("03/06/2026","109",49,10573),
    ("04/06/2026","33",100,35666.5),("04/06/2026","105",66,16604),("04/06/2026","109",60,13146),
    ("05/06/2026","33",92,35456),("05/06/2026","105",66,19500),("05/06/2026","109",58,13589),
    ("06/06/2026","33",83,32714),("06/06/2026","105",68,22902),("06/06/2026","109",53,13867),
]

LOC_MAP = {"33":"MW1","105":"SE3","109":"PKT","169":"MW1"}
BRANCH_ORDER = ["MW1","SE3","PKT"]
BRANCH_COLORS = {"MW1":"#5551FE","SE3":"#F27061","PKT":"#2E7D32"}

# Build per-date per-branch dict
by_date = defaultdict(lambda: {"MW1":{"net":0,"bills":0},"SE3":{"net":0,"bills":0},"PKT":{"net":0,"bills":0}})
for (dt, loc, bills, net) in qa_raw:
    b = LOC_MAP[loc]
    by_date[dt]["MW1" if b=="MW1" else b]["net"] += net
    by_date[dt]["MW1" if b=="MW1" else b]["bills"] += bills

# Ordered dates
dates_sorted = sorted(by_date.keys(), key=lambda d: (d[6:],d[3:5],d[:2]))

# Yesterday
yest = by_date["06/06/2026"]
mw1_net_yest = yest["MW1"]["net"]
se3_net_yest = yest["SE3"]["net"]
pkt_net_yest = yest["PKT"]["net"]
mw1_bills_yest = yest["MW1"]["bills"]
se3_bills_yest = yest["SE3"]["bills"]
pkt_bills_yest = yest["PKT"]["bills"]
comb_net_yest = mw1_net_yest + se3_net_yest + pkt_net_yest

# 30-day branch sums
mw1_30d = sum(by_date[d]["MW1"]["net"] for d in dates_sorted)
se3_30d = sum(by_date[d]["SE3"]["net"] for d in dates_sorted)
pkt_30d = sum(by_date[d]["PKT"]["net"] for d in dates_sorted)
comb_30d = mw1_30d + se3_30d + pkt_30d

mw1_avg = mw1_30d/30; se3_avg = se3_30d/30; pkt_avg = pkt_30d/30
comb_avg = comb_30d/30

mw1_daily = [by_date[d]["MW1"]["net"] for d in dates_sorted]
se3_daily = [by_date[d]["SE3"]["net"] for d in dates_sorted]
pkt_daily = [by_date[d]["PKT"]["net"] for d in dates_sorted]

mw1_min = min(mw1_daily); mw1_max = max(mw1_daily)
se3_min = min(se3_daily); se3_max = max(se3_daily)
pkt_min = min(pkt_daily); pkt_max = max(pkt_daily)

# vs 30d avg
def pct(actual, avg): return round((actual - avg) / avg * 100, 1)
mw1_vs = pct(mw1_net_yest, mw1_avg)
se3_vs = pct(se3_net_yest, se3_avg)
pkt_vs = pct(pkt_net_yest, pkt_avg)
comb_vs = pct(comb_net_yest, comb_avg)

signed_pct = comb_vs
subject_prefix = "🔥" if signed_pct >= 10 else ("✅" if signed_pct >= -10 else "⚠️")

# Chart max (single-branch day max in window)
chart_max = max(max(mw1_daily), max(se3_daily), max(pkt_daily))

def bar(v): return max(1, round(v / chart_max * 220))
def fmt(v): return f"{int(round(v)):,}"
def fmtf(v): return f"{round(v):,}"

# Thai weekdays
THAI_WD = {0:"วันจันทร์",1:"วันอังคาร",2:"วันพุธ",3:"วันพฤหัสบดี",4:"วันศุกร์",5:"วันเสาร์",6:"วันอาทิตย์"}
THAI_WD_ABBR = {0:"จ.",1:"อ.",2:"พ.",3:"พฤ.",4:"ศ.",5:"ส.",6:"อา."}
import datetime
def parse_dd(dt_str):
    d,m,y = dt_str.split("/")
    return datetime.date(int(y),int(m),int(d))

report_dt = datetime.date(2026,6,6)
report_day_th = THAI_WD[report_dt.weekday()]

def display_date(dt):
    return dt.strftime("%-d %B %Y")

# Chart days (30 entries)
chart_days = []
for i, dt_str in enumerate(dates_sorted):
    d = parse_dd(dt_str)
    chart_days.append({
        "date": dt_str,
        "day_num": d.day,
        "weekday_th_abbr": THAI_WD_ABBR[d.weekday()],
        "mw1_net": fmt(by_date[dt_str]["MW1"]["net"]),
        "se3_net": fmt(by_date[dt_str]["SE3"]["net"]),
        "pkt_net": fmt(by_date[dt_str]["PKT"]["net"]),
        "mw1_bar_px": bar(by_date[dt_str]["MW1"]["net"]),
        "se3_bar_px": bar(by_date[dt_str]["SE3"]["net"]),
        "pkt_bar_px": bar(by_date[dt_str]["PKT"]["net"]),
    })

# Last 7 days
last7_dates = dates_sorted[-7:]
def cell_style_yest(dt_str): return "background:#FFF3E0;font-weight:700;" if dt_str == "06/06/2026" else ""
def header_bg_yest(dt_str): return "background:#4744CD;" if dt_str == "06/06/2026" else ""

last7_headers = []
for dt_str in last7_dates:
    d = parse_dd(dt_str)
    last7_headers.append({
        "col_date": d.strftime("%-d/%m"),
        "col_weekday_th": THAI_WD_ABBR[d.weekday()],
        "header_bg": header_bg_yest(dt_str),
    })

def make_last7(branch):
    rows = []
    for dt_str in last7_dates:
        rows.append({"net": fmt(by_date[dt_str][branch]["net"]), "cell_style": cell_style_yest(dt_str)})
    return rows

def make_last7_comb():
    rows = []
    for dt_str in last7_dates:
        comb = sum(by_date[dt_str][b]["net"] for b in BRANCH_ORDER)
        rows.append({"net": fmt(comb), "cell_bg": "background:#FFF3E0;" if dt_str=="06/06/2026" else ""})
    return rows

mw1_7d_total = sum(by_date[d]["MW1"]["net"] for d in last7_dates)
se3_7d_total = sum(by_date[d]["SE3"]["net"] for d in last7_dates)
pkt_7d_total = sum(by_date[d]["PKT"]["net"] for d in last7_dates)
comb_7d_total = mw1_7d_total + se3_7d_total + pkt_7d_total
last7_avg = comb_7d_total / 7

# ── Query B — Top 20 per branch ───────────────────────────────────────────────
qb_raw = [
    ("33","EVIAN",40,4486,4),
    ("33","COCONUT READY TO DRINK",11,1747.68,2),
    ("33","WATERMELON 400G.",9,1261.71,3),
    ("33","PRIDE PARROT RED",8,1495.35,2),
    ("33","COCONUT JUICE BOTTLE",8,1383.18,3),
    ("33","S3 WATERMELON SMOOTHIE 22OZ",7,1210.29,3),
    ("33","PRIDE PARROT YELLOW",7,1308.42,3),
    ("33","CARROT JUICE BOTTLE",6,1037.38,2),
    ("33","WATERMELON JUICE BOTTLE",6,1037.39,1),
    ("33","MANGO 400G.",6,897.18,3),
    ("33","C1 GUAVA&GREEN APPLE&RED APPLE COLD PREESED 22OZ",5,981.3,2),
    ("33","T1 ICED THAI MILK TEA 16OZ",5,700.94,2),
    ("33","CI3 ICED AMERICANO 22OZ",5,841.1,3),
    ("33","S5 MANGO SMOOTHIE 22OZ",5,864.49,2),
    ("33","3 kinds of fruit400g Papaya/Pineapple/Guava",4,560.76,2),
    ("33","S3 WATERMELON SMOOTHIE 16OZ",3,448.59,2),
    ("33","C3 WATERMELON COLD PREESED 22OZ",3,588.79,1),
    ("33","PAPAYA 400G.",3,420.57,2),
    ("33","Mango juice (Bottle) 300 ml",3,518.7,2),
    ("33","C1 GUAVA&GREEN APPLE&RED APPLE COLD PREESED 16OZ",3,518.7,1),
    ("105","EVIAN",48,5383.2,3),
    ("105","WATERMELON 400G.",7,981.33,2),
    ("105","COCONUT READY TO DRINK",6,953.28,2),
    ("105","S1 COCONUT SMOOTHIE 22OZ",4,766.36,2),
    ("105","3 kinds of fruit400g Papaya/Pineapple/Guava",4,560.76,2),
    ("105","S5 MANGO SMOOTHIE 22OZ",4,691.59,1),
    ("105","S2 MANGO PASSION SMOOTHIE 22OZ",4,691.59,2),
    ("105","S2 MANGO PASSION SMOOTHIE 16OZ",4,598.12,2),
    ("105","MANGO 400G.",3,448.59,2),
    ("105","MAEVAREE MANGO STICKY RICE SMOOTHIE 22OZ",3,644.85,3),
    ("105","S3 WATERMELON SMOOTHIE 16OZ",3,448.6,2),
    ("105","PAPAYA 400G.",3,420.56,1),
    ("105","Chicken Club Croissant",3,417.75,2),
    ("105","Cantaloupe 400 g (Pack)",3,420.57,2),
    ("105","PRIDE PARROT RED",2,373.84,2),
    ("105","T1 ICED THAI MILK TEA 16OZ",2,280.38,1),
    ("105","LYCHEE 400G.",2,317.75,2),
    ("105","T1 ICED THAI MILK TEA 22OZ",2,327.1,2),
    ("105","PRIDE PARROT YELLOW",2,373.83,2),
    ("105","S5 MANGO SMOOTHIE 16OZ",2,299.06,2),
    ("109","Evian 500ml. (Bottle)",26,2915.9,3),
    ("109","Up size Smoothie & Cold Press Juice 16 oz. to 22 oz .",9,210.24,3),
    ("109","Coconut (EA)",8,1271.03,2),
    ("109","Mango 400 g. (Pack)",6,897.18,2),
    ("109","C1 Guava & green apple & red apple cold pressed 16oz",4,691.6,1),
    ("109","Watermelon 400 g. (Pack)",4,560.76,2),
    ("109","Pineapple 400 g. (Pack)",4,560.76,2),
    ("109","Fanta Strawberry 450 ml. (Bottle)",3,224.31,2),
    ("109","CH4 Americano (hot) 12oz",3,378.51,2),
    ("109","C2 orange cold pressed 16oz",3,518.7,2),
    ("109","YS2 Strawberry yoghurt smoothie 16oz",3,490.65,2),
    ("109","Hot water 12oz",2,56.08,2),
    ("109","CH1 Cappuccino (hot) 12oz",2,280.38,2),
    ("109","Tuna Salad Japanese Rice Balls (Onigiri)",2,203.74,1),
    ("109","Coke Zero 500 ml. (Bottle)",2,149.54,1),
    ("109","Butter Croissant",2,186.92,2),
    ("109","C6 pineapple cold pressed 16oz",2,345.8,2),
    ("109","YS1 mango yoghurt smoothie 16oz",2,327.11,1),
    ("109","Indian Tea Cardamom Chai 12oz",2,224.3,1),
]

from collections import defaultdict as dd2
by_branch_b = {"MW1":[],"SE3":[],"PKT":[]}
for (loc, memo, qty, rev, bills) in qb_raw:
    b = LOC_MAP[loc]
    by_branch_b[b].append((qty, rev, bills, memo))

def trunc(s, n=34): return s[:n]+"…" if len(s)>n else s

top20_branches = []
branch_labels = {"MW1":"MW1 · 26-T1MW1-03+04","SE3":"SE3 · 27-T1SE3-05","PKT":"PKT · 28 Unit 362 (Phuket)"}
for branch in BRANCH_ORDER:
    rows_raw = sorted(by_branch_b[branch], reverse=True)[:20]
    rows = []
    for i,(qty,rev,bills,memo) in enumerate(rows_raw):
        rows.append({
            "rank": i+1,
            "memo_display": trunc(memo),
            "memo_full": memo,
            "qty": qty,
            "revenue": fmt(rev),
            "bills": bills,
            "row_bg": "#fff" if i%2==0 else "#FAFAFA",
        })
    top20_branches.append({
        "header_color": BRANCH_COLORS[branch],
        "header_label": branch_labels[branch],
        "top20_rows": rows,
    })

# ── Query D — Dormant SKUs ─────────────────────────────────────────────────────
# Filter: qty_30d >= 3, drop \n memos, drop 'Transfer Deduct', 'Add-on aloe vera' etc
qd_raw = [
    ("33","SHINE MUSCAT GRAPES 400G (PACK)","21/05/2026",36,14,5383.1),
    ("33","HOT CHOCOLATE 8 oz","27/05/2026",18,4,2186.96),
    ("33","VANILLA BEAN GREEK YOGURT","26/05/2026",14,11,2472.91),
    ("33","RASPBERRY GREEK YOGURT","22/05/2026",9,7,1589.7),
    ("33","SEEDLESS GRAPE 400G.","26/05/2026",7,5,1046.71),
    ("33","Mango Berry Smoothie 16oz","23/05/2026",5,4,864.5),
    ("33","CI1 ICED ESPRESSO ORANGE 16OZ","23/05/2026",5,4,934.6),
    ("33","Mango Pineapple Smoothie 16oz","23/05/2026",4,2,691.59),
    ("33","CAESAR SALAD","29/05/2026",4,3,672.88),
    ("33","MANGO TOPPING","27/05/2026",3,3,70.08),
    ("33","HONEY TOPPING","27/05/2026",3,3,70.08),
    ("105","HOT CHOCOLATE 8 oz","29/05/2026",22,6,2672.98),
    ("105","BANANA YOGHURT SMOOTHIE 16OZ","28/05/2026",9,7,1471.95),
    ("105","MANGO BERRY SMOOTHIE 16OZ","19/05/2026",8,5,1383.2),
    ("105","Overnight Oat Berry 16 oz","27/05/2026",7,5,1694.4),
    ("105","T2 ICED THAI TEA WITH LIME 22OZ","28/05/2026",7,7,1144.85),
    ("105","CI4 ICED CAPPUCCINO 22OZ","30/05/2026",6,5,1093.43),
    ("109","Orange Cold Pressed Juice 300 ml. (bottle)","27/05/2026",13,9,2247.66),
    ("109","Mango Pineapple Smoothie 16oz","28/05/2026",11,9,1901.93),
    ("109","Mango Berry Smoothie 16oz","30/05/2026",10,6,1728.97),
    ("109","Ebiko salad Japanese Rice Balls (Onigiri)","30/05/2026",6,5,611.22),
    ("109","Mango Sticky Rice (Box)","25/05/2026",5,5,1168.21),
]

def gap_color(last_str):
    ld = parse_dd(last_str.replace("/","/")); g=(report_dt-ld).days
    return "#E65100" if g<14 else "#C62828", g

dormant_by_branch = {"MW1":[],"SE3":[],"PKT":[]}
for (loc, memo, last, qty, days, rev) in qd_raw:
    b = LOC_MAP.get(loc, loc)
    col, gap = gap_color(last)
    dormant_by_branch[b].append({
        "memo_display": trunc(memo),
        "memo_full": memo,
        "last_sold": parse_dd(last).strftime("%-d %b"),
        "gap_days": gap,
        "gap_color": col,
        "qty_30d": qty,
        "days_sold_30d": days,
        "rev_30d": fmt(rev),
    })

dormant_branches = []
for branch in BRANCH_ORDER:
    rows = dormant_by_branch[branch]
    dormant_branches.append({
        "branch": branch,
        "header_color": BRANCH_COLORS[branch],
        "branch_count": len(rows),
        "dormant_rows": rows,
    })

dormant_count = sum(len(dormant_by_branch[b]) for b in BRANCH_ORDER)

# ── Query E — Grape baseline ──────────────────────────────────────────────────
# MW1: SHINE MUSCAT 891u ฿133186.69 (Dec1→May21) + SEEDLESS 7u ฿1046.71
# SE3: SHINE MUSCAT 706u ฿105553.37 (Dec5→Apr28) + SEEDLESS 17u ฿2542.01
grape_total_rev = 133186.69 + 105553.37 + 1046.71 + 2542.01  # 242328.78
# Baseline per juiceland-queries.md: MW1 ฿339/d, SE3 ฿251/d
mw1_grape_baseline = 339
se3_grape_baseline = 251
grape_last_mw1 = "21 May 2026"
grape_last_se3 = "28 Apr 2026"

# ── Query C — New product data ─────────────────────────────────────────────────
# PRIDE PARROT RED
pp_red = {"memo":"PRIDE PARROT RED","launch":"1 Jun 2026","type":"drinks","notes":"Rainbow parrot smoothie"}
pp_red_data = [
    ("01/06/2026","33",3,560.76),("01/06/2026","105",1,186.92),
    ("02/06/2026","33",6,1121.51),("02/06/2026","105",1,186.92),
    ("03/06/2026","33",4,747.67),
    ("04/06/2026","33",7,1308.43),
    ("05/06/2026","33",12,2243.03),("05/06/2026","105",3,542.06),
    ("06/06/2026","33",8,1495.35),("06/06/2026","105",2,373.84),
]
pp_red_mw1_qty = sum(q for d,l,q,r in pp_red_data if l=="33")
pp_red_se3_qty = sum(q for d,l,q,r in pp_red_data if l=="105")
pp_red_tot_qty = pp_red_mw1_qty + pp_red_se3_qty  # 47
pp_red_tot_rev = sum(r for d,l,q,r in pp_red_data)  # 8765.53
pp_red_mw1_days = len(set(d for d,l,q,r in pp_red_data if l=="33"))  # 6
pp_red_se3_days = len(set(d for d,l,q,r in pp_red_data if l=="105"))  # 3
pp_red_mw1_per_day = round(sum(r for d,l,q,r in pp_red_data if l=="33") / 6, 0)
pp_red_se3_per_day = round(sum(r for d,l,q,r in pp_red_data if l=="105") / 3, 0)
pp_red_yest = sum(q for d,l,q,r in pp_red_data if d=="06/06/2026")  # 10

# PRIDE PARROT YELLOW
pp_yel_data = [
    ("01/06/2026","33",2,373.83),("01/06/2026","105",1,186.92),
    ("02/06/2026","33",3,560.76),
    ("03/06/2026","33",2,373.83),
    ("04/06/2026","33",5,934.57),
    ("05/06/2026","33",5,934.6),("05/06/2026","105",1,186.92),
    ("06/06/2026","33",7,1308.42),("06/06/2026","105",2,373.83),
]
pp_yel_mw1_qty = sum(q for d,l,q,r in pp_yel_data if l=="33")
pp_yel_se3_qty = sum(q for d,l,q,r in pp_yel_data if l=="105")
pp_yel_tot_qty = pp_yel_mw1_qty + pp_yel_se3_qty  # 28
pp_yel_tot_rev = sum(r for d,l,q,r in pp_yel_data)  # 4933.68
pp_yel_yest = sum(q for d,l,q,r in pp_yel_data if d=="06/06/2026")  # 9

# LYCHEE 400G.
lychee_data = [
    ("28/05/2026","33",2,317.76),
    ("29/05/2026","105",3,476.64),
    ("01/06/2026","105",1,158.88),
    ("03/06/2026","105",1,158.88),
    ("04/06/2026","33",2,317.76),
    ("05/06/2026","105",4,635.52),
    ("06/06/2026","105",2,317.75),
]
lychee_mw1_qty = sum(q for d,l,q,r in lychee_data if l=="33")  # 4
lychee_se3_qty = sum(q for d,l,q,r in lychee_data if l=="105")  # 11
lychee_tot_qty = lychee_mw1_qty + lychee_se3_qty  # 15
lychee_tot_rev = sum(r for d,l,q,r in lychee_data)  # 2383.19
lychee_mw1_days = len(set(d for d,l,q,r in lychee_data if l=="33"))  # 2
lychee_se3_days = len(set(d for d,l,q,r in lychee_data if l=="105"))  # 5
lychee_mw1_per_day = round(sum(r for d,l,q,r in lychee_data if l=="33") / max(lychee_mw1_days,1))
lychee_se3_per_day = round(sum(r for d,l,q,r in lychee_data if l=="105") / max(lychee_se3_days,1))
lychee_yest = sum(q for d,l,q,r in lychee_data if d=="06/06/2026")  # 2

# MANGOSTEEN
mango_st_data = [
    ("28/05/2026","105",1,233.64),
    ("31/05/2026","105",1,233.64),
    ("01/06/2026","105",1,233.64),
]
mango_st_qty = sum(q for d,l,q,r in mango_st_data)  # 3
mango_st_rev = sum(r for d,l,q,r in mango_st_data)  # 700.92
mango_st_days = len(set(d for d,l,q,r in mango_st_data))
mango_st_se3_per_day = round(mango_st_rev / max(mango_st_days,1))
mango_st_yest = 0  # not sold June 6

# SOFT-SLUSH! ORIGINAL
sso_data = [
    ("02/05","33",1,149.53),("03/05","33",2,299.06),("04/05","33",4,598.12),
    ("06/05","33",1,149.53),("07/05","33",1,149.53),("08/05","33",3,448.6),
    ("09/05","33",1,149.53),("10/05","33",1,149.53),("11/05","33",1,149.53),
    ("14/05","33",1,149.53),("17/05","33",1,149.54),("18/05","33",2,299.06),
    ("19/05","33",1,149.53),("20/05","33",1,149.54),("21/05","33",2,299.06),
    ("24/05","33",1,149.53),("26/05","33",2,299.06),("27/05","33",7,1046.73),
    ("29/05","33",1,149.53),("31/05","33",2,299.06),("01/06","33",2,299.06),
    ("03/06","33",1,149.53),("04/06","33",1,149.53),("05/06","33",5,747.65),
]
sso_qty = sum(q for d,l,q,r in sso_data)  # 45
sso_rev = sum(r for d,l,q,r in sso_data)  # 6728.9
sso_yest = 0  # not sold June 6

# SOFT-SLUSH! DELUXE
ssd_data = [
    ("01/05","33",2,448.6),("02/05","33",1,224.3),("03/05","33",3,672.89),
    ("04/05","33",3,672.9),("05/05","33",1,224.3),("07/05","33",1,224.3),
    ("08/05","33",3,672.88),("09/05","33",1,224.3),("10/05","33",1,224.3),
    ("11/05","33",1,224.3),("12/05","33",1,224.3),("13/05","33",3,672.9),
    ("15/05","33",1,224.3),("19/05","33",1,224.3),("20/05","33",1,224.3),
    ("21/05","33",2,448.61),("24/05","33",1,201.87),("26/05","33",2,448.6),
    ("31/05","33",1,224.3),("05/06","33",2,448.6),
]
ssd_qty = sum(q for d,l,q,r in ssd_data)  # 32
ssd_rev = sum(r for d,l,q,r in ssd_data)  # 7155.15
ssd_yest = 0  # not sold June 6

# New product type totals
drinks_units = pp_red_tot_qty + pp_yel_tot_qty  # 47+28=75
drinks_rev = round(pp_red_tot_rev + pp_yel_tot_rev)  # 13699
drinks_yest = pp_red_yest + pp_yel_yest  # 10+9=19

fruit_units = lychee_tot_qty + mango_st_qty  # 15+3=18
fruit_rev = round(lychee_tot_rev + mango_st_rev)  # 2383+701=3084
fruit_yest = lychee_yest + mango_st_yest  # 2

new_cat_units = sso_qty + ssd_qty  # 45+32=77
new_cat_rev = round(sso_rev + ssd_rev)  # 6729+7155=13884
new_cat_yest = sso_yest + ssd_yest  # 0

np_total_units = drinks_units + fruit_units + new_cat_units  # 170
np_total_rev = drinks_rev + fruit_rev + new_cat_rev  # 30667

# np_summary_line
np_summary_line = f"6 SKUs tracked · {drinks_units+fruit_units+new_cat_units} total units to date · ฿{np_total_rev:,} revenue"

# np_type_tables (REPEAT:np_type_tables with nested REPEAT:np_rows)
def make_status(yest, daily_avg, gap_days=0):
    if gap_days >= 2: return "🟠 Stock-out suspect"
    if daily_avg == 0: return "⚪ No baseline yet"
    pct_vs = yest / daily_avg if daily_avg else 0
    if pct_vs >= 1.0: return "🟢 On target"
    if pct_vs >= 0.5: return "🟡 Below target (≥50%)"
    return "🔴 Waste risk (<50%)"

np_rows_drinks = [
    {
        "memo": "PRIDE PARROT RED",
        "launch": "1 Jun 2026",
        "notes": "BKK launch — Pride month special",
        "total_units": pp_red_tot_qty,
        "total_rev": fmt(pp_red_tot_rev),
        "branch_split": f"MW1:{pp_red_mw1_qty}u · SE3:{pp_red_se3_qty}u",
        "yest_units": pp_red_yest,
        "status_badge": "🟢 On target",
    },
    {
        "memo": "PRIDE PARROT YELLOW",
        "launch": "1 Jun 2026",
        "notes": "BKK launch — Pride month special",
        "total_units": pp_yel_tot_qty,
        "total_rev": fmt(pp_yel_tot_rev),
        "branch_split": f"MW1:{pp_yel_mw1_qty}u · SE3:{pp_yel_se3_qty}u",
        "yest_units": pp_yel_yest,
        "status_badge": "🟢 On target",
    },
]
np_rows_fruit = [
    {
        "memo": "LYCHEE 400G.",
        "launch": "28 May 2026",
        "notes": "Seasonal – replaces grape at MW1+SE3",
        "total_units": lychee_tot_qty,
        "total_rev": fmt(lychee_tot_rev),
        "branch_split": f"MW1:{lychee_mw1_qty}u · SE3:{lychee_se3_qty}u",
        "yest_units": lychee_yest,
        "status_badge": "🟡 Below target (≥50%)",
    },
    {
        "memo": "MANGOSTEEN 400g.",
        "launch": "28 May 2026",
        "notes": "Seasonal – SE3 only",
        "total_units": mango_st_qty,
        "total_rev": fmt(mango_st_rev),
        "branch_split": f"SE3:{mango_st_qty}u",
        "yest_units": mango_st_yest,
        "status_badge": "🟠 Stock-out suspect",
    },
]
np_rows_newcat = [
    {
        "memo": "SOFT-SLUSH! ORIGINAL",
        "launch": "2 May 2026",
        "notes": "Slush drinks – MW1 only",
        "total_units": sso_qty,
        "total_rev": fmt(sso_rev),
        "branch_split": f"MW1:{sso_qty}u",
        "yest_units": sso_yest,
        "status_badge": "🟡 Below target (≥50%)",
    },
    {
        "memo": "SOFT-SLUSH! DELUXE",
        "launch": "1 May 2026",
        "notes": "Slush drinks – MW1 only",
        "total_units": ssd_qty,
        "total_rev": fmt(ssd_rev),
        "branch_split": f"MW1:{ssd_qty}u",
        "yest_units": ssd_yest,
        "status_badge": "🟡 Below target (≥50%)",
    },
]

np_type_tables = [
    {"type_bg":"#1565C0","type_fg":"#fff","type_icon":"🥤","type_label":"Drinks","np_rows":np_rows_drinks},
    {"type_bg":"#880E4F","type_fg":"#fff","type_icon":"🍉","type_label":"Seasonal Fruits","np_rows":np_rows_fruit},
    {"type_bg":"#1B5E20","type_fg":"#fff","type_icon":"⭐","type_label":"New Category","np_rows":np_rows_newcat},
]

# ── Seasonal tracker ──────────────────────────────────────────────────────────
# Lychee + Mangosteen replace grapes
# MW1 new fruit per day = lychee_mw1 / days in window since launch
mw1_fruit_per_day = round(lychee_mw1_per_day)  # ฿159/d (2 days, 317.76 total = ~159/d)
se3_fruit_per_day = round((lychee_se3_per_day * lychee_se3_days + mango_st_se3_per_day * mango_st_days) / max(lychee_se3_days + mango_st_days,1))

# Coverage
mw1_coverage = round(mw1_fruit_per_day / mw1_grape_baseline * 100)
se3_coverage = round(se3_fruit_per_day / se3_grape_baseline * 100)

def coverage_info(cov):
    if cov >= 100: return "#155724","#D4EDDA","✅ Fully replaced"
    if cov >= 70: return "#856404","#FFF3CD","🟡 Partial — monitor"
    return "#721C24","#F8D7DA","🔴 Large gap — push promotion or add SKU"

mw1_cov_color, mw1_badge_bg, mw1_badge_text = coverage_info(mw1_coverage)
se3_cov_color, se3_badge_bg, se3_badge_text = coverage_info(se3_coverage)

seasonal_skus = [
    {"fruit_emoji":"🍈","memo":"LYCHEE 400G.","launch":"28 May 2026",
     "mw1_units":lychee_mw1_qty,"mw1_per_day":f"฿{lychee_mw1_per_day:,}",
     "se3_units":lychee_se3_qty,"se3_per_day":f"฿{lychee_se3_per_day:,}"},
    {"fruit_emoji":"🍊","memo":"MANGOSTEEN 400g.","launch":"28 May 2026",
     "mw1_units":0,"mw1_per_day":"—",
     "se3_units":mango_st_qty,"se3_per_day":f"฿{mango_st_se3_per_day:,}"},
]

mw1_daily_gap = mw1_grape_baseline - mw1_fruit_per_day
se3_daily_gap = se3_grape_baseline - se3_fruit_per_day
seasonal_coverage = [
    {
        "branch_color":"#5551FE","branch_label":"MW1 · Suvarnabhumi T1MW",
        "grape_baseline":f"{mw1_grape_baseline:,}",
        "new_fruit_per_day":f"{mw1_fruit_per_day:,}",
        "coverage_pct":mw1_coverage,
        "coverage_color":mw1_cov_color,
        "daily_gap":f"−฿{mw1_daily_gap:,}/d" if mw1_daily_gap>0 else "฿0 (covered)",
        "monthly_impact":f"−฿{mw1_daily_gap*30:,}/mo" if mw1_daily_gap>0 else "฿0",
        "badge_bg":mw1_badge_bg,"badge_text":mw1_badge_text,
    },
    {
        "branch_color":"#F27061","branch_label":"SE3 · Suvarnabhumi T1SE",
        "grape_baseline":f"{se3_grape_baseline:,}",
        "new_fruit_per_day":f"{se3_fruit_per_day:,}",
        "coverage_pct":se3_coverage,
        "coverage_color":se3_cov_color,
        "daily_gap":f"−฿{se3_daily_gap:,}/d" if se3_daily_gap>0 else "฿0 (covered)",
        "monthly_impact":f"−฿{se3_daily_gap*30:,}/mo" if se3_daily_gap>0 else "฿0",
        "badge_bg":se3_badge_bg,"badge_text":se3_badge_text,
    },
]

# ── AM review ─────────────────────────────────────────────────────────────────
# From dormant: items that are truly new products (in new-product registry) with gap
# PP RED and PP YELLOW sold yesterday so no AM review needed
# LYCHEE sold yesterday so no AM review
# MANGOSTEEN: last sold June 1, gap = 5 days — under 7, not in dormant
# SOFT-SLUSH! ORIGINAL: not sold June 6, not sold June 5? June 5 yes. Not dormant.
# No new products qualify for AM review (none in dormant with 7+ day gap)
am_items = []
am_queue_count = len(am_items)

# ── Scalars ───────────────────────────────────────────────────────────────────
def sfmt(v): return f"+{v}" if v>0 else str(v)

scalars = {
    "report_date_display": "6 June 2026",
    "report_date": "2026-06-06",
    "report_day_th": report_day_th,
    "window_30d_start": "8 May 2026",
    "generated_timestamp": GENERATED_TS,
    "subject_prefix": subject_prefix,
    "comb_net": fmt(comb_net_yest),
    "signed_pct": sfmt(signed_pct),
    "mw1_net": fmt(mw1_net_yest),
    "se3_net": fmt(se3_net_yest),
    "pkt_net": fmt(pkt_net_yest),
    "mw1_bills": mw1_bills_yest,
    "se3_bills": se3_bills_yest,
    "pkt_bills": pkt_bills_yest,
    "mw1_vs_30d": sfmt(mw1_vs),
    "se3_vs_30d": sfmt(se3_vs),
    "pkt_vs_30d": sfmt(pkt_vs),
    "mw1_avg_30d": fmt(mw1_avg),
    "se3_avg_30d": fmt(se3_avg),
    "pkt_avg_30d": fmt(pkt_avg),
    "comb_avg_30d": fmt(comb_avg),
    "mw1_min_30d": fmt(mw1_min),
    "mw1_max_30d": fmt(mw1_max),
    "se3_min_30d": fmt(se3_min),
    "se3_max_30d": fmt(se3_max),
    "pkt_min_30d": fmt(pkt_min),
    "pkt_max_30d": fmt(pkt_max),
    "comb_monthly_runrate": f"{round(comb_avg*30/1000,1):,}K",
    "last7_total": fmt(comb_7d_total),
    "last7_avg": fmt(last7_avg),
    "mw1_7d_total": fmt(mw1_7d_total),
    "se3_7d_total": fmt(se3_7d_total),
    "pkt_7d_total": fmt(pkt_7d_total),
    "comb_7d_total": fmt(comb_7d_total),
    # NP
    "np_summary_line": np_summary_line,
    "np_total_units": np_total_units,
    "np_total_rev": fmt(np_total_rev),
    "drinks_n": 2,
    "drinks_todate_units": drinks_units,
    "drinks_todate_rev": fmt(drinks_rev),
    "fruit_n": 2,
    "fruit_todate_units": fruit_units,
    "fruit_todate_rev": fmt(fruit_rev),
    "new_cat_n": 2,
    "new_cat_todate_units": new_cat_units,
    "new_cat_todate_rev": fmt(new_cat_rev),
    # Seasonal
    "grape_total_rev": fmt(grape_total_rev),
    "grape_last_mw1": grape_last_mw1,
    "grape_last_se3": grape_last_se3,
    # Dormant
    "dormant_count": dormant_count,
    # AM review
    "am_queue_count": am_queue_count,
}

repeats = {
    "chart_days": chart_days,
    "last7_headers": last7_headers,
    "last7_mw1": make_last7("MW1"),
    "last7_se3": make_last7("SE3"),
    "last7_pkt": make_last7("PKT"),
    "last7_comb": make_last7_comb(),
    "top20_branches": top20_branches,
    "np_type_tables": np_type_tables,
    "seasonal_skus": seasonal_skus,
    "seasonal_coverage": seasonal_coverage,
    "dormant_branches": dormant_branches,
    "am_items": am_items,
}

sections = {
    "am_review": am_queue_count > 0,
    "seasonal": fruit_units > 0,
    "dormant": dormant_count > 0,
    "forecast_shown": False,
    "forecast_suppressed": True,
    "anomaly_shown": False,
}

data = {"scalars": scalars, "repeats": repeats, "sections": sections}

with open("/home/user/report/data.json","w",encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"report_date: 2026-06-06")
print(f"MW1: ฿{fmt(mw1_net_yest)} ({sfmt(mw1_vs)}% vs 30d) · {mw1_bills_yest} bills")
print(f"SE3: ฿{fmt(se3_net_yest)} ({sfmt(se3_vs)}% vs 30d) · {se3_bills_yest} bills")
print(f"PKT: ฿{fmt(pkt_net_yest)} ({sfmt(pkt_vs)}% vs 30d) · {pkt_bills_yest} bills")
print(f"COMB: ฿{fmt(comb_net_yest)} ({sfmt(comb_vs)}% vs 30d avg ฿{fmt(comb_avg)})")
print(f"dormant_count={dormant_count} am_queue_count={am_queue_count}")
print(f"sections: am_review={sections['am_review']} seasonal={sections['seasonal']} dormant={sections['dormant']}")
print("data.json written.")
