# Codebase-Analysis Tooling — Phase C Findings

Capstone synthesis of the 8-tool harness experiment against the **paperclip** subject (a
TS/TSX pnpm monorepo: ~2,961 files, ~38 workspace packages — 9 headline + ~29 adapter/plugin
sub-packages). Source: the 8 Phase B exploitation reports + 8 Phase A capability cards + the
Codex Phase A review. This is the one place cross-tool reading is allowed; no tools were re-run.
Method is **capability-first**: the comparison is an *output* of capability discovery, not a
uniform benchmark. Every number below traces to a Phase B exploitation report.

Tools: `serena`, `ast-grep`, `codegraph`, `codebase-memory-mcp` (CBM), `repomix`,
`understand-anything` (UA), `graphify`, `headroom`.

---

## 1. Executive summary

The eight tools are **not interchangeable**; they cluster by what they actually do, and only one
capability — "who calls the *shared* `isUuidLike` across the pnpm workspace?" — was attempted by
every understanding tool, making it the natural universal axis. On that axis the firm ranking is
**codebase-memory-mcp (16/16 files, 100% precision+recall) > codegraph (cross-package but missed
all 5 UI/JSX callers) ≈ graphify (15/16, one silent filename-filter drop) > understand-anything
(16/18 by tree-sitter callee-name, its import resolver scored 0) > ast-grep / repomix (lexical
parity with ripgrep, no binding) > serena (~2% recall — reverse references stay blind to barrel
re-exports even when the workspace is `pnpm install`ed; re-test confirmed)**. The crucial twist every semantic tool surfaced and grep
cannot: `isUuidLike` is **defined three times** (one shared canonical + two cli-local shadowing
copies), so the raw lexical "45 refs / 21 files" conflates callers of three different functions.
Beyond that axis, each tool has a genuine, defensible niche: ast-grep for AST-precise call-site
isolation and codemods, repomix for token-mass triage and bounded context packaging, graphify for
a zero-token whole-repo architecture map, codegraph for answer-sized verbatim source + tiered
blast radius, CBM for the cleanest cross-package call graph, serena for in-package symbol
de-duplication and navigation, UA for a free tree-sitter structural corpus, and headroom (not an
analyzer at all) for shrinking *structured* tool output before it hits the model.

---

## 2. Capability × tool matrix

Cells: `++` strong/verified, `+` partial/works-with-caveat, `~` only as a lexical or degraded
fallback, `-` not supported / out of scope by design, `N/A` category mismatch. Evidence numbers
are from Phase B.

| Capability | ast-grep | repomix | serena | codegraph | CBM | graphify | UA (det.) | headroom |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Lexical / structural pattern search | `++` 44/20 + AST call-site 24 | `++` 44/20 (=rg) | `~` regex fallback | `+` kind filters | `+` `search_code` | `+` graph query | `+` name sweep | `-` |
| Semantic cross-package ref resolution (shared `isUuidLike`) | `-` no import binding | `-` lexical only | `~` 1/45 (pruned collapse) | `++` cross-pkg, 0-config | `++` 16/16 files | `++` 15/16 importers | `+` 16/18 by callee-name | `-` |
| Symbol disambiguation (the 3 defs) | `~` surfaces, can't bind | `-` | `++` splits + attributes | `++` 3 defs split | `++` 3 defs, in_degree | `++` 3 nodes by site | `~` name sweep, no bind | `-` |
| Blast-radius / impact (transitive) | `-` | `~` lexical superset | `~` gated on workspace | `++` d1 159/85, d3 287/138 | `++` Cypher + risk | `+` affected by node-ID | `~` via callGraph | `-` |
| Architecture / module / dep map | `~` outline only | `+` 38-pkg edge map | `-` per-symbol only | `+` counts, no pkg edges | `+` boundaries/clusters | `++` 40s, edge-weighted | `+` in-degree hubs | `-` |
| Verbatim answer-sized source retrieval | `~` `-A/-B/-C` | `+` full digest blocks | `+` symbol body | `++` `explore`/`node` line-numbered | `+` `get_code_snippet` | `~` subgraph stdout | `-` | `-` |
| Entrypoint / call-path trace | `+` 1-hop CLI surface | `-` | `++` clean in-pkg | `+` cross-pkg w/ name noise | `++` depth-5 trace | `+` 2-hop import trace | `+` import map | `-` |
| Context packaging / token-mass triage | `-` | `++` 21.5k manifest, db=77% | `-` | `-` | `-` | `~` report MD | `+` scan-result | `-` |
| Structural lint / codemod | `++` YAML rules, rewrite | `-` | `+` rename (in-pkg) | `-` | `-` | `~` cycle detect | `-` | `N/A` |
| Output token compression | `-` | `+` `--compress` 45-58% (lossy) | `-` | `-` | `-` | `-` | `-` | `++` JSON 59% lossless |

Cross-cutting facts (verified): the four graph/LSP analyzers (serena, codegraph, CBM, graphify)
**separated and bound the 3 `isUuidLike` definitions** (UA only name-matches the callee, without
binding); only CBM, codegraph, and graphify **bound cross-package callers to the shared def with zero
config**; the **strongest human-usable whole-repo architecture artifacts were repomix and graphify**
(CBM's `get_architecture` and UA's structural corpus also span the repo, with weaker package/entrypoint
views); only headroom **compresses output**; only ast-grep does **codemod**.

---

## 3. Capability classification & comparison

### 3.1 UNIVERSAL — semantic cross-package reference resolution (the `isUuidLike` axis)

Every understanding tool attempted "who calls the *shared* `isUuidLike`," so this is the one axis
where a firm cross-all conclusion is warranted. The firm ranking and reconciliation are in §4.

### 3.2 UNIVERSAL — symbol disambiguation (the 3-definition shadowing)

All four graph/LSP tools (serena, codegraph, CBM, graphify) independently
discovered and *bound* that `isUuidLike` is **defined three times**: the canonical export at
`packages/shared/src/agent-url-key.ts` (with a `typeof`/null guard) plus two **local** copies at
`cli/src/commands/client/company.ts:157` and `teams.ts:461` (inline regex, **no null-guard**).
This is the single most important shared finding: the lexical "45 refs" conflates callers of
three *different* functions. The two cli files appear in the grep set as "consumers" but actually
call their own local copy — changing the shared function would **not** change cli behavior.
Verdict: **firm and unanimous among the binding tools** — all four graph/LSP tools refuse to merge
the three. The lexical tools (ast-grep, repomix) cannot bind (ast-grep at least *surfaces* the 3
defs); UA's deterministic pass only **name-matches** the callee `isUuidLike` and would over-count on a
colliding name — it does not split or bind the definitions. headroom is N/A (no resolver).

### 3.3 UNIVERSAL — lexical / structural pattern search

All tools can match text; the question is precision. **ast-grep and repomix are tied at the
ceiling**: both reproduce ripgrep exactly (44 refs / 20 files on the TS/TSX surface; the 1 miss
vs the 45/21 baseline is the `.md` prose ref, outside both tools' grammar/scope). **ast-grep
wins on structural precision**: its `isUuidLike($$$)` call-site pattern isolates **24 real
invocations / 18 files**, deterministically excluding the 3 def lines, the barrel re-export, and
the ~6 `import` statements that plain grep lumps in — a clean "actual calls" set with no regex
gymnastics. repomix's digest grep is byte-identical to ripgrep (it *is* grep over a flattened
file), so its reference set is an **upper bound / superset**, never a resolved graph. Firm
conclusion: **ast-grep is the best precise-grep tool; repomix is the best lexical-completeness
artifact; neither resolves bindings.**

### 3.4 OVERLAPPING — blast-radius / impact (codegraph, CBM, graphify)

Three tools quantify transitive impact, but they measure different things, so the counts are not
directly comparable:

- **codegraph**: `impact -d1` = 159 nodes / 85 files, `-d3` = 287 / 138 (transitive, pulls in
  test files). Tiered and quantified in a way grep cannot express.
- **CBM**: Cypher var-length paths + `detect_changes` risk classes; `trace_path` depth-5 in ~10ms
  over an 82k-node graph. Most expressive (openCypher subset).
- **graphify**: `affected <node-id> --depth 2` reverse blast radius (16 direct + transitive), but
  **only by node ID** — its label-keyed `affected "isUuidLike()"` *refuses* on duplicate labels.

Conclusion: **codegraph for tiered numeric blast radius, CBM for query-expressive impact, graphify
for offline impact if you key by node ID.** All three inherit their reference-resolution recall
ceiling from §4 (so codegraph's impact under-counts UI, graphify's misses `secrets.ts`).

### 3.5 OVERLAPPING — architecture / module / dependency map (repomix, graphify, CBM, codegraph, UA)

- **graphify** is the strongest *offline structural* map: whole-repo extract in **~40s, 0 tokens**,
  edge-weighted (`server→db 1731`, `ui→shared 1423`, `server→shared 1091`, `adapters→adapter-utils
  554`), God-Nodes (`cn()` 511 edges), and **free import-cycle detection** (`plugin-lifecycle`
  cycle, `adapter-utils` cycles). It recovers the real hub structure (shared/db) directionally with
  no config. Caveat: `--no-label` leaves 669 communities as "Community N" (over-segmented for 9
  packages); naming needs an LLM.
- **repomix** is the strongest *declared-dependency* map: one 21.5k-token manifest packs all 41
  `package.json`/workspace files → the complete **38-package** internal edge map (server/ui/cli
  fan-in, shared + adapter-utils + plugin-sdk hubs). This is *declared* truth, not resolved-import
  truth — but exact and bounded.
- **CBM** gives `boundaries` (cross-segment call counts: `src→plugins 766`, `adapters→adapter-utils
  498`) and labeled Louvain `clusters` (ui/server/cli) — but its `packages` view uses dir-name
  segments, not the 9 pnpm names, with fan_in/out all 0; the real hub signal comes from `layers`
  fan-in (`plugins 922 in`, `adapter-utils 889 in`).
- **codegraph** gives accurate per-dir file/symbol counts (ui 784, packages 665, server 568, cli
  132) but **no first-class package-edge graph** (edges are inferred from call trails).
- **UA (deterministic)** finds intra-package in-degree hubs (`ui/src/lib/utils.ts` 115) but
  **systematically under-counts cross-package coupling** because its resolver drops `workspace:*`.

Conclusion: **graphify for the offline weighted structural map; repomix for the exact declared
dependency edges; CBM for call-boundary + cluster orientation.** None emits a clean "9 pnpm
packages and their edges" view without caveats — repomix's declared-dep map is the closest to that.

### 3.6 OVERLAPPING — verbatim answer-sized source retrieval (codegraph, CBM, repomix)

- **codegraph** is purpose-built here: `explore`/`node` return **line-numbered verbatim source**
  (`<n>\t<line>`, safe to Edit) + call path + blast-radius annotations in one capped call
  (`explore_arch.out` = 372 source lines + relationships). This is the concrete basis for its
  "near-zero file reads" claim — real for *symbol/flow* questions.
- **CBM** `get_code_snippet` returns exact source by qualified name (the 4-line `isUuidLike`).
- **repomix** packs full file bodies into a digest, but at whole-repo scale (5.96M compressed
  tokens) you must slice; it is retrieval-by-packing, not retrieval-by-query.

Conclusion: **codegraph is the best "answer-sized source + context in one call" tool.**

### 3.7 OVERLAPPING — entrypoint / call-path trace (serena, codegraph, CBM, graphify, UA)

- **serena**: cleanest *in-package* trace (CLI `index.ts → registerRunCommands → run.ts`, 2-3 hops,
  sub-second, high confidence) — but cannot cross the package boundary on the pruned subject.
- **CBM**: `trace_path` depth-5, e.g. `registerCompanyCommands` outbound → 96 callees spanning
  cli→shared→db; the most capable multi-hop tracer.
- **codegraph**: `node --symbols-only` lists 94 calls from `cli/src/index.ts`, cross-package, but
  with name-collision noise (`version`→`ui/...`, `description`→a server service).
- **graphify**: 2-hop import trace (entrypoint → command module → `register*`), import-edge based.
- **UA**: import-map trace, degraded by the same workspace-alias gap.

Conclusion: **CBM for deepest multi-hop, serena for cleanest in-package, both better than the
import-edge tracers (graphify/UA) which lose cross-package hops.**

### 3.8 UNIQUE capabilities (one tool — standalone result)

- **Context packaging / token-mass triage → repomix (unique).** `--token-count-tree` surfaced that
  `packages/db` = **77% of all package tokens** (~all generated migration snapshots), full subject
  = **10.86M raw / 5.96M compressed** tokens. "What will blow my context, exclude it" becomes a
  1-second answer. No other tool does this.
- **Structural lint / codemod → ast-grep (unique).** Config-free YAML rules (`--inline-rules`),
  AST-precise rewrite (`-r`), SARIF/GitHub output. One-shot surface counts: **512 `useEffect`, 601
  `useState`, 412 route registrations**. (Constraint: `constraints:` field failed to parse inline
  in 0.44.0 — needs a rule file.)
- **Output token compression → headroom (unique, and not an analyzer).** See §3.9.
- **Free import-cycle detection → graphify (effectively unique among these runs).** Surfaced real
  cycles (`server/src/services/plugin-{lifecycle,loader,tool-dispatcher}.ts`, `adapter-utils`) for
  free during extraction.
- **Near-clone detection → CBM (unique).** `SIMILAR_TO` (MinHash/LSH) found 1,763 clone pairs
  (`AssigneePicker`↔`ProjectPicker` 0.969); but it **missed the 3 tiny `isUuidLike` copies**
  (4-line bodies below the shingle threshold) — useful for large bodies, blind to small ones.

### 3.9 NOT-A-CAPABILITY (category) — headroom

headroom is a compression layer, ranked only as an add-on. Verified content-typed behavior:
**JSON arrays ~58.7% (SmartCrusher, lossless-ish, deterministic — the one trustworthy win);
search/grep results ~98.7% but LOSSY** (samples ~30 of 2,897 matches + a retrieval hash stub);
**plain file listings and raw `.ts` source ~0%** through the default API. Two structural traps:
(1) the default profile **protects the most-recent message**, so the canonical "compress this tool
output and answer" shape compresses *nothing* but JSON; (2) AST code compression (37% body removal,
signatures preserved) only fires via direct `CodeStructureHandler` invocation, **not** through the
public `compress()` API on TS. On a precision-sensitive reference task it can only **degrade
recall** — its 98.7% on the rg set would drop ~15 of 45 hits unless `headroom_retrieve` is wired.

---

## 4. Firm universal conclusion — the `isUuidLike` ranking (with caveats)

**Question:** who calls the *shared* `isUuidLike` (defined at
`packages/shared/src/agent-url-key.ts`, exported via `@paperclipai/shared`), resolving the pnpm
`workspace:*` alias across packages?

**Ground truth.** Lexical (ripgrep): **45 refs / 21 files** (server 11, ui 5, packages 2, cli 2,
doc 1). But `isUuidLike` is **defined 3 times** (shared + two cli-local shadows), so the true
cross-package consumers of the *shared* def ≈ **16 files (11 server + 5 ui)**. The counts below
differ legitimately by **(a) file-vs-callsite counting, (b) whether the 2 cli shadow files are
attributed to the shared symbol or excluded, and (c) the JSX/dynamic-dispatch boundary** — shown,
not flattened.

| Rank | Tool | Result on the shared-def callers | Mechanism | Why it ranks here |
| --- | --- | --- | --- | --- |
| 1 | **CBM** | **19 caller symbols / 16 files = exactly 11 server + 5 ui** | Hybrid-LSP CALLS edges resolve `@paperclipai/shared`, 0-config | **100% precision AND recall** for "callers of the shared def," **including the 5 UI calls codegraph missed**; correctly excludes def/barrel/doc/cli-local. Caveat: traces **by name** — would collapse the 3 defs if their caller sets overlapped (here they don't). |
| 2 | **codegraph** | 20 caller symbols / 13 files (cli 2 + server 18); `impact -d1` ui:6 | tree-sitter graph, cross-pkg 0-config | Resolved cross-package with zero config and returns answer-sized source, **but `callers` dropped all 5 UI calls** — they sit in React component bodies / JSX arrow `const`s (the dynamic boundary); `query`/`impact` partly compensate. |
| 2= | **graphify** | **15/16 importers** (94% recall, 100% precision) + barrel + 3 call edges | offline AST, barrel re-export followed | Bare `@paperclipai/shared` resolved through the `index.ts` barrel, 0-config, 0 tokens. The **1 miss = `server/src/services/secrets.ts`**, silently dropped by a credential-filename filter (`detect.py:123`) — a **real tool defect**, not a resolution failure. |
| 4 | **understand-anything** | name-based callsite sweep: callGraph **16/18 files**; import-resolver **0/18** | callee-NAME match, **not** shared-def/import resolution | **Not a shared-def binding** like ranks 1–2: its import resolver scored 0/18 (drops `workspace:*` by design), and the 16/18 comes from matching the callee name `isUuidLike` across files. Because the server/ui consumers have **no** local shadow, name-matching recovers them — but the method **cannot distinguish a call to the shared def from a call to a cli-local copy** and does not bind to any definition (it would conflate the three wherever their call sites coexist). The advertised semantic product is LLM-host-driven and not runnable isolation-clean. The 2 misses are a nested `catch` and a JSX-arrow attribution failure. |
| 5 | **ast-grep** | 44 refs / 20 files lexical; **24 call sites** via `isUuidLike($$$)` | syntactic AST, no binding | Exact ripgrep parity + AST-precise call-site isolation, but **no import resolution — cannot bind the 3 defs.** Cross-package = N/A by design. |
| 5= | **repomix** | 44 / 20 (= ripgrep) | lexical over flattened digest | An **upper bound, not a graph**; `--compress` drops bodies → recall collapses to **19/44 (43%)**. Not semantic. |
| 7 | **serena** | **1 ref (the barrel re-export only) ≈ 2% recall** | LSP/tsserver | `find_referencing_symbols` reaches only same-file + barrel refs, never the 16 cross-package consumers (it does correctly separate the 3 defs). **Re-tested on a fully `pnpm install`ed workspace** ([retest doc](results/serena/retest-installed-workspace.md)): **still 1 ref / 0-of-16.** Install rescues *forward* go-to-def (now resolves cross-package) but NOT *reverse* references — the cause is **barrel re-export indirection** (tsserver's `references` does not transit the `export {X} from './y'` hop), not pruning. The Phase-B "pruning" hypothesis was only half right. |
| — | **headroom** | N/A — compression only | — | Can only *degrade* recall (its 98.7% on the rg set was lossy sampling). |

**Firm conclusion:** **CBM is the single best tool on this axis** (only tool at 100%/100% including
UI/JSX), **codegraph and graphify are a close, well-matched second** (both resolve cross-package
0-config; each has exactly one recall hole — codegraph's JSX boundary, graphify's `secrets.ts`
filter defect), **UA's deterministic callGraph is a strong free fourth**, the **two lexical tools
are exact but unresolved**, and **serena is last because its reverse `find_referencing_symbols` is
structurally blind to barrel-exported symbols** — a re-test on a fully installed workspace (§5, §6)
proved this is a tsserver/barrel limitation, not the pruned-subject artifact Phase B assumed. The
honest reconciliation of the differing counts: file-vs-callsite explains 16 files vs
19-20 symbols vs 24 call sites; the 3-def shadowing explains why cli's "2 files" are correctly
excluded by the graph tools but counted by grep; and the JSX/dynamic boundary explains codegraph's
5-call UI gap vs CBM's full coverage.

---

## 5. Per-tool verdict (best at / where it fails, on a TS/TSX monorepo)

**ast-grep** — Best at **AST-precise structural search and codemod**: `isUuidLike($$$)` cleanly
isolates 24 real call sites from defs/imports (grep conflates 44), one-shot surface inventory (512
useEffect / 601 useState / 412 routes), sub-second over 2,162 files, lowest friction (stateless,
zero files written even to HOME), and the only codemod tool. Fails at anything semantic: no import
resolution, no cross-package binding, no caller graph; one language per invocation; no markdown
grammar (its sole baseline miss). T4 is out of scope by construction.

**repomix** — Best at **bounded context packaging and token-mass triage**: a 21.5k-token manifest
of all 2,961 files, the complete 38-package declared-dependency edge map from one pack of 41
`package.json`s, and the finding that `packages/db` = 77% of package tokens (slicing mandatory).
Its uncompressed digest grep equals ripgrep exactly. Fails as an analyzer: no symbol resolution or
call graph; `--compress` halves reference recall (19/44) because it drops bodies; whole compressed
subject (5.96M tokens) still exceeds any context window. Footguns: `--no-gitignore` mandatory on
this subject; git context bleeds from cwd unless run inside the subject.

**serena** — Best at **in-package symbol navigation, forward go-to-definition, and de-duplication**:
clean 2-3-hop CLI trace, sub-second outlines/bodies, authoritative "is this the same symbol?" (it
found the 2 cli shadow defs and refused to merge them), and — once the workspace is `pnpm install`ed
— **exact cross-package go-to-definition** (server and ui consumers resolve to the shared def). Fails
at **reverse cross-package references / blast radius**: ~2% recall (1 of 16 caller files) on shared
`isUuidLike`. A re-test on a fully installed workspace
([results/serena/retest-installed-workspace.md](results/serena/retest-installed-workspace.md)) proved
this is **not** a pruning artifact — it is **barrel re-export indirection** that tsserver's
`references` does not traverse, so serena is structurally blind to the real consumers of any
barrel-exported symbol (i.e. paperclip's entire public API). No whole-repo architecture output;
headless use requires a scripted MCP client; backgrounded launches need inline `env HOME=…` (see §7).

**codegraph** — Best at **answer-sized verbatim source + tiered blast radius in one call**:
`explore`/`node` return line-numbered editable source + call path + impact (`-d1` 159/85, `-d3`
287/138), resolves cross-package imports with zero config, separates the 3 `isUuidLike` defs. Fails
on **JSX/React call sites**: `callers` dropped all 5 UI calls (component bodies / arrow consts —
the dynamic boundary); NL `explore` is keyword-matched not semantic; indexes **code only** (no
README/docs/yaml), so onboarding/doc questions need Read/grep. Footgun: `--no-watch` is invalid on
`init` (silent no-op).

**codebase-memory-mcp** — Best at **the cleanest cross-package call graph**: 16/16 files at 100%
precision+recall on shared `isUuidLike` (including the UI calls codegraph missed), 0-config
`workspace:*` resolution, an openCypher subset for impact/dead-code, near-clone detection (1,763
pairs), all sub-100ms over an 82k-node graph indexed in 3.27s. Fails at **package-level
architecture** (the `packages`/`entry_points` views are dir-name heuristics with fan_in/out 0, not
the 9 pnpm packages); `detect_changes` read the **parent repo's** git diff (worktree bleed);
`semantic_query` doesn't exist; traces **by name** (would collapse colliding symbols). Build is a
65s C compile (single-shot). Token-savings claims are unmeasurable from the CLI.

**graphify** — Best at **a zero-token, offline, whole-repo architecture map**: ~40s extract →
edge-weighted dependency graph (server→db 1731, ui→shared 1423), God-Nodes, **free import-cycle
detection**, and 94% recall / 100% precision on shared `isUuidLike` (barrel re-export followed
0-config). Fails via a **real silent defect**: any file named `secrets.ts`/`credential*`/`password*`
is dropped by a credential-filename filter (`detect.py:123`) — that is its 1 isUuidLike miss and a
general recall hole. Label-keyed `path`/`explain`/`affected` are brittle on duplicate names (must
use node IDs); 669 communities over-segment 9 packages; offline `--no-label` leaves communities
unnamed.

**understand-anything** — Best at **a free deterministic structural corpus**: whole code set
(2,236 files) scanned + structured in ~10s, 9,659 functions / 7,889 exports as queryable JSON, and
a tree-sitter callGraph that recovered **16/18 `isUuidLike` callers (89%) at 100% precision with
enclosing-function per call site** — beating its own import resolver. Fails at the **advertised
product**: the knowledge graph, guided tours, domain view, and dashboard are LLM-host-driven and
**not runnable isolation-clean** (every install path is global/PATH-polluting); its deterministic
import resolver drops `workspace:*` entirely (0/18 on cross-package edges), so it systematically
under-counts monorepo coupling.

**headroom** — Best at **shrinking structured tool output before it hits the model**: JSON arrays
compress ~58.7% deterministically (SmartCrusher, the one trustworthy lossless-ish win), robust to
config. Fails everything else: it is **not an analyzer** (no query/answer surface, never crawls the
repo); grep/search results compress ~98.7% but **lossily** (samples ~30 of 2,897, hashes the rest);
plain listings and raw `.ts` source compress 0% through the public API; the default profile protects
the last message so the canonical "compress this and answer" shape yields ~0%. Only safe in front of
a reference task if `headroom_retrieve` is wired.

---

## 6. Monorepo lesson — pnpm `workspace:*`, barrel re-exports, JSX call sites

The defining challenge of this subject is resolving the `@paperclipai/shared` workspace alias
through a barrel re-export to the leaf definition, on a subject that was **pruned of `node_modules`**
and has **no tsconfig `paths`** for the workspace packages.

| Concern | Resolve it 0-config | Resolve via callee-name (not imports) | Need a built/linked workspace | Lexical-only (no resolution) |
| --- | --- | --- | --- | --- |
| pnpm `workspace:*` alias | CBM, codegraph, graphify | UA (callGraph) | **serena** — *forward* go-to-def only (even installed, *reverse* refs stay ~2%) | ast-grep, repomix |
| Barrel re-export (`index.ts`) | graphify (explicit `re_exports` edge), CBM, codegraph | — | serena reverse-refs blind to barrel even when installed | ast-grep, repomix |
| JSX / React component-body call sites | **CBM (got all 5)** | UA (16/18; 2 misses = nested `catch` / JSX-arrow attribution) | — | ast-grep, repomix (lexical only) |

Lessons: (1) **Tools that read `workspace:*` deps and/or follow barrel re-exports (CBM, codegraph,
graphify) out-resolve everything else with zero config** — this is the single most discriminating
monorepo signal. (2) **A tree-sitter callGraph keyed on callee name (UA, and graphify's call edges)
recovers most callers even with no import resolution at all** — cheap and surprisingly effective for
a unique symbol name, but it over-counts on name collisions. (3) **LSP tools (serena) split sharply by
direction.** A `pnpm install`ed workspace rescues *forward* go-to-definition (cross-package resolution
via the symlink), but *reverse* `find_referencing_symbols` stays blind to **barrel-exported** symbols
even when installed — tsserver's `references` does not transit `export {X} from './y'` re-export hops
(verified by re-test, not inferred). Serena is strong for "where is this defined?" and weak for "who
calls this?" on a barrel-API monorepo. (4) **JSX/React call sites are
the recall frontier**: only CBM bound all 5 UI calls; codegraph's static extractor and UA's
tree-sitter attribution both miss calls inside component bodies / arrow consts.

---

## 7. Isolation outcome

**Phase B (all 8 runs): clean** (orchestrator-verified — [results/_isolation_audit.md](results/_isolation_audit.md)). Every run was independently verified **home-local** (tool-local
`HOME` + tool-specific cache/store env vars), **no-global-bin** (`command -v <tool>` returns nothing;
invoked only by explicit path), and **subject-untouched** (canonical `_paperclip_src` still
read-only `dr-xr-xr-x`, file count unchanged, no tool artifacts written into it; `external/paperclip`
submodule clean). Notable: serena/codegraph/CBM/graphify wrote indexes only into writable copies or
tool-local caches; ast-grep, repomix, and headroom are effectively stateless (wrote zero or one
artifact to the tool-local HOME); serena's TS language server auto-installed under `SERENA_HOME` by
explicit path, never globally.

**Two Phase-A leaks (caught by an independent orchestrator audit, since remediated).** Full evidence:
[results/_isolation_audit.md](results/_isolation_audit.md). Before the HOME/telemetry hardening existed,
two tools leaked into the real `$HOME` on their *first* executing (Phase-A discovery) run: **codegraph**
wrote `~/.codegraph` (a `telemetry.json` with `machine_id` `85a36509-…` + one queued anonymous
`cli_command:init` event; its `daemons/` dir was empty — no socket, no live process), and **graphify**
wrote `~/.cache/graphify-queries.log` (one 314-byte query record). The orchestrator audit **removed both**
(verified absent afterward); the real `$HOME` is now clean of all 8 tools' artifacts. Independently,
graphify's Phase B report notes its real-`$HOME` query log was byte-identical/untouched *by the Phase B
run* (Phase B writes landed in the tool-local `HOME`); removing the Phase-A record was the orchestrator's
action.

**A third leak — the serena re-test (background-process `HOME` non-inheritance).** When serena's MCP
server was launched as a *background* process for the installed-workspace re-test, it did **not**
inherit the shell's exported `HOME`/`SERENA_HOME` (the harness background-task wrapper re-sources the
user profile), so serena wrote 146 global home files (TS LS install, `serena_config.yml`, logs) to the
real `~/.serena`. The worker verified every file was from that run, then **quarantined** the dir into
the tool sandbox; the orchestrator independently confirmed real `~/.serena` and `~/.solidlsp` are now
absent. No global PATH binary was created (no install-bleed). Evidence:
[results/_isolation_audit.md](results/_isolation_audit.md) and
[results/serena/retest-installed-workspace.md](results/serena/retest-installed-workspace.md).

**Lesson:** the tool-local-HOME + telemetry/log kill-switch hardening must apply **from the very
first run that EXECUTES a tool**, not just from the heavy phase — and for **backgrounded** processes it
must be passed **inline** (`env HOME=… SERENA_HOME=… <cmd>`), because a background wrapper that
re-sources the user profile drops the parent shell's `export`s. Capability cards correctly *flagged* the
telemetry/log risks (codegraph `CODEGRAPH_TELEMETRY=0`, graphify query log, headroom telemetry opt-out,
CBM `~/.cache` default), but a flag only helps if it is actually wired at first execution and survives
backgrounding.

---

## 8. Open questions / what remains unmeasured

- **serena on a `pnpm install`ed subject — RESOLVED (the Phase-B hypothesis was wrong).** Re-tested
  ([results/serena/retest-installed-workspace.md](results/serena/retest-installed-workspace.md)):
  installing the workspace rescues *forward* go-to-definition but **not** reverse
  `find_referencing_symbols`, which stays at 1 ref / 0-of-16 due to barrel re-export indirection, not
  pruning. Residual unknown: a symbol imported **directly** from its defining module (no barrel) would
  likely get full reference recall — untested here, since paperclip's public API is entirely barrel-exported.
- **The LLM-driven products were never run.** understand-anything's knowledge graph / tours / domain
  view / dashboard and graphify's LLM-named communities + narrative report are the advertised value
  and are **not runnable isolation-clean** (global install + host-model tokens). Only the
  deterministic substrates were measured.
- **Vendor token-saving claims are unmeasurable from the CLIs.** CBM's "10x/120x fewer tokens,"
  codegraph's "47% fewer tokens / 58% fewer tool calls," graphify's "71.5x fewer tokens," and
  headroom's "60-95%" are *workflow* comparisons vs a Read/grep loop, not output fields — none can
  be confirmed without an equal-answer-quality agentic A/B, which this harness did not run.
- **No equal-answer-quality task A/B.** The comparison is capability- and accuracy-based (precision/
  recall on a labeled anchor), not a tokens-at-equal-quality benchmark across the 6 standing tasks —
  that remains the highest-value unrun measurement (Codex Phase-A "top measurement #3").
- **codegraph's JSX gap and graphify's `secrets.ts` filter** are single data points on one anchor;
  whether codegraph misses *all* JSX call sites generally, and how many files graphify's credential
  filter silently drops repo-wide, are not quantified.
- **CBM's name-collision robustness** is untested: `trace_path` traces by name and would collapse
  the 3 `isUuidLike` defs if their caller sets overlapped — here they don't, so its 100% is partly
  fortunate on this anchor.
- **Full-subject scalability ceilings** (peak RAM, OOM thresholds, failure modes at >2,961 files)
  were observed only at this subject's size, not stress-tested.
