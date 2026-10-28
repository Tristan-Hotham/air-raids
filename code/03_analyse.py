"""Step 3. All statistics for the page, paper, blog and collage: writes data/results.json, data/populations.csv,
data/stories.csv, data/wikipedia_compare.csv and work/site_data.json (the map and chart data for the page).
Every number used anywhere comes from results.json.
Run: python3 code/03_analyse.py
"""
import collections, csv, datetime as dt, json, os, re, statistics
from common import DATA, WORK, WIKI9, articles, strip, wiki_has, wurl, nodash

R = {}
D = lambda s: dt.date.fromisoformat(s)
ww1 = json.load(open(os.path.join(WORK, "ww1.json")))
meta2 = json.load(open(os.path.join(WORK, "ww2.json")))
A = list(csv.DictReader(open(os.path.join(DATA, "ww2_areas.csv"), encoding="utf-8")))
for a in A:
    for k in ("aid", "deaths", "peak_deaths", "age_stated", "under16", "over60", "county_of_london", "greater_london"): a[k] = int(a[k])
    for k, *_ in meta2["periods"]: a["p_" + k] = int(a["p_" + k])
AID = {a["aid"]: a for a in A}
daily = [(D(r["date"]), int(r["uk_deaths"]), int(r["greater_london"]), int(r["county_of_london"])) for r in csv.DictReader(open(os.path.join(DATA, "ww2_daily.csv")))]
AD = collections.Counter({(aid, D(d)): n for aid, d, n in json.load(open(os.path.join(WORK, "area_day.json")))})
months = collections.defaultdict(dict)
for r in csv.DictReader(open(os.path.join(DATA, "ww2_area_month.csv"))): months[int(r["aid"])][r["month"]] = int(r["deaths"])
age = [(r["age_band"], int(r["uk_deaths"])) for r in csv.DictReader(open(os.path.join(DATA, "ww2_age.csv")))]

# ---------------- First World War ----------------
W1 = ww1["rows"]; T1 = ww1["totals"]
air = T1["airship"]["killed"] + T1["aeroplane"]["killed"]
listed_civ = [r for r in W1 if r["who"] not in ("soldiers", "sailors", "mostly soldiers")]
R["ww1"] = dict(
    airship_killed=T1["airship"]["killed"], aeroplane_killed=T1["aeroplane"]["killed"], air_killed=air,
    airship_injured=T1["airship"]["injured"], aeroplane_injured=T1["aeroplane"]["injured"], air_injured=T1["airship"]["injured"] + T1["aeroplane"]["injured"],
    london_killed=T1["london_mpd"]["killed"], london_injured=T1["london_mpd"]["injured"], outside_air=air - T1["london_mpd"]["killed"],
    london_share=T1["london_mpd"]["killed"] / air, dec1914=T1["dec1914"]["killed"], dec1914_casualties=T1["dec1914"]["injured"],
    n_incidents=len(W1), n_mapped=sum(1 for r in W1 if r["lat"] != ""), listed_killed=sum(r["killed"] for r in W1),
    listed_military=sum(r["killed"] for r in W1 if r["who"] in ("soldiers", "sailors")),
    naval_killed_listed=sum(r["killed"] for r in W1 if r["attack"] == "naval"),
    hartlepool_1914=next(r["killed"] for r in W1 if r["id"] == "1914hart"), hartlepool_1918=next(r["killed"] for r in W1 if r["id"] == "1918hart"),
    scarborough_1914=next(r["killed"] for r in W1 if r["id"] == "1914scar"), whitby_1914=next(r["killed"] for r in W1 if r["id"] == "1914whit"),
    lowestoft_1916=next(r["killed"] for r in W1 if r["id"] == "1916lowe"), folkestone=next(r["killed"] for r in W1 if r["id"] == "1917folk"),
    poplar_june=next(r["killed"] for r in W1 if r["id"] == "1917jun"), poplar_school=18, yarmouth=4,
    chatham=next(r["killed"] for r in W1 if r["id"] == "1917chat"), tipton=next(r["killed"] for r in W1 if r["id"] == "1916blac"),
    years=dict(collections.Counter(r["date"][:4] for r in W1)),
    raids_airship=51, raids_aeroplane=52)
assert wiki_has("Mayflower Primary School, Poplar", "resulting in the deaths of eighteen children")
assert wiki_has("German bombing of Britain, 1914–1918", "Aeroplanes carried out 52 raids")
R["ww1"]["top"] = [dict(id=r["id"], date=r["date"], places=r["places"], killed=r["killed"], who=r["who"], attack=r["attack"], london=r["london"])
                   for r in sorted(W1, key=lambda r: -r["killed"])[:12]]
by_kind = collections.Counter(); by_kind_n = collections.Counter()
for r in W1: by_kind[r["attack"]] += r["killed"]; by_kind_n[r["attack"]] += 1
R["ww1"]["by_attack"] = {k: dict(killed=by_kind[k], n=by_kind_n[k]) for k in by_kind}
R["ww1"]["listed_london"] = sum(r["killed"] for r in W1 if r["london"])
R["ww1"]["listed_outside"] = sum(r["killed"] for r in W1 if not r["london"])

# ---------------- Second World War ----------------
tot = lambda rows: sum(a["deaths"] for a in rows)
UK = [a for a in A if a["scope"] == "uk"]
R["cwgc"] = dict(rows=meta2["n_rows"], retrieved=meta2["retrieved"][:10], last=meta2["last_date"],
                 uk=tot(UK), overseas=tot(a for a in A if a["scope"] == "overseas"), sea=tot(a for a in A if a["scope"] == "sea"),
                 crown=tot(a for a in A if a["scope"] == "crown"), areas=len(A), uk_areas=len(UK),
                 uk_placed=tot(a for a in UK if a["lat"] != ""), uk_placed_areas=sum(1 for a in UK if a["lat"] != ""),
                 capped_days=[x for x in meta2["log"] if x.startswith("CAP")], malta=next(a["deaths"] for a in A if a["area"] == "MALTA, G.C."))
R["cwgc"]["uk_share"] = R["cwgc"]["uk"] / R["cwgc"]["rows"]; R["cwgc"]["placed_share"] = R["cwgc"]["uk_placed"] / R["cwgc"]["uk"]
gl = tot(a for a in UK if a["greater_london"]); col = tot(a for a in UK if a["county_of_london"])
R["london"] = dict(greater=gl, county=col, outer=gl - col, outside=R["cwgc"]["uk"] - gl, greater_share=gl / R["cwgc"]["uk"], county_share=col / R["cwgc"]["uk"],
                   outside_share=1 - gl / R["cwgc"]["uk"], n_greater_areas=sum(1 for a in UK if a["greater_london"]))
nat = collections.Counter()
for a in UK: nat[a["nation"]] += a["deaths"]
R["nations"] = [dict(nation=k, deaths=v, share=v / R["cwgc"]["uk"]) for k, v in nat.most_common()]
# periods
P = []
for k, lab, s, e in meta2["periods"]:
    u = sum(a["p_" + k] for a in UK); l = sum(a["p_" + k] for a in UK if a["greater_london"])
    P.append(dict(key=k, label=lab, start=s, end=e, uk=u, london=l, outside=u - l, london_share=l / u if u else 0, share=u / R["cwgc"]["uk"],
                  days=(D(e) - D(s)).days + 1 if k != "after" else None))
for p in P: p["outside_share"] = 1 - p["london_share"]
R["periods"] = P; PK = {p["key"]: p for p in P}
yr = collections.Counter(); yrl = collections.Counter()
for d, n, l, c in daily: yr[d.year] += n; yrl[d.year] += l
R["years"] = [dict(year=y, uk=yr[y], london=yrl[y], outside=yr[y] - yrl[y]) for y in sorted(yr)]
# worst days nationally and per area
wd = sorted(daily, key=lambda x: -x[1])[:12]
R["worst_days"] = [dict(date=d.isoformat(), uk=n, london=l, outside=n - l) for d, n, l, c in wd]
top_ad = sorted(AD.items(), key=lambda x: -x[1])[:25]
R["worst_area_days"] = [dict(area=AID[a]["name"], kind=AID[a]["kind"], date=d.isoformat(), deaths=n, london=AID[a]["greater_london"]) for (a, d), n in top_ad]
R["sep7_london"] = next(l for d, n, l, c in daily if d == dt.date(1940, 9, 7))
R["worst12_outside_majority"] = sum(1 for w in R["worst_days"] if w["outside"] > w["london"])
# ages
known = [(b, n) for b, n in age if b != "0 or not stated"]; nk = sum(n for b, n in known)
R["age"] = dict(bands=[dict(band=b, n=n) for b, n in age], stated=nk, not_stated=dict(age)["0 or not stated"],
                under16=dict(age)["1 to 4"] + dict(age)["5 to 15"], under5=dict(age)["1 to 4"])
R["age"]["under16_share"] = R["age"]["under16"] / nk
R["age"]["over60"] = sum(a["over60"] for a in UK); R["age"]["over60_share"] = R["age"]["over60"] / nk
R["age"]["median"] = None
# top areas
def arow(a):
    return dict(aid=a["aid"], name=a["name"], kind=a["kind"], nation=a["nation"], deaths=a["deaths"], london=a["greater_london"], county_of_london=a["county_of_london"],
                peak_day=a["peak_day"], peak=a["peak_deaths"], first=a["first"], last=a["last"],
                blitz=a["p_blitz"], vweap=a["p_vweap"], mid=a["p_mid"], baby=a["p_baby"], early=a["p_early"],
                under16=a["under16"], age_stated=a["age_stated"])
R["top_areas"] = [arow(a) for a in sorted(UK, key=lambda a: -a["deaths"])[:40]]
R["top_outside"] = [arow(a) for a in sorted([a for a in UK if not a["greater_london"]], key=lambda a: -a["deaths"])[:25]]
R["top_london"] = [arow(a) for a in sorted([a for a in UK if a["greater_london"]], key=lambda a: -a["deaths"])[:15]]
R["n_areas_100"] = sum(1 for a in UK if a["deaths"] >= 100); R["n_areas_100_outside"] = sum(1 for a in UK if a["deaths"] >= 100 and not a["greater_london"])
R["n_areas_any"] = len(UK)

# V weapons: where
v = sorted(UK, key=lambda a: -a["p_vweap"])
R["vweap_top"] = [dict(name=a["name"], deaths=a["p_vweap"], london=a["greater_london"]) for a in v[:12]]
R["vweap_outside_top"] = [dict(name=a["name"], deaths=a["p_vweap"]) for a in v if not a["greater_london"]][:8]

# window helper
def window(aids, s, e):
    return sum(n for (a, d), n in AD.items() if a in aids and s <= d <= e)
def area(name):
    return next(a for a in A if a["area"] == name)
def win_area(name, s, e):
    a = area(name)
    m = {r: n for r, n in months[a["aid"]].items()}
    return sum(n for (x, d), n in AD.items() if x == a["aid"] and D(s) <= d <= D(e)) if True else 0
# NB: area_day.json only holds area-days with 5 or more deaths; windows below therefore use the monthly
# file when a whole month is wanted and the area-day file only for single big raids (stated in the text).

# Baedeker raids, April to June 1942, from monthly counts
BAED = [("EXETER, COUNTY BOROUGH", "Exeter"), ("BATH, COUNTY BOROUGH", "Bath"), ("NORWICH, COUNTY BOROUGH", "Norwich"), ("YORK, CITY AND COUNTY BOROUGH", "York"), ("CANTERBURY, COUNTY BOROUGH", "Canterbury")]
R["baedeker"] = [dict(name=n, apr_jun_1942=sum(months[area(c)["aid"]].get(m, 0) for m in ("1942-04", "1942-05", "1942-06")), total=area(c)["deaths"]) for c, n in BAED]
R["baedeker_sum"] = sum(x["apr_jun_1942"] for x in R["baedeker"])

# tip and run years: March 1942 to June 1943, areas outside London
TR = []
for a in UK:
    if a["greater_london"]: continue
    n = sum(v for m, v in months[a["aid"]].items() if "1942-03" <= m <= "1943-06")
    if n: TR.append((n, a))
TR.sort(key=lambda x: -x[0])
R["tipandrun_top"] = [dict(name=a["name"], deaths=n, total=a["deaths"]) for n, a in TR[:15]]

# Dover shelling and bombing by year
dov = area("DOVER, MUNICIPAL BOROUGH")
R["seaside"] = {x["name"]: x["deaths"] for x in R["tipandrun_top"]}
R["dover"] = dict(total=dov["deaths"], by_year={y: sum(v for m, v in months[dov["aid"]].items() if m.startswith(str(y))) for y in range(1940, 1946)})
# Hartlepool then and now
R["hartlepool_ww2"] = area("HARTLEPOOL, MUNICIPAL BOROUGH")["deaths"] + area("WEST HARTLEPOOL, COUNTY BOROUGH")["deaths"]
R["scarborough_ww2"] = area("SCARBOROUGH, MUNICIPAL BOROUGH")["deaths"]
R["whitby_ww2"] = area("WHITBY, URBAN DISTRICT")["deaths"]
R["yarmouth_ww2"] = area("GREAT YARMOUTH, COUNTY BOROUGH")["deaths"]
R["lowestoft_ww2"] = area("LOWESTOFT, MUNICIPAL BOROUGH")["deaths"]
R["folkestone_ww2"] = area("FOLKESTONE, MUNICIPAL BOROUGH")["deaths"]

# ---------------- stories: CWGC count on the day or days of named incidents ----------------
STORIES = [  # key, title, area, from, to, war-time fact (Wikipedia article, quote that must be in it)
    ("balham", "Balham station", "WANDSWORTH, METROPOLITAN BOROUGH", "1940-10-14", "1940-10-15", "Balham station", "sixty-six people in the station were killed"),
    ("coventry", "Coventry, 14 November 1940", "COVENTRY, COUNTY BOROUGH", "1940-11-14", "1940-11-16", "Coventry Blitz", "An estimated 568 people were killed in the raid"),
    ("bank", "Bank station", "LONDON CITY", "1941-01-11", "1941-01-12", "Bank and Monument stations", "killing 56 people"),
    ("cafe", "Café de Paris", "WESTMINSTER CITY", "1941-03-08", "1941-03-09", "Café de Paris, London", "At least 34 people were killed"),
    ("clydebank", "Clydebank", "CLYDEBANK, BURGH OF, SCOTLAND", "1941-03-13", "1941-03-15", "Clydebank Blitz", "1,200 people died"),
    ("belfast", "Belfast, Easter Tuesday 1941", "BELFAST, COUNTY BOROUGH, N. IRELAND", "1941-04-15", "1941-04-17", "Belfast Blitz", "Some 987 people died as a result of the bombing"),
    ("liverpool", "Liverpool's May Blitz", "LIVERPOOL, COUNTY BOROUGH", "1941-05-01", "1941-05-08", "Liverpool Blitz", "a seven-night bombardment that devastated the city"),
    ("hull", "Hull, 7 to 9 May 1941", "KINGSTON-UPON-HULL, COUNTY BOROUGH", "1941-05-07", "1941-05-09", "Hull Blitz", "resulting in just under 400 deaths"),
    ("bath", "Bath, April 1942", "BATH, COUNTY BOROUGH", "1942-04-25", "1942-04-28", "Bath Blitz", "417 people were killed"),
    ("sandhurst", "Sandhurst Road School", "LEWISHAM, METROPOLITAN BOROUGH", "1943-01-20", "1943-01-21", "Bombing of Sandhurst Road School", "killing 38 children"),
    ("bethnal", "Bethnal Green tube shelter", "BETHNAL GREEN, METROPOLITAN BOROUGH", "1943-03-03", "1943-03-04", "Bethnal Green tube station", "173 people, including 62 children, were killed in a crush"),
    ("newcross", "Woolworth's, New Cross", "DEPTFORD, METROPOLITAN BOROUGH", "1944-11-25", "1944-11-26", "V-2 rocket", "160 were killed and 108 seriously injured in one explosion"),
    ("orpington", "The last V-2, Orpington", "ORPINGTON, URBAN DISTRICT", "1945-03-27", "1945-03-27", "V-2 rocket", "the final civilian casualty of the war on British soil"),
]
# full area-day counts for the story windows (computed here from the area-day file, which keeps days with 5 or more
# deaths, plus the daily file for the single-death last V-2)
AD_ALL = collections.Counter()
import gzip, io
from common import CWGC
J = json.load(gzip.open(CWGC))
for r in csv.DictReader(io.StringIO(J["csv"])):
    AD_ALL[(r["Cemetery"].strip(), dt.datetime.strptime(r["DateOfDeath"], "%d/%m/%Y").date())] += 1   # counts only
del J
st = []
for key, title, ar, s, e, art, q in STORIES:
    assert wiki_has(art, q), (key, q)
    n = sum(v for (c, d), v in AD_ALL.items() if c == ar and D(s) <= d <= D(e))
    a = area(ar)
    st.append(dict(key=key, title=title, area=a["name"], date_from=s, date_to=e, cwgc=n, area_total=a["deaths"], lat=a["lat"], lon=a["lon"],
                   source=wurl(art), quote=q))
R["stories"] = {x["key"]: x for x in st}
# the very last date with a death in Orpington, and the last V-2 day nationally
R["last_v2_day_uk"] = sum(v for (c, d), v in AD_ALL.items() if d == D("1945-03-27") and area(c)["scope"] == "uk")
# Tynemouth (North Shields) 3 and 4 May 1941, Wilkinson's lemonade factory shelter
assert wiki_has("Bethnal Green tube station", "The largest number killed by a wartime bomb was 107 at Wilkinson's Lemonade Factory in North Shields (1941)")
R["stories"]["northshields"] = dict(key="northshields", title="Wilkinson's lemonade factory, North Shields", area="Tynemouth",
    date_from="1941-05-03", date_to="1941-05-04", cwgc=sum(v for (c, d), v in AD_ALL.items() if c == "TYNEMOUTH, COUNTY BOROUGH" and D("1941-05-03") <= d <= D("1941-05-04")),
    area_total=area("TYNEMOUTH, COUNTY BOROUGH")["deaths"], source=wurl("Bethnal Green tube station"),
    quote="The largest number killed by a wartime bomb was 107 at Wilkinson's Lemonade Factory in North Shields (1941)")
with open(os.path.join(DATA, "stories.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["key", "title", "area", "date_from", "date_to", "cwgc", "area_total", "source", "quote"], extrasaction="ignore")
    w.writeheader(); w.writerows(R["stories"].values())

# ---------------- CWGC against the figures in Wikipedia ----------------
CMP = [("Liverpool", ["LIVERPOOL, COUNTY BOROUGH", "BOOTLE, COUNTY BOROUGH", "BIRKENHEAD, COUNTY BOROUGH", "WALLASEY, COUNTY BOROUGH", "CROSBY, MUNICIPAL BOROUGH", "LITHERLAND, URBAN DISTRICT", "BEBINGTON, MUNICIPAL BOROUGH", "HUYTON-WITH-ROBY, URBAN DISTRICT"],
        4000, "Liverpool Blitz", "Around 4,000 people were killed in the Merseyside area during the Blitz", "Merseyside: eight Merseyside rolls"),
       ("Birmingham", ["BIRMINGHAM, COUNTY BOROUGH"], 2241, "Birmingham Blitz", "In total, 2,241 people were killed", ""),
       ("Bristol", ["BRISTOL, COUNTY BOROUGH"], 1299, "Bristol Blitz", "1,299 people killed", ""),
       ("Coventry", ["COVENTRY, COUNTY BOROUGH"], 1236, "Coventry Blitz", "some 1,236 people had been killed by air raids on Coventry", "to August 1942"),
       ("Clydebank", ["CLYDEBANK, BURGH OF, SCOTLAND"], 1200, "Clydebank Blitz", "1,200 people died", "the burgh's memorial castings name 528"),
       ("Hull", ["KINGSTON-UPON-HULL, COUNTY BOROUGH"], 1200, "Hull Blitz", "almost 1,200 people in the city killed", ""),
       ("Plymouth", ["PLYMOUTH, COUNTY BOROUGH"], 1174, "Plymouth Blitz", "at least 1,174 civilians were killed", ""),
       ("Belfast", ["BELFAST, COUNTY BOROUGH, N. IRELAND"], 987, "Belfast Blitz", "Some 987 people died as a result of the bombing", "Easter raid only"),
       ("Portsmouth", ["PORTSMOUTH, COUNTY BOROUGH"], 930, "History of Portsmouth", "930 people were killed", ""),
       ("Sheffield", ["SHEFFIELD, COUNTY BOROUGH"], 660, "Sheffield Blitz", "In total over 660 people were killed", "December 1940 raids"),
       ("Southampton", ["SOUTHAMPTON, COUNTY BOROUGH"], 631, "Southampton Blitz", "631 people died, 898 people were seriously wounded", ""),
       ("Bath", ["BATH, COUNTY BOROUGH"], 417, "Bath Blitz", "417 people were killed", "April 1942"),
       ("Norwich", ["NORWICH, COUNTY BOROUGH"], 340, "Norwich Blitz", "340 by bombing throughout the war", ""),
       ("Sunderland", ["SUNDERLAND, COUNTY BOROUGH"], 273, "Sunderland Blitz", "273 civilians were killed and 838 injured", ""),
       ("Greenock", ["GREENOCK, BURGH OF, SCOTLAND"], 271, "Greenock Blitz", "Over the two nights, 271 people were killed", "May 1941"),
       ("Swansea", ["SWANSEA, COUNTY BOROUGH, WALES"], 230, "Swansea Blitz", "230 killed, 397 injured", "February 1941 (infobox)"),
       ("Nottingham", ["NOTTINGHAM, COUNTY BOROUGH"], 186, "Nottingham Blitz", "lists 186 civilians died in Nottingham County Borough", ""),
       ("Barrow-in-Furness", ["BARROW IN FURNESS, COUNTY BOROUGH"], 83, "Barrow Blitz", "83 civilians were killed", "")]
cmp = []
for town, rolls, wn, art, q, note in CMP:
    if not wiki_has(art, q):
        assert q in articles()[art], (town, q)   # infobox text
    n = sum(area(c)["deaths"] for c in rolls)
    cmp.append(dict(town=town, cwgc=n, wikipedia=wn, ratio=n / wn, n_rolls=len(rolls), note=note, article=art, source=wurl(art), quote=q))
R["compare"] = cmp
with open(os.path.join(DATA, "wikipedia_compare.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(cmp[0])); w.writeheader(); w.writerows(cmp)
R["compare_by"] = {c["town"]: c for c in cmp}; R["compare_n"] = len(cmp)
R["compare_within10"] = sum(1 for c in cmp if abs(c["ratio"] - 1) <= 0.10)

# ---------------- deaths per 1,000 people ----------------
wk = json.load(open(WIKI9))["List of towns and cities in England by historical population"]["text"]
def table(y):
    i = wk.find("|+ " + y) if ("|+ " + y) in wk else wk.find("|+" + y)
    j = wk.find("|}", i)
    return {(b or a): int(c.replace(",", "")) for a, b, c in re.findall(r"\|\|?\s*\[\[([^\]|]+)(?:\|([^\]]+))?\]\]\s*\|\|\s*([\d,]+)", wk[i:j])}
t21, t51 = table("1921"), table("1951")
assert t21 and t51
POPMAP = {"Birmingham": "BIRMINGHAM, COUNTY BOROUGH", "Liverpool": "LIVERPOOL, COUNTY BOROUGH", "Manchester": "MANCHESTER, COUNTY BOROUGH", "Sheffield": "SHEFFIELD, COUNTY BOROUGH",
          "Leeds": "LEEDS, COUNTY BOROUGH", "Bristol": "BRISTOL, COUNTY BOROUGH", "Bradford": "BRADFORD, COUNTY BOROUGH", "Hull": "KINGSTON-UPON-HULL, COUNTY BOROUGH",
          "Newcastle": "NEWCASTLE-UPON-TYNE, COUNTY BOROUGH", "Nottingham": "NOTTINGHAM, COUNTY BOROUGH", "Portsmouth": "PORTSMOUTH, COUNTY BOROUGH",
          "Stoke-on-Trent": "STOKE-ON-TRENT, COUNTY BOROUGH", "Leicester": "LEICESTER, COUNTY BOROUGH", "Salford": "SALFORD, COUNTY BOROUGH", "Plymouth": "PLYMOUTH, COUNTY BOROUGH",
          "Bolton": "BOLTON, COUNTY BOROUGH", "Southampton": "SOUTHAMPTON, COUNTY BOROUGH", "Sunderland": "SUNDERLAND, COUNTY BOROUGH", "Birkenhead": "BIRKENHEAD, COUNTY BOROUGH",
          "Oldham": "OLDHAM, COUNTY BOROUGH", "Brighton": "BRIGHTON, COUNTY BOROUGH", "Middlesbrough": "MIDDLESBROUGH, COUNTY BOROUGH", "Derby": "DERBY, COUNTY BOROUGH",
          "Coventry": "COVENTRY, COUNTY BOROUGH", "Blackburn": "BLACKBURN, COUNTY BOROUGH", "Gateshead": "GATESHEAD, COUNTY BOROUGH", "Stockport": "STOCKPORT, COUNTY BOROUGH",
          "Wolverhampton": "WOLVERHAMPTON, COUNTY BOROUGH", "Norwich": "NORWICH, COUNTY BOROUGH", "South Shields": "SOUTH SHIELDS, COUNTY BOROUGH", "Preston": "PRESTON, COUNTY BOROUGH",
          "Huddersfield": "HUDDERSFIELD, COUNTY BOROUGH", "Southend-on-Sea": "SOUTHEND ON SEA, COUNTY BOROUGH", "St Helens": "ST. HELENS, COUNTY BOROUGH",
          "Walsall": "WALSALL, COUNTY BOROUGH", "Reading": "READING, COUNTY BOROUGH"}
# start-of-war figures stated in the city's own Wikipedia article take priority
START = {"Plymouth": (220000, "Plymouth Blitz", "At the outbreak of the Second World War, Plymouth had a population of approximately 220,000."),
         "Hull": (320000, "Hull Blitz", "Of a population of approximately 320,000 at the beginning of the war")}
LONDON_POP = (4000000, "History of London (1900–1939)", "the population of which actually fell during the interwar years from 4.5 to 4 million")
pops = []
for town, c in POPMAP.items():
    if town not in t21 or town not in t51: continue
    a = area(c)
    if town in START:
        p, art, q = START[town]; assert wiki_has(art, q); src = f"Wikipedia, {art}: start of the war"
    else:
        p = (t21[town] + t51[town]) / 2; src = f"Mean of the 1921 ({t21[town]:,}) and 1951 ({t51[town]:,}) census figures, Wikipedia list of towns by historical population"
    pops.append(dict(name=a["name"], area=c, population=round(p), deaths=a["deaths"], per1000=1000 * a["deaths"] / p, source=src))
assert wiki_has(*LONDON_POP[1:])
pops.append(dict(name="County of London", area="28 metropolitan boroughs, the City and Westminster", population=LONDON_POP[0], deaths=col, per1000=1000 * col / LONDON_POP[0],
                 source="Wikipedia, History of London (1900 to 1939): about 4 million on the eve of the war"))
pops.sort(key=lambda r: -r["per1000"])
with open(os.path.join(DATA, "populations.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(pops[0])); w.writeheader(); w.writerows([dict(r, per1000=round(r["per1000"], 2)) for r in pops])
R["rates"] = [dict(name=r["name"], population=r["population"], deaths=r["deaths"], per1000=r["per1000"], start=r["source"].startswith("Wikipedia, ") and "start" in r["source"]) for r in pops]
R["rates_n"] = len(pops)
R["small_rolls"] = {n: area(c)["deaths"] for n, c in [("Leeds", "LEEDS, COUNTY BOROUGH"), ("Bradford", "BRADFORD, COUNTY BOROUGH"), ("Blackburn", "BLACKBURN, COUNTY BOROUGH"), ("Preston", "PRESTON, COUNTY BOROUGH")]}
R["rate_london"] = next(r for r in R["rates"] if r["name"] == "County of London")
R["rates_rank"] = {r["name"]: i + 1 for i, r in enumerate(R["rates"])}

# ---------------- comparisons across the wars ----------------
R["ratio_ww2_ww1"] = R["cwgc"]["uk"] / air
R["then_and_now"] = [dict(town="Hartlepool", ww1=R["ww1"]["hartlepool_1914"] + R["ww1"]["hartlepool_1918"], ww2=R["hartlepool_ww2"]),
                     dict(town="Scarborough", ww1=R["ww1"]["scarborough_1914"] + 3, ww2=R["scarborough_ww2"]),
                     dict(town="Folkestone", ww1=R["ww1"]["folkestone"], ww2=R["folkestone_ww2"]),
                     dict(town="Great Yarmouth", ww1=None, ww2=R["yarmouth_ww2"])]

# headline peaks
blitz_lon = PK["blitz"]["london"]
R["peak_day"] = R["worst_days"][0]
R["peak_month"] = max(((m, sum(v.get(m, 0) for aid, v in months.items() if AID[aid]["scope"] == "uk")) for m in sorted({m for v in months.values() for m in v})), key=lambda x: x[1])
R["first_death"] = next(d.isoformat() for d, n, l, c in daily if n)
R["n_days_100"] = sum(1 for d, n, l, c in daily if n >= 100)
R["n_days_any"] = sum(1 for d, n, l, c in daily if n)

# ---------------- site data ----------------
mlist = []
d = dt.date(1939, 9, 1)
while d <= dt.date(1945, 12, 1):
    mlist.append(d.strftime("%Y-%m")); d = (d.replace(day=28) + dt.timedelta(days=5)).replace(day=1)
mi = {m: i for i, m in enumerate(mlist)}
pts = []
for a in sorted(UK, key=lambda a: -a["deaths"]):
    if a["lat"] == "": continue
    ms = [[mi[m], n] for m, n in sorted(months[a["aid"]].items()) if m in mi]
    pts.append([float(a["lat"]), float(a["lon"]), a["name"], a["kind"], a["nation"][0], a["deaths"], a["greater_london"], a["peak_day"], a["peak_deaths"],
                a["p_blitz"], a["p_vweap"], a["under16"], a["age_stated"], ms])
w1m = []
for r in W1:
    w1m.append([r["lat"] if r["lat"] != "" else None, r["lon"] if r["lon"] != "" else None, r["date"], r["attack"], r["places"], r["killed"], r["who"], r["note"], r["source"], r["url"], r["london"], r["injured"]])
dl = [[n, l] for d, n, l, c in daily]
SITE = dict(months=mlist, pts=pts, ww1=w1m, daily0=daily[0][0].isoformat(), daily=dl,
            stories=[dict(k=k, t=v["title"], a=v["area"], d=v["date_from"], n=v["cwgc"], lat=v.get("lat"), lon=v.get("lon")) for k, v in R["stories"].items()])
json.dump(SITE, open(os.path.join(WORK, "site_data.json"), "w"), separators=(",", ":"), ensure_ascii=False)

def clean(o):
    if isinstance(o, float): return round(o, 6)
    if isinstance(o, dict): return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [clean(v) for v in o]
    return o
json.dump(clean(R), open(os.path.join(DATA, "results.json"), "w"), indent=1, ensure_ascii=False)
for k in ("cwgc", "london", "periods", "worst_days", "age", "rates", "compare", "stories", "baedeker", "tipandrun_top", "dover", "vweap_top", "then_and_now", "peak_month", "nations"):
    print(k, json.dumps(clean(R[k]), ensure_ascii=False)[:900])
