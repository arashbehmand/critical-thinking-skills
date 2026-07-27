"""Script ↔ core parity.

The stdlib-only scripts bundled inside the skills and the core package must
compute identical results (AGENTS.md rule: change both together or neither).
Pinned here by running each script with --json and comparing to core output.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from ctmcp.core import ach, fermi, panel
from tests.test_core import PIANO_FACTORS, TOY_MATRIX

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"


def run_json(script: Path, args: list[str]) -> Any:
    result = subprocess.run(
        [sys.executable, str(script), *args], capture_output=True, text=True, check=True
    )
    return json.loads(result.stdout)


def test_ach_script_matches_core(tmp_path: Path) -> None:
    matrix_file = tmp_path / "matrix.json"
    matrix_file.write_text(json.dumps(TOY_MATRIX))
    script = run_json(SKILLS / "ct-ach/scripts/ach_score.py", [str(matrix_file), "--json"])
    assert script == ach.score(TOY_MATRIX)


def test_fermi_script_matches_core(tmp_path: Path) -> None:
    factors_file = tmp_path / "factors.json"
    factors_file.write_text(json.dumps({"factors": PIANO_FACTORS}))
    script = run_json(SKILLS / "ct-question-tree/scripts/fermi.py", [str(factors_file), "--json"])
    assert script == fermi.combine(PIANO_FACTORS)


def test_aggregate_numeric_script_matches_core() -> None:
    values = ["6", "7", "4", "7", "5"]
    script = run_json(
        SKILLS / "ct-panel/scripts/aggregate.py", ["--mode", "numeric", "--json", *values]
    )
    assert script == panel.numeric([float(v) for v in values])


def test_aggregate_vote_script_matches_core() -> None:
    votes = ["A", "B", "A", "A", "C"]
    script = run_json(
        SKILLS / "ct-panel/scripts/aggregate.py", ["--mode", "vote", "--json", *votes]
    )
    assert script == panel.vote(votes)
