# Robustness Findings — OpenHands (R2: the Python generality test)

**Round R2 of `multi-repo-robustness-plan.md`.** The same 7 tools × 20 anchors × the S1/S2 symbol-nav
core, on a **Python-heavy** repo (845 `.py` core + `enterprise/` + 1,231 TS/TSX React frontend). The
question R2 answers: **are the R1 paperclip tool-verdicts general, or were they TS/paperclip-specific?**

> **Evidence.** Every F1/P/R is a real fresh-index tool run scored against an **independently-computed,
> dual-reviewed binding-resolved gold** (Codex gpt-5.5 xhigh **and** an independent Opus auditor both
> audited it; they converged; the zero-unaccounted invariant holds exactly on the hard anchors). The gold's
> Python resolver (two roots `openhands`+`enterprise`, transitive `__init__.py` re-export closure, `#/` TS
> alias) was itself validated over 2 review rounds. Raw data: gitignored `scratchpad/harness-openhands/`.

## 0. Headline — what reproduced, what reversed

| R1 paperclip finding | R2 OpenHands verdict | why |
| --- | --- | --- |
| **CBM catastrophic on db-schema (0.08)** | **REVERSED** (model_schema bucket 0.95) | CBM's own metadata labels these anchors `Class` with rich inbound `USAGE/IMPORTS/INHERITS` edges — whereas TS Drizzle tables were `Variable` nodes (no inbound edges). The blindness tracked the node type, not the tool. (A13/A16 = 1.00; A12 itself = 0.85 — `Settings` name-bleed FPs cap its precision.) |
| **serena barrel-blind (0.47)** | **REVERSED** (barrel_initpy 1.00) | pyright follows `__init__.py` re-exports transparently — and serena even resolved *through TS `index.ts` barrels here* (A18). R1's barrel-blindness **did not reproduce**; the most plausible R1 cause was the unbuilt pnpm-workspace `dist/` (not A/B-proven here), not an inherent serena property. |
| **graphify silently drops secret files** | **REPRODUCED + WORSE** | drops 29 OpenHands source files (whole `openhands/app_server/secrets/` pkg + enterprise token stores). Unlike paperclip, **a dropped file (`stored_custom_secrets.py`) references an anchor (A13 `Org`)**, so it measurably **corrupts** A13 **recall to 0.76** (F1 0.84), missing the dropped file — not just metadata. |
| **CBM git-bleed (reads parent repo HEAD)** | **REPRODUCED** | OpenHands snapshot has no own `.git`; CBM walked up to the parent `orchestrators/.git`, baked HEAD `9fd20c9` + a Branch node into the graph; `detect_changes` ran on the **wrong repo**. |
| **lexical tools: perfect recall, collision precision collapse** | **REPRODUCED** | ast-grep/repomix recall ~0.9, but A5/A11 `start_job` collapse to identical sets; short Python names (`app`,`Settings`,`Org`) are noisy. |
| **codegraph strong all-round, captures JSX** | **REPRODUCED** (0.85→0.89) | barrel-transparent on Python too; JSX `<X/>` found; only same-name collisions and `callers`-merging limit it. |

**Net:** two of R1's most-cited tool weaknesses (CBM db-schema, serena barrels) **did not reproduce on
Python** — CBM's was a TS-`Variable`-node artifact (confirmed by node type), serena's most plausibly the
paperclip build (not A/B-proven). Two safety/robustness findings (graphify secret-drop, CBM git-bleed) **are
general and the secret-drop is worse on Python.** This is the entire value of replication.

## 1. The 7-tool matrix — S1 "where is this symbol used?" macro-F1

| scope | ag* | rpx* | ser | cg | CBM | gfy | UA |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **overall (20)** | 0.81 | 0.75 | 0.90 | 0.89 | **0.95** | 0.62 | 0.66 |
| entrypoint (2) | 0.71 | 0.64 | 0.80 | 0.87 | 0.90 | 0.40 | 0.90 |
| service_method (4) | 0.55 | 0.62 | 0.83 | 0.80 | **0.92** | 0.35 | 0.49 |
| barrel_initpy (3) | 0.95 | 0.97 | **1.00** | **1.00** | **1.00** | 0.82 | 0.72 |
| cross_package (5) | 0.94 | 1.00 | 0.93 | 1.00 | 0.98 | 0.90 | 0.81 |
| collision (4) | 0.56 | 0.73 | 0.67 | 0.64 | **0.95** | 0.42 | 0.46 |
| model_schema (3) | 0.90 | 0.72 | 1.00 | 0.92 | 0.95 | 0.93 | 0.74 |
| type_protocol (4) | 0.93 | 0.66 | 0.75 | 0.89 | **0.99** | 0.73 | 0.60 |
| react_jsx (3) | 0.76 | 0.86 | **1.00** | 0.88 | 0.92 | 0.43 | 0.48 |
| dynamic_dispatch (2) | 0.66 | 0.61 | 1.00 | 1.00 | 1.00 | 0.25 | 0.53 |

Precision / recall split (S1): ag 0.83/0.88 · rpx 0.68/0.94 · ser **0.95**/0.87 · cg 0.87/0.97 · CBM 0.96/0.94 ·
gfy 0.70/0.67 · UA 0.66/0.80. `*` lexical baselines (recall-inflated; see R1 §2 caveat — same here).

## 2. R1 → R2 deltas (overall S1 macro-F1)

| tool | paperclip | OpenHands | Δ | reading |
| --- | --- | --- | --- | --- |
| **CBM** | 0.63 | 0.95 | **+0.32** | Python models fixed the db-schema blindness; best on OpenHands |
| **serena** | 0.66 | 0.90 | **+0.24** | barrel-blindness gone; pyright forward-nav excellent |
| UA | 0.57 | 0.66 | +0.09 | better Python import resolution (70% vs TS 31%) |
| codegraph | 0.85 | 0.89 | +0.04 | consistent, strong on both |
| ast-grep | 0.85 | 0.81 | −0.04 | lexical; Python short-name noise |
| repomix | 0.84 | 0.75 | −0.09 | lexical; cross-language bleed lowers precision |
| **graphify** | 0.77 | 0.62 | **−0.15** | method call-graph is **same-file-only** on Python; secret-drop corrupts A13 |

## 3. New findings, OpenHands-specific (not visible on a single TS repo)

- **Cross-language name bleed (polyglot hazard).** CBM and codegraph mix Python `Settings`(A12) where-used
  with frontend `.tsx`; CBM, repomix, UA mix `capture`(A20) with JS `posthog.capture`. On A12 the two
  bleeding tools land at P=0.73 (CBM) and 0.63 (codegraph). **ast-grep avoids it** — its `-l python` / `-l tsx`
  split keeps A12 at P=1.0. A single-language repo hides the hazard entirely.
- **graphify method call-graph is local-only.** `calls` edges link caller→callee only within the **same
  file**, so cross-file method callers for A3/A20 = 0. This drags the method buckets — service_method
  (A3/A4/A5/A20) = 0.35 and dynamic_dispatch (A3/A4) = 0.25 — though both buckets *also* include the
  non-method anchor A4 (`get_impl` = 0), so the call-graph locality is a major but not sole cause. New and
  severe on Python's method-heavy code.
- **serena abstract-method blind spot.** A11 `Manager.start_job` (abstract) → `{}` — pyright binds
  `self.start_job()` to the concrete subclass, so the ABC method shows no callers; `find_implementations`
  is unsupported by pyright. Polymorphic call-site discovery is weak.
- **Truncation reliability traps (two failure shapes, one trap).** serena `max_answer_chars` silently
  truncated A9 `ProviderType` to *empty* (actually 103 files / 686 refs) until the limit was raised — looks
  like "0 results". codegraph's default `callers` limit (20) silently **caps to a partial set** (true counts
  107/135/189/102 for A9/A12/A13/A19) — not empty, but confidently incomplete. Different shapes (zero vs
  truncated), same trap: an agent that trusts the returned count is misled either way.
- **graphify barrels weaker on Python.** It emits `re_exports` edges for `__init__.py` but **file-granular**
  (file→file, 0 symbol targets); on TS `index.ts` it resolved re_exports to symbol nodes. The barrel bucket
  still scores 0.82 — A6/A7 resolve fine; A8 `GitHubReposMixin` is the one that drops (extra files). The
  file-granular mechanism is real but not uniform across all three barrel anchors.

## 4. Setup / freshness / isolation (this round)

- **Fresh indexes built per tool:** CBM 1.76s · codegraph ~12s · graphify ~41s · UA ~6s · repomix 1.96s ·
  serena ~12s Python-LSP cold (pyright auto-installed) +~13s TS-LS · ast-grep stateless. All confirmed
  `.py` indexed, `.venv`/`__pycache__`/`node_modules` excluded (0 leaks).
- **serena Python-LSP setup was fully automated** (pyright 1.1.403 + cpython via uvx, zero manual steps) —
  contradicts any worry that Python support is high-friction.
- **Isolation audit:** clean — [`results/_isolation_audit_R2.md`](results/_isolation_audit_R2.md). Cleaner
  than R1: the codegraph telemetry kill-switch (R1 leak) held this round (0 fresh `~/.codegraph` writes); only
  a benign empty `~/.serena` dir. CBM git-bleed (§0) is a freshness hazard recorded there, not a sandbox leak.

## 5. Caveats

- Method anchors (A3/A5/A11/A20) are polymorphic dispatch — gold = call-site set (single-def) or class-scoped
  (collision); precision is inherently capped. A5's `method_def_sites` lists all 8 same-named overrides (the
  method-*name* find_implementations answer); a tool returning only the JiraManager def is not penalized.
- OpenHands has **milder collisions** than paperclip (fewer extreme same-name top-level symbols), so the
  collision bucket is easier here for everyone — the absolute collision scores are not directly comparable to
  R1; the *ranking* (serena/CBM handle collisions, lexical/graph-name-keyed collapse) is what transfers.
- F1-overall still flatters the lexical tools (recall-inflated); read per-bucket + precision.

---

*Status: gold dual-reviewed (Codex gpt-5.5 xhigh + independent Opus, converged); battery scored; isolation
audit clean (R2.8); **Codex adversarially reviewed these findings (R2.6) — verdict applied** (softened the
serena-cause and cross-language-bleed claims, corrected the `dynamic_dispatch` anchor list and the A13 recall
figure, distinguished serena's empty-truncation from codegraph's partial-cap). The cross-repo synthesis (which
findings held across paperclip + OpenHands, pending deer-flow R3) is the final deliverable. Raw data, gold,
scorers: gitignored `scratchpad/harness-openhands/`. Matrix: `scratchpad/harness-openhands/_gt/scores_matrix.md`.
Next: **R3 deer-flow**.*
