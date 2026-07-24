# CBM capability discovery

Status: **COMPLETE — deterministic discovery; agent-mediated probe not run**

Tool: `codebase-memory-mcp` (CBM)

Frozen source revision: `53ebeb4cf1fca0f4b2384e7ab085e529a2d2750b`

Current frozen fixture revision: `e7ddad2c44321f7b50e60c923b8f0733fb757874`

Discovery date: 2026-07-24

## Executive result

The runtime exposes exactly 14 MCP tools, and all 14 were re-exercised through
the public interface on the repaired, isolated mixed TypeScript/Rust fixture at
`e7ddad2c44321f7b50e60c923b8f0733fb757874`. Eight are `VERIFIED`, five are
`PARTIAL`, and one is `BROKEN` for its advertised
purpose.

CBM is strongest at repository indexing, ranked or structural discovery,
collision-aware snippets, schema inspection, literal source search, and
project lifecycle operations. It also produces a useful first-pass
architecture summary. The important caveats are:

- incremental refresh lost 22 edges (`211 -> 189`) after a three-file patch and
  did not restore them when the patch was reversed; only delete plus fresh
  reindex restored the original graph;
- `detect_changes` found the three modified files and 20 directly contained
  symbols, but returned no transitive blast-radius or risk fields;
- cross-repository intelligence safely scanned a second isolated project but
  produced zero cross edges; this verifies execution, not matching quality;
- automatic startup indexing created a ready 108-node/211-edge index, but a
  retained session with a baseline, a newly exported symbol, and a 15-second
  dirty window did not refresh the graph; the symbol remained absent;
- grouped aggregate Cypher results were collapsed into incorrect totals;
- `trace_path` accepted three modes, but this fixture did not demonstrate
  distinct `data_flow` or `cross_service` semantics;
- `get_architecture` contained internally inconsistent package fan counts and
  suspicious entry-point classifications;
- `ingest_traces` accepts input but explicitly states that runtime edge creation
  is not implemented.

No current-fixture Terra run was performed. The historical
`faa03d6...`/`f9...` attempt is explicitly superseded as
`DISCOVERY_SETUP`: it produced no model completion and made no CBM call, and it
is excluded from every current metric and capability disposition. Provider
usage for a future agent-mediated probe remains `UNKNOWN`.

## Scope, isolation, and evidence precedence

Discovery followed the frozen capability methodology and operations policy in
this directory. Runtime MCP discovery is authoritative over the README, then
source and tests explain runtime behavior. The live external submodule was not
modified or queried as a subject.

The disposable source checkout and fixture remained at their frozen revisions
except for the authorized patch/apply/reverse sequence inside the CBM fixture.
The final verifier and Git status confirm the fixture was restored exactly.
All CBM state was redirected to the dedicated ignored lane under
`scratchpad/code-intelligence/`. An executable `curl` blocker was prepended to
the isolated process path because this environment cannot create a network
namespace; this prevented CBM's initialize-time update check from reaching the
network. This is audited process isolation, not kernel-enforced isolation.

Raw evidence is retained in these ignored locations:

- `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/`
- `scratchpad/code-intelligence/indexes/cbm/`
- `scratchpad/code-intelligence/sessions/capability-discovery/cbm/`
- `scratchpad/code-intelligence/metrics/capability-discovery/cbm/`
- `scratchpad/code-intelligence/runtime/rebuild-cbm/evidence/`

## Final deterministic-completeness audit

The final audit independently re-read the retained runtime `tools/list` result,
the frozen source registry, and the fixture verifier. The runtime list has
exactly 14 object-shaped tool schemas; the 14 names match the registry at
`src/mcp/mcp.c:273-447` exactly, with no runtime-only or source-only negotiated
tool. Every negotiated tool has a representative retained deterministic probe
in the raw-output ledger, and the report separately inventories non-tool MCP
surfaces, CLI modes, config/environment controls, optional UI, languages, and
Hybrid-LSP dispatch.

The first fixture audit observed
`4e18ad2e397aa2f81a24b905a7ac66ede87dbddb` and found that the stored
synthetic patch did not apply cleanly. The shared fixture contract was
subsequently repaired by representing the same source change with
whitespace-clean context, refreshing its hashes, and recreating all three
disposable repositories. `prepare-fixture.sh verify` now passes at
`e7ddad2c44321f7b50e60c923b8f0733fb757874`, with manifest digest
`fc12b07aa2219f346ee1e00f52875efae8c52bbb12dc410456e9457ea1b58e24`.
All fixture-dependent deterministic probes were then rerun against that exact
identity in fresh `cbm-e7dd-*` cache lanes. The run reproduced full,
moderate, and fast indexes; query/path/schema/architecture/search/project/ADR/
trace behavior; the grouped-Cypher defect; and the `211 -> 189` incremental
edge-loss defect. It also corrected one stale result: `detect_changes` now
returns 20 directly contained impacted symbols rather than zero. The final
fixture verifier passes and the fixture worktree is clean. A separate,
two-project isolated lane also indexed two clean `e7ddad2...` fixture clones
at 108 nodes/211 edges each and safely ran cross-repository intelligence
against one target; the operation returned zero cross edges. Three fresh
auto-index lanes created the same ready baseline index at MCP startup. A fourth
retained terminal transcript then waited for the baseline, added a new exported
function, held the tree dirty for 15 seconds (three base polling intervals),
and queried both the symbol and status. The symbol remained absent and the
graph stayed 108/211. The patch was reversed and the fixture was clean. This
demonstrates startup indexing but not working watcher refresh in this build.
Terra was intentionally not rerun.

## Frozen runtime inventory

| Surface | Observed result | Disposition |
|---|---|---|
| Binary | 266,071,720 bytes; dynamically linked to standard C/C++/zlib runtime libraries | `VERIFIED` for this build |
| CLI version | `codebase-memory-mcp 0.9.0+53ebeb4cf1fc` | `VERIFIED` |
| MCP server version | initialize reports `0.10.0` | `PARTIAL`: version surfaces disagree |
| MCP capabilities | `tools` only | `VERIFIED` |
| MCP tools | exactly 14, matching the source registry | `VERIFIED` |
| MCP resources | `resources/list` returns JSON-RPC `-32601 Method not found`; resources are not a negotiated CBM capability | `NOT APPLICABLE` |
| MCP prompts | `prompts/list` returns JSON-RPC `-32601 Method not found`; prompts are not a negotiated CBM capability | `NOT APPLICABLE` |
| Server instructions | absent from initialize; no declared instruction surface | `NOT APPLICABLE` |
| CLI | MCP server default, `cli`, install/uninstall/update/config, UI flags | `VERIFIED` inventory |
| Hidden command | source dispatches `hook-augment`, but public help omits it; internal install component, excluded from public matrix | `NOT APPLICABLE` |
| Languages | README advertises 158 distinct language names. Source has 159 dialect enum members and 159 name entries, but only 158 distinct display names because both CFScript and CFML display as `CFML`. There is no runtime list command. | `PARTIAL`: source inventory reconciled; quality was not tested across all languages |
| Hybrid LSP | README names nine families. TypeScript and Rust per-file analysis ran on the fixture; the production cross-file dispatcher covers eight documented families but omits Rust even though Rust cross-file code and direct tests exist. | `PARTIAL` |

The public README example uses `cli --raw`, while the frozen runtime accepts
`cli --json` (`src/main.c:183,238`). The README also describes a static,
zero-dependency binary; this particular locally rebuilt binary is dynamically
linked. These are documentation/build-profile discrepancies, not proof that
the release artifact has the same linkage.

The canonical MCP tool registry begins at `src/mcp/mcp.c:273`; runtime dispatch
begins at `src/mcp/mcp.c:4215`. Initialize advertises only tools and hard-codes
server version `0.10.0` at `src/mcp/mcp.c:493-528`.

## Evidence key

The detailed tables use:

- **D** — public README: tool list `README.md:380-398`, configuration
  `README.md:430-470`, Hybrid LSP/languages `README.md:487-526`.
- **S** — frozen source: registry `src/mcp/mcp.c:273-447`, dispatch
  `src/mcp/mcp.c:4215-4266`, CLI `src/main.c:183-366`, UI routes
  `src/ui/http_server.c:1231-1303`.
- **R** — non-fixture runtime inventory in the exact artifacts listed in the
  capability-to-artifact ledger.
- **P** — current-fixture runtime probes under the exact
  `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/`
  artifact paths listed below.

There are no declared MCP output schemas. Output shapes below are therefore
observed runtime contracts, not schema guarantees. Schema byte/token counts are
the compact runtime `inputSchema` only.

## Capability-to-artifact ledger

The machine-readable ledger is
`scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/artifact-ledger.tsv`;
the adjacent `artifact-manifest.sha256` covers the ledger and every retained
artifact path referenced by it. All manifest entries are repository-relative.
Verify content digests and exact ledger coverage from the repository root with
`scratchpad/code-intelligence/raw-output/capability-discovery/cbm/artifact-manifest-e7ddad2.sh verify`.
The following paths are exact, repository-relative evidence paths rather than
directory shorthand.

| Public tool | Primary exact retained artifact |
|---|---|
| `index_repository` | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/modes/index-full.json` |
| `search_graph` | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/tools/search-semantic-array.json` |
| `query_graph` | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/tools/query-calls.json` |
| `trace_path` | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/tools/trace-workflow.json` |
| `get_code_snippet` | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/tools/snippet-workflow.json` |
| `get_graph_schema` | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/tools/schema.json` |
| `get_architecture` | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/tools/architecture.json` |
| `search_code` | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/tools/search-code.json` |
| `list_projects` | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/tools/list-projects.json` |
| `delete_project` | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/tools/delete-project.json` |
| `index_status` | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/tools/status.json` |
| `detect_changes` | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/tools/detect-changes.json` |
| `manage_adr` | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/tools/adr-update.json` |
| `ingest_traces` | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/tools/ingest-traces.json` |

Other public-surface claims map as follows:

| Claim family | Exact retained artifacts |
|---|---|
| Fixture/source identity and final cleanliness | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/fixture-verify-final.stdout` |
| MCP initialize, tools, schemas, missing resources/prompts | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/mcp/discovery-output.jsonl` |
| CLI help/version/install/uninstall/update | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/cli/install-plan.stdout` |
| Persistent config | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/config/list-final.stdout` |
| Environment behavior | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/env/workers-999.stderr` |
| Standard-build UI behavior | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/ui/standard-ui.stderr` |
| Custom extension | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/custom-extension/search-custom-extension.json` |
| Schema-valid semantic request | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/tools/search-semantic-array.request.json` |
| Cross-repository public mode | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/cross-repo/cross-repo.json`; `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/cross-repo/list.json` |
| Automatic startup indexing | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/auto-index/session2.jsonl`; `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/auto-index/session3.jsonl` |
| Persistence export and cleanup | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/persistence/index.json` |
| Cross-repository mode | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/cross-repo/cross-repo.json` |
| Ignore and symlink controls | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/ignore/index.json` |
| Extension precedence | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/precedence/index.json` |
| Auto-index/watcher transcript | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/auto-index/session4.typescript` |
| Hidden profiler | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/profile/index-profile.stderr` |
| Per-tool deterministic cost and result classification | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/tool-metrics.json` |

## Tool-by-tool capability matrix

Disposition meanings follow `methodology.md`: `VERIFIED` means the declared
safe behavior worked; `PARTIAL` means only part of the declared behavior was
demonstrated or output was materially misleading; `BROKEN` means the public
operation returned but did not perform its advertised core effect.

| Tool | Purpose; inputs -> observed outputs | Prerequisites and effects | Evidence and fixture result | Pi/Codex study hypothesis; limitation | Disposition |
|---|---|---|---|---|---|
| `index_repository` | Build/update graph. Required `repo_path`; optional `mode`, `target_projects`, `persistence` -> project/status/exclusions/node/edge/artifact fields. | Read repository/Git and write cache. `persistence=true` writes `.codebase-memory/` inside the subject. Cross-repo mode requires existing target indexes. No credential; update check is separately network-capable. | D380; S274; R schema; P full/moderate/fast, persistence, and two-project cross-repo mode. Full 18 files, 108/211. Moderate and fast each 15 files, 96/196. Persistence emitted a 72,757-byte zstd graph artifact and metadata, then cleanup restored a clean tree. Cross-repo mode scanned one target and found zero fixture matches. Incremental patch/reversal produced 189 edges until delete/fresh rebuild. | Setup for every arm; fresh full may expose system structure. Incremental drift can corrupt comparisons. Persistence and cross-repo execution are demonstrated, but persistence should remain off in measured read-only arms and the fixture does not exercise a positive cross-service match. | `PARTIAL` |
| `search_graph` | BM25, regex/QN filters, semantic keywords, degree/relationship filters, connected context, pagination -> `results`, totals, `has_more`, separate `semantic_results`. | Existing index. Read cache only. Moderate/full required for semantic vectors. | D389; S295; R schema; current P includes BM25 and the schema-valid array `semantic_query=["workflow","dispatch","handler"]`. The semantic call returned 20 semantic results across a reported total of 108. | Likely best low-cost concept/symbol discovery for unfamiliar systems. Semantic output was broad, low-scoring, and 12,505 bytes despite `limit=20`; narrow filters and smaller limits are required. | `VERIFIED` |
| `query_graph` | Read-only Cypher subset. Required `query`,`project`; optional `max_rows` -> columns/rows/total or explicit error. | Existing index; reads cache. No write/network/credential. Hard 100k ceiling. | D392; S332; R schema; P calls/inheritance/read rejection/group aggregates. | Useful for explicit system relationship questions after schema discovery. Grouped aggregates collapsed to totals, so aggregates require independent verification. | `PARTIAL` |
| `trace_path` | Required `function_name`,`project`; optional direction/depth/mode/edge types/parameter/test/risk controls -> path nodes, edges and risk context or qualification hints. | Existing index and exact QN for collisions. Reads cache; no network/credential. | D390; S355; R schema; P exact/short-name calls, data-flow and cross-service modes. | Could explain lifecycle and boundary flow. Exact call tracing worked; `data_flow` and `cross_service` did not demonstrate distinct semantics on this fixture. | `PARTIAL` |
| `get_code_snippet` | Required `qualified_name`,`project`; optional neighbors -> source text/location/signature/neighbors or ambiguity suggestions. | Existing index plus source files still present. Reads cache and selected source. | D394; S374; R schema; P four-way `normalize` ambiguity and two exact resolutions. | High-value evidence retrieval after graph discovery; likely reduces broad source reads. Still bounded by indexed symbol accuracy and current working tree. | `VERIFIED` |
| `get_graph_schema` | Required `project` -> actual labels, edge types, counts and property definitions. | Existing index; cache read only. | D393; S383; R schema; P 108/211 graph schema. | Enables valid, compact graph queries before system analysis. `relationship_patterns` was null, so it does not fully teach valid topology. | `VERIFIED` |
| `get_architecture` | Required `project`; optional aspect list -> languages/packages/entry points/routes/hotspots/boundaries/layers/clusters/ADR. | Existing index; reads cache. Potentially large response. | D395; S387; R schema; P all-aspects output. | Fast systems-map hypothesis generator. It misclassified helper normalizers as entry points and contradicted boundaries with zero package fan counts. | `PARTIAL` |
| `search_code` | Required `pattern`,`project`; optional regex/file/path/context/limit/mode -> compact matches, full context, or file inventory with timing/dedup fields. | Existing project registration and readable source. Reads source paths; invalid regex errors. | D396; S396; R schema; P compact/full/files/invalid regex. | Literal fallback and source verification, but not a graph-specific advantage. Output size varies sharply by mode. | `VERIFIED` |
| `list_projects` | No inputs -> projects, roots, node/edge counts and Git metadata. | Reads cache directory only. | D381; S420; R schema; P isolated inventory. | Contamination/isolation check before measured arms; not an understanding tool. | `VERIFIED` |
| `delete_project` | Required `project` -> deleted project/status. | Destructively deletes the selected cache DB; no subject write or network. | D382; S422; R schema; P delete/list/status/fresh restore. | Reliable cleanup for fresh experimental arms. Must be scoped to disposable cache. | `VERIFIED` |
| `index_status` | Required `project` -> readiness, root, nodes/edges and Git identity. | Reads cache/Git metadata. | D383; S426; R schema; P ready and after-delete error. | Required preflight to pin subject identity and graph freshness. It does not prove semantic graph correctness. | `VERIFIED` |
| `detect_changes` | Required `project`; optional base/since/scope/depth -> changed files and impacted symbols. | Reads cache and local Git/diff; may invoke Git. No subject write/network credential. | D391; S430,3886-4014; R schema; current P clean and frozen three-file patch. It returned the exact three files plus 20 directly contained symbols. | Direct containment impact now works, correcting the stale zero-symbol result. No transitive dependent, risk, or blast-radius fields were returned, despite the impact-oriented purpose and `depth=3`. | `PARTIAL` |
| `manage_adr` | Required `project`; `mode` plus optional content/sections -> stored content or section list. | Reads/writes ADR data inside selected cache DB; no subject/network. | D397; S437; R schema; P empty/update/sections/get round-trip. | Could preserve human/system insights across lessons, but would contaminate independent experiment arms unless reset. Schema exposes `get/update/sections`; runtime hint also says undocumented `store`. | `VERIFIED` |
| `ingest_traces` | Required `project`,`traces` -> accepted status/count/note. | Declared graph enhancement would write cache; current handler only counts input. No network/credential. | D398; S443,4200-4203; R schema; P one synthetic trace. | Dynamic evidence could validate cross-service flows, but current runtime explicitly does not create edges. | `BROKEN` |

Summary: **8 VERIFIED, 5 PARTIAL, 1 BROKEN**.

Two callable compatibility aliases are outside the negotiated `tools/list`
surface:

| Alias | Discovery/runtime result | Effects | Disposition |
|---|---|---|---|
| tool name `trace_call_path` | README documents it; source dispatches it to `trace_path`; exact fixture invocation returned the expected 10 callees and two callers | cache read only | `VERIFIED`; compatibility alias, but clients cannot discover it from MCP |
| `manage_adr(mode="store")` | omitted from the input-schema enum, but source treats it as `update`; isolated cache round-trip returned the stored content | cache DB write | `VERIFIED`; compatibility alias, but schema-invalid for strict clients |

### Per-tool schema, timing, output, and token mapping

Each row is one representative deterministic public-interface probe. Wall time
and RSS include process startup. `Schema tok` and `Output tok` are local o200k
estimates; model/provider tokens are **N/A** because no model was used.

| Tool | Input schema bytes / tok | Current representative | Envelope class | Wall s | Peak RSS KiB | Output bytes / tok | Model tokens |
|---|---:|---|---|---:|---:|---:|---|
| `index_repository` | 968 / 215 | `modes/index-full.json` | success | 0.09 | 35,440 | 538 / 125 | N/A deterministic |
| `search_graph` | 1,622 / 363 | `tools/search-semantic-array.json` | success | 0.00 | 11,584 | 12,505 / 3,007 | N/A deterministic |
| `query_graph` | 320 / 73 | `tools/query-calls.json` | success | 0.00 | 11,976 | 6,547 / 1,600 | N/A deterministic |
| `trace_path` | 1,032 / 243 | `tools/trace-workflow.json` | success | 0.00 | 11,636 | 2,744 / 653 | N/A deterministic |
| `get_code_snippet` | 268 / 56 | `tools/snippet-workflow.json` | success | 0.00 | 11,592 | 2,996 / 929 | N/A deterministic |
| `get_graph_schema` | 83 / 19 | `tools/schema.json` | success | 0.00 | 11,628 | 5,056 / 1,158 | N/A deterministic |
| `get_architecture` | 136 / 33 | `tools/architecture.json` | success | 0.00 | 11,580 | 7,631 / 1,914 | N/A deterministic |
| `search_code` | 942 / 222 | `tools/search-code.json` | success | 0.00 | 12,032 | 2,519 / 621 | N/A deterministic |
| `list_projects` | 33 / 9 | `tools/list-projects.json` | success | 0.01 | 11,776 | 821 / 244 | N/A deterministic |
| `delete_project` | 83 / 19 | `tools/delete-project.json` | success | 0.00 | 10,752 | 165 / 43 | N/A deterministic |
| `index_status` | 83 / 19 | `tools/status.json` | success | 0.01 | 12,032 | 805 / 235 | N/A deterministic |
| `detect_changes` | 305 / 88 | `tools/detect-changes.json` | success | 0.00 | 11,520 | 2,087 / 451 | N/A deterministic |
| `manage_adr` | 225 / 54 | `tools/adr-update.json` | success | 0.01 | 11,776 | 64 / 18 | N/A deterministic |
| `ingest_traces` | 144 / 36 | `tools/ingest-traces.json` | success | 0.00 | 10,496 | 154 / 35 | N/A deterministic |

Machine-readable mapping:
`scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/tool-metrics.json`.
The generator checked that these 14 names exactly match current
`tools/list`. It classified all 14 representatives as successful envelopes
and separately classified three expected error envelopes—write Cypher, invalid
regex, and status-after-delete—as `intentional_failure`. Their combined
current-fixture totals are 45,055 bytes and 11,136 local o200k tokens. Tool
disposition is kept separate from envelope class: `ingest_traces`, for example,
returns success but remains `BROKEN` for its advertised core effect.

## Fixture index modes and graph coverage

`full`, `moderate`, and `fast` were each run from a clean, byte-identical Git
fixture at the frozen commit, in a dedicated cache and runtime lane. The
existing full lane was not reused for the new mode probes. All three fixture
trees were clean after indexing; all writes stayed in their lane caches.

| Mode | Files | Nodes / edges | Internal pipeline ms | Wall s | Peak RSS KiB | Cache bytes | Result bytes / local tok | Observed limitation |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `full` | 18 | 108 / 211 | 76 | 0.09 | 35,440 | 1,900,544 | 538 / 125 | Includes documentation and builds similarity/semantic data; zero similarity/semantic edges on this small fixture. |
| `moderate` | 15 | 96 / 196 | 69 | 0.08 | 35,020 | 1,900,544 | 546 / 127 | Excluded `docs` and `.git`; similarity and semantic passes ran but added zero edges. |
| `fast` | 15 | 96 / 196 | 26 | 0.04 | 24,316 | 1,769,472 | 546 / 127 | Excluded `docs` and `.git`; skipped similarity/semantic passes. |

The runtime result does not expose indexed file count or elapsed time. File
count and internal time therefore come from deterministic pipeline logs; wall
time/RSS come from `/usr/bin/time`. Both filtered modes logged
`pipeline.route path=full` despite their distinct behavior, so that log field
must not be interpreted as the requested mode. On this fixture moderate and
fast produced identical node/edge counts; moderate's only observable benefit
was the additional semantic/vector work and larger DB.

All three new mode lanes contain only their project DB. Full and moderate are
both 1,900,544 bytes at this scale; fast is 1,769,472 bytes.

The fresh rebuild after the incremental-drift experiment took 0.08 seconds,
peaked at 35,468 KiB, and reproduced 108 nodes/211 edges.

Node counts were:

`File 18`, `Module 18`, `Method 17`, `Class 13`, `Folder 9`,
`Interface 9`, `Variable 7`, `Function 6`, `Type 3`, `Section 2`, and one
each of `Branch`, `Decorator`, `Enum`, `EnvVar`, `Field`, and `Project`.

Relationship counts were:

`DEFINES 77`, `USAGE 39`, `CALLS 25`, `IMPORTS 21`,
`CONTAINS_FILE 18`, `DEFINES_METHOD 17`, `CONTAINS_FOLDER 5`,
`IMPLEMENTS 4`, `INHERITS 2`, and one each of `CONFIGURES`, `DECORATES`,
and `HAS_BRANCH`.

### Documentation, source, and runtime graph reconciliation

The README's “Graph Data Model” is not a complete runtime schema. The source
can emit labels omitted there, while the current fixture naturally observes
only the constructs it contains. “Source” below means a production node
creation/extraction path, not merely a string in a test or comment.

| Node label | README data model | Production source | Current fixture count |
|---|---|---|---:|
| `Project` | yes | yes | 1 |
| `Package` | yes | yes | 0 |
| `Folder` | yes | yes | 9 |
| `File` | yes | yes | 18 |
| `Module` | yes | yes | 18 |
| `Class` | yes | yes | 13 |
| `Function` | yes | yes | 6 |
| `Method` | yes | yes | 17 |
| `Interface` | yes | yes | 9 |
| `Enum` | yes | yes | 1 |
| `Type` | yes | yes | 3 |
| `Route` | yes | yes | 0 |
| `Resource` | yes | yes | 0 |
| `Channel` | no | yes | 0 |
| `Chart` | no | yes | 0 |
| `Variable` | no | yes | 7 |
| `Section` | no | yes | 2 |
| `Branch` | no | yes | 1 |
| `Decorator` | no | yes | 1 |
| `EnvVar` | no | yes | 1 |
| `Field` | no | yes | 1 |
| `Struct` | no | yes | 0 |
| `Macro` | no | yes | 0 |

The edge table uses the same rule: “source” requires a production insertion
path. README “yes” includes the selected-edge/features sections in addition to
the formal data-model list. The runtime count comes from current
`get_graph_schema`, so zero means not observed on this fixture, not unsupported.

| Edge type | README | Production source | Fixture count |
|---|---|---|---:|
| `CONTAINS_PACKAGE` | yes | no production insertion found | 0 |
| `CONTAINS_FOLDER` | yes | yes | 5 |
| `CONTAINS_FILE` | yes | yes | 18 |
| `DEFINES` | yes | yes | 77 |
| `DEFINES_METHOD` | yes | yes | 17 |
| `IMPORTS` | yes | yes | 21 |
| `CALLS` | yes | yes | 25 |
| `HTTP_CALLS` | yes | yes | 0 |
| `ASYNC_CALLS` | yes | yes | 0 |
| `IMPLEMENTS` | yes | yes | 4 |
| `INHERITS` | yes | yes | 2 |
| `OVERRIDE` | no | yes | 0 |
| `HANDLES` | yes | yes | 0 |
| `USAGE` | yes | yes | 39 |
| `CONFIGURES` | yes | yes | 1 |
| `WRITES` | yes | yes | 0 |
| `MEMBER_OF` | yes | no production insertion found | 0 |
| `TESTS` | yes | yes | 0 |
| `USES_TYPE` | yes | no production insertion found | 0 |
| `FILE_CHANGES_WITH` | yes | yes | 0 |
| `EMITS` | yes | yes | 0 |
| `LISTENS_ON` | yes | yes | 0 |
| `DATA_FLOWS` | yes | yes | 0 |
| `SIMILAR_TO` | yes | yes | 0 |
| `SEMANTICALLY_RELATED` | yes | yes | 0 |
| `READS` | no | yes | 0 |
| `DECORATES` | no | yes | 1 |
| `HAS_BRANCH` | no | yes | 1 |
| `TESTS_FILE` | no | yes | 0 |
| `THROWS` | no | yes | 0 |
| `RAISES` | no | yes | 0 |
| `DEPENDS_ON` | no | yes | 0 |
| `INFRA_MAPS` | no | yes | 0 |
| `GRPC_CALLS` | no | yes | 0 |
| `GRAPHQL_CALLS` | no | yes | 0 |
| `TRPC_CALLS` | no | yes | 0 |
| `CROSS_HTTP_CALLS` | generic `CROSS_*` claim | yes | 0 |
| `CROSS_ASYNC_CALLS` | generic `CROSS_*` claim | yes | 0 |
| `CROSS_CHANNEL` | generic `CROSS_*` claim | yes | 0 |
| `CROSS_GRPC_CALLS` | generic `CROSS_*` claim | yes | 0 |
| `CROSS_GRAPHQL_CALLS` | generic `CROSS_*` claim | yes | 0 |
| `CROSS_TRPC_CALLS` | generic `CROSS_*` claim | yes | 0 |

The source evidence for the previously omitted rows is explicit:
`src/pipeline/pass_definitions.c:353` creates `Channel` nodes,
`src/pipeline/pass_k8s.c:444,462` creates `Chart` nodes, and
`src/pipeline/pass_semantic.c:288` inserts `OVERRIDE` edges. The current
`e7ddad2/tools/schema.json` `get_graph_schema` artifact observes none of the
three on this fixture, hence their zero runtime counts.

This exposes three documentation drifts: the formal node table omits ten
production labels; the formal edge table advertises three names for which no
production insertion path was found; and it omits many implemented enrichment,
infrastructure, exception, and cross-repository edges.

### File-discovery and precedence controls

| Control | README claim | Source behavior | Current fixture observation |
|---|---|---|---|
| hardcoded directories and suffixes | `.git`, `node_modules`, etc. precede ignore files | more than 60 always-skip directories, binary/generated suffix filters, plus mode-specific filters | `node_modules/hardcoded.ts` was not indexed |
| root and nested `.gitignore` | hierarchical gitignore syntax | root file plus nested files, with paths made relative to each nested ignore | root-ignored probe was not indexed; nested negation was not separately exercised |
| root `.cbmignore` / explicit ignore file | project-specific gitignore syntax after `.gitignore` | root `.cbmignore`, or `ignore_file` when supplied internally | `.cbmignore` probe was not indexed |
| symlinks | always skipped | `lstat`/reparse-point checks prevent following file and directory symlinks | symlink path was absent; its regular target was indexed once |
| full/moderate/fast filtering | fast/moderate exclude docs and generated/noise paths | fast/moderate directory, filename, substring, and suffix filters | full indexed 18 files; moderate/fast indexed 15 and omitted docs |
| language detection | supported languages only | unknown language returns no accepted file; selected JSON config files are separately filtered | `legacy.capfixture` was absent from graph and source search |
| project extensions | `.codebase-memory.json` | project mapping overrides the same global extension key | conflicting `.precedenceprobe` parsed as TypeScript and exposed a Function |
| global extensions | XDG config JSON | global mapping applies before project override | global-only `.globalprobe` parsed as TypeScript and exposed a Function |
| maximum file size | not exposed in MCP schema | discovery supports a limit, but the production index path sets `0` (no limit) | not independently exercised |
| malformed/oversized extension config | not detailed | invalid entries fail open with warnings; config above 64 KiB is ignored | source-inspected only |

The index log recorded 80 definitions, 61 calls, 31 imports, 28 resolved calls,
33 unresolved calls, five inheritance relationships, one decoration, and one
implementation relationship. The deliberately unsupported
`unsupported/legacy.capfixture` file was absent from both graph and source
search results. This is correct exclusion behavior, but it also demonstrates
that "158 languages" is not equivalent to arbitrary file coverage.

Architecture output counted TypeScript 12, Rust 2, and TOML 1. It identified
`core`, `policy`, and `gateway` packages and three dependency boundaries. It did
not present the unsupported file as parsed code.

## Incremental correctness concern

The synthetic-change sequence was:

1. Confirm a clean fixture and 108/211 fresh graph.
2. Apply the frozen patch to `contracts.ts`, `handlers.ts`, and `workflow.ts`.
3. Confirm `detect_changes` reports exactly those three paths and 20 symbols
   contained directly in those files, but no transitive blast-radius/risk data.
4. Re-run default indexing: 108/189.
5. Reverse the patch and confirm the fixture is clean.
6. Re-run default indexing: still 108/189.
7. Delete the isolated project and run a fresh full index: 108/211.

This is a reproducible correctness concern, not merely a performance variance.
The final graph was restored by the supported delete/reindex path and the
fixture was returned to its exact clean revision.

## CLI and operational surface

The runtime help, source flag parsers, public README, and safe dry runs were
reconciled. The binary's help names nine agents. The README names eleven,
adding VS Code and OpenClaw. The frozen source detects twelve, adding
undocumented Cursor. Thus help, README, and implementation are three distinct
inventories: 9, 11, and 12.

| Surface / flags | Purpose and output | Effects / prerequisites | Runtime result and limitation | Disposition |
|---|---|---|---|---|
| no subcommand | MCP JSON-RPC server on stdio | Reads/writes selected cache; may watch indexed repositories; initialize-time update check can use network | Initialize/tools worked offline with update `curl` blocked. | `VERIFIED` |
| `--help`, `-h`, `--version` | Help/version text | Read-only | Commands work, but CLI version is `0.9.0+SHA`, MCP version says `0.10.0`, and help lists only 9 of 12 implemented profiles. | `PARTIAL` |
| `cli [--progress] [--json] TOOL [JSON]` | One public MCP call; progress to stderr; envelope JSON with `--json` | Tool-dependent | Both flags are in source usage. README's `--raw` example is stale and unsupported. | `VERIFIED` |
| `install [-y\|--yes\|-n\|--no] [--force] [--dry-run] [--plan]` | Detect/configure 12 agents, hooks, instructions and skills | Real run writes user/agent config; may inspect PATH/home. No network required for an already-installed binary. | All 12 profiles were separately detected through `--plan` and `-n --dry-run`, with empty before/after file diffs. Real config application was not run. | `PARTIAL` |
| `uninstall [-y\|--yes\|-n\|--no] [--dry-run]` | Remove CBM entries/hooks/instructions, not binary or graph DBs | Real run mutates multiple agent configs | Dry run stayed isolated but counted `_config.db` as a project index. Real removal was not run. | `PARTIAL` |
| `update [-y\|--yes\|-n\|--no] [--dry-run] [--standard\|--ui] [--force]` | Select release variant, delete incompatible indexes, download/check/replace binary | Real run is networked and destructive to indexes/binary; checksum verification required | Standard dry run printed URL/target only. `CBM_DOWNLOAD_URL` override changed URL without network. Help omits variant/force/dry-run detail; real update was not run. | `PARTIAL` |
| `config list\|get\|set\|reset` | Persistent key/value settings in `_config.db` | Writes only lane cache for set/reset | Round-trip worked, but any arbitrary key/value is accepted even though list displays only two supported keys. | `PARTIAL` |
| `--ui=true\|false`, `--port=N` | Persist visualization enablement/port, then start UI with MCP server | Writes `config.json`; a UI build opens loopback listener | Standard binary persisted flags but cannot start UI. Invalid non-`true` values silently mean false; ports outside 1-65534 are ignored. | `PARTIAL` |
| `--profile` / `CBM_PROFILE` | Enable internal timing profiler | Adds phase timing to stderr and small measurement overhead | Hidden `--profile` was run on a fresh fast index and emitted 21 `msg=prof` phase/dump/write records, including `pipeline TOTAL`; the 96/196 result matched an unprofiled fast index. The flag and environment variable share the same active gate, although only the flag was varied at runtime. | `VERIFIED` for the hidden flag; environment spelling source-confirmed |
| `hook-augment` | Claude PreToolUse graph-context shim | Reads stdin/cache and emits hook JSON | Dispatched by source but omitted from public help; installed indirectly; not separately runtime-probed. | `UNTESTED` |
| distribution `install.sh --ui\|--standard --dir[=]PATH --skip-config` | Download/install selected release asset | Network, binary write, optional config mutation | Source/docs inventory only; not safe offline and separate from installed binary command. | `RESTRICTED` |

### Integration profiles

Each profile was detected in its own isolated `HOME`/config/cache tree. Both
`install --plan` and `install -n --dry-run` exited zero; every plan reports
`writes_started=false` and `network_after_install=false`; every before/after
file diff is empty. The disposition below applies to the dry-run/plan surface.
Real installation remains restricted because it would mutate user configuration.

| Profile | Planned target/effect | Detection caveat | Exact plan artifact | Dry-run disposition |
|---|---|---|---|---|
| Claude Code | `.claude/.mcp.json`, `.claude.json`, `settings.json`, skills, PreToolUse and SessionStart hook scripts | Help/README/source agree | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/profiles/claude-code/install-plan.json` | `VERIFIED` |
| Codex CLI | `.codex/config.toml`, `.codex/AGENTS.md`, SessionStart entry in config | Help/README/source agree | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/profiles/codex/install-plan.json` | `VERIFIED` |
| Gemini CLI | `.gemini/settings.json`, `.gemini/GEMINI.md`, BeforeTool and SessionStart entries | Help/README/source agree | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/profiles/gemini/install-plan.json` | `VERIFIED` |
| Zed | `.config/zed/settings.json` MCP entry | Help/README/source agree | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/profiles/zed/install-plan.json` | `VERIFIED` |
| OpenCode | `.config/opencode/opencode.json`, `.config/opencode/AGENTS.md` | Detected from executable on isolated PATH | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/profiles/opencode/install-plan.json` | `VERIFIED` |
| Antigravity | shared `.gemini/config/mcp_config.json`, `antigravity-cli/AGENTS.md`, SessionStart settings | Its directory necessarily also detects Gemini, so the plan includes both profiles | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/profiles/antigravity/install-plan.json` | `VERIFIED` |
| Aider | `CONVENTIONS.md`; no MCP target | Detected from executable on isolated PATH | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/profiles/aider/install-plan.json` | `VERIFIED` |
| KiloCode | `mcp_settings.json`, `.kilocode/rules/codebase-memory-mcp.md` | Its detection directory necessarily also detects VS Code, so the plan includes both profiles | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/profiles/kilocode/install-plan.json` | `VERIFIED` |
| VS Code | `.config/Code/User/mcp.json` using the VS Code `servers`/stdio shape | Omitted from help, present in README/source | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/profiles/vscode/install-plan.json` | `VERIFIED` |
| Cursor | `.cursor/mcp.json` | Present in source only; omitted from both help and README | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/profiles/cursor/install-plan.json` | `VERIFIED` |
| OpenClaw | `.openclaw/openclaw.json` | Omitted from help, present in README/source | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/profiles/openclaw/install-plan.json` | `VERIFIED` |
| Kiro | `.kiro/settings/mcp.json` | Help/README/source agree | `scratchpad/code-intelligence/raw-output/capability-discovery/cbm/e7ddad2/profiles/kiro/install-plan.json` | `VERIFIED` |

Representative non-MCP metrics (stdout plus stderr tokens, local o200k; no
model/provider tokens):

| Surface | Wall s | Peak RSS KiB | Stdout / stderr bytes | Local output tok | Model tokens |
|---|---:|---:|---:|---:|---|
| help | 0.00 | 8,448 | 999 / 0 | 282 | N/A deterministic |
| version | 0.00 | 8,448 | 39 / 0 | 20 | N/A deterministic |
| install plan | 0.00 | 8,704 | 1,269 / 0 | 324 | N/A deterministic |
| install dry run | 0.00 | 8,704 | 942 / 0 | 258 | N/A deterministic |
| uninstall dry run | 0.00 | 8,704 | 190 / 0 | 45 | N/A deterministic |
| update dry run | 0.00 | 8,704 | 510 / 0 | 135 | N/A deterministic |
| config list | 0.08 | 17,336 | 97 / 0 | 19 | N/A deterministic |
| standard binary UI startup | 0.50 | 11,008 | 0 / 282 | 76 | N/A deterministic |

Machine-readable mapping:
`scratchpad/code-intelligence/metrics/capability-discovery/cbm/surface-probe-metrics.json`.
Restricted real install/update/UI-build operations have `UNKNOWN` runtime,
output, resource, and model-token metrics because they were not executed.

Repository persistence was exercised only in a disposable clean clone. With
`persistence=true`, full indexing produced 108 nodes/211 edges and wrote
`.codebase-memory/graph.db.zst` (72,757 bytes),
`.codebase-memory/artifact.json` (356 bytes), and
`.codebase-memory/.gitattributes` (120 bytes). The artifact records the exact
`e7ddad2...` commit, 1,310,720 uncompressed bytes, zstd level 9, and the graph
counts. All three generated files were then removed; the clone returned clean.
Cross-repository intelligence was run safely in a separate isolated lane with
two clean clones of the frozen fixture. Both indexes reported 108 nodes and 211
edges at `e7ddad2...`; `list_projects` confirmed exactly those two projects.
The primary then scanned the secondary and returned success with
`projects_scanned=1` and all six cross-edge counters at zero. This is the
observed result, not evidence that CBM can form correct cross-repository edges:
the identical fixture clones do not provide a controlled caller/callee pair.

## Persistent configuration and custom extensions

| Config surface | Default / accepted input | Effect and storage | Offline probe | Limitation / disposition |
|---|---|---|---|---|
| `auto_index` | `false`; bool parser recognizes `true/1/on` and `false/0/off` | `_config.db`; enables session-start indexing/watcher registration | Fresh MCP startup created a ready 108/211 project DB. In a retained fourth session, after startup and watcher baseline time, a new exported `watcherCapabilityProbe` remained absent after a 15-second dirty window and status stayed 108/211; cleanup restored the fixture. | `PARTIAL`; startup indexing is `VERIFIED`, CLI values are not validated, and automatic watcher refresh failed this controlled runtime probe |
| `auto_index_limit` | `50000`; integer consumer | `_config.db`; caps automatic indexing by file count | Storage round-trip set `123`/reset to `50000`; all three startup lanes separately set `1000` and indexed this 18-file fixture. | `PARTIAL`; configured startup below the limit worked, but CLI accepts arbitrary strings/ranges and no boundary or over-limit behavior was tested. |
| arbitrary keys | no documented default | `_config.db` | `arbitrary_key=arbitrary_value` stored/read/reset successfully | `VERIFIED`; hidden from `config list` and unconstrained |
| UI `ui_enabled`,`ui_port` | false/9749 for standard build; UI build auto-enables if config absent | separate cache `config.json` written by `--ui=`/`--port=` | persisted `true`/19749 exactly | `PARTIAL`; storage works, but the standard build cannot use the enabled UI |
| project `extra_extensions` | JSON map in `.codebase-memory.json` | Changes discovery for that repository; reads subject config, no external network | `.cbmprobe -> typescript` indexed `customExtensionProbe` as a Function and source search found it | `VERIFIED`; project overrides global |
| global `extra_extensions` | JSON map in `$XDG_CONFIG_HOME/codebase-memory-mcp/config.json` | Applies to all subjects in that environment; project mapping wins on a key conflict | A global-only `.globalprobe -> typescript` file indexed as a Function. A conflicting global `.precedenceprobe -> rust` plus project `.precedenceprobe -> typescript` also indexed the TypeScript function. | `VERIFIED`; global mapping and project-over-global precedence both demonstrated |

Custom extension values are case-insensitive language aliases, but the mapping
table contains 73 aliases for only 64 language enums, not every advertised
language. Unknown languages, malformed entries, missing files, and corrupt JSON
are skipped with warnings/fail-open behavior. Configuration files larger than
64 KiB are ignored. A custom extension changes parsing, so experiment arms must
freeze both project and global config bytes.

## Environment variables

The first five are documented public configuration. The remaining five are
source-visible tuning/debug switches omitted from public docs; they are
inventoried so they cannot silently contaminate an experiment.

| Variable | Default / accepted input | Effect and risk | Runtime/source result | Disposition |
|---|---|---|---|---|
| `CBM_CACHE_DIR` | home cache path; any path | Redirects all DB/config state; write effect | Every lane wrote only its dedicated cache | `VERIFIED`, required isolation control |
| `CBM_DIAGNOSTICS` | false; `1` or `true` | Periodic process JSON in temp directory; local write every 5s, removed on clean stop | Start message observed and file cleaned on exit | `VERIFIED` |
| `CBM_DOWNLOAD_URL` | GitHub releases | Changes real update/check download destination; network/remote trust risk | Dry-run override produced the exact custom base URL, no download; real network use was restricted | `PARTIAL` |
| `CBM_LOG_LEVEL` | `info`; debug/info/warn/error/none or 0-4 | Stderr verbosity and artifact/token noise | debug server startup emitted 59 bytes; none emitted 0 | `VERIFIED` |
| `CBM_WORKERS` | detected; integer 1-256 | Parallelism, memory/time and potentially nondeterministic ordering | `1` accepted; `999` warned and fell back to detection | `VERIFIED` |
| `CBM_PROFILE` | off; any nonempty/nonzero | Internal profiling overhead/output | Source parser shares the same gate as hidden `--profile`; the runtime flag emitted 21 phase timing records on a fresh fast index | `PARTIAL`; profiler behavior verified through the flag, environment spelling source-confirmed but not separately varied |
| `CBM_DISABLE_LSP_CROSS` | unset; any presence disables | Removes cross-file LSP resolution, materially changing graph | Source `pipeline.c:677-690`; deliberately not set in probes | `UNTESTED` |
| `CBM_SEMANTIC_THRESHOLD` | compiled threshold; numeric `(0,1]` | Changes semantic-edge selection | Source parser found; not documented or varied | `UNTESTED` |
| `CBM_SEMANTIC_ENABLED` | disabled unless first char is `1` | Function exists but has no production caller at this revision | Source-only dead/unwired switch | `NOT APPLICABLE` |
| `CBM_SQLITE_MMAP_SIZE` | 67,108,864 bytes; negative -> 0 | Changes SQLite memory mapping and resource profile | Source and tests reconcile; not varied | `UNTESTED` |

Standard platform variables (`HOME`, `XDG_CONFIG_HOME`, `PATH`, `TMPDIR`,
`CLAUDE_CONFIG_DIR`) also affect path detection/install integration but are not
CBM-specific feature flags. The isolated runner pins them and strips inherited
credentials.

## Graph visualization UI

The supplied 266 MB binary is the standard build and contains zero embedded UI
assets. A bounded offline startup with `--ui=true --port=19749`, stdin at EOF,
exited 0, persisted the requested config, and printed:

> `--ui requested, but this binary was built without the embedded UI, so the HTTP server will not start.`

Therefore no loopback socket or visualization response was available to probe.
Building the UI variant would run `npm ci` and requires unavailable/unapproved
package retrieval, so it was not attempted. Source shows that the optional
server binds IPv4 `127.0.0.1` only and accepts localhost CORS origins. It exposes
the following public local routes without a separately visible authentication
layer:

| UI route | Purpose / output | Effects | Runtime disposition |
|---|---|---|---|
| `GET /`, `/assets/*` | Embedded 3D frontend/static assets | read embedded bytes | `UNAVAILABLE`; standard build contains no UI assets |
| `POST /rpc` | JSON-RPC bridge to the same 14 MCP tools | tool-dependent read/write/delete | `UNAVAILABLE`; route exists in source but the standard build cannot start the UI server |
| `GET /api/layout` | 3D graph layout | read project DB; potentially large output | `UNAVAILABLE`; source-only in this build |
| `POST /api/index` | Start background repository indexing | reads chosen path; writes DB; process/thread work | `UNAVAILABLE`; source-only in this build |
| `GET /api/index-status` | All UI index jobs | read process state | `UNAVAILABLE`; source-only in this build |
| `DELETE /api/project` | Delete selected graph DB | destructive cache delete | `UNAVAILABLE`; source-only in this build |
| `GET /api/browse` | Directory picker | reads local filesystem directory names | `UNAVAILABLE`; source-only and privacy-sensitive |
| `GET /api/adr`, `POST /api/adr` | Read/write ADR | cache DB read/write | `UNAVAILABLE`; source-only in this build |
| `GET /api/project-health` | SQLite integrity/health | reads project DB | `UNAVAILABLE`; source-only in this build |
| `GET /api/processes` | Enumerate CBM processes via `ps` | reads process metadata | `UNAVAILABLE`; source-only in this build |
| `GET /api/logs` | Recent in-memory logs | may expose local paths/query metadata | `UNAVAILABLE`; source-only in this build |
| `POST /api/process-kill` | Kill selected CBM PID | destructive process signal | `RESTRICTED`; source-only, unavailable in this build, and destructive |

The UI is optional operational tooling, not part of the controlled MCP study
surface. If later used, it needs its own build hash, endpoint/CORS/security
validation, output metrics, and isolation approval.

## Language and Hybrid-LSP inventory

The README's benchmark tiers name 35 languages:

| Advertised tier | Count | Names | Evidence status |
|---|---:|---|---|
| Excellent (>=90%) | 17 | Lua, Kotlin, C++, Perl, Objective-C, Groovy, C, Bash, Zig, Swift, CSS, YAML, TOML, HTML, SCSS, HCL, Dockerfile | `UNTESTED`; documentation benchmark claim only |
| Good (75-89%) | 16 | Python, TypeScript, TSX, Go, Rust, Java, R, Dart, JavaScript, Erlang, Elixir, Scala, Ruby, PHP, C#, SQL | `UNTESTED`; documentation benchmark claim only |
| Functional (<75%) | 2 | OCaml, Haskell | `UNTESTED`; documentation benchmark claim only |

The README additionally names 117 "supported, not yet benchmarked" entries:
Ada, Agda, Apex, Assembly (NASM), Astro, AWK, Beancount, BibTeX, Bicep,
Bitbake, Blade, Cairo, Cap'n Proto, Clojure, CMake, COBOL, Common Lisp,
Crystal, CSV, CUDA, D, Devicetree, Diff, `.env`, Elm, Emacs Lisp, F#, Fennel,
Fish, FORM, Fortran, FunC, GDScript, `.gitattributes`, `.gitignore`, Gleam,
GLSL, GN, Go module, Go template, GraphQL, Hare, HLSL, Hyprlang, INI, ISPC,
Janet, Jinja2, JSDoc, JSON, JSON5, Jsonnet, Julia, Just, Kconfig, KDL, Lean 4,
Linker Script, Liquid, LLVM IR, Luau, Magma, Makefile, Markdown, MATLAB,
Mermaid, Meson, Move, Nickel, Nim, Nix, Odin, Pascal, Pkl, PO (gettext), Pony,
PowerShell, Prisma, `.properties`, Protobuf, Puppet, PureScript, Racket, Regex,
`requirements.txt`, ReScript, RON, reStructuredText, Scheme, Slang, Smali,
Smithy, Solidity, SOQL, SOSL, Squirrel, SSH config, Starlark, Svelte, Sway,
SystemVerilog, TableGen, Tcl, Teal, Templ, Thrift, TLA+, Typst, Verilog, VHDL,
Vim script, Vue, WGSL, WIT, Wolfram, XML, and Zsh.

That named README inventory totals 152, not 158. Source closes the accounting
gap differently: 159 dialect enum members map to 158 distinct display names
(CFScript and CFML both display as `CFML`) and 156 `grammar_*.c` sources are
present because some dialects/special formats share parsers or use detectors.
No runtime language-list/schema exists, so "158" is source/docs reconciliation,
not a runtime-negotiated capability and not evidence of equal extraction
quality. The fixture verified TypeScript, Rust and TOML and correctly skipped
an unknown extension; it cannot validate the other languages.

The nine documented Hybrid-LSP families are:

| Family | Documented resolver scope | Source/runtime reconciliation | Disposition |
|---|---|---|---|
| Python | imports, dataclasses, typing/narrowing, common stdlib | wired in production per-file and cross-file dispatcher; not in fixture | `UNTESTED`; source-wired, runtime quality not exercised |
| TypeScript / JavaScript / JSX / TSX | generics, JSX/JSDoc, declarations/re-exports, chaining | production per-file/cross-file; 12 TS files processed in fixture cross pass, but not every advertised semantic behavior was isolated | `PARTIAL` |
| PHP | namespaces, traits, PHPDoc, binding/inference | production per-file/cross-file; not fixture-tested | `UNTESTED`; source-wired only |
| C# | namespaces/records/LINQ/async/generics/BCL | production prebuilt/cross-file path; not fixture-tested | `UNTESTED`; source-wired only |
| Go | package registry, generics, embedding/interfaces/imports | production prebuilt/cross-file path; not fixture-tested | `UNTESTED`; source-wired only |
| C / C++ | macros/typedef/header linking/templates/namespaces/inference | production cross-file includes CUDA; not fixture-tested | `UNTESTED`; source-wired only |
| Java | imports/hierarchy/generics/overloads/lambdas/JDK | production fallback cross-file path; not fixture-tested | `UNTESTED`; source-wired only |
| Kotlin | imports/classes/extensions/nullability/scope functions | production fallback cross-file path; not fixture-tested | `UNTESTED`; source-wired only |
| Rust | use/module paths, impl/traits/generics/operators/derive/UFCS/std | per-file resolver runs, and cross-file implementation/direct tests exist, but production `cbm_pxc_has_cross_lsp` omits Rust; source test explicitly records it as never called | `PARTIAL`, advertised cross-file quality not wired |

The full index log reported 12 files processed by the production cross-LSP
pass and six skipped for having no supported cross-LSP path. The two Rust files
were parsed and received per-file Rust LSP behavior, but their cross-file Rust
resolver was not invoked through the production index pipeline.

## Token and resource characteristics

These counts are local artifact estimates using
`gpt-tokenizer@3.4.0:o200k_base`; they are not provider billing counts.

| Artifact | Bytes | Local o200k tokens |
|---|---:|---:|
| MCP initialize artifact | 161 | 58 |
| Full current `tools/list` artifact | 15,389 | 3,541 |
| Pretty current input-schema artifact | 9,079 | 2,283 |
| `get_architecture` result | 7,631 | 1,914 |
| `get_graph_schema` result | 5,056 | 1,158 |
| Fresh full index result | 538 | 125 |
| Schema-valid semantic-array search | 12,505 | 3,007 |
| Exact workflow trace | 2,744 | 653 |
| Workflow snippet | 2,996 | 929 |

The mechanically regenerated representative ledger contains exactly one
current-fixture artifact for each of the 14 negotiated tools: 44,632 output
bytes and 11,033 local tokens. Three separately validated intentional failures
add 423 bytes/103 tokens, for 45,055 bytes/11,136 tokens across all 17
classified calls. Compact input schemas total 6,244 bytes/1,449 tokens across
the 14 representatives. These totals are exclusively from the
`e7ddad2...` ledger; mode, persistence, profile, ignore, precedence,
cross-repository, and watcher setup evidence is deliberately excluded from the
per-tool aggregate. The semantic-array response alone consumed 12,505 bytes
and 3,007 local tokens despite `limit=20`, so callers should prefer narrow
labels, qualified names, and smaller limits.

Provider usage for the Terra probe remains:

| Field | Value |
|---|---|
| Model | `gpt-5.6-terra` |
| Effort | `medium` |
| Completion obtained | no |
| CBM calls | 0 |
| Input/cached/output/reasoning tokens | UNKNOWN |
| Disposition | `UNTESTED`; historical attempt superseded as `DISCOVERY_SETUP` |

## Terra-medium probe disposition

No Terra run was launched for the current `e7ddad2...` fixture. The earlier
record used historical fixture `faa03d6...` and manifest `f9...`; it stopped
during runner setup before a model completion or CBM call. It is therefore
superseded as `DISCOVERY_SETUP`, not a capability result, and is excluded from
all tables and aggregates above. No replacement Terra attempt was made during
this repair.

The agent-mediated disposition remains `UNTESTED`, with provider tokens
`UNKNOWN`. A future controlled run must pin the current fixture, manifest,
prompt, runner version, model, effort, and call ceiling and must obtain any
required authorization independently; it cannot reuse the superseded metric.

## Reproduction outline

Use repository-relative paths and the isolated runner:

```bash
repo_root="$(git rev-parse --show-toplevel)"
fixture="$repo_root/scratchpad/code-intelligence/fixtures/cbm-e7ddad2-primary"
binary="$repo_root/scratchpad/code-intelligence/runtime/rebuild-cbm/source/build/c/codebase-memory-mcp"
blocker_dir="$repo_root/scratchpad/code-intelligence/runtime/lanes/cbm-capability-discovery/bin"

CODE_INTEL_EXTRA_PATH="$blocker_dir" \
  "$repo_root/docs/research/harness-tools/codebase-intelligence/experiments/coding-agents/run-isolated.sh" \
  cbm-e7ddad2-repro "$binary" cli --json index_repository \
  "{\"repo_path\":\"$fixture\",\"mode\":\"full\"}"
```

Before reproduction, verify source
`53ebeb4cf1fca0f4b2384e7ab085e529a2d2750b`, fixture
`e7ddad2c44321f7b50e60c923b8f0733fb757874`, and manifest digest
`fc12b07aa2219f346ee1e00f52875efae8c52bbb12dc410456e9457ea1b58e24`.
Reproduction must use a fresh isolated `CBM_CACHE_DIR`; real
install/update/uninstall and subject persistence remain outside ordinary
measured arms.

There is no single full-evidence replay script. The accurately bounded
`scratchpad/code-intelligence/raw-output/capability-discovery/cbm/rerun-core-tools-profiles-e7ddad2.sh`
regenerates only the legacy `full/`, `moderate/`, `fast/`, and `profiles/`
groups, plus identity, fixture-verification, and initial-ledger files. It
copies the immutable fixture template into a validated disposable work
directory and fails with the retained work-copy path if cleanup cannot
complete.

That bounded rerun excludes `mcp/`, `tools/`, `modes/`, `cross-repo/`,
`auto-index/`, `persistence/`, `ignore/`, `precedence/`, and `profile/`, plus
the root-level `cli/`, `config/`, `env/`, `ui/`, and `surface-metrics/`
groups. Retained companion entry points are `custom-extension-e7ddad2.sh` for
`custom-extension/`, `semantic-correction-e7ddad2.sh` for the corrected
semantic probe, `measure-e7ddad2.mjs` for legacy metrics, and
`e7ddad2/build-metrics.mjs` for current classified metrics. No replay command
was retained for the other excluded groups; those bytes are
integrity-verifiable through the manifest only when the ledger references
them. This is an explicit reproducibility limitation, not a full-rerun claim.

Run
`scratchpad/code-intelligence/raw-output/capability-discovery/cbm/test-rerun-safety-e7ddad2.sh`
to exercise cleanup-failure injection, immutable-template checks, portable
manifest digest verification, and exact ledger-reference coverage.

## Recommendation for controlled Pi/Codex experiments

Use CBM only from a fresh full index for each measured subject and verify the
reported source revision before every arm. Prefer:

- `search_graph` with qualified filters and explicit limits;
- `get_code_snippet` after ambiguity resolution;
- `query_graph` for non-aggregate read patterns whose rows can be
  source-checked;
- `get_graph_schema` to construct valid queries;
- `search_code` as a graph-adjacent literal fallback;
- `get_architecture` only as a hypothesis generator.

Do not use incremental refresh, `detect_changes`, grouped aggregation,
`ingest_traces`, or unverified `trace_path` modes as authoritative experimental
evidence. Any graph-derived claim still requires source verification. The
Terra-mediated capability probe should be rerun only after explicit
authorization for the exact prompt/fixture-derived payload and destination.
