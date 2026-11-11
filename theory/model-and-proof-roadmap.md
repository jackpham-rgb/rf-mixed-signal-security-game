# Model and proof roadmap

## 1. Status vocabulary

- **Proved:** complete argument checked line by line against stated assumptions.
- **Proof sketch:** route is credible, but details or regularity conditions remain.
- **Conjecture:** a target statement supported only by intuition/numerics.
- **Falsified:** counterexample or experiment invalidates the statement.

At project creation, only elementary finite-game results below are “proved.”
Research-specific claims are proof targets.

## 2. Variables

Let the secret \(S\in\{1,\ldots,m\}\), public input \(X\), defender action
\(d\in\mathcal D\), observer type \(\theta\in\Theta\), and observer action
\(a\in\mathcal A_\theta\). A trace is

\[
Y = H_a L(S,X) + B_d(X) + N_d + W.
\]

- \(L\): secret-dependent physical leakage.
- \(H_a\): observer-selected measurement/filter operator.
- \(B_d\): deterministic defense activity.
- \(N_d\): randomized defense activity.
- \(W\): ambient and instrument noise.

The finite first model uses empirical losses

\[
\ell_{\theta}(d,a)
= \widehat I(S;Z_{d,a})
+\lambda_E \bar E_d+\lambda_L\bar T_d+\lambda_F\bar F_d
-c_\theta(a),
\]

where \(Z\) is a declared feature of \(Y\), barred costs are dimensionless, and
\(c_\theta\) is the observer resource cost. Sign conventions must be frozen:
the defender minimizes \(\ell\), while a zero-sum observer maximizes it.

Mutual information is

\[
I(S;Z)=\sum_{s,z}p(s,z)\log_2\frac{p(s,z)}{p(s)p(z)}.
\]

For continuous features, the estimator and its bias calibration are part of the
experiment, not hidden inside this symbol.

The empirical realization of \(L\), \(B_d\), \(N_d\), and the costs
\(\bar E_d,\bar T_d\) is planned to come from a digital-circuit track (not built yet),
which would derive them from RTL switching activity rather than from invented
constants: \(L\) from secret-dependent per-cycle toggles, \(N_d\) from a dummy
switching bank, and the cost coefficients from synthesis timing/power reports.
Simulated switching activity is a declared **proxy** for current demand, not a
measurement of leakage, so every bound proved here inherits that caveat until
the hardware calibration gate passes.

## 3. Finite zero-sum foundation

Let \(M\in\mathbb R^{D\times A}\) be a fixed payoff matrix. The defender chooses
\(p\in\Delta_D\), observer \(q\in\Delta_A\):

\[
v^\star=\min_{p\in\Delta_D}\max_{q\in\Delta_A}p^\top Mq.
\]

The defender LP is

\[
\begin{aligned}
\min_{p,v}\quad &v\\
\text{s.t.}\quad&M^\top p\le v\mathbf 1,\\
&\mathbf 1^\top p=1,\quad p\ge0.
\end{aligned}
\]

The observer dual is

\[
\begin{aligned}
\max_{q,u}\quad &u\\
\text{s.t.}\quad&Mq\ge u\mathbf 1,\\
&\mathbf 1^\top q=1,\quad q\ge0.
\end{aligned}
\]

### Result F1: finite equilibrium

**Status: proved by standard theorem, not original.** For finite nonempty action
sets, von Neumann's minimax theorem gives equality of the two programs and at
least one mixed equilibrium.

**Implementation check:** solve both LPs and require nonnegative probabilities,
unit sums, constraint residual below tolerance, and small primal-dual gap.

## 4. Bayesian Stackelberg model

Nature draws observer type \(\theta\sim\pi\). The defender publicly commits to
\(p\in\Delta_D\). Type \(\theta\) chooses a best response

\[
a_\theta^\star(p)\in
\arg\max_{a\in\mathcal A_\theta} U_A^\theta(p,a).
\]

The defender solves

\[
\min_{p\in\Delta_D}
\sum_{\theta}\pi_\theta
J_D^\theta\left(p,a_\theta^\star(p)\right).
\]

Tie-breaking must be declared. Use pessimistic tie-breaking for a conservative
security claim: among observer best responses, choose the one worst for the
defender.

### Target T1: existence

**Status: proof sketch.** For finite \(\mathcal D,\Theta,\mathcal A_\theta\),
the defender simplex is compact. The pessimistic leader objective can be written
as the pointwise maximum of finitely many affine/piecewise-affine functions over
best-response regions. A minimum exists after expressing the problem as a
finite collection of closed-region programs or a standard strong Stackelberg
MILP. Check the exact semicontinuity argument for the selected tie rule.

**Value:** necessary plumbing, not enough for publication alone.

### Target T2: tractable special case

**Status: conjecture pending exact utility definition.** If observer utility and
defender loss are zero-sum within each type and actions are finite, the Bayesian
problem can be represented by an LP over defender probabilities and one
epigraph variable per type:

\[
\min_{p,v_\theta}\sum_\theta \pi_\theta v_\theta,\qquad
(M^\theta)^\top p\le v_\theta\mathbf1.
\]

This is straightforward but useful as a verified reference solution.

## 5. Information-to-success bounds

For a uniform \(m\)-ary secret, Fano's inequality gives

\[
H(S|Z)\le h_2(P_e)+P_e\log_2(m-1)
\]

for an estimator with error probability \(P_e\). Since
\(H(S|Z)=\log_2m-I(S;Z)\), measured/upper-bounded mutual information constrains
possible error. Fano is commonly rearranged into lower bounds on \(P_e\); it is
often loose and must not be sold as exact attack success.

Pinsker's inequality,

\[
\|P-Q\|_{\mathrm{TV}}\le
\sqrt{\tfrac12 D_{\mathrm{KL}}(P\|Q)},
\]

can connect distinguishability to KL divergence. Log base changes constants.

### Target T3: operational leakage bound

**Status: proof target.** Choose one operational task (binary distinguishability
or \(m\)-ary key-byte classification), define distributions precisely, and
derive a bound that includes the defense mixture. Validate looseness against
Bayes-optimal success in synthetic Gaussian cases.

Do not claim that low estimated MI proves security. The estimator, feature map,
finite samples, and unobserved channels limit the statement.

## 6. Robustness to an unknown type prior

Let the nominal prior be \(\pi_0\), with uncertainty set

\[
\mathcal U_\rho=\{\pi\in\Delta_\Theta:
\|\pi-\pi_0\|_1\le\rho\}.
\]

The robust policy is

\[
\min_{p\in\Delta_D}\max_{\pi\in\mathcal U_\rho}
\sum_\theta\pi_\theta v_\theta(p).
\]

For finite empirical \(v_\theta(p)\), this is a robust LP or a small nested LP.

### Target T4: robust counterpart and stability

**Status: proof target.** Dualize the inner prior maximization, derive the
single-level LP, and show monotonicity of robust value in \(\rho\). Quantify how
policy support changes with \(\rho\). The meaningful result is not monotonicity
alone; it is an interpretable robustness/overhead tradeoff.

## 7. Payoff-estimation uncertainty

Empirical payoff entries \(\widehat M_{da}\) are random. With bounded per-run
loss in \([0,1]\), Hoeffding gives

\[
\Pr(|\widehat M_{da}-M_{da}|\ge\epsilon)
\le2e^{-2n\epsilon^2}.
\]

A union bound over \(DA\) cells yields simultaneous control. Real MI estimates
are not automatically bounded/unbiased, so this result applies only after
choosing a bounded per-run statistic or a valid concentration result.

### Target T5: equilibrium-value confidence interval

**Status: proof target.** Establish a sup-norm confidence set
\(\|M-\widehat M\|_\infty\le\epsilon\), then prove
\(|v(M)-v(\widehat M)|\le\epsilon\). This Lipschitz result follows because any
mixed expectation changes by at most \(\epsilon\). Extend to session bootstrap
for the actual trace statistic.

With \(n_{\min}\) independent sessions per cell and a bounded per-run statistic,
a union bound over the \(DA\) cells gives
\(\epsilon=\sqrt{\ln(2DA/\delta)/(2n_{\min})}\), so the interval is governed by
the number of *sessions*, not traces. This arithmetic is what motivates the high-volume track: at \(n_{\min}=30\) the bound is too
wide to separate any two defenses.

Two refinements belong with T5 and are developed in that document:

- **Hierarchical uncertainty.** A Bayesian hierarchical model over
  sessions/netlists/PVT corners yields posterior samples of the whole matrix
  \(M^{(t)}\) with cells correlated through shared variance components. Solving
  the LP per sample gives posterior distributions for \(v\) and \(p^\star\), and
  a direct probability for the project's central question,
  \(\Pr(p^\star\neq p_{\mathrm{robust}}\mid\text{data})\) from §9. It also
  exposes whether a single payoff number exists at all: a large between-netlist
  variance means the equilibrium is netlist-dependent.
- **Policy versus value.** The Lipschitz bound covers \(v\) only. The argmin
  \(p^\star\) can jump discontinuously when the support changes, so it must be
  reported as a bootstrap/posterior distribution with per-action support
  stability rather than as a point estimate. Establishing conditions under which
  the support is stable is an open proof target, not a known result.

## 8. Dynamic extension (only after static results)

State \(x_t\) may include temperature, battery, recent alarms, and channel
estimate. A stochastic game or constrained MDP can model sequential adaptation:

\[
x_{t+1}\sim P(\cdot|x_t,d_t,a_t),\qquad
\min_\pi\max_\sigma
\mathbb E\sum_{t=0}^{T}\gamma^t\ell(x_t,d_t,a_t).
\]

**Status: postponed.** Do not use deep RL. First determine whether state and
long-horizon effects materially change decisions. A contextual bandit or robust
receding-horizon controller is preferred if transitions are weak.

## 9. Why game theory instead of one optimizer?

The game framing earns its place only if:

1. the observer changes band/filter/budget after seeing the defense policy;
2. that response changes the optimal defense;
3. commitment/randomization improves worst-case or Bayesian performance; and
4. the model predicts held-out adaptive behavior.

Required comparator:

\[
\min_d\;\mathbb E_{\text{fixed channel}}\ell(d)
\]

or its robust convex counterpart. If it matches the game policy and performance,
report that the strategic model added no value.

## 9a. Findings from the value-of-game study (2026-10-30)

The first full numerical study (see
[`../software/results/VALUE_OF_GAME_RESULTS.md`](../software/results/VALUE_OF_GAME_RESULTS.md))
settled several points and reshaped the theory targets. Record them honestly.

### Commitment needs a general-sum game
Committing first is worthless in a pure zero-sum game: Stackelberg, Nash, minimax,
and maximin all coincide (Korzhyk et al., JAIR 2011). So the value of commitment
here cannot come from the shared leakage term. It comes only from the private
costs: the defender prices energy, latency, and false alarms, while the observer
prices traces and bandwidth, which the other side does not value identically.
That asymmetry is what makes the game general-sum. The zero-sum-within-type case
(T2) is only a reference solve where commitment is expected to add nothing.

### P1 (proved, elementary): one effective observer action forces a pure defense
If the observer effectively has one action (a fused or wideband observer that
sees all bands at once, or an observer whose action does not depend on the
defender policy), the defender loss is linear in p over the simplex, so a vertex
(a pure defense) is optimal and the value of mixing is zero. Mixing can help only
because the defender minimizes a maximum of several linear functions (one per
observer action), whose minimizer can lie strictly inside the simplex.

### P2 (proved under its assumption): convex loss forbids useful mixing
If the action set is convex and the loss is convex in the action for every
observer action, then by Jensen the deterministic mean action does at least as
well as any mixture. Binary-input Gaussian mutual information is convex in noise
variance only in part of the range (numerical observation), which is consistent
with the gap appearing only at moderate-to-high leakage.

### Positive value of mixing is numerical, not a theorem
In the general-sum, band-separable regime a mixed policy strictly beats every
pure defense at some grid points. This is a numerical result with an exact
quadrature-MI check and a 36,402-row fine-library check, not a proof. It is
specific to this synthetic channel.

### Target T6 (candidate original result): when does band choice reveal the mode?
The epigraph LP scores a mixed policy with a payoff that is linear in p. That is
exact if the observer can identify which clock mode produced each trace, and a
conservative upper bound on leakage if it cannot (mutual information is convex in
the channel, so within-trace mixing hides more). A theorem characterizing when
the observer's band or filter choice reveals the realized mode, with a corollary
that a fused/wideband observer type (via P1) erases the value of mixing, would be
a genuine contribution. This is the most promising original-theory lead and is
currently a proof target, not a result.

## 10. Proof workflow

For every candidate theorem:

1. Write definitions and dimensions.
2. List assumptions and a physical test for each.
3. Search for the nearest theorem; state what is inherited versus new.
4. Test small counterexamples numerically.
5. Write proof without relying on solver output.
6. Ask an advisor to attack regularity, tie-breaking, estimator, and units.
7. Link theorem to one experiment that can falsify its assumptions.

The strongest plausible paper package is T3 or T4 plus T5, not the elementary
existence result.
