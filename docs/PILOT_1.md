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

## Results (18 Oct 2026; 72/72 runs on Tanish's Mac, 15 workers, 11.5 min). EXPLORATORY.
Full tables: `sim/evidence/pilot1_summary.txt` and `sim/evidence/pilot1_perhop.txt`.
- **Fair per-request measure.** The total request rate is fixed, but the user count differs (ion2020: 1,236 / 1,772 / 2,010 users), so per-user shares are diluted differently on each lattice. We therefore use **success per request at each hop distance**: deliveries at hop h divided by the expected requests at hop h.
- **Longest-hop success, no check, no offset (`kg`):**

  | Hardware, hop | 2D 11×11 | 2D 13×13 | 3D 5³ |
  |---|---|---|---|
  | ion2020, 2 hops | 0.21 | 0.11 | 0.26 |
  | ionproj, 3 hops | 0.70 | 0.59 | 0.84 |

  Shorter requests succeed almost always on every lattice.
- **Route choice:** mean shortest paths per pair are 1.50 → 1.68 at 2 hops and 2.34 → 3.42 at 3 hops. U_max (ionproj) is 7 → 12.
- **Delivered fidelity is unchanged:** mean kept fidelity is 0.937 / 0.937 / 0.934 (ion2020, `kg`). 3D serves more requests, not better pairs.
- **Always-on margin, no offset:**
  - ionproj 3-hop success: 0.26 / 0.20 / 0.33.
  - ion2020 2-hop success: 0.048 / 0.006 / 0.022, so the margin cost is mixed.
- **Safety:** 0 bad pairs after an alarm, and 0 bad pairs under the always-on margin, on every lattice and hardware.
- **Detection (one cell):** ion2020 with offset 0.044 and the hybrid check alarmed in 2/2 networks on both 2D lattices and in 0/2 on 3D. We need to watch this; n = 2.
- **Unexplained:** 2D 13×13 does worse than 11×11 per request. Possible causes are network-to-network variation or larger-grid effects. Check this in the next run.
- **Platform:** the same 6 tasks run in the cloud (Linux) and on the Mac (macOS) give close but not identical values (`sim/evidence/pilot1_mac_vs_cloud.txt`). Tiny floating-point differences change a route choice and the runs diverge. Bit-for-bit reproduction therefore holds only on one platform: confirmatory runs and their d = 2 check must run on the same machine type.
- **Bug found and handled:** ion2020 and ionproj rows had different column sets in the appended CSVs. `sim/tools/load_runs.py` re-keys them exactly, and `study3d.py` now always writes the columns h1–h3.
