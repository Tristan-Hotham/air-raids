"""Step 5. Render header.png (1200x630 social card) with Playwright Chromium.

Fonts: FONT_DIR holding FrauncesVar.ttf, SourceSerif4-Regular.ttf, IBMPlexMono-Regular.ttf, IBMPlexMono-Medium.ttf
(from github.com/google/fonts); otherwise system serif is used. Coastline: data/coast_ne10m.json (Natural Earth, public domain).
Run: FONT_DIR=/path/to/fonts python3 code/05_header.py
"""
import csv, json, math, os
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
A = [a for a in csv.DictReader(open(os.path.join(ROOT, "data", "ww2_areas.csv"), encoding="utf-8")) if a["scope"] == "uk" and a["lat"]]
W1 = [r for r in csv.DictReader(open(os.path.join(ROOT, "data", "ww1_incidents.csv"), encoding="utf-8")) if r["lat"]]
FD = os.environ.get("FONT_DIR", "")
K = math.cos(math.radians(54.5))
X0, X1, Y0, Y1 = -8.3 * K, 2.0 * K, -59.0, -49.9
Hh = 610; Ww = Hh * (X1 - X0) / (Y1 - Y0)
pr = lambda lat, lon: ((lon * K - X0) / (Y1 - Y0) * Hh, (-lat - Y0) / (Y1 - Y0) * Hh)
land = ""
for g in json.load(open(os.path.join(ROOT, "data", "coast_ne10m.json"))):
    for poly in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
        land += "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in (pr(q[1], q[0]) for q in poly[0])) + "Z"
COL = ["#F6D79A", "#F0A65A", "#DD6F2E", "#B9431B", "#7E2410"]
dots = ""
for a in sorted(A, key=lambda a: -int(a["deaths"])):
    n = int(a["deaths"]); x, y = pr(float(a["lat"]), float(a["lon"])); rr = min(22, 0.8 + math.sqrt(n) * 0.33)
    c = COL[sum(n >= t for t in (10, 50, 250, 1000))]
    dots += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr * 2.2:.1f}" fill="#F2B33D" fill-opacity=".10"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{rr:.1f}" fill="{c}" fill-opacity=".85" stroke="#EEECE7" stroke-width=".5"/>'
for r in W1:
    x, y = pr(float(r["lat"]), float(r["lon"])); dots += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{max(3, math.sqrt(int(r["killed"])) * .9):.1f}" fill="none" stroke="#3E5878" stroke-width="2"/>'
ff = ""
if FD:
    ff = "".join(f"@font-face{{font-family:'{n}';src:url('file://{FD}/{f}');font-weight:{w};}}" for n, f, w in [
        ("Fraunces", "FrauncesVar.ttf", "100 900"), ("Source Serif 4", "SourceSerif4-Regular.ttf", "400"),
        ("IBM Plex Mono", "IBMPlexMono-Regular.ttf", "400"), ("IBM Plex Mono", "IBMPlexMono-Medium.ttf", "500")])
html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{ff}
body{{margin:0;width:1200px;height:630px;background:radial-gradient(circle at 78% 45%,#FFF6DE 0%,#F1EEE7 45%,#E2DED5 100%);color:#1D1C1A;overflow:hidden;position:relative;font-family:'Source Serif 4',Georgia,serif}}
.k{{position:absolute;left:70px;top:60px;font:500 15px/1 'IBM Plex Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:#66625B;display:flex;gap:12px;align-items:center}}
.k b{{background:#C8481C;color:#fff;padding:7px 9px;font-weight:500}}
h1{{position:absolute;left:64px;top:100px;margin:0;font:900 108px/.9 Fraunces,Georgia,serif;letter-spacing:-.02em;width:720px}}
h1 em{{font-style:normal;color:#C8481C}}
p{{position:absolute;left:70px;top:330px;width:620px;margin:0;font-size:25px;line-height:1.36}}
p b{{color:#C8481C}} p i{{font-style:normal;color:#3E5878;font-weight:600}}
.f{{position:absolute;left:70px;bottom:38px;font:400 14px/1 'IBM Plex Mono',monospace;letter-spacing:.12em;text-transform:uppercase;color:#66625B}}
svg{{position:absolute;right:20px;top:10px}}
</style></head><body>
<div class="k"><b>Data study</b><span>Remembrance · 1914 to 1945</span></div>
<h1>Bombs on <em>Britain</em></h1>
<p>Where the air raids killed. <b>{R['cwgc']['uk']:,}</b> civilians on the Second World War roll, <b>{round(R['london']['outside_share'] * 100)}%</b> of them outside London, and <i>{R['ww1']['air_killed']:,}</i> killed by Zeppelins and Gothas in the First World War.</p>
<div class="f">Dr Tristan Hotham · Independent researcher</div>
<svg width="{Ww:.0f}" height="{Hh}" viewBox="0 0 {Ww:.0f} {Hh}"><path d="{land}" fill="#DDD8CD" stroke="#C3BDB1" stroke-width="1"/>{dots}</svg>
</body></html>"""
tmp = os.path.join(ROOT, "work", "header.html"); open(tmp, "w").write(html)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 630})
    pg.goto("file://" + os.path.abspath(tmp)); pg.wait_for_timeout(600)
    pg.screenshot(path=os.path.join(ROOT, "header.png")); b.close()
os.remove(tmp)
print("header.png written")
