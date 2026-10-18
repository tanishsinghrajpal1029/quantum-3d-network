# Design note: Study 3D-2, reach (draft, not a pre-registration; 18 Oct 2026)

## Why a second study
Study 3D-1 tested near-neighbour demand (1–3 hops), where 3D only adds route choice, and that turned out to be a weak lever. The main argument for 3D is **reach**: in 3D a random pair of users is about half as many hops apart (9.9 vs 21.3 at 1,000 nodes), so more pairs are close enough to serve. Today's presets cannot use that: with ion2020 links only 1-hop pairs clear τ = 0.9, and with ionproj only up to 3 hops. A reach study therefore needs better links.

## Exploratory analytic baseline (P3D-E8; `analytics/reach_baseline.py`, output in `reach_baseline_output.txt`)
- **Model:** the paper's physics model (two chains plus one purification round, memory dephasing, gate error) with homogeneous links. The guard is approximated by a confidence bound at level α/U_max.
- **Purpose:** an optimistic guide, not a result.

| Preset | Max hop, true F ≥ 0.9 | Max hop with guard | 2D 32×32 | 3D 10³ | 2D 37×37 (matched links) |
|---|---|---|---|---|---|
| ion2020 (F0 0.94) | 1 | 1 | 0.4% | 0.5% | 0.3% |
| ionproj (F0 0.97) | 3 | 2 | 1.1% | 2.0% | 0.8% |
| **ionfut (F0 0.99, 1,000 pairs/s)** | **6** | **5** | **5.2%** | **14.6%** | **4.0%** |

The shares are for uniform demand with the guard. With `ionfut` links, 3D serves about **2.8×** the share of uniform demand at matched nodes, and **3.6×** at matched links. The guard's extra cost in 3D is mild: U_max is 33 vs 17, but the per-link bound grows only with log U, so the guard gives up 1 hop on both lattices.

## Proposed design (to be fixed in a pre-registration after a pilot)
- **Hardware:** `ionfut` (F0 0.99, R 1,000/s, T2 1 s, gate error 0.003). It is the paper's existing projected preset (`drift_queue_des_v15.IONFUT`). Lmax = 6, the true-model reach.
- **Lattices:** 2D 32×32 · 3D 10³ (matched nodes) · 2D 37×37 (matched links).
- **Demand:** uniform random ordered pairs over all nodes. Pairs beyond Lmax count as requested but not servable.
- **Primary outcome:** share of uniform-demand requests delivered above τ, per network.
- **Arms:** `kg` (no offset); `kgMCa` and `kgMChN` with offset 0.044 (safety).
- **Hypotheses (draft):**
  - (R1) safety carries over with U_max ≈ 33;
  - (R2) the 3D served share exceeds both 2D lattices;
  - (R3) the size of the reach gain, as a prediction band from the analytic baseline;
  - (R4) the guard's cost relative to the exact model.

## Engineering needed (fork v2)
1. **Lazy users.** With Lmax = 6, 3D 10³ has about 217k users, too many to precompute candidate path lists for. Users and their candidates must be computed on first request and cached. (Today every candidate list is built at start-up.)
2. **Routing without enumeration.** Up to 90 shortest paths per pair (6!/(2!·2!·2!)). The best path on current estimates can come from dynamic programming over the pair's box, which is exact. At Lmax ≤ 3 the existing enumeration must stay, so Study 34 and Study 3D-1 still reproduce.
3. **U_max in closed form,** from the per-offset union of shortest-path links, instead of a set union over all candidates.
4. **Scaling checks** for the correlated-link generator (O(NL²) neighbour lists for about 2,700 links) and run time per run.
5. **Gates:** the existing d = 2 Study 34 check, plus a new check that DP routing and enumeration pick the same path on all pairs up to 4 hops.

## Not decided yet (for Tanish and Mike)
- Is a projected preset acceptable as the headline, or should the study sweep F0 (0.97 / 0.98 / 0.99) to show where 3D starts to pay off?
- Include purification beyond one round (would extend reach)?
- Compute: likely PSC. Run time must be measured after the fork.
