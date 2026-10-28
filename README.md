# Bombs on Britain: where the air raids killed, 1914 to 1945

Where did the air raids on Britain kill civilians, and how did London's share change? Every civilian on the Commonwealth War Graves Commission's Second World War roll, counted town by town and day by day, with the First World War raids and bombardments that came first.

**Interactive version:** https://tristan-hotham.github.io/air-raids/

**Paper and archived release:** https://doi.org/10.5281/zenodo.23729652

A data study by Dr Tristan Hotham (Independent researcher), published for Remembrance 2026. It pairs with [How many names on your war memorial?](https://tristan-hotham.github.io/war-memorials/) (https://doi.org/10.5281/zenodo.23727151).

## Headline results

- The CWGC Civilian War Dead roll (exported 28 October 2026) holds 67,779 people; 61,542 are filed under places in the United Kingdom.
- 29,983 (49%) are in Greater London and 31,559 (51%) elsewhere; 51 civic areas outside London have 100 or more dead.
- London's share swings with the war: 48% of the 39,222 dead of the Blitz (7 September 1940 to 16 May 1941), 12% between May 1941 and January 1944 (the Baedeker and tip-and-run years), 87% of the 9,479 dead of the V-1 and V-2 campaign.
- The worst day on the roll is 16 April 1941 (1,580 dead: 789 in London, 791 elsewhere, mostly Belfast). The worst days for any single place were all outside London: Liverpool 669 on 3 May 1941, Belfast 565 on 16 April 1941, Coventry 417 on 14 November 1940.
- Approximate deaths per 1,000 people: Coventry 5.7, Plymouth 5.1, County of London 4.8.
- 13% of the dead with a stated age were children under 16.
- First World War: airships killed 557 and aeroplanes 857 (1,414 in all), 668 (47%) of them in the London police district; the naval bombardment of Hartlepool, Scarborough and Whitby on 16 December 1914 killed 137. Hartlepool lost 94 people in 1914 and 1918, more than the 76 on its two Second World War rolls.
- The roll agrees within 10% with the city totals quoted in Wikipedia in 13 of 18 cases.

Every number is in `data/results.json`, which the page, paper, blog and collage are built from.

## Files

| Path | What it is |
| - | - |
| `index.html` | The interactive page (map with a month-by-month slider for both wars, charts, tables, story cards, search). All data embedded. |
| `header.png` | Social card (1200 by 630). |
| `data/ww2_areas.csv` | One row per civic area on the CWGC roll (1,140): scope (UK, sea, Crown dependency, overseas), name, kind, nation, London flags, placed coordinates and their source, total dead, first, last and worst day, dead in each period, ages (counts only). |
| `data/ww2_daily.csv` | UK civilian dead per day, 3 September 1939 to 27 December 1947, with Greater London and County of London. |
| `data/ww2_area_month.csv` | Dead per civic area per month. |
| `data/ww2_age.csv` | UK dead by age band. |
| `data/ww1_incidents.csv` | 36 First World War raids and bombardments: date, attack, places, killed, injured, who, notes, map coordinates, source, URL and the quoted sentence. |
| `data/populations.csv` | Populations used for the rates and their sources. |
| `data/wikipedia_compare.csv` | The roll against the totals quoted in 18 Wikipedia city articles. |
| `data/stories.csv` | Roll counts on the dates of named incidents, with the Wikipedia sentence. |
| `data/results.json` | Every number used anywhere. |
| `data/coast_ne10m.json` | Natural Earth 1:10m land (public domain), for the header and figures. |
| `code/common.py` | Paths, the Wikipedia reader and quote checker, the OS Open Names gazetteer. |
| `code/01_ww1.py` | Builds the First World War incident table, checking every quoted sentence. |
| `code/02_cwgc.py` | Reads the CWGC export, sorts and places the civic areas, writes only aggregates. |
| `code/03_analyse.py` | All statistics; writes `results.json` and the page data. |
| `code/04_build_site.py` | Fills `code/page_template.html` to make `index.html`. |
| `code/05_header.py` | Renders `header.png` with Playwright. |
| `code/06_figures.py` | Static figures for the paper and blog. |
| `code/07_paper.py` | Builds the paper PDF from `code/paper_template.tex` with xelatex. |
| `code/08_release.py` | Blog post, blog and Zenodo metadata, Zenodo folder. |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |
| `release/` | Paper PDF and source, blog post and figures, Zenodo files. |

## Method in brief

- **The roll.** CWGC Find War Dead, Civilian War Dead 1939 to 1945, exported month by month (day by day for months over the 1,000-row export cap). One day, 16 April 1941, passed the cap on its own and was collected again by age, so a few people of unknown age that day may be missing. Only civic area, date of death and age are used; no names, addresses or free text are kept or published.
- **Areas.** The 1,140 civic areas are sorted by their local government type into the United Kingdom (953), ships and air crashes at sea, the Channel Islands and Isle of Man, and overseas. Monmouthshire's rolls carry no Welsh suffix and are counted as Welsh.
- **Placing.** Each UK area is placed at a populated place of the same name in OS Open Names (Wikidata for Northern Ireland); where several share a name, the one with the largest Wikidata population within 8 km. Spelling fixes and the main towns of rural districts named after hundreds are listed in `code/02_cwgc.py`. Scottish county rolls are not placed. 99.5% of the UK dead are placed. Points mark namesake towns, not bomb sites.
- **Greater London.** The County of London (28 metropolitan boroughs, the City, Westminster) plus every area whose namesake lies in today's Greater London region.
- **Periods.** By date of death: before the Blitz (to 6 September 1940), the Blitz (7 September 1940 to 16 May 1941), to 20 January 1944, the Baby Blitz (to 12 June 1944), flying bombs and rockets (13 June 1944 to 29 March 1945), after.
- **Rates.** Approximate: the mean of the 1921 and 1951 census figures in Wikipedia's list of English towns by historical population; start-of-war figures for Plymouth and Hull from their blitz articles; four million for the County of London. Real wartime populations were lower, so true rates were higher.
- **First World War.** A hand-built table of incidents whose tolls are stated in Wikipedia, each quoted sentence checked against the downloaded article text, plus three web figures (English Heritage for Scarborough 1914, ITV News for Whitby, Ian Castle for Hull 1915). Some rows include soldiers and sailors and are flagged.

## Known limits

- The roll is filed by civic area and date, not by incident; the area may be where a person died or lived, and neighbouring areas may hold some of a town's dead (Clydebank's roll has 448 against the 1,200 in Wikipedia).
- Age 0 can mean an infant or an unknown age; it is kept apart.
- First World War figures differ between sources (13 June 1917: 162 deaths, or 104 civilians); totals are as Wikipedia gives them.
- The Hartlepool "monkey hanger" story on the page is presented as folklore, as Wikipedia describes it.

## How to rerun

Inputs are read from paths at the top of `code/common.py` (override with environment variables): `cwgc_civilians.json.gz` and the Wikipedia extracts in `DATA12`, OS Open Names (`OSNAMES`), the Wikipedia historical population list (`WIKI9`) and the Wikidata settlement populations (`WD8`).

```
python3 code/01_ww1.py
python3 code/02_cwgc.py
python3 code/03_analyse.py
python3 code/04_build_site.py
FONT_DIR=path/to/fonts python3 code/05_header.py
FONT_DIR=path/to/fonts python3 code/06_figures.py
python3 code/07_paper.py
python3 code/08_release.py
```

Needs Python 3 with numpy, matplotlib, Pillow and playwright, and xelatex with TeX Gyre Pagella and Inter for the paper.

## Sources and licences

- Second World War dead: Commonwealth War Graves Commission, Find War Dead (Civilian War Dead 1939-1945), https://www.cwgc.org, used for research with credit. Only aggregate counts are published.
- First World War raids, city totals, historical populations and the monkey legend: English Wikipedia (CC BY-SA 4.0), articles listed in `data/ww1_incidents.csv`, `data/wikipedia_compare.csv` and `data/populations.csv`; English Heritage, ITV News and iancastlezeppelin.co.uk for three figures (quoted, with links).
- Places: OS Open Names, contains OS data © Crown copyright and database right 2026 (Open Government Licence v3.0); Wikidata (CC0).
- Coastline: Natural Earth (public domain). Base map tiles © Esri.

Because the incident table and figures build on Wikipedia, the derived data (`data/`) and the text of the page and paper are released under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/). The code (`code/`) is released under the MIT licence (see `LICENSE`).

## Citation

Hotham, T. (2026) Bombs on Britain: Where the Air Raids Killed, 1914 to 1945. Civilian Deaths Town by Town from the CWGC Roll and the First World War Raids. Zenodo. https://doi.org/10.5281/zenodo.23729652

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
