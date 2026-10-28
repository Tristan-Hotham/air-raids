"""Step 7. Build the paper PDF: fill code/paper_template.tex with numbers and tables from data/results.json,
write release/paper/Hotham_Bombs_on_Britain.tex and compile it with xelatex (figures from step 6).
Run: python3 code/07_paper.py
"""
import importlib.util, json, os, re, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
spec = importlib.util.spec_from_file_location("b", os.path.join(HERE, "04_build_site.py")); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
R = b.R
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Bombs_on_Britain"
tex = lambda s: str(s).replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")


def sub(m):
    v = b.fmt(b.get(m.group(1)), m.group(3))
    return tex(v)


ATT = {"airship": "Airship", "aeroplane": "Aeroplane", "naval": "Warships"}
rows = "".join(f"{b.fmt(r['date'], 'date')} & {tex(r['places'])} & {ATT[r['attack']]} & {r['killed']:,}\\\\\n" for r in R["ww1"]["top"][:10])
T1 = ("\\begin{table}[tbp]\\centering\\small\\caption{The ten deadliest raids and bombardments of 1914 to 1918 in the table. Chatham's dead were naval ratings and most of the "
      "Cleethorpes dead were soldiers; other rows are mainly civilians.}\\label{tab:ww1}\\begin{tabular}{l>{\\raggedright\\arraybackslash}p{7.6cm}lr}\\toprule Date & Place & Attack & Killed\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rate = {r["name"]: r["per1000"] for r in R["rates"]}
rows = "".join(f"{i + 1} & {tex(r['name'])} & {r['deaths']:,} & {r['blitz']:,} & {b.fmt(r['peak_day'], 'date')} ({r['peak']:,}) & {('%.1f' % rate[r['name']]) if r['name'] in rate else ''}\\\\\n" for i, r in enumerate(R["top_outside"][:15]))
T2 = ("\\begin{table}[tbp]\\centering\\small\\caption{The fifteen longest civilian rolls outside Greater London, 1939 to 1947, with deaths in the Blitz, the worst day and, where a population is available, approximate deaths per 1,000 people.}\\label{tab:top}"
      "\\begin{tabular}{rlrrlr}\\toprule & Area & Dead & Blitz & Worst day & Per 1,000\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = "".join(f"{tex(r['town'])} & {r['cwgc']:,} & {r['wikipedia']:,} & {tex(r['note'])}\\\\\n" for r in R["compare"])
T3 = ("\\begin{table}[tbp]\\centering\\small\\caption{Civilian dead on the CWGC roll against the figure quoted in each place's Wikipedia article (Liverpool: eight Merseyside rolls).}\\label{tab:cmp}"
      "\\begin{tabular}{lrrl}\\toprule Place & Roll & Wikipedia & Note\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
t = open(os.path.join(HERE, "paper_template.tex")).read()
t = re.sub(r"\{\{(?!TABLE_)([^}|]+)(\|(\w+))?\}\}", sub, t).replace("{{TABLE_WW1}}", T1).replace("{{TABLE_TOP}}", T2).replace("{{TABLE_CMP}}", T3)
assert "{{" not in t and "--" not in t.replace("\\%E2\\%80\\%93", "") and "—" not in t and "–" not in t
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
for ext in (".aux", ".log", ".out"):
    p = os.path.join(OUT, NAME + ext)
    if os.path.exists(p): os.remove(p)
shutil.copy(os.path.join(OUT, NAME + ".pdf"), os.path.join(ROOT, "release", NAME + ".pdf"))
print("paper written", r.returncode)
