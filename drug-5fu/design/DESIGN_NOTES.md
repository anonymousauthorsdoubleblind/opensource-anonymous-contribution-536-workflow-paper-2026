# Design notes: the 5-fluorouracil drug test

These notes record why the drug test was set up as it was, which claims it supports, and the wording rules used in every figure and page. The site page `design.html` is the short, illustrated version.

## 0. Where the workflow comes from

The drug experiments were carried out with the open-source workflow located at <https://anonymousauthorsdoubleblind.github.io/opensource-anonymous-contribution-535-workflow-paper-2026/index.html>. The group first validated the open-source modules on annulenes, and then ran the same modules, unchanged, on the drug. The methods and the annulene runs are open-sourced at that address.

## 1. Question and scope

- **Question.** Run unchanged on a drug molecule, does the open-source Skala-1.1 workflow take rough, strained starting shapes to one stable structure whose computed infrared (IR) spectrum is consistent with a laboratory spectrum?
- **Molecule.** 5-fluorouracil (5-FU), C4H3FN2O2, 12 atoms, neutral closed-shell singlet, gas-phase model. Anticancer drug, first approved in 1962 (ChEMBL CHEMBL185; PubChem CID 3385; ATC L01BC02).
- **Form.** Only the 2,4-diketo tautomer, T1 (5-fluoropyrimidine-2,4(1H,3H)-dione, SMILES `O=c1[nH]cc(F)c(=O)[nH]1`). It is the form of the clinical drug and the only form detected in the argon-matrix experiment used for comparison.
- **Modules used.** Module 1 (agentic optimizer) and Module 2 (Hessian, thermochemistry, IR). Modules 3 (NMR) and 4 (molecular properties) were used for the annulenes only.

## 2. Why deformed starts

Screening pipelines produce approximate geometries (force-field, semi-empirical or machine-learned). A usable refinement step must relax them to the same minimum regardless of the start. Two strained starts were therefore made on purpose:

| Run | Start | Energy above final (Skala-1.1/def2-SVP) | Gradient evaluations | Result |
|---|---|---|---|---|
| 1 | standard (MMFF start, nudged 0.01 Å RMS) | at least 0.11 eV (first recorded step) | 23 | reference structure |
| 2 | deformed | 3.11 eV | 64 | 0.0072 Å RMSD and 0.51 meV from Run 1 |
| 3 | very deformed | 6.38 eV | 72 | 0.0051 Å RMSD and 0.29 meV from Run 1 |

These starts mimic rough screening geometries; they are not taken from a screening run.

## 3. Why Module 2 starts from Run 2

Module 2 read the structure that Module 1 had relaxed from the 3.1 eV start, re-optimized it at def2-TZVP (largest force 0.0099 eV/Å, 19 gradient evaluations) and built the finite-difference Hessian (73 force calculations, ±0.01 Å). The hand-off is gated: Module 2 refuses a deformed-start structure unless the same-structure check against Run 1 passed. No Module 2 run was made from the 6.4 eV start, so the 6.4 eV result is a geometry result only.

## 4. Why an argon-matrix reference

No gas-phase IR spectrum of 5-FU was found. Ivanov et al. (Low Temp. Phys. 43, 400, 2017) tabulate 26 fundamentals of 5-FU isolated in argon at 6 K, with integrated intensities and assignments; 25 of them (1800 to 300 cm-1) are compared. Solid-state (KBr) spectra are shifted by hydrogen bonding and were not used. The N–H stretches are not in that table and are not compared.

## 5. How the comparison is made

- Bands paired by frequency order; the character of the C=O, C6–H out-of-plane and N–H out-of-plane modes was checked.
- One least-squares scale factor, 0.9736, fitted on the same 25 bands (in-sample).
- Reported: unscaled mean offset (+21 cm-1), unscaled mean absolute error below and above 1000 cm-1 (10 and 46 cm-1), scaled mean absolute error (11 cm-1), largest scaled error (29 cm-1), rank correlation of intensities (0.86), and the two C=O bands (1764.5 vs 1761.2, 1740.3 vs 1742.0 cm-1).
- Everything is recomputed by `code/analysis/ir_compare.py`.

## 6. The supervised optimizer (Module 1)

L-BFGS runs in passes on Skala-1.1 forces. Code measures each step (step size against the cap, energy trend, curvature) and fires triggers. At fixed moments a language model (Gemini) is asked to choose one action from a fixed menu and to cite the measured evidence. A guard bounds each change and a probation period can roll it back. The agent never writes coordinates. In the three drug runs it raised the step cap (maxstep) 1, 3 and 4 times; all changes were accepted and none was rolled back.

## 7. Claims ledger

| Claim | Number | Status |
|---|---|---|
| Computed IR is consistent with the argon-matrix spectrum | 11 cm-1 after one scale factor (in-sample) | supported |
| Both C=O bands within 4 cm-1 after scaling | 1764.5/1761.2, 1740.3/1742.0 | supported |
| Strong and weak peaks in the same order | rank correlation 0.86 | supported |
| Zero imaginary frequencies (T1, def2-TZVP, Run 2 structure) | 0 of 30 | supported |
| IR computed from a 3.1 eV start | Module 2 from Run 2 | supported |
| Starts up to 6.4 eV reach one structure | within 0.0072 Å, 0.51 meV | supported (geometry only) |
| IR computed from the 6.4 eV start | none | not claimed |
| Skala-1.1 more accurate or faster than other methods | none | not claimed |

## 8. Wording rules

- Say "consistent with", never "reproduces" or "validated".
- Say "the workflow started 3.1 eV bent".
- Never "faster"; costs are "gradient evaluations".
- Never "all 25 peaks match".
- State with the headline: one molecule; harmonic; argon matrix at 6 K; bands paired by order; scale factor fitted on the same bands; N–H stretches not compared.
- Skala-1.1 is described in a preprint (arXiv:2506.14665, version 6), not peer reviewed. Its weights and licence belong to its developers.

## 9. Figure rules

- Main paper: Figure 1 (set-up, three starts to one shape) and Figure 2 (three questions: same shape, stable, IR consistent with the lab).
- Only T1. IR numbers only from the Run 2 start. Scale factor printed as 0.9736.
- Skala highlighted; no red for results that are not bad; the screening strip is marked as context only.
