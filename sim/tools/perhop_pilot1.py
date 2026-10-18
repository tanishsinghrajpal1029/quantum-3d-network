"""Exposure-adjusted per-hop delivery (exploratory). Requests pick a user uniformly, so expected requests at hop h are
requests * users_h / users_all; success_h = deliveries at hop h / that. Removes the dilution from different user counts."""
import glob, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import pandas as pd, load_runs
df = pd.concat([load_runs.load(f) for f in sorted(glob.glob(os.path.join(H, "..", "out", "pilot1", "mac_*_w*.csv")))])
df["lat"] = df.block.str.replace("Q3D", "").map({"d2g11": "2D 11x11", "d2g13": "2D 13x13", "d3g5": "3D 5^3"})
rows = []
for h in (1, 2, 3):
    exp_req = df.requests * df[f"h{h}_users"] / df.users_all
    df[f"succ_h{h}"] = df[f"h{h}_deliv"] / exp_req
    df[f"badfrac_h{h}"] = df[f"h{h}_bad"] / df[f"h{h}_deliv"].clip(lower=1)
out = []
for hw in ("ion2020", "ionproj"):
    for arm, cfg in (("kg", "-|p00|base"), ("kgMCa", "-|p10|base"), ("kg", "o0.044|p00|base"), ("kgMCa", "o0.044|p10|base")):
        g = df[(df.hw == hw) & (df.arm == arm) & (df.cfg == cfg)]
        cols = [c for c in ("succ_h1", "succ_h2", "succ_h3", "badfrac_h2", "badfrac_h3") if g[c].notna().any()]
        t = g.groupby("lat")[cols].mean().T.round(3)
        out.append(f"== {hw} | {arm} {cfg}\n{t.to_string()}\n")
txt = "\n".join(out); print(txt)
open(os.path.join(H, "..", "evidence", "pilot1_perhop.txt"), "w").write("EXPLORATORY (2 networks per cell)\n" + txt)
