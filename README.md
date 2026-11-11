# Adaptive Spectral Camouflage for Mixed-Signal Side Channels

This project studies a defensive question:

> Can an embedded device adapt its clocking and dummy-current activity so that an
> RF/power observer learns less, while the device still meets energy and latency
> limits?

The proposed system treats defense and observation as a Bayesian Stackelberg
game. The defender commits to a randomized mixed-signal policy. An adaptive
observer then chooses a measurement band, trace budget, and signal-processing
strategy. The central output is not merely an implementation: it is a formal
model, equilibrium analysis, leakage bounds, reproducible simulation, and
controlled validation on hardware owned by the researcher.

## Why this project

It deliberately joins four areas:

- RF measurement: spectrum selection, near-field EM capture, filtering, SNR.
- Mixed-signal design: clock/frequency modes, switching current, PDN coupling,
  dummy loads, power and timing overhead.
- Probability and optimization: Bayesian inference, mutual information,
  hypothesis testing, convex programs, robust optimization.
- Hardware security: measurement-driven leakage assessment and defensive
  countermeasures.

The practical example is an owned BLE/IoT sensor or access-control prototype.
No experiment targets a third-party device, network, or deployed product.

## Contribution hypothesis, not a novelty claim

Random clocks, voltage/frequency variation, dummy activity, noise injection,
EM masking, and game-theoretic timing defenses already exist. The research
hypothesis is narrower:

1. jointly choose a stochastic spectral/power defense under explicit energy,
   latency, and false-alarm costs;
2. model an adaptive physical observer rather than a fixed classifier;
3. derive equilibrium and information-leakage guarantees; and
4. test whether the game-derived policy outperforms fixed and random baselines.

“First” or “novel” must not appear in a paper abstract until the literature and
patent review in `literature/novelty-search-log.md` is completed and checked by
an advisor.

## Current results (honest status)

The first full study has run. The headline question, does a committed randomized
defense beat the best fixed defense and a non-strategic optimizer against an
adaptive observer, is **partially supported**, not a clean win.

- On a synthetic four-band model, mixing strictly beats both the best fixed
  defense and the nominal optimizer at 28 of 400 tested regimes (7 after the
  strict Bonferroni correction), by about 3 to 8 percent of loss.
- It helps only when the observer's bands are separable, the leakage is
  non-trivial, overhead is moderately priced, and most observers actually adapt.
  When bands are inseparable, or in the original scalar model, the best policy is
  a single fixed defense and the advantage is exactly zero.
- The large apparent advantage over the non-strategic optimizer mostly comes from
  that optimizer assuming a naive uniform observer. A mildly robust optimizer
  recovers the best fixed defense, so the honest advantage is the small 3 to 8
  percent number, not the larger one.
- Two elementary results are proved: a single effective observer action, or a
  convex loss, each forces a pure optimal defense. The positive value of mixing
  is a numerical finding checked against exact quadrature and a 36,402-row
  library, not yet a theorem.

Full numbers, confidence intervals, caveats, and five figures are in
[`software/results/VALUE_OF_GAME_RESULTS.md`](software/results/VALUE_OF_GAME_RESULTS.md).
The practical next step is to measure band separability on real hardware, since
that single parameter decides whether the effect exists at all.

## Architecture

```text
secret-dependent workload
        |
        v
device + mixed-signal defense ---- energy / latency / alarm cost
        |
        +---- conducted power trace
        +---- near-field EM trace
                         |
                         v
adaptive observer: band + filter + trace allocation
                         |
                         v
 leakage metrics: TVLA, MI, guessing entropy, success probability
```

A second, parallel track supplies the data volume that the statistics require.
Instead of hand-written synthetic traces, a small AES or synthetic switching
kernel in Verilog/SystemVerilog is simulated (`iverilog`/Verilator), its
per-cycle switching activity is extracted from VCD, and that activity is pushed
through the same mixed-signal channel model to yield 10k to 1M labeled traces:

```text
RTL kernel (+ clock gating, frequency hopping, dummy bank, LFSR/CSPRNG)
        |
        v
iverilog / Verilator  ->  VCD / SAIF  ->  per-cycle switching activity Q[k]
        |
        +---- optional Yosys -> Sky130 gate-level netlist (glitch fidelity)
        |
        v
mixed-signal channel model (PDN, pulse shape, RF mixing, noise)
        |
        v
chunked dataset (Zarr traces + Parquet features) -> hierarchical statistics
```

Switching activity from simulation is a **proxy** for current demand, not a
measurement of silicon EM leakage. It is calibrated against hardware only at the
optional FPGA gate, and every claim derived from it is labeled accordingly. See
`theory/high-volume-data-and-digital-circuit-extension.md`.

## Stage gates

This is a summary. The authoritative list is the twelve stages (Stage 0 to
Stage 11) in `research-project-master-plan.txt`; the matching stage numbers are
in parentheses.

1. **Reproduction (Stages 0 to 2):** generate a trace model and reproduce
   no-defense, fixed-noise, and random-frequency baselines.
2. **Finite game (Stage 3):** solve and independently verify a zero-sum matrix
   game.
3. **Bayesian commitment (Stage 4):** add observer types and solve the
   Stackelberg policy.
4. **Theory (Stage 5):** prove only claims whose assumptions are explicit and
   tested.
5. **Trace replay (Stage 6):** evaluate on public or researcher-owned captures.
6. **Bench validation (Stages 7 to 10):** proceed only if simulation predicts a
   measurable effect.
7. **Paper package (Stage 11):** freeze code, seeds, figures, proof status, and
   limitations.

Digital-circuit track (master plan Stage 2D), running in parallel from gate 1
onward. Its phases are
labeled R0 to R4 so they do not collide with the defender actions D0 to D3:

- **R0 Toolchain and DUT:** RTL kernel simulates; per-cycle switching activity
  reproduces a known ground-truth leakage model.
- **R1 First 10k traces:** at least 10,000 traces over at least 30 independent
  sessions, grouped splits, bootstrap/MI/hierarchical analysis, null
  calibration passes.
- **R2 Gate level:** Yosys/Sky130 netlist with timing; test whether the
  behavioral ordering of defenses survives glitch-accurate simulation.
- **R3 Scale to 100k and beyond:** demonstrate estimator convergence and produce a
  payoff matrix whose per-cell intervals are narrow enough to separate actions.
- **R4 FPGA calibration (optional, gated):** regress measured supply current
  against simulated activity to quantify how good the proxy is.

## Repository map

- `research-project-master-plan.txt`: start here after a long break.
- `theory/model-and-proof-roadmap.md`: notation, mathematical model, theorem work.
- `theory/high-volume-data-and-digital-circuit-extension.md`: RTL/FPGA trace
  factory, dataset schema and storage, and the statistical plan for 10k to 1M
  traces.
- `literature/novelty-search-log.md`: prior art and search protocol.
- `experiments/simulation-and-bench-plan.md`: measurements and stage gates.
- `paper/paper-outline.md`: claims, figures, venue strategy, reproducibility.
- `software/`: executable reference simulator and tests.
- `docs/public-tool-roadmap.md`: CLI/API shape, data schema, extension points,
  versioning, and release criteria for the public tool.
- `CLAUDE.md`: instructions for an AI coding assistant, including writing rules.
- `private/`: personal planning notes (schedules, shopping lists, abandoned
  claims). Gitignored, so it stays local.
- `LICENSE`: MIT.

## The tool

The research is meant to produce a small, reusable tool, not only a paper.

**What it does.** It evaluates adaptive mixed-signal side-channel defenses
(clock gating, frequency hopping/DVFS, dummy switching, injected noise) against
adaptive observers (band choice, filtering, trace budget). It takes a labeled
trace dataset, estimates a payoff matrix of leakage plus overhead with
confidence intervals, solves the defender/observer game, and reports the
recommended randomized defense together with how stable that recommendation is.
Datasets come first from large synthetic RTL/VCD simulations, and later from
measured traces of hardware the user owns.

**Who it is for.** Students learning side-channel evaluation, researchers
comparing countermeasures, and hardware designers checking their own designs or
devices they are authorized to test, before tape-out or before buying bench
equipment.

**What it does not do.** It does not attack third-party devices, recover keys
from products, provide exploit or capture workflows for systems you do not own,
increase RF range, or evade monitoring. Key-ranking metrics (guessing entropy,
success rate) exist only to score defenses on synthetic keys. A low leakage score
from this tool is not a security certification.

**Input/output contract.**

| | Contents |
|---|---|
| Input: dataset | `manifest.json` (version, seeds, tool versions, checksums), `traces.zarr` (N x T array), `features.parquet` (one row per trace: labels, defense/observer action, session/netlist/PVT/key groups, split) |
| Input: config | JSON/YAML listing defenses, observers, estimator, cost weights, bootstrap count, stopping rule, master seed |
| Output: results | JSON with payoff matrix and per-cell intervals, equilibrium value interval, mixed strategy with per-action support stability, primal-dual gap, solver status, N and G (sessions), full provenance |
| Output: figures | regenerated from the results JSON only, never hand-edited |

**Example.** Today the reference simulator runs as shown in the next section.
The planned CLI (working name `ascam`, see `docs/public-tool-roadmap.md`) will
look like:

```powershell
ascam generate --dut synth_kernel --traces 10000 --sessions 30 --seed 126 --out data/p1
ascam evaluate --data data/p1 --config configs/d0-d3_a0-a3.yaml --out results/p1.json
ascam report --results results/p1.json --out figures/p1
```

**Reproducibility expectations.** Same dataset version, config, master seed, and
tool version must give bit-identical results JSON. Every result records N, G,
estimator, interval method, number of tests, and the proxy caveat for simulated
data. Splits are by key/session/netlist/PVT, never by random trace.

**License.** MIT (see `LICENSE`). Third-party RTL cores and datasets keep their
own licenses, which must be recorded in each dataset manifest.

**Roadmap.** Reference simulator (now) -> RTL/VCD dataset generator with the
documented schema -> `ascam` CLI plus importable Python library with stable
schema -> example dataset, CITATION.cff, CI, and v1.0 release -> importer for
measured traces from owned hardware. Details and release gates are in
`docs/public-tool-roadmap.md`.

## Quick software start

```powershell
cd software
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest
python -m src.run_experiment --seed 126 --output results/baseline.json
```

The first simulator is intentionally small. It is a correctness scaffold, not
evidence for publication. Publication-quality results require calibrated channel
models, confidence intervals, adaptive baselines, and independent review.

## Success criteria

A strong result must include all of the following:

- a game formulation that changes the selected defense relative to a
  non-adaptive optimizer;
- at least one proved equilibrium, convergence, or leakage result;
- an adaptive-observer baseline;
- statistically sound leakage and cost measurements;
- a reproducible artifact and honest negative results;
- a trace dataset large enough that the estimators used are not bias-dominated
  (at least 10,000 traces to start, scaling to 100k and beyond), with the number
  of independent sessions reported next to the number of traces;
- defense overheads taken from synthesis timing/power reports rather than
  assumed constants;
- equilibrium results reported as distributions with support stability, not as
  point estimates of an estimated payoff matrix.

If the game adds no measurable value over robust convex optimization, that is a
valid negative result and the framing should change rather than forcing a claim.

