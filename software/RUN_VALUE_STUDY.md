# Running the value-of-game study

These commands reproduce every number and figure in
`results/VALUE_OF_GAME_RESULTS.md`. Run them in PowerShell from this
`software/` directory. All secrets are synthetic and nothing here touches real
hardware.

## 1. Environment

```powershell
cd software
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If `.venv` already exists, only the `Activate.ps1` and `pip install` lines are
needed.

## 2. Tests

```powershell
python -m pytest
```

Expected: all tests pass (25 at the time of writing, a few seconds).

## 3. Smoke test of the sweep (seconds)

```powershell
python -m src.run_sweep --quick --output results/quick/value_of_game.json --figures results/quick/figures --tables results/quick/tables.md
```

The quick grid is far too small to support any conclusion; it only checks the
pipeline.

## 4. Confirmatory sweep

```powershell
$env:OMP_NUM_THREADS = "1"; $env:OPENBLAS_NUM_THREADS = "1"; $env:MKL_NUM_THREADS = "1"
python -m src.run_sweep --seed 126 --workers 4
```

Pinning BLAS threads to 1 avoids oversubscription when several worker processes
run. Runtime is roughly 15 minutes on 4 cores (400 grid points, 1000
session-bootstrap replicates each, plus the exact-model and fine-library
phases). The bootstrap dominates; `--n-boot 200` gives a faster check.
Use `--workers` to match your core count; results do not depend on it because
every (A, s) dataset has its own seed stream.

Outputs:

- `results/value_of_game.json`: full results, configuration, seeds, versions.
- `results/value_of_game_tables.md`: machine-generated tables (every grid point).
- `results/figures/fig_A_frontier.png`: leakage vs energy frontier.
- `results/figures/fig_B_gap_robust_heatmap.png`: gap_robust heatmap.
- `results/figures/fig_B_supp_gap_pure_heatmap.png`: gap_pure heatmap.
- `results/figures/fig_C_payoff_equilibrium.png`: payoff matrix and equilibrium.
- `results/figures/fig_D_validation.png`: estimates vs the exact model.

To redraw figures from an existing JSON without rerunning:

```powershell
python -m src.figures --results results/value_of_game.json --figures results/figures
```

Note: `results/` is gitignored except for `VALUE_OF_GAME_RESULTS.md`,
`value_of_game_tables.md`, and the PNG figures. The large JSON stays
local; regenerate it with the command above.
