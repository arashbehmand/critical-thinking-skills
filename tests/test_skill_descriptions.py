"""Skill descriptions are what a model reads when choosing: they must parse and name real skills.

A description is a plain YAML scalar, so a colon followed by a space inside it can break
parsing (it did once: "the shape rules still hold: triangle angles…"). And every
description that says "that is ct-X" is telling a model where to go instead, so ct-X has to
exist.
"""

import re
from pathlib import Path

import pytest

SKILLS = Path(__file__).resolve().parent.parent / "skills"
NAMES = sorted(p.parent.name for p in SKILLS.glob("*/SKILL.md"))


def description(name: str) -> str:
    text = (SKILLS / name / "SKILL.md").read_text()
    match = re.search(r"^description: (.*)$", text, re.MULTILINE)
    assert match, f"{name}: no description line"
    return match.group(1)


@pytest.mark.parametrize("name", NAMES)
def test_description_is_a_safe_plain_scalar(name: str) -> None:
    text = description(name)
    assert ": " not in text, f"{name}: ': ' inside an unquoted description breaks YAML"
    assert " #" not in text, f"{name}: ' #' starts a YAML comment"


@pytest.mark.parametrize("name", NAMES)
def test_every_named_neighbour_exists(name: str) -> None:
    referenced = set(re.findall(r"\b(ct-[a-z-]+)", description(name))) - {name}
    assert referenced <= set(NAMES), f"{name} points at missing skills: {referenced - set(NAMES)}"


@pytest.mark.parametrize(
    ("skill", "neighbour"),
    [
        ("ct-panel", "ct-ensemble"),
        ("ct-ensemble", "ct-panel"),
        ("ct-reformat", "ct-reframe"),
        ("ct-reformat", "ct-formalize"),
        ("ct-reframe", "ct-reformat"),
        ("ct-reframe", "ct-formalize"),
        ("ct-formalize", "ct-reformat"),
        ("ct-formalize", "ct-reframe"),
        ("ct-ach", "ct-ensemble"),
        ("ct-steelman", "ct-premortem"),
        ("ct-premortem", "ct-steelman"),
        ("ct-evidence-ledger", "ct-entailment"),
        ("ct-entailment", "ct-evidence-ledger"),
        ("ct-counterexample", "ct-sanity-check"),
        ("ct-sanity-check", "ct-counterexample"),
    ],
)
def test_confusable_pairs_name_each_other_where_the_model_chooses(
    skill: str, neighbour: str
) -> None:
    assert neighbour in description(skill)
