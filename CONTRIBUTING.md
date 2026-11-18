# Contributing to IndicEval

## Model submissions

1. Use the frozen dataset and unmodified runner from the same commit.
2. Run all 200 tasks for at least two repetitions.
3. Preserve run.json, samples.jsonl and report.json.
4. Run: uv run indiceval validate-run runs/my-model --submission
5. Open a result-submission issue with a public artifact URL and the commit.
   Declare model version, endpoint provider, sampling, tools, prompt changes,
   known training exposure, pricing and currency. Do not publish credentials.
6. A maintainer checks the complete task/sample grid, hashes, source records,
   grading and cost calculations. Report validation alone is not authentication.
   Run untrusted code only in an isolated disposable environment.
7. Accepted artifacts are committed under results/, and leaderboard entries
   link to those artifacts. Never rank a fixture or reference-answer oracle.

No automatic acceptance or review turnaround is promised. A changing alias is
not an immutable model version; state the provider's available version evidence.
Two repeated runs are not a statistically significant model comparison.

## Task corrections and language reviews

Open a task-review issue identifying task ID and hash. Include the original and
proposed wording, source evidence, and rationale. Do not copy unlicensed text.
A human review must state the reviewer's handle, language competence, review
date, semantic equivalence decision, answer/test decision, and permission to
publish that review. Never sign a human-review entry on someone else's behalf.

Review status changes require evidence. Changes to prompts or grading require a
new dataset hash and version; old results must retain the prior version.
Hinglish reviews are particularly needed for the 50 code adaptations.

## Development

    uv sync --frozen
    docker pull python:3.12-slim
    uv run pytest -q
    uv run python scripts/verify_answers.py
    uv run python scripts/build_pages.py
    uv run python scripts/build_site.py

The importer reuses pinned source metadata. To introduce a new source revision,
review its licence and changes, then explicitly update the source manifest.
Original data and upstream notices remain in data/upstream and data/licenses.

## Conduct

Be specific, respectful and evidence-based. Avoid personal attacks and publishing
private information. Maintainers may remove abusive or irrelevant submissions.
