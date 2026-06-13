# Mechanically Checkable Invariants

Status: adopted for v2.7 design docs on 2026-04-07

These are current mechanically checkable project facts for the repo as it exists today.
Promote implementation invariants only after code, manifests, and test config exist.

## [INV-01] Common Design Is The Top Authority

- Statement: `docs/design/v_2_7/core/bodha-design-v2_7.md` is present and marked authoritative.
- Check: `rg -n "^\\*\\*Status:\\*\\* Authoritative$" docs/design/v_2_7/core/bodha-design-v2_7.md`
- Must return: exactly one line
- Why it matters: this is the source of truth when component docs or historical setup files disagree.

## [INV-02] Temporal Replaced The Older Scheduler Model

- Statement: the v2.7 design says Temporal is the sole orchestrator and replaces `async_core.Scheduler`.
- Check: `rg -n "Temporal as sole orchestrator|replaces async_core\\.Scheduler" docs/design/v_2_7/core/bodha-design-v2_7.md docs/design/v_2_7/core/bodha-infrastructure-v2_7.md`
- Must return: one or more matching lines
- Why it matters: the old Bodha setup still assumes the pre-Temporal scheduler model.

## [INV-03] pydantic-settings Replaced OmegaConf

- Statement: the v2.7 design adopts `pydantic-settings` instead of OmegaConf.
- Check: `rg -n "pydantic-settings replaces OmegaConf" docs/design/v_2_7/core/bodha-design-v2_7.md docs/design/v_2_7/core/bodha-infrastructure-v2_7.md`
- Must return: one or more matching lines
- Why it matters: historical Python/config rules that still hard-code OmegaConf are stale.

## [INV-04] PostgreSQL Is The Authoritative Write Boundary

- Statement: Bodha treats PostgreSQL as the authoritative write boundary and source of record.
- Check: `rg -n "Postgres.*(sole authority|source of record|Authoritative write boundary)" docs/design/v_2_7/core/bodha-design-v2_7.md docs/design/v_2_7/core/bodha-chitta-v2_7.md`
- Must return: one or more matching lines
- Why it matters: write-path safety, replayability, and projection discipline all depend on this boundary.

## [INV-05] Tools And Skills Are Registry Infrastructure

- Statement: tools and skills are registry infrastructure, not memory-ledger entries.
- Check: `rg -n "Tools and skills are \\*\\*identity infrastructure\\*\\*" docs/design/v_2_7/core/bodha-tools-skills-v2_7.md`
- Must return: exactly one line
- Why it matters: this keeps capability identity separate from memory storage and Dhṛti write-gate logic.

## [INV-06] Raw Document Chunks Never Enter Citta

- Statement: raw document chunks and verbatim passages do not enter Citta.
- Check: `rg -n "Raw chunks and verbatim passages never enter Citta" docs/design/v_2_7/core/bodha-rag-v2_7.md`
- Must return: exactly one line
- Why it matters: the bookshelf model depends on keeping raw document content external while storing only internalized knowledge and provenance.

## [INV-07] Source Quote Is Mandatory In v2.7 Extraction

- Statement: every ExtractionCandidate must include a `source_quote` field in v2.7.
- Check: `rg -n "Every ExtractionCandidate must include a .source_quote. field|source_quote mandatory" docs/design/v_2_7/core/bodha-design-v2_7.md docs/design/v_2_7/core/bodha-dhriti-v2_7.md`
- Must return: one or more matching lines
- Why it matters: v2.7 extraction grounding depends on verbatim evidence instead of trusting model confidence alone.

## [INV-08] Phase 1.5 Mechanical Verification Is Non-LLM

- Statement: Phase 1.5 grounding verification uses mechanical checks, not LLM calls.
- Check: `rg -n "Phase 1\\.5.*non-LLM|No LLM calls|mechanical verification is non-LLM" docs/design/v_2_7/core/bodha-design-v2_7.md docs/design/v_2_7/core/bodha-dhriti-v2_7.md docs/design/v_2_7/core/bodha-job-plan-v2_7.md`
- Must return: one or more matching lines
- Why it matters: the v2.7 hardening story depends on adding verifiable guardrails rather than another opaque reasoning step.

## [INV-08b] `claim_support` Is The Sole LLM-Generation Call Site In The Post-Grounding Dhriti Pipeline

- Statement: within the post-grounding Dhriti sub-pipeline (`grounding_guard.py`,
  `claim_support.py`, `promotion_gate.py`, `promotion_gate_helpers.py`, `commit.py`),
  `src/bodha/dhriti/claim_support.py` is the only file permitted to invoke an LLM
  *generation* call (chat completion, structured output, judge call) — and only
  inside a function named `judge_call`. Exactly one such call site may exist in
  the file. INV-08 ("no LLM calls in `grounding_guard`") remains unchanged and
  is the narrower invariant inside INV-08b's scope. Embedding queries via
  `Gateway.embed()` are explicitly permitted (deterministic math transform,
  not generation). Files explicitly OUTSIDE this invariant — because LLM
  generation is the whole point of the stage — are `dhriti_agents.py`,
  `signal_capture.py`, and `escalation_repair.py`. `dharana/signal_repair.py`
  is in the `dharana` module and is outside the invariant entirely.
- Check 1 (Stage A gate, already enforced): `pytest tests/invariant/test_authority_boundary.py::test_no_forbidden_llm_calls_in_post_grounding_pipeline`
- Check 2 (Stage B gate, lands with `claim_support.py`): `pytest tests/invariant/test_authority_boundary.py::test_claim_support_has_exactly_one_llm_call_in_judge_call_wrapper`
- Must return: both tests green
- Why it matters: the v2 Schema introduces a per-granularity cosine band where
  `grounding_guard` cannot decide alone. The judge belongs in its own stage
  with its own boundary so future contributors see a single authoritative
  LLM-call site in the post-grounding pipeline. Loosening INV-08 to "no LLM
  in Layer 1, LLM allowed in Layer 2" would split a clean invariant down a
  fuzzy seam; a separate file with its own invariant is the cleaner cut.

## [INV-09] Fabricated Candidates Are Rejected Before Phase 2

- Statement: if grounding fails badly enough, the candidate is rejected before escalation or Phase 2.
- Check: `rg -n "Fabricated candidates are rejected before Phase 2|grounding_score < 0\\.5.*REJECT|automatic \\*\\*REJECT\\*\\*" docs/design/v_2_7/core/bodha-design-v2_7.md docs/design/v_2_7/core/bodha-dhriti-v2_7.md`
- Must return: one or more matching lines
- Why it matters: this is the strongest new v2.7 safeguard against fabricated memories entering the write path.

## [INV-10] verification.md Reflects Repo Reality (No False-Green Gate)

- Statement: while runnable application code exists under `src/bodha/`, the verification-command
  registry `.claude/project/verification.md` must point the completion gate at real code checks — it
  must name the canonical test command (`uv run pytest`) and must NOT carry the obsolete
  "no runnable application code → doc-existence checks" claim. This stops the keystone
  `verification-before-completion` gate from silently rotting back into passing on `test -f` while the
  code is broken.
- Check 1 (real gate present): `test -d src/bodha && rg -n "uv run pytest" .claude/project/verification.md`
- Check 2 (stale claim absent): `rg -n "not runnable application code" .claude/project/verification.md`
- Must return: Check 1 → one or more matching lines; Check 2 → NO matching lines (empty output).
- Why it matters: `verification.md` is the source of truth the `verification-before-completion` skill
  reads to choose the command that proves "done." It went stale once (frozen at the design-only stage,
  contradicting the python rules), turning the accuracy keystone into a false-green hazard. This
  invariant makes that specific rot mechanically detectable by `/check-invariants`.
