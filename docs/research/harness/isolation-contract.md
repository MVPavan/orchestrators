# Isolation Contract — codebase-analysis harness experiment

**Authoritative.** Every tool worker (Phase A and Phase B) is handed this file. The orchestrator
enforces it. Violating it invalidates that tool's results. Docker/containers are **unavailable** on
this host (WSL integration off, no `cargo`/`go`), so isolation is enforced by **filesystem +
environment + visibility** discipline, not by sandboxing.

## Why this exists (the three things that must NOT happen)

1. **Result bleed** — one tool's output (index, graph, digest, answer) must never be an input to
   another tool's experiment.
2. **Install bleed** — installing a tool for experiment X must never make that tool available to the
   worker running experiment Y. No global installs; if worker Y can run tool X just by typing its
   name, isolation has failed.
3. **Subject mutation** — no tool may write into the canonical paperclip source or the real
   `external/paperclip` submodule.

## Planes of isolation

### A. Filesystem
| Purpose | Path | Rule |
| --- | --- | --- |
| Tool code | `external/harness_repos/<tool>/` | Read the repo here; do not edit it. |
| Tool runtime env | `external/harness_repos/<tool>/` (its own `venv`/`node_modules`) | Installs land **here only**. |
| Canonical subject (read-only) | `scratchpad/harness/_paperclip_src/` | `chmod a-w`. Read-only tools may point here. **Never written.** |
| Per-tool writable subject copy | `scratchpad/harness/<tool>/paperclip-src/` | Indexing/mutating tools get their **own** copy. |
| Tool artifacts/index/logs | `scratchpad/harness/<tool>/` | All scratch output lands here (gitignored). |
| Tool results (committed) | `docs/research/harness/results/<tool>/` | `capabilities.md`, `exploitation.md`, small artifacts. |

The canonical subject (`_paperclip_src`) is the **controlled variable** — sharing it read-only across
tools is correct (it is the subject, not a result). Sharing any *result* is forbidden.

### B. Environment / install (the install-bleed rule)
- **NO global installs.** Forbidden: `npm i -g` / `npm install -g`, `pnpm add -g`, `uv tool install`,
  `pipx install`, `pip install --user`, `cargo install`, `brew install`, or anything that writes to a
  shared `PATH` location (`~/.local/bin`, npm global prefix, `~/.cargo/bin`, `/usr/local/bin`).
- **Install locally, invoke by explicit path:**
  - Node tools → `npm install <pkg>` (or `pnpm install`) **inside the tool dir**; invoke via
    `external/harness_repos/<tool>/node_modules/.bin/<bin>` or `node <path>`. Never bare `npx <pkg>`
    against a global, never a bare tool name.
  - Python tools → a tool-local `uv venv` inside the tool dir; invoke via `uv run --project <tool dir>`
    or that venv's `bin/`. uv's shared **download cache** (`~/.cache/uv`) is allowed (a content-addressed
    package cache does not put any tool on another worker's `PATH`).
  - Binary tools (ast-grep) → install the prebuilt binary **into the tool dir** (e.g. local npm
    `@ast-grep/cli`) and call it by full path. **Never** call bare `sg` — on this host `/usr/bin/sg` is
    the unrelated *switch-group* command, not ast-grep.
- A worker must invoke **only its own tool**, always by explicit path. It must not rely on, or call,
  anything another worker installed.

### C. Visibility / input
- A worker is told **only** about its own tool's paths. It must not read another tool's
  `results/<other>/` or `external/harness_repos/<other>/`, and must not consume another tool's artifacts.
- Only the **orchestrator** reads across tools, and only in Phase C synthesis.

## Subject-scoping (never ingest the whole tree)
Point the tool at the scoped subject only. Never run with `cwd` = the `orchestrators` repo root.
Never ingest: the parent repo; `external/harness_repos/**`; the Codex CLI binary; any tool binary;
`.git/`; `node_modules/`; build output (`dist/ build/ .next/ coverage/ .turbo/`); the pnpm store;
binary assets; oversized lockfiles. Exclude globs:

```text
.git/  node_modules/  dist/  build/  .next/  coverage/  .turbo/
**/*.png  **/*.jpg  **/*.jpeg  **/*.svg  **/*.ico  **/*.woff*  **/*.mp4
pnpm-lock.yaml  **/*.min.js  **/*.map
```

The canonical `_paperclip_src` snapshot is **already** pruned of binaries and the lockfile, so pointing
a tool at it satisfies most of the above; still apply the tool's own ignore syntax for `node_modules`/
build output if the tool would otherwise create them.

## No silent truncation
If a tool cannot handle full paperclip source, scope it to representative packages and **log exactly
what was excluded and why** in that tool's `exploitation.md`. Never quietly analyze a subset and report
it as the whole.

## Per-worker preflight (must pass before real work)
1. Confirm `cwd` is the scoped subject or the tool dir — never the repo root.
2. Confirm the tool resolves to a **local** path under `external/harness_repos/<tool>/` (run
   `command -v` / `which` and assert it is **not** a global bin).
3. Confirm the subject is `_paperclip_src` (read-only tools) or this tool's own `paperclip-src/` copy.
4. On exit, confirm nothing was written under `external/paperclip/` or `_paperclip_src/`.

## Phase B runtime hardening (from the Codex audit, 2026-06-22)
Codex's review found several tools write into the shared home dir or phone home by default. Every
Phase B worker MUST, before running its tool:

- **Tool-local HOME.** `export HOME=<repo>/scratchpad/harness/<tool>/home` (mkdir -p first). This
  contains ALL `~/.*` writes inside the tool's own sandbox: `~/.serena`, `~/.solidlsp`,
  `~/.understand-anything`, `~/.cache/codebase-memory-mcp`, `~/.cache/graphify-queries.log`, and
  npm/uv/pnpm caches. PATH-resolved binaries (node, uv, gcc) use absolute paths and keep working.
- **Kill telemetry / phone-home / update checks / query logs:** codegraph `CODEGRAPH_TELEMETRY=0`;
  codebase-memory-mcp `CBM_CACHE_DIR=<repo>/scratchpad/harness/codebase-memory-mcp/cbm-cache` + pass an
  explicit `project`/`repo_path`; graphify disable query logging (flag/env, else it writes
  `~/.cache/graphify-queries.log` — the tool-local HOME also catches it); headroom telemetry + update
  check off.
- **NEVER run** (these mutate shared/global state or other agents): any `install.sh` / `local-install.sh`
  / `curl | bash` / `npm i -g` / `uv tool install` / agent-config or MCP-config installers that edit
  shared files; `headroom learn` (rewrites `AGENTS.md`/`CLAUDE.md`); headroom `proxy` / `wrap`
  (intercepts other agents); understand-anything `/plugin` or global install.
- **Write targets:** indexing tools write into their OWN writable subject copy
  (`scratchpad/harness/<tool>/paperclip-src/` — serena, codegraph, graphify) or an external cache dir
  (codebase-memory-mcp). Read-only tools (ast-grep, repomix, understand-anything scan, headroom's
  inputs) point at the read-only canonical `_paperclip_src`.
- **Post-run assertions:** `_paperclip_src` still read-only and byte-identical; no new global PATH
  binary; the REAL `$HOME` gained no tool artifacts from this run.
