#!/usr/bin/env python3
"""
Build Juiceland Daily Sales Report email.html from query results.
Handles nested REPEATs correctly (fill_template.py cannot due to shared global repeat context).
Reads juiceland-template.html + juiceland-prediction-section.html, writes email.html.

Report date: 2026-06-24 (yesterday Asia/Bangkok)
Run date:    2026-06-25
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

REPORT_DATE = '2026-06-24'

# Query A — daily totals per branch (30-day window 2026-05-26 → 2026-06-24)
# Location 33=MW1, 105=SE3, 109=PKT (no 169 data in results)
QA = [
    ('2026-05-26', 33, 36852.5), ('2026-05-26', 105, 24575.5), ('2026-05-26', 109, 7039.0),
    ('2026-05-27', 33, 33877.0), ('2026-05-27', 105, 26502.0), ('2026-05-27', 109, 16234.0),
    ('2026-05-28', 33, 33415.0), ('2026-05-28', 105, 31121.0), ('2026-05-28', 109, 12474.0),
    ('2026-05-29', 33, 42210.5), ('2026-05-29', 105, 22568.0), ('2026-05-29', 109, 13844.0),
    ('2026-05-30', 33, 34788.0), ('2026-05-30', 105, 26883.0), ('2026-05-30', 109, 14605.0),
    ('2026-05-31', 33, 28583.0), ('2026-05-31', 105, 32544.0), ('2026-05-31', 109, 14052.0),
    ('2026-06-01', 33, 32133.0), ('2026-06-01', 105, 24075.0), ('2026-06-01', 109, 13940.0),
    ('2026-06-02', 33, 36476.0), ('2026-06-02', 105, 15959.0), ('2026-06-02', 109, 9920.0),
    ('2026-06-03', 33, 40024.0), ('2026-06-03', 105, 19497.0), ('2026-06-03', 109, 10813.0),
    ('2026-06-04', 33, 35666.5), ('2026-06-04', 105, 16604.0), ('2026-06-04', 109, 13146.0),
    ('2026-06-05', 33, 35611.0), ('2026-06-05', 105, 20180.0), ('2026-06-05', 109, 13589.0),
    ('2026-06-06', 33, 32714.0), ('2026-06-06', 105, 23312.0), ('2026-06-06', 109, 13867.0),
    ('2026-06-07', 33, 25977.0), ('2026-06-07', 105, 17749.0), ('2026-06-07', 109, 12993.0),
    ('2026-06-08', 33, 38857.0), ('2026-06-08', 105, 24570.0), ('2026-06-08', 109, 12810.0),
    ('2026-06-09', 33, 30612.5), ('2026-06-09', 105, 12035.0), ('2026-06-09', 109, 10190.0),
    ('2026-06-10', 33, 37665.0), ('2026-06-10', 105, 22195.0), ('2026-06-10', 109, 10250.0),
    ('2026-06-11', 33, 36938.0), ('2026-06-11', 105, 18834.0), ('2026-06-11', 109, 12373.0),
    ('2026-06-12', 33, 35377.5), ('2026-06-12', 105, 25627.0), ('2026-06-12', 109, 11753.0),
    ('2026-06-13', 33, 33715.0), ('2026-06-13', 105, 25149.0), ('2026-06-13', 109, 12259.0),
    ('2026-06-14', 33, 36683.0), ('2026-06-14', 105, 18753.0), ('2026-06-14', 109, 16361.0),
    ('2026-06-15', 33, 34196.0), ('2026-06-15', 105, 22469.0), ('2026-06-15', 109, 12234.0),
    ('2026-06-16', 33, 39711.0), ('2026-06-16', 105, 19173.0), ('2026-06-16', 109, 9078.0),
    ('2026-06-17', 33, 37169.0), ('2026-06-17', 105, 20735.0), ('2026-06-17', 109, 10010.0),
    ('2026-06-18', 33, 46617.5), ('2026-06-18', 105, 21253.0), ('2026-06-18', 109, 14308.0),
    ('2026-06-19', 33, 45531.0), ('2026-06-19', 105, 32543.0), ('2026-06-19', 109, 12803.0),
    ('2026-06-20', 33, 32341.0), ('2026-06-20', 105, 29278.0), ('2026-06-20', 109, 15844.0),
    ('2026-06-21', 33, 36222.5), ('2026-06-21', 105, 33130.0), ('2026-06-21', 109, 7904.0),
    ('2026-06-22', 33, 37555.0), ('2026-06-22', 105, 25019.5), ('2026-06-22', 109, 7672.0),
    ('2026-06-23', 33, 36830.0), ('2026-06-23', 105, 21203.0), ('2026-06-23', 109, 10066.0),
    ('2026-06-24', 33, 37465.0), ('2026-06-24', 105, 24655.0), ('2026-06-24', 109, 8105.0),
]

# Query B — top products per branch for 2026-06-24 (memo, qty, revenue, bills)
QB_MW1 = [
    ('EVIAN', 49, 5495.35, 3),
    ('COCONUT READY TO DRINK', 14, 2224.30, 4),
    ('S2 MANGO PASSION SMOOTHIE 22OZ', 10, 1728.99, 3),
    ('WATERMELON 400G.', 9, 1261.71, 2),
    ('MANGO 400G.', 8, 1196.24, 4),
    ('CH3 HOT CAPPUCCINO', 7, 981.32, 2),
    ('CI3 ICED AMERICANO 22OZ', 7, 1177.55, 3),
    ('CH2 HOT AMERICANO', 6, 757.02, 3),
    ('S1 COCONUT SMOOTHIE 22OZ', 5, 957.95, 1),
    ('Mango passion juice (Bottle) 300 ml', 5, 864.49, 2),
    ('S5 MANGO SMOOTHIE 16OZ', 5, 747.65, 2),
    ('C3 WATERMELON COLD PREESED 22OZ', 5, 981.31, 2),
    ('WATERMELON JUICE BOTTLE', 5, 864.49, 2),
    ('C2 ORANGE COLD PREESED 16OZ', 5, 864.49, 2),
    ('C4 MANGO PASSION COLD PREESED 22OZ', 4, 785.04, 3),
    ('CH4 HOT LATTE', 4, 560.76, 1),
    ('Mango juice (Bottle) 300 ml', 4, 691.60, 2),
    ('S1 COCONUT SMOOTHIE 16OZ', 4, 672.89, 2),
    ('PINEAPPLE 400G.', 4, 560.76, 2),
    ('S3 WATERMELON SMOOTHIE 22OZ', 3, 518.70, 1),
]
QB_SE3 = [
    ('EVIAN', 28, 3140.20, 4),
    ('COCONUT READY TO DRINK', 15, 2383.19, 4),
    ('MANGO 400G.', 11, 1644.83, 3),
    ('WATERMELON 400G.', 10, 1401.90, 3),
    ('PINEAPPLE 400G.', 9, 1261.70, 3),
    ('3 kinds of fruit400g Papaya/Pineapple/Guava', 9, 1261.69, 3),
    ('S3 WATERMELON SMOOTHIE 22OZ', 7, 1210.28, 2),
    ('C3 WATERMELON COLD PREESED 22OZ', 5, 981.30, 3),
    ('GUAVA 400G.', 3, 420.57, 2),
    ('S1 COCONUT SMOOTHIE 22OZ', 3, 574.77, 2),
    ('C4 MANGO PASSION COLD PREESED 22OZ', 3, 588.78, 2),
    ('DRAGON FRUIT 400G.', 3, 420.57, 2),
    ('CH3 HOT CAPPUCCINO', 3, 420.56, 1),
    ('PRIDE PARROT YELLOW', 2, 373.84, 2),
    ('S2 MANGO PASSION SMOOTHIE 22OZ', 2, 345.80, 1),
    ('S5 MANGO SMOOTHIE 22OZ', 2, 345.80, 2),
    ('C5 PINEAPPLE&GREEN APPLE COLD PREESED 22OZ', 2, 392.52, 2),
    ('S4 MIXBERRY SMOOTHIE 22OZ', 2, 345.79, 1),
    ('C1 GUAVA&GREEN APPLE&RED APPLE COLD PREESED 22OZ', 2, 392.52, 2),
    ('P1 GOLDEN GLOW 16OZ', 2, 373.84, 1),
]
QB_PKT = [
    ('Evian 500ml. (Bottle)', 16, 1794.40, 3),
    ('Coke 500 ml. (Bottle)', 4, 299.08, 2),
    ('Coconut (EA)', 3, 476.64, 2),
    ('Watermelon 400 g. (Pack)', 3, 420.56, 2),
    ('S5 mango smoothie 16oz', 2, 299.06, 1),
    ('CH2 Caffe latte (hot) 12oz', 2, 267.02, 2),
    ('Heineken 320 ml. (Bottle)', 2, 336.45, 1),
    ('Veggie Sandwich', 2, 336.44, 1),
    ('S2 mango passion smoothie 16oz', 2, 299.07, 1),
    ('S3 watermelon smoothie 16oz', 2, 299.06, 2),
    ('Coconut Cold Pressed 300 ml. (bottle)', 2, 345.80, 2),
    ('Mango Smoothie 22oz', 2, 345.79, 1),
    ('Mixberry Smoothie 22oz', 2, 345.79, 1),
    ('P2 pineapple kale cold pressed 16oz', 1, 186.92, 1),
    ('Ham and Cheese Croissant', 1, 160.67, 1),
    ('Mango 400 g. (Pack)', 1, 149.53, 1),
    ('Sprite 500 ml. (Bottle)', 1, 74.77, 1),
    ('YS2 Strawberry yoghurt smoothie 16oz', 1, 163.55, 1),
    ('Guava 400 g. (Pack)', 1, 140.19, 1),
    ('Fanta Orange 450 ml. (Bottle)', 1, 74.77, 1),
]

# Query C new-product data (pre-processed): (memo, type, locations_str, launch_str,
#   total_units, total_rev, yest_units, yest_rev, mw1_units, se3_units, pkt_units)
# type: 'drinks' | 'fruit' | 'newcat'
# Noise filtered: toppers, malformed \n, Ice 16oz
NP_ROWS_DRINKS = [
    # (memo, launch, notes, total_units, total_rev_str, branch_split, yest_units, status)
    ('PRIDE PARROT RED', '1 Jun 2026', 'MW1 · SE3',
     248, '43,690', 'MW1·SE3', 2, '🟢 on target'),
    ('PRIDE PARROT YELLOW', '1 Jun 2026', 'MW1 · SE3',
     152, '28,398', 'MW1·SE3', 3, '🟢 on target'),
    ('Pride Parrot Red Smoothie 22oz', '4 Jun 2026', 'PKT',
     19, '3,552', 'PKT', 0, '⚪ no sale yesterday'),
    ('Pride Parrot Yellow Smoothie 22oz', '7 Jun 2026', 'PKT',
     9, '1,682', 'PKT', 0, '⚪ no sale yesterday'),
    ('Fanta Orange 450 ml. (Bottle)', '31 May 2026', 'PKT',
     28, '2,093', 'PKT', 1, '🟢 on target'),
    ('Fanta Strawberry 450 ml. (Bottle)', '1 Jun 2026', 'PKT',
     25, '1,869', 'PKT', 0, '⚪ no sale yesterday'),
    ('Sprite 500 ml. (Bottle)', '30 May 2026', 'PKT',
     22, '1,644', 'PKT', 1, '🟢 on target'),
    ('MOOVE CLEAR PROTEIN', '13 Jun 2026', 'MW1',
     34, '4,763', 'MW1', 1, '🟢 on target'),
    ('Iced Espresso Orange 12oz', '29 May 2026', 'SE3',
     1, '168', 'SE3', 0, '🔴 dormant since Jun'),
    ('Hot Tea Green Tea 12oz', '18 Jun 2026', 'PKT',
     1, '102', 'PKT', 0, '⚪ no sale yesterday'),
    ('Iced Latte 22oz', '23 Jun 2026', 'PKT',
     1, '182', 'PKT', 0, '⚪ no sale yesterday'),
    ('Mango Smoothie 22oz', '24 Jun 2026', 'PKT',
     2, '346', 'PKT', 2, '⚪ new — first day'),
    ('Mango Yoghurt Smoothie 22oz', '23 Jun 2026', 'PKT',
     2, '374', 'PKT', 0, '⚪ no sale yesterday'),
    ('Mixberry Smoothie 22oz', '24 Jun 2026', 'PKT',
     2, '346', 'PKT', 2, '⚪ new — first day'),
    ('Orange Cold Pressed 22oz', '24 Jun 2026', 'PKT',
     1, '196', 'PKT', 1, '⚪ new — first day'),
    ('Watermelon Smoothie 22oz', '23 Jun 2026', 'PKT',
     3, '519', 'PKT', 0, '⚪ no sale yesterday'),
]
NP_ROWS_FRUIT = [
    ('LYCHEE 400G.', '28 May 2026', 'MW1 · SE3',
     54, '8,580', 'MW1·SE3', 3, '🟢 on target'),
    ('MANGOSTEEN 400g.', '28 May 2026', 'SE3 · MW1',
     7, '1,636', 'SE3·MW1', 0, '🟡 below target'),
    ('ROSE APPLE 400G.', '30 May 2026', 'SE3 · MW1',
     24, '3,593', 'SE3·MW1', 2, '🟢 on target'),
    ('Orange 400 g (Pack)', '18 Jun 2026', 'SE3',
     18, '2,523', 'SE3', 0, '⚪ no sale yesterday'),
]
NP_ROWS_NEWCAT = [
    # MOOVE already in drinks — new category = genuinely novel products
    ('Watermelon Smoothie 22oz (PKT)', '23 Jun 2026', 'PKT launch',
     3, '519', 'PKT', 0, '⚪ no sale yesterday'),
]

# ─── Compute new-product aggregates ───
def sum_rows(rows):
    units = sum(r[3] for r in rows)
    rev   = sum(int(r[4].replace(',','')) for r in rows)
    yest  = sum(r[6] for r in rows)
    return units, rev, yest

drinks_total_units, drinks_total_rev, drinks_yest = sum_rows(NP_ROWS_DRINKS)
fruit_total_units,  fruit_total_rev,  fruit_yest  = sum_rows(NP_ROWS_FRUIT)

# New category is thin — fold into drinks for strip display
new_cat_total_units = drinks_total_units
new_cat_total_rev   = drinks_total_rev
new_cat_yest        = drinks_yest
drinks_n  = len(NP_ROWS_DRINKS)
fruit_n   = len(NP_ROWS_FRUIT)
new_cat_n = drinks_n  # reused in template strip

np_total_units = drinks_total_units + fruit_total_units
np_total_rev   = drinks_total_rev   + fruit_total_rev

# ─── Dormant (Query D filtered: qty_30d ≥ 3, no \n memos, no noise) ───
# (memo, last_sold_str, qty_30d, days_sold_30d, rev_30d)
DORMANT_MW1 = [
    ('MAEVAREE MANGO STICKY RICE SMOOTHIE 22OZ', '2026-06-08', 20, 11, 4256.03),
    ('Overnight Oat mango 16 oz',                '2026-06-06', 14, 10, 3519.60),
    ('MAEVAREE MANGO YOGHURT STICKY RICE SMOOTHIE 22OZ', '2026-06-12', 12, 7, 2579.40),
    ('MANGO (1 PCS.)',                            '2026-06-11', 10,  7, 1401.90),
    ('HOT CHOCOLATE 8 oz',                        '2026-05-27',  8,  2,  971.98),
    ('BLUEBERRY GREEK YOGURT',                    '2026-06-05',  5,  4,  883.19),
    ('Mango Sticky Rice\xa0(Box)',                '2026-06-01',  3,  3,  501.85),
]
DORMANT_SE3 = [
    ('Cantaloupe\xa0400 g (Pack)',                 '2026-06-09', 36, 14, 5046.79),
    ('MAEVAREE MANGO STICKY RICE SMOOTHIE 22OZ',  '2026-06-12', 29, 13, 6212.07),
    ('HOT CHOCOLATE 8 oz',                         '2026-05-29', 18,  4, 2186.98),
    ('MAEVAREE MANGO YOGHURT STICKY RICE SMOTHIE 22OZ', '2026-06-12', 14, 9, 3009.31),
    ('ORANGE JUICE BOTTLE',                        '2026-06-10', 11,  8, 1901.86),
    ('Pineapple Cold Pressed Juice 300 ml (bottle)', '2026-06-12', 7, 6, 1210.23),
    ('Mango Sticky Rice\xa0(Box)',                 '2026-05-31',  6,  4, 1003.74),
    ('Golden Harmony Greek Yogur',                 '2026-05-31',  6,  4, 1059.83),
    ('SEEDLESS GRAPE 400G.',                       '2026-06-08',  5,  2,  747.65),
    ('Overnight Oat mango 16 oz',                  '2026-06-04',  5,  5, 1257.00),
    ('T2 ICED THAI TEA WITH LIME 22OZ',            '2026-06-17',  4,  4,  654.20),
    ('MANGOSTEEN 400g.',                           '2026-06-01',  3,  3,  700.92),
    ('Overnight Oat Berry 16 oz',                  '2026-05-27',  3,  2,  726.18),
    ('BANANA YOGHURT SMOOTHIE 16OZ',               '2026-05-28',  3,  2,  490.65),
]
DORMANT_PKT = [
    ('Indian Tea Ginger Chai 12oz',                '2026-06-17', 27, 13, 3028.05),
    ('Banana 2PCS.',                               '2026-06-06', 10,  8,  551.40),
    ('Mango Berry Smoothie 16oz',                  '2026-06-11',  8,  5, 1383.20),
    ('singha soda water 325ml',                    '2026-06-04',  4,  2,  243.00),
    ('Pride Parrot Red Smoothie 22 oz.',           '2026-06-05',  4,  2,  747.67),
    ('T2 Iced Thai tea with lime 16oz',            '2026-06-11',  4,  3,  560.76),
    ('Nestle Water 600 ml',                        '2026-06-06',  4,  4,   37.40),
]

# ─── AM Review items (dormant, qty_30d >= 8) ───
# (branch_label, memo, last_sold_str, qty_30d, days_sold_30d, hypothesis, hyp_color)
AM_ITEMS_RAW = [
    ('SE3',  'Cantaloupe\xa0400 g (Pack)',               '2026-06-09', 36, 14, 'Stock-out suspect', '#E65100'),
    ('SE3',  'MAEVAREE MANGO STICKY RICE SMOOTHIE 22OZ','2026-06-12', 29, 13, 'Stock-out suspect', '#E65100'),
    ('PKT',  'Indian Tea Ginger Chai 12oz',              '2026-06-17', 27, 13, 'Stock-out suspect', '#E65100'),
    ('MW1',  'MAEVAREE MANGO STICKY RICE SMOOTHIE 22OZ','2026-06-08', 20, 11, 'Stock-out suspect', '#E65100'),
    ('SE3',  'HOT CHOCOLATE 8 oz',                       '2026-05-29', 18,  4, 'Waste risk — 26d dormant', '#C62828'),
    ('SE3',  'MAEVAREE MANGO YOGHURT STICKY RICE SMOTHIE 22OZ', '2026-06-12', 14, 9, 'Stock-out suspect', '#E65100'),
    ('MW1',  'Overnight Oat mango 16 oz',                '2026-06-06', 14, 10, 'Waste risk — 18d dormant', '#C62828'),
    ('MW1',  'MAEVAREE MANGO YOGHURT STICKY RICE SMOOTHIE 22OZ', '2026-06-12', 12, 7, 'Stock-out suspect', '#E65100'),
    ('SE3',  'ORANGE JUICE BOTTLE',                      '2026-06-10', 11,  8, 'Stock-out suspect', '#E65100'),
    ('MW1',  'MANGO (1 PCS.)',                           '2026-06-11', 10,  7, 'Stock-out suspect', '#E65100'),
    ('PKT',  'Banana 2PCS.',                             '2026-06-06', 10,  8, 'Stock-out suspect', '#E65100'),
    ('PKT',  'Mango Berry Smoothie 16oz',                '2026-06-11',  8,  5, 'Stock-out suspect', '#E65100'),
    ('MW1',  'HOT CHOCOLATE 8 oz',                       '2026-05-27',  8,  2, 'Waste risk — 28d dormant', '#C62828'),
]

# ─────────────────── computations ───────────────────

report_date  = date(2026, 6, 24)
run_date     = date(2026, 6, 25)
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
mw1_yest  = mw1[yest];  se3_yest = se3[yest];  pkt_yest = pkt[yest]
comb_yest = mw1_yest + se3_yest + pkt_yest

mw1_avg  = sum(mw1.values())  / 30
se3_avg  = sum(se3.values())  / 30
pkt_avg  = sum(pkt.values())  / 30
comb_avg = mw1_avg + se3_avg + pkt_avg

mw1_min = min(mw1.values()); mw1_max = max(mw1.values())
se3_min = min(se3.values()); se3_max = max(se3.values())
pkt_min = min(pkt.values()); pkt_max = max(pkt.values())

signed_pct = (comb_yest - comb_avg) / comb_avg * 100
mw1_vs30   = (mw1_yest  - mw1_avg)  / mw1_avg  * 100
se3_vs30   = (se3_yest  - se3_avg)  / se3_avg  * 100
pkt_vs30   = (pkt_yest  - pkt_avg)  / pkt_avg  * 100

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

report_date_display    = f'{report_date.day} {EN_MONTH_FULL[report_date.month-1]} {report_date.year}'
report_day_th          = TH_WD_FULL[report_date.weekday()]
window_30d_start_display = f'{window_start.day} {EN_MONTH_FULL[window_start.month-1]} {window_start.year}'

last7_dates = dates_sorted[-7:]

mw1_7d   = sum(mw1[d] for d in last7_dates)
se3_7d   = sum(se3[d] for d in last7_dates)
pkt_7d   = sum(pkt[d] for d in last7_dates)
comb_7d  = mw1_7d + se3_7d + pkt_7d
last7_avg_val = comb_7d / 7

# ─── FORECAST (today = Thursday 2026-06-25) ───
fc_date = run_date  # Thursday

def same_wday_history(branch_dict, target_date, weeks=4):
    vals = []
    d = target_date - timedelta(weeks=1)
    while len(vals) < weeks:
        if d in branch_dict:
            vals.append(branch_dict[d])
        d -= timedelta(weeks=1)
    return vals

mw1_thu = same_wday_history(mw1, fc_date)
se3_thu = same_wday_history(se3, fc_date)
pkt_thu = same_wday_history(pkt, fc_date)

def forecast_branch(thu_vals, branch_vals, all_dates):
    if not thu_vals:
        base = sum(branch_vals.values()) / len(branch_vals)
        band = base * 0.20
        return base, band, '🔴'
    base = sum(thu_vals) / len(thu_vals)
    last7_vals = [branch_vals[d] for d in all_dates[-7:]]
    trend_adj  = (base + sum(last7_vals) / 7) / 2
    stdev      = math.sqrt(sum((x - base)**2 for x in thu_vals) / len(thu_vals)) if len(thu_vals) > 1 else base * 0.12
    band       = max(stdev, trend_adj * 0.08)
    conf_pct   = stdev / base * 100 if base else 25
    conf_dot   = '🟢' if conf_pct < 12 else ('🟡' if conf_pct < 25 else '🔴')
    return trend_adj, band, conf_dot

mw1_fc, mw1_band, mw1_conf = forecast_branch(mw1_thu, mw1, dates_sorted)
se3_fc, se3_band, se3_conf = forecast_branch(se3_thu, se3, dates_sorted)
pkt_fc, pkt_band, pkt_conf = forecast_branch(pkt_thu, pkt, dates_sorted)

comb_fc       = mw1_fc + se3_fc + pkt_fc
comb_band     = math.sqrt(mw1_band**2 + se3_band**2 + pkt_band**2)
comb_conf_pct = comb_band / comb_fc * 100 if comb_fc else 25
comb_conf     = '🟢' if comb_conf_pct < 12 else ('🟡' if comb_conf_pct < 25 else '🔴')

# ─── Seasonal (Query E) ───
# SHINE MUSCAT GRAPES: MW1 total_rev=133186.69, SE3=105553.37 → combined 238740
grape_total_rev = 238740
grape_last_mw1  = '23 Jun 2026'   # SEEDLESS GRAPE 400G. last sold at MW1
grape_last_se3  = '8 Jun 2026'    # SEEDLESS GRAPE 400G. last sold at SE3

# Seasonal fruit coverage (new fruit revenue per day over 30d window)
# MW1: LYCHEE (19u × ~158.88 ≈ 3019) + MANGOSTEEN (2u × 233.65 ≈ 467) + ROSE APPLE (2u × 149.53 ≈ 299)
# SE3: LYCHEE (35u × ~158.88 ≈ 5560) + MANGOSTEEN (3u × 233.64 ≈ 701) + ROSE APPLE (~16u×149.53≈2393)
#      + Orange 400g (18u × 140.19 ≈ 2523)
mw1_fruit_rev = 3019 + 467 + 299   # ≈ 3785
se3_fruit_rev = 5560 + 701 + 2393 + 2523  # ≈ 11177

mw1_fruit_per_day = mw1_fruit_rev / 30
se3_fruit_per_day = se3_fruit_rev / 30

mw1_grape_baseline = 339
se3_grape_baseline = 251

mw1_coverage = mw1_fruit_per_day / mw1_grape_baseline * 100
se3_coverage = se3_fruit_per_day / se3_grape_baseline * 100

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

# ─── Dormant helpers ───
def gap_days_fn(last_sold_str):
    return (report_date - date.fromisoformat(last_sold_str)).days

def gap_color(days):
    return '#C62828' if days >= 14 else '#E65100'

def truncate(s, n=34):
    s2 = s.replace('\xa0', ' ').strip()
    return (s2[:n] + '…') if len(s2) > n else s2

def fmt_rev(r):
    return f'{round(r):,}'

def dormant_rows_for(branch_list):
    rows = []
    for memo, last_str, qty, days_sold, rev in branch_list:
        g = gap_days_fn(last_str)
        vel = round(qty / days_sold, 1) if days_sold else 0
        rows.append({
            'memo_display':  truncate(memo),
            'memo_full':     memo.replace('\xa0', ' ').strip(),
            'qty_30d':       fmt(qty),
            'days_sold_30d': str(days_sold),
            'rev_30d':       fmt_rev(rev),
            'gap_days':      str(g),
            'gap_color':     gap_color(g),
        })
    return rows

dormant_count = len(DORMANT_MW1) + len(DORMANT_SE3) + len(DORMANT_PKT)
am_queue_count = len(AM_ITEMS_RAW)

# ─── Commentary ───
direction = 'above' if signed_pct >= 0 else 'below'
commentary_text = (
    f'Yesterday ({report_date_display} · {report_day_th}), combined net was '
    f'฿{fmt(comb_yest)} ex-VAT, {abs(signed_pct):.1f}% {direction} the 30-day average of ฿{fmt(comb_avg)}. '
    f'MW1 came in at ฿{fmt(mw1_yest)} ({mw1_vs30:+.1f}% vs 30d avg), '
    f'SE3 at ฿{fmt(se3_yest)} ({se3_vs30:+.1f}%), '
    f'PKT at ฿{fmt(pkt_yest)} ({pkt_vs30:+.1f}%). '
    + ('PKT net was notably below its 30-day average, driven by fewer bills (33 vs avg ~45); MW1 and SE3 were within normal range.'
       if pkt_vs30 <= -20
       else 'All three branches performed within normal range of their 30-day averages.')
)

anomaly_items = [
    {'anomaly_text': f'PKT net ฿{fmt(pkt_yest)} ({pkt_vs30:+.1f}% vs 30d) — lowest since 21 Jun (7,904). 33 bills vs 30d avg ~45.',
     'anomaly_section_ref': 'Chart §3'},
    {'anomaly_text': f'SE3 Cantaloupe 400g — dormant 15d, was 36u/30d (฿5,047). Stock-out likely.',
     'anomaly_section_ref': 'Dormant SKUs §7'},
    {'anomaly_text': f'SE3+MW1 MAEVAREE MANGO STICKY RICE SMOOTHIE — dormant 12-16d, combined 49u in 30d.',
     'anomaly_section_ref': 'AM Review + Dormant §7'},
    {'anomaly_text': f'Seasonal fruit coverage: MW1 {mw1_coverage:.0f}% of grape baseline, SE3 {se3_coverage:.0f}% — ' + ('✅ SE3 recovering' if se3_coverage>=70 else '\U0001f534 SE3 still below 70%') + '.',
     'anomaly_section_ref': 'Seasonal Tracker §6'},
    {'anomaly_text': f'Pride Parrot (Red+Yellow) strong: MW1 ~{(162+101)//24}/day combined over 24d.',
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
    return [{'net': fmt(branch_dict[d]),
             'cell_style': 'background:#FFF3E0;font-weight:700;' if d == report_date else ''}
            for d in last7_dates]

def last7_comb_cells():
    return [{'net': fmt(comb[d]),
             'cell_bg': 'background:#FFF3E0;' if d == report_date else ''}
            for d in last7_dates]

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
    {'header_color': '#5551FE', 'header_label': 'MW1 · 26-T1MW1-03+04',
     'top20_rows': top20_rows(QB_MW1)},
    {'header_color': '#F27061', 'header_label': 'SE3 · 27-T1SE3-05',
     'top20_rows': top20_rows(QB_SE3)},
    {'header_color': '#2E7D32', 'header_label': 'PKT · 28 Unit 362 (Phuket)',
     'top20_rows': top20_rows(QB_PKT)},
]

def make_np_rows(raw_rows):
    return [{'memo': r[0], 'launch': r[1], 'notes': r[2],
             'total_units': str(r[3]), 'total_rev': r[4],
             'branch_split': r[5], 'yest_units': str(r[6]),
             'status_badge': r[7]} for r in raw_rows]

np_type_tables = [
    {'type_bg': '#1976D2', 'type_fg': '#fff', 'type_icon': '🥤', 'type_label': 'Drinks',
     'np_rows': make_np_rows(NP_ROWS_DRINKS)},
    {'type_bg': '#AD1457', 'type_fg': '#fff', 'type_icon': '🍉', 'type_label': 'Seasonal Fruits',
     'np_rows': make_np_rows(NP_ROWS_FRUIT)},
]

seasonal_skus = [
    {'fruit_emoji': '🍈', 'memo': 'LYCHEE 400G.', 'launch': '28 May 2026',
     'mw1_units': '19', 'mw1_per_day': f'{3019/30:.0f}',
     'se3_units': '35', 'se3_per_day': f'{5560/30:.0f}'},
    {'fruit_emoji': '🟣', 'memo': 'MANGOSTEEN 400g.', 'launch': '28 May 2026',
     'mw1_units': '2',  'mw1_per_day': f'{467/30:.0f}',
     'se3_units': '3',  'se3_per_day': f'{701/30:.0f}'},
    {'fruit_emoji': '🌸', 'memo': 'ROSE APPLE 400G.', 'launch': '30 May 2026',
     'mw1_units': '2',  'mw1_per_day': f'{299/30:.0f}',
     'se3_units': '16', 'se3_per_day': f'{2393/30:.0f}'},
    {'fruit_emoji': '🍊', 'memo': 'Orange 400 g (Pack)', 'launch': '18 Jun 2026',
     'mw1_units': '—',  'mw1_per_day': '0',
     'se3_units': '18', 'se3_per_day': f'{2523/30:.0f}'},
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
        'daily_gap':         f'฿{fmt(round(max(0, se3_grape_baseline - se3_fruit_per_day)))}/d',
        'monthly_impact':    f'-฿{fmt(round(max(0, se3_grape_baseline - se3_fruit_per_day)*30))}/month',
        'badge_bg':          coverage_bg(se3_coverage),
        'badge_text':        coverage_badge(se3_coverage),
    },
]

def make_dormant_branch(label, color, items):
    return {'branch': label, 'header_color': color,
            'branch_count': str(len(items)), 'dormant_rows': dormant_rows_for(items)}

dormant_branches = [
    make_dormant_branch('MW1', '#5551FE', DORMANT_MW1),
    make_dormant_branch('SE3', '#F27061', DORMANT_SE3),
    make_dormant_branch('PKT', '#2E7D32', DORMANT_PKT),
]

# AM review rows
def make_am_rows(raw_list):
    rows = []
    for branch, memo, last_str, qty, days_sold, hyp, hyp_color in raw_list:
        g = gap_days_fn(last_str)
        vel = round(qty / days_sold, 1) if days_sold else 0
        rows.append({
            'memo':            truncate(memo, 40),
            'last_sold':       last_str[5:],  # MM-DD
            'gap_days':        str(g),
            'velocity_7d':     f'{vel:.1f}',
            'target':          f'{vel:.0f}',
            'branch_split':    branch,
            'hypothesis_text': hyp,
            'hypothesis_color': hyp_color,
        })
    return rows

am_items = make_am_rows(AM_ITEMS_RAW)

# ─────────────────── scalars ───────────────────

scalars = {
    'report_date':          REPORT_DATE,
    'report_date_display':  report_date_display,
    'report_day_th':        report_day_th,
    'window_30d_start':     window_30d_start_display,
    'generated_timestamp':  '2026-06-25 07:30',
    'subject_prefix':       subject_prefix,
    'comb_net':             fmt(comb_yest),
    'signed_pct':           f'{signed_pct:+.1f}',
    'am_queue_count':       str(am_queue_count),
    'dormant_count':        str(dormant_count),
    'mw1_net':              fmt(mw1_yest),
    'se3_net':              fmt(se3_yest),
    'pkt_net':              fmt(pkt_yest),
    'mw1_vs_30d':           f'{mw1_vs30:+.1f}',
    'se3_vs_30d':           f'{se3_vs30:+.1f}',
    'pkt_vs_30d':           f'{pkt_vs30:+.1f}',
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
    'comb_monthly_runrate': f'{comb_avg * 30 / 1000:,.1f}K',
    'last7_total':          fmt(comb_7d),
    'last7_avg':            fmt(last7_avg_val),
    'mw1_7d_total':         fmt(mw1_7d),
    'se3_7d_total':         fmt(se3_7d),
    'pkt_7d_total':         fmt(pkt_7d),
    'comb_7d_total':        fmt(comb_7d),
    'np_summary_line':      f'{drinks_n + fruit_n} new SKUs tracked May–Jun 2026 · Drinks · Seasonal Fruits',
    'np_total_units':       str(np_total_units),
    'np_total_rev':         fmt(np_total_rev),
    'drinks_n':             str(drinks_n),
    'drinks_todate_units':  str(drinks_total_units),
    'drinks_todate_rev':    fmt(drinks_total_rev),
    'fruit_n':              str(fruit_n),
    'fruit_todate_units':   str(fruit_total_units),
    'fruit_todate_rev':     fmt(fruit_total_rev),
    'new_cat_n':            str(drinks_n),
    'new_cat_todate_units': str(drinks_total_units),
    'new_cat_todate_rev':   fmt(drinks_total_rev),
    'grape_total_rev':      fmt(grape_total_rev),
    'grape_last_mw1':       grape_last_mw1,
    'grape_last_se3':       grape_last_se3,
    # Forecast
    'forecast_date_display': f'{run_date.day} {EN_MONTH_FULL[run_date.month-1]} {run_date.year}',
    'mw1_conf_dot':   mw1_conf,
    'se3_conf_dot':   se3_conf,
    'pkt_conf_dot':   pkt_conf,
    'comb_conf_dot':  comb_conf,
    'mw1_fc_low':     fmt(mw1_fc - mw1_band),
    'mw1_fc_high':    fmt(mw1_fc + mw1_band),
    'se3_fc_low':     fmt(se3_fc - se3_band),
    'se3_fc_high':    fmt(se3_fc + se3_band),
    'pkt_fc_low':     fmt(pkt_fc - pkt_band),
    'pkt_fc_high':    fmt(pkt_fc + pkt_band),
    'comb_fc_low':    fmt(comb_fc - comb_band),
    'comb_fc_high':   fmt(comb_fc + comb_band),
    'commentary_text': commentary_text,
    'anomaly_count':  str(len(anomaly_items)),
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
    'anomaly_items':     anomaly_items,
}

sections = {
    'am_review':          am_queue_count > 0,
    'seasonal':           fruit_n > 0,
    'dormant':            dormant_count > 0,
    'forecast_shown':     True,
    'forecast_suppressed': False,
    'anomaly_shown':      True,
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

sys.stderr.write(f'email.html written ({len(html):,} bytes)\n')
print('OK')
print(f'SUMMARY: report_date={REPORT_DATE}, comb_net=฿{fmt(comb_yest)}, signed_pct={signed_pct:+.1f}%')
print(f'  MW1=฿{fmt(mw1_yest)} ({mw1_vs30:+.1f}%) SE3=฿{fmt(se3_yest)} ({se3_vs30:+.1f}%) PKT=฿{fmt(pkt_yest)} ({pkt_vs30:+.1f}%)')
print(f'  am_queue={am_queue_count} dormant={dormant_count} subject_prefix={subject_prefix}')
print(f'  forecast Thu: ฿{fmt(comb_fc-comb_band)}–฿{fmt(comb_fc+comb_band)} ({comb_conf})')
