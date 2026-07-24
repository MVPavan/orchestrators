# Robustness Findings — DeerFlow 2.0 (R3: the second Python generality test)

**Round R3 of `multi-repo-robustness-plan.md`.** The same 7 tools × 20 anchors × the S1 symbol-nav
core, on a **second Python-heavy** repo (DeerFlow 2.0: 635 `.py` across two roots `deerflow`@`backend/packages/harness`
+ `app`@`backend`, plus a 357-file Next.js/React frontend). R3 asks: **do the R1→R2 verdicts hold on a
different Python codebase, or were R2's results OpenHands-specific?**

> **Evidence.** Every F1/P/R is a real fresh-index tool run scored against an **independently-computed,
> dual-reviewed binding-resolved gold** (Codex gpt-5.5 xhigh **and** an independent Opus auditor both audited
> it; they converged on one bug, fixed; zero-unaccounted invariant holds exactly on all 17 bind anchors). The
> resolver handles deer-flow's two Python roots (single dotted-form each), the `@/`→`frontend/src` alias, and a
> submodule-alias attr-access binding. Gold md5 `05352aaa`; reconciliation in `_gt/GOLD_REVIEW.md`. Raw data:
> gitignored `scratchpad/harness-deerflow/`.

## 0. Headline — what reproduced across all 3 repos

| Finding (origin) | paperclip | OpenHands | DeerFlow | verdict |
| --- | --- | --- | --- | --- |
| **CBM strong on Python models** (db-schema reversal, R2) | 0.08 ✗ (TS) | 0.95 ✓ | **0.85 ✓** (model_schema 0.97) | **CONFIRMED general on Python** — Pydantic/SQLAlchemy are Class nodes w/ inbound edges; the R1 0.08 was a TS-`Variable` artifact, not a CBM property. Holds on 2 Python repos. |
| **graphify silently drops secret files** (R1) | ✓ | ✓ worse | **✓ REPRODUCED** | 3rd repo: drops 8 files incl. `test_mcp_config_secrets.py`, which references anchor A7 `ExtensionsConfig` → real recall corruption, not just metadata. |
| **graphify method call-graph is same-file-only** (R2) | — | ✓ | **✓ REPRODUCED** | A5/A11/A20 cross-file method callers ≈ 0 → service_method 0.53, A20 `get_tool_config` F1 0.12. |
| **CBM git-bleed (reads parent repo HEAD)** (R1) | ✓ | ✓ | **✓ REPRODUCED** | snapshot has no own `.git`; CBM walked to parent `orchestrators/.git` (`worktree_root=<repo-root>`). |
| **lexical: perfect recall, collision-precision collapse** (R1) | ✓ | ✓ | **✓ REPRODUCED** | ag/rpx recall = 1.00, collision bucket 0.41–0.55; short names (`app`,`Message`,`Sandbox`) noisy. |
| **codegraph balanced-strong, captures JSX** (R1) | ✓ | ✓ | **✓ REPRODUCED** | 0.79 (P0.83/R0.85); barrel-transparent on `__init__.py`; .tsx captured but merges collisions. |
| **serena barrel-blindness reversed** (R2) | 0.47 ✗ | 1.00 ✓ | **0.76 ~ PARTIAL** | **barrel-bucket partial recovery, not renewed blindness** — serena resolves `__init__.py` barrels but misses downstream app/test refs; recall is idiom-sensitive (§3). |

**Net:** the two *safety/robustness* findings (graphify secret-drop, CBM git-bleed) are now **confirmed general
across 3 repos / 2 languages**, and the CBM Python-model strength is **confirmed on both Python repos**. The one
finding that *partially* transferred is serena's barrel-perfection — strong but not 1.00 here.

## 1. The 7-tool matrix — S1 "where is this symbol used?" macro-F1

| scope | ag* | rpx* | ser | cg | CBM | gfy | UA |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **overall (20)** | 0.84 | 0.65 | 0.74 | 0.79 | **0.85** | 0.61 | 0.72 |
| entrypoint (2) | 1.00 | 0.50 | 1.00 | 0.75 | 1.00 | 0.44 | 0.90 |
| service_method (4) | 0.81 | 0.69 | 0.65 | 0.78 | **0.86** | 0.53 | 0.75 |
| barrel_initpy (3) | 1.00 | 0.86 | 0.76 | 0.92 | 0.96 | 0.89 | 0.87 |
| cross_package (5) | 1.00 | 0.88 | 0.70 | 0.98 | 0.98 | 0.75 | 0.83 |
| collision (4) | 0.47 | 0.41 | 0.45 | 0.55 | 0.54 | 0.49 | 0.45 |
| model_schema (3) | 1.00 | 0.95 | 0.57 | 0.86 | **0.97** | 0.53 | 0.79 |
| type_protocol (3) | 0.80 | 0.40 | 0.85 | 0.77 | 0.83 | 0.75 | 0.60 |
| react_jsx (3) | 0.55 | 0.43 | **1.00** | 0.59 | 0.38 | 0.58 | 0.67 |
| dynamic_dispatch (2) | 1.00 | 0.80 | 0.82 | 0.90 | 0.98 | 0.80 | 0.93 |

**Precision vs recall (S1, the story F1 hides):** ag **0.80 / 1.00** · rpx **0.55 / 1.00** · ser **0.90 / 0.67**
· cg 0.83 / 0.85 · CBM **0.89 / 0.88** · gfy 0.71 / 0.67 · UA 0.75 / 0.74. `*` lexical baselines: F1 is
recall-inflated — ast-grep's 0.84 (2nd place) is **R=1.00, P=0.80**; its sharp precision loss is on *collisions*
(A17 0.14, A11 0.40), not overall. **CBM is the genuine winner** (best-balanced 0.89/0.88); **serena has the
highest precision (0.90)** but real recall holes.

## 2. R1 → R2 → R3 trend (overall S1 macro-F1)

| tool | paperclip | OpenHands | DeerFlow | reading |
| --- | --- | --- | --- | --- |
| **CBM** | 0.63 | 0.95 | **0.85** | top on both Python repos; the R1 weakness was TS-specific |
| codegraph | 0.85 | 0.89 | 0.79 | consistently strong & balanced on all 3 |
| ast-grep* | 0.85 | 0.81 | 0.84 | lexical; high F1 is recall-inflation (P=0.80) |
| serena | 0.66 | 0.90 | **0.74** | barrels fixed vs R1, but recall **regressed** R2→R3 (method/collision holes) |
| repomix* | 0.84 | 0.75 | 0.65 | lexical; precision erodes as repos get more polyglot/doc-heavy (P=0.55) |
| UA | 0.57 | 0.66 | **0.72** | best UA round yet, but capped by a cross-root resolver gap (§3) |
| graphify | 0.77 | 0.62 | 0.61 | secret-drop + same-file-only method graph drag it on Python both times |

## 3. New findings, DeerFlow-specific

- **serena uniquely wins the cross-language collision.** A17 `Message` and A18 `WorkspaceHeader` → serena
  **1.00 / 1.00**, the only tool perfect on **both**. On A17 every other tool collapses (ag 0.14 / cg 0.10 /
  CBM 0.12 / rpx 0.05 / UA 0) — serena's LSP is the *only* tool that separates the local `<Message/>` from the
  19 files importing `Message` from `@langchain/langgraph-sdk`. A18 is easier for some (ag/rpx 0.50, cg 0.67,
  UA 1.00) but CBM scores 0.00. React JSX disambiguation on the hard collision (A17) is an LSP-only capability here.
- **serena's recall is idiom-sensitive (precise but holed).** Despite P=0.90, serena returns **`[]` for A5
  `LocalSandbox.execute_command`** and **only the def file for A12 `StreamEvent`**, and just 18/44 for A9
  `AppConfig` — pyright under-resolves specific methods, a collision class, and the submodule-alias/barrel
  re-export chains. This is why serena's **macro-F1 fell 0.90→0.74** from R2 (**macro-recall 0.87→0.67**):
  same tool, recall sensitive to the codebase's import idioms. `find_implementations` was run and **errored** on
  all targets (A11/A14/A15) — the R2 abstract-method blind spot reproduces.
- **UA cross-root resolution gap (a two-root monorepo hazard).** UA's Python resolver walks only the
  *importer's own* ancestor dirs as candidate roots. `deerflow` lives at `backend/packages/harness/` — **not** an
  ancestor of `backend/app/` — so the pervasive `from deerflow.x import N` in `app` code resolves to **0 edges**
  (app-root file-import resolution 29%, vs deerflow-root 66%). This **clearly caps A9** (recall 0.68) and
  **partly A16** (0.86); A10/A20 recall hold (A20's hit is precision/file-granularity, not a recall cap). The
  gap is invisible on a single-root repo.
- **UA frontend `@/` alias dead → React anchors lost.** UA's JSONC comment-stripper mangled
  `frontend/tsconfig.json`, so `@/*→./src/*` never applied; A17 `Message` S1≈0 despite UA capturing the export.
  (codegraph & CBM index `.tsx` fine; ast-grep needs `-l tsx`.)
- **CBM indexes docs (`.md`/`.mdx`) as graph nodes.** `Sandbox`/`AppConfig` appear as nodes in
  `backend/docs/*.md` and frontend `.mdx` content — a mild over-recall source on common names (A1 `app` P drops).
- **The collision bucket is the universal hard floor (0.41–0.55 for all 7).** No tool exceeds 0.55: serena wins
  the React half (A17/A18) but loses the Python-method half (A5/A12); graph/lexical tools merge same-named
  symbols. Collision disambiguation remains unsolved across every tool and every repo.

## 4. Setup / freshness / isolation (this round)

- **Fresh indexes built per tool:** ast-grep stateless · repomix 1,336-file digest · codegraph 1,025 files /
  19.6K nodes / 54K edges · CBM 19.4K-node graph · graphify 20K nodes / 44.5K edges (AST-only, `uv run`) ·
  serena pyright+TS LSP over a subject copy · UA core built + scan/structure/import-map. All confirmed `.py`
  indexed and `.venv`/`__pycache__`/`node_modules`/`.next` excluded (0 leaks).
- **Battery execution note:** a session-limit interruption killed the 7 initial LLM workers mid-run; 6 tools
  were then re-run **deterministically via shell** (reusing each worker's adapted runner) and UA via a worker.
  Per-tool setup bugs found & fixed: repomix packed 0 files until `useGitignore` was disabled (the parent
  repo's `.gitignore` hides `scratchpad/`); codegraph's runner wrapped a bash *function* in `/usr/bin/time`
  (can't exec a function); CBM's built `.db` had to be linked into `$HOME/.cache`; graphify needed `uv run`
  for `networkx`; serena driven via a self-managed streamable-http MCP server.
- **Isolation audit:** R3.8 (separate doc) — codegraph telemetry kill-switch applied; CBM git-bleed is a
  freshness hazard recorded in §0, not a sandbox leak.

## 5. Caveats

- Method anchors (A5/A11/A20) are polymorphic dispatch; gold = call-site superset (single real def, A20
  `get_tool_config`) or binding-resolved class-scoped set (collision, A5/A11). Precision is inherently capped;
  `method_def_sites` lists all same-named real defs.
- F1-overall flatters the lexical tools (ag/rpx recall = 1.00); read per-bucket + the precision split.
- DeerFlow's collisions are milder than paperclip's; absolute collision scores are not cross-round comparable —
  the *ranking* (serena wins React collisions, all tools collapse on method collisions) is what transfers.

---

*Status: gold dual-reviewed + locked (R3.4); battery scored (R3.5); isolation audit clean (R3.8,
[`results/_isolation_audit_R3.md`](results/_isolation_audit_R3.md)); **Codex gpt-5.5 xhigh adversarially
reviewed these findings (R3.6) — verdict applied** (all substance CONFIRMED; scoped the "others collapse ~0.1"
claim to A17 only, relabeled serena's drop as macro-F1 0.90→0.74 / macro-recall 0.87→0.67, narrowed the UA
cross-root cap to A9/A16, sharpened ast-grep's precision loss to collisions). Cross-repo synthesis (which
findings held across paperclip + OpenHands + DeerFlow / TS + Python) is the final deliverable. Raw data, gold,
scorers: gitignored `scratchpad/harness-deerflow/`. Matrix: `scratchpad/harness-deerflow/_gt/scores_matrix.md`.*
