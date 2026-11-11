"""Figures regenerated from the sweep results JSON only (never hand-edited).

    python -m src.figures --results results/value_of_game.json --figures results/figures
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from .band_channel import OBS_COST, coarse_library  # noqa: E402
from .channel import OBSERVER_ACTIONS  # noqa: E402

GAME_C, PURE_C = "#3b6fb6", "#d1823a"


def fig_frontier(p, out):
    fr = p["frontier"]
    fig, axes = plt.subplots(1, len(fr), figsize=(5.2 * len(fr), 4.2), squeeze=False)
    for ax, f in zip(axes[0], fr):
        for m, c, lab in (("game", GAME_C, "game (mixed)"), ("best_pure", PURE_C, "best pure")):
            e = np.array([pt[m]["energy"] for pt in f["points"]])
            y = np.array([pt[m]["leak"] for pt in f["points"]])
            ci = np.array([pt[m]["leak_ci"] for pt in f["points"]])
            o = np.argsort(e)
            ax.fill_between(e[o], ci[o, 0], ci[o, 1], color=c, alpha=0.15, lw=0)
            ax.errorbar(e, y, yerr=[np.maximum(y - ci[:, 0], 0), np.maximum(ci[:, 1] - y, 0)], fmt="o", ms=4, color=c, capsize=2, label=lab)
            ax.plot(e[o], y[o], color=c, lw=1)
        ax.set_title(f"A = {f['A']}, s = {f['s']}, one adaptive type")
        ax.set_xlabel("normalized energy E")
        ax.set_ylabel("leakage vs B5 (bits per trace)")
        ax.grid(alpha=0.3)
        ax.legend(frameon=False)
    fig.suptitle("Leakage vs energy as the price multiplier sweeps (cross-fitted, 95% CI)")
    fig.tight_layout()
    fig.savefig(out / "fig_A_frontier.png", dpi=150)
    plt.close(fig)


def fig_heatmap(p, out, gap, fname):
    res = p["results"]
    A = sorted({r["A"] for r in res})
    S = sorted({r["s"] for r in res})
    K = sorted({r["k"] for r in res})
    T = list(dict.fromkeys(r["types"] for r in res))
    vals = np.array([r["gaps"][gap]["est"] for r in res])
    vmax = max(abs(vals).max(), 1e-9)
    fig, axes = plt.subplots(len(K), len(S), figsize=(2.6 * len(S), 2.3 * len(K)), squeeze=False,
                             sharex=True, sharey=True)
    for i, k in enumerate(K):
        for j, s in enumerate(S):
            ax = axes[i, j]
            Z = np.full((len(T), len(A)), np.nan)
            for r in res:
                if r["k"] == k and r["s"] == s:
                    a, t = A.index(r["A"]), T.index(r["types"])
                    Z[t, a] = r["gaps"][gap]["est"]
                    mark = "**" if r["flags"]["both_bonferroni"] else ("*" if r["flags"]["both"] else "")
                    if mark:
                        ax.text(a, t, mark, ha="center", va="center", fontsize=9)
            im = ax.imshow(Z, cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
            if i == 0:
                ax.set_title(f"s = {s}", fontsize=9)
            if j == 0:
                ax.set_ylabel(f"k = {k}", fontsize=9)
                ax.set_yticks(range(len(T)), [t.replace(" (adaptive ", "\n(ad. ") for t in T], fontsize=6)
            ax.set_xticks(range(len(A)), [f"{a:g}" for a in A], fontsize=7)
    fig.colorbar(im, ax=axes, shrink=0.6, label=f"cross-fitted {gap}")
    fig.supxlabel("LNR A")
    fig.suptitle(f"{gap} over A x observer types, faceted by s (columns) and k (rows). * decision rule, ** Bonferroni")
    fig.savefig(out / fname, dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_payoff(p, out, n_rows=8):
    rep = p["representative"]
    res = rep["result"]
    names = rep["rows"]
    rows = coarse_library()
    mi = np.array(rep["mi_full"])
    E = np.array([r.energy for r in rows])
    T = np.array([r.latency for r in rows])
    M = mi + (res["k"] * (0.3 * E + 0.2 * T))[:, None] - OBS_COST[None, :]
    sel = list(dict.fromkeys(list(res["game_policy"]) + [res["chosen_rows"][m] for m in ("best_pure", "B3", "B4")]
                             + names[:4]))[:n_rows]
    idx = [names.index(n) for n in sel]
    pst = [res["game_policy"].get(n, 0.0) for n in sel]
    stab = [res["support_stability"].get(n, 0.0) for n in sel]
    q = res["observer_mixtures"].get("adaptive", [np.nan] * 4)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(10, 4.6), gridspec_kw={"width_ratios": [3, 1.4]})
    im = ax.imshow(M[idx], cmap="viridis", aspect="auto")
    for i in range(len(idx)):
        for j in range(4):
            ax.text(j, i, f"{M[idx[i], j]:.3f}", ha="center", va="center", color="w", fontsize=8)
    ax.set_yticks(range(len(sel)), [f"{n}  p*={pp:.2f}" for n, pp in zip(sel, pst)], fontsize=8)
    ax.set_xticks(range(4), [f"{a.name.split('-')[0]}\nq*={qq:.2f}" for a, qq in zip(OBSERVER_ACTIONS, q)], fontsize=8)
    fig.colorbar(im, ax=ax, label="loss (bits + priced overhead)")
    ax.set_title(f"Payoff at A={res['A']}, s={res['s']}, k={res['k']} ({len(sel)} of {len(names)} rows)")
    ax2.barh(range(len(sel)), stab, color=GAME_C)
    ax2.set_yticks(range(len(sel)), [""] * len(sel))
    ax2.invert_yaxis()
    ax.set_ylim(len(sel) - 0.5, -0.5)
    ax2.set_xlim(0, 1)
    ax2.set_xlabel("cross-fitted support stability")
    fig.tight_layout()
    fig.savefig(out / "fig_C_payoff_equilibrium.png", dpi=150)
    plt.close(fig)


def fig_validation(p, out):
    res = p["results"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.4))
    for ax, gap in zip(axes, ("gap_pure", "gap_robust")):
        x = np.array([r["gaps_exact"][gap] for r in res])
        y = np.array([r["gaps"][gap]["est"] for r in res])
        yi = np.array([r["gaps_in_sample"][gap] for r in res])
        lo, hi = min(x.min(), y.min(), yi.min()), max(x.max(), y.max(), yi.max())
        ax.plot([lo, hi], [lo, hi], "k--", lw=0.8)
        ax.scatter(x, yi, s=8, color=PURE_C, alpha=0.6, label="in-sample")
        ax.scatter(x, y, s=8, color=GAME_C, alpha=0.7, label="cross-fitted")
        ax.set_xlabel(f"exact-model {gap}")
        ax.set_ylabel(f"estimated {gap}")
        ax.grid(alpha=0.3)
        ax.legend(frameon=False)
    fig.suptitle(f"Gap estimates vs the exact model, all {len(res)} grid points")
    fig.tight_layout()
    fig.savefig(out / "fig_D_validation.png", dpi=150)
    plt.close(fig)


def make_all(payload: dict, out_dir) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    fig_frontier(payload, out)
    fig_heatmap(payload, out, "gap_robust", "fig_B_gap_robust_heatmap.png")
    fig_heatmap(payload, out, "gap_pure", "fig_B_supp_gap_pure_heatmap.png")
    fig_payoff(payload, out)
    fig_validation(payload, out)


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results", default="results/value_of_game.json")
    ap.add_argument("--figures", default="results/figures")
    args = ap.parse_args(argv)
    make_all(json.loads(Path(args.results).read_text()), args.figures)
    print(f"wrote figures to {args.figures}")


if __name__ == "__main__":
    main()
