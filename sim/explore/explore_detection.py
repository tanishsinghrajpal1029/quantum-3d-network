"""EXPLORATORY (not pre-registered): why does the gated check alarm less often on 3D ion2020 (Study 3D-1, S1)?
Re-runs Study 3D-1 tasks of the cell kgMChN o0.044|p10|base (same seeds) and records, without changing any random draw,
every model-check update (E_i, q_i): the evidence per test is E_i - q_i (the check bets that P(E=1) > q).
Usage: P3D_D=3 P3D_GRID=5 python3 explore/explore_detection.py ion2020 0,1,2,3 out.csv"""
import os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "fork"))
import numpy as np, pandas as pd, study3d as m

LAST = {}
Base = m.Net3D


class NetI(Base):
    def __init__(s, *a, **k):
        super().__init__(*a, **k)
        orig = s.mc.update; s.log = []; LAST["net"] = s
        def upd(E, q):
            r = orig(E, q); s.log.append((int(E), float(q), bool(r))); return r
        s.mc.update = upd


m.Net3D = NetI
hw, idxs, out = sys.argv[1], [int(i) for i in sys.argv[2].split(",")], sys.argv[3]
for i in idxs:
    t = [f"P3Dd{m.D}g{m.GRID}", hw, "field", "kgMChN", "o0.044|p10|base", i]
    row = m.run_one(t); L = np.array(LAST["net"].log, float)
    first = int(np.argmax(L[:, 2])) if L[:, 2].any() else len(L)
    pre = L[:first] if first > 0 else L[:0]
    rec = dict(run=row["run"], lat=f"d{m.D}g{m.GRID}", hw=hw, idx=i, alarms=row["alarms"], first_alarm_ep=row["first_alarm_ep"],
               n_tests=len(L), n_pre=len(pre), E_pre=pre[:, 0].mean() if len(pre) else np.nan, q_pre=pre[:, 1].mean() if len(pre) else np.nan,
               gap_pre=(pre[:, 0] - pre[:, 1]).mean() if len(pre) else np.nan,
               E_all=L[:, 0].mean(), q_all=L[:, 1].mean(), delivered=row["delivered"], bad=row["bad"])
    pd.DataFrame([rec]).to_csv(out, mode="a", header=not os.path.exists(out), index=False)
    print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in rec.items()}), flush=True)
