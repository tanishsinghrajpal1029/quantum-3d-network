# EXPLORATORY geometry check: is the 3D gain about dimension, or just about shorter hop distances (degree / diameter / boundary)?
# Share of ordered node pairs within h hops (h = analytic true-model reach: 3 / 4 / 6 for F0 0.97 / 0.98 / 0.99).
import itertools, numpy as np
def share(n, d, h, torus=False, king=False):
    offs = np.array(list(itertools.product(range(-(n - 1), n), repeat=d)))
    pairs = np.prod(n - np.abs(offs), axis=1).astype(float)          # number of ordered pairs with this offset (open lattice)
    a = np.abs(offs)
    if torus: a = np.minimum(a, n - a)
    dist = a.max(1) if king else a.sum(1)
    m = (dist >= 1) & (dist <= h); tot = pairs[(dist >= 1)].sum() if not torus else (n ** d) * (n ** d - 1)
    if torus: pairs = np.prod(n - np.abs(offs), axis=1)
    return pairs[m].sum() / pairs[dist >= 1].sum()
rows = [("2D 32x32 grid (degree 4)", 32, 2, False, False), ("2D 32x32 torus (degree 4, no edges)", 32, 2, True, False),
        ("2D 32x32 king's graph (degree 8, diagonals)", 32, 2, False, True), ("3D 10^3 cube (degree 6)", 10, 3, False, False),
        ("3D 10^3 torus (degree 6, no edges)", 10, 3, True, False)]
print(f"{'lattice':46s} {'mean hop':>8s} " + " ".join(f"{'<=%d hops' % h:>9s}" for h in (3, 4, 6)))
for name, n, d, t, k in rows:
    offs = np.array(list(itertools.product(range(-(n - 1), n), repeat=d))); w = np.prod(n - np.abs(offs), axis=1).astype(float)
    a = np.abs(offs); a = np.minimum(a, n - a) if t else a; dist = a.max(1) if k else a.sum(1); m = dist >= 1
    mean = (dist[m] * w[m]).sum() / w[m].sum()
    print(f"{name:46s} {mean:8.1f} " + " ".join(f"{share(n, d, h, t, k):9.1%}" for h in (3, 4, 6)))
