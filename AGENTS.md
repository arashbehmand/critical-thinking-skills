# critical-thinking-skills — instructions for coding agents

Critical-thinking practices for LLM agents, delivered as **recipes + math**. Recipes
(the skills in `skills/`) are procedures the host model follows; whenever a recipe needs
an LLM judgment it has the host spawn a **fresh subagent** for it. The MCP server here
is deliberately the opposite of clever: a **lean set of purely deterministic functions**
that aggregate collected judgments or inspect recorded structure (QBAF gradual
semantics, ACH inconsistency scoring, panel statistics, Brier calibration, Fermi
intervals, truth-maintenance withdrawal impact).

Companion project: **argLLM** (`~/Projects/argLLM`) — the full machinery tier for
argument mapping, with server-side judgment elicitation. The design doctrine shared by
both lives in `docs/critical-thinking-whitepaper.md`.

## Architecture — enforced dependency direction

```
hooks/                  Tier 2 locks: standalone harness scripts (Stop hook), run by
                        the agent runtime, importing nothing from this package
skills/                 recipes: procedure + prompts; ALL LLM judgments are
                        host-side subagents (fresh minds), never server calls
    │ drives
src/ctmcp/server/       thin FastMCP shell: schema validation, tool annotations
    │ calls
src/ctmcp/core/         pure math, zero I/O — the aggregators

bench/                  measurement, not shipped and currently NOT COMMITTED (.gitignore,
                        along with tests/test_bench.py which imports it). Off to the
                        side; nothing in src/, skills/ or hooks/ depends on it.
```

- **No LLM calls anywhere in this codebase, ever.** No provider SDKs, no MCP sampling,
  no `ctx.sample()`. When judgment is needed, the recipe instructs the *host* model to
  run a subagent (fresh-mind rule: `skills/critical-thinking/references/conventions.md`
  §2). Judgment sourcing with server-side *guarantees* is argLLM's territory; this
  server guarantees arithmetic only — and its results must be labeled accordingly
  (inputs self-assigned vs subagent-elicited). **This covers `bench/`**: the process
  audit is a protocol a host agent runs by hand, plus deterministic scripts that score
  the artifacts afterwards. The generator and the scorers never call a model.
- **Gate over label.** Where a self-administered check finds a disqualifying input, it
  *refuses* rather than computing and disclaiming — a disclaimer beside a number reads as
  care, not as a warning. `aggregate_numeric` and `combine_fermi` refuse an `invented`
  load-bearing input; each states the *mechanical* rule by which it decided that, because
  a load-bearing test left to judgment is a label again.
- **`core/` is pure**: functions of plain data; no I/O, no MCP imports, deterministic.
  Every formula or algorithm's docstring cites its source (DF-QuAD — Rago et al. 2016,
  as used in Freedman et al. 2024 arXiv:2405.02079; ACH — Heuer 1999 ch. 8; Brier 1950;
  truth maintenance — Doyle 1979).
- **`server/` is thin**: pydantic input models, calls into core, sets tool annotations.
  Every tool is pure → `readOnlyHint=True, idempotentHint=True`, always.
- **Bundled skill scripts stay standalone.** `skills/*/scripts/*.py` are stdlib-only on
  purpose: recipes must work in hosts where this server is not registered. Script and
  core implementations of the same math must agree — parity tests pin script `--json`
  output equal to core output. Change both together or neither.

## Commands

```sh
uv sync                      # install (Python 3.13, uv-managed; uv.lock committed)
uv run pytest                # offline test suite
uv run ruff check
uv run ruff format --check
uv run mypy                  # strict
```

Run the server: `ctmcp` / `python -m ctmcp` / `fastmcp run src/ctmcp/server/app.py:mcp`.
Register with Claude Code:
`claude mcp add critical-thinking -- uv run --directory /path/to/critical-thinking-skills ctmcp`.

Every change must end green on all four commands above. Do not commit unless asked.

## Doctrine (short form — whitepaper is the long form)

- **The lawyer test** decides delivery tiers: an act that still works when the model is
  motivated ships as a skill; an act whose value depends on a guarantee needs machinery.
- Three tiers: **skill** (method) → **harness hook** (locks) → **service** (guarantees).
  This server is a Tier-3 service for *arithmetic only*; it does not and must not claim
  elicitation guarantees.
- **Receipts**: every recipe ends with an artifact under `.ct/` and the final answer
  cites it. Server outputs echo the rule they applied so a reader can check by hand.

## Working discipline

- **Simplicity first.** Minimum code that solves the problem; no speculative features,
  no new abstractions. The extension seams are: a new pure function in `core/` + a thin
  tool in `server/` + a recipe in `skills/` that uses it. Nothing else without asking.
- **Surgical changes**; match existing style; formulas and parsing decisions come from
  the cited papers — reread the source before guessing.
- **Tests are the spec.** Exact-value tests pin the math (hand-computed); parity tests
  pin script↔core agreement; new behavior lands with tests in the same change.
- **Skills are prompts.** SKILL.md `description:` fields are the triggers — trigger-rich,
  third person. Keep the plain-language voice; the fresh-mind rule in recipe wording is
  non-negotiable.

## Layout notes

- `skills/` is canonical. `.claude/skills` is a symlink to it, so the skills are live
  when working inside this repo. Installing elsewhere = copy skill directories into that
  project's `.claude/skills/` (or `~/.claude/skills/` for global use); each skill's
  scripts travel with its directory.
- `CLAUDE.md` is a symlink to this file — keep everything here agent-agnostic.
- `hooks/` holds harness locks, not library code: standalone stdlib scripts the agent
  runtime executes, installed by path from `.claude/settings.json`. They import nothing
  from `src/ctmcp` and must **fail open** — a hook that wedges a session is worse than
  the check it skipped.
- `bench/` is measurement and is **gitignored for now**, together with
  `tests/test_bench.py`, which imports it. Both exist locally; neither is in the
  repository. `pyproject.toml` therefore leaves `bench` out of the ruff and mypy targets
  and excludes that one test file, so a fresh clone still comes up green on all four
  commands — check that it does before changing those lists.
- Docs still cite `bench/` where a measurement from it changed a decision (the ACH
  mutual-exclusivity premise, the withdrawal of per-cell accuracy). Those citations point
  at unpublished work on purpose: the finding is real and the reasoning should be
  followable, so keep the citation and keep the caveat rather than deleting either.

## Licensing / clean-room rules

Same as argLLM: formulas come from the papers, never from the authors' reference repo
(`CLArg-group/argumentative-llms`) or its Uncertainpy fork (restrictive license — may be
consulted only to cross-check behavior). Do not add a license file without direction.

## Non-goals (v0) — do not add without direction

Server-side LLM calls or MCP sampling (argLLM's job) · sessions or persistent server
state (all tools stateless and pure; ledgers live in caller-side `.ct/` files via the
recipes) · PDF/RAG ingestion · web UI · a benchmark CLI *in the shipped package* (`bench/`
is out-of-package measurement and is in scope; `src/ctmcp` stays aggregators-only) · a
license file.

Also out, and named so they cannot creep back: multi-attribute utility machinery or
consistency ratios over elicited weights · expected-value-of-information arithmetic over
invented utilities · equilibrium computation over invented payoff matrices · belief
filtering or planning over invented dynamics · factor-graph inference over invented
factors · chain-reliability arithmetic over guessed per-step rates · conformal or credal
infrastructure (it needs maintained labelled calibration sets, and a stale set emitting a
live guarantee is worse than none) · a trained router. The common property: each computes
exactly over quantities the model invented, and defends itself with a label rather than a
refusal.
