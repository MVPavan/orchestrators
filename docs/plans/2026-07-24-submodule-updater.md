# Guarded External Submodule Updater

## Goal

Provide `external/sync-submodules.sh` to advance configured `external/` Git
submodules to their configured upstream branches without merging, forcing,
staging, committing, or pushing.

## Scope

- Discover paths, URLs, and branches from `.gitmodules`.
- Accept either all configured `external/` paths or explicitly named paths.
- Preflight every selected path before any update; refuse uninitialized, dirty,
  missing-branch, or non-`external/` paths.
- Fetch `origin` and check out the configured remote-tracking commit directly.
- Print the resulting Gitlink-only parent-repository diff for the selected paths.
- Provide `--dry-run` and a local fixture test.

## Non-goals

- No merge or rebase.
- No force checkout/reset.
- No `git add`, commit, or push.
- No partial run: if any selected submodule fails preflight, update none of them.

## Execution

1. Add a failing fixture test that creates an isolated parent/submodule setup
   and asserts dry-run/update/dirty safeguards through the script interface.
2. Implement the smallest Bash script needed to pass the fixture.
3. Run Bash syntax validation, the fixture test, submodule metadata checks,
   and `git status`.

## Risk and verification

The updater changes checked-out submodule commits. Its preflight must reject
dirty or uninitialized paths, and the successful path must use a direct
checkout of the fetched `origin/<branch>` commit after an explicit fetch of
that branch. The test must prove no parent staging occurs, that a preflight
failure makes no changes to any selected submodule, and that the printed diff
is a Gitlink pointer diff.
