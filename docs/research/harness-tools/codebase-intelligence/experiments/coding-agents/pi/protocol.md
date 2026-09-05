# Pi primary-agent-turn tracer protocol

Status: `FROZEN`

Recorded: 2026-07-24

Tracking: `orch-8sk.17`

## Decision

The initial Pi comparison contains one question and four fresh, independent
answer turns:

1. Graphify-assisted
2. Source-only
3. CBM-assisted
4. CodeGraph-assisted

The order is the ascending SHA-256 order recorded in `tracer-arms.json`, using
the frozen seed and arm ID. This is one tracer case study, not a statistically
generalizable estimate.

Every arm uses Pi commit
`24bace27cf308c89707cf8005b4795d873e23f17`,
`gpt-5.6-terra`, medium reasoning effort, the same question, the same answer
schema, and one answer turn. There are no automatic retries, repair turns, or
additional replicates.

No provider session is authorized by this file. Before the four turns, report
the frozen batch and request explicit user approval. After each turn, report
provider usage. Any setup failure stops the batch before retrying.

## Question and output

- Question: `PI-T01` in `tracer-prompt.md`
- Answer contract: `tracer-answer.schema.json`
- External metrics: `tracer-metrics.schema.json`
- Arm configuration: `tracer-arms.json`

The arm configuration pins SHA-256 digests for the prompt and both schemas.
Preflight rejects any content drift before a run.

The answer contains no arm label so it can be normalized for later blinded
review. Arm identity, provider usage, operations, elapsed time, and
contamination are recorded outside the answer.

The scoring anchor and mandatory source facts are deliberately absent. They
belong to `orch-8sk.3` and must be frozen before any measured runner sees the
question.

## Access contract

All arms operate in a read-only disposable Pi clone. They may search and read
that clone, but may not use the web, Git history, learning workspace,
reference answer, scoring anchor, live submodule, or another graph tool.

The source-only arm has no graph interface. Each assisted arm must make its
first repository-information operation through its assigned graph, after
which it may use the same source-search and file-read surface as source-only.
Fallback reads and their tokens are charged to that assisted arm.

The enabled graph operations are frozen explicitly in `tracer-arms.json`.
They are subsets of the public surfaces frozen by
`../capabilities/experiment-surface-freeze.md`. CBM setup and change-analysis
operations are not exposed for this lifecycle question.

## Setup versus answer accounting

Fresh indexing or extraction occurs before a measured answer and is recorded
separately:

- CodeGraph: full index, then `status`;
- CBM: fresh full index in a lane-local cache, then `index_status`;
- Graphify: fresh offline `--code-only` extraction outside the subject clone,
  then summary and diagnostics.

Setup records wall time, peak RSS when available, output bytes, local artifact
tokens, indexed/skipped files, and zero or observed model tokens. These values
are never added to provider usage.

The measured answer records provider input, cached input, output, and reasoning
tokens from the completion event; graph calls; source searches; file reads;
returned bytes and local tokens; elapsed time; outcome; and contamination.
Missing fields are `UNKNOWN`, never zero.

## Stop and classification rules

- Failure before inference is `SETUP_FAILURE`, not an answer result.
- Missing provider usage, multiple turns, or an unexpected provider failure
  stops the batch.
- Pre-graph source access in an assisted arm is contamination.
- Web, another graph, live-submodule access, reference/scoring material, or an
  unexpected write is contamination.
- A contaminated or failed arm remains in the ledger but is excluded from
  quality and token-savings claims.
- An arm above 12 credit-equivalent stops the batch.
- Any retry, repair, replicate, additional question, reviewer session, or
  model escalation requires new explicit approval.

## Deterministic preflight

Run:

```bash
python3 -m unittest \
  docs/research/harness-tools/codebase-intelligence/experiments/coding-agents/pi/test_protocol.py

python3 \
  docs/research/harness-tools/codebase-intelligence/experiments/coding-agents/pi/preflight.py \
  --config \
  docs/research/harness-tools/codebase-intelligence/experiments/coding-agents/pi/tracer-arms.json
```

The preflight validates the schemas, four-arm contract, deterministic order,
frozen public operation subsets, clone roots, commits, and clean state. It does
not invoke Codex or any provider.
