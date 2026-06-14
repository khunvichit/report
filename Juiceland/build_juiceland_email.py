#!/usr/bin/env python3
"""
Build Juiceland Daily Sales Report email.html from query results.
Handles nested REPEATs correctly (fill_template.py cannot due to shared global repeat context).
Reads juiceland-template.html + juiceland-prediction-section.html, writes email.html.

Report date: 2026-06-13 (yesterday Asia/Bangkok)
Run date:    2026-06-14
"""
import re, sys, json, math, os
from datetime import date, timedelta
from collections import defaultdict

# ─────────────────── template filler ───────────────────

def fill(template, scalars, repeats, sections):
    """Sections first (dropped sections kill their REPEATs), then repeats, then scalars."""
    for name, keep in sections.items():
        pat = re.compile(
            r'<!--\s*SECTION:' + re.escape(name) + r'[\s\S]*?-->([\s\S]*?)<!--\s*/SECTION:' + re.escape(name) + r'\s*-->',
            re.DOTALL)
        template = pat.sub(r'\1' if keep else '', template)
    template = expand_repeats(template, repeats)
    for k, v in scalars.items():
        template = template.replace('{{' + k + '}}', str(v))
    template = re.sub(r'<!--\s*={10,}[\s\S]*?={10,}\s*-->', '', template)
    template = re.sub(r'<!--\s*/?(?:REPEAT|SECTION):\w+[\s\S]*?-->', '', template)
    leftovers = sorted(set(re.findall(r'\{\{(\w+)\}\}', template)))
    if leftovers:
        sys.stderr.write('WARNING unresolved: ' + ', '.join(leftovers) + '\n')
    return template


def expand_repeats(html, global_repeats):
    pat = re.compile(
        r'<!--\s*REPEAT:(\w+)[\s\S]*?-->([\s\S]*?)<!--\s*/REPEAT:\1\s*-->',
        re.DOTALL)
    def repl(m):
        name, inner = m.group(1), m.group(2)
        items = global_repeats.get(name, [])
        out = []
        for item in items:
            local = dict(global_repeats)
            for k, v in item.items():
                if isinstance(v, list):
                    local[k] = v
            block = inner
            for k, v in item.items():
                if not isinstance(v, list):
                    block = block.replace('{{' + k + '}}', str(v))
            block = expand_repeats(block, local)
            out.append(block)
        return ''.join(out)
    prev = None
    while prev != html:
        prev = html
        html = pat.sub(repl, html)
    return html

# ─────────────────── raw query data ───────────────────

REPORT_DATE = '2026-06-13'

# Query A — window 2026-05-15 → 2026-06-13 (30 days), loc 33=MW1, 105=SE3, 109=PKT
QA = [
    ('2026-05-15', 33, 35787.0),  ('2026-05-15', 105, 19010.0),  ('2026-05-15', 109, 10244.0),
    ('2026-05-16', 33, 30765.5),  ('2026-05-16', 105, 25470.0),  ('2026-05-16', 109, 9920.0),
    ('2026-05-17', 33, 34754.0),  ('2026-05-17', 105, 35410.0),  ('2026-05-17', 109, 13484.0),
    ('2026-05-18', 33, 25913.0),  ('2026-05-18', 105, 22700.0),  ('2026-05-18', 109, 12484.0),
    ('2026-05-19', 33, 33034.5),  ('2026-05-19', 105, 25820.0),  ('2026-05-19', 109, 7867.0),
    ('2026-05-20', 33, 31093.0),  ('2026-05-20', 105, 17307.5),  ('2026-05-20', 109, 10311.0),
    ('2026-05-21', 33, 36940.5),  ('2026-05-21', 105, 29297.0),  ('2026-05-21', 109, 9611.0),
    ('2026-05-22', 33, 40088.0),  ('2026-05-22', 105, 26689.0),  ('2026-05-22', 109, 10358.0),
    ('2026-05-23', 33, 38639.5),  ('2026-05-23', 105, 39492.0),  ('2026-05-23', 109, 12698.0),
    ('2026-05-24', 33, 45429.5),  ('2026-05-24', 105, 28328.0),  ('2026-05-24', 109, 12933.0),
    ('2026-05-25', 33, 38221.0),  ('2026-05-25', 105, 31983.5),  ('2026-05-25', 109, 10502.0),
    ('2026-05-26', 33, 36852.5),  ('2026-05-26', 105, 24575.5),  ('2026-05-26', 109, 7039.0),
    ('2026-05-27', 33, 33877.0),  ('2026-05-27', 105, 26502.0),  ('2026-05-27', 109, 16234.0),
    ('2026-05-28', 33, 33415.0),  ('2026-05-28', 105, 31121.0),  ('2026-05-28', 109, 12474.0),
    ('2026-05-29', 33, 42210.5),  ('2026-05-29', 105, 22568.0),  ('2026-05-29', 109, 13844.0),
    ('2026-05-30', 33, 34788.0),  ('2026-05-30', 105, 26883.0),  ('2026-05-30', 109, 14605.0),
    ('2026-05-31', 33, 28583.0),  ('2026-05-31', 105, 32544.0),  ('2026-05-31', 109, 14052.0),
    ('2026-06-01', 33, 32133.0),  ('2026-06-01', 105, 24075.0),  ('2026-06-01', 109, 13940.0),
    ('2026-06-02', 33, 36476.0),  ('2026-06-02', 105, 15959.0),  ('2026-06-02', 109, 9920.0),
    ('2026-06-03', 33, 40024.0),  ('2026-06-03', 105, 19497.0),  ('2026-06-03', 109, 10813.0),
    ('2026-06-04', 33, 35666.5),  ('2026-06-04', 105, 16604.0),  ('2026-06-04', 109, 13146.0),
    ('2026-06-05', 33, 35611.0),  ('2026-06-05', 105, 20180.0),  ('2026-06-05', 109, 13589.0),
    ('2026-06-06', 33, 32714.0),  ('2026-06-06', 105, 23312.0),  ('2026-06-06', 109, 13867.0),
    ('2026-06-07', 33, 25977.0),  ('2026-06-07', 105, 17749.0),  ('2026-06-07', 109, 12993.0),
    ('2026-06-08', 33, 38857.0),  ('2026-06-08', 105, 24570.0),  ('2026-06-08', 109, 12810.0),
    ('2026-06-09', 33, 30612.5),  ('2026-06-09', 105, 12035.0),  ('2026-06-09', 109, 10190.0),
    ('2026-06-10', 33, 37665.0),  ('2026-06-10', 105, 22195.0),  ('2026-06-10', 109, 10250.0),
    ('2026-06-11', 33, 36938.0),  ('2026-06-11', 105, 18834.0),  ('2026-06-11', 109, 12373.0),
    ('2026-06-12', 33, 35377.5),  ('2026-06-12', 105, 25575.0),  ('2026-06-12', 109, 11753.0),
    ('2026-06-13', 33, 33715.0),  ('2026-06-13', 105, 25149.0),  ('2026-06-13', 109, 12119.0),
]

# Query B — top-20 per branch on 2026-06-13, sorted by qty desc
QB_MW1 = [
    ('EVIAN', 38, 4261.70, 5),
    ('S5 MANGO SMOOTHIE 16OZ', 11, 1644.87, 2),
    ('COCONUT JUICE BOTTLE', 8, 1383.18, 3),
    ('COCONUT READY TO DRINK', 8, 1271.04, 3),
    ('PRIDE PARROT YELLOW', 7, 1308.43, 3),
    ('SOFT-SLUSH! ORIGINAL', 7, 1046.71, 3),
    ('WATERMELON JUICE BOTTLE', 6, 1037.37, 2),
    ('C1 GUAVA&GREEN APPLE&RED APPLE COLD PRESSED 22OZ', 5, 981.30, 3),
    ('PAPAYA 400G.', 5, 700.95, 2),
    ('MOOVE CLEAR PROTEIN', 5, 700.94, 1),
    ('3 kinds of fruit 400g Papaya/Pineapple/Guava', 5, 700.95, 2),
    ('PRIDE PARROT RED', 4, 747.68, 3),
    ('S1 COCONUT SMOOTHIE 22OZ', 4, 766.36, 3),
    ('S3 WATERMELON SMOOTHIE 16OZ', 4, 598.12, 1),
    ('MANGO 400G.', 4, 598.12, 1),
    ('P1 GOLDEN GLOW 22OZ', 3, 630.84, 2),
    ('C3 WATERMELON COLD PRESSED 22OZ', 3, 588.78, 3),
    ('C5 PINEAPPLE&GREEN APPLE COLD PRESSED 16OZ', 3, 518.70, 1),
    ('S1 COCONUT SMOOTHIE 16OZ', 3, 504.66, 2),
    ('C2 ORANGE COLD PRESSED 22OZ', 3, 588.78, 1),
]
QB_SE3 = [
    ('EVIAN', 38, 4261.70, 5),
    ('COCONUT READY TO DRINK', 13, 2049.53, 4),
    ('WATERMELON 400G.', 11, 1542.07, 3),
    ('PRIDE PARROT YELLOW', 8, 1476.65, 3),
    ('3 kinds of fruit 400g Papaya/Pineapple/Guava', 7, 981.33, 2),
    ('P1 GOLDEN GLOW 22OZ', 5, 1051.40, 4),
    ('PINEAPPLE 400G.', 5, 700.95, 2),
    ('Chicken Club Croissant', 4, 557.00, 2),
    ('MANGO 400G.', 4, 598.12, 2),
    ('S1 COCONUT SMOOTHIE 22OZ', 4, 766.36, 2),
    ('PRIDE PARROT RED', 4, 747.67, 3),
    ('C8 CARROT&CELERY&RED APPLE&PINEAPPLE COLD PRESSED 22OZ', 4, 785.04, 2),
    ('C3 WATERMELON COLD PRESSED 22OZ', 3, 588.78, 2),
    ('S1 COCONUT SMOOTHIE 16OZ', 3, 504.67, 1),
    ('S5 MANGO SMOOTHIE 22OZ', 3, 518.69, 2),
    ('C4 MANGO PASSION COLD PRESSED 16OZ', 3, 518.70, 2),
    ('MANGO (1 PCS.) 380 G.', 3, 420.56, 2),
    ('MANGO JUICE (BOTTLE) 300 ML', 3, 518.69, 2),
    ('C6 PINEAPPLE COLD PRESSED 22OZ', 2, 392.52, 2),
    ('S5 MANGO SMOOTHIE 16OZ', 2, 299.06, 1),
]
QB_PKT = [
    ('Evian 500ml. (Bottle)', 16, 1782.19, 3),
    ('S5 mango smoothie 16oz', 7, 1046.73, 2),
    ('Mango 400 g. (Pack)', 5, 747.66, 3),
    ('Coke Zero 500 ml. (Bottle)', 4, 299.08, 1),
    ('Indian Tea Cardamom Chai 12oz', 4, 448.60, 2),
    ('Up size Smoothie & Cold Press 16oz to 22oz', 4, 93.44, 2),
    ('Ham and Cheese Croissant', 3, 513.41, 1),
    ('C3 Watermelon cold pressed 16oz', 3, 518.70, 1),
    ('S2 mango passion smoothie 16oz', 3, 448.60, 2),
    ('Fanta Orange 450 ml. (Bottle)', 3, 224.30, 1),
    ('YS3 banana yoghurt smoothie 16oz', 2, 327.11, 1),
    ('Sprite 500 ml. (Bottle)', 2, 149.54, 2),
    ('P1 Mango passion fruit cold pressed 16oz', 2, 373.84, 1),
    ('Coke 500 ml. (Bottle)', 2, 149.54, 1),
    ('Pride Parrot Red Smoothie 22 oz.', 2, 373.84, 1),
    ('Fanta Strawberry 450 ml. (Bottle)', 2, 149.53, 2),
    ('S6 banana smoothie 16oz', 2, 299.07, 1),
    ('T1 Iced Thai milk tea 16oz', 2, 280.38, 1),
    ('CH2 Caffe latte (hot) 12oz', 1, 140.19, 1),
    ('S3 watermelon smoothie 16oz', 1, 149.53, 1),
]

# Dormant SKUs (Query D filtered: qty_30d >= 3, no malformed \n memos)
# (memo, last_sold_str, qty_30d, days_sold_30d, rev_30d)
DORMANT_MW1 = [
    ('P1 GOLDEN GLOW 16OZ',           '2026-06-05', 44, 17, 8224.41),
    ('Overnight Oat mango 16 oz',      '2026-06-06', 27, 15, 6787.80),
    ('HOT CHOCOLATE 8 oz',             '2026-05-27', 18,  4, 2186.96),
    ('SHINE MUSCAT GRAPES 400G (PACK)','2026-05-21', 16,  7, 2392.48),
    ('VANILLA BEAN GREEK YOGURT',      '2026-05-26', 12,  9, 2119.65),
    ('BLUEBERRY GREEK YOGURT',         '2026-06-05', 10,  8, 1766.39),
    ('RASPBERRY GREEK YOGURT',         '2026-05-22',  8,  6, 1413.06),
    ('T2 ICED THAI TEA WITH LIME 16OZ','2026-06-01',  6,  5,  841.13),
    ('Mango Berry Smoothie 16oz',      '2026-05-26',  5,  4,  864.50),
    ('CAESAR SALAD',                   '2026-05-29',  4,  3,  672.88),
    ('Mango Pineapple Smoothie 16oz',  '2026-05-23',  4,  2,  691.59),
    ('Mango Sticky Rice (Box)',        '2026-06-01',  3,  3,  501.85),
]
DORMANT_SE3 = [
    ('HOT CHOCOLATE 8 oz',             '2026-05-29', 22,  6, 2672.98),
    ('Mango Sticky Rice (Box)',         '2026-05-31', 19,  8, 3178.51),
    ('Golden Harmony Greek Yogurt',    '2026-05-31', 17,  8, 3002.81),
    ('MANGO PINEAPPLE SMOOTHIE 16OZ',  '2026-05-31', 14,  8, 2420.60),
    ('CI3 ICED AMERICANO 16OZ',        '2026-06-04', 10,  9, 1448.60),
    ('Overnight Oat Berry 16 oz',      '2026-05-27',  7,  5, 1694.40),
    ('BANANA YOGHURT SMOOTHIE 16OZ',   '2026-05-28',  7,  6, 1144.85),
    ('T2 ICED THAI TEA WITH LIME 16OZ','2026-06-06',  6,  6,  841.14),
    ('CH1 ESPRESSO',                   '2026-06-05',  6,  5,  700.92),
    ('CI4 ICED CAPPUCCINO 22OZ',       '2026-05-30',  5,  4,  911.20),
    ('Overnight Oat mango 16 oz',      '2026-06-04',  5,  5, 1257.00),
    ('MANGO BERRY SMOOTHIE 16OZ',      '2026-05-19',  5,  4,  864.50),
    ('T2 ICED THAI TEA WITH LIME 22OZ','2026-05-28',  5,  5,  817.75),
    ('CARROT JUICE BOTTLE',            '2026-06-02',  4,  4,  691.59),
    ('MANGOSTEEN 400g.',               '2026-06-01',  3,  3,  700.92),
]
DORMANT_PKT = [
    ('Banana 2PCS.',                            '2026-06-06', 17, 14,  937.38),
    ('Mango Pineapple Smoothie 16oz',           '2026-05-28',  8,  6, 1383.22),
    ('Orange Cold Pressed Juice 300 ml. (bottle)','2026-05-27', 5,  4,  864.49),
    ('singha soda water 325ml',                 '2026-06-04',  4,  2,  243.00),
    ('Nestle Water 600 ml',                     '2026-06-06',  4,  4,   37.40),
    ('Pride Parrot Red Smoothie 22 oz.',        '2026-06-05',  4,  2,  747.67),
]

# ─────────────────── computations ───────────────────

report_date  = date(2026, 6, 13)
run_date     = date(2026, 6, 14)
window_start = report_date - timedelta(days=29)  # 2026-05-15

daily = defaultdict(lambda: {33: 0.0, 105: 0.0, 109: 0.0})
for d_str, loc, net in QA:
    d = date.fromisoformat(d_str)
    daily[d][loc] += net

dates_sorted = sorted(daily.keys())   # 30 dates: 05/15 → 06/13

mw1  = {d: daily[d][33]  for d in dates_sorted}
se3  = {d: daily[d][105] for d in dates_sorted}
pkt  = {d: daily[d][109] for d in dates_sorted}
comb = {d: mw1[d] + se3[d] + pkt[d] for d in dates_sorted}

yest = report_date
mw1_yest = mw1[yest]; se3_yest = se3[yest]; pkt_yest = pkt[yest]
comb_yest = mw1_yest + se3_yest + pkt_yest

mw1_avg  = sum(mw1.values()) / 30
se3_avg  = sum(se3.values()) / 30
pkt_avg  = sum(pkt.values()) / 30
comb_avg = mw1_avg + se3_avg + pkt_avg

mw1_min = min(mw1.values()); mw1_max = max(mw1.values())
se3_min = min(se3.values()); se3_max = max(se3.values())
pkt_min = min(pkt.values()); pkt_max = max(pkt.values())

signed_pct = (comb_yest - comb_avg) / comb_avg * 100
mw1_vs30   = (mw1_yest - mw1_avg)  / mw1_avg  * 100
se3_vs30   = (se3_yest - se3_avg)  / se3_avg  * 100
pkt_vs30   = (pkt_yest - pkt_avg)  / pkt_avg  * 100

subject_prefix = '🔥' if signed_pct >= 10 else ('⚠️' if signed_pct <= -10 else '✅')

chart_max = max(max(mw1.values()), max(se3.values()), max(pkt.values()))

def fmt(n, decimals=0):
    if decimals == 0:
        return f'{round(n):,}'
    return f'{n:,.{decimals}f}'

def bar(n): return str(round(n / chart_max * 220))

TH_WD      = ['จ','อ','พ','พฤ','ศ','ส','อา']
TH_WD_FULL = ['วันจันทร์','วันอังคาร','วันพุธ','วันพฤหัสบดี','วันศุกร์','วันเสาร์','วันอาทิตย์']
EN_MONTH   = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
EN_MONTH_FULL = ['January','February','March','April','May','June',
                 'July','August','September','October','November','December']

def th_weekday_abbr(d): return TH_WD[d.weekday()]

report_date_display  = f'{report_date.day} {EN_MONTH_FULL[report_date.month-1]} {report_date.year}'
report_day_th        = TH_WD_FULL[report_date.weekday()]
window_30d_start_str = f'{window_start.day} {EN_MONTH_FULL[window_start.month-1]} {window_start.year}'

last7_dates  = dates_sorted[-7:]   # 06/07 → 06/13
mw1_7d   = sum(mw1[d] for d in last7_dates)
se3_7d   = sum(se3[d] for d in last7_dates)
pkt_7d   = sum(pkt[d] for d in last7_dates)
comb_7d  = mw1_7d + se3_7d + pkt_7d
last7_avg_val = comb_7d / 7

# ─── FORECAST (today = Sunday 2026-06-14) ───
fc_date = run_date   # Sunday

def same_wday_history(branch_dict, target_date, weeks=4):
    vals = []
    d = target_date - timedelta(weeks=1)
    while len(vals) < weeks:
        if d in branch_dict:
            vals.append(branch_dict[d])
        d -= timedelta(weeks=1)
    return vals

mw1_sun = same_wday_history(mw1, fc_date)   # [06/07, 05/31, 05/24, 05/17]
se3_sun = same_wday_history(se3, fc_date)
pkt_sun = same_wday_history(pkt, fc_date)

def forecast_branch(sun_vals, branch_dict, all_dates):
    base = sum(sun_vals) / len(sun_vals) if sun_vals else 0
    last7_vals = [branch_dict[d] for d in all_dates[-7:]]
    trend_adj  = (base + sum(last7_vals) / 7) / 2
    stdev = math.sqrt(sum((x - base)**2 for x in sun_vals) / len(sun_vals)) if len(sun_vals) > 1 else base * 0.12
    band  = max(stdev, trend_adj * 0.08)
    conf_pct = stdev / base * 100 if base else 25
    conf_dot = '🟢' if conf_pct < 12 else ('🟡' if conf_pct < 25 else '🔴')
    return trend_adj, band, conf_dot

mw1_fc, mw1_band, mw1_conf = forecast_branch(mw1_sun, mw1, dates_sorted)
se3_fc, se3_band, se3_conf = forecast_branch(se3_sun, se3, dates_sorted)
pkt_fc, pkt_band, pkt_conf = forecast_branch(pkt_sun, pkt, dates_sorted)

comb_fc      = mw1_fc + se3_fc + pkt_fc
comb_band    = math.sqrt(mw1_band**2 + se3_band**2 + pkt_band**2)
comb_conf_pct = comb_band / comb_fc * 100 if comb_fc else 25
comb_conf = '🟢' if comb_conf_pct < 12 else ('🟡' if comb_conf_pct < 25 else '🔴')

# ─── NEW PRODUCTS ───
# Drinks to-date (through 2026-06-13, from Query C)
drinks_n            = 12
drinks_total_units  = 304
drinks_total_rev    = 48337

drinks_yest_units = 38   # PPR 4+4+2 + PPY 7+8+1 + MOOVE 5 + Fanta Org 3 + Fanta Str 2 + Sprite 2
drinks_yest_rev   = round(747.68+747.67+373.84+1308.43+1476.65+186.92+700.94+224.30+149.53+149.54)

# Seasonal fruits
fruit_n            = 4
fruit_total_units  = 40
fruit_total_rev    = 6453

fruit_yest_units = 2   # LYCHEE: MW1 1u + SE3 1u
fruit_yest_rev   = round(158.88 + 158.88)

# New Category
new_cat_n            = 9
new_cat_total_units  = 88
new_cat_total_rev    = 15329

new_cat_yest_units = 4   # Chicken Club Croissant SE3
new_cat_yest_rev   = 557

np_total_units = drinks_total_units + fruit_total_units + new_cat_total_units
np_total_rev   = drinks_total_rev + fruit_total_rev + new_cat_total_rev

NP_DRINKS_ROWS = [
    {'memo': 'PRIDE PARROT RED', 'launch': '1 Jun 2026', 'notes': 'MW1, SE3, PKT',
     'total_units': 129, 'total_rev': '24,075', 'branch_split': 'MW1 82u · SE3 34u · PKT 13u',
     'yest_units': 10, 'status_badge': '🟢 on target'},
    {'memo': 'PRIDE PARROT YELLOW', 'launch': '1 Jun 2026', 'notes': 'MW1, SE3, PKT',
     'total_units': 77, 'total_rev': '14,354', 'branch_split': 'MW1 55u · SE3 18u · PKT 4u',
     'yest_units': 16, 'status_badge': '🟢 on target'},
    {'memo': 'HOT CHOCOLATE 8 oz', 'launch': '24 May 2026', 'notes': 'MW1, SE3 — now dormant',
     'total_units': 40, 'total_rev': '4,860', 'branch_split': 'MW1 18u · SE3 22u',
     'yest_units': 0, 'status_badge': '🔴 no sales — dormant'},
    {'memo': 'MOOVE CLEAR PROTEIN', 'launch': '13 Jun 2026', 'notes': 'MW1 — first sale yesterday!',
     'total_units': 5, 'total_rev': '701', 'branch_split': 'MW1',
     'yest_units': 5, 'status_badge': '⚪ new — 1 day'},
    {'memo': 'Fanta Orange 450ml. (Bottle)', 'launch': '31 May 2026', 'notes': 'PKT only',
     'total_units': 17, 'total_rev': '1,271', 'branch_split': 'PKT',
     'yest_units': 3, 'status_badge': '🟢 on target'},
    {'memo': 'Sprite 500ml. (Bottle)', 'launch': '30 May 2026', 'notes': 'PKT only',
     'total_units': 17, 'total_rev': '1,272', 'branch_split': 'PKT',
     'yest_units': 2, 'status_badge': '🟢 on target'},
    {'memo': 'Fanta Strawberry 450ml. (Bottle)', 'launch': '1 Jun 2026', 'notes': 'PKT only',
     'total_units': 13, 'total_rev': '973', 'branch_split': 'PKT',
     'yest_units': 2, 'status_badge': '🟢 on target'},
    {'memo': 'HOT MOCHA 8 oz', 'launch': '20 May 2026', 'notes': 'MW1 — now dormant',
     'total_units': 2, 'total_rev': '252', 'branch_split': 'MW1',
     'yest_units': 0, 'status_badge': '🔴 no sales — dormant'},
    {'memo': 'Iced Espresso Coconut 12oz', 'launch': '15 May 2026', 'notes': 'SE3 — now dormant',
     'total_units': 2, 'total_rev': '336', 'branch_split': 'SE3',
     'yest_units': 0, 'status_badge': '🔴 no sales — dormant'},
    {'memo': 'Iced Espresso Orange 12oz', 'launch': '29 May 2026', 'notes': 'SE3 — now dormant',
     'total_units': 1, 'total_rev': '168', 'branch_split': 'SE3',
     'yest_units': 0, 'status_badge': '🔴 no sales — dormant'},
    {'memo': 'Fanta Fruit Punch 450ml. (Bottle)', 'launch': '31 May 2026', 'notes': 'PKT — now dormant',
     'total_units': 1, 'total_rev': '75', 'branch_split': 'PKT',
     'yest_units': 0, 'status_badge': '🔴 no sales — dormant'},
]
NP_FRUIT_ROWS = [
    {'memo': 'LYCHEE 400G.', 'launch': '28 May 2026', 'notes': 'MW1, SE3',
     'total_units': 28, 'total_rev': '4,449', 'branch_split': 'MW1 9u · SE3 19u',
     'yest_units': 2, 'status_badge': '🟢 on target'},
    {'memo': 'ROSE APPLE 400G.', 'launch': '30 May 2026', 'notes': 'SE3 only',
     'total_units': 7, 'total_rev': '1,047', 'branch_split': 'SE3',
     'yest_units': 0, 'status_badge': '⚪ not sold yesterday'},
    {'memo': 'MANGOSTEEN 400g.', 'launch': '28 May 2026', 'notes': 'SE3, MW1 — slowing',
     'total_units': 4, 'total_rev': '935', 'branch_split': 'SE3 3u · MW1 1u',
     'yest_units': 0, 'status_badge': '🟡 below target — SE3 dormant'},
    {'memo': 'SEEDLESS GRAPE TOPPING', 'launch': '5 Jun 2026', 'notes': 'MW1 only',
     'total_units': 1, 'total_rev': '23', 'branch_split': 'MW1',
     'yest_units': 0, 'status_badge': '⚪ dormant — 1 sale total'},
]
NP_NEWCAT_ROWS = [
    {'memo': 'Overnight Oat mango 16 oz', 'launch': '21 May 2026', 'notes': 'MW1, SE3 — now dormant',
     'total_units': 33, 'total_rev': '8,296', 'branch_split': 'MW1 28u · SE3 5u',
     'yest_units': 0, 'status_badge': '🔴 no sales — dormant'},
    {'memo': 'Chicken Club Croissant', 'launch': '22 May 2026', 'notes': 'SE3',
     'total_units': 27, 'total_rev': '3,760', 'branch_split': 'SE3',
     'yest_units': 4, 'status_badge': '🟢 on target'},
    {'memo': 'Overnight Oat Berry 16 oz', 'launch': '22 May 2026', 'notes': 'SE3, MW1 — now dormant',
     'total_units': 8, 'total_rev': '1,936', 'branch_split': 'SE3 7u · MW1 1u',
     'yest_units': 0, 'status_badge': '🔴 no sales — dormant'},
    {'memo': 'HONEY TOPPING', 'launch': '18 May 2026', 'notes': 'MW1',
     'total_units': 7, 'total_rev': '165', 'branch_split': 'MW1',
     'yest_units': 0, 'status_badge': '⚪ not sold yesterday'},
    {'memo': 'CAESAR SALAD', 'launch': '18 May 2026', 'notes': 'MW1 — now dormant',
     'total_units': 4, 'total_rev': '673', 'branch_split': 'MW1',
     'yest_units': 0, 'status_badge': '🔴 no sales — dormant'},
    {'memo': 'MANGO TOPPING', 'launch': '14 May 2026', 'notes': 'MW1',
     'total_units': 4, 'total_rev': '93', 'branch_split': 'MW1',
     'yest_units': 0, 'status_badge': '⚪ not sold yesterday'},
    {'memo': 'JAPANESE SALAD', 'launch': '16 May 2026', 'notes': 'MW1 — now dormant',
     'total_units': 2, 'total_rev': '336', 'branch_split': 'MW1',
     'yest_units': 0, 'status_badge': '🔴 no sales — dormant'},
    {'memo': 'GRANOLA TOPPING', 'launch': '20 May 2026', 'notes': 'MW1 — now dormant',
     'total_units': 2, 'total_rev': '47', 'branch_split': 'MW1',
     'yest_units': 0, 'status_badge': '🔴 no sales — dormant'},
    {'memo': 'BANANA TOPPING', 'launch': '12 Jun 2026', 'notes': 'MW1 — minimal data',
     'total_units': 1, 'total_rev': '23', 'branch_split': 'MW1',
     'yest_units': 0, 'status_badge': '⚪ new — 1 sale total'},
]

# ─── SEASONAL (Query E) ───
grape_total_rev = 238740   # SHINE MUSCAT both branches all-time
grape_last_mw1  = '11 Jun 2026'   # SEEDLESS GRAPE 400G. last sold
grape_last_se3  = '8 Jun 2026'

# New fruit per day (30-day window based on Query C totals)
mw1_fruit_rev      = 1429.92 + 233.65 + 23.36   # LYCHEE + MANGOSTEEN + GRAPE TOPPING
se3_fruit_rev      = 3018.71 + 700.92 + 1046.73  # LYCHEE + MANGOSTEEN + ROSE APPLE
mw1_fruit_per_day  = mw1_fruit_rev / 30           # ≈ 55.6/d
se3_fruit_per_day  = se3_fruit_rev / 30           # ≈ 158.9/d
mw1_grape_baseline = 339
se3_grape_baseline = 251
mw1_coverage = mw1_fruit_per_day / mw1_grape_baseline * 100   # ≈ 16%
se3_coverage = se3_fruit_per_day / se3_grape_baseline * 100   # ≈ 63%

def coverage_color(pct):
    return '#155724' if pct >= 100 else ('#856404' if pct >= 70 else '#721C24')

def coverage_bg(pct):
    return '#D4EDDA' if pct >= 100 else ('#FFF3CD' if pct >= 70 else '#F8D7DA')

def coverage_badge(pct):
    return '✅ Fully replaced' if pct >= 100 else ('🟡 Partial — monitor' if pct >= 70 else '🔴 Large gap — push promotion or add SKU')

# ─── DORMANT ───
def gap_days(last_sold_str):
    return (report_date - date.fromisoformat(last_sold_str)).days

def gap_color(days):
    return '#C62828' if days >= 14 else '#E65100'

def truncate(s, n=34):
    return (s[:n] + '…') if len(s) > n else s

def fmt_rev(r):
    return f'{round(r):,}'

def dormant_rows_for(branch_list):
    rows = []
    for memo, last_str, qty, days_sold, rev in branch_list:
        g = gap_days(last_str)
        rows.append({
            'memo_display':  truncate(memo),
            'memo_full':     memo,
            'qty_30d':       fmt(qty),
            'days_sold_30d': days_sold,
            'rev_30d':       fmt_rev(rev),
            'gap_days':      g,
            'gap_color':     gap_color(g),
        })
    return rows

dormant_count = len(DORMANT_MW1) + len(DORMANT_SE3) + len(DORMANT_PKT)

# ─── PREDICTION ───
commentary_text = (
    f'Yesterday (13 June 2026 · วันเสาร์), combined net was ฿{fmt(comb_yest)} ex-VAT, '
    f'{abs(signed_pct):.1f}% {"above" if signed_pct >= 0 else "below"} the 30-day average of ฿{fmt(comb_avg)}. '
    f'MW1 came in at ฿{fmt(mw1_yest)} ({mw1_vs30:+.1f}% vs avg), '
    f'SE3 at ฿{fmt(se3_yest)} ({se3_vs30:+.1f}% vs avg), '
    f'PKT at ฿{fmt(pkt_yest)} ({pkt_vs30:+.1f}% vs avg). '
    f'All three branches performed within normal range of their 30-day averages. '
    f'Notable: MOOVE CLEAR PROTEIN sold for the first time at MW1 (5u, ฿{fmt(700.94)}).'
)

anomaly_items = [
    {'anomaly_text': 'MW1 P1 GOLDEN GLOW 16OZ — dormant 8d, was ฿8,224 in 30d. Likely stock-out.',
     'anomaly_section_ref': 'Dormant SKUs §7'},
    {'anomaly_text': 'SE3: HOT CHOC, Mango Sticky Rice, Golden Harmony Yogurt — all dormant 13–15d (฿9,000+ combined 30d rev)',
     'anomaly_section_ref': 'Dormant SKUs §7'},
    {'anomaly_text': 'Seasonal fruit coverage: MW1 only 16% of grape baseline, SE3 63% — both below 70% target',
     'anomaly_section_ref': 'Seasonal Tracker §6'},
    {'anomaly_text': 'MOOVE CLEAR PROTEIN first sale at MW1 (5u ฿701) — monitor for repeat demand',
     'anomaly_section_ref': 'New Products §4'},
    {'anomaly_text': f'Pride Parrot Red+Yellow: 26u at MW1 yesterday — strongest new-drink seller',
     'anomaly_section_ref': 'New Products §4'},
]

# ─────────────────── build repeats ───────────────────

chart_days = []
for d in dates_sorted:
    chart_days.append({
        'date':            d.strftime('%Y-%m-%d'),
        'day_num':         str(d.day),
        'weekday_th_abbr': th_weekday_abbr(d),
        'mw1_net':         fmt(mw1[d]),
        'se3_net':         fmt(se3[d]),
        'pkt_net':         fmt(pkt[d]),
        'mw1_bar_px':      bar(mw1[d]),
        'se3_bar_px':      bar(se3[d]),
        'pkt_bar_px':      bar(pkt[d]),
    })

last7_headers = []
for d in last7_dates:
    is_yest = (d == report_date)
    last7_headers.append({
        'col_date':       f'{d.day} {EN_MONTH[d.month-1]}',
        'col_weekday_th': th_weekday_abbr(d),
        'header_bg':      'background:#4744CD;' if is_yest else '',
    })

def last7_cells(branch_dict):
    cells = []
    for d in last7_dates:
        is_yest = (d == report_date)
        cells.append({
            'net':        fmt(branch_dict[d]),
            'cell_style': 'background:#FFF3E0;font-weight:700;' if is_yest else '',
        })
    return cells

def last7_comb_cells():
    cells = []
    for d in last7_dates:
        is_yest = (d == report_date)
        cells.append({
            'net':     fmt(comb[d]),
            'cell_bg': 'background:#FFF3E0;' if is_yest else '',
        })
    return cells

def top20_rows_fn(items):
    rows = []
    for i, (memo, qty, rev, bills) in enumerate(items[:20]):
        rows.append({
            'rank':         str(i+1),
            'memo_display': truncate(memo, 32),
            'memo_full':    memo,
            'qty':          str(qty),
            'revenue':      f'{rev:,.2f}',
            'bills':        str(bills),
            'row_bg':       '#FAFAFA' if i % 2 else '#fff',
        })
    return rows

top20_branches = [
    {'header_color': '#5551FE', 'header_label': 'MW1 · 26-T1MW1-03+04', 'top20_rows': top20_rows_fn(QB_MW1)},
    {'header_color': '#F27061', 'header_label': 'SE3 · 27-T1SE3-05',    'top20_rows': top20_rows_fn(QB_SE3)},
    {'header_color': '#2E7D32', 'header_label': 'PKT · 28 Unit 362 (Phuket)', 'top20_rows': top20_rows_fn(QB_PKT)},
]

np_type_tables = [
    {'type_bg': '#1976D2', 'type_fg': '#fff', 'type_icon': '🥤', 'type_label': 'Drinks',          'np_rows': NP_DRINKS_ROWS},
    {'type_bg': '#AD1457', 'type_fg': '#fff', 'type_icon': '🍉', 'type_label': 'Seasonal Fruits', 'np_rows': NP_FRUIT_ROWS},
    {'type_bg': '#2E7D32', 'type_fg': '#fff', 'type_icon': '⭐', 'type_label': 'New Category',    'np_rows': NP_NEWCAT_ROWS},
]

seasonal_skus = [
    {'fruit_emoji': '🍈', 'memo': 'LYCHEE 400G.',       'launch': '28 May 2026',
     'mw1_units': '9',  'mw1_per_day': f'{1429.92/30:.0f}',
     'se3_units': '19', 'se3_per_day': f'{3018.71/30:.0f}'},
    {'fruit_emoji': '🟣', 'memo': 'MANGOSTEEN 400g.',   'launch': '28 May 2026',
     'mw1_units': '1',  'mw1_per_day': f'{233.65/30:.0f}',
     'se3_units': '3',  'se3_per_day': f'{700.92/30:.0f}'},
    {'fruit_emoji': '🌸', 'memo': 'ROSE APPLE 400G.',   'launch': '30 May 2026',
     'mw1_units': '—',  'mw1_per_day': '0',
     'se3_units': '7',  'se3_per_day': f'{1046.73/30:.0f}'},
    {'fruit_emoji': '🍇', 'memo': 'SEEDLESS GRAPE TOPPING', 'launch': '5 Jun 2026',
     'mw1_units': '1',  'mw1_per_day': '1',
     'se3_units': '—',  'se3_per_day': '0'},
]

seasonal_coverage = [
    {
        'branch_label':      'MW1 (Suvarnabhumi T1)',
        'branch_color':      '#5551FE',
        'grape_baseline':    fmt(mw1_grape_baseline),
        'new_fruit_per_day': fmt(round(mw1_fruit_per_day)),
        'coverage_pct':      f'{mw1_coverage:.0f}',
        'coverage_color':    coverage_color(mw1_coverage),
        'daily_gap':         f'฿{fmt(round(mw1_grape_baseline - mw1_fruit_per_day))}/d',
        'monthly_impact':    f'-฿{fmt(round((mw1_grape_baseline - mw1_fruit_per_day)*30))}/month',
        'badge_bg':          coverage_bg(mw1_coverage),
        'badge_text':        coverage_badge(mw1_coverage),
    },
    {
        'branch_label':      'SE3 (Suvarnabhumi T1)',
        'branch_color':      '#F27061',
        'grape_baseline':    fmt(se3_grape_baseline),
        'new_fruit_per_day': fmt(round(se3_fruit_per_day)),
        'coverage_pct':      f'{se3_coverage:.0f}',
        'coverage_color':    coverage_color(se3_coverage),
        'daily_gap':         f'฿{fmt(round(se3_grape_baseline - se3_fruit_per_day))}/d',
        'monthly_impact':    f'-฿{fmt(round((se3_grape_baseline - se3_fruit_per_day)*30))}/month',
        'badge_bg':          coverage_bg(se3_coverage),
        'badge_text':        coverage_badge(se3_coverage),
    },
]

def make_dormant_branch(label, color, items):
    return {
        'branch':       label,
        'header_color': color,
        'branch_count': str(len(items)),
        'dormant_rows': dormant_rows_for(items),
    }

dormant_branches = [
    make_dormant_branch('MW1', '#5551FE', DORMANT_MW1),
    make_dormant_branch('SE3', '#F27061', DORMANT_SE3),
    make_dormant_branch('PKT', '#2E7D32', DORMANT_PKT),
]

# ─────────────────── assemble scalars ───────────────────

scalars = {
    'report_date':          REPORT_DATE,
    'report_date_display':  report_date_display,
    'report_day_th':        report_day_th,
    'window_30d_start':     window_30d_start_str,
    'generated_timestamp':  '2026-06-14 08:00',
    'subject_prefix':       subject_prefix,
    'comb_net':             fmt(comb_yest),
    'signed_pct':           f'{signed_pct:+.1f}',
    'am_queue_count':       '0',
    'dormant_count':        str(dormant_count),
    'mw1_avg_30d':          fmt(mw1_avg),
    'se3_avg_30d':          fmt(se3_avg),
    'pkt_avg_30d':          fmt(pkt_avg),
    'comb_avg_30d':         fmt(comb_avg),
    'mw1_min_30d':          fmt(mw1_min),
    'mw1_max_30d':          fmt(mw1_max),
    'se3_min_30d':          fmt(se3_min),
    'se3_max_30d':          fmt(se3_max),
    'pkt_min_30d':          fmt(pkt_min),
    'pkt_max_30d':          fmt(pkt_max),
    'comb_monthly_runrate': f'{comb_avg*30/1000:,.1f}K',
    'last7_total':          fmt(comb_7d),
    'last7_avg':            fmt(last7_avg_val),
    'mw1_7d_total':         fmt(mw1_7d),
    'se3_7d_total':         fmt(se3_7d),
    'pkt_7d_total':         fmt(pkt_7d),
    'comb_7d_total':        fmt(comb_7d),
    'np_summary_line':      f'{drinks_n + fruit_n + new_cat_n} new SKUs launched May–Jun 2026 · Drinks · Seasonal Fruits · New Category',
    'np_total_units':       str(np_total_units),
    'np_total_rev':         fmt(np_total_rev),
    'drinks_n':             str(drinks_n),
    'drinks_todate_units':  str(drinks_total_units),
    'drinks_todate_rev':    fmt(drinks_total_rev),
    'fruit_n':              str(fruit_n),
    'fruit_todate_units':   str(fruit_total_units),
    'fruit_todate_rev':     fmt(fruit_total_rev),
    'new_cat_n':            str(new_cat_n),
    'new_cat_todate_units': str(new_cat_total_units),
    'new_cat_todate_rev':   fmt(new_cat_total_rev),
    'grape_total_rev':      fmt(grape_total_rev),
    'grape_last_mw1':       grape_last_mw1,
    'grape_last_se3':       grape_last_se3,
    # Forecast for Sunday 2026-06-14
    'forecast_date_display': f'{run_date.day} {EN_MONTH_FULL[run_date.month-1]} {run_date.year}',
    'mw1_conf_dot':  mw1_conf,
    'se3_conf_dot':  se3_conf,
    'pkt_conf_dot':  pkt_conf,
    'comb_conf_dot': comb_conf,
    'mw1_fc_low':    fmt(mw1_fc - mw1_band),
    'mw1_fc_high':   fmt(mw1_fc + mw1_band),
    'se3_fc_low':    fmt(se3_fc - se3_band),
    'se3_fc_high':   fmt(se3_fc + se3_band),
    'pkt_fc_low':    fmt(pkt_fc - pkt_band),
    'pkt_fc_high':   fmt(pkt_fc + pkt_band),
    'comb_fc_low':   fmt(comb_fc - comb_band),
    'comb_fc_high':  fmt(comb_fc + comb_band),
    'commentary_text': commentary_text,
    'anomaly_count': str(len(anomaly_items)),
}

repeats = {
    'chart_days':        chart_days,
    'last7_headers':     last7_headers,
    'last7_mw1':         last7_cells(mw1),
    'last7_se3':         last7_cells(se3),
    'last7_pkt':         last7_cells(pkt),
    'last7_comb':        last7_comb_cells(),
    'top20_branches':    top20_branches,
    'np_type_tables':    np_type_tables,
    'seasonal_skus':     seasonal_skus,
    'seasonal_coverage': seasonal_coverage,
    'dormant_branches':  dormant_branches,
    'anomaly_items':     anomaly_items,
    'am_items':          [],
}

sections = {
    'am_review':           False,
    'seasonal':            True,
    'dormant':             True,
    'forecast_shown':      True,
    'forecast_suppressed': False,
    'anomaly_shown':       True,
}

# ─────────────────── read templates & build ───────────────────

base = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(base, 'juiceland-template.html'), encoding='utf-8') as f:
    main_tpl = f.read()

with open(os.path.join(base, 'juiceland-prediction-section.html'), encoding='utf-8') as f:
    pred_tpl = f.read()

pred_html = fill(pred_tpl, scalars, repeats, sections)

inject_marker = '<div style="padding:24px;">'
main_tpl = main_tpl.replace(inject_marker, inject_marker + '\n' + pred_html, 1)

html = fill(main_tpl, scalars, repeats, sections)

out_path = os.path.join(base, 'email.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'email.html written ({len(html):,} bytes)', file=sys.stderr)
print('OK')
