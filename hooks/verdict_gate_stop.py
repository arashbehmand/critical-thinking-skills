#!/usr/bin/env python3
"""Stop hook: refuse to end a turn that ships a verdict with no gate file.

`ct-verdict-gate` is the one skill in the set that names itself as the weak form:
a checklist in context is still advice, and the model most likely to skip it is
the confident, hurried one — exactly the case the gate targets. The skill ships
the checklist; only a harness hook can ship the lock. This is the lock.

It blocks when BOTH hold:
  * the assistant's final message carries a verdict marker (by default the
    line-anchored labels the gate template itself writes — "Verdict:",
    "Recommendation:", "Decision:", "Final answer:", or "go/no-go"), and
  * no `.ct/gate--*.md` under the project was written during this session.

Passing it is cheap and honest: run the gate, write the file. Every item may be
answered `SKIPPED` with one true sentence — the gate exists to make skipping
*visible*, not forbidden, because forbidding produces pencil-whipping while
candour produces signal.

Deliberately fails OPEN. A hook that crashes a session is worse than a missed
gate, and Claude Code already treats any non-2 exit as non-blocking, so a
malformed payload lets the turn end. This is a lock on the careless path, not a
guarantee against a determined one — it is Tier 2, and Tier 2 buys locks, not
virtue (see docs/critical-thinking-whitepaper.md §4.3).

Install: see hooks/README.md. Stdlib only; no dependency on this repo.
"""

import fnmatch
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

DEFAULT_MARKERS = r"(?im)^\s*(?:verdict|recommendation|decision|final answer)\s*:|go/no-go"
GATE_GLOB = "gate--*.md"
ALLOW, BLOCK = 0, 2


def payload() -> dict[str, Any]:
    raw = sys.stdin.read()
    data: dict[str, Any] = json.loads(raw) if raw.strip() else {}
    return data


def last_reply(data: dict[str, Any]) -> str:
    """The turn's final assistant text, preferring the field over the transcript."""
    direct = data.get("last_assistant_message")
    if isinstance(direct, str) and direct.strip():
        return direct
    return transcript_reply(data.get("transcript_path"))


def transcript_reply(path: object) -> str:
    """Fallback for older hosts: last assistant text block in the transcript JSONL."""
    if not isinstance(path, str) or not path:
        return ""
    try:
        lines = Path(path).read_text(errors="replace").splitlines()
    except OSError:
        return ""
    for line in reversed(lines):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        message = entry.get("message") or {}
        if entry.get("type") != "assistant" and message.get("role") != "assistant":
            continue
        content = message.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = [b.get("text", "") for b in content if isinstance(b, dict)]
            joined = "\n".join(p for p in parts if p)
            if joined.strip():
                return joined
    return ""


def session_start(path: object) -> float | None:
    """Epoch seconds of the transcript's first entry — when this session began."""
    if not isinstance(path, str) or not path:
        return None
    try:
        with open(path, errors="replace") as handle:
            for line in handle:
                try:
                    stamp = json.loads(line).get("timestamp")
                except json.JSONDecodeError:
                    continue
                if not isinstance(stamp, str):
                    continue
                try:
                    return datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp()
                except ValueError:
                    return None
    except OSError:
        return None
    return None


def fresh_gate(root: Path, since: float | None) -> Path | None:
    """A gate file written during this session, or None."""
    gate_dir = root / os.environ.get("CT_GATE_DIR", ".ct")
    try:
        names = os.listdir(gate_dir)
    except OSError:
        return None
    for name in sorted(names):
        if not fnmatch.fnmatch(name, GATE_GLOB):
            continue
        candidate = gate_dir / name
        try:
            written = candidate.stat().st_mtime
        except OSError:
            continue
        # No usable session start (older host, unparsable stamp): any gate counts.
        if since is None or written >= since:
            return candidate
    return None


REASON = """\
This reply ships a verdict, but no gate file was written this session.

Run `ct-verdict-gate` before delivering it: write {gate}/gate--<slug>.md with one
line per item — a link to the artifact, or the word SKIPPED plus one honest
sentence why. SKIPPED is a legitimate pass; a silent skip is what this blocks.
Items 5 (FLIP: what observation would change this) and 7 (FRAGILE: which single
input, if wrong, flips it) have no SKIPPED option.

Then deliver the verdict with its strongest surviving counter-argument beside it
and the gate path cited. If this reply is not actually a verdict, say so plainly
and stop again — this hook blocks at most once per turn.\
"""


def main() -> int:
    try:
        data = payload()
    except json.JSONDecodeError:
        return ALLOW  # fail open: never wedge a session on a malformed payload

    # Already blocked once this turn — let it stop rather than trap the model.
    if data.get("stop_hook_active"):
        return ALLOW

    markers = os.environ.get("CT_VERDICT_MARKERS") or DEFAULT_MARKERS
    try:
        pattern = re.compile(markers)
    except re.error:
        return ALLOW
    if not pattern.search(last_reply(data)):
        return ALLOW

    root = Path(str(data.get("cwd") or ".")).expanduser()
    if fresh_gate(root, session_start(data.get("transcript_path"))):
        return ALLOW

    print(REASON.format(gate=os.environ.get("CT_GATE_DIR", ".ct")), file=sys.stderr)
    return BLOCK


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as err:  # fail open, loudly, never fatally
        print(f"verdict_gate_stop: {err}", file=sys.stderr)
        sys.exit(ALLOW)
