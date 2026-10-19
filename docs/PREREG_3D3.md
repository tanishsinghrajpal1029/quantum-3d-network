# Pre-registration: Study 3D-3, the king's-graph control (is the reach gain about dimension or about degree?)

**Status:** pre-registered when this file and the files listed in `sim/psc3d3/HASHES_PREREG_3D3.txt` are pushed to GitHub, before any confirmatory run. **Author:** Tanish Singh Rajpal (analysis drafted with Claude). **Date:** 19 Oct 2026.

## Question
Study 3D-2 found that a 3D cube serves 2.3–3.5× more of uniform demand than a 2D grid with the same number of nodes. A 2D graph with more links per node also shortens distances. Does 3D still win against the **2D grid plus both diagonals** (the king's graph: 1,024 nodes, 3,906 links, up to 8 links per node), which has more links and higher degree than the cube (2,700 links, up to 6 per node)?

## Already known (exploratory)
- **Geometry only (P3D-E15):** the share of pairs within reach (3 / 4 / 6 hops) is 4.2% / 6.8% / 13.3% for the king's graph and 4.7% / 8.9% / 21.7% for the cube. The predicted 3D lead is therefore small at F0 0.97 (ratio about 1.1) and larger at 0.99 (about 1.6).
- **One smoke run** (king's graph, fut99, `kg`, network 0, pilot seed; cloud): served share 15.7%, U_max 96, 3.2 GB of memory, 408 s.
- No pilot was run. The hypotheses below follow from the geometry and from Study 3D-2, and **K1 may fail at F0 0.97.**

## Design
| | Fixed choice |
|---|---|
| New lattice | **King's graph 32×32**: the 2D grid plus both diagonals. Hop distance is Chebyshev; every link has the same quality model as in Study 3D-2. This is a graph assumption: diagonal links are not made longer or worse |
| Compared with | Study 3D-2's confirmatory runs for 3D 10³ and 2D 32×32 (2D 37×37 descriptive), read from frozen copies `sim/reference/s3d2_*_runs.csv` whose sha256 equal Study 3D-2's merge output. The networks are independent and come from the same platform and code paths; the gate checks the code |
| Everything else | Exactly as Study 3D-2: link levels fut97/98/99, radius 5/6/8, demand, arms, 32 networks (8 in the harm cell). **408 runs** |
| Seeds | `K3D_SEEDS = (19371, 19372, 19373, 19374)`, blocks `P3Kd2g32`, seed tag `p3k`. Never used before |
| Code | Fork v3 adds `GRID_KING` (`fork/drift_queue_des_g1.py`: diagonal links, Chebyshev hops, `shortest_paths_king`, U_max from centred placements; `fork/study3d.py`: `P3D_KING=1`, per-hop path counts by DP). With `P3D_KING` unset, every earlier path is unchanged |
| Tests (cloud) | `sim/tests/test_king.py`: on 4×4, 6×6 and 9×9, link counts, hop distance and every shortest-path list (h ≤ 4) match brute-force BFS. U_max matches brute force. The per-hop counter matches enumeration for every user on 9×9 and 12×12 |
| Equivalence checks (cloud) | v3 = v2 on a reach task, all 136 columns. Study 34 is reproduced exactly on the default path and with lazy users |
| Platform | PSC Bridges-2, RM-shared, the paper's anaconda Python |

## Gate (before any confirmatory job)
`sim/psc3d3/check_v3.sbatch`, with the frozen v3 code on PSC. Four runs must match their recorded rows in every column:
- 2 Study 34 runs on the default path;
- 1 Study 34 run with lazy users;
- **1 Study 3D-2 confirmatory run** (2D 32×32, fut97, `kg`, network 0).

If any differs, we stop.

## Hypotheses (one-sided CP95; bootstrap over networks with B = 20,000 and seed 3003)
**K1 (primary, dimension).** Served share in `kg -`, 3D 10³ minus the king's graph, at each link level: 98.33% two-sided intervals (Bonferroni over 3). Each passes if its lower bound is > 0. K1 passes if all 3 pass. The ratio and its 95% interval are reported next to the geometry-only ratio.

**K2 (primary, safety on the king's graph).** As Study 3D-2 R1, at each link level:
- (a) gated check after a forced alarm;
- (b) always-on margin;
- bars: harmed-network bound ≤ 0.10 and bad-pair bound ≤ 0.01.

**K3 (secondary).** Degree helps in 2D: the king's graph minus the 2D grid in `kg -`, 98.33% intervals, at each link level.

**K4 (secondary).** The 3D lead over the king's graph survives the always-on margin (`kgMCa -`), 98.33% intervals, at each link level.

**S1 (prediction).** On the king's graph with no check, offset 0.044 harms more than 10% of served users.

**S2 (falsification test).** Certificate on the king's graph, `kg -`, 96 networks: FAIL if the CP95 lower bound > 0.05.

**Descriptive:**
- D1: served share in every cell, and served share per 1,000 links.
- D2: king's-graph success by hop, paths per pair and U_max.

## Analysis
`sim/psc3d3/analyze_3d3.py`, fixed by its hash. It checks the sha256 of the Study 3D-2 reference files before using them. It was dry-run only on synthetic input (Study 3D-2 rows relabelled) to exercise the code paths; see `sim/evidence/analyze_3d3_dryrun_synthetic.txt`. That output is not data.

## Cost and execution
- **Memory:** about 3.2 GB per run, so 16 workers on 32 cores (`--cpus-per-task=32`).
- **Shards:** 8, with `--time=02:00:00`.
- **Run time:** expected about 600–900 s per run on PSC.
- **Expected cost: about 190–230 SU.** Hard cap: 8 × 32 × 2 h = 512 SU.

## Deviations and failures
- A crashed or timed-out task is resumed with the same seed.
- No runs are added or dropped.
- Every failed hypothesis is reported.
- Deviations go in the results file.

## PSC commands (Tanish runs these)
```bash
# 1. copy sim/ (from the Mac), check hashes and submit the gate: one command, given in chat
cd /ocean/projects/<charge-id>/<psc-user>/p3d3/sim/psc3d3
grep -v '^#' HASHES_PREREG_3D3.txt | grep ' sim/' | (cd ../.. && sha256sum -c --quiet) && echo HASHES OK
mkdir -p s18c-logs; PY=/opt/packages/anaconda3-2024.10-1/bin/python3
sbatch --account=<charge-id> --export=ALL,PY=$PY check_v3.sbatch                       # continue only on GATE PASS
sbatch --account=<charge-id> --array=0-7 --cpus-per-task=32 --time=02:00:00 --export=ALL,P3D_REACH=1,P3D_KING=1,P3D_D=2,P3D_GRID=32,PY=$PY,TASKS=tasks_3d3_king32.jsonl,OUT=des_3d3_king32,NSHARDS=8,WORKERS=16 reach_array.sbatch
$PY psc_array_runner.py --merge des_3d3_king32 && $PY analyze_3d3.py des_3d3_king32/runs.csv > analysis_3d3.txt; cat analysis_3d3.txt
```
