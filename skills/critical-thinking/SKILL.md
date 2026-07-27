---
name: critical-thinking
description: Router for the critical-thinking skill set — picks the right thinking act for the task. Use when careful reasoning is needed and it is unclear which act applies - verifying a contested claim, choosing between explanations, making a decision, estimating an unknown, or checking a conclusion before shipping it. Triggers - "think critically", "are you sure", "check your reasoning", "what am I missing", "how confident are you".
argument-hint: [question, claim, or decision to think through]
---

# Critical thinking — the skill set

This set turns critical-thinking acts into procedures a model actually runs, instead of
advice it half-remembers. Every skill in the set applies the same three moves:

1. **Externalize** — the thinking goes into a structure (a tree, a table, a ledger), not
   into prose. Working memory is small; the file is the notebook.
2. **Mechanize** — arithmetic and counting are done by bundled scripts, never in-head.
   Same input, same output.
3. **Contest** — judgments come from fresh minds (subagents that never saw your draft),
   and every act leaves an artifact someone can attack.

## Routing table

| You are about to… | Use |
|---|---|
| answer a big or vague question in one jump | `ct-question-tree` |
| estimate a number you cannot look up | `ct-question-tree` (Fermi mode) |
| argue about a loaded word ("safe", "better", "significant") | `ct-definition-pin` |
| wrestle a slippery or badly-formatted problem | `ct-reformat` |
| rely on a claim with unstated premises | `ct-assumption-audit` |
| conclude on a contested question | `ct-steelman`, then `ct-verdict-gate` |
| choose between explanations of the same evidence | `ct-ach` |
| deliver a fact-heavy answer | `ct-evidence-ledger` |
| work a long multi-step task | `ct-consistency-log` |
| make a noisy one-shot judgment (score, grade, pick-one) | `ct-panel` |
| commit to a plan or irreversible decision | `ct-premortem` |
| state a probability that matters later | `ct-calibration` |
| produce a quantitative, contestable verdict on a claim | `ct-argument-map` (argLLM MCP) |

Acts compose. A serious contested-claim job typically runs: `ct-definition-pin` →
`ct-argument-map` (or `ct-steelman`) → `ct-evidence-ledger` → `ct-verdict-gate`.

## Shared conventions (read before first use)

The full text lives in [references/conventions.md](references/conventions.md). The four
rules that must never be broken:

- **Receipts.** Every act writes its artifact under `.ct/` and the final answer cites the
  path. The artifact is the transparency.
- **Fresh minds.** When a step calls for an independent judgment, it comes from a subagent
  whose prompt contains the question and raw materials only — never your draft, your lean,
  or which side is "ours". Copy the exact prompts from
  [references/subagent-templates.md](references/subagent-templates.md).
- **Script arithmetic.** Numbers are combined by the bundled scripts, not in prose.
- **Append-only ledgers.** Corrections supersede; they never overwrite.

## Honesty note

These skills are procedures, not enforcement. Each one documents, under "Limits", what a
skill cannot guarantee and what machinery (an MCP server, a harness hook) would. The
classification lives in `docs/critical-thinking-whitepaper.md`. The one-line test used
there: *does the act still work when the model is being a lawyer?* If yes, the skill
suffices. If it only works because something outside the model refuses to let the
lawyering through, it needs machinery — and the skill says so rather than pretending.
