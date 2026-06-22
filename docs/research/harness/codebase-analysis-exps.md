# Codebase Analysis — Tooling Experiments

**Goal.** Use the codebase-analysis tools below as independent *lenses* to understand the **paperclip** repo (`external/paperclip`) as deeply as possible, then compare them — but only where their capabilities genuinely overlap.

**Method (capability-first, not a uniform benchmark).** These tools do not solve the same problem; each is strong in its own domain, so we do **not** force a single head-to-head. Comparison is an *output* of capability discovery, not a rubric imposed up front:

1. **Characterize** each tool — what it is actually capable of, and where it is strong.
2. **Exploit** each tool to the *full* extent of those capabilities against paperclip; store the results.
3. **Repeat** for every tool.
4. **Compare overlaps** — where a capability is shared by a *subset* of tools, compare those head-to-head.
5. **Establish universals** — where a capability is common to *all* tools, compare and draw a firm conclusion.

## 1. Subject under test — paperclip

- **Path:** `external/paperclip`  ·  **Origin:** `github.com/paperclipai/paperclip`
- **What it is:** "the app people use to manage AI agents for work."
- **Stack & size (verified):** TypeScript/TSX **pnpm monorepo** — ~3,071 tracked files (1,674 `.ts`, 488 `.tsx`, 311 `.md`, 192 `.json`, 110 `.sql`); workspaces include `packages/`, `server`, `ui`, `cli`, `evals`.
- **Why it is a good subject:** large, multi-package, multi-language (TS + SQL + shell) — a realistic stress test that punishes shallow file-by-file exploration.

## 2. Tools under test (the lenses)

Each tool lives in `external/harness_repos/<tool>/`. **Status:** only `headroom` is cloned so far; the other seven still need cloning (see §4).

| Layer                   | Tool                    | GitHub                                                                            | Best functionality to test                                                                                                                                                                                                                                                                      | What success should look like                                                                                                      |
| ----------------------- | ----------------------- | --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Base navigation         | **Serena**              | [oraios/serena](https://github.com/oraios/serena)                                 | Symbol-level code navigation: find symbol, symbol overview, find references, semantic edits, diagnostics. Serena says it lets agents explore codebases "at the symbol level" without reading entire files. ([source](https://github.com/oraios/serena))                                         | Agent answers "where is this defined / who calls this / what should I edit?" without doing many grep/read loops.                   |
| Base structural search  | **ast-grep**            | [ast-grep/ast-grep](https://github.com/ast-grep/ast-grep)                         | AST-based structural search and rewrite. It searches/replaces code using Tree-sitter ASTs rather than plain text. ([source](https://github.com/ast-grep/ast-grep))                                                                                                                              | Agent finds "all code shaped like this" reliably: handlers, decorators, async functions, config patterns, repeated anti-patterns.  |
| Base graph memory       | **CodeGraph**           | [colbymchenry/codegraph](https://github.com/colbymchenry/codegraph)               | Pre-indexed local code knowledge graph, auto-sync, MCP integration. It claims agents query graph structure instead of scanning files. ([source](https://github.com/colbymchenry/codegraph))                                                                                                     | Agent uses graph queries for architecture, entrypoints, dependencies, and impact instead of raw file discovery.                    |
| Base graph memory       | **Codebase-Memory MCP** | [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp)   | Persistent Tree-sitter/LSP knowledge graph, call chains, architecture, impact analysis, dead-code detection, cross-service links. It claims 10× fewer tokens and 2.1× fewer tool calls vs file-by-file exploration. ([source](https://github.com/DeusData/codebase-memory-mcp))                 | Agent answers "what depends on this?" and "what is the blast radius?" with a graph result, not a long exploratory trace.           |
| Base repo packaging     | **Repomix**             | [yamadashy/repomix](https://github.com/yamadashy/repomix)                         | Pack repo/folder into AI-friendly output, token counting, ignore rules, Secretlint, Tree-sitter compression. ([source](https://github.com/yamadashy/repomix))                                                                                                                                   | You get a compact repo digest and token-count tree; useful for comparing raw vs compressed context.                                |
| Teaching / onboarding   | **Understand Anything** | [Egonex-AI/Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) | Interactive codebase knowledge graph, guided tours, semantic search, domain view, onboarding, diff impact. It explicitly says it builds a graph of files/functions/classes/dependencies and gives a dashboard to explore visually. ([source](https://github.com/Egonex-AI/Understand-Anything)) | It teaches the repo: architecture, main flows, business/domain concepts, "read these files first," and impact of changes.          |
| Teaching / graph report | **Graphify**            | [safishamsi/graphify](https://github.com/safishamsi/graphify)                     | Queryable knowledge graph over code, docs, SQL, infra, images, PDFs, etc. It nudges agents to query the graph before grepping/reading raw files. ([source](https://github.com/safishamsi/graphify))                                                                                             | Agent uses `graphify query` for architecture questions and produces `GRAPH_REPORT.md` / `graph.json` you can inspect.              |
| Compression             | **Headroom**            | [headroomlabs-ai/headroom](https://github.com/headroomlabs-ai/headroom)           | Runtime compression of tool outputs, logs, files, RAG chunks, and history. It offers library, proxy, agent wrap, and MCP modes; claims 60–95% fewer tokens. ([source](https://github.com/headroomlabs-ai/headroom))                                                                             | Same final answers with fewer input/output tokens; especially useful on verbose grep, logs, test failures, and large tool outputs. |

> **Headroom is the odd one out.** It is a token-*compression* layer, not a codebase-*understanding* tool. It is tested differently (Phase B): wrap another tool's output and measure token reduction at equal answer quality — never "ask Headroom about paperclip."

## 3. Repo layout and where results go

- **Tools:** `external/harness_repos/<tool>/` — plain clones, **not** submodules (consistent with the existing `headroom`).
- **Per-tool results:** `docs/research/harness/results/<tool>/` — `capabilities.md` (Phase A) + `exploitation.md` (Phase B) + small artifacts.
- **Large / raw artifacts** (packed digests, `graph.json`, logs): `scratchpad/harness/<tool>/` (gitignored); link them from `exploitation.md`.
- **Final synthesis:** `docs/research/harness/findings.md` (Phase C).

## 4. Setup — clone and wiring

Clone each missing tool into `external/harness_repos/`. Exact build/run commands are confirmed per-tool in Phase A — read each README first, do not assume.

| Tool                | Clone (run inside `external/harness_repos/`)                                     | Consumed as                                                         |
| ------------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Serena              | `git clone https://github.com/oraios/serena serena`                              | MCP server (Python / uv)                                            |
| ast-grep            | `git clone https://github.com/ast-grep/ast-grep ast-grep`                        | CLI `ast-grep`/`sg` (install binary separately; repo for reference) |
| CodeGraph           | `git clone https://github.com/colbymchenry/codegraph codegraph`                  | MCP server (Claude Code)                                            |
| Codebase-Memory MCP | `git clone https://github.com/DeusData/codebase-memory-mcp codebase-memory-mcp`  | MCP server (static binary)                                          |
| Repomix             | `git clone https://github.com/yamadashy/repomix repomix`                         | CLI `npx repomix` (repo for reference)                              |
| Understand-Anything | `git clone https://github.com/Egonex-AI/Understand-Anything understand-anything` | App/CLI → interactive graph                                         |
| Graphify            | `git clone https://github.com/safishamsi/graphify graphify`                      | Coding-assistant skill                                              |
| Headroom            | _already cloned_                                                                 | Library / proxy / MCP                                               |

## 5. Phase A — Capability discovery (per tool)

For each tool, read its repo in `external/harness_repos/<tool>/` (README, docs, `--help`, examples) and write `results/<tool>/capabilities.md` answering:

- **Domain & sweet spot** — what class of question is this tool *built* to answer?
- **Capabilities** — concrete, named operations (e.g. find references, structural rewrite, impact/blast-radius query, pack + token-count, compress tool output).
- **Inputs / outputs** — what it ingests, what artifacts it emits.
- **Invocation** — exact, verified commands or MCP wiring to run it against paperclip.
- **Claimed wins** — vendor claims worth checking (e.g. "10× fewer tokens").
- **Limits** — languages, repo-size ceilings, setup friction, known gaps.

Output: one **capability card** per tool. This is what makes Phases B and C possible.

## 6. Phase B — Full exploitation against paperclip (per tool)

Drive each tool to the *full* extent of its capabilities on paperclip and record everything in `results/<tool>/exploitation.md`:

- **Run every capability** from the card against paperclip; capture the actual output/artifact.
- **Understanding tools:** answer the standing paperclip questions the tool is meant to answer — architecture map, entrypoints, "what depends on X", "blast radius of changing Y", "read-these-first onboarding".
- **Headroom:** wrap a verbose operation (e.g. a Repomix digest or a large grep/log) and record tokens in/out before vs after at equal fidelity.
- **Telemetry per run:** usefulness (your judgment, with evidence), tokens, tool-calls, wall-time, setup friction, failures.

No capability is left untested; every result is stored so it can be cited in Phase C.

## 7. Phase C — Capability map and comparison

1. Build a **capability × tool matrix** from the cards (rows = capabilities, columns = tools, cells = supported? how well?).
2. Classify each capability:
   - **Unique** — only one tool does it → document the standalone result; nothing to compare.
   - **Overlapping** — a *subset* of tools do it → compare those head-to-head on that capability.
   - **Universal** — *all* tools touch it → compare across all and **establish a firm conclusion**.
3. Expect (but confirm from the matrix, do not pre-commit) comparison axes like: accurate architecture/onboarding summary, dependency/impact answers, token cost of equivalent understanding.
4. Write `findings.md`: per-tool verdict (what each is best at on paperclip) + the overlap/universal comparisons, with evidence.

## 8. Execution notes

- Run Phase A → B one tool at a time; a fresh worker per tool keeps context clean. Phase C is a single synthesis pass.
- Verify before claiming: every entry in `exploitation.md` cites the actual command/output, not a recollection.
- Beads not seeded yet (per decision). When this plan is approved, seed: one epic + one issue per tool (Phase A+B) + one synthesis issue.
