import random, time, tkinter as tk
from tkinter import messagebox, simpledialog

ASSETS = [("AAPL",220),("TSLA",330),("NVDA",175),("MSFT",510),("AMZN",230),("GOOGL",185),("META",560),("NFLX",700),("AMD",160),("BTC",78780),("ETH",3800)]
TIMEFRAMES = ["1s","30s","1m","5m","15m","1H","1D","1W","1M"]
SPAN = {"1s":1,"30s":30,"1m":60,"5m":300,"15m":900,"1H":3600,"1D":86400,"1W":604800,"1M":2592000}
REGIMES = ["CALM","TREND","CHOP","MANIA","PANIC","CRISIS"]
REGIME_VOL = {"CALM":.002,"TREND":.003,"CHOP":.0045,"MANIA":.006,"PANIC":.009,"CRISIS":.012}
NEWS_POOL = ["做市商撤单","巨鲸异动","算法追涨","强平扫描","流动性变薄","恐慌蔓延","逼空开始","空头回补","大户对冲"]
PAY_METHODS = {
    "电子钱包": (.015, 0.0, 10_000, 0, .00, .00, "即时到账 · 费1.5%"),
    "信用卡":   (.029, 0.3, 50_000, 0, .00, .03, "即时 · 费2.9%+$0.3 · 3%拒付"),
    "银行转账": (.008, 15., 1_000_000, 4, .00, .00, "4s审核 · 费0.8%+$15"),
    "加密货币": (.001, 8.0, 500_000, 3, .02, .01, "3s链上确认 · gas随机 · +2% bonus"),
}
DW, DH = 1300, 760

def money(v): return f"${v/1e6:,.2f}M" if abs(v) >= 1e6 else f"${v:,.2f}"
def die(title, msg): tk.Tk().withdraw(); messagebox.showerror(title, msg+"\nThe simulator refuses to start."); raise SystemExit(1)
def flash_error(app, title, msg): messagebox.showerror(title, msg); app.r.bell()
def note(app, s, col="#24d38d"):
    app.msg.config(text=s, fg=col)
    app.r.after(1400, lambda: app.msg.config(text="● RANDOM CHAOS ENGINE ONLINE", fg="#7f8ca8"))
def T(app,x,y,s,z=12,col="#aeb7ca",a="w",bold=False,tg="d"): app.c.create_text(x*app.SX,y*app.SY,text=s,fill=col,anchor=a,font=("Segoe UI",max(7,int(z*app.FS)),"bold" if bold else "normal"),tags=tg)
def R(app,x1,y1,x2,y2,fill="",outline="",tg="d",wd=1): app.c.create_rectangle(x1*app.SX,y1*app.SY,x2*app.SX,y2*app.SY,fill=fill,outline=outline,width=wd,tags=tg)
def L(app,x1,y1,x2,y2,fill="#22253a",tg="d",wd=1): app.c.create_line(x1*app.SX,y1*app.SY,x2*app.SX,y2*app.SY,fill=fill,width=wd,tags=tg)

def build(app):
    app.r.title("NEXUS RANDOM ULTRA"); app.r.geometry("1300x760"); app.r.configure(bg="#04050c")
    app.c = tk.Canvas(app.r, bg="#04050c", highlightthickness=0); app.c.pack(fill="both", expand=True)
    app.SX = app.SY = app.FS = 1.; app._widgets = []
    _build_widgets(app)
    app.c.bind("<Button-1>", lambda e: on_click(app, e))
    app.c.bind("<Configure>", lambda e: relayout(app))
    app.r.bind("<F11>", lambda e: fullscreen(app))

def add_button(app, text, x, y, w, cmd, bg="#30364a"):
    b = tk.Button(app.c, text=text, command=cmd, bg=bg, fg="#eef2fa", bd=0, cursor="hand2", font=("Segoe UI", max(7,int(9*app.FS)), "bold"), activebackground=bg)
    app._widgets.append((app.c.create_window(x*app.SX, y*app.SY, window=b, anchor="nw", width=w*app.SX, height=30*app.SY), x, y, w, 30))

def _build_widgets(app):
    app.msg = tk.Label(app.c, text="● RANDOM CHAOS ENGINE ONLINE", bg="#0b0e19", fg="#7f8ca8", font=("Segoe UI",10,"bold"))
    app._widgets.append((app.c.create_window(275, 700, window=app.msg, anchor="nw"), 275, 700, 0, 0))
    for i,(s,v) in enumerate(ASSETS): add_button(app, f"{s}/USD ${v:,.2f}", 25, 115+i*49, 205, lambda i=i: app.choose(i), "#20243a")
    for i,x in enumerate(TIMEFRAMES): add_button(app, x, 270+i*58, 117, 52, lambda x=x: app.period(x), "#273454")
    add_button(app, "DEPOSIT", 1000, 16, 88, lambda: deposit(app), "#24d38d")
    add_button(app, "WITHDRAW", 1092, 16, 88, lambda: withdraw(app))
    add_button(app, "⛶ FULLSCREEN", 1184, 16, 100, lambda: fullscreen(app), "#39406b")
    add_button(app, "BUY/LONG", 1120, 340, 145, lambda: app.trade(1), "#24d38d")
    add_button(app, "SELL/SHORT", 1120, 385, 145, lambda: app.trade(-1), "#f0446e")
    add_button(app, "⚡ RANDOM EVENT", 1120, 430, 145, lambda: (setattr(app, 'cool', 0), app.shock(), render(app)), "#5d3a95")
    add_button(app, "CLOSE ALL", 1120, 475, 145, lambda: ([app.close(j) for j in list(app.POS)], render(app)), "#8290a8")

def relayout(app):
    w, h = app.r.winfo_width(), app.r.winfo_height()
    w = DW if w < 100 else w; h = DH if h < 100 else h
    app.SX, app.SY = w/DW, h/DH; app.FS = max(.7, min(2.2, min(app.SX, app.SY)))
    app.c.configure(width=w, height=h); app.c.delete("s"); sdraw(app)
    for iid,x,y,bw,bh in app._widgets:
        app.c.coords(iid, x*app.SX, y*app.SY)
        if bw: app.c.itemconfigure(iid, width=bw*app.SX, height=bh*app.SY)
    render(app)

def fullscreen(app):
    app.r.attributes("-fullscreen", not app.r.attributes("-fullscreen")); note(app, "⛶ FULLSCREEN TOGGLED", "#8ea0ff")

def sdraw(app):
    for i in range(24): R(app, 0, i*32, 1300, i*33+2, fill="#%02x%02x%02x"%(4+i//4,5+i//4,10+i//3), tg="s")
    for x1,y1,x2,y2 in [(15,70,245,740),(255,70,850,170),(255,180,850,545),(860,70,1090,545),(1100,70,1285,740),(255,555,1090,740)]:
        R(app, x1,y1,x2,y2, fill="#0b0e19", outline="#262b40", tg="s"); L(app, x1+1,y1,x2-1,y1, fill="#3a4160", tg="s")
    R(app, 22,52,120,55, fill="#24d38d", tg="s"); T(app, 22,31,"◩ NEXUS",24,"#f3f5fb",bold=True,tg="s")
    T(app, 180,31,"RANDOM ULTRA PAPER TRADING",11,"#8e98b0",bold=True,tg="s"); T(app, 30,93,"STOCK & CRYPTO PERPS",10,"#73809b",bold=True,tg="s")
    T(app, 878,94,"ORDER BOOK",12,"#edf1fa",bold=True,tg="s"); T(app, 878,120,"TOTAL     SIZE       PRICE",9,"#74819c",tg="s")
    T(app, 1120,95,"PAPER FUTURES",10,"#8290a8",bold=True,tg="s"); T(app, 1120,170,"ORDER SIZE · CLICK",9,"#77839d",tg="s")
    T(app, 1120,285,"MARGIN HEALTH",9,"#8290a8",tg="s")
    R(app, 1110,178,1275,213, outline="#3d5fa8", tg="s"); R(app, 1110,222,1275,266, outline="#3d5fa8", tg="s")
    R(app, 1110,300,1275,315, fill="#121423", outline="#2b3046", tg="s"); R(app, 640,148,800,158, fill="#121423", outline="#2b3046", tg="s")
    T(app, 1192,650,"SIMULATION ONLY",10,"#f5bc4b","center",True,"s"); T(app, 1192,672,"Fees · Funding · Multi-position",9,"#7c889f","center",False,"s")
    T(app, 275,580,"POSITIONS · click a row to close",12,"#edf1fa",bold=True,tg="s")
    for x,hh in [(275,"SIDE"),(375,"SIZE"),(490,"ENTRY"),(650,"MARK"),(810,"PNL")]: T(app, x,615,hh,9,"#71809c",tg="s")

def render(app):
    app.c.delete("d")
    T(app, 985,31,time.strftime("%H:%M:%S"),13,"#dce2f0","e",True); T(app, 275,95,f"◉ {ASSETS[app.sel][0]}/USD",17,"#edf1fa",bold=True)
    pc = "#ffffff" if abs(app.price/max(app.prev,1)-1) > .008 else "#2ee6a0" if app.price >= app.prev else "#ff5c7a"
    T(app, 477,97,f"${app.price:,.2f}",22,"#000000"); T(app, 475,95,f"${app.price:,.2f}",22,pc,bold=True)
    T(app, 620,95,f"{app.reg} · FEAR {app.fear}",11,"#ff5c7a" if app.fear > 70 else "#f5bc4b" if app.fear > 45 else "#2ee6a0",bold=True)
    T(app, 845,95,f"FUND {app.fund:+.3%}",10,"#8ea0ff","e")
    T(app, 275,164,f"{app.tf} · closes {max(0,int(SPAN[app.tf]-(time.time()-app.started)))}s · vol {app.vol*100:.2f}% · {app.news[:14]}",10,"#7d89a3")
    R(app, 640,148,640+160*app.fear/100,158, fill="#ff5c7a" if app.fear > 70 else "#f5bc4b" if app.fear > 45 else "#2ee6a0")
    for j in range(1,5): L(app, 640+j*32,148,640+j*32,158, fill="#04050c")
    vals = [v for b in app.bars for v in b]; lo, hi = min(vals)*.992, max(vals)*1.008
    step = 540/max(1,len(app.bars)); Y = lambda v: 520-(v-lo)/((hi-lo) or 1)*315
    for i in range(5): L(app, 275,205+i*73,825,205+i*73, fill="#1d2133"); T(app, 830,205+i*73,f"{hi-(hi-lo)*i/4:,.2f}",9,"#7a86a0","e")
    for i,b in enumerate(app.bars):
        x = 280+i*step; o,h,l,z = b; co = "#2ee6a0" if z >= o else "#ff5c7a"
        L(app, x,Y(h),x,Y(l), fill=co, wd=2); R(app, x-4,Y(max(o,z)),x+4,max(Y(min(o,z)),Y(max(o,z))+2), fill=co, outline="#0b0e19")
    L(app, 878,286,1078,286, fill="#3a4160")
    for i in range(12):
        y = 150+i*28; q = app.price+(6-i)*max(app.price*.00013,.01)+app.spread
        co = "#ff5c7a" if i < 6 else "#2ee6a0"; w = int(random.randint(12,95)*(1.7 if i < 6 and app.fear > 70 else .6 if i >= 6 and app.fear > 70 else 1))
        R(app, 950,y-9,min(1035,950+w),y+9, fill="#301827" if i < 6 else "#102d27")
        T(app, 878,y,f"{random.randint(6,95)}.{random.randint(10,99)}K",10,"#71809c"); T(app, 970,y,f"{random.random()*2:.5f}",10,"#c9cfdd"); T(app, 1078,y,f"{q:,.2f}",10,co,"e")
    eq = app.equity(); fr = app.frozen(); mr = (eq/max(fr,1)*100) if app.POS else 100
    T(app, 1120,120,money(app.cash),15,"#edf1fa",bold=True); T(app, 1120,140,f"EQUITY {money(eq)}",11,"#8ea0ff",bold=True)
    T(app, 1120,157,f"AVAIL {money(max(0,eq-fr))} · FROZEN {money(fr)}",8,"#7c889f")
    T(app, 1120,195,f"{app.lot} shares",16,"#edf1fa"); T(app, 1192,244,f"LEVERAGE · CLICK {app.lev}×",11,"#edf1fa","center")
    R(app, 1110,300,1110+165*max(0,min(100,mr))/100,315, fill="#2ee6a0" if mr > 80 else "#f5bc4b" if mr > 55 else "#ff5c7a")
    T(app, 1192,330,f"MRG {min(mr,999):.0f}% · FEE {app.FEE:.2%} · BRW {app.BORROW*100:.4f}%",8,"#7c889f","center")
    app.ROWS = list(app.POS)
    if app.ROWS:
        for idx,i in enumerate(app.ROWS[:6]):
            v = app.POS[i]; y = 645+idx*26; pn = app.upnl(i)
            T(app, 275,y,("LONG " if v[0] > 0 else "SHORT ")+ASSETS[i][0],11,"#2ee6a0" if v[0] > 0 else "#ff5c7a",bold=True)
            T(app, 375,y,f"{v[2]} sh"); T(app, 490,y,f"${v[1]:,.2f}"); T(app, 650,y,f"${app.P[i]:,.2f}")
            T(app, 810,y,f"{money(pn)}",11,"#2ee6a0" if pn >= 0 else "#ff5c7a",bold=True); T(app, 1000,y,"[click to close]",8,"#7c889f")
    else:
        for x in (275,375,490,650,810): T(app, x,660,"—")
    T(app, 275,735,f"RANDOM NEWS · {app.news[:14]} · FEAR {app.fear} · FEES {money(app.fees)}",10,"#8ea0ff")
    if app.MODE in ("dep","wd"): _draw_pay(app)
    if app.MODE == "bonus": _draw_bonus(app)

def _draw_pay(app):
    R(app, 300,170,1000,610, fill="#0d1020", outline="#8ea0ff", wd=2)
    T(app, 650,205,"DEPOSIT" if app.MODE == "dep" else "WITHDRAW",22,"#edf1fa","center",True)
    T(app, 650,235,"选择支付方式 · 真实限额/手续费/到账延迟 · 点击 CONFIRM 输入金额",10,"#8e98b0","center")
    for i,name in enumerate(PAY_METHODS):
        fr,ff,cap,dl,bo,risk,ds = PAY_METHODS[name]
        R(app, 330+i*165,270,480+i*165,390, fill="#1d2b4a" if app.PSEL == i else "#12152a", outline="#8ea0ff" if app.PSEL == i else "#262b40", wd=2)
        T(app, 405+i*165,295,name,13,"#edf1fa","center",True); T(app, 405+i*165,320,ds,9,"#8e98b0","center")
        T(app, 405+i*165,340,f"限额 ${cap:,}",9,"#7c889f","center"); T(app, 405+i*165,360,f"到账 {dl}s" if dl else "即时",9,"#2ee6a0","center")
    T(app, 650,415,f"当前可用 {money(max(0,app.equity()-app.frozen()))} · 首充+10% · ≥5万+5% · 加密+2% · 20%幸运+1~8%",10,"#f5bc4b","center")
    for j,p in enumerate(app.PEND[:4]): T(app, 330,445+j*18,f"⏳ {p[2]} {money(abs(p[1] if p[1] else p[3]))} {'入账' if p[1] else '提现'} · {max(0,p[0]-time.time()):.0f}s",9,"#8ea0ff")
    R(app, 330,520,530,565, fill="#24d38d"); T(app, 430,542,"CONFIRM",13,"#04120c","center",True)
    R(app, 560,520,760,565, fill="#3a3f55"); T(app, 660,542,"CANCEL",13,"#eef2fa","center",True)
    T(app, 650,590,"模拟支付 · 不会发生真实资金移动",9,"#7c889f","center")

def _draw_bonus(app):
    R(app, 350,220,950,480, fill="#101426", outline="#f5bc4b", wd=3)
    T(app, 650,280,"🎁 DEPOSIT BONUS",26,"#f5bc4b","center",True)
    T(app, 650,350,f"+{money(app.BON)}",40,"#2ee6a0","center",True)
    T(app, 650,420,"BONUS 已计入你的模拟账户",12,"#8e98b0","center")
    for p in app.PT: p[0] += p[2]; p[1] += p[3]; p[5] -= 1
    app.PT = [p for p in app.PT if p[5] > 0]
    for p in app.PT: R(app, p[0],p[1],p[0]+5,p[1]+5, fill=p[4])

def confetti(app):
    app.PT = [[random.uniform(360,940), random.uniform(230,260), random.uniform(-4,4), random.uniform(2,6), random.choice(["#f5bc4b","#2ee6a0","#ff5c7a","#8ea0ff","#ffffff"]), 50] for _ in range(90)]

def deposit(app): app.MODE = "dep"; app.PSEL = 0; render(app)
def withdraw(app): app.MODE = "wd"; app.PSEL = 0; render(app)

def pay(app):
    name = list(PAY_METHODS)[app.PSEL]; fr,ff,cap,dl,bo,risk,ds = PAY_METHODS[name]
    av = max(0., app.equity()-app.frozen())
    if app.MODE == "wd" and av < 1:
        messagebox.showwarning("WITHDRAW", "No available funds (margin is frozen)."); return
    q = simpledialog.askfloat("DEPOSIT" if app.MODE == "dep" else "WITHDRAW",
          f"{name} amount (USD) · cap ${cap:,} · {ds}"+("" if app.MODE == "dep" else f" · available ${av:,.2f}"),
          minvalue=1, maxvalue=cap if app.MODE == "dep" else max(1., av)) or 0
    if not q: return
    fee = q*fr+ff+(random.uniform(1,15) if name == "加密货币" else 0)
    if app.MODE == "dep":
        if random.random() < risk:
            app.MODE = ""; note(app, f"✗ {name} 支付被拒/失败,资金未动", "#f0446e"); app.r.bell(); return
        b = q*(bo+(.1 if app.FIRST_DEP else 0)+(.05 if q >= 50000 else 0)+(random.uniform(.01,.08) if random.random() < .2 else 0))
        net = q-fee+b; app.FIRST_DEP = False; app.BON = b
        if dl > 0:
            app.PEND.append([time.time()+dl, net, name, net]); app.MODE = ""; note(app, f"⏳ {name} {money(net)} 处理中 · 约{dl}s到账")
        else:
            app.cash += net; app.MODE = "bonus"; confetti(app); app.r.after(2300, lambda: (setattr(app, 'MODE', ''), render(app)))
            note(app, f"✓ {name} +{money(net)} · 含 bonus {money(b)}"); app.r.bell()
    else:
        if q+fee > av: messagebox.showwarning("WITHDRAW", "Exceeds available equity (margin is frozen)."); return
        if random.random() < risk:
            app.MODE = ""; note(app, f"✗ {name} 提现被拒,资金未动", "#f0446e"); app.r.bell(); return
        if not app.KYC: messagebox.showinfo("KYC CHECK", "模拟 KYC 身份验证已通过 ✓"); app.KYC = True
        dl2 = dl+(2 if q > 100000 else 0); app.cash -= q+fee; app.MODE = ""
        app.PEND.append([time.time()+max(dl2,1), 0, name, q])
        note(app, f"⏳ 提现 {money(q)} 已提交 · {name}"+(" · 大额审核+2s" if q > 100000 else "")); app.r.bell()

def on_click(app, e):
    ux, uy = e.x/app.SX, e.y/app.SY
    if app.MODE in ("dep","wd"):
        for i in range(4):
            if 330+i*165 < ux < 480+i*165 and 270 < uy < 390: app.PSEL = i; render(app); return
        if 330 < ux < 530 and 520 < uy < 565: pay(app); render(app); return
        if 560 < ux < 760 and 520 < uy < 565: app.MODE = ""; render(app); return
        return
    if app.MODE == "bonus": return
    for idx,i in enumerate(app.ROWS):
        if idx < 6 and abs(uy-(645+idx*26)) < 13 and 260 < ux < 1040: app.close(i); render(app); return
    if 1120 < ux < 1280 and 160 < uy < 220:
        q = simpledialog.askinteger("Lot size","Sim shares 1-10000", initialvalue=app.lot, minvalue=1, maxvalue=10000)
        if q: app.lot = q; note(app, f"⚙ LOT {q}")
        return
    if 1120 < ux < 1280 and 220 <= uy < 275:
        q = simpledialog.askinteger("Leverage","1-100x", initialvalue=app.lev, minvalue=1, maxvalue=100)
        if q: app.lev = q; note(app, f"⚙ LEV {q}x")
