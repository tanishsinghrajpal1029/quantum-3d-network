# Files12-3D-Network: does a 3D network topology deliver better entanglement?

A separate project from the quantum_grid_router paper. It reuses ideas and, later, a forked copy of the simulator. It never edits the paper's files.

## Question
At a matched number of nodes, does a 3D cubic lattice deliver more usable entanglement (above a fidelity threshold τ) than a 2D square grid? Three things decide this:
- **Fewer hops:** shorter paths mean fewer entanglement swaps and less time in memory.
- **More candidate paths:** better routing choices.
- **What it costs:**
  - more links per node, so more hardware;
  - a larger U_max, so the guard needs a stricter per-link budget α/U_max;
  - more selection bias (the winner's curse) when routes are chosen from data.

## Rules (same discipline as the paper)
- Pre-register every confirmatory run before it starts: hypotheses, pass bars, locked analysis script.
- Keep and report failures. Number every result in `LEDGER.md`.
- Pilots and analytics are labelled exploratory.
- The user runs all PSC and IBM commands; this project never handles credentials.
- The repository stays **private** until the authors decide otherwise.

## Layout
| Folder | Contents |
|---|---|
| `analytics/` | Exact counts and toy fidelity formulas, with no simulation (`lattice_baseline.py`) |
| `docs/` | Design notes and pre-registrations |
| `sim/` | (next) forked simulator with a d-dimensional lattice topology |
| `studies/` | (later) one folder per pre-registered study |

## Status
- **D1 (exploratory analytics):** done. See `analytics/lattice_baseline_output.txt` and `LEDGER.md` P3D-E1.
- **Next:** fork the simulator, generalise the topology to d dimensions, and check that the 2D case reproduces Study 34 exactly before running any 3D case.
