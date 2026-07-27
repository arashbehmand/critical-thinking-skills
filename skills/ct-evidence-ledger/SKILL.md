---
name: ct-evidence-ledger
description: Keep a ledger tying every factual claim in a deliverable to its source with a quality grade, so unsourced claims stop blending in with backed ones. Use for fact-heavy answers, reports, research summaries, and decision documents; when the user asks "where did that come from"; or before publishing anything with numbers, dates, quotes, or causal statements in it.
argument-hint: [the deliverable to audit, or start logging as you draft]
---

# Evidence ledger

Confident sentences outlive their sources: the claim survives every rewrite, where it
came from is lost by the second draft. A ledger re-couples them — and makes the claims
with *nothing* behind them visible instead of letting them borrow credibility from their
neighbors.

## Grades

| Grade | Meaning |
|---|---|
| **A** | primary / measured — the dataset, the log, the spec, the experiment itself |
| **B** | reputable secondary — official docs, peer-reviewed paper, quality press |
| **C** | weak — blog, forum, single unverified account, hearsay |
| **D** | memory / unsourced — model prior, "I recall that…" |

Grade the **source**, not the claim: a claim you love from a forum post is C; a claim
you hate from the primary dataset is A. The uncomfortable grade is the point.

## Procedure

1. **Draft** the deliverable (or take the existing one).
2. **Sweep for factual claims**: numbers, dates, names, quotes, and causal statements
   presented as fact. Opinions and clearly-flagged speculation stay out of the ledger.
3. **Log each claim:**

   ```sh
   python3 skills/ct-evidence-ledger/scripts/ledger.py add \
     --file .ct/evidence--<slug>.jsonl \
     --claim "p99 fell 40% after the index change" \
     --source "grafana dashboard, deploy-4812 annotation" --grade A
   ```

   Claims from memory get `--grade D` and no source — *honestly*. The ledger only works
   if D means D.
4. **Run the report:**

   ```sh
   python3 skills/ct-evidence-ledger/scripts/ledger.py report \
     --file .ct/evidence--<slug>.jsonl
   ```

   It lists the naked claims (grade D or empty source) and the grade distribution.
5. **Fix every naked claim** — one of: source it (go search; upgrade the entry with a
   superseding line), hedge it in the text ("unverified, from memory: …"), or cut it.
   Naked-and-stated-as-fact is the only forbidden state.
6. **Cite ids in the deliverable** for load-bearing claims (`[E3]`), so a reader can walk
   claim → ledger → source.

## Integrity rules

- Log at drafting time, not after — retro-logging invites inventing sources for
  sentences you already like.
- Corrections supersede (`--supersedes ev-3`); never edit a line (conventions §4).
- A quote gets the exact text and location; "somewhere in the docs" is grade C at best.

## Limits

Two things discipline cannot give: nothing stops *generous grading*, and nothing checks
the source actually says what the claim says. Machinery would: a citation-checker that
fetches each source and verifies the quoted content against the claim, plus an
append-only store. Until then, the ledger's honesty is only as good as the fresh-eyes
review it gets — for high-stakes deliverables, have a subagent spot-check the A/B
entries against their sources. See `docs/critical-thinking-whitepaper.md`.

Part of the critical-thinking set — see the `critical-thinking` skill for routing and
shared conventions.
