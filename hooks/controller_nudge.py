#!/usr/bin/env python3
"""UserPromptSubmit hook: hand the controller to the model when the request looks consequential.

The v1.4 measurement is blunt about why this exists. With the skills installed but not
mentioned, Claude Haiku 4.5 opened one in **0 of 200 runs**; told to use the controller on
the same items it opened it in 200 of 200 and answered 14 points better than a plain run
and 10 points better than a plain run at higher effort. Availability is not uptake. The
skill text cannot fix that — only something outside the model can put the instruction in
front of it, which is the Tier 2 job (docs/critical-thinking-whitepaper.md §4.3).

So this hook does one small thing: on a prompt whose *wording* matches a deterministic
trigger, it appends one line asking the model to run the `critical-thinking` controller and
reminding it that `NO_SCAFFOLD` is a valid outcome. It never picks an act, never mentions
the catalog to the user, and fires at most once per session so a long conversation is not
nagged. Every decision, fired or skipped, is appended to `.ct/nudge-log.jsonl`, so the
engage rate is measurable from outside the model rather than from its own account.

Deliberately fails OPEN: any bad payload, unreadable state file or unexpected error exits
0 with no output, and the turn proceeds untouched.

Install: see hooks/README.md. Stdlib only; no dependency on this repo.
"""

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

# Wording that has repeatedly preceded a consequential answer. Deliberately narrow: a
# trigger that fires on everything is the "always engage" failure the whitepaper names.
TRIGGERS: dict[str, str] = {
    "decision": r"(?i)\b(should (we|i|they)|which (option|approach|one)|worth it|go/no-go"
    r"|trade-?off|decide between)\b",
    "estimate": r"(?i)\b(how (many|much|long)|estimate|roughly|order of magnitude|capacity"
    r"|throughput|budget)\b",
    "diagnosis": r"(?i)\b(why (did|does|is|are|would)|root cause|what explains"
    r"|keeps? (failing|happening|breaking))\b",
    "universal": r"(?i)\b(always|never|guarantee[sd]?|cannot happen|impossible|every case"
    r"|invariant)\b",
    "risk": r"(?i)\b(irreversible|production|outage|migrat(e|ion)|roll ?back|safety|incident"
    r"|data loss)\b",
    "verdict": r"(?i)\b(is it (safe|correct|true)|are you sure|what am i missing"
    r"|how confident)\b",
}
NUDGE = (
    "This request matched a consequential-work trigger ({matched}). Before answering, run the "
    "`critical-thinking` controller skill to choose the smallest useful act, and follow it. "
    "`NO_SCAFFOLD` is a valid outcome — most requests deserve no ceremony. Do not ask the user "
    "to pick a technique."
)
STATE, LOG = ".ct/nudge-state.json", ".ct/nudge-log.jsonl"


def matched_triggers(prompt: str) -> list[str]:
    return sorted(name for name, pattern in TRIGGERS.items() if re.search(pattern, prompt))


def record(root: Path, entry: dict[str, Any]) -> None:
    path = root / LOG
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as out:
        out.write(json.dumps(entry) + "\n")


def already_fired(root: Path, session: str) -> bool:
    try:
        state: dict[str, Any] = json.loads((root / STATE).read_text())
    except (OSError, ValueError):
        return False
    return bool(state.get("session") == session)


def main() -> int:
    raw = sys.stdin.read()
    data: dict[str, Any] = json.loads(raw) if raw.strip() else {}
    prompt = str(data.get("prompt") or "")
    session = str(data.get("session_id") or "")
    root = Path(str(data.get("cwd") or os.getcwd()))

    matched = matched_triggers(prompt)
    fired = bool(matched) and not already_fired(root, session)
    record(
        root,
        {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "session": session,
            "matched": matched,
            "fired": fired,
            "chars": len(prompt),
        },
    )
    if not fired:
        return 0

    (root / STATE).write_text(json.dumps({"session": session, "ts": time.time()}))
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": NUDGE.format(matched=", ".join(matched)),
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # fail open: a hook that breaks a session is worse than a missed nudge
        sys.exit(0)
