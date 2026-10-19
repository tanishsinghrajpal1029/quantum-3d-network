# Study 3D-3 results: the king's-graph control (is the reach gain about dimension or about degree?) (19 Oct 2026)

**Status:** confirmatory, as pre-registered in `docs/PREREG_3D3.md` (frozen at commit `1fe2dba`).
- **Gate:** passed on PSC (job 49450927; 4/4 exact: 2 Study 34 default, 1 Study 34 lazy, 1 Study 3D-2 reach row).
- **Runs:** 408/408 on PSC Bridges-2 (array job 49451287).
- **Output:** `sim/evidence/analysis_3d3.txt`. Study 3D-2 references verified by sha256 inside the analysis.
- **runs.csv sha256:** 5b38e19d853ad3c7aa22e01d6a3b618499f888a74f358470f053edf2c000eb64.
- **No deviations from the plan.**

## Verdicts
| | Hypothesis | Verdict |
|---|---|---|
| **K1** (primary) | 3D 10³ serves more of uniform demand than the king's graph (2D 32×32 + diagonals), every link level | **PASS (3/3).** Ratios 1.16 / 1.38 / 1.71 (geometry-only 1.12 / 1.31 / 1.63) |
| **K2** (primary) | Safety on the king's graph (gated after alarm; always-on margin) | **PASS.** 0/32 harmed networks in every cell; 0 bad pairs in about 1.5 million guarded deliveries |
| K3 (secondary) | Degree helps in 2D: king's graph > plain 2D grid | **PASS (3/3).** The king's graph serves 2.0× the plain grid at every link level |
| K4 (secondary) | The 3D lead over the king's graph survives the always-on margin (no offset) | **FAIL at F0 0.97** (diff +0.0012 [−0.0008, +0.0032]); PASS at 0.98 and 0.99 |
| S1 (prediction) | No check, offset 0.044 harms > 10% of served users on the king's graph | **PASS** (0.64–0.68) |
| S2 (falsification) | Certificate not invalidated on the king's graph | **PASS** (largest lower bound 0.009 < 0.05) |

## Served share of uniform all-pairs demand (`kg`, no offset; mean over 32 networks)
| Link F0 | 2D 32×32 (1,984 links) | **2D + diagonals (3,906 links)** | **3D 10³ (2,700 links)** | 3D ÷ king | Share of the 3D gain over the grid that diagonals recover |
|---|---|---|---|---|---|
| 0.97 | 2.1% | 4.3% | 5.0% | 1.16 | 75% |
| 0.98 | 3.7% | 7.4% | 10.2% | 1.38 | 57% |
| 0.99 | 7.6% | 15.3% | 26.2% | 1.71 | 42% |

Per 1,000 links, 3D serves 1.7× / 2.0× / 2.5× as much as the king's graph.

## Descriptive, not pre-registered as a test: under a model error the king's graph matches or beats 3D
| Link F0 | `kg o0.044` (8 networks), 3D ÷ king | `kgMCa o0.044` (margin + offset, 32 networks), 3D ÷ king |
|---|---|---|
| 0.97 | 0.89 | 0.71 |
| 0.98 | 0.93 | 0.79 |
| 0.99 | 1.27 | 1.04 |

No intervals were pre-registered for these cells, so they are descriptive.

## What this means (plain language)
1. **Dimension matters, not just extra links.** A 2D grid with both diagonals has 45% more links than the cube and higher degree (8 vs 6), yet the cube still serves more, at every link quality. The lead grows with link quality (1.16× → 1.71×).
2. **But a lot of 3D's gain over a plain grid is available in 2D.** Adding diagonals doubles what a flat grid serves. That recovers 42–75% of the 3D gain, most of it when links are weakest. The honest summary is: "short distances explain much of the gain at F0 0.97; dimension explains more as links improve."
3. **3D uses links far more efficiently:** about 2× the served share per link.
4. **The geometry predicted these ratios well** (within about 0.1). Simulated ratios sit slightly above the geometry-only ratios, as in Study 3D-2.
5. **Safety holds on the king's graph too**, with up to 96 routes per user.
6. **Under a model error, 3D's edge over the king's graph disappears at F0 0.97–0.98.** With the margin and offset 0.044, the king's graph serves more (3D ÷ king 0.71 / 0.79 / 1.04). K4 (margin, no offset) also fails at F0 0.97. A possible reason, not tested: 3D's extra share comes from long requests near the edge of reach, and those are the first that the margin turns away. This should be stated as a limitation of any "3D is better" claim.
7. **Caveat in favour of 3D's opponent:** diagonal links are modelled with the same quality as straight links. Physically they are √2 longer and would usually be worse. So the king's graph here is a generous control.

## Scope
- As Study 3D-2: projected link hardware (ionfut rate, memory and gates; F0 0.97–0.99), simplified physics, one purification round, about 1,000 nodes, serial service, same servable request rate on every lattice.
- The king's-graph runs use independent networks from Study 3D-2's, on the same platform and code paths (the gate checks the code).
- Success per servable request at 1–2 hops is reported as 1.00–1.01; the small excess is sampling noise in the expected-request denominator.
