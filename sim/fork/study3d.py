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
g1.GRID_N, g1.GRID_D = GRID, D                            # must precede every import that builds the lattice (corr_net)
import study32 as s32
import corr_net as cn1
assert cn1.NL == D * GRID ** (D - 1) * (GRID - 1), (cn1.NL, D, GRID)
assert len(cn1.NODES) == GRID ** D

SEEDS = (19341, 19342, 19343, 19344); DEV = (20341, 20342, 20343, 20344)    # Study 34 (compat); P3D blocks set their own below
P3D_SEEDS = (19351, 19352, 19353, 19354)                 # Study 3D-1 confirmatory (docs/PREREG_3D1.md); pilots use P3D_DEV
P3D_DEV = (30341, 30342, 30343, 30344)
HWS = ("ion2020", "ionproj")
HMAX = 3                                                  # per-hop columns h1..h3 always written


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
        if not s.compat34:                                         # per-hop breakdown (read-only: no random draws)
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
        assert blk == f"P3Dd{D}g{GRID}" or blk == f"Q3Dd{D}g{GRID}", f"block {blk} != lattice d{D}g{GRID}"
        seeds = P3D_DEV if blk.startswith("Q3D") else P3D_SEEDS
        assert seeds is not None, "confirmatory P3D seeds are set only in the pre-registration"
        nseed = int(hashlib.sha256(f"p3dnet|d{D}|g{GRID}|{hw}|{idx}".encode()).hexdigest()[:8], 16)
        rseed = int(hashlib.sha256(f"p3drun|d{D}|g{GRID}|{hw}|{idx}".encode()).hexdigest()[:8], 16)
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
