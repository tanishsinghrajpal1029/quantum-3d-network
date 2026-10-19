"""Fork v2 smoke test and timing (exploratory): one reach task on one lattice, with import and run times.
Usage: P3D_REACH=1 P3D_D=3 P3D_GRID=10 python3 tools/reach_smoke.py fut99 kg "-|p00|base" 0 out.csv"""
import os, sys, time, resource
t0 = time.time()
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "fork"))
import pandas as pd, study3d as m
t1 = time.time()
hw, arm, cfg, idx, out = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
t = [f"Q3Rd{m.D}g{m.GRID}", hw, "field", arm, cfg, idx]
r = m.run_one(t); t2 = time.time()
r["import_s"] = round(t1 - t0, 1); r["run_s"] = round(t2 - t1, 1); r["maxrss_mb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024
pd.DataFrame([r]).to_csv(out, mode="a", header=not os.path.exists(out), index=False)
L = m.g1.HW[hw][2]
print(f"d{m.D} g{m.GRID} {hw} {arm} {cfg} idx {idx}: import {t1 - t0:.0f}s, run {t2 - t1:.0f}s, rss {r['maxrss_mb']} MB | users {r['users_all']}"
      f" (servable share {r['share_servable']:.3f}), U_max {r['umax']}, requests {r['requests']}, delivered {r['delivered']}, bad {r['bad']}")
for h in range(1, L + 1):
    e = r["requests"] * r[f"h{h}_users"] / r["users_all"]
    print(f"   hop {h}: users {r[f'h{h}_users']}, paths/pair {r[f'h{h}_paths_mean']:.2f}, success/request {r[f'h{h}_deliv'] / e:.3f}")
