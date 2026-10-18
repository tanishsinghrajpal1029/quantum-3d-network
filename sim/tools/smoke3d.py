"""Smoke test of the 3D lattice (exploratory, not a result): run a few pilot tasks on one lattice and print key columns.
Usage: P3D_D=3 P3D_GRID=3 python3 tools/smoke3d.py 0,8 out/smoke_d3g3.csv   (indices into the pilot task list)"""
import os, sys, time
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "fork"))
import pandas as pd, study3d as m
ts = m.tasks("Q3D", 2); idx = [int(i) for i in sys.argv[1].split(",")]
print(f"d={m.D} n={m.GRID}: {len(m.cn1.NODES)} nodes, {m.cn1.NL} links; {len(ts)} pilot tasks", flush=True)
for i in idx:
    t0 = time.time(); r = m.run_one(ts[i])
    pd.DataFrame([r]).to_csv(sys.argv[2], mode="a", header=not os.path.exists(sys.argv[2]), index=False)
    print(ts[i][1:], f"{time.time()-t0:.0f}s users={r['users_all']} served={r['users_served']} delivered={r['delivered']}"
          f" bad={r['bad']} qual={r['qual']} alarms={r['alarms']} users_bad_served={r['users_bad_served']}", flush=True)
