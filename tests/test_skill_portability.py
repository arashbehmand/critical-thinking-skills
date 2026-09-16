"""Each skill must work after an installer copies only its own folder somewhere else.

`npx skills`, `gh skill` and Claude Code plugins copy `skills/<name>/` on its own, into
`~/.agents/skills/<name>`, `~/.claude/skills/<name>` or a plugin cache. A path written relative
to this repository's root, a file reached by climbing out of the folder, or a pointer at
`hooks/` all resolve to nothing there.
"""

import re
from pathlib import Path

import pytest

SKILLS = Path(__file__).resolve().parent.parent / "skills"
NAMES = sorted(p.parent.name for p in SKILLS.glob("*/SKILL.md"))
DOCS = sorted(SKILLS.glob("*/**/*.md"))
HARNESS_TABLE = {
    "critical-thinking/references/conventions.md",
    "critical-thinking/references/subagent-templates.md",
}


def rel(path: Path) -> str:
    return str(path.relative_to(SKILLS))


@pytest.mark.parametrize("doc", DOCS, ids=rel)
def test_no_repo_root_or_escaping_paths(doc: Path) -> None:
    text = doc.read_text()
    assert not re.search(r"\bskills/[a-z-]+/", text), "repo-root skill path"
    assert "../" not in text, "path climbs out of the skill folder"
    assert not re.search(r"\bhooks/", text), "hooks/ does not ship with a skill"


@pytest.mark.parametrize("doc", DOCS, ids=rel)
def test_harness_tool_names_live_only_in_the_conventions_table(doc: Path) -> None:
    if rel(doc) in HARNESS_TABLE:
        return
    assert not re.search(r"\bAgent tool\b|`Agent`|\bTask tool\b|`task`", doc.read_text())


@pytest.mark.parametrize("name", NAMES)
def test_every_script_a_skill_runs_is_in_its_own_folder(name: str) -> None:
    text = (SKILLS / name / "SKILL.md").read_text()
    for script in re.findall(r"<skill-dir>/scripts/([\w.-]+\.py)", text):
        assert (SKILLS / name / "scripts" / script).is_file(), script


@pytest.mark.parametrize("doc", DOCS, ids=rel)
def test_named_cross_skill_references_exist(doc: Path) -> None:
    for skill, target in re.findall(
        r"the `([a-z-]+)` skill's `(references/[\w.-]+)`", doc.read_text()
    ):
        assert (SKILLS / skill / target).is_file(), f"{skill}/{target}"


def test_fresh_mind_rule_says_what_to_do_without_a_subagent_tool() -> None:
    conventions = (SKILLS / "critical-thinking/references/conventions.md").read_text()
    assert "fresh-mind: degraded (same context)" in conventions
