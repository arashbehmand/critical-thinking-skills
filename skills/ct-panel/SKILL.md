---
name: ct-panel
description: Replace one roll of the dice with the median of an independent panel - the same canonical question to several fresh subagents, mechanical aggregation by a bundled script, disagreement surfaced instead of averaged away. Use for noisy one-shot judgments - scores, grades, ratings, effort estimates, pick-one decisions - whenever the answer would plausibly differ on a different day.
argument-hint: [the judgment call to panelize]
---

# Judgment panel

The same mind gives different answers on different days — noise, not bias, and a single
draw hides it completely. Panels fix the noise the mechanical way: several independent
draws, arithmetic in the middle, and the spread reported instead of laundered.

## Procedure

1. **Write ONE canonical prompt** (template T4,
   `critical-thinking/references/subagent-templates.md`): the question, every material
   needed to answer it, and the exact output format
   (`ANSWER: <integer 0–10>` / `ANSWER: <option>`). No lean, no draft, no hint.
2. **Spawn N identical fresh panelists.** N = 3 for cheap calls, 5 when it matters.
   *Identical is sacred* — a per-panelist tweak ("you focus on risks…") is a thumb on
   the scale; if you want diverse lenses, that is a different act (run panels per lens
   and report them separately).
3. **Extract the `ANSWER:` lines** verbatim.
4. **Aggregate mechanically — never in your head:**

   ```sh
   python3 skills/ct-panel/scripts/aggregate.py --mode numeric 6 7 4 7 5
   python3 skills/ct-panel/scripts/aggregate.py --mode vote A B A A C
   ```

5. **Read the disagreement flag before the headline number.** High spread or a split
   vote means the question is underspecified (→ `ct-definition-pin`, then rerun) or
   genuinely contested (→ report the split; a 3–2 vote *is* the answer, not a rounding
   problem). Averaging away a bimodal panel manufactures false precision.

## Reporting

Always: *"panel of N, median X, range [a, b]"* — never a bare X. The spread is the
honesty; a stakeholder who sees `7` decides differently than one who sees
`7 (panel range 4–9)`.

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
model family or a human. And nothing proves all draws were reported: machinery would be
a sampling service that logs every draw at the boundary (the shape argLLM's sampling
adapter already has — its concurrency semaphore and call log live server-side precisely
so the pipeline cannot quietly resample). See `docs/critical-thinking-whitepaper.md`.

Part of the critical-thinking set — see the `critical-thinking` skill for routing and
shared conventions.
