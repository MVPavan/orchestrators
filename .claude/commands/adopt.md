---
description: Adopt this reusable Claude setup to the current repository by refreshing only the project overlay files.
---

# Adopt This Setup

Use this after the setup has been copied into a target repository root.

## Goal

Keep the core harness stable. Update only `.claude/project/*` with facts derived from the current repo.

## Workflow

1. Read:
   - `AGENTS.md`
   - `adopt.md`
   - `.claude/project/*.md`
2. Scan the target repo in this order:
   - root instruction files
   - README and design docs
   - manifests, lock files, CI, and test config
   - relevant source and test directories
3. Use this authority order:
   - repo reality
   - current config and CI
   - maintained docs
   - older docs
   - explicit assumptions
4. Verify claims against the actual repo when possible.
5. Update only:
   - `.claude/project/brief.md`
   - `.claude/project/repo-map.md`
   - `.claude/project/verification.md`
   - `.claude/project/invariants.md`
   - `.claude/project/docs-index.md`
   - `.claude/project/tools.md`
   - `.claude/project/tracking.md`
   - `.claude/project/learnings.md`
   - `.claude/project/adoption-report.md`
6. Use repo-relative paths only.
7. If running in Claude Code with Codex available and the adoption work is `standard` or `deep`, ask Codex to challenge major assumptions before finalizing.
8. Stop and present the adoption report for review.

## Rules

- Do not rewrite core rules, agents, commands, or skills unless the user asks.
- Do not copy unverifiable design-doc claims into project facts.
- Do not invent verification commands. If local commands are unclear, say so in `verification.md` and
  keep the completion gate structural until real code, manifests, or CI exist.
- If the repo has a language-specific stack, document the observed commands and any mismatch with
  `.claude/rules/` in the adoption report.
