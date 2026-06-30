#!/usr/bin/env python3
"""
Build Juiceland Daily Sales Report email.html from query results.
Handles nested REPEATs correctly (fill_template.py cannot due to shared global repeat context).
Reads juiceland-template.html + juiceland-prediction-section.html, writes email.html.

Report date: 2026-06-29 (yesterday Asia/Bangkok)
Run date:    2026-06-30
"""
import re, sys, math

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

REPORT_DATE = '2026-06-29'

# Query A — daily totals per branch 2026-05-31 to 2026-06-29
# Location 33=MW1, 105=SE3, 109=PKT
QA = [
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
    ('2026-06-12', 33, 35377.5),  ('2026-06-12', 105, 25627.0),  ('2026-06-12', 109, 11753.0),
    ('2026-06-13', 33, 33715.0),  ('2026-06-13', 105, 25149.0),  ('2026-06-13', 109, 12259.0),
    ('2026-06-14', 33, 36683.0),  ('2026-06-14', 105, 18753.0),  ('2026-06-14', 109, 16361.0),
    ('2026-06-15', 33, 34196.0),  ('2026-06-15', 105, 22469.0),  ('2026-06-15', 109, 12234.0),
    ('2026-06-16', 33, 39711.0),  ('2026-06-16', 105, 19173.0),  ('2026-06-16', 109, 9078.0),
    ('2026-06-17', 33, 37169.0),  ('2026-06-17', 105, 20735.0),  ('2026-06-17', 109, 10010.0),
    ('2026-06-18', 33, 46617.5),  ('2026-06-18', 105, 21253.0),  ('2026-06-18', 109, 14308.0),
    ('2026-06-19', 33, 45531.0),  ('2026-06-19', 105, 32543.0),  ('2026-06-19', 109, 12803.0),
    ('2026-06-20', 33, 32341.0),  ('2026-06-20', 105, 29278.0),  ('2026-06-20', 109, 15844.0),
    ('2026-06-21', 33, 36222.5),  ('2026-06-21', 105, 33130.0),  ('2026-06-21', 109, 7904.0),
    ('2026-06-22', 33, 37555.0),  ('2026-06-22', 105, 25019.5),  ('2026-06-22', 109, 7672.0),
    ('2026-06-23', 33, 36830.0),  ('2026-06-23', 105, 21203.0),  ('2026-06-23', 109, 10066.0),
    ('2026-06-24', 33, 37465.0),  ('2026-06-24', 105, 24795.0),  ('2026-06-24', 109, 8185.0),
    ('2026-06-25', 33, 36247.5),  ('2026-06-25', 105, 21621.0),  ('2026-06-25', 109, 8293.0),
    ('2026-06-26', 33, 36515.5),  ('2026-06-26', 105, 17724.5),  ('2026-06-26', 109, 11868.0),
    ('2026-06-27', 33, 33294.0),  ('2026-06-27', 105, 28583.15), ('2026-06-27', 109, 10604.0),
    ('2026-06-28', 33, 33438.5),  ('2026-06-28', 105, 30919.0),  ('2026-06-28', 109, 8779.0),
    ('2026-06-29', 33, 37725.0),  ('2026-06-29', 105, 28374.0),  ('2026-06-29', 109, 13915.5),
]

# Query B — Top 20 per branch on 2026-06-29 (memo, qty, revenue, bills)
QB_MW1 = [
    ('EVIAN', 43, 4822.45, 5),
    ('S3 WATERMELON SMOOTHIE 22OZ', 10, 1728.98, 2),
    ('3 kinds of fruit400g Papaya/Pineapple/Guava', 10, 1401.9, 3),
    ('COCONUT READY TO DRINK', 10, 1588.8, 2),
    ('P1 GOLDEN GLOW 22OZ', 9, 1892.52, 1),
    ('CH3 HOT CAPPUCCINO', 7, 981.32, 1),
    ('PAPAYA 400G.', 7, 981.33, 1),
    ('COCONUT JUICE BOTTLE', 6, 1037.39, 2),
    ('WATERMELON 400G.', 6, 841.13, 2),
    ('CI3 ICED AMERICANO 22OZ', 5, 841.10, 3),
    ('PRIDE PARROT RED', 4, 747.67, 1),
    ('WATERMELON JUICE BOTTLE', 4, 691.58, 2),
    ('MANGO 400G.', 4, 598.12, 2),
    ('S5 MANGO SMOOTHIE 22OZ', 4, 691.59, 2),
    ('CH4 HOT LATTE', 4, 560.76, 3),
    ('CI3 ICED AMERICANO 16OZ', 4, 579.44, 2),
    ('PINEAPPLE 400G.', 3, 420.56, 1),
    ('CH1 ESPRESSO', 3, 350.46, 2),
    ('PRIDE PARROT YELLOW', 3, 560.75, 1),
    ('S6 BANANA SMOOTHIE 22OZ', 3, 518.70, 3),
]
QB_SE3 = [
    ('EVIAN', 36, 4037.40, 3),
    ('COCONUT READY TO DRINK', 18, 2859.83, 4),
    ('WATERMELON 400G.', 15, 2102.82, 3),
    ('MANGO 400G.', 14, 2093.43, 3),
    ('PINEAPPLE 400G.', 13, 1822.46, 2),
    ('3 kinds of fruit400g Papaya/Pineapple/Guava', 7, 981.33, 2),
    ('P1 GOLDEN GLOW 22OZ', 5, 1051.40, 3),
    ('S2 MANGO PASSION SMOOTHIE 22OZ', 5, 864.49, 1),
    ('S2 MANGO PASSION SMOOTHIE 16OZ', 4, 598.12, 2),
    ('S3 WATERMELON SMOOTHIE 16OZ', 3, 448.60, 2),
    ('S5 MANGO SMOOTHIE 16OZ', 3, 448.60, 1),
    ('YS2 STRAWBERRY YOGHURT SMOOTHIE 16OZ', 3, 490.65, 2),
    ('S1 COCONUT SMOOTHIE 16OZ', 3, 504.66, 2),
    ('C4 MANGO PASSION COLD PRESSED 16OZ', 3, 518.70, 2),
    ('S4 MIXBERRY SMOOTHIE 16OZ', 3, 448.60, 1),
    ('S1 COCONUT SMOOTHIE 22OZ', 2, 383.18, 2),
    ('LYCHEE 400G.', 2, 317.76, 2),
    ('PRIDE PARROT RED', 2, 373.84, 2),
    ('C3 WATERMELON COLD PRESSED 16OZ', 2, 345.79, 2),
    ('C2 ORANGE COLD PRESSED 22OZ', 2, 392.52, 2),
]
QB_PKT = [
    ('Evian 500ml. (Bottle)', 16, 1794.40, 2),
    ('CH2 Caffe latte (hot) 12oz', 5, 700.94, 3),
    ('Mango 400 g. (Pack)', 5, 747.65, 2),
    ('CH1 Cappuccino (hot) 12oz', 5, 700.93, 1),
    ('Watermelon 400 g. (Pack)', 5, 700.95, 3),
    ('Mango Passion Smoothie 22oz', 4, 691.59, 2),
    ('Watermelon Smoothie 22oz', 4, 691.60, 1),
    ('Pineapple 400 g. (Pack)', 3, 420.57, 2),
    ('Chicken Ham Sandwich', 3, 504.67, 2),
    ('Mango Smoothie 22oz', 3, 518.70, 1),
    ('Pineapple Smoothie 22oz', 2, 345.79, 2),
    ('S5 mango smoothie 16oz', 2, 299.06, 2),
    ('Pride Parrot Red Smoothie 22 oz.', 2, 373.84, 1),
    ('Orange Cold Pressed 22oz', 2, 392.52, 2),
    ('Heineken 320 ml. (Bottle)', 2, 336.44, 1),
    ('Ham and Cheese Croissant', 2, 355.14, 1),
    ('Sprite 500 ml. (Bottle)', 1, 74.76, 1),
    ('Butter Croissant', 1, 93.46, 1),
    ('CH4 Americano (hot) 12oz', 1, 126.17, 1),
    ('Coconut (EA)', 1, 158.88, 1),
]

# Dormant SKUs (Query D filtered: qty_30d >= 3, clean memos, 7+ day gap)
# (memo, last_sold_str, qty_30d, days_sold_30d, rev_30d)
DORMANT_MW1 = [
    ('ORANGE JUICE BOTTLE',                          '2026-06-20', 44, 11, 7607.51),
    ('MAEVAREE MANGO STICKY RICE SMOOTHIE 22OZ',    '2026-06-08', 12,  6, 2557.91),
    ('Overnight Oat mango 16 oz',                   '2026-06-06',  7,  3, 1759.80),
    ('BLUEBERRY GREEK YOGURT',                      '2026-06-05',  4,  3,  706.55),
    ('MAEVAREE MANGO YOGHURT STICKY RICE SMOOTHIE 22OZ', '2026-06-12', 3, 3, 644.85),
]
DORMANT_SE3 = [
    ('MANGO (1 PCS.) 380G.',                        '2026-06-18', 22, 11, 3084.15),
    ('ROSE APPLE 400G.',                            '2026-06-22', 19, 11, 2841.11),
    ('MAEVAREE MANGO STICKY RICE SMOOTHIE 22OZ',   '2026-06-12', 17,  9, 3632.67),
    ('Cantaloupe 400g (Pack)',                      '2026-06-09', 17,  9, 2383.21),
    ('MANGO (2 PCS.) 760G.',                        '2026-06-18', 13,  7, 3644.82),
    ('ORANGE JUICE BOTTLE',                         '2026-06-10', 11,  8, 1901.86),
    ('MAEVAREE MANGO YOGHURT STICKY RICE SMOTHIE 22OZ', '2026-06-12', 10, 6, 2149.50),
    ('Up size Smoothie & Cold Press',               '2026-06-20',  6,  6,  140.16),
    ('SEEDLESS GRAPE 400G.',                        '2026-06-08',  5,  2,  747.65),
    ('Overnight Oat mango 16oz',                    '2026-06-04',  3,  3,  754.20),
]
DORMANT_PKT = [
    ('Tuna Sandwich',                               '2026-06-21', 26, 15, 4312.50),
    ('P1 Mango passion fruit cold pressed 16oz',   '2026-06-22', 22, 13, 4112.23),
    ('C2 orange cold pressed 16oz',                '2026-06-19', 18,  9, 3112.20),
    ('Indian Tea Ginger Chai 12oz',                '2026-06-17', 18, 10, 2018.70),
    ('CH3 Espresso (hot) 4oz',                     '2026-06-21',  7,  5,  817.74),
    ('Mango Berry Smoothie 16oz',                  '2026-06-11',  5,  3,  864.50),
    ('Pride Parrot Red Smoothie 22 oz.',           '2026-06-05',  4,  2,  747.67),
    ('C7 Green Apple & Celery & Pineapple CP 16oz','2026-06-18',  4,  4,  691.60),
    ('singha soda water 325ml',                    '2026-06-04',  4,  2,  243.00),
    ('T2 Iced Thai tea with lime 16oz',            '2026-06-11',  3,  2,  420.57),
]

# ─────────────────── computations ───────────────────

from datetime import date, timedelta
from collections import defaultdict

report_date  = date(2026, 6, 29)
run_date     = date(2026, 6, 30)
window_start = report_date - timedelta(days=29)

daily = defaultdict(lambda: {33: 0.0, 105: 0.0, 109: 0.0})
for d_str, loc, net in QA:
    d = date.fromisoformat(d_str)
    daily[d][loc] += net

dates_sorted = sorted(daily.keys())

mw1  = {d: daily[d][33]  for d in dates_sorted}
se3  = {d: daily[d][105] for d in dates_sorted}
pkt  = {d: daily[d][109] for d in dates_sorted}
comb = {d: mw1[d] + se3[d] + pkt[d] for d in dates_sorted}

yest = report_date
mw1_yest  = mw1[yest];  se3_yest  = se3[yest];  pkt_yest  = pkt[yest]
comb_yest = mw1_yest + se3_yest + pkt_yest

mw1_avg  = sum(mw1.values())  / 30
se3_avg  = sum(se3.values())  / 30
pkt_avg  = sum(pkt.values())  / 30
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

TH_WD       = ['จ','อ','พ','พฤ','ศ','ส','อา']
TH_WD_FULL  = ['วันจันทร์','วันอังคาร','วันพุธ','วันพฤหัสบดี','วันศุกร์','วันเสาร์','วันอาทิตย์']
EN_MONTH    = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
EN_MONTH_FULL = ['January','February','March','April','May','June',
                 'July','August','September','October','November','December']

def th_weekday_abbr(d): return TH_WD[d.weekday()]

report_date_display      = f'{report_date.day} {EN_MONTH_FULL[report_date.month-1]} {report_date.year}'
report_day_th            = TH_WD_FULL[report_date.weekday()]
window_30d_start_display = f'{window_start.day} {EN_MONTH_FULL[window_start.month-1]} {window_start.year}'

last7_dates  = dates_sorted[-7:]
mw1_7d  = sum(mw1[d] for d in last7_dates)
se3_7d  = sum(se3[d] for d in last7_dates)
pkt_7d  = sum(pkt[d] for d in last7_dates)
comb_7d = mw1_7d + se3_7d + pkt_7d
last7_avg_val = comb_7d / 7

# ─── FORECAST (Monday 2026-06-30) ───
# Same-weekday (Monday) in trailing 4 weeks
def same_wday_history(branch_dict, target_date, weeks=4):
    vals = []
    d = target_date - timedelta(weeks=1)
    while len(vals) < weeks:
        if d in branch_dict:
            vals.append(branch_dict[d])
        d -= timedelta(weeks=1)
    return vals

def forecast_branch(wday_vals, branch_vals, all_dates):
    base      = sum(wday_vals) / len(wday_vals) if wday_vals else 0
    last7vals = [branch_vals[d] for d in all_dates[-7:]]
    trend_adj = (base + sum(last7vals) / 7) / 2
    stdev     = math.sqrt(sum((x - base)**2 for x in wday_vals) / len(wday_vals)) if len(wday_vals) > 1 else base * 0.12
    band      = max(stdev, trend_adj * 0.08)
    conf_pct  = stdev / base * 100 if base else 25
    conf_dot  = '🟢' if conf_pct < 12 else ('🟡' if conf_pct < 25 else '🔴')
    return trend_adj, band, conf_dot

mw1_mon = same_wday_history(mw1, run_date)
se3_mon = same_wday_history(se3, run_date)
pkt_mon = same_wday_history(pkt, run_date)

mw1_fc, mw1_band, mw1_conf = forecast_branch(mw1_mon, mw1, dates_sorted)
se3_fc, se3_band, se3_conf = forecast_branch(se3_mon, se3, dates_sorted)
pkt_fc, pkt_band, pkt_conf = forecast_branch(pkt_mon, pkt, dates_sorted)

comb_fc      = mw1_fc + se3_fc + pkt_fc
comb_band    = math.sqrt(mw1_band**2 + se3_band**2 + pkt_band**2)
comb_conf_pct = comb_band / comb_fc * 100 if comb_fc else 25
comb_conf    = '🟢' if comb_conf_pct < 12 else ('🟡' if comb_conf_pct < 25 else '🔴')

# ─── NEW PRODUCTS (Query C aggregated) ───
# All totals pre-computed from Query C results

# DRINKS
NP_DRINKS_ROWS = [
    {'memo': 'PRIDE PARROT RED',        'launch': '1 Jun 2026',  'notes': 'MW1, SE3, PKT',
     'total_units': 209+119+25,         'total_rev': '65,927',   'branch_split': 'MW1·SE3·PKT',
     'yest_units': 4+2+2,               'status_badge': '🟢 on target'},
    {'memo': 'PRIDE PARROT YELLOW',     'launch': '1 Jun 2026',  'notes': 'MW1, SE3, PKT',
     'total_units': 126+83+11,          'total_rev': '41,122',   'branch_split': 'MW1·SE3·PKT',
     'yest_units': 3+1+1,               'status_badge': '🟢 on target'},
    {'memo': 'GRAPE CLEAR PROTEIN',     'launch': '25 Jun 2026', 'notes': 'MW1, SE3 — new launch',
     'total_units': 11+9,               'total_rev': '2,804',    'branch_split': 'MW1·SE3',
     'yest_units': 2+1,                 'status_badge': '🟢 strong start (5d)'},
    {'memo': 'LYCHEE CLEAR PROTEIN',    'launch': '25 Jun 2026', 'notes': 'MW1, SE3 — new launch',
     'total_units': 10+6,               'total_rev': '2,243',    'branch_split': 'MW1·SE3',
     'yest_units': 0,                   'status_badge': '🟡 no sales yesterday'},
    {'memo': 'MOOVE CLEAR PROTEIN',     'launch': '13 Jun 2026', 'notes': 'MW1 only',
     'total_units': 40,                 'total_rev': '5,608',    'branch_split': 'MW1',
     'yest_units': 0,                   'status_badge': '🟡 no sales yesterday (last 24 Jun)'},
    {'memo': 'Fanta Orange 450ml.',     'launch': '31 May 2026', 'notes': 'PKT only',
     'total_units': 30,                 'total_rev': '2,243',    'branch_split': 'PKT',
     'yest_units': 0,                   'status_badge': '🟡 no sales yesterday'},
    {'memo': 'Fanta Strawberry 450ml.', 'launch': '1 Jun 2026',  'notes': 'PKT only',
     'total_units': 27,                 'total_rev': '2,019',    'branch_split': 'PKT',
     'yest_units': 1,                   'status_badge': '🟢 selling'},
    {'memo': 'Sprite 500ml. (Bottle)',  'launch': '30 May 2026', 'notes': 'PKT only',
     'total_units': 28,                 'total_rev': '2,094',    'branch_split': 'PKT',
     'yest_units': 1,                   'status_badge': '🟢 selling'},
]

NP_FRUIT_ROWS = [
    {'memo': 'ROSE APPLE 400G.',        'launch': '30 May 2026', 'notes': 'SE3 main, MW1 light — SE3 now dormant 7d',
     'total_units': 19+2,               'total_rev': '3,140',   'branch_split': 'SE3·MW1',
     'yest_units': 0,                   'status_badge': '🔴 SE3 dormant — check stock'},
    {'memo': 'Orange 400g (Pack)',      'launch': '18 Jun 2026', 'notes': 'SE3 only',
     'total_units': 18,                 'total_rev': '2,523',   'branch_split': 'SE3',
     'yest_units': 0,                   'status_badge': '🟡 no sales since 23 Jun (6d)'},
]

NP_NEWCAT_ROWS = [
    {'memo': 'Watermelon Smoothie 22oz',     'launch': '23 Jun 2026', 'notes': 'PKT only',
     'total_units': 7,  'total_rev': '1,210', 'branch_split': 'PKT',
     'yest_units': 4,   'status_badge': '🟢 strong'},
    {'memo': 'Mango Passion Smoothie 22oz',  'launch': '25 Jun 2026', 'notes': 'PKT only',
     'total_units': 11, 'total_rev': '1,902', 'branch_split': 'PKT',
     'yest_units': 4,   'status_badge': '🟢 strong'},
    {'memo': 'Mango Smoothie 22oz',          'launch': '24 Jun 2026', 'notes': 'PKT only',
     'total_units': 8,  'total_rev': '1,383', 'branch_split': 'PKT',
     'yest_units': 3,   'status_badge': '🟢 selling'},
    {'memo': 'Pineapple Smoothie 22oz',      'launch': '27 Jun 2026', 'notes': 'PKT only',
     'total_units': 3,  'total_rev': '519',   'branch_split': 'PKT',
     'yest_units': 2,   'status_badge': '🟢 new — 3d data'},
    {'memo': 'Mango Passion Cold Pressed 22oz','launch': '25 Jun 2026', 'notes': 'PKT only',
     'total_units': 4,  'total_rev': '785',   'branch_split': 'PKT',
     'yest_units': 1,   'status_badge': '🟢 selling'},
    {'memo': 'Orange Cold Pressed 22oz',     'launch': '24 Jun 2026', 'notes': 'PKT only',
     'total_units': 3,  'total_rev': '589',   'branch_split': 'PKT',
     'yest_units': 2,   'status_badge': '🟢 selling'},
    {'memo': 'Iced Cappuccino 22oz',         'launch': '25 Jun 2026', 'notes': 'PKT only',
     'total_units': 3,  'total_rev': '497',   'branch_split': 'PKT',
     'yest_units': 1,   'status_badge': '🟢 selling'},
    {'memo': 'Mango Yoghurt Smoothie 22oz',  'launch': '23 Jun 2026', 'notes': 'PKT only',
     'total_units': 4,  'total_rev': '748',   'branch_split': 'PKT',
     'yest_units': 0,   'status_badge': '⚪ no sales yesterday'},
    {'memo': 'Pride Parrot Red Smoothie 22oz','launch': '4 Jun 2026',  'notes': 'PKT only',
     'total_units': 25, 'total_rev': '4,673', 'branch_split': 'PKT',
     'yest_units': 2,   'status_badge': '🟢 selling'},
    {'memo': 'Pride Parrot Yellow Smoothie 22oz','launch': '7 Jun 2026','notes': 'PKT only',
     'total_units': 11, 'total_rev': '2,056', 'branch_split': 'PKT',
     'yest_units': 1,   'status_badge': '🟢 selling'},
    {'memo': 'PINEAPPLE TOPPING',            'launch': '29 Jun 2026', 'notes': 'MW1 — first sale today',
     'total_units': 1,  'total_rev': '23',    'branch_split': 'MW1',
     'yest_units': 1,   'status_badge': '⚪ first sale today'},
    {'memo': 'BANANA TOPPING',               'launch': '12 Jun 2026', 'notes': 'MW1 — dormant since launch',
     'total_units': 1,  'total_rev': '23',    'branch_split': 'MW1',
     'yest_units': 0,   'status_badge': '🔴 no sales since launch'},
]

drinks_n             = 8
drinks_total_units   = sum(r['total_units'] for r in NP_DRINKS_ROWS)
drinks_total_rev     = 65927+41122+2804+2243+5608+2243+2019+2094  # 124,060
drinks_yest_units    = sum(r['yest_units'] for r in NP_DRINKS_ROWS)
drinks_yest_rev      = int(1495.35+934.58+420.57+186.92+74.77+74.76)  # 3187

fruit_n              = 2
fruit_total_units    = sum(r['total_units'] for r in NP_FRUIT_ROWS)
fruit_total_rev      = 3140+2523  # 5663
fruit_yest_units     = 0
fruit_yest_rev       = 0

new_cat_n            = len(NP_NEWCAT_ROWS)
new_cat_total_units  = sum(r['total_units'] for r in NP_NEWCAT_ROWS)
new_cat_total_rev    = 1210+1902+1383+519+785+589+497+748+4673+2056+23+23  # 14408
new_cat_yest_units   = sum(r['yest_units'] for r in NP_NEWCAT_ROWS)
new_cat_yest_rev     = int(691.6+691.59+518.7+345.79+196.26+392.52+182.24+373.84+186.92+23.36)  # 3603

np_total_units = drinks_total_units + fruit_total_units + new_cat_total_units
np_total_rev   = drinks_total_rev + fruit_total_rev + new_cat_total_rev

# ─── SEASONAL (Query E) ───
# Grape: SEEDLESS GRAPE 400G. MW1 last 27 Jun; SE3 last 8 Jun
# GRAPE CLEAR PROTEIN is a protein drink, not counted in grape baseline
grape_total_rev = 133186 + 1495 + 105553 + 3290  # SHINE MUSCAT + SEEDLESS GRAPE both branches

# New seasonal fruit coverage in 30-day window
# SE3: ROSE APPLE (2841.11 rev) + Orange 400g (2523.40 rev) = 5364.51 → 178.8/d
# MW1: ROSE APPLE (299.06 rev only on 24 Jun) → 9.97/d
se3_fruit_per_day = (2841.11 + 2523.40) / 30   # 178.82/d
mw1_fruit_per_day = 299.06 / 30                 # 9.97/d
mw1_grape_baseline = 339
se3_grape_baseline = 251
mw1_coverage = mw1_fruit_per_day / mw1_grape_baseline * 100   # 2.9%
se3_coverage = se3_fruit_per_day / se3_grape_baseline * 100   # 71.2%

def coverage_color(pct):
    return '#155724' if pct >= 100 else ('#856404' if pct >= 70 else '#721C24')

def coverage_bg(pct):
    return '#D4EDDA' if pct >= 100 else ('#FFF3CD' if pct >= 70 else '#F8D7DA')

def coverage_badge(pct):
    return ('✅ Fully replaced' if pct >= 100 else
            ('🟡 Partial — monitor' if pct >= 70 else '🔴 Large gap — push promotion or add SKU'))

# ─── DORMANT helpers ───
def gap_days(last_str):
    return (report_date - date.fromisoformat(last_str)).days

def gap_color(days):
    return '#C62828' if days >= 14 else '#E65100'

def truncate(s, n=34):
    return (s[:n] + '…') if len(s) > n else s

def dormant_rows_for(branch_list):
    rows = []
    for memo, last_str, qty, days_sold, rev in branch_list:
        g = gap_days(last_str)
        rows.append({
            'memo_display':   truncate(memo),
            'memo_full':      memo,
            'qty_30d':        fmt(qty),
            'days_sold_30d':  str(days_sold),
            'rev_30d':        f'{round(rev):,}',
            'gap_days':       str(g),
            'gap_color':      gap_color(g),
        })
    return rows

dormant_count = len(DORMANT_MW1) + len(DORMANT_SE3) + len(DORMANT_PKT)

# AM queue items (14+ day gap dormant): 14 items
def am_hypothesis(memo):
    m = memo.upper()
    if 'MANGO STICKY RICE' in m or 'MAEVAREE' in m:
        return ('Seasonal / removed from menu', '#E65100')
    if 'OAT' in m or 'YOGURT' in m or 'YOGHURT' in m:
        return ('SKU discontinued / batch stopped', '#C62828')
    if 'CANTALOUPE' in m:
        return ('Seasonal end — cantaloupe out of season', '#C62828')
    if 'ORANGE JUICE' in m:
        return ('Supplier issue or discontinued', '#C62828')
    if 'GRAPE' in m:
        return ('Seasonal end — replaced by new grape SKUs', '#C62828')
    if 'BERRY SMOOTHIE' in m:
        return ('Menu change or stock-out', '#C62828')
    if 'PRIDE PARROT' in m:
        return ('Duplicate item memo — check against active Pride Parrot entries', '#C62828')
    if 'SODA' in m or 'SINGHA' in m:
        return ('Low demand — consider removing', '#C62828')
    return ('Menu change or stock-out', '#C62828')

def am_items_for(branch_list, branch_label):
    items = []
    for memo, last_str, qty, days_sold, rev in branch_list:
        g = gap_days(last_str)
        if g >= 14:
            hyp_text, hyp_color = am_hypothesis(memo)
            vel = f'{qty/30:.1f}'
            tgt = f'{qty/days_sold:.1f}' if days_sold > 0 else '—'
            last_d = date.fromisoformat(last_str)
            last_display = f'{last_d.day} {EN_MONTH_FULL[last_d.month-1]}'
            items.append({
                'memo':             truncate(memo, 40),
                'last_sold':        last_display,
                'gap_days':         str(g),
                'velocity_7d':      vel,
                'target':           tgt,
                'branch_split':     branch_label,
                'hypothesis_color': hyp_color,
                'hypothesis_text':  hyp_text,
            })
    return items

am_items_list = (am_items_for(DORMANT_MW1, 'MW1') +
                 am_items_for(DORMANT_SE3, 'SE3') +
                 am_items_for(DORMANT_PKT, 'PKT'))
am_queue_count = len(am_items_list)  # should be 14

# ─── PREDICTION (commentary + anomaly) ───
commentary_text = (
    f'Yesterday (29 June 2026 · วันอาทิตย์), combined net was ฿{fmt(comb_yest)} ex-VAT, '
    f'{abs(signed_pct):.1f}% {"above" if signed_pct >= 0 else "below"} the 30-day average. '
    f'MW1 came in at ฿{fmt(mw1_yest)} ({mw1_vs30:+.1f}% vs avg), '
    f'SE3 at ฿{fmt(se3_yest)} ({se3_vs30:+.1f}% vs avg), '
    f'PKT at ฿{fmt(pkt_yest)} ({pkt_vs30:+.1f}% vs avg). '
    f'SE3 posted its best Sunday result in the 30-day window; all three branches were above their 30-day means.'
)

anomaly_items = [
    {'anomaly_text': f'PKT: Tuna Sandwich dormant 8d (฿4,313/30d) + P1 Mango Passion CP dormant 7d (฿4,112/30d)',
     'anomaly_section_ref': 'Dormant §7'},
    {'anomaly_text': f'SE3 ROSE APPLE 400G. reached 7-day dormancy today — was ฿2,841 in 30d; check stock',
     'anomaly_section_ref': 'Dormant §7'},
    {'anomaly_text': f'Seasonal fruit: MW1 only 3% of grape baseline (฿10/d vs ฿339/d) — ฿9,870/month gap',
     'anomaly_section_ref': 'Seasonal §6'},
    {'anomaly_text': f'14 items in AM review (14+ day dormant): top — SE3 Cantaloupe 20d, MW1 MAEVAREE 21d',
     'anomaly_section_ref': 'AM Review §1'},
    {'anomaly_text': f'GRAPE CLEAR PROTEIN (launched 25 Jun): 20u in 5d at MW1+SE3 — strong start, monitor stock',
     'anomaly_section_ref': 'New Products §4'},
]

# ─────────────────── build repeats ───────────────────

chart_days = []
for d in dates_sorted:
    chart_days.append({
        'date':              d.strftime('%Y-%m-%d'),
        'day_num':           str(d.day),
        'weekday_th_abbr':   th_weekday_abbr(d),
        'mw1_net':           fmt(mw1[d]),
        'se3_net':           fmt(se3[d]),
        'pkt_net':           fmt(pkt[d]),
        'mw1_bar_px':        bar(mw1[d]),
        'se3_bar_px':        bar(se3[d]),
        'pkt_bar_px':        bar(pkt[d]),
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
    {'header_color': '#5551FE', 'header_label': 'MW1 · 26-T1MW1-03+04', 'top20_rows': top20_rows(QB_MW1)},
    {'header_color': '#F27061', 'header_label': 'SE3 · 27-T1SE3-05',    'top20_rows': top20_rows(QB_SE3)},
    {'header_color': '#2E7D32', 'header_label': 'PKT · 28 Unit 362 (Phuket)', 'top20_rows': top20_rows(QB_PKT)},
]

np_type_tables = [
    {'type_bg': '#1976D2', 'type_fg': '#fff', 'type_icon': '🥤', 'type_label': 'Drinks',          'np_rows': NP_DRINKS_ROWS},
    {'type_bg': '#AD1457', 'type_fg': '#fff', 'type_icon': '🍉', 'type_label': 'Seasonal Fruits', 'np_rows': NP_FRUIT_ROWS},
    {'type_bg': '#2E7D32', 'type_fg': '#fff', 'type_icon': '⭐', 'type_label': 'New Category',    'np_rows': NP_NEWCAT_ROWS},
]

seasonal_skus = [
    {'fruit_emoji': '🌸', 'memo': 'ROSE APPLE 400G.', 'launch': '30 May 2026',
     'mw1_units': '2', 'mw1_per_day': f'{299.06/30:.0f}',
     'se3_units': '19', 'se3_per_day': f'{2841.11/30:.0f}'},
    {'fruit_emoji': '🍊', 'memo': 'Orange 400g (Pack)', 'launch': '18 Jun 2026',
     'mw1_units': '—', 'mw1_per_day': '0',
     'se3_units': '18', 'se3_per_day': f'{2523.40/30:.0f}'},
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

# ─────────────────── scalars ───────────────────

scalars = {
    'report_date':           REPORT_DATE,
    'report_date_display':   report_date_display,
    'report_day_th':         report_day_th,
    'window_30d_start':      window_30d_start_display,
    'generated_timestamp':   '2026-06-30 07:30',
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
    'np_summary_line':       f'New SKUs launched May–Jun 2026 · Drinks · Seasonal Fruits · PKT New Menu',
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
    'grape_last_mw1':        '27 June 2026',
    'grape_last_se3':        '8 June 2026',
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
    'am_items':          am_items_list,
    'anomaly_items':     anomaly_items,
}

sections = {
    'am_review':           am_queue_count > 0,
    'seasonal':            True,
    'dormant':             True,
    'forecast_shown':      True,
    'forecast_suppressed': False,
    'anomaly_shown':       True,
}

# ─────────────────── read templates & build ───────────────────

import os
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
print(f'am_queue={am_queue_count} dormant={dormant_count} comb={fmt(comb_yest)} signed={signed_pct:+.1f}%')
