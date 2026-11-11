> **Archived record (simulator 0.2.0, original laptop).** The source code that produced
> these numbers was lost with that laptop; only this document survived. The current code
> (0.3.0) is a rebuild from the project documentation and does not reproduce these numbers
> exactly. See `docs/RECOVERY_NOTES.md` and `software/results/VALUE_OF_GAME_RESULTS.md`.

# Value of the game (claim C8): results

Status: computed. Every number below comes from the confirmatory run (seed 126) recorded in
`results/value_of_game.json`, with all grid points listed in `results/value_of_game_tables.md`.
Regenerate with the commands in `software/RUN_VALUE_STUDY.md`.

**C8 verdict: partially supported.** On this synthetic four-band model, a committed randomized
defense strictly beats the best single fixed defense and the nominal non-strategic optimizer B4
against an adaptive observer. This holds at 28 of 400 grid points (both 95% CIs exclude 0), and at
7 of 400 after Bonferroni correction. The advantage over the best fixed defense is small: 0.006 to
0.042 bits-equivalent of loss per trace, about 3% to 8% of the best fixed defense's loss. It
appears only when leakage is moderate to strong and bands are separable. It is exactly zero when
bands are inseparable. It is not significant in most of the grid.

## 1. Question and decision rule

C8 asks whether a committed mixed defense against an adaptive observer (B5) strictly beats both:

- (a) the best single fixed defense scored against B5 (`gap_pure = L(best pure) - L(game)`), and
- (b) the non-strategic optimizer B4, which minimizes loss under a nominal (uniform) observer and
  is then scored against B5 (`gap_robust = L(B4) - L(game)`).

Loss is `MI + lambda_E E + lambda_L T + lambda_F F`, in bits per trace plus priced overhead. In
the game the observer pays its own action cost, so loss values can be slightly negative when
leakage is near 0.

Decision rule, fixed before the confirmatory seed was run: the game strictly helps at a grid point
only if the cross-fitted 95% session-bootstrap CIs of gap_pure and gap_robust both lie above 0.
Bonferroni flags use the bootstrap SE at alpha / (2m), which gives z = 3.84 for m = 400.

## 2. Method summary

- **Channel.** The four-band model is `Z_b = h_b u_g kappa_{d,b} L(S) + B_{d,b} + N_{d,b} + W_b`.
  - The secret is binary and synthetic.
  - Session gain and noise factors are log-normal (sd 0.15 and 0.10).
  - Separability s spreads injected noise power and hop leakage between "uniform over bands"
    (s = 0) and "band-targeted" (s = 1). The total effect is the same at every s.
  - Hopping moves the narrowband bands A1/A2 out of band with probability 0.75, where they
    couple at 0.15.
  - The observers are A0 conducted-low, A1 clock-fundamental, A2 harmonic, and A3
    adaptive-high-pass. These are the same OBSERVER_ACTIONS (gains, noises, costs) as the
    original scaffold.
- **Defender library.** The library has 212 rows. Rows 0 to 3 are D0 to D3. The rest are
  hop in {off, on} crossed with "no injection" or any 1/4-lattice band allocation at powers
  {0.75, 1.5, 3.0}. Energy is 0.13 hop + 0.2 P, latency is 0.18 hop, and F = 0 (no
  false-alarm model).
- **Observer type models.** There are four:
  - 1 type: adaptive A0 to A3.
  - 2 types: adaptive 0.5 / conducted-A0-only 0.5.
  - 3 types: adaptive 0.5 / conducted 0.25 / EM narrowband A1-A2 0.25.
  - 3 types: adaptive 0.2 / conducted 0.4 / EM narrowband 0.4.
  - The game is the Bayesian Stackelberg epigraph LP. Observer mixtures come from the LP duals.
- **Baselines.** All baselines are scored against B5, which best-responds per type with ties
  broken toward more leakage.
  - B0: no defense.
  - B1: fixed dummy (D1).
  - B2: random frequency (D2).
  - B3: the best noise-only row against an observer frozen at its best response to D0.
  - B4: the nominal uniform-observer optimum. B4_robust is its L1-ball worst case at rho = 0.5.
  - best_baseline: the best of B1 to B4, selected on training data.
- **MI estimation.** MI is estimated from pooled per-session histograms with 16 equal-mass bins.
  The bin edges are frozen from 16 separate calibration sessions, and a Miller-Madow correction
  is applied.
- **Cross-fitting.** In-sample, the game can never lose to its own pure strategies, so in-sample
  gap_pure >= 0 always. To remove that optimism, sessions are split in halves. Policies are fit
  on one half and evaluated against B5 best-responding on the other half (conservative for the
  game). The halves are then swapped and the results averaged.
- **CIs.** Sessions are resampled within halves and everything is refit, B = 1000 times. Intervals
  are percentile, with bias-corrected percentile intervals as a sensitivity check.
- **Exact checks.**
  - (i) Exact binned and continuous MI of the same 212-row library, computed by Gauss-Hermite
    quadrature over session factors (7 points).
  - (ii) A fine library: every 1/12-lattice allocation at 41 powers in [0, 3], with and without
    hop. That is 36,402 distinct rows for s > 0 and 82 at s = 0, where allocations collapse. It
    contains every coarse row, which tests whether the value of mixing is just a missing
    in-between deterministic option.
- **Design.** There are 128 sessions per dataset with 1000 traces per session per cell, so
  128,000 traces per (defense, band) cell, plus calibration. All configs at the same (A, s)
  share one simulated dataset.

## 3. Grid

| Parameter | Values |
|---|---|
| LNR A (leakage amplitude / ambient noise sd) | 0.125, 0.25, 0.5, 1, 2 |
| Separability s | 0, 0.25, 0.5, 0.75, 1 |
| Price multiplier k on (lambda_E, lambda_L) = (0.30, 0.20) | 0.1, 0.3, 1, 3 |
| Observer type model | the four listed above |

There are 5 x 5 x 4 x 4 = 400 grid points. The robust radius is rho = 0.5.

## 4. Headline counts

| Quantity (of 400 grid points) | Count |
|---|---|
| gap_pure CI above 0 | 28 |
| gap_robust CI above 0 | 124 |
| Both CIs above 0 (decision rule) | 28 |
| Both, bias-corrected percentile CIs (sensitivity) | 37 |
| Both, Bonferroni (z = 3.84) | 7 |
| gap_pure CI entirely below 0 | 0 |
| Exact-model gap_pure > 0.002 / > 0.01 | 48 / 16 |
| Exact-model gap_robust > 0.01 | 105 |
| Fine-library exact gap_pure > 0.002 / > 0.01 | 29 / 10 |
| Max exact gap_pure, coarse library / fine library | 0.0508 / 0.0512 |
| Max exact gap_robust (coarse library) | 0.2905 |

All 28 points where gap_pure is significant also have a significant gap_robust. Of those 28,
22 still have a fine-library exact gap_pure above 0.002 and 9 above 0.01. A few shrink a lot
when the best fixed defense gets the finer options. For example, at A = 1, s = 1, k = 3, one
adaptive type, gap_pure goes from 0.0247 to 0.0024. At A = 0.5, s = 0.75, k = 0.3, three types
(adaptive 0.5), it goes from 0.0047 to 0.0001.

## 5. Points that survive Bonferroni

Values are cross-fitted estimates with 95% session-bootstrap CIs, in loss units (bits plus priced
overhead). "Rel." is gap_pure / L(best pure).

| A | s | k | Types | L(game) | L(best pure) | L(B4) | gap_pure | gap_robust | Rel. | Fine exact gap_pure / gap_robust |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.5 | 0.75 | 0.3 | 2 types | 0.1015 [0.0984, 0.1070] | 0.1103 [0.1056, 0.1145] | 0.1203 [0.1135, 0.1324] | 0.0087 [0.0046, 0.0104] | 0.0188 [0.0120, 0.0311] | 7.9% | 0.0043 / 0.0250 |
| 1 | 0.75 | 1 | 1 type | 0.4171 [0.4065, 0.4297] | 0.4406 [0.4287, 0.4531] | 0.5055 [0.4660, 0.5192] | 0.0236 [0.0127, 0.0304] | 0.0884 [0.0488, 0.0931] | 5.3% | 0.0155 / 0.0881 |
| 1 | 1 | 0.3 | 2 types | 0.2800 [0.2706, 0.2921] | 0.2918 [0.2819, 0.3049] | 0.3371 [0.3255, 0.3490] | 0.0118 [0.0079, 0.0172] | 0.0571 [0.0528, 0.0602] | 4.0% | 0.0100 / 0.0419 |
| 1 | 1 | 1 | 1 type | 0.4361 [0.4230, 0.4490] | 0.4740 [0.4638, 0.4848] | 0.5399 [0.5196, 0.6017] | 0.0380 [0.0312, 0.0442] | 0.1038 [0.0808, 0.1703] | 8.0% | 0.0270 / 0.1203 |
| 1 | 1 | 1 | 2 types | 0.4139 [0.4027, 0.4287] | 0.4264 [0.4130, 0.4413] | 0.5406 [0.5038, 0.5772] | 0.0125 [0.0055, 0.0154] | 0.1266 [0.0920, 0.1586] | 2.9% | 0.0037 / 0.1547 |
| 1 | 1 | 3 | 1 type | 0.5682 [0.5525, 0.5867] | 0.5930 [0.5752, 0.6096] | 0.6669 [0.6483, 0.6855] | 0.0247 [0.0157, 0.0295] | 0.0987 [0.0899, 0.1052] | 4.2% | 0.0024 / 0.1133 |
| 2 | 1 | 1 | 1 type | 0.8284 [0.8138, 0.8490] | 0.8702 [0.8541, 0.8914] | 1.0028 [0.9751, 1.0167] | 0.0418 [0.0320, 0.0472] | 0.1744 [0.1427, 0.1908] | 4.8% | 0.0512 / 0.2008 |

### Representative point (A = 0.5, s = 1, k = 1, one adaptive type)

This point was pre-specified before the run. It meets the decision rule but not Bonferroni.

| Method | Loss vs B5 [95% CI] | Leakage, bits [95% CI] | Energy |
|---|---|---|---|
| game (mixed) | 0.1556 [0.1504, 0.1685] | 0.1669 [0.1335, 0.2033] | 0.129 |
| best pure (F-x0103-P0.75) | 0.1626 [0.1556, 0.1745] | 0.1376 [0.1228, 0.1556] | 0.150 |
| B0 no defense | 0.2342 [0.2192, 0.2506] | 0.3142 [0.2992, 0.3306] | 0.000 |
| B1 fixed dummy | 0.3299 [0.3140, 0.3461] | 0.3199 [0.3040, 0.3361] | 0.300 |
| B2 random frequency | 0.3118 [0.2955, 0.3279] | 0.3168 [0.3005, 0.3329] | 0.130 |
| B3 MI-optimal noise vs fixed observer | 0.2156 [0.2067, 0.2250] | 0.1556 [0.1413, 0.1650] | 0.300 |
| B4 non-strategic (nominal) | 0.2342 [0.2036, 0.2458] | 0.3142 [0.2369, 0.3258] | 0.000 |
| B4 robust counterpart (rho = 0.5) | 0.1626 [0.1559, 0.1759] | 0.1376 [0.1234, 0.1636] | 0.150 |

The gaps here are:

- gap_pure = 0.0070 [0.0003, 0.0142]. The in-sample value is 0.0075 and the exact-model value
  is 0.0084.
- gap_robust = 0.0786 [0.0448, 0.0812].
- gap vs the best of B1 to B4 = 0.0600 [0.0307, 0.0613].

The game policy mixes four rows on the full data: D0 0.14, F-x0103-P0.75 0.45, F-x0004-P0.75
0.34, and F-x0013-P0.75 0.06. It accepts more leakage than the best pure defense (0.167 vs 0.138
bits) in exchange for less energy. Under these prices, the game buys loss, not leakage.

### Scaffold check (original 4x4 scalar model, same pipeline)

On the original D0-D3 by A0-A3 model, the equilibrium is pure D3 and gap_pure is 0.0000
[0.0000, 0.0000]. The original `run_experiment` in-sample comparison (game value 0.1831 vs best
pure 0.1852, gap 0.0021, largest cell SE 0.0131) falls inside its Monte Carlo noise. The original
scaffold therefore gives no evidence for C8.

## 6. Where and how much the game helps

- **Separability is necessary.**
  - At s = 0, no grid point is significant, and the exact and fine gap_pure are 0.
  - All 28 significant points have s >= 0.5: 15 at s = 1, 9 at s = 0.75, and 4 at s = 0.5.
  - When noise and hop act the same way on every band, the observer's band choice cannot be
    played against, and a single defense is optimal.
- **Leakage must be non-trivial.**
  - The significant points by A are: 0.25 (1), 0.5 (8), 1 (12), and 2 (7).
  - At A = 0.125, nothing is significant. Every row leaks so little that overhead dominates and
    D0 is optimal.
- **Prices matter.**
  - The significant points by k are: 0.1 (7), 0.3 (12), 1 (8), and 3 (1).
  - At k = 3, energy is expensive enough that the cheap pure defenses usually win.
- **Observer types.**
  - The significant points by type model are: 1 adaptive type (18), 2 types (6), and 3 types with
    adaptive 0.5 (4).
  - There are none with 3 types and adaptive 0.2. When most observers are fixed-band, the
    defender can just target them with one fixed defense.
- **Magnitude.**
  - Where gap_pure is significant, it ranges from about 0.003 to 0.042 per trace, which is 3% to
    8% of the best fixed defense's loss.
  - gap_robust is much larger, reaching about 0.17 at the Bonferroni points and 0.29 in the exact
    model.
  - However, most of gap_robust comes from B4's nominal uniform observer, not from mixing. At the
    representative point, B4 picks D0, while B4's robust counterpart at rho = 0.5 picks the same
    row as best pure.
  - So "beats a robust optimizer" is only as strong as gap_pure once the optimizer is made mildly
    robust.
- **Main-effect variance shares.** For gap_pure: A 0.042, s 0.077, k 0.014, types 0.074. For
  gap_robust: A 0.170, s 0.090, k 0.009, types 0.091.
  - These shares are small, which means the gaps come from interactions. The game helps in a
    corner of high A and high s, not along any single axis.
  - Fig B plots gap_robust on the top-2 axes (A and type model), faceted by s and k.

## 7. Estimator diagnostics (MI bias is real)

- **Plug-in MI bias.** Binned plug-in MI is biased upward at finite N and downward from binning.
  Miller-Madow reduces the first but does not remove it.
  - Against the exact binned MI of the same library, the mean MC error per (A, s) dataset ranges
    from -0.0149 to +0.0072 bits, and the worst single cell is 0.0288 bits.
  - Part of this error is sampling of the realized session factors (diagnosed during
    development: with the realized factors the offset was -0.00006 bits). It is not a coding
    error.
  - Binning loss (continuous minus binned exact MI) is at most 0.065 bits for one cell.
- **Gap estimates vs the exact model.** Fig D plots cross-fitted gap estimates against exact-model
  population gaps for all 400 points. The points sit near y = x. The in-sample estimate is above
  the cross-fitted estimate near ties, which is the optimism that cross-fitting removes.
- **Sign check.** No grid point has a gap_pure CI entirely below 0.
- **Bootstrap coverage.** Percentile bootstrap CIs for argmin-type functionals can under-cover
  near ties.
  - The bias-corrected count (37 vs 28) shows how sensitive the borderline points are.
  - The exact-model and fine-library columns are the independent check, and they are the reason
    the verdict is "partial" rather than "supported".

## 8. Physical plausibility

The value of mixing in this model depends on three things.

1. **The observer commits to one band or filter for many sessions and sees one band at a time.**
   An observer that captures all bands at once, fuses them, or learns the defense mode per trace
   is not modeled.
2. **Separability is high.** Injected noise and hopping must affect bands very differently
   (s >= 0.5). Real injectors and spread-spectrum clocks leak broadband energy, so s near 1 is
   optimistic. Its realistic value is unknown until bench measurement.
3. **Leakage-to-noise is moderate** (A between 0.25 and 2) and energy is priced (k <= 1).

Scoring mixed policies with a linear payoff assumes that the observer identifies the realized mode
in each trace. If the observer cannot, MI is convex in the channel and mixing within a trace hides
more. In that sense the linear payoff is conservative for the defender. A wideband or fused
observer removes the band choice entirely, and P1 below then says a fixed defense is optimal.

## 9. Theory notes

- **P1 (proved, elementary).** Suppose the observer effectively has one action, for example a
  fused observer that sees all bands, or an observer whose action does not depend on the
  defender's policy. Then the defender's loss is linear in p over the simplex, so a vertex (some
  pure defense) is optimal and gap_pure = 0.
  - With several observer actions, the defender minimizes a maximum of linear functions, and that
    minimum can lie strictly inside the simplex. That is the only source of value of mixing here.
  - At s = 0 the observer's actions become payoff-equivalent up to their costs, which is
    consistent with the zero gaps there and in the scaffold.
- **P2 (proved under its assumption).** Suppose the action set is convex and the loss is convex in
  the action for every observer action. Then by Jensen, the deterministic mean action does at
  least as well as any mixture, so mixing cannot help.
  - Binary-input Gaussian MI is convex in noise variance iff s^2 I'(s) is nondecreasing.
  - Numerically, this holds at low SNR and fails near saturation (numerical observation, not
    proved). That failure is consistent with the gap appearing only at moderate-to-high A.
- **Positive value of mixing in this model.** This is a numerical observation with an exact-model
  check, not a theorem. The fine-library result shows that it is not purely a coarse-lattice
  artifact: the max gap_pure stays 0.051, and 29 points remain > 0.002. It is still specific to
  this synthetic channel.

## 10. Figures

All figures were generated by this run in `software/results/figures/`:

- `fig_A_frontier.png`: leakage vs energy frontier at A = 0.5, s in {0.25, 1}, one adaptive type,
  with the price swept from 0.01 to 10 and 95% CI bars and bands.
- `fig_B_gap_robust_heatmap.png`: cross-fitted gap_robust over A x type model, faceted by s and k.
  One star marks the decision rule and two stars mark Bonferroni.
- `fig_B_supp_gap_pure_heatmap.png`: the same layout for gap_pure.
- `fig_C_payoff_equilibrium.png`: the payoff matrix (8 of 212 rows) at the representative point,
  with p*, q*, and cross-fitted support stability.
- `fig_D_validation.png`: cross-fitted and in-sample gap estimates vs the exact model, all 400
  points.

## 11. Seeds, config, versions

- **Seeds.** The confirmatory seed is 126, with per-dataset streams
  `SeedSequence(126, spawn_key=(i_A, i_s))` and the scaffold on `spawn_key=(1000,)`. The
  exploratory pilot used seed 7 and the smoke test used seed 1. Both are disjoint from 126 and
  are not reported. The pilot motivated the sample size of 128 sessions x 1000 traces.
- **Config.**
  - The bootstrap uses B = 1000 with session resampling within cross-fit halves.
  - Histograms use 16 bins, and bin edges come from 16 calibration sessions x 250 traces.
  - Quadrature uses 7 points, rho = 0.5, and the fine library is 12 / 41 / 121 (lattice steps /
    power levels / variance grid).
- **Versions.** Python 3.14.7, NumPy 2.5.4, SciPy 1.18.1 (HiGHS LP), matplotlib 3.11.2, and
  simulator 0.2.0.
- **Runtime.** The main sweep took 2317 s on 8 workers, and the fine phase took about 544 s.
- **Tests.** `python -m pytest` reports 23 passed. These include matching pennies (gap 0.5), a
  saddle (gap 0), and cross-fitting removing in-sample optimism.

## 12. Limitations

- The channel is synthetic, and the four bands, gains, separability, and costs are modeling knobs
  that are not calibrated to any device. There is no false-alarm cost (F = 0).
- MI estimates are biased (section 7). The exact model is a check of the estimator, not of
  reality.
- The linear mixed-policy payoff assumes band commitment and per-trace mode identification.
  Fused, wideband, or learning observers are not modeled.
- B4's nominal observer is uniform. A practitioner using a slightly robust B4 recovers the best
  pure defense, so gap_robust overstates the practical advantage over a sensible non-game
  optimizer.
- Bootstrap CIs can under-cover near ties. A two-sided 95% CI lies entirely above 0 by chance
  about 2.5% of the time, which would be about 10 of 400 points if no point were real. Many
  points are exact ties with degenerate intervals, so the true chance count is lower. The count
  of 28 is therefore informative but not decisive by itself. The exact-model and fine-library
  agreement is what supports a real effect at the high-A, high-s points.
- Low estimated leakage is not a security proof, and an observer failing to extract the secret is
  not evidence of no leakage.

## 13. Resume / paper paragraph

On a synthetic four-band mixed-signal leakage model with an adaptive band-selecting observer, we
tested whether a committed randomized defense (Bayesian Stackelberg equilibrium) beats the best
fixed defense and a non-strategic optimizer. We used cross-fitted, session-bootstrap estimates
over 400 regimes, checked them against exact quadrature MI and a 36,402-row deterministic library.

Mixing helped significantly in 28 of 400 regimes (7 after Bonferroni), all with separable bands
(s >= 0.5) and non-trivial leakage. In those regimes it reduced loss by 3% to 8% (up to 0.042
bits-equivalent per trace; for example, 0.0380 [0.0312, 0.0442] at A = 1, s = 1). The
improvement over a nominal non-strategic optimizer was larger (up to 0.17), but it largely
disappears against a mildly robust optimizer. With inseparable bands, or in the original 4x4
scaffold, the equilibrium was a single fixed defense. We therefore report the value of
randomization as real but regime-limited and small, and we do not claim it as a general
advantage.

## 14. Recommended next step

Measure separability on hardware. Characterize how differently the injector and clock hopping
affect each observer band on a real board, because s is the parameter that decides whether C8
holds at all. In parallel, add a fused or wideband observer type to the game. By P1, that type
should erase the gap, so the realistic mix of observer types determines the practical value.
