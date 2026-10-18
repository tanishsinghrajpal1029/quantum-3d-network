"""Study 3D-1 analysis, fixed in the pre-registration (docs/PREREG_3D1.md). Do not change after data are read.

Usage:
  python3 analyze_3d1.py des_3d1_d2g11/runs.csv des_3d1_d2g13/runs.csv des_3d1_d3g5/runs.csv > analysis_3d1.txt
  python3 analyze_3d1.py --dry-run ../out/pilot1/mac_*_w*.csv      # pilot data (Q3D blocks), only to test this script
Unit of replication: the network (lattice, hardware, idx). Runs of one network share its links and seeds.
"""
import glob, os, sys
import numpy as np, pandas as pd
from scipy.stats import beta
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import load_runs

ALPHA = 0.05; B = 20000; BOOT_SEED = 3001
LAT = {"d2g11": "2D 11x11", "d2g13": "2D 13x13", "d3g5": "3D 5^3"}
LMAX = {"ion2020": 2, "ionproj": 3}
NNET = 32


def cp_up(k, n, a=ALPHA):                       # one-sided Clopper-Pearson upper bound (0/32 -> 0.089, as in the paper)
    return 1.0 if n == 0 else (1.0 if k >= n else float(beta.ppf(1 - a, k + 1, n - k)))


def cp_lo(k, n, a=ALPHA):                       # one-sided Clopper-Pearson lower bound
    return 0.0 if k == 0 else float(beta.ppf(a, k, n - k + 1))


def boot_diff(x, y, level, seed):               # mean(x) - mean(y), independent networks, percentile interval
    r = np.random.default_rng(seed); x, y = np.asarray(x, float), np.asarray(y, float)
    bx = x[r.integers(0, len(x), (B, len(x)))].mean(1); by = y[r.integers(0, len(y), (B, len(y)))].mean(1)
    lo, hi = np.quantile(bx - by, [(1 - level) / 2, (1 + level) / 2]); return x.mean() - y.mean(), lo, hi


def boot_mean(x, level, seed):
    r = np.random.default_rng(seed); x = np.asarray(x, float); b = x[r.integers(0, len(x), (B, len(x)))].mean(1)
    lo, hi = np.quantile(b, [(1 - level) / 2, (1 + level) / 2]); return x.mean(), lo, hi


def main(argv):
    dry = "--dry-run" in argv; files = [f for a in argv if a != "--dry-run" for f in glob.glob(a)]
    df = pd.concat([load_runs.load(f) for f in files]).drop_duplicates("run")
    pre = "Q3D" if dry else "P3D"; df = df[df.block.str.startswith(pre)].copy()
    df["lat"] = df.block.str[3:]
    out = []; P = lambda *a: out.append(" ".join(str(x) for x in a))
    P("STUDY 3D-1 ANALYSIS" + ("  ***DRY RUN ON PILOT DATA: NOT A RESULT***" if dry else ""))
    P("runs per lattice x hardware:", df.groupby(["lat", "hw"]).size().to_dict())
    if not dry:
        for (l, hw), g in df.groupby(["lat", "hw"]):
            assert len(g) == 7 * NNET and g.idx.nunique() == NNET, f"incomplete cell {l} {hw}: {len(g)} runs"
    for h in (1, 2, 3):
        df[f"s{h}"] = df[f"h{h}_deliv"] / (df.requests * df[f"h{h}_users"] / df.users_all)
    df["sL"] = [r[f"s{LMAX[r.hw]}"] for _, r in df.iterrows()]
    sel = lambda arm, cfgs: df[(df.arm == arm) & df.cfg.isin(cfgs)]

    # ---------------- H1 (primary on 3D; replication on 2D): safety guarantees carry over
    P("\n== H1 safety (network level: a network is harmed if any of its runs in the arm harms a user; bound = one-sided CP95)")
    H1 = {}
    for name, arm, cfgs, ucol, bcol, dcol in (
            ("H1a gated check, after the alarm (Theorem 2)", "kgMChN", ["o0.044|p10|base", "o0.044F|p10|base"], "users_bad_post", "bad_after_alarm", "deliv_after_alarm"),
            ("H1b always-on margin, whole run (Corollary 3)", "kgMCa", ["-|p10|base", "o0.044|p10|base"], "users_bad_served", "bad", "delivered")):
        g = sel(arm, cfgs); P(f"-- {name}")
        for (l, hw), c in g.groupby(["lat", "hw"]):
            nets = c.groupby("idx")[ucol].max(); k, n = int((nets > 0).sum()), len(nets)
            kb, nb = int(c[bcol].sum()), int(c[dcol].sum())
            ok = cp_up(k, n) <= 0.10 and cp_up(kb, nb) <= 0.01
            H1[(name[:3], l, hw)] = ok
            P(f"   {LAT[l]:9s} {hw}: harmed networks {k}/{n} (bound {cp_up(k, n):.3f}, bar 0.10); bad pairs {kb}/{nb} "
              f"(bound {cp_up(kb, nb):.2e}, bar 0.01) -> {'PASS' if ok else 'FAIL'}")
    v = all(H1[(t, "d3g5", hw)] for t in ("H1a", "H1b") for hw in LMAX if (t, "d3g5", hw) in H1)
    P(f"H1 VERDICT (3D 5^3, both parts, both hardware): {'PASS' if v else 'FAIL'}")

    # ---------------- H2 (primary): 3D serves more of the longest requests than both 2D lattices
    lev = 1 - ALPHA / 4
    P(f"\n== H2 longest-hop success per request, no check, no offset (kg -); 3D minus 2D, {lev:.4f} two-sided bootstrap over networks")
    g = sel("kg", ["-|p00|base"]); res = []
    for j, hw in enumerate(LMAX):
        x = g[(g.lat == "d3g5") & (g.hw == hw)].sL
        for k_, ref in enumerate(("d2g11", "d2g13")):
            y = g[(g.lat == ref) & (g.hw == hw)].sL
            d, lo, hi = boot_diff(x, y, lev, BOOT_SEED + 10 * j + k_); ok = lo > 0; res.append(ok)
            P(f"   {hw} (hop {LMAX[hw]}): 3D {x.mean():.3f} vs {LAT[ref]} {y.mean():.3f}: diff {d:+.3f} [{lo:+.3f}, {hi:+.3f}] -> {'PASS' if ok else 'FAIL'}")
    P(f"H2 VERDICT (all 4 comparisons): {'PASS' if all(res) else 'FAIL'} ({sum(res)}/4)")

    # ---------------- H3 (secondary, equivalence): delivered fidelity changes by less than 0.01
    P("\n== H3 mean kept fidelity (p10_F), kg -; 3D minus 2D 11x11, 90% bootstrap (TOST at 5%), margin +-0.01")
    for j, hw in enumerate(LMAX):
        x = g[(g.lat == "d3g5") & (g.hw == hw)].p10_F; y = g[(g.lat == "d2g11") & (g.hw == hw)].p10_F
        d, lo, hi = boot_diff(x, y, 0.90, BOOT_SEED + 100 + j); ok = lo > -0.01 and hi < 0.01
        P(f"   {hw}: 3D {x.mean():.4f} vs 2D {y.mean():.4f}: diff {d:+.4f} [{lo:+.4f}, {hi:+.4f}] -> {'PASS' if ok else 'FAIL'}")

    # ---------------- Secondary predictions and descriptive results
    P("\n== S1 (prediction) detection carries over: alarm rate, gated check, offset 0.044; |3D - 2D 11x11| <= 0.15")
    g = sel("kgMChN", ["o0.044|p10|base"])
    for hw in LMAX:
        a3 = (g[(g.lat == "d3g5") & (g.hw == hw)].alarms > 0).mean(); a2 = (g[(g.lat == "d2g11") & (g.hw == hw)].alarms > 0).mean()
        a13 = (g[(g.lat == "d2g13") & (g.hw == hw)].alarms > 0).mean()
        P(f"   {hw}: 3D {a3:.3f}, 2D 11x11 {a2:.3f}, 2D 13x13 {a13:.3f} -> {'PASS' if abs(a3 - a2) <= 0.15 else 'FAIL'}")
    P("\n== S2 (prediction) the test can tell rules apart: with no check, offset 0.044 harms > 10% of served users (every lattice, hardware)")
    g = sel("kg", ["o0.044|p00|base"])
    for (l, hw), c in g.groupby(["lat", "hw"]):
        f = c.users_bad_served.sum() / c.users_served.sum(); P(f"   {LAT[l]:9s} {hw}: {f:.3f} -> {'PASS' if f > 0.10 else 'FAIL'}")
    P("\n== S3 (falsification test) certificate validity, no feedback (kg -, 64 networks per lattice): the certificate allows at most")
    P("   5% violating runs; FAIL only if the one-sided CP95 LOWER bound exceeds 0.05 (evidence of excess violations)")
    g = sel("kg", ["-|p00|base"])
    for l, c in g.groupby("lat"):
        for tag in ("p10", "p20"):
            k, n = int(c[f"{tag}_viol"].sum()), len(c); lo = cp_lo(k, n)
            P(f"   {LAT[l]:9s} {tag}: {k}/{n} (lower {lo:.3f}, upper {cp_up(k, n):.3f}) -> {'FAIL' if lo > 0.05 else 'PASS'}")
    P("   all 7 cells, runs (descriptive; runs of one network share test randomness, so they are not independent):")
    for l, c in df.groupby("lat"):
        P(f"   {LAT[l]:9s} " + "; ".join(f"{t}: {int(c[f'{t}_viol'].sum())}/{len(c)} runs, {int((c.groupby(['hw', 'idx'])[f'{t}_viol'].max() > 0).sum())}/{c.groupby(['hw', 'idx']).ngroups} networks" for t in ("p10", "p20")))
    P("\n== D1 (descriptive) false alarms: gated check with no offset, share of runs with an alarm")
    g = sel("kgMChN", ["-|p10|base"])
    for (l, hw), c in g.groupby(["lat", "hw"]):
        k = int((c.alarms > 0).sum()); P(f"   {LAT[l]:9s} {hw}: {k}/{len(c)} (bound {cp_up(k, len(c)):.3f})")
    P("\n== D2 (descriptive) cost of the always-on margin: longest-hop success kept, kgMCa - / kg - (same network), 95% bootstrap")
    a = sel("kgMCa", ["-|p10|base"]).set_index(["lat", "hw", "idx"]).sL; b = sel("kg", ["-|p00|base"]).set_index(["lat", "hw", "idx"]).sL
    ratio = (a / b).dropna()
    for j, ((l, hw), r) in enumerate(ratio.groupby(level=[0, 1])):
        m, lo, hi = boot_mean(r.values, 0.95, BOOT_SEED + 200 + j); P(f"   {LAT[l]:9s} {hw}: {m:.3f} [{lo:.3f}, {hi:.3f}]")
    P("\n== D3 (descriptive) every hop and lattice, kg -: success per request, served share, route choices, U_max")
    g = sel("kg", ["-|p00|base"])
    cols = ["s1", "s2", "s3", "h2_paths_mean", "h3_paths_mean", "umax", "users_all", "p10_F"]
    P(g.groupby(["hw", "lat"])[cols].mean().round(3).to_string())
    P("\n== D4 (descriptive) matched links: 2D 13x13 minus 2D 11x11, longest-hop success (95% bootstrap)")
    for j, hw in enumerate(LMAX):
        x = g[(g.lat == "d2g13") & (g.hw == hw)].sL; y = g[(g.lat == "d2g11") & (g.hw == hw)].sL
        d, lo, hi = boot_diff(x, y, 0.95, BOOT_SEED + 300 + j); P(f"   {hw}: {d:+.3f} [{lo:+.3f}, {hi:+.3f}]")
    print("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1:])
