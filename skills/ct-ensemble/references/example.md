# Historical worked example — real output, real agents

Run on the pre-2026-08-14 `bench/generate_instance.py --seed 7`: a 22-item incident dossier, four
hypotheses, one true cause hidden in the answer key. Seven perspectives, each shown 14
of the 22 items. Nothing here is invented for the documentation; the verdicts came from
seven fresh agents and the numbers from `bag.py`. This is a frozen measurement record,
not a reproducible command against the current generator: the packet was later repaired
to expose its authoritative synthetic prediction model, remove impossible probe-value
questions, and keep the key out of the solver directory.

## The draw

The recorded draw used seven subsets at rate 0.65 and seed 1. Re-running those parameters
against the current generator creates a different, validity-repaired packet and must be
treated as a new experiment.

> Rule: 7 subsets, 14 of 22 items each (65%), sampled without replacement, seed 1. Every
> item is included in at least one subset and left out of at least one, so every item gets
> an influence score.

## The verdicts

Seven agents, template T10, one subset each, no contact between them.

| | S1 | S2 | S3 | S4 | S5 | S6 | S7 |
|---|---|---|---|---|---|---|---|
| verdict | H2 | H2 | H3 | H2 | H3 | H2 | H3 |

## The aggregate

```
perspectives: 7   votes: {'H2': 4, 'H3': 3}
WEAK PLURALITY — H2 at 57%. Report the split, not just the winner.

Evidence influence on the winner (most load-bearing first):
    E19: +0.80  (with it 80% of 5, without it 0% of 2)  <-- load-bearing
     E3: +0.80  (with it 80% of 5, without it 0% of 2)  <-- load-bearing
    E10: +0.67  (with it 67% of 6, without it 0% of 1)  <-- load-bearing
    E11: +0.67  (with it 67% of 6, without it 0% of 1)  <-- load-bearing
    E17: +0.67  (with it 67% of 6, without it 0% of 1)  <-- load-bearing
    E12: -0.60  (with it 40% of 5, without it 100% of 2)  <-- load-bearing
    E15: -0.60  (with it 40% of 5, without it 100% of 2)  <-- load-bearing
    E18: -0.60  (with it 40% of 5, without it 100% of 2)  <-- load-bearing
     E2: -0.50  (with it 50% of 6, without it 100% of 1)  <-- load-bearing
```

**H2 is the true cause.** The two hypotheses nobody voted for, H1 and H4, are the
firmware-pause and stale-routing decoys; every perspective killed both on their own core
readings. The real contest was H2 against H3, which is the contest the instance is built
to stage.

## What to notice

**The vote is right and honestly weak.** 4–3 is flagged, not smoothed. A reader is told
the ensemble nearly went the other way, which is true and would be invisible from a single
confident pass.

**The influence table found the crux the reasoning found.** `E3` — *"lease renewal
failure count reads nominal"* — tops the table at +0.80. Independently, in prose, two
perspectives named exactly that item as the thing the answer turns on:

> *S1:* "H2 beats H3 solely on E3 … Strip E3 out and H3 explains this evidence at least
> as well as H2 does."
>
> *S2:* "E3 is the ONLY thing scoring against H3, and it is plausibly a mis-rating —
> which would make H3, not H2, the correct answer."

The mechanical measure and the written arguments converged on the same load-bearing item
without either being shown the other. That is the method working: the number tells you
*where* to look, the prose tells you *why*, and they are produced independently.

**Both raised the same objection to their own answer.** Under clock skew, a lease can
expire early while every renewal RPC still succeeds — so a *failure counter* reading
nominal is compatible with H3 after all. That is the kind of objection a single pass
rarely volunteers about its own verdict, and here two of seven did unprompted, because
T10 asks for it.

## The honest limit this run exposes

Nine of 22 items cleared the load-bearing threshold. That is too many, and it is an
artifact of `--n 7`: with seven perspectives a share can only take a few values, so the
influence numbers are coarse and the ranking is noisy. The script now says so on its own
output.

Rule of thumb from this run: **`--n 7` is enough for the vote, not for the ranking.** Use
15 or more before acting on the order of the influence table. The vote costs seven agents;
a trustworthy importance ranking costs more, and that is a real price rather than a
rounding error.
