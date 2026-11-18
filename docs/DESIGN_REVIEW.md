# Research and product design review

Planning began before implementation on 19 November 2026 (Asia/Kolkata).

## Research-engineer perspective
A score needs an immutable dataset, explicit sampling policy, stable grader,
raw outputs, error accounting, and enough metadata for reproduction. Different
languages and task types must not silently share a single interpretation.
Code must run isolated; a reference answer is not evidence of model ability.
Two repeats report observed variance only. A public test set cannot provide a
credible contamination-free claim. Source human review and new adaptation
review must be represented separately.

## Researcher-user perspective
A researcher should inspect a real task before installing anything, understand
what a score means, copy a working command, and see why a submission qualifies.
Do not require an account or expose API keys in a browser. Provide downloadable
tasks, raw evidence, filters, a local report inspector, and correction links.
Make the empty leaderboard a truthful invitation to submit, not fabricated data.

## Discussion and decisions
- Broad coverage versus credibility: launch four sourced strata (50 each), not
  a purported representative sample of India. Type and language are confounded;
  do not interpret the strata as a cross-language comparison.
- Novel tasks versus reviewed sources: import licensed published benchmarks.
  Add Hinglish adaptations of HumanEval with unchanged executable tests. Their
  translations are new and require independent review; do not inherit an English
  task's human review as proof of Hinglish quality.
- Convenient scoring versus validity: exact normalized answers for extraction,
  numeric equality for math, discrete choices for causal reasoning, isolated
  functional tests for Python. Exact match misses valid paraphrases; expose this.
- Attractive rankings versus evidence: publish no model row without a real run.
  A local reference fixture is a diagnostic and is never leaderboard-eligible.
- Full agent evaluation versus honest scope: this release evaluates single-turn
  capabilities of agent backends, not planning, tool use or repository repair.
- Usability versus uncontrolled execution: API calls happen in a local Python
  CLI; Docker is mandatory for code grading. No browser-supplied code runs on
  the site or in the host process.

## Source research
- HumanEval: https://github.com/openai/human-eval (MIT, human-written source
  problems and tests; new Hinglish adaptation review is pending).
- NVIDIA GSM8K-Hi: https://huggingface.co/datasets/nvidia/GSM8K-Hi (CC BY 4.0;
  dataset card documents human review and correction of translations).
- XCOPA: https://github.com/cambridgeltl/xcopa (CC BY 4.0; translated and
  reannotated causal reasoning tasks; use data/, never machine-translated data-gmt/).
- IndicGenBench XQuAD-IN: https://github.com/google-research-datasets/indic-gen-bench
  (CC BY-SA 4.0; professional human translations; retain canary and attribution).
- Related work: https://github.com/mrigankpawagi/HinglishEval. Human-verified
  Hinglish translations exist, but an explicit repository redistribution license
  was not found; not imported.
- Related work: https://github.com/telekom/IndicEval-XL and
  https://arxiv.org/html/2502.19067v1. Sampled human review does not establish
  item-level verification; observed mistranslated examples and ambiguous licence
  packaging make it unsuitable for this first import. Not imported.
- pass@k reference: https://github.com/openai/human-eval/blob/master/human_eval/evaluation.py

No claim of affiliation, novelty, or a new scientific finding is made.
The user clarified that no launch kit exists; a fresh repository is authorized.
