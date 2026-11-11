import json

import numpy as np
import pytest

from src.band_channel import (coarse_library, fine_library, hop_out_prob, inject_var, simulate_dataset)
from src.baselines import TYPE_MODELS, b5_response, fit_policies, one_hot, score
from src.run_experiment import run
from src.value_of_game import Config, analyze_dataset, analyze_scaffold


def test_library_shape_and_names():
    rows = coarse_library()
    assert [r.name for r in rows[:4]] == ["D0-no-defense", "D1-fixed-dummy", "D2-random-frequency",
                                          "D3-shaped-stochastic"]
    assert len({r.name for r in rows}) == len(rows) == 213
    assert any(r.name == "F-x0103-P0.75" for r in rows)


def test_separability_preserves_total_effect():
    for s in (0.0, 0.3, 1.0):
        assert hop_out_prob(s).sum() == pytest.approx(1.5)
        assert inject_var((0, 0.25, 0, 0.75), 1.5, s).sum() == pytest.approx(6.0)
    assert np.allclose(inject_var((0, 0, 0, 1), 1.0, 0.0), 1.0)


def test_fine_library_counts():
    assert len(fine_library(12, 41, s=1.0)[0]) == 36402
    assert len(fine_library(12, 41, s=0.0)[0]) == 82


def test_b5_breaks_ties_toward_leakage():
    M = np.array([[0.5, 0.5]])
    MI = np.array([[0.1, 0.3]])
    assert b5_response(np.array([1.0]), M, MI, (0, 1)) == 1


def test_simulation_is_seed_reproducible():
    rows = coarse_library()[:6]
    a = simulate_dataset(0.5, 1.0, np.random.SeedSequence(5), rows, n_sessions=4, n_traces=200)
    b = simulate_dataset(0.5, 1.0, np.random.SeedSequence(5), rows, n_sessions=4, n_traces=200)
    assert np.array_equal(a.mi_matrix(), b.mi_matrix())


def test_mc_mi_converges_to_exact_model_with_sessions():
    # MI is convex in the channel, so pooling a finite number of sessions G
    # biases the estimate upward (about 1/G). With many sessions it must vanish.
    rows = coarse_library()[:8]
    ds = simulate_dataset(1.0, 0.5, np.random.SeedSequence(6), rows, n_sessions=2048, n_traces=150)
    assert np.abs(ds.mi_matrix() - ds.exact_mi_matrix("binned")).max() < 0.01


def test_in_sample_game_never_loses_to_pure():
    rng = np.random.default_rng(7)
    rows = coarse_library()
    MI = rng.random((len(rows), 4)) * 0.3
    M = MI + 0.1 * np.array([r.energy for r in rows])[:, None]
    for name, types in TYPE_MODELS.items():
        fits = fit_policies(M, MI, types, rows)
        assert score(fits["game"][0], M, MI, types)[0] <= score(fits["best_pure"][0], M, MI, types)[0] + 1e-9


def test_crossfitting_removes_in_sample_optimism_under_null():
    # Every row has the same true leakage, so the true gap is 0. In-sample the
    # game exploits noise (gap >= 0); cross-fitting must not show a positive gap.
    out = analyze_dataset(0.25, 0.0, np.random.SeedSequence(8), [Config(0.0, "1 type")], n_boot=20,
                          n_sessions=32, n_traces=300, fine=False)
    r = out["results"][0]
    assert r["gaps_in_sample"]["gap_pure"] >= -1e-12
    assert r["gaps"]["gap_pure"]["est"] <= r["gaps_in_sample"]["gap_pure"] + 1e-12
    assert r["gaps"]["gap_pure"]["ci"][0] <= 0.0


def test_scaffold_equilibrium_is_pure():
    r = analyze_scaffold(np.random.SeedSequence(9), n_boot=10, n_sessions=32, n_traces=500)
    assert len(r["game_policy"]) == 1
    assert r["gaps"]["gap_pure"]["est"] == pytest.approx(0.0, abs=1e-9)


def test_run_experiment_writes_wellformed_json():
    res = run(seed=1, n_runs=5, n_traces=1000, lambda_e=0.3, lambda_l=0.2)
    json.dumps(res)
    assert res["equilibrium"]["primal_dual_gap"] < 1e-8
    assert res["seed"] == 1 and "numpy" in res["environment"]
    assert res["in_sample_gap_pure"] >= -1e-12
