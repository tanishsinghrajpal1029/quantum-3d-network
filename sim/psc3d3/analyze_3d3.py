"""Study 3D-3 (king's-graph control) analysis, fixed in the pre-registration (docs/PREREG_3D3.md). Do not change after data
are read. Compares the new king's-graph runs (2D 32x32 with diagonals) with Study 3D-2's confirmatory runs (same code paths,
same platform, independent networks), read from frozen copies whose sha256 equal Study 3D-2's.

Usage (from sim/psc3d3):
  python3 analyze_3d3.py des_3d3_king32/runs.csv > analysis_3d3.txt
  python3 analyze_3d3.py --dry-run <king pilot or smoke csv(s)>          # only to test this script
"""
import glob, hashlib, os, sys
import numpy as np, pandas as pd
from scipy.stats import beta

H = os.path.dirname(os.path.abspath(__file__)); REF = os.path.join(H, "..", "reference")
S3D2 = {"d2g32": "c7ec6fbfeb9c4b4db13d79076626d31934ab0bd493a386a51fe897e217726f9d",
        "d3g10": "801a9552951f8f57a6a0d3be788e838446219e42950d9a224bce408c5feb1d73",
        "d2g37": "b569e80e92469bc403d0a903334b6c981daad91ebb123bd603dcfb7dfb12a880"}
ALPHA = 0.05; B = 20000; BOOT_SEED = 3003
HWS = ("fut97", "fut98", "fut99"); NNET, NHARM = 32, 8
LINKS = {"king": 3906, "d2g32": 1984, "d3g10": 2700, "d2g37": 2664}
NAME = {"king": "2D 32x32 + diagonals", "d2g32": "2D 32x32", "d3g10": "3D 10^3", "d2g37": "2D 37x37"}
GEO = {"fut97": 4.7 / 4.2, "fut98": 8.9 / 6.8, "fut99": 21.7 / 13.3}   # geometry-only 3D / king ratios (P3D-E15)


def cp_up(k, n, a=ALPHA):
    return 1.0 if n == 0 else (1.0 if k >= n else float(beta.ppf(1 - a, k + 1, n - k)))


def cp_lo(k, n, a=ALPHA):
    return 0.0 if k == 0 else float(beta.ppf(a, k, n - k + 1))


def boot(x, y, level, seed, ratio=False):
    r = np.random.default_rng(seed); x, y = np.asarray(x, float), np.asarray(y, float)
    bx = x[r.integers(0, len(x), (B, len(x)))].mean(1); by = y[r.integers(0, len(y), (B, len(y)))].mean(1)
    st = bx / by if ratio else bx - by; lo, hi = np.quantile(st, [(1 - level) / 2, (1 + level) / 2])
    return (x.mean() / y.mean() if ratio else x.mean() - y.mean()), lo, hi


def main(argv):
    dry = "--dry-run" in argv; files = [f for a in argv if a != "--dry-run" for f in glob.glob(a)]
    K = pd.concat([pd.read_csv(f) for f in files]).drop_duplicates("run")
    K = K[K.block.str.startswith("Q3K" if dry else "P3K")].copy(); K["lat"] = "king"
    refs = []
    for l, h in S3D2.items():
        p = os.path.join(REF, f"s3d2_{l}_runs.csv"); got = hashlib.sha256(open(p, "rb").read()).hexdigest()
        assert got == h, f"reference {p} does not match Study 3D-2 ({got[:12]})"
        d = pd.read_csv(p); d["lat"] = l; refs.append(d)
    df = pd.concat([K] + refs, ignore_index=True); df["served"] = df.qual / df.requests * df.share_servable
    out = []; P = lambda *a: out.append(" ".join(str(x) for x in a))
    P("STUDY 3D-3 (KING'S-GRAPH CONTROL) ANALYSIS" + ("  ***DRY RUN: NOT A RESULT***" if dry else ""))
    P("king runs per link level:", K.groupby("hw").size().to_dict(), "| Study 3D-2 references verified by sha256")
    if not dry:
        for hw, g in K.groupby("hw"): assert len(g) == 4 * NNET + NHARM, f"incomplete king cell {hw}: {len(g)}"
    sel = lambda lat, arm, cfg: df[(df.lat == lat) & (df.arm == arm) & (df.cfg == cfg)]

    P("\n== K1 (primary) dimension, not degree: 3D 10^3 serves more of uniform demand than the king's graph (kg -), every link level;"
      f" {1 - ALPHA / 3:.4f} two-sided bootstrap over networks")
    res = []
    for j, hw in enumerate(HWS):
        x = sel("d3g10", "kg", "-|p00|base"); x = x[x.hw == hw].served; y = sel("king", "kg", "-|p00|base"); y = y[y.hw == hw].served
        d, lo, hi = boot(x, y, 1 - ALPHA / 3, BOOT_SEED + j); r, rlo, rhi = boot(x, y, 0.95, BOOT_SEED + 50 + j, ratio=True)
        ok = lo > 0; res.append(ok)
        P(f"   {hw}: 3D {x.mean():.4f} vs king {y.mean():.4f}: diff {d:+.4f} [{lo:+.4f}, {hi:+.4f}]; ratio {r:.2f} [{rlo:.2f}, {rhi:.2f}]"
          f" (geometry-only {GEO[hw]:.2f}) -> {'PASS' if ok else 'FAIL'}")
    P(f"K1 VERDICT (all 3): {'PASS' if all(res) else 'FAIL'} ({sum(res)}/3)")

    P("\n== K2 (primary, safety on the king's graph) as Study 3D-2 R1: harmed networks bound <= 0.10 and bad-pair bound <= 0.01")
    ok_all = True
    for name, arm, cfgs, ucol, bcol, dcol in (("K2a gated, after a forced alarm", "kgMChN", ["o0.044F|p10|base"], "users_bad_post", "bad_after_alarm", "deliv_after_alarm"),
                                              ("K2b always-on margin, whole run", "kgMCa", ["-|p10|base", "o0.044|p10|base"], "users_bad_served", "bad", "delivered")):
        g = K[(K.arm == arm) & K.cfg.isin(cfgs)]; P(f"-- {name}")
        for hw, c in g.groupby("hw"):
            nets = c.groupby("idx")[ucol].max(); k, n = int((nets > 0).sum()), len(nets); kb, nb = int(c[bcol].sum()), int(c[dcol].sum())
            ok = cp_up(k, n) <= 0.10 and cp_up(kb, nb) <= 0.01; ok_all &= ok
            P(f"   {hw}: harmed networks {k}/{n} (bound {cp_up(k, n):.3f}); bad pairs {kb}/{nb} (bound {cp_up(kb, nb):.2e}) -> {'PASS' if ok else 'FAIL'}")
    P(f"K2 VERDICT: {'PASS' if ok_all else 'FAIL'}")

    P(f"\n== K3 (secondary) degree helps in 2D: king minus 2D 32x32 grid (kg -), every link level; {1 - ALPHA / 3:.4f} two-sided bootstrap")
    for j, hw in enumerate(HWS):
        x = sel("king", "kg", "-|p00|base"); x = x[x.hw == hw].served; y = sel("d2g32", "kg", "-|p00|base"); y = y[y.hw == hw].served
        d, lo, hi = boot(x, y, 1 - ALPHA / 3, BOOT_SEED + 100 + j)
        P(f"   {hw}: king {x.mean():.4f} vs grid {y.mean():.4f}: diff {d:+.4f} [{lo:+.4f}, {hi:+.4f}] -> {'PASS' if lo > 0 else 'FAIL'}")

    P(f"\n== K4 (secondary) the 3D lead over the king's graph survives the always-on margin (kgMCa -); {1 - ALPHA / 3:.4f} two-sided bootstrap")
    for j, hw in enumerate(HWS):
        x = sel("d3g10", "kgMCa", "-|p10|base"); x = x[x.hw == hw].served; y = sel("king", "kgMCa", "-|p10|base"); y = y[y.hw == hw].served
        d, lo, hi = boot(x, y, 1 - ALPHA / 3, BOOT_SEED + 200 + j)
        P(f"   {hw}: 3D {x.mean():.4f} vs king {y.mean():.4f}: diff {d:+.4f} [{lo:+.4f}, {hi:+.4f}] -> {'PASS' if lo > 0 else 'FAIL'}")

    P("\n== S1 (prediction) king's graph, no check, offset 0.044 harms > 10% of served users (8 networks per link level)")
    for hw, c in K[(K.arm == "kg") & (K.cfg == "o0.044|p00|base")].groupby("hw"):
        f = c.users_bad_served.sum() / max(c.users_served.sum(), 1); P(f"   {hw}: {f:.3f} -> {'PASS' if f > 0.10 else 'FAIL'}")
    P("\n== S2 (falsification) certificate on the king's graph, kg -, 96 networks: FAIL only if the CP95 lower bound > 0.05")
    c = K[(K.arm == "kg") & (K.cfg == "-|p00|base")]
    for tag in ("p10", "p20"):
        k, n = int(c[f"{tag}_viol"].sum()), len(c)
        P(f"   {tag}: {k}/{n} (lower {cp_lo(k, n):.3f}, upper {cp_up(k, n):.3f}) -> {'FAIL' if cp_lo(k, n) > 0.05 else 'PASS'}")

    P("\n== D1 (descriptive) served share by lattice, arm and link level; links; served share per 1,000 links")
    t = df.pivot_table(index=["hw", "arm", "cfg"], columns="lat", values="served", aggfunc="mean")[["d2g32", "d2g37", "king", "d3g10"]]
    P(t.rename(columns=NAME).round(4).to_string())
    g = df[(df.arm == "kg") & (df.cfg == "-|p00|base")].groupby(["hw", "lat"]).served.mean().unstack()[["d2g32", "d2g37", "king", "d3g10"]]
    P("\nkg -, served share per 1,000 links:"); P((g / pd.Series(LINKS) * 1000).dropna(axis=1).rename(columns=NAME).round(4).to_string())
    P("\n== D2 (descriptive) king's graph, kg -: success per servable request by hop, paths per pair, U_max, servable share")
    g = K[(K.arm == "kg") & (K.cfg == "-|p00|base")].copy()
    for h in range(1, 9): g[f"s{h}"] = g[f"h{h}_deliv"] / (g.requests * g[f"h{h}_users"] / g.users_all)
    P(g.groupby("hw")[[f"s{h}" for h in range(1, 9)] + ["umax", "share_servable", "p10_F"]].mean().round(3).to_string())
    print("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1:])
