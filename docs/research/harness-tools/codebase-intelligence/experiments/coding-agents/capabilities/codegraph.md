# CodeGraph capability discovery

Status: `DONE_WITH_CONCERNS`

Recorded: 2026-07-24

Tracking: `orch-8sk.16.2`

## Authoritative evidence generation

This report is authoritative only for the following frozen identities:

| Component | Current identity |
| --- | --- |
| CodeGraph source | `03666584ed9836d7954cbb19e2252081b96fcad9` |
| Package | `@colbymchenry/codegraph` 1.0.1 |
| Built CLI SHA-256 | `f6ae07cc5ce347eb30fa06ca2091b61f5abaa24d36b43b16b42504c50323de47` |
| Fixture source commit | `e7ddad2c44321f7b50e60c923b8f0733fb757874` |
| Fixture manifest digest | `fc12b07aa2219f346ee1e00f52875efae8c52bbb12dc410456e9457ea1b58e24` |
| Synthetic patch SHA-256 | `17f48230009d36b4140213ed39e38fccb9a42a0045483e8798d27f5f996bf408` |
| Artifact tokenizer | `gpt-tokenizer@3.4.0:o200k_base` |

The machine-readable identity is
`scratchpad/code-intelligence/raw-output/capability-discovery/codegraph/current/identity-manifest.json`.

All earlier deterministic results tied to fixture commit
`faa03d6bb4e0855f57f76b0485a46a54f4d83d62` and manifest
`f9cf965fd10a1852f80c7713479e0c1935baa70607dbed66d3b0606fe5338bf9`
are superseded. The earlier Terra event stream is also superseded because it
used that fixture generation. A final user-approved current-fixture probe ran
after repairing the nested Codex sandbox and initializing an isolated
`.codegraph-probe` index. The provider exited 0 after 21 successful CodeGraph
calls with zero unrelated MCP calls and zero contamination. Both output schemas
and the canonical output validator passed. The strict runner nevertheless
classified the run `BLOCKED_OR_INVALID` because the model reordered its
redundant `operations` summary relative to the machine audit. Agent-mediated
behavior is therefore exercised and usable as evidence, but the run is not a
strict protocol pass and must not be labeled `VALIDATED`.
The complete run artifacts are under
`scratchpad/code-intelligence/sessions/capability-runner/codegraph/codegraph-bounded-final-validated/`.

## Scope and isolation

Discovery covered CodeGraph only. It did not read another tool's output,
another capability report, Pi, Codex, or a live subject repository. Every tool
operation ran through the tracked isolation wrapper with a lane-local home,
cache, configuration, state, and temporary directory. No provider credential or
ordinary Git credential was inherited.

The shared fixture was observed being reset concurrently between a successful
index build and MCP initialization. To prevent cross-agent cleanup from
invalidating evidence, all authoritative behavior probes ran against a
CodeGraph-owned local clone at
`scratchpad/code-intelligence/indexes/codegraph/current-fixture`. That clone
was verified at the exact frozen commit and digest above. It is a probe lane,
not a new source fixture.

No network fetch, package install, credentialed operation, live-submodule
mutation, or real host integration write was performed. Material integration
writes targeted only disposable global homes and a disposable local project
inside the CodeGraph lane, with `DO_NOT_TRACK=1`. The synthetic patch was
applied only inside the disposable clone and reversed. Temporary SDK edits and
destructive API checks ran only under the isolated lane home.

## Result at a glance

| Area | Current result | Disposition |
| --- | --- | --- |
| Offline index | 14 code files, 93 nodes, 211 edges; TypeScript and Rust | `VERIFIED` |
| Build/update | full index, clean sync, stale detection, three-file incremental sync, patch reversal | `VERIFIED` |
| Structural queries | search, source retrieval, callers, callees, files, status | `VERIFIED` |
| Architecture synthesis | useful source-rich lifecycle, but a false TypeScript-to-Rust same-name edge | `PARTIAL` |
| Ambiguous names | path-qualified search and MCP file disambiguation work; CLI traversal aggregates definitions | `PARTIAL` |
| Change analysis | status and explicit-file `affected` work; no public patch-aware semantic diff | `PARTIAL` |
| MCP | 1 default tool, 8 statically exposed opt-in definitions, 3 dynamically listed on this tiny repository; all 8 handlers callable | `PARTIAL` |
| Shared daemon | Unix socket bind denied by this sandbox; documented direct stdio mode works | `UNAVAILABLE` |
| JavaScript SDK | 38 runtime exports and all 66 facade methods accounted for; watcher edit and handle replacement exercised | `VERIFIED`, with explicitly untested conditions |
| Languages | 32 declared, 31 accepted by support predicate, 26 returned by loader-oriented list | `PARTIAL` as a support contract |
| Extensions | 58 mapped extensions plus Play, Shopify JSON, and content-sensitive `.h` routing | `VERIFIED` as exposure/routing |
| Framework resolvers | 24 registered; fixture detects none | `UNTESTED` for behavior |
| Terra agent probe | 21/21 evaluated calls succeeded; schemas/canonical output passed; model-authored operation order disagreed with the machine audit | tool behavior `VERIFIED`; strict protocol result `BLOCKED_OR_INVALID` |
| Installer/uninstaller | print paths plus public CLI material install/uninstall covered all 8 global targets and all 5 locally supported targets; Codex, Hermes, and Antigravity correctly rejected local scope; host configuration was untouched | `VERIFIED` in isolated scopes |
| Upgrade/model offload/telemetry transmit | network, credentials, host mutation, or unregistered internal model path | `RESTRICTED` |

CodeGraph is a useful local structural-navigation layer. Its strongest current
uses are exact symbol/file lookup, local call traversal, source retrieval, and
index freshness checks. It should not be treated as a runtime-semantics oracle:
dynamic/cross-language synthesis can over-connect same-name symbols, and impact
is graph traversal rather than semantic patch interpretation.

## Current deterministic measurements

Authoritative artifact measurements come from
`completion-v2/run/authoritative-metrics.json`; all evidence paths in this
report are relative to
`scratchpad/code-intelligence/raw-output/capability-discovery/codegraph/`.
Deterministic CLI, MCP, and SDK operations invoked no model, so their model
token usage is exactly 0. The ledger covers both authoritative roots,
`current/` and `completion-v2/run/`: 552 files, 418,877 bytes, and 115,510
`o200k_base` tokens at generation time. Its `artifacts` map gives bytes/tokens
for every evidence file, `cli_capability_costs` aggregates every captured safe
CLI capability, and `completion_operations` records measured completion runs.

| Run | Wall time | Peak RSS | Output/cost evidence |
| --- | ---: | ---: | --- |
| verbose initial index | 0.39 s | 115,244 KB | `current/cli/init.{out,err,time}` |
| changed-file sync | 0.17 s | 99,948 KB | `current/update/sync.{out,err,time}` |
| default MCP transcript | 2.00 s including a deliberate 2-second stdin hold | 86,400 KB | 19,113 B / 5,059 tokens |
| expanded MCP transcript | 2.00 s including the same hold | 90,584 KB | 27,440 B / 7,308 tokens |
| complete SDK probe | 1.37 s | 269,120 KB | 10,200 B / 2,955 tokens |
| SDK low-level/logger/lock/watcher follow-up | 0.75 s | 86,684 KB | 26,112 B / 6,471 tokens |
| SDK directory/grammar/direct-watcher follow-up | 0.24 s | 185,084 KB | 1,007 B / 266 tokens |
| CLI install, all 8 global targets | 0.09 s | 62,968 KB | 2,037 B / 430 tokens |
| CLI uninstall, all 8 global targets | 0.08 s | 63,488 KB | 931 B / 280 tokens |
| CLI install/uninstall, 5 supported local targets | 0.08 s each | 63,408 / 63,160 KB | 3,180 / 2,276 B; 676 / 568 tokens |
| CLI telemetry on/status, forced offline | 0.06 / 0.05 s | 58,112 / 56,576 KB | 206 / 428 B; 55 / 139 tokens |
| final Terra agent probe | 130.30 s | `UNKNOWN` | 21 tool calls; 128,477 input tokens (97,536 cached), 6,490 output tokens, 1,368 reasoning tokens; 4.977163 credit-equivalent |

The MCP times are transport-capture durations, not query latency; the input was
held open for two seconds so the server could finish asynchronous calls before
EOF. Individual untimed CLI query latency is `UNKNOWN`, not inferred.
For those earlier variants, the authoritative ledger records `UNKNOWN:
captured without /usr/bin/time` rather than inventing elapsed time or RSS.
Output bytes/tokens remain measured for every captured artifact.

## Exposure versus behavior

This report uses two separate questions:

1. **Exposure:** is the command, option, schema, language, extension, resolver,
   or SDK symbol actually registered at the frozen source/runtime?
2. **Behavior:** did the exact operation run against the frozen fixture or a
   controlled temporary project?

Source registration alone never receives a behavioral `VERIFIED`. Absent
language/framework fixtures are `UNTESTED`, even when their parser/resolver is
exposed. A safe variant not exercised receives `UNTESTED`; a meaningful probe
requiring external state receives `RESTRICTED` or `UNAVAILABLE` with a reason.

## CLI: complete public and hidden surface

Root help exposes 20 public commands. Root without a command enters an
interactive installer. `serve` and `prompt-hook` are registered hidden
commands. Recursive help for root, every public command, and both hidden
commands exited 0 in `current/cli/help-*`.

Model tokens are 0 for every executed row. Query time is `UNKNOWN` unless a
timing path is named.

| Surface | Complete options/actions | Behavior, effects, and limitations | Disposition | Evidence / artifact cost |
| --- | --- | --- | --- | --- |
| root | `-V/--version`, `-h/--help`; no-command installer | help/version ran; no-command path would write host agent config | help/version `VERIFIED`; installer `RESTRICTED` | `current/cli/help-root.*`, `version-*` |
| `init [path]` | deprecated `-i/--index`; `-f/--force`; `-v/--verbose` | normal/verbose init indexed by default; deprecated flag is redundant; unsafe-path force bypass not used | `VERIFIED`; force `RESTRICTED` | `current/cli/init.*`; 0.39 s |
| `uninit [path]` | `-f/--force` | removed the configured alternate index and disposable current index while preserving project files | `VERIFIED` | `completion-v2/run/uninit-alt-force.stdout`, `completion-v2/run/uninit-alt-force.stderr`, `completion-v2/run/uninit-alt-force.exit`, `completion-v2/run/alt-dir.before-uninit.state`, `completion-v2/run/alt-dir.after-uninit.state`, `completion-v2/run/uninit-current-force.stdout`, `completion-v2/run/uninit-current-force.stderr`, `completion-v2/run/uninit-current-force.exit`, `completion-v2/run/current.after-uninit.state` |
| `index [path]` | `-f/--force`, `-q/--quiet`, `-v/--verbose` | quiet rebuild and verbose equivalent ran; unsafe-root bypass not used | `VERIFIED`; force `RESTRICTED` | `current/cli/index-quiet.*`, `init.*` |
| `sync [path]` | `-q/--quiet` | clean, quiet, changed, and reversed-change sync ran; writes index only | `VERIFIED` | `current/cli/sync-*`, `current/update/*`; changed sync 0.17 s |
| `status [path]` | `-j/--json` | text, JSON, stale, clean, custom-dir, and uninitialized states covered | `VERIFIED` | `current/cli/status-*`; JSON 822 B/234 tok |
| `query <search>` | `-p/--path`; `-l/--limit=10`; `-k/--kind`; `-j/--json` | search/limit/kind/JSON/missing ran; invalid kind silently returned empty with exit 0 | query `VERIFIED`; validation `PARTIAL` | `current/cli/query-*`; collision 3,534 B/1,076 tok |
| `explore <query...>` | `-p/--path`; `--max-files` | lifecycle/collision/max-files, line-number-off, adaptive-off ran; synthesized one false cross-language edge | `PARTIAL` | `current/cli/explore-*`, `current/config/explore-*`; lifecycle 12,077 B/2,886 tok |
| `node <name>` | `-p/--path`; `-f/--file`; `--offset`; `--limit`; `--symbols-only` | symbol, disambiguated symbol, file, range, symbols-only, and missing modes ran | `VERIFIED` | `current/cli/node-*`; range 986 B/239 tok |
| `files` | `-p/--path`; `--filter`; `--pattern`; `--format` tree/flat/grouped default tree; `--max-depth`; `--no-metadata`; `-j/--json` | every option family ran; invalid format silently fell back instead of failing | behavior `VERIFIED`; validation `PARTIAL` | `current/cli/files-*`; grouped 1,680 B/541 tok |
| `daemon` / `daemons` | interactive daemon picker | empty-list path ran; current live Unix socket attempt returned `EPERM` and proxy fell back to a successful in-process response | manager `VERIFIED`; daemon `UNAVAILABLE` | `current/cli/daemon-list.*`, `current/mcp/daemon-attempt.*`, `current/mcp/daemon.log` |
| `unlock [path]` | no flags | both no-lock and created dead-PID lock removal ran; removes lock file | `VERIFIED` | `current/cli/unlock-{no-lock,stale-lock}.*` |
| `callers <symbol>` | `-p/--path`; `-l/--limit=20`; `-j/--json` | ordinary and collision queries ran; CLI merges same-name definitions | `PARTIAL` | `current/cli/callers-*`; collision 595 B/176 tok |
| `callees <symbol>` | `-p/--path`; `-l/--limit=20`; `-j/--json` | lifecycle call set ran | `VERIFIED` | `current/cli/callees-run.*`; 993 B/289 tok |
| `impact <symbol>` | `-p/--path`; `-d/--depth=2`; `-j/--json` | depth/JSON and ambiguous symbol ran; generic reverse traversal, not patch semantics | `PARTIAL` | `current/cli/impact-*`; WorkResult 2,688 B/788 tok |
| `affected [files...]` | `-p/--path`; `--stdin`; `-d/--depth=5`; `-f/--filter`; `-j/--json`; `-q/--quiet` | positional/stdin quiet output selected both dependent tests in a disposable targeted corpus; unit/e2e filters each selected the expected positive test | `VERIFIED` | `completion-v2/run/affected-positional-quiet.stdout`, `completion-v2/run/affected-stdin-quiet.stdout`, `completion-v2/run/affected-filter-unit.stdout`, `completion-v2/run/affected-filter-e2e.stdout`, `completion-v2/run/exit-summary.tsv` |
| `install` | `-t/--target` list/auto/all/none; `-l/--location` global/local; `-y/--yes`; `--no-permissions`; `--print-config` | print config ran for all 8 targets; public CLI material install created all 8 global configurations and all 5 supported local configurations in disposable scopes; Codex/Hermes/Antigravity correctly skipped local scope; invalid target failed | safe offline behavior `VERIFIED`; host write `RESTRICTED` | `current/cli/install-print-*`, `completion-v2/run/cli-install-{global,local}-all.*`; measured costs above |
| `uninstall` | `-t/--target` list/all; `-l/--location`; `-y/--yes` | the public CLI removed CodeGraph entries for all 8 isolated global targets and all 5 supported local targets, leaving only empty/preserved config containers; the 3 global-only targets reported unsupported locally | safe offline behavior `VERIFIED`; host write `RESTRICTED` | `completion-v2/run/cli-uninstall-{global,local}-all.*` and matching `.files`; measured costs above |
| `telemetry [action]` | `status`, `on`, `off` | status/off and public CLI `on` ran in lane-local state; `on` persisted enabled consent, while `DO_NOT_TRACK=1` made the effective state disabled and prevented transmission | state behavior `VERIFIED`; real transmission `RESTRICTED` | `current/cli/telemetry-*`, `completion-v2/run/cli-telemetry-{on,status-after-on}.*`, `cli-telemetry-after-on.files`; measured costs above |
| `upgrade [version]` | optional version; `--check`; `-f/--force` | check needs release/package network; install mutates package files | `RESTRICTED` | `current/cli/help-upgrade.*`; run/output/model tokens `UNKNOWN` |
| `version` | command; root version aliases | reports 1.0.1 | `VERIFIED` | `current/cli/version-*` |
| hidden `serve` | `-p/--path`; `--mcp`; `--no-watch` | direct stdio initialization/list/calls ran; shared daemon unavailable | direct `VERIFIED`; daemon `UNAVAILABLE` | `current/mcp/*.jsonl` |
| hidden `prompt-hook` | stdin `{prompt,cwd}` | structural injection, nonstructural no-op, and both kill switches ran; no source write | `VERIFIED` | `current/config/prompt-hook-*`; default 6,498 B/1,552 tok |

## Configuration controls

The authoritative machine-readable control inventory is
`completion-v2/control-ledger.tsv`. The tables below summarize that ledger;
the validator derives the expected control set from frozen `src/` plus public
`install.sh`, requires exact set equality, and validates every disposition,
prerequisite, effect, and evidence citation.

### User-facing controls

| Control | Contract | Behavior | Disposition | Evidence / prerequisite |
| --- | --- | --- | --- | --- |
| `CODEGRAPH_DIR` | plain directory name, default `.codegraph`; invalid names fall back | alternate index initialized/statused/uninitialized while canonical index remained; invalid `../invalid` warned and fell back | `VERIFIED` | `current/config/codegraph-dir-*` |
| `CODEGRAPH_MCP_TOOLS` | comma allowlist; explore listed by default | default, all-eight allowlist, dynamic tiny-repo list, and calls ran | `PARTIAL` because exposure lists disagree | `current/mcp/*`, `static-tools.json` |
| `CODEGRAPH_NO_DAEMON` | truthy selects direct MCP | direct mode ran | `VERIFIED` | MCP commands/evidence |
| `CODEGRAPH_NO_WATCH` | `1` disables live watcher | `serve --no-watch` ran | `VERIFIED` | current MCP evidence |
| `CODEGRAPH_FORCE_WATCH` | `1` overrides auto-suppression | not distinguishable without an auto-suppressed platform/filesystem | `UNTESTED` | `src/sync/watch-policy.ts` |
| `CODEGRAPH_WATCH_DEBOUNCE_MS` | integer 100–60,000 ms; default 2,000; invalid ignored | direct MCP parsed and logged the 100 ms env value, started its watcher, and the SDK watcher observed and indexed an edit at 100 ms | `VERIFIED` | `completion-v2/run/mcp-watch-env.stderr`, `completion-v2/run/mcp-watch-env.exit`, `completion-v2/run/sdk-completeness.stdout`, `completion-v2/run/sdk-completeness.exit` |
| `CODEGRAPH_MAX_DIR_WATCHES` | positive integer; default 50,000 | SDK env value 1 produced the cap warning and `watchedDirs: 1`; the watcher remained operational and indexed a root edit | `VERIFIED` for cap enforcement and continued operation | `completion-v2/run/sdk-completeness.stdout`, `completion-v2/run/sdk-completeness.exit` |
| `CODEGRAPH_EXPLORE_LINENUMS` | default on; `0` removes source line prefixes | default and off ran | `VERIFIED` | `current/config/explore-no-linenums.*` 4,610 B/1,037 tok |
| `CODEGRAPH_ADAPTIVE_EXPLORE` | default on; `0`/`false` disables adaptive sizing | default and off ran | `VERIFIED` | `current/config/explore-no-adaptive.*` 4,889 B/1,157 tok |
| `CODEGRAPH_RANK_NO_MULTITERM` | `1` disables multi-term ranking component | default and disabled explore calls both exited 0 but were byte-identical on this corpus | `PARTIAL`; needs a scored multi-term corpus with expected divergent ordering | `completion-v2/run/explore-rank-default.stdout`, `completion-v2/run/explore-rank-no-multiterm.stdout`, `completion-v2/run/exit-summary.tsv` |
| `CODEGRAPH_VALUE_REFS` | default on; `0` disables value-reference edges | a full disabled reindex exited 0 with the same 93 nodes/211 edges; this fixture lacks an asserted value-reference edge whose absence would distinguish the control | `PARTIAL`; disabled runtime accepted, semantic effect not anchored | `completion-v2/run/init-value-refs-disabled.stdout`, `completion-v2/run/status-value-refs-disabled.stdout`, `completion-v2/run/exit-summary.tsv` |
| `CODEGRAPH_RESOLVER_CACHE_SIZE` | positive integer; default 5,000 per cache | a full index and status with cache size 1 exited 0 at 93/211 | `PARTIAL`; needs a resolution working set that proves eviction/overflow behavior | `completion-v2/run/init-resolver-cache-one.stdout`, `completion-v2/run/status-resolver-cache-one.stdout`, `completion-v2/run/exit-summary.tsv` |
| `CODEGRAPH_TELEMETRY` / `DO_NOT_TRACK` | precedence is `DO_NOT_TRACK` > `CODEGRAPH_TELEMETRY` > stored config > default on; `0`/`false` disables and other nonempty values enable | with `DO_NOT_TRACK` absent, `0` recorded/sent nothing and created no state; `1` overrode stored disabled state and reached only the injected fetch sink | `VERIFIED` for both forced directions; real network remains `RESTRICTED` | `completion-v2/run/telemetry-ledger.json`; `src/telemetry/index.ts:186-205`; `__tests__/telemetry.test.ts:60-94` |
| `CODEGRAPH_TELEMETRY_ENDPOINT` | internal send-endpoint override; default `https://telemetry.getcodegraph.com/v1/events` | forced-on lifecycle event selected `http://127.0.0.1:1/inert-enabled`; an injected fetch implementation captured the request and threw before any socket/global fetch could run | safe-sink routing `VERIFIED`; actual network transport `RESTRICTED` | `completion-v2/run/telemetry-ledger.json`; `src/telemetry/index.ts:470-514`; `__tests__/telemetry.test.ts:198-208` |
| `CODEGRAPH_TELEMETRY_DEBUG` | `1` emits telemetry send/failure diagnostics through stderr writer only | safe-sink run captured POST and failure diagnostics; telemetry itself did not write probe stdout | `VERIFIED` for diagnostic emission under injected sink | `completion-v2/run/telemetry-ledger.json`; `src/telemetry/index.ts:503-514,537-541`; stdout-safety test `__tests__/telemetry.test.ts:279-288` |
| `CODEGRAPH_ASCII` / `CODEGRAPH_UNICODE` | terminal glyph selection | both status variants ran | `VERIFIED` | `current/config/status-{ascii,unicode}.*` |
| `CODEGRAPH_DEBUG` | detailed error diagnostics | missing-index error ran with debug set | `VERIFIED` as control exposure | `current/config/debug-error.*`; error exit 1 |
| `CODEGRAPH_NO_PROMPT_HOOK` / `CODEGRAPH_PROMPT_HOOK=0` | disables prompt injection | both produced successful empty output | `VERIFIED` | prompt-hook config evidence |
| `CODEGRAPH_ALLOW_UNSAFE_NODE` | bypasses supported-Node refusal | meaningful behavior bypasses a runtime safety gate | `RESTRICTED` | `src/bin/node-version-check.ts` |
| `CODEGRAPH_NO_RELAUNCH` | disables V8/WASM flag relaunch | requires a runtime needing relaunch to distinguish | `UNTESTED` | `src/extraction/wasm-runtime-flags.ts` |

### Installer path controls

All material checks below ran with `env -i` and lane-local `HOME`,
`HERMES_HOME`, `XDG_CONFIG_HOME`, and `APPDATA`. The guarded probe received
the independent work-copy path, and no host configuration path was read,
written, or deleted.

The public CLI—not only target helper APIs—ran material `install --target all`
and `uninstall --target all` cycles in both scopes. Global scope created and
then removed CodeGraph entries for Claude, Cursor, Codex, opencode, Hermes,
Gemini, Antigravity, and Kiro. Local scope did the same for Claude, Cursor,
opencode, Gemini, and Kiro; Codex, Hermes, and Antigravity explicitly reported
that local configuration is unsupported. Every command exited 0. Post-uninstall
snapshots show only empty or preserved config containers and the later
lane-local telemetry choice. Evidence:
`completion-v2/run/cli-{install,uninstall}-{global,local}-all.*`,
their matching `.files`, and `cli-material-exit-summary.tsv`.

| Control | Default and material scope | Disposition | Evidence |
| --- | --- | --- | --- |
| `CODEGRAPH_BIN_DIR` | standalone `install.sh` defaults to `~/.local/bin`; the override selects the directory where install creates/replaces the `codegraph` symlink and whose `codegraph` entry uninstall removes. It does not relocate the version bundle, which is controlled separately by `CODEGRAPH_INSTALL_DIR`. | runtime `RESTRICTED`: install also downloads/extracts a release and uninstall deletes the selected symlink/bundle; inventory only | `install.sh:14-27,66-93` |
| `HERMES_HOME` | defaults to `~/.hermes`; override is resolved and targets only `$HERMES_HOME/config.yaml`. Detection reads the directory/file; install atomically adds/updates `mcp_servers.codegraph` and `platform_toolsets.cli`; uninstall rewrites that same file to remove those CodeGraph entries without deleting unrelated YAML or the file. Global location only. | `VERIFIED` in isolated home for default/override resolution and material update/removal | `completion-v2/run/installer-env-ledger.json`; `src/installer/targets/hermes.ts:40-112` |
| `XDG_CONFIG_HOME` | opencode global default is `~/.config/opencode`; override is `$XDG_CONFIG_HOME/opencode` on every platform. It reads/selects existing `opencode.jsonc` then `.json`, otherwise creates `.jsonc`; install writes the `mcp.codegraph` entry and marker-fenced `AGENTS.md`; uninstall removes that entry, an emptied `mcp` wrapper, and the marked instructions (deleting `AGENTS.md` only when the helper leaves it empty). | `VERIFIED` in isolated home for default/override resolution and material create/removal | `completion-v2/run/installer-env-ledger.json`; `src/installer/targets/opencode.ts:59-105,137-172,217-253,282-285`; `__tests__/installer-targets.test.ts:1523-1555` |
| `APPDATA` | no current opencode config is created here. When nonempty and different from the resolved XDG directory, detect treats `$APPDATA/opencode` as legacy presence; global install and uninstall sweep only CodeGraph's `mcp.codegraph` entries from legacy `opencode.jsonc`/`.json` and its marker-fenced `AGENTS.md` block, preserving sibling entries/text and files that remain nonempty. | `VERIFIED` for isolated legacy cleanup; host `APPDATA` never accessed | `completion-v2/run/installer-env-ledger.json`; `src/installer/targets/opencode.ts:68-80,137-172,256-274`; `__tests__/installer-targets.test.ts:1557-1605` |

### Daemon, diagnostic, and internal controls

| Control | Contract / prerequisite | Disposition |
| --- | --- | --- |
| `CODEGRAPH_MCP_DEBUG` | diagnostic stderr logging | `VERIFIED` in direct MCP: mode, parsed debounce, active watcher, and watchdog arming were captured in `completion-v2/run/mcp-watch-env.stderr` and `completion-v2/run/mcp-watchdog-enabled-v3.stderr`; both exits are 0 |
| `CODEGRAPH_MCP_LOG_ATTACH` | shared-proxy attach logging | `UNTESTED`; needs an available shared daemon/proxy attach |
| `CODEGRAPH_DAEMON_IDLE_TIMEOUT_MS` | default 300,000 ms | `UNAVAILABLE` with daemon socket denied |
| `CODEGRAPH_DAEMON_MAX_IDLE_MS` | default 1,800,000 ms; 0 disables | `UNAVAILABLE` |
| `CODEGRAPH_DAEMON_CLIENT_SWEEP_MS` | default 30,000 ms; 0 disables | `UNAVAILABLE` |
| `CODEGRAPH_PPID_POLL_MS` | default 5,000 ms | `UNTESTED`; long-lived parent-liveness condition |
| `CODEGRAPH_NO_WATCHDOG`, `CODEGRAPH_WATCHDOG_TIMEOUT_MS` | default timeout 60,000 ms; opt-out suppresses watchdog creation | configuration/arming `VERIFIED`: enabled v3 logged `timeoutMs=1000`, disabled v3 emitted no watchdog line, both initialized and exited 0; actual wedged-main-thread kill remains `UNTESTED` | `completion-v2/run/mcp-watchdog-enabled-v3.stdout`, `completion-v2/run/mcp-watchdog-enabled-v3.stderr`, `completion-v2/run/mcp-watchdog-enabled-v3.exit`, `completion-v2/run/mcp-watchdog-disabled-v3.stdout`, `completion-v2/run/mcp-watchdog-disabled-v3.stderr`, `completion-v2/run/mcp-watchdog-disabled-v3.exit` |
| `CODEGRAPH_DAEMON_INTERNAL`, `CODEGRAPH_HOST_PPID`, `CODEGRAPH_WASM_RELAUNCHED` | detached-child and relaunch plumbing | `NOT_APPLICABLE` as public user capabilities |
| `CODEGRAPH_INSTALL_DIR`, `CODEGRAPH_VERSION` | preserve install location / pin upgrade | `RESTRICTED` with upgrade |
| `CODEGRAPH_LOGIN_URL` | dormant device-login endpoint override | `RESTRICTED`; network and no public login command |
| `CODEGRAPH_OFFLOAD_DISABLE`, `CODEGRAPH_OFFLOAD_URL`, `CODEGRAPH_OFFLOAD_KEY`, `CODEGRAPH_OFFLOAD_MODEL`, `CODEGRAPH_OFFLOAD_EFFORT`, `CODEGRAPH_OFFLOAD_STYLE`, `CODEGRAPH_OFFLOAD_TIMEOUT_MS`, `CODEGRAPH_OFFLOAD_MAXTOKENS`, `CODEGRAPH_OFFLOAD_STRIP`, `CODEGRAPH_OFFLOAD_DEBUG`, `CODEGRAPH_OFFLOAD_USAGE_LOG` | internal reasoning configuration; defaults include 20,000 ms, 12,000 tokens, low/plain | `RESTRICTED` or `NOT_APPLICABLE`: no offload/login CLI or MCP command is registered at this revision |

Installer marker constants such as `CODEGRAPH_SECTION_START` are exported
strings, not environment controls.

The post-fix structured-ledger audit reconciles the exact product-specific
configuration set across `src/` and public `install.sh` after excluding marker
constants. The count is derived from that set, not used as its authority.
Evidence: `completion-v2/control-ledger.tsv`,
`completion-v2/run/config-ledger-source-tokens.txt`, and
`completion-v2/run/config-ledger-audit.json`.

## MCP: exposure, schemas, and behavior

Runtime initialize succeeded with protocol `2024-11-05`, server
`codegraph` 1.0.1, and 4,653-byte/1,049-token instructions. Resources,
resource templates, and prompts are empty.

Exposure differs by layer:

- ordinary runtime `tools/list`: 1 tool, `codegraph_explore`;
- static source/runtime registry with all allowlisted names: 8 definitions,
  8,220 bytes/1,865 tokens;
- direct engine `tools/list` on this 14-file repository with all eight
  allowlisted: 3 tools (`search`, `node`, `explore`), 4,764 bytes/1,094 tokens;
- direct calls: all eight registered handlers executed despite only three
  being dynamically listed.

This is a discoverability inconsistency. Exposure and callability must not be
conflated.

### Complete input schemas

| Tool | Required | Optional/default/enum | Input-schema bytes/tokens | Output / effects / limitation | Behavior disposition |
| --- | --- | --- | ---: | --- | --- |
| `codegraph_search` | `query:string` | `kind` enum function/method/class/interface/type/variable/route/component; `limit:number=10`; `projectPath:string` | 577 / 133 | location/signature text; reads graph | `VERIFIED` |
| `codegraph_callers` | `symbol:string` | `file:string`; `limit:number=20`; `projectPath` | 615 / 143 | inbound callers; file narrows collisions | `VERIFIED` |
| `codegraph_callees` | `symbol:string` | `file:string`; `limit:number=20`; `projectPath` | 570 / 130 | outbound callees/references | `VERIFIED` |
| `codegraph_impact` | `symbol:string` | `file:string`; `depth:number=2`; `projectPath` | 558 / 124 | reverse traversal; not patch-aware | `PARTIAL` |
| `codegraph_node` | none at schema level; operationally symbol or file | `symbol`; `includeCode:boolean=false`; `file`; `offset`; `limit` (whole file, cap 2,000 lines); `symbolsOnly:boolean=false`; `line`; `projectPath` | 1,568 / 361 | symbol trail or current file source; reads disk in source modes | `VERIFIED` |
| `codegraph_explore` | `query:string` | `maxFiles:number=12`; `projectPath` | 716 / 159 | ranked source, paths, synthesized links, blast radius | `PARTIAL` |
| `codegraph_status` | none | `projectPath` | 207 / 45 | counts/backend/kinds/languages | `VERIFIED` |
| `codegraph_files` | none | `path`; `pattern`; `format=tree` enum tree/flat/grouped; `includeMetadata=true`; `maxDepth`; `projectPath` | 901 / 206 | indexed file inventory | `VERIFIED` |

Every tool is source-read-only. Supplying `projectPath` expands read scope to
another initialized project and should be constrained by the caller.
Schema sizes are serialized `inputSchema` measurements from
`completion-v2/run/authoritative-metrics.json`; they exclude tool-name and
description prose. The 8,220-byte/1,865-token figure above measures the complete
static tool definitions instead.

### Current MCP call costs

| Handler/query | Output bytes | `o200k_base` tokens | Query time | Model tokens | Evidence |
| --- | ---: | ---: | --- | ---: | --- |
| search `normalize` | 537 | 137 | `UNKNOWN` | 0 | `current/mcp/expanded.jsonl`, id 10 |
| callers core collision | 352 | 92 | `UNKNOWN` | 0 | id 11 |
| callers gateway collision | 369 | 96 | `UNKNOWN` | 0 | id 12 |
| callees `run` | 449 | 118 | `UNKNOWN` | 0 | id 13 |
| impact `WorkResult` | 545 | 161 | `UNKNOWN` | 0 | id 14 |
| node file range | 639 | 162 | `UNKNOWN` | 0 | id 15 |
| explore lifecycle | 11,730 | 2,809 | `UNKNOWN` | 0 | id 16 |
| status | 451 | 166 | `UNKNOWN` | 0 | id 17 |
| files grouped | 691 | 177 | `UNKNOWN` | 0 | id 18 |
| missing search | 46 | 9 | `UNKNOWN` | 0 | id 19 |
| unknown tool | JSON-RPC `-32602` | separately `UNKNOWN` | `UNKNOWN` | 0 | id 20 |

## Fixture build and structural findings

The 25-file tracked fixture yielded 14 indexed code files:

- 12 TypeScript-family files, including `.d.ts`;
- 2 Rust files.

It skipped documentation, manifests/configuration outside mapped source
extensions, fixture metadata, the synthetic patch, and
`unsupported/legacy.capfixture`. Initial build produced 93 nodes and 211
edges. Runtime kinds were:

- nodes: 9 classes, 4 constants, 1 enum, 1 enum member, 14 files, 5 functions,
  24 imports, 8 interfaces, 17 methods, 5 properties, 1 struct, 1 trait, 3
  type aliases;
- edges: 20 calls, 81 contains, 2 extends, 4 implements, 54 imports, 8
  instantiates, 42 references.

### Lifecycle and collision behavior

`callees run` recovered authorization, resolution, execution, persistence, and
publication calls. `explore` returned current line-numbered source across the
principal lifecycle. It also synthesized:

```text
authorize → authorize [dynamic: interface → impl @rust/policy/src/lib.rs:23]
```

The fixture crosses TypeScript to Rust through a child-process line protocol;
there is no static TypeScript call to that Rust method. This is a false
same-name/interface connection.

Two TypeScript `normalize` definitions were returned separately by search.
MCP callers correctly narrowed them with `file`. CLI callers/impact aggregate
same-name definitions because those commands expose no equivalent
disambiguator.

## Synthetic update behavior

The current 1,206-byte patch changed three TypeScript files by adding an
`attempts` property to interfaces and object literals.

| State | Observed behavior |
| --- | --- |
| before patch | zero pending changes; `attempts` search empty |
| patched, before sync | status reported 3 modified files; graph remained 93/211; `attempts` search empty; file-mode node read showed current source |
| `affected` | the primary fixture has no tests, but a separate exact-identity targeted corpus positively selected both dependent tests and correctly separated unit/e2e filters |
| after sync | three files processed; 0.17 s/99,948 KB; graph remained 93/211; property still not an independently searchable symbol |
| after reversal | quiet sync restored frozen bytes and clean tracked status |

CodeGraph's freshness detection is reliable here, but its graph granularity does
not index every interface/object-literal property occurrence. `impact` is
generic dependency traversal. No public operation accepts a patch and explains
field-level semantic change.

Evidence: `current/update/*`.

## Language and extension contract

Three runtime sets have different meanings:

| Set | Count | Meaning |
| --- | ---: | --- |
| `LANGUAGES` | 32 | full type/discriminator universe, including `unknown` |
| `isLanguageSupported` true set | 31 | 22 WASM grammar languages plus 9 custom/file-level extractors; excludes `unknown` |
| `getSupportedLanguages()` | 26 | 22 WASM languages plus Svelte, Vue, Astro, Liquid; omits Razor, YAML, Twig, XML, Properties even though the support predicate accepts them |

The 26-value function is loader-oriented rather than the complete public
support predicate. Calling it “all supported languages” is therefore
misleading at this revision.

### All declared languages

| Disposition | Languages | Reason |
| --- | --- | --- |
| `VERIFIED` behavior | `typescript`, `rust` | present in frozen fixture and runtime status |
| `PARTIAL` | `unknown` | sentinel routing verified; unknown fixture extension correctly skipped |
| `UNTESTED` behavior | `javascript`, `tsx`, `jsx`, `python`, `go`, `java`, `c`, `cpp`, `csharp`, `razor`, `php`, `ruby`, `swift`, `kotlin`, `dart`, `svelte`, `vue`, `astro`, `liquid`, `pascal`, `scala`, `lua`, `luau`, `objc`, `r`, `yaml`, `twig`, `xml`, `properties` | exposure/routing verified, but no frozen semantic fixture and expected anchors |

All 32 values are accounted for: 2 behavior-`VERIFIED`, 1 `PARTIAL`, 29
behavior-`UNTESTED`.

### All 58 extension mappings

| Language | Extensions |
| --- | --- |
| TypeScript/TSX | `.ts`, `.mts`, `.cts`; `.tsx` |
| JavaScript/JSX | `.js`, `.mjs`, `.cjs`, `.xsjs`, `.xsjslib`; `.jsx` |
| Python/Go/Rust/Java | `.py`, `.pyw`; `.go`; `.rs`; `.java` |
| C/C++/Objective-C | `.c`, `.h`; `.cc`, `.cpp`, `.cxx`, `.hpp`, `.hxx`; `.m`, `.mm` |
| C#/Razor | `.cs`; `.cshtml`, `.razor` |
| PHP/Drupal | `.php`, `.module`, `.install`, `.theme`, `.inc` |
| YAML/Twig/XML/Properties | `.yml`, `.yaml`; `.twig`; `.xml`; `.properties` |
| Ruby/Swift/Kotlin/Dart | `.rb`, `.rake`; `.swift`; `.kt`, `.kts`; `.dart` |
| SFC/template | `.liquid`, `.svelte`, `.vue`, `.astro` |
| R/Pascal/Scala/Lua/Luau | `.r`; `.pas`, `.dpr`, `.dpk`, `.lpr`, `.dfm`, `.fmx`; `.scala`, `.sc`; `.lua`; `.luau` |

Special routes also ran:

- extensionless `conf/routes` and `conf/*.routes` are indexed as YAML-like
  Play inputs;
- `templates/**/*.json` and `sections/**/*.json` route to Liquid, while
  ordinary JSON remains unsupported/unknown;
- `.h` defaults to C, but source heuristics route C++ constructs to `cpp` and
  Objective-C constructs to `objc`;
- YAML, Twig, and Properties are file-level-only; XML can emit MyBatis nodes.

Exposure/routing is `VERIFIED`; semantic extraction for absent languages is
`UNTESTED`. Evidence:
`current/config/language-routing.json` (6,585 B/1,747 tokens).

## Node and edge kind contract

| Contract | Behavior-verified on fixture | Exposed but behavior-untested |
| --- | --- | --- |
| 22 node kinds | `file`, `class`, `struct`, `interface`, `trait`, `function`, `method`, `property`, `constant`, `enum`, `enum_member`, `type_alias`, `import` | `module`, `protocol`, `field`, `variable`, `namespace`, `parameter`, `export`, `route`, `component` |
| 12 edge kinds | `contains`, `calls`, `imports`, `extends`, `implements`, `references`, `instantiates` | `exports`, `type_of`, `returns`, `overrides`, `decorates` |

Property-kind presence does not mean every property syntax becomes a node; the
synthetic update demonstrates that boundary.

## All 24 framework resolvers

Registry exposure is `VERIFIED` by
`current/config/framework-registry.json` (6,446 B/1,603 tokens). The fixture's
`getDetectedFrameworks()` returned `[]`, so behavior of every resolver is
`UNTESTED`.

All resolvers read project files/metadata and add nodes/references/edges to the
index; they do not change source. Detection and resolution are best-effort and
require the named framework dependency/layout/syntax.

| Resolver | Languages | Detection prerequisite and graph effect | Principal limit | Disposition |
| --- | --- | --- | --- | --- |
| Laravel | PHP | Laravel dependency/layout; routes/controllers/model references | conventions and dynamic container binding | `UNTESTED` |
| Drupal | PHP, YAML | Drupal module/composer/YAML layout; routes/hooks/service references | custom modules/conventions | `UNTESTED` |
| Express | JS, TS | Express dependency and route calls; route-to-handler edges | wrapper/alias-heavy routers | `UNTESTED` |
| NestJS | TS, JS | `@nestjs/*` plus decorators/modules; controller/provider/route graph | metadata/dynamic modules | `UNTESTED` |
| React | JS, TS, TSX, JSX | React imports/JSX/hooks; component/render/callback relations | runtime composition/indirection | `UNTESTED` |
| Svelte | Svelte | `.svelte` component syntax; component/event relations | generated/runtime wiring | `UNTESTED` |
| Vue | all-language resolver, practically Vue/JS/TS | Vue files/dependency; component/router relations | no language allowlist; dynamic registration | `UNTESTED` |
| Astro | all-language resolver, practically Astro/JS/TS | Astro files/dependency; component/frontmatter relations | integrations/runtime islands | `UNTESTED` |
| Django | Python | Django layout/imports; URL/view/model/callback relations | settings and dynamic apps | `UNTESTED` |
| Flask | Python | Flask imports/decorators; route-handler graph | blueprints/wrappers | `UNTESTED` |
| FastAPI | Python | FastAPI decorators/dependencies; route/handler/DI graph | dynamic dependency factories | `UNTESTED` |
| Rails | Ruby | Rails/Gemfile/routes layout; controller/model/route references | metaprogramming | `UNTESTED` |
| Spring | Java, Kotlin, YAML, Properties | Spring Maven/Gradle/config/decorators; bean/route/config references | reflection/profiles/runtime injection | `UNTESTED` |
| Play | Scala, Java, YAML-like routes | Play build and `conf/routes`; route-controller references | generated routes/dynamic includes | `UNTESTED` |
| Go | Go | Go module/framework call patterns; package/handler references | interface/runtime registration | `UNTESTED` |
| Rust | Rust | Cargo/project patterns; trait/framework relations | macros/generated code | `UNTESTED` |
| ASP.NET | C# | ASP.NET dependencies/controllers; route/DI/component references | conventions/source generation | `UNTESTED` |
| SwiftUI | Swift | SwiftUI imports/views; state/navigation/component relations | property wrappers/runtime view graph | `UNTESTED` |
| UIKit | Swift | UIKit types/selectors/outlets; target/action relations | storyboard/runtime wiring | `UNTESTED` |
| Vapor | Swift | Vapor package/imports/routes; route-handler references | builder wrappers | `UNTESTED` |
| Swift–ObjC bridge | Swift, ObjC | bridge annotations/names; cross-language references | generated headers/runtime selectors | `UNTESTED` |
| React Native bridge | JS, TS, TSX, JSX, ObjC | bridge/module declarations; JS-native references | codegen/runtime registration | `UNTESTED` |
| Expo Modules | Swift, Kotlin | Expo module DSL; exported function/property relations | generated bridge/runtime DSL | `UNTESTED` |
| Fabric view | TS, TSX, ObjC, Java, Kotlin | Codegen component spec/native view declarations; cross-language edges | generated artifacts/naming conventions | `UNTESTED` |

## JavaScript SDK: complete facade

The CommonJS entry exposed 38 runtime names. The probe explicitly initialized
grammars before direct extraction/per-file indexing, then exercised every
facade family. This corrects the superseded run's false parser concern:
`extractFromSource` emitted TypeScript nodes and `indexFiles` succeeded
(1 file, 2 nodes, 1 edge, 666 ms).

### All 66 `CodeGraph` methods

| Method family | Every method | Behavior and final disposition |
| --- | --- | --- |
| static lifecycle | `init`, `initSync`, `open`, `openSync`, `isInitialized` | all `VERIFIED` on clone or lane-home project |
| handle lifecycle | `reopenIfReplaced`, `close`, `destroy`, `uninitialize`, `getProjectRoot` | true and false replacement cases, close aliases, removal `VERIFIED`; destructive calls only on temporary indexes |
| indexing | `indexAll`, `indexFiles`, `sync`, `isIndexing` | all `VERIFIED`; direct parser calls require grammar initialization |
| watcher | `watch`, `unwatch`, `isWatching`, `isWatcherDegraded`, `getWatcherDegradedReason`, `getPendingFiles`, `waitUntilWatcherReady` | live edit appeared in pending/changed lists; healthy path `VERIFIED`; actual degraded-resource path `UNTESTED` |
| freshness | `getChangedFiles`, `getLastIndexedAt`, `getIndexBuildInfo`, `isIndexStale` | clean and edited states/build stamp `VERIFIED` |
| extraction/resolution | `extractFromSource`, `resolveReferences`, `resolveReferencesBatched`, `getDetectedFrameworks`, `reinitializeResolver` | calls `VERIFIED`; framework-positive behavior `UNTESTED` |
| stats/backend | `getStats`, `getBackend`, `getJournalMode` | 93/211, node-sqlite, WAL `VERIFIED` |
| node/search | `getNode`, `getNodesInFile`, `getNodesByKind`, `getNodesByName`, `searchNodes`, `getProjectNameTokens`, `getTopRouteFile`, `getRoutingManifest` | calls `VERIFIED`; route methods correctly null without routes |
| graph/file | `getOutgoingEdges`, `getIncomingEdges`, `getFile`, `getFiles`, `getContext` | `VERIFIED` |
| traversal | `traverse`, `getCallGraph`, `getTypeHierarchy`, `findUsages`, `getCallers`, `getCallees`, `getImpactRadius`, `findPath`, `getAncestors`, `getChildren` | calls `VERIFIED`; same best-effort semantic limits as CLI/MCP |
| dependency analysis | `getFileDependencies`, `getFileDependents`, `findCircularDependencies`, `findDeadCode`, `getNodeMetrics` | `VERIFIED` as static graph outputs |
| context | `getCode`, `findRelevantContext`, `buildContext` | `VERIFIED`; no model |
| database maintenance | `optimize`, `clear` | `VERIFIED` only on disposable indexes |

The watcher probe copied the fixture into lane home, initialized it, started a
500 ms watcher, edited `normalize.ts`, observed a pending modified file,
restored the bytes, stopped watching, and synchronized. The replacement probe
renamed the temporary index, built a new index at the same path, and verified
`reopenIfReplaced() === true` with 93/211 visible from the healed handle.

### Remaining runtime exports

| Exports | Exposure/behavior |
| --- | --- |
| `CodeGraph`, `default` | presence and facade behavior `VERIFIED` |
| `DatabaseConnection`, `QueryBuilder`, `getDatabasePath` | direct open/path/backend/WAL/schema/stats/search/close behavior `VERIFIED` |
| `getCodeGraphDir`, `isInitialized`, `findNearestCodeGraphRoot`, `CODEGRAPH_DIR` | direct helper behavior `VERIFIED` |
| `detectLanguage`, `isLanguageSupported`, `isGrammarLoaded`, `getSupportedLanguages`, `initGrammars`, `loadGrammarsForLanguages`, `loadAllGrammars` | direct behavior `VERIFIED`; absent-language semantic quality `UNTESTED` |
| error classes `CodeGraphError`, `FileError`, `ParseError`, `DatabaseError`, `SearchError`, `VectorError`, `ConfigError` | direct construction/name/message/code behavior `VERIFIED`; inducing every production failure path remains `UNTESTED` |
| `setLogger`, `getLogger`, `silentLogger`, `defaultLogger` | custom/default/silent replacement and debug-gating behavior `VERIFIED` |
| `Mutex`, `FileLock`, `FileWatcher`, `LockUnavailableError` | direct mutex ordering, lock contention/release, healthy watcher, and error construction `VERIFIED`; actual resource-degraded watcher path `UNTESTED` |
| `processInBatches`, `debounce`, `throttle`, `MemoryMonitor` | direct batch result/progress, debounce-last, throttle queued-call, and memory-threshold behavior `VERIFIED` |
| `MCPServer` | export/direct stdio `VERIFIED`; daemon `UNAVAILABLE` |
| `LANGUAGES`, `NODE_KINDS` | runtime constants `VERIFIED` as exposure; behavior dispositions above |
| TypeScript-only interfaces/types | `NOT_APPLICABLE` as runtime JavaScript callables |

Evidence: `current/sdk/probe.{cjs,output.json,err,time}`,
`completion-v2/run/sdk-completeness.{stdout,stderr,exit,time}`, and
`completion-v2/run/exports-followup.{stdout,stderr,exit,time}`. The measured
follow-ups cost 26,112 B/6,471 tokens/0.75 s/86,684 KB and 1,007 B/266
tokens/0.24 s/185,084 KB respectively; model tokens were 0.

## Side effects, prerequisites, and restricted paths

- Indexing, sync, optimize, resolution, and clear write only CodeGraph database
  state; init/uninit create/remove the configured index directory.
- Source-returning node/explore paths reread source from disk; graph
  relationships can still be stale until sync.
- Watch mode observes source but its only automatic write is the index.
- Install/uninstall can mutate agent configuration and permission lists. Public
  CLI material cycles ran for all 8 global targets and all 5 locally supported
  targets under disposable scopes; no host configuration was targeted.
- Upgrade can contact release/package endpoints and mutate installation files.
- Telemetry transmission can contact a remote endpoint. Public CLI `on`
  persisted consent while `DO_NOT_TRACK=1` kept effective telemetry disabled;
  the separate forced-on routing probe used only an injected fetch sink that
  cannot open a socket. No real network transport ran.
- Internal reasoning/offload source can use remote/BYO endpoints and
  credentials, but no public command exposes it at this revision.
- No public visualization or graph-export command is registered:
  visualization/export is `NOT_APPLICABLE` for this tool surface.

## Current evidence map

Authoritative evidence:

- `current/identity-manifest.json`
- `current/cli/` — recursive help and every safe CLI/config variant
- `current/config/` — routing, framework registry, custom-dir, prompt-hook,
  presentation, debug, adaptive, and line-number controls
- `current/update/` — pre/stale/sync/reversed hashes and outputs
- `current/mcp/` — request JSONL, runtime transcripts, static schemas, timing
- `current/sdk/` — complete facade probe and measurement
- `completion-v2/run/telemetry-ledger.json` — opt-out/forced-on precedence,
  inert endpoint routing, debug capture, and injected-failure requeue
- `completion-v2/run/installer-env-ledger.json` — isolated default/override
  installer paths and material Hermes/opencode cleanup behavior
- `completion-v2/run/cli-{install,uninstall}-{global,local}-all.*` — public CLI
  material cycles for every globally and locally supported target
- `completion-v2/run/cli-telemetry-{on,status-after-on}.*` — public state
  mutation with `DO_NOT_TRACK` effective-off isolation
- `completion-v2/run/{sdk-completeness,exports-followup}.*` — direct remaining
  runtime-export behavior plus elapsed/RSS measurements
- `completion-v2/run/` — guarded debounce/watch-cap, MCP debug/watchdog,
  rank/value-reference/cache, positive affected, and captured uninit evidence
- `completion-v2/run/config-ledger-audit.tsv` — 52-control `src/` plus
  `install.sh` reconciliation and required report/evidence regression anchors
- `completion-v2/run/authoritative-metrics.json` — both authoritative roots,
  per-file and per-CLI-capability bytes/tokens, MCP per-schema costs, measured
  completion time/RSS, and explicit `UNKNOWN` reasons for untimed variants

Current raw evidence is ignored and reproducible; the tracked conclusions live
here. Old top-level `runtime/`, `metrics/`, and Terra session artifacts remain
only as superseded history and must not be mixed into current counts.

## Reproduction

All commands use:

```bash
docs/research/harness-tools/codebase-intelligence/experiments/coding-agents/run-isolated.sh \
  codegraph-current <command> [arguments...]
```

The complete deterministic scripts are:

- `current/run-safe-cli.sh`
- `current/run-update.sh`
- `current/mcp/*-requests.jsonl`
- `current/sdk/probe.cjs`
- `current/config/language-routing-probe.cjs`
- `current/config/framework-registry-probe.cjs`
- `current/metrics/build-metrics.cjs`
- `completion-v2/cli-material-probe.sh`
- `completion-v2/sdk-completeness.cjs`
- `completion-v2/exports-followup.cjs`
- `completion-v2/build-authoritative-metrics.cjs`

No reproduction step requires network or credentials.
