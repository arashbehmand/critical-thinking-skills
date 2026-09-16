---
name: ct-premortem
description: Finds how a plan fails before it is committed — assumes the plan already failed, has fresh subagents write the post-mortem, and turns each failure story into a plan change or an observable tripwire. Use before committing to a plan, migration, launch, architecture choice, or irreversible decision; when the user says "premortem", "what could go wrong", or "poke holes in this plan". Not for arguing that the conclusion itself is wrong (that is ct-steelman), and not for auditing the premises a claim rests on (that is ct-assumption-audit).
argument-hint: [the plan or decision]
---

# Premortem

"Any risks?" produces polite nothing, because imagining your own plan failing feels like
betraying it. The premortem flips the frame: the failure has *already happened*, and the
job is to explain a fact, not to attack a proposal. Explanation unlocks specifics that
critique never surfaces.

This is not `ct-steelman`, which argues the conclusion is wrong; a premortem accepts the
plan and asks how carrying it out fails. Nor is it `ct-assumption-audit`, which inspects
premises one at a time instead of telling the failure story.

## Procedure

1. **Snapshot the plan** into `.ct/premortem--<slug>.md`: goal, steps, owners, dates,
   horizon. The snapshot is what the subagents get — the plan as it *is*, with none of
   your enthusiasm attached.
2. **Spawn 2–3 fresh post-mortem authors** (template T5,
   the `critical-thinking` skill's `references/subagent-templates.md`): "It is <horizon date>. The plan
   below was carried out and it failed badly. Write the post-mortem: top causes, most
   likely first, each naming the step that broke and the earliest observable signal."
   Run them independently — no author sees another's list.
3. **Merge and dedupe** the failure modes. Keep singletons: a mode only one author saw
   is still a mode (that is why there are several authors).
4. **For each surviving mode, decide one of:**
   - **Prevent** — change the plan now; write the change.
   - **Tripwire** — the earliest *observable* signal, plus what you will do when it
     fires. Observable means checkable by a stranger: "two engineers miss standup twice
     in week one", not "morale drops".
   - **Accept** — explicitly, with one line on why the cost of prevention exceeds the
     risk. Silent acceptance is the failure mode of risk registers.
5. **Decide:** proceed / proceed with the listed changes / stop. The accepted-unmitigated
   list goes next to the decision, not in a drawer.

## Artifact format

```markdown
# Plan: <one line>   Horizon: <date>
## Snapshot
## Failure modes (merged from N independent authors)
| # | Cause | Step that breaks | Earliest signal | Decision (prevent/tripwire/accept) |
## Decision: PROCEED WITH CHANGES — …
Accepted unmitigated: F3 (why), F5 (why)
```

## Integrity rules

- Run **before** the decision is announced. A premortem after commitment is theater —
  the lawyer already owns the plan.
- Subagents get the snapshot only — not "our exciting plan", not the benefits case. The
  frame is a completed failure, and the prompt must not argue with that frame.
- Tripwires get revisited: when one fires later in the work, do what the artifact said
  you would. A tripwire you ignore at fire time was never a tripwire.

## Limits

None that need machinery for the act itself — the declarative-failure frame plus fresh
authors covers the core bias. What a skill cannot do is *make you check the tripwires
later*; a harness hook or scheduled job watching for the named signals would.

Part of the critical-thinking set — see the `critical-thinking` skill for routing and
shared conventions.
