"""3D model of the ASCAM-1 board: STL export, annotated top view, rotating GIF.

    python hardware/scripts/board_3d.py

Units are millimetres. The placement follows the layout plan in hardware/README.md;
it is a mechanical concept model (package sizes are real, routing is not drawn).
"""

from __future__ import annotations

import struct
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import animation  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

HW = Path(__file__).resolve().parents[1]
BOARD_W, BOARD_H, BOARD_T = 70.0, 45.0, 1.6
GREEN, GOLD, BLACK, SILVER, TAN, WHITE = "#1d5c3a", "#d4a537", "#1b1b1b", "#b9bec4", "#c9a66b", "#efefef"


def box(x, y, w, h, z0, dz):
    """Six quads of an axis-aligned box with corner (x, y, z0)."""
    X, Y, Z = (x, x + w), (y, y + h), (z0, z0 + dz)
    v = np.array([[X[i], Y[j], Z[k]] for i in (0, 1) for j in (0, 1) for k in (0, 1)])
    faces = [(0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4), (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5)]
    return [v[list(f)] for f in faces]


def cylinder(cx, cy, r, z0, dz, axis="z", n=18):
    """Prism approximation of a cylinder along z (vertical) or y (edge connector barrel)."""
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    quads, ring0, ring1 = [], [], []
    for a in t:
        if axis == "z":
            p0 = [cx + r * np.cos(a), cy + r * np.sin(a), z0]
            p1 = [p0[0], p0[1], z0 + dz]
        else:   # along +y or -y from (cx, cy) at height z0, length dz (sign gives direction)
            p0 = [cx + r * np.cos(a), cy, z0 + r * np.sin(a)]
            p1 = [p0[0], cy + dz, p0[2]]
        ring0.append(p0)
        ring1.append(p1)
    ring0, ring1 = np.array(ring0), np.array(ring1)
    for i in range(n):
        j = (i + 1) % n
        quads.append(np.array([ring0[i], ring0[j], ring1[j], ring1[i]]))
    quads += [ring0, ring1]
    return quads


def parts():
    """List of (faces, color, label or None)."""
    z = BOARD_T
    P = [(box(0, 0, BOARD_W, BOARD_H, 0, BOARD_T), GREEN, None)]
    # power entry
    P.append((box(-1.0, 18.0, 7.5, 9.0, z, 3.2), SILVER, "J5 USB-C"))
    P.append((box(11.0, 21.0, 2.9, 1.6, z, 1.1), BLACK, "U1 LDO"))
    P.append((box(9.0, 25.0, 1.6, 0.8, z, 0.8), TAN, None))
    P.append((box(15.0, 21.4, 2.0, 1.25, z, 0.9), TAN, None))
    P.append((box(19.5, 21.2, 3.2, 1.6, z, 0.6), BLACK, "R_SH 1 Ω shunt"))
    # SMA edge connectors (square body + barrel sticking out of the edge)
    for cx, edge, lab in ((21.0, "top", "J1 conducted"), (48.0, "top", "J2 trigger"), (35.0, "bottom", "J3 EM loop")):
        y0 = BOARD_H - 6.35 if edge == "top" else 0.0
        P.append((box(cx - 3.2, y0, 6.35, 6.35, z, 6.35), GOLD, lab))
        dirn = 1 if edge == "top" else -1
        ys = BOARD_H if edge == "top" else 0.0
        P.append((cylinder(cx, ys, 2.4, z + 3.2, dirn * 7.0, axis="y"), GOLD, None))
    # MCU and its neighbours
    P.append((box(31.5, 18.5, 7.0, 7.0, z, 0.9), BLACK, "U2 STM32G431"))
    P.append((box(27.0, 28.5, 3.2, 2.5, z, 0.8), SILVER, "Y1 8 MHz"))
    for (x, y) in ((30.3, 21.5), (39.0, 21.5), (34.5, 17.0), (34.5, 26.3), (30.3, 18.0)):
        P.append((box(x, y, 1.0, 0.5, z, 0.5), TAN, None))
    P.append((box(41.5, 27.0, 5.0, 3.0, z, 0.05), GOLD, "J4 SWD pads"))
    # clock logic
    P.append((box(42.0, 21.0, 2.0, 2.1, z, 1.0), BLACK, "U3 AND"))
    P.append((box(42.0, 16.0, 2.0, 2.1, z, 1.0), BLACK, "U4 XOR doubler"))
    # four balanced branches
    for i, y in enumerate((7.5, 16.0, 24.5, 33.0)):
        P.append((box(52.0, y + 1.0, 2.0, 2.1, z, 1.0), BLACK, None))           # gate / inverter
        P.append((box(56.0, y + 2.4, 2.9, 1.3, z, 1.0), BLACK, None))           # Q1
        P.append((box(56.0, y - 0.2, 2.9, 1.3, z, 1.0), BLACK, None))           # Q2
        P.append((box(61.0, y + 2.4, 3.2, 1.6, z, 0.6), BLACK, None))           # R_LOAD
        P.append((box(61.0, y - 0.4, 3.2, 1.6, z, 0.6), BLACK, None))           # R_COMP
        P.append((box(51.0, y - 1.2, 15.0, 0.25, z, 0.02), WHITE, f"branch B{[0, 3, 1, 2][i]}"))
    # mounting holes (drawn as dark posts)
    for (x, y) in ((3.5, 3.5), (66.5, 3.5), (3.5, 41.5), (66.5, 41.5)):
        P.append((cylinder(x, y, 1.6, -0.01, BOARD_T + 0.05), "#0b0b0b", None))
    return P


def loop_ring():
    """Printed EM pickup loop around the MCU (copper on top layer)."""
    t = np.linspace(0, 2 * np.pi, 60)
    return np.c_[35.0 + 6.5 * np.cos(t), 22.0 + 6.5 * np.sin(t), np.full_like(t, BOARD_T + 0.02)]


def write_stl(P, path):
    tris = []
    for faces, _, _ in P:
        for f in faces:
            for k in range(1, len(f) - 1):
                tris.append((f[0], f[k], f[k + 1]))
    with open(path, "wb") as fh:
        fh.write(b"ASCAM-1 concept model, mm".ljust(80, b" "))
        fh.write(struct.pack("<I", len(tris)))
        for a, b, c in tris:
            n = np.cross(np.subtract(b, a), np.subtract(c, a))
            n = n / (np.linalg.norm(n) or 1.0)
            fh.write(struct.pack("<12fH", *n, *a, *b, *c, 0))
    return len(tris)


def draw(ax, P, labels=False):
    ax.computed_zorder = False      # painter's order: board first, parts on top (view is from above)
    for faces, col, _ in P:
        ax.add_collection3d(Poly3DCollection(faces, facecolors=col, edgecolors="#00000040", linewidths=0.2))
    ring = loop_ring()
    ax.plot(ring[:, 0], ring[:, 1], ring[:, 2], color=GOLD, lw=1.6)
    ax.text(36, 6.0, BOARD_T + 0.1, "ASCAM-1 rev 2", color=WHITE, fontsize=7, zdir="x")
    ax.set_xlim(-2, 72)
    ax.set_ylim(-9, 54)
    ax.set_zlim(-8, 14)
    ax.set_box_aspect((74, 63, 22), zoom=1.12)
    ax.set_axis_off()
    if labels:
        for faces, _, lab in P:
            if lab:
                c = np.vstack(faces).mean(axis=0)
                ax.text(c[0], c[1], c[2] + 4, lab, fontsize=7, ha="center")


def top_view(P, path):
    fig, ax = plt.subplots(figsize=(10, 6.8))
    for faces, col, lab in P:
        top = max(faces, key=lambda f: f[:, 2].mean())
        ax.fill(top[:, 0], top[:, 1], color=col, ec="#00000055", lw=0.4)
    ring = loop_ring()
    ax.plot(ring[:, 0], ring[:, 1], color=GOLD, lw=2)
    callouts = {
        "J5 USB-C power": (3, 22.5, -8, 32), "U1 LDO 3.3 V": (12.5, 21.8, 6, 36),
        "R_SH 1 Ω shunt\n(conducted band B0)": (21, 22, 14, 10), "J1 SMA: shunt to scope": (21, 46, 6, 52),
        "U2 STM32G431\nsynthetic AES, PLL hop": (35, 22, 28, 38), "printed EM loop\n(bands B1, B2, B3)": (29, 17, 18, 3),
        "J3 SMA: EM loop": (35, -1, 26, -9), "J2 SMA: trigger": (48, 46, 46, 52),
        "U3 / U4 clock gate\nand XOR doubler": (43, 19, 44, 8),
        "4 balanced load branches\nR_LOAD + R_COMP, 2 MOSFETs each": (60, 20, 72, 30),
    }
    for text, (x, y, tx, ty) in callouts.items():
        ax.annotate(text, (x, y), (tx, ty), fontsize=8.5, ha="left",
                    arrowprops=dict(arrowstyle="-", color="#333333", lw=0.7))
    ax.set_xlim(-12, 95)
    ax.set_ylim(-12, 56)
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title("ASCAM-1 rev 2: 70 x 45 mm, 4 layers (top view, concept placement)")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def main():
    (HW / "cad").mkdir(exist_ok=True)
    (HW / "figures").mkdir(exist_ok=True)
    P = parts()
    n = write_stl(P, HW / "cad" / "ascam1_board.stl")
    top_view(P, HW / "figures" / "board_top_annotated.png")
    fig = plt.figure(figsize=(7.2, 5.4))
    ax = fig.add_subplot(projection="3d")
    draw(ax, P)
    fig.subplots_adjust(0, 0, 1, 1)

    def frame(i):
        ax.view_init(elev=32 + 10 * np.sin(2 * np.pi * i / 48), azim=-60 + 7.5 * i)
        return []
    anim = animation.FuncAnimation(fig, frame, frames=48, interval=90)
    anim.save(HW / "figures" / "board_3d.gif", writer=animation.PillowWriter(fps=11), dpi=80)
    frame(0)
    fig.savefig(HW / "figures" / "board_3d.png", dpi=130)
    plt.close(fig)
    print(f"STL triangles: {n}; wrote board_3d.gif, board_3d.png, board_top_annotated.png")


if __name__ == "__main__":
    main()
