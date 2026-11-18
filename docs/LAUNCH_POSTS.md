# Launch drafts — not published

## 1. Short community post

Shipping an IndicEval research preview: 200 sourced coding/reasoning tasks across
Hinglish, Hindi, Tamil and Bengali, an OpenAI-compatible Python runner, and an
inspectable task explorer.

Raw outputs, pass@k, cost, latency and repeat variance travel with every run.
No invented rankings: model submissions are open.

150 tasks retain upstream review evidence; 50 new Hinglish adaptations still
need independent language review. Help audit them:
https://indiceval.vercel.app
https://github.com/SayedZahur786/indiceval

## 2. Research community discussion

How do we make Indic-language evaluations easier to audit?

IndicEval is a small research preview focused on that workflow: inspect a task,
follow its source and licence, run an endpoint twice, and share the raw evidence
behind the score. It includes 200 tasks drawn from HumanEval, GSM8K-Hi, XCOPA and
IndicGenBench, plus new Hinglish adaptations of the coding prompts.

The important caveats are public: the Hinglish adaptations need independent
review, task type and language are coupled, and public benchmark contamination
is possible. This is not a new state-of-the-art claim or a full autonomous-agent
benchmark. The leaderboard has no accepted model submissions yet.

We would particularly value translation review, scoring-contract criticism and
reproducible model submissions. Sources and limitations:
https://indiceval.vercel.app/methodology.html
Code: https://github.com/SayedZahur786/indiceval

## 3. Technical release announcement

IndicEval v0.1 research preview is available.

The release includes a uv-based Python harness, OpenAI-compatible API runner,
restricted Docker execution for Python outputs, deterministic answer graders,
content-addressed tasks, raw JSONL evidence and a static Vercel interface.

Metrics include first-sample accuracy, unbiased pass@k, declared-price cost
estimates, API latency distributions and repeated-run sample variance. Failed
requests stay in the denominator; absent pricing remains unknown. Submission
validation checks completeness, recomputes metrics and regrades outputs.

The reference-answer HTTP diagnostic passed all 200 tasks in both repetitions
(400 requests; variance 0). This verifies infrastructure, not model performance.

Before treating the release as a research baseline, read the limitations:
50 Hinglish adaptations await independent review, upstream consent paperwork
is unavailable, and the four language/task strata are not a controlled
cross-language experiment. Model submissions and careful reviews are welcome.

Live: https://indiceval.vercel.app
Source: https://github.com/SayedZahur786/indiceval
