# Code-intelligence experiment surface freeze

Status: `FROZEN`

Recorded: 2026-07-24

Tracking: `orch-8sk.16.5`

## Decision

The later Pi and Codex experiments use the smallest normal public surface that
represents each tool's demonstrated strengths. Tool counts are not equalized,
and no hidden helper fills a missing capability.

The three capability-discovery Terra probes were canceled after the current
Codex CLI failed before inference inside the read-only runner. Their
dispositions remain `UNTESTED`; their failed setup and historical invalid
outputs are excluded. The freeze is based on source registration, public
documentation, and deterministic runtime evidence in `codegraph.md`, `cbm.md`,
`graphify.md`, and `capability-matrix.csv`.

## Frozen identities

| Item | Identity |
| --- | --- |
| Shared fixture | commit `e7ddad2c44321f7b50e60c923b8f0733fb757874` |
| Fixture manifest | `fc12b07aa2219f346ee1e00f52875efae8c52bbb12dc410456e9457ea1b58e24` |
| CodeGraph | `03666584ed9836d7954cbb19e2252081b96fcad9` |
| CBM | `53ebeb4cf1fca0f4b2384e7ab085e529a2d2750b` |
| Graphify | `2fa6cd3d5548577f8c5f591b713f0bf80c1af183` |
| Artifact tokenizer | `gpt-tokenizer@3.4.0:o200k_base` |

Pi and Codex subject revisions are frozen separately by their protocol tasks.
No experiment may fetch or sync an upstream while a comparison is in progress.

## Common controls

- Use a fresh disposable subject clone and a fresh graph/index for every arm.
- Keep tool home, cache, index, output, and temporary state under the assigned
  ignored `scratchpad/code-intelligence/` lane.
- Disable telemetry, watchers, daemons, update checks, credentials, unrelated
  MCP servers, learning overlays, and remote backends.
- Indexing/extraction is setup and measured separately. It is not an answer
  tool call.
- An offline graph-only case study may use only its frozen tool surface.
  Generic shell, file search, file read, web, Git history, another graph tool,
  reference answers, and expected anchors are prohibited in that lane.
- A graph-assisted tracer must call its assigned graph tool first and may then
  use the same source-search and file-read surface as the source-only tracer.
  It may not use another graph tool, web, reference answers, or expected
  anchors. All fallback reads and their tokens are charged to that arm.
- Source returned by the evaluated tool is admissible and labeled as such.
  Documentation and synthesized architecture remain hypotheses until verified
  by the independent reference lane.
- Controlled source-only and graph-assisted arms retain the same model,
  effort, question, output contract, answer-turn limit, and scoring key.
- Capability-discovery setup, failed probes, invalid historical sessions, and
  local artifact-token totals are excluded from controlled provider-token
  comparisons.

## CodeGraph surface

Setup:

- `init` or full `index` against a disposable clone;
- `CODEGRAPH_NO_DAEMON=1`, `CODEGRAPH_NO_WATCH=1`,
  `DO_NOT_TRACK=1`;
- verify `status` before the measured answer.

Allowed answer operations:

| Adapter name | Public capability |
| --- | --- |
| `query` | symbol search |
| `explore` | ranked source-rich architecture/lifecycle exploration |
| `callers` | inbound call/reference traversal |
| `callees` | outbound call/reference traversal |
| `impact` | reverse graph impact traversal |
| `node` | symbol or file source inspection |
| `status` | index status and counts |
| `files` | indexed-file inventory |

Require file qualification for duplicate symbols. Treat `explore` synthesis,
cross-language links, and `impact` as hypotheses. Incremental sync is excluded
from initial measured arms even though it worked on the small fixture.

## CBM surface

Setup:

- create a fresh `full` index in a new cache;
- disable persistence and cross-repository mode;
- verify `index_status` before the measured answer.

Allowed answer tools:

- `search_graph`
- `query_graph`
- `trace_path`
- `get_code_snippet`
- `get_graph_schema`
- `get_architecture`
- `search_code`
- `list_projects`
- `index_status`
- `detect_changes` only for an explicitly designated change question

`index_repository` is setup-only. `delete_project`, `manage_adr`, and
`ingest_traces` are excluded from answer turns. Do not use incremental refresh,
grouped aggregate queries, persistence, or automatic watcher results as
authoritative evidence. Use qualified names for collisions and small limits
for semantic search.

## Graphify surface

Setup:

- run a fresh local `--code-only` extraction;
- store output outside the subject clone;
- do not create a learning/reflection overlay;
- verify graph summary and diagnostics before the measured answer.

Allowed answer operations:

| Adapter name | Public CLI capability |
| --- | --- |
| `query` | BFS/DFS graph-context query |
| `explain` | exact-node explanation |
| `path` | graph path between exact nodes |
| `affected` | reverse relationship traversal |
| `god_nodes` | `god-nodes` hub inspection |
| `diagnose` | local graph diagnostics |
| `benchmark` | local corpus/query-size estimate |

Use exact node IDs whenever labels collide. Exclude `update`, memory/reflection,
graph merge, exports, installers, hooks, global/provider registries, PR tools,
remote databases, semantic backends, and optional parser installation from
initial measured answer turns. Graphify's benchmark is not a provider-token
saving measurement.

## Explicit exclusions

The following are inventoried but not activated:

- network, GitHub, cloud, provider, telemetry, upgrade, and remote-search paths;
- credentials, external databases, paid semantic/model backends, and global
  host configuration;
- tool installation/uninstallation during measured runs;
- cross-repository graphs, persistence overlays, ADR mutation, runtime-trace
  ingestion, visualization/export, and automatic code changes;
- any retry of the canceled capability-discovery Terra probes.

An excluded capability may be introduced only through a new Beads decision
that states the question it answers, safety boundary, expected token cost, and
why the existing surface is insufficient.

## Cost accounting

For each later arm, record:

- setup wall time, peak RSS when available, index/output bytes, and local
  artifact tokens;
- answer-turn tool-call count and returned bytes/tokens;
- provider input, cached input, output, and reasoning tokens from provider
  events;
- contamination and failure status.

Local artifact tokens and provider tokens remain separate. A missing
measurement is `UNKNOWN`, never zero. Failed or contaminated runs remain in
the ledger but are excluded from quality and savings comparisons.
