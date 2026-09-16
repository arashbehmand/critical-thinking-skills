---
name: ct-formalize
description: Recognize the formal shape of a problem — allocation under constraints, a graph, a scheduling or satisfiability question, waiting and queues, noisy measurement, feedback and delay, uncertainty over inputs — then write it down as that object in code and let a solver, enumeration or simulation answer it instead of reasoning it out in prose. Also borrows a discipline's machinery when the behavior is familiar even if the domain is not. Use for optimization, allocation, scheduling, routing, capacity, dependency and reachability questions, rate and stock models, threshold and error-cost tradeoffs, "what is the best/most/least/fastest", "will this converge", "why does this keep oscillating", "our error is stuck", and any quantitative answer someone will act on.
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
   provenance tag in a comment: `measured`, `cited`, or `assumed`.
3. **Let a machine answer it.** Preference order: exact solver → exhaustive enumeration
   (when the space is small) → simulation → a formula recalled from memory. Recalled
   formulas are the weakest link in the chain; check one against a brute-force case.
4. **Attack the encoding before you trust the number.** Reproduce a case whose answer you
   already know. Check units and dimensions. Run a degenerate case (zero demand, one
   server, all costs equal) and confirm the answer is the boring one. Confirm the objective
   moves the right way when you push an input.
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
Checks: known case reproduced · units · degenerate case · objective direction
Sensitivity: <input → answer range>; flips at <value> if it flips
Exact about: the encoding above. Not a claim about the world.
Frames tried and dropped: <frame → the prediction it got wrong>
```

## Integrity rules

- The model file ships with the answer. A number whose code cannot be shown is prose.
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
- **Unmeasured.** The v1.4 measurements cover abstention on underdetermined word problems,
  not this act. Nothing here is evidence that formalizing improves outcomes; it is the
  standard argument that computation beats recall on the property it checks.
