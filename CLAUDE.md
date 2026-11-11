# Instructions for future coding agents

Read, in order:

1. `README.md`
2. `research-project-master-plan.txt`
3. `theory/model-and-proof-roadmap.md`
4. `experiments/simulation-and-bench-plan.md`
5. `literature/novelty-search-log.md`

Then inspect `software/` and run its tests before editing.

## Operating rules

- Determine the current stage gate from the master plan and do only the next
  blocked task unless the user requests otherwise.
- Preserve reproducibility: fixed seeds, machine-readable result files, testable
  equations, explicit units, and environment/version records.
- Keep private schedules, shopping notes, abandoned claims, and personal
  planning in `private/` at the project root. That folder is gitignored, so it
  never reaches the public repository. A public repository should contain
  technical documentation, reproducible code, sanitized data instructions,
  figures, and citations. Generated `results/`, `.venv/`, and large datasets
  (`data/`, `*.zarr`, `*.parquet`) are also gitignored.
- Update the user's existing public portfolio with a concise project status,
  one strong figure, the public repository link, and the exact contribution
  status. Do not imply publication or novelty before either exists.
- Treat every “novel,” “first,” and “no prior work” statement as unverified.
  Search IEEE Xplore, ACM DL, IACR/TCHES, arXiv, Google Scholar citation graphs,
  and Google Patents; record query, date, and result in the search log.
- Never convert a conjecture or numerical observation into a theorem. Mark proof
  status as `proved`, `proof sketch`, `conjecture`, or `falsified`.
- Use NumPy/SciPy/cvxpy for the core. ML may estimate leakage or model an
  adaptive observer, but it is not the contribution and must be compared against
  simpler statistical baselines.
- Do not add custom hardware until software and trace-replay gates pass.
- Prefer buying or salvaging calibrated capture/power modules over designing
  commodity regulators, probes, or chargers. Build only a module that exposes
  a research variable unavailable in an inexpensive product.

## Writing rules (permanent, whole project)

- No em dashes anywhere: not the Unicode character U+2014 and not a spaced
  double hyphen used as a dash. Use a comma, colon, semicolon, parentheses, or a new sentence,
  whichever reads best. En dashes in numeric ranges (`1–2 weeks`) are fine.
- Keep language simple. Keep the technical jargon that a reader in the field
  needs (TVLA, ICC, Stackelberg, SDF), but use short sentences and plain words
  around it. Explain a term once when it first appears.
- Before finishing any documentation change, search all `.md` and `.txt` files
  outside `software/` for U+2014 and confirm zero matches.
- Public tool scope and contribution boundaries are in
  `docs/public-tool-roadmap.md`. Do not add features that the roadmap lists as
  out of scope.

## Safety boundary

All experiments must be defensive and limited to hardware owned by or explicitly
authorized for the researcher. Do not provide workflows for extracting secrets
from third-party devices, bypassing access controls, increasing RF range, or
evading monitoring. Use synthetic keys and test firmware. Keep intentional RF
emissions cabled, shielded, or compliant with applicable regulations.

## Definition of done for each change

1. Tests pass.
2. Equations and code use the same notation and units.
3. A result records seed, configuration, and software version.
4. A claim points to evidence or is labeled as a hypothesis.
5. Public-facing documentation says what is complete and what remains.
