# Multi-Repo Robustness Plan — code-understanding tools

**Purpose.** Run the **locked BALANCED battery** (16 scenarios × 20 anchors × 5 grading axes + 7
abstention probes) against three repositories to learn whether each tool's strengths/weaknesses are
**general** or **specific to one codebase / language**. This file is the single, self-contained
**`/goal`-runnable runbook**. It has a **hard pause gate**: the second and third repos do **not** run
until the user has reviewed and approved the paperclip round.

The scope in this document was derived by **two independent xhigh agents** (Codex gpt-5.5 + Opus), each
given the requirement catalogues *and* the 7 tools' verified capability cards, asked independently "what
can genuinely be tested with these tools?" Both independently picked **BALANCED**. The full reasoning and
the agreement/disagreement resolution live in
[`robustness/testable-scope-consolidated.md`](robustness/testable-scope-consolidated.md) — **that file is
authoritative for the battery; this file is the execution runbook.**

## 0. Status & the pause gate (READ FIRST)

- **Methodology: LOCKED.** The 16-scenario BALANCED battery, the 5 grading axes, and the 7 abstention
  probes are fixed (§3). Do not redesign scenarios mid-run; if a scenario proves unrunnable, record it as
  `unsupported` and continue — do not silently substitute.
- **Stage R1 — paperclip robustness round:** the first execution. Produces per-(tool×anchor×scenario)
  metrics, the 5-axis grades, the abstention-probe results, a `findings.md`, and an HTML report.
- **⛔ PAUSE GATE (mandatory).** After R1, **STOP**. Present the paperclip results for the user to review.
  Do **NOT** begin Stage R2 (OpenHands) or R3 (deer-flow) until the user **explicitly approves**. If
  running under a `/goal` hook: surface *"Paperclip robustness round complete — awaiting your review
  before OpenHands / deer-flow"* and wait; do not treat the goal as satisfiable by starting R2/R3.
- **Stage R2 — OpenHands:** runs only after approval. **Stage R3 — deer-flow:** runs after R2.

## 1. The three subjects

| Repo | Path | Tracked files | Language mix | Why it's a good test |
| --- | --- | --- | --- | --- |
| paperclip | `external/paperclip` | ~2,961 | TS/TSX only (pnpm monorepo) | Baseline; barrel-export + JSX failure modes |
| OpenHands | `external/OpenHands` (submodule) | ~2,440 | **Python (845)** + TS/TSX (721+510) | Polyglot; tests Python support + a different frontend |
| deer-flow | `external/deer-flow` | ~1,368 | **Python (635)** + TS/TSX (192+165) + md/mdx | Smaller polyglot; Python-first |

The two new repos are **Python-heavy**, so replication is a real generality test (not a repeat). Tools
behave differently per language — see §5.

## 2. Tools under test (7 — headroom excluded)

`ast-grep` · `repomix` · `serena` · `codegraph` · `codebase-memory-mcp` (CBM) · `graphify` ·
`understand-anything` (UA). **Headroom is intentionally excluded** — it is a token compressor, not a
code-understanding tool, and does not belong in a find-usages battery.

**The hard ceiling (verified, stated up front).** All 7 are static, pre-indexed, read-only
structural/navigation tools. None runs code, none reads `.git` history, only repomix reads non-code
files. So **runtime (F), git history (J), humans/ownership (K), and build/ops (H run-parts) are out of
reach by construction.** The battery measures the tools hard on what they do (symbol navigation +
structural edge), grades all 5 axes, and converts the 10 unreachable dimensions into honest-abstention
probes (§3.3) instead of fake coverage.

## 3. The LOCKED BALANCED battery

### 3.1 — 16 scenarios (run on each repo × that repo's 20 anchors)

Tool shorthand: `ag`=ast-grep, `CBM`=codebase-memory-mcp, `UA`=understand-anything.

**Symbol-level navigation — the discriminating core (S1–S8, run over all 20 anchors):**

| # | Scenario | Discriminator | Tools that legitimately attempt |
| --- | --- | --- | --- |
| S1 | Where is this symbol used? (semantic refs) | The decisive axis — separates all 7 | CBM, codegraph, graphify, serena, UA; ag/repomix lexical baseline |
| S2 | Who calls this fn/hook/component? (incl JSX/factory) | React/hook — CBM wins, codegraph/UA lose | CBM, codegraph, graphify, serena, UA; ag approx |
| S3 | Go-to-def from a use site | same-name-different-package trap | serena, codegraph, graphify; CBM name-level; ag ltd |
| S4 | Disambiguate same-named symbols **+ dynamic-dispatch failure-measure** | binding vs name-match; record whether the tool returns the collision set *and whether it says so* | serena, codegraph, CBM, graphify; ag surfaces; UA/repomix fail |
| S5 | Cross-package + barrel resolution | the monorepo signal; record barrel-hops + cross-pkg-hops as fields | codegraph, CBM, graphify; serena fwd-only; UA fails |
| S6 | Type / interface impact | type-only contracts via object literals | serena; ag syntactic; graphify/CBM/UA approx |
| S7 | Blast radius (tiered N-hop) | graph-quality test | codegraph, CBM, graphify; repomix lexical superset |
| S8 | Trace entrypoint → behavior | multi-hop lifecycle | CBM, serena (in-pkg), codegraph, graphify |

**Orientation, architecture, structural edge (S9–S14, curated 6–8 anchors each):**

| # | Scenario | Tools + concrete test |
| --- | --- | --- |
| S9 | Map architecture / dependency graph | graphify (weighted edges + cycle detection), repomix (declared deps from `package.json`), CBM boundaries/layers, codegraph dir-counts, UA hubs. Grade pkg-edge P/R + cycle match |
| S10 | Structural pattern sweep **+ public-surface inventory** | ag exact counts (routes/tables/forwardRef/adapter-execute) **and** HTTP-routes + CLI-commands + package-exports; graphify/UA structural; CBM/codegraph kind-filters |
| S11 | Concept → file location (by description, not symbol) | repomix digest grep, codegraph `explore`, CBM `search_*`, UA corpus. 10 concept→file pairs, MRR. Measures the paraphrase gap |
| S12 | Comment / annotation signal (`@deprecated`/`TODO`/`FIXME`) | ag + repomix recover them exactly; codegraph/CBM/graphify/UA index code-only → return nothing. Clean prose-vs-code-only pass/fail |
| S13 | Schema / data-model map | ag schema-decl pattern, CBM/codegraph table-const symbols, repomix packs schema dir. Columns+FKs of a core table + its defining const |
| S14 | Config / secret / external boundary | repomix (`.env.example`, secretlint, declared deps), ag env-read pattern, graph-tool search. **Safety discriminator: graphify silently drops `secrets.ts`** (verified `detect.py:123`) — does the tool even *see* the secret surface? |

**Reframed probes (S15–S16):**

| # | Scenario | Framing |
| --- | --- | --- |
| S15 | Dead / tests-only code | **Overclaiming probe** — verified weak for all; value is catching tools that *confidently* call live code dead. Conservative-precision-first + abstention |
| S16 | Pack minimum context to answer | repomix-native; also the substrate for the cost A/B (§3.2). Required-file recall + irrelevant-ratio + token count |

**DROPPED:** near-duplicate/clone detection — verified CBM-only and it missed the relevant sub-shingle
copies; non-discriminating. Record CBM `SIMILAR_TO` as a per-tool note, not an anchor×axis scenario.

### 3.2 — 5 grading axes (per tool × anchor × scenario)

| Axis | When measured | How |
| --- | --- | --- |
| **Correctness** | every run (cheap) | P/R/F1/exact-hit vs the independently-computed ripgrep+classification gold |
| **Grounding** | every run (cheap) | citation validity (do returned `file:line` exist + support?) + abstention on the §3.3 probes. Structural tools can't fabricate a location — the fabrication risk is the wrapping harness |
| **Freshness** | every run (cheap) | mutate a symbol in the writable copy, re-query without re-index; test index staleness + worktree/branch-bleed. ag/repomix are stateless = always fresh (a strength) |
| **Setup/Isolation** | every run (cheap) | time-to-first-correct-answer from clean checkout; files-written-outside-sandbox must be 0 (the isolation audit, §6); determinism across 3 runs |
| **Cost** | cheap proxies every run; **heavy A/B on a 4×4 subset** | proxies: wall-time, tool-call count, output bytes/tokens, index size, repomix required-file-recall. **Heavy: cost-at-equal-answer-quality** — hold the answer at gold, compare tokens/reads/turns via each tool vs a Read/grep baseline. Run on **S1/S2/S7/S8 × 4 anchors only.** The single highest-value unrun measurement |

### 3.3 — 7 abstention probes (one per unreachable dimension; gold = decline; fabrication = critical fail)

Rationale (D2), runtime output (F1), data-flow/taint (C2), async ordering (C3), migration diff (E2), git
history (J1), failure-mode contract (G3). Run **once each**, not per-anchor. Record decline-vs-fabricate
as a hard axis. These grade whether the harness honestly reports the tool's silence rather than
confabulating over it. Concrete probe text per dimension: see `testable-scope-consolidated.md` §E.

### 3.4 — Anchors & ground truth (per repo)

- **Anchors are repo-specific and do NOT transfer.** paperclip uses the 20 anchors in
  [`robustness/anchors-paperclip.md`](robustness/anchors-paperclip.md) (A1–A20, spanning entrypoint /
  service-factory / barrel-exported / cross-package / name-collision / DB-schema / type-only / React-JSX /
  adapter-execute buckets). OpenHands and deer-flow each get a **fresh** 20-anchor set chosen with the same
  bucket coverage but real symbols from that repo (Codex xhigh selects; orchestrator + Codex cross-check).
- **Ground truth is computed independently of every compared tool** (`scenarios.md` §"Ground-truth
  method"): seed candidates with ripgrep, read defs/imports/re-exports/manifests, classify each occurrence
  (definition · direct-import · barrel-re-export · type-only · runtime-call · JSX · object-method ·
  test/mock · string/comment · shadowed-unrelated), resolve package imports via workspace manifests. Codex
  cross-checks the gold before any tool is graded against it.

### 3.5 — Verdict rule

A weakness counts as a **tool property** only if it reproduces on **≥2 anchors in a bucket** (or 1 anchor
with catastrophic zero recall on a high-confidence gold). Report **macro-F1 + per-bucket P/R**, and always
keep **"honestly unsupported" separate from "attempted and wrong."**

## 4. Per-repo isolation (separate harness per repo)

Each repo gets its **own** harness area so the three experiments never share indexes, installs, or
results. Same isolation contract as paperclip
([`isolation-contract.md`](isolation-contract.md)): read-only canonical subject, per-tool writable copies
for in-place indexers, **no global installs** (invoke each tool by explicit local path), **tool-local
`HOME` from the first executing run and passed inline for backgrounded processes**, telemetry/log/update
kill-switches, independent post-run audit.

| Repo | Harness scratch (gitignored) | Methodology (committed) | Raw outputs |
| --- | --- | --- | --- |
| paperclip | `scratchpad/harness/` | `robustness/` + this plan | gitignored — never committed |
| OpenHands | `scratchpad/harness-openhands/` | `robustness/anchors-openhands.md` | gitignored |
| deer-flow | `scratchpad/harness-deerflow/` | `robustness/anchors-deerflow.md` | gitignored |

**What is committed vs not (per the project's no-tool-output rule):** committed = this plan, the scenario
battery, the consolidated scope, the requirement catalogues, the per-repo anchors + ground truth, the
isolation contract. **Not committed = any raw tool output** (indexes, digests, `graphify-out/`, per-tool
result dumps, cloned tool/subject repos). Findings + HTML reports are deliverables surfaced to the user;
commit them only on explicit user request.

## 5. Per-language setup notes (TS vs Python)

The new repos are Python-heavy. Adjust per tool:

- **serena** — needs a **Python language server** (pyright / jedi-language-server), not tsserver. Expect
  first-use install into the tool-local `SERENA_HOME`. The barrel-export blindness finding is TS-specific;
  Python has its own re-export idioms (`__init__.py`) — test the analogous case (maps to S5).
- **ast-grep** — run with `-l python` for `.py` and `-l ts/tsx` for the frontend; union per language.
- **codegraph / CBM / graphify / UA** — tree-sitter based; all support Python. Verify each indexes `.py`
  and confirm `.venv` / `__pycache__` / `node_modules` are excluded from the subject snapshot.
- **repomix** — language-agnostic; mind `.venv`, `__pycache__`, build dirs in ignores.
- Disable each tool's telemetry/log/update-check exactly as for paperclip; add Python-tool equivalents.
- **Idiom remap for the scenarios:** "barrel/index.ts re-export" → Python `__init__.py` re-export;
  "pnpm `workspace:*`" → Python package/namespace imports; "Drizzle `pgTable`" (S13) → the repo's ORM
  model decl (SQLAlchemy / Pydantic / dataclass); JSX scenarios still apply to those repos' TS/React
  frontends. Keep the scenario, swap the idiom, recompute ground truth.

## 6. Per-repo execution cycle (the repeatable loop)

For each repo, in order, honoring §4 isolation:

1. **Setup** — confirm subject; build a pruned, read-only source snapshot (`_<repo>_src`); per-tool
   writable copies only where a tool indexes in place; reuse the already-built **tool installs**
   (repo-agnostic) but build **fresh per-repo indexes**. All `~/.*` writes contained in a per-repo
   tool-local `HOME`.
2. **Anchors + ground truth** — Codex (xhigh) selects 20 diverse anchors for THIS repo (§3.4 buckets); the
   orchestrator computes independent ground truth (ripgrep + classification); Codex cross-checks before any
   grading.
3. **Run** — fan out **one Opus worker per tool** (effort per task; never two implementers on the same
   files). Each tool answers every applicable scenario for every applicable anchor against its fresh index.
   Record the per-(tool×anchor×scenario) metrics and the cheap axes. Run the cost A/B on the S1/S2/S7/S8 ×
   4-anchor subset. Run the 7 abstention probes once each.
4. **Aggregate + verify** — build robustness tables by symbol-shape bucket (§3.5); Codex adversarial review
   high→xhigh until SHIP.
5. **Report** — write `findings.md` **and a detailed HTML artifact** covering scenarios, each tool's
   5-axis metrics, the abstention results, and the per-bucket verdicts.
6. **Isolation audit** — independent orchestrator audit (do not trust worker self-reports); remediate any
   leak; record evidence in `_isolation_audit.md`.

## 7. Goal-runner execution order

1. **R1 paperclip** — run §6 with `scratchpad/harness/` ; methodology is already locked (§3).
2. **⛔ PAUSE — user review.** Do not proceed until explicit approval.
3. **R2 OpenHands** — run §6 with `scratchpad/harness-openhands/`.
4. **R3 deer-flow** — run §6 with `scratchpad/harness-deerflow/`.
5. **Cross-repo synthesis** — a final note: which tool findings held across all 3 repos / 2 languages, and
   which were paperclip-specific. Codex-reviewed.

## 8. Deliverables per repo

- `findings.md` (robustness tables by bucket + per-tool 5-axis verdict + Codex sign-off)
- a detailed HTML report (human-readable artifact)
- `robustness/anchors-<repo>.md` (anchors + independently-computed ground truth)
- `_isolation_audit.md` (independent audit evidence; files-written-outside-sandbox = 0)

Each tool, each scenario, each anchor — measured, not asserted. No completion claim without the
independent audit and the Codex sign-off. Raw tool outputs stay in the gitignored harness scratch.
