# Robustness Findings — paperclip (R1 of the multi-repo battery)

**Round R1 of `multi-repo-robustness-plan.md`.** 7 tools × 20 anchors × the S1/S2 symbol-navigation
core + structural scenarios, graded against an independently-computed **binding-resolved** ground truth.
This is the paperclip round; OpenHands (R2) and deer-flow (R3) run only after user review (the ⛔ pause gate).

> **Status of evidence.** The F1/precision/recall numbers are real tool runs scored against the gold by
> `scratchpad/harness/_gt/score.py`. The §4 file-count and §7 secret-drop figures are *raw measured*
> counts (not scorer output). A few mechanism descriptions are *qualitative*, recovered from a worker's
> structured notes and labelled as such. Raw per-tool answers, the gold, and the scorer live in the
> gitignored `scratchpad/harness/`. This report was adversarially reviewed by Codex gpt-5.5 xhigh, which
> narrowed several over-broad claims (UA-A3, CBM mechanism, CBM-JSX "win", abstention wording) — corrected below.

---

## 0. The hard ceiling (unchanged, restated)

All 7 are **static, pre-indexed, read-only structural/navigation tools.** None runs code, none reads
`.git` history, only repomix reads non-code files. **Runtime (F), git history (J), humans/ownership (K),
build/ops (H) are out of reach by construction.** This round measures the tools hard on what they *do*
(symbol navigation + structural edge) and converts the unreachable dimensions into honesty checks (§7).

## 1. The controlled variable — binding-resolved ground truth

Gold was computed independently of every tool (`scratchpad/harness/_gt/harvest2.py`): ripgrep seed →
per-file import/re-export binding (all clauses scanned) → **transitive re-export closure** from each
definition site → 38-package dynamic manifest map. **Codex gpt-5.5 xhigh adversarially cross-checked it**
and found one real undercount (A16 `execute`: a mixed-import file `server/src/adapters/registry.ts` that
imports `execute` from several adapters — my resolver stopped at the first clause). Fixed; A16 → 5 bound
files. A2/A7/A12/A13/A14 confirmed correct.

**The lexical→bound gap is the whole discriminator.** A naive grep returns a noisy superset; the gold is
the binding-resolved subset that a *good* tool should converge on:

| anchor | symbol | naive lexical hits | **bound files (gold)** | what the gap is |
| --- | --- | --- | --- | --- |
| A7 | `issues` (Drizzle table) | 6,251 occ / 490 files | **123 files** | `.issues` member access, Zod `error.issues`, locals |
| A16 | `execute` (codex-local fn) | 673 / 171 | **5 files** | 127 polymorphic `.execute()` dispatch + 38 sibling-adapter defs |
| A2 | `createApp` (app factory) | 770 / 83 | **1 file** | 80 test files declare their *own* local `createApp` |
| A12/A13 | `CatalogTeam` ×2 packages | 82 / 14 (shared name) | **9 / 3** (clean split) | same name, two packages — binding separates them |

## 2. The core result — S1 "where is this symbol used?" macro-F1

File-level F1 vs the binding-resolved gold. `ag`=ast-grep, `rpx`=repomix, `ser`=serena, `cg`=codegraph,
`CBM`=codebase-memory-mcp, `gfy`=graphify, `UA`=understand-anything.

| scope | ag | rpx | ser | cg | CBM | gfy | UA |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **overall (20 anchors)** | 0.85 | 0.84 | 0.66 | **0.85** | 0.63 | 0.77 | 0.57 |
| collision (A2,A12,A13,A16) | 0.37 | 0.35 | **0.78** | 0.35 | 0.54 | 0.50 | 0.48 |
| jsx_react (A17,A18,A19) | 0.98 | 0.98 | 0.98 | 0.98 | **0.44** | 0.96 | 1.00 |
| barrel_xpkg (A3,A6,A8,A9,A10,A11,A14) | 1.00 | 1.00 | **0.47** | 1.00 | 0.61 | 0.87 | **0.26** |
| db_schema (A7,A8) | 0.96 | 0.88 | 0.49 | 0.99 | **0.08** | 1.00 | 0.19 |
| factory_service (A2,A4,A5,A6) | 0.76 | 0.76 | 0.85 | 0.76 | **0.91** | 0.67 | 0.58 |
| type_only (A11,A12,A13,A14) | 0.81 | 0.80 | 0.39 | 0.78 | 0.42 | **0.91** | 0.25 |

**The same matrix split into precision vs recall (this is the real story F1-overall hides):**

| | ag* | rpx* | ser | cg | CBM | gfy | UA |
| --- | --- | --- | --- | --- | --- | --- | --- |
| macro-Precision (20) | 0.82 | 0.80 | **0.94** | 0.82 | 0.79 | 0.75 | 0.64 |
| macro-Recall (20) | **1.00** | **1.00** | 0.59 | 0.98 | 0.61 | 0.92 | 0.58 |
| **collision-bucket Precision** | **0.28** | **0.26** | **1.00** | **0.26** | 0.61 | 0.51 | 0.55 |

`*` = **lexical baselines** (ast-grep, repomix): they match text, not bindings. Their recall is 1.0 *by
construction* (the gold is a subset of any superset grep) and the scorer does not penalize member-access
noise — so their **F1-overall is inflated**. The truth is in the bottom row: **on collisions their
precision craters to ~0.27** (they return the whole same-named pile). Conversely **serena trades recall
for precision** (P 0.94 / R 0.59) — it is the *only* tool that nails collisions (P 1.00) but it is
barrel-blind (low recall). Read the lexical tools and the semantic tools as two different classes; do not
rank them on the same F1 column. §4 shows the raw output-size cost behind these precision numbers.

## 3. Per-bucket verdicts (verdict rule: a weakness counts only if it reproduces on ≥2 anchors in a bucket)

- **collision** — *serena wins (0.78).* Its LSP returns each same-named symbol as a separate kind-tagged
  entry, so `createApp` (A2→exactly 1), `execute` (A16→3 in-package), and both `CatalogTeam`s are
  separated. Lexical tools (ag/rpx) and **name-keyed graphs** (cg, gfy, UA) collapse the collision —
  reproduced across A2 + A16. CBM is middle (0.54): it stores each def as a separate `file_path+line` node
  and can scope to one, but you must enumerate the set yourself.
- **barrel_xpkg** — *serena (0.47) and UA (0.26) are both barrel-blind.* Serena reproduces on
  **A3/A9/A11/A14** (`find_referencing_symbols` stops at the **barrel index file** — A14→`adapter-utils/
  src/index.ts` only, missing all 12 downstream consumers; A9→`shared/src/index.ts` only; A3 F1 0.25).
  UA reproduces on **A9/A10/A11/A14** (import-map resolves an import only to the barrel `index.ts`, never
  to the leaf) — **but not A3** (UA A3 F1 0.96, 13/14; do not cite A3 as UA evidence). codegraph/ast-grep/
  repomix get 1.00; **graphify (0.87) has real `re_exports` edges** that pierce the barrel to the def
  (cross-package).
- **db_schema** — *CBM is catastrophic (0.08)* — reproduced on both A7 and A8. The mechanism is
  **reference-style-dependent, not blanket "Variable-node blindness":** a symbol *invoked* as a value still
  gets edges (A7 `issues` is also a Variable node yet got 14 CALLS/USAGE refs), but a Drizzle table whose
  references are FK/column member-access (A8 → `[]`) or pure type/const reads gets **zero inbound edges**.
  So CBM recovers a tiny CALLS-only subset (A7→14 of 123) and nothing for A8. codegraph (0.99) and graphify
  (1.00) nail both.
- **jsx_react** — *CBM weak (0.44)* — A18 `ChatComposer` (a `forwardRef` stored as a `Variable`) is
  graph-invisible (0 inbound edges → recall 0); A17 `MarkdownBody` (a function component) recovered only
  **5 of 25** (F1 0.33). All other tools handle JSX well. **This corrects the prior capability card's "CBM
  wins JSX callers" claim:** the scored data shows CBM captures only a *small function-component subset*
  (A17 5/25) and is *blind* to forwardRef/const-stored components (A18 0/7) — it does not "win" JSX.
- **type_only** — graphify (0.91) and the lexical pair (0.80) lead; serena (0.39)/UA (0.25)/CBM (0.42)
  weak because type references travel through barrels (same root cause as barrel_xpkg).

## 4. Cost proxy — the noise behind the F1 (cheap axis; reported file count vs gold)

The headline cost difference is **how much noise you wade through to get the answer.** Reported file count
per tool on the collision/heavy anchors (gold in bold):

| anchor (gold) | ag | rpx | ser | cg | CBM | gfy | UA |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A2 `createApp` (**1**) | 82 | 83 | **1** | 50 | 2 | 49 | 5 |
| A7 `issues` (**123**) | 173 | 544 | 32 | **121** | 14 | **123** | 29 |
| A16 `execute` (**5**) | 46 | 175 | **3** | 43 | 2 | 8 | 2 |
| A17 `MarkdownBody` (**25**) | 29 | 47 | 28 | 28 | 5 | 32 | **25** |

repomix on A16 returns **175 files for a 5-file answer (35× noise)**; serena returns 3. codegraph and
graphify converge on A7 (121–123 vs gold 123) where the lexical tools return 173–544. **Precision/output-size
is the real differentiator the overall-F1 hides.** Wall-times (worker meta): ag/rpx/cg/CBM queries ~0.1–0.5s
each against warm indexes; serena needed an MCP daemon + warm-up (see §6 freshness).

> **The one heavy measurement still unrun:** cost-at-equal-answer-quality (tokens/reads/turns via each tool
> vs a Read/grep baseline, answer held at gold). Both Codex and Opus independently flagged this as the
> single highest-value unrun measurement. The cheap proxy above is captured; the heavy A/B is **deferred**,
> not skipped — it needs a dedicated agent-style A/B harness (planned, not run this round).

## 5. Per-tool one-line verdicts (5-axis)

- **ast-grep** — honest lexical baseline. Recall 1.0, precision collapses on collisions (A2 0.02). Stateless
  = always fresh (a strength), zero setup, zero isolation risk. Strong at S10 exact structural counts.
- **repomix** — context packer, not a query engine. Same lexical profile as ast-grep but noisier (A16 175
  files). Real strengths: comments/`@deprecated` survive the digest (S12), native context-pack (S16:
  171,608 tokens for a 3-file `issueService` slice), **does index `secrets.ts`** (unlike graphify).
- **serena** — best collision/disambiguation (LSP; collision-bucket precision 1.00, the only tool to
  separate every same-named symbol), highest overall precision (0.94) but lowest-tier recall (0.59) because
  it is **barrel-blind** (stops at the barrel index — shared with UA) and **cold-cache flaky** (first query
  after load returns 0/1; warm re-run correct — A5 0→12, A7 1→32). Highest setup cost (MCP daemon, no
  one-shot CLI). Secrets visible.
- **codegraph** — best all-round semantic tool (overall 0.85 with *real* precision). Resolves barrels and
  cross-package, captures JSX **and hooks** (contradicting its capability card's "misses JSX"), indexes
  `secrets.ts`. Only weakness: heavy same-name collisions (name-keyed; A2 enumerates but truncates at ~29).
- **codebase-memory-mcp** — two catastrophic, **reference-style-dependent** blind spots: **db-table
  references** (A8→0, A7→14/123 — value-invocations get edges, member/FK refs do not) and **forwardRef
  components** (A18 invisible; A17 only 5/25). Genuinely wins the `createApp` collision (A2 1.00, file-path
  scoped). **Git-bleed confirmed:** reports the *parent* repo's HEAD `9fd20c9`, not the subject's. Indexes
  secrets.
- **graphify** — strong on db-schema/type/barrel via genuine `re_exports` edges; clean package dep graph
  (exactly 1 cycle: server↔scripts). **Polymorphic-dispatch blind** (A16 `execute` 0 incoming edges, F1
  0.00). **Silently drops secret files** (see §7).
- **understand-anything** — weakest at symbol nav (barrel-blind, interfaces invisible, JSX uncaptured) but
  good at coarse architecture/hubs/layers. File/module-level graph, no symbol binding.

## 6. Freshness & isolation (cheap axes, observed)

- **Freshness:** ast-grep/repomix stateless → always fresh. Precomputed tools (cg/CBM/gfy/serena/UA) all
  served from prior-session indexes. **serena cold-cache flakiness** is a real freshness hazard (first query
  unreliable). **CBM git-bleed** (reads the parent repo's git state) is a worktree-isolation hazard.
- **Isolation:** all tools invoked by explicit local path; tool-local HOME/cache; the canonical subject
  stayed `chmod a-w` (unmutated). Independent audit in §8 / `_isolation_audit.md`.

## 7. Honesty / abstention (the unreachable dimensions)

**Correction (Codex review):** the 7 designed abstention probes for the genuinely unreachable *dimensions*
(D2 rationale, F1 runtime, C2 data-flow, C3 async, E2 migration, J1 history, G3 failure-mode) were **not
run as explicit probes this round** — they are **deferred** alongside the heavy cost A/B. It is therefore
*not* true that "all 7 workers marked out-of-reach scenarios unsupported": several workers correctly
*answered* the reachable scenarios their tool supports (repomix did S11/S12/S16, codegraph and UA did S11).

What this round *did* establish about honesty, from the raw runs:

- **The static tools cannot fabricate a location** — they return `file:line` or nothing; the fabrication
  risk lives only in an agent/harness wrapping the silence (not exercised here).
- **Per-scenario support was reported honestly:** each worker marked the scenarios its tool genuinely cannot
  do (e.g. serena/CBM → type-impact; graph tools → comment-signal) `unsupported` *with reasons*, and
  attempted only what the tool supports. No worker invented an op its tool lacks.

The one *safety* abstention failure is a tool, not the harness:

- **graphify silently drops secret files (verified S14).** Its `detect.py._is_sensitive` removes any file
  whose name contains `secret/token/password/credential/private_key` or that sits under a `secrets/` dir —
  the **entire `server/src/secrets/` provider directory, `Secrets.tsx`, the `company_secrets` table, and
  `.env.example`** (34 TS/TSX files) vanish from the graph **with no warning**. No anchor lives in a dropped
  file, so where-used is unaffected — but secret-handling code is invisible to architecture/blast-radius
  analysis. Every other tool indexes these files.

## 8. Caveats & what is paperclip-specific

- **F1-overall flatters lexical tools** (see §2 caveat) — read per-bucket precision + §4 cost, not the
  overall row alone.
- The scorer treats member-access/ambiguous files as "ignored" (not penalized), because whether `.issues`
  counts is tool-dependent. This is generous to high-recall tools; the cost table (§4) restores the picture.
- S1 and S2 collapse to the same set for tools with no separate semantic-references op (cg, ag, rpx) — only
  serena/CBM distinguish callers from type-only refs.
- **Likely paperclip-specific:** the *severity* of the collision buckets (paperclip has 10 sibling adapter
  `execute`s and 80 test-local `createApp`s — an unusually adversarial monorepo). The barrel-blindness and
  CBM Variable-node blindness are **structural tool properties** and should reproduce on the Python repos —
  R2/R3 will test exactly that (Python `__init__.py` re-export ≈ barrel; SQLAlchemy model ≈ Drizzle const).

## 9. What reproduced vs what's new vs the prior capability cards

- **Reproduced:** serena barrel-blindness (and UA's, on A9/A10/A11/A14); graphify `secrets.ts` silent drop;
  CBM git-bleed; collision-hardness for lexical tools.
- **Corrected:** "codegraph misses JSX/hooks" — **did not reproduce** (codegraph captured both, A17 25/25).
  "CBM wins JSX callers" — **not supported by the data**: CBM recovered only a small function-component
  subset (A17 5/25) and is blind to forwardRef/const components (A18 0/7).
- **New:** CBM's catastrophic, reference-style-dependent db-table blindness (A8 0.00 / A7 0.08); graphify's
  polymorphic-dispatch blindness (A16 0.00); serena cold-cache flakiness; the precision/recall split that
  shows the lexical tools' F1-overall is inflated; the quantified per-bucket separation of all 7 tools.

---

*Raw answers, gold, scorer, and per-tool scored JSON: `scratchpad/harness/` (gitignored). Score matrix:
`scratchpad/harness/_gt/scores_matrix.md`. Pending: Codex adversarial review of these findings (R1.6),
isolation audit (R1.8), then the ⛔ user-review pause gate before R2/R3.*
