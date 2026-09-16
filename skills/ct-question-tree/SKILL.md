---
name: ct-question-tree
description: Splits a big or vague question into small sub-questions answered separately, and builds the answer only from those parts; its Fermi mode turns a number nobody has a source for into factor ranges combined by a bundled interval-arithmetic script. Use for broad or vague questions, multi-part comparisons, and "estimate how many/much" questions with no direct source; when the user says "break this down" or an honest answer needs several distinct facts. Not for a problem whose exact answer a solver, search or simulation can compute from the data given (that is ct-formalize).
argument-hint: [the big question]
---

# Question tree

A big question is usually five smaller ones wearing a coat. Answered in one jump, some of
the five get skipped — and you cannot see which. Split it, answer the parts on their own,
and let the final answer be assembled from parts you can point at.

This is not `ct-formalize`. A question tree splits a question into parts and, in Fermi
mode, estimates a number from guessed factor ranges. When the data is given and a solver,
search or simulation can compute the exact answer, formalize instead.

## Procedure

1. **Write the root question verbatim** at the top of `.ct/tree--<slug>.md`.
2. **Decompose** into 2–7 children. Do it yourself, or use template T7
   (the `critical-thinking` skill's `references/subagent-templates.md`) for a second opinion. Test each
   set: every child answerable on its own; answering all children settles the parent
   *mechanically* — no overlaps, no gaps. If T7 reports a "Residue", add a child for it.
3. **Recurse only where a child is still too big.** Three levels is the ceiling — deeper
   trees are usually avoidance, not analysis.
4. **Answer the leaves independently.**
   - Factual leaves: look them up; record the source next to the answer.
   - Judgment leaves: get the answer from a fresh subagent (conventions §2) so the
     parent's desired conclusion cannot leak downward.
   - Unanswerable leaves: mark `UNKNOWN` and carry the uncertainty up. Never silently
     fill a leaf with a guess dressed as a fact.
5. **Synthesize upward.** A parent's answer may cite **only** its children's answers. If
   the synthesis needs something no child provides, that is a missing child — add it and
   answer it first. This binding is what makes the tree real rather than decorative.
6. Deliver the root answer citing the artifact path.

## Artifact format

```markdown
# Q: <root question>
Status: ANSWERED | PARTIAL (n UNKNOWN leaves)

## 1. <child question> — ANSWERED
<answer> [source: …]
### 1.1 <grandchild> — …
## 2. <child question> — UNKNOWN
<why, and what would answer it>

# Root answer
<assembled strictly from the children above>
```

## Fermi mode (numeric estimates)

For "how many / how much" with no direct source:

1. Decompose the quantity into 3–6 **factors** that multiply or divide
   (`answers = population × rate ÷ capacity …`).
2. Each factor gets a `[low, high]` range **and a `pedigree`** — `sourced` when you
   looked it up, `elicited` when a fresh subagent supplied the range (asked for the range
   only, never your target number: anchoring flows downhill), `given` when it was handed
   to you, `invented` when you made it up.
3. Combine with the bundled script — never in your head:

   `<skill-dir>` is the folder this skill was loaded from; with the `critical-thinking` server connected, its `combine_fermi` tool computes the same result.

   ```sh
   python3 <skill-dir>/scripts/fermi.py factors.json
   ```

   Input: `{"factors": [{"name": "US households", "low": 1.2e8, "high": 1.4e8,
   "op": "multiply", "pedigree": "sourced"}, …]}` (first factor's `op` is ignored;
   `divide` uses interval division). Output: combined `[low, high]`, a geometric-mean
   point estimate, each factor's span ratio, and which factors are load-bearing.
4. **Report the range, not just the point.** The script names the widest factor — that is
   where an hour of research buys the most narrowing.

**The script refuses an invented load-bearing factor.** Load-bearing is mechanical, not a
judgment call: a factor whose `log10(high/low)` share of the total is at or above the
average, or that is stated as a point (`low == high`), which asserts a precision nobody
sourced. The measure is *uncertainty contributed*, not size — the census-sized multiplier
is the one somebody looked up; the guessed share is the one carrying a 3× range. When it
refuses, go get the range: that is the whole instruction. Do not relabel the factor to get
past the gate — `invented` is an honest answer, and an estimate with a hole in it reported
as a hole is worth more than a decimal nobody can defend.

## Integrity rules

- Decompose **before** drafting an answer. A tree drawn around an existing answer is
  decoration and will inherit its blind spots.
- Do not prune or reword children whose answers point somewhere inconvenient; an
  inconvenient child is a finding.
- If two decompositions give materially different answers, that disagreement is itself
  the headline — report it, don't pick quietly.

## Limits

The synthesis binding (step 5) is discipline: nothing stops a lawyer from citing children
selectively. That enforcement would need a workflow engine that checks the citation graph
— low value for this act; the discipline plus a visible artifact catches most of it. See
`docs/critical-thinking-whitepaper.md`.

Part of the critical-thinking set — see the `critical-thinking` skill for routing and
shared conventions.
