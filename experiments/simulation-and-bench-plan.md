# Simulation and bench plan

This document defines the safe, staged experimental program for *Adaptive
Spectral Camouflage for Mixed-Signal Side Channels*. It turns the model in
`theory/model-and-proof-roadmap.md` and the twelve stages in
`research-project-master-plan.txt` into concrete, reproducible experiments with
explicit variables, metrics, baselines, statistics, pass/fail gates, and
figures.

It is written to be **beginner-friendly but rigorous**: each stage explains the
intuition first, then the exact procedure. Read it top to bottom once, then use
each stage section as a checklist while running experiments.

> Scope reminder. Every experiment here is **defensive** and limited to
> synthetic data or hardware the researcher owns or is explicitly authorized to
> test. See [Section 9 (Safety and ethics)](#9-safety-and-ethics). Hardware
> stages are *optional* and gated behind simulation evidence.

---

## 0. How to use this document

- **Notation is inherited.** Symbols (\(S, X, d, a, \theta, Y, H_a, L, B_d,
  N_d, W, \ell_\theta, J_D, U_A, \lambda_E, \lambda_L, \lambda_F\)) and the
  defender/observer action sets (D0–D3, A0–A3) are defined in
  `theory/model-and-proof-roadmap.md` and `research-project-master-plan.txt`.
  Do not redefine them differently here.
- **Software is specified separately.** The reference simulator lives in
  `software/` and is run from that directory as:

  ```powershell
  python -m src.run_experiment --seed 126 --output results/baseline.json
  ```

  This plan specifies *what* to run and *what to log*, not the internal code.
  Treat `software/` as a black box with a JSON config/result contract.
- **Large synthetic datasets.** The RTL/VCD trace factory, dataset schema, and
  statistics for 10k to 1M traces are in
  `theory/high-volume-data-and-digital-circuit-extension.md`; the public tool
  contract is in `docs/public-tool-roadmap.md`.
- **Experiment ID convention** (from master plan Stage 0):
  `YYYYMMDD_model_defense_observer_seed`, e.g.
  `20261101_zerosum_D3_A3_126`. Every run writes a JSON config/result file named
  by its ID. Figures are regenerated from those files, never hand-edited.
- **Three experiment classes.** Keep them separate and never reuse data across
  them without re-splitting:
  1. **Exploratory**: look for effects, tune ranges. Results are never quoted
     as evidence.
  2. **Calibration**: fit estimator bias corrections, pick observer filters,
     set thresholds. Uses its own split.
  3. **Confirmatory**: the preregistered run that produces reported numbers.
     Primary metric and analysis are frozen *before* this run.

---

## 1. Measurement stack overview (what the whole program produces)

The program proceeds through three environments with increasing realism and
cost. Each environment answers a different question and has an explicit gate
before the next:

| Env | Stages | Question | Data source | Gate to proceed |
|-----|--------|----------|-------------|-----------------|
| **A. Synthetic simulation** | S1–S5 | Does the game change the optimal defense and beat fixed/random/robust baselines *in a model we fully control*? | Generated traces from the channel model | Game policy measurably beats best non-adaptive baseline vs. an adaptive observer, with CIs |
| **B. Trace replay** | S6 | Does the effect survive on *real recorded traces* (public datasets or owned captures), split by capture session? | Public SCA datasets and/or owned synthetic-firmware captures | Effect persists under session-split; raw-data checksum + repeatable table |
| **C. Owned hardware** | S8–S10 | Does the effect survive on *live owned hardware*, conducted power first, then optional near-field EM? | Owned MCU board with synthetic firmware | Preregistered primary metric CI excludes "no effect"; ablations isolate the cause |

Stages S0, S7, and S11 are environment/decision/freeze stages (setup, bench
go/no-go review, and paper artifact freeze). Stage numbering matches the master
plan's "Twelve Stages."

The common metrics computed in every environment are defined once in
[Section 2](#2-metrics-definitions-estimators-and-pitfalls) and the common
baselines in [Section 3](#3-baselines). Statistical design is in
[Section 4](#4-statistical-design).

---

## 2. Metrics: definitions, estimators, and pitfalls

All metrics are functions of a **feature** \(Z = Z_{d,a}\) derived from the
trace \(Y = H_a L(S,X) + B_d(X) + N_d + W\). State which feature (raw sample,
Welch PSD bin, filtered envelope, template projection) every metric uses. Never
mix incompatible features silently.

Leakage metrics measure *how much the observer can learn*; cost metrics measure
*what the defense pays*. A result is only interesting as a **(leakage, cost)
pair**, i.e., a point on a Pareto frontier.

### 2.1 Leakage / attack-strength metrics

**TVLA (Test Vector Leakage Assessment): Welch t-test.**
- *Intuition:* split traces into two groups (fixed-vs-random, or secret bit = 0
  vs 1); if their means differ at some time/frequency point, the trace leaks.
- *Statistic:* at each sample/bin, \(t = (\bar z_0 - \bar z_1)/\sqrt{s_0^2/n_0 +
  s_1^2/n_1}\).
- *Convention:* \(|t| > 4.5\) is an **engineering screening threshold**, not a
  proof of security (master plan Section 6). Report it as a screen only.
- *Pitfall:* testing many points inflates false positives; apply multiple-
  comparison control (Section 4.4). Record the number of points tested.

**Mutual information \(I(S;Z)\) with estimator-bias calibration.**
- *Intuition:* how many bits about the secret are present in the feature.
  \(I(S;Z) = \sum p(s,z)\log_2\frac{p(s,z)}{p(s)p(z)}\) (as in the roadmap).
- *Estimators to use and compare:* histogram/binning plug-in; k-NN
  (Kraskov–Stögbauer–Grassberger, KSG) for continuous \(Z\); optionally a
  Gaussian-assumption estimator as a sanity check when \(Z\) is near-Gaussian.
- *Bias calibration (mandatory):* MI estimators are biased, especially plug-in
  with finite samples. For **every** reported MI:
  1. Run the estimator on **shuffled** data (secret labels permuted) to get the
     null/bias floor; subtract or report alongside.
  2. Report MI vs. sample size \(n\) (a convergence curve) to show the estimate
     has stabilized.
  3. Validate on a **synthetic Gaussian** case with known closed-form MI,
     \(I = \tfrac12\log_2(1+\mathrm{SNR})\) for the scalar Gaussian channel, and
     report estimator error there.
- *Reporting:* always state estimator, bin count / k, sample size, and the
  shuffle floor. Never report a single MI number alone.

**Guessing entropy (GE).**
- *Intuition:* run an attack (correlation/template/ML) that ranks the \(m\)
  secret hypotheses; GE is the *average rank of the true secret* over repeated
  attacks. GE = 1 means the true secret is almost always ranked first (bad for
  the defender); GE near \(m/2\) means the attack is near-random.
- *Report:* GE vs. number of attack traces (a decreasing curve), with CIs over
  independent attack repetitions.

**Success rate (SR) / attack success probability.**
- *Intuition:* probability the attack's top guess is correct, as a function of
  trace budget.
- *Report:* SR vs. traces, with CIs. A **failed attack is not evidence of no
  leakage** (master plan Section 6); SR is an upper-bound-ish witness of
  exploitability by *this* attack, nothing more.

> Relation to theory. Measured/upper-bounded \(I(S;Z)\) feeds the Fano-based
> bound (Target T3): \(H(S|Z)\le h_2(P_e)+P_e\log_2(m-1)\) with
> \(H(S|Z)=\log_2 m - I(S;Z)\). The experiments provide the empirical \(I\) and
> the empirical \(P_e\) (= 1 − SR) so looseness of the bound can be plotted.

### 2.2 Cost metrics (the "overhead" axis)

**Energy.** Normalized energy overhead \(\bar E_d\) relative to the no-defense
baseline D0. In simulation: integral of modeled instantaneous power over the
operation. On hardware: measured from the shunt trace (∫ V·I dt), **not**
estimated from instruction counts (master plan Stage 8).

**Latency.** Normalized added latency \(\bar T_d\) (extra cycles / wall time) vs.
D0. In simulation it is the modeled operation length; on hardware it is measured
between GPIO trigger edges.

**False-alarm rate.** \(\bar F_d\): rate at which the defense's own
detector/monitor (if the policy includes a detect-and-react component) fires on
benign activity. Track separately from missed-detection rate.

All three are combined in the defender loss with prices \(\lambda_E,
\lambda_L, \lambda_F\):
\[
J_D = \text{leakage} + \lambda_E \bar E_d + \lambda_L \bar T_d + \lambda_F \bar F_d .
\]
Always record the **reference values** used to normalize (what counts as energy
= 1, latency = 1). Dimensionless numbers without their reference are
meaningless (master plan Section 2).

### 2.3 Observer cost (attacker side)

The observer utility \(U_A = \text{leakage\_or\_success} - c_\text{trace}\cdot
\text{traces} - c_\text{band}\cdot\text{bandwidth}\). Log the trace budget and
bandwidth used by each observer action so \(U_A\) is reconstructable.

---

## 3. Baselines

Every confirmatory comparison must include **all** of the following, evaluated
against the **same adaptive observer** unless stated. The proposed game policy
(D3-type stochastic policy / Bayesian Stackelberg policy) must be compared to
each:

| ID | Baseline | What it represents | Why it is here |
|----|----------|--------------------|----------------|
| **B0** | **No defense (D0)** | Raw leakage floor | Shows maximum exploitable leakage; anchors overhead = 0 |
| **B1** | **Fixed noise / dummy load (D1)** | Classic "hiding" with constant injected activity | The simplest countermeasure; often filterable |
| **B2** | **Random frequency (D2)** | Open-loop clock/frequency randomization (random DVFS-style) | Established countermeasure; test whether an adaptive observer filters it |
| **B3** | **MI-optimal noise injection** | Noise allocation that minimizes \(I(S;Z)\) against a *fixed* observer, no strategic follower | Represents "optimization-only" prior art (e.g. optimal-noise / MI-minimization) |
| **B4** | **Robust convex optimization (no strategic follower)** | \(\min_d \mathbb E_{\text{fixed channel}}\ell(d)\) or its robust counterpart over a channel-uncertainty set | The key comparator from roadmap Section 9; if the game ties this, the game adds no value |
| **B5** | **Adaptive observer** | *Not a defense*: the strongest observer the program models (band + filter + trace allocation, A3-type, calibrated) | The yardstick all defenses are measured against |

Decision rule (preregistered): the game earns its framing **only** if, against
B5, the game policy beats the best of {B1, B2, B3, B4} on the primary metric by
more than the CI width. If it merely ties B4 (robust convex), that is a **valid
negative result**: report it and reframe, per master plan Section 7
(stop/pivot rules).

---

## 4. Statistical design (applies to all environments)

### 4.1 Seeds and repetitions
- Every run records its RNG seed in the result JSON.
- Minimum **30 independent seeds** per confirmatory condition (master plan
  Stage 2 exit). Increase until the CI is tight enough to resolve the expected
  effect.
- Seeds for exploratory, calibration, and confirmatory sets are **disjoint**.

### 4.2 Resampling and confidence intervals
- Report an **effect estimate and a 95% CI**, not just p-values (master plan
  Section 6).
- **Session bootstrap:** when traces within a capture session (or within a
  simulated "session" block) are correlated, resample **whole sessions**, not
  individual traces, to avoid underestimating variance. This is mandatory for
  trace-replay (S6) and hardware (S8–S10) and recommended when simulated traces
  are generated in correlated blocks.
- For paired comparisons (same seed, two defenses), use paired/bootstrap CIs on
  the difference.

### 4.3 Preregistration
- Before each confirmatory run, write a short prereg note (committed to the
  repo) stating: the **primary metric**, the exact conditions compared, the
  decision rule, the planned sample size, and the exclusion criteria. Do not
  change these after seeing confirmatory data.
- **Primary metric (program-level default):** guessing entropy at a fixed trace
  budget against the adaptive observer B5, at a matched energy overhead. Any
  deviation per stage is stated in that stage.

### 4.4 Multiple comparisons
- When screening many time samples or frequency bins (TVLA, MI maps), control
  the family-wise error or FDR (e.g., Bonferroni for small families,
  Benjamini–Hochberg for leakage maps). Record the number of tests.
- When comparing many defenses/observers, correct across the comparison family
  or declare a single primary comparison and treat the rest as secondary.

### 4.5 Equilibrium-value confidence (links to Target T5)
- Payoff-matrix entries \(\widehat M_{da}\) are Monte-Carlo estimates. Report a
  sup-norm confidence set \(\|M-\widehat M\|_\infty \le \epsilon\) (Hoeffding +
  union bound over \(DA\) cells for a bounded per-run statistic), then the game
  value CI follows from the Lipschitz result \(|v(M)-v(\widehat M)|\le\epsilon\).
  Use session bootstrap for the real trace statistic.

---

## 5. Environment A: Synthetic simulation (Stages S0–S5)

**Purpose.** In a model we fully control, establish that (a) the leakage
machinery behaves as theory predicts, (b) an adaptive observer defeats naive
defenses, (c) a finite game can be solved and verified, (d) the Bayesian
Stackelberg policy is computable and robust, and (e) the game policy beats all
baselines. This is the gate for spending any money on hardware.

### Stage S0: Environment and discipline
- **Objective:** reproducible setup; result/figure pipeline works end to end.
- **Setup:** Python env from `software/requirements.txt`; run `python -m pytest`
  and the quick-start command above.
- **Variables to log:** OS, Python version, package versions (freeze), git
  commit of `software/`, seed.
- **Procedure:** run the provided baseline experiment; confirm a JSON result is
  written and a figure regenerates from it.
- **Metrics:** none (infrastructure only).
- **Pass/fail gate:** clean setup reproduces on a second machine from
  `requirements.txt` + README; a run writes a well-formed result JSON.
- **Expected figure:** none (or a trivial smoke-test plot).

### Stage S1: Signals refresher and synthetic leakage
- **Objective:** confirm the channel model leaks as designed and that estimators
  behave.
- **Setup:** generate traces with a known secret-dependent mean shift under the
  model \(Y = H_a L(S,X) + B_d + N_d + W\); start with D0 (no defense) and a
  trivial observer.
- **Variables/config to log:** secret alphabet size \(m\); number of traces
  \(n\); leakage amplitude; measurement gain \(H_a\) (the \(\alpha(a)\) scale);
  injected-noise variance for \(N_d\); ambient-noise variance for \(W\);
  sampling rate; PSD window and length; seed.
- **Procedure:** plot time waveform, Welch PSD, spectrogram, and filter
  responses. Compute Welch \(t\) and histogram + KSG MI. Sweep gain \(\alpha\)
  up and injected-noise variance up.
- **Metrics:** TVLA \(t\); MI (with shuffle floor and the Gaussian closed-form
  check \(I=\tfrac12\log_2(1+\mathrm{SNR})\)); SNR.
- **Baselines:** D0 only (this stage validates the instrument, not a defense).
- **Statistical design:** ≥30 seeds; show MI-vs-\(n\) convergence and the
  shuffle floor.
- **Pass/fail gate:** unit tests pass; **leakage rises with \(\alpha\)** and
  **falls with injected Gaussian noise**, matching analytic expectation; MI
  estimator matches the Gaussian closed form within stated tolerance.
- **Expected figures:** (F-S1a) PSD/spectrogram of a leaking trace; (F-S1b) MI
  and TVLA vs. SNR with the analytic curve overlaid; (F-S1c) MI-vs-\(n\)
  convergence with shuffle floor.

### Stage S2: Fixed baselines and the "filtering" failure case
- **Objective:** demonstrate the core motivation: a fixed/random defense looks
  good against a fixed observer but loses advantage once the observer adapts
  (selects band / filters).
- **Setup:** implement B0 (D0), B1 (fixed noise/dummy, D1), B2 (random
  frequency, D2). Add an **adaptive observer** (A3-type) that, after a
  calibration split, selects the best band and high-pass/whitening filter.
- **Variables/config to log:** defense parameters for D1/D2 (noise level,
  frequency set and switching rate); observer calibration budget; chosen
  band/filter per run; trace budget; seed.
- **Procedure:** evaluate each defense against (i) a *fixed* observer (A0/A1)
  and (ii) the *adaptive* observer (A3). Use disjoint calibration vs. evaluation
  splits.
- **Metrics:** MI, GE, SR, TVLA; energy and latency overhead of each defense.
- **Baselines:** B0, B1, B2 (B3/B4 appear from S5 on).
- **Statistical design:** ≥30 seeds; paired CIs on (fixed-observer vs
  adaptive-observer) leakage per defense; session-block bootstrap if traces are
  generated in blocks.
- **Pass/fail gate:** CIs from ≥30 seeds show the **advantage of B1/B2 shrinks
  significantly** when moving from fixed to adaptive observer (the motivating
  phenomenon). If it does not, the premise is weak; document and reconsider.
- **Expected figures:** (F-S2a) leakage of each defense under fixed vs adaptive
  observer, with CIs; (F-S2b) chosen band/filter histogram showing the observer
  adapting.

### Stage S3: Finite zero-sum game (links to Result F1)
- **Objective:** estimate a payoff matrix, solve the minimax game both ways, and
  verify numerically against theory.
- **Setup:** fix small action sets \(\mathcal D=\{D0..D3\}\),
  \(\mathcal A=\{A0..A3\}\). Estimate \(\widehat M_{da}\) from held-out Monte
  Carlo runs (the per-run statistic must be the bounded loss used for T5).
- **Variables/config to log:** \(\widehat M\) and its per-cell sample count and
  variance; solver status; primal \(p\), dual \(q\), value \(v\); residuals.
- **Procedure:** solve defender LP \(\min_{p,v} v\) s.t. \(M^\top p\le v\mathbf
  1,\ \mathbf1^\top p=1,\ p\ge0\) and observer dual
  \(\max_{q,u} u\) s.t. \(Mq\ge u\mathbf1,\ \mathbf1^\top q=1,\ q\ge0\)
  (`scipy.optimize.linprog`). Check primal–dual gap. Enumerate pure strategies
  to see whether mixing strictly helps. Cross-check against a hand-solvable
  \(2\times2\) sub-game.
- **Metrics:** game value \(v\); primal–dual gap; constraint residuals;
  probability-simplex validity.
- **Baselines:** pure-strategy defenses vs. the mixed equilibrium.
- **Statistical design:** bootstrap \(\widehat M\) entries; report \(v\) CI via
  the T5 Lipschitz argument; ≥30 seeds for the matrix estimate.
- **Pass/fail gate:** nonnegative probabilities, unit sums, residuals below
  tolerance, small primal–dual gap, and LP value agrees with the hand-checked
  \(2\times2\) example (Result F1 implementation check).
- **Expected figures:** (F-S3a) payoff-matrix heatmap with CIs; (F-S3b)
  equilibrium mixed strategies \(p^\star, q^\star\); (F-S3c) value vs.
  matrix-estimation sample size with the T5 confidence band.

### Stage S4: Bayesian observer types (Stackelberg commitment)
- **Objective:** solve the defender's commitment against a prior over observer
  types and test robustness to prior misspecification.
- **Setup:** define types \(\theta\): passive band-limited, filtering/template,
  resource-rich. Set prior \(\pi_0\) from stated scenarios (not invented
  precision). Solve the leader commitment with per-type best response
  \(a_\theta^\star(p)\) and **pessimistic tie-breaking** (roadmap Section 4).
- **Variables/config to log:** type definitions and action sets \(\mathcal
  A_\theta\); prior \(\pi_0\); per-type payoff matrices \(M^\theta\); tie-break
  rule; resulting policy \(p^\star\); per-type best responses.
- **Procedure:** for the zero-sum-within-type special case, solve the LP
  \(\min_{p,v_\theta}\sum_\theta\pi_\theta v_\theta\) s.t. \((M^\theta)^\top p\le
  v_\theta\mathbf1\) (Target T2 reference). Then stress the prior over an
  \(\ell_1\) ball \(\mathcal U_\rho=\{\pi:\|\pi-\pi_0\|_1\le\rho\}\) and solve
  the robust policy \(\min_p\max_{\pi\in\mathcal U_\rho}\sum_\theta\pi_\theta
  v_\theta(p)\) (Target T4 reference).
- **Metrics:** Bayesian expected loss; robust (worst-case-over-\(\mathcal
  U_\rho\)) loss; policy support vs. \(\rho\).
- **Baselines:** nominal-prior policy evaluated under misspecified priors; B4
  (robust convex, no strategic follower).
- **Statistical design:** sweep \(\rho\) on a grid; CIs on per-type values;
  report how policy support shifts with \(\rho\).
- **Pass/fail gate:** the committed policy remains useful across the stated
  \(\mathcal U_\rho\) **or fails honestly** (master plan Stage 4 exit). Robust
  value is monotone in \(\rho\) and the robustness/overhead tradeoff is
  interpretable (Target T4).
- **Expected figures:** (F-S4a) Stackelberg policy vs. per-type best responses;
  (F-S4b) robust value and policy support vs. \(\rho\).

### Stage S5: Full comparison against all baselines
- **Objective:** the headline simulation result: does the game policy beat
  every baseline against the adaptive observer on the leakage–overhead frontier?
- **Setup:** fix the adaptive observer B5 (calibrated on its own split).
  Evaluate B0–B4 and the game policy (from S3/S4) on a common held-out
  confirmatory split.
- **Variables/config to log:** all defense configs; observer calibration; prices
  \(\lambda_E,\lambda_L,\lambda_F\) and the sweep grid; normalization references;
  seeds (confirmatory set, disjoint from calibration).
- **Procedure:** preregister the primary metric (default: GE at fixed trace
  budget at matched energy overhead). Sweep the energy/latency prices to trace
  out each method's leakage–overhead frontier. Compare frontiers.
- **Metrics:** MI, GE, SR (primary + secondary), energy, latency, false alarms,
  all with CIs; empirical Fano bound overlay (MI → \(P_e\) bound vs. measured
  \(1-\mathrm{SR}\)).
- **Baselines:** B0, B1, B2, B3, B4, all vs. B5.
- **Statistical design:** ≥30 seeds (more if needed); session/block bootstrap;
  paired CIs on game-minus-best-baseline; multiple-comparison control across the
  baseline family with GE-vs-B4 as the single primary comparison.
- **Pass/fail gate (preregistered):** game policy beats the best of {B1,B2,B3,
  B4} vs. B5 on the primary metric by more than the CI width **at equal or lower
  overhead**. Tie with B4 ⇒ negative result ⇒ reframe (no hardware).
- **Expected figures:** (F-S5a) **leakage-vs-energy Pareto frontier** for all
  methods with uncertainty (this is the portfolio's headline figure); (F-S5b) GE
  vs. traces for game vs. baselines against B5; (F-S5c) Fano bound vs. measured
  success.

---

## 6. Environment B: Trace replay (Stage S6)

**Purpose.** Check that the simulated effect is not an artifact of the synthetic
channel by re-running the *evaluation* pipeline on **real recorded traces**.

- **Objective:** reproduce the leakage comparison on public datasets or
  researcher-owned captures, with a split that cannot leak information across
  near-identical acquisitions.
- **Data sources (legal only):**
  - Public SCA trace datasets that permit research use (e.g., ASCAD-style
    public AES power/EM trace sets and similar openly licensed corpora). Record
    the exact dataset name, version, license, and download checksum.
  - Or captures from **owned** hardware running **synthetic firmware** with
    synthetic keys (produced in Environment C, fed back here for offline
    analysis).
- **Setup:** map dataset traces onto the feature/observer pipeline. Because
  defense actions D1–D3 cannot be retro-applied to a fixed public capture, use
  trace replay primarily to validate the **observer model, leakage estimators,
  and attack strength** on real data, and, where owned multi-mode captures
  exist, to compare defense modes that were actually recorded.
- **Variables/config to log:** dataset name/version/license/checksum;
  preprocessing script and parameters; capture-session identifiers; split
  definition; observer calibration; seeds.
- **Procedure:** **freeze the train/calibration/test split by capture session,
  not by random trace** (master plan Stage 6), to avoid leakage between
  near-identical traces from the same acquisition. Compare fixed vs. adaptive
  observers. Recompute MI (with bias calibration), GE, SR, TVLA.
- **Metrics:** MI, GE, SR, TVLA: same definitions as Section 2; session
  bootstrap CIs.
- **Baselines:** whatever defense modes are present in the recorded data
  (minimum: a no-defense capture vs. any recorded countermeasure); fixed vs.
  adaptive observer always compared.
- **Statistical design:** session-level bootstrap is **mandatory**; report
  effect + 95% CI; multiple-comparison control over leakage maps.
- **Pass/fail gate:** raw-data checksum recorded, preprocessing script produces
  a repeatable table/figure, and the qualitative ordering of observers (adaptive
  ≥ fixed) and any defense comparison **matches the simulation** or the
  discrepancy is explained. (Master plan Stage 6 exit.)
- **Expected figures:** (F-S6a) MI/GE on real traces, fixed vs adaptive
  observer, with session-bootstrap CIs; (F-S6b) leakage map on a real trace with
  multiple-comparison-controlled significance.

---

## 7. Stage S7: Bench go/no-go decision (one review meeting)

Before buying or powering any hardware, hold a documented review. **Proceed to
hardware only if all are true** (master plan Stage 7):

1. The simulated/replayed effect size **exceeds expected instrument noise** for
   the intended capture setup.
2. The defense policy uses controls **actually available** on the chosen board
   (clock/frequency modes, a controllable load, GPIO trigger).
3. A capture setup is **affordable/available** (see equipment list, Section 8).
4. The simulation makes a **clear, falsifiable prediction** for the bench.

If any fails: **publish the theory/simulation honestly or revise the model**.
Do not buy hardware to rescue a null result. Record the decision and rationale.

---

## 8. Environment C: Owned-hardware bench (Stages S8–S10)

> Gated by Stage S7. Conducted-power capture first; **near-field EM only after
> conducted capture works**. All safety rules in Section 9 apply.

### 8.1 Low-cost equipment list and build-vs-buy rationale

Following master plan Section 4 (Build versus Buy). The guiding rule: **buy or
salvage calibrated commodity gear; build only a module that exposes a research
variable no cheap product provides.**

**Buy / borrow (preferred):**

| Item | Role | Rationale (buy) |
|------|------|-----------------|
| Oscilloscope or capture ADC w/ adequate bandwidth + memory depth | Primary conducted-power capture | Calibrated, commodity; building a scope is out of scope and lower quality |
| Current shunt + low-noise diff probe (or current probe) | Conducted-power sensing | Cheap, well-characterized; defines the conducted channel |
| Regulated bench supply | Clean, known supply rail | Stable rail is a confound-control, not a research variable |
| Owned MCU dev board (STM32 / nRF52 / ESP32-class) | Target running synthetic firmware | Already owned/cheap; exposes clock modes + GPIO trigger |
| Near-field H-field probe + LNA | Optional EM stage | Only if EM stage is justified by S7; buy a calibrated probe |
| Cables, attenuators, terminations, shield-box materials | Signal integrity + containment | Commodity; keeps emissions cabled/shielded |
| ChipWhisperer-Lite | Optional capture/trigger/glitch | **Only if** its specific capture/glitch features are actually needed |

**Build (only if gated in):**

| Item | Gate to build |
|------|---------------|
| Small switchable **dummy-load daughterboard** (KiCad) | Only if the owned board's existing loads **cannot** expose controllable load levels needed by defense actions D1/D3. If built, it must expose the *controllable load* research variable. |
| Test firmware, GPIO trigger interface, safe fixture | Always (this is the experiment harness, not commodity hardware) |
| Custom PCB | Only after breadboard/fixture parasitics are characterized **and** repeatable probe placement / current sensing / load switching is impossible with a safe fixture |

**Custom-PCB simulation gate (if a daughterboard is built):** design in KiCad
only when justified; then simulate the load switch and **PDN in LTspice/ngspice**
and include **Bode magnitude/phase and impedance \(Z_\text{PDN}(f)\) plots** plus
test points *before* fabrication. These simulations are a prerequisite, not
decoration.

**Do NOT build** (master plan Section 4): commodity buck converter, charger,
SDR, scope, or VNA; any high-voltage / high-energy fault injector; a custom IC
before the model is validated.

### 8.2 Stage S8: Safe bench prototype (baseline capture)
- **Objective:** a stable, repeatable conducted-power baseline on owned hardware.
- **Setup:** owned MCU board runs synthetic firmware (synthetic AES or a
  synthetic leakage kernel) with **test-harness-generated random keys and
  plaintexts**. GPIO trigger brackets the synthetic operation. Firmware
  implements the defense actions (D0–D3) as selectable modes. Capture conducted
  power via the shunt/scope.
- **Variables/config to log:** board ID and firmware commit; supply voltage;
  clock/frequency mode; shunt value; probe type/location; scope gain, sample
  rate, bandwidth, memory depth, coupling, termination; trigger definition;
  ambient temperature; capture-session ID; synthetic key/plaintext seed.
- **Procedure:** capture baseline D0 traces; verify the trigger is stable and
  there is no unexplained clipping/saturation. Measure **actual energy and
  latency** from the trace (∫V·I dt and trigger-edge timing), not instruction
  estimates.
- **Metrics:** baseline MI/TVLA (sanity), measured energy, measured latency,
  trigger jitter, clipping check.
- **Baselines:** D0 (defines the hardware leakage floor).
- **Statistical design:** multiple capture sessions; session-bootstrap from the
  start; ≥30 seeds/sessions as feasible.
- **Pass/fail gate:** stable trigger, repeatable baseline leakage across
  sessions, no unexplained clipping (master plan Stage 8 exit).
- **Expected figures:** (F-S8a) measured conducted-power trace with trigger
  window; (F-S8b) measured energy/latency distribution across sessions.

### 8.3 Stage S9: Adaptive bench experiment (confirmatory)
- **Objective:** the hardware analogue of S5: does the committed defense policy
  beat baselines against a calibrated adaptive observer on real captures?
- **Setup:** calibrate observer actions (band/filter/trace budget) on **separate**
  calibration traces. **Commit the defender policy before** the held-out
  evaluation (preregistration). Randomize run order to avoid temperature/time
  confounds.
- **Variables/config to log:** everything from S8 **plus** observer calibration
  outputs (chosen band, filter, trace budget), committed policy \(p^\star\), run
  order, per-run environmental readings.
- **Procedure:** for each defense mode, capture evaluation traces in randomized
  order; run the adaptive observer; compute leakage metrics. Keep calibration
  and evaluation captures in different sessions.
- **Metrics:** MI (bias-calibrated), GE, SR, TVLA; measured energy/latency/false
  alarms, all with session-bootstrap CIs.
- **Baselines:** B0, B1, B2, and (where realizable on hardware) a hardware proxy
  for B3/B4, all vs. the adaptive observer B5.
- **Statistical design:** preregistered primary metric + CI; **all exclusions
  logged** with reasons; session bootstrap; randomized order.
- **Pass/fail gate:** preregistered primary-metric CI **excludes "no effect"**
  in the predicted direction; all exclusions logged (master plan Stage 9 exit).
- **Expected figures:** (F-S9a) measured leakage–energy frontier, game vs
  baselines, with CIs (hardware analogue of F-S5a); (F-S9b) GE vs traces on
  hardware.

### 8.4 Stage S10: Ablation and robustness
- **Objective:** identify *which component* of the policy actually creates any
  advantage, and whether it survives distribution shift.
- **Setup:** take the S9 winning configuration and ablate.
- **Variables/config to log:** which component removed; swept price values;
  shifted-channel parameters; unseen-filter definition.
- **Procedure:** remove, one at a time, (i) frequency mixing, (ii) dummy
  activity, (iii) the robust term. Sweep energy and latency prices
  \(\lambda_E,\lambda_L\). Test an **unseen observer filter** and a **shifted
  channel gain** (held-out conditions). Compare against **robust convex
  optimization without a strategic follower (B4)**.
- **Metrics:** change in primary metric per ablation, with CIs; frontier shift
  under price sweeps.
- **Baselines:** full policy vs. each ablated variant; B4.
- **Statistical design:** paired CIs on full-minus-ablated; session bootstrap.
- **Pass/fail gate:** the analysis **isolates exactly which component** produces
  any advantage; if removing the strategic/robust term does not hurt, the game
  framing is not earning its place; report that honestly (master plan Stage 10
  exit; roadmap Section 9).
- **Expected figures:** (F-S10a) ablation bar chart with CIs; (F-S10b) frontier
  under price sweeps; (F-S10c) performance under unseen filter / shifted gain.

---

## 9. Safety and ethics

These are hard constraints, not guidelines (README, CLAUDE.md, master plan
Section 0):

- **Owned or authorized hardware only.** Every physical experiment targets
  hardware the researcher owns or is explicitly authorized to test. **No
  third-party devices, networks, or deployed products.** This project provides
  **no** workflow for extracting secrets from someone else's device, bypassing
  access control, increasing RF range, or evading monitoring.
- **Synthetic secrets only.** Keys and plaintexts are synthetic, generated by
  the test harness. No real credentials.
- **RF containment.** Keep any intentional RF emissions **cabled, shielded (in a
  shield box), or otherwise compliant** with applicable regulations. Near-field
  EM capture stays local and contained.
- **Low-voltage fault testing only, with supervision.** Any fault/glitch testing
  is low-voltage/low-energy, **only with appropriate supervision**, and only if
  genuinely required by the model. **No high-voltage / high-energy fault
  injectors** are built or used.
- **Defensive framing.** The deliverable is a defensive countermeasure analysis.
  Attack code exists only as an *evaluation tool* on synthetic/owned data.

---

## 10. Deliverables checklist (what "done" produces)

- Per-stage result JSON files named by experiment ID, each with seed, config,
  software version, and metrics.
- Preregistration notes for every confirmatory run (primary metric, decision
  rule, sample size, exclusions).
- Regenerable figures F-S1a … F-S10c from result files via a single command.
- A data manifest (dataset names, versions, licenses, checksums) for any trace
  replay.
- Honest negative results recorded where gates fail.
- Inputs for the paper's claims-to-evidence matrix in `paper/paper-outline.md`.

---

## 11. Traceability: stages ↔ theory ↔ master plan

| This doc | Master plan stage | Theory target(s) | Primary gate |
|----------|-------------------|------------------|--------------|
| S0 | Stage 0 | none | Reproducible setup |
| S1 | Stage 1 | MI/Fano machinery | Trends match analytic |
| S2 | Stage 2 | motivation (roadmap §9) | Adaptive observer erodes naive defense |
| S3 | Stage 3 | F1, T5 | LP primal–dual + 2×2 check |
| S4 | Stage 4 | T1, T2, T4 | Robust over \(\mathcal U_\rho\) |
| S5 | Stage 5 (parallel) | T3, and comparison §9 | Beats best baseline vs B5 |
| S6 | Stage 6 | T5 (session bootstrap) | Session-split reproducibility |
| S7 | Stage 7 | none | Go/no-go criteria |
| S8 | Stage 8 | none | Stable repeatable baseline |
| S9 | Stage 9 | T3/T5 on real data | Preregistered CI excludes null |
| S10 | Stage 10 | §9 (game vs robust convex) | Component attribution |
| (freeze) | Stage 11 | all | Artifact regenerates results |

If, at any gate, the strategic/game model does not change the optimal defense or
does not beat robust convex optimization (B4), apply the master plan's stop/pivot
rules: reframe as robust optimization or as generic leakage privacy, and report
the negative result rather than forcing a novelty claim.
