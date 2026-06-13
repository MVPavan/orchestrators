---
description: Manually annotate gold memories for a scenario (or range) via the enumerate-then-rebuild loop. Synthesizes a fresh proposed gold set from the conversation alone — no extractor output, no matcher, no runs. See docs/plans/manual-gold-review.md.
---

# Annotate Gold Memories

Drives a structured, resumable, scenario-by-scenario **gold-only**
review pass over the validated-50 AlpsBench set. The activity is
**enumerate-then-rebuild**: the reviewer reads everything, enumerates
the canonical situations in their own words, the command both judges
the existing gold against that enumeration AND synthesizes a fresh
proposed gold set, then iterates with the reviewer until approved.

Authoritative spec: [`docs/plans/manual-gold-review.md`](../../docs/plans/manual-gold-review.md).
**If this command and that plan disagree, the plan wins** — sync this
file immediately.

> **What this does:** judge whether each existing gold accurately
> reflects the conversation, then design a clean atomic gold set from
> the same conversation. That's it. No extracted signals, no matcher
> verdict, no F1 deltas, no per-prompt comparison — those are
> downstream analyses run *after* the gold is trusted.
>
> **Command-name note:** historically named `annotate-extraction`
> because gold annotation is the first phase of the broader Dhriti
> review arc (extraction → grounding → promotion audits). The name is
> preserved for stability; the contents are gold-only.

## Argument — always explicit, never "next-N"

The user types one of:

- `/annotate-extraction 5` → annotate **scenario 5 only** (single
  scenario; a bare number is always one scenario, never "next 5")
- `/annotate-extraction 1-5` → annotate scenarios 01 through 05
  (inclusive range)
- `/annotate-extraction 7,12,40` → annotate exactly those three
  scenarios (comma-separated list)
- `/annotate-extraction resume` → continue the most recently
  in-progress scenario without starting a new one
- `/annotate-extraction` (no arg) → **error out** and remind the user
  the command requires an explicit scenario number, range, or list.
  Do NOT auto-pick "next pending".

If the resolved list contains zero scenarios (e.g., all already
`gold_refined` and the user didn't say `resume`), surface that and ask
whether the user wants to **re-refine** the specified IDs (latest
line wins per the idempotency rule).

## Pre-flight (do this every invocation, in order)

1. **Read state.**
   - `experiments/dhriti/manual_gold_review/progress.json` — find each
     scenario's status (`pending` → `in_progress` → `reviewed` →
     `gold_refined`). Note that `gold_refined` is **additive** on top
     of `reviewed`; a scenario already at `reviewed` (legacy
     walk-through) is eligible for advancement to `gold_refined` by
     this command without re-doing prior verdict work.
   - `experiments/dhriti/manual_gold_review/results.jsonl` — per-gold
     verdicts from prior sessions (create empty if missing).
   - `experiments/dhriti/manual_gold_review/proposed_gold/` — any
     already-synthesized gold sets from prior sessions.

2. **Resolve the request.**
   - Parse the argument into a list of scenario indices (1-based).
   - For any already `gold_refined` scenarios in the requested set,
     ask whether to **re-refine** or **skip**.

3. **Announce.**
   - One line per scenario: `[idx] scenario_id  n_gold=N  n_turns=T`
   - That's all — no source extraction, no prompt selection, no
     matcher run.

## Per-scenario loop — 7 steps

Same structure every scenario. The reviewer relies on the consistency
to build muscle memory. Persist after every step that produces data
so a crash never loses progress.

### Step 1 — Present scenario + existing gold

Display the **full conversation** from the trace's
`01_conversation.json` (any run's conversation works — it's the input,
identical across runs since it's the input, not the output), with
turn indices and roles (USER / ASSISTANT). Use markdown blockquotes
so multi-line turns stay readable. Cap at 80 turns; if longer, print
first 40 + last 40 with a clear marker between.

Immediately after the conversation, print **all existing gold
memories** from
`experiments/dhriti/golden_dataset/results/golden_memories_50_validated.jsonl`
for this scenario, numbered `G00..GN-1`, each prefixed with the gold's
`category` and `subject` for quick context.

Format:

```text
G00 [entity      subj=Samiullah Mahaal      ] Samiullah Mahaal is the groom in the marriage affidavit.
G01 [event       subj=Samiullah Mahaal      ] Samiullah Mahaal accepted a Mahaar dower of 300,000 Afghanis...
G02 [task_state  subj=affidavit             ] The affidavit was structured with sections for Personal Information...
```

This is the entire reference surface. The reviewer sees everything
before they enumerate — they can push back on the existing gold's
framing rather than being anchored by it one item at a time.

**Persists:** nothing yet (this step is pure display).

### Step 2 — Ask the reviewer to enumerate situations in their own words

Prompt the reviewer for a free-form summary of the canonical
situations the conversation establishes. No template, no schema — the
reviewer's verbatim text becomes the truth source for Steps 3 and 4.

Suggested prompt shape (adapt tone to the session):

```text
Now in your own words: what are the canonical situations / facts this
conversation establishes? Group them however feels natural. Don't worry
about wording — this is the truth source we'll judge the existing gold
against and rebuild from.
```

**Persists immediately** to
`experiments/dhriti/manual_gold_review/user_enumeration/<NN>_<sid>.md`
— the reviewer's text verbatim, with a small header (`scenario_id`,
`captured_at`, `reviewer`). Atomic write: write to
`<NN>_<sid>.md.tmp` then `mv`. Re-enumeration overwrites; prior
content is preserved by git history, not by file proliferation.

### Step 3 — Analyse existing gold against the enumeration

For each existing gold `G00..GN-1`, derive a verdict from the
enumeration in Step 2:

| value | meaning |
| --- | --- |
| `correct` | gold accurately reflects a situation the reviewer enumerated |
| `partial` | right idea but wrong detail, missing nuance, or over-bundles facts |
| `wrong` | contradicts the conversation or asserts something not enumerated |
| `meta` | true statement *about* the AI-assist transaction (heading edits, formatting requests, "the affidavit was structured with sections for…") that no realistic extractor should produce |
| `duplicate` | semantically the same as another gold in this scenario (specify which in `duplicate_of`) |
| `ambiguous` | enumeration neither clearly supports nor clearly contradicts |

Present the analysis as a table **organized by the reviewer's
situations** (one section per enumerated situation, listing the golds
that map to it), plus an explicit **false-negatives** list: facts in
the enumeration that no existing gold covers.

Format sketch:

```text
== Situation S1: User identity ==
  G05 correct       — name matches enumeration
  G09 partial       — has DOB but missing birthplace from S1
  G14 meta          — describes a heading the assistant wrote

== Situation S2: Marriage event ==
  G00 correct
  G01 correct
  G02 meta          — describes affidavit structure
  G07 duplicate of G01

== False negatives (in enumeration but no existing gold) ==
  - Wedding date (29 Dec 2021)
  - Venue full address
  - Bride as a standalone entity
```

The reviewer confirms or edits each verdict before persistence (batch
in groups of ~5 to avoid input fatigue). Free-text `notes` are
strongly encouraged on every non-`correct` verdict — the one-line
reason future-you will want.

**Persists immediately** to
`experiments/dhriti/manual_gold_review/results.jsonl`, one line per
gold per the schema:

```json
{"scenario_id":"alpsbench:sess_0517169e56bb__4722","memory_idx":3,"verdict":"correct","duplicate_of":null,"notes":"S4: matches the wedding-event situation in the enumeration","reviewer":"human","timestamp":"2026-06-02T00:00:00Z"}
```

Append-only. Re-judging appends a new line; the **latest** line per
`(scenario_id, memory_idx)` wins. Never batch in memory.

### Step 4 — Extract new ground truths from the conversation

Design a fresh, atomic gold set from the conversation, anchored to the
reviewer's enumeration. Rules (apply strictly):

- **Atomic** — one fact per memory; never bundle two assertions.
- **No session-meta** — no facts about the AI-assist transaction
  itself (heading edits, formatting requests, "the affidavit was
  structured with sections for…").
- **No over-extensions** — drop anything the assistant produced that
  the user never asserted.
- **Preserve specific details** — dates, full addresses, amounts,
  proper nouns stay intact; do not paraphrase away precision.
- **Distinguish stable identity facts from current-session task state**
  — `user_fact` / `entity` / `relationship` for stable; `task_state`
  for in-flight work.
- **Categories:** `user_fact`, `user_context`, `relationship`,
  `entity`, `event`, `task_state`.
- **Optional grouping** by `slot` prefix (`A1..A6`, `B1..B3`,
  `C1..C6`, …) for readability — one prefix per situation cluster.

**Persists immediately** to
`experiments/dhriti/manual_gold_review/proposed_gold/<NN>_<sid>.jsonl`
as a single JSONL line matching the canonical example
(`01_sess_0517169e56bb__4722.jsonl`):

```json
{"scenario_id":"alpsbench:sess_…","source":"manual_gold_review/proposed_gold","designed_by":"human-reviewer + claude","designed_at":"YYYY-MM-DD","rationale":"…","memories":[{"slot":"A1","category":"user_fact","subject":"user","memory":"…"}]}
```

Atomic write: `<NN>_<sid>.jsonl.tmp` then `mv`. Whole-file rewrite
each iteration — the proposed gold is a single artifact, not append-
only.

### Step 5 — Present old-vs-new comparison

See the plan ([`docs/plans/manual-gold-review.md`](../../docs/plans/manual-gold-review.md))
for the authoritative `<NN>_<sid>__diff.md` schema. This command
describes only the presentation flow.

Show the reviewer three things, in this order:

1. **Counts.** One line, dense:

   ```text
   counts: 36 → 19 (-17)
     dropped: 13 meta + 2 duplicate + 3 wrong/over-extension
     added:   6 missing facts (wedding date, venue address, office address, birth location, bride standalone, witness attendance)
   ```

2. **Diff table.** Each existing gold mapped to its new equivalent
   slot, or marked `dropped because <reason>`:

   ```text
   G00 → C1        Samiullah groom (kept verbatim)
   G01 → C6        Mahaar dower (rewording for precision)
   G02 → dropped   meta (affidavit structure)
   G07 → dup of C6 dropped as duplicate
   ```

3. **Shape comparison.** Categories breakdown old vs new:

   ```text
   category       old   new   Δ
   user_fact        4     4    0
   user_context     0     1   +1
   relationship     1     1    0
   entity           8     5   -3
   event            5     5    0
   task_state      18     3  -15
   meta            13     0  -13
   ```

**Persists** to
`experiments/dhriti/manual_gold_review/proposed_gold/<NN>_<sid>__diff.md`
— a written file matching the plan's diff template (headline, counts,
category mix, per-gold mapping, and new-no-prior-equivalent). Atomic
write. Whole-file rewrite each iteration.

### Step 6 — Refinement loop

The reviewer can request changes; iterate until they say `good` /
`finalize` / `approved` / `done`. Common operations and their
persistence side-effects:

| reviewer says | action | files touched |
| --- | --- | --- |
| "rename A6 to be more direct" | edit slot in proposed gold | rewrite `proposed_gold/<NN>_<sid>.jsonl` |
| "add a gold for X" | append new memory | rewrite `proposed_gold/<NN>_<sid>.jsonl` |
| "drop D2" | remove memory | rewrite `proposed_gold/<NN>_<sid>.jsonl` |
| "flip G14's verdict to partial" | new verdict line | append to `results.jsonl` |
| "re-cluster the C slots" | edit slot prefixes | rewrite `proposed_gold/<NN>_<sid>.jsonl` |
| "update the enumeration" | edit verbatim text | rewrite `user_enumeration/<NN>_<sid>.md` |

After **every** iteration, refresh `proposed_gold/<NN>_<sid>__diff.md`
to reflect the latest state. Persist before showing the new diff so a
crash never loses an accepted edit. Loop until the reviewer signals
approval; do not auto-approve based on iteration count or elapsed
time.

### Step 7 — Finalize

On explicit approval:

1. **Regenerate `progress.json`** from `results.jsonl` + the presence
   of `proposed_gold/<NN>_<sid>.jsonl` files. Atomic write
   (`progress.json.tmp` → `mv`). Never hand-edit individual fields.
   The scenario advances to `gold_refined` (additive on top of
   `reviewed`).

2. **Write per-scenario findings** at
   `experiments/dhriti/manual_gold_review/findings/<NN>_<sid>.md`.
   Idempotent: re-refining overwrites. Contents:
   - mini-summary (counts old → new, dropped buckets, added facts)
   - verdict distribution from this session
   - qualitative bullets the reviewer flagged
   - pointer line to `proposed_gold/<NN>_<sid>.jsonl` and the diff

3. **Propose a commit.** Print the proposed commit message and the
   exact `git add` invocation, named files only — never `git add .`,
   never autonomous. Adapt the subject to the actual range covered:

   ```text
   experiments/dhriti: manual gold refined — scenario NN
       (or scenarios NN-MM / scenarios NN,MM,QQ for non-contiguous)

   <P> per-gold verdicts recorded, <Q>-memory proposed gold synthesized.
   Headline: <one-sentence finding>.

   Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
   ```

   Named files for staging: `results.jsonl`, `progress.json`,
   `user_enumeration/<NN>_<sid>.md`, `proposed_gold/<NN>_<sid>.jsonl`,
   `proposed_gold/<NN>_<sid>__diff.md`,
   `findings/<NN>_<sid>.md`. **Do not run `git commit` autonomously —
   the user explicitly confirms.**

## End-of-session (after all scenarios in this invocation are done)

Runs whether the invocation covered 1 scenario or many. Same shape
both times.

1. **Print the session summary.** If the invocation covered exactly
   one scenario, this is just the per-scenario mini-summary from
   Step 7. If more than one, print this aggregate:

   ```text
   === Session summary ===
   Scenarios: <list of NN>
   Existing gold reviewed: G   →   Proposed gold designed: G'
     verdicts: correct=A wrong=B partial=C duplicate=D meta=E ambiguous=F
     dropped buckets: meta=M  duplicate=D  wrong/over-extension=W
     added facts:     N

   Notable patterns:
     - <qualitative bullet>
     - <bullet>
   ```

2. **Milestone update.** If the post-session total of `gold_refined`
   scenarios crosses 5 / 10 / 20 / 30 / 50, refresh
   `experiments/dhriti/manual_gold_review/findings/cumulative.md` with
   the cumulative verdict mix, average old→new size delta, and
   recurring qualitative themes across all refined scenarios so far.

3. **Suggest the session commit.** Same shape as Step 7's per-scenario
   commit, but spanning all scenarios this session touched. Stage
   explicit files only. Do not run `git commit` autonomously.

`PROGRESS.md` (the human-readable status table) is **not** regenerated
by this command — it's owned by `build_review_sheets.py`. If the
reviewer wants a refreshed `PROGRESS.md`, they run that separately.

## Idempotency & resume rules

- **`results.jsonl`** is append-only. Re-judging a gold appends a new
  line; the latest line per `(scenario_id, memory_idx)` wins. Earlier
  lines stay for the audit trail.
- **`user_enumeration/<NN>_<sid>.md`**, **`proposed_gold/<NN>_<sid>.jsonl`**,
  and **`proposed_gold/<NN>_<sid>__diff.md`** are whole-file rewrites,
  always atomic (`.tmp` then `mv`). Git history is the audit trail
  for these.
- **`progress.json`** is rebuilt from `results.jsonl` + the presence
  of `proposed_gold/<NN>_<sid>.jsonl`; never edited by hand.
- If the command crashes mid-scenario, all persisted data is already
  on disk. Re-invoking `/annotate-extraction resume` picks up at the
  next unfinished step for that scenario:
  - missing `user_enumeration/<NN>_<sid>.md` → resume at Step 2
  - present enumeration but unfinished `results.jsonl` for that
    scenario → resume at Step 3
  - verdicts complete but no `proposed_gold/<NN>_<sid>.jsonl` →
    resume at Step 4
  - proposed gold present but no `__diff.md` → resume at Step 5
  - diff present but not marked `gold_refined` → resume at Step 6
    (refinement loop)

## OPTIONAL — run-comparison sub-flow

**Off by default.** Only enter this sub-flow if the reviewer
explicitly says something like "evaluate the new gold against run X"
or "compare prompt v9 against the refined gold for scenario 1". The
default 7-step loop **never** touches extractor output.

When invoked:

1. Load the requested run's `03_extracted.json` for the scenario(s).
2. Run the v2 substance matcher from
   `tests/eval/diagnostics/substance_matcher.py` (the `substance_match`
   entry point) against **both** the original validated-50 gold AND
   the new `proposed_gold/<NN>_<sid>.jsonl`.
3. Print per-cell `tp / fp / fn / F1` for both gold sets, with the
   delta. Format:

   ```text
   scenario NN — run X
                       tp   fp   fn   F1
     old gold          17    8   19  0.55
     proposed gold     16    5    3  0.80   (+0.25)
   ```

4. Optionally, on request, drill into per-gold cosine scores and the
   matcher-edge vs honestly-missed decomposition (which proposed-gold
   memories failed to match due to wording-edge vs being absent from
   extraction).

This sub-flow writes **nothing** to disk by default — it is read-only
analysis. If the reviewer wants the comparison persisted, ask before
writing; the canonical location is
`experiments/dhriti/manual_gold_review/run_compare/`.

## What this command will NOT do (default path)

- Run any extractor signal comparison.
- Compute F1 against any run.
- Look at extracted signals, matcher output, or any extractor run.
- Do per-prompt analysis (v8/v9/v10/v11).
- Invoke the matcher.
- Make per-signal grounding or coverage judgments.
- Reference runs, prompts, or signals in any form.
- Run `git commit` / `git push` autonomously. It will only **propose**
  a commit with named files and a message.
- Re-generate the per-scenario sheets (`scenarios/<NN>_<sid>.md`).
  Those are stable artifacts; this command treats them as inputs.
- Touch any later-phase audit data. Phase 2 (grounding) and Phase 3
  (promotion) audits are entirely separate workflows.

If the reviewer asks for any of the above mid-session, decline
politely and point at the run-comparison sub-flow above (for matcher
work) or at the relevant separate plan (for grounding / promotion).
Mixing gold annotation with downstream coverage analysis contaminates
both.

The plan ([`docs/plans/manual-gold-review.md`](../../docs/plans/manual-gold-review.md))
holds the authoritative anti-patterns list — refer to it when in
doubt.

## Failure modes & recoveries

- **Gold JSONL missing for a `scenario_id`** → skip that scenario in
  the session, surface in the session summary, do not write empty
  artifacts.
- **Conversation source missing** (no `01_conversation.json` for the
  scenario) → hard-fail that scenario with a clear pointer to where
  the trace should live; do not invent or partially proceed.
- **Reviewer enumeration is empty / single-word** → ask once for more
  detail; if the reviewer insists it's complete, persist as-is and
  proceed (their call).
- **Schema gap surfaces mid-session** (a verdict category that
  doesn't fit, a new memory category needed) → pause, ask the
  reviewer how to extend the schema, update the plan first via Edit
  on `docs/plans/manual-gold-review.md`, then this file, then resume.
- **Crash mid-scenario** → re-invoke
  `/annotate-extraction resume`; the resume rules above pick up at
  the next unfinished step. No work is lost because every step
  persists before advancing.
- **Reviewer wants to look at extractor output mid-annotation** →
  decline, point at the run-comparison sub-flow, and only enter it
  if they explicitly opt in. Mixing the two contaminates both.
- **Reviewer asks to compute F1 / per-prompt comparisons** → same:
  off-path by default; offer the run-comparison sub-flow as the
  opt-in surface.
