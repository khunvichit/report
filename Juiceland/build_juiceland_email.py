#!/usr/bin/env python3
"""
Build Juiceland Daily Sales Report email.html from query results.
Handles nested REPEATs correctly (fill_template.py cannot due to shared global repeat context).
Reads juiceland-template.html + juiceland-prediction-section.html, writes email.html.

Report date: 2026-06-27 (yesterday Asia/Bangkok)
Run date:    2026-06-28
"""
import re, sys, json

# ─────────────────── template filler ───────────────────

def fill(template, scalars, repeats, sections):
    """Sections first (dropped sections kill their REPEATs), then repeats, then scalars."""
    # Sections
    for name, keep in sections.items():
        pat = re.compile(
            r'<!--\s*SECTION:' + re.escape(name) + r'[\s\S]*?-->([\s\S]*?)<!--\s*/SECTION:' + re.escape(name) + r'\s*-->',
            re.DOTALL)
        template = pat.sub(r'\1' if keep else '', template)

    # Repeats (nested-aware)
    template = expand_repeats(template, repeats)

    # Scalars
    for k, v in scalars.items():
        template = template.replace('{{' + k + '}}', str(v))

    # Strip leftover REPEAT/SECTION markers and HTML comment headers
    template = re.sub(r'<!--\s*={10,}[\s\S]*?={10,}\s*-->', '', template)
    template = re.sub(r'<!--\s*/?(?:REPEAT|SECTION):\w+[\s\S]*?-->', '', template)

    leftovers = sorted(set(re.findall(r'\{\{(\w+)\}\}', template)))
    if leftovers:
        sys.stderr.write('WARNING unresolved: ' + ', '.join(leftovers) + '\n')
    return template


def expand_repeats(html, global_repeats):
    """Expand all REPEAT blocks, supporting nested repeats via per-item list keys."""
    pat = re.compile(
        r'<!--\s*REPEAT:(\w+)[\s\S]*?-->([\s\S]*?)<!--\s*/REPEAT:\1\s*-->',
        re.DOTALL)

    def repl(m):
        name, inner = m.group(1), m.group(2)
        items = global_repeats.get(name, [])
        out = []
        for item in items:
            # Build local repeat context: global + any list values in this item
            local = dict(global_repeats)
            for k, v in item.items():
                if isinstance(v, list):
                    local[k] = v
            block = inner
            # Substitute scalar tokens from this item
            for k, v in item.items():
                if not isinstance(v, list):
                    block = block.replace('{{' + k + '}}', str(v))
            # Recursively expand nested repeats
            block = expand_repeats(block, local)
            out.append(block)
        return ''.join(out)

    # Loop until stable (handles multiple nesting levels)
    prev = None
    while prev != html:
        prev = html
        html = pat.sub(repl, html)
    return html

# ─────────────────── raw query data ───────────────────

REPORT_DATE = '2026-06-27'

# Query A — daily totals per branch over 30 days (2026-05-29 to 2026-06-27)
# Location 33 = MW1, 105 = SE3, 109 = PKT (no 169 data)
QA = [
    ('2026-05-29', 33, 42210.5),  ('2026-05-29', 105, 22568.0),   ('2026-05-29', 109, 13844.0),
    ('2026-05-30', 33, 34788.0),  ('2026-05-30', 105, 26883.0),   ('2026-05-30', 109, 14605.0),
    ('2026-05-31', 33, 28583.0),  ('2026-05-31', 105, 32544.0),   ('2026-05-31', 109, 14052.0),
    ('2026-06-01', 33, 32133.0),  ('2026-06-01', 105, 24075.0),   ('2026-06-01', 109, 13940.0),
    ('2026-06-02', 33, 36476.0),  ('2026-06-02', 105, 15959.0),   ('2026-06-02', 109, 9920.0),
    ('2026-06-03', 33, 40024.0),  ('2026-06-03', 105, 19497.0),   ('2026-06-03', 109, 10813.0),
    ('2026-06-04', 33, 35666.5),  ('2026-06-04', 105, 16604.0),   ('2026-06-04', 109, 13146.0),
    ('2026-06-05', 33, 35611.0),  ('2026-06-05', 105, 20180.0),   ('2026-06-05', 109, 13589.0),
    ('2026-06-06', 33, 32714.0),  ('2026-06-06', 105, 23312.0),   ('2026-06-06', 109, 13867.0),
    ('2026-06-07', 33, 25977.0),  ('2026-06-07', 105, 17749.0),   ('2026-06-07', 109, 12993.0),
    ('2026-06-08', 33, 38857.0),  ('2026-06-08', 105, 24570.0),   ('2026-06-08', 109, 12810.0),
    ('2026-06-09', 33, 30612.5),  ('2026-06-09', 105, 12035.0),   ('2026-06-09', 109, 10190.0),
    ('2026-06-10', 33, 37665.0),  ('2026-06-10', 105, 22195.0),   ('2026-06-10', 109, 10250.0),
    ('2026-06-11', 33, 36938.0),  ('2026-06-11', 105, 18834.0),   ('2026-06-11', 109, 12373.0),
    ('2026-06-12', 33, 35377.5),  ('2026-06-12', 105, 25627.0),   ('2026-06-12', 109, 11753.0),
    ('2026-06-13', 33, 33715.0),  ('2026-06-13', 105, 25149.0),   ('2026-06-13', 109, 12259.0),
    ('2026-06-14', 33, 36683.0),  ('2026-06-14', 105, 18753.0),   ('2026-06-14', 109, 16361.0),
    ('2026-06-15', 33, 34196.0),  ('2026-06-15', 105, 22469.0),   ('2026-06-15', 109, 12234.0),
    ('2026-06-16', 33, 39711.0),  ('2026-06-16', 105, 19173.0),   ('2026-06-16', 109, 9078.0),
    ('2026-06-17', 33, 37169.0),  ('2026-06-17', 105, 20735.0),   ('2026-06-17', 109, 10010.0),
    ('2026-06-18', 33, 46617.5),  ('2026-06-18', 105, 21253.0),   ('2026-06-18', 109, 14308.0),
    ('2026-06-19', 33, 45531.0),  ('2026-06-19', 105, 32543.0),   ('2026-06-19', 109, 12803.0),
    ('2026-06-20', 33, 32341.0),  ('2026-06-20', 105, 29278.0),   ('2026-06-20', 109, 15844.0),
    ('2026-06-21', 33, 36222.5),  ('2026-06-21', 105, 33130.0),   ('2026-06-21', 109, 7904.0),
    ('2026-06-22', 33, 37555.0),  ('2026-06-22', 105, 25019.5),   ('2026-06-22', 109, 7672.0),
    ('2026-06-23', 33, 36830.0),  ('2026-06-23', 105, 21203.0),   ('2026-06-23', 109, 10066.0),
    ('2026-06-24', 33, 37465.0),  ('2026-06-24', 105, 24795.0),   ('2026-06-24', 109, 8185.0),
    ('2026-06-25', 33, 36247.5),  ('2026-06-25', 105, 21621.0),   ('2026-06-25', 109, 8293.0),
    ('2026-06-26', 33, 36515.5),  ('2026-06-26', 105, 17651.5),   ('2026-06-26', 109, 11643.0),
    ('2026-06-27', 33, 33294.0),  ('2026-06-27', 105, 28583.15),  ('2026-06-27', 109, 10379.0),
]

# Top-20 per branch from Query B (sorted by qty desc, 2026-06-27)
QB_MW1 = [
    ('EVIAN', 36, 4037.40, 5),
    ('WATERMELON 400G.', 11, 1542.09, 2),
    ('3 kinds of fruit400g Papaya/Pineapple/Guava', 7, 981.32, 2),
    ('Mango juice (Bottle) 300 ml', 7, 1210.28, 2),
    ('PRIDE PARROT RED', 6, 1121.52, 2),
    ('P1 GOLDEN GLOW 22OZ', 5, 1030.37, 3),
    ('S5 MANGO SMOOTHIE 22OZ', 5, 864.49, 3),
    ('PAPAYA 400G.', 5, 700.95, 3),
    ('SOFT-SLUSH! ORIGINAL', 5, 747.65, 2),
    ('MANGO 400G.', 5, 747.65, 3),
    ('PRIDE PARROT YELLOW', 5, 934.58, 2),
    ('COCONUT READY TO DRINK', 4, 635.52, 2),
    ('CH1 ESPRESSO', 4, 467.28, 2),
    ('S3 WATERMELON SMOOTHIE 22OZ', 4, 691.60, 2),
    ('WATERMELON JUICE BOTTLE', 4, 691.60, 2),
    ('CI5 ICED LATTE 22OZ', 3, 546.73, 2),
    ('Mango passion juice (Bottle) 300 ml', 3, 518.69, 1),
    ('C3 WATERMELON  COLD PREESED 22OZ', 3, 588.78, 1),
    ('S7 PINEAPPLE SMOOTHIE 22OZ', 3, 518.69, 1),
    ('CH3 HOT CAPPUCCINO', 3, 420.57, 2),
]
QB_SE3 = [
    ('EVIAN', 38, 4261.70, 5),
    ('COCONUT READY TO DRINK', 15, 2383.18, 5),
    ('WATERMELON 400G.', 12, 1682.27, 4),
    ('3 kinds of fruit400g Papaya/Pineapple/Guava', 8, 1121.52, 2),
    ('GUAVA 400G.', 7, 981.31, 3),
    ('PAPAYA 400G.', 7, 981.33, 2),
    ('PINEAPPLE 400G.', 7, 981.33, 2),
    ('S3 WATERMELON SMOOTHIE 16OZ', 6, 897.19, 1),
    ('CI3 ICED AMERICANO 22OZ', 4, 672.89, 3),
    ('S5 MANGO SMOOTHIE 16OZ', 4, 598.12, 2),
    ('CH4 HOT LATTE', 4, 532.72, 2),
    ('S1 COCONUT SMOOTHIE 22OZ', 3, 574.77, 2),
    ('S2 MANGO PASSION SMOOTHIE 16OZ', 3, 448.59, 2),
    ('MANGO JUICE (BOTTLE) 300 ML', 3, 518.68, 1),
    ('C1 GUAVA&GREEN APPLE&RED APPLE COLD PREESED 22OZ', 3, 588.78, 3),
    ('C3 WATERMELON  COLD PREESED 22OZ', 3, 588.78, 2),
    ('S5 MANGO SMOOTHIE 22OZ', 3, 516.97, 1),
    ('S2 MANGO PASSION SMOOTHIE 22OZ', 3, 518.69, 1),
    ('DRAGON FRUIT 400G.', 3, 420.57, 1),
    ('C4 MANGO PASSION  COLD PREESED 16OZ', 3, 518.70, 1),
]
QB_PKT = [
    ('Evian 500ml. (Bottle)', 10, 1121.50, 3),
    ('Mango 400 g. (Pack)', 8, 1196.24, 3),
    ('Chicken Ham Sandwich', 4, 672.88, 2),
    ('Mango Passion Smoothie 22oz', 3, 518.69, 1),
    ('CH2 Caffe latte (hot) 12oz', 3, 404.27, 2),
    ('Coke 500 ml. (Bottle)', 3, 224.31, 2),
    ('S3 watermelon smoothie 16oz', 2, 299.07, 2),
    ('Chicken Sandwich', 2, 285.48, 1),
    ('Coke Zero 500 ml. (Bottle)', 2, 149.53, 1),
    ('Pride Parrot Red Smoothie 22 oz. ', 2, 373.84, 1),
    ('Mango Passion Cold Pressed 22oz', 2, 392.52, 1),
    ('Papaya 400 g. (Pack)', 2, 280.38, 2),
    ('Watermelon 400 g. (Pack)', 2, 280.38, 1),
    ('CH1 Cappuccino (hot) 12oz', 2, 237.88, 1),
    ('Singha Beer 320 ml. (Bottle)\xa0', 1, 168.22, 1),
    ('Coconut (EA)', 1, 158.87, 1),
    ('Guava 400 g. (Pack)', 1, 140.18, 1),
    ('T1 Iced Thai milk tea 16oz', 1, 140.19, 1),
    ('YS3 banana yoghurt smoothie 16oz', 1, 163.55, 1),
    ('S2 mango passion smoothie 16oz', 1, 149.53, 1),
]

# Dormant SKUs (Query D filtered: qty_30d >= 3, no malformed \n memos, no noise)
# (memo, last_sold_str, qty_30d, days_sold_30d, rev_30d)
DORMANT_MW1 = [
    ('ORANGE JUICE BOTTLE',                        '2026-06-20', 55, 13, 9509.39),
    ('Add-on Pearl Jelly',                         '2026-06-20', 17, 10,  571.88),
    ('MAEVAREE MANGO STICKY RICE SMOOTHIE 22OZ',   '2026-06-08', 15,  8, 3202.77),
    ('Overnight Oat mango 16 oz',                  '2026-06-06', 10,  8, 2514.00),
    ('MAEVAREE MANGO YOGHURT STICKY RICE SMOOTHIE 22OZ', '2026-06-12', 8, 5, 1719.60),
    ('BLUEBERRY GREEK YOGURT',                     '2026-06-05',  4,  3,  706.55),
]
DORMANT_SE3 = [
    ('MANGO (1 PCS.) 380 G.',                      '2026-06-18', 26, 12, 3644.90),
    ('Cantaloupe\xa0400 g (Pack)',                  '2026-06-09', 25, 11, 3504.71),
    ('MAEVAREE MANGO STICKY RICE SMOOTHIE 22OZ',   '2026-06-12', 24, 11, 5137.32),
    ('MANGO (2 PCS.) 760 G.',                      '2026-06-18', 16,  8, 4485.94),
    ('MAEVAREE MANGO YOGHURT STICKY RICE SMOTHIE 22OZ', '2026-06-12', 12, 7, 2579.41),
    ('ORANGE JUICE BOTTLE',                        '2026-06-10', 11,  8, 1901.86),
    ('Up size Smoothie & Cold Press',              '2026-06-20',  7,  7,  163.52),
    ('SEEDLESS GRAPE 400G.',                       '2026-06-08',  5,  2,  747.65),
    ('Golden Harmony Greek Yogur',                 '2026-05-31',  4,  2,  706.56),
    ('Overnight Oat mango 16 oz',                  '2026-06-04',  3,  3,  754.20),
]
DORMANT_PKT = [
    ('Indian Tea Ginger Chai 12oz',                    '2026-06-17', 22, 12, 2467.30),
    ('C2 orange cold pressed 16oz',                    '2026-06-19', 19, 10, 3285.10),
    ('Banana 2PCS.',                                   '2026-06-06',  8,  6,  441.12),
    ('Ebiko salad Japanese Rice Balls (Onigiri)',       '2026-06-19',  8,  6,  814.96),
    ('Mango Berry Smoothie 16oz',                      '2026-06-11',  7,  4, 1210.30),
    ('C7 Green Apple & Celery & Pineapple Cold Pressed 16 oz.', '2026-06-18', 5, 5, 864.50),
    ('Pride Parrot Red Smoothie 22 oz.',               '2026-06-05',  4,  2,  747.67),
    ('singha soda water 325ml',                        '2026-06-04',  4,  2,  243.00),
    ('T2 Iced Thai tea with lime 16oz',                '2026-06-11',  3,  2,  420.57),
]

# ─────────────────── computations ───────────────────

from datetime import date, timedelta
import math

report_date  = date(2026, 6, 27)
run_date     = date(2026, 6, 28)
window_start = report_date - timedelta(days=29)  # 2026-05-29

# Build day-keyed lookup for QA
from collections import defaultdict
daily = defaultdict(lambda: {33: 0.0, 105: 0.0, 109: 0.0})
for d_str, loc, net in QA:
    d = date.fromisoformat(d_str)
    daily[d][33 if loc == 33 else (105 if loc == 105 else 109)] += net

dates_sorted = sorted(daily.keys())  # 30 dates

mw1  = {d: daily[d][33]  for d in dates_sorted}
se3  = {d: daily[d][105] for d in dates_sorted}
pkt  = {d: daily[d][109] for d in dates_sorted}
comb = {d: mw1[d] + se3[d] + pkt[d] for d in dates_sorted}

# Yesterday
yest = report_date
mw1_yest  = mw1[yest];  se3_yest = se3[yest];  pkt_yest = pkt[yest]
comb_yest = mw1_yest + se3_yest + pkt_yest

# 30-day averages
mw1_avg  = sum(mw1.values())  / 30
se3_avg  = sum(se3.values())  / 30
pkt_avg  = sum(pkt.values())  / 30
comb_avg = mw1_avg + se3_avg + pkt_avg

mw1_min = min(mw1.values());  mw1_max = max(mw1.values())
se3_min = min(se3.values());  se3_max = max(se3.values())
pkt_min = min(pkt.values());  pkt_max = max(pkt.values())

signed_pct = (comb_yest - comb_avg) / comb_avg * 100
mw1_vs30   = (mw1_yest - mw1_avg)  / mw1_avg  * 100
se3_vs30   = (se3_yest - se3_avg)  / se3_avg  * 100
pkt_vs30   = (pkt_yest - pkt_avg)  / pkt_avg  * 100

subject_prefix = ('🔥' if signed_pct >= 10 else ('⚠️' if signed_pct <= -10 else '✅'))

chart_max = max(max(mw1.values()), max(se3.values()), max(pkt.values()))

def fmt(n, decimals=0):
    if decimals == 0:
        return f'{round(n):,}'
    return f'{n:,.{decimals}f}'

def bar(n): return str(round(n / chart_max * 220))

TH_WD      = ['จ','อ','พ','พฤ','ศ','ส','อา']
TH_WD_FULL = ['วันจันทร์','วันอังคาร','วันพุธ','วันพฤหัสบดี','วันศุกร์','วันเสาร์','วันอาทิตย์']
EN_MONTH      = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
EN_MONTH_FULL = ['January','February','March','April','May','June',
                 'July','August','September','October','November','December']

def th_weekday_abbr(d): return TH_WD[d.weekday()]
def en_day_display(d): return f'{d.day} {EN_MONTH_FULL[d.month-1]}'

report_date_display     = f'{report_date.day} {EN_MONTH_FULL[report_date.month-1]} {report_date.year}'
report_day_th           = TH_WD_FULL[report_date.weekday()]
window_30d_start_display = f'{window_start.day} {EN_MONTH_FULL[window_start.month-1]} {window_start.year}'

# Last 7 days (Jun 21-27)
last7_dates  = dates_sorted[-7:]

# 7-day totals
mw1_7d   = sum(mw1[d] for d in last7_dates)
se3_7d   = sum(se3[d] for d in last7_dates)
pkt_7d   = sum(pkt[d] for d in last7_dates)
comb_7d  = mw1_7d + se3_7d + pkt_7d
last7_avg_val = comb_7d / 7

# ─── FORECAST (today = Sunday 2026-06-28) ───
fc_date = run_date  # Sunday

def same_wday_history(branch_dict, target_date, weeks=4):
    vals = []
    d = target_date - timedelta(weeks=1)
    while len(vals) < weeks:
        if d in branch_dict:
            vals.append(branch_dict[d])
        d -= timedelta(weeks=1)
    return vals

mw1_sun = same_wday_history(mw1, fc_date)
se3_sun = same_wday_history(se3, fc_date)
pkt_sun = same_wday_history(pkt, fc_date)

def forecast_branch(sun_vals, branch_vals, all_dates):
    base      = sum(sun_vals) / len(sun_vals) if sun_vals else 0
    last7_vals = [branch_vals[d] for d in all_dates[-7:]]
    trend_adj = (base + sum(last7_vals) / 7) / 2
    stdev     = math.sqrt(sum((x - base)**2 for x in sun_vals) / len(sun_vals)) if len(sun_vals) > 1 else base * 0.12
    band      = max(stdev, trend_adj * 0.08)
    conf_pct  = stdev / base * 100 if base else 25
    if conf_pct < 12:   conf_dot = '🟢'
    elif conf_pct < 25: conf_dot = '🟡'
    else:               conf_dot = '🔴'
    return trend_adj, band, conf_dot

mw1_fc, mw1_band, mw1_conf = forecast_branch(mw1_sun, mw1, dates_sorted)
se3_fc, se3_band, se3_conf = forecast_branch(se3_sun, se3, dates_sorted)
pkt_fc, pkt_band, pkt_conf = forecast_branch(pkt_sun, pkt, dates_sorted)

comb_fc       = mw1_fc + se3_fc + pkt_fc
comb_band     = math.sqrt(mw1_band**2 + se3_band**2 + pkt_band**2)
comb_conf_pct = comb_band / comb_fc * 100 if comb_fc else 25
comb_conf     = '🟢' if comb_conf_pct < 12 else ('🟡' if comb_conf_pct < 25 else '🔴')

# SE3 is 🔴 (high variance Sundays: 33130/18753/17749/32544) → forecast_suppressed = True
forecast_suppressed = (se3_conf == '🔴')

# ─── NEW PRODUCTS (from Query C, 30d window, exclusions applied) ───
# Excluded: malformed "DRAGON FRUIT 400G.3 KINDS OF FRUIT400G..." and "ICE 16OZ"
# Buckets: Seasonal Fruits (400G/PACK/fruit keywords), New Category (TOPPING keywords), Drinks (default)

NP_DRINKS_ROWS = [
    {'memo': 'PRIDE PARROT RED', 'launch': '1 Jun',
     'notes': '27d live · MW1+SE3', 'total_units': 288, 'total_rev': '53,758',
     'branch_split': 'MW1:189 · SE3:99', 'yest_units': 8, 'status_badge': '🟢 on target'},
    {'memo': 'PRIDE PARROT YELLOW', 'launch': '1 Jun',
     'notes': '27d live · MW1+SE3', 'total_units': 179, 'total_rev': '33,421',
     'branch_split': 'MW1:118 · SE3:61', 'yest_units': 7, 'status_badge': '🟢 on target'},
    {'memo': 'MOOVE CLEAR PROTEIN', 'launch': '13 Jun',
     'notes': '15d live · MW1 only', 'total_units': 40, 'total_rev': '5,608',
     'branch_split': 'MW1:40', 'yest_units': 0, 'status_badge': '🟠 stock-out suspect (3d gap)'},
    {'memo': 'FANTA ORANGE 450 ML. (BOTTLE)', 'launch': '31 May',
     'notes': '28d live · PKT only', 'total_units': 28, 'total_rev': '2,094',
     'branch_split': 'PKT:28', 'yest_units': 0, 'status_badge': '🔴 waste risk'},
    {'memo': 'SPRITE 500 ML. (BOTTLE)', 'launch': '30 May',
     'notes': '29d live · PKT only', 'total_units': 27, 'total_rev': '2,019',
     'branch_split': 'PKT:27', 'yest_units': 1, 'status_badge': '🔴 waste risk'},
    {'memo': 'FANTA STRAWBERRY 450 ML. (BOTTLE)', 'launch': '1 Jun',
     'notes': '27d live · PKT only', 'total_units': 26, 'total_rev': '1,944',
     'branch_split': 'PKT:26', 'yest_units': 1, 'status_badge': '🔴 waste risk'},
    {'memo': 'PRIDE PARROT RED SMOOTHIE 22 OZ.', 'launch': '4 Jun',
     'notes': '24d live · PKT only', 'total_units': 23, 'total_rev': '4,299',
     'branch_split': 'PKT:23', 'yest_units': 2, 'status_badge': '🔴 waste risk'},
    {'memo': 'PRIDE PARROT YELLOW SMOOTHIE 22 OZ.', 'launch': '7 Jun',
     'notes': '21d live · PKT only', 'total_units': 10, 'total_rev': '1,869',
     'branch_split': 'PKT:10', 'yest_units': 0, 'status_badge': '🟠 stock-out suspect (4d gap)'},
    {'memo': 'GRAPE CLEAR PROTEIN', 'launch': '25 Jun',
     'notes': '3d live · MW1+SE3', 'total_units': 9, 'total_rev': '1,262',
     'branch_split': 'MW1:8 · SE3:1', 'yest_units': 3, 'status_badge': '🔴 waste risk'},
    {'memo': 'LYCHEE CLEAR PROTEIN', 'launch': '25 Jun',
     'notes': '3d live · MW1+SE3', 'total_units': 6, 'total_rev': '841',
     'branch_split': 'MW1:2 · SE3:4', 'yest_units': 1, 'status_badge': '🔴 waste risk'},
    {'memo': 'MANGO PASSION SMOOTHIE 22OZ', 'launch': '25 Jun',
     'notes': '3d live · PKT only', 'total_units': 6, 'total_rev': '1,037',
     'branch_split': 'PKT:6', 'yest_units': 3, 'status_badge': '🔴 waste risk'},
    {'memo': 'MANGO YOGHURT SMOOTHIE 22 OZ', 'launch': '23 Jun',
     'notes': '5d live · PKT only', 'total_units': 4, 'total_rev': '748',
     'branch_split': 'PKT:4', 'yest_units': 0, 'status_badge': '🟠 stock-out suspect (2d gap)'},
    {'memo': 'MANGO PASSION COLD PRESSED 22OZ', 'launch': '25 Jun',
     'notes': '3d live · PKT only', 'total_units': 3, 'total_rev': '589',
     'branch_split': 'PKT:3', 'yest_units': 2, 'status_badge': '🔴 waste risk'},
    {'memo': 'WATERMELON SMOOTHIE 22OZ', 'launch': '23 Jun',
     'notes': '5d live · PKT only', 'total_units': 3, 'total_rev': '519',
     'branch_split': 'PKT:3', 'yest_units': 0, 'status_badge': '🟠 stock-out suspect (4d gap)'},
    {'memo': 'HOT TEA GREEN TEA 12OZ', 'launch': '18 Jun',
     'notes': '10d live · PKT only', 'total_units': 2, 'total_rev': '204',
     'branch_split': 'PKT:2', 'yest_units': 1, 'status_badge': '🔴 waste risk'},
    {'memo': 'MANGO SMOOTHIE 22OZ', 'launch': '24 Jun',
     'notes': '4d live · PKT only', 'total_units': 2, 'total_rev': '346',
     'branch_split': 'PKT:2', 'yest_units': 0, 'status_badge': '🟠 stock-out suspect (3d gap)'},
    {'memo': 'MIXBERRY SMOOTHIE 22OZ', 'launch': '24 Jun',
     'notes': '4d live · PKT only', 'total_units': 2, 'total_rev': '346',
     'branch_split': 'PKT:2', 'yest_units': 0, 'status_badge': '🟠 stock-out suspect (3d gap)'},
    {'memo': 'PINEAPPLE & GREEN APPLE COLD PRESSED 22OZ', 'launch': '26 Jun',
     'notes': '2d live · PKT only', 'total_units': 2, 'total_rev': '393',
     'branch_split': 'PKT:2', 'yest_units': 1, 'status_badge': '🔴 waste risk'},
    {'memo': 'STRAWBERRY YOGHURT SMOOTHIE 22 OZ', 'launch': '25 Jun',
     'notes': '3d live · PKT only', 'total_units': 2, 'total_rev': '374',
     'branch_split': 'PKT:2', 'yest_units': 1, 'status_badge': '🔴 waste risk'},
    {'memo': 'ICED CAPPUCCINO 22OZ', 'launch': '25 Jun',
     'notes': '3d live · PKT only', 'total_units': 2, 'total_rev': '314',
     'branch_split': 'PKT:2', 'yest_units': 0, 'status_badge': '🟠 stock-out suspect (2d gap)'},
    {'memo': 'COCONUT SMOOTHIE 22OZ', 'launch': '25 Jun',
     'notes': '3d live · PKT only', 'total_units': 1, 'total_rev': '192',
     'branch_split': 'PKT:1', 'yest_units': 0, 'status_badge': '🟠 stock-out suspect (2d gap)'},
    {'memo': 'ICED LATTE 22OZ', 'launch': '23 Jun',
     'notes': '5d live · PKT only', 'total_units': 1, 'total_rev': '182',
     'branch_split': 'PKT:1', 'yest_units': 0, 'status_badge': '🟠 stock-out suspect (4d gap)'},
    {'memo': 'ORANGE COLD PRESSED 22OZ', 'launch': '24 Jun',
     'notes': '4d live · PKT only', 'total_units': 1, 'total_rev': '196',
     'branch_split': 'PKT:1', 'yest_units': 0, 'status_badge': '🟠 stock-out suspect (3d gap)'},
    {'memo': 'PINEAPPLE SMOOTHIE 22OZ', 'launch': '27 Jun',
     'notes': '1d live · PKT only', 'total_units': 1, 'total_rev': '173',
     'branch_split': 'PKT:1', 'yest_units': 1, 'status_badge': '⚪ new — 1 sale'},
    {'memo': 'ICED THAI MILK TEA 22OZ', 'launch': '25 Jun',
     'notes': '3d live · PKT only', 'total_units': 1, 'total_rev': '164',
     'branch_split': 'PKT:1', 'yest_units': 0, 'status_badge': '🟠 stock-out suspect (2d gap)'},
    {'memo': 'ICED THAI TEA WITH LIME 22OZ', 'launch': '25 Jun',
     'notes': '3d live · PKT only', 'total_units': 1, 'total_rev': '164',
     'branch_split': 'PKT:1', 'yest_units': 0, 'status_badge': '🟠 stock-out suspect (2d gap)'},
    {'memo': 'FANTA FRUIT PUNCH 450 ML. (BOTTLE)', 'launch': '31 May',
     'notes': '28d live · PKT only', 'total_units': 1, 'total_rev': '75',
     'branch_split': 'PKT:1', 'yest_units': 0, 'status_badge': '🟠 stock-out suspect (27d gap)'},
    {'memo': 'ICED ESPRESSO ORANGE 12OZ', 'launch': '29 May',
     'notes': '30d live · SE3 only', 'total_units': 1, 'total_rev': '168',
     'branch_split': 'SE3:1', 'yest_units': 0, 'status_badge': '🟠 stock-out suspect (29d gap)'},
]

NP_FRUIT_ROWS = [
    {'memo': 'LYCHEE 400G.', 'launch': '28 May',
     'notes': '31d live · MW1+SE3', 'total_units': 62, 'total_rev': '9,851',
     'branch_split': 'MW1:19 · SE3:43', 'yest_units': 2, 'status_badge': '🟢 on target'},
    {'memo': 'ORANGE 400 G (PACK)', 'launch': '18 Jun',
     'notes': '10d live · SE3 only', 'total_units': 18, 'total_rev': '2,523',
     'branch_split': 'SE3:18', 'yest_units': 0, 'status_badge': '🟠 stock-out suspect (4d gap)'},
    {'memo': 'ROSE APPLE 400G.', 'launch': '30 May',
     'notes': '29d live · MW1+SE3', 'total_units': 22, 'total_rev': '3,290',
     'branch_split': 'MW1:2 · SE3:20', 'yest_units': 0, 'status_badge': '🟠 stock-out suspect (3d gap)'},
    {'memo': 'MANGOSTEEN 400G.', 'launch': '28 May',
     'notes': '31d live · MW1+SE3', 'total_units': 6, 'total_rev': '1,402',
     'branch_split': 'MW1:3 · SE3:3', 'yest_units': 0, 'status_badge': '🟠 stock-out suspect (4d gap)'},
]

NP_NEWCAT_ROWS = [
    {'memo': 'SEEDLESS GRAPE TOPPING', 'launch': '5 Jun',
     'notes': '23d live · MW1 only', 'total_units': 1, 'total_rev': '23',
     'branch_split': 'MW1:1', 'yest_units': 0, 'status_badge': '🟠 stock-out suspect (22d gap)'},
    {'memo': 'BANANA TOPPING', 'launch': '12 Jun',
     'notes': '16d live · MW1 only', 'total_units': 1, 'total_rev': '23',
     'branch_split': 'MW1:1', 'yest_units': 0, 'status_badge': '🟠 stock-out suspect (15d gap)'},
    {'memo': 'DRAGON FRUIT TOPPING', 'launch': '19 Jun',
     'notes': '9d live · MW1 only', 'total_units': 1, 'total_rev': '23',
     'branch_split': 'MW1:1', 'yest_units': 0, 'status_badge': '🟠 stock-out suspect (8d gap)'},
]

# Bucket totals
drinks_n           = len(NP_DRINKS_ROWS)   # 28
drinks_total_units = sum(r['total_units'] for r in NP_DRINKS_ROWS)  # 672
drinks_total_rev   = 113299
drinks_yest_units  = sum(r['yest_units'] for r in NP_DRINKS_ROWS)   # 32
drinks_yest_rev    = 5458

fruit_n           = len(NP_FRUIT_ROWS)    # 4
fruit_total_units = sum(r['total_units'] for r in NP_FRUIT_ROWS)   # 108
fruit_total_rev   = 17066
fruit_yest_units  = sum(r['yest_units'] for r in NP_FRUIT_ROWS)    # 2
fruit_yest_rev    = 318

new_cat_n           = len(NP_NEWCAT_ROWS)  # 3
new_cat_total_units = sum(r['total_units'] for r in NP_NEWCAT_ROWS)  # 3
new_cat_total_rev   = 69
new_cat_yest_units  = sum(r['yest_units'] for r in NP_NEWCAT_ROWS)   # 0
new_cat_yest_rev    = 0

np_total_units = drinks_total_units + fruit_total_units + new_cat_total_units  # 783
np_total_rev   = drinks_total_rev + fruit_total_rev + new_cat_total_rev        # 130,434

# ─── SEASONAL (Query E) ───
grape_total_rev = 238740   # SHINE MUSCAT both branches
grape_last_mw1  = '27 Jun 2026'   # SEEDLESS GRAPE 400G. still active at MW1
grape_last_se3  = '8 Jun 2026'    # SEEDLESS GRAPE 400G. dormant at SE3

# New fruit revenue in 30d window from Query C
mw1_fruit_rev = 3019.0 + 701.0 + 299.0        # LYCHEE + MANGOSTEEN + ROSE APPLE
se3_fruit_rev = 6832.0 + 701.0 + 2991.0 + 2523.0  # LYCHEE + MANGOSTEEN + ROSE APPLE + ORANGE 400G

mw1_fruit_per_day = mw1_fruit_rev / 30   # 133.97/d
se3_fruit_per_day = se3_fruit_rev / 30   # 434.90/d

mw1_grape_baseline = 339   # hardcoded reference from queries.md
se3_grape_baseline = 251

mw1_coverage = mw1_fruit_per_day / mw1_grape_baseline * 100   # ~39.5%
se3_coverage = se3_fruit_per_day / se3_grape_baseline * 100   # ~173.3%

def coverage_color(pct):
    if pct >= 100: return '#155724'
    if pct >= 70:  return '#856404'
    return '#721C24'

def coverage_bg(pct):
    if pct >= 100: return '#D4EDDA'
    if pct >= 70:  return '#FFF3CD'
    return '#F8D7DA'

def coverage_badge(pct):
    if pct >= 100: return '✅ Fully replaced — new fruits exceed grape baseline'
    if pct >= 70:  return '🟡 Partial — monitor'
    return '🔴 Large gap — push promotion or add SKU'

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

dormant_count = len(DORMANT_MW1) + len(DORMANT_SE3) + len(DORMANT_PKT)  # 25

# ─── AM REVIEW ITEMS (6 MW1 dormant, high-priority) ───
am_queue_count = len(DORMANT_MW1)  # 6

def am_row(memo, last_sold_str, qty_30d, days_sold_30d, rev_30d):
    g = gap_days(last_sold_str)
    hist_target = round(qty_30d / max(days_sold_30d, 1), 1)
    ls_d = date.fromisoformat(last_sold_str)
    ls_display = f'{ls_d.day} {EN_MONTH[ls_d.month-1]}'
    v7 = 0.0  # all dormant, no sales in last 7 days
    color = gap_color(g)
    if g >= 14:
        hyp = 'Likely discontinued or stockout >2 weeks — needs AM decision'
    else:
        hyp = f'Possible stock-out at MW1 — {g}d gap since last sale'
    return {
        'memo':             truncate(memo, 40),
        'last_sold':        ls_display,
        'gap_days':         str(g),
        'velocity_7d':      '0.0',
        'target':           str(hist_target),
        'branch_split':     'MW1',
        'hypothesis_color': color,
        'hypothesis_text':  hyp,
    }

am_items = [am_row(*row) for row in DORMANT_MW1]

# ─── PREDICTION scalars ───
commentary_text = (
    f'Yesterday (27 June 2026 · วันเสาร์), combined net was ฿{fmt(comb_yest)} ex-VAT, '
    f'{abs(signed_pct):.1f}% {"above" if signed_pct >= 0 else "below"} the 30-day average. '
    f'MW1 came in at ฿{fmt(mw1_yest)} ({mw1_vs30:+.1f}% vs avg), '
    f'SE3 at ฿{fmt(se3_yest)} ({se3_vs30:+.1f}% vs avg — SE3\'s strongest Saturday in the window), '
    f'PKT at ฿{fmt(pkt_yest)} ({pkt_vs30:+.1f}% vs avg). '
    f'SE3\'s strong Saturday performance offset softer results at MW1 and PKT.'
)

anomaly_items = [
    {'anomaly_text': f'SE3 +25.4% vs 30d avg (฿28,583) — best Saturday in the report window; monitor next Saturday for trend confirmation.',
     'anomaly_section_ref': 'Chart §3'},
    {'anomaly_text': f'PKT -12.3% vs 30d avg (฿10,379) — below threshold; Saturday usually weaker at PKT.',
     'anomaly_section_ref': 'Chart §3'},
    {'anomaly_text': f'MW1: 6 dormant SKUs incl. ORANGE JUICE BOTTLE (7d gap, ฿9,509 in 30d) — AM review required.',
     'anomaly_section_ref': 'AM Review §2 + Dormant §7'},
    {'anomaly_text': f'SE3: 10 dormant SKUs incl. MANGO 380G, Cantaloupe, MAEVAREE lines — high-value items stopped selling.',
     'anomaly_section_ref': 'Dormant §7'},
    {'anomaly_text': f'Seasonal fruit: MW1 coverage only 40% of grape baseline (🔴 large gap); SE3 at 173% (✅).',
     'anomaly_section_ref': 'Seasonal Tracker §6'},
    {'anomaly_text': f'PKT added 15+ new smoothie/cold-press names (Jun 23-27) — most show 🟠/🔴 status; expected for very new items.',
     'anomaly_section_ref': 'New Products §4'},
]

# ─────────────────── build repeats ───────────────────

# chart_days
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

# last7_headers
last7_headers = []
for i, d in enumerate(last7_dates):
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

# top20 per branch
def top20_rows(items):
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
    {
        'header_color': '#5551FE',
        'header_label': 'MW1 · 26-T1MW1-03+04',
        'top20_rows':   top20_rows(QB_MW1),
    },
    {
        'header_color': '#F27061',
        'header_label': 'SE3 · 27-T1SE3-05',
        'top20_rows':   top20_rows(QB_SE3),
    },
    {
        'header_color': '#2E7D32',
        'header_label': 'PKT · 28 Unit 362 (Phuket)',
        'top20_rows':   top20_rows(QB_PKT),
    },
]

# np_type_tables
np_type_tables = [
    {
        'type_bg':    '#1976D2',
        'type_fg':    '#fff',
        'type_icon':  '🥤',
        'type_label': 'Drinks',
        'np_rows':    NP_DRINKS_ROWS,
    },
    {
        'type_bg':    '#AD1457',
        'type_fg':    '#fff',
        'type_icon':  '🍉',
        'type_label': 'Seasonal Fruits',
        'np_rows':    NP_FRUIT_ROWS,
    },
    {
        'type_bg':    '#2E7D32',
        'type_fg':    '#fff',
        'type_icon':  '⭐',
        'type_label': 'New Category',
        'np_rows':    NP_NEWCAT_ROWS,
    },
]

# seasonal_skus
seasonal_skus = [
    {'fruit_emoji': '🍈', 'memo': 'LYCHEE 400G.', 'launch': '28 May 2026',
     'mw1_units': '19', 'mw1_per_day': f'{3019/30:.0f}',
     'se3_units': '43', 'se3_per_day': f'{6832/30:.0f}'},
    {'fruit_emoji': '🟣', 'memo': 'MANGOSTEEN 400G.', 'launch': '28 May 2026',
     'mw1_units': '3', 'mw1_per_day': f'{701/30:.0f}',
     'se3_units': '3', 'se3_per_day': f'{701/30:.0f}'},
    {'fruit_emoji': '🌸', 'memo': 'ROSE APPLE 400G.', 'launch': '30 May 2026',
     'mw1_units': '2', 'mw1_per_day': f'{299/30:.0f}',
     'se3_units': '20', 'se3_per_day': f'{2991/30:.0f}'},
    {'fruit_emoji': '🍊', 'memo': 'ORANGE 400 G (PACK)', 'launch': '18 Jun 2026',
     'mw1_units': '—', 'mw1_per_day': '0',
     'se3_units': '18', 'se3_per_day': f'{2523/30:.0f}'},
]

# seasonal_coverage
def se3_gap_display(baseline, per_day):
    if per_day >= baseline:
        return 'Surplus vs baseline'
    return f'฿{fmt(round(baseline - per_day))}/d'

def se3_impact_display(baseline, per_day):
    if per_day >= baseline:
        return f'+฿{fmt(round((per_day - baseline)*30))}/month surplus'
    return f'-฿{fmt(round((baseline - per_day)*30))}/month'

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
        'daily_gap':         se3_gap_display(se3_grape_baseline, se3_fruit_per_day),
        'monthly_impact':    se3_impact_display(se3_grape_baseline, se3_fruit_per_day),
        'badge_bg':          coverage_bg(se3_coverage),
        'badge_text':        coverage_badge(se3_coverage),
    },
]

# dormant_branches (nested dormant_rows per branch)
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
    'report_date':           REPORT_DATE,
    'report_date_display':   report_date_display,
    'report_day_th':         report_day_th,
    'window_30d_start':      window_30d_start_display,
    'generated_timestamp':   '2026-06-28 07:00',
    'subject_prefix':        subject_prefix,
    'comb_net':              fmt(comb_yest),
    'signed_pct':            f'{signed_pct:+.1f}',
    'am_queue_count':        str(am_queue_count),
    'dormant_count':         str(dormant_count),
    'mw1_avg_30d':           fmt(mw1_avg),
    'se3_avg_30d':           fmt(se3_avg),
    'pkt_avg_30d':           fmt(pkt_avg),
    'comb_avg_30d':          fmt(comb_avg),
    'mw1_min_30d':           fmt(mw1_min),
    'mw1_max_30d':           fmt(mw1_max),
    'se3_min_30d':           fmt(se3_min),
    'se3_max_30d':           fmt(se3_max),
    'pkt_min_30d':           fmt(pkt_min),
    'pkt_max_30d':           fmt(pkt_max),
    'comb_monthly_runrate':  f'{comb_avg*30/1000:,.1f}K',
    'last7_total':           fmt(comb_7d),
    'last7_avg':             fmt(last7_avg_val),
    'mw1_7d_total':          fmt(mw1_7d),
    'se3_7d_total':          fmt(se3_7d),
    'pkt_7d_total':          fmt(pkt_7d),
    'comb_7d_total':         fmt(comb_7d),
    'np_summary_line':       f'35 new SKUs launched May–Jun 2026 · Drinks · Seasonal Fruits · New Category',
    'np_total_units':        str(np_total_units),
    'np_total_rev':          fmt(np_total_rev),
    'drinks_n':              str(drinks_n),
    'drinks_todate_units':   str(drinks_total_units),
    'drinks_todate_rev':     fmt(drinks_total_rev),
    'fruit_n':               str(fruit_n),
    'fruit_todate_units':    str(fruit_total_units),
    'fruit_todate_rev':      fmt(fruit_total_rev),
    'new_cat_n':             str(new_cat_n),
    'new_cat_todate_units':  str(new_cat_total_units),
    'new_cat_todate_rev':    fmt(new_cat_total_rev),
    'grape_total_rev':       fmt(grape_total_rev),
    'grape_last_mw1':        grape_last_mw1,
    'grape_last_se3':        grape_last_se3,
    # Forecast
    'forecast_date_display': f'{run_date.day} {EN_MONTH_FULL[run_date.month-1]} {run_date.year}',
    'mw1_conf_dot':          mw1_conf,
    'se3_conf_dot':          se3_conf,
    'pkt_conf_dot':          pkt_conf,
    'comb_conf_dot':         comb_conf,
    'mw1_fc_low':            fmt(mw1_fc - mw1_band),
    'mw1_fc_high':           fmt(mw1_fc + mw1_band),
    'se3_fc_low':            fmt(se3_fc - se3_band),
    'se3_fc_high':           fmt(se3_fc + se3_band),
    'pkt_fc_low':            fmt(pkt_fc - pkt_band),
    'pkt_fc_high':           fmt(pkt_fc + pkt_band),
    'comb_fc_low':           fmt(comb_fc - comb_band),
    'comb_fc_high':          fmt(comb_fc + comb_band),
    'commentary_text':       commentary_text,
    'anomaly_count':         str(len(anomaly_items)),
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
    'am_items':          am_items,
}

sections = {
    'am_review':           True,
    'seasonal':            True,
    'dormant':             True,
    'forecast_shown':      True,
    'forecast_suppressed': forecast_suppressed,
    'anomaly_shown':       True,
}

# ─────────────────── read templates & build ───────────────────

import os
base = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(base, 'juiceland-template.html'), encoding='utf-8') as f:
    main_tpl = f.read()

with open(os.path.join(base, 'juiceland-prediction-section.html'), encoding='utf-8') as f:
    pred_tpl = f.read()

# Fill prediction section
pred_html = fill(pred_tpl, scalars, repeats, sections)

# Inject prediction section at top of body (just after <div style="padding:24px;">)
inject_marker = '<div style="padding:24px;">'
main_tpl = main_tpl.replace(inject_marker, inject_marker + '\n' + pred_html, 1)

# Fill main template
html = fill(main_tpl, scalars, repeats, sections)

out_path = os.path.join(base, 'email.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'email.html written ({len(html):,} bytes)', file=sys.stderr)
print('OK')
