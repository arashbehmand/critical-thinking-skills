---
name: ct-verdict-gate
description: A pre-verdict checklist that must produce written answers before any consequential conclusion ships - terms pinned, opposing case built by a fresh mind, assumptions audited, claims sourced, flip conditions named. Use before delivering a final recommendation, verdict, go/no-go, or any conclusion someone will act on; when the user says "final answer", "ship it", or "so what's the call".
argument-hint: [the conclusion about to ship]
---

# Verdict gate

Known checks get skipped exactly when they matter — under time pressure, and when the
answer feels obvious. Awareness does not fire on demand; a checklist that must produce
*written output* before the verdict unlocks does. This is the set's checklist-gate: the
last act, run when the others should already have happened.

## The gate

Write `.ct/gate--<slug>.md` with one line per item: **a link to the artifact, or the
word `SKIPPED` plus one honest sentence why.** Silent skips are the failure mode this
gate exists to catch; a written "SKIPPED because the stakes are one Slack reply" is a
legitimate pass.

```markdown
# Gate: <the conclusion, one line>

1. TERMS    — load-bearing words pinned?            → .ct/definitions--….md | SKIPPED: …
2. OPPOSE   — other side's best case, built by a
              mind that never saw my lean?          → .ct/steelman--….md    | SKIPPED: …
3. FLOOR    — assumptions listed, weakest named?    → .ct/assumptions--….md | SKIPPED: …
4. EVIDENCE — every factual claim sourced/hedged?   → .ct/evidence--….jsonl | SKIPPED: …
5. FLIP     — what observation would change this
              conclusion? (concrete, checkable)     → <named inline — no artifact excuses this one>
6. NUMBER   — confidence as a probability;
              logged if consequential?              → p=…, .ct/predictions.jsonl | not consequential
7. FRAGILE  — which single input, if wrong,
              flips the verdict?                    → <from ach_score sensitivity / argument-map probing / reasoned inline>

Verdict: <the conclusion>
Strongest surviving counter-argument: <stated next to it, not buried>
```

Items 5 and 7 have no SKIPPED option: a conclusion whose holder cannot name a flip
condition is not a conclusion, it is an identity.

## Procedure

1. Draft the verdict privately.
2. Fill the gate file. Where an item points to an act that never ran and the stakes
   warrant it, **go run the act now** — the gate is late-binding quality control, not
   paperwork about work already done.
3. Deliver the verdict **with** the strongest surviving counter-argument beside it and
   the gate artifact cited. A verdict shipped naked of its best objection is marketing.

## Integrity rules

- The gate is filled after drafting but **before delivering** — its whole value is
  standing between those two moments.
- `SKIPPED` lines must name the real reason (stakes, time, irrelevance), not a
  flattering one. A gate full of "SKIPPED: obviously fine" on a consequential call is
  itself a finding: the confidence that skips checks is the confidence least entitled to.

## Limits — this skill is honest about being the weak form

A checklist in context is still advice: nothing *prevents* delivering a verdict without
the gate file, and the model most likely to skip it is the one most confident — exactly
the case the gate targets. Hard enforcement is harness work, one level up from skills:
e.g. a Claude Code `Stop` hook that blocks ending the turn while the reply contains a
verdict marker but no `.ct/gate--*.md` was written this session. The skill ships the
checklist; only a hook can ship the lock. See `docs/critical-thinking-whitepaper.md`
§three tiers.

Part of the critical-thinking set — see the `critical-thinking` skill for routing and
shared conventions.
