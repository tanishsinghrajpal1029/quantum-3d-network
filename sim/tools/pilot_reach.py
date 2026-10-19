"""Reach pilot (Study 3D-2; EXPLORATORY; pilot seeds Q3R; not confirmatory): 3 link levels x 4 arms x 2 networks per lattice.
Checks run time, memory and the arms on 2D 32x32, 3D 10^3 and 2D 37x37 before the pre-registration fixes the design.
Usage: P3D_REACH=1 P3D_D=3 P3D_GRID=10 python3 tools/pilot_reach.py <worker> <nworkers> <out.csv>   (resume-safe)"""
import os, sys, time, resource
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "fork"))
import pandas as pd, study3d as m
assert m.REACH, "set P3D_REACH=1"
NNET = 2
HWS_R = ("fut97", "fut98", "fut99")
CFGS = [("kg", "-|p00|base"), ("kgMCa", "-|p10|base"), ("kgMCa", "o0.044|p10|base"), ("kgMChN", "o0.044F|p10|base")]
TASKS = [[f"Q3Rd{m.D}g{m.GRID}", hw, "field", arm, cfg, i] for hw in HWS_R for (arm, cfg) in CFGS for i in range(NNET)]
if __name__ == "__main__":
    w, nw, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    done = set(pd.read_csv(out).run) if os.path.exists(out) else set()
    for k, t in enumerate(TASKS):
        if k % nw != w or m.run_id(t) in done: continue
        t0 = time.time(); r = m.run_one(t); r["elapsed_s"] = round(time.time() - t0, 1)
        r["maxrss_mb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // (1024 * 1024 if sys.platform == "darwin" else 1024)
        pd.DataFrame([r]).to_csv(out, mode="a", header=not os.path.exists(out), index=False)
        print(f"{k:3d} {t[1:]} {r['elapsed_s']:.0f}s", flush=True)
