# hooks — the Tier 2 rung

Skills provide *method*. Services provide *guarantees*. Between them sits the harness:
enforcement without domain logic — gates in the agent runtime that block a transition
until an artifact exists. This directory is that rung, and it currently holds two hooks.

Nothing here is imported by `src/ctmcp`, ships in the wheel, or calls a model. A hook is
a standalone stdlib script the *harness* runs.

## `verdict_gate_stop.py` — the lock for `ct-verdict-gate`

`ct-verdict-gate` says on its own label that it is the weak, skippable form: a checklist
in context is advice, and the model most likely to skip it is the confident, hurried one
— exactly the case it targets. This hook is the enforcement the skill names and could
not ship.

It refuses to end a turn when **both**:

- the assistant's final message carries a verdict marker — by default the line-anchored
  labels the gate template itself writes (`Verdict:`, `Recommendation:`, `Decision:`,
  `Final answer:`) or `go/no-go`; and
- no `.ct/gate--*.md` was written during this session.

Passing it is cheap: run the gate, write the file. Every item may be answered `SKIPPED`
with one honest sentence — the gate makes skipping **visible**, not forbidden, because
forbidding produces pencil-whipping while candour produces signal.

### Install

Add to `.claude/settings.json` (project) or `~/.claude/settings.json` (global):

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 /absolute/path/to/critical-thinking-mcp/hooks/verdict_gate_stop.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

Inside a project that vendors the skills, `${CLAUDE_PROJECT_DIR}/.claude/hooks/verdict_gate_stop.py`
is the tidier path — copy the file there and reference it that way. `Stop` takes no
matcher; it always fires.

### Configuration

| Env var | Default | Meaning |
|---|---|---|
| `CT_VERDICT_MARKERS` | line-anchored `Verdict:` / `Recommendation:` / `Decision:` / `Final answer:` / `go/no-go` | Python regex deciding what counts as shipping a verdict |
| `CT_GATE_DIR` | `.ct` | where gate files live, relative to the session `cwd` |

Widen `CT_VERDICT_MARKERS` and the hook fires on ordinary replies; narrow it and it stops
catching the case it exists for. The default deliberately matches the gate template's own
`Verdict:` line, so the marker and the artifact are the same convention.

### Mechanics

Blocks with **exit code 2** and the reason on stderr — the documented, version-stable way
for a `Stop` hook to prevent the turn ending. It honours `stop_hook_active`, so it blocks
**at most once per turn**: a model that considers the block and disagrees can say so and
stop again. That is deliberate. A gate that cannot be passed is a gate that gets
uninstalled.

"This session" means a gate file whose mtime is at or after the first timestamp in the
transcript. On hosts that expose neither `last_assistant_message` nor a parsable
transcript, it degrades to "any gate file exists" rather than blocking blindly.

### What it does not do

It **fails open**. A malformed payload, an unreadable transcript, or an unexpected error
lets the turn end — a hook that wedges a session is worse than a missed gate, and Claude
Code already treats any non-2 exit as non-blocking.

It cannot tell a real gate from a file with the right name and seven lines of
`SKIPPED: obviously fine`. It checks that the artifact **exists**, not that the procedure
**ran** — the fourth guarantee in the whitepaper, and precisely the gap
`bench/process_audit/` is built to measure. Tier 2 buys locks, not virtue.


## `controller_nudge.py` — the lock for uptake

`critical-thinking` is an autonomous controller, but only if something opens it. The v1.4
measurement says nothing does: with the skills installed and unmentioned, Haiku 4.5 opened
one in **0 of 200 runs**. Ordered to use the controller on the same items it opened it in
200 of 200 and scored 83.3% against 68.8% plain and 72.9% for a plain run at high effort.
Availability is not uptake, and no wording inside a skill file can change that — the
instruction has to arrive from outside the model.

This hook runs on `UserPromptSubmit`. When the prompt's wording matches one of six narrow
triggers (decision, estimate, diagnosis, universal claim, risk, verdict), it appends one
line: run the controller, `NO_SCAFFOLD` is a valid outcome, do not hand the user a menu. It
fires **at most once per session**, names no act, and writes every decision — fired or not —
to `.ct/nudge-log.jsonl`, so the engage rate is a number from outside the model instead of
its own account of what it did.

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {"hooks": [{"type": "command", "command": "python3 /path/to/hooks/controller_nudge.py"}]}
    ]
  }
}
```

Fails open like the other hook: a malformed payload, an unreadable state file, or any
unexpected error exits 0 with no output. It is a nudge with a log, not a gate — whether it
closes the uptake gap is an open measurement (`bench/`, arm `hook-nudged`), not a claim.
