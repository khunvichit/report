#!/usr/bin/env python3
"""
Build Juiceland Daily Sales Report email.html for 2026-06-22.
Report date: 2026-06-22 (yesterday Asia/Bangkok)
Run date:    2026-06-23
"""
import re, sys, os, math
from datetime import date, timedelta
from collections import defaultdict

# ─────────────────── template filler ───────────────────

def fill(template, scalars, repeats, sections):
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

REPORT_DATE = '2026-06-22'

QA = [
    ('2026-05-24', 33, 45429.5),  ('2026-05-24', 105, 28328.0),   ('2026-05-24', 109, 12933.0),
    ('2026-05-25', 33, 38221.0),  ('2026-05-25', 105, 31983.5),   ('2026-05-25', 109, 10502.0),
    ('2026-05-26', 33, 36852.5),  ('2026-05-26', 105, 24575.5),   ('2026-05-26', 109, 7039.0),
    ('2026-05-27', 33, 33877.0),  ('2026-05-27', 105, 26502.0),   ('2026-05-27', 109, 16234.0),
    ('2026-05-28', 33, 33415.0),  ('2026-05-28', 105, 31121.0),   ('2026-05-28', 109, 12474.0),
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
]

QB_MW1 = [
    ('EVIAN',                          43, 4822.00, 10),
    ('COCONUT READY TO DRINK',         11, 1748.00,  4),
    ('MANGO 400G.',                     9, 1346.00,  4),
    ('C3 WATERMELON COLD PRESSED 22OZ', 7, 1374.00,  3),
    ('C3 WATERMELON COLD PRESSED 16OZ', 6, 1037.00,  3),
    ('S4 MIXBERRY SMOOTHIE 22OZ',       6, 1038.00,  3),
    ('PRIDE PARROT YELLOW',             6, 1122.00,  3),
    ('COCONUT JUICE BOTTLE',            6, 1038.00,  3),
    ('S2 MANGO PASSION SMOOTHIE 22OZ',  6, 1038.00,  3),
    ('S5 MANGO SMOOTHIE 16OZ',          5,  747.00,  2),
    ('S1 COCONUT SMOOTHIE 16OZ',        5,  748.00,  3),
    ('S5 MANGO SMOOTHIE 22OZ',          5,  865.00,  2),
    ('MOOVE CLEAR PROTEIN',             5,  701.00,  2),
    ('3 KINDS FRUIT 400G.',             5,  747.00,  3),
    ('PINEAPPLE 400G.',                 4,  560.00,  2),
    ('S1 COCONUT SMOOTHIE 22OZ',        4,  692.00,  2),
    ('S2 MANGO PASSION SMOOTHIE 16OZ',  4,  692.00,  2),
    ('S3 WATERMELON SMOOTHIE 22OZ',     4,  692.00,  2),
    ('CI3 ICED AMERICANO 22OZ',         4,  672.00,  2),
    ('PAPAYA 400G.',                    4,  560.00,  2),
]
QB_SE3 = [
    ('COCONUT READY TO DRINK',         19, 3019.00,  6),
    ('EVIAN',                          18, 2019.00,  5),
    ('MANGO 400G.',                    12, 1794.00,  5),
    ('WATERMELON 400G.',               11, 1542.00,  4),
    ('3 KINDS FRUIT 400G.',             8, 1196.00,  3),
    ('PINEAPPLE 400G.',                 6,  841.00,  3),
    ('Orange 400g Pack',                5,  745.00,  2),
    ('LYCHEE 400G.',                    4,  635.00,  2),
    ('ROSE APPLE 400G.',                4,  598.00,  2),
    ('YS1 MANGO YOGHURT SMOOTHIE 22OZ', 4,  785.00,  2),
    ('PAPAYA 400G.',                    4,  561.00,  2),
    ('S5 MANGO SMOOTHIE 16OZ',          4,  598.00,  2),
    ('S5 MANGO SMOOTHIE 22OZ',          3,  519.00,  2),
    ('PRIDE PARROT YELLOW',             3,  561.00,  2),
    ('MANGO JUICE BOTTLE',              3,  519.00,  2),
    ('GUAVA 400G.',                     3,  447.00,  2),
    ('Chicken Club Croissant',          3,  418.00,  1),
    ('S7 PINEAPPLE SMOOTHIE 16OZ',      2,  345.00,  1),
    ('T1 ICED THAI MILK TEA 22OZ',      2,  346.00,  1),
    ('MANGO PASSION JUICE BOTTLE',      2,  346.00,  1),
]
QB_PKT = [
    ('Evian 500ml. (Bottle)',                        6, 673.00, 3),
    ('Mango 400g Pack',                              6, 897.00, 3),
    ('Up size Smoothie & Cold Press 16oz to 22oz',   6, 140.00, 4),
    ('S5 mango smoothie 16oz',                       4, 598.00, 2),
    ('Watermelon 400g Pack',                         3, 421.00, 2),
    ('Coke 500 ml. (Bottle)',                        3, 224.00, 2),
    ('Pineapple 400g Pack',                          2, 281.00, 1),
    ('C6 pineapple cold pressed 16oz',               2, 346.00, 1),
    ('Mango passion juice bottle',                   2, 346.00, 1),
    ('S2 mango passion smoothie 16oz',               2, 299.00, 1),
    ('T1 Thai milk tea 16oz',                        2, 299.00, 1),
    ('Ham and Cheese Croissant',                     1, 140.00, 1),
    ('Salt Grilled Salmon Onigiri',                  1, 102.00, 1),
    ('Fanta Strawberry 450 ml. (Bottle)',             1,  75.00, 1),
    ('Pineapple Cold Pressed Juice Bottle',          1, 172.00, 1),
    ('Pride Parrot Yellow 22oz',                     1, 187.00, 1),
    ('YS2 Strawberry yoghurt smoothie 16oz',         1, 187.00, 1),
    ('CI5 Iced Latte 16oz',                          1, 163.00, 1),
    ('S1 Coconut smoothie 16oz',                     1, 149.00, 1),
    ('Larb Salmon Onigiri',                          1, 102.00, 1),
]

DORMANT_MW1 = [
    ('MAEVAREE MANGO STICKY RICE SMOOTHIE 22OZ', '2026-06-08', 24, 12, 5115.83),
    ('Overnight Oat mango 16 oz',                '2026-06-06', 20, 12, 5028.00),
    ('HOT CHOCOLATE 8 oz',                       '2026-05-27', 18,  4, 2186.96),
    ('MAEVAREE MANGO YOGHURT STICKY RICE SMTHIE','2026-06-12', 17,  9, 3654.15),
    ('MANGO (1 PCS.)',                           '2026-06-11', 12,  8, 1682.28),
    ('BLUEBERRY GREEK YOGURT',                   '2026-06-05',  8,  6, 1413.11),
    ('SEEDLESS GRAPE 400G.',                     '2026-06-11',  6,  4,  897.17),
    ('Mango Sticky Rice (Box)',                  '2026-06-01',  3,  2,  501.85),
]
DORMANT_SE3 = [
    ('Cantaloupe 400g (Pack)',                   '2026-06-09', 40, 15, 5607.55),
    ('MAEVAREE MANGO STICKY RICE SMOOTHIE 22OZ', '2026-06-12', 33, 15, 7071.87),
    ('HOT CHOCOLATE 8 oz',                       '2026-05-29', 22,  6, 2672.98),
    ('MAEVAREE MANGO YOGHURT STICKY RICE SMTHIE','2026-06-12', 17, 10, 3654.16),
    ('Mango Sticky Rice (Box)',                  '2026-05-31', 16,  6, 2676.64),
    ('ORANGE JUICE BOTTLE',                      '2026-06-10', 11,  8, 1901.86),
    ('Pineapple Cold Pressed Juice Bottle',      '2026-06-12', 11,  8, 1901.82),
    ('Golden Harmony Greek Yogurt',              '2026-05-31',  7,  5, 1236.47),
    ('MANGO PINEAPPLE SMOOTHIE 16OZ',            '2026-05-31',  6,  4, 1037.41),
    ('Overnight Oat mango 16 oz',                '2026-06-04',  5,  5, 1257.00),
    ('SEEDLESS GRAPE 400G.',                     '2026-06-08',  5,  2,  747.65),
    ('Overnight Oat Berry 16 oz',                '2026-05-27',  4,  3,  968.24),
    ('BANANA YOGHURT SMOOTHIE 16OZ',             '2026-05-28',  4,  3,  654.20),
    ('MANGOSTEEN 400g.',                         '2026-06-01',  3,  3,  700.92),
]
DORMANT_PKT = [
    ('C5 pineapple & green apple CP 16oz', '2026-06-15', 15, 10, 2593.48),
    ('Banana 2PCS.',                       '2026-06-06', 11,  9,  606.54),
    ('Mango Berry Smoothie 16oz',          '2026-06-11',  8,  5, 1383.20),
    ('singha soda water 325ml',            '2026-06-04',  4,  2,  243.00),
    ('T2 Iced Thai tea with lime 16oz',    '2026-06-11',  4,  3,  560.76),
]

NP_DRINKS_ROWS = [
    {'memo': 'PRIDE PARROT RED',          'launch': '1 Jun 2026',  'notes': 'MW1, SE3, PKT',
     'total_units': 260, 'total_rev': '46,674', 'branch_split': 'MW1·SE3·PKT',
     'yest_units': 5,  'status_badge': '🟢 on target'},
    {'memo': 'PRIDE PARROT YELLOW',       'launch': '1 Jun 2026',  'notes': 'MW1, SE3, PKT',
     'total_units': 149, 'total_rev': '27,440', 'branch_split': 'MW1·SE3·PKT',
     'yest_units': 10, 'status_badge': '🟢 on target'},
    {'memo': 'HOT CHOCOLATE 8 oz',        'launch': '24 May 2026', 'notes': 'MW1, SE3 — dormant',
     'total_units': 40,  'total_rev': '5,860',  'branch_split': 'MW1·SE3',
     'yest_units': 0,  'status_badge': '🔴 no sales — dormant'},
    {'memo': 'Fanta Orange 450ml. (Bottle)', 'launch': '31 May 2026', 'notes': 'PKT only',
     'total_units': 24,  'total_rev': '1,819',  'branch_split': 'PKT',
     'yest_units': 0,  'status_badge': '⚪ not sold yesterday'},
    {'memo': 'Fanta Strawberry 450ml. (Bottle)', 'launch': '1 Jun 2026', 'notes': 'PKT only',
     'total_units': 24,  'total_rev': '1,797',  'branch_split': 'PKT',
     'yest_units': 1,  'status_badge': '🟢 on target'},
    {'memo': 'Sprite 500ml. (Bottle)',    'launch': '30 May 2026', 'notes': 'PKT only',
     'total_units': 23,  'total_rev': '1,721',  'branch_split': 'PKT',
     'yest_units': 0,  'status_badge': '⚪ not sold yesterday'},
    {'memo': 'Iced Espresso Orange 12oz', 'launch': '29 May 2026', 'notes': 'SE3 — dormant',
     'total_units': 1,   'total_rev': '168',    'branch_split': 'SE3',
     'yest_units': 0,  'status_badge': '🔴 no sales — dormant'},
    {'memo': 'Fanta Fruit Punch 450ml. (Bottle)', 'launch': '31 May 2026', 'notes': 'PKT — 1 day only',
     'total_units': 1,   'total_rev': '75',     'branch_split': 'PKT',
     'yest_units': 0,  'status_badge': '🔴 no sales — dormant'},
    {'memo': 'Hot Tea Green Tea 12oz',    'launch': '18 Jun 2026', 'notes': 'PKT only',
     'total_units': 1,   'total_rev': '102',    'branch_split': 'PKT',
     'yest_units': 0,  'status_badge': '⚪ new — 1 sale'},
]
NP_FRUIT_ROWS = [
    {'memo': 'LYCHEE 400G.',     'launch': '28 May 2026', 'notes': 'MW1, SE3',
     'total_units': 54, 'total_rev': '8,421', 'branch_split': 'MW1·SE3',
     'yest_units': 7,  'status_badge': '🟢 on target'},
    {'memo': 'ROSE APPLE 400G.', 'launch': '30 May 2026', 'notes': 'SE3 only',
     'total_units': 20, 'total_rev': '3,290', 'branch_split': 'SE3',
     'yest_units': 4,  'status_badge': '🟢 on target'},
    {'memo': 'Orange 400g Pack', 'launch': '18 Jun 2026', 'notes': 'SE3 only',
     'total_units': 17, 'total_rev': '2,383', 'branch_split': 'SE3',
     'yest_units': 6,  'status_badge': '🟢 on target (new)'},
    {'memo': 'MANGOSTEEN 400g.', 'launch': '28 May 2026', 'notes': 'SE3, MW1',
     'total_units': 4,  'total_rev': '935',   'branch_split': 'SE3·MW1',
     'yest_units': 0,  'status_badge': '🟡 sporadic'},
]
NP_NEWCAT_ROWS = [
    {'memo': 'MOOVE CLEAR PROTEIN', 'launch': '13 Jun 2026', 'notes': 'MW1 only',
     'total_units': 38, 'total_rev': '5,327', 'branch_split': 'MW1',
     'yest_units': 5,  'status_badge': '🟢 on target'},
]

# ─────────────────── computations ───────────────────

report_date  = date(2026, 6, 22)
run_date     = date(2026, 6, 23)
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
mw1_yest  = mw1[yest]; se3_yest = se3[yest]; pkt_yest = pkt[yest]
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
def en_day_display(d):  return f'{d.day} {EN_MONTH_FULL[d.month-1]}'

report_date_display      = f'{report_date.day} {EN_MONTH_FULL[report_date.month-1]} {report_date.year}'
report_day_th            = TH_WD_FULL[report_date.weekday()]
window_30d_start_display = f'{window_start.day} {EN_MONTH_FULL[window_start.month-1]} {window_start.year}'

last7_dates = dates_sorted[-7:]

mw1_7d  = sum(mw1[d] for d in last7_dates)
se3_7d  = sum(se3[d] for d in last7_dates)
pkt_7d  = sum(pkt[d] for d in last7_dates)
comb_7d = mw1_7d + se3_7d + pkt_7d
last7_avg_val = comb_7d / 7

# ─── FORECAST (tomorrow = Tuesday 2026-06-23) ───
fc_date = run_date

def same_wday_history(branch_dict, target_date, weeks=4):
    vals = []
    d = target_date - timedelta(weeks=1)
    while len(vals) < weeks:
        if d in branch_dict:
            vals.append(branch_dict[d])
        d -= timedelta(weeks=1)
    return vals

mw1_tue = same_wday_history(mw1, fc_date)
se3_tue = same_wday_history(se3, fc_date)
pkt_tue = same_wday_history(pkt, fc_date)

def forecast_branch(tue_vals, branch_vals, all_dates):
    base = sum(tue_vals) / len(tue_vals) if tue_vals else 0
    last7_vals = [branch_vals[d] for d in all_dates[-7:]]
    trend_adj = (base + sum(last7_vals) / 7) / 2
    stdev = math.sqrt(sum((x - base)**2 for x in tue_vals) / len(tue_vals)) if len(tue_vals) > 1 else base * 0.12
    band = max(stdev, trend_adj * 0.08)
    conf_pct = stdev / base * 100 if base else 25
    if conf_pct < 12:   conf_dot = '🟢'
    elif conf_pct < 25: conf_dot = '🟡'
    else:               conf_dot = '🔴'
    return trend_adj, band, conf_dot

mw1_fc, mw1_band, mw1_conf = forecast_branch(mw1_tue, mw1, dates_sorted)
se3_fc, se3_band, se3_conf = forecast_branch(se3_tue, se3, dates_sorted)
pkt_fc, pkt_band, pkt_conf = forecast_branch(pkt_tue, pkt, dates_sorted)

comb_fc      = mw1_fc + se3_fc + pkt_fc
comb_band    = math.sqrt(mw1_band**2 + se3_band**2 + pkt_band**2)
comb_conf_pct = comb_band / comb_fc * 100 if comb_fc else 25
comb_conf    = '🟢' if comb_conf_pct < 12 else ('🟡' if comb_conf_pct < 25 else '🔴')

# ─── NEW PRODUCTS totals ───
drinks_n            = len(NP_DRINKS_ROWS)        # 9
drinks_total_units  = 523
drinks_total_rev    = 85656
drinks_yest_units   = 16
drinks_yest_rev     = 2879

fruit_n             = len(NP_FRUIT_ROWS)         # 4
fruit_total_units   = 95
fruit_total_rev     = 15029
fruit_yest_units    = 17
fruit_yest_rev      = 2551

new_cat_n           = len(NP_NEWCAT_ROWS)        # 1
new_cat_total_units = 38
new_cat_total_rev   = 5327
new_cat_yest_units  = 5
new_cat_yest_rev    = 701

np_total_units = drinks_total_units + fruit_total_units + new_cat_total_units  # 656
np_total_rev   = drinks_total_rev + fruit_total_rev + new_cat_total_rev        # 106,012

# ─── SEASONAL ───
grape_total_rev = 238740
grape_last_mw1  = '11 Jun 2026'
grape_last_se3  = '8 Jun 2026'

mw1_grape_baseline = 339
se3_grape_baseline = 251

# per_day = sum of per-shelf-day rates for each seasonal fruit SKU
mw1_fruit_per_day = 108   # LYCHEE(฿101/d) + MANGOSTEEN(฿8/d)
se3_fruit_per_day = 393   # LYCHEE(฿180/d) + MANGOSTEEN(฿23/d) + ROSE APPLE(฿110/d) + ORANGE(฿79/d)

mw1_coverage = mw1_fruit_per_day / mw1_grape_baseline * 100   # 31.9% ≈ 32%
se3_coverage = se3_fruit_per_day / se3_grape_baseline * 100   # 156.6% ≈ 156%

def coverage_color(pct):
    if pct >= 100: return '#155724'
    if pct >= 70:  return '#856404'
    return '#721C24'

def coverage_bg(pct):
    if pct >= 100: return '#D4EDDA'
    if pct >= 70:  return '#FFF3CD'
    return '#F8D7DA'

def coverage_badge(pct):
    if pct >= 100: return '✅ Fully replaced'
    if pct >= 70:  return '🟡 Partial — monitor'
    return '🔴 Large gap — push promotion or add SKU'

# ─── DORMANT helpers ───
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

dormant_count = len(DORMANT_MW1) + len(DORMANT_SE3) + len(DORMANT_PKT)  # 27

# ─── Commentary & anomaly ───
commentary_text = (
    'Combined net sales for Monday 22 June 2026 were ฿70,247 ex-VAT, '
    '2.9% below the 30-day average (฿72,321). '
    'MW1 came in at ฿37,555 (+3.3% vs avg), SE3 at ฿25,020 (+5.3% vs avg). '
    'PKT net was ฿7,672, down 37.1% vs its 30-day average of ฿12,193 — '
    'the weakest day at PKT in the 30-day window; previous Mondays at PKT averaged '
    'approximately ฿12,661. MW1 and SE3 were within normal range.'
)

anomaly_items = [
    {'anomaly_text': 'PKT net ฿7,672 — down 37.1% vs 30d avg, weakest PKT day in window',
     'anomaly_section_ref': 'Charts §§3'},
    {'anomaly_text': '27 dormant SKUs total (8 MW1, 14 SE3, 5 PKT)',
     'anomaly_section_ref': 'Dormant SKUs §7'},
    {'anomaly_text': 'SE3: Cantaloupe 40u dormant 13d, MAEVAREE MANGO 33u dormant 10d, HOT CHOC 22u dormant 24d',
     'anomaly_section_ref': 'Dormant SKUs §7'},
    {'anomaly_text': 'MW1 seasonal fruit coverage 32% of grape baseline (฿108/d vs ฿339 baseline)',
     'anomaly_section_ref': 'Seasonal Tracker §6'},
    {'anomaly_text': 'Pride Parrot Red+Yellow strong: 15u combined yesterday (5+10), 409u since launch',
     'anomaly_section_ref': 'New Products §4'},
]

# ─────────────────── build repeats ───────────────────

chart_days = []
for d in dates_sorted:
    chart_days.append({
        'date':             d.strftime('%Y-%m-%d'),
        'day_num':          str(d.day),
        'weekday_th_abbr':  th_weekday_abbr(d),
        'mw1_net':          fmt(mw1[d]),
        'se3_net':          fmt(se3[d]),
        'pkt_net':          fmt(pkt[d]),
        'mw1_bar_px':       bar(mw1[d]),
        'se3_bar_px':       bar(se3[d]),
        'pkt_bar_px':       bar(pkt[d]),
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
    {'fruit_emoji': '🍈', 'memo': 'LYCHEE 400G.',     'launch': '28 May 2026',
     'mw1_units': '19', 'mw1_per_day': '101', 'se3_units': '35', 'se3_per_day': '180'},
    {'fruit_emoji': '🟣', 'memo': 'MANGOSTEEN 400g.', 'launch': '28 May 2026',
     'mw1_units': '1',  'mw1_per_day': '8',   'se3_units': '3',  'se3_per_day': '23'},
    {'fruit_emoji': '🌸', 'memo': 'ROSE APPLE 400G.', 'launch': '30 May 2026',
     'mw1_units': '—',  'mw1_per_day': '0',   'se3_units': '20', 'se3_per_day': '110'},
    {'fruit_emoji': '🍊', 'memo': 'Orange 400g Pack', 'launch': '18 Jun 2026',
     'mw1_units': '—',  'mw1_per_day': '0',   'se3_units': '17', 'se3_per_day': '79'},
]

mw1_daily_gap = mw1_grape_baseline - mw1_fruit_per_day    # 231
se3_daily_gap = se3_grape_baseline - se3_fruit_per_day    # -142

seasonal_coverage = [
    {
        'branch_label':      'MW1 (Suvarnabhumi T1)',
        'branch_color':      '#5551FE',
        'grape_baseline':    fmt(mw1_grape_baseline),
        'new_fruit_per_day': fmt(mw1_fruit_per_day),
        'coverage_pct':      f'{mw1_coverage:.0f}',
        'coverage_color':    coverage_color(mw1_coverage),
        'daily_gap':         f'฿{fmt(abs(mw1_daily_gap))}/d',
        'monthly_impact':    f'-฿{fmt(abs(mw1_daily_gap)*30)}/month',
        'badge_bg':          coverage_bg(mw1_coverage),
        'badge_text':        coverage_badge(mw1_coverage),
    },
    {
        'branch_label':      'SE3 (Suvarnabhumi T1)',
        'branch_color':      '#F27061',
        'grape_baseline':    fmt(se3_grape_baseline),
        'new_fruit_per_day': fmt(se3_fruit_per_day),
        'coverage_pct':      f'{se3_coverage:.0f}',
        'coverage_color':    coverage_color(se3_coverage),
        'daily_gap':         f'+฿{fmt(abs(se3_daily_gap))}/d surplus',
        'monthly_impact':    f'+฿{fmt(abs(se3_daily_gap)*30)}/month (surplus)',
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
    'report_date':           REPORT_DATE,
    'report_date_display':   report_date_display,
    'report_day_th':         report_day_th,
    'window_30d_start':      window_30d_start_display,
    'generated_timestamp':   '2026-06-23 07:30',
    'subject_prefix':        subject_prefix,
    'comb_net':              fmt(comb_yest),
    'signed_pct':            f'{signed_pct:+.1f}',
    'mw1_net':               fmt(mw1_yest),
    'se3_net':               fmt(se3_yest),
    'pkt_net':               fmt(pkt_yest),
    'mw1_vs_30d':            f'{mw1_vs30:+.1f}',
    'se3_vs_30d':            f'{se3_vs30:+.1f}',
    'pkt_vs_30d':            f'{pkt_vs30:+.1f}',
    'am_queue_count':        '0',
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
    'np_summary_line':       '14 new SKUs launched May–Jun 2026 · Drinks · Seasonal Fruits · New Category',
    'np_total_units':        str(np_total_units),
    'np_total_rev':          fmt(np_total_rev),
    'drinks_n':              str(drinks_n),
    'drinks_todate_units':   str(drinks_total_units),
    'drinks_todate_rev':     fmt(drinks_total_rev),
    'drinks_yest':           str(drinks_yest_units),
    'drinks_yest_rev':       fmt(drinks_yest_rev),
    'fruit_n':               str(fruit_n),
    'fruit_todate_units':    str(fruit_total_units),
    'fruit_todate_rev':      fmt(fruit_total_rev),
    'fruit_yest':            str(fruit_yest_units),
    'fruit_yest_rev':        fmt(fruit_yest_rev),
    'new_cat_n':             str(new_cat_n),
    'new_cat_todate_units':  str(new_cat_total_units),
    'new_cat_todate_rev':    fmt(new_cat_total_rev),
    'new_cat_yest':          str(new_cat_yest_units),
    'new_cat_yest_rev':      fmt(new_cat_yest_rev),
    'grape_total_rev':       fmt(grape_total_rev),
    'grape_last_mw1':        grape_last_mw1,
    'grape_last_se3':        grape_last_se3,
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
