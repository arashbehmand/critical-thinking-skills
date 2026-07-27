---
name: ct-assumption-audit
description: Surface the unstated assumptions a claim or plan stands on, rate how load-bearing and how shaky each one is, and attack the weakest load-bearing one first. Use before relying on a conclusion, when a claim "feels obvious", when reviewing a plan or design, or when the user asks "what are we assuming" or "what could make this wrong".
argument-hint: [the claim or plan to audit]
---

# Assumption audit

A claim stands on premises nobody wrote down — and that is where it breaks. Most weak
arguments do not die at the main claim; they die at an assumption its supporters never
noticed they were making. Write the floor down before standing on it.

## Procedure

1. **State the target verbatim** at the top of `.ct/assumptions--<slug>.md`.
2. **Elicit from a fresh mind.** Use template T6
   (`critical-thinking/references/subagent-templates.md`): a subagent that gets the claim
   only — not your lean — lists what must be true for it to hold. The author of an
   argument is the worst-placed person to see its floor; that is why this step is not
   optional.
3. **Add your own pass**, then merge and dedupe. Keep the union: an assumption only one
   pass surfaced is still an assumption.
4. **Rate every assumption on two axes**, one line of reasoning each:
   - **Load-bearing:** if this is false, does the claim fall? `falls / weakens / survives`
   - **Confidence that it holds:** `high / medium / low`
5. **Work the kill zone** — load-bearing + low-confidence. For each item there:
   - name the cheapest check (a source to read, a query to run, a measurement, a person
     to ask);
   - run the checks that are runnable now; record what happened.
6. **Verdict on the target:** `stands` / `stands on conditions` (name the conditions —
   they are the unchecked kill-zone items) / `falls` (name the assumption that broke).

## Artifact

```markdown
# Target: <claim/plan verbatim>

| # | Assumption | If false → | Confidence | Cheapest check | Checked? |
|---|------------|-----------|------------|----------------|----------|
| A1 | users tolerate a second login step | falls | low | support tickets from 2024 SSO change | yes — 40% drop-off |

Kill zone: A1, A4.
Verdict: stands on conditions (A4 unchecked).
```

## Integrity rules

- Include at least one assumption you would *rather not examine*. If every row came out
  high-confidence, the elicitation failed — rerun T6 with the claim restated in its
  least flattering form.
- Rate load-bearing-ness against the claim as stated, not against a retreat position
  ("well, the weaker version still holds") — if you find yourself retreating, record the
  retreat as a new, weaker target and say so.
- Do the audit **before** publicly committing to the claim; an audit after commitment
  inherits the lawyer.

## Limits

None that strictly need machinery: the fresh-mind elicitation covers the worst failure
(the author grading their own floor), and the artifact makes selective rating visible.
Residual risk — generous confidence ratings — is caught downstream when `ct-steelman`'s
advocate or `ct-argument-map`'s contestation attacks the same rows.

Part of the critical-thinking set — see the `critical-thinking` skill for routing and
shared conventions.
