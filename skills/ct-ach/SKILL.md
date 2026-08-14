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
4. **Tag origins before rating.** Items that trace back to the *same observation* get the
   same `origin`. A shift-log entry, the summary that copies it, the ticket citing the
   summary and the operator repeating it are **one** observation, not four, and four
   independent credibility weights out of one source is how a matrix manufactures a
   confident wrong survivor. Where the sources are documents, `ct-entailment`'s
   `origins.py` proposes the clusters; the judgment of which are really one observation
   stays yours.
5. **Rate cells independently — the honesty core.** For **each evidence item**, spawn a
   fresh cell-rater (template T3, `critical-thinking/references/subagent-templates.md`)
   that sees the full hypothesis list and *that one evidence item only*: `C` (would
   expect to see this if the hypothesis were true), `I` (would be surprised), `N`
   (uninformative). The rater never sees your lean, other evidence, or other ratings —
   so no story momentum can form.

   **Consider `ct-ensemble` instead, and prefer it unless you specifically need the
   matrix.** One-item raters are maximally uncontaminated and minimally competent: a mind
   holding a single line cannot notice that three unrelated readings all point one way,
   and it costs one agent per evidence item. Measured on a bench instance with a known
   answer, per-item rating placed the true cause **third**; seven bagged perspectives —
   each seeing the whole question and two thirds of the evidence — voted it **first**, at
   a tenth of the calls (`ct-ensemble/references/example.md`). Reach for per-cell rating
   when you want the matrix itself: the flip-cell report, the non-diagnostic list, and a
   cell-level artifact someone can argue with. Reach for the ensemble when you want the
   verdict and to know what it rests on.
6. **Assemble `matrix.json`** (schema below) and score:

   ```sh
   python3 skills/ct-ach/scripts/ach_score.py .ct/ach--<slug>/matrix.json
   ```

7. **Read the report:**
   - ranking by weighted inconsistency (low = survivor);
   - **collapsed origins** — which items were counted once and how many they replaced;
   - non-diagnostic evidence (rated the same for every hypothesis) — decoration; it
     supports your favorite exactly as much as everyone else's;
   - **sensitivity**: the single cells that would swap ranks 1↔2 — re-examine exactly
     those ratings and that evidence's credibility before trusting the verdict. A cell
     inside a collapsed cluster will rarely appear here, and that is the correct answer:
     with a sibling still carrying the origin, that cell never decided anything.
8. **Verdict.** The least-inconsistent hypothesis, stated *with* its remaining
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
                  "source": "grafana", "credibility": 3},
                 {"id": "E2", "text": "on-call recalls the queue backing up",
                  "source": "handover note", "credibility": 2, "origin": "og-shift-log"},
                 {"id": "E3", "text": "postmortem draft repeats the queue backup",
                  "source": "postmortem", "credibility": 2, "origin": "og-shift-log"}],
  "ratings":    [{"evidence_id": "E1", "hypothesis_id": "H1", "rating": "C",
                  "why": "timing matches"}]
}
```

Every (evidence × hypothesis) pair must be rated exactly once; the script refuses
incomplete or duplicated matrices. `origin` is optional — an item without one is its own
origin, so a matrix that never uses the field scores exactly as it always did. Items that
share one contribute **the credibility of their best-evidenced I-rated member, once**.

## Integrity rules

- **Never delete a hypothesis mid-run.** Mark it eliminated in notes.md with the evidence
  that killed it; the corpse is information.
- Adding new evidence after seeing the ranking is fine — that is how the method is meant
  to breathe. **Re-rating old cells to save a favorite is not**; new ratings go in a new
  `matrix-v2.json` with the change and reason noted, old file kept.
- Evidence consistent with everything (the script flags it) must not be cited in the
  verdict as support for the winner.
- Tag origins **before** rating, not after seeing which way the ranking went. And if two
  items you tagged as one origin end up rated differently against the same hypothesis,
  they were not restatements of one observation — retag, or explain in notes.md why both
  stand.

## Limits

Cell-rater independence is discipline — nothing proves each cell came from a fresh
context rather than one lawyerly pass. The machinery version is a sibling of the argLLM
server: per-cell elicitation enforced server-side, matrix validated at the boundary,
ranking recomputed per revision. See `docs/critical-thinking-whitepaper.md`; method
details and a worked example in [references/method.md](references/method.md).

Part of the critical-thinking set — see the `critical-thinking` skill for routing and
shared conventions.
