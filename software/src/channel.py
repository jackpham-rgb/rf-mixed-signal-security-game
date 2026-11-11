"""Synthetic scalar channel: the original 4 x 4 correctness scaffold.

Model (one scalar feature per trace):

    Z = g_a * kappa * L(S) + N_{d,a} + sigma_a * W

* S in {0, 1} is a synthetic secret bit and L(S) = amplitude * (2S - 1).
* g_a, sigma_a are the observer's band gain and ambient noise sd.
* kappa = 1 when the clock sits in the observer's band and kappa = HOP_COUPLING
  when a hop moved it out (probability ``hop_out[a]`` per trace).
* N_{d,a} is Gaussian injected activity with variance ``inject_var[a]``.
* B_d (deterministic dummy activity) is a constant offset, which does not
  change MI, so it is omitted from Z.

This is not a calibrated model of any real device.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

HOP_COUPLING = 0.15
HOP_PROB = 0.75


@dataclass(frozen=True)
class ObserverAction:
    name: str
    gain: float
    noise_sd: float
    cost: float


@dataclass(frozen=True)
class DefenderAction:
    name: str
    hop_out: tuple       # per observer action: P(hop moves clock out of that band)
    inject_var: tuple    # per observer action: injected noise variance seen there
    energy: float        # normalized energy overhead E_d (dimensionless)
    latency: float       # normalized latency overhead T_d (dimensionless)
    false_alarm: float = 0.0


OBSERVER_ACTIONS = (
    ObserverAction("A0-conducted-low", gain=0.75, noise_sd=0.85, cost=0.01),
    ObserverAction("A1-clock-fundamental-em", gain=1.00, noise_sd=1.00, cost=0.03),
    ObserverAction("A2-harmonic-em", gain=0.65, noise_sd=0.70, cost=0.02),
    ObserverAction("A3-adaptive-high-pass", gain=1.18, noise_sd=0.78, cost=0.08),
)

DEFENDER_ACTIONS = (
    DefenderAction("D0-no-defense", (0, 0, 0, 0), (0, 0, 0, 0), 0.00, 0.00),
    # Fixed dummy load: broadband in the conducted band, mostly removed by high-pass.
    DefenderAction("D1-fixed-dummy", (0, 0, 0, 0), (1.0, 0.3, 0.3, 0.1), 0.28, 0.00),
    # Random frequency: moves narrowband EM bands out often, conducted bands rarely.
    DefenderAction("D2-random-frequency", (0.30, HOP_PROB, HOP_PROB, 0.30), (0, 0, 0, 0), 0.13, 0.18),
    # Shaped stochastic: hop plus randomized dummy levels spread over bands.
    DefenderAction("D3-shaped-stochastic", (0.30, HOP_PROB, HOP_PROB, 0.30), (0.6, 0.4, 0.4, 0.4), 0.36, 0.18),
)


def simulate_traces(rng: np.random.Generator, d: DefenderAction, a_idx: int, n: int,
                    amplitude: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """Draw n (S, Z) pairs for defender action d and observer action index a_idx."""
    a = OBSERVER_ACTIONS[a_idx]
    s = rng.integers(0, 2, size=n)
    out = rng.random(n) < d.hop_out[a_idx]
    kappa = np.where(out, HOP_COUPLING, 1.0)
    z = (a.gain * kappa * amplitude * (2 * s - 1)
         + np.sqrt(d.inject_var[a_idx]) * rng.standard_normal(n)
         + a.noise_sd * rng.standard_normal(n))
    return s, z


def overhead(d: DefenderAction, lambda_e: float, lambda_l: float, lambda_f: float = 0.0) -> float:
    return lambda_e * d.energy + lambda_l * d.latency + lambda_f * d.false_alarm


def exact_components(d: DefenderAction, a_idx: int, amplitude: float = 1.0):
    """Gaussian-mixture description of Z | S for exact MI checks."""
    a = OBSERVER_ACTIONS[a_idx]
    sd = np.sqrt(d.inject_var[a_idx] + a.noise_sd ** 2)
    k = np.array([1.0, HOP_COUPLING])
    w = np.array([1 - d.hop_out[a_idx], d.hop_out[a_idx]])
    means = np.vstack([-a.gain * k * amplitude, a.gain * k * amplitude])
    return means, np.full_like(means, sd), w
