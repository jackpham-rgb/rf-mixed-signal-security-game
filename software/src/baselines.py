"""Baselines B0 to B4 as solvable policies, and the adaptive observer B5.

A loss matrix M has shape (R, 4): M[r, a] = MI[r, a] + k * overhead[r] - c_a.
An observer type model is a list of (name, action indices, prior weight).
Policies are probability vectors over the R library rows.
"""

from __future__ import annotations

import numpy as np

from .games import solve_bayesian

TIE_TOL = 1e-12

TYPE_MODELS = {
    "1 type": [("adaptive", (0, 1, 2, 3), 1.0)],
    "2 types": [("adaptive", (0, 1, 2, 3), 0.5), ("conducted", (0,), 0.5)],
    "3 types (adaptive 0.5)": [("adaptive", (0, 1, 2, 3), 0.5), ("conducted", (0,), 0.25),
                               ("em-narrowband", (1, 2), 0.25)],
    "3 types (adaptive 0.2)": [("adaptive", (0, 1, 2, 3), 0.2), ("conducted", (0,), 0.4),
                               ("em-narrowband", (1, 2), 0.4)],
}

METHODS = ("game", "best_pure", "B0", "B1", "B2", "B3", "B4", "B4_robust", "best_baseline")


def b5_response(p: np.ndarray, M: np.ndarray, MI: np.ndarray, acts) -> int:
    """Adaptive observer B5: best response to the deployed policy, ties toward more leakage."""
    acts = list(acts)
    vals = p @ M[:, acts]
    tied = np.flatnonzero(vals >= vals.max() - TIE_TOL)
    if len(tied) > 1:
        leak = p @ MI[:, [acts[i] for i in tied]]
        return acts[int(tied[int(np.argmax(leak))])]
    return acts[int(tied[0])]


def score(p: np.ndarray, M: np.ndarray, MI: np.ndarray, types) -> tuple[float, float]:
    """(loss, leakage in bits) of policy p against B5 on matrices (M, MI)."""
    loss = leak = 0.0
    for _, acts, w in types:
        a = b5_response(p, M, MI, acts)
        loss += w * float(p @ M[:, a])
        leak += w * float(p @ MI[:, a])
    return loss, leak


def pure_scores(M: np.ndarray, types) -> np.ndarray:
    """Loss of every pure row against B5 (vectorized; ties do not change loss)."""
    return sum(w * M[:, list(acts)].max(axis=1) for _, acts, w in types)


def l1_worst_uniform(V: np.ndarray, rho: float) -> np.ndarray:
    """Row-wise max of pi . v over the L1 ball of radius rho around the uniform prior.

    Vectorized form of ``games.l1_worst_value``: move up to rho/2 mass from the
    lowest entries (1/n each) onto the highest entry.
    """
    n = V.shape[1]
    srt = np.sort(V, axis=1)
    top = srt[:, -1]
    val = V.mean(axis=1)
    budget = np.full(V.shape[0], rho / 2.0)
    for j in range(n - 1):
        move = np.minimum(budget, 1.0 / n)
        val += move * (top - srt[:, j])
        budget -= move
    return val


def one_hot(r: int, R: int) -> np.ndarray:
    p = np.zeros(R)
    p[r] = 1.0
    return p


def fit_policies(M: np.ndarray, MI: np.ndarray, types, rows, rho: float = 0.5) -> dict:
    """Fit every method on a training matrix. Returns name -> (policy, chosen row or None)."""
    R = M.shape[0]
    out = {}
    sol = solve_bayesian([M[:, list(a)] for _, a, _ in types], np.array([w for *_, w in types]))
    out["game"] = (sol.p, None)
    r = int(np.argmin(pure_scores(M, types)))
    out["best_pure"] = (one_hot(r, R), r)
    for name, r in (("B0", 0), ("B1", 1), ("B2", 2)):
        out[name] = (one_hot(r, R), r)
    # B3: best noise-only row against an observer frozen at its best response to D0.
    frozen = [(n, b5_response(one_hot(0, R), M, MI, a), w) for n, a, w in types]
    noise_rows = np.array([i for i, row in enumerate(rows) if not row.hop and row.power > 0])
    sc = sum(w * M[noise_rows, a] for _, a, w in frozen)
    r = int(noise_rows[np.argmin(sc)])
    out["B3"] = (one_hot(r, R), r)
    # B4: non-strategic optimum under a nominal uniform observer per type.
    sc = sum(w * M[:, list(a)].mean(axis=1) for _, a, w in types)
    r = int(np.argmin(sc))
    out["B4"] = (one_hot(r, R), r)
    # B4_robust: same, worst case over an L1 ball of radius rho around uniform.
    sc = sum(w * l1_worst_uniform(M[:, list(a)], rho) for _, a, w in types)
    r = int(np.argmin(sc))
    out["B4_robust"] = (one_hot(r, R), r)
    # best_baseline: best of B1 to B4, selected on this (training) data against B5.
    cand = ["B1", "B2", "B3", "B4"]
    best = min(cand, key=lambda k: score(out[k][0], M, MI, types)[0])
    out["best_baseline"] = out[best]
    return out
