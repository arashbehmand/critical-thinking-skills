---
name: ct-definition-pin
description: Keeps the question and fixes what its load-bearing words mean — pins operational definitions of words like "safe", "better", "fair", "soon", "significant", "done" before arguing or evaluating, so verbal disputes die early instead of poisoning everything after. Use when a question turns on such words; when two sides seem to disagree about facts but might disagree about meanings; or before evaluating anything against criteria. Not when the question itself may be the wrong one (that is ct-reframe).
argument-hint: [the claim or question containing the loaded terms]
---

# Definition pin

Many disagreements are two meanings of one word wearing a single spelling. Argued
unpinned, every step inherits the ambiguity, and both sides can be "right" until the end,
when the dispute reappears intact. Pin the words first; the verbal part of the dispute
dies in minute one.

This is not `ct-reframe`. Pinning keeps the question and fixes what its words mean;
reframing asks whether the question should survive at all.

## Procedure

1. **Find the load-bearing terms.** Two tests, either one qualifies a word:
   - Could two reasonable people apply this word differently to the *same* facts?
   - Would the verdict plausibly change under a different reading?

   Usual suspects: evaluative adjectives (safe, better, fair, robust), vague quantities
   (soon, often, significant, at scale), and category words doing quiet work (breach,
   user, done, production-ready).

2. **Pin each term operationally.** A pin is a decidable test, not a synonym:
   - who/what it applies to, threshold or units, timeframe;
   - one edge case settled explicitly ("a leak with no personal data **is not** a
     'breach' here").

   "Safe" → "no incident requiring disclosure under policy X within 12 months."
   "Better" → "p95 latency lower at equal cost, measured on workload Y."

3. **When the user's intended sense is genuinely ambiguous** and the verdict depends on
   it: ask once. If asking is impossible, pin the most standard sense, and say so in the
   artifact — a visible default beats a silent one.

4. **Lock the glossary.** Every later step uses the pinned sense. If an argument works
   only under a *different* sense, that is a finding — name it as equivocation in the
   output. Do not silently switch senses to make an argument land.

## Artifact

`.ct/definitions--<slug>.md`:

```markdown
| Term | Pinned meaning (decidable test) | Explicitly excluded senses |
|------|--------------------------------|----------------------------|
| safe | no reportable incident under policy X in 12 months | "feels safe", zero-risk |
```

Cite the artifact wherever the terms are used; quote the pinned test when a verdict
hangs on it.

## Integrity rules

- Pin **before** taking a side. A definition introduced mid-argument that happens to
  favor your lean is the exact failure this skill exists to stop — if you must refine a
  pin later, record the old one as superseded and check whether the verdict changed
  with it.
- The pin must be faithful to the asker's intent, not to convenience. When in doubt
  between a strict and a loose sense, evaluate both and report both verdicts.

## Limits

None that need machinery — pinning is judgment work, and the artifact makes drift
visible. The residual risk (a self-serving pin) is caught downstream by `ct-steelman`'s
opposing advocate, who is free to attack the definitions.

Part of the critical-thinking set — see the `critical-thinking` skill for routing and
shared conventions.
