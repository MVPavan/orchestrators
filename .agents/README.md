# .agents

Placeholder directory. Active repo-local Codex configuration lives in [`.codex/`](../.codex/).

This directory exists because some sandboxed agent runtimes (notably Codex) fail
to traverse a symlink-to-directory at the repo root during sandbox setup.
Previously `.agents` was a symlink to `.claude/`; that symlink was replaced with
a real directory + this README on 2026-06-04 so Codex's sandbox can initialize.

The current local Codex CLI has been verified to load skills from `.codex/skills`.
This directory should remain empty apart from this README unless a future Codex
release or team policy requires `.agents/skills` or `.agents/plugins`.

If you need active Codex configuration, look in:

- [`.codex/agents/`](../.codex/agents/) — Codex custom agents
- [`.codex/skills/`](../.codex/skills/) — Codex skills
- [`.codex/hooks.json`](../.codex/hooks.json) and [`.codex/hooks/`](../.codex/hooks/) — lifecycle hooks
- [`.codex/rules/`](../.codex/rules/) — exec-policy rules and guidance
- [`.codex/project/`](../.codex/project/) — repo-specific project facts
- [`AGENTS.md`](../AGENTS.md) — top-level agent operating guide

Legacy Claude Code configuration remains under [`.claude/`](../.claude/) for Claude-specific runs.
