---
name: ct-counterexample
description: Try to falsify a universal claim, invariant, guarantee, specification, or proposed rule by finding and shrinking one admissible counterexample, using execution, tests, search, or a solver before model judgment. Use for "always", "never", "must", "cannot", "guaranteed", safety properties, API invariants, mathematical conjectures, and designs whose correctness depends on all cases; distinguishes a proved result from bounded search that merely found no witness.
argument-hint: [the claim to try to break]
---

# Counterexample search — one witness beats a page of objections

Universal claims are asymmetric: one admissible witness can kill them, while a hundred
friendly examples cannot prove them. Search for the witness directly. The valuable part
is not "be sceptical"; it is moving the claim into an independently constrained channel
whenever execution, enumeration, property tests, or a solver can decide a case.

## Procedure

1. **Freeze the claim** in `.ct/counterexample--<slug>.md`. Pin:
   - the exact conclusion;
   - the admissible domain;
   - every premise a candidate must satisfy;
   - the quantifier (`all`, `none`, `for every`, or an invariant over steps).

   If these are ambiguous, run `ct-definition-pin` first. A witness outside the domain is
   not a counterexample.
2. **Choose the strongest available oracle**, in this order:
   - exhaustive enumeration over a finite domain;
   - compilation, execution, tests, property-based generation, or simulation with a
     deterministic checker;
   - SAT/SMT/constraint/model checking where a faithful encoding is available;
   - retrieval of a documented real case with claim-level entailment checking;
   - only then, a fresh counterexample hunter using template T12.
3. **Search the boundaries first.** Empty, zero, one, maximum, minimum, duplicate,
   adversarial ordering, sign change, unit change, concurrency, missing value, and the
   transition between two stated regimes are common places where universals break. Use
   domain-appropriate boundaries; do not paste this list mechanically into every task.
4. **Validate a candidate independently.** Check both halves:
   - it satisfies every frozen premise;
   - the conclusion actually fails under the chosen oracle.

   A model-authored story that merely sounds awkward is not a witness.
5. **Shrink it.** Remove inputs, steps, entities, and conditions while the failure
   survives. The smallest witness exposes the real assumption and is easier to preserve
   as a regression test.
6. **Classify the result honestly:**
   - `DISPROVED` — a validated witness exists;
   - `PROVED_WITHIN_FORMALISATION` — exhaustive search or a sound formal certificate
     covers the frozen domain, with the encoding and scope named;
   - `SURVIVED_BOUNDED_SEARCH` — no witness found in the stated search; not proof;
   - `UNKNOWN` — the claim could not be made checkable or the oracle failed.
7. **Repair, do not erase.** If the user's intent survives, write the narrowest revised
   claim that excludes the witness for a principled reason, keep the original and the
   witness, then search the revision again. A patch that merely names the observed case
   is overfitting unless that case reveals a real missing premise.

## Artifact

```markdown
# Frozen claim: …
Domain: …
Premises: …
Oracle: …
Search scope: …

Result: DISPROVED | PROVED_WITHIN_FORMALISATION | SURVIVED_BOUNDED_SEARCH | UNKNOWN
Witness: … | none found
Premise check: …
Failure check: …
Shrunk from: …
Unsearched boundary: …
Revised claim: … | none
```

Where the witness is executable, keep it as a test beside the receipt when the user has
authorized code changes. The `.ct/` artifact records the reasoning; the regression test
is the lasting lock.

## Integrity rules

- Never weaken a premise after seeing a candidate. Reject the candidate or record a
  revised claim; do not silently move the goalposts.
- `NO_COUNTEREXAMPLE_FOUND` is forbidden wording in the final verdict unless immediately
  followed by the search boundary. Prefer `SURVIVED_BOUNDED_SEARCH`.
- A timeout, solver `UNKNOWN`, flaky test, or failed retrieval is `UNKNOWN`, never
  evidence for the claim.
- A proof is only about the encoded domain. Report the formalisation gap beside the
  certificate, not in a footnote.

## Limits

Open-world empirical generalizations rarely have enumerable domains, and fresh-model
hunters share the generator's blind spots. In those cases this is a disciplined search,
not a verifier. Its strongest form is deliberately opportunistic: use it when the task
already offers a real oracle. Otherwise the receipt makes the search boundary visible
and nothing more.

Part of the critical-thinking set — selected automatically by the `critical-thinking`
controller when one concrete witness could decide more than another round of critique.
