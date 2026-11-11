"""Payoff estimation, game solution, and uncertainty for ``ascam evaluate``.

From the train split of a dataset this module estimates the defender loss

    L[d, a] = I(S; Z_{d,a}) + lambda_E E_d + lambda_L T_d + lambda_F F_d - c(a)

with binned plug-in MI (``metrics.mi_from_counts``, Miller-Madow corrected,
equal-mass bin edges frozen on the calib split), solves the defender/observer
game with ``games.solve_bayesian``, and attaches session-bootstrap uncertainty:
per-cell percentile intervals, an interval for the equilibrium value, and the
support stability of every defense. A second, cross-fitted bootstrap
(``value_of_game.analyze``) scores the game against the best single defense
and baselines B0 to B4 on held-out sessions. The test split is never used.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, fields
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from . import __version__
from .band_channel import N_BANDS, OBS_COST, Row
from .baselines import TYPE_MODELS
from .dataset import OBSERVER_NAMES, AscamError, Dataset
from .games import solve_bayesian
from .metrics import bin_index, mi_from_counts, quantile_edges
from .provenance import environment_record
from .value_of_game import LAMBDA_E, LAMBDA_L, SUPPORT_TOL, Config, _ci, analyze, loss_matrix

RESULTS_SCHEMA_VERSION = "0.1.0"
EVALUATE_SEED_ROLE = 2  # spawn_key role, distinct from dataset generation
LEVEL = 0.95
STABLE_SUPPORT = 0.95
TYPE_MODEL_NAMES = tuple(TYPE_MODELS)
LOSS_DEFINITION = ("L[d, a] = I(S; Z_da) + lambda_E E_d + lambda_L T_d + lambda_F F_d "
                   "- c(a); the defender minimizes and the observer maximizes")


@dataclass(frozen=True)
class EvalSettings:
    seed: int = 126
    bootstrap: int = 1000
    bins: int = 16
    lambda_energy: float = 0.30
    lambda_latency: float = 0.20
    lambda_false_alarm: float = 0.0
    type_model: int = 0
    robust_rho: float = 0.5
    label: str = "label_hw"

    def __post_init__(self) -> None:
        problems = []
        if self.seed < 0:
            problems.append("seed must be nonnegative")
        if self.bootstrap < 2:
            problems.append("bootstrap needs at least 2 replicates")
        if self.bins < 2:
            problems.append("bins must be at least 2")
        if min(self.lambda_energy, self.lambda_latency, self.lambda_false_alarm) < 0:
            problems.append("prices must be nonnegative")
        if not 0 <= self.type_model < len(TYPE_MODEL_NAMES):
            problems.append(f"type_model must be 0 to {len(TYPE_MODEL_NAMES) - 1}")
        if not 0.0 <= self.robust_rho <= 2.0:
            problems.append("robust_rho must lie in [0, 2]")
        if problems:
            raise AscamError("; ".join(problems))


FIELD_TYPES = {f.name: type(f.default) for f in fields(EvalSettings)}


def load_settings(config: Path | None = None, overrides: dict | None = None) -> EvalSettings:
    """Defaults, then a JSON config file, then non-None command-line overrides."""
    values = {}
    if config is not None:
        if config.suffix.lower() in (".yaml", ".yml"):
            raise AscamError("YAML configs are planned; use a JSON config")
        try:
            data = json.loads(Path(config).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise AscamError(f"cannot read config {config}: {error}") from error
        if not isinstance(data, dict):
            raise AscamError("config must be a JSON object")
        unknown = sorted(set(data) - FIELD_TYPES.keys())
        if unknown:
            raise AscamError(f"unknown config keys {unknown}; known keys: {sorted(FIELD_TYPES)}")
        values.update(data)
    values.update({k: v for k, v in (overrides or {}).items() if v is not None})
    typed = {}
    for key, value in values.items():
        kind = FIELD_TYPES[key]
        if kind is int and (isinstance(value, bool)
                            or isinstance(value, float) and not value.is_integer()):
            raise AscamError(f"config key {key} must be an integer")
        try:
            typed[key] = kind(value)
        except (TypeError, ValueError) as error:
            raise AscamError(f"config key {key}: {error}") from error
    return EvalSettings(**typed)


@dataclass
class Cells:
    counts: NDArray        # (G, D, A, C, K) train histograms per session
    edges: NDArray         # (D, A, K - 1) bin edges frozen on the calib split
    traces: NDArray        # (G, D) train traces per session and defense
    energy_sum: NDArray    # (G, D)
    latency_sum: NDArray   # (G, D)
    sessions: list[str]
    defenses: list[dict]   # manifest defense_actions, in row order
    observers: list[str]
    classes: list[int]
    calib_traces: int
    calib_sessions: int
    test_rows: int

    @property
    def names(self) -> list[str]:
        return [d["name"] for d in self.defenses]


def extract_cells(dataset: Dataset, settings: EvalSettings) -> Cells:
    """Freeze bin edges on calib and histogram the train split per session.

    Test-split rows are counted but their traces are never indexed.
    """
    m, f = dataset.manifest, dataset.features
    split = f["split"]
    train, calib = split == "train", split == "calib"
    defenses = list(m["defense_actions"])
    names = [d["name"] for d in defenses]
    observers = list(m["observer_actions"])
    if observers != list(OBSERVER_NAMES):
        raise AscamError("observer costs and type models are defined for the band4 actions "
                         f"{list(OBSERVER_NAMES)} only; other observer sets are planned")
    overhead = m.get("overhead_columns", {})
    columns = (settings.label, overhead.get("energy"), overhead.get("latency"))
    for column in columns:
        if column not in f:
            raise AscamError(f"features: column {column!r} is needed by evaluate")
    labels = f[settings.label]
    if labels.dtype.kind not in "iu":
        raise AscamError(f"label column {settings.label} must be integer")
    classes = np.unique(labels[train | calib])
    if classes.size < 2:
        raise AscamError("the label needs at least two classes in the train and calib splits")

    lookup = {name: i for i, name in enumerate(names)}
    unique, inverse = np.unique(f["defense_action"], return_inverse=True)
    defense = np.array([lookup[str(name)] for name in unique])[inverse]
    session_names, session = np.unique(f["session_id"][train], return_inverse=True)
    g_count, d_count, a_count = session_names.size, len(names), len(observers)
    if g_count < 4:
        raise AscamError(f"evaluate needs at least 4 train sessions (cross-fitting uses two "
                         f"halves); found {g_count}")
    calib_sessions = int(np.unique(f["session_id"][calib]).size)
    if calib_sessions < 1:
        raise AscamError("evaluate needs a calib split to freeze bin edges")

    t_defense, t_label = defense[train], np.searchsorted(classes, labels[train])
    t_samples = dataset.traces[f["trace_offset"][train]]
    c_defense, c_samples = defense[calib], dataset.traces[f["trace_offset"][calib]]
    cell = session * d_count + t_defense
    traces = np.bincount(cell, minlength=g_count * d_count).reshape(g_count, d_count)
    if np.any(traces == 0):
        g, d = np.argwhere(traces == 0)[0]
        raise AscamError(f"train session {session_names[g]} has no traces for {names[d]}; "
                         "every train session must cover every defense")
    sums = []
    for column in columns[1:]:
        values = f[column][train].astype(float)
        if not np.all(np.isfinite(values)):
            raise AscamError(f"overhead column {column} must be finite on the train split")
        sums.append(np.bincount(cell, weights=values,
                                minlength=g_count * d_count).reshape(g_count, d_count))

    c_count, k_count = classes.size, settings.bins
    counts = np.zeros((g_count, d_count, a_count, c_count, k_count), dtype=np.int64)
    edges = np.zeros((d_count, a_count, k_count - 1))
    for d in range(d_count):
        calibration, rows = c_samples[c_defense == d], t_defense == d
        if len(calibration) < k_count:
            raise AscamError(f"{names[d]}: {len(calibration)} calib traces cannot freeze "
                             f"{k_count} bins; generate more traces or lower --bins")
        base = (session[rows] * c_count + t_label[rows]) * k_count
        for a in range(a_count):
            edges[d, a] = quantile_edges(calibration[:, a], k_count)
            if np.any(np.diff(edges[d, a]) <= 0):
                raise AscamError(f"{names[d]} x {observers[a]}: the calib values do not give "
                                 f"{k_count} distinct bins; lower --bins")
            bins = bin_index(t_samples[rows, a], edges[d, a])
            counts[:, d, a] = np.bincount(base + bins, minlength=g_count * c_count * k_count
                                          ).reshape(g_count, c_count, k_count)
    return Cells(counts, edges, traces, sums[0], sums[1], session_names.tolist(), defenses,
                 observers, classes.tolist(), int(calib.sum()), calib_sessions,
                 int(np.sum(split == "test")))


class _SessionCounts:
    """Train histograms behind the dataset interface that value_of_game.analyze uses."""

    def __init__(self, counts: NDArray, channel: dict):
        self.counts = counts
        self.A = channel.get("leakage_amplitude")
        self.s = channel.get("separability")

    @property
    def n_sessions(self) -> int:
        return self.counts.shape[0]

    def mi_matrix(self, sessions: NDArray | None = None) -> NDArray:
        selected = self.counts if sessions is None else self.counts[sessions]
        return mi_from_counts(selected.sum(axis=0))


def _estimate(flat: NDArray, cells: Cells, weights: NDArray, settings: EvalSettings
              ) -> tuple[NDArray, NDArray, NDArray, NDArray]:
    """(MI, energy, latency, loss) from session weights (ones = the full data).

    False alarms are not modeled (F_d = 0 for every row), so lambda_F adds nothing.
    """
    mi = mi_from_counts((weights @ flat).reshape(cells.counts.shape[1:]))
    n = weights @ cells.traces
    energy = (weights @ cells.energy_sum) / n
    latency = (weights @ cells.latency_sum) / n
    overhead = settings.lambda_energy * energy + settings.lambda_latency * latency
    return mi, energy, latency, loss_matrix(mi, overhead)


def _solve(loss: NDArray, types: list) -> tuple:
    """games.solve_bayesian plus a solver-independent duality certificate.

    primal = sum_t pi_t max_a (p* M_t)_a and dual = min_d sum_t pi_t (M_t q*_t)_d
    bound the game value from above and below, so their gap is zero only at an
    optimum.
    """
    mats = [loss[:, list(actions)] for _, actions, _ in types]
    prior = np.array([weight for *_, weight in types])
    try:
        solution = solve_bayesian(mats, prior)
    except (RuntimeError, ValueError) as error:
        raise AscamError(f"game solve failed: {error}") from error
    primal = float(sum(prior[t] * np.max(solution.p @ m) for t, m in enumerate(mats)))
    mixed = sum(prior[t] * (m @ q) for t, (m, q) in enumerate(zip(mats, solution.q_type)))
    return solution, primal, float(np.min(mixed))


def _interval(replicates: NDArray) -> tuple[NDArray, NDArray, NDArray]:
    tail = 0.5 * (1.0 - LEVEL)
    low, high = np.quantile(replicates, [tail, 1.0 - tail], axis=0)
    return low, high, replicates.std(axis=0, ddof=1)


def _cell_block(point: NDArray, replicates: NDArray) -> dict:
    low, high, se = _interval(replicates)
    return {"matrix": point, "ci_low": low, "ci_high": high, "se": se}


def _value_of_game(cells: Cells, energy: NDArray, latency: NDArray, settings: EvalSettings,
                   seed: np.random.SeedSequence, channel: dict) -> dict:
    """The cross-fitted check of value_of_game.analyze, or the reason it cannot run."""
    names = cells.names
    if [name[:2] for name in names[:3]] != ["D0", "D1", "D2"]:
        return {"skipped": "src/baselines.py fit_policies takes B0, B1, B2 from the first "
                           "three rows, so the library must start with D0, D1, D2; found "
                           + ", ".join(names[:3])}
    if not any(not d.get("hop", False) and d.get("power", 0.0) > 0 for d in cells.defenses):
        return {"skipped": "baseline B3 picks the best noise-only defense (injected noise, "
                           "no hopping) and this library has none (D1-fixed-dummy injects no "
                           "noise); generate with --library full to run the check"}
    k = settings.lambda_energy / LAMBDA_E
    if not math.isclose(settings.lambda_latency, k * LAMBDA_L, rel_tol=1e-9, abs_tol=1e-12):
        return {"skipped": f"src/value_of_game.py prices overhead as k ({LAMBDA_E:g} E + "
                           f"{LAMBDA_L:g} T), and lambda_energy = {settings.lambda_energy:g}, "
                           f"lambda_latency = {settings.lambda_latency:g} are not on that line"}
    rows = [Row(d["name"], bool(d.get("hop", False)),
                tuple(d.get("allocation") or (0.0,) * N_BANDS), float(d.get("power", 0.0)),
                float(e), float(t))
            for d, e, t in zip(cells.defenses, energy, latency)]
    split_seq, bootstrap_seq = seed.spawn(2)
    try:
        out = analyze(_SessionCounts(cells.counts, channel), rows,
                      [Config(k, TYPE_MODEL_NAMES[settings.type_model])], split_seq,
                      bootstrap_seq, settings.bootstrap, settings.robust_rho)
    except (RuntimeError, ValueError) as error:
        raise AscamError(f"cross-fitted check failed: {error}") from error
    record = {key: value for key, value in out["results"][0].items() if value is not None}
    gaps = record["gaps"]
    return {
        "method": ("cross-fitted (src/value_of_game.py analyze): the train sessions are "
                   "split at random into two halves, every policy is fit on one half and "
                   "scored on the other against the adaptive observer B5, halves swapped "
                   "and averaged; session bootstrap within halves"),
        "decision_rule": ("the game strictly helps only if the 95% CIs of gap_pure and "
                          "gap_robust both exclude 0 (one decision, family size 1)"),
        "game_strictly_helps": bool(gaps["gap_pure"]["ci"][0] > 0
                                    and gaps["gap_robust"]["ci"][0] > 0),
        **record,
    }


def evaluate_dataset(dataset: Dataset, settings: EvalSettings) -> dict:
    """Build the results dictionary (results_schema_version 0.1.0)."""
    type_name = TYPE_MODEL_NAMES[settings.type_model]
    types = TYPE_MODELS[type_name]
    cells = extract_cells(dataset, settings)
    g_count, d_count = cells.traces.shape
    flat = cells.counts.reshape(g_count, -1).astype(float)
    mi, energy, latency, loss = _estimate(flat, cells, np.ones(g_count), settings)
    solved, primal, dual = _solve(loss, types)

    equilibrium_seq, value_seq = np.random.SeedSequence(
        settings.seed, spawn_key=(EVALUATE_SEED_ROLE,)).spawn(2)
    rng = np.random.default_rng(equilibrium_seq)
    b_count = settings.bootstrap
    loss_reps = np.empty((b_count,) + loss.shape)
    mi_reps = np.empty_like(loss_reps)
    value_reps, policy_reps = np.empty(b_count), np.empty((b_count, d_count))
    uniform = np.full(g_count, 1.0 / g_count)
    for r in range(b_count):
        weights = rng.multinomial(g_count, uniform).astype(float)
        mi_reps[r], _, _, loss_reps[r] = _estimate(flat, cells, weights, settings)
        replicate, _, _ = _solve(loss_reps[r], types)
        value_reps[r], policy_reps[r] = replicate.value, replicate.p
    support = (policy_reps > SUPPORT_TOL).mean(axis=0)
    p_low, p_high, _ = _interval(policy_reps)
    (value_low, value_high), value_ci_bc, value_se = _ci(solved.value, value_reps, LEVEL)

    names, observers, manifest = cells.names, cells.observers, dataset.manifest
    channel = manifest.get("channel", {}).get("parameters") or {}
    environment = environment_record()
    defender_policy = [
        {"action": names[d], "p": solved.p[d], "ci": [p_low[d], p_high[d]],
         "bootstrap_mean": policy_reps[:, d].mean(), "support_stability": support[d]}
        for d in range(d_count)
    ]
    result = {
        "results_schema_version": RESULTS_SCHEMA_VERSION,
        "tool": {"name": "ascam", "command": "evaluate", "version": __version__,
                 "status": "research preview"},
        "N": int(cells.traces.sum()),
        "G": g_count,
        "data": {
            "origin": dataset.origin,
            "dataset_id": f"sha256:{dataset.manifest_sha256}",
            "dataset_version": manifest.get("dataset_version"),
            "schema_version": manifest.get("schema_version"),
            "container": manifest.get("container", {}).get("format"),
            "source": manifest.get("source"),
            "dut": manifest.get("dut"),
            "abstraction": manifest.get("abstraction"),
            "master_seed": manifest.get("master_seed"),
            "generator": manifest.get("generator"),
            "channel_parameters": channel,
            "files": manifest.get("files"),
            "validation": dataset.validation,
            "splits_used": {
                "train": {"traces": int(cells.traces.sum()), "sessions": g_count},
                "calib": {"traces": cells.calib_traces, "sessions": cells.calib_sessions,
                          "use": "bin edges only"},
            },
            "traces_per_defense": dict(zip(names, cells.traces.sum(axis=0).tolist())),
            "label": {"column": settings.label, "classes": cells.classes},
        },
        "test_split": {"rows_present": cells.test_rows, "rows_used": 0, "reads": []},
        "config": {**asdict(settings), "type_model_name": type_name,
                   "observer_cost": dict(zip(observers, OBS_COST.tolist()))},
        "actions": {"defender": names, "observer": observers},
        "estimator": {
            "name": "binned plug-in mutual information with Miller-Madow correction",
            "function": "src/metrics.py mi_from_counts",
            "bins": settings.bins,
            "bin_edges": "equal-mass, frozen per (defense, observer) on the calib split",
            "label": settings.label,
            "units": "bits per trace",
        },
        "interval_method": {
            "name": "session (cluster) bootstrap, percentile",
            "level": LEVEL,
            "bootstrap": b_count,
            "resampling_unit": "train session; every cell is recomputed from the same "
                               "resample, so correlations between cells are kept",
            "value_sensitivity": "bias-corrected percentile interval (value_ci_bc)",
        },
        "payoff": {
            "definition": LOSS_DEFINITION,
            "units": "bits per trace plus priced normalized overhead minus observer cost",
            "rows": names,
            "columns": observers,
            **_cell_block(loss, loss_reps),
            "leakage_mi_bits": _cell_block(mi, mi_reps),
            "overhead": {"energy": energy, "latency": latency,
                         "false_alarm": np.zeros(d_count), "observer_cost": OBS_COST,
                         "source": "per-defense means of the dataset overhead columns, "
                                   "resampled with the sessions; false alarms are not "
                                   "modeled, so lambda_false_alarm has no effect"},
            "traces_per_cell": cells.traces.sum(axis=0),
        },
        "equilibrium": {
            "game": "zero_sum" if len(types) == 1 else "bayesian, zero-sum per type",
            "type_model": {
                "index": settings.type_model, "name": type_name,
                "prior": [weight for *_, weight in types],
                "types": [{"name": name, "actions": [observers[a] for a in actions]}
                          for name, actions, _ in types],
            },
            "value": solved.value,
            "value_ci": [value_low, value_high],
            "value_ci_bc": value_ci_bc,
            "value_outside_ci": bool(not value_low <= solved.value <= value_high),
            "value_se": value_se,
            "value_bootstrap_mean": value_reps.mean(),
            "value_replicates": value_reps,
            "defender_policy": defender_policy,
            "support_tolerance": SUPPORT_TOL,
            "stable_support": [names[d] for d in range(d_count) if support[d] >= STABLE_SUPPORT],
            "unstable_support": [names[d] for d in range(d_count)
                                 if 1.0 - STABLE_SUPPORT < support[d] < STABLE_SUPPORT],
            "observer_policies": [
                {"type": name, "policy": dict(zip([observers[a] for a in actions], q))}
                for (name, actions, _), q in zip(types, solved.q_type)
            ],
            "type_values": solved.v_type,
            "primal_value": primal,
            "dual_value": dual,
            "duality_gap": primal - dual,
            "solver": {
                "name": "scipy.optimize.linprog", "method": "highs",
                "function": "src/games.py solve_bayesian",
                "problem": "Bayesian epigraph LP; with one observer type it is the plain "
                           "zero-sum LP",
                "status": solved.status,
                "certificate": "duality_gap = primal_value - dual_value from p* and the "
                               "dual observer mixtures q*",
            },
            "note": ("in-sample plug-in equilibrium of the estimated matrix; the bootstrap "
                     "shows sampling variability, and value_of_game is the held-out check. "
                     "value_outside_ci flags a full-data value outside its percentile "
                     "interval, a sign of plug-in bias in the min over noisy rows; compare "
                     "value_ci_bc"),
        },
        "value_of_game": _value_of_game(cells, energy, latency, settings, value_seq, channel),
        "multiplicity": {
            "family_size": 1,
            "scan": "none",
            "note": "per-cell and per-action intervals are pointwise 95% percentile "
                    "intervals with no multiplicity correction",
        },
        "stopping_rule": "fixed n: every train trace is used once; no sequential looks",
        "provenance": {
            "seed": settings.seed,
            "seed_derivation": ("numpy SeedSequence(seed, spawn_key=(2,)).spawn(2) gives the "
                                "equilibrium bootstrap and the value-of-game stream, which "
                                "spawns the session split and the bootstrap of "
                                "value_of_game.analyze"),
            "versions": {"ascam": __version__,
                         **{k: v for k, v in environment.items() if k != "platform"}},
            "platform": environment["platform"],
            "dataset_id": f"sha256:{dataset.manifest_sha256}",
            "dataset_master_seed": manifest.get("master_seed"),
            "reproducibility": ("the same dataset, config, seed, and versions give a "
                                "byte-identical results JSON"),
        },
        "caveat": manifest.get("caveat", "unknown data source"),
        "limitations": [
            "The band4 channel is synthetic: gains, separability, and costs are modeling "
            "knobs, not calibrated to any device.",
            "Binned plug-in MI is biased at finite N (Miller-Madow removes only the leading "
            "term) and binning loses information; intervals do not remove that bias.",
            "The equilibrium is an in-sample plug-in of the estimated matrix; its bootstrap "
            "interval shows sampling variability, not the optimism of fitting and scoring "
            "on the same data. value_of_game is the held-out check.",
            "Percentile bootstrap intervals for min/max functionals can under-cover near "
            "ties, and all intervals are pointwise, not simultaneous.",
            "A low leakage estimate is not a security certification, and a failed observer "
            "is not evidence of no leakage.",
        ],
    }
    return _jsonable(result)


def _jsonable(value):
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        number = float(value)
        return number if math.isfinite(number) else None
    return value


def write_results(result: dict, path: str | Path) -> Path:
    """Write the results JSON with LF line endings on every platform."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8",
                    newline="\n")
    return path
