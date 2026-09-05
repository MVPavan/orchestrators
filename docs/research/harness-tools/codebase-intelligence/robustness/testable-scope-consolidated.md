# Testable Scope — CONSOLIDATED (Codex gpt-5.5 xhigh ⊕ Opus xhigh, independent)

Two agents were each given the full consolidated report (both requirement catalogues + gap analysis +
14-scenario battery + 20 paperclip anchors) **plus**, for the first time, the 7 tools' real verified
capability cards, and asked the same question independently: **given these 7 specific tools, what can
genuinely be tested?** Neither saw the other's answer. The gap-analysis recommendation was handed to both
only as a *challengeable input*.

- **Codex** → `scratchpad/harness/codex/testable_scope.out` (17-scenario battery; pick BALANCED; 111 cases × 5 axes)
- **Opus** → `testable-scope-opus.md` (15-scenario battery; pick BALANCED; ~900 runs + ~80 A/B + 7 probes)

This file is the merge: where they agree (treat as high-confidence), where they differ (resolved on
evidence), and the single lockable battery + scope.

---

## A. Where they agree — high confidence (independent convergence)

1. **The hard ceiling is identical.** All 7 are static, pre-indexed, read-only structural/navigation tools.
   None runs code, none reads `.git` history, only repomix reads non-code files. So **runtime (F), git
   history (J), humans/ownership (K), and build/ops (H run-parts) are OUT OF REACH by construction** — no
   querying recovers them. Both call this *the headline finding*, not a limitation to pad around.
2. **The gap-analysis "~1–2 of 12 dimensions" framing is slightly *pessimistic*.** Both independently say:
   B (symbol nav) is the strong home turf, but **A (orientation/architecture), and the cheap edge of
   C/D/E/G/I are genuinely testable too** — including three things the 14-scenario battery missed.
3. **Three additions both demand** (each with a named tool that really attempts it, each a clean
   discriminator): **concept→file location**, **comment/`@deprecated` signal**, **schema/data-model map**.
4. **Five-axis grading, with exactly one heavy axis.** Correctness, grounding, freshness, setup/isolation
   are **cheap, single-tool, mostly already captured in the cards**. **Cost-at-equal-quality (L1) is the one
   heavy axis** — it needs an agent-style A/B because the vendor "10×/120× fewer tokens" claims are
   *workflow* comparisons unmeasurable from the CLIs. Both flag it **the single highest-value UNRUN
   measurement**.
5. **OUT-OF-REACH dimensions become honest-abstention probes, not fake scenarios.** For each unreachable
   dimension, run one probe whose gold answer is *decline*; **fabrication = critical failure**. Both note
   the same subtlety: a raw static tool rarely fabricates (it returns `file:line` or nothing) — the
   fabrication risk lives in the **agent/harness wrapping the tool's silence**. So these probes really grade
   *harness honesty*.
6. **Both pick BALANCED scope.** Minimal re-proves B and stops; Maximal over-spends the one heavy axis to
   re-confirm patterns the ≥2-anchors-per-bucket rule already settles.

## B. Where they differ — resolved on evidence

| # | Disagreement | Codex | Opus | Resolution (and why) |
| --- | --- | --- | --- | --- |
| 1 | **Clone / near-duplicate scenario** | KEEP (S10, CBM primary) | **DROP** — verified CBM-only AND it **missed the 4-line `isUuidLike` copies** (below shingle threshold); non-comparative, non-discriminating for this anchor set | **DROP** (side with Opus). Opus's case is evidence-backed: the one duplication that matters in our anchors is exactly what CBM's clone detector misses. Report CBM `SIMILAR_TO` as a per-tool note in findings, not an anchor×axis scenario. Revisit only if a future repo has large duplicated bodies. |
| 2 | **Merge granularity of the symbol-nav core** | Merge old 1+2 (refs+callers) and 3+6 (go-to-def+disambiguation) | Keep 1, 2, 6 **split**; merge only 4+5 | **Keep split** (side with Opus). The battery exists to find where tool *rankings diverge*; refs (S1), callers-incl-JSX (S2), and same-name binding (S4) divide the 7 tools **differently** (e.g. CBM wins JSX callers specifically; disambiguation is a binding test serena passes forward / fails reverse). Merging collapses three distinct rankings into averaged fields. Merge only cross-pkg+barrel (4+5) — those genuinely test one resolution. |
| 3 | **Public-surface inventory** | Standalone scenario (S13) | Folded into A2/C5 | **Fold into the structural sweep (S10)** as an explicit sub-target. S10 already enumerates routes/tables/forwardRef; HTTP-routes + CLI-commands + package-exports is the same structural enumeration. Avoid a near-duplicate scenario. |
| 4 | **Dynamic-dispatch / registry resolution** | Standalone scenario (S15) | Folded as a *measured failure* inside S4/S5 | **Fold into S4** as a graded failure-measure. Both effectively agree it's a failure measurement (tools return the collision set, not the resolved runtime impl); the only question is standalone vs folded. Folding avoids manufacturing coverage for something no tool can actually do. |
| 5 | **Config/secret/external boundary** | Standalone scenario (S17) | Secrets folded into I4 (graphify `secrets.ts` trap), config = locate-only | **Promote to a standalone scenario (S14).** This is the one Codex-only standalone I keep: the verified **graphify silently drops any file named `secrets.ts`** (`detect.py:123`) is a clean, high-value *safety* discriminator ("does the tool even see the secret surface?") that doesn't grade cleanly folded inside another scenario. |

Net: start from Opus's 15, **drop clones**, **add config/secret boundary as standalone** → **16 scenarios**.

---

## C. The locked battery — 16 scenarios

Tool shorthand: `ag`=ast-grep, `CBM`=codebase-memory-mcp, `UA`=understand-anything.

### Symbol-level navigation — Dimension B (the discriminating core)

| # | Scenario | Discriminator / stress anchor | Tools that legitimately attempt |
| --- | --- | --- | --- |
| **S1** | Where is this symbol used? (semantic refs) | The decisive B2 axis — separates all 7 cleanly | CBM, codegraph, graphify, serena, UA; ag/repomix = lexical baseline |
| **S2** | Who calls this fn/hook/component? (incl JSX/factory) | A17/A18/A19 React/hook — CBM wins, codegraph/UA lose | CBM, codegraph, graphify, serena, UA; ag approx |
| **S3** | Go-to-def from a use site | A12/A13 same-name-different-package trap | serena, codegraph, graphify; CBM name-level; ag ltd |
| **S4** | Disambiguate same-named symbols **+ dynamic-dispatch failure-measure** | A16 sibling `execute` — binding vs name-match; record whether tools return the collision set and *whether they say so* | serena, codegraph, CBM, graphify; ag surfaces; UA/repomix fail |
| **S5** | Cross-package + barrel resolution (old 4+5 merged) | The monorepo signal; serena reverse-barrel-blind; record barrel-hops + cross-pkg-hops as fields | codegraph, CBM, graphify; serena fwd-only; UA fails |
| **S6** | Type / interface impact | A11/A14 type-only contracts via object literals | serena; ag syntactic; graphify/CBM/UA approx |
| **S7** | Blast radius (tiered N-hop) | codegraph tiers, CBM Cypher var-length, graphify node-ID | codegraph, CBM, graphify; repomix lexical superset |
| **S8** | Trace entrypoint → behavior | Multi-hop lifecycle; A1 `startServer` | CBM, serena (in-pkg), codegraph, graphify |

### Orientation, architecture, structural edge

| # | Scenario | Requirement | Tools that make it real + test |
| --- | --- | --- | --- |
| **S9** | Map architecture / dependency graph | A4 | graphify (weighted edges + free cycle detection), repomix (declared deps from 41 `package.json`), CBM boundaries/layers, codegraph dir-counts, UA hubs. Grade pkg-edge P/R + cycle-set match |
| **S10** | Structural pattern sweep **+ public-surface inventory** | B8 / C5 | ag exact counts (routes/tables/forwardRef/adapter-execute) **and** HTTP-routes+CLI-commands+package-exports; graphify/UA structural; CBM/codegraph kind-filters |
| **S11** | Concept → file location (by description, not symbol) | A3/D4 | repomix digest grep, codegraph `explore` (verified keyword-not-semantic), CBM `search_*`, UA corpus. 10 concept→file pairs, MRR. Measures the paraphrase gap |
| **S12** | Comment / annotation signal (`@deprecated`/`TODO`/`FIXME`) | D5 | ag + repomix recover them exactly; **codegraph/CBM/graphify/UA index code-only → return nothing.** Clean prose-vs-code-only pass/fail |
| **S13** | Schema / data-model map | E1 | ag `pgTable($$$)`, CBM/codegraph table-const symbols, repomix packs `schema/`. "Columns+FKs of `issues` + defining const" (A7/A8) |
| **S14** | Config / secret / external boundary | I1/I3/I4 | repomix (`.env.example`, secretlint, declared deps), ag `process.env.$K`, graph-tool search. **Safety discriminator: graphify silently drops `secrets.ts`** (verified `detect.py:123`) — does the tool even *see* the secret surface? |

### Reframed probes (kept, re-scoped)

| # | Scenario | Change | Why |
| --- | --- | --- | --- |
| **S15** | Dead / tests-only code | Reframe as **overclaiming probe** | Verified weak for all; value is catching tools that *confidently* call live code dead. Conservative-precision-first + abstention |
| **S16** | Pack minimum context to answer | repomix-native (old scen 14) | repomix's fair task; also the substrate for the L1 cost A/B. Required-file recall + irrelevant-ratio + token count |

**DROPPED:** old scen 13 (near-duplicates/clones) — CBM-only, missed the relevant `isUuidLike` copies, non-discriminating. Per-tool note only.

---

## D. The 5 grading axes (consolidated)

| Axis | Single-tool measurable? | How / heavy? |
| --- | --- | --- |
| **Correctness** | **YES — every run** | P/R/F1/exact-hit vs independent ripgrep+classification gold. Cards already produced these. Cheap. |
| **Grounding** | **YES — every run** | (a) citation validity — do returned `file:line` exist & support? (structural tools can't fabricate a location, only miss/mis-bind). (b) abstention on the OUT-OF-REACH probes. Signal is in (b): grades whether the *harness* reports "tool returned nothing" vs confabulates. Cheap (one-time probe design). |
| **Freshness** | **YES — every run** | Mutate a symbol in the writable copy, re-query without re-index. codegraph/CBM/graphify/serena/UA precompute → test staleness; + worktree/branch-bleed check (verified CBM `detect_changes` read parent repo's diff). ag/repomix stateless → always fresh = a *strength*. Cheap. |
| **Setup/Isolation** | **YES — every run** | Time-to-first-correct-answer from clean checkout (CBM 65s build+3.27s index; codegraph 20s; serena 18s+TS-LS install; graphify 40s; UA 28s+10s; ag/repomix ~0). Files-written-outside-sandbox must be 0 (verified leak audit). Determinism across 3 runs. Cheap — already encoded in isolation contract + `_isolation_audit.md`. |
| **Cost** | **PARTLY — cheap proxies every run; HEAVY version on a subset** | Cheap proxies everywhere: wall-time, tool-call count, output bytes/tokens, index size, repomix required-file-recall + irrelevant-ratio. **HEAVY: cost-at-equal-answer-quality A/B** — hold the answer fixed at gold, compare tokens/reads/turns via each tool vs a Read/grep baseline. **The single highest-value unrun measurement.** Run on a **4-scenario × 4-anchor subset** (S1/S2/S7/S8) only. |

## E. Abstention probes — 7, one per unreachable dimension (gold = decline)

| Dim | Probe | Fabrication = critical fail |
| --- | --- | --- |
| **D2** Rationale | "Why does `prepareCommandManagedRuntime` exist / what does it guard?" (A15) | Invented "guards against race conditions…" with no citation |
| **F1** Runtime | "For CLI `run` with input I, exact stdout + exit code?" | Predicting output it never executed |
| **C2** Data-flow | "Does env `<SECRET>` reach any log/serialize sink?" | Claiming a sink set with no traced edges |
| **C3** Async | "Every emitter/handler pair for event E + is ordering guaranteed?" | Inventing ordering guarantees |
| **E2** Migration | "What did `0066_issue_tree_holds.sql` change + current head?" | Summarizing a diff it cannot compute |
| **J1** History | "Why was the null-guard added to shared `isUuidLike`, which commit?" | Inventing a commit SHA / rationale |
| **G3** Failure-mode | "Storage backend down — throw, retry, or degrade, decided where?" | Asserting a failure contract from static shape |

---

## F. LOCKED scope — BALANCED (both agents' independent pick)

- **Scenarios:** all **16** (S1–S16).
- **Axes:** correctness + grounding + freshness + setup on **every** (tool×anchor×scenario) run (all cheap)
  **+ cost-at-equal-quality A/B on a 4-scenario × 4-anchor subset** (S1/S2/S7/S8) **+ 7 abstention probes**
  (one pass each, not per-anchor).
- **Anchors:** all 20 for symbol-nav S1–S8; curated 6–8 for S9–S16 (architecture/schema/concept/config
  scenarios do not need 20).
- **Verdict rule (unchanged):** a weakness counts only if it reproduces on ≥2 anchors in a bucket (or 1
  anchor with catastrophic zero recall on a high-confidence gold). Report macro-F1 + per-bucket P/R, keep
  "honestly unsupported" separate from "attempted and wrong."
- **Headline cost:** ≈ **900 deterministic tool-runs** (×4 cheap axes each) **+ ~80 heavy cost-A/B runs**
  **+ 7 one-shot abstention probes**. (Codex's independent count: 111 scenario-anchor cases × 5 axes = 555
  axis scores before tool multiplication — same scope, different unit.)

**This is the full honest testable scope for these 7 tools on paperclip.** It tests B hard, measures the
A/C/D/E/G/I structural edge (incl. the failures), grades all 5 axes, runs the one missing cost measurement
bounded, and converts the 10 unreachable dimensions into cheap honesty probes instead of fake coverage.
