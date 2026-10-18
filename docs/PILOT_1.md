# Pilot 1: 2D vs 3D on the paper's closed loop (exploratory, 18 Oct 2026)

**Status: exploratory.** Dev seeds (blocks `Q3D…`), two networks per cell. No hypothesis is tested here. The pilot decides what to pre-register and checks run times. Its numbers must not be reported as results.

## Lattices
| Label | Lattice | Nodes | Links | Matched with 3D 5³ on |
|---|---|---|---|---|
| A2 | 2D 11×11 | 121 | 220 | nodes (125) |
| B2 | 2D 13×13 | 169 | 312 | links (300) |
| A3 | 3D 5³ | 125 | 300 | (reference) |

## Fixed set-up (unchanged from Study 34)
- **Hardware:** ion2020 (Lmax 2) and ionproj (Lmax 3).
- **Demand:** near-neighbour. Requests go to a random ordered node pair at hop distance 1..Lmax, at the same total rate on every lattice. So this pilot measures **route diversity and guard cost at fixed hop distance**, not the reach benefit of shorter paths (see "Not covered").
- **Six configurations:**
  - `kg` with no offset;
  - `kg` with offset 0.044;
  - hybrid check (p = 0.1) with offset 0.044;
  - the same with a forced early alarm;
  - always-on margin with no offset;
  - always-on margin with offset 0.044.
- **Runs:** 3 lattices × 2 hardware × 6 configurations × 2 networks = 72 runs.

## What we look at
- **Service, at each hop distance h:** served share of users, deliveries per user and the oracle-servable share of requests.
- **Delivered quality:** mean fidelity of kept pairs (`p10_F`) and the bad-pair rate.
- **Guard cost:** U_max, guard blocks per request, and service under the always-on margin.
- **Safety:** bad pairs after an alarm and harmed users per arm. These carry no inference at n = 2.

## Already seen (one network, kg, no offset, ion2020; same pilot seeds)
| | 2D 11×11 | 3D 5³ |
|---|---|---|
| Users (hop 1 / hop 2) | 440 / 796 | 600 / 1,410 |
| Mean shortest paths per 2-hop pair | 1.50 | 1.68 |
| 2-hop users served | 179/796 (22%) | 677/1,410 (48%) |
| Requests an oracle could serve above τ | 52% | 72% |
| Mean kept fidelity | 0.937 | 0.934 |

This first sign points to more choice of routes, not better pairs: 3D serves more users at the same hop count, while the delivered pairs keep about the same fidelity. Both cells are a single network, so this is not evidence.

## Not covered (needs a separate design)
- **Reach** (long requests that become short in 3D) needs a demand model with hop distances beyond the hardware's Lmax. With these presets, pairs beyond 3 hops rarely clear τ. A reach study needs better hardware presets or entanglement distillation, so it is a separate study.
- **Larger lattices** (32×32 vs 10³) only if the pilot shows run times that fit PSC.

## Commands
```bash
cd sim && tools/run_pilot1.sh        # about 2 h on 2 cores; output in sim/out/pilot1/
python3 tools/summarise_pilot1.py    # writes sim/evidence/pilot1_summary.txt
```
