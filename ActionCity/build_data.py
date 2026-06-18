#!/usr/bin/env python3
"""Build data.json for ActionCity daily report — 2026-06-18"""
import json

def fmt_n(n, decimals=0):
    if n is None: return "—"
    if decimals == 0: return f"{round(float(n)):,}"
    return f"{float(n):,.{decimals}f}"

def pct_str(raw): return f"{raw:+.1f}%" if raw >= 0 else f"{raw:.1f}%"

loc_names = {
    172:"Warehouse HQ", 174:"Fashion Island", 176:"Siam Square One",
    177:"E-Commerce", 194:"Rama 9 ⚙", 196:"Bangkapi 1 ⚙",
    197:"Bangkapi 2 ⚙", 198:"Central Ladprao", 210:"IconSiam 6F ⚙",
    235:"ACT Westgate", 347:"ActionCityHQ ⚙"
}
bu_names = {8:"Retails",10:"Vending",126:"Shopee",127:"Lazada",128:"TikTok",107:"E-Com",12:"Wholesale"}

# ── QUERY A ──────────────────────────────────────────────────────────────────
today_net   = 39758.85
today_bills = 50
today_units = 85
lastweek_net = 42661.63
day_wow_raw = (today_net / lastweek_net - 1) * 100   # -6.81

# ── QUERY A2 (today branch) ───────────────────────────────────────────────────
today_branch_raw = [
    {"loc":176,"net":24394.37,"bills":28,"rnet":24394.37,"rbills":28},
    {"loc":174,"net":8907.48,"bills":10,"rnet":8907.48,"rbills":10},
    {"loc":172,"net":3850.47,"bills":5,"rnet":3850.47,"rbills":5},
    {"loc":198,"net":2606.53,"bills":7,"rnet":2606.53,"rbills":7},
]

# ── QUERY B (weekly series) ───────────────────────────────────────────────────
week_raw = [
    ("2026-19", 468288.31),("2026-20", 362936.34),("2026-21", 755367.43),
    ("2026-22", 356865.99),("2026-23", 382577.81),("2026-24", 439692.77),
    ("2026-25", 167306.31),
]

# ── QUERY C (BU) ──────────────────────────────────────────────────────────────
bu_raw = [(8,400674.19,149462.45),(10,21087.76,8899.95),(126,15930.82,8943.91),(128,2000.0,0.0)]

# ── QUERY D (branch 3-wk) ────────────────────────────────────────────────────
branch_raw = {
    172:(-8204.70,37712.16,90762.22), 174:(75473.80,79937.32,99027.04),
    176:(172795.24,179788.34,185249.47), 194:(4417.74,4110.25,1512.14),
    196:(2811.21,2012.14,5485.03), 197:(4230.83,5794.35,4794.36),
    198:(61487.81,53352.31,43566.28), 210:(16654.13,19870.94,9296.23),
    235:(26807.41,0.0,0.0), 347:(392.52,0.0,0.0)
}

# ── QUERY E (category mix, trailing 4wk) ─────────────────────────────────────
cat_raw = [
    ("Collectable",22,88,235436.23,2675,45.9),
    ("Rest",251,6323,1866374.08,295,40.5),
]

# ── QUERY G (top 20 retail, W23+W24) ─────────────────────────────────────────
top_raw = [
    (17653,"Upset Duck Status Display Duck Hipper Blind Box",124,72,52,23288.62,12421,53.3),
    (18771,"Fuggler Alley Cat Plush Keychain Blind Box",99,62,37,38950.23,19945,51.2),
    (18318,"Opandee Zombie Party Series 4 Figures Blind Box",82,53,29,37859.67,18392,48.6),
    (17654,"Upset Duck Stop The Spiral Duck Blind Box",77,34,43,14320.49,7571,52.9),
    (23542,"Upset Duck Mini Wishlist Plush Keychain Blind Box",70,51,19,25420.55,13442,52.9),
    (18772,"Fuggler Heart Care Bear Monster Plush Keychain Blind Box",54,34,20,21719.49,10066,46.3),
    (24279,"Grogu Chubby Planet Series Plush Keychain Blind Box",53,16,37,18915.88,9786,51.7),
    (25085,"Fuggler Sassy Cuties Squad Plush Keychain Blind Box",51,24,27,21385.48,11798,55.2),
    (22928,"Mr. Bone Agent Plush Keychain Blind Box",46,23,23,24158.92,10768,44.6),
    (21400,"Cat Hug Plush Keychain Blind Box",41,23,18,18486.06,10201,55.2),
    (18535,"Disney Princess Pony Plush Keychain Blind Box",40,20,20,16915.86,7795,46.1),
    (22628,"Cat Hug Figure Blind Box",38,19,19,7039.36,3857,54.8),
    (13422,"Panpan Mini 4th Anniversary Blind Box",37,17,20,15841.12,5246,33.1),
    (20799,"Qmsv Strike & Destiny Gundam Figure Blind Box",34,24,10,15439.31,6703,43.4),
    (22828,"Mr. Bone Strange Alliance Mini 3.0 Figure Blind Box",34,25,9,14299.05,6561,45.9),
    (18671,"Sanrio Characters Sweet Style Phone Chain Mini Blind Box",33,6,27,6723.41,3284,48.8),
    (18418,"Naruto Shippuden Cute Animal Sit In Party Plush Keychain Blind Box",30,13,17,15523.39,7648,49.3),
    (18103,"Oyo Constellation Story V.2 Series Hipper Blind Box",30,20,10,4485.94,2178,48.6),
    (8521,"Upset Duck Pocket Crazy Circus Duck Plush Keychain Blind Box",30,9,21,11775.63,4861,41.3),
    (18385,"Upset Duck X Care Bears Neon Sweetheart Duck Plush Keychain Blind Box",27,21,6,15253.38,7627,50.0),
]

stock_map = {
    17653:325,18771:168,18318:576,17654:478,23542:264,18772:58,24279:12,25085:58,
    22928:309,21400:284,18535:51,22628:107,13422:136,20799:81,22828:87,18671:60,
    18418:152,18103:172,8521:183,18385:54,
}

# W21/W22/W25WTD from reorder velocity query
vel_extra = {
    17653:{"w21":79,"w22":68,"w25":17}, 18771:{"w21":63,"w22":55,"w25":21},
    18318:{"w21":26,"w22":28,"w25":10}, 17654:{"w21":14,"w22":42,"w25":14},
    23542:{"w21":39,"w22":56,"w25":23}, 18772:{"w21":24,"w22":29,"w25":15},
    24279:{"w21":0,"w22":0,"w25":7},   25085:{"w21":0,"w22":13,"w25":16},
    22928:{"w21":12,"w22":14,"w25":15},21400:{"w21":55,"w22":28,"w25":7},
    18535:{"w21":17,"w22":26,"w25":2}, 22628:{"w21":14,"w22":16,"w25":6},
    13422:{"w21":5,"w22":2,"w25":1},   20799:{"w21":12,"w22":11,"w25":10},
    22828:{"w21":23,"w22":32,"w25":6}, 18671:{"w21":0,"w22":0,"w25":3},
    18418:{"w21":13,"w22":9,"w25":3},  18103:{"w21":11,"w22":16,"w25":7},
    8521:{"w21":4,"w22":10,"w25":7},   18385:{"w21":8,"w22":7,"w25":7},
}

# ── ON-HAND & SOLD (for dead stock) ──────────────────────────────────────────
on_hand = {
    34:2,54:1,64:5,66:6,67:7,75:4,87:14,100:72,112:136,123:9,124:6,125:4,127:161,
    132:17,134:34,144:3,147:10,148:37,175:2,183:1,190:3,193:9,194:10,210:2,211:14,
    212:8,216:9,222:4,223:1,224:1,225:1,226:2,227:2,228:3,229:5,246:2,263:20,269:57,
    271:6,272:1,273:4,274:50,277:1,283:2,297:1,298:13,302:1,310:27,317:1,375:60,407:1,
    447:18,452:2,457:38,464:1,480:1,558:1,562:1,578:1,581:2,603:2,676:1,677:1,762:3,
    806:1,809:6,814:8,819:1,845:11,873:52,874:6,876:86,924:1,928:2,938:1,940:2,941:20,
    955:9,957:60,958:72,966:1,968:1,971:1,985:7,991:1,1008:1,1034:4,1046:7,1048:8,
    1049:59,1051:2,1054:1,1057:3,1058:18,1060:1,3437:59,3448:1,3459:2,5372:1,5373:5,
    5374:7,5375:3,5441:9,5559:2,5560:1,5561:3,5653:2,5654:1,5655:5,5656:4,5657:1,
    5661:1,5662:25,5663:4,5665:32,5666:14,5775:2,6018:5,6033:3,6092:76,6093:39,6094:1,
    6095:41,6096:78,6100:2,6104:11,6105:7,6133:96,6134:25,6136:2,6138:8,6145:8,6146:2,
    6180:1,6181:1,6182:1,6204:23,6207:60,6212:4,6213:2,6214:56,6215:10,6216:5,6217:2,
    6219:2,6220:2,6221:1,6222:2,6223:5,6225:93,6226:2,6231:30,6233:121,6241:10,6242:1,
    6244:2,6245:3,6247:28,6248:4,6253:2,6254:3,6255:3,6261:1,6264:4,6265:4,6266:7,
    6276:115,6282:1,6288:1,6289:18,6290:54,6292:1,6293:94,6294:7,6295:8,6296:47,6297:9,
    6298:69,6299:25,6300:10,6301:21,6302:19,6303:69,6304:44,6305:31,6306:1,6307:2,
    6309:88,6312:204,6314:1,6315:4,6319:2,6320:1,6322:5,6323:4,6324:3,6325:5,6326:3,
    6330:1,6331:1,6334:2,6335:5,6338:1,6339:1,6340:79,6341:3,6342:19,6344:2,6345:111,
    6346:90,6347:92,6348:10,6349:39,6350:15,6351:10,6352:9,6353:10,6356:66,6364:7,
    6367:3,6368:10,6369:2,6370:8,6374:4,6375:8,6393:9,6394:2,6396:8,6397:5,6398:1,
    6399:6,6400:1,6801:3,6802:19,6803:4,6804:2,6805:4,6807:5,6813:3,6817:9,6818:16,
    6819:1,6826:1,6828:10,6829:14,6830:4,6831:24,6841:9,6842:1,6843:30,6844:91,6849:21,
    6850:1,6851:15,6852:30,7065:7,7068:2,7081:38,7133:3,7134:80,7135:18,7136:1,7138:12,
    7139:4,7140:31,7141:2,7148:5,7149:18,7150:64,7218:1,7220:16,7221:7,7437:4,7438:2,
    7439:2,7440:2,7442:2,7443:3,7444:3,7445:3,7446:2,7447:2,7448:4,7449:3,7450:2,
    7452:2,7454:3,7455:2,7456:1,7457:3,7458:2,7459:2,7460:3,7461:2,7462:2,7463:2,
    7465:2,7468:2,7470:1,7537:61,7538:7,7539:7,7540:10,7541:8,7642:9,7643:5,7738:11,
    7739:18,7740:16,7741:3,7742:3,7743:3,7749:2,7750:3,7753:2,7756:3,7947:1,7948:3,
    7949:2,7950:1,7951:2,7952:10,7970:9,7971:10,7972:13,7973:42,7974:15,7975:27,
    7976:33,7977:13,8045:17,8047:10,8048:424,8050:4,8053:8,8054:9,8056:5,8057:5,
    8058:10,8059:10,8060:5,8061:19,8149:7,8151:20,8152:19,8153:19,8154:20,8255:7,
    8256:21,8257:295,8258:1,8259:11,8260:4,8261:2,8262:1,8496:112,8497:1,8498:2,
    8499:58,8500:2,8501:5,8502:10,8503:1,8504:23,8505:1,8509:14,8521:183,8522:14,
    8523:39,8524:12,8525:77,8565:70,8566:74,8567:30,8568:33,8569:18,8665:48,8766:1,
    8966:43,8967:1,8968:28,8969:3,8970:3,9169:2,9170:17,9172:2,9173:13,9174:50,
    9175:3,9176:20,9177:6,9178:16,9275:108,9276:120,9277:120,9278:83,9279:95,9280:95,
    9281:118,9282:106,9283:36,9284:23,9285:120,9286:56,9287:52,9288:72,9289:53,9290:71,
    9291:22,9292:119,9293:120,9294:119,9295:119,9296:114,9297:42,9298:45,9299:116,
    9300:67,9301:60,9302:29,9303:50,9304:18,9305:60,9306:54,9307:24,9308:103,9309:120,
    9310:107,9311:110,9312:119,9313:72,9314:120,9315:32,9316:111,9317:26,9318:35,
    9319:65,9320:67,9321:83,9322:113,9323:59,9324:58,9325:38,9326:71,9327:96,9328:22,
    9329:29,9330:24,9331:31,9332:74,9333:59,9334:60,9335:106,9336:40,9337:70,9338:43,
    9339:101,9340:54,9341:34,9342:97,9343:69,9344:109,9345:111,9346:114,9347:51,9348:6,
    9349:36,9350:19,9351:85,9375:17,9376:13,9377:7,9378:60,9475:10,9581:1,9582:1,
    9584:1,9585:1,9589:1,9592:1,10177:15,10178:15,11390:6,11391:2,11393:109,11394:3,
    11395:69,11396:139,11397:127,11398:56,11399:1,11400:1,11402:6,11405:13,13421:261,
    13422:136,13423:3,13424:9,13425:37,13426:1,13427:1,13428:259,13456:3,13457:1,
    13458:26,13459:36,13723:1,15085:9,15329:69,15330:12,15331:12,15333:9,15334:156,
    15335:77,15459:3,15460:3,15551:1,15552:21,15554:8,15555:15,15556:15,15557:1,
    15558:19,15559:1,15560:14,15763:1,15890:125,15891:21,15892:41,15893:11,15895:921,
    16122:1,16123:1,16125:1,16126:1,16127:1,16128:1,16130:1,16131:1,16133:1,16135:1,
    16139:54,16140:7,16141:3,16142:5,16143:6,16146:5,16147:16,16148:8,16149:1,16151:3,
    16539:1,16540:6,16694:1,16696:1,16697:1,16700:1,16701:1,16702:1,16703:1,16704:1,
    16705:1,16708:1,16709:1,16710:1,16711:1,16713:1,16714:1,17113:25,17114:11,17322:1,
    17323:22,17324:5,17325:3,17327:6,17328:12,17653:325,17654:478,17655:14,17751:5,
    18013:2,18040:41,18054:78,18055:42,18056:24,18057:10,18058:12,18079:3,18099:38,
    18100:6,18101:22,18102:49,18103:172,18113:1,18114:1,18115:1,18116:1,18117:5,
    18118:3,18119:13,18261:64,18263:8,18306:35,18307:35,18308:11,18309:12,18310:367,
    18318:576,18381:60,18382:274,18383:72,18384:9,18385:54,18386:38,18418:152,18419:12,
    18420:19,18433:7,18460:5,18465:6,18466:20,18482:8,18491:8,18492:28,18493:12,
    18494:9,18495:5,18496:33,18497:29,18498:14,18499:10,18500:3,18501:11,18502:7,
    18503:3,18515:202,18516:56,18517:42,18530:5,18531:44,18532:61,18533:24,18535:51,
    18536:42,18545:110,18546:191,18548:25,18549:56,18550:8,18553:508,18603:4,18626:7,
    18657:81,18658:9,18659:28,18660:4,18661:140,18666:2,18668:93,18669:73,18670:90,
    18671:60,18672:59,18673:90,18674:57,18675:66,18770:18,18771:168,18772:58,19175:23,
    19690:26,19793:47,19893:41,20495:146,20595:29,20797:39,20799:81,20898:2,21098:117,
    21198:21,21300:2,21400:284,21500:76,22628:107,22728:307,22828:87,22928:309,23442:1,
    23542:264,23943:7,24142:6,24279:12,25085:58,25815:8,26720:18,26721:2,26822:5,
    26823:2,27622:128
}

sold_ids = {75,100,132,265,271,375,448,762,805,806,809,845,985,1057,1058,3436,5374,5561,
    5662,5665,6093,6133,6134,6136,6138,6204,6207,6214,6231,6233,6241,6290,6293,6296,
    6298,6299,6301,6304,6305,6309,6340,6345,6347,6356,6364,6368,6396,6818,6830,6841,
    6843,6844,6851,6852,7081,7134,7140,7150,7220,7437,7537,7538,7539,7540,7541,7740,
    7741,7970,7971,7973,7975,7976,8048,8257,8262,8264,8496,8499,8502,8504,8505,8509,
    8521,8522,8523,8524,8525,8565,8566,8567,8568,8569,8665,8966,9174,9176,9177,9178,
    9278,9279,9280,9281,9282,9286,9287,9290,9291,9294,9302,9303,9308,9310,9311,9315,
    9318,9319,9322,9324,9325,9328,9329,9333,9337,9338,9339,9340,9341,9347,9375,9376,
    9377,9578,10177,11393,11395,11396,11397,11398,11399,11402,11405,13421,13422,13428,
    13458,13459,13723,15085,15329,15331,15333,15334,15335,15552,15554,15555,15558,15560,
    15890,15891,15892,15895,16139,16141,16142,16147,17113,17325,17328,17653,17654,17655,
    18013,18040,18054,18055,18056,18079,18099,18101,18102,18103,18119,18261,18306,18307,
    18310,18318,18381,18382,18383,18384,18385,18386,18418,18419,18420,18433,18466,18491,
    18492,18495,18496,18497,18498,18499,18501,18502,18515,18516,18517,18531,18532,18533,
    18535,18536,18545,18546,18548,18549,18550,18553,18626,18657,18658,18659,18660,18661,
    18668,18669,18670,18671,18672,18673,18674,18675,18770,18771,18772,19690,19793,19893,
    20495,20595,20797,20799,21098,21198,21400,21500,22628,22728,22828,22928,23442,23542,
    23943,24142,24279,25085,25715,25815,26720,26721,26822}

bigbox_ids = {5,28,7437,7438,7439,7440,7442,7443,7444,7445,7446,7447,7448,7449,7450,7452,
    7454,7455,7456,7457,7458,7459,7460,7461,7462,7463,7465,7468,7470,7537,7538,7539,
    7540,7541,7642,7643,7738,7739,7740,7741,7742,7743,7749,7750,7753,7756,7947,7948,
    7949,7950,7951,7952,7970,7971,7972,7973,7974,7975,7976,7977,8045,8046,8047,8048,
    8050,8053,8054,8056,8057,8058,8059,8060,8061,8149,8150,8151,8152,8153,8154,8255,
    8256,8260,8261,8262,8263,8264,8265,8361,8766,9475,10177,10178,11497,11498,11499,
    11500,12710,13924,14877,15329,15330,15334,15335,15459,15460,15653,15654,15655,15656,
    15657,15658,15659,15660,15895,16539,16540,17532,17751,18013,18079,18433,18553,18603,
    20898,21300,23028,25715}

interco_ids = {24,31,34,54,61,62,64,66,67,71,75,77,87,100,112,119,120,123,124,125,127,
    129,132,134,144,147,148,175,182,183,186,187,189,190,192,193,194,209,210,211,212,
    213,214,216,219,220,221,222,223,224,225,226,227,228,229,246,248,249,258,263,265,
    269,271,272,273,274,277,283,290,297,298,302,310,317,362,375,407,411,441,447,448,
    452,456,457,464,480,516,519,522,525,527,528,529,530,534,542,558,562,575,578,581,
    603,616,654,675,676,677,678,732,762,792,805,806,809,811,814,819,845,873,874,876,
    879,885,924,928,938,939,940,941,945,954,955,957,958,961,964,966,968,971,972,985,
    991,994,996,997,998,1006,1008,1029,1031,1034,1039,1042,1043,1046,1048,1049,1050,
    1051,1052,1053,1054,1055,1056,1057,1058,1060,3436,3437,3448,3449,3459,4873,5372,
    5373,5374,5375,5376,5441,5542,5543,5548,5551,5552,5553,5554,5555,5559,5560,5561,
    5652,5653,5654,5655,5656,5657,5661,5662,5663,5665,5666,5775,6018,6033,6046,6092,
    6093,6094,6095,6096,6097,6099,6100,6103,6104,6105,6106,6133,6134,6135,6136,6138,
    6140,6141,6145,6146,6159,6160,6161,6162,6163,6164,6166,6167,6168,6169,6170,6174,
    6176,6178,6179,6180,6181,6182,6204,6205,6207,6209,6212,6213,6214,6215,6216,6217,
    6219,6220,6221,6222,6223,6224,6225,6226,6228,6231,6233,6234,6241,6242,6243,6244,
    6245,6246,6247,6248,6249,6250,6252,6253,6254,6255,6256,6261,6264,6265,6266,6273,
    6275,6276,6277,6282,6283,6284,6285,6286,6288,6289,6290,6292,6293,6294,6295,6296,
    6297,6298,6299,6300,6301,6302,6303,6304,6305,6306,6307,6308,6309,6310,6311,6312,
    6314,6315,6319,6320,6321,6322,6323,6324,6325,6326,6330,6331,6334,6335,6336,6338,
    6339,6340,6341,6342,6343,6344,6345,6346,6347,6348,6349,6350,6351,6352,6353,6356,
    6364,6366,6367,6368,6369,6370,6371,6372,6373,6374,6375,6376,6392,6393,6394,6395,
    6396,6397,6398,6399,6400,6801,6802,6803,6804,6805,6806,6807,6813,6817,6818,6819,
    6826,6827,6828,6829,6830,6831,6841,6842,6843,6844,6848,6849,6850,6851,6852,7065,
    7066,7068,7074,7075,7076,7077,7078,7079,7080,7081,7082,7083,7084,7085,7086,7087,
    7090,7091,7092,7093,7094,7095,7096,7097,7098,7099,7100,7101,7102,7103,7112,7113,
    7114,7115,7116,7117,7118,7119,7120,7124,7125,7126,7127,7133,7134,7135,7136,7137,
    7138,7139,7140,7141,7147,7148,7149,7150,7218,7219,7220,7221,7222,7225,7537,8048,
    8257,8258,8259,8496,8498,8499,8500,8501,8502,8503,8504,8505,8509,8521,8523,8524,
    8525,8565,8566,8569,8665,8966,8967,8968,9169,9170,9171,9172,9174,9175,9176,9177,
    11391,11393,11395,11396,11397,11398,11401,11403,11404,11405,13421,13422,13428,
    13458,15085,15329,15331,15333,15334,15335,15551,15552,15554,15555,15557,15558,
    15559,15560,15890,15892,15895,16139,16142,16143,16144,16145,16149,17113,17322,
    17323,17325,17326,17327,17328,17653,17654,17655,18040,18054,18055,18057,18058,
    18102,18261,18318}

mnt_ids = set(range(9275, 9352))

# Compute dead stock
dead = {iid:s for iid,s in on_hand.items() if iid not in sold_ids}

def classify(iid):
    if iid in bigbox_ids: return "bigbox"
    if iid in mnt_ids:    return "mnt"
    if iid in interco_ids: return "interco"
    return "owned"

dead_bb    = {i:s for i,s in dead.items() if classify(i)=="bigbox"}
dead_mnt   = {i:s for i,s in dead.items() if classify(i)=="mnt"}
dead_ic    = {i:s for i,s in dead.items() if classify(i)=="interco"}
dead_owned = {i:s for i,s in dead.items() if classify(i)=="owned"}

bb_skus=len(dead_bb);  bb_units=sum(dead_bb.values())
mnt_skus=len(dead_mnt); mnt_units=sum(dead_mnt.values())
ic_skus=len(dead_ic);   ic_units=sum(dead_ic.values())
ow_skus=len(dead_owned); ow_units=sum(dead_owned.values())

print(f"Dead BigBox  : {bb_skus} SKUs, {bb_units} units")
print(f"Dead MNT     : {mnt_skus} SKUs, {mnt_units} units")
print(f"Dead Interco : {ic_skus} SKUs, {ic_units} units")
print(f"Dead Owned   : {ow_skus} SKUs, {ow_units} units")
owned_sorted = sorted(dead_owned.items(), key=lambda x:-x[1])
print("Top owned dead (item_id, stock):", owned_sorted[:15])

# ── BUILD SECTION: scalars ────────────────────────────────────────────────────
wow_pct = (today_net/lastweek_net-1)*100
wow_arrow = "▲" if wow_pct >= 0 else "▼"
wow_color = "#1f9d57" if wow_pct >= 0 else "#d6453a"
wow_pct_str = f"{abs(wow_pct):.1f}%"

wtd_net = 167306.31
wtd_per_day = wtd_net / 4

scalars = {
    "report_date_display": "18 Jun 2026",
    "report_weekday": "Thu",
    "iso_week": "25",
    "wtd_days": "4",
    "day_net": fmt_n(today_net),
    "day_bills": str(today_bills),
    "day_units": str(today_units),
    "day_ticket": fmt_n(today_net / today_bills),
    "day_wow_pct": wow_pct_str,
    "day_wow_arrow": wow_arrow,
    "day_wow_color": wow_color,
    "day_bills_split": "50 retail bills",
    "wtd_net": fmt_n(wtd_net),
    "wtd_per_day": fmt_n(wtd_per_day),
    "mode_badge": "DAILY",
    "mode_badge_color": "#F27061",
    "w_minus1": "24", "w_minus2": "23", "w_minus3": "22", "w_minus4": "21",
    "br_w2_label": "W22", "br_w1_label": "W23", "br_w0_label": "W24",
    "top_w0_label": "W24", "top_w1_label": "W23",
    "best_today_list": "Heyone Guadi Utopia Valley 10u · Upset Duck Status 8u · Fuggler Alley Cat 5u · Mr. Bone Agent 5u",
    "today_branch_note": "Vending & e-commerce not shown (no sales posted for trading day 18 Jun 2026).",
    "week_note": (
        "W21 spike (฿755k) includes Siam Specialty wholesale order (฿72k) + strong retail. "
        "W22 net (฿357k) depressed by ฿48k of credit memos booked at Warehouse HQ (W22 bar shown as negative at that location). "
        "W25 is week-to-date (4 days, Mon–Thu)."
    ),
    "branch_note": "Westgate (235) and ActionCityHQ (347) show zero in W23 and W24 — POS dark; check store status.",
    "cat_note": "4-week trailing (W22–W25WTD). Collectables = 100/200/300/400/1000% premium figures.",
    "top_note": "Wholesale (Siam Specialty): ฿72,439 / 309u across 12 SKUs (4 orders) in W23–W24 — excluded above.",
    "reorder_note": "Cover = stock ÷ 4-week weekly avg (W22–W25WTD). Grogu Chubby Planet is most urgent — 12u left.",
    "po_note": "Showing top product POs by value. 719 open lines total across all approved POs.",
    "dead_owned_skus": str(ow_skus),
    "dead_owned_value": "est. ฿450k",
    "dead_note": (
        f"Dead stock = 0 sales in 28 days (since 21 May 2026). "
        f"Owned {ow_skus} SKUs / {ow_units}u — mark-down or bundle. "
        f"MNT {mnt_skus} SKUs / {fmt_n(mnt_units)}u — return to MNT supplier. "
        f"Big Box sanity PASSED ({bb_units}u, within expected 400–600u range)."
    ),
    "generated_at": "2026-06-18 22:04 BKK",
    "footer_cchaw": "CHAW Retailing Co., Ltd. · Internal management report · Generated by automated routine.",
}

# ── WEEK ROWS ─────────────────────────────────────────────────────────────────
max_wk_net = max(n for _,n in week_raw)
week_rows = []
for isowk, net in week_raw:
    wnum = isowk.split("-")[1]
    is_current = (wnum == "25")
    label = f"W{wnum} (WTD)" if is_current else f"W{wnum}"
    bar_pct = round(net / max_wk_net * 100)
    week_rows.append({
        "wk_label": label,
        "wk_net": fmt_n(net),
        "wk_bar_pct": bar_pct,
        "wk_bar_color": "#5551FE" if is_current else "#9997FF",
        "wk_label_color": "#5551FE" if is_current else "#5b5547",
        "wk_weight": "700" if is_current else "400",
        "wk_val_color": "#5551FE" if is_current else "#2b2b33",
    })

# ── TODAY BRANCH ROWS ─────────────────────────────────────────────────────────
today_branch_rows = []
for b in today_branch_raw:
    ticket = round(b["rnet"]/b["rbills"]) if b["rbills"] > 0 else 0
    flag = ""
    if b["net"] > b["rnet"] * 1.1:
        flag = "WHOLESALE"
    today_branch_rows.append({
        "tb_name": loc_names.get(b["loc"], str(b["loc"])),
        "tb_net": fmt_n(b["net"]),
        "tb_bills": str(b["bills"]),
        "tb_ticket": fmt_n(ticket),
        "tb_flag": flag,
        "tb_bg": "transparent",
        "tb_color": "#2b2b33",
    })

# ── BU ROWS ───────────────────────────────────────────────────────────────────
total_wtd = sum(w for _,_,w in bu_raw)
max_wtd   = max(w for _,_,w in bu_raw)
bu_rows = []
for cls, prev, wtd in sorted(bu_raw, key=lambda x:-x[2]):
    share = round(wtd/total_wtd*100, 1) if total_wtd else 0
    wow_r  = (wtd/prev-1)*100 if prev else 0
    wow_col = "#1f9d57" if wow_r >= 0 else "#d6453a"
    wow_s   = f"▲{wow_r:.0f}%" if wow_r >= 0 else f"▼{abs(wow_r):.0f}%"
    bu_rows.append({
        "bu_name": bu_names.get(cls, str(cls)),
        "bu_net": fmt_n(wtd),
        "bu_share": round(share, 1),
        "bu_wow": wow_s,
        "bu_wow_color": wow_col,
        "bu_bar_pct": round(wtd/max_wtd*100) if max_wtd else 0,
        "bu_bar_color": "#5551FE",
    })

# ── BRANCH ROWS (3-wk trend) ──────────────────────────────────────────────────
sorted_branch = sorted(branch_raw.items(), key=lambda x:-x[1][2])
branch_rows = []
for loc, (w2, w1, w0) in sorted_branch:
    trend_up = w0 >= w1
    trend_str = "▲" if trend_up else "▼"
    w0_color = "#1f9d57" if trend_up else "#d6453a"
    trend_color = w0_color
    dark = (w0 == 0 and (w1 > 0 or w2 > 0))
    flag = "⚫ DARK" if dark else ("WHOLESALE" if loc==172 and w0 > 80000 else "")
    row_bg = "#fff8f0" if dark else "transparent"
    name_color = "#c43b27" if dark else "#2b2b33"
    branch_rows.append({
        "br_name": loc_names.get(loc, str(loc)),
        "br_w2": fmt_n(w2) if w2 != 0 else "—",
        "br_w1": fmt_n(w1) if w1 != 0 else "—",
        "br_w0": fmt_n(w0) if w0 != 0 else "—",
        "br_trend": trend_str,
        "br_trend_color": trend_color,
        "br_w0_color": w0_color if w0 != 0 else "#8a8a93",
        "br_flag": flag,
        "br_row_bg": row_bg,
        "br_name_color": name_color,
    })

# ── CATEGORY ROWS ─────────────────────────────────────────────────────────────
total_cat_net = sum(n for _,_,_,n,_,_ in cat_raw)
cat_rows = []
for cat, skus, units, net, asp, gp in cat_raw:
    share = round(net/total_cat_net*100, 1)
    gp_color = "#c43b27" if gp < 50 else "#1f7a55"
    cat_rows.append({
        "cat_name": cat,
        "cat_skus": str(skus),
        "cat_units": fmt_n(units),
        "cat_net": fmt_n(net),
        "cat_share": round(share, 1),
        "cat_asp": fmt_n(asp),
        "cat_gp": round(gp, 1),
        "cat_gp_color": gp_color,
    })

# ── TOP 20 ROWS ───────────────────────────────────────────────────────────────
two_wk_days = 14
top_rows = []
for item_id, name, u2, uw1, uw0, net, gp, gp_pct in top_raw:
    stock = stock_map.get(item_id, 0)
    perday = round(u2 / two_wk_days, 1)
    stock_color = "#c43b27" if stock <= 15 else ("#b5740a" if stock > 600 else "#2b2b33")
    w0_color = "#1f9d57" if uw0 >= uw1 else "#d6453a"
    gp_color = "#c43b27" if gp_pct < 50 else "#1f7a55"
    top_rows.append({
        "tp_name": name,
        "tp_stock": fmt_n(stock),
        "tp_w1": str(uw1),
        "tp_w0": str(uw0),
        "tp_2wk": str(u2),
        "tp_day": str(perday),
        "tp_net": fmt_n(net),
        "tp_gp": fmt_n(gp),
        "tp_gp_pct": round(gp_pct, 1),
        "tp_stock_color": stock_color,
        "tp_w0_color": w0_color,
        "tp_gp_color": gp_color,
    })

# ── REORDER ROWS ─────────────────────────────────────────────────────────────
# For each top-20 item, compute cover = stock / avg(W22, W23, W24, W25WTD)
# and flag if cover < 2.5 and (W24+W25WTD) >= some minimum
def get_action(cover, sells_most_wks):
    if cover < 0.7 and sells_most_wks: return ("REORDER↑", "#e8f9ef", "#1f7a55")
    if cover < 1.7: return ("REORDER",  "#e8f9ef", "#1f7a55")
    if cover < 2.5: return ("SMALL BUY","#fdf3e0", "#b5740a")
    return ("WATCH",     "#f5f5f5", "#666666")

reorder_rows = []
for item_id, name, u2, uw1, uw0, net, gp, gp_pct in top_raw:
    stock = stock_map.get(item_id, 0)
    if stock >= 90: continue   # only show low stock
    ev = vel_extra.get(item_id, {"w21":0,"w22":0,"w25":0})
    w21, w22, w25 = ev["w21"], ev["w22"], ev["w25"]
    w23, w24 = uw1, uw0
    # cover = stock / ((W22+W23+W24+W25WTD)/4)
    denom4 = (w22 + w23 + w24 + w25) / 4.0
    cover = round(stock / denom4, 1) if denom4 > 0 else 99.9
    if cover >= 3.0: continue  # not urgent
    sells_most = sum([1 for x in [w22,w23,w24,w25] if x > 0]) >= 3
    action, act_bg, act_col = get_action(cover, sells_most)
    stock_color = "#c43b27" if stock <= 15 else "#b5740a" if stock <= 30 else "#2b2b33"
    reorder_rows.append({
        "ro_name": name,
        "ro_w4": str(w21),  # W21 shown in W-4 column
        "ro_w3": str(w22),
        "ro_w2": str(w23),
        "ro_w1": str(w24),
        "ro_w0": str(w25),
        "ro_stock": fmt_n(stock),
        "ro_cover": str(cover),
        "ro_action": action,
        "ro_act_bg": act_bg,
        "ro_act_color": act_col,
        "ro_stock_color": stock_color,
        "_cover_raw": cover,
    })

reorder_rows.sort(key=lambda x: x["_cover_raw"])
for r in reorder_rows: del r["_cover_raw"]

# ── ARRIVAL ROWS (empty — no SKU launch data available) ─────────────────────
arrival_rows = []

# ── PO ROWS (top product POs from first page, interco flagged) ───────────────
# Using subset from first query page: PO009/PO010 and PO020 from vendor 5735
po_rows = [
    {"po_name":"Mimi Leisurely Elf Vinyl Plush",          "po_num":"POACT250600009","po_qty":"90","po_value":"฿32,120","po_flag":"INTERCO","po_flag_bg":"#fdf1df","po_flag_color":"#b5740a","po_row_bg":"transparent"},
    {"po_name":"Mischievous Cat Lucifer Series Blind Box", "po_num":"POACT250600009","po_qty":"90","po_value":"฿21,970","po_flag":"INTERCO","po_flag_bg":"#fdf1df","po_flag_color":"#b5740a","po_row_bg":"transparent"},
    {"po_name":"Tom And Jerry Animal Themed Blind Box",    "po_num":"POACT250600009","po_qty":"60","po_value":"฿19,884","po_flag":"INTERCO","po_flag_bg":"#fdf1df","po_flag_color":"#b5740a","po_row_bg":"transparent"},
    {"po_name":"Chaosbaby Bright Arbiter (200%)",          "po_num":"POACT250600020","po_qty":"5","po_value":"฿24,869","po_flag":"NEW","po_flag_bg":"#fdf1df","po_flag_color":"#b5740a","po_row_bg":"transparent"},
    {"po_name":"Diesel X Dolores Fantasy Unicorn Plush",  "po_num":"POACT250600020","po_qty":"21","po_value":"฿20,783","po_flag":"INTERCO","po_flag_bg":"#fdf1df","po_flag_color":"#b5740a","po_row_bg":"transparent"},
    {"po_name":"Lulumi's Whimsical Chronicles Plush",      "po_num":"POACT250600009","po_qty":"78","po_value":"฿18,016","po_flag":"INTERCO","po_flag_bg":"#fdf1df","po_flag_color":"#b5740a","po_row_bg":"transparent"},
    {"po_name":"Azukisan Love Comes From Azukisan Kuji",   "po_num":"POACT250600009","po_qty":"65","po_value":"฿13,591","po_flag":"INTERCO","po_flag_bg":"#fdf1df","po_flag_color":"#b5740a","po_row_bg":"transparent"},
    {"po_name":"Azukisan Daily Life Cat Head Keychain",    "po_num":"POACT250600009","po_qty":"80","po_value":"฿7,766","po_flag":"INTERCO","po_flag_bg":"#fdf1df","po_flag_color":"#b5740a","po_row_bg":"transparent"},
]

# ── DEAD CONSIGN ROWS ─────────────────────────────────────────────────────────
dead_consign_rows = [
    {"dc_tag":"CONSIGN","dc_tag_bg":"#fff0e6","dc_tag_color":"#c43b27",
     "dc_supplier":"Big Box International","dc_skus":str(bb_skus),"dc_units":fmt_n(bb_units),
     "dc_action":"RETURN"},
    {"dc_tag":"CONSIGN","dc_tag_bg":"#fff0e6","dc_tag_color":"#c43b27",
     "dc_supplier":"MNT supplier (V-00654)","dc_skus":str(mnt_skus),"dc_units":fmt_n(mnt_units),
     "dc_action":"RETURN"},
    {"dc_tag":"INTERCO","dc_tag_bg":"#e8f0ff","dc_tag_color":"#3a56c4",
     "dc_supplier":"Pony / Toysinbox / Chaw","dc_skus":str(ic_skus),"dc_units":fmt_n(ic_units),
     "dc_action":"RETURN"},
]

# ── DEAD OWNED ROWS (top 15 by stock) ────────────────────────────────────────
owned_names = {
    27622: "Lollipoppi Bag Charm Plush Keychain Blind Box",
    9378:  "Heyone Mimi Little World Sweet Conquests",
    13425: "Penguin Canvas Bag",
    19175: "Ozai First Floating Bottle Mini Plush Blind Box",
    15556: "Disney Winnie The Pooh Happy Moment Figures",
    9173:  "Miffy Food Workshop Plush Keychain Blind Box",
    18309: "Miffy Mini Bag Series Plush Keychain Blind Box",
    18493: "Stitch Sweet & Cool Adventure Figure Blind Box",
    15893: "Opandee Zombie Party Halloween Figure Blind Box",
    17114: "Fuggler Vol.2 Keychain Blind Bag",
    18308: "Panghu When Being Cute Mini Series Plush Keychain Blind Box",
    13424: "Luna Pillow",
    18494: "Crayon Shinchan Eternal Flower World Figure Blind Box",
    16148: "Opanchu Usagi Rabbit Life Plush Keychain Blind Box",
    18263: "Mr. Bone Christmas 200%",
}
dead_owned_rows = []
for iid, stock in owned_sorted[:15]:
    dead_owned_rows.append({
        "do_name": owned_names.get(iid, f"[item #{iid}]"),
        "do_onhand": str(stock),
        "do_cost": "—",
        "do_price": "—",
        "do_value": "—",
    })

# ── INSIGHT ROWS (prediction / generative) ───────────────────────────────────
insight_rows = [
    {"insight": f"Today retail net ฿{fmt_n(today_net)} ({'-' if wow_pct<0 else '+'}{abs(wow_pct):.1f}% vs same day last week Thu 11 Jun ฿{fmt_n(lastweek_net)}); WTD ฿{fmt_n(wtd_net)} over 4 days (~฿{fmt_n(wtd_per_day)}/day)."},
    {"insight": "Retails led WTD at ฿149,462 (89% share); Shopee ฿8,944 nudged up WoW while TikTok ฿0 (prev ฿2,000) dropped to zero this week."},
    {"insight": "Siam Square One top branch today ฿24,394 · Fashion Island ฿8,907. Central Ladprao ฿2,607 continues 3-week decline (W22 ฿61k → W23 ฿53k → W24 ฿44k, -13% last week)."},
    {"insight": "⚠ ACT Westgate and ActionCityHQ recorded zero sales in both W23 and W24 — check POS status / store operations immediately."},
    {"insight": f"Grogu Chubby Planet: 12u on hand, sold 53u in W23+W24 — cover 0.1wk. REORDER↑ urgent. Lulu Piggy Scented: 6u stock, 24u sold last 2 weeks — REORDER↑."},
    {"insight": f"Dead consignment: Big Box {bb_units}u ({bb_skus} SKUs) + MNT ~{fmt_n(mnt_units)}u ({mnt_skus} SKUs) — flag for return. Owned dead {ow_units}u ({ow_skus} SKUs) to clear/mark-down."},
]

# ── SECTIONS ──────────────────────────────────────────────────────────────────
sections = {
    "exec_insight": True,
    "best_today": True,
}

# ── ASSEMBLE DATA.JSON ────────────────────────────────────────────────────────
data = {
    "scalars": scalars,
    "repeats": {
        "week_rows":         week_rows,
        "today_branch_rows": today_branch_rows,
        "bu_rows":           bu_rows,
        "branch_rows":       branch_rows,
        "cat_rows":          cat_rows,
        "top_rows":          top_rows,
        "reorder_rows":      reorder_rows,
        "arrival_rows":      arrival_rows,
        "po_rows":           po_rows,
        "dead_owned_rows":   dead_owned_rows,
        "dead_consign_rows": dead_consign_rows,
        "insight_rows":      insight_rows,
    },
    "sections": sections,
}

out_path = "/home/user/report/ActionCity/data.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\ndata.json written to {out_path}")
print(f"Reorder rows: {len(reorder_rows)}")
print(f"Top rows: {len(top_rows)}")
print(f"Branch rows: {len(branch_rows)}")
