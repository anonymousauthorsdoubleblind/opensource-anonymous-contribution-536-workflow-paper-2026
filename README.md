# Skala-1.1 workflow: drug test on 5-fluorouracil

Code, data, figures, design notes and a static website for the drug test of an open-source workflow built around the machine-learned density functional Skala-1.1. The workflow takes a rough, strained molecular structure to a verified minimum and computes quantities a laboratory can measure. Here it is run, unchanged, on the anticancer drug 5-fluorouracil (5-FU).

**Result in one line.** The harmonic infrared spectrum of 5-FU computed with Skala-1.1 is consistent with the measured argon-matrix spectrum (25 bands; 11 cm-1 typical error after one scale factor fitted on the same bands), even when the workflow started from a structure 3.1 eV above the final energy.

Author names and affiliations are withheld for double-anonymous review.

## Browse

Open `drug-5fu/index.html` in a browser, or the GitHub Pages site once it is enabled. The site has a plain-language findings report at three reading levels, explainers, the workflow, a page on what the AI agent did, the findings with their sources, all figures, the data catalogue, the code map, reproduction steps, design notes, a page of ideas for future use (such as high-throughput screening) and limits.

## Layout

```
drug-5fu/
  index.html ... limits.html   the website (14 linked pages; the only script is the bundled 3Dmol.js viewer on runlog.html, no external scripts or fonts)
  assets/                      stylesheet, web-sized preview images, and the bundled 3Dmol.js viewer (BSD-3-Clause, licence files beside it)
  code/notebooks/              Colab notebooks: Module 1 (three starts) and Module 2 (Hessian, IR)
  code/figure_scripts/         scripts that redraw the supplementary vibration figures from saved forces
  code/analysis/ir_compare.py  recomputes the IR comparison numbers (standard library only)
  data/                        structures, run logs, agent transcripts, Hessian forces, frequencies, IR tables
  data/MANIFEST.csv            every data file with size and SHA-256
  figures/                     main, appendix and supplementary figures (PNG, PDF, SVG; GIF animations)
  design/DESIGN_NOTES.md       design decisions, claims ledger, wording and figure rules
```

## Quick check (no GPU)

```
python drug-5fu/code/analysis/ir_compare.py
```

## Scope and limits

One molecule (the diketo form, T1), harmonic vibrations, an argon-matrix reference at 6 K, bands paired by frequency order, a scale factor fitted on the same 25 bands. No other density functional was run on 5-FU here, so nothing in this repository claims that Skala-1.1 is more or less accurate than another method. The 6.4 eV start is a geometry result only. See `drug-5fu/limits.html`.

## Third-party material

- **Skala-1.1** is described in a preprint (arXiv:2506.14665, version 6) that has not been peer reviewed. The functional, its weights and its licence belong to its developers. This repository does not redistribute them; the notebooks install the published package (`skala` 2026.9).
- **Argon-matrix IR bands** in `drug-5fu/data/ir_reference/` and the measured columns of `drug-5fu/data/comparison/` are transcribed from Ivanov, Leontiev, Belous, Rubin and Karachevtsev, Low Temperature Physics 43, 400–408 (2017), doi:10.1063/1.4979957. Cite that paper when using them. The MIT licence covers our own code and data, not these values.
- **Language model.** Module 1 calls Gemini models through the Google GenAI API; you need your own API key.

## Licence

MIT, Copyright (c) 2026 The Authors. See `LICENSE`.

## Search engines

`robots.txt` (at the root and again inside `drug-5fu/`) tells all crawlers, including named search and AI crawlers, not to crawl. Every HTML page also carries `<meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex">` plus matching `googlebot` and `bingbot` tags. Crawlers read `robots.txt` only at the root of a domain, so on a GitHub Pages project site the meta tags are what keeps pages out of search results. The github.com repository pages themselves cannot be hidden this way if the repository is public.
