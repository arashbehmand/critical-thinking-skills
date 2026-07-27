---
name: ct-consistency-log
description: Log every decision and factual position taken during long multi-step work, and periodically sweep the log for contradictions with a fresh subagent before they compound. Use for tasks spanning many steps or sessions - migrations, long documents, multi-file refactors, investigations; or when the user says "didn't you say earlier" or "keep our decisions straight".
argument-hint: [optional topic slug for the log file]
---

# Consistency log

Long chains of work contradict themselves quietly: nobody remembers step 3 by step 40,
and each local decision feels consistent with a past that is half-imagined. Attention
over a long context is shallow — write commitments down at decision time and check new
ones against the record mechanically.

## Procedure

1. **Log at decision time.** Whenever you fix a decision, adopt a factual position, or
   make a promise the rest of the work relies on:

   ```sh
   python3 skills/ct-consistency-log/scripts/commitlog.py add \
     --file .ct/commitments--<slug>.jsonl \
     --statement "retry budget is 3 attempts, then dead-letter" --tags retries,queue
   ```

   Statements are atomic and checkable — one commitment per entry, concrete enough that
   a stranger could say whether a later statement clashes with it.
2. **Changing a decision is an event, not an edit:** new entry with
   `--supersedes c-4` and the reason in the statement. The old line stays — the history
   of changed minds is signal (conventions §4).
3. **Sweep periodically** — every ~10 entries, and always before the final deliverable:

   ```sh
   python3 skills/ct-consistency-log/scripts/commitlog.py pairs \
     --file .ct/commitments--<slug>.jsonl
   ```

   emits candidate pairs of active same-tag entries. Hand the pairs to a fresh
   contradiction reviewer (template T8,
   `critical-thinking/references/subagent-templates.md`) — it judges the written pairs
   with no task context, which is exactly what makes it cheap and unbiased. You wrote
   both lines; you *will* harmonize them without noticing. It won't.
4. **Resolve every flag:** supersede one side explicitly, or record next to the pair why
   both stand. An unresolved CONTRADICT flag blocks the deliverable.

## Tagging

Tags are the pairing key — pick 1–3 per entry from a small stable set you establish
early (component names, decision areas). Too many tags and contradictions hide across
tag boundaries; run `pairs --all` before the final sweep to catch cross-tag clashes.

## Integrity rules

- Log at decision time, **not retroactively** — a log reconstructed at the end inherits
  the very drift it was supposed to catch.
- The pair review must be a fresh mind (T8), never you re-reading your own log.
- Superseding without a reason in the statement is an edit in disguise.

## Limits

Capture is voluntary: the skill cannot make you log the commitment you'd rather not
write down, and the JSONL is a mutable file. Machinery would: a boundary that logs
commitments automatically (every tool response, every stated position at the server
edge) into an append-only store. That gap — voluntary capture — is this act's main
leak; see `docs/critical-thinking-whitepaper.md`.

Part of the critical-thinking set — see the `critical-thinking` skill for routing and
shared conventions.
