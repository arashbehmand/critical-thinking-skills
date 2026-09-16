---
name: ct-consistency-log
description: Keeps your own decisions straight across a long task — logs every decision and factual position taken during multi-step work with what it rests on, sweeps for contradictions, propagates retractions, and simulates each premise's withdrawal to show which recorded claims it carries. Use for tasks spanning many steps or sessions — migrations, long documents, multi-file refactors, investigations; or when the user says "didn't you say earlier", "we changed our mind about that", "what is load-bearing", or "keep our decisions straight". Not for tying a deliverable's factual claims to outside sources (that is ct-evidence-ledger).
argument-hint: [optional topic slug for the log file]
---

# Consistency log

Long chains of work contradict themselves quietly: nobody remembers step 3 by step 40,
and each local decision feels consistent with a past that is half-imagined. Attention
over a long context is shallow — write commitments down at decision time and check new
ones against the record mechanically.

Two failures, two sweeps. `pairs` catches *"I said A at step 3 and not-A at step 40"*.
`check` catches *"I withdrew A at step 4 and step 19 still rests on it"* — which the pair
sweep cannot see, and which is invisible in the output by construction: a conclusion
resting on a retracted premise looks exactly like a correct one.

This is not `ct-evidence-ledger`, which ties a deliverable's factual claims to outside
sources. The consistency log tracks your own decisions and positions over time, and what
each one rests on.

## Procedure

1. **Log at decision time, with what it rests on.** Whenever you fix a decision, adopt a
   factual position, or make a promise the rest of the work relies on:

   `<skill-dir>` is the folder this skill was loaded from; with the `critical-thinking` server connected, its `analyze_dependencies` tool computes the same impact report.

   ```sh
   python3 <skill-dir>/scripts/commitlog.py add \
     --file .ct/commitments--<slug>.jsonl \
     --statement "dead-letter queue drains hourly" --tags retries,queue \
     --depends-on c-1,c-4
   ```

   Statements are atomic and checkable — one commitment per entry, concrete enough that a
   stranger could say whether a later statement clashes with it. `--depends-on` names the
   entries this one is built on, **written now, never reconstructed at the end**: a
   dependency recalled after the fact is a rationalisation of the shape the work took.
2. **Changing a decision is an event, not an edit:** new entry with `--supersedes c-4` and
   the reason in the statement. The old line stays — the history of changed minds is
   signal (conventions §4). The `add` prints, right then, which entries just fell over.
3. **Sweep for contradictions periodically** — every ~10 entries, and always before the
   final deliverable:

   ```sh
   python3 <skill-dir>/scripts/commitlog.py pairs \
     --file .ct/commitments--<slug>.jsonl
   ```

   emits candidate pairs of live same-tag entries. Hand them to a fresh contradiction
   reviewer (template T8, the `critical-thinking` skill's `references/subagent-templates.md`) — it
   judges the written pairs with no task context, which is exactly what makes it cheap
   and unbiased. You wrote both lines; you *will* harmonize them without noticing. It
   won't.
4. **Walk the dependencies before delivering:**

   ```sh
   python3 <skill-dir>/scripts/commitlog.py check \
     --file .ct/commitments--<slug>.jsonl
   ```

   Reports `OUT` entries with the withdrawn premise each rests on, circular support, and
   shared premises carrying several live claims at once. It exits non-zero while any
   `OUT` entry remains.
5. **Rank recorded withdrawal impact** when the log informs a consequential conclusion:

   ```sh
   python3 <skill-dir>/scripts/commitlog.py impact \
     --file .ct/commitments--<slug>.jsonl --targets c-18
   ```

   The script removes every ACTIVE entry in simulation, repeats the same transitive
   status walk, and reports which live claims become `OUT`. `--targets` optionally names
   final conclusions; the output then lists every recorded premise whose withdrawal
   knocks each target out. Check the highest-impact premises first. This is more useful
   than direct fan-out: a premise with one child can still carry the whole downstream
   deliverable.

   Where the MCP server is registered, `analyze_dependencies` computes the same result
   from the entries directly. Script and core parity tests pin the two implementations.
6. **Resolve every flag.** A `CONTRADICT` is resolved by superseding one side explicitly
   or recording next to the pair why both stand. An `OUT` entry is **re-derived from live
   premises or dropped** — never quietly kept. Both block the deliverable.
7. **Pre-delivery check:** every load-bearing claim in the final answer traces to a live
   entry. Any that does not is the bug.

## Status

Computed from the log, never written into it — the file stays append-only.

| Status | Meaning |
|---|---|
| `ACTIVE` | live: not superseded, and every premise it rests on is live |
| `SUPERSEDED` | a later entry replaced it |
| `OUT` | rests, directly or transitively, on something not live |

The walk is deliberately conservative and **over-marks when edges are missing** — an
entry whose premise is not in the log at all is `OUT` too. Silence is the safe failure
here; false confidence is not.

## Tagging

Tags are the pairing key — pick 1–3 per entry from a small stable set you establish early
(component names, decision areas). Too many tags and contradictions hide across tag
boundaries; run `pairs --all` before the final sweep to catch cross-tag clashes.

## Integrity rules

- Log at decision time, **not retroactively** — a log reconstructed at the end inherits
  the very drift it was supposed to catch.
- `depends_on` is written when the entry is written. Backfilling edges produces a graph
  that agrees with the conclusion you already reached.
- The pair review must be a fresh mind (T8), never you re-reading your own log.
- Superseding without a reason in the statement is an edit in disguise.

## Signs it is being run badly

- Entries with empty `depends_on` across the board — that is a transcript summary, not a
  dependency record, and `check` says so.
- The log written once, at the end.
- Corrections that produce no `OUT` marks: either nothing rested on the retracted claim,
  or the edges were never recorded.
- An `impact` report treated as evidence that the recorded dependencies are complete.
- A final answer citing an `OUT` entry.

## Limits

Capture is voluntary: the skill cannot make you log the commitment you'd rather not write
down, and the JSONL is a mutable file. That gap is this act's main leak. And the walk
carries a caveat it prints on every run: **the record is model-authored, so this detects
inconsistencies among recorded dependencies only.** Writing claims and support edges into
a ledger is itself an encoding of ambiguous reasoning into graph form, performed one
assertion at a time by the same fallible model — dependencies it did not notice are
absent, dependencies it imagined are present. Retraction and withdrawal impact are exact
*about the record* and say nothing about unrecorded reasoning; an impact rank is a
verification-budget heuristic, not a structural or epistemic certificate. Machinery
would be a boundary that logs commitments automatically into an append-only store. See
`docs/critical-thinking-whitepaper.md`.

Part of the critical-thinking set — see the `critical-thinking` skill for routing and
shared conventions.
