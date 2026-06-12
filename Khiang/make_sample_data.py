#!/usr/bin/env python3
"""
make_sample_data.py — generate a realistic SAMPLE data.json for khiang-template.html.

Purpose: preview the email layout without touching NetSuite. Seeded RNG → stable output.
Implements the same derivations as khiang-queries.md (heatmap shading, WoW, chart scaling,
customer-trend chart) so the preview looks like a real send.

Usage:
    python3 make_sample_data.py > sample-data.json
    python3 fill_template.py khiang-template.html sample-data.json > khiang-sample.html

Regenerate BOTH files whenever khiang-template.html changes.
"""
import json, random, datetime

random.seed(27)  # Khiang location id — stable sample across runs

TARGET = 40000
BAR_PX_MAX = 90

TH_DAYS = ["จ", "อ", "พ", "พฤ", "ศ", "ส", "อา"]  # Mon..Sun
TH_MONTHS = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
             "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
EN_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

MENU = [
    ("K037", "ข้าวกะเพราหมูสับ", 26.2, True),
    ("K038", "ข้าวกะเพราไก่", 24.3, True),
    ("K039", "ข้าวกะเพราหมูกรอบ", 23.3, True),
    ("K040", "ข้าวผัดกุ้ง", 29.7, True),
    ("K041", "ข้าวคั่วกลิ้งหมู", 26.1, True),
    ("K042", "ข้าวผัดพริกแกงไก่", 23.3, True),
    ("K043", "ข้าวหมูกระเทียม", 25.3, True),
    ("K045", "ข้าวผัดปู", 29.9, True),
    ("K046", "ข้าวไก่กระเทียม", 22.6, True),
    ("K047", "ข้าวผัดต้มยำทะเล", 29.1, True),
    ("K008", "ข้าวไข่เจียวหมูสับ", 27.2, True),
    ("K013", "ข้าวไข่ข้นกุ้ง", 26.0, True),
    ("K101", "ไข่ดาว", None, False),
    ("K102", "น้ำเปล่า", None, False),
    ("K103", "ชาไทยเย็น", None, False),
    ("K104", "โค้ก", None, False),
]

def fmt(n):
    return f"{round(n):,}"

def lerp_hex(a, b, t):
    a = a.lstrip("#"); b = b.lstrip("#")
    out = "".join(f"{round(int(a[i:i+2],16)+(int(b[i:i+2],16)-int(a[i:i+2],16))*t):02X}"
                  for i in (0, 2, 4))
    return "#" + out

def th_label(d):
    return f"{TH_DAYS[d.weekday()]} {d.day}/{d.month}"

# ── dates: pretend REPORT_DATE = yesterday (Asia/Bangkok-ish; sample only) ──
today = datetime.date.today()
REPORT_DATE = today - datetime.timedelta(days=1)
PREV_DATE = REPORT_DATE - datetime.timedelta(days=1)
D30 = [REPORT_DATE - datetime.timedelta(days=i) for i in range(29, -1, -1)]
D35 = [REPORT_DATE - datetime.timedelta(days=i) for i in range(34, -1, -1)]
D14 = [REPORT_DATE - datetime.timedelta(days=i) for i in range(13, -1, -1)]

# ── synth daily series: weekday-shaped revenue + bills ──
def day_sales(d):
    base = 42000 + [0, -2500, -1500, 1000, 4500, 6500, 3000][d.weekday()]
    return max(18000, round(base + random.gauss(0, 4200)))

sales = {d: day_sales(d) for d in D14 + D35}
bills = {d: max(90, round(sales[d] / random.uniform(175, 200))) for d in sales}

rep_sales = sales[REPORT_DATE]
rep_bills = bills[REPORT_DATE]
walk_in_bills = round(rep_bills * 0.72)
staff_bills = rep_bills - walk_in_bills
walk_in_rev = round(rep_sales * 0.78)
staff_rev = rep_sales - walk_in_rev
avg_ticket = round(rep_sales / rep_bills)

# 5d benchmarks
d5 = [REPORT_DATE - datetime.timedelta(days=i) for i in range(1, 6)]
avg_5d = round(sum(sales[d] for d in d5) / 5)
avg_bills_5d = round(sum(bills[d] for d in d5) / 5)
avg_ticket_bench = round(avg_5d / avg_bills_5d)

# 30d + MTD
net_30d = sum(sales[d] for d in D30)
avg_30d = round(net_30d / 30)
mtd_days_list = [d for d in D30 if d.month == REPORT_DATE.month and d <= REPORT_DATE]
net_mtd = sum(sales[d] for d in mtd_days_list)
mtd_days = len(mtd_days_list)
avg_mtd = round(net_mtd / mtd_days)
mtd_signed = round((avg_mtd - TARGET) / TARGET * 100, 1)

signed_pct = round((rep_sales - TARGET) / TARGET * 100, 1)

# ── 30-day sales chart ──
chart_max = max(sales[d] for d in D30)
mtd_line_px = round(min(avg_mtd, chart_max) / chart_max * BAR_PX_MAX)
chart_days, chart_labels = [], []
for d in D30:
    chart_days.append({
        "bar_px": max(2, round(sales[d] / chart_max * BAR_PX_MAX)),
        "bar_color": "#27AE60" if sales[d] >= TARGET else "#E74C3C",
        "bar_title": f"{d.day} {EN_MONTHS[d.month-1]} — ฿{fmt(sales[d])}",
    })
    is_rep = d == REPORT_DATE
    chart_labels.append({
        "day_label": f"{d.day:02d}",
        "label_color": "#5551FE" if is_rep else "#AAA",
        "label_weight": "700" if is_rep else "400",
    })

# ── customer trend by week: TRANSPOSED, 5 week columns × segment rows ──
walk_b = {d: round(bills[d] * random.uniform(0.65, 0.80)) for d in D35}
staff_b = {d: bills[d] - walk_b[d] for d in D35}
avg_bills_30d = round(sum(bills[d] for d in D30) / 30)

def week_days(w):  # w = 1 newest .. 5 oldest
    end = REPORT_DATE - datetime.timedelta(days=(w - 1) * 7)
    return [end - datetime.timedelta(days=i) for i in range(6, -1, -1)]

def week_label(days):
    a, b = days[0], days[-1]
    if a.month == b.month:
        return f"{a.day}–{b.day} {TH_MONTHS[a.month-1]}"
    return f"{a.day} {TH_MONTHS[a.month-1]}–{b.day} {TH_MONTHS[b.month-1]}"

weeks = []
for w in (5, 4, 3, 2, 1):  # oldest → newest
    ds = week_days(w)
    walk = sum(walk_b.get(d, 0) for d in ds)
    staff = sum(staff_b.get(d, 0) for d in ds)
    weeks.append({"w": w, "days": ds, "walk": walk, "staff": staff,
                  "total": walk + staff})

week_headers = [{
    "label": week_label(wk["days"]),
    "head_color": "#5551FE" if wk["w"] == 1 else "#888",
    "head_bg": "#EEECFF" if wk["w"] == 1 else "#F8F9FA",
} for wk in weeks]

cells = {"walk": [], "staff": [], "total": []}
for i, wk in enumerate(weeks):
    cur = wk["w"] == 1
    for col in ("walk", "staff", "total"):
        prev = weeks[i - 1][col] if i > 0 else 0
        if prev == 0:
            pct, color = "", "#888"
        else:
            p = round((wk[col] - prev) / prev * 100, 1)
            pct = f"{'▲' if p >= 0 else '▼'}{'+' if p >= 0 else ''}{p}%"
            color = "#27AE60" if p >= 0 else "#E74C3C"
        cells[col].append({
            "val": fmt(wk[col]), "pct": pct, "color": color,
            "weight": "700" if cur else "400",
            "bg": "#EEECFF" if cur else "#FFFFFF",
        })
walk_cells, staff_cells, total_cells = cells["walk"], cells["staff"], cells["total"]

# ── promotion trend by week: same 5 buckets, rows = Staff 10% / +฿50 Drink Set ──
staff10_d = {d: max(0, round(random.gauss(16, 4))) for d in D35}
set50_d = {d: max(0, round(random.gauss(30, 6))) for d in D35}

def weekly_cells(series):
    totals = [sum(series.get(d, 0) for d in wk["days"]) for wk in weeks]
    out = []
    for i, v in enumerate(totals):
        cur = weeks[i]["w"] == 1
        prev = totals[i - 1] if i > 0 else 0
        if prev == 0:
            pct, color = "", "#888"
        else:
            p = round((v - prev) / prev * 100, 1)
            pct = f"{'▲' if p >= 0 else '▼'}{'+' if p >= 0 else ''}{p}%"
            color = "#27AE60" if p >= 0 else "#E74C3C"
        out.append({"val": fmt(v), "pct": pct, "color": color,
                    "weight": "700" if cur else "400",
                    "bg": "#EEECFF" if cur else "#FFFFFF"})
    return out

staff10_cells, set50_cells = weekly_cells(staff10_d), weekly_cells(set50_d)

# ── 7-day heatmap (+ WoW vs same weekday last week) ──
last7 = D14[7:]
rows = [{"d": d, "rev": sales[d], "bills": bills[d],
         "ticket": round(sales[d] / bills[d])} for d in last7]
heatmap_rows = []
for m in ("rev", "bills", "ticket"):
    lo = min(r[m] for r in rows); hi = max(r[m] for r in rows)
    for r in rows:
        t = 0.5 if hi == lo else (r[m] - lo) / (hi - lo)
        r[m + "_bg"] = lerp_hex("#FBF3EA", "#C9C7FF", t)
        r[m + "_weight"] = "700" if r[m] == hi else "400"
for r in rows:
    prev = sales.get(r["d"] - datetime.timedelta(days=7))
    if not prev:
        wow, wc, ww = "—", "#888", "400"
    else:
        pct = round((r["rev"] - prev) / prev * 100, 1)
        wow = f"{'+' if pct >= 0 else ''}{pct}%"
        wc = "#27AE60" if pct >= 0 else "#E74C3C"
        ww = "700" if abs(pct) >= 10 else "400"
    heatmap_rows.append({
        "day_label_th": th_label(r["d"]),
        "day_weight": "700" if r["d"] == REPORT_DATE else "400",
        "rev": fmt(r["rev"]), "rev_fg": "#2C3E50",
        "rev_bg": r["rev_bg"], "rev_weight": r["rev_weight"],
        "bills": str(r["bills"]), "bills_fg": "#2C3E50",
        "bills_bg": r["bills_bg"], "bills_weight": r["bills_weight"],
        "ticket": fmt(r["ticket"]), "ticket_fg": "#2C3E50",
        "ticket_bg": r["ticket_bg"], "ticket_weight": r["ticket_weight"],
        "wow_pct": wow, "wow_color": wc, "wow_weight": ww,
    })

# ── top 10 tables ──
def badge(qty, avg5d):
    if avg5d is None:
        return "#D1ECF1", "#0C5460", "New"
    pct = round((qty - avg5d) / avg5d * 100)
    label = f"{'+' if pct >= 0 else ''}{pct}%"
    if pct >= 15: return "#D4EDDA", "#155724", label
    if pct <= -10: return "#F8D7DA", "#721C24", label
    return "#FEF3CD", "#856404", label

qty_y = {}
for i, (code, name, fc, rice) in enumerate(MENU):
    base = 38 - i * 2.5 if rice else 18 - (i - 12) * 3
    qty_y[code] = max(2, round(base + random.gauss(0, 4)))
avg5 = {c: max(2, round(q * random.uniform(0.8, 1.2))) for c, q in qty_y.items()}
avg5[MENU[10][0]] = None  # one "New" item for variety

ranked = sorted(MENU, key=lambda m: qty_y[m[0]], reverse=True)
top10_all, top10_rice = [], []
for rank, (code, name, fc, rice) in enumerate(ranked[:10], 1):
    bg, fg, lbl = badge(qty_y[code], avg5[code])
    top10_all.append({"rank": rank, "itemid": code,
        "name": ("⭐ " if rice else "") + name, "qty": qty_y[code],
        "avg5d": avg5[code] if avg5[code] is not None else "—",
        "badge_bg": bg, "badge_fg": fg, "badge_label": lbl,
        "row_bg": "#FFFFFF" if rank % 2 else "#FAFAFA"})
for rank, (code, name, fc, rice) in enumerate(
        [m for m in ranked if m[3]][:10], 1):
    bg, fg, lbl = badge(qty_y[code], avg5[code])
    top10_rice.append({"rank": rank, "itemid": code, "name": name,
        "qty": qty_y[code],
        "avg5d": avg5[code] if avg5[code] is not None else "—",
        "fc_pct": f"{fc}%" if fc else "—",
        "badge_bg": bg, "badge_fg": fg, "badge_label": lbl,
        "row_bg": "#FFFFFF" if rank % 2 else "#FAFAFA"})

# ── hourly comparison 07:00–21:00, with one anomaly hour ──
HOURS = list(range(7, 22))
shape = {7:.03,8:.05,9:.06,10:.07,11:.10,12:.13,13:.11,14:.07,15:.06,
         16:.06,17:.07,18:.09,19:.06,20:.03,21:.01}
anomaly_hour = 14
hourly_rows, anomaly_count = [], 0
rice_names = [m for m in MENU if m[3]]
for i, h in enumerate(HOURS):
    prev_rev = round(sales[PREV_DATE] * shape[h] * random.uniform(.85, 1.15))
    cur_rev = round(rep_sales * shape[h] * random.uniform(.85, 1.15))
    if h == anomaly_hour:
        cur_rev = round(cur_rev * 0.35)
    bench = round(avg_5d * shape[h])
    pct = round((cur_rev - prev_rev) / prev_rev * 100, 1) if prev_rev else 0
    is_anom = cur_rev < bench * 0.5
    if is_anom: anomaly_count += 1
    picks = random.sample(rice_names, 3)
    qs = sorted([random.randint(2, 14) for _ in range(3)], reverse=True)
    top3 = "<br>".join(f"{(n[1][:22] + '…') if len(n[1]) > 22 else n[1]} ×{q}"
                       for n, q in zip(picks, qs))
    hourly_rows.append({
        "hour": f"{h:02d}:00", "hour_flag": " 🚨" if is_anom else "",
        "hour_color": "#C62828" if is_anom else "#2C3E50",
        "row_bg": "#FFEBEE" if is_anom else ("#FFFFFF" if i % 2 else "#FAFAFA"),
        "prev_rev": fmt(prev_rev), "prev_color": "#555",
        "cur_rev": fmt(cur_rev),
        "cur_color": "#C62828" if is_anom else "#555",
        "change_pct": f"{'+' if pct >= 0 else ''}{pct}%",
        "change_color": "#27AE60" if pct >= 0 else "#E74C3C",
        "change_weight": "700" if abs(pct) >= 25 else "400",
        "bench": fmt(bench), "top3": top3,
    })

# ── assemble ──
data = {
    "scalars": {
        "report_date_display": f"{REPORT_DATE.day} {EN_MONTHS[REPORT_DATE.month-1]} {REPORT_DATE.year}",
        "report_day_en": REPORT_DATE.strftime("%A"),
        "report_date_short": f"{REPORT_DATE.day} {TH_MONTHS[REPORT_DATE.month-1]}",
        "prev_date_short": f"{PREV_DATE.day} {TH_MONTHS[PREV_DATE.month-1]}",
        "d30_start": f"{D30[0].day} {TH_MONTHS[D30[0].month-1]}",
        "mtd_month": f"{EN_MONTHS[REPORT_DATE.month-1]} {REPORT_DATE.year}",
        "generated_date": f"{today.day} {EN_MONTHS[today.month-1]} {today.year} (SAMPLE)",
        "net_sales": fmt(rep_sales), "signed_pct": f"{'+' if signed_pct >= 0 else ''}{signed_pct}",
        "target_icon": "🔥" if rep_sales >= 50000 else ("✅" if rep_sales >= TARGET else "⚠️"),
        "avg_5d": fmt(avg_5d),
        "total_bills": rep_bills, "avg_bills": avg_bills_5d,
        "bills_arrow": "↑" if rep_bills >= avg_bills_5d else "↓",
        "walk_in_bills": walk_in_bills, "walk_in_revenue": fmt(walk_in_rev),
        "walk_in_pct": round(walk_in_bills / rep_bills * 100, 1),
        "staff_bills": staff_bills, "staff_revenue": fmt(staff_rev),
        "staff_pct": round(staff_bills / rep_bills * 100, 1),
        "avg_ticket": avg_ticket, "avg_ticket_bench": avg_ticket_bench,
        "ticket_arrow": "↑" if avg_ticket >= avg_ticket_bench else "↓",
        "net_30d": fmt(net_30d), "avg_30d": fmt(avg_30d),
        "net_mtd": fmt(net_mtd), "avg_mtd": fmt(avg_mtd),
        "mtd_days": mtd_days,
        "mtd_signed_pct": f"{'+' if mtd_signed >= 0 else ''}{mtd_signed}",
        "mtd_line_px": mtd_line_px,
        "avg_bills_30d": avg_bills_30d,
        "anomaly_count": anomaly_count,
        "staff10_bills": 18, "staff10_status": "ACTIVE",
        "staff10_badge_bg": "#D4EDDA", "staff10_badge_fg": "#155724",
        "set50_bills": 31, "set50_status": "ACTIVE",
        "set50_badge_bg": "#D4EDDA", "set50_badge_fg": "#155724",
        "chaw_values": "ซื่อสัตย์ · ขยัน · ประหยัด · อดทน · กตัญญู",
    },
    "repeats": {
        "chart_days": chart_days, "chart_labels": chart_labels,
        "week_headers": week_headers, "walk_cells": walk_cells,
        "staff_cells": staff_cells, "total_cells": total_cells,
        "staff10_cells": staff10_cells, "set50_cells": set50_cells,
        "heatmap_rows": heatmap_rows,
        "top10_all": top10_all, "top10_rice": top10_rice,
        "hourly_rows": hourly_rows,
    },
    "sections": {"alert_banner": anomaly_count > 0, "promo": True},
}
print(json.dumps(data, ensure_ascii=False, indent=1))
