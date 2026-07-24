# Testable Scope — what these 7 tools can honestly be evaluated on (Opus, independent)

**Question answered:** GIVEN the 7 specific tools we will actually run — `ast-grep`, `repomix`,
`serena`, `codegraph`, `codebase-memory-mcp` (CBM), `graphify`, `understand-anything` (UA) — and their
**verified** behavior on paperclip, **what can genuinely be tested?** Not what the requirement
catalogues *wish* were testable; what these deterministic, pre-indexed, static structural tools can
*legitimately attempt*.

**Method.** I read the two requirement catalogues (codex 50, opus A–L/58), the gap analysis (whose
recommendation I treat as one input to challenge, not the answer), `scenarios.md` (14), the paperclip
anchors (20), and — decisively — all 14 capability+exploitation cards plus `findings.md`. Coverage
verdicts below cite the **verified** behavior, not the vendor claim. Where a card proved a tool *fails*
a thing, that is a TESTABLE failure, not OUT OF REACH — measuring the failure is the point.

**The one hard ceiling, stated up front.** All 7 are *static, pre-indexed, read-only structural/navigation
tools.* Verified: none runs code, none reads `.git` history (CBM's `detect_changes` reads a *working-tree
diff*, not history, and bled the parent repo's diff), and only two even read non-code files (repomix packs
everything as bytes; UA's *scanner* classifies docs but its *graph* substrate is code-only). So every
requirement that needs **execution (F), git history (J), humans/ownership (K), or operational reality
(H4/H5/ops)** is OUT OF REACH by construction — no amount of clever querying recovers it. That ceiling is
itself the headline finding and I do not pad around it.

---

## 1. Coverage classification — every requirement, TESTABLE vs OUT OF REACH

Convention: **TESTABLE** = at least one of the 7 can *legitimately attempt* it (I name the tools and the
concrete test). **OUT OF REACH** = no tool here can attempt it; I say what it would actually take. I use
the opus A–L dimensions as the spine (they are the finer-grained 58) and fold each codex requirement (C#)
into the matching dimension so nothing is dropped.

### Dimension A — Orientation & Topology  → **mostly TESTABLE**

| Req | Verdict | Tools + concrete test (verified capability) |
| --- | --- | --- |
| **A1** Scale/composition census (C1 scope, C2 classify) | **TESTABLE** | **repomix** `--token-count-tree`/`--no-files` → file+token mass per dir (verified: `db`=77% of tokens); **UA** scanner → 2951 files by language/category in 0.23s; **codegraph/CBM** `status`/`get_graph_schema` → node counts by kind. Test: "rank top-3 token-heavy dirs + language-per-dir." Generated-vs-handwritten (C6) only *partially*: token-mass flags it, no tool reads generator config. |
| **A2** Entry-point inventory (C4 surfaces) | **TESTABLE (partial)** | **ast-grep** `program.command($$$)` → CLI surface (verified: 9 cli commands); **CBM** has a `Route` node kind (1177); **codegraph** `route` kind (676). Test: "list CLI registrars + HTTP routes." **Caveat to grade:** CBM's `entry_points` view is heuristic and *wrong* (listed `.github/scripts/*`); that wrongness is a gradeable result. |
| **A3** Where-does-X-live by concept (C5 feature→code) | **TESTABLE — and a discriminator** | **repomix** digest grep on concept words; **codegraph** `explore "<concept>"` (verified keyword-matched, *not* semantic — `explore "high-level architecture"` matched symbols literally containing "high"); **CBM** `search_code`/`search_graph` name-regex; **UA** structure corpus. Test: 10 concept→file pairs (e.g. "issue references"→`packages/shared/src/issue-references.ts`), MRR. Expect tools to do well on lexical-overlap concepts, poorly on paraphrase — that gap is the measurement. |
| **A4** Architecture/dependency map (C3 sys map, C9 dep graph) | **TESTABLE — battery scen 10** | **graphify** weighted edges + free cycle detection (verified: `server→db 1731`, real cycles); **repomix** declared-dep map from 41 `package.json` bodies (exact, bounded, 21k tok); **CBM** `boundaries`/`layers`/`clusters`; **codegraph** per-dir counts (no first-class pkg edges); **UA** in-degree hubs (under-counts cross-pkg). Test: pkg import graph edge P/R + cycle-set match. |
| **A5** Naming/layout conventions | **TESTABLE (weak/inferential)** | **ast-grep** `outline` + **UA**/**repomix** tree show test co-location, barrel idiom, dir semantics structurally. No tool *states* the convention; it must be inferred from samples. Gradeable as "does the sampled pattern match the dominant one." |

### Dimension B — Symbol-Level Navigation  → **fully TESTABLE (the home turf)**

| Req | Verdict | Tools + test |
| --- | --- | --- |
| **B1** Go-to-def (C7) | **TESTABLE** scen 3 | **serena** `find_symbol`/`find_declaration` (forward go-to-def works *when installed*, verified retest); **codegraph** `query`/`node`; **graphify**/**CBM** by node/name. Exact `file:line`; the A12/A13 same-name-different-package trap is the discriminator. |
| **B2** Find-all-references semantic (C8) | **TESTABLE — the decisive axis** scen 1 | **CBM** (16/16, 100/100 incl JSX), **codegraph** (cross-pkg, drops 5 UI), **graphify** (15/16, `secrets.ts` drop), **UA** (16/18 by callee-name, import-resolver 0/18), **serena** (~2%, barrel-blind), **ast-grep/repomix** (lexical superset = ripgrep). The single sharpest tool separator in the whole set. |
| **B3** Caller graph incl JSX/factory | **TESTABLE** scen 2 | Same tools; the A17/A18/A19 React/hook anchors are exactly where CBM wins and codegraph/UA lose. |
| **B4** Symbol disambiguation (same name) | **TESTABLE — unanimous binding test** scen 6 | All four graph/LSP tools (serena, codegraph, CBM, graphify) split the 3 `isUuidLike` defs; ast-grep/repomix/UA-name-match cannot bind. A16 (many sibling `execute`) is the stress anchor. |
| **B5** Cross-package / barrel resolution | **TESTABLE — the monorepo signal** scen 4,5 | **codegraph/CBM/graphify** resolve `workspace:*` + barrel 0-config; **serena** forward-only (reverse barrel-blind); **UA** drops `workspace:*`; **ast-grep/repomix** lexical. |
| **B6** Blast radius transitive | **TESTABLE** scen 7 | **codegraph** tiered (`-d1` 159/85, `-d3` 287/138), **CBM** Cypher var-length, **graphify** `affected` by node-ID. Recall ceiling inherited from B2. |
| **B7** Type/interface impact | **TESTABLE** scen 9 | **serena** type-aware; **ast-grep** syntactic type patterns; **graphify/CBM/UA** approximate. A11/A14 (type-only contracts implemented by object literals) is the discriminator. |
| **B8** Structural pattern sweep | **TESTABLE — ast-grep's native turf** scen 11 | **ast-grep** exact counts (512 useEffect, 601 useState, 412 routes); **graphify/UA** structural; **CBM/codegraph** via kind filters. |

### Dimension C — Control & Data Flow  → **partly TESTABLE**

| Req | Verdict | Tools + test / what it needs |
| --- | --- | --- |
| **C1** Entry-to-behavior trace (C10,C11) | **TESTABLE (bounded)** scen 8 | **CBM** `trace_path` depth-5 (verified 96 callees), **serena** clean in-pkg 2-3 hop, **codegraph** cross-pkg w/ name noise, **graphify** 2-hop import trace. Grade ordered-path edit-distance; expect cross-pkg + dynamic hops to break. |
| **C4** Dynamic dispatch / plugin-registry resolution | **TESTABLE — as a measured FAILURE** | A16 `codex-local` adapter `execute`: ask "which concrete `execute` runs for adapter id X?" No tool resolves a string-keyed registry → concrete impl; static go-to-def lands on the interface. **codegraph/CBM** will return the sibling-collision set. Measuring that they *cannot* disambiguate the runtime target — and whether they say so — is the point. |
| **C5** Public-surface/API enumeration | **TESTABLE** | **ast-grep** route/command patterns, **CBM** `Route` nodes, **codegraph** `route` kind. Same as A2; signature-link accuracy is gradeable. |
| **C2** Data-flow / taint trace | **OUT OF REACH** | These are *call* graphs, not *value/dataflow* graphs. None tracks a value through transforms to a sink. Needs dataflow analysis or runtime taint. (Partial proxy: ast-grep can *locate* a config key's read sites lexically, but cannot trace propagation.) |
| **C3** Async / event / concurrency flow | **OUT OF REACH** | Event edges (`emit`→`on`, enqueue→consume) are not call edges. CBM has `EMITS/LISTENS_ON/HANDLES` edge *types* but the cards never verified emitter↔handler pairing or ordering, and ordering/causality needs runtime. Honest-abstention probe only (see §4). |

### Dimension D — Intent, Domain & Rationale  → **one cheap TESTABLE, rest OUT OF REACH**

| Req | Verdict | Tools + test / what it needs |
| --- | --- | --- |
| **D5** Comment/annotation signal (`TODO`/`@deprecated`) | **TESTABLE — cheap, ast-grep-native** | **ast-grep** pattern/regex over comments + **repomix** digest grep recover `@deprecated`/`TODO`/`FIXME` exactly. The one D-requirement structural tools genuinely serve. A tool that *can't* read comments (codegraph/CBM/graphify/UA index code only — they drop comments) **fails outright**, which is a clean discriminator. |
| **D4** Feature→code vertical slice | **TESTABLE (partial, = A3 at multi-layer)** | **repomix** scoped pack assembles a cross-layer slice into one artifact; **codegraph/CBM/UA** can name files per concept. Grade slice recall (shared util + DB schema + route + UI + tests). Tools that index code-only miss the docs/migration parts of the slice — gradeable. |
| **D3** Docs/spec discoverability | **TESTABLE (binary: does it even see docs?)** | Only **repomix** reads `.md`/`AGENTS.md`/`CONTRIBUTING.md` (they're files in the digest); **UA scanner** *classifies* them but the graph ignores them; **codegraph/CBM/graphify/serena** index code only → return nothing. Test: "where is the contributor workflow documented?" — pass/fail on whether the tool indexes docs at all. |
| **D1** Domain vocabulary/glossary (C14) | **OUT OF REACH** | Mapping a domain term to its meaning needs prose/docs/intent synthesis. repomix can *surface* the doc text but does not build a glossary; no tool maps "issue reference mention" to its semantics. Needs an LLM over docs+code. |
| **D2** Rationale / "why" (C16 design rationale) | **OUT OF REACH** | Why code exists lives in commits/PRs/ADRs/comments. No tool reads git; only repomix reads comments (and only as raw bytes). **This is the prime honest-abstention probe** (§4): ask "why does `prepareCommandManagedRuntime` exist?" — a fabricated rationale scores zero. |

### Dimension E — Data Modeling & Persistence  → **schema map TESTABLE, evolution OUT OF REACH**

| Req | Verdict | Tools + test / what it needs |
| --- | --- | --- |
| **E1** Schema / data-model map (C20) | **TESTABLE — Drizzle tables are right there** | **ast-grep** `export const $T = pgTable($$$)` enumerates tables/columns structurally; **CBM/codegraph** index the table consts as symbols; **repomix** packs `packages/db/src/schema/`. Test: "columns + FKs of `issues` table + the defining const" (A7/A8). Structural, legitimately attemptable. |
| **E4** Data lifecycle / write-site set (C21 lineage) | **TESTABLE (partial)** | **CBM/codegraph** callers-of `issueService(db).create` give the write sites *as call edges* (A4 — object-method calls are the hard part, partially recoverable). Grade write-site recall. Full lineage (origin→transform→persist) is C2-shaped → OUT OF REACH. |
| **E3** Serialization / wire-format boundaries | **TESTABLE (weak)** | **ast-grep**/**codegraph** can locate a route handler and its request/response *types*; matching field-sets on both sides is partly structural. Borderline; grade leniently. |
| **E2** Schema evolution / migration history | **OUT OF REACH** | "What did migration 0066 change / what's the latest" needs reading the ordered migration *files' diffs* and applied-vs-pending state. repomix can *pack* the 106 migration files but cannot diff or order-reason them. Needs git/DB state. |

### Dimension F — Runtime & Behavioral  → **entirely OUT OF REACH**

| Req | Verdict | What it needs |
| --- | --- | --- |
| **F1** Observed behavior / execution (C11 control-flow at runtime) | **OUT OF REACH** | Running the code. No tool executes. Pure honest-abstention territory. |
| **F2** Runtime state/lifecycle (C22,C29) | **OUT OF REACH** | Needs a debugger/REPL/instrumentation. Static init-order reading is a weak proxy, not the answer. |
| **F3** Performance/resource profile (C32) | **OUT OF REACH** (one cheap proxy) | Real answer needs profiling. **Cheap static proxy only:** repomix token-mass flags the largest *artifact* (`db`=77%); that is a partial, gradeable sub-answer, not perf. |
| **F4** Logging/observability surface (C30) | **TESTABLE (lexical only)** | **ast-grep** `logger.$M($$$)` / **repomix** grep enumerate log/trace emission sites in a path. Recoverable as a structural sweep; "what each captures at runtime" is not. |

### Dimension G — Contracts & Invariants  → **type contracts TESTABLE, semantic invariants OUT OF REACH**

| Req | Verdict | Tools + test / what it needs |
| --- | --- | --- |
| **G1** Type/signature contracts (C34) | **TESTABLE** | **serena** exact signature/return type (LSP); **codegraph/CBM** symbol signatures (verified CBM gave `isUuidLike` signature). A15 anchor. |
| **G4** Test inventory / test→code map (C36) | **TESTABLE (partial)** | **codegraph** `affected` returns *test files* for changed source; **CBM** has `TESTS_FILE` edges (328); **ast-grep**/test-file naming convention sweeps. Test: "which tests cover `extractIssueReferenceMatches`." Coverage *gaps* and "is the empty-input case tested" need reading assertions → weaker. |
| **G5** Validation/boundary-enforcement points (C25 security boundary) | **TESTABLE (locate-only)** | **ast-grep**/grep can *locate* validation/auth/parse calls in a request path structurally. Whether input is validated *before* a DB write is a flow question (C2-adjacent) → only partial; grade "located the enforcement site," not "proved ordering." |
| **G2** Runtime invariants/preconditions (C35) | **OUT OF REACH (one cheap edge)** | Unstated ordering/idempotency/non-null assumptions. **One cheap exception:** the verified `isUuidLike` finding — the shared copy has a null-guard the 2 cli shadows lack — is recoverable by **serena/CBM/codegraph** *because it surfaced as a binding/disambiguation difference*. General invariant extraction needs comments+runtime → OUT OF REACH. |
| **G3** Error-handling/failure-mode model (C27) | **OUT OF REACH** | "throw vs retry vs degrade when storage is down" needs flow + runtime. ast-grep can locate `catch` blocks lexically; classifying the failure contract it cannot. |

### Dimension H — Build/Run/Test/Debug  → **entirely OUT OF REACH** (except trivial discoverability)

| Req | Verdict | What it needs / thin proxy |
| --- | --- | --- |
| **H1/H2/H3** Build/dev/test reproduction (C28,C37) | **OUT OF REACH** | Running commands. **Thin proxy:** repomix packs `package.json` `scripts` so the *command strings* are visible — but "give the commands that actually build it" verified-by-running is execution. Grade only as "located the scripts," not "build is green." |
| **H4** Debug/repro workflow | **OUT OF REACH** | Execution + fixtures. |
| **H5** CI/CD & release pipeline (C33,C42) | **OUT OF REACH** | repomix can pack `.github/workflows/*.yml` (text); reasoning about gates/release/rollback is not structural. |

### Dimension I — Config, Env & External Boundaries  → **partly TESTABLE**

| Req | Verdict | Tools + test / what it needs |
| --- | --- | --- |
| **I1** Config surface (key set, read sites) (C23) | **TESTABLE (locate), OUT OF REACH (precedence)** | **repomix** packs `.env.example` + config loaders; **ast-grep** `process.env.$K` enumerates env reads. Key set + read sites: testable. *Precedence/override order* and per-env values: needs runtime/deploy config → OUT OF REACH. |
| **I3** External dependency inventory + seams (C24) | **TESTABLE** | **repomix** declared deps from `package.json`; **ast-grep**/graph tools locate the wrapper/boundary (A16: which SDK `codex-local` wraps + where). Boundary-site location is structural. |
| **I4** Secrets/sensitive-surface map (C25) | **TESTABLE — and a known trap** | **ast-grep**/repomix locate secret keys + injection sites; repomix secretlint flags `.env.example`. **The graded trap:** **graphify silently drops any file named `secrets.ts`** (verified `detect.py:123`) — so "does the tool even *see* the secret surface?" is a real recall/safety discriminator. |
| **I2** Env/runtime prerequisites | **OUT OF REACH (locate-only)** | repomix packs Dockerfile/compose/engines text; verifying prereqs needs running. |

### Dimension J — History & Change  → **entirely OUT OF REACH**

| Req | Verdict | What it needs |
| --- | --- | --- |
| **J1** Blame/intent (C16,C43,C45) | **OUT OF REACH** | `.git`. The snapshot is pruned of `.git`; no tool reads history. CBM's `detect_changes` reads a *working-tree diff* and bled the parent repo's — not history. |
| **J2** Churn/hotspot/co-change | **OUT OF REACH** | `git log` frequency. |
| **J3** Idiom evolution (deprecated-vs-current) | **OUT OF REACH (one partial)** | Recency needs git. **Partial:** `@deprecated` markers (D5) flag the deprecated side lexically via ast-grep; "which is *current*" still needs dates/history. |

### Dimension K — Human & Organizational  → **entirely OUT OF REACH** (one file-existence proxy)

| Req | Verdict | What it needs |
| --- | --- | --- |
| **K1** Ownership map (C44) | **OUT OF REACH** | CODEOWNERS + git authorship. (repomix can pack a CODEOWNERS file if present, but paperclip's pruned snapshot/ownership is not structural.) |
| **K2** Contribution rules/guardrails (C49) | **TESTABLE (discoverability only)** | **repomix** packs `AGENTS.md`/`CONTRIBUTING.md` + `scripts/check-*.mjs` → "what does the repo forbid + which script enforces it" is answerable *because the files are in the digest*. Code-only tools fail it. Grade as doc-discoverability, = D3. |
| **K3** Decision artifacts (ADR/RFC/roadmap) | **OUT OF REACH (locate-only)** | repomix locates `ROADMAP.md`/`docs/`; CBM has `manage_adr` (CRUD, not discovery). Summarizing direction is LLM work. |

### Dimension L — Efficiency, Trust, Freshness (cross-cutting)  → **all four TESTABLE as axes** (see §3)

C45 provenance → **L2**; C46 uncertainty → **L2**; C47 cost → **L1**; C48 context-packaging → **L1/repomix scen 14**; C28/L4 setup; C-freshness → **L3**. Handled as the 5 grading axes in §3, not as scenarios.

**Coverage tally (honest):**
- **Strongly TESTABLE:** all of B (8), A1–A4, C1/C4/C5, D5, E1, B8 → the structural core. ~20 requirements.
- **TESTABLE-but-partial / locate-only / failure-measuring:** A5, D3/D4, E3/E4, F4, G1/G4/G5, I1/I3/I4, K2, C4-as-failure. ~15.
- **OUT OF REACH (needs execution / git / docs-synthesis / humans):** all F, all H (run-parts), all J, K1/K3, C2, C3, D1/D2, E2, G2/G3, I2. ~20+.

So the merged picture's "structural tools serve ~1–2 of 12 dimensions well" is **correct on the strong
axis** (B), but slightly *pessimistic*: A, the cheap edge of C/D/E/G/I, and D5 are genuinely attemptable.
The honest framing is: **B fully, A/E1/B8/D5 well, the C4/D2/E2/F/H/J/K edge measured as failure-or-abstention.**

---

## 2. The recommended testable battery (run on paperclip × the 20 anchors)

Principle: keep the 14 where they discriminate, merge the redundant, drop the non-discriminating, add only
scenarios a *named* tool can really attempt. Every scenario below names the tool(s) that make it
non-trivial. **15 scenarios.**

### KEEP (discriminating, well-designed — 10)

| # | Scenario | Why kept (discriminator) | Legit tools |
| --- | --- | --- | --- |
| S1 | Where is this symbol used? (semantic refs) | The decisive B2 axis; separates 7 tools cleanly | ag(lex), serena, codegraph, CBM, graphify, UA |
| S2 | Who calls this fn/hook/component? (incl JSX) | A17/A18/A19 — CBM wins, codegraph/UA lose on JSX | serena, codegraph, CBM, graphify, UA; ag approx |
| S3 | Go-to-def from a use site | A12/A13 same-name-diff-pkg trap | serena, codegraph, graphify; CBM name-level; ag ltd |
| S4 | Disambiguate same-named symbols | A16 sibling `execute`; binding vs name-match | all 4 graph/LSP; ag surfaces; UA/repomix fail |
| S5 | Cross-package / barrel resolution | The monorepo signal; serena reverse-blind | codegraph, CBM, graphify; serena fwd-only; UA fails |
| S6 | Blast radius (tiered N-hop) | codegraph tiers, CBM Cypher, graphify node-ID | codegraph, CBM, graphify; repomix lexical superset |
| S7 | Type/interface impact | A11/A14 type-only contracts | serena; ag syntactic; graphify/CBM/UA approx |
| S8 | Trace entrypoint→behavior | Multi-hop lifecycle; A1 | CBM, serena, codegraph, graphify |
| S9 | Map architecture/dependencies | graphify cycles, repomix declared edges | graphify, repomix, CBM, codegraph, UA |
| S10 | Sweep for structural patterns | ag's native task (routes/tables/forwardRef) | ag, graphify, UA; CBM/codegraph kind-filters |

**Merged into the above:** old scen 4 (cross-package import path) and old scen 5 (barrel resolution) →
**S5** (they test the same `workspace:*`+barrel resolution; running both on the same anchors is redundant —
record barrel-hops and cross-pkg-hops as *fields*, not separate scenarios). Old scen 1 + 2 + 6 stay split
(refs vs callers vs disambiguation genuinely separate the tools differently).

### RECLASSIFY / re-scope (2)

| # | Scenario | Change | Why |
| --- | --- | --- | --- |
| S11 | Find dead / tests-only code | **KEEP but reframe as overclaiming probe** | Verified weak for all (CBM `EXISTS{}` Cypher, codegraph reachability) — value is catching tools that *confidently* call live code dead. Grade conservative-precision-first + abstention. |
| S12 | Pack minimum context to answer | **KEEP, repomix-native** (old scen 14) | repomix's fair task; also the substrate for the L1 cost A/B (§3). Required-file recall + irrelevant-ratio + token count. |

**DROP:** old scen 13 (near-duplicates/clones). Verified CBM-only (`SIMILAR_TO`, 1763 pairs) and it
**missed the 4-line `isUuidLike` copies** (below shingle threshold) — i.e. it does not even serve the one
duplication that matters in this anchor set. It is a single-tool, non-comparative, non-discriminating
capability for *this* battery. Report CBM clone-detection as a per-tool note in findings; do not spend
anchor×axis budget on a scenario only one tool attempts and which misses the relevant case. (If a future
repo has large duplicated bodies, revisit.)

### ADD (testable, a named tool can really do it, the 14 missed — 3)

| # | New scenario | Requirement | Tool that makes it real + concrete test |
| --- | --- | --- | --- |
| S13 | **Concept→file location** | A3/D4 | "Find the code for behavior Y" by *description*, not symbol (10 concept→file pairs). **repomix** digest grep, **codegraph** `explore`, **CBM** `search_*`, **UA** corpus. Discriminator: verified `explore` is keyword-matched not semantic → measures the paraphrase gap. MRR. |
| S14 | **Comment/annotation signal** (`@deprecated`/`TODO`/`FIXME`) | D5 | **ast-grep** (regex/pattern over comments) + **repomix** (digest grep) recover them exactly; **codegraph/CBM/graphify/UA index code-only → return nothing.** Cheap, clean pass/fail discriminator between "reads prose" and "code-only." Exact recall. |
| S15 | **Schema / data-model map** | E1 | "List columns+FKs of the `issues` table + its defining const" (A7/A8). **ast-grep** `pgTable($$$)` pattern, **CBM/codegraph** table-const symbols, **repomix** packs `schema/`. Structural, legitimately attemptable; grade column/FK set match. |

**Deliberately NOT added** (no tool can attempt — measured via §4 abstention probes instead, not as
scenarios): dynamic-dispatch *resolution to the runtime target* (C4 — added only as a failure-measure
*inside S4/S5*, since tools return the collision set, not the resolved impl), data/taint flow (C2), async
event flow (C3), runtime behavior (F), build/run (H), git history (J), ownership (K1). Padding these as
"scenarios" would manufacture fake coverage; the right instrument is one abstention probe per dimension.

**Net battery: 15 scenarios** (10 kept incl. 2 old ones merged into S5, 2 reframed, 3 added, 1 dropped).

---

## 3. The 5 grading axes — what's measurable single-tool vs needs an A/B

| Axis | Measurable on a deterministic single-tool run? | How to measure it cheaply with THESE tools | Heavy? |
| --- | --- | --- | --- |
| **Correctness** (P/R vs gold) | **YES — fully single-tool.** | Per (tool×anchor×scenario): precision/recall/F1 vs the independently-computed ripgrep+classification gold. This is the core and it is cheap — the cards already produced these numbers (CBM 16/16, codegraph 5-UI-miss, graphify `secrets.ts`, serena 2%, UA 16/18). | No |
| **Cost** (L1) | **PARTLY single-tool; the *honest* version needs an A/B.** | *Cheap single-tool proxies (capture now):* wall-time bucket, tool-call count, output bytes/tokens, index size, and **required-file recall + irrelevant-context ratio** for repomix's S12 pack. *Heavy version:* **cost-at-equal-answer-quality** — hold the answer fixed (e.g. S1 at gold) and compare tokens/reads/turns to deliver it via each tool vs a Read/grep loop. **This is the single highest-value UNRUN measurement** (findings §8, both catalogues, Codex top-3). It needs an agent-style A/B because the vendor "10×/120× fewer tokens" claims are *workflow* comparisons, **unmeasurable from the CLIs** (verified for CBM/codegraph/graphify). | **YES — flag it.** |
| **Grounding** (L2) | **YES — single-tool, but needs a designed probe set.** | Two sub-measures, both cheap: (a) **citation validity** — do the `file:line` a tool returns actually exist and support the claim? Trivially checkable since these tools *only* emit `file:line` (good news: structural tools are inherently grounded — they cannot fabricate a location, only miss/mis-bind one). (b) **honest abstention** — inject the OUT-OF-REACH questions (§4) and grade decline-vs-fabricate. The abstention half is where the signal is, because a *static tool* mostly can't fabricate, but the *agent wrapping it* can — so grounding is really about whether the harness reports "tool returned nothing" honestly vs the model confabulating. | No (probe design is one-time) |
| **Freshness** (L3) | **YES — single-tool, but requires a mutate-then-query step.** | Edit a symbol in the **writable copy**, then immediately re-query without re-indexing. Verified-relevant failure modes to test: codegraph/CBM/graphify/serena/UA all use a **precomputed index** — does it auto-sync or go stale? (codegraph watcher lags ~1s, `--no-watch` on WSL2 means manual `sync`; CBM/graphify/UA need explicit re-index.) Plus the **worktree/branch-bleed** check (verified: CBM `detect_changes` read the *parent* repo's diff). ast-grep/repomix are stateless → always fresh (gradeable as a *strength*). | No |
| **Setup/Isolation** (L4) | **YES — fully single-tool, mostly already captured.** | Time-to-first-correct-answer from clean checkout (verified: CBM 65s C build + 3.27s index; codegraph 20s index; serena 18s index + first-use TS-LS npm install; graphify 40s; UA 28s install + 10s; ast-grep/repomix ~0). Files-written-outside-sandbox (must be 0 — verified the codegraph `~/.codegraph` + graphify query-log + serena background-HOME leaks). Determinism across 3 identical runs. The isolation contract + `_isolation_audit.md` already encode this. | No |

**Bottom line on axes:** four of five (correctness, grounding, freshness, setup) are **cheap and
single-tool** and largely already captured in the cards — lock them in for every (tool×anchor×scenario).
The **one heavy axis is cost-at-equal-quality (L1)**, and it is heavy precisely because it requires an
agent-style A/B (deliver the *same correct answer* through tool-X vs a baseline loop, count
tokens/turns). Run the *cheap cost proxies* (time, calls, bytes, required-file recall) everywhere; run the
*equal-quality A/B* on a **small high-value subset** (e.g. S1/S2/S6/S8 × 3–4 anchors), because it is the
measurement the whole experiment is missing and the vendor claims rest on.

---

## 4. Out-of-reach honesty — one abstention probe per unreachable dimension

For each dimension no tool can serve, the *useful* test is not "can it answer" (it can't) but **does the
tool/harness decline, or fabricate a plausible-but-ungrounded answer?** This grades L2 where it bites
hardest. One probe each, with the gold being "honest abstention / no result," and **fabrication = critical
failure**:

| Dim | Single abstention probe (gold = decline/abstain) | What fabrication looks like |
| --- | --- | --- |
| **D2** Rationale | "Why does `prepareCommandManagedRuntime` exist / what failure does it guard?" (A15) — no rationale is in the indexed code | A confident invented "it guards against race conditions in…" with no citation |
| **F1** Runtime | "For CLI command `run` with input I, what is the exact stdout + exit code?" | Predicting output it never executed |
| **C2** Data-flow | "Does the value of env `<SECRET>` reach any log/serialize sink?" | Claiming a sink set with no traced edges |
| **C3** Async | "List every emitter/handler pair for event E and whether handler ordering is guaranteed." | Inventing ordering guarantees |
| **E2** Migration | "What did migration `0066_issue_tree_holds.sql` change, and what is the current head?" | Summarizing a diff it cannot compute |
| **J1** History | "Why was the null-guard added to shared `isUuidLike`, and in which commit?" | Inventing a commit SHA / rationale |
| **G3** Failure-mode | "If the storage backend is unavailable — throw, retry, or degrade — and where decided?" | Asserting a failure contract from static shape |

**Note on a subtlety the cards expose:** a *raw static tool* can rarely fabricate — it returns `file:line`
or nothing (e.g. serena's literal "No symbol declaration found", CBM's `unknown tool: semantic_query`).
The fabrication risk lives in the **model/agent that wraps the tool's empty result**. So these probes are
really a test of the *harness's* honesty about a tool's silence — which is exactly the L2 property both
catalogues flag as decisive for agents. Run each probe once; record decline vs fabricate as a hard axis.

---

## 5. Final scope recommendation — minimal / balanced / maximal

Three honest scopes, defined in terms of THIS testable set, with the resulting **scenario × anchor × axis**
cost so the price is explicit. (20 paperclip anchors; not every scenario applies to every anchor — symbol-
nav scenarios use all 20, structural/architecture scenarios use a curated subset. Counts below are
*tool-runs*, the real cost driver: scenario × applicable-anchors × applicable-tools, graded on the axes.)

### MINIMAL — "prove the discriminator, cheaply"
- **Scenarios:** S1–S8 (the B-axis core) + S9 (architecture) = **9**.
- **Axes:** correctness + setup + freshness only (the 3 fully-cheap single-tool axes); skip the cost A/B and the abstention probes.
- **Anchors:** all 20 for S1–S7; ~6 curated for S8/S9.
- **Cost:** ≈ 8 scenarios × ~17 avg applicable (anchor×tool combos, ~6 tools) ≈ **~800–900 tool-runs**, each graded on 3 axes. No agent A/B.
- **What you lose:** the cost story (the most-demanded number), the prose-reading discriminators (D3/D5/E1), and the abstention/grounding signal. You'd re-confirm B and stop — which findings.md already largely did.
- **Verdict:** too thin. It mostly re-runs what the single-subject experiment proved.

### BALANCED — **RECOMMENDED**
- **Scenarios:** all **15** (S1–S15) — the full B core, architecture, the 3 added structural-edge scenarios (S13 concept→file, S14 comment-signal, S15 schema-map), the 2 reframed (S11 dead-code overclaim, S12 context-pack), minus the dropped clone scenario.
- **Axes:** **correctness + grounding + freshness + setup on every run** (all cheap, mostly already captured) **+ the cost-at-equal-quality A/B on a 4-scenario × 4-anchor subset** (S1/S2/S6/S8) **+ the 7 abstention probes** (run once each, not per-anchor).
- **Anchors:** all 20 for S1–S7; curated 6–8 for S8–S15 (architecture/schema/concept scenarios don't need 20).
- **Cost:**
  - Symbol-nav (S1–S7, S14): ~8 scenarios × 20 anchors × ~6 tools, but each tool only legitimately attempts a subset → **~700 tool-runs** × 4 cheap axes.
  - Architecture/flow/structural (S8–S13, S15): ~7 scenarios × ~7 anchors × ~4 applicable tools → **~200 tool-runs** × 4 cheap axes.
  - Cost A/B: 4 scenarios × 4 anchors × (each tool vs baseline) ≈ **~60–100 agent-style A/B runs** (the only heavy item).
  - Abstention: **7 probes × (decline/fabricate)**, one pass.
  - **Total ≈ 900 deterministic tool-runs (4 cheap axes each) + ~80 heavy A/B runs + 7 probes.**
- **Why this one:** it (a) keeps the rigorous B discrimination the battery was built for, (b) *measures* the structural edge where tools break (concept→file, comment-signal, schema, dead-code overclaim) instead of ignoring it, (c) finally runs the **one measurement everyone flags as missing** (cost-at-equal-quality) but bounds it to a high-value subset so it stays affordable, and (d) converts the 10 unreachable dimensions into 7 cheap honesty probes rather than fake scenarios. It is the smallest scope that produces a defensible, multi-axis, robustness-by-bucket profile.

### MAXIMAL — "everything, every anchor, full A/B"
- **Scenarios:** all 15 **+** re-add the clone scenario as a CBM-only note **+** per-language idiom variants (for the planned OpenHands/deer-flow repos).
- **Axes:** all 5 on **every** run, including the cost A/B across **all** symbol-nav scenarios × all 20 anchors × all tools vs baseline.
- **Cost:** the cost A/B alone explodes to ~8 scenarios × 20 anchors × ~6 tools × baseline ≈ **~900+ agent-style A/B runs** on top of the ~900 deterministic runs. Multiply by 3 for the multi-repo plan.
- **Why not:** the equal-quality A/B is genuinely expensive (it spends model tokens to *measure* model tokens); running it exhaustively buys diminishing signal once the per-bucket pattern is established (the robustness rule already says a finding needs only ≥2 anchors per bucket to count). Maximal burns budget re-proving stable patterns.

### Pick: **BALANCED.**
Rationale, concretely: the **cheap four axes are nearly free** and turn a correctness-only battery into the
multi-axis profile both catalogues demand; the **three added structural scenarios + dropped clone scenario**
fix the battery's real coverage gaps without padding (each new scenario has a named tool that genuinely
attempts it and a clean discriminator); the **cost A/B is the highest-value unrun measurement** so it must
appear, but bounding it to a 4×4 subset keeps it affordable while still covering the buckets that matter
(barrel-exported, JSX, cross-package, entrypoint-trace); and the **7 abstention probes** are the honest,
non-padding way to grade the 10 dimensions structural tools cannot reach — by checking whether the harness
*declines* rather than confabulates. Minimal under-measures (re-proves B and stops); Maximal over-spends on
the one heavy axis to re-confirm patterns the ≥2-anchors-per-bucket rule already settles.

**Resulting headline cost (BALANCED):** 15 scenarios · 20 anchors (subset for non-symbol scenarios) ·
4 cheap axes on every run (~900 deterministic tool-runs) · 1 heavy axis (cost A/B) on a 4-scenario×4-anchor
subset (~80 runs) · 7 one-shot abstention probes. That is the full honest testable scope for these 7 tools
on paperclip.
