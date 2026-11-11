import numpy as np
import pytest
from scipy import stats

from src.metrics import (bayes_success_binary_gaussian, binned_mi, exact_binned_mi_mixture,
                         exact_continuous_mi_mixture, guessing_entropy, mi_from_counts, quantile_edges,
                         success_rate, welch_t)


def test_welch_t_matches_scipy():
    rng = np.random.default_rng(0)
    a, b = rng.normal(0, 1, 500), rng.normal(0.2, 1.5, 700)
    assert welch_t(a, b) == pytest.approx(-stats.ttest_ind(a, b, equal_var=False).statistic)


def test_mi_zero_for_independent_and_one_bit_for_copy():
    c_ind = np.array([[50, 50], [50, 50]])
    assert mi_from_counts(c_ind, miller_madow=False) == pytest.approx(0.0)
    c_copy = np.array([[100, 0], [0, 100]])
    assert mi_from_counts(c_copy, miller_madow=False) == pytest.approx(1.0)


def test_miller_madow_reduces_null_bias():
    rng = np.random.default_rng(1)
    plug, mm = [], []
    for _ in range(200):
        s = rng.integers(0, 2, 400)
        z = rng.standard_normal(400)
        e = quantile_edges(rng.standard_normal(4000), 16)
        plug.append(binned_mi(s, z, edges=e, miller_madow=False))
        mm.append(binned_mi(s, z, edges=e, miller_madow=True))
    assert abs(np.mean(mm)) < 0.25 * np.mean(plug)


def test_mi_rises_with_amplitude_and_falls_with_noise():
    rng = np.random.default_rng(2)
    s = rng.integers(0, 2, 20000)
    w = rng.standard_normal(20000)
    mi = [binned_mi(s, a * (2 * s - 1) + w) for a in (0.1, 0.5, 1.0)]
    assert mi[0] < mi[1] < mi[2]
    mi_n = [binned_mi(s, 0.5 * (2 * s - 1) + sd * w) for sd in (0.5, 1.0, 2.0)]
    assert mi_n[0] > mi_n[1] > mi_n[2]


def test_exact_binned_mi_matches_monte_carlo():
    rng = np.random.default_rng(3)
    a, sd = 0.7, 1.0
    means = np.array([[-a], [a]])
    sds = np.full((2, 1), sd)
    e = quantile_edges(rng.standard_normal(200000) * np.hypot(a, sd), 16)
    exact = exact_binned_mi_mixture(means, sds, np.array([1.0]), e)
    s = rng.integers(0, 2, 400000)
    z = a * (2 * s - 1) + sd * rng.standard_normal(400000)
    assert binned_mi(s, z, edges=e) == pytest.approx(exact, abs=0.003)


def test_binning_loses_information():
    a = 1.0
    means = np.array([[-a, -0.15 * a], [a, 0.15 * a]])
    sds = np.ones((2, 2))
    w = np.array([0.6, 0.4])
    cont = exact_continuous_mi_mixture(means, sds, w)
    e = np.linspace(-3, 3, 15)
    assert exact_binned_mi_mixture(means, sds, w, e) <= cont + 1e-9
    assert 0 < cont < 1


def test_bayes_success_and_key_ranks():
    assert bayes_success_binary_gaussian(0.0, 1.0) == pytest.approx(0.5)
    assert bayes_success_binary_gaussian(2.0, 1.0) == pytest.approx(stats.norm.cdf(1.0))
    scores = np.array([[0.9, 0.1, 0.0], [0.2, 0.5, 0.3], [0.1, 0.1, 0.8]])
    true = np.array([0, 2, 1])
    assert success_rate(scores, true) == pytest.approx(1 / 3)
    # ranks: 1, 2, 3 (tie in row 3 broken pessimistically)
    assert guessing_entropy(scores, true) == pytest.approx(2.0)
