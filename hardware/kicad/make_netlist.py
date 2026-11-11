"""Generate the ASCAM-1 rev 2 KiCad netlist and BOM from one parts table.

    python hardware/kicad/make_netlist.py

Writes hardware/kicad/ascam1.net (KiCad netlist, import in the PCB editor with
File > Import > Netlist), hardware/kicad/NETLIST.md (readable net list), and
hardware/bom.csv. Pin numbers are looked up by pin NAME in the official KiCad
symbol libraries, and every pin number is checked against the footprint's pads.
The script stops with an error if anything does not match.

Needs the KiCad symbol and footprint libraries (set KICAD_SYMBOL_DIR and
KICAD_FOOTPRINT_DIR if they are not in /usr/share/kicad).
"""

from __future__ import annotations

import csv
import sys
import uuid
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kicad_lib import footprint_pads, symbol_pins  # noqa: E402

HERE = Path(__file__).resolve().parent
HW = HERE.parent

R0402, R1206 = "Resistor_SMD:R_0402_1005Metric", "Resistor_SMD:R_1206_3216Metric"
C0402, C0603, C0805 = "Capacitor_SMD:C_0402_1005Metric", "Capacitor_SMD:C_0603_1608Metric", "Capacitor_SMD:C_0805_2012Metric"
SOT353, SOT23 = "Package_TO_SOT_SMD:SOT-353_SC-70-5", "Package_TO_SOT_SMD:SOT-23"
SMA = "Connector_Coaxial:SMA_Amphenol_132289_EdgeMount"
TP = "TestPoint:TestPoint_Pad_D1.0mm"

# Rough unit prices (USD) for the BOM; check a distributor before ordering.
PRICE = {"STM32G431CBU6": 5.50, "AP2112K-3.3TRG1": 0.40, "8 MHz": 0.30, "DMG2302U": 0.10,
         "74LVC1G08": 0.15, "74LVC1G86": 0.15, "74LVC1G04": 0.12, "SMA": 3.00, "USB-C": 0.60,
         "1R 0.1%": 0.60}


def part(ref, lib, sym, value, fp, pins, note="", mpn=""):
    return dict(ref=ref, lib=lib, sym=sym, value=value, fp=fp, pins=pins, note=note, mpn=mpn)


def R(ref, value, a, b, fp=R0402, note=""):
    return part(ref, "Device", "R", value, fp, {"1": a, "2": b}, note)


def C(ref, value, a, b, fp=C0402, note=""):
    return part(ref, "Device", "C", value, fp, {"1": a, "2": b}, note)


def parts():
    P = [
        # ---- Sheet 1: power and measurement ----
        part("J5", "Connector", "USB_C_Receptacle_PowerOnly_6P", "USB-C power",
             "Connector_USB:USB_C_Receptacle_GCT_USB4125-xx-x_6P_TopMnt_Horizontal",
             {"VBUS": "+5V", "GND": "GND", "SHIELD": "GND", "CC1": "CC1", "CC2": "CC2"},
             "5 V sink, power only", "GCT USB4125-GF-A"),
        R("R9", "5.1k", "CC1", "GND", note="USB-C CC pull-down"),
        R("R10", "5.1k", "CC2", "GND", note="USB-C CC pull-down"),
        part("U1", "Regulator_Linear", "AP2112K-3.3", "AP2112K-3.3", "Package_TO_SOT_SMD:SOT-23-5",
             {"VIN": "+5V", "EN": "+5V", "GND": "GND", "VOUT": "3V3_SRC"}, "3.3 V LDO", "AP2112K-3.3TRG1"),
        C("C1", "1u", "+5V", "GND", C0603, "LDO input"),
        C("C2", "10u", "3V3_SRC", "GND", C0805, "LDO output"),
        R("R1", "1R 0.1%", "3V3_SRC", "3V3_DUT", R1206, "R_SH current shunt, Kelvin pads"),
        part("TP3", "Connector", "TestPoint", "SHUNT_HI", TP, {"1": "3V3_SRC"}, "Kelvin sense, shunt high"),
        part("TP4", "Connector", "TestPoint", "SHUNT_LO", TP, {"1": "3V3_DUT"}, "Kelvin sense, shunt low"),
        C("C3", "100n", "3V3_DUT", "J1_SIG", note="AC coupling to J1"),
        part("J1", "Connector", "Conn_Coaxial", "SMA conducted", SMA, {"In": "J1_SIG", "Ext": "GND"},
             "conducted band B0", "Amphenol 132289"),
        R("R7", "49.9", "TRIG", "J2_SIG", note="trigger series termination"),
        part("J2", "Connector", "Conn_Coaxial", "SMA trigger", SMA, {"In": "J2_SIG", "Ext": "GND"}, "", "Amphenol 132289"),
        part("J3", "Connector", "Conn_Coaxial", "SMA EM loop", SMA, {"In": "EM_LOOP", "Ext": "GND"},
             "EM bands B1 B2 B3", "Amphenol 132289"),
        part("TP1", "Connector", "TestPoint", "LOOP_START", TP, {"1": "EM_LOOP"},
             "draw the 5 mm loop trace from TP1 around U2 to TP2"),
        part("TP2", "Connector", "TestPoint", "LOOP_END", TP, {"1": "GND"}, "loop return to ground"),
        # ---- Sheet 2: MCU ----
        part("U2", "MCU_ST_STM32G4", "STM32G431CBUx", "STM32G431CBU6",
             "Package_DFN_QFN:QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm",
             {"VBAT": "3V3_DUT", "VDD": "3V3_DUT", "VDDA": "3V3_DUT", "VREF+": "3V3_DUT", "VSS": "GND",
              "PF0": "OSC_IN", "PF1": "OSC_OUT", "PG10": "NRST", "PB8": "BOOT0",
              "PA13": "SWDIO", "PA14": "SWCLK", "PB3": "SWO",
              "PA0": "TRIG", "PA6": "DRV0", "PB0": "DRV3", "PA8": "MCO",
              "PB4": "EN0", "PB5": "EN1", "PB6": "EN2", "PB7": "EN3"},
             "PA6 = TIM3_CH1, PB0 = TIM3_CH3, PA8 = MCO, PG10 = NRST, PB8 = BOOT0", "STM32G431CBU6"),
        part("Y1", "Device", "Crystal_GND24", "8 MHz", "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm",
             {"1": "OSC_IN", "3": "OSC_OUT", "2": "GND", "4": "GND"}, "HSE, PLL reference"),
        C("C10", "10p", "OSC_IN", "GND", note="crystal load, check crystal datasheet"),
        C("C11", "10p", "OSC_OUT", "GND", note="crystal load, check crystal datasheet"),
        C("C12", "100n", "NRST", "GND", note="reset filter"),
        R("R11", "10k", "BOOT0", "GND", note="boot from flash"),
        part("J4", "Connector", "Conn_ARM_SWD_TagConnect_TC2030-NL", "SWD",
             "Connector:Tag-Connect_TC2030-IDC-NL_2x03_P1.27mm_Vertical",
             {"VCC": "3V3_DUT", "SWDIO": "SWDIO", "~{RESET}": "NRST", "SWCLK": "SWCLK", "GND": "GND", "SWO": "SWO"},
             "pads only, no part to buy"),
        C("C4", "100n", "3V3_DUT", "GND", note="VDD pin 23"),
        C("C5", "100n", "3V3_DUT", "GND", note="VDD pin 35"),
        C("C6", "100n", "3V3_DUT", "GND", note="VDD pin 48"),
        C("C7", "100n", "3V3_DUT", "GND", note="VDDA / VREF+"),
        C("C8", "4.7u", "3V3_DUT", "GND", C0603, "MCU bulk"),
        # XOR frequency doubler for branch 2
        part("U4", "74xGxx", "74LVC1G86", "74LVC1G86", SOT353,
             {"1": "MCO", "2": "DLY", "4": "DRV2", "GND": "GND", "VCC": "3V3_DUT"}, "XOR doubler"),
        R("R8", "100", "MCO", "DLY", note="doubler delay"),
        C("C9", "3.3p", "DLY", "GND", note="doubler delay, C0G"),
        C("C13", "100n", "3V3_DUT", "GND", note="U4 decoupling"),
    ]
    # ---- Sheet 3: four balanced branches ----
    drive = {0: "DRV0", 1: "MCO", 2: "DRV2", 3: "DRV3"}
    rload = {0: "100", 1: "150", 2: "150", 3: "100"}
    rcomp = {1: "301", 2: "301", 3: "200"}
    and_ref = {0: "U5", 1: "U3", 2: "U6", 3: "U7"}
    inv_ref = {1: "U8", 2: "U9", 3: "U10"}
    cap = 14
    for b in range(4):
        band = ["B0 conducted", "B1 clock", "B2 harmonic", "B3 high-pass"][b]
        P.append(part(and_ref[b], "74xGxx", "74LVC1G08", "74LVC1G08", SOT353,
                      {"1": drive[b], "2": f"EN{b}", "4": f"G{b}", "GND": "GND", "VCC": "3V3_DUT"},
                      f"branch {b} ({band}): carrier AND random enable"))
        P.append(part(f"Q{b + 1}", "Transistor_FET", "DMG2302U", "DMG2302U", SOT23,
                      {"G": f"G{b}", "S": "GND", "D": f"D{b}"}, f"branch {b} main switch"))
        P.append(R(f"R{12 + b}", rload[b], "3V3_DUT", f"D{b}", R1206, f"branch {b} R_LOAD, 0.25 W"))
        P.append(C(f"C{cap}", "100n", "3V3_DUT", "GND", note=f"{and_ref[b]} decoupling"))
        cap += 1
        if b in rcomp:
            P.append(part(inv_ref[b], "74xGxx", "74LVC1G04", "74LVC1G04", SOT353,
                          {"2": f"EN{b}", "4": f"GC{b}", "GND": "GND", "VCC": "3V3_DUT"},
                          f"branch {b}: NOT(enable) for the complementary load"))
            P.append(part(f"Q{4 + b}", "Transistor_FET", "DMG2302U", "DMG2302U", SOT23,
                          {"G": f"GC{b}", "S": "GND", "D": f"DC{b}"}, f"branch {b} complementary switch"))
            P.append(R(f"R{15 + b}", rcomp[b], "3V3_DUT", f"DC{b}", R1206, f"branch {b} R_COMP, 0.25 W"))
            P.append(C(f"C{cap}", "100n", "3V3_DUT", "GND", note=f"{inv_ref[b]} decoupling"))
            cap += 1
    for h in range(1, 5):
        P.append(part(f"H{h}", "Mechanical", "MountingHole", "M3", "MountingHole:MountingHole_3.2mm_M3", {}, "mounting hole"))
    return P


def resolve(P):
    """Turn pin names into pin numbers and run every check. Returns {net: [(ref, pin)]}."""
    nets, errors = defaultdict(list), []
    for p in P:
        if p["sym"] == "MountingHole":
            continue
        sym = symbol_pins(p["lib"], p["sym"])
        by_num = {n for nums in sym.values() for n in nums}
        pads = footprint_pads(p["fp"])
        used = set()
        for key, net in p["pins"].items():
            nums = sym.get(key) or ([key] if key in by_num else None)
            if not nums:
                errors.append(f"{p['ref']}: pin '{key}' not in symbol {p['sym']}")
                continue
            for n in nums:
                if n not in pads:
                    errors.append(f"{p['ref']}: pin {n} not a pad of {p['fp']}")
                nets[net].append((p["ref"], n))
                used.add(n)
        unused = sorted(by_num - used)
        names = {n: k for k, v in sym.items() for n in v}
        if p["sym"] != "STM32G431CBUx":
            for n in unused:
                if names[n] not in ("NC", "~"):
                    errors.append(f"{p['ref']}: pin {n} ({names[n]}) left unconnected")
    for net, nodes in nets.items():
        if len(nodes) < 2:
            errors.append(f"net {net} has only one connection: {nodes}")
    if errors:
        raise SystemExit("Netlist checks failed:\n  " + "\n  ".join(errors))
    return nets


def q(s):
    return '"' + str(s).replace('"', '\\"') + '"'


def write_netlist(P, nets, path):
    ns = uuid.UUID("6f1d2a8e-0b7c-4c44-9a0e-3c5ba1a5c001")
    L = ["(export (version \"E\")",
         "  (design (source \"ascam1.kicad_sch\") (tool \"make_netlist.py (ASCAM-1 rev 2)\"))",
         "  (components"]
    for p in P:
        ts = uuid.uuid5(ns, p["ref"])
        L.append(f"    (comp (ref {q(p['ref'])}) (value {q(p['value'])}) (footprint {q(p['fp'])})")
        L.append(f"      (libsource (lib {q(p['lib'])}) (part {q(p['sym'])}) (description {q(p['note'])}))")
        L.append(f"      (sheetpath (names \"/\") (tstamps \"/\")) (tstamps {q(ts)}))")
    L.append("  )")
    L.append("  (nets")
    for code, net in enumerate(sorted(nets, key=lambda n: (n != "GND", n)), start=1):
        nodes = " ".join(f"(node (ref {q(r)}) (pin {q(pin)}))" for r, pin in sorted(set(nets[net])))
        L.append(f"    (net (code {q(code)}) (name {q('/' + net)}) {nodes})")
    L.append("  )")
    L.append(")")
    path.write_text("\n".join(L) + "\n")


def write_readable(P, nets, path):
    L = ["# ASCAM-1 rev 2 netlist (generated)", "",
         "Generated by `make_netlist.py`. Do not edit by hand. Pin numbers come from the",
         "official KiCad symbol libraries and are checked against each footprint's pads.", "",
         "## Parts", "", "| Ref | Value | Footprint | Note |", "|---|---|---|---|"]
    for p in sorted(P, key=lambda p: (p["ref"].rstrip("0123456789"), int(''.join(c for c in p["ref"] if c.isdigit()) or 0))):
        L.append(f"| {p['ref']} | {p['value']} | `{p['fp'].split(':')[1]}` | {p['note']} |")
    L += ["", "## Nets", "", "| Net | Connections |", "|---|---|"]
    for net in sorted(nets, key=lambda n: (n not in ("GND", "3V3_DUT", "3V3_SRC", "+5V"), n)):
        L.append(f"| {net} | {', '.join(f'{r}.{pin}' for r, pin in sorted(set(nets[net])))} |")
    path.write_text("\n".join(L) + "\n")


def write_bom(P, path):
    groups = defaultdict(list)
    for p in P:
        groups[(p["value"], p["fp"], p["mpn"])].append(p)
    rows = []
    for (value, fp, mpn), ps in sorted(groups.items(), key=lambda g: g[1][0]["ref"]):
        key = mpn or value
        price = next((v for k, v in PRICE.items() if k in key or k == value), 0.0 if "Mounting" in fp or "TestPoint" in fp or "Tag-Connect" in fp else 0.02)
        if "SMA" in value:
            price = PRICE["SMA"]
        if "USB-C" in value:
            price = PRICE["USB-C"]
        rows.append({"refs": " ".join(sorted((p["ref"] for p in ps), key=lambda r: (r[0], int(''.join(c for c in r if c.isdigit()) or 0)))),
                     "qty": len(ps), "value": value, "footprint": fp.split(":")[1], "part number": mpn,
                     "notes": "; ".join(sorted({p["note"] for p in ps if p["note"]}))[:120], "approx unit USD": f"{price:.2f}"})
    rows.append({"refs": "PCB", "qty": 1, "value": "4-layer PCB", "footprint": "70 x 45 mm, 1.6 mm",
                 "part number": "", "notes": "layer 2 solid ground; about 10-30 USD for 5 boards", "approx unit USD": "4.00"})
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return sum(r["qty"] * float(r["approx unit USD"]) for r in rows)


def main():
    P = parts()
    nets = resolve(P)
    write_netlist(P, nets, HERE / "ascam1.net")
    write_readable(P, nets, HERE / "NETLIST.md")
    total = write_bom(P, HW / "bom.csv")
    n_pins = sum(len(v) for v in nets.values())
    print(f"OK: {len(P)} parts, {len(nets)} nets, {n_pins} pin connections; all checks passed. "
          f"BOM about {total:.2f} USD per board.")


if __name__ == "__main__":
    main()
