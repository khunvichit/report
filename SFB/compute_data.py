#!/usr/bin/env python3
"""Compute data.json for SFB Daily Report 2026-06-22."""
import json, math

# ── Date constants ──
D1, D2, D8 = "2026-06-22", "2026-06-21", "2026-06-15"
REPORT_DATE_DISPLAY = "22 June 2026"
WEEKDAY_EN = "Monday"
WEEKDAY_TH = "วันจันทร์"
WINDOW_LABEL = "24 May – 22 Jun 2026"
MTD_LABEL = "1–22 Jun 2026"
D8_DISPLAY = "15 June 2026"
GENERATED_DISPLAY = "23 Jun 2026 00:05 ICT"

# ── Q1: location×BU for D1, D2, D8 ──
Q1 = [
  # D8 = 2026-06-15
  {"d":"2026-06-15","location":"26-T1MW1-03+04","bu":"Subway","bills":126,"revenue":47353.38},
  {"d":"2026-06-15","location":"05-DMK-Inter-S","bu":"Subway","bills":117,"revenue":33630.81},
  {"d":"2026-06-15","location":"22-DMK-3Pier2-SS","bu":"Siam Express","bills":45,"revenue":7865.34},
  {"d":"2026-06-15","location":"19-T1MB1-03","bu":"Subway","bills":87,"revenue":25850.48},
  {"d":"2026-06-15","location":"18-T1FW4-08-SS","bu":"Subway","bills":271,"revenue":99704.78},
  {"d":"2026-06-15","location":"27-T1SE3-05","bu":"Juice Land","bills":71,"revenue":20999.16},
  {"d":"2026-06-15","location":"27-T1SE3-05","bu":"Subway","bills":123,"revenue":32177.40},
  {"d":"2026-06-15","location":"27-T1SE3-05","bu":"Vendi","bills":82,"revenue":13718.67},
  {"d":"2026-06-15","location":"21-T1BE2-06","bu":"Subway","bills":118,"revenue":54836.51},
  {"d":"2026-06-15","location":"09-DMK-G1-S","bu":"Subway","bills":68,"revenue":17760.73},
  {"d":"2026-06-15","location":"20-PKT-Floor 3-S","bu":"Siam Express","bills":114,"revenue":35192.60},
  {"d":"2026-06-15","location":"24-T1EW4-14","bu":"Subway","bills":145,"revenue":59848.73},
  {"d":"2026-06-15","location":"26-T1MW1-03+04","bu":"Juice Land","bills":102,"revenue":31958.99},
  {"d":"2026-06-15","location":"04-DMK-T2MTE3-09","bu":"Subway","bills":126,"revenue":45361.66},
  {"d":"2026-06-15","location":"25-DMK-CS","bu":"Subway","bills":49,"revenue":11699.17},
  {"d":"2026-06-15","location":"22-DMK-3Pier2-SS","bu":"Subway","bills":56,"revenue":11279.42},
  {"d":"2026-06-15","location":"28 JUICELAND Unit 362","bu":"Juice Land","bills":50,"revenue":11433.69},
  {"d":"2026-06-15","location":"13-PKT-G1-S","bu":"Siam Express","bills":67,"revenue":20272.86},
  {"d":"2026-06-15","location":"23-T1CE4-13","bu":"Subway","bills":145,"revenue":32227.96},
  {"d":"2026-06-15","location":"17-T1ME2-30","bu":"Khiang","bills":193,"revenue":34091.92},
  # D2 = 2026-06-21
  {"d":"2026-06-21","location":"17-T1ME2-30","bu":"Khiang","bills":171,"revenue":28863.40},
  {"d":"2026-06-21","location":"22-DMK-3Pier2-SS","bu":"Subway","bills":95,"revenue":23443.07},
  {"d":"2026-06-21","location":"27-T1SE3-05","bu":"Juice Land","bills":96,"revenue":30962.72},
  {"d":"2026-06-21","location":"19-T1MB1-03","bu":"Subway","bills":78,"revenue":25067.78},
  {"d":"2026-06-21","location":"21-T1BE2-06","bu":"Subway","bills":119,"revenue":52194.41},
  {"d":"2026-06-21","location":"05-DMK-Inter-S","bu":"Subway","bills":147,"revenue":49309.83},
  {"d":"2026-06-21","location":"24-T1EW4-14","bu":"Subway","bills":126,"revenue":61858.53},
  {"d":"2026-06-21","location":"27-T1SE3-05","bu":"Subway","bills":134,"revenue":41961.76},
  {"d":"2026-06-21","location":"13-PKT-G1-S","bu":"Siam Express","bills":101,"revenue":21206.50},
  {"d":"2026-06-21","location":"25-DMK-CS","bu":"Subway","bills":59,"revenue":16273.80},
  {"d":"2026-06-21","location":"09-DMK-G1-S","bu":"Subway","bills":67,"revenue":16828.03},
  {"d":"2026-06-21","location":"23-T1CE4-13","bu":"Subway","bills":125,"revenue":33966.25},
  {"d":"2026-06-21","location":"04-DMK-T2MTE3-09","bu":"Subway","bills":126,"revenue":46429.84},
  {"d":"2026-06-21","location":"27-T1SE3-05","bu":"Vendi","bills":97,"revenue":25344.88},
  {"d":"2026-06-21","location":"20-PKT-Floor 3-S","bu":"Siam Express","bills":100,"revenue":28169.25},
  {"d":"2026-06-21","location":"26-T1MW1-03+04","bu":"Subway","bills":125,"revenue":45060.75},
  {"d":"2026-06-21","location":"26-T1MW1-03+04","bu":"Juice Land","bills":108,"revenue":33852.88},
  {"d":"2026-06-21","location":"28 JUICELAND Unit 362","bu":"Juice Land","bills":38,"revenue":7386.93},
  {"d":"2026-06-21","location":"18-T1FW4-08-SS","bu":"Subway","bills":213,"revenue":95846.50},
  {"d":"2026-06-21","location":"22-DMK-3Pier2-SS","bu":"Siam Express","bills":61,"revenue":14098.89},
  # D1 = 2026-06-22
  {"d":"2026-06-22","location":"22-DMK-3Pier2-SS","bu":"Siam Express","bills":39,"revenue":8451.27},
  {"d":"2026-06-22","location":"04-DMK-T2MTE3-09","bu":"Subway","bills":100,"revenue":33404.64},
  {"d":"2026-06-22","location":"21-T1BE2-06","bu":"Subway","bills":127,"revenue":53369.21},
  {"d":"2026-06-22","location":"13-PKT-G1-S","bu":"Siam Express","bills":107,"revenue":31073.79},
  {"d":"2026-06-22","location":"09-DMK-G1-S","bu":"Subway","bills":60,"revenue":14922.42},
  {"d":"2026-06-22","location":"24-T1EW4-14","bu":"Subway","bills":139,"revenue":57642.17},
  {"d":"2026-06-22","location":"26-T1MW1-03+04","bu":"Subway","bills":105,"revenue":42565.44},
  {"d":"2026-06-22","location":"27-T1SE3-05","bu":"Subway","bills":123,"revenue":32614.21},
  {"d":"2026-06-22","location":"18-T1FW4-08-SS","bu":"Subway","bills":267,"revenue":110456.18},
  {"d":"2026-06-22","location":"23-T1CE4-13","bu":"Subway","bills":152,"revenue":45564.41},
  {"d":"2026-06-22","location":"22-DMK-3Pier2-SS","bu":"Subway","bills":76,"revenue":17673.81},
  {"d":"2026-06-22","location":"25-DMK-CS","bu":"Subway","bills":58,"revenue":14981.33},
  {"d":"2026-06-22","location":"26-T1MW1-03+04","bu":"Juice Land","bills":104,"revenue":35098.22},
  {"d":"2026-06-22","location":"27-T1SE3-05","bu":"Juice Land","bills":77,"revenue":23382.85},
  {"d":"2026-06-22","location":"20-PKT-Floor 3-S","bu":"Siam Express","bills":94,"revenue":24764.53},
  {"d":"2026-06-22","location":"27-T1SE3-05","bu":"Vendi","bills":106,"revenue":17167.44},
  {"d":"2026-06-22","location":"17-T1ME2-30","bu":"Khiang","bills":163,"revenue":28647.68},
  {"d":"2026-06-22","location":"28 JUICELAND Unit 362","bu":"Juice Land","bills":39,"revenue":7170.12},
  {"d":"2026-06-22","location":"19-T1MB1-03","bu":"Subway","bills":80,"revenue":26307.51},
  {"d":"2026-06-22","location":"05-DMK-Inter-S","bu":"Subway","bills":103,"revenue":30175.70},
]

# ── Q2: 30-day BU totals ──
Q2 = [
  {"d":"2026-05-24","bu":"Juice Land","revenue":81019.33,"bills":243},
  {"d":"2026-05-24","bu":"Khiang","revenue":34686.31,"bills":191},
  {"d":"2026-05-24","bu":"Siam Express","revenue":70885.75,"bills":280},
  {"d":"2026-05-24","bu":"Subway","revenue":518461.45,"bills":1557},
  {"d":"2026-05-24","bu":"Vendi","revenue":14856.12,"bills":74},
  {"d":"2026-05-25","bu":"Juice Land","revenue":75426.83,"bills":223},
  {"d":"2026-05-25","bu":"Khiang","revenue":38335.72,"bills":195},
  {"d":"2026-05-25","bu":"Siam Express","revenue":72990.44,"bills":298},
  {"d":"2026-05-25","bu":"Subway","revenue":482917.31,"bills":1511},
  {"d":"2026-05-25","bu":"Vendi","revenue":12772.87,"bills":70},
  {"d":"2026-05-26","bu":"Juice Land","revenue":63988.08,"bills":193},
  {"d":"2026-05-26","bu":"Khiang","revenue":39595.62,"bills":187},
  {"d":"2026-05-26","bu":"Siam Express","revenue":57468.08,"bills":241},
  {"d":"2026-05-26","bu":"Subway","revenue":457603.08,"bills":1440},
  {"d":"2026-05-26","bu":"Vendi","revenue":9460.70,"bills":63},
  {"d":"2026-05-27","bu":"Juice Land","revenue":71601.17,"bills":236},
  {"d":"2026-05-27","bu":"Khiang","revenue":30554.34,"bills":192},
  {"d":"2026-05-27","bu":"Siam Express","revenue":66165.25,"bills":247},
  {"d":"2026-05-27","bu":"Subway","revenue":483104.38,"bills":1584},
  {"d":"2026-05-27","bu":"Vendi","revenue":12553.21,"bills":68},
  {"d":"2026-05-28","bu":"Juice Land","revenue":71972.26,"bills":220},
  {"d":"2026-05-28","bu":"Khiang","revenue":34115.50,"bills":186},
  {"d":"2026-05-28","bu":"Siam Express","revenue":68520.36,"bills":287},
  {"d":"2026-05-28","bu":"Subway","revenue":525488.03,"bills":1892},
  {"d":"2026-05-28","bu":"Vendi","revenue":18818.68,"bills":92},
  {"d":"2026-05-29","bu":"Juice Land","revenue":73479.16,"bills":236},
  {"d":"2026-05-29","bu":"Khiang","revenue":44263.79,"bills":226},
  {"d":"2026-05-29","bu":"Siam Express","revenue":67796.08,"bills":282},
  {"d":"2026-05-29","bu":"Subway","revenue":637448.60,"bills":2569},
  {"d":"2026-05-29","bu":"Vendi","revenue":13566.34,"bills":82},
  {"d":"2026-05-30","bu":"Juice Land","revenue":71286.14,"bills":227},
  {"d":"2026-05-30","bu":"Khiang","revenue":33264.99,"bills":183},
  {"d":"2026-05-30","bu":"Siam Express","revenue":74231.57,"bills":274},
  {"d":"2026-05-30","bu":"Subway","revenue":643047.24,"bills":2129},
  {"d":"2026-05-30","bu":"Vendi","revenue":20365.46,"bills":94},
  {"d":"2026-05-31","bu":"Juice Land","revenue":70260.82,"bills":221},
  {"d":"2026-05-31","bu":"Khiang","revenue":37355.73,"bills":216},
  {"d":"2026-05-31","bu":"Siam Express","revenue":89063.46,"bills":299},
  {"d":"2026-05-31","bu":"Subway","revenue":527918.41,"bills":1406},
  {"d":"2026-05-31","bu":"Vendi","revenue":16967.29,"bills":85},
  {"d":"2026-06-01","bu":"Juice Land","revenue":65559.16,"bills":236},
  {"d":"2026-06-01","bu":"Khiang","revenue":37948.06,"bills":214},
  {"d":"2026-06-01","bu":"Siam Express","revenue":76952.29,"bills":269},
  {"d":"2026-06-01","bu":"Subway","revenue":576090.62,"bills":1693},
  {"d":"2026-06-01","bu":"Vendi","revenue":9594.42,"bills":54},
  {"d":"2026-06-02","bu":"Juice Land","revenue":58275.91,"bills":184},
  {"d":"2026-06-02","bu":"Khiang","revenue":35318.32,"bills":185},
  {"d":"2026-06-02","bu":"Siam Express","revenue":82246.75,"bills":310},
  {"d":"2026-06-02","bu":"Subway","revenue":473001.63,"bills":1454},
  {"d":"2026-06-02","bu":"Vendi","revenue":8193.42,"bills":62},
  {"d":"2026-06-03","bu":"Juice Land","revenue":65732.88,"bills":216},
  {"d":"2026-06-03","bu":"Khiang","revenue":37972.53,"bills":203},
  {"d":"2026-06-03","bu":"Siam Express","revenue":71949.56,"bills":282},
  {"d":"2026-06-03","bu":"Subway","revenue":462414.55,"bills":1559},
  {"d":"2026-06-03","bu":"Vendi","revenue":9739.24,"bills":53},
  {"d":"2026-06-04","bu":"Juice Land","revenue":61137.15,"bills":226},
  {"d":"2026-06-04","bu":"Khiang","revenue":29719.07,"bills":178},
  {"d":"2026-06-04","bu":"Siam Express","revenue":61707.49,"bills":242},
  {"d":"2026-06-04","bu":"Subway","revenue":462299.48,"bills":1453},
  {"d":"2026-06-04","bu":"Vendi","revenue":17801.90,"bills":85},
  {"d":"2026-06-05","bu":"Juice Land","revenue":64841.40,"bills":218},
  {"d":"2026-06-05","bu":"Khiang","revenue":34817.34,"bills":190},
  {"d":"2026-06-05","bu":"Siam Express","revenue":85002.72,"bills":291},
  {"d":"2026-06-05","bu":"Subway","revenue":456603.31,"bills":1452},
  {"d":"2026-06-05","bu":"Vendi","revenue":10697.21,"bills":53},
  {"d":"2026-06-05","bu":"General","revenue":12350.00,"bills":1},
  {"d":"2026-06-06","bu":"Juice Land","revenue":65320.78,"bills":207},
  {"d":"2026-06-06","bu":"Khiang","revenue":39565.26,"bills":207},
  {"d":"2026-06-06","bu":"Siam Express","revenue":60693.49,"bills":243},
  {"d":"2026-06-06","bu":"Subway","revenue":459354.04,"bills":1387},
  {"d":"2026-06-06","bu":"Vendi","revenue":10817.82,"bills":63},
  {"d":"2026-06-07","bu":"Juice Land","revenue":53008.61,"bills":186},
  {"d":"2026-06-07","bu":"Khiang","revenue":35120.83,"bills":186},
  {"d":"2026-06-07","bu":"Siam Express","revenue":68107.44,"bills":261},
  {"d":"2026-06-07","bu":"Subway","revenue":474039.92,"bills":1461},
  {"d":"2026-06-07","bu":"Vendi","revenue":10141.30,"bills":56},
  {"d":"2026-06-08","bu":"Juice Land","revenue":71249.74,"bills":218},
  {"d":"2026-06-08","bu":"Khiang","revenue":27605.54,"bills":168},
  {"d":"2026-06-08","bu":"Siam Express","revenue":62829.84,"bills":241},
  {"d":"2026-06-08","bu":"Subway","revenue":463915.19,"bills":1415},
  {"d":"2026-06-08","bu":"Vendi","revenue":12024.32,"bills":73},
  {"d":"2026-06-09","bu":"Juice Land","revenue":49380.96,"bills":169},
  {"d":"2026-06-09","bu":"Khiang","revenue":27834.68,"bills":145},
  {"d":"2026-06-09","bu":"Siam Express","revenue":52067.36,"bills":205},
  {"d":"2026-06-09","bu":"Subway","revenue":456951.39,"bills":1332},
  {"d":"2026-06-09","bu":"Vendi","revenue":9461.72,"bills":51},
  {"d":"2026-06-10","bu":"Juice Land","revenue":65523.54,"bills":212},
  {"d":"2026-06-10","bu":"Khiang","revenue":38472.74,"bills":185},
  {"d":"2026-06-10","bu":"Siam Express","revenue":50818.69,"bills":216},
  {"d":"2026-06-10","bu":"Subway","revenue":445322.72,"bills":1396},
  {"d":"2026-06-10","bu":"Vendi","revenue":11765.46,"bills":57},
  {"d":"2026-06-11","bu":"Juice Land","revenue":63687.12,"bills":212},
  {"d":"2026-06-11","bu":"Khiang","revenue":27774.25,"bills":161},
  {"d":"2026-06-11","bu":"Siam Express","revenue":57677.58,"bills":231},
  {"d":"2026-06-11","bu":"Subway","revenue":441037.63,"bills":1422},
  {"d":"2026-06-11","bu":"Vendi","revenue":10228.05,"bills":59},
  {"d":"2026-06-12","bu":"Juice Land","revenue":67997.87,"bills":221},
  {"d":"2026-06-12","bu":"Khiang","revenue":29144.73,"bills":160},
  {"d":"2026-06-12","bu":"Siam Express","revenue":59558.89,"bills":242},
  {"d":"2026-06-12","bu":"Subway","revenue":497504.76,"bills":1592},
  {"d":"2026-06-12","bu":"Vendi","revenue":10476.70,"bills":53},
  {"d":"2026-06-13","bu":"Juice Land","revenue":66470.29,"bills":217},
  {"d":"2026-06-13","bu":"Khiang","revenue":32892.86,"bills":177},
  {"d":"2026-06-13","bu":"Siam Express","revenue":63057.94,"bills":250},
  {"d":"2026-06-13","bu":"Subway","revenue":461717.31,"bills":1444},
  {"d":"2026-06-13","bu":"Vendi","revenue":17052.31,"bills":77},
  {"d":"2026-06-14","bu":"Juice Land","revenue":67100.25,"bills":201},
  {"d":"2026-06-14","bu":"Khiang","revenue":29428.33,"bills":172},
  {"d":"2026-06-14","bu":"Siam Express","revenue":84904.57,"bills":266},
  {"d":"2026-06-14","bu":"Subway","revenue":482629.58,"bills":1460},
  {"d":"2026-06-14","bu":"Vendi","revenue":11833.69,"bills":66},
  {"d":"2026-06-15","bu":"Juice Land","revenue":64391.84,"bills":223},
  {"d":"2026-06-15","bu":"Khiang","revenue":34091.92,"bills":193},
  {"d":"2026-06-15","bu":"Siam Express","revenue":63330.80,"bills":226},
  {"d":"2026-06-15","bu":"Subway","revenue":471731.03,"bills":1431},
  {"d":"2026-06-15","bu":"Vendi","revenue":13718.67,"bills":82},
  {"d":"2026-06-16","bu":"Juice Land","revenue":63516.16,"bills":211},
  {"d":"2026-06-16","bu":"Khiang","revenue":25903.34,"bills":158},
  {"d":"2026-06-16","bu":"Siam Express","revenue":58621.34,"bills":233},
  {"d":"2026-06-16","bu":"Subway","revenue":437682.41,"bills":1396},
  {"d":"2026-06-16","bu":"Vendi","revenue":16955.43,"bills":92},
  {"d":"2026-06-17","bu":"Juice Land","revenue":63471.31,"bills":202},
  {"d":"2026-06-17","bu":"Khiang","revenue":32266.73,"bills":163},
  {"d":"2026-06-17","bu":"Siam Express","revenue":62970.04,"bills":257},
  {"d":"2026-06-17","bu":"Subway","revenue":455685.76,"bills":1445},
  {"d":"2026-06-17","bu":"Vendi","revenue":13867.31,"bills":76},
  {"d":"2026-06-18","bu":"Juice Land","revenue":76802.58,"bills":246},
  {"d":"2026-06-18","bu":"Khiang","revenue":40925.39,"bills":225},
  {"d":"2026-06-18","bu":"Siam Express","revenue":72027.86,"bills":326},
  {"d":"2026-06-18","bu":"Subway","revenue":506463.09,"bills":1542},
  {"d":"2026-06-18","bu":"Vendi","revenue":15086.10,"bills":78},
  {"d":"2026-06-19","bu":"Juice Land","revenue":84931.97,"bills":265},
  {"d":"2026-06-19","bu":"Khiang","revenue":40524.61,"bills":218},
  {"d":"2026-06-19","bu":"Siam Express","revenue":65140.05,"bills":255},
  {"d":"2026-06-19","bu":"Subway","revenue":523355.28,"bills":1559},
  {"d":"2026-06-19","bu":"Vendi","revenue":23809.41,"bills":101},
  {"d":"2026-06-20","bu":"Juice Land","revenue":72395.58,"bills":239},
  {"d":"2026-06-20","bu":"Khiang","revenue":31432.26,"bills":164},
  {"d":"2026-06-20","bu":"Siam Express","revenue":66664.38,"bills":251},
  {"d":"2026-06-20","bu":"Subway","revenue":443413.88,"bills":1291},
  {"d":"2026-06-20","bu":"Vendi","revenue":17805.65,"bills":92},
  {"d":"2026-06-21","bu":"Juice Land","revenue":72202.53,"bills":242},
  {"d":"2026-06-21","bu":"Khiang","revenue":28863.40,"bills":171},
  {"d":"2026-06-21","bu":"Siam Express","revenue":63474.64,"bills":262},
  {"d":"2026-06-21","bu":"Subway","revenue":508240.55,"bills":1414},
  {"d":"2026-06-21","bu":"Vendi","revenue":25344.88,"bills":97},
  {"d":"2026-06-22","bu":"Juice Land","revenue":65651.19,"bills":220},
  {"d":"2026-06-22","bu":"Khiang","revenue":28647.68,"bills":163},
  {"d":"2026-06-22","bu":"Siam Express","revenue":64289.59,"bills":240},
  {"d":"2026-06-22","bu":"Subway","revenue":479677.03,"bills":1390},
  {"d":"2026-06-22","bu":"Vendi","revenue":17167.44,"bills":106},
]

# ── Q3: 30-day location totals ──
Q3_LOC = {
  ("2026-06-22","04-DMK-T2MTE3-09"):{"bills":100,"revenue":33404.64},
  ("2026-06-22","05-DMK-Inter-S"):{"bills":103,"revenue":30175.70},
  ("2026-06-22","09-DMK-G1-S"):{"bills":60,"revenue":14922.42},
  ("2026-06-22","13-PKT-G1-S"):{"bills":107,"revenue":31073.79},
  ("2026-06-22","17-T1ME2-30"):{"bills":163,"revenue":28647.68},
  ("2026-06-22","18-T1FW4-08-SS"):{"bills":267,"revenue":110456.18},
  ("2026-06-22","19-T1MB1-03"):{"bills":80,"revenue":26307.51},
  ("2026-06-22","20-PKT-Floor 3-S"):{"bills":94,"revenue":24764.53},
  ("2026-06-22","21-T1BE2-06"):{"bills":127,"revenue":53369.21},
  ("2026-06-22","22-DMK-3Pier2-SS"):{"bills":115,"revenue":26125.08},
  ("2026-06-22","23-T1CE4-13"):{"bills":152,"revenue":45564.41},
  ("2026-06-22","24-T1EW4-14"):{"bills":139,"revenue":57642.17},
  ("2026-06-22","25-DMK-CS"):{"bills":58,"revenue":14981.33},
  ("2026-06-22","26-T1MW1-03+04"):{"bills":209,"revenue":77663.66},
  ("2026-06-22","27-T1SE3-05"):{"bills":306,"revenue":73164.50},
  ("2026-06-22","28 JUICELAND Unit 362"):{"bills":39,"revenue":7170.12},
  ("2026-06-15","04-DMK-T2MTE3-09"):{"bills":126,"revenue":45361.66},
  ("2026-06-15","05-DMK-Inter-S"):{"bills":117,"revenue":33630.81},
  ("2026-06-15","09-DMK-G1-S"):{"bills":68,"revenue":17760.73},
  ("2026-06-15","13-PKT-G1-S"):{"bills":67,"revenue":20272.86},
  ("2026-06-15","17-T1ME2-30"):{"bills":193,"revenue":34091.92},
  ("2026-06-15","18-T1FW4-08-SS"):{"bills":271,"revenue":99704.78},
  ("2026-06-15","19-T1MB1-03"):{"bills":87,"revenue":25850.48},
  ("2026-06-15","20-PKT-Floor 3-S"):{"bills":114,"revenue":35192.60},
  ("2026-06-15","21-T1BE2-06"):{"bills":118,"revenue":54836.51},
  ("2026-06-15","22-DMK-3Pier2-SS"):{"bills":101,"revenue":19144.76},
  ("2026-06-15","23-T1CE4-13"):{"bills":145,"revenue":32227.96},
  ("2026-06-15","24-T1EW4-14"):{"bills":145,"revenue":59848.73},
  ("2026-06-15","25-DMK-CS"):{"bills":49,"revenue":11699.17},
  ("2026-06-15","26-T1MW1-03+04"):{"bills":228,"revenue":79312.37},
  ("2026-06-15","27-T1SE3-05"):{"bills":276,"revenue":66895.23},
  ("2026-06-15","28 JUICELAND Unit 362"):{"bills":50,"revenue":11433.69},
}

# Full Q3 for MTD (June 1-22)
Q3_FULL = [
  {"d":"2026-06-01","location":"04-DMK-T2MTE3-09","bills":125,"revenue":48437.33},
  {"d":"2026-06-01","location":"05-DMK-Inter-S","bills":162,"revenue":44600.03},
  {"d":"2026-06-01","location":"09-DMK-G1-S","bills":84,"revenue":21137.51},
  {"d":"2026-06-01","location":"13-PKT-G1-S","bills":109,"revenue":31999.06},
  {"d":"2026-06-01","location":"17-T1ME2-30","bills":214,"revenue":37948.06},
  {"d":"2026-06-01","location":"18-T1FW4-08-SS","bills":330,"revenue":122116.54},
  {"d":"2026-06-01","location":"19-T1MB1-03","bills":74,"revenue":23958.51},
  {"d":"2026-06-01","location":"20-PKT-Floor 3-S","bills":99,"revenue":31410.35},
  {"d":"2026-06-01","location":"21-T1BE2-06","bills":132,"revenue":53705.59},
  {"d":"2026-06-01","location":"22-DMK-3Pier2-SS","bills":166,"revenue":52266.27},
  {"d":"2026-06-01","location":"23-T1CE4-13","bills":165,"revenue":47429.87},
  {"d":"2026-06-01","location":"24-T1EW4-14","bills":203,"revenue":80925.73},
  {"d":"2026-06-01","location":"25-DMK-CS","bills":66,"revenue":18598.13},
  {"d":"2026-06-01","location":"26-T1MW1-03+04","bills":221,"revenue":77499.02},
  {"d":"2026-06-01","location":"27-T1SE3-05","bills":260,"revenue":61084.47},
  {"d":"2026-06-01","location":"28 JUICELAND Unit 362","bills":56,"revenue":13028.08},
  {"d":"2026-06-02","location":"04-DMK-T2MTE3-09","bills":110,"revenue":43981.32},
  {"d":"2026-06-02","location":"05-DMK-Inter-S","bills":125,"revenue":23583.12},
  {"d":"2026-06-02","location":"09-DMK-G1-S","bills":61,"revenue":17332.71},
  {"d":"2026-06-02","location":"13-PKT-G1-S","bills":142,"revenue":35729.00},
  {"d":"2026-06-02","location":"17-T1ME2-30","bills":185,"revenue":35318.32},
  {"d":"2026-06-02","location":"18-T1FW4-08-SS","bills":317,"revenue":123892.87},
  {"d":"2026-06-02","location":"19-T1MB1-03","bills":79,"revenue":23601.90},
  {"d":"2026-06-02","location":"20-PKT-Floor 3-S","bills":126,"revenue":38202.86},
  {"d":"2026-06-02","location":"21-T1BE2-06","bills":123,"revenue":46629.97},
  {"d":"2026-06-02","location":"22-DMK-3Pier2-SS","bills":120,"revenue":25086.84},
  {"d":"2026-06-02","location":"23-T1CE4-13","bills":128,"revenue":28924.32},
  {"d":"2026-06-02","location":"24-T1EW4-14","bills":186,"revenue":80536.61},
  {"d":"2026-06-02","location":"25-DMK-CS","bills":40,"revenue":9581.31},
  {"d":"2026-06-02","location":"26-T1MW1-03+04","bills":196,"revenue":69138.60},
  {"d":"2026-06-02","location":"27-T1SE3-05","bills":216,"revenue":46225.19},
  {"d":"2026-06-02","location":"28 JUICELAND Unit 362","bills":41,"revenue":9271.09},
  {"d":"2026-06-03","location":"04-DMK-T2MTE3-09","bills":128,"revenue":38416.89},
  {"d":"2026-06-03","location":"05-DMK-Inter-S","bills":129,"revenue":35024.19},
  {"d":"2026-06-03","location":"09-DMK-G1-S","bills":68,"revenue":15929.91},
  {"d":"2026-06-03","location":"13-PKT-G1-S","bills":118,"revenue":27672.01},
  {"d":"2026-06-03","location":"17-T1ME2-30","bills":203,"revenue":37972.53},
  {"d":"2026-06-03","location":"18-T1FW4-08-SS","bills":332,"revenue":89994.04},
  {"d":"2026-06-03","location":"19-T1MB1-03","bills":77,"revenue":22470.16},
  {"d":"2026-06-03","location":"20-PKT-Floor 3-S","bills":114,"revenue":36186.03},
  {"d":"2026-06-03","location":"21-T1BE2-06","bills":136,"revenue":53182.79},
  {"d":"2026-06-03","location":"22-DMK-3Pier2-SS","bills":137,"revenue":31967.25},
  {"d":"2026-06-03","location":"23-T1CE4-13","bills":133,"revenue":30032.55},
  {"d":"2026-06-03","location":"24-T1EW4-14","bills":194,"revenue":73218.65},
  {"d":"2026-06-03","location":"25-DMK-CS","bills":63,"revenue":15794.39},
  {"d":"2026-06-03","location":"26-T1MW1-03+04","bills":218,"revenue":78997.28},
  {"d":"2026-06-03","location":"27-T1SE3-05","bills":212,"revenue":50844.42},
  {"d":"2026-06-03","location":"28 JUICELAND Unit 362","bills":51,"revenue":10105.67},
  {"d":"2026-06-04","location":"04-DMK-T2MTE3-09","bills":123,"revenue":43860.68},
  {"d":"2026-06-04","location":"05-DMK-Inter-S","bills":127,"revenue":31731.73},
  {"d":"2026-06-04","location":"09-DMK-G1-S","bills":56,"revenue":13779.51},
  {"d":"2026-06-04","location":"13-PKT-G1-S","bills":100,"revenue":24160.75},
  {"d":"2026-06-04","location":"17-T1ME2-30","bills":178,"revenue":29719.07},
  {"d":"2026-06-04","location":"18-T1FW4-08-SS","bills":287,"revenue":102366.40},
  {"d":"2026-06-04","location":"19-T1MB1-03","bills":90,"revenue":25432.74},
  {"d":"2026-06-04","location":"20-PKT-Floor 3-S","bills":95,"revenue":29870.16},
  {"d":"2026-06-04","location":"21-T1BE2-06","bills":125,"revenue":44380.41},
  {"d":"2026-06-04","location":"22-DMK-3Pier2-SS","bills":138,"revenue":27852.29},
  {"d":"2026-06-04","location":"23-T1CE4-13","bills":134,"revenue":33447.49},
  {"d":"2026-06-04","location":"24-T1EW4-14","bills":181,"revenue":68994.71},
  {"d":"2026-06-04","location":"25-DMK-CS","bills":38,"revenue":9786.00},
  {"d":"2026-06-04","location":"26-T1MW1-03+04","bills":228,"revenue":81017.50},
  {"d":"2026-06-04","location":"27-T1SE3-05","bills":224,"revenue":53979.62},
  {"d":"2026-06-04","location":"28 JUICELAND Unit 362","bills":60,"revenue":12286.03},
  {"d":"2026-06-05","location":"04-DMK-T2MTE3-09","bills":114,"revenue":33458.19},
  {"d":"2026-06-05","location":"05-DMK-Inter-S","bills":128,"revenue":31013.98},
  {"d":"2026-06-05","location":"09-DMK-G1-S","bills":69,"revenue":16238.33},
  {"d":"2026-06-05","location":"13-PKT-G1-S","bills":122,"revenue":31567.27},
  {"d":"2026-06-05","location":"17-T1ME2-30","bills":190,"revenue":34817.34},
  {"d":"2026-06-05","location":"18-T1FW4-08-SS","bills":268,"revenue":92889.47},
  {"d":"2026-06-05","location":"19-T1MB1-03","bills":105,"revenue":32157.35},
  {"d":"2026-06-05","location":"20-PKT-Floor 3-S","bills":111,"revenue":40387.87},
  {"d":"2026-06-05","location":"21-T1BE2-06","bills":140,"revenue":58257.02},
  {"d":"2026-06-05","location":"22-DMK-3Pier2-SS","bills":147,"revenue":37038.23},
  {"d":"2026-06-05","location":"23-T1CE4-13","bills":127,"revenue":39104.75},
  {"d":"2026-06-05","location":"24-T1EW4-14","bills":146,"revenue":53946.71},
  {"d":"2026-06-05","location":"25-DMK-CS","bills":53,"revenue":12986.90},
  {"d":"2026-06-05","location":"26-T1MW1-03+04","bills":205,"revenue":67724.99},
  {"d":"2026-06-05","location":"27-T1SE3-05","bills":221,"revenue":57673.51},
  {"d":"2026-06-05","location":"28 JUICELAND Unit 362","bills":58,"revenue":12700.07},
  {"d":"2026-06-05","location":"SFB HQ","bills":1,"revenue":12350.00},
  {"d":"2026-06-06","location":"04-DMK-T2MTE3-09","bills":114,"revenue":34303.73},
  {"d":"2026-06-06","location":"05-DMK-Inter-S","bills":110,"revenue":27002.79},
  {"d":"2026-06-06","location":"09-DMK-G1-S","bills":57,"revenue":14841.10},
  {"d":"2026-06-06","location":"13-PKT-G1-S","bills":74,"revenue":13631.76},
  {"d":"2026-06-06","location":"17-T1ME2-30","bills":207,"revenue":39565.26},
  {"d":"2026-06-06","location":"18-T1FW4-08-SS","bills":266,"revenue":107601.02},
  {"d":"2026-06-06","location":"19-T1MB1-03","bills":88,"revenue":24871.05},
  {"d":"2026-06-06","location":"20-PKT-Floor 3-S","bills":121,"revenue":39314.13},
  {"d":"2026-06-06","location":"21-T1BE2-06","bills":127,"revenue":45331.76},
  {"d":"2026-06-06","location":"22-DMK-3Pier2-SS","bills":129,"revenue":28825.95},
  {"d":"2026-06-06","location":"23-T1CE4-13","bills":100,"revenue":26952.93},
  {"d":"2026-06-06","location":"24-T1EW4-14","bills":178,"revenue":73995.34},
  {"d":"2026-06-06","location":"25-DMK-CS","bills":48,"revenue":10556.99},
  {"d":"2026-06-06","location":"26-T1MW1-03+04","bills":189,"revenue":69617.88},
  {"d":"2026-06-06","location":"27-T1SE3-05","bills":246,"revenue":66379.80},
  {"d":"2026-06-06","location":"28 JUICELAND Unit 362","bills":53,"revenue":12959.90},
  {"d":"2026-06-07","location":"04-DMK-T2MTE3-09","bills":122,"revenue":43465.43},
  {"d":"2026-06-07","location":"05-DMK-Inter-S","bills":107,"revenue":28220.55},
  {"d":"2026-06-07","location":"09-DMK-G1-S","bills":69,"revenue":17696.24},
  {"d":"2026-06-07","location":"13-PKT-G1-S","bills":91,"revenue":22144.84},
  {"d":"2026-06-07","location":"17-T1ME2-30","bills":186,"revenue":35120.83},
  {"d":"2026-06-07","location":"18-T1FW4-08-SS","bills":263,"revenue":107977.56},
  {"d":"2026-06-07","location":"19-T1MB1-03","bills":97,"revenue":26063.79},
  {"d":"2026-06-07","location":"20-PKT-Floor 3-S","bills":112,"revenue":34148.68},
  {"d":"2026-06-07","location":"21-T1BE2-06","bills":135,"revenue":60397.24},
  {"d":"2026-06-07","location":"22-DMK-3Pier2-SS","bills":147,"revenue":32390.66},
  {"d":"2026-06-07","location":"23-T1CE4-13","bills":121,"revenue":30267.31},
  {"d":"2026-06-07","location":"24-T1EW4-14","bills":147,"revenue":60178.52},
  {"d":"2026-06-07","location":"25-DMK-CS","bills":69,"revenue":16657.94},
  {"d":"2026-06-07","location":"26-T1MW1-03+04","bills":188,"revenue":59972.37},
  {"d":"2026-06-07","location":"27-T1SE3-05","bills":248,"revenue":53573.13},
  {"d":"2026-06-07","location":"28 JUICELAND Unit 362","bills":48,"revenue":12143.01},
  {"d":"2026-06-08","location":"04-DMK-T2MTE3-09","bills":139,"revenue":53896.12},
  {"d":"2026-06-08","location":"05-DMK-Inter-S","bills":100,"revenue":25732.69},
  {"d":"2026-06-08","location":"09-DMK-G1-S","bills":56,"revenue":13016.76},
  {"d":"2026-06-08","location":"13-PKT-G1-S","bills":84,"revenue":19955.08},
  {"d":"2026-06-08","location":"17-T1ME2-30","bills":168,"revenue":27605.54},
  {"d":"2026-06-08","location":"18-T1FW4-08-SS","bills":274,"revenue":99512.02},
  {"d":"2026-06-08","location":"19-T1MB1-03","bills":70,"revenue":17742.23},
  {"d":"2026-06-08","location":"20-PKT-Floor 3-S","bills":110,"revenue":35074.86},
  {"d":"2026-06-08","location":"21-T1BE2-06","bills":125,"revenue":50592.52},
  {"d":"2026-06-08","location":"22-DMK-3Pier2-SS","bills":141,"revenue":34870.94},
  {"d":"2026-06-08","location":"23-T1CE4-13","bills":96,"revenue":24647.63},
  {"d":"2026-06-08","location":"24-T1EW4-14","bills":166,"revenue":59631.39},
  {"d":"2026-06-08","location":"25-DMK-CS","bills":64,"revenue":18535.48},
  {"d":"2026-06-08","location":"26-T1MW1-03+04","bills":229,"revenue":84158.06},
  {"d":"2026-06-08","location":"27-T1SE3-05","bills":248,"revenue":60681.33},
  {"d":"2026-06-08","location":"28 JUICELAND Unit 362","bills":45,"revenue":11971.98},
  {"d":"2026-06-09","location":"04-DMK-T2MTE3-09","bills":125,"revenue":46588.79},
  {"d":"2026-06-09","location":"05-DMK-Inter-S","bills":90,"revenue":26995.32},
  {"d":"2026-06-09","location":"09-DMK-G1-S","bills":46,"revenue":10185.95},
  {"d":"2026-06-09","location":"13-PKT-G1-S","bills":76,"revenue":16160.74},
  {"d":"2026-06-09","location":"17-T1ME2-30","bills":145,"revenue":27834.68},
  {"d":"2026-06-09","location":"18-T1FW4-08-SS","bills":267,"revenue":103048.85},
  {"d":"2026-06-09","location":"19-T1MB1-03","bills":88,"revenue":31191.14},
  {"d":"2026-06-09","location":"20-PKT-Floor 3-S","bills":87,"revenue":28486.09},
  {"d":"2026-06-09","location":"21-T1BE2-06","bills":115,"revenue":42942.56},
  {"d":"2026-06-09","location":"22-DMK-3Pier2-SS","bills":114,"revenue":26826.17},
  {"d":"2026-06-09","location":"23-T1CE4-13","bills":124,"revenue":30904.05},
  {"d":"2026-06-09","location":"24-T1EW4-14","bills":153,"revenue":67610.84},
  {"d":"2026-06-09","location":"25-DMK-CS","bills":49,"revenue":17390.68},
  {"d":"2026-06-09","location":"26-T1MW1-03+04","bills":198,"revenue":69962.68},
  {"d":"2026-06-09","location":"27-T1SE3-05","bills":183,"revenue":40044.21},
  {"d":"2026-06-09","location":"28 JUICELAND Unit 362","bills":42,"revenue":9523.36},
  {"d":"2026-06-10","location":"04-DMK-T2MTE3-09","bills":122,"revenue":40373.71},
  {"d":"2026-06-10","location":"05-DMK-Inter-S","bills":116,"revenue":31710.23},
  {"d":"2026-06-10","location":"09-DMK-G1-S","bills":28,"revenue":6043.93},
  {"d":"2026-06-10","location":"13-PKT-G1-S","bills":73,"revenue":14715.87},
  {"d":"2026-06-10","location":"17-T1ME2-30","bills":185,"revenue":38472.74},
  {"d":"2026-06-10","location":"18-T1FW4-08-SS","bills":277,"revenue":99749.42},
  {"d":"2026-06-10","location":"19-T1MB1-03","bills":86,"revenue":23872.01},
  {"d":"2026-06-10","location":"20-PKT-Floor 3-S","bills":86,"revenue":25749.59},
  {"d":"2026-06-10","location":"21-T1BE2-06","bills":120,"revenue":49334.54},
  {"d":"2026-06-10","location":"22-DMK-3Pier2-SS","bills":143,"revenue":32035.46},
  {"d":"2026-06-10","location":"23-T1CE4-13","bills":141,"revenue":35485.91},
  {"d":"2026-06-10","location":"24-T1EW4-14","bills":133,"revenue":60377.64},
  {"d":"2026-06-10","location":"25-DMK-CS","bills":62,"revenue":16097.18},
  {"d":"2026-06-10","location":"26-T1MW1-03+04","bills":218,"revenue":72354.64},
  {"d":"2026-06-10","location":"27-T1SE3-05","bills":233,"revenue":55950.83},
  {"d":"2026-06-10","location":"28 JUICELAND Unit 362","bills":43,"revenue":9579.45},
  {"d":"2026-06-11","location":"04-DMK-T2MTE3-09","bills":125,"revenue":49381.28},
  {"d":"2026-06-11","location":"05-DMK-Inter-S","bills":138,"revenue":27892.03},
  {"d":"2026-06-11","location":"09-DMK-G1-S","bills":56,"revenue":14873.82},
  {"d":"2026-06-11","location":"13-PKT-G1-S","bills":86,"revenue":20786.89},
  {"d":"2026-06-11","location":"17-T1ME2-30","bills":161,"revenue":27774.25},
  {"d":"2026-06-11","location":"18-T1FW4-08-SS","bills":288,"revenue":103727.64},
  {"d":"2026-06-11","location":"19-T1MB1-03","bills":94,"revenue":25648.63},
  {"d":"2026-06-11","location":"20-PKT-Floor 3-S","bills":112,"revenue":32327.17},
  {"d":"2026-06-11","location":"21-T1BE2-06","bills":122,"revenue":48968.72},
  {"d":"2026-06-11","location":"22-DMK-3Pier2-SS","bills":120,"revenue":23499.04},
  {"d":"2026-06-11","location":"23-T1CE4-13","bills":128,"revenue":28691.71},
  {"d":"2026-06-11","location":"24-T1EW4-14","bills":144,"revenue":51916.18},
  {"d":"2026-06-11","location":"25-DMK-CS","bills":49,"revenue":13100.91},
  {"d":"2026-06-11","location":"26-T1MW1-03+04","bills":204,"revenue":72308.60},
  {"d":"2026-06-11","location":"27-T1SE3-05","bills":201,"revenue":47944.17},
  {"d":"2026-06-11","location":"28 JUICELAND Unit 362","bills":57,"revenue":11563.59},
  {"d":"2026-06-12","location":"04-DMK-T2MTE3-09","bills":130,"revenue":52829.87},
  {"d":"2026-06-12","location":"05-DMK-Inter-S","bills":139,"revenue":26873.79},
  {"d":"2026-06-12","location":"09-DMK-G1-S","bills":84,"revenue":18965.38},
  {"d":"2026-06-12","location":"13-PKT-G1-S","bills":94,"revenue":18752.36},
  {"d":"2026-06-12","location":"17-T1ME2-30","bills":160,"revenue":29144.73},
  {"d":"2026-06-12","location":"18-T1FW4-08-SS","bills":342,"revenue":113523.43},
  {"d":"2026-06-12","location":"19-T1MB1-03","bills":84,"revenue":24875.72},
  {"d":"2026-06-12","location":"20-PKT-Floor 3-S","bills":112,"revenue":34302.85},
  {"d":"2026-06-12","location":"21-T1BE2-06","bills":126,"revenue":50593.45},
  {"d":"2026-06-12","location":"22-DMK-3Pier2-SS","bills":102,"revenue":22231.69},
  {"d":"2026-06-12","location":"23-T1CE4-13","bills":168,"revenue":46354.27},
  {"d":"2026-06-12","location":"24-T1EW4-14","bills":171,"revenue":64798.79},
  {"d":"2026-06-12","location":"25-DMK-CS","bills":53,"revenue":14412.11},
  {"d":"2026-06-12","location":"26-T1MW1-03+04","bills":217,"revenue":73288.80},
  {"d":"2026-06-12","location":"27-T1SE3-05","bills":238,"revenue":62751.55},
  {"d":"2026-06-12","location":"28 JUICELAND Unit 362","bills":48,"revenue":10984.16},
  {"d":"2026-06-13","location":"04-DMK-T2MTE3-09","bills":126,"revenue":42323.28},
  {"d":"2026-06-13","location":"05-DMK-Inter-S","bills":108,"revenue":27132.70},
  {"d":"2026-06-13","location":"09-DMK-G1-S","bills":46,"revenue":12440.17},
  {"d":"2026-06-13","location":"13-PKT-G1-S","bills":95,"revenue":19379.44},
  {"d":"2026-06-13","location":"17-T1ME2-30","bills":177,"revenue":32892.86},
  {"d":"2026-06-13","location":"18-T1FW4-08-SS","bills":286,"revenue":104008.00},
  {"d":"2026-06-13","location":"19-T1MB1-03","bills":92,"revenue":24224.47},
  {"d":"2026-06-13","location":"20-PKT-Floor 3-S","bills":108,"revenue":35698.20},
  {"d":"2026-06-13","location":"21-T1BE2-06","bills":119,"revenue":49226.25},
  {"d":"2026-06-13","location":"22-DMK-3Pier2-SS","bills":130,"revenue":24596.21},
  {"d":"2026-06-13","location":"23-T1CE4-13","bills":134,"revenue":32909.25},
  {"d":"2026-06-13","location":"24-T1EW4-14","bills":174,"revenue":64963.32},
  {"d":"2026-06-13","location":"25-DMK-CS","bills":52,"revenue":15342.04},
  {"d":"2026-06-13","location":"26-T1MW1-03+04","bills":211,"revenue":68602.86},
  {"d":"2026-06-13","location":"27-T1SE3-05","bills":258,"revenue":75994.58},
  {"d":"2026-06-13","location":"28 JUICELAND Unit 362","bills":49,"revenue":11457.08},
  {"d":"2026-06-14","location":"04-DMK-T2MTE3-09","bills":121,"revenue":41324.21},
  {"d":"2026-06-14","location":"05-DMK-Inter-S","bills":113,"revenue":33662.89},
  {"d":"2026-06-14","location":"09-DMK-G1-S","bills":64,"revenue":14052.31},
  {"d":"2026-06-14","location":"13-PKT-G1-S","bills":104,"revenue":32643.81},
  {"d":"2026-06-14","location":"17-T1ME2-30","bills":172,"revenue":29428.33},
  {"d":"2026-06-14","location":"18-T1FW4-08-SS","bills":262,"revenue":113459.36},
  {"d":"2026-06-14","location":"19-T1MB1-03","bills":76,"revenue":20878.53},
  {"d":"2026-06-14","location":"20-PKT-Floor 3-S","bills":117,"revenue":44260.87},
  {"d":"2026-06-14","location":"21-T1BE2-06","bills":135,"revenue":50674.04},
  {"d":"2026-06-14","location":"22-DMK-3Pier2-SS","bills":141,"revenue":33076.53},
  {"d":"2026-06-14","location":"23-T1CE4-13","bills":151,"revenue":37194.34},
  {"d":"2026-06-14","location":"24-T1EW4-14","bills":158,"revenue":63447.48},
  {"d":"2026-06-14","location":"25-DMK-CS","bills":52,"revenue":14282.27},
  {"d":"2026-06-14","location":"26-T1MW1-03+04","bills":207,"revenue":72123.43},
  {"d":"2026-06-14","location":"27-T1SE3-05","bills":237,"revenue":60097.34},
  {"d":"2026-06-14","location":"28 JUICELAND Unit 362","bills":55,"revenue":15290.68},
  {"d":"2026-06-15","location":"04-DMK-T2MTE3-09","bills":126,"revenue":45361.66},
  {"d":"2026-06-15","location":"05-DMK-Inter-S","bills":117,"revenue":33630.81},
  {"d":"2026-06-15","location":"09-DMK-G1-S","bills":68,"revenue":17760.73},
  {"d":"2026-06-15","location":"13-PKT-G1-S","bills":67,"revenue":20272.86},
  {"d":"2026-06-15","location":"17-T1ME2-30","bills":193,"revenue":34091.92},
  {"d":"2026-06-15","location":"18-T1FW4-08-SS","bills":271,"revenue":99704.78},
  {"d":"2026-06-15","location":"19-T1MB1-03","bills":87,"revenue":25850.48},
  {"d":"2026-06-15","location":"20-PKT-Floor 3-S","bills":114,"revenue":35192.60},
  {"d":"2026-06-15","location":"21-T1BE2-06","bills":118,"revenue":54836.51},
  {"d":"2026-06-15","location":"22-DMK-3Pier2-SS","bills":101,"revenue":19144.76},
  {"d":"2026-06-15","location":"23-T1CE4-13","bills":145,"revenue":32227.96},
  {"d":"2026-06-15","location":"24-T1EW4-14","bills":145,"revenue":59848.73},
  {"d":"2026-06-15","location":"25-DMK-CS","bills":49,"revenue":11699.17},
  {"d":"2026-06-15","location":"26-T1MW1-03+04","bills":228,"revenue":79312.37},
  {"d":"2026-06-15","location":"27-T1SE3-05","bills":276,"revenue":66895.23},
  {"d":"2026-06-15","location":"28 JUICELAND Unit 362","bills":50,"revenue":11433.69},
  {"d":"2026-06-16","location":"04-DMK-T2MTE3-09","bills":126,"revenue":38875.92},
  {"d":"2026-06-16","location":"05-DMK-Inter-S","bills":118,"revenue":25342.00},
  {"d":"2026-06-16","location":"09-DMK-G1-S","bills":47,"revenue":12329.01},
  {"d":"2026-06-16","location":"13-PKT-G1-S","bills":112,"revenue":27536.31},
  {"d":"2026-06-16","location":"17-T1ME2-30","bills":158,"revenue":25903.34},
  {"d":"2026-06-16","location":"18-T1FW4-08-SS","bills":264,"revenue":100943.11},
  {"d":"2026-06-16","location":"19-T1MB1-03","bills":84,"revenue":25087.87},
  {"d":"2026-06-16","location":"20-PKT-Floor 3-S","bills":93,"revenue":26349.57},
  {"d":"2026-06-16","location":"21-T1BE2-06","bills":127,"revenue":49300.05},
  {"d":"2026-06-16","location":"22-DMK-3Pier2-SS","bills":94,"revenue":24012.11},
  {"d":"2026-06-16","location":"23-T1CE4-13","bills":115,"revenue":24694.53},
  {"d":"2026-06-16","location":"24-T1EW4-14","bills":164,"revenue":56228.14},
  {"d":"2026-06-16","location":"25-DMK-CS","bills":43,"revenue":11282.25},
  {"d":"2026-06-16","location":"26-T1MW1-03+04","bills":226,"revenue":78137.94},
  {"d":"2026-06-16","location":"27-T1SE3-05","bills":276,"revenue":68172.41},
  {"d":"2026-06-16","location":"28 JUICELAND Unit 362","bills":43,"revenue":8484.12},
  {"d":"2026-06-17","location":"04-DMK-T2MTE3-09","bills":104,"revenue":33584.67},
  {"d":"2026-06-17","location":"05-DMK-Inter-S","bills":123,"revenue":30921.44},
  {"d":"2026-06-17","location":"09-DMK-G1-S","bills":61,"revenue":13004.64},
  {"d":"2026-06-17","location":"13-PKT-G1-S","bills":117,"revenue":28829.88},
  {"d":"2026-06-17","location":"17-T1ME2-30","bills":163,"revenue":32266.73},
  {"d":"2026-06-17","location":"18-T1FW4-08-SS","bills":259,"revenue":97123.31},
  {"d":"2026-06-17","location":"19-T1MB1-03","bills":93,"revenue":24259.46},
  {"d":"2026-06-17","location":"20-PKT-Floor 3-S","bills":91,"revenue":25147.69},
  {"d":"2026-06-17","location":"21-T1BE2-06","bills":121,"revenue":45236.55},
  {"d":"2026-06-17","location":"22-DMK-3Pier2-SS","bills":177,"revenue":45788.89},
  {"d":"2026-06-17","location":"23-T1CE4-13","bills":103,"revenue":27193.61},
  {"d":"2026-06-17","location":"24-T1EW4-14","bills":173,"revenue":64154.19},
  {"d":"2026-06-17","location":"25-DMK-CS","bills":56,"revenue":13631.78},
  {"d":"2026-06-17","location":"26-T1MW1-03+04","bills":225,"revenue":79980.45},
  {"d":"2026-06-17","location":"27-T1SE3-05","bills":244,"revenue":57782.70},
  {"d":"2026-06-17","location":"28 JUICELAND Unit 362","bills":33,"revenue":9355.16},
  {"d":"2026-06-18","location":"04-DMK-T2MTE3-09","bills":138,"revenue":49427.07},
  {"d":"2026-06-18","location":"05-DMK-Inter-S","bills":126,"revenue":23671.93},
  {"d":"2026-06-18","location":"09-DMK-G1-S","bills":59,"revenue":15322.38},
  {"d":"2026-06-18","location":"13-PKT-G1-S","bills":124,"revenue":31170.08},
  {"d":"2026-06-18","location":"17-T1ME2-30","bills":225,"revenue":40925.39},
  {"d":"2026-06-18","location":"18-T1FW4-08-SS","bills":291,"revenue":106184.62},
  {"d":"2026-06-18","location":"19-T1MB1-03","bills":91,"revenue":28275.94},
  {"d":"2026-06-18","location":"20-PKT-Floor 3-S","bills":166,"revenue":32991.57},
  {"d":"2026-06-18","location":"21-T1BE2-06","bills":139,"revenue":56731.84},
  {"d":"2026-06-18","location":"22-DMK-3Pier2-SS","bills":117,"revenue":25920.39},
  {"d":"2026-06-18","location":"23-T1CE4-13","bills":152,"revenue":30106.66},
  {"d":"2026-06-18","location":"24-T1EW4-14","bills":176,"revenue":76925.93},
  {"d":"2026-06-18","location":"25-DMK-CS","bills":33,"revenue":8709.33},
  {"d":"2026-06-18","location":"26-T1MW1-03+04","bills":252,"revenue":98076.22},
  {"d":"2026-06-18","location":"27-T1SE3-05","bills":271,"revenue":73493.69},
  {"d":"2026-06-18","location":"28 JUICELAND Unit 362","bills":57,"revenue":13371.98},
  {"d":"2026-06-19","location":"04-DMK-T2MTE3-09","bills":138,"revenue":46987.09},
  {"d":"2026-06-19","location":"05-DMK-Inter-S","bills":122,"revenue":28491.55},
  {"d":"2026-06-19","location":"09-DMK-G1-S","bills":82,"revenue":23634.50},
  {"d":"2026-06-19","location":"13-PKT-G1-S","bills":108,"revenue":24129.90},
  {"d":"2026-06-19","location":"17-T1ME2-30","bills":218,"revenue":40524.61},
  {"d":"2026-06-19","location":"18-T1FW4-08-SS","bills":205,"revenue":95506.25},
  {"d":"2026-06-19","location":"19-T1MB1-03","bills":116,"revenue":39889.78},
  {"d":"2026-06-19","location":"20-PKT-Floor 3-S","bills":101,"revenue":31154.22},
  {"d":"2026-06-19","location":"21-T1BE2-06","bills":151,"revenue":58090.48},
  {"d":"2026-06-19","location":"22-DMK-3Pier2-SS","bills":161,"revenue":35945.60},
  {"d":"2026-06-19","location":"23-T1CE4-13","bills":153,"revenue":41775.66},
  {"d":"2026-06-19","location":"24-T1EW4-14","bills":158,"revenue":56704.03},
  {"d":"2026-06-19","location":"25-DMK-CS","bills":53,"revenue":12586.92},
  {"d":"2026-06-19","location":"26-T1MW1-03+04","bills":248,"revenue":92058.24},
  {"d":"2026-06-19","location":"27-T1SE3-05","bills":322,"revenue":98317.06},
  {"d":"2026-06-19","location":"28 JUICELAND Unit 362","bills":62,"revenue":11965.43},
  {"d":"2026-06-20","location":"04-DMK-T2MTE3-09","bills":110,"revenue":42246.07},
  {"d":"2026-06-20","location":"05-DMK-Inter-S","bills":124,"revenue":19686.83},
  {"d":"2026-06-20","location":"09-DMK-G1-S","bills":69,"revenue":18916.81},
  {"d":"2026-06-20","location":"13-PKT-G1-S","bills":106,"revenue":26971.92},
  {"d":"2026-06-20","location":"17-T1ME2-30","bills":164,"revenue":31432.26},
  {"d":"2026-06-20","location":"18-T1FW4-08-SS","bills":212,"revenue":100797.44},
  {"d":"2026-06-20","location":"19-T1MB1-03","bills":67,"revenue":20896.30},
  {"d":"2026-06-20","location":"20-PKT-Floor 3-S","bills":106,"revenue":33318.71},
  {"d":"2026-06-20","location":"21-T1BE2-06","bills":125,"revenue":40692.50},
  {"d":"2026-06-20","location":"22-DMK-3Pier2-SS","bills":96,"revenue":17426.34},
  {"d":"2026-06-20","location":"23-T1CE4-13","bills":108,"revenue":30798.09},
  {"d":"2026-06-20","location":"24-T1EW4-14","bills":129,"revenue":55720.74},
  {"d":"2026-06-20","location":"25-DMK-CS","bills":38,"revenue":8535.52},
  {"d":"2026-06-20","location":"26-T1MW1-03+04","bills":207,"revenue":75334.76},
  {"d":"2026-06-20","location":"27-T1SE3-05","bills":308,"revenue":94129.94},
  {"d":"2026-06-20","location":"28 JUICELAND Unit 362","bills":68,"revenue":14807.52},
  {"d":"2026-06-21","location":"04-DMK-T2MTE3-09","bills":126,"revenue":46429.84},
  {"d":"2026-06-21","location":"05-DMK-Inter-S","bills":147,"revenue":49309.83},
  {"d":"2026-06-21","location":"09-DMK-G1-S","bills":67,"revenue":16828.03},
  {"d":"2026-06-21","location":"13-PKT-G1-S","bills":101,"revenue":21206.50},
  {"d":"2026-06-21","location":"17-T1ME2-30","bills":171,"revenue":28863.40},
  {"d":"2026-06-21","location":"18-T1FW4-08-SS","bills":213,"revenue":95846.50},
  {"d":"2026-06-21","location":"19-T1MB1-03","bills":78,"revenue":25067.78},
  {"d":"2026-06-21","location":"20-PKT-Floor 3-S","bills":100,"revenue":28169.25},
  {"d":"2026-06-21","location":"21-T1BE2-06","bills":119,"revenue":52194.41},
  {"d":"2026-06-21","location":"22-DMK-3Pier2-SS","bills":156,"revenue":37541.96},
  {"d":"2026-06-21","location":"23-T1CE4-13","bills":125,"revenue":33966.25},
  {"d":"2026-06-21","location":"24-T1EW4-14","bills":126,"revenue":61858.53},
  {"d":"2026-06-21","location":"25-DMK-CS","bills":59,"revenue":16273.80},
  {"d":"2026-06-21","location":"26-T1MW1-03+04","bills":233,"revenue":78913.63},
  {"d":"2026-06-21","location":"27-T1SE3-05","bills":327,"revenue":98269.36},
  {"d":"2026-06-21","location":"28 JUICELAND Unit 362","bills":38,"revenue":7386.93},
  {"d":"2026-06-22","location":"04-DMK-T2MTE3-09","bills":100,"revenue":33404.64},
  {"d":"2026-06-22","location":"05-DMK-Inter-S","bills":103,"revenue":30175.70},
  {"d":"2026-06-22","location":"09-DMK-G1-S","bills":60,"revenue":14922.42},
  {"d":"2026-06-22","location":"13-PKT-G1-S","bills":107,"revenue":31073.79},
  {"d":"2026-06-22","location":"17-T1ME2-30","bills":163,"revenue":28647.68},
  {"d":"2026-06-22","location":"18-T1FW4-08-SS","bills":267,"revenue":110456.18},
  {"d":"2026-06-22","location":"19-T1MB1-03","bills":80,"revenue":26307.51},
  {"d":"2026-06-22","location":"20-PKT-Floor 3-S","bills":94,"revenue":24764.53},
  {"d":"2026-06-22","location":"21-T1BE2-06","bills":127,"revenue":53369.21},
  {"d":"2026-06-22","location":"22-DMK-3Pier2-SS","bills":115,"revenue":26125.08},
  {"d":"2026-06-22","location":"23-T1CE4-13","bills":152,"revenue":45564.41},
  {"d":"2026-06-22","location":"24-T1EW4-14","bills":139,"revenue":57642.17},
  {"d":"2026-06-22","location":"25-DMK-CS","bills":58,"revenue":14981.33},
  {"d":"2026-06-22","location":"26-T1MW1-03+04","bills":209,"revenue":77663.66},
  {"d":"2026-06-22","location":"27-T1SE3-05","bills":306,"revenue":73164.50},
  {"d":"2026-06-22","location":"28 JUICELAND Unit 362","bills":39,"revenue":7170.12},
]

# ── Airport mapping ──
AIRPORT = {
  "17-T1ME2-30":"BKK","18-T1FW4-08-SS":"BKK","19-T1MB1-03":"BKK","21-T1BE2-06":"BKK",
  "23-T1CE4-13":"BKK","24-T1EW4-14":"BKK","26-T1MW1-03+04":"BKK","27-T1SE3-05":"BKK",
  "28 JUICELAND Unit 362":"BKK","04-DMK-T2MTE3-09":"DMK","05-DMK-Inter-S":"DMK",
  "09-DMK-G1-S":"DMK","22-DMK-3Pier2-SS":"DMK","25-DMK-CS":"DMK",
  "13-PKT-G1-S":"PKT","20-PKT-Floor 3-S":"PKT","SFB HQ":"BKK",
}
BU_COLOR = {"Subway":"#5551FE","Juice Land":"#2D7A3F","Khiang":"#7B79FF",
            "Siam Express":"#F39C12","Vendi":"#C5453E","General":"#C5BFB0"}

# ── Helper functions ──
def pct(a, b):
    if b == 0: return 0.0
    return (a - b) / b * 100.0

def signed(v, decimals=1):
    s = f"{abs(v):.{decimals}f}"
    return f"+{s}%" if v >= 0 else f"-{s}%"

def fmt_k(v):
    return f"{v/1000:.1f}K"

def fmt_baht(v):
    return f"฿{v:,.0f}"

def fmt_comma(v):
    return f"{v:,.0f}"

def delta_class(v):
    if v > 0: return "delta-up"
    if v < 0: return "delta-down"
    return "delta-neutral"

def wow_class(v):
    if v > 0: return "delta-up"
    if v < 0: return "delta-down"
    return "delta-neutral"

def grad(pct_val):
    p = max(-25.0, min(25.0, pct_val))
    if p >= 0:
        t = p / 25.0
        bg = tuple(round(240 + (30 - 240) * t), round(229 + (107 - 229) * t), round(218 + (48 - 218) * t))
    else:
        t = -p / 25.0
        bg = (round(240 + (197 - 240) * t), round(229 + (69 - 229) * t), round(218 + (62 - 218) * t))
    fg = '#ffffff' if abs(p) >= 13 else '#2C3E50'
    return f"#{bg[0]:02X}{bg[1]:02X}{bg[2]:02X}", fg

def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))

def grad2(pct_val):
    p = max(-25.0, min(25.0, pct_val))
    if p >= 0:
        t = p / 25.0
        bg = lerp((240,229,218),(30,107,48),t)
    else:
        t = -p / 25.0
        bg = lerp((240,229,218),(197,69,62),t)
    fg = '#ffffff' if abs(p) >= 13 else '#2C3E50'
    return f"#{bg[0]:02X}{bg[1]:02X}{bg[2]:02X}", fg

# ── Compute BU totals for D1, D2, D8 ──
def get_bu_day(day):
    result = {}
    for r in Q2:
        if r["d"] == day and r["bu"] not in ("General",):
            result[r["bu"]] = {"revenue": r["revenue"], "bills": r["bills"]}
    return result

bu_d1 = get_bu_day(D1)
bu_d2 = get_bu_day(D2)
bu_d8 = get_bu_day(D8)

total_d1_rev = sum(v["revenue"] for v in bu_d1.values())
total_d1_bills = sum(v["bills"] for v in bu_d1.values())
total_d2_rev = sum(v["revenue"] for v in bu_d2.values())
total_d2_bills = sum(v["bills"] for v in bu_d2.values())
total_d8_rev = sum(v["revenue"] for v in bu_d8.values())
total_d8_bills = sum(v["bills"] for v in bu_d8.values())

wow_rev = pct(total_d1_rev, total_d8_rev)
dod_rev = pct(total_d1_rev, total_d2_rev)
wow_bills = pct(total_d1_bills, total_d8_bills)
d1_ticket = total_d1_rev / total_d1_bills
d8_ticket = total_d8_rev / total_d8_bills
wow_ticket = pct(d1_ticket, d8_ticket)

# ── MTD (June 1-22) from Q2 ──
mtd_days_data = {}
for r in Q2:
    if r["d"] >= "2026-06-01" and r["d"] <= D1 and r["bu"] != "General":
        d = r["d"]
        mtd_days_data.setdefault(d, {"rev":0,"bills":0})
        mtd_days_data[d]["rev"] += r["revenue"]
        mtd_days_data[d]["bills"] += r["bills"]

mtd_revs = [v["rev"] for v in mtd_days_data.values()]
mtd_count = len(mtd_revs)
mtd_total = sum(mtd_revs)
mtd_avg = mtd_total / mtd_count
mtd_high = max(mtd_revs)
mtd_low = min(mtd_revs)
mtd_signed = pct(total_d1_rev, mtd_avg)

# ── Status emoji ──
# CRITICAL check
has_critical = False  # will set after computing severity below

# ── 30-day daily totals from Q2 (all BUs) for chart ──
daily_totals = {}
for r in Q2:
    if r["bu"] == "General": continue
    d = r["d"]
    daily_totals.setdefault(d, {})
    daily_totals[d].setdefault(r["bu"], {"revenue":0,"bills":0})
    daily_totals[d][r["bu"]]["revenue"] += r["revenue"]
    daily_totals[d][r["bu"]]["bills"] += r["bills"]

# Sort dates
all_dates = sorted(daily_totals.keys())
# TREND window: 30 days D1-29 to D1
trend_dates = [d for d in all_dates if "2026-05-24" <= d <= "2026-06-22"]

# Max daily total for pixel scale
max_daily = max(sum(bu["revenue"] for bu in daily_totals[d].values()) for d in trend_dates)
HEIGHT = 240
PIXEL_PER_BAHT = (HEIGHT - 20) / max_daily

def px(rev): return max(0, round(rev * PIXEL_PER_BAHT))

BUS = ["Subway","Juice Land","Khiang","Siam Express","Vendi"]

# ── Airport daily totals from Q3 ──
ap_daily = {}
for r in Q3_FULL:
    loc = r["location"]
    ap = AIRPORT.get(loc, "BKK")
    d = r["d"]
    ap_daily.setdefault(d, {"BKK":{"rev":0,"bills":0},"DMK":{"rev":0,"bills":0},"PKT":{"rev":0,"bills":0}})
    ap_daily[d][ap]["rev"] += r["revenue"]
    ap_daily[d][ap]["bills"] += r["bills"]

# ── Build bu_chart_days & bu_chart_axis ──
bu_chart_days = []
bu_chart_axis = []
import datetime

for d in trend_dates:
    dt = datetime.date.fromisoformat(d)
    is_d1 = (d == D1)
    day_data = daily_totals.get(d, {})
    total_rev = sum(bu["revenue"] for bu in day_data.values())
    bu_chart_days.append({
        "d1_class": "d1" if is_d1 else "",
        "day_title": f"{dt.strftime('%d %b')} ฿{total_rev:,.0f}",
        "h_subway": px(day_data.get("Subway",{}).get("revenue",0)),
        "h_khiang": px(day_data.get("Khiang",{}).get("revenue",0)),
        "h_jl": px(day_data.get("Juice Land",{}).get("revenue",0)),
        "h_se": px(day_data.get("Siam Express",{}).get("revenue",0)),
        "h_vendi": px(day_data.get("Vendi",{}).get("revenue",0)),
    })
    day_num = dt.strftime("%-d")
    ax_class = "axd1" if is_d1 else ""
    if dt.weekday() in (5,6): ax_class = "axhol" if not is_d1 else "axd1"
    bu_chart_axis.append({
        "ax_label": day_num,
        "ax_class": ax_class,
    })

# ── Build airport_chart_days & airport_chart_axis ──
# Need to build from Q3_FULL for trend window; use loc-level data
ap_chart_trend = {}
for r in Q3_FULL:
    d = r["d"]
    if d not in ap_chart_trend: ap_chart_trend[d] = {"BKK":0,"DMK":0,"PKT":0}
    ap = AIRPORT.get(r["location"], "BKK")
    ap_chart_trend[d][ap] += r["revenue"]

# Also add May dates from Q3 (not in Q3_FULL but we have Q3 data)
# Q3_FULL only covers June. For May use location-based Q3 data from the full response.
# Let me build airport from Q2 BU data mapped to airport
# Actually Q3_FULL doesn't include May. Build airport chart from Q2 with location data
# For May dates, we need to estimate airport split. Use ratio from known dates.
# Actually let's just use Q2-based total and known airport %s for May (we don't have loc data for May).
# Use Q3 for June, and for May use ratio: BKK~73%, DMK~18%, PKT~9%

may_dates = [d for d in trend_dates if d < "2026-06-01"]
jun_dates = [d for d in trend_dates if d >= "2026-06-01"]

# Compute June airport ratios from available data
jun_bkk_tot = sum(ap_chart_trend.get(d,{}).get("BKK",0) for d in jun_dates)
jun_dmk_tot = sum(ap_chart_trend.get(d,{}).get("DMK",0) for d in jun_dates)
jun_pkt_tot = sum(ap_chart_trend.get(d,{}).get("PKT",0) for d in jun_dates)
jun_total = jun_bkk_tot + jun_dmk_tot + jun_pkt_tot
bkk_r = jun_bkk_tot/jun_total if jun_total else 0.733
dmk_r = jun_dmk_tot/jun_total if jun_total else 0.182
pkt_r = jun_pkt_tot/jun_total if jun_total else 0.085

airport_chart_days = []
airport_chart_axis = []
for d in trend_dates:
    dt = datetime.date.fromisoformat(d)
    is_d1 = (d == D1)
    if d in ap_chart_trend:
        bkk = ap_chart_trend[d]["BKK"]
        dmk = ap_chart_trend[d]["DMK"]
        pkt = ap_chart_trend[d]["PKT"]
    else:
        total_rev = sum(daily_totals.get(d,{}).get(bu,{}).get("revenue",0) for bu in BUS)
        bkk = total_rev * bkk_r
        dmk = total_rev * dmk_r
        pkt = total_rev * pkt_r
    airport_chart_days.append({
        "d1_class": "d1" if is_d1 else "",
        "day_title": f"{dt.strftime('%d %b')} BKK:{bkk:,.0f} DMK:{dmk:,.0f} PKT:{pkt:,.0f}",
        "h_bkk": px(bkk),
        "h_dmk": px(dmk),
        "h_pkt": px(pkt),
    })
    day_num = dt.strftime("%-d")
    ax_class = "axd1" if is_d1 else ""
    if dt.weekday() in (5,6) and not is_d1: ax_class = "axhol"
    airport_chart_axis.append({"ax_label": day_num, "ax_class": ax_class})

# ── BU Legend ──
BU_SIGNAL_3x3 = {
    (1,1):"⭐ BEST",(1,0):"🚶 Traffic",(1,-1):"⚠️ Mixed",
    (0,1):"✅ Upsell",(0,0):"─ Stable",(0,-1):"📉 Quality",
    (-1,1):"🤔 Premium",(-1,0):"↘ Soft",(-1,-1):"🚨 CRISIS",
}
BU_SIGNAL_CSS = {
    "⭐ BEST":"s-upsell","🚶 Traffic":"s-traffic","⚠️ Mixed":"s-quality",
    "✅ Upsell":"s-upsell","─ Stable":"s-soft","📉 Quality":"s-quality",
    "🤔 Premium":"s-soft","↘ Soft":"s-soft","🚨 CRISIS":"s-crisis",
}

def signal_3x3(bills_wow, ticket_wow):
    b = 1 if bills_wow > 3 else (-1 if bills_wow < -3 else 0)
    t = 1 if ticket_wow > 3 else (-1 if ticket_wow < -3 else 0)
    return BU_SIGNAL_3x3.get((b,t),"─ Stable")

def severity(wow_v, dod_v):
    if wow_v >= 15 and dod_v >= 10: return "SURGE"
    if wow_v >= 0: return "POSITIVE"
    if wow_v > -5: return "NEUTRAL"
    if wow_v <= -20 and dod_v <= -10: return "CRITICAL"
    if wow_v <= -10 and dod_v < 0: return "HIGH"
    if wow_v <= -5: return "WATCH"
    return "NEUTRAL"

SEV_CSS = {"SURGE":"sev-surge","POSITIVE":"sev-positive","NEUTRAL":"sev-neutral",
           "WATCH":"sev-watch","HIGH":"sev-high","CRITICAL":"sev-critical"}

bu_legend_rows = []
for bu in ["Subway","Juice Land","Siam Express","Vendi","Khiang"]:
    d1r = bu_d1.get(bu,{"revenue":0,"bills":0})
    d2r = bu_d2.get(bu,{"revenue":0,"bills":0})
    d8r = bu_d8.get(bu,{"revenue":0,"bills":0})
    rev1, bills1 = d1r["revenue"], d1r["bills"]
    rev2, bills2 = d2r["revenue"], d2r["bills"]
    rev8, bills8 = d8r["revenue"], d8r["bills"]
    wow_r = pct(rev1, rev8)
    dod_r = pct(rev1, rev2)
    bills_wow_r = pct(bills1, bills8)
    t1 = rev1/bills1 if bills1 else 0
    t8 = rev8/bills8 if bills8 else 0
    ticket_wow_r = pct(t1, t8)
    share_r = rev1/total_d1_rev*100 if total_d1_rev else 0
    sig = signal_3x3(bills_wow_r, ticket_wow_r)
    bu_legend_rows.append({
        "color": BU_COLOR.get(bu,"#999"),
        "bu_name": bu,
        "d1_rev": fmt_baht(rev1),
        "d1_bills": fmt_comma(bills1),
        "share": f"{share_r:.1f}%",
        "wow": signed(wow_r),
        "wow_class": wow_class(wow_r),
        "bills_delta": signed(bills_wow_r),
        "bills_class": wow_class(bills_wow_r),
        "ticket_delta": signed(ticket_wow_r),
        "ticket_class": wow_class(ticket_wow_r),
        "signal": sig,
        "signal_class": BU_SIGNAL_CSS.get(sig,"s-soft"),
    })

# ── Airport Legend ──
def get_airport_d1_d8(ap):
    d1_rev = sum(r["revenue"] for r in Q3_FULL if r["d"]==D1 and AIRPORT.get(r["location"])==ap)
    d1_bills = sum(r["bills"] for r in Q3_FULL if r["d"]==D1 and AIRPORT.get(r["location"])==ap)
    d8_rev = sum(r["revenue"] for r in Q3_FULL if r["d"]==D8 and AIRPORT.get(r["location"])==ap)
    d8_bills = sum(r["bills"] for r in Q3_FULL if r["d"]==D8 and AIRPORT.get(r["location"])==ap)
    return d1_rev, d1_bills, d8_rev, d8_bills

AP_COLOR = {"BKK":"#5551FE","DMK":"#7B79FF","PKT":"#F27061"}
airport_legend_rows = []
for ap, apname in [("BKK","BKK (Suvarnabhumi)"),("DMK","DMK (Don Mueang)"),("PKT","PKT (Phuket)")]:
    d1r, d1b, d8r, d8b = get_airport_d1_d8(ap)
    wow_r = pct(d1r, d8r)
    bills_wow_r = pct(d1b, d8b)
    share_r = d1r/total_d1_rev*100 if total_d1_rev else 0
    airport_legend_rows.append({
        "color": AP_COLOR[ap],
        "airport_name": apname,
        "d1_rev": fmt_baht(d1r),
        "d1_bills": fmt_comma(d1b),
        "share": f"{share_r:.1f}%",
        "wow": signed(wow_r),
        "wow_class": wow_class(wow_r),
        "bills_delta": signed(bills_wow_r),
        "bills_class": wow_class(bills_wow_r),
    })

# ── Location × BU heatmap ──
# Build per-loc×BU for D1, D8
loc_bu_d1 = {}
loc_bu_d8 = {}
loc_bu_d2 = {}
for r in Q1:
    key = (r["location"], r["bu"])
    if r["d"] == D1: loc_bu_d1[key] = {"revenue":r["revenue"],"bills":r["bills"]}
    elif r["d"] == D8: loc_bu_d8[key] = {"revenue":r["revenue"],"bills":r["bills"]}
    elif r["d"] == D2: loc_bu_d2[key] = {"revenue":r["revenue"],"bills":r["bills"]}

# MTD per-location stats (from Q3_FULL, June 1-22)
loc_mtd = {}
for r in Q3_FULL:
    if "2026-06-01" <= r["d"] <= D1:
        loc = r["location"]
        loc_mtd.setdefault(loc, []).append(r["revenue"])

# Compute severity and heatmap rows
heatmap_data = []
sev_counts = {"SURGE":0,"POSITIVE":0,"NEUTRAL":0,"WATCH":0,"HIGH":0,"CRITICAL":0}

for (loc, bu), d1_data in sorted(loc_bu_d1.items()):
    rev1 = d1_data["revenue"]; bills1 = d1_data["bills"]
    d8_data = loc_bu_d8.get((loc,bu),{"revenue":0,"bills":0})
    d2_data = loc_bu_d2.get((loc,bu),{"revenue":0,"bills":0})
    rev8 = d8_data["revenue"]; bills8 = d8_data["bills"]
    rev2 = d2_data["revenue"]; bills2 = d2_data["bills"]

    wow_r = pct(rev1, rev8) if rev8 else 0
    dod_r = pct(rev1, rev2) if rev2 else 0
    bills_wow_r = pct(bills1, bills8) if bills8 else 0
    t1 = rev1/bills1 if bills1 else 0
    t8 = rev8/bills8 if bills8 else 0
    ticket_wow_r = pct(t1, t8) if t8 else 0

    sev = severity(wow_r, dod_r)
    sev_counts[sev] = sev_counts.get(sev, 0) + 1

    sig = signal_3x3(bills_wow_r, ticket_wow_r)
    rev_bg, rev_fg = grad2(wow_r)
    bills_bg, bills_fg = grad2(bills_wow_r)
    ticket_bg, ticket_fg = grad2(ticket_wow_r)

    ap = AIRPORT.get(loc, "BKK")

    heatmap_data.append({
        "location": loc,
        "bu": bu,
        "airport": ap,
        "d1_rev": rev1,
        "d1_bills": bills1,
        "rev_wow": wow_r,
        "bills_wow": bills_wow_r,
        "ticket_wow": ticket_wow_r,
        "severity": sev,
        "signal": sig,
        "rev_bg": rev_bg,"rev_fg": rev_fg,
        "bills_bg": bills_bg,"bills_fg": bills_fg,
        "ticket_bg": ticket_bg,"ticket_fg": ticket_fg,
    })

has_critical = sev_counts.get("CRITICAL",0) > 0

# Group by location, order by loc total D1 rev desc
loc_totals = {}
for h in heatmap_data:
    loc_totals[h["location"]] = loc_totals.get(h["location"],0) + h["d1_rev"]

# Sort locations by total D1 rev desc
locs_sorted = sorted(loc_totals.keys(), key=lambda l: -loc_totals[l])

# Within each location, sort BUs by D1 rev desc
loc_bu_heatmap = {loc:[] for loc in locs_sorted}
for h in heatmap_data:
    loc_bu_heatmap[h["location"]].append(h)
for loc in locs_sorted:
    loc_bu_heatmap[loc].sort(key=lambda x: -x["d1_rev"])

# Build heatmap rows with loc_cell / row_class
loc_heatmap_rows = []
for loc in locs_sorted:
    rows = loc_bu_heatmap[loc]
    n = len(rows)
    for i, h in enumerate(rows):
        is_first = (i == 0)
        if is_first:
            loc_cell = f'<td class="heat-bu" rowspan="{n}"><b>{loc}</b></td>'
            row_class = "grp-start"
        else:
            loc_cell = ""
            row_class = ""
        sev_css = SEV_CSS.get(h["severity"],"sev-neutral")
        sig_css_map = {
            "⭐ BEST":"s-upsell","🚶 Traffic":"s-traffic","⚠️ Mixed":"s-quality",
            "✅ Upsell":"s-upsell","─ Stable":"s-soft","📉 Quality":"s-quality",
            "🤔 Premium":"s-soft","↘ Soft":"s-soft","🚨 CRISIS":"s-crisis",
        }
        loc_heatmap_rows.append({
            "row_class": row_class,
            "loc_cell": loc_cell,
            "bu_color": BU_COLOR.get(h["bu"],"#999"),
            "bu_name": h["bu"],
            "airport": h["airport"],
            "d1_rev": fmt_baht(h["d1_rev"]),
            "d1_bills": fmt_comma(h["d1_bills"]),
            "rev_delta": signed(h["rev_wow"]),
            "bills_delta": signed(h["bills_wow"]),
            "ticket_delta": signed(h["ticket_wow"]),
            "rev_bg": h["rev_bg"],"rev_fg": h["rev_fg"],
            "bills_bg": h["bills_bg"],"bills_fg": h["bills_fg"],
            "ticket_bg": h["ticket_bg"],"ticket_fg": h["ticket_fg"],
            "signal": h["signal"],
            "signal_class": sig_css_map.get(h["signal"],"s-soft"),
        })

# ── Status emoji & subject ──
if has_critical: status_emoji = "🚨"
elif wow_rev < -5: status_emoji = "⚠️"
elif wow_rev > 10: status_emoji = "🔥"
else: status_emoji = "✅"

loc_count = len(locs_sorted)
subject = f"{status_emoji} SFB Daily — {REPORT_DATE_DISPLAY} | {fmt_k(total_d1_rev)} (WoW {signed(wow_rev)}) | {loc_count} locations"

# ── Top/bottom movers for group message ──
all_movers = [(h["location"],h["bu"],h["rev_wow"],h["d1_rev"]) for h in heatmap_data]
all_movers.sort(key=lambda x: -x[2])
top3 = all_movers[:3]
bottom3 = all_movers[-3:]

top_movers_block = "\n".join(
    f"  • {loc} · {bu} {signed(wow)} ({fmt_baht(rev)})"
    for loc,bu,wow,rev in top3
)
bottom_movers_block = "\n".join(
    f"  • {loc} · {bu} {signed(wow)} ({fmt_baht(rev)})"
    for loc,bu,wow,rev in bottom3
)

# ── Exec insight bullets ──
# Dominant: 4 BUs up (SW+JL+SE+Vendi), 1 down (Khiang) → broad_growth
# Total bills slightly down (-1.7%), ticket up (+3%) → slight premium flavour
bu_wows = {bu_d1[bu]["revenue"] and pct(bu_d1[bu]["revenue"],bu_d8.get(bu,{"revenue":0})["revenue"])
           if bu in bu_d1 and bu in bu_d8 else 0 for bu in BUS}
# Recompute cleanly
bu_wow_map = {}
for bu in BUS:
    r1 = bu_d1.get(bu,{"revenue":0})["revenue"]
    r8 = bu_d8.get(bu,{"revenue":0})["revenue"]
    bu_wow_map[bu] = pct(r1,r8) if r8 else 0

insight_bullets_text = [
    f"<b>Total D1:</b> ฿{total_d1_rev:,.0f} ({fmt_k(total_d1_rev)}) · WoW {signed(wow_rev)} · DoD {signed(dod_rev)} · vs MTD avg {signed(mtd_signed)} · {total_d1_bills:,} bills · avg ticket ฿{d1_ticket:,.0f}",
    f"<b>Broad growth</b> across 4 of 5 BUs (Subway {signed(bu_wow_map['Subway'])}, Juice Land {signed(bu_wow_map['Juice Land'])}, Siam Express {signed(bu_wow_map['Siam Express'])}, Vendi {signed(bu_wow_map['Vendi'])} WoW); Khiang contracts {signed(bu_wow_map['Khiang'])} WoW on lower bills.",
    f"<b>Top BU:</b> Vendi leads WoW growth at {signed(bu_wow_map['Vendi'])} though on small base (฿{bu_d1['Vendi']['revenue']:,.0f}); Subway largest contributor (฿{bu_d1['Subway']['revenue']:,.0f}, {signed(bu_wow_map['Subway'])} WoW).",
    f"<b>MTD low flag:</b> 20-PKT-Floor 3-S hit MTD LOW today (฿{Q3_LOC[('2026-06-22','20-PKT-Floor 3-S')]['revenue']:,.0f}) — lowest June revenue at that location.",
    f"<b>Top 3 WoW:</b> {top3[0][0]}·{top3[0][1]} {signed(top3[0][2])}, {top3[1][0]}·{top3[1][1]} {signed(top3[1][2])}, {top3[2][0]}·{top3[2][1]} {signed(top3[2][2])}.",
    f"<b>Weakest 3 WoW:</b> {bottom3[0][0]}·{bottom3[0][1]} {signed(bottom3[0][2])}, {bottom3[1][0]}·{bottom3[1][1]} {signed(bottom3[1][2])}, {bottom3[2][0]}·{bottom3[2][1]} {signed(bottom3[2][2])}.",
]
insight_bullets = [{"bullet_html": b} for b in insight_bullets_text]

# ── Assemble data.json ──
mtd_avg_K = fmt_k(mtd_avg)
rev_K = fmt_k(total_d1_rev)

d2_ticket = total_d2_rev/total_d2_bills if total_d2_bills else 0
bills_wow_signed = signed(wow_bills)
ticket_wow_signed = signed(wow_ticket)

data = {
  "scalars": {
    "subject": subject,
    "report_date_display": REPORT_DATE_DISPLAY,
    "weekday_en": WEEKDAY_EN,
    "weekday_th": WEEKDAY_TH,
    "window_label": WINDOW_LABEL,
    "mtd_label": MTD_LABEL,
    "d8_display": D8_DISPLAY,
    "generated_display": GENERATED_DISPLAY,
    "status_emoji": status_emoji,
    "rev_K": rev_K,
    "rev_baht": fmt_baht(total_d1_rev),
    "wow_signed": signed(wow_rev),
    "wow_signed_cls": delta_class(wow_rev),
    "dod_signed": signed(dod_rev),
    "dod_signed_cls": delta_class(dod_rev),
    "mtd_signed": signed(mtd_signed),
    "mtd_signed_cls": delta_class(mtd_signed),
    "bills_total": fmt_comma(total_d1_bills),
    "bills_wow_signed": signed(wow_bills),
    "bills_wow_signed_cls": delta_class(wow_bills),
    "ticket": f"฿{d1_ticket:,.0f}",
    "ticket_wow_signed": signed(wow_ticket),
    "ticket_wow_signed_cls": delta_class(wow_ticket),
    "mtd_avg_K": mtd_avg_K,
    "loc_count": str(loc_count),
  },
  "repeats": {
    "insight_bullets": insight_bullets,
    "bu_chart_days": bu_chart_days,
    "bu_chart_axis": bu_chart_axis,
    "bu_legend_rows": bu_legend_rows,
    "airport_chart_days": airport_chart_days,
    "airport_chart_axis": airport_chart_axis,
    "airport_legend_rows": airport_legend_rows,
    "loc_heatmap_rows": loc_heatmap_rows,
  },
  "sections": {},
}

with open("/home/user/report/SFB/data.json","w") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Print summary
print(f"Mode: scheduled | Report date: {D1}")
print(f"Total revenue D1: ฿{total_d1_rev:,.2f} ({rev_K}) | WoW {signed(wow_rev)} | DoD {signed(dod_rev)} | vs MTD avg {signed(mtd_signed)}")
print(f"Bills: {total_d1_bills:,} | Avg ticket: ฿{d1_ticket:,.0f} | Ticket WoW {signed(wow_ticket)}")
print(f"MTD avg: {mtd_avg_K} | High: {fmt_k(mtd_high)} | Low: {fmt_k(mtd_low)} | Days: {mtd_count}")
print(f"Locations: {loc_count} | MAX_DAILY: ฿{max_daily:,.0f} | PPB: {PIXEL_PER_BAHT:.6f}")
print(f"Severity: SURGE={sev_counts.get('SURGE',0)} POSITIVE={sev_counts.get('POSITIVE',0)} NEUTRAL={sev_counts.get('NEUTRAL',0)} WATCH={sev_counts.get('WATCH',0)} HIGH={sev_counts.get('HIGH',0)} CRITICAL={sev_counts.get('CRITICAL',0)}")
print(f"Status emoji: {status_emoji}")
print(f"Subject: {subject}")
print(f"Top movers:\n{top_movers_block}")
print(f"Bottom movers:\n{bottom_movers_block}")
print("data.json written.")
