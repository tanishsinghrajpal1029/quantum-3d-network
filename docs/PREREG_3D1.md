# Pre-registration: Study 3D-1, 2D vs 3D lattices under the paper's closed loop

**Status:** pre-registered when this file and the files listed in `sim/psc/HASHES_PREREG_3D1.txt` are pushed to GitHub, before any confirmatory run. **Author:** Tanish Singh Rajpal (analysis drafted with Claude). **Date:** 18 Oct 2026.

## Question
At a matched node count (and, separately, a matched link count), does a 3D lattice serve more of the hardest entanglement requests than a 2D lattice? Do the safety guarantees of the paper (Theorem 2, Corollary 3) still hold in 3D? Does 3D change the fidelity of the pairs it delivers?

## What is already known (exploratory; must not be reported as a result)
- P3D-E1: exact lattice counts.
- P3D-E2: at d = 2 the fork reproduces Study 34 bit for bit.
- P3D-E4: Pilot 1 used dev seeds and 2 networks per cell. The hypotheses below were chosen after seeing it. Three things from the pilot shaped the design:
  - per-request success was used, to avoid dilution;
  - a no-offset gated cell was added to count false alarms;
  - a certificate falsification test was added (pilot: 5/24 p20 violating runs on 3D, from 2 of 4 networks).

## Design
| | Fixed choice |
|---|---|
| Lattices | 2D 11×11 (121 nodes, 220 links; matched nodes) · 2D 13×13 (169 nodes, 312 links; matched links) · 3D 5³ (125 nodes, 300 links) |
| Hardware | ion2020 (Lmax 2) and ionproj (Lmax 3), the paper's presets |
| Model | Study 34 unchanged: correlated links, guard, hybrid check, offset bound. Demand is near-neighbour (hop 1..Lmax) at the same total rate on every lattice |
| Cells (7) | `kg -`; `kg o0.044`; `kgMChN -` p10; `kgMChN o0.044` p10; `kgMChN o0.044F` p10; `kgMCa -` p10; `kgMCa o0.044` p10 |
| Networks | 32 per lattice × hardware, so 7 × 2 × 32 = 448 runs per lattice and **1,344 runs** in total |
| Seeds | Confirmatory `P3D_SEEDS = (19351, 19352, 19353, 19354)`, blocks `P3Dd{d}g{n}`. Network and run seeds come from sha256 of (p3dnet/p3drun, d, n, hardware, idx). No seed was used before this file |
| Code | `sim/upstream/` verbatim (MANIFEST) · `sim/fork/drift_queue_des_g1.py` · `sim/fork/study3d.py`. Task files `sim/psc/tasks_3d1_*.jsonl`. Hashes in `sim/psc/HASHES_PREREG_3D1.txt` |
| Platform | PSC Bridges-2, RM-shared, the paper's Python (`/opt/packages/anaconda3-2024.10-1/bin/python3`). All confirmatory runs on this one platform |

**Unit of replication:** the network (lattice, hardware, idx). Runs of one network share its links and seeds.

**Outcome "longest-hop success"** for a network: deliveries at hop Lmax divided by the expected requests at hop Lmax. Users are picked uniformly, so the expected requests at hop h are requests × users(h) / users. This removes the dilution from different user counts.

## Gate (must pass before any confirmatory job)
`sim/psc/check_d2.sbatch` runs 4 Study 34 tasks (lines 1, 161, 673 and 1000) with the fork at d = 2 on PSC. All 4 must match the paper's `runs.csv` in all 83 columns. **If any differs, stop.** We then report the failure and run no confirmatory job.

## Hypotheses and pass rules (one-sided Clopper–Pearson 95% bounds; bootstrap over networks with B = 20,000 and seed 3001)
**H1 (primary, safety).** Checked on 3D 5³ for each hardware; 2D results are reported as replication.
- **(a) Gated check after the alarm** (Theorem 2; cells `kgMChN o0.044` and `o0.044F`). A network counts as harmed if any of its runs gave a bad pair to a user after the alarm. Pass if the bound on harmed networks is ≤ 0.10 **and** the bound on post-alarm bad pairs is ≤ 0.01.
- **(b) Always-on margin, whole run** (Corollary 3; cells `kgMCa -` and `o0.044`). The same two bars, using harmed served users and all bad pairs.
- H1 passes if (a) and (b) pass for both hardware types.

**H2 (primary, benefit).** No check, no offset (`kg -`). Compare longest-hop success, 3D minus 2D, in 4 comparisons: 2D 11×11 and 2D 13×13, each for both hardware types. Use 98.75% two-sided percentile bootstrap intervals (Bonferroni over 4). Each comparison passes if its lower bound is > 0. H2 passes if all 4 pass. Pilot effect sizes: +0.05 (the weakest) to +0.25.

**H3 (secondary, equivalence).** Mean kept fidelity (`p10_F`, cell `kg -`), 3D minus 2D 11×11, for each hardware type. Pass if the 90% bootstrap interval lies inside ±0.01 (TOST at 5%).

**S1 (prediction).** Detection carries over. Alarm rate in `kgMChN o0.044`: |3D − 2D 11×11| ≤ 0.15 for each hardware type. The pilot saw 0/2 vs 2/2 on ion2020, so this may fail. It is reported either way.

**S2 (prediction).** With no check, offset 0.044 harms > 10% of served users on every lattice and hardware type.

**S3 (falsification test, certificate).** In `kg -` (no feedback), per lattice over 64 networks, for p10 and p20: FAIL if the one-sided CP95 **lower** bound on the violating-run rate exceeds 0.05, the certificate's own level. All-cell counts are reported, by run and by network.

**Descriptive only (no pass rule):**
- D1: false-alarm rate (`kgMChN -`).
- D2: longest-hop success kept under the always-on margin, as the ratio `kgMCa -` / `kg -` on the same network.
- D3: success, route choices, U_max and served share at every hop.
- D4: 2D 13×13 minus 2D 11×11.

## Analysis
`sim/psc/analyze_3d1.py` is fixed by its hash. It was tested only on Pilot 1 data (`--dry-run`; output in `sim/evidence/analyze_3d1_dryrun_pilot.txt`). Its assertions require complete cells (7 × 32 runs per lattice × hardware).

## Deviations and failures
- A crashed task is resumed with the same seed. The runner skips finished run ids.
- No runs are added or dropped.
- Every failed hypothesis is reported.
- Any deviation from this plan goes in the results file with its reason.

## PSC commands (Tanish runs these; about 60–100 SU expected, hard cap 3 × 4 × 16 core-hours = 192 SU)
```bash
# 1. copy sim/ to PSC, e.g. from the Mac:  rsync -av sim/ <psc-user>@bridges2.psc.edu:/ocean/projects/<charge-id>/<psc-user>/p3d/sim/
cd /ocean/projects/<charge-id>/<psc-user>/p3d/sim/psc
PY=/opt/packages/anaconda3-2024.10-1/bin/python3
mkdir -p s18c-logs
# 2. gate (about 4 SU): wait for it and read the last line of check_d2_<jobid>.log
sbatch --account=<charge-id> --export=ALL,PY=$PY check_d2.sbatch
# 3. only if GATE PASS: three jobs, one per lattice
for L in "2 11" "2 13" "3 5"; do set -- $L
  sbatch --account=<charge-id> --array=0-3 --cpus-per-task=16 --time=01:00:00 \
    --export=ALL,P3D_D=$1,P3D_GRID=$2,PYTHONPATH=$PWD/../fork,S18C_DIR=$PWD,PY=$PY,S18C_MODULE=study3d,S18C_TASKS=tasks_3d1_d$1g$2.jsonl,S18C_OUT=des_3d1_d$1g$2,S18C_NSHARDS=4 \
    s18c_array.sbatch
done
# 4. merge and analyse
for L in d2g11 d2g13 d3g5; do $PY psc_array_runner.py --merge des_3d1_$L; done
$PY analyze_3d1.py des_3d1_d2g11/runs.csv des_3d1_d2g13/runs.csv des_3d1_d3g5/runs.csv > analysis_3d1.txt
```
