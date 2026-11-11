"""Value of the game (claim C8): cross-fitted policy evaluation with a session bootstrap.

For one simulated (A, s) dataset and a list of configs (price multiplier k and
observer type model), this module computes, per config:

* cross-fitted losses of every method against the adaptive observer B5,
  where policies are fit on one half of the sessions and scored on the other;
* percentile and bias-corrected session-bootstrap CIs (sessions resampled
  within halves, everything refit);
* in-sample estimates (optimistic for the game, reported for comparison);
* exact-model gaps from quadrature MI of the same library (binned and
  continuous), and fine-library gaps with a 36,402-row deterministic library.

Gaps (all in loss units, bits per trace plus priced overhead):
    gap_pure      = L(best pure)      - L(game)
    gap_robust    = L(B4)             - L(game)
    gap_baselines = L(best of B1..B4) - L(game)
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np
from scipy import stats

from .band_channel import OBS_COST, coarse_library, fine_mi_matrix, simulate_dataset
from .baselines import METHODS, TYPE_MODELS, fit_policies, pure_scores, score
from .games import solve_bayesian

LAMBDA_E, LAMBDA_L = 0.30, 0.20
GAPS = {"gap_pure": "best_pure", "gap_robust": "B4", "gap_baselines": "best_baseline"}
SUPPORT_TOL = 1e-6


@dataclass(frozen=True)
class Config:
    k: float
    types: str

    def type_model(self):
        return TYPE_MODELS[self.types]


def overhead(rows, k: float) -> np.ndarray:
    E = np.array([r.energy for r in rows])
    T = np.array([r.latency for r in rows])
    return k * (LAMBDA_E * E + LAMBDA_L * T)


def loss_matrix(MI: np.ndarray, oh: np.ndarray) -> np.ndarray:
    return MI + oh[:, None] - OBS_COST[None, :]


def _evaluate(fits, M, MI, types, energy) -> dict:
    out = {}
    for m in METHODS:
        p = fits[m][0]
        loss, leak = score(p, M, MI, types)
        out[m] = (loss, leak, float(p @ energy))
    return out


def crossfit(MI_a, MI_b, rows, cfg: Config, rho: float, energy):
    """Fit on half a, score on half b, and vice versa; return the average and the fits."""
    types = cfg.type_model()
    oh = overhead(rows, cfg.k)
    Ma, Mb = loss_matrix(MI_a, oh), loss_matrix(MI_b, oh)
    fa = fit_policies(Ma, MI_a, types, rows, rho)
    fb = fit_policies(Mb, MI_b, types, rows, rho)
    ea = _evaluate(fa, Mb, MI_b, types, energy)
    eb = _evaluate(fb, Ma, MI_a, types, energy)
    avg = {m: tuple(0.5 * (x + y) for x, y in zip(ea[m], eb[m])) for m in METHODS}
    return avg, (fa, fb)


def _gaps(res: dict) -> dict:
    return {g: res[m][0] - res["game"][0] for g, m in GAPS.items()}


def _ci(est: float, boot: np.ndarray, level: float = 0.95):
    a = (1 - level) / 2
    pct = np.quantile(boot, [a, 1 - a])
    # Bias-corrected percentile (sensitivity check).
    frac = np.clip(np.mean(boot < est) + 0.5 * np.mean(boot == est), 1e-6, 1 - 1e-6)
    z0 = stats.norm.ppf(frac)
    zq = stats.norm.ppf([a, 1 - a])
    bc = np.quantile(boot, stats.norm.cdf(2 * z0 + zq))
    return [float(pct[0]), float(pct[1])], [float(bc[0]), float(bc[1])], float(boot.std(ddof=1))


def analyze_dataset(A: float, s: float, seed_seq: np.random.SeedSequence, configs: list[Config],
                    n_boot: int = 1000, rho: float = 0.5, n_sessions: int = 128, n_traces: int = 1000,
                    fine: bool = True, fine_kwargs: dict | None = None) -> dict:
    """Simulate the four-band dataset at (A, s) and analyze every config on it."""
    t0 = time.time()
    rows = coarse_library()
    sim_ss, split_ss, boot_ss = seed_seq.spawn(3)
    ds = simulate_dataset(A, s, sim_ss, rows, n_sessions=n_sessions, n_traces=n_traces)
    MI_exact = ds.exact_mi_matrix("binned")
    MI_cont = ds.exact_mi_matrix("continuous")
    fine_data = fine_mi_matrix(A, s, **(fine_kwargs or {})) if fine else None
    out = analyze(ds, rows, configs, split_ss, boot_ss, n_boot, rho, MI_exact, MI_cont, fine_data)
    MI_full = np.asarray(out["matrices"]["mi_full"])
    out["diagnostics"] = {
        "A": A, "s": s,
        "mc_minus_exact_binned_mean": float((MI_full - MI_exact).mean()),
        "mc_minus_exact_binned_worst": float(np.abs(MI_full - MI_exact).max()),
        "binning_loss_max": float((MI_cont - MI_exact).max()),
        "n_rows": len(rows), "n_sessions": ds.n_sessions, "n_traces_per_session": n_traces,
        "runtime_s": time.time() - t0,
    }
    out["matrices"]["mi_exact_binned"] = MI_exact.tolist()
    return out


def analyze(ds, rows, configs, split_ss, boot_ss, n_boot, rho,
            MI_exact=None, MI_cont=None, fine_data=None) -> dict:
    """Cross-fit, bootstrap, and (when exact matrices are given) exact checks for one dataset.

    ``ds`` needs ``n_sessions`` and ``mi_matrix(sessions=None)``.
    """
    energy = np.array([r.energy for r in rows])
    names = [r.name for r in rows]
    G = ds.n_sessions
    perm = np.random.default_rng(split_ss).permutation(G)
    h1, h2 = np.sort(perm[: G // 2]), np.sort(perm[G // 2:])
    MI_full = ds.mi_matrix()
    MI_1, MI_2 = ds.mi_matrix(h1), ds.mi_matrix(h2)

    # Point estimates.
    point = {}
    for cfg in configs:
        avg, (fa, fb) = crossfit(MI_1, MI_2, rows, cfg, rho, energy)
        point[cfg] = {"crossfit": avg, "fits": (fa, fb)}

    # Session bootstrap within halves.
    rng = np.random.default_rng(boot_ss)
    boot = {cfg: {"loss": np.zeros((n_boot, len(METHODS))), "leak": np.zeros((n_boot, len(METHODS))),
                  "support": np.zeros(len(rows))} for cfg in configs}
    for bi in range(n_boot):
        s1 = rng.choice(h1, size=len(h1), replace=True)
        s2 = rng.choice(h2, size=len(h2), replace=True)
        mi1, mi2 = ds.mi_matrix(s1), ds.mi_matrix(s2)
        for cfg in configs:
            avg, (fa, fb) = crossfit(mi1, mi2, rows, cfg, rho, energy)
            b = boot[cfg]
            b["loss"][bi] = [avg[m][0] for m in METHODS]
            b["leak"][bi] = [avg[m][1] for m in METHODS]
            b["support"] += (fa["game"][0] > SUPPORT_TOL).astype(float) + (fb["game"][0] > SUPPORT_TOL)

    results = []
    for cfg in configs:
        types = cfg.type_model()
        prior = np.array([w for *_, w in types])
        oh = overhead(rows, cfg.k)
        cf = point[cfg]["crossfit"]
        b = boot[cfg]
        gaps_est = _gaps(cf)
        gidx = {m: METHODS.index(m) for m in METHODS}
        gaps = {}
        for g, m in GAPS.items():
            bvals = b["loss"][:, gidx[m]] - b["loss"][:, gidx["game"]]
            pct, bc, se = _ci(gaps_est[g], bvals)
            gaps[g] = {"est": gaps_est[g], "ci": pct, "ci_bc": bc, "se": se}
        methods = {}
        for m in METHODS:
            lp, _, lse = _ci(cf[m][0], b["loss"][:, gidx[m]])
            kp, _, _ = _ci(cf[m][1], b["leak"][:, gidx[m]])
            methods[m] = {"loss": cf[m][0], "loss_ci": lp, "leak": cf[m][1], "leak_ci": kp, "energy": cf[m][2]}

        # In-sample (full data) fit and evaluation.
        M_full = loss_matrix(MI_full, oh)
        f_full = fit_policies(M_full, MI_full, types, rows, rho)
        ins = _evaluate(f_full, M_full, MI_full, types, energy)
        ex = cont = None
        fine_res = None
        if MI_exact is not None:
            # Exact held-out: full-data policies scored on the exact binned model.
            M_ex = loss_matrix(MI_exact, oh)
            held = _evaluate(f_full, M_ex, MI_exact, types, energy)
            for m in METHODS:
                methods[m]["exact_heldout_loss"] = held[m][0]
            # Exact population gaps: fit and score on the exact binned model.
            ex = _evaluate(fit_policies(M_ex, MI_exact, types, rows, rho), M_ex, MI_exact, types, energy)
        if MI_cont is not None:
            M_c = loss_matrix(MI_cont, oh)
            cont = _evaluate(fit_policies(M_c, MI_cont, types, rows, rho), M_c, MI_cont, types, energy)
        if fine_data is not None and cont is not None:
            mi_f, e_f, t_f = fine_data
            M_f = mi_f + (cfg.k * (LAMBDA_E * e_f + LAMBDA_L * t_f))[:, None] - OBS_COST[None, :]
            L_game_c = cont["game"][0]
            bp = float(pure_scores(M_f, types).min())
            nom = sum(w * M_f[:, list(a)].mean(axis=1) for _, a, w in types)
            r4 = int(np.argmin(nom))
            L_b4 = float(pure_scores(M_f[[r4]], types)[0])
            fine_res = {"gap_pure": bp - L_game_c, "gap_robust": L_b4 - L_game_c, "n_rows": int(len(M_f))}

        p_full = f_full["game"][0]
        sol_full = solve_bayesian([M_full[:, list(a)] for _, a, _ in types], prior)
        results.append({
            "A": getattr(ds, "A", None), "s": getattr(ds, "s", None), "k": cfg.k, "types": cfg.types,
            "lambda_E": cfg.k * LAMBDA_E, "lambda_L": cfg.k * LAMBDA_L,
            "gaps": gaps,
            "gaps_in_sample": _gaps(ins),
            "gaps_exact": _gaps(ex) if ex else None,
            "gaps_exact_continuous": _gaps(cont) if cont else None,
            "gaps_fine": fine_res,
            "methods": methods,
            "game_policy": {names[i]: float(p_full[i]) for i in np.flatnonzero(p_full > SUPPORT_TOL)},
            "observer_mixtures": {t[0]: q.tolist() for t, q in zip(types, sol_full.q_type)},
            "chosen_rows": {m: names[f_full[m][1]] for m in METHODS if f_full[m][1] is not None},
            "support_stability": {names[i]: float(v / (2 * n_boot))
                                  for i, v in enumerate(b["support"]) if v > 0},
        })

    return {"results": results, "matrices": {"mi_full": MI_full.tolist()}}


def frontier(A: float, s: float, seed_seq: np.random.SeedSequence, ks, n_boot: int = 200,
             rho: float = 0.5, n_sessions: int = 128, n_traces: int = 1000) -> list[dict]:
    """Leakage vs energy of the game and the best pure defense, one adaptive type, price swept."""
    out = analyze_dataset(A, s, seed_seq, [Config(k, "1 type") for k in ks], n_boot=n_boot, rho=rho,
                          n_sessions=n_sessions, n_traces=n_traces, fine=False)
    pts = []
    for r in out["results"]:
        pts.append({"k": r["k"], **{m: {kk: r["methods"][m][kk] for kk in ("leak", "leak_ci", "energy", "loss")}
                                    for m in ("game", "best_pure")}})
    return pts


# ---------------------------------------------------------------------------
# Scaffold check: the original 4 x 4 scalar model through the same pipeline
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class _ScaffoldRow:
    name: str
    hop: bool
    power: float
    energy: float
    latency: float


class ScaffoldDataset:
    """Per-session count tables for the scalar D0-D3 x A0-A3 model."""

    def __init__(self, seed_seq, n_sessions=128, n_traces=1000, n_bins=16, cal_traces=4000, amplitude=1.0):
        from .channel import DEFENDER_ACTIONS, OBSERVER_ACTIONS, simulate_traces
        from .metrics import counts_table, quantile_edges
        D, Aa = len(DEFENDER_ACTIONS), len(OBSERVER_ACTIONS)
        self.counts = np.zeros((D, Aa, n_sessions, 2, n_bins), dtype=np.int32)
        for i, d in enumerate(DEFENDER_ACTIONS):
            for j in range(Aa):
                cal, *sess = np.random.SeedSequence(seed_seq.entropy, spawn_key=tuple(seed_seq.spawn_key) + (i, j)).spawn(n_sessions + 1)
                _, zc = simulate_traces(np.random.default_rng(cal), d, j, cal_traces, amplitude)
                e = quantile_edges(zc, n_bins)
                for g, ss in enumerate(sess):
                    sv, z = simulate_traces(np.random.default_rng(ss), d, j, n_traces, amplitude)
                    self.counts[i, j, g] = counts_table(sv, z, e)
        self.rows = [_ScaffoldRow(d.name, any(h > 0 for h in d.hop_out), float(sum(d.inject_var) > 0),
                                  d.energy, d.latency) for d in DEFENDER_ACTIONS]

    @property
    def n_sessions(self):
        return self.counts.shape[2]

    def mi_matrix(self, sessions=None):
        from .metrics import mi_from_counts
        c = self.counts if sessions is None else self.counts[:, :, sessions]
        return mi_from_counts(c.sum(axis=2))


def analyze_scaffold(seed_seq, k=1.0, n_boot=1000, rho=0.5, n_sessions=128, n_traces=1000) -> dict:
    ds = ScaffoldDataset(seed_seq, n_sessions=n_sessions, n_traces=n_traces)
    split_ss, boot_ss = np.random.SeedSequence(seed_seq.entropy, spawn_key=tuple(seed_seq.spawn_key) + (99,)).spawn(2)
    out = analyze(ds, ds.rows, [Config(k, "1 type")], split_ss, boot_ss, n_boot, rho)
    return out["results"][0]
