---
name: ct-steelman
description: Build the strongest honest case for the other side using a fresh subagent that has no ownership of the draft, then judge both cases blind. Use before concluding on any contested question; when an argument feels one-sided; when the user says "steelman", "devil's advocate", "what would critics say", or "am I missing something".
argument-hint: [the contested question]
---

# Steelman

Minds argue like lawyers: full effort for their own side, decoration for the other. The
fix is not "try harder to be fair" — ownership poisons counter-effort no matter how hard
you try. The fix is structural: the other side's case is built by a mind that does not
know it is "the other side", and the comparison is judged blind. Production is split;
evaluation — the stronger faculty — carries the verdict.

## Procedure

All templates are in `critical-thinking/references/subagent-templates.md`. Artifact:
`.ct/steelman--<slug>.md`, written in this order — the order is the method:

1. **Pre-register.** Write your current lean and confidence (a number) into the artifact
   **before anything else**. This is preregistration: it makes later movement — or
   suspicious non-movement — visible instead of deniable.
2. **Advocate for the other side** (template T1). Spawn a fresh subagent whose prompt
   contains only: the question verbatim, the position to argue (the side *opposing* your
   lean, stated affirmatively as its own position — never as "the objection to X"), and
   any raw materials. It must not see your lean, your draft, or the word "however".
3. **Advocate for your side** (T1 again, same effort budget, same materials). Do **not**
   substitute your own draft for this case — your draft was not built under advocate
   discipline, and using it breaks the symmetry the judge depends on.
4. **Blind judge** (template T2). A third fresh subagent receives both cases labeled
   Case 1 / Case 2 — assignment by alphabetical order of the position names, so you
   cannot unconsciously put your side first — and reports: strongest/weakest argument of
   each, the crux where they actually clash, and which case is stronger as argued.
5. **Reconcile — this part is yours.** Read both cases and the judgment, then write the
   post-position: *moved* (to what, and which argument moved you) or *held* (and
   specifically why the opposing case's best argument fails). "I hold, and here is the
   flaw in their strongest point" is legitimate. "I hold" alone is not an outcome; it is
   a refusal to engage the exercise.

## Artifact format

```markdown
# Question: …
Pre-registered lean: <position>, confidence <0–1>   ← written first
## Case A (position: …)   ← the side opposing the lean
## Case B (position: …)
## Blind judgment (Case 1 = alphabetically first position)
## Post-position: MOVED to … because … | HELD because their best argument … fails because …
```

## Integrity rules

- The two advocate prompts must be **word-for-word symmetric** except for the position
  line. If you catch yourself writing "briefly consider…" for one side, you are
  lawyering through the prompt.
- No subagent ever sees the pre-registered lean. The judge never learns which side was
  yours — that information has no legitimate use.
- Confidence must move like a number, not a mood: if the judge called it "split", your
  post-confidence should not be 0.95.

## Limits

Discipline, not guarantee: nothing *enforces* that the advocates ran blind, that effort
was symmetric, or that the pre-registration wasn't backdated. Machinery would: a debate
service with hidden channels between isolated contexts, effort accounting per side, and
timestamps on the pre-registration. Also note the same-weights caveat (conventions §2):
both advocates share this model's blind spots — for high stakes, source one case from a
different model family or a human. See `docs/critical-thinking-whitepaper.md`.

Part of the critical-thinking set — see the `critical-thinking` skill for routing and
shared conventions.
