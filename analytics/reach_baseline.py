"""P3D-E8 (EXPLORATORY, analytic + small Monte Carlo; no network simulation): the REACH question.
With requests between uniformly random node pairs (any hop distance), how many can be served above tau on 2D vs 3D lattices,
and how much of that survives the per-user guard, whose per-link level alpha/U_max shrinks as U_max (links a user can be routed
over) grows with path length, faster in 3D?

Physics: the paper's Pauli-transfer model (upstream ptm_model.delivered_F): two chains of h Werner links, exponential heralding
waits at rate (1-rho)R per link, memory dephasing T2, gate error e, one DEJMPS round. Homogeneous links at the fleet mean
lambda = (4F0-1)/3 - AMP/2 (AMP = 0.02, as the simulator's mean shift). Chain-timing averaged over 400 draws.
Guard (approximate): per-link lower bound lambda_lo = lambda - w, w = (2/r) sqrt(p(1-p)) sqrt((4/n) ln(sqrt2 / a)) (normal-mixture
confidence sequence with its free parameter matched to n), a = alpha / U_max, alpha = 0.05, n = calibration pairs per link after
E epochs (rho R T per epoch). The guard serves hop h if the mean predicted fidelity from lambda_lo is >= tau. This ignores link
spread, drift and the risk controller, so it is an optimistic, upper-bound-style guide, not a result.
Usage: python3 reach_baseline.py [upstream dir]"""
import itertools, math, os, sys
import numpy as np
UP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sim", "upstream")
sys.path.insert(0, UP)
import ptm_model as ptm

RHO, T, AMP, ALPHA, TAU, E_EP = 0.3, 100.0, 0.02, 0.05, 0.9, 10
PRESETS = {"ion2020": dict(F0=0.940, R=182.0, T2=1.0, q=0.001, e=0.005), "ionproj": dict(F0=0.970, R=200.0, T2=1.0, q=0.001, e=0.003),
           "ionfut": dict(F0=0.990, R=1000.0, T2=1.0, q=0.001, e=0.003)}
# link-quality sweep (P3D-E10): ionfut's rate, memory and gates, with link fidelity 0.97 / 0.98 / 0.99
SWEEP = {f"fut{int(round(F * 100))}": dict(F0=F, R=1000.0, T2=1.0, q=0.001, e=0.003) for F in (0.97, 0.98, 0.99)}
if os.environ.get("REACH_SWEEP"): PRESETS = SWEEP
rng = np.random.default_rng(8)


def F_path(lam, h, P, M=400):
    rt = (1 - RHO) * P["R"]; out = []
    for _ in range(M):
        h1 = rng.exponential(1 / rt, h); d1 = h1.max(); h2 = d1 + rng.exponential(1 / rt, h); d2 = h2.max()
        out.append(float(ptm.delivered_F(np.full((1, h), lam), d1 - h1, d2 - h2, d2 - d1, P["e"], np.inf, P["T2"])[0]))
    return float(np.mean(out))


def width(lam, P, U):
    r = (1 - 2 * P["q"]) ** 2; p = (1 + r * lam) / 2; n = RHO * P["R"] * T * E_EP
    return (2 / r) * math.sqrt(p * (1 - p)) * math.sqrt((4 / n) * math.log(math.sqrt(2) * U / ALPHA))


def union_links(v):                       # links on some shortest path for offset vector v (|v_i| per axis)
    a = [abs(x) for x in v]; return sum(a[ax] * math.prod(a[j] + 1 for j in range(len(a)) if j != ax) for ax in range(len(a)))


def hop_stats(n, d):
    """for each hop h: number of ordered node pairs at distance h, and max U over those pairs."""
    cnt, umax = {}, {}
    for v in itertools.product(range(-(n - 1), n), repeat=d):
        h = sum(abs(x) for x in v)
        if h == 0: continue
        pairs = math.prod(n - abs(x) for x in v)
        cnt[h] = cnt.get(h, 0) + pairs; umax[h] = max(umax.get(h, 0), union_links(v))
    return cnt, umax


LATS = {"2D 32x32 (1,024 nodes)": (32, 2), "3D 10^3 (1,000 nodes)": (10, 3), "2D 37x37 (2,664 links, ~ 3D's 2,700)": (37, 2)}
if __name__ == "__main__":
    print(__doc__.split("Usage")[0])
    HS = list(range(1, 31))
    for name, P in PRESETS.items():
        lam = (4 * P["F0"] - 1) / 3 - AMP / 2
        Ft = {h: F_path(lam, h, P) for h in HS}
        htrue = max([h for h in HS if Ft[h] >= TAU], default=0)
        print(f"== {name}: link F0 {P['F0']}, R {P['R']}/s; true fidelity by hop: " + ", ".join(f"{h}:{Ft[h]:.3f}" for h in HS[:12]))
        print(f"   longest hop with true F >= {TAU}: {htrue}")
        for lname, (n, d) in LATS.items():
            cnt, um = hop_stats(n, d); tot = sum(cnt.values())
            # guard: serve hops 1..H with U_max = max U over those hops; largest H that passes at every h <= H
            Hg = 0
            for H in range(1, htrue + 1):
                U = max(um[h] for h in range(1, H + 1) if h in um)
                lo = lam - width(lam, P, U)
                if F_path(lo, H, P, 300) >= TAU: Hg = H      # fidelity falls with hop count, so hop H is the binding one
                else: break
            Uhg = max([um[h] for h in range(1, Hg + 1) if h in um], default=0)
            s_true = sum(c for h, c in cnt.items() if h <= htrue) / tot; s_g = sum(c for h, c in cnt.items() if h <= Hg) / tot
            print(f"   {lname:38s} mean hop {sum(h * c for h, c in cnt.items()) / tot:5.1f} | servable share (true model) {s_true:6.1%}"
                  f" | with guard: max hop {Hg:2d}, U_max {Uhg:5d}, share {s_g:6.1%}")
