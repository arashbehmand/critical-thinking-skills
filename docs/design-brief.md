# A Cognitive Scaffold for Machine Thinking

**A full statement of the problem, addressed to whoever will design the solution.**

This document explains a problem. It contains everything we know about it: why it
exists, why it is hard, what we tried, what our attempt taught us, and what any solution
has to live with. It deliberately contains no solutions. Where something below sounds
like a design decision, it is a property of the problem, not a choice we have made for
you — the design is yours.

---

## 1. The problem

No human thinks well alone, and no serious human institution expects one to.

A physician is reliable because of the chart, the lab result, the second opinion, and
the morbidity conference — not because her unaided judgment is flawless. An accountant
is trusted because the books must balance and someone else audits them. A scientist's
claim is credible because a hostile stranger reviewed it and the analysis was registered
before the data arrived. A forecaster becomes calibrated only when someone keeps the
score, and an engineer's design survives because a checklist forced questions he was too
confident to ask himself. Everywhere reliable thinking exists, it was achieved the same
way: not by producing better thinkers, but by surrounding thinkers with **counterparts
they could depend on** — external memories that do not bend, colleagues whose errors are
not their errors, instruments that compute instead of opine, record-keepers the thinker
cannot edit, adversaries who must be answered before the conclusion ships.

An LLM agent, today, is the lone expert with none of this. One context, one pass,
self-checked at best. And because it learned to think from human text, it inherited
precisely the failure modes the human web exists to catch: it anchors, it confirms, it
rationalizes after committing, its confidence outruns its accuracy, its answers move
when the phrasing moves and the facts do not, it favors its own prior work when asked to
judge it, and over a long task it quietly forgets what it decided and why. We have
watched all of these in our own agents, on our own work.

**The problem we want solved: build the counterpart-web for the agent.** A cognitive
scaffold the agent can *depend on*, the way a human professional depends on their
counterparts, so that a better thinking journey becomes possible. Not a smarter model —
an environment in which the model's existing capability yields answers that are
checkable, contestable, and measurably better.

The word *depend* carries most of the weight in that sentence, and it is where our own
attempt fell short. A counterpart you can ignore is advice. A record you can rewrite is
a diary. A colleague who has already seen your draft is an echo. A receipt you can write
yourself proves only that a receipt was written. Dependence means the scaffold is
actually there under load — precisely when the agent is confident, hurried, or twenty
steps into a long task, which is exactly when human checks get skipped too, and exactly
why the human web is built out of institutions rather than reminders. The replication
crisis was not fixed by teaching scientists more statistics; it was fixed by
preregistration — a gate passed before the answer is known, kept by someone other than
the author. That is the grade of dependability the scaffold needs, and prompting alone
has never provided it.

---

## 2. Why the human web does not port directly

The analogy is the motivation, not the blueprint. Five disanalogies define the actual
design space, and each one broke something in our prior attempt.

**There is no independent colleague on the shelf.** The most powerful element of the
human web is the second opinion — a mind whose training, history, and error pattern
differ from yours. An agent asking a copy of itself is consulting the same distribution
that produced the error; the copy's mistakes are correlated with its own, and correlation
is substantial even across model families that share training corpora. Ten agreeing
samples from one model are not ten witnesses. Genuine independence must be manufactured,
imported, or measured — it cannot be assumed from the count of voices — and any part of
the scaffold that aggregates opinions has to know how independent they actually were.

**Rearranging your own thoughts adds no evidence.** When a human "considers the
opposite," memory, affect, and social experience genuinely inject something new. When a
model re-reads, critiques, or debates its own output, no information about the world
enters that was not already there; structure can improve what gets *extracted* — it can
expose an omission, make a contradiction visible, decompose a leap — but it cannot
improve the *evidence*. Only things outside the model can: an executed result, a
retrieved source, a resolved outcome, a measurement, a genuinely different mind. A
scaffold that cannot tell which of the two it is adding at any moment will launder
reorganized confidence as corroboration. Ours sometimes did.

**The agent's account of its own process is produced by the process.** A hospital knows
the checklist ran because the nurse is not the surgeon. When an agent reports that it
followed a procedure, the report is generated by the same machinery whose diligence is
in question — and an artifact of the procedure can be produced without the procedure. A
model can fill an analysis table in one motivated breath: the table exists; the
independent analysis never happened. Process claims therefore need grounding that does
not pass through the agent's own account, and observability alone is not sufficient.

**Confidence is bound to nothing.** A human expert who is repeatedly, publicly wrong
pays for it, and the memory of paying changes the next judgment. An agent's stated
probability costs it nothing, resolves nowhere, and is forgotten at the end of the
context window. Score-keeping — the single mechanism known to couple human confidence to
accuracy — does not exist unless something outside the agent keeps the score, because a
self-kept score is the confidence problem restated.

**But the machine side has advantages the human web never had.** Perfect resettability:
a genuinely fresh mind, with no ego investment in the draft, can be summoned at will —
no human institution ever had that. Cheap parallelism. Tireless enumeration. Exact,
replayable records. The scaffold should be designed for a thinker with these properties,
not a slower human; the disanalogies cut both ways, and our prior attempt exploited far
too little of this side.

---

## 3. What "a better thinking journey" has to mean

The scaffold is for **consequential work**, which for us means: diagnosing a production
failure where several stories fit the same telemetry; technical or commercial decisions
under uncertainty that are expensive to reverse; research and fact-heavy writing whose
claims will be acted on; estimating quantities no source states directly; and long,
multi-session work where an early error propagates silently.

Success, in priority order:

1. **The answers get better at matched cost** — measured against the same agent, same
   task, same budget, without the scaffold, by someone who is not the builder.
2. **A reader can see what an answer rests on and what would change it** — and can
   challenge a specific input and watch the conclusion recompute.
3. **It costs less than the errors it prevents.**

And one explicit anti-goal, because it is the failure mode this whole field is prone to:
**output that looks more rigorous without being more accurate is worse than nothing.**
Structure persuades on its own; a reader trusts a table more than a paragraph regardless
of what is in it. A scaffold that raises the reader's confidence faster than it raises
correctness is a harm, and whether it does so is a measurable property that must be
measured.

---

## 4. What we tried, and what it taught us

We spent a serious effort building a version of this — deliberation procedures the agent
was instructed to follow, deterministic aggregation of collected judgments, one runtime
enforcement hook, and a synthetic benchmark with planted traps. The details do not
matter here and should not constrain you. What we measured does, because each finding is
a fact about the problem:

1. **We still cannot say whether any of it works.** After all of it, no matched-cost
   comparison against an unaided baseline ever produced a usable signal. This is the
   central fact of the prior attempt.
2. **Advice is not depended on.** Agents merely *encouraged* to use the procedures used
   them two times in five; three of five used nothing. Compliance measured on a run
   where the procedure was explicitly ordered came out at 100% — and meant nothing,
   because ordered compliance says nothing about unobserved use.
3. **Compliance cannot be measured from inside.** We asked the system to report whether
   it had followed its own procedures; the report is generated by the thing under test.
   Measuring real dependence requires observation from outside, during ordinary use, and
   we never built that.
4. **The prescribed procedure and a single motivated pass produce genuinely different
   work** — they disagreed on roughly 29% of judgments across 648 comparisons — but
   nothing we built could say which was *better*.
5. **Verdicts moved on wording alone.** Restating a stakeholder's confidence — no new
   information — flipped the leading conclusion in three of three instances, while the
   underlying judgments barely moved. The conclusions were more volatile than the inputs
   they were supposedly computed from.
6. **Formal structure laundered the model's prior.** In one formal-argumentation trial,
   whenever the two sides' arguments arrived equally strong, the computed verdict
   collapsed exactly to the model's initial guess about the claim — mathematically
   correct, and decorative. Two of four verdicts were wrong, both from that collapse,
   and both were fixed only by a human contesting one specific input.
7. **Our measuring instrument broke before the model did — four separate times.** An
   answer key that contradicted the method it scored; costs that leaked the hidden
   answer; a scorer that accepted only one of several valid answers; control-arm agents
   that found the procedures under test lying in the working directory and used them.
   Assume the first version of any instrument is broken and budget for discovering how.
8. **Fair and informative traded off silently.** The fix that made our benchmark honest
   — every scored answer reconstructable from participant-visible data — also made it
   solvable by plain careful reading. Both arms then scored perfectly, ten runs,
   byte-identical answers. A test with no headroom measures nothing, and we did not
   notice until the control arm ran.
9. **In short, well-structured contexts, the unaided agent was already good.** The traps
   our benchmark planted were handled by ordinary careful reading. Whatever value this
   scaffold has, we now believe it lives across *long horizons* — where the correction
   was twenty steps ago and the context has moved on — and that regime has never been
   tested by us or, as far as we know, anyone.
10. **Cost is real and the granularity was wrong.** One three-instance measurement
    consumed 87 model calls and roughly 1.9 million tokens, largely because we bought
    independence by atomizing the evidence down to one item per judge — destroying each
    judge's ability to see the whole. Independent nonsense does not average into sense.
    What we actually want, and never got, is stated in one line: **genuinely different
    views of the whole problem, cheaply, combined by rule rather than by taste.**
11. **The owner lost the thread.** The person paying for all of this had to repeatedly
    beg for a plain-language account of what had been built, what was failing, and what
    was next. A scaffold whose own state cannot be held in a human head has failed as a
    product no matter what it does for the agent.

---

## 5. What any solution must provide

These follow from the problem above; the identifiers exist so your design can answer
them point by point.

### The answer it helps produce

- **A1.** Measurably better answers than the same model without the scaffold, at
  matched budget, with "better" defined per task family before any run.
- **A2.** The ability to say "not determinable from what is available," name what is
  missing, and stop — rather than produce a plausible number from invented inputs. A
  gap is preferable to a guess wearing a disclaimer.
- **A3.** Every consequential answer states what would have to be different for it to
  change — computed from the recorded inputs, not asserted in prose.
- **A4.** A reader can see which specific inputs carry a conclusion, ranked, and check
  the ranking by hand; where the ranking is only exact about what was recorded, it says
  so on its face.
- **A5.** Answers hold still under information-free perturbation — reordering,
  renaming, rephrased confidence, changed formatting. Residual instability is measured
  and reported, never assumed away.
- **A6.** Every consequential answer separates three things that polished prose blurs:
  what came from outside the model, what was computed deterministically, and what was
  only restructured or elicited from the model.
- **A7.** No number enters a computation without a recorded origin; a load-bearing
  input with no origin stops the computation rather than decorating it. Relabelling an
  input to get past such a stop must itself be visible.
- **A8.** A human can contest one specific input and watch the conclusion recompute,
  with the change and both verdicts permanently recorded. Gaming an input must be
  possible — and permanently visible.

### The counterparts themselves

- **B1.** Where an independent judgment feeds a verdict, it comes from a context that
  could not have seen the draft, the lean, or the other judgments — and that this held
  is observable from outside the component claiming it.
- **B2.** Anything that combines several judgments reports how independent they
  actually were, measured; unmeasured independence counts as none.
- **B3.** Independence is never bought by destroying competence: every contributing
  perspective must remain able to see enough of the whole problem to have a real view,
  and the cost curve of the split must be stated.
- **B4.** Claims that a procedure ran are supported by evidence gathered outside the
  component that ran it. Self-report and self-authored artifacts do not count.
- **B5.** When a conclusion is recorded as resting on a premise, the link is recorded
  at write time; withdrawing the premise mechanically flags everything resting on it,
  and an incomplete record fails toward over-flagging.
- **B6.** Records used as evidence about the agent's own past — predictions,
  commitments, resolutions, scores — cannot be rewritten by the component they
  describe.
- **B7.** Every act of the scaffold runs under a stated cost ceiling, degrades
  gracefully when the ceiling binds, and reports what it actually cost.

### The human in the loop

- **C1.** A person who has read none of the design documentation can learn, in under
  two minutes: what ran, what it cost, what the answer rests on, what would change it,
  and what remains unknown. This is a hard requirement; see finding 11.
- **C2.** The user states the problem. The scaffold decides what, if anything, to
  engage. The user is never handed a menu of techniques.
- **C3.** The scaffold interrupts a human only for a value judgment, a materially
  ambiguous meaning, evidence only they hold, or authority over an irreversible act —
  and it does interrupt for those, rather than deciding them itself. Structure never
  confers authority.
- **C4.** Silence is a first-class route. Most tasks deserve no ceremony; the scaffold
  declines to engage where it adds nothing, and how often it declines is itself
  reported. A scaffold that always engages has failed before its accuracy is read.
- **C5.** Nothing wedges. A counterpart that can halt the thinker's ordinary work is
  worse than one that is absent; any blocking behavior must be justified by a measured
  error reduction and must fail open when uncertain.

### Its honesty about itself

- **E1.** Anything presented as computed is recomputable: identical output for
  identical input, by us, in isolation, with no model in the loop.
- **E2.** Any statistical or calibrated claim carries the conditions under which it
  holds and expires automatically when they stop holding — including on a model version
  change. A stale basis must not keep emitting a live guarantee.
- **E3.** Every component earns its place through removal: whatever does not survive a
  leave-one-out comparison at matched cost is taken out. Expect a material fraction of
  any first design to go.
- **E4.** The scaffold lives where the agent lives. We run agents in several different
  harnesses; a counterpart available in only one of them is furniture. Reduced modes
  are acceptable; they must be documented as such.

---

## 6. The measurement problem is part of the problem

Do not read measurement as our acceptance bureaucracy; it is half of the design problem
itself. Every finding in §4 about broken instruments happened to competent people
building in good faith, and the default outcome of this project is a system whose value
is unknowable. Any credible design therefore treats the instrument as a deliverable of
equal rank with the scaffold, and builds it first:

- **D1.** The instrument that will judge the scaffold is designed, validated, and shown
  to work before the scaffold it judges.
- **D2.** Every test family demonstrates headroom: a competent unaided baseline must
  fail on a stated fraction of instances, or the family is discarded.
- **D3.** Every scored field is shown to defeat degenerate strategies; a field a
  constant answer can win is not a scored field.
- **D4.** Every scored answer is reconstructable from data the test-taker is allowed to
  see, proven by an independent reconstruction, before the instance is used.
- **D5.** Nothing is tuned on what it is scored on; a sealed held-out family is scored
  last and reported separately.
- **D6.** Metrics, arms, exclusions, and stopping rules are fixed in writing before
  data collection, and results report both directions — tasks the scaffold fixed and
  tasks it broke.
- **D7.** We can re-run the whole measurement ourselves, from the artifacts, without
  help, and get the same numbers.
- **D8.** At least one family separates the error from its correction by a long
  horizon — long context, many steps, or separate sessions — because that is where we
  now believe the value lives, and it is untested.
- **D9.** At least one family uses messy real tasks where the scaffold must build its
  own representation of the situation, and the faithfulness of that representation is
  itself scored. Synthetic instances with pre-formalized inputs test discipline only.
- **D10.** The trust effect is measured: whether the scaffold's output raises a
  reader's confidence faster than its accuracy. If it does, that is a defect to fix,
  not a caveat to disclose.

**A null result is a fully acceptable outcome.** "This does not help, and here is the
number" is a success of the project. Arriving at the end with no instrument capable of
detecting a null is the only unacceptable one.

---

## 7. Shapes that look like solutions and are not

Each of these is a known failure of this problem wearing a solution's clothes. Naming
them here is what keeps them from arriving under new names.

- **Exact arithmetic over invented inputs, defended by a disclaimer.** The precision is
  real, the inputs are fiction, and the caveat beside the number reads as care rather
  than as a warning.
- **Any guarantee whose only evidence is the model's account of what it did.**
- **Self-graded history** — a score the scorer keeps on itself.
- **Sample count presented as corroboration.** More draws from one distribution reduce
  noise; they do not create witnesses.
- **"Provably better reasoning."** What can honestly be claimed: *this computation is
  exact about these recorded inputs*, and *this measured difference, at matched cost,
  with this uncertainty*. Nothing more general.
- **Coverage guarantees resting on calibration data nobody maintains.** A stale basis
  emitting a live guarantee is worse than no guarantee.
- **A learned selection policy with no outcome data to learn from.**
- **Ceremony as evidence** — confidence that rose because the output passed through
  more stages, rather than because a named uncertainty got resolved.
- **A scaffold whose value depends on the user knowing its catalog.**

---

## 8. What nobody knows yet

These are open questions of the problem itself. We do not expect answers on day one; we
expect any serious design to name its method, and its cost, for getting each one.

1. **What fraction of real-task error is addressable by any scaffold at all?** If most
   of our agents' error is unreachable by procedure, perfect execution caps out early
   and the right system is small. This is the single most decision-relevant unknown.
2. **How is independence between same-model judgments measured, and what does it cost
   to raise it?**
3. **How is a skipped-procedure-with-forged-record detected from outside, during
   ordinary use** — not during a demonstration?
4. **What is the trust-to-accuracy elasticity of structured output** for real readers?
5. **What is the shelf life of any measured gain across model upgrades**, and what does
   re-validation cost per upgrade?
6. **Does any of this help across long horizons** — and by how much? This is the bet
   the whole problem now rests on.
7. **Does thinking inside the scaffold improve the agent's unaided thinking**, or only
   its paperwork?

---

## 9. What we ask of you

Design the scaffold. You have a free hand on method, architecture, and vocabulary —
nothing in our prior attempt binds you, including its framing of the acts, its division
of labor, or its taxonomy.

Begin, before any building, with a design document that answers:

1. How you will measure before you build, and what result would make you stop.
2. How your own null result would be detected, concretely enough for us to audit the
   detector.
3. What you refuse to build, and why. A design with no refusals has not engaged §7.
4. What a consequential task will cost under your design, including the cost of your
   own measurement.
5. The strongest case against your own design — where it is most likely to fail, and
   how we would know before it costs us.
6. Your position on each question in §8 — a method, a cost, or a reason it cannot be
   answered.

We will weigh the measurement plan first, honesty about limits second, and breadth of
capability last. You will have from us: a corpus of real consequential tasks with known
outcomes where they exist; the full record of our prior attempt, including every
negative result; model access and the agent harnesses we use; a human operator for
field observation; and a domain reviewer for the task families.

One last restatement of the heart of it. Humans did not become reliable thinkers by
trying harder; they built counterparts and learned to lean on them — the notebook, the
ledger, the colleague, the referee, the score. We are asking for the equivalent
environment for a mind that can be copied, reset, and replayed, with failure modes we
can now name and measure. Make the leaning possible, make it real rather than
performed, and make the difference show up in a number someone else can check.
