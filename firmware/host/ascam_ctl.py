"""Drive the ASCAM-1 firmware and save labeled trace metadata.

    python firmware/host/ascam_ctl.py --port COM5 --plan firmware/host/plans/leakage.json --out captures/leakage
    python firmware/host/ascam_ctl.py --sim firmware/build/ascam_sim --plan ... --out ...   (no board needed)

The board runs the traces and pulses the trigger (SMA J2) around each AES call;
your scope captures the waveforms on J1/J3. This script records what happened in
each trace (defense used, secret bit, plaintext, ciphertext), checks every
ciphertext with an independent AES, and writes:

    <out>/traces.csv     one row per trace, in trigger order
    <out>/run.json       plan, firmware ID, seed, settings, and timing

Line up row i of traces.csv with the i-th triggered scope capture.
Synthetic keys only; this tool talks to your own board.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Independent AES-128 (FIPS-197) used only to verify the board's output
# ---------------------------------------------------------------------------

def _sbox():
    def gmul(a, b):
        p = 0
        while b:
            if b & 1:
                p ^= a
            a = ((a << 1) ^ 0x11B) if a & 0x80 else (a << 1)
            b >>= 1
        return p
    inv = [0] * 256
    for x in range(1, 256):
        for y in range(1, 256):
            if gmul(x, y) == 1:
                inv[x] = y
                break
    box = []
    for x in range(256):
        b = inv[x]
        s = b
        for i in range(1, 5):
            s ^= ((b << i) | (b >> (8 - i))) & 0xFF
        box.append(s ^ 0x63)
    return box


SBOX = _sbox()


def _xt(a):
    return ((a << 1) ^ 0x1B) & 0xFF if a & 0x80 else a << 1


def aes128_encrypt(key: bytes, pt: bytes) -> bytes:
    w = list(key)
    rcon = 1
    for i in range(16, 176, 4):
        t = w[i - 4:i]
        if i % 16 == 0:
            t = [SBOX[t[1]] ^ rcon, SBOX[t[2]], SBOX[t[3]], SBOX[t[0]]]
            rcon = _xt(rcon)
        w += [w[i - 16 + j] ^ t[j] for j in range(4)]
    s = [pt[i] ^ w[i] for i in range(16)]
    for rnd in range(1, 11):
        t = [SBOX[s[4 * ((c + r) % 4) + r]] for c in range(4) for r in range(4)]
        if rnd != 10:
            for c in range(4):
                a = t[4 * c:4 * c + 4]
                al = a[0] ^ a[1] ^ a[2] ^ a[3]
                t[4 * c:4 * c + 4] = [a[j] ^ al ^ _xt(a[j] ^ a[(j + 1) % 4]) for j in range(4)]
        s = [t[i] ^ w[16 * rnd + i] for i in range(16)]
    return bytes(s)


# ---------------------------------------------------------------------------
# Links: real serial port or the host simulator
# ---------------------------------------------------------------------------

class SimLink:
    def __init__(self, exe):
        self.p = subprocess.Popen([exe], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
        self.readline()   # banner

    def send(self, line):
        self.p.stdin.write(line + "\n")
        self.p.stdin.flush()

    def readline(self):
        return self.p.stdout.readline().strip()

    def close(self):
        self.p.stdin.close()
        self.p.wait(timeout=10)


class SerialLink:
    def __init__(self, port, baud=115200):
        import serial   # pip install pyserial
        self.s = serial.Serial(port, baud, timeout=10)
        time.sleep(0.2)
        self.s.reset_input_buffer()

    def send(self, line):
        self.s.write((line + "\n").encode())

    def readline(self):
        return self.s.readline().decode(errors="replace").strip()

    def close(self):
        self.s.close()


def command(link, line):
    link.send(line)
    while True:
        r = link.readline()
        if not r:
            raise RuntimeError(f"no answer to {line!r}")
        if r.startswith("ERR"):
            raise RuntimeError(f"{line!r}: {r}")
        if r.startswith("OK"):
            return r


# ---------------------------------------------------------------------------
# Plans
# ---------------------------------------------------------------------------

def apply_plan(link, plan):
    command(link, "CLEAR")
    command(link, f"SEED {plan.get('seed', 126)}")
    for s, k in enumerate(plan.get("keys", [])):
        command(link, f"KEY {s} {k}")
    for name in ("gate_us", "lead_us", "gap_us"):
        if name in plan:
            command(link, f"{name.split('_')[0].upper()} {plan[name]}")
    for i, d in enumerate(plan["defenses"]):
        command(link, f"DEF {i} {d['clock_mhz']} {d['loads']}")
        command(link, f"WEIGHT {i} {d['weight']}")


def run(link, plan, out: Path):
    ident = command(link, "ID")
    apply_plan(link, plan)
    keys = [bytes.fromhex(k) for k in plan.get("keys", [])] or [bytes(range(16)), bytes(0xF0 | i for i in range(16))]
    n = int(plan["traces"])
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    rows, bad = [], 0
    link.send(f"RUN {n}")
    first = link.readline()
    if not first.startswith("OK"):
        raise RuntimeError(f"RUN refused: {first}")
    while True:
        line = link.readline()
        if line.startswith("DONE"):
            break
        if line.startswith("ERR") or not line:
            raise RuntimeError(f"run stopped: {line!r}")
        _, idx, d, sbit, pt, ct = line.split()
        ok = aes128_encrypt(keys[int(sbit)], bytes.fromhex(pt)).hex() == ct
        bad += not ok
        rows.append({"index": int(idx), "defense": int(d), "secret": int(sbit), "plaintext": pt,
                     "ciphertext": ct, "ct_ok": int(ok)})
    with open(out / "traces.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    meta = {"firmware": ident, "plan": plan, "traces": len(rows), "ciphertext_errors": bad,
            "seconds": round(time.time() - t0, 3),
            "defense_counts": {str(i): sum(r["defense"] == i for r in rows) for i in range(len(plan["defenses"]))}}
    (out / "run.json").write_text(json.dumps(meta, indent=2))
    return meta


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--port", help="serial port of the USB-UART adapter on J6, e.g. COM5 or /dev/ttyUSB0")
    src.add_argument("--sim", help="path to the host simulator (firmware/build/ascam_sim)")
    ap.add_argument("--plan", required=True, help="plan JSON (see firmware/host/plans)")
    ap.add_argument("--out", required=True, help="output folder")
    ap.add_argument("--traces", type=int, help="override the plan's trace count")
    args = ap.parse_args(argv)
    plan = json.loads(Path(args.plan).read_text())
    if args.traces:
        plan["traces"] = args.traces
    link = SimLink(args.sim) if args.sim else SerialLink(args.port)
    try:
        meta = run(link, plan, Path(args.out))
    finally:
        link.close()
    print(f"{meta['traces']} traces, {meta['ciphertext_errors']} ciphertext errors, "
          f"defense counts {meta['defense_counts']}, {meta['seconds']} s -> {args.out}")
    return 1 if meta["ciphertext_errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
