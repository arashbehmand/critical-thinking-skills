# critical-thinking-mcp

Critical-thinking for LLM agents, split the way the evidence says it should be:

- **Recipes** (`skills/`) — sixteen Claude Code skills that turn validated
  critical-thinking practices (steelmanning, competing-hypotheses analysis, premortems,
  entailment checking, calibration score-keeping, …) into procedures a model actually
  runs. Whenever a recipe needs an LLM judgment, the host model spawns a **fresh
  subagent** for it — a mind that never saw the draft or the lean.
- **Math** (`src/ctmcp/`) — a lean MCP server of **purely mathematical aggregators**
  that turn collected judgments into final decisions, deterministically: QBAF gradual
  semantics (DF-QuAD), ACH inconsistency scoring with flip-cell sensitivity, panel
  statistics, Brier calibration bins, Fermi interval arithmetic. No LLM calls, no state,
  no cleverness — same input, same output, rule printed with the result.
- **Locks** (`hooks/`) — the harness rung between the two: standalone stdlib scripts the
  agent runtime runs. Currently one `Stop` hook that refuses to end a turn shipping a
  verdict with no gate file. See [hooks/README.md](hooks/README.md).
- **Measurement** (`bench/`) — a seeded adversarial instance generator with hidden ground
  truth, exact scorers, and the process-vs-artifact audit protocol. **Not in this
  repository yet** — it is kept local while the instrument is still being corrected, so
  references to `bench/` in the docs below describe work that exists but is unpublished.
  Findings from it are quoted where they changed a decision.

The design doctrine — which practices a skill can carry, which need machinery, and why —
is in **[docs/critical-thinking-whitepaper.md](docs/critical-thinking-whitepaper.md)**.
The one-line version: *method* lives in recipes, *judgments* come from fresh subagents,
*verdicts* come from arithmetic. The full machinery tier for argument mapping (with
server-side judgment elicitation) is the companion project
[argLLM](https://github.com/arashbehmand/argLLM).

## Install

```sh
uv sync
uv run pytest        # offline
```

Register the math server with Claude Code:

```sh
claude mcp add critical-thinking -- uv run --directory /path/to/critical-thinking-mcp ctmcp
```

The MCP server also advertises all sixteen recipes as `skill://` resources. An
MCP client can list `skill://<name>/SKILL.md` resources to discover the practices,
then read a chosen one (and its supporting files) before calling its math tools. They
remain live inside this repo too (`.claude/skills` → `skills/`); for hosts without MCP
skill-resource support, copy the skill directories into that project's `.claude/skills/`
or into `~/.claude/skills/` for global use.

## Tools (all pure functions)

| Tool | Aggregates | Rule |
|---|---|---|
| `evaluate_qbaf` | a pro/con argument tree with base scores | DF-QuAD gradual semantics; σ(root) > 0.5 → True |
| `score_ach` | a hypotheses × evidence rating matrix | least weighted inconsistency wins (Heuer); reports flip cells |
| `aggregate_numeric` | independent numeric judgments | median + spread, disagreement flag |
| `aggregate_vote` | independent categorical picks | plurality + share, tie/weak-plurality flag |
| `score_calibration` | resolved probability predictions | Brier score + per-bin stated-vs-happened |
| `combine_fermi` | factor ranges for an estimate | interval arithmetic, geometric-mean point |

Honesty rule: these tools aggregate whatever they are given. Feed them self-assigned
numbers and they will faithfully aggregate a lawyer's spreadsheet — label inputs
(self-assigned vs subagent-elicited) when reporting results, as the recipes instruct.

Two places the labelling is not left to you, because a disclaimer beside a number reads
as care rather than as a warning:

- **Pedigree gate.** `aggregate_numeric` and `combine_fermi` require a `pedigree` per
  input — `given` / `sourced` / `elicited` / `invented` — and **refuse** when an
  `invented` one is load-bearing. Load-bearing is mechanical, and each tool prints the
  rule it used: for a panel, the draw at the median position; for a Fermi estimate, a
  factor at or above the average share of the total `log10(high/low)`, or one stated as a
  point. An invented outlier a median already absorbs still computes — and says so.
- **Composition.** Every panel draw names its `source`, so five draws from one model and
  three models plus a human stop printing identically. A panel of one model cancels
  *noise*, not shared bias.

`score_ach` deliberately has no pedigree gate: ordinal C/I/N cells over 1–3 credibility
already sit near the honest resolution limit of the judgment, and the output is a ranking
plus flip cells rather than a decimal. The gate belongs where exact arithmetic meets
continuous invented inputs, not everywhere a judgment enters.
