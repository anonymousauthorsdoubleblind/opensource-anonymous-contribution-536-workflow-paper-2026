"""Supplementary T1 vibration figures, built from saved Module 2 data (no new calculations).
Run from anywhere: python code/figure_scripts/make_hess.py  (set FIG_OUT to write elsewhere)."""
from pathlib import Path as _P
import os as _os
ROOT = _P(__file__).resolve().parents[2]                      # repository root
DATA = ROOT / "data" / "module2_T1"                           # opt_final.xyz and ir_cache/ from Module 2
OUT = _os.environ.get("FIG_OUT", str(ROOT / "figures" / "supplement"))
import numpy as np, json, csv, os, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.colors import LogNorm
from ase.io import read
if "Inter" in {f.name for f in fm.fontManager.ttflist}: plt.rcParams["font.family"]="Inter"
os.chdir(DATA)
a=read("opt_final.xyz"); N=12; m=a.get_masses(); sym=a.get_chemical_symbols()
lab=[f"{s}{i}" for i,s in enumerate(sym)]
d=0.01
def forces(tag):
    j=json.load(open(f"ir_cache/cache.{tag}.json"))["forces"]["__ndarray__"]
    return np.array(j[2]).reshape(j[0]).ravel()
Hc=np.zeros((36,36));Hf=np.zeros((36,36));Hb=np.zeros((36,36))
F0=None
for i in range(N):
    for c,ax in enumerate("xyz"):
        fp=forces(f"{i}{ax}+");fm_=forces(f"{i}{ax}-")
        Hc[3*i+c]=-(fp-fm_)/(2*d)
        # one-sided: needs reference forces at equilibrium; estimate from mean of +/- (error O(d^2))
        f0=(fp+fm_)/2
        Hf[3*i+c]=-(fp-f0)/d; Hb[3*i+c]=-(f0-fm_)/d   # identical by construction -> not independent; skip
M=np.repeat(m,3)
def freqs(H):
    Hs=(H+H.T)/2; w2=np.linalg.eigvalsh(Hs/np.sqrt(np.outer(M,M)))
    conv=np.sqrt(1.602176634e-19/1.66053906660e-27/1e-20)/(2*np.pi*2.99792458e10)
    return np.sign(w2)*np.sqrt(np.abs(w2))*conv
fc=freqs(Hc); print(fc[6:12])
# atom-pair coupling map: Frobenius norm of each 3x3 block
B=np.array([[np.linalg.norm(Hc[3*i:3*i+3,3*j:3*j+3]) for j in range(N)] for i in range(N)])
Hsym=(Hc+Hc.T)/2
asym=np.abs(Hc-Hc.T); rel=asym.max()/np.abs(Hc).max()
# sum rule: translational invariance, sum over j of block (i,j) should be ~0
sumrule=max(np.abs(sum(Hsym[3*i:3*i+3,3*j:3*j+3] for j in range(N))).max() for i in range(N))
print("asym max",asym.max(),"rel",rel,"sum-rule max",sumrule)
fig,axs=plt.subplots(1,3,figsize=(14,5.4),dpi=200,gridspec_kw={"width_ratios":[1.05,1.05,1]})
im=axs[0].imshow(Hsym,cmap="RdBu_r",vmin=-40,vmax=40)
for k in range(1,N): axs[0].axhline(3*k-.5,c="#999",lw=.4);axs[0].axvline(3*k-.5,c="#999",lw=.4)
axs[0].set_xticks(np.arange(N)*3+1);axs[0].set_xticklabels(lab,rotation=90,fontsize=7);axs[0].set_yticks(np.arange(N)*3+1);axs[0].set_yticklabels(lab,fontsize=7)
axs[0].set_title("The full Hessian: 36 × 36\n(each 3 × 3 square is one atom pair; colour = stiffness, eV/Å²)",fontsize=9.5)
plt.colorbar(im,ax=axs[0],fraction=.046,pad=.03,label="eV/Å² (colour range clipped at ±40)")
Bm=B.copy()
im2=axs[1].imshow(np.where(Bm>0,Bm,np.nan),cmap="viridis",norm=LogNorm(vmin=0.05,vmax=Bm.max()))
axs[1].set_xticks(range(N));axs[1].set_xticklabels(lab,rotation=90,fontsize=7);axs[1].set_yticks(range(N));axs[1].set_yticklabels(lab,fontsize=7)
axs[1].set_title("Which atoms feel each other: 12 × 12\n(size of each 3 × 3 block, log colour)",fontsize=9.5)
plt.colorbar(im2,ax=axs[1],fraction=.046,pad=.03,label="block size, eV/Å²")
axs[2].axis("off")
txt=("Sanity checks from the saved calculation\n\n"
 f"• Symmetry: the matrix should mirror across\n  its diagonal. Largest mismatch\n  {asym.max():.3f} eV/Å², i.e. {rel*100:.2f}% of the\n  largest entry ({np.abs(Hc).max():.0f} eV/Å²).\n\n"
 f"• Translation invariance: moving the whole\n  molecule should cost nothing. Largest\n  leftover row-sum {sumrule:.2f} eV/Å²\n  ({sumrule/np.abs(Hc).max()*100:.2f}% of the largest entry).\n\n"
 "• Method: central differences, ±0.01 Å on\n  every coordinate (72 displaced geometries\n  + 1 reference), forces from Skala-1.1 /\n  def2-TZVP.\n\n"
 "• Lowest six eigenvalues belong to overall\n  translation and rotation; the 30 real\n  vibrations are above them.")
axs[2].text(0,1,txt,va="top",fontsize=9,linespacing=1.3)
fig.suptitle("5-Fluorouracil T1: the force-constant (Hessian) matrix behind the vibrations",fontsize=11)
fig.tight_layout(rect=(0,0,1,.95))
for ext in ("png","pdf","svg"): fig.savefig(f"{OUT}/5fu_T1_hessian_map.{ext}")
print("TR block",fc[:6])
