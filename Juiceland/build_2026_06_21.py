#!/usr/bin/env python3
"""
Build Juiceland Daily Sales Report email.html
Report date: 2026-06-21 (Sunday, วันอาทิตย์, Asia/Bangkok)
Run date:    2026-06-22
"""
import re, sys, math, os, json
from datetime import date, timedelta
from collections import defaultdict

# ─── Template helpers ───

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

# ─── Load raw query data from transcript ───

JSONL = '/root/.claude/projects/-home-user-report/0648b92c-3144-526e-a932-0d9d4f69bfcc.jsonl'

def load_query(line_idx):
    with open(JSONL) as f:
        lines = f.readlines()
    obj = json.loads(lines[line_idx])
    msg = obj['message']
    content = msg['content']
    for b in content:
        if isinstance(b, dict) and b.get('type') == 'tool_result':
            for sub in b.get('content', []):
                if isinstance(sub, dict):
                    return json.loads(sub['text'])['items']
    return []

QA_ITEMS = load_query(44)  # daily totals
QB_ITEMS = load_query(45)  # top-20
QC_ITEMS = load_query(50)  # new products
QD_ITEMS = load_query(52)  # dormant
QE_ITEMS = load_query(53)  # seasonal

# ─── Dates ───

REPORT_DATE  = date(2026, 6, 21)
RUN_DATE     = date(2026, 6, 22)
WINDOW_START = REPORT_DATE - timedelta(days=29)  # 2026-05-23

TH_WD      = ['จ','อ','พ','พฤ','ศ','ส','อา']
TH_WD_FULL = ['วันจันทร์','วันอังคาร','วันพุธ','วันพฤหัสบดี','วันศุกร์','วันเสาร์','วันอาทิตย์']
EN_MON     = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
EN_MON_F   = ['January','February','March','April','May','June',
               'July','August','September','October','November','December']

def fmt(n, d=0):
    return f'{round(n):,}' if d == 0 else f'{n:,.{d}f}'

def th_wd(d): return TH_WD[d.weekday()]
def en_day(d): return f'{d.day} {EN_MON_F[d.month-1]} {d.year}'
def en_short(d): return f'{d.day} {EN_MON[d.month-1]}'

def parse_date(s):
    """Parse DD/MM/YYYY."""
    d, m, y = s.split('/')
    return date(int(y), int(m), int(d))

def truncate(s, n=34):
    s = s.strip().split('\n')[0]  # strip newlines
    return (s[:n] + '…') if len(s) > n else s

# ─── Query A: daily totals ───

daily = defaultdict(lambda: {33: 0.0, 105: 0.0, 109: 0.0})
for item in QA_ITEMS:
    d = parse_date(item['trandate'])
    loc = int(item['location'])
    net = float(item['net_sales'])
    if loc in (33, 105, 109, 169):
        key = 33 if loc in (33, 169) else loc
        daily[d][key] += net

dates = sorted(daily.keys())
assert len(dates) == 30, f'Expected 30 dates, got {len(dates)}'

mw1  = {d: daily[d][33]  for d in dates}
se3  = {d: daily[d][105] for d in dates}
pkt  = {d: daily[d][109] for d in dates}
comb = {d: mw1[d] + se3[d] + pkt[d] for d in dates}

yest       = REPORT_DATE
mw1_y      = mw1[yest]
se3_y      = se3[yest]
pkt_y      = pkt[yest]
comb_y     = mw1_y + se3_y + pkt_y

mw1_avg  = sum(mw1.values()) / 30
se3_avg  = sum(se3.values()) / 30
pkt_avg  = sum(pkt.values()) / 30
comb_avg = mw1_avg + se3_avg + pkt_avg

mw1_min = min(mw1.values());  mw1_max = max(mw1.values())
se3_min = min(se3.values());  se3_max = max(se3.values())
pkt_min = min(pkt.values());  pkt_max = max(pkt.values())

signed_pct = (comb_y - comb_avg) / comb_avg * 100
mw1_vs30   = (mw1_y - mw1_avg)   / mw1_avg   * 100
se3_vs30   = (se3_y - se3_avg)   / se3_avg   * 100
pkt_vs30   = (pkt_y - pkt_avg)   / pkt_avg   * 100

subject_prefix = '🔥' if signed_pct >= 10 else ('⚠️' if signed_pct <= -10 else '✅')

chart_max = max(max(mw1.values()), max(se3.values()), max(pkt.values()))
def bar(n): return str(round(n / chart_max * 220))

last7 = dates[-7:]
mw1_7d   = sum(mw1[d] for d in last7)
se3_7d   = sum(se3[d] for d in last7)
pkt_7d   = sum(pkt[d] for d in last7)
comb_7d  = mw1_7d + se3_7d + pkt_7d
last7_avg_val = comb_7d / 7

# ─── Forecast (for Monday 2026-06-23, same weekday = Monday) ───
# forecast_date = RUN_DATE (2026-06-22, Sunday)
fc_date = RUN_DATE

def same_wday_hist(branch_dict, target, weeks=4):
    vals = []
    d = target - timedelta(weeks=1)
    while len(vals) < weeks:
        if d in branch_dict:
            vals.append(branch_dict[d])
        d -= timedelta(weeks=1)
    return vals

def forecast_branch(hist, branch_dict, all_dates):
    if len(hist) < 2:
        return 0, 0, '🔴'
    base = sum(hist) / len(hist)
    last7v = [branch_dict[d] for d in all_dates[-7:]]
    trend  = (base + sum(last7v) / 7) / 2
    stdev  = math.sqrt(sum((x - base) ** 2 for x in hist) / len(hist))
    band   = max(stdev, trend * 0.08)
    cp     = stdev / base * 100 if base else 25
    conf   = '🟢' if cp < 12 else ('🟡' if cp < 25 else '🔴')
    return trend, band, conf

mw1_hist = same_wday_hist(mw1, fc_date)
se3_hist = same_wday_hist(se3, fc_date)
pkt_hist = same_wday_hist(pkt, fc_date)

mw1_fc, mw1_band, mw1_conf = forecast_branch(mw1_hist, mw1, dates)
se3_fc, se3_band, se3_conf = forecast_branch(se3_hist, se3, dates)
pkt_fc, pkt_band, pkt_conf = forecast_branch(pkt_hist, pkt, dates)

comb_fc   = mw1_fc + se3_fc + pkt_fc
comb_band = math.sqrt(mw1_band**2 + se3_band**2 + pkt_band**2)
cp_c      = comb_band / comb_fc * 100 if comb_fc else 25
comb_conf = '🟢' if cp_c < 12 else ('🟡' if cp_c < 25 else '🔴')

# ─── Query B: top-20 per branch ───

def top20_rows(items, loc_id):
    branch_items = [i for i in items if int(i['location']) == loc_id]
    branch_items.sort(key=lambda x: -int(x['qty']))
    rows = []
    for i, item in enumerate(branch_items[:20]):
        memo = truncate(item['memo'].strip().split('\n')[0], 32)
        rows.append({
            'rank':         str(i + 1),
            'memo_display': memo,
            'memo_full':    item['memo'].strip().split('\n')[0],
            'qty':          str(item['qty']),
            'revenue':      f"{float(item['revenue']):,.2f}",
            'bills':        str(item['bills']),
            'row_bg':       '#FAFAFA' if i % 2 else '#fff',
        })
    return rows

top20_branches = [
    {'header_color': '#5551FE', 'header_label': 'MW1 · 26-T1MW1-03+04',    'top20_rows': top20_rows(QB_ITEMS, 33)},
    {'header_color': '#F27061', 'header_label': 'SE3 · 27-T1SE3-05',        'top20_rows': top20_rows(QB_ITEMS, 105)},
    {'header_color': '#2E7D32', 'header_label': 'PKT · 28 Unit 362 (Phuket)', 'top20_rows': top20_rows(QB_ITEMS, 109)},
]

# ─── Query C: new products ───

# Category mapping: (normalized_key → (display_name, launch_str, notes_str, category))
# category: 'drinks' | 'fruits' | 'newcat'
SKU_MAP = {
    # Drinks
    'PPR':       ('PRIDE PARROT RED',             '1 Jun 2026',  'MW1, SE3, PKT', 'drinks'),
    'PPY':       ('PRIDE PARROT YELLOW',           '1 Jun 2026',  'MW1, SE3, PKT', 'drinks'),
    'HOTCHOC':   ('HOT CHOCOLATE 8 oz',            '24 May 2026', 'MW1, SE3',      'drinks'),
    'FANTAORG':  ('Fanta Orange 450ml. (Bottle)',  '31 May 2026', 'PKT',           'drinks'),
    'FANTASTR':  ('Fanta Strawberry 450ml.',       '1 Jun 2026',  'PKT',           'drinks'),
    'SPRITE':    ('Sprite 500ml. (Bottle)',         '30 May 2026', 'PKT',           'drinks'),
    'MOOVE':     ('MOOVE CLEAR PROTEIN',           '13 Jun 2026', 'MW1',           'drinks'),
    # Fruits
    'LYCHEE':    ('LYCHEE 400G.',                  '28 May 2026', 'MW1, SE3',      'fruits'),
    'MANGOSTEEN':('MANGOSTEEN 400g.',              '28 May 2026', 'SE3, MW1',      'fruits'),
    'ROSEAPPLE': ('ROSE APPLE 400G.',              '30 May 2026', 'SE3',           'fruits'),
    'ORANGE400': ('Orange 400g Pack',              '18 Jun 2026', 'SE3',           'fruits'),
    # New Category
    'CHICKEN':   ('Chicken Club Croissant',        '22 May 2026', 'SE3',           'newcat'),
    'OATBERRY':  ('Overnight Oat Berry 16 oz',    '22 May 2026', 'SE3, MW1',      'newcat'),
    'BANANATOP': ('BANANA TOPPING',               '12 Jun 2026', 'MW1',           'newcat'),
    'DFTOP':     ('DRAGON FRUIT TOPPING',         '19 Jun 2026', 'MW1',           'newcat'),
    'GRPETOP':   ('SEEDLESS GRAPE TOPPING',       '5 Jun 2026',  'MW1',           'newcat'),
    'ICE16':     ('Ice 16oz',                     '18 Jun 2026', 'PKT',           'newcat'),
    'HOTEGREEN': ('Hot Tea Green Tea 12oz',       '18 Jun 2026', 'PKT',           'newcat'),
}

def classify_qc(memo, loc):
    """Return SKU key for a QC item."""
    m = memo.strip().split('\n')[0].upper()
    if 'PRIDE PARROT RED' in m or 'PRIDE PARROT RED SMOOTHIE' in m:
        return 'PPR'
    if 'PRIDE PARROT YELLOW' in m or 'PRIDE PARROT YELLOW SMOOTHIE' in m:
        return 'PPY'
    if 'HOT CHOCOLATE' in m:
        return 'HOTCHOC'
    if 'FANTA ORANGE' in m:
        return 'FANTAORG'
    if 'FANTA STRAWBERRY' in m:
        return 'FANTASTR'
    if 'SPRITE' in m:
        return 'SPRITE'
    if 'MOOVE CLEAR PROTEIN' in m:
        return 'MOOVE'
    if 'LYCHEE' in m:
        return 'LYCHEE'
    if 'MANGOSTEEN' in m:
        return 'MANGOSTEEN'
    if 'ROSE APPLE' in m:
        return 'ROSEAPPLE'
    if 'ORANGE 400' in m or memo.strip().split('\n')[0] == 'Orange 400 g (Pack)':
        return 'ORANGE400'
    if 'CHICKEN CLUB' in m or 'CHICKEN CLUB CROISSANT' in m or (loc == 105 and 'CHICKEN CLUB' in m):
        return 'CHICKEN'
    if 'OVERNIGHT OAT BERRY' in m or 'OVERNIGHT OAT BERRY' in m.replace(' ',''):
        return 'OATBERRY'
    if 'BANANA TOPPING' in m:
        return 'BANANATOP'
    if 'DRAGON FRUIT TOPPING' in m:
        return 'DFTOP'
    if 'SEEDLESS GRAPE TOPPING' in m:
        return 'GRPETOP'
    if 'ICE 16OZ' in m or m == 'ICE 16OZ':
        return 'ICE16'
    if 'HOT TEA GREEN TEA' in m:
        return 'HOTEGREEN'
    return None  # exclude: noise/malformed/one-hit-wonders

# Additional check for Chicken Club (SE3 specific)
def classify_qc_v2(memo, loc):
    m = memo.strip().split('\n')[0]
    mu = m.upper()
    if 'PRIDE PARROT RED' in mu:
        return 'PPR'
    if 'PRIDE PARROT YELLOW' in mu:
        return 'PPY'
    if 'HOT CHOCOLATE' in mu:
        return 'HOTCHOC'
    if 'FANTA ORANGE' in mu:
        return 'FANTAORG'
    if 'FANTA STRAWBERRY' in mu:
        return 'FANTASTR'
    if 'SPRITE' in mu:
        return 'SPRITE'
    if 'MOOVE CLEAR PROTEIN' in mu:
        return 'MOOVE'
    if 'LYCHEE' in mu:
        return 'LYCHEE'
    if 'MANGOSTEEN' in mu:
        return 'MANGOSTEEN'
    if 'ROSE APPLE' in mu:
        return 'ROSEAPPLE'
    if mu == 'ORANGE 400 G (PACK)':
        return 'ORANGE400'
    if 'CHICKEN CLUB' in mu:
        return 'CHICKEN'
    if 'OVERNIGHT OAT BERRY' in mu:
        return 'OATBERRY'
    if mu == 'BANANA TOPPING':
        return 'BANANATOP'
    if mu == 'DRAGON FRUIT TOPPING':
        return 'DFTOP'
    if mu == 'SEEDLESS GRAPE TOPPING':
        return 'GRPETOP'
    if mu in ('ICE 16OZ',):
        return 'ICE16'
    if 'GREEN TEA' in mu and 'HOT TEA' in mu:
        return 'HOTEGREEN'
    # Exact match for Orange 400g
    if m == 'Orange 400 g (Pack)':
        return 'ORANGE400'
    if 'ICE 16' in mu and loc == 109:
        return 'ICE16'
    return None

REPORT_DATE_STR = '21/06/2026'

sku_totals = defaultdict(lambda: {'qty': 0, 'rev': 0.0, 'yest_qty': 0})
for item in QC_ITEMS:
    key = classify_qc_v2(item['memo'], int(item['location']))
    if key is None:
        continue
    q = int(item['qty'])
    r = float(item['revenue'])
    sku_totals[key]['qty'] += q
    sku_totals[key]['rev'] += r
    if item['trandate'] == REPORT_DATE_STR:
        sku_totals[key]['yest_qty'] += q

# Build NP rows per category
def status_badge(key, yest_qty, total_qty, total_days=30):
    avg_per_day = total_qty / total_days
    # Check if dormant (not sold yesterday)
    if yest_qty == 0 and total_qty < 5:
        return '🔴 no sales — dormant'
    if yest_qty == 0 and avg_per_day < 0.5:
        return '⚪ not sold yesterday'
    if yest_qty == 0:
        return '🟡 no sales yesterday'
    if yest_qty >= 2:
        return '🟢 on target'
    return '⚪ 1 sale yesterday'

def build_np_rows(category):
    rows = []
    for key, (display, launch, notes, cat) in SKU_MAP.items():
        if cat != category:
            continue
        t = sku_totals.get(key, {'qty': 0, 'rev': 0.0, 'yest_qty': 0})
        total_u = t['qty']
        yest_u  = t['yest_qty']
        if total_u == 0:
            badge = '🔴 no sales recorded'
        elif yest_u == 0 and total_u < 5:
            badge = '🔴 no sales — dormant'
        elif yest_u == 0:
            badge = '🟡 no sales yesterday'
        elif yest_u >= 2:
            badge = '🟢 on target'
        else:
            badge = '⚪ 1 sale yesterday'
        # Special overrides
        if key == 'HOTCHOC':
            badge = '🔴 dormant since 29 May'
        if key in ('BANANATOP', 'DFTOP', 'GRPETOP', 'ICE16', 'HOTEGREEN') and total_u <= 5:
            badge = '⚪ new — minimal data'
        rows.append({
            'memo':        display,
            'launch':      launch,
            'notes':       notes,
            'total_units': str(total_u),
            'total_rev':   fmt(round(t['rev'])),
            'branch_split': notes,
            'yest_units':  str(yest_u),
            'status_badge': badge,
        })
    return rows

drinks_rows  = build_np_rows('drinks')
fruits_rows  = build_np_rows('fruits')
newcat_rows  = build_np_rows('newcat')

drinks_n  = len(drinks_rows)
fruits_n  = len(fruits_rows)
newcat_n  = len(newcat_rows)

drinks_u   = sum(sku_totals[k]['qty'] for k, (_, _, _, c) in SKU_MAP.items() if c == 'drinks')
fruits_u   = sum(sku_totals[k]['qty'] for k, (_, _, _, c) in SKU_MAP.items() if c == 'fruits')
newcat_u   = sum(sku_totals[k]['qty'] for k, (_, _, _, c) in SKU_MAP.items() if c == 'newcat')
drinks_rev = sum(sku_totals[k]['rev'] for k, (_, _, _, c) in SKU_MAP.items() if c == 'drinks')
fruits_rev = sum(sku_totals[k]['rev'] for k, (_, _, _, c) in SKU_MAP.items() if c == 'fruits')
newcat_rev = sum(sku_totals[k]['rev'] for k, (_, _, _, c) in SKU_MAP.items() if c == 'newcat')
np_total_u   = drinks_u + fruits_u + newcat_u
np_total_rev = drinks_rev + fruits_rev + newcat_rev

total_skus = drinks_n + fruits_n + newcat_n

np_type_tables = [
    {'type_bg': '#1976D2', 'type_fg': '#fff', 'type_icon': '🥤', 'type_label': 'Drinks',         'np_rows': drinks_rows},
    {'type_bg': '#AD1457', 'type_fg': '#fff', 'type_icon': '🍉', 'type_label': 'Seasonal Fruits', 'np_rows': fruits_rows},
    {'type_bg': '#2E7D32', 'type_fg': '#fff', 'type_icon': '⭐', 'type_label': 'New Category',    'np_rows': newcat_rows},
]

# ─── Query D: dormant items ───

# Filter: qty_30d >= 3, last_sold <= report_date - 7, no \n in memo
DORMANT_CUTOFF = REPORT_DATE - timedelta(days=7)  # 2026-06-14

def is_clean(memo):
    return '\n' not in memo and len(memo.strip()) > 0

def gap_days_fn(last_str):
    return (REPORT_DATE - parse_date(last_str)).days

def gap_color_fn(g):
    return '#C62828' if g >= 14 else '#E65100'

def build_dormant_rows(loc_id):
    rows = []
    for item in QD_ITEMS:
        if int(item['location']) != loc_id:
            continue
        memo = item['memo']
        if not is_clean(memo):
            continue
        qty = int(item['qty_30d'])
        if qty < 3:
            continue
        last_str = item['last_sold']
        last_d   = parse_date(last_str)
        if last_d > DORMANT_CUTOFF:
            continue
        g = gap_days_fn(last_str)
        rows.append({
            'memo_display':  truncate(memo),
            'memo_full':     memo.strip(),
            'qty_30d':       fmt(qty),
            'days_sold_30d': item['days_sold_30d'],
            'rev_30d':       fmt(round(float(item['rev_30d']))),
            'gap_days':      g,
            'gap_color':     gap_color_fn(g),
        })
    # Sort by qty_30d desc
    rows.sort(key=lambda r: -int(r['qty_30d'].replace(',', '')))
    return rows

dormant_mw1 = build_dormant_rows(33)
dormant_se3 = build_dormant_rows(105)
dormant_pkt = build_dormant_rows(109)
dormant_count = len(dormant_mw1) + len(dormant_se3) + len(dormant_pkt)

dormant_branches = [
    {'branch': 'MW1', 'header_color': '#5551FE', 'branch_count': str(len(dormant_mw1)), 'dormant_rows': dormant_mw1},
    {'branch': 'SE3', 'header_color': '#F27061', 'branch_count': str(len(dormant_se3)), 'dormant_rows': dormant_se3},
    {'branch': 'PKT', 'header_color': '#2E7D32', 'branch_count': str(len(dormant_pkt)), 'dormant_rows': dormant_pkt},
]

# ─── AM review items: dormant with gap 7-13d, top 9 by rev ───

am_items_raw = []
for loc_id, branch in [(33, 'MW1'), (105, 'SE3'), (109, 'PKT')]:
    for item in QD_ITEMS:
        if int(item['location']) != loc_id:
            continue
        memo = item['memo']
        if not is_clean(memo):
            continue
        qty = int(item['qty_30d'])
        if qty < 3:
            continue
        last_str = item['last_sold']
        last_d   = parse_date(last_str)
        g = (REPORT_DATE - last_d).days
        if 7 <= g <= 13:
            rev = float(item['rev_30d'])
            days_sold = int(item['days_sold_30d'])
            velocity  = round(qty / days_sold, 1) if days_sold > 0 else 0
            target    = max(1, round(qty / 30, 1))
            hypo = f'🟠 Possible stock-out — was ฿{fmt(round(rev/30))}/d avg when selling'
            am_items_raw.append({
                'memo':          memo.strip().split('\n')[0],
                'last_sold':     f'{last_d.day} {EN_MON_F[last_d.month-1]} {last_d.year}',
                'gap_days':      str(g),
                'velocity_7d':   str(velocity),
                'target':        str(target),
                'branch_split':  branch,
                'hypothesis_color': '#E65100',
                'hypothesis_text':  hypo,
                'sort_rev':      rev,
            })

am_items_raw.sort(key=lambda x: -x['sort_rev'])
am_items = [{k: v for k, v in item.items() if k != 'sort_rev'} for item in am_items_raw[:9]]
am_queue_count = len(am_items)

# ─── Query E: seasonal tracker ───

grape_total_rev = sum(float(i['total_revenue']) for i in QE_ITEMS)
grape_last_mw1 = None
grape_last_se3 = None
for i in QE_ITEMS:
    last = parse_date(i['last_sold'])
    loc  = int(i['location'])
    if 'SEEDLESS GRAPE 400G' in i['memo'].upper():
        if loc == 33 and (grape_last_mw1 is None or last > grape_last_mw1):
            grape_last_mw1 = last
        if loc == 105 and (grape_last_se3 is None or last > grape_last_se3):
            grape_last_se3 = last

# New seasonal fruit revenue in 30-day window for MW1 and SE3
# MW1: LYCHEE + MANGOSTEEN + SEEDLESS GRAPE TOPPING
mw1_fruit_keys = {'LYCHEE', 'MANGOSTEEN', 'GRPETOP'}
se3_fruit_keys = {'LYCHEE', 'MANGOSTEEN', 'ROSEAPPLE', 'ORANGE400'}

mw1_fruit_rev = sum(sku_totals[k]['rev'] for k in mw1_fruit_keys)
se3_fruit_rev = sum(sku_totals[k]['rev'] for k in se3_fruit_keys)

mw1_fruit_pd  = mw1_fruit_rev / 30
se3_fruit_pd  = se3_fruit_rev / 30

# Historical grape baselines (daily avg while grapes were selling)
mw1_grape_baseline = 339
se3_grape_baseline = 251

mw1_coverage = mw1_fruit_pd / mw1_grape_baseline * 100
se3_coverage = se3_fruit_pd / se3_grape_baseline * 100

def cov_color(p):
    return '#155724' if p >= 100 else ('#856404' if p >= 70 else '#721C24')
def cov_bg(p):
    return '#D4EDDA' if p >= 100 else ('#FFF3CD' if p >= 70 else '#F8D7DA')
def cov_badge(p):
    return '✅ Fully replaced' if p >= 100 else ('🟡 Partial — monitor' if p >= 70 else '🔴 Large gap — push promotion or add SKU')

# Seasonal SKUs for the table
# Compute per-SKU per-branch totals from QC
lychee_mw1_u  = sum(int(i['qty']) for i in QC_ITEMS if classify_qc_v2(i['memo'], int(i['location'])) == 'LYCHEE' and int(i['location']) == 33)
lychee_se3_u  = sum(int(i['qty']) for i in QC_ITEMS if classify_qc_v2(i['memo'], int(i['location'])) == 'LYCHEE' and int(i['location']) == 105)
mango_mw1_u   = sum(int(i['qty']) for i in QC_ITEMS if classify_qc_v2(i['memo'], int(i['location'])) == 'MANGOSTEEN' and int(i['location']) == 33)
mango_se3_u   = sum(int(i['qty']) for i in QC_ITEMS if classify_qc_v2(i['memo'], int(i['location'])) == 'MANGOSTEEN' and int(i['location']) == 105)
rose_se3_u    = sku_totals['ROSEAPPLE']['qty']
orange_se3_u  = sku_totals['ORANGE400']['qty']

lychee_mw1_rev = sum(float(i['revenue']) for i in QC_ITEMS if classify_qc_v2(i['memo'], int(i['location'])) == 'LYCHEE' and int(i['location']) == 33)
lychee_se3_rev = sum(float(i['revenue']) for i in QC_ITEMS if classify_qc_v2(i['memo'], int(i['location'])) == 'LYCHEE' and int(i['location']) == 105)
mango_mw1_rev  = sum(float(i['revenue']) for i in QC_ITEMS if classify_qc_v2(i['memo'], int(i['location'])) == 'MANGOSTEEN' and int(i['location']) == 33)
mango_se3_rev  = sum(float(i['revenue']) for i in QC_ITEMS if classify_qc_v2(i['memo'], int(i['location'])) == 'MANGOSTEEN' and int(i['location']) == 105)

seasonal_skus = [
    {'fruit_emoji': '🍈', 'memo': 'LYCHEE 400G.',    'launch': '28 May 2026',
     'mw1_units': str(lychee_mw1_u), 'mw1_per_day': fmt(lychee_mw1_rev / 30),
     'se3_units': str(lychee_se3_u), 'se3_per_day': fmt(lychee_se3_rev / 30)},
    {'fruit_emoji': '🟣', 'memo': 'MANGOSTEEN 400g.', 'launch': '28 May 2026',
     'mw1_units': str(mango_mw1_u) if mango_mw1_u else '—', 'mw1_per_day': fmt(mango_mw1_rev / 30),
     'se3_units': str(mango_se3_u), 'se3_per_day': fmt(mango_se3_rev / 30)},
    {'fruit_emoji': '🌸', 'memo': 'ROSE APPLE 400G.', 'launch': '30 May 2026',
     'mw1_units': '—', 'mw1_per_day': '0',
     'se3_units': str(rose_se3_u), 'se3_per_day': fmt(sku_totals['ROSEAPPLE']['rev'] / 30)},
    {'fruit_emoji': '🍊', 'memo': 'Orange 400g Pack', 'launch': '18 Jun 2026',
     'mw1_units': '—', 'mw1_per_day': '0',
     'se3_units': str(orange_se3_u), 'se3_per_day': fmt(sku_totals['ORANGE400']['rev'] / 30)},
]

seasonal_coverage = [
    {
        'branch_label':       'MW1 (Suvarnabhumi T1)',
        'branch_color':       '#5551FE',
        'grape_baseline':     fmt(mw1_grape_baseline),
        'new_fruit_per_day':  fmt(round(mw1_fruit_pd)),
        'coverage_pct':       f'{mw1_coverage:.0f}',
        'coverage_color':     cov_color(mw1_coverage),
        'daily_gap':          f'฿{fmt(round(mw1_grape_baseline - mw1_fruit_pd))}/d',
        'monthly_impact':     f'-฿{fmt(round(abs(mw1_grape_baseline - mw1_fruit_pd) * 30))}/month',
        'badge_bg':           cov_bg(mw1_coverage),
        'badge_text':         cov_badge(mw1_coverage),
    },
    {
        'branch_label':       'SE3 (Suvarnabhumi T1)',
        'branch_color':       '#F27061',
        'grape_baseline':     fmt(se3_grape_baseline),
        'new_fruit_per_day':  fmt(round(se3_fruit_pd)),
        'coverage_pct':       f'{se3_coverage:.0f}',
        'coverage_color':     cov_color(se3_coverage),
        'daily_gap':          f'฿{fmt(round(abs(se3_grape_baseline - se3_fruit_pd)))}/d surplus' if se3_coverage > 100 else f'฿{fmt(round(se3_grape_baseline - se3_fruit_pd))}/d',
        'monthly_impact':     f'+฿{fmt(round(abs(se3_fruit_pd - se3_grape_baseline) * 30))}/month surplus' if se3_coverage > 100 else f'-฿{fmt(round((se3_grape_baseline - se3_fruit_pd) * 30))}/month',
        'badge_bg':           cov_bg(se3_coverage),
        'badge_text':         cov_badge(se3_coverage),
    },
]

# ─── Forecast scalars ───

commentary_text = (
    f'Yesterday ({en_day(REPORT_DATE)} · {TH_WD_FULL[REPORT_DATE.weekday()]}), '
    f'combined net was ฿{fmt(comb_y)} ex-VAT, '
    f'{abs(signed_pct):.1f}% {"above" if signed_pct >= 0 else "below"} the 30-day average. '
    f'MW1 came in at ฿{fmt(mw1_y)} ({mw1_vs30:+.1f}% vs avg), '
    f'SE3 at ฿{fmt(se3_y)} ({se3_vs30:+.1f}% vs avg), '
    f'PKT at ฿{fmt(pkt_y)} ({pkt_vs30:+.1f}% vs avg). '
    f'SE3 and PKT moved sharply in opposite directions — SE3 had its strongest Sunday in 4 weeks '
    f'while PKT came in below average, keeping the combined figure near baseline. '
    f'All branches recorded sales.'
)

anomaly_items = [
    {'anomaly_text': f'SE3 +{se3_vs30:.0f}% vs 30d avg (฿{fmt(se3_y)}) — strongest Sunday in recent weeks',
     'anomaly_section_ref': 'Trend Chart §3'},
    {'anomaly_text': f'PKT {pkt_vs30:.0f}% vs 30d avg (฿{fmt(pkt_y)}) — sharp dip, check staffing/hours',
     'anomaly_section_ref': 'Trend Chart §3'},
    {'anomaly_text': f'MAEVAREE Mango Sticky Rice dormant MW1 13d + SE3 9d — was top revenue item (฿{fmt(5331+8147)})',
     'anomaly_section_ref': 'Dormant SKUs §7'},
    {'anomaly_text': f'MW1 seasonal fruit coverage only {mw1_coverage:.0f}% of grape baseline (฿{fmt(mw1_grape_baseline)}/d lost)',
     'anomaly_section_ref': 'Seasonal Tracker §6'},
    {'anomaly_text': f'Pride Parrot Red+Yellow on target — combined {sku_totals["PPR"]["yest_qty"]+sku_totals["PPY"]["yest_qty"]} units yesterday across branches',
     'anomaly_section_ref': 'New Products §4'},
]

# ─── Chart data ───

chart_days = []
for d in dates:
    chart_days.append({
        'date':            d.strftime('%Y-%m-%d'),
        'day_num':         str(d.day),
        'weekday_th_abbr': th_wd(d),
        'mw1_net':         fmt(mw1[d]),
        'se3_net':         fmt(se3[d]),
        'pkt_net':         fmt(pkt[d]),
        'mw1_bar_px':      bar(mw1[d]),
        'se3_bar_px':      bar(se3[d]),
        'pkt_bar_px':      bar(pkt[d]),
    })

# ─── Last-7 table ───

last7_headers = []
for i, d in enumerate(last7):
    is_y = (d == REPORT_DATE)
    last7_headers.append({
        'col_date':       en_short(d),
        'col_weekday_th': th_wd(d),
        'header_bg':      'background:#4744CD;' if is_y else '',
    })

def last7_cells_branch(branch_dict):
    cells = []
    for d in last7:
        is_y = (d == REPORT_DATE)
        cells.append({
            'net':        fmt(branch_dict[d]),
            'cell_style': 'background:#FFF3E0;font-weight:700;' if is_y else '',
        })
    return cells

def last7_cells_comb():
    cells = []
    for d in last7:
        is_y = (d == REPORT_DATE)
        cells.append({
            'net':     fmt(comb[d]),
            'cell_bg': 'background:#FFF3E0;' if is_y else '',
        })
    return cells

# ─── Assemble scalars ───

scalars = {
    'report_date':         REPORT_DATE.strftime('%Y-%m-%d'),
    'report_date_display': en_day(REPORT_DATE),
    'report_day_th':       TH_WD_FULL[REPORT_DATE.weekday()],
    'window_30d_start':    en_day(WINDOW_START),
    'generated_timestamp': '2026-06-22 07:30',
    'subject_prefix':      subject_prefix,
    'comb_net':            fmt(comb_y),
    'signed_pct':          f'{signed_pct:+.1f}',
    'am_queue_count':      str(am_queue_count),
    'dormant_count':       str(dormant_count),
    'mw1_avg_30d':         fmt(mw1_avg),
    'se3_avg_30d':         fmt(se3_avg),
    'pkt_avg_30d':         fmt(pkt_avg),
    'comb_avg_30d':        fmt(comb_avg),
    'mw1_min_30d':         fmt(mw1_min),
    'mw1_max_30d':         fmt(mw1_max),
    'se3_min_30d':         fmt(se3_min),
    'se3_max_30d':         fmt(se3_max),
    'pkt_min_30d':         fmt(pkt_min),
    'pkt_max_30d':         fmt(pkt_max),
    'comb_monthly_runrate': f'{comb_avg * 30 / 1000:,.1f}K',
    'last7_total':         fmt(comb_7d),
    'last7_avg':           fmt(last7_avg_val),
    'mw1_7d_total':        fmt(mw1_7d),
    'se3_7d_total':        fmt(se3_7d),
    'pkt_7d_total':        fmt(pkt_7d),
    'comb_7d_total':       fmt(comb_7d),
    'np_summary_line':     f'{total_skus} new SKUs · launched 22 May–21 Jun 2026 · Drinks · Seasonal Fruits · New Category',
    'np_total_units':      str(np_total_u),
    'np_total_rev':        fmt(round(np_total_rev)),
    'drinks_n':            str(drinks_n),
    'drinks_todate_units': str(drinks_u),
    'drinks_todate_rev':   fmt(round(drinks_rev)),
    'fruit_n':             str(fruits_n),
    'fruit_todate_units':  str(fruits_u),
    'fruit_todate_rev':    fmt(round(fruits_rev)),
    'new_cat_n':           str(newcat_n),
    'new_cat_todate_units': str(newcat_u),
    'new_cat_todate_rev':  fmt(round(newcat_rev)),
    'grape_total_rev':     fmt(round(grape_total_rev)),
    'grape_last_mw1':      en_day(grape_last_mw1) if grape_last_mw1 else 'n/a',
    'grape_last_se3':      en_day(grape_last_se3) if grape_last_se3 else 'n/a',
    # Forecast
    'forecast_date_display': en_day(RUN_DATE),
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
    'last7_mw1':         last7_cells_branch(mw1),
    'last7_se3':         last7_cells_branch(se3),
    'last7_pkt':         last7_cells_branch(pkt),
    'last7_comb':        last7_cells_comb(),
    'top20_branches':    top20_branches,
    'np_type_tables':    np_type_tables,
    'seasonal_skus':     seasonal_skus,
    'seasonal_coverage': seasonal_coverage,
    'dormant_branches':  dormant_branches,
    'anomaly_items':     anomaly_items,
    'am_items':          am_items,
}

sections = {
    'am_review':           am_queue_count > 0,
    'seasonal':            True,
    'dormant':             dormant_count > 0,
    'forecast_shown':      True,
    'forecast_suppressed': False,
    'anomaly_shown':       len(anomaly_items) > 0,
}

# ─── Read templates & build ───

BASE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE, 'juiceland-template.html'), encoding='utf-8') as f:
    main_tpl = f.read()

with open(os.path.join(BASE, 'juiceland-prediction-section.html'), encoding='utf-8') as f:
    pred_tpl = f.read()

# Fill prediction section first
pred_html = fill(pred_tpl, scalars, repeats, sections)

# Inject prediction section at top of body padding div
inject = '<div style="padding:24px;">'
main_tpl = main_tpl.replace(inject, inject + '\n' + pred_html, 1)

# Fill main template
html = fill(main_tpl, scalars, repeats, sections)

out_path = os.path.join(BASE, 'email.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)

sys.stderr.write(f'email.html written ({len(html):,} bytes)\n')
sys.stderr.write(f'np_total_units={np_total_u}, drinks={drinks_u}, fruits={fruits_u}, newcat={newcat_u}\n')
sys.stderr.write(f'dormant_count={dormant_count} (MW1:{len(dormant_mw1)}, SE3:{len(dormant_se3)}, PKT:{len(dormant_pkt)})\n')
sys.stderr.write(f'am_queue_count={am_queue_count}\n')
sys.stderr.write(f'comb_y={comb_y:.0f} signed_pct={signed_pct:+.1f}%\n')
sys.stderr.write(f'mw1_coverage={mw1_coverage:.0f}% se3_coverage={se3_coverage:.0f}%\n')
sys.stderr.write(f'forecast_comb={fmt(comb_fc-comb_band)}–{fmt(comb_fc+comb_band)} {comb_conf}\n')
print('OK')
