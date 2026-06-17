#!/usr/bin/env python3
"""Build data.json for SFB Daily Report — 2026-06-16"""
import json, math

# ── helpers ──────────────────────────────────────────────────────────────────
def lerp(a, b, t):
    return tuple(round(a[i] + (b[i]-a[i])*t) for i in range(3))

def grad(pct):
    p = max(-25.0, min(25.0, float(pct)))
    if p >= 0:
        t = p/25.0
        bg = lerp((240,229,218),(30,107,48),t)
    else:
        t = -p/25.0
        bg = lerp((240,229,218),(197,69,62),t)
    fg = '#ffffff' if abs(p) >= 13 else '#2C3E50'
    return '#{:02x}{:02x}{:02x}'.format(*bg), fg

def fmt_baht(v):
    return '฿{:,.0f}'.format(v)

def fmt_K(v):
    return '฿{:.0f}K'.format(v/1000)

def pct_str(v, decimals=1):
    sign = '+' if v >= 0 else ''
    return f'{sign}{v:.{decimals}f}%'

def delta_class(v):
    if v > 0.5: return 'delta-up'
    if v < -0.5: return 'delta-down'
    return 'delta-neutral'

def wow_class(v):
    if v >= 0: return 'delta-up'
    if v < -5: return 'delta-down'
    return 'delta-neutral'

# ── date tokens ───────────────────────────────────────────────────────────────
D1 = '2026-06-16'
report_date_display = '16 Jun 2026'
weekday_en = 'Tuesday'
weekday_th = 'วันอังคาร'
window_label = '18 May – 16 Jun 2026'
mtd_label = '1–16 Jun 2026'
d8_display = '9 Jun 2026'
generated_display = '17 Jun 2026 00:15 BKK'

# ── BU chart data (Q2) — 30 days ──────────────────────────────────────────────
BU_DAYS = [
  ('2026-05-18','18/5','Mon', 456785.19,57100.09,62555.97,37360.84,11580.37),
  ('2026-05-19','19/5','Tue', 424776.53,62356.70,63097.00,36278.14,13715.92),
  ('2026-05-20','20/5','Wed', 415251.15,54870.71,84249.38,33292.89,14503.77),
  ('2026-05-21','21/5','Thu', 435188.21,70886.70,54455.93,22005.40,11084.09),
  ('2026-05-22','22/5','Fri', 512707.76,72088.98,84378.20,35263.44,16037.40),
  ('2026-05-23','23/5','Sat', 507555.76,88532.48,58455.91,33600.66,14857.06),
  ('2026-05-24','24/5','Sun', 518461.45,81019.33,70885.75,34686.31,14856.12),
  ('2026-05-25','25/5','Mon', 482917.31,75426.83,72990.44,38335.72,12772.87),
  ('2026-05-26','26/5','Tue', 457603.08,63988.08,57468.08,39595.62, 9460.70),
  ('2026-05-27','27/5','Wed', 483104.38,71601.17,66165.25,30554.34,12553.21),
  ('2026-05-28','28/5','Thu', 525488.03,71972.26,68520.36,34115.50,18818.68),
  ('2026-05-29','29/5','Fri', 637448.60,73479.16,67796.08,44263.79,13566.34),
  ('2026-05-30','30/5','Sat', 643047.24,71286.14,74231.57,33264.99,20365.46),
  ('2026-05-31','31/5','Sun', 527918.41,70260.82,89063.46,37355.73,16967.29),
  ('2026-06-01', '1/6','Mon', 576089.77,65559.16,76952.29,37948.06, 9594.42),
  ('2026-06-02', '2/6','Tue', 473001.63,58275.91,82246.75,35318.32, 8193.42),
  ('2026-06-03', '3/6','Wed', 462414.55,65732.88,71949.56,37972.53, 9739.24),
  ('2026-06-04', '4/6','Thu', 462299.48,61137.15,61707.49,29719.07,17801.90),
  ('2026-06-05', '5/6','Fri', 456603.31,64841.40,85002.72,34817.34,10697.21),
  ('2026-06-06', '6/6','Sat', 459354.04,65320.78,60693.49,39565.26,10817.82),
  ('2026-06-07', '7/6','Sun', 474039.92,53008.61,68107.44,35120.83,10141.30),
  ('2026-06-08', '8/6','Mon', 463915.19,71249.74,62829.84,27605.54,12024.32),
  ('2026-06-09', '9/6','Tue', 456951.39,49380.96,52067.36,27834.68, 9461.72),
  ('2026-06-10','10/6','Wed', 445322.72,65523.54,50818.69,38472.74,11765.46),
  ('2026-06-11','11/6','Thu', 441037.63,63687.12,57677.58,27774.25,10228.05),
  ('2026-06-12','12/6','Fri', 497504.76,67997.87,59558.89,29144.73,10476.70),
  ('2026-06-13','13/6','Sat', 461717.31,66470.29,63057.94,32892.86,17052.31),
  ('2026-06-14','14/6','Sun', 482629.58,67100.25,84904.57,29428.33,11833.69),
  ('2026-06-15','15/6','Mon', 471730.92,64391.84,63330.80,34091.92,13718.67),
  ('2026-06-16','16/6','Tue', 437682.41,63516.16,58621.34,25903.34,16955.43),
]

# ── airport chart data — 30 days ─────────────────────────────────────────────
AP_DAYS = [
  ('2026-05-18', 424007.02, 156854.83, 44520.61),
  ('2026-05-19', 408421.83, 143211.88, 48590.58),
  ('2026-05-20', 403733.73, 124690.33, 73743.84),
  ('2026-05-21', 411267.66, 137253.64, 45099.03),
  ('2026-05-22', 465046.28, 183363.30, 72066.20),
  ('2026-05-23', 488527.21, 163526.10, 47303.71),
  ('2026-05-24', 479529.82, 191812.84, 48566.30),
  ('2026-05-25', 460220.84, 166086.88, 56135.45),
  ('2026-05-26', 431577.58, 157729.56, 38808.42),
  ('2026-05-27', 454556.19, 154491.41, 54930.75),
  ('2026-05-28', 492518.96, 170441.76, 55954.11),
  ('2026-05-29', 577488.70, 204601.76, 54463.51),
  ('2026-05-30', 550925.69, 236790.27, 54479.44),
  ('2026-05-31', 480351.99, 185948.24, 75265.48),
  ('2026-06-01', 517695.87, 185038.42, 63409.41),
  ('2026-06-02', 463538.87, 119565.30, 73931.86),
  ('2026-06-03', 446818.09, 137132.63, 63858.04),
  ('2026-06-04', 451623.97, 127010.21, 54030.91),
  ('2026-06-05', 449271.21, 130735.63, 71955.14),
  ('2026-06-06', 467274.94, 115530.56, 52945.89),
  ('2026-06-07', 445693.76, 138430.82, 56293.52),
  ('2026-06-08', 436542.70, 146051.99, 55029.94),
  ('2026-06-09', 423062.37, 127986.91, 44646.83),
  ('2026-06-10', 445177.18, 126260.51, 40465.46),
  ('2026-06-11', 418543.49, 128747.08, 53114.06),
  ('2026-06-12', 476314.90, 135312.84, 53055.21),
  ('2026-06-13', 464278.67, 121834.40, 55077.64),
  ('2026-06-14', 462593.53, 136398.21, 76904.68),
  ('2026-06-15', 464201.67, 127597.02, 55465.46),
  ('2026-06-16', 436951.51, 111841.29, 53885.88),
]

# ── Q1: location×BU for D1/D2/D8 ─────────────────────────────────────────────
# (location, bu, d1_rev, d1_bills, d2_rev, d2_bills, d8_rev, d8_bills, airport)
LOC_BU = [
  ('18-T1FW4-08-SS','Subway',  100943.11,264, 99704.78,271,103048.85,267,'BKK'),
  ('26-T1MW1-03+04','Subway',   41024.70,119, 47353.38,126, 41352.80,111,'BKK'),
  ('26-T1MW1-03+04','Juice Land',37113.24,107, 31958.99,102, 28609.88, 87,'BKK'),
  ('27-T1SE3-05',  'Subway',    33298.18,123, 32177.40,123, 19334.77, 92,'BKK'),
  ('27-T1SE3-05',  'Juice Land',17918.80, 61, 20999.16, 71, 11247.72, 40,'BKK'),
  ('27-T1SE3-05',  'Vendi',     16955.43, 92, 13718.67, 82,  9461.72, 51,'BKK'),
  ('24-T1EW4-14',  'Subway',    56228.14,164, 59848.73,145, 67610.84,153,'BKK'),
  ('21-T1BE2-06',  'Subway',    49300.05,127, 54836.51,118, 42942.56,115,'BKK'),
  ('04-DMK-T2MTE3-09','Subway', 38875.92,126, 45361.66,126, 46588.79,125,'DMK'),
  ('13-PKT-G1-S',  'Siam Express',27536.31,112,20272.86,67, 16160.74, 76,'PKT'),
  ('20-PKT-Floor 3-S','Siam Express',26349.57,93,35192.60,114,28486.09,87,'PKT'),
  ('17-T1ME2-30',  'Khiang',    25903.34,158, 34091.92,193, 27834.68,145,'BKK'),
  ('05-DMK-Inter-S','Subway',   25342.00,118, 33630.81,117, 26995.32, 90,'DMK'),
  ('19-T1MB1-03',  'Subway',    25087.87, 84, 25850.48, 87, 31191.14, 88,'BKK'),
  ('23-T1CE4-13',  'Subway',    24694.53,115, 32227.96,145, 30904.05,124,'BKK'),
  ('22-DMK-3Pier2-SS','Subway', 19276.65, 66, 11279.42, 56, 19405.64, 72,'DMK'),
  ('22-DMK-3Pier2-SS','Siam Express',4735.46,28,7865.34,45,7420.53,42,'DMK'),
  ('09-DMK-G1-S',  'Subway',    12329.01, 47, 17760.73, 68, 10185.95, 46,'DMK'),
  ('25-DMK-CS',    'Subway',    11282.25, 43, 11699.06, 49, 17390.68, 49,'DMK'),
  ('28 JUICELAND Unit 362','Juice Land',8484.12,43,11433.69,50,9523.36,42,'BKK'),
]

BU_COLOR = {
    'Subway':      '#5551FE',
    'Juice Land':  '#2D7A3F',
    'Siam Express':'#F39C12',
    'Khiang':      '#7B79FF',
    'Vendi':       '#C5453E',
}

SIGNAL_LABEL = {
    'best':     ('⭐ BEST',      's-traffic'),
    'traffic':  ('🚶 Traffic',   's-traffic'),
    'mixed':    ('⚠️ Mixed',     's-quality'),
    'upsell':   ('✅ Upsell',    's-upsell'),
    'stable':   ('─ Stable',    's-soft'),
    'quality':  ('📉 Quality ↓', 's-quality'),
    'premium':  ('🤔 Premium mix','s-upsell'),
    'soft':     ('↘ Soft',      's-soft'),
    'crisis':   ('🚨 CRISIS',   's-crisis'),
}

def signal_3x3(bills_wow, ticket_wow):
    b = 'up' if bills_wow > 3 else ('down' if bills_wow < -3 else 'flat')
    t = 'up' if ticket_wow > 3 else ('down' if ticket_wow < -3 else 'flat')
    m = {
        ('up','up'):'best', ('up','flat'):'traffic', ('up','down'):'mixed',
        ('flat','up'):'upsell', ('flat','flat'):'stable', ('flat','down'):'quality',
        ('down','up'):'premium', ('down','flat'):'soft', ('down','down'):'crisis',
    }
    return SIGNAL_LABEL[m[(b,t)]]

# ── constants ─────────────────────────────────────────────────────────────────
MAX_DAILY = 842195.40
PPB = 220 / MAX_DAILY   # pixel per baht

# ── compute KPIs ─────────────────────────────────────────────────────────────
d1 = BU_DAYS[-1]
d2 = BU_DAYS[-2]
d8 = BU_DAYS[-8]   # index 22 (0-based): '2026-06-09'

d1_subway,d1_jl,d1_se,d1_kh,d1_ve = d1[3],d1[4],d1[5],d1[6],d1[7]
d1_total = d1_subway+d1_jl+d1_se+d1_kh+d1_ve
d2_total = sum(d2[3:8])
d8_total = sum(d8[3:8])

# bills from LOC_BU
d1_bills_total = sum(r[3] for r in LOC_BU)
d8_bills_total = sum(r[7] for r in LOC_BU)
d2_bills_total = sum(r[5] for r in LOC_BU)

d1_ticket = d1_total / d1_bills_total
d8_ticket = d8_total / d8_bills_total

wow_rev  = (d1_total - d8_total) / d8_total * 100
dod_rev  = (d1_total - d2_total) / d2_total * 100
wow_bills = (d1_bills_total - d8_bills_total) / d8_bills_total * 100
wow_ticket = (d1_ticket - (d8_total/d8_bills_total)) / (d8_total/d8_bills_total) * 100

# MTD (Jun 1-16 = last 16 days in BU_DAYS)
mtd_days = BU_DAYS[14:]   # index 14..29
mtd_totals = [sum(r[3:8]) for r in mtd_days]
mtd_sum = sum(mtd_totals)
mtd_avg = mtd_sum / len(mtd_days)
mtd_high = max(mtd_totals)
mtd_low  = min(mtd_totals)
mtd_vs_d1 = (d1_total - mtd_avg) / mtd_avg * 100

# BU-level WoW for legend
BU_NAMES = ['Subway','Juice Land','Siam Express','Khiang','Vendi']
bu_d1 = {'Subway':d1_subway,'Juice Land':d1_jl,'Siam Express':d1_se,'Khiang':d1_kh,'Vendi':d1_ve}
bu_d8 = {'Subway':d8[3],'Juice Land':d8[4],'Siam Express':d8[5],'Khiang':d8[6],'Vendi':d8[7]}

# BU bills from LOC_BU
bu_d1_bills = {}; bu_d8_bills = {}
for r in LOC_BU:
    b = r[1]
    bu_d1_bills[b] = bu_d1_bills.get(b,0) + r[3]
    bu_d8_bills[b] = bu_d8_bills.get(b,0) + r[7]

# airport totals
ap_d1 = {'BKK':AP_DAYS[-1][1],'DMK':AP_DAYS[-1][2],'PKT':AP_DAYS[-1][3]}
ap_d8 = {'BKK':AP_DAYS[-8][1],'DMK':AP_DAYS[-8][2],'PKT':AP_DAYS[-8][3]}
ap_d1_bills = {'BKK':0,'DMK':0,'PKT':0}
ap_d8_bills = {'BKK':0,'DMK':0,'PKT':0}
for r in LOC_BU:
    ap_d1_bills[r[8]] = ap_d1_bills.get(r[8],0) + r[3]
    ap_d8_bills[r[8]] = ap_d8_bills.get(r[8],0) + r[7]

# status_emoji
any_critical = any(
    (r[1]=='Subway' and r[0] in ['23-T1CE4-13']) or
    (r[1]=='Siam Express' and r[0]=='22-DMK-3Pier2-SS')
    for r in LOC_BU
)
status_emoji = '🚨' if any_critical else ('⚠️' if wow_rev < -5 else ('🔥' if wow_rev > 10 else '✅'))

rev_K = fmt_K(d1_total)
loc_count = len(set(r[0] for r in LOC_BU))

# ── build chart repeats ───────────────────────────────────────────────────────
bu_chart_days = []
bu_chart_axis = []
airport_chart_days = []
airport_chart_axis = []

for i,(row,ap_row) in enumerate(zip(BU_DAYS, AP_DAYS)):
    date,axlbl,dow,sw,jl,se,kh,ve = row
    is_d1 = (i == len(BU_DAYS)-1)
    total_day = sw+jl+se+kh+ve
    title = f"{date} ({dow}) — {fmt_baht(total_day)}"

    bu_chart_days.append({
        'd1_class': 'd1' if is_d1 else '',
        'day_title': title,
        'h_subway':  max(1,round(sw*PPB)),
        'h_jl':      max(0,round(jl*PPB)),
        'h_se':      max(0,round(se*PPB)),
        'h_khiang':  max(0,round(kh*PPB)),
        'h_vendi':   max(0,round(ve*PPB)),
    })
    bu_chart_axis.append({
        'ax_label': axlbl,
        'ax_class': 'axd1' if is_d1 else '',
    })

    bkk,dmk,pkt = ap_row[1],ap_row[2],ap_row[3]
    ap_title = f"{date} ({dow}) — {fmt_baht(bkk+dmk+pkt)}"
    airport_chart_days.append({
        'd1_class': 'd1' if is_d1 else '',
        'day_title': ap_title,
        'h_bkk':  max(1,round(bkk*PPB)),
        'h_dmk':  max(0,round(dmk*PPB)),
        'h_pkt':  max(0,round(pkt*PPB)),
    })
    airport_chart_axis.append({
        'ax_label': axlbl,
        'ax_class': 'axd1' if is_d1 else '',
    })

# ── BU legend rows ────────────────────────────────────────────────────────────
bu_legend_rows = []
bu_d1_share_total = d1_total
for bn in BU_NAMES:
    rv1 = bu_d1.get(bn,0)
    rv8 = bu_d8.get(bn,0)
    bl1 = bu_d1_bills.get(bn,0)
    bl8 = bu_d8_bills.get(bn,0)
    tk1 = rv1/bl1 if bl1 else 0
    tk8 = rv8/bl8 if bl8 else 0
    wow_r = (rv1-rv8)/rv8*100 if rv8 else 0
    wow_b = (bl1-bl8)/bl8*100 if bl8 else 0
    wow_t = (tk1-tk8)/tk8*100 if tk8 else 0
    share = rv1/bu_d1_share_total*100
    sig_label, sig_cls = signal_3x3(wow_b, wow_t)
    bu_legend_rows.append({
        'color':       BU_COLOR[bn],
        'bu_name':     bn,
        'd1_rev':      fmt_baht(rv1),
        'd1_bills':    str(bl1),
        'share':       f'{share:.1f}%',
        'wow':         pct_str(wow_r),
        'wow_class':   wow_class(wow_r),
        'bills_delta': pct_str(wow_b),
        'bills_class': delta_class(wow_b),
        'ticket_delta':pct_str(wow_t),
        'ticket_class':delta_class(wow_t),
        'signal':      sig_label,
        'signal_class':sig_cls,
    })

# ── airport legend rows ───────────────────────────────────────────────────────
AP_INFO = [('BKK','Suvarnabhumi','#5551FE'),('DMK','Don Mueang','#7B79FF'),('PKT','Phuket','#F27061')]
airport_legend_rows = []
for code,name,color in AP_INFO:
    rv1 = ap_d1[code]; rv8 = ap_d8[code]
    bl1 = ap_d1_bills[code]; bl8 = ap_d8_bills[code]
    wow_r = (rv1-rv8)/rv8*100 if rv8 else 0
    wow_b = (bl1-bl8)/bl8*100 if bl8 else 0
    share = rv1/d1_total*100
    airport_legend_rows.append({
        'color':       color,
        'airport_name':name,
        'd1_rev':      fmt_baht(rv1),
        'd1_bills':    str(bl1),
        'share':       f'{share:.1f}%',
        'wow':         pct_str(wow_r),
        'wow_class':   wow_class(wow_r),
        'bills_delta': pct_str(wow_b),
        'bills_class': delta_class(wow_b),
    })

# ── heatmap rows ──────────────────────────────────────────────────────────────
# group by location (ordered by location total D1 rev desc)
loc_order = {}
for r in LOC_BU:
    loc = r[0]
    loc_order[loc] = loc_order.get(loc,0) + r[2]
sorted_locs = sorted(loc_order, key=lambda l: -loc_order[l])

heatmap_groups = {}
for r in LOC_BU:
    heatmap_groups.setdefault(r[0],[]).append(r)
for loc in heatmap_groups:
    heatmap_groups[loc].sort(key=lambda r: -r[2])

loc_heatmap_rows = []
for loc in sorted_locs:
    rows = heatmap_groups[loc]
    N = len(rows)
    for i, r in enumerate(rows):
        loc_name, bu, rv1, bl1, rv2, bl2, rv8, bl8, airport = r
        tk1 = rv1/bl1 if bl1 else 0
        tk8 = rv8/bl8 if bl8 else 0
        wow_r = (rv1-rv8)/rv8*100 if rv8 else 0
        wow_b = (bl1-bl8)/bl8*100 if bl8 else 0
        wow_t = (tk1-tk8)/tk8*100 if tk8 else 0

        rb, rf = grad(wow_r); bb, bf = grad(wow_b); tb, tf = grad(wow_t)
        sig_label, sig_cls = signal_3x3(wow_b, wow_t)

        if i == 0:
            loc_cell = f'<td class="heat-bu" rowspan="{N}"><b>{loc_name}</b></td>'
            row_class = 'grp-start'
        else:
            loc_cell = ''
            row_class = ''

        loc_heatmap_rows.append({
            'loc_cell':     loc_cell,
            'row_class':    row_class,
            'bu_color':     BU_COLOR.get(bu,'#999'),
            'bu_name':      bu,
            'airport':      airport,
            'd1_rev':       fmt_baht(rv1),
            'd1_bills':     str(bl1),
            'rev_delta':    pct_str(wow_r),
            'rev_bg':       rb, 'rev_fg': rf,
            'bills_delta':  pct_str(wow_b),
            'bills_bg':     bb, 'bills_fg': bf,
            'ticket_delta': pct_str(wow_t),
            'ticket_bg':    tb, 'ticket_fg': tf,
            'signal':       sig_label,
            'signal_class': sig_cls,
        })

# ── insight bullets ───────────────────────────────────────────────────────────
# top/bottom 3 movers by rev WoW
loc_bu_wows = []
for r in LOC_BU:
    wow_r = (r[2]-r[6])/r[6]*100 if r[6] else 0
    loc_bu_wows.append((r[0], r[1], wow_r, r[2]))
loc_bu_wows.sort(key=lambda x: -x[2])
top3 = loc_bu_wows[:3]
bot3 = loc_bu_wows[-3:]

top3_lines = '\n'.join(f'  • {l} · {b} {pct_str(w)} ({fmt_baht(rv)})' for l,b,w,rv in top3)
bot3_lines = '\n'.join(f'  • {l} · {b} {pct_str(w)} ({fmt_baht(rv)})' for l,b,w,rv in bot3)

insight_bullets = [
    {'bullet_html': f'<b>Revenue {fmt_baht(d1_total)}</b> — WoW <b>{pct_str(wow_rev)}</b> · DoD {pct_str(dod_rev)} · vs MTD avg {pct_str(mtd_vs_d1)} · Bills {d1_bills_total} · Avg ticket {fmt_baht(d1_ticket)}'},
    {'bullet_html': 'Broad growth: Juice Land <b>+28.6%</b> WoW, Siam Express <b>+12.6%</b>, Vendi <b>+79.2%</b> — offset by Subway <b>−4.2%</b> WoW (largest revenue BU).'},
    {'bullet_html': f'<b>Hero BU — Juice Land</b>: ฿{d1_jl:,.0f} D1, WoW +28.6%, bills +24.9%, ticket +3.0%.'},
    {'bullet_html': '<b>17-T1ME2-30 (Khiang) hit NEW MTD LOW</b>: ฿25,903 vs prior MTD low ฿27,606. 28 JUICELAND Unit 362 also NEW MTD LOW: ฿8,484.'},
    {'bullet_html': f'<b>Top 3 movers (WoW)</b>: 27-T1SE3-05·Vendi +79.2% (฿16,955) · 27-T1SE3-05·Subway +72.2% (฿33,298) · 13-PKT-G1-S·Siam Express +70.4% (฿27,536).'},
    {'bullet_html': f'<b>Weakest 3 (WoW)</b>: 22-DMK-3Pier2-SS·Siam Express −36.2% (฿4,735) · 25-DMK-CS·Subway −35.1% (฿11,282) · 24-T1EW4-14·Subway −16.8% (฿56,228).'},
]

# ── subject ───────────────────────────────────────────────────────────────────
subject = f'{status_emoji} SFB Daily — {report_date_display} | {rev_K} (WoW {pct_str(wow_rev)}) | {loc_count} locations'

# ── scalars ───────────────────────────────────────────────────────────────────
scalars = {
    'subject':             subject,
    'report_date_display': report_date_display,
    'weekday_en':          weekday_en,
    'weekday_th':          weekday_th,
    'window_label':        window_label,
    'mtd_label':           mtd_label,
    'd8_display':          d8_display,
    'generated_display':   generated_display,
    'status_emoji':        status_emoji,
    'rev_K':               rev_K,
    'wow_signed':          pct_str(wow_rev),
    'dod_signed':          pct_str(dod_rev),
    'mtd_signed':          pct_str(mtd_vs_d1),
    'bills_total':         str(d1_bills_total),
    'ticket':              fmt_baht(d1_ticket),
    'rev_delta_class':     delta_class(wow_rev),
    'bills_delta_class':   delta_class(wow_bills),
    'ticket_delta_class':  delta_class(wow_ticket),
    'bills_wow_signed':    pct_str(wow_bills),
    'ticket_wow_signed':   pct_str(wow_ticket),
    'mtd_avg_K':           fmt_K(mtd_avg),
    'footer_cchaw':        'CHAW Retailing Co., Ltd. · Internal management report · Generated by automated routine.',
}

data = {
    'scalars': scalars,
    'repeats': {
        'insight_bullets':    insight_bullets,
        'bu_chart_days':      bu_chart_days,
        'bu_chart_axis':      bu_chart_axis,
        'bu_legend_rows':     bu_legend_rows,
        'airport_chart_days': airport_chart_days,
        'airport_chart_axis': airport_chart_axis,
        'airport_legend_rows':airport_legend_rows,
        'loc_heatmap_rows':   loc_heatmap_rows,
    },
    'sections': {},
}

with open('/home/user/report/SFB/data.json','w',encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"data.json written. D1={fmt_baht(d1_total)} WoW={pct_str(wow_rev)} Bills={d1_bills_total}")
print(f"Subject: {subject}")
