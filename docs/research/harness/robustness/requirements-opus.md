# Requirements for Understanding a Codebase — A First-Principles Catalogue

**Purpose.** A tool-agnostic, exhaustive catalogue of what it actually takes to *understand* and *safely
change* a large, unfamiliar, real-world codebase — for **both** a human developer and an AI coding agent.
This is a requirements analysis, not a tool review. Each requirement has a one-line definition, a rationale,
an explicit human-vs-agent split, and a **concrete objective test** (question + ground-truth method + metric)
so the catalogue can grade *any* method or capability — grep, an LSP, a graph indexer, a RAG store, an agent
harness, or a human with an IDE.

**Method.** Derived from the actual cognitive and operational tasks a newcomer must complete to become
productive. The taxonomy is the *task*, not any tool's feature list. Where a requirement maps onto the
existing symbol-navigation scenario battery (`scenarios.md`), it is noted, but the battery covers only one
tier (B) of twelve dimensions here.

**Touchstone.** Concrete tests reference the TypeScript pnpm monorepo at
`scratchpad/harness/_paperclip_src` (~2,961 files, ~38 workspace packages, server + ui + cli + db + adapters,
106 SQL migrations, 739 test files, Docker, CI under `.github/workflows/`). Requirements stay general; the
touchstone only makes the tests executable. **Caveat:** this snapshot is pruned of `.git`, so history tests
(Dimension J) must be run against the live repo (`external/paperclip`), not the snapshot.

---

## 0. The frame: what "understanding" decomposes into

A person or agent dropped into an unfamiliar codebase is trying to answer, in rough order of escalating depth:

1. **Where am I?** — shape, scale, entry points, where things live. (Dimension A)
2. **Where is X, and what touches it?** — locate and trace symbols/usages. (Dimension B)
3. **How does control and data flow?** — execution paths end-to-end. (Dimension C)
4. **What does it mean and why does it exist?** — domain intent, naming, rationale. (Dimension D)
5. **How is data modeled and how does it move?** — schemas, persistence, serialization. (Dimension E)
6. **What does it actually do at runtime?** — observed behavior, state, timing, concurrency. (Dimension F)
7. **What must stay true?** — contracts, invariants, types, error behavior. (Dimension G)
8. **How do I build / run / test / debug it?** — the operational loop. (Dimension H)
9. **What does it depend on and where are the edges?** — config, env, external boundaries. (Dimension I)
10. **How did it get this way and how does it change?** — history, ownership, conventions. (Dimension J)
11. **Who owns it and how do people work here?** — human/organizational context. (Dimension K)
12. **How cheaply can I get a *correct* answer?** — efficiency, trust, freshness. (Dimension L)

Two orthogonal **cross-cutting properties** apply to every requirement and are graded separately:
**Trust/grounding** (is the answer verifiable, or a confident guess?) and **Freshness** (does it reflect
the current tree, or a stale index?). These are pulled out in §13 because they make or break agents specifically.

A requirement counts as *satisfied* by a method only if it returns a **correct, grounded, current** answer
at a **cost proportional to the question** — not if it merely *can* surface raw material a human then reads.

---

## Dimension A — Orientation & Topology (Where am I? Where do things live?)

### A1. Scale & composition census
**Def.** Get the size, language mix, and gross composition of the repo (file/line counts by language, by
top-level area, generated vs hand-written, vendored vs first-party).
**Why.** First triage decision: what is worth reading, what to exclude, where the mass is. You cannot plan
an exploration budget without knowing the terrain size. (Touchstone: `packages/db` is ~77% of package tokens
— almost all generated migration snapshots; knowing this *before* reading saves the whole budget.)
**Human vs agent.** A human eyeballs the tree and `cloc` output once and internalizes it. An agent needs it
as a *cheap, structured, machine-readable* fact up front, because every file it blindly reads costs tokens and
context; the census is what lets it *not* read 77% of the bytes.
**Objective test.** Q: "Give file count and primary language per top-level dir, and name the single directory
holding the largest share of tokens." Gold: `find`/`cloc` + a tokenizer over `_paperclip_src` (db dominates).
Metric: correct ranking of the top-3 token-heavy dirs (exact set match), and language-per-dir accuracy ≥ 90%.

### A2. Entry-point inventory
**Def.** Enumerate every way the system is *started* or *invoked*: process main(s), CLI command registrations,
server bootstrap, HTTP/route roots, background workers, scheduled jobs, build/release scripts.
**Why.** Entry points are the roots of every behavior trace (Dimension C) and the anchors for "what does
running this *do*." Missing one means an entire subsystem is invisible.
**Human vs agent.** Humans find entrypoints from the README's "quickstart" and `package.json` scripts. An
agent must derive them mechanically (manifest `bin`/`scripts`, server `listen`, CLI `register*` calls) because
it cannot rely on a human's prior framework knowledge of "where main usually is."
**Objective test.** Q: "List every process entry point and CLI command registrar." Gold: `package.json`
`scripts` + `bin`, `server/src/index.ts:startServer`, `cli/src/.../register*` registrars (e.g.
`registerRunCommands @ cli/src/commands/client/run.ts:46`). Metric: recall of the curated entrypoint set;
penalize any missed registrar class. (Overlaps battery scenario 8.)

### A3. Where-does-X-live (locate by concept/feature)
**Def.** Given a *feature or concept name* ("issue references", "heartbeat", "auth", "storage"), find the
file(s)/package(s) that implement it — not just a literal symbol.
**Why.** The most frequent real task is "I need to change behavior X"; step zero is locating X from a fuzzy
human description, not an exact identifier.
**Human vs agent.** Humans use fuzzy filename intuition + search; tolerate several wrong opens. An agent needs
high top-k precision because each wrong file opened is wasted context; concept→file mapping (vs symbol→file)
is where pure text search degrades.
**Objective test.** Q: "Which package/file implements issue-reference extraction?" Gold:
`packages/shared/src/issue-references.ts` (`extractIssueReferenceMatches`, `buildIssueReferenceHref`).
Metric: is the correct file in top-3 results for a *concept* query (not the exact symbol)? Report MRR over a
set of 10 concept→file pairs drawn from the anchor list.

### A4. Mental-model / architecture map
**Def.** Produce the module/package dependency graph: components, their responsibilities, the edges between
them, layering, and cycles.
**Why.** This is the "map of the city." It tells you what depends on what, where the hubs are, what is safe to
touch, and where a change will ripple. Cycles flag fragility.
**Human vs agent.** A human benefits from a *visual* weighted graph and remembers it. An agent benefits from
the same graph as queryable edges (`server→db`, `ui→shared`), with hub/God-node and cycle annotations, so it
can reason about blast radius without re-deriving the graph each turn.
**Objective test.** Q: "Give the package import graph with edge directions and any import cycles." Gold:
parse all `package.json` workspace deps + resolved imports → the ~38-package edge map; known cycles in
`server/src/services/plugin-{lifecycle,loader,tool-dispatcher}.ts` and `adapter-utils`. Metric: edge
precision/recall against the declared-dependency graph + cycle-set exact match. (Battery scenario 10.)

### A5. Naming & layout conventions
**Def.** Infer the project's organizing conventions: directory semantics, file-naming patterns, where tests
live relative to source, barrel/`index` re-export idiom, package boundaries.
**Why.** Once you know the convention, you can *predict* where anything is without searching — the single
biggest multiplier on navigation speed. Violating a convention in a change is a code-review failure.
**Human vs agent.** Humans absorb conventions implicitly after a few files. An agent should be told them
explicitly (or infer and state them) so its *new* code matches and its *search* is convention-guided rather
than brute-force.
**Objective test.** Q: "Where would a new shared utility and its test go, and how is it exported to other
packages?" Gold: `packages/shared/src/<name>.ts`, co-located `<name>.test.ts`, re-exported via the package
barrel (`index.ts`), consumed as `@paperclipai/shared`. Metric: convention statement matches the dominant
observed pattern (verify by sampling 20 real files).

---

## Dimension B — Symbol-Level Navigation (Where is X used? What is this?)

*(This dimension is the existing scenario battery's home turf; B1–B7 map to its scenarios. Listed for
completeness and because they are the highest-frequency micro-tasks.)*

### B1. Go-to-definition (resolve a use to its def)
**Def.** From a use site, find the exact defining `file:line`, through aliases, barrels, type-only imports,
and workspace packages.
**Why.** The atomic comprehension step: "what is this thing?" Everything else builds on it.
**Human vs agent.** Human: one keystroke in an IDE, tolerates a wrong jump. Agent: needs exact `file:line`
to read the right span and *only* that span; ambiguity wastes a turn.
**Objective test.** Q: "Definition of `CatalogTeam` as imported at use site U." Gold: must distinguish
`packages/shared/.../teams-catalog.ts:76` from the same-named `packages/teams-catalog/src/types.ts:67`.
Metric: exact `file:line`; partial credit for right file/wrong symbol. (Battery scenario 3, anchors A12/A13.)

### B2. Find-all-references / find-usages (semantic, not textual)
**Def.** All *binding-correct* uses of a symbol, excluding shadows, same-name collisions, comments, and
unrelated locals.
**Why.** Required before any rename, signature change, or deletion. Textual matches over- and under-count
(barrel re-exports, JSX, name collisions) and produce unsafe changes.
**Human vs agent.** Human cross-checks a noisy grep list by eye. Agent must trust the set: a false negative
→ a missed call site → a runtime break; a false positive → wasted edits. Precision *and* recall both matter.
**Objective test.** Q: "All callers of the shared `isUuidLike`, resolving the `workspace:*` alias and the
barrel re-export, excluding the two cli-local shadow copies." Gold: 16 files (11 server + 5 ui), computed by
ripgrep-seed + manual classification. Metric: precision/recall vs the labeled gold; bucket by JSX vs
non-JSX. (Battery scenarios 1, 2, 6; this is the empirically hardest axis — see `findings.md` §4.)

### B3. Caller graph (who calls this?)
**Def.** Direct and N-hop callers of a function/hook/component, including JSX instantiation and
factory-returned method calls (`factory(db).method()`).
**Why.** "If I change this, who breaks?" starts here. JSX and factory-method patterns are the recall frontier.
**Human/agent split.** As B2. Agents especially need JSX/component-body calls (often missed by static graphs)
because they cannot visually scan the component to confirm.
**Objective test.** Q: "Callers of `usePaperclipIssueRuntime` (a React hook called inside component bodies)."
Gold: enumerated component-body call sites. Metric: caller F1 + missed-call category. (Battery scenario 2,
anchor A19.)

### B4. Symbol disambiguation (same name, different thing)
**Def.** Split occurrences of a colliding name and attribute each to its owning definition.
**Why.** Conflating shadows produces wrong impact analysis and wrong edits (the `isUuidLike` 3-def case:
cli "consumers" call their *own* copy; changing the shared def would not affect cli).
**Human/agent split.** Humans usually notice "wait, there are two of these." Agents silently merge unless the
method binds — a top source of confident-but-wrong agent reasoning.
**Objective test.** Q: "How many distinct definitions of `execute` are reachable, and which call sites bind to
which?" Gold: the many sibling adapter `execute` defs (anchor A16) labeled by owning module. Metric:
false-positive rate by collision bucket. (Battery scenario 6.)

### B5. Cross-package / barrel resolution
**Def.** Resolve an import through workspace aliases (`workspace:*`) and `index.ts` barrel re-export hops to
the leaf definition, and back.
**Why.** In a monorepo the *public API* is entirely barrel-exported; a method blind to barrels is blind to the
real consumers of every shared symbol (the empirically decisive monorepo signal).
**Human/agent split.** Both need it; agents more so, because they cannot manually "open the index and follow
the hop" cheaply at scale.
**Objective test.** Q: "Trace `@paperclipai/shared` → barrel → `extractIssueReferenceMatches` def, and list
re-export hops." Gold: manifest + barrel chain. Metric: hop recall + path completeness. (Battery scenarios
4, 5, anchors A9/A10.)

### B6. Blast radius / change impact (transitive)
**Def.** The 1st/2nd/N-order set of files affected by changing a symbol, tiered by hop distance.
**Why.** The core safety question. Determines test scope and review scope.
**Human/agent split.** Human eyeballs direct callers and guesses transitive. Agent needs an explicit tiered
set to bound *which tests to run* and *what to re-read* — and must not under-count (false confidence) or
over-count (wasted work).
**Objective test.** Q: "Files affected at depth 1 and depth 3 by changing the shared `isUuidLike` signature."
Gold: curated 1st/2nd-order affected files. Metric: recall by hop + precision; penalize missing critical nodes.
(Battery scenario 7.)

### B7. Type / interface impact
**Def.** All type-level uses of an interface/type: annotations, `satisfies`, implementing object literals,
type-only imports, exported-API surface.
**Why.** Type changes ripple differently from call changes; type-only imports are erased at runtime and missed
by call-graph-only methods, yet a breaking type change fails the build everywhere.
**Human/agent split.** Both rely on the type checker; agents need the *set* without running a full build per
hypothesis.
**Objective test.** Q: "Everything affected by changing `ServerAdapterModule` (a type-only contract,
implemented by object literals)." Gold: type imports/annotations/impls (anchor A14). Metric: typed-use recall.
(Battery scenario 9.)

### B8. Structural pattern sweep
**Def.** Enumerate all instances of a syntactic shape: route registrations, DB table decls, `forwardRef`
components, hooks, adapter `execute` defs, decorators.
**Why.** Inventory questions ("how many routes? where are all the tables?") and codemod targeting. The native
strength of AST search.
**Human/agent split.** Both want exact counts; agents use the inventory as a checklist to avoid missing a case.
**Objective test.** Q: "Count and locate all route registrations and all Drizzle table decls." Gold: AST/manual
list (e.g. ~412 route registrations; tables under `packages/db/src/schema/`). Metric: exact count + location
set. (Battery scenario 11.)

---

## Dimension C — Control & Data Flow (How does it actually work, end-to-end?)

### C1. Entry-to-behavior trace
**Def.** Follow an ordered execution path from an entry point to a specific observable behavior, across
function/module/package boundaries (the *lifecycle*, not one symbol).
**Why.** This is "how does a request actually get handled" — the difference between knowing the parts and
knowing the machine. Required to place a change correctly in the flow.
**Human/agent split.** A human steps through with a debugger or reads top-down. An agent needs the *ordered
path segments* as data so it can reason about where in the flow to intervene without 20 file reads.
**Objective test.** Q: "Trace from `startServer` to where an issue-reference mention gets persisted." Gold:
ordered path segments (entry → route → service → db write). Metric: path edit-distance to the gold ordered
list + count of missing *critical* nodes. (Battery scenario 8, anchor A1.)

### C2. Data-flow / taint trace (where does this value come from / go to?)
**Def.** For a given value (a request field, a config value, a secret), trace its provenance backward and its
propagation forward through transforms, stores, and outputs.
**Why.** Essential for correctness ("is this validated before use?"), security ("does this secret reach a
log?"), and debugging ("where did this wrong value originate?").
**Human/agent split.** Humans do this in their head over a few hops and lose the thread on long chains. Agents
can in principle track longer chains but need the dataflow edges, not just call edges, surfaced.
**Objective test.** Q: "Trace where a value from `.env`'s `<SECRET>` is read and every sink it reaches." Gold:
manual provenance from `.env.example` key → config loader → consumers, including any log/serialize sink.
Metric: source-correct + sink recall; a missed log/serialize sink is a critical (security) miss.

### C3. Async / concurrency / event flow
**Def.** Identify asynchronous boundaries: queues, event emitters/handlers, promises/awaits across the
lifecycle, background tasks, retries, and the ordering/causality between them.
**Why.** The hardest correctness surface. A change that looks local can race with a background task or break an
implicit ordering. Event-driven edges are invisible to call graphs.
**Human/agent split.** Both struggle; humans use runtime traces, agents must infer from registration patterns
(emit/on, enqueue/consume). This is widely **under-served** by static tools.
**Objective test.** Q: "List every emitter/handler pair for event E and say whether handler ordering is
guaranteed." Gold: manual map of `emit('E')` → `on('E')` registrations + ordering semantics. Metric:
emitter/handler pairing F1 + correct ordering verdict.

### C4. Dynamic dispatch & indirection resolution
**Def.** Resolve calls that are not statically obvious: dependency-injected implementations, registry/plugin
lookups, string-keyed dispatch tables, reflection, higher-order factories.
**Why.** Plugin/adapter architectures (this touchstone has ~29 adapter/plugin packages dispatched at runtime)
hide the *real* implementation behind a lookup; static "go-to-def" lands on the interface, not the impl that
actually runs.
**Human/agent split.** Humans trace the registry by reading the wiring once. Agents need the dispatch table
made explicit, or they will reason about the wrong (abstract) implementation.
**Objective test.** Q: "When adapter id `codex-local` is invoked, which concrete `execute` runs?" Gold: the
registry/dispatch wiring → `packages/adapters/codex-local/src/server/execute.ts:323` (anchor A16). Metric:
correct concrete target among the many sibling `execute` defs.

### C5. Public-surface / API enumeration
**Def.** Enumerate the externally-callable surface: HTTP/RPC routes, CLI commands, exported package APIs,
plugin contracts — with their signatures.
**Why.** Defines the system's contract with the outside world; the set you must not break and the set you
extend. The "stable API" boundary for change safety.
**Human/agent split.** Both consult it; agents use it as the authoritative contract list to avoid breaking
consumers they cannot see.
**Objective test.** Q: "List all HTTP routes and all CLI commands with their handlers." Gold: route registrars
(`issueRoutes @ server/src/routes/issues.ts`) + CLI registrars. Metric: route/command recall + handler-link
accuracy.

---

## Dimension D — Intent, Domain & Rationale (What does it mean? Why does it exist?)

*This dimension is the most under-served by structure-centric tooling and the most load-bearing for non-trivial
changes. Code answers "what"; this answers "why" and "should."*

### D1. Domain vocabulary / ubiquitous language
**Def.** Map the project's domain terms to their code representations and definitions ("issue", "mention",
"heartbeat", "adapter", "runtime", "catalog team") — the glossary that makes names meaningful.
**Why.** Names are only useful if you know the domain they encode. Misreading a domain term ("environment" =
deployment env vs. a DB entity) causes whole-feature misunderstandings.
**Human/agent split.** Humans build this glossary from docs + Slack + tribal knowledge. Agents have *only* what
is in the repo; if intent isn't written down, the agent cannot recover it and will guess plausibly-wrongly.
**Objective test.** Q: "Define 'issue reference mention' as this codebase uses it and point to its canonical
type and table." Gold: `issueReferenceMentions @ packages/db/.../issue_reference_mentions.ts:6` +
`extractIssueReferenceMatches` semantics, cross-checked against README/docs prose. Metric: definition matches
the doc/design intent (human-judged) and cites the right artifacts.

### D2. Rationale / design intent ("why is it this way?")
**Def.** Recover *why* a non-obvious design exists: why a workaround, why a constraint, why this boundary —
from comments, ADRs, design docs, commit messages, PR discussions, and code shape.
**Why.** Most dangerous changes are the ones that "simplify" something that looked redundant but encoded a hard
lesson. Chesterton's fence. Intent is what stops you removing load-bearing weirdness.
**Human/agent split.** Humans ask the author or read the PR. Agents must mine durable artifacts (commit
messages, ADRs, `// NOTE:`/`// HACK:` comments, design docs) — and must *flag when intent is unrecoverable*
rather than inventing a rationale. This is the cross-cutting "trust" property at its sharpest.
**Objective test.** Q: "Why does `prepareCommandManagedRuntime` exist and what failure does it guard against?"
Gold: the rationale as stated in docs/comments/commit history (anchor A15). Metric: rationale matches a
written source; **a fabricated-but-plausible rationale scores zero** (grounding check).

### D3. Documentation & spec discoverability
**Def.** Find the authoritative docs: README, `AGENTS.md`/`CONTRIBUTING.md`, design docs, ADRs, inline doc
comments, RFCs — and know which is current vs stale.
**Why.** The fastest path to intent when it exists. But docs rot; knowing *which* doc is authoritative (and
detecting drift from code) is itself a requirement.
**Human/agent split.** Humans skim and judge currency. Agents need the doc *surfaced and ranked*; many indexers
silently exclude `.md`/docs entirely (a real gap: a code-only indexer cannot answer onboarding questions).
**Objective test.** Q: "What is the authoritative contributor workflow and where is it documented?" Gold:
`CONTRIBUTING.md` + `AGENTS.md` (221 lines) + `docs/`. Metric: correct authoritative source identified;
penalize a method that indexes code only and returns nothing.

### D4. Feature-to-code & requirement-to-code mapping
**Def.** Given a product feature or requirement, find all code, tests, config, and docs that realize it
(vertical slice across layers).
**Why.** Real work is feature-shaped, not file-shaped. Changing a feature safely means finding its *entire*
footprint, not one function.
**Human/agent split.** Humans assemble the slice from memory and search. Agents need the cross-layer slice
assembled because they cannot rely on "I remember the UI part is over there."
**Objective test.** Q: "Assemble the full vertical slice for 'issue references': shared util, DB schema +
migration, server route/service, UI component, tests." Gold: curated multi-layer file set spanning
`packages/shared`, `packages/db`, `server`, `ui`, and tests. Metric: slice recall (files found / files in gold)
+ irrelevant-file ratio.

### D5. Comment / annotation signal extraction
**Def.** Surface in-code intent markers: `TODO`/`FIXME`/`HACK`/`XXX`/`@deprecated`/`@internal`, license
headers, and explanatory comments that encode constraints.
**Why.** These are the author's own warnings and contracts. A `// must run before X` comment is an invariant;
a `@deprecated` is a do-not-extend signal.
**Human/agent split.** Both read them, but agents must be *steered by* them (treat `@deprecated` as a hard
constraint) rather than ignoring prose.
**Objective test.** Q: "List all `@deprecated` exports and all `HACK`/`FIXME` markers with their location."
Gold: grep + AST over annotations/comments. Metric: exact recall (this one is cheap and a method that *can't*
read comments fails outright).

---

## Dimension E — Data Modeling & Persistence (How is data shaped, and how does it move?)

### E1. Schema & data-model map
**Def.** Enumerate the persistent data model: tables/collections, columns/fields, relationships, keys,
constraints, and the code types that mirror them.
**Why.** Data is the most durable, hardest-to-change part of any system. You cannot safely change behavior
without knowing the shape of the data it reads/writes.
**Human/agent split.** Humans read the schema files. Agents need the schema as structured relations to reason
about joins, nullability, and cascade effects.
**Objective test.** Q: "List the columns and foreign keys of the `issues` table and the code const that defines
it." Gold: `issues @ packages/db/src/schema/issues.ts:22` (Drizzle table) + its migration. Metric: column/FK
set match.

### E2. Schema evolution / migration history
**Def.** Trace how the data model reached its current shape: ordered migrations, what each changed, and which
are applied vs pending.
**Why.** Migrations are the audit trail of the data model and the thing most likely to break in prod. A change
that ignores migration ordering corrupts data.
**Human/agent split.** Humans read the migrations dir in order. Agents need the ordered diff sequence and the
current head to avoid generating a conflicting migration.
**Objective test.** Q: "What did migration `0066_issue_tree_holds.sql` change, and what is the current latest
migration?" Gold: the 106 ordered files under `packages/db/src/migrations/`. Metric: correct change summary +
correct head identification.

### E3. Serialization / wire-format boundaries
**Def.** Identify where data crosses a serialization boundary (JSON over HTTP, queue payloads, DB row ↔ object,
env/string parsing) and the schemas that govern each.
**Why.** Most cross-component bugs live at serialization seams (a field renamed on one side, a nullable that
isn't). These are also the compatibility boundaries (old client, new server).
**Human/agent split.** Both must find the seam; agents need the schema-on-each-side to check compatibility
without runtime probing.
**Objective test.** Q: "For route R, what is the request/response JSON shape and which type defines it?" Gold:
route handler + its request/response types. Metric: field-set match on both sides of the boundary.

### E4. Data lifecycle & ownership
**Def.** For a key entity, determine where it is created, mutated, read, and deleted — its CRUD footprint and
which component "owns" it.
**Why.** Ownership tells you where to make a change and who else will be affected; scattered mutation is a
maintenance hazard you must know before touching it.
**Human/agent split.** Humans infer ownership from convention. Agents need the explicit write-site set
(otherwise they patch one writer and miss three).
**Objective test.** Q: "Every place an `issue` row is written (insert/update/delete)." Gold: write-site set via
`issueService` (`issueService(db).create`, anchor A4) + direct DB writes. Metric: write-site recall (a missed
writer is a correctness hole).

---

## Dimension F — Runtime & Behavioral Understanding (What does it do when it runs?)

*Static reading has a ceiling: some truths exist only at runtime. This dimension is structurally invisible to
any purely static method and is therefore systematically under-served.*

### F1. Observed behavior / ground-truth execution
**Def.** Run the thing (or a slice of it) and observe what it actually does for a given input — outputs, side
effects, logs.
**Why.** The ultimate disambiguator. When static analysis is ambiguous (dynamic dispatch, config-dependent
branches), execution is ground truth. Tests and reproductions live here.
**Human/agent split.** Humans run and watch. Agents need a sandbox + the ability to run a targeted command and
parse structured output; an agent that *cannot* execute is permanently guessing on this dimension.
**Objective test.** Q: "For CLI command C with input I, what is the exact output/exit code?" Gold: actually run
it. Metric: predicted vs observed output match. (A static-only method should *honestly decline*, not fabricate.)

### F2. State & lifecycle at runtime
**Def.** Understand the live state model: process/session/connection lifecycle, in-memory caches, what persists
across requests, startup/shutdown order.
**Why.** Bugs and changes around caching, sessions, and lifecycle are invisible in the static tree but dominate
production behavior.
**Human/agent split.** Humans use a debugger/REPL. Agents must infer from init/teardown code + observe via
instrumentation; rarely supported well.
**Objective test.** Q: "What state does `heartbeatService` keep between invocations and when is it reset?"
Gold: read the service + confirm by running (anchor A5). Metric: state-model description matches observed
behavior.

### F3. Performance & resource profile
**Def.** Where time and memory go: hot paths, N+1 queries, large allocations, the token/byte mass of generated
artifacts.
**Why.** Determines what is safe to change without regressing performance and where optimization pays off.
**Human/agent split.** Humans profile. Agents can reason about *obvious* hot spots statically (loops over
queries) but need profiling data for real answers; the static proxy (token-mass triage: `db` = 77%) is a cheap
partial.
**Objective test.** Q: "Identify the most likely N+1 query site for feature F and the largest generated
artifact by size." Gold: profile + size scan. Metric: correct hot-path identification (human-judged) + exact
largest-artifact.

### F4. Logging, tracing & observability surface
**Def.** Find where the system emits diagnostics: log statements, trace spans, metrics, error reporting — and
what each captures.
**Why.** The first thing you reach for when debugging; also a security surface (does a secret reach a log?).
Knowing the observability surface tells you how you'll *see* a change's effect.
**Human/agent split.** Both grep for log calls; agents use the log map to predict what evidence a change will
produce and where to look.
**Objective test.** Q: "Every log/trace emission in the issue-reference flow and the fields each logs." Gold:
log-call set in the traced path. Metric: emission recall + field accuracy (cross-checks C2's sink-recall).

---

## Dimension G — Correctness, Contracts & Invariants (What must stay true?)

### G1. Type & signature contracts
**Def.** The static contracts the compiler enforces: function signatures, generic bounds, exported type
surface, nullability.
**Why.** The cheapest correctness net. A change that satisfies types is far more likely safe; the type surface
*is* a machine-checkable contract.
**Human/agent split.** Both lean on the type checker; agents should run it as a verification gate, not infer it.
**Objective test.** Q: "What is the exact signature of `prepareCommandManagedRuntime` and its return type?"
Gold: the declaration (anchor A15) + `tsc` confirmation. Metric: signature exactness.

### G2. Runtime invariants & preconditions
**Def.** The assumptions that must hold but aren't in the type system: ordering ("must init before use"),
non-null-after-check, idempotency, "single instance", value ranges — found in asserts, guards, and comments.
**Why.** These are the silent landmines. Violating an unstated invariant produces corruption, not a compile
error. (The `isUuidLike` shared copy has a null-guard the two cli shadows *lack* — an invariant divergence that
only binding-aware analysis reveals.)
**Human/agent split.** Humans learn invariants by breaking them. Agents must extract them from guards/asserts/
comments and treat them as constraints — and flag when an invariant is implied but unverifiable.
**Objective test.** Q: "What precondition must hold before calling `startServer`, and what guard enforces it?"
Gold: read guards/asserts + init order. Metric: invariant correctly stated + enforcement site cited.

### G3. Error-handling & failure-mode model
**Def.** How errors propagate: thrown vs returned, error types, retry/backoff, fallback/degradation, what is
swallowed vs surfaced.
**Why.** Changing error handling wrongly turns a recoverable failure into an outage (or hides a real one). You
must know the failure contract before touching a boundary.
**Human/agent split.** Both trace catch blocks; agents need the explicit propagation map to avoid swallowing or
double-handling.
**Objective test.** Q: "If the storage backend is unavailable, what happens — throw, retry, or degrade — and
where is that decided?" Gold: trace `createStorageServiceFromConfig` error paths (anchor A6). Metric: correct
failure-mode classification + decision-site.

### G4. Test inventory & coverage map
**Def.** What tests exist, what each asserts, which code paths they cover, and where coverage is thin.
**Why.** Tests are executable specifications of intended behavior *and* your safety net. Before changing X you
must know which tests guard X (and whether any do).
**Human/agent split.** Humans run the suite. Agents need the test→code mapping to pick the *minimal* tests to
run for a change (running all 739 every hypothesis is wasteful) and to know where they're flying blind.
**Objective test.** Q: "Which tests cover `extractIssueReferenceMatches`, and is the empty-input case tested?"
Gold: the co-located/related test files + assertion reading. Metric: covering-test recall + correct
gap-identification.

### G5. Validation & boundary-enforcement points
**Def.** Where input is validated/sanitized/authorized at trust boundaries (request parsing, auth checks,
schema validation, path/shell-arg sanitization).
**Why.** Security and correctness depend on knowing the boundary is enforced *before* use. A change that moves
logic before a validation point creates a vulnerability.
**Human/agent split.** Both audit boundaries; agents should treat "is this validated upstream?" as a required
check before trusting an input.
**Objective test.** Q: "Is the input to route R validated before it reaches the DB, and where?" Gold: trace
request → validation → write. Metric: correct validation-presence verdict + site; a false "yes" is a critical
miss.

---

## Dimension H — Build, Run, Test & Debug (The operational loop)

### H1. Build & toolchain reproduction
**Def.** Determine how to build the project from scratch: package manager, exact commands, build order, output
artifacts, required toolchain versions.
**Why.** You cannot change what you cannot build. The first hour of any onboarding. Reproducing the build
deterministically is a hard, frequently-broken requirement.
**Human/agent split.** Humans follow the README and debug failures interactively. Agents need the *exact*
command sequence and must detect when a prerequisite (lockfile, link step) is missing — e.g. this repo's
`preflight:workspace-links` step before build/test.
**Objective test.** Q: "Give the exact commands to build the whole workspace from a clean checkout." Gold:
`package.json` scripts: `pnpm install` → `pnpm run build` (which runs `preflight:workspace-links` then
`pnpm -r build`). Metric: command sequence matches and actually builds (run it).

### H2. Run / dev-loop reproduction
**Def.** How to start the system locally (dev server, services, dependencies like DB) and the watch/reload loop.
**Why.** The inner loop of all development. Slow or broken run-loop knowledge kills productivity.
**Human/agent split.** Humans tinker until it runs. Agents need the canonical `dev` entry
(`pnpm dev` → `scripts/dev-runner.ts watch`) and the service dependencies (Docker compose) made explicit.
**Objective test.** Q: "How do I run the server + ui in dev mode, and what backing services must be up?" Gold:
`dev:server`/`dev:ui` scripts + `docker/docker-compose.yml`. Metric: instructions actually start the system.

### H3. Test execution & targeting
**Def.** How to run tests — all, by package, by file, by pattern — and the framework/markers used.
**Why.** The verification gate for every change. Must know how to run the *relevant subset* fast.
**Human/agent split.** Humans run `vitest` and filter. Agents need the precise invocation
(`pnpm test:run` → `scripts/run-vitest-stable.mjs`, with `--mode general/serialized`) and per-file targeting to
verify a change cheaply.
**Objective test.** Q: "Run only the issue-reference tests and report pass/fail." Gold: the targeted vitest
invocation. Metric: correct command + correct pass/fail read.

### H4. Debug & reproduction workflow
**Def.** How to reproduce a bug deterministically and inspect state: debugger attach, log levels, fixtures,
seed data, repro scripts.
**Why.** Debugging is most of maintenance. A reproducible failing case is the precondition for a safe fix
(test-first).
**Human/agent split.** Humans use breakpoints. Agents lean on adding logs + running a minimal repro and reading
structured output; need to know the fixture/seed mechanism.
**Objective test.** Q: "Write and run a minimal reproduction for behavior B of `heartbeatService`." Gold: a
runnable repro that exercises the path. Metric: repro runs and exhibits the behavior.

### H5. CI/CD & release pipeline
**Def.** What CI runs on a change (lint, typecheck, test, e2e, smoke), the gates that block merge, and how a
release is cut/rolled back.
**Why.** Your change must pass CI; knowing the gates lets you self-check before pushing. Release/rollback
knowledge is essential for shipping safely.
**Human/agent split.** Humans read the green/red checks. Agents should *mirror* CI locally (run the same
typecheck/test) before claiming done, and know the release scripts.
**Objective test.** Q: "List the checks that gate a PR and the command to cut a stable release." Gold:
`.github/workflows/pr.yml` (+ e2e/docker/release-smoke) and `release:stable` → `scripts/release.sh stable`.
Metric: gate-set recall + correct release command.

---

## Dimension I — Configuration, Environment & External Boundaries

### I1. Configuration surface & precedence
**Def.** Every knob that changes behavior: env vars, config files, feature flags, CLI flags, defaults — and the
precedence/override order among them.
**Why.** Behavior is config-dependent; the same code does different things under different config. A change
tested under one config can break another. Precedence bugs are subtle and common.
**Human/agent split.** Humans read `.env.example` and config loaders. Agents need the full key set + where each
is consumed + default/override order, because they can't "just try it and see."
**Objective test.** Q: "List all configuration keys, their defaults, and where each is read." Gold:
`.env.example` + config loader + `docker/.env.aws.example`. Metric: key recall + correct
read-site/default per key.

### I2. Environment & runtime prerequisites
**Def.** What the system needs to run: runtime versions, OS deps, services (DB, queues, object storage),
network access, credentials.
**Why.** "Works on my machine" failures live here. Onboarding and reproducibility depend on a complete prereq
list.
**Human/agent split.** Humans discover prereqs by hitting errors. Agents need them enumerated from
Dockerfile/compose/manifests so they don't burn turns on environment errors.
**Objective test.** Q: "What external services and runtime versions are required to run this?" Gold:
`Dockerfile` + `docker-compose.yml` + `package.json` engines. Metric: prereq-set recall.

### I3. External dependency inventory & boundaries
**Def.** Third-party packages, external APIs/SDKs, and the *seams* where the codebase calls out — including
version constraints and where each is wrapped/adapted.
**Why.** External boundaries are where breakage, security issues, and version drift enter. Knowing the wrapper
layer tells you the blast radius of swapping a dependency.
**Human/agent split.** Humans scan `package.json`. Agents need the dependency→call-site map to assess upgrade
impact and to *not invent APIs* for a dependency they don't actually know (verify against real docs).
**Objective test.** Q: "Which external SDK does the `codex-local` adapter wrap, and where is the boundary?"
Gold: the adapter's dependency + its `execute` wrapper (anchor A16). Metric: correct dependency + boundary site.

### I4. Secrets & sensitive-surface map
**Def.** Where secrets/credentials are defined, injected, and consumed — and confirmation they are *not* in
git, logs, or serialized output.
**Why.** A leaked secret is a critical incident. Before changing a boundary you must know the secret-handling
contract (inject at construction, never log).
**Human/agent split.** Both audit; agents must treat "does this path touch a secret?" as a mandatory check
(and note tools that silently *drop* files named `secrets.ts` — a real recall hole from `findings.md`).
**Objective test.** Q: "List every secret/credential and confirm none is committed or logged." Gold: secret
keys + their injection sites + a scan for leaks. Metric: secret recall + zero false "safe" on an actual leak.

---

## Dimension J — History, Change Patterns & Evolution

*(Requires `.git`; not testable on the pruned snapshot — run against `external/paperclip`.)*

### J1. Change history & blame
**Def.** For a file/symbol: when and why it last changed, who changed it, and the commit/PR rationale.
**Why.** History is the cheapest source of *intent* (Dimension D) and of "is this code hot or frozen?" Recent
churn flags risk; a line untouched for years is load-bearing.
**Human/agent split.** Humans `git blame` + open the PR. Agents need commit messages mined as the durable
intent record (most teams' only written rationale).
**Objective test.** Q: "Why was the null-guard added to the shared `isUuidLike`, and in which commit?" Gold:
`git log -p`/blame on the line. Metric: correct commit + rationale from its message.

### J2. Churn & hotspot analysis
**Def.** Which files change most often, co-change together, and concentrate bugfix commits — the risk hotspots.
**Why.** Hotspots predict where bugs and merge conflicts will occur and where extra care/tests pay off.
Co-change reveals *implicit* coupling that the import graph misses.
**Human/agent split.** Humans have a gut feel ("that file again"). Agents need churn computed from git so they
can prioritize attention and detect hidden coupling.
**Objective test.** Q: "Top-10 most-churned files in the last N commits and which pairs co-change." Gold:
`git log --name-only` frequency + co-occurrence. Metric: hotspot-set overlap + top co-change pair correctness.

### J3. Convention & idiom evolution
**Def.** Detect deprecated-but-present patterns vs current idioms (old vs new way of doing X), and migration
state (half-migrated subsystems).
**Why.** New code should follow the *current* idiom, not a deprecated one still visible in the tree. Picking
the wrong pattern is a review failure and adds tech debt.
**Human/agent split.** Humans know "we don't do it that way anymore." Agents must infer recency (newest files /
most-tested pattern wins) and *surface the conflict* rather than blending the two (per the project's own
AK guideline #7).
**Objective test.** Q: "There are two patterns for X in the tree; which is current and which is deprecated?"
Gold: dates/comments/`@deprecated` + commit recency. Metric: correct current-vs-deprecated verdict with
evidence.

---

## Dimension K — Human & Organizational Context

### K1. Ownership & responsibility map
**Def.** Who owns each area: CODEOWNERS, maintainers, dominant committers per directory, review requirements.
**Why.** Tells you who to ask, who must review a change, and where tribal knowledge lives. Routing a change to
the wrong owner stalls it.
**Human/agent split.** Humans ask around. Agents derive ownership from CODEOWNERS + git authorship to know
whose review a change needs and whose intent to trust.
**Objective test.** Q: "Who owns / must review changes to `packages/adapters/`?" Gold: CODEOWNERS (if present)
+ top committers. Metric: correct owner set.

### K2. Contribution rules & guardrails
**Def.** The project's explicit rules for contributors: coding style, commit/PR conventions, forbidden patterns,
required checks, agent-specific instructions.
**Why.** A change that violates the house rules is rejected regardless of correctness. These rules also encode
hard constraints (e.g. forbidden-token checks).
**Human/agent split.** Humans read `CONTRIBUTING.md` once. Agents must *load and obey* `AGENTS.md`/
`CONTRIBUTING.md` and check rules like `check:tokens` / `check:no-git-push` — these are machine-enforced gates
the agent will trip if it doesn't read them.
**Objective test.** Q: "What does this repo forbid in committed code, and which script enforces it?" Gold:
`AGENTS.md` + `scripts/check-forbidden-tokens.mjs` / `check-no-git-push.mjs`. Metric: correct rule + enforcement
script.

### K3. Communication & decision artifacts
**Def.** Where decisions are recorded and discussed: ADRs, RFCs, roadmap, issue tracker, PR threads, design docs.
**Why.** The *why* behind direction lives here (Dimension D's organizational layer). Knowing where to look
saves re-litigating settled decisions.
**Human/agent split.** Humans know the team's channels. Agents are limited to in-repo artifacts (`ROADMAP.md`,
`docs/`, commit/PR text) and must flag when a decision's rationale lives outside the repo and is unrecoverable.
**Objective test.** Q: "Where is the project's roadmap/direction recorded and what's the next planned area?"
Gold: `ROADMAP.md` + `docs/`. Metric: correct artifact + accurate summary.

---

## Dimension L — Efficiency, Trust & Freshness of Answers (Cross-cutting)

*These four are not separate questions — they are properties every answer to A–K must have. They are the
properties that most sharply separate a usable method from an unusable one, especially for agents.*

### L1. Answer cost / token & read economy
**Def.** How much must be read (tokens, files, tool calls, wall-clock) to get a correct answer of a given kind.
**Why.** For an agent, cost *is* feasibility: a method that answers B2 correctly but only by packing 5.96M
tokens has not answered it usably. For a human, cost is patience/time. The ideal is *answer-sized* retrieval —
the minimal context that supports the answer.
**Human/agent split.** Humans tolerate slow visual exploration and pay attention, not dollars. Agents pay per
token and per turn and have a hard context ceiling; the same correct answer at 200 tokens vs 200k tokens is a
different product.
**Objective test.** Q: hold answer-quality fixed (e.g. B2 at the labeled gold) and measure cost. Gold:
required-files-per-anchor set. Metric: tokens consumed, files read, tool calls, wall-time **at equal accuracy**;
also "required-file recall" and "irrelevant-context ratio." (Battery scenario 14; `findings.md` §8 flags this
equal-quality A/B as the highest-value *unrun* measurement.)

### L2. Grounding / verifiability / anti-hallucination
**Def.** Every answer cites checkable evidence (`file:line`, command output) and the method *declines or flags*
when it cannot ground the answer, rather than fabricating.
**Why.** An ungrounded answer is worse than no answer because it is acted on. This is the single most important
property for agents, which produce fluent, plausible, wrong answers by default.
**Human/agent split.** Humans naturally distrust and double-check. Agents must be *engineered* to ground —
a method that returns confident prose with no citation fails this regardless of how often it's right.
**Objective test.** Inject answerable and unanswerable questions (e.g. "why does X exist?" where no rationale
is recorded). Gold: the answerable set + the known-unrecoverable set. Metric: citation-validity on answerable
Qs (do the cited `file:line` exist and support the claim?) + **honest-abstention rate** on unanswerable Qs
(fabrication = critical failure).

### L3. Freshness / staleness safety
**Def.** Answers reflect the *current* working tree; if the method uses a precomputed index, it knows its index
is stale and refreshes or warns.
**Why.** A stale index gives confidently-wrong answers about code that just changed — exactly when an agent is
mid-edit and most needs truth. Worktree/branch bleed (an index answering about the *parent* repo's diff, per
`findings.md` §5) is a real, observed failure.
**Human/agent split.** Humans re-open the file. Agents trust the index unless told otherwise; staleness must be
detected mechanically.
**Objective test.** Q: edit a symbol, then immediately ask B1/B2 about it. Gold: the post-edit state. Metric:
does the answer reflect the edit (correct), or the stale index (fail)? Also test branch/worktree isolation.

### L4. Setup cost, isolation & determinism
**Def.** What it costs to make the method *work* on a new repo: install/index time, prerequisites, whether it
pollutes global state, and whether repeated runs give the same answer.
**Why.** A method that needs a 65s compile, a language server install, or a built/linked workspace before its
first answer has a real adoption cost; one that writes telemetry to global `$HOME` or bleeds git context across
repos is unsafe to run (all observed in `findings.md` §7). Determinism is required to trust and to test.
**Human/agent split.** Humans set up once and forget. Agents may spin up per-task/per-repo, so per-invocation
setup cost and isolation matter far more, and non-determinism breaks their verification loop.
**Objective test.** Q: from a clean checkout, time to first correct answer + audit of global-state writes.
Gold: a clean `$HOME` and a read-only subject before the run. Metric: setup wall-time, count of files written
outside the sandbox (must be 0), and answer-stability across 3 identical runs.

---

## 13. Cross-cutting properties summary

Every requirement in A–K is graded on **four axes** simultaneously (L1–L4):

| Axis | Question | Failure looks like |
| --- | --- | --- |
| **Correctness** | Is the answer right (precision + recall vs gold)? | Missed callers; merged shadows; wrong def |
| **Cost (L1)** | How little must be read to get it? | Correct only by packing the whole repo |
| **Grounding (L2)** | Is it cited + does it abstain when it can't know? | Fluent, plausible, uncited, wrong |
| **Freshness (L3)** | Does it reflect the current tree? | Stale index; worktree/branch bleed |
| **Setup/Isolation (L4)** | What does it cost to run + does it stay clean? | Global-`$HOME` pollution; long index build |

A method can be excellent on correctness and still unusable (packs 6M tokens, or hallucinates rationale, or
answers about a stale tree). **Grading correctness alone — which most benchmarks do — is the most common
evaluation mistake.**

---

## 14. Prioritized view

### 14a. Most load-bearing for day-to-day productivity (in rough order)

1. **A3/A4 — Orientation & architecture map.** Everything starts with "where am I / what depends on what."
   Cheap to provide, disproportionately enabling; without it every other query is unguided.
2. **B1/B2/B5 — Go-to-def, semantic find-usages, barrel/cross-package resolution.** The highest-*frequency*
   micro-tasks; every edit needs them. Empirically the hardest to get right on a monorepo (`findings.md` §4).
3. **B6 — Blast radius.** The core change-safety question; gates test scope and review scope.
4. **H1/H3 — Build & test reproduction.** You cannot change what you can't build or verify; first-hour
   blockers, frequently broken.
5. **D4 — Feature-to-code vertical slice.** Real work is feature-shaped; assembling the cross-layer footprint
   is what makes a change complete rather than partial.
6. **L1/L2 — Answer economy + grounding.** Determine whether *any* of the above is usable by an agent at all.

### 14b. Most often UNDER-served by typical approaches

- **Reverse references across barrel re-exports (B2/B5)** — LSP `find_referencing_symbols` is structurally
  blind to barrel-exported public APIs (verified, not inferred). The single most decisive monorepo gap.
- **JSX / component-body / dynamic-dispatch call sites (B3/C4)** — the recall frontier; static graphs and
  tree-sitter attribution both drop them.
- **Intent & rationale (D1/D2)** — code-structure tools answer "what," almost never "why"; many index code
  only and exclude docs/comments entirely, so onboarding/intent questions return nothing.
- **Runtime & behavioral truth (F1–F4)** — structurally invisible to static methods; most "understanding"
  tools cannot run anything, so they permanently guess on dynamic dispatch and config-dependent behavior.
- **Async / concurrency / event flow (C3)** — event edges aren't call edges; near-universally unsupported.
- **History-as-intent (J1–J3)** — the cheapest rationale source, ignored by any method that doesn't read git.
- **Grounding & abstention (L2)** and **freshness (L3)** — rarely measured at all, yet decisive for agents.

### 14c. Easy to overlook because they concern comprehension / intent / runtime / operations, not structure

These are the requirements a structure-and-navigation mindset systematically forgets, even though they
dominate the *safety* of real changes:

- **D2 Rationale / Chesterton's fence** — *why* the weird code exists; removing load-bearing weirdness is the
  classic confident-agent failure.
- **G2 Runtime invariants** — unstated ordering/idempotency/non-null assumptions that produce corruption, not
  compile errors (e.g. the null-guard present in one `isUuidLike` copy and absent in its shadows).
- **G3 Failure-mode model** — what happens when a dependency is down; mis-changing it turns a degrade into an
  outage.
- **F1/F2 Runtime behavior & state** — the static tree never shows what actually runs under dynamic dispatch
  and config.
- **I1 Config precedence** — the same code behaving differently under different config; tested-here-broken-there.
- **I4 Secret surface** — a path touching a secret; one observed tool silently drops files named `secrets.ts`.
- **H5/K2 CI gates & house rules** — machine-enforced gates (`check:tokens`, `check:no-git-push`, required
  reviews) that reject a correct change for violating convention.
- **L2/L3 Grounding & freshness** — properties, not features; their absence makes every other correct answer
  untrustworthy.

---

## 15. How to use this catalogue to evaluate a method

1. Pick a repo and a labeled anchor set spanning the symbol-shape buckets (per `anchors-<repo>.md`) **plus**
   non-symbol anchors for D/E/F/H/I/J/K (a feature, a table, a config key, a build command, a migration, a
   commit).
2. For each requirement, pose its objective-test question against the anchors; compute the gold independently
   of the method under test (the ground-truth method in `scenarios.md` §"Ground-truth method").
3. Score every answer on all five axes of §13 — never correctness alone.
4. Aggregate **by requirement and by symbol-shape bucket**, not a single mean; a weakness counts only if it
   reproduces across ≥2 anchors in a bucket (the robustness rule).
5. Keep **"honestly unsupported / abstained"** separate from **"attempted and wrong"** — a method that knows
   its limits is safer than one that confidently overclaims.

A method's profile is then a matrix (requirement × bucket × {correctness, cost, grounding, freshness, setup}),
which is what actually predicts whether a human or an agent can be productive with it — far more than any
single headline score.
