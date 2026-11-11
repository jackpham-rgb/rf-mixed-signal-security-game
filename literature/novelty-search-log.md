# Novelty search log

## Rule

This log supports a search; it does not prove absence. “No direct match found”
means only that the recorded queries and citation paths did not expose one.
Before submission, an advisor should review the claim and a fresh search should
be run.

For every search record:

- date and database;
- exact query;
- inclusion/exclusion criteria;
- promising papers and backward/forward citations inspected;
- patents and non-English/alternate terminology;
- resulting change to the proposed claim.

## Initial boundary, 2026-10-23

### Established and therefore not claimable as new

- power and EM side-channel analysis;
- dummy activity, hiding, masking, shuffling, clock randomization;
- random/dynamic voltage-frequency scaling as a side-channel countermeasure;
- optimal artificial-noise allocation under a mutual-information objective;
- adaptive/software EM masking;
- game-theoretic timing protection and cloud side-channel allocation;
- game-theoretic anti-jamming and wireless spectrum selection;
- voltage/fault monitors and clock/fault detection;
- general Bayesian, signaling, zero-sum, and Stackelberg security games.

### Narrow hypothesis to investigate

A single framework in which a resource-constrained embedded defender commits to
a stochastic mixed-signal spectral/power policy, physical observer types
best-respond through measurement-band/filter/trace allocation, and the resulting
policy receives formal leakage and robustness guarantees plus owned-hardware
validation.

Potentially differentiating elements must be evaluated separately:

1. cross-channel power plus near-field EM policy;
2. adaptive observer with explicit capture-resource choices;
3. equilibrium policy under energy, latency, and false-alarm costs;
4. robust uncertainty over observer type;
5. measured advantage over robust optimization and adaptive filtering.

## Initial searches and findings

### Query group A: game-theoretic physical side channels

Queries:

- `"Stackelberg" electromagnetic side-channel countermeasure`
- `"signaling game" power side channel hardware security`
- `game theoretic physical side channel defense power EM`

Finding: direct results included Stackelberg timing-defense work and games for
cloud/mobile sensor leakage, but the initial search did not expose the exact
physical RF/EM adaptive-defense model. This is promising, not conclusive.

Key nearby work:

- Doychev and Köpf, “Rational Protection against Timing Attacks,” CSF 2015.
  https://doi.org/10.1109/CSF.2015.39
  (Corrected 2026-10-30: an earlier draft miscredited this to Köpf and Basin.
  Köpf and Basin's relevant paper is the CCS 2007 work on adaptive side-channel
  attacks. See the Deep search 2026-10-30 corrections below.)
- “Toward a Protected Cloud Against Side Channel Attacks: A Game-Theoretic
  Framework,” Allerton 2018.
  https://doi.org/10.1109/ALLERTON.2018.8636050
- “Analyzing Defense Strategies Against Mobile Information Leakages: A
  Game-Theoretic Approach,” arXiv:1904.13352.
  https://arxiv.org/abs/1904.13352

Action: inspect all citing papers and search terms “leader-follower,” “Bayesian
defender,” “inspection game,” “moving-target defense,” and “physical leakage.”

### Query group B: adaptive EM masking and optimal noise

Queries:

- `adaptive electromagnetic side channel obfuscation random frequency defense`
- `mutual information minimization side-channel optimal noise injection`

Nearby work:

- “EMMasker: EM Obfuscation Against Website Fingerprinting,” MADWeb/NDSS 2024.
  https://www.ndss-symposium.org/ndss-paper/auto-draft-485/
- “Mutual Information Minimization for Side-Channel Attack Resistance via
  Optimal Noise Injection,” arXiv:2504.20556.
  https://arxiv.org/abs/2504.20556
- Geng, Kwiat, Kamhoua, and Shi, “On Random Dynamic Voltage Scaling for
  Internet-of-Things: A Game-Theoretic Approach,” IEEE TCAD, vol. 37, no. 1,
  pp. 123-132, 2018. https://doi.org/10.1109/TCAD.2017.2717780
  (Corrected 2026-10-30: an earlier draft credited this to “Yu et al.” The game
  is a nonzero-sum game over the alarm threshold of an off-chip supply-voltage
  monitor, not a game over the DVFS policy itself. See the Deep search
  2026-10-30 corrections below.)
- “Combining Clock and Voltage Noise Countermeasures Against Power Side-Channel
  Analysis,” ASAP 2019.
  https://doi.org/10.1109/ASAP.2019.00009

Impact on claim: adaptive masking, MI minimization, and random DVFS cannot be the
novelty. The game must demonstrate a strategic/adaptive measurement response and
must compare against these simpler formulations.

### Query group C: realistic RF/EM channels

- Camurati et al., “Screaming Channels,” ACM CCS 2018.
  https://doi.org/10.1145/3243734.3243802
- Ayoub et al., “BlueScream: Screaming Channels on Bluetooth Low Energy,” ACSAC
  2024. https://doi.org/10.1109/ACSAC63791.2024.00060
- Danial et al., “SCNIFFER: Low-Cost, Automated, Efficient Electromagnetic
  Side-Channel Sniffing,” IEEE Access 2020.
  https://doi.org/10.1109/ACCESS.2020.3025022
- “Active Electromagnetic Side-Channel Analysis: Crossing Physical Security
  Boundaries through Impedance Variations,” IACR TCHES.
  https://tches.iacr.org/index.php/TCHES/article/view/12686

Impact: RF leakage and automated probe/band search are real and established.
Use this work to define an adaptive evaluator, not to reproduce attack novelty.

### Query group D: defense limitations and fault monitoring

- Galli et al., “The Impact of Run-Time Variability on Side-Channel Attacks
  Targeting FPGAs,” ICECS 2024.
  https://doi.org/10.1109/ICECS61496.2024.10848741
- Zhang et al., “DARPT: Defense Against Remote Physical Attack Based on TDC,”
  DAC 2022. https://doi.org/10.1145/3489517.3530494
- Gao et al., “EO-Shield,” ASP-DAC 2023.
  https://doi.org/10.1145/3566097.3567924
- Ghosh et al., “R-STELLAR,” IEEE OJ-SSCS 2025.
  https://doi.org/10.1109/OJSSCS.2025.3571334

Action: verify titles, versions, conclusions, and citation context from primary
PDFs before citing. Do not rely on search snippets.

### Query group E: patents

- Oracle, “Camouflaging EMI Fingerprints…,” US 11,012,862 B2.
  https://patents.google.com/patent/US11012862B2/en
- “Circuitry and Methods for Attenuation and Obfuscation…,”
  US 2025/0005209 A1.
  https://patents.google.com/patent/US20250005209A1/en

Impact: do not claim broad ownership of adaptive EM camouflage. Any contribution
must be a narrow mathematical/experimental method, not the generic concept.

### Query group F: pre-silicon leakage simulation and large trace datasets

**Status: placeholder, not yet searched.** Added with
`theory/high-volume-data-and-digital-circuit-extension.md`. Until this group is
searched and logged, make no claim that the dataset, its scale, or its
generation method is new.

Planned queries:

- `pre-silicon power side-channel leakage assessment RTL simulation`
- `gate-level simulation power side channel VCD switching activity`
- `RTL leakage detection toggle count Hamming distance pre-silicon`
- `synthetic side-channel trace dataset generation simulation`
- `side-channel dataset ASCAD AES_HD CHES CTF FPGA power traces`
- `large-scale side-channel evaluation statistics multiple comparisons TVLA`
- `Bayesian hierarchical model side-channel leakage across devices`
- `mutual information estimator bias side-channel evaluation`
- `clock gating frequency hopping dummy logic countermeasure gate-level evaluation`

Also check: commercial pre-silicon leakage tools (vendor white papers), open
pre-silicon tools on GitHub, and the citation graphs of the public datasets
used.

Record for each hit: what is simulated (RTL, gate, SPICE), dataset size and
grouping, statistics used, whether defenses are compared, and whether an
adaptive observer or game appears. Expected outcome: the simulation pipeline
and dataset scale are prior art, and any contribution is the game-theoretic
evaluation with propagated uncertainty. Update the claim template below if this
expectation is wrong in either direction.

## Four brainstorm directions: disposition

### 1. SoC substrate/supply coexistence game

Keep as a strong alternative or later application. Physical coupling and on-chip
DVFS games exist separately; a game using measured substrate/PDN transfer
functions may be defensible. It is less accessible to validate without suitable
silicon, and “why not centralized optimization?” is a major reviewer question.

Starting references:

- Afzali-Kusha et al., “Substrate Noise Coupling in SoC Design: Modeling,
  Avoidance, and Validation,” Proceedings of the IEEE.
  https://ieeexplore.ieee.org/document/4077249
- Puschini et al., “Temperature-Aware Distributed Run-Time Optimization on
  MP-SoC Using Game Theory,” ISVLSI 2008.
  https://doi.org/10.1109/ISVLSI.2008.33
- Rosen, “Existence and Uniqueness of Equilibrium Points for Concave N-Person
  Games,” Econometrica 1965. https://doi.org/10.2307/1911749

### 2. Stackelberg digitally assisted analog calibration

Strong theory project, especially where simultaneous adaptive loops diverge and
leader/follower timescales restore stability. It is less directly RF-security
focused and risks being two-timescale stochastic approximation relabeled.

Starting references:

- Chiu et al., “LMS Adaptive Digital Background Calibration of Pipelined ADCs,”
  IEEE TCAS-I 2004. https://doi.org/10.1109/TCSI.2003.821306
- Fiez et al., “Implicit Learning Dynamics in Stackelberg Games,” ICML 2020.
  http://proceedings.mlr.press/v119/fiez20a/fiez20a.pdf

### 3. Evolutionary allocation for biosensor ADC arrays

Potentially high novelty and proof depth, but it does not satisfy the user's RF
focus as directly. Ethical constraints and clinically meaningful loss functions
need domain collaborators.

Starting references:

- “Adaptive Resolution ADC Array for an Implantable Neural Sensor,” IEEE
  TBioCAS. https://doi.org/10.1109/TBCAS.2011.2145418
- “Potential-Game Approach for Information-Maximizing Sensor Planning,” IEEE
  TCST. https://doi.org/10.1109/TCST.2015.2403475

### 4. Mixed-signal security signaling game

Selected, narrowed to adaptive physical observation and resource-constrained
spectral/power defense. “Signaling game” should be used only if the model has
private information and meaningful signals/beliefs. Otherwise call it Bayesian
Stackelberg or zero-sum; terminology must follow the mathematics.

## Required pre-submission search

1. Search title/abstract/full text in IEEE, ACM, IACR, arXiv, Springer, Elsevier.
2. Search all combinations of:
   - physical/power/EM/RF side channel;
   - Stackelberg/Bayesian/signaling/inspection/minimax/robust game;
   - adaptive masking/noise injection/DVFS/frequency hopping/dummy current;
   - probe placement/band selection/trace allocation.
3. Perform backward and forward citation chaining on the ten nearest papers.
4. Search Google Patents, Espacenet, and USPTO by concept and CPC classes.
5. Contact a hardware-security or mixed-signal faculty member with a one-page
   model and nearest-work table.
6. Rewrite claim to identify exact difference, not “no one did this.”

## Claim template

Safe before completion:

> We investigate a Bayesian Stackelberg formulation for jointly allocating
> mixed-signal defense activity against resource-bounded adaptive physical
> observers, and evaluate whether it improves the leakage-overhead frontier
> relative to fixed, randomized, and robust-optimization baselines.

Unsafe until independently established:

> This is the first game-theoretic adaptive RF side-channel defense.

## Deep search 2026-10-30

### Scope, method, and limits

Claim under test (as worded in the request for this pass):

> A single framework where a resource-constrained embedded defender commits
> (Stackelberg/Bayesian) to a stochastic mixed-signal spectral/power policy
> (clock/frequency modes plus dummy-current/noise shaping) against a
> resource-bounded adaptive physical observer that best-responds by choosing
> measurement band, filter, and trace budget, with formal leakage (mutual
> information / Fano) and robustness (prior-uncertainty) analysis, validated by
> large simulated RTL/VCD trace datasets and later owned-hardware traces.

Method:

- Searcher: an AI coding agent, one session on 2026-10-30.
- Database for every query: the Cursor WebSearch tool, a general web search
  engine that returns ranked pages plus an automatic summary. Result pages came
  from IEEE Xplore, ACM DL, IACR ePrint and TCHES, arXiv, NDSS, IOPscience,
  Springer, dblp, researchr, NSF PAR, university repositories, and patent
  aggregators. Facts recorded below come from each hit's abstract, metadata
  page, or full text, not from the automatic summaries. Where a summary only
  repeated details from my own query (for example volume and page numbers),
  those details are left out unless a source page confirmed them.
- Direct fetches: arXiv 2504.20556 (full HTML including the reference list,
  read); the EMMasker PDF (sections I to V and part of VI, read); the IOPscience full text of
  Yao and Zhang 2024 (HTTP 403, not read; the doi.org fetch also timed out).
- Not done in this pass: field-restricted searches inside IEEE Xplore, ACM DL,
  Scopus, or Web of Science; Google Scholar "cited by" (forward) chaining;
  Espacenet, USPTO, or CPC-class patent searches; non-English sources such as
  CNKI. These remain required by the pre-submission list above.

Inclusion rule. A work counts as "near" if it shares at least two of these
elements with the claim:

- E1: a defender that commits to, or optimizes, a randomized physical
  countermeasure under explicit cost;
- E2: clock/frequency modes or dummy-current/noise as the action set;
- E3: an observer that adapts its measurement (band, filter, location, or
  trace budget) to the defense;
- E4: an information-theoretic leakage objective or bound;
- E5: robustness to uncertainty about the observer type;
- E6: validation on simulated or measured power/EM traces.

Pure attack papers are kept only when they document an observer capability that
the model uses.

Standing rule, restated: "no direct match found" below means only that these
recorded queries and the citation paths listed here did not expose one. It is
not evidence of novelty and must not be cited as such.

### Corrections to earlier entries in this log

The earlier text above is left unchanged (append-only). Cite from this list
instead.

1. Query group A attributes "Rational Protection against Timing Attacks" (CSF
   2015) to "Köpf and Basin." The authors are Goran Doychev and Boris Köpf
   (IEEE CSF 2015, pp. 526-536). Köpf and Basin wrote a different paper: "An
   Information-Theoretic Model for Adaptive Side-Channel Attacks," ACM CCS
   2007, pp. 286-296, https://doi.org/10.1145/1315245.1315282.
2. Query group B attributes "On Random Dynamic Voltage Scaling for
   Internet-of-Things: A Game-Theoretic Approach" (IEEE TCAD 2018) to "Yu et
   al." The authors are Hui Geng, Kevin A. Kwiat, Charles A. Kamhoua, and Yiyu
   Shi (vol. 37, no. 1, pp. 123-132). Its game is not over the DVFS policy. The
   paper shows that lowering the off-chip supply undermines random dynamic
   voltage scaling, adds a supply-voltage monitor with an alarm, and models the
   choice of the alarm threshold as a nonzero-sum Nash game between attacker
   and circuit supplier.
3. arXiv:2504.20556 (Woo et al.) now has a peer-reviewed version at IEEE ISIT
   2026, https://doi.org/10.1109/ISIT62367.2026.11653960. Its direct
   predecessor is Jin, Xu, Bettati, and Christodorescu, IEEE WIFS 2022,
   https://doi.org/10.1109/WIFS55849.2022.9975384.
4. The Allerton 2018 cloud game is by Ahmed H. Anwar, George Atia, and Mina
   Guirguis (pp. 78-83). The provider picks an intrusion-detection security
   level, the attacker picks a VM collocation duration, and the solution is a
   Nash equilibrium.

### Exact queries run

All 54 queries used the Cursor WebSearch tool on 2026-10-30. "D" marks a
discovery query. "V" marks a query run to verify a citation found earlier.
Queries are listed in the order run within each cluster.

Cluster 1, game-theoretic side-channel and physical-security defenses:

- D `Stackelberg game power side-channel countermeasure defender attacker hardware`
- V `"Rational Protection against Timing Attacks" Köpf Basin CSF 2015`
- D `game theory electromagnetic side-channel defense adaptive attacker mixed strategy`
- V `"Toward a Protected Cloud Against Side Channel Attacks: A Game-Theoretic Framework" Allerton 2018`
- D `"Bayesian Stackelberg" side-channel leakage defense`
- D `game-theoretic side-channel countermeasure selection mutual information leakage cost trade-off equilibrium 2023 2024 2025`
- V `"Bypass Leakage Risk Assessment Based on Mutual Information Game" CSAT 2023 authors`
- D `game theory noise injection power analysis IoT defender attacker number of traces equilibrium`
- D `zero-sum game side-channel countermeasure attacker chooses measurement frequency band defender randomizes clock`
- V `Köpf Basin "An information-theoretic model for adaptive side-channel attacks" CCS 2007`
- D `game theory side-channel attack defense survey hardware security game-theoretic models review`
- D `Stackelberg game cache side-channel defense randomization attacker leader follower`
- V `"Side-Channel Attack Security Risk Assessment Model Based on Mutual Information Game" Journal of Physics Conference Series 2732 authors`
- D `Stackelberg game side-channel defense IoT energy constraint adaptive attacker 2025 2026 power EM leakage`

Clusters 2 and 3, adaptive EM masking and MI-optimal noise:

- V `EMMasker EM obfuscation website fingerprinting MADWeb NDSS 2024 authors`
- V `Jin Xu Bettati Christodorescu "Optimal energy efficient design of artificial noise to prevent side-channel attacks" WIFS 2022`
- D `adversarial learning noise generator countermeasure deep learning side-channel attack minimax trained against attacker`
- D `robust side-channel countermeasure design unknown attacker uncertainty worst-case leakage optimization noise allocation minimax`
- V `Woo Ryu Seo Kim Lee Cassuto Kim "mutual information minimization" side-channel optimal noise injection ISIT 2025 OR ITW 2025 conference`

Clusters 4 and 5, random DVFS, clock randomization, combined clock and voltage
noise:

- V `"On Random Dynamic Voltage Scaling for Internet-of-Things" game-theoretic approach IEEE TCAD`
- V `"Combining Clock and Voltage Noise Countermeasures Against Power Side-Channel Analysis" ASAP 2019 authors`
- D `random dynamic voltage and frequency scaling side-channel countermeasure DPA RDVFS attack evaluation`
- D `frequency hopping clock randomization countermeasure EM side-channel attacker filter resynchronization defeat`
- V `"Power attack resistant cryptosystem design: a dynamic voltage and frequency switching approach" DATE 2005 Yang Wolf Vijaykrishnan Serpanos Xie DOI`
- V `eprint 2022/1416 "Do Not Rely on Clock Randomization" side-channel attack protected hardware AES Brisfors Moraitis Dubrova`

Cluster 6, anti-jamming, wiretap, and spectrum games (transplantable
mathematics, different domain):

- V `"Bayesian Stackelberg game for antijamming transmission with incomplete information" IEEE Communications Letters`
- V `"Coping with a smart jammer in wireless networks: A Stackelberg game approach" IEEE Transactions on Wireless Communications 2013`
- V `"Jamming games in the MIMO wiretap channel with an active eavesdropper" Mukherjee Swindlehurst`
- D `TEMPEST electromagnetic emanation eavesdropper jamming countermeasure game theory optimal noise`
- D `Altman Avrachenkov Garnaev jamming game water-filling closed form power allocation across channels user selects channel`
- D `eavesdropper selects subchannel artificial noise allocation game parallel channels secrecy zero-sum OFDM`
- V `"Power Allocation for Cooperative Jamming Against a Strategic Eavesdropper Over Parallel Channels" IEEE Transactions on Information Forensics and Security volume 18 pages Xu Baykal-Gursoy Spasojevic`
- V `"A Game-Theoretic Approach for Probabilistic Cooperative Jamming Strategies over Parallel Wireless Channels" Xu Baykal-Gursoy Spasojevic IEEE CNS 2021`
- V `Mukherjee Swindlehurst "Jamming Games in the MIMO Wiretap Channel With an Active Eavesdropper" IEEE Transactions on Signal Processing vol. 61 no. 1 pp. 82-91 2013`

Cluster 7, moving-target, randomized-defense, and signaling games in hardware
security:

- D `moving target defense power side-channel hardware randomized reconfiguration game-theoretic`
- D `signaling game hardware security Trojan detection Bayesian game Kamhoua testing`
- V `RandOhm mitigating impedance side-channel attacks randomized circuit configurations ICCAD 2024 authors`

Added cluster, power-trace shaping against an inference adversary (smart-meter
privacy):

- D `smart meter privacy battery load hiding adversary hypothesis testing game-theoretic mutual information energy cost`
- V `"Privacy against a hypothesis testing adversary" Li Oechtering Gündüz IEEE Transactions on Information Forensics and Security`
- V `"Privacy Against a Hypothesis Testing Adversary" IEEE TIFS vol. 14 no. 6 pp. 1567 2019`

Cluster 8, realistic RF/EM channels and automated observer search:

- V `Camurati "Screaming Channels: When Electromagnetic Side Channels Meet Radio Transceivers" CCS 2018 DOI`
- V `"BlueScream" Screaming Channels Bluetooth Low Energy ACSAC 2024 Ayoub`
- V `SCNIFFER low-cost automated efficient electromagnetic side-channel sniffing IEEE Access 2020 Danial`
- D `automated EM probe positioning frequency band selection side-channel leakage search reinforcement learning Bayesian optimization`
- D `Screaming Channels countermeasure mixed-signal chip defense noise frequency hopping mitigation`

Cluster 9 (Query Group F), pre-silicon leakage simulation and trace datasets:

- D `pre-silicon power side-channel leakage assessment RTL simulation VCD switching activity RTL-PSC`
- D `synthetic side-channel trace dataset generation gate-level simulation deep learning large dataset million traces`
- V `ASCAD database deep learning side-channel analysis Benadjila Journal of Cryptographic Engineering 2020`
- D `EMSim microarchitecture-level simulation electromagnetic side-channel signals HPCA 2020`
- D `pre-silicon evaluation hiding countermeasures clock randomization dummy logic noise generator gate-level simulation TVLA comparison`
- V `"RTL-PSC" VTS 2019 DOI 10.1109/VTS.2019`
- D `side-channel leakage mutual information estimator bias evaluation Bayesian hierarchical model across devices sessions`
- V `AIPS AI-Based Power Simulation for Pre-Silicon Side-Channel Security Evaluation TCHES 2026 authors`

Patents:

- D `patent side-channel countermeasure randomized clock frequency noise injection selected by game theory policy attacker model`

### Nearest-work findings

The condensed table is in `paper/related-work-nearest-table.md`. Full entries
follow, grouped by cluster. "Read" says what was actually read.

1. **Doychev and Köpf** (cluster 1). G. Doychev and B. Köpf, "Rational
   Protection against Timing Attacks," Proc. IEEE 28th Computer Security
   Foundations Symposium (CSF), pp. 526-536, 2015.
   https://doi.org/10.1109/CSF.2015.39 (author PDF:
   https://boriskoepf.de/papers/csf15.pdf). Read: abstract, introduction, and
   the opening of the model section.
   - Shares: a two-stage Stackelberg game; a resource-bounded adversary who
     splits its budget between measurements and offline key search; an
     equilibrium protection that trades defender cost against a bound on
     key-recovery probability; a case study on a real library.
   - Differs: timing channel with input blinding and bucketing on discrete-log
     cryptography; the defender commits to one pure configuration (key length,
     bucket count), not a randomized policy; no spectral, band, filter, power,
     or EM model; no observer types.
2. **Geng, Kwiat, Kamhoua, and Shi** (cluster 4, the random-DVS game). H. Geng,
   K. A. Kwiat, C. A. Kamhoua, and Y. Shi, "On Random Dynamic Voltage Scaling
   for Internet-of-Things: A Game-Theoretic Approach," IEEE Trans.
   Computer-Aided Design of Integrated Circuits and Systems, vol. 37, no. 1,
   pp. 123-132, 2018. https://doi.org/10.1109/TCAD.2017.2717780. Read:
   abstract and the opening of the introduction.
   - Shares: a game-theoretic analysis of a physical power countermeasure on
     IoT devices, with alarm and denial-of-service costs.
   - Differs: the decision is the alarm threshold of a supply-voltage monitor
     against an undervolting attacker, solved as a nonzero-sum Nash
     equilibrium; no committed randomized policy; no band, filter, or trace
     choice; no MI bound.
3. **Yao and Zhang** (cluster 1). J. Yao and T. Zhang, "Side-Channel Attack
   Security Risk Assessment Model Based on Mutual Information Game," J. Phys.:
   Conf. Ser., vol. 2732, 012002, 2024.
   https://doi.org/10.1088/1742-6596/2732/1/012002. Companion: J. Yao and T.
   Zhang, "Bypass Leakage Risk Assessment Based on Mutual Information Game,"
   Proc. Int. Conf. Computer Science and Automation Technology (CSAT), 2023.
   https://doi.org/10.1109/CSAT61646.2023.00046. Read: abstracts only (full
   text not retrieved).
   - Shares: a game between a cryptographic chip designer and an attacker with
     mutual-information payoffs and Nash-equilibrium strategy selection.
   - Differs, as far as the abstracts show: Nash rather than commitment;
     strategies are options in a case analysis; no physical channel model,
     band choice, cost model, or trace data are mentioned. Highest residual
     risk in this list because the full text was not read.
4. **Woo et al., with predecessor Jin et al.** (cluster 3). J. Woo, D. Ryu, D.
   Seo, Y.-S. Kim, N. Lee, Y. Cassuto, and Y. Kim, "Mutual Information
   Minimization for Side-Channel Attack Resistance via Optimal Noise
   Injection," IEEE ISIT 2026,
   https://doi.org/10.1109/ISIT62367.2026.11653960; extended version
   arXiv:2504.20556 (v1 April 2025), https://arxiv.org/abs/2504.20556.
   Predecessor: S. Jin, M. Xu, R. Bettati, and M. Christodorescu, "Optimal
   Energy Efficient Design of Artificial Noise to Prevent Side-Channel
   Attacks," IEEE WIFS 2022, pp. 1-6,
   https://doi.org/10.1109/WIFS55849.2022.9975384. Read: Woo et al. full HTML
   including references; Jin et al. abstract.
   - Shares: minimize total or worst-case MI between the secret and the leakage
     under an artificial-noise power budget for resource-constrained devices;
     Fano is used to motivate MI minimization.
   - Differs: the observer is fixed and does not respond; noise only, no clock
     modes; per-leakage-point allocation with known signal powers; numerical
     results only, with no estimation uncertainty or measured traces.
5. **Wu, Wagner, and Suh** (clusters 1 and 3). B. Wu, A. B. Wagner, and G. E.
   Suh, "A Case for Maximal Leakage as a Side Channel Leakage Metric,"
   arXiv:2004.08035, 2020. https://arxiv.org/abs/2004.08035. Read: abstract
   and main theorem statement.
   - Shares: the side-channel cost-leakage trade-off posed as an optimization
     (an LP) over randomized protection schemes.
   - Differs: the observer is not strategic; under maximal leakage, a mix of at
     most two deterministic schemes is optimal, so randomization by itself is
     not a contribution; abstract channel, not spectral or power.
6. **Li, Oechtering, and Gündüz** (added cluster, power-trace shaping). Z. Li,
   T. J. Oechtering, and D. Gündüz, "Privacy Against a Hypothesis Testing
   Adversary," IEEE Trans. Information Forensics and Security, 2019
   (published online November 2018). https://doi.org/10.1109/TIFS.2018.2882343;
   preprint https://arxiv.org/abs/1807.01916. Read: abstract and conclusions.
   - Shares: a management unit reshapes a power-consumption sequence under an
     average distortion (energy) budget to defeat a fully informed,
     policy-aware hypothesis-testing adversary; guarantees are KL-divergence
     and Chernoff-information exponents.
   - Differs: smart-meter time scale; the adversary only chooses its test, not
     a band, filter, or trace budget; binary hypothesis; no clock modes or
     chip-level leakage.
7. **Xu and Baykal-Gürsoy, with the Bayesian variant by Xu, Baykal-Gürsoy, and
   Spasojević** (cluster 6). Z. Xu and M. Baykal-Gürsoy, "Power Allocation for
   Cooperative Jamming Against a Strategic Eavesdropper Over Parallel
   Channels," IEEE Trans. Information Forensics and Security, vol. 18, pp.
   846-858, 2023. https://doi.org/10.1109/TIFS.2022.3228520. Companion: Z. Xu,
   M. Baykal-Gürsoy, and P. Spasojević, "A Game-Theoretic Approach for
   Probabilistic Cooperative Jamming Strategies over Parallel Wireless
   Channels," IEEE CNS 2021, pp. 47-55.
   https://doi.org/10.1109/CNS53000.2021.9705044. Read: abstracts; CNS
   introduction.
   - Shares: a defender spreads limited noise (jamming) power over parallel
     channels while a strategic eavesdropper picks which channels to attack;
     water-filling and threshold-type equilibria; the CNS paper adds a Bayesian
     game for unknown channel state.
   - Differs: secrecy of intentional wireless transmissions, not unintentional
     leakage; Nash rather than commitment; no clock modes, trace budget, or
     payoffs estimated from traces. This is the most likely source of the
     mathematics of our band-selection subgame.
8. **Yang et al., with Jia et al.** (cluster 6). D. Yang, G. Xue, J. Zhang, A.
   Richa, and X. Fang, "Coping with a Smart Jammer in Wireless Networks: A
   Stackelberg Game Approach," IEEE Trans. Wireless Communications, vol. 12,
   no. 8, pp. 4038-4047, 2013.
   https://doi.org/10.1109/TWC.2013.071913121570. Companion: L. Jia, F. Yao,
   Y. Sun, Y. Niu, and Y. Zhu, "Bayesian Stackelberg Game for Antijamming
   Transmission With Incomplete Information," IEEE Communications Letters,
   vol. 20, no. 10, pp. 1991-1994, 2016.
   https://doi.org/10.1109/LCOMM.2016.2598808. Read: abstracts.
   - Shares: the leader commits to a power strategy and a smart follower
     best-responds; Jia et al. add incomplete information (Bayesian types);
     existence and uniqueness proofs.
   - Differs: domain mismatch; the follower is a jammer harming a link and the
     payoffs are throughput or SINR, not leakage; no measurement band, trace
     budget, or hardware cost model.
9. **EMMasker** (cluster 2). M. Aldeen, S. Liang, Z. Zhang, L. Guo, Z. Song,
   and L. Cheng, "EMMasker: EM Obfuscation Against Website Fingerprinting,"
   Workshop on Measurements, Attacks, and Defenses for the Web (MADWeb),
   co-located with NDSS, 2024. https://doi.org/10.14722/madweb.2024.23018.
   Read: full text, sections I to V and part of VI.
   - Shares: a software defense that injects GPU rendering noise and pushes the
     GPU's DVFS clock state out of a band-limited SDR observer's band, scaling
     noise intensity with the clock state, with overhead measured. Its threat
     model explicitly assumes the observer cannot cover the whole spectrum.
     This is the closest mechanism found.
   - Differs: the observer's band is fixed (810 MHz) and is not a best
     response; the classifier is retrained on defended traces but the band is
     not; no game and no formal leakage measure; GPU website fingerprinting
     rather than key leakage on an embedded device.
10. **Randomized clock and voltage hiding lineage** (clusters 4 and 5). S. Yang,
    W. Wolf, N. Vijaykrishnan, D. N. Serpanos, and Y. Xie, "Power Attack
    Resistant Cryptosystem Design: A Dynamic Voltage and Frequency Switching
    Approach," DATE 2005, pp. 64-69, https://doi.org/10.1109/DATE.2005.241.
    K. Baddam and M. Zwolinski, "Evaluation of Dynamic Voltage and Frequency
    Scaling as a Differential Power Analysis Countermeasure," VLSID 2007,
    https://doi.org/10.1109/VLSID.2007.79. J. Lagasse, C. Bartoli, and W.
    Burleson, "Combining Clock and Voltage Noise Countermeasures Against Power
    Side-Channel Analysis," IEEE ASAP 2019, pp. 214-217,
    https://doi.org/10.1109/ASAP.2019.00009. Read: abstracts; Baddam and
    Zwolinski abstract, introduction, and conclusion.
    - Shares: the same physical knobs (random voltage and frequency modes,
      combined clock and voltage noise) with overhead reported.
    - Differs: open-loop randomization with hand-set distributions. Baddam and
      Zwolinski show that an observer who detects the frequency mode from
      supply glitches defeats RDVFS, but no work in this group models that
      observer as a player; no game; no MI bound.
11. **Gammell, Raghunathan, and Roy** (adaptive defense learning). J. Gammell,
    A. Raghunathan, and K. Roy, "Power side-channel leakage localization
    through adversarial training of deep neural networks," arXiv:2410.22425,
    2024. https://arxiv.org/abs/2410.22425. Read: abstract and introduction.
    - Shares: a minimax game between a deep-learning attacker and a trainable
      noise generator on power traces, with a penalty on the amount of noise.
    - Differs: the goal is leakage localization; the noise is added in software
      to recorded traces, not a deployable committed device policy; no band,
      trace budget, or energy and latency costs.
12. **RandOhm** (cluster 7). S. Khalaj Monfared, D. Forte, and S. Tajik,
    "RandOhm: Mitigating Impedance Side-channel Attacks using Randomized
    Circuit Configurations," IEEE/ACM ICCAD 2024.
    https://doi.org/10.1145/3676536.3676687 (arXiv:2401.08925). Read: abstract
    and introduction.
    - Shares: a moving-target defense that randomizes the physical circuit
      configuration at run time to decorrelate leakage, with overhead measured
      on FPGA hardware.
    - Differs: the randomization is not optimized against a strategic
      observer; impedance (backscatter) channel rather than power or EM
      emission; no game or leakage bound.
13. **Screaming Channels and BlueScream** (cluster 8). G. Camurati, S. Poeplau,
    M. Muench, T. Hayes, and A. Francillon, "Screaming Channels: When
    Electromagnetic Side Channels Meet Radio Transceivers," ACM CCS 2018, pp.
    163-177, https://doi.org/10.1145/3243734.3243802. G. Camurati, A.
    Francillon, and F.-X. Standaert, "Understanding Screaming Channels: From a
    Detailed Analysis to Improved Attacks," IACR TCHES 2020(3), pp. 358-401,
    https://doi.org/10.13154/tches.v2020.i3.358-401. P. Ayoub, R. Cayre, A.
    Francillon, and C. Maurice, "BlueScream: Screaming Channels on Bluetooth
    Low Energy," ACSAC 2024, https://doi.org/10.1109/ACSAC63791.2024.00060.
    Read: abstracts; the TCHES hopping section; the BlueScream countermeasure
    section.
    - Shares: mixed-signal BLE and Wi-Fi chips leak digital activity through
      the radio; the observer tunes to the leak and, as BLE master, can
      restrict hopping to a few channels. This supports a band-choosing,
      resource-bounded observer.
    - Differs: attack papers; countermeasures are discussed only qualitatively
      (shielding, scheduling cryptography away from transmission, re-keying,
      connection limits); no defense optimization.
14. **SCNIFFER** (cluster 8). J. Danial, D. Das, S. Ghosh, A. Raychowdhury, and
    S. Sen, "SCNIFFER: Low-Cost, Automated, Efficient Electromagnetic
    Side-Channel Sniffing," IEEE Access, vol. 8, pp. 173414-173427, 2020.
    https://doi.org/10.1109/ACCESS.2020.3025022. Read: abstract and motivation.
    - Shares: the observer automates its measurement choice (probe location)
      with TVLA or SNR and counts trace cost (minimum traces to disclosure).
    - Differs: attack-side search over probe position, not band; no defender
      response or game.
15. **AIPS, with RTL-PSC** (cluster 9). Y. Gao, H. Ma, T. Zhang, J. He, Y.
    Zhao, M. Stojilović, and Y. Jin, "AIPS: AI-Based Power Simulation for
    Pre-Silicon Side-Channel Security Evaluation," IACR TCHES, vol. 2026, no.
    2, pp. 441-467, https://doi.org/10.46586/tches.v2026.i2.441-467. M. He, J.
    Park, A. Nahiyan, A. Vassilev, Y. Jin, and M. Tehranipoor, "RTL-PSC:
    Automated Power Side-Channel Leakage Assessment at Register-Transfer
    Level," IEEE VTS 2019, https://doi.org/10.1109/VTS.2019.8758600. Read:
    abstracts and method summaries.
    - Shares: VCD switching activity turned into synthetic transient power
      traces, scaled to 1M traces (AIPS); RTL switching-activity leakage
      assessment (RTL-PSC).
    - Differs: no defense policy, game, or adaptive observer. These show that
      our dataset pipeline and its scale are prior art.

### Secondary works inspected (not in the nearest table)

Each was judged less near than the fifteen entries above. Authors are listed
only where a source page showed them.

- Adaptive side-channel theory: B. Köpf and D. Basin, ACM CCS 2007,
  https://doi.org/10.1145/1315245.1315282 (adaptive attacker, remaining
  uncertainty as a function of the number of measurements; no defender
  optimization).
- Other side-channel games: Anwar, Atia, and Guirguis, Allerton 2018,
  https://doi.org/10.1109/ALLERTON.2018.8636050 (cloud collocation, Nash);
  "Modeling Adversarial Strategies in GPU Side-Channel Attacks: A
  Game-Theoretic Perspective," COMP-SIF 2025,
  https://doi.org/10.1109/COMP-SIF65618.2025.10969860 (abstract only; generic
  two-player game; quality uncertain). The arXiv:1904.13352 mobile-leakage game
  from query group A was not re-inspected.
- Observer capability against clock randomization: M. Brisfors, M. Moraitis,
  and E. Dubrova, "Do Not Rely on Clock Randomization," FPS 2022, LNCS 13877,
  pp. 38-53, https://doi.org/10.1007/978-3-031-30122-3_3 (oversampling plus
  resynchronization plus first-round targeting, under 500 traces); "Synchronous
  Real-Time Sampling Technique for Side-Channel Analysis Against Randomly
  Varying Clock-Based Countermeasures," IEEE Access 2021,
  https://doi.org/10.1109/ACCESS.2021.3103183; IACR ePrint 2013/294
  (synchronous sampling and clock recovery); IACR ePrint 2024/1019 (clock slew
  plus randomization); "Sound of Interference," USENIX Security 2025,
  https://www.usenix.org/system/files/usenixsecurity25-onishi.pdf (clock
  deviation as a defense, checked against a defense-aware attacker).
- Observer measurement search: IACR ePrint 2020/988 (probe positioning with an
  MLP); "Automated Probe Repositioning for On-Die EM Measurements" (Ruhr
  University Bochum, 2019); "Fuzz'EMup" (2026 preprint,
  https://cactilab.github.io/assets/pdf/moradihaghighi2026fuzzemup.pdf), which
  picks the EM frequency band by a Welch t-statistic.
- Wireless and EM game mathematics: A. Mukherjee and A. L. Swindlehurst,
  "Jamming Games in the MIMO Wiretap Channel With an Active Eavesdropper," IEEE
  Trans. Signal Processing, January 2013,
  https://doi.org/10.1109/TSP.2012.2222386 (zero-sum and extensive-form games
  with artificial noise and a secrecy-rate payoff); E. Altman, K. Avrachenkov,
  and A. Garnaev, closed-form water-filling games, IEEE INFOCOM 2007,
  https://doi.org/10.1109/INFOCOM.2007.117, and Telecommunication Systems 2010,
  https://doi.org/10.1007/s11235-010-9308-0; "Mutual Information Games in
  Multiuser Channels With Correlated Jamming," IEEE Trans. Information Theory
  2009, https://doi.org/10.1109/TIT.2009.2027577; "Correlated Jamming on MIMO
  Gaussian Fading Channels," IEEE Trans. Information Theory 2004,
  https://doi.org/10.1109/TIT.2004.833358; L. Xiao, T. Chen, J. Liu, and H.
  Dai, "Anti-Jamming Transmission Stackelberg Game With Observation Errors,"
  IEEE Communications Letters 2015,
  https://doi.org/10.1109/LCOMM.2015.2418776; H. T. Banks, S. L. Grove, K.
  Ito, and J. Toivanen, "Static two-player evasion-interrogation games with
  uncertainty," Computational and Applied Mathematics 2006,
  https://doi.org/10.1590/S1807-03022006000200010 (min-max over probability
  measures where the interrogator picks frequency and angle; radar, not side
  channels).
- Security-game theory sources for T1, T2, and T4: J. Pita, M. Jain, M. Tambe,
  F. Ordóñez, and S. Kraus, "Robust solutions to Stackelberg games,"
  Artificial Intelligence 2010, https://doi.org/10.1016/j.artint.2010.07.002;
  "Signaling in Bayesian Stackelberg Games," AAMAS 2016,
  https://www.cs.cmu.edu/~conitzer/signalingAAMAS16.pdf; "Learning Optimal
  Commitment to Overcome Insecurity," NeurIPS 2014; "Lazy Defenders Are Almost
  Optimal Against Diligent Attackers," AAAI 2014 (limited observation of the
  committed strategy).
- TEMPEST jamming: "Noise-Jamming Effect as a Countermeasure Against TEMPEST
  During High-Speed Signaling," IEEE Trans. Electromagnetic Compatibility 2015,
  https://doi.org/10.1109/TEMC.2015.2466593 (band-noise jamming; no game).
- Hardware-security games and moving-target defenses: "A Game-Theoretic
  Approach for Testing for Hardware Trojans," IEEE TMSCS 2016,
  https://doi.org/10.1109/TMSCS.2016.2564963; "Hardware Trojan Detection Game:
  A Prospect-Theoretic Approach," IEEE TVT 2017,
  https://doi.org/10.1109/TVT.2017.2686853; "Circuit-Variant Moving Target
  Defense for Side-Channel Attacks," ICCWS 2022,
  https://doi.org/10.34190/iccws.17.1.14 (spatial randomization against probe
  placement). No signaling game for physical leakage was found.
- Learned noise defenses: AIAShield, arXiv:2312.04035; "Adversarial Attack
  Based Countermeasures against Deep Learning Side-Channel Attacks,"
  arXiv:2009.10568.
- Smart-meter privacy: Li, Oechtering, and Gündüz, ISIT 2017,
  https://doi.org/10.1109/ISIT.2017.8006633; ICASSP 2019,
  https://doi.org/10.1109/ICASSP.2019.8682381; ACC 2016,
  https://doi.org/10.1109/ACC.2016.7525225; Allerton 2013,
  https://doi.org/10.1109/ALLERTON.2013.6736513 (MI or hypothesis-testing
  leakage under energy cost, mostly MDP formulations, not games).
- Patents seen (abstracts and claims only): US 2018/0309566 A1 (clock frequency
  hopping, frequencies drawn from a lookup table by random number); US
  10,958,414 (clock period randomization); US 5,404,402 (clock frequency
  modulation for secure microprocessors); US 8,427,194 (randomized clock with a
  closed clock-data eye). None of these selects its randomization by a game or
  against an explicit observer model.

### Citation-chaining notes

Backward chaining (reference lists or related-work sections actually read):

- Woo et al. (arXiv HTML reference list): led to Jin et al. WIFS 2022 (direct
  predecessor; capacity minimization under an energy budget; uniform noise over
  a subset of leakage points as the baseline), Wu, Wagner, and Suh 2020
  (maximal leakage; artificial delay; LP), Das et al. "ASNI," IEEE TCAS-I 2018
  (noise-to-signal current ratio used for costs), and Issa, Wagner, and Kamath,
  IEEE Trans. Information Theory 2020 (maximal leakage). None models a
  strategic observer.
- Xu, Baykal-Gürsoy, and Spasojević (CNS 2021 introduction): points to Garnaev
  and Trappe (zero-sum allocation against nature), Yüksel et al. (rate
  allocation with a jammer helping an eavesdropper), and a game in which the
  attacker chooses which parallel channel to eavesdrop (reference [9] there,
  not retrieved).
- "A Hierarchical Learning Solution for Anti-Jamming Stackelberg Game With
  Discrete Power Strategies," IEEE WCL 2017,
  https://doi.org/10.1109/LWC.2017.2747543 (reference list): led to Yang et al.
  2013, Jia et al. 2016, Xiao et al. 2015, and Pita et al. 2010.
- Baddam and Zwolinski 2007: led to Yang et al. DATE 2005 (original RDVFS).
- Li, Oechtering, and Gündüz ISIT 2017 (reference list): led to Li and
  Oechtering 2015, Giaconi, Gündüz, and Poor 2015, Gündüz and Gómez-Vilardebó
  2013, and Kalogridis et al. 2010 (battery load hiding).
- RTL-PSC led to PARAM (HOST 2020); "Leverage the Average"
  (arXiv:2204.04160) cites both; VeriSide (LATS 2025) led to RTL-PAT.
- EMMasker: led to the GPU EM website-fingerprinting attack it defends against
  and to SweepSense (wideband spectrum scanning), which EMMasker names as the
  way an attacker could escape its fixed-band assumption.
- SCNIFFER: led to ML probe positioning (ePrint 2020/988) and automated probe
  repositioning (Bochum 2019).

Forward chaining ("cited by") was not done; the tool does not expose citation
graphs. Seeds for the pre-submission forward pass: Doychev and Köpf 2015; Geng
et al. 2018; Jin et al. 2022 and Woo et al. 2026; EMMasker 2024; Xu and
Baykal-Gürsoy 2023; Li, Oechtering, and Gündüz 2019; Yao and Zhang 2023 and
2024.

### Query Group F: status update

Status changes from "placeholder, not yet searched" to "partly searched,
2026-10-30."

- Found: RTL switching-activity leakage assessment (RTL-PSC 2019; PARAM 2020;
  RTL-PAT; VeriSide, LATS 2025, https://doi.org/10.1109/LATS65346.2025.10963943,
  a modified Verilator that writes Hamming-distance and Hamming-weight traces);
  gate-level flows (PACA, IACR ePrint 2021/530; arXiv:2204.11972; a 2023
  SSH-SoC workshop paper that checks a ring-oscillator noise countermeasure with
  Cadence Joules next to a test chip); a fidelity study finding toggle-count
  simulation matches SPICE qualitatively for unprotected designs but not for
  masked ones (SciTePress 2022); AIPS (TCHES 2026), which generates up to 1M
  transient power traces from VCD; EMSim (HPCA 2020,
  https://doi.org/10.1109/HPCA47549.2020.00016) for cycle-level EM simulation;
  ASCAD (Benadjila et al., Journal of Cryptographic Engineering 2020,
  https://doi.org/10.1007/s13389-019-00220-8; 50k profiling plus 10k attack
  traces); the SoftPower measured dataset (3.2M traces,
  https://github.com/UCdasec/SoftPower); diffusion-based trace synthesis
  (https://cetinkayakoc.net/docs/j104.pdf).
- MI estimator bias: IACR ePrint 2011/322 (all MI estimators are biased; no
  ideal estimator) and ePrint 2013/706 (separating estimation error from
  assumption error with cross-validation). No Bayesian hierarchical model of
  leakage across devices and sessions was found by this query.
- Planned queries not yet run as written: `RTL leakage detection toggle count
  Hamming distance pre-silicon`; `side-channel dataset ASCAD AES_HD CHES CTF
  FPGA power traces` (only ASCAD checked); `large-scale side-channel evaluation
  statistics multiple comparisons TVLA`; vendor white papers; a survey of open
  tools on GitHub.
- Conclusion: the expectation in Query Group F is confirmed in direction. The
  RTL/VCD-to-trace pipeline and generation at the 1M-trace scale are prior art.
  Make no claim about the pipeline, the dataset, its scale, or its generation
  method. The toggle-count fidelity result is a further reason to keep the
  proxy caveat on every simulated result.

### Element coverage after this pass

| Element | Nearest prior coverage found | Not exposed by these queries |
|---|---|---|
| E1 commitment to a randomized defense | anti-jamming Stackelberg games (Yang 2013; Jia 2016); pure commitment for timing (Doychev and Köpf 2015) | commitment to a randomized physical side-channel policy |
| E2 clock modes plus dummy current or noise | RDVFS (Yang 2005); clock plus voltage noise (Lagasse 2019); DVFS-state shifting plus noise (EMMasker 2024); MI-optimal noise (Jin 2022; Woo 2026) | these knobs as the action set of a game |
| E3 observer adapts band, filter, trace budget | capabilities: SCNIFFER; Fuzz'EMup band selection; Brisfors 2022; Baddam 2007; Screaming Channels hopping control. Strategic channel selection against noise allocation, in wireless (Xu and Baykal-Gürsoy 2023) | a best-responding measurement observer in a physical side-channel game |
| E4 MI or Fano leakage | Woo 2026; Köpf and Basin 2007; Li et al. 2019 (KL, Chernoff); Wu et al. 2020 (maximal leakage) | an MI or Fano bound for a defense mixture against a band-choosing observer |
| E5 robustness to the type prior | robust Stackelberg (Pita et al. 2010); Bayesian anti-jamming (Jia 2016; Xu et al. CNS 2021) | the same in side-channel defense |
| E6 large RTL/VCD datasets plus owned hardware | RTL-PSC 2019; VeriSide 2025; AIPS 2026 (1M traces); SoftPower (3.2M measured) | such datasets used to estimate a game payoff matrix with uncertainty |

### Disposition and claim impact

- Occupancy: no single work found by these queries combines E1, E2, and E3 in
  a physical side-channel setting. That is a statement about these queries, not
  evidence of novelty. Every element on its own is prior art.
- Most likely reviewer objection: "this is the cooperative-jamming band game
  (Xu and Baykal-Gürsoy 2023) applied to EMMasker-style clock-state shifting."
  The project must show what does not transfer: clock modes change the leakage
  operator and trace alignment, not only additive noise; the observer's trace
  budget averages over the defender's mixture; payoffs are estimated from data
  with session-level uncertainty (T5); the policy is robust to the type prior
  (T4).
- Caution from Wu, Wagner, and Suh 2020: without a strategic observer, mixing
  at most two deterministic schemes is optimal under maximal leakage. Any value
  of randomization in this project must come from the observer's best response,
  and must be measured.
- Highest residual risks: the full text of Yao and Zhang 2023 and 2024 (only
  abstracts read); Chinese-language follow-ups (not searched); forward
  citations of the seven seeds (not searched).
- Claim template: the safe template above remains acceptable. A narrower
  positioning sentence that credits the wireless lineage is in
  `paper/related-work-nearest-table.md`, section (a). The unsafe example stays
  unsafe.
- Next required actions, in order: read Yao and Zhang in full; run
  field-restricted IEEE Xplore, ACM DL, and Scopus searches; forward-chain the
  seven seeds; search Google Patents and Espacenet with candidate CPC classes
  (to be confirmed: G06F 21/75, G06F 21/755, H04L 9/003, H04L 2209/08); run a
  CNKI search for mutual-information games on side channels; then advisor
  review.

## Deep search 2 (2026-10-30)

### Scope, method, and limits

Claim under test: unchanged from "Deep search 2026-10-30" above. This pass
first closed three gaps that the first pass flagged (Yao and Zhang; EMMasker;
Xu and Baykal-Gürsoy), then ran the additional targeted searches recorded
below. Inclusion rule: unchanged (a work is "near" if it shares at least two
of E1 to E6).

Method:

- Searcher: an AI coding agent, a second session on 2026-10-30.
- WebSearch: the same Cursor general web search tool as the first pass
  (ranked pages plus an automatic summary). Facts below come from abstracts,
  metadata pages, or full text. One automatic summary that only echoed my
  query terms (it said Yao and Zhang's strategies were "power analysis versus
  electromagnetic analysis" and "masking versus probabilistic hiding") was
  discarded; the full text has no such strategy table.
- WebFetch: direct page fetches, including the Semantic Scholar Graph API
  (metadata and "citations" lists, used for forward chaining), accepted
  manuscripts on the NSF Public Access Repository (PAR), and arXiv.
- Local retrieval, used once and outside the project folder: IOPscience
  returned HTTP 403 to the fetch tool, and the Yao and Zhang PDF's text layer
  uses an unmapped font, so text extraction returns garbage for most pages.
  The open-access PDF (CC BY 3.0) was downloaded with curl to the system temp
  folder, its seven pages were rendered to images with PyMuPDF, and the images
  were read page by page. Quotes from that paper below are my transcriptions
  from page images; check them against the PDF before quoting in the paper.
- Not done in this pass: field-restricted IEEE Xplore, ACM DL, Scopus, or Web
  of Science searches; a search inside CNKI itself (one Chinese-language query
  went through the general search tool); Espacenet or USPTO class browsing
  (CPC codes were used only as query terms); Google Scholar "cited by" lists
  (Semantic Scholar lists were used instead; their coverage is incomplete,
  especially for IEEE conference papers and Chinese venues).

Standing rule, restated: "no match found" means only that these recorded
queries and citation paths did not expose one. It is not proof of novelty.

### Corrections and updates to earlier entries (Deep search 2)

The earlier text stays unchanged (append-only). These items supersede it.

5. Yao and Zhang 2024 is now read in full (gap 1 below). The research line
   starts in 2012, not 2023: J. Yao and T. Zhang, "Side Channel Attack Risk
   Evaluation Model Based on Mutual Information Game" (in Chinese:
   基于互信息博弈的侧信道攻击风险评估模型), Computer Engineering (计算机工程),
   vol. 38, no. 15, pp. 12-15, 2012,
   https://doi.org/10.3969/j.issn.1000-3428.2012.15.004. The CSAT 2023
   abstract is a near-verbatim English version of the 2012 abstract.
6. Xu and Baykal-Gürsoy, TIFS 2023, is explicitly a non-zero-sum,
   simultaneous (Nash) game. The defender's power allocation is a
   deterministic vector; only the eavesdropper randomizes. In the CNS 2021
   paper the defender randomizes which channel to protect. Details in gap 3.
7. EMMasker is now read in full, including the discussion, limitations, and
   references. It already randomizes its noise schedule (gap 2). The earlier
   statement that its observer's band is not a best response stands.
8. Galli et al., ICECS 2024 (query group D; preprint arXiv:2409.01881,
   https://arxiv.org/abs/2409.01881): the preprint reports that applying a
   high-pass filter "restores most of the side-channel vulnerabilities" left
   by random voltage scaling, that frequency scaling was the most effective
   hiding knob tested, and that robustness "improves with the distance
   between operating frequencies rather than depending on the number of
   frequencies used". This documents an observer filter choice that undoes a
   randomized power defense, which our observer model relies on.

### Gap 1: Yao and Zhang, full text

Citation: J. Yao and T. Zhang, "Side-Channel Attack Security Risk Assessment
Model Based on Mutual Information Game," J. Phys.: Conf. Ser., vol. 2732,
012002, 2024 (2nd Int. Conf. on Algorithms, Network and Computer Technology,
Wuhan, December 2023), https://doi.org/10.1088/1742-6596/2732/1/012002.
Read: full text (cover plus six printed pages).

Contents, by section:

- Section 2: a risk index R = P_s + C_s - P_s C_s, where the probability P_s
  is estimated with fuzzy theory and the consequence C_s is the mutual
  information I(leak_i; Key). MI is defined through entropies (Eqs. 2 to 6),
  with a key-candidate set from an unspecified statistical test
  D(leak_i, P_e) after q encryptions.
- Section 3: the game tuple GAME = <N, A, U, ST>, mixed strategies per leak
  type, and two definitions: "local" and "global policy entropy" (the Shannon
  entropy of a player's mixed strategy).
- Section 4: qualitative design advice. Section 5: conclusion.
- Absent: any numerical example, payoff matrix, computed equilibrium, data,
  or experiment. The only figure is an entropy Venn diagram.

Answers to the four questions, with quotes (page numbers as printed):

1. Designer versus attacker? Yes. Abstract, p. 1: "the two sides of the game
   are the cryptographic device designer (defence) and the enemy."
2. Simultaneous or commitment? Simultaneous. P. 3: "the bypass attack model
   conforms to the two-person non-cooperative incomplete information static
   game [8]." The only solution concept named is Nash (p. 5: "the
   quantitative evaluation of mutual information benefits of both sides under
   Nash equilibrium conditions can also provide a basis..."). No leader,
   follower, or commitment appears. "Incomplete information" is not
   formalized: no types, priors, or beliefs are defined.
3. Physical channel or abstract? Abstract. Leak types are labels (p. 5 gives
   "electromagnetic leakage, power leakage" as examples), and the payoff is a
   scalar. P. 4: "u^j_ik = I_{a_ik}(leak_i, key) represents the mutual
   information return function of strategy a_ik when bypass information
   leak_i is adopted by player j." No signal, noise, spectral, or measurement
   model appears.
4. Is the attacker's band or filter a strategy? No. Strategy sets are
   unspecified lists. P. 4: "A^j_i = {a_i1, ..., a_ik, ..., a_iq} represents
   the set of strategies taken by player j to leak information leak_i." The
   number of observed encryptions appears only inside the MI estimate (p. 3:
   "By monitoring the q encryption operations of Key, the attacker obtains
   bypass leakage information leak_i"), not as a costly decision. Resource
   limits appear in words (p. 3: "the increase of system defense capability
   is at the cost of sacrificing certain system resources") and as an
   unspecified constraint set ST.

Defense prescriptions (p. 5): existing countermeasures by citation ("mask
technology[9], insert random delay[10], increase noise signal[11]"), and a
heuristic: "the designer of cryptographic chip should follow the principle of
maximizing local policy entropy and global policy entropy under constrained
conditions when selecting security policies". That is a maximum-entropy
heuristic, not an equilibrium computation; an equilibrium mixed policy need
not have maximal entropy.

Verdict: the paper does not occupy the combination. It pre-empts only the
high-level framing "side-channel attack and defense as a designer-versus-
attacker game with mutual-information payoffs and mixed strategies", and the
2012 paper gives that framing a 2012 priority date. Cite it for the framing;
do not claim the framing.

Lineage and chaining:

- Backward: the 2024 paper has 11 references. Its only game-theory reference
  is [8], Hausken and Ortmann 2008 (an experiment on a multilevel prisoner's
  dilemma). Its countermeasure references are Itoh et al. 2002 (masking),
  Bucci et al. 2005 (random delay), and Mangard 2004. The 2012 paper's
  reference list (journal page) adds Fudenberg's game theory text (Chinese
  translation), Campenhout and Cover 1981 (maximum entropy), and He and Qiu,
  "Nash Equilibria Based on Strategic Entropy" (2003 preprint), which matches
  the strategy-entropy device.
- Same authors: J. Yao and T. Zhang, "Side channel risk qualitative
  evaluation model based on hierarchy," Computer Engineering and Applications,
  2012 (CNKI record JSGG201226020,
  http://en.cnki.com.cn/Article_en/CJFDTOTAL-JSGG201226020.htm): a fuzzy,
  hierarchy-based MI risk model with no game (abstract only).
- Forward (Semantic Scholar): the 2024 paper has one citing paper, "Average
  Relative SNR: New Metric to Evaluate the Attack Performance of Non-Profiled
  Side-Channel Traces," J. Electronic Testing, 2026,
  https://doi.org/10.1007/s10836-026-06218-5 (a trace metric, not a game, by
  title). The CSAT 2023 paper has none listed.
- Residual risk: low. The CSAT 2023 and 2012 full texts were not read (IEEE
  paywall; the journal's PDF link timed out). Their abstracts mention a "case
  analysis" with Nash strategies and MI benefits. With the same abstract and
  a 2012 date, a physical measurement model there is unlikely, but this is
  not verified. Next action: open
  https://www.ecice06.com/EN/10.3969/j.issn.1000-3428.2012.15.004 in a
  browser and read the PDF.

### Gap 2: EMMasker, full reading

Citation unchanged (MADWeb 2024, https://doi.org/10.14722/madweb.2024.23018;
PDF https://www.ndss-symposium.org/wp-content/uploads/madweb2024-18-paper.pdf).
Read: full text.

Facts that matter for positioning:

- Observer (Sec. V-A): "The SDR frequency was tuned to 810 MHz which is the
  second lowest frequency of the GPU and a 25 MHz sampling frequency was
  employed." The band never changes during the evaluation.
- Threat model (Sec. IV-A): "Our threat model assumes that the attacker is
  unable to monitor the entire spectrum including the full range of GPU
  frequency levels. Attackers could deploy multiple SDRs to cover a wider
  spectrum, or utilize advanced spectrum scanning techniques like SweepSense
  [9]. However, such advanced monitoring approaches require significant
  resources, making them less practical for most attackers."
- Mechanism: WebGL shader load in the browser; the GPU's DVFS governor
  responds, so the clock-state shift is an indirect side effect ("EMMasker
  rendering noise shifted the GPU frequency clock beyond the 810MHz range").
  Noise intensity follows a feedback rule ("when the GPU clock frequency
  increases, EMMasker increases the noise intensity"). Noise is randomized in
  time: "EMMasker triggers noise at random intervals every 1 to 15 seconds
  with each noise session lasting a brief 1 to 5 seconds." All parameters are
  hand-set.
- Evaluation: five websites with about 350 captures each (280 train, 70
  test); one GPU (GTX 1650); a USRP B210 receiver. A ResNet retrained on
  defended captures drops from 81.03% to 22.56% average accuracy. Overhead is
  a 7 to 13 percent increase (called GPU utilization in Sec. V-B and memory
  utilization in the contribution list). There is no MI, TVLA, guessing
  entropy, confidence interval, or accuracy-versus-capture-count curve. The
  statement that "no matter how much training data an attacker collects,
  their classifier will not be able to identify any patterns" is not tested.
- Limitations (Sec. VI-B): five websites, one attack scenario, one GPU.
- Forward citations (Semantic Scholar, 2026-10-30): none listed.

Not differences (concede): randomized timing of the defense, shifting a clock
state out of a band-limited receiver, noise scaled with the clock state, and
an attacker who retrains its classifier on defended data. EMMasker has all
four.

Answer to "this is just EMMasker":

1. EMMasker's receiver never re-tunes, and its threat model sets aside the
   re-tuning or wideband observer as too costly. That excluded observer is
   our follower: each type chooses band, filter, and trace budget as a best
   response to the published policy and pays for it, so "too costly" becomes
   a modeled price instead of an assumption.
2. EMMasker's randomization (1 to 15 s gaps, 1 to 5 s bursts, an intensity
   rule) is hand-set, and its clock shift is a side effect of load. Our
   defender selects clock modes and dummy-current levels directly, and their
   distribution is the solution of a game priced in energy, latency, and
   false alarms.
3. EMMasker reports one classifier's accuracy on five classes. We target
   key-dependent leakage with calibrated MI estimates, success rate or
   guessing entropy versus trace budget, and session-level intervals.
4. Different target and channel: website fingerprinting from far-field GPU
   memory-clock emanation, versus key leakage from an embedded device through
   conducted power and near-field EM, simulated from RTL.
5. A fair test includes an EMMasker-style baseline (load-induced mode shift,
   clock-scaled noise, random bursts) against the same band-switching
   observer. If it matches the equilibrium policy, report that the game added
   nothing.

### Gap 3: Xu and Baykal-Gürsoy (TIFS 2023) and the Bayesian CNS 2021 paper

Sources read:

- Z. Xu and M. Baykal-Gürsoy, TIFS 2023 (full citation in first-pass entry
  7); accepted manuscript at https://par.nsf.gov/servlets/purl/10461811.
  Read: abstract, Sections I and II, and the opening of Section III.
- Z. Xu, M. Baykal-Gürsoy, and P. Spasojević, CNS 2021 (full citation in
  first-pass entry 7); manuscript at
  https://par.nsf.gov/servlets/purl/10353172. Read: Sections I and II, the
  end of Section IV, and Section V; proofs not read.
- Companion with a jamming cost: Z. Xu and M. Baykal-Gürsoy, "A Cooperative
  Jamming Game in Wireless Networks Under Uncertainty," SecureComm 2020,
  LNICST 335, pp. 233-254, https://doi.org/10.1007/978-3-030-63086-7_14
  (manuscript https://par.nsf.gov/servlets/purl/10291817). Read: abstract and
  introduction.
- Z. Xu, "Optimization and Game-Theoretic Approaches for Defensive Resource
  Allocation in Communication and Network Security," PhD dissertation,
  Rutgers University, 2022,
  https://rucore.libraries.rutgers.edu/rutgers-lib/76253/. Read: abstract.

Model facts:

- TIFS 2023: a friendly interferer splits jamming power J_i over N parallel
  channels (the J_i sum to at most J); the eavesdropper attacks n of N
  channels with probabilities p_i that sum to n. Capacities have the form
  C_E,i = ln(1 + g^E_i T_i / (sigma^2 + h^E_i J_i)). The eavesdropper's
  payoff is the sum of p_i C_E,i(J_i); the interferer's payoff is the
  expected secret rate. The game is non-zero-sum. On timing: "Since it is
  difficult for the friendly interferer and the eavesdropper to know each
  other's decision ahead of time, this paper considers that the friendly
  interferer and the eavesdropper are playing a Nash game." The transmitter
  leads only at a first level (transmit power), outside the jamming game.
  Results: a unique NE with threshold (water-filling) structure, a
  strategy-iteration algorithm, and a game policy that beats "the
  conservative power allocation strategy that assumes every channel to be
  under attack."
- CNS 2021: the eavesdropper "can only use hardware with limited capability
  to listen on n_E of N different frequencies at the same time," motivated by
  "budget limitation, or to reduce the risk of Local Oscillator (LO) leakage."
  The analysis takes n_E = 1. The defender protects one channel per block,
  chosen by a mixed strategy (or does not jam). Timing: "assume that Ian and
  Eve make their choices simultaneously and thus, they are engaged in a
  one-shot simultaneous play Nash game." Two non-zero-sum games plus a
  Bayesian game with two eavesdropper types and a belief alpha, all with
  closed-form equilibria. Baselines: equal-proportion protection and no
  jamming. Sec. V-C: "an eavesdropper can indeed exploit the friendly
  interferer's incorrect belief about the attacker's type. Hence, an accurate
  inference on the type of upcoming attackers is crucial." No prior-robust
  policy is proposed.
- SecureComm 2020 adds a cost for interference and incomplete eavesdropper
  channel-state information; non-zero-sum, threshold NE.
- Forward citations (Semantic Scholar): TIFS 2023 has 11 citing papers, all
  wireless by title; CNS 2021 has none listed.

What carries over (concede and cite):

1. The band subgame's structure: a limited noise budget over parallel
   frequency channels; an observer limited to a few frequencies by hardware
   cost; mixed strategies on both sides; threshold and water-filling
   equilibria; Bayesian observer types with a prior.
2. With Gaussian leakage and a noise-only defense, per-band leakage
   0.5 log(1 + SNR_b) has the same form as their eavesdropping capacity. In
   that special case our band subgame is their game; cite its solution
   instead of re-deriving it.
3. The evaluation logic: game policy versus a conservative "every channel
   attacked" policy (our robust-convex baseline B4), and versus
   equal-proportion and no-defense policies (our B2 and B0).
4. The motivation for prior robustness: CNS 2021 shows that a wrong type
   belief is exploitable and stops there; our T4 targets that gap.

What does not carry over:

1. The defender moves the signal, not only the noise. In these games the
   defender's action enters only as interference power in a fixed channel's
   SINR, and channel gains are exogenous. A clock-mode change moves the
   leakage in frequency (clock harmonics), rescales it (with voltage), and
   shifts its timing (trace alignment); in their notation the defender would
   control the eavesdropper gains, not only the jamming term. That part
   resembles transmitter frequency hopping against a band-limited listener,
   which is itself a known wireless game family (group H below), so the
   difference is the combination with points 2 to 4, not hopping alone.
2. Evidence accumulates about a fixed key. Secrecy capacity is per block with
   a fresh message, so an eavesdropper gains nothing by averaging blocks. A
   side-channel observer averages N traces of the same key: independent dummy
   noise loses effect roughly as 1/N, the noise energy needed to hold a
   success rate grows with the observer's budget, and the observer pays per
   trace. The payoff is success or MI after N traces, not a rate. (Bounds on
   leakage from repeated independent runs exist in QIF; see Smith and Smith
   2017, group B. Do not claim them.)
3. Whether mixing helps depends on what the observer measures. If the clock
   mode is drawn per trace and hidden, each trace sees a mixture channel, and
   leakage is convex in hidden mixing (Alvim et al., group A), so a mix can
   leak less than the average of its pure modes. If the observer spends part
   of its measurement on detecting the mode (the clock line is usually the
   strongest EM emission; Baddam and Zwolinski 2007 detect the mode from
   supply glitches), choice becomes visible and the payoff becomes linear in
   the mix. The observer's band choice thus decides whether the defender's
   randomization is hidden. Nothing in the wireless games couples the
   eavesdropper's channel choice to the visibility of the defender's
   randomization.
4. Costs and objective: a side channel has no legitimate receiver. Defender
   costs are energy, latency (slower modes lengthen computation), and false
   alarms; observer costs are bandwidth, filters, and traces.
5. Payoffs: theirs are closed-form capacities from channel-state information;
   ours are estimated from simulated traces with session-level uncertainty
   (T5), and switching-activity leakage is not Gaussian, so closed-form
   water-filling need not apply.

Commitment is not a valid difference by itself. Korzhyk et al. (group C):
"For finite two-person zero-sum games, it is known that the different game
theoretic solution concepts of NE, minimax, maximin and SSE all give the same
answer." von Stengel and Zamir (group C): "The value of a zero-sum game is its
unique leadership and Nash payoff." In our zero-sum-within-type case (roadmap
T2) the same minimax argument, applied to the defender against the profile of
type best responses, makes the committed policy a Bayes-Nash minimax policy.
Commitment can change the answer only in a general-sum version, for example
when the observer's resource cost is not credited to the defender. There,
moving from simultaneous play to leadership "never harms the leader" (von
Stengel and Zamir), but the size of the gain has to be shown. The modeling
case for commitment still holds: a firmware-fixed policy can be profiled
offline, unlike a per-block jamming decision, and per-block simultaneity is
the reason the wireless papers gave for choosing Nash.

Answer to "this is that wireless game applied to EM": "With additive noise,
Gaussian leakage, and a single-band observer, our band subgame is the Xu and
Baykal-Gürsoy game, and we cite its solution. Three things do not transfer.
The defender's clock modes move and reshape the leakage instead of adding
noise to a fixed channel. The observer accumulates evidence about a fixed key
over a costly trace budget, which erodes dummy noise roughly as 1/N and makes
the value of mixing depend on whether the observer spends bandwidth on
detecting the mode. Costs and payoffs come from device energy, latency, and
false alarms and from trace data with uncertainty, not from secrecy rates and
channel-state information. Commitment is not among the differences while the
game is zero-sum."

### New nearby works from the additional targeted searches

Each item gives the citation and link, what it shares, and how it differs.
"Read" gives read depth.

A. Information-leakage games (the most important new find; theory side)

- M. S. Alvim, K. Chatzikokolakis, Y. Kawamoto, and C. Palamidessi,
  "Information Leakage Games," GameSec 2017,
  https://doi.org/10.1007/978-3-319-68711-7_23; extended as "Information
  Leakage Games: Exploring Information as a Utility Function," ACM Trans.
  Privacy and Security, 2022, https://doi.org/10.1145/3517330
  (arXiv:2012.12060; author PDF
  https://staff.aist.go.jp/yusuke.kawamoto/papers/TOPS2022long.pdf).
  Companions by the same authors: "Leakage and Protocol Composition in a
  Game-Theoretic Perspective," POST 2018,
  https://doi.org/10.1007/978-3-319-89722-6_6, and "A Game-Theoretic Approach
  to Information-Flow Control via Protocol Composition," Entropy 20(5):382,
  2018, https://doi.org/10.3390/e20050382. Read: TOPS Sections 1 to 3.1;
  Entropy abstract.
  - Shares: zero-sum games whose utility is information leakage; a
    randomizing defender; the result that hidden mixing makes leakage convex
    (not linear) in the defender's strategy (TOPS: "information is non-linear
    with respect to hidden choice"), so a mix can leak less than its parts;
    equilibrium existence and algorithms; simultaneous and sequential
    variants with the defender's choice visible or hidden (Entropy 2018).
  - Differs: abstract channels (programs, the Crowds protocol, local
    differential privacy); no physical measurement, band, filter, or trace
    budget; no energy or latency costs; observer types and prior robustness
    not studied in the parts read.
  - Consequence for us: an LP built from per-mode leakage estimates (roadmap
    Sections 3 and 4) is exact when the observer can tell each trace's mode,
    and conservative (an upper bound on single-trace leakage, by convexity of
    MI in the channel) when it cannot.

B. Leakage-minimal design, adaptive adversaries, repeated runs (theory side)

- M. H. R. Khouzani and P. Malacaria, "Relative Perfect Secrecy:
  Universally Optimal Strategies and Channel Design," CSF 2016,
  https://doi.org/10.1109/CSF.2016.12; "Leakage-Minimal Design: Universality,
  Limitations, and Applications," CSF 2017,
  https://doi.org/10.1109/CSF.2017.40; "Optimal Channel Design: A Game
  Theoretical Analysis," Entropy 2018, https://doi.org/10.3390/e20090675.
  Read: the description in Alvim et al. TOPS, Sec. 1.3, and titles.
  - Shares: leakage-minimizing channel design under hard and soft
    constraints, posed as a zero-sum game with incomplete information, with
    Bayes-Nash defender strategies from convex programs.
  - Differs: abstract channels; no physical knobs, band choice, or traces.
- A. Antonopoulos and T. Terauchi, "Games for Security Under Adaptive
  Adversaries," CSF 2019, https://doi.org/10.1109/CSF.2019.00022. Read: title
  only (found by forward chaining); inspect before submission.
- D. M. Smith and G. Smith, "Tight Bounds on Information Leakage from
  Repeated Independent Runs," CSF 2017, https://doi.org/10.1109/CSF.2017.18.
  Read: metadata only. Shares the trace-budget question (leakage after n
  independent runs); no defense optimization or game.

C. Commitment versus Nash (needed for the commitment caveat in gap 3)

- D. Korzhyk, Z. Yin, C. Kiekintveld, V. Conitzer, and M. Tambe, "Stackelberg
  vs. Nash in Security Games: An Extended Investigation of Interchangeability,
  Equivalence, and Uniqueness," JAIR 41:297-327, 2011,
  https://doi.org/10.1613/jair.3269. Read: abstract and Section 3 excerpts.
- B. von Stengel and S. Zamir, "Leadership games with convex strategy sets,"
  Games and Economic Behavior 69(2):446-457, 2010,
  https://doi.org/10.1016/j.geb.2009.11.008 (author version
  https://eprints.lse.ac.uk/27653/). Read: introduction excerpts. It cites
  inspection games (Avenhaus, von Stengel, and Zamir, 2002 survey; not
  retrieved) as the classic application of commitment to mixed strategies.
  No inspection game applied to side channels was found.

D. Side-channel noise framed as wiretap artificial noise

- S. Jin, M. Xu, and Y. Cai, "Energy Efficient Obfuscation of Side-Channel
  Leakage for Preventing Side-Channel Attacks," ACM SAC 2024,
  https://doi.org/10.1145/3605098.3635997 (arXiv:2208.09140). Read: abstract
  and Sections 1 to 2.1.
  - Shares: energy-budgeted noise that minimizes side-channel capacity, by
    explicit analogy with artificial noise against a wiretap eavesdropper;
    covers the attacker's choice of compression method (sample selection,
    PCA, LDA) by aggregating optimal noise patterns "without making any prior
    assumption on attacker's attack strategies"; experiments.
  - Differs: aggregation instead of a best response or equilibrium; noise
    only, no clock modes; no band or trace-budget choice.

E. Clock-mode optimization and randomization (no game)

- G. Klasson Landin and T. Jilborg, "Determining the Optimal Frequencies for
  a Duplicated Randomized Clock SCA Countermeasure," arXiv:2307.13834, 2023,
  https://arxiv.org/abs/2307.13834. Read: abstract, introduction, opening of
  the method.
  - Shares: chooses the clock-frequency set for a randomized-clock plus
    dummy-core FPGA defense, trading protection (CPA traces needed) against
    timing overhead.
  - Differs: open-loop design against a fixed CPA attacker; no game, MI
    bound, or band choice.
- T.-H. Tran, B.-A. Dao, D.-H. Le, V.-P. Hoang, T.-T. Hoang, and C.-K. Pham,
  "Spread Spectrum-Based Countermeasures for Cryptographic RISC-V SoC," IEEE
  TVLSI, 2024, https://doi.org/10.1109/TVLSI.2024.3444851. Read: abstract.
  - Shares: random dynamic frequency hopping (223 spread-spectrum clock
    parameter sets) for an AES accelerator, tested with up to five million
    power traces, CPA with alignment preprocessing, TVLA, and deep-learning
    leakage assessment.
  - Differs: open-loop; no game, observer model, or MI bound.
- Same lineage, abstracts only: "Lightweight Side-Channel Protection using
  Dynamic Clock Randomization," FPL 2020,
  https://doi.org/10.1109/FPL50879.2020.00041; "Island-based Random Dynamic
  Voltage Scaling vs ML-Enhanced Power Side-Channel Attacks," ACM, 2023,
  https://doi.org/10.1145/3583781.3590266; "RAD-FS: Remote Timing and Power
  SCA Security in DVFS-augmented Ultra-Low-Power Embedded Systems," ACM,
  https://doi.org/10.1145/3711836 (measured on a 40 nm test chip). None
  models a strategic observer.

F. Moving-target defense with commitment

- M. Ayrault, E. Borde, U. Kühne, and J. Leneutre, "Moving Target Defense
  Strategy in Critical Embedded Systems: A Game-theoretic Approach," IEEE
  PRDC 2021, https://doi.org/10.1109/PRDC53464.2021.00014. Read: abstract.
  - Shares: Bayesian Stackelberg commitment to a randomized reconfiguration
    policy for an embedded system under quality-of-service constraints,
    solved as a MILP, with an automotive case study.
  - Differs: system reconfiguration against vulnerability exploitation, not
    physical leakage; no measurement band, filter, traces, or MI.
- "ShuffleV: A Microarchitectural Defense Strategy against Electromagnetic
  Side-Channel Attacks in Microprocessors," RAID 2025,
  https://doi.org/10.1109/RAID67961.2025.00065. Read: abstract. Moving-target
  instruction shuffling and dummy instructions on a RISC-V core against EM
  attacks; no game or optimized distribution.

G. Observer capabilities relevant to band and filter choice

- M. G. Kuhn, "Security Limits for Compromising Emanations," CHES 2005,
  author PDF https://www.cl.cam.ac.uk/~mgk25/ches2005-limits.pdf. Read: the
  receiver-bandwidth passage. Received impulse amplitude grows linearly with
  receiver bandwidth B while thermal noise grows as the square root of B, and
  a narrower band makes a quiet window easier to find. This is a physical
  basis for a bandwidth trade-off in the observer's action set.
- "Periodic Nonuniform Sampling for Enhanced Recognition of Spread Spectrum
  Clocking-Based Electromagnetic Signature," IEEE TEMC, 2024,
  https://doi.org/10.1109/TEMC.2024.3425852, and "Complete Coherent
  Demodulation and Recovery of Spread Spectrum Clocking-Based Electromagnetic
  Information Leakage: Theory and Demonstration," IEEE TIFS, 2025,
  https://doi.org/10.1109/TIFS.2025.3553029. Read: abstracts. Receivers can
  undo spread-spectrum clocking, which limits any claim that frequency
  spreading alone hides leakage from an adaptive observer.

H. Wireless frequency-hopping games (the hide-and-seek part of gap 3, point 1)

- "Dogfight in Spectrum: Jamming and Anti-Jamming in Multichannel Cognitive
  Radio Systems," IEEE GLOBECOM 2009,
  https://doi.org/10.1109/GLOCOM.2009.5425707 (a zero-sum one-stage game of
  random hopping against a jammer; a POMDP for the multi-stage case).
- "Game Theory-Based Anti-Jamming Strategies for Frequency Hopping Wireless
  Communications," IEEE TWC, 2018, https://doi.org/10.1109/TWC.2018.2841921
  (a bimatrix game).
- "The Eavesdropping and Jamming Dilemma in Multi-Channel Communications,"
  IEEE ICC 2013, https://doi.org/10.1109/ICC.2013.6654847.
- "Uncoordinated Frequency Hopping for Secrecy with Broadband Jammers and
  Eavesdroppers," IEEE ICC 2015, author PDF
  https://www.dcc.fc.up.pt/~joaovilela/publications/icc15-ufhbroadband.pdf
  (eavesdroppers that listen on several channels; an analysis, not a game).
- "Frequency Hopping against a Powerful Adversary," ETH Zurich,
  https://tik-old.ee.ethz.ch/file/0f70f63b504824883946ae59f0f4cef9/fh.pdf
  (randomized hopping against a jammer that learns the channel with a lag).
- Read: abstracts or snippets. Shared: a transmitter randomizes its frequency
  against a band-limited adversary. Differs: intentional transmissions;
  throughput or secrecy payoffs; no fixed-key accumulation or device costs.

I. Learned obfuscation against adaptive attackers

- "FriendlyFoe: Adversarial Machine Learning as a Practical Architectural
  Defense against Side Channel Attacks," PACT 2024,
  https://doi.org/10.1145/3656019.3676952. Read: abstract. Shares: a learned
  defender that perturbs signals (including system power) at an energy cost
  and resists attackers retrained on obfuscated signals. Differs: no
  equilibrium or commitment; no band or trace-budget choice; no clock modes.

J. Patents (abstracts and claims only; legal scope not assessed)

- US 11,594,962 B2, "Techniques to Improve Current Regulator Capability to
  Protect the Secured Circuit from Power Side Channel Attack," NVIDIA Corp.
  (inventors S. S. Kudva, N. Nedovic, and S. Song), filed 2022-01-20,
  https://patents.google.com/patent/US11594962B2/en (read via
  https://patents.us/US11594962). It claims randomly steering clock edges
  between a real load and a dummy load; embodiments add a randomized current
  shunt and a randomized (edge-blocking) clock. It is listed under H02M 3/155
  (other classes not checked). Consequence: combining randomized clocking
  with dummy current is patented; our knobs are not new.
- US 8,332,448 (SANYO Semiconductor),
  https://www.freepatentsonline.com/8332448.html: oscillator frequency varied
  by random numbers within a programmable range to reduce electromagnetic
  radiation noise. Shares a configurable random clock-frequency distribution;
  differs: EMI reduction, no adversary.
- US 2002/0124178 A1, "Differential power analysis method and apparatus,"
  https://patents.google.com/patent/US20020124178A1/en (random clock skipping
  among other countermeasures). Its Google Patents page confirms the CPC
  meanings below.
- EP 0660562 A3, "Clock frequency modulation for secure microprocessors,"
  https://data.epo.org/publication-server/rest/v1.0/publication-dates/19970618/patents/EP0660562NWA3/document.pdf
  (same title as US 5,404,402 from the first pass; family link not
  verified).
- None of these selects its randomization by a game or against a modeled
  observer.
- CPC terms for the pre-submission patent search. Confirmed on Google Patents
  pages or a USPTO CPC notice: G06F 21/75 (protecting components by
  inhibiting the analysis of circuitry or operation); G06F 21/755 (the same,
  with measures against power attack; the USPTO definition lists "Change
  instruction clocking" and "Execute dummy instructions" as examples);
  H04L 9/002 (countermeasures against attacks on cryptographic mechanisms);
  H04L 9/003 (the same, for power analysis such as DPA or SPA);
  H04L 2209/08 (randomization, for example dummy operations or noise). Seen
  but not checked: H02M 3/155. Not yet confirmed, to try: H04K 3/80 and its
  subgroups (jamming or countermeasures against interception), G06F 1/08
  (clock generators with changeable frequency), H03K 3/84 (random pulse
  generators), and H04B 15/02 (reducing interference from electric
  apparatus).

### Exact queries run (Deep search 2)

All 27 queries used the Cursor WebSearch tool on 2026-10-30. "D" marks a
discovery query. "V" marks a retrieval or verification query. Queries are
listed in the order run within each group.

Gap 1, Yao and Zhang:

- V `"Side-Channel Attack Security Risk Assessment Model Based on Mutual Information Game" pdf`
- V `Yao Zhang "mutual information game" side channel "local strategy entropy" "global strategy entropy" Nash equilibrium defender attacker`
- V `Jianbo Yao Tao Zhang mutual information game side channel case analysis payoff matrix power analysis electromagnetic leakage defender strategy probability` (exposed the 2012 Chinese paper)
- V `"mutual information game" side channel 2732 012002 Nash equilibrium mixed strategy defender attacker risk value case example table`
- V `Yao Zhang 2024 J. Phys. Conf. Ser. 2732 012002 side channel introduction power consumption electromagnetic radiation timing cryptographic chip mutual information leakage key entropy`
- D `"bypass leakage" mutual information game defender attacker "strategy entropy" "Nash equilibrium" risk assessment cryptographic device designer enemy` (exposed Alvim et al.)
- D `"global policy entropy" OR "global strategy entropy" bypass leakage space multiple leakage attack defense policy side channel risk`
- V `bypass attack cryptographic chip power consumption electromagnetic radiation time leakage information entropy key mutual information "bypass information" risk Yao Zhang 2024`
- V `mutual information game side channel case analysis attacker chooses power analysis attack electromagnetic attack defender chooses masking hiding probability equilibrium mutual information benefit Yao Zhang` (its automatic summary was discarded; see method)

Gaps 2 and 3, EMMasker and Xu and Baykal-Gürsoy:

- V `EMMasker EM Obfuscation Against Website Fingerprinting MADWeb 2024 paper pdf ndss-symposium.org`
- V `Xu Baykal-Gursoy "Power Allocation for Cooperative Jamming Against a Strategic Eavesdropper Over Parallel Channels" arXiv`
- V `"A Game-Theoretic Approach for Probabilistic Cooperative Jamming Strategies over Parallel Wireless Channels" arXiv Bayesian game eavesdropper`
- D `Zhifan Xu Rutgers dissertation cooperative jamming strategic eavesdropper game theory parallel channels`
- V `Xu Baykal-Gursoy "A Cooperative Jamming Game in Wireless Networks under Uncertainty" SecureComm 2020 LNICST`

Additional targeted searches:

- D `inspection game side-channel leakage evaluation inspector chooses measurement randomized countermeasure`
- D `moving target defense electromagnetic emanation power side channel randomized frequency hopping clock embedded device game-theoretic`
- D `spread spectrum clocking side-channel countermeasure EM attack mixed strategy game attacker filter band`
- D `Stackelberg game electromagnetic emission control emanation security leader commits noise follower eavesdropper receiver bandwidth`
- D `Bayesian game attacker types measurement selection probe placement side-channel evaluation adversary chooses frequency band trace budget`
- V `Alvim Chatzikokolakis Kawamoto Palamidessi "A Game-Theoretic Approach to Information-Flow Control via Protocol Composition" Entropy 2018 sequential games visible hidden choice`
- V `Korzhyk Yin Kiekintveld Conitzer Tambe "Stackelberg vs. Nash in Security Games" JAIR 2011 interchangeability equivalence zero-sum`
- D `frequency hopping transmitter versus eavesdropper channel selection game mixed strategy hide and seek secrecy limited-band eavesdropper`
- D `侧信道 博弈 防御策略 随机时钟 动态电压频率 Stackelberg 互信息` (Chinese: side channel, game, defense strategy, random clock, dynamic voltage and frequency, Stackelberg, mutual information; exposed only the 2012 Yao and Zhang paper plus English DVFS and clock-randomization work)
- D `adaptive side-channel countermeasure reinforcement learning defender versus adaptive attacker noise injection clock randomization 2025 2026 game`
- V `von Stengel Zamir "Leadership games with convex strategy sets" Games and Economic Behavior 2010 commitment leader payoff at least Nash equilibrium`

Patents (Google Patents and aggregators, reached through WebSearch):

- D `patent side channel countermeasure selects clock frequency mode probabilistically based on attacker model cost optimization G06F21/755 H04L9/003`
- D `patent G06F21/755 OR H04L9/003 OR H04L2209/08 randomly selecting clock frequency and dummy current noise level according to probability distribution to counter power and electromagnetic analysis`

Fetches and API calls (WebFetch unless noted), with outcomes:

- IOPscience article page, its PDF URL, and the "google." and "beta." mirrors
  of the PDF: HTTP 403.
- r.jina.ai reader proxy of the IOP PDF: retrieved (seven pages), but the
  text layer is undecodable.
- Unpaywall API: HTTP 422 (needs a real email). Wayback Machine: timeout.
  scholar.archive.org: HTTP 403. pdfs.semanticscholar.org: returned the
  Semantic Scholar landing page, not a PDF.
- Semantic Scholar API for both Yao and Zhang papers: metadata, references,
  and citations (the CSAT 2023 record is closed access with references
  elided).
- Computer Engineering journal page for the 2012 paper: retrieved (metadata,
  English and Chinese abstracts, reference list). Its PDF link: HTTP 504
  directly and HTTP 401 through the reader proxy. The reader proxy also
  returned HTTP 401 for the CSAT 2023 DOI.
- NSF PAR record and accepted manuscript for TIFS 2023 (purl 10461811):
  retrieved. arXiv 2208.09140: retrieved.
- Semantic Scholar "citations" lists for nine seeds (forward-chaining table
  below) and metadata for TVLSI 2024, PRDC 2021, SAC 2024, and CSF 2017
  (Smith and Smith): retrieved. One Semantic Scholar search: HTTP 429 (rate
  limited).
- Local shell, run outside the sandbox (permission requested): curl download
  of the IOP PDF (449,438 bytes) to the system temp folder; PyMuPDF installed
  to a temp folder; seven pages rendered at 130 dpi and read as images.
  Nothing was written inside the project except this log and the
  nearest-work table.
- Full texts that the search tool saved alongside results (no separate
  fetch): EMMasker; Alvim et al. TOPS 2022; the CNS 2021 and SecureComm 2020
  manuscripts; Xu's dissertation; Entropy 2018; JAIR 2011; von Stengel and
  Zamir 2010; Kuhn 2005; Klasson Landin and Jilborg 2023; the Galli et al.
  preprint; the US 11,594,962 page.

### Citation-chaining notes (Deep search 2)

Backward:

- Yao and Zhang 2024 and 2012: see gap 1.
- EMMasker: the attack it defends against is Z. Zhan, Z. Zhang, S. Liang, F.
  Yao, and X. Koutsoukos, "Graphics Peeping Unit: Exploiting EM Side-Channel
  Information of GPUs to Eavesdrop on Your Neighbors," IEEE S&P 2022; the
  wideband-observer escape route is SweepSense (NSDI 2019). Both were named
  in the first pass; neither is a defense paper.
- TIFS 2023 related work: Garnaev and Trappe's game against an eavesdropper
  who listens on one of several parallel channels, and Garnaev et al.'s
  zero-sum game in which interferer and eavesdropper each pick one channel
  (references [34] and [37] there; not retrieved). Yang et al. 2013
  (Stackelberg smart jammer) and Altman et al. (jamming games) were already
  logged.
- Alvim et al. TOPS 2022 related work: Khouzani and Malacaria (group B);
  Korzhyk et al. (group C); Boreale and Pampaloni and Mardziel et al.
  (adaptive QIF attackers, no game).

Forward (Semantic Scholar "citations" lists on 2026-10-30; incomplete
coverage):

| Seed | Citing papers listed | Relevant to the claim |
|---|---|---|
| EMMasker 2024 | 0 | none |
| Xu and Baykal-Gürsoy, TIFS 2023 | 11 | none (all wireless by title) |
| Xu, Baykal-Gürsoy, Spasojević, CNS 2021 | 0 | none |
| Doychev and Köpf, CSF 2015 | 17 | Khouzani and Malacaria 2016 and 2017; Smith and Smith 2017; Doychev's 2016 thesis (timing) |
| Geng et al., TCAD 2018 | 2 | none by title |
| Jin et al., WIFS 2022 | 4 | Jin, Xu, and Cai, SAC 2024 (group D); Woo et al. |
| Woo et al., arXiv 2025 and ISIT 2026 | 1 | none (a review) |
| Alvim et al., GameSec 2017 | 23 | Khouzani and Malacaria 2018; Antonopoulos and Terauchi 2019; a QIF game for collaborative security (IEEE TIFS 2019, https://doi.org/10.1109/TIFS.2019.2914358); none physical |
| Yao and Zhang, J. Phys. 2024 | 1 | none (a trace metric) |

Not forward-chained in this pass: Li, Oechtering, and Gündüz 2019.

### Element coverage after Deep search 2

Additions to the first-pass coverage table, which stands:

| Element | New coverage found in this pass |
|---|---|
| E1 commitment to a randomized defense | Bayesian Stackelberg commitment to randomized moving-target reconfiguration on an embedded system (Ayrault et al. 2021); a defender that randomizes which channel to protect, under Nash (Xu et al. CNS 2021); EMMasker's hand-set random burst schedule |
| E2 clock modes plus dummy current or noise | frequency-set choice for randomized clocks with a dummy core (Klasson Landin and Jilborg 2023); spread-spectrum hopping (Tran et al. 2024); clock-edge steering between real and dummy loads (US 11,594,962 B2) |
| E3 observer adapts band, filter, trace budget | eavesdropper limited by hardware budget to n_E of N frequencies (Xu et al. CNS 2021, wireless); high-pass filtering undoes random voltage scaling (Galli et al. 2024); de-spreading of spread-spectrum clocks (TEMC 2024; TIFS 2025); receiver-bandwidth trade-off (Kuhn 2005); attacker compression-method uncertainty handled by aggregation (Jin, Xu, and Cai 2024) |
| E4 MI or Fano leakage | information leakage as game utility, convex under hidden mixing (Alvim et al. 2017 to 2022); MI payoffs in a static designer-attacker game with no channel model (Yao and Zhang 2012, 2024); side-channel capacity under an energy budget (Jin, Xu, and Cai 2024) |
| E5 robustness to the type prior | Bayesian eavesdropper types with a fixed prior and an observed exploitation of wrong beliefs, no robust policy (Xu et al. CNS 2021); Bayes-Nash optimal channel design in abstract QIF (Khouzani and Malacaria) |
| E6 traces | no new game paper with traces |

Still not exposed by these queries: a physical side-channel defense game in
which an observer best-responds with band, filter, and trace budget to a
committed clock-mode and dummy-current policy; and any treatment of how the
observer's measurement choice decides whether the defender's randomization is
hidden or visible.

### Disposition and claim impact (Deep search 2)

- Occupancy: no single work found occupies the combination. The nearest by
  element count are Xu et al. CNS 2021 (a randomized defender over channels,
  a band-limited observer, Bayesian types; but wireless secrecy, simultaneous
  play, no clock modes or traces), Alvim et al. (information as utility with
  hidden mixing; abstract channels), EMMasker (the mechanism, with a fixed
  observer and no game), and Yao and Zhang (the designer-versus-attacker MI
  game framing; abstract and static). This is a statement about the recorded
  queries, not evidence of novelty.
- Yao and Zhang's residual risk drops from "highest" to "low": the 2024 full
  text answers all four questions in our favor; the 2012 and 2023 full texts
  remain unread.
- Concessions the paper must make: randomization; commitment while the game
  is zero-sum; the band subgame and its solution; the MI-game framing; the
  wiretap analogy for side-channel noise; the clock-plus-dummy-current
  mechanism (papers and a patent); and the frequency-hopping hide-and-seek
  structure.
- The defensible differences, strongest first:
  1. A measurement observer that best-responds with band, filter, and trace
     budget at a cost: the case EMMasker explicitly leaves out of scope and
     that Yao and Zhang do not model.
  2. Defender actions that move and reshape the leakage, combined with
     evidence accumulated about a fixed key over a costly trace budget, so
     that dummy noise erodes with N and the value of mixing depends on
     whether the observer spends measurement on detecting the mode. Neither
     the wireless jamming games nor the information-leakage games couple
     these.
  3. A prior-robust policy over observer types, with payoffs estimated from
     traces under session-level uncertainty, where the closest Bayesian
     analog (CNS 2021) uses a fixed prior and notes that wrong beliefs are
     exploitable.
  Points 2 and 3 are modeling differences until a result shows that they
  change the recommended policy (Upgrades 1 and 3 in the table file).
- Implications for the theory files (for the theory owner; this pass did not
  edit `theory/`):
  - In the zero-sum-within-type model (T2) the committed policy equals a
    Bayes-Nash minimax policy, so the "value of commitment" target in Upgrade
    1 is zero there; it must be stated for a general-sum variant.
  - The LP over p built from per-mode leakage estimates assumes visible
    choice. Under hidden per-trace mode draws, single-trace leakage is convex
    in p and the LP is conservative. A theorem on when the observer's band
    choice makes the mode visible would be a result that does not follow
    from the wireless band games (candidate for Upgrade 3; status:
    conjecture, not checked).
- Claim template: the safe template earlier in this log remains acceptable.
  The refined positioning sentence and the reviewer answers are in
  `paper/related-work-nearest-table.md`, sections (a) and (d).
- Next required actions, in order: read the 2012 Computer Engineering PDF and
  the CSAT 2023 paper; read Alvim et al. TOPS 2022 from Section 3 on and the
  Entropy 2018 sequential-game section; read Khouzani and Malacaria 2017 and
  Antonopoulos and Terauchi 2019; run field-restricted IEEE Xplore, ACM DL,
  and Scopus searches that combine "information leakage game" or
  "Stackelberg" with "side channel", "clock", or "electromagnetic";
  forward-chain Li, Oechtering, and Gündüz 2019 and Alvim et al. TOPS 2022 in
  Google Scholar; run Espacenet and USPTO searches with the confirmed CPC
  codes plus H02M and H04K 3; search CNKI directly; then advisor review.
