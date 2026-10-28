"""Shared helpers: paths, the Wikipedia reader and the OS Open Names gazetteer.

Paths to the shared inputs can be overridden with environment variables (see README).
"""
import csv, gzip, json, os, re, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
DATA = os.path.join(ROOT, "data")
WORK = os.path.join(ROOT, "work")
SRC12 = os.environ.get("DATA12", "/home/claude/hist/_data12")
OSNAMES = os.environ.get("OSNAMES", "/home/claude/hist/osnames_gb.tsv")
WIKI9 = os.environ.get("WIKI9", "/home/claude/hist/_data9/wikipedia_wikitext.json")
CWGC = os.path.join(SRC12, "cwgc_civilians.json.gz")
os.makedirs(DATA, exist_ok=True); os.makedirs(WORK, exist_ok=True)

_A = None


def articles():
    global _A
    if _A is None:
        _A = {}
        for f in ("wikipedia_batch12.json.gz", "wikipedia_batch12b.json.gz"):
            for t, a in json.load(gzip.open(os.path.join(SRC12, f)))["articles"].items():
                if a.get("text"): _A[t] = a["text"]
    return _A


def strip(t):
    """Wikitext to plain text (good enough for checking quotations)."""
    t = re.sub(r"<ref[^>]*/>", "", t); t = re.sub(r"<ref.*?</ref>", "", t, flags=re.S)
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    for _ in range(4): t = re.sub(r"\{\{(?:[^{}])*\}\}", "", t)
    t = re.sub(r"\[\[(?:File|Image):[^\[\]]*(?:\[\[[^\]]*\]\][^\[\]]*)*\]\]", "", t)
    t = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", t)
    t = t.replace("&nbsp;", " ").replace("'''", "").replace("''", "")
    return re.sub(r"\s+", " ", t)


def wiki_has(title, quote):
    return re.sub(r"\s+", " ", quote) in strip(articles()[title])


def wurl(title):
    from urllib.parse import quote
    return "https://en.wikipedia.org/wiki/" + quote(title.replace(" ", "_"), safe="_(),'")


def dash(s):
    """Visible-text form of a title: ranges with "to", never a dash."""
    return s.replace("\u2013", " to ").replace("\u2014", ", ").replace("  ", " ")


def norm(s):
    s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()
    s = s.replace("&", " and ").replace("'", "")
    s = re.sub(r"\bst\.? ", "st ", s); s = re.sub(r"\bsaint ", "st ", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


_G = None
RANK = {"City": 0, "Town": 1, "Other Settlement": 1, "Suburban Area": 2, "Village": 3, "Hamlet": 4}


def gazetteer():
    """name -> list of (rank, lat, lon, district, county, region, country) for populated places."""
    global _G
    if _G is None:
        _G = {}
        with open(OSNAMES, encoding="utf-8") as f:
            r = csv.DictReader(f, delimiter="\t")
            for row in r:
                if row["type"] != "populatedPlace": continue
                rec = (RANK.get(row["local_type"], 9), float(row["lat"]), float(row["lon"]), row["district"], row["county"], row["region"], row["country"])
                for n in (row["name1"], row["name2"]):
                    if n: _G.setdefault(norm(n), []).append(rec)
    return _G


def place(name, near=None, country=None, region=None):
    """Best OS Open Names populated place for a name: highest rank (city before town...), optionally
    restricted to a country, or nearest to a (lat, lon) hint."""
    c = gazetteer().get(norm(name))
    if not c: return None
    if region: c = [x for x in c if x[5] == region] or None
    if not c: return None
    if country: c = [x for x in c if x[6] == country] or None
    if not c: return None
    if near:
        return min(c, key=lambda x: (x[1] - near[0]) ** 2 + ((x[2] - near[1]) * 0.6) ** 2)
    if len(c) > 1:
        # several places share the name: prefer the one with the largest Wikidata population of that name within 8 km
        pops = wd_pops().get(norm(name), [])
        def score(x):
            best = max([pp for (la, lo, pp) in pops if (la - x[1]) ** 2 + ((lo - x[2]) * 0.6) ** 2 < 0.0052] or [0])
            return (-best, x[0])
        return min(c, key=score)
    return min(c, key=lambda x: x[0])


WD8 = os.environ.get("WD8", "/home/claude/hist/_data8/uk_bundle_wikidata_osm.json")
_W = None


def wd_pops():
    """Wikidata UK settlements with a population (CC0): norm label -> [(lat, lon, population)]."""
    global _W
    if _W is None:
        _W = {}
        for l in json.load(open(WD8))["wd_settlements_pop_tsv"].split("\n")[1:]:
            if not l: continue
            it, lab, cls, co, pop = l.split("\t")
            m = re.match(r"POINT\(([-\d.]+) ([-\d.]+)\)", co)
            if not m or '"' not in lab: continue
            try: pp = float(pop)
            except ValueError: continue
            _W.setdefault(norm(lab.split('"')[1]), []).append((float(m.group(2)), float(m.group(1)), pp))
    return _W


def nodash(s):
    return "—" not in s and "–" not in s and "--" not in s
