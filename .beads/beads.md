# Beads Issue Tracker - Policy

This project uses **bd (Beads)** for durable issue tracking. The command reference and live
session-close protocol come from `bd prime`; this file holds the repo-specific policy that
`bd prime` does not own.

## Repo-Specific Rules

- **Durable work items.** Use Beads for tasks, bugs, features, epics, dependencies, blockers,
  follow-ups, and any work that must survive a reset, compaction, handoff, or multi-agent run.
- **In-turn checklists.** Short execution checklists for the current turn stay outside Beads.
  One Beads issue should represent one durable unit of work, not every local step.
- **Durable knowledge.** This repo does not yet have a separate project knowledge store. Use
  `bd remember` / `bd memories` only for durable cross-session facts or decisions, not for task
  tracking. If this repo later adopts a dedicated knowledge store, update this policy and keep
  Beads focused on work items.
- **Actor attribution.** Every mutating Beads command should include an actor tag when practical:
  `--actor "<runtime>:<session-or-purpose>"`. Examples: `codex:setup`, `cc:<session>`,
  `gemini:<session>`. The goal is attributable changes across agent runtimes.
- **Conservative git authority.** Use Beads for tracking, but do not run git commits, pushes,
  `bd dolt push`, or `bd dolt pull` unless the user explicitly asks or an active workflow grants
  that authority. At handoff, report changed files, validation, and proposed commands.
- **Source of truth and durability.** The local Dolt database under `.beads/` is the source of
  truth. `.beads/issues.jsonl` is a committed plaintext mirror for git-native review and recovery.
  Auto-export is best-effort; refresh it explicitly with `bd export -o .beads/issues.jsonl` after
  issue changes that should be preserved in git.
- **Remote sync.** Cross-machine operational sync uses the configured Dolt remote:
  `bd dolt push` / `bd dolt pull`. Treat that as a separate sync action from normal git commits.
- **Hygiene cadence.** Use `bd stats`, `bd lint`, `bd stale`, `bd orphans`, and
  `bd preflight --check` when useful. Do not assume `bd doctor` is a complete health gate in
  embedded mode.

## Ideas And Backlog

Use two deferred labels for parked work:

- **`idea`** means raw and untriaged:
  `bd create "idea in one line" -l idea --defer 2099-01-01 -q --actor "<actor>"`.
- **`backlog`** means accepted but not now:
  `bd create "work item" -l backlog -t <type> -p <prio> --defer 2099-01-01 -q --actor "<actor>"`.

Labels are case-sensitive. Use lowercase kebab-case labels.

## Epics And Specs

Before creating an epic, check whether it has a spec, plan, or design document. If yes, attach it
with `--spec-id <path>`. If no such document exists, an epic without `--spec-id` is acceptable, but
the reason should be clear from the issue description.

Keep child tasks as flat as practical. Add dependencies only when work genuinely depends on another
issue's output; do not chain tasks only because they appear in sequence.

## Session Close

Before reporting completion:

1. Close any completed Beads issues with evidence in `--reason`.
2. Run relevant quality gates.
3. If Beads issues changed, refresh `.beads/issues.jsonl`.
4. Run `git status`.
5. Report the handoff and avoid commits/pushes unless explicitly authorized.
