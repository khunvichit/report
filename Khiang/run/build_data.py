import json, math

# ── DATES ──────────────────────────────────────────────────────────────────
REPORT_DATE      = "2026-06-19"
report_date_display = "19 June 2026"
report_date_short   = "19 มิ.ย."
prev_date_short     = "18 มิ.ย."
report_day_en       = "Friday"
d30_start           = "21 พ.ค."
mtd_month           = "June 2026"
generated_date      = "20 June 2026"
chaw_values         = "Curious · Team · Act Fast · Empowered · Simple"

def fmt_k(n):   # thousands comma, no decimal
    return f"{int(round(n)):,}"

def lerp_hex(a, b, t):
    ar,ag,ab = int(a[1:3],16),int(a[3:5],16),int(a[5:7],16)
    br,bg,bb = int(b[1:3],16),int(b[3:5],16),int(b[5:7],16)
    r=int(ar + t*(br-ar)); g=int(ag + t*(bg-ag)); bv=int(ab + t*(bb-ab))
    return f"#{r:02X}{g:02X}{bv:02X}"

# ── QUERY A: KPIs ───────────────────────────────────────────────────────────
walk_in_bills=143; walk_in_revenue=31069.0
staff_bills=76;    staff_revenue=12432.7
credit_notes=0
net_sales = walk_in_revenue + staff_revenue - credit_notes   # 43501.7
total_bills = walk_in_bills + staff_bills                    # 219
avg_ticket = round(net_sales / total_bills)                  # 199
signed_pct_raw = round((net_sales - 40000) / 40000 * 100, 1)
signed_pct = f"+{signed_pct_raw}" if signed_pct_raw >= 0 else str(signed_pct_raw)
walk_in_pct = round(walk_in_bills / total_bills * 100, 1)
staff_pct   = round(staff_bills  / total_bills * 100, 1)
target_icon = "🔥" if net_sales>=50000 else ("✅" if net_sales>=40000 else "⚠️")

# ── QUERY F: 5-day ──────────────────────────────────────────────────────────
qf = [("14/06/2026",172,31488.6),("15/06/2026",193,36478.5),("16/06/2026",158,27716.8),
      ("17/06/2026",163,34525.6),("18/06/2026",225,43790.5)]
avg_5d_raw    = sum(r[2] for r in qf)/len(qf)
avg_5d        = round(avg_5d_raw)            # 34800
avg_bills_5d  = round(sum(r[1] for r in qf)/len(qf))  # 182
avg_ticket_bench = round(avg_5d_raw / avg_bills_5d)   # 191
bills_arrow  = "↑" if total_bills >= avg_bills_5d else "↓"
ticket_arrow = "↑" if avg_ticket >= avg_ticket_bench  else "↓"

# ── QUERY I: MTD ─────────────────────────────────────────────────────────────
net_mtd_raw = 682084.3; mtd_trading_days = 19
avg_mtd = round(net_mtd_raw / mtd_trading_days)   # 35899
mtd_days = 19
mtd_signed_pct_raw = round((avg_mtd - 40000)/40000*100,1)
mtd_signed_pct = f"+{mtd_signed_pct_raw}" if mtd_signed_pct_raw>=0 else str(mtd_signed_pct_raw)

# ── QUERY H: 30-day + 35-day ─────────────────────────────────────────────────
# Per-day (date, staff_bills, staff_rev, walk_bills, walk_rev)
h_raw = [
  ("15/05/2026",74,13679.4,139,31218),(  "16/05/2026",74,11144.8,123,26853),
  ("17/05/2026",83,12228.9,138,28968),(  "18/05/2026",75,10443.4,132,29533),
  ("19/05/2026",55, 8242.8,133,30575),(  "20/05/2026",76,11338.7,114,24285),
  ("21/05/2026",47, 6224.0, 86,17322),(  "22/05/2026",87,15109.2,110,22623),
  ("23/05/2026",72,10007.0,112,25946),(  "24/05/2026",74,10707.6,117,26407),
  ("25/05/2026",63, 8525.5,132,32494),(  "26/05/2026",64,10427.6,123,31940),
  ("27/05/2026",85,12681.4,107,20012),(  "28/05/2026",65, 9930.8,121,26573),
  ("29/05/2026",71,10340.5,155,37022),(  "30/05/2026",75,11424.8,108,24169),
  ("31/05/2026",84,12473.9,132,27497),(  "01/06/2026",83,13023.7,131,27581),
  ("02/06/2026",54, 7957.9,131,29833),(  "03/06/2026",91,15291.8,112,25339),
  ("04/06/2026",66,10156.6,112,21643),(  "05/06/2026",67, 9948.8,123,27306),
  ("06/06/2026",67, 9763.0,140,32572),(  "07/06/2026",74,10333.6,112,27246),
  ("08/06/2026",64, 8598.2,104,20940),(  "09/06/2026",56, 9678.3, 89,20105),
  ("10/06/2026",52, 7971.2,133,33195),(  "11/06/2026",49, 7230.7,112,22488),
  ("12/06/2026",55, 7677.1,105,23508),(  "13/06/2026",59, 8358.7,118,26837),
  ("14/06/2026",75,10094.6, 97,21394),(  "15/06/2026",69, 8979.5,124,27499),
  ("16/06/2026",69,11105.8, 89,16611),(  "17/06/2026",60, 8850.6,103,25675),
  ("18/06/2026",73,10042.5,152,33748),(  "19/06/2026",76,12432.7,143,31069),
]
def parse_date(s):
    d,m,y=s.split("/"); return int(y)*10000+int(m)*100+int(d)

# Build per-day combined dict
day_data = {}
for (dt,sb,sr,wb,wr) in h_raw:
    k=parse_date(dt)
    day_data[k]={
        "dt":dt,"key":k,"staff_bills":sb,"staff_rev":sr,
        "walk_bills":wb,"walk_rev":wr,
        "bills":sb+wb,"net":sb+wb and (sr+wr)  # revenue sum
    }
    day_data[k]["net"]=sr+wr

# 30-day window: D30_START=2026-05-21 to 2026-06-19
d30_keys = sorted(k for k in day_data if 20260521 <= k <= 20260619)
net_30d_raw = sum(day_data[k]["net"] for k in d30_keys)
net_30d = round(net_30d_raw)
avg_30d = round(net_30d_raw / len(d30_keys))
total_bills_30d = sum(day_data[k]["bills"] for k in d30_keys)
avg_bills_30d = round(total_bills_30d / len(d30_keys))

# MTD line position
chart_max_val = max(day_data[k]["net"] for k in d30_keys)  # 47362.5
mtd_line_px = round(min(avg_mtd, chart_max_val)/chart_max_val*90)

# ── CHART DAYS (30-day bar chart) ───────────────────────────────────────────
chart_days=[]
chart_labels=[]
for k in d30_keys:
    d=day_data[k]
    rev=d["net"]
    bar_px=max(2,round(rev/chart_max_val*90))
    bar_color="#27AE60" if rev>=40000 else "#E74C3C"
    day_num=str(int(d["dt"].split("/")[0]))
    is_report = (k==20260619)
    bar_title=f"฿{fmt_k(rev)} ({d['dt']})"
    chart_days.append({"bar_px":bar_px,"bar_color":bar_color,"bar_title":bar_title})
    chart_labels.append({
        "day_label": day_num,
        "label_color":"#5551FE" if is_report else "#AAA",
        "label_weight":"700" if is_report else "400"
    })

# ── 5-WEEK CUSTOMER TABLE ────────────────────────────────────────────────────
# week w (1=newest,5=oldest) covers 7 days ending REPORT_DATE-(w-1)*7
# W1: Jun 13-19, W2: Jun 6-12, W3: May 30-Jun 5, W4: May 23-29, W5: May 16-22
week_ranges = [
    (20260516,20260522,"16–22 พ.ค."),
    (20260523,20260529,"23–29 พ.ค."),
    (20260530,20260605,"30 พ.ค.–5 มิ.ย."),
    (20260606,20260612,"6–12 มิ.ย."),
    (20260613,20260619,"13–19 มิ.ย."),
]
week_data=[]
for (s,e,lbl) in week_ranges:
    ks=[k for k in day_data if s<=k<=e]
    wb=sum(day_data[k]["walk_bills"] for k in ks)
    sb=sum(day_data[k]["staff_bills"] for k in ks)
    tb=wb+sb
    week_data.append({"label":lbl,"walk":wb,"staff":sb,"total":tb})

def week_pct(cur,prev):
    if prev==0: return "",""
    p=round((cur-prev)/prev*100,1)
    pct_str=("▲+" if p>=0 else "▼")+str(p)+"%"
    color="#27AE60" if p>=0 else "#E74C3C"
    return pct_str,color

week_headers=[]
walk_cells=[]; staff_cells=[]; total_cells=[]
for i,wd in enumerate(week_data):
    is_cur=(i==4)
    hc="#5551FE" if is_cur else "#888"
    hb="#EEECFF" if is_cur else "#F8F9FA"
    week_headers.append({"label":wd["label"],"head_color":hc,"head_bg":hb})
    wt=700 if is_cur else 400
    wb2="#EEECFF" if is_cur else "#FFFFFF"
    prev_wd=week_data[i-1] if i>0 else None
    for seg,cells in [("walk",walk_cells),("staff",staff_cells),("total",total_cells)]:
        val=wd[seg]
        if prev_wd is None:
            pct_s,pct_c="","#888"
        else:
            pct_s,pct_c=week_pct(val,prev_wd[seg])
        cells.append({
            "val":f"{val:,}",
            "pct":pct_s,
            "color":pct_c if pct_s else "#888",
            "weight":str(wt),
            "bg":wb2
        })

# ── 7-DAY HEATMAP ────────────────────────────────────────────────────────────
# Query J data (14 days Jun 6-19)
j_data = {
    20260606:(207,42335),20260607:(186,37579.6),20260608:(168,29538.2),
    20260609:(145,29783.3),20260610:(185,41166.2),20260611:(161,29718.7),
    20260612:(160,31185.1),20260613:(177,35195.7),20260614:(172,31488.6),
    20260615:(193,36478.5),20260616:(158,27716.8),20260617:(163,34525.6),
    20260618:(225,43790.5),20260619:(219,43501.7)
}
def avg_ticket_j(bills,rev): return round(rev/bills) if bills else 0

heatmap_7d_keys=sorted(k for k in j_data if 20260613<=k<=20260619)
h7_net=[j_data[k][1] for k in heatmap_7d_keys]
h7_bills=[j_data[k][0] for k in heatmap_7d_keys]
h7_ticket=[avg_ticket_j(j_data[k][0],j_data[k][1]) for k in heatmap_7d_keys]

def col_shade(vals,i,lo_color="#FBF3EA",hi_color="#C9C7FF"):
    lo,hi=min(vals),max(vals)
    t=0.5 if hi==lo else (vals[i]-lo)/(hi-lo)
    return lerp_hex(lo_color,hi_color,t)

thai_wd=["อา","จ","อ","พ","พฤ","ศ","ส"]  # Sun=0..Sat=6
def thai_weekday(key):
    y,m,d=key//10000,(key//100)%100,key%100
    import datetime
    wd=datetime.date(y,m,d).weekday()  # Mon=0..Sun=6
    thai_idx=(wd+1)%7  # Mon=1,Tue=2,...,Sun=0
    return thai_wd[thai_idx]

def wow_calc(k,cur_rev):
    prev_k=k-7  # same weekday last week
    if prev_k not in j_data or j_data[prev_k][1]==0:
        return "—","#888",400
    prev=j_data[prev_k][1]
    p=round((cur_rev-prev)/prev*100,1)
    s=("+" if p>=0 else "")+str(p)+"%"
    c="#27AE60" if p>=0 else "#E74C3C"
    w=700 if abs(p)>=10 else 400
    return s,c,w

heatmap_rows=[]
for i,k in enumerate(heatmap_7d_keys):
    bills_v,rev_v=j_data[k]
    ticket_v=avg_ticket_j(bills_v,rev_v)
    is_report=(k==20260619)
    day_w=700 if is_report else 400
    rev_bg=col_shade(h7_net,i)
    bills_bg=col_shade(h7_bills,i)
    ticket_bg=col_shade(h7_ticket,i)
    rev_weight=700 if rev_v==max(h7_net) else 400
    bills_weight=700 if bills_v==max(h7_bills) else 400
    ticket_weight=700 if ticket_v==max(h7_ticket) else 400
    wow_pct_s,wow_col,wow_w=wow_calc(k,rev_v)
    y2=k//10000; m2=(k//100)%100; d2=k%100
    lbl_th=f"{thai_weekday(k)} {d2}/{m2}"
    heatmap_rows.append({
        "day_label_th":lbl_th,"day_weight":str(day_w),
        "rev":fmt_k(rev_v),"rev_bg":rev_bg,"rev_fg":"#2C3E50","rev_weight":str(rev_weight),
        "bills":str(bills_v),"bills_bg":bills_bg,"bills_fg":"#2C3E50","bills_weight":str(bills_weight),
        "ticket":fmt_k(ticket_v),"ticket_bg":ticket_bg,"ticket_fg":"#2C3E50","ticket_weight":str(ticket_weight),
        "wow_pct":wow_pct_s,"wow_color":wow_col,"wow_weight":str(wow_w)
    })

# ── QUERY B: TOP 10 ALL / TOP 10 RICE ────────────────────────────────────────
rice_list={"K008","K013","K016","K017","K037","K038","K039","K040","K041","K042","K043","K044","K045","K046","K047"}
fc_pct_map={"K037":26.2,"K038":24.3,"K039":23.3,"K040":29.7,"K041":26.1,"K042":23.3,"K043":25.3,"K045":29.9,"K046":22.6,"K047":29.1,"K008":27.2,"K013":26.0}

b_raw=[
    ("K008","ข้าวผัดโบราณ",10),("K013","ข้าวกะเพราไก่คาราเกะ",10),("K014","มาม่าผัดกะเพราไก่",12),
    ("K015","มาม่าต้มยำทรงเครื่อง",11),("K016","ไข่กระทะ",1),("K017","ข้าวผัดอเมริกัน",2),
    ("K018","แกงจืดเต้าหู้หมูสับ",11),("K019","ต้มยำกุ้ง",4),("K020","หมูยอทอด",9),
    ("K021","กุยช่ายกรอบ",16),("K023","ไข่ดาว",123),("K024","ไข่เจียว",14),
    ("K025","ข้าวสวย",6),("K026","กุนเชียง",2),("K028","โค้ก",79),("K029","โค้ก ซีโร่",3),
    ("K030","ชามะนาว",2),("K031","เก็กฮวย",2),("K032","ชาไทย (แก้ว)",3),
    ("K036","ลูกตาลลอยแก้ว",2),("K037","ข้าวผัดกะเพราหมูสับ",66),("K038","ข้าวผัดกะเพราไก่ชิ้น",34),
    ("K039","ข้าวไก่กระเทียม",6),("K040","ข้าวหมูกระเทียม",10),("K041","ข้าวไข่ยู่ยี่",16),
    ("K042","ข้าวกะเพราดิบเถือน",15),("K043","ข้าวกะเพราเทพหมู",22),("K045","ข้าวกะเพราเปิดย่าง",30),
    ("K046","ข้าวไก่ผัดน้ำมันหอย",7),("K047","ข้าวหมูผัดน้ำมันหอย",5),
    ("K056","Minere Mineral Water 600 Ml",41),("K057","กุยช่ายแซ่บ",13)
]
b_sorted=sorted(b_raw,key=lambda x:-x[2])

# 5d avg map
c_map={
    "K008":round(66/5),"K013":round(32/5),"K014":round(68/5),"K015":round(39/5),
    "K017":round(2/2),"K018":round(47/5),"K019":round(30/5),"K020":round(41/5),
    "K021":round(40/5),"K023":round(526/5),"K024":round(72/5),"K025":round(38/5),
    "K026":round(9/4),"K028":round(330/5),"K029":round(31/4),"K030":round(8/2),
    "K031":round(9/3),"K032":round(13/5),"K036":round(5/4),"K037":round(274/5),
    "K038":round(121/5),"K039":round(50/5),"K040":round(57/5),"K041":round(72/5),
    "K042":round(49/5),"K043":round(83/5),"K045":round(94/5),"K046":round(16/4),
    "K047":round(23/5),"K056":round(127/5),"K057":round(22/4)
}

def badge(qty, avg5d):
    if avg5d is None: return "New","#D1ECF1","#0C5460","+New"
    if avg5d==0: return "New","#D1ECF1","#0C5460","+New"
    p=round((qty-avg5d)/avg5d*100,1)
    s=("+" if p>=0 else "")+str(p)+"%"
    if p>=15: return s,"#D4EDDA","#155724",s
    elif p<=-10: return s,"#F8D7DA","#721C24",s
    else: return s,"#FEF3CD","#856404",s

def build_top_rows(items, include_fc=False):
    rows=[]
    for rank_i,(itemid,name,qty) in enumerate(items,1):
        avg5d=c_map.get(itemid)
        avg5d_disp=str(avg5d) if avg5d else "—"
        lbl,bb,bf,_=badge(qty,avg5d)
        star="⭐ " if itemid in rice_list else ""
        row={
            "rank":str(rank_i),
            "itemid":itemid,
            "name":star+name,
            "qty":str(qty),
            "avg5d":avg5d_disp,
            "badge_label":lbl,
            "badge_bg":bb,
            "badge_fg":bf,
            "row_bg":"#FFFFFF" if rank_i%2==1 else "#FAFAFA"
        }
        if include_fc:
            fc=fc_pct_map.get(itemid)
            row["fc_pct"]=f"{fc}%" if fc else "—"
        rows.append(row)
    return rows

top10_all  = build_top_rows(b_sorted[:10])
rice_sorted= sorted([(id,n,q) for (id,n,q) in b_raw if id in rice_list],key=lambda x:-x[2])
top10_rice = build_top_rows(rice_sorted[:10], include_fc=True)

# Group digest rice lines
rice_top10_lines_list=[]
for rank_i,(itemid,name,qty) in enumerate(rice_sorted[:10],1):
    avg5d=c_map.get(itemid)
    if avg5d and avg5d>0:
        p=round((qty-avg5d)/avg5d*100,1)
        pct_s=("+" if p>=0 else "")+str(p)+"%"
    else:
        pct_s="New"
    rice_top10_lines_list.append(f"{rank_i}. {itemid} {name} — {qty} ({pct_s})")
rice_top10_lines="\n".join(rice_top10_lines_list)

# ── HOURLY TABLE ─────────────────────────────────────────────────────────────
# Revenue benchmarks (display)
rev_bench={0:1149,1:763,2:373,3:356,4:240,5:166,6:538,7:1636,8:1910,9:3223,
           10:3827,11:4673,12:5768,13:3631,14:4196,15:3000,16:3813,17:2969,
           18:3641,19:3069,20:3080,21:2162,22:1562,23:553}
# Bill benchmark derived
bill_bench_total=298; rev_bench_total=sum(rev_bench.values())
bill_bench={h:max(1,round(rev_bench[h]/rev_bench_total*bill_bench_total)) for h in range(24)}

today_h={
    0:(6,1566.5),1:(11,1879.7),2:(5,858.7),3:(1,265.5),4:(0,0),5:(1,85.5),
    6:(5,621.9),7:(6,1226.1),8:(9,1314.1),9:(10,1881.5),10:(11,2615.3),
    11:(17,3349.5),12:(16,3565.0),13:(13,3322.2),14:(9,1216.7),15:(4,681.0),
    16:(14,2740.0),17:(16,3010.1),18:(17,2811.9),19:(17,3910.6),20:(12,2579.7),
    21:(9,2152.2),22:(6,835.0),23:(4,1013.0)
}
prev_h={
    1:(3,332.0),2:(2,249.5),3:(1,290.0),5:(3,509.0),6:(2,200.7),7:(5,680.5),
    8:(12,2157.6),9:(8,1497.5),10:(8,1616.0),11:(8,1900.2),12:(26,3970.9),
    13:(21,4111.2),14:(11,2009.7),15:(11,2458.6),16:(18,2298.7),17:(8,1124.6),
    18:(16,3162.5),19:(20,5959.7),20:(15,3542.0),21:(16,3772.4),22:(10,1792.2),
    23:(1,155.0)
}

# Anomalies: hours where today_bills < bill_bench * 0.50
anomaly_hours=set()
for h in range(24):
    tb_h=today_h.get(h,(0,0))[0]
    if tb_h < bill_bench[h]*0.50:
        anomaly_hours.add(h)
anomaly_count=len(anomaly_hours)

# Top 3 per hour
top3_map={
    0:"ไข่ดาว ×5<br>โค้ก ×5<br>ข้าวผัดกะเพราหมูสับ ×2",
    1:"ไข่ดาว ×7<br>ข้าวผัดกะเพราหมูสับ ×6<br>ข้าวกะเพราเทพหมู ×3",
    2:"ไข่ดาว ×3<br>โค้ก ×2<br>ข้าวกะเพราเปิดย่าง ×2",
    3:"ข้าวผัดกะเพราหมูสับ ×1<br>ข้าวผัดกะเพราไก่ชิ้น ×1<br>กุยช่ายแซ่บ ×1",
    4:"—",
    5:"ข้าวไข่ยู่ยี่ ×1",
    6:"ข้าวผัดกะเพราไก่ชิ้น ×3<br>ไข่เจียว ×2<br>ข้าวผัดกะเพราหมูสับ ×2",
    7:"แกงจืดเต้าหู้หมูสับ ×2<br>ไข่ดาว ×2<br>ข้าวสวย ×2",
    8:"ไข่ดาว ×4<br>ข้าวผัดกะเพราหมูสับ ×3<br>ข้าวผัดกะเพราไก่ชิ้น ×3",
    9:"ไข่ดาว ×6<br>โค้ก ×5<br>ข้าวผัดกะเพราไก่ชิ้น ×3",
    10:"ไข่ดาว ×9<br>โค้ก ×5<br>ข้าวผัดกะเพราหมูสับ ×4",
    11:"ไข่ดาว ×12<br>โค้ก ×10<br>ข้าวผัดกะเพราหมูสับ ×8",
    12:"โค้ก ×12<br>ไข่ดาว ×11<br>ข้าวผัดกะเพราหมูสับ ×5",
    13:"ไข่ดาว ×15<br>โค้ก ×8<br>ข้าวกะเพราไก่คาราเกะ ×2",
    14:"Minere Mineral Water… ×4<br>ไข่ดาว ×3<br>ข้าวผัดกะเพราหมูสับ ×3",
    15:"ข้าวสวย ×2<br>ข้าวผัดโบราณ ×1<br>แกงจืดเต้าหู้หมูสับ ×1",
    16:"ไข่ดาว ×5<br>ข้าวผัดกะเพราไก่ชิ้น ×5<br>Minere Mineral Water… ×4",
    17:"ไข่ดาว ×9<br>โค้ก ×6<br>ข้าวผัดกะเพราหมูสับ ×6",
    18:"ไข่ดาว ×6<br>ข้าวผัดกะเพราหมูสับ ×6<br>ข้าวผัดกะเพราไก่ชิ้น ×4",
    19:"ไข่ดาว ×11<br>ข้าวผัดกะเพราหมูสับ ×7<br>Minere Mineral Water… ×7",
    20:"ไข่ดาว ×6<br>โค้ก ×3<br>Minere Mineral Water… ×3",
    21:"ไข่ดาว ×4<br>ข้าวผัดกะเพราหมูสับ ×3<br>แกงจืดเต้าหู้หมูสับ ×2",
    22:"โค้ก ×3<br>ข้าวกะเพราเปิดย่าง ×3<br>ไข่ดาว ×1",
    23:"ไข่ดาว ×3<br>ข้าวกะเพราเทพหมู ×3<br>โค้ก ×2"
}

hourly_rows=[]
for h in range(24):
    cb,cr=today_h.get(h,(0,0))
    pb,pr=prev_h.get(h,(0,0))
    is_anom=(h in anomaly_hours)
    row_bg="#FFEBEE" if is_anom else ("#FFFFFF" if h%2==0 else "#FAFAFA")
    hflag=" 🚨" if is_anom else ""
    hcolor="#C62828" if is_anom else "#2C3E50"
    cur_r=f"฿{fmt_k(cr)}" if cr else "—"
    prev_r=f"฿{fmt_k(pr)}" if pr else "—"
    if cr>0 and pr>0:
        chg=round((cr-pr)/pr*100,1)
        change_s=("+" if chg>=0 else "")+str(chg)+"%"
        change_c="#27AE60" if chg>=0 else "#E74C3C"
        change_w="700" if abs(chg)>=20 else "400"
    elif cr>0 and pr==0:
        change_s="New"; change_c="#0C5460"; change_w="400"
    elif cr==0 and pr>0:
        change_s="-100%"; change_c="#E74C3C"; change_w="700"
    else:
        change_s="—"; change_c="#888"; change_w="400"
    prev_color="#888" if pr==0 else "#2C3E50"
    cur_color="#C62828" if is_anom else ("#2C3E50" if cr>0 else "#AAA")
    hourly_rows.append({
        "hour":f"{h:02d}:00",
        "hour_flag":hflag,
        "hour_color":hcolor,
        "prev_rev":prev_r,
        "prev_color":prev_color,
        "cur_rev":cur_r,
        "cur_color":cur_color,
        "change_pct":change_s,
        "change_color":change_c,
        "change_weight":change_w,
        "bench":fmt_k(rev_bench[h]),
        "top3":top3_map.get(h,"—"),
        "row_bg":row_bg
    })

# ── PROMO WEEKLY TREND (Query G2) ───────────────────────────────────────────
# Aggregated per week for staff10 (-9.81) and set50 (-16.20)
# Week 5(May16-22), 4(May23-29), 3(May30-Jun5), 2(Jun6-12), 1(Jun13-19)
promo_weeks={
    5:{"staff10":211,"set50":329},
    4:{"staff10":226,"set50":329},
    3:{"staff10":216,"set50":239},
    2:{"staff10":180,"set50":297},
    1:{"staff10":186,"set50":343}
}
staff10_cells=[]; set50_cells=[]
for i,w in enumerate([5,4,3,2,1]):
    wd=promo_weeks[w]
    is_cur=(w==1)
    wt=700 if is_cur else 400
    bg="#EEECFF" if is_cur else "#FFFFFF"
    prev_w=promo_weeks.get(w+1)
    for promo,cells in [("staff10",staff10_cells),("set50",set50_cells)]:
        val=wd[promo]
        if prev_w is None:
            pct_s=""; pct_c="#888"
        else:
            pv=prev_w[promo]
            if pv==0: pct_s=""; pct_c="#888"
            else:
                p=round((val-pv)/pv*100,1)
                pct_s=("▲+" if p>=0 else "▼")+str(p)+"%"
                pct_c="#27AE60" if p>=0 else "#E74C3C"
        cells.append({
            "val":f"{val:,}",
            "pct":pct_s,
            "color":pct_c,
            "weight":str(wt),
            "bg":bg
        })

# ── ASSEMBLE data.json ───────────────────────────────────────────────────────
data={
    "scalars":{
        "report_date_display":report_date_display,
        "report_day_en":report_day_en,
        "net_sales":fmt_k(net_sales),
        "signed_pct":signed_pct,
        "target_icon":target_icon,
        "avg_5d":fmt_k(avg_5d),
        "total_bills":str(total_bills),
        "avg_bills":str(avg_bills_5d),
        "bills_arrow":bills_arrow,
        "walk_in_bills":str(walk_in_bills),
        "walk_in_revenue":fmt_k(walk_in_revenue),
        "walk_in_pct":str(walk_in_pct),
        "staff_bills":str(staff_bills),
        "staff_revenue":fmt_k(staff_revenue),
        "staff_pct":str(staff_pct),
        "avg_ticket":str(avg_ticket),
        "avg_ticket_bench":str(avg_ticket_bench),
        "ticket_arrow":ticket_arrow,
        "net_30d":fmt_k(net_30d),
        "avg_30d":fmt_k(avg_30d),
        "d30_start":d30_start,
        "report_date_short":report_date_short,
        "net_mtd":fmt_k(int(round(net_mtd_raw))),
        "avg_mtd":fmt_k(avg_mtd),
        "mtd_days":str(mtd_days),
        "mtd_month":mtd_month,
        "mtd_signed_pct":mtd_signed_pct,
        "mtd_line_px":str(mtd_line_px),
        "anomaly_count":str(anomaly_count),
        "staff10_bills":str(33),
        "staff10_status":"Active",
        "staff10_badge_bg":"#D4EDDA",
        "staff10_badge_fg":"#155724",
        "set50_bills":str(53),
        "set50_status":"Active",
        "set50_badge_bg":"#D4EDDA",
        "set50_badge_fg":"#155724",
        "prev_date_short":prev_date_short,
        "avg_bills_30d":str(avg_bills_30d),
        "generated_date":generated_date,
        "chaw_values":chaw_values,
        "report_year":"2026"
    },
    "repeats":{
        "chart_days":chart_days,
        "chart_labels":chart_labels,
        "week_headers":week_headers,
        "walk_cells":walk_cells,
        "staff_cells":staff_cells,
        "total_cells":total_cells,
        "heatmap_rows":heatmap_rows,
        "top10_all":top10_all,
        "top10_rice":top10_rice,
        "hourly_rows":hourly_rows,
        "staff10_cells":staff10_cells,
        "set50_cells":set50_cells
    },
    "sections":{
        "alert_banner": anomaly_count > 0,
        "promo": True
    }
}

with open("/home/user/report/Khiang/run/data.json","w",encoding="utf-8") as f:
    json.dump(data,f,ensure_ascii=False,indent=2)

print(f"✅ data.json written")
print(f"   net_sales={fmt_k(net_sales)}  bills={total_bills}  anomalies={anomaly_count}")
print(f"   avg_mtd={fmt_k(avg_mtd)}  avg_30d={fmt_k(avg_30d)}")
print(f"   rice_top10_lines=\\n{rice_top10_lines}")
print(f"   promo_w5_staff10={promo_weeks[5]['staff10']}  promo_w1_staff10={promo_weeks[1]['staff10']}")
