# Evidence ledger: Files12-3D-Network

## P3D-E1: Exact lattice baseline, exploratory (17 Oct 2026)
- **What was run:** `analytics/lattice_baseline.py`, exact pair counts and a toy Werner formula (no memory decay, ideal swaps). No simulation.
- **Matched node counts:** 2D 32×32 (1,024 nodes) against 3D 10³ (1,000 nodes).
  - Mean hops: 21.3 vs 9.9. Diameter: 62 vs 27.
  - Share of node pairs within 3 hops: 2.2% vs 4.7%.
  - Links per node: 3.9 vs 5.4, so 3D needs about 36% more links.
- **Servable pairs** (F ≥ 0.9 on the toy model):

  | Link level λ | Max hops | 2D 32×32 | 3D 10³ |
  |---|---|---|---|
  | 0.97 | ≤ 4 | 3.5% | 8.9% |
  | 0.99 | ≤ 14 | 29% | 86% |

- **Guard cost:** U_max with requests up to Lmax hops is the same at Lmax ≤ 2 (4). It grows to 12 vs 7 at Lmax = 3 and 20 vs 12 at Lmax = 4. The per-link budget α/U_max is correspondingly stricter in 3D.
- **Caveats:**
  - The toy formula ignores memory decay, gate errors and contention.
  - A fair comparison must also match hardware: total links, or memory qubits per node. This has not been done yet.

## P3D-E2: Simulator fork reproduces Study 34 exactly at d = 2 (18 Oct 2026)
- **Set-up:** `sim/upstream/` holds verbatim copies of the 34 paper modules, with sha256 values in `MANIFEST.txt`. Only `drift_queue_des_g1.py` was forked: the lattice functions are now d-dimensional. The new driver is `sim/fork/study3d.py`.
- **Topology test** (`sim/tests/test_topology.py`):
  - At d = 2 and n = 5, 10, 30, node order, link ids and every candidate path list (Lmax 2 and 3) are identical to upstream.
  - At d = 3, link counts equal 3n²(n−1) and path counts are multinomial.
- **Run reproduction** (`sim/tools/repro_check.py`, cloud container, newer numpy/scipy than PSC): 4 of 4 Study 34 5×5 runs matched the paper's PSC `runs.csv` in all 83 columns:
  - `kg` with no offset;
  - `kgMChN` with offset 0.044 at p = 0.1;
  - `kgMCa` with offset 0.044 and a forced alarm (ionproj);
  - `kgMChN` with offset 0.044, a forced alarm, p = 0.2 and triple load.
  
  Upstream (unforked) code also matched for 2 of 2 runs.
- **Evidence:** `sim/evidence/` (logs, CSVs, environment, hashes).

## P3D-E3: 3D smoke test, exploratory, not a result (18 Oct 2026)
- **Set-up:** cube 3³ (27 nodes, 54 links), ion2020, pilot seeds (Q3D), 7 runs.
- **What it shows:** the closed loop runs in 3D, and its behaviour looks like 2D.
  - With no check, offset 0.044 gave 8,198 bad pairs out of 16,104 and harmed 169/256 served users (66%; 2D Study 34: 67–74%).
  - The hybrid check (p = 0.1) alarmed at epoch 70 with 0 bad pairs after the alarm. 166 users were harmed *before* the alarm, as in 2D.
  - The always-on margin gave 0 bad pairs but served only 54/306 users.
- **Not evidence for any hypothesis:** one network per cell, and a lattice too small to compare.

## P3D-E4: Pilot 1, 2D vs 3D closed loop (18 Oct 2026). EXPLORATORY, dev seeds, 2 networks per cell
- **Runs:** 72/72 on the Mac (macOS, labs env). Lattices: 2D 11×11, 2D 13×13 and 3D 5³; ion2020 and ionproj; 6 configurations. Data: `sim/evidence/pilot1_runs.csv` (sha 207286137ead3eaa).
- **Longest-hop success per request (no check, no offset):**

  | Hardware, hop | 2D 11×11 | 2D 13×13 | 3D 5³ |
  |---|---|---|---|
  | ion2020, 2 hops | 0.21 | 0.11 | 0.26 |
  | ionproj, 3 hops | 0.70 | 0.59 | 0.84 |

- **Fidelity:** delivered fidelity is unchanged (0.937 vs 0.934).
- **Safety:** 0 bad pairs after an alarm and under the always-on margin, on all lattices.
- **To watch:** the 3D hybrid check did not alarm in 0/2 ion2020 offset networks (2D: 2/2).
- **Platform:** Mac and cloud runs of the same tasks diverge slightly (floating point), so confirmatory runs need one platform.
- **Data note:** the CSV column-set issue was repaired exactly by `load_runs.py`, and the writer is fixed.
- **Not evidence for any hypothesis.**

## P3D-E5: Study 3D-1 pre-registration written (18 Oct 2026). Not yet run
- **Plan:** `docs/PREREG_3D1.md`. 3 lattices (2D 11×11, 2D 13×13, 3D 5³) × 2 hardware × 7 cells × 32 networks = 1,344 runs on PSC. Confirmatory seeds 19351–19354, never used before.
- **Hypotheses:**
  - H1 safety (primary): network-level bound ≤ 0.10 and pair-level bound ≤ 0.01.
  - H2 benefit (primary): 3D minus each 2D lattice in longest-hop success, 4 comparisons at Bonferroni 98.75%.
  - H3 fidelity equivalence (±0.01).
  - S1–S3 predictions, including a certificate falsification test.
  - D1–D4 descriptive.
- **Gate:** before any confirmatory job, the fork at d = 2 must reproduce 4 Study 34 runs on PSC (`sim/psc/check_d2.sbatch`).
- **Checks done before freezing:**
  - The analysis script was dry-run on pilot data (`sim/evidence/analyze_3d1_dryrun_pilot.txt`).
  - The PSC runner path was tested in the cloud. This found and fixed a path-order bug in `study3d.py` (the upstream g1 could shadow the fork; the GRID_D assertion caught it).
  - Study 34 reproduction re-checked after the fix: 2/2 MATCH.
- **Frozen files:** `sim/psc/HASHES_PREREG_3D1.txt` (15 files). Timestamped by the GitHub push.
- **Frozen:** the pre-registration was pushed to GitHub at commit `fc3660d` (18 Oct 2026, 05:13 UTC), before any confirmatory run. `origin/main` equals `fc3660d`, and all prereg hashes verified on the Mac.

## P3D-E6: PSC gate passed (18 Oct 2026)
- **Gate result:** job 49402863 (PSC Bridges-2, RM-shared; the paper's anaconda Python) finished COMPLETED in 10 min 20 s. The fork at d = 2 reproduced 4/4 Study 34 runs in all 83 columns: `9686e9db3060`, `683f07a56b42`, `538775e95fe5` and `798df27b89fa`.
- **Hashes:** the files on PSC were checked against `HASHES_PREREG_3D1.txt` before the run (HASHES OK).
- **PSC speed:** about 1.55× slower per run than the cloud container (101 / 220 / 318 / 612 s, against 63–73 / 140–150 / 204 / 392 s).
- **Execution note, decided before any confirmatory output:**
  - The confirmatory jobs use 8 shards (`--array=0-7`, `S18C_NSHARDS=8`) instead of 4, so each lattice fits the pre-registered 1 h limit at PSC speed.
  - Tasks, seeds, code and analysis are unchanged. Each run's seeds depend only on its task, so sharding cannot change any result.
  - The expected cost rises to about 100–130 SU because of idle tails.

## P3D-E7: Study 3D-1 confirmatory results (18 Oct 2026)
- **Runs:** 1,344/1,344 on PSC. runs.csv sha256: d2g11 583c7c40…, d2g13 885c609d…, d3g5 d1e148be… (in full in `sim/evidence/analysis_3d1.txt`).
- **H1 safety:** PASS. 0/32 harmed networks in every lattice × hardware × arm, and 0 bad pairs.
- **H2 benefit:** FAIL (1/4). Longest-hop success, 3D vs 2D 11×11 and 3D vs 2D 13×13:
  - ion2020: −0.007 and −0.022;
  - ionproj: +0.072 (not significant) and +0.091 (significant).
- **H3 fidelity equivalence:** PASS. 3D minus 2D is −0.002 to −0.003.
- **S1 detection:** FAIL for ion2020 (3D 0.69 vs 2D 0.97); PASS for ionproj.
- **S2:** PASS. **S3 certificate falsification:** PASS (not falsified).
- **Write-up:** `docs/RESULTS_3D1.md`. The pilot overestimated the route-diversity benefit; the confirmatory run is the result.
