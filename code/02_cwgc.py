"""Step 2. Second World War: the Commonwealth War Graves Commission's Civilian War Dead roll, aggregated.

Input: cwgc_civilians.json.gz (CWGC Find War Dead, Civilian War Dead 1939 to 1945, CSV exports by month or day,
retrieved 28 Oct 2026). One row per person. Personal data never leaves this script: only counts by civic area,
date and age band are written. Names, addresses and the free-text "additional information" are not used at all.

Each roll is filed under a civic area (a county borough, metropolitan borough, municipal borough, urban or rural
district, Scottish burgh or county, a Northern Irish district, a country overseas, or a ship). I sort the areas
into the United Kingdom, the Crown dependencies, overseas and at sea, and place each UK area at a settlement of
the same name in OS Open Names (Great Britain) or Wikidata (Northern Ireland).
Writes data/ww2_areas.csv, data/ww2_daily.csv, data/ww2_area_month.csv, data/ww2_age.csv and work/ww2.json.
Run: python3 code/02_cwgc.py
"""
import collections, csv, datetime as dt, gzip, io, json, os, re, statistics
from common import CWGC, DATA, WORK, place, norm, gazetteer

WD8 = os.environ.get("WD8", "/home/claude/hist/_data8/uk_bundle_wikidata_osm.json")
KINDS = ["COUNTY BOROUGH", "METROPOLITAN BOROUGH", "MUNICIPAL BOROUGH", "URBAN DISTRICT", "RURAL DISTRICT", "BURGH OF", "CITY AND COUNTY BOROUGH", "BOROUGH"]
CROWN = {"GUERNSEY", "JERSEY", "SARK", "ISLE OF MAN"}
SEA = re.compile(r"^(S\.S\.|M\.V\.|H\.M\.|R\.M\.S\.|AIR CRASHES AT SEA|COUNTRY CRAFT)")
# Name fixes for the gazetteer (CWGC spelling -> OS Open Names name); only spelling, never a different place
FIX = {"KINGSTON-UPON-HULL": "Kingston upon Hull", "BARROW IN FURNESS": "Barrow-in-Furness", "NEWCASTLE-UPON-TYNE": "Newcastle upon Tyne",
       "SOUTHEND ON SEA": "Southend-on-Sea", "STOCKTON ON TEES": "Stockton-on-Tees", "BURTON-UPON-TRENT": "Burton upon Trent",
       "BERWICK ON TWEED": "Berwick-upon-Tweed", "HENLEY ON THAMES": "Henley-on-Thames", "NEWARK ON TRENT": "Newark-on-Trent",
       "STRATFORD UPON AVON": "Stratford-upon-Avon", "MORELY": "Morley", "BENTLY WITH ARKSEY": "Bentley", "LEISTON CUM-SIZEWELL": "Leiston",
       "WEYMOUTH AND MELCOMBE REGIS": "Weymouth", "LONDON": "City of London", "WESTMINSTER": "City of Westminster", "CHEPPING WYCOMBE": "High Wycombe",
       "BRIDGE BLEAN": "Bridge", "HAVANT AND WATERLOO": "Havant", "BROADSTAIRS AND ST. PETERS": "Broadstairs", "BEDDINGTON AND WALLINGTON": "Wallington",
       "HESTON AND ISLEWORTH": "Isleworth", "SWINTON AND PENDLEBURY": "Swinton", "MERTON AND MORDEN": "Morden", "MALDEN AND COOMBE": "New Malden",
       "BRENTFORD AND CHISWICK": "Chiswick", "WANSTEAD AND WOODFORD": "Woodford", "SUTTON AND CHEAM": "Sutton", "HAYES AND HARLINGTON": "Hayes",
       "RUISLIP AND NORTHWOOD": "Ruislip", "EPSOM AND EWELL": "Epsom", "COULSDON AND PURLEY": "Purley", "CHISLEHURST AND SIDCUP": "Sidcup",
       "CATERHAM AND WARLINGHAM": "Caterham", "WALTON AND WEYBRIDGE": "Walton-on-Thames", "BEESTON AND STAPLEFORD": "Beeston",
       "CAMBORNE AND REDRUTH": "Camborne", "SITTINGBOURNE AND MILTON": "Sittingbourne", "SANDOWN AND SHANKLIN": "Shanklin",
       "MABLETHORPE AND SUTTON": "Mablethorpe", "BRAINTREE AND BOCKING": "Braintree", "FRINTON AND WALTON": "Frinton-on-Sea",
       "WHITLEY AND MONKSEATON": "Whitley Bay", "SALTBURN AND MASKE-BY-THE-SEA": "Saltburn-by-the-Sea", "SKELTON AND BROTTON": "Skelton",
       "BUCKHAVEN AND METHIL": "Methil", "HUYTON-WITH-ROBY": "Huyton", "THORNTON CLEVELEYS": "Cleveleys", "LYTHAM ST. ANNES": "Lytham St Anne's",
       "MORECAMBE AND HEYSHAM": "Morecambe", "DORKING AND HORLEY": "Dorking", "BORDER": "Brampton", "FRIMLEY AND CAMBERLEY": "Camberley",
       "BURNHAM ON CROUCH": "Burnham-on-Crouch", "SHOREHAM BY SEA": "Shoreham-by-Sea", "NEWBIGGIN BY THE SEA": "Newbiggin-by-the-Sea",
       "WALTON-LE-DALE": "Walton-le-Dale", "ST. HELENS": "St Helens", "ST. ALBANS": "St Albans", "ST. IVES": "St Ives", "ST. AUSTELL": "St Austell",
       "ST. NEOTS": "St Neots", "ST. ANDREWS": "St Andrews", "ST. JUST": "St Just", "ST. MARYLEBONE": "Marylebone", "ST. PANCRAS": "St Pancras",
       "ST. GERMANS": "St Germans", "BURY ST. EDMUNDS": "Bury St Edmunds", "HEDON": "Hedon", "BANGOR CITY": "Bangor", "LLWCHWR": "Gorseinon",
       "MYNYDDISLWYN": "Blackwood", "THURROCK": "Grays", "SEATON VALLEY": "Seaton Delaval", "BLOFIELD AND FLEGG": "Blofield", "LOTHINGLAND": "Gorleston-on-Sea",
       "DEPWADE": "Long Stratton", "SMALLBURGH": "Smallburgh", "ERPINGHAM": "Aylsham", "ST. FAITH'S AND AYLSHAM": "Aylsham", "FOREHOE AND HENSTEAD": "Wymondham",
       "MITFORD AND LAUNDITCH": "Dereham", "FREEBRIDGE LYNN": "King's Lynn", "LODDON": "Loddon", "DEBEN": "Woodbridge", "SAMFORD": "Holbrook",
       "COSFORD": "Hadleigh", "GIPPING": "Needham Market", "HARTISMERE": "Eye", "THEDWASTRE": "Thurston", "THINGOE": "Bury St Edmunds",
       "MELFORD": "Long Melford", "CLARE": "Clare", "PLYMPTON ST. MARY": "Plympton", "ST. THOMAS": "Exeter", "OSGOLDCROSS": "Pontefract",
       "BATHAVON": "Bath", "LONG ASHTON": "Long Ashton", "SODBURY": "Chipping Sodbury", "THORNBURY": "Thornbury", "AXBRIDGE": "Axbridge",
       "CLUTTON": "Clutton", "LANGPORT": "Langport", "WINCANTON": "Wincanton", "WILLITON": "Williton", "SWALE": "Faversham", "EASTRY": "Eastry",
       "ELHAM": "Elham", "MALLING": "West Malling", "STROOD": "Strood", "HOLLINGBOURNE": "Hollingbourne", "CHANCTONBURY": "Steyning",
       "CHAILEY": "Chailey", "HAILSHAM": "Hailsham", "UCKFIELD": "Uckfield", "CUCKFIELD": "Cuckfield", "PETWORTH": "Petworth", "WEST DEAN": "West Dean",
       "DROXFORD": "Droxford", "HAMBLEDON": "Hambledon", "GODSTONE": "Godstone", "BULLINGDON": "Wheatley", "PLOUGHLEY": "Bicester",
       "NORTH COTSWOLD": "Moreton-in-Marsh", "EAST KESTEVEN": "Sleaford", "NORTH KESTEVEN": "Sleaford", "WEST KESTEVEN": "Grantham",
       "GLANFORD BRIGG": "Brigg", "CASTLE WARD": "Ponteland", "WORTLEY": "Stocksbridge", "WHISTON": "Whiston", "BUCKLOW": "Knutsford",
       "BASFORD": "Bulwell", "SEISDON": "Wombourne", "MERIDEN": "Meriden", "LUNESDALE": "Kirkby Lonsdale", "FYLDE": "Kirkham",
       "TOTTINGTON": "Tottington", "NIDDERDALE": "Pateley Bridge", "MASHAM": "Masham", "FLAXTON": "Flaxton", "HOLDERNESS": "Hedon",
       "HALTEMPRICE": "Cottingham", "WELTON": "Welton", "SOUTH WESTMORLAND": "Kendal", "MILLOM": "Millom", "SOUTH CAMBRIDGESHIRE": "Cambridge",
       "CHESTERTON": "Chesterton", "EASTHAMPSTEAD": "Crowthorne", "WEST LANCASHIRE": "Ormskirk", "CEIRIOG": "Glyn Ceiriog", "GWYRFAI": "Caernarfon",
       "VALLEY": "Valley", "GOWER": "Gower", "WEST PENWITH": "Penzance", "KERRIER": "Helston", "WEST ASHFORD": "Ashford", "EAST ASHFORD": "Ashford",
       "MAGOR AND ST. MELLONS": "Magor", "CALNE AND CHIPPENHAM": "Chippenham", "CRICKLADE AND WOOTON BASSETT": "Royal Wootton Bassett",
       "RINGWOOD AND FORDINGBRIDGE": "Ringwood", "ROMSEY AND STOCKBRIDGE": "Romsey", "KINGSCLERE AND WHITCHURCH": "Kingsclere",
       "WAREHAM AND PURBECK": "Wareham", "WARMINSTER AND WESTBURY": "Warminster", "WIMBORNE AND CRANBORNE": "Wimborne Minster",
       "OUNDLE AND THRAPSTON": "Oundle", "MELTON AND BELVOIR": "Melton Mowbray", "ROSS AND WHITCHURCH": "Ross-on-Wye", "ROSS ON WYE": "Ross-on-Wye",
       "DOWNHAM": "Downham Market", "WING": "Wing", "WEM": "Wem", "DRAYTON": "Market Drayton", "WELLINGTON": "Wellington", "ISLE OF WIGHT": "Newport",
       "ISLES OF SCILLY": "Hugh Town", "NEW FOREST": "Lyndhurst", "SPILSBY": "Spilsby", "CAISTOR": "Caistor", "STOKESLEY": "Stokesley",
       "EASINGTON": "Easington", "BLACKWELL": "Blackwell", "DERWENT": "Derwent", "LEISTON": "Leiston", "TUTBURY": "Tutbury", "REPTON": "Repton",
       "SHARDLOW": "Shardlow", "HIGHWORTH": "Highworth", "WEST BRIDGFORD": "West Bridgford", "WEST MERSEA": "West Mersea", "TENDRING": "Tendring",
       "LEXDEN AND WINSTREE": "Colchester", "WALTHAM HOLY CROSS": "Waltham Abbey", "BOLDON": "East Boldon", "BENFLEET": "South Benfleet",
       "CANVEY ISLAND": "Canvey Island", "WELWYN GARDEN CITY": "Welwyn Garden City", "LONGBENTON": "Longbenton", "YORK": "York",
       "RICHMOND": "Richmond upon Thames", "STAINES": "Staines-upon-Thames", "WEST HARTLEPOOL": "Hartlepool", "LEAMINGTON": "Royal Leamington Spa",
       "TUNBRIDGE WELLS": "Royal Tunbridge Wells", "BEXHILL": "Bexhill-on-Sea", "CLACTON": "Clacton-on-Sea", "DUNMOW": "Great Dunmow",
       "LONDONDERRY": "Derry", "WANSTEAD AND WOODFORD": "Wanstead", "PORTLAND": "Fortuneswell"}
COUNTY_HINT = {"HYTHE": "Kent", "CRANBROOK": "Kent"}   # same-name places elsewhere
MONMOUTHSHIRE = {"NEWPORT, COUNTY BOROUGH", "PONTYPOOL, URBAN DISTRICT", "RISCA, URBAN DISTRICT", "CWMBRAN, URBAN DISTRICT", "MYNYDDISLWYN, URBAN DISTRICT",
                 "CHEPSTOW, RURAL DISTRICT", "MAGOR AND ST. MELLONS, RURAL DISTRICT"}
SCOT_COUNTY = re.compile(r"^(.*) COUNTY$")
NATION_SUFFIX = {"SCOTLAND": "Scotland", "WALES": "Wales", "N. IRELAND": "Northern Ireland"}
LONDON_COUNTY_EXTRA = {"LONDON CITY", "WESTMINSTER CITY"}

PERIODS = [  # (key, label, start, end inclusive) dates from Wikipedia: The Blitz, Baedeker Blitz, Operation Steinbock, V-1 flying bomb, V-2 rocket
    ("early", "Before the Blitz", "1939-09-03", "1940-09-06"),
    ("blitz", "The Blitz", "1940-09-07", "1941-05-16"),
    ("mid", "Baedeker and tip-and-run years", "1941-05-17", "1944-01-20"),
    ("baby", "The Baby Blitz", "1944-01-21", "1944-06-12"),
    ("vweap", "Flying bombs and rockets", "1944-06-13", "1945-03-29"),
    ("after", "After the last attacks", "1945-03-30", "1947-12-31"),
]
AGE_BANDS = [("0 or not stated", 0, 0), ("1 to 4", 1, 4), ("5 to 15", 5, 15), ("16 to 29", 16, 29), ("30 to 44", 30, 44), ("45 to 59", 45, 59),
             ("60 to 74", 60, 74), ("75 and over", 75, 200)]


def period(d):
    s = d.isoformat()
    for k, _, a, b in PERIODS:
        if a <= s <= b: return k
    return "after"


def classify(c):
    """Return (scope, base name, kind, nation)."""
    if SEA.match(c): return "sea", c, "ship or air crash at sea", ""
    if c in CROWN: return "crown", c, "Crown dependency", ""
    parts = [p.strip() for p in c.split(",")]
    nation = "England"
    if parts[-1] in NATION_SUFFIX: nation = NATION_SUFFIX[parts.pop()]
    if c in MONMOUTHSHIRE: nation = "Wales"   # Monmouthshire rolls carry no ", WALES" suffix
    if parts[-1] in ("YORKSHIRE", "MIDDLESEX", "CUMBERLAND"): parts.pop()
    if c in LONDON_COUNTY_EXTRA: return "uk", parts[0].replace(" CITY", ""), "City", "England"
    kind = ", ".join(parts[1:])
    m = SCOT_COUNTY.match(parts[0])
    if nation == "Scotland" and m and not kind: return "uk", m.group(1), "county", nation
    if parts[0].endswith(" CITY") and nation == "Scotland": return "uk", parts[0][:-5], "city", nation
    if kind and any(kind.startswith(k) or k in kind for k in KINDS): return "uk", parts[0], kind.lower(), nation
    if "RURAL DISTRICT" in parts[0]: return "uk", parts[0].replace(" RURAL DISTRICT", ""), "rural district", nation
    return "overseas", c, "overseas", ""


def ni_lookup():
    d = json.load(open(WD8))
    out = {}
    for l in d["wd_settlements_pop_tsv"].split("\n")[1:]:
        if not l: continue
        it, lab, cls, co, pop = l.split("\t")
        m = re.match(r"POINT\(([-\d.]+) ([-\d.]+)\)", co)
        if not m: continue
        lon, lat = float(m.group(1)), float(m.group(2))
        if 54.0 < lat < 55.35 and -8.2 < lon < -5.4:
            n = norm(lab.split('"')[1]); out.setdefault(n, (lat, lon, "Wikidata " + it.strip("<>").split("/")[-1]))
    return out


def geocode(base, kind, nation, ni):
    raw = FIX.get(base, base)
    name = raw.title() if raw.isupper() else raw
    if nation == "Northern Ireland":
        h = ni.get(norm(name))
        return (h[0], h[1], h[2], "") if h else None
    if kind == "county": return None   # Scottish counties: too large to place at a point
    country = "England" if nation == "England" else nation
    reg = "London" if kind.startswith("metropolitan") or base in ("LONDON", "WESTMINSTER") or kind.startswith("city") and base == "WESTMINSTER" else None
    for cand in (name, name.split(" And ")[0], name.replace("-", " ")):
        p = place(cand, country=country, region=reg)
        if p and base in COUNTY_HINT:
            p = next((x for x in gazetteer().get(norm(cand), []) if x[4] == COUNTY_HINT[base]), None)
        if p: return (p[1], p[2], "OS Open Names: " + cand, p[5])
    return None


if __name__ == "__main__":
    J = json.load(gzip.open(CWGC))
    rows = list(csv.DictReader(io.StringIO(J["csv"])))
    ids = set(); people = []
    for r in rows:
        if r["Id"] in ids: continue
        ids.add(r["Id"])
        d = dt.datetime.strptime(r["DateOfDeath"], "%d/%m/%Y").date()
        try: age = int(r["AgeAtDeath"])
        except ValueError: age = 0
        people.append((r["Cemetery"].strip(), d, age))
    del rows, J
    ni = ni_lookup()
    areas = {}
    for c in sorted(set(p[0] for p in people)):
        scope, base, kind, nation = classify(c)
        g = geocode(base, kind, nation, ni) if scope == "uk" else None
        county_of_london = scope == "uk" and (kind.startswith("metropolitan") or c in LONDON_COUNTY_EXTRA)
        greater_london = county_of_london or (g is not None and g[3] == "London")
        areas[c] = dict(area=c, scope=scope, name=base.title().replace("'S", "'s").replace(" And ", " and ").replace(" Upon ", " upon ").replace("-Upon-", " upon ").replace(" On ", " on ").replace(" Of ", " of "),
                        kind=kind, nation=nation, county_of_london=int(county_of_london), greater_london=int(greater_london),
                        lat=round(g[0], 4) if g else "", lon=round(g[1], 4) if g else "", geocode=g[2] if g else "")
    # aggregates
    tot = collections.Counter(); daily = collections.Counter(); daily_lon = collections.Counter(); daily_col = collections.Counter()
    by_area_day = collections.Counter(); by_area_month = collections.Counter(); age_all = collections.Counter(); age_area = collections.defaultdict(collections.Counter)
    per_area_period = collections.defaultdict(collections.Counter); ages_known = collections.defaultdict(list)
    for c, d, age in people:
        a = areas[c]; tot[c] += 1
        band = next(b[0] for b in AGE_BANDS if b[1] <= age <= b[2])
        age_area[c][band] += 1
        per_area_period[c][period(d)] += 1
        if age > 0: ages_known[c].append(age)
        if a["scope"] == "uk":
            daily[d] += 1; age_all[band] += 1
            if a["greater_london"]: daily_lon[d] += 1
            if a["county_of_london"]: daily_col[d] += 1
            by_area_day[(c, d)] += 1
            by_area_month[(c, d.strftime("%Y-%m"))] += 1
    out = []
    for c, a in areas.items():
        days = {d: n for (cc, d), n in by_area_day.items() if cc == c}
        pk = max(days.items(), key=lambda x: (x[1], -x[0].toordinal())) if days else (None, 0)
        ak = ages_known[c]
        rec = dict(a, deaths=tot[c], first=min(days).isoformat() if days else "", last=max(days).isoformat() if days else "",
                   peak_day=pk[0].isoformat() if pk[0] else "", peak_deaths=pk[1],
                   **{"p_" + k: per_area_period[c][k] for k, *_ in PERIODS},
                   age_stated=len(ak), under16=sum(1 for x in ak if x < 16), over60=sum(1 for x in ak if x >= 60),
                   median_age=statistics.median(ak) if ak else "")
        out.append(rec)
    out.sort(key=lambda r: -r["deaths"])
    for i, r in enumerate(out): r["aid"] = i
    with open(os.path.join(DATA, "ww2_areas.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["aid"] + [k for k in out[0] if k != "aid"]); w.writeheader(); w.writerows(out)
    aid = {r["area"]: r["aid"] for r in out}
    d0, d1 = dt.date(1939, 9, 3), max(p[1] for p in people)
    with open(os.path.join(DATA, "ww2_daily.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["date", "uk_deaths", "greater_london", "county_of_london"])
        x = d0
        while x <= d1:
            w.writerow([x.isoformat(), daily[x], daily_lon[x], daily_col[x]]); x += dt.timedelta(days=1)
    with open(os.path.join(DATA, "ww2_area_month.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["aid", "area", "month", "deaths"])
        for (c, m), n in sorted(by_area_month.items(), key=lambda x: (aid[x[0][0]], x[0][1])): w.writerow([aid[c], c, m, n])
    with open(os.path.join(DATA, "ww2_age.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["age_band", "uk_deaths"])
        for b, *_ in AGE_BANDS: w.writerow([b, age_all[b]])
    # area-day table for worst days (aggregates only)
    with open(os.path.join(WORK, "area_day.json"), "w") as f:
        json.dump([[aid[c], d.isoformat(), n] for (c, d), n in by_area_day.items() if n >= 5], f)
    uk = [r for r in out if r["scope"] == "uk"]
    print("people", len(people), "areas", len(out), "uk", sum(r["deaths"] for r in uk),
          "placed", sum(r["deaths"] for r in uk if r["lat"] != ""), "unplaced areas", [(r["area"], r["deaths"]) for r in uk if r["lat"] == "" and r["deaths"] >= 10])
    json.dump(dict(n_rows=len(people), retrieved=json.load(gzip.open(CWGC))["retrieved"], log=json.load(gzip.open(CWGC))["log"], periods=PERIODS,
                   age_bands=[b[0] for b in AGE_BANDS], last_date=d1.isoformat()), open(os.path.join(WORK, "ww2.json"), "w"))
