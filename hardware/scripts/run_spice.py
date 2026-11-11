"""Simulate the ASCAM-1 board in ngspice and estimate its separability s and hop coupling.

    python hardware/scripts/run_spice.py          (needs ngspice on PATH)

For each case the script runs hardware/spice/ascam_board.cir with different
parameters, resamples the result on a uniform grid, and measures power in the
four observer bands:

    B0 conducted-low   20 kHz - 1 MHz   from the shunt current (SMA J1)
    B3 high-pass band   2 - 20 MHz      from the decoupling-loop current (near-field probe)
    B1 clock band      28 - 36 MHz      from the decoupling-loop current
    B2 harmonic band   60 - 68 MHz      from the decoupling-loop current

Leakage in a band is the power of (current with secret = 1) minus (secret = 0).
Injected power is the power a dummy-load branch adds. Separability follows the
model's definition: a branch aimed at band b puts a share (1 - s)/4 + s of its
(leakage-normalized) noise into band b, so s = (share_bb - 1/4) / (3/4).
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HW = Path(__file__).resolve().parents[1]
NETLIST = HW / "spice" / "ascam_board.cir"
BANDS = {  # model band index -> (name, f_lo, f_hi, sensor)
    0: ("B0 conducted-low", 20e3, 1e6, "shunt"),
    1: ("B1 clock", 28e6, 36e6, "loop"),
    2: ("B2 harmonic", 60e6, 68e6, "loop"),
    3: ("B3 high-pass", 2e6, 20e6, "loop"),
}
DT, T0, T1 = 0.5e-9, 60e-6, 100e-6   # skip 60 us: the supply settles with tau ~ 15 us


GATE_BIT = {0: 5e-6, 1: 1e-6, 2: 1e-6, 3: 1e-6}   # LFSR bit period per branch (s)


def random_gating_netlist(seed: int = 126) -> str:
    """Replace the static enables VR0..VR3 with pseudo-random on/off PWL sequences."""
    rng = np.random.default_rng(seed)
    text = NETLIST.read_text()
    for b, tb in GATE_BIT.items():
        bits = rng.integers(0, 2, size=int(np.ceil(T1 / tb)) + 1)
        pts, edge = [], 5e-9
        for i, bit in enumerate(bits):
            v = 3.3 * bit
            pts += [f"{i * tb + (edge if i else 0):.4g} {v}", f"{(i + 1) * tb:.4g} {v}"]
        text = text.replace(f"VR{b} r{b} 0 3.3", f"VR{b} r{b} 0 PWL(" + " ".join(pts) + ")")
    return text


def simulate(gating: str = "static", **params) -> dict:
    with tempfile.TemporaryDirectory() as td:
        dat = Path(td) / "out.dat"
        net = NETLIST
        if gating == "random":
            net = Path(td) / "board_random.cir"
            net.write_text(random_gating_netlist())
        alters = "\n".join(f"alterparam {k}={v}" for k, v in params.items())
        deck = Path(td) / "run.sp"
        deck.write_text(f".include {net}\n.control\n{alters}\nreset\nrun\n"
                        f"wrdata {dat} v(n_ldo,n_sh) i(vloop)\nquit\n.endc\n.end\n")
        subprocess.run(["ngspice", "-b", str(deck)], check=True, capture_output=True)
        raw = np.loadtxt(dat)
    t = raw[:, 0]
    grid = np.arange(T0, T1, DT)
    return {"shunt": np.interp(grid, t, raw[:, 1] / 1.0),   # 1 ohm shunt: volts = amps
            "loop": np.interp(grid, t, raw[:, 3])}


def spectrum(x):
    w = np.hanning(len(x))
    X = np.fft.rfft((x - x.mean()) * w)
    f = np.fft.rfftfreq(len(x), DT)
    return f, (np.abs(X) ** 2) / np.sum(w ** 2)


def band_powers(sim) -> np.ndarray:
    out = np.zeros(4)
    for b, (_, lo, hi, sensor) in BANDS.items():
        f, P = spectrum(sim[sensor])
        out[b] = P[(f >= lo) & (f < hi)].sum()
    return out


def diff(a, b):
    return {k: a[k] - b[k] for k in a}


def analyze(gating: str, **extra) -> dict:
    base0 = simulate(gating, secret=0, **extra)
    base1 = simulate(gating, secret=1, **extra)
    leak = band_powers(diff(base1, base0))
    hop0 = simulate(gating, secret=0, fclk="24meg", **extra)
    hop1 = simulate(gating, secret=1, fclk="24meg", **extra)
    leak_hop = band_powers(diff(hop1, hop0))
    inj = np.zeros((4, 4))
    sims = {}
    for b in range(4):
        sims[b] = diff(simulate(gating, secret=0, **{f"en{b}": 1}, **extra), base0)
        inj[b] = band_powers(sims[b])
    rel = inj / leak[None, :]          # injected noise relative to leakage, per band
    share = rel / rel.sum(axis=1, keepdims=True)
    s_branch = (np.diag(share) - 0.25) / 0.75
    return {"leak_power": leak.tolist(), "leak_power_hopped": leak_hop.tolist(),
            "hop_coupling_kappa": np.sqrt(leak_hop / leak).tolist(),
            "injected_power": inj.tolist(), "share_matrix": share.tolist(),
            "s_per_branch": s_branch.tolist(), "s_estimate": float(s_branch.mean()), "_sims": sims}


def plot_spectra(sims, share, title, path):
    names = [BANDS[b][0] for b in range(4)]
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharex=True)
    for b, ax in zip(range(4), axes.ravel()):
        for sensor, col in (("shunt", "#b5651d"), ("loop", "#1f5aa6")):
            f, P = spectrum(sims[b][sensor])
            ax.semilogx(f[1:], 10 * np.log10(P[1:] + 1e-30), lw=0.6, color=col, label=f"{sensor} current")
        for bb, (_, lo, hi, _) in BANDS.items():
            ax.axvspan(lo, hi, color="#2a9d8f" if bb == b else "#999999", alpha=0.25 if bb == b else 0.12)
        ax.set_title(f"Branch aimed at {names[b]}  (share in target {share[b][b]:.2f})", fontsize=9)
        ax.set_ylim(-160, -20)
        ax.grid(alpha=0.3)
    for ax in axes[1]:
        ax.set_xlabel("frequency (Hz)")
    for ax in axes[:, 0]:
        ax.set_ylabel("power (dB, A^2)")
    axes[0, 0].legend(frameon=False, fontsize=8)
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def main() -> None:
    res = {"bands": {BANDS[b][0]: [BANDS[b][1], BANDS[b][2], BANDS[b][3]] for b in BANDS},
           "note": "Ideal parts, no board parasitics beyond the listed L and ESR. A first design "
                   "estimate, not a measurement."}
    for gating in ("static", "random"):
        res[gating] = analyze(gating)
    res["random_rev1_unbalanced"] = analyze("random", bal=0)
    (HW / "sim").mkdir(exist_ok=True)
    (HW / "sim" / "spice_results.json").write_text(json.dumps(
        {k: ({kk: vv for kk, vv in v.items() if kk != "_sims"} if isinstance(v, dict) and "_sims" in v else v)
         for k, v in res.items()}, indent=2))
    names = [BANDS[b][0] for b in range(4)]
    plot_spectra(res["random"]["_sims"], res["random"]["share_matrix"],
                 "Simulated spectrum added by each dummy-load branch, LFSR-gated (green = target band)",
                 HW / "figures" / "spice_branch_spectra.png")
    fig, axes = plt.subplots(1, 3, figsize=(16.5, 4.8))
    for ax, gating, label in zip(axes, ("static", "random_rev1_unbalanced", "random"),
                                 ("always-on loads", "LFSR-gated, rev 1 (plain loads)",
                                  "LFSR-gated, rev 2 (balanced loads)")):
        sh = np.array(res[gating]["share_matrix"])
        kap = res[gating]["hop_coupling_kappa"]
        im = ax.imshow(sh, cmap="Greens", vmin=0, vmax=1)
        for i in range(4):
            for j in range(4):
                ax.text(j, i, f"{sh[i, j]:.2f}", ha="center", va="center", fontsize=10)
        ax.set_xticks(range(4), [n.split()[0] for n in names])
        ax.set_yticks(range(4), [f"branch -> {n.split()[0]}" for n in names])
        ax.set_xlabel("band where the injected noise lands")
        ax.set_title(f"{label}: s = {res[gating]['s_estimate']:.2f}\n"
                     f"hop coupling B1 = {kap[1]:.3f}, B2 = {kap[2]:.3f}", fontsize=10)
    fig.colorbar(im, ax=axes, label="share (leakage-normalized)", shrink=0.8)
    fig.savefig(HW / "figures" / "spice_separability.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(json.dumps({g: {k: res[g][k] for k in ("s_per_branch", "s_estimate", "hop_coupling_kappa")}
                      for g in ("static", "random_rev1_unbalanced", "random")}, indent=1))


if __name__ == "__main__":
    main()
