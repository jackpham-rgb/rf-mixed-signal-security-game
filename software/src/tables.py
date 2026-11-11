"""Machine-generated markdown tables from the sweep results JSON (never hand-edited)."""

from __future__ import annotations

from pathlib import Path


def _ci(x):
    return f"[{x[0]:.4f}, {x[1]:.4f}]"


def _n(x):
    return "n/a" if x is None else f"{x:.4f}"


def _method_table(res: dict) -> list[str]:
    lines = ["| Method | Loss vs B5 | Leakage (bits) | Energy | Exact held-out loss |", "|---|---|---|---|---|"]
    for m, v in res["methods"].items():
        lines.append(f"| {m} | {v['loss']:.4f} {_ci(v['loss_ci'])} | {v['leak']:.4f} {_ci(v['leak_ci'])} | "
                     f"{v['energy']:.3f} | {_n(v.get('exact_heldout_loss'))} |")
    lines += ["", "| Gap | Cross-fitted [95% CI] | In-sample | Exact population |", "|---|---|---|---|"]
    for g, v in res["gaps"].items():
        exact = res["gaps_exact"][g] if res.get("gaps_exact") else None
        lines.append(f"| {g} | {v['est']:.4f} {_ci(v['ci'])} | {res['gaps_in_sample'][g]:.4f} | {_n(exact)} |")
    lines += ["", f"Full-data game policy: {res['game_policy']}", "",
              f"Full-data chosen rows: {res['chosen_rows']}", ""]
    return lines


def write_tables(payload: dict, path: Path) -> None:
    s = payload["summary"]
    cfg = payload["config"]
    L = ["# Value-of-game sweep: generated tables", "",
         f"Seed {payload['seed']}, simulator {payload['simulator_version']}, {s['grid_points']} grid points, "
         f"runtime {payload['runtime_s']:.0f} s, {cfg['n_sessions']} sessions x {cfg['n_traces']} traces per cell, "
         f"B = {cfg['n_boot']} bootstrap replicates. All gaps are cross-fitted estimates against the adaptive "
         "observer B5 with 95% session-bootstrap percentile CIs, in loss units (bits plus priced overhead). "
         "Regenerate with `python -m src.run_sweep`.", "",
         "## Summary", "", "| Quantity | Count |", "|---|---|",
         f"| Grid points | {s['grid_points']} |",
         f"| gap_pure CI excludes 0 (above) | {s['gap_pure_ci_above_0']} |",
         f"| gap_robust CI excludes 0 (above) | {s['gap_robust_ci_above_0']} |",
         f"| Both CIs exclude 0 (above) | {s['both_above_0']} |",
         f"| Both, bias-corrected percentile CIs (sensitivity) | {s['both_above_0_bias_corrected']} |",
         f"| Both, Bonferroni (z = {s['z_bonferroni']:.2f}) | {s['both_above_0_bonferroni']} |",
         f"| gap_pure CI entirely below 0 | {s['gap_pure_ci_below_0']} |",
         f"| Exact gap_pure > 0.002 / > 0.01 | {s['exact_gap_pure_gt_0.002']} / {s['exact_gap_pure_gt_0.01']} |",
         f"| Exact gap_robust > 0.01 | {s['exact_gap_robust_gt_0.01']} |",
         f"| Fine-library exact gap_pure > 0.002 / > 0.01 | {s['fine_gap_pure_gt_0.002']} / {s['fine_gap_pure_gt_0.01']} |",
         f"| Max exact gap_pure, coarse / fine library | {_n(s['max_exact_gap_pure'])} / {_n(s['max_fine_gap_pure'])} |",
         f"| Max exact gap_robust (coarse) | {_n(s['max_exact_gap_robust'])} |", "",
         "Main-effect variance share of each parameter:", "",
         "| Gap | A | s | k | types |", "|---|---|---|---|---|"]
    for g, v in s["variance_share"].items():
        L.append(f"| {g} | {v['A']:.3f} | {v['s']:.3f} | {v['k']:.3f} | {v['types']:.3f} |")
    rep = payload["representative"]["result"]
    L += ["", "## Representative point", "",
          f"A = {rep['A']}, s = {rep['s']}, k = {rep['k']} (lambda_E = {rep['lambda_E']:.3f}, "
          f"lambda_L = {rep['lambda_L']:.3f}); {rep['types']}.", ""]
    L += _method_table(rep)
    L += ["## Scaffold check (original 4x4 scalar model)", ""]
    L += _method_table(payload["scaffold"])
    L += ["## All grid points", "",
          "Exact columns use the exact binned MI of the simulated library; fine columns use exact continuous MI, "
          "with the game on the coarse library and pure rows from the fine library. Flags: * both CIs above 0, "
          "** also Bonferroni.", "",
          "| A | s | k | types | gap_pure [CI] | gap_robust [CI] | exact gap_pure | exact gap_robust | "
          "fine gap_pure | fine gap_robust | in-sample gap_pure | flag |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in payload["results"]:
        g, e, f = r["gaps"], r["gaps_exact"], r["gaps_fine"] or {}
        flag = "**" if r["flags"]["both_bonferroni"] else ("*" if r["flags"]["both"] else "")
        L.append(f"| {r['A']} | {r['s']} | {r['k']} | {r['types']} | {g['gap_pure']['est']:.4f} "
                 f"{_ci(g['gap_pure']['ci'])} | {g['gap_robust']['est']:.4f} {_ci(g['gap_robust']['ci'])} | "
                 f"{e['gap_pure']:.4f} | {e['gap_robust']:.4f} | {_n(f.get('gap_pure'))} | "
                 f"{_n(f.get('gap_robust'))} | {r['gaps_in_sample']['gap_pure']:.4f} | {flag} |")
    L += ["", "## MI estimator diagnostics per dataset", "",
          "| A | s | mean MC - exact binned (bits) | worst cell abs error | max binning loss | runtime (s) |",
          "|---|---|---|---|---|---|"]
    for d in payload["diagnostics"]:
        L.append(f"| {d['A']} | {d['s']} | {d['mc_minus_exact_binned_mean']:.4f} | "
                 f"{d['mc_minus_exact_binned_worst']:.4f} | {d['binning_loss_max']:.4f} | {d['runtime_s']:.0f} |")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(L) + "\n")
