# Codex Usage Options

Date: 2026-06-13
Location: `docs/research/`

This note captures the current Codex integration options for the orchestrators repo. It compares Codex Cloud, the native Codex CLI, Codex SDK, app-server, MCP, and the installed Claude Code Codex plugin.

## Summary

Use the Claude Code Codex plugin as a convenience layer inside Claude Code, but do not make it the core orchestration substrate for this project.

Preferred project foundation:

1. `codex exec` for repo-native, scriptable Codex jobs.
2. `codex exec resume` for continuation.
3. `codex review` for read-only reviews.
4. `codex cloud ...` for offloaded cloud tasks tied to GitHub branches.
5. `codex mcp-server` or the Codex SDK when Gemini, Claude, or other agents need to call Codex as a tool.
6. Raw `codex app-server` only for richer client or bridge work, because it is experimental.

## Codex Surfaces

| Surface | Best use | Notes |
| --- | --- | --- |
| Codex Cloud / ChatGPT Codex | Remote branch work, PR-style tasks, parallel task execution | Uses cloud environments, checks out a branch/SHA, runs setup, and returns diffs, PRs, or follow-ups. |
| `codex` interactive CLI | Human-in-the-loop local coding | Good for direct local Codex sessions. |
| `codex exec` | Headless local automation | Best default primitive for repo-native orchestrator wrappers. Supports JSONL output, sandbox modes, API-key auth, and resume. |
| `codex review` | Noninteractive code review | Good for read-only review tasks from Claude, Gemini, or CI. |
| `codex cloud` | CLI access to cloud Codex tasks | Commands include `exec`, `list`, `status`, `diff`, and `apply`. Requires a configured cloud environment. |
| Codex SDK | Programmatic orchestration | Officially recommended for automation and internal tools when simple CLI wrappers are not enough. |
| `codex app-server` | Rich client protocol | JSON-RPC backend for app-like integrations. Powerful, but experimental. |
| `codex mcp-server` | Exposing Codex to MCP clients | Useful for Gemini CLI, Agents SDK, and other MCP-aware runtimes. |
| GitHub Action | CI/PR automation | Prefer this over hand-rolled API-key CLI usage inside GitHub Actions. |

## Cloud Usage

Codex Cloud runs in configured cloud environments. A task checks out the selected branch or SHA, runs setup or maintenance scripts, applies configured internet settings, reads repo instructions such as `AGENTS.md`, then produces an answer, diff, PR, or follow-up.

Useful command shapes:

```bash
codex cloud exec --env <ENV_ID> --branch <branch> "Implement X"
codex cloud list --json
codex cloud status <TASK_ID>
codex cloud diff <TASK_ID>
codex cloud apply <TASK_ID>
```

Use cloud tasks for offloaded branch work. Do not use them as the first primitive for a tight local multi-agent loop.

## Local CLI Usage

The strongest default for this repo is the local CLI.

Useful command shapes:

```bash
codex exec --sandbox read-only "Review this repo for X"
codex exec --sandbox workspace-write "Implement X"
codex exec --json --sandbox read-only "Review X"
codex exec resume --last "Continue"
codex review --uncommitted
```

Reasons to prefer this as the base layer:

- It is repo-native and easy to wrap.
- It works from Claude, Gemini, shell scripts, Beads workflows, or future orchestrator code.
- It can emit JSONL event streams.
- It has explicit sandbox and approval knobs.
- It does not bind the repo design to Claude Code plugin internals.

## Claude Code Codex Plugin

The installed plugin is `codex@openai-codex`, version `1.0.2`, from OpenAI's Claude plugin marketplace source.

Local evidence:

- `/home/pavanmv/.claude/plugins/cache/openai-codex/codex/1.0.2/.claude-plugin/plugin.json`
- `/home/pavanmv/.claude/plugins/cache/openai-codex/codex/1.0.2/scripts/codex-companion.mjs`
- `/home/pavanmv/.claude/plugins/cache/openai-codex/codex/1.0.2/scripts/lib/codex.mjs`
- `/home/pavanmv/.claude/plugins/cache/openai-codex/codex/1.0.2/hooks/hooks.json`
- `/home/pavanmv/.claude/plugins/cache/openai-codex/codex/1.0.2/skills/codex-cli-runtime/SKILL.md`

Important finding: the plugin is not just a thin wrapper around `codex exec`. It uses `codex app-server` internally, manages Claude-specific background task state, and exposes Claude slash-command workflows such as review, task, result, status, cancel, and rescue.

Good uses:

- Ad hoc Codex delegation from Claude Code.
- Claude-native review and rescue workflows.
- Background tasks with status, result, and cancel operations.
- Stop-time review gates if that behavior is desired.

Weaknesses:

- Claude-specific.
- State lives outside the repo.
- Behavior is hidden behind plugin scripts.
- It depends on `codex app-server`, which is experimental.
- It is not a good universal bridge for Gemini or other agents.

## Recommended Adoption

Adopt a layered design:

1. Keep the Claude Code Codex plugin enabled for interactive Claude workflows.
2. Build repo-native Codex conventions around `codex exec`, `codex review`, and `codex exec resume`.
3. Add a Codex MCP profile when Gemini or other MCP clients need to call Codex.
4. Use the Codex SDK only when the project needs a real programmatic controller rather than shell wrappers.
5. Use `codex cloud` for remote GitHub-backed branch work.
6. Treat raw `codex app-server` as an advanced integration path that should be version-pinned and isolated.

## Update And Maintenance

Useful commands:

```bash
codex --version
codex update
codex doctor --summary
codex cloud list --json
claude plugin details codex@openai-codex
claude plugin update codex@openai-codex
```

Local caveat from this review: `codex` is logged in with ChatGPT, but `codex doctor --summary` showed provider reachability failures under the current sandbox. The official docs fetch worked after escalation, so long-running Codex jobs should be verified from the normal shell environment before relying on them.

## Sources

- OpenAI Codex overview: https://developers.openai.com/codex
- Codex CLI reference: https://developers.openai.com/codex/cli/reference
- Noninteractive / `codex exec`: https://developers.openai.com/codex/noninteractive
- Codex app-server: https://developers.openai.com/codex/app-server
- Codex SDK: https://developers.openai.com/codex/sdk
- Codex cloud environments: https://developers.openai.com/codex/cloud/environments
