# sim/: the paper's simulator, forked to d-dimensional lattices

## Layout
- `upstream/`: **verbatim** copies of the 34 modules Study 34 needs (from `Files11-EndToEnd-PRX-Claude/prx_work`), plus the Study 34 5×5 task file. **Never edit.** `MANIFEST.txt` lists the sha256 and origin of each file.
- `fork/`: the only changed or new code. It shadows `upstream/` when it comes first on `sys.path`.
  - `drift_queue_des_g1.py`: d-dimensional `grid_topology`, `shortest_paths` and `hop_distance`, plus a `GRID_D` switch (default 2). Nothing else in it changed (see `diff upstream/drift_queue_des_g1.py fork/drift_queue_des_g1.py`).
  - `study3d.py`: the Study 34 driver for a lattice of dimension `P3D_D` and side `P3D_GRID`.
    - Blocks named `S34g<n>` with d = 2 reuse Study 34's seeds and run ids (compat mode, for the reproduction check).
    - `Q3D…` blocks are pilots with fresh dev seeds.
    - `P3D…` blocks are confirmatory runs. Their seeds are set only in the pre-registration.
- `tools/repro_check.py`: runs tasks and compares every column with the paper's `runs.csv` after the same pandas round trip.
- `tools/smoke3d.py`: a quick 3D run that prints key columns. It is exploratory, not a result.
- `tests/test_topology.py`: checks that d = 2 node order, link ids and candidate paths are identical to upstream for n = 5, 10, 30, and checks 3D link counts and path counts (multinomial).
- `reference/s34_g5_runs.csv`: Study 34 5×5 results from the paper (PSC), used for comparison.

No other upstream module needed a change: link correlations, neighbour sets and U_max all work from node coordinates and link endpoints in any dimension.

## Commands
```bash
cd sim
python3 tests/test_topology.py
# d = 2 reproduction (fork first): every column must match Study 34
python3 tools/repro_check.py --module study3d --lib fork:upstream --tasks upstream/tasks_s34_g5.jsonl \
  --lines 1,161,673,1000 --ref reference/s34_g5_runs.csv --out out/fork_d2.csv
# 3D smoke test (27-node cube)
P3D_D=3 P3D_GRID=3 python3 tools/smoke3d.py 0,1,4 out/smoke_d3g3.csv
```
Requirements: numpy, scipy, pandas and scikit-learn (imported by an upstream module).

## Known limits of the fork
- Study 34's matched-exposure variant `u` is not ported.
- Feature scalings in the AI prior (`len(NB1)/6`, `len(NB2)/12`) were set for 2D degrees. The `kg`/`kgMChN`/`kgMCa` arms do not use the AI prior.

## Fork v2 (reach; 19 Oct 2026)
- `P3D_REACH=1` adds the presets `fut97`, `fut98` and `fut99` (ionfut's rate, memory and gates; link F0 0.97/0.98/0.99). The service radius is the analytic reach plus `P3D_RADIUS_EXTRA` (default 2).
- It also switches on lazy users (`LazyCands`) and fast path enumeration (`shortest_paths_fast`).
- `P3D_LAZY=1` switches on lazy users alone, for the equivalence gate.
- Reach blocks: `Q3R…` (pilot seeds 30361–30364) and `P3R…` (confirmatory seeds, set only in the pre-registration). Network seeds use the `p3r` tag, so they never overlap Study 3D-1.
- Without these variables, every earlier path is unchanged (`evidence/fork_v2_gates.txt`).
- Tests: `python3 tests/test_lazy.py`. Smoke test: `P3D_REACH=1 P3D_D=3 P3D_GRID=10 python3 tools/reach_smoke.py fut99 kg "-|p00|base" 0 out.csv`.
- Note: Study 3D-1 was frozen at commit `fc3660d`. To reproduce it, use the `study3d.py` and `drift_queue_des_g1.py` from that commit. The v2 files give identical 3D-1 rows, but their hashes differ.
