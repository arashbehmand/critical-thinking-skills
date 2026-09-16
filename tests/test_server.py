"""The thin shell: tools wired to core, pure annotations set, validation → ToolError."""

from pathlib import Path

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from ctmcp.server.app import mcp

EXPECTED_TOOLS = {
    "evaluate_qbaf",
    "score_ach",
    "aggregate_numeric",
    "aggregate_vote",
    "score_calibration",
    "combine_fermi",
    "analyze_dependencies",
}

EXPECTED_SKILLS = {
    p.parent.name for p in (Path(__file__).resolve().parent.parent / "skills").glob("*/SKILL.md")
}


async def test_all_tools_registered_and_pure() -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()
        assert {t.name for t in tools} == EXPECTED_TOOLS
        for tool in tools:
            assert tool.annotations is not None, tool.name
            assert tool.annotations.readOnlyHint is True, tool.name
            assert tool.annotations.idempotentHint is True, tool.name


async def test_all_skills_are_advertised_as_resources() -> None:
    async with Client(mcp) as client:
        resources = await client.list_resources()
        uris = {str(resource.uri) for resource in resources}
        expected_uris = {
            f"skill://{skill}/{file_name}"
            for skill in EXPECTED_SKILLS
            for file_name in ("SKILL.md", "_manifest")
        }
        assert expected_uris <= uris
        advertised = {
            uri.split("/")[2]
            for uri in uris
            if uri.startswith("skill://") and uri.endswith("/SKILL.md")
        }
        assert advertised == EXPECTED_SKILLS

        skill = await client.read_resource("skill://ct-ach/SKILL.md")
        assert "# ACH — analysis of competing hypotheses" in skill[0].text


async def test_evaluate_qbaf_end_to_end() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "evaluate_qbaf",
            {
                "arguments": [
                    {"id": "claim", "base_score": 0.5},
                    {"id": "A1", "base_score": 0.8, "parent_id": "claim", "stance": "con"},
                    {"id": "S1", "base_score": 0.4, "parent_id": "claim", "stance": "pro"},
                ]
            },
        )
        assert result.data["verdict"] is False
        assert result.data["root_strength"] == pytest.approx(0.3)
        assert "DF-QuAD" in result.data["rule"]


async def test_score_ach_end_to_end() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "score_ach",
            {
                "question": "q",
                "hypotheses": [{"id": "H1", "text": "one"}, {"id": "H2", "text": "two"}],
                "evidence": [{"id": "E1", "text": "e1", "credibility": 3}],
                "ratings": [
                    {"evidence_id": "E1", "hypothesis_id": "H1", "rating": "I"},
                    {"evidence_id": "E1", "hypothesis_id": "H2", "rating": "C"},
                ],
            },
        )
        assert result.data["ranking"] == ["H2", "H1"]


async def test_aggregate_numeric_reports_composition_end_to_end() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "aggregate_numeric",
            {
                "draws": [
                    {"value": 6, "source": "opus", "pedigree": "elicited"},
                    {"value": 7, "source": "opus", "pedigree": "elicited"},
                    {"value": 4, "source": "human", "pedigree": "given"},
                ]
            },
        )
        assert result.data["median"] == 6
        assert result.data["composition"] == {"opus": 2, "human": 1}
        assert result.data["distinct_sources"] == 2


async def test_pedigree_gate_refuses_at_the_tool_boundary() -> None:
    """The gate has to shut through MCP too, or it is only a convention in core."""
    async with Client(mcp) as client:
        with pytest.raises(ToolError, match="refusing to compute"):
            await client.call_tool(
                "aggregate_numeric",
                {
                    "draws": [
                        {"value": 6, "source": "self", "pedigree": "invented"},
                        {"value": 7, "source": "opus", "pedigree": "elicited"},
                        {"value": 4, "source": "opus", "pedigree": "elicited"},
                    ]
                },
            )


async def test_combine_fermi_refuses_an_invented_load_bearing_factor() -> None:
    async with Client(mcp) as client:
        with pytest.raises(ToolError, match="refusing to compute"):
            await client.call_tool(
                "combine_fermi",
                {
                    "factors": [
                        {"name": "households", "low": 1.2e8, "high": 1.4e8, "pedigree": "sourced"},
                        {"name": "share", "low": 0.01, "high": 0.5, "pedigree": "invented"},
                    ]
                },
            )


async def test_score_calibration_splits_by_resolver() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "score_calibration",
            {
                "predictions": [
                    {
                        "id": "p-1",
                        "p": 0.8,
                        "resolve_by": "2026-07-01",
                        "outcome": 1,
                        "resolved_by": "self",
                    },
                    {
                        "id": "p-2",
                        "p": 0.9,
                        "resolve_by": "2026-07-02",
                        "outcome": 0,
                        "resolved_by": "ci",
                    },
                ],
                "today": "2026-07-27",
            },
        )
        assert result.data["n_self_resolved"] == 1
        assert {row["resolver"] for row in result.data["by_resolver"]} == {"self", "ci"}


async def test_validation_errors_are_tool_errors() -> None:
    async with Client(mcp) as client:
        with pytest.raises(ToolError, match="exactly one root"):
            await client.call_tool(
                "evaluate_qbaf",
                {"arguments": [{"id": "a", "base_score": 0.5}, {"id": "b", "base_score": 0.5}]},
            )


async def test_analyze_dependencies_end_to_end() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "analyze_dependencies",
            {
                "entries": [
                    {"id": "c-1"},
                    {"id": "c-2", "depends_on": ["c-1"]},
                    {"id": "c-3", "depends_on": ["c-2"]},
                    {"id": "c-4"},
                ],
                "targets": ["c-3"],
            },
        )
        assert result.data["critical"] == [
            {"id": "c-1", "n_affected": 2, "affected": ["c-2", "c-3"]},
            {"id": "c-2", "n_affected": 1, "affected": ["c-3"]},
        ]
        assert result.data["target_dependencies"] == {"c-3": ["c-1", "c-2"]}
        assert "recorded edges only" in result.data["rule"]
