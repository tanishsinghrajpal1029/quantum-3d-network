"""Summarise Pilot 1 (exploratory). Means over the 2 networks per cell; no intervals (n = 2 carries no inference)."""
import glob, os, sys
import pandas as pd
H = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(H, "..", "out", "pilot1")
sys.path.insert(0, H); import load_runs
PAT = sys.argv[1] if len(sys.argv) > 1 else "mac_*_w*.csv"          # one platform only (see P3D-E4)
fs = sorted(glob.glob(os.path.join(D, PAT)))
df = pd.concat([load_runs.load(f) for f in fs]).drop_duplicates("run")
df["lattice"] = df.block.str.replace("Q3D", "")
LAB = {"d2g11": "2D 11x11 (nodes)", "d2g13": "2D 13x13 (links)", "d3g5": "3D 5^3"}
df["lat"] = df.lattice.map(LAB)
df["cell"] = df.arm + " " + df.cfg.str.replace("|base", "", regex=False)
df["serve_share"] = df.users_served / df.users_all
df["oracle_share"] = df.oracle_qual / df.requests
df["deliv_share"] = df.delivered / df.requests
df["block_rate"] = df.guard_blocks / df.requests
df["bad_rate"] = df.bad / df.delivered.clip(lower=1)
df["harmed_served"] = df.users_bad_served / df.users_served.clip(lower=1)
for h in (1, 2, 3):
    if f"h{h}_users" in df: df[f"h{h}_serve"] = df[f"h{h}_served"] / df[f"h{h}_users"].clip(lower=1)
out = []
P = lambda *a: out.append(" ".join(str(x) for x in a))
P(f"Pilot 1 summary: {len(df)} runs ({', '.join(f'{k}: {v}' for k, v in df.lattice.value_counts().sort_index().items())}); means over networks")
P("EXPLORATORY: dev seeds, 2 networks per cell. Not evidence for any hypothesis.\n")
cols = ["users_all", "umax", "serve_share", "h1_serve", "h2_serve", "h3_serve", "h2_paths_mean", "h3_paths_mean", "oracle_share",
        "deliv_share", "block_rate", "p10_F", "bad_rate", "harmed_served", "alarms", "first_alarm_ep", "bad_after_alarm", "users_bad_post", "elapsed_s"]
for hw in ("ion2020", "ionproj"):
    for cell in df.cell.drop_duplicates():
        g = df[(df.hw == hw) & (df.cell == cell)]
        if g.empty: continue
        t = g.groupby("lat")[[c for c in cols if c in g]].mean().T
        t = t[[LAB[k] for k in ("d2g11", "d2g13", "d3g5") if LAB[k] in t.columns]]
        P(f"== {hw} | {cell}"); P(t.round(3).to_string()); P("")
txt = "\n".join(out); print(txt)
ev = os.path.join(H, "..", "evidence"); os.makedirs(ev, exist_ok=True)
open(os.path.join(ev, "pilot1_summary.txt"), "w").write(txt + "\n")
df.to_csv(os.path.join(ev, "pilot1_runs.csv"), index=False)
