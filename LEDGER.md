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
