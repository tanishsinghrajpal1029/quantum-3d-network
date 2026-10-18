"""3D vs 2D lattices at matched node counts: analytic / exact-count baseline (no network simulation).
For a d-dimensional n^d lattice with nearest-neighbour links:
  - hop distance of uniform random node pairs (exact, from displacement counts: pairs at offset v number prod(n-|v_i|));
  - share of pairs within Lmax hops (the request range the guard can serve on the simulated hardware);
  - shortest-path candidates and U_max (links on the union of all shortest paths of a pair, maximised over pairs within Lmax);
  - Werner fidelity after h hops at link level lam, F = (3 lam^h + 1)/4 (no memory decay, ideal swaps): an optimistic toy.
Usage: python3 lattice_baseline.py > lattice_baseline_output.txt"""
import itertools, math
import numpy as np

def offsets(n, d):
    r = range(-(n - 1), n)
    for v in itertools.product(r, repeat=d):
        if any(v): yield v

def pair_hist(n, d):
    """Unordered node pairs by hop distance."""
    h = {}
    for v in offsets(n, d):
        c = math.prod(n - abs(x) for x in v); k = sum(abs(x) for x in v); h[k] = h.get(k, 0) + c
    return {k: c // 2 for k, c in sorted(h.items())}

def n_shortest(v):
    a = [abs(x) for x in v]; return math.factorial(sum(a)) // math.prod(math.factorial(x) for x in a)

def union_links(v):
    """Number of distinct lattice links used by all shortest paths for offset v (inside the bounding box)."""
    a = [abs(x) for x in v]; d = len(a); tot = 0
    for ax in range(d):                       # links along axis ax inside the box: a[ax] * prod_{j!=ax}(a[j]+1)
        tot += a[ax] * math.prod(a[j] + 1 for j in range(d) if j != ax)
    return tot

def umax(d, L):
    best = 0
    for v in itertools.product(range(L + 1), repeat=d):
        if 1 <= sum(v) <= L: best = max(best, union_links(v))
    return best

F = lambda lam, h: (3 * lam ** h + 1) / 4
cases = [("2D 11x11", 11, 2), ("3D 5^3", 5, 3), ("2D 32x32", 32, 2), ("3D 10^3", 10, 3), ("2D 30x30", 30, 2), ("2D 58x58", 58, 2), ("3D 15^3", 15, 3)]
print("Matched-size lattices (nearest-neighbour links)")
print(f"{'lattice':10s} {'nodes':>6s} {'links':>6s} {'deg':>4s} {'diam':>5s} {'mean hops':>9s}  share of pairs within L=1..4 hops")
for name, n, d in cases:
    h = pair_hist(n, d); tot = sum(h.values()); mean = sum(k * c for k, c in h.items()) / tot
    links = d * n ** (d - 1) * (n - 1); share = [sum(c for k, c in h.items() if k <= L) / tot for L in (1, 2, 3, 4)]
    print(f"{name:10s} {n**d:6d} {links:6d} {2*links/n**d:4.2f} {d*(n-1):5d} {mean:9.2f}  " + "  ".join(f"{100*s:5.2f}%" for s in share))
print("\nU_max (links a user could be routed over, all shortest paths, requests up to Lmax hops) and the guard's per-link level")
for L in (1, 2, 3, 4):
    u2, u3 = umax(2, L), umax(3, L); print(f"  Lmax={L}: 2D U_max={u2:3d} (alpha/{u2})   3D U_max={u3:3d} (alpha/{u3})")
print("\nShortest-path candidates per pair, by offset (2D vs 3D)")
for v in [(1, 1), (2, 1), (1, 1, 1), (2, 1, 0), (2, 1, 1)]: print(f"  offset {v}: {n_shortest(v)} paths, {union_links(v)} links in their union")
print("\nToy Werner fidelity after h hops (no memory decay, ideal swaps), F=(3 lam^h+1)/4")
for lam in (0.95, 0.97, 0.99):
    print(f"  lam={lam}: " + "  ".join(f"h={h}:{F(lam,h):.3f}" for h in range(1, 9)) + f"   max hops with F>=0.9: {max([h for h in range(1,60) if F(lam,h)>=0.9] or [0])}")
print("\nShare of uniform random pairs servable at F>=0.9 under the toy model (hops <= max hops above)")
for lam in (0.97, 0.99):
    hm = max([h for h in range(1, 60) if F(lam, h) >= 0.9] or [0])
    row = []
    for name, n, d in cases:
        h = pair_hist(n, d); tot = sum(h.values()); row.append(f"{name}: {100*sum(c for k,c in h.items() if k<=hm)/tot:5.1f}%")
    print(f"  lam={lam} (<= {hm} hops): " + "; ".join(row))
