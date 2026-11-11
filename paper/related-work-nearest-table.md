# Related work: nearest-work table

Sources: two literature searches on 2026-10-30 (54 recorded web queries in
one session plus citation chaining, then 27 more queries; full-text reads of Yao and
Zhang 2024, EMMasker, and the Xu and Baykal-Gürsoy manuscripts; Semantic
Scholar forward chaining of nine seeds). This is a positioning aid, not a
novelty finding. "No direct match found" means only that the recorded queries
did not expose one; it is not evidence of novelty.

How to read the table:

- "Us" means the claim under test: an embedded defender commits to a randomized
  clock-mode and dummy-current or noise policy against observer types that
  best-respond with band, filter, and trace budget, with MI/Fano and
  prior-robustness analysis, on simulated RTL/VCD traces and later owned
  hardware.
- "Shares" and "Differs" are one line each, except for Yao and Zhang, Xu and
  Baykal-Gürsoy, and EMMasker, whose "Differs" cells now carry the
  reviewer-rebuttal points (full answers in section (d)). Most rows rest on
  abstracts; Yao and Zhang 2024 and EMMasker were read in full, and the Xu
  and Baykal-Gürsoy models were read from the accepted manuscripts (read
  depth per work is in the log). Re-check each line against the primary PDF
  before it goes into the paper.
- Full citations with pages, secondary works, the exact queries, and
  citation-chaining notes are in the log.

## Nearest-work table

| Work | Venue/Year | Shares with us | Differs from us | Link |
|---|---|---|---|---|
| Doychev, Köpf: "Rational Protection against Timing Attacks" | IEEE CSF 2015 | Stackelberg protection against a resource-bounded adversary who splits its budget between measurements and offline search | Timing channel; defender commits to one pure configuration, not a randomized policy; no band, filter, power, or EM model | https://doi.org/10.1109/CSF.2015.39 |
| Geng, Kwiat, Kamhoua, Shi: "On Random Dynamic Voltage Scaling for Internet-of-Things: A Game-Theoretic Approach" | IEEE TCAD 2018 | Game analysis of a physical power countermeasure on IoT devices, with alarm and denial-of-service costs | Game is over a supply-monitor alarm threshold against an undervolting attacker (Nash); no committed randomized policy, band choice, or MI bound | https://doi.org/10.1109/TCAD.2017.2717780 |
| Yao, Zhang: "Side-Channel Attack Security Risk Assessment Model Based on Mutual Information Game" (CSAT 2023 companion; Chinese original in Computer Engineering 2012) | J. Phys.: Conf. Ser. 2024; CSAT 2023; Computer Engineering 2012 | Chip-designer versus attacker game with mutual-information payoffs and mixed strategies; the framing dates to 2012 | Full text read (2024). A "static game": simultaneous, Nash named but never computed, no commitment. Payoffs are abstract scalars I(leak_i; key) with no signal, noise, or spectral model. Attacker strategies are unspecified lists, so no band, filter, or trace-budget choice (the trace count sits inside the MI estimate). No costs beyond an unspecified constraint set; no example, equilibrium, or data. Defense advice is "maximize policy entropy," not an equilibrium policy. They own the framing, not the model | https://doi.org/10.1088/1742-6596/2732/1/012002 ; https://doi.org/10.1109/CSAT61646.2023.00046 ; https://doi.org/10.3969/j.issn.1000-3428.2012.15.004 |
| Woo, Ryu, Seo, Kim, Lee, Cassuto, Kim: "Mutual Information Minimization for Side-Channel Attack Resistance via Optimal Noise Injection" (predecessor: Jin, Xu, Bettati, Christodorescu, WIFS 2022) | IEEE ISIT 2026 (arXiv 2025); IEEE WIFS 2022 | Minimizes total or worst-case MI under a noise power budget for resource-constrained devices; Fano motivation | Fixed observer that does not respond; noise only, no clock modes; numerical results with no estimation uncertainty or measured traces | https://doi.org/10.1109/ISIT62367.2026.11653960 ; https://arxiv.org/abs/2504.20556 ; https://doi.org/10.1109/WIFS55849.2022.9975384 |
| Wu, Wagner, Suh: "A Case for Maximal Leakage as a Side Channel Leakage Metric" | arXiv 2020 | Cost-leakage trade-off solved as an LP over randomized protection schemes | Non-strategic observer; at most two deterministic schemes suffice under maximal leakage, so randomization alone is not a contribution | https://arxiv.org/abs/2004.08035 |
| Li, Oechtering, Gündüz: "Privacy Against a Hypothesis Testing Adversary" | IEEE TIFS 2019 | Power-trace shaping under an energy (distortion) budget against a fully informed adversary; KL and Chernoff exponent guarantees | Smart-meter scale; the adversary only picks its test, not band, filter, or trace budget; binary hypothesis; no clock modes | https://doi.org/10.1109/TIFS.2018.2882343 |
| Xu, Baykal-Gürsoy: "Power Allocation for Cooperative Jamming Against a Strategic Eavesdropper Over Parallel Channels" (Bayesian variant: Xu, Baykal-Gürsoy, Spasojević; cost variant: Xu, Baykal-Gürsoy, SecureComm 2020) | IEEE TIFS 2023; IEEE CNS 2021; SecureComm 2020 | Defender spreads limited noise power over parallel channels (TIFS) or randomizes which channel to protect (CNS) while an eavesdropper limited by hardware budget to a few frequencies picks channels; threshold and water-filling equilibria; Bayesian eavesdropper types; the game policy beats an all-channels-attacked policy | Secrecy of intentional wireless links, not unintentional leakage; likely source of our band-subgame mathematics. Concede: with additive noise, Gaussian leakage, and a one-band observer, our band subgame is their game. Differs: their defender only adds noise to fixed channels, while clock modes move, rescale, and misalign the leakage; secrecy is per block with fresh messages, while our observer averages N traces of a fixed key, so dummy noise erodes with N and mixing pays only if the observer does not spend measurement on detecting the mode; no legitimate receiver, and costs are energy, latency, false alarms, bandwidth, and traces; closed-form capacities versus payoffs estimated from traces; a fixed prior (CNS notes that wrong beliefs are exploitable) versus a prior-robust policy. Not a difference while our game is zero-sum: their simultaneous Nash versus our commitment, because our committed policy is then a Nash minimax policy | https://doi.org/10.1109/TIFS.2022.3228520 ; https://doi.org/10.1109/CNS53000.2021.9705044 ; https://doi.org/10.1007/978-3-030-63086-7_14 ; https://par.nsf.gov/servlets/purl/10461811 |
| Yang, Xue, Zhang, Richa, Fang: "Coping with a Smart Jammer in Wireless Networks: A Stackelberg Game Approach" (with Jia, Yao, Sun, Niu, Zhu: "Bayesian Stackelberg Game for Antijamming Transmission With Incomplete Information") | IEEE TWC 2013; IEEE Commun. Lett. 2016 | Leader commits and an adaptive follower best-responds; Bayesian types; existence and uniqueness proofs | Domain mismatch: a jammer harms a link and the payoff is throughput or SINR, not leakage; no measurement band, trace budget, or hardware cost | https://doi.org/10.1109/TWC.2013.071913121570 ; https://doi.org/10.1109/LCOMM.2016.2598808 |
| Aldeen, Liang, Zhang, Guo, Song, Cheng: "EMMasker: EM Obfuscation Against Website Fingerprinting" | NDSS MADWeb 2024 | Injects GPU noise that shifts the DVFS clock state out of a band-limited SDR observer's band; scales noise with the clock state; randomizes burst timing (1 to 15 s gaps, 1 to 5 s bursts); retrains the attacker's classifier on defended traces; overhead measured; closest mechanism found | Full text read. Observer band fixed at 810 MHz (25 MHz sampling) throughout, not a best response, and the threat model sets aside multi-radio or sweeping observers as too costly, which is exactly our follower. The clock shift is a side effect of injected load and all randomization parameters are hand-set, while our mode and dummy-current distribution solves a priced game. No game or formal leakage measure: one ResNet's accuracy on five websites and one GPU, with no MI, TVLA, trace-budget curve, or intervals. GPU website fingerprinting from far-field emanation, not embedded key leakage. Not differences: randomization, clock-state shifting, or classifier retraining | https://doi.org/10.14722/madweb.2024.23018 |
| Randomized clock and voltage hiding: Yang, Wolf, Vijaykrishnan, Serpanos, Xie (RDVFS); Baddam, Zwolinski (RDVFS break); Lagasse, Bartoli, Burleson (clock plus voltage noise) | DATE 2005; VLSID 2007; IEEE ASAP 2019 | Same physical knobs (random frequency and voltage modes, combined clock and voltage noise) with overhead reported | Open-loop, hand-set distributions; an observer who detects the frequency mode defeats RDVFS, but none models that observer as a player; no game or MI bound | https://doi.org/10.1109/DATE.2005.241 ; https://doi.org/10.1109/VLSID.2007.79 ; https://doi.org/10.1109/ASAP.2019.00009 |
| Gammell, Raghunathan, Roy: "Power side-channel leakage localization through adversarial training of deep neural networks" | arXiv 2024 | Minimax game between a deep-learning attacker and a trainable noise generator on power traces, with a noise penalty | Goal is leakage localization; noise is added in software to recorded traces, not a deployable committed device policy; no band, budget, or energy cost | https://arxiv.org/abs/2410.22425 |
| Khalaj Monfared, Forte, Tajik: "RandOhm: Mitigating Impedance Side-channel Attacks using Randomized Circuit Configurations" | IEEE/ACM ICCAD 2024 | Moving-target defense: run-time randomization of the physical configuration to decorrelate leakage, with overhead measured on FPGA | Randomization is not optimized against a strategic observer; impedance channel, not power or EM emission; no game or leakage bound | https://doi.org/10.1145/3676536.3676687 |
| Camurati, Poeplau, Muench, Hayes, Francillon: "Screaming Channels" (with Ayoub, Cayre, Francillon, Maurice: "BlueScream") | ACM CCS 2018; ACSAC 2024 | Mixed-signal BLE chips leak through the radio; the observer tunes to the leak and can restrict hopping; supports a band-choosing observer | Attack papers; countermeasures only qualitative; no defense optimization | https://doi.org/10.1145/3243734.3243802 ; https://doi.org/10.1109/ACSAC63791.2024.00060 |
| Danial, Das, Ghosh, Raychowdhury, Sen: "SCNIFFER: Low-Cost, Automated, Efficient Electromagnetic Side-Channel Sniffing" | IEEE Access 2020 | The observer automates its measurement choice (probe location) by TVLA or SNR and counts trace cost | Attack-side search over position, not band; no defender response or game | https://doi.org/10.1109/ACCESS.2020.3025022 |
| Gao, Ma, Zhang, He, Zhao, Stojilović, Jin: "AIPS: AI-Based Power Simulation for Pre-Silicon Side-Channel Security Evaluation" (with He et al.: "RTL-PSC") | IACR TCHES 2026; IEEE VTS 2019 | VCD switching activity turned into synthetic power traces, up to 1M traces; RTL switching-activity leakage assessment | No defense policy, game, or adaptive observer; shows our dataset pipeline and its scale are prior art | https://doi.org/10.46586/tches.v2026.i2.441-467 ; https://doi.org/10.1109/VTS.2019.8758600 |
| Alvim, Chatzikokolakis, Kawamoto, Palamidessi: "Information Leakage Games" (extended: "Information Leakage Games: Exploring Information as a Utility Function"; companion on visible and hidden choice) | GameSec 2017; ACM TOPS 2022; Entropy 2018 | Zero-sum games with information leakage as the utility; a randomizing defender; hidden mixing makes leakage convex in the defender's strategy, so a mix can leak less than its parts; equilibria and algorithms; simultaneous and sequential variants | Abstract channels (programs, Crowds, local differential privacy); no physical measurement, band, filter, or trace budget; no energy or latency costs. Consequence: our per-mode LP is exact only if the observer can tell each trace's mode, and conservative otherwise | https://doi.org/10.1007/978-3-319-68711-7_23 ; https://doi.org/10.1145/3517330 ; https://doi.org/10.3390/e20050382 |
| Jin, Xu, Cai: "Energy Efficient Obfuscation of Side-Channel Leakage for Preventing Side-Channel Attacks" | ACM SAC 2024 (arXiv 2022) | Energy-budgeted noise that minimizes side-channel capacity, by explicit analogy with wiretap artificial noise; covers the attacker's choice of compression method by aggregating optimal noise patterns; experiments | Aggregation, not a best response or equilibrium; noise only, no clock modes; no band or trace-budget choice | https://doi.org/10.1145/3605098.3635997 ; https://arxiv.org/abs/2208.09140 |
| Klasson Landin, Jilborg: "Determining the Optimal Frequencies for a Duplicated Randomized Clock SCA Countermeasure" (with Tran, Dao, Le, Hoang, Hoang, Pham: "Spread Spectrum-Based Countermeasures for Cryptographic RISC-V SoC") | arXiv 2023; IEEE TVLSI 2024 | Choosing the frequency set of a randomized clock with a dummy core under a timing-overhead trade-off (Klasson Landin); random spread-spectrum frequency hopping tested with up to five million traces (Tran) | Open-loop designs against fixed CPA and alignment attacks; no best-responding observer, game, or MI bound | https://arxiv.org/abs/2307.13834 ; https://doi.org/10.1109/TVLSI.2024.3444851 |
| Ayrault, Borde, Kühne, Leneutre: "Moving Target Defense Strategy in Critical Embedded Systems: A Game-theoretic Approach" | IEEE PRDC 2021 | Bayesian Stackelberg commitment to a randomized reconfiguration policy on an embedded system under quality-of-service constraints, solved as a MILP | System-level moving-target defense against exploitation, not physical leakage; no measurement band, filter, traces, or MI | https://doi.org/10.1109/PRDC53464.2021.00014 |

The three nearest works overall:

- Mechanism: EMMasker (clock-state shifting plus noise against a band-limited
  observer, with the band held fixed and no game).
- Mathematics: Xu and Baykal-Gürsoy (noise power over parallel channels against
  an eavesdropper who picks channels).
- Framing within side-channel security: Doychev and Köpf (Stackelberg
  protection against a resource-bounded adversary).

Added in Deep search 2:

- Theory of randomized defense with information as the payoff: Alvim,
  Chatzikokolakis, Kawamoto, and Palamidessi (information leakage games;
  hidden mixing makes leakage convex in the defender's strategy).
- Closest structural analog of the whole game, in wireless: Xu,
  Baykal-Gürsoy, and Spasojević, CNS 2021 (a defender that randomizes which
  channel to protect, an eavesdropper limited to a few frequencies, and
  Bayesian types, under simultaneous Nash play).
- Mutual-information game framing within side-channel security, now traced to
  2012: Yao and Zhang (a static designer-versus-attacker game with abstract
  MI payoffs).

## (a) Narrowest defensible positioning sentence (supportable today)

Refined version (Deep search 2, 2026-10-30):

> We adapt band-selection jamming games (Xu and Baykal-Gürsoy 2023; Xu et al.
> 2021) and information-leakage games (Alvim et al. 2017, 2022) to
> unintentional power and EM leakage from an embedded device, in which the
> defender commits to a randomized mix of clock-frequency modes and
> dummy-current levels priced in energy, latency, and false alarms and each
> observer type best-responds with a measurement band, filter, and trace
> budget, and we ask whether what those games lack (defender actions that
> move the leakage rather than add noise, evidence about a fixed key
> accumulated over a costly trace budget, and uncertainty over observer
> types) changes the recommended policy or improves the leakage-overhead
> frontier over fixed, random, MI-optimal-noise (Woo et al. 2026),
> EMMasker-style, and robust-convex baselines on simulated RTL-derived
> traces.

Why this refinement: it credits both borrowed game families, names the three
features that do not transfer as the object of study rather than as results,
adds the EMMasker-style baseline a reviewer will ask for, and stops presenting
commitment as a difference (commitment remains the modeling assumption, but in
the zero-sum case it coincides with Nash). Like the first version, it claims
nothing new, nothing proved beyond F1, and nothing measured on hardware.

First-pass version (kept for the record):

> We adapt leader-follower and band-selection game models from wireless jamming
> and eavesdropping (Jia et al. 2016; Xu and Baykal-Gürsoy 2023) to
> unintentional power and EM leakage from an embedded device: the defender
> commits to a randomized mix of clock-frequency modes and dummy-current or
> noise levels, priced in energy, latency, and false-alarm cost, each observer
> type best-responds with a measurement band, filter, and trace budget, and we
> ask whether the resulting policy differs from, or improves on, fixed, random,
> MI-optimal-noise (Woo et al. 2026), and robust-convex baselines on simulated
> RTL-derived traces.

Why this version: it describes the formulation that already exists in
`theory/model-and-proof-roadmap.md`, credits the borrowed game mathematics,
names the strongest non-game baseline, and asks a question instead of reporting
a result. It does not say the formulation is new, that the game beats any
baseline, that any theorem beyond the standard finite minimax result (F1) is
proved, or that anything was measured on hardware.

## (b) What must be proven or measured to upgrade the claim

The steps are cumulative. Status labels follow
`theory/model-and-proof-roadmap.md`.

Upgrade 1, "the strategic model changes the recommended defense":

- Measure: on simulated traces, the observer's best band, filter, and trace
  budget change when the defender's policy changes, with session-level
  intervals (roadmap Section 9, items 1 and 2).
- Measure: the bootstrap or posterior probability
  \(\Pr(p^\star\neq p_{\mathrm{robust}}\mid\text{data})\) exceeds a
  preregistered threshold, reported with per-action support stability.
- Prove: T2 for the exact utilities, plus a value-of-commitment condition in
  this model, that is, when the committed mixed policy is strictly better than
  the best deterministic policy and than the robust-convex policy. Without it,
  the Wu, Wagner, and Suh result (two deterministic schemes suffice when the
  observer is not strategic) suggests mixing may add nothing.
- Added in Deep search 2: in the zero-sum-within-type model (T2) the
  committed policy equals a Bayes-Nash minimax policy (Korzhyk et al. 2011;
  von Stengel and Zamir 2010), so the value of commitment over Nash play is
  zero there. Either state and test the commitment condition in a
  general-sum variant (for example, observer resource costs not credited to
  the defender), or keep commitment only as the modeling assumption that
  matches a firmware-fixed, profileable policy and do not present it as an
  advantage. The value of mixing over the best deterministic policy is a
  separate question and stays in scope.

Upgrade 2, "improves the leakage-overhead frontier":

- Measure: the frontier gap against the best of fixed noise, random frequency,
  MI-optimal noise at matched energy (Woo or Jin style), robust convex (B4), and
  an EMMasker-style mode-shifting heuristic, all against a band-switching
  observer, with session-level intervals that exclude zero, multiple-comparison
  control, and a preregistered decision rule.
- Added in Deep search 2: include the inherited wireless solution as a
  baseline (a noise-only band allocation from the Xu and Baykal-Gürsoy
  equilibrium), so any gain attributable to clock modes is isolated; and
  implement the EMMasker-style heuristic from its published rules (random
  gaps and bursts, intensity scaled with the clock state), adapted to the
  device's time scale.
- Measure: held-out adaptive observers the solver never saw: unseen filters,
  oversampling plus resynchronization (Brisfors et al. 2022), frequency-mode
  detection (Baddam and Zwolinski 2007), and a deep-learning classifier. The
  ordering of defenses must hold.
- Prove: T5 (sup-norm confidence set to a value interval, extended to the
  session bootstrap), so the gap carries valid uncertainty.

Upgrade 3, "formal leakage and robustness guarantees":

- Prove: T3, an operational bound for one stated task that includes the
  defender's mixture over clock modes, checked against Bayes-optimal success in
  a synthetic Gaussian case.
- Prove: T4, the dualized robust counterpart over the \(\ell_1\) prior ball,
  monotone robust value in \(\rho\), and a description of when the support
  changes.
- Prove: at least one result that does not follow from the wireless band games,
  for example a condition under which mixing clock modes (which changes the
  leakage operator and trace alignment, not only additive noise) gives strictly
  lower equilibrium leakage than every noise-only policy of equal energy, or a
  proof that it cannot. Without such a result the theory is inherited.
- Added in Deep search 2 (candidate; conjecture, not checked by the theory
  owner): an LP over p built from per-mode leakage estimates is exact when
  the observer can identify each trace's mode and an upper bound on
  single-trace leakage when it cannot (convexity of MI in the channel; Alvim
  et al. 2017, 2022). A theorem stating when the observer's band and filter
  choice makes the mode visible, and how much hidden mixing then gains over
  the LP value, would not follow from the wireless band games. Check it
  against Alvim et al.'s visible and hidden choice results (Entropy 2018)
  before claiming it.

Upgrade 4, "holds on hardware":

- Measure: proxy calibration (stage R4): regress measured supply current and
  near-field EM spectra on simulated switching activity and report fit and
  spectral error, before any statement about silicon.
- Measure: conducted and near-field EM traces from owned hardware over at least
  30 sessions, with energy and latency overhead measured rather than assumed,
  reproducing the simulated ordering of defenses.

Upgrade 5, any "to our knowledge" sentence:

- Search: read Yao and Zhang 2023 and 2024 in full; run field-restricted IEEE
  Xplore, ACM DL, and Scopus searches; forward-chain the seven seeds named in
  the log; search Google Patents and Espacenet with the candidate CPC classes
  listed there; search CNKI; get an advisor's sign-off. Even then, write "to our
  knowledge," never "first."
- Status after Deep search 2: Yao and Zhang 2024 read in full (it does not
  occupy the combination); the CSAT 2023 paper and the 2012 Chinese original
  are still unread; nine seeds forward-chained in Semantic Scholar
  (incomplete coverage); a Google Patents concept search run with confirmed
  CPC codes. Still open: field-restricted IEEE Xplore, ACM DL, and Scopus
  searches; Espacenet and USPTO class searches; a search inside CNKI; and
  advisor sign-off. New items to read first: Alvim et al. (TOPS 2022 from
  Section 3; Entropy 2018), Khouzani and Malacaria 2017, and Antonopoulos and
  Terauchi 2019.

## (c) Claims we must NOT make

- That game-theoretic, Stackelberg, or MI-game side-channel defense is new
  (Doychev and Köpf 2015; Geng et al. 2018; Yao and Zhang 2012, 2023, 2024;
  Anwar et al. 2018).
- That committing to a noise or power allocation against an adversary who
  chooses bands or channels is new, or that our band-selection subgame or its
  solution is new (Xu and Baykal-Gürsoy 2023; Xu et al. 2021; Jia et al. 2016;
  Yang et al. 2013; Altman et al. water-filling games).
- That MI-optimal or energy-constrained noise injection, or Fano-motivated MI
  minimization, is new (Jin et al. 2022; Woo et al. 2026).
- That random clocks, random DVFS, frequency hopping, or combined clock and
  voltage noise are new, in papers or patents (Yang et al. 2005; Lagasse et al.
  2019; US 2018/0309566 A1; US 10,958,414).
- That shifting clock or DVFS states to move leakage out of an observer's band
  is new (EMMasker 2024).
- That modeling a resource-bounded or adaptive side-channel adversary is new
  (Doychev and Köpf 2015; Köpf and Basin 2007).
- That shaping a power trace against a policy-aware inference adversary under
  an energy budget is new (Li, Oechtering, and Gündüz 2019, and the smart-meter
  battery literature).
- That training a noise defense against an adaptive, learned attacker is new
  (Gammell et al. 2024; AIAShield).
- That randomization by itself is the contribution or is necessary (Wu,
  Wagner, and Suh 2020). Any value of mixing must come from the observer's best
  response and must be measured.
- That the RTL/VCD-to-trace pipeline, the generation method, or a 100k to 1M
  trace scale is new (RTL-PSC 2019; VeriSide 2025; AIPS 2026; SoftPower).
- Any security guarantee from MI, TVLA, Fano, or a failed attack. MI estimators
  are biased (IACR ePrint 2011/322 and 2013/706), and Fano bounds are loose
  (roadmap T3).
- That simulated results transfer to silicon, or to Screaming-Channels-style
  radio coupling, before the proxy calibration gate and owned-hardware tests
  pass.
- "First," "novel," "no prior work," or "unexplored" as fact; or "to our
  knowledge" before Upgrade 5 is complete.
- "Signaling game," unless the model has private information and meaningful
  signals.
- That the method protects deployed products or third-party devices.

Added in Deep search 2:

- That commitment (Stackelberg) by itself distinguishes the model from
  Nash-based wireless or side-channel games while the game is zero-sum;
  values and defender strategies coincide (Korzhyk et al. 2011; von Stengel
  and Zamir 2010).
- That using information leakage as a game's utility, or showing that hidden
  randomization leaks less than the average of its parts, is new (Alvim et
  al. 2017, 2018, 2022).
- That treating side-channel noise as wiretap artificial noise, or optimizing
  noise energy against an uncertain attacker feature extractor, is new (Jin
  et al. 2022; Jin, Xu, and Cai 2024).
- That an eavesdropper limited to a few frequencies, a defender who
  randomizes which channel to protect, or Bayesian eavesdropper types are new
  (Xu et al. 2021; Xu and Baykal-Gürsoy 2020, 2023).
- That a transmitter randomizing its frequency against a band-limited
  listener or jammer is a new game (wireless frequency-hopping games; log,
  Deep search 2, group H).
- That combining randomized clocking with dummy current or a dummy load is
  new (US 11,594,962 B2; Lagasse et al. 2019), or that choosing a randomized
  clock's frequency set under an overhead budget is new (Klasson Landin and
  Jilborg 2023).
- That randomized or spread-spectrum clocking hides leakage from an adaptive
  receiver (de-spreading: IEEE TEMC 2024; IEEE TIFS 2025), or that a filter
  cannot undo randomized voltage scaling (Galli et al. 2024 report that
  high-pass filtering restores most of the leakage).
- That Bayesian Stackelberg commitment to a randomized defense on an embedded
  system is new (Ayrault et al. 2021, for moving-target reconfiguration).
- That EMMasker is deterministic or ignores adaptation: it randomizes burst
  timing and retrains the classifier on defended traces; only its receiver
  band is fixed.
- That maximizing the entropy of the defense mix is our idea or our method
  (Yao and Zhang 2024 recommend it; we compute equilibrium mixes, which need
  not have maximal entropy).

## (d) Reviewer objections and answers (Deep search 2)

Full evidence and quotes are in the log, section "Deep search 2
(2026-10-30)", gaps 1 to 3.

"This is just Yao and Zhang." Their 2024 paper (with a 2012 Chinese
original) is a static designer-versus-attacker game whose payoffs are abstract
MI scalars per leak type, with unspecified strategy lists, no signal or
measurement model, no costs beyond an unspecified constraint set, no computed
equilibrium, no example, and no data; its defense advice is to maximize the
entropy of the strategy mix. They own the framing, and we cite it. They do not
model a defender's physical knobs, an observer's band, filter, or trace
budget, commitment, prior robustness, or estimation from traces.

"This is just EMMasker." EMMasker's receiver stays at 810 MHz, and its threat
model sets aside observers who use several radios or sweep the spectrum as
too costly. That excluded observer is our follower, and its cost is a modeled
price. EMMasker's randomization (burst timing and a clock-scaled intensity
rule) is hand-set, and its clock shift is a side effect of load; ours is a
distribution over directly selected clock modes and dummy-current levels that
solves a priced game. EMMasker reports one classifier's accuracy on five
websites with one GPU; we report MI, success versus trace budget, and
session-level intervals for key leakage from an embedded device. We include
an EMMasker-style baseline against the same band-switching observer and will
report a tie if there is one.

"This is the wireless cooperative-jamming game applied to EM." With additive
noise, Gaussian leakage, and a single-band observer, our band subgame is the
Xu and Baykal-Gürsoy game, and we cite its solution. Three things do not
transfer. Clock modes move and reshape the leakage instead of adding noise to
a fixed channel. The observer accumulates evidence about a fixed key over a
costly trace budget, which erodes dummy noise roughly as 1/N and makes the
value of mixing depend on whether the observer spends bandwidth detecting the
mode. Costs and payoffs come from device energy, latency, and false alarms
and from trace data with uncertainty, not from secrecy rates. We do not list
commitment as a difference while the game is zero-sum, because Stackelberg
and Nash values then coincide.

The differences a reviewer is most likely to accept, strongest first:

1. A measurement observer that best-responds with band, filter, and trace
   budget at a cost, inside a physical side-channel defense game. EMMasker's
   own threat model leaves this observer out, and no side-channel game found
   models it.
2. Defender actions that move the leakage, combined with fixed-key evidence
   accumulated over a costly trace budget, so that the observer's measurement
   choice decides whether the defender's randomization is hidden or visible.
   Neither the wireless jamming games nor the information-leakage games
   couple these.
3. A prior-robust policy over observer types, with payoffs estimated from
   traces under session-level uncertainty, where the closest Bayesian analog
   (Xu et al. 2021) uses a fixed prior and notes, without a remedy, that a
   wrong belief is exploitable.

Points 2 and 3 are differences in the model until a theorem or measurement
shows that they change the recommended policy (Upgrades 1 and 3).
