# Graphify capability discovery

Report state: `DONE_WITH_CONCERNS`

Recorded: 2026-07-24

Tracking: `orch-8sk.16.4`

## Scope and evidence boundary

This report covers Graphify only. Discovery used the disposable tool checkout at
`scratchpad/code-intelligence/tools/graphify`, the isolated fixture at
`scratchpad/code-intelligence/fixtures/graphify`, and Graphify-only ignored
indexes, outputs, metrics, and sessions. It did not inspect Pi, Codex, another
graph tool, or another tool's output. No fetch, package install, model-backed
Graphify extraction, remote API, external database, credentialed operation,
persistent user-global mutation, or live-submodule mutation was performed.

The evidence order was:

1. runtime CLI help/version and public probes;
2. source registration and optional-dependency declarations;
3. maintained documentation and tests;
4. fixture behavior, including boundary and failure cases.

The frozen tool revision is
`2fa6cd3d5548577f8c5f591b713f0bf80c1af183`. The editable isolated
distribution and `pyproject.toml` both report `graphifyy 0.9.25`. The tool
checkout was clean before and after discovery.

## Result at a glance

| Area | Result | Disposition |
| --- | --- | --- |
| Offline code-only build | 18 classified code files; 108 nodes; 173 edges; 10 communities | `VERIFIED` |
| Model use in code-only build | `.graphify_analysis.json` reports 0 input and 0 output model tokens | `VERIFIED` |
| Query and inspection | query, exact-ID explain, path, affected, god nodes, diagnostics, benchmark; precision limitations are detailed below | `VERIFIED` |
| Clustering/report | offline/no-label clustering, placeholder community labels, Markdown report | `VERIFIED` |
| Local exports | HTML, call-flow HTML, tree HTML, Obsidian, wiki, GraphML, local Neo4j/FalkorDB Cypher | `VERIFIED` |
| SVG | exposed, but `matplotlib` is absent | `UNAVAILABLE` |
| Incremental update | completed, but did not preserve the code-only corpus and changed source-path spelling | `PARTIAL` |
| Update shrink behavior | both unflagged and `--force` update overwrote an induced 127→112-node shrink, contrary to the help-implied distinction | `PARTIAL` |
| Update `--no-cluster` | produced zero communities and no report/HTML | `VERIFIED` |
| Cargo introspection | works when the scan root contains `Cargo.toml`; fails at the mixed fixture root where the manifest is nested | `PARTIAL` |
| Provider registry reads | isolated empty `provider list` exited 0; missing show exited 1; preseeded non-secret `provider show offline-fixture` exited 0 without modifying configuration | `VERIFIED` |
| Disposable state lifecycles | lane-local global/provider add-remove and fixture-local hook install-uninstall completed and cleaned up | `VERIFIED` |
| Project platform lifecycle | 19 generic project installs succeeded, but 6 uninstalls left residue | `PARTIAL` |
| MCP | source registers 10 tools and 6 resources; the isolated environment lacks the `mcp` extra, so no runtime handshake/list was possible | `UNAVAILABLE` |
| Semantic labeling/extraction | requires a model backend, credentials, or local model service | `RESTRICTED` |
| Real-user/remote integration writes | network, GitHub, external DB, persistent global graph/provider state, live hooks/platform config, or destructive effects | `RESTRICTED` |
| Valid capped Terra probe | historical attempt retained separately as invalid metadata because it exceeded the call cap and failed schema validation; valid retry is runner-gated | `UNTESTED` |

The most important systems-level conclusion is that Graphify is a useful
low-cost structural orientation layer, not a complete source-analysis oracle.
On this fixture it found both languages, most type/import structure, stable
path-qualified IDs, and a short lifecycle segment. It did not represent object
literal constructors, dynamic dispatch, the runtime-selected TypeScript-to-Rust
process boundary, or the complete success/failure lifecycle. A label-only
lookup also silently selected one of two `normalize` symbols; callers should
use exact IDs.

## Frozen runtime and isolation

| Component | Frozen value |
| --- | --- |
| Graphify source | `2fa6cd3d5548577f8c5f591b713f0bf80c1af183` |
| Distribution | `graphifyy 0.9.25` |
| Python | 3.12 |
| NetworkX | 3.6.1 |
| tree-sitter | 0.25.2 |
| Fixture commit | `e7ddad2c44321f7b50e60c923b8f0733fb757874` |
| Fixture manifest digest | `fc12b07aa2219f346ee1e00f52875efae8c52bbb12dc410456e9457ea1b58e24` |
| Artifact tokenizer | `gpt-tokenizer@3.4.0:o200k_base` |

Every tool invocation ran through
`docs/research/harness-tools/codebase-intelligence/experiments/coding-agents/run-isolated.sh`
with a lane-local home, cache, config, state, temp, and output directory; no
provider keys or ordinary Git credentials were inherited. Destructive-looking
state mutations were confined to disposable fixture copies and lane-local
homes; no real user-global, live-submodule, or host configuration was changed.
Graphify wrote to
the wrapper's absolute `GRAPHIFY_OUT`, even when `extract --out` was also
supplied. In this environment the environment override took precedence over
the CLI output argument. The resulting graph was copied to
`indexes/graphify/baseline/` before query operations could write freshness
stamps.

The canonical fixture hashes were verified before extraction and after the
synthetic update was reversed. The synthetic patch was applied with `git
apply`, the public update was exercised, and the patch was reversed with `git
apply -R`; final fixture status was clean and every frozen SHA-256 matched.

A separate immutable comparison baseline lives at
`indexes/graphify/clean-baseline-e7ddad2/`. It contains exactly
`.graphify_analysis.json`, `.graphify_root`, `GRAPH_REPORT.md`, `graph.json`,
and `manifest.json`; it contains no `.graphify_learning.json`, result memory,
query log, or `cache/last_query_stamp`. All five files have recorded SHA-256
digests and read-only modes, and the directory itself is non-writable.
Evidence: `clean-baseline-manifest.txt`.

## CLI and configuration inventory

`graphify --help` exposes 44 command families. The universal help guard sends
most `subcommand --help` calls back to the top-level help rather than providing
independent recursive parsers, so the dispatcher and per-command usage errors
were reconciled with the help text. Free-text commands require positional text
before `--graph`; for example, `graphify explain WorkResult --graph GRAPH`.

### Core graph operations

| Public surface | Purpose and effects | Probe result | Disposition |
| --- | --- | --- | --- |
| `extract` | detect, AST/semantic extraction, build, cluster, analyze, write graph/manifest/cache | `--code-only` succeeded offline; optional modes split below | `VERIFIED` |
| `update` | rebuild current code graph and report without LLM | succeeded in 0.20 s, but changed corpus/path representation | `PARTIAL` |
| `watch` | long-running rebuild watcher; needs `watchdog` | dependency absent and unbounded process not started | `UNAVAILABLE` |
| `cluster-only` | recluster existing graph and regenerate report/visualization | `--no-label --no-viz` produced 10 communities and report | `VERIFIED` |
| `label` | LLM community naming | inventoried; not given credentials/backend | `RESTRICTED` |
| `query` | BFS/DFS natural-language/keyword traversal with budget and context filters | lifecycle and collision queries exercised | `VERIFIED` |
| `explain` | node plus direct in/out relationships | exact IDs worked; ambiguous label chose first match | `PARTIAL` |
| `path` | shortest undirected route with stored relation/confidence | exact-ID lifecycle path succeeded; missing endpoint returned diagnostic | `VERIFIED` |
| `affected` | reverse traversal with relation/depth controls | type-reference blast radius returned | `VERIFIED` |
| `god-nodes` | degree-ranked architectural hubs, text or JSON | top 10 returned | `VERIFIED` |
| `diagnose multigraph` | read-only edge-collapse and producer-suppression audit | 108/173 graph, no duplicate/collapsed endpoint groups | `VERIFIED` |
| `benchmark` | local corpus-versus-query token estimate | reported about 7,200 naive vs 1,684 average query tokens, 4.3x; this is an estimate, not a saving claim | `VERIFIED` |
| `check-update` | cron-safe semantic-update marker check | clean case exited 0 without output | `VERIFIED` |
| `save-result` | write query outcome memory | wrote one lane-local result | `VERIFIED` |
| `reflect` | aggregate result memory into deterministic lessons/overlay | aggregated one useful result | `VERIFIED` |

### Export, composition, and visualization

| Public surface | Probe result | Disposition |
| --- | --- | --- |
| `tree` | wrote 20,797-byte D3 tree HTML | `VERIFIED` |
| `export html` | wrote standalone `graph.html` | `VERIFIED` |
| `export callflow-html` | wrote 63,090-byte HTML, 6 sections, 5 Mermaid diagrams, 4 call tables | `VERIFIED` |
| `export obsidian` | wrote 118 notes plus canvas | `VERIFIED` |
| `export wiki` | wrote 20 Markdown articles and index | `VERIFIED` |
| `export graphml` | wrote local GraphML | `VERIFIED` |
| `export neo4j` without `--push` | wrote 35,136-byte local Cypher script | `VERIFIED` |
| `export falkordb` without `--push` | wrote 35,136-byte local OpenCypher script | `VERIFIED` |
| `export svg` | raised `ImportError: matplotlib not installed` | `UNAVAILABLE` |
| Neo4j/FalkorDB `--push` | needs external database, network, and normally credentials | `RESTRICTED` |
| `merge-graphs` | merged baseline and crate graph to 122 nodes/188 edges | `VERIFIED` |
| `merge-driver` | union-merged disposable graph copies | `VERIFIED` |
| `global list/path` | read an empty lane-local global registry and printed its path | `VERIFIED` |
| lane-local `global add/remove` | added 108 nodes under an isolated home and removed them cleanly | `VERIFIED` |
| real-home `global add/remove`; `extract --global` | write the operator's persistent global graph; not exercised outside isolation | `RESTRICTED` |

### Acquisition, PR, provider, hook, and platform integration

| Surface | Effects/prerequisites | Disposition |
| --- | --- | --- |
| `clone` | network plus clone below user storage | `RESTRICTED` |
| `add` | fetch URL, write corpus, update graph | `RESTRICTED` |
| `prs` and MCP PR tools | `gh`, GitHub authentication/network; triage can also use a configured backend | `RESTRICTED` |
| `provider list`; `provider show NAME` | read the lane-local global provider registry; list created only its parent directory, missing show exited 1, and a non-secret preseeded record displayed successfully without activation or mutation; evidence: `provider-read-only.txt` | `VERIFIED` |
| lane-local `provider add/remove` | added, listed, showed, and removed a non-secret record pointing to an unbound loopback endpoint; no backend was activated | `VERIFIED` |
| real-home `provider add/remove` | mutate the operator's persistent provider registry; a configured endpoint receives corpus content and its configured key | `RESTRICTED` |
| `hook status` | fixture read-only status reported all hooks absent | `VERIFIED` |
| lane-local `hook install/uninstall` | disposable fixture gained post-commit/post-checkout hooks and a merge driver, then returned to clean Git status | `VERIFIED` |
| live-repository `hook install/uninstall` | modifies real Git hooks and merge-driver config | `RESTRICTED` |
| project-scoped top-level `install`/`uninstall` | 19 advertised generic platform values installed successfully in separate fixture copies; 13 cleaned fully and 6 left residue | `PARTIAL` |
| direct platform `install`/`uninstall` | all 21 dispatcher targets were exercised in isolated homes/projects, including the previously missing Copilot, Kilo, and VS Code paths; six uninstall paths left Graphify-related residue | `PARTIAL` |
| user-scoped top-level installers/uninstallers | all 19 generic values were exercised in isolated homes; the generic user-scope uninstaller ignores its parsed platform selector and 15 paths retained Graphify artifacts | `BROKEN` |
| Claude project `--strict`; disposable `--purge` | strict hook payload contained `--strict`; purge deleted the wrapper-configured isolated output directory, while a control sentinel at the default project path demonstrated that `GRAPHIFY_OUT` takes precedence | `VERIFIED` |
| live user-home/platform installers | mutate real host integration files and were not exercised outside isolation | `RESTRICTED` |

The dispatcher also contains `cache-check`, `merge-chunks`,
`merge-semantic`, `hook-check`, and `hook-guard`. They support Graphify's own
agent/hook pipeline but are absent from the advertised top-level command list;
they are recorded as hidden/internal surfaces, not promoted to supported public
capabilities by source existence alone.

The normalized machine-readable matrix is
`normalized-capability-matrix.json`. It contains 433 unique entries and permits
all seven protocol dispositions, including `BROKEN`: 249 `VERIFIED`, 36
`PARTIAL`, 27 `BROKEN`, 42 `UNAVAILABLE`, 54 `RESTRICTED`, 24 `UNTESTED`,
and one `NOT APPLICABLE`. Every row carries the public surface, purpose,
inputs, output/schema, prerequisites, effects, evidence, fixture result,
Pi/Codex applicability, limitations, and cost fields. A mechanical set
comparison confirms that its 44 `command.*` entries cover every advertised
command in `help-command-families.txt` exactly once. Additional one-key rows
cover public subcommands, effect-bearing flags, individual `GRAPHIFY_*`
controls, direct and generic platform/scope operations, 10 MCP tools, six MCP
resources, both transports, filename/ignore routing controls, all 23 declared
extras, and the valid capped Terra probe.

### Exhaustive public flag and configuration inventory

The following inventory reconciles top-level help with the frozen dispatcher.
“Accepted” means the parser accepted the flag; it does not imply that a
dormant semantic/model control affected a code-only run.

| Surface | Public flags/configuration | Effects, prerequisites, and evidence | Disposition |
| --- | --- | --- | --- |
| global CLI | `-h`, `--help`, `-?`, `-v`, `--version`, `version` | read-only help/version; universal help guard applies to most subcommands; evidence: `help.txt`, `version.txt` | `VERIFIED` |
| `extract` corpus/output | positional path; `--out`/`--output`; `--code-only`; `--no-gitignore`; repeatable `--exclude`; `--google-workspace`; `--postgres`; `--cargo`; `--global`; `--as` | local corpus/output flags worked, while optional external/global integrations were not activated; evidence: `extract-code-only.txt`, `extract-safe-flags.txt`, Cargo artifacts | `PARTIAL` |
| `extract` pipeline | `--backend`, `--model`, `--mode deep`, `--force`, `--no-cluster`, `--dedup-llm`, `--allow-partial`, `--timing` | force/no-cluster/timing worked; guarded allow-partial behavior is untested and model modes are restricted; evidence: `extract-safe-flags.txt` | `PARTIAL` |
| `extract` tuning | positive `--max-workers`, `--token-budget`, `--max-concurrency`, `--api-timeout`, `--resolution`; numeric `--exclude-hubs` | parser and code-only acceptance worked; semantic/model-side effects were not exercised; evidence: `extract-safe-flags.txt` | `PARTIAL` |
| `update` | path, `--force`, `--no-cluster` | all paths executed, but corpus/path continuity failed and unflagged shrink contradicted the help-implied force distinction; evidence: `update-synthetic-change.txt`, `update-force-shrink.txt`, `update-no-cluster.txt` | `PARTIAL` |
| `cluster-only` | path; `--graph`; `--no-viz`; `--no-label`; `--backend`; `--model`; `--resolution`; `--exclude-hubs`; `--max-concurrency`; `--batch-size`; `--min-community-size`; `--timing` | offline/no-label reclustering worked; `--resolution`, `--exclude-hubs`, and `--min-community-size` are individually `PARTIAL` because combined low/high runs produced identical community counts and do not establish causal attribution; optional model labeling remained restricted; evidence: `cluster-only.txt`, `safe-flag-probes.txt` | `PARTIAL` |
| `label` | path; `--graph`; `--missing-only`; `--backend`; `--model`; `--max-concurrency`; `--batch-size`; `--min-community-size`; `--timing` | names all or only missing communities with model | `RESTRICTED` |
| `query` | question; `--dfs`; repeatable `--context`; `--budget`; `--graph` | BFS/DFS, context filters, and budgets worked; evidence: `query-lifecycle.txt`, `query-dfs-context-budget.txt`, `query-multi-context-budget.txt` | `VERIFIED` |
| `affected` | node; repeatable `--relation`; `--depth`; `--graph` | relation/depth variants worked; evidence: `affected-workresult.txt`, `affected-relation-depth.txt` | `VERIFIED` |
| `path`, `explain` | positional labels/IDs; `--graph` | exact-ID lookup worked, but label-only explain is ambiguous; evidence: `path-lifecycle.txt`, `explain-core-normalize.txt` | `PARTIAL` |
| `god-nodes` | `--top`; `--graph`; `--json` | local degree ranking; evidence: `god-nodes.json` | `VERIFIED` |
| `diagnose multigraph` | `--graph`; `--json`; `--max-examples`; mutually exclusive `--directed`/`--undirected`; `--extract-path` | directed and undirected modes, example limits, producer-source scan, and mutual-exclusion error worked; evidence: `diagnose-multigraph.json`, `safe-flag-probes.txt` | `VERIFIED` |
| `benchmark` | optional graph path | local approximate word/token comparison; `benchmark.txt` records the estimate boundary | `VERIFIED` |
| `save-result` | required `--question`; `--answer` or `--answer-file`; `--type`; `--nodes`; enum `--outcome useful|dead_end|corrected`; `--correction`; `--memory-dir` | writes local result memory; evidence: `save-result.txt` | `VERIFIED` |
| `reflect` | `--memory-dir`; `--out`; `--graph`; `--analysis`; `--labels`; `--half-life-days`; `--min-corroboration`; `--if-stale` | writes lesson document and optional graph-side learning overlay; evidence: `reflect.txt` | `VERIFIED` |
| `tree` | `--graph`; `--output`; `--root`; `--max-children`; `--top-k-edges`; `--label` | custom root/limits/label/output wrote an 18,860-byte D3 HTML; evidence: `tree.txt`, `safe-flag-probes.txt` | `VERIFIED` |
| `merge-graphs` | two or more graph paths; `--out` | writes union graph; evidence: `merge-graphs.txt` | `VERIFIED` |
| `merge-driver` | base/current/other positional paths | overwrites current disposable graph with union; evidence: `merge-driver.txt` | `VERIFIED` |
| `export html` | `--graph`; `--labels`; `--node-limit`; `--no-viz` | a 10-node limit selected the aggregated community view; `--no-viz` removed/skipped HTML; evidence: `export-html.txt`, `safe-flag-probes.txt` | `VERIFIED` |
| `export callflow-html` | optional graph/dir; `--graph`; `--labels`; `--report`; `--sections`; `--output`; `--lang`; `--max-sections`; `--diagram-scale`; `--max-diagram-nodes`; `--max-diagram-edges` | explicit section/label/report/output/language/diagram controls and automatic section selection worked; evidence: `export-callflow.txt`, `safe-flag-probes.txt` | `VERIFIED` |
| other local exports | `obsidian --graph --labels --dir`; `wiki/svg --graph --labels`; `graphml --graph` | Obsidian/wiki/GraphML worked, while SVG was unavailable without matplotlib; evidence: `export-*.txt` | `PARTIAL` |
| DB exports | `neo4j`/`falkordb`: `--graph`; optional `--push`, `--user`, `--password` or password env | local no-push Cypher worked; remote push remained restricted; evidence: `export-neo4j.txt`, `export-falkordb.txt` | `PARTIAL` |
| `global` | `add GRAPH --as`; `remove TAG`; `list`; `path` | all four operations worked under an isolated home; real-home use and `extract --global` remain restricted; evidence: `global-read-only.txt`, `safe-state-mutations.txt` | `PARTIAL` |
| `provider` | `list`; `show NAME`; `add NAME --base-url --default-model --env-key [--pricing-input --pricing-output]`; `remove NAME` | all registry operations worked with a non-secret, unbound-loopback record in an isolated home; real-home mutation or backend activation remains restricted; evidence: `provider-read-only.txt`, `safe-state-mutations.txt` | `PARTIAL` |
| `prs` | `--triage`; `--worktrees`; `--conflicts`; `--wrong-base`; `--base`/`-b`; `--repo`/`-R`; `--graph` | invokes Git/`gh`; triage may invoke model | `RESTRICTED` |
| `clone`, `add` | clone URL with `--branch`, `--out`; add URL with `--author`, `--contributor`, `--dir` | network plus corpus writes | `RESTRICTED` |
| hooks/watch/update check | `hook install|uninstall|status`; `watch PATH`; `check-update PATH` | hook lifecycle worked in a disposable fixture and check worked; live-repository hooks remain restricted and watch is unavailable without watchdog | `PARTIAL` |
| host installation | `install [--project] [--strict] [--platform P]`; `uninstall [--purge] [--project] [--platform P]`; platform `install|uninstall`, with project scope where supported and Claude strict mode | isolated probes cover 21 direct, 19 generic user, and 19 generic project targets with timing/RSS, plus strict and purge; project and direct residue is recorded per key, and generic user-scope uninstall is broken for retained integrations; evidence: `direct-platform-probes.txt`, `user-install-matrix.txt`, `project-install-timing-matrix.txt`, `strict-and-purge-probes.txt`, `purge-configured-out-probe.txt` | `PARTIAL` |

Declared `GRAPHIFY_*` environment configuration is also part of the public
surface. User-facing path/cache/security controls are `GRAPHIFY_OUT`,
`GRAPHIFY_FORCE`, `GRAPHIFY_MAX_WORKERS`, `GRAPHIFY_API_TIMEOUT`,
`GRAPHIFY_MAX_GRAPH_BYTES`, `GRAPHIFY_NO_INCREMENTAL_CACHE`,
`GRAPHIFY_NO_BACKUP`, `GRAPHIFY_VIZ_NODE_LIMIT`, and
`GRAPHIFY_ALLOW_LOCAL_PROVIDERS`. Query/log controls are
`GRAPHIFY_QUERY_LOG`, `_ENABLE`, `_DISABLE`, `_RESPONSES`,
`GRAPHIFY_LOG`, `GRAPHIFY_DEBUG`, `GRAPHIFY_NO_TIPS`. Model controls are
`GRAPHIFY_MAX_OUTPUT_TOKENS`, `GRAPHIFY_MAX_RETRIES`,
`GRAPHIFY_LLM_TEMPERATURE`, `GRAPHIFY_DISABLE_THINKING`,
provider-specific `GRAPHIFY_{GEMINI,DEEPSEEK,OPENAI,AZURE,BEDROCK}_MODEL`,
`GRAPHIFY_CLAUDE_CLI_MODEL`, `_PARALLEL`,
`GRAPHIFY_OLLAMA_{KEEP_ALIVE,NUM_CTX,PARALLEL,VISION}`,
`GRAPHIFY_TRIAGE_{BACKEND,MODEL}`, and
`GRAPHIFY_WHISPER_{MODEL,PROMPT}`. Workspace/hook controls are
`GRAPHIFY_GOOGLE_WORKSPACE`, `_TIMEOUT`, `GRAPHIFY_HOOK_STRICT`,
`GRAPHIFY_HOOK_STRICT_TTL`, `GRAPHIFY_SKIP_HOOK`,
`GRAPHIFY_REBUILD_{LOG,TIMEOUT,MEMORY_LIMIT_MB}`,
and `GRAPHIFY_API_KEY`. `GRAPHIFY_CHANGED`, `GRAPHIFY_REPO_ROOT`,
`GRAPHIFY_PYTHON`, and `GRAPHIFY_BIN` are hook/launcher handoff variables;
`GRAPHIFY_OUT_NAME` is an internal constant rather than an operator setting.
Credential and endpoint variable names are inventoried below; no credential
values were inherited, printed, or supplied.

The normalized matrix assigns every named operator variable its own key rather
than treating this inventory as one capability. `GRAPHIFY_OUT`, `FORCE`,
`MAX_WORKERS`, `API_TIMEOUT`, and `VIZ_NODE_LIMIT` are `PARTIAL`: equivalent
CLI/path effects ran, but environment-over-CLI precedence was not isolated for
each. Model/provider/credential controls are individually `RESTRICTED`.
Remaining cache/log/hook/rebuild/handoff controls are individually `UNTESTED`
with the exact missing A/B prerequisite: a fixture whose observable state
distinguishes that single variable. No bundled probe is used to promote an
individual environment control to `VERIFIED`.

### Additional safe-mode probes

One combined isolated extraction exercised every previously untested safe
offline extraction flag:

```text
--code-only --no-cluster --force --allow-partial --no-gitignore
--exclude docs --max-workers 1 --token-budget 1000 --max-concurrency 1
--api-timeout 10 --resolution 0.75 --exclude-hubs 0.9 --timing
```

It exited 0 in 0.17 s with 41,824 KiB peak RSS and wrote 108 nodes/177
edges without communities. `--exclude docs` removed
`docs/architecture.md`; `README.md` remained the one document skipped by
`--code-only`. `--allow-partial` was accepted but no partial condition
occurred. The semantic token/concurrency/timeout controls were dormant in
code-only mode, so their parser acceptance is verified but their model-side
effect is not.

DFS with explicit `call` context returned three nodes in 0.15 s. A repeated
`import`+`references` context filter with a 250-token budget returned 25
matches but truncated display to nine in 0.16 s. Repeated affected relations
at depth 1 returned eight nodes, while calls+references+imports at depth 4
returned ten, demonstrating the reach control. Isolated `global list` and
`global path` completed read-only against empty lane-local homes. Evidence:
`extract-safe-flags.txt`, `query-dfs-context-budget.txt`,
`query-multi-context-budget.txt`, `affected-relation-depth.txt`, and
`global-read-only.txt`.

In a separate isolated home, `provider list` printed “No custom providers
registered.” and exited 0 in 0.05 s. It created only the lane-local
`~/.graphify/` parent directory, not `providers.json`. `provider show
missing-provider` printed a not-found diagnostic and exited 1 in 0.05 s. A
lane-local `providers.json` was then preseeded with a non-secret
`offline-fixture` record whose endpoint was an unbound loopback port and whose
named environment key was unset. `provider show offline-fixture` printed the
record and exited 0 in 0.04 s; the file hash was identical before and after,
and no provider/model/endpoint was activated. These read/failure paths are
`VERIFIED`. A second disposable-home probe verified add/list/show/remove with
the same non-secret, unbound-loopback configuration. Real-home mutation and
backend activation remain `RESTRICTED`. Evidence: `provider-read-only.txt` and
`safe-state-mutations.txt`.

The same state-mutation probe verified lane-local `global add/list/remove`
(108 nodes added, then pruned) and a full `hook
status/install/status/uninstall/status` lifecycle in a disposable fixture.
The hook copy ended with clean Git status. These isolated lifecycles are
`VERIFIED`; applying them to the live repository or real user home remains
`RESTRICTED`.

Safe flag probes closed the remaining local effect gaps. Two no-label/no-viz
`cluster-only` runs jointly exercised resolution, hub exclusion, minimum
community size, and timing controls and each produced 52 communities. Because
the selected low/high combinations produced the same count, `--resolution`,
`--exclude-hubs`, and `--min-community-size` are individually `PARTIAL`:
parser acceptance is proven, causal effect is not. Directed and undirected diagnostics,
example limiting, producer-source extraction, and the mutually exclusive mode
error behaved as advertised. Custom tree controls produced an 18,860-byte
artifact; HTML node limiting produced a 10-community-node aggregate and
`--no-viz` left no HTML; explicit and automatic call-flow section controls
produced bounded outputs. Evidence: `safe-flag-probes.txt`.

Generic project-scoped installation was exercised in 19 independent fixture
copies: `claude`, `windows`, `codebuddy`, `codex`, `opencode`, `aider`, `amp`,
`agents`, `claw`, `droid`, `trae`, `trae-cn`, `gemini`, `cursor`,
`antigravity`, `hermes`, `kiro`, `pi`, and `devin`. Every install and
uninstall command exited successfully, but cleanup was complete for only 13.
Claude/Windows, Codex, Gemini, and OpenCode left empty or hook-config residue;
CodeBuddy left the complete project skill tree because its generic uninstall
path did not preserve project scope. Project installation is therefore
`PARTIAL`, not cleanly reversible. Evidence: `project-install-matrix.txt`.

A second timed sweep repeated those 19 project lifecycles, exercised all 19
generic user-scope installers, and exercised 21 direct dispatcher targets.
That closes the missing Copilot, Kilo, and VS Code direct paths. Each command
records elapsed time and peak RSS plus post-install/post-uninstall snapshots.
The generic user-scope parser accepts `--platform`, but `uninstall_all()` does
not use the parsed selector; 15 rows retained Graphify artifacts and are
classified `BROKEN` individually. Claude `--strict` registered the strict read
hook. The first purge control intentionally placed a sentinel at the default
project path and showed that the wrapper's absolute `GRAPHIFY_OUT` wins; the
corrected probe placed the sentinel at that configured output and verified its
deletion. Evidence: `direct-platform-probes.txt`, `user-install-matrix.txt`,
`project-install-timing-matrix.txt`, `strict-and-purge-probes.txt`, and
`purge-configured-out-probe.txt`.

Ignore handling was tested with root and nested `.graphifyignore` files, a
`.gitignore`-excluded file, negations, and `--no-gitignore`.
`.graphifyignore` exclusions remained effective with or without Git-ignore
processing, and nested negation worked. However, a `.graphifyignore` negation
re-included the file excluded by `.gitignore` in default mode. That contradicts
the maintained README claim that `.graphifyignore` only excludes more and
never re-includes Git-ignored files, so ignore semantics are `PARTIAL`.
Evidence: `graphifyignore-probes.txt`.

### Extraction modes and backends

The verified offline lane used `extract PATH --code-only`. The following
advertised variants were inventoried but not activated:

| Variant | Requirement/effect | Probe result | Disposition |
| --- | --- | --- | --- |
| semantic docs/papers/images and `--mode deep` | configured model backend; corpus leaves the process for remote backends | not activated | `RESTRICTED` |
| `--backend`/`--model` | Gemini, Kimi, Claude, OpenAI, DeepSeek, Ollama, Azure, Bedrock, or custom provider | not activated | `RESTRICTED` |
| `--google-workspace` | `gws` export/network and generated sidecars | not activated | `RESTRICTED` |
| `--postgres DSN` | live external PostgreSQL schema introspection | not activated | `RESTRICTED` |
| `--cargo` | local Cargo manifest introspection | works at crate root but not mixed fixture root | `PARTIAL` |
| `--no-cluster` | raw graph without community analysis | produced 108 nodes/177 edges without communities in the safe-flags extraction | `VERIFIED` |
| `--force` | bypasses manifest/semantic-cache reads | emitted the full-rescan notice in the safe-flags extraction | `VERIFIED` |
| `--allow-partial` | permits guarded partial output | parser accepted it, but no partial-build condition was safely induced | `UNTESTED` |
| `--no-gitignore`, excludes | changes corpus selection | `--no-gitignore` was accepted and `--exclude docs` removed `docs/architecture.md` | `VERIFIED` |

`--cargo` at the mixed fixture root failed because it looked for
`<scan-root>/Cargo.toml`, while the fixture manifest is
`rust/policy/Cargo.toml`. Pointing the same public operation at
`rust/policy/` succeeded and added a `fixture-policy` crate concept, producing
14 nodes and 15 edges. This makes the capability root-sensitive rather than a
recursive nested-manifest discovery feature.

## MCP inventory

The isolated environment does not contain `mcp` or `starlette`.
`graphify-mcp --help` works because argument parsing does not import the
transport, but starting stdio raises:

```text
ImportError: mcp not installed. Run: pip install "graphifyy[mcp]"
```

Therefore runtime `initialize`, `tools/list`, `resources/list`,
`prompts/list`, resource reads, server instructions, and call behavior are
`UNAVAILABLE` at this frozen environment. They are not reported as
runtime-verified.

Static source registration contains 10 tools:

1. `query_graph`
2. `get_node`
3. `get_neighbors`
4. `get_community`
5. `god_nodes`
6. `graph_stats`
7. `shortest_path`
8. `list_prs`
9. `get_pr_impact`
10. `triage_prs`

Every schema also receives optional `project_path`. The first seven are local
graph operations; the final three require GitHub/`gh` access. Static
registration contains six resources:

- `graphify://report`
- `graphify://stats`
- `graphify://god-nodes`
- `graphify://surprises`
- `graphify://audit`
- `graphify://questions`

No prompt handlers or server-instruction string are registered. The canonical
serialized source-registered tool array is 5,798 bytes and 1,234
`o200k_base` tokens. These are schema-overhead estimates, not provider usage.

### Complete MCP tool schemas and behavior

Every tool also accepts optional string `project_path`, which resolves
`<project_path>/<GRAPHIFY_OUT>/graph.json`; omission uses the server default.
All successful tool calls return one MCP `TextContent`. Local handlers can
hot-reload a graph when its mtime/size changes. Runtime dispositions remain
`UNAVAILABLE` because importing the MCP server fails before initialization;
the following is frozen source-registration/handler evidence from
`mcp-source-registry.json`, `mcp-item-metrics.json`, and `serve.py`.

| Tool | Required; optional/default/enum inputs | Text output and effects | Full tool bytes/tokens; input-schema bytes/tokens | Disposition |
| --- | --- | --- | ---: | --- |
| `query_graph` | required `question`; `mode=bfs` enum `bfs|dfs`; `depth=3` (handler caps maximum at 6); `token_budget=2000`; string-array `context_filter`; `project_path` | source schema/handler verified: node/edge context text; local graph read, optional plaintext query log, no network | 901/201; 753/173 | `UNAVAILABLE` |
| `get_node` | required `label`; `project_path` | source schema/handler verified: first substring/exact-ID match with ID/source/type/community/degree; local read | 413/88; 310/66 | `UNAVAILABLE` |
| `get_neighbors` | required `label`; optional `relation_filter`; `token_budget=2000`; `project_path` | source schema/handler verified: incoming/outgoing neighbors, relations, confidence and relation-site, budget-truncated; local read | 544/113; 435/92 | `UNAVAILABLE` |
| `get_community` | required integer `community_id`; `token_budget=2000`; `project_path` | source schema/handler verified: community header and member/source list, budget-truncated; local read | 514/110; 413/89 | `UNAVAILABLE` |
| `god_nodes` | `top_n=10`; `project_path` | source schema/handler verified: degree-ranked hub text; local read | 390/80; 259/55 | `UNAVAILABLE` |
| `graph_stats` | only optional `project_path` | source schema/handler verified: nodes, edges, communities, and confidence percentages; local read | 358/69; 219/44 | `UNAVAILABLE` |
| `shortest_path` | required `source`, `target`; `max_hops=8`; `project_path` | source schema/handler verified: deterministic undirected path with stored relation/confidence, ambiguity/max-hop diagnostics; local read | 606/124; 483/101 | `UNAVAILABLE` |
| `list_prs` | optional `base`, `repo`, `project_path` | source schema/handler verified: formatted open PR/CI/review/worktree/graph-impact text; additionally requires Git/`gh`, network, and auth | 673/146; 409/90 | `UNAVAILABLE` |
| `get_pr_impact` | required integer `pr_number`; optional `repo`, `project_path` | source schema/handler verified: PR metadata, changed files (first 20), touched communities/nodes; additionally requires GitHub network/auth | 684/143; 405/87 | `UNAVAILABLE` |
| `triage_prs` | optional `base`, `repo`, `project_path` | source schema/handler verified: actionable PR ranking; additionally requires GitHub network/auth | 704/158; 409/90 | `UNAVAILABLE` |

Schema descriptions mention ranges, but JSON Schema does not encode minimum or
maximum constraints for `depth`, `token_budget`, `top_n`, or `max_hops`.
Handlers coerce integers; only query depth is explicitly capped at 6. The
three PR tools are read-only with respect to repositories but are not offline:
they invoke Git/`gh` and GitHub.

### Complete MCP resources and transport configuration

Resources have no input schema and always use the server's default graph rather
than `project_path`.

| Resource | MIME; returned content/effects | Registration bytes/tokens | Disposition |
| --- | --- | ---: | --- |
| `graphify://report` | source registration verified: Markdown reads sibling `GRAPH_REPORT.md`, or returns a missing-report diagnostic | 113/27 | `UNAVAILABLE` |
| `graphify://stats` | source registration verified: text with the same local counters as `graph_stats` | 139/30 | `UNAVAILABLE` |
| `graphify://god-nodes` | source registration verified: text with local top-10 degree ranking | 117/30 | `UNAVAILABLE` |
| `graphify://surprises` | source registration verified: text computes top-10 cross-community connections or diagnostic | 141/28 | `UNAVAILABLE` |
| `graphify://audit` | source registration verified: text with exact confidence counts/percentages | 136/36 | `UNAVAILABLE` |
| `graphify://questions` | source registration verified: text with suggested questions from graph/community labels or diagnostic | 137/28 | `UNAVAILABLE` |

The resource registration array is 790 bytes/176 `o200k_base` tokens. There
are zero MCP prompts and no server instructions.

`graphify-mcp` accepts positional `graph_path` or alias `--graph`;
`--transport` enum `stdio|http` (default `stdio`); HTTP `--host`
(`127.0.0.1`), `--port` (8080), `--path` (`/mcp`), `--api-key` or
`GRAPHIFY_API_KEY`, `--json-response`, `--stateless`, and
`--session-timeout` (3600 seconds; 0 disables reaping; ignored in stateless
mode). HTTP is MCP Streamable HTTP, not the older SSE transport;
`--json-response` selects plain JSON responses instead of SSE-formatted
streams within Streamable HTTP. API-key auth accepts `X-API-Key` or Bearer
headers with constant-time comparison; OAuth is absent. A wildcard bind
without a key warns that the graph is exposed, while specific-host binds apply
DNS-rebinding host checks. Both transports require `mcp`; HTTP additionally
requires Starlette and Uvicorn. All are `UNAVAILABLE` in the isolated frozen
environment.

## Languages, files, entities, and relationships

Runtime source registries contain:

- 94 extensions classified as code by detection;
- 95 extension-to-extractor entries, including Markdown-family structural
  extractors;
- 46 distinct registered extractor functions;
- 14 extensionless shebang interpreter names;
- 9 document extensions, 1 paper extension, 6 image extensions, 2 office
  extensions, and 10 video/audio extensions.

The complete detected code-extension set is:

```text
.F .F03 .F08 .F90 .F95 .astro .bash .c .cc .cjs .cls .cpp .cs
.cshtml .csproj .cts .cu .cuh .cxx .dart .dfm .dm .dme .dmf .dmi
.dmm .dpk .dpr .ejs .ets .ex .exs .f .f03 .f08 .f90 .f95 .fsproj
.go .gradle .groovy .h .hcl .hpp .inc .java .jl .js .json .jsx .kt
.kts .lfm .lpk .lpr .lua .luau .m .metal .mjs .mm .mts .pas .php
.pp .ps1 .psd1 .psm1 .py .r .rake .razor .rb .rs .scala .sh .sln
.slnx .sql .sv .svelte .svh .swift .tf .tfvars .toc .trigger .ts
.tsx .v .vbproj .vue .xaml .zig
```

The declared non-code sets are documents
`.html .md .mdx .qmd .rst .skill .txt .yaml .yml`; paper `.pdf`;
images `.gif .jpeg .jpg .png .svg .webp`; office `.docx .xlsx`; and
video/audio `.avi .m4a .m4v .mkv .mov .mp3 .mp4 .ogg .wav .webm`.
The closed detector `FileType` enum is `code`, `document`, `paper`, `image`,
and `video`; unsupported/unclassified files receive no type. Office and Google
Workspace shortcuts are converted before routing rather than adding enum
members.

The sets are not identical. Detection includes `.ejs`, `.ets`, and `.r`, but
the extractor dispatcher has no corresponding handler. Conversely, the
dispatcher structurally parses `.md`, `.mdx`, `.qmd`, and `.skill`, which are
classified as documents. This registry mismatch is a real filename-filter risk
and means “detected as code” is not equivalent to “produces AST nodes.”

SQL, Terraform/HCL, and DreamMaker extensions have optional parser extras.
Pascal has a documented fallback. Filename-aware extraction recognizes the
exact MCP configuration basenames `.mcp.json`, `claude_desktop_config.json`,
`mcp.json`, and `mcp_servers.json`, and the package manifests `apm.yml`,
`apm.yaml`, `pyproject.toml`, `go.mod`, and `pom.xml` before generic suffix
routing. An isolated 28-file/133-node/197-edge extraction verified all nine
routes. It also verified the special `.blade.php` route by observing
`binds_method`, `includes`, and `uses_component` relationships. Evidence:
`filename-routing-probes.txt`.

The 95-extension dispatch uses 46 extractor functions across Python;
JS/TS; C/C++/CUDA/Metal; Java/Groovy; C#; Go; Rust; Ruby; Swift; Kotlin;
Scala; PHP; Lua; Objective-C; Elixir; Julia; Vue; Svelte; Astro; Dart; Zig;
PowerShell; Fortran; Verilog; SQL; Pascal/Lazarus/Delphi; Bash; JSON;
Terraform; DreamMaker; solution/project formats; XAML; Razor; Apex; and
structural Markdown. The complete extension/function lists are retained in
`language-registry.json`. Extensionless dispatch supports
`bash dash julia ksh lua node nodejs php python python2 python3 ruby sh zsh`.
SQL requires the `sql` extra; Terraform/HCL requires `terraform`; `.dm/.dme`
requires `dm`. `.h` is content-sniffed among C, C++, and Objective-C; `.m`
is parsed only when Objective-C markers are present.

Graphify does not emit a closed, stable symbol-kind field. The declared model
`file_type` vocabulary extends the detector enum with `rationale` and
`concept`; manifest ingestion can attach `type=package`, and C# extraction can
attach namespace metadata. Across producers, nodes can encode files,
packages/crates/modules/namespaces, classes/interfaces/traits/structs/enums/
unions/type aliases, functions/methods/constructors/operators/procedures,
fields/properties/constants/variables/parameters, document headings,
rationale/concept nodes, MCP servers/commands/env requirements, and database
schema objects. These are producer categories, not a validated closed `kind`
enum. Source paths and `L<number>` locations are common but not universal.

The frozen source-declared literal relation vocabulary is:

```text
binds_method bound_to calls cites contains crate_depends_on defines depends_on
dynamic_import embeds extends implements imports imports_from includes
indirect_call inherits instantiates listened_by method mixes_in rationale_for
re_exports references references_constant requires_env uses uses_component
uses_static_prop
```

Model semantic extraction additionally prompts for
`conceptually_related_to`, `shares_data_with`, and
`semantically_similar_to`; hyperedge suggestions are `participate_in`,
`implement`, and `form`. Relation is nevertheless an open string field:
extractors can assign it through variables, semantic input is not constrained
by one global relation enum, and export normalization accepts arbitrary text.
The list above is a frozen producer inventory, not a forward-compatible closed
enum.

The fixture's observed runtime relation set was:

- `calls` (10)
- `contains` (60)
- `extends` (2)
- `implements` (4)
- `imports` (31)
- `imports_from` (20)
- `inherits` (2)
- `method` (23)
- `references` (21)

Confidence was 172 `EXTRACTED`, 1 `INFERRED`, and 0 `AMBIGUOUS`. Source and
semantic extractors can emit additional relations, so this observed set is not
a closed global enum.

## Fixture extraction and manifest audit

The main command was:

```bash
/usr/bin/time -v env \
  CODE_INTEL_EXTRA_PATH=scratchpad/code-intelligence/tools/graphify/.venv-harness/bin \
  docs/research/harness-tools/codebase-intelligence/experiments/coding-agents/run-isolated.sh \
  graphify-capability \
  graphify extract scratchpad/code-intelligence/fixtures/graphify \
  --code-only --out scratchpad/code-intelligence/indexes/graphify/fixture --timing
```

Observed build evidence:

| Measure | Value |
| --- | ---: |
| Wall time | 0.32 s (`time -v`); Graphify stage total 0.2 s |
| Peak RSS | 62,152 KiB |
| Classified code files | 18 |
| Non-code skipped by `--code-only` | 2 documents |
| Unclassified skipped | 5 |
| Nodes | 108 |
| Edges | 173 |
| Communities | 10 |
| Graph-output directory | 143,288 bytes before later exports |
| `graph.json` | 95,965 bytes |
| Model tokens | 0 input / 0 output |

All 18 files in `manifest.json` appear in the graph's source-file set:
TypeScript sources, two Rust sources, three `package.json` files, and
`tsconfig.json`. The five explicit unclassified skips were
`.fixture-manifest.digest`, `.fixture-source.sha256`, nested `Cargo.toml`,
`unsupported/legacy.capfixture`, and `synthetic-change.patch`. The two
code-only document skips were `README.md` and `docs/architecture.md`.

This is a strong skipped-file audit because the CLI names the unknown
`legacy.capfixture`; absence was not inferred from an empty query. It also
shows that nested `Cargo.toml` is invisible to the normal code-only graph unless
the separate root-sensitive Cargo operation is used.

## Query quality and limitations

### Architecture and lifecycle

The broad lifecycle query returned the major types and many import/type
relationships. Exact-ID path found:

```text
handleRequest() --calls [EXTRACTED]--> .run()
  --calls [EXTRACTED]--> .publish()
```

This is useful orientation, but it is not the complete request lifecycle.
Graphify did not return a single resolved path covering validation,
authorization, dynamic handler selection, execution, every state write, and
event delivery. In particular, object-literal construction and several member
calls are not represented as constructor/data-flow facts. The graph-only answer
must therefore be partial and explicit about missing causal links.

### Name collision

Two distinct stable IDs exist:

- `packages_core_src_normalize_normalize`
- `packages_gateway_src_normalize_normalize`

Exact-ID `explain` correctly returned different callers:
`BaseHandler.execute` for core normalization and `handleRequest` for gateway
normalization. However, `explain normalize` silently selected the core symbol,
and `query "normalize callers"` seeded only that binding. There was no
ambiguity warning. Stable IDs preserve the distinction, while label-only
lookup is `PARTIAL` for collision-sensitive investigation.

### Impact/change

`affected WorkResult --depth 4` returned imports and type references including
handlers, `execute`, store, `save`, `history`, workflow, `run`, router, and
`handleRequest`. It did not identify the three object-literal constructors
changed by `synthetic-change.patch`, nor distinguish constructors from
consumers. Graphify's `affected` is a graph reverse traversal, not patch-aware
semantic change analysis.

### Dynamic and cross-language ambiguity

The graph represents TypeScript launcher/policy nodes and the independent Rust
crate, but it has no statically resolved TypeScript-to-Rust call edge. That is
the correct place to abstain: runtime command selection and a delimiter
protocol are not a source-level symbol call. Graphify also cannot prove the
boundary merely from the disconnected AST graph.

### Missing/failure behavior

An unknown `explain` label and impossible path returned a concise “No node
matching” message but exited 0. This is friendly for interactive use, but
automation must inspect content rather than relying on the process exit code.
`diagnose multigraph` was read-only and reported no missing/dangling endpoints,
self loops, exact duplicates, or endpoint-collapse groups.

## Incremental update result

The frozen patch changed `WorkResult` and three result object literals. Public
`graphify update` succeeded:

| Measure | Pre-update | Post-update |
| --- | ---: | ---: |
| Nodes | 108 | 112 |
| Edges | 173 | 175 |
| Communities | 10 | 11 |
| Update wall time | — | 0.20 s |
| Peak RSS | — | 42,772 KiB |

The added nodes were the structurally parsed `README.md` and
`docs/architecture.md` content. `update` deliberately includes documents with
AST extractors, so it did not preserve the original `--code-only` corpus. It
also rewrote stored source paths from fixture-root-relative paths such as
`packages/core/src/contracts.ts` to parent-repo-relative paths beginning
`scratchpad/code-intelligence/fixtures/graphify/...` under this relative-root,
external-output invocation. The query then emitted a legacy-ID warning.

No `attempts` node appeared, and pre/post impact queries did not reveal the
changed object-literal fields. The operation is therefore mechanically
functional but `PARTIAL` for this study's strict stale-index/change contract.
The post-update graph was retained separately, the patch was reversed, and the
fixture returned to its frozen clean state.

Two fresh lane-local fixture copies and output trees then isolated the update
flags from that synthetic-change run:

| Variant | Baseline | Result | Elapsed / peak RSS | Disposition |
| --- | --- | --- | --- | --- |
| `update --force` (continuity lane) | 108 nodes, 173 edges, 10 communities | 112 nodes, 175 edges, 11 communities; regenerated graph, HTML, report, and labels; this lane did not induce shrink | 0.22 s / 43,044 KiB | `VERIFIED` |
| `update --no-cluster` | 108 nodes, 173 edges, 10 communities | 112 nodes, 179 edges, zero assigned communities; no HTML, report, or labels | 0.20 s / 41,920 KiB | `VERIFIED` |

Both variants retained the same update limitation: they reintroduced
`README.md` and `docs/architecture.md` into the code-only baseline and rewrote
source paths to lane-relative parent-repository paths. Both fixture copies
remained clean at commit
`e7ddad2c44321f7b50e60c923b8f0733fb757874`. Evidence:
`update-force.txt` and `update-no-cluster.txt`.

A further isolated work-copy probe induced a real shrink by adding a
disposable TypeScript file, extracting a 127-node/203-edge graph, deleting the
file, and updating:

| Shrink variant | Before | After | Elapsed / peak RSS | Observed behavior |
| --- | --- | --- | --- | --- |
| unflagged `update` | 127 nodes, 203 edges, 10 communities | 112 nodes, 175 edges, 11 communities | 0.23 s / 42,988 KiB | exited 0 and removed all 19 disposable-file nodes; no refusal |
| `update --force` | 127 nodes, 203 edges, 10 communities | 112 nodes, 175 edges, 11 communities | 0.23 s / 43,192 KiB | exited 0, removed the same 19 nodes, and emitted curated-graph backup output |

Thus both variants overwrite a smaller rebuilt graph at this frozen revision.
`--force` is accepted and exercises force/backup plumbing, but it was not
required for the tested shrink. This conflicts with the distinction implied by
the top-level help text (“overwrite even if fewer nodes”), so the behavior is
`PARTIAL`, not inferred force-only protection. The work copy
ended clean at the frozen fixture commit with the final 112/175/11 graph.
Evidence: `update-force-shrink.txt`.

## Optional dependencies and restricted surfaces

Installed in the isolated environment: core Graphify, NetworkX, tree-sitter and
the default language parsers. The complete extra registry was frozen from
`pyproject.toml` and checked against `importlib.metadata`; requirements whose
markers do not apply to Python 3.12 are retained explicitly.

| Extra | Exact frozen requirements | Availability and capability effect | Disposition |
| --- | --- | --- | --- |
| `mcp` | `mcp`; `starlette>=1.3.1` | both absent; server startup fails before initialize | `UNAVAILABLE` |
| `neo4j` | `neo4j` | absent; local Cypher export works, client-backed push does not | `UNAVAILABLE` |
| `falkordb` | `falkordb` | absent; local OpenCypher export works, client-backed push does not | `UNAVAILABLE` |
| `pdf` | `pypdf>=6.12.0`; `markdownify` | both absent; PDF/HTML-to-Markdown conversion unavailable | `UNAVAILABLE` |
| `watch` | `watchdog` | absent; `watch` unavailable | `UNAVAILABLE` |
| `svg` | `matplotlib`; `numpy>=2.0; python_version >= '3.13'` | matplotlib absent; NumPy 2.5.0 is installed transitively but its extra marker does not apply on Python 3.12 | `UNAVAILABLE` |
| `leiden` | `graspologic; python_version < '3.13'` | applicable dependency absent; default core clustering still works | `UNAVAILABLE` |
| `office` | `python-docx`; `openpyxl` | both absent; DOCX/XLSX conversion unavailable | `UNAVAILABLE` |
| `google` | `openpyxl` | absent; Workspace export also requires external `gws` and network | `UNAVAILABLE` |
| `postgres` | `psycopg[binary]` | absent; schema introspection also requires a reachable DSN | `UNAVAILABLE` |
| `video` | `faster-whisper; python_version >= '3.11'`; `yt-dlp>=2026.6.9` | both applicable dependencies absent; media download/transcription unavailable | `UNAVAILABLE` |
| `kimi` | `openai`; `tiktoken` | both absent; Kimi backend also requires service credentials/network | `UNAVAILABLE` |
| `ollama` | `openai` | absent; backend also requires a running compatible service | `UNAVAILABLE` |
| `bedrock` | `boto3` | absent; backend also requires AWS credentials, region, entitlement, and network | `UNAVAILABLE` |
| `anthropic` | `anthropic` | absent; API backend also requires credentials/network | `UNAVAILABLE` |
| `gemini` | `openai`; `tiktoken` | both absent; backend also requires credentials/network | `UNAVAILABLE` |
| `openai` | `openai`; `tiktoken` | both absent; OpenAI/DeepSeek/Azure/custom-compatible paths also require endpoint credentials/network | `UNAVAILABLE` |
| `chinese` | `jieba` | absent; enhanced Chinese segmentation unavailable | `UNAVAILABLE` |
| `sql` | `tree-sitter-sql` | absent; SQL AST extraction unavailable | `UNAVAILABLE` |
| `pascal` | `tree-sitter-pascal` | absent; enhanced parser unavailable, while the documented fallback remains | `UNAVAILABLE` |
| `dm` | `tree-sitter-dm` | absent; DreamMaker AST extraction unavailable | `UNAVAILABLE` |
| `terraform` | `tree-sitter-hcl` | absent; Terraform/HCL AST extraction unavailable | `UNAVAILABLE` |
| `all` | union of the declared extras above | packaging meta-extra, not an independent runtime capability | `NOT APPLICABLE` |

The exact package objects, marker applicability, installed versions, and
distribution names are in `optional-extras-registry.json`. `UNAVAILABLE`
describes the frozen environment. Where a capability would additionally send
data to a model, database, workspace, or media endpoint after installation,
that activation is also `RESTRICTED` by this experiment's safety boundary.

The complete frozen headless semantic-backend prerequisite map below
reconciles `pyproject.toml`, `graphify.llm.BACKENDS`, dispatch, maintained
README guidance, and backend/provider tests. Variable names are evidence; no
secret values, endpoints, services, or model calls were activated.

| Backend | Package/extra | Credential and endpoint configuration | Service prerequisite | Disposition |
| --- | --- | --- | --- | --- |
| Gemini | `graphifyy[gemini]` → `openai`, `tiktoken` | `GEMINI_API_KEY` or `GOOGLE_API_KEY`; optional `GEMINI_BASE_URL`, `GRAPHIFY_GEMINI_MODEL` | Google OpenAI-compatible endpoint by default, or an explicitly configured compatible endpoint | `RESTRICTED` |
| Kimi | `graphifyy[kimi]` → `openai`, `tiktoken` | `MOONSHOT_API_KEY`; optional `KIMI_BASE_URL`; model override is `--model` | Moonshot OpenAI-compatible endpoint by default, or an explicitly configured compatible endpoint | `RESTRICTED` |
| Claude API | `graphifyy[anthropic]` → `anthropic` | `ANTHROPIC_API_KEY`; optional `ANTHROPIC_BASE_URL`, `ANTHROPIC_MODEL` | Anthropic API by default, or an Anthropic-compatible endpoint | `RESTRICTED` |
| Claude CLI | no Python extra; `claude` executable on `PATH` | optional `GRAPHIFY_CLAUDE_CLI_MODEL` | installed/authenticated Claude Code subscription | `RESTRICTED` |
| OpenAI | `graphifyy[openai]` → `openai`, `tiktoken` | `OPENAI_API_KEY`; optional `OPENAI_BASE_URL`, `OPENAI_MODEL`, `GRAPHIFY_OPENAI_MODEL` | OpenAI API or running OpenAI-compatible service; local services still need a non-empty client key value | `RESTRICTED` |
| DeepSeek | no dedicated extra; OpenAI-compatible dispatch needs `openai` from `graphifyy[openai]` | `DEEPSEEK_API_KEY`; optional `DEEPSEEK_BASE_URL`, `GRAPHIFY_DEEPSEEK_MODEL` | DeepSeek API by default, or an explicitly configured OpenAI-compatible endpoint | `RESTRICTED` |
| Ollama | `graphifyy[ollama]` → `openai` | optional `OLLAMA_API_KEY`; `OLLAMA_BASE_URL` or `OLLAMA_HOST`; optional `OLLAMA_MODEL` and `GRAPHIFY_OLLAMA_*` tuning | running Ollama OpenAI-compatible service, loopback port 11434 by default; missing API key uses a visible sentinel warning | `RESTRICTED` |
| Azure OpenAI | README calls this the Azure capability, but `pyproject.toml` declares no `azure` extra; install `graphifyy[openai]` | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`; optional `AZURE_OPENAI_API_VERSION`, `AZURE_OPENAI_DEPLOYMENT`, `GRAPHIFY_AZURE_MODEL` | reachable Azure OpenAI resource and deployment | `RESTRICTED` |
| AWS Bedrock | `graphifyy[bedrock]` → `boto3` | standard AWS credential chain/`AWS_PROFILE`; optional `AWS_REGION`, `AWS_DEFAULT_REGION`, `GRAPHIFY_BEDROCK_MODEL` | AWS access, region, Bedrock model entitlement, reachable Bedrock Runtime | `RESTRICTED` |
| Custom OpenAI-compatible | no dedicated extra; needs `openai` from `graphifyy[openai]` | provider-defined `env_key`, `base_url`, and `default_model` in global or project config; project-local loading requires `GRAPHIFY_ALLOW_LOCAL_PROVIDERS=1` | reachable configured endpoint, which receives corpus content and its configured key | `RESTRICTED` |

The machine-readable counterpart is `backend-prerequisites.json`. The source
has two noteworthy packaging mismatches: DeepSeek has no named extra despite
using the OpenAI-compatible client, and the README names an Azure capability
whose install path is the `openai` extra rather than a declared `azure` extra.

Graphify's query log is opt-in and was not enabled. Query/path/explain still
write `cache/last_query_stamp` next to the graph. Source describes plaintext
query/response logging under an explicit `GRAPHIFY_QUERY_LOG` or enable flag,
with a disable flag taking precedence. The isolated run exposed no telemetry or
provider credentials, and the code-only lane made no observed network calls.

## Capability evidence, cost, and agent applicability

`artifact-item-metrics.json` mechanically measures UTF-8 bytes and local
`o200k_base` tokens for every retained TXT/JSON evidence artifact. The
bytes/tokens below are sums of the named evidence bundle, not necessarily raw
stdout alone and never provider usage. Elapsed time is `UNKNOWN` only where the
retained artifact has no explicit timing field; filesystem timestamps are not
substituted. Provider tokens and local artifact estimates stay separate.
The sole authoritative aggregate generator is `measure-artifacts.js`; it reads
only the repo-relative inputs and SHA-256 values frozen in
`evidence-input-manifest.json`, failing on missing, changed, or unlisted
TXT/JSON evidence. It writes `artifact-metrics.json`,
`artifact-item-metrics.json`, and `generated-output-metrics.json`.
`test-measure-artifacts-idempotence.js` executes that generator twice and
requires all three outputs to be byte-identical with unchanged counts. Scripts,
generated summaries (including `normalized-capability-matrix.json`), and
idempotence output are excluded by construction. The
stale alternate aggregate generator was removed; `measure-mcp-items.mjs`
remains a separate, MCP-schema-only measurement utility rather than an
aggregate generator.

| Capability | Primary evidence | Timing; output bytes; local o200k tokens; model tokens | Pi / Codex applicability | Main limitation |
| --- | --- | --- | --- | --- |
| clustered code-only extraction | `extract-code-only.txt`, `graph-summary.json`, `runtime-manifest.json` | 0.32 s; evidence 7,200 bytes/2,534 tokens; generated tree 143,288 bytes, graph 95,965; provider 0/0 | CLI usable by both | structural AST graph, incomplete dynamic/data flow |
| safe extract flags/no-cluster | `extract-safe-flags.txt` | 0.17 s; evidence 1,465 bytes/409 tokens; provider 0/0 | CLI usable by both | semantic tuning dormant; allow-partial failure behavior untested |
| BFS query | `query-lifecycle.txt`, `query-normalize.txt`, timed rerun | 0.13 s; evidence 11,301 bytes/2,929 tokens plus shared timing ledger; provider 0/0 | strong orientation primitive for both | label collision and approximate token budget |
| DFS/context/budget query | `query-dfs-context-budget.txt`, `query-multi-context-budget.txt` | 0.15/0.16 s; evidence 1,072 bytes/304 tokens; provider 0/0 | usable by both | 250-token output truncated 16/25 nodes |
| explain/path | six success/boundary artifacts plus timed rerun | 0.11/0.11 s; evidence 1,498 bytes/418 tokens plus shared timing ledger; provider 0/0 | usable by both; exact IDs recommended | missing targets exit 0; label-only first match |
| affected variants | `affected-workresult.txt`, `affected-relation-depth.txt` | 0.12-0.13 s where retained; evidence 1,168 bytes/318 tokens; provider 0/0 | useful to both for graph blast radius | not patch-aware; misses object-literal constructors |
| hubs/diagnostics/benchmark | `god-nodes.json`, `diagnose-multigraph.json`, `benchmark.txt`, timed rerun | 0.11/0.12/0.10 s; evidence 4,368 bytes/1,256 tokens plus shared timing ledger; provider 0/0 | local diagnostics usable by both | benchmark is estimate, not measured provider saving |
| cluster-only | `cluster-only.txt`, timed rerun | 0.14 s; evidence 1,322 bytes/383 tokens plus shared timing ledger; provider 0/0 with no-label | usable by both | labels need model; clustering alters graph structure |
| local HTML/tree/wiki/Obsidian/GraphML exports | six export artifacts plus timed rerun | tree/HTML/callflow 0.10 s each; Obsidian 0.11 s; wiki 0.10 s; GraphML 0.17 s; evidence 1,623 bytes/410 tokens plus shared ledger; provider 0/0 | human orientation artifacts for both | derived views; not additional source truth |
| local Cypher exports | `export-neo4j.txt`, `export-falkordb.txt`, timed rerun | Neo4j/FalkorDB 0.10/0.10 s; evidence 444 bytes/116 tokens plus shared ledger; generated scripts 35,136 bytes each; provider 0/0 | usable by both without push | DB push restricted |
| SVG export | `export-svg.txt` | failed before generated output; evidence 1,241 bytes/322 tokens; provider 0 | unavailable to both frozen lanes | matplotlib absent |
| memory/reflection | `save-result.txt`, `reflect.txt`, timed rerun | 0.05/0.05 s; evidence 302 bytes/79 tokens plus shared timing ledger; provider 0/0 | persistent hints consumable by both | overlay can contaminate controlled probes |
| graph merge | `merge-graphs.txt`, `merge-driver.txt`, timed rerun | 0.10/0.12 s; evidence 148 bytes/39 tokens plus shared timing ledger; merged graph 122 nodes/188 edges; provider 0/0 | usable by both on disposable copies | union, not semantic reconciliation |
| Cargo introspection | three Cargo artifacts plus timed reruns | mixed root 0.13 s exit 1; crate root 0.19 s exit 0; evidence 4,728 bytes/1,380 tokens plus shared timing ledger; provider 0/0 | usable by both | nested manifest not discovered from mixed root |
| update variants | synthetic, force/no-cluster, and induced-shrink evidence | 0.20/0.22/0.20 s; induced unflagged/forced shrink 0.23/0.23 s; evidence 7,386 bytes/2,104 tokens; provider 0/0 | usable by both through adapter below | code-only/path continuity not preserved; unflagged shrink contradicts help-implied force distinction |
| global registry lifecycle | `global-read-only.txt`, `safe-state-mutations.txt`, timed rerun | list/path 0.10/0.10 s; lifecycle evidence bytes/tokens are included in the aggregate; provider 0/0 | usable by both in an isolated home | real-home use and `extract --global` restricted |
| provider registry lifecycle | `provider-read-only.txt`, `safe-state-mutations.txt` | reads 0.05/0.05/0.04 s; lifecycle evidence bytes/tokens are included in the aggregate; provider 0/0 | safe configuration orientation for both in isolated home | activation and real-home mutation restricted |
| hook and installer lifecycles | `safe-state-mutations.txt`, `direct-platform-probes.txt`, `user-install-matrix.txt`, `project-install-timing-matrix.txt`, strict/purge artifacts | every new install/uninstall records elapsed/RSS; per-artifact bytes/tokens are in the matrix/aggregate; provider 0/0 | disposable integration checks for both | per-key residue classifications expose six direct, 15 generic-user, and six generic-project cleanup failures |
| safe effect flags | `safe-flag-probes.txt`, `flag-routing-timing-probes.txt` | clustering plus diagnose/tree/HTML/callflow reruns retain elapsed/RSS; output bytes/tokens included per row and aggregate; provider 0/0 | bounded local tuning/view checks for both | cluster tuning contributions not individually attributable |
| ignore and filename routing | `graphifyignore-probes.txt`, `filename-routing-probes.txt`, `flag-routing-timing-probes.txt` | three fresh extraction reruns retain elapsed/RSS; output bytes/tokens included per row and aggregate; provider 0/0 | helps both predict corpus boundaries and special routing | `.graphifyignore` can re-include a Git-ignored file contrary to docs |
| optional-extra registry | `optional-extras-registry.json` | static inventory; output bytes/tokens included in aggregate; provider 0 | prerequisite planning for both | every applicable optional runtime dependency is absent |
| MCP tools/resources | three MCP registry/runtime artifacts | no successful runtime timing: startup fails before initialize because declared `graphifyy[mcp]` packages `mcp` and `starlette` are absent; evidence 12,058 bytes/2,900 tokens; tools 5,798/1,234, resources 790/176; model 0 | Pi/Codex can consume MCP when installed/configured | runtime unavailable; PR tools need GitHub |
| semantic backend inventory | `backend-prerequisites.json` | no execution elapsed; evidence 4,672 bytes/1,190 tokens; model 0 | both can invoke CLI when provisioned | credentials/backend/network restricted |
| CLI/host/remote inventory | `help.txt`, `help-command-families.txt` plus source dispatch | full help/version 0.04/0.04 s; help evidence 12,801 bytes/2,923 tokens plus shared timing ledger; model 0 | host installers and remote commands exist | writes/network/auth intentionally restricted |

The shared `timed-safe-operations.txt` ledger supplies the fresh timings cited
above and also records `check-update` 0.05 s and `hook status` 0.04 s. The
current primary deterministic evidence is 78 TXT/JSON files, 361,467 bytes,
and 92,333 local `o200k_base` tokens. Including the current
`artifact-metrics.json` summary itself, the per-item inventory covers 79 files,
364,185 bytes, and 93,088 tokens. Generated summaries, including the normalized
433-row matrix, are excluded from the immutable input manifest. These aggregates include inventories and
diagnostics, not just graph answers, so they are not a measure of prompt
context that Pi or Codex must consume. The generated per-item/output metrics
files and measurement script are excluded from the primary aggregate.

`generated-output-metrics.json` separately enumerates all 475 regular files
under the retained Graphify output roots: 3,696,088 bytes and 1,038,422 local
`o200k_base` tokens. Different retained snapshots are counted separately.
Those token counts measure decodable artifact text; they do not mean the files
were placed into model context. Per-file elapsed is `NOT_APPLICABLE`; elapsed
belongs to the producing command and is reported from command evidence above.

## Safe update adapter requirements

No shared runner was changed. A future Graphify adapter can mediate the public
`update` operation safely if it implements all of these requirements:

1. Copy the frozen fixture into a unique lane-local writable working tree;
   never patch the canonical fixture or live submodule.
2. Verify the frozen fixture manifest digest and source commit before copying,
   then verify the copy before mutation.
3. Seed a fresh lane-local output directory with the accepted baseline
   `graph.json`, `manifest.json`, `.graphify_analysis.json`, build config, and
   required cache only. Exclude `.graphify_learning.json`, memory, query logs,
   and freshness stamps.
4. Accept only the frozen synthetic patch, verify its SHA-256, run `git apply
   --check`, apply it once, and record the patched-file hash delta. Reject
   arbitrary shell, network, merge, commit, or unscoped filesystem operations.
5. Invoke only the public `graphify update WORKING_COPY` command through the
   isolated wrapper with an absolute lane-local `GRAPHIFY_OUT`. Support
   `--force` and `--no-cluster` only when the probe explicitly requests them.
6. Capture exit status, wall time, peak RSS, stdout/stderr, pre/post graph
   counts, relation/confidence counts, manifest, build config, source-file
   spellings, and every output-file byte/token count.
7. Compare the post-update corpus with the baseline contract. Treat
   reintroduced documents, dropped files, changed root/path spelling, graph
   shrink, missing patch anchors, or a legacy-ID warning as explicit partial
   results rather than silently normalizing them.
8. Expose the updated graph read-only to subsequent `query`, exact-ID
   `explain`, `affected`, and `path`; do not let those operations write learning
   memory or query logs. Freshness stamps must remain lane-local.
9. Destroy or retain only the ignored lane copy after the run. Re-verify that
   the canonical fixture, disposable source checkout, and live submodule are
   clean and at frozen revisions.
10. Emit frozen-schema operation records and metrics, including
    `unauthorized_operation`, contamination notes, provider usage, and
    `UNKNOWN` where a measurement truly was not captured.

This adapter does not “fix” Graphify's code-only continuity behavior. It makes
the public behavior safely reproducible and observable.

## Metrics artifacts

Two ignored metrics artifacts validate against `metrics.schema.json`:

- `deterministic-discovery.metrics.json` is `DISCOVERY_SETUP`. Provider usage
  and operation totals are `UNKNOWN`; its 170 ms elapsed value is explicitly
  the final safe-flags completeness probe, not aggregate discovery time. Its
  artifact estimate reflects the 78-file primary deterministic inventory. Its
  current fixture identity is manifest digest
  `fc12b07aa2219f346ee1e00f52875efae8c52bbb12dc410456e9457ea1b58e24`
  at fixture commit `e7ddad2c44321f7b50e60c923b8f0733fb757874`;
  the separate Graphify tool revision remains recorded in `runtime_version`.
- `terra-invalid.metrics.json` is the actual `CAPABILITY_PROBE`, with provider
  usage, 26 tool calls, invalid-schema/call-cap contamination, and 301,000 ms
  elapsed derived from prompt/output filesystem birth times because JSONL
  events carry no timestamps. Its identity fields are explicitly retained as
  pre-repair historical values and are excluded; they were not rewritten to
  impersonate the repaired fixture run.

The Terra evidence counts are zero because no returned `answers` evidence
array validated. The metrics file retains the substantive output separately
without laundering invalid evidence into schema-valid counts.

## Agent-mediated probe

The required fresh `gpt-5.6-terra`, medium-effort attempt was made last, using
the exact fixed questions and the Graphify CLI as the only permitted
code-intelligence interface. The first sandboxed runner failed before a model
turn because the local app-server could not initialize on the read-only
filesystem. The approved outer-sandbox retry reached the provider, but the
frozen JSON Schema was rejected before inference because the provider response
format does not accept its `allOf` wrappers. A deterministic flattened schema
was also rejected because the provider requires an explicit `type` beside
`const`.

The final inference attempt therefore omitted provider-side structured-output
enforcement but retained the unchanged fixed prompt and required local
validation against the frozen schema. Its result and provider usage are
recorded in the final subsection below.

<!-- TERRA_RESULT_START -->
The completed session used thread
`019f942e-4244-7f91-8932-6afe8435297b`. It executed 26 Graphify commands,
including six failed syntax-discovery attempts, although its own returned
operation log listed only 25. The frozen limit is 24.

The substantive answer was directionally useful: it found the central
TypeScript request-flow nodes, kept the two exact-ID `normalize` bindings
separate, returned a partial lifecycle, used `affected` for the `WorkResult`
blast radius, and abstained from claiming a TypeScript-to-Rust call edge. It
also missed the indexed Rust files, could not establish the manifest-backed
unsupported-file skip, did not recover the patch's constructor changes, and
reported several non-frozen status values.

Local validation failed with exit 1:

```text
answers must be an array
operations must contain at most 24 items
every operation sequence must be an integer
```

The output used top-level `Q01` through `Q11` objects and an array of command
name strings rather than the required `answers` array and integer-sequenced
operation objects. In addition, the baseline directory contained a
lane-generated `.graphify_learning.json` overlay from the preceding
deterministic `save-result`/`reflect` probe.
The historical Terra session is invalid for controlled comparison. Its content
is retained as diagnostic
evidence only; it must not be scored as a valid capability probe.

Provider usage for this completed inference was:

| Quantity | Value |
| --- | ---: |
| Input tokens | 637,486 |
| Cached input tokens | 609,536 |
| Output tokens | 5,761 |
| Reasoning output tokens | 1,625 |
| Graphify command executions | 26 |
| Returned JSON bytes | 7,181 |
| Event-log bytes | 35,648 |

Direct elapsed time is `UNKNOWN` because the JSONL completion stream did not
record wall-clock timestamps. The metrics artifact separately records a
301,000 ms filesystem-derived interval from prompt birth to output birth and
labels it as an approximation. Cached input is reported separately and is not
subtracted from provider input usage.
<!-- TERRA_RESULT_END -->

The schema-format failures are `SMOKE_EXCLUDED` runner setup, not Graphify
capability failures and not controlled-experiment usage.

## Resource and token accounting

Deterministic discovery is excluded from later controlled comparisons. The
Terra row preserves provider usage from the invalid historical attempt; the
deterministic rows reflect the completed inventory:

| Quantity | Value | Source |
| --- | ---: | --- |
| MCP source-schema bytes | 5,798 | canonical JSON serialization |
| MCP source-schema tokens | 1,234 | local `o200k_base` |
| Primary deterministic raw output | 78 files; 361,467 bytes / 92,333 tokens | `artifact-metrics.json`; canonical SHA-256-manifested inputs only; generated summaries, including `normalized-capability-matrix.json`, are excluded |
| Per-item deterministic inventory | 79 files; 364,185 bytes / 93,088 tokens | `artifact-item-metrics.json`; includes `artifact-metrics.json` itself |
| Retained generated outputs | 475 files; 3,696,088 bytes / 1,038,422 local tokens | `generated-output-metrics.json`; duplicate snapshots counted separately |
| Graphify code-only provider/model tokens | 0 / 0 | `.graphify_analysis.json` |
| Terra provider usage | 637,486 input; 609,536 cached input; 5,761 output; 1,625 reasoning output | provider completion event |

Provider usage and local artifact-token estimates are separate and are never
summed. Graphify's 4.3x benchmark is a local corpus/query estimate; it is not an
experimentally established token saving and must not be compared directly with
provider usage.

## Evidence index

Ignored raw evidence:

- `scratchpad/code-intelligence/raw-output/capability-discovery/graphify/`
- `scratchpad/code-intelligence/indexes/graphify/`
- `scratchpad/code-intelligence/runtime/lanes/graphify-capability*/`
- `scratchpad/code-intelligence/sessions/capability-discovery/graphify/`
- `scratchpad/code-intelligence/metrics/capability-discovery/graphify/`

Most discriminating retained artifacts:

- `extract-code-only.txt`
- `graph-summary.json`
- `runtime-manifest.json`
- `query-lifecycle.txt`
- `explain-label-collision.txt`
- `explain-core-normalize.txt`
- `explain-gateway-normalize.txt`
- `path-lifecycle.txt`
- `affected-workresult.txt`
- `update-synthetic-change.txt`
- `post-update-summary.json`
- `extract-code-only-cargo.txt`
- `extract-cargo-crate-root.txt`
- `mcp-runtime-attempt.txt`
- `mcp-source-registry.json`
- `mcp-item-metrics.json`
- `artifact-metrics.json`
- `artifact-item-metrics.json`
- `generated-output-metrics.json`
- `evidence-input-manifest.json`
- `measure-artifacts.js`
- `test-measure-artifacts-idempotence.js`
- `backend-prerequisites.json`
- `extract-safe-flags.txt`
- `query-dfs-context-budget.txt`
- `query-multi-context-budget.txt`
- `affected-relation-depth.txt`
- `global-read-only.txt`
- `provider-read-only.txt`
- `update-force.txt`
- `update-no-cluster.txt`
- `timed-safe-operations.txt`
- `update-force-shrink.txt`
- `clean-baseline-manifest.txt`
- `safe-state-mutations.txt`
- `project-install-matrix.txt`
- `direct-platform-probes.txt`
- `user-install-matrix.txt`
- `project-install-timing-matrix.txt`
- `strict-and-purge-probes.txt`
- `purge-configured-out-probe.txt`
- `safe-flag-probes.txt`
- `flag-routing-timing-probes.txt`
- `graphifyignore-probes.txt`
- `filename-routing-probes.txt`
- `optional-extras-registry.json`
- `normalized-capability-matrix.json`
- `generate-normalized-capability-matrix.py`
- `refresh-evidence-manifest.py`
- `deterministic-discovery.metrics.json`
- `terra-invalid.metrics.json`
- `terra-events.jsonl`
- `terra-output.json` when present

## Report state

Report state: `DONE_WITH_CONCERNS`.

Graphify's safe offline CLI surface was broadly exercised, its restricted and
unavailable surfaces were inventoried, the manifest and resource costs were
measured, and its strengths and failure modes are concrete. The concerns are
material:

1. the frozen environment cannot run the advertised MCP surface;
2. label-only resolution is unsafe for collisions;
3. impact is type/reference traversal rather than patch-aware constructor
   analysis;
4. code-only update continuity is not preserved;
5. unflagged update accepted the same induced shrink as `--force`, contrary to
   the force-only protection implied by help text;
6. nested Cargo discovery is root-sensitive;
7. full dynamic/cross-language lifecycle reconstruction requires verification
   outside the graph;
8. `.graphifyignore` can re-include a Git-ignored file despite the maintained
   documentation saying it cannot;
9. six of 19 generic project uninstall lanes left residue, with CodeBuddy
   retaining its full project skill tree;
10. the historical Terra attempt is not comparison-valid because it exceeded the
   call cap, failed schema validation, and saw a prior learning overlay.

The deterministic Graphify lane is complete. The user canceled the fixed
Terra-medium retry after the equivalent CodeGraph runner failed before
inference inside the read-only sandbox. Graphify's current-fixture
agent-mediated capability disposition remains `UNTESTED`; the invalid
historical attempt stays diagnostic-only and excluded.
