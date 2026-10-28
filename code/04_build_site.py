"""Step 4. Build index.html from code/page_template.html.

Every number in the text is a {{path|format}} token filled from data/results.json, so the page cannot drift
from the analysis. The map and chart data (work/site_data.json, from step 3) and a slim copy of the results are
embedded, so the page is a single self-contained file.
Run: python3 code/04_build_site.py
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
R = json.load(open(os.path.join(ROOT, "data", "results.json"), encoding="utf-8"))
MN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def get(path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(v):,}"
    if f == "pct": return f"{round(v * 100)}%"
    if f == "pct1": return f"{v * 100:.1f}%"
    if f in ("f1", "x1"): return f"{v:.1f}"
    if f in ("f2", "x2"): return f"{v:.2f}"
    if f == "date":
        y, m, d = map(int, v.split("-")); return f"{d} {MN[m - 1]} {y}"
    raise ValueError(f)


def sub(m):
    return fmt(get(m.group(1)), m.group(3))


TOK = r"\{\{([^}|]+)(\|(\w+))?\}\}"
# facts the template states in words: check them against the data
assert R["top_areas"][0]["name"] == "Liverpool" and R["top_outside"][1]["name"] == "Birmingham"
assert [a["name"] for a in R["top_outside"][2:6]] == ["Bristol", "Kingston upon Hull", "Plymouth", "Coventry"] and R["top_outside"][5]["deaths"] > 1000
assert [r["name"] for r in R["rates"][:3]] == ["Coventry", "Plymouth", "County of London"]
assert all(r["per1000"] >= 2.95 for r in R["rates"][3:9])
assert R["worst_days"][0]["date"] == "1941-04-16" and R["worst_area_days"][0]["area"] == "Liverpool"
assert [R["worst_area_days"][i]["area"] for i in (1, 2, 3, 6)] == ["Belfast", "Coventry", "Glasgow", "Clydebank"] and R["worst_area_days"][3]["date"] == R["worst_area_days"][6]["date"]
assert R["then_and_now"][0]["ww1"] > R["then_and_now"][0]["ww2"]
assert [x["name"] for x in R["vweap_top"][:5]] == ["Wandsworth", "Deptford", "Lambeth", "Lewisham", "West Ham"]
assert R["stories"]["orpington"]["cwgc"] == 1
assert R["cwgc"]["capped_days"] == ["CAP 1941-4-16"] and R["worst_days"][0]["date"] == "1941-04-16"

if __name__ == "__main__":
    tpl = open(os.path.join(HERE, "page_template.html"), encoding="utf-8").read()
    SITE = open(os.path.join(ROOT, "work", "site_data.json"), encoding="utf-8").read()
    html = re.sub(TOK, sub, tpl)
    slim = {k: R[k] for k in ["periods", "worst_days", "top_outside", "top_london", "rates", "age", "baedeker", "compare", "stories"]}
    html = html.replace("/*SITE*/", SITE).replace("/*RESULTS*/", json.dumps(slim, ensure_ascii=False, separators=(",", ":")))
    assert "{{" not in html
    vis = re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", html, flags=re.S))
    for bad in ("—", "–", "--"):
        assert bad not in vis, bad
        assert bad not in SITE, bad
    # visible strings inside the script (cards, labels) too
    js = re.search(r"<script>\nconst D.*?</script>", html, flags=re.S).group(0)
    for bad in ("—", "–"): assert bad not in js, bad
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print("index.html", len(html.encode()), "bytes")
