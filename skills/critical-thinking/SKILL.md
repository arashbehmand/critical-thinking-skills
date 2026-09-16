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
| the asked question may be the wrong problem: an anomaly does not fit, fixes do not touch it, the work is stuck in one frame — *changes the question* | `ct-reframe` |
| a universal, invariant, guarantee, or "must/never" claim could be broken by one witness — *attacks a claim about every case* | `ct-counterexample` |
| a big or vague question invites a one-jump answer | `ct-question-tree` |
| a number cannot be looked up directly — *estimates it from guessed factor ranges* | `ct-question-tree` (Fermi mode) |
| the question is right but is an ordinary formal object in disguise: allocation, scheduling, a graph, a threshold, queues, feedback, noisy measurement — *keeps the question, answers it in code* | `ct-formalize` |
| a quantitative answer that needs a solver, search or simulation is being reasoned out in prose, or the same fix keeps failing in a familiar-looking way | `ct-formalize` |
| a result is about to be computed from a model, formula, table, diagram, or data copied out of a source — *inspects a representation you built* | `ct-sanity-check` first |
| a load-bearing word is contestable ("safe", "better", "significant") — *keeps the question, fixes its words* | `ct-definition-pin` |
| the question is right and answerable by hand, but its notation invites mistakes: probabilities, negations, abstractions, prose comparisons — *keeps the question, changes the notation* | `ct-reformat` |
| a claim or plan rests on premises nobody stated — *inspects the premises* | `ct-assumption-audit` |
| a contested conclusion already has an owner or a lean — *argues the conclusion is wrong* | `ct-steelman`, then `ct-verdict-gate` if consequential |
| several mutually exclusive explanations fit the same evidence — *decides which one survives* | `ct-ach` |
| a set of evidence items supports more than one reading, and it matters which items the verdict rests on — *varies the evidence each fresh mind sees* | `ct-ensemble` |
| a factual deliverable could contain naked claims — *does each claim have a source* | `ct-evidence-ledger` |
| sources may be relevant without entailing the claims, or may share one origin — *does the source actually say it* | `ct-entailment` |
| work spans many decisions, files, steps, or sessions — *your own decisions over time* | `ct-consistency-log` |
| a score, grade, estimate, or pick-one judgment is noisy across occasions — *the identical prompt to several fresh minds; nothing varies* | `ct-panel` |
| a plan is about to become costly or hard to reverse — *assumes the plan failed and asks how* | `ct-premortem` |
| a probability matters and will resolve later | `ct-calibration` |
| one yes-or-no claim needs a quantitative, editable pro/con verdict — *one claim, for and against* | `ct-argument-map` (argLLM MCP) |

### Near neighbours

Some rows describe symptoms that overlap. Break the tie by what the act changes, not by
which symptom sounds closest.

- **`ct-reframe`, `ct-reformat`, `ct-formalize`** all apply to a slippery question. Ask what
  should change: the *question* → `ct-reframe`; only its *notation*, after which it is
  doable by hand → `ct-reformat`; *who answers it*, because it needs a solver, search or
  simulation → `ct-formalize`. When unsure whether the question is right, reframe first —
  the other two harden whatever question they are handed.
- **`ct-panel` and `ct-ensemble`** both send work to several fresh minds and vote. Ask what
  varies between those minds: *nothing*, the prompt is identical and the question is how
  noisy one judgment is → `ct-panel`; *the evidence each one sees*, and the question is what
  the verdict rests on → `ct-ensemble`. Without discrete evidence items to slice, an
  ensemble is just a panel.
- **`ct-ach`, `ct-ensemble`, `ct-argument-map`** all weigh evidence toward a conclusion. Ask
  what you need to learn: *which of several explanations survives* → `ct-ach`; *what an
  existing verdict rests on* → `ct-ensemble`; *whether one yes-or-no claim holds*, with a
  verdict others can contest → `ct-argument-map`.
- **`ct-steelman`, `ct-premortem`, `ct-assumption-audit`** all attack before commitment. Ask
  what is under attack: *the conclusion* → `ct-steelman`; *the plan, once carried out* →
  `ct-premortem`; *the premises underneath* → `ct-assumption-audit`. `ct-verdict-gate` does
  none of these; it checks that the relevant ones ran.
- **`ct-evidence-ledger` and `ct-entailment`** both deal with sources. *Does each claim have a
  source?* → ledger. *Does the source actually say it, and how many independent origins?* →
  entailment, which starts from the ledger's pairs.
- **`ct-question-tree` (Fermi mode) and `ct-formalize`** both produce numbers. *Estimated from
  guessed factor ranges* → Fermi. *Computed exactly from given data by a solver, search or
  simulation* → formalize.
- **`ct-counterexample` and `ct-sanity-check`** both check with execution. *A claim about every
  case* → counterexample. *A representation you built, before computing from it* → sanity
  check.
- **`ct-definition-pin` and `ct-reframe`**: *keep the question and fix what its words mean* →
  pin; *the question itself may be wrong* → reframe.
- **`ct-consistency-log` and `ct-evidence-ledger`**: *your own decisions and positions over a
  long task* → log; *a deliverable's claims against outside sources* → ledger.

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

**Check before you crunch.** Whenever any act, or your own direct work, builds a
representation and computes an answer from it, run `ct-sanity-check` on the representation
first — including when you recognize a formal problem and solve it inline without opening
`ct-formalize`. Recognizing the shape is not the same as encoding it correctly.

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
