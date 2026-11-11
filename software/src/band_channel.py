"""Four-band synthetic channel with a separability knob, and the defender library.

Per trace, the observer that committed to band b sees one scalar feature

    Z_b = h_b * u_g * kappa_{d,b} * L(S) + N_{d,b} + v_g * sigma_b * W_b

* L(S) = A * (2S - 1) with a synthetic secret bit S; A is the leakage-to-noise
  ratio (LNR) because the ambient sd sigma_b is set by the observer actions.
* h_b, sigma_b and the observer cost come from ``channel.OBSERVER_ACTIONS``
  (band b is observer action A_b).
* u_g, v_g are log-normal session gain and noise factors (sd 0.15 and 0.10).
* Hopping: per trace the clock leaves band b with probability
  q_b(s) = (1 - s) * mean(t) + s * t_b, t = (0, 0.75, 0.75, 0); out of band it
  couples at kappa = 0.15.
* Injection with power P and band allocation x (sum 1) has per-band variance
  var_b(s) = 4 P ((1 - s) / 4 + s x_b).

At s = 0 hop and noise act identically on every band; at s = 1 they are fully
band-targeted. The total effect (sum over bands) is the same at every s.

Not a calibrated model of any device.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass

import numpy as np

from .channel import HOP_COUPLING, HOP_PROB, OBSERVER_ACTIONS
from .metrics import (counts_table, exact_binned_mi_mixture, exact_continuous_mi_mixture,
                      gauss_hermite_normal, mi_from_counts, quantile_edges)

N_BANDS = 4
HOP_TARGET = np.array([0.0, HOP_PROB, HOP_PROB, 0.0])
GAIN = np.array([a.gain for a in OBSERVER_ACTIONS])
SIGMA = np.array([a.noise_sd for a in OBSERVER_ACTIONS])
OBS_COST = np.array([a.cost for a in OBSERVER_ACTIONS])
SESSION_GAIN_SD = 0.15
SESSION_NOISE_SD = 0.10
POWERS = (0.75, 1.5, 3.0)
E_HOP, E_POWER, T_HOP = 0.13, 0.20, 0.18


@dataclass(frozen=True)
class Row:
    name: str
    hop: bool
    alloc: tuple    # band allocation x (sums to 1), or zeros for no injection
    power: float
    energy: float
    latency: float


def hop_out_prob(s: float) -> np.ndarray:
    return (1 - s) * HOP_TARGET.mean() + s * HOP_TARGET


def inject_var(alloc, power: float, s: float) -> np.ndarray:
    x = np.asarray(alloc, dtype=float)
    return 4.0 * power * ((1 - s) / N_BANDS + s * x) if power > 0 else np.zeros(N_BANDS)


def lattice(steps: int) -> list[tuple]:
    """All allocations of ``steps`` equal units over 4 bands, as fractions."""
    out = []
    for c in itertools.product(range(steps + 1), repeat=N_BANDS):
        if sum(c) == steps:
            out.append(tuple(ci / steps for ci in c))
    return out


def _row(hop: bool, alloc, power: float, name: str | None = None) -> Row:
    if name is None:
        if power == 0:
            name = f"{'H' if hop else 'F'}-none"
        else:
            digits = "".join(str(int(round(a * 4))) for a in alloc)
            name = f"{'H' if hop else 'F'}-x{digits}-P{power:g}"
    return Row(name, hop, tuple(alloc), power, E_HOP * hop + E_POWER * power, T_HOP * hop)


def coarse_library() -> list[Row]:
    """D0 to D3 followed by hop x (no injection, or 1/4-lattice allocation x power).

    Rows that duplicate D0, D2, or D3 are dropped from the rest. D1 (fixed
    dummy load) is deterministic structured activity B_d: it costs energy but
    is a constant offset, so it does not change MI.
    """
    zero = (0.0,) * N_BANDS
    uni = (0.25,) * N_BANDS
    rows = [
        Row("D0-no-defense", False, zero, 0.0, 0.0, 0.0),
        Row("D1-fixed-dummy", False, zero, 0.0, E_POWER * 1.5, 0.0),
        Row("D2-random-frequency", True, zero, 0.0, E_HOP, T_HOP),
        _row(True, uni, 0.75, "D3-shaped-stochastic"),
    ]
    dup = {("F", zero, 0.0), ("H", zero, 0.0), ("H", uni, 0.75)}
    for hop in (False, True):
        cands = [(zero, 0.0)] + [(x, P) for x in lattice(4) for P in POWERS]
        for x, P in cands:
            if (("H" if hop else "F"), x, P) in dup:
                continue
            rows.append(_row(hop, x, P))
    return rows


def fine_library(steps: int = 12, n_powers: int = 41, p_max: float = 3.0, s: float = 1.0):
    """Every 1/steps-lattice allocation at n_powers powers in [0, p_max], with and without hop.

    Returned as arrays (hop, var (R x 4), energy, latency). At s = 0 all
    allocations give the same variances, so duplicates are collapsed.
    """
    allocs = np.array(lattice(steps))
    powers = np.linspace(0.0, p_max, n_powers)[1:]
    hop_l, var_l, e_l, t_l = [], [], [], []
    for hop in (0, 1):
        hop_l.append(hop); var_l.append(np.zeros(N_BANDS)); e_l.append(E_HOP * hop); t_l.append(T_HOP * hop)
        for P in powers:
            v = 4.0 * P * ((1 - s) / N_BANDS + s * allocs)
            hop_l += [hop] * len(v); var_l += list(v)
            e_l += [E_HOP * hop + E_POWER * P] * len(v); t_l += [T_HOP * hop] * len(v)
    hop_a, var_a = np.array(hop_l), np.array(var_l)
    e_a, t_a = np.array(e_l), np.array(t_l)
    key = np.c_[hop_a, np.round(var_a, 12), e_a]
    _, keep = np.unique(key, axis=0, return_index=True)
    keep = np.sort(keep)
    return hop_a[keep], var_a[keep], e_a[keep], t_a[keep]


def row_cells(rows: list[Row], s: float):
    """Map every (row, band) to a distinct physical cell (hop, variance) per band."""
    q = hop_out_prob(s)
    cells = [dict() for _ in range(N_BANDS)]   # band -> {(hop, var): idx}
    idx = np.zeros((len(rows), N_BANDS), dtype=int)
    for r, row in enumerate(rows):
        v = inject_var(row.alloc, row.power, s)
        for b in range(N_BANDS):
            key = (bool(row.hop), round(float(v[b]), 12))
            idx[r, b] = cells[b].setdefault(key, len(cells[b]))
    params = []
    for b in range(N_BANDS):
        ks = sorted(cells[b], key=cells[b].get)
        params.append([(q[b] if hop else 0.0, var) for hop, var in ks])
    return idx, params


def _draw(rng, n_sessions, n_traces):
    u = np.exp(SESSION_GAIN_SD * rng.standard_normal(n_sessions))
    v = np.exp(SESSION_NOISE_SD * rng.standard_normal(n_sessions))
    shape = (N_BANDS, n_sessions, n_traces)
    S = rng.integers(0, 2, size=shape, dtype=np.int8)
    U = rng.random(shape)
    N = rng.standard_normal(shape)
    W = rng.standard_normal(shape)
    return u, v, S, U, N, W


def _features(b, hop_q, var, A, base):
    u, v, S, U, N, W = base
    kappa = np.where(U[b] < hop_q, HOP_COUPLING, 1.0)
    return (GAIN[b] * u[:, None] * kappa * A * (2.0 * S[b] - 1.0)
            + np.sqrt(var) * N[b] + v[:, None] * SIGMA[b] * W[b])


@dataclass
class BandDataset:
    A: float
    s: float
    rows: list
    cell_idx: np.ndarray          # (R, 4) -> cell index within band
    cell_params: list             # per band: list of (hop_q, var)
    edges: list                   # per band: array (n_cells_b, n_bins - 1)
    counts: list                  # per band: int array (n_cells_b, G, 2, n_bins)

    @property
    def n_sessions(self) -> int:
        return self.counts[0].shape[1]

    def mi_matrix(self, sessions: np.ndarray | None = None) -> np.ndarray:
        """Miller-Madow binned MI (R x 4) from pooled per-session histograms."""
        out = np.zeros(self.cell_idx.shape)
        for b in range(N_BANDS):
            c = self.counts[b] if sessions is None else self.counts[b][:, sessions]
            mi_b = mi_from_counts(c.sum(axis=1))
            out[:, b] = mi_b[self.cell_idx[:, b]]
        return out

    def exact_mi_matrix(self, kind: str = "binned", n_quad: int = 7) -> np.ndarray:
        out = np.zeros(self.cell_idx.shape)
        for b in range(N_BANDS):
            vals = np.array([exact_cell_mi(self.A, b, hq, var, kind=kind, edges=self.edges[b][i], n_quad=n_quad)
                             for i, (hq, var) in enumerate(self.cell_params[b])])
            out[:, b] = vals[self.cell_idx[:, b]]
        return out


def simulate_dataset(A: float, s: float, seed_seq: np.random.SeedSequence, rows: list[Row],
                     n_sessions: int = 128, n_traces: int = 1000, n_bins: int = 16,
                     cal_sessions: int = 16, cal_traces: int = 250) -> BandDataset:
    """Simulate every distinct cell with common random numbers across rows.

    Bin edges for each cell are frozen from separate calibration sessions.
    """
    cal_ss, main_ss = seed_seq.spawn(2)
    idx, params = row_cells(rows, s)
    cal = _draw(np.random.default_rng(cal_ss), cal_sessions, cal_traces)
    base = _draw(np.random.default_rng(main_ss), n_sessions, n_traces)
    edges, counts = [], []
    for b in range(N_BANDS):
        e_b = np.zeros((len(params[b]), n_bins - 1))
        c_b = np.zeros((len(params[b]), n_sessions, 2, n_bins), dtype=np.int32)
        for i, (hq, var) in enumerate(params[b]):
            e_b[i] = quantile_edges(_features(b, hq, var, A, cal).ravel(), n_bins)
            z = _features(b, hq, var, A, base)
            for g in range(n_sessions):
                c_b[i, g] = counts_table(base[2][b, g], z[g], e_b[i])
        edges.append(e_b)
        counts.append(c_b)
    return BandDataset(A, s, rows, idx, params, edges, counts)


def _components(A, b, hop_q, var, n_quad):
    xi, w = gauss_hermite_normal(n_quad)
    u = np.exp(SESSION_GAIN_SD * xi)
    v = np.exp(SESSION_NOISE_SD * xi)
    uu, vv = np.meshgrid(u, v, indexing="ij")
    ww = np.outer(w, w)
    mean_parts, sd_parts, wt_parts = [], [], []
    for kappa, pk in ((1.0, 1 - hop_q), (HOP_COUPLING, hop_q)):
        if pk <= 0:
            continue
        mean_parts.append((GAIN[b] * uu * kappa * A).ravel())
        sd_parts.append(np.sqrt(var + (vv * SIGMA[b]) ** 2).ravel())
        wt_parts.append(pk * ww.ravel())
    m = np.concatenate(mean_parts)
    sd = np.concatenate(sd_parts)
    wt = np.concatenate(wt_parts)
    return np.vstack([-m, m]), np.vstack([sd, sd]), wt


def exact_cell_mi(A, b, hop_q, var, kind="binned", edges=None, n_quad=7, n_grid=2001):
    """Exact MI of the pooled (over session factors) channel, by Gauss-Hermite quadrature."""
    means, sds, wt = _components(A, b, hop_q, var, n_quad)
    if kind == "binned":
        return exact_binned_mi_mixture(means, sds, wt, edges)
    return exact_continuous_mi_mixture(means, sds, wt, n_grid=n_grid)


def fine_mi_matrix(A: float, s: float, steps=12, n_powers=41, n_var_grid=121, n_quad=7):
    """Exact continuous MI for the fine library, interpolated on a variance grid."""
    hop, var, e, t = fine_library(steps, n_powers, s=s)
    q = hop_out_prob(s)
    vgrid = np.linspace(0.0, max(var.max(), 1e-9), n_var_grid)
    mi = np.zeros(var.shape)
    for b in range(N_BANDS):
        for h in (0, 1):
            g = np.array([exact_cell_mi(A, b, q[b] if h else 0.0, vv, kind="continuous", n_quad=n_quad)
                          for vv in vgrid])
            sel = hop == h
            mi[sel, b] = np.interp(var[sel, b], vgrid, g)
    return mi, e, t
