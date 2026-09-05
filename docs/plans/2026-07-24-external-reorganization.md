# External Agent-System Reorganization

## Goal

Group the six agent-system submodules under `external/agent-systems/`, and
organize the codebase-understanding tool submodules under
`external/harness-tools/`.

## Scope

- Move Gas City, Gas Town, OpenHands, Paperclip, Puppetmaster, and DeerFlow to
  `external/agent-systems/`.
- Move ast-grep, codebase-memory-mcp, codegraph, graphify, repomix, serena,
  and understand-anything to `external/harness-tools/codebase-intelligence/`.
- Move Headroom to `external/harness-tools/compression/`.
- Update `.gitmodules` and parent-repository documentation/source references.

## Constraints

- Preserve every submodule's current pinned commit and do not edit its internals.
- Keep `external/sync-submodules.sh` at its existing location.
- Use Git moves so the parent index retains Gitlink mode `160000`.

## Verification

1. Confirm every moved path remains a `160000` Gitlink and `.gitmodules`
   declares the same path.
2. Confirm `git submodule status --recursive` resolves all paths.
3. Search parent-owned files for stale old paths and run the existing updater
   fixture and Bash syntax checks.
