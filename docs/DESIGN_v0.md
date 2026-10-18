# Design note v0: 3D vs 2D topology (draft, not a pre-registration)

## Hypotheses to sharpen before pre-registration
1. **Reach.** At matched node count, a 3D lattice serves a larger share of uniform user pairs above τ. The main reason is the shorter hop distance; P3D-E1 predicts about 2–3× at λ ≈ 0.97.
2. **Matched hardware.** With total links (or memory qubits per node) held fixed, the 3D advantage shrinks. It may change sign on low-rate hardware (NV, SiV), where memory per link matters more than hop count.
3. **Guard cost.** At Lmax = 3, U_max rises from 7 to 12, so the per-user guarantee costs more throughput in 3D. It should still stay valid: 0 harmed users, with network-level bounds as in the paper.
4. **Selection bias.** More shortest-path candidates (6 vs 2 at offset (1,1,1)) make the winner's curse larger. The plug-in rule should fail more often in 3D than in 2D.

## Comparison arms (to fix in the pre-registration)
| Arm | Lattice | Matched quantity |
|---|---|---|
| A | 2D 32×32 vs 3D 10³ | Nodes only |
| B | 3D 10³ vs a 2D grid with the same number of links | Links (2D with some extra links, or a thinned 3D) |
| C | Same comparisons on a small scale (2D 11×11 vs 3D 5³) | Fast pilot |

## Demand model
Uniform random node pairs, plus the current near-neighbour demand (hop distance 1..Lmax). Under the near-neighbour model 3D shows mostly the U_max cost, because requests are already short; under the uniform model 3D shows the reach benefit.

## Simulator changes (fork, never edit the paper's code)
- Generalise `grid_topology` and `shortest_paths` (drift_queue_des_g1) and the correlated-link field (corr_net) to d dimensions. The node coordinates enter the Gaussian kernel unchanged.
- Hard check before any 3D run: with d = 2, the fork must reproduce Study 34's runs.csv rows bit for bit for the same seeds.
- Compute: pilots on the Mac or in the cloud; confirmatory runs on PSC (CIS261606). The user runs all PSC jobs.

## Open decisions for the user
- Hardware types to include. Suggestion: ion2020 and ionproj first, as in the closed-loop studies.
- Whether to include the closed loop (Theorem 2) or only the guard and the certificate.
