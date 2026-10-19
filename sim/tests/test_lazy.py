"""Fork v2: LazyCands must equal the eager candidate list entry for entry (same users, same order, same sorted paths),
and give the same U_max, for d = 2 and d = 3."""
import importlib.util, os, sys, time
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "upstream"))
sp = importlib.util.spec_from_file_location("g1f", os.path.join(H, "..", "fork", "drift_queue_des_g1.py"))
g = importlib.util.module_from_spec(sp); sp.loader.exec_module(g)
for n, d, L in ((5, 2, 2), (5, 2, 3), (11, 2, 3), (4, 3, 3), (5, 3, 4), (6, 3, 6)):
    nodes, edges = g.grid_topology(n, d)
    eager = [g.shortest_paths(a, b, edges) for a in nodes for b in nodes if 1 <= g.hop_distance(a, b) <= L]
    lazy = g.LazyCands(nodes, edges, L)
    assert len(lazy) == len(eager), (n, d, L)
    assert all(lazy[i] == eager[i] for i in range(len(eager))), (n, d, L)
    um_e = max(len(set().union(*[set(c) for c in cs])) for cs in eager)
    um_l = max(len(set().union(*[set(c) for c in cs])) for cs in lazy)
    assert um_e == um_l, (um_e, um_l)
    print(f"d={d} n={n} Lmax={L}: {len(eager)} users identical; U_max {um_e} (lazy iterates {len(lazy._rep)} offsets)")
t0 = time.time(); nodes, edges = g.grid_topology(10, 3); lz = g.LazyCands(nodes, edges, 6)
um = max(len(set().union(*[set(c) for c in cs])) for cs in lz)
print(f"3D 10^3, Lmax 6: {len(lz)} users, U_max {um}, built + U_max in {time.time() - t0:.1f}s")
print("ALL LAZY TESTS PASS")

# fork v2: the fast enumerator must equal the original one exactly (sorted lists of link-id tuples)
import itertools, random
random.seed(1)
for n, d, L in ((5, 2, 4), (11, 2, 6), (6, 3, 6), (5, 3, 4)):
    nodes, edges = g.grid_topology(n, d); pairs = [(a, b) for a in nodes for b in nodes if 1 <= g.hop_distance(a, b) <= L]
    for a, b in random.sample(pairs, min(400, len(pairs))):
        assert g.shortest_paths_fast(a, b, edges) == g.shortest_paths(a, b, edges), (a, b)
    print(f"fast enumerator == original on 400 random pairs: d={d} n={n} Lmax={L}")
nodes, edges = g.grid_topology(10, 3); t0 = time.time(); ps = g.shortest_paths_fast((0, 0, 0), (3, 3, 2), edges)
print(f"3D offset (3,3,2): {len(ps)} paths in {time.time() - t0:.3f}s (8!/(3!3!2!) = 560)")
assert len(ps) == 560
print("FAST ENUMERATOR TESTS PASS")
