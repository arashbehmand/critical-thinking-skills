# critical-thinking-skills

[![skills.sh](https://skills.sh/b/arashbehmand/critical-thinking-skills)](https://skills.sh/arashbehmand/critical-thinking-skills)

Critical-thinking for LLM agents, split the way the evidence says it should be:

- **Recipes** (`skills/`) — twenty agent skills in the open Agent Skills format (Claude
  Code, Codex, opencode, Cursor and other agents read them), led by an **autonomous
  controller** that recognizes the problem shape, chooses the minimum useful act, and
  treats `NO_SCAFFOLD` as a valid route. The user describes the problem; they do not
  select techniques. Whenever a recipe needs an LLM judgment, the host spawns a **fresh
  subagent** — a mind that never saw the draft or the lean.
- **Math** (`src/ctmcp/`) — a lean MCP server of **purely mathematical aggregators**
  that turn collected judgments into final decisions, deterministically: QBAF gradual
  semantics (DF-QuAD), ACH inconsistency scoring with flip-cell sensitivity, panel
  statistics, Brier calibration bins, Fermi interval arithmetic, and truth-maintenance
  withdrawal impact over recorded commitment dependencies. No LLM calls, no state, no
  cleverness — same input, same output, rule printed with the result.
- **Locks** (`hooks/`) — the harness rung between the two: standalone stdlib scripts the
  agent runtime runs. A `UserPromptSubmit` hook that hands the controller over on
  consequential requests, and a `Stop` hook that refuses to end a turn shipping a verdict
  with no gate file. Claude Code only. See [hooks/README.md](hooks/README.md).
- **Measurement** (`bench/`) — a seeded adversarial instance generator with hidden ground
  truth, exact scorers, and the process-vs-artifact audit protocol. **Not in this
  repository yet** — it is kept local while the instrument is still being corrected, so
  references to `bench/` in the docs below describe work that exists but is unpublished.
  Findings from it are quoted where they changed a decision.

The design doctrine — which practices a skill can carry, which need machinery, and why —
is in **[docs/critical-thinking-whitepaper.md](docs/critical-thinking-whitepaper.md)**.
The one-line version: *the controller selects, method lives in recipes, judgments come
from fresh subagents, verdicts come from arithmetic*. The full machinery tier for
argument mapping (with server-side judgment elicitation) is the companion project
[argLLM](https://github.com/arashbehmand/argLLM).

## Install

### Skills, for any agent

```sh
npx skills add arashbehmand/critical-thinking-skills --list   # see the twenty skills
npx skills add arashbehmand/critical-thinking-skills -g -y     # install all of them
npx skills update -g            # later: pick up changes
```

`-g` installs into `~/.agents/skills/` (read by Codex, opencode, Cursor, GitHub Copilot,
Gemini CLI and others) and links each skill into `~/.claude/skills/`. Without `-g` the
skills go into the current project instead. To choose skills, add `--skill <name>` once per
skill, and keep `critical-thinking` in the set: the other skills use its shared conventions
and fresh-mind templates. `gh skill install arashbehmand/critical-thinking-skills` reads the same layout.

Skills that need an independent judgment spawn a subagent with the agent's own tool. Where an
agent has none, the skill runs the judgment in context and says so in its receipt
(`fresh-mind: degraded (same context)`).

### Claude Code, full install

The plugin adds the math server and the controller nudge hook to the same twenty skills. Use
it instead of the `npx skills` install for Claude Code, not as well: both at once list every
skill twice.

```sh
claude plugin marketplace add arashbehmand/critical-thinking-skills
claude plugin install critical-thinking@critical-thinking-skills --scope user
```

Skills are then named `critical-thinking:ct-ach`, `critical-thinking:ct-formalize`, and so
on. To try it for one session without installing anything, clone the repository and run
`claude --plugin-dir /path/to/critical-thinking-skills`.

The plugin ships only the nudge hook. The verdict gate (`hooks/verdict_gate_stop.py`) blocks
a reply once when it carries a verdict label and no gate file exists; add it to
`~/.claude/settings.json` by hand if you want that lock everywhere (see
[hooks/README.md](hooks/README.md)).

### The math server, for other agents

The skills work without it: every calculation also ships as a standard-library script inside
its skill. The server gives agents the same calculations as MCP tools, and runs from a clone
of this repository:

```sh
codex mcp add critical-thinking -- uv run --directory /path/to/critical-thinking-skills ctmcp
```

For opencode, add to `~/.config/opencode/opencode.json`:

```json
{
  "mcp": {
    "critical-thinking": {
      "type": "local",
      "command": ["uv", "run", "--directory", "/path/to/critical-thinking-skills", "ctmcp"]
    }
  }
}
```

The server also serves the skills as `skill://` resources for MCP clients that cannot load
skills. That route is weaker: a model reaches a recipe only by reading it from the server, and
never sees the skill descriptions while choosing (checked 2026-09-16: with only the server,
Claude Code listed none of the twenty skills).

### Receipts

Skills write their receipts under `.ct/` in whatever project you are in. Keep them out of git
everywhere with `echo ".ct/" >> ~/.gitignore_global` (or your global excludes file).

### Development

```sh
uv sync
uv run pytest        # offline
```

## Tools (all pure functions)

| Tool | Aggregates | Rule |
|---|---|---|
| `evaluate_qbaf` | a pro/con argument tree with base scores | DF-QuAD gradual semantics; σ(root) > 0.5 → True |
| `score_ach` | a hypotheses × evidence rating matrix | least weighted inconsistency wins (Heuer); reports flip cells |
| `aggregate_numeric` | independent numeric judgments | median + spread, disagreement flag |
| `aggregate_vote` | independent categorical picks | plurality + share, tie/weak-plurality flag |
| `score_calibration` | resolved probability predictions | Brier score + per-bin stated-vs-happened |
| `combine_fermi` | factor ranges for an estimate | interval arithmetic, geometric-mean point |
| `analyze_dependencies` | an append-only commitment dependency record | simulate each active withdrawal; rank recorded transitive impact |

Honesty rule: report separately what came from external evidence, what was independently
computed, and what was only structured or elicited by the model. A deterministic tool is
exact about its inputs; it does not certify that the model supplied a faithful
formalisation. `analyze_dependencies`, for example, is exact about recorded edges and
cannot detect a dependency the author never logged.

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
