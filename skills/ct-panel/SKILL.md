---
name: ct-panel
description: Measures and cancels the noise in one judgment — sends the identical prompt, with identical material, to several fresh subagents, aggregates their answers with a bundled script, and reports the median or majority together with the spread. Every panelist sees exactly the same thing, with no varied lenses and no varied evidence. Use for a score, grade, rating, effort estimate or pick-one decision that would plausibly come out differently if asked again tomorrow. Not for learning what a conclusion rests on, or for different viewpoints on a body of evidence — that varies what each mind sees, which is ct-ensemble.
argument-hint: [the judgment call to panelize]
---

# Judgment panel

The same mind gives different answers on different days — noise, not bias, and a single
draw hides it completely. Panels fix the noise the mechanical way: several independent
draws, arithmetic in the middle, and the spread reported instead of laundered.

This is not `ct-ensemble`. A panel varies nothing: every panelist gets the identical prompt
and material, and the output is how noisy one judgment is. An ensemble gives each mind a
different slice of the evidence, and the output is what a verdict rests on.

## Procedure

1. **Write ONE canonical prompt** (template T4,
   the `critical-thinking` skill's `references/subagent-templates.md`): the question, every material
   needed to answer it, and the exact output format
   (`ANSWER: <integer 0–10>` / `ANSWER: <option>`). No lean, no draft, no hint.
2. **Spawn N identical fresh panelists.** N = 3 for cheap calls, 5 when it matters.
   *Identical is sacred* — a per-panelist tweak ("you focus on risks…") is a thumb on
   the scale; if you want diverse lenses, that is a different act (run panels per lens
   and report them separately).
3. **Extract the `ANSWER:` lines** verbatim.
4. **Aggregate mechanically — never in your head.** Name who supplied each draw, and for
   numeric panels where the numbers came from:

   `<skill-dir>` is the folder this skill was loaded from; with the `critical-thinking` server connected, its `aggregate_numeric` and `aggregate_vote` tools compute the same results.

   ```sh
   python3 <skill-dir>/scripts/aggregate.py --mode numeric \
     --source opus,opus,sonnet,opus,human --pedigree elicited 6 7 4 7 5
   python3 <skill-dir>/scripts/aggregate.py --mode vote --source opus A B A A C
   ```

   `--source` and `--pedigree` take one value for the whole panel, or one per draw
   comma-separated. An invented draw **at the median position** is refused — that is the
   only place it could move the headline. An invented outlier the median already absorbs
   computes and is stamped, because the median is exactly the instrument that neutralises
   a wild draw; refusing there too would be theatre.

5. **Read the disagreement flag before the headline number.** High spread or a split
   vote means the question is underspecified (→ `ct-definition-pin`, then rerun) or
   genuinely contested (→ report the split; a 3–2 vote *is* the answer, not a rounding
   problem). Averaging away a bimodal panel manufactures false precision.

## Reporting

Always: *"panel of N, median X, range [a, b]"* — never a bare X. The spread is the
honesty; a stakeholder who sees `7` decides differently than one who sees
`7 (panel range 4–9)`.

Carry the script's `Panel:` line too. Five draws from one model and three models plus a
human must not read alike, and only the composition line tells them apart: *"panel of 5
from opus×5 — cancels noise, not shared bias"* is a different claim from *"panel of 5
from opus×3, sonnet, human — 3 independent sources"*.

## Integrity rules

- Your own draft judgment is **not a panelist** — it was formed with context the panel
  is designed to exclude.
- **All N results enter the aggregate.** Dropping a "weird" run after seeing it is
  cherry-picking; if one panelist misread the task, the prompt was ambiguous — fix the
  prompt and rerun the *whole* panel.
- Decide N before spawning. "Best of three… make it five" after seeing results is
  sampling until the dice agree with you.

## Limits

A panel of one model cancels noise, **not shared bias** — the median of five answers
wrong in the same direction is still wrong. For stakes, add a panelist from a different
model family or a human. The `--source` tag moves that caveat out of prose and into the
output, which is the part a skill can actually do; it does not make the tags true, and a
panel labelled `sonnet` that was five more of the same is a lie the script will faithfully
print. And nothing proves all draws were reported: machinery would be
a sampling service that logs every draw at the boundary (the shape argLLM's sampling
adapter already has — its concurrency semaphore and call log live server-side precisely
so the pipeline cannot quietly resample). See `docs/critical-thinking-whitepaper.md`.

Part of the critical-thinking set — see the `critical-thinking` skill for routing and
shared conventions.
