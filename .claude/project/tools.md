# Tools And Runtimes

Routing guidance for this repo. Current project facts live in `.claude/project/`; deeper tool research lives in `docs/research/`.

## Beads

- **When:** durable tasks, blockers, follow-ups, workstream phases, multi-session handoff.
- **How:** use `bd`; policy lives in `.beads/beads.md`.
- **Mirror:** refresh `.beads/issues.jsonl` after issue changes that should be preserved in git.
- **Authority:** no commits, pushes, `bd dolt push`, or `bd dolt pull` unless explicitly asked or an active workflow grants that authority.

## Codex

- **Current research:** `docs/research/codex-usage-options.md` is the current project research note.
- **Default project direction:** prefer repo-native `codex exec`, `codex exec resume`, and `codex review` wrappers for automation.
- **Cloud work:** use `codex cloud` for offloaded branch/PR-style work after a Codex cloud environment is configured.
- **Cross-agent bridge:** consider `codex mcp-server` or the Codex SDK when Gemini or another runtime needs Codex as a callable tool.
- **Claude plugin:** the `codex-adapter` plugin is the supported Claude Code integration — it wraps `codex exec` with roles, concurrency, and no broker. Install from the marketplace (`MVPavan/codex-adapter`); invocation rules in `.claude/commands/use-codex.md`. (The old `openai-codex` broker plugin is retired.)
- **Raw app-server:** treat `codex app-server` as experimental and isolate/version-pin any direct integration.

## Claude Code

- **Harness:** `.claude/agents`, `.claude/commands`, `.claude/skills`, `.claude/hooks`, and `.claude/rules`.
- **Project overlay:** `.claude/project/` is the source of repo-specific facts.
- **Caution:** some copied skills and docs are still legacy or source-project-specific. Check `.claude/project/docs-index.md` before treating them as current policy.

## Gemini CLI

- Gemini CLI is a target peer runtime for this orchestration repo, but no project-native Gemini wrapper exists yet.
- Prefer direct, explicit commands until a wrapper or MCP profile is created.
- If using Codex from Gemini, the likely first integration path is MCP via `codex mcp-server`.

## Docs Research

- For current library, SDK, CLI, API, cloud, or model-provider behavior, use official/reference docs instead of guessing.
- In Claude Code, use the `docs-researcher` subagent when available for narrow documentation lookup.
- Use brainstorming, not docs-researcher, for open-ended project research, tradeoff analysis, and requirements decisions.
- For OpenAI/Codex behavior, prefer current official docs and the local research note in `docs/research/codex-usage-options.md`.

## External Repos

- `external/gascity` and `external/gastown` are upstream submodules.
- Inspect them when evaluating orchestration patterns or syncing upstreams.
- Do not modify their internals from the parent repo unless the task is explicitly submodule-local.

## HTML Artifacts

- Use the `html-artifact` skill only when the user asks for HTML, or when the output is purely for human reading and richer structure clearly helps.
- Do not use it for README files, agent prompts, harness docs, or content meant for another agent.
