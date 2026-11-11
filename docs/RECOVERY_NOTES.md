# Recovery notes (2026-11-11)

The laptop that held this project broke. What survived was one text file with
the project documentation pasted end to end. This note records what was
restored as-is, what was rebuilt, and what is now different, so no later
reader mistakes a rebuilt number for an original one.

## Restored as-is (text unchanged, only split back into files)

| File | Notes |
|---|---|
| `README.md` | Two links updated (results paths below). |
| `research-project-master-plan.txt` | |
| `CLAUDE.md` | |
| `theory/model-and-proof-roadmap.md` | One link updated. |
| `theory/high-volume-data-and-digital-circuit-extension.md` | |
| `experiments/simulation-and-bench-plan.md` | |
| `literature/novelty-search-log.md` | |
| `paper/paper-outline.md` | |
| `paper/related-work-nearest-table.md` | File name taken from the references in the search log. |
| `docs/public-tool-roadmap.md` | |
| `software/README.md`, `software/RUN_VALUE_STUDY.md` | Updated for the rebuild (version, row count, test count, runtime). |
| `software/results/archive/v0.2.0/` | The original results write-up and generated tables, with an archive notice on top. |

## Rebuilt from the documentation

All Python under `software/` (simulator 0.3.0). The module list, model
equations, grid, baselines, estimators, seeds, and outputs follow
`software/README.md`, `software/RUN_VALUE_STUDY.md`, and the archived results
write-up. The surviving text did not contain these details, so they are new
choices:

| Item | Rebuilt choice |
|---|---|
| Observer actions (gain, ambient noise sd, cost) | A0 (1.00, 1.00, 0.00), A1 (1.30, 1.10, 0.02), A2 (0.80, 0.80, 0.03), A3 (0.90, 0.70, 0.05) |
| Scalar scaffold D1 to D3 | Fixed dummy: injected variance (1.0, 0.3, 0.3, 0.1) per band, E = 0.28. Random frequency: hop-out (0.30, 0.75, 0.75, 0.30), E = 0.13, T = 0.18. Shaped stochastic: both, variance (0.6, 0.4, 0.4, 0.4), E = 0.36, T = 0.18 |
| Four-band D1 | Deterministic structured activity (a constant offset), E = 0.30. It changes no MI. This matches the archived table, where B1 leaks the same as B0. |
| Four-band D3 | Hop plus uniform injection at P = 0.75 |
| Library size | 213 rows, not 212. Rows 0 to 3 are D0 to D3; rows that duplicate D0, D2, or D3 are dropped from the rest. How the original reached 212 is not recoverable. |
| Session factors | Shared across bands within a session |
| Simulation | Common random numbers across library rows that share a band, which lowers the variance of gaps between rows |

The fine library (36,402 rows for s > 0, 82 at s = 0) matches the documented
count exactly.

## What this means for the results

- The archived 0.2.0 numbers (28 of 400 significant points, 7 after
  Bonferroni) cannot be reproduced bit for bit, because the code and constants
  that produced them are gone.
- `software/results/VALUE_OF_GAME_RESULTS.md` reports the rebuilt run with the
  same seed, grid, and decision rule. Where the two runs agree in direction,
  that is weak independent support. Where they differ, the rebuilt run is the
  one that can be reproduced, and it is the one to cite.
- No claim in the paper outline may use an archived number unless it is
  regenerated with the current code.

## Next steps once the old laptop is repaired

1. Copy the original `software/src/` into `private/recovered-v0.2.0/` (local
   only) and diff it against the rebuild, constant by constant.
2. If the original constants are recovered, set them in `src/channel.py` and
   `src/band_channel.py`, rerun the sweep, and check whether the archived
   counts come back.
3. Record the outcome here and in the results write-up.
