---
name: ct-argument-map
description: Drive the argLLM MCP server to build a quantitative argument map (QBAF) for a contested claim - the verdict computed by gradual semantics from fresh-context base scores, then contested by editing scores and adding, removing, or expanding arguments, with sensitivity probing for flip points. Use when a contested claim needs a transparent, contestable verdict; when the user says "map the arguments", "verify this claim", or "what would change the verdict". Requires the argllm MCP server (degraded fallback documented inside).
argument-hint: [the claim to verify]
---

# Argument map (argLLM orchestration)

This is the one act in the set whose core is deliberately **not** a skill. In argLLM,
every argument's base score (τ) is elicited server-side from a fresh context — the
orchestrating model never types τ itself; pydantic validators enforce the tree shape at
every boundary; strength (σ) is recomputed per response as a pure function of the
structure and never stored; every edit is copy-on-write with a revision history. A
skill-only argument map, where the same mind that holds the lean writes all the numbers
into a file, is a lawyer with a spreadsheet. This skill is the *driver's manual* for the
machinery, not a replacement.

## Drive procedure

1. **Build.** `evaluate_claim` with the claim verbatim. Defaults (depth 1, breadth 1)
   are the paper's; use depth 2, breadth 2 for genuinely contested claims. Returns a
   session id, the rendered tree (every node id quotable), σ(claim), and the verdict —
   σ > 0.5 → True, otherwise False.
2. **Read.** `inspect_qbaf`. Actually read the arguments; the contest loop responds to
   their content, not their scores.
3. **Contest — an uncontested map is a first draft, not a verdict.** At least one edit
   before trusting anything:
   - an argument is factually wrong or weak → `set_base_score` (or `remove_argument`);
   - a consideration is missing → `add_argument` (pro or con, with the text);
   - a subtree is thin where the action is → `expand_argument`.

   Every mutation returns old vs new σ and verdict plus a new revision — record verdict
   flips in your notes as you go.
4. **Probe sensitivity — find the flip set.** For each leaf argument: `set_base_score`
   to 0.0, note σ(claim); restore the original τ; then 1.0; note; restore. (Revisions
   make this safe; always end back on the real τ.) Leaves whose extremes flip the
   verdict are the **flip set** — the arguments actually carrying the conclusion, and
   therefore the ones whose truth is worth checking hardest (send them through
   `ct-evidence-ledger` or `ct-ach` if contested).
5. **Export the receipt.** `export_qbaf` → save to `.ct/qbaf--<slug>.json`
   (`import_qbaf` resumes it in a later session — sessions are in-memory by design).
6. **Report:** the verdict and σ at the final revision; the flip set; what single edit
   *would* flip the verdict. That last line is the contestability statement — the
   invitation for a human to disagree productively.

## Integrity rules

- Never present σ from a stale revision — every reported number names its revision.
- Contesting means engaging the argument's *content*; setting a con-argument's τ to 0
  because it is inconvenient is exactly the move the server exists to make visible (the
  revision history shows it, which is the point).
- The flip-set probe (step 4) is not optional on consequential claims: a verdict whose
  fragility is unknown is unfinished.

## Degraded mode (argLLM unavailable) — two rungs, label which you used

1. **Preferred — subagent scores + mechanical aggregation.** If the
   critical-thinking-mcp math server is registered: draft the tree yourself (claim,
   pro/con arguments, parents); elicit each argument's base score from a **fresh
   subagent** — one per argument, template T4 with the question "how likely is this
   statement to be true? end with `ANSWER: <0–1>`", never showing your lean or the
   other scores — then call `evaluate_qbaf` with the tree and the elicited scores.
   Label the result *"subagent-elicited scores, mechanical aggregation — independence
   unenforced"*. This is the middle rung: more honest than a hand map (fresh minds
   supplied the numbers, arithmetic delivered the verdict), less than argLLM (nothing
   enforced the independence).
2. **Last resort — hand map.** A markdown file whose first line is
   **`UNENFORCED — self-assigned scores`**; its numbers carry no authority beyond your
   own say-so, and the honest alternative is usually better: `ct-steelman` +
   `ct-verdict-gate`, which at least get fresh minds into the loop.

Either way, name the gap; do not present the output as if the machinery had run.

## Why machinery (the general lesson)

Of the whole set, this act needs guarantees a skill cannot give: validated structure,
judgment sourcing from fresh contexts, recomputed-never-stored strengths, and an edit
history that cannot be quietly rewritten. That is what an MCP server *is for* — see
`docs/critical-thinking-whitepaper.md` for the classification, and the `argllm://method`
resource for the methodology.

Part of the critical-thinking set — see the `critical-thinking` skill for routing and
shared conventions.
