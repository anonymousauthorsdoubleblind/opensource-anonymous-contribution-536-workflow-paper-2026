"""Supplementary T1 vibration figures, built from saved Module 2 data (no new calculations).
Run from anywhere: python code/figure_scripts/make_table.py  (set FIG_OUT to write elsewhere)."""
from pathlib import Path as _P
import os as _os
ROOT = _P(__file__).resolve().parents[2]                      # repository root
DATA = ROOT / "data" / "module2_T1"                           # opt_final.xyz and ir_cache/ from Module 2
OUT = _os.environ.get("FIG_OUT", str(ROOT / "figures" / "supplement"))
import csv,re,matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
if "Inter" in {f.name for f in fm.fontManager.ttflist}: plt.rcParams["font.family"]="Inter"
rows=[]
for r in csv.DictReader(open(ROOT / "data" / "comparison" / "5fu_T1_ir_vs_argon_matrix.csv")):
    try: x=float(r["matrix_cm1"])
    except: continue
    rows.append(r)
kind={"nu":"stretch","beta":"in-plane bend","gamma":"out-of-plane bend","tau":"torsion"}
def plain(ted):
    if "doublet" in ted:
        return "N1–H in-plane bend + C4–C5 stretch (matrix doublet 1418.6 / 1400.5, mean)"
    out=[]
    for part in ted.split(") "):
        part=part.strip().rstrip(")")
        if not part: continue
        m=re.match(r"(nu|beta|gamma|tau)([A-Za-z0-9]*)\((\d+)",part)
        if not m: out.append(part); continue
        k,rest,pc=m.groups()
        what=kind[k]
        if rest=="ring": nm="ring"
        else:
            toks=re.findall(r"[A-Z][a-z]?\d*",rest); nm="–".join(toks) if toks else rest
        out.append(f"{nm} {what} ({pc}%)")
    return ", ".join(out)
S=0.9736
n=len(rows)
fig,ax=plt.subplots(figsize=(11,0.34*n+1.6),dpi=200); ax.axis("off")
hdr=["Band","Measured\n(cm⁻¹)","Computed ×0.974\n(cm⁻¹)","Gap\n(cm⁻¹)","What moves (published assignment, share of the motion)","Measured strength"]
xs=[0.0,0.07,0.17,0.29,0.36,0.88]
ax.set_xlim(0,1);ax.set_ylim(-n-.6,1.2)
for x,h in zip(xs,hdr): ax.text(x,0.6,h,fontsize=8,weight="bold",va="center",color="#333")
ax.plot([0,1],[0.05,0.05],c="#333",lw=1)
mx=max(float(r["matrix_rel_intensity"]) for r in rows)
for i,r in enumerate(rows):
    y=-i-0.5
    if i%2==0: ax.axhspan(y-.5,y+.5,color="#f2f5f9",zorder=0)
    mc=float(r["matrix_cm1"]); cs=float(r["skala_cm1_unscaled"])*S; g=cs-mc
    ax.text(xs[0],y,r["matrix_mode"],fontsize=8,va="center",color="#555")
    ax.text(xs[1],y,f"{mc:.1f}",fontsize=8.5,va="center")
    ax.text(xs[2],y,f"{cs:.1f}",fontsize=8.5,va="center")
    ax.text(xs[3],y,f"{g:+.1f}",fontsize=8.5,va="center",color="#1d7a3e" if abs(g)<=15 else ("#a15c00" if abs(g)<=25 else "#b3261e"),weight="bold")
    ax.text(xs[4],y,plain(r["matrix_assignment_TED"]),fontsize=8,va="center")
    w=0.11*float(r["matrix_rel_intensity"])/mx
    ax.add_patch(plt.Rectangle((xs[5],y-.28),max(w,0.002),.56,color="#c8782c"))
ax.set_title("5-Fluorouracil T1: every compared band, what moves, and how far off the computed value is",fontsize=10.5,loc="left",pad=8)
fig.text(0.01,0.008,"Gap colours: green within 15 cm⁻¹, amber 15 to 25, red beyond 25. Computed bands are paired with measured ones by frequency order; for the C=O, C6–H wag and N–H wag modes we also checked the character against our own atom motions.\nMeasured: argon matrix, 6 K (Ivanov et al. 2017). Assignments are the published ones (potential-energy distribution); N–H stretches are not compared.",fontsize=6.8,color="#555",va="bottom")
fig.tight_layout(rect=(0,0.04,1,1))
for ext in ("png","pdf","svg"): fig.savefig(f"{OUT}/5fu_T1_band_assignment_table.{ext}")
