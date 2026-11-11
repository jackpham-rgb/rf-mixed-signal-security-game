"""ascam command-line interface (research preview).

Run from ``software/`` as ``python -m src.cli COMMAND ...``. After
``python -m pip install -e .`` the same commands run as ``ascam COMMAND ...``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .dataset import AscamError

DESCRIPTION = f"""\
ascam {__version__}, research preview (working name, from Adaptive Spectral
CAMouflage). Evaluates synthetic mixed-signal side-channel defenses against an
adaptive observer: write a synthetic dataset, estimate the defender loss
matrix with session-bootstrap intervals, solve the defender/observer game, and
draw figures from the results JSON.

Defensive research only: synthetic keys, no capture or attack workflows. A
low leakage score is not a security certification."""

EPILOG = """\
implemented today:
  generate   synthetic band4 dataset (the four-band channel of
             src/band_channel.py), written as manifest.json + features.npz +
             traces.npz: a documented NPZ fallback for the planned
             Parquet/Zarr layout, same column names
  evaluate   payoff matrix with per-cell session-bootstrap intervals; game
             value interval, mixed strategy with support stability,
             primal-dual gap, solver status; cross-fitted value-of-game check
             for datasets made with --library full
  report     figures regenerated from a results JSON only

planned, not implemented:
  ascam import; RTL/VCD DUTs (synth_kernel, aes128_32b) and the flags
  --netlists, --pvt, --abstraction; Parquet/Zarr containers; YAML configs;
  --workers, --log-level, --dry-run; reading the test split under a
  pre-registered hypothesis ID; an importable "ascam" Python package.

Run from software/ as "python -m src.cli COMMAND", or as "ascam COMMAND"
after "python -m pip install -e .". Status and examples are in
software/README.md, section "Command-line tool (ascam)"."""

GENERATE_HELP = """\
Write a small synthetic dataset from the band4 channel (src/band_channel.py).

The directory holds manifest.json, traces.npz (N x 4 float32, one column per
observer band A0 to A3), and features.npz (one row per trace; text columns
dictionary-encoded). The manifest lists every column with its type and a
note on its meaning. This NPZ + JSON container is a light-weight fallback: it
has no chunking and suits small datasets. Parquet/Zarr containers and RTL DUTs
are planned."""

EVALUATE_HELP = """\
Estimate the payoff matrix from the train split (bin edges frozen on the calib
split), solve the defender/observer game, and write a results JSON with
per-cell session-bootstrap intervals, the equilibrium value interval, the
mixed strategy with per-action support stability, the primal-dual gap, solver
status, N and G, and provenance. The test split is never read.

A cross-fitted bootstrap (src/value_of_game.py analyze) then compares the game
with the best single defense and baselines B0 to B4 on held-out sessions. It
runs only when the library has a noise-only defense for baseline B3 (generate
with --library full; the named D0 to D3 library has none) and the prices keep
lambda_energy : lambda_latency = 0.30 : 0.20, the price line of
src/value_of_game.py. Otherwise the results JSON records why it was skipped.

Settings come from the defaults, then --config (JSON; YAML is planned), then
the flags below. Config keys: seed, bootstrap, bins, lambda_energy,
lambda_latency, lambda_false_alarm, type_model, robust_rho, label."""

REPORT_HELP = """\
Regenerate figures from an ascam evaluate results JSON only (it never reads
traces): payoff_equilibrium.png, equilibrium_uncertainty.png, and, when the
cross-fitted check ran, value_of_game.png."""


def _fractions(text: str) -> tuple[float, float, float]:
    try:
        values = tuple(float(part) for part in text.split(","))
    except ValueError:
        values = ()
    if len(values) != 3:
        raise argparse.ArgumentTypeError("expected three comma-separated fractions, "
                                         "for example 0.6,0.2,0.2")
    return values


def build_parser() -> argparse.ArgumentParser:
    raw = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(prog="ascam", description=DESCRIPTION, epilog=EPILOG,
                                     formatter_class=raw)
    parser.add_argument("--version", action="version",
                        version=f"ascam {__version__} (research preview)")
    commands = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    generate = commands.add_parser("generate", help="write a small synthetic dataset",
                                   description=GENERATE_HELP, formatter_class=raw)
    generate.add_argument("--out", type=Path, required=True,
                          help="dataset directory to create; refused if it exists and is "
                               "not empty")
    generate.add_argument("--dut", choices=["band4"], default="band4",
                          help="data source; only band4, the parametric four-band channel, is "
                               "implemented (default: %(default)s)")
    generate.add_argument("--traces", type=int, default=10_000,
                          help="total traces over all splits, sessions, and defenses "
                               "(default: %(default)s)")
    generate.add_argument("--sessions", type=int, default=30,
                          help="total sessions over all splits (default: %(default)s)")
    generate.add_argument("--split", type=_fractions, default=(0.6, 0.2, 0.2),
                          metavar="TRAIN,CALIB,TEST",
                          help="session fractions per split (default: 0.6,0.2,0.2)")
    generate.add_argument("--seed", type=int, default=126,
                          help="master seed (default: %(default)s)")
    generate.add_argument("--library", choices=["named", "full"], default="named",
                          help="named: D0 to D3; full: D0 to D3 plus every hop/noise "
                               "combination, 213 rows (default: %(default)s)")
    generate.add_argument("--leakage-amplitude", type=float, default=0.5,
                          help="leakage-to-noise ratio A (default: %(default)s)")
    generate.add_argument("--separability", type=float, default=1.0,
                          help="band separability s in [0, 1] (default: %(default)s)")
    generate.add_argument("--dataset-version", default="0.1.0",
                          help="semver recorded for the dataset (default: %(default)s)")
    generate.set_defaults(handler=_generate)

    evaluate = commands.add_parser("evaluate", help="estimate the payoff matrix and solve "
                                   "the game", description=EVALUATE_HELP, formatter_class=raw)
    evaluate.add_argument("--out", type=Path, required=True, help="results JSON to write")
    evaluate.add_argument("--data", type=Path,
                          help="dataset directory from ascam generate; if omitted, a dataset "
                               "is synthesized in memory with the generate defaults and --seed")
    evaluate.add_argument("--config", type=Path, help="JSON config file")
    evaluate.add_argument("--seed", type=int,
                          help="bootstrap seed, also the generator seed when --data is omitted "
                               "(default: 126)")
    evaluate.add_argument("--bootstrap", type=int,
                          help="session-bootstrap replicates (default: 1000)")
    evaluate.add_argument("--bins", type=int, help="MI histogram bins (default: 16)")
    evaluate.add_argument("--type-model", type=int, choices=range(4),
                          help="observer types: 0 = one adaptive type over A0 to A3 (default); "
                               "1 to 3 = the Bayesian type mixtures of TYPE_MODELS in "
                               "src/baselines.py")
    evaluate.add_argument("--lambda-energy", type=float,
                          help="price of normalized energy (default: 0.30)")
    evaluate.add_argument("--lambda-latency", type=float,
                          help="price of normalized latency (default: 0.20)")
    evaluate.set_defaults(handler=_evaluate)

    report = commands.add_parser("report", help="draw figures from a results JSON",
                                 description=REPORT_HELP, formatter_class=raw)
    report.add_argument("--results", type=Path, required=True,
                        help="results JSON from ascam evaluate")
    report.add_argument("--out", type=Path, required=True,
                        help="figure directory (created if needed)")
    report.set_defaults(handler=_report)
    return parser


def _generate(args: argparse.Namespace) -> int:
    from .dataset import GenerateSpec, synthesize, write_dataset

    spec = GenerateSpec(seed=args.seed, traces=args.traces, sessions=args.sessions,
                        split=args.split, dut=args.dut, library=args.library,
                        leakage_amplitude=args.leakage_amplitude,
                        separability=args.separability, dataset_version=args.dataset_version)
    dataset = synthesize(spec)
    path = write_dataset(dataset, args.out)
    m = dataset.manifest
    splits = ", ".join(f"{name} {s['sessions']}" for name, s in m["splits"].items())
    print(f"Wrote {path}: N = {m['N']} traces, G = {m['G']} sessions ({splits}), "
          f"{len(m['defense_actions'])} defenses x {len(m['observer_actions'])} observer "
          f"bands, {m['traces_per_session_per_defense']} traces per session per defense")
    return 0


def _evaluate(args: argparse.Namespace) -> int:
    from .dataset import GenerateSpec, open_dataset, synthesize_in_memory
    from .evaluate import evaluate_dataset, load_settings, write_results

    settings = load_settings(args.config, {
        "seed": args.seed, "bootstrap": args.bootstrap, "bins": args.bins,
        "type_model": args.type_model, "lambda_energy": args.lambda_energy,
        "lambda_latency": args.lambda_latency,
    })
    if args.data is None:
        dataset = synthesize_in_memory(GenerateSpec(seed=settings.seed))
    else:
        dataset = open_dataset(args.data)
    result = evaluate_dataset(dataset, settings)
    write_results(result, args.out)
    eq = result["equilibrium"]
    low, high = eq["value_ci"]
    print(f"Wrote {args.out}: N = {result['N']} train traces, G = {result['G']} sessions, "
          f"game value {eq['value']:.4f} [95% CI {low:.4f}, {high:.4f}], duality gap "
          f"{eq['duality_gap']:.1e}, solver {eq['solver']['status']}")
    if eq["value_outside_ci"]:
        print("Note: the full-data value lies outside its percentile interval (plug-in bias "
              "of the min over noisy rows); compare value_ci_bc in the JSON")
    support = [f"{r['action']} p={r['p']:.2f} (in support {100 * r['support_stability']:.0f}%)"
               for r in eq["defender_policy"] if r["p"] > eq["support_tolerance"]]
    others = sum(r["p"] <= eq["support_tolerance"] and r["support_stability"] >= 0.05
                 for r in eq["defender_policy"])
    print("Equilibrium defense (full train split): " + "; ".join(support)
          + (f"; {others} other defenses enter the support in >= 5% of bootstrap replicates"
             if others else ""))
    vog = result["value_of_game"]
    if "gaps" in vog:
        gaps = ", ".join(
            f"{gap} {vog['gaps'][gap]['est']:.4f} "
            f"[{vog['gaps'][gap]['ci'][0]:.4f}, {vog['gaps'][gap]['ci'][1]:.4f}]"
            for gap in ("gap_pure", "gap_robust"))
        print(f"Cross-fitted {gaps}; game strictly helps: {vog['game_strictly_helps']}")
    else:
        print(f"Cross-fitted value-of-game check skipped: {vog['skipped']}")
    return 0


def _report(args: argparse.Namespace) -> int:
    try:
        results = json.loads(Path(args.results).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise AscamError(f"cannot read results {args.results}: {error}") from error
    if (results.get("tool", {}).get("command") != "evaluate"
            or not str(results.get("results_schema_version", "")).startswith("0.")):
        raise AscamError(f"{args.results} is not an ascam evaluate results JSON (results "
                         "schema 0.x); sweep results are drawn by python -m src.figures")
    from .report import make_evaluation_figures

    for path in make_evaluation_figures(results, Path(args.out)):
        print(f"Wrote {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.handler(args)
    except AscamError as error:
        print(f"ascam: error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
