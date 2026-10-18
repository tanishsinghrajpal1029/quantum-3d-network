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
