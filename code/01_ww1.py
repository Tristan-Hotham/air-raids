"""Step 1. First World War: the deadliest air raids and naval bombardments on Britain, 1914 to 1918.

There is no open, place-by-place list of First World War air raid deaths, so this is a hand-built table of the
incidents whose death tolls are stated in English Wikipedia (CC BY-SA 4.0) and, for three figures not given there,
in named web pages. Every Wikipedia figure is checked: the quoted sentence must appear in the article text on disk,
or the script stops. Each incident is placed at one representative OS Open Names settlement.
Writes data/ww1_incidents.csv and work/ww1.json.
Run: python3 code/01_ww1.py
"""
import csv, json, os
from common import DATA, WORK, place, wiki_has, wurl, nodash, dash

A = "German bombing of Britain, 1914–1918"
S = "Raid on Scarborough, Hartlepool and Whitby"
T = "Timeline of the United Kingdom home front during the First World War"
EH = "https://www.english-heritage.org.uk/visit/places/scarborough-castle/history/shelling-of-scarborough"
ITV = "https://itv.com/news/calendar/story/2014-12-16/100th-anniversary-of-wwi-bombardments"
IC = "https://iancastlezeppelin.co.uk/6/7-jun-1915"

# id, date, kind, label, map place (OS Open Names), London?, killed, injured, who, note, source, quote
ROWS = [
    ("1914hart", "1914-12-16", "naval", "Hartlepool and West Hartlepool", "Hartlepool", 0, 86, 424, "civilians",
     "Shelled by the battlecruisers Seydlitz, Moltke and Blücher. Seven soldiers were also killed. Arthur Marder (1965) gave 122 killed.", S,
     "86 civilians were killed and 424 injured"),
    ("1914scar", "1914-12-16", "naval", "Scarborough", "Scarborough", 0, 19, None, "people",
     "Shelled by Derfflinger and Von der Tann: 17 killed that morning and two who died later of their wounds (English Heritage). ITV News gives 18.", EH,
     "In total, 17 people were killed in Scarborough that morning, with two others dying later of their wounds."),
    ("1914whit", "1914-12-16", "naval", "Whitby", "Whitby", 0, 2, None, "people",
     "The same two ships then shelled the coastguard station, also hitting Whitby Abbey. Figure implied by ITV News (20 killed in the two towns, 18 in Scarborough); uncertain.", ITV,
     "20 people were killed"),
    ("1915yarm", "1915-01-19", "airship", "Great Yarmouth, Sheringham and King's Lynn", "Great Yarmouth", 0, 4, 16, "civilians",
     "The first air raid deaths in Britain: Zeppelins L 3 and L 4, aiming for the Humber, were blown south to the Norfolk coast.", T,
     "four civilians are killed and sixteen injured"),
    ("1915lz38", "1915-05-26", "airship", "Ipswich, Southend, Dover and Ramsgate (four raids by LZ 38)", "Southend-on-Sea", 0, 6, 6, "people",
     "Four raids between 29 April and 27 May 1915; three of the deaths were at Southend on 26/27 May.", A,
     "These four raids killed six people and injured six"),
    ("1915lon1", "1915-05-31", "airship", "Stoke Newington, Shoreditch and Stepney: the first London raid", "Stepney", 1, 7, 35, "people",
     "LZ 38 dropped about 120 small bombs on a line from Stoke Newington to Stepney and Leytonstone.", A,
     "Seven people were killed and 35 injured"),
    ("1915hull", "1915-06-06", "airship", "Hull", "Kingston upon Hull", 0, 26, 40, "people",
     "L 9, sent against London, bombed Hull instead (figure from Ian Castle's raid record; not stated in the Wikipedia article).", IC,
     "Other bombs took the total fatalities up to 26 with 40 injured."),
    ("1915walt", "1915-08-17", "airship", "Walthamstow and Leytonstone", "Leytonstone", 1, 10, 48, "people",
     "L 10, the first Navy airship to reach London, mistook the Lea Valley reservoirs for the Thames.", A,
     "Ten people were killed, 48 injured"),
    ("1915sel", "1915-09-07", "airship", "Deptford, Greenwich, Bermondsey and New Cross", "Bermondsey", 1, 18, 28, "people",
     "Two Army airships, SL 2 and LZ 74.", A, "Eighteen people were killed and 28 injured"),
    ("1915dere", "1915-09-08", "airship", "East Dereham", "Dereham", 0, 4, 7, "people",
     "L 14, apparently aiming for Norwich.", A, "four men were killed at East Dereham"),
    ("1915city", "1915-09-08", "airship", "Bartholomew Close, the City and Liverpool Street", "City of London", 1, 22, 87, "people",
     "L 13 under Heinrich Mathy. Its fire in the textile warehouses north of St Paul's caused over half a million pounds of damage.", A,
     "The raid killed 22 people and injured 87"),
    ("1915thea", "1915-10-13", "airship", "The Theatreland raid: the Strand, Holborn, Aldgate, and camps and towns in Kent and Surrey", "Covent Garden", 1, 71, 128, "people",
     "The first bombs struck by the Lyceum Theatre, killing 17. The total includes 14 soldiers killed at Otterpool Army Camp near Folkestone.", A,
     "In total, 71 people were killed and 128 were injured."),
    ("1916blac", "1916-01-31", "airship", "Tipton, Wednesbury and Walsall", "Tipton", 0, 61, 101, "people",
     "Nine Zeppelins sent to Liverpool wandered over the Black Country in fog. Fifteen died in Tipton (14 in the Tipton raid article).", A,
     "61 people were reported killed and 101 injured"),
    ("1916hull", "1916-03-05", "airship", "Hull", "Kingston upon Hull", 0, 18, 52, "people",
     "Three Zeppelins sent against Rosyth were diverted by high winds.", A, "killing 18 people, injuring 52"),
    ("1916clee", "1916-03-31", "airship", "Cleethorpes and eastern England", "Cleethorpes", 0, 48, None, "mostly soldiers",
     "Most of the dead were soldiers, killed by a bomb on an Army billet in Cleethorpes.", A,
     "Most of the 48 people killed in the raid were victims of a bomb which fell on an Army billet in Cleethorpes"),
    ("1916north", "1916-04-01", "airship", "Targets in the north of England", None, 0, 22, 130, "people",
     "Two Navy Zeppelins diverted from London by the weather. The article does not name the towns, so this raid is not on the map.", A,
     "killing 22 people and injuring 130"),
    ("1916leith", "1916-04-02", "airship", "Leith and Edinburgh", "Leith", 0, 13, 24, "people",
     "Aimed at Rosyth and the Forth Bridge; much of the damage came from a burning whisky warehouse in Leith.", A,
     "13 people were killed, 24 injured"),
    ("1916dilh", "1916-04-24", "airship", "Dilham, Norfolk", "Dilham", 0, 1, None, "civilian",
     "An elderly woman died of fright after 45 bombs fell close to her home, the night before the Lowestoft bombardment.",
     "Bombardment of Yarmouth and Lowestoft", "an elderly woman died of fright"),
    ("1916lowe", "1916-04-25", "naval", "Lowestoft and Great Yarmouth", "Lowestoft", 0, 3, 19, "civilians",
     "Four battlecruisers fired on Lowestoft for ten minutes, destroying 200 houses. A serviceman was also killed.",
     "Bombardment of Yarmouth and Lowestoft", "A serviceman and three civilians were killed and 19 were wounded at Lowestoft"),
    ("1916lon", "1916-08-24", "airship", "Deptford, Greenwich, Eltham and Plumstead", "Deptford", 1, 9, 40, "people",
     "L 31 dropped 36 bombs in ten minutes.", A, "Nine people were killed, 40 injured"),
    ("1916stre", "1916-09-23", "airship", "Streatham and Brixton", "Streatham", 1, 7, 27, "people",
     "L 31 again; the same night L 32 was shot down in flames at Great Burstead with all 22 crew.", A, "killing seven people and wounding 27"),
    ("1916leyt", "1916-09-23", "airship", "Leyton", "Leyton", 1, 8, 30, "people", "L 31 crossed the river and dropped 10 bombs on Leyton.", A,
     "killing another eight people and injuring 30"),
    ("1916scar", "1916-09-25", "naval", "Scarborough (shelled by a U-boat)", "Scarborough", 0, 3, 5, "people",
     "A second attack on Scarborough from the sea, by a submarine.", "Scarborough, North Yorkshire", "saw three people killed and a further five injured"),
    ("1916nov", "1916-11-27", "airship", "The Midlands and Tyneside", None, 0, 4, 37, "people",
     "L 34 was shot down in flames off Hartlepool the same night. Towns not named, so not on the map.", A, "killed four people, injured 37"),
    ("1917folk", "1917-05-25", "aeroplane", "Folkestone: Tontine Street", "Folkestone", 0, 72, None, "71 civilians and a soldier",
     "The first Gotha raid. Cloud over London turned the bombers to Folkestone, where Tontine Street was full of shoppers: fifteen men, 31 women and 25 children were among the dead.", A,
     "At Folkestone a soldier and fifteen men, 31 women and 25 children were killed"),
    ("1917shor", "1917-05-25", "aeroplane", "Shorncliffe Army Camp and Cheriton", "Cheriton", 0, 17, 93, "soldiers",
     "Canadian soldiers in camp, the same raid. The raid's total was 95 killed and 195 injured.", A, "17 Canadian soldiers were killed and 93 wounded"),
    ("1917jun", "1917-06-13", "aeroplane", "The City, the East End and Poplar: the first daylight raid on London", "Poplar", 1, 162, 432, "people",
     "The deadliest air raid of the war. A bomb on Upper North Street School in Poplar killed 18 children. The home front timeline gives 104 civilians killed.", A,
     "The raid caused 162 deaths and 432 injuries."),
    ("1917jul", "1917-07-07", "aeroplane", "London", "City of London", 1, 57, 193, "people", "A second daylight raid by 22 Gothas.", A,
     "resulting in 57 deaths and 193 injuries on the ground"),
    ("1917chat", "1917-09-03", "aeroplane", "Chatham: the naval drill hall", "Chatham", 0, 130, 88, "sailors",
     "The first night raid by Gothas. Two bombs hit a drill hall used as a barracks: the worst single death toll of the war, but these were naval ratings, not civilians.", A,
     "The explosions killed 130 sailors and wounded another 88"),
    ("1917sep", "1917-09-29", "aeroplane", "London", "City of London", 1, 40, 87, "people",
     "Up to 300,000 Londoners were now sheltering in Underground stations.", A, "killing 40 people and injuring 87"),
    ("1918jan", "1918-01-28", "aeroplane", "Long Acre (Odhams printing works) and London", "Covent Garden", 1, 67, 166, "people",
     "A bomb hit the Odhams works, used as a shelter; 14 died in crushes at shelter entrances when maroons were mistaken for bombs.", A,
     "The bombing killed 67 people and injured 166"),
    ("1918isle", "1918-01-29", "aeroplane", "Isleworth, Kew and Brentford", "Isleworth", 1, 10, 10, "people", "A Giant bomber, turned west by a night fighter.", A,
     "killing ten people and wounding ten"),
    ("1918panc", "1918-02-17", "aeroplane", "St Pancras station", "St Pancras", 1, 21, 32, "people", "A single Giant bomber.", A,
     "21 people were killed and 32 injured"),
    ("1918hart", "1918-03-13", "airship", "Hartlepool", "Hartlepool", 0, 8, None, "people", "Hartlepool's second ordeal: one Zeppelin reached England.", A,
     "The bombs killed eight people"),
    ("1918apr", "1918-04-12", "airship", "The Midlands", None, 0, 7, 20, "people", "Most bombs fell in open country; towns not named, so not on the map.", A,
     "Seven people were killed, 20 injured"),
    ("1918may", "1918-05-19", "aeroplane", "London and Essex: the Whitsun raid", "City of London", 1, 49, 177, "people",
     "The last and largest aeroplane raid of the war: 38 Gothas and 3 Giants. Six Gothas were shot down.", A, "49 people were killed, 177 injured"),
]

REG = {'Hartlepool': 'North East', 'Scarborough': 'Yorkshire and the Humber', 'Whitby': 'Yorkshire and the Humber', 'Great Yarmouth': 'Eastern', 'Southend-on-Sea': 'Eastern', 'Kingston upon Hull': 'Yorkshire and the Humber', 'Dereham': 'Eastern', 'Tipton': 'West Midlands', 'Cleethorpes': 'Yorkshire and the Humber', 'Leith': 'Scotland', 'Dilham': 'Eastern', 'Lowestoft': 'Eastern', 'Folkestone': 'South East', 'Cheriton': 'South East', 'Chatham': 'South East'}

TOTALS = dict(
    airship=(557, 1358, A, "Airships made 51 bombing raids on Britain during the war in which 557 people were killed and 1,358 injured."),
    aeroplane=(857, 2058, A, "killing 857 people, injuring 2,058"),
    london_mpd=(668, 1938, T, "The total number of civilian casualties from air raids since 1915 within London's Metropolitan Police District was 668 killed and 1,938 injured."),
    dec1914=(137, 592, T, "resulting in 137 deaths and 592 casualties, most of whom are civilians"),
)

if __name__ == "__main__":
    out, miss = [], []
    for (i, d, k, lab, geo, lon_, kil, inj, who, note, src, q) in ROWS:
        if src.startswith("http"): url = src; srcname = {EH: "English Heritage, The shelling of Scarborough", ITV: "ITV News Calendar, 16 December 2014", IC: "Ian Castle, Zeppelin raid record, 6/7 June 1915"}[src]; checked = "web page, read 28 Oct 2026"
        else:
            assert wiki_has(src, q), (i, q); url = wurl(src); srcname = "Wikipedia, " + dash(src); checked = "quote found in article text"
        p = place(geo.replace("Covent Garden", "Strand"), region="London" if lon_ else REG.get(geo)) if geo else None
        if geo and not p: miss.append(geo)
        out.append(dict(id=i, date=d, attack=k, places=lab, map_place=geo or "", london=lon_, killed=kil, injured=inj if inj is not None else "",
                        who=who, note=note, lat=round(p[1], 4) if p else "", lon=round(p[2], 4) if p else "", source=srcname, url=url, quote=q, check=checked))
        for s in (lab, note, who): assert nodash(s), s
    assert not miss, miss
    for k, (a, b, src, q) in TOTALS.items(): assert wiki_has(src, q), (k, q)
    with open(os.path.join(DATA, "ww1_incidents.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    json.dump(dict(rows=out, totals={k: dict(killed=v[0], injured=v[1], source=wurl(v[2]), quote=v[3]) for k, v in TOTALS.items()}),
              open(os.path.join(WORK, "ww1.json"), "w"), indent=1, ensure_ascii=False)
    print(len(out), "incidents;", sum(r["killed"] for r in out), "killed listed")
