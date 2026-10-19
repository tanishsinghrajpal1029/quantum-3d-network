"""Fork v3 (king's graph): brute-force check of shortest paths, hop distance, link counts and U_max on small grids;
and GRID_KING off leaves every earlier topology unchanged."""
import importlib.util, itertools, os, sys
from collections import deque
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "upstream"))
sp = importlib.util.spec_from_file_location("g1k", os.path.join(H, "..", "fork", "drift_queue_des_g1.py"))
g = importlib.util.module_from_spec(sp); sp.loader.exec_module(g)
# 1. GRID_KING off: identical to the plain grid
for n, d in ((5, 2), (6, 3)):
    assert g.grid_topology(n, d) == g.grid_topology(n, d, king=False)
g.GRID_KING = True
for n in (4, 6, 9):
    nodes, edges = g.grid_topology(n, 2)
    assert len(edges) == 2 * n * (n - 1) + 2 * (n - 1) ** 2, (n, len(edges))
    adj = {v: [] for v in nodes}
    for e, l in edges.items():
        a, b = tuple(e); adj[a].append((b, l)); adj[b].append((a, l))
    def bfs_paths(s, t):                                   # all shortest paths by BFS layering (brute force)
        dist = {s: 0}; q = deque([s])
        while q:
            u = q.popleft()
            for w, _ in adj[u]:
                if w not in dist: dist[w] = dist[u] + 1; q.append(w)
        out = []
        def rec(u, path):
            if u == t: out.append(tuple(path)); return
            for w, l in adj[u]:
                if dist.get(w) == dist[u] + 1 and dist[w] <= dist[t]: path.append(l); rec(w, path); path.pop()
        rec(s, []); return dist[t], sorted(out)
    for a in nodes:
        for b in nodes:
            if a == b: continue
            h, ref = bfs_paths(a, b)
            assert h == g.hop_distance(a, b), (a, b)
            if h <= 4: assert g.shortest_paths_king(a, b, edges) == ref, (a, b)
    lz = g.LazyCands(nodes, edges, 4)
    um_l = max(len(set().union(*[set(c) for c in cs])) for cs in lz)
    um_b = max(len(set().union(*[set(p) for p in bfs_paths(a, b)[1]])) for a in nodes for b in nodes if 1 <= g.hop_distance(a, b) <= 4)
    assert um_l == um_b, (n, um_l, um_b)
    print(f"king {n}x{n}: {len(edges)} links; hop distance and every shortest-path list (h <= 4) match BFS; U_max {um_l} matches brute force")
print("ALL KING TESTS PASS")

# fork v3: study3d's per-hop counter (_king_hops_paths) equals the enumerated path counts for every user
import ast, numpy as np
src = open(os.path.join(H, "..", "fork", "study3d.py")).read()
fn = [n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "_king_hops_paths"][0]
ns = {}; exec(compile(ast.Module(body=[fn], type_ignores=[]), "study3d", "exec"), ns)
for n, L in ((9, 4), (12, 6)):
    nodes, edges = g.grid_topology(n, 2); lz = g.LazyCands(nodes, edges, L); X = np.array(nodes)
    hop, npaths = ns["_king_hops_paths"](X, lz.a, lz.b)
    for i in range(len(lz)):
        assert hop[i] == len(lz[i][0]) and npaths[i] == len(lz[i]), (n, i)
    print(f"king {n}x{n}, Lmax {L}: per-hop counter matches enumeration for all {len(lz)} users")
print("ALL KING COUNTER TESTS PASS")
