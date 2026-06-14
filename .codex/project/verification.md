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
bash -n .codex/hooks/block-dangerous-commands.sh
bash -n .codex/hooks/bd-prime.sh
jq empty .codex/hooks.json
python3 -c "import py_compile; py_compile.compile('.codex/hooks/block-generated-edits.py', cfile='/tmp/block-generated-edits.pyc', doraise=True)"
python3 -c "import tomllib; tomllib.load(open('.codex/config.toml','rb'))"
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

Use these when editing `.codex/project/`:

```bash
rg -n "Bo[d]ha|bo[d]ha|Dhri[t]i|Dhṛ[t]i|src/bo[d]ha|docs/design/v_2_[0-9]" .codex/project
rg -n "^## \\[INV-" .codex/project/invariants.md
test -f docs/research/codex-usage-options.md
test -f docs/workstreams/README.md
test -f .codex/skills/use-codex/SKILL.md
test -f .codex/agents/planner.toml
```

The first command should return no matches after the overlay is fully adapted.

## Future Code Checks

When first-party code is added, update this file with the repo's real commands. Do not use generic placeholders as completion gates. The command that proves a claim must exist and must exit 0.
