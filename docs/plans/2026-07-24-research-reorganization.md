# Research Taxonomy Reorganization

## Goal

Mirror the external taxonomy in `docs/research/`.

## Scope

- Move the codebase research category to `docs/research/agent-systems/`.
- Move the harness research category to
  `docs/research/harness-tools/codebase-intelligence/`, including Headroom
  research.
- Update parent-owned links, ignore rules, and report-tree defaults.

## Constraints

- Preserve research content and history through Git moves.
- Do not change research conclusions or submodule contents.

## Verification

1. Search parent-owned files for references to the former research categories.
2. Confirm moved directories and root ignore behavior.
3. Run whitespace checks and inspect `git status`.
