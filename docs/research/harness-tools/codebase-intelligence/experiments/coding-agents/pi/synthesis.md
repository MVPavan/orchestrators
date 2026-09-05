# Pi primary-turn tracer synthesis

Status: tracer review complete; independent adjudication and learner gate
pending

Reviewed: 2026-07-25

Tracking: `orch-8sk.18`

Subject revision: `24bace27cf308c89707cf8005b4795d873e23f17`

## Decision

All four accepted answers were operationally valid, source-grounded, and free
of contamination. None passed the frozen equal-quality gate.

The graph-assisted arms reduced source navigation, but they did not eliminate
source reading and did not preserve every mandatory systems fact. Therefore
this tracer does **not** establish a token-saving winner. Operational token and
navigation deltas are reported below, but they must not be described as
savings at equal answer quality.

The first Pi lesson is built from the frozen source reference, not from any
single experimental answer.

## Evidence and review method

The accepted lineage is retained under:

`scratchpad/code-intelligence/sessions/pi-tracer-v1/authorized-codegraph-retry-2/`

The review used:

- [the frozen reference ledger](reference-ledger.md);
- [the frozen scoring key](tracer-scoring-key.json);
- normalized answer documents without arm names;
- provider completion metrics and evaluated-interface audits;
- a mechanical check that every cited repository path exists in the frozen Pi
  subject clone.

Answers were labeled by ascending answer SHA-256 before review:

| Blind label | Revealed arm |
| --- | --- |
| A | CBM-assisted |
| B | Source-only |
| C | Graphify-assisted |
| D | CodeGraph-assisted |

This was identity-masked, not independently blinded. The same orchestrator had
observed run progress before scoring. No separate reviewer model was launched,
consistent with the no-extra-model policy. Because every answer was at or
within one point of the numeric threshold, the frozen method calls for a
second review; that remains pending explicit approval or learner adjudication.

## Quality result

Each dimension is scored from 0 to 2. Numeric score alone is insufficient:
all twelve mandatory facts must be present, and factual precision and citation
correctness must both score 2.

| Arm | Precision | Coverage | Citations | Mechanism | Uncertainty | Learning | Total | Mandatory facts | Gate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| CBM | 2 | 1 | 2 | 2 | 2 | 2 | 11 | 9/12 | FAIL |
| Source-only | 2 | 0 | 2 | 2 | 2 | 2 | 10 | 7/12 | FAIL |
| Graphify | 2 | 1 | 2 | 2 | 2 | 2 | 11 | 10/12 | FAIL |
| CodeGraph | 2 | 0 | 2 | 2 | 2 | 2 | 10 | 8/12 | FAIL |

Detailed machine-readable scores are in
[tracer-quality-scores.csv](tracer-quality-scores.csv).

### Shared omission

Every answer described `InteractiveMode` creating or updating assistant and
tool components. None completed mandatory fact F11: render requests are
coalesced by Pi TUI, and the terminal receives a full or differential write.
The answers stopped at “request render,” which is not the final rendered
outcome asked by the tracer.

### Other decisive omissions

- No answer fully covered F10: finalized messages become parent-linked JSONL
  entries, while session ID, entry ID/`parentId`, and tool-call ID have
  distinct roles.
- Source-only did not trace the `Agent` active-run snapshot deeply enough,
  omitted the `ModelRuntime` delegation boundary, and did not explain
  assistant-order reconstruction of parallel tool results.
- CBM did not make the `ModelRuntime` delegation boundary explicit.
- CodeGraph omitted assistant-order reconstruction for parallel tool results
  and did not state the core no-sandbox/no-general-permission conclusion.

All cited paths existed. No automatic failure such as a fabricated path,
critical contradiction, or false project-trust sandbox claim was found.

## Accepted operational measurements

| Arm | Input | Cached input | Output | Reasoning | Credits | Graph calls | Searches | Reads | Returned bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Graphify | 331,560 | 272,640 | 5,324 | 373 | 7.383000 | 1 | 4 | 7 | 189,515 |
| Source-only | 385,600 | 320,000 | 5,416 | 682 | 8.131000 | 0 | 7 | 9 | 218,051 |
| CBM | 452,556 | 380,160 | 5,399 | 348 | 8.925375 | 2 | 4 | 7 | 344,245 |
| CodeGraph | 549,574 | 481,792 | 5,591 | 679 | 9.344200 | 3 | 4 | 8 | 216,603 |

Accepted-arm totals:

- input: 1,719,290;
- cached input: 1,454,592;
- output: 21,730;
- reasoning: 2,082;
- credit-equivalent: 33.783575;
- elapsed: 524,170 ms.

Relative to source-only, these are operational deltas, not quality-adjusted
savings:

| Arm | Credits | Input | Searches | Reads |
| --- | ---: | ---: | ---: | ---: |
| Graphify | -9.20% | -14.01% | -42.86% | -22.22% |
| CBM | +9.77% | +17.36% | -42.86% | -22.22% |
| CodeGraph | +14.92% | +42.52% | -42.86% | -11.11% |

## What each graph actually contributed

### Graphify

One broad BFS query returned 6,845 bytes and surfaced relevant `Agent`,
`Context`, `runWithLifecycle`, and tool-finalization nodes. It helped the agent
start with four targeted source searches instead of seven and produced the
lowest operational cost. The seed set also contained unrelated nodes, so the
result was a navigation hint rather than a trustworthy trace. Source
verification still required seven reads. Its answer tied for the strongest
quality score but missed persistence identity and terminal rendering.

### CBM

The first architecture call failed because the indexed project name differed
from the requested short name. A subsequent BM25 graph search reported 1,433
matches and returned 14,361 bytes, including noisy example symbols. The agent
still read 344,245 local bytes, the largest tool-return-plus-source burden of
the accepted arms. CBM helped surface tool-result ordering and session
relationships, but it cost more than source-only and missed the provider
delegation and final rendering boundaries.

### CodeGraph

The accepted run used three graph calls. Broad exploration returned 25,408
bytes, a query returned 7,016 bytes, and a caller lookup returned no callers.
It reduced searches from seven to four but produced the highest accepted input
and credit usage. It also incurred one schema-invalid answer and one
unmeasured provider failure before the accepted replacement. The graph was
useful for locating symbols, but its broad output did not improve answer
quality over source-only.

### Source-only

Source-only required seven searches and nine reads. It was cheaper than CBM
and CodeGraph but missed more mandatory facts because broad file reading did
not force explicit treatment of active-run ownership, parallel-result
ordering, persistence identity, or terminal diff rendering.

## Failure and overhead accounting

The accepted four turns are not the full cost of stabilizing this tracer.
[token-usage.csv](token-usage.csv) preserves every measured or unmeasured
controlled-tracer attempt retained in the current run history.

Known measured controlled-tracer usage, including rejected attempts:

- input: 3,506,531;
- cached input: 2,972,416;
- output: 39,093;
- reasoning: 3,750;
- credit-equivalent: 66.619663.

Two provider failures have `UNKNOWN` usage because no completion event arrived.
Pre-inference configuration and schema rejections are setup evidence and are
not assigned inferred zero usage in this ledger. Separate native smoke and
capability-discovery sessions remain outside the controlled tracer accounting.

## Conclusions

1. Graphs helped choose source locations; they did not replace source
   verification.
2. Lower navigation count did not guarantee lower provider cost. Graphify was
   operationally cheaper, while CBM and CodeGraph were more expensive.
3. None of the four answers reached equal reference quality, so no
   quality-adjusted token-saving claim is permitted.
4. The common omissions show that the prompt encouraged a strong model/tool
   loop explanation but did not reliably force persistence identity and the
   terminal-rendering mechanism.
5. For human learning, the reference lane is the teaching authority. Tool
   outputs are useful examples of retrieval strengths and blind spots.

## Next gate

Use the source-backed lesson in
`docs/learning/coding-agents/lessons/0001-pi-primary-agent-turn.md`. The learner
must teach the lifecycle back, repair the first vague link through one
Socratic probe, answer one transfer question, and approve or revise the lesson
format before `orch-8sk.18` closes.
