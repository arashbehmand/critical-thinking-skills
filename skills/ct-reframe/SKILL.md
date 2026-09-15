---
name: ct-reframe
description: Challenge whether the asked question is the right problem before solving it — expose the current frame, start from the anomaly it explains worst, generate materially different boundaries and success criteria with a fresh mind, and record what would make each frame wrong. Use when work is stuck, repeated fixes do not touch the problem, an observation does not fit, the question smuggles in a solution or fixed constraint, or a consequential answer may be precise about the wrong target.
argument-hint: [the question or situation to reframe]
---

# Reframe — find the problem before solving it

A precise answer to the wrong question is often worse than an admitted uncertainty. The
original wording silently chooses the target, boundary, unit of analysis, timeframe, and
success criterion; once those choices enter the question, every later tool treats them as
facts. Reframing makes those choices contestable before computation hardens them.

This is not `ct-reformat`. Reformat changes the representation while preserving the
question. Reframe asks whether the question itself should survive.

## Procedure

1. **Separate observation from frame.** Start `.ct/reframe--<slug>.md` with:
   - the asked question, verbatim;
   - raw observations and constraints actually given;
   - the current frame's target, boundary, unit of analysis, timeframe, and success test.

   Do not put proposed causes or solutions in the observation list.
2. **Name the anomaly.** Which observation is least well explained by the current frame,
   most often treated as noise, or requires the most excuses? If there is none, write
   `NO_ANOMALY`; do not invent one to justify the act.
3. **Get frames from an uncommitted mind.** Run template T11 from
   `critical-thinking/references/subagent-templates.md`. It receives the question and raw
   observations only — not your proposed answer. Keep all materially distinct frames it
   returns, including inconvenient ones.
4. **Apply four perturbations yourself**, retaining only results that genuinely change
   the problem:
   - **anomaly-first:** make the unexplained observation the thing to explain;
   - **boundary shift:** move one level up or down — user↔system, component↔interaction,
     event↔process, local↔population;
   - **constraint release:** ask what becomes possible if one apparently fixed constraint
     is a choice rather than a law;
   - **inversion:** replace "how do we achieve X?" with "what reliably prevents X?" or
     "why has X not happened already?".
5. **Test every surviving frame.** Record:
   - what it reveals and what it hides;
   - which evidence would become relevant;
   - one observable `WRONG-IF` condition;
   - whether it changes the available actions, or merely renames them.
6. **Select without collapsing.** Prefer the frame that explains the observations with
   the fewest special excuses and exposes a useful next observation or action. If two
   frames imply materially different actions and current evidence cannot choose, keep
   both and route the disagreement to `ct-question-tree`, `ct-ach`, or a real probe. Do
   not average frames into a vague compromise.
7. **Proceed under the chosen frame**, quoting it at the top of the next artifact. The
   original question remains in the receipt so a reader can see what changed.

## Artifact

```markdown
# Asked question: …
## Raw observations and constraints
## Original frame
Target: …  Boundary: …  Unit: …  Timeframe: …  Success: …
Anomaly: … | NO_ANOMALY

| Frame | Reveals | Hides | New evidence/action | Wrong if |
|---|---|---|---|---|

Selected frame: …
Why: …
Unresolved competing frame: … | none
```

## Integrity rules

- Reframe **before** investing in a solution. A new frame invented only after the old
  answer failed can still be useful, but record that sequence; do not present it as
  foresight.
- A frame must change target, boundary, unit, timeframe, or success criterion. A
  paraphrase is not a frame.
- Do not select by which frame makes the preferred action win. Select by observations,
  explanatory strain, and what becomes testable.
- Releasing a constraint does not prove it is removable. It produces a question to
  check, not permission to ignore reality.

## Limits

Frames are model-generated structures, not exogenous evidence. A fresh context reduces
ownership of the original wording but shares the model class's blind spots. The receipt
makes the choice and its exclusions visible; it cannot guarantee that the missing frame
was generated. For consequential work, an affected human or domain expert is the best
source of a frame the model's training distribution systematically omits.

Part of the critical-thinking set — selected automatically by the `critical-thinking`
controller when the failure signal is a possibly wrong problem rather than a wrong
answer.
