#!/usr/bin/env python3
"""
generate_email.py — Self-contained email generator for Juiceland Daily Sales Report
Date: 2026-06-19
"""
import re, sys

TEMPLATE_PATH = "/home/user/report/Juiceland/juiceland-template.html"
OUTPUT_PATH   = "/home/user/report/Juiceland/email.html"

# ─────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────

SECTIONS = {
    "am_review":          False,
    "seasonal":           True,
    "dormant":            True,
    "forecast_shown":     True,
    "forecast_suppressed":False,
    "anomaly_shown":      True,
}

SCALARS = {
    "report_date":            "2026-06-19",
    "report_date_display":    "19 June 2026",
    "report_day_th":          "วันศุกร์",
    "window_30d_start":       "2026-05-21",
    "generated_timestamp":    "2026-06-20 07:15",
    "subject_prefix":         "🔥",
    "comb_net":               "90,344",
    "mw1_net":                "45,531",
    "se3_net":                "32,140",
    "pkt_net":                "12,673",
    "signed_pct":             "+23.9",
    "mw1_vs_30d":             "+24.1",
    "se3_vs_30d":             "+33.9",
    "pkt_vs_30d":             "+3.6",
    "mw1_avg_30d":            "36,691",
    "se3_avg_30d":            "24,010",
    "pkt_avg_30d":            "12,231",
    "mw1_min_30d":            "25,977",
    "mw1_max_30d":            "46,618",
    "se3_min_30d":            "12,035",
    "se3_max_30d":            "39,492",
    "pkt_min_30d":            "7,039",
    "pkt_max_30d":            "16,361",
    "comb_avg_30d":           "72,931",
    "comb_monthly_runrate":   "2,187.9K",
    "last7_total":            "520,218",
    "last7_avg":              "74,317",
    "mw1_7d_total":           "273,623",
    "se3_7d_total":           "159,672",
    "pkt_7d_total":           "86,923",
    "comb_7d_total":          "520,218",
    "am_queue_count":         "0",
    "dormant_count":          "36",
    "grape_total_rev":        "238,740",
    "grape_last_mw1":         "21 May 2026",
    "grape_last_se3":         "28 Apr 2026",
    "np_summary_line":        "First sold in trailing 30 days (21 May–19 Jun 2026) · All branches · ex-VAT",
    "np_total_units":         "619",
    "np_total_rev":           "102,148",
    "drinks_n":               "10",
    "drinks_todate_units":    "132",
    "drinks_todate_rev":      "13,373",
    "fruit_n":                "4",
    "fruit_todate_units":     "63",
    "fruit_todate_rev":       "10,115",
    "new_cat_n":              "9",
    "new_cat_todate_units":   "424",
    "new_cat_todate_rev":     "78,660",
    "drinks_yest":            "3",
    "drinks_yest_rev":        "355",
    "fruit_yest":             "8",
    "fruit_yest_rev":         "1,178",
    "new_cat_yest":           "27",
    "new_cat_yest_rev":       "4,720",
}

# ── Chart days (30 days) ──────────────────────
chart_days = [
  {"date":"21 May","day_num":"21","weekday_th_abbr":"พ","mw1_net":"36,941","mw1_bar_px":174,"se3_net":"29,297","se3_bar_px":138,"pkt_net":"9,611","pkt_bar_px":45},
  {"date":"22 May","day_num":"22","weekday_th_abbr":"พฤ","mw1_net":"40,088","mw1_bar_px":189,"se3_net":"26,689","se3_bar_px":126,"pkt_net":"10,358","pkt_bar_px":49},
  {"date":"23 May","day_num":"23","weekday_th_abbr":"ส","mw1_net":"38,640","mw1_bar_px":182,"se3_net":"39,492","se3_bar_px":186,"pkt_net":"12,698","pkt_bar_px":60},
  {"date":"24 May","day_num":"24","weekday_th_abbr":"อา","mw1_net":"45,430","mw1_bar_px":214,"se3_net":"28,328","se3_bar_px":134,"pkt_net":"12,933","pkt_bar_px":61},
  {"date":"25 May","day_num":"25","weekday_th_abbr":"จ","mw1_net":"38,221","mw1_bar_px":180,"se3_net":"31,984","se3_bar_px":151,"pkt_net":"10,502","pkt_bar_px":50},
  {"date":"26 May","day_num":"26","weekday_th_abbr":"อ","mw1_net":"36,853","mw1_bar_px":174,"se3_net":"24,576","se3_bar_px":116,"pkt_net":"7,039","pkt_bar_px":33},
  {"date":"27 May","day_num":"27","weekday_th_abbr":"พ","mw1_net":"33,877","mw1_bar_px":160,"se3_net":"26,502","se3_bar_px":125,"pkt_net":"16,234","pkt_bar_px":77},
  {"date":"28 May","day_num":"28","weekday_th_abbr":"พฤ","mw1_net":"33,415","mw1_bar_px":158,"se3_net":"31,121","se3_bar_px":147,"pkt_net":"12,474","pkt_bar_px":59},
  {"date":"29 May","day_num":"29","weekday_th_abbr":"ศ","mw1_net":"42,211","mw1_bar_px":199,"se3_net":"22,568","se3_bar_px":106,"pkt_net":"13,844","pkt_bar_px":65},
  {"date":"30 May","day_num":"30","weekday_th_abbr":"ส","mw1_net":"34,788","mw1_bar_px":164,"se3_net":"26,883","se3_bar_px":127,"pkt_net":"14,605","pkt_bar_px":69},
  {"date":"31 May","day_num":"31","weekday_th_abbr":"อา","mw1_net":"28,583","mw1_bar_px":135,"se3_net":"32,544","se3_bar_px":153,"pkt_net":"14,052","pkt_bar_px":66},
  {"date":"1 Jun","day_num":"1","weekday_th_abbr":"จ","mw1_net":"32,133","mw1_bar_px":152,"se3_net":"24,075","se3_bar_px":114,"pkt_net":"13,940","pkt_bar_px":66},
  {"date":"2 Jun","day_num":"2","weekday_th_abbr":"อ","mw1_net":"36,476","mw1_bar_px":172,"se3_net":"15,959","se3_bar_px":75,"pkt_net":"9,920","pkt_bar_px":47},
  {"date":"3 Jun","day_num":"3","weekday_th_abbr":"พ","mw1_net":"40,024","mw1_bar_px":189,"se3_net":"19,497","se3_bar_px":92,"pkt_net":"10,813","pkt_bar_px":51},
  {"date":"4 Jun","day_num":"4","weekday_th_abbr":"พฤ","mw1_net":"35,667","mw1_bar_px":168,"se3_net":"16,604","se3_bar_px":78,"pkt_net":"13,146","pkt_bar_px":62},
  {"date":"5 Jun","day_num":"5","weekday_th_abbr":"ศ","mw1_net":"35,611","mw1_bar_px":168,"se3_net":"20,180","se3_bar_px":95,"pkt_net":"13,589","pkt_bar_px":64},
  {"date":"6 Jun","day_num":"6","weekday_th_abbr":"ส","mw1_net":"32,714","mw1_bar_px":154,"se3_net":"23,312","se3_bar_px":110,"pkt_net":"13,867","pkt_bar_px":65},
  {"date":"7 Jun","day_num":"7","weekday_th_abbr":"อา","mw1_net":"25,977","mw1_bar_px":123,"se3_net":"17,749","se3_bar_px":84,"pkt_net":"12,993","pkt_bar_px":61},
  {"date":"8 Jun","day_num":"8","weekday_th_abbr":"จ","mw1_net":"38,857","mw1_bar_px":183,"se3_net":"24,570","se3_bar_px":116,"pkt_net":"12,810","pkt_bar_px":60},
  {"date":"9 Jun","day_num":"9","weekday_th_abbr":"อ","mw1_net":"30,613","mw1_bar_px":144,"se3_net":"12,035","se3_bar_px":57,"pkt_net":"10,190","pkt_bar_px":48},
  {"date":"10 Jun","day_num":"10","weekday_th_abbr":"พ","mw1_net":"37,665","mw1_bar_px":178,"se3_net":"22,195","se3_bar_px":105,"pkt_net":"10,250","pkt_bar_px":48},
  {"date":"11 Jun","day_num":"11","weekday_th_abbr":"พฤ","mw1_net":"36,938","mw1_bar_px":174,"se3_net":"18,834","se3_bar_px":89,"pkt_net":"12,373","pkt_bar_px":58},
  {"date":"12 Jun","day_num":"12","weekday_th_abbr":"ศ","mw1_net":"35,378","mw1_bar_px":167,"se3_net":"25,627","se3_bar_px":121,"pkt_net":"11,753","pkt_bar_px":55},
  {"date":"13 Jun","day_num":"13","weekday_th_abbr":"ส","mw1_net":"33,715","mw1_bar_px":159,"se3_net":"25,149","se3_bar_px":119,"pkt_net":"12,259","pkt_bar_px":58},
  {"date":"14 Jun","day_num":"14","weekday_th_abbr":"อา","mw1_net":"36,683","mw1_bar_px":173,"se3_net":"18,753","se3_bar_px":88,"pkt_net":"16,361","pkt_bar_px":77},
  {"date":"15 Jun","day_num":"15","weekday_th_abbr":"จ","mw1_net":"34,196","mw1_bar_px":161,"se3_net":"22,469","se3_bar_px":106,"pkt_net":"12,234","pkt_bar_px":58},
  {"date":"16 Jun","day_num":"16","weekday_th_abbr":"อ","mw1_net":"39,711","mw1_bar_px":187,"se3_net":"19,173","se3_bar_px":90,"pkt_net":"9,078","pkt_bar_px":43},
  {"date":"17 Jun","day_num":"17","weekday_th_abbr":"พ","mw1_net":"37,169","mw1_bar_px":175,"se3_net":"20,735","se3_bar_px":98,"pkt_net":"10,010","pkt_bar_px":47},
  {"date":"18 Jun","day_num":"18","weekday_th_abbr":"พฤ","mw1_net":"46,618","mw1_bar_px":220,"se3_net":"21,253","se3_bar_px":100,"pkt_net":"14,308","pkt_bar_px":67},
  {"date":"19 Jun","day_num":"19","weekday_th_abbr":"ศ","mw1_net":"45,531","mw1_bar_px":215,"se3_net":"32,140","se3_bar_px":151,"pkt_net":"12,673","pkt_bar_px":60},
]

last7_headers = [
  {"col_date":"13 Jun","col_weekday_th":"ส","header_bg":""},
  {"col_date":"14 Jun","col_weekday_th":"อา","header_bg":""},
  {"col_date":"15 Jun","col_weekday_th":"จ","header_bg":""},
  {"col_date":"16 Jun","col_weekday_th":"อ","header_bg":""},
  {"col_date":"17 Jun","col_weekday_th":"พ","header_bg":""},
  {"col_date":"18 Jun","col_weekday_th":"พฤ","header_bg":""},
  {"col_date":"19 Jun","col_weekday_th":"ศ","header_bg":"background:#4744CD;"},
]

last7_mw1 = [
  {"net":"33,715","cell_style":""},
  {"net":"36,683","cell_style":""},
  {"net":"34,196","cell_style":""},
  {"net":"39,711","cell_style":""},
  {"net":"37,169","cell_style":""},
  {"net":"46,618","cell_style":""},
  {"net":"45,531","cell_style":"background:#FFF3E0;font-weight:700;"},
]
last7_se3 = [
  {"net":"25,149","cell_style":""},
  {"net":"18,753","cell_style":""},
  {"net":"22,469","cell_style":""},
  {"net":"19,173","cell_style":""},
  {"net":"20,735","cell_style":""},
  {"net":"21,253","cell_style":""},
  {"net":"32,140","cell_style":"background:#FFF3E0;font-weight:700;"},
]
last7_pkt = [
  {"net":"12,259","cell_style":""},
  {"net":"16,361","cell_style":""},
  {"net":"12,234","cell_style":""},
  {"net":"9,078","cell_style":""},
  {"net":"10,010","cell_style":""},
  {"net":"14,308","cell_style":""},
  {"net":"12,673","cell_style":"background:#FFF3E0;font-weight:700;"},
]
last7_comb = [
  {"net":"71,123","cell_bg":""},
  {"net":"71,797","cell_bg":""},
  {"net":"68,899","cell_bg":""},
  {"net":"67,962","cell_bg":""},
  {"net":"67,914","cell_bg":""},
  {"net":"82,179","cell_bg":""},
  {"net":"90,344","cell_bg":"background:#FFF3E0;"},
]

seasonal_skus = [
  {"fruit_emoji":"🍒","memo":"LYCHEE 400G.","launch":"28 May","mw1_units":"15","mw1_per_day":"79","se3_units":"24","se3_per_day":"127"},
  {"fruit_emoji":"🍈","memo":"MANGOSTEEN 400g.","launch":"28 May","mw1_units":"1","mw1_per_day":"8","se3_units":"3","se3_per_day":"23"},
  {"fruit_emoji":"🌹","memo":"ROSE APPLE 400G.","launch":"30 May","mw1_units":"0","mw1_per_day":"0","se3_units":"14","se3_per_day":"71"},
  {"fruit_emoji":"🍊","memo":"Orange 400 g (Pack)","launch":"18 Jun","mw1_units":"0","mw1_per_day":"0","se3_units":"6","se3_per_day":"28"},
]

seasonal_coverage = [
  {"branch_label":"MW1 · Suvarnabhumi T1","branch_color":"#5551FE","grape_baseline":"339","new_fruit_per_day":"87","coverage_pct":"25.7","daily_gap":"฿-252/d","monthly_impact":"฿-7,554/mo","coverage_color":"#721C24","badge_bg":"#F8D7DA","badge_text":"🔴 Large gap — push promotion or add SKU"},
  {"branch_label":"SE3 · Suvarnabhumi T1","branch_color":"#F27061","grape_baseline":"251","new_fruit_per_day":"250","coverage_pct":"99.6","daily_gap":"฿-1/d","monthly_impact":"฿-33/mo","coverage_color":"#155724","badge_bg":"#D4EDDA","badge_text":"✅ Fully replaced"},
]

# ── Top 20 per branch (raw lists) ─────────────
def truncate(s, n=34):
    return s if len(s) <= n else s[:n] + "…"

mw1_top20_raw = [
  ("EVIAN", 50, 5608, 5),
  ("MANGO 400G.", 13, 1944, 4),
  ("PRIDE PARROT RED", 13, 2430, 2),
  ("COCONUT READY TO DRINK", 11, 1748, 3),
  ("WATERMELON 400G.", 11, 1542, 3),
  ("C3 WATERMELON COLD PREESED 22OZ", 9, 1766, 2),
  ("3 kinds of fruit400g Papaya/Pineapple/Watermelon", 9, 1262, 3),
  ("S1 COCONUT SMOOTHIE 16OZ", 8, 1346, 2),
  ("S5 MANGO SMOOTHIE 22OZ", 8, 1383, 3),
  ("C3 WATERMELON COLD PREESED 16OZ", 6, 1037, 2),
  ("C1 GUAVA&GREEN APPLE&RED APPLE COLD PRESSED 22OZ", 5, 981, 3),
  ("P1 GOLDEN GLOW 22OZ", 5, 1051, 3),
  ("Mango juice (Bottle) 300 ml", 5, 864, 2),
  ("S3 WATERMELON SMOOTHIE 16OZ", 5, 748, 3),
  ("PAPAYA 400G.", 5, 701, 2),
  ("WATERMELON JUICE BOTTLE", 5, 864, 2),
  ("P1 GOLDEN GLOW 16OZ", 5, 935, 2),
  ("C2 ORANGE COLD PREESED 22OZ", 4, 785, 3),
  ("PINEAPPLE 400G.", 4, 561, 2),
  ("COCONUT JUICE BOTTLE", 4, 692, 2),
]
se3_top20_raw = [
  ("EVIAN", 44, 4923, 3),
  ("WATERMELON 400G.", 16, 2243, 3),
  ("MANGO 400G.", 12, 1794, 3),
  ("3 kinds of fruit400g Papaya/Pineapple/Watermelon", 9, 1262, 4),
  ("COCONUT READY TO DRINK", 9, 1430, 3),
  ("PINEAPPLE 400G.", 8, 1122, 2),
  ("PRIDE PARROT RED", 8, 1495, 4),
  ("DRAGON FRUIT 400G.", 5, 701, 3),
  ("P1 GOLDEN GLOW 22OZ", 5, 1051, 1),
  ("S3 WATERMELON SMOOTHIE 16OZ", 5, 748, 2),
  ("PAPAYA 400G.", 5, 701, 3),
  ("S1 COCONUT SMOOTHIE 22OZ", 5, 958, 3),
  ("S2 MANGO PASSION SMOOTHIE 16OZ", 5, 748, 3),
  ("CI3 ICED AMERICANO 16OZ", 4, 579, 2),
  ("S5 MANGO SMOOTHIE 16OZ", 4, 598, 2),
  ("Orange 400 g (Pack)", 4, 561, 3),
  ("CI5 ICED LATTE 16OZ", 3, 477, 2),
  ("S1 COCONUT SMOOTHIE 16OZ", 3, 505, 2),
  ("C5 PINEAPPLE&GREEN APPLE COLD PRESSED 16OZ", 3, 519, 2),
  ("C1 GUAVA&GREEN APPLE&RED APPLE COLD PRESSED 22OZ", 3, 519, 1),
]
pkt_top20_raw = [
  ("Evian 500ml. (Bottle)", 12, 1335, 2),
  ("Up size Smoothie & Cold Pressed", 9, 208, 4),
  ("Pineapple 400 g. (Pack)", 4, 561, 2),
  ("CH1 Cappuccino (hot) 12oz", 3, 392, 1),
  ("Coconut (EA)", 3, 477, 2),
  ("C2 orange cold pressed 16oz", 3, 519, 2),
  ("S1 Coconut smoothie 16oz", 3, 505, 2),
  ("Watermelon Cold Pressed Juice 300ml", 2, 346, 2),
  ("Chicken Ham Wrap", 2, 481, 2),
  ("Watermelon 400 g. (Pack)", 2, 280, 1),
  ("Coke 500 ml. (Bottle)", 2, 150, 2),
  ("YS2 Strawberry yoghurt smoothie 16oz", 2, 327, 2),
  ("S5 mango smoothie 16oz", 2, 299, 2),
  ("Mango 400 g. (Pack)", 2, 299, 2),
  ("S2 mango passion smoothie 16oz", 2, 299, 2),
  ("CI4 Iced Americano 16oz", 2, 276, 1),
  ("Mango juice (Bottle) 300 ml", 2, 346, 2),
  ("Ham and Cheese Croissant", 2, 355, 1),
  ("Tuna Sandwich", 2, 303, 2),
  ("P2 pineapple kale cold pressed 16oz", 2, 374, 1),
]

def build_top20_rows(raw_list):
    rows = []
    for i, (memo, qty, rev, bills) in enumerate(raw_list):
        row_bg = "#fff" if i % 2 == 0 else "#FAFAFA"
        rows.append({
            "rank": str(i + 1),
            "memo_full": memo,
            "memo_display": truncate(memo),
            "qty": str(qty),
            "revenue": f"{rev:,}",
            "bills": str(bills),
            "row_bg": row_bg,
        })
    return rows

top20_branches_data = [
    {"header_color":"#5551FE","header_label":"MW1 · 26-T1MW1-03+04","rows":build_top20_rows(mw1_top20_raw)},
    {"header_color":"#F27061","header_label":"SE3 · 27-T1SE3-05","rows":build_top20_rows(se3_top20_raw)},
    {"header_color":"#2E7D32","header_label":"PKT · 28 Unit 362 (Phuket)","rows":build_top20_rows(pkt_top20_raw)},
]

# ── Dormant SKUs ──────────────────────────────
mw1_dormant_raw = [
  ("Overnight Oat mango 16 oz","06/06",13,27,15,"6,788","#E65100"),
  ("MAEVAREE MANGO STICKY RICE SMOOTHIE","08/06",11,26,14,"5,546","#E65100"),
  ("MAEVAREE MANGO YOGHURT STICKY RICE","12/06",7,21,12,"4,514","#E65100"),
  ("HOT CHOCOLATE 8 oz","27/05",23,18,4,"2,187","#C62828"),
  ("MANGO (1 PCS.)","11/06",8,13,9,"1,822","#E65100"),
  ("BLUEBERRY GREEK YOGURT","05/06",14,9,7,"1,590","#C62828"),
  ("SEEDLESS GRAPE 400G.","11/06",8,6,4,"897","#E65100"),
  ("VANILLA BEAN GREEK YOGURT","26/05",24,6,4,"1,060","#C62828"),
  ("T2 ICED THAI TEA WITH LIME 16OZ","01/06",18,4,3,"561","#C62828"),
  ("Mango Pineapple Smoothie 16oz","23/05",27,4,2,"692","#C62828"),
  ("Mango Berry Smoothie 16oz","26/05",24,4,3,"692","#C62828"),
  ("Mango Sticky Rice (Box)","01/06",18,3,3,"502","#C62828"),
]
se3_dormant_raw = [
  ("Cantaloupe 400 g (Pack)","09/06",10,52,18,"7,290","#E65100"),
  ("MAEVAREE MANGO STICKY RICE SMOOTHIE","12/06",7,38,16,"8,147","#E65100"),
  ("HOT CHOCOLATE 8 oz","29/05",21,22,6,"2,673","#C62828"),
  ("MAEVAREE MANGO YOGHURT STICKY RICE","12/06",7,21,12,"4,492","#E65100"),
  ("Mango Sticky Rice (Box)","31/05",19,19,8,"3,179","#C62828"),
  ("Golden Harmony Greek Yogur","31/05",19,17,8,"3,003","#C62828"),
  ("Pineapple Cold Pressed Juice 300ml","12/06",7,14,10,"2,421","#E65100"),
  ("ORANGE JUICE BOTTLE","10/06",9,14,11,"2,421","#E65100"),
  ("Overnight Oat Berry 16 oz","27/05",23,7,5,"1,694","#C62828"),
  ("CI3 ICED AMERICANO 22OZ","08/06",11,6,5,"1,009","#E65100"),
  ("MANGO PINEAPPLE SMOOTHIE 16OZ","31/05",19,6,4,"1,037","#C62828"),
  ("BANANA YOGHURT SMOOTHIE 16OZ","28/05",22,6,5,"981","#C62828"),
  ("Overnight Oat mango 16 oz","04/06",15,5,5,"1,257","#C62828"),
  ("SEEDLESS GRAPE 400G.","08/06",11,5,2,"748","#E65100"),
  ("CI4 ICED CAPPUCCINO 22OZ","30/05",20,4,3,"729","#C62828"),
  ("CI4 ICED CAPPUCCINO 16OZ","10/06",9,3,2,"477","#E65100"),
  ("MANGOSTEEN 400g.","01/06",18,3,3,"701","#C62828"),
]
pkt_dormant_raw = [
  ("Banana 2PCS.","06/06",13,15,12,"827","#E65100"),
  ("CH3 Espresso (hot) 4oz","12/06",7,11,7,"1,285","#E65100"),
  ("Mango Berry Smoothie 16oz","11/06",8,8,5,"1,383","#E65100"),
  ("Pride Parrot Red Smoothie 22 oz.","05/06",14,4,2,"748","#C62828"),
  ("T2 Iced Thai tea with lime 16oz","11/06",8,4,3,"561","#E65100"),
  ("Nestle Water 600 ml","06/06",13,4,4,"37","#E65100"),
  ("singha soda water 325ml","04/06",15,4,2,"243","#C62828"),
]

def build_dormant_rows(raw_list):
    rows = []
    for (memo, last, gap, qty30, days30, rev30, gap_color) in raw_list:
        rows.append({
            "memo_full": memo,
            "memo_display": truncate(memo),
            "gap_days": str(gap),
            "gap_color": gap_color,
            "qty_30d": str(qty30),
            "days_sold_30d": str(days30),
            "rev_30d": rev30,
        })
    return rows

dormant_branches_data = [
    {"header_color":"#5551FE","branch":"MW1","branch_count":"12","rows":build_dormant_rows(mw1_dormant_raw)},
    {"header_color":"#F27061","branch":"SE3","branch_count":"17","rows":build_dormant_rows(se3_dormant_raw)},
    {"header_color":"#2E7D32","branch":"PKT","branch_count":"7","rows":build_dormant_rows(pkt_dormant_raw)},
]

# ── New Product Type Tables ───────────────────
drinks_rows = [
  {"memo":"MOOVE CLEAR PROTEIN","total_units":"23","total_rev":"3,224","branch_split":"MW1 only","yest_units":"2","launch":"13 Jun","notes":"MW1 functional drink","status_badge":"🟢 on target"},
  {"memo":"HOT CHOCOLATE 8 oz","total_units":"40","total_rev":"4,860","branch_split":"MW1+SE3","yest_units":"0","launch":"24 May","notes":"seasonal","status_badge":"🔴 waste risk (dormant)"},
  {"memo":"Fanta Orange","total_units":"21","total_rev":"1,570","branch_split":"PKT only","yest_units":"1","launch":"31 May","notes":"PKT beverage","status_badge":"🟢 on target"},
  {"memo":"Fanta Strawberry","total_units":"22","total_rev":"1,645","branch_split":"PKT only","yest_units":"0","launch":"1 Jun","notes":"PKT beverage","status_badge":"🟠 stock-out suspect"},
  {"memo":"Sprite","total_units":"19","total_rev":"1,421","branch_split":"PKT only","yest_units":"0","launch":"30 May","notes":"PKT beverage","status_badge":"🟠 stock-out suspect"},
  {"memo":"HOT MOCHA 8 oz","total_units":"4","total_rev":"470","branch_split":"MW1+SE3","yest_units":"0","launch":"24 May","notes":"seasonal","status_badge":"🔴 waste risk (dormant)"},
  {"memo":"Iced Espresso Orange 16oz","total_units":"1","total_rev":"163","branch_split":"MW1","yest_units":"0","launch":"3 Jun","notes":"MW1 special","status_badge":"🟡 below target"},
  {"memo":"Hot Tea Green Tea","total_units":"1","total_rev":"130","branch_split":"PKT","yest_units":"0","launch":"30 May","notes":"PKT hot beverage","status_badge":"🟡 below target"},
  {"memo":"Ice 16oz","total_units":"1","total_rev":"52","branch_split":"PKT","yest_units":"0","launch":"5 Jun","notes":"PKT add-on","status_badge":"⚪ no sales yet"},
  {"memo":"Fanta Fruit Punch","total_units":"0","total_rev":"0","branch_split":"PKT only","yest_units":"0","launch":"1 Jun","notes":"PKT beverage","status_badge":"⚪ no sales yet"},
]
fruit_rows = [
  {"memo":"LYCHEE 400G.","total_units":"39","total_rev":"6,196","branch_split":"MW1+SE3","yest_units":"2","launch":"28 May","notes":"seasonal fruit","status_badge":"🟢 on target"},
  {"memo":"MANGOSTEEN 400g.","total_units":"4","total_rev":"935","branch_split":"MW1+SE3","yest_units":"0","launch":"28 May","notes":"seasonal fruit","status_badge":"🟡 below target"},
  {"memo":"ROSE APPLE 400G.","total_units":"14","total_rev":"2,143","branch_split":"SE3 only","yest_units":"2","launch":"30 May","notes":"seasonal fruit","status_badge":"🟢 on target"},
  {"memo":"Orange 400 g (Pack)","total_units":"6","total_rev":"841","branch_split":"SE3 only","yest_units":"4","launch":"18 Jun","notes":"seasonal fruit","status_badge":"🟢 on target"},
]
new_cat_rows = [
  {"memo":"PRIDE PARROT RED","total_units":"223","total_rev":"41,439","branch_split":"MW1+SE3+PKT","yest_units":"22","launch":"1 Jun","notes":"signature smoothie","status_badge":"🟢 on target"},
  {"memo":"PRIDE PARROT YELLOW","total_units":"119","total_rev":"22,550","branch_split":"MW1+SE3+PKT","yest_units":"3","launch":"1 Jun","notes":"signature smoothie","status_badge":"🟢 on target"},
  {"memo":"Overnight Oat mango 16 oz","total_units":"32","total_rev":"8,045","branch_split":"MW1+SE3","yest_units":"0","launch":"21 May","notes":"perishable oat","status_badge":"🔴 waste risk (dormant)"},
  {"memo":"Overnight Oat Berry 16 oz","total_units":"8","total_rev":"1,936","branch_split":"SE3+MW1","yest_units":"0","launch":"22 May","notes":"perishable oat","status_badge":"🔴 waste risk (dormant)"},
  {"memo":"Chicken Club Croissant","total_units":"32","total_rev":"4,456","branch_split":"SE3 only","yest_units":"0","launch":"22 May","notes":"food item","status_badge":"🟠 stock-out suspect"},
  {"memo":"BANANA TOPPING","total_units":"6","total_rev":"450","branch_split":"MW1+SE3","yest_units":"0","launch":"1 Jun","notes":"topping add-on","status_badge":"🟠 stock-out suspect"},
  {"memo":"DRAGON FRUIT TOPPING","total_units":"5","total_rev":"373","branch_split":"MW1+SE3","yest_units":"0","launch":"1 Jun","notes":"topping add-on","status_badge":"🟠 stock-out suspect"},
  {"memo":"GRANOLA TOPPING","total_units":"2","total_rev":"150","branch_split":"MW1","yest_units":"0","launch":"1 Jun","notes":"topping add-on","status_badge":"⚪ no sales yet"},
  {"memo":"SEEDLESS GRAPE TOPPING","total_units":"1","total_rev":"75","branch_split":"MW1","yest_units":"0","launch":"1 Jun","notes":"topping add-on","status_badge":"⚪ no sales yet"},
]

np_type_tables_data = [
    {"type_bg":"#1976D2","type_fg":"#fff","type_icon":"🥤","type_label":"Drinks","rows":drinks_rows},
    {"type_bg":"#AD1457","type_fg":"#fff","type_icon":"🍉","type_label":"Seasonal Fruits","rows":fruit_rows},
    {"type_bg":"#2E7D32","type_fg":"#fff","type_icon":"⭐","type_label":"New Category","rows":new_cat_rows},
]

# ─────────────────────────────────────────────
# RENDERING HELPERS
# ─────────────────────────────────────────────

def apply_sections(html, sections):
    """Remove false section blocks; keep content of true ones."""
    pattern = re.compile(
        r"<!--\s*SECTION:(\w+)[\s\S]*?-->([\s\S]*?)<!--\s*/SECTION:\1\s*-->",
        re.DOTALL
    )
    def repl(m):
        name, inner = m.group(1), m.group(2)
        return inner if sections.get(name, False) else ""
    prev = None
    while prev != html:
        prev = html
        html = pattern.sub(repl, html)
    return html

def extract_repeat_inner(html, repeat_name):
    """Return the inner template for a named REPEAT block."""
    pat = re.compile(
        r"<!--\s*REPEAT:" + re.escape(repeat_name) + r"[\s\S]*?-->([\s\S]*?)<!--\s*/REPEAT:" + re.escape(repeat_name) + r"\s*-->",
        re.DOTALL
    )
    m = pat.search(html)
    if not m:
        return None
    return m.group(1)

def render_items(inner_template, items):
    """Render a list of dict items into an inner template."""
    out = []
    for item in items:
        block = inner_template
        for k, v in item.items():
            block = block.replace("{{" + k + "}}", str(v))
        out.append(block)
    return "".join(out)

def replace_repeat_block(html, repeat_name, rendered_html):
    """Replace the entire REPEAT block (including markers) with rendered_html."""
    pat = re.compile(
        r"<!--\s*REPEAT:" + re.escape(repeat_name) + r"[\s\S]*?-->[\s\S]*?<!--\s*/REPEAT:" + re.escape(repeat_name) + r"\s*-->",
        re.DOTALL
    )
    return pat.sub(rendered_html, html, count=1)

def render_simple_repeat(html, repeat_name, items):
    """Extract inner, render items, replace block — for flat (non-nested) repeats."""
    inner = extract_repeat_inner(html, repeat_name)
    if inner is None:
        return html
    rendered = render_items(inner, items)
    return replace_repeat_block(html, repeat_name, rendered)

def apply_scalars(html, scalars):
    for k, v in scalars.items():
        html = html.replace("{{" + k + "}}", str(v))
    return html

# ─────────────────────────────────────────────
# TOP 20 BRANCHES nested rendering
# ─────────────────────────────────────────────

def render_top20_branches(html, branches_data):
    """
    Extract the outer REPEAT:top20_branches block, including the nested
    REPEAT:top20_rows inside it. For each branch, pre-render the inner rows,
    then substitute into the outer template (with the REPEAT:top20_rows marker
    replaced by the pre-rendered HTML).
    """
    outer_inner = extract_repeat_inner(html, "top20_branches")
    if outer_inner is None:
        return html

    # Extract the inner REPEAT:top20_rows template from within the outer inner block
    inner_rows_template = extract_repeat_inner(outer_inner, "top20_rows")
    if inner_rows_template is None:
        return html

    # Pattern to match the entire inner REPEAT:top20_rows block
    inner_repeat_pat = re.compile(
        r"<!--\s*REPEAT:top20_rows[\s\S]*?-->[\s\S]*?<!--\s*/REPEAT:top20_rows\s*-->",
        re.DOTALL
    )

    rendered_branches = []
    for branch in branches_data:
        # Pre-render this branch's rows
        pre_rendered_rows = render_items(inner_rows_template, branch["rows"])
        # Replace the inner REPEAT block in the outer inner template with pre-rendered rows
        branch_block = inner_repeat_pat.sub(pre_rendered_rows, outer_inner, count=1)
        # Substitute branch-level scalars
        for k in ("header_color", "header_label"):
            branch_block = branch_block.replace("{{" + k + "}}", str(branch[k]))
        rendered_branches.append(branch_block)

    rendered = "".join(rendered_branches)
    return replace_repeat_block(html, "top20_branches", rendered)

# ─────────────────────────────────────────────
# DORMANT BRANCHES nested rendering
# ─────────────────────────────────────────────

def render_dormant_branches(html, branches_data):
    outer_inner = extract_repeat_inner(html, "dormant_branches")
    if outer_inner is None:
        return html

    inner_rows_template = extract_repeat_inner(outer_inner, "dormant_rows")
    if inner_rows_template is None:
        return html

    inner_repeat_pat = re.compile(
        r"<!--\s*REPEAT:dormant_rows[\s\S]*?-->[\s\S]*?<!--\s*/REPEAT:dormant_rows\s*-->",
        re.DOTALL
    )

    rendered_branches = []
    for branch in branches_data:
        pre_rendered_rows = render_items(inner_rows_template, branch["rows"])
        branch_block = inner_repeat_pat.sub(pre_rendered_rows, outer_inner, count=1)
        for k in ("header_color", "branch", "branch_count"):
            branch_block = branch_block.replace("{{" + k + "}}", str(branch[k]))
        rendered_branches.append(branch_block)

    rendered = "".join(rendered_branches)
    return replace_repeat_block(html, "dormant_branches", rendered)

# ─────────────────────────────────────────────
# NP TYPE TABLES nested rendering
# ─────────────────────────────────────────────

def render_np_type_tables(html, tables_data):
    outer_inner = extract_repeat_inner(html, "np_type_tables")
    if outer_inner is None:
        return html

    inner_rows_template = extract_repeat_inner(outer_inner, "np_rows")
    if inner_rows_template is None:
        return html

    inner_repeat_pat = re.compile(
        r"<!--\s*REPEAT:np_rows[\s\S]*?-->[\s\S]*?<!--\s*/REPEAT:np_rows\s*-->",
        re.DOTALL
    )

    rendered_tables = []
    for table in tables_data:
        pre_rendered_rows = render_items(inner_rows_template, table["rows"])
        table_block = inner_repeat_pat.sub(pre_rendered_rows, outer_inner, count=1)
        for k in ("type_bg", "type_fg", "type_icon", "type_label"):
            table_block = table_block.replace("{{" + k + "}}", str(table[k]))
        rendered_tables.append(table_block)

    rendered = "".join(rendered_tables)
    return replace_repeat_block(html, "np_type_tables", rendered)

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        html = f.read()

    # 1. Apply sections (drop false ones)
    html = apply_sections(html, SECTIONS)

    # 2. Handle nested REPEATs first (top20, dormant, np_type)
    html = render_top20_branches(html, top20_branches_data)
    html = render_dormant_branches(html, dormant_branches_data)
    html = render_np_type_tables(html, np_type_tables_data)

    # 3. Handle flat REPEATs
    html = render_simple_repeat(html, "chart_days", chart_days)
    html = render_simple_repeat(html, "last7_headers", last7_headers)
    html = render_simple_repeat(html, "last7_mw1", last7_mw1)
    html = render_simple_repeat(html, "last7_se3", last7_se3)
    html = render_simple_repeat(html, "last7_pkt", last7_pkt)
    html = render_simple_repeat(html, "last7_comb", last7_comb)
    html = render_simple_repeat(html, "seasonal_skus", seasonal_skus)
    html = render_simple_repeat(html, "seasonal_coverage", seasonal_coverage)
    # am_items is in the am_review section which was removed; skip it
    # But if there's still a marker, clear it
    html = render_simple_repeat(html, "am_items", [])

    # 4. Apply scalars
    html = apply_scalars(html, SCALARS)

    # 5. Strip leftover REPEAT/SECTION markers
    html = re.sub(r"<!--\s*/?(?:REPEAT|SECTION):\w+[\s\S]*?-->", "", html)

    # 6. Warn about unresolved placeholders
    leftovers = sorted(set(re.findall(r"\{\{(\w+)\}\}", html)))
    if leftovers:
        print("WARNING: unresolved placeholders:", ", ".join(leftovers), file=sys.stderr)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Written: {OUTPUT_PATH} ({len(html):,} bytes)")

if __name__ == "__main__":
    main()

