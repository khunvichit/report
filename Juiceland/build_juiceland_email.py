#!/usr/bin/env python3
"""
Build Juiceland Daily Sales Report email.html from query results.
Handles nested REPEATs correctly (fill_template.py cannot due to shared global repeat context).
Reads juiceland-template.html + juiceland-prediction-section.html, writes email.html.

Report date: 2026-06-15 (yesterday Asia/Bangkok)
Run date:    2026-06-16
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

REPORT_DATE = '2026-06-15'

# Query A — daily totals per branch over 30 days (17 May – 15 Jun 2026)
# Location 33 = MW1, 105 = SE3, 109 = PKT (169 rolled into MW1; no 169 data present)
QA = [
    ('2026-05-17', 33, 34754.0),   ('2026-05-17', 105, 35410.0),  ('2026-05-17', 109, 13484.0),
    ('2026-05-18', 33, 25913.0),   ('2026-05-18', 105, 22700.0),  ('2026-05-18', 109, 12484.0),
    ('2026-05-19', 33, 33034.5),   ('2026-05-19', 105, 25820.0),  ('2026-05-19', 109,  7867.0),
    ('2026-05-20', 33, 31093.0),   ('2026-05-20', 105, 17307.5),  ('2026-05-20', 109, 10311.0),
    ('2026-05-21', 33, 36940.5),   ('2026-05-21', 105, 29297.0),  ('2026-05-21', 109,  9611.0),
    ('2026-05-22', 33, 40088.0),   ('2026-05-22', 105, 26689.0),  ('2026-05-22', 109, 10358.0),
    ('2026-05-23', 33, 38639.5),   ('2026-05-23', 105, 39492.0),  ('2026-05-23', 109, 12698.0),
    ('2026-05-24', 33, 45429.5),   ('2026-05-24', 105, 28328.0),  ('2026-05-24', 109, 12933.0),
    ('2026-05-25', 33, 38221.0),   ('2026-05-25', 105, 31983.5),  ('2026-05-25', 109, 10502.0),
    ('2026-05-26', 33, 36852.5),   ('2026-05-26', 105, 24575.5),  ('2026-05-26', 109,  7039.0),
    ('2026-05-27', 33, 33877.0),   ('2026-05-27', 105, 26502.0),  ('2026-05-27', 109, 16234.0),
    ('2026-05-28', 33, 33415.0),   ('2026-05-28', 105, 31121.0),  ('2026-05-28', 109, 12474.0),
    ('2026-05-29', 33, 42210.5),   ('2026-05-29', 105, 22568.0),  ('2026-05-29', 109, 13844.0),
    ('2026-05-30', 33, 34788.0),   ('2026-05-30', 105, 26883.0),  ('2026-05-30', 109, 14605.0),
    ('2026-05-31', 33, 28583.0),   ('2026-05-31', 105, 32544.0),  ('2026-05-31', 109, 14052.0),
    ('2026-06-01', 33, 32133.0),   ('2026-06-01', 105, 24075.0),  ('2026-06-01', 109, 13940.0),
    ('2026-06-02', 33, 36476.0),   ('2026-06-02', 105, 15959.0),  ('2026-06-02', 109,  9920.0),
    ('2026-06-03', 33, 40024.0),   ('2026-06-03', 105, 19497.0),  ('2026-06-03', 109, 10813.0),
    ('2026-06-04', 33, 35666.5),   ('2026-06-04', 105, 16604.0),  ('2026-06-04', 109, 13146.0),
    ('2026-06-05', 33, 35611.0),   ('2026-06-05', 105, 20180.0),  ('2026-06-05', 109, 13589.0),
    ('2026-06-06', 33, 32714.0),   ('2026-06-06', 105, 23312.0),  ('2026-06-06', 109, 13867.0),
    ('2026-06-07', 33, 25977.0),   ('2026-06-07', 105, 17749.0),  ('2026-06-07', 109, 12993.0),
    ('2026-06-08', 33, 38857.0),   ('2026-06-08', 105, 24570.0),  ('2026-06-08', 109, 12810.0),
    ('2026-06-09', 33, 30612.5),   ('2026-06-09', 105, 12035.0),  ('2026-06-09', 109, 10190.0),
    ('2026-06-10', 33, 37665.0),   ('2026-06-10', 105, 22195.0),  ('2026-06-10', 109, 10250.0),
    ('2026-06-11', 33, 36938.0),   ('2026-06-11', 105, 18834.0),  ('2026-06-11', 109, 12373.0),
    ('2026-06-12', 33, 35377.5),   ('2026-06-12', 105, 25627.0),  ('2026-06-12', 109, 11753.0),
    ('2026-06-13', 33, 33715.0),   ('2026-06-13', 105, 25149.0),  ('2026-06-13', 109, 12259.0),
    ('2026-06-14', 33, 36683.0),   ('2026-06-14', 105, 18753.0),  ('2026-06-14', 109, 16361.0),
    ('2026-06-15', 33, 34196.0),   ('2026-06-15', 105, 22469.0),  ('2026-06-15', 109, 12234.0),
]

# Query B — Top 20 products per branch on 15 Jun (sorted by qty desc)
QB_MW1 = [
    ('EVIAN', 47, 5271.05, 4),
    ('WATERMELON JUICE BOTTLE', 10, 1728.98, 5),
    ('MANGO 400G.', 9, 1345.77, 3),
    ('S2 MANGO PASSION SMOOTHIE 22OZ', 8, 1383.20, 3),
    ('PRIDE PARROT RED', 8, 1476.65, 3),
    ('S2 MANGO PASSION SMOOTHIE 16OZ', 7, 1046.73, 2),
    ('Mango passion juice (Bottle) 300 ml', 7, 1210.29, 3),
    ('COCONUT JUICE BOTTLE', 7, 1210.29, 4),
    ('WATERMELON 400G.', 6, 841.13, 2),
    ('CARROT JUICE BOTTLE', 6, 1037.39, 3),
    ('COCONUT READY TO DRINK', 6, 953.28, 4),
    ('P1 GOLDEN GLOW 22OZ', 5, 1051.40, 3),
    ('S5 MANGO SMOOTHIE 22OZ', 5, 864.49, 2),
    ('C1 GUAVA&GREEN APPLE&RED APPLE COLD PREESED 22OZ', 4, 785.04, 2),
    ('S3 WATERMELON SMOOTHIE 16OZ', 3, 448.59, 2),
    ('BANANA YOGHURT SMOOTHIE 16OZ', 3, 490.65, 2),
    ('DRAGON FRUIT 400G.', 3, 420.57, 2),
    ('P2 GREEN BOOST 22OZ', 3, 630.84, 2),
    ('C3 WATERMELON COLD PREESED 16OZ', 3, 518.70, 3),
    ('SOFT-SLUSH! DELUXE', 2, 448.60, 1),
]
QB_SE3 = [
    ('EVIAN', 31, 3476.65, 5),
    ('3 kinds of fruit400g Papaya/Pineapple/Guava', 11, 1542.08, 3),
    ('PRIDE PARROT RED', 8, 1495.33, 3),
    ('WATERMELON 400G.', 8, 1121.51, 2),
    ('MANGO 400G.', 7, 1046.71, 3),
    ('PINEAPPLE 400G.', 6, 841.14, 2),
    ('COCONUT READY TO DRINK', 6, 953.28, 2),
    ('S2 MANGO PASSION SMOOTHIE 22OZ', 5, 864.49, 2),
    ('C2 ORANGE COLD PREESED 16OZ', 4, 691.59, 1),
    ('P1 GOLDEN GLOW 16OZ', 4, 747.68, 3),
    ('S2 MANGO PASSION SMOOTHIE 16OZ', 3, 448.60, 2),
    ('CH3 HOT CAPPUCCINO', 3, 420.57, 2),
    ('S6 BANANA SMOOTHIE 16OZ', 3, 448.60, 3),
    ('DRAGON FRUIT 400G.', 3, 420.57, 2),
    ('S5 MANGO SMOOTHIE 22OZ', 3, 518.70, 2),
    ('PRIDE PARROT YELLOW', 3, 560.75, 2),
    ('GUAVA 400G.', 3, 420.56, 2),
    ('COCONUT JUICE BOTTLE', 2, 345.79, 1),
    ('S3 WATERMELON SMOOTHIE 22OZ', 2, 345.80, 2),
    ('C4 MANGO PASSION COLD PREESED 16OZ', 2, 345.80, 2),
]
QB_PKT = [
    ('Evian 500ml. (Bottle)', 11, 1233.64, 2),
    ('Up size Smoothie & Cold Press Juice 16oz to 22oz', 10, 233.60, 3),
    ('Watermelon 400 g. (Pack)', 7, 981.32, 2),
    ('Coke Zero 500 ml. (Bottle)', 6, 448.61, 2),
    ('Coke 500 ml. (Bottle)', 4, 299.07, 1),
    ('Coconut (EA)', 4, 635.52, 2),
    ('Mango 400 g. (Pack)', 4, 598.12, 2),
    ('P1 Mango passion fruit cold pressed 16oz', 3, 560.76, 1),
    ('S5 mango smoothie 16oz', 3, 448.60, 2),
    ('Chicken Ham Sandwich', 3, 504.67, 2),
    ('YS2 Strawberry yoghurt smoothie 16oz', 3, 490.65, 3),
    ('Pineapple 400 g. (Pack)', 2, 280.38, 1),
    ('C2 orange cold pressed 16oz', 2, 345.80, 1),
    ('T1 Iced Thai milk tea 16oz', 2, 280.38, 1),
    ('CI5 Iced Latte 16oz', 2, 317.76, 1),
    ('C5 pineapple & green apple cold pressed 16oz', 2, 345.80, 2),
    ('P2 pineapple kale cold pressed 16oz', 2, 373.84, 1),
    ('Fanta Strawberry 450 ml. (Bottle)', 1, 74.77, 1),
    ('S1 Coconut smoothie 16oz', 1, 168.23, 1),
    ('Mango juice (Bottle) 300 ml', 1, 172.90, 1),
]

# Dormant SKUs (Query D filtered: qty_30d >= 3, no malformed memos, no noise)
# (memo, last_sold_str, qty_30d, days_sold_30d, rev_30d)
DORMANT_MW1 = [
    ('MAEVAREE MANGO STICKY RICE SMOOTHIE 22OZ', '2026-06-08', 37, 17, 7910.18),
    ('Overnight Oat mango 16 oz',                '2026-06-06', 27, 15, 6787.80),
    ('HOT CHOCOLATE 8 oz',                       '2026-05-27', 18,  4, 2186.96),
    ('SHINE MUSCAT GRAPES 400G (PACK)',           '2026-05-21', 12,  5, 1794.36),
    ('VANILLA BEAN GREEK YOGURT',                '2026-05-26', 11,  8, 1943.01),
    ('BLUEBERRY GREEK YOGURT',                   '2026-06-05',  9,  7, 1589.75),
    ('Mango Berry Smoothie 16oz',                '2026-05-26',  5,  4,  864.50),
    ('T2 ICED THAI TEA WITH LIME 16OZ',          '2026-06-01',  5,  4,  700.94),
    ('RASPBERRY GREEK YOGURT',                   '2026-05-22',  5,  4,  883.16),
    ('CAESAR SALAD',                             '2026-05-29',  4,  3,  672.88),
    ('Mango Pineapple Smoothie 16oz',            '2026-05-23',  4,  2,  691.59),
    ('Mango Sticky Rice (Box)',                  '2026-06-01',  3,  3,  501.85),
]
DORMANT_SE3 = [
    ('HOT CHOCOLATE 8 oz',          '2026-05-29', 22,  6, 2672.98),
    ('Mango Sticky Rice (Box)',      '2026-05-31', 19,  8, 3178.51),
    ('P2 GREEN BOOST 16OZ',         '2026-06-07', 19, 12, 3551.45),
    ('Golden Harmony Greek Yogurt', '2026-05-31', 17,  8, 3002.81),
    ('MANGO PINEAPPLE SMOOTHIE 16OZ','2026-05-31', 11,  6, 1901.90),
    ('BANANA YOGHURT SMOOTHIE 16OZ','2026-05-28',  7,  6, 1144.85),
    ('CI3 ICED AMERICANO 22OZ',     '2026-06-08',  7,  6, 1177.54),
    ('Overnight Oat Berry 16 oz',   '2026-05-27',  7,  5, 1694.40),
    ('CH1 ESPRESSO',                '2026-06-05',  6,  5,  700.92),
    ('CI4 ICED CAPPUCCINO 22OZ',    '2026-05-30',  5,  4,  911.20),
    ('Overnight Oat mango 16 oz',   '2026-06-04',  5,  5, 1257.00),
    ('SEEDLESS GRAPE 400G.',        '2026-06-08',  5,  2,  747.65),
    ('MANGO BERRY SMOOTHIE 16OZ',   '2026-05-19',  4,  3,  691.60),
    ('CARROT JUICE BOTTLE',         '2026-06-02',  3,  3,  518.69),
    ('MANGOSTEEN 400g.',            '2026-06-01',  3,  3,  700.92),
]
DORMANT_PKT = [
    ('C6 pineapple cold pressed 16oz',          '2026-06-07', 17, 13, 2939.32),
    ('Banana 2PCS.',                             '2026-06-06', 17, 14,  937.38),
    ('Ebiko salad Japanese Rice Balls (Onigiri)','2026-06-08',  8,  5,  814.96),
    ('Mango Pineapple Smoothie 16oz',            '2026-05-28',  8,  6, 1383.22),
    ('Nestle Water 600 ml',                      '2026-06-06',  4,  4,   37.40),
    ('singha soda water 325ml',                  '2026-06-04',  4,  2,  243.00),
    ('Orange Cold Pressed Juice 300 ml. (bottle)','2026-05-27', 3,  3,  518.69),
]

# AM review items — top 5 high-value dormants needing manager attention
AM_ITEMS = [
    {
        'memo':             'MAEVAREE MANGO STICKY RICE SMOOTHIE 22OZ',
        'last_sold':        '8 Jun 2026',
        'gap_days':         '7',
        'velocity_7d':      '2.2',
        'target':           '1.2',
        'branch_split':     'MW1 only',
        'hypothesis_color': '#E65100',
        'hypothesis_text':  'Stock-out? Was top SKU — 37 units in 30d',
    },
    {
        'memo':             'Overnight Oat mango 16 oz',
        'last_sold':        '6 Jun 2026',
        'gap_days':         '9',
        'velocity_7d':      '1.8',
        'target':           '0.9',
        'branch_split':     'MW1 (+ SE3 until 4 Jun)',
        'hypothesis_color': '#E65100',
        'hypothesis_text':  'Sold-out or reduced order?',
    },
    {
        'memo':             'P2 GREEN BOOST 16OZ',
        'last_sold':        '7 Jun 2026',
        'gap_days':         '8',
        'velocity_7d':      '1.6',
        'target':           '0.6',
        'branch_split':     'SE3 only',
        'hypothesis_color': '#E65100',
        'hypothesis_text':  'Stock-out likely — check SE3',
    },
    {
        'memo':             'C6 pineapple cold pressed 16oz',
        'last_sold':        '7 Jun 2026',
        'gap_days':         '8',
        'velocity_7d':      '1.3',
        'target':           '0.6',
        'branch_split':     'PKT only',
        'hypothesis_color': '#E65100',
        'hypothesis_text':  'Stock-out? Was top-5 at PKT',
    },
    {
        'memo':             'Banana 2PCS.',
        'last_sold':        '6 Jun 2026',
        'gap_days':         '9',
        'velocity_7d':      '1.2',
        'target':           '0.6',
        'branch_split':     'PKT only',
        'hypothesis_color': '#E65100',
        'hypothesis_text':  'Stock-out or seasonal?',
    },
]

# ─────────────────── computations ───────────────────

from datetime import date, timedelta
import math

report_date  = date(2026, 6, 15)
run_date     = date(2026, 6, 16)
window_start = report_date - timedelta(days=29)

# Build day-keyed lookup for QA
from collections import defaultdict
daily = defaultdict(lambda: {33: 0.0, 105: 0.0, 109: 0.0})
for d_str, loc, net in QA:
    d = date.fromisoformat(d_str)
    daily[d][loc] += net

dates_sorted = sorted(daily.keys())

mw1  = {d: daily[d][33]  for d in dates_sorted}
se3  = {d: daily[d][105] for d in dates_sorted}
pkt  = {d: daily[d][109] for d in dates_sorted}
comb = {d: mw1[d] + se3[d] + pkt[d] for d in dates_sorted}

yest      = report_date
mw1_yest  = mw1[yest];  se3_yest = se3[yest];  pkt_yest = pkt[yest]
comb_yest = mw1_yest + se3_yest + pkt_yest

mw1_avg  = sum(mw1.values()) / 30
se3_avg  = sum(se3.values()) / 30
pkt_avg  = sum(pkt.values()) / 30
comb_avg = mw1_avg + se3_avg + pkt_avg

mw1_min = min(mw1.values());  mw1_max = max(mw1.values())
se3_min = min(se3.values());  se3_max = max(se3.values())
pkt_min = min(pkt.values());  pkt_max = max(pkt.values())

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
EN_MONTH      = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
EN_MONTH_FULL = ['January','February','March','April','May','June',
                 'July','August','September','October','November','December']

def th_weekday_abbr(d): return TH_WD[d.weekday()]
def en_day_display(d):  return f'{d.day} {EN_MONTH_FULL[d.month-1]}'

report_date_display    = f'{report_date.day} {EN_MONTH_FULL[report_date.month-1]} {report_date.year}'
report_day_th          = TH_WD_FULL[report_date.weekday()]
window_30d_start_display = f'{window_start.day} {EN_MONTH_FULL[window_start.month-1]} {window_start.year}'

last7_dates = dates_sorted[-7:]

mw1_7d    = sum(mw1[d] for d in last7_dates)
se3_7d    = sum(se3[d] for d in last7_dates)
pkt_7d    = sum(pkt[d] for d in last7_dates)
comb_7d   = mw1_7d + se3_7d + pkt_7d
last7_avg_val = comb_7d / 7

# ─── FORECAST (today = Tuesday 2026-06-16) ───
fc_date = run_date   # Tuesday

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

def forecast_branch(wday_vals, branch_vals, all_dates):
    base    = sum(wday_vals) / len(wday_vals) if wday_vals else 0
    last7v  = [branch_vals[d] for d in all_dates[-7:]]
    trend   = (base + sum(last7v) / 7) / 2
    stdev   = math.sqrt(sum((x - base)**2 for x in wday_vals) / len(wday_vals)) if len(wday_vals) > 1 else base * 0.12
    band    = max(stdev, trend * 0.08)
    conf_pct = stdev / base * 100 if base else 25
    conf_dot = '🟢' if conf_pct < 12 else ('🟡' if conf_pct < 25 else '🔴')
    return trend, band, conf_dot

mw1_fc, mw1_band, mw1_conf = forecast_branch(mw1_tue, mw1, dates_sorted)
se3_fc, se3_band, se3_conf = forecast_branch(se3_tue, se3, dates_sorted)
pkt_fc, pkt_band, pkt_conf = forecast_branch(pkt_tue, pkt, dates_sorted)

comb_fc       = mw1_fc + se3_fc + pkt_fc
comb_band     = math.sqrt(mw1_band**2 + se3_band**2 + pkt_band**2)
comb_conf_pct = comb_band / comb_fc * 100 if comb_fc else 25
comb_conf     = '🟢' if comb_conf_pct < 12 else ('🟡' if comb_conf_pct < 25 else '🔴')

# ─── NEW PRODUCTS (from Query C) ───

# Drinks — to-date cumulative totals
NP_DRINKS_ROWS = [
    {'memo': 'PRIDE PARROT RED', 'launch': '1 Jun 2026', 'notes': 'MW1, SE3, PKT',
     'total_units': 159, 'total_rev': '29,664', 'branch_split': 'MW1: 98u · SE3: 48u · PKT: 13u',
     'yest_units': 16, 'status_badge': '🟢 scaling — day 15'},
    {'memo': 'PRIDE PARROT YELLOW', 'launch': '1 Jun 2026', 'notes': 'MW1, SE3, PKT',
     'total_units': 92, 'total_rev': '17,158', 'branch_split': 'MW1: 63u · SE3: 22u · PKT: 7u',
     'yest_units': 5, 'status_badge': '🟢 on target'},
    {'memo': 'HOT CHOCOLATE 8 oz', 'launch': '24 May 2026', 'notes': 'MW1, SE3 — now dormant',
     'total_units': 40, 'total_rev': '4,860', 'branch_split': 'MW1: 18u · SE3: 22u',
     'yest_units': 0, 'status_badge': '🔴 dormant — 19d (MW1) / 17d (SE3)'},
    {'memo': 'MOOVE CLEAR PROTEIN', 'launch': '13 Jun 2026', 'notes': 'MW1 only',
     'total_units': 15, 'total_rev': '2,103', 'branch_split': 'MW1 only',
     'yest_units': 2, 'status_badge': '🟢 new launch — day 3'},
    {'memo': 'Fanta Strawberry 450 ml. (Bottle)', 'launch': '1 Jun 2026', 'notes': 'PKT only',
     'total_units': 19, 'total_rev': '1,421', 'branch_split': 'PKT only',
     'yest_units': 1, 'status_badge': '🟢 on target'},
    {'memo': 'Sprite 500 ml. (Bottle)', 'launch': '30 May 2026', 'notes': 'PKT only',
     'total_units': 19, 'total_rev': '1,421', 'branch_split': 'PKT only',
     'yest_units': 1, 'status_badge': '🟢 on target'},
    {'memo': 'Fanta Orange 450 ml. (Bottle)', 'launch': '31 May 2026', 'notes': 'PKT only',
     'total_units': 17, 'total_rev': '1,271', 'branch_split': 'PKT only',
     'yest_units': 0, 'status_badge': '⚪ not sold yesterday (last: 13 Jun)'},
    {'memo': 'HOT MOCHA 8 oz', 'launch': '20 May 2026', 'notes': 'MW1 — now dormant',
     'total_units': 2, 'total_rev': '252', 'branch_split': 'MW1 only',
     'yest_units': 0, 'status_badge': '🔴 dormant — 24d'},
    {'memo': 'Fanta Fruit Punch 450 ml. (Bottle)', 'launch': '31 May 2026', 'notes': 'PKT — 1 day only',
     'total_units': 1, 'total_rev': '75', 'branch_split': 'PKT',
     'yest_units': 0, 'status_badge': '🔴 dormant'},
    {'memo': 'Iced Espresso Orange 12oz', 'launch': '29 May 2026', 'notes': 'SE3 — dormant',
     'total_units': 1, 'total_rev': '168', 'branch_split': 'SE3 only',
     'yest_units': 0, 'status_badge': '🔴 dormant — 17d'},
]

NP_FRUIT_ROWS = [
    {'memo': 'LYCHEE 400G.', 'launch': '28 May 2026', 'notes': 'MW1, SE3',
     'total_units': 33, 'total_rev': '5,243', 'branch_split': 'MW1: 13u · SE3: 20u',
     'yest_units': 2, 'status_badge': '🟢 on target'},
    {'memo': 'ROSE APPLE 400G.', 'launch': '30 May 2026', 'notes': 'SE3 only',
     'total_units': 9, 'total_rev': '946', 'branch_split': 'SE3 only',
     'yest_units': 1, 'status_badge': '🟢 on target'},
    {'memo': 'MANGOSTEEN 400g.', 'launch': '28 May 2026', 'notes': 'SE3 + MW1 sparse',
     'total_units': 4, 'total_rev': '935', 'branch_split': 'SE3: 3u · MW1: 1u',
     'yest_units': 0, 'status_badge': '⚠️ slow — 14d since last SE3 sale'},
]

NP_NEWCAT_ROWS = [
    {'memo': 'Overnight Oat mango 16 oz', 'launch': '21 May 2026', 'notes': 'MW1, SE3 — now dormant',
     'total_units': 32, 'total_rev': '8,045', 'branch_split': 'MW1: 27u · SE3: 5u',
     'yest_units': 0, 'status_badge': '🔴 dormant — 9d'},
    {'memo': 'Chicken Club Croissant', 'launch': '22 May 2026', 'notes': 'SE3 only',
     'total_units': 30, 'total_rev': '4,178', 'branch_split': 'SE3 only',
     'yest_units': 1, 'status_badge': '🟢 on target'},
    {'memo': 'Overnight Oat Berry 16 oz', 'launch': '22 May 2026', 'notes': 'SE3 + MW1 — dormant',
     'total_units': 8, 'total_rev': '1,936', 'branch_split': 'SE3: 7u · MW1: 1u',
     'yest_units': 0, 'status_badge': '🔴 dormant — 19d'},
    {'memo': 'HONEY TOPPING', 'launch': '18 May 2026', 'notes': 'MW1',
     'total_units': 7, 'total_rev': '164', 'branch_split': 'MW1 only',
     'yest_units': 0, 'status_badge': '⚪ sporadic'},
    {'memo': 'CAESAR SALAD', 'launch': '18 May 2026', 'notes': 'MW1 — dormant',
     'total_units': 4, 'total_rev': '673', 'branch_split': 'MW1 only',
     'yest_units': 0, 'status_badge': '🔴 dormant — 17d'},
    {'memo': 'JAPANESE SALAD', 'launch': '16 May 2026', 'notes': 'MW1 — dormant',
     'total_units': 2, 'total_rev': '336', 'branch_split': 'MW1 only',
     'yest_units': 0, 'status_badge': '🔴 dormant — 27d'},
    {'memo': 'GRANOLA TOPPING', 'launch': '20 May 2026', 'notes': 'MW1 — dormant',
     'total_units': 2, 'total_rev': '47', 'branch_split': 'MW1 only',
     'yest_units': 0, 'status_badge': '🔴 dormant'},
    {'memo': 'BANANA TOPPING', 'launch': '12 Jun 2026', 'notes': 'MW1',
     'total_units': 1, 'total_rev': '23', 'branch_split': 'MW1 only',
     'yest_units': 0, 'status_badge': '⚪ new — minimal data'},
    {'memo': 'SEEDLESS GRAPE TOPPING', 'launch': '5 Jun 2026', 'notes': 'MW1',
     'total_units': 1, 'total_rev': '23', 'branch_split': 'MW1 only',
     'yest_units': 0, 'status_badge': '⚪ minimal data'},
]

drinks_total_units = sum(r['total_units'] for r in NP_DRINKS_ROWS)
drinks_total_rev   = 58393
drinks_n           = 10
drinks_yest_units  = sum(r['yest_units'] for r in NP_DRINKS_ROWS)
drinks_yest_rev    = 4337

fruit_total_units  = sum(r['total_units'] for r in NP_FRUIT_ROWS)
fruit_total_rev    = 7124
fruit_n            = 3
fruit_yest_units   = sum(r['yest_units'] for r in NP_FRUIT_ROWS)
fruit_yest_rev     = 467

new_cat_total_units = sum(r['total_units'] for r in NP_NEWCAT_ROWS)
new_cat_total_rev   = 15425
new_cat_n           = len(NP_NEWCAT_ROWS)
new_cat_yest_units  = sum(r['yest_units'] for r in NP_NEWCAT_ROWS)
new_cat_yest_rev    = 139

np_total_units = drinks_total_units + fruit_total_units + new_cat_total_units
np_total_rev   = drinks_total_rev + fruit_total_rev + new_cat_total_rev

# ─── SEASONAL (Query E + Query C fruit data) ───
grape_total_rev  = 238740   # SHINE MUSCAT both branches combined (all-time through May)
grape_last_mw1   = '11 Jun 2026'   # SEEDLESS GRAPE 400G. last sold at MW1
grape_last_se3   = '8 Jun 2026'    # SEEDLESS GRAPE 400G. last sold at SE3

# Seasonal fruit revenue in 30-day window (17 May – 15 Jun)
mw1_fruit_rev = 2065.44 + 233.65          # LYCHEE + MANGOSTEEN at MW1
se3_fruit_rev = 3177.59 + 700.92 + 945.79  # LYCHEE + MANGOSTEEN + ROSE APPLE at SE3

mw1_fruit_per_day  = mw1_fruit_rev / 30   # 76.6/d
se3_fruit_per_day  = se3_fruit_rev / 30   # 160.8/d

mw1_grape_baseline = 339
se3_grape_baseline = 251

mw1_coverage = mw1_fruit_per_day / mw1_grape_baseline * 100   # 22.6%
se3_coverage = se3_fruit_per_day / se3_grape_baseline * 100   # 64.1%

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
def gap_days_calc(last_sold_str):
    return (report_date - date.fromisoformat(last_sold_str)).days

def gap_color(days):
    return '#C62828' if days >= 14 else '#E65100'

def truncate(s, n=34):
    return (s[:n] + '…') if len(s) > n else s

def dormant_rows_for(branch_list):
    rows = []
    for memo, last_str, qty, days_sold, rev in branch_list:
        g = gap_days_calc(last_str)
        rows.append({
            'memo_display':  truncate(memo),
            'memo_full':     memo,
            'qty_30d':       fmt(qty),
            'days_sold_30d': str(days_sold),
            'rev_30d':       fmt(round(rev)),
            'gap_days':      str(g),
            'gap_color':     gap_color(g),
        })
    return rows

dormant_count = len(DORMANT_MW1) + len(DORMANT_SE3) + len(DORMANT_PKT)
am_queue_count = len(AM_ITEMS)

# ─── PREDICTION ───
commentary_text = (
    f'Yesterday (15 June 2026 · วันจันทร์), combined net was ฿{fmt(comb_yest)} ex-VAT, '
    f'{abs(signed_pct):.1f}% {"above" if signed_pct >= 0 else "below"} the 30-day average '
    f'of ฿{fmt(comb_avg)}. MW1 came in at ฿{fmt(mw1_yest)} ({mw1_vs30:+.1f}% vs avg), '
    f'SE3 at ฿{fmt(se3_yest)} ({se3_vs30:+.1f}% vs avg), PKT at ฿{fmt(pkt_yest)} '
    f'({pkt_vs30:+.1f}% vs avg). All three branches finished within normal range. '
    f'PRIDE PARROT RED drove the strongest new-product volume: 8 units at MW1 and 8 at SE3 '
    f'(฿2,972 combined) on day 15 since launch.'
)

anomaly_items_list = [
    {'anomaly_text': f'{dormant_count} dormant SKUs across all branches — {am_queue_count} high-value (≥10u/mo)',
     'anomaly_section_ref': 'Dormant §7'},
    {'anomaly_text': f'Seasonal fruit coverage: MW1 {mw1_coverage:.0f}% / SE3 {se3_coverage:.0f}% of grape baseline',
     'anomaly_section_ref': 'Seasonal §6'},
    {'anomaly_text': f'SE3 Tuesdays highly variable (฿12K–฿39K range in 30d) — 9 Jun was ฿12,035',
     'anomaly_section_ref': 'Chart §3'},
    {'anomaly_text': f'PRIDE PARROT RED scaling well — 16 units / ฿2,972 at MW1+SE3 yesterday',
     'anomaly_section_ref': 'New Products §4'},
    {'anomaly_text': f'MOOVE CLEAR PROTEIN new at MW1 (13 Jun) — 15u in 3 days, strong start',
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
    return [
        {'net': fmt(branch_dict[d]),
         'cell_style': 'background:#FFF3E0;font-weight:700;' if d == report_date else ''}
        for d in last7_dates
    ]

def last7_comb_cells():
    return [
        {'net': fmt(comb[d]),
         'cell_bg': 'background:#FFF3E0;' if d == report_date else ''}
        for d in last7_dates
    ]

def top20_rows_build(items):
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
    {'header_color': '#5551FE', 'header_label': 'MW1 · 26-T1MW1-03+04',
     'top20_rows': top20_rows_build(QB_MW1)},
    {'header_color': '#F27061', 'header_label': 'SE3 · 27-T1SE3-05',
     'top20_rows': top20_rows_build(QB_SE3)},
    {'header_color': '#2E7D32', 'header_label': 'PKT · 28 Unit 362 (Phuket)',
     'top20_rows': top20_rows_build(QB_PKT)},
]

np_type_tables = [
    {'type_bg': '#1976D2', 'type_fg': '#fff', 'type_icon': '🥤',
     'type_label': 'Drinks', 'np_rows': NP_DRINKS_ROWS},
    {'type_bg': '#AD1457', 'type_fg': '#fff', 'type_icon': '🍉',
     'type_label': 'Seasonal Fruits', 'np_rows': NP_FRUIT_ROWS},
    {'type_bg': '#2E7D32', 'type_fg': '#fff', 'type_icon': '⭐',
     'type_label': 'New Category', 'np_rows': NP_NEWCAT_ROWS},
]

seasonal_skus = [
    {'fruit_emoji': '🍒', 'memo': 'LYCHEE 400G.', 'launch': '28 May 2026',
     'mw1_units': '13', 'mw1_per_day': f'{2065.44/30:.0f}',
     'se3_units': '20', 'se3_per_day': f'{3177.59/30:.0f}'},
    {'fruit_emoji': '🟣', 'memo': 'MANGOSTEEN 400g.', 'launch': '28 May 2026',
     'mw1_units': '1',  'mw1_per_day': f'{233.65/30:.0f}',
     'se3_units': '3',  'se3_per_day': f'{700.92/30:.0f}'},
    {'fruit_emoji': '🌸', 'memo': 'ROSE APPLE 400G.', 'launch': '30 May 2026',
     'mw1_units': '—',  'mw1_per_day': '0',
     'se3_units': '9',  'se3_per_day': f'{945.79/30:.0f}'},
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

dormant_branches = [
    {'branch': 'MW1', 'header_color': '#5551FE', 'branch_count': str(len(DORMANT_MW1)),
     'dormant_rows': dormant_rows_for(DORMANT_MW1)},
    {'branch': 'SE3', 'header_color': '#F27061', 'branch_count': str(len(DORMANT_SE3)),
     'dormant_rows': dormant_rows_for(DORMANT_SE3)},
    {'branch': 'PKT', 'header_color': '#2E7D32', 'branch_count': str(len(DORMANT_PKT)),
     'dormant_rows': dormant_rows_for(DORMANT_PKT)},
]

am_items = AM_ITEMS

# ─────────────────── assemble scalars ───────────────────

scalars = {
    'report_date':          REPORT_DATE,
    'report_date_display':  report_date_display,
    'report_day_th':        report_day_th,
    'window_30d_start':     window_30d_start_display,
    'generated_timestamp':  '2026-06-16 07:05',
    'subject_prefix':       subject_prefix,
    'comb_net':             fmt(comb_yest),
    'signed_pct':           f'{signed_pct:+.1f}',
    'am_queue_count':       str(am_queue_count),
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
    'np_summary_line':      '29 new SKUs launched May–Jun 2026 · Drinks · Seasonal Fruits · New Category',
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
    # Forecast scalars
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
    'anomaly_count': str(len(anomaly_items_list)),
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
    'am_items':          am_items,
    'anomaly_items':     anomaly_items_list,
}

sections = {
    'am_review':           am_queue_count > 0,
    'seasonal':            True,
    'dormant':             dormant_count > 0,
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
print('OK')
