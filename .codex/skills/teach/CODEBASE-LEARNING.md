# Codebase Learning Protocol

Use this protocol when teaching an unfamiliar software repository. The goal is not coverage; it is a source-grounded mental model the learner can explain, trace, challenge, and apply.

## 1. Establish the learning contract

- Record the learner's practical reason for understanding the codebase in `MISSION.md`.
- Freeze the repository path and commit before analysis. Record the analysis date.
- Define what is in scope and explicitly defer adjacent repositories or subsystems.
- Calibrate prior knowledge with one question at a time. Do not assume familiarity from vocabulary alone.

## 2. Keep evidence lanes separate

Maintain three distinguishable evidence classes:

1. **Verified source fact**: confirmed in a specific file, symbol, test, or runtime observation.
2. **Inference**: a reasoned interpretation supported by facts but not directly established.
3. **Open question**: unresolved, contradictory, or requiring an experiment.

When evaluating code-intelligence tools, isolate each tool's index and outputs. Do not let one tool's answer become another tool's ground truth. Build the reference understanding from primary repository sources, then reconcile tool claims against it.

## 3. Build a learning map

Start broad, then follow one real execution path:

- purpose and system boundary;
- packages, modules, and dependency direction;
- entry points and startup;
- one primary request, turn, job, or agent lifecycle;
- state, persistence, and identity;
- integration and extension points;
- operational model, safety boundaries, and failure handling.

Choose repository-specific modules only after the initial map. Prefer central runtime paths over exhaustive file inventories.

## 4. Run the lesson loop

Each lesson should produce one observable gain and use this sequence:

1. **Retrieve**: ask the learner to recall the relevant prior model before showing new material.
2. **Anchor**: show the smallest source-backed trace or diagram that establishes the mechanism.
3. **Explain**: provide a plain-language explanation with jargon removed or immediately defined.
4. **Feynman teach-back**: ask the learner to explain the mechanism as if teaching a capable newcomer.
5. **Diagnose**: identify the first missing link, vague phrase, hidden assumption, or contradiction.
6. **Socratic probe**: ask one question that makes the learner repair the model.
7. **Transfer**: present a changed input, failure, extension, or counterfactual and ask for a prediction.
8. **Consolidate**: update the glossary or a learning record only after evidence of understanding.

Do not answer several probes at once. Wait for the learner's response, give precise feedback, and continue from the first unresolved gap.

## 5. Socratic question types

Select the smallest useful probe:

- **Clarification**: “What exactly do you mean by session state here?”
- **Evidence**: “Which source path or event establishes that claim?”
- **Mechanism**: “What happens between these two components?”
- **Assumption**: “What must be true for this path to work?”
- **Counterexample**: “When would that explanation fail?”
- **Counterfactual**: “If this adapter disappeared, what would change?”
- **Tradeoff**: “Why might the project choose this boundary?”
- **Transfer**: “Where would you make this change, and what else would it affect?”

Questions should reveal reasoning, not reward memorized names.

## 6. Apply mastery gates

Advance only when the learner can do the relevant subset of these without being led:

- explain the concept plainly and use the agreed terminology;
- trace a real path through named components and source evidence;
- distinguish verified fact from inference;
- predict behavior under a changed condition;
- identify at least one limitation or failure mode;
- compare a tool-generated claim with source evidence;
- connect the concept to the mission.

Do not convert confidence or a single quiz score into mastery. Record the demonstrated evidence and any remaining misconception in `learning-records/`.

## 7. Preserve retention

- Begin later lessons with retrieval of earlier concepts.
- Revisit important mechanisms after spacing, using a different example.
- Interleave adjacent concepts only after each is individually understood.
- Mark corrected learning records as superseded rather than deleting the history.
- Keep canonical architecture research separate from learner-specific records so evidence does not become personalized or stale.
