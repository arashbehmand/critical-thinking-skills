"""The Tier 2 lock, driven the way the harness drives it: JSON on stdin, exit code out.

`hooks/verdict_gate_stop.py` is stdlib-only and standalone — it never imports this
package — so it is exercised as a subprocess rather than called.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

HOOK = Path(__file__).resolve().parent.parent / "hooks/verdict_gate_stop.py"
ALLOW, BLOCK = 0, 2
VERDICT = "Verdict: ship the migration on Friday."


def transcript(tmp_path: Path, started: str = "2026-08-13T09:00:00Z") -> Path:
    path = tmp_path / "transcript.jsonl"
    path.write_text(
        json.dumps({"type": "user", "timestamp": started, "message": {"role": "user"}}) + "\n"
    )
    return path


def gate(tmp_path: Path, name: str = "gate--migration.md") -> Path:
    ct = tmp_path / ".ct"
    ct.mkdir(exist_ok=True)
    path = ct / name
    path.write_text("# Gate\n\nVerdict: ship it\n")
    return path


def run(
    payload: dict[str, Any], env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
        env={"PATH": "/usr/bin:/bin", **(env or {})},
    )


def stop_payload(tmp_path: Path, message: str = VERDICT, **extra: Any) -> dict[str, Any]:
    return {
        "session_id": "s-1",
        "hook_event_name": "Stop",
        "cwd": str(tmp_path),
        "transcript_path": str(transcript(tmp_path)),
        "last_assistant_message": message,
        "stop_hook_active": False,
        **extra,
    }


def test_blocks_a_verdict_with_no_gate_file(tmp_path: Path) -> None:
    result = run(stop_payload(tmp_path))
    assert result.returncode == BLOCK
    assert "no gate file was written this session" in result.stderr
    assert "SKIPPED is a legitimate pass" in result.stderr


def test_allows_a_verdict_once_the_gate_exists(tmp_path: Path) -> None:
    payload = stop_payload(tmp_path)
    gate(tmp_path)  # written after the transcript's first timestamp
    assert run(payload).returncode == ALLOW


def test_allows_an_ordinary_reply(tmp_path: Path) -> None:
    """No verdict marker, no gate needed — the hook must stay out of the way."""
    payload = stop_payload(tmp_path, message="Here is the diff; tests pass locally.")
    assert run(payload).returncode == ALLOW


@pytest.mark.parametrize(
    "message",
    [
        "Recommendation: hold the release.",
        "Decision: roll forward.",
        "Final answer: 42",
        "This is a go/no-go call and I say go.",
    ],
)
def test_recognises_each_default_marker(tmp_path: Path, message: str) -> None:
    assert run(stop_payload(tmp_path, message=message)).returncode == BLOCK


def test_marker_must_be_a_label_not_a_passing_mention(tmp_path: Path) -> None:
    """'the verdict: ...' mid-sentence is prose, not a shipped conclusion."""
    payload = stop_payload(tmp_path, message="I read the verdict: it was unconvincing.")
    assert run(payload).returncode == ALLOW


def test_blocks_at_most_once_per_turn(tmp_path: Path) -> None:
    """A model that considers the block and disagrees may say so and stop."""
    payload = stop_payload(tmp_path, stop_hook_active=True)
    assert run(payload).returncode == ALLOW


def test_a_stale_gate_from_an_earlier_session_does_not_count(tmp_path: Path) -> None:
    stale = gate(tmp_path)
    os.utime(stale, (0, 0))  # written long before this session started
    assert run(stop_payload(tmp_path)).returncode == BLOCK


def test_falls_back_to_the_transcript_when_the_message_field_is_absent(tmp_path: Path) -> None:
    path = tmp_path / "transcript.jsonl"
    path.write_text(
        json.dumps({"type": "user", "timestamp": "2026-08-13T09:00:00Z", "message": {}})
        + "\n"
        + json.dumps(
            {
                "type": "assistant",
                "message": {"role": "assistant", "content": [{"type": "text", "text": VERDICT}]},
            }
        )
        + "\n"
    )
    payload = {
        "hook_event_name": "Stop",
        "cwd": str(tmp_path),
        "transcript_path": str(path),
        "stop_hook_active": False,
    }
    assert run(payload).returncode == BLOCK


def test_custom_markers_and_gate_dir_are_honoured(tmp_path: Path) -> None:
    env = {"CT_VERDICT_MARKERS": r"(?i)ship it", "CT_GATE_DIR": "receipts"}
    payload = stop_payload(tmp_path, message="ship it")
    assert run(payload, env).returncode == BLOCK

    receipts = tmp_path / "receipts"
    receipts.mkdir()
    (receipts / "gate--x.md").write_text("ok")
    assert run(payload, env).returncode == ALLOW


def test_fails_open_on_a_malformed_payload() -> None:
    """A hook that wedges a session is worse than a missed gate."""
    result = subprocess.run(
        [sys.executable, str(HOOK)], input="not json", capture_output=True, text=True, check=False
    )
    assert result.returncode == ALLOW


def test_fails_open_on_an_unreadable_transcript(tmp_path: Path) -> None:
    payload = {
        "hook_event_name": "Stop",
        "cwd": str(tmp_path),
        "transcript_path": str(tmp_path / "missing.jsonl"),
        "stop_hook_active": False,
    }
    assert run(payload).returncode == ALLOW
