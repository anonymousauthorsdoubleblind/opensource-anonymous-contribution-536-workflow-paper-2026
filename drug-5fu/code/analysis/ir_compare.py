"""Recompute the T1 infrared comparison numbers from the released data.

Reads   data/comparison/5fu_T1_ir_vs_argon_matrix.csv  (25 paired bands)
Prints  the fitted scale factor, mean absolute errors (unscaled, scaled,
        below/above 1000 cm-1), the largest single error and the rank
        correlation of intensities.

Note: the scale factor is fitted on the same 25 bands it is then judged on
(in-sample). Bands are paired by frequency order. N-H stretches are not used.

Usage (from the repository root):  python code/analysis/ir_compare.py
Needs only the Python standard library.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSV = ROOT / "data" / "comparison" / "5fu_T1_ir_vs_argon_matrix.csv"

rows = []
with open(CSV, newline="") as fh:
    for r in csv.DictReader(fh):
        try:
            rows.append((float(r["matrix_cm1"]), float(r["skala_cm1_unscaled"]),
                         float(r["matrix_rel_intensity"]), float(r["skala_km_per_mol"])))
        except (ValueError, TypeError, KeyError):
            continue  # skips the N-H stretch notes at the end of the file

exp = [r[0] for r in rows]
calc = [r[1] for r in rows]
n = len(rows)

# least-squares scale factor  s = sum(exp*calc) / sum(calc^2)
s = sum(e * c for e, c in zip(exp, calc)) / sum(c * c for c in calc)

def mae(pairs):
    pairs = list(pairs)
    return sum(abs(a - b) for a, b in pairs) / len(pairs)

unscaled = list(zip(calc, exp))
scaled = [(c * s, e) for c, e in zip(calc, exp)]
low = [(c, e) for c, e in zip(calc, exp) if e < 1000]
high = [(c, e) for c, e in zip(calc, exp) if e >= 1000]
mean_signed = sum(c - e for c, e in unscaled) / n
largest = max(abs(c - e) for c, e in scaled)

def ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    rk = [0.0] * len(v)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            rk[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return rk

def pearson(x, y):
    mx, my = sum(x) / len(x), sum(y) / len(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / (sxx * syy) ** 0.5

rho = pearson(ranks([r[2] for r in rows]), ranks([r[3] for r in rows]))

print(f"bands compared                     : {n}")
print(f"fitted scale factor (in-sample)    : {s:.4f}")
print(f"mean signed offset, unscaled       : {mean_signed:+.1f} cm-1")
print(f"MAE unscaled, all bands            : {mae(unscaled):.1f} cm-1")
print(f"MAE unscaled, bands below 1000 cm-1: {mae(low):.1f} cm-1  ({len(low)} bands)")
print(f"MAE unscaled, bands >= 1000 cm-1   : {mae(high):.1f} cm-1  ({len(high)} bands)")
print(f"MAE after scaling                  : {mae(scaled):.1f} cm-1")
print(f"largest single error after scaling : {largest:.1f} cm-1")
print(f"rank correlation of intensities    : {rho:.2f}")
