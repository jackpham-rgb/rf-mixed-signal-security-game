"""Two extensions of the value-of-game study.

1. Fused ("hears everything") observer. A fifth observer action that captures all
   four bands of the same trace and combines them with the sum of per-band
   log-likelihood ratios (optimal when bands are conditionally independent).
   It pays its own cost c_F. Theory (P1): if this action dominates, the observer
   effectively has one action and a pure defense is optimal.

2. General-sum game. The zero-sum loss M = MI + overhead - c_a lets the defender
   "gain" when the observer pays for an expensive band. In the general-sum model:

       defender loss     L[d, a] = MI[d, a] + overhead[d]
       observer utility  U[d, a] = MI[d, a] - c_a

   Each side counts only its own costs. The defender commits to a mixed policy p
   and each observer type best-responds by U. The strong Stackelberg policy is
   found by solving one LP per observer response profile (Conitzer and Sandholm
   2006), with a small margin so the induced response is strict.

Everything is synthetic. The fused statistic uses the deployed row's channel
parameters at median session factors, i.e. a calibrated observer.
"""

from __future__ import annotations

import itertools
import time
from dataclasses import dataclass

import numpy as np
from scipy import stats
from scipy.optimize import linprog

from .band_channel import (GAIN, HOP_COUPLING, N_BANDS, OBS_COST, SIGMA, SESSION_GAIN_SD, SESSION_NOISE_SD,
                           coarse_library, hop_out_prob, inject_var, simulate_dataset)
from .baselines import TYPE_MODELS, fit_policies, one_hot, score
from .metrics import counts_table, mi_from_counts, quantile_edges
from .value_of_game import _ci, overhead

FUSED = N_BANDS          # column index of the fused action
GS_MARGIN = 0.01         # bits: induced best responses must win by this much (robust)
GS_MARGIN_TINY = 1e-4    # bits: near-tie version, reported to show its fragility
TIE_TOL = 1e-12


# ---------------------------------------------------------------------------
# Fused observer simulation
# ---------------------------------------------------------------------------

def _llr(z, b, hop_q, var, A):
    """Per-band log-likelihood ratio log p(z | S=1) / p(z | S=0) at median session factors."""
    sd = np.sqrt(var + SIGMA[b] ** 2)
    m = GAIN[b] * A
    def mix(mu):
        a = stats.norm.logpdf(z, mu, sd) + np.log(max(1 - hop_q, 1e-300))
        if hop_q <= 0:
            return a
        c = stats.norm.logpdf(z, HOP_COUPLING * mu, sd) + np.log(hop_q)
        return np.logaddexp(a, c)
    return mix(m) - mix(-m)


def _draw_joint(rng, n_sessions, n_traces):
    """One secret and one hop event per trace, shared by all bands; noise is per band."""
    u = np.exp(SESSION_GAIN_SD * rng.standard_normal(n_sessions))
    v = np.exp(SESSION_NOISE_SD * rng.standard_normal(n_sessions))
    S = rng.integers(0, 2, size=(n_sessions, n_traces), dtype=np.int8)
    U = rng.random((n_sessions, n_traces))
    N = rng.standard_normal((N_BANDS, n_sessions, n_traces))
    W = rng.standard_normal((N_BANDS, n_sessions, n_traces))
    return u, v, S, U, N, W


def _fused_stat(row, s, A, base):
    u, v, S, U, N, W = base
    q = hop_out_prob(s)
    var = inject_var(row.alloc, row.power, s)
    T = np.zeros(S.shape)
    for b in range(N_BANDS):
        hq = q[b] if row.hop else 0.0
        kappa = np.where(U < hq, HOP_COUPLING, 1.0)   # one clock: the hop event is shared
        z = (GAIN[b] * u[:, None] * kappa * A * (2.0 * S - 1.0)
             + np.sqrt(var[b]) * N[b] + v[:, None] * SIGMA[b] * W[b])
        T += _llr(z, b, hq, var[b], A)
    return T


@dataclass
class CombinedDataset:
    """Four single-band columns plus one fused column, with per-session count tables."""
    band: object
    fused_counts: np.ndarray      # (R, G, 2, n_bins)

    @property
    def n_sessions(self):
        return self.band.n_sessions

    def mi_matrix(self, sessions=None):
        mi4 = self.band.mi_matrix(sessions)
        c = self.fused_counts if sessions is None else self.fused_counts[:, sessions]
        return np.c_[mi4, mi_from_counts(c.sum(axis=1))]


def simulate_combined(A, s, seed_seq, rows, n_sessions=128, n_traces=1000, n_bins=16,
                      cal_sessions=16, cal_traces=250) -> CombinedDataset:
    band_ss, cal_ss, main_ss = seed_seq.spawn(3)
    band = simulate_dataset(A, s, band_ss, rows, n_sessions=n_sessions, n_traces=n_traces)
    cal = _draw_joint(np.random.default_rng(cal_ss), cal_sessions, cal_traces)
    base = _draw_joint(np.random.default_rng(main_ss), n_sessions, n_traces)
    counts = np.zeros((len(rows), n_sessions, 2, n_bins), dtype=np.int32)
    for r, row in enumerate(rows):
        e = quantile_edges(_fused_stat(row, s, A, cal).ravel(), n_bins)
        T = _fused_stat(row, s, A, base)
        for g in range(n_sessions):
            counts[r, g] = counts_table(base[2][g], T[g], e)
    return CombinedDataset(band, counts)


# ---------------------------------------------------------------------------
# General-sum strong Stackelberg solver
# ---------------------------------------------------------------------------

def best_response(p, U, MI, acts):
    """Observer best response by its own utility U; ties go toward more leakage."""
    acts = list(acts)
    vals = p @ U[:, acts]
    tied = np.flatnonzero(vals >= vals.max() - TIE_TOL)
    leak = p @ MI[:, [acts[i] for i in tied]]
    return acts[int(tied[int(np.argmax(leak))])]


def gs_score(p, L, U, MI, types):
    """(defender loss, leakage bits) when every type best-responds to p by U."""
    loss = leak = 0.0
    for _, acts, w in types:
        a = best_response(p, U, MI, acts)
        loss += w * float(p @ L[:, a])
        leak += w * float(p @ MI[:, a])
    return loss, leak


def gs_best_pure(L, U, MI, types):
    R = L.shape[0]
    tot = np.zeros(R)
    for _, acts, w in types:
        acts = list(acts)
        Ua, MIa = U[:, acts], MI[:, acts]
        best = Ua.max(axis=1, keepdims=True)
        cand = np.where(Ua >= best - TIE_TOL, MIa, -np.inf)       # ties toward leakage
        a_idx = np.array(acts)[np.argmax(cand, axis=1)]
        tot += w * L[np.arange(R), a_idx]
    r = int(np.argmin(tot))
    return r, float(tot[r])


def solve_gs_stackelberg(L, U, types, margin=None):
    """Strong Stackelberg commitment: min over response profiles of an LP in p."""
    margin = GS_MARGIN if margin is None else margin
    R = L.shape[0]
    prior = np.array([w for *_, w in types])
    best = (np.inf, None, None)
    for profile in itertools.product(*[list(a) for _, a, _ in types]):
        c = sum(w * L[:, a] for w, a in zip(prior, profile))
        rows_ub, b_ub = [], []
        for (_, acts, _), a in zip(types, profile):
            for a2 in acts:
                if a2 != a:   # p . (U[:, a2] - U[:, a]) <= -margin
                    rows_ub.append(U[:, a2] - U[:, a])
                    b_ub.append(-margin)
        res = linprog(c, A_ub=np.array(rows_ub) if rows_ub else None, b_ub=b_ub or None,
                      A_eq=np.ones((1, R)), b_eq=[1.0], bounds=[(0, None)] * R, method="highs")
        if res.status == 0 and res.fun < best[0]:
            p = np.where(res.x < 1e-9, 0.0, res.x)
            best = (float(res.fun), p / p.sum(), profile)
    if best[1] is None:   # margin infeasible everywhere: fall back to the best pure row
        return None, None
    return best[1], best[2]


# ---------------------------------------------------------------------------
# Per-config evaluation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ExtConfig:
    k: float
    types: str
    fused_cost: float | None      # None: no fused action available

    def type_model(self):
        base = TYPE_MODELS[self.types]
        if self.fused_cost is None:
            return base
        return [(n, tuple(a) + ((FUSED,) if n == "adaptive" else ()), w) for n, a, w in base]

    def costs(self):
        return np.r_[OBS_COST, self.fused_cost if self.fused_cost is not None else 0.0]


def _fit_eval(MI_fit, MI_eval, rows, cfg, energy):
    """Fit every policy on one matrix, score on another. Returns dict of metrics."""
    types = cfg.type_model()
    oh = overhead(rows, cfg.k)
    c = cfg.costs()
    M_f, M_e = MI_fit + oh[:, None] - c, MI_eval + oh[:, None] - c
    L_f, L_e = MI_fit + oh[:, None], MI_eval + oh[:, None]
    U_f, U_e = MI_fit - c, MI_eval - c
    zs = fit_policies(M_f, MI_fit, types, rows)
    p_zs, p_bp = zs["game"][0], zs["best_pure"][0]
    p_gs, _ = solve_gs_stackelberg(L_f, U_f, types)
    p_tiny, _ = solve_gs_stackelberg(L_f, U_f, types, margin=GS_MARGIN_TINY)
    r_gp, _ = gs_best_pure(L_f, U_f, MI_fit, types)
    p_gp = one_hot(r_gp, len(rows))
    p_gs = p_gp if p_gs is None else p_gs
    p_tiny = p_gp if p_tiny is None else p_tiny
    out = {
        "zs_game": score(p_zs, M_e, MI_eval, types)[0],
        "zs_best_pure": score(p_bp, M_e, MI_eval, types)[0],
        "gs_stackelberg": gs_score(p_gs, L_e, U_e, MI_eval, types)[0],
        "gs_zero_sum_policy": gs_score(p_zs, L_e, U_e, MI_eval, types)[0],
        "gs_best_pure": gs_score(p_gp, L_e, U_e, MI_eval, types)[0],
        "gs_stackelberg_tiny": gs_score(p_tiny, L_e, U_e, MI_eval, types)[0],
        "gs_leak": gs_score(p_gs, L_e, U_e, MI_eval, types)[1],
        "gs_energy": float(p_gs @ energy),
    }
    fused_used = 0.0
    if cfg.fused_cost is not None:
        for _, acts, w in types:
            if FUSED in acts and best_response(p_gs, U_e, MI_eval, acts) == FUSED:
                fused_used += w
    out["fused_share"] = fused_used
    out["_policies"] = (p_zs, p_gs)
    return out


METRICS = {
    "gap_pure": ("zs_best_pure", "zs_game"),               # zero-sum value of mixing
    "gs_gap_pure": ("gs_best_pure", "gs_stackelberg"),     # general-sum value of mixing
    "commitment_value": ("gs_zero_sum_policy", "gs_stackelberg"),  # GS commitment vs zero-sum policy
    "gs_gap_pure_tiny_margin": ("gs_best_pure", "gs_stackelberg_tiny"),
}


def _gaps(o):
    return {g: o[a] - o[b] for g, (a, b) in METRICS.items()}


def analyze_extensions(A, s, seed_seq, configs, n_boot=200, n_sessions=128, n_traces=1000) -> dict:
    t0 = time.time()
    rows = coarse_library()
    sim_ss, split_ss, boot_ss = seed_seq.spawn(3)
    ds = simulate_combined(A, s, sim_ss, rows, n_sessions=n_sessions, n_traces=n_traces)
    energy = np.array([r.energy for r in rows])
    names = [r.name for r in rows]
    G = ds.n_sessions
    perm = np.random.default_rng(split_ss).permutation(G)
    h1, h2 = np.sort(perm[: G // 2]), np.sort(perm[G // 2:])

    def cross(mi1, mi2, cfg):
        a, b = _fit_eval(mi1, mi2, rows, cfg, energy), _fit_eval(mi2, mi1, rows, cfg, energy)
        avg = {k: 0.5 * (a[k] + b[k]) for k in a if not k.startswith("_")}
        return avg, (a["_policies"], b["_policies"])

    MI_full, MI_1, MI_2 = ds.mi_matrix(), ds.mi_matrix(h1), ds.mi_matrix(h2)
    point = {cfg: cross(MI_1, MI_2, cfg)[0] for cfg in configs}
    boot = {cfg: [] for cfg in configs}
    rng = np.random.default_rng(boot_ss)
    for _ in range(n_boot):
        s1 = rng.choice(h1, size=len(h1), replace=True)
        s2 = rng.choice(h2, size=len(h2), replace=True)
        m1, m2 = ds.mi_matrix(s1), ds.mi_matrix(s2)
        for cfg in configs:
            boot[cfg].append(_gaps(cross(m1, m2, cfg)[0]))
    results = []
    for cfg in configs:
        est = _gaps(point[cfg])
        gaps = {}
        for g in METRICS:
            pct, bc, se = _ci(est[g], np.array([b[g] for b in boot[cfg]]))
            gaps[g] = {"est": est[g], "ci": pct, "se": se}
        full = _fit_eval(MI_full, MI_full, rows, cfg, energy)
        p_zs, p_gs = full.pop("_policies")
        results.append({
            "A": A, "s": s, "k": cfg.k, "types": cfg.types, "fused_cost": cfg.fused_cost,
            "gaps": gaps, "gaps_in_sample": _gaps(full),
            "losses": {k: v for k, v in point[cfg].items()},
            "gs_policy": {names[i]: float(p_gs[i]) for i in np.flatnonzero(p_gs > 1e-6)},
            "zs_policy": {names[i]: float(p_zs[i]) for i in np.flatnonzero(p_zs > 1e-6)},
        })
    best_band = MI_full[:, :N_BANDS].max(axis=1)
    diag = {"A": A, "s": s, "runtime_s": time.time() - t0,
            "fused_minus_best_band_mi_mean": float((MI_full[:, FUSED] - best_band).mean()),
            "fused_minus_best_band_mi_min": float((MI_full[:, FUSED] - best_band).min())}
    return {"results": results, "diagnostics": diag}
