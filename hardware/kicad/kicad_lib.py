"""Tiny reader for KiCad symbol (.kicad_sym) and footprint (.kicad_mod) libraries.

Used by make_netlist.py to look up pin numbers by pin name and to confirm that
every pin number exists as a pad on the chosen footprint.
"""

from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path

SYM_DIR = Path(os.environ.get("KICAD_SYMBOL_DIR", "/usr/share/kicad/symbols"))
FP_DIR = Path(os.environ.get("KICAD_FOOTPRINT_DIR", "/usr/share/kicad/footprints"))
TOKEN = re.compile(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()"]+')


def parse(text: str):
    stack, cur = [], []
    for tok in TOKEN.findall(text):
        if tok == "(":
            stack.append(cur)
            cur = []
        elif tok == ")":
            done, cur = cur, stack.pop()
            cur.append(done)
        else:
            cur.append(tok[1:-1] if tok.startswith('"') else tok)
    return cur[0]


@lru_cache(maxsize=None)
def _symbols(lib: str) -> dict:
    tree = parse((SYM_DIR / f"{lib}.kicad_sym").read_text())
    return {node[1]: node for node in tree[1:] if isinstance(node, list) and node[0] == "symbol"}


def _pins_of(node) -> dict:
    out = {}
    def walk(n):
        for c in n[1:]:
            if isinstance(c, list):
                if c[0] == "pin":
                    name = next(x[1] for x in c if isinstance(x, list) and x[0] == "name")
                    num = next(x[1] for x in c if isinstance(x, list) and x[0] == "number")
                    out.setdefault(name, []).append(num)
                else:
                    walk(c)
    walk(node)
    return out


def symbol_pins(lib: str, name: str) -> dict:
    """Pin name -> list of pin numbers, following 'extends' to the base symbol."""
    syms = _symbols(lib)
    node = syms[name]
    ext = next((c[1] for c in node[1:] if isinstance(c, list) and c[0] == "extends"), None)
    return _pins_of(syms[ext]) if ext else _pins_of(node)


def symbol_property(lib: str, name: str, prop: str):
    node = _symbols(lib)[name]
    for c in node[1:]:
        if isinstance(c, list) and c[0] == "property" and c[1] == prop:
            return c[2]
    return None


@lru_cache(maxsize=None)
def footprint_pads(fp_id: str) -> set:
    lib, name = fp_id.split(":")
    tree = parse((FP_DIR / f"{lib}.pretty" / f"{name}.kicad_mod").read_text())
    return {c[1] for c in tree[1:] if isinstance(c, list) and c[0] == "pad" and c[1] != ""}
