"""The plugin manifest is how the package installs system-wide; every path it names must exist."""

import json
import re
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = json.loads((REPO / ".claude-plugin/plugin.json").read_text())


def test_manifest_version_matches_the_package() -> None:
    project = tomllib.loads((REPO / "pyproject.toml").read_text())["project"]
    assert MANIFEST["version"] == project["version"]


def test_manifest_skills_directory_holds_every_skill() -> None:
    skills = REPO / MANIFEST["skills"][0]
    assert len(list(skills.glob("*/SKILL.md"))) == 20


def test_hook_commands_point_at_scripts_that_exist() -> None:
    hooks = json.loads((REPO / MANIFEST["hooks"]).read_text())["hooks"]
    commands = [h["command"] for blocks in hooks.values() for b in blocks for h in b["hooks"]]
    assert commands
    for command in commands:
        for script in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+\.py)", command):
            assert (REPO / script).is_file(), script


def test_mcp_server_runs_from_the_plugin_root_not_a_hardcoded_path() -> None:
    server = MANIFEST["mcpServers"]["critical-thinking"]
    assert "${CLAUDE_PLUGIN_ROOT}" in server["args"]
    assert "/Users/" not in json.dumps(server)


def test_marketplace_lists_this_plugin_at_the_repo_root() -> None:
    market = json.loads((REPO / ".claude-plugin/marketplace.json").read_text())
    assert [(p["name"], p["source"]) for p in market["plugins"]] == [(MANIFEST["name"], "./")]
