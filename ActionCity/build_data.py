#!/usr/bin/env python3
"""Build data.json for ActionCity daily report — 2026-06-28 (EOD)."""
import json, math

def fmt_k(v, decimals=0):
    """Format number with commas."""
    if decimals == 0:
        return f"{int(round(float(v))):,}"
    return f"{float(v):,.{decimals}f}"

def pct_arrow(pct_float):
    if pct_float > 0: return "▲", "#1f9d57"
    if pct_float < 0: return "▼", "#d6453a"
    return "—", "#8a8a93"

def gp_color(gp_pct):
    try:
        return "#1f7a55" if float(gp_pct) >= 50 else "#c43b27"
    except: return "#8a8a93"

def stock_color(stock, avg_weekly_vel):
    """Red if stock < 1 week cover."""
    try:
        if float(stock) < avg_weekly_vel: return "#c43b27"
        return "#2b2b33"
    except: return "#2b2b33"

# === SCALARS ===
scalars = {
    "report_date_display": "28 Jun 2026",
    "report_weekday": "Sun · EOD",
    "iso_week": "26",
    "w_minus1": "25",
    "w_minus2": "24",
    "w_minus3": "23",
    "w_minus4": "22",
    "mode_badge": "SCHEDULED",
    "mode_badge_color": "#5551FE",

    # Today KPIs (Query A, retail only, Jun 28)
    # retail_net=64,699.90, bills=108, units=195; last week retail=59,342.94
    "day_net": "64,700",
    "day_wow_pct": "+9.0%",
    "day_wow_arrow": "&#9650;",
    "day_wow_color": "#1f9d57",
    "day_bills": "108",
    "day_bills_split": "108 retail bills &middot; 195 units",
    "day_ticket": "599",

    # WTD (W26 complete, Jun 22-28)
    "wtd_net": "527,149",
    "wtd_days": "7",
    "wtd_per_day": "75,307",

    # Best sellers today (≥5 units, retail)
    "best_today_list": (
        "Happy Balloon Dog 2 (25u &middot; &#3647;3,505) &bull; "
        "Opandee Zombie Party S4 (18u &middot; &#3647;8,243) &bull; "
        "Heyone Baobao (13u &middot; &#3647;3,402) &bull; "
        "Upset Duck Status Display (11u &middot; &#3647;2,046) &bull; "
        "Disney Princess Pony (7u &middot; &#3647;2,944) &bull; "
        "Cat Hug KC (6u &middot; &#3647;2,785) &bull; "
        "Snoopy Fun Button (6u &middot; &#3647;2,168) &bull; "
        "Mr. Bone SA Mini 3.0 (5u &middot; &#3647;2,103)"
    ),

    # Notes (analytical)
    "today_branch_note": (
        "Sunday EOD &mdash; 4 stores posted sales. "
        "<b>Siam Square One &#3647;35,692 / 49 bills</b> (avg ticket &#3647;728) led the day. "
        "Fashion Island &#3647;16,039, Central Ladprao &#3647;9,735, Warehouse HQ &#3647;3,234. "
        "Vending machines, Westgate, and E-Com: no posts today."
    ),
    "week_note": (
        "W26 headline &#3647;527K is <b>inflated by a &#3647;214K Siam Specialty wholesale order</b> "
        "(3 orders &bull; 463u &bull; 39 SKUs). Retail-only W26 = &#3647;273,505 &mdash; "
        "<b>down 13.6% vs W25 retail (&#3647;316,515)</b>. "
        "Underlying retail run-rate ~&#3647;270&ndash;320K/week after the W21 promo peak (&#3647;755K)."
    ),
    "branch_note": (
        "Last 3 complete weeks (net &#3647;, W24/W25/W26). "
        "<b>Warehouse HQ W26 spike = Siam Specialty wholesale (&#3647;214K)</b> &mdash; retail HQ ~&#3647;25K. "
        "<b>Siam Square One declining</b> (&#3647;185K &rarr; &#3647;190K &rarr; &#3647;158K). "
        "<b>Fashion Island declining</b> 3 weeks (&#3647;99K &rarr; &#3647;78K &rarr; &#3647;72K). "
        "Central Ladprao recovering (&#3647;44K &rarr; &#3647;37K &rarr; &#3647;42K). "
        "Westgate &bull; E-Com &bull; ACT HQ: all DARK."
    ),
    "cat_note": (
        "Collectables (100/200/400%) = <b>12.3% revenue</b> from 70 units &amp; 28 SKUs "
        "(ASP &#3647;3,115). <b>GP 35.4% &mdash; below threshold</b>; check premium figure pricing. "
        "Standard blind box / plush / KC = 87.7% at 47.5% GP."
    ),
    "reorder_note": (
        "<b>Grogu Chubby Planet nearly out</b> (5u, cover 0.3w) &mdash; urgent reorder. "
        "Fuggler HCB Monster (32u, 1.2w), Disney Princess On The Run (20u, 1.4w), "
        "Disney Princess Pony (28u, 1.6w) &mdash; all below 2-week cover, reorder. "
        "Sanrio Sweet Style &amp; Little World Squishy at WATCH (cover 2.8&ndash;2.9w)."
    ),

    # Top 20 labels (W25 + W26)
    "top_w1_label": "W25",
    "top_w0_label": "W26",
    "top_note": (
        "<b>Retail only &mdash; wholesale excluded.</b> "
        "Wholesale this period (W25+W26): <b>Siam Specialty &#3647;213,876 / 463u / 39 SKUs (3 orders)</b> "
        "&mdash; shown here, not in the ranking."
    ),

    # PO note
    "po_note": (
        "Approved POs only. "
        "<b>Bearbrick S44/S49 consignment open (96u each)</b> on POACT250800059 &mdash; coordinate return. "
        "Large MNT batch POACT250700030 (~&#3647;199K) and Toysinbox interco POACT250600020 pending delivery."
    ),

    # Dead stock
    "dead_owned_skus": "21",
    "dead_owned_value": "107K",
    "dead_note": (
        "MNT consignment (50 SKUs, 3,766u) &amp; Big Box Bearbrick/Astro Boy (43 SKUs, 146u) "
        "&mdash; coordinate returns. "
        "Toysinbox interco (346 SKUs, 3,831u, &#3647;4.25M) &mdash; review/renegotiate. "
        "Owned dead (21 SKUs, &#3647;107K) &mdash; clear/discount immediately."
    ),

    # Footer
    "generated_at": "28 Jun 2026, 22:00 (EOD)",
    "footer_cchaw": "CHAW Retailing Co., Ltd. &middot; Internal management report &middot; Scheduled EOD (2026-06-28).",

    # Branch table column labels
    "br_w2_label": "W24",
    "br_w1_label": "W25",
    "br_w0_label": "W26",
}

# === SECTIONS ===
sections = {
    "exec_insight": True,
    "best_today": True,
}

# === REPEATS ===
repeats = {}

# --- today_branch_rows (Query A2, Jun 28) ---
# loc 172 HQ: net=3233.64, bills=8, retail_net=3233.64, retail_bills=8
# loc 174 FI: net=16039.24, bills=30, retail_net=16039.24, retail_bills=30
# loc 176 SSO: net=35691.53, bills=49, retail_net=35691.53, retail_bills=49
# loc 198 CLP: net=9735.49, bills=21, retail_net=9735.49, retail_bills=21
branches_today = [
    {"name": "Siam Square One",        "net": 35691.53, "bills": 49, "retail_net": 35691.53, "retail_bills": 49},
    {"name": "Fashion Island",          "net": 16039.24, "bills": 30, "retail_net": 16039.24, "retail_bills": 30},
    {"name": "Central Ladprao",         "net": 9735.49,  "bills": 21, "retail_net": 9735.49,  "retail_bills": 21},
    {"name": "Warehouse HQ (Liberty)", "net": 3233.64,  "bills": 8,  "retail_net": 3233.64,  "retail_bills": 8},
]
today_branch_rows = []
for b in branches_today:
    ticket = b["retail_net"] / b["retail_bills"] if b["retail_bills"] > 0 else 0
    today_branch_rows.append({
        "tb_bg": "#ffffff",
        "tb_color": "#2b2b33",
        "tb_name": b["name"],
        "tb_net": fmt_k(b["net"]),
        "tb_bills": str(b["bills"]),
        "tb_ticket": fmt_k(ticket),
        "tb_flag": "",
    })
repeats["today_branch_rows"] = today_branch_rows

# --- insight_rows ---
repeats["insight_rows"] = [
    {"insight": "<b>W26 headline &#3647;527K driven by &#3647;214K Siam Specialty wholesale</b> (3 orders, 463u, 39 SKUs). Retail-only W26 = &#3647;273,505 &mdash; down 13.6% vs W25 retail (&#3647;316,515)."},
    {"insight": "<b>Fashion Island declining 3 straight weeks</b> (&#3647;99K &rarr; &#3647;78K &rarr; &#3647;72K) &mdash; investigate. Siam Square One also softer in W26 (&#3647;185K &rarr; &#3647;190K &rarr; &#3647;158K)."},
    {"insight": "Collectable GP at <b>35.4%</b> &mdash; below target (&ge;45%). Premium figure pricing likely needs review; ASP &#3647;3,115 vs cost structure."},
    {"insight": "<b>Reorder urgent:</b> Grogu Chubby Planet 5u left (0.3-week cover); Fuggler HCB Monster, Disney Princess On Run &amp; Pony all below 2-week cover."},
    {"insight": "<b>Dead stock:</b> 21 owned SKUs (&#3647;107K) + MNT 50 SKUs (3,766u consign) + Big Box 43 SKUs (146u consign) &mdash; coordinate returns. Toysinbox 346 SKUs (3,831u, &#3647;4.25M) &mdash; review."},
    {"insight": "Lollipoppi Bag Charm (W24 launch) accelerating: W25=6u &rarr; W26=29u, 123u on hand. Happy Balloon Dog 2 had a strong Sunday: 25u / &#3647;3,505 today alone."},
]

# --- week_rows (Query B, W20-W26) ---
weeks_data = [
    ("2026-20", "W20", 362936.34, 976),
    ("2026-21", "W21", 755367.43, 2317),
    ("2026-22", "W22", 356865.99, 1444),
    ("2026-23", "W23", 382577.81, 1014),
    ("2026-24", "W24", 439692.77, 1247),
    ("2026-25", "W25", 355410.28, 844),
    ("2026-26", "W26 (WTD)", 527149.28, 1365),
]
max_net = max(w[2] for w in weeks_data)
week_rows = []
for i, (wk_id, label, net, units) in enumerate(weeks_data):
    is_current = "WTD" in label
    is_max = (net == max_net)
    bar_pct = max(1, int(round(net / max_net * 100)))
    bar_color = "#F27061" if is_current else ("#5551FE" if is_max else "#C9C7FF")
    label_color = "#2b2b33" if (is_current or i == len(weeks_data)-2) else "#8a8a93"
    weight = "600" if (is_current or is_max) else "500"
    val_color = "#F27061" if is_current else ("#5551FE" if is_max else "#2b2b33")
    week_rows.append({
        "wk_label": label,
        "wk_label_color": label_color,
        "wk_weight": weight,
        "wk_bar_color": bar_color,
        "wk_bar_pct": str(bar_pct),
        "wk_val_color": val_color,
        "wk_net": fmt_k(net),
    })
repeats["week_rows"] = week_rows

# --- bu_rows (Query C) ---
# class 8=Retails, 10=Vending, 12=Wholesale, 126=Shopee
bu_raw = [
    ("Retails",   "#5551FE", 316515.09, 273504.71),
    ("Wholesale", "#F27061", 0,          213875.51),
    ("Shopee",    "#1f9d57", 15046.73,  23104.64),
    ("Vending",   "#b5740a", 23848.46,  16664.42),
]
total_wtd = sum(r[3] for r in bu_raw)
max_wtd = max(r[3] for r in bu_raw)
bu_rows = []
for name, bar_color, prev, wtd in bu_raw:
    share = round(wtd / total_wtd * 100, 1)
    bar_pct = max(1, int(round(wtd / max_wtd * 100)))
    if prev > 0:
        wow_pct = (wtd - prev) / prev * 100
        arrow, wow_color = pct_arrow(wow_pct)
        wow_str = f"{arrow}{abs(round(wow_pct)):d}%"
    else:
        wow_str = "new"
        wow_color = "#8a8a93"
    bu_rows.append({
        "bu_name": name,
        "bu_bar_color": bar_color,
        "bu_bar_pct": str(bar_pct),
        "bu_net": fmt_k(wtd),
        "bu_share": str(share),
        "bu_wow_color": wow_color,
        "bu_wow": wow_str,
    })
repeats["bu_rows"] = bu_rows

# --- branch_rows (Query D, W24/W25/W26 trend) ---
# loc: (name, w2=W24, w1=W25, w0=W26, flag)
branch_data = [
    (172, "Warehouse HQ (Liberty)", 90762.22,  26122.43,  239223.15, "wholesale"),
    (176, "Siam Square One",         185249.47, 189879.74, 157579.64, "store"),
    (174, "Fashion Island",           99027.04,  78218.60,  71511.11,  "store"),
    (198, "Central Ladprao",          43566.28,  37341.05,  42170.96,  "store"),
    (210, "IconSiam 6F &#9881;",      9296.23,   12282.18,  8583.14,   "vending"),
    (196, "Bangkapi 1 &#9881;",       5485.03,   3392.50,   4357.00,   "vending"),
    (197, "Bangkapi 2 &#9881;",       4794.36,   3579.42,   2401.86,   "vending"),
    (194, "Rama 9 &#9881;",           1512.14,   4594.36,   1322.42,   "vending"),
    (235, "ACT Westgate",             0,          0,          0,         "dark"),
    (177, "E-Commerce",               0,          0,          0,         "dark"),
    (347, "ActionCityHQ &#9881;",     0,          0,          0,         "dark"),
]
branch_rows = []
for loc, name, w2, w1, w0, flag in branch_data:
    if flag == "dark":
        row_bg = "#fde7e4"
        name_color = "#b3261e"
        w0_color = "#b3261e"
        trend = "&mdash;"
        trend_color = "#b3261e"
        flag_html = '<span style="background:#d6453a;color:#fff;font-size:9px;font-weight:600;padding:1px 6px;border-radius:9px;">DARK</span>'
        branch_rows.append({
            "br_row_bg": row_bg,
            "br_name_color": name_color,
            "br_name": name,
            "br_w2": "&mdash;",
            "br_w1": "&mdash;",
            "br_w0": "&mdash;",
            "br_w0_color": w0_color,
            "br_trend": trend,
            "br_trend_color": trend_color,
            "br_flag": flag_html,
        })
        continue

    # Color for w0 vs w1
    if flag == "wholesale":
        row_bg = "#fff8ec"
        w0_color = "#8a8a93"
        trend = "&#9650;*"
        trend_color = "#8a8a93"
        flag_html = '<span style="background:#fbeecd;color:#b5740a;font-size:9px;font-weight:600;padding:1px 6px;border-radius:9px;">WHOLESALE</span>'
    elif w0 >= w1:
        row_bg = "#ffffff"
        w0_color = "#1f7a55"
        trend = "&#9650;"
        trend_color = "#1f9d57"
        flag_html = flag
    else:
        row_bg = "#ffffff"
        w0_color = "#c43b27"
        trend = "&#9660;"
        trend_color = "#d6453a"
        flag_html = flag

    name_color = "#6a665e" if flag == "vending" else "#2b2b33"

    branch_rows.append({
        "br_row_bg": row_bg,
        "br_name_color": name_color,
        "br_name": name,
        "br_w2": fmt_k(w2),
        "br_w1": fmt_k(w1),
        "br_w0": fmt_k(w0),
        "br_w0_color": w0_color,
        "br_trend": trend,
        "br_trend_color": trend_color,
        "br_flag": flag_html,
    })
repeats["branch_rows"] = branch_rows

# --- cat_rows (Query E, trailing 4-wk from May 31) ---
# Collectable: 28 SKUs, 70u, ฿218,036, ASP=3115, GP=35.4%
# Rest: 225 SKUs, 4584u, ฿1,550,009, ASP=338, GP=47.5%
cat_total_net = 218036.44 + 1550008.55
cat_rows = [
    {
        "cat_name": "Collectables (100/200/300/400%)",
        "cat_skus": "28",
        "cat_units": "70",
        "cat_net": fmt_k(218036.44),
        "cat_share": str(round(218036.44/cat_total_net*100, 1)),
        "cat_asp": "3,115",
        "cat_gp_color": "#c43b27",
        "cat_gp": "35.4",
    },
    {
        "cat_name": "The rest (blind box / plush / KC)",
        "cat_skus": "225",
        "cat_units": "4,584",
        "cat_net": fmt_k(1550008.55),
        "cat_share": str(round(1550008.55/cat_total_net*100, 1)),
        "cat_asp": "338",
        "cat_gp_color": "#c43b27",
        "cat_gp": "47.5",
    },
]
repeats["cat_rows"] = cat_rows

# --- reorder_rows (Query F, retail velocity) ---
# Sorted by urgency (cover ascending)
# Labels: w4=W21, w3=W22, w2=W23, w1=W24, w0_prev=W25, w0=W26
reorder_data = [
    # name,         w4, w3,  w2,  w1, w0_prev, w0, stock, cover
    ("Naruto Kittenland Plush Keychain Blind Box",       0,   0,   0,  18,   2,   0,   0,  0.0),
    ("Grogu Chubby Planet Series Plush Keychain Blind Box", 0, 0, 16, 37,  14,   0,   5,  0.3),
    ("Fuggler Heart Care Bear Monster Plush Keychain Blind Box", 24, 29, 34, 20, 21, 19, 32, 1.2),
    ("Disney Princess On The Run Plush Keychain Blind Box",     41, 30,  7,  8,  12,  5,  20, 1.4),
    ("Disney Princess Pony Plush Keychain Blind Box",           17, 26, 20, 20,   6, 18,  28, 1.6),
    ("Little World Sweet Conguests Stressrelief Squishy Blind Box", 5, 2, 0, 8, 14,  0,  17, 2.8),
    ("Sanrio Characters Sweet Style Phone Chain Mini Blind Box",    0,  0,  6, 27,  10, 10,  31, 2.9),
]

def cover_to_action(cover, stock):
    if stock == 0: return "SOLD OUT", "#fde3df", "#c43b27"
    if cover < 0.7: return "REORDER&#8593;", "#e3f5ec", "#1f9d57"
    if cover < 2.0: return "REORDER", "#e3f5ec", "#1f9d57"
    if cover < 2.5: return "SMALL BUY", "#fbeecd", "#b5740a"
    return "WATCH", "#fbeecd", "#b5740a"

reorder_rows = []
for name, w4, w3, w2, w1, w0p, w0, stock, cover in reorder_data:
    action, act_bg, act_color = cover_to_action(cover, stock)
    s_color = "#c43b27" if stock < 15 else "#2b2b33"
    cover_str = f"{cover}w" if stock > 0 else "n/a"
    reorder_rows.append({
        "ro_name": name,
        "ro_w4": str(w4) if w4 > 0 else "&mdash;",
        "ro_w3": str(w3) if w3 > 0 else "&mdash;",
        "ro_w2": str(w2) if w2 > 0 else "&mdash;",
        "ro_w1": str(w1) if w1 > 0 else "&mdash;",
        "ro_w0": str(w0) if w0 > 0 else "&mdash;",
        "ro_stock_color": s_color,
        "ro_stock": str(stock) if stock > 0 else "0",
        "ro_cover": cover_str,
        "ro_act_bg": act_bg,
        "ro_act_color": act_color,
        "ro_action": action,
    })
repeats["reorder_rows"] = reorder_rows

# --- top_rows (Query G, top 20 by u2, W25+W26 retail) ---
top_20 = [
    ("Upset Duck Status Display Duck Hipper Blind Box",    143,  64,  79, 175,  26747, 14218, 53.2),
    ("Fuggler Alley Cat Plush Keychain Blind Box",          78,  46,  32,  98,  30574, 15610, 51.1),
    ("Upset Duck Mini Wishlist Plush Keychain Blind Box",   68,  41,  27, 183,  24321, 12684, 52.2),
    ("Upset Duck Stop The Spiral Duck Blind Box",           63,  33,  30, 423,  11717,  6194, 52.9),
    ("Opandee Zombie Party Series 4 Figures Blind Box",     60,  33,  27, 526,  27477, 13231, 48.2),
    ("Mr. Bone Agent Plush Keychain Blind Box",             49,  24,  25, 269,  26421, 12158, 46.0),
    ("Fuggler Sassy Cuties Squad Plush Keychain Blind Box", 42,  31,  11, 134,  17600,  9676, 55.0),
    ("Fuggler Heart Care Bear Monster Plush Keychain Blind Box", 40, 21, 19, 32, 16315, 7683, 47.1),
    ("Lollipoppi Bag Charm Plush Keychain Blind Box",       35,   6,  29, 123,  19626, 10050, 51.2),
    ("Cat Hug Plush Keychain Blind Box",                    33,  11,  22, 258,  14897,  8229, 55.2),
    ("Happy Balloon Dog 2 Figure Blind Box",                32,   5,  27, 161,   4486,  3137, 69.9),
    ("Upset Duck Pocket Crazy Circus Duck Plush KC BB",     30,  17,  13, 136,  11776,  4863, 41.3),
    ("Qmsv Strike & Destiny Gundam Figure Blind Box",       28,  17,  11,  55,  12654,  5460, 43.1),
    ("A Day In The Life Of A Bikini Bottom Resident KC BB", 25,   8,  17,  83,   9794,  4655, 47.5),
    ("Bearbrick Series 51 Figure Blind Box",                25,   8,  17, 488,   4650,  2545, 54.7),
    ("Disney Princess Pony Plush Keychain Blind Box",       24,   6,  18,  28,  10280,  4807, 46.8),
    ("Mr. Bone Strange Alliance Mini 3.0 Figure Blind Box", 22,  10,  12, 395,   9505,  4401, 46.3),
    ("Heyone Baobao Baobao's Seasons Sweet House",          22,   1,  21,  14,   5757,  1137, 19.7),
    ("Bearbrick Series 50 Figure Blind Box",                21,  12,   9, 907,   3906,  2074, 53.1),
    ("Upset Duck X Care Bears Be Rainbow Duck KC BB",       21,  13,   8,  96,  11383,  5437, 47.8),
]

top_rows = []
for name, u2, uw1, uw0, stock, net, gp, gp_pct in top_20:
    avg_vel = u2 / 2.0  # 2-week average weekly
    s_color = "#c43b27" if stock < avg_vel else "#2b2b33"
    w0_color = "#1f7a55" if uw0 >= uw1 else "#2b2b33"
    g_color = gp_color(gp_pct)
    top_rows.append({
        "tp_name": name,
        "tp_stock_color": s_color,
        "tp_stock": fmt_k(stock),
        "tp_w1": str(uw1),
        "tp_w0_color": w0_color,
        "tp_w0": str(uw0),
        "tp_2wk": str(u2),
        "tp_day": str(round(u2/14.0, 1)),
        "tp_net": fmt_k(net),
        "tp_gp": fmt_k(gp),
        "tp_gp_color": g_color,
        "tp_gp_pct": str(gp_pct),
    })
repeats["top_rows"] = top_rows

# --- arrival_rows (Query H, 2026W20-W26 launches with stock) ---
arrival_rows = [
    {
        "na_wk": "W26",
        "na_name": "Shiba Macarons Squishy Blind Box",
        "na_recvd": "24",
        "na_sold": "0",
        "na_oh_color": "#2b2b33",
        "na_onhand": "24",
        "na_read_bg": "#eeedfe",
        "na_read_color": "#5551FE",
        "na_read": "JUST IN",
    },
    {
        "na_wk": "W24",
        "na_name": "Lollipoppi Bag Charm Plush Keychain Blind Box",
        "na_recvd": "&mdash;",
        "na_sold": "35+",
        "na_oh_color": "#2b2b33",
        "na_onhand": "123",
        "na_read_bg": "#e3f5ec",
        "na_read_color": "#1f9d57",
        "na_read": "HOT&#8593;",
    },
    {
        "na_wk": "W21",
        "na_name": "Fuggler Sassy Cuties Squad Plush Keychain Blind Box",
        "na_recvd": "&mdash;",
        "na_sold": "42+",
        "na_oh_color": "#2b2b33",
        "na_onhand": "134",
        "na_read_bg": "#e3f5ec",
        "na_read_color": "#1f9d57",
        "na_read": "SELLING",
    },
    {
        "na_wk": "W20",
        "na_name": "Grogu Chubby Planet Series Plush Keychain Blind Box",
        "na_recvd": "~72",
        "na_sold": "67+",
        "na_oh_color": "#c43b27",
        "na_onhand": "5",
        "na_read_bg": "#e3f5ec",
        "na_read_color": "#1f9d57",
        "na_read": "HOT",
    },
    {
        "na_wk": "W21",
        "na_name": "Sanrio Family &amp; Friends Series Plush Blind Box",
        "na_recvd": "&mdash;",
        "na_sold": "5",
        "na_oh_color": "#b5740a",
        "na_onhand": "91",
        "na_read_bg": "#fbeecd",
        "na_read_color": "#b5740a",
        "na_read": "SLOW",
    },
]
repeats["arrival_rows"] = arrival_rows

# --- po_rows (selected from Query I) ---
# Key approved POs sorted by importance
po_rows = [
    {
        "po_row_bg": "#fdeeec",
        "po_name": "Bearbrick Series 44 &amp; 49 Figure Blind Box",
        "po_num": "POACT250800059",
        "po_qty": "192 (96u each)",
        "po_value": "consignment",
        "po_flag_bg": "#fde3df",
        "po_flag_color": "#c43b27",
        "po_flag": "OLD &middot; CONSIGN",
    },
    {
        "po_row_bg": "#fff8ec",
        "po_name": "MNT Series Batch (Bob / Heyone / Kimmon / Ziyuli / Repolar &hellip;)",
        "po_num": "POACT250700030",
        "po_qty": "~555 units",
        "po_value": "&#3647;198,825",
        "po_flag_bg": "#fbeecd",
        "po_flag_color": "#b5740a",
        "po_flag": "PENDING",
    },
    {
        "po_row_bg": "#ffffff",
        "po_name": "Toysinbox Multi-SKU (Lulupie / Dolores / Diesel&times;Dolores / Momo &hellip;)",
        "po_num": "POACT250600020",
        "po_qty": "600+ units",
        "po_value": "&#3647;426,000+",
        "po_flag_bg": "#eeedfe",
        "po_flag_color": "#5551FE",
        "po_flag": "INTERCO",
    },
    {
        "po_row_bg": "#ffffff",
        "po_name": "Evangelion Vol.1 Figure Blind Box",
        "po_num": "POACT250800030",
        "po_qty": "72",
        "po_value": "&#3647;18,632",
        "po_flag_bg": "#e3f5ec",
        "po_flag_color": "#1f9d57",
        "po_flag": "NEW",
    },
    {
        "po_row_bg": "#ffffff",
        "po_name": "Bearbrick Series 50 Figure Blind Box",
        "po_num": "POACT250700031",
        "po_qty": "10",
        "po_value": "&#3647;18,393",
        "po_flag_bg": "#e3f5ec",
        "po_flag_color": "#1f9d57",
        "po_flag": "OK",
    },
]
repeats["po_rows"] = po_rows

# --- dead_owned_rows ---
dead_owned_rows = [
    {"do_name": "Liiaocao Mini Blessing Golden Plush KC (Thailand Ed.)", "do_onhand": "76", "do_cost": "293", "do_price": "&mdash;", "do_value": "22,253"},
    {"do_name": "Hitohatausagi (HAM000018)", "do_onhand": "1", "do_cost": "20,828", "do_price": "&mdash;", "do_value": "20,828"},
    {"do_name": "Poyunwang Caishen Flower Thrower 200%", "do_onhand": "5", "do_cost": "2,990", "do_price": "&mdash;", "do_value": "14,951"},
    {"do_name": "Poh Bear Jiangshi Ver", "do_onhand": "2", "do_cost": "4,635", "do_price": "&mdash;", "do_value": "9,269"},
    {"do_name": "Jpx Nong Toy (HAM000015)", "do_onhand": "1", "do_cost": "6,820", "do_price": "&mdash;", "do_value": "6,820"},
    {"do_name": "Shiba Macarons Squishy Blind Box (W26 &mdash; zero sales)", "do_onhand": "24", "do_cost": "159", "do_price": "&mdash;", "do_value": "3,819"},
    {"do_name": "Ozai First Floating Bottle Mini Plush Blind Box", "do_onhand": "12", "do_cost": "204", "do_price": "&mdash;", "do_value": "2,444"},
    {"do_name": "Andy Mouse / Care Bears / Transformers (HAM rare, 4 SKUs)", "do_onhand": "4", "do_cost": "5,000", "do_price": "&mdash;", "do_value": "20,000"},
    {"do_name": "Miffy Winter / Crayon Shinchan / Fufutietie Door God (+misc)", "do_onhand": "16", "do_cost": "&mdash;", "do_price": "&mdash;", "do_value": "~2,000"},
]
repeats["dead_owned_rows"] = dead_owned_rows

# --- dead_consign_rows ---
dead_consign_rows = [
    {
        "dc_tag_bg": "#e1f5ee",
        "dc_tag_color": "#0f6e56",
        "dc_tag": "CONSIGN",
        "dc_supplier": "Big Box Intl (Bearbrick TCT series &amp; Astro Boy &mdash; 43 SKUs, ~&#3647;1.0M)",
        "dc_skus": "43",
        "dc_units": "146",
        "dc_action": "RETURN",
    },
    {
        "dc_tag_bg": "#e1f5ee",
        "dc_tag_color": "#0f6e56",
        "dc_tag": "CONSIGN",
        "dc_supplier": "MNT series via V-00654 (Molinta / Shinwoo / Zzoton / Rico / Bob &hellip;)",
        "dc_skus": "50",
        "dc_units": "3,766",
        "dc_action": "RETURN",
    },
    {
        "dc_tag_bg": "#eeedfe",
        "dc_tag_color": "#5551FE",
        "dc_tag": "INTERCO",
        "dc_supplier": "Toysinbox (Lulupie / Dolores / Wasababy / Rainbowkido / Duckyo &hellip;)",
        "dc_skus": "346",
        "dc_units": "3,831",
        "dc_action": "REVIEW",
    },
]
repeats["dead_consign_rows"] = dead_consign_rows

# === ASSEMBLE & WRITE ===
data = {
    "scalars": scalars,
    "sections": sections,
    "repeats": repeats,
}

out_path = "/home/user/report/ActionCity/data.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"data.json written: {out_path}")
print(f"  scalars: {len(scalars)} keys")
print(f"  sections: {list(sections.keys())}")
for k, v in repeats.items():
    print(f"  repeats.{k}: {len(v)} rows")
