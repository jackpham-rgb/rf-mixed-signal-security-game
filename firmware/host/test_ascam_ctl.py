"""Tests for ascam_ctl.py against the host simulator. Run: make sim && python -m pytest host"""
import json
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SIM = HERE.parent / "build" / "ascam_sim"
import sys
sys.path.insert(0, str(HERE))
import ascam_ctl  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def sim_built():
    subprocess.run(["make", "-C", str(HERE.parent), "sim"], check=True, capture_output=True)


def test_python_aes_matches_fips197():
    assert ascam_ctl.aes128_encrypt(bytes.fromhex("000102030405060708090a0b0c0d0e0f"),
                                    bytes.fromhex("00112233445566778899aabbccddeeff")).hex() == \
        "69c4e0d86a7b0430d8cdb78070b4c55a"
    assert ascam_ctl.aes128_encrypt(bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c"),
                                    bytes.fromhex("3243f6a8885a308d313198a2e0370734")).hex() == \
        "3925841d02dc09fbdc118597196a0b32"


@pytest.mark.parametrize("plan", sorted(p.name for p in (HERE / "plans").glob("*.json")))
def test_every_plan_runs_and_verifies(plan, tmp_path):
    rc = ascam_ctl.main(["--sim", str(SIM), "--plan", str(HERE / "plans" / plan),
                         "--out", str(tmp_path), "--traces", "400"])
    assert rc == 0
    meta = json.loads((tmp_path / "run.json").read_text())
    assert meta["traces"] == 400 and meta["ciphertext_errors"] == 0
    weights = [d["weight"] for d in meta["plan"]["defenses"]]
    for i, w in enumerate(weights):   # each defense used about as often as its weight says
        expect = 400 * w / sum(weights)
        assert abs(meta["defense_counts"][str(i)] - expect) < 5 * (expect ** 0.5) + 2


def test_same_seed_same_traces(tmp_path):
    plan = str(HERE / "plans" / "hop.json")
    for d in ("a", "b"):
        ascam_ctl.main(["--sim", str(SIM), "--plan", plan, "--out", str(tmp_path / d), "--traces", "50"])
    assert (tmp_path / "a" / "traces.csv").read_text() == (tmp_path / "b" / "traces.csv").read_text()


def test_bad_command_is_reported():
    link = ascam_ctl.SimLink(str(SIM))
    try:
        with pytest.raises(RuntimeError, match="ERR"):
            ascam_ctl.command(link, "DEF 1 99 0000")
    finally:
        link.close()
