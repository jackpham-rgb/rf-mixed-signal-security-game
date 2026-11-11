# Public tool roadmap

This document defines the public tool that this research should leave behind.
The README has the short version; this is the contract a contributor or user
can build against.

**Status: planned.** No `ascam` package or CLI exists yet. Everything below is
a design target. The only runnable code today is the reference simulator in
`software/` (`python -m src.run_experiment`).

## 1. Scope

**One sentence.** `ascam` (working name, from *Adaptive Spectral CAMouflage*)
evaluates adaptive mixed-signal side-channel defenses against adaptive
observers, using large labeled trace datasets, and reports the game-optimal
randomized defense with honest uncertainty.

**In scope**

- Generating synthetic trace datasets from RTL simulation (switching activity
  from VCD or a Verilator harness, pushed through a declared channel model).
- Importing measured traces from hardware the user owns or is authorized to
  test, as long as they fit the dataset schema in Section 4.
- Estimating leakage (TVLA, mutual information, GLM, CPA-style scores on
  synthetic keys) and overhead (energy, latency, area) per defense/observer pair.
- Building the payoff matrix with grouped confidence intervals.
- Solving zero-sum, Bayesian Stackelberg, and prior-robust games, and reporting
  equilibrium uncertainty (value interval, mixed-strategy distribution, support
  stability).

**Out of scope, permanently**

- Capture automation against devices the user does not own.
- Key extraction from real products, firmware dumping, bypassing access
  controls, fault-injection recipes, RF range extension, or evasion of
  monitoring.
- Any feature whose main use is attacking rather than evaluating a defense.

Pull requests that add out-of-scope features are closed without review.

## 2. Users and their questions

| User | Question the tool answers |
|---|---|
| Student | "If I add dummy switching to this AES core, how much leakage does it remove, and how sure am I?" |
| Researcher | "Does my new countermeasure beat fixed noise and random DVFS against an observer that adapts its band and filter?" |
| Hardware designer | "Which mix of clock gating and frequency hopping gives the best leakage/overhead tradeoff on my own RTL, before tape-out?" |

## 3. CLI shape

Four subcommands. Each reads files and writes files; none keeps hidden state.

```text
ascam generate  --dut NAME --traces N --sessions G --netlists K --pvt LIST
                --abstraction {behavioral,gate_zero_delay,gate_sdf}
                --seed SEED --out DATASET_DIR
ascam import    --raw RAW_DIR --mapping MAPPING.yaml --out DATASET_DIR
ascam evaluate  --data DATASET_DIR --config CONFIG.yaml --out RESULTS.json
ascam report    --results RESULTS.json --out FIGURE_DIR
```

Shared flags: `--workers N`, `--log-level`, `--dry-run` (print the plan and
estimated disk/compute cost, do nothing).

Rules:

- `generate` refuses to overwrite an existing dataset directory.
- `evaluate` refuses to read the `test` split unless the config names a
  pre-registered hypothesis ID, and it records every test-split read in the
  results file.
- `report` reads only the results JSON. It never reads traces.

## 4. Python API shape

The CLI is a thin wrapper over a library, so notebooks and scripts get the same
behavior.

```python
import ascam

ds = ascam.Dataset.open("data/p1")                 # manifest + Zarr + Parquet
cfg = ascam.EvalConfig.from_yaml("configs/d0-d3_a0-a3.yaml")

payoff = ascam.estimate_payoff(ds, cfg)            # matrix + per-cell CIs
eq = ascam.solve(payoff, game="zero_sum")          # or "bayesian", "robust"
unc = ascam.equilibrium_uncertainty(ds, cfg, method="cluster_bootstrap")

ascam.write_results("results/p1.json", payoff, eq, unc, provenance=ds.manifest)
```

Public objects: `Dataset`, `EvalConfig`, `PayoffMatrix`, `Equilibrium`,
`EquilibriumUncertainty`, plus the extension protocols in Section 6. Everything
else is private and may change without notice.

## 5. Data schema

Reused from `theory/high-volume-data-and-digital-circuit-extension.md`
Section 6. A dataset is a directory:

```text
DATASET_DIR/
  manifest.json       dataset_version, schema_version, master_seed,
                      generator commit, tool versions (iverilog, Verilator,
                      Yosys, PDK tag), DUT source and license, channel model
                      and parameters, N, G, splits, SHA-256 of every file
  traces.zarr/        N x T array, int16 with recorded scale or float32,
                      chunked along traces (8 to 64 MB per chunk), Blosc/Zstd
  features.parquet    one row per trace (columns below)
  activity.zarr/      optional N x P per-cycle switching activity Q[k]
```

Required `features.parquet` columns:

| Column | Type | Meaning |
|---|---|---|
| `trace_id` | int64 | unique, monotonic |
| `trace_offset` | int64 | row index into `traces.zarr` |
| `dataset_version` | string | semver of the dataset |
| `source` | category | `synthetic` or `measured` |
| `dut` | category | design under test name |
| `abstraction` | category | `behavioral`, `gate_zero_delay`, `gate_sdf`, `fpga`, `board` |
| `netlist_id` | category | synthesis run or board identity |
| `pvt_corner` | category | process/voltage/temperature label |
| `session_id` | category | grouping unit for bootstrap |
| `key_id` | int32 | synthetic key identity (grouping unit) |
| `defense_action` | category | `D0`... |
| `defense_params` | string (JSON) | e.g. dummy level, gate mask, hop set |
| `observer_action` | category | `A0`... |
| `plaintext` | binary | public input |
| `label_hw`, `label_hd` | uint8 | leakage-model labels |
| `tvla_group` | uint8 | 0 fixed, 1 random |
| `energy_nj`, `latency_cycles` | float32, int32 | overhead per operation |
| `seed_sim`, `seed_noise`, `seed_defense` | uint64 | per-trace RNG seeds |
| `split` | category | `train`, `calib`, `test`, fixed at creation |

Optional feature columns (`toggle_total`, `switched_cap_total`,
`toggle_cycle_*`, `band_energy_*`, `peak_freq_hz`) follow the same
definitions as the extension document. New features are new columns in a new
dataset version, never in-place edits.

Validation (`ascam.Dataset.open` runs it every time): checksums match, required
columns exist with the right types, `trace_offset` is in range, and the group
sets (key, session, netlist, PVT) of the three splits do not overlap.

The results JSON has its own `results_schema_version` and always includes N, G,
estimator name and parameters, interval method, bootstrap count, family size
for any scan, stopping rule, every test-split read, and for synthetic data the
string `"proxy: simulated switching activity, not measured leakage"`.

## 6. Extension points

Each extension is a small Python class implementing a protocol. Plugins register
through a Python entry point group (`ascam.duts`, `ascam.channels`, and so on),
so third parties can ship them as separate packages.

| Extension | Protocol (main method) | Must declare |
|---|---|---|
| DUT | `simulate(stimulus, defense, seed) -> ActivityTrace` | RTL source path, license, simulator, clock period, trigger window |
| Channel model | `apply(activity, observer, seed) -> Trace` | parameters, units, which roadmap term (\(H_a\), \(B_d\), \(N_d\), \(W\)) each part models |
| Defense | `register_writes(params) -> list[RegWrite]`, `overhead() -> Overhead` | register map entries, energy/latency/area source (report or estimate) |
| Observer | `transform(traces, budget) -> Features`, `cost() -> float` | band, filter, trace budget, calibration needs |
| Estimator | `estimate(features, labels, groups) -> Estimate` | bias correction, null calibration method, valid input types |
| Game solver | `solve(payoff) -> Equilibrium` | game type, tie-breaking rule, residual checks |

Every new extension must ship with:

1. a unit test against a known answer (for example, a Gaussian channel with
   known SNR for an estimator, or a 2x2 game solvable by hand for a solver);
2. a null test (zero true leakage must not be detected at the declared level);
3. a short docs page with assumptions and units.

A defense that cannot be expressed as register writes plus a measured or
declared overhead is not accepted, because the game needs both.

## 7. Contribution boundaries

**Welcome:** new DUTs (open-licensed RTL), channel models with a stated
physical basis, defenses, observer models, estimators with bias analysis,
solver improvements, importers for measured traces from owned hardware,
documentation, and bug reports with a seed that reproduces them.

**Not accepted:**

- out-of-scope features from Section 1;
- datasets captured from devices the contributor does not own or is not
  authorized to test, or datasets whose license forbids redistribution;
- real (non-synthetic) keys in any dataset or test fixture;
- estimators or ML models without a comparison against a simple statistical
  baseline on the same grouped splits;
- changes that drop a provenance field, a caveat string, or a validation check.

Contributors agree their code is MIT-licensed. Third-party RTL keeps its own
license, recorded in the manifest.

## 8. Versioning

Three independent version numbers, all semver:

| Version | Bumps major when |
|---|---|
| Package (`ascam`) | public API or CLI flags change incompatibly |
| `schema_version` (dataset) | a required column is added, removed, or retyped |
| `results_schema_version` | a results field is removed or changes meaning |

A dataset is immutable once published: fixes become a new `dataset_version`.
Deprecated API or flags keep working for one minor release with a warning.
Each release notes which schema versions it reads and writes.

## 9. Release criteria

### v0.1 (research preview)

- Reference simulator wrapped behind `ascam evaluate` for the existing
  synthetic channel.
- Tests pass on Windows and Linux in CI (GitHub Actions), with a fixed-seed
  regression test on the results JSON.
- README tool section and this document are accurate to the code.

### v0.5 (dataset generator)

- `ascam generate` for DUT-A (synthetic switching kernel) at the behavioral
  level with Icarus Verilog and Verilator, writing the Section 5 schema.
- Icarus-versus-Verilator per-cycle toggle agreement test.
- Ground-truth test: DUT-A with no defense recovers its known leakage.
- Split-disjointness and checksum validation enforced on open.
- Example dataset of 10k traces over at least 30 sessions published with
  manifest and checksums (small enough to download quickly; larger datasets
  regenerate from the seed).

### v1.0 (public tool)

- DUT-B (small AES core) and gate-level (Yosys + Sky130) generation.
- Cluster bootstrap, permutation tests with multiple-comparison control, MI
  with bias calibration, GLM baseline, and equilibrium uncertainty all behind
  the API.
- Documentation site: install, tutorial from dataset to figure, schema
  reference, extension guide, and limitations (including the proxy caveat).
- `CITATION.cff` with author Jack Pham, version, and DOI once archived (for
  example on Zenodo).
- CI runs unit tests, null tests, schema validation, a small end-to-end
  regeneration that compares checksums, and a lint check that rejects em
  dashes in docs.
- A second person has installed it on a clean machine and reproduced the
  tutorial figure from the example dataset.

### After v1.0

- `ascam import` mappings for common bench formats from owned hardware
  (oscilloscope exports, ChipWhisperer captures of the user's own targets).
- Proxy calibration report: regress measured current on simulated activity for
  the same RTL on an owned FPGA, and publish \(R^2\) with its interval.

## 10. What stays out of the public repository

Private schedules, shopping notes, abandoned claims, and personal planning stay
local in the gitignored `private/` folder (see `CLAUDE.md`). Large datasets are published as versioned archives with
checksums, not committed to git.
