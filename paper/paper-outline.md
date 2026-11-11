# Paper outline

Working outline for the eventual write-up of *Adaptive Spectral Camouflage for
Mixed-Signal Side Channels*. It is deliberately conservative: it is a plan for a
paper **if and only if** the evidence in `experiments/simulation-and-bench-plan.md`
and the proofs in `theory/model-and-proof-roadmap.md` materialize. Nothing here
authorizes a novelty claim; see the standing rules in `CLAUDE.md` and
`literature/novelty-search-log.md`.

Notation and terminology follow `theory/model-and-proof-roadmap.md`. Result and
target labels (F1, T1–T5) and stage labels (S0–S11 / Stages 0–11) are reused as
is.

---

## 0. Working title (candidates)

Pick the most honest title that the final evidence supports. Avoid "first,"
"novel," "optimal," and "secure" as unqualified words.

- *"A Bayesian Stackelberg Model for Mixed-Signal Side-Channel Defense Against
  Resource-Bounded Adaptive Observers"* (primary candidate: descriptive, no
  superlatives).
- *"Leakage–Overhead Trade-offs for Adaptive Spectral/Power Side-Channel
  Defenses: A Game-Theoretic Study"* (if the headline is the frontier, not the
  theory).
- *"When Does Strategic Commitment Help a Side-Channel Defense? A Comparison with
  Robust Convex Optimization"* (if the main finding is the comparison, including
  a possible negative result).

---

## 1. Contribution statement (narrow, no "first" claims)

> We study a **Bayesian Stackelberg formulation** in which a resource-constrained
> embedded defender commits to a *stochastic mixed-signal spectral/power policy*
> (clock/frequency modes and dummy-current/noise shaping) under explicit
> **energy, latency, and false-alarm costs**, while a **resource-bounded physical
> observer** best-responds by choosing measurement band, filter, and trace
> budget. We (i) give the model and its finite zero-sum and Bayesian special
> cases with solution methods; (ii) [state proved results among T1–T5: fill in
> only what is actually proved]; and (iii) evaluate, in controlled simulation,
> on replayed traces, and [optionally] on owned hardware, whether the committed
> policy improves the **leakage–overhead frontier** relative to no-defense,
> fixed-noise, random-frequency, MI-optimal-noise, and robust-convex baselines
> against an adaptive observer.

What this contribution is **not** (state plainly in the paper):
- not a claim that game-theoretic side-channel defense is new;
- not a claim that adaptive EM masking / MI-minimizing noise / random DVFS is
  new (these are prior art; see novelty log);
- not a security proof; TVLA/MI/GE/SR are evaluation witnesses, not guarantees.

**Honest fallback contribution.** If the game ties robust convex optimization
(baseline B4), the contribution becomes a **negative/clarifying result**: "under
these conditions, strategic commitment does not improve over robust convex
optimization," which is itself publishable at a workshop and valuable to the
community.

---

## 2. Section-by-section outline

1. **Introduction**
   - Problem: physical (power/EM) side channels on embedded/BLE/IoT devices;
     open-loop countermeasures can be filtered/adapted around.
   - Gap framed as a *question*, not a claim: does modeling the observer as a
     strategic, resource-bounded adapter, and committing to a randomized
     defense, change the right defense and improve the leakage–overhead
     frontier over non-strategic optimization?
   - Contribution bullets (from Section 1), explicitly scoped.
   - Defensive/ethical scope statement (owned/authorized hardware, synthetic
     keys).
2. **Background and related work**
   - Side-channel leakage and evaluation (TVLA, MI, GE, SR).
   - Countermeasures: hiding/masking/shuffling, random clock, random DVFS,
     dummy activity, optimal noise injection / MI minimization.
   - Realistic RF/EM channels (e.g., Screaming Channels / BlueScream) and
     automated probe/band search (SCNIFFER), used to motivate the *adaptive
     observer*, not to reproduce attacks.
   - Game-theoretic security (zero-sum, Bayesian, Stackelberg; timing-defense
     and cloud-allocation games).
   - A **nearest-work table** stating, for each closest paper, what is shared
     and what differs. Drawn from `literature/novelty-search-log.md`.
3. **Threat and system model**
   - Players, secret \(S\in\{1,\dots,m\}\), input \(X\), defender action \(d\),
     observer type \(\theta\), observer action \(a\).
   - Channel \(Y=H_aL(S,X)+B_d(X)+N_d+W\); feature \(Z_{d,a}\).
   - Defender loss \(J_D=\text{leakage}+\lambda_E\bar E_d+\lambda_L\bar
     T_d+\lambda_F\bar F_d\); observer utility \(U_A=\text{leakage\_or\_success}
     -c_\text{trace}\,\text{traces}-c_\text{band}\,\text{bandwidth}\).
   - Resource bounds and assumptions, each with a physical interpretation.
4. **Game formulation and solutions**
   - Finite zero-sum game and the minimax LP / dual (Result **F1**).
   - Bayesian Stackelberg commitment with pessimistic tie-breaking; existence
     (**T1**); zero-sum-within-type LP special case (**T2**).
   - Robustness to the type prior over \(\mathcal U_\rho=\{\pi:\|\pi-\pi_0\|_1\le
     \rho\}\) (**T4**).
5. **Leakage and confidence bounds**
   - Operational leakage bound via Fano/Pinsker (**T3**), with explicit task and
     distributions; honest looseness discussion.
   - Payoff-estimation confidence: sup-norm set \(\|M-\widehat M\|_\infty\le
     \epsilon\) ⇒ value Lipschitz bound \(|v(M)-v(\widehat M)|\le\epsilon\)
     (**T5**); session bootstrap for the trace statistic.
6. **Experimental methodology**
   - Metrics and estimator-bias calibration; baselines B0–B5; statistical
     design (seeds, session bootstrap, CIs, multiple comparisons,
     preregistration). Points to `experiments/simulation-and-bench-plan.md`.
7. **Results**
   - Simulation (Stages S1–S5): motivation (adaptive observer erodes naive
     defenses), game solution, and the leakage–overhead frontier vs. baselines.
   - Trace replay (S6): session-split reproducibility on real traces.
   - [Optional] Hardware (S8–S10): conducted-power (and optional near-field EM)
     confirmation and ablations.
8. **Ablations and robustness** (Stage S10): which component matters; price
   sweeps; unseen filter / shifted gain; comparison to robust convex (B4).
9. **Discussion**: when strategic commitment helps vs. when robust convex
   optimization suffices; practical overhead.
10. **Threats to validity and limitations** (Section 5 below).
11. **Reproducibility** (Section 6 below).
12. **Conclusion**: scoped restatement; explicit open problems (dynamic/MDP
    extension is future work, not claimed).
13. **Ethics statement**: defensive scope, owned/authorized hardware,
    synthetic keys, RF containment, low-voltage supervised fault testing only.

---

## 3. Claims-to-evidence matrix

Fill `Status` honestly using the roadmap vocabulary (**proved / proof sketch /
conjecture / falsified** for theory; **supported / partial / not-yet-run /
refuted** for experiments). A claim may appear in the paper **only** when its
status is strong enough and it links to specific evidence. At project state, the
theory targets are not yet proved and experiments not yet run.

| # | Claim (as it would appear) | Evidence (theorem / experiment) | Status (fill in) |
|---|----------------------------|---------------------------------|------------------|
| C1 | The finite zero-sum defense game has a mixed equilibrium computable by LP; our primal/dual agree. | **F1** + Stage S3 (LP primal–dual gap, 2×2 hand-check) | F1 proved (standard); S3 not-yet-run |
| C2 | The Bayesian Stackelberg defender problem admits a solution (existence) under finite actions. | **T1** | proof sketch |
| C3 | The zero-sum-within-type case reduces to a tractable LP over \(p\) and per-type epigraph variables. | **T2** + Stage S4 reference solve | conjecture pending exact utilities |
| C4 | An operational leakage-to-success bound holds for the defended channel (Fano-based). | **T3** + Stage S5 Fano overlay | proof target / not-yet-run |
| C5 | The robust counterpart over \(\mathcal U_\rho\) is a single-level program; robust value is monotone in \(\rho\). | **T4** + Stage S4 \(\rho\)-sweep | proof target / not-yet-run |
| C6 | The estimated game value has a sup-norm/Lipschitz confidence interval. | **T5** + Stages S3/S6 bootstrap | proof target / not-yet-run |
| C7 | Against an adaptive observer, naive fixed/random defenses lose advantage after band selection/filtering. | Stage S2 | not-yet-run |
| C8 | The committed policy improves the leakage–overhead frontier over the best of {fixed, random, MI-optimal noise, robust convex} baselines vs. the adaptive observer. | Stage S5 (sim) done; S6/S9 pending | **partial (sim):** helps in 28/400 regimes (7 after Bonferroni), 3-8%, only when bands separable; largely ties a mildly robust optimizer; see `software/results/VALUE_OF_GAME_RESULTS.md` |
| C9 | Ablations attribute any advantage to specific components (frequency mixing / dummy activity / robust term). | Stage S10 | not-yet-run |
| C10 | [If applicable] Strategic commitment does **not** beat robust convex optimization here (negative result). | Stage S5/S10 comparison to B4 | contingent |

> Rule: never promote a row to "stated as fact" in the paper until Status is
> `proved`/`supported` with a linked artifact. C8 is the paper's make-or-break
> claim; if it is refuted, pivot to C10.

**Update (2026-10-30), from the value-of-game study.** C8 is now partial: not
refuted, not fully supported. The paper should lead with the characterization
("when does commitment help") per title candidate 3, not with a win. Add two
proved elementary results as C11: P1, one effective observer action forces a pure
defense; P2, a convex loss forbids useful mixing (both in
`theory/model-and-proof-roadmap.md` Section 9a). Commitment has value only because
the game is general-sum (shared leakage, private costs); in the zero-sum-within-type
case it is vacuous (Korzhyk et al., JAIR 2011), so soften pure-Stackelberg
language. The strongest original-theory lead is T6: characterize when the
observer's band choice reveals the clock mode (the LP is exact if it does,
conservative if not), with a fused-observer corollary that erases the gap.

---

## 4. Figures, ablations, and baselines

### 4.1 Figure list (regenerated from result files)
- **Fig. 1 (system diagram):** secret → device+defense → conducted/EM traces →
  adaptive observer → leakage metrics. (Portfolio diagram.)
- **Fig. 2 (payoff/equilibrium):** payoff-matrix heatmap + equilibrium mixed
  strategies \(p^\star,q^\star\) (from S3).
- **Fig. 3 (headline Pareto):** **leakage-vs-energy frontier** for all methods with
  uncertainty bands (from S5; hardware analogue from S9). This is the single
  most important figure.
- **Fig. 4 (adaptive-observer motivation):** leakage of fixed/random defenses under
  fixed vs. adaptive observer, with CIs (from S2).
- **Fig. 5 (GE/SR vs traces):** guessing entropy and success rate vs. trace budget,
  game vs. baselines against B5 (from S5/S9).
- **Fig. 6 (bound vs measured):** Fano bound overlaid on measured success (from S5).
- **Fig. 7 (robustness):** robust value and policy support vs. \(\rho\) (from S4).
- **Fig. 8 (ablation):** per-component ablation bar chart with CIs (from S10).
- **Fig. 9 (real-trace/spectrum):** measured or simulated spectrum / leakage map on
  real traces with multiple-comparison control (from S6/S8).

### 4.2 Ablations (Stage S10)
- Remove frequency mixing.
- Remove dummy activity.
- Remove the robust term.
- Sweep \(\lambda_E,\lambda_L\) (and \(\lambda_F\)).
- Test an unseen observer filter and a shifted channel gain.

### 4.3 Baseline comparisons (from experiments Section 3)
- **B0** no defense; **B1** fixed noise/dummy; **B2** random frequency; **B3**
  MI-optimal noise injection (fixed observer, no strategic follower); **B4**
  robust convex optimization (no strategic follower, the key comparator); **B5**
  adaptive observer (the yardstick). The paper must show the game vs. the best
  of {B1,B2,B3,B4} against B5.

---

## 5. Threats to validity and limitations

State these up front; reviewers will raise them regardless.

- **Model vs. reality.** The synthetic channel may not capture real PDN coupling,
  cross-channel EM, or device variability. Trace replay (S6) and hardware
  (S8–S10) mitigate but do not eliminate this.
- **Estimator bias.** MI estimates are biased; conclusions depend on estimator,
  bin/k choice, and sample size. Mitigation: shuffle floor, convergence curves,
  Gaussian closed-form calibration (experiments Section 2.1).
- **Attack strength.** A failed attack is not proof of no leakage; GE/SR reflect
  *this* observer's power. We do not claim security.
- **TVLA as a screen only.** \(|t|>4.5\) is an engineering convention, not a
  guarantee.
- **Session leakage.** Random trace splits can leak across near-identical
  acquisitions; we split by capture session and bootstrap by session.
- **Scope of theory.** T1–T5 assume finite action sets and stated regularity /
  tie-breaking; the dynamic/MDP extension is out of scope.
- **Generalization.** Results are specific to the tested board(s), firmware, and
  observer models; no claim of universal applicability.
- **Possible negative result.** The game may not beat robust convex optimization
  (B4); we report that outcome honestly if it occurs.

---

## 6. Reproducibility checklist

- [ ] Public code with pinned versions (`software/requirements.txt`) and a
      single figure-regeneration command.
- [ ] Fixed seeds recorded in every result JSON; experiment-ID naming
      (`YYYYMMDD_model_defense_observer_seed`).
- [ ] Machine-readable config/result files for every reported number.
- [ ] Preregistration notes for confirmatory runs (primary metric, decision
      rule, sample size, exclusions) committed before the runs.
- [ ] Data manifest for any trace dataset: name, version, license, download
      checksum, preprocessing script.
- [ ] Session-split definition published; session-bootstrap scripts included.
- [ ] Multiple-comparison procedure and number of tests reported.
- [ ] Exact equations match code notation and units.
- [ ] Negative results and excluded runs reported, with reasons.
- [ ] Only safe, legally redistributable data/firmware released; synthetic keys
      only.
- [ ] An independent person can regenerate the main figures from the artifact
      (master plan Stage 11 exit).
- [ ] Large-dataset and public-tool release criteria met
      (`theory/high-volume-data-and-digital-circuit-extension.md` Section 17;
      `docs/public-tool-roadmap.md`).

---

## 7. Venue ladder (realistic, with honest notes)

Match the venue to the **actual** evidence. Do not target a top journal with a
conjecture or weak baselines (master plan Section 7: do not submit if the central
proof is still a conjecture, baselines are weak, or the novelty search reveals the
same model and experiment).

**Tier 1: workshops / conferences (first realistic targets):**
- **COSADE**: constructive side-channel analysis & secure design; a natural fit
  for a well-evaluated countermeasure study, including honest negative results.
- **HOST**: hardware-oriented security & trust; good for the measurement +
  defense framing with owned-hardware results.
- **CARDIS**: smart card / embedded security; fits embedded side-channel work.
- **ISCAS**: circuits & systems; fits the mixed-signal / PDN-modeling angle,
  especially if the KiCad/LTspice daughterboard stage is used.
- *Note:* a solid simulation + trace-replay study with correct baselines and CIs,
  even without a proved headline theorem, can be workshop-appropriate, provided
  claims are scoped and the nearest-work table is honest.

**Tier 2: journals (only with proven theory + strong baselines + hardware):**
- **IEEE TIFS** (Transactions on Information Forensics and Security).
- **IACR TCHES** (Transactions on Cryptographic Hardware and Embedded Systems):
  strong fit, but expects rigorous SCA evaluation and real artifacts.
- **IEEE TCAD** / **IEEE TVLSI**: fit the mixed-signal / design-automation angle
  if the circuit/PDN modeling is substantial.
- **IEEE Access**: faster/broader venue; reasonable if the contribution is solid
  but narrower, or as a fallback.
- *Honest note:* **journal acceptance realistically requires at least one proved
  result among T3/T4/T5 (not a conjecture), strong adaptive-attacker and
  robust-convex baselines, and reproducible measured results.** Per the roadmap,
  "the strongest plausible paper package is T3 or T4 plus T5, not the elementary
  existence result." Without proven theory, aim Tier 1.

**Submission gating rule.** Before submitting anywhere: (1) rerun the novelty
search and update `literature/novelty-search-log.md`; (2) have an advisor
challenge novelty, assumptions, and statistical design; (3) confirm the
claims-to-evidence matrix has no claim above its evidence. Only then choose the
venue tier the evidence actually supports.
