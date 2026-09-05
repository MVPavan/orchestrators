# Coding Agent Submodules

## Goal

Track four upstream agent projects under `external/coding-agents/`:

- OpenAI Codex
- Pydantic AI
- LangChain Deep Agents
- Pi Coding Agent

## Scope

- Add each official repository to `.gitmodules` on its default branch.
- Clone each repository as a Git submodule.
- Initialize any nested submodules recursively.
- Confirm `external/sync-submodules.sh` recognizes the new paths.

Installing project dependencies or globally installing the agent CLIs is out of
scope; these repositories are reference source trees managed as submodules.

## Paths

- Modify: `.gitmodules`
- Create gitlinks:
  - `external/coding-agents/codex`
  - `external/coding-agents/pydantic-ai`
  - `external/coding-agents/deepagents`
  - `external/coding-agents/pi`

## Risks And Invariants

- Use current canonical upstream URLs, not forks or obsolete redirects.
- Keep the submodule updater checkout-only: no merges, rebases, commits, or
  pushes in upstream repositories.
- Do not update unrelated existing submodule pointers.
- Preserve any upstream nested-submodule topology via recursive initialization.

## Verification

1. Check `.gitmodules` path, URL, and branch entries.
2. Check all four parent index entries are mode `160000`.
3. Run `git submodule update --init --recursive` for the four paths.
4. Run `external/test-sync-submodules.sh`.
5. Run a targeted `external/sync-submodules.sh --dry-run` for the four paths.
6. Inspect recursive submodule status, parent diff, and working-tree status.
