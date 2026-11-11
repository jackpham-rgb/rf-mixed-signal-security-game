# Value of the game (claim C8): results

Status: computed with simulator 0.3.0.
Every number below comes from the confirmatory run (seed 126) in
`results/value_of_game.json`; every grid point is listed in
`results/value_of_game_tables.md`. Regenerate with the commands in
`software/RUN_VALUE_STUDY.md`. Section 6 compares this run with an earlier,
independent implementation (0.2.0, not published).

**C8 verdict: partially supported, and smaller than the coarse numbers suggest.**
Against the 213-row defender library, a committed mixed defense strictly beats the
best fixed defense and the non-strategic optimizer B4 at 96 of 400 grid points
(both 95% CIs above 0), and at 77 after Bonferroni. But most of that advantage
comes from the coarse library missing in-between options. With a 36,402-row fine
library of fixed defenses, the mixture still wins by more than 0.002 at only 21 of
those 96 points (17 of them Bonferroni), and by more than 0.01 at 7. Where mixing
survives, it saves 0.002 to 0.054 bits-equivalent of loss per trace. Every
surviving point has separable bands (s >= 0.25, mostly s >= 0.5) and moderate to
strong leakage (A >= 0.5).

## 1. Question and decision rule

Unchanged from the original study. C8 asks whether a committed mixed defense
against the adaptive observer B5 strictly beats:

- (a) the best single fixed defense scored against B5, `gap_pure = L(best pure) - L(game)`;
- (b) the nominal non-strategic optimizer B4, `gap_robust = L(B4) - L(game)`.

Loss is `MI + lambda_E E + lambda_L T - c(a)` in bits per trace plus priced
overhead, with `(lambda_E, lambda_L) = k (0.30, 0.20)` and no false-alarm term.
Decision rule, fixed before the run: the game helps at a grid point only if the
cross-fitted 95% session-bootstrap CIs of both gaps lie above 0. Bonferroni uses
the bootstrap SE at z = 3.84 (m = 400).

## 2. Method

Four-band channel with separability s,
log-normal session gain and noise factors (sd 0.15 and 0.10), hop-out
probability 0.75 at coupling 0.15, 16 equal-mass bins frozen from 16 calibration
sessions x 250 traces per cell, Miller-Madow MI, 128 sessions x 1000 traces per
cell, cross-fitting over session halves, B = 1000 session-bootstrap replicates,
exact binned and continuous MI by 7 x 7 Gauss-Hermite quadrature, and the fine
library (1/12 lattice, 41 powers, 121-point variance grid). Four observer type
models and the grid A x s x k x types = 5 x 5 x 4 x 4 = 400 points. Seeds:
`SeedSequence(126, spawn_key=(i_A, i_s))`, scaffold on `spawn_key=(1000,)`.

Model constants are listed in `software/README.md`. Library rows share common
random numbers within a band, so gaps between rows have lower variance and the
CIs are tight.

## 3. Headline counts

| Quantity (of 400 grid points) | Count |
|---|---|
| gap_pure CI above 0 | 96 |
| gap_robust CI above 0 | 191 |
| Both CIs above 0 (decision rule) | 96 |
| Both, bias-corrected percentile CIs (sensitivity) | 113 |
| Both, Bonferroni (z = 3.84) | 77 |
| gap_pure CI entirely below 0 | 0 |
| Exact-model gap_pure > 0.002 / > 0.01 | 113 / 56 |
| Exact-model gap_robust > 0.01 | 116 |
| Fine-library exact gap_pure > 0.002 / > 0.01 | 27 / 7 |
| Fine-library exact gap_pure < -0.002 (a finer fixed defense beats the coarse mixture) | 61 |
| Max exact gap_pure, coarse / fine library | 0.0722 / 0.0540 |
| Max exact gap_robust (coarse) | 0.1748 |

Of the 96 decision-rule points, 95 also have an exact-model gap_pure above
0.002, so the estimator is not inventing the coarse-library effect. But 55 of the
96 have a negative fine-library gap: a single finer fixed defense does better
than the mixture. Only 21 keep a fine-library gap above 0.002.

## 4. Where the effect survives the fine library

Cross-fitted gap_pure with 95% CI; "Rel." is gap_pure / L(best pure, coarse).
`**` marks Bonferroni.

| A | s | k | Types | gap_pure [95% CI] | Rel. | Fine exact gap_pure | |
|---|---|---|---|---|---|---|---|
| 2 | 1 | 3 | 1 type | 0.0539 [0.0411, 0.0615] | 5.9% | 0.0540 | ** |
| 2 | 0.75 | 3 | 1 type | 0.0679 [0.0561, 0.0757] | 7.4% | 0.0534 | ** |
| 2 | 1 | 3 | 3 types (ad. 0.5) | 0.0409 [0.0352, 0.0464] | 4.5% | 0.0276 | ** |
| 2 | 0.5 | 3 | 2 types | 0.0250 [0.0203, 0.0269] | 2.9% | 0.0163 | ** |
| 2 | 0.5 | 3 | 1 type | 0.0273 [0.0184, 0.0296] | 3.1% | 0.0163 | ** |
| 1 | 1 | 1 | 1 type | 0.0274 [0.0208, 0.0289] | 8.3% | 0.0139 | ** |
| 2 | 0.75 | 3 | 2 types | 0.0078 [0.0035, 0.0103] | 0.9% | 0.0109 | ** |
| 1 | 1 | 1 | 2 types | 0.0269 [0.0239, 0.0284] | 8.2% | 0.0092 | ** |
| 1 | 0.75 | 3 | 1 type | 0.0334 [0.0238, 0.0376] | 6.5% | 0.0086 | ** |
| 1 | 0.75 | 3 | 3 types (ad. 0.5) | 0.0211 [0.0144, 0.0245] | 4.2% | 0.0045 | ** |
| 0.5 | 1 | 0.3 | 2 types | 0.0030 [0.0005, 0.0035] | 3.7% | 0.0044 | |
| 2 | 0.75 | 1 | 1 type | 0.0242 [0.0157, 0.0270] | 4.4% | 0.0035 | |
| 2 | 0.5 | 0.3 | 1 type | 0.0243 [0.0175, 0.0273] | 6.8% | 0.0034 | ** |
| 2 | 0.5 | 0.1 | 1 type | 0.0243 [0.0175, 0.0273] | 7.9% | 0.0034 | ** |
| 1 | 1 | 3 | 1 type | 0.0693 [0.0614, 0.0727] | 12.4% | 0.0032 | ** |
| 1 | 0.5 | 0.1 | 1 type | 0.0115 [0.0068, 0.0129] | 10.7% | 0.0024 | ** |
| 1 | 0.5 | 0.3 | 1 type | 0.0115 [0.0068, 0.0129] | 7.3% | 0.0024 | ** |
| 2 | 0.25 | 0.1 | 1 type | 0.0066 [0.0004, 0.0106] | 2.4% | 0.0021 | |
| 2 | 0.25 | 0.3 | 1 type | 0.0066 [0.0004, 0.0106] | 2.1% | 0.0021 | |
| 2 | 0.75 | 0.3 | 1 type | 0.0246 [0.0181, 0.0269] | 6.5% | 0.0021 | ** |
| 2 | 0.75 | 0.1 | 1 type | 0.0246 [0.0181, 0.0269] | 7.5% | 0.0021 | ** |

Note the cross-fitted gap here is measured against the coarse best pure defense,
so it overstates what mixing buys once finer fixed options exist. The fine column
is the fairer size of the effect.

### Representative point (A = 0.5, s = 1, k = 1, one adaptive type)

Pre-specified before the run. Here the game mixes four noise-allocation
rows (F-x1201-P0.75 0.52, F-x1111-P0.75 0.23, F-x1210-P0.75 0.23, F-x2200-P0.75
0.01) at the same energy as the best pure row (0.150) and leaks less (0.113 vs
0.142 bits). gap_pure = 0.0241 [0.0182, 0.0292], exact 0.0263, but the
fine-library gap is -0.0005: a finer fixed allocation does as well. So this point
does not survive the fine check. B4 and its robust version both pick the best
pure row here, so gap_robust equals gap_pure at this point.

### Scaffold check (original 4 x 4 scalar model)

The equilibrium is pure D3 and gap_pure = 0.0000 [0.0000, 0.0000], as in the
earlier implementation. `run_experiment` (seed 126): game value 0.3535, best pure D3
0.3535, in-sample gap 0.0000, largest cell SE 0.0028. The scaffold gives no
evidence for C8.

## 5. Pattern across the grid

- **Separability is necessary.** At s = 0 no point is significant and every gap
  is 0 (consistent with P1: identical bands leave one effective observer
  action). Decision-rule points by s: 0.25 (9), 0.5 (25), 0.75 (25), 1 (37).
- **Leakage must be non-trivial.** By A: 0.25 (2), 0.5 (13), 1 (35), 2 (46);
  none at A = 0.125, where overhead dominates and D0 wins.
- **Prices.** By k: 0.1 (22), 0.3 (24), 1 (30), 3 (20). Unlike the earlier implementation,
  the largest fine-surviving effects are at k = 3, where cheap partial
  allocations are mixed instead of paying for a stronger fixed one.
- **Observer types.** 1 type (29), 2 types (24), 3 types adaptive 0.5 (28),
  3 types adaptive 0.2 (15). Fewer adaptive observers means less to gain.
- **Main-effect variance shares** (gap_pure: A 0.207, s 0.131, k 0.017, types
  0.052; gap_robust: A 0.262, s 0.097, k 0.019, types 0.044). Most variance is
  interaction: the effect lives in the high-A, high-s corner.

## 6. Comparison with an earlier, independent implementation

| Quantity | 0.2.0 (earlier) | 0.3.0 (this run) |
|---|---|---|
| Decision-rule points | 28 | 96 |
| Bonferroni points | 7 | 77 |
| gap_pure CI entirely below 0 | 0 | 0 |
| Fine-library gap_pure > 0.002 / > 0.01 | 29 / 10 | 27 / 7 |
| Max fine-library gap_pure | 0.0512 | 0.0540 |
| Significant points at s = 0 | 0 | 0 |
| Scaffold equilibrium | pure D3 | pure D3 |

The coarse-library counts differ a lot, mostly because of tighter CIs (common
random numbers here), a 212- versus 213-row library, and different model
constants. The fine-library counts
and the size of the largest real effect agree closely between two independent
implementations. That agreement is the most trustworthy finding here: the value
of mixing that cannot be matched by a finer fixed defense appears at roughly 7%
of regimes, is at most about 0.05 bits per trace, and needs separable bands.

## 7. Estimator diagnostics

- Mean MC minus exact binned MI per dataset ranges from -0.0149 to +0.0060 bits;
  the worst single cell is 0.0234 bits. Part of this is a real property of
  pooling a finite number of sessions: MI is convex in the channel, so the
  plug-in estimate over G sessions is biased up by roughly 1/G. The test suite
  checks that the error vanishes as G grows.
- Binning loss (continuous minus binned exact MI) is at most 0.016 bits.
- Cross-fitted gap estimates track the exact-model gaps closely across all 400
  points (correlation 0.996, mean difference -0.0005); see Fig D.
- Percentile bootstrap CIs can under-cover near ties; the bias-corrected count
  (113 vs 96) shows the borderline sensitivity.

## 8. Theory notes (status unchanged)

- **P1 (proved, elementary):** one effective observer action forces a pure
  optimal defense. Consistent with zero gaps at s = 0 and in the scaffold.
- **P2 (proved under its assumption):** convex loss in a convex action set means
  the mean action beats any mixture. The fine-library result is a numerical view
  of the same idea: as the fixed-defense set gets denser, most of the apparent
  value of mixing disappears.
- **Positive value of mixing** at the 21 fine-surviving points is a numerical
  observation for this synthetic channel, not a theorem.
- **Open issue:** the epigraph LP is zero-sum within each type, so commitment
  adds nothing beyond minimax there (Korzhyk et al. 2011). A general-sum version
  with separate defender and observer costs is needed before "Stackelberg" is
  more than a label.

## 9. Figures

In `software/results/figures/`: `fig_A_frontier.png` (leakage vs energy as the
price sweeps, A = 0.5, s in {0.25, 1}), `fig_B_gap_robust_heatmap.png`,
`fig_B_supp_gap_pure_heatmap.png`, `fig_C_payoff_equilibrium.png` (8 of 213 rows
at the representative point with p*, q*, and support stability), and
`fig_D_validation.png` (estimates vs the exact model).

## 10. Seeds, config, versions

Seed 126; B = 1000; 128 sessions x 1000 traces; 16 bins; rho = 0.5; quadrature
7 points; fine library 12 / 41 / 121. Python 3.13.18, NumPy 2.5.3, SciPy 1.18.1
(HiGHS), matplotlib 3.11.2, simulator 0.3.0. Runtime 796 s on 4 workers.
`python -m pytest`: 25 passed.

## 11. Limitations

The channel is synthetic and
uncalibrated, F = 0, MI estimates are biased, the linear mixed-policy payoff
assumes per-trace mode identification and a band-committed observer, and low
estimated leakage is not a security proof. The model constants are choices, so no number here should be compared with hardware until
separability is measured.

## 12. Next steps

1. Add a fused/wideband observer type (sees all bands). By P1 it should erase
   the gap; the realistic share of such observers sets the practical value.
2. Make the game general-sum (defender prices energy/latency/false alarms,
   observer prices traces/bandwidth) so commitment can matter.
3. Report fine-library gaps as the primary effect size from now on.
4. Measure band separability on owned hardware.
