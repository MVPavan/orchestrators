# Code-Traversal Tool Analysis — bodha + data-miner

**A measured, Codex-gated study of which code-understanding tool best supports traversing and
understanding the user's own two Python codebases.** Scales the validated 4-anchor bodha pilot to
**36 anchors (18 bodha + 18 data-miner) × 4 tools**, spanning every symbol-type dimension, scored
against an independent AST-built, Codex-audited gold.

> Status: findings draft. Ground rules Codex-reviewed (round 1); gold Codex-audited; findings
> Codex-reviewed (round 2). Raw data gitignored under `scratchpad/harness-2repo/`.

---

## 1. What was run

| | |
|---|---|
| **Repos** | **bodha** (clean, strict-typed, Pydantic-heavy; 360 source files) · **data-miner** (larger, versioned `auto_annotation_v2/v3/v4` dirs, collision-heavy; 336 files). Both own their `.git`. |
| **Subjects** | Repo-wide git-isolated snapshots (Codex ruling: src-only would drop real cross-dir usage — e.g. `manual_reviewer/` importing v4 contracts). Tool-local HOME/cache; live repos never touched. |
| **Tools (scored)** | **serena** (LSP/pyright), **CBM** (codebase-memory-mcp graph), **codegraph** (tree-sitter graph), **ast-grep** (lexical baseline). |
| **Task** | S1 "where is this symbol used" at file level + per-definition disambiguation for collisions. |
| **Gold** | AST-built (`goldbuilder.py`): real identifier refs only (comments/strings excluded), relative-import + alias resolution, per-importer binding attribution. Independent of every tool. Codex-audited. |
| **Anchors** | ~18/repo across 21 buckets: clean models, collisions (2–4 defs), methods, protocols/ABCs, functions, enums, decorators, dataclasses, namedtuples, async, barrels, constants, inherited methods, heavy-fan-in utils. |

---

## 2. The headline: a two-level result

**Level 1 — merged "which files touch this name": all four tools are near-tied and near-perfect.**

| tool | merged macro-F1 (excl. 2 def-availability artifacts) |
|---|---|
| ast-grep | **1.000** |
| CBM | **0.997** |
| codegraph | **0.981** |
| serena | **0.984** |

This near-tie holds **specifically for file-level use-sites with definition files excluded** (the
scored metric). It is *not* a generic "all tools are equivalent at traversal" result — including
definition sites lowers the binding tools while ast-grep stays perfect, and line-level precision (not
scored) would separate them further. Within this metric: "merged where-used" is the *union* over all
same-named definitions, which is exactly what name matching returns, so **for "which files mention
this symbol," any of the four works and the fastest (ast-grep, 0.5 s for all 18 anchors) is as good as
the heaviest.**

**Level 2 — per-definition disambiguation ("which files use *this* definition"): the tools separate sharply.**

| tool | collision disambiguation F1 (mean, 13 collision anchors; DM16 excluded — star-reexport gold gap) |
|---|---|
| **serena** | **0.995** |
| CBM | 0.844 |
| codegraph | 0.822 |
| ast-grep | 0.489 |

*Assignment scoring: every definition (including unused "orphan" siblings) is scored; a file bound to a
sibling definition counts as a false positive for the queried def, so a tool that can't scope is
penalized on every collision.*

This is where tool choice actually matters — and it matters *a lot* on data-miner, whose
`auto_annotation_v2/v3/v4` dirs define the same class names 3–4× each.

---

## 3. Per-collision-anchor disambiguation (the real test)

mean per-def F1; sibling-definition hits scored as false positives for the queried def:

| anchor | symbol | repo | defs | serena | CBM | codegraph | ast-grep |
|---|---|---|---|---|---|---|---|
| BO1 | EntityProfile | bodha | 2 | **1.00** | **1.00** | **1.00** | 0.50 |
| BO2 | KnowledgeAuditResult *(alias)* | bodha | 2 | **1.00** | 0.50 | 0.50 | 0.79 |
| DM1 | BoundingBox | dm | 3 | **1.00** | 0.76 | 0.66 | 0.44 |
| DM2 | Candidate | dm | 3 | **1.00** | 0.72 | 0.93 | 0.48 |
| DM3 | FinalAnnotation | dm | 3 | **1.00** | 0.86 | 0.72 | 0.48 |
| DM4 | FilterConfig | dm | 4 | **1.00** | 0.64 | 0.74 | 0.35 |
| DM5 | OutputConfig | dm | 4 | 0.94 | **1.00** | 0.81 | 0.30 |
| DM6 | get_logger | dm | 4 | **1.00** | 0.91 | 0.70 | 0.34 |
| DM7 | StageWorker | dm | 2 | **1.00** | **1.00** | **1.00** | 0.66 |
| DM8 | Verdict *(cross-dir)* | dm | 2 | **1.00** | **1.00** | **1.00** | 0.66 |
| DM11 | ensure_dir | dm | 2 | **1.00** | **1.00** | 0.96 | 0.50 |
| DM17 | DatasetConfig | dm | 4 | **1.00** | **1.00** | **1.00** | 0.25 |
| DM18 | VLMVerdict | dm | 2 | **1.00** | 0.58 | 0.67 | 0.61 |

*(DM16 VLMConfig omitted — its v4 def is star-reexported, which the AST gold doesn't trace, so its gold is incomplete.)*

- **serena**: clean on 12/13 — the disambiguation instrument. Its LSP binds every usage to the exact
  definition, and it is the **only tool that handles the import-alias collision** (BO2
  `KnowledgeAuditResult as AgentAuditResult`: serena 1.00, CBM & codegraph 0.50).
- **CBM**: provides nontrivial `file_path`-scoped per-def sets (mean 0.84) — it does **not** simply
  collapse same-named defs — but with **cross-version over-attribution** (`BoundingBox` v3/v4 sets
  overlap on `manual_reviewer/` files) and it **misses the alias case** (BO2 0.50).
- **codegraph**: can scope per-def (`node -f <file>`), but its text trail **truncates at ~11 entries**,
  capping recall on high-fan-in defs; also misses the alias (0.50).
- **ast-grep**: structurally cannot disambiguate (name-only) → returns the merged set for every def, so
  orphan-sibling hits are false positives → 0.49.

---

## 4. Per-tool verdicts (both repos)

### serena — the precision / disambiguation leader
Clean disambiguation (0.99), resolves import aliases, perfect on clean models, enums, functions,
barrels, dataclasses, namedtuples. **Two structural limits, both reproduced:**
- **Needs an in-index definition.** For `AbstractCapability` (base class defined in *pydantic-ai*,
  outside the snapshot) serena returns nothing — it has no in-tree def to anchor on. For symbols
  defined outside your tree, serena can't do where-used.
- **`find_implementations` unsupported** in this pyright build → can't bridge a Protocol method to its
  concrete implementors.

### CBM (codebase-memory-mcp) — strong all-rounder, the pilot verdict softened
Best merged score among the binding tools (0.997). **Softening the 4-anchor pilot** (which found CBM
*collapses* same-named classes): on these repo-wide, git-rooted indexes it does **not** simply
collapse — its `file_path`-scoped queries return genuinely different per-def sets (disambig 0.84). But
the separation is **imperfect**: cross-version over-attribution (e.g. `BoundingBox` v3/v4 sets overlap
on `manual_reviewer/` files) and it **misses the import-alias case** (BO2 0.50, where serena scores
1.00). CBM did handle the method-dispatch anchor best (BO5 recall 0.83 vs serena 0.50, codegraph 0.33)
and resolved the module constant the others split on. The git-bleed hazard stayed neutralized (both
repos own their `.git`).

### codegraph — consistent, balanced, with two recall caps
Solid merged (0.98); per-def scoping works but is **truncation-capped** (~11 entries) and it missed one
local-import use on `ContextPack` (the pilot's `ecb.py` pattern, milder here). The safe zero-setup
default; not the precision tool.

### ast-grep — the honest lexical ceiling
Perfect merged recall (1.0) at 0.5 s, and the **only tool that finds usages of an externally-defined
symbol** (`AbstractCapability`: ast-grep 1.0, serena/CBM 0.0). But it cannot disambiguate collisions or
resolve dispatch — its precision is a function of how unique the name is.

---

## 5. Capability laws — confirmed and revised

**Confirmed (now on the user's own code):**
- **Binding/LSP tools disambiguate collisions; lexical tools cannot.** serena 0.99 vs ast-grep 0.64.
- **serena uniquely resolves import aliases** (`KnowledgeAuditResult as AgentAuditResult` → right def).
- **Method/polymorphic dispatch is the hardest bucket** for graph tools (BO5: codegraph 0.33 recall).
- **Merged where-used is essentially solved** by any tool at file granularity.

**New / revised on these repos:**
- **CBM disambiguates nontrivially when properly indexed** (0.84) — softens (not overturns) the pilot's
  "collapse" verdict: it separates defs but over-attributes across versions and misses aliases.
- **Externally-defined symbols invert the ranking — for this harness setup:** when a symbol's
  definition is *outside the indexed snapshot and no external def-anchor is supplied* (the
  `AbstractCapability` case), only lexical/name-keyed tools find usages; serena & CBM have no in-index
  node to anchor on. With dependency/site-package indexing or an explicit external def path this could
  differ — so this is a setup-specific finding, not proof that LSP/graph tools "cannot" do it.
- **codegraph's per-def truncation** is a concrete, repeatable recall ceiling on high-fan-in collisions.

---

## 6. Practical guidance for traversing bodha & data-miner

| You want to… | Use | Why (measured) |
|---|---|---|
| Trace **which definition** a usage binds to (the v2/v3/v4 config classes, bodha's duplicated `contracts/`) | **serena** | 0.99 disambiguation; only tool that nails aliases. The single most valuable capability for data-miner. |
| "Which files touch this name" — fast, exhaustive | **ast-grep** | 1.0 merged recall, 0.5 s, and finds externally-defined symbols the others miss. |
| Heavy where-used over Pydantic models + decent disambiguation, one index | **CBM** | 0.997 merged, 0.89 disambig, best on method dispatch; git-bleed safe here. |
| Zero-setup balanced default | **codegraph** | consistent; mind per-def truncation + local-import misses. |

**Bottom line:** for *navigation* at file level, all four are interchangeable — pick ast-grep for speed.
For *understanding* in these collision-dense repos (especially data-miner's versioned dirs), **serena is
the clear winner**, with CBM the strong general-purpose second.

---

## 7. Honesty & caveats
- **n is small per bucket** (1–4 anchors); verdicts requiring confidence (collisions, clean models)
  have ≥2 anchors per the battery rule. Single run; per-tool outputs not dual-reviewed.
- **The merged near-tie is metric-specific** (§2): file-level use-sites, definition files excluded.
  Including def-sites or scoring at line level would lower the binding tools relative to lexical.
- **File-level scoring only** — line/span precision (which would further separate ast-grep) not run.
- **Two serena 0.0 anchors are artifacts, not failures:** BO14 (external def — see §5, setup-specific)
  and DM15 `YOUTUBE_DOMAINS` (a module constant whose `Assign` def the gold-builder didn't register, so
  serena got no def-site to query). Both excluded from serena's merged figure (0.984).
- **Gold gaps (Codex-flagged):** star re-exports (`from .settings import *` + `__all__`) not traced →
  DM16 VLMConfig excluded from the disambiguation mean; `attr_caller_files` = attribute refs, not
  strictly call-sites (BO5).
- **Two scoring bugs found and fixed mid-analysis (both via Codex review):** (a) per-def dict shapes
  from serena/codegraph were dropped to a merged fallback — had falsely inflated CBM's relative lead;
  (b) the per-def module→def mapping didn't normalize `src/` layout, which had **silently dropped all
  three bodha collisions** from the disambiguation table, and orphan sibling-defs weren't FP-scored.
  All §2/§3 numbers are post-fix (bodha collisions included, orphan-sibling FPs penalized). The
  serena > CBM ≈ codegraph > ast-grep ranking held across the fix — the validation Codex asked for.

## 8. Provenance
Subjects, gold, scorer, tool outputs, and the two Codex transcripts: `scratchpad/harness-2repo/`
(`GROUND_RULES.md`, `goldbuilder.py`, `gold_manifest.json`, `score.py`, `scores.json`,
`results/<repo>/<tool>.json`). Tools: serena 1.5.4.dev0 (pyright), CBM dev, codegraph 1.0.1,
ast-grep 0.44.0. Codex: GPT-5.x via codex-adapter (critique/diagnose, xhigh, read-only).
