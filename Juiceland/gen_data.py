#!/usr/bin/env python3
"""Generate data.json for the Juiceland Daily Sales Report — 7 June 2026."""
import json

# ── helpers ──────────────────────────────────────────────────────────────────
def fmt(n): return f"{int(round(n)):,}"
def fmtd(n): return f"{n:,.1f}"

# ── dates ────────────────────────────────────────────────────────────────────
report_date          = "2026-06-07"
report_date_display  = "7 June 2026"
report_day_th        = "วันอาทิตย์"
window_30d_start_iso = "2026-05-09"
window_30d_start_disp= "9 May 2026"
generated_timestamp  = "2026-06-08 07:30"

# ── Query A daily data (30 days, 3 branches) ─────────────────────────────────
# MW1 = loc33, SE3 = loc105, PKT = loc109
daily = [
    # date_iso, day_num, weekday_th_abbr, mw1, se3, pkt
    ("2026-05-09",  9, "ส.",   27290,   22575,  9516),
    ("2026-05-10", 10, "อา.",  36901,   26350, 10994),
    ("2026-05-11", 11, "จ.",   33927.5, 25400,  9884),
    ("2026-05-12", 12, "อ.",   31386,   18990, 11704),
    ("2026-05-13", 13, "พ.",   34122,   25085, 13897),
    ("2026-05-14", 14, "พฤ.",  40908,   21800,  7820),
    ("2026-05-15", 15, "ศ.",   35787,   19010, 10244),
    ("2026-05-16", 16, "ส.",   30765.5, 25470,  9920),
    ("2026-05-17", 17, "อา.",  34754,   35410, 13484),
    ("2026-05-18", 18, "จ.",   25913,   22700, 12484),
    ("2026-05-19", 19, "อ.",   33034.5, 25820,  7867),
    ("2026-05-20", 20, "พ.",   31093,   17307.5,10311),
    ("2026-05-21", 21, "พฤ.",  36940.5, 29297,  9611),
    ("2026-05-22", 22, "ศ.",   40088,   26689, 10358),
    ("2026-05-23", 23, "ส.",   38639.5, 39492, 12698),
    ("2026-05-24", 24, "อา.",  45429.5, 28328, 12933),
    ("2026-05-25", 25, "จ.",   38221,   31983.5,10502),
    ("2026-05-26", 26, "อ.",   36852.5, 24575.5, 7039),
    ("2026-05-27", 27, "พ.",   33877,   26502, 16234),
    ("2026-05-28", 28, "พฤ.",  33415,   31121, 12474),
    ("2026-05-29", 29, "ศ.",   42210.5, 22568, 13844),
    ("2026-05-30", 30, "ส.",   34788,   26883, 14605),
    ("2026-05-31", 31, "อา.",  28583,   32544, 14052),
    ("2026-06-01",  1, "จ.",   32133,   24075, 13940),
    ("2026-06-02",  2, "อ.",   36476,   15959,  9920),
    ("2026-06-03",  3, "พ.",   40024,   19497, 10813),
    ("2026-06-04",  4, "พฤ.",  35666.5, 16604, 13146),
    ("2026-06-05",  5, "ศ.",   35611,   20180, 13589),
    ("2026-06-06",  6, "ส.",   32714,   23312, 13867),
    ("2026-06-07",  7, "อา.",  25977,   17749, 12993),
]

chart_max = max(max(r[3], r[4], r[5]) for r in daily)  # 45429.5

chart_days = []
for (dt, dn, wth, mw1, se3, pkt) in daily:
    chart_days.append({
        "date": dt,
        "day_num": str(dn),
        "weekday_th_abbr": wth,
        "mw1_net": fmt(mw1),
        "se3_net": fmt(se3),
        "pkt_net": fmt(pkt),
        "mw1_bar_px": str(round(mw1 / chart_max * 220)),
        "se3_bar_px": str(round(se3 / chart_max * 220)),
        "pkt_bar_px": str(round(pkt / chart_max * 220)),
    })

# ── 30-day KPIs ──────────────────────────────────────────────────────────────
mw1_vals = [r[3] for r in daily]
se3_vals = [r[4] for r in daily]
pkt_vals = [r[5] for r in daily]
comb_vals = [r[3]+r[4]+r[5] for r in daily]

mw1_sum = sum(mw1_vals);  mw1_avg = mw1_sum/30
se3_sum = sum(se3_vals);  se3_avg = se3_sum/30
pkt_sum = sum(pkt_vals);  pkt_avg = pkt_sum/30
comb_sum = sum(comb_vals);comb_avg = comb_sum/30

yest_mw1  = daily[-1][3]; yest_se3 = daily[-1][4]; yest_pkt = daily[-1][5]
yest_comb = yest_mw1 + yest_se3 + yest_pkt

signed_pct    = round((yest_comb - comb_avg) / comb_avg * 100, 1)
mw1_vs_30d    = round((yest_mw1  - mw1_avg)  / mw1_avg  * 100, 1)
se3_vs_30d    = round((yest_se3  - se3_avg)  / se3_avg  * 100, 1)
pkt_vs_30d    = round((yest_pkt  - pkt_avg)  / pkt_avg  * 100, 1)

subject_prefix = "⚠️" if signed_pct <= -10 else ("🔥" if signed_pct >= 10 else "✅")

comb_runrate_k = comb_avg * 30 / 1000

# ── Last 7 days ───────────────────────────────────────────────────────────────
last7 = daily[-7:]
last7_headers, last7_mw1, last7_se3, last7_pkt, last7_comb = [], [], [], [], []
for i, (dt, dn, wth, mw1, se3, pkt) in enumerate(last7):
    is_yest = (i == 6)
    hbg  = "background:#4744CD;" if is_yest else ""
    cbg  = "background:#FFF3E0;font-weight:700;" if is_yest else ""
    ccbg = "background:#FFF3E0;" if is_yest else ""
    d, m = dt[8:], str(int(dt[5:7]))
    last7_headers.append({"col_date": f"{int(d)}/{m}", "col_weekday_th": wth, "header_bg": hbg})
    last7_mw1.append({"net": fmt(mw1), "cell_style": cbg})
    last7_se3.append({"net": fmt(se3), "cell_style": cbg})
    last7_pkt.append({"net": fmt(pkt), "cell_style": cbg})
    last7_comb.append({"net": fmt(mw1+se3+pkt), "cell_bg": ccbg})

mw1_7d = sum(r[3] for r in last7); se3_7d = sum(r[4] for r in last7)
pkt_7d = sum(r[5] for r in last7); comb_7d = mw1_7d+se3_7d+pkt_7d

# ── AM Review items ───────────────────────────────────────────────────────────
am_items = [
    {"memo":"HOT CHOCOLATE 8 oz","last_sold":"27/05/2026","gap_days":"11","velocity_7d":"0","target":"4","branch_split":"MW1 only","hypothesis_text":"Stock-out or pilot ended early","hypothesis_color":"#E65100"},
    {"memo":"HOT CHOCOLATE 8 oz","last_sold":"29/05/2026","gap_days":"9","velocity_7d":"0","target":"4","branch_split":"SE3 only","hypothesis_text":"Stock-out or pilot ended early","hypothesis_color":"#E65100"},
    {"memo":"VANILLA BEAN GREEK YOGURT","last_sold":"26/05/2026","gap_days":"12","velocity_7d":"0","target":"1.5","branch_split":"MW1 only","hypothesis_text":"Low demand — consider pulling","hypothesis_color":"#856404"},
    {"memo":"RASPBERRY GREEK YOGURT","last_sold":"22/05/2026","gap_days":"16","velocity_7d":"0","target":"1.5","branch_split":"MW1 only","hypothesis_text":"Low demand — consider pulling","hypothesis_color":"#856404"},
    {"memo":"Mango Sticky Rice\xa0(Box)","last_sold":"31/05/2026","gap_days":"7","velocity_7d":"0","target":"2.5","branch_split":"SE3 only","hypothesis_text":"Stock-out suspected","hypothesis_color":"#E65100"},
    {"memo":"Overnight Oat Berry 16 oz","last_sold":"27/05/2026","gap_days":"11","velocity_7d":"0","target":"1.5","branch_split":"SE3 only","hypothesis_text":"Low demand or supply issue","hypothesis_color":"#856404"},
    {"memo":"BLUEBERRY GREEK YOGURT","last_sold":"05/06/2026","gap_days":"2","velocity_7d":"0.3","target":"1.5","branch_split":"MW1 only","hypothesis_text":"Declining — monitor closely","hypothesis_color":"#1565C0"},
]
am_queue_count = len(am_items)

# ── Top 20 per branch (pre-rendered rows HTML) ────────────────────────────────
def row_html(rank, memo, bills, qty, revenue, odd):
    bg = "#fff" if odd else "#FAFAFA"
    m34 = (memo[:33] + "…") if len(memo) > 34 else memo
    return (f'<tr style="background:{bg};">'
            f'<td style="padding:5px 6px;border-bottom:1px solid #eee;vertical-align:top;font-size:10px;color:#888;">{rank}</td>'
            f'<td style="padding:5px 6px;border-bottom:1px solid #eee;vertical-align:top;" title="{memo}">'
            f'<div style="font-weight:600;font-size:10px;line-height:1.2;">{m34}</div>'
            f'<div style="font-size:9px;color:#888;">{bills} bills</div></td>'
            f'<td style="padding:5px 6px;text-align:right;border-bottom:1px solid #eee;vertical-align:top;font-size:10px;">{qty}</td>'
            f'<td style="padding:5px 6px;text-align:right;border-bottom:1px solid #eee;vertical-align:top;font-size:10px;">฿{revenue}</td>'
            f'</tr>')

def build_top20_html(rows_data):
    html = ""
    for i,(memo,bills,qty,rev) in enumerate(rows_data[:20]):
        html += row_html(i+1, memo, bills, fmt(qty), fmt(rev), i%2==0)
    return html

mw1_top20_data = [
    ("EVIAN",39,39,4373.85,4),("MANGO 400G.",8,8,1196.24,2),
    ("WATERMELON 400G.",7,7,981.33,1),("COCONUT JUICE BOTTLE",6,6,1037.39,3),
    ("S5 MANGO SMOOTHIE 22OZ",6,6,1037.4,2),("COCONUT READY TO DRINK",6,6,953.28,2),
    ("S3 WATERMELON SMOOTHIE 22OZ",5,5,864.5,2),("S1 COCONUT SMOOTHIE 22OZ",5,5,957.95,3),
    ("CH2 HOT AMERICANO",4,4,504.68,2),("3 kinds of fruit400g Papaya/Pineapple/Guava",4,4,560.76,2),
    ("WATERMELON JUICE BOTTLE",4,4,691.59,1),("PRIDE PARROT RED",4,4,747.68,3),
    ("PRIDE PARROT YELLOW",3,3,560.76,2),("Mango juice (Bottle) 300 ml",3,3,518.7,3),
    ("P1 GOLDEN GLOW 22OZ",3,3,630.84,2),("PINEAPPLE JUICE BOTTLE",3,3,518.69,2),
    ("CARROT JUICE BOTTLE",3,3,518.69,2),("PINEAPPLE 400G.",2,2,280.37,1),
    ("Mango passion juice (Bottle) 300 ml",2,2,345.79,1),
    ("C5 PINEAPPLE&GREEN APPLE COLD PREESED 22OZ",2,2,392.52,2),
]
# fix: cols are (memo, qty, qty, rev, bills) → normalise
def top20_html_from(rows):
    html = ""
    for i,(memo,qty,_,rev,bills) in enumerate(rows[:20]):
        html += row_html(i+1, memo, bills, fmt(qty), fmt(rev), i%2==0)
    return html

mw1_rows_raw = [
    ("EVIAN",39,39,4373.85,4),("MANGO 400G.",8,8,1196.24,2),
    ("WATERMELON 400G.",7,7,981.33,1),("COCONUT JUICE BOTTLE",6,6,1037.39,3),
    ("S5 MANGO SMOOTHIE 22OZ",6,6,1037.4,2),("COCONUT READY TO DRINK",6,6,953.28,2),
    ("S3 WATERMELON SMOOTHIE 22OZ",5,5,864.5,2),("S1 COCONUT SMOOTHIE 22OZ",5,5,957.95,3),
    ("CH2 HOT AMERICANO",4,4,504.68,2),("3 kinds of fruit400g Papaya/Pineapple/Guava",4,4,560.76,2),
    ("WATERMELON JUICE BOTTLE",4,4,691.59,1),("PRIDE PARROT RED",4,4,747.68,3),
    ("PRIDE PARROT YELLOW",3,3,560.76,2),("Mango juice (Bottle) 300 ml",3,3,518.7,3),
    ("P1 GOLDEN GLOW 22OZ",3,3,630.84,2),("PINEAPPLE JUICE BOTTLE",3,3,518.69,2),
    ("CARROT JUICE BOTTLE",3,3,518.69,2),("PINEAPPLE 400G.",2,2,280.37,1),
    ("Mango passion juice (Bottle) 300 ml",2,2,345.79,1),
    ("C5 PINEAPPLE&GREEN APPLE COLD PREESED 22OZ",2,2,392.52,2),
]
se3_rows_raw = [
    ("EVIAN",21,21,2355.15,4),("COCONUT READY TO DRINK",9,9,1429.92,4),
    ("WATERMELON 400G.",9,9,1261.71,2),("3 kinds of fruit400g Papaya/Pineapple/Guava",8,8,1121.52,2),
    ("PRIDE PARROT RED",6,6,1121.52,3),("YS1 MANGO YOGHURT SMOOTHIE 22OZ",4,4,747.67,2),
    ("MANGO 400G.",4,4,598.12,2),("PINEAPPLE 400G.",3,3,420.57,2),
    ("S5 MANGO SMOOTHIE 22OZ",2,2,345.79,1),("COCONUT JUICE BOTTLE",2,2,345.8,2),
    ("C1 GUAVA&GREEN APPLE&RED APPLE COLD PREESED 16OZ",2,2,345.8,2),
    ("S4 MIXBERRY SMOOTHIE 22OZ",2,2,345.8,1),("S2 MANGO PASSION SMOOTHIE 16OZ",2,2,299.06,1),
    ("S2 MANGO PASSION SMOOTHIE 22OZ",2,2,345.8,2),("PAPAYA 400G.",2,2,280.38,2),
    ("P1 GOLDEN GLOW 22OZ",1,1,210.28,1),("CH3 HOT CAPPUCCINO",1,1,140.19,1),
    ("MANGO (1 PCS.) 380 G.",1,1,140.19,1),("Chicken Club Croissant",1,1,139.25,1),
    ("MANGO PASSION JUICE (BOTTLE) 300 ML",1,1,172.9,1),
]
pkt_rows_raw = [
    ("Evian 500ml. (Bottle)",16,16,1794.4,2),
    ("Up size Smoothie & Cold Press Juice 16→22oz",7,7,163.52,2),
    ("Mango 400 g. (Pack)",6,6,897.18,2),("Coconut (EA)",6,6,953.28,1),
    ("CH2 Caffe latte (hot) 12oz",5,5,700.92,2),("Watermelon 400 g. (Pack)",4,4,560.76,1),
    ("Watermelon Cold Pressed Juice 300ml (bottle)",3,3,518.7,1),
    ("Mango Berry Smoothie 16oz",3,3,518.7,2),("Ham and Cheese Croissant",2,2,355.14,1),
    ("C6 pineapple cold pressed 16oz",2,2,345.8,1),("S5 mango smoothie 16oz",2,2,299.06,2),
    ("YS2 Strawberry yoghurt smoothie 16oz",2,2,327.1,1),
    ("S3 watermelon smoothie 16oz",2,2,299.08,2),("Mango juice (Bottle) 300 ml",2,2,345.79,1),
    ("Pineapple 400 g. (Pack)",2,2,280.38,2),
    ("C5 pineapple & green apple cold pressed 16oz",2,2,345.8,2),
    ("Tuna Sandwich",1,1,168.23,1),("Salt Grilled Salmon Onigiri",1,1,101.87,1),
    ("Pride Parrot Yellow Smoothie 22oz",1,1,186.91,1),("CI3 Iced Cappuccino 16oz",1,1,158.88,1),
]

top20_branches = [
    {"header_color":"#5551FE","header_label":"MW1 · 26-T1MW1-03+04",
     "top20_rows_html": top20_html_from(mw1_rows_raw)},
    {"header_color":"#F27061","header_label":"SE3 · 27-T1SE3-05",
     "top20_rows_html": top20_html_from(se3_rows_raw)},
    {"header_color":"#2E7D32","header_label":"PKT · 28 Unit 362 (Phuket)",
     "top20_rows_html": top20_html_from(pkt_rows_raw)},
]

# ── Dormant SKUs (pre-rendered rows HTML) ─────────────────────────────────────
def dorm_row(memo, qty_30d, days_sold, rev_30d, last_sold, gap_days):
    gc = "#C62828" if gap_days >= 14 else "#E65100"
    m34 = (memo[:33]+"…") if len(memo)>34 else memo
    return (f'<tr style="background:#fff;border-bottom:1px solid #eee;">'
            f'<td style="padding:5px 6px;vertical-align:top;" title="{memo}">'
            f'<div style="font-weight:600;font-size:10px;line-height:1.2;">{m34}</div>'
            f'<div style="font-size:9px;color:#888;margin-top:1px;">Was selling: {qty_30d}u over {days_sold}d (฿{rev_30d})</div>'
            f'</td><td style="padding:5px 6px;text-align:right;vertical-align:top;color:{gc};font-weight:700;font-size:10px;">{gap_days}d</td>'
            f'</tr>')

mw1_dorm = [
    ("SHINE MUSCAT GRAPES 400G (PACK)",34,13,"5,084","21/05/2026",17),
    ("HOT CHOCOLATE 8 oz",18,4,"2,187","27/05/2026",11),
    ("VANILLA BEAN GREEK YOGURT",14,11,"2,473","26/05/2026",12),
    ("RASPBERRY GREEK YOGURT",9,7,"1,590","22/05/2026",16),
    ("SEEDLESS GRAPE 400G.",7,5,"1,047","26/05/2026",12),
    ("CI1 ICED ESPRESSO ORANGE 16OZ",5,4,"935","23/05/2026",15),
    ("Mango Berry Smoothie 16oz",5,4,"865","26/05/2026",12),
    ("Mango Pineapple Smoothie 16oz",4,2,"692","23/05/2026",15),
    ("CAESAR SALAD",4,3,"673","29/05/2026",9),
    ("HONEY TOPPING",3,3,"70","27/05/2026",11),
    ("MANGO TOPPING",3,3,"70","27/05/2026",11),
]
se3_dorm = [
    ("HOT CHOCOLATE 8 oz",22,6,"2,673","29/05/2026",9),
    ("Mango Sticky Rice\xa0(Box)",19,8,"3,179","31/05/2026",7),
    ("Golden Harmony Greek Yogur",17,8,"3,003","31/05/2026",7),
    ("MANGO PINEAPPLE SMOOTHIE 16OZ",17,9,"2,939","31/05/2026",7),
    ("BANANA YOGHURT SMOOTHIE 16OZ",9,7,"1,472","28/05/2026",10),
    ("MANGO BERRY SMOOTHIE 16OZ",8,5,"1,383","19/05/2026",19),
    ("T2 ICED THAI TEA WITH LIME 22OZ",7,7,"1,145","28/05/2026",10),
    ("Overnight Oat Berry 16 oz",7,5,"1,694","27/05/2026",11),
    ("CI4 ICED CAPPUCCINO 22OZ",6,5,"1,093","30/05/2026",8),
]
pkt_dorm = [
    ("CH3 Espresso (hot) 4oz",14,10,"1,626","31/05/2026",7),
    ("Orange Cold Pressed Juice 300ml (bottle)",11,8,"1,902","27/05/2026",11),
    ("Mango Pineapple Smoothie 16oz",10,8,"1,729","28/05/2026",10),
    ("Chicken Ham Wrap",6,6,"1,570","31/05/2026",7),
    ("Mango Sticky Rice\xa0(Box)",5,5,"1,168","25/05/2026",13),
    ("Ebiko salad Japanese Rice Balls (Onigiri)",5,4,"509","30/05/2026",8),
]

def build_dorm_html(rows):
    return "".join(dorm_row(m,q,d,r,ls,g) for (m,q,d,r,ls,g) in rows)

dormant_branches = [
    {"branch":"MW1","header_color":"#5551FE","branch_count":str(len(mw1_dorm)),
     "dormant_rows_html": build_dorm_html(mw1_dorm)},
    {"branch":"SE3","header_color":"#F27061","branch_count":str(len(se3_dorm)),
     "dormant_rows_html": build_dorm_html(se3_dorm)},
    {"branch":"PKT","header_color":"#2E7D32","branch_count":str(len(pkt_dorm)),
     "dormant_rows_html": build_dorm_html(pkt_dorm)},
]
dormant_count = len(mw1_dorm)+len(se3_dorm)+len(pkt_dorm)

# ── New products (Section 4) ──────────────────────────────────────────────────
def np_row_html(memo, launch, notes, total_units, total_rev, branch_split, yest_units, status_badge, odd):
    bg = "#fff" if odd else "#FAFAFA"
    return (f'<tr style="border-bottom:1px solid #eee;background:{bg};">'
            f'<td style="padding:6px 8px;">'
            f'<div style="font-weight:600;">{memo}</div>'
            f'<div style="font-size:9px;color:#888;">Launched {launch} · {notes}</div></td>'
            f'<td style="padding:6px 8px;text-align:right;">{total_units}u</td>'
            f'<td style="padding:6px 8px;text-align:right;">฿{total_rev}</td>'
            f'<td style="padding:6px 8px;font-size:10px;color:#666;">{branch_split}</td>'
            f'<td style="padding:6px 8px;text-align:right;">{yest_units}u</td>'
            f'<td style="padding:6px 8px;font-size:10px;">{status_badge}</td>'
            f'</tr>')

drinks_rows = [
    ("SOFT-SLUSH! ORIGINAL","02/05","MW1 exclusive",46,"6,878","MW1",1,"🟢 on target"),
    ("SOFT-SLUSH! DELUXE","01/05","MW1 exclusive",33,"7,379","MW1",1,"🟢 on target"),
    ("PRIDE PARROT RED","01/06","All branches",63,"11,757","MW1:44 SE3:13 PKT:6",11,"🟢 on target"),
    ("PRIDE PARROT YELLOW","01/06","All branches",33,"6,169","MW1:27 SE3:5 PKT:1",5,"🟢 on target"),
    ("Overnight Oat mango 16 oz","21/05","MW1+SE3",32,"8,045","MW1:27 SE3:5",0,"🟠 stock-out suspect"),
    ("Overnight Oat Berry 16 oz","22/05","SE3",8,"1,936","SE3",0,"🔴 waste risk"),
]
fruit_rows = [
    ("LYCHEE 400G.","28/05","MW1+SE3",15,"2,384","MW1:4 SE3:11",0,"🟠 stock-out suspect"),
    ("MANGOSTEEN 400g.","28/05","SE3 only",3,"701","SE3",0,"🔴 waste risk"),
    ("ROSE APPLE 400G.","30/05","SE3 only",3,"449","SE3",0,"🔴 waste risk"),
]
newcat_rows = [
    ("BLUEBERRY GREEK YOGURT","13/05","MW1 only",12,"2,120","MW1",0,"🟠 stock-out suspect"),
    ("RASPBERRY GREEK YOGURT","13/05","MW1 only",9,"1,590","MW1",0,"🔴 waste risk"),
    ("VANILLA BEAN GREEK YOGURT","13/05","MW1 only",14,"2,473","MW1",0,"🔴 waste risk"),
]

def build_np_html(rows):
    return "".join(np_row_html(m,l,n,u,r,b,y,s,i%2==0) for i,(m,l,n,u,r,b,y,s) in enumerate(rows))

np_type_tables = [
    {"type_bg":"#E3F2FD","type_fg":"#1976D2","type_icon":"🥤","type_label":"New Drinks & Smoothies",
     "np_rows_html": build_np_html(drinks_rows)},
    {"type_bg":"#FCE4EC","type_fg":"#AD1457","type_icon":"🍉","type_label":"Seasonal Fruits",
     "np_rows_html": build_np_html(fruit_rows)},
    {"type_bg":"#E8F5E9","type_fg":"#2E7D32","type_icon":"⭐","type_label":"New Category (Greek Yogurt)",
     "np_rows_html": build_np_html(newcat_rows)},
]

drinks_yest_rev = 149.53+224.3+747.68+1121.52+186.92+560.76+186.91+186.91

# ── Seasonal tracker ──────────────────────────────────────────────────────────
# Baselines: MW1 ฿339/d, SE3 ฿251/d
# New fruit:
#   MW1: LYCHEE 4u, ฿636, first 28/05 → days since launch = 11 → 636/11 = 57.8
#   SE3: LYCHEE 11u/฿1,748 (10d) + MANGOSTEEN 3u/฿701 (11d) + ROSE APPLE 3u/฿449 (9d)
#        = 174.8 + 63.7 + 49.9 = 288.4/d
mw1_new_fruit_per_day = 57.8
se3_new_fruit_per_day = 288.4
mw1_coverage = round(mw1_new_fruit_per_day / 339 * 100)   # 17%
se3_coverage = round(se3_new_fruit_per_day / 251 * 100)   # 115%

def coverage_style(pct):
    if pct >= 100: return ("#155724","#D4EDDA","✅ Fully replaced")
    if pct >= 70:  return ("#856404","#FFF3CD","🟡 Partial — monitor")
    return ("#721C24","#F8D7DA","🔴 Large gap — push promotion or add SKU")

mw1_cc, mw1_bg, mw1_badge = coverage_style(mw1_coverage)
se3_cc, se3_bg, se3_badge = coverage_style(se3_coverage)

seasonal_skus = [
    {"fruit_emoji":"🍊","memo":"LYCHEE 400G.","launch":"28/05/2026",
     "mw1_units":"4","mw1_per_day":"58","se3_units":"11","se3_per_day":"175"},
    {"fruit_emoji":"🟣","memo":"MANGOSTEEN 400g.","launch":"28/05/2026",
     "mw1_units":"0","mw1_per_day":"0","se3_units":"3","se3_per_day":"64"},
    {"fruit_emoji":"🌹","memo":"ROSE APPLE 400G.","launch":"30/05/2026",
     "mw1_units":"0","mw1_per_day":"0","se3_units":"3","se3_per_day":"50"},
]
seasonal_coverage = [
    {"branch_label":"MW1 · Suvarnabhumi","branch_color":"#5551FE",
     "grape_baseline":"339","new_fruit_per_day":fmt(mw1_new_fruit_per_day),
     "coverage_pct":str(mw1_coverage),
     "daily_gap":f"฿{fmt(339 - mw1_new_fruit_per_day)}/d shortfall",
     "monthly_impact":f"฿{fmt((339 - mw1_new_fruit_per_day)*30)}/mo shortfall",
     "coverage_color":mw1_cc,"badge_bg":mw1_bg,"badge_text":mw1_badge},
    {"branch_label":"SE3 · Suvarnabhumi","branch_color":"#F27061",
     "grape_baseline":"251","new_fruit_per_day":fmt(se3_new_fruit_per_day),
     "coverage_pct":str(se3_coverage),
     "daily_gap":f"+฿{fmt(se3_new_fruit_per_day - 251)}/d surplus",
     "monthly_impact":f"+฿{fmt((se3_new_fruit_per_day - 251)*30)}/mo",
     "coverage_color":se3_cc,"badge_bg":se3_bg,"badge_text":se3_badge},
]

# ── Grape baseline totals ─────────────────────────────────────────────────────
grape_total_rev = 133186.69 + 105553.37  # 238,740

# ── np totals ─────────────────────────────────────────────────────────────────
drinks_tu = sum(r[3] for r in drinks_rows)
drinks_tr = sum(int(r[4].replace(",","")) for r in drinks_rows)
fruit_tu  = sum(r[3] for r in fruit_rows)
fruit_tr  = sum(int(r[4].replace(",","")) for r in fruit_rows)
ncat_tu   = sum(r[3] for r in newcat_rows)
ncat_tr   = sum(int(r[4].replace(",","")) for r in newcat_rows)

# ── Assemble data.json ────────────────────────────────────────────────────────
data = {
    "scalars": {
        "report_date": report_date,
        "report_date_display": report_date_display,
        "report_day_th": report_day_th,
        "window_30d_start": window_30d_start_disp,
        "generated_timestamp": generated_timestamp,
        "subject_prefix": subject_prefix,
        "comb_net": fmt(yest_comb),
        "signed_pct": ("+"+str(signed_pct) if signed_pct > 0 else str(signed_pct)),
        "mw1_net": fmt(yest_mw1),
        "se3_net": fmt(yest_se3),
        "pkt_net": fmt(yest_pkt),
        "mw1_vs_30d": ("+"+str(mw1_vs_30d) if mw1_vs_30d > 0 else str(mw1_vs_30d)),
        "se3_vs_30d": ("+"+str(se3_vs_30d) if se3_vs_30d > 0 else str(se3_vs_30d)),
        "pkt_vs_30d": ("+"+str(pkt_vs_30d) if pkt_vs_30d > 0 else str(pkt_vs_30d)),
        "mw1_avg_30d": fmt(mw1_avg),
        "mw1_min_30d": fmt(min(mw1_vals)),
        "mw1_max_30d": fmt(max(mw1_vals)),
        "se3_avg_30d": fmt(se3_avg),
        "se3_min_30d": fmt(min(se3_vals)),
        "se3_max_30d": fmt(max(se3_vals)),
        "pkt_avg_30d": fmt(pkt_avg),
        "pkt_min_30d": fmt(min(pkt_vals)),
        "pkt_max_30d": fmt(max(pkt_vals)),
        "comb_avg_30d": fmt(comb_avg),
        "comb_monthly_runrate": f"{comb_runrate_k:,.1f}K",
        "last7_total": fmt(comb_7d),
        "last7_avg": fmt(comb_7d/7),
        "mw1_7d_total": fmt(mw1_7d),
        "se3_7d_total": fmt(se3_7d),
        "pkt_7d_total": fmt(pkt_7d),
        "comb_7d_total": fmt(comb_7d),
        "am_queue_count": str(am_queue_count),
        "dormant_count": str(dormant_count),
        "np_total_units": str(drinks_tu+fruit_tu+ncat_tu),
        "np_total_rev": fmt(drinks_tr+fruit_tr+ncat_tr),
        "np_summary_line": f"6 drink + 3 seasonal-fruit + 3 new-category SKUs launched since May 2026",
        "drinks_n": "6",
        "drinks_todate_units": str(drinks_tu),
        "drinks_todate_rev": fmt(drinks_tr),
        "drinks_yest": str(sum(r[6] for r in drinks_rows)),
        "drinks_yest_rev": fmt(drinks_yest_rev),
        "fruit_n": "3",
        "fruit_todate_units": str(fruit_tu),
        "fruit_todate_rev": fmt(fruit_tr),
        "fruit_yest": "0",
        "fruit_yest_rev": "0",
        "new_cat_n": "3",
        "new_cat_todate_units": str(ncat_tu),
        "new_cat_todate_rev": fmt(ncat_tr),
        "new_cat_yest": "0",
        "new_cat_yest_rev": "0",
        "grape_total_rev": fmt(grape_total_rev),
        "grape_last_mw1": "21 May 2026",
        "grape_last_se3": "28 Apr 2026",
        "chaw_values": "Curious · Team · Act Fast · Empowered · Simple",
    },
    "repeats": {
        "chart_days": chart_days,
        "last7_headers": last7_headers,
        "last7_mw1": last7_mw1,
        "last7_se3": last7_se3,
        "last7_pkt": last7_pkt,
        "last7_comb": last7_comb,
        "am_items": am_items,
        "top20_branches": top20_branches,
        "dormant_branches": dormant_branches,
        "np_type_tables": np_type_tables,
        "seasonal_skus": seasonal_skus,
        "seasonal_coverage": seasonal_coverage,
    },
    "sections": {
        "am_review": True,
        "seasonal": True,
        "dormant": True,
        "forecast_shown": False,
        "forecast_suppressed": True,
        "anomaly_shown": False,
    }
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("data.json written.")
