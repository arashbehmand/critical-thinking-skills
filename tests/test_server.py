"""The thin shell: tools wired to core, pure annotations set, validation → ToolError."""

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
}


async def test_all_tools_registered_and_pure() -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()
        assert {t.name for t in tools} == EXPECTED_TOOLS
        for tool in tools:
            assert tool.annotations is not None, tool.name
            assert tool.annotations.readOnlyHint is True, tool.name
            assert tool.annotations.idempotentHint is True, tool.name


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


async def test_validation_errors_are_tool_errors() -> None:
    async with Client(mcp) as client:
        with pytest.raises(ToolError, match="exactly one root"):
            await client.call_tool(
                "evaluate_qbaf",
                {"arguments": [{"id": "a", "base_score": 0.5}, {"id": "b", "base_score": 0.5}]},
            )
