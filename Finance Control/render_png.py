#!/usr/bin/env python3
"""render_png.py — CHAW Finance Control snapshot PNG (KPI meter + Executive Summary).
Reads render.json (from fc_build_data.py). Uses bundled Poppins + Noto Sans Thai (per-glyph fallback)
so Thai names render. Usage: python3 render_png.py render.json fc-report-snapshot.png"""
import sys, json, os, textwrap
import matplotlib; matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

RJ = sys.argv[1] if len(sys.argv) > 1 else "render.json"
OUT = sys.argv[2] if len(sys.argv) > 2 else "fc-report-snapshot.png"
D = json.load(open(RJ, encoding="utf-8"))
S = D["scalars"]; R = D["repeats"]; SEC = D["sections"]

HERE = os.path.dirname(os.path.abspath(__file__))
for f in ["Poppins-400.ttf","Poppins-700.ttf","NotoThai-400.ttf","NotoThai-700.ttf"]:
    fm.fontManager.addfont(os.path.join(HERE,"fonts",f))
plt.rcParams["font.family"] = ["Poppins","Noto Sans Thai"]

# CHAW palette
PURPLE="#5551FE"; CORAL="#F27061"; CREAM="#F5EDE4"; INK="#1B2A4A"; WHITE="#FFFFFF"
GREY="#777777"; BORDER="#E0DCD3"
RED="#FBE4E0"; AMBER="#FFF3E0"; GREEN="#E8F5E9"; CORALBG="#F8C8C0"

W = 1180; LM = 30; CW = W - 2*LM
rows = []   # drawing ops collected, then we know height

# ---- compute layout height ----
risks = R["risk_rows"][:8]
acts  = R["action_rows"][:5]
ov    = R["overview_rows"]
wrapped_acts = [(a["sev"], a["sev_bg"], textwrap.wrap(a["text"], 118)) for a in acts]
act_h = sum(22 + 16*len(w) for _,_,w in wrapped_acts) + 8
H = 64 + 22 + 118 + 30 + (len(ov)+2)*26 + 46 + 28 + (len(risks)+1)*26 + 30 + act_h + 40
H = int(H)

fig = plt.figure(figsize=(W/100, H/100), dpi=100)
ax = fig.add_axes([0,0,1,1]); ax.set_xlim(0,W); ax.set_ylim(0,H); ax.invert_yaxis(); ax.axis("off")
fig.patch.set_facecolor(CREAM)
ax.add_patch(Rectangle((0,0),W,H,facecolor=CREAM,edgecolor="none"))

def rect(x,y,w,h,fc,ec="none",lw=0): ax.add_patch(Rectangle((x,y),w,h,facecolor=fc,edgecolor=ec,lw=lw))
def text(x,y,s,size=11,color=INK,weight="normal",ha="left",va="center"):
    ax.text(x,y,s,fontsize=size,color=color,fontweight=weight,ha=ha,va=va)

y = 0
# ---- header band ----
rect(0,0,W,64,PURPLE)
text(LM,24,"CHAW · Weekly Finance Control",20,WHITE,"bold")
text(LM,46,f"{S['date_str']} · SFB · Vending · ActionCity · all amounts THB · source: {S['source']}",10.5,WHITE)
y = 64+18

# ---- KPI meter ----
text(LM,y,"Issues by section",13,PURPLE,"bold"); y += 14
cards = R["kpi_cards"]; n=len(cards); gap=12
cw = (CW - (n-1)*gap)/n; ch=102
for i,c in enumerate(cards):
    x = LM + i*(cw+gap)
    rect(x,y,cw,ch,c["bg"])
    rect(x,y,cw,5,c["color"])
    text(x+cw/2,y+32,c["value"],28,c["color"],"bold",ha="center")
    text(x+cw/2,y+56,c["label"],11.5,INK,"bold",ha="center")
    text(x+cw/2,y+71,c["detail"],8.5,GREY,ha="center")
    text(x+cw/2,y+88,c.get("wow",""),8,c.get("wcolor",GREY),"bold",ha="center")
y += ch+26

# ---- Cash & Receivables ----
text(LM,y,"1 · Executive Summary — Cash & Receivables",14,PURPLE,"bold"); y += 16
cols = [("Subsidiary",LM,"l"),("Cash",470,"r"),("Total AR",590,"r"),("Current",695,"r"),
        ("Overdue",800,"r"),("% O/D",862,"r"),("Sub-Acct",975,"r"),("Recon",LM+CW,"r")]
rh=26
rect(LM,y,CW,rh,PURPLE)
for name,x,al in cols: text(x+(0 if al=="l" else 0),y+rh/2,name,10.5,WHITE,"bold",ha=("left" if al=="l" else "right"))
y+=rh
def row_cells(vals,bold=False,bg=None):
    global y
    if bg: rect(LM,y,CW,rh,bg)
    rect(LM,y+rh-1,CW,1,BORDER)
    for (name,x,al),v,col in vals:
        text(x,y+rh/2,v,10.5,col,("bold" if bold else "normal"),ha=("left" if al=="l" else "right"))
    y+=rh
for r in ov:
    row_cells([(cols[0],r["sub_name"],INK),(cols[1],r["cash"],INK),(cols[2],r["ar_total"],INK),
               (cols[3],r["ar_current"],INK),(cols[4],r["ar_overdue"],CORAL),(cols[5],r["pct"]+"%",INK),
               (cols[6],r["subacct"],INK),(cols[7],r["recon_txt"],INK)])
rect(LM,y,CW,rh,PURPLE)
tot=[(cols[0],"TOTAL",WHITE),(cols[1],S["cash_total"],WHITE),(cols[2],S["ar_total_all"],WHITE),
     (cols[3],S["ar_current_all"],WHITE),(cols[4],S["ar_overdue_all"],WHITE),(cols[5],"",WHITE),
     (cols[6],S["subacct_total"],WHITE),(cols[7],"",WHITE)]
for (name,x,al),v,col in tot: text(x,y+rh/2,v,10.5,col,"bold",ha=("left" if al=="l" else "right"))
y+=rh+12

# ---- recon alert ----
if SEC.get("recon_alert"):
    rect(LM,y,CW,32,CORALBG,ec=CORAL,lw=1)
    text(LM+10,y+16,"! Bank recon: "+S["recon_note"],11,INK,"bold")
    y+=44

# ---- Top risks ----
text(LM,y,"Top Risk Items",14,PURPLE,"bold"); y+=16
rc=[("#",LM,"l"),("Area",LM+30,"l"),("Item",LM+170,"l"),("Amount",LM+CW-150,"r"),("Severity",LM+CW,"r")]
rect(LM,y,CW,rh,PURPLE)
for name,x,al in rc: text(x,y+rh/2,name,10.5,WHITE,"bold",ha=("left" if al=="l" else "right"))
y+=rh
SBG={"CRITICAL":CORAL,"HIGH":"#E6A23C","PAST TERMS":"#E6A23C","WATCH":"#E6A23C"}
for r in risks:
    rect(LM,y+rh-1,CW,1,BORDER)
    text(LM,y+rh/2,r["n"],10.5,INK)
    text(LM+30,y+rh/2,r["area"],10,INK)
    item=r["item"]
    if len(item)>40: item=item[:39]+"…"
    text(LM+170,y+rh/2,item,10,INK)
    text(LM+CW-150,y+rh/2,r["amount"],10.5,CORAL,"bold",ha="right")
    sv=r["severity"]; text(LM+CW,y+rh/2,sv,10,SBG.get(sv,GREY),"bold",ha="right")
    y+=rh
y+=14

# ---- Priority actions ----
text(LM,y,"Priority Actions",14,PURPLE,"bold"); y+=18
ABG={"URGENT":CORAL,"CRITICAL":CORAL,"ACTION":PURPLE}
for sev,sevbg,lines in wrapped_acts:
    rect(LM,y-2,86,16,ABG.get(sev,PURPLE))
    text(LM+43,y+6,sev,9.5,WHITE,"bold",ha="center")
    for j,ln in enumerate(lines):
        text(LM+96,y+6+j*16,ln,10.5,INK)
    y += 22 + 16*(len(lines)-1) + 4

# ---- footer ----
text(LM,H-16,"CHAW Management · Finance Control · automated weekly routine · "+S["date_str"]+" · all amounts THB.",9,GREY)

fig.savefig(OUT, dpi=100, facecolor=CREAM)
print("wrote", OUT, "size", os.path.getsize(OUT), "H", H)
