---
name: ct-ach
description: Race competing explanations against the evidence in a matrix - each evidence-hypothesis pair rated by an independent fresh subagent, then a bundled script picks the survivor by least inconsistency and reports which single cell would flip the ranking. Use for "what explains this" questions - debugging a weird failure, diagnosing a metric change, attributing an outage, weighing competing theories - whenever more than one story fits the facts.
argument-hint: [the observation to explain]
---

# ACH — analysis of competing hypotheses

The default failure: we test one story ("is it true?") instead of racing several ("which
fits best?"), so the first decent story wins and every later fact gets bent toward it.
Heuer's fix, built for intelligence analysts: judge each piece of evidence against *all*
hypotheses, and crown the one with the **least evidence against it** — not the most for
it, because almost any story can collect consistent evidence, while inconsistent evidence
is what actually kills.

## Procedure

1. **Write the question** ("what explains X?") into `.ct/ach--<slug>/notes.md`.
2. **Enumerate hypotheses** — 3–7, jointly covering the plausible space, including at
   least one you dislike and, where sensible, "something not yet thought of". Get a fresh
   subagent to propose a set from the question alone (it will name stories you didn't);
   merge with yours. Freeze ids `H1…Hn`.
3. **List evidence** — observable items only (log lines, metrics, documents, testimony),
   each with id `E1…Em`, one-line content, source, and **credibility 1–3**
   (3 = measured/primary, 2 = reliable secondary, 1 = hearsay/uncertain).
4. **Rate cells independently — the honesty core.** For **each evidence item**, spawn a
   fresh cell-rater (template T3, `critical-thinking/references/subagent-templates.md`)
   that sees the full hypothesis list and *that one evidence item only*: `C` (would
   expect to see this if the hypothesis were true), `I` (would be surprised), `N`
   (uninformative). The rater never sees your lean, other evidence, or other ratings —
   so no story momentum can form.
5. **Assemble `matrix.json`** (schema below) and score:

   ```sh
   python3 skills/ct-ach/scripts/ach_score.py .ct/ach--<slug>/matrix.json
   ```

6. **Read the report:**
   - ranking by weighted inconsistency (low = survivor);
   - non-diagnostic evidence (rated the same for every hypothesis) — decoration; it
     supports your favorite exactly as much as everyone else's;
   - **sensitivity**: the single cells that would swap ranks 1↔2 — re-examine exactly
     those ratings and that evidence's credibility before trusting the verdict.
7. **Verdict.** The least-inconsistent hypothesis, stated *with* its remaining
   inconsistencies (a survivor with two I-cells is a lead, not a proof). If the top two
   are within one credibility point, the honest verdict is "undecided between H_a and
   H_b" plus the evidence that would separate them — go get that evidence if it is
   gettable.

## matrix.json schema

```json
{
  "question": "what explains the p99 latency spike on 2026-07-20?",
  "hypotheses": [{"id": "H1", "text": "deploy 4812 regression"}],
  "evidence":   [{"id": "E1", "text": "spike began 14:02, deploy landed 14:00",
                  "source": "grafana", "credibility": 3}],
  "ratings":    [{"evidence_id": "E1", "hypothesis_id": "H1", "rating": "C",
                  "why": "timing matches"}]
}
```

Every (evidence × hypothesis) pair must be rated exactly once; the script refuses
incomplete or duplicated matrices.

## Integrity rules

- **Never delete a hypothesis mid-run.** Mark it eliminated in notes.md with the evidence
  that killed it; the corpse is information.
- Adding new evidence after seeing the ranking is fine — that is how the method is meant
  to breathe. **Re-rating old cells to save a favorite is not**; new ratings go in a new
  `matrix-v2.json` with the change and reason noted, old file kept.
- Evidence consistent with everything (the script flags it) must not be cited in the
  verdict as support for the winner.

## Limits

Cell-rater independence is discipline — nothing proves each cell came from a fresh
context rather than one lawyerly pass. The machinery version is a sibling of the argLLM
server: per-cell elicitation enforced server-side, matrix validated at the boundary,
ranking recomputed per revision. See `docs/critical-thinking-whitepaper.md`; method
details and a worked example in [references/method.md](references/method.md).

Part of the critical-thinking set — see the `critical-thinking` skill for routing and
shared conventions.
