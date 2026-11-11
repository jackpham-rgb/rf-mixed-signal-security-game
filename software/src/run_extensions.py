"""Extension study: fused ("hears everything") observer and the general-sum game.

    python -m src.run_extensions --seed 126 --workers 4
    python -m src.run_extensions --quick        # smoke test

Writes results/extensions.json, results/extensions_tables.md, and figures in
results/figures/ (fig_E1_fused_observer.png, fig_E2_general_sum.png).
"""

from __future__ import annotations

import argparse
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from . import __version__  # noqa: E402
from .extensions import GS_MARGIN, GS_MARGIN_TINY, METRICS, ExtConfig, analyze_extensions  # noqa: E402
from .provenance import environment_record  # noqa: E402

FULL = dict(A=(0.5, 1.0, 2.0), s=(0.0, 0.5, 0.75, 1.0), k=(0.3, 1.0, 3.0),
            types=("1 type", "2 types", "3 types (adaptive 0.5)"), fused=(None, 0.05, 0.1, 0.2),
            n_sessions=128, n_traces=1000, n_boot=150)
QUICK = dict(A=(1.0,), s=(0.0, 1.0), k=(1.0,), types=("1 type",), fused=(None, 0.05),
             n_sessions=24, n_traces=300, n_boot=10)


def _task(args):
    seed, iA, iS, A, s, grid = args
    cfgs = [ExtConfig(k, t, c) for k in grid["k"] for t in grid["types"] for c in grid["fused"]]
    # spawn_key offset 2000 keeps these streams disjoint from the main sweep
    ss = np.random.SeedSequence(seed, spawn_key=(2000, iA, iS))
    return analyze_extensions(A, s, ss, cfgs, n_boot=grid["n_boot"], n_sessions=grid["n_sessions"],
                              n_traces=grid["n_traces"])


def _label(c):
    return "no fused" if c is None else f"c_F={c:g}"


def summarize(results):
    def above(r, g):
        return r["gaps"][g]["ci"][0] > 0
    out = {"configs": len(results)}
    for c in sorted({r["fused_cost"] for r in results}, key=lambda x: -1 if x is None else x):
        sub = [r for r in results if r["fused_cost"] == c]
        out[_label(c)] = {
            "n": len(sub),
            "gap_pure_ci_above_0": sum(above(r, "gap_pure") for r in sub),
            "gs_gap_pure_ci_above_0": sum(above(r, "gs_gap_pure") for r in sub),
            "gs_gap_pure_tiny_ci_above_0": sum(above(r, "gs_gap_pure_tiny_margin") for r in sub),
            "gs_gap_pure_tiny_ci_below_0": sum(r["gaps"]["gs_gap_pure_tiny_margin"]["ci"][1] < 0 for r in sub),
            "commitment_value_ci_above_0": sum(above(r, "commitment_value") for r in sub),
            "max_gap_pure": max(r["gaps"]["gap_pure"]["est"] for r in sub),
            "max_gs_gap_pure": max(r["gaps"]["gs_gap_pure"]["est"] for r in sub),
            "max_commitment_value": max(r["gaps"]["commitment_value"]["est"] for r in sub),
            "mean_fused_share": float(np.mean([r["losses"]["fused_share"] for r in sub])),
        }
    return out


def write_tables(p, path):
    def ci(g):
        return f"{g['est']:.4f} [{g['ci'][0]:.4f}, {g['ci'][1]:.4f}]"
    L = ["# Extension study: generated tables", "",
         f"Seed {p['seed']}, simulator {p['simulator_version']}, {len(p['results'])} configs, runtime "
         f"{p['runtime_s']:.0f} s, B = {p['config']['n_boot']}, general-sum margin {GS_MARGIN} bits "
         f"(tiny-margin variant {GS_MARGIN_TINY}). Cross-fitted estimates with 95% session-bootstrap CIs. "
         "Regenerate with `python -m src.run_extensions`.", "", "## Summary by fused-observer cost", "",
         "| Fused cost | n | gap_pure > 0 | GS gap_pure > 0 | GS tiny-margin > 0 / < 0 | commitment value > 0 | "
         "max gap_pure | max GS gap_pure | max commitment value | mean fused share |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for k, v in p["summary"].items():
        if k == "configs":
            continue
        L.append(f"| {k} | {v['n']} | {v['gap_pure_ci_above_0']} | {v['gs_gap_pure_ci_above_0']} | "
                 f"{v['gs_gap_pure_tiny_ci_above_0']} / {v['gs_gap_pure_tiny_ci_below_0']} | "
                 f"{v['commitment_value_ci_above_0']} | {v['max_gap_pure']:.4f} | {v['max_gs_gap_pure']:.4f} | "
                 f"{v['max_commitment_value']:.4f} | {v['mean_fused_share']:.2f} |")
    L += ["", "## All configs", "",
          "| A | s | k | types | fused | gap_pure | GS gap_pure | GS tiny margin | commitment value | fused share |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for r in p["results"]:
        g = r["gaps"]
        L.append(f"| {r['A']} | {r['s']} | {r['k']} | {r['types']} | {_label(r['fused_cost'])} | "
                 f"{ci(g['gap_pure'])} | {ci(g['gs_gap_pure'])} | {ci(g['gs_gap_pure_tiny_margin'])} | "
                 f"{ci(g['commitment_value'])} | {r['losses']['fused_share']:.2f} |")
    L += ["", "## Diagnostics", "", "| A | s | fused minus best-band MI, mean / min (bits) | runtime (s) |",
          "|---|---|---|---|"]
    for d in p["diagnostics"]:
        L.append(f"| {d['A']} | {d['s']} | {d['fused_minus_best_band_mi_mean']:.4f} / "
                 f"{d['fused_minus_best_band_mi_min']:.4f} | {d['runtime_s']:.0f} |")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(L) + "\n")


def make_figures(p, out):
    out.mkdir(parents=True, exist_ok=True)
    res = p["results"]
    fused = list(p["config"]["fused"])
    xs = np.arange(len(fused))
    s_max = max(r["s"] for r in res)
    k_mid = sorted({r["k"] for r in res})[len({r["k"] for r in res}) // 2]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=False)
    for ax, gap, title in ((axes[0], "gap_pure", "Zero-sum value of mixing"),
                           (axes[1], "gs_gap_pure", "General-sum value of mixing")):
        for A in sorted({r["A"] for r in res}):
            pts = [next((r for r in res if r["A"] == A and r["s"] == s_max and r["k"] == k_mid
                         and r["types"] == "1 type" and r["fused_cost"] == c), None) for c in fused]
            if any(x is None for x in pts):
                continue
            y = np.array([x["gaps"][gap]["est"] for x in pts])
            ci = np.array([x["gaps"][gap]["ci"] for x in pts])
            ax.errorbar(xs, y, yerr=[np.maximum(y - ci[:, 0], 0), np.maximum(ci[:, 1] - y, 0)],
                        marker="o", capsize=3, label=f"A = {A:g}")
        ax.axhline(0, color="k", lw=0.8)
        ax.set_xticks(xs, [_label(c) for c in fused])
        ax.set_xlabel("fused (hears-everything) observer available, at cost c_F")
        ax.set_ylabel("loss saved by mixing (bits per trace)")
        ax.set_title(title)
        ax.grid(alpha=0.3)
        ax.legend(frameon=False)
    fig.suptitle(f"A cheap fused observer erases the value of mixing (s = {s_max:g}, k = {k_mid:g}, one adaptive type)")
    fig.tight_layout()
    fig.savefig(out / "fig_E1_fused_observer.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.2))
    for c, mk in zip(fused, "osD^v"):
        sub = [r for r in res if r["fused_cost"] == c]
        x = [r["gaps"]["gap_pure"]["est"] for r in sub]
        y = [r["gaps"]["commitment_value"]["est"] for r in sub]
        ax.scatter(x, y, s=14, marker=mk, alpha=0.7, label=_label(c))
    ax.axhline(0, color="k", lw=0.8)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_xlabel("zero-sum value of mixing (gap_pure)")
    ax.set_ylabel("general-sum commitment value")
    ax.set_title("Does a general-sum commitment beat the zero-sum policy? (all configs)")
    ax.grid(alpha=0.3)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(out / "fig_E2_general_sum.png", dpi=150)
    plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, default=126)
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--n-boot", type=int, default=None)
    ap.add_argument("--output", default=None)
    args = ap.parse_args(argv)
    grid = dict(QUICK if args.quick else FULL)
    if args.n_boot:
        grid["n_boot"] = args.n_boot
    base = Path("results/quick" if args.quick else "results")
    out_json = Path(args.output or base / "extensions.json")
    t0 = time.time()
    tasks = [(args.seed, iA, iS, A, s, grid) for iA, A in enumerate(grid["A"]) for iS, s in enumerate(grid["s"])]
    outs = []
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for i, o in enumerate(ex.map(_task, tasks)):
            outs.append(o)
            d = o["diagnostics"]
            print(f"[{i + 1}/{len(tasks)}] A={d['A']} s={d['s']} {d['runtime_s']:.0f}s", flush=True)
    results = [r for o in outs for r in o["results"]]
    payload = {"simulator_version": __version__, "seed": args.seed,
               "seed_streams": "SeedSequence(seed, spawn_key=(2000, i_A, i_s))",
               "config": {**grid, "gs_margin": GS_MARGIN, "gs_margin_tiny": GS_MARGIN_TINY,
                          "metrics": {k: list(v) for k, v in METRICS.items()}},
               "environment": environment_record(), "runtime_s": time.time() - t0,
               "summary": summarize(results), "results": results,
               "diagnostics": [o["diagnostics"] for o in outs]}
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=1, default=float))
    write_tables(payload, out_json.parent / "extensions_tables.md")
    make_figures(payload, out_json.parent / "figures")
    print(f"done in {payload['runtime_s']:.0f}s; wrote {out_json}")
    for k, v in payload["summary"].items():
        print(k, v)


if __name__ == "__main__":
    main()
