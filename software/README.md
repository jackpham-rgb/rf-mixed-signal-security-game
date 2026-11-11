# Reference simulator

This directory contains a small, synthetic correctness scaffold for the model

`Y = H_a L(S, X) + B_d + N_d + W`.

It implements the documented defender actions D0 to D3, observer actions A0 to A3,
basic leakage estimators, finite zero-sum and Bayesian games, an L1
prior-robust solver, and seeded Monte Carlo payoff estimation. It is defensive
research code: secrets are synthetic and the channel is not a calibrated model
of any real device.

## Setup (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest
python -m src.run_experiment --seed 126 --output results/baseline.json
python -m src.run_sweep --seed 126
```

The JSON result records the seed, configuration, dependency versions, payoff
matrix, equilibrium (including its primal-dual gap), and pure-defense
baselines. Run commands from this `software/` directory.

`python -m src.run_sweep` is the value-of-game sweep (about 15 minutes on 4
cores with B = 1000 bootstrap replicates; `--n-boot 200` is a faster check). It writes `results/value_of_game.json`, machine-generated tables in
`results/value_of_game_tables.md`, and PNG figures in `results/figures/`.
`python -m src.run_sweep --quick` runs a tiny smoke-test grid in seconds, and
`python -m src.figures` redraws the figures from an existing results JSON. The
interpretation of the sweep is in `results/VALUE_OF_GAME_RESULTS.md`.

## Model constants

These are modeling choices, not measurements of any device:

| Item | Value |
|---|---|
| Observer actions (gain, ambient noise sd, cost) | A0 (1.00, 1.00, 0.00), A1 (1.30, 1.10, 0.02), A2 (0.80, 0.80, 0.03), A3 (0.90, 0.70, 0.05) |
| Hopping | Leaves a band with probability 0.75 (targeted) and couples at 0.15 when out |
| Overheads | E = 0.13 hop + 0.20 P, T = 0.18 hop, F = 0 |
| Session factors | Log-normal gain (sd 0.15) and noise (sd 0.10), shared across bands |
| Four-band D1 | Deterministic dummy activity (constant offset), E = 0.30; changes no MI |
| Four-band D3 | Hop plus uniform injection at P = 0.75 |
| Library | 213 rows: D0 to D3, then hop x (none or 1/4-lattice allocation x P in {0.75, 1.5, 3}), without duplicates |

## Modules

- `src/channel.py`: synthetic trace generation and definitions of D0 to D3 and A0 to A3.
- `src/metrics.py`: Welch TVLA, binned mutual information, guessing entropy,
  success rate, MI from count tables with a Miller-Madow correction, frozen
  quantile bin edges, and exact (quadrature) MI for Gaussian-mixture channels.
- `src/games.py`: primal/dual minimax LPs, Bayesian epigraph LP (with each
  type's equilibrium observer mixture from the duals), and robust L1-prior
  constraint-generation LP.
- `src/monte_carlo.py`: reproducible empirical payoff matrices.
- `src/run_experiment.py`: command-line baseline experiment.
- `src/band_channel.py`: four-band channel in which a separability knob sets
  how band-specific each defense is, plus a 213-row defender library (D0 to
  D3 and every hop/noise-allocation combination that does not duplicate them),
  exact quadrature MI, and the 36,402-row fine library.
- `src/baselines.py`: baselines B0 to B4 as solvable policies and the adaptive
  observer B5 that best-responds to whatever policy is deployed.
- `src/value_of_game.py`: per-session simulation, cross-fitted policy
  evaluation, session bootstrap, and exact-model validation of the gaps.
- `src/run_sweep.py`: command-line sweep over leakage-to-noise ratio,
  separability, prices, and observer types.
- `src/tables.py`: machine-generated markdown tables from the results JSON.
- `src/provenance.py`: Python and dependency versions written into every result.
- `src/figures.py`: frontier, gap heatmaps, payoff/equilibrium, and validation
  figures, regenerated from the results JSON only.

The binned MI estimator is biased at finite sample sizes: upward from finite
samples and downward from binning. The sweep applies a Miller-Madow correction
and measures both effects against exact quadrature MI, but that does not make
the estimator unbiased in general. TVLA's conventional threshold is a screening
rule, not proof of security. Publication results require calibrated channels,
confidence intervals, held-out adaptive evaluation, and estimator-bias analysis.
