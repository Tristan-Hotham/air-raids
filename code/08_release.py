"""Step 8. Blog post (release/blog/post.html from code/blog_template.html), blog and Zenodo meta files,
and the Zenodo folder (paper, key CSVs, results.json and a code-and-data zip).
Image placeholders {{IMG|file|alt|caption}} are left for the uploader (numbers inside them are filled).
Run: python3 code/08_release.py
"""
import importlib.util, json, os, re, shutil, zipfile

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
spec = importlib.util.spec_from_file_location("b", os.path.join(HERE, "04_build_site.py")); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
R = b.R
t = open(os.path.join(HERE, "blog_template.html")).read()
t = re.sub(r"\{\{(?!IMG\|)([^}|]+)(\|(\w+))?\}\}", b.sub, t)
assert "{{" not in t.replace("{{IMG|", "")
vis = re.sub(r"<!--.*?-->", "", t, flags=re.S)
for bad in ("—", "–", "--"): assert bad not in vis, bad
os.makedirs(os.path.join(ROOT, "release", "blog"), exist_ok=True)
open(os.path.join(ROOT, "release", "blog", "post.html"), "w").write(t)
for m in re.findall(r"\{\{IMG\|([^|]+)\|", t):
    assert os.path.exists(os.path.join(ROOT, "release", "blog", m)), m
meta = dict(
    title="Bombs on Britain: where the air raids killed",
    slug="air-raids",
    excerpt=(f"I counted all {R['cwgc']['uk']:,} civilians on the Commonwealth War Graves Commission's Second World War roll for the UK, town by town. "
             f"{round(R['london']['outside_share'] * 100)}% of them died outside London, and the story starts with the shelling of Hartlepool in 1914."),
    seo_description=f"Civilian air raid deaths town by town, 1914 to 1945: {R['cwgc']['uk']:,} on the CWGC roll, {round(R['london']['outside_share'] * 100)}% outside London.",
    tags=["air raids", "the Blitz", "Remembrance", "Second World War", "First World War", "Zeppelin", "maps", "data"],
    header_alt=(f"Title card reading 'Bombs on Britain' in black and fire orange on a pale stone background, beside a map of Britain and Northern Ireland with orange dots "
                f"sized by civilian dead and blue rings for First World War raids. Text: {R['cwgc']['uk']:,} civilians on the Second World War roll, "
                f"{round(R['london']['outside_share'] * 100)}% of them outside London, and {R['ww1']['air_killed']:,} killed by Zeppelins and Gothas in the First World War."))
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
for v in meta.values():
    for bad in ("—", "–", "--"): assert bad not in str(v)
json.dump(meta, open(os.path.join(ROOT, "release", "blog", "meta.json"), "w"), indent=2, ensure_ascii=False)

NAME = "Hotham_Bombs_on_Britain"
pt = open(os.path.join(ROOT, "release", "paper", NAME + ".tex")).read()
ab = pt.split("\\begin{center}\\textbf{Abstract}\\end{center}")[1].split("\\textbf{Keywords:}")[0].strip()
ab = ab.replace("\\%", "%").replace("\\&", "&").replace("``", "“").replace("''", "”")
Z = os.path.join(ROOT, "release", "zenodo"); os.makedirs(Z, exist_ok=True)
zmeta = dict(
    title="Bombs on Britain: Where the Air Raids Killed, 1914 to 1945. Civilian Deaths Town by Town from the CWGC Roll and the First World War Raids",
    description_html=f"<p>{ab}</p><p>Interactive version: https://tristan-hotham.github.io/air-raids/. Data and code: https://github.com/Tristan-Hotham/air-raids. Blog post: to follow.</p>",
    keywords=["air raids", "the Blitz", "civilian war dead", "Commonwealth War Graves Commission", "First World War", "Second World War", "Zeppelin raids",
              "Remembrance", "United Kingdom", "open data"],
    licence="cc-by-sa-4.0",
    related=[
        dict(identifier="https://github.com/Tristan-Hotham/air-raids", relation="issupplementedby", resource_type="software"),
        dict(identifier="https://tristan-hotham.github.io/air-raids/", relation="issupplementedby", resource_type="other"),
        dict(identifier="https://www.cwgc.org/find-records/find-war-dead/", relation="isderivedfrom", resource_type="dataset"),
        dict(identifier="https://en.wikipedia.org/wiki/German_bombing_of_Britain,_1914%E2%80%931918", relation="isderivedfrom", resource_type="other"),
        dict(identifier="https://en.wikipedia.org/wiki/Raid_on_Scarborough,_Hartlepool_and_Whitby", relation="isderivedfrom", resource_type="other"),
        dict(identifier="https://en.wikipedia.org/wiki/List_of_towns_and_cities_in_England_by_historical_population", relation="isderivedfrom", resource_type="other"),
        dict(identifier="https://www.ordnancesurvey.co.uk/products/os-open-names", relation="isderivedfrom", resource_type="dataset"),
        dict(identifier="https://www.wikidata.org", relation="isderivedfrom", resource_type="dataset"),
        dict(identifier="https://doi.org/10.5281/zenodo.23727151", relation="isderivedfrom", resource_type="other"),
    ])
for bad in ("—", "–", "--"): assert bad not in json.dumps(zmeta, ensure_ascii=False).replace("%E2%80%93", "")
json.dump(zmeta, open(os.path.join(Z, "meta.json"), "w"), indent=2, ensure_ascii=False)
shutil.copy(os.path.join(ROOT, "release", NAME + ".pdf"), Z)
for f in ["ww2_areas.csv", "ww2_daily.csv", "ww2_area_month.csv", "ww2_age.csv", "ww1_incidents.csv", "populations.csv", "wikipedia_compare.csv", "stories.csv", "results.json"]:
    shutil.copy(os.path.join(ROOT, "data", f), Z)
with zipfile.ZipFile(os.path.join(Z, "air-raids_code_and_data.zip"), "w", zipfile.ZIP_DEFLATED) as zf:
    for sub in ("code", "data"):
        for f in sorted(os.listdir(os.path.join(ROOT, sub))):
            p = os.path.join(ROOT, sub, f)
            if os.path.isfile(p) and not f.endswith(".pyc"): zf.write(p, f"air-raids/{sub}/{f}")
    for f in ("README.md", "LICENSE"): zf.write(os.path.join(ROOT, f), f"air-raids/{f}")
words = len(re.sub(r"<[^>]+>", " ", re.sub(r"\{\{IMG\|.*?\}\}", "", t)).split())
print("release files written; post words:", words)
