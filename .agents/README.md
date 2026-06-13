# .agents

Placeholder directory. The real per-agent configuration lives in [.claude/](../.claude/).

This directory exists because some sandboxed agent runtimes (notably Codex) fail
to traverse a symlink-to-directory at the repo root during sandbox setup.
Previously `.agents` was a symlink to `.claude/`; that symlink was replaced with
a real directory + this README on 2026-06-04 so Codex's sandbox can initialize.

No code in this repo reads files under `.agents/<...>`; all per-agent rules,
skills, plugins, and configuration are read directly from `.claude/<...>`.
This directory should remain empty apart from this README.

If you need agent configuration, look in:

- [`.claude/agents/`](../.claude/agents/) — per-subagent definitions
- [`.claude/commands/`](../.claude/commands/) — slash commands
- [`.claude/rules/`](../.claude/rules/) — repo invariants and style rules
- [`.claude/project/`](../.claude/project/) — repo-specific project facts
- [`.claude/skills/`](../.claude/skills/) — skills
- [`AGENTS.md`](../AGENTS.md) — top-level agent operating guide
