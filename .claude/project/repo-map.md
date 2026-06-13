# Repo Map

Physical layout and navigation for the parent repo.

## Top Level

| Path | What |
| --- | --- |
| `README.md` | Public description and submodule sync commands |
| `AGENTS.md` | Main agent operating guide |
| `CLAUDE.md` | Claude Code pointer to `AGENTS.md` |
| `.gitmodules` | Submodule configuration for upstream projects |
| `.gitignore` | Local runtime, cache, env, and Beads ignore rules |
| `RESEARCH/` | Research notes and integration analysis |
| `.beads/` | Beads issue tracker state, policy, and git-reviewable mirror |
| `.claude/` | Claude Code harness: agents, commands, hooks, rules, skills, and project overlay |
| `.agents/` | Placeholder for cross-agent configuration |
| `.codex/` | Placeholder for Codex-specific repo configuration |
| `external/` | Git submodules for upstream projects |

## External Upstreams

| Path | Role |
| --- | --- |
| `external/gascity` | Upstream submodule from `gastownhall/gascity`, branch `main` |
| `external/gastown` | Upstream submodule from `gastownhall/gastown`, branch `main` |

The parent repo tracks only the submodule commit pointers. If a task is about parent orchestration, avoid editing inside `external/*`. If a task is about updating upstream pointers, use `git submodule update --remote --merge ...` and stage the submodule path only.

## Claude Harness

| Path | Role |
| --- | --- |
| `.claude/agents/` | Local Claude subagent definitions |
| `.claude/commands/` | Slash-command workflows copied from the reusable harness |
| `.claude/hooks/` | Safety hooks and Beads session startup hook |
| `.claude/rules/` | General operating rules |
| `.claude/skills/` | Reusable skills; some are generic, some still need adaptation |
| `.claude/project/` | Current repo-specific facts. Prefer this over inherited harness docs. |
| `.claude/docs/` | Background/reference docs; some are historical and need review before adoption |

## Current Research

| Path | Role |
| --- | --- |
| `RESEARCH/codex-usage-options.md` | Current Codex integration comparison and recommendation |

## Missing First-Party Runtime Areas

These paths do not exist yet in the parent repo:

- `src/`
- `tests/`
- `docs/`
- `scripts/`
- CI configuration

Do not assume Python, Node, Go, Docker, or test commands until the repo adds first-party code or manifests.

## How To Orient On A Task

1. Read `README.md` for the parent repo purpose and submodule model.
2. Read `.claude/project/brief.md` for current constraints.
3. Read `.claude/project/docs-index.md` to find the relevant durable docs.
4. For work tracking, read `.beads/beads.md` and use `bd`.
5. For Codex decisions, read `RESEARCH/codex-usage-options.md`.
6. For upstream-specific work, enter the relevant `external/*` submodule and read its own docs.
