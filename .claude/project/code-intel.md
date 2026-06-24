# Code Intelligence (code-intel plugin)

Per-repo facts for the `code-intel` plugin (serena + CBM + ast-grep). The `adopt`
command fills these in for the current repo; the angle-bracket values are
placeholders until adoption runs. Plugin lives at `external/code-intel/`.

## Is code-intel warranted here?
- **Substantial codebase?** <yes/no — large, multi-session, navigation-heavy work benefits; tiny/throwaway repos don't>
- **Decision:** <enable / skip — ast-grep via the plugin's `bin/` is ~0 cost regardless; serena + CBM are the cost/benefit call>
- **Primary language(s):** <e.g. python> → serena LSP backend: <e.g. pyright>

## Enablement (per-repo, opt-in — never auto-enabled; it's a trust decision)
1. Register the marketplace once on this machine — point it at the plugin dir
   (the path to `external/code-intel`) or its git URL once pushed:
   `claude plugin marketplace add <path-to>/external/code-intel`   # or a git URL
2. Enable for this repo — commit `"enabledPlugins": { "code-intel@code-intel": true }`
   to `.claude/settings.json` (team) or `.claude/settings.local.json` (machine-local),
   or toggle it via `/plugin`.
3. Once per machine: `/code-intel:setup` (locate/install binaries).
   Once per repo: `/code-intel:index-repo` (build the CBM graph).

## State (fill via /code-intel:doctor and /code-intel:index-repo)
- **Binaries resolved?** <serena / CBM / ast-grep — via PATH or CODE_INTEL_*_BIN?>
- **Indexed?** <yes/no>
- **CBM project name:** <path-slug from `list_projects`; REQUIRED as the `project` arg in every CBM query — see `learnings.md` (2026-06-24)>

## Workflow rule
For navigation / where-used / impact / concept-search / rename: query the graph
(serena / CBM) or ast-grep FIRST and stop on bounded evidence; don't read whole
files to re-derive what the graph returns. The `graph-first` skill enforces this;
remember CBM queries need the `project` arg above.
