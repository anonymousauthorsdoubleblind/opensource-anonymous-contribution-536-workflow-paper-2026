"""Supplementary T1 vibration figures, built from saved Module 2 data (no new calculations).
Run from anywhere: python code/figure_scripts/make_viz.py  (set FIG_OUT to write elsewhere)."""
from pathlib import Path as _P
import os as _os
ROOT = _P(__file__).resolve().parents[2]                      # repository root
DATA = ROOT / "data" / "module2_T1"                           # opt_final.xyz and ir_cache/ from Module 2
OUT = _os.environ.get("FIG_OUT", str(ROOT / "figures" / "supplement"))
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Circle, FancyArrowPatch
from ase.io import read
from ase.data import atomic_masses, atomic_numbers
from ase.vibrations import Infrared
import os, io
from PIL import Image
if "Inter" in {f.name for f in fm.fontManager.ttflist}: plt.rcParams["font.family"]="Inter"
os.chdir(DATA)
a=read("opt_final.xyz"); N=len(a)
ir=Infrared(a,name="ir_cache",delta=0.01,nfree=2)
fr=np.real(ir.get_frequencies()); inten=np.array(ir.intensities)
H=ir.get_vibrations().get_hessian_2d()
m=a.get_masses(); sym=a.get_chemical_symbols()
M=np.repeat(m,3)
Hmw=H/np.sqrt(np.outer(M,M))
w2,V=np.linalg.eigh(Hmw)           # V columns = mass-weighted normal modes
order=np.argsort(w2); V=V[:,order]
fr_chk=np.sqrt(np.abs(w2[order]))*np.sign(w2[order])*0  # not used
# match ASE freqs by order (ASE sorted ascending in same way)
vib=list(range(6,36))              # 30 vibrational modes (skip 6 TR)
E=[]   # per-mode per-atom energy share (mass-weighted eigenvector squared)
for k in vib:
    e=(V[:,k].reshape(N,3)**2).sum(1); E.append(e/e.sum())
E=np.array(E)                      # (30,12)
F=fr[6:]; I=inten[6:]
S=0.9736
# raw (unsymmetrised) Hessian check from cache
import json
d=0.01
def forces(tag):
    j=json.load(open(f"ir_cache/cache.{tag}.json"))["forces"]["__ndarray__"]
    return np.array(j[2]).reshape(j[0])
Hraw=np.zeros((36,36))
for i in range(N):
    for c,ax in enumerate("xyz"):
        fp=forces(f"{i}{ax}+"); fm_=forces(f"{i}{ax}-")
        Hraw[3*i+c,:]=-(fp-fm_).ravel()/(2*d)
asym=np.abs(Hraw-Hraw.T).max(); print("raw asymmetry max",asym,"max |H|",np.abs(Hraw).max())
# np.save(OUT + "/Hraw.npy", Hraw)  # optional intermediate
# --- geometry views
X=a.positions-a.positions.mean(0)
u,s,vt=np.linalg.svd(X-0, full_matrices=False)
P=vt            # rows: principal directions; P[0],P[1] in-plane, P[2] normal
col={"C":"#555b66","O":"#d6362d","N":"#2f6fb8","F":"#2a9d5c","H":"#e8ebef"}
rad={"C":.32,"O":.30,"N":.30,"F":.28,"H":.17}
bonds=[(i,j) for i in range(N) for j in range(i+1,N) if np.linalg.norm(a.positions[i]-a.positions[j])<(1.2 if "H" in (sym[i],sym[j]) else 1.75)]
def draw(ax,pos2,disp2=None,lab=True,arrowscale=1.0,depth=None):
    for i,j in bonds: ax.plot([pos2[i,0],pos2[j,0]],[pos2[i,1],pos2[j,1]],c="#8c94a3",lw=2.2,zorder=1)
    for i in np.argsort(depth if depth is not None else np.zeros(N)):
        ax.add_patch(Circle(pos2[i],rad[sym[i]],fc=col[sym[i]],ec="#2b2f36",lw=.8,zorder=2))
        if lab and sym[i] in "OFN": ax.text(*pos2[i],sym[i],ha="center",va="center",fontsize=6.5,color="white",zorder=3,weight="bold")
    if disp2 is not None:
        for i in range(N):
            v=disp2[i]*arrowscale
            if np.hypot(*v)>0.12:
                ax.add_patch(FancyArrowPatch(pos2[i],pos2[i]+v,arrowstyle="-|>",mutation_scale=9,lw=1.8,color="#7a2fd0",zorder=4))
    ax.set_aspect("equal");ax.axis("off")
def project(vec3):  # onto (in-plane long, in-plane short, normal)
    return vec3@P.T
Xp=project(X)
EL=np.radians(35)
def vproj(pos,dsp,view):
    if view=="top": return pos[:,[0,1]],dsp[:,[0,1]],pos[:,2]
    f=lambda q: np.stack([q[:,0],q[:,1]*np.sin(EL)+q[:,2]*np.cos(EL)],1)
    return f(pos),f(dsp),pos[:,1]*np.cos(EL)-pos[:,2]*np.sin(EL)
def mode_disp(k):   # Cartesian displacement pattern, normalised so max atom shift = 1
    dsp=(V[:,k].reshape(N,3)/np.sqrt(m)[:,None])
    return dsp/np.abs(dsp).max()
# modes to show: (label, vib index 0-based into F)
def idx(f): return int(np.argmin(abs(F-f)))
KEY=[("C1=O0 stretch",1812.3,"top"),("C6=O7 stretch",1787.4,"top"),("C–F stretch band (published assignment)",1293.2,"top"),
     ("N2–H9 stretch",3663.2,"top"),("N–H out-of-plane wag (H9)",542.2,"side"),("C3–H10 out-of-plane wag",876.9,"side")]
fig,axs=plt.subplots(2,3,figsize=(11,7.2),dpi=200)
for ax,(lab,f0,view) in zip(axs.ravel(),KEY):
    k=idx(f0); dsp=mode_disp(vib[k]); dp=project(dsp)
    pos2,d2,dep=vproj(Xp,dp,view)
    draw(ax,pos2,d2,arrowscale=1.1,depth=dep)
    ax.set_xlim(pos2[:,0].min()-.9,pos2[:,0].max()+.9); ax.set_ylim(pos2[:,1].min()-.9,pos2[:,1].max()+.9)
    ax.set_title(f"{lab}\ncomputed {F[k]:.0f} cm$^{{-1}}$ (×0.974: {F[k]*S:.0f}) · {"top view" if view=="top" else "tilted view"}",fontsize=9.5)
fig.suptitle("5-Fluorouracil T1: what each key infrared band is (Skala-1.1 / def2-TZVP). Purple arrows = direction and relative size of each atom's motion.",fontsize=10)
fig.tight_layout(rect=(0,0,1,.95))
for ext in ("png","pdf","svg"): fig.savefig(f"{OUT}/5fu_T1_mode_arrows.{ext}")
plt.close(fig)
# --- animations
def frame(k,view,phase,figsize=(4.6,3.9)):
    dsp=mode_disp(vib[k]); amp=0.45
    pos=X+amp*np.sin(phase)*dsp
    Pp=project(pos)
    f,ax=plt.subplots(figsize=figsize,dpi=100)
    p2,_,dep=vproj(Pp,Pp,view); lim,_,_=vproj(project(X),project(X),view)
    draw(ax,p2,None,lab=True,depth=dep)
    ax.set_xlim(lim[:,0].min()-.9,lim[:,0].max()+.9); ax.set_ylim(lim[:,1].min()-.9,lim[:,1].max()+.9)
    ax.set_title(f"{lab_of[k]}  ·  {F[k]:.0f} cm$^{{-1}}$ computed (amplitude exaggerated)",fontsize=8.5)
    buf=io.BytesIO(); f.savefig(buf,format="png"); plt.close(f); buf.seek(0)
    return Image.open(buf).convert("P",palette=Image.ADAPTIVE)
lab_of={}
os.makedirs(f"{OUT}/animations",exist_ok=True)
names=["CO_C1O0_1812","CO_C6O7_1787","CF_1293","NH_N2H9_3663","NH_wag_542","CH_wag_877"]
for (lab,f0,view),nm in zip(KEY,names):
    k=idx(f0); lab_of[k]=lab
    frames=[frame(k,view,2*np.pi*t/24) for t in range(24)]
    frames[0].save(f"{OUT}/animations/5fu_T1_mode_{nm}.gif",save_all=True,append_images=frames[1:],duration=45,loop=0,disposal=2)
# --- element-projected vDOS
def broaden(x,freq,w,sig=18.0):
    return sum(wi*np.exp(-0.5*((x-fi)/sig)**2)/(sig*np.sqrt(2*np.pi)) for fi,wi in zip(freq,w))
elem={"H":[9,10,11],"C":[1,3,4,6],"N":[2,8],"O":[0,7],"F":[5]}
ecol={"H":"#9aa3b2","C":"#555b66","N":"#2f6fb8","O":"#d6362d","F":"#2a9d5c"}
Fs=F*S
fig,(a1,a2)=plt.subplots(1,2,figsize=(11,4.2),dpi=200,sharey=True,gridspec_kw={"width_ratios":[4.2,1],"wspace":.04})
for ax,(lo,hi) in zip((a1,a2),((150,1950),(3050,3750))):
    x=np.linspace(lo,hi,2000); base=np.zeros_like(x)
    for el in ["H","C","N","O","F"]:
        y=broaden(x,Fs,E[:,elem[el]].sum(1))
        ax.fill_between(x,base,base+y,color=ecol[el],alpha=.85,label=el,lw=0); base=base+y
    ax.set_xlim(lo,hi); ax.grid(alpha=.25)
a1.set_ylabel("vibrational density of states\n(share of motion energy per cm$^{-1}$)")
a1.set_xlabel("wavenumber (cm$^{-1}$), computed × 0.974");a2.set_xlabel("")
a1.spines["right"].set_visible(False);a2.spines["left"].set_visible(False);a2.tick_params(left=False)

for lab,f0 in [("C=O stretches",1750),("C–F stretch band",1259),("C–H out-of-plane wag",854),("ring and N–H wags",540)]:
    a1.axvline(f0,color="#444",lw=.8,ls=":",zorder=5); a1.text(f0,0.0665,lab,fontsize=7.5,ha="center",va="bottom",color="#333",rotation=0)
a1.set_ylim(0,0.075)
a2.text(3150,0.0665,"C–H",fontsize=7.5,ha="center",color="#333");a2.text(3540,0.0665,"N–H",fontsize=7.5,ha="center",color="#333")
a2.set_title("stretches",fontsize=8.5,color="#555",pad=-4)
h_,l_=a1.get_legend_handles_labels()
a2.legend(h_,l_,title="atom type",loc="center",bbox_to_anchor=(0.5,0.52),fontsize=8.5,frameon=False)
fig.suptitle("5-Fluorouracil T1: where each type of atom moves, by vibration frequency (Skala-1.1 / def2-TZVP, harmonic; 12-atom molecule, 30 vibrations)",fontsize=10)
fig.tight_layout(rect=(0,0,1,.94))
for ext in ("png","pdf","svg"): fig.savefig(f"{OUT}/5fu_T1_projected_vDOS.{ext}")
plt.close(fig)
# np.save(OUT + "/E.npy", E); np.save(OUT + "/F.npy", F)  # optional intermediates
# print element shares for key modes
for lab,f0,_ in KEY:
    k=idx(f0); print(lab,round(F[k],1),{el:round(E[k,elem[el]].sum(),2) for el in elem})
