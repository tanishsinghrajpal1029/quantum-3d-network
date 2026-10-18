"""Reproduction check: run Study 34 tasks with a given library path and compare each row with the paper's runs.csv.

Usage: python3 repro_check.py [--module study3d] --lib DIR[:DIR...] --tasks FILE --lines 1,161 --ref REF.csv --out OUT.csv
The first DIR on --lib wins (put the 3D fork before upstream to test the fork). S34_GRID is read from the task block.
A row passes only if every column matches exactly after the same pandas CSV round trip the PSC runner used.
"""
import argparse, io, json, os, sys, time
ap = argparse.ArgumentParser()
ap.add_argument("--lib", required=True); ap.add_argument("--tasks", required=True); ap.add_argument("--lines", required=True)
ap.add_argument("--ref", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--module", default="study34")
a = ap.parse_args()
tasks = [json.loads(l) for l in open(a.tasks)]
sel = [tasks[int(i) - 1] for i in a.lines.split(",")]
os.environ["S34_GRID"] = os.environ["P3D_GRID"] = sel[0][0].split("g")[-1]; os.environ.setdefault("P3D_D", "2")
for d in reversed(a.lib.split(":")): sys.path.insert(0, os.path.abspath(d))
import pandas as pd
import importlib; study34 = importlib.import_module(a.module)
print(a.module, "from", study34.__file__, "| g1 from", sys.modules["drift_queue_des_g1"].__file__, flush=True)
ref = pd.read_csv(a.ref).set_index("run")
ok_all = True
for t in sel:
    t0 = time.time(); row = study34.run_one(t)
    df = pd.read_csv(io.StringIO(pd.DataFrame([row]).to_csv(index=False))).set_index("run")
    df.to_csv(a.out, mode="a", header=not os.path.exists(a.out))
    r = df.index[0]; R = ref.loc[r]
    bad = [c for c in df.columns if not ((pd.isna(df.loc[r, c]) and pd.isna(R[c])) or df.loc[r, c] == R[c])]
    ok_all &= not bad
    print(f"{r} {t[1:5]} {time.time()-t0:.0f}s ->", "MATCH (all %d columns)" % len(df.columns) if not bad else f"DIFF in {bad[:8]}", flush=True)
print("ALL MATCH" if ok_all else "SOME DIFFER", flush=True)
