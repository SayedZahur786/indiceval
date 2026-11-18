# IndicEval — research preview specification

## User job
An India-focused model builder needs to measure whether an agent can follow
Hinglish and Indic-language instructions, inspect failures, and share a result
that another researcher can reproduce. Success means an auditable experiment,
not merely a position on a leaderboard.

## Five core flows
1. Discover the benchmark: inspect scope, language/type coverage, release hash,
   provenance, review status, methodology, and limitations before running it.
2. Explore tasks: search and filter 200 tasks, inspect a prompt, verified target,
   executable checks or derivation, paired English control, and source record.
3. Evaluate an OpenAI-compatible chat endpoint: configure model, sampling,
   repetitions, token prices and timeouts; save raw responses and run metadata.
4. Interpret results: compare two repetitions, accuracy, unbiased pass@k,
   per-task cost, latency, failures, and breakdowns by task type and language.
5. Submit evidence: validate a complete run bundle locally, open a repository
   contribution with the artifact and disclosure, and publish only reviewed
   results. Task corrections and human review are separate contribution flows.

## Dataset contract
200 task records; 50 each for code generation (Hinglish adaptation of MIT
HumanEval), mathematical reasoning (Hindi, GSM8K-Hi), causal reasoning (Tamil,
XCOPA), and reading comprehension (Bengali, XQuAD-IN). All retain source IDs,
licences, original answers, transformations, and upstream revision hashes.
The 150 non-code tasks retain upstream human-review evidence. The 50 new
Hinglish translations require independent language review; English source
review does not transfer to them. This distinction must be visible in the UI.
English controls are provided where the upstream mapping is reliable; no
claim of a fully crossed language-by-task design is permitted.

## Data model
- Task: id, version, type, language, prompt, English control, answer/checks,
  reference solution/derivation, source id, licence, review state, content hash.
- Source: id, origin, exact repository path, rights basis, licence, consent
  applicability, transformation notes, contamination notes.
- Review: task id/hash, reviewer handle, timestamp, language and answer
  decisions, permission to publish the review, notes.
- Run: schema version, run id, dataset hash, model, sanitized endpoint,
  sampling settings, seed, run time, git commit, pricing, environment.
- Sample: task id, repetition, sample index, output, pass/fail/error,
  token usage, wall latency, optional estimated cost.
- Report: coverage, per-repeat accuracy, sample variance and range, pass@k,
  per-language/type aggregates, latency distribution, cost completeness.
- Submission: immutable run bundle, disclosure, reviewer decision, report.

## Methodology decisions
Use deterministic normalized exact/numeric equality for answers and Docker-isolated
execution for Python code. Never execute model code directly on the host.
Report malformed responses and request failures in the denominator. Unknown
usage/pricing means unknown cost, never a fabricated zero. Only calculate
pass@k for k <= samples per task. Two repetitions expose observed variability;
they do not establish statistical reliability. No invented model scores.
Local fixture results exercise infrastructure and must never rank as models.

## Vertical slices
1. Dataset schema, sources, independent answer checks, review ledger.
2. API runner, isolated code grading, metrics, unit/integration tests.
3. Explorer, leaderboard, run inspector, submission guide and policy pages.
4. Twice-run validation, launch gates, screenshots, GitHub and Vercel preview.

## Out of scope
Claims of representing all Indian languages; autonomous multi-step agent
environments; training data; LLM-as-judge subjective scoring; hidden test-set
security; paid hosted execution; user accounts; unsupported model rankings;
commercial readiness claims; human-review claims without evidence.

## Release gates and dependencies
The supplied DONE list is the release contract. Record pass/fail/evidence in
LAUNCH.md. The user confirmed that no launch kit exists and authorized a new Desktop
folder and GitHub repository. Use the documented project launch checklist. A research preview may
be deployed while human review is pending, but must visibly state that status.
No provider key is exposed at initial inspection; use clearly labeled local
protocol fixtures until a real endpoint is available.

## Research context
The name overlaps existing independent research. This project is unaffiliated
with IndicEval-XL, HinglishEval, and other IndicEval projects. Do not claim
novelty from the name. See docs/DESIGN_REVIEW.md for sources and tradeoffs.
