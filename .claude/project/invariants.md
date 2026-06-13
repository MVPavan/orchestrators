# Mechanically Checkable Invariants

Status: adapted for Agent Orchestrators on 2026-06-13

These invariants describe the repo as it exists now. Update them when the project adds first-party code, a workstream renderer, CI, or additional external repositories.

## [INV-01] External Upstreams Are Git Submodules

- Statement: `gascity` and `gastown` are tracked as submodules under `external/`, both on `main`.
- Check: `git config --file .gitmodules --get-regexp '^submodule\\.(gascity|gastown)\\.(path|url|branch)$'`
- Must return: path, URL, and branch entries for both submodules.
- Why it matters: the parent repo should track upstream pointers, not vendor entire upstream internals.

## [INV-02] README Documents Submodule Clone And Sync

- Statement: `README.md` explains recursive clone/init and upstream sync commands.
- Check: `rg -n "git clone --recurse-submodules|git submodule update --init --recursive|git submodule update --remote --merge" README.md`
- Must return: all three command patterns.
- Why it matters: contributors need a stable way to hydrate and update upstream projects.

## [INV-03] Beads Has A Durable Mirror

- Statement: Beads exports to `.beads/issues.jsonl` and does not auto-stage it.
- Check: `rg -n "export\\.auto: true|export\\.path: \"issues.jsonl\"|export\\.git-add: false" .beads/config.yaml`
- Must return: all three settings.
- Why it matters: issue state must be reviewable in git without giving Beads authority to stage files automatically.

## [INV-04] Beads Policy Defines Generated Workstream Mirrors

- Statement: generated workstream mirrors are listed in `.beads/beads.md`.
- Check: `rg -n "docs/workstreams/status.md|docs/workstreams/\\*/tracking/\\*\\.md|Update Beads first" .beads/beads.md`
- Must return: matching policy lines.
- Why it matters: once workstream docs are created, agents must not hand-edit generated tracker views.

## [INV-05] Claude Safety Hooks Are Wired

- Statement: Claude PreToolUse hooks block dangerous shell commands and hand-edits to generated mirrors.
- Check: `jq -e '.hooks.PreToolUse[] | select(.matcher=="Bash")' .claude/settings.json >/dev/null && jq -e '.hooks.PreToolUse[] | select(.matcher=="Write|Edit")' .claude/settings.json >/dev/null`
- Must return: exit 0.
- Why it matters: the harness should enforce the local safety rules it documents.

## [INV-06] Project Overlay Has No Source-Project Leakage

- Statement: `.claude/project/` should not contain copied source-project facts.
- Check: `! rg -n "Bo[d]ha|bo[d]ha|Dhri[t]i|Dhṛ[t]i|src/bo[d]ha|docs/design/v_2_[0-9]" .claude/project`
- Must return: exit 0.
- Why it matters: reusable harness files can remain generic, but project overlay facts must describe this repo.

## [INV-07] Codex Research Note Exists

- Statement: Codex integration research is recorded under `RESEARCH/`.
- Check: `test -f RESEARCH/codex-usage-options.md && rg -n "codex exec|codex cloud|codex mcp-server|Claude Code Codex Plugin" RESEARCH/codex-usage-options.md`
- Must return: exit 0 and matching lines.
- Why it matters: Codex adoption decisions should be durable and reviewable, not only chat context.

## [INV-08] Parent Repo Has No First-Party Source Tree Yet

- Statement: the parent repo currently has no `src/` or `tests/`; upstream source lives in submodules.
- Check: `test ! -d src && test ! -d tests && test -d external/gascity && test -d external/gastown`
- Must return: exit 0.
- Why it matters: verification must not pretend there are application tests until first-party code exists.
