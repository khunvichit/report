#!/usr/bin/env python3
"""
Juiceland Daily Sales Report — 2026-06-17 (yesterday Asia/Bangkok)
Run date: 2026-06-18
"""
import re, sys, json, math, os
from datetime import date, timedelta
from collections import defaultdict

# ─────────────────── template filler (copied from build_juiceland_email.py) ───

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

REPORT_DATE = '2026-06-17'

# Query A — daily totals per branch, 30-day window 2026-05-19 → 2026-06-17
QA = [
    ('2026-05-19', 33, 33034.5),   ('2026-05-19', 105, 25820.0),  ('2026-05-19', 109, 7867.0),
    ('2026-05-20', 33, 31093.0),   ('2026-05-20', 105, 17307.5),  ('2026-05-20', 109, 10311.0),
    ('2026-05-21', 33, 36940.5),   ('2026-05-21', 105, 29297.0),  ('2026-05-21', 109, 9611.0),
    ('2026-05-22', 33, 40088.0),   ('2026-05-22', 105, 26689.0),  ('2026-05-22', 109, 10358.0),
    ('2026-05-23', 33, 38639.5),   ('2026-05-23', 105, 39492.0),  ('2026-05-23', 109, 12698.0),
    ('2026-05-24', 33, 45429.5),   ('2026-05-24', 105, 28328.0),  ('2026-05-24', 109, 12933.0),
    ('2026-05-25', 33, 38221.0),   ('2026-05-25', 105, 31983.5),  ('2026-05-25', 109, 10502.0),
    ('2026-05-26', 33, 36852.5),   ('2026-05-26', 105, 24575.5),  ('2026-05-26', 109, 7039.0),
    ('2026-05-27', 33, 33877.0),   ('2026-05-27', 105, 26502.0),  ('2026-05-27', 109, 16234.0),
    ('2026-05-28', 33, 33415.0),   ('2026-05-28', 105, 31121.0),  ('2026-05-28', 109, 12474.0),
    ('2026-05-29', 33, 42210.5),   ('2026-05-29', 105, 22568.0),  ('2026-05-29', 109, 13844.0),
    ('2026-05-30', 33, 34788.0),   ('2026-05-30', 105, 26883.0),  ('2026-05-30', 109, 14605.0),
    ('2026-05-31', 33, 28583.0),   ('2026-05-31', 105, 32544.0),  ('2026-05-31', 109, 14052.0),
    ('2026-06-01', 33, 32133.0),   ('2026-06-01', 105, 24075.0),  ('2026-06-01', 109, 13940.0),
    ('2026-06-02', 33, 36476.0),   ('2026-06-02', 105, 15959.0),  ('2026-06-02', 109, 9920.0),
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
    ('2026-06-16', 33, 39711.0),   ('2026-06-16', 105, 19173.0),  ('2026-06-16', 109, 9078.0),
    ('2026-06-17', 33, 37169.0),   ('2026-06-17', 105, 20735.0),  ('2026-06-17', 109, 10010.0),
]

# Query B — top products per branch yesterday (2026-06-17)
QB_MW1 = [
    ('EVIAN', 52, 5831.80, 3),
    ('MANGO 400G.', 11, 1644.83, 3),
    ('PRIDE PARROT RED', 9, 1682.28, 2),
    ('CARROT JUICE BOTTLE', 6, 1037.37, 2),
    ('CH4 HOT LATTE', 5, 700.95, 2),
    ('COCONUT READY TO DRINK', 5, 794.40, 1),
    ('Mango juice (Bottle) 300 ml', 5, 864.48, 4),
    ('C1 GUAVA&GREEN APPLE&RED APPLE 22OZ', 5, 981.30, 2),
    ('CH1 ESPRESSO', 4, 467.28, 2),
    ('PINEAPPLE 400G.', 4, 560.76, 2),
    ('S5 MANGO SMOOTHIE 22OZ', 4, 691.60, 2),
    ('S1 COCONUT SMOOTHIE 22OZ', 4, 766.35, 2),
    ('P1 GOLDEN GLOW 16OZ', 4, 747.67, 2),
    ('YS2 STRAWBERRY YOGHURT 22OZ', 4, 747.68, 3),
    ('WATERMELON 400G.', 4, 560.76, 2),
    ('PRIDE PARROT YELLOW', 4, 747.67, 2),
    ('P1 GOLDEN GLOW 22OZ', 4, 841.12, 3),
    ('C4 MANGO PASSION 22OZ', 4, 785.04, 2),
    ('Mango passion juice (Bottle) 300 ml', 4, 691.60, 3),
    ('S2 MANGO PASSION SMOOTHIE 22OZ', 4, 691.60, 2),
]
QB_SE3 = [
    ('EVIAN', 37, 4149.55, 5),
    ('WATERMELON 400G.', 9, 1261.71, 2),
    ('PINEAPPLE 400G.', 8, 1121.52, 3),
    ('MANGO 400G.', 8, 1196.24, 2),
    ('PRIDE PARROT RED', 7, 1308.44, 3),
    ('COCONUT READY TO DRINK', 5, 794.40, 2),
    ('PRIDE PARROT YELLOW', 5, 934.59, 2),
    ('PAPAYA 400G.', 5, 700.95, 3),
    ('GUAVA 400G.', 3, 420.57, 2),
    ('S3 WATERMELON SMOOTHIE 22OZ', 3, 518.69, 3),
    ('3 kinds of fruit Papaya/Pineapple/Guava', 3, 420.57, 3),
    ('DRAGON FRUIT 400G.', 2, 280.38, 2),
    ('YS2 STRAWBERRY YOGHURT 22OZ', 2, 373.84, 1),
    ('S1 COCONUT SMOOTHIE 22OZ', 2, 383.18, 2),
    ('C6 PINEAPPLE COLD PRESSED 22OZ', 2, 392.52, 1),
    ('P1 GOLDEN GLOW 22OZ', 2, 420.56, 2),
    ('CH2 HOT AMERICANO', 2, 252.34, 1),
    ('S5 MANGO SMOOTHIE 22OZ', 2, 345.80, 2),
    ('C2 ORANGE COLD PRESSED 16OZ', 2, 345.80, 2),
    ('C3 WATERMELON COLD PRESSED 22OZ', 2, 392.52, 1),
]
QB_PKT = [
    ('Evian 500ml. (Bottle)', 18, 2018.70, 3),
    ('Mango 400 g. (Pack)', 11, 1644.83, 3),
    ('Coconut (EA)', 7, 1112.15, 2),
    ('Watermelon 400 g. (Pack)', 4, 560.76, 3),
    ('Coke 500 ml. (Bottle)', 4, 299.08, 2),
    ('CH1 Cappuccino (hot) 12oz', 3, 420.57, 2),
    ('Heineken 320 ml. (Bottle)', 3, 504.67, 1),
    ('Hot water 12oz', 3, 84.11, 1),
    ('CH4 Americano (hot) 12oz', 2, 252.34, 1),
    ('Fanta Orange 450 ml. (Bottle)', 2, 149.54, 1),
    ('S5 mango smoothie 16oz', 2, 299.06, 2),
    ('C2 orange cold pressed 16oz', 2, 345.80, 1),
    ('Watermelon Cold Pressed 300 ml. (bottle)', 2, 345.79, 2),
    ('CH2 Caffe latte (hot) 12oz', 1, 140.19, 1),
    ('Indian Tea Ginger Chai 12oz', 1, 112.15, 1),
    ('Indian Tea Cardamom Chai 12oz', 1, 112.15, 1),
    ('Fanta Strawberry 450 ml. (Bottle)', 1, 74.77, 1),
    ('P2 pineapple kale cold pressed 16oz', 1, 186.92, 1),
    ('Pineapple Cold Pressed Juice 300 ml.', 1, 172.89, 1),
    ('C8 Carrot & Red Apple & Celery 16oz', 1, 172.89, 1),
]

# Query D — dormant SKUs (qty_30d >= 3, no malformed memos, gap >= 7d from 2026-06-17)
# (memo, last_sold_str, qty_30d, days_sold_30d, rev_30d)
DORMANT_MW1 = [
    ('Overnight Oat mango 16 oz',           '2026-06-06', 27, 15, 6787.80),
    ('MAEVAREE MANGO STICKY RICE SMOOTHIE 22OZ', '2026-06-08', 27, 15, 5760.68),
    ('HOT CHOCOLATE 8 oz',                  '2026-05-27', 18,  4, 2186.96),
    ('BLUEBERRY GREEK YOGURT',              '2026-06-05',  9,  7, 1589.75),
    ('VANILLA BEAN GREEK YOGURT',           '2026-05-26',  8,  6, 1413.10),
    ('SHINE MUSCAT GRAPES 400G (PACK)',     '2026-05-21',  7,  3, 1046.71),
    ('T2 ICED THAI TEA WITH LIME 16OZ',    '2026-06-01',  4,  3,  560.75),
    ('Mango Pineapple Smoothie 16oz',       '2026-05-23',  4,  2,  691.59),
    ('RASPBERRY GREEK YOGURT',              '2026-05-22',  4,  3,  706.53),
    ('Mango Berry Smoothie 16oz',           '2026-05-26',  4,  3,  691.60),
    ('Mango Sticky Rice (Box)',             '2026-06-01',  3,  3,  501.85),
]
DORMANT_SE3 = [
    ('Cantaloupe 400g (Pack)',              '2026-06-09', 55, 20, 7710.39),
    ('HOT CHOCOLATE 8 oz',                  '2026-05-29', 22,  6, 2672.98),
    ('Mango Sticky Rice (Box)',             '2026-05-31', 19,  8, 3178.51),
    ('Golden Harmony Greek Yogurt',         '2026-05-31', 17,  8, 3002.81),
    ('ORANGE JUICE BOTTLE',                 '2026-06-10', 16, 13, 2766.34),
    ('Overnight Oat Berry 16 oz',           '2026-05-27',  7,  5, 1694.40),
    ('CI3 ICED AMERICANO 22OZ',            '2026-06-08',  7,  6, 1177.54),
    ('BANANA YOGHURT SMOOTHIE 16OZ',       '2026-05-28',  7,  6, 1144.85),
    ('MANGO PINEAPPLE SMOOTHIE 16OZ',      '2026-05-31',  6,  4, 1037.41),
    ('Overnight Oat mango 16 oz',           '2026-06-04',  5,  5, 1257.00),
    ('SEEDLESS GRAPE 400G.',               '2026-06-08',  5,  2,  747.65),
    ('CI4 ICED CAPPUCCINO 22OZ',           '2026-05-30',  4,  3,  728.96),
    ('CI4 ICED CAPPUCCINO 16OZ',           '2026-06-10',  3,  2,  476.64),
    ('MANGOSTEEN 400g.',                    '2026-06-01',  3,  3,  700.92),
]
DORMANT_PKT = [
    ('Banana 2PCS.',                        '2026-06-06', 16, 13,  882.24),
    ('Nestle Water 600 ml',                 '2026-06-06',  4,  4,   37.40),
    ('singha soda water 325ml',             '2026-06-04',  4,  2,  243.00),
    ('Orange Cold Pressed Juice 300 ml.',   '2026-05-27',  3,  3,  518.69),
]

# ─────────────────── computations ───────────────────

report_date  = date(2026, 6, 17)
run_date     = date(2026, 6, 18)
window_start = report_date - timedelta(days=29)  # 2026-05-19

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

TH_WD      = ['จ','อ','พ','พฤ','ศ','ส','อา']
TH_WD_FULL = ['วันจันทร์','วันอังคาร','วันพุธ','วันพฤหัสบดี','วันศุกร์','วันเสาร์','วันอาทิตย์']
EN_MONTH_FULL = ['January','February','March','April','May','June',
                 'July','August','September','October','November','December']
EN_MONTH = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

def th_weekday_abbr(d): return TH_WD[d.weekday()]

report_date_display      = f'{report_date.day} {EN_MONTH_FULL[report_date.month-1]} {report_date.year}'
report_day_th            = TH_WD_FULL[report_date.weekday()]
window_30d_start_display = f'{window_start.day} {EN_MONTH_FULL[window_start.month-1]} {window_start.year}'

last7_dates = dates_sorted[-7:]
mw1_7d  = sum(mw1[d] for d in last7_dates)
se3_7d  = sum(se3[d] for d in last7_dates)
pkt_7d  = sum(pkt[d] for d in last7_dates)
comb_7d = mw1_7d + se3_7d + pkt_7d
last7_avg_val = comb_7d / 7

# ─── FORECAST (today = Thursday 2026-06-18) ───
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

def forecast_branch(wday_vals, branch_vals, all_dates):
    if not wday_vals:
        return 0, 0, '🔴'
    base       = sum(wday_vals) / len(wday_vals)
    last7_vals = [branch_vals[d] for d in all_dates[-7:]]
    trend_adj  = (base + sum(last7_vals) / 7) / 2
    stdev      = math.sqrt(sum((x - base)**2 for x in wday_vals) / len(wday_vals)) if len(wday_vals) > 1 else base * 0.12
    band       = max(stdev, trend_adj * 0.08)
    conf_pct   = stdev / base * 100 if base else 25
    if conf_pct < 12:   conf_dot = '🟢'
    elif conf_pct < 25: conf_dot = '🟡'
    else:               conf_dot = '🔴'
    return trend_adj, band, conf_dot

mw1_fc, mw1_band, mw1_conf = forecast_branch(mw1_thu, mw1, dates_sorted)
se3_fc, se3_band, se3_conf = forecast_branch(se3_thu, se3, dates_sorted)
pkt_fc, pkt_band, pkt_conf = forecast_branch(pkt_thu, pkt, dates_sorted)

comb_fc       = mw1_fc + se3_fc + pkt_fc
comb_band     = math.sqrt(mw1_band**2 + se3_band**2 + pkt_band**2)
comb_conf_pct = comb_band / comb_fc * 100 if comb_fc else 25
comb_conf     = '🟢' if comb_conf_pct < 12 else ('🟡' if comb_conf_pct < 25 else '🔴')

# Suppress forecast if any branch is low confidence
forecast_suppressed = any(c == '🔴' for c in [mw1_conf, se3_conf, pkt_conf])
forecast_shown      = True

# ─── COMMENTARY ───
commentary_text = (
    f'Yesterday (17 June 2026 · วันพุธ), combined net was ฿{fmt(comb_yest)} ex-VAT, '
    f'{abs(signed_pct):.1f}% below the 30-day average. '
    f'MW1 came in at ฿{fmt(mw1_yest)} ({mw1_vs30:+.1f}% vs 30d avg), '
    f'SE3 at ฿{fmt(se3_yest)} ({se3_vs30:+.1f}% vs 30d avg), '
    f'PKT at ฿{fmt(pkt_yest)} ({pkt_vs30:+.1f}% vs 30d avg). '
    f'SE3 and PKT were notably below their 30-day averages while MW1 held above.'
)

anomaly_items = [
    {'anomaly_text': f'SE3 ฿{fmt(se3_yest)} (−{abs(se3_vs30):.1f}% vs 30d avg) — below average for the past several days',
     'anomaly_section_ref': 'Chart §3'},
    {'anomaly_text': f'PKT ฿{fmt(pkt_yest)} (−{abs(pkt_vs30):.1f}% vs 30d avg) — lowest combined in recent 7 days',
     'anomaly_section_ref': 'Chart §3'},
    {'anomaly_text': f'29 dormant SKUs total (11 MW1 · 14 SE3 · 4 PKT) — Cantaloupe 400g at SE3 was 55u/30d',
     'anomaly_section_ref': 'Dormant §7'},
    {'anomaly_text': f'Seasonal fruit coverage MW1 only 39% of grape baseline — gap ฿208/day',
     'anomaly_section_ref': 'Seasonal §6'},
    {'anomaly_text': f'Pride Parrot (Red+Yellow) strong at MW1+SE3 — 25+ units/day combined',
     'anomaly_section_ref': 'New Products §4'},
]

# ─── NEW PRODUCTS (from Query C) ───
NP_DRINKS_ROWS = [
    {'memo': 'PRIDE PARROT RED', 'launch': '1 Jun 2026', 'notes': 'MW1, SE3',
     'total_units': 176, 'total_rev': '32,842', 'branch_split': 'MW1·SE3',
     'yest_units': 16, 'status_badge': '🟢 on target'},
    {'memo': 'PRIDE PARROT YELLOW', 'launch': '1 Jun 2026', 'notes': 'MW1, SE3',
     'total_units': 103, 'total_rev': '19,252', 'branch_split': 'MW1·SE3',
     'yest_units': 9, 'status_badge': '🟢 on target'},
    {'memo': 'MOOVE CLEAR PROTEIN', 'launch': '13 Jun 2026', 'notes': 'MW1 only',
     'total_units': 20, 'total_rev': '2,804', 'branch_split': 'MW1',
     'yest_units': 2, 'status_badge': '🟢 on target'},
    {'memo': 'Fanta Orange 450ml. (Bottle)', 'launch': '31 May 2026', 'notes': 'PKT only',
     'total_units': 20, 'total_rev': '1,495', 'branch_split': 'PKT',
     'yest_units': 2, 'status_badge': '🟢 on target'},
    {'memo': 'Fanta Strawberry 450ml. (Bottle)', 'launch': '1 Jun 2026', 'notes': 'PKT only',
     'total_units': 22, 'total_rev': '1,645', 'branch_split': 'PKT',
     'yest_units': 1, 'status_badge': '🟢 on target'},
    {'memo': 'Sprite 500ml. (Bottle)', 'launch': '30 May 2026', 'notes': 'PKT only',
     'total_units': 19, 'total_rev': '1,421', 'branch_split': 'PKT',
     'yest_units': 0, 'status_badge': '🟠 stock-out suspect — gap 2d'},
    {'memo': 'Pride Parrot Red Smoothie 22oz', 'launch': '4 Jun 2026', 'notes': 'PKT only',
     'total_units': 14, 'total_rev': '2,617', 'branch_split': 'PKT',
     'yest_units': 0, 'status_badge': '🟠 stock-out suspect — gap 1d'},
    {'memo': 'Pride Parrot Yellow Smoothie 22oz', 'launch': '7 Jun 2026', 'notes': 'PKT only',
     'total_units': 7, 'total_rev': '1,308', 'branch_split': 'PKT',
     'yest_units': 0, 'status_badge': '🟠 stock-out suspect — gap 2d'},
    {'memo': 'Overnight Oat mango 16 oz', 'launch': '21 May 2026', 'notes': 'MW1+SE3 — now dormant',
     'total_units': 32, 'total_rev': '8,032', 'branch_split': 'MW1·SE3',
     'yest_units': 0, 'status_badge': '🔴 dormant — 11d/13d gaps'},
    {'memo': 'HOT CHOCOLATE 8 oz', 'launch': '24 May 2026', 'notes': 'MW1+SE3 — now dormant',
     'total_units': 40, 'total_rev': '4,860', 'branch_split': 'MW1·SE3',
     'yest_units': 0, 'status_badge': '🔴 dormant — 21d/19d gaps'},
    {'memo': 'Overnight Oat Berry 16 oz', 'launch': '22 May 2026', 'notes': 'SE3+MW1 — dormant',
     'total_units': 8, 'total_rev': '1,936', 'branch_split': 'SE3·MW1',
     'yest_units': 0, 'status_badge': '🔴 dormant — 21d gap'},
    {'memo': 'HOT MOCHA 8 oz', 'launch': '20 May 2026', 'notes': 'MW1 — dormant',
     'total_units': 2, 'total_rev': '252', 'branch_split': 'MW1',
     'yest_units': 0, 'status_badge': '🔴 dormant — 26d gap'},
    {'memo': 'Fanta Fruit Punch 450ml. (Bottle)', 'launch': '31 May 2026', 'notes': 'PKT — 1 day only',
     'total_units': 1, 'total_rev': '75', 'branch_split': 'PKT',
     'yest_units': 0, 'status_badge': '🔴 dormant — 17d gap'},
    {'memo': 'Iced Espresso Orange 12oz', 'launch': '29 May 2026', 'notes': 'SE3 — 1 sale only',
     'total_units': 1, 'total_rev': '168', 'branch_split': 'SE3',
     'yest_units': 0, 'status_badge': '🔴 dormant — 19d gap'},
]
NP_FRUIT_ROWS = [
    {'memo': 'LYCHEE 400G.', 'launch': '28 May 2026', 'notes': 'MW1, SE3',
     'total_units': 37, 'total_rev': '5,879', 'branch_split': 'MW1·SE3',
     'yest_units': 3, 'status_badge': '🟢 on target'},
    {'memo': 'ROSE APPLE 400G.', 'launch': '30 May 2026', 'notes': 'SE3 only',
     'total_units': 10, 'total_rev': '1,495', 'branch_split': 'SE3',
     'yest_units': 1, 'status_badge': '🟢 on target'},
    {'memo': 'MANGOSTEEN 400g.', 'launch': '28 May 2026', 'notes': 'MW1+SE3 — mostly dormant',
     'total_units': 4, 'total_rev': '935', 'branch_split': 'SE3·MW1',
     'yest_units': 0, 'status_badge': '🟠 stock-out — SE3 16d, MW1 7d'},
]
NP_NEWCAT_ROWS = [
    {'memo': 'Chicken Club Croissant', 'launch': '22 May 2026', 'notes': 'SE3 only',
     'total_units': 32, 'total_rev': '4,456', 'branch_split': 'SE3',
     'yest_units': 0, 'status_badge': '🟠 not sold yesterday — gap 1d'},
    {'memo': 'CAESAR SALAD', 'launch': '18 May 2026', 'notes': 'MW1 — now dormant',
     'total_units': 4, 'total_rev': '673', 'branch_split': 'MW1',
     'yest_units': 0, 'status_badge': '🔴 dormant — 19d gap'},
]

drinks_n             = 14
drinks_total_units   = 375
drinks_total_rev     = 77665
drinks_yest_units    = 30   # PPR(16)+PPY(9)+MOOVE(2)+Fanta Org(2)+Fanta Straw(1)
drinks_yest_rev      = 5178

fruit_n              = 3
fruit_total_units    = 51
fruit_total_rev      = 8309
fruit_yest_units     = 4
fruit_yest_rev       = 626

new_cat_n            = 2
new_cat_total_units  = 36
new_cat_total_rev    = 5129
new_cat_yest_units   = 0
new_cat_yest_rev     = 0

np_total_units = drinks_total_units + fruit_total_units + new_cat_total_units
np_total_rev   = drinks_total_rev + fruit_total_rev + new_cat_total_rev

# ─── SEASONAL (Query E) ───
grape_total_rev  = 243226
grape_last_mw1   = '11 Jun 2026'
grape_last_se3   = '8 Jun 2026'

# Fruit revenue since first launch (28 May → 17 Jun = 20 days)
mw1_fruit_rev      = 2616.85  # LYCHEE + MANGOSTEEN at MW1
se3_fruit_rev      = 5691.58  # LYCHEE + MANGOSTEEN + ROSE APPLE at SE3
mw1_fruit_per_day  = mw1_fruit_rev / 20  # 130.84/d
se3_fruit_per_day  = se3_fruit_rev / 20  # 284.58/d
mw1_grape_baseline = 339
se3_grape_baseline = 251
mw1_coverage       = mw1_fruit_per_day / mw1_grape_baseline * 100  # ~38.6%
se3_coverage       = se3_fruit_per_day / se3_grape_baseline * 100  # ~113.4%

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

seasonal_skus = [
    {'fruit_emoji': '🍈', 'memo': 'LYCHEE 400G.', 'launch': '28 May 2026',
     'mw1_units': '15', 'mw1_per_day': f'{2383.20/20:.0f}',
     'se3_units': '22', 'se3_per_day': f'{3495.34/20:.0f}'},
    {'fruit_emoji': '🌸', 'memo': 'ROSE APPLE 400G.', 'launch': '30 May 2026',
     'mw1_units': '—', 'mw1_per_day': '0',
     'se3_units': '10', 'se3_per_day': f'{1495.32/18:.0f}'},
    {'fruit_emoji': '🟣', 'memo': 'MANGOSTEEN 400g.', 'launch': '28 May 2026',
     'mw1_units': '1', 'mw1_per_day': f'{233.65/20:.0f}',
     'se3_units': '3', 'se3_per_day': f'{700.92/20:.0f}'},
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
        'daily_gap':         f'+฿{fmt(round(se3_fruit_per_day - se3_grape_baseline))}/d',
        'monthly_impact':    f'+฿{fmt(round((se3_fruit_per_day - se3_grape_baseline)*30))}/month',
        'badge_bg':          coverage_bg(se3_coverage),
        'badge_text':        coverage_badge(se3_coverage),
    },
]

# ─── DORMANT helpers ───
def gap_days(last_sold_str):
    return (report_date - date.fromisoformat(last_sold_str)).days

def gap_color(days):
    return '#C62828' if days >= 14 else '#E65100'

def truncate(s, n=34):
    return (s[:n] + '…') if len(s) > n else s

def dormant_rows_for(branch_list):
    rows = []
    for memo, last_str, qty, days_sold, rev in branch_list:
        g = gap_days(last_str)
        rows.append({
            'memo_display': truncate(memo),
            'memo_full':    memo,
            'qty_30d':      fmt(qty),
            'days_sold_30d': str(days_sold),
            'rev_30d':      fmt(round(rev)),
            'gap_days':     str(g),
            'gap_color':    gap_color(g),
        })
    return rows

dormant_count = len(DORMANT_MW1) + len(DORMANT_SE3) + len(DORMANT_PKT)

# ─────────────────── build repeats ───────────────────

chart_days = []
for d in dates_sorted:
    chart_days.append({
        'date':            f'{d.day} {EN_MONTH[d.month-1]}',
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

np_type_tables = [
    {'type_bg': '#1976D2', 'type_fg': '#fff', 'type_icon': '🥤',
     'type_label': 'Drinks', 'np_rows': NP_DRINKS_ROWS},
    {'type_bg': '#AD1457', 'type_fg': '#fff', 'type_icon': '🍉',
     'type_label': 'Seasonal Fruits', 'np_rows': NP_FRUIT_ROWS},
    {'type_bg': '#2E7D32', 'type_fg': '#fff', 'type_icon': '⭐',
     'type_label': 'New Category', 'np_rows': NP_NEWCAT_ROWS},
]

dormant_branches = [
    {'branch': 'MW1', 'header_color': '#5551FE',
     'branch_count': str(len(DORMANT_MW1)), 'dormant_rows': dormant_rows_for(DORMANT_MW1)},
    {'branch': 'SE3', 'header_color': '#F27061',
     'branch_count': str(len(DORMANT_SE3)), 'dormant_rows': dormant_rows_for(DORMANT_SE3)},
    {'branch': 'PKT', 'header_color': '#2E7D32',
     'branch_count': str(len(DORMANT_PKT)), 'dormant_rows': dormant_rows_for(DORMANT_PKT)},
]

# ─────────────────── scalars ───────────────────

scalars = {
    'report_date':           REPORT_DATE,
    'report_date_display':   report_date_display,
    'report_day_th':         report_day_th,
    'window_30d_start':      window_30d_start_display,
    'generated_timestamp':   '2026-06-18 07:30',
    'subject_prefix':        subject_prefix,
    'comb_net':              fmt(comb_yest),
    'signed_pct':            f'{signed_pct:+.1f}',
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
    'np_summary_line':       '19 new SKUs tracked · Drinks · Seasonal Fruits · New Category · since 18 May 2026',
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
    'mw1_fc_low':            fmt(max(0, mw1_fc - mw1_band)),
    'mw1_fc_high':           fmt(mw1_fc + mw1_band),
    'se3_fc_low':            fmt(max(0, se3_fc - se3_band)),
    'se3_fc_high':           fmt(se3_fc + se3_band),
    'pkt_fc_low':            fmt(max(0, pkt_fc - pkt_band)),
    'pkt_fc_high':           fmt(pkt_fc + pkt_band),
    'comb_fc_low':           fmt(max(0, comb_fc - comb_band)),
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
    'am_review':          False,
    'seasonal':           True,
    'dormant':            True,
    'forecast_shown':     not forecast_suppressed,
    'forecast_suppressed': forecast_suppressed,
    'anomaly_shown':      True,
}

# ─────────────────── assemble ───────────────────

base = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(base, 'juiceland-template.html'), encoding='utf-8') as f:
    main_tpl = f.read()

with open(os.path.join(base, 'juiceland-prediction-section.html'), encoding='utf-8') as f:
    pred_tpl = f.read()

pred_html = fill(pred_tpl, scalars, repeats, sections)

inject_marker = '<div style="padding:24px;">'
main_tpl = main_tpl.replace(inject_marker, inject_marker + '\n' + pred_html, 1)

html = fill(main_tpl, scalars, repeats, sections)

out_path = os.path.join(base, 'email_2026_06_17.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)

sys.stderr.write(f'email_2026_06_17.html written ({len(html):,} bytes)\n')
print('OK')
print(f'subject_prefix={subject_prefix} comb={fmt(comb_yest)} signed_pct={signed_pct:+.1f}%')
print(f'mw1={fmt(mw1_yest)} se3={fmt(se3_yest)} pkt={fmt(pkt_yest)}')
print(f'forecast_suppressed={forecast_suppressed} dormant={dormant_count}')
