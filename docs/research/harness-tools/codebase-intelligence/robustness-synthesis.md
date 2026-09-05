# Cross-Repo Synthesis — code-understanding tool robustness across 3 repos / 2 languages

**The capstone of `multi-repo-robustness-plan.md`.** Three rounds, same 7 tools × 20 anchors × the S1
"where is this symbol used?" core, each scored against an independently-computed, **binding-resolved gold**
(Codex gpt-5.5 xhigh reviewed every round's gold; R2/R3 golds were *also* independently Opus-audited; adversarial
Codex review ran on every round's findings):

| Round | Repo | Language profile | gold |
| --- | --- | --- | --- |
| R1 | paperclip | TypeScript/TSX monorepo (pnpm) | Codex-reviewed |
| R2 | OpenHands | Python (2 roots) + React/TS | dual-reviewed (Opus + Codex) |
| R3 | DeerFlow 2.0 | Python (2 roots) + Next.js/React | dual-reviewed (Opus + Codex), md5 `05352aaa` |

The question the whole battery answers: **which tool verdicts are general capability laws, and which were
artifacts of one repo, one build, or one language?**

## 1. The 3-round scoreboard — overall S1 macro-F1

| tool | paperclip (TS) | OpenHands (py+ts) | DeerFlow (py+ts) | spread | character |
| --- | --- | --- | --- | --- | --- |
| **codegraph** | 0.85 | 0.89 | 0.79 | 0.10 | **most consistent**; balanced P/R; JSX-aware |
| **CBM** | 0.63 | 0.95 | 0.85 | **0.32** | **bimodal by language** (see §2.1); best on Python |
| **ast-grep**\* | 0.85 | 0.81 | 0.84 | 0.04 | stable, but F1 is recall-inflated (R≈1.0) |
| **serena** | 0.66 | 0.90 | 0.74 | **0.24** | highest precision; **most idiom-sensitive** |
| **repomix**\* | 0.84 | 0.75 | 0.65 | 0.19 | lexical; precision erodes as repos get polyglot/doc-heavy |
| **graphify** | 0.77 | 0.62 | 0.61 | 0.16 | weakest on Python; safety + method-graph defects |
| **UA** | 0.57 | 0.66 | 0.72 | 0.15 | improving; capped by file-granularity + multi-root |

\* lexical baselines — F1 flatters them (recall ≈ 1.0); judge on precision + per-bucket.

## 2. What GENERALIZED (held across ≥2 repos — durable capability laws)

### 2.1 Node-type + reference-style determines graph-tool blindness — the single biggest discriminator
A graph tool can only answer "where is X used" if its extractor models X as a **node with inbound edges** *and*
the references are expressed in a style the extractor links. CBM is the clean experiment: TS schemas defined as
`const`/`Variable` and used via member-access (paperclip Drizzle tables) → **0.08, catastrophic**; the *same
tool* on Python Pydantic/SQLAlchemy models (`class` → Class nodes with USAGE/IMPORTS/INHERITS edges) → **0.95
(R2), 0.97 model_schema (R3)**. (R1 narrowed the mechanism: it's node-type *plus* reference-style — some TS
Variable nodes still drew CALLS/USAGE edges.) The blindness was never a blanket CBM property — it tracked **the
node type and reference idiom the language produces**, which is why CBM swings 0.63→0.95→0.85. Lesson:
**graph-tool coverage is a function of (extractor × language idiom), not the tool alone.**

### 2.2 Safety hazards are tool-intrinsic and reproduce everywhere
- **graphify silently drops "secret"-named source files** — all **3 repos**. On OpenHands and DeerFlow a dropped
  file *referenced a live anchor* (`stored_custom_secrets.py`→A13; `test_mcp_config_secrets.py`→A7), measurably
  corrupting recall — not just metadata loss. A security-analysis tool that can't see secret-handling code is a
  deployment risk independent of language.
- **CBM git-bleeds into the parent repo** — all **3 repos**. With no own `.git`, CBM walks up to the enclosing
  worktree and bakes the *wrong* repo's HEAD/changed-files into its graph. A freshness/worktree hazard that will
  bite anyone analyzing a subdirectory or vendored snapshot.

### 2.3 Lexical tools: near-perfect recall, collision-precision collapse — all 3 repos
ast-grep & repomix hit very high recall every round (R2 0.88/0.94, R3 1.00/1.00 — they see every token) but
their precision collapses on collisions and common names. ast-grep's language split (`-l python`/`-l tsx`) is its
one structural advantage — it avoids cross-language name bleed (R2 A12 `Settings`: ast-grep P=1.0 where graph
tools mix Python and TS same-named symbols).

### 2.4 codegraph is the most consistent *semantic* tool
0.79–0.89 across all 3 (among binding-aware tools; ast-grep's raw spread is smaller but it's a lexical
baseline), balanced precision/recall, barrel-transparent on both `index.ts` and `__init__.py`, captures JSX. Its
only systematic weakness is merging same-named symbols (collisions). If you must pick one semantic tool blind to
the codebase, codegraph is the safest default.

### 2.5 Polymorphic / method dispatch is hard for graph tools — reproduced on both Python repos
graphify's call-graph is **same-file-only** (cross-file method callers ≈ 0 → DeerFlow A20 F1 0.12); codegraph
merges same-named methods; serena's pyright has method-resolution gaps. No graph tool resolves runtime dispatch;
lexical tools over-recall it. The method-anchor bucket is depressed for everyone every round.

### 2.6 Collisions are the hardest bucket, and absolute difficulty is repo-dependent
Same-named symbols (two `StreamEvent`, abstract+concrete `execute_command`, cross-language `Message`) are the
lowest-scoring bucket in every round, but *how* low is repo-dependent: OpenHands' milder collisions let CBM reach
0.95 and repomix 0.73 there, whereas DeerFlow's harder collisions hold every tool ≤ 0.55. So the **floor moves
with the repo**; what transfers is the **ranking** — binding/LSP tools (serena, CBM) handle collisions better
than name-keyed graph/lexical tools, which merge same-named symbols. The standout: **only serena's LSP cleanly
disambiguates the hard cross-language collision** (DeerFlow A17 `Message`: local React component vs
`@langchain/langgraph-sdk` import → serena 1.00, all others ≤ 0.14) — yet serena *itself* loses DeerFlow's
Python-method collisions (A5/A12 → 0). Disambiguation is the open frontier; no tool is reliable across collision types.

## 3. What did NOT generalize (artifacts mistaken for tool properties)

- **"CBM is blind to data models" (R1, 0.08)** — **FALSE in general.** A paperclip/TS-`Variable` artifact;
  reversed to best-in-class on both Python repos. Had we stopped at R1 we'd have published a wrong verdict.
- **"serena is barrel-blind" (R1, 0.47)** — **FALSE in general.** Did not reproduce: R2 barrels were perfect
  (1.00), R3 a partial recovery (0.76); serena follows `__init__.py`/`index.ts` re-exports fine when the project
  is resolvable. The most plausible R1 cause was the unbuilt pnpm-workspace `dist/`, but that is **not
  A/B-proven**.
- **serena's overall rank** — **does not transfer** (0.66→0.90→0.74). serena is the most idiom-sensitive tool:
  its recall depends on build state, LSP coverage, and the codebase's import idioms (submodule-alias, two-root
  layouts, abstract methods). High precision (0.90 on DeerFlow) is its constant; recall is the variable.

**This is the entire value of replication: two of R1's most-cited "tool weaknesses" were repo/build artifacts,
and we would have shipped them as general truths from a single-repo study.**

## 4. Practical tool guidance (3-repo evidence)

| tool | use it for | watch out for |
| --- | --- | --- |
| **codegraph** | general-purpose nav default; balanced; JSX | merges same-named symbols (collisions) |
| **CBM** | Python codebases (Class-node models), heavy where-used | **catastrophic on TS Drizzle/member-access data-models (Variable nodes)**; **git-bleed** — verify worktree root |
| **serena** | precision-critical nav; LSP-resolvable React/collision + JSX disambiguation | idiom-sensitive recall; **loses Python-method collisions**; abstract-method blind spot (`find_implementations` errors); build/LSP setup-dependent |
| **ast-grep** | fast exhaustive recall; cross-language-safe (`-l`) | collision-precision collapse; no binding/barrel resolution |
| **repomix** | context-packing whole repos for an LLM | pure lexical; precision erodes with doc/polyglot density; `useGitignore` can hide a snapshot |
| **graphify** | architecture/community overview | **drops secret-named files**; same-file-only method graph; weakest on Python |
| **UA** | lightweight single-root structure maps | file→file granularity; **multi-root resolver gap**; fragile alias parsing |

## 5. Method notes & honesty caveats
- 20 anchors/round across 9 buckets; verdicts require reproduction on ≥2 anchors in a bucket. Method anchors
  (polymorphic) have inherently capped precision — gold = call-site superset (single real def) or
  binding-resolved class-scoped set (collision).
- F1-overall flatters lexical tools; every claim here is grounded in the per-bucket + precision/recall split.
- Collision absolute scores are not cross-round comparable (paperclip's collisions are harder); the **ranking**
  transfers, the absolute numbers do not.
- Each round's gold was Codex-reviewed (R2/R3 also independently Opus-audited) and each round's findings
  adversarially Codex-reviewed; corrections were applied before these numbers were used here. Raw data, golds, scorers: gitignored
  `scratchpad/harness-{paperclip,openhands,deerflow}/`. Per-round detail:
  [paperclip](robustness-findings-paperclip.md) · [OpenHands](robustness-findings-openhands.md) ·
  [DeerFlow](robustness-findings-deerflow.md).

---

*Bottom line: there is no single best tool — there are capability laws. Graph-tool coverage tracks
(extractor × language idiom); binding-resolution buys precision at the cost of idiom-sensitive recall; lexical
buys recall at the cost of collision precision; safety hazards (secret-drop, git-bleed) are tool-intrinsic and
language-independent; and collision disambiguation is unsolved. A single-repo benchmark would have mistaken at
least two build/language artifacts for permanent tool verdicts.*
