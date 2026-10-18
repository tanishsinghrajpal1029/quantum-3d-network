"""Pilot 1 (exploratory; dev seeds Q3D; not confirmatory): 2D 11x11 (matched nodes), 2D 13x13 (matched links) and 3D 5^3.
Usage: P3D_D=3 P3D_GRID=5 python3 tools/pilot1.py <worker> <nworkers> <out.csv>   (resume-safe: finished run ids are skipped)"""
import os, sys, time
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "fork"))
import pandas as pd, study3d as m
NNET = 2
CFGS = [("kg", "-|p00|base"), ("kg", "o0.044|p00|base"), ("kgMChN", "o0.044|p10|base"), ("kgMChN", "o0.044F|p10|base"),
        ("kgMCa", "-|p10|base"), ("kgMCa", "o0.044|p10|base")]
TASKS = [[f"Q3Dd{m.D}g{m.GRID}", hw, "field", arm, cfg, i] for hw in m.HWS for (arm, cfg) in CFGS for i in range(NNET)]
if __name__ == "__main__":
    w, nw, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    done = set(pd.read_csv(out).run) if os.path.exists(out) else set()
    for k, t in enumerate(TASKS):
        if k % nw != w or m.run_id(t) in done: continue
        t0 = time.time(); r = m.run_one(t); r["elapsed_s"] = round(time.time() - t0, 1)
        pd.DataFrame([r]).to_csv(out, mode="a", header=not os.path.exists(out), index=False)
        print(f"{k:3d} {t[1:]} {r['elapsed_s']:.0f}s", flush=True)
