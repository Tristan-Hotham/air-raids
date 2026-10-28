"""Step 6. Static figures for the paper (release/paper/f_*.png) and the blog (release/blog/b_*.png, 1520 px wide),
drawn with matplotlib from data/ (no web tiles). Fonts: FONT_DIR as in step 5; falls back to matplotlib defaults.
Run: FONT_DIR=/path/to/fonts python3 code/06_figures.py
"""
import csv, datetime as dt, json, math, os
import numpy as np, matplotlib, matplotlib.dates
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
A = [a for a in csv.DictReader(open(os.path.join(ROOT, "data", "ww2_areas.csv"), encoding="utf-8")) if a["scope"] == "uk" and a["lat"]]
W1 = list(csv.DictReader(open(os.path.join(ROOT, "data", "ww1_incidents.csv"), encoding="utf-8")))
DAILY = [(dt.date.fromisoformat(r["date"]), int(r["uk_deaths"]), int(r["greater_london"])) for r in csv.DictReader(open(os.path.join(ROOT, "data", "ww2_daily.csv")))]
COAST = json.load(open(os.path.join(ROOT, "data", "coast_ne10m.json")))
FD = os.environ.get("FONT_DIR", "")
SER, MONO = "serif", "monospace"
if FD:
    for f in ["FrauncesVar.ttf", "IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf", "SourceSerif4-Regular.ttf"]:
        fm.fontManager.addfont(os.path.join(FD, f))
    SER, MONO = "Source Serif 4", "IBM Plex Mono"
BG, FG, MUT, RULE, LAND = "#EEECE7", "#1D1C1A", "#66625B", "#D3CFC5", "#DDD8CD"
HOT, EMBER, GLOW, SLATE = "#C8481C", "#8E2A12", "#F2B33D", "#3E5878"
FC = ["#F6D79A", "#F0A65A", "#DD6F2E", "#B9431B", "#7E2410"]
K = math.cos(math.radians(54.5))
OUTP = os.path.join(ROOT, "release", "paper"); OUTB = os.path.join(ROOT, "release", "blog")
os.makedirs(OUTP, exist_ok=True); os.makedirs(OUTB, exist_ok=True)
plt.rcParams.update({"font.family": MONO, "text.color": FG, "axes.labelcolor": FG})


def style(ax, blog):
    ax.set_facecolor(BG if blog else "white")
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    for s in ("left", "bottom"): ax.spines[s].set_color(MUT)
    ax.tick_params(colors=FG, labelsize=13 if blog else 8.5)


def fig(h, blog, w=None):
    return plt.figure(figsize=(w or (7.6 if blog else 6.5), h), dpi=200, facecolor=BG if blog else "white")


def save(f, name, blog):
    if blog:
        out = os.path.join(OUTB, "b_" + name + ".png")
        f.savefig(out, facecolor=f.get_facecolor(), bbox_inches="tight", pad_inches=0.2)
        from PIL import Image
        im = Image.open(out); im.resize((1520, round(im.height * 1520 / im.width)), Image.LANCZOS).save(out, optimize=True)
    else: f.savefig(os.path.join(OUTP, "f_" + name + ".png"), facecolor=f.get_facecolor(), bbox_inches="tight", pad_inches=0.08)
    plt.close(f)


def fmap(blog):
    f = fig(9.4 if blog else 7.4, blog, 7.6 if blog else 6.0); ax = f.add_axes([0, 0, 1, 1]); ax.set_facecolor(BG if blog else "white")
    for g in COAST:
        for poly in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
            a = np.array(poly[0]); ax.add_patch(Polygon(np.c_[a[:, 0] * K, a[:, 1]], closed=True, fc=LAND, ec="#C3BDB1", lw=.4))
    for a in sorted(A, key=lambda a: -int(a["deaths"])):
        n = int(a["deaths"]); x, y = float(a["lon"]) * K, float(a["lat"])
        s = (0.8 + math.sqrt(n) * 0.45) ** 2 * (1.6 if blog else 1.0)
        ax.scatter([x], [y], s=s * 4, c=GLOW, alpha=.12, lw=0, zorder=2)
        ax.scatter([x], [y], s=s, c=FC[sum(n >= t for t in (10, 50, 250, 1000))], alpha=.9, ec=BG if blog else "white", lw=.3, zorder=3)
    for r in W1:
        if not r["lat"]: continue
        ax.scatter([float(r["lon"]) * K], [float(r["lat"])], s=(2 + math.sqrt(int(r["killed"])) * 1.3) ** 2 * (1.4 if blog else .9), facecolors="none", edgecolors=SLATE, lw=1.4, zorder=4)
    ax.set_xlim(-8.3 * K, 2.0 * K); ax.set_ylim(49.85, 59.0); ax.set_aspect("equal"); ax.axis("off")
    fs = 12 if blog else 8
    ax.text(-8.1 * K, 58.75, "Civilian dead, 1939 to 1947", fontsize=fs + 1, color=FG, fontweight="medium")
    for i, (c, l) in enumerate(zip(FC, ["1 to 9", "10 to 49", "50 to 249", "250 to 999", "1,000 or more"])):
        ax.scatter([-7.95 * K], [58.45 - i * .27], s=60 if blog else 30, c=c); ax.text(-7.7 * K, 58.45 - i * .27, l, va="center", fontsize=fs, color=FG)
    ax.scatter([-7.95 * K], [57.0], s=80 if blog else 40, facecolors="none", edgecolors=SLATE, lw=1.4)
    ax.text(-7.7 * K, 57.0, "First World War raid or\nbombardment (ring size = killed)", va="center", fontsize=fs, color=FG)
    for nm, dx, dy in [("Liverpool", -1.6, .25), ("Clydebank", -1.2, .3), ("Belfast", -.4, .35), ("Plymouth", -1.0, -.35), ("Coventry", .55, .2), ("Kingston upon Hull", .5, .25)]:
        a = next(a for a in A if a["name"] == nm)
        ax.annotate(nm.replace("Kingston upon ", ""), (float(a["lon"]) * K, float(a["lat"])), (float(a["lon"]) * K + dx * K, float(a["lat"]) + dy), fontsize=fs, color=FG,
                    arrowprops=dict(arrowstyle="-", color=MUT, lw=.6))
    h = next(r for r in W1 if r["id"] == "1914hart")
    ax.annotate("Hartlepool 1914", (float(h["lon"]) * K, float(h["lat"])), (float(h["lon"]) * K + .9 * K, float(h["lat"]) + .45), fontsize=fs, color=SLATE, arrowprops=dict(arrowstyle="-", color=SLATE, lw=.6))
    ax.annotate("London", (-0.12 * K, 51.5), (-1.9 * K, 51.95), fontsize=fs + 1, color=FG, fontweight="medium", arrowprops=dict(arrowstyle="-", color=MUT, lw=.6))
    save(f, "map", blog)


def fweekly(blog):
    f = fig(4.2 if blog else 3.0, blog); ax = f.add_axes([.08, .12, .9, .78] if blog else [.1, .14, .88, .76]); style(ax, blog)
    d0 = DAILY[0][0]; wk = {}
    for d, n, l in DAILY:
        k = (d - d0).days // 7; w = wk.setdefault(k, [0, 0]); w[0] += n; w[1] += l
    ks = [k for k in sorted(wk) if d0 + dt.timedelta(days=7 * k) <= dt.date(1945, 12, 31)]
    xs = [d0 + dt.timedelta(days=7 * k) for k in ks]
    lon = np.array([wk[k][1] for k in ks]); out = np.array([wk[k][0] - wk[k][1] for k in ks])
    for p in R["periods"]:
        if p["key"] in ("blitz", "baby", "vweap", "mid"):
            ax.axvspan(dt.date.fromisoformat(p["start"]), dt.date.fromisoformat(p["end"]), color=GLOW, alpha=.07 if p["key"] == "mid" else .2, lw=0)
    ax.bar(xs, lon, width=6, color=FG, label="Greater London"); ax.bar(xs, out, bottom=lon, width=6, color=HOT, label="Elsewhere in the UK")
    fs = 13 if blog else 8
    top = (lon + out).max()
    for key, lab in [("blitz", "The Blitz"), ("mid", "Baedeker, tip and run"), ("vweap", "V-1 and V-2")]:
        p = next(p for p in R["periods"] if p["key"] == key); s, e = dt.date.fromisoformat(p["start"]), dt.date.fromisoformat(p["end"])
        ax.text(s + (e - s) / 2, top * 1.04, lab, ha="center", fontsize=fs, color=FG)
    ax.set_ylim(0, top * 1.12); ax.set_xlim(dt.date(1939, 9, 1), dt.date(1945, 12, 31))
    ax.set_ylabel("Civilian dead per week", fontsize=fs); ax.legend(frameon=False, fontsize=fs, loc="upper right", bbox_to_anchor=(1, .9))
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    save(f, "weekly", blog)


def fww1(blog):
    f = fig(4.0 if blog else 2.9, blog); ax = f.add_axes([.08, .12, .9, .8] if blog else [.1, .15, .88, .78]); style(ax, blog)
    col = {"airship": SLATE, "aeroplane": HOT, "naval": FG}
    fs = 13 if blog else 8
    for r in sorted(W1, key=lambda r: int(r["killed"])):
        d = dt.date.fromisoformat(r["date"]); k = int(r["killed"])
        ax.vlines(d, 0, k, color=col[r["attack"]], lw=2 if blog else 1.4)
        ax.scatter([d], [k], s=(math.sqrt(k) * (2.2 if blog else 1.6)) ** 2 / 2 + 12, color=col[r["attack"]], zorder=3, ec="white", lw=.5)
    for i, lab, dx, dy, ha in [("1914hart", "Hartlepool, Dec 1914", 25, 5, "left"), ("1917folk", "Folkestone", -25, -4, "right"), ("1917jun", "London and Poplar, June 1917", -25, 5, "right"),
                           ("1917chat", "Chatham\ndrill hall", 25, 0, "left"), ("1916blac", "Black\nCountry", 25, -4, "left"), ("1915thea", "Theatreland\nraid", 25, 4, "left")]:
        r = next(r for r in W1 if r["id"] == i)
        ax.text(dt.date.fromisoformat(r["date"]) + dt.timedelta(days=dx), int(r["killed"]) + dy, lab, ha=ha, fontsize=fs - 1, color=FG)
    ax.xaxis.set_major_locator(matplotlib.dates.YearLocator()); ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%Y"))
    for k, l in [("airship", "Airship"), ("aeroplane", "Aeroplane"), ("naval", "Warships")]: ax.scatter([], [], color=col[k], label=l)
    ax.legend(frameon=False, fontsize=fs, loc="upper left"); ax.set_ylim(0, 185); ax.set_ylabel("Killed", fontsize=fs)
    ax.set_xlim(dt.date(1914, 11, 1), dt.date(1918, 7, 1))
    save(f, "ww1", blog)


def hb(ax, names, vals, cols, blog, fmtf=lambda v: f"{v:,}", v2=None):
    y = np.arange(len(names))[::-1]
    ax.barh(y, vals, color=cols, height=.7)
    if v2 is not None: ax.barh(y, v2, color=EMBER, height=.7)
    for yy, v in zip(y, vals): ax.text(v + max(vals) * .01, yy, fmtf(v), va="center", fontsize=12 if blog else 7.5, color=FG)
    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=13 if blog else 8)
    ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0); ax.set_xlim(0, max(vals) * 1.12)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}" if max(vals) > 50 else f"{v:g}"))


def ftop(blog):
    rows = R["top_outside"][:15]
    f = fig(6.2 if blog else 4.3, blog); ax = f.add_axes([.27, .08, .7, .9] if blog else [.27, .1, .7, .88]); style(ax, blog)
    hb(ax, [r["name"].replace("Kingston upon ", "") for r in rows], [r["deaths"] for r in rows], ["#F0A65A"] * len(rows), blog, v2=[r["blitz"] for r in rows])
    ax.set_xlabel("Civilian dead, 1939 to 1947 (dark: in the Blitz, Sept 1940 to May 1941)", fontsize=12 if blog else 7.5)
    save(f, "top", blog)


def frates(blog):
    rows = R["rates"][:16]
    f = fig(5.6 if blog else 4.0, blog); ax = f.add_axes([.27, .09, .7, .89] if blog else [.27, .11, .7, .87]); style(ax, blog)
    hb(ax, [r["name"].replace("Kingston upon ", "") for r in rows], [r["per1000"] for r in rows], [FG if r["name"] == "County of London" else "#DD6F2E" for r in rows], blog, fmtf=lambda v: f"{v:.1f}")
    ax.set_xlabel("Civilian dead per 1,000 people (approximate populations)", fontsize=12 if blog else 7.5)
    save(f, "rates", blog)


def fperiods(blog):
    P = [p for p in R["periods"] if p["key"] != "after"]
    f = fig(3.8 if blog else 2.6, blog); ax = f.add_axes([.33, .14, .64, .84] if blog else [.33, .17, .64, .8]); style(ax, blog)
    y = np.arange(len(P))[::-1]
    ax.barh(y, [p["london_share"] for p in P], color=FG, height=.62, label="Greater London")
    ax.barh(y, [1 - p["london_share"] for p in P], left=[p["london_share"] for p in P], color=HOT, height=.62, label="Elsewhere in the UK")
    for yy, p in zip(y, P): ax.text(.015, yy, f"{round(p['london_share'] * 100)}%", va="center", color="white", fontsize=12 if blog else 7.5)
    ax.set_yticks(y); ax.set_yticklabels([f"{p['label']}\n{p['uk']:,} dead" for p in P], fontsize=12 if blog else 7.5)
    ax.set_xlim(0, 1); ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1)); ax.tick_params(axis="y", length=0); ax.spines["left"].set_visible(False)
    ax.legend(frameon=False, fontsize=12 if blog else 7.5, loc="upper center", bbox_to_anchor=(.5, -.1), ncol=2)
    save(f, "periods", blog)


def fages(blog):
    B = R["age"]["bands"]
    f = fig(3.8 if blog else 2.6, blog); ax = f.add_axes([.2, .14, .76, .84] if blog else [.2, .17, .76, .8]); style(ax, blog)
    hb(ax, [b["band"] for b in B], [b["n"] for b in B], ["#ABA59A" if b["band"].startswith("0") else "#B9431B" if b["band"] in ("1 to 4", "5 to 15") else "#F0A65A" for b in B], blog)
    ax.set_xlabel("Civilian dead in the UK by age at death", fontsize=12 if blog else 7.5)
    save(f, "ages", blog)


if __name__ == "__main__":
    for blog in (False, True):
        fmap(blog); fweekly(blog); fww1(blog); ftop(blog); frates(blog); fperiods(blog)
        if not blog: fages(blog)
    print("figures written")
