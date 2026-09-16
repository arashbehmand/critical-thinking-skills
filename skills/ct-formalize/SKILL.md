---
name: ct-formalize
description: Keeps the question and hands the answering to a machine — names the formal object underneath (an allocation, schedule, graph, queue, feedback loop, noisy measurement, or a range of uncertain inputs), writes it as a model in code, runs a solver, enumeration or simulation, and then attacks the encoding. Use for best, most, least or fastest questions, capacity, scheduling, routing, dependency and reachability, threshold and error-cost tradeoffs, things that oscillate or never converge, and any number someone will act on that is being worked out in prose. Not when a clear restatement makes the answer doable by hand (that is ct-reformat), not when the question itself may be the wrong one (that is ct-reframe), and not for a rough estimate built from guessed factors (that is ct-question-tree, Fermi mode).
argument-hint: [the problem that might be an ordinary formal object in disguise]
---

# Formalize and compute — stop doing it in your head

Many hard-looking questions are ordinary objects wearing domain clothes. Crew rosters and
ad budgets are the same assignment problem. A release plan and a chemical plant are both
stocks, flows and delays. The costly move is answering them in prose, where the arithmetic
is invisible, the constraints are half-remembered, and nothing checks the result.

The act: **name the object, write it as that object in a file, let a machine answer it, then
attack the encoding.** The leverage is independent computation — it adds no evidence about
the world, and it replaces fallible in-head work on the property it actually checks.

This is not `ct-reformat`, whose restatement makes a problem doable by hand; formalize is
for answers a careful person should not be computing by hand at all. Nor is it
`ct-reframe`: formalize takes the question as given and makes it exact, so run reframe
first if the question itself is in doubt.

## Shape catalog — the signal, then the object

| The problem sounds like | It is usually | Reach for |
|---|---|---|
| split a limited resource to get the most/least of something | linear or integer program | `scipy.optimize.linprog`, PuLP, OR-Tools; tiny cases: enumerate |
| fit jobs to slots/people under rules | constraint program | OR-Tools CP-SAT; tiny cases: `itertools` + a checker |
| a set of yes/no choices must satisfy conditions | SAT / SMT | `z3-solver`; tiny cases: brute force all assignments |
| things connect to things; reachability, cycles, bottleneck, dependency, shortest path | graph | `networkx`; stdlib: dict of lists + BFS/DFS/topological sort |
| arrivals, servers, waiting, utilization | queueing | M/M/c formulas, or a simple event simulation |
| noisy readings over time, want the true state | estimation / filtering | Bayes update or Kalman filter over the data you have |
| it overshoots, oscillates, or never settles after a change | control | model the loop with its delay and simulate a step response |
| stocks, flows, delays, feedback over time | system dynamics | Euler or discrete-step simulation |
| inputs are ranges, not numbers | Monte Carlo | sample inputs, report the distribution and the tails |
| rare but very costly events | reliability / extreme value | model the tail; averages will mislead |
| a threshold trades one error against the other | decision theory | cost-weighted threshold, ROC; state the cost ratio |
| parties respond to each other's choices | game theory | small payoff matrix, best responses, check the tie |
| "how many/much" with no source to look up | Fermi estimate | `ct-question-tree` Fermi mode — don't rebuild it here |

The catalog is a prompt, not a taxonomy. If the shape is not on it, describe the behavior
in one sentence and ask which field studies that behavior (next section).

## Procedure

1. **Name the object in one sentence.** "This is an assignment problem with a capacity
   limit and a fairness constraint." If you cannot name it, say so and stop — a forced fit
   produces an exact answer to the wrong question. Naming nothing is a valid outcome.
2. **Write the model in a file, not in prose.** Sets, decision variables, constraints,
   objective, data, units. Keep it small enough to read in one screen. Every input gets a
   provenance tag in a comment: `measured`, `cited`, or `assumed`. **Data enters by copy,
   never by retyping:** paste the problem's data block into the file as-is and parse it in
   code. Retyping 48 edges by hand is how 10 of them go missing.
3. **Let a machine answer it.** Preference order: exact solver → exhaustive enumeration
   (when the space is small) → simulation → a formula recalled from memory. **Running the
   model is the act.** An answer you did not get by executing the model is not a
   `ct-formalize` result; if you answer without running it, say so plainly.
4. **Run `ct-sanity-check` on the model before you trust the number.** At minimum: a count
   or round trip for every block of data taken from the problem, and a limit case or second
   method for every formula written from memory — one that does not reuse that formula.
   Then units, and one check that the answer moves the right way when you push an input.
5. **Sensitivity, computed not asserted.** Re-run with each load-bearing input at its
   plausible bounds. Report which input moves the answer most. If the answer flips inside
   an input's uncertainty, the flip is the finding, not the point estimate.
6. **Say what the computation is exact about.** It is exact about the model you encoded.
   Whether the model matches the world is a judgment, and it stays labelled as one.

## Borrowing a discipline

When the shape has no name in your domain, describe the *behavior* and ask which field has
studied that behavior for fifty years.

| The behavior | The field that owns it | The question it hands you |
|---|---|---|
| error stays high although the sensor got better | estimation theory | is the limit observability rather than precision? |
| each fix overshoots and sets off the next | control theory | is the loop gain too high, or the feedback delayed? |
| averages look fine, the bad case ruins us | reliability, extreme value | what does the tail do, not the mean? |
| everyone behaves sensibly and the outcome is bad | game theory, mechanism design | what do the incentives make optimal? |
| the process drifts until someone intervenes | statistical process control | is this common-cause noise or a real shift? |
| more data, no better decisions | information theory, value of information | which measurement would actually change the choice? |

Rules for borrowing: the frame is a hypothesis, not an answer. It earns its place only by
making a prediction you can check against data you already have. Record the frames you
tried and dropped — a rejected frame is cheap to record and expensive to re-try.

## Artifact

Write `.ct/model-<slug>.md` next to the model code, and cite it in the answer:

```markdown
# Model — <one-line object name>
Code: <path>            Tool: <solver/library + version>
Inputs: <name = value (measured|cited|assumed, source)> …
Result: <the number or set, with units>
Checks: .ct/sanity-<slug>.md (counts / round trip, limit case, units, direction)
Sensitivity: <input → answer range>; flips at <value> if it flips
Exact about: the encoding above. Not a claim about the world.
Frames tried and dropped: <frame → the prediction it got wrong>
```

## Integrity rules

- The model file ships with the answer. A number whose code cannot be shown is prose.
- No retyped data. Parse it from a pasted copy of the source and check the count.
- No untested formula from memory. It passes a limit case or a second method first.
- Inputs carry provenance. If a load-bearing input is `assumed` and the answer depends on
  it, that dependency is the finding — report it rather than a confident number. The
  `aggregate_numeric` and `combine_fermi` tools refuse this case outright; do the same here.
- Do not invent coefficients to complete a model. A missing coefficient is a gap; name it.
- No new dependency without need. Enumeration and simulation with the standard library
  answer most small problems, and they run where a solver is not installed.
- The solver certifies the encoded statement, never the modelling choice.

## Limits

- **Formalisation is the weak point.** A wrong model computes an exact wrong answer, and
  its structure makes the wrong answer more persuasive. Step 4 exists for this and does not
  remove it.
- **Cost.** Writing a model costs more than a guess. Use it when the answer matters, when
  the shape is recognizable, or when the guess has already failed twice.
- **Barely measured.** In an exploratory Haiku probe on five hard instances, ordering this
  act first got code run in 9 of 10 runs with 8 correct: the errors had moved from
  arithmetic into the encoding (a retyped graph, a misremembered formula). With the copy,
  run and sanity-check rules added, the next 10 runs ran code 10 times and were all
  correct, against 9 of 10 for plain Haiku. Ten runs a side is a behaviour check, not
  evidence of an accuracy gain.
