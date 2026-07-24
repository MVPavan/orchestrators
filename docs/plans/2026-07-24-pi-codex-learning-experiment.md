# Pi and Codex Learning and Code-Graph Tool Evaluation Plan

**Status:** Approved and revised to lean tracer-first execution on 2026-07-24;
Phase 0B capability discovery complete; Phase 0C in progress

**Execution boundary:** Offline preparation, indexing, direct graph queries, and
source-grounded research are approved. Do not launch a provider/model session,
repair, retry, replicate, or escalation without the explicit approval required
by Section 3.4.

**Order:** Pi first; Codex only after the Pi learning gate. Pydantic AI and Deep Agents are deferred.

**Beads planning task:** `orch-ge6` (closed)

**Beads execution epic:** `orch-8sk`

## 1. Objective

Build a durable, source-grounded understanding of two unfamiliar coding-agent repositories:

1. `external/coding-agents/pi`
2. `external/coding-agents/codex`

At the same time, determine how well these three tools help an agent and a human understand those repositories:

- CodeGraph
- codebase-memory-mcp (CBM)
- Graphify

The work has two equally important outcomes:

- a mental model the learner can explain, trace, challenge, and apply; and
- evidence about each tool's capabilities, limitations, operating workflow, and token economics.

The learning outcome takes precedence. A tool result is never accepted as true merely because it came from a graph.

This is a systems-engineering study. Source code is evidence for system behavior, but programming syntax, language idioms, and line-by-line implementation technique are not learning objectives.

## 2. Questions This Work Must Answer

### About Pi and Codex

- What problem does the repository solve, and where are its system boundaries?
- Which subsystems, processes, services, and public interfaces exist, and who owns each control decision?
- Where are the control plane, data plane, trust boundaries, and dependency directions?
- What happens from user input through model inference, tool execution, state update, and rendered output?
- How are sessions, turns, messages, context, compaction, persistence, and resume represented?
- Which identities and invariants link those state transitions?
- How are providers, tools, extensions, skills, plugins, hooks, or adapters connected?
- Where are permissions, approvals, sandboxing, process execution, and network boundaries enforced?
- How do streaming, concurrency, scheduling, cancellation, retries, failures, recovery, and shutdown work?
- How is the system deployed, configured, observed, debugged, tested, and operated?
- What are the scaling constraints, bottlenecks, and failure domains?
- What are the important architectural tradeoffs, and where is our understanding still inferential?

### About CodeGraph, CBM, and Graphify

- What does each tool actually index and model?
- How should each tool be installed, isolated, indexed, queried, refreshed, and debugged?
- Which questions does each answer well, partially, incorrectly, or not at all?
- What evidence does it return: source, symbols, edges, paths, clusters, or generated prose?
- Where does it silently lose recall or merge unrelated symbols?
- What is the indexing cost in wall time, memory, disk, and model tokens?
- What is the per-session schema cost, per-query output cost, and total agent token cost?
- Does it reduce total tokens and file reads at equal answer quality?
- How does it help the learner form and retain a better mental model?

## 3. Scope and Non-Goals

### In scope

- Pi at its frozen submodule commit.
- Codex at its frozen submodule commit.
- CodeGraph, CBM, and Graphify only.
- Source reading, local indexing, read-only graph queries, controlled agent runs, and teaching sessions.
- Markdown-first canonical research and learner-specific records.
- Small synthesized tables and reports in Git; large indexes and raw logs in `scratchpad/`.

### Out of scope

- Pydantic AI and Deep Agents until the user explicitly starts their phase.
- Changing code inside any upstream submodule.
- Updating submodule pointers during the experiment.
- Comparing other code-intelligence tools.
- Editing, refactoring, or fixing Pi or Codex.
- Using tool-generated architecture prose as ground truth.
- Merging, rebasing, pushing, publishing, or opening pull requests.
- Committing large CodeGraph, CBM, or Graphify index artifacts.
- A paid or API-backed Graphify semantic pass in the primary comparison.
- Teaching TypeScript or Rust syntax, programming style, or language-specific implementation techniques.
- Exhaustive line-by-line code review or algorithm study unless an implementation detail materially changes system behavior.

Graphify's primary run will be code-only and offline. A separately measured semantic-labeling run may be proposed later, but it requires a distinct approval because it changes both cost and experimental meaning.

### 3.1 Systems-engineering lens

Pi and Codex will be understood as complete software systems for coding agents, not as collections of source files. Every report, experiment, and lesson must explain the relevant combination of:

- system purpose, external actors, trust boundaries, and deployment boundary;
- subsystem responsibilities, interfaces, dependency direction, and control ownership;
- control plane versus data plane;
- request, event, message, and tool-call lifecycles;
- state, identity, persistence, context, compaction, and resume invariants;
- scheduling, concurrency, streaming, cancellation, backpressure, retry, and shutdown;
- permissions, approvals, sandboxing, process isolation, networking, and secrets;
- extension contracts for providers, tools, clients, skills, hooks, plugins, and MCP;
- failure domains, recovery behavior, degraded modes, and observability;
- resource use, scaling constraints, operational tradeoffs, and likely bottlenecks.

Source reading goes only as deep as needed to verify these mechanisms. The preferred explanations are component maps, sequence traces, state transitions, invariants, failure scenarios, and design tradeoffs. Syntax, framework trivia, generic algorithms, and language conventions are included only when they change a system-level conclusion.

### 3.2 Cost-efficient model and effort strategy

The model assignment follows current OpenAI guidance and the authenticated local Codex model catalog, both rechecked on 2026-07-24:

- `gpt-5.6-sol` is the frontier model for the hardest architecture and reasoning work.
- `gpt-5.6-terra` is the balanced lower-cost model and is specifically suited to read-heavy exploration and large-file review.
- `gpt-5.6-luna` is the fast, lowest-cost model for bounded, high-volume work.

Current Codex credit rates per one million tokens are:

| Model | Input | Cached input | Output | Relative to Sol |
| --- | ---: | ---: | ---: | ---: |
| `gpt-5.6-sol` | 125 | 12.5 | 750 | 100% |
| `gpt-5.6-terra` | 62.5 | 6.25 | 375 | 50% |
| `gpt-5.6-luna` | 25 | 2.5 | 150 | 20% |

The experiment will therefore use the least expensive assignment that preserves the validity of the work:

| Work | Model and effort | Reason |
| --- | --- | --- |
| CLI/MCP capability enumeration, schema capture, indexing, token counting, manifests, metrics, CSV transforms, and other deterministic work | No model | A model adds cost without adding evidence. |
| Bounded capability-schema or evidence normalization with an explicit source and output schema, only when a deterministic transform is insufficient | Luna low | Cheapest suitable lane; its output is mechanically checked and no capability judgment is delegated to it. |
| Scan-only repository orientation or candidate-file discovery | Terra low | Efficient broad reading before deeper analysis. |
| Comparable agent-mediated capability probes and the cross-tool capability matrix | Terra medium | Natural-language tool use needs a capable agent, and one fixed configuration keeps tool comparisons fair. |
| One approved source-only tracer and its three graph-assisted tracer arms | Terra medium | Same capable, balanced configuration in the four-arm tracer prevents model choice from confounding the comparison. |
| Offline tool-lane investigation, indexing, querying, and evidence capture | No model | CodeGraph, CBM, and Graphify are local parsers/indexers; their raw capability and evidence do not require a provider session. |
| Routine lesson drafting, teaching dialogue, scoring, and systems synthesis | Current orchestrator, without delegated model sessions | Preserve continuity and avoid paying for repeated fresh contexts. A separate model session requires an explicit cost approval. |
| Reference architecture, central lifecycle reconstruction, and anchor selection | Current orchestrator using source and offline evidence | Ground truth is source evidence, not model tier. Escalation to a dedicated Sol session requires explicit approval for a specific unresolved question. |
| Disputed evidence, fairness decisions, or mastery/quality adjudication | No separate model by default | Use source and learner review first. A bounded Sol session is optional only after explicit approval for the contested question. |
| A failed quality gate or irreconcilable evidence | Sol high, then xhigh only if measured benefit is still needed | Higher effort is an exception with a recorded reason and before/after result. |

`max` is reserved for an exceptional unresolved systems question after `xhigh` proves insufficient. `ultra` is excluded from the experiment because its delegated execution changes the independence and cost structure being measured. Although public API guidance discusses a `none` effort in some contexts, the current local Codex catalog advertises `low`, `medium`, `high`, `xhigh`, and `max` for all three models, plus `ultra` for Sol and Terra; Phase 0 must revalidate the live CLI rather than assume `none` is available.

Luna must not select reference anchors, infer central causality, judge system
correctness, or produce the final architecture. Model efficiency will be
judged as **cost to a passing answer**, not price per token alone. A failed
lane is retained and reported; model or effort promotion is never automatic
and requires the explicit approval in Section 3.4.

### 3.3 Strict orchestration and bounded-prerequisite policy

The user approved strict mode with bounded prerequisites on 2026-07-24 after
the capability-discovery review loop caused excessive model usage. Until the
Pi tracer lesson gate, this policy overrides the broader escalation routes in
Section 3.2:

- Use no Sol model and do not escalate model effort.
- Keep at most one model session active. Every delegated task uses a fresh,
  minimal-context Terra session; do not reuse a reviewer or send follow-up
  turns into an accumulated context.
- Use deterministic local checks for manifests, schemas, tests, evidence
  reconciliation, and acceptance whenever code can answer the question.
- Read the final provider token event from the fresh session log after every
  delegated model turn and compute its published-rate equivalent from
  uncached input, cached input, and output tokens. Stop and report before
  another call if telemetry is missing, if one turn exceeds 12
  credit-equivalent, or if the remaining Phase 0B work exceeds 50
  credit-equivalent cumulatively.
- The earlier Phase 0B ceiling was eight delegated model turns. Phase 0B is
  now closed and authorizes no further model turns.
- A failed review or run is recorded as a limitation. Any repair or retry
  follows the stricter explicit-approval rule in Section 3.4.
- Do not expand capability discovery with new languages, frameworks, optional
  backends, credentials, network services, or exhaustive variants. Preserve
  truthful `UNTESTED`, `PARTIAL`, `UNAVAILABLE`, and `RESTRICTED`
  dispositions instead.

The bounded Phase 0B prerequisites are: accept the tested shared runner,
stabilize the current CodeGraph and Graphify evidence sets, retain the
completed CBM deterministic report, and freeze one cross-tool matrix. The user
canceled the three agent-mediated capability probes after the current Codex
CLI failed before inference inside the read-only runner. Those probes remain
`UNTESTED` and excluded.

No further capability work may delay Pi unless it affects safety,
reproducibility, or the fairness of the later controlled arms. After
deterministic evidence stabilization, do not launch additional
capability-discovery model sessions. Produce the matrix directly from the
validated reports, record non-safety limitations, and proceed to Pi.

### 3.4 Lean tracer-first budget decision

The user replaced the exhaustive fresh-session grid with a lean design after
confirming that all three code-intelligence tools are primarily offline
parsers and indexers. This decision supersedes any later wording that implies
one provider session per question, automatic replication, paid smoke sessions,
or automatic repair turns.

- Index and query each tool offline against its own disposable Pi clone.
- Validate runner configuration, schemas, isolation, and tool availability
  deterministically. Do not run paid model smoke sessions.
- Use exactly one initial controlled Pi question: the primary agent-turn
  lifecycle.
- For that tracer only, run four fresh Terra-medium sessions: source-only,
  CodeGraph-assisted, CBM-assisted, and Graphify-assisted.
- Permit one answer turn per arm. A repair, retry, replicate, additional
  question, reviewer session, or model escalation requires a new explicit user
  approval after reporting the observed usage.
- After the tracer gate, use the tools directly for the remaining systems
  questions and continue learning in one coherent research-and-teaching
  workspace. Additional four-arm comparisons are optional experiments, not
  completion requirements.
- A setup failure before inference is classified as setup evidence, not a
  measured result. Stop before retrying it.

The initial paid Pi experiment is therefore capped at four model sessions.
Offline parser work, local artifact tokens, provider usage, and teaching
workspace usage remain separate measurements.

Official sources:

- [OpenAI model guidance for GPT-5.6](https://developers.openai.com/api/docs/guides/model-guidance?model=gpt-5.6)
- [OpenAI Codex pricing](https://learn.chatgpt.com/docs/pricing#what-are-tokens-and-credits)
- [OpenAI recommended models](https://learn.chatgpt.com/docs/models#recommended-models)
- [OpenAI subagent model choice](https://learn.chatgpt.com/docs/agent-configuration/subagents#model-choice)

## 4. Frozen Inputs

The plan is based on the locally checked-out revisions below. Phase 0 will re-record the full SHAs before any experiment and will not fetch or sync upstream:

| Subject/tool | Current local revision | Branch |
| --- | --- | --- |
| Pi | `24bace27cf30` | `main` |
| Codex | `f61b51ddd924` | `main` |
| CodeGraph | `03666584ed98` | `main` |
| CBM | `53ebeb4cf1fc` | `main` |
| Graphify | `2fa6cd3d5548` | `v8` |

Current readiness observations:

- CodeGraph's isolated CLI and offline index/query surface were verified during
  capability discovery.
- CBM's isolated binary and offline index/query surface were verified during
  capability discovery.
- Graphify's isolated import, package version, and offline supported command
  surface were verified during capability discovery; provider-backed and
  restricted paths remain excluded.
- The reconciled runtime/source capability counts and dispositions are frozen
  in the three capability reports and cross-tool matrix.
- Pi is primarily a TypeScript monorepo; Codex is substantially larger and primarily a Rust workspace with additional TypeScript surfaces.

These observations are setup facts, not experiment results.

## 5. Experimental Principles

### 5.1 Separate learning from judging the tools

The work uses four evidence lanes:

1. **Reference lane:** source-first architecture and lifecycle reconstruction.
2. **CodeGraph lane:** CodeGraph-native investigation.
3. **CBM lane:** CBM-native investigation.
4. **Graphify lane:** Graphify-native investigation.

The tool lanes do not read one another's outputs. Tool output does not become reference truth. A later synthesis reconciles all claims against source evidence.

Use a fresh runner context for each lane. Tool runners receive the frozen subject, the questions, the output contract, and the allowed operations, but not the reference answer or scoring key. The reference curator does not see tool outputs until the source anchors and scoring key are frozen.

### 5.2 Use capability-first, assisted, and baseline comparisons

The prior harness experiments showed that these tools are not interchangeable. Therefore:

- **Graph-only capability run:** use each tool the way it is designed to be used, without independent source search, and record its unique wins, failures, and sufficiency.
- **Graph-assisted controlled run:** require the assigned graph tool first, then allow normal source search and file reads as needed for verification or completion.
- **Source-only baseline:** allow the same normal source search and file reads but no graph tool.

The primary token comparison is the single tracer's graph-assisted arms versus
its source-only arm. The remaining question battery is investigated through
offline graph queries and source-grounded learning, not a fresh-session grid.
Graph-only results measure tool sufficiency and explain failure modes; they are
not used alone to claim end-to-end token savings.

### 5.3 Compare at equal answer quality

Token savings are valid only if the answer reaches the same predeclared quality gate. A shorter but incomplete or incorrect answer is not a saving.

Each controlled answer must:

- cover the required reference facts;
- cite real source locations accurately;
- explain causal flow rather than list components;
- distinguish verified facts from inference;
- name relevant limitations or unresolved questions.

Each initial tracer arm has exactly one answer turn. If it misses the quality
gate, retain the failure and report its usage. Do not launch a repair turn
without explicit user approval after the four initial results are visible.

The graph-only capability run may use source returned by the graph tool but may not independently grep or read the subject. The graph-assisted run may search and read source after its required graph query; those operations and their tokens are charged to the tool arm. The source-only baseline uses normal source search and file reading and has no graph access.

### 5.4 Preserve isolation

Create disposable clones for both subjects and tools under `scratchpad/`. Never build, install, index, or create a virtual environment inside a live submodule.

Each subject clone and tool clone must:

- resolve to the same frozen commit;
- contain its own `.git`, preventing CBM from walking into the parent repository;
- have its own explicitly configured cache, state, index, and output paths;
- start with a clean `git status`;
- record a tracked-file manifest before the run;
- be checked for unexpected tracked-source changes and new files after the run.

Tool subprocesses use a minimal environment and must not inherit provider API keys, Git credentials, or unrelated MCP configuration. The offline Graphify arm receives no model credential. If a tool build requires network downloads, system package installation, or writes outside `scratchpad/`, stop and request separate approval.

Do not index the live submodule directly. Do not use a live tool checkout as a build directory. Do not reuse an index between tools or between Pi and Codex.

### 5.5 Prefer evidence over confidence

Every material claim is labeled as:

- **VERIFIED:** supported by a file, symbol, test, command, or runtime observation;
- **INFERENCE:** reasoned from verified evidence but not directly established;
- **OPEN QUESTION:** unresolved or requiring another experiment.

## 6. Common Question Battery

The controlled comparison will use the same core questions on both repositories:

1. **Architecture:** What are the central subsystems and dependency directions?
2. **Primary lifecycle:** Trace one user request or agent turn from entry point to final output.
3. **Model interaction:** Where is model context assembled, sent, streamed, and incorporated?
4. **Tool execution:** How is a tool selected, authorized, executed, and returned to the model?
5. **State and resume:** What persists, what is ephemeral, and how is a session resumed?
6. **Extension model:** Where can providers, tools, plugins, skills, hooks, or clients extend the system?
7. **Safety and failure:** Where are trust boundaries, permissions, sandboxing, cancellation, errors, and recovery handled?
8. **Impact question:** If a selected central abstraction changed, what would be affected?
9. **Disambiguation question:** Can the tool distinguish deliberately selected same-named or similarly named symbols?
10. **Operations question:** How is the system configured, observed, resumed, and debugged in a degraded or failed state?
11. **Onboarding question:** Which system traces and source files should a new systems maintainer study first, and why?

The reference lane will select concrete lifecycle, impact, and collision anchors before tool runners begin. The selection must be based on source centrality and discriminating value, not on what one tool happens to find.

## 7. Repository-Specific Learning Maps

### 7.1 Pi

The initial map will test and refine these boundaries rather than assume them:

- system boundary, external actors, monorepo subsystem responsibilities, and dependency structure;
- provider-neutral model API and streaming events;
- agent control loop, tool-call data flow, and state transitions;
- coding-agent CLI composition and session model;
- terminal UI event/rendering pipeline and backpressure behavior;
- storage and server packages where relevant;
- extensions, custom providers, prompts, and tool registration;
- context management, compaction, persistence, and resume invariants;
- scheduling, concurrency, cancellation, failure, and shutdown;
- trust and permission boundaries, including the implications of relying on host/process permissions;
- deployment, configuration, observability, debugging, and resource constraints.

The first tracer bullet is Pi's primary agent-turn lifecycle. All three tools and the reference lane will answer that one module before the experiment scales to the rest of Pi.

### 7.2 Codex

Codex begins only after the Pi learning gate. Its map will test and refine:

- system boundary, external actors, workspace subsystem responsibilities, and dependency direction;
- CLI, TUI, app-server, protocol, and core responsibilities;
- thread, turn, response-event, and rollout lifecycle;
- model client, context construction, compaction, and history invariants;
- tool registry, execution, patching, and shell/process boundaries;
- approvals, sandboxing, escalation, networking, and secrets;
- configuration, instructions, skills, hooks, plugins, MCP, and connectors;
- persistence, resume, state stores, and diagnostics;
- cancellation, retry, recovery, and concurrency;
- deployment, configuration, observability, testing, and resource/scaling constraints.

The Codex scope will be divided into smaller lessons than Pi because the repository is materially larger. Breadth must not replace a traceable mental model.

## 8. Capability Discovery and Tool-Native Runbooks

Exact commands and versions will be captured in the Phase 0 runbook after live `--help` checks. The intended operations are:

### 8.1 Complete public-capability discovery

“Complete capabilities” means every public capability exposed by the frozen tool revision:

- documented CLI commands, subcommands, flags, and configuration;
- runtime-registered MCP tools, input schemas, resources, prompts, and server instructions;
- supported languages, file types, graph entities/relationships, index/update modes, and query modes;
- installation, health, status, export, visualization, integration, and optional-backend surfaces;
- observable prerequisites, filesystem or network effects, credentials, external services, and failure behavior.

Hidden debug commands and internal functions are recorded separately but are not treated as supported public capabilities merely because they exist in source.

Capability discovery triangulates four evidence sources in this order:

1. **Runtime surface:** recursive CLI `--help`, version output, MCP initialization, `tools/list`, `resources/list`, and exposed schemas.
2. **Source registration:** command dispatchers, MCP registries, schemas, supported-language tables, feature gates, and optional-dependency declarations.
3. **Tests and maintained documentation:** expected behavior, examples, limitations, and claimed coverage.
4. **Runtime probes:** controlled success, boundary, ambiguity, stale-index, unsupported-input, and failure cases.

Runtime discovery at the frozen revision is authoritative about what is actually exposed. Source and documentation explain intent and find surfaces that may be unavailable in the current build; neither is accepted as proof that a capability works.

Every public capability receives one final disposition:

- **VERIFIED:** exercised successfully with expected evidence;
- **PARTIAL:** works only for a documented subset or with material loss;
- **BROKEN:** exposed but fails its declared contract;
- **UNAVAILABLE:** requires an optional dependency or backend absent from the frozen environment;
- **RESTRICTED:** requires credentials, paid services, network access, an external database, or a destructive/remote action not authorized for this study;
- **NOT APPLICABLE:** public capability exists but does not apply to codebase understanding;
- **UNTESTED:** no safe conclusive probe was possible, with the reason recorded.

The discovery procedure is:

1. Capture the frozen revision, build/version, recursive help, MCP schemas/resources, configuration surface, optional dependencies, and source registries without a model.
2. Normalize the inventory deterministically. Luna low may be used only for bounded schema normalization that cannot be expressed reliably as a deterministic transform; its output must be mechanically checked.
3. Build a disposable mixed TypeScript/Rust fixture containing packages, cross-file calls, inheritance or traits, callbacks/events, name collisions, unresolved/dynamic edges, entry points, state, and a synthetic change.
4. Exercise every safe offline public capability. Mutating, update, install, delete, or change-analysis operations run only inside disposable tool and subject clones.
5. Inventory but do not execute restricted network, paid-model, GitHub-write, external-database, global-install, or credential-bearing capabilities without separate approval.
6. The planned fixed Terra-medium capability probes are canceled and recorded
   as `UNTESTED` after the read-only runner failed before inference. Do not
   retry them or substitute a weaker-isolation run.
7. Reconcile deterministic runtime observations with source and documentation
   without another capability-discovery model session.
8. Freeze the exact tool surface used later in controlled Pi/Codex arms and record any capability intentionally excluded.

Capability-discovery model tokens, tool calls, and smoke-test outputs are measured separately and excluded from the controlled source-only versus graph-assisted experiment. “Full discovery” does not justify unsafe execution or installing every optional backend.

The capability matrix records, at minimum:

- public name and surface (`CLI`, `MCP tool`, `MCP resource`, or configuration);
- purpose, inputs, outputs, schema size, and prerequisites;
- supported languages/file types and graph entity/edge types where relevant;
- read/write/network/credential effects;
- documentation, source-registration, and runtime evidence;
- fixture result, Pi/Codex applicability hypothesis, limitations, and final disposition;
- setup time, query time, output tokens/bytes, and model tokens when applicable.

### 8.2 CodeGraph

- Build or copy the CLI inside the disposable CodeGraph tool clone; do not install globally or write into the live tool submodule.
- Disable or redirect telemetry and home-directory writes.
- Enumerate every public CLI command and the complete runtime MCP tool list before selecting the experiment surface.
- Initialize one isolated subject clone and record index statistics.
- Use `explore` for architecture and flow questions.
- Use `node`, `query`, `callers`, `callees`, and `impact` when they add discriminating evidence.
- Record verbatim-source coverage, symbol resolution, path quality, blast-radius usefulness, stale-index behavior, and output size.
- In the MCP measurement, expose only the normal listed tool surface unless the run explicitly measures the expanded set.

### 8.3 CBM

- Build or provision the binary inside the disposable CBM tool clone without global installation.
- Give each run a dedicated `CBM_CACHE_DIR`.
- Capture all fourteen advertised tools from the disposable runtime and reconcile them with `tools/list` and the source registry.
- Verify the indexed project root before trusting any result.
- Run `get_graph_schema` first, then `get_architecture`.
- Use `search_graph`, `trace_path`, `query_graph`, `get_code_snippet`, and `search_code` according to the question.
- Use the qualified-name workflow rather than guessing identifiers.
- Record hybrid-LSP behavior, call-path quality, name-collision behavior, language/idiom sensitivity, schema overhead, and any git-root bleed.
- Keep the primary comparison read-only; a synthetic diff for `detect_changes` may be created only in a disposable clone and measured separately.

### 8.4 Graphify

- Create or reuse a virtual environment inside the disposable Graphify tool clone with explicit tool-local cache and state paths; do not modify the live Graphify submodule.
- Set telemetry off and run the code-only AST path without an LLM backend.
- Capture the full CLI dispatcher, runtime MCP tools/resources, optional extras, and backend prerequisites before selecting the offline experiment surface.
- Direct all artifacts to an explicit writable output directory.
- Use extraction, clustering/report generation, `query`, `explain`, `path`, and impact/affected operations where supported.
- Prefer stable node IDs over ambiguous labels.
- Audit the manifest against the source file list, including known filename-filter risks.
- Record extracted/inferred/ambiguous edge counts, skipped files, community usefulness, query precision, output size, and zero-token claims.
- Do not run incremental update against the live subject.

## 9. Token and Resource Accounting

“Token usage” will be reported as separate quantities, not one ambiguous total.

### 9.1 Index/build cost

- wall-clock time;
- peak resident memory where measurable;
- index/output disk size;
- number of indexed and skipped files;
- tool-reported LLM input/output tokens;
- whether the path was fully offline.

Static AST work may use zero model tokens while still consuming significant CPU, memory, and disk. The report will say “zero model tokens,” not “free.”

### 9.2 Tool-surface overhead

- serialized MCP tool-schema tokens in a fresh session;
- number of exposed tools;
- initialization instructions injected into context;
- whether schemas are cached or repeatedly charged.

CLI-only runs have no MCP schema charge and will be labeled separately.

### 9.3 Per-query cost

- raw tool-output bytes and tokens;
- result tokens actually placed into model context;
- number of graph calls;
- fallback searches and file reads;
- elapsed time to a usable answer.

### 9.4 End-to-end agent cost

For the primary-lifecycle tracer, use one fresh session with
`gpt-5.6-terra` at `medium` for the source-only baseline and each of the three
graph-assisted arms. Pin the same observable model build, CLI/runtime version,
configuration, prompt, output contract, and repository commit:

- input tokens;
- cached input tokens, when exposed;
- output tokens;
- reasoning tokens, when exposed;
- tool calls;
- file reads;
- elapsed time;
- repair-pass tokens;
- final quality result.

Run the source-only baseline and all three graph-assisted arms once using the
same contract, in a deterministically recorded shuffled order. Do not run
automatic replicates. Report individual observations and explicitly label the
four-arm result a tracer case study, not a statistically generalizable saving.

The remaining questions are offline capability and learning case studies.
Their parser/query bytes, local tokens, wall time, and resource use may be
measured, but they do not receive provider-token comparisons unless the user
separately promotes a specific question after reviewing the tracer.

Compare each graph-assisted arm against the source-only baseline only after blinded quality review. Graph-only capability runs are reported separately.

Phase 0 will also pin the tokenizer used to count serialized schemas and raw outputs. Provider-reported session usage remains authoritative for billed/context usage; local tokenization is a reproducible estimate for artifacts the provider does not itemize.

If a token field is not exposed, record `UNKNOWN`; do not infer it as zero. Never add or subtract provider-reported usage and local-tokenizer estimates in the same derived total. Report them in separate columns with their measurement source.

### 9.5 Derived measures

- tokens to first passing answer;
- percentage token change versus baseline;
- file-read reduction;
- tool-call reduction;
- setup cost amortization after 1, 5, and 20 representative questions;
- useful verified facts per 1,000 context tokens;
- unsupported or incorrect claims per answer.

No vendor token-saving claim will be repeated as an experimental result unless reproduced here.

## 10. Answer Quality and Tool Helpfulness

Before runs, create a scoring key for each question from the reference lane. A blinded reviewer will see normalized answers labeled A/B/C/D, not tool names.

Each answer is judged on:

- factual precision;
- required-fact coverage;
- source-citation correctness;
- causal/mechanistic explanation;
- handling of uncertainty;
- usefulness for building the learner's mental model.

Each dimension is scored `0` (fails), `1` (partial), or `2` (meets). A passing answer must:

- score `2` for factual precision and source-citation correctness;
- contain no fabricated source, critical contradiction, or unsafe operational claim;
- cover every mandatory fact in the frozen scoring key;
- score at least `10/12` overall.

An answer within one point of the threshold, or disputed by the first reviewer, receives a second blinded review and a written adjudication. A valid extra fact absent from the scoring key can earn credit only after the reference curator verifies it in source; novelty is not penalized merely because the original key missed it.

The qualitative synthesis will also ask:

- Did the tool reveal a relationship ordinary file reading was unlikely to find quickly?
- Did it return enough source evidence to verify its claim?
- Did it create a misleading sense of certainty?
- Did it help choose the next source file or question?
- Was its graph useful to a human, an agent, or both?
- Which failure modes must a future user actively guard against?

Model routing is part of methodology, not a hidden implementation detail. Quality scoring must report any promotion from the Section 3.2 assignment, why it happened, and whether the promoted run replaced or supplemented the original.

## 11. Teaching Protocol

The repo-local `$teach` skill has been extended for unfamiliar codebases. It preserves the existing multi-session workspace, retrieval practice, and learning records while adding:

- source-fact/inference/open-question separation;
- a codebase learning map;
- a Feynman teach-back loop;
- one-at-a-time Socratic probes;
- transfer questions and counterfactuals;
- evidence-based mastery gates;
- misconception history and spaced retrieval.

### Per-lesson loop

1. Ask the learner to retrieve the relevant prior model.
2. Present one small source-backed mechanism.
3. Explain it in plain language.
4. Ask the learner to teach it back as if to a capable newcomer.
5. Identify the first vague link or hidden assumption.
6. Ask one Socratic question that repairs that link.
7. Test transfer with a changed condition, failure, or design alternative.
8. Record learning only after demonstrated understanding.

### Pi learning gate before Codex

The learner must be able to:

- explain Pi's system boundary, major subsystem responsibilities, and dependency direction;
- trace a real agent turn through model and tool interactions;
- explain session, state, identity, persistence, context, and resume behavior;
- identify control/data flow, extension points, trust, and permission boundaries;
- explain cancellation, failure, recovery, observability, and operating behavior;
- predict the effect of one representative change, load condition, or failure;
- cite or locate the source evidence for the important claims;
- name what remains uncertain.

This is not a numeric quiz threshold. Passing requires an unprompted explanation, a source-grounded trace, and a transfer answer. If the gate is not met, the next action is a targeted Pi lesson, not starting Codex.

Codex will use the same gate at a finer-grained module level and then at repository level.

## 12. Durable Artifact Layout

### Canonical architecture research

```text
docs/research/coding-agents/pi/agent/
  00-index.md
  01-core-architecture.md
  02-runtime-lifecycle.md
  03-data-state-and-persistence.md
  04-integration-and-extension-points.md
  05-operational-model.md
  90-open-questions.md

docs/research/coding-agents/codex/agent/
  ...same report set...
```

These files contain source-grounded project facts, not learner progress or tool marketing.

Each core report should include only the diagrams needed to communicate the system: normally one component/dependency map, one primary sequence trace, and one state or failure-transition diagram. Diagrams summarize verified evidence; they do not replace source citations.

### Tool experiments

```text
docs/research/harness-tools/codebase-intelligence/experiments/coding-agents/
  methodology.md
  capabilities/
    methodology.md
    codegraph.md
    cbm.md
    graphify.md
    capability-matrix.csv
    experiment-surface-freeze.md
  pi/
    reference-ledger.md
    codegraph.md
    cbm.md
    graphify.md
    synthesis.md
    token-usage.csv
  codex/
    ...same set...
  cross-repo-synthesis.md
```

### Teaching workspace

```text
docs/learning/coding-agents/
  MISSION.md
  RESOURCES.md
  GLOSSARY.md
  NOTES.md
  lessons/
  reference/
  learning-records/
```

Canonical source findings stay in `docs/research`; learner-specific understanding stays in `docs/learning`.

### Uncommitted experiment data

```text
scratchpad/code-intelligence/
  subjects/
    pi/
      reference/
      source-only/
      codegraph/
      cbm/
      graphify/
    codex/
      ...created only after the Pi learning gate...
  tools/
    codegraph/
    cbm/
    graphify/
  indexes/
  raw-output/
    capability-discovery/
  sessions/
  metrics/
```

Large graph databases, raw event streams, copied repositories, and generated visualizations remain under `scratchpad/` unless the user later selects a small artifact for preservation.

## 13. Execution Phases and Gates

### Phase 0 — Readiness and protocol freeze

#### Phase 0A — Runtime and isolation readiness

- Re-record full SHAs and clean state.
- Verify local tool versions, build paths, and runtime prerequisites.
- Revalidate the live Sol/Terra/Luna model and effort catalog, record current pricing, and pin the Section 3.2 routing matrix.
- Pin Terra medium for every controlled comparison arm, along with runtime configuration and the artifact tokenizer.
- Create disposable tool clones; build CBM and create other tool environments only inside those clones.
- Create Pi subject clones and tool-local homes/caches. Do not create, inspect, or index Codex subject clones yet.
- Strip model credentials, Git credentials, and unrelated MCP configuration from tool subprocess environments.

#### Phase 0B — Bounded tool-capability completion

- Execute the Section 8.1 discovery protocol using recursive CLI help, live MCP discovery, source registries, tests/docs, and disposable runtime probes.
- Produce the four capability reports, matrix, and experiment-surface freeze listed in Section 12.
- Apply the strict orchestration policy in Section 3.3. Use no additional model
  session for Phase 0B; build the matrix mechanically from the frozen reports.
- Treat the current deterministic evidence as the boundary. Resolve only safety, reproducibility, evidence-stability, and comparison-fairness blockers; inventory all other gaps without expanding the probe surface.
- Record capability-discovery setup, schema, query, output, and model costs separately from the controlled experiment.
- Freeze the normal public interface and enabled tool list each later experimental arm will receive.

#### Phase 0C — Pi experiment protocol freeze

- Freeze the Pi question battery, tracer prompt templates, allowed tools,
  one-turn output contract, zero-replicate policy, recorded arm order, metric
  schema, contamination rules, and setup-failure handling.
- Freeze concrete Pi source anchors and scoring keys during the Pi systems-reference task before any tool runner sees them.
- Validate all four runner configurations deterministically without a model.
  The first four measured tracer arms are the only initial provider sessions.

**Gate:** the current reports give every inventoried public capability a
truthful disposition; unresolved breadth is explicitly marked rather than
probed further; the shared fixture and runner pass deterministic checks; the
canceled agent-mediated capability probes remain `UNTESTED` and excluded; the
exact later experiment surfaces are frozen in the cross-tool matrix; all
three tools run against disposable Pi clones without touching any live
submodule or real home/cache; every measured-run control is frozen; tool and
subject clones remain clean except for declared build/index artifacts; and no
paid smoke or automatic retry is required.

### Phase 1 — Pi tracer bullet

- Build a narrow source-first trace of Pi's primary agent-turn lifecycle.
- Run all three tools independently on that same lifecycle question.
- Reconcile their claims against source.
- Measure the first controlled token comparison.
- Deliver one teaching lesson and run the full teach-back loop.

**Gate:** methodology works end to end, metrics are collectible, and the user agrees the lesson format is effective.

### Phase 2 — Pi full understanding

- Complete the Pi reference report set.
- Run the remaining questions as offline per-tool case studies and
  source-grounded learning traces.
- Produce per-tool Pi reports, offline resource metrics, and the tracer's
  provider-token metrics.
- Request approval before promoting any additional question to a four-arm
  provider comparison.
- Synthesize what each tool contributed or distorted.
- Teach Pi in small modules with retrieval and transfer checks.

**Gate:** the Pi learning gate in Section 11 passes.

### Phase 3 — Codex tracer bullet

- Create fresh Codex subject clones at the frozen commit only after the Pi learning gate.
- Adapt anchors to Codex's Rust workspace and event-driven architecture.
- Build a narrow source-first turn/tool-execution trace.
- Run all three tools independently.
- Check whether the Pi methodology transfers or needs revision.
- Deliver the first Codex lesson.

**Gate:** method remains fair for Rust and the Codex repository's larger scale.

### Phase 4 — Codex full understanding

- Complete the Codex reference report set.
- Run the remaining tool experiments and controlled comparisons.
- Teach Codex in smaller subsystem modules.
- Run module-level and repository-level mastery gates.

**Gate:** the learner can explain and trace Codex with explicit uncertainty.

### Phase 5 — Cross-repository synthesis

- Compare Pi and Codex architectural choices without flattening their different goals.
- Compare tool behavior across TypeScript and Rust.
- Calculate token/resource results and amortization.
- Produce “use this tool when / guard against this failure” guidance.
- Run a spaced retrieval and transfer review across both repositories.

**Gate:** every recommendation traces to experiment evidence, and vendor claims remain clearly separated.

## 14. Beads Execution Structure

The approved execution is tracked by epic `orch-8sk`. Its current direct children are:

1. `orch-8sk.1` — Finalize approved systems-level plan and model routing.
2. `orch-8sk.2` — Verify isolated tool runtimes and model readiness.
3. `orch-8sk.3` — Build Pi tracer reference and scoring anchor.
4. `orch-8sk.4` — Run remaining Pi CodeGraph offline case studies.
5. `orch-8sk.5` — Run remaining Pi CBM offline case studies.
6. `orch-8sk.6` — Run remaining Pi Graphify offline case studies.
7. `orch-8sk.7` — Synthesize Pi systems results and token accounting.
8. `orch-8sk.8` — Teach and review Pi to systems mastery gate.
9. `orch-8sk.9` — Build Codex tracer reference and scoring anchor.
10. `orch-8sk.10` — Run remaining Codex CodeGraph offline case studies.
11. `orch-8sk.11` — Run remaining Codex CBM offline case studies.
12. `orch-8sk.12` — Run remaining Codex Graphify offline case studies.
13. `orch-8sk.13` — Synthesize Codex systems results and token accounting.
14. `orch-8sk.14` — Teach and review Codex to systems mastery gate.
15. `orch-8sk.15` — Produce cross-repository and cross-tool systems synthesis.
16. `orch-8sk.16` — Discover and validate code-graph tool capabilities.
17. `orch-8sk.17` — Freeze Pi experiment protocol and runner surfaces.
18. `orch-8sk.18` — Run Pi tracer bullet and approve lesson format.
19. `orch-8sk.19` — Retired remaining Pi source-only session grid.
20. `orch-8sk.20` — Run Codex tracer bullet and approve method transfer.
21. `orch-8sk.21` — Retired remaining Codex source-only session grid.
22. `orch-8sk.22` — Run cross-repository spaced retrieval and transfer review.
23. `orch-8sk.23` — Verify complete study against approved plan.
24. `orch-8sk.24` — Complete Pi systems reference map after tracer gate.
25. `orch-8sk.25` — Complete Codex systems reference map after tracer gate.
26. `orch-8sk.26` — Reconcile approved plan with audited Beads execution graph.
27. `orch-8sk.27` — Audit unauthorized checkpoint commit and preserve recovery options.
28. `orch-8sk.28` — Stop reviewer token explosion and enforce model budget guardrails.

Capability discovery is tracked as nested epic `orch-8sk.16`:

1. `orch-8sk.16.1` — Define capability-discovery protocol and model routing.
2. `orch-8sk.16.2` — Discover and validate CodeGraph capabilities.
3. `orch-8sk.16.3` — Discover and validate CBM capabilities.
4. `orch-8sk.16.4` — Discover and validate Graphify capabilities.
5. `orch-8sk.16.5` — Produce cross-tool capability matrix and freeze experiment surfaces.
6. `orch-8sk.16.6` — Freeze capability fixture and agent probe battery.
7. `orch-8sk.16.7` — Repair provider-compatible capped Terra probe runner.
8. `orch-8sk.16.8` — Repair shared capability fixture freeze regression.

`orch-8sk.1` and `orch-8sk.2` are the completed Phase 0A prerequisites. Phase 0B starts with the discovery protocol (`orch-8sk.16.1`) and the shared fixture/probe battery (`orch-8sk.16.6`). The fixture-freeze repair (`orch-8sk.16.8`) and provider-compatible capped Terra runner repair (`orch-8sk.16.7`) must restore the common probe foundation before the three per-tool discovery tasks (`orch-8sk.16.2`–`.16.4`) complete. Their capability matrix (`orch-8sk.16.5`) then gates Phase 0C's Pi protocol and runner-surface freeze (`orch-8sk.17`).

The authoritative subject sequence is: Phase 0B → Phase 0C → Pi tracer reference
(`orch-8sk.3`) → one four-arm Pi tracer and interactive lesson-format gate
(`orch-8sk.18`) → post-tracer Pi reference (`orch-8sk.24`) plus the three
offline tool lanes (`orch-8sk.4`, `.5`, `.6`) → Pi synthesis (`orch-8sk.7`) →
Pi mastery (`orch-8sk.8`) → Codex tracer reference (`orch-8sk.9`) → one
four-arm Codex tracer and interactive method-transfer gate (`orch-8sk.20`) →
post-tracer Codex reference (`orch-8sk.25`) plus the three offline tool lanes
(`orch-8sk.10`, `.11`, `.12`) → Codex synthesis (`orch-8sk.13`) → Codex
mastery (`orch-8sk.14`) → cross-repository synthesis (`orch-8sk.15`) → spaced
retrieval and transfer review (`orch-8sk.22`) → final audit (`orch-8sk.23`).
The retired source-only grids (`orch-8sk.19`, `.21`) are not execution
requirements. The final audit is gated by the spaced review (`orch-8sk.22`),
this plan/graph reconciliation (`orch-8sk.26`), and the checkpoint audit
(`orch-8sk.27`).

`orch-8sk.27` is an operational recovery and audit task only. It preserves non-destructive recovery options for an unauthorized checkpoint commit and does not alter the study's scientific method, model routing, controlled comparisons, or learning gates.

`orch-8sk.28` records the excessive reviewer usage and the user-approved strict
orchestration policy in Section 3.3. Its bounded Phase 0B gate supersedes the
earlier exhaustive execution interpretation but preserves truthful capability
dispositions and controlled-comparison fairness.

There are explicit user-interaction pauses at the Pi tracer gate: the learner must complete teach-back/transfer and approve or revise the lesson format before the post-tracer Pi work begins. There is a second explicit user-interaction pause at the Codex tracer gate: the learner must complete teach-back/transfer and accept or request correction to the method before the post-tracer Codex work begins. The spaced review is also interactive; unresolved misconceptions create targeted follow-up lessons rather than being silently passed.

The three offline per-tool case-study tasks for each repository can run
independently only after that repository's post-tracer reference anchors and
scoring keys are frozen. Teaching depends on validated synthesis, not raw tool
output. Codex subject indexing or analysis remains prohibited until the Pi
mastery gate passes.

This task graph records the approved work; it does not by itself authorize paid services, upstream changes, or a push.

## 15. Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| Documentation overstates the runtime surface | Reconcile recursive help and live MCP discovery with source registries; use runtime dispositions rather than marketing claims. |
| “Full capability” becomes unsafe scope expansion | Inventory restricted and optional capabilities, but execute only safe offline operations without separate approval. |
| Capability probing contaminates the tracer | Use separate fixture clones, sessions, logs, and accounting; deterministic preflight and offline case studies remain outside the four measured tracer sessions. |
| Tool output biases the reference truth | Complete source anchors and scoring key before exposing tool outputs to synthesis. |
| One tool contaminates another's index or cache | Separate clones, homes, caches, indexes, sessions, and raw-output directories. |
| CBM indexes the parent repo | Require an independent `.git` per clone and verify CBM's project root. |
| Graphify silently skips files | Compare manifest to tracked source list and probe known filename-filter patterns. |
| Same-name symbols inflate apparent graph quality | Preselect a collision/disambiguation anchor and verify binding against source. |
| Dynamic dispatch or UI/event callbacks disappear | Include lifecycle anchors that cross callback/event boundaries and measure omissions. |
| Tool schemas dominate token cost | Measure fresh-session schema overhead separately from query output. |
| Short answers look efficient but are incomplete | Compare only at equal answer quality; retain failures, and run a repair only after explicit approval. |
| Repeated questions leak cached knowledge | Use fresh sessions and separate runner contexts; record cached-token fields. |
| Codex's size causes shallow coverage | Use tracer bullets and subsystem gates rather than exhaustive file inventories. |
| Learner fluency is mistaken for mastery | Require teach-back, source trace, counterfactual prediction, and spaced retrieval. |
| Upstream revisions drift during a long study | Freeze SHAs; update only in a later explicitly approved refresh. |
| Raw artifacts bloat the parent repository | Keep them in `scratchpad/`; preserve only concise evidence and metrics. |

## 16. Verification and Completion Criteria

### Plan and skill verification

- Validate the `$teach` skill structure.
- Check the plan for unresolved placeholders and path consistency.
- Check the capability epic/task IDs and dependency graph against live Beads state.
- Run documentation whitespace checks.
- Export the Beads mirror.
- Inspect `git status` and report pre-existing changes separately.

### Experiment completion

The Pi/Codex study is complete only when:

- both canonical report sets are source-cited and revision-pinned;
- all three capability inventories and the cross-tool matrix are source- and runtime-grounded, with every public capability assigned a disposition;
- all six offline tool case-study lanes have reproducible runbooks and
  isolation audits;
- each repository's single four-arm tracer includes a no-graph baseline,
  equal-quality judgment, and provider-token accounting;
- limitations and failed queries are recorded, not hidden;
- the learner passes the Pi and Codex mastery gates;
- the cross-tool recommendation distinguishes human learning value from agent retrieval value;
- all experiment Beads issues are closed with evidence;
- no upstream submodule internals were changed.

## 17. Approved Decisions

Approved defaults:

1. Approve Markdown-first canonical research and teaching artifacts; do not generate HTML by default.
2. Keep Graphify's primary comparison code-only/offline; consider semantic labeling only as a separately approved secondary experiment.
3. Enforce the Pi mastery gate before beginning Codex.
4. Use the Section 3.2 model routing, with Terra medium fixed across controlled experimental arms.
5. Track execution under Beads epic `orch-8sk`.
6. Complete nested capability-discovery epic `orch-8sk.16` before Pi source-reference work, executing safe offline capabilities and inventorying restricted ones.
7. Use the Section 3.4 lean tracer-first design: offline parser evaluation by
   default, one four-arm one-turn tracer per repository, no paid smoke,
   automatic repair, or replication, and explicit approval before any
   additional provider session.

User approval of this plan authorizes planning/tracking setup and the local read-only experiment workflow. The current request separately authorizes committing the preparation changes. It does not authorize pushes, submodule updates beyond the already prepared additions, paid API use, or upstream edits.
