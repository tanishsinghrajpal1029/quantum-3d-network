# Study 3D-1 results: 2D vs 3D lattices under the paper's closed loop (18 Oct 2026)

**Status:** confirmatory, as pre-registered in `docs/PREREG_3D1.md` (frozen at commit `fc3660d`).
- **Gate:** passed (P3D-E6).
- **Runs:** 1,344/1,344 on PSC Bridges-2.
- **Output:** `sim/evidence/analysis_3d1.txt` (with the runs.csv sha256 values).
- **One execution deviation, logged before any output:** 8 shards instead of 4. It cannot change a result.

## Verdicts
| | Hypothesis | Verdict |
|---|---|---|
| **H1** (primary) | Safety guarantees carry over to 3D (Theorem 2 after an alarm; Corollary 3 always-on) | **PASS.** 0/32 harmed networks in every lattice × hardware × arm (bound 0.089). 0 bad pairs in about 3.5 million guarded deliveries |
| **H2** (primary) | 3D serves more of the longest requests than both 2D lattices (4 comparisons) | **FAIL (1/4).** Only ionproj vs 2D 13×13 passes (+0.091 [+0.010, +0.170]) |
| **H3** (secondary) | Delivered fidelity unchanged within ±0.01 | **PASS.** 3D is lower by 0.002–0.003. The interval excludes 0 but lies well inside the margin |
| S1 (prediction) | Detection carries over: alarm rate within 0.15 | **ion2020 FAIL** (3D 0.69 vs 2D 0.97); ionproj PASS (0.97 vs 1.00) |
| S2 (prediction) | With no check, offset 0.044 harms > 10% of served users | **PASS** everywhere (0.68–0.74) |
| S3 (falsification) | The certificate's nominal 5% violation rate is not rejected (FAIL only if the CP95 lower bound > 0.05) | **PASS** (not rejected). Violations did occur: 3D p20 3/64 (lower 0.013, upper 0.117) |

## What this means (plain language)
1. **Safety holds in 3D.** The guard and the check keep their guarantees on a cube as on a grid, even though a 3-hop user in 3D can be routed over 12 links instead of 7.
2. **Extra route choice is a weak lever.** At the same hop distance, 3D gives more alternative routes: 3.4 vs 2.3 per 3-hop pair, and 1.7 vs 1.5 per 2-hop pair.
   - On 2-hop hardware (ion2020) this did not raise the success of the hardest requests at all: 0.164 vs 0.172 and 0.186.
   - On 3-hop hardware (ionproj) the gain was about +0.07 to +0.09. It was significant only against the 2D grid with the same number of links.
   - Pilot 1 (2 networks per cell) had overestimated the effect: +0.05 to +0.25 there, against −0.02 to +0.09 here.
3. **3D does not make better pairs.** Mean delivered fidelity was 0.935 vs 0.937–0.938.
4. **Detection was slower on 3D ion2020:** 69% of networks alarmed within the run, against 97% on 2D. The pilot hinted at this (0/2 vs 2/2). The cause is not established (see the exploratory follow-up).
5. **The pilot's oddity was noise.** 2D 13×13 vs 11×11 shows no difference (D4: +0.015 and −0.019, both intervals include 0).

## Scope
- Demand is near-neighbour (1–3 hops), so this study tests route diversity at a fixed hop distance, not the "shorter paths" benefit of 3D (P3D-E1).
- Two ion presets; simplified physics; requests served one at a time; one lattice size (about 125 nodes).
- These findings do not transfer to the reach question, which needs better links or distillation.

## Exploratory follow-ups (not pre-registered; to be labelled as such)
- Why detection is slower on 3D ion2020: compare tests per network, deliveries and the timing of the first alarm across lattices (needs the runs.csv files from PSC).
- A reach study with long-distance demand on better hardware presets.

## Correction (19 Oct 2026)
The falsification row originally read "Certificate not invalidated". A test that does not reject the certificate's nominal 5% violation rate shows neither that no violations occurred nor that the rate is below 5%, so the row now states what the test established. The bad-pair bound in the pre-registered safety bars pools all guarded deliveries of a cell as if they were independent; deliveries of one network share its links, calibration data and history, so that bound is reported for the record only. The inferential safety statement is the network-level one (0 of 32 harmed networks in every cell, one-sided 95% bound 8.9%, networks independent); the count of bad pairs is descriptive. No verdict, number or run changed. See LEDGER P3D-E20.
