import numpy as np
import pytest

from src.band_channel import coarse_library
from src.extensions import (FUSED, ExtConfig, analyze_extensions, gs_best_pure, gs_score, simulate_combined,
                            solve_gs_stackelberg)
from src.games import solve_zero_sum


def test_commitment_beats_nash_in_textbook_game():
    # Leader payoff [[1, 3], [0, 2]] (row 0 dominates, so Nash gives 1).
    # Follower payoff [[1, 0], [0, 1]]. Committing to p(row 1) just above 1/2
    # makes the follower play column 1, so the leader gets about 2.5, more than
    # any pure commitment (2) and the simultaneous-move Nash value (1).
    leader = np.array([[1.0, 3.0], [0.0, 2.0]])
    L, U = -leader, np.array([[1.0, 0.0], [0.0, 1.0]])
    types = [("t", (0, 1), 1.0)]
    p, profile = solve_gs_stackelberg(L, U, types, margin=1e-6)
    assert profile == (1,)
    assert -gs_score(p, L, U, L * 0, types)[0] == pytest.approx(2.5, abs=1e-4)
    # Best pure commitment: row 1, follower answers column 1, leader gets 2.
    r, v = gs_best_pure(L, U, np.zeros_like(L), types)
    assert (r, -v) == (1, pytest.approx(2.0))


def test_zero_sum_case_matches_minimax():
    rng = np.random.default_rng(0)
    M = rng.random((5, 3))
    types = [("t", (0, 1, 2), 1.0)]
    p, _ = solve_gs_stackelberg(M, M, types, margin=0.0)
    assert gs_score(p, M, M, M, types)[0] == pytest.approx(solve_zero_sum(M).value, abs=1e-7)


def test_fused_observer_leaks_more_than_any_single_band():
    rows = coarse_library()[:6]
    ds = simulate_combined(1.0, 1.0, np.random.SeedSequence(4), rows, n_sessions=16, n_traces=1000)
    mi = ds.mi_matrix()
    assert np.all(mi[:, FUSED] > mi[:, :FUSED].max(axis=1))


def test_free_fused_observer_erases_value_of_mixing():
    cfgs = [ExtConfig(1.0, "1 type", 0.0)]
    out = analyze_extensions(1.0, 1.0, np.random.SeedSequence(5), cfgs, n_boot=3, n_sessions=16, n_traces=300)
    r = out["results"][0]
    assert r["losses"]["fused_share"] == pytest.approx(1.0)
    assert r["gaps_in_sample"]["gap_pure"] == pytest.approx(0.0, abs=1e-9)
    assert len(r["zs_policy"]) == 1
