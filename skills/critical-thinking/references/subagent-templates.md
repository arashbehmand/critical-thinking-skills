# Fresh-mind prompt templates

Copy these verbatim, fill the `<placeholders>`, and pass to the Agent tool
(`general-purpose`). Add raw materials (documents, evidence) after the template text.
Never add your draft, your lean, prior scores, or any cue about which answer is wanted —
see conventions.md §2.

## T1 — Advocate (ct-steelman)

> You are the advocate for the following position. It is your side; argue it to win,
> honestly.
>
> Position: <the side, stated affirmatively>
> Question at issue: <the question, verbatim>
>
> Build the strongest honest case: the best arguments, the best available evidence, and
> answers to the two most obvious objections. No strawmen, no hedging, no "some might
> say". Concede nothing you don't have to; invent nothing.
>
> Output: a numbered case, strongest argument first, each argument 2–4 sentences with its
> evidence named. End with the single piece of evidence that would most damage your side
> if it existed — labeled "Exposure:".

## T2 — Blind judge (ct-steelman)

> Two advocates argued opposite answers to the question below. Judge the cases on their
> merits. You do not know who holds which view, and it does not matter.
>
> Question: <verbatim>
> Case 1: <full text of the case listed first — assign labels by alphabetical order of
> the position names, so the assignment is mechanical, not chosen>
> Case 2: <full text>
>
> Output: (a) for each case, its single strongest and single weakest argument, one line
> each; (b) where the cases actually clash — name the crux, the disagreement that decides
> it; (c) which case is stronger as argued, or "split" with what would settle it. Do not
> average politely; pick where the arguments allow.

## T3 — Cell rater (ct-ach)

> You will judge one piece of evidence against several hypotheses. Consider only this
> evidence — no outside knowledge of the case beyond what is written here.
>
> Hypotheses:
> <the full hypothesis list, ids and text>
>
> Evidence <id>: <the single evidence item, verbatim, with its source>
>
> For each hypothesis, output one line: `<hypothesis-id>: C|I|N — <one-line reason>`
> where C = this evidence is consistent with the hypothesis (you'd expect to see it if
> the hypothesis were true), I = inconsistent (you'd be surprised to see it), N = neutral
> (tells you nothing either way). Rate every hypothesis. N is a legitimate answer;
> do not force a lean.

## T4 — Panelist (ct-panel)

> <the canonical question, verbatim, with all materials needed to answer it>
>
> Work independently and end your reply with exactly one line:
> `ANSWER: <value in the required format>`

(The whole panel receives this identical text. Any per-panelist variation is a thumb on
the scale.)

## T5 — Premortem author (ct-premortem)

> It is <horizon date>. The plan below was carried out and it failed badly. Write the
> post-mortem.
>
> Plan (as it stood at the decision date):
> <plan snapshot: goal, steps, owners, dates — nothing about how promising it is>
>
> Output: the top 3–5 causes of failure, most likely first. For each: what specifically
> broke (name the step), and the earliest observable signal that it was breaking. Be
> concrete; "poor communication" is not a cause, "the API contract changed and nobody
> owned updating the client" is.

## T6 — Assumption elicitor (ct-assumption-audit)

> List everything that must be true for the following to hold — especially the things
> its supporters usually do not bother to state.
>
> Claim/plan: <verbatim>
>
> Output: one assumption per line, each concrete and checkable ("users will tolerate a
> second login step", not "users are flexible"). Include unflattering assumptions.
> 5–12 lines.

## T7 — Decomposer (ct-question-tree)

> Break the question below into 2–7 sub-questions such that: each sub-question can be
> answered on its own, and answering all of them settles the original mechanically —
> no overlaps, no gaps.
>
> Question: <verbatim>
>
> Output: the numbered sub-questions, then one line starting "Residue:" naming anything
> in the original that no sub-question covers (or "none").

## T8 — Contradiction reviewer (ct-consistency-log)

> Below are pairs of statements recorded at different times during one piece of work.
> For each pair, say whether they contradict, are in tension (both could be true but
> pull opposite ways), or are compatible.
>
> <numbered pairs>
>
> Output: `<pair-number>: CONTRADICT|TENSION|OK — <one line>` for every pair. Judge only
> what is written; do not guess intent.
