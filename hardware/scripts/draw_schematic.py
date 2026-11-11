"""Draw the ASCAM-1 schematic (three sheets) with schemdraw.

    python hardware/scripts/draw_schematic.py

Writes hardware/figures/schematic_sheet{1,2,3}_*.png/.svg. Component values
match hardware/spice/ascam_board.cir and hardware/bom.csv.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402
import schemdraw.logic as logic  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "figures"
schemdraw.config(fontsize=11, lw=1.3)


def ctr(e):
    """Center of a placed element, from its bounding box."""
    bb = e.get_bbox(transform=True)
    return ((bb.xmin + bb.xmax) / 2, (bb.ymin + bb.ymax) / 2)


def nfet():
    return elm.NFet(bulk=False).right().reverse()   # drain up, gate left, source down


def title(d, text, xy):
    d += elm.Label().at(xy).label(text, fontsize=14, halign="left")


def sheet_power(d):
    title(d, "Sheet 1: power path and measurement ports", (0, 3.6))
    # USB input and input cap
    d += elm.Dot(open=True).at((0, 0)).label("J5 USB-C\nVBUS 5 V", loc="left")
    d += elm.Line().right(1.5)
    n_in = d.add(elm.Dot())
    d += elm.Capacitor().down(2).label("C1 1 µF", loc="bottom")
    d += elm.Ground()
    d += elm.Line().at(n_in.center).right(1.5)
    ldo = d.add(elm.Ic(pins=[elm.IcPin("VIN", side="left", slot="2/2"), elm.IcPin("EN", side="left", slot="1/2"),
                              elm.IcPin("VOUT", side="right"), elm.IcPin("GND", side="bottom")],
                       edgepadW=0.8, edgepadH=0.5).anchor("VIN"))
    d += elm.Label().at((ctr(ldo)[0], ctr(ldo)[1] + 1.6)).label("U1 AP2112K-3.3 (LDO)", fontsize=10)
    d += elm.Line().at(ldo.EN).left(0.5)
    d += elm.Line().toy(n_in.center)
    d += elm.Line().at(ldo.GND).down(0.5)
    d += elm.Ground()
    d += elm.Line().at(ldo.VOUT).right(1.2)
    n_src = d.add(elm.Dot().label("3V3_SRC", loc="top"))
    d += elm.Capacitor().down(2).label("C2 10 µF", loc="bottom")
    d += elm.Ground()
    d += elm.Line().at(n_src.center).right(1.0)
    d += elm.Line().right(0.5)
    rsh = d.add(elm.Resistor().right(2.5).label("R_SH 1 Ω 0.1%", loc="top"))
    d += elm.Dot()
    d += elm.Arrow().right(2.5).label("3V3_DUT to MCU\nand load branches", loc="right")
    # Kelvin taps from both ends of the shunt to the conducted port J1
    d += elm.Line().at(rsh.end).down(1.2)
    d += elm.Capacitor().right(1.6).label("C3 100 nF", loc="top", fontsize=9)
    d += elm.Coax().right(1.6).label("J1 SMA: conducted\n(scope, AC, 50 Ω)", loc="bottom")
    d += elm.Line().at(rsh.start).down(2.8)
    d += elm.Line().right(5.7)
    d += elm.Dot(open=True)
    d += elm.Label().at((rsh.start[0], rsh.start[1] - 3.4)).label(
        "Kelvin pair: shunt-high reference for a differential probe or 1:1 balun at J1",
        fontsize=9, halign="left")
    # Second row: EM loop and trigger
    d += elm.Inductor2(loops=2).at((0, -5.6)).right(2).label("L_LOOP: printed 5 mm loop\nunder the MCU", loc="top")
    d += elm.Coax().right(1.8).label("J3 SMA\nEM pickup", loc="bottom")
    d += elm.Dot(open=True).at((8.5, -5.6)).label("PA0 TRIG", loc="left")
    d += elm.Resistor().right(2).label("R7 49.9 Ω", loc="top")
    d += elm.Coax().right(1.8).label("J2 SMA\ntrigger", loc="bottom")


def sheet_mcu(d):
    title(d, "Sheet 2: MCU and clock-derived drives", (-6, 8.6))
    mcu = d.add(elm.Ic(pins=[elm.IcPin("VDD", side="left"), elm.IcPin("OSC_IN", side="left"),
                              elm.IcPin("OSC_OUT", side="left"), elm.IcPin("SWD", side="left"),
                              elm.IcPin("PA8", side="right"), elm.IcPin("PA6", side="right"),
                              elm.IcPin("PB0", side="right"), elm.IcPin("PB4-7", side="right"),
                              elm.IcPin("PA0", side="right"), elm.IcPin("VSS", side="bottom")],
                       edgepadW=5.0, edgepadH=0.6, pinspacing=1.4).at((0, 0)))
    d += elm.Label().at((ctr(mcu)[0] + 0.2, ctr(mcu)[1] + 0.5)).label("U2 STM32G431", fontsize=11)
    d += elm.Label().at((ctr(mcu)[0] + 0.2, ctr(mcu)[1] - 0.5)).label("synthetic AES, PLL hop 24 / 32 MHz", fontsize=8)
    # VDD and decoupling
    d += elm.Line().at(mcu.VDD).left(1.2)
    d += elm.Dot()
    d += elm.Capacitor().down(1.6).label("C4-C8", loc="bottom", fontsize=9)
    d += elm.Ground()
    d += elm.Line().at(mcu.VDD).left(4.0)
    d += elm.Dot(open=True).label("3V3_DUT", loc="left")
    d += elm.Label().at((ctr(mcu)[0] - 9.0, ctr(mcu)[1] - 5.6)).label(
        "C4-C7: 4 x 100 nF, one per VDD pin\nC8: 4.7 µF bulk", fontsize=9, halign="left")
    # crystal between OSC_IN and OSC_OUT
    d += elm.Line().at(mcu.OSC_IN).left(2.6)
    xa = d.add(elm.Dot())
    d += elm.Line().at(mcu.OSC_OUT).left(2.6)
    d += elm.Dot()
    d += elm.Crystal().at(xa.center).up(1.4).label("Y1 8 MHz", loc="bottom", fontsize=9)
    d += elm.Line().at(mcu.SWD).left(2.6)
    d += elm.Dot(open=True).label("J4 SWD (Tag-Connect)", loc="left")
    d += elm.Line().at(mcu.VSS).down(0.5)
    d += elm.Ground()
    # Plain outputs
    for pin, txt in (("PA0", "TRIG to J2"), ("PB4-7", "EN0-EN3: LFSR random gating"),
                     ("PB0", "DRV3: TIM3 6 MHz PWM"), ("PA6", "DRV0: TIM3 250 kHz, slow edges")):
        d += elm.Line().at(mcu[pin]).right(1.0)
        d += elm.Dot(open=True).label(txt, loc="right")
    # MCO -> AND gate (branch 1) and XOR doubler (branch 2)
    d += elm.Line().at(mcu.PA8).right(1.0)
    mco = d.add(elm.Dot().label("MCO", loc="top", fontsize=9))
    d += elm.Line().right(0.6)
    g1 = d.add(logic.And(inputs=2).right().anchor("in2"))
    d += elm.Label().at((ctr(g1)[0] + 0.2, ctr(g1)[1] - 0.95)).label("U3 74LVC1G08", fontsize=9)
    d += elm.Line().at(g1.out).right(0.6)
    d += elm.Dot(open=True).label("DRV1: clock band", loc="right")
    d += elm.Line().at(g1.in1).left(0.25)
    d += elm.Line().up(0.45)
    d += elm.Dot(open=True).label("EN1", loc="left", fontsize=9)
    d += elm.Line().at(mco.center).down(2.6)
    tap = d.add(elm.Dot())
    d += elm.Line().right(1.6)
    x2 = d.add(logic.Xor(inputs=2).right().anchor("in1"))
    d += elm.Label().at((ctr(x2)[0], ctr(x2)[1] + 0.9)).label("U4 74LVC1G86", fontsize=9)
    d += elm.Line().at(x2.out).right(0.6)
    d += elm.Dot(open=True).label("DRV2: 2x clock band", loc="right")
    d += elm.Line().at(tap.center).down(1.4)
    d += elm.Resistor().right(1.6).label("R8 100 Ω", loc="top", fontsize=9)
    n_rc = d.add(elm.Dot())
    d += elm.Line().toy(x2.in2)
    d += elm.Line().tox(x2.in2)
    d += elm.Capacitor().at(n_rc.center).down(1.0).label("C9 3.3 pF", loc="bottom", fontsize=9)
    d += elm.Ground()
    d += elm.Label().at((ctr(x2)[0] + 2.6, ctr(x2)[1] - 3.6)).label(
        "XOR of the clock and its RC-delayed copy\ndoubles the frequency (48 / 64 MHz)", fontsize=9)


def sheet_branches(d):
    title(d, "Sheet 3: balanced dummy-load branch (one of four)", (-3, 4.2))
    d += elm.Dot().at((0, 3)).label("3V3_DUT", loc="left")
    d += elm.Line().right(3)
    top_a = d.add(elm.Dot())
    d += elm.Line().right(5)
    top_b = d.add(elm.Dot())
    # Main load: R_LOAD + Q1, gate from AND(DRVb, ENb)
    d += elm.Resistor().at(top_a.center).down(2).label("R_LOAD", loc="bottom")
    q1 = d.add(nfet().anchor("drain"))
    d += elm.Label().at((ctr(q1)[0] + 1.4, ctr(q1)[1] - 0.2)).label("Q1\nDMG2302U", fontsize=9)
    d += elm.Line().at(q1.source).down(0.4)
    d += elm.Ground()
    d += elm.Line().at(q1.gate).left(0.6)
    ga = d.add(logic.And(inputs=2).left().anchor("out").reverse())
    d += elm.Label().at((ctr(ga)[0], ctr(ga)[1] + 0.9)).label("74LVC1G08", fontsize=9)
    d += elm.Line().at(ga.in1).left(0.6)
    d += elm.Dot(open=True).label("DRVb", loc="left")
    d += elm.Line().at(ga.in2).left(0.3)
    en_node = d.add(elm.Dot())
    d += elm.Line().left(0.3)
    d += elm.Dot(open=True).label("ENb", loc="left")
    # Complementary load: R_COMP + Q2, gate from NOT(ENb)
    d += elm.Resistor().at(top_b.center).down(2).label("R_COMP\n≈ 2 R_LOAD", loc="bottom")
    q2 = d.add(nfet().anchor("drain"))
    d += elm.Label().at((ctr(q2)[0] + 1.4, ctr(q2)[1] - 0.2)).label("Q2\nDMG2302U", fontsize=9)
    d += elm.Line().at(q2.source).down(0.4)
    d += elm.Ground()
    d += elm.Line().at(q2.gate).left(0.4)
    inv = d.add(logic.Not().left().anchor("out").reverse())
    d += elm.Label().at((ctr(inv)[0], ctr(inv)[1] + 0.8)).label("74LVC1G04", fontsize=9)
    d += elm.Line().at(inv.in1).left(0.3)
    d += elm.Line().down(2.4)
    d += elm.Line().tox(en_node.center)
    d += elm.Line().toy(en_node.center)
    d += elm.Label().at((-3, -4.2)).label(
        "Branch values (b: target band, carrier, R_LOAD, R_COMP)\n"
        "0: B0 conducted-low, 250 kHz with slow edges, 100 Ω, no R_COMP\n"
        "1: B1 clock band, gated MCO 24 / 32 MHz, 150 Ω, 301 Ω\n"
        "2: B2 harmonic band, XOR doubler 48 / 64 MHz, 150 Ω, 301 Ω\n"
        "3: B3 high-pass band, 6 MHz timer PWM, 100 Ω, 200 Ω\n\n"
        "Rev 2 fix: R_COMP draws the same average current as R_LOAD when ENb is off,\n"
        "so random gating does not step the supply current (s rises from 0.17 to 0.78 in SPICE).",
        fontsize=10, halign="left")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in (("schematic_sheet1_power", sheet_power), ("schematic_sheet2_mcu", sheet_mcu),
                     ("schematic_sheet3_branch", sheet_branches)):
        with schemdraw.Drawing(show=False) as d:
            fn(d)
            d.save(str(OUT / f"{name}.svg"))
            d.save(str(OUT / f"{name}.png"), dpi=130)
    print("wrote schematic sheets to", OUT)


if __name__ == "__main__":
    main()
