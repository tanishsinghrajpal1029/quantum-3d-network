# Design note: Study 3D-2, reach (draft, not a pre-registration; updated 19 Oct 2026)

## Why a second study
Study 3D-1 tested near-neighbour demand (1–3 hops), where 3D only adds route choice, and that turned out to be a weak lever. The main argument for 3D is **reach**: at 1,000 nodes a random pair of users is 9.9 hops apart in 3D against 21.3 in 2D. Today's presets cannot use this: with ion2020 links only 1-hop pairs clear τ = 0.9, and with ionproj up to 3 hops. A reach study needs better links, so we sweep link quality.

## Analytic link-quality sweep (P3D-E10; `analytics/reach_baseline.py` with `REACH_SWEEP=1`, output in `reach_sweep_output.txt`)
- **Presets:** the paper's `ionfut` rate, memory and gates (R 1,000/s, T2 1 s, gate error 0.003), with link fidelity F0 = 0.97 / 0.98 / 0.99.
- **Model:** homogeneous links and a guard approximated by a bound at level α/U_max. This is an optimistic guide, not a result.

| Link F0 | Reach (true model) | Reach with guard | 2D 32×32 | **3D 10³** | 2D 37×37 (matched links) | 3D ÷ 2D (nodes / links) |
|---|---|---|---|---|---|---|
| 0.97 | 3 hops | 3 | 2.2% | **4.7%** | 1.6% | 2.1× / 2.9× |
| 0.98 | 4 | 4 | 3.5% | **8.9%** | 2.7% | 2.5× / 3.3× |
| 0.99 | 6 | 5 | 5.2% | **14.6%** | 4.0% | 2.8× / 3.6× |

The shares are of uniform demand served with the guard. The 3D advantage grows with link quality, and is already about 2× at F0 = 0.97.

## Fork v2 (done, 19 Oct): what changed and how it was checked
- **Lazy users** (`LazyCands` in `fork/drift_queue_des_g1.py`): user lists are built on first request, in exactly the eager order. With radius 8, 3D 10³ has 388k users, which cannot be precomputed.
- **Fast path enumeration** (`shortest_paths_fast`): it generates each distinct shortest path once, and returns the same sorted list as the original. It is used only with lazy users.
- **U_max from one user per distinct offset:** exact, because a user's link union depends only on its offset.
- **Per-hop outputs without building every list,** using multinomial path counts.
- **Reach presets** `fut97/98/99` with service radius = analytic reach + 2 (5/6/8). The network attempts requests beyond the analytic reach, so the guard decides and reach becomes an *outcome*, not an input.
- **Gates:** all pass (`sim/evidence/fork_v2_gates.txt`, `test_lazy_output.txt`):
  - the default path reproduces 2/2 Study 34 runs exactly;
  - lazy users reproduce 2/2 Study 34 runs exactly, before and after the fast enumerator;
  - lazy lists equal eager lists entry for entry on 6 lattices;
  - the fast enumerator equals the original on 1,600 random pairs;
  - the Study 3D-1 path is unchanged (a cloud re-run gives the identical row).

## Smoke tests (exploratory, network 0, no offset; `sim/evidence/reach_smoke.txt`)
| fut99, `kg` | Servable users | U_max | Success at hops 1–5 | Hop 6 | Hop 7 | Hop 8 | Run time (cloud) | Memory |
|---|---|---|---|---|---|---|---|---|
| 2D 32×32, radius 6 | 7.1% of pairs | 24 | 0.95–1.0 | 0.86 | – | – | 218 s | 1.6 GB |
| 3D 10³, radius 6 | 21.7% | 54 | 0.98–1.0 | 0.96 | – | – | 255 s | 2.1 GB |
| 3D 10³, radius 8 | 38.9% | 104 | 0.94–1.0 | 0.95 | **0.55** | **0.07** | 402 s | 2.3 GB |

- The guard serves part of the 7-hop demand, so the wider radius matters: about 26% of uniform demand served vs about 21% at radius 6.
- A doubled U_max (104) did not reduce success at hops 1–6 in this run.

## Proposed design (to fix in a pre-registration)
- **Hardware:** fut97, fut98 and fut99, with radius = reach + 2.
- **Lattices:** 2D 32×32 · 3D 10³ (matched nodes) · 2D 37×37 (matched links).
- **Demand:** uniform over all ordered pairs. Servable requests (within the radius) arrive at Γ = 3/s on every lattice; requests beyond the radius use no resources. Served share of uniform demand = servable share × success per request.
- **Primary outcomes:** (R1) safety, with the same bars as Study 3D-1; (R2) the 3D served share above both 2D lattices, at each F0.
- **Secondary:** (R3) the analytic baseline as a prediction band; (R4) the margin cost.
- **Arms:** `kg` (no offset); `kgMCa` (no offset and offset 0.044); `kgMChN` with offset 0.044 and a forced alarm.
- **Size:** 32 networks per cell, as before. 3 F0 × 3 lattices × 4 arms × 32 = 1,152 runs. At about 600–900 s per run on PSC, that is about 200–300 core-hours, so **roughly 250–400 SU**.

## Open decisions (for Tanish and Mike)
1. Is the cost (about 250–400 SU) acceptable? Alternatives: drop the matched-links lattice, or use 16 networks for the secondary F0 levels.
2. **Memory:** about 2.3 GB per run in 3D, but RM-shared gives 2 GB per core. Run 12 workers on 16 cores, at the cost of some idle cores.
3. **PSC gate for v2:** rerun `check_d2.sbatch`, plus a new lazy-users gate, before any confirmatory job.
