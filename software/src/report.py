"""Figures for one ``ascam evaluate`` results JSON.

Every figure is drawn from the results JSON only, never from traces. Sweep
results of ``python -m src.run_sweep`` are drawn by ``python -m src.figures``.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

METHOD_STYLE = {
    "game": ("Game: committed mixed policy", "tab:blue", "o"),
    "best_pure": ("Best single defense vs B5", "tab:orange", "s"),
    "B4": ("B4 non-strategic (uniform observer)", "tab:green", "^"),
    "B4_robust": ("B4 robust counterpart", "tab:olive", "v"),
    "B3": ("B3 best noise-only defense vs frozen observer", "tab:red", "D"),
    "B2": ("B2 random frequency (D2)", "tab:purple", "P"),
    "B1": ("B1 fixed dummy (D1)", "tab:brown", "X"),
    "B0": ("B0 no defense (D0)", "black", "*"),
}


def _wrap(*paragraphs: str, width: int = 125) -> str:
    return "\n".join(textwrap.fill(p, width) for p in paragraphs)


def _caption(results: dict) -> str:
    data, estimator = results["data"], results["estimator"]
    actions, interval = results["actions"], results["interval_method"]
    return _wrap(f"N = {results['N']} train traces, G = {results['G']} sessions; {data['dut']} "
                 f"({data['abstraction']}), {len(actions['defender'])} defenses x "
                 f"{len(actions['observer'])} observer actions; estimator: {estimator['name']}, "
                 f"{estimator['bins']} bins; intervals: {interval['name']}, "
                 f"B = {interval['bootstrap']}.", results["caveat"])


def _interval_errors(estimate, low, high) -> np.ndarray:
    estimate, low, high = (np.atleast_1d(np.asarray(v, dtype=float)) for v in (estimate, low, high))
    return np.vstack((np.clip(estimate - low, 0.0, None), np.clip(high - estimate, 0.0, None)))


def _chosen_rows(results: dict) -> dict:
    return results.get("value_of_game", {}).get("chosen_rows", {})


def _shown_rows(results: dict, limit: int = 12) -> list[int]:
    """All rows for small libraries; otherwise support, D0 to D3, and chosen baselines."""
    names = results["payoff"]["rows"]
    if len(names) <= limit:
        return list(range(len(names)))
    eq = results["equilibrium"]
    keep = {i for i, r in enumerate(eq["defender_policy"])
            if r["p"] > eq["support_tolerance"] or r["support_stability"] >= 0.05}
    keep |= {i for i, name in enumerate(names) if name.startswith(("D0", "D1", "D2", "D3"))}
    keep |= {names.index(name) for name in _chosen_rows(results).values() if name in names}
    return sorted(keep)


def _row_labels(results: dict, rows: list[int]) -> list[str]:
    """Row names tagged with the baselines and methods that chose them."""
    names = results["payoff"]["rows"]
    tags: dict[str, list[str]] = {}
    for method, name in _chosen_rows(results).items():
        if method != "best_baseline":
            tags.setdefault(name, []).append(method.replace("_", " "))
    for name in names:
        tag = f"B{name[1]}" if name.startswith(("D0", "D1", "D2")) else None
        if tag and tag not in tags.get(name, []):
            tags.setdefault(name, []).append(tag)
    return [f"{names[i]} [{', '.join(tags[names[i]])}]" if names[i] in tags else names[i]
            for i in rows]


def figure_payoff_equilibrium(results: dict, path: Path) -> None:
    """Payoff matrix (loss +/- bootstrap SE) with p* and q* on the full train split."""
    payoff, eq, config = results["payoff"], results["equilibrium"], results["config"]
    names, policy = payoff["rows"], eq["defender_policy"]
    first_type = eq["type_model"]["types"][0]
    columns = [payoff["columns"].index(action) for action in first_type["actions"]]
    rows = _shown_rows(results)
    labels = _row_labels(results, rows)
    loss = np.asarray(payoff["matrix"])[np.ix_(rows, columns)]
    se = np.asarray(payoff["se"])[np.ix_(rows, columns)]
    p = [policy[i]["p"] for i in rows]
    stability = [policy[i]["support_stability"] for i in rows]
    q = list(eq["observer_policies"][0]["policy"].values())
    title = _wrap(
        f"ascam evaluate: payoff matrix and equilibrium, observer types: "
        f"{eq['type_model']['name']}, lambda_E = {config['lambda_energy']:.2f}, "
        f"lambda_L = {config['lambda_latency']:.2f}, {len(rows)} of {len(names)} defenses shown.",
        "Cell: loss (bits + priced overhead - observer cost) +/- session-bootstrap SE; bars: "
        "p* and q* on the full train split; support % over bootstrap refits.",
        width=110) + "\n" + _caption(results)

    height = max(0.42 * len(labels) + 3.2 + 0.16 * title.count("\n"), 7.0)
    fig = plt.figure(figsize=(11, height), constrained_layout=True)
    grid = fig.add_gridspec(2, 2, width_ratios=(4, 1.5), height_ratios=(1, 0.33 * len(labels)))
    ax = fig.add_subplot(grid[1, 0])
    top = fig.add_subplot(grid[0, 0], sharex=ax)
    side = fig.add_subplot(grid[1, 1], sharey=ax)
    image = ax.imshow(loss, cmap="viridis", aspect="auto")
    for (i, j), v in np.ndenumerate(loss):
        ax.text(j, i, f"{v:.3f}\n+/-{se[i, j]:.3f}", ha="center", va="center",
                fontsize=6.5, color="white" if v < loss.mean() else "black")
    ax.set_xticks(range(loss.shape[1]), first_type["actions"], fontsize=8)
    ax.set_yticks(range(len(labels)), labels, fontsize=7)
    ax.set_xlabel("Observer action (band / filter)")
    fig.colorbar(image, ax=ax, location="left", shrink=0.7,
                 label="Defender loss M[d, a] (bits + priced overhead)")
    top.bar(range(len(q)), q, color="tab:gray")
    top.set_ylabel("q* (observer)")
    top.set_ylim(0, 1)
    top.tick_params(labelbottom=False)
    side.barh(range(len(p)), p, color="tab:blue")
    for i, (pi, st) in enumerate(zip(p, stability)):
        side.text(min(pi + 0.02, 0.75), i, f"p={pi:.2f}, in support {100 * st:.0f}%",
                  va="center", fontsize=6.5)
    side.set_xlim(0, 1)
    side.set_xlabel("p* (defender equilibrium)")
    side.tick_params(labelleft=False)
    fig.suptitle(title, fontsize=9)
    fig.savefig(path, dpi=150)
    plt.close(fig)


def figure_equilibrium_uncertainty(results: dict, path: Path) -> None:
    """Bootstrap distribution of the game value and the stability of p*."""
    eq = results["equilibrium"]
    replicates = np.asarray(eq["value_replicates"], dtype=float)
    rows = [eq["defender_policy"][i] for i in _shown_rows(results)]
    fig, (left, right) = plt.subplots(1, 2, figsize=(12.5, 0.32 * len(rows) + 4.2),
                                      constrained_layout=True)
    left.hist(replicates, bins=int(np.clip(len(replicates) // 10, 10, 40)), color="tab:blue",
              alpha=0.7, label="bootstrap replicates")
    low, high = eq["value_ci"]
    left.axvspan(low, high, color="tab:orange", alpha=0.2,
                 label=f"95% percentile CI [{low:.4f}, {high:.4f}]")
    left.axvline(eq["value"], color="black", label=f"full-data value {eq['value']:.4f}")
    left.set_xlabel("Equilibrium value v (bits + priced overhead - observer cost)")
    left.set_ylabel("Replicates")
    left.legend(fontsize=8)
    left.grid(alpha=0.3)
    p = np.array([r["p"] for r in rows])
    low_p, high_p = np.array([r["ci"] for r in rows]).T
    positions = np.arange(len(rows))
    right.barh(positions, p, xerr=_interval_errors(p, low_p, high_p), color="tab:blue",
               capsize=3)
    for i, record in enumerate(rows):
        right.text(1.04, i, f"in support {100 * record['support_stability']:.0f}%",
                   va="center", fontsize=7)
    right.set_yticks(positions, [r["action"] for r in rows], fontsize=7)
    right.invert_yaxis()
    right.set_xlim(0, 1.4)
    right.set_xticks(np.linspace(0.0, 1.0, 6))
    right.set_xlabel("p* (bar: full train split; whisker: 95% bootstrap interval)")
    right.grid(alpha=0.3, axis="x")
    fig.suptitle(_wrap(
        f"Equilibrium uncertainty (observer types: {eq['type_model']['name']}), duality gap "
        f"{eq['duality_gap']:.1e}, solver {eq['solver']['status']}; stable support "
        f"(>= 95% of replicates): {', '.join(eq['stable_support']) or 'none'}")
        + "\n" + _caption(results), fontsize=9)
    fig.savefig(path, dpi=150)
    plt.close(fig)


def figure_value_of_game(results: dict, path: Path) -> None:
    """Cross-fitted loss of the game and baselines against B5, with the two gaps."""
    vog = results["value_of_game"]
    methods = list(METHOD_STYLE)
    fig, (left, right) = plt.subplots(1, 2, figsize=(13, 4.8), constrained_layout=True,
                                      gridspec_kw={"width_ratios": (1.8, 1.0)})
    for i, method in enumerate(methods):
        _, color, marker = METHOD_STYLE[method]
        record = vog["methods"][method]
        left.errorbar(record["loss"], i, xerr=_interval_errors(record["loss"], *record["loss_ci"]),
                      color=color, marker=marker, capsize=3, linestyle="none", markersize=7)
    labels = [METHOD_STYLE[m][0] for m in methods]
    labels[methods.index("B4_robust")] = (
        f"B4 robust counterpart (rho = {results['config']['robust_rho']:g})")
    left.set_yticks(range(len(methods)), labels, fontsize=8)
    left.invert_yaxis()
    left.set_xlabel("Cross-fitted loss vs adaptive observer B5 (bits + priced overhead)")
    left.grid(alpha=0.3, axis="x")
    gaps = ("gap_pure", "gap_robust")
    for i, gap in enumerate(gaps):
        record = vog["gaps"][gap]
        right.errorbar(record["est"], i, xerr=_interval_errors(record["est"], *record["ci"]),
                       color="tab:blue", marker="o", capsize=3, linestyle="none")
    right.axvline(0.0, color="gray", linewidth=0.8)
    right.set_yticks(range(len(gaps)), ["gap_pure = L(best pure) - L(game)",
                                         "gap_robust = L(B4) - L(game)"], fontsize=8)
    right.set_ylim(len(gaps) - 0.5, -0.5)
    right.set_xlabel("Gap (positive favors the game)")
    right.grid(alpha=0.3, axis="x")
    verdict = "yes" if vog["game_strictly_helps"] else "no"
    fig.suptitle(_wrap(
        "Value of the game on held-out sessions (cross-fitted halves, 95% session-bootstrap "
        f"CIs). Game strictly helps (both gap CIs above 0): {verdict}")
        + "\n" + _caption(results), fontsize=9)
    fig.savefig(path, dpi=150)
    plt.close(fig)


def make_evaluation_figures(results: dict, directory: Path) -> list[Path]:
    """Figures for one ascam evaluate results JSON; returns the written paths."""
    directory.mkdir(parents=True, exist_ok=True)
    jobs = [("payoff_equilibrium.png", figure_payoff_equilibrium),
            ("equilibrium_uncertainty.png", figure_equilibrium_uncertainty)]
    if "gaps" in results.get("value_of_game", {}):
        jobs.append(("value_of_game.png", figure_value_of_game))
    paths = []
    for name, function in jobs:
        path = directory / name
        function(results, path)
        paths.append(path)
    return paths
