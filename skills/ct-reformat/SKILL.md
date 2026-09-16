---
name: ct-reformat
description: Keeps the question and changes only its notation, so that once restated it can be worked out reliably by hand — percentages into natural frequencies (counts out of 1,000), options compared in prose into a table, stacked negations into plain affirmatives, an abstraction into one concrete case. Use when the right question is stated in a way that invites mistakes — base rates and conditional probabilities, several options compared in prose, double negatives, very large or small numbers, vague quantifiers. Not when the question itself may be the wrong one (that is ct-reframe), and not when even a clear restatement still needs a solver, a search or a simulation to answer (that is ct-formalize).
argument-hint: [the awkwardly-stated problem]
---

# Reformat

The difficulty is often in the wording, not the problem: the same question asked in
counts instead of percentages, or as a table instead of prose, is suddenly easy. Minds —
human and model — are format-sensitive. Translate first; then think.

This is not `ct-reframe`, which asks whether the question should change; reformat keeps the
question exactly. Nor is it `ct-formalize`: if the restated problem still needs a solver,
a search or a simulation rather than a page of arithmetic, formalize it instead.

## The translation catalog

| When the problem has… | Translate to… |
|---|---|
| probabilities, base rates, "given that" | **natural frequencies**: "out of 1,000 comparable cases, N are X; of those…" — do the Bayes arithmetic in counts, convert back at the end |
| several options compared in prose | **a table**: rows = options, columns = the *same* attributes for every option; an empty cell is missing information made visible |
| stacked negations ("not unlikely to fail to…") | **an affirmative restatement**: say who does what, positively |
| an abstract claim ("X degrades quality") | **one concrete, fully-specified instance**, checked first; generalize after |
| very large or very small numbers | **human-scale anchors**: per person, per day, per request |
| vague quantifiers ("often", "significant", "most") | **numbers or ranges** — or an explicit flag that no number exists (then consider `ct-definition-pin`) |
| a compound question | **a numbered list of atomic questions** (three or more parts: hand to `ct-question-tree`) |

## Procedure

1. **Before forming any opinion**, pick the translation from the catalog.
2. **Restate faithfully.** The translation must preserve information; if a nuance won't
   survive (a correlation the table can't show, a distribution the range flattens), write
   the loss down next to the restatement.
3. **Solve in the better format.** Frequencies stay frequencies until the last step;
   comparisons happen inside the table.
4. **Translate the answer back** into the asker's terms, keeping the restatement visible
   in the reply so the reader can check the translation — the restatement is the receipt
   for this act (inline; a separate `.ct/` file is optional for long ones).

## Worked micro-example

"Test is 90% accurate, disease hits 1%, you test positive — how worried?"
→ Out of 1,000 people: 10 have it, ~9 test positive; 990 don't, ~99 test positive
anyway. Positive tests: 108, of which 9 real → about 8%. The percentage phrasing invites
the famous wrong answer ("90%!"); the counts make the right one almost automatic.

## Integrity rules

- **Reformat, then think — never think, then reformat to persuade.** A format chosen
  after you have a lean is a rhetorical device; the catalog is chosen by problem shape,
  which is visible before any answer exists.
- Choose the format that makes the problem *clearer*, not the one that makes a preferred
  answer look stronger. If two formats give different intuitions, that tension is a
  finding to report.

## Limits

None that need machinery — this is pure judgment work, and the visible restatement lets
any reader audit the translation. Residual risk (an unfaithful restatement) is exactly
what the visible side-by-side exposes.

Part of the critical-thinking set — see the `critical-thinking` skill for routing and
shared conventions.
