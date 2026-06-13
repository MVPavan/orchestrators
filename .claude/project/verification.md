# Verification Commands

Status: adapted for Agent Orchestrators on 2026-06-13

This repo currently has no first-party application source tree, package manifest, CI, or test suite. Verification is therefore focused on repo structure, Git/submodule integrity, Beads state, JSON/shell syntax, and documentation consistency.

Do not invent application-level test commands until first-party code exists.

## Default Checks

Use these for most documentation, harness, and policy changes:

```bash
git status --short --branch
git submodule status --recursive
jq empty .claude/settings.json
bash -n .claude/hooks/block-dangerous-commands.sh
bash -n .claude/hooks/block-generated-edits.sh
bash -n .claude/hooks/bd-prime.sh
```

## Beads Checks

Use these when Beads issues, policies, generated mirror rules, or tracker configuration changed:

```bash
bd stats
bd lint
bd export -o .beads/issues.jsonl
```

`bd preflight --check` may include toolchain-specific checks. Use it only when its checks match this repo's current stack.

## Submodule Checks

Use these when touching `.gitmodules`, `README.md` submodule instructions, or submodule pointers:

```bash
git config --file .gitmodules --get-regexp '^submodule\\..*\\.(path|url|branch)$'
git submodule status --recursive
git diff --submodule
```

If updating upstream pointers, stage only the intended submodule paths.

## Overlay Consistency Checks

Use these when editing `.claude/project/`:

```bash
rg -n "Bo[d]ha|bo[d]ha|Dhri[t]i|Dhṛ[t]i|src/bo[d]ha|docs/design/v_2_[0-9]" .claude/project
rg -n "^## \\[INV-" .claude/project/invariants.md
test -f docs/research/codex-usage-options.md
test -f docs/workstreams/README.md
```

The first command should return no matches after the overlay is fully adapted.

## Future Code Checks

When first-party code is added, update this file with the repo's real commands. Do not use generic placeholders as completion gates. The command that proves a claim must exist and must exit 0.
