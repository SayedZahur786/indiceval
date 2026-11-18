# IndicEval launch gate — 19 November 2026

**Decision: public research preview deployed; full research-release gate not met.**

Public site: https://indiceval.vercel.app  
Preview: https://indiceval-50e3rys9g-braveeminent-gmailcoms-projects.vercel.app  
Repository: https://github.com/SayedZahur786/indiceval  
Source folder: /Users/sayedzahur/Desktop/IndicEval

The user clarified that no shared launch kit exists. This project checklist
covers the supplied requirements; it is not represented as a kit's checklist.

| Gate | Status | Evidence / remaining action |
| --- | --- | --- |
| Research and user-persona planning before implementation | PASS | SPEC.md and docs/DESIGN_REVIEW.md; first commit is specification |
| 200 tasks / four task types | PASS | data/manifest.json; 50 per type |
| Every task has a documented source | PASS | pinned revisions, item IDs, data/sources.json |
| Verified reference answers | PASS with limits | docs/evidence/answer-verification.json; execution, arithmetic, source-label and span checks; not independent human adjudication |
| 200 hand-checked tasks | NOT MET | 150 upstream-reviewed; 50 new Hinglish adaptations await human review |
| Source licensing | PASS | per-record licence and preserved texts; CC BY-SA kept |
| Individual source consent evidence | NOT MET | published licence basis recorded; upstream annotator paperwork unavailable |
| OpenAI-compatible runner | PASS | Python harness and HTTP end-to-end tests |
| Accuracy, pass@k, cost/task, latency | PASS | tested estimators; unknown cost retained; methodology published |
| Two full repeated runs / variance | PASS for diagnostic only | 400 HTTP fixture requests; both 200/200; variance 0 |
| Real model baseline | NOT MET | no provider endpoint/key supplied; no fabricated rankings |
| Unit and end-to-end tests | PASS locally | docs/evidence/pytest.txt |
| Remote CI | BLOCKED externally | Actions run 44400543680: job not started because account locked due to billing |
| Submission validation | PASS | complete grid, hashes, report recomputation, output regrading and cost checks; fixture exclusion |
| Public leaderboard page | PASS | live empty state; evidence-linked accepted-row pipeline; no accepted models |
| Task explorer and report inspector | PASS | browser-checks.json; filters, search, paging, details, local report |
| Privacy, terms and licence pages | PASS | live pages, HTTP 200 |
| Methodology and limitations | PASS | methodology.html, README; contamination and sampling caveats |
| Generated-code isolation | PASS with limits | no network/host mounts; unprivileged, bounded containers; not multi-tenant hardening |
| Secret hygiene | PASS | env files ignored; keys never written by runner; no raw error bodies |
| Security headers / invalid route | PASS | deployment-smoke.json; CSP, nosniff, DENY; 404 |
| Responsive UI | PASS at tested widths | desktop and 390px browser checks; no mobile horizontal overflow |
| Analytics | PASS wiring/enabled | Vercel CLI confirmed enabled; public analytics script HTTP 200; no report custom events |
| Deployment and public smoke tests | PASS | deployment-smoke.json and browser-checks.json |
| README with screenshots | PASS | docs/screenshots and README.md |
| Three launch drafts | PASS | docs/LAUNCH_POSTS.md; drafts only |
| Known gaps recorded | PASS | README and this gate |
| No fabricated scores or human sign-offs | PASS | fixtures excluded; review status explicit |

## Verification interpretation

The fixture knows the reference answers. Its 100% result must not be cited as
model quality. The local test suite covers estimator edge cases, hash tampering,
incomplete samples, numeric normalization, HTTP failure handling, full API
workflow, fixture exclusion, grade tampering and Docker isolation.

Manual browser checks cover filtering, search, pagination, answer reveal,
local report display, mobile width and deployed task-source inspection.
HTTP checks cover all public policy pages, the downloadable corpus, analytics
script, security headers and missing-page behavior.

## Remaining full-release dependencies

- Independent language reviewers for 50 Hinglish adaptations, with recorded
  semantic checks, reviewer identity/date and consent to publish the reviews.
- A real configured model endpoint and explicit model identity for a baseline.
- Upstream individual consent evidence if that remains a strict launch gate.
- Resolution of GitHub's account billing lock so remote CI can run.
- A balanced language-by-task design and more repetitions for research claims.

No fabricated review, consent, baseline or CI success substitutes for these.
