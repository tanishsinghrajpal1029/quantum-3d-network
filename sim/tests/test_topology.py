"""Fork vs upstream: d = 2 topology and candidate paths must be identical; d = 3 sanity counts."""
import importlib.util, itertools, sys, os
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "upstream"))
def load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
up = load("g1_up", os.path.join(H, "..", "upstream", "drift_queue_des_g1.py"))
fk = load("g1_fk", os.path.join(H, "..", "fork", "drift_queue_des_g1.py"))
for n in (5, 10, 30):
    nu, eu = up.grid_topology(n); nf, ef = fk.grid_topology(n, 2)
    assert nu == nf and eu == ef and list(eu.items()) == list(ef.items()), n
    for L in (2, 3):
        cu = [up.shortest_paths(a, b, eu) for a in nu for b in nu if 1 <= abs(a[0]-b[0]) + abs(a[1]-b[1]) <= L]
        cf = [fk.shortest_paths(a, b, ef) for a in nf for b in nf if 1 <= fk.hop_distance(a, b) <= L]
        assert cu == cf, (n, L)
    print(f"d=2 n={n}: nodes, link ids and candidate paths identical (Lmax 2, 3)")
for n in (3, 5, 10):
    nodes, edges = fk.grid_topology(n, 3)
    assert len(nodes) == n ** 3 and len(edges) == 3 * n * n * (n - 1)
    for a, b in itertools.islice(((a, b) for a in nodes for b in nodes if 1 <= fk.hop_distance(a, b) <= 3), 0, None, 97):
        ps = fk.shortest_paths(a, b, edges); h = fk.hop_distance(a, b)
        assert all(len(p) == h for p in ps)
        dv = [abs(x - y) for x, y in zip(a, b)]
        from math import factorial
        assert len(ps) == factorial(h) // (factorial(dv[0]) * factorial(dv[1]) * factorial(dv[2]))
    print(f"d=3 n={n}: {len(nodes)} nodes, {len(edges)} links; path counts = multinomial")
print("ALL TOPOLOGY TESTS PASS")
