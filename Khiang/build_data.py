#!/usr/bin/env python3
import json, math
from datetime import date, timedelta

def fmt_num(v, decimals=0):
    """Format number with thousands separator."""
    if decimals == 0:
        return f"{int(round(v)):,}"
    return f"{v:,.{decimals}f}"

def lerp_hex(a_hex, b_hex, t):
    """Linear interpolate two hex colours."""
    def h2r(h): return tuple(int(h[i:i+2],16) for i in (1,3,5))
    a = h2r(a_hex); b = h2r(b_hex)
    r = lambda x,y: max(0,min(255,int(x+(y-x)*t+0.5)))
    return '#{:02X}{:02X}{:02X}'.format(r(a[0],b[0]),r(a[1],b[1]),r(a[2],b[2]))

def signed_pct_str(pct, decimals=1):
    s = f"{pct:.{decimals}f}"
    return ('+' if pct >= 0 else '') + s + '%'

def arrow_pct_str(pct):
    if pct == '': return ''
    arrow = '▲' if pct >= 0 else '▼'
    return arrow + ('+' if pct >= 0 else '') + f"{pct:.1f}%"

REPORT_DATE = date(2026, 6, 14)
PREV_DATE = REPORT_DATE - timedelta(days=1)

# ── Fixed values ──────────────────────────────────────────────────────────────
# Query A
walk_in_bills = 97; walk_in_revenue = 21394.0
staff_bills   = 75; staff_revenue   = 10094.6
credit_notes  = 0.0  # no CustCred rows in Query A

net_sales   = walk_in_revenue + staff_revenue - credit_notes   # 31488.6
total_bills = walk_in_bills + staff_bills                       # 172
avg_ticket  = int(net_sales / total_bills + 0.5)               # 183

signed_pct   = round((net_sales - 40000) / 40000 * 100, 1)    # -21.3
walk_in_pct  = round(walk_in_bills / total_bills * 100, 1)     # 56.4
staff_pct    = round(staff_bills   / total_bills * 100, 1)     # 43.6
target_icon  = '⚠️'  # net < 40000

# Query F (5d excl. REPORT_DATE)
f_data = [
    (date(2026,6,9),  29783.3, 145),
    (date(2026,6,10), 41166.2, 185),
    (date(2026,6,11), 29718.7, 161),
    (date(2026,6,12), 31185.1, 160),
    (date(2026,6,13), 35195.7, 177),
]
avg_5d       = int(sum(x[1] for x in f_data)/len(f_data) + 0.5)   # 33,410
avg_bills    = int(sum(x[2] for x in f_data)/len(f_data) + 0.5)   # 166
avg_ticket_bench = int(sum(x[1] for x in f_data)/sum(x[2] for x in f_data) + 0.5)  # 201

bills_arrow  = '↑' if total_bills >= avg_bills else '↓'
ticket_arrow = '↑' if avg_ticket >= avg_ticket_bench else '↓'

# Query I (MTD)
net_mtd  = 496071.2; mtd_days_q = 14
avg_mtd  = int(net_mtd / mtd_days_q + 0.5)   # 35,434
mtd_signed_pct = round((avg_mtd - 40000)/40000*100, 1)  # -11.4

# Query H 35-day data (per day, combined segments)
h35 = [
    (date(2026,5,11), 33124.86, 76+104),   # week5
    (date(2026,5,12), 40121.0,  78+116),
    (date(2026,5,13), 40024.7,  102+111),
    (date(2026,5,14), 35358.7,  79+112),
    (date(2026,5,15), 44897.4,  74+139),
    (date(2026,5,16), 37997.8,  74+123),   # 30d start
    (date(2026,5,17), 41196.9,  83+138),
    (date(2026,5,18), 39976.4,  75+132),
    (date(2026,5,19), 38817.8,  55+133),
    (date(2026,5,20), 35623.7,  76+114),
    (date(2026,5,21), 23546.0,  47+86),
    (date(2026,5,22), 37732.2,  87+110),
    (date(2026,5,23), 35953.0,  72+112),
    (date(2026,5,24), 37114.6,  74+117),
    (date(2026,5,25), 41019.5,  63+132),
    (date(2026,5,26), 42367.6,  64+123),
    (date(2026,5,27), 32693.4,  85+107),
    (date(2026,5,28), 36503.8,  65+121),
    (date(2026,5,29), 47362.5,  71+155),
    (date(2026,5,30), 35593.8,  75+108),
    (date(2026,5,31), 39970.9,  84+132),
    (date(2026,6,1),  40604.7,  83+131),
    (date(2026,6,2),  37790.9,  54+131),
    (date(2026,6,3),  40630.8,  91+112),
    (date(2026,6,4),  31799.6,  66+112),
    (date(2026,6,5),  37254.8,  67+123),
    (date(2026,6,6),  42335.0,  67+140),
    (date(2026,6,7),  37579.6,  74+112),
    (date(2026,6,8),  29538.2,  64+104),
    (date(2026,6,9),  29783.3,  56+89),
    (date(2026,6,10), 41166.2,  52+133),
    (date(2026,6,11), 29718.7,  49+112),
    (date(2026,6,12), 31185.1,  55+105),
    (date(2026,6,13), 35195.7,  59+118),
    (date(2026,6,14), 31488.6,  75+97),
]
D30_START = REPORT_DATE - timedelta(days=29)
h30 = [(d,ns,b) for d,ns,b in h35 if d >= D30_START]
net_30d     = sum(ns for _,ns,_ in h30)
days_30     = len(h30)
avg_30d     = int(net_30d / days_30 + 0.5)
bills_30d   = sum(b for _,_,b in h30)
avg_bills_30d = int(bills_30d / days_30 + 0.5)
chart_max   = max(ns for _,ns,_ in h30)
mtd_line_px = round(min(avg_mtd, chart_max) / chart_max * 90)

# Chart days (30 bars)
chart_days = []
chart_labels = []
for d, ns, b in h30:
    bp = max(2, round(ns / chart_max * 90))
    col = '#27AE60' if ns >= 40000 else '#E74C3C'
    chart_days.append({
        'bar_px': bp,
        'bar_color': col,
        'bar_title': f"{d.strftime('%d %b')} ฿{ns:,.0f}",
    })
    is_rd = (d == REPORT_DATE)
    chart_labels.append({
        'day_label': str(d.day),
        'label_color': '#5551FE' if is_rd else '#AAA',
        'label_weight': '700' if is_rd else '400',
    })

# Weekly segment data for customer table
h35_seg = {
    date(2026,5,11): {'walk':104,'staff':76},
    date(2026,5,12): {'walk':116,'staff':78},
    date(2026,5,13): {'walk':111,'staff':102},
    date(2026,5,14): {'walk':112,'staff':79},
    date(2026,5,15): {'walk':139,'staff':74},
    date(2026,5,16): {'walk':123,'staff':74},
    date(2026,5,17): {'walk':138,'staff':83},
    date(2026,5,18): {'walk':132,'staff':75},
    date(2026,5,19): {'walk':133,'staff':55},
    date(2026,5,20): {'walk':114,'staff':76},
    date(2026,5,21): {'walk':86,'staff':47},
    date(2026,5,22): {'walk':110,'staff':87},
    date(2026,5,23): {'walk':112,'staff':72},
    date(2026,5,24): {'walk':117,'staff':74},
    date(2026,5,25): {'walk':132,'staff':63},
    date(2026,5,26): {'walk':123,'staff':64},
    date(2026,5,27): {'walk':107,'staff':85},
    date(2026,5,28): {'walk':121,'staff':65},
    date(2026,5,29): {'walk':155,'staff':71},
    date(2026,5,30): {'walk':108,'staff':75},
    date(2026,5,31): {'walk':132,'staff':84},
    date(2026,6,1):  {'walk':131,'staff':83},
    date(2026,6,2):  {'walk':131,'staff':54},
    date(2026,6,3):  {'walk':112,'staff':91},
    date(2026,6,4):  {'walk':112,'staff':66},
    date(2026,6,5):  {'walk':123,'staff':67},
    date(2026,6,6):  {'walk':140,'staff':67},
    date(2026,6,7):  {'walk':112,'staff':74},
    date(2026,6,8):  {'walk':104,'staff':64},
    date(2026,6,9):  {'walk':89,'staff':56},
    date(2026,6,10): {'walk':133,'staff':52},
    date(2026,6,11): {'walk':112,'staff':49},
    date(2026,6,12): {'walk':105,'staff':55},
    date(2026,6,13): {'walk':118,'staff':59},
    date(2026,6,14): {'walk':97,'staff':75},
}

THAI_MONTHS_ABB = ['','ม.ค.','ก.พ.','มี.ค.','เม.ย.','พ.ค.','มิ.ย.','ก.ค.','ส.ค.','ก.ย.','ต.ค.','พ.ย.','ธ.ค.']

def week_label(start_d, end_d):
    if start_d.month == end_d.month:
        return f"{start_d.day}–{end_d.day} {THAI_MONTHS_ABB[end_d.month]}"
    else:
        return f"{start_d.day} {THAI_MONTHS_ABB[start_d.month]}–{end_d.day} {THAI_MONTHS_ABB[end_d.month]}"

weeks_agg = {}
for w in range(1, 6):
    end = REPORT_DATE - timedelta(days=(w-1)*7)
    start = end - timedelta(days=6)
    wa = 0; sa = 0
    for dd in (start + timedelta(days=i) for i in range(7)):
        if dd in h35_seg:
            wa += h35_seg[dd]['walk']; sa += h35_seg[dd]['staff']
    weeks_agg[w] = {'walk':wa,'staff':sa,'total':wa+sa,'start':start,'end':end,
                    'label': week_label(start, end), 'is_current': w==1}

def cell_tokens(cur, prev, is_current):
    if prev and prev != 0:
        p = round((cur - prev)/prev * 100, 1)
        pct = arrow_pct_str(p)
        col = '#27AE60' if p >= 0 else '#E74C3C'
    else:
        pct = ''; col = '#888'
    return {
        'val': f"{cur:,}",
        'pct': pct,
        'color': col,
        'weight': '700' if is_current else '400',
        'bg': '#EEECFF' if is_current else '#FFFFFF',
    }

week_headers = []
walk_cells   = []
staff_cells  = []
total_cells  = []
for w in range(5, 0, -1):
    wa = weeks_agg[w]; is_cur = wa['is_current']
    prev_w = w + 1
    prev_wa = weeks_agg.get(prev_w)
    week_headers.append({'label': wa['label'],
                         'head_color': '#5551FE' if is_cur else '#888',
                         'head_bg':    '#EEECFF' if is_cur else '#F8F9FA'})
    walk_cells.append(cell_tokens(wa['walk'], prev_wa['walk'] if prev_wa else None, is_cur))
    staff_cells.append(cell_tokens(wa['staff'], prev_wa['staff'] if prev_wa else None, is_cur))
    total_cells.append(cell_tokens(wa['total'], prev_wa['total'] if prev_wa else None, is_cur))
    # total row always weight 700
    total_cells[-1]['weight'] = '700'

# Promo weekly
promo_agg = {
    5: {'staff10':236, 'set50':271},
    4: {'staff10':214, 'set50':311},
    3: {'staff10':224, 'set50':301},
    2: {'staff10':217, 'set50':254},
    1: {'staff10':163, 'set50':319},
}
staff10_cells = []
set50_cells   = []
for w in range(5, 0, -1):
    pa = promo_agg[w]; is_cur = (w==1)
    prev_pa = promo_agg.get(w+1)
    staff10_cells.append(cell_tokens(pa['staff10'], prev_pa['staff10'] if prev_pa else None, is_cur))
    set50_cells.append(cell_tokens(pa['set50'],   prev_pa['set50']   if prev_pa else None, is_cur))

# Query J 14-day (heatmap)
j14 = {
    date(2026,6,1):  {'ns':40604.7, 'bills':214},
    date(2026,6,2):  {'ns':37790.9, 'bills':185},
    date(2026,6,3):  {'ns':40630.8, 'bills':203},
    date(2026,6,4):  {'ns':31799.6, 'bills':178},
    date(2026,6,5):  {'ns':37254.8, 'bills':190},
    date(2026,6,6):  {'ns':42335.0, 'bills':207},
    date(2026,6,7):  {'ns':37579.6, 'bills':186},
    date(2026,6,8):  {'ns':29538.2, 'bills':168},
    date(2026,6,9):  {'ns':29783.3, 'bills':145},
    date(2026,6,10): {'ns':41166.2, 'bills':185},
    date(2026,6,11): {'ns':29718.7, 'bills':161},
    date(2026,6,12): {'ns':31185.1, 'bills':160},
    date(2026,6,13): {'ns':35195.7, 'bills':177},
    date(2026,6,14): {'ns':31488.6, 'bills':172},
}
for d, row in j14.items():
    row['ticket'] = int(row['ns'] / row['bills'] + 0.5)

# Last 7 displayed rows
D7_START = REPORT_DATE - timedelta(days=6)
heatmap_display = sorted([(d,v) for d,v in j14.items() if d >= D7_START])

# Per-column min/max for shading
revs    = [v['ns']     for _,v in heatmap_display]
billss  = [v['bills']  for _,v in heatmap_display]
tickets = [v['ticket'] for _,v in heatmap_display]

def shade(vals, val, cream='#FBF3EA', indigo='#C9C7FF'):
    lo, hi = min(vals), max(vals)
    t = 0.5 if hi == lo else (val - lo) / (hi - lo)
    return lerp_hex(cream, indigo, t)

def is_max(vals, val): return val == max(vals)

THAI_DAYS = ['จ.','อ.','พ.','พฤ.','ศ.','ส.','อา.']  # Mon=0..Sun=6

heatmap_rows = []
for d, row in heatmap_display:
    ns = row['ns']; b = row['bills']; tk = row['ticket']
    is_rd = (d == REPORT_DATE)
    wd = THAI_DAYS[d.weekday()]
    day_label = f"{wd} {d.day}/{d.month}"
    prev_d = d - timedelta(days=7)
    if prev_d in j14 and j14[prev_d]['ns'] > 0:
        prev_ns = j14[prev_d]['ns']
        wp = round((ns - prev_ns)/prev_ns*100, 1)
        wow_pct    = ('+' if wp >= 0 else '') + f"{wp:.1f}%"
        wow_color  = '#27AE60' if wp >= 0 else '#E74C3C'
        wow_weight = '700' if abs(wp) >= 10 else '400'
    else:
        wow_pct = '—'; wow_color = '#888'; wow_weight = '400'
    heatmap_rows.append({
        'day_label_th': day_label,
        'day_weight':   '700' if is_rd else '400',
        'rev':          f"{int(ns+0.5):,}",
        'rev_bg':       shade(revs, ns),
        'rev_fg':       '#2C3E50',
        'rev_weight':   '700' if is_max(revs, ns) else '400',
        'bills':        str(b),
        'bills_bg':     shade(billss, b),
        'bills_fg':     '#2C3E50',
        'bills_weight': '700' if is_max(billss, b) else '400',
        'ticket':       str(tk),
        'ticket_bg':    shade(tickets, tk),
        'ticket_fg':    '#2C3E50',
        'ticket_weight':'700' if is_max(tickets, tk) else '400',
        'wow_pct':      wow_pct,
        'wow_color':    wow_color,
        'wow_weight':   wow_weight,
    })

# Top items (Query B)
items_raw = [
    ('K008','ข้าวผัดโบราณ',15),
    ('K013','ข้าวกะเพราไก่คาราเกะ',7),
    ('K014','มาม่าผัดกะเพราไก่',14),
    ('K015','มาม่าต้มยำทรงเครื่อง',4),
    ('K018','แกงจืดเต้าหู้หมูสับ',7),
    ('K019','ต้มยำกุ้ง',4),
    ('K020','หมูยอทอด',6),
    ('K021','กุยช่ายกรอบ',12),
    ('K022','ไก่คาราเกะทอด',2),
    ('K023','ไข่ดาว',90),
    ('K024','ไข่เจียว',16),
    ('K025','ข้าวสวย',9),
    ('K026','กุนเชียง',3),
    ('K028','โค้ก',61),
    ('K029','โค้ก ซีโร่',9),
    ('K031','เก๊กฮวย',3),
    ('K032','ชาไทย (แก้ว)',4),
    ('K035','สละลอยแก้ว',2),
    ('K036','ลูกตาลลอยแก้ว Toddy Palm In Syrup',1),
    ('K037','ข้าวผัดกะเพราหมูสับ',56),
    ('K038','ข้าวผัดกะเพราไก่ชิ้น',24),
    ('K039','ข้าวไก่กระเทียม',6),
    ('K040','ข้าวหมูกระเทียม',13),
    ('K041','ข้าวไข่ยู่ยี่',17),
    ('K042','ข้าวกะเพราดิบเถื่อน (เนื้อโคขุน)',7),
    ('K043','ข้าวกะเพราเทพหมู',10),
    ('K045','ข้าวกะเพราเปิดย่าง',14),
    ('K046','ข้าวไก่ผัดน้ำมันหอย',3),
    ('K047','ข้าวหมูผัดน้ำมันหอย',4),
    ('K056','Minere Mineral Water 600 Ml',27),
    ('K057','กุยช่ายแซ่บ',6),
]
RICE = {'K008','K013','K016','K017','K037','K038','K039','K040','K041','K042','K043','K044','K045','K046','K047'}

# 5d avg per item (Query C)
avg5d_map = {
    'K008':49/5,'K013':45/5,'K014':46/5,'K015':39/5,'K016':2/2,'K017':3/3,
    'K018':39/5,'K019':21/5,'K020':40/5,'K021':87/5,'K022':1/1,'K023':465/5,
    'K024':72/5,'K025':34/5,'K026':9/4,'K028':293/5,'K029':76/5,'K030':9/5,
    'K031':10/5,'K032':20/5,'K035':1/1,'K036':8/4,'K037':241/5,'K038':101/5,
    'K039':39/5,'K040':62/5,'K041':54/5,'K042':47/5,'K043':69/5,'K045':94/5,
    'K046':24/5,'K047':39/5,'K056':132/5,'K057':37/5,
}
FC_PCT = {'K037':'26.2%','K038':'24.3%','K039':'23.3%','K040':'29.7%','K041':'26.1%',
          'K042':'23.3%','K043':'25.3%','K045':'29.9%','K046':'22.6%','K047':'29.1%',
          'K008':'27.2%','K013':'26.0%'}

def badge(itemid, qty):
    a5 = avg5d_map.get(itemid)
    if a5 is None: return {'bg':'#D1ECF1','fg':'#0C5460','label':'New'}
    a5r = int(a5 + 0.5)
    if a5r == 0: return {'bg':'#D1ECF1','fg':'#0C5460','label':'New'}
    pct = (qty - a5r) / a5r * 100
    label = ('+' if pct >= 0 else '') + f"{pct:.0f}%"
    if pct >= 15:    return {'bg':'#D4EDDA','fg':'#155724','label':label}
    if pct <= -10:   return {'bg':'#F8D7DA','fg':'#721C24','label':label}
    return {'bg':'#FEF3CD','fg':'#856404','label':label}

items_sorted = sorted(items_raw, key=lambda x: -x[2])
top10_all  = []
top10_rice = []
for i, (itemid, name, qty) in enumerate(items_sorted[:10]):
    b = badge(itemid, qty)
    a5 = avg5d_map.get(itemid)
    a5_str = str(int(a5+0.5)) if a5 else '—'
    star = ' ⭐' if itemid in RICE else ''
    top10_all.append({
        'rank': str(i+1), 'itemid': itemid, 'name': name + star, 'qty': str(qty),
        'avg5d': a5_str, 'badge_bg': b['bg'], 'badge_fg': b['fg'], 'badge_label': b['label'],
        'row_bg': '#FAFAFA' if i%2==1 else '#FFFFFF',
    })
rice_sorted = [(itemid,name,qty) for itemid,name,qty in items_sorted if itemid in RICE]
for i, (itemid, name, qty) in enumerate(rice_sorted[:10]):
    b = badge(itemid, qty)
    a5 = avg5d_map.get(itemid)
    a5_str = str(int(a5+0.5)) if a5 else '—'
    top10_rice.append({
        'rank': str(i+1), 'itemid': itemid, 'name': name, 'qty': str(qty),
        'avg5d': a5_str, 'fc_pct': FC_PCT.get(itemid,'—'),
        'badge_bg': b['bg'], 'badge_fg': b['fg'], 'badge_label': b['label'],
        'row_bg': '#FAFAFA' if i%2==1 else '#FFFFFF',
    })

# Anomaly detection
REV_BENCH = {0:1149,1:763,2:373,3:356,4:240,5:166,6:538,7:1636,8:1910,9:3223,10:3827,
             11:4673,12:5768,13:3631,14:4196,15:3000,16:3813,17:2969,18:3641,19:3069,
             20:3080,21:2162,22:1562,23:553}
BILL_BENCH = {h: max(1, int(rev/avg_ticket+0.5)) for h,rev in REV_BENCH.items()}

qD = {0:(3,605),1:(2,404.5),2:(2,134.5),6:(3,784.5),7:(8,1126),8:(5,545.7),9:(8,1336.7),
      10:(14,1891.2),11:(20,2711.1),12:(19,3800.9),13:(18,3688.5),14:(7,1385),15:(12,2401.5),
      16:(5,1658.5),17:(9,1995.7),18:(10,1688.7),19:(4,1163),20:(8,1262.5),21:(8,1428.7),
      22:(5,1186.4),23:(2,290)}
qE = {0:(3,595),1:(5,781),2:(4,518.5),3:(1,117),5:(1,150),6:(7,999.7),7:(7,913.5),8:(5,1028),
      9:(10,2165),10:(5,1531.5),11:(19,3491.9),12:(15,3047.1),13:(10,2356),14:(11,2298.8),
      15:(11,2398.2),16:(13,2644.2),17:(13,2045.9),18:(13,3081),19:(9,1934.7),20:(11,2714.7),
      21:(2,195),22:(1,104),23:(1,85)}

# Top3 per hour from Query E2 (decoded)
top3_raw = {
    0: [('K023','ไข่ดาว',3),('K028','โค้ก',3),('K014','มาม่าผัดกะเพราไก่',2)],
    1: [('K014','มาม่าผัดกะเพราไก่',1),('K023','ไข่ดาว',1),('K028','โค้ก',1)],
    2: [('K037','ข้าวผัดกะเพราหมูสับ',1),('K056','Minere Mineral W…',1)],
    6: [('K021','กุยช่ายกรอบ',2),('K008','ข้าวผัดโบราณ',1),('K037','ข้าวผัดกะเพราหมูสับ',1)],
    7: [('K023','ไข่ดาว',3),('K028','โค้ก',2),('K038','ข้าวผัดกะเพราไก่ชิ้น',2)],
    8: [('K023','ไข่ดาว',2),('K041','ข้าวไข่ยู่ยี่',2),('K028','โค้ก',1)],
    9: [('K037','ข้าวผัดกะเพราหมูสับ',3),('K023','ไข่ดาว',2),('K028','โค้ก',2)],
    10:[('K037','ข้าวผัดกะเพราหมูสับ',6),('K023','ไข่ดาว',5),('K029','โค้ก ซีโร่',3)],
    11:[('K023','ไข่ดาว',11),('K037','ข้าวผัดกะเพราหมูสับ',9),('K028','โค้ก',7)],
    12:[('K023','ไข่ดาว',17),('K028','โค้ก',14),('K037','ข้าวผัดกะเพราหมูสับ',8)],
    13:[('K023','ไข่ดาว',12),('K038','ข้าวผัดกะเพราไก่ชิ้น',7),('K028','โค้ก',6)],
    14:[('K023','ไข่ดาว',5),('K014','มาม่าผัดกะเพราไก่',3),('K028','โค้ก',2)],
    15:[('K028','โค้ก',5),('K037','ข้าวผัดกะเพราหมูสับ',5),('K023','ไข่ดาว',4)],
    16:[('K023','ไข่ดาว',6),('K028','โค้ก',5),('K037','ข้าวผัดกะเพราหมูสับ',2)],
    17:[('K024','ไข่เจียว',5),('K037','ข้าวผัดกะเพราหมูสับ',3),('K014','มาม่าผัดกะเพราไก่',2)],
    18:[('K023','ไข่ดาว',6),('K028','โค้ก',5),('K041','ข้าวไข่ยู่ยี่',3)],
    19:[('K056','Minere Mineral W…',3),('K043','ข้าวกะเพราเทพหมู',2),('K015','มาม่าต้มยำทรงเครื่อง',1)],
    20:[('K024','ไข่เจียว',3),('K008','ข้าวผัดโบราณ',2),('K037','ข้าวผัดกะเพราหมูสับ',2)],
    21:[('K023','ไข่ดาว',5),('K045','ข้าวกะเพราเปิดย่าง',3),('K056','Minere Mineral W…',3)],
    22:[('K023','ไข่ดาว',5),('K028','โค้ก',4),('K037','ข้าวผัดกะเพราหมูสับ',3)],
    23:[('K023','ไข่ดาว',1),('K028','โค้ก',1),('K032','ชาไทย (แก้ว)',1)],
}

def build_top3(h):
    items = top3_raw.get(h, [])
    if not items: return '—'
    parts = [f"{name} ×{qty}" for _,name,qty in items[:3]]
    return '<br>'.join(parts)

# Check anomaly (only hours present in Query D)
anomaly_hours = set()
for h, (b, rev) in qD.items():
    thresh = BILL_BENCH[h] * 0.50
    if b < thresh:
        anomaly_hours.add(h)

anomaly_count = len(anomaly_hours)

# Build hourly rows
all_hours = sorted(set(qD.keys()) | set(qE.keys()))
hourly_rows = []
row_counter = 0
for h in all_hours:
    cur_b, cur_r = qD.get(h, (0, 0))
    prv_b, prv_r = qE.get(h, (0, 0))
    is_anom = h in anomaly_hours
    if is_anom:
        row_bg = '#FFEBEE'
    else:
        row_bg = '#FFFFFF' if row_counter % 2 == 0 else '#FAFAFA'
    row_counter += 1

    if prv_r > 0:
        chg = (cur_r - prv_r) / prv_r * 100
        chg_str = ('+' if chg >= 0 else '') + f"{chg:.1f}%"
        chg_col = '#27AE60' if chg >= 10 else ('#E74C3C' if chg <= -10 else '#888')
        chg_wt  = '700' if abs(chg) >= 10 else '400'
    elif cur_r > 0:
        chg_str = 'New'; chg_col = '#0C5460'; chg_wt = '400'
    else:
        chg_str = '—'; chg_col = '#888'; chg_wt = '400'

    hour_color = '#C62828' if is_anom else '#2C3E50'
    cur_color  = '#E74C3C' if is_anom else '#2C3E50'
    hourly_rows.append({
        'hour':         f"{h:02d}:00",
        'hour_flag':    ' 🚨' if is_anom else '',
        'hour_color':   hour_color,
        'row_bg':       row_bg,
        'prev_rev':     f"{int(prv_r+0.5):,}" if prv_r else '—',
        'cur_rev':      f"{int(cur_r+0.5):,}" if cur_r else '—',
        'prev_color':   '#888',
        'cur_color':    cur_color,
        'change_pct':   chg_str,
        'change_color': chg_col,
        'change_weight':chg_wt,
        'bench':        f"{REV_BENCH[h]:,}",
        'top3':         build_top3(h),
    })

# Promo status
staff10_bills = 28; set50_bills = 46
promo = (staff10_bills + set50_bills) > 0

# Build rice_top10_lines for group message
rice_lines = []
for i, (itemid, name, qty) in enumerate(rice_sorted[:10]):
    a5 = avg5d_map.get(itemid)
    a5r = int(a5 + 0.5) if a5 else 0
    pct = round((qty - a5r) / a5r * 100) if a5r else 0
    badge_label = ('+' if pct >= 0 else '') + f"{pct}%"
    rice_lines.append(f"{i+1}. {itemid} {name} — {qty} ({badge_label})")
rice_top10_lines = '\n'.join(rice_lines)

# ── Assemble data.json ────────────────────────────────────────────────────────
data = {
    "scalars": {
        "report_date_display": "14 June 2026",
        "report_day_en":       "Sunday",
        "report_date_short":   "14 มิ.ย.",
        "prev_date_short":     "13 มิ.ย.",
        "report_year":         "2026",
        "generated_date":      "15 June 2026",
        "chaw_values":         "Curious · Team · Act Fast · Empowered · Simple",
        "net_sales":           f"{int(net_sales+0.5):,}",
        "signed_pct":          signed_pct_str(signed_pct),
        "target_icon":         target_icon,
        "avg_5d":              f"{avg_5d:,}",
        "total_bills":         str(total_bills),
        "avg_bills":           str(avg_bills),
        "bills_arrow":         bills_arrow,
        "walk_in_bills":       str(walk_in_bills),
        "walk_in_revenue":     f"{int(walk_in_revenue+0.5):,}",
        "walk_in_pct":         f"{walk_in_pct:.1f}",
        "staff_bills":         str(staff_bills),
        "staff_revenue":       f"{int(staff_revenue+0.5):,}",
        "staff_pct":           f"{staff_pct:.1f}",
        "avg_ticket":          str(avg_ticket),
        "avg_ticket_bench":    str(avg_ticket_bench),
        "ticket_arrow":        ticket_arrow,
        "net_30d":             f"{int(net_30d+0.5):,}",
        "avg_30d":             f"{avg_30d:,}",
        "d30_start":           "16 พ.ค.",
        "net_mtd":             f"{int(net_mtd+0.5):,}",
        "avg_mtd":             f"{avg_mtd:,}",
        "mtd_days":            str(mtd_days_q),
        "mtd_month":           "June 2026",
        "mtd_signed_pct":      signed_pct_str(mtd_signed_pct),
        "mtd_line_px":         str(mtd_line_px),
        "avg_bills_30d":       str(avg_bills_30d),
        "anomaly_count":       str(anomaly_count),
        "staff10_bills":       str(staff10_bills),
        "set50_bills":         str(set50_bills),
        "staff10_status":      "ACTIVE",
        "set50_status":        "ACTIVE",
        "staff10_badge_bg":    "#D4EDDA",
        "staff10_badge_fg":    "#155724",
        "set50_badge_bg":      "#D4EDDA",
        "set50_badge_fg":      "#155724",
    },
    "repeats": {
        "chart_days":    chart_days,
        "chart_labels":  chart_labels,
        "week_headers":  week_headers,
        "walk_cells":    walk_cells,
        "staff_cells":   staff_cells,
        "total_cells":   total_cells,
        "heatmap_rows":  heatmap_rows,
        "top10_all":     top10_all,
        "top10_rice":    top10_rice,
        "hourly_rows":   hourly_rows,
        "staff10_cells": staff10_cells,
        "set50_cells":   set50_cells,
    },
    "sections": {
        "alert_banner": anomaly_count > 0,
        "promo":        promo,
    },
}

with open('/home/user/report/Khiang/data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"data.json written.")
print(f"Anomaly hours: {sorted(anomaly_hours)}")
print(f"anomaly_count: {anomaly_count}")
print(f"rice_top10_lines:\n{rice_top10_lines}")
print(f"net_sales={int(net_sales+0.5):,}  signed_pct={signed_pct_str(signed_pct)}")
print(f"avg_mtd={avg_mtd:,}  avg_30d={avg_30d:,}")
