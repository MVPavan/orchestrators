# Scenario Battery (repo-AGNOSTIC template) — Codex-designed

**These scenarios are generic capability tests, NOT tied to any repo.** They are designed once
(independently by Codex gpt-5.5, xhigh), validated on paperclip, and **reused unchanged** for OpenHands
and deer-flow. What changes per repo is the **anchors** (real symbols) and the **ground truth** (computed
per anchor) — see `anchors-<repo>.md`.

Tool shorthand: `ag` = ast-grep, `UA` = understand-anything, `CBM` = codebase-memory-mcp.
Several scenarios are deliberately `N/A` for tools outside their envelope (esp. `repomix`) — recording
"honestly unsupported" separately from "attempted and wrong" is part of the design.

## Scenarios

| # | Question | Why it discriminates | Legit tools | Objective grading |
| --- | --- | --- | --- | --- |
| 1 | "Where is this symbol used?" | Separates semantic refs from text/name matches | ag (baseline), serena, codegraph, CBM, graphify, UA | Gold = manually-classified rg candidates; semantic recall/precision, excluding defs/imports/(tests if scoped) |
| 2 | "Who calls this function/hook/component?" | Exposes JSX-body & factory-call blind spots | serena, codegraph, CBM, graphify, UA; ag approx | Gold = call/JSX sites only; caller F1 + missed-call category |
| 3 | "Go to definition from this use site" | Tests barrels, aliases, type-only imports, workspace pkgs | serena, codegraph, graphify; CBM name-level; ag limited | exact file:line; partial credit for right file/wrong symbol |
| 4 | "Trace a cross-package import path" | Breaks tools that ignore workspace:*/exports | serena, codegraph, graphify, CBM, UA; repomix context | Gold = manifest+import chain+export; path completeness |
| 5 | "Resolve through barrel/hub exports" | Tests index.ts re-export hops | serena, codegraph, graphify, CBM; ag syntactic | Gold = def + all re-export hops; hop recall |
| 6 | "Disambiguate same-named symbols" | Name tracers overcount collisions | all except repomix | Gold labels each occurrence by owning def; false-positive rate by collision bucket |
| 7 | "Blast radius of changing this symbol?" | Tests N-hop graph quality | serena, codegraph, CBM, graphify, UA; repomix context | Gold = curated 1st/2nd-order affected files; recall by hop + precision |
| 8 | "Trace from entrypoint to behavior" | Multi-hop lifecycle, not one symbol | codegraph, CBM, graphify, UA, serena; repomix context | Gold = ordered path segments; path edit-distance + missing critical nodes |
| 9 | "Find type/interface impact" | Separates type-aware from call-graph-only | serena; ag syntax; graphify/CBM/UA approx | Gold = type imports/annotations/satisfies/impls; typed-use recall |
| 10 | "Map architecture/dependencies" | Package-level graph, cycles, communities | graphify, codegraph, UA, repomix; CBM if queryable | Gold = pkg import graph; edge precision/recall + cycle correctness |
| 11 | "Sweep for structural patterns" | ag's fair native task | ag, graphify, UA; others optional | Gold = AST/manual list (routes, tables, forwardRef, adapter execute); exact count |
| 12 | "Find dead / tests-only code" | All likely weak → reveals overclaiming | all | Gold = no prod import/call path from entrypoints; conservative precision first |
| 13 | "Find near-duplicates / clones" | Native CBM differentiator | CBM, ag pattern, graphify structural | Gold = paired fns/modules w/ shared skeleton; clone-pair P/R |
| 14 | "Pack the minimum context to answer" | Fair task for repomix | repomix; graph tools may assist | Gold = required files per anchor; required-file recall, irrelevant ratio, token count |

## Metrics (record per tool × anchor × scenario)

`attempted`, `unsupported_reason`, `needs_setup`, `query_text`, `wall_time_bucket`, `failure_mode`,
`raw_found_count`, `gold_count`, `true_positive_count`, `false_positive_count`, `false_negative_count`,
`precision`, `recall`, `F1`, `exact_definition_hit`, `barrel_hops_found`, `cross_package_hops_found`,
`test_only_hits`, `shadowed_name_hits`, `notes`.

**Aggregate by bucket, not just global mean:** unique symbols · colliding names · barrel-exported ·
cross-package · React/JSX · type-only · service factory · DB schema · CLI · adapter execute.

**Verdict rule:** a weakness counts as real only if it reproduces on ≥2 anchors in a bucket (or 1 anchor
with catastrophic zero recall on a high-confidence gold set). Report macro-avg F1, recall/precision by
bucket, and keep "honestly unsupported" separate from "attempted and wrong".

## Ground-truth method (independent of every compared tool)

1. Seed candidates: `rg -n '\bSYMBOL\b'` across source extensions.
2. Read defs, imports, re-exports, manifests, nearby callers manually.
3. Classify each candidate: `definition` · `direct import` · `barrel re-export` · `type-only use` ·
   `runtime call` · `JSX element` · `object-method use` · `test/mock` · `string/comment/doc` ·
   `shadowed unrelated`.
4. Resolve package imports via the workspace manifests + local barrels.
5. Call-path Qs: include only executable edges (calls, JSX instantiation, createElement, traceable
   factory-returned method calls).
6. Type-impact Qs: type imports, annotations, `satisfies`, interface-typed literals, exported API.
7. Dead-code Qs: define scope (prod-only vs prod+tests) explicitly; don't count docs/comments/mocks.

**Traps:** test-helper name collisions, many adapter `execute` defs, duplicate interfaces, local vars
sharing a symbol name, barrel re-exports that aren't semantic uses, type-only imports erased at runtime,
React components used as JSX not calls, and `factory(db).method()` receiver patterns.

## Per-language note (for OpenHands / deer-flow, Python-heavy)

The scenarios are language-agnostic, but the *idioms* shift: "barrel/index.ts re-export" → Python
`__init__.py` re-export; "pnpm workspace:*" → Python package/namespace imports; "JSX component" still
applies to those repos' TS/React frontends. Keep the scenario, swap the idiom, recompute ground truth.
