# Study 3D-2 results: reach under uniform demand, link-quality sweep (19 Oct 2026)

**Status:** confirmatory, as pre-registered in `docs/PREREG_3D2.md` (frozen at commit `7e3dc97`).
- **Gate:** passed on PSC (job 49442164; 6/6 Study 34 runs exact, 4 default and 2 with lazy users).
- **Runs:** 1,224/1,224 on PSC Bridges-2.
- **Output:** `sim/evidence/analysis_3d2.txt`.
- **runs.csv sha256:** d2g32 c7ec6fbf…, d3g10 801a9552…, d2g37 b569e80e… (the full values are printed by the merge and match the downloaded files).
- **No deviations from the plan.**

## Verdicts
| | Hypothesis | Verdict |
|---|---|---|
| **R1** (primary) | Safety holds at reach (Theorem 2 after a forced alarm; Corollary 3 always-on), with U_max up to 104 | **PASS.** 0/32 harmed networks in every lattice × link level × arm. 0 bad pairs in about 3.8 million guarded deliveries (0.58 million after alarms, 3.2 million under the margin) |
| **R2** (primary) | 3D serves a larger share of uniform demand than both 2D lattices, at every link level | **PASS (6/6)** |
| R3 (secondary) | 3D / 2D 32×32 ratio ≥ 1.5 | **PASS.** 2.33 / 2.78 / 3.46 (analytic 2.1 / 2.5 / 2.8) |
| R4 (secondary) | The advantage survives the always-on margin | **PASS (3/3)** |
| S1 (prediction) | With no check, offset 0.044 harms > 10% of served users | **PASS.** 0.65–0.69 on 2D; **0.73–0.77 on 3D** |
| S2 (falsification) | Certificate not invalidated | **PASS** (largest lower bound 0.014 < 0.05) |

## Served share of uniform all-pairs demand (`kg`, no offset; mean over 32 networks)
| Link F0 | 2D 32×32 | 2D 37×37 (matched links) | **3D 10³** | 3D ÷ 2D 32×32 |
|---|---|---|---|---|
| 0.97 | 2.1% | 1.6% | **5.0%** | 2.3× |
| 0.98 | 3.7% | 2.7% | **10.2%** | 2.8× |
| 0.99 | 7.6% | 5.7% | **26.2%** | 3.5× |

## What this means (plain language)
1. **Reach is where 3D pays off.** When users are spread across the whole network, a cube serves 2.3–3.5× more of their requests than a flat grid with the same number of nodes, and even more against a grid with the same number of links. The gain grows with link quality.
2. **The gain is larger than the simple formula predicted.** At the edge of reach the extra route choice helps. For example, at F0 0.99, 7-hop requests succeed 52% of the time in 3D against 32% in 2D, and 8-hop requests 8.5% against 3%. This differs from Study 3D-1: route choice did little for short requests, but at the edge of reach it matters.
3. **Safety holds even with very large routing budgets.** A 3D user could be routed over up to 104 links, yet the guarantees held everywhere.
4. **The price of an unchecked model error is also higher in 3D.** With no check, an optimistic model harmed about 75% of 3D's served users against about 66% in 2D. More reach means more users exposed.
5. **Under a model error, the safety margin keeps users safe but much of the 3D advantage goes.** With the always-on margin and offset 0.044, 3D still serves 1.4× / 1.6× / 2.2× the share of 2D 32×32, down from 2.3–3.5× with a correct model.
6. **Fidelity of delivered pairs is about the same** (0.930–0.931 in 3D vs 0.934–0.936 in 2D). 3D delivers more long-distance pairs, which sit closer to the threshold.

## Scope
- **Projected link hardware** (ionfut's rate, memory and gates, with F0 0.97–0.99), simplified physics and one purification round.
- **One lattice size** of about 1,000 nodes, with requests served one at a time and the same servable request rate on every lattice.
- **This is a simulation result about topology,** not a hardware forecast.
