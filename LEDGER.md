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

## P3D-E8: Why detection was slower on 3D ion2020, exploratory (18 Oct 2026)
- **Inputs:** the PSC runs.csv files were downloaded and match the analysis hashes (`sim/evidence/3d1_runs/`).
- **Same number of tests:** 677 tests per network on 3D vs 673 on 2D 11×11, so test count is not the cause.
- **Instrumented re-run** (`sim/explore/explore_detection.py`; it logs every model-check update without changing any random draw; 8 networks per lattice, cloud):
  - The null bound q is the same (0.048 vs 0.047).
  - The evidence per test (E − q) is smaller on 3D (0.023 vs 0.032), but within noise: SD across networks 0.014–0.016, so the standard error of the difference is about 0.007.
  - Alarms: 4/8 on 3D vs 8/8 on 2D.
- **PSC data point the other way:** the true kept fidelity under the offset is slightly *lower* on 3D (0.894 vs 0.896), with more bad pairs (61% vs 56%). That alone would make detection easier, not harder.
- **Conclusion:** mechanism not resolved; the 31/32 vs 22/32 gap is unlikely to be chance (Fisher p ≈ 0.006). Resolving it needs a targeted study: more networks and the per-test logs.
- **Reproducibility finding:** cloud re-runs of the P3D tasks are not bit-identical to PSC. For example, network 0 on 11×11 gave 7,478 delivered pairs in the cloud vs 7,170 on PSC, and the hook was checked to change nothing. PSC's MKL and the cloud's OpenBLAS diverge on these larger lattices, although they agreed on 5×5. Reproducing Study 3D-1 exactly therefore needs PSC's anaconda Python.

## P3D-E9: Reach baseline, exploratory analytic (18 Oct 2026)
- **Method:** `analytics/reach_baseline.py`. The paper's physics model with homogeneous links, uniform demand, and the guard approximated by a confidence bound at level α/U_max.
- **ion2020:** reach is 1 hop.
- **ionproj:** reach is 3 hops (2 with the guard).
- **ionfut** (F0 0.99, R 1,000/s): reach is 6 hops (5 with the guard). Served share of uniform demand with the guard:

  | 2D 32×32 | 3D 10³ | 2D 37×37 (matched links) |
  |---|---|---|
  | 5.2% | **14.6%** | 4.0% |

  That is about 2.8× the 2D share at matched nodes and 3.6× at matched links. U_max is 33 vs 17, but it costs the same one hop on both lattices.
- **Next:** design note `docs/DESIGN_3D2_REACH.md`. It lists the fork v2 work (lazy users, DP routing, closed-form U_max) and open decisions. It is not pre-registered.

## P3D-E10: Link-quality sweep, reach analytic, exploratory (19 Oct 2026)
- **Method:** `analytics/reach_baseline.py` with `REACH_SWEEP=1` (output in `reach_sweep_output.txt`). ionfut's rate, memory and gates; F0 = 0.97 / 0.98 / 0.99.
- **Reach** (true model / with guard): 3/3, 4/4 and 6/5 hops.
- **Uniform demand served, with the guard:**

  | F0 | 2D 32×32 | 3D 10³ | 2D 37×37 (matched links) | 3D advantage (nodes / links) |
  |---|---|---|---|---|
  | 0.97 | 2.2% | 4.7% | 1.6% | 2.1× / 2.9× |
  | 0.98 | 3.5% | 8.9% | 2.7% | 2.5× / 3.3× |
  | 0.99 | 5.2% | 14.6% | 4.0% | 2.8× / 3.6× |

## P3D-E11: Fork v2 for reach, gates and smoke tests (19 Oct 2026)
- **New code:** lazy users (`LazyCands`), `shortest_paths_fast`, U_max from one user per offset, per-hop outputs from multinomial counts, and the presets `fut97/98/99` with radius = reach + 2.
- **Gates** (`sim/evidence/fork_v2_gates.txt`, `test_lazy_output.txt`):
  - Study 34 is reproduced exactly on the default path (2/2) and with lazy users (2/2, before and after the fast enumerator).
  - Lazy lists equal eager lists on 6 lattices.
  - The fast enumerator equals the original on 1,600 random pairs.
  - The Study 3D-1 path is unchanged (identical cloud row).
- **Smoke tests** (exploratory; network 0, fut99, `kg`; `sim/evidence/reach_smoke.txt`):
  - 2D 32×32 at radius 6: 0 bad pairs; success 0.95–1.0 at hops 1–5 and 0.86 at hop 6.
  - 3D 10³ at radius 6: 0 bad pairs; success 0.98–1.0 at hops 1–5 and 0.96 at hop 6.
  - 3D at radius 8: U_max 104, and the guard serves 55% at hop 7 and 7% at hop 8. That is about 26% of uniform demand, against about 21% at radius 6.
- **Cost:** 218–402 s per run in the cloud, and 1.6–2.3 GB of memory.
- **Next:** pre-registration decisions (cost of about 250–400 SU, memory, v2 gate on PSC); see `docs/DESIGN_3D2_REACH.md`.

## P3D-E12: Reach pilot, exploratory (19 Oct 2026)
- **Runs:** 72/72 on the Mac (64 GB, 15 workers, 38 min). Pilot seeds Q3R, 2 networks per cell. Data: `sim/evidence/pilot_reach_runs.csv`.
- **Served share of uniform demand, `kg`, no offset** (2D 32×32 / 2D 37×37 / 3D 10³):
  - fut97: 2.1% / 1.6% / 4.6%;
  - fut98: 3.6% / 2.7% / 10.2%;
  - fut99: 7.6% / 5.7% / 26.0%.
  
  That is 3D / 2D 32×32 = 2.2× / 2.8× / 3.4×, against analytic 2.1 / 2.5 / 2.8.
- **Safety:** 0 bad pairs in every cell, including after the forced alarm and under the always-on margin.
- **Under offset 0.044 the 3D advantage shrinks.** With the always-on margin: fut98 0.79% vs 0.58%; fut99 3.0% vs 1.4%.
- **Cost:** 410–450 s per run on average (at most 540 s, with 15 at once). Peak memory 1.9 GB (2D 32×32) and 2.7–2.9 GB (3D, 2D 37×37).
- **Not evidence for any hypothesis.**

## P3D-E13: Study 3D-2 pre-registration written (19 Oct 2026). Not yet run
- **Plan:** `docs/PREREG_3D2.md`. 3 lattices × 3 link levels × (4 cells × 32 + harm cell × 8) = 1,224 runs on PSC. Seeds 19361–19364, never used before.
- **Hypotheses:**
  - R1 safety (primary);
  - R2: 3D serves more of uniform demand than both 2D lattices at every link level (6 comparisons, Bonferroni);
  - R3: ratio ≥ 1.5;
  - R4: the advantage survives the always-on margin;
  - S1 harm sanity check; S2 certificate falsification test;
  - D1, D2 descriptive.
- **Gate:** `sim/psc3d2/check_v2.sbatch` (6 runs: 4 default + 2 lazy users).
- **Checks before freezing:** the analysis was dry-run on pilot data, and the PSC runner path was tested in the cloud (`sim/evidence/psc3d2_plumbing_test.txt`).
- **Expected cost:** about 400–500 SU; hard cap 1,024 SU.
- **Frozen files:** `sim/psc3d2/HASHES_PREREG_3D2.txt` (14 files). All hashes verified on the Mac.
- **Frozen:** the pre-registration was pushed at commit `7e3dc97` (`origin/main` equals `7e3dc97`) before the PSC gate. Files on PSC: HASHES OK. Gate job 49442164 submitted.

## P3D-E14: Study 3D-2 confirmatory results (19 Oct 2026)
- **Runs:** 1,224/1,224 on PSC. Gate job 49442164 passed (6/6). runs.csv sha256: d2g32 c7ec6fbf…, d3g10 801a9552…, d2g37 b569e80e…
- **R1 safety:** PASS. 0/32 harmed networks everywhere, and 0 bad pairs, with U_max up to 104.
- **R2:** PASS 6/6. Served share of uniform demand, 3D 10³ vs 2D 32×32: 5.0% vs 2.1% (F0 0.97), 10.2% vs 3.7% (0.98), 26.2% vs 7.6% (0.99).
- **R3:** PASS. Ratios 2.33 / 2.78 / 3.46.
- **R4:** PASS 3/3.
- **S1:** PASS. 3D harm without a check is 0.73–0.77, vs 0.65–0.69 on 2D.
- **S2:** PASS.
- **Descriptive:** under offset 0.044 with the always-on margin the 3D advantage falls to 1.4–2.2×; edge-of-reach success in 3D is 0.52 vs 0.32 at 7 hops (F0 0.99).
- **Write-up:** `docs/RESULTS_3D2.md`.

## P3D-E15: Is it dimension, or just shorter distances? Exploratory geometry check (19 Oct 2026)
- **Method:** `analytics/topology_controls.py`. Share of ordered pairs within 3 / 4 / 6 hops (the true-model reach at F0 0.97 / 0.98 / 0.99). Geometry only: no guard, no simulation.

  | Lattice | Degree | Mean hop | ≤ 3 hops | ≤ 4 hops | ≤ 6 hops |
  |---|---|---|---|---|---|
  | 2D grid 32×32 | 4 | 21.3 | 2.2% | 3.5% | 7.1% |
  | 2D torus 32×32 | 4 | 16.0 | 2.3% | 3.9% | 8.2% |
  | 2D king's graph (diagonals) 32×32 | 8 | 14.9 | 4.2% | 6.8% | 13.3% |
  | 3D cube 10³ | 6 | 9.9 | 4.7% | 8.9% | 21.7% |
  | 3D torus 10³ | 6 | 7.5 | 6.2% | 12.8% | 35.5% |

- **Reading:** part of the 3D gain is simply shorter hop distances. A degree-8 2D graph recovers 40–80% of it (80% at a 3-hop reach, 40% at 6 hops), but 3D still wins with fewer links per node (6 vs 8), and its lead grows with reach. Edge effects favour neither strongly.
- **Implication:** a referee-proof claim needs a degree-matched 2D control in simulation (king's graph, or 2D with random shortcuts), plus a statement about physical embedding (link lengths).

## P3D-E16: Fork v3 (king's graph) and Study 3D-3 pre-registration (19 Oct 2026). Not yet run
- **Why:** to check that Study 3D-2's reach gain comes from dimension and not just from more links per node. The control is a 2D 32×32 grid plus both diagonals (3,906 links, up to 8 per node), against the 3D cube (2,700 links, up to 6 per node).
- **Code (v3):**
  - `GRID_KING` with diagonal links and Chebyshev hops;
  - `shortest_paths_king`;
  - U_max from centred placements (king's-graph paths can bulge past the bounding box);
  - per-hop path counts by DP.
- **Tests and gates (cloud):**
  - every king shortest-path list (h ≤ 4) on 4×4, 6×6 and 9×9 matches brute-force BFS, and U_max matches brute force;
  - the per-hop counter matches enumeration for every user (`sim/evidence/test_king_output.txt`);
  - v3 = v2 on a reach task (136 columns);
  - Study 34 is reproduced exactly on the default path and with lazy users (`sim/evidence/fork_v3_gates.txt`).
- **Smoke run** (king's graph, fut99, `kg`, network 0): served share 15.7%, U_max 96, 3.2 GB of memory, 408 s.
- **Pre-registration:** `docs/PREREG_3D3.md`. 408 runs, seeds 19371–19374. It compares against Study 3D-2's frozen runs.csv copies (`sim/reference/s3d2_*`, sha256 verified by the analysis).
  - K1 (primary): 3D > king's graph at every link level. It may fail at F0 0.97, where geometry predicts a ratio of only about 1.1.
  - K2 (primary): safety on the king's graph.
  - K3, K4 (secondary); S1, S2; descriptive outputs.
- **Gate:** `check_v3.sbatch` (2 Study 34 runs on the default path, 1 with lazy users, and 1 Study 3D-2 confirmatory row).
- **Expected cost:** about 190–230 SU; hard cap 512.
- **Frozen files:** `sim/psc3d3/HASHES_PREREG_3D3.txt` (16 files). All match on the Mac.
- **Note:** to reproduce Study 3D-2 exactly, use the fork files from commit `7e3dc97`. The v3 files are checked to give identical rows for it, but their hashes differ.
- **Frozen:** the pre-registration was pushed at commit `1fe2dba` before the gate. Files on PSC: HASHES OK. Gate job 49450927. A first launch attempt, made before the gate finished, was refused by the GATE PASS check, so nothing ran.
- **Gate passed** (job 49450927: 4/4 reproduced exactly, including a Study 3D-2 reach row). Confirmatory array job 49451287 submitted (8 shards × 16 workers on 32 cores).

## P3D-E17: Study 3D-3 confirmatory results, the king's-graph control (19 Oct 2026)
- **Runs:** 408/408 on PSC (array job 49451287); runs.csv sha256 5b38e19d853ad3c7…; analysis `sim/evidence/analysis_3d3.txt`. No deviations.
- **K1 PASS (3/3):** 3D 10³ beats 2D 32×32 + diagonals in `kg -`: 5.0% vs 4.3% / 10.2% vs 7.4% / 26.2% vs 15.3%; ratios 1.16 / 1.38 / 1.71 (geometry-only 1.12 / 1.31 / 1.63).
- **K2 PASS:** 0/32 harmed networks in every cell; 0 bad pairs.
- **K3 PASS:** diagonals double the plain grid (2.0×), recovering 75% / 57% / 42% of the 3D gain.
- **K4 FAIL at F0 0.97** (margin, no offset: +0.0012 [−0.0008, +0.0032]); PASS at 0.98 and 0.99.
- **S1 PASS** (0.64–0.68). **S2 PASS.**
- **Descriptive:** under offset 0.044 the king's graph matches or beats 3D (margin + offset: 3D ÷ king 0.71 / 0.79 / 1.04). Per link, 3D serves 1.7–2.5× the king's graph.
- **Reading:** the reach gain is partly dimension and partly shorter distances; dimension dominates as links improve. Any "3D wins" claim must carry the model-error caveat. Diagonal links were modelled as equal to straight links, which favours the king's graph.
- Write-up: `docs/RESULTS_3D3.md`.

## P3D-E18: Pre-registration timing record (19 Oct 2026)
- **Sources:** `audit/github_activity_2026-10-19.json` (GitHub repository activity log, server-side push times), `audit/github_push_events_2026-10-19.json` (events feed; incomplete, missed the later pushes), `audit/psc_job_times_2026-10-19.txt` (PSC `sacct`; PSC clock is EDT = UTC−4, checked with `date`).
- **S3D-1:** fc3660d pushed 18 Oct 05:13:42 UTC; gate 49402863 submitted 05:46:16; first confirmatory shard (arrays 49423730–2) 21:07:07.
- **S3D-2:** 7e3dc97 pushed 19 Oct 02:27:40; gate 49442164 submitted 02:28:23; first shard (arrays 49442852/4/7) 02:41:55.
- **S3D-3:** 1fe2dba pushed 04:29:40; gate 49450927 submitted 04:30:32; first shard (array 49451287) 04:42:12.
- The repository was private at all these times.

## P3D-E19: Redaction before making the repository public (19 Oct 2026)
- Three evidence files (`sim/evidence/3d2_runs/check_v2_49442164.log`, `sim/evidence/3d3_runs/check_v3_49450927.log`, `sim/evidence/psc_env_3d2.txt`) had the PSC username and charge id replaced by `<psc-user>` and `<charge-id>`, and an unrelated second allocation was removed from the last one. No number, result or hash-listed file changed. The unredacted versions remain in the git history (decision: keep history intact, so the pre-registration commits keep their hashes).
- **Allocation:** the PSC charge id is the PSC name of ACCESS allocation CIS261606 (same title, same resources), which the paper acknowledges.
- **Study 3D-3 cost (from `sacct`):** shard times 39 min–2 h 0 min; about 7.1 shard-hours × 32 cores ≈ 228 SU, inside the expected 190–230. Shard 0 finished 6 s before its 2 h limit: future heavy arrays need a longer limit or more shards.

## P3D-E20: Wording correction after a targeted review (19 Oct 2026); release v1.0.1
- **What a reviewer found:** (1) "Certificate not invalidated" / "not falsified" (RESULTS_3D1–3, and P3D-E7 here) overstates the falsification tests: they did not reject the nominal 5% violation rate; violations occurred (largest lower bound: 4/96 on 2D 32×32 p10, upper bound 0.093; largest upper bound: 3/64 on 3D 5³ p20, 0.117). (2) The pre-registered bad-pair bound pools deliveries as independent, which they are not.
- **Fix:** the falsification rows of RESULTS_3D1–3 now state what the tests established, and each file ends with a dated correction note. The bad-pair bound is labelled as reported for the record; inference rests on 0/32 harmed networks per cell (bound 8.9%). Ledger entries are append-only, so P3D-E7's "(not falsified)" stays as written and is superseded by this entry. The pre-registrations are frozen and unchanged.
- **No verdict, number, run or analysis changed.** Manuscript v0.9 Appendix B.5 carries the same corrections.

