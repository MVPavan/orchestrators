# Codebase Analysis — Tooling Experiments

**Goal.** Use the codebase-analysis tools below as independent *lenses* to understand the **paperclip** repo (`external/paperclip`) as deeply as possible, then compare them — but only where their capabilities genuinely overlap. This file is the **executable runbook**: a goal runner can drive it phase by phase after a context compaction.

## 0. How this runs (orchestration contract)

- **Main thread = orchestrator only.** It scopes work, curates context, fans out subagents, reviews, and synthesizes. It does **not** do the heavy reading/analysis itself.
- **Executors = Opus 4.8 subagents**, launched via the Workflow harness `agent({ model: 'opus', effort })`, **one tool per worker**, run in **parallel**.
- **Critic = Codex `gpt-5.5`**, via `external/codex-adapter/scripts/codex-run.mjs -m gpt-5.5 -e <effort>` (canonical per the `use-codex` skill; read-only sandbox, parallel-safe). At every judgment point, hand Codex an **unbiased, self-contained** prompt (no leading conclusion) and **iterate Opus ↔ Codex until satisfied**.
- **Plumbing verified 2026-06-22:** Opus and Codex both spawn and run at `medium` / `high` / `xhigh`.
- **Effort is set by §3's map**, not a flat default.

**Method (capability-first, not a uniform benchmark).** These tools do not solve the same problem; comparison is an *output* of capability discovery, not a rubric imposed up front:

1. **Characterize** each tool — what it is actually capable of, and where it is strong.
2. **Exploit** each tool to the *full* extent of those capabilities against paperclip; store the results.
3. **Repeat** for every tool.
4. **Compare overlaps** — where a capability is shared by a *subset* of tools, compare those head-to-head.
5. **Establish universals** — where a capability is common to *all* tools, compare and draw a firm conclusion.

## 1. Subject under test — paperclip

- **Path:** `external/paperclip`  ·  **Origin:** `github.com/paperclipai/paperclip`
- **What it is:** "the app people use to manage AI agents for work."
- **Stack & size (verified):** TypeScript/TSX **pnpm monorepo** — ~3,071 tracked files (1,674 `.ts`, 488 `.tsx`, 311 `.md`, 192 `.json`, 110 `.sql`); workspaces include `packages/`, `server`, `ui`, `cli`, `evals`.
- **Why it is a good subject:** large, multi-package, multi-language — a realistic stress test that punishes shallow file-by-file exploration.

## 2. Isolation rules (MANDATORY)

Each tool runs as an **isolated experiment scoped to paperclip source only**. A tool left to its defaults will happily ingest the entire working tree, the other tool repos, and binaries — that is **not** what we want.

- **Target = paperclip source only.** Point every tool explicitly at `external/paperclip` (or a named subset of it). Never run a tool with `cwd` = the `orchestrators` repo root — it would pull in everything.
- **Never ingest:** the parent `orchestrators` repo; `external/harness_repos/**` (the tool repos and their binaries); the Codex CLI binary (`~/.local/bin/codex`); any tool's own binary; `.git/`; `node_modules/`; build output (`dist/`, `build/`, `.next/`, `coverage/`); the pnpm store; large binary assets (`*.png`, `*.jpg`, `*.svg`, fonts); oversized lockfiles.
- **Output isolation:** each tool writes its index/artifacts **only** to `scratchpad/harness/<tool>/`. If a tool insists on writing into its target, run it against a throwaway copy at `scratchpad/harness/<tool>/paperclip/`, never against `external/paperclip` directly.
- **One tool per subagent**, no shared working directories. Codex stays in its default read-only sandbox.
- **No silent truncation:** if a tool cannot handle full paperclip source, scope to representative packages and **log exactly what was excluded** in that tool's `exploitation.md`.

Suggested exclude globs (adapt per tool's ignore syntax):

```text
.git/  node_modules/  dist/  build/  .next/  coverage/  .turbo/
**/*.png  **/*.jpg  **/*.jpeg  **/*.svg  **/*.ico  **/*.woff*  **/*.mp4
pnpm-lock.yaml  **/*.min.js  **/*.map
```

## 3. Effort map (approved)

| Task / phase                                                                    | Nature                                            | Opus                       | Codex 2nd opinion                                           | Rationale                                                     |
| ------------------------------------------------------------------------------- | ------------------------------------------------- | -------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------- |
| Setup — clone/install/wire tools                                                | Mechanical (Bash)                                 | orchestrator (no subagent) | —                                                           | Deterministic; no reasoning to spend effort on                |
| Phase A — capability discovery                                                  | Read repo/docs, extract capability card           | **medium**                 | Codex **medium** on the best-at / claim-credibility verdict | Mostly reading; only the verdict is judgment                  |
| Phase B — ast-grep, Repomix                                                     | Run CLI, capture output + telemetry               | **medium**                 | optional                                                    | Deterministic invocation, little judgment                     |
| Phase B — Headroom                                                              | Wrap an output, measure token delta               | **medium**                 | —                                                           | Pure measurement                                              |
| Phase B — Serena, CodeGraph, Codebase-Memory MCP, Understand-Anything, Graphify | Setup + drive + judge answer quality on paperclip | **high**                   | Codex **medium** if a result is ambiguous                   | MCP/binary setup + judging answer accuracy                    |
| Phase C — matrix, classify, conclusions                                         | Cross-tool synthesis & judgment                   | **xhigh**                  | Codex **high → xhigh**, iterate until agreement             | Hardest reasoning; firm conclusions need an adversarial check |

## 4. Tools under test (the lenses)

Each tool lives in `external/harness_repos/<tool>/`. **Status:** only `headroom` is cloned so far; the other seven still need cloning (see §6, Phase 0).

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

## 5. Repo layout and where results go

- **Tools:** `external/harness_repos/<tool>/` — plain clones, **not** submodules (consistent with the existing `headroom`).
- **Per-tool results:** `docs/research/harness/results/<tool>/` — `capabilities.md` (Phase A) + `exploitation.md` (Phase B) + small artifacts.
- **Large / raw artifacts** (packed digests, `graph.json`, logs) and any throwaway paperclip copies: `scratchpad/harness/<tool>/` (gitignored); link them from `exploitation.md`.
- **Final synthesis:** `docs/research/harness/findings.md` (Phase C).

## 6. Phase 0 — Setup (orchestrator, Bash)

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

**Also:** create `scratchpad/harness/` and define the exclude list from §2.
**Done when:** all 7 tool dirs exist under `external/harness_repos/`; `scratchpad/harness/` exists; the exclude list is written down; one tool runs once against the scoped target without error.

## 7. Phase A — Capability discovery (Opus **medium** ×7, parallel)

For each tool, an Opus-medium worker reads its repo in `external/harness_repos/<tool>/` (README, docs, `--help`, examples) and writes `results/<tool>/capabilities.md`:

- **Domain & sweet spot** — what class of question is this tool *built* to answer?
- **Capabilities** — concrete, named operations.
- **Inputs / outputs** — what it ingests, what artifacts it emits.
- **Invocation** — exact, verified commands or MCP wiring to run it against the **scoped** paperclip target (§2).
- **Claimed wins** — vendor claims worth checking (e.g. "10× fewer tokens").
- **Limits** — languages, repo-size ceilings, setup friction, known gaps.

**Codex (medium):** unbiased second opinion on the "what is this tool actually best at, and is the vendor claim credible?" verdict; iterate until the orchestrator is satisfied.
**Done when:** 7 capability cards exist, each with a Codex-reviewed verdict.

## 8. Phase B — Full exploitation against paperclip (effort per §3, parallel)

Each worker drives its tool to the *full* extent of its capabilities against the **scoped, isolated** paperclip target and records everything in `results/<tool>/exploitation.md`:

- **Run every capability** from the card; capture the actual output/artifact (to `scratchpad/harness/<tool>/`).
- **Understanding tools:** answer the standing paperclip questions the tool is meant to answer — architecture map, entrypoints, "what depends on X", "blast radius of changing Y", "read-these-first onboarding".
- **Headroom:** wrap a verbose operation (e.g. a Repomix digest or a large grep/log) and record tokens in/out before vs after at equal fidelity.
- **Telemetry per run:** usefulness (judgment, with evidence), tokens, tool-calls, wall-time, setup friction, failures.
- **Honor §2 isolation on every invocation.**

**Done when:** every capability is exercised and its result + telemetry recorded; isolation respected (no whole-tree / binary ingestion).

## 9. Phase C — Capability map and comparison (Opus **xhigh**)

1. Build a **capability × tool matrix** from the cards (rows = capabilities, columns = tools, cells = supported? how well?).
2. Classify each capability:
   - **Unique** — only one tool does it → document the standalone result; nothing to compare.
   - **Overlapping** — a *subset* of tools do it → compare those head-to-head on that capability.
   - **Universal** — *all* tools touch it → compare across all and **establish a firm conclusion**.
3. Compare only along overlapping and universal axes (confirm them from the matrix; do not pre-commit).
4. Write `findings.md`: per-tool verdict (what each is best at on paperclip) + the overlap/universal comparisons, with evidence.

**Codex (high → xhigh):** adversarial review of the overlap/universal conclusions; iterate Opus ↔ Codex until agreement.
**Done when:** matrix complete; every conclusion has evidence and a Codex sign-off.

## 10. Execution order for the goal runner

1. Run **Phase 0** (orchestrator). Gate on its Done-when.
2. Run **Phase A**: fan out 7 Opus-medium workers in parallel (one per tool); insert the Codex-medium verdict review; gate on Done-when.
3. Run **Phase B**: fan out one worker per tool at the effort from §3; Headroom last (it wraps another tool's output); gate on Done-when.
4. Run **Phase C**: single Opus-xhigh synthesis pass + Codex high→xhigh review; gate on Done-when.
5. Beads not seeded yet (per decision). Seed only if the user asks: one epic + one issue per tool (A+B) + one synthesis issue.

Throughout: the main thread orchestrates and reviews; it does not do the per-tool reading/analysis itself.
