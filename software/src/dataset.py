"""Datasets for ascam: synthetic generation, an NPZ + JSON container, validation.

The planned layout is ``manifest.json`` + ``traces.zarr`` + ``features.parquet``.
To keep the dependencies to NumPy and SciPy, this version writes and reads a
documented fallback that keeps the same column names:

    DATASET_DIR/
      manifest.json   versions, seeds, generator, channel parameters, actions,
                      N and G per split, column notes, SHA-256 of each file
      traces.npz      member ``traces``: N x T float32. For the band4 channel
                      T = 4, one sample per observer band (A0 to A3).
      features.npz    one member per numeric column; string and category
                      columns are dictionary-encoded as ``NAME__codes``
                      (int32) plus ``NAME__categories`` (unicode)

NPZ members are stored uncompressed with fixed timestamps, so the same seed
and versions give byte-identical files. NPZ has no chunking and loads whole
arrays, so it suits small datasets only; Parquet and Zarr are planned. The
band4 samples follow the four-band channel of ``band_channel.py``. All secrets
are synthetic.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import platform
import shutil
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from . import __version__
from .band_channel import (
    GAIN,
    HOP_TARGET,
    N_BANDS,
    SESSION_GAIN_SD,
    SESSION_NOISE_SD,
    SIGMA,
    Row,
    _features,
    coarse_library,
    hop_out_prob,
    inject_var,
)
from .channel import HOP_COUPLING, OBSERVER_ACTIONS


class AscamError(Exception):
    """A user-facing error: bad arguments, invalid data, or a failed solve."""


SCHEMA_VERSION = "0.1.0"
MANIFEST_FILE = "manifest.json"
TRACES_FILE = "traces.npz"
FEATURES_FILE = "features.npz"
SPLITS = ("train", "calib", "test")
DUTS = ("band4",)
LIBRARIES = ("named", "full")
ALL_BANDS = "all-bands"
OBSERVER_NAMES = tuple(action.name for action in OBSERVER_ACTIONS)
GENERATE_SEED_ROLE = 1  # spawn_key role, so generation and bootstrap streams never coincide
PARAMETRIC_CAVEAT = (
    "synthetic: parametric four-band channel model, not simulated switching "
    "activity and not measured leakage"
)

REQUIRED_COLUMNS = {
    "trace_id": "int64",
    "trace_offset": "int64",
    "dataset_version": "string",
    "source": "category",
    "dut": "category",
    "abstraction": "category",
    "netlist_id": "category",
    "pvt_corner": "category",
    "session_id": "category",
    "key_id": "int32",
    "defense_action": "category",
    "defense_params": "string",
    "observer_action": "category",
    "plaintext": "binary",
    "label_hw": "uint8",
    "label_hd": "uint8",
    "tvla_group": "uint8",
    "energy_nj": "float32",
    "latency_cycles": "int32",
    "seed_sim": "uint64",
    "seed_noise": "uint64",
    "seed_defense": "uint64",
    "split": "category",
}
OPTIONAL_COLUMNS = {"energy_norm": "float64", "latency_norm": "float64"}
GROUP_COLUMNS = ("key_id", "session_id", "netlist_id", "pvt_corner")
COLUMN_NOTES = {
    "abstraction": "parametric: closed-form synthetic channel with no RTL or gate-level "
                   "simulation (a value added to the documented list)",
    "netlist_id": "none: the parametric channel has no netlist",
    "pvt_corner": "nominal: the parametric channel has no PVT model",
    "key_id": "one synthetic key per session, so key_id is the global session index",
    "defense_params": "JSON with hop, allocation (band shares of injected noise), and "
                      "power; D1-fixed-dummy injects no noise and differs from D0 only by "
                      "its energy cost",
    "observer_action": "all-bands: each trace stores one sample per observer band; "
                       "column j of traces.npz is observer action j",
    "plaintext": "empty: the parametric channel has no public input",
    "label_hw": "synthetic secret bit S (the Hamming weight of a one-bit value)",
    "label_hd": "equals S: the bit is written into a cleared register",
    "tvla_group": "1 for every trace: only random-input traces are generated",
    "energy_nj": "NaN: energy is not modeled in physical units (see energy_norm)",
    "latency_cycles": "-1: latency is not modeled in cycles (see latency_norm)",
    "energy_norm": "normalized, dimensionless energy overhead of the defense",
    "latency_norm": "normalized, dimensionless latency overhead of the defense",
    "seed_sim": "64-bit state word of the SeedSequence of the trace's (split, defense) "
                "block; one stream draws secrets, hops, and noise",
    "seed_noise": "equal to seed_sim (single stream per block)",
    "seed_defense": "equal to seed_sim (single stream per block)",
}
_ZIP_DATE = (1980, 1, 1, 0, 0, 0)


@dataclass(frozen=True)
class GenerateSpec:
    seed: int = 126
    traces: int = 10_000
    sessions: int = 30
    split: tuple[float, float, float] = (0.6, 0.2, 0.2)
    dut: str = "band4"
    library: str = "named"
    leakage_amplitude: float = 0.5
    separability: float = 1.0
    dataset_version: str = "0.1.0"


@dataclass
class Dataset:
    manifest: dict
    features: dict[str, NDArray]
    traces: NDArray
    origin: str = "memory"
    manifest_sha256: str | None = None
    validation: dict = field(default_factory=dict)


def split_sessions(total: int, fractions) -> tuple[int, int, int]:
    """Sessions per split by largest remainder; needs train >= 4 and calib >= 1."""
    f = np.asarray(fractions, dtype=float)
    if f.shape != (3,) or np.any(f < 0) or not np.isclose(f.sum(), 1.0):
        raise AscamError("--split needs three nonnegative fractions train,calib,test "
                         "that sum to 1")
    raw = f / f.sum() * total
    counts = np.floor(raw + 1e-9).astype(int)
    order = np.argsort(-(raw - counts), kind="stable")
    counts[order[: total - int(counts.sum())]] += 1
    train, calib, test = (int(c) for c in counts)
    if train < 4 or calib < 1:
        raise AscamError(f"{total} sessions split {train}/{calib}/{test} (train/calib/test); "
                         "need at least 4 train sessions and 1 calib session")
    return train, calib, test


def _session_factors(rng: np.random.Generator, count: int) -> tuple[NDArray, NDArray]:
    """Log-normal session gain u_g and noise v_g factors, drawn as in band_channel._draw."""
    gain = np.exp(SESSION_GAIN_SD * rng.standard_normal(count))
    noise = np.exp(SESSION_NOISE_SD * rng.standard_normal(count))
    return gain, noise


def _band_samples(row: Row, spec: GenerateSpec, gain: NDArray, noise: NDArray,
                  per_cell: int, rng: np.random.Generator) -> tuple[NDArray, NDArray]:
    """Secrets (G, n) and band samples (G, n, 4) of one defense row for G sessions.

    A trace has one secret bit and one clock-hop draw shared by its four band
    samples; injected and ambient noise are drawn per band. Each band sample
    follows ``band_channel._features``, so every (defense, band) cell has the
    distribution that ``band_channel.simulate_dataset`` simulates.
    """
    shape = (len(gain), per_cell)
    banded = (N_BANDS,) + shape
    secret = rng.integers(0, 2, size=shape, dtype=np.int8)
    hop = rng.random(shape)
    base = (gain, noise, np.broadcast_to(secret, banded), np.broadcast_to(hop, banded),
            rng.standard_normal(banded), rng.standard_normal(banded))
    hop_q = hop_out_prob(spec.separability) if row.hop else np.zeros(N_BANDS)
    variance = inject_var(row.alloc, row.power, spec.separability)
    samples = [_features(b, hop_q[b], variance[b], spec.leakage_amplitude, base)
               for b in range(N_BANDS)]
    return secret, np.stack(samples, axis=-1)


def synthesize(spec: GenerateSpec) -> Dataset:
    """Simulate a band4 dataset in memory, rows ordered split, session, defense, trace.

    Each split has its own session factors, common to every defense as in
    ``band_channel.simulate_dataset``, and one random stream per defense.
    """
    if spec.dut not in DUTS:
        raise AscamError(f"--dut {spec.dut} is not implemented; available: {', '.join(DUTS)}")
    if spec.library not in LIBRARIES:
        raise AscamError(f"--library must be one of {', '.join(LIBRARIES)}")
    if spec.seed < 0:
        raise AscamError("--seed must be nonnegative")
    if not 0.0 <= spec.leakage_amplitude < math.inf:
        raise AscamError("--leakage-amplitude must be a finite nonnegative number")
    if not 0.0 <= spec.separability <= 1.0:
        raise AscamError("--separability must lie in [0, 1]")
    library = coarse_library()
    if spec.library == "named":
        library = library[:4]
    sessions = split_sessions(spec.sessions, spec.split)
    d_count = len(library)
    per_cell = spec.traces // (spec.sessions * d_count)
    if per_cell < 2:
        raise AscamError(
            f"--traces {spec.traces} over {spec.sessions} sessions and {d_count} defenses "
            f"gives {per_cell} traces per session per defense; use --traces >= "
            f"{2 * spec.sessions * d_count}")

    root = np.random.SeedSequence(spec.seed, spawn_key=(GENERATE_SEED_ROLE,))
    parts, first = [], 0
    for split, count, split_seq in zip(SPLITS, sessions, root.spawn(len(SPLITS))):
        if count == 0:
            continue
        session_seq, rows_seq = split_seq.spawn(2)
        gain, noise = _session_factors(np.random.default_rng(session_seq), count)
        secrets, samples, seeds = [], [], []
        for row, child in zip(library, rows_seq.spawn(d_count)):
            s, z = _band_samples(row, spec, gain, noise, per_cell, np.random.default_rng(child))
            secrets.append(s)
            samples.append(z)
            seeds.append(child.generate_state(1, dtype=np.uint64)[0])
        shape = (count, d_count, per_cell)
        local = np.broadcast_to(np.arange(count)[:, None, None], shape).ravel()
        defense = np.broadcast_to(np.arange(d_count)[None, :, None], shape).ravel()
        width = max(3, len(str(count - 1)))
        names = np.array([f"{split}-{i:0{width}d}" for i in range(count)])
        parts.append({
            "split": np.full(local.size, split),
            "session_id": names[local],
            "key_id": first + local,
            "defense": defense,
            "secret": np.stack(secrets, axis=1).ravel(),
            "samples": np.stack(samples, axis=1).reshape(-1, N_BANDS),
            "seed": np.asarray(seeds, dtype=np.uint64)[defense],
        })
        first += count

    def joined(key: str) -> NDArray:
        return np.concatenate([part[key] for part in parts])

    defense, secret, seeds = joined("defense"), joined("secret").astype(np.uint8), joined("seed")
    n = secret.size
    params = np.array([json.dumps({"hop": r.hop, "allocation": list(r.alloc), "power": r.power},
                                  sort_keys=True) for r in library])
    features = {
        "trace_id": np.arange(n, dtype=np.int64),
        "trace_offset": np.arange(n, dtype=np.int64),
        "dataset_version": np.full(n, spec.dataset_version),
        "source": np.full(n, "synthetic"),
        "dut": np.full(n, spec.dut),
        "abstraction": np.full(n, "parametric"),
        "netlist_id": np.full(n, "none"),
        "pvt_corner": np.full(n, "nominal"),
        "session_id": joined("session_id"),
        "key_id": joined("key_id").astype(np.int32),
        "defense_action": np.array([r.name for r in library])[defense],
        "defense_params": params[defense],
        "observer_action": np.full(n, ALL_BANDS),
        "plaintext": np.zeros(n, dtype="S1"),
        "label_hw": secret,
        "label_hd": secret.copy(),
        "tvla_group": np.ones(n, dtype=np.uint8),
        "energy_nj": np.full(n, np.nan, dtype=np.float32),
        "latency_cycles": np.full(n, -1, dtype=np.int32),
        "seed_sim": seeds,
        "seed_noise": seeds.copy(),
        "seed_defense": seeds.copy(),
        "split": joined("split"),
        "energy_norm": np.array([r.energy for r in library], dtype=np.float64)[defense],
        "latency_norm": np.array([r.latency for r in library], dtype=np.float64)[defense],
    }
    traces = joined("samples").astype(np.float32)
    manifest = _manifest(spec, library, sessions, per_cell, n)
    return Dataset(manifest, features, traces)


def _manifest(spec, library, sessions, per_cell, n) -> dict:
    d_count = len(library)
    return {
        "schema_version": SCHEMA_VERSION,
        "dataset_version": spec.dataset_version,
        "container": {
            "format": "npz",
            "traces": TRACES_FILE,
            "features": FEATURES_FILE,
            "text_columns": "dictionary-encoded as NAME__codes (int32) and "
                            "NAME__categories (unicode)",
            "binary_columns": "fixed-width bytes",
            "planned": "traces.zarr + features.parquet",
        },
        "source": "synthetic",
        "dut": spec.dut,
        "abstraction": "parametric",
        "caveat": PARAMETRIC_CAVEAT,
        "license": "MIT (synthetic data generated by ascam; no third-party RTL)",
        "master_seed": spec.seed,
        "seed_derivation": (
            "numpy SeedSequence(master_seed, spawn_key=(1,)).spawn(3) gives the train, "
            "calib, and test streams; each spawns [session factors, trace blocks], and "
            "the trace-block stream spawns one child per defense, which draws secrets, "
            "hop uniforms, injected noise, and ambient noise in that order"),
        "generator": {
            "tool": "ascam generate",
            "version": __version__,
            "channel_module": "src/band_channel.py",
            "arguments": asdict(spec),
            "generator_commit": None,
        },
        "tool_versions": {
            "ascam": __version__,
            "python": platform.python_version(),
            "numpy": np.__version__,
            "rtl_tools": "not used (parametric channel)",
        },
        "channel": {
            "model": "band4",
            "equation": "Z_b = h_b u_g kappa_{d,b} L(S) + N_{d,b} + v_g sigma_b W_b",
            "roadmap_terms": {"H_a": "h_b u_g kappa_{d,b}",
                              "B_d": "left out: a constant offset does not change MI, so "
                                     "D1-fixed-dummy only costs energy",
                              "N_d": "N_{d,b}", "W": "v_g sigma_b W_b"},
            "parameters": {
                "leakage_amplitude": spec.leakage_amplitude,
                "separability": spec.separability,
                "band_gain": GAIN.tolist(),
                "ambient_noise_sd": SIGMA.tolist(),
                "hop_target": HOP_TARGET.tolist(),
                "hop_out_probability": hop_out_prob(spec.separability).tolist(),
                "out_of_band_coupling": HOP_COUPLING,
                "session_gain_sd": SESSION_GAIN_SD,
                "session_noise_sd": SESSION_NOISE_SD,
            },
            "rules": {
                "leakage": "L(S) = A (2S - 1), A = leakage_amplitude, S a synthetic bit",
                "hop": "the clock leaves band b with probability q_b = (1 - s) mean(t) + "
                       "s t_b (t = hop_target); out of band the leakage couples at "
                       "out_of_band_coupling",
                "injection": "power P with band allocation x gives variance "
                             "4 P ((1 - s) / 4 + s x_b) in band b",
                "session_factors": "u_g = exp(session_gain_sd xi), v_g = "
                                   "exp(session_noise_sd xi'), one pair per session shared "
                                   "by every defense",
                "draws": "one secret bit and one hop draw per trace, shared by the four "
                         "bands; injected and ambient noise independent per band",
            },
            "units": "dimensionless; A is in units of the A0 ambient-noise standard deviation",
        },
        "defense_actions": [
            {"name": r.name, "hop": r.hop, "allocation": list(r.alloc), "power": r.power,
             "energy": r.energy, "latency": r.latency, "false_alarm": 0.0}
            for r in library
        ],
        "observer_actions": list(OBSERVER_NAMES),
        "observer_encoding": "trace_columns",
        "trace": {"dtype": "float32", "shape": [n, N_BANDS], "columns": list(OBSERVER_NAMES)},
        "label": {"column": "label_hw", "classes": [0, 1],
                  "meaning": "synthetic secret bit S"},
        "overhead_columns": {"energy": "energy_norm", "latency": "latency_norm",
                             "units": "normalized, dimensionless"},
        "N": n,
        "G": int(sum(sessions)),
        "traces_per_session_per_defense": per_cell,
        "splits": {split: {"sessions": count, "traces": count * d_count * per_cell}
                   for split, count in zip(SPLITS, sessions)},
        "columns": {**REQUIRED_COLUMNS, **OPTIONAL_COLUMNS},
        "column_notes": COLUMN_NOTES,
    }


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _npz_bytes(arrays: dict[str, NDArray]) -> bytes:
    """A standard .npz archive (readable by numpy.load) with deterministic bytes."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, array in arrays.items():
            member = io.BytesIO()
            np.lib.format.write_array(member, np.ascontiguousarray(array), allow_pickle=False)
            info = zipfile.ZipInfo(f"{name}.npy", date_time=_ZIP_DATE)
            info.create_system = 3
            info.external_attr = 0o644 << 16
            archive.writestr(info, member.getvalue())
    return buffer.getvalue()


def _encode_columns(features: dict[str, NDArray]) -> dict[str, NDArray]:
    members = {}
    for name, values in features.items():
        if values.dtype.kind == "U":
            categories, codes = np.unique(values, return_inverse=True)
            members[f"{name}__codes"] = codes.astype(np.int32)
            members[f"{name}__categories"] = categories
        else:
            members[name] = values
    return members


def _decode_columns(members: dict[str, NDArray]) -> dict[str, NDArray]:
    features = {}
    for key, values in members.items():
        if key.endswith("__categories"):
            continue
        if not key.endswith("__codes"):
            features[key] = values
            continue
        name = key[: -len("__codes")]
        categories = members.get(f"{name}__categories")
        if categories is None or values.dtype.kind not in "iu":
            raise AscamError(f"features: {key} needs integer codes and {name}__categories")
        if values.size and (values.min() < 0 or values.max() >= len(categories)):
            raise AscamError(f"features: {key} has codes outside its categories")
        features[name] = categories[values]
    return features


def encode_dataset(dataset: Dataset) -> dict[str, bytes]:
    """File name to bytes; the manifest gains the SHA-256 of each data file."""
    files = {
        TRACES_FILE: _npz_bytes({"traces": dataset.traces}),
        FEATURES_FILE: _npz_bytes(_encode_columns(dataset.features)),
    }
    manifest = dict(dataset.manifest)
    manifest["files"] = {name: {"sha256": _sha256(data), "bytes": len(data)}
                         for name, data in files.items()}
    files[MANIFEST_FILE] = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
    return files


def write_dataset(dataset: Dataset, out: str | Path) -> Path:
    """Write the dataset directory; refuses to touch an existing non-empty path."""
    out = Path(out)
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise AscamError(f"{out} already exists and is not empty; generate never "
                         "overwrites a dataset")
    files = encode_dataset(dataset)
    partial = out.with_name(f".{out.name}.partial")
    if partial.exists():
        shutil.rmtree(partial)
    partial.mkdir(parents=True)
    try:
        for name, data in files.items():
            (partial / name).write_bytes(data)
        if out.exists():
            out.rmdir()
        partial.rename(out)
    except BaseException:
        shutil.rmtree(partial, ignore_errors=True)
        raise
    return out


def _load_npz(data: bytes, name: str) -> dict[str, NDArray]:
    try:
        with np.load(io.BytesIO(data), allow_pickle=False) as archive:
            return {key: archive[key] for key in archive.files}
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        raise AscamError(f"cannot read {name}: {error}") from error


def _has_kind(values: NDArray, kind: str) -> bool:
    if kind in ("string", "category"):
        return values.dtype.kind == "U"
    if kind == "binary":
        return values.dtype.kind == "S"
    return values.dtype == np.dtype(kind)


def validate(dataset: Dataset) -> dict:
    """Schema, range, and split-disjointness checks; raises AscamError on failure.

    A grouping column with a single value in the whole dataset (for example
    one netlist) cannot be held out, so it is reported as exempt.
    """
    m, f, traces = dataset.manifest, dataset.features, dataset.traces
    if str(m.get("schema_version", "")).split(".")[0] != SCHEMA_VERSION.split(".")[0]:
        raise AscamError(f"unsupported schema_version {m.get('schema_version')!r}; this "
                         f"ascam reads {SCHEMA_VERSION}")
    if traces.ndim != 2 or traces.dtype.kind != "f":
        raise AscamError("traces must be a 2-D floating-point array")
    missing = [name for name in REQUIRED_COLUMNS if name not in f]
    if missing:
        raise AscamError(f"features: missing required columns {missing}")
    kinds = {**REQUIRED_COLUMNS, **{k: v for k, v in OPTIONAL_COLUMNS.items() if k in f}}
    for name, kind in kinds.items():
        if not _has_kind(f[name], kind):
            raise AscamError(f"features: column {name} has dtype {f[name].dtype}, "
                             f"expected {kind}")
    lengths = {len(values) for values in f.values()}
    if len(lengths) != 1 or 0 in lengths:
        raise AscamError("features: columns must be nonempty and of equal length")
    offset = f["trace_offset"]
    if offset.min() < 0 or offset.max() >= len(traces):
        raise AscamError("features: trace_offset points outside traces")
    if np.any(np.diff(f["trace_id"]) <= 0):
        raise AscamError("features: trace_id must be unique and increasing")
    split = f["split"]
    unknown = sorted(set(np.unique(split).tolist()) - set(SPLITS))
    if unknown:
        raise AscamError(f"features: unknown split values {unknown}")
    defenses = [d.get("name") for d in m.get("defense_actions", [])]
    observers = list(m.get("observer_actions", []))
    if not defenses or not observers:
        raise AscamError("manifest: defense_actions and observer_actions are required")
    extra = sorted(set(np.unique(f["defense_action"]).tolist()) - set(defenses))
    if extra:
        raise AscamError(f"features: defense_action values {extra[:3]} are not in the manifest")
    if m.get("observer_encoding") != "trace_columns":
        raise AscamError("manifest: only observer_encoding 'trace_columns' is implemented")
    if traces.shape[1] != len(observers) or np.any(f["observer_action"] != ALL_BANDS):
        raise AscamError(f"trace_columns encoding needs one trace column per observer "
                         f"action and observer_action '{ALL_BANDS}' on every row")
    checked, exempt = [], []
    for column in GROUP_COLUMNS:
        values = f[column]
        if np.unique(values).size < 2:
            exempt.append(column)
            continue
        groups = [set(np.unique(values[split == s]).tolist()) for s in SPLITS]
        for i in range(len(SPLITS)):
            for j in range(i + 1, len(SPLITS)):
                shared = sorted(groups[i] & groups[j])
                if shared:
                    raise AscamError(f"split leak: {column} {shared[:3]} appears in both "
                                     f"{SPLITS[i]} and {SPLITS[j]}")
        checked.append(column)
    return {"required_columns": "present with documented dtypes",
            "group_disjointness_checked": checked,
            "single_level_groups_exempt": exempt}


def open_dataset(path: str | Path) -> Dataset:
    """Read a dataset directory, verify checksums, and validate it."""
    path = Path(path)
    manifest_path = path / MANIFEST_FILE
    if not manifest_path.is_file():
        raise AscamError(f"{path} is not an ascam dataset (no {MANIFEST_FILE})")
    raw = manifest_path.read_bytes()
    try:
        manifest = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise AscamError(f"{MANIFEST_FILE} is not valid JSON: {error}") from error
    if manifest.get("container", {}).get("format") != "npz":
        raise AscamError("only the npz container is implemented; Parquet/Zarr are planned")
    contents = {}
    for name in (TRACES_FILE, FEATURES_FILE):
        entry = manifest.get("files", {}).get(name)
        if not (path / name).is_file() or entry is None:
            raise AscamError(f"{name} or its manifest checksum is missing")
        contents[name] = (path / name).read_bytes()
        if _sha256(contents[name]) != entry.get("sha256"):
            raise AscamError(f"checksum mismatch for {name}: the file changed after "
                             "generation")
    traces = _load_npz(contents[TRACES_FILE], TRACES_FILE).get("traces")
    if traces is None:
        raise AscamError(f"{TRACES_FILE} has no 'traces' member")
    features = _decode_columns(_load_npz(contents[FEATURES_FILE], FEATURES_FILE))
    dataset = Dataset(manifest, features, traces, origin="file", manifest_sha256=_sha256(raw))
    dataset.validation = {"checksums": "verified (SHA-256)", **validate(dataset)}
    return dataset


def synthesize_in_memory(spec: GenerateSpec) -> Dataset:
    """Synthesize without writing; the identity matches ``generate`` with the same spec."""
    dataset = synthesize(spec)
    files = encode_dataset(dataset)
    dataset.manifest = json.loads(files[MANIFEST_FILE].decode("utf-8"))
    dataset.manifest_sha256 = _sha256(files[MANIFEST_FILE])
    dataset.origin = "synthesized in memory by ascam evaluate"
    dataset.validation = {"checksums": "computed in memory, not written",
                          **validate(dataset)}
    return dataset
