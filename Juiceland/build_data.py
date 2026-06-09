#!/usr/bin/env python3
"""
build_data.py — processes NetSuite query results and writes data.json.
Also patches the template to replace nested REPEAT blocks with {{token}} placeholders.
Run once before fill_template.py.
"""
import json, re, math

# ── REPORT DATE (hardcoded for this run) ──────────────────────────────────────
REPORT_DATE = "2026-06-08"
REPORT_DATE_DISPLAY = "8 June 2026"
REPORT_DAY_TH = "วันจันทร์"
WINDOW_30D_START = "2026-05-10"
GENERATED_TIMESTAMP = "2026-06-09 07:00"

# ── QUERY A RESULTS ───────────────────────────────────────────────────────────
# Roll loc 169 → MW1 (loc 33). No 169 rows in this run.
query_a_raw = [
 {"trandate":"10/05/2026","location":"33","net_sales":36901},
 {"trandate":"10/05/2026","location":"105","net_sales":26350},
 {"trandate":"10/05/2026","location":"109","net_sales":10994},
 {"trandate":"11/05/2026","location":"33","net_sales":33927.5},
 {"trandate":"11/05/2026","location":"105","net_sales":25400},
 {"trandate":"11/05/2026","location":"109","net_sales":9884},
 {"trandate":"12/05/2026","location":"33","net_sales":31386},
 {"trandate":"12/05/2026","location":"105","net_sales":18990},
 {"trandate":"12/05/2026","location":"109","net_sales":11704},
 {"trandate":"13/05/2026","location":"33","net_sales":34122},
 {"trandate":"13/05/2026","location":"105","net_sales":25085},
 {"trandate":"13/05/2026","location":"109","net_sales":13897},
 {"trandate":"14/05/2026","location":"33","net_sales":40908},
 {"trandate":"14/05/2026","location":"105","net_sales":21800},
 {"trandate":"14/05/2026","location":"109","net_sales":7820},
 {"trandate":"15/05/2026","location":"33","net_sales":35787},
 {"trandate":"15/05/2026","location":"105","net_sales":19010},
 {"trandate":"15/05/2026","location":"109","net_sales":10244},
 {"trandate":"16/05/2026","location":"33","net_sales":30765.5},
 {"trandate":"16/05/2026","location":"105","net_sales":25470},
 {"trandate":"16/05/2026","location":"109","net_sales":9920},
 {"trandate":"17/05/2026","location":"33","net_sales":34754},
 {"trandate":"17/05/2026","location":"105","net_sales":35410},
 {"trandate":"17/05/2026","location":"109","net_sales":13484},
 {"trandate":"18/05/2026","location":"33","net_sales":25913},
 {"trandate":"18/05/2026","location":"105","net_sales":22700},
 {"trandate":"18/05/2026","location":"109","net_sales":12484},
 {"trandate":"19/05/2026","location":"33","net_sales":33034.5},
 {"trandate":"19/05/2026","location":"105","net_sales":25820},
 {"trandate":"19/05/2026","location":"109","net_sales":7867},
 {"trandate":"20/05/2026","location":"33","net_sales":31093},
 {"trandate":"20/05/2026","location":"105","net_sales":17307.5},
 {"trandate":"20/05/2026","location":"109","net_sales":10311},
 {"trandate":"21/05/2026","location":"33","net_sales":36940.5},
 {"trandate":"21/05/2026","location":"105","net_sales":29297},
 {"trandate":"21/05/2026","location":"109","net_sales":9611},
 {"trandate":"22/05/2026","location":"33","net_sales":40088},
 {"trandate":"22/05/2026","location":"105","net_sales":26689},
 {"trandate":"22/05/2026","location":"109","net_sales":10358},
 {"trandate":"23/05/2026","location":"33","net_sales":38639.5},
 {"trandate":"23/05/2026","location":"105","net_sales":39492},
 {"trandate":"23/05/2026","location":"109","net_sales":12698},
 {"trandate":"24/05/2026","location":"33","net_sales":45429.5},
 {"trandate":"24/05/2026","location":"105","net_sales":28328},
 {"trandate":"24/05/2026","location":"109","net_sales":12933},
 {"trandate":"25/05/2026","location":"33","net_sales":38221},
 {"trandate":"25/05/2026","location":"105","net_sales":31983.5},
 {"trandate":"25/05/2026","location":"109","net_sales":10502},
 {"trandate":"26/05/2026","location":"33","net_sales":36852.5},
 {"trandate":"26/05/2026","location":"105","net_sales":24575.5},
 {"trandate":"26/05/2026","location":"109","net_sales":7039},
 {"trandate":"27/05/2026","location":"33","net_sales":33877},
 {"trandate":"27/05/2026","location":"105","net_sales":26502},
 {"trandate":"27/05/2026","location":"109","net_sales":16234},
 {"trandate":"28/05/2026","location":"33","net_sales":33415},
 {"trandate":"28/05/2026","location":"105","net_sales":31121},
 {"trandate":"28/05/2026","location":"109","net_sales":12474},
 {"trandate":"29/05/2026","location":"33","net_sales":42210.5},
 {"trandate":"29/05/2026","location":"105","net_sales":22568},
 {"trandate":"29/05/2026","location":"109","net_sales":13844},
 {"trandate":"30/05/2026","location":"33","net_sales":34788},
 {"trandate":"30/05/2026","location":"105","net_sales":26883},
 {"trandate":"30/05/2026","location":"109","net_sales":14605},
 {"trandate":"31/05/2026","location":"33","net_sales":28583},
 {"trandate":"31/05/2026","location":"105","net_sales":32544},
 {"trandate":"31/05/2026","location":"109","net_sales":14052},
 {"trandate":"01/06/2026","location":"33","net_sales":32133},
 {"trandate":"01/06/2026","location":"105","net_sales":24075},
 {"trandate":"01/06/2026","location":"109","net_sales":13940},
 {"trandate":"02/06/2026","location":"33","net_sales":36476},
 {"trandate":"02/06/2026","location":"105","net_sales":15959},
 {"trandate":"02/06/2026","location":"109","net_sales":9920},
 {"trandate":"03/06/2026","location":"33","net_sales":40024},
 {"trandate":"03/06/2026","location":"105","net_sales":19497},
 {"trandate":"03/06/2026","location":"109","net_sales":10813},
 {"trandate":"04/06/2026","location":"33","net_sales":35666.5},
 {"trandate":"04/06/2026","location":"105","net_sales":16604},
 {"trandate":"04/06/2026","location":"109","net_sales":13146},
 {"trandate":"05/06/2026","location":"33","net_sales":35611},
 {"trandate":"05/06/2026","location":"105","net_sales":20180},
 {"trandate":"05/06/2026","location":"109","net_sales":13589},
 {"trandate":"06/06/2026","location":"33","net_sales":32714},
 {"trandate":"06/06/2026","location":"105","net_sales":23312},
 {"trandate":"06/06/2026","location":"109","net_sales":13867},
 {"trandate":"07/06/2026","location":"33","net_sales":25977},
 {"trandate":"07/06/2026","location":"105","net_sales":17749},
 {"trandate":"07/06/2026","location":"109","net_sales":12993},
 {"trandate":"08/06/2026","location":"33","net_sales":38857},
 {"trandate":"08/06/2026","location":"105","net_sales":24570},
 {"trandate":"08/06/2026","location":"109","net_sales":12810},
]

# ── QUERY B RESULTS (yesterday top items per branch) ─────────────────────────
query_b_raw = {
 "33": [
  {"memo":"EVIAN","qty":50,"revenue":5607.5,"bills":4},
  {"memo":"PRIDE PARROT RED","qty":11,"revenue":2056.11,"bills":4},
  {"memo":"PRIDE PARROT YELLOW","qty":11,"revenue":2037.39,"bills":4},
  {"memo":"COCONUT READY TO DRINK","qty":9,"revenue":1429.92,"bills":2},
  {"memo":"WATERMELON 400G.","qty":8,"revenue":1121.51,"bills":2},
  {"memo":"P1 GOLDEN GLOW 22OZ","qty":7,"revenue":1471.96,"bills":2},
  {"memo":"S4 MIXBERRY SMOOTHIE 16OZ","qty":7,"revenue":1046.72,"bills":2},
  {"memo":"MANGO 400G.","qty":6,"revenue":897.18,"bills":3},
  {"memo":"CI3 ICED AMERICANO 22OZ","qty":6,"revenue":1009.33,"bills":2},
  {"memo":"CARROT JUICE BOTTLE","qty":6,"revenue":1037.38,"bills":2},
  {"memo":"S1 COCONUT SMOOTHIE 22OZ","qty":6,"revenue":1149.54,"bills":3},
  {"memo":"S3 WATERMELON SMOOTHIE 22OZ","qty":6,"revenue":1037.4,"bills":2},
  {"memo":"C3 WATERMELON  COLD PREESED 22OZ","qty":5,"revenue":981.3,"bills":4},
  {"memo":"S2 MANGO PASSION SMOOTHIE 22OZ","qty":5,"revenue":864.5,"bills":3},
  {"memo":"WATERMELON JUICE BOTTLE","qty":5,"revenue":864.49,"bills":3},
  {"memo":"COCONUT JUICE BOTTLE","qty":5,"revenue":864.49,"bills":2},
  {"memo":"S5 MANGO SMOOTHIE 22OZ","qty":5,"revenue":864.5,"bills":3},
  {"memo":"S3 WATERMELON SMOOTHIE 16OZ","qty":5,"revenue":747.65,"bills":3},
  {"memo":"PINEAPPLE JUICE BOTTLE","qty":4,"revenue":691.6,"bills":2},
  {"memo":"C4 MANGO PASSION  COLD PREESED 16OZ","qty":3,"revenue":518.7,"bills":2},
 ],
 "105": [
  {"memo":"EVIAN","qty":30,"revenue":3364.5,"bills":3},
  {"memo":"WATERMELON 400G.","qty":11,"revenue":1542.07,"bills":3},
  {"memo":"MANGO 400G.","qty":10,"revenue":1495.3,"bills":2},
  {"memo":"COCONUT READY TO DRINK","qty":8,"revenue":1271.04,"bills":2},
  {"memo":"P1 GOLDEN GLOW 16OZ","qty":6,"revenue":1121.51,"bills":2},
  {"memo":"MANGO (1 PCS.) 380 G.","qty":6,"revenue":841.13,"bills":2},
  {"memo":"PAPAYA 400G.","qty":6,"revenue":841.13,"bills":3},
  {"memo":"PINEAPPLE 400G.","qty":5,"revenue":700.95,"bills":2},
  {"memo":"3 kinds of fruit400g Papaya/Pineapple/Guava","qty":5,"revenue":700.95,"bills":3},
  {"memo":"PRIDE PARROT RED","qty":5,"revenue":934.59,"bills":2},
  {"memo":"SEEDLESS GRAPE 400G.","qty":4,"revenue":598.12,"bills":2},
  {"memo":"P2 GREEN BOOST 22OZ","qty":3,"revenue":630.84,"bills":2},
  {"memo":"P1 GOLDEN GLOW 22OZ","qty":3,"revenue":630.84,"bills":1},
  {"memo":"S1 COCONUT SMOOTHIE 22OZ","qty":3,"revenue":574.77,"bills":2},
  {"memo":"S2 MANGO PASSION SMOOTHIE 22OZ","qty":3,"revenue":518.69,"bills":1},
  {"memo":"MAEVAREE MANGO YOGHURT STICKY RICE SMOTHIE 22OZ","qty":2,"revenue":429.9,"bills":2},
  {"memo":"C5 PINEAPPLE&GREEN APPLE  COLD PREESED 22OZ","qty":2,"revenue":392.52,"bills":2},
  {"memo":"C2 ORANGE  COLD PREESED 22OZ","qty":2,"revenue":392.52,"bills":1},
  {"memo":"S2 MANGO PASSION SMOOTHIE 16OZ","qty":2,"revenue":299.06,"bills":2},
  {"memo":"C4 MANGO PASSION  COLD PREESED 22OZ","qty":2,"revenue":392.53,"bills":2},
 ],
 "109": [
  {"memo":"Evian 500ml. (Bottle)","qty":17,"revenue":1906.54,"bills":2},
  {"memo":"Mango 400 g. (Pack)","qty":9,"revenue":1323.13,"bills":2},
  {"memo":"CH1 Cappuccino (hot) 12oz","qty":9,"revenue":1240.44,"bills":3},
  {"memo":"Watermelon 400 g. (Pack)","qty":5,"revenue":700.95,"bills":1},
  {"memo":"Pineapple 400 g. (Pack)","qty":4,"revenue":560.75,"bills":2},
  {"memo":"Butter Croissant","qty":4,"revenue":345.52,"bills":2},
  {"memo":"Coconut (EA)","qty":4,"revenue":635.51,"bills":2},
  {"memo":"CH4 Americano (hot) 12oz","qty":4,"revenue":504.68,"bills":2},
  {"memo":"Singha Beer 320 ml. (Bottle)","qty":3,"revenue":504.66,"bills":1},
  {"memo":"Ebiko salad Japanese Rice Balls (Onigiri)","qty":3,"revenue":305.61,"bills":1},
  {"memo":"S5 mango smoothie  16oz","qty":3,"revenue":448.6,"bills":2},
  {"memo":"CI5 Iced Latte 16oz","qty":2,"revenue":317.76,"bills":1},
  {"memo":"Guava 400 g. (Pack)","qty":2,"revenue":280.38,"bills":2},
  {"memo":"CH2 Caffe latte (hot) 12oz","qty":2,"revenue":238.51,"bills":2},
  {"memo":"Chang Lager Beer Bottle 320ml","qty":2,"revenue":334.58,"bills":1},
  {"memo":"CH3 Espresso (hot) 4oz","qty":2,"revenue":233.64,"bills":1},
  {"memo":"Hot water 12oz","qty":2,"revenue":56.08,"bills":1},
  {"memo":"Ham and Cheese Croissant","qty":2,"revenue":294.51,"bills":2},
  {"memo":"Up size Smoothie & Cold Press Juice 16 oz. to 22 oz .","qty":2,"revenue":46.72,"bills":2},
  {"memo":"3 kinds of fruit (400 g.) Papaya 150 g. / Pineapple 150 g. / Guava 100 g.)","qty":1,"revenue":140.19,"bills":1},
 ]
}

# ── QUERY D RESULTS (dormant SKUs — pre-filtered: qty_30d >= 3, no \n memos) ──
# gap_days computed from report_date 2026-06-08
DORMANT = {
 "33": [
  {"memo":"SHINE MUSCAT GRAPES 400G (PACK)","qty_30d":31,"days_sold_30d":12,"rev_30d":4635.45,"gap_days":18},
  {"memo":"HOT CHOCOLATE 8 oz","qty_30d":18,"days_sold_30d":4,"rev_30d":2186.96,"gap_days":12},
  {"memo":"Up size Smoothie & Cold Press","qty_30d":17,"days_sold_30d":8,"rev_30d":397.12,"gap_days":7},
  {"memo":"VANILLA BEAN GREEK YOGURT","qty_30d":14,"days_sold_30d":11,"rev_30d":2472.91,"gap_days":13},
  {"memo":"T2 ICED THAI TEA WITH LIME 16OZ","qty_30d":9,"days_sold_30d":7,"rev_30d":1261.69,"gap_days":7},
  {"memo":"RASPBERRY GREEK YOGURT","qty_30d":9,"days_sold_30d":7,"rev_30d":1589.7,"gap_days":17},
  {"memo":"SEEDLESS GRAPE 400G.","qty_30d":6,"days_sold_30d":4,"rev_30d":897.18,"gap_days":13},
  {"memo":"Mango Berry Smoothie 16oz","qty_30d":5,"days_sold_30d":4,"rev_30d":864.5,"gap_days":13},
  {"memo":"CAESAR SALAD","qty_30d":4,"days_sold_30d":3,"rev_30d":672.88,"gap_days":10},
  {"memo":"Mango Pineapple Smoothie 16oz","qty_30d":4,"days_sold_30d":2,"rev_30d":691.59,"gap_days":16},
  {"memo":"MANGO TOPPING","qty_30d":3,"days_sold_30d":3,"rev_30d":70.08,"gap_days":12},
  {"memo":"CI1 ICED ESPRESSO ORANGE 16OZ","qty_30d":3,"days_sold_30d":3,"rev_30d":560.76,"gap_days":16},
  {"memo":"Mango Sticky Rice (Box)","qty_30d":3,"days_sold_30d":3,"rev_30d":501.85,"gap_days":7},
  {"memo":"HONEY TOPPING","qty_30d":3,"days_sold_30d":3,"rev_30d":70.08,"gap_days":12},
 ],
 "105": [
  {"memo":"Up size Smoothie & Cold Press","qty_30d":30,"days_sold_30d":17,"rev_30d":700.8,"gap_days":7},
  {"memo":"HOT CHOCOLATE 8 oz","qty_30d":22,"days_sold_30d":6,"rev_30d":2672.98,"gap_days":10},
  {"memo":"Mango Sticky Rice (Box)","qty_30d":19,"days_sold_30d":8,"rev_30d":3178.51,"gap_days":8},
  {"memo":"Golden Harmony Greek Yogur","qty_30d":17,"days_sold_30d":8,"rev_30d":3002.81,"gap_days":8},
  {"memo":"MANGO PINEAPPLE SMOOTHIE 16OZ","qty_30d":17,"days_sold_30d":9,"rev_30d":2939.3,"gap_days":8},
  {"memo":"MANGO BERRY SMOOTHIE 16OZ","qty_30d":8,"days_sold_30d":5,"rev_30d":1383.2,"gap_days":20},
  {"memo":"BANANA YOGHURT SMOOTHIE 16OZ","qty_30d":7,"days_sold_30d":6,"rev_30d":1144.85,"gap_days":11},
  {"memo":"T2 ICED THAI TEA WITH LIME 22OZ","qty_30d":7,"days_sold_30d":7,"rev_30d":1144.85,"gap_days":11},
  {"memo":"Overnight Oat Berry 16 oz","qty_30d":7,"days_sold_30d":5,"rev_30d":1694.4,"gap_days":12},
  {"memo":"CI4 ICED CAPPUCCINO 22OZ","qty_30d":6,"days_sold_30d":5,"rev_30d":1093.43,"gap_days":9},
  {"memo":"MANGOSTEEN 400g.","qty_30d":3,"days_sold_30d":3,"rev_30d":700.92,"gap_days":7},
  {"memo":"ROSE APPLE 400G.","qty_30d":3,"days_sold_30d":3,"rev_30d":448.59,"gap_days":7},
 ],
 "109": [
  {"memo":"Mango Pineapple Smoothie 16oz","qty_30d":10,"days_sold_30d":8,"rev_30d":1729.03,"gap_days":11},
  {"memo":"Orange Cold Pressed Juice 300 ml. (bottle)","qty_30d":8,"days_sold_30d":7,"rev_30d":1383.18,"gap_days":12},
  {"memo":"Chicken Ham Wrap","qty_30d":6,"days_sold_30d":6,"rev_30d":1570.08,"gap_days":8},
  {"memo":"Mango Sticky Rice (Box)","qty_30d":4,"days_sold_30d":4,"rev_30d":934.57,"gap_days":14},
  {"memo":"T2 Iced Thai tea with lime 16oz","qty_30d":3,"days_sold_30d":2,"rev_30d":420.57,"gap_days":7},
 ]
}

# ── HELPERS ───────────────────────────────────────────────────────────────────
def fmt(n):
    """Format number: comma-thousands, no decimals."""
    return f"{round(n):,}"

def trunc(s, n=34):
    return (s[:n] + "…") if len(s) > n else s

def gap_color(days):
    return "#C62828" if days >= 14 else "#E65100"

# ── PROCESS QUERY A ───────────────────────────────────────────────────────────
# Build {date: {loc: net_sales}}
from collections import defaultdict
by_date = defaultdict(dict)
for r in query_a_raw:
    loc = "33" if r["location"] in ("33","169") else r["location"]
    d = r["trandate"]
    by_date[d][loc] = by_date[d].get(loc, 0) + r["net_sales"]

# Sort dates
def parse_dd_mm_yyyy(s):
    d, m, y = s.split("/")
    return (int(y), int(m), int(d))

sorted_dates = sorted(by_date.keys(), key=parse_dd_mm_yyyy)

# Helpers
def get_net(date, loc):
    return by_date.get(date, {}).get(loc, 0)

def get_comb(date):
    return sum(by_date.get(date, {}).get(l, 0) for l in ["33","105","109"])

all_mw1 = [get_net(d,"33") for d in sorted_dates]
all_se3 = [get_net(d,"105") for d in sorted_dates]
all_pkt = [get_net(d,"109") for d in sorted_dates]
all_comb = [get_comb(d) for d in sorted_dates]

mw1_avg = sum(all_mw1) / 30
se3_avg = sum(all_se3) / 30
pkt_avg = sum(all_pkt) / 30
comb_avg = sum(all_comb) / 30

yesterday_mw1 = get_net("08/06/2026","33")
yesterday_se3 = get_net("08/06/2026","105")
yesterday_pkt = get_net("08/06/2026","109")
yesterday_comb = yesterday_mw1 + yesterday_se3 + yesterday_pkt

signed_pct_val = (yesterday_comb / comb_avg - 1) * 100
mw1_vs = (yesterday_mw1 / mw1_avg - 1) * 100
se3_vs = (yesterday_se3 / se3_avg - 1) * 100
pkt_vs = (yesterday_pkt / pkt_avg - 1) * 100

signed_pct = ("+{:.1f}" if signed_pct_val >= 0 else "{:.1f}").format(signed_pct_val)
mw1_vs_30d = ("+{:.1f}" if mw1_vs >= 0 else "{:.1f}").format(mw1_vs)
se3_vs_30d = ("+{:.1f}" if se3_vs >= 0 else "{:.1f}").format(se3_vs)
pkt_vs_30d = ("+{:.1f}" if pkt_vs >= 0 else "{:.1f}").format(pkt_vs)

subject_prefix = "✅" if -10 <= signed_pct_val <= 10 else ("🔥" if signed_pct_val > 10 else "⚠️")

chart_max = max(max(all_mw1), max(all_se3), max(all_pkt))

# Thai weekday abbreviations (Sun=อา Mon=จ Tue=อ Wed=พ Thu=พฤ Fri=ศ Sat=ส)
# 08/06/2026 = Monday → weekday index Mon=0 for our purposes
# Python: weekday() Mon=0 Sun=6; isoweekday() Mon=1 Sun=7
from datetime import date, timedelta
TH_ABBR = {0:"จ",1:"อ",2:"พ",3:"พฤ",4:"ศ",5:"ส",6:"อา"}

def parse_date(s):
    d, m, y = s.split("/")
    return date(int(y), int(m), int(d))

# ── CHART DAYS REPEAT ────────────────────────────────────────────────────────
chart_days = []
for i, ds in enumerate(sorted_dates):
    dt = parse_date(ds)
    mw1_v = get_net(ds,"33")
    se3_v = get_net(ds,"105")
    pkt_v = get_net(ds,"109")
    chart_days.append({
        "date": dt.strftime("%-d %b"),
        "day_num": str(dt.day),
        "weekday_th_abbr": TH_ABBR[dt.weekday()],
        "mw1_net": fmt(mw1_v),
        "se3_net": fmt(se3_v),
        "pkt_net": fmt(pkt_v),
        "mw1_bar_px": str(round(mw1_v / chart_max * 220)),
        "se3_bar_px": str(round(se3_v / chart_max * 220)),
        "pkt_bar_px": str(round(pkt_v / chart_max * 220)),
    })

# ── LAST 7 ────────────────────────────────────────────────────────────────────
last7_dates = sorted_dates[-7:]  # 02/06 … 08/06

last7_headers = []
for ds in last7_dates:
    dt = parse_date(ds)
    is_yest = ds == "08/06/2026"
    last7_headers.append({
        "col_date": dt.strftime("%-d %b"),
        "col_weekday_th": TH_ABBR[dt.weekday()],
        "header_bg": "background:#4744CD;" if is_yest else "",
    })

def last7_cells(loc_key):
    cells = []
    for ds in last7_dates:
        v = get_net(ds, loc_key) if loc_key != "comb" else get_comb(ds)
        is_yest = ds == "08/06/2026"
        cells.append({
            "net": fmt(v),
            "cell_style": "background:#FFF3E0;font-weight:700;" if is_yest else "",
            "cell_bg": "background:#FFF3E0;" if is_yest else "",
        })
    return cells

last7_mw1 = last7_cells("33")
last7_se3 = last7_cells("105")
last7_pkt = last7_cells("109")
last7_comb = last7_cells("comb")

mw1_7d_total = fmt(sum(get_net(d,"33") for d in last7_dates))
se3_7d_total = fmt(sum(get_net(d,"105") for d in last7_dates))
pkt_7d_total = fmt(sum(get_net(d,"109") for d in last7_dates))
comb_7d_total = fmt(sum(get_comb(d) for d in last7_dates))
last7_total = fmt(sum(get_comb(d) for d in last7_dates))
last7_avg = fmt(sum(get_comb(d) for d in last7_dates) / 7)

# ── TOP 20 BRANCHES — pre-render inner HTML ───────────────────────────────────
TOP20_ROW_TMPL = (
    '<tr style="background:{row_bg};">'
    '<td style="padding:5px 6px;border-bottom:1px solid #eee;vertical-align:top;font-size:10px;color:#888;">{rank}</td>'
    '<td style="padding:5px 6px;border-bottom:1px solid #eee;vertical-align:top;" title="{memo_full}">'
    '<div style="font-weight:600;font-size:10px;line-height:1.2;">{memo_display}</div>'
    '<div style="font-size:9px;color:#888;">{bills} bills</div></td>'
    '<td style="padding:5px 6px;text-align:right;border-bottom:1px solid #eee;vertical-align:top;font-size:10px;">{qty}</td>'
    '<td style="padding:5px 6px;text-align:right;border-bottom:1px solid #eee;vertical-align:top;font-size:10px;">฿{revenue}</td>'
    '</tr>'
)

BRANCH_META = [
    ("33",  "#5551FE", "MW1 · 26-T1MW1-03+04"),
    ("105", "#F27061", "SE3 · 27-T1SE3-05"),
    ("109", "#2E7D32", "PKT · 28 Unit 362 (Phuket)"),
]
BRANCH_NAMES = {"33":"MW1","105":"SE3","109":"PKT"}
BRANCH_COLORS = {"33":"#5551FE","105":"#F27061","109":"#2E7D32"}

def render_top20_rows(loc):
    rows = query_b_raw.get(loc, [])[:20]
    if not rows:
        return '<tr><td colspan="4" style="padding:8px;color:#888;">—</td></tr>'
    html = ""
    for i, r in enumerate(rows):
        row_bg = "#fff" if i % 2 == 0 else "#FAFAFA"
        memo = r["memo"].strip()
        html += TOP20_ROW_TMPL.format(
            row_bg=row_bg,
            rank=i+1,
            memo_full=memo.replace('"', '&quot;'),
            memo_display=trunc(memo),
            bills=r["bills"],
            qty=r["qty"],
            revenue=fmt(r["revenue"]),
        )
    return html

top20_branches = []
for loc, color, label in BRANCH_META:
    top20_branches.append({
        "header_color": color,
        "header_label": label,
        "top20_rows_html": render_top20_rows(loc),
    })

# ── DORMANT BRANCHES — pre-render inner HTML ──────────────────────────────────
DORMANT_ROW_TMPL = (
    '<tr style="background:#fff;border-bottom:1px solid #eee;">'
    '<td style="padding:5px 6px;vertical-align:top;" title="{memo_full}">'
    '<div style="font-weight:600;font-size:10px;line-height:1.2;">{memo_display}</div>'
    '<div style="font-size:9px;color:#888;margin-top:1px;">Was selling: {qty_30d}u over {days_sold_30d}d (฿{rev_30d})</div>'
    '</td>'
    '<td style="padding:5px 6px;text-align:right;vertical-align:top;color:{gap_color};font-weight:700;font-size:10px;">{gap_days}d</td>'
    '</tr>'
)

def render_dormant_rows(loc):
    rows = DORMANT.get(loc, [])
    if not rows:
        return '<tr><td colspan="2" style="padding:8px;color:#888;">—</td></tr>'
    html = ""
    for r in rows:
        memo = r["memo"].strip()
        html += DORMANT_ROW_TMPL.format(
            memo_full=memo.replace('"', '&quot;'),
            memo_display=trunc(memo),
            qty_30d=r["qty_30d"],
            days_sold_30d=r["days_sold_30d"],
            rev_30d=fmt(r["rev_30d"]),
            gap_color=gap_color(r["gap_days"]),
            gap_days=r["gap_days"],
        )
    return html

dormant_count = sum(len(v) for v in DORMANT.values())

dormant_branches = []
for loc, color, _ in BRANCH_META:
    dormant_branches.append({
        "header_color": color,
        "branch": BRANCH_NAMES[loc],
        "branch_count": len(DORMANT.get(loc, [])),
        "dormant_rows_html": render_dormant_rows(loc),
    })

# ── NEW PRODUCTS (Query C skipped — minimal placeholder) ─────────────────────
np_type_tables = []  # Empty since Query C was not run (prediction.md missing)

# ── SEASONAL COVERAGE (from Query E data) ────────────────────────────────────
# SEEDLESS GRAPE 400G. still active at SE3 (last sold 08/06/2026)
# MW1: both grape SKUs dormant (last sold 26 May)
GRAPE_BASELINES = {"33": 339, "105": 251}
# SE3: total rev 3289.66 over 69 days (01/04 to 08/06)
se3_grape_per_day = round(3289.66 / 69)
# MW1: SEEDLESS GRAPE dormant since 26 May → 0 current daily
mw1_grape_per_day = 0
grape_total_rev = 133186.69 + 105553.37  # MW1 + SE3 Shine Muscat all-time

seasonal_skus = [
    {
        "fruit_emoji": "🍇",
        "memo": "SEEDLESS GRAPE 400G.",
        "launch": "1 Apr 2026",
        "mw1_units": "7",
        "mw1_per_day": "62",  # active 9 May–26 May = 17 days, rev 1046.71
        "se3_units": "22",
        "se3_per_day": str(se3_grape_per_day),
    }
]

def coverage_meta(new_per_day, baseline):
    pct = round(new_per_day / baseline * 100) if baseline else 0
    if pct >= 100:
        return pct, "#155724", "#D4EDDA", "✅ Fully replaced"
    elif pct >= 70:
        return pct, "#856404", "#FFF3CD", "🟡 Partial — monitor"
    else:
        return pct, "#721C24", "#F8D7DA", "🔴 Large gap — push promotion or add SKU"

mw1_cov_pct, mw1_cov_color, mw1_badge_bg, mw1_badge_text = coverage_meta(mw1_grape_per_day, 339)
se3_cov_pct, se3_cov_color, se3_badge_bg, se3_badge_text = coverage_meta(se3_grape_per_day, 251)

seasonal_coverage = [
    {
        "branch_label": "MW1",
        "branch_color": "#5551FE",
        "grape_baseline": "339",
        "new_fruit_per_day": str(mw1_grape_per_day),
        "coverage_pct": str(mw1_cov_pct),
        "coverage_color": mw1_cov_color,
        "badge_bg": mw1_badge_bg,
        "badge_text": mw1_badge_text,
        "daily_gap": f"−฿{339 - mw1_grape_per_day:,}",
        "monthly_impact": f"−฿{(339 - mw1_grape_per_day)*30:,}/mo",
    },
    {
        "branch_label": "SE3",
        "branch_color": "#F27061",
        "grape_baseline": "251",
        "new_fruit_per_day": str(se3_grape_per_day),
        "coverage_pct": str(se3_cov_pct),
        "coverage_color": se3_cov_color,
        "badge_bg": se3_badge_bg,
        "badge_text": se3_badge_text,
        "daily_gap": f"−฿{251 - se3_grape_per_day:,}",
        "monthly_impact": f"−฿{(251 - se3_grape_per_day)*30:,}/mo",
    },
]

# ── ASSEMBLE DATA.JSON ────────────────────────────────────────────────────────
am_queue_count = 0

data = {
    "scalars": {
        "report_date": REPORT_DATE,
        "report_date_display": REPORT_DATE_DISPLAY,
        "report_day_th": REPORT_DAY_TH,
        "window_30d_start": WINDOW_30D_START,
        "generated_timestamp": GENERATED_TIMESTAMP,
        "subject_prefix": subject_prefix,
        "comb_net": fmt(yesterday_comb),
        "signed_pct": signed_pct,
        "mw1_net": fmt(yesterday_mw1),
        "se3_net": fmt(yesterday_se3),
        "pkt_net": fmt(yesterday_pkt),
        "mw1_vs_30d": mw1_vs_30d,
        "se3_vs_30d": se3_vs_30d,
        "pkt_vs_30d": pkt_vs_30d,
        "mw1_avg_30d": fmt(mw1_avg),
        "se3_avg_30d": fmt(se3_avg),
        "pkt_avg_30d": fmt(pkt_avg),
        "comb_avg_30d": fmt(comb_avg),
        "mw1_min_30d": fmt(min(all_mw1)),
        "mw1_max_30d": fmt(max(all_mw1)),
        "se3_min_30d": fmt(min(all_se3)),
        "se3_max_30d": fmt(max(all_se3)),
        "pkt_min_30d": fmt(min(all_pkt)),
        "pkt_max_30d": fmt(max(all_pkt)),
        "comb_monthly_runrate": f"{round(comb_avg*30/1000, 1):,}K",
        "last7_total": last7_total,
        "last7_avg": last7_avg,
        "mw1_7d_total": mw1_7d_total,
        "se3_7d_total": se3_7d_total,
        "pkt_7d_total": pkt_7d_total,
        "comb_7d_total": comb_7d_total,
        "am_queue_count": str(am_queue_count),
        "dormant_count": str(dormant_count),
        # NP section (minimal — query C not run)
        "np_summary_line": "New product tracking unavailable (juiceland-prediction.md not found)",
        "np_total_units": "—",
        "np_total_rev": "—",
        "drinks_n": "0",
        "drinks_todate_units": "—",
        "drinks_todate_rev": "—",
        "fruit_n": "1",
        "fruit_todate_units": "22",
        "fruit_todate_rev": "3,290",
        "new_cat_n": "0",
        "new_cat_todate_units": "—",
        "new_cat_todate_rev": "—",
        # Seasonal
        "grape_total_rev": fmt(grape_total_rev),
        "grape_last_mw1": "21 May 2026",
        "grape_last_se3": "28 Apr 2026",
    },
    "repeats": {
        "chart_days": chart_days,
        "last7_headers": last7_headers,
        "last7_mw1": last7_mw1,
        "last7_se3": last7_se3,
        "last7_pkt": last7_pkt,
        "last7_comb": last7_comb,
        "top20_branches": top20_branches,
        "dormant_branches": dormant_branches,
        "np_type_tables": np_type_tables,
        "seasonal_skus": seasonal_skus,
        "seasonal_coverage": seasonal_coverage,
        "am_items": [],
    },
    "sections": {
        "am_review": am_queue_count > 0,
        "seasonal": True,
        "dormant": dormant_count > 0,
        "forecast_shown": False,
        "forecast_suppressed": True,
        "anomaly_shown": False,
    }
}

with open("/home/user/report/Juiceland/data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("data.json written.")

# ── PATCH TEMPLATE: replace nested REPEAT blocks with {{token}} placeholders ──
TMPL_PATH = "/home/user/report/Juiceland/juiceland-template.html"
with open(TMPL_PATH, "r", encoding="utf-8") as f:
    tmpl = f.read()

def replace_inner_repeat(html, inner_name, token_name):
    pattern = re.compile(
        r'<!--\s*REPEAT:' + inner_name + r'[\s\S]*?-->([\s\S]*?)<!--\s*/REPEAT:' + inner_name + r'\s*-->',
        re.DOTALL
    )
    new_html, count = pattern.subn('{{' + token_name + '}}', html, count=1)
    print(f"  Replaced REPEAT:{inner_name} → {{{{{token_name}}}}} ({count} substitution)")
    return new_html

tmpl = replace_inner_repeat(tmpl, "top20_rows", "top20_rows_html")
tmpl = replace_inner_repeat(tmpl, "dormant_rows", "dormant_rows_html")
tmpl = replace_inner_repeat(tmpl, "np_rows", "np_rows_html")

with open(TMPL_PATH, "w", encoding="utf-8") as f:
    f.write(tmpl)
print("Template patched.")
