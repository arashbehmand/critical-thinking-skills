---
name: ct-ensemble
description: Finds what a conclusion rests on — gives each fresh subagent the same question and hypotheses but a different random slice (about two thirds) of the evidence, votes mechanically, and scores each evidence item by how much seeing it moved the verdict. Needs a set of discrete evidence items and competing answers to choose between. Use when evidence supports more than one reading, to stress-test a conclusion already reached, or for "what is this resting on", "would we still conclude that without X", "other perspectives on this evidence". Not for a noisy score or pick on a fixed prompt with nothing to slice — asking the identical question several times is ct-panel. Not for deciding which of several explanations survives the evidence (that is ct-ach).
argument-hint: [the question, plus the evidence file]
---

# Ensemble of perspectives

A single pass sees everything and commits once — one roll of the dice, and the first
pattern it notices frames the rest. The obvious fix is to split the work up and have
different minds do the pieces. Done wrong, that is worse than not doing it: hand one
agent one line of evidence and it cannot notice that three unrelated readings all point
the same way. You get independence by destroying competence, and independent nonsense
does not average into sense.

Bagging is the shape that works, and it is borrowed rather than invented: a random forest
decorrelates its trees by giving each a *resample* of the data, not a single column. Each
tree stays a real predictor. Here, each agent sees the whole question and every
hypothesis, and about two thirds of the evidence — enough to have a view, different
enough to have its own.

This is not `ct-panel`. A panel sends the identical prompt several times to measure the
noise in one judgment; nothing varies. An ensemble varies the evidence on purpose, and it
needs discrete evidence items to vary — a single judgment with nothing to slice is a panel.

## Procedure

1. **Put the evidence in a file.** Any of these work: an ACH `matrix.json`, a bench
   `instance.json`, or a bare list of `{id, text, source, credibility}`.
2. **Draw the subsets with the script — never by hand:**

   `<skill-dir>` is the folder this skill was loaded from.

   ```sh
   python3 <skill-dir>/scripts/bag.py draw \
     --evidence .ct/ach--<slug>/matrix.json --n 7 --rate 0.65 --seed 1
   ```

   It prints one block per perspective, ready to paste, and guarantees every item is in
   at least one subset and out of at least one — which is what makes step 5 possible.
   Save the machine-readable copy too (`--json > .ct/ensemble--<slug>/draws.json`).
3. **Spawn one fresh agent per subset** (template T10,
   the `critical-thinking` skill's `references/subagent-templates.md`). Each gets the question, the
   full hypothesis list, and **its subset only**. No lean, no other agents' answers, no
   hint that other subsets exist.
4. **Collect the verdicts** into `.ct/ensemble--<slug>/verdicts.json` as
   `[{"subset_id": "S1", "verdict": "H2", "why": "…"}, …]`.
5. **Aggregate mechanically:**

   ```sh
   python3 <skill-dir>/scripts/bag.py aggregate \
     --draws .ct/ensemble--<slug>/draws.json \
     --verdicts .ct/ensemble--<slug>/verdicts.json
   ```

6. **Report the split and the influence table**, not just the winner.

## Reading the influence table

`influence(e)` is the winner's vote share among the perspectives that saw item `e`, minus
its share among those that did not. It is permutation importance, and it answers the
question a reader actually has: *what is this conclusion resting on?*

- **`+1.0`** — every perspective that saw it agreed, none that missed it did. The verdict
  is that one item. Go and verify it against its source before anything else.
- **around `0`** — the verdict does not need it. Common, and a good sign: it means the
  conclusion is carried by the body of evidence rather than by one line.
- **negative** — seeing the item pushed perspectives *away* from the overall winner. Two
  or more of those and the ensemble is genuinely split; treat the plurality as provisional.

This is strictly better than flipping one ACH cell at a time, because it measures effect
on the **verdict** rather than on an intermediate score, and it costs nothing extra once
the perspectives are in.

## Integrity rules

- **The script draws the subsets. You do not.** If you choose who sees what, you picked
  the jury, and the ensemble becomes a way of laundering the answer you wanted.
- **Decide `--n` and `--seed` before you look at any verdict.** Re-rolling the seed after
  seeing a split is sampling until the dice agree with you.
- **Every returned verdict enters the aggregate.** A perspective that reached an odd
  answer on a thin slice is information about the evidence, not a bad draw to discard.
- Do not paste one agent's reasoning into another's prompt. They are decorrelated by what
  they were not shown; sharing reasoning destroys exactly that.
- `--rate` below about 0.5 starts producing agents too thin to be competent, which is the
  failure this act exists to avoid. Above about 0.8 they all see the same thing and you
  have paid for one opinion several times.

## Limits

Same weights, so the perspectives share the model class's blind spots — seven agents
wrong in the same direction still lose the vote to nothing. Subsetting decorrelates over
*evidence*, not over priors. For stakes, draw one perspective from a different model
family or a human and say so in the report.

And the influence number describes **this ensemble**, not the world: it tells you what
the verdict rested on given these draws, which is a fact about your evidence and your
sampling, not proof that the item is true. Verify load-bearing items against their
sources — `ct-entailment` is the act for that.

Part of the critical-thinking set — see the `critical-thinking` skill for routing and
shared conventions.
