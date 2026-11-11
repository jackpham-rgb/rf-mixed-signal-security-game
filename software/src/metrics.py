"""Leakage metrics for the reference simulator.

Everything here works on synthetic data. Low estimated leakage is not a
security proof, and the binned MI estimators are biased (upward from finite
samples, downward from binning).
"""

from __future__ import annotations

import numpy as np
from scipy import stats

LOG2 = np.log(2.0)


# ---------------------------------------------------------------------------
# TVLA
# ---------------------------------------------------------------------------

def welch_t(x0: np.ndarray, x1: np.ndarray, axis: int = 0) -> np.ndarray:
    """Welch t statistic between two groups (TVLA fixed-vs-fixed or fixed-vs-random).

    |t| > 4.5 is an engineering screening convention, not a proof of security.
    """
    x0 = np.asarray(x0, dtype=float)
    x1 = np.asarray(x1, dtype=float)
    m0, m1 = x0.mean(axis=axis), x1.mean(axis=axis)
    v0, v1 = x0.var(axis=axis, ddof=1), x1.var(axis=axis, ddof=1)
    n0, n1 = x0.shape[axis], x1.shape[axis]
    return (m1 - m0) / np.sqrt(v0 / n0 + v1 / n1)


# ---------------------------------------------------------------------------
# Binned mutual information
# ---------------------------------------------------------------------------

def quantile_edges(z: np.ndarray, n_bins: int = 16) -> np.ndarray:
    """Interior equal-mass bin edges (length n_bins - 1) from calibration data."""
    qs = np.linspace(0.0, 1.0, n_bins + 1)[1:-1]
    return np.quantile(np.asarray(z, dtype=float), qs)


def bin_index(z: np.ndarray, edges: np.ndarray) -> np.ndarray:
    """Bin index in [0, len(edges)] for each sample."""
    return np.searchsorted(edges, z, side="right")


def counts_table(s: np.ndarray, z: np.ndarray, edges: np.ndarray, n_secrets: int = 2) -> np.ndarray:
    """Joint count table of shape (n_secrets, n_bins)."""
    n_bins = len(edges) + 1
    idx = np.asarray(s, dtype=np.int64) * n_bins + bin_index(z, edges)
    return np.bincount(idx, minlength=n_secrets * n_bins).reshape(n_secrets, n_bins)


def mi_from_counts(counts: np.ndarray, miller_madow: bool = True) -> np.ndarray:
    """Plug-in MI in bits from count tables of shape (..., n_secrets, n_bins).

    With ``miller_madow`` the first-order bias term (K_occupied - 1) / (2 N ln 2)
    is subtracted from each plug-in entropy. This reduces, but does not remove,
    the finite-sample bias.
    """
    c = np.asarray(counts, dtype=float)
    n = c.sum(axis=(-2, -1))
    ps = c.sum(axis=-1)
    pz = c.sum(axis=-2)

    def h(x, total, axes):
        with np.errstate(divide="ignore", invalid="ignore"):
            p = x / np.expand_dims(total, axis=tuple(range(-len(axes), 0)))
            t = np.where(x > 0, -p * np.log2(p), 0.0)
        val = t.sum(axis=axes)
        if miller_madow:
            k = (x > 0).sum(axis=axes)
            val = val + (k - 1) / (2.0 * np.maximum(total, 1) * LOG2)
        return val

    h_s = h(ps, n, (-1,))
    h_z = h(pz, n, (-1,))
    h_sz = h(c, n, (-2, -1))
    # Miller-Madow can go slightly negative near zero leakage; that is kept on
    # purpose so the estimator is not clipped (clipping adds upward bias).
    return h_s + h_z - h_sz


def binned_mi(s: np.ndarray, z: np.ndarray, n_bins: int = 16, edges: np.ndarray | None = None,
              miller_madow: bool = True) -> float:
    """Binned MI estimate in bits. Edges default to quantiles of z itself."""
    if edges is None:
        edges = quantile_edges(z, n_bins)
    n_secrets = int(np.max(s)) + 1
    return float(mi_from_counts(counts_table(s, z, edges, max(n_secrets, 2)), miller_madow))


# ---------------------------------------------------------------------------
# Key-ranking metrics (synthetic keys only, used to score defenses)
# ---------------------------------------------------------------------------

def key_ranks(scores: np.ndarray, true_key: np.ndarray) -> np.ndarray:
    """Rank (1 = best) of the true key for each experiment.

    ``scores`` has shape (n_experiments, n_keys); higher is more likely.
    Ties are broken pessimistically (the true key ranks after equal scores).
    """
    scores = np.asarray(scores, dtype=float)
    true_key = np.asarray(true_key, dtype=int)
    true_score = scores[np.arange(len(scores)), true_key]
    return (scores >= true_score[:, None]).sum(axis=1)


def guessing_entropy(scores: np.ndarray, true_key: np.ndarray) -> float:
    """Mean rank of the true key (log2 is often reported; this returns the rank)."""
    return float(np.mean(key_ranks(scores, true_key)))


def success_rate(scores: np.ndarray, true_key: np.ndarray, order: int = 1) -> float:
    """Fraction of experiments where the true key ranks within the top ``order``."""
    return float(np.mean(key_ranks(scores, true_key) <= order))


# ---------------------------------------------------------------------------
# Exact MI for binary-input Gaussian-mixture channels
# ---------------------------------------------------------------------------

def gauss_hermite_normal(n: int) -> tuple[np.ndarray, np.ndarray]:
    """Nodes and weights for E[f(xi)], xi ~ N(0, 1)."""
    x, w = np.polynomial.hermite_e.hermegauss(n)
    return x, w / w.sum()


def _mi_from_joint(joint: np.ndarray) -> np.ndarray:
    """MI in bits from joint probabilities of shape (..., n_secrets, n_bins)."""
    ps = joint.sum(axis=-1, keepdims=True)
    pz = joint.sum(axis=-2, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        t = np.where(joint > 0, joint * np.log2(joint / (ps * pz)), 0.0)
    return t.sum(axis=(-2, -1))


def exact_binned_mi_mixture(means: np.ndarray, sds: np.ndarray, weights: np.ndarray,
                            edges: np.ndarray, prior=(0.5, 0.5)) -> float:
    """Exact MI of a binned binary-input channel.

    ``means`` and ``sds`` have shape (2, K): row s holds the K Gaussian
    components of Z | S = s, with mixture ``weights`` of shape (K,) (or (2, K)).
    """
    means = np.asarray(means, dtype=float)
    sds = np.asarray(sds, dtype=float)
    weights = np.broadcast_to(np.asarray(weights, dtype=float), means.shape)
    e = np.concatenate(([-np.inf], np.asarray(edges, dtype=float), [np.inf]))
    cdf = stats.norm.cdf((e[None, None, :] - means[..., None]) / sds[..., None])
    p_bin = (weights[..., None] * np.diff(cdf, axis=-1)).sum(axis=1)  # (2, n_bins)
    joint = np.asarray(prior, dtype=float)[:, None] * p_bin
    return float(_mi_from_joint(joint))


def exact_continuous_mi_mixture(means: np.ndarray, sds: np.ndarray, weights: np.ndarray,
                                prior=(0.5, 0.5), n_grid: int = 4001) -> float:
    """Exact continuous MI of a binary-input Gaussian-mixture channel by grid quadrature."""
    means = np.asarray(means, dtype=float)
    sds = np.asarray(sds, dtype=float)
    weights = np.broadcast_to(np.asarray(weights, dtype=float), means.shape)
    lo = (means - 9 * sds).min()
    hi = (means + 9 * sds).max()
    z = np.linspace(lo, hi, n_grid)
    dz = z[1] - z[0]
    f = (weights[..., None] * stats.norm.pdf(z, means[..., None], sds[..., None])).sum(axis=1)
    pri = np.asarray(prior, dtype=float)[:, None]
    fbar = (pri * f).sum(axis=0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        t = np.where(f > 0, pri * f * np.log2(f / fbar), 0.0)
    return float(t.sum() * dz)


def bayes_success_binary_gaussian(delta_mean: float, sd: float) -> float:
    """Bayes-optimal success probability for two equiprobable Gaussians."""
    return float(stats.norm.cdf(abs(delta_mean) / (2.0 * sd)))
