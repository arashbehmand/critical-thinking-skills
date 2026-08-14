---
name: ct-calibration
description: Keep score on stated probabilities - log consequential predictions with a number and a resolve-by date, resolve them when truth arrives, and read the Brier scorecard to see systematic over- or under-confidence. Use when stating probabilities that matter later, forecasting outcomes ("this migration finishes by...", "this fix resolves the bug"), or when the user asks "how confident are you really".
argument-hint: [the prediction to log, or "report"]
---

# Calibration scorecard

Confidence grows without accuracy when nobody keeps score. Weather forecasters are
almost perfectly calibrated for one reason: fast, unambiguous feedback, every day. This
skill builds that loop where the world doesn't provide it — every consequential
probability gets logged, resolved, and scored, so "when I say 80%" eventually has a
measured answer.

## Procedure

1. **Log at statement time.** When a probability that matters leaves your mouth:

   ```sh
   python3 skills/ct-calibration/scripts/brier.py add \
     --file .ct/predictions.jsonl \
     --q "the retry fix resolves issue #88 with no recurrence for 30 days" \
     --p 0.8 --resolve-by 2026-08-26
   ```

   The question must be resolvable by a stranger: named outcome, named deadline, no
   weasel room. "The fix probably helps" is unloggable on purpose.
2. **Read the scorecard at session start** when the file exists:

   ```sh
   python3 skills/ct-calibration/scripts/brier.py report --file .ct/predictions.jsonl
   ```

   Overdue predictions surface here — resolve them before making new ones.
3. **Resolve on observation, not vibes:**

   ```sh
   python3 skills/ct-calibration/scripts/brier.py resolve \
     --file .ct/predictions.jsonl --id p-3 --outcome 1 --resolved-by ci \
     --note "CI green 30 days, no reopen"
   ```

   The `--note` names the observation a stranger could check. Resolution judges the
   question **as recorded**, not as you now wish it had been phrased.

   `--resolved-by` is required and records **who observed the outcome** — `self`, `ci`,
   `tracker`, `human`, or a name. Write `self` when you resolved it yourself; that is the
   honest answer and it is the entire point of the field. The report then splits the
   score by resolver, so a ledger you graded yourself says so on its own face instead of
   printing a bare number.
4. **Use the bins, not just the score.** The report's finding looks like: *"at 80–90%
   stated, 5 of 9 happened (56%)"* — that is systematic overconfidence in that band.
   The fix is to adjust *future* numbers downward in that band; relabeling past entries
   is forbidden and the tooling refuses it.

`.ct/predictions.jsonl` lives in the project and is shared across sessions — the score
only means something if it accumulates.

## Integrity rules

- **p and the question text are immutable once logged.** The script has no edit command;
  a genuinely mis-logged entry is resolved `--outcome` per the recorded text, with the
  note explaining, and a corrected entry added fresh.
- One prediction per entry; compound predictions ("X and then Y") get split, or the
  resolution will be arguable.
- Do not log only the safe bets. The scorecard is diagnostic only if the 60%s and 70%s
  go in too — a ledger of 99%s measures nothing.

## Limits — read this one

This is the **weak form** of the act, and the gap matters more here than anywhere else
in the set: you are grader of your own homework, on a file you can edit. Append-only
discipline and the no-edit tooling narrow the leak; they do not close it. `resolved_by`
does not close it either — nothing stops you writing `ci` on a resolution you made up.
What it does is make the gap **measurable instead of merely disclosed**: a scorecard that
reads *"Brier 0.31 across 3 predictions, 2 self-resolved (67% graded by the predictor)"*
carries its own discount, and one where every outcome is self-recorded says outright that
it measures consistency, not accuracy. The strong form is machinery: an external ledger
the model cannot rewrite, fed outcomes by something other than the predictor (CI results,
issue trackers, a human). Even so, the weak form pays — a self-kept score still reveals
*directional* overconfidence, and the habit of naming a number and a deadline is most of
the benefit. See `docs/critical-thinking-whitepaper.md`.

Part of the critical-thinking set — see the `critical-thinking` skill for routing and
shared conventions.
