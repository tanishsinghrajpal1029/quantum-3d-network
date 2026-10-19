"""Study 3D-2 (reach) analysis, fixed in the pre-registration (docs/PREREG_3D2.md). Do not change after data are read.

Usage:
  python3 analyze_3d2.py des_3d2_d2g32/runs.csv des_3d2_d3g10/runs.csv des_3d2_d2g37/runs.csv > analysis_3d2.txt
  python3 analyze_3d2.py --dry-run "../out/pilot_reach/mac_*_w*.csv"     # pilot data (Q3R blocks), only to test this script
Unit of replication: the network (lattice, link level, idx). Outcome "served share" of a run: good deliveries per servable
request x the servable share of all ordered pairs = the share of uniform all-pairs demand served above tau (requests beyond
the service radius use no resources).
"""
import glob, sys
import numpy as np, pandas as pd
from scipy.stats import beta

ALPHA = 0.05; B = 20000; BOOT_SEED = 3002
LAT = {"d2g32": "2D 32x32", "d3g10": "3D 10^3", "d2g37": "2D 37x37"}
HWS = ("fut97", "fut98", "fut99")
PRED = {"fut97": 2.1, "fut98": 2.5, "fut99": 2.8}            # analytic 3D / 2D 32x32 ratios with the guard (P3D-E10)
NNET, NHARM = 32, 8


def cp_up(k, n, a=ALPHA):
    return 1.0 if n == 0 else (1.0 if k >= n else float(beta.ppf(1 - a, k + 1, n - k)))


def cp_lo(k, n, a=ALPHA):
    return 0.0 if k == 0 else float(beta.ppf(a, k, n - k + 1))


def boot_diff(x, y, level, seed):
    r = np.random.default_rng(seed); x, y = np.asarray(x, float), np.asarray(y, float)
    bx = x[r.integers(0, len(x), (B, len(x)))].mean(1); by = y[r.integers(0, len(y), (B, len(y)))].mean(1)
    lo, hi = np.quantile(bx - by, [(1 - level) / 2, (1 + level) / 2]); return x.mean() - y.mean(), lo, hi


def boot_ratio(x, y, level, seed):
    r = np.random.default_rng(seed); x, y = np.asarray(x, float), np.asarray(y, float)
    bx = x[r.integers(0, len(x), (B, len(x)))].mean(1); by = y[r.integers(0, len(y), (B, len(y)))].mean(1)
    lo, hi = np.quantile(bx / by, [(1 - level) / 2, (1 + level) / 2]); return x.mean() / y.mean(), lo, hi


def main(argv):
    dry = "--dry-run" in argv; files = [f for a in argv if a != "--dry-run" for f in glob.glob(a)]
    df = pd.concat([pd.read_csv(f) for f in files]).drop_duplicates("run")
    pre = "Q3R" if dry else "P3R"; df = df[df.block.str.startswith(pre)].copy(); df["lat"] = df.block.str[3:]
    df["served"] = df.qual / df.requests * df.share_servable
    out = []; P = lambda *a: out.append(" ".join(str(x) for x in a))
    P("STUDY 3D-2 (REACH) ANALYSIS" + ("  ***DRY RUN ON PILOT DATA: NOT A RESULT***" if dry else ""))
    P("runs per lattice x link level:", df.groupby(["lat", "hw"]).size().to_dict())
    if not dry:
        for (l, hw), g in df.groupby(["lat", "hw"]):
            assert len(g) == 4 * NNET + NHARM, f"incomplete cell {l} {hw}: {len(g)} runs"
    sel = lambda arm, cfg: df[(df.arm == arm) & (df.cfg == cfg)]

    # ---------------- R1 (primary): safety at reach (3D primary; 2D replication)
    P("\n== R1 safety (network level; one-sided CP95). Network harmed if any run in the arm harms a user")
    R1 = {}
    for name, arm, cfgs, ucol, bcol, dcol in (
            ("R1a gated check after the alarm (Theorem 2; forced alarm)", "kgMChN", ["o0.044F|p10|base"], "users_bad_post", "bad_after_alarm", "deliv_after_alarm"),
            ("R1b always-on margin, whole run (Corollary 3)", "kgMCa", ["-|p10|base", "o0.044|p10|base"], "users_bad_served", "bad", "delivered")):
        g = df[(df.arm == arm) & df.cfg.isin(cfgs)]; P(f"-- {name}")
        for (l, hw), c in g.groupby(["lat", "hw"]):
            nets = c.groupby("idx")[ucol].max(); k, n = int((nets > 0).sum()), len(nets)
            kb, nb = int(c[bcol].sum()), int(c[dcol].sum())
            ok = cp_up(k, n) <= 0.10 and cp_up(kb, nb) <= 0.01; R1[(name[:3], l, hw)] = ok
            P(f"   {LAT[l]:9s} {hw}: harmed networks {k}/{n} (bound {cp_up(k, n):.3f}, bar 0.10); bad pairs {kb}/{nb} "
              f"(bound {cp_up(kb, nb):.2e}, bar 0.01) -> {'PASS' if ok else 'FAIL'}")
    v = all(R1.get((t, "d3g10", hw), False) for t in ("R1a", "R1b") for hw in HWS)
    P(f"R1 VERDICT (3D 10^3, both parts, all three link levels): {'PASS' if v else 'FAIL'}")

    # ---------------- R2 (primary): 3D serves a larger share of uniform demand than both 2D lattices, at every link level
    lev = 1 - ALPHA / 6
    P(f"\n== R2 served share of uniform demand, no check, no offset (kg -); 3D minus 2D; {lev:.4f} two-sided bootstrap over networks")
    g = sel("kg", "-|p00|base"); res = []
    for j, hw in enumerate(HWS):
        x = g[(g.lat == "d3g10") & (g.hw == hw)].served
        for k_, ref in enumerate(("d2g32", "d2g37")):
            y = g[(g.lat == ref) & (g.hw == hw)].served
            d, lo, hi = boot_diff(x, y, lev, BOOT_SEED + 10 * j + k_); ok = lo > 0; res.append(ok)
            P(f"   {hw}: 3D {x.mean():.4f} vs {LAT[ref]} {y.mean():.4f}: diff {d:+.4f} [{lo:+.4f}, {hi:+.4f}] -> {'PASS' if ok else 'FAIL'}")
    P(f"R2 VERDICT (all 6 comparisons): {'PASS' if all(res) else 'FAIL'} ({sum(res)}/6)")

    # ---------------- R3 (secondary prediction): size of the gain
    P("\n== R3 (prediction) the 3D / 2D 32x32 ratio of served share is at least 1.5 at every link level (95% bootstrap lower bound);"
      " analytic ratios 2.1 / 2.5 / 2.8 shown for comparison")
    for j, hw in enumerate(HWS):
        x = g[(g.lat == "d3g10") & (g.hw == hw)].served; y = g[(g.lat == "d2g32") & (g.hw == hw)].served
        r, lo, hi = boot_ratio(x, y, 0.90, BOOT_SEED + 100 + j)
        P(f"   {hw}: ratio {r:.2f} [{lo:.2f}, {hi:.2f}] (analytic {PRED[hw]}) -> {'PASS' if lo >= 1.5 else 'FAIL'}")

    # ---------------- R4 (secondary): the 3D advantage survives the always-on margin
    lev4 = 1 - ALPHA / 3
    P(f"\n== R4 the always-on margin (kgMCa -) keeps a 3D advantage over 2D 32x32; {lev4:.4f} two-sided bootstrap")
    g4 = sel("kgMCa", "-|p10|base")
    for j, hw in enumerate(HWS):
        x = g4[(g4.lat == "d3g10") & (g4.hw == hw)].served; y = g4[(g4.lat == "d2g32") & (g4.hw == hw)].served
        d, lo, hi = boot_diff(x, y, lev4, BOOT_SEED + 200 + j)
        P(f"   {hw}: 3D {x.mean():.4f} vs 2D {y.mean():.4f}: diff {d:+.4f} [{lo:+.4f}, {hi:+.4f}] -> {'PASS' if lo > 0 else 'FAIL'}")

    # ---------------- S1, S2 (predictions / falsification)
    P("\n== S1 (prediction) with no check, offset 0.044 harms > 10% of served users (8 networks per cell)")
    for (l, hw), c in sel("kg", "o0.044|p00|base").groupby(["lat", "hw"]):
        f = c.users_bad_served.sum() / max(c.users_served.sum(), 1); P(f"   {LAT[l]:9s} {hw}: {f:.3f} -> {'PASS' if f > 0.10 else 'FAIL'}")
    P("\n== S2 (falsification) certificate validity, kg - (no feedback), 96 networks per lattice: FAIL only if the CP95 LOWER bound > 0.05")
    for l, c in sel("kg", "-|p00|base").groupby("lat"):
        for tag in ("p10", "p20"):
            k, n = int(c[f"{tag}_viol"].sum()), len(c)
            P(f"   {LAT[l]:9s} {tag}: {k}/{n} (lower {cp_lo(k, n):.3f}, upper {cp_up(k, n):.3f}) -> {'FAIL' if cp_lo(k, n) > 0.05 else 'PASS'}")

    # ---------------- descriptive
    P("\n== D1 (descriptive) served share by arm, lattice and link level (mean over networks)")
    P(df.pivot_table(index=["hw", "arm", "cfg"], columns="lat", values="served", aggfunc="mean").round(4).to_string())
    P("\n== D2 (descriptive) kg -: success per servable request by hop, U_max, servable share, kept fidelity")
    g = sel("kg", "-|p00|base").copy()
    for h in range(1, 9):
        if f"h{h}_users" in g: g[f"s{h}"] = g[f"h{h}_deliv"] / (g.requests * g[f"h{h}_users"] / g.users_all)
    cols = [c for c in [f"s{h}" for h in range(1, 9)] if c in g] + ["umax", "share_servable", "p10_F"]
    P(g.groupby(["hw", "lat"])[cols].mean().round(3).to_string())
    print("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1:])
