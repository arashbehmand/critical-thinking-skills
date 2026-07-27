# ACH method notes

Adapted from Richards Heuer, *Psychology of Intelligence Analysis* (CIA, 1999), ch. 8.
Heuer designed ACH for exactly the failure this skill targets: analysts settling on the
first satisfying story and then reading every later fact as support for it
(satisficing + confirmation bias).

## Heuer's steps, adapted for an agent

| Heuer | Here |
|---|---|
| 1. Identify all hypotheses (use a group) | fresh subagent proposes a set; merge with yours |
| 2. List significant evidence and arguments | evidence items with source + credibility 1–3 |
| 3. Matrix: evidence vs hypotheses, diagnosticity | independent per-evidence cell raters (T3) |
| 4. Refine — drop non-diagnostic evidence | script flags it; keep it listed, cite it never |
| 5. Tentative conclusions: **disprove**, not prove | ranking by inconsistency, ascending |
| 6. Sensitivity of the conclusion to a few items | script's single-cell flip report |
| 7. Report all conclusions, not just the winner | verdict names runner-up + separating evidence |
| 8. Milestones for future observation | "what evidence would separate the top two" |

Two Heuer points worth keeping verbatim in mind:

- **Evidence consistent with all hypotheses has no diagnostic value.** Most evidence
  people collect is of this kind — it feels like support and decides nothing.
- **The correct conclusion is the hypothesis with the *least evidence against it*.**
  Seeking confirmation instead is the natural, wrong move the matrix exists to block.

## Worked example (toy)

Question: what explains the p99 latency spike at 14:02?

Hypotheses: H1 deploy 4812 regression · H2 traffic surge · H3 db index gone stale.

| Evidence (credibility) | H1 | H2 | H3 |
|---|---|---|---|
| E1 spike began 2 min after deploy (3) | C | N | N |
| E2 request rate flat all afternoon (3) | N | **I** | N |
| E3 slow-query log clean (2) | N | N | **I** |
| E4 rollback restored p99 (3) | C | **I** | **I** |

Inconsistency: H1 = 0, H2 = 3+3 = 6, H3 = 2+3 = 5 → survivor **H1**.

Notice what the matrix did: E1 (the "obvious" clue) is non-decisive — it is merely
consistent, and consistent-with cannot separate stories. The kill shots are E2 and E4,
the *inconsistencies* with the rivals. That inversion — hunting I-cells, not C-cells —
is the whole method.

Sensitivity here: no single cell change makes H3 beat H1 (gap 5, max cell weight 3), so
the lead is cell-robust; the report would say so.
