# Code-Intelligence Tooling — Decision & Adoption Plan

**Single source of truth for the "which code-intelligence tools to adopt for maintaining large
codebases" effort.** Read this first to resume. Everything we decided, why, the evidence, and the
concrete next steps are here.

- **Owner:** user (mvpavan42)
- **Last updated:** 2026-06-24
- **Status:** ✅ Decision made (stack chosen) · ⏳ Not yet wired into the project (adoption = §8)
- **Next action on resume:** §8 Step 1 (register serena + CBM MCP servers; verify ast-grep CLI).

---

## 0. How to resume (30-second orientation)

1. We evaluated 8 code-intelligence tools for one use case: **an AI coding agent maintaining LARGE
   codebases over many sessions without re-reading files every task (to cut token cost).**
2. **Decision: adopt `serena` + `CBM` (codebase-memory-mcp) + `ast-grep` as the working stack.**
3. The decision is backed by (a) a measured 36-anchor accuracy study and (b) an independent 4-agent
   token-economics research panel (2 Opus + 2 Codex). Both are summarized below; raw artifacts in §10.
4. The stack is **chosen but not yet installed/configured**. The adoption plan is §8.
5. If revisiting the CBM-vs-codegraph choice or adding codegraph/headroom, see §7.

---

## 1. The decision

| Tool | Role in the stack | One-line justification |
|---|---|---|
| **serena** | Exact navigation + **symbol-level editing** | Only tool that is LSP-exact AND edits at symbol level (rename/replace-body/safe-delete) without reading whole files. |
| **CBM** (codebase-memory-mcp) | Persistent **auto-sync knowledge graph + semantic memory** — "where/what-calls/impact+risk/architecture/semantic-search" | Richest analysis surface (14 tools): semantic/NL code search, `detect_changes` impact+risk, dead-code, cross-service HTTP/gRPC linking, ADR memory, trace ingestion, Cypher; **highest measured accuracy** of the graph engines (§3.2). |
| **ast-grep** | Structural **search + rewrite + lint-rules** | The only safe bulk-codemod + structural-pattern + CI-invariant tool; does what ripgrep/serena/CBM cannot. |

**Absolute 2-tool floor (read-only navigation):** CBM + ast-grep.
**Full maintenance spine (navigate + edit):** serena + CBM + ast-grep ← **this is what we picked.**

**Tradeoff we accept by choosing CBM over codegraph (be aware on revisit):** CBM mounts **14 MCP tools** (~10–15K tool-schema on the first turn) vs codegraph's single tool (~tiny). We accept that overhead in exchange for CBM's far richer surface (semantic search, impact+risk, ADR, traces, cross-service) and its higher measured accuracy. The "mount only ONE graph engine" rule still holds — CBM **is** that one engine; do not also mount codegraph. See §2 and §7.

Tool versions/paths in this repo (verified 2026-06-24):
- serena `1.5.4.dev0` — `external/harness_repos/serena/.venv/bin/serena` (pyright LSP backend)
- CBM (codebase-memory-mcp) `0.8.1` — built static binary `external/harness_repos/codebase-memory-mcp/build/c/codebase-memory-mcp` (266 MB, zero-dep; has `install` to auto-register MCP, `cli` for headless queries)
- ast-grep `0.44.0` — `external/harness_repos/ast-grep/.local-npm/node_modules/@ast-grep/cli-linux-x64-gnu/ast-grep`
  (NOTE: `/usr/bin/sg` is **not** ast-grep — it's `newgrp`. Use the full path.)

---

## 2. Why this stack — the reasoning

**The 8 tools are four different species** (this framing drove everything; all 4 panel researchers
arrived at it independently):

| Species | Tools | Role |
|---|---|---|
| Graph/LSP query MCPs | **serena, CBM, codegraph** | the token lever — answer where/what/affected out-of-band |
| Structural search + rewrite | **ast-grep** | low-token pattern search + edit-without-reading |
| Whole-repo packers / comprehension | repomix, UA, graphify | onboarding/architecture; repomix *adds* tokens |
| Context-compression proxy | headroom | orthogonal amplifier (its `--code-graph` flag literally installs CBM) |

- We need **one** graph/LSP engine (not all three — they overlap and each adds MCP schema overhead),
  plus serena for editing, plus ast-grep for structural rewrite/lint. That's the spine.
- We picked **CBM** (codebase-memory-mcp) as the graph engine over codegraph for: the **richest
  analysis surface** in the set (14 tools — semantic/NL search, `detect_changes` impact+risk
  classification, dead-code, cross-service HTTP/gRPC/GraphQL linking, ADR memory, runtime-trace
  ingestion, Cypher queries, architecture overview), plus the **highest measured accuracy** of the three
  graph engines (merged 0.997, disambiguation 0.844 — §3.2), plus auto-sync freshness and a team-shared
  graph artifact. The **accepted cost** is more MCP schema overhead (14 tools vs codegraph's 1) — see
  the §1 tradeoff note. **codegraph is the close runner-up**, held in reserve as the minimal-overhead
  alternative (§7).
- We picked **serena** because it is the only tool that is *exact* (LSP) **and** can *edit* at the
  symbol level — the core of a maintenance loop is navigate-then-modify, and serena does both
  token-cheaply (rename/refactor 8–12× cheaper than read-rewrite cycles).
- We picked **ast-grep** because its lane (structural pattern match + bulk rewrite + YAML lint-rules)
  is genuinely disjoint from ripgrep (text), serena (named symbols), and CBM (edges) — see §5.3.

**Two divergences in the panel, and how we settled them:**
1. *Is serena in the minimum?* One researcher said the 2-tool floor (graph + ast-grep) suffices; three
   said serena is essential. → Resolved: it depends on editing. We maintain (edit) code, so serena is in.
2. *CBM vs codegraph?* Split 2–2. The panel leaned codegraph for *lowest MCP overhead*; the user's
   decision is **CBM**, valuing its richer feature surface (semantic search, impact+risk, ADR, traces,
   cross-service) and higher measured accuracy over codegraph's smaller schema footprint. → Resolved:
   **CBM is the engine**; we accept the higher tool-schema cost and keep codegraph in reserve as the
   minimal-overhead fallback (§7).

---

## 3. Evidence trail (so the decision is defensible on revisit)

### 3.1 Validated 4-anchor bodha pilot
Ran serena/CBM/codegraph on 4 bodha anchors. Established the capability laws and the AST-gold method.
Superseded by the full study below.

### 3.2 The 36-anchor two-repo accuracy study (Codex-gated)
**Files:** [two-repo-traversal-analysis.md](two-repo-traversal-analysis.html) (+ `.md`). Raw data:
`scratchpad/harness-2repo/`. 36 anchors (18 bodha + 18 data-miner), 21 symbol-type buckets, AST gold
(Codex-audited), 3 Codex review passes.

**The two-level result:**
- **Merged "which files touch this name" — near-tied** (file-level, def-files excluded):
  ast-grep 1.000 · CBM 0.997 · serena 0.984 · codegraph 0.981. *Any tool works for basic navigation;
  ast-grep ties at 0.5 s.*
- **Per-definition disambiguation — separates sharply:**
  **serena 0.995 · CBM 0.844 · codegraph 0.822 · ast-grep 0.489.** serena is the only tool that
  resolves import aliases; lexical can't scope.

**Caveat carried forward:** accuracy ≠ the deciding factor for *adoption* — token economics is. All three
chosen tools are accurate enough; serena leads on disambiguation, **CBM is the most accurate graph engine**
(merged 0.997 / disambiguation 0.844, both above codegraph's 0.981 / 0.822), and ast-grep is fast/cheap for
lexical+structural matches. CBM's accuracy edge is one reason the user's pick of CBM over codegraph is sound.

### 3.3 The token-economics research panel (4 independent agents: 2 Opus + 2 Codex/GPT-5.x)
Each researched independently (no access to our prior rankings) and converged. Key conclusions embedded
below so this file is self-contained (panel raw outputs were ephemeral in `/tmp`).

**Token-cost table (consensus; "agent tokens" = what lands in the context window):**

| Tool | One-time / index (agent tokens) | Per-query (context tokens) | Notes |
|---|---|---|---|
| **serena** | ~0 index (out-of-band LSP); **~24K tool-schema first turn** (29 tools, cached) | hundreds → few K (stubs by default; bodies on demand) | small 1–3 line edits favor built-in Edit; serena wins on cross-file refactor (8–12×) |
| **CBM** *(chosen engine)* | ~0 index (out-of-band, ms-fast; auto-sync watcher); **~10–15K** for 14 tool schemas first turn | ~300–1.5K typical (~680/q); deep hub-traces 17–32K (file-offloaded) | ~10× fewer tokens (arXiv 31 repos); 99.2% on 5 structural queries (CBM bench); 83% answer quality vs 92% file-read |
| **ast-grep** | 0 (stateless) | very low (matches only); rewrite edits in place = 0 read tokens | — |
| **codegraph** *(reserve)* | ~0 index (auto-sync); **1 tool = tiny schema** | ~5–10K per `explore`, but 1–3 calls, ~0 file reads | ~47% fewer tokens, 58% fewer tool calls (its Opus-4.8 benchmark) |
| repomix | 0 | **100K–500K+ (ADDS tokens)**; `--compress` ~70% off | snapshot/onboarding only |
| graphify | code-only ~0; semantic stage = LLM tokens | report ~250–300 tok / 2K query budget | architecture sidecar |
| UA | **HIGH** (multi-agent build) | low after build | human onboarding |
| headroom | 0 | **negative** — strips 60–95% off residual outputs | orthogonal amplifier |

**Do they reduce tokens? YES — decisively, for the spine.** Mechanism: replace the
`grep → read several files → grep again` discovery loop with one structured query returning
symbols/locations/edges/signatures (never file bodies). Realistic savings ≈ **an order of magnitude** on
relational work.

**The honest caveats (the skeptic's points — design around these):**
1. **The risk is BEHAVIORAL, not technical.** If the agent queries the graph *then still reads every
   candidate file*, savings collapse. Must enforce "graph-first, stop on bounded evidence" (§8 Step 4).
2. **MCP schema overhead is real** (~1K/tool/session) ⇒ mount ONE graph engine, not three. CBM is the
   chosen engine and its 14 tools cost ~10–15K of schema on the first turn — this is the price we pay
   for its richer surface; the mitigation is to mount *only* CBM (never also codegraph) and to lean on
   it enough that the per-session schema cost is amortized many times over.
3. **Stale indexes force fallback re-reads** ⇒ CBM's background-watcher auto-sync (and the optional
   team-shared `.codebase-memory/graph.db.zst` artifact) keep the graph fresh.
4. **repomix is the anti-pattern** for steady-state maintenance.

### 3.4 Clarifications from the follow-up Q&A
- **CBM does semantic / natural-language code search** (verified, README:147): `semantic_query` =
  local vector search via bundled `nomic-embed-code` (no API key, no Ollama, compiled into the binary),
  plus `SEMANTICALLY_RELATED` edges and MinHash near-clone (`SIMILAR_TO`). **Unique in the set** —
  serena/codegraph/ast-grep/ripgrep are name/pattern/edge based. It's embedding *similarity* (concept
  search), not an internal LLM NL→query translator (the agent is the translator, by design).
  → **This is one of the main reasons we chose CBM**: vocabulary-agnostic "find code that does X" is a
  first-class capability the lighter engines simply don't have.
- **ast-grep's unique lane vs ripgrep+serena+codegraph** (verified): it operates on **AST shape** (not
  text lines like ripgrep, not named symbols like serena, not edges like codegraph). Unique: (a) match
  by code *shape* with metavariables, (b) **structural rewrite/codemod at scale**, (c) **YAML lint-rules
  as CI gates**. It is NOT for "where is X used" (ripgrep+serena cover that) — it earns its slot only for
  bulk edits, pattern hunting, and invariant enforcement, which large-codebase maintenance needs.

---

## 4. (reserved)

---

## 5. Per-tool deep dive (the three we chose)

### 5.1 serena — exact navigation + symbol-level editing
- **Core value:** LSP-exact references/definitions/implementations + **editing** (`replace_symbol_body`,
  `insert_before/after_symbol`, `rename_symbol`, safe-delete; JetBrains backend adds move/inline +
  debugger). Returns symbol *stubs* by default, bodies on demand → token-cheap.
- **Token cost:** ~24K tool-schema on first turn (cached); per-query hundreds–few K.
- **Caveats (measured):** needs an **in-index definition** (can't do where-used for a symbol defined
  outside the indexed tree); `find_implementations` unsupported in this pyright build (no Protocol→impl
  bridge); small 1–3 line edits are cheaper with the built-in Edit tool (crossover ≈ rewriting >50% of a
  method).
- **Extra features to pilot:** `.serena/memories/*.md` (durable project knowledge across sessions),
  onboarding, structural diagnostics (compiler/lint errors as data).
- **Run:** `serena start-mcp-server --transport streamable-http --port <P> --project <repo> --context ide-assistant`

### 5.2 CBM (codebase-memory-mcp) — persistent auto-sync knowledge graph + semantic memory
- **Core value:** a single tree-sitter (+Hybrid-LSP) knowledge graph of functions/classes/call-chains/
  routes/cross-service links, queried by **14 MCP tools** spanning four jobs: (1) **search** —
  `search_graph` (label/name/degree filters), `search_code` (graph-augmented grep), `query_graph`
  (read-only openCypher subset), and `semantic_query` (local vector/NL concept search, no API key);
  (2) **trace** — `trace_path` BFS (who-calls / what-it-calls, depth 1–5); (3) **impact** —
  `detect_changes` maps a git diff to affected symbols + blast radius **with risk classification**;
  (4) **architecture/memory** — `get_architecture` (languages/packages/routes/hotspots/clusters in one
  call), `manage_adr` (persists Architecture Decision Records across sessions), `ingest_traces`
  (validate HTTP_CALLS edges from runtime traces). `get_graph_schema` first, `get_code_snippet` pulls a
  body by qualified name. Auto-syncs via a background watcher; ms-fast indexing; zero runtime deps.
- **Token cost:** ~0 index (out-of-band, ms-fast); **~10–15K tool-schema on the first turn** (14 tools,
  the price of the rich surface); per-query ~300–1.5K typical (~680/q), deep hub-traces 17–32K
  (file-offloaded). CBM's own bench: ~10× fewer tokens (arXiv, 31 repos) / 99.2% on 5 structural queries.
- **Caveats (measured):** **83% answer quality vs 92% for full file-read** (arXiv) — it trades a little
  completeness for an order-of-magnitude token cut; same-named-def disambiguation is **0.844** in our
  study (best of the graph engines, but cross-version over-attribution exists — below serena's 0.995);
  14-tool schema overhead means it must be the *only* graph engine mounted.
- **Extra features to pilot (high value):** `semantic_query` (vocabulary-agnostic "find code that does
  X"); `detect_changes` (git diff → affected symbols + risk → **which tests to run**, CI-ready);
  `manage_adr` (decision memory across sessions); `get_architecture` (one-call onboarding overview);
  dead-code detection (Cypher `WHERE NOT EXISTS { (f)<-[:CALLS]-() }`); cross-service HTTP/gRPC/GraphQL
  linking; team-shared graph artifact (`.codebase-memory/graph.db.zst`, commit once → teammates skip reindex).
- **Commands:** `codebase-memory-mcp install` (auto-detects agents, registers MCP + hooks);
  `codebase-memory-mcp config set auto_index true` (index on session start); `codebase-memory-mcp cli
  index_repository '{"repo_path":"<repo>"}'` (headless build); `... cli search_graph|trace_path|query_graph
  '{...}'` (headless queries); `CBM_CACHE_DIR=<dir>` relocates the store off the live repo.

### 5.3 ast-grep — structural search + rewrite + lint-rules (the unique lane)
- **Why it's not redundant with ripgrep/serena/CBM** (each works on a different unit — text /
  symbols / edges; ast-grep works on **AST shape**):
  - **(a) Search by code shape** with metavariables: `$X == None`, bare `except:`, `requests.get($U)`
    without `timeout=`. ripgrep false-positives on strings/comments; serena/CBM have no
    "find code shaped like this."
  - **(b) Structural rewrite / codemods at scale** (`run -p '<pat>' -r '<fix>' -l <lang> -U`): the
    killer feature. ripgrep can't edit; serena edits one named symbol; CBM doesn't edit.
  - **(c) YAML lint-rules as CI gates** (`scan -r rule.yml` / `--inline-rules`): encode invariants.
    **This repo already has such invariants** — bodha `safety.md`/`coding-style.md`: "no `os.environ`
    in business logic," "no f-string SQL," "no bare `except:`," "no mutable default args." ast-grep can
    enforce them. (High-value pilot — §8 Step 5.)
- **Token cost:** ~0 (stateless); matches only; rewrites edit in place with 0 read tokens.
- **Subcommands:** `run` (search/rewrite), `scan` (rule linting), `new` (scaffold rules), `lsp`.

---

## 6. (folded into §3.3 token table)

---

## 7. What we did NOT pick — and the trigger to revisit

| Tool | Why not now | Revisit when… |
|---|---|---|
| **codegraph** | Close runner-up to CBM, **held in reserve as the minimal-overhead engine**; CBM beats it on accuracy (0.997/0.844 vs 0.981/0.822) and feature breadth, so it lost on those — but codegraph wins on MCP footprint (**1 tool** vs 14) | The 14-tool MCP schema cost of CBM proves too heavy (e.g. crowding the tool budget), or you want a leaner read-only nav engine and don't need semantic search / ADR / traces / cross-service. Then swap CBM→codegraph (don't run both). Its `affected` test-impact (`git diff \| codegraph affected --stdin`) overlaps CBM's `detect_changes`. |
| **repomix** | Packs the whole repo — *increases* tokens; opposite of the goal | One-shot overview of an unfamiliar/remote repo; `--token-count-tree` budget diagnosis. Use `--compress`. |
| **graphify** | LLM build cost; human-facing | Architecture onboarding artifact; unique: **PR merge-conflict risk** (`prs --conflicts`), design-rationale ("why") capture. Run code-only/offline to keep tokens ~0. |
| **understand-anything (UA)** | High build cost; onboarding dashboard, not per-task | Human onboarding / guided tours / business-domain mapping. |
| **headroom** | Orthogonal — a compression proxy, not code intelligence | Optional **amplifier**: wrap the spine to strip 60–95% off residual tool outputs (reversible). Its `--code-graph` flag installs CBM — authors intend headroom+CBM as a stack, so it pairs naturally with our chosen engine. |

---

## 8. Adoption plan (resumable, ordered steps)

**Step 1 — Register the MCP servers + verify CLI.** *(start here on resume)*
- CBM: `external/harness_repos/codebase-memory-mcp/build/c/codebase-memory-mcp install` (auto-detects
  Claude Code and writes the MCP entry + hooks). Or register manually in `.mcp.json`:
  `{"mcpServers":{"codebase-memory-mcp":{"command":"<abs path to the built binary>","args":[]}}}`.
  Verify with `/mcp` — you should see `codebase-memory-mcp` with **14 tools**.
- serena: add an MCP server entry running `serena start-mcp-server --context ide-assistant --project <repo>`
  (streamable-http or stdio). Decide stdio vs http; set a tool-local SERENA_HOME.
- ast-grep: CLI is ready (full path above). Optionally add `ast-grep-mcp` if structural search via MCP
  is wanted; otherwise the agent calls the CLI.
- ⚠️ Mind MCP schema overhead — CBM's 14 tools are the heavy line item (~10–15K first turn). Mount CBM
  **as the only graph engine** (do NOT also mount codegraph), and consider trimming serena's tool surface.

**Step 2 — Index the target repos (out-of-band, ~0 agent tokens).**
- CBM: `codebase-memory-mcp cli index_repository '{"repo_path":"<bodha-repo>"}'` and the same for
  `<data-miner-repo>` (ms-fast). Then `codebase-memory-mcp config set auto_index true` so the
  background watcher keeps them fresh. `codebase-memory-mcp cli list_projects` / `index_status` to verify.
- serena indexes via LSP on project activation; optionally pre-warm.
- Confirm auto-sync works after an edit (re-query a changed symbol).

**Step 3 — Decide where indexes/config live** (don't pollute the live repos; per project git-safety).
CBM persists to `~/.cache/codebase-memory-mcp/` by default — override with `CBM_CACHE_DIR=<dir>` to keep
the store off the live repos. The optional team artifact `.codebase-memory/graph.db.zst` is only written
on demand; add `.codebase-memory/` and `.serena/` to ignore lists if you don't want them committed.

**Step 4 — Encode the workflow rule (prevents the behavioral token-collapse — the #1 caveat).**
Add a short rule (e.g. in `CLAUDE.md` or `.claude/rules/`): *"For navigation/where-used/impact
questions, query CBM/serena FIRST and stop on bounded evidence; do not read whole files to
re-derive what the graph already returned. Use CBM `semantic_query` for concept/NL search and
`detect_changes` for diff impact. Use ast-grep for structural patterns and bulk edits. Use
serena for symbol-level edits/renames instead of read-rewrite cycles."*

**Step 5 — Pilot the high-value untested features:**
- CBM `detect_changes` wired into a pre-commit/CI hook → map a diff to affected symbols + risk → run
  only the tests it touches.
- CBM `semantic_query` on a "find code that does X" task where the vocabulary doesn't match the symbol
  names → compare against grep/serena.
- ast-grep YAML lint-rules enforcing the bodha invariants (`no os.environ`, `no f-string SQL`,
  `no bare except`, `no mutable default args`) → CI gate.
- serena `rename_symbol` / safe-delete on a real refactor → compare token cost vs read-rewrite.

**Step 6 — Validate token reduction on a real maintenance task.** Pick a representative task; run it
"naive" (file reading) vs "graph-first" and record tokens/tool-calls. Target ≈ order-of-magnitude on
relational work. Record results back in this file.

**Step 7 (optional) — Amplify with headroom** if residual tool outputs are large; and/or fall back
CBM→codegraph if the §7 codegraph trigger fires (CBM's 14-tool schema cost proves too heavy).

---

## 9. Open questions / decisions deferred
- **CBM's real per-session token cost on our repos** — the ~10–15K first-turn schema + per-query cost is
  estimated, not measured in *our* harness; Step 6 settles whether the order-of-magnitude saving holds net
  of that overhead. If the 14-tool footprint proves too heavy, the §7 codegraph fallback is the lever.
- **serena MCP transport** (stdio vs streamable-http) and tool-surface trimming (its ~24–29 tools add
  schema cost; consider a slimmed tool set).
- **Line-level vs file-level** value (accuracy study was file-level only).
- **headroom integration** shape (proxy vs MCP vs agent-wrap) — not yet evaluated hands-on.

---

## 10. Provenance / artifact index
- **This file:** `docs/research/harness/tooling-decision-and-adoption-plan.md`
- **Accuracy study:** `docs/research/harness/two-repo-traversal-analysis.{md,html}`; pilot +
  cross-repo robustness: `docs/research/harness/robustness-synthesis.md`,
  `robustness-findings-deerflow.md`, `deerflow-architecture-learned.html`.
- **Study raw data/scripts/gold/scorer + 3 Codex transcripts:** `scratchpad/harness-2repo/`
  (`GROUND_RULES.md`, `goldbuilder.py`, `gold_manifest.json`, `score.py`, `scores.json`,
  `results/<repo>/<tool>.json`).
- **Tools:** `external/harness_repos/{serena,codegraph,ast-grep,codebase-memory-mcp,repomix,graphify,understand-anything,headroom}`.
- **Beads:** epic for this adoption = see `bd list` (created alongside this file). Research tasks
  `orch-y8u` (closed, accuracy study), `orch-kfd` (closed, Codex token research).
- **Panel:** 2 Opus + 2 Codex (GPT-5.x) token-economics researchers; conclusions embedded in §3.3
  (raw outputs were ephemeral).
