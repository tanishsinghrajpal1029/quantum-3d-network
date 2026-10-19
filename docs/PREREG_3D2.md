# Pre-registration: Study 3D-2, reach (2D vs 3D under uniform demand, link-quality sweep)

**Status:** pre-registered when this file and the files listed in `sim/psc3d2/HASHES_PREREG_3D2.txt` are pushed to GitHub, before any confirmatory run. **Author:** Tanish Singh Rajpal (analysis drafted with Claude). **Date:** 19 Oct 2026.

## Question
With requests between uniformly random pairs of nodes, does a 3D lattice serve a larger share of all requests above τ = 0.9 than 2D lattices with the same number of nodes or of links? How does the gain depend on link quality (F0 = 0.97, 0.98, 0.99)? Do the paper's safety guarantees hold when users can be routed over up to 104 links?

## Already known (exploratory; chose the hypotheses below)
- **P3D-E10 (analytic):** the 3D / 2D 32×32 ratio with the guard is 2.1, 2.5 and 2.8 at F0 0.97, 0.98 and 0.99.
- **P3D-E11:** fork v2 and its gates.
- **Reach pilot** (`sim/evidence/analyze_3d2_dryrun_pilot.txt`; Mac, pilot seeds Q3R, 2 networks per cell, 72 runs):
  - served share with `kg` and no offset: 3D 4.6% / 10.2% / 26.0% vs 2D 32×32 2.1% / 3.6% / 7.6%;
  - 0 bad pairs in every cell;
  - under offset 0.044 the 3D advantage was much smaller.
- **Lesson from Study 3D-1:** a 2-network pilot can overstate an effect. The confirmatory run is the result.

## Design
| | Fixed choice |
|---|---|
| Lattices | 2D 32×32 (1,024 nodes, 1,984 links) · **3D 10³** (1,000 nodes, 2,700 links) · 2D 37×37 (1,369 nodes, 2,664 links; matched links) |
| Link levels | `fut97`, `fut98`, `fut99`: ionfut's rate (1,000/s), memory (T2 1 s) and gate error (0.003), with fleet F0 0.97 / 0.98 / 0.99; τ = 0.9 |
| Service radius | Analytic reach + 2 = 5 / 6 / 8 hops. Pairs within the radius are users; requests beyond it use no resources |
| Demand | Servable requests arrive at Γ = 3/s on every lattice, each for a uniformly random user, served one at a time |
| Model | Study 34 unchanged: correlated links, guard, hybrid check, offset bound. Fork v2: lazy users and fast path enumeration |
| Cells | 4 main cells × 32 networks: `kg -`; `kgMCa -` (p = 0.1); `kgMCa o0.044`; `kgMChN o0.044F` (forced alarm, p = 0.1). Plus a harm sanity cell, `kg o0.044`, × 8 networks |
| Runs | 3 lattices × 3 link levels × (4 × 32 + 8) = **1,224 runs** |
| Seeds | `R3D_SEEDS = (19361, 19362, 19363, 19364)`, blocks `P3Rd{d}g{n}`. Network and run seeds come from sha256 of (p3rnet/p3rrun, d, n, link level, idx). Never used before |
| Code | `sim/upstream/` verbatim · `sim/fork/` v2 · tasks `sim/psc3d2/tasks_3d2_*.jsonl` · hashes `sim/psc3d2/HASHES_PREREG_3D2.txt` |
| Platform | PSC Bridges-2 RM-shared, the paper's anaconda Python. All confirmatory runs on this platform |

**Outcome "served share"** of a run: good deliveries per servable request × the servable share of all ordered pairs. This equals the share of uniform all-pairs demand served above τ. **Unit:** the network.

## Gate (before any confirmatory job)
`sim/psc3d2/check_v2.sbatch` runs on PSC with the frozen v2 code:
- the default path must reproduce 4 Study 34 runs;
- lazy users must reproduce 2 of them;
- every one must match in all 83 columns.

If any differs, we stop and report it.

## Hypotheses and pass rules (one-sided Clopper–Pearson 95%; bootstrap over networks with B = 20,000 and seed 3002)
**R1 (primary, safety).** Checked on 3D 10³ at all three link levels; 2D results are reported as replication.
- **(a) Gated check after a forced alarm** (`kgMChN o0.044F`). A network counts as harmed if any of its runs gave a bad pair to a user after the alarm. Pass if the bound on harmed networks is ≤ 0.10 and the bound on post-alarm bad pairs is ≤ 0.01.
- **(b) Always-on margin, whole run** (`kgMCa -` and `o0.044`). The same two bars.
- R1 passes if (a) and (b) pass at every link level.

**R2 (primary, benefit).** Served share in `kg -`, 3D minus 2D 32×32 and 3D minus 2D 37×37, at each link level: 6 comparisons with 99.17% two-sided intervals (Bonferroni). Each comparison passes if its lower bound is > 0. R2 passes if all 6 pass.

**R3 (secondary, size).** The 3D / 2D 32×32 ratio of served share has a one-sided 95% lower bound ≥ 1.5 at every link level. The analytic ratios (2.1 / 2.5 / 2.8) are reported alongside.

**R4 (secondary).** The always-on margin keeps a 3D advantage: in `kgMCa -`, 3D minus 2D 32×32 has a 98.33% interval (Bonferroni over 3) whose lower bound is > 0, at each link level.

**S1 (prediction).** With no check, offset 0.044 harms more than 10% of served users in every lattice × link-level cell (8 networks each).

**S2 (falsification test, certificate).** In `kg -` (no feedback), 96 networks per lattice, for p10 and p20: FAIL if the one-sided CP95 lower bound on the violating-run rate exceeds 0.05.

**Descriptive:**
- D1: served share in every arm and cell, including how much of the 3D advantage survives the offset.
- D2: success per request by hop, U_max, servable share and kept fidelity.

## Analysis
`sim/psc3d2/analyze_3d2.py`, fixed by its hash. It was tested only on pilot data (`--dry-run`). Its assertions require complete cells (4 × 32 + 8 runs per lattice × link level).

## Cost and execution (measured on the pilot)
- **Run time:** pilot runs took 410–450 s on the Mac (mean; at most 540 s) with 15 at once. Expect about 700–1,100 s on PSC.
- **Memory:** peak 1.9 GB (2D 32×32) and 2.7–2.9 GB (3D, 2D 37×37), against about 2 GB per RM-shared core. So:
  - 2D 32×32: 16 workers on 16 cores;
  - 3D 10³ and 2D 37×37: 16 workers on 24 cores.
- **Shards:** 8 per lattice, with `--time=02:00:00`.
- **Expected cost: about 400–500 SU.** Hard cap: 8 × 2 h × (16 + 24 + 24) = 1,024 SU.

## Deviations and failures
- A crashed or timed-out task is resumed with the same seed (the runner skips finished run ids).
- No runs are added or dropped.
- Every failed hypothesis is reported.
- Any deviation goes in the results file with its reason.

## PSC commands (Tanish runs these)
```bash
# 1. copy sim/ (from the Mac):
#    cd ~/Documents/Independent-Study/quantum_grid_router/Files12-3D-Network && COPYFILE_DISABLE=1 tar --exclude 'sim/out' --exclude '__pycache__' -czf - sim | ssh <psc-user>@bridges2.psc.edu 'D=/ocean/projects/<charge-id>/<psc-user>/p3d2; mkdir -p $D && cd $D && tar -xzf -'
cd /ocean/projects/<charge-id>/<psc-user>/p3d2/sim/psc3d2
grep -v '^#' HASHES_PREREG_3D2.txt | grep ' sim/' | (cd ../.. && sha256sum -c --quiet) && echo HASHES OK
mkdir -p s18c-logs; PY=/opt/packages/anaconda3-2024.10-1/bin/python3
# 2. gate (about 5 SU); continue only on "GATE PASS"
sbatch --account=<charge-id> --export=ALL,PY=$PY check_v2.sbatch
# 3. confirmatory: one array job per lattice
sbatch --account=<charge-id> --array=0-7 --cpus-per-task=16 --time=02:00:00 --export=ALL,P3D_REACH=1,P3D_D=2,P3D_GRID=32,PY=$PY,TASKS=tasks_3d2_d2g32.jsonl,OUT=des_3d2_d2g32,NSHARDS=8,WORKERS=16 reach_array.sbatch
sbatch --account=<charge-id> --array=0-7 --cpus-per-task=24 --time=02:00:00 --export=ALL,P3D_REACH=1,P3D_D=3,P3D_GRID=10,PY=$PY,TASKS=tasks_3d2_d3g10.jsonl,OUT=des_3d2_d3g10,NSHARDS=8,WORKERS=16 reach_array.sbatch
sbatch --account=<charge-id> --array=0-7 --cpus-per-task=24 --time=02:00:00 --export=ALL,P3D_REACH=1,P3D_D=2,P3D_GRID=37,PY=$PY,TASKS=tasks_3d2_d2g37.jsonl,OUT=des_3d2_d2g37,NSHARDS=8,WORKERS=16 reach_array.sbatch
# 4. merge and analyse
for L in d2g32 d3g10 d2g37; do $PY psc_array_runner.py --merge des_3d2_$L; done
$PY analyze_3d2.py des_3d2_d2g32/runs.csv des_3d2_d3g10/runs.csv des_3d2_d2g37/runs.csv > analysis_3d2.txt; cat analysis_3d2.txt
```
