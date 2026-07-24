# CodeGraph capability discovery

Status: `DONE_WITH_CONCERNS`

Recorded: 2026-07-24

Tracking: `orch-8sk.16.2`

## Scope and evidence boundary

This report covers CodeGraph only. Discovery used the disposable checkout at
`scratchpad/code-intelligence/tools/codegraph`, the isolated fixture at
`scratchpad/code-intelligence/fixtures/codegraph`, and CodeGraph-only ignored
indexes, outputs, metrics, and sessions. It did not inspect Pi, Codex, another
graph tool, or another tool's output. No fetch, package install, credentialed
operation, global integration write, destructive operation, or live-submodule
mutation was performed.

Every invocation ran through
`docs/research/harness-tools/codebase-intelligence/experiments/coding-agents/run-isolated.sh`
with lane-local home, cache, config, state, temp, and output directories. The
frozen tool revision was
`03666584ed9836d7954cbb19e2252081b96fcad9`; its package version was `1.0.1`.
The fixture revision was
`e7ddad2c44321f7b50e60c923b8f0733fb757874`, with manifest digest
`fc12b07aa2219f346ee1e00f52875efae8c52bbb12dc410456e9457ea1b58e24`.
The tool checkout remained clean.

## Result at a glance

| Area | Result | Disposition |
| --- | --- | --- |
| Offline index | 14 files, 93 nodes, 211 edges across TypeScript and Rust | `VERIFIED` |
| Structural discovery | symbol search, source retrieval, callers, callees, file inventory, and status were useful | `VERIFIED` |
| Architecture synthesis | `explore` returned substantial grounded source, but invented a static TypeScript-to-Rust same-name edge | `PARTIAL` |
| Ambiguous names | MCP callers can narrow by file; CLI callers and impact aggregate same-name definitions | `PARTIAL` |
| Incremental maintenance | status detected three changed files and sync processed them without changing tracked source | `VERIFIED`, with granularity limits |
| Change analysis | `affected` consumes explicit file lists; impact is generic graph traversal, not patch-aware semantic diffing | `PARTIAL` |
| MCP | one default tool; eight source-registered opt-in tools; direct stdio works | `VERIFIED`, with surface inconsistency |
| Shared daemon | Unix socket creation failed with `EPERM` in this sandbox; documented direct mode worked | `UNAVAILABLE` in this environment |
| JavaScript library API | 38 runtime exports and the full `CodeGraph` facade were probed; direct per-file parsing from an opened facade exposed a grammar-loading limitation | `VERIFIED`, with `PARTIAL` methods |
| Installer integrations | config generation for eight targets worked; host writes were not authorized | `PARTIAL` |
| Upgrade, telemetry transmission, remote reasoning | network, host mutation, credentials, or an unexposed internal path | `RESTRICTED` |
| Fixed Terra probe | provider rejected the frozen output schema before model execution | `BLOCKED` as a probe, not a CodeGraph failure |

The systems-level conclusion is that CodeGraph is a strong low-cost structural
navigation layer when its answers are treated as graph-backed evidence rather
than authoritative runtime semantics. It is particularly useful for locating
symbols, retrieving exact source, following local calls, and checking index
freshness. Its higher-level traversal can over-connect same-name symbols across
languages, and it does not provide a public patch-aware change-analysis
operation.

## Frozen runtime and isolation

| Component | Frozen value |
| --- | --- |
| CodeGraph source | `03666584ed9836d7954cbb19e2252081b96fcad9` |
| Package | `codegraph 1.0.1` |
| Built CLI SHA-256 | `f6ae07cc5ce347eb30fa06ca2091b61f5abaa24d36b43b16b42504c50323de47` |
| `package.json` SHA-256 | `f5479247f65d44529d27febb6f454ce50d4f45036c1e4c33b2fd0f09f9fd8d37` |
| lockfile SHA-256 | `d7ebf3d112d20627d7476f50440006dfb811147f1c875ac45903e7b7d1847203` |
| Node | 22.22 in the frozen tool lane |
| Fixture commit | `e7ddad2c44321f7b50e60c923b8f0733fb757874` |
| Fixture manifest digest | `fc12b07aa2219f346ee1e00f52875efae8c52bbb12dc410456e9457ea1b58e24` |
| Artifact tokenizer | `gpt-tokenizer@3.4.0:o200k_base` |

Initialization wrote only `.codegraph/` in the disposable fixture. The SQLite
database used the `node-sqlite` backend and WAL journal mode. The final cleanup
removed that index; the fixture's tracked hashes and Git status were then
checked against the frozen baseline.

## Public CLI inventory

Root help advertises 20 commands. `prompt-hook` and `serve` are hidden support
commands and are recorded separately rather than promoted to public
capabilities. Invoking the root without a command enters an interactive
installer; that host-mutating path was restricted.

### Public command dispositions

| Command | Purpose and observed behavior | Disposition |
| --- | --- | --- |
| `init` | initialized the fixture and performed the first index | `VERIFIED` |
| `uninit` | removes the local index; used during final cleanup | `VERIFIED` |
| `index` | full rebuild completed and preserved 93 nodes/211 edges | `VERIFIED` |
| `sync` | clean sync and three-file incremental sync both completed | `VERIFIED` |
| `status` | text/JSON status, stale-file detection, and uninitialized state worked | `VERIFIED` |
| `query` | name/kind search and empty missing result worked | `VERIFIED` |
| `explore` | returned rich source context, but synthesized one false cross-language edge | `PARTIAL` |
| `node` | exact symbol and file/range retrieval worked; missing symbol gave guidance | `VERIFIED` |
| `files` | flat, grouped, tree, language, and directory views worked; invalid format was silently accepted | `PARTIAL` |
| `daemon` / `daemons` | manager/list path worked; server socket was denied by the sandbox | `PARTIAL` |
| `unlock` | safe no-lock case returned success | `VERIFIED` |
| `callers` | useful, but the CLI merges multiple same-name definitions | `PARTIAL` |
| `callees` | recovered the fixture's principal lifecycle callees | `VERIFIED` |
| `impact` | useful reverse traversal, but broad and same-name aggregating | `PARTIAL` |
| `affected` | accepts changed file paths and finds dependent tests; no tests exist in the fixture | `PARTIAL` |
| `install` | `--print-config` worked for eight targets; host writes were restricted | `PARTIAL` |
| `uninstall` | isolated no-op behavior is safe; real host removal was not needed | `VERIFIED` |
| `telemetry` | status/off worked in lane-local state; transmission was not enabled | `PARTIAL` |
| `upgrade` | requires package/network/host mutation | `RESTRICTED` |
| `version` | reported `1.0.1` | `VERIFIED` |

CLI count: 11 `VERIFIED`, 8 `PARTIAL`, and 1 `RESTRICTED`.

The CLI's argument validation is permissive in two places. `query --kind
bogus` returned an empty array with exit 0, while `files --format bogus --json`
fell back to a flat list with exit 0. Consumers should validate enum-like
arguments before invocation.

### Hidden/internal commands

- `serve` is the MCP transport entry point.
- `prompt-hook` supports structural prompt injection.

The source also contains reasoning/offload modules and remote endpoint
configuration, but this revision registers no public CLI command for them.
Their existence is not treated as a usable public capability.

## MCP inventory

Runtime `initialize` succeeded with protocol `2024-11-05`, server name
`codegraph`, and version `1.0.1`. The indexed server instruction string was
4,653 bytes. Resources, resource templates, and prompts were all empty.

The ordinary default `tools/list` surface contains only:

1. `codegraph_explore`

The source registry and `CODEGRAPH_MCP_TOOLS` opt-in surface contain:

1. `codegraph_search`
2. `codegraph_callers`
3. `codegraph_callees`
4. `codegraph_impact`
5. `codegraph_node`
6. `codegraph_explore`
7. `codegraph_status`
8. `codegraph_files`

| MCP tool | Probe result | Disposition |
| --- | --- | --- |
| `codegraph_search` | collision and missing-symbol searches worked | `VERIFIED` |
| `codegraph_callers` | file-scoped disambiguation separated both `normalize` definitions | `VERIFIED` |
| `codegraph_callees` | recovered the `run` lifecycle calls | `VERIFIED` |
| `codegraph_impact` | returned a broad WorkResult reverse traversal | `PARTIAL` |
| `codegraph_node` | file/range retrieval worked | `VERIFIED` |
| `codegraph_explore` | returned source-rich context, with one false semantic connection | `PARTIAL` |
| `codegraph_status` | returned indexed state and counts | `VERIFIED` |
| `codegraph_files` | grouped file inventory worked | `VERIFIED` |

MCP count: 6 `VERIFIED` and 2 `PARTIAL`.

There is a discoverability inconsistency. The proxy's static opt-in
`tools/list` returned all eight schemas. The direct engine dynamically reduced
the list to search, node, and explore for this tiny 14-file repository, yet
direct calls to all eight allowlisted handlers still executed. Agents should
not assume either list is a complete statement of callable handlers.

The normal shared-daemon transport could not bind
`.codegraph/daemon.sock` in this sandbox:

```text
listen EPERM: operation not permitted .../.codegraph/daemon.sock
```

No daemon was left running. The documented `CODEGRAPH_NO_DAEMON=1` direct
stdio mode completed initialization, list, and call probes. This is an
environment limitation, not evidence that the direct MCP server is broken.

## Languages, entities, relationships, and frameworks

The runtime type registry declares 32 language values:

`typescript`, `javascript`, `tsx`, `jsx`, `python`, `go`, `rust`, `java`, `c`,
`cpp`, `csharp`, `razor`, `php`, `ruby`, `swift`, `kotlin`, `dart`, `svelte`,
`vue`, `astro`, `liquid`, `pascal`, `scala`, `lua`, `luau`, `objc`, `r`,
`yaml`, `twig`, `xml`, `properties`, and `unknown`.

It declares 22 node kinds:

`file`, `module`, `class`, `struct`, `interface`, `trait`, `protocol`,
`function`, `method`, `property`, `field`, `variable`, `constant`, `enum`,
`enum_member`, `type_alias`, `namespace`, `parameter`, `import`, `export`,
`route`, and `component`.

It declares 12 edge kinds:

`contains`, `calls`, `imports`, `exports`, `extends`, `implements`,
`references`, `type_of`, `returns`, `instantiates`, `overrides`, and
`decorates`.

The resolver registry contains 24 framework/integration resolvers:

`spring`, `vue`, `swiftui`, `uikit`, `vapor`, `swift-objc-bridge`, `svelte`,
`go`, `rust`, `express`, `fabric-view`, `react`, `drupal`,
`react-native-bridge`, `expo-modules`, `aspnet`, `django`, `flask`, `fastapi`,
`play`, `astro`, `laravel`, `rails`, and `nestjs`.

Maintained prose still mentions 17 frameworks in places, so source registration
is the stronger inventory at this revision. The authoritative type declarations
are in `scratchpad/code-intelligence/tools/codegraph/src/types.ts`; public
library methods are exposed in
`scratchpad/code-intelligence/tools/codegraph/src/index.ts`.

## Fixture indexing and corpus coverage

The fixture has 25 tracked files. CodeGraph indexed 14:

- 12 TypeScript-family files, including declaration files;
- 2 Rust files.

It skipped 11 non-code or unsupported inputs: fixture hash metadata, Markdown
documentation, three package manifests, `Cargo.toml`, `tsconfig.json`, the
synthetic patch, and `unsupported/legacy.capfixture`. The unknown
`.capfixture` file was explicitly not indexed.

| Measurement | Result |
| --- | --- |
| First init/index | 14 files, 93 nodes, 211 edges |
| Internal first-index time | 150 ms |
| First-index wall time | 0.30 s |
| First-index peak RSS | 116,064 KB |
| Full reindex wall time | 0.24 s |
| Full reindex peak RSS | 108,076 KB |
| Database size | 290,816 bytes |
| Total `.codegraph` size | 291,045 bytes |

These are measurements of this tiny synthetic fixture, not scaling claims.

## Systems-understanding probes

### Successful lifecycle reconstruction

`callees run` recovered calls to `authorize`, `save`, `resolve`, `execute`, and
`publish`. `explore lifecycle` returned verbatim source around the request
handler, workflow runner, and TypeScript policy authorization. That is enough
to orient a systems engineer to the principal control path without reading the
whole repository.

### Cross-language false connection

The same lifecycle exploration also emitted:

```text
authorize → authorize [dynamic: interface → impl @rust/policy/src/lib.rs:23]
```

The fixture defines a child-process/delimiter protocol boundary; there is no
statically resolvable TypeScript call into that Rust method. This is a
same-name/interface heuristic overreach. Any cross-language edge produced by
high-level exploration must be confirmed against exact source and the actual
transport boundary.

### Same-name collision

Two TypeScript `normalize` functions were intentionally present. `query`
returned separate path-qualified nodes, and `explore` showed separate bodies.
MCP callers correctly narrowed each definition with a file argument. The CLI
`callers normalize` and `impact normalize` combined relationships from both
bindings because those commands expose no equivalent file discriminator.

### WorkResult impact

`impact WorkResult` returned a 24-node/23-edge reverse subgraph containing
consumers and construction-adjacent nodes. It was useful as a broad blast
radius, but it did not identify which object literals construct a newly added
field. Treat this as dependency traversal rather than semantic field-level
change analysis.

## Staleness and synthetic update

The frozen three-file patch added an `attempts` property to interfaces and
object literals.

Before the patch:

- status reported zero modified files;
- search for `attempts` was empty.

After applying the patch but before sync:

- status reported three modified files;
- graph counts remained 93 nodes and 211 edges;
- search for `attempts` remained empty;
- file/range retrieval read the current disk and displayed the new property.

After `sync`:

- three changed files and 29 nodes were processed;
- internal sync time was 43 ms;
- wall time was 0.17 s and peak RSS was 99,112 KB;
- graph totals remained 93 nodes and 211 edges;
- `attempts` still was not independently searchable.

This is coherent with the graph's symbol granularity: interface/object-literal
property additions are not necessarily independent indexed symbols. Status is
the reliable stale-index check; node file mode can expose current disk content
even while graph queries remain stale.

`affected` accepted the explicit changed-file list and found seven dependent
files but no tests, because the fixture contains no test files. There is no
public command that accepts a patch and explains semantic change. The patch was
reversed and a final sync/reindex restored the frozen content.

## Installation, configuration, side effects, and network

`install --print-config` generated configurations for eight advertised targets:

- Claude
- Cursor
- Codex
- OpenCode
- Hermes
- Gemini
- Antigravity
- Kiro

An unknown target failed with exit 1 and listed known identifiers. Actual
installation and removal can modify host integration files and were not
authorized. Root no-argument installer behavior was likewise not run.

Important public environment controls include:

- `CODEGRAPH_MCP_TOOLS`
- `CODEGRAPH_NO_DAEMON`
- `CODEGRAPH_NO_WATCH`
- `CODEGRAPH_WATCH_DEBOUNCE_MS`
- `CODEGRAPH_DIR`
- `CODEGRAPH_TELEMETRY`
- `DO_NOT_TRACK`
- `CODEGRAPH_EXPLORE_LINENUMS`
- `CODEGRAPH_ADAPTIVE_EXPLORE`
- resolver cache, directory-watch, daemon-timeout, and Node override controls.

The default index skips ignored files and files larger than 1 MB. Node is
required; the package engine range is Node 20 through 24, while the embedded
library's `node:sqlite` path requires a sufficiently recent Node runtime.

Network- or host-affecting paths include upgrade/download, package installation,
telemetry transmission, and internal reasoning endpoints. Telemetry `status`
and `off` were verified in lane-local state with `DO_NOT_TRACK`; no event was
transmitted. No credential was made available.

## Targeted test evidence

Seven focused Vitest files ran through the isolated wrapper:

- 97 tests collected;
- 85 passed;
- 10 failed;
- 2 skipped.

Seven sync failures contained `spawnSync git EPERM` and are `UNAVAILABLE` in
this sandbox. Two status CLI failures produced undefined JSON, and one
`affected` CLI test returned an empty result. Those three tests do invoke a
child Node process, but their captured failures do not expose an `EPERM` (nor
another conclusive sandbox error), so their root cause remains
`UNRESOLVED_TEST_FAILURE`, not a verified sandbox limitation. Direct isolated
CLI probes of sync, status, and affected succeeded; this is useful conflicting
runtime evidence, but it does not convert the three focused-test failures into
passes. A less-restricted test run is required to classify them as product
defects or runner incompatibilities.

Vitest also wrote `.vite/vitest/results.json` at the repository root rather
than inside its configured lane. That isolation leak was moved intact to
`scratchpad/code-intelligence/raw-output/capability-discovery/codegraph/vite-leak/`;
the root `.vite` directory was removed. The leak is generated test-runner
state, not a source change.

## Token and resource accounting

Artifact estimates use `gpt-tokenizer@3.4.0:o200k_base`. They are serialized
artifact costs, not provider billing.

| Artifact | Bytes | `o200k_base` tokens |
| --- | ---: | ---: |
| Default one-tool MCP schema | 1,366 | 302 |
| Expanded static eight-tool schemas | 8,220 | 1,865 |
| Direct tiny-repo three-tool list | 4,764 | 1,094 |
| Indexed server instructions | 4,653 | 1,049 |
| Frozen probe schema | 6,530 | 1,562 |
| Frozen probe prompt | 4,133 | 856 |
| CLI explore output | 11,058 | 2,626 |
| Entire direct default MCP evidence JSONL | 18,953 | 5,006 |
| Failed Terra event stream | 801 | 237 |

The 5,006-token MCP number is the complete JSONL evidence stream, including
initialize/list/schema traffic and response framing; it must not be read as
the explore tool's standalone answer size. Measured indexing resource numbers
appear in [Fixture indexing and corpus coverage](#fixture-indexing-and-corpus-coverage).

## Agent-mediated Terra probe

Exactly one fresh `gpt-5.6-terra` medium-effort, ephemeral, read-only Codex
session was attempted. It was configured with only CodeGraph MCP, direct mode,
the default `explore` tool, the fixed prompt, and the frozen output schema.

The provider rejected the request before model execution:

```text
invalid_request_error: Invalid schema for response_format
'codex_output_schema': In context=(), 'allOf' is not permitted.
```

Consequences:

- no model answer was generated;
- no CodeGraph tool was called;
- no file read or fallback search occurred;
- provider input, cached-input, output, and reasoning tokens are `UNKNOWN`;
- the 2,487 ms elapsed time covers request rejection, not inference;
- the event stream is only 801 bytes because it contains setup and the schema
  rejection.

The frozen protocol allowed no retry. This is a shared probe-schema
compatibility defect, not a negative finding about CodeGraph. The deterministic
capability discovery remains complete, so the overall status is
`DONE_WITH_CONCERNS` rather than `BLOCKED`.

## Reproduction pattern

All commands should remain isolated. The general pattern is:

```bash
docs/research/harness-tools/codebase-intelligence/experiments/coding-agents/run-isolated.sh \
  codegraph <command> [arguments...]
```

Representative operations:

```bash
# Runtime inventory
.../run-isolated.sh codegraph node \
  scratchpad/code-intelligence/tools/codegraph/dist/bin/codegraph.js --help

# Initialize and inspect the disposable fixture
.../run-isolated.sh codegraph node \
  scratchpad/code-intelligence/tools/codegraph/dist/bin/codegraph.js init \
  scratchpad/code-intelligence/fixtures/codegraph --verbose
.../run-isolated.sh codegraph node \
  scratchpad/code-intelligence/tools/codegraph/dist/bin/codegraph.js status \
  scratchpad/code-intelligence/fixtures/codegraph --json

# Direct MCP mode avoids the shared Unix socket
CODEGRAPH_NO_DAEMON=1 CODEGRAPH_MCP_TOOLS=explore \
  .../run-isolated.sh codegraph node \
  scratchpad/code-intelligence/tools/codegraph/dist/bin/codegraph.js serve \
  scratchpad/code-intelligence/fixtures/codegraph
```

The literal `.../run-isolated.sh` abbreviation above means the tracked wrapper
path shown in the first command; it avoids machine-local absolute paths.

## Evidence map

Ignored reproducibility evidence is under:

- `scratchpad/code-intelligence/raw-output/capability-discovery/codegraph/help/`
- `scratchpad/code-intelligence/raw-output/capability-discovery/codegraph/runtime/`
- `scratchpad/code-intelligence/raw-output/capability-discovery/codegraph/vite-leak/`
- `scratchpad/code-intelligence/metrics/capability-discovery/codegraph/`
- `scratchpad/code-intelligence/sessions/capability-discovery/codegraph/`

Notable files include:

- `runtime/mcp-unindexed.jsonl`
- `runtime/mcp-default.jsonl`
- `runtime/mcp-expanded.jsonl`
- `runtime/mcp-direct-default-probe.jsonl`
- `runtime/mcp-direct-expanded-probes.jsonl`
- `runtime/targeted-tests-tool-cwd.txt`
- `runtime/update-stale-status.json`
- `runtime/update-sync-time.txt`
- `artifact-token-counts.json`
- `terra-probe-metrics.json`
- `events.jsonl`

No ignored artifact is a substitute for the tracked conclusions in this
report. The raw files exist so later reviewers can reproduce counts, inspect
failure text, and distinguish tool behavior from interpretation.

## Appendix A: exhaustive CLI option ledger

This appendix closes the gap between command-family inventory and individual
option coverage. Dispositions apply to the exact frozen revision. `VERIFIED`
means the option or action ran in the isolated lane; `PARTIAL` means a useful
subset ran or the behavior has a demonstrated limitation; `UNTESTED` means the
surface is declared but the required fixture condition was absent;
`RESTRICTED` means the meaningful probe would require network, credentials,
host/global mutation, unsafe-path bypass, or a long-running process.

All deterministic CLI operations used the already measured 0.30 s initial
setup. Unless a separate wall time is stated, per-query elapsed time was not
captured and is `UNKNOWN`. Model tokens are exactly 0: these paths are local
AST/SQLite operations and no model backend was invoked.

| Surface | Complete arguments/options | Coverage, effects, limits, and final disposition | Evidence; representative output |
| --- | --- | --- | --- |
| root | `-V/--version`, `-h/--help`; no command enters interactive installer | help/version `VERIFIED`; no-command installer `RESTRICTED` because it writes host agent configuration | `help/root.txt`, `help/version.txt`; help output size not separately counted |
| `init [path]` | `-i/--index` deprecated compatibility flag; `-f/--force`; `-v/--verbose`; help | normal and verbose initial index `VERIFIED`; deprecated `--index` `UNTESTED` because indexing is already unconditional; unsafe-path refusal `VERIFIED`; `--force` `RESTRICTED` because its meaningful purpose is bypassing that safety guard | `runtime/init-verbose-time.txt` 2,120 B/738 tok; `boundary-unsafe-home.txt` 330 B/78 tok |
| `uninit [path]` | `-f/--force`; help | `--force` `VERIFIED` on disposable index; deletes only `.codegraph/` | final cleanup console evidence; output bytes/tokens `UNKNOWN` |
| `index [path]` | `-f/--force`, `-q/--quiet`, `-v/--verbose`; help | normal and `--quiet` full index `VERIFIED`; verbose worker reporting `PARTIAL` via equivalent init path; `--force` `RESTRICTED` for unsafe-root bypass | `runtime/full-reindex-time.txt` 1,022 B/303 tok; 0.24 s, 108,076 KB |
| `sync [path]` | `-q/--quiet`; help | clean, changed, and quiet sync `VERIFIED`; updates index only | `sync-clean.txt` 290 B/99 tok; `update-sync-time.txt` 1,287 B/441 tok; changed sync 0.17 s |
| `status [path]` | `-j/--json`; help | text, JSON, stale, and uninitialized modes `VERIFIED`; read-only | `status-json.txt` 958 B/265 tok; `status-text.txt` 857 B/297 tok; `update-stale-status.json`; elapsed `UNKNOWN` |
| `query <search>` | `-p/--path`, `-l/--limit` default 10, `-k/--kind`, `-j/--json`; help | alternate path, limit, kind, and JSON `VERIFIED`; invalid kind silently returns empty with exit 0, so validation is `PARTIAL` | `query-function.txt` 1,349 B/403 tok; `query-normalize.txt` 3,701 B/1,113 tok; invalid 170 B/38 tok |
| `explore <query...>` | `-p/--path`, `--max-files`; help | path/default and bounded source exploration `VERIFIED`; semantic synthesis `PARTIAL` because of the false cross-language edge | `explore-lifecycle.txt` 11,058 B/2,626 tok; `explore-collision.txt` 8,225 B/1,934 tok |
| `node <name>` | `-p/--path`, `-f/--file`, `--offset`, `--limit`, `--symbols-only`; help | symbol, disambiguated file, whole-file, range, and symbols-only modes `VERIFIED`; file mode reads current disk while graph relationships can be stale | `node-workflow.txt` 1,209 B/282 tok; `node-file-range.txt` 541 B/122 tok; `node-file-symbols-correct.txt` 1,004 B/244 tok |
| `files` | `-p/--path`, `--filter`, `--pattern`, `--format` enum tree/flat/grouped default tree, `--max-depth`, `--no-metadata`, `-j/--json`; help | every filtering/format family `VERIFIED`; invalid format fallback makes validation `PARTIAL` | `files-tree.txt` 1,321 B/441 tok; `files-grouped.txt` 1,846 B/578 tok; `files-core.txt` 889 B/266 tok; `files-ts.txt` 1,632 B/502 tok |
| `daemon` / `daemons` | help only; interactive selection stops a daemon | empty-manager/list behavior `VERIFIED`; live daemon start/stop `UNAVAILABLE` here because Unix socket bind returned `EPERM` | `daemon-list.txt` 43 B/17 tok; daemon failure in MCP runtime evidence |
| `unlock [path]` | help only | no-lock case `VERIFIED`; stale-lock deletion `UNTESTED` because no safe stale lock existed at probe time | `unlock-no-lock.txt` 50 B/19 tok |
| `callers <symbol>` | `-p/--path`, `-l/--limit` default 20, `-j/--json`; help | options and ordinary symbol `VERIFIED`; ambiguous CLI name aggregation `PARTIAL` | `callers-run.txt` 351 B/94 tok; `callers-normalize.txt` 762 B/213 tok |
| `callees <symbol>` | `-p/--path`, `-l/--limit` default 20, `-j/--json`; help | options and lifecycle call set `VERIFIED` | `callees-run.txt` 1,160 B/326 tok |
| `impact <symbol>` | `-p/--path`, `-d/--depth` default 2, `-j/--json`; help | options and reverse traversal `VERIFIED`; patch semantics and ambiguous CLI names `PARTIAL` | `impact-workresult.txt` 3,535 B/1,021 tok; `impact-normalize.txt` 1,356 B/393 tok |
| `affected [files...]` | `-p/--path`, `--stdin`, `-d/--depth` default 5, `-f/--filter`, `-j/--json`, `-q/--quiet`; help | positional path/depth/JSON and changed-list operation `VERIFIED`; stdin/filter/quiet variants `UNTESTED` because the fixture has no tests with which to distinguish their behavior; capability remains `PARTIAL` | `affected-contracts.txt` 288 B/72 tok; `update-stale-affected.txt` 361 B/90 tok |
| `install` | `-t/--target` comma list or auto/all/none; `-l/--location` global/local; `-y/--yes`; `--no-permissions`; `--print-config <id>`; help | write-free `--print-config` for all eight targets and invalid target `VERIFIED`; target/location/yes/no-permissions actual writes `RESTRICTED` because they mutate host/project integration configuration | eight `install-print-config-*.txt`, 198–352 B and 53–97 tok each |
| `uninstall` | `-t/--target` list/all; `-l/--location` global/local; `-y/--yes`; help | all three options `VERIFIED` as a lane-local global no-op across eight unconfigured agents; deletion of a real host integration `RESTRICTED` | isolated console evidence; output bytes/tokens `UNKNOWN` |
| `telemetry [action]` | actions `status`, `on`, `off`; help | status/off `VERIFIED` in lane-local state; on/transmission `RESTRICTED` by no-network/no-telemetry policy | telemetry lane state; output bytes/tokens `UNKNOWN` |
| `upgrade [version]` | optional version; `--check`; `-f/--force`; help | all actions `RESTRICTED`: even check contacts package/release endpoints; install mutates package files | `help/upgrade.txt`; output/query/model usage `UNKNOWN`/`UNKNOWN`/0 |
| `version` | help; aliases root `-v/--version` | command and alias `VERIFIED`, reports 1.0.1 | `help/version.txt`; runtime output bytes/tokens `UNKNOWN` |
| hidden `serve` | `-p/--path`, `--mcp`, `--no-watch`; help | all flags `VERIFIED` in direct stdio mode; shared daemon unavailable in sandbox | `serve-info.txt` 765 B/262 tok and MCP JSONL files |
| hidden `prompt-hook` | stdin JSON `{prompt,cwd}`; help | structural prompt case `VERIFIED`; writes no source | `prompt-hook-structural.txt` 6,141 B/1,458 tok |
| help router | `help [command]` and every command `--help` | root, 20 public, and 2 hidden help surfaces `VERIFIED`, all exit 0 | `help/*.txt` |

Safe unexercised variants are explicitly `UNTESTED`; unsafe or externally
effective variants are explicitly `RESTRICTED`.

## Appendix B: configuration-control ledger

The table distinguishes user-facing behavior controls from internal diagnostics
and child-process plumbing. Source registration is exact evidence that a
control exists; runtime verification is stated separately.

| Control | Meaning/default/validation | Runtime status and applicability | Evidence |
| --- | --- | --- | --- |
| `CODEGRAPH_DIR` | plain directory name only; default `.codegraph`; invalid path separator, absolute path, or `..` falls back | `UNTESTED`; useful for Windows/WSL dual indexes; changes index location | `src/directory.ts:12-78`, README around line 722 |
| `CODEGRAPH_MCP_TOOLS` | comma allowlist; ordinary default lists explore only | `VERIFIED` for default, all-eight proxy, and tiny-repo dynamic list | `runtime/mcp-default.jsonl`, `mcp-expanded.jsonl`, direct probes |
| `CODEGRAPH_NO_DAEMON` | truthy selects direct MCP | `VERIFIED`; required in this sandbox | `src/mcp/index.ts:125-267`, direct MCP JSONL |
| `CODEGRAPH_NO_WATCH` | `1` disables watcher | `VERIFIED` through `serve --no-watch`; makes index manually synchronized | `src/sync/watch-policy.ts:78-88`, MCP direct setup |
| `CODEGRAPH_FORCE_WATCH` | `1` overrides automatic watch suppression | `UNTESTED`; needs a platform condition that would otherwise suppress watch | `src/sync/watch-policy.ts:78-88` |
| `CODEGRAPH_WATCH_DEBOUNCE_MS` | integer 100–60,000 ms; invalid value ignored; default 2,000 ms | `PARTIAL`; SDK watcher ran with explicit 100 ms option, env override not separately run | `src/mcp/engine.ts:269-289`, SDK output |
| `CODEGRAPH_MAX_DIR_WATCHES` | positive integer, default 50,000 | `UNTESTED`; only relevant to large Linux directory trees | `src/sync/watcher.ts:123-137` |
| `CODEGRAPH_EXPLORE_LINENUMS` | default on; `0` disables line numbers | `PARTIAL`; default line-number output verified, disabled form untested | `src/mcp/tools.ts:268-272`, explore evidence |
| `CODEGRAPH_ADAPTIVE_EXPLORE` | default on; `0`/`false` disables adaptive sizing | `PARTIAL`; tiny-repo adaptive cap observed, disabled form untested | `src/mcp/tools.ts:285-288`, direct `tools/list` |
| `CODEGRAPH_RANK_NO_MULTITERM` | `1` disables multi-term ranking contribution | `UNTESTED`; ranking diagnostic/escape hatch | `src/mcp/tools.ts:2532-2534` |
| `CODEGRAPH_VALUE_REFS` | default on; `0` disables value-reference edges | `PARTIAL`; default graph includes reference edges, disabled extraction untested | `src/extraction/tree-sitter.ts:324-329` |
| `CODEGRAPH_RESOLVER_CACHE_SIZE` | positive integer, default 5,000 per resolver cache | `UNTESTED`; only materially distinguishable on large resolution batches | `src/resolution/index.ts:51-61` |
| `CODEGRAPH_TELEMETRY` | environment override for telemetry policy | disabled form `VERIFIED`; enabled/transmit form `RESTRICTED` | `src/bin/codegraph.ts:2054-2071`, telemetry lane |
| `DO_NOT_TRACK` | standard telemetry opt-out | `VERIFIED`; wrapper forces it | wrapper and README around line 613 |
| `CODEGRAPH_ASCII` / `CODEGRAPH_UNICODE` | terminal glyph override | `UNTESTED`; presentation only | `src/ui/glyphs.ts:14-23` |
| `CODEGRAPH_DEBUG` | include stack/detail in error rendering | `UNTESTED`; diagnostics only | `src/errors.ts:181` |
| `CODEGRAPH_MCP_DEBUG` | MCP/watchdog diagnostic stderr | `UNTESTED`; diagnostics only | `src/mcp/index.ts:329`, liveness watchdog |
| `CODEGRAPH_MCP_LOG_ATTACH` | proxy attach logging diagnostic | `UNTESTED`; diagnostics only | `src/mcp/proxy.ts:44` |
| `CODEGRAPH_DAEMON_IDLE_TIMEOUT_MS` | nonnegative integer; default 300,000 ms | `UNAVAILABLE` with daemon socket blocked | `src/mcp/daemon.ts:60,506-511` |
| `CODEGRAPH_DAEMON_MAX_IDLE_MS` | nonnegative integer; default 1,800,000 ms; 0 disables | `UNAVAILABLE` with daemon socket blocked | `src/mcp/daemon.ts:70,514-519` |
| `CODEGRAPH_DAEMON_CLIENT_SWEEP_MS` | nonnegative integer; default 30,000 ms; 0 disables | `UNAVAILABLE` with daemon socket blocked | `src/mcp/daemon.ts:73,522-527` |
| `CODEGRAPH_PPID_POLL_MS` | nonnegative integer; default 5,000 ms | `PARTIAL`; parent liveness path existed but timing override untested | `src/mcp/index.ts:63,103-107` |
| `CODEGRAPH_NO_WATCHDOG` | truthy disables main-thread watchdog | `UNTESTED`; long-lived daemon only | `src/mcp/liveness-watchdog.ts:35-109` |
| `CODEGRAPH_WATCHDOG_TIMEOUT_MS` | positive number; default 60,000 ms | `UNTESTED`; long-lived daemon only | `src/mcp/liveness-watchdog.ts:49-66` |
| `CODEGRAPH_NO_PROMPT_HOOK` / `CODEGRAPH_PROMPT_HOOK=0` | disables installed Claude front-load hook | default hook logic `VERIFIED`; disable override `UNTESTED` | `src/bin/codegraph.ts:1041`, prompt-hook evidence |
| `CODEGRAPH_ALLOW_UNSAFE_NODE` | bypasses supported Node-version refusal | `RESTRICTED`; intentionally bypasses runtime safety check | `src/bin/node-version-check.ts`, `src/bin/codegraph.ts:71-81` |
| `CODEGRAPH_NO_RELAUNCH` | disables WASM/V8 flag relaunch | `UNTESTED`; process-runtime escape hatch | `src/extraction/wasm-runtime-flags.ts:87-95` |

Internal/environment plumbing is also fully accounted for:

| Internal control | Meaning/default | Disposition |
| --- | --- | --- |
| `CODEGRAPH_DAEMON_INTERNAL` | marks the detached daemon child and selects socket-listen behavior | `UNAVAILABLE` here because socket bind is denied; internal, not user-facing |
| `CODEGRAPH_HOST_PPID` | carries the original host parent PID across WASM relaunch | `UNTESTED`; internal liveness plumbing |
| `CODEGRAPH_WASM_RELAUNCHED` | one-time relaunch guard | `UNTESTED`; internal process plumbing |
| `CODEGRAPH_INSTALL_DIR` | preserves a custom install directory across upgrade | `RESTRICTED`; upgrade/network/host mutation |
| `CODEGRAPH_VERSION` | upgrade version pin alternative to positional version | `RESTRICTED`; upgrade/network/host mutation |
| `CODEGRAPH_LOGIN_URL` | test/override base for dormant device login | `RESTRICTED`; network and no registered public login command |
| `CODEGRAPH_OFFLOAD_DISABLE` | disables dormant reasoning offload | `UNTESTED`; no registered public offload command |
| `CODEGRAPH_OFFLOAD_URL`, `CODEGRAPH_OFFLOAD_KEY`, `CODEGRAPH_OFFLOAD_MODEL` | BYO endpoint, credential, and model; managed default model or `gpt-oss-120b` depending origin | `RESTRICTED`; network/credential path and unregistered publicly |
| `CODEGRAPH_OFFLOAD_EFFORT`, `CODEGRAPH_OFFLOAD_STYLE` | defaults `low` and `plain` | `RESTRICTED`; unregistered model path |
| `CODEGRAPH_OFFLOAD_TIMEOUT_MS`, `CODEGRAPH_OFFLOAD_MAXTOKENS` | defaults 20,000 ms and 12,000 tokens | `RESTRICTED`; unregistered model path |
| `CODEGRAPH_OFFLOAD_STRIP`, `CODEGRAPH_OFFLOAD_DEBUG` | response stripping and diagnostics, enabled by `1` | `UNTESTED`; unregistered model path |
| `CODEGRAPH_OFFLOAD_USAGE_LOG` | append-only per-call usage JSONL path | `RESTRICTED`; only meaningful if offload/network executes |

`CODEGRAPH_SECTION_START`, `CODEGRAPH_SECTION_END`,
`CODEGRAPH_INSTRUCTIONS_BLOCK`, and their `CODEGRAPH_START`/`CODEGRAPH_END`
marker text are exported installer constants, not environment configuration.
They delimit managed instruction blocks. The reasoning source comments mention
an offload CLI, but no `offload` or `login` command is registered in root help
or `src/bin/codegraph.ts` at this revision; those controls are therefore not
promoted into the public capability contract.

## Appendix C: complete MCP schemas and operation costs

Every schema below comes from runtime `tools/list`, not a hand-reconstructed
type. All tools require an initialized `.codegraph/` at `projectPath` or the
current project. They are read-only with respect to source. They read SQLite
and, for source-returning node/explore modes, current on-disk source. No tool
invokes a model, so model tokens are 0.

| Tool | Required input | Optional inputs, types, defaults, enums | Output and effects | Disposition |
| --- | --- | --- | --- | --- |
| `codegraph_search` | `query: string` | `kind: string` enum function/method/class/interface/type/variable/route/component; `limit: number=10`; `projectPath: string` | text locations/signatures; no source write | `VERIFIED` |
| `codegraph_callers` | `symbol: string` | `file: string` disambiguator; `limit: number=20`; `projectPath` | text definitions and inbound callers; no write | `VERIFIED` |
| `codegraph_callees` | `symbol: string` | `file: string`; `limit: number=20`; `projectPath` | text outbound callees/references; no write | `VERIFIED` |
| `codegraph_impact` | `symbol: string` | `file: string`; `depth: number=2`; `projectPath` | text reverse dependency traversal; no write; not diff-aware | `PARTIAL` |
| `codegraph_node` | none at schema level; operationally `symbol` or `file` | `symbol:string`; `includeCode:boolean=false`; `file:string`; `offset:number`; `limit:number` (file default whole file, cap 2,000 lines); `symbolsOnly:boolean=false`; `line:number`; `projectPath` | symbol trail or current line-numbered file source; read-only | `VERIFIED` |
| `codegraph_explore` | `query: string` | `maxFiles:number=12`; `projectPath` | ranked source, call path, dynamic links, blast radius; reads source, no write | `PARTIAL` |
| `codegraph_status` | none | `projectPath:string` | index counts/backend/kinds/languages; read-only | `VERIFIED` |
| `codegraph_files` | none | `path:string`; `pattern:string`; `format:string=tree` enum tree/flat/grouped; `includeMetadata:boolean=true`; `maxDepth:number`; `projectPath` | indexed file tree/list; read-only | `VERIFIED` |

The schemas do not declare numeric minima/maxima. Operational validation is
therefore implementation-side. `projectPath` can open another initialized
project, which is a read scope expansion and should be constrained by the
calling harness.

| Runtime call | Query | Output bytes | `o200k_base` tokens | Query time | Model tokens | Exact evidence |
| --- | --- | ---: | ---: | --- | ---: | --- |
| search | `normalize` collision | 537 | 137 | `UNKNOWN` | 0 | `runtime/mcp-direct-expanded-probes.jsonl`, id 3 |
| callers | core `normalize`, file-scoped | 352 | 92 | `UNKNOWN` | 0 | same, id 4 |
| callers | gateway `normalize`, file-scoped | 369 | 96 | `UNKNOWN` | 0 | same, id 5 |
| callees | `run` | 449 | 118 | `UNKNOWN` | 0 | same, id 6 |
| impact | `WorkResult` | 641 | 191 | `UNKNOWN` | 0 | same, id 7 |
| node | workflow file lines 10–21 | 639 | 162 | `UNKNOWN` | 0 | same, id 8 |
| explore | lifecycle query | 11,730 | 2,809 | `UNKNOWN` | 0 | same, id 9 |
| status | fixture | 451 | 166 | `UNKNOWN` | 0 | same, id 10 |
| files | grouped | 691 | 177 | `UNKNOWN` | 0 | same, id 11 |
| search failure | missing symbol | 46 | 9 | `UNKNOWN` | 0 | same, id 12 |
| unknown tool | `codegraph_unknown` | JSON-RPC error | not separately counted | `UNKNOWN` | 0 | same, id 13, error -32602 |

MCP setup was the shared 0.30 s index build plus a stdio initialize handshake.
Handshake elapsed time was not separately captured. The default schema is
1,366 B/302 tokens; all-eight static schemas are 8,220 B/1,865 tokens; direct
tiny-repo discovery listed three schemas at 4,764 B/1,094 tokens. Server
instructions add 4,653 B/1,049 tokens before any tool answer.

## Appendix D: language, entity, edge, and resolver dispositions

Registry presence alone is not runtime verification. This appendix gives every
declared value an allowed final disposition and states the missing prerequisite
for unexercised surfaces.

### Languages

| Declared language | Disposition | Evidence or prerequisite |
| --- | --- | --- |
| `typescript` | `VERIFIED` | 12 fixture files, including `.d.ts`; runtime status |
| `rust` | `VERIFIED` | 2 fixture files; runtime status |
| `unknown` | `PARTIAL` | sentinel classification exists; `.capfixture` was correctly skipped rather than parsed |
| `javascript`, `tsx`, `jsx` | `UNTESTED` | grammar/extractor registered; no frozen fixture file in these languages |
| `python`, `go`, `java`, `c`, `cpp`, `csharp`, `razor`, `php`, `ruby` | `UNTESTED` | requires representative frozen source and expected-anchor assertions |
| `swift`, `kotlin`, `dart`, `svelte`, `vue`, `astro`, `liquid`, `pascal` | `UNTESTED` | requires representative frozen source; framework-aware languages also need framework fixtures |
| `scala`, `lua`, `luau`, `objc`, `r`, `yaml`, `twig`, `xml`, `properties` | `UNTESTED` | requires representative frozen source and expected-anchor assertions |

All 32 registry values are accounted for: 2 `VERIFIED`, 1 `PARTIAL`, and 29
`UNTESTED`. “Supported” here means declared parser routing, not demonstrated
semantic precision for the 29 absent languages.

### Node/entity kinds

| Disposition | Kinds | Evidence or prerequisite |
| --- | --- | --- |
| `VERIFIED` | `file`, `class`, `struct`, `interface`, `trait`, `function`, `method`, `property`, `constant`, `enum`, `enum_member`, `type_alias`, `import` | present in fixture runtime `nodesByKind` |
| `UNTESTED` | `module`, `protocol`, `field`, `variable`, `namespace`, `parameter`, `export`, `route`, `component` | declared but absent from frozen fixture; needs language/framework-specific fixtures |

All 22 node kinds are accounted for: 13 `VERIFIED`, 9 `UNTESTED`. Property
presence does not imply every property occurrence becomes a node; the
`attempts` update demonstrated that limitation.

### Edge kinds

| Disposition | Edge kinds | Evidence or prerequisite |
| --- | --- | --- |
| `VERIFIED` | `contains`, `calls`, `imports`, `extends`, `implements`, `references`, `instantiates` | present in fixture runtime `edgesByKind` |
| `UNTESTED` | `exports`, `type_of`, `returns`, `overrides`, `decorates` | declared but absent from frozen fixture; needs targeted syntax/expected edges |

All 12 edge kinds are accounted for: 7 `VERIFIED`, 5 `UNTESTED`. A declared
edge kind does not guarantee cross-file resolution correctness; ambiguous name
matching remains best effort.

### Framework/integration resolvers

No framework was detected in the frozen fixture, so every resolver is
`UNTESTED`, not `VERIFIED`:

| Resolver | Disposition | Required proof fixture |
| --- | --- | --- |
| `spring`, `play`, `aspnet`, `laravel`, `rails`, `nestjs` | `UNTESTED` | framework routes/controllers/dependency wiring in their host language |
| `vue`, `svelte`, `astro`, `react`, `express` | `UNTESTED` | component/template/route and framework-call anchors |
| `swiftui`, `uikit`, `vapor`, `swift-objc-bridge` | `UNTESTED` | Swift/Objective-C UI, server, and bridge anchors |
| `go`, `rust` | `UNTESTED` | resolver-specific framework/conformance chains, beyond basic language parsing |
| `fabric-view`, `react-native-bridge`, `expo-modules` | `UNTESTED` | native/JavaScript boundary fixtures |
| `drupal`, `django`, `flask`, `fastapi` | `UNTESTED` | route/hook/controller fixtures and expected framework edges |

All 24 registered resolvers are named. Source registry evidence is
`src/resolution/frameworks/index.ts`; runtime evidence is the SDK
`getDetectedFrameworks: []` result. Documentation text that says 17 frameworks
is stale relative to this registry.

## Appendix E: complete JavaScript facade

The CommonJS package entry exported 38 runtime names in the isolated probe.
The entire probe took 0.80 s, peaked at 133,264 KB RSS, and produced a
5,435-byte/1,591-token JSON result. Model tokens were 0. Evidence:
`runtime/sdk-probe.cjs`, `runtime/sdk-probe-output.json`, and
`runtime/sdk-probe-time.txt`.

### `CodeGraph` class: all 66 public methods

| Method group | Every method in group | Result, effects, and disposition |
| --- | --- | --- |
| static lifecycle | `init`, `initSync`, `open`, `openSync`, `isInitialized` | all `VERIFIED` using fixture or lane-home temporary projects; init/open can create/open SQLite and index |
| handle lifecycle | `reopenIfReplaced`, `close`, `destroy`, `uninitialize`, `getProjectRoot` | `close`, `destroy`, `uninitialize`, root `VERIFIED`; replacement-healing false case `VERIFIED`, actual inode-replacement case `UNTESTED`; uninitialize deletes only the temporary project's index |
| indexing | `indexAll`, `indexFiles`, `sync`, `isIndexing` | full index via `init({index:true})`, sync, and state `VERIFIED`; `indexFiles` `PARTIAL` because an opened facade returned `parser_error` for TypeScript despite CLI/full init support |
| watcher | `watch`, `unwatch`, `isWatching`, `isWatcherDegraded`, `getWatcherDegradedReason`, `getPendingFiles`, `waitUntilWatcherReady` | lifecycle and healthy empty state `VERIFIED`; actual edit event/degraded watcher `UNTESTED` |
| freshness | `getChangedFiles`, `getLastIndexedAt`, `getIndexBuildInfo`, `isIndexStale` | clean state and build stamp `VERIFIED`; stale state independently verified by CLI |
| extraction/resolution | `extractFromSource`, `resolveReferences`, `resolveReferencesBatched`, `getDetectedFrameworks`, `reinitializeResolver` | resolver calls and empty framework result `VERIFIED`; direct virtual TypeScript extraction `PARTIAL` because it returned zero nodes in the opened facade |
| statistics/backend | `getStats`, `getBackend`, `getJournalMode` | `VERIFIED`: 93/211 before SDK mutation, node-sqlite, WAL |
| node lookup/search | `getNode`, `getNodesInFile`, `getNodesByKind`, `getNodesByName`, `searchNodes`, `getProjectNameTokens`, `getTopRouteFile`, `getRoutingManifest` | all calls `VERIFIED`; route methods correctly returned null for fixture without routes |
| raw graph/file access | `getOutgoingEdges`, `getIncomingEdges`, `getFile`, `getFiles`, `getContext` | all `VERIFIED`; read-only |
| traversal | `traverse`, `getCallGraph`, `getTypeHierarchy`, `findUsages`, `getCallers`, `getCallees`, `getImpactRadius`, `findPath`, `getAncestors`, `getChildren` | all `VERIFIED`; same best-effort ambiguity/semantic limits as CLI/MCP |
| dependency analysis | `getFileDependencies`, `getFileDependents`, `findCircularDependencies`, `findDeadCode`, `getNodeMetrics` | all `VERIFIED`; outputs are static graph results, not correctness proofs |
| context | `getCode`, `findRelevantContext`, `buildContext` | all `VERIFIED`; current source read and graph-derived context, no model |
| database maintenance | `optimize`, `clear` | both `VERIFIED`; optimize mutates index layout, clear tested only on disposable temporary index |

### Remaining runtime exports

| Runtime exports | Capability and final disposition |
| --- | --- |
| `CodeGraph`, `default` | facade/default alias presence and methods `VERIFIED` |
| `DatabaseConnection`, `QueryBuilder`, `getDatabasePath` | embedded database building blocks exported `VERIFIED`; direct low-level query construction `UNTESTED` because facade coverage was sufficient |
| `getCodeGraphDir`, `isInitialized`, `findNearestCodeGraphRoot`, `CODEGRAPH_DIR` | directory helpers exported `VERIFIED`; facade/static initialization exercised; alternate-dir and nearest-root variants `UNTESTED` |
| `detectLanguage`, `isLanguageSupported`, `isGrammarLoaded`, `getSupportedLanguages`, `initGrammars`, `loadGrammarsForLanguages`, `loadAllGrammars` | grammar API exports `VERIFIED` as present; initialization was exercised indirectly; per-language loaders are `UNTESTED` for the 29 absent languages |
| `CodeGraphError`, `FileError`, `ParseError`, `DatabaseError`, `SearchError`, `VectorError`, `ConfigError` | error class exports `VERIFIED` as present; individual construction/formatting paths `UNTESTED` |
| `Logger` | type-only TypeScript export; no runtime value, therefore `NOT_APPLICABLE` as a JavaScript callable |
| `setLogger`, `getLogger`, `silentLogger`, `defaultLogger` | logger runtime exports `VERIFIED` as present; logger replacement `UNTESTED` |
| `Mutex`, `FileLock` | exports `VERIFIED`; used indirectly by indexing; direct contention behavior `UNTESTED` |
| `processInBatches`, `debounce`, `throttle`, `MemoryMonitor` | utility exports `VERIFIED` as present; direct utility semantics `UNTESTED` |
| `FileWatcher`, `LockUnavailableError` | exports `VERIFIED`; watcher used through facade; direct constructor/lock-error path `UNTESTED` |
| `MCPServer` | export and direct stdio runtime `VERIFIED`; shared-daemon transport unavailable in sandbox |
| `LANGUAGES`, `NODE_KINDS` | runtime constants `VERIFIED` and exhaustively dispositioned in Appendix D |
| `IndexProgress`, `IndexResult`, `SyncResult`, `ResolutionResult`, `WatchOptions`, `PendingFile`, and `export * from './types'` interfaces | type-only compile-time surfaces; `NOT_APPLICABLE` as runtime JavaScript callables |

The facade's significant new concern is not mere lack of testing:
`indexFiles` and `extractFromSource` could not acquire the TypeScript parser
when called on both sync-opened and async-opened instances, while CLI
initialization and `CodeGraph.init(...,{index:true})` indexed TypeScript. That
is a public embedded-API prerequisite or defect requiring focused upstream
investigation before relying on per-file SDK indexing.

## Appendix F: per-capability evidence and measurement interpretation

Evidence filenames, not narrative confidence, determine what was actually run.
For any row above without a measured elapsed time, query time is `UNKNOWN`.
For any output not captured to a file, bytes and artifact tokens are `UNKNOWN`.
This is deliberate; timings and byte counts are never inferred from file
content or tool claims.

| Capability family | Setup time | Query/run time | Representative bytes/tokens | Model tokens | Read/write effects | Applicability and limitation |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| init/index | 0.30 s first setup | 0.24 s full reindex | 2,120/738 initial; 1,022/303 reindex | 0 | writes `.codegraph` only | required before all graph queries |
| sync/status | shared | 0.17 s changed sync; other query time `UNKNOWN` | sync 1,287/441; status JSON 958/265 | 0 | sync writes index; status read-only | status is freshness authority |
| query/node/files | shared | `UNKNOWN` | 170–3,701 B; 38–1,113 tok across named evidence | 0 | read index; node may read source | precise structural lookup; validation and stale-source caveats |
| callers/callees/impact/affected | shared | `UNKNOWN` | 288–3,535 B; 72–1,021 tok | 0 | read-only | dependency traversal; ambiguous names/diff-awareness limits |
| explore | shared | `UNKNOWN` | 8,225–11,058 B; 1,934–2,626 tok CLI | 0 | reads index and source | best orientation, but synthesized edge needs confirmation |
| MCP | shared plus handshake `UNKNOWN` | `UNKNOWN` | per-tool table in Appendix C | 0 | read-only | direct mode verified; daemon unavailable |
| SDK facade | shared | 0.80 s complete probe | 5,435 B/1,591 tok | 0 | reads/writes disposable indexes; temporary clear/uninitialize | broad embedded API, per-file parser caveat |
| installer config | none beyond CLI | `UNKNOWN` | 198–352 B; 53–97 tok | 0 | print only | actual integration writes restricted |
| telemetry off/status | none beyond CLI | `UNKNOWN` | `UNKNOWN` | 0 | lane-local config/buffer | transmission restricted |
| upgrade | not run | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` because no operation occurred | network/package mutation | restricted |
| Terra probe | MCP index ready | 2.487 s rejection | 801 B/237 tok event stream | provider usage `UNKNOWN` | no tool call/read/write | invalid frozen schema; no retry in this task |
