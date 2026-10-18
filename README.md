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
- **D2 (simulator fork):** done. At d = 2 it reproduces Study 34 bit for bit (4/4 runs, 83 columns). A 3D smoke test runs. See `sim/README.md` and `LEDGER.md` P3D-E2 and P3D-E3.
- **D3 (Pilot 1, exploratory):** done. 72 runs on the Mac. See `docs/PILOT_1.md` and `LEDGER.md` P3D-E4.
- **Next:** pre-register Study 3D-1 (hypotheses, lattices, 32 networks per stratum, platform), then run on PSC.
