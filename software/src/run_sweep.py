"""Value-of-game sweep over LNR A, separability s, price multiplier k, and observer types.

    python -m src.run_sweep --seed 126 --workers 4
    python -m src.run_sweep --quick          # smoke test, seconds; supports no conclusion

Writes the results JSON, machine-generated markdown tables, and figures.
Every (A, s) dataset has its own seed stream SeedSequence(seed, spawn_key=(i_A, i_s)),
so results do not depend on the number of workers.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from . import __version__
from .band_channel import coarse_library
from .baselines import METHODS, TYPE_MODELS
from .provenance import environment_record
from .value_of_game import GAPS, Config, analyze_dataset, analyze_scaffold, frontier

FULL = dict(A=(0.125, 0.25, 0.5, 1.0, 2.0), s=(0.0, 0.25, 0.5, 0.75, 1.0), k=(0.1, 0.3, 1.0, 3.0),
            types=tuple(TYPE_MODELS), n_sessions=128, n_traces=1000, n_boot=1000,
            fine=dict(steps=12, n_powers=41, n_var_grid=121),
            frontier_A=0.5, frontier_s=(0.25, 1.0), frontier_k=tuple(np.round(np.logspace(-2, 1, 13), 4)),
            frontier_boot=200, representative=dict(A=0.5, s=1.0, k=1.0, types="1 type"))
QUICK = dict(A=(0.5, 1.0), s=(0.0, 1.0), k=(0.3, 1.0), types=("1 type", "2 types"),
             n_sessions=32, n_traces=300, n_boot=30, fine=dict(steps=4, n_powers=7, n_var_grid=21),
             frontier_A=0.5, frontier_s=(1.0,), frontier_k=(0.03, 0.3, 1.0, 3.0), frontier_boot=20,
             representative=dict(A=0.5, s=1.0, k=1.0, types="1 type"))
RHO = 0.5
BONFERRONI_ALPHA = 0.05


def _task(args):
    seed, iA, iS, A, s, grid = args
    cfgs = [Config(k, t) for k in grid["k"] for t in grid["types"]]
    ss = np.random.SeedSequence(seed, spawn_key=(iA, iS))
    return analyze_dataset(A, s, ss, cfgs, n_boot=grid["n_boot"], rho=RHO, n_sessions=grid["n_sessions"],
                           n_traces=grid["n_traces"], fine=True, fine_kwargs=grid["fine"])


def _frontier_task(args):
    seed, iA, iS, A, s, grid = args
    ss = np.random.SeedSequence(seed, spawn_key=(iA, iS))
    return {"A": A, "s": s, "points": frontier(A, s, ss, grid["frontier_k"], n_boot=grid["frontier_boot"],
                                                rho=RHO, n_sessions=grid["n_sessions"], n_traces=grid["n_traces"])}


def _flags(r: dict, z_bonf: float) -> dict:
    gp, gr = r["gaps"]["gap_pure"], r["gaps"]["gap_robust"]
    return {
        "pure_above": gp["ci"][0] > 0,
        "robust_above": gr["ci"][0] > 0,
        "both": gp["ci"][0] > 0 and gr["ci"][0] > 0,
        "both_bc": gp["ci_bc"][0] > 0 and gr["ci_bc"][0] > 0,
        "both_bonferroni": (gp["est"] - z_bonf * gp["se"] > 0) and (gr["est"] - z_bonf * gr["se"] > 0),
        "pure_below": gp["ci"][1] < 0,
    }


def variance_shares(results: list[dict], gap: str) -> dict:
    """Main-effect variance share Var(E[gap | factor]) / Var(gap) for each grid factor."""
    y = np.array([r["gaps"][gap]["est"] for r in results])
    tot = y.var()
    out = {}
    for f in ("A", "s", "k", "types"):
        keys = np.array([str(r[f]) for r in results])
        means = {k: y[keys == k].mean() for k in np.unique(keys)}
        out[f] = float(np.var([means[k] for k in keys]) / tot) if tot > 0 else 0.0
    return out


def summarize(results: list[dict], z_bonf: float) -> dict:
    fl = [r["flags"] for r in results]
    ex = [r["gaps_exact"] for r in results]
    fi = [r["gaps_fine"] for r in results if r["gaps_fine"]]
    return {
        "grid_points": len(results),
        "gap_pure_ci_above_0": sum(f["pure_above"] for f in fl),
        "gap_robust_ci_above_0": sum(f["robust_above"] for f in fl),
        "both_above_0": sum(f["both"] for f in fl),
        "both_above_0_bias_corrected": sum(f["both_bc"] for f in fl),
        "both_above_0_bonferroni": sum(f["both_bonferroni"] for f in fl),
        "gap_pure_ci_below_0": sum(f["pure_below"] for f in fl),
        "z_bonferroni": z_bonf,
        "exact_gap_pure_gt_0.002": sum(e["gap_pure"] > 0.002 for e in ex),
        "exact_gap_pure_gt_0.01": sum(e["gap_pure"] > 0.01 for e in ex),
        "exact_gap_robust_gt_0.01": sum(e["gap_robust"] > 0.01 for e in ex),
        "fine_gap_pure_gt_0.002": sum(f["gap_pure"] > 0.002 for f in fi),
        "fine_gap_pure_gt_0.01": sum(f["gap_pure"] > 0.01 for f in fi),
        "max_exact_gap_pure": max(e["gap_pure"] for e in ex),
        "max_fine_gap_pure": max((f["gap_pure"] for f in fi), default=None),
        "max_exact_gap_robust": max(e["gap_robust"] for e in ex),
        "variance_share": {g: variance_shares(results, g) for g in ("gap_pure", "gap_robust")},
    }


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, default=126)
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    ap.add_argument("--quick", action="store_true", help="tiny smoke-test grid")
    ap.add_argument("--n-boot", type=int, default=None, help="override bootstrap replicates")
    ap.add_argument("--output", default=None)
    ap.add_argument("--tables", default=None)
    ap.add_argument("--figures", default=None)
    args = ap.parse_args(argv)
    grid = dict(QUICK if args.quick else FULL)
    if args.n_boot:
        grid["n_boot"] = args.n_boot
    base = Path("results/quick" if args.quick else "results")
    out_json = Path(args.output or base / "value_of_game.json")
    out_md = Path(args.tables or base / "value_of_game_tables.md")
    out_fig = Path(args.figures or base / "figures")

    t0 = time.time()
    tasks = [(args.seed, iA, iS, A, s, grid) for iA, A in enumerate(grid["A"]) for iS, s in enumerate(grid["s"])]
    ftasks = [(args.seed, list(grid["A"]).index(grid["frontier_A"]), list(grid["s"]).index(s),
               grid["frontier_A"], s, grid) for s in grid["frontier_s"]]
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        sc_future = ex.submit(analyze_scaffold, np.random.SeedSequence(args.seed, spawn_key=(1000,)),
                              grid["representative"]["k"], grid["n_boot"], RHO,
                              grid["n_sessions"], grid["n_traces"])
        fr_futures = [ex.submit(_frontier_task, t) for t in ftasks]
        outs = []
        for i, o in enumerate(ex.map(_task, tasks)):
            outs.append(o)
            print(f"[{i + 1}/{len(tasks)}] A={o['diagnostics']['A']} s={o['diagnostics']['s']} "
                  f"{o['diagnostics']['runtime_s']:.0f}s", flush=True)
        scaffold = sc_future.result()
        fronts = [f.result() for f in fr_futures]

    from scipy import stats
    results = [r for o in outs for r in o["results"]]
    m = len(results)
    z_bonf = float(stats.norm.ppf(1 - BONFERRONI_ALPHA / (2 * m)))
    for r in results:
        r["flags"] = _flags(r, z_bonf)
    rep = grid["representative"]
    rep_out = next(o for o in outs if o["diagnostics"]["A"] == rep["A"] and o["diagnostics"]["s"] == rep["s"])
    rep_res = next(r for r in rep_out["results"] if r["k"] == rep["k"] and r["types"] == rep["types"])

    payload = {
        "simulator_version": __version__,
        "seed": args.seed,
        "seed_streams": "SeedSequence(seed, spawn_key=(i_A, i_s)); scaffold spawn_key=(1000,)",
        "config": {**{k: v for k, v in grid.items()}, "rho": RHO, "lambda_E": 0.30, "lambda_L": 0.20,
                   "lambda_F": 0.0, "n_bins": 16, "calibration": "16 sessions x 250 traces per cell",
                   "quadrature_points": 7, "quick": args.quick, "methods": list(METHODS), "gaps": GAPS},
        "environment": environment_record(),
        "runtime_s": time.time() - t0,
        "summary": summarize(results, z_bonf),
        "results": results,
        "diagnostics": [o["diagnostics"] for o in outs],
        "representative": {"result": rep_res, "rows": [r.name for r in coarse_library()],
            "mi_full": rep_out["matrices"]["mi_full"]},
        "scaffold": scaffold,
        "frontier": fronts,
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=1, default=float))
    from .tables import write_tables
    write_tables(payload, out_md)
    from .figures import make_all
    make_all(payload, out_fig)
    s = payload["summary"]
    print(f"done in {payload['runtime_s']:.0f}s: both CIs above 0 at {s['both_above_0']}/{s['grid_points']} "
          f"({s['both_above_0_bonferroni']} Bonferroni). Wrote {out_json}, {out_md}, {out_fig}/")


if __name__ == "__main__":
    main()
