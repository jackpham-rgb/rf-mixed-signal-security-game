import numpy as np
import pytest

from src.games import (best_pure, l1_worst_prior, l1_worst_value, solve_bayesian, solve_robust_prior,
                       solve_zero_sum)
from src.baselines import l1_worst_uniform


def test_matching_pennies_value_and_gap():
    M = np.array([[1.0, 0.0], [0.0, 1.0]])
    sol = solve_zero_sum(M)
    assert sol.value == pytest.approx(0.5)
    assert sol.p == pytest.approx([0.5, 0.5])
    assert sol.q == pytest.approx([0.5, 0.5])
    assert sol.gap < 1e-9
    _, v_pure = best_pure(M)
    assert v_pure - sol.value == pytest.approx(0.5)


def test_saddle_point_gives_pure_policy_and_zero_gap():
    M = np.array([[0.3, 0.4], [0.5, 0.6]])
    sol = solve_zero_sum(M)
    d, v = best_pure(M)
    assert d == 0
    assert sol.value == pytest.approx(v)
    assert sol.p == pytest.approx([1.0, 0.0])


def test_hand_solvable_2x2():
    # mixed solution: p = (c - d)/(a - b - c + d) style; here value 2.5 at p = (0.5, 0.5)
    M = np.array([[4.0, 1.0], [1.0, 4.0]])
    sol = solve_zero_sum(M)
    assert sol.value == pytest.approx(2.5)
    assert sol.dual_value == pytest.approx(2.5)


def test_primal_dual_agree_on_random_matrices():
    rng = np.random.default_rng(0)
    for _ in range(20):
        M = rng.random((5, 4))
        sol = solve_zero_sum(M)
        assert sol.gap < 1e-8
        assert np.all(sol.p >= 0) and sol.p.sum() == pytest.approx(1.0)
        assert (M.T @ sol.p).max() == pytest.approx(sol.value, abs=1e-8)


def test_bayesian_single_type_equals_zero_sum():
    rng = np.random.default_rng(1)
    M = rng.random((6, 4))
    zs = solve_zero_sum(M)
    bs = solve_bayesian([M], np.array([1.0]))
    assert bs.value == pytest.approx(zs.value, abs=1e-8)
    assert bs.q_type[0] @ np.ones(4) == pytest.approx(1.0)
    # the dual observer mixture guarantees the value
    assert (M @ bs.q_type[0]).min() == pytest.approx(zs.value, abs=1e-6)


def test_bayesian_types_weight_their_values():
    rng = np.random.default_rng(2)
    M = rng.random((5, 4))
    types = [M[:, [0, 1, 2, 3]], M[:, [0]]]
    bs = solve_bayesian(types, np.array([0.3, 0.7]))
    v = [(t.T @ bs.p).max() for t in types]
    assert bs.value == pytest.approx(0.3 * v[0] + 0.7 * v[1], abs=1e-8)


def test_l1_worst_prior_moves_half_rho():
    v = np.array([1.0, 2.0, 3.0])
    nom = np.full(3, 1 / 3)
    pi = l1_worst_prior(v, nom, 0.4)
    assert np.abs(pi - nom).sum() == pytest.approx(0.4)
    assert pi.sum() == pytest.approx(1.0)
    assert l1_worst_value(v, nom, 0.0) == pytest.approx(2.0)
    V = np.array([[1.0, 2.0, 3.0], [3.0, 3.0, 0.0]])
    for rho in (0.0, 0.3, 0.5, 2.0):
        expected = [l1_worst_value(r, nom, rho) for r in V]
        assert l1_worst_uniform(V, rho) == pytest.approx(expected)


def test_robust_prior_value_monotone_in_rho():
    rng = np.random.default_rng(3)
    M = rng.random((5, 4))
    types = [M[:, [0, 1, 2, 3]], M[:, [0]], M[:, [1, 2]]]
    nom = np.array([0.5, 0.25, 0.25])
    vals = [solve_robust_prior(types, nom, rho).value for rho in (0.0, 0.2, 0.5, 1.0)]
    assert vals[0] == pytest.approx(solve_bayesian(types, nom).value, abs=1e-7)
    assert all(b >= a - 1e-9 for a, b in zip(vals, vals[1:]))
