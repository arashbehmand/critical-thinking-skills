---
name: critical-thinking
description: Autonomous controller for the critical-thinking skill set — silently recognizes the shape and stakes of a substantive problem, chooses the smallest useful thinking act, escalates only when a failure signal appears, and uses no scaffold when direct work is better. The user never has to name a technique. Use for decisions, investigations, estimates, plans, contested or sourced claims, long tasks, surprising anomalies, universal claims, and any consequential answer whose failure would matter; also for "think critically", "are you sure", "what am I missing", and "how confident are you".
argument-hint: [question, claim, plan, or decision]
---

# Critical thinking — autonomous controller

The user supplies the problem, not the method. Do **not** ask which critical-thinking act
to run, recite the toolbox, or make the user conduct the analysis. Triage silently, load
only the selected skill, run it, and deliver the answer. Interrupt the user only for a
missing value judgment, a materially ambiguous meaning, unavailable evidence they must
supply, or authority for an irreversible action.

The set changes the thinking environment in three ways:

1. **Externalize** — put thought into a checkable structure, not free prose.
2. **Mechanize** — give arithmetic, counting, execution, and search to deterministic
   tools whenever the problem permits it.
3. **Contest** — separate production from evaluation with fresh minds, then keep every
   conclusion open to attack.

## Silent triage

Before substantive work, classify the task using visible features. Do not manufacture
numeric expected utilities for this decision.

1. **Can an external operation settle part of it?** Retrieval, code execution, tests,
   database queries, measurement, or a solver outrank model-only reflection. Use them.
2. **What is the failure signature?** Route by the problem's shape using the table below.
3. **How costly is a wrong answer?** Stakes, irreversibility, disagreement, and long
   dependency chains justify more checking. Length and sophistication do not.
4. **What new constraint will the act add?** Prefer external evidence or independently
   constrained computation; use model-only structure when it makes omissions or
   disagreement visible. If the act adds neither and no concrete failure signal called
   for it, skip it.
5. **Choose the minimum useful act.** Start with one. Escalate only when it exposes a
   split, an unsupported load-bearing claim, a fragile input, a missing observable, or a
   failed check.

`NO_SCAFFOLD` is a successful route. Use it for low-stakes, directly answerable work
where a recipe would add ceremony rather than information, computation, or visibility.
Answer normally; do not create a routing receipt merely to record that nothing ran.

## Routing table

| Failure signal in the task | Run |
|---|---|
| the asked question may be the wrong problem; an anomaly does not fit; the work is stuck in one frame | `ct-reframe` |
| a universal, invariant, guarantee, or "must/never" claim could be broken by one witness | `ct-counterexample` |
| a big or vague question invites a one-jump answer | `ct-question-tree` |
| a number cannot be looked up directly | `ct-question-tree` (Fermi mode) |
| the question is an ordinary formal object in disguise: allocation, scheduling, a graph, a threshold, queues, feedback, noisy measurement | `ct-formalize` |
| a quantitative answer is being reasoned out in prose, or the same fix keeps failing in a familiar-looking way | `ct-formalize` |
| a load-bearing word is contestable ("safe", "better", "significant") | `ct-definition-pin` |
| the representation is slippery: probabilities, negations, abstractions, prose comparisons | `ct-reformat` |
| a claim or plan rests on premises nobody stated | `ct-assumption-audit` |
| a contested conclusion already has an owner or a lean | `ct-steelman`, then `ct-verdict-gate` if consequential |
| several mutually exclusive explanations fit the same evidence | `ct-ach` |
| several evidence-conditioned perspectives are useful, including what drives their split | `ct-ensemble` |
| a factual deliverable could contain naked claims | `ct-evidence-ledger` |
| sources may be relevant without entailing the claims, or may share one origin | `ct-entailment` |
| work spans many decisions, files, steps, or sessions | `ct-consistency-log` |
| a score, grade, estimate, or pick-one judgment is noisy across occasions | `ct-panel` |
| a plan is about to become costly or hard to reverse | `ct-premortem` |
| a probability matters and will resolve later | `ct-calibration` |
| a claim needs a quantitative, editable pro/con verdict | `ct-argument-map` (argLLM MCP) |

## Progressive escalation

Do not run a canonical pipeline by default. Move one rung at a time:

- **Rung 0 — direct.** External lookup/execution if needed, then answer. Most tasks stop
  here.
- **Rung 1 — expose.** One cheap act that changes the representation or exposes a hidden
  premise: reframe, reformat, definition pin, question tree, assumption audit, or
  counterexample search.
- **Rung 2 — contest.** Fresh-context judgments plus mechanical aggregation when the
  first pass reveals real ambiguity, competing explanations, or noise.
- **Rung 3 — gate.** For consequential conclusions, ground load-bearing claims, name the
  flip condition and fragile input, and run the verdict gate. High-stakes domain judgment
  still escalates to an appropriate human; structure does not confer authority.

Stop when the current answer is supported by the available evidence and checks, the next
act would not address a named unresolved failure, or the missing information cannot be
obtained. Return `UNKNOWN` or a conditional answer instead of filling the hole.

## Composition without ceremony

Acts compose because findings trigger the next act, not because a fixed workflow says
so. Examples:

- ACH finds a rank-flip cell whose source is doubtful → `ct-entailment` on that item.
- A premortem exposes an assumption the plan cannot survive → `ct-assumption-audit`.
- A panel splits because "ready" was underspecified → `ct-definition-pin`, then rerun.
- A counterexample breaks the current formulation but not the user's intent → revise the
  claim, preserve the witness, and test the revision again.

Keep orchestration invisible in ordinary answers. When an act ran, cite its `.ct/`
receipt and state the strongest surviving limitation; do not dump the internal routing
discussion unless the route itself materially affects the conclusion.

## Shared conventions

Read [references/conventions.md](references/conventions.md) before the first act. The
non-negotiables are receipts, uncontaminated fresh minds, script arithmetic, append-only
ledgers, provenance, and the epistemic-leverage rule: report separately what came from
external evidence, what was independently computed, and what was only reorganized or
elicited from the model.

## Honesty note

These skills are procedures, not enforcement. Each skill's `Limits` section says what
the recipe cannot guarantee and which boundary could. The lawyer test still decides the
tier: if the act only works because something outside the model refuses to let motivated
reasoning through, prompting is not enough. Autonomous routing removes user
micromanagement; it does not turn compliance into a guarantee.
