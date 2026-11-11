"""Animated explainer of how the board and the game work (illustration, not data).

    python hardware/scripts/how_it_works_gif.py

Writes hardware/figures/how_it_works.gif. Band edges and frequencies match the
board design (hardware/README.md); spectral levels are stylized for clarity.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import animation  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

HW = Path(__file__).resolve().parents[1]
BANDS = [("B0 conducted", 2e4, 1e6, "#c77d2e"), ("B3 high-pass", 2e6, 2e7, "#7a5ea8"),
         ("B1 clock", 2.8e7, 3.6e7, "#2b7bb9"), ("B2 harmonic", 6e7, 6.8e7, "#2a9d8f")]
F = np.logspace(4, 8.1, 900)
FLOOR = 1.0
SCENES = [
    ("1. No defense", "The chip's power use depends on the secret. The listener tunes to the band that leaks most.",
     dict(hop=False, noise=[0, 0, 0, 0])),
    ("2. Fixed defense: noise in the clock band",
     "Dummy load B1 drowns the clock band. A smart listener just moves to another band.",
     dict(hop=False, noise=[0, 0, 6, 0])),
    ("3. Clock hop", "Changing the clock from 32 to 24 MHz moves the clock lines out of B1 and B2. B0 and B3 still leak.",
     dict(hop=True, noise=[0, 0, 0, 0])),
    ("4. Randomized mix (the game)",
     "Each trace picks a defense at random. A listener stuck on one band only gets the average: less to learn.",
     dict(mix=True)),
    ("5. A listener that hears everything",
     "Capturing all bands at once removes the band choice, and randomizing stops helping (theorem P1).",
     dict(mix=True, fused=True)),
]
MIX_MODES = [dict(hop=False, noise=[5, 3, 0, 0]), dict(hop=True, noise=[0, 0, 0, 0]),
             dict(hop=False, noise=[0, 0, 6, 0]), dict(hop=True, noise=[4, 4, 0, 0])]
FRAMES_PER_SCENE = 26


def gauss_line(f0, width, h):
    return h * np.exp(-0.5 * ((np.log10(F) - np.log10(f0)) / width) ** 2)


def leak_spectrum(hop):
    fc = 24e6 if hop else 32e6
    return (gauss_line(5e5, 0.18, 5.0) + gauss_line(6e6, 0.12, 3.0)
            + gauss_line(fc, 0.012, 9.0) + gauss_line(2 * fc, 0.012, 6.0))


def noise_spectrum(noise):
    out = np.zeros_like(F)
    for (name, lo, hi, _), lvl in zip(BANDS, noise):
        if lvl:
            mid = np.sqrt(lo * hi)
            out += gauss_line(mid, 0.6 * np.log10(hi / lo) / 2 + 0.01, lvl)
    return out


def band_info(mode):
    """Stylized 'bits learned' per band: SNR-like leak / (noise + floor), saturating."""
    leak, noise = leak_spectrum(mode["hop"]), noise_spectrum(mode["noise"])
    vals = []
    for _, lo, hi, _ in BANDS:
        m = (F >= lo) & (F < hi)
        snr = leak[m].max() ** 2 / (noise[m].max() ** 2 + FLOOR) if m.any() else 0
        vals.append(0.5 * np.log2(1 + snr) / 3.5)
    return np.array(vals)


def main():
    fig = plt.figure(figsize=(10.5, 5.8))
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 1.5], height_ratios=[1.15, 1], hspace=0.45, wspace=0.18,
                          left=0.03, right=0.98, top=0.83, bottom=0.08)
    ax_b, ax_s, ax_i = fig.add_subplot(gs[:, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, 1])
    title = fig.text(0.5, 0.955, "", ha="center", fontsize=15, weight="bold")
    sub = fig.text(0.5, 0.895, "", ha="center", fontsize=10.5, wrap=True)
    rng = np.random.default_rng(3)
    mix_avg = np.mean([band_info(m) for m in MIX_MODES], axis=0)

    def board(ax, mode, fused, t):
        ax.clear()
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis("off")
        ax.add_patch(FancyBboxPatch((0.3, 0.6), 9.4, 8.8, boxstyle="round,pad=0.1", fc="#1d5c3a", ec="none"))
        ax.text(5, 9.0, "ASCAM-1 test board", color="w", ha="center", fontsize=10)
        clk = "24 MHz" if mode["hop"] else "32 MHz"
        ax.add_patch(FancyBboxPatch((3.6, 4.4), 2.8, 2.6, boxstyle="round,pad=0.05", fc="#1b1b1b", ec="#d4a537"))
        ax.text(5, 6.1, "MCU", color="w", ha="center", fontsize=11, weight="bold")
        ax.text(5, 5.2, f"secret AES\nclock {clk}", color="#ddd", ha="center", fontsize=8)
        pulse = 0.35 + 0.25 * np.sin(t * 1.3)
        ax.add_patch(plt.Circle((5, 5.7), 2.0 + pulse, fill=False, ec="#d4a537", lw=1.5, alpha=0.6))
        for i, ((name, *_rest, col), lvl) in enumerate(zip(BANDS, mode["noise"])):
            y = 1.2 + i * 0.9
            on = lvl > 0
            ax.add_patch(FancyBboxPatch((7.2, y), 2.2, 0.65, boxstyle="round,pad=0.03",
                                        fc=col if on else "#2f6b4a", ec=col, lw=1.5))
            ax.text(8.3, y + 0.32, f"load {name.split()[0]}", color="w", ha="center", va="center", fontsize=7.5)
        ax.text(8.3, 4.95, "dummy loads", color="#cfe", ha="center", fontsize=8)
        ax.add_patch(FancyBboxPatch((0.8, 7.2), 1.6, 0.8, boxstyle="round,pad=0.03", fc="#b9bec4", ec="none"))
        ax.text(1.6, 7.6, "shunt", ha="center", va="center", fontsize=8)
        ax.text(1.6, 6.8, "-> B0", color="w", ha="center", fontsize=8)
        ax.text(5, 2.6, "EM loop -> B1 B2 B3", color="#f3d58a", ha="center", fontsize=8.5)
        ax.text(1.0, 1.5, "listener:\n" + ("ALL bands" if fused else "one band"), color="w", fontsize=9)

    def update(i):
        k, j = divmod(i, FRAMES_PER_SCENE)
        name, desc, spec = SCENES[k]
        title.set_text(name)
        sub.set_text(desc)
        fused = spec.get("fused", False)
        mode = MIX_MODES[rng.integers(len(MIX_MODES))] if spec.get("mix") else spec
        board(ax_b, mode, fused, i)
        ax_s.clear()
        leak, noise = leak_spectrum(mode["hop"]), noise_spectrum(mode["noise"])
        for n, lo, hi, col in BANDS:
            ax_s.axvspan(lo, hi, color=col, alpha=0.18)
            ax_s.text(np.sqrt(lo * hi), 11.3, n.split()[0], ha="center", fontsize=8, color=col, weight="bold")
        ax_s.fill_between(F, 0, noise, color="#888888", alpha=0.6, label="injected noise")
        ax_s.plot(F, leak, color="#d62828", lw=1.6, label="secret-dependent leakage")
        ax_s.set_xscale("log")
        ax_s.set_ylim(0, 12.5)
        ax_s.set_xlim(F[0], F[-1])
        ax_s.set_yticks([])
        ax_s.set_xlabel("frequency (Hz)", fontsize=9)
        ax_s.set_title("what each band sees", fontsize=10)
        ax_s.legend(loc="upper left", fontsize=8, frameon=False)
        ax_i.clear()
        info = mix_avg if spec.get("mix") else band_info(mode)
        names = [b[0].split()[0] for b in BANDS]
        cols = [b[3] for b in BANDS]
        if fused:
            names, cols = names + ["ALL"], cols + ["#333333"]
            info = np.r_[info, min(0.98, np.sqrt((info ** 2).sum()) * 1.15)]
        bars = ax_i.bar(names, info, color=cols, alpha=0.85)
        best = int(np.argmax(info))
        bars[best].set_edgecolor("k")
        bars[best].set_linewidth(2.5)
        ax_i.text(best, info[best] + 0.04, "listener picks this", ha="center", fontsize=8.5)
        ax_i.set_ylim(0, 1.15)
        ax_i.set_yticks([])
        ax_i.set_title("how much the listener learns per band (stylized)", fontsize=10)
        return []

    anim = animation.FuncAnimation(fig, update, frames=FRAMES_PER_SCENE * len(SCENES), interval=110)
    out = HW / "figures" / "how_it_works.gif"
    anim.save(out, writer=animation.PillowWriter(fps=9), dpi=72)
    update(FRAMES_PER_SCENE * 3 + 5)
    fig.savefig(HW / "figures" / "how_it_works_frame.png", dpi=110)
    plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    main()
