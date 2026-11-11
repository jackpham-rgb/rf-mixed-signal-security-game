"""Finite game solvers: zero-sum minimax, Bayesian epigraph LP, L1 prior-robust LP.

Sign convention (frozen): entries are defender LOSS. The defender minimizes,
the observer maximizes. All LPs use SciPy's HiGHS backend.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import linprog

TOL = 1e-9


@dataclass
class ZeroSumSolution:
    p: np.ndarray          # defender mixed strategy over rows
    q: np.ndarray          # observer mixed strategy over columns
    value: float           # primal value min_p max_a (M^T p)_a
    dual_value: float      # max_q min_d (M q)_d
    gap: float             # |primal - dual|
    status: str


def solve_zero_sum(M: np.ndarray) -> ZeroSumSolution:
    """Solve min_p max_q p^T M q by the primal LP and the separate dual LP."""
    M = np.asarray(M, dtype=float)
    D, A = M.shape
    # primal: variables (p, v); min v s.t. M^T p - v <= 0, sum p = 1
    c = np.r_[np.zeros(D), 1.0]
    A_ub = np.c_[M.T, -np.ones(A)]
    A_eq = np.r_[np.ones(D), 0.0][None, :]
    bounds = [(0, None)] * D + [(None, None)]
    rp = linprog(c, A_ub=A_ub, b_ub=np.zeros(A), A_eq=A_eq, b_eq=[1.0], bounds=bounds, method="highs")
    # dual: variables (q, u); max u s.t. u - M q <= 0, sum q = 1
    c2 = np.r_[np.zeros(A), -1.0]
    A_ub2 = np.c_[-M, np.ones(D)]
    A_eq2 = np.r_[np.ones(A), 0.0][None, :]
    bounds2 = [(0, None)] * A + [(None, None)]
    rd = linprog(c2, A_ub=A_ub2, b_ub=np.zeros(D), A_eq=A_eq2, b_eq=[1.0], bounds=bounds2, method="highs")
    if rp.status != 0 or rd.status != 0:
        raise RuntimeError(f"LP failed: primal {rp.message}; dual {rd.message}")
    p = _clean_simplex(rp.x[:D])
    q = _clean_simplex(rd.x[:A])
    v, u = float(rp.x[-1]), float(rd.x[-1])
    return ZeroSumSolution(p, q, v, u, abs(v - u), "optimal")


def _clean_simplex(x: np.ndarray) -> np.ndarray:
    x = np.where(np.asarray(x) < TOL, 0.0, x)
    return x / x.sum()


def best_pure(M: np.ndarray) -> tuple[int, float]:
    """Best single row against a best-responding column player."""
    worst = np.asarray(M).max(axis=1)
    d = int(np.argmin(worst))
    return d, float(worst[d])


# ---------------------------------------------------------------------------
# Bayesian (per-type zero-sum) commitment: epigraph LP
# ---------------------------------------------------------------------------

@dataclass
class BayesianSolution:
    p: np.ndarray
    value: float
    v_type: np.ndarray                       # per-type epigraph values
    q_type: list = field(default_factory=list)  # per-type observer mixtures (from duals)
    status: str = "optimal"


def solve_bayesian(M_types: list[np.ndarray], prior: np.ndarray) -> BayesianSolution:
    """min_p sum_t pi_t v_t  s.t.  (M_t)^T p <= v_t 1 for every type t.

    ``M_types[t]`` has shape (D, A_t): the loss matrix restricted to the
    actions available to type t. The per-type observer mixtures are read from
    the inequality duals and normalized.
    """
    prior = np.asarray(prior, dtype=float)
    T = len(M_types)
    D = M_types[0].shape[0]
    rows, sizes = [], []
    for t, Mt in enumerate(M_types):
        Mt = np.asarray(Mt, dtype=float)
        block = np.zeros((Mt.shape[1], D + T))
        block[:, :D] = Mt.T
        block[:, D + t] = -1.0
        rows.append(block)
        sizes.append(Mt.shape[1])
    A_ub = np.vstack(rows)
    c = np.r_[np.zeros(D), prior]
    A_eq = np.r_[np.ones(D), np.zeros(T)][None, :]
    bounds = [(0, None)] * D + [(None, None)] * T
    r = linprog(c, A_ub=A_ub, b_ub=np.zeros(A_ub.shape[0]), A_eq=A_eq, b_eq=[1.0],
                bounds=bounds, method="highs")
    if r.status != 0:
        raise RuntimeError(f"Bayesian LP failed: {r.message}")
    p = _clean_simplex(r.x[:D])
    duals = -np.asarray(r.ineqlin.marginals)
    q_type, start = [], 0
    for t, k in enumerate(sizes):
        d = np.maximum(duals[start:start + k], 0.0)
        q_type.append(d / d.sum() if d.sum() > 0 else np.full(k, 1.0 / k))
        start += k
    return BayesianSolution(p, float(r.fun), r.x[D:].copy(), q_type)


# ---------------------------------------------------------------------------
# L1-ball robust prior
# ---------------------------------------------------------------------------

def l1_worst_prior(values: np.ndarray, nominal: np.ndarray, rho: float) -> np.ndarray:
    """argmax_{pi in simplex, ||pi - nominal||_1 <= rho} pi . values.

    Greedy: move up to rho/2 mass from the lowest-value entries to the
    highest-value entry.
    """
    values = np.asarray(values, dtype=float)
    pi = np.asarray(nominal, dtype=float).copy()
    budget = rho / 2.0
    top = int(np.argmax(values))
    for i in np.argsort(values):
        if budget <= 0:
            break
        if i == top:
            continue
        move = min(pi[i], budget)
        pi[i] -= move
        pi[top] += move
        budget -= move
    return pi


def l1_worst_value(values: np.ndarray, nominal: np.ndarray, rho: float) -> float:
    return float(l1_worst_prior(values, nominal, rho) @ np.asarray(values, dtype=float))


def solve_robust_prior(M_types: list[np.ndarray], nominal: np.ndarray, rho: float,
                       max_iter: int = 100, tol: float = 1e-9) -> BayesianSolution:
    """min_p max_{pi in U_rho} sum_t pi_t v_t(p), by constraint generation.

    v_t(p) = max_a (M_t^T p)_a. The inner maximum over the L1 ball is a
    maximum over finitely many priors, so we add worst-case priors until the
    oracle cannot find a violated one.
    """
    nominal = np.asarray(nominal, dtype=float)
    T = len(M_types)
    D = M_types[0].shape[0]
    priors = [nominal.copy()]
    for _ in range(max_iter):
        # variables (p, v_1..v_T, z): min z s.t. M_t^T p <= v_t, pi_k . v <= z
        rows = []
        for t, Mt in enumerate(M_types):
            block = np.zeros((Mt.shape[1], D + T + 1))
            block[:, :D] = np.asarray(Mt).T
            block[:, D + t] = -1.0
            rows.append(block)
        for pk in priors:
            r_ = np.zeros(D + T + 1)
            r_[D:D + T] = pk
            r_[-1] = -1.0
            rows.append(r_[None, :])
        A_ub = np.vstack(rows)
        c = np.r_[np.zeros(D + T), 1.0]
        A_eq = np.r_[np.ones(D), np.zeros(T + 1)][None, :]
        bounds = [(0, None)] * D + [(None, None)] * (T + 1)
        r = linprog(c, A_ub=A_ub, b_ub=np.zeros(A_ub.shape[0]), A_eq=A_eq, b_eq=[1.0],
                    bounds=bounds, method="highs")
        if r.status != 0:
            raise RuntimeError(f"robust LP failed: {r.message}")
        p = _clean_simplex(r.x[:D])
        v = np.array([float((np.asarray(Mt).T @ p).max()) for Mt in M_types])
        worst = l1_worst_prior(v, nominal, rho)
        if worst @ v <= r.x[-1] + tol:
            return BayesianSolution(p, float(worst @ v), v, [])
        priors.append(worst)
    raise RuntimeError("constraint generation did not converge")
