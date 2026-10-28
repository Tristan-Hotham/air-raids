"""r/dataisbeautiful collage: reddit/was_the_blitz_londons.png (2400 x 3000), light stone, searchlight cream and fire orange.
Every number comes from ../data/results.json and the CSVs in ../data/. Fonts: FONT_DIR (Fraunces, Source Serif 4, IBM Plex Mono).
Run from this folder: FONT_DIR=/path/to/fonts python3 collage.py
"""
import csv, datetime as dt, json, math, os
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
FD = os.environ.get("FONT_DIR", "/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/fonts")
for f in ["FrauncesVar.ttf", "IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf", "SourceSerif4-It.ttf"]:
    fm.fontManager.addfont(os.path.join(FD, f))
DISP = fm.FontProperties(fname=os.path.join(FD, "FrauncesVar.ttf"), weight=900)
SER, MONO = "Source Serif 4", "IBM Plex Mono"
BG, FG, MUT, LAND, EDGE = "#ECEAE4", "#1D1C1A", "#66625B", "#DCD7CC", "#C6BFB2"
HOT, EMBER, GLOW, CREAM, SLATE = "#C8481C", "#7E2410", "#F2B33D", "#FFF3D2", "#3E5878"
FC = ["#F6D79A", "#F0A65A", "#DD6F2E", "#B9431B", "#7E2410"]
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
A = [a for a in csv.DictReader(open(os.path.join(ROOT, "data", "ww2_areas.csv"), encoding="utf-8")) if a["scope"] == "uk" and a["lat"]]
W1 = [r for r in csv.DictReader(open(os.path.join(ROOT, "data", "ww1_incidents.csv"), encoding="utf-8")) if r["lat"]]
DAILY = [(dt.date.fromisoformat(r["date"]), int(r["uk_deaths"]), int(r["greater_london"])) for r in csv.DictReader(open(os.path.join(ROOT, "data", "ww2_daily.csv")))]
COAST = json.load(open(os.path.join(ROOT, "data", "coast_ne10m.json")))
K = math.cos(math.radians(54.5))
P = {p["key"]: p for p in R["periods"]}


def land(ax, lw=.5):
    for g in COAST:
        for poly in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
            a = np.array(poly[0])
            if a[:, 0].min() > 1.75: continue
            ax.add_patch(Polygon(np.c_[a[:, 0] * K, a[:, 1]], closed=True, fc=LAND, ec=EDGE, lw=lw))


def fire(ax, vals, scale, glow=True):
    pts = sorted([(v, float(a["lon"]) * K, float(a["lat"])) for v, a in zip(vals, A) if v > 0], reverse=True)
    v = np.array([p[0] for p in pts]); x = np.array([p[1] for p in pts]); y = np.array([p[2] for p in pts])
    s = (0.6 + np.sqrt(v) * scale) ** 2
    if glow:
        ax.scatter(x, y, s=s * 7, c=GLOW, alpha=.07, lw=0, zorder=2)
        ax.scatter(x, y, s=s * 2.6, c=GLOW, alpha=.13, lw=0, zorder=2)
    ax.scatter(x, y, s=s, c=[FC[sum(n >= t for t in (10, 50, 250, 1000))] for n in v], alpha=.92, lw=.3, ec=BG, zorder=3)


fig = plt.figure(figsize=(12, 15), dpi=200, facecolor=BG)
fig.text(0.045, 0.970, "Was the Blitz London's?", fontproperties=DISP, fontsize=50, color=FG, va="top")
fig.text(0.045, 0.922, f"{round(R['london']['outside_share'] * 100)}% of the dead were not.", fontproperties=DISP, fontsize=50, color=HOT, va="top")
fig.text(0.045, 0.864, f"Every civilian on the Commonwealth War Graves Commission's Second World War roll for the UK,\n"
         f"{R['cwgc']['uk']:,} people, counted by the town or district they are filed under. Blue rings: the raids and\n"
         f"bombardments of 1914 to 1918 that came first.", family=SER, fontsize=14.5, color=FG, va="top", linespacing=1.3)

# hero map
ax = fig.add_axes([0.02, 0.355, 0.56, 0.44]); ax.set_facecolor(BG)
land(ax)
fire(ax, [int(a["deaths"]) for a in A], 0.36)
for r in sorted(W1, key=lambda r: -int(r["killed"])):
    ax.scatter([float(r["lon"]) * K], [float(r["lat"])], s=(2 + math.sqrt(int(r["killed"])) * 1.25) ** 2, facecolors="none", edgecolors=SLATE, lw=1.5, zorder=4)
ax.set_xlim(-10.6 * K, 1.9 * K); ax.set_ylim(49.9, 59.0); ax.set_aspect(1); ax.axis("off")
ax.text(-10.5 * K, 58.85, "Civilian dead, 1939 to 1947", family=MONO, fontsize=10.5, color=MUT)
for i, l in enumerate(["1 to 9", "10 to 49", "50 to 249", "250 to 999", "1,000 or more"]):
    ax.scatter([-10.35 * K], [58.55 - i * .28], s=70, c=FC[i]); ax.text(-10.1 * K, 58.55 - i * .28, l, va="center", family=MONO, fontsize=10.5, color=FG)
ax.scatter([-10.35 * K], [58.55 - 5 * .28], s=90, facecolors="none", edgecolors=SLATE, lw=1.5)
ax.text(-10.1 * K, 58.55 - 5 * .28, "1914 to 1918 raid", va="center", family=MONO, fontsize=10.5, color=SLATE)
for nm, lab, dx, dy in [("Liverpool", "Liverpool", -2.6, .1), ("Clydebank", "Clydebank", -2.4, .25), ("Belfast", "Belfast", -1.2, .55), ("Plymouth", "Plymouth", -2.0, -.3),
                        ("Coventry", "Coventry", 1.6, .7), ("Kingston upon Hull", "Hull", .8, .45), ("Bath", "Bath", -1.4, -.5)]:
    a = next(a for a in A if a["name"] == nm)
    ax.annotate(lab, (float(a["lon"]) * K, float(a["lat"])), (float(a["lon"]) * K + dx * K, float(a["lat"]) + dy), family=MONO, fontsize=10.5, color=FG,
                arrowprops=dict(arrowstyle="-", color=MUT, lw=.7), zorder=6)
h = next(r for r in W1 if r["id"] == "1914hart")
ax.annotate("Hartlepool,\n16 Dec 1914", (float(h["lon"]) * K, float(h["lat"])), (float(h["lon"]) * K - 3.3 * K, float(h["lat"]) + .35), family=MONO, fontsize=10.5, color=SLATE,
            arrowprops=dict(arrowstyle="-", color=SLATE, lw=.7), zorder=6)
ax.annotate("London", (-0.12 * K, 51.5), (-2.4 * K, 51.85), family=MONO, fontsize=11, color=FG, fontweight="medium", arrowprops=dict(arrowstyle="-", color=MUT, lw=.7), zorder=6)

# headline numbers
tx = fig.add_axes([0.60, 0.355, 0.37, 0.43]); tx.axis("off")
wd = R["worst_days"][0]; wa = R["worst_area_days"][0]
items = [
    (f"{R['london']['outside']:,}", f"civilians died outside Greater London, against\n{R['london']['greater']:,} in it. Liverpool alone lost {R['top_areas'][0]['deaths']:,}."),
    (f"{round(P['blitz']['london_share'] * 100)}%  to  {round(P['vweap']['london_share'] * 100)}%", f"London's share of the dead: during the Blitz of\n1940 to 1941, then in the V-1 and V-2 attacks\nof 1944 to 1945. In between, just {round(P['mid']['london_share'] * 100)}%."),
    (f"{wa['deaths']}", f"dead in Liverpool on 3 May 1941, the worst day\nfor any one place. The worst day overall,\n16 April 1941 ({wd['uk']:,}), was half London, half Belfast."),
    (f"{R['ww1']['hartlepool_1914'] + R['ww1']['hartlepool_1918']} v {R['hartlepool_ww2']}", f"Hartlepool's dead from German shells in 1914\nand a Zeppelin in 1918, against its rolls for\nthe whole Second World War."),
]
y = 0.995
for big, small in items:
    tx.text(0, y, big, fontproperties=DISP, fontsize=38, color=HOT, va="top", transform=tx.transAxes)
    tx.text(0, y - 0.105, small, family=SER, fontsize=13, color=FG, va="top", transform=tx.transAxes, linespacing=1.18)
    y -= 0.257

# small multiples: five periods
fig.text(0.045, 0.335, "WHERE THE DEAD FELL, PERIOD BY PERIOD  ·  % = SHARE IN GREATER LONDON", family=MONO, fontsize=11, color=MUT)
keys = [("early", "Before the Blitz", "to Sep 1940"), ("blitz", "The Blitz", "Sep 1940 to May 1941"), ("mid", "Baedeker, tip and run", "May 1941 to Jan 1944"),
        ("baby", "Baby Blitz", "Jan to Jun 1944"), ("vweap", "V-1 and V-2", "Jun 1944 to Mar 1945")]
for i, (k, lab, when) in enumerate(keys):
    a2 = fig.add_axes([0.035 + i * 0.188, 0.178, 0.18, 0.145]); a2.set_facecolor(BG)
    land(a2, .3); fire(a2, [int(a["p_" + k]) for a in A], 0.21, glow=False)
    a2.set_xlim(-8.0 * K, 1.9 * K); a2.set_ylim(49.9, 58.8); a2.set_aspect(1); a2.axis("off")
    a2.text(.02, -.02, lab, transform=a2.transAxes, family=SER, fontsize=12.5, color=FG, va="top", fontweight="semibold")
    a2.text(.02, -.12, f"{when}\n{P[k]['uk']:,} dead", transform=a2.transAxes, family=MONO, fontsize=9.5, color=MUT, va="top", linespacing=1.35)
    a2.text(.98, .97, f"{round(P[k]['london_share'] * 100)}%", transform=a2.transAxes, fontproperties=DISP, fontsize=22, color=FG if P[k]["london_share"] > .5 else HOT, ha="right", va="top")

# weekly strip
a3 = fig.add_axes([0.065, 0.072, 0.9, 0.028]); a3.set_facecolor(BG)
d0 = DAILY[0][0]; wk = {}
for d, n, l in DAILY:
    kk = (d - d0).days // 7; w = wk.setdefault(kk, [0, 0]); w[0] += n; w[1] += l
ks = [kk for kk in sorted(wk) if d0 + dt.timedelta(days=7 * kk) <= dt.date(1945, 6, 30)]
xs = [d0 + dt.timedelta(days=7 * kk) for kk in ks]
lon = np.array([wk[kk][1] for kk in ks]); out = np.array([wk[kk][0] - wk[kk][1] for kk in ks])
a3.bar(xs, lon, width=6, color=FG); a3.bar(xs, out, bottom=lon, width=6, color=HOT)
for s in ("top", "right", "left"): a3.spines[s].set_visible(False)
a3.spines["bottom"].set_color(MUT); a3.set_yticks([]); a3.tick_params(colors=FG, labelsize=10)
for t in a3.get_xticklabels(): t.set_fontfamily(MONO)
a3.set_xlim(dt.date(1939, 9, 1), dt.date(1945, 6, 30))
fig.text(0.065, 0.108, "CIVILIAN DEAD PER WEEK, 1939 TO 1945: BLACK = GREATER LONDON, ORANGE = ELSEWHERE", family=MONO, fontsize=11, color=MUT)

fig.text(0.045, 0.008,
         "Data: Commonwealth War Graves Commission, Find War Dead (Civilian War Dead 1939-1945), exported 28 Oct 2026, counts only, by civic area and\n"
         "date of death; places: OS Open Names (OGL v3), Wikidata (CC0); 1914 to 1918 raids: Wikipedia (CC BY-SA 4.0), English Heritage, Ian Castle;\n"
         "coast: Natural Earth. Dots mark the town an area is named after. Analysis and chart: Tristan Hotham, with Python and matplotlib.",
         family=MONO, fontsize=9.5, color=MUT, linespacing=1.45)
fig.savefig(os.path.join(HERE, "was_the_blitz_londons.png"), facecolor=BG)
print("collage written")
