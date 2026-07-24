# Requirements Gap Analysis — tool-first battery vs requirements-first catalogue

Two **independent, tool-agnostic** xhigh research passes derived "what understanding a codebase actually
requires (human + agent)" from first principles, neither shown the 7 tools nor `scenarios.md`:

- **Codex gpt-5.5** → 50 requirements ([requirements-codex.md](requirements-codex.md))
- **Opus** → 12 dimensions A–L / 58 sub-requirements + 4 cross-cutting axes ([requirements-opus.md](requirements-opus.md))

**They converge strongly** (same taxonomy, same gaps, same "easy-to-overlook" list) — so treat the merged
picture as high-confidence, not one model's opinion.

## The merged picture: 12 dimensions of "understanding"

| Dim | What it answers | Covered by our 14 scenarios? |
| --- | --- | --- |
| **A** Orientation & topology | where am I, scale, entrypoints, where things live, conventions | **Partial** — only arch-map (scen. 10) |
| **B** Symbol navigation | where is X, who calls it, defs, refs, barrels, impact | **Yes — the battery's home turf** (scen. 1–9, 11, 13) |
| **C** Control & data flow | execution paths, data/taint flow, async/events, dynamic dispatch | **Partial** — only entry-trace (scen. 8) |
| **D** Intent, domain & rationale | domain glossary, *why* code exists, docs, feature→code, comment signal | **No** |
| **E** Data modeling & persistence | schema map, migration history, serialization, data lifecycle | **No** |
| **F** Runtime & behavioral | observed behavior, runtime state, performance, observability | **No** (needs running code) |
| **G** Contracts & invariants | type contracts, invariants, error-modes, test map, validation points | **Partial** — only type-impact (scen. 9) |
| **H** Build/run/test/debug | build, dev loop, test targeting, debug, CI/CD | **No** |
| **I** Config, env & external | config surface+precedence, prereqs, external deps, **secrets** | **No** |
| **J** History & change | git blame/intent, churn hotspots, idiom evolution | **No** (needs `.git`) |
| **K** Human & org | ownership, contribution rules, decision artifacts | **No** |
| **L** Efficiency, trust, freshness | **cost** at equal quality, **grounding**, **freshness**, **setup/isolation** | **Partial** — only context-pack (scen. 14) |

**Bottom line:** our 14 tool-first scenarios essentially measure **Dimension B** (+ a slice of A, C, L).
That is ~1–2 of 12 dimensions.

## The two upgrades BOTH passes demand (independently)

1. **Grade on 5 axes, not just correctness.** Every answer should be scored on **correctness · cost
   (tokens/reads/calls at equal accuracy) · grounding (citations + honest abstention) · freshness (current
   tree, no stale/worktree bleed) · setup/isolation**. Both passes call grading correctness *alone* "the most
   common evaluation mistake." We already have partial data for cost/setup/freshness from `findings.md`
   (token mass, the 65s build, the worktree git-diff bleed, the global-`$HOME` leaks).
2. **The cost-at-equal-quality A/B (L1)** — both flag it as the single highest-value *unrun* measurement
   (also `findings.md` §8).

## The strategic finding (report it, don't pad the battery)

Our 7 tools are **structural / navigation** tools. They serve Dimension B well and almost nothing else.
The comprehension (D), runtime (F), data (E), history (J), ops (H), config/secrets (I), async (C3), and
ownership (K) dimensions are **systemically under-served by *all* of them** — these need running code,
reading git, reading docs, or asking humans. That ceiling is an honest, valuable conclusion in its own right.

## Recommendation for the battery (before locking)

Keep the 14 (they are well-designed for Dimension B). Then:

- **Add the 5-axis grading to every scenario** (the most important upgrade; cheap, mostly data we can capture).
- **Add a small set of CAN-attempt scenarios** our structural tools could plausibly serve, so we *measure*
  the gaps instead of ignoring or padding them:
  - concept/feature → file location (A3/D4) — "find the code for behavior Y" by description, not symbol
  - entry-point + public-surface inventory (A2/C5)
  - comment/annotation signal: `TODO`/`FIXME`/`@deprecated` (D5) — cheap, ast-grep-native
  - architecture-map *quality*, sharpened (A4 — beyond today's scen. 10)
  - dynamic-dispatch / plugin-registry resolution (C4) — our tools mostly **fail** this; measuring the failure is the point
  - data/schema map (E1) — structural, the Drizzle tables are right there
  - the **cost-at-equal-quality A/B** (L1)
- **Do NOT pad** with scenarios no tool can attempt (runtime F, history J, ownership K) — instead add a single
  **honest-abstention probe** per such dimension to check whether tools **decline** vs **fabricate** (grades L2).

This keeps the battery rigorous and honest: measure the tools hard on what they do (B), measure the edge
where they break (A3/C4/E1/D5), grade everything on the 5 axes, and *report* the 10 dimensions structural
tools simply don't reach.
