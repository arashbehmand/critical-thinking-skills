---
name: ct-sanity-check
description: Before computing from a representation you built — an equation, a model file, parsed or retyped data, a table, a graph, a diagram, a spreadsheet — step back and check the representation itself against what must be true of it. Counts match the source, units balance, totals are conserved, formulas reduce to cases you can solve another way, quantities stay in bounds, and the shape rules still hold: triangle angles sum to 180, parallel lines do not meet, probabilities sum to one, adding a server never makes the wait longer. Catches the wrong-model-exact-answer failure. Use after writing a model or formula, after parsing or copying data out of a problem, before trusting any computed result, and whenever a clean-looking table or plot is about to be believed.
argument-hint: [the model, table, formula or data you are about to compute from]
---

# Sanity check — look at the representation before you crunch it

A result that came out of code, a spreadsheet or a derivation is usually arithmetically
right. What goes wrong is the thing it was computed on: a row dropped while copying the
data, a formula recalled with a factor missing, a sign flipped, a rate left in hours when
everything else is in minutes. The number that comes out is exact and wrong, and the
table around it makes it look careful.

A practised engineer or mathematician looks at the page before trusting the crunch: do
the angles still add to 180, did the parallel lines stay parallel, does the balance sheet
balance. This act is that look, made explicit, and every check in it is executed rather
than eyeballed.

## What must be true — the check catalog

| Check | The question | Example |
|---|---|---|
| Round trip | Render the representation back into the source's form. Does it match? | print the parsed graph as `A->B cost` lines and diff them against the problem text |
| Counts | Does it hold as many things as the source says or shows? | 48 edges in the problem, 48 in the model; 15 items; an 8×8 matrix |
| Units and dimensions | Do both sides of every equation carry the same units? | calls per minute against service rate per minute, not per hour |
| Conservation | Does what goes in equal what comes out? | money, mass, people; probabilities sum to 1; flow in equals flow out at every node |
| Bounds | Is every quantity in its legal range? | probabilities in [0, 1], waits ≥ 0, utilization < 1 for a stable queue |
| Limit case | Does it reduce to a case you can solve a different way? | one agent gives the single-server formula; zero arrivals gives zero wait |
| Direction | Does it move the right way when you push an input? | more agents never lengthen the wait; more capacity never lowers the best value |
| Structure | Do the rules of the shape still hold? | triangle angles sum to 180°; parallel lines never meet; a tree on n nodes has n−1 edges; a schedule has no job in two places |
| Symmetry | If the problem is symmetric, is the answer? | swapping two identical items cannot change the total |
| Second method | Does a different method agree on a small instance? | brute force against the formula; a quick simulation against the closed form |

## Procedure

1. **Stop before the answer.** Name the representation you are about to trust: the file,
   the equation, the table, the diagram.
2. **Pick the checks that must hold for it**, usually three to five. Two are not optional:
   - anything taken from a source (numbers, edges, rows, clauses) gets a **count** or a
     **round trip** against that source;
   - any formula written from memory gets a **limit case** or a **second method** that does
     not reuse the formula.
3. **Execute each check.** Print the diff, run the limit case, compute the totals. A check
   you only read and agreed with is not a check.
4. **If a check fails, fix the representation, then run every check again.** Never adjust
   the answer to make a check pass.
5. **Only then compute the result**, and report the checks next to it.

## Artifact

Write `.ct/sanity-<slug>.md` and cite it with the answer. Fill every row from output you
actually produced; the placeholders below are not results.

```markdown
# Sanity check — <what was checked>
Representation: <file / equation / table>
| Check | How it was run | Result | Fix made |
|---|---|---|---|
| count: <items> | parsed <n>, source lists <m> | <pass/FAIL> | <what you changed, or —> |
| limit case: <case> | <this method's value> vs <independent method's value> | <pass/FAIL> | <fix> |
| direction: <input pushed> | <how the output moved> | <pass/FAIL> | <fix> |
Could not check: <invariant — why>
```

## Integrity rules

- **Executed, not asserted.** Every row records how the check was run and what it printed.
- **Independent, not circular.** A limit case or second method must not reuse the code or
  formula it is testing. Re-running the same function and getting the same number checks
  nothing.
- **Failures stay in the record.** A check that failed and was fixed is the most useful
  line in the artifact; never delete it.
- **"Could not check" is a valid answer.** Name the invariant and the reason. A silent gap
  looks like a pass.

## Limits

- **Consistency is not correctness.** A representation can pass every check and still model
  the wrong problem; that is `ct-reframe`'s job, not this one.
- **Choosing the checks is judgment.** A missing invariant is invisible, which is why the
  two mandatory checks exist.
- **Evidence so far is a probe, not a study.** In 10 exploratory Haiku runs of
  `ct-formalize` on hard instances, both confident wrong answers from running code were
  exactly what these two checks catch: a graph retyped with 10 of 48 edges missing, and an
  Erlang C formula recalled with a factor dropped, which a one-agent case at a light load
  exposes. After this skill and the copy-and-parse rule were added, the next 10 runs
  printed their edge counts or tested the formula against a simulation, and all 10 were
  right. Ten runs cannot separate that from luck.
