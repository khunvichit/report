#!/usr/bin/env python3
"""Generate data.json for SFB Daily report from embedded Q1/Q2/Q3 results."""
import json, math

# ── raw query results ──────────────────────────────────────────────────────
Q1 = [
 {"d":"2026-06-20","location":"18-T1FW4-08-SS","bu":"Subway","bills":212,"revenue":100797.44},
 {"d":"2026-06-20","location":"26-T1MW1-03+04","bu":"Juice Land","bills":93,"revenue":30225.37},
 {"d":"2026-06-20","location":"05-DMK-Inter-S","bu":"Subway","bills":124,"revenue":19686.83},
 {"d":"2026-06-20","location":"25-DMK-CS","bu":"Subway","bills":38,"revenue":8535.52},
 {"d":"2026-06-20","location":"04-DMK-T2MTE3-09","bu":"Subway","bills":110,"revenue":42246.07},
 {"d":"2026-06-20","location":"21-T1BE2-06","bu":"Subway","bills":125,"revenue":40692.50},
 {"d":"2026-06-20","location":"22-DMK-3Pier2-SS","bu":"Siam Express","bills":39,"revenue":6373.75},
 {"d":"2026-06-20","location":"23-T1CE4-13","bu":"Subway","bills":108,"revenue":30798.09},
 {"d":"2026-06-20","location":"09-DMK-G1-S","bu":"Subway","bills":69,"revenue":18916.81},
 {"d":"2026-06-20","location":"28 JUICELAND Unit 362","bu":"Juice Land","bills":68,"revenue":14807.52},
 {"d":"2026-06-20","location":"13-PKT-G1-S","bu":"Siam Express","bills":106,"revenue":26971.92},
 {"d":"2026-06-20","location":"19-T1MB1-03","bu":"Subway","bills":67,"revenue":20896.30},
 {"d":"2026-06-20","location":"22-DMK-3Pier2-SS","bu":"Subway","bills":57,"revenue":11052.59},
 {"d":"2026-06-20","location":"17-T1ME2-30","bu":"Khiang","bills":164,"revenue":31432.26},
 {"d":"2026-06-20","location":"27-T1SE3-05","bu":"Vendi","bills":92,"revenue":17805.65},
 {"d":"2026-06-20","location":"27-T1SE3-05","bu":"Subway","bills":138,"revenue":48961.60},
 {"d":"2026-06-20","location":"27-T1SE3-05","bu":"Juice Land","bills":78,"revenue":27362.69},
 {"d":"2026-06-20","location":"26-T1MW1-03+04","bu":"Subway","bills":114,"revenue":45109.39},
 {"d":"2026-06-20","location":"20-PKT-Floor 3-S","bu":"Siam Express","bills":106,"revenue":33318.71},
 {"d":"2026-06-20","location":"24-T1EW4-14","bu":"Subway","bills":129,"revenue":55720.74},
 {"d":"2026-06-26","location":"23-T1CE4-13","bu":"Subway","bills":157,"revenue":37574.79},
 {"d":"2026-06-26","location":"18-T1FW4-08-SS","bu":"Subway","bills":261,"revenue":106490.80},
 {"d":"2026-06-26","location":"21-T1BE2-06","bu":"Subway","bills":139,"revenue":60852.40},
 {"d":"2026-06-26","location":"26-T1MW1-03+04","bu":"Subway","bills":119,"revenue":45533.64},
 {"d":"2026-06-26","location":"26-T1MW1-03+04","bu":"Juice Land","bills":101,"revenue":34126.79},
 {"d":"2026-06-26","location":"24-T1EW4-14","bu":"Subway","bills":158,"revenue":63935.67},
 {"d":"2026-06-26","location":"27-T1SE3-05","bu":"Vendi","bills":98,"revenue":24502.86},
 {"d":"2026-06-26","location":"19-T1MB1-03","bu":"Subway","bills":119,"revenue":34472.35},
 {"d":"2026-06-26","location":"27-T1SE3-05","bu":"Subway","bills":143,"revenue":40689.68},
 {"d":"2026-06-26","location":"09-DMK-G1-S","bu":"Subway","bills":83,"revenue":23125.15},
 {"d":"2026-06-26","location":"17-T1ME2-30","bu":"Khiang","bills":190,"revenue":34290.55},
 {"d":"2026-06-26","location":"22-DMK-3Pier2-SS","bu":"Subway","bills":81,"revenue":17750.42},
 {"d":"2026-06-26","location":"28 JUICELAND Unit 362","bu":"Juice Land","bills":44,"revenue":10881.34},
 {"d":"2026-06-26","location":"22-DMK-3Pier2-SS","bu":"Siam Express","bills":41,"revenue":7169.06},
 {"d":"2026-06-26","location":"20-PKT-Floor 3-S","bu":"Siam Express","bills":96,"revenue":24899.10},
 {"d":"2026-06-26","location":"25-DMK-CS","bu":"Subway","bills":51,"revenue":13829.92},
 {"d":"2026-06-26","location":"13-PKT-G1-S","bu":"Siam Express","bills":86,"revenue":22048.61},
 {"d":"2026-06-26","location":"05-DMK-Inter-S","bu":"Subway","bills":132,"revenue":32939.30},
 {"d":"2026-06-26","location":"27-T1SE3-05","bu":"Juice Land","bills":49,"revenue":16496.81},
 {"d":"2026-06-26","location":"04-DMK-T2MTE3-09","bu":"Subway","bills":125,"revenue":43578.48},
 {"d":"2026-06-27","location":"22-DMK-3Pier2-SS","bu":"Subway","bills":66,"revenue":13452.33},
 {"d":"2026-06-27","location":"26-T1MW1-03+04","bu":"Juice Land","bills":103,"revenue":31115.96},
 {"d":"2026-06-27","location":"27-T1SE3-05","bu":"Juice Land","bills":78,"revenue":26713.37},
 {"d":"2026-06-27","location":"27-T1SE3-05","bu":"Vendi","bills":92,"revenue":18114.00},
 {"d":"2026-06-27","location":"19-T1MB1-03","bu":"Subway","bills":84,"revenue":26232.26},
 {"d":"2026-06-27","location":"28 JUICELAND Unit 362","bu":"Juice Land","bills":46,"revenue":9699.99},
 {"d":"2026-06-27","location":"24-T1EW4-14","bu":"Subway","bills":183,"revenue":61682.94},
 {"d":"2026-06-27","location":"13-PKT-G1-S","bu":"Siam Express","bills":105,"revenue":22522.40},
 {"d":"2026-06-27","location":"20-PKT-Floor 3-S","bu":"Siam Express","bills":99,"revenue":31994.44},
 {"d":"2026-06-27","location":"18-T1FW4-08-SS","bu":"Subway","bills":253,"revenue":102018.09},
 {"d":"2026-06-27","location":"25-DMK-CS","bu":"Subway","bills":43,"revenue":10152.97},
 {"d":"2026-06-27","location":"21-T1BE2-06","bu":"Subway","bills":171,"revenue":61797.30},
 {"d":"2026-06-27","location":"26-T1MW1-03+04","bu":"Subway","bills":105,"revenue":38963.60},
 {"d":"2026-06-27","location":"22-DMK-3Pier2-SS","bu":"Siam Express","bills":43,"revenue":9125.13},
 {"d":"2026-06-27","location":"09-DMK-G1-S","bu":"Subway","bills":78,"revenue":21099.98},
 {"d":"2026-06-27","location":"23-T1CE4-13","bu":"Subway","bills":148,"revenue":38077.48},
 {"d":"2026-06-27","location":"27-T1SE3-05","bu":"Subway","bills":133,"revenue":44450.97},
 {"d":"2026-06-27","location":"04-DMK-T2MTE3-09","bu":"Subway","bills":122,"revenue":44034.57},
 {"d":"2026-06-27","location":"17-T1ME2-30","bu":"Khiang","bills":196,"revenue":35388.27},
 {"d":"2026-06-27","location":"05-DMK-Inter-S","bu":"Subway","bills":113,"revenue":21837.31},
]

# Q2: per-BU per-day totals (30-day window May 29 – Jun 27)
Q2 = [
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
 {"d":"2026-06-05","bu":"General","revenue":12350.00,"bills":1},
 {"d":"2026-06-05","bu":"Juice Land","revenue":64841.40,"bills":218},
 {"d":"2026-06-05","bu":"Khiang","revenue":34817.34,"bills":190},
 {"d":"2026-06-05","bu":"Siam Express","revenue":85002.72,"bills":291},
 {"d":"2026-06-05","bu":"Subway","revenue":456603.31,"bills":1452},
 {"d":"2026-06-05","bu":"Vendi","revenue":10697.21,"bills":53},
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
 {"d":"2026-06-23","bu":"Juice Land","revenue":63644.21,"bills":208},
 {"d":"2026-06-23","bu":"Khiang","revenue":31337.19,"bills":158},
 {"d":"2026-06-23","bu":"Siam Express","revenue":43546.76,"bills":166},
 {"d":"2026-06-23","bu":"Subway","revenue":438767.76,"bills":1307},
 {"d":"2026-06-23","bu":"Vendi","revenue":13474.81,"bills":80},
 {"d":"2026-06-24","bu":"Juice Land","revenue":65836.66,"bills":206},
 {"d":"2026-06-24","bu":"Khiang","revenue":36589.37,"bills":184},
 {"d":"2026-06-24","bu":"Siam Express","revenue":59216.88,"bills":221},
 {"d":"2026-06-24","bu":"Subway","revenue":447080.66,"bills":1386},
 {"d":"2026-06-24","bu":"Vendi","revenue":14798.09,"bills":76},
 {"d":"2026-06-25","bu":"Juice Land","revenue":61833.36,"bills":209},
 {"d":"2026-06-25","bu":"Khiang","revenue":25630.28,"bills":149},
 {"d":"2026-06-25","bu":"Siam Express","revenue":53420.45,"bills":218},
 {"d":"2026-06-25","bu":"Subway","revenue":459496.40,"bills":1431},
 {"d":"2026-06-25","bu":"Vendi","revenue":23440.24,"bills":111},
 {"d":"2026-06-26","bu":"Juice Land","revenue":61504.94,"bills":194},
 {"d":"2026-06-26","bu":"Khiang","revenue":34290.55,"bills":190},
 {"d":"2026-06-26","bu":"Siam Express","revenue":54116.77,"bills":223},
 {"d":"2026-06-26","bu":"Subway","revenue":520772.60,"bills":1568},
 {"d":"2026-06-26","bu":"Vendi","revenue":24502.86,"bills":98},
 {"d":"2026-06-27","bu":"Juice Land","revenue":67529.32,"bills":227},
 {"d":"2026-06-27","bu":"Khiang","revenue":35388.27,"bills":196},
 {"d":"2026-06-27","bu":"Siam Express","revenue":63641.97,"bills":247},
 {"d":"2026-06-27","bu":"Subway","revenue":483799.80,"bills":1499},
 {"d":"2026-06-27","bu":"Vendi","revenue":18114.00,"bills":92},
]

# Q3: per-location per-day totals (30-day window)
Q3 = [
 {"d":"2026-05-29","location":"04-DMK-T2MTE3-09","revenue":56461.25,"bills":141},
 {"d":"2026-05-29","location":"05-DMK-Inter-S","revenue":65152.87,"bills":400},
 {"d":"2026-05-29","location":"09-DMK-G1-S","revenue":19753.26,"bills":71},
 {"d":"2026-05-29","location":"13-PKT-G1-S","revenue":21002.79,"bills":97},
 {"d":"2026-05-29","location":"17-T1ME2-30","revenue":44263.79,"bills":226},
 {"d":"2026-05-29","location":"18-T1FW4-08-SS","revenue":137665.86,"bills":747},
 {"d":"2026-05-29","location":"19-T1MB1-03","revenue":31863.54,"bills":96},
 {"d":"2026-05-29","location":"20-PKT-Floor 3-S","revenue":33460.72,"bills":115},
 {"d":"2026-05-29","location":"21-T1BE2-06","revenue":63928.28,"bills":147},
 {"d":"2026-05-29","location":"22-DMK-3Pier2-SS","revenue":47149.29,"bills":237},
 {"d":"2026-05-29","location":"23-T1CE4-13","revenue":44182.17,"bills":203},
 {"d":"2026-05-29","location":"24-T1EW4-14","revenue":80329.79,"bills":244},
 {"d":"2026-05-29","location":"25-DMK-CS","revenue":16085.09,"bills":62},
 {"d":"2026-05-29","location":"26-T1MW1-03+04","revenue":89239.33,"bills":229},
 {"d":"2026-05-29","location":"27-T1SE3-05","revenue":73077.58,"bills":322},
 {"d":"2026-05-29","location":"28 JUICELAND Unit 362","revenue":12938.36,"bills":58},
 {"d":"2026-05-30","location":"04-DMK-T2MTE3-09","revenue":69932.68,"bills":157},
 {"d":"2026-05-30","location":"05-DMK-Inter-S","revenue":55086.88,"bills":290},
 {"d":"2026-05-30","location":"09-DMK-G1-S","revenue":21982.17,"bills":68},
 {"d":"2026-05-30","location":"13-PKT-G1-S","revenue":22966.32,"bills":86},
 {"d":"2026-05-30","location":"17-T1ME2-30","revenue":33264.99,"bills":183},
 {"d":"2026-05-30","location":"18-T1FW4-08-SS","revenue":123879.56,"bills":426},
 {"d":"2026-05-30","location":"19-T1MB1-03","revenue":27384.21,"bills":104},
 {"d":"2026-05-30","location":"20-PKT-Floor 3-S","revenue":31513.12,"bills":112},
 {"d":"2026-05-30","location":"21-T1BE2-06","revenue":57252.34,"bills":136},
 {"d":"2026-05-30","location":"22-DMK-3Pier2-SS","revenue":70568.89,"bills":266},
 {"d":"2026-05-30","location":"23-T1CE4-13","revenue":44371.04,"bills":187},
 {"d":"2026-05-30","location":"24-T1EW4-14","revenue":78971.17,"bills":207},
 {"d":"2026-05-30","location":"25-DMK-CS","revenue":19219.65,"bills":68},
 {"d":"2026-05-30","location":"26-T1MW1-03+04","revenue":80336.85,"bills":233},
 {"d":"2026-05-30","location":"27-T1SE3-05","revenue":91815.96,"bills":324},
 {"d":"2026-05-30","location":"28 JUICELAND Unit 362","revenue":13649.57,"bills":60},
 {"d":"2026-05-31","location":"04-DMK-T2MTE3-09","revenue":57902.71,"bills":154},
 {"d":"2026-05-31","location":"05-DMK-Inter-S","revenue":48158.83,"bills":115},
 {"d":"2026-05-31","location":"09-DMK-G1-S","revenue":11812.12,"bills":53},
 {"d":"2026-05-31","location":"13-PKT-G1-S","revenue":25316.82,"bills":100},
 {"d":"2026-05-31","location":"17-T1ME2-30","revenue":37355.73,"bills":216},
 {"d":"2026-05-31","location":"18-T1FW4-08-SS","revenue":88750.65,"bills":168},
 {"d":"2026-05-31","location":"19-T1MB1-03","revenue":28722.53,"bills":89},
 {"d":"2026-05-31","location":"20-PKT-Floor 3-S","revenue":49948.66,"bills":141},
 {"d":"2026-05-31","location":"21-T1BE2-06","revenue":53448.56,"bills":132},
 {"d":"2026-05-31","location":"22-DMK-3Pier2-SS","revenue":50320.45,"bills":182},
 {"d":"2026-05-31","location":"23-T1CE4-13","revenue":29283.19,"bills":93},
 {"d":"2026-05-31","location":"24-T1EW4-14","revenue":76620.92,"bills":168},
 {"d":"2026-05-31","location":"25-DMK-CS","revenue":17754.13,"bills":65},
 {"d":"2026-05-31","location":"26-T1MW1-03+04","revenue":62876.70,"bills":196},
 {"d":"2026-05-31","location":"27-T1SE3-05","revenue":90161.02,"bills":301},
 {"d":"2026-05-31","location":"28 JUICELAND Unit 362","revenue":13132.69,"bills":54},
 {"d":"2026-06-01","location":"04-DMK-T2MTE3-09","revenue":48437.33,"bills":125},
 {"d":"2026-06-01","location":"05-DMK-Inter-S","revenue":44600.03,"bills":162},
 {"d":"2026-06-01","location":"09-DMK-G1-S","revenue":21137.51,"bills":84},
 {"d":"2026-06-01","location":"13-PKT-G1-S","revenue":31999.06,"bills":109},
 {"d":"2026-06-01","location":"17-T1ME2-30","revenue":37948.06,"bills":214},
 {"d":"2026-06-01","location":"18-T1FW4-08-SS","revenue":122116.54,"bills":330},
 {"d":"2026-06-01","location":"19-T1MB1-03","revenue":23958.51,"bills":74},
 {"d":"2026-06-01","location":"20-PKT-Floor 3-S","revenue":31410.35,"bills":99},
 {"d":"2026-06-01","location":"21-T1BE2-06","revenue":53705.59,"bills":132},
 {"d":"2026-06-01","location":"22-DMK-3Pier2-SS","revenue":52266.27,"bills":166},
 {"d":"2026-06-01","location":"23-T1CE4-13","revenue":47429.87,"bills":165},
 {"d":"2026-06-01","location":"24-T1EW4-14","revenue":80925.73,"bills":203},
 {"d":"2026-06-01","location":"25-DMK-CS","revenue":18598.13,"bills":66},
 {"d":"2026-06-01","location":"26-T1MW1-03+04","revenue":77499.02,"bills":221},
 {"d":"2026-06-01","location":"27-T1SE3-05","revenue":61084.47,"bills":260},
 {"d":"2026-06-01","location":"28 JUICELAND Unit 362","revenue":13028.08,"bills":56},
 {"d":"2026-06-02","location":"04-DMK-T2MTE3-09","revenue":43981.32,"bills":110},
 {"d":"2026-06-02","location":"05-DMK-Inter-S","revenue":23583.12,"bills":125},
 {"d":"2026-06-02","location":"09-DMK-G1-S","revenue":17332.71,"bills":61},
 {"d":"2026-06-02","location":"13-PKT-G1-S","revenue":35729.00,"bills":142},
 {"d":"2026-06-02","location":"17-T1ME2-30","revenue":35318.32,"bills":185},
 {"d":"2026-06-02","location":"18-T1FW4-08-SS","revenue":123892.87,"bills":317},
 {"d":"2026-06-02","location":"19-T1MB1-03","revenue":23601.90,"bills":79},
 {"d":"2026-06-02","location":"20-PKT-Floor 3-S","revenue":38202.86,"bills":126},
 {"d":"2026-06-02","location":"21-T1BE2-06","revenue":46629.97,"bills":123},
 {"d":"2026-06-02","location":"22-DMK-3Pier2-SS","revenue":25086.84,"bills":120},
 {"d":"2026-06-02","location":"23-T1CE4-13","revenue":28924.32,"bills":128},
 {"d":"2026-06-02","location":"24-T1EW4-14","revenue":80536.61,"bills":186},
 {"d":"2026-06-02","location":"25-DMK-CS","revenue":9581.31,"bills":40},
 {"d":"2026-06-02","location":"26-T1MW1-03+04","revenue":69138.60,"bills":196},
 {"d":"2026-06-02","location":"27-T1SE3-05","revenue":46225.19,"bills":216},
 {"d":"2026-06-02","location":"28 JUICELAND Unit 362","revenue":9271.09,"bills":41},
 {"d":"2026-06-03","location":"04-DMK-T2MTE3-09","revenue":38416.89,"bills":128},
 {"d":"2026-06-03","location":"05-DMK-Inter-S","revenue":35024.19,"bills":129},
 {"d":"2026-06-03","location":"09-DMK-G1-S","revenue":15929.91,"bills":68},
 {"d":"2026-06-03","location":"13-PKT-G1-S","revenue":27672.01,"bills":118},
 {"d":"2026-06-03","location":"17-T1ME2-30","revenue":37972.53,"bills":203},
 {"d":"2026-06-03","location":"18-T1FW4-08-SS","revenue":89994.04,"bills":332},
 {"d":"2026-06-03","location":"19-T1MB1-03","revenue":22470.16,"bills":77},
 {"d":"2026-06-03","location":"20-PKT-Floor 3-S","revenue":36186.03,"bills":114},
 {"d":"2026-06-03","location":"21-T1BE2-06","revenue":53182.79,"bills":136},
 {"d":"2026-06-03","location":"22-DMK-3Pier2-SS","revenue":31967.25,"bills":137},
 {"d":"2026-06-03","location":"23-T1CE4-13","revenue":30032.55,"bills":133},
 {"d":"2026-06-03","location":"24-T1EW4-14","revenue":73218.65,"bills":194},
 {"d":"2026-06-03","location":"25-DMK-CS","revenue":15794.39,"bills":63},
 {"d":"2026-06-03","location":"26-T1MW1-03+04","revenue":78997.28,"bills":218},
 {"d":"2026-06-03","location":"27-T1SE3-05","revenue":50844.42,"bills":212},
 {"d":"2026-06-03","location":"28 JUICELAND Unit 362","revenue":10105.67,"bills":51},
 {"d":"2026-06-04","location":"04-DMK-T2MTE3-09","revenue":43860.68,"bills":123},
 {"d":"2026-06-04","location":"05-DMK-Inter-S","revenue":31731.73,"bills":127},
 {"d":"2026-06-04","location":"09-DMK-G1-S","revenue":13779.51,"bills":56},
 {"d":"2026-06-04","location":"13-PKT-G1-S","revenue":24160.75,"bills":100},
 {"d":"2026-06-04","location":"17-T1ME2-30","revenue":29719.07,"bills":178},
 {"d":"2026-06-04","location":"18-T1FW4-08-SS","revenue":102366.40,"bills":287},
 {"d":"2026-06-04","location":"19-T1MB1-03","revenue":25432.74,"bills":90},
 {"d":"2026-06-04","location":"20-PKT-Floor 3-S","revenue":29870.16,"bills":95},
 {"d":"2026-06-04","location":"21-T1BE2-06","revenue":44380.41,"bills":125},
 {"d":"2026-06-04","location":"22-DMK-3Pier2-SS","revenue":27852.29,"bills":138},
 {"d":"2026-06-04","location":"23-T1CE4-13","revenue":33447.49,"bills":134},
 {"d":"2026-06-04","location":"24-T1EW4-14","revenue":68994.71,"bills":181},
 {"d":"2026-06-04","location":"25-DMK-CS","revenue":9786.00,"bills":38},
 {"d":"2026-06-04","location":"26-T1MW1-03+04","revenue":81017.50,"bills":228},
 {"d":"2026-06-04","location":"27-T1SE3-05","revenue":53979.62,"bills":224},
 {"d":"2026-06-04","location":"28 JUICELAND Unit 362","revenue":12286.03,"bills":60},
 {"d":"2026-06-05","location":"04-DMK-T2MTE3-09","revenue":33458.19,"bills":114},
 {"d":"2026-06-05","location":"05-DMK-Inter-S","revenue":31013.98,"bills":128},
 {"d":"2026-06-05","location":"09-DMK-G1-S","revenue":16238.33,"bills":69},
 {"d":"2026-06-05","location":"13-PKT-G1-S","revenue":31567.27,"bills":122},
 {"d":"2026-06-05","location":"17-T1ME2-30","revenue":34817.34,"bills":190},
 {"d":"2026-06-05","location":"18-T1FW4-08-SS","revenue":92889.47,"bills":268},
 {"d":"2026-06-05","location":"19-T1MB1-03","revenue":32157.35,"bills":105},
 {"d":"2026-06-05","location":"20-PKT-Floor 3-S","revenue":40387.87,"bills":111},
 {"d":"2026-06-05","location":"21-T1BE2-06","revenue":58257.02,"bills":140},
 {"d":"2026-06-05","location":"22-DMK-3Pier2-SS","revenue":37038.23,"bills":147},
 {"d":"2026-06-05","location":"23-T1CE4-13","revenue":39104.75,"bills":127},
 {"d":"2026-06-05","location":"24-T1EW4-14","revenue":53946.71,"bills":146},
 {"d":"2026-06-05","location":"25-DMK-CS","revenue":12986.90,"bills":53},
 {"d":"2026-06-05","location":"26-T1MW1-03+04","revenue":67724.99,"bills":205},
 {"d":"2026-06-05","location":"27-T1SE3-05","revenue":57673.51,"bills":221},
 {"d":"2026-06-05","location":"28 JUICELAND Unit 362","revenue":12700.07,"bills":58},
 {"d":"2026-06-05","location":"SFB HQ","revenue":12350.00,"bills":1},
 {"d":"2026-06-06","location":"04-DMK-T2MTE3-09","revenue":34303.73,"bills":114},
 {"d":"2026-06-06","location":"05-DMK-Inter-S","revenue":27002.79,"bills":110},
 {"d":"2026-06-06","location":"09-DMK-G1-S","revenue":14841.10,"bills":57},
 {"d":"2026-06-06","location":"13-PKT-G1-S","revenue":13631.76,"bills":74},
 {"d":"2026-06-06","location":"17-T1ME2-30","revenue":39565.26,"bills":207},
 {"d":"2026-06-06","location":"18-T1FW4-08-SS","revenue":107601.02,"bills":266},
 {"d":"2026-06-06","location":"19-T1MB1-03","revenue":24871.05,"bills":88},
 {"d":"2026-06-06","location":"20-PKT-Floor 3-S","revenue":39314.13,"bills":121},
 {"d":"2026-06-06","location":"21-T1BE2-06","revenue":45331.76,"bills":127},
 {"d":"2026-06-06","location":"22-DMK-3Pier2-SS","revenue":28825.95,"bills":129},
 {"d":"2026-06-06","location":"23-T1CE4-13","revenue":26952.93,"bills":100},
 {"d":"2026-06-06","location":"24-T1EW4-14","revenue":73995.34,"bills":178},
 {"d":"2026-06-06","location":"25-DMK-CS","revenue":10556.99,"bills":48},
 {"d":"2026-06-06","location":"26-T1MW1-03+04","revenue":69617.88,"bills":189},
 {"d":"2026-06-06","location":"27-T1SE3-05","revenue":66379.80,"bills":246},
 {"d":"2026-06-06","location":"28 JUICELAND Unit 362","revenue":12959.90,"bills":53},
 {"d":"2026-06-07","location":"04-DMK-T2MTE3-09","revenue":43465.43,"bills":122},
 {"d":"2026-06-07","location":"05-DMK-Inter-S","revenue":28220.55,"bills":107},
 {"d":"2026-06-07","location":"09-DMK-G1-S","revenue":17696.24,"bills":69},
 {"d":"2026-06-07","location":"13-PKT-G1-S","revenue":22144.84,"bills":91},
 {"d":"2026-06-07","location":"17-T1ME2-30","revenue":35120.83,"bills":186},
 {"d":"2026-06-07","location":"18-T1FW4-08-SS","revenue":107977.56,"bills":263},
 {"d":"2026-06-07","location":"19-T1MB1-03","revenue":26063.79,"bills":97},
 {"d":"2026-06-07","location":"20-PKT-Floor 3-S","revenue":34148.68,"bills":112},
 {"d":"2026-06-07","location":"21-T1BE2-06","revenue":60397.24,"bills":135},
 {"d":"2026-06-07","location":"22-DMK-3Pier2-SS","revenue":32390.66,"bills":147},
 {"d":"2026-06-07","location":"23-T1CE4-13","revenue":30267.31,"bills":121},
 {"d":"2026-06-07","location":"24-T1EW4-14","revenue":60178.52,"bills":147},
 {"d":"2026-06-07","location":"25-DMK-CS","revenue":16657.94,"bills":69},
 {"d":"2026-06-07","location":"26-T1MW1-03+04","revenue":59972.37,"bills":188},
 {"d":"2026-06-07","location":"27-T1SE3-05","revenue":53573.13,"bills":248},
 {"d":"2026-06-07","location":"28 JUICELAND Unit 362","revenue":12143.01,"bills":48},
 {"d":"2026-06-08","location":"04-DMK-T2MTE3-09","revenue":53896.12,"bills":139},
 {"d":"2026-06-08","location":"05-DMK-Inter-S","revenue":25732.69,"bills":100},
 {"d":"2026-06-08","location":"09-DMK-G1-S","revenue":13016.76,"bills":56},
 {"d":"2026-06-08","location":"13-PKT-G1-S","revenue":19955.08,"bills":84},
 {"d":"2026-06-08","location":"17-T1ME2-30","revenue":27605.54,"bills":168},
 {"d":"2026-06-08","location":"18-T1FW4-08-SS","revenue":99512.02,"bills":274},
 {"d":"2026-06-08","location":"19-T1MB1-03","revenue":17742.23,"bills":70},
 {"d":"2026-06-08","location":"20-PKT-Floor 3-S","revenue":35074.86,"bills":110},
 {"d":"2026-06-08","location":"21-T1BE2-06","revenue":50592.52,"bills":125},
 {"d":"2026-06-08","location":"22-DMK-3Pier2-SS","revenue":34870.94,"bills":141},
 {"d":"2026-06-08","location":"23-T1CE4-13","revenue":24647.63,"bills":96},
 {"d":"2026-06-08","location":"24-T1EW4-14","revenue":59631.39,"bills":166},
 {"d":"2026-06-08","location":"25-DMK-CS","revenue":18535.48,"bills":64},
 {"d":"2026-06-08","location":"26-T1MW1-03+04","revenue":84158.06,"bills":229},
 {"d":"2026-06-08","location":"27-T1SE3-05","revenue":60681.33,"bills":248},
 {"d":"2026-06-08","location":"28 JUICELAND Unit 362","revenue":11971.98,"bills":45},
 {"d":"2026-06-09","location":"04-DMK-T2MTE3-09","revenue":46588.79,"bills":125},
 {"d":"2026-06-09","location":"05-DMK-Inter-S","revenue":26995.32,"bills":90},
 {"d":"2026-06-09","location":"09-DMK-G1-S","revenue":10185.95,"bills":46},
 {"d":"2026-06-09","location":"13-PKT-G1-S","revenue":16160.74,"bills":76},
 {"d":"2026-06-09","location":"17-T1ME2-30","revenue":27834.68,"bills":145},
 {"d":"2026-06-09","location":"18-T1FW4-08-SS","revenue":103048.85,"bills":267},
 {"d":"2026-06-09","location":"19-T1MB1-03","revenue":31191.14,"bills":88},
 {"d":"2026-06-09","location":"20-PKT-Floor 3-S","revenue":28486.09,"bills":87},
 {"d":"2026-06-09","location":"21-T1BE2-06","revenue":42942.56,"bills":115},
 {"d":"2026-06-09","location":"22-DMK-3Pier2-SS","revenue":26826.17,"bills":114},
 {"d":"2026-06-09","location":"23-T1CE4-13","revenue":30904.05,"bills":124},
 {"d":"2026-06-09","location":"24-T1EW4-14","revenue":67610.84,"bills":153},
 {"d":"2026-06-09","location":"25-DMK-CS","revenue":17390.68,"bills":49},
 {"d":"2026-06-09","location":"26-T1MW1-03+04","revenue":69962.68,"bills":198},
 {"d":"2026-06-09","location":"27-T1SE3-05","revenue":40044.21,"bills":183},
 {"d":"2026-06-09","location":"28 JUICELAND Unit 362","revenue":9523.36,"bills":42},
 {"d":"2026-06-10","location":"04-DMK-T2MTE3-09","revenue":40373.71,"bills":122},
 {"d":"2026-06-10","location":"05-DMK-Inter-S","revenue":31710.23,"bills":116},
 {"d":"2026-06-10","location":"09-DMK-G1-S","revenue":6043.93,"bills":28},
 {"d":"2026-06-10","location":"13-PKT-G1-S","revenue":14715.87,"bills":73},
 {"d":"2026-06-10","location":"17-T1ME2-30","revenue":38472.74,"bills":185},
 {"d":"2026-06-10","location":"18-T1FW4-08-SS","revenue":99749.42,"bills":277},
 {"d":"2026-06-10","location":"19-T1MB1-03","revenue":23872.01,"bills":86},
 {"d":"2026-06-10","location":"20-PKT-Floor 3-S","revenue":25749.59,"bills":86},
 {"d":"2026-06-10","location":"21-T1BE2-06","revenue":49334.54,"bills":120},
 {"d":"2026-06-10","location":"22-DMK-3Pier2-SS","revenue":32035.46,"bills":143},
 {"d":"2026-06-10","location":"23-T1CE4-13","revenue":35485.91,"bills":141},
 {"d":"2026-06-10","location":"24-T1EW4-14","revenue":60377.64,"bills":133},
 {"d":"2026-06-10","location":"25-DMK-CS","revenue":16097.18,"bills":62},
 {"d":"2026-06-10","location":"26-T1MW1-03+04","revenue":72354.64,"bills":218},
 {"d":"2026-06-10","location":"27-T1SE3-05","revenue":55950.83,"bills":233},
 {"d":"2026-06-10","location":"28 JUICELAND Unit 362","revenue":9579.45,"bills":43},
 {"d":"2026-06-11","location":"04-DMK-T2MTE3-09","revenue":49381.28,"bills":125},
 {"d":"2026-06-11","location":"05-DMK-Inter-S","revenue":27892.03,"bills":138},
 {"d":"2026-06-11","location":"09-DMK-G1-S","revenue":14873.82,"bills":56},
 {"d":"2026-06-11","location":"13-PKT-G1-S","revenue":20786.89,"bills":86},
 {"d":"2026-06-11","location":"17-T1ME2-30","revenue":27774.25,"bills":161},
 {"d":"2026-06-11","location":"18-T1FW4-08-SS","revenue":103727.64,"bills":288},
 {"d":"2026-06-11","location":"19-T1MB1-03","revenue":25648.63,"bills":94},
 {"d":"2026-06-11","location":"20-PKT-Floor 3-S","revenue":32327.17,"bills":112},
 {"d":"2026-06-11","location":"21-T1BE2-06","revenue":48968.72,"bills":122},
 {"d":"2026-06-11","location":"22-DMK-3Pier2-SS","revenue":23499.04,"bills":120},
 {"d":"2026-06-11","location":"23-T1CE4-13","revenue":28691.71,"bills":128},
 {"d":"2026-06-11","location":"24-T1EW4-14","revenue":51916.18,"bills":144},
 {"d":"2026-06-11","location":"25-DMK-CS","revenue":13100.91,"bills":49},
 {"d":"2026-06-11","location":"26-T1MW1-03+04","revenue":72308.60,"bills":204},
 {"d":"2026-06-11","location":"27-T1SE3-05","revenue":47944.17,"bills":201},
 {"d":"2026-06-11","location":"28 JUICELAND Unit 362","revenue":11563.59,"bills":57},
 {"d":"2026-06-12","location":"04-DMK-T2MTE3-09","revenue":52829.87,"bills":130},
 {"d":"2026-06-12","location":"05-DMK-Inter-S","revenue":26873.79,"bills":139},
 {"d":"2026-06-12","location":"09-DMK-G1-S","revenue":18965.38,"bills":84},
 {"d":"2026-06-12","location":"13-PKT-G1-S","revenue":18752.36,"bills":94},
 {"d":"2026-06-12","location":"17-T1ME2-30","revenue":29144.73,"bills":160},
 {"d":"2026-06-12","location":"18-T1FW4-08-SS","revenue":113523.43,"bills":342},
 {"d":"2026-06-12","location":"19-T1MB1-03","revenue":24875.72,"bills":84},
 {"d":"2026-06-12","location":"20-PKT-Floor 3-S","revenue":34302.85,"bills":112},
 {"d":"2026-06-12","location":"21-T1BE2-06","revenue":50593.45,"bills":126},
 {"d":"2026-06-12","location":"22-DMK-3Pier2-SS","revenue":22231.69,"bills":102},
 {"d":"2026-06-12","location":"23-T1CE4-13","revenue":46354.27,"bills":168},
 {"d":"2026-06-12","location":"24-T1EW4-14","revenue":64798.79,"bills":171},
 {"d":"2026-06-12","location":"25-DMK-CS","revenue":14412.11,"bills":53},
 {"d":"2026-06-12","location":"26-T1MW1-03+04","revenue":73288.80,"bills":217},
 {"d":"2026-06-12","location":"27-T1SE3-05","revenue":62751.55,"bills":238},
 {"d":"2026-06-12","location":"28 JUICELAND Unit 362","revenue":10984.16,"bills":48},
 {"d":"2026-06-13","location":"04-DMK-T2MTE3-09","revenue":42323.28,"bills":126},
 {"d":"2026-06-13","location":"05-DMK-Inter-S","revenue":27132.70,"bills":108},
 {"d":"2026-06-13","location":"09-DMK-G1-S","revenue":12440.17,"bills":46},
 {"d":"2026-06-13","location":"13-PKT-G1-S","revenue":19379.44,"bills":95},
 {"d":"2026-06-13","location":"17-T1ME2-30","revenue":32892.86,"bills":177},
 {"d":"2026-06-13","location":"18-T1FW4-08-SS","revenue":104008.00,"bills":286},
 {"d":"2026-06-13","location":"19-T1MB1-03","revenue":24224.47,"bills":92},
 {"d":"2026-06-13","location":"20-PKT-Floor 3-S","revenue":35698.20,"bills":108},
 {"d":"2026-06-13","location":"21-T1BE2-06","revenue":49226.25,"bills":119},
 {"d":"2026-06-13","location":"22-DMK-3Pier2-SS","revenue":24596.21,"bills":130},
 {"d":"2026-06-13","location":"23-T1CE4-13","revenue":32909.25,"bills":134},
 {"d":"2026-06-13","location":"24-T1EW4-14","revenue":64963.32,"bills":174},
 {"d":"2026-06-13","location":"25-DMK-CS","revenue":15342.04,"bills":52},
 {"d":"2026-06-13","location":"26-T1MW1-03+04","revenue":68602.86,"bills":211},
 {"d":"2026-06-13","location":"27-T1SE3-05","revenue":75994.58,"bills":258},
 {"d":"2026-06-13","location":"28 JUICELAND Unit 362","revenue":11457.08,"bills":49},
 {"d":"2026-06-14","location":"04-DMK-T2MTE3-09","revenue":41324.21,"bills":121},
 {"d":"2026-06-14","location":"05-DMK-Inter-S","revenue":33662.89,"bills":113},
 {"d":"2026-06-14","location":"09-DMK-G1-S","revenue":14052.31,"bills":64},
 {"d":"2026-06-14","location":"13-PKT-G1-S","revenue":32643.81,"bills":104},
 {"d":"2026-06-14","location":"17-T1ME2-30","revenue":29428.33,"bills":172},
 {"d":"2026-06-14","location":"18-T1FW4-08-SS","revenue":113459.36,"bills":262},
 {"d":"2026-06-14","location":"19-T1MB1-03","revenue":20878.53,"bills":76},
 {"d":"2026-06-14","location":"20-PKT-Floor 3-S","revenue":44260.87,"bills":117},
 {"d":"2026-06-14","location":"21-T1BE2-06","revenue":50674.04,"bills":135},
 {"d":"2026-06-14","location":"22-DMK-3Pier2-SS","revenue":33076.53,"bills":141},
 {"d":"2026-06-14","location":"23-T1CE4-13","revenue":37194.34,"bills":151},
 {"d":"2026-06-14","location":"24-T1EW4-14","revenue":63447.48,"bills":158},
 {"d":"2026-06-14","location":"25-DMK-CS","revenue":14282.27,"bills":52},
 {"d":"2026-06-14","location":"26-T1MW1-03+04","revenue":72123.43,"bills":207},
 {"d":"2026-06-14","location":"27-T1SE3-05","revenue":60097.34,"bills":237},
 {"d":"2026-06-14","location":"28 JUICELAND Unit 362","revenue":15290.68,"bills":55},
 {"d":"2026-06-15","location":"04-DMK-T2MTE3-09","revenue":45361.66,"bills":126},
 {"d":"2026-06-15","location":"05-DMK-Inter-S","revenue":33630.81,"bills":117},
 {"d":"2026-06-15","location":"09-DMK-G1-S","revenue":17760.73,"bills":68},
 {"d":"2026-06-15","location":"13-PKT-G1-S","revenue":20272.86,"bills":67},
 {"d":"2026-06-15","location":"17-T1ME2-30","revenue":34091.92,"bills":193},
 {"d":"2026-06-15","location":"18-T1FW4-08-SS","revenue":99704.78,"bills":271},
 {"d":"2026-06-15","location":"19-T1MB1-03","revenue":25850.48,"bills":87},
 {"d":"2026-06-15","location":"20-PKT-Floor 3-S","revenue":35192.60,"bills":114},
 {"d":"2026-06-15","location":"21-T1BE2-06","revenue":54836.51,"bills":118},
 {"d":"2026-06-15","location":"22-DMK-3Pier2-SS","revenue":19144.76,"bills":101},
 {"d":"2026-06-15","location":"23-T1CE4-13","revenue":32227.96,"bills":145},
 {"d":"2026-06-15","location":"24-T1EW4-14","revenue":59848.73,"bills":145},
 {"d":"2026-06-15","location":"25-DMK-CS","revenue":11699.17,"bills":49},
 {"d":"2026-06-15","location":"26-T1MW1-03+04","revenue":79312.37,"bills":228},
 {"d":"2026-06-15","location":"27-T1SE3-05","revenue":66895.23,"bills":276},
 {"d":"2026-06-15","location":"28 JUICELAND Unit 362","revenue":11433.69,"bills":50},
 {"d":"2026-06-16","location":"04-DMK-T2MTE3-09","revenue":38875.92,"bills":126},
 {"d":"2026-06-16","location":"05-DMK-Inter-S","revenue":25342.00,"bills":118},
 {"d":"2026-06-16","location":"09-DMK-G1-S","revenue":12329.01,"bills":47},
 {"d":"2026-06-16","location":"13-PKT-G1-S","revenue":27536.31,"bills":112},
 {"d":"2026-06-16","location":"17-T1ME2-30","revenue":25903.34,"bills":158},
 {"d":"2026-06-16","location":"18-T1FW4-08-SS","revenue":100943.11,"bills":264},
 {"d":"2026-06-16","location":"19-T1MB1-03","revenue":25087.87,"bills":84},
 {"d":"2026-06-16","location":"20-PKT-Floor 3-S","revenue":26349.57,"bills":93},
 {"d":"2026-06-16","location":"21-T1BE2-06","revenue":49300.05,"bills":127},
 {"d":"2026-06-16","location":"22-DMK-3Pier2-SS","revenue":24012.11,"bills":94},
 {"d":"2026-06-16","location":"23-T1CE4-13","revenue":24694.53,"bills":115},
 {"d":"2026-06-16","location":"24-T1EW4-14","revenue":56228.14,"bills":164},
 {"d":"2026-06-16","location":"25-DMK-CS","revenue":11282.25,"bills":43},
 {"d":"2026-06-16","location":"26-T1MW1-03+04","revenue":78137.94,"bills":226},
 {"d":"2026-06-16","location":"27-T1SE3-05","revenue":68172.41,"bills":276},
 {"d":"2026-06-16","location":"28 JUICELAND Unit 362","revenue":8484.12,"bills":43},
 {"d":"2026-06-17","location":"04-DMK-T2MTE3-09","revenue":33584.67,"bills":104},
 {"d":"2026-06-17","location":"05-DMK-Inter-S","revenue":30921.44,"bills":123},
 {"d":"2026-06-17","location":"09-DMK-G1-S","revenue":13004.64,"bills":61},
 {"d":"2026-06-17","location":"13-PKT-G1-S","revenue":28829.88,"bills":117},
 {"d":"2026-06-17","location":"17-T1ME2-30","revenue":32266.73,"bills":163},
 {"d":"2026-06-17","location":"18-T1FW4-08-SS","revenue":97123.31,"bills":259},
 {"d":"2026-06-17","location":"19-T1MB1-03","revenue":24259.46,"bills":93},
 {"d":"2026-06-17","location":"20-PKT-Floor 3-S","revenue":25147.69,"bills":91},
 {"d":"2026-06-17","location":"21-T1BE2-06","revenue":45236.55,"bills":121},
 {"d":"2026-06-17","location":"22-DMK-3Pier2-SS","revenue":45788.89,"bills":177},
 {"d":"2026-06-17","location":"23-T1CE4-13","revenue":27193.61,"bills":103},
 {"d":"2026-06-17","location":"24-T1EW4-14","revenue":64154.19,"bills":173},
 {"d":"2026-06-17","location":"25-DMK-CS","revenue":13631.78,"bills":56},
 {"d":"2026-06-17","location":"26-T1MW1-03+04","revenue":79980.45,"bills":225},
 {"d":"2026-06-17","location":"27-T1SE3-05","revenue":57782.70,"bills":244},
 {"d":"2026-06-17","location":"28 JUICELAND Unit 362","revenue":9355.16,"bills":33},
 {"d":"2026-06-18","location":"04-DMK-T2MTE3-09","revenue":49427.07,"bills":138},
 {"d":"2026-06-18","location":"05-DMK-Inter-S","revenue":23671.93,"bills":126},
 {"d":"2026-06-18","location":"09-DMK-G1-S","revenue":15322.38,"bills":59},
 {"d":"2026-06-18","location":"13-PKT-G1-S","revenue":31170.08,"bills":124},
 {"d":"2026-06-18","location":"17-T1ME2-30","revenue":40925.39,"bills":225},
 {"d":"2026-06-18","location":"18-T1FW4-08-SS","revenue":106184.62,"bills":291},
 {"d":"2026-06-18","location":"19-T1MB1-03","revenue":28275.94,"bills":91},
 {"d":"2026-06-18","location":"20-PKT-Floor 3-S","revenue":32991.57,"bills":166},
 {"d":"2026-06-18","location":"21-T1BE2-06","revenue":56731.84,"bills":139},
 {"d":"2026-06-18","location":"22-DMK-3Pier2-SS","revenue":25920.39,"bills":117},
 {"d":"2026-06-18","location":"23-T1CE4-13","revenue":30106.66,"bills":152},
 {"d":"2026-06-18","location":"24-T1EW4-14","revenue":76925.93,"bills":176},
 {"d":"2026-06-18","location":"25-DMK-CS","revenue":8709.33,"bills":33},
 {"d":"2026-06-18","location":"26-T1MW1-03+04","revenue":98076.22,"bills":252},
 {"d":"2026-06-18","location":"27-T1SE3-05","revenue":73493.69,"bills":271},
 {"d":"2026-06-18","location":"28 JUICELAND Unit 362","revenue":13371.98,"bills":57},
 {"d":"2026-06-19","location":"04-DMK-T2MTE3-09","revenue":46987.09,"bills":138},
 {"d":"2026-06-19","location":"05-DMK-Inter-S","revenue":28491.55,"bills":122},
 {"d":"2026-06-19","location":"09-DMK-G1-S","revenue":23634.50,"bills":82},
 {"d":"2026-06-19","location":"13-PKT-G1-S","revenue":24129.90,"bills":108},
 {"d":"2026-06-19","location":"17-T1ME2-30","revenue":40524.61,"bills":218},
 {"d":"2026-06-19","location":"18-T1FW4-08-SS","revenue":95506.25,"bills":205},
 {"d":"2026-06-19","location":"19-T1MB1-03","revenue":39889.78,"bills":116},
 {"d":"2026-06-19","location":"20-PKT-Floor 3-S","revenue":31154.22,"bills":101},
 {"d":"2026-06-19","location":"21-T1BE2-06","revenue":58090.48,"bills":151},
 {"d":"2026-06-19","location":"22-DMK-3Pier2-SS","revenue":35945.60,"bills":161},
 {"d":"2026-06-19","location":"23-T1CE4-13","revenue":41775.66,"bills":153},
 {"d":"2026-06-19","location":"24-T1EW4-14","revenue":56704.03,"bills":158},
 {"d":"2026-06-19","location":"25-DMK-CS","revenue":12586.92,"bills":53},
 {"d":"2026-06-19","location":"26-T1MW1-03+04","revenue":92058.24,"bills":248},
 {"d":"2026-06-19","location":"27-T1SE3-05","revenue":98317.06,"bills":322},
 {"d":"2026-06-19","location":"28 JUICELAND Unit 362","revenue":11965.43,"bills":62},
 {"d":"2026-06-20","location":"04-DMK-T2MTE3-09","revenue":42246.07,"bills":110},
 {"d":"2026-06-20","location":"05-DMK-Inter-S","revenue":19686.83,"bills":124},
 {"d":"2026-06-20","location":"09-DMK-G1-S","revenue":18916.81,"bills":69},
 {"d":"2026-06-20","location":"13-PKT-G1-S","revenue":26971.92,"bills":106},
 {"d":"2026-06-20","location":"17-T1ME2-30","revenue":31432.26,"bills":164},
 {"d":"2026-06-20","location":"18-T1FW4-08-SS","revenue":100797.44,"bills":212},
 {"d":"2026-06-20","location":"19-T1MB1-03","revenue":20896.30,"bills":67},
 {"d":"2026-06-20","location":"20-PKT-Floor 3-S","revenue":33318.71,"bills":106},
 {"d":"2026-06-20","location":"21-T1BE2-06","revenue":40692.50,"bills":125},
 {"d":"2026-06-20","location":"22-DMK-3Pier2-SS","revenue":17426.34,"bills":96},
 {"d":"2026-06-20","location":"23-T1CE4-13","revenue":30798.09,"bills":108},
 {"d":"2026-06-20","location":"24-T1EW4-14","revenue":55720.74,"bills":129},
 {"d":"2026-06-20","location":"25-DMK-CS","revenue":8535.52,"bills":38},
 {"d":"2026-06-20","location":"26-T1MW1-03+04","revenue":75334.76,"bills":207},
 {"d":"2026-06-20","location":"27-T1SE3-05","revenue":94129.94,"bills":308},
 {"d":"2026-06-20","location":"28 JUICELAND Unit 362","revenue":14807.52,"bills":68},
 {"d":"2026-06-21","location":"04-DMK-T2MTE3-09","revenue":46429.84,"bills":126},
 {"d":"2026-06-21","location":"05-DMK-Inter-S","revenue":49309.83,"bills":147},
 {"d":"2026-06-21","location":"09-DMK-G1-S","revenue":16828.03,"bills":67},
 {"d":"2026-06-21","location":"13-PKT-G1-S","revenue":21206.50,"bills":101},
 {"d":"2026-06-21","location":"17-T1ME2-30","revenue":28863.40,"bills":171},
 {"d":"2026-06-21","location":"18-T1FW4-08-SS","revenue":95846.50,"bills":213},
 {"d":"2026-06-21","location":"19-T1MB1-03","revenue":25067.78,"bills":78},
 {"d":"2026-06-21","location":"20-PKT-Floor 3-S","revenue":28169.25,"bills":100},
 {"d":"2026-06-21","location":"21-T1BE2-06","revenue":52194.41,"bills":119},
 {"d":"2026-06-21","location":"22-DMK-3Pier2-SS","revenue":37541.96,"bills":156},
 {"d":"2026-06-21","location":"23-T1CE4-13","revenue":33966.25,"bills":125},
 {"d":"2026-06-21","location":"24-T1EW4-14","revenue":61858.53,"bills":126},
 {"d":"2026-06-21","location":"25-DMK-CS","revenue":16273.80,"bills":59},
 {"d":"2026-06-21","location":"26-T1MW1-03+04","revenue":78913.63,"bills":233},
 {"d":"2026-06-21","location":"27-T1SE3-05","revenue":98269.36,"bills":327},
 {"d":"2026-06-21","location":"28 JUICELAND Unit 362","revenue":7386.93,"bills":38},
 {"d":"2026-06-22","location":"04-DMK-T2MTE3-09","revenue":33404.64,"bills":100},
 {"d":"2026-06-22","location":"05-DMK-Inter-S","revenue":30175.70,"bills":103},
 {"d":"2026-06-22","location":"09-DMK-G1-S","revenue":14922.42,"bills":60},
 {"d":"2026-06-22","location":"13-PKT-G1-S","revenue":31073.79,"bills":107},
 {"d":"2026-06-22","location":"17-T1ME2-30","revenue":28647.68,"bills":163},
 {"d":"2026-06-22","location":"18-T1FW4-08-SS","revenue":110456.18,"bills":267},
 {"d":"2026-06-22","location":"19-T1MB1-03","revenue":26307.51,"bills":80},
 {"d":"2026-06-22","location":"20-PKT-Floor 3-S","revenue":24764.53,"bills":94},
 {"d":"2026-06-22","location":"21-T1BE2-06","revenue":53369.21,"bills":127},
 {"d":"2026-06-22","location":"22-DMK-3Pier2-SS","revenue":26125.08,"bills":115},
 {"d":"2026-06-22","location":"23-T1CE4-13","revenue":45564.41,"bills":152},
 {"d":"2026-06-22","location":"24-T1EW4-14","revenue":57642.17,"bills":139},
 {"d":"2026-06-22","location":"25-DMK-CS","revenue":14981.33,"bills":58},
 {"d":"2026-06-22","location":"26-T1MW1-03+04","revenue":77663.66,"bills":209},
 {"d":"2026-06-22","location":"27-T1SE3-05","revenue":73164.50,"bills":306},
 {"d":"2026-06-22","location":"28 JUICELAND Unit 362","revenue":7170.12,"bills":39},
 {"d":"2026-06-23","location":"04-DMK-T2MTE3-09","revenue":38109.59,"bills":125},
 {"d":"2026-06-23","location":"05-DMK-Inter-S","revenue":13634.55,"bills":80},
 {"d":"2026-06-23","location":"09-DMK-G1-S","revenue":12845.76,"bills":49},
 {"d":"2026-06-23","location":"13-PKT-G1-S","revenue":16119.65,"bills":61},
 {"d":"2026-06-23","location":"17-T1ME2-30","revenue":31337.19,"bills":158},
 {"d":"2026-06-23","location":"18-T1FW4-08-SS","revenue":98929.90,"bills":223},
 {"d":"2026-06-23","location":"19-T1MB1-03","revenue":22472.97,"bills":69},
 {"d":"2026-06-23","location":"20-PKT-Floor 3-S","revenue":22372.02,"bills":77},
 {"d":"2026-06-23","location":"21-T1BE2-06","revenue":65539.29,"bills":165},
 {"d":"2026-06-23","location":"22-DMK-3Pier2-SS","revenue":11959.77,"bills":67},
 {"d":"2026-06-23","location":"23-T1CE4-13","revenue":31462.48,"bills":103},
 {"d":"2026-06-23","location":"24-T1EW4-14","revenue":66583.57,"bills":175},
 {"d":"2026-06-23","location":"25-DMK-CS","revenue":10685.05,"bills":43},
 {"d":"2026-06-23","location":"26-T1MW1-03+04","revenue":76396.36,"bills":199},
 {"d":"2026-06-23","location":"27-T1SE3-05","revenue":62915.08,"bills":285},
 {"d":"2026-06-23","location":"28 JUICELAND Unit 362","revenue":9407.50,"bills":40},
 {"d":"2026-06-24","location":"04-DMK-T2MTE3-09","revenue":37643.01,"bills":122},
 {"d":"2026-06-24","location":"05-DMK-Inter-S","revenue":29506.50,"bills":103},
 {"d":"2026-06-24","location":"09-DMK-G1-S","revenue":15323.35,"bills":59},
 {"d":"2026-06-24","location":"13-PKT-G1-S","revenue":24953.28,"bills":82},
 {"d":"2026-06-24","location":"17-T1ME2-30","revenue":36589.37,"bills":184},
 {"d":"2026-06-24","location":"18-T1FW4-08-SS","revenue":99878.02,"bills":286},
 {"d":"2026-06-24","location":"19-T1MB1-03","revenue":27073.85,"bills":79},
 {"d":"2026-06-24","location":"20-PKT-Floor 3-S","revenue":26015.04,"bills":97},
 {"d":"2026-06-24","location":"21-T1BE2-06","revenue":60244.92,"bills":146},
 {"d":"2026-06-24","location":"22-DMK-3Pier2-SS","revenue":25364.44,"bills":103},
 {"d":"2026-06-24","location":"23-T1CE4-13","revenue":29500.09,"bills":102},
 {"d":"2026-06-24","location":"24-T1EW4-14","revenue":43367.02,"bills":145},
 {"d":"2026-06-24","location":"25-DMK-CS","revenue":10906.52,"bills":39},
 {"d":"2026-06-24","location":"26-T1MW1-03+04","revenue":71431.97,"bills":203},
 {"d":"2026-06-24","location":"27-T1SE3-05","revenue":78074.72,"bills":289},
 {"d":"2026-06-24","location":"28 JUICELAND Unit 362","revenue":7649.56,"bills":34},
 {"d":"2026-06-25","location":"04-DMK-T2MTE3-09","revenue":36962.85,"bills":103},
 {"d":"2026-06-25","location":"05-DMK-Inter-S","revenue":18264.44,"bills":94},
 {"d":"2026-06-25","location":"09-DMK-G1-S","revenue":15700.93,"bills":57},
 {"d":"2026-06-25","location":"13-PKT-G1-S","revenue":22599.97,"bills":92},
 {"d":"2026-06-25","location":"17-T1ME2-30","revenue":25630.28,"bills":149},
 {"d":"2026-06-25","location":"18-T1FW4-08-SS","revenue":104849.44,"bills":269},
 {"d":"2026-06-25","location":"19-T1MB1-03","revenue":29931.65,"bills":91},
 {"d":"2026-06-25","location":"20-PKT-Floor 3-S","revenue":24515.90,"bills":88},
 {"d":"2026-06-25","location":"21-T1BE2-06","revenue":57837.75,"bills":150},
 {"d":"2026-06-25","location":"22-DMK-3Pier2-SS","revenue":20965.29,"bills":106},
 {"d":"2026-06-25","location":"23-T1CE4-13","revenue":37595.45,"bills":155},
 {"d":"2026-06-25","location":"24-T1EW4-14","revenue":56778.96,"bills":157},
 {"d":"2026-06-25","location":"25-DMK-CS","revenue":10991.59,"bills":43},
 {"d":"2026-06-25","location":"26-T1MW1-03+04","revenue":80641.00,"bills":233},
 {"d":"2026-06-25","location":"27-T1SE3-05","revenue":72804.74,"bills":295},
 {"d":"2026-06-25","location":"28 JUICELAND Unit 362","revenue":7750.49,"bills":36},
 {"d":"2026-06-26","location":"04-DMK-T2MTE3-09","revenue":43578.48,"bills":125},
 {"d":"2026-06-26","location":"05-DMK-Inter-S","revenue":32939.30,"bills":132},
 {"d":"2026-06-26","location":"09-DMK-G1-S","revenue":23125.15,"bills":83},
 {"d":"2026-06-26","location":"13-PKT-G1-S","revenue":22048.61,"bills":86},
 {"d":"2026-06-26","location":"17-T1ME2-30","revenue":34290.55,"bills":190},
 {"d":"2026-06-26","location":"18-T1FW4-08-SS","revenue":106490.80,"bills":261},
 {"d":"2026-06-26","location":"19-T1MB1-03","revenue":34472.35,"bills":119},
 {"d":"2026-06-26","location":"20-PKT-Floor 3-S","revenue":24899.10,"bills":96},
 {"d":"2026-06-26","location":"21-T1BE2-06","revenue":60852.40,"bills":139},
 {"d":"2026-06-26","location":"22-DMK-3Pier2-SS","revenue":24919.48,"bills":122},
 {"d":"2026-06-26","location":"23-T1CE4-13","revenue":37574.79,"bills":157},
 {"d":"2026-06-26","location":"24-T1EW4-14","revenue":63935.67,"bills":158},
 {"d":"2026-06-26","location":"25-DMK-CS","revenue":13829.92,"bills":51},
 {"d":"2026-06-26","location":"26-T1MW1-03+04","revenue":79660.43,"bills":220},
 {"d":"2026-06-26","location":"27-T1SE3-05","revenue":81689.35,"bills":290},
 {"d":"2026-06-26","location":"28 JUICELAND Unit 362","revenue":10881.34,"bills":44},
 {"d":"2026-06-27","location":"04-DMK-T2MTE3-09","revenue":44034.57,"bills":122},
 {"d":"2026-06-27","location":"05-DMK-Inter-S","revenue":21837.31,"bills":113},
 {"d":"2026-06-27","location":"09-DMK-G1-S","revenue":21099.98,"bills":78},
 {"d":"2026-06-27","location":"13-PKT-G1-S","revenue":22522.40,"bills":105},
 {"d":"2026-06-27","location":"17-T1ME2-30","revenue":35388.27,"bills":196},
 {"d":"2026-06-27","location":"18-T1FW4-08-SS","revenue":102018.09,"bills":253},
 {"d":"2026-06-27","location":"19-T1MB1-03","revenue":26232.26,"bills":84},
 {"d":"2026-06-27","location":"20-PKT-Floor 3-S","revenue":31994.44,"bills":99},
 {"d":"2026-06-27","location":"21-T1BE2-06","revenue":61797.30,"bills":171},
 {"d":"2026-06-27","location":"22-DMK-3Pier2-SS","revenue":22577.46,"bills":109},
 {"d":"2026-06-27","location":"23-T1CE4-13","revenue":38077.48,"bills":148},
 {"d":"2026-06-27","location":"24-T1EW4-14","revenue":61682.94,"bills":183},
 {"d":"2026-06-27","location":"25-DMK-CS","revenue":10152.97,"bills":43},
 {"d":"2026-06-27","location":"26-T1MW1-03+04","revenue":70079.56,"bills":208},
 {"d":"2026-06-27","location":"27-T1SE3-05","revenue":89278.34,"bills":303},
 {"d":"2026-06-27","location":"28 JUICELAND Unit 362","revenue":9699.99,"bills":46},
]

# ── constants ─────────────────────────────────────────────────────────────
D1, D2, D8 = "2026-06-27", "2026-06-26", "2026-06-20"
MTD_START = "2026-06-01"

AIRPORT = {
 "17-T1ME2-30":"BKK","18-T1FW4-08-SS":"BKK","19-T1MB1-03":"BKK",
 "21-T1BE2-06":"BKK","23-T1CE4-13":"BKK","24-T1EW4-14":"BKK",
 "26-T1MW1-03+04":"BKK","27-T1SE3-05":"BKK","28 JUICELAND Unit 362":"BKK",
 "04-DMK-T2MTE3-09":"DMK","05-DMK-Inter-S":"DMK","09-DMK-G1-S":"DMK",
 "22-DMK-3Pier2-SS":"DMK","25-DMK-CS":"DMK",
 "13-PKT-G1-S":"PKT","20-PKT-Floor 3-S":"PKT",
}
BU_COLOR = {
 "Subway":"#5551FE","Khiang":"#7B79FF","Juice Land":"#2D7A3F",
 "Siam Express":"#F39C12","Vendi":"#C5453E",
}
AP_COLOR = {"BKK":"#5551FE","DMK":"#7B79FF","PKT":"#F27061"}

# ── helpers ────────────────────────────────────────────────────────────────
def lerp(a, b, t):
    return tuple(round(a[i] + (b[i]-a[i])*t) for i in range(3))

def rgb_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)

def grad(pct):
    p = max(-25.0, min(25.0, pct))
    if p >= 0:
        t = p/25.0
        bg = lerp((240,229,218),(30,107,48),t)
    else:
        t = -p/25.0
        bg = lerp((240,229,218),(197,69,62),t)
    fg = "#ffffff" if abs(p) >= 13 else "#2C3E50"
    return rgb_hex(bg), fg

def pct_str(v, decimals=1):
    sign = "+" if v >= 0 else ""
    return f"{sign}{v:.{decimals}f}%"

def wow(d1, d8):
    return (d1-d8)/d8*100 if d8 else 0.0

def signal_3x3(bills_wow, ticket_wow):
    band = 3.0
    if bills_wow > band:
        bdir = 1
    elif bills_wow < -band:
        bdir = -1
    else:
        bdir = 0
    if ticket_wow > band:
        tdir = 1
    elif ticket_wow < -band:
        tdir = -1
    else:
        tdir = 0
    table = {
        (1,1):("s-upsell","⭐ BEST"),
        (1,0):("s-traffic","🚶 Traffic-driven"),
        (1,-1):("s-quality","⚠️ Mixed"),
        (0,1):("s-upsell","✅ Pure upsell"),
        (0,0):("s-soft","─ Stable"),
        (0,-1):("s-quality","📉 Quality slip"),
        (-1,1):("s-soft","🤔 Premium mix"),
        (-1,0):("s-soft","↘ Soft decline"),
        (-1,-1):("s-crisis","🚨 CRISIS"),
    }
    return table[(bdir,tdir)]

# ── index Q1 by date+location+bu ─────────────────────────────────────────
def q1_key(d,loc,bu): return (d,loc,bu)
q1idx = {}
for r in Q1:
    q1idx[(r["d"],r["location"],r["bu"])] = r

def get_q1(d,loc,bu):
    r = q1idx.get((d,loc,bu))
    return (r["revenue"],r["bills"]) if r else (0.0,0)

# ── index Q2 by date+bu ───────────────────────────────────────────────────
from collections import defaultdict
q2_day_bu = defaultdict(lambda:{"revenue":0.0,"bills":0})
for r in Q2:
    if r["bu"] in BU_COLOR:
        q2_day_bu[(r["d"],r["bu"])]["revenue"] += r["revenue"]
        q2_day_bu[(r["d"],r["bu"])]["bills"] += r["bills"]

q2_day_total = defaultdict(lambda:{"revenue":0.0,"bills":0})
for r in Q2:
    q2_day_total[r["d"]]["revenue"] += r["revenue"]
    q2_day_total[r["d"]]["bills"] += r["bills"]

# ── index Q3 by date+location ────────────────────────────────────────────
q3_loc = defaultdict(lambda:{"revenue":0.0,"bills":0})
for r in Q3:
    if r["location"] in AIRPORT:
        q3_loc[(r["d"],r["location"])]["revenue"] += r["revenue"]
        q3_loc[(r["d"],r["location"])]["bills"] += r["bills"]

q3_day_ap = defaultdict(lambda:{"revenue":0.0,"bills":0})
for r in Q3:
    ap = AIRPORT.get(r["location"])
    if ap:
        q3_day_ap[(r["d"],ap)]["revenue"] += r["revenue"]
        q3_day_ap[(r["d"],ap)]["bills"] += r["bills"]

# ── KPI scalars ───────────────────────────────────────────────────────────
d1_rev = q2_day_total[D1]["revenue"]
d1_bills = q2_day_total[D1]["bills"]
d8_rev = q2_day_total[D8]["revenue"]
d8_bills = q2_day_total[D8]["bills"]
d2_rev = q2_day_total[D2]["revenue"]

d1_ticket = d1_rev/d1_bills if d1_bills else 0
d8_ticket = d8_rev/d8_bills if d8_bills else 0

wow_rev = wow(d1_rev, d8_rev)
dod_rev = wow(d1_rev, d2_rev)
wow_bills = wow(d1_bills, d8_bills)
wow_ticket = wow(d1_ticket, d8_ticket)

# MTD avg
mtd_days = [d for d in sorted(set(r["d"] for r in Q2)) if MTD_START <= d <= D1]
mtd_sum = sum(q2_day_total[d]["revenue"] for d in mtd_days)
mtd_avg = mtd_sum/len(mtd_days)
mtd_vs = wow(d1_rev, mtd_avg)

# MAX for chart
all_days_sorted = sorted(set(r["d"] for r in Q2))
max_daily = max(q2_day_total[d]["revenue"] for d in all_days_sorted)
PPB = 220.0/max_daily
HEIGHT = 240

# subject status emoji
# first check CRITICAL severity
d1_loc_bu = {}
for r in Q1:
    if r["d"] == D1:
        k = (r["location"],r["bu"])
        d1_loc_bu[k] = {"rev":r["revenue"],"bills":r["bills"]}

d8_loc_bu = {}
for r in Q1:
    if r["d"] == D8:
        k = (r["location"],r["bu"])
        d8_loc_bu[k] = {"rev":r["revenue"],"bills":r["bills"]}

d2_loc_bu = {}
for r in Q1:
    if r["d"] == D2:
        k = (r["location"],r["bu"])
        d2_loc_bu[k] = {"rev":r["revenue"],"bills":r["bills"]}

def severity(wow_pct, dod_pct):
    if wow_pct >= 15 and dod_pct >= 10: return "SURGE","sev-surge"
    if wow_pct >= 0: return "POSITIVE","sev-positive"
    if wow_pct > -5: return "NEUTRAL","sev-neutral"
    if wow_pct <= -20 and dod_pct <= -10: return "CRITICAL","sev-critical"
    if wow_pct <= -10 and dod_pct < 0: return "HIGH","sev-high"
    if wow_pct <= -5: return "WATCH","sev-watch"
    return "NEUTRAL","sev-neutral"

has_critical = False
for k in d1_loc_bu:
    r1 = d1_loc_bu[k]
    r8 = d8_loc_bu.get(k,{"rev":0,"bills":0})
    r2 = d2_loc_bu.get(k,{"rev":0,"bills":0})
    ww = wow(r1["rev"], r8["rev"]) if r8["rev"] else 0
    dd = wow(r1["rev"], r2["rev"]) if r2["rev"] else 0
    sev,_ = severity(ww, dd)
    if sev == "CRITICAL":
        has_critical = True

if has_critical:
    status_emoji = "🚨"
elif wow_rev < -5:
    status_emoji = "⚠️"
elif wow_rev > 10:
    status_emoji = "🔥"
else:
    status_emoji = "✅"

loc_count = len(set(r["location"] for r in Q1 if r["d"]==D1))

rev_K = f"฿{round(d1_rev/1000)}K"
subject = f"{status_emoji} SFB Daily — 27 Jun 2026 | {rev_K} (WoW {pct_str(wow_rev)}) | {loc_count} locations"

# ── BU legend rows ────────────────────────────────────────────────────────
BU_ORDER = ["Subway","Khiang","Juice Land","Siam Express","Vendi"]
bu_legend_rows = []
for bu in BU_ORDER:
    r1 = q2_day_bu[(D1,bu)]
    r8 = q2_day_bu[(D8,bu)]
    rev1,b1 = r1["revenue"],r1["bills"]
    rev8,b8 = r8["revenue"],r8["bills"]
    t1 = rev1/b1 if b1 else 0
    t8 = rev8/b8 if b8 else 0
    ww = wow(rev1,rev8)
    wb = wow(b1,b8)
    wt = wow(t1,t8)
    sc,sig = signal_3x3(wb,wt)
    share = rev1/d1_rev*100
    bu_legend_rows.append({
        "color": BU_COLOR[bu],
        "bu_name": bu,
        "d1_rev": f"฿{rev1/1000:.1f}K",
        "d1_bills": f"{b1:,}",
        "share": f"{share:.1f}%",
        "wow_class": "delta-up" if ww>=0 else "delta-down",
        "wow": pct_str(ww,1),
        "bills_class": "delta-up" if wb>=0 else "delta-down",
        "bills_delta": pct_str(wb,1),
        "ticket_class": "delta-up" if wt>=0 else "delta-down",
        "ticket_delta": pct_str(wt,1),
        "signal_class": sc,
        "signal": sig,
    })

# ── airport legend rows ───────────────────────────────────────────────────
AP_ORDER = ["BKK","DMK","PKT"]
AP_NAMES = {"BKK":"BKK (Suvarnabhumi)","DMK":"DMK (Don Mueang)","PKT":"PKT (Phuket)"}
airport_legend_rows = []
for ap in AP_ORDER:
    rev1 = sum(q3_day_ap[(D1,ap)]["revenue"] for _ in [1])
    b1   = q3_day_ap[(D1,ap)]["bills"]
    rev8 = q3_day_ap[(D8,ap)]["revenue"]
    b8   = q3_day_ap[(D8,ap)]["bills"]
    # Fix: q3_day_ap is defaultdict, need explicit access
    rev1 = q3_day_ap[(D1,ap)]["revenue"]
    ww = wow(rev1,rev8)
    wb = wow(b1,b8)
    share = rev1/d1_rev*100
    airport_legend_rows.append({
        "color": AP_COLOR[ap],
        "airport_name": AP_NAMES[ap],
        "d1_rev": f"฿{rev1/1000:.1f}K",
        "d1_bills": f"{b1:,}",
        "share": f"{share:.1f}%",
        "wow_class": "delta-up" if ww>=0 else "delta-down",
        "wow": pct_str(ww,1),
        "bills_class": "delta-up" if wb>=0 else "delta-down",
        "bills_delta": pct_str(wb,1),
    })

# ── chart data ────────────────────────────────────────────────────────────
bu_chart_days = []
airport_chart_days = []
bu_chart_axis = []
airport_chart_axis = []

BU_KEYS = ["Subway","Khiang","Juice Land","Siam Express","Vendi"]
BU_H = {"Subway":"h_subway","Khiang":"h_khiang","Juice Land":"h_jl","Siam Express":"h_se","Vendi":"h_vendi"}
AP_H = {"BKK":"h_bkk","DMK":"h_dmk","PKT":"h_pkt"}

for i,d in enumerate(all_days_sorted):
    d_rev = q2_day_total[d]["revenue"]
    is_d1 = (d == D1)
    d1_cls = "d1" if is_d1 else ""
    day_title = f"{d}: ฿{d_rev:,.0f}"
    bu_row = {"d1_class":d1_cls,"day_title":day_title}
    for bu in BU_KEYS:
        rev = q2_day_bu[(d,bu)]["revenue"]
        bu_row[BU_H[bu]] = max(1,round(rev*PPB))
    bu_chart_days.append(bu_row)

    ap_row = {"d1_class":d1_cls,"day_title":day_title}
    for ap in AP_ORDER:
        rev = q3_day_ap[(d,ap)]["revenue"]
        ap_row[AP_H[ap]] = max(1,round(rev*PPB))
    airport_chart_days.append(ap_row)

    # axis label: every 5th or D1
    mm_dd = d[5:]
    if i == len(all_days_sorted)-1:
        bu_chart_axis.append({"ax_class":"axd1","ax_label":mm_dd})
        airport_chart_axis.append({"ax_class":"axd1","ax_label":mm_dd})
    elif i % 5 == 0:
        bu_chart_axis.append({"ax_class":"","ax_label":mm_dd})
        airport_chart_axis.append({"ax_class":"","ax_label":mm_dd})
    else:
        bu_chart_axis.append({"ax_class":"","ax_label":"·"})
        airport_chart_axis.append({"ax_class":"","ax_label":"·"})

# ── location×BU heatmap ───────────────────────────────────────────────────
# gather all loc×BU pairs present on D1
pairs = set()
for r in Q1:
    if r["d"]==D1:
        pairs.add((r["location"],r["bu"]))

# compute loc totals for ordering
loc_d1_total = defaultdict(float)
for r in Q1:
    if r["d"]==D1:
        loc_d1_total[r["location"]] += r["revenue"]

# group by location, ordered by loc_d1_total desc, then BU by d1 rev desc
locs_ordered = sorted(loc_d1_total.keys(), key=lambda l: -loc_d1_total[l])

loc_heatmap_rows = []
for loc in locs_ordered:
    bus_here = [(bu,d1_loc_bu[(loc,bu)]["rev"]) for (_loc,bu) in pairs if _loc==loc]
    bus_here.sort(key=lambda x: -x[1])
    n = len(bus_here)
    for idx,(bu,rev1) in enumerate(bus_here):
        b1 = d1_loc_bu[(loc,bu)]["bills"]
        r8 = d8_loc_bu.get((loc,bu),{"rev":0,"bills":0})
        r2 = d2_loc_bu.get((loc,bu),{"rev":0,"bills":0})
        rev8,b8 = r8["rev"],r8["bills"]
        t1 = rev1/b1 if b1 else 0
        t8 = rev8/b8 if b8 else 0
        ww_rev = wow(rev1,rev8)
        ww_b   = wow(b1,b8)
        ww_t   = wow(t1,t8)
        dod_r  = wow(rev1, r2["rev"]) if r2["rev"] else 0
        rev_bg,rev_fg = grad(ww_rev)
        b_bg,b_fg     = grad(ww_b)
        t_bg,t_fg     = grad(ww_t)
        sc,sig = signal_3x3(ww_b,ww_t)
        if idx==0:
            loc_cell = f'<td class="heat-bu" rowspan="{n}"><b>{loc}</b></td>'
            row_class = "grp-start"
        else:
            loc_cell = ""
            row_class = ""
        loc_heatmap_rows.append({
            "bu_name": bu,
            "bu_color": BU_COLOR.get(bu,"#999"),
            "airport": AIRPORT.get(loc,"?"),
            "d1_rev": f"฿{rev1/1000:.1f}K",
            "d1_bills": str(b1),
            "rev_bg": rev_bg,
            "rev_fg": rev_fg,
            "rev_delta": pct_str(ww_rev,1),
            "bills_bg": b_bg,
            "bills_fg": b_fg,
            "bills_delta": pct_str(ww_b,1),
            "ticket_bg": t_bg,
            "ticket_fg": t_fg,
            "ticket_delta": pct_str(ww_t,1),
            "signal_class": sc,
            "signal": sig,
            "loc_cell": loc_cell,
            "row_class": row_class,
        })

# ── MTD flags (per location) ──────────────────────────────────────────────
loc_mtd_flags = {}
for loc in AIRPORT:
    daily = [q3_loc[(d,loc)]["revenue"] for d in mtd_days]
    daily = [v for v in daily if v>0]
    if not daily:
        continue
    mtd_loc_avg = sum(daily)/len(daily)
    mtd_loc_high = max(daily)
    mtd_loc_low  = min(daily)
    d1_loc_rev = q3_loc[(D1,loc)]["revenue"]
    if d1_loc_rev <= mtd_loc_low:
        loc_mtd_flags[loc] = "🚨 NEW LOW"
    elif d1_loc_rev >= mtd_loc_high:
        loc_mtd_flags[loc] = "🔥 NEW HIGH"
    elif mtd_loc_avg>0 and d1_loc_rev < mtd_loc_avg*0.80:
        loc_mtd_flags[loc] = "<80% avg"

# ── Executive Insight bullets ─────────────────────────────────────────────
# rank BUs
bu_wows = {}
for bu in BU_ORDER:
    r1 = q2_day_bu[(D1,bu)]["revenue"]
    r8 = q2_day_bu[(D8,bu)]["revenue"]
    bu_wows[bu] = wow(r1,r8)

up_bus = [b for b in BU_ORDER if bu_wows[b]>0]
dn_bus = [b for b in BU_ORDER if bu_wows[b]<0]
if len(up_bus)>=3:
    pattern = "broad_growth"
elif len(dn_bus)>=3:
    pattern = "broad_decline"
elif wow_bills<0 and wow_ticket>0:
    pattern = "premium_shift"
elif wow_bills>5 and abs(wow_ticket)<2:
    pattern = "traffic_surge"
else:
    pattern = "balanced"

hero_bu = max(BU_ORDER, key=lambda b: bu_wows[b])
hero_r1 = q2_day_bu[(D1,hero_bu)]
hero_r8 = q2_day_bu[(D8,hero_bu)]
hero_b1,hero_b8 = hero_r1["bills"],hero_r8["bills"]
hero_t1 = hero_r1["revenue"]/hero_b1 if hero_b1 else 0
hero_t8 = hero_r8["revenue"]/hero_b8 if hero_b8 else 0
hero_ww  = bu_wows[hero_bu]
hero_wb  = wow(hero_b1,hero_b8)
hero_wt  = wow(hero_t1,hero_t8)

# top/bottom movers by loc×BU rev WoW
lb_wows = []
for k,r1 in d1_loc_bu.items():
    loc,bu = k
    r8 = d8_loc_bu.get(k,{"rev":0,"bills":0})
    if r8["rev"]>0:
        ww = wow(r1["rev"],r8["rev"])
        lb_wows.append((ww,loc,bu,r1["rev"]))

lb_wows.sort(key=lambda x:-x[0])
top3 = lb_wows[:3]
bot3 = lb_wows[-3:]

def mover_line(mw,loc,bu,rev):
    return f"• {loc} · {bu} {pct_str(mw,1)} (฿{rev/1000:.0f}K)"

# most material MTD flag
mtd_flag_loc = None
for loc in locs_ordered:
    if loc in loc_mtd_flags:
        mtd_flag_loc = loc
        break

pattern_text = {
    "broad_growth": "Broad growth: 3 of 5 BUs positive WoW — Subway, Khiang, and Vendi all advanced.",
    "broad_decline": "Broad decline: 3+ BUs posting negative WoW.",
    "premium_shift": "Premium shift: total bills declining while average ticket rising.",
    "traffic_surge": "Traffic surge: bills climbing strongly, ticket essentially flat.",
    "balanced": "Mixed signals: BU performance diverges, no single dominant pattern.",
}

bullets = []
bullets.append({"bullet_html":
    f"D1 SFB revenue <b>฿{d1_rev:,.0f}</b> ({pct_str(wow_rev,1)} WoW · {pct_str(dod_rev,1)} DoD · vs MTD avg {pct_str(mtd_vs,1)}), "
    f"{d1_bills:,} bills, avg ticket <b>฿{d1_ticket:,.0f}</b>"})
bullets.append({"bullet_html": f"<b>{pattern_text[pattern]}</b>"})
bullets.append({"bullet_html":
    f"⭐ <b>{hero_bu}</b> leading: WoW {pct_str(hero_ww,1)} (bills {pct_str(hero_wb,1)}, ticket {pct_str(hero_wt,1)})"})
if mtd_flag_loc:
    flag = loc_mtd_flags[mtd_flag_loc]
    bullets.append({"bullet_html": f"<b>{mtd_flag_loc}</b> hit {flag} this MTD period"})
else:
    # CRITICAL severity call-out
    for k,r1 in d1_loc_bu.items():
        loc,bu = k
        r8 = d8_loc_bu.get(k,{"rev":0,"bills":0})
        r2 = d2_loc_bu.get(k,{"rev":0,"bills":0})
        ww = wow(r1["rev"],r8["rev"]) if r8["rev"] else 0
        dd = wow(r1["rev"],r2["rev"]) if r2["rev"] else 0
        sev,_ = severity(ww,dd)
        if sev=="CRITICAL":
            bullets.append({"bullet_html":
                f"🚨 <b>{loc} · {bu}</b> CRITICAL — WoW {pct_str(ww,1)}, DoD {pct_str(dd,1)}"})
            break

top_lines = " | ".join(mover_line(*m) for m in top3)
bot_lines = " | ".join(mover_line(*m) for m in bot3)
bullets.append({"bullet_html": f"<b>Top location×BU movers</b>: {top_lines}"})
bullets.append({"bullet_html": f"🔻 <b>Weakest location×BU</b>: {bot_lines}"})

# ── severity counts ───────────────────────────────────────────────────────
sev_counts = defaultdict(int)
for k,r1 in d1_loc_bu.items():
    loc,bu = k
    r8 = d8_loc_bu.get(k,{"rev":0,"bills":0})
    r2 = d2_loc_bu.get(k,{"rev":0,"bills":0})
    ww = wow(r1["rev"],r8["rev"]) if r8["rev"] else 0
    dd = wow(r1["rev"],r2["rev"]) if r2["rev"] else 0
    sev,_ = severity(ww,dd)
    sev_counts[sev] += 1

# ── assemble data.json ───────────────────────────────────────────────────
data = {
 "scalars": {
  "subject": subject,
  "report_date_display": "27 Jun 2026",
  "weekday_en": "Sat",
  "weekday_th": "วันเสาร์",
  "status_emoji": status_emoji,
  "rev_K": rev_K,
  "wow_signed": pct_str(wow_rev,1),
  "wow_signed_full": pct_str(wow_rev,2),
  "dod_signed": pct_str(dod_rev,2),
  "mtd_signed": pct_str(mtd_vs,2),
  "bills_total": f"{d1_bills:,}",
  "bills_wow_signed": pct_str(wow_bills,2),
  "ticket": f"฿{d1_ticket:,.0f}",
  "ticket_wow_signed": pct_str(wow_ticket,2),
  "window_label": f"May 29 → Jun 27",
  "mtd_avg_K": f"฿{mtd_avg/1000:.0f} K",
  "mtd_label": f"Jun 1–27 ({len(mtd_days)} days)",
  "d8_display": "20 Jun",
  "surge_count": str(sev_counts.get("SURGE",0)),
  "generated_display": "28 Jun 2026",
  "loc_count": str(loc_count),
  "rev_delta_class": "delta-up" if wow_rev>=0 else "delta-down",
  "bills_delta_class": "delta-up" if wow_bills>=0 else "delta-down",
  "ticket_delta_class": "delta-up" if wow_ticket>=0 else "delta-down",
  "problem_count": str(sev_counts.get("CRITICAL",0)+sev_counts.get("HIGH",0)+sev_counts.get("WATCH",0)),
  "ok_count": str(sev_counts.get("SURGE",0)+sev_counts.get("POSITIVE",0)+sev_counts.get("NEUTRAL",0)),
 },
 "repeats": {
  "insight_bullets": bullets,
  "bu_chart_days": bu_chart_days,
  "bu_chart_axis": bu_chart_axis,
  "airport_chart_days": airport_chart_days,
  "airport_chart_axis": airport_chart_axis,
  "bu_legend_rows": bu_legend_rows,
  "airport_legend_rows": airport_legend_rows,
  "loc_heatmap_rows": loc_heatmap_rows,
 },
}

out = "/home/user/report/SFB/data.json"
with open(out,"w",encoding="utf-8") as f:
    json.dump(data,f,ensure_ascii=False,indent=1)
print(f"Wrote {out}")
print(f"D1={d1_rev:,.2f}  WoW={wow_rev:+.2f}%  DoD={dod_rev:+.2f}%  MTDavg={mtd_avg:,.2f}")
print(f"Bills={d1_bills}  Ticket={d1_ticket:.2f}")
print(f"Severity: {dict(sev_counts)}")
print(f"MTD flags: {loc_mtd_flags}")
print(f"Status: {status_emoji}")
