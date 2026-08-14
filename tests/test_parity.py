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

import pytest

from ctmcp.core import ach, brier, fermi, panel
from tests.test_core import LEDGER, PIANO_FACTORS, TOY_MATRIX, VOTE_DRAWS, echo_matrix, panel_draws

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


def test_ach_script_matches_core_with_origins(tmp_path: Path) -> None:
    """The collapse rule has to land in both implementations or in neither."""
    matrix = echo_matrix()
    matrix_file = tmp_path / "echo.json"
    matrix_file.write_text(json.dumps(matrix))
    script = run_json(SKILLS / "ct-ach/scripts/ach_score.py", [str(matrix_file), "--json"])
    assert script == ach.score(matrix)
    assert script["origin_clusters"] == {"og-1": ["E2", "E3", "E4"]}


def test_fermi_script_matches_core(tmp_path: Path) -> None:
    factors_file = tmp_path / "factors.json"
    factors_file.write_text(json.dumps({"factors": PIANO_FACTORS}))
    script = run_json(SKILLS / "ct-question-tree/scripts/fermi.py", [str(factors_file), "--json"])
    assert script == fermi.combine(PIANO_FACTORS)


def test_aggregate_numeric_script_matches_core() -> None:
    draws = panel_draws()
    script = run_json(
        SKILLS / "ct-panel/scripts/aggregate.py",
        [
            "--mode",
            "numeric",
            "--json",
            "--source",
            ",".join(d["source"] for d in draws),
            "--pedigree",
            ",".join(d["pedigree"] for d in draws),
            *[str(d["value"]) for d in draws],
        ],
    )
    assert script == panel.numeric(draws)


def test_aggregate_numeric_script_refuses_the_same_invented_draw() -> None:
    """The gate is only a gate if both implementations shut."""
    draws = panel_draws()
    draws[0]["pedigree"] = "invented"  # value 6 — the median of [4, 5, 6, 7, 7]
    result = subprocess.run(
        [
            sys.executable,
            str(SKILLS / "ct-panel/scripts/aggregate.py"),
            "--mode",
            "numeric",
            "--json",
            "--source",
            ",".join(d["source"] for d in draws),
            "--pedigree",
            ",".join(d["pedigree"] for d in draws),
            *[str(d["value"]) for d in draws],
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "refusing to compute" in result.stderr
    with pytest.raises(ValueError, match="refusing to compute"):
        panel.numeric(draws)


def test_aggregate_vote_script_matches_core() -> None:
    script = run_json(
        SKILLS / "ct-panel/scripts/aggregate.py",
        [
            "--mode",
            "vote",
            "--json",
            "--source",
            ",".join(d["source"] for d in VOTE_DRAWS),
            *[d["choice"] for d in VOTE_DRAWS],
        ],
    )
    assert script == panel.vote(VOTE_DRAWS)


def test_brier_script_matches_core(tmp_path: Path) -> None:
    """The one maths script that had no parity test until the resolver breakout landed."""
    ledger = tmp_path / "predictions.jsonl"
    ledger.write_text("".join(json.dumps(e) + "\n" for e in LEDGER))
    script = run_json(
        SKILLS / "ct-calibration/scripts/brier.py",
        ["report", "--file", str(ledger), "--json", "--today", "2026-07-27"],
    )
    assert script == brier.report(LEDGER, today="2026-07-27")
