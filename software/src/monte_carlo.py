"""Reproducible Monte Carlo payoff matrices for the scalar scaffold."""

from __future__ import annotations

import numpy as np

from .channel import DEFENDER_ACTIONS, OBSERVER_ACTIONS, overhead, simulate_traces
from .metrics import binned_mi, quantile_edges


def payoff_matrix(seed: int, n_runs: int = 30, n_traces: int = 4000, n_bins: int = 16,
                  amplitude: float = 1.0, lambda_e: float = 0.3, lambda_l: float = 0.2,
                  lambda_f: float = 0.0) -> dict:
    """Estimate M[d, a] = MI + priced overhead - observer cost.

    Each cell averages ``n_runs`` independent runs. Bin edges for each cell are
    frozen from a separate calibration run, so the evaluation runs are held out.
    Returns the mean matrix, per-cell standard errors, and the MI part alone.
    """
    D, A = len(DEFENDER_ACTIONS), len(OBSERVER_ACTIONS)
    mi = np.zeros((D, A, n_runs))
    for i, d in enumerate(DEFENDER_ACTIONS):
        for j in range(A):
            cal_ss, *run_ss = np.random.SeedSequence(seed, spawn_key=(i, j)).spawn(n_runs + 1)
            _, zc = simulate_traces(np.random.default_rng(cal_ss), d, j, n_traces, amplitude)
            edges = quantile_edges(zc, n_bins)
            for r, ss in enumerate(run_ss):
                s, z = simulate_traces(np.random.default_rng(ss), d, j, n_traces, amplitude)
                mi[i, j, r] = binned_mi(s, z, edges=edges)
    oh = np.array([overhead(d, lambda_e, lambda_l, lambda_f) for d in DEFENDER_ACTIONS])
    cost = np.array([a.cost for a in OBSERVER_ACTIONS])
    mi_mean = mi.mean(axis=2)
    M = mi_mean + oh[:, None] - cost[None, :]
    se = mi.std(axis=2, ddof=1) / np.sqrt(n_runs)
    return {"M": M, "se": se, "mi": mi_mean, "overhead": oh, "observer_cost": cost}
