"""Baseline experiment on the original 4 x 4 scalar scaffold.

    python -m src.run_experiment --seed 126 --output results/baseline.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from . import __version__
from .channel import DEFENDER_ACTIONS, OBSERVER_ACTIONS
from .games import best_pure, solve_zero_sum
from .monte_carlo import payoff_matrix
from .provenance import environment_record


def run(seed: int, n_runs: int, n_traces: int, lambda_e: float, lambda_l: float) -> dict:
    pm = payoff_matrix(seed, n_runs=n_runs, n_traces=n_traces, lambda_e=lambda_e, lambda_l=lambda_l)
    M = pm["M"]
    sol = solve_zero_sum(M)
    d_star, v_pure = best_pure(M)
    names_d = [d.name for d in DEFENDER_ACTIONS]
    names_a = [a.name for a in OBSERVER_ACTIONS]
    return {
        "simulator_version": __version__,
        "seed": seed,
        "config": {"n_runs": n_runs, "n_traces": n_traces, "lambda_E": lambda_e,
                   "lambda_L": lambda_l, "lambda_F": 0.0, "n_bins": 16, "estimator": "binned MI, Miller-Madow"},
        "environment": environment_record(),
        "defender_actions": names_d,
        "observer_actions": names_a,
        "payoff_matrix": M.round(6).tolist(),
        "payoff_se": pm["se"].round(6).tolist(),
        "mi_bits": pm["mi"].round(6).tolist(),
        "equilibrium": {
            "p": dict(zip(names_d, sol.p.round(6).tolist())),
            "q": dict(zip(names_a, sol.q.round(6).tolist())),
            "value": sol.value,
            "dual_value": sol.dual_value,
            "primal_dual_gap": sol.gap,
        },
        "pure_baselines": {
            "worst_case_loss": dict(zip(names_d, M.max(axis=1).round(6).tolist())),
            "best_pure": names_d[d_star],
            "best_pure_value": v_pure,
        },
        "in_sample_gap_pure": v_pure - sol.value,
        "largest_cell_se": float(pm["se"].max()),
        "note": "Synthetic scaffold. Not evidence for publication.",
    }


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=126)
    ap.add_argument("--runs", type=int, default=30)
    ap.add_argument("--traces", type=int, default=4000)
    ap.add_argument("--lambda-e", type=float, default=0.3)
    ap.add_argument("--lambda-l", type=float, default=0.2)
    ap.add_argument("--output", default="results/baseline.json")
    args = ap.parse_args(argv)
    res = run(args.seed, args.runs, args.traces, args.lambda_e, args.lambda_l)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2))
    eq = res["equilibrium"]
    print(f"game value {eq['value']:.4f} (gap {eq['primal_dual_gap']:.1e}); "
          f"best pure {res['pure_baselines']['best_pure']} {res['pure_baselines']['best_pure_value']:.4f}; "
          f"largest cell SE {res['largest_cell_se']:.4f}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
