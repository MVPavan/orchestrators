# Graphify capability discovery

Status: `DONE_WITH_CONCERNS`

Recorded: 2026-07-24

Tracking: `orch-8sk.16.4`

## Scope and evidence boundary

This report covers Graphify only. Discovery used the disposable tool checkout at
`scratchpad/code-intelligence/tools/graphify`, the isolated fixture at
`scratchpad/code-intelligence/fixtures/graphify`, and Graphify-only ignored
indexes, outputs, metrics, and sessions. It did not inspect Pi, Codex, another
graph tool, or another tool's output. No fetch, package install, model-backed
Graphify extraction, remote API, external database, credentialed operation,
global graph mutation, or live-submodule mutation was performed.

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
| Query and inspection | query, exact-ID explain, path, affected, god nodes, diagnostics, benchmark | `VERIFIED`, with precision limitations |
| Clustering/report | deterministic clustering, placeholder community labels, Markdown report | `VERIFIED` |
| Local exports | HTML, call-flow HTML, tree HTML, Obsidian, wiki, GraphML, local Neo4j/FalkorDB Cypher | `VERIFIED` |
| SVG | exposed, but `matplotlib` is absent | `UNAVAILABLE` |
| Incremental update | completed, but did not preserve the code-only corpus and changed source-path spelling | `PARTIAL` |
| Update flags | `--force` completed but no shrink case was induced; `--no-cluster` produced zero communities and no report/HTML | `PARTIAL` / `VERIFIED` |
| Cargo introspection | works when the scan root contains `Cargo.toml`; fails at the mixed fixture root where the manifest is nested | `PARTIAL` |
| Provider registry reads | isolated empty `provider list` exited 0; missing `provider show` exited 1 without creating a config file | `VERIFIED` |
| MCP | source registers 10 tools and 6 resources; the isolated environment lacks the `mcp` extra, so no runtime handshake/list was possible | `UNAVAILABLE` |
| Semantic labeling/extraction | requires a model backend, credentials, or local model service | `RESTRICTED` |
| Remote/global/integration writes | network, GitHub, external DB, global graph, hook/platform config, or destructive effects | `RESTRICTED` |
| Fixed Terra probe | substantive answer retained, but 26 calls exceeded the 24-call cap and the output failed the frozen schema | `INVALID` for comparison |

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
provider keys or ordinary Git credentials were inherited. Graphify wrote to
the wrapper's absolute `GRAPHIFY_OUT`, even when `extract --out` was also
supplied. In this environment the environment override took precedence over
the CLI output argument. The resulting graph was copied to
`indexes/graphify/baseline/` before query operations could write freshness
stamps.

The canonical fixture hashes were verified before extraction and after the
synthetic update was reversed. The synthetic patch was applied with `git
apply`, the public update was exercised, and the patch was reversed with `git
apply -R`; final fixture status was clean and every frozen SHA-256 matched.

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
| `benchmark` | local corpus-versus-query token estimate | reported about 7,200 naive vs 1,684 average query tokens, 4.3x | `VERIFIED` as an estimate, not a saving claim |
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
| `global add/remove` and `extract --global` | write a user-global graph | `RESTRICTED` |

### Acquisition, PR, provider, hook, and platform integration

| Surface | Effects/prerequisites | Disposition |
| --- | --- | --- |
| `clone` | network plus clone below user storage | `RESTRICTED` |
| `add` | fetch URL, write corpus, update graph | `RESTRICTED` |
| `prs` and MCP PR tools | `gh`, GitHub authentication/network; triage can also use a configured backend | `RESTRICTED` |
| `provider list`; `provider show NAME` | read the lane-local global provider registry; list created only its parent directory, and missing show exited 1 | `VERIFIED`; `provider-read-only.txt` |
| `provider add/remove` | mutate `~/.graphify/providers.json`; a configured endpoint receives corpus content and its configured key | `RESTRICTED` |
| `hook status` | fixture read-only status reported all hooks absent | `VERIFIED` |
| `hook install/uninstall` | modifies Git hooks and merge-driver config | `RESTRICTED` |
| top-level `install`/`uninstall` | writes or deletes host integration files; `--purge` deletes graph output | `RESTRICTED` |
| `claude`, `codebuddy`, `codex`, `opencode`, `kilo`, `gemini`, `cursor`, `aider`, `copilot`, `vscode`, `claw`, `droid`, `trae`, `trae-cn`, `antigravity`, `hermes`, `kiro`, `pi`, `devin` | install/uninstall skills, instructions, hooks, plugins, or host config | `RESTRICTED` |

The dispatcher also contains `cache-check`, `merge-chunks`,
`merge-semantic`, `hook-check`, and `hook-guard`. They support Graphify's own
agent/hook pipeline but are absent from the advertised top-level command list;
they are recorded as hidden/internal surfaces, not promoted to supported public
capabilities by source existence alone.

### Exhaustive public flag and configuration inventory

The following inventory reconciles top-level help with the frozen dispatcher.
“Accepted” means the parser accepted the flag; it does not imply that a
dormant semantic/model control affected a code-only run.

| Surface | Public flags/configuration | Effects and prerequisites | Disposition and evidence |
| --- | --- | --- | --- |
| global CLI | `-h`, `--help`, `-?`, `-v`, `--version`, `version` | read-only help/version; universal help guard applies to most subcommands | `VERIFIED`; `help.txt`, `version.txt` |
| `extract` corpus/output | positional path; `--out`/`--output`; `--code-only`; `--no-gitignore`; repeatable `--exclude`; `--google-workspace`; `--postgres`; `--cargo`; `--global`; `--as` | selects corpus/output and optional local or external sources; Google/Postgres/global need integration access | local flags `VERIFIED`; integrations `RESTRICTED`; `extract-code-only.txt`, `extract-safe-flags.txt`, Cargo evidence |
| `extract` pipeline | `--backend`, `--model`, `--mode deep`, `--force`, `--no-cluster`, `--dedup-llm`, `--allow-partial`, `--timing` | force bypasses manifest/semantic cache; no-cluster writes raw graph; deep/dedup require model backend; allow-partial permits guarded partial output | force/no-cluster/timing `VERIFIED`; allow-partial parser acceptance `VERIFIED` but guarded behavior `UNTESTED`; model modes `RESTRICTED`; `extract-safe-flags.txt` |
| `extract` tuning | positive `--max-workers`, `--token-budget`, `--max-concurrency`, `--api-timeout`, `--resolution`; numeric `--exclude-hubs` | AST process count; semantic chunk budget/concurrency/request timeout; clustering resolution/hub exclusion | parser and code-only acceptance `VERIFIED`; semantic effect `UNTESTED`; `extract-safe-flags.txt` |
| `update` | path, `--force`, `--no-cluster` | local AST rebuild; force allows shrink; no-cluster skips community pass | all three command paths executed; update remains `PARTIAL` for corpus/path continuity, force shrink override is `UNTESTED`, and no-cluster effect is `VERIFIED`; `update-synthetic-change.txt`, `update-force.txt`, `update-no-cluster.txt` |
| `cluster-only` | path; `--graph`; `--no-viz`; `--no-label`; `--backend`; `--model`; `--resolution`; `--exclude-hubs`; `--max-concurrency`; `--batch-size`; `--min-community-size`; `--timing` | local recluster/report; optional model labels | deterministic no-label/no-viz `VERIFIED`; labeling `RESTRICTED`; `cluster-only.txt` |
| `label` | path; `--graph`; `--missing-only`; `--backend`; `--model`; `--max-concurrency`; `--batch-size`; `--min-community-size`; `--timing` | names all or only missing communities with model | `RESTRICTED` |
| `query` | question; `--dfs`; repeatable `--context`; `--budget`; `--graph` | BFS default or DFS; explicit edge-context filter; approximate output-token cap | variants `VERIFIED`; `query-lifecycle.txt`, `query-dfs-context-budget.txt`, `query-multi-context-budget.txt` |
| `affected` | node; repeatable `--relation`; `--depth`; `--graph` | reverse traversal over selected relations and depth | variants `VERIFIED`; `affected-workresult.txt`, `affected-relation-depth.txt` |
| `path`, `explain` | positional labels/IDs; `--graph` | local graph lookup; also writes freshness stamp | `VERIFIED`; `path-lifecycle.txt`, `explain-core-normalize.txt` |
| `god-nodes` | `--top`; `--graph`; `--json` | local degree ranking | `VERIFIED`; `god-nodes.json` |
| `diagnose multigraph` | `--graph`; `--json`; `--max-examples`; mutually exclusive `--directed`/`--undirected`; `--extract-path` | local edge-collapse simulation plus optional producer-source scan | `VERIFIED`; `diagnose-multigraph.json` |
| `benchmark` | optional graph path | local approximate word/token comparison | `VERIFIED` as estimate; `benchmark.txt` |
| `save-result` | required `--question`; `--answer` or `--answer-file`; `--type`; `--nodes`; enum `--outcome useful|dead_end|corrected`; `--correction`; `--memory-dir` | writes local result memory | `VERIFIED`; `save-result.txt` |
| `reflect` | `--memory-dir`; `--out`; `--graph`; `--analysis`; `--labels`; `--half-life-days`; `--min-corroboration`; `--if-stale` | writes deterministic lesson document and optional graph-side learning overlay | `VERIFIED`; `reflect.txt` |
| `tree` | `--graph`; `--output`; `--root`; `--max-children`; `--top-k-edges`; `--label` | writes local D3 HTML | `VERIFIED`; `tree.txt` |
| `merge-graphs` | two or more graph paths; `--out` | writes union graph | `VERIFIED`; `merge-graphs.txt` |
| `merge-driver` | base/current/other positional paths | overwrites current disposable graph with union | `VERIFIED`; `merge-driver.txt` |
| `export html` | `--graph`; `--labels`; `--node-limit`; `--no-viz` | local standalone HTML or explicit skip | `VERIFIED`; `export-html.txt` |
| `export callflow-html` | optional graph/dir; `--graph`; `--labels`; `--report`; `--sections`; `--output`; `--lang`; `--max-sections`; `--diagram-scale`; `--max-diagram-nodes`; `--max-diagram-edges` | local architecture/call-flow HTML | `VERIFIED`; `export-callflow.txt` |
| other local exports | `obsidian --graph --labels --dir`; `wiki/svg --graph --labels`; `graphml --graph` | writes local artifacts; SVG needs matplotlib | all except SVG `VERIFIED`; SVG `UNAVAILABLE`; `export-*.txt` |
| DB exports | `neo4j`/`falkordb`: `--graph`; optional `--push`, `--user`, `--password` or password env | no-push writes Cypher; push writes remote DB | local `VERIFIED`; push `RESTRICTED`; `export-neo4j.txt`, `export-falkordb.txt` |
| `global` | `add GRAPH --as`; `remove TAG`; `list`; `path` | add/remove write user-global graph; list/path are read-only | list/path `VERIFIED`; writes `RESTRICTED`; `global-read-only.txt` |
| `provider` | `list`; `show NAME`; `add NAME --base-url --default-model --env-key [--pricing-input --pricing-output]`; `remove NAME` | list/show read global provider config; add/remove write it; configured endpoints later receive corpus/key data | list and missing-show behavior `VERIFIED`; add/remove `RESTRICTED`; `provider-read-only.txt` |
| `prs` | `--triage`; `--worktrees`; `--conflicts`; `--wrong-base`; `--base`/`-b`; `--repo`/`-R`; `--graph` | invokes Git/`gh`; triage may invoke model | `RESTRICTED` |
| `clone`, `add` | clone URL with `--branch`, `--out`; add URL with `--author`, `--contributor`, `--dir` | network plus corpus writes | `RESTRICTED` |
| hooks/watch/update check | `hook install|uninstall|status`; `watch PATH`; `check-update PATH` | install/uninstall mutate Git config/hooks; watch is unbounded and needs watchdog; status/check are local | status/check `VERIFIED`; writes `RESTRICTED`; watch `UNAVAILABLE` |
| host installation | `install [--project] [--strict] [--platform P]`; `uninstall [--purge] [--project] [--platform P]`; platform `install|uninstall`, with project scope where supported and Claude strict mode | writes/removes skills, instructions, hooks, plugins, config, and optionally graph output | `RESTRICTED` |

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
`_TTL`, `GRAPHIFY_SKIP_HOOK`, `GRAPHIFY_REBUILD_{LOG,TIMEOUT,MEMORY_LIMIT_MB}`,
and `GRAPHIFY_API_KEY`. `GRAPHIFY_CHANGED`, `GRAPHIFY_REPO_ROOT`,
`GRAPHIFY_PYTHON`, and `GRAPHIFY_BIN` are hook/launcher handoff variables;
`GRAPHIFY_OUT_NAME` is an internal constant rather than an operator setting.
Credential and endpoint variable names are inventoried below; no credential
values were inherited, printed, or supplied.

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
missing-provider` printed a not-found diagnostic and exited 1 in 0.05 s. These
read/failure paths are `VERIFIED`; add/remove remain `RESTRICTED` writes.
Evidence: `provider-read-only.txt`.

### Extraction modes and backends

The verified offline lane used `extract PATH --code-only`. The following
advertised variants were inventoried but not activated:

| Variant | Requirement/effect | Disposition |
| --- | --- | --- |
| semantic docs/papers/images and `--mode deep` | configured model backend; corpus leaves the process for remote backends | `RESTRICTED` |
| `--backend`/`--model` | Gemini, Kimi, Claude, OpenAI, DeepSeek, Ollama, Azure, Bedrock, or custom provider | `RESTRICTED` |
| `--google-workspace` | `gws` export/network and generated sidecars | `RESTRICTED` |
| `--postgres DSN` | live external PostgreSQL schema introspection | `RESTRICTED` |
| `--cargo` | local Cargo manifest introspection | `PARTIAL` |
| `--no-cluster` | raw graph without community analysis | produced 108 nodes/177 edges without communities in the safe-flags extraction | `VERIFIED` |
| `--force` | bypasses manifest/semantic-cache reads | emitted the full-rescan notice in the safe-flags extraction | `VERIFIED` |
| `--allow-partial` | permits guarded partial output | parser accepted it, but no partial-build condition was safely induced | parser acceptance `VERIFIED`; guarded behavior `UNTESTED` |
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
| `query_graph` | required `question`; `mode=bfs` enum `bfs|dfs`; `depth=3` (handler caps maximum at 6); `token_budget=2000`; string-array `context_filter`; `project_path` | node/edge context text; local graph read, optional plaintext query log, no network | 901/201; 753/173 | source `VERIFIED`, runtime `UNAVAILABLE` |
| `get_node` | required `label`; `project_path` | first substring/exact-ID match with ID/source/type/community/degree; local read | 413/88; 310/66 | source `VERIFIED`, runtime `UNAVAILABLE` |
| `get_neighbors` | required `label`; optional `relation_filter`; `token_budget=2000`; `project_path` | incoming/outgoing neighbors, relations, confidence and relation-site, budget-truncated; local read | 544/113; 435/92 | source `VERIFIED`, runtime `UNAVAILABLE` |
| `get_community` | required integer `community_id`; `token_budget=2000`; `project_path` | community header and member/source list, budget-truncated; local read | 514/110; 413/89 | source `VERIFIED`, runtime `UNAVAILABLE` |
| `god_nodes` | `top_n=10`; `project_path` | degree-ranked hub text; local read | 390/80; 259/55 | source `VERIFIED`, runtime `UNAVAILABLE` |
| `graph_stats` | only optional `project_path` | nodes, edges, communities, and confidence percentages; local read | 358/69; 219/44 | source `VERIFIED`, runtime `UNAVAILABLE` |
| `shortest_path` | required `source`, `target`; `max_hops=8`; `project_path` | deterministic undirected path with stored relation/confidence, ambiguity/max-hop diagnostics; local read | 606/124; 483/101 | source `VERIFIED`, runtime `UNAVAILABLE` |
| `list_prs` | optional `base`, `repo`, `project_path` | formatted open PR/CI/review/worktree/graph-impact text | 673/146; 409/90 | Git/`gh` plus GitHub network/auth `RESTRICTED`; runtime `UNAVAILABLE` |
| `get_pr_impact` | required integer `pr_number`; optional `repo`, `project_path` | PR metadata, changed files (first 20), touched communities/nodes | 684/143; 405/87 | GitHub network/auth `RESTRICTED`; runtime `UNAVAILABLE` |
| `triage_prs` | optional `base`, `repo`, `project_path` | actionable PRs ranked with CI/review/age/worktree/blast radius; concurrently fetches file lists | 704/158; 409/90 | GitHub network/auth `RESTRICTED`; runtime `UNAVAILABLE` |

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
| `graphify://report` | Markdown; reads sibling `GRAPH_REPORT.md`, or a missing-report diagnostic | 113/27 | source `VERIFIED`, runtime `UNAVAILABLE` |
| `graphify://stats` | text; same local counters as `graph_stats` | 139/30 | source `VERIFIED`, runtime `UNAVAILABLE` |
| `graphify://god-nodes` | text; local top-10 degree ranking | 117/30 | source `VERIFIED`, runtime `UNAVAILABLE` |
| `graphify://surprises` | text; computes top-10 cross-community connections or diagnostic | 141/28 | source `VERIFIED`, runtime `UNAVAILABLE` |
| `graphify://audit` | text; exact confidence counts/percentages | 136/36 | source `VERIFIED`, runtime `UNAVAILABLE` |
| `graphify://questions` | text; deterministically suggested questions from graph/community labels or diagnostic | 137/28 | source `VERIFIED`, runtime `UNAVAILABLE` |

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
Pascal has a documented fallback. Filename-aware extraction also recognizes
MCP configuration and package manifests before generic suffix routing.

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
| `update --force` | 108 nodes, 173 edges, 10 communities | 112 nodes, 175 edges, 11 communities; regenerated graph, HTML, report, and labels | 0.22 s / 43,044 KiB | command path `VERIFIED`; smaller-graph overwrite semantics `UNTESTED` because no shrink was induced |
| `update --no-cluster` | 108 nodes, 173 edges, 10 communities | 112 nodes, 179 edges, zero assigned communities; no HTML, report, or labels | 0.20 s / 41,920 KiB | no-cluster effect `VERIFIED` |

Both variants retained the same update limitation: they reintroduced
`README.md` and `docs/architecture.md` into the code-only baseline and rewrote
source paths to lane-relative parent-repository paths. Both fixture copies
remained clean at commit
`e7ddad2c44321f7b50e60c923b8f0733fb757874`. Evidence:
`update-force.txt` and `update-no-cluster.txt`.

## Optional dependencies and restricted surfaces

Installed in the isolated environment: core Graphify, NetworkX, tree-sitter and
the default language parsers.

Absent optional packages observed directly:

| Extra/capability | Frozen availability |
| --- | --- |
| `mcp`, `starlette` | absent |
| `matplotlib` (`svg`) | absent |
| `neo4j`, `falkordb` clients | absent; local Cypher export still works |
| `watchdog` | absent |
| `graspologic` (`leiden`) | absent; core clustering still worked |
| `openai`, `tiktoken`, `boto3`, `anthropic` | absent |

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

Other declared extras include PDF/Markdown conversion, office, Google
workspace, PostgreSQL, video/transcription, Chinese segmentation, SQL,
Pascal, DreamMaker, and Terraform parsers. Missing extras are
`UNAVAILABLE`; credentialed/network services are additionally `RESTRICTED`.

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

| Capability | Primary evidence | Timing; output bytes; local o200k tokens; model tokens | Pi / Codex applicability | Main limitation |
| --- | --- | --- | --- | --- |
| clustered code-only extraction | `extract-code-only.txt`, `graph-summary.json`, `runtime-manifest.json` | 0.32 s; evidence 7,200 bytes/2,534 tokens; generated tree 143,288 bytes, graph 95,965; provider 0/0 | CLI usable by both | structural AST graph, incomplete dynamic/data flow |
| safe extract flags/no-cluster | `extract-safe-flags.txt` | 0.17 s; evidence 1,465 bytes/409 tokens; provider 0/0 | CLI usable by both | semantic tuning dormant; allow-partial failure behavior untested |
| BFS query | `query-lifecycle.txt`, `query-normalize.txt` | elapsed `UNKNOWN` (not retained); evidence 11,301 bytes/2,929 tokens; provider 0/0 | strong orientation primitive for both | label collision and approximate token budget |
| DFS/context/budget query | `query-dfs-context-budget.txt`, `query-multi-context-budget.txt` | 0.15/0.16 s; evidence 1,072 bytes/304 tokens; provider 0/0 | usable by both | 250-token output truncated 16/25 nodes |
| explain/path | six success/boundary artifacts | elapsed `UNKNOWN` (not retained); evidence 1,498 bytes/418 tokens; provider 0/0 | usable by both; exact IDs recommended | missing targets exit 0; label-only first match |
| affected variants | `affected-workresult.txt`, `affected-relation-depth.txt` | 0.12-0.13 s where retained; evidence 1,168 bytes/318 tokens; provider 0/0 | useful to both for graph blast radius | not patch-aware; misses object-literal constructors |
| hubs/diagnostics/benchmark | `god-nodes.json`, `diagnose-multigraph.json`, `benchmark.txt` | elapsed `UNKNOWN` (not retained); evidence 4,368 bytes/1,256 tokens; provider 0/0 | local diagnostics usable by both | benchmark is estimate, not measured provider saving |
| cluster-only | `cluster-only.txt` | elapsed `UNKNOWN` (not retained); evidence 1,322 bytes/383 tokens; provider 0/0 with no-label | usable by both | labels need model; clustering alters graph structure |
| local HTML/tree/wiki/Obsidian/GraphML exports | six export artifacts | elapsed `UNKNOWN` (not retained); evidence 1,623 bytes/410 tokens; generated tree 20,797 and callflow 63,090 bytes; provider 0/0 | human orientation artifacts for both | derived views; not additional source truth |
| local Cypher exports | `export-neo4j.txt`, `export-falkordb.txt` | elapsed `UNKNOWN` (not retained); evidence 444 bytes/116 tokens; generated scripts 35,136 bytes each; provider 0/0 | usable by both without push | DB push restricted |
| SVG export | `export-svg.txt` | failed before generated output; evidence 1,241 bytes/322 tokens; provider 0 | unavailable to both frozen lanes | matplotlib absent |
| memory/reflection | `save-result.txt`, `reflect.txt` | elapsed `UNKNOWN` (not retained); evidence 302 bytes/79 tokens; provider 0/0 | persistent hints consumable by both | overlay can contaminate controlled probes |
| graph merge | `merge-graphs.txt`, `merge-driver.txt` | elapsed `UNKNOWN` (not retained); evidence 148 bytes/39 tokens; merged graph 122 nodes/188 edges; provider 0/0 | usable by both on disposable copies | union, not semantic reconciliation |
| Cargo introspection | three Cargo artifacts | elapsed `UNKNOWN` (not retained); evidence 4,728 bytes/1,380 tokens; provider 0/0 | usable by both | nested manifest not discovered from mixed root |
| update variants | synthetic update plus force/no-cluster evidence | 0.20/0.22/0.20 s; evidence 5,708 bytes/1,670 tokens; provider 0/0 | usable by both through adapter below | code-only/path continuity not preserved; force shrink behavior untested |
| global list/path | `global-read-only.txt` | 0.12/0.13 s; evidence 337 bytes/102 tokens; provider 0/0 | usable by both in isolated home | add/remove remain separate restricted writes |
| provider list/missing show | `provider-read-only.txt` | 0.05/0.05 s; evidence 1,590 bytes/393 tokens; provider 0/0 | safe configuration orientation for both | list creates lane-local parent directory; add/remove restricted |
| MCP tools/resources | three MCP registry/runtime artifacts | runtime attempt elapsed `UNKNOWN`; evidence 12,058 bytes/2,900 tokens; tools 5,798/1,234, resources 790/176; model 0 | Pi/Codex can consume MCP when installed/configured | runtime unavailable; PR tools need GitHub |
| semantic backend inventory | `backend-prerequisites.json` | no execution elapsed; evidence 4,672 bytes/1,190 tokens; model 0 | both can invoke CLI when provisioned | credentials/backend/network restricted |
| CLI/host/remote inventory | `help.txt`, `help-command-families.txt` plus source dispatch | no execution elapsed retained; help evidence 12,801 bytes/2,923 tokens; model 0 | host installers and remote commands exist | writes/network/auth intentionally restricted |

The current primary deterministic evidence is 63 TXT/JSON files, 103,396
bytes, and 27,810 local `o200k_base` tokens. Including the current
`artifact-metrics.json` summary itself, the per-item inventory covers 64 files,
105,379 bytes, and 28,358 tokens. These aggregates include inventories and
diagnostics, not just graph answers, so they are not a measure of prompt
context that Pi or Codex must consume. The generated per-item/output metrics
files and measurement script are excluded from the primary aggregate.

`generated-output-metrics.json` separately enumerates all 268 regular files
under the retained Graphify output roots: 2,181,808 bytes and 612,551 local
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
  artifact estimate now reflects the 63-file primary deterministic inventory.
- `terra-invalid.metrics.json` is the actual `CAPABILITY_PROBE`, with provider
  usage, 26 tool calls, invalid-schema/call-cap contamination, and 301,000 ms
  elapsed derived from prompt/output filesystem birth times because JSONL
  events carry no timestamps.

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
deterministic `save-result`/`reflect` probe. The Terra session therefore is
`INVALID` for controlled comparison. Its content is retained as diagnostic
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
| Primary deterministic raw output | 63 files; 103,396 bytes / 27,810 tokens | regenerated `artifact-metrics.json`; generated metrics files excluded |
| Per-item deterministic inventory | 64 files; 105,379 bytes / 28,358 tokens | `artifact-item-metrics.json`; includes `artifact-metrics.json` itself |
| Retained generated outputs | 268 files; 2,181,808 bytes / 612,551 local tokens | `generated-output-metrics.json`; duplicate snapshots counted separately |
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
- `measure-artifacts.js`
- `backend-prerequisites.json`
- `extract-safe-flags.txt`
- `query-dfs-context-budget.txt`
- `query-multi-context-budget.txt`
- `affected-relation-depth.txt`
- `global-read-only.txt`
- `provider-read-only.txt`
- `update-force.txt`
- `update-no-cluster.txt`
- `deterministic-discovery.metrics.json`
- `terra-invalid.metrics.json`
- `terra-events.jsonl`
- `terra-output.json` when present

## Final disposition

`DONE_WITH_CONCERNS`.

Graphify's safe offline CLI surface was broadly exercised, its restricted and
unavailable surfaces were inventoried, the manifest and resource costs were
measured, and its strengths and failure modes are concrete. The concerns are
material:

1. the frozen environment cannot run the advertised MCP surface;
2. label-only resolution is unsafe for collisions;
3. impact is type/reference traversal rather than patch-aware constructor
   analysis;
4. code-only update continuity is not preserved;
5. nested Cargo discovery is root-sensitive;
6. full dynamic/cross-language lifecycle reconstruction requires verification
   outside the graph;
7. the fixed Terra attempt is not comparison-valid because it exceeded the
   call cap, failed schema validation, and saw a prior learning overlay.

The deterministic Graphify lane is complete. The only remaining execution is
the fixed Terra-medium retry after the shared capped runner is repaired under
`orch-8sk.16.7`; it is not a deterministic capability gap and was not run here.
