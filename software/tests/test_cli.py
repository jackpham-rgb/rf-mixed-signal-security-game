import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from src.band_channel import coarse_library, exact_cell_mi, hop_out_prob, inject_var
from src.baselines import METHODS
from src.cli import main
from src.dataset import (
    AscamError,
    GenerateSpec,
    open_dataset,
    split_sessions,
    synthesize,
    validate,
)
from src.evaluate import EvalSettings, extract_cells, load_settings
from src.metrics import mi_from_counts

SOFTWARE = Path(__file__).resolve().parents[1]
SMALL = ["--traces", "2400", "--sessions", "10", "--seed", "7"]
FULL = ["--library", "full", "--traces", str(2 * 7 * 213), "--sessions", "7", "--seed", "9"]
NAMED = ["D0-no-defense", "D1-fixed-dummy", "D2-random-frequency", "D3-shaped-stochastic"]


def generate(out, *extra):
    assert main(["generate", *SMALL, "--out", str(out), *extra]) == 0


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_generate_evaluate_report_pipeline_and_module_entry_point(tmp_path):
    data, results, figures = tmp_path / "data", tmp_path / "results.json", tmp_path / "figures"
    generate(data)
    run = subprocess.run([sys.executable, "-m", "src.cli", "evaluate", "--data", str(data),
                          "--bootstrap", "40", "--seed", "7", "--out", str(results)],
                         cwd=SOFTWARE, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    assert "Cross-fitted value-of-game check skipped" in run.stdout
    assert main(["report", "--results", str(results), "--out", str(figures)]) == 0
    assert {p.name for p in data.iterdir()} == {"manifest.json", "traces.npz", "features.npz"}
    assert {p.name for p in figures.iterdir()} == {"payoff_equilibrium.png",
                                                   "equilibrium_uncertainty.png"}
    for path in figures.iterdir():
        assert path.stat().st_size > 10_000

    parsed = load(results)
    payoff, eq = parsed["payoff"], parsed["equilibrium"]
    assert parsed["results_schema_version"] == "0.1.0"
    assert payoff["rows"] == NAMED and len(payoff["columns"]) == 4
    for block in (payoff, payoff["leakage_mi_bits"]):
        for key in ("matrix", "ci_low", "ci_high", "se"):
            assert np.asarray(block[key]).shape == (4, 4)
        assert np.all(np.asarray(block["ci_low"]) <= np.asarray(block["ci_high"]))
    # Positive control: the undefended device leaks detectably at A = 0.5.
    assert np.asarray(payoff["leakage_mi_bits"]["ci_low"])[0].max() > 0.05
    assert eq["value_ci"][0] <= eq["value_ci"][1]
    assert len(eq["value_replicates"]) == 40
    assert sum(r["p"] for r in eq["defender_policy"]) == pytest.approx(1.0)
    assert all(0.0 <= r["support_stability"] <= 1.0 for r in eq["defender_policy"])
    assert abs(eq["duality_gap"]) < 1e-8
    assert eq["solver"]["status"] == "optimal"
    assert (parsed["N"], parsed["G"]) == (6 * 4 * 60, 6)
    assert parsed["test_split"] == {"rows_present": 2 * 4 * 60, "rows_used": 0, "reads": []}
    assert parsed["provenance"]["seed"] == 7 and parsed["data"]["master_seed"] == 7
    assert {"ascam", "python", "numpy", "scipy"} <= parsed["provenance"]["versions"].keys()
    assert parsed["data"]["dataset_id"].startswith("sha256:")
    assert parsed["caveat"].startswith("synthetic: parametric")
    # The named library has no noise-only row, so baseline B3 and the check cannot run.
    assert "B3" in parsed["value_of_game"]["skipped"]


def test_full_library_runs_the_cross_fitted_check_and_draws_its_figure(tmp_path):
    data = tmp_path / "full"
    assert main(["generate", *FULL, "--out", str(data)]) == 0
    names = [d["name"] for d in load(data / "manifest.json")["defense_actions"]]
    assert len(names) == 213 and names[:4] == NAMED
    assert main(["evaluate", "--data", str(data), "--bins", "4", "--bootstrap", "10",
                 "--out", str(tmp_path / "full.json")]) == 0
    result = load(tmp_path / "full.json")
    assert np.asarray(result["payoff"]["matrix"]).shape == (213, 4)
    assert abs(result["equilibrium"]["duality_gap"]) < 1e-8
    vog = result["value_of_game"]
    assert set(METHODS) <= vog["methods"].keys()
    assert {"gap_pure", "gap_robust", "gap_baselines"} <= vog["gaps"].keys()
    assert (vog["k"], vog["types"], vog["A"], vog["s"]) == (1.0, "1 type", 0.5, 1.0)
    assert vog["game_strictly_helps"] in (True, False)
    figures = tmp_path / "figures"
    assert main(["report", "--results", str(tmp_path / "full.json"), "--out", str(figures)]) == 0
    assert {p.name for p in figures.iterdir()} == {
        "payoff_equilibrium.png", "equilibrium_uncertainty.png", "value_of_game.png"}
    # Prices off the k (0.30 E + 0.20 T) line of src/value_of_game.py skip the check.
    assert main(["evaluate", "--data", str(data), "--bins", "4", "--bootstrap", "2",
                 "--lambda-energy", "0.1", "--out", str(tmp_path / "off.json")]) == 0
    assert "not on that line" in load(tmp_path / "off.json")["value_of_game"]["skipped"]


def test_mi_estimates_recover_the_exact_band_channel():
    # Ground truth: with many sessions the estimates must match the quadrature
    # MI of src/band_channel.py for the same frozen bins, cell by cell.
    cells = extract_cells(synthesize(GenerateSpec(traces=200_000, sessions=1000, seed=11)),
                          EvalSettings())
    estimate = mi_from_counts(cells.counts.sum(axis=0))
    q = hop_out_prob(1.0)
    exact = np.array([[exact_cell_mi(0.5, b, q[b] if row.hop else 0.0,
                                     inject_var(row.alloc, row.power, 1.0)[b],
                                     edges=cells.edges[d, b]) for b in range(4)]
                      for d, row in enumerate(coarse_library()[:4])])
    assert exact[3].max() < exact[0].min()
    assert np.abs(estimate - exact).max() < 0.015


def test_generate_refuses_to_overwrite_and_rejects_too_few_traces(tmp_path, capsys):
    out = tmp_path / "data"
    generate(out)
    assert main(["generate", *SMALL, "--out", str(out)]) == 2
    assert "not empty" in capsys.readouterr().err
    assert main(["generate", "--traces", "10", "--sessions", "10",
                 "--out", str(tmp_path / "small")]) == 2
    assert "traces per session per defense" in capsys.readouterr().err
    assert not (tmp_path / "small").exists()


def test_split_sessions_uses_largest_remainder_and_minimum_sizes():
    assert split_sessions(30, (0.6, 0.2, 0.2)) == (18, 6, 6)
    assert split_sessions(12, (0.6, 0.2, 0.2)) == (7, 3, 2)
    assert split_sessions(8, (0.75, 0.25, 0.0)) == (6, 2, 0)
    with pytest.raises(AscamError, match="at least 4 train"):
        split_sessions(5, (0.6, 0.2, 0.2))


def test_open_dataset_checks_columns_groups_and_checksums(tmp_path):
    out = tmp_path / "data"
    generate(out)
    dataset = open_dataset(out)
    assert dataset.validation["group_disjointness_checked"] == ["key_id", "session_id"]
    assert dataset.validation["single_level_groups_exempt"] == ["netlist_id", "pvt_corner"]
    assert dataset.traces.shape == (2400, 4) and dataset.traces.dtype == np.float32
    assert set(np.unique(dataset.features["split"])) == {"train", "calib", "test"}
    tampered = bytearray((out / "traces.npz").read_bytes())
    tampered[-100] ^= 0xFF
    (out / "traces.npz").write_bytes(bytes(tampered))
    with pytest.raises(AscamError, match="checksum mismatch"):
        open_dataset(out)


def test_validation_rejects_a_session_shared_by_two_splits():
    dataset = synthesize(GenerateSpec(traces=2400, sessions=10, seed=3))
    sessions = dataset.features["session_id"]
    dataset.features["session_id"] = np.where(sessions == "test-000", "train-000", sessions)
    with pytest.raises(AscamError, match="split leak: session_id"):
        validate(dataset)


def test_same_seed_gives_identical_dataset_bytes_and_results_json(tmp_path):
    generate(tmp_path / "a")
    generate(tmp_path / "b")
    for name in ("manifest.json", "traces.npz", "features.npz"):
        assert (tmp_path / "a" / name).read_bytes() == (tmp_path / "b" / name).read_bytes()
    for run in ("r1", "r2"):
        assert main(["evaluate", "--data", str(tmp_path / "a"), "--bootstrap", "30",
                     "--out", str(tmp_path / f"{run}.json")]) == 0
    assert (tmp_path / "r1.json").read_bytes() == (tmp_path / "r2.json").read_bytes()


def test_evaluate_without_data_matches_the_generated_dataset(tmp_path):
    data = tmp_path / "data"
    assert main(["generate", "--seed", "5", "--out", str(data)]) == 0
    assert main(["evaluate", "--data", str(data), "--seed", "5", "--bootstrap", "20",
                 "--out", str(tmp_path / "file.json")]) == 0
    assert main(["evaluate", "--seed", "5", "--bootstrap", "20",
                 "--out", str(tmp_path / "memory.json")]) == 0
    from_file, in_memory = load(tmp_path / "file.json"), load(tmp_path / "memory.json")
    assert in_memory["data"]["origin"].startswith("synthesized in memory")
    for result in (from_file, in_memory):
        result["data"].pop("origin")
        result["data"]["validation"].pop("checksums")
    assert from_file == in_memory


def test_zero_leakage_is_not_detected_and_no_defense_wins(tmp_path):
    data = tmp_path / "null"
    assert main(["generate", "--leakage-amplitude", "0", "--traces", "9600", "--sessions", "12",
                 "--seed", "21", "--out", str(data)]) == 0
    assert main(["evaluate", "--data", str(data), "--bootstrap", "60",
                 "--out", str(tmp_path / "null.json")]) == 0
    result = load(tmp_path / "null.json")
    assert np.abs(result["payoff"]["leakage_mi_bits"]["matrix"]).max() < 0.02
    policy = {r["action"]: r for r in result["equilibrium"]["defender_policy"]}
    assert policy["D0-no-defense"]["p"] == pytest.approx(1.0)
    assert result["equilibrium"]["stable_support"] == ["D0-no-defense"]


def test_bayesian_type_model_gives_one_observer_mixture_per_type(tmp_path):
    data = tmp_path / "data"
    generate(data)
    assert main(["evaluate", "--data", str(data), "--type-model", "2", "--bootstrap", "20",
                 "--out", str(tmp_path / "types.json")]) == 0
    eq = load(tmp_path / "types.json")["equilibrium"]
    assert eq["type_model"]["name"] == "3 types (adaptive 0.5)"
    assert [o["type"] for o in eq["observer_policies"]] == ["adaptive", "conducted",
                                                            "em-narrowband"]
    assert eq["game"] == "bayesian, zero-sum per type"
    assert abs(eq["duality_gap"]) < 1e-8


def test_json_config_is_applied_and_unknown_or_yaml_configs_are_rejected(tmp_path):
    assert load_settings(SOFTWARE / "configs" / "d0-d3_a0-a3.json") == EvalSettings()
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"bins": 8, "lambda_energy": 0.1}), encoding="utf-8")
    settings = load_settings(config, {"bins": 10, "seed": None})
    assert (settings.bins, settings.lambda_energy, settings.seed) == (10, 0.1, 126)
    config.write_text(json.dumps({"bootstraps": 5}), encoding="utf-8")
    with pytest.raises(AscamError, match="unknown config keys"):
        load_settings(config)
    with pytest.raises(AscamError, match="YAML configs are planned"):
        load_settings(tmp_path / "config.yaml")


def test_report_rejects_a_json_that_is_not_an_evaluate_result(tmp_path, capsys):
    sweep = tmp_path / "sweep.json"
    sweep.write_text(json.dumps({"experiment": "value_of_game_sweep"}), encoding="utf-8")
    assert main(["report", "--results", str(sweep), "--out", str(tmp_path / "figures")]) == 2
    assert "not an ascam evaluate results JSON" in capsys.readouterr().err
    assert not (tmp_path / "figures").exists()
