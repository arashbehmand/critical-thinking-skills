# critical-thinking-mcp — instructions for coding agents

Critical-thinking practices for LLM agents, delivered as **recipes + math**. Recipes
(the skills in `skills/`) are procedures the host model follows; whenever a recipe needs
an LLM judgment it has the host spawn a **fresh subagent** for it. The MCP server here
is deliberately the opposite of clever: a **lean set of purely mathematical functions**
that aggregate collected judgments into final decisions (QBAF gradual semantics, ACH
inconsistency scoring, panel statistics, Brier calibration, Fermi intervals).

Companion project: **argLLM** (`~/Projects/argLLM`) — the full machinery tier for
argument mapping, with server-side judgment elicitation. The design doctrine shared by
both lives in `docs/critical-thinking-whitepaper.md`.

## Architecture — enforced dependency direction

```
skills/                 recipes: procedure + prompts; ALL LLM judgments are
                        host-side subagents (fresh minds), never server calls
    │ drives
src/ctmcp/server/       thin FastMCP shell: schema validation, tool annotations
    │ calls
src/ctmcp/core/         pure math, zero I/O — the aggregators
```

- **No LLM calls anywhere in this codebase, ever.** No provider SDKs, no MCP sampling,
  no `ctx.sample()`. When judgment is needed, the recipe instructs the *host* model to
  run a subagent (fresh-mind rule: `skills/critical-thinking/references/conventions.md`
  §2). Judgment sourcing with server-side *guarantees* is argLLM's territory; this
  server guarantees arithmetic only — and its results must be labeled accordingly
  (inputs self-assigned vs subagent-elicited).
- **`core/` is pure**: functions of plain data; no I/O, no MCP imports, deterministic.
  Every formula's docstring cites its source (DF-QuAD — Rago et al. 2016, as used in
  Freedman et al. 2024 arXiv:2405.02079; ACH — Heuer 1999 ch. 8; Brier 1950).
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
`claude mcp add critical-thinking -- uv run --directory /path/to/critical-thinking-mcp ctmcp`.

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

## Licensing / clean-room rules

Same as argLLM: formulas come from the papers, never from the authors' reference repo
(`CLArg-group/argumentative-llms`) or its Uncertainpy fork (restrictive license — may be
consulted only to cross-check behavior). Do not add a license file without direction.

## Non-goals (v0) — do not add without direction

Server-side LLM calls or MCP sampling (argLLM's job) · sessions or persistent server
state (all tools stateless and pure; ledgers live in caller-side `.ct/` files via the
recipes) · PDF/RAG ingestion · web UI · benchmark CLI · a license file.
