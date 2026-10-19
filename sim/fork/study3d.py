"""P3D driver: the Study 34 closed loop (study32.Net32 arms) on d-dimensional square lattices.

Set P3D_D (2 or 3) and P3D_GRID (side n) BEFORE import; one process runs one lattice (the correlated-link generator builds
its lattice at import, as in Study 34). Put fork/ before upstream/ on sys.path so the d-dimensional drift_queue_des_g1 wins.

Compatibility mode (task block 'S34g<n>', d = 2): seeds, run ids and rows are those of Study 34, so the fork can be checked
bit for bit against the paper's runs.csv. Any other block uses fresh P3D seed strings (pre-register them before a real run).
Changes vs study34.py: lattice dimension; link-count assertion d n^(d-1) (n-1); 'u' (matched exposure) variant not ported.
"""
import hashlib, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.abspath(os.path.join(HERE, "..", "upstream"))
# fork/ first, upstream/ second, whatever was on the path before (PYTHONPATH, runner dir): the fork's g1 must shadow upstream
sys.path[:] = [HERE, UP] + [p for p in sys.path if not p or os.path.abspath(p) not in (HERE, UP)]
import drift_queue_des_g1 as g1
assert hasattr(g1, "GRID_D"), f"wrong drift_queue_des_g1 on path: {g1.__file__}"
D = int(os.environ.get("P3D_D", "2")); GRID = int(os.environ.get("P3D_GRID", "5"))
# fork v2 (reach): P3D_REACH=1 adds the link-quality sweep presets and lazy users; P3D_LAZY=1 alone tests lazy users
REACH = os.environ.get("P3D_REACH") == "1"
g1.GRID_LAZY = REACH or os.environ.get("P3D_LAZY") == "1"
if REACH:
    # ionfut's rate, memory and gates (drift_queue_des_v15.IONFUT) with link fidelity 0.97 / 0.98 / 0.99. Service radius
    # Lmax = analytic reach (longest hop whose mean true fidelity clears tau = 0.9: 3 / 4 / 6; analytics/reach_baseline.py,
    # REACH_SWEEP=1) + P3D_RADIUS_EXTRA (default 2), so the network also attempts requests beyond the analytic reach and the
    # guard, not the radius, decides what is served.
    EXTRA = int(os.environ.get("P3D_RADIUS_EXTRA", "2"))
    for F0, Lm in ((0.97, 3), (0.98, 4), (0.99, 6)):
        g1.HW.setdefault(f"fut{int(round(F0 * 100))}", (dict(F0=F0, R=1000.0, T2=1.0, q=0.001, e=0.003), 0.90, Lm + EXTRA, 3.0))
g1.GRID_N, g1.GRID_D = GRID, D                            # must precede every import that builds the lattice (corr_net)
import study32 as s32
import corr_net as cn1
assert cn1.NL == D * GRID ** (D - 1) * (GRID - 1), (cn1.NL, D, GRID)
assert len(cn1.NODES) == GRID ** D

SEEDS = (19341, 19342, 19343, 19344); DEV = (20341, 20342, 20343, 20344)    # Study 34 (compat); P3D blocks set their own below
P3D_SEEDS = (19351, 19352, 19353, 19354)                 # Study 3D-1 confirmatory (docs/PREREG_3D1.md); pilots use P3D_DEV
P3D_DEV = (30341, 30342, 30343, 30344)
R3D_DEV = (30361, 30362, 30363, 30364)                    # Study 3D-2 (reach) pilots
R3D_SEEDS = None                                          # Study 3D-2 confirmatory: fixed only in its pre-registration
HWS = ("ion2020", "ionproj")
HMAX = (6 + EXTRA) if REACH else 3                                  # per-hop columns h1..h{HMAX} always written


def configs(mults=("base",)):
    C = []
    for mult in mults:
        for hw in HWS:
            for sc in ("-", "o0.044"): C.append((hw, "kg", f"{sc}|p00|{mult}"))
            for sc in ("-", "o0.044", "o0.044F"):
                for p in ("p10", "p20"): C.append((hw, "kgMChN", f"{sc}|{p}|{mult}"))
                C.append((hw, "kgMCa", f"{sc}|p10|{mult}"))
    return C


class Net3D(s32.Net32):
    def __init__(s, hw, pat, arm, cfg, seed):
        super().__init__(hw, pat, arm, cfg, seed)
        var = cfg.split("|")[2]; s.var34 = var
        assert var in ("base", "m3"), "variant 'u' not ported"
        s.mult = 3.0 if var == "m3" else 1.0
        s.rate25 *= s.mult
        s.users_all = len(s.cands)

    def run(s):
        out = super().run()
        out.update(grid=GRID, nl=s.nl, rate_mult=s.mult, var34=s.var34, users_all=s.users_all, users_served=len(s.ustat),
                   users_bad_served=sum(1 for x in s.ustat.values() if x[1] > 0))
        if not s.compat34 and isinstance(s.cands, g1.LazyCands):   # fork v2: per-hop breakdown without building every list
            import numpy as np
            from math import factorial
            C = s.cands; X = np.array(C.nodes, int); off = np.abs(X[C.b] - X[C.a]); hop = off.sum(1)
            fac = np.array([factorial(k) for k in range(off.max() * D + 1)], float)
            npaths = fac[hop] / np.prod(fac[off], axis=1)                 # shortest paths = multinomial(hop; offsets)
            by_h = {}
            for ci, x in s.ustat.items(): by_h.setdefault(int(hop[ci]), []).append(x)
            for h in range(1, HMAX + 1):
                m_ = hop == h; us = by_h.get(h, [])
                out[f"h{h}_users"] = int(m_.sum()); out[f"h{h}_paths_mean"] = float(npaths[m_].mean()) if m_.any() else float("nan")
                out[f"h{h}_served"] = len(us); out[f"h{h}_users_bad"] = sum(1 for x in us if x[1] > 0)
                out[f"h{h}_deliv"] = sum(x[0] for x in us); out[f"h{h}_bad"] = sum(x[1] for x in us)
            out["umax"] = s.Umax
            if REACH:
                N = GRID ** D; out["n_pairs_all"] = N * (N - 1); out["share_servable"] = len(s.cands) / (N * (N - 1))
        elif not s.compat34:                                       # per-hop breakdown (read-only: no random draws)
            hop = [len(cs[0]) for cs in s.cands]
            for h in range(1, HMAX + 1):                           # fixed column set for every hardware (pilot 1 lesson)
                ids = [i for i, x in enumerate(hop) if x == h]; us = [s.ustat[i] for i in ids if i in s.ustat]
                out[f"h{h}_users"] = len(ids); out[f"h{h}_paths_mean"] = float(sum(len(s.cands[i]) for i in ids) / len(ids)) if ids else float("nan")
                out[f"h{h}_served"] = len(us); out[f"h{h}_users_bad"] = sum(1 for x in us if x[1] > 0)
                out[f"h{h}_deliv"] = sum(x[0] for x in us); out[f"h{h}_bad"] = sum(x[1] for x in us)
            out["umax"] = s.Umax
        return out


def compat(t):
    return t[0] == f"S34g{GRID}" and D == 2


def run_id(t):
    if compat(t): return hashlib.sha256("s34|{}|{}|{}|{}|{}|{}".format(*t).encode()).hexdigest()[:12]
    return hashlib.sha256("p3d|{}|{}|{}|{}|{}|{}".format(*t).encode()).hexdigest()[:12]


def run_one(t):
    blk, hw, pat, arm, cfg, idx = t
    if compat(t):
        seeds = SEEDS
        nseed = int(hashlib.sha256(f"s34net|g{GRID}|{hw}|{idx}".encode()).hexdigest()[:8], 16)
        rseed = int(hashlib.sha256(f"s34run|g{GRID}|{hw}|{idx}".encode()).hexdigest()[:8], 16)
    else:
        assert blk[3:] == f"d{D}g{GRID}" and blk[:3] in (("Q3R", "P3R") if REACH else ("Q3D", "P3D")), f"block {blk} vs d{D}g{GRID}, reach={REACH}"
        seeds = {"Q3D": P3D_DEV, "P3D": P3D_SEEDS, "Q3R": R3D_DEV, "P3R": R3D_SEEDS}[blk[:3]]
        assert seeds is not None, "confirmatory P3D seeds are set only in the pre-registration"
        tag = "p3r" if REACH else "p3d"                       # Study 3D-2 (reach) seeds never overlap Study 3D-1's
        nseed = int(hashlib.sha256(f"{tag}net|d{D}|g{GRID}|{hw}|{idx}".encode()).hexdigest()[:8], 16)
        rseed = int(hashlib.sha256(f"{tag}run|d{D}|g{GRID}|{hw}|{idx}".encode()).hexdigest()[:8], 16)
    Net3D.compat34 = compat(t)
    net = Net3D(hw, pat, arm, cfg, [rseed, seeds[1], nseed, seeds[0] + seeds[2]])
    r = net.run(); r.pop("arm32", None)
    row = dict(run=run_id(t), block=blk, hw=hw, pat=pat, arm=arm, cfg=cfg, idx=idx, **r)
    if not compat(t): row.update(dim=D)
    return row


# Study 3D-1 confirmatory cells (docs/PREREG_3D1.md): the 6 Pilot 1 cells plus the gated check with no offset (false alarms)
CFGS_3D1 = [("kg", "-|p00|base"), ("kg", "o0.044|p00|base"), ("kgMChN", "-|p10|base"), ("kgMChN", "o0.044|p10|base"),
            ("kgMChN", "o0.044F|p10|base"), ("kgMCa", "-|p10|base"), ("kgMCa", "o0.044|p10|base")]
NNET_3D1 = 32


def tasks_3d1(nnet=NNET_3D1):
    return [[f"P3Dd{D}g{GRID}", hw, "field", arm, cfg, i] for hw in HWS for (arm, cfg) in CFGS_3D1 for i in range(nnet)]


def tasks(prefix, nnet, mults=("base",)):
    return [[f"{prefix}d{D}g{GRID}", hw, "field", arm, cfg, i] for (hw, arm, cfg) in configs(mults) for i in range(nnet)]


if __name__ == "__main__":
    if sys.argv[1:2] in (["--write-pilot"], ["--write-3d1"]):
        ts = tasks("Q3D", int(sys.argv[3]) if len(sys.argv) > 3 else 2) if sys.argv[1] == "--write-pilot" else tasks_3d1()
        with open(sys.argv[2], "w") as f:
            for t in ts: f.write(json.dumps(t) + "\n")
        print(f"d{D} g{GRID}: wrote {len(ts)} tasks to {sys.argv[2]}")
