"""Pure mathematical aggregator tools for critical-thinking recipes.

Every tool is a pure function of its inputs — hence readOnlyHint and
idempotentHint are True on all of them, deliberately. No tool makes an LLM
call: judgments arrive from the caller's side (the recipes have the host model
elicit them from fresh subagents), and each result echoes the rule it applied
so a reader can check it by hand. Validation errors are ToolErrors ("call
differently"); there is no server state of any kind.
"""

from typing import Any, Literal

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import BaseModel, Field

from ctmcp.core import ach, brier, fermi, panel, qbaf

PURE = {"readOnlyHint": True, "idempotentHint": True}

mcp: FastMCP[None] = FastMCP(
    name="critical-thinking-mcp",
    instructions=(
        "Pure mathematical aggregators for critical-thinking work: they turn judgments "
        "you collected (ideally from fresh subagents that never saw your lean) into "
        "decisions, deterministically. No tool here calls an LLM or keeps state. "
        "Honesty rule: these tools aggregate whatever they are given — when reporting "
        "results, label the inputs (self-assigned vs subagent-elicited)."
    ),
)


class QbafArgument(BaseModel):
    id: str
    base_score: float = Field(ge=0.0, le=1.0, description="τ ∈ [0, 1]")
    parent_id: str | None = Field(default=None, description="omit for the root claim")
    stance: Literal["pro", "con"] | None = Field(
        default=None, description="'pro' supports the parent, 'con' attacks it; root: omit"
    )


class Hypothesis(BaseModel):
    id: str
    text: str


class Evidence(BaseModel):
    id: str
    text: str
    source: str = ""
    credibility: int = Field(ge=1, le=3, description="3 = measured/primary, 1 = hearsay")


class Rating(BaseModel):
    evidence_id: str
    hypothesis_id: str
    rating: Literal["C", "I", "N"]
    why: str = ""


class Prediction(BaseModel):
    id: str
    p: float = Field(ge=0.0, le=1.0)
    resolve_by: str = Field(description="ISO date")
    outcome: Literal[0, 1] | None = Field(default=None, description="null while pending")
    q: str = ""


class Factor(BaseModel):
    name: str
    low: float = Field(gt=0.0)
    high: float = Field(gt=0.0)
    op: Literal["multiply", "divide"] = "multiply"


@mcp.tool(annotations=PURE)
def evaluate_qbaf(arguments: list[QbafArgument]) -> dict[str, Any]:
    """Evaluate a pro/con argument tree under DF-QuAD gradual semantics.

    One root (the claim, no parent/stance); every other argument names its
    parent and whether it supports (pro) or attacks (con) it, with a caller-
    supplied base score τ. Returns σ for every argument and the strict verdict
    σ(root) > 0.5. Aggregates only — the honesty of τ is on the caller.
    """
    try:
        result = qbaf.evaluate(
            [
                qbaf.Argument(
                    id=a.id, base_score=a.base_score, parent_id=a.parent_id, stance=a.stance
                )
                for a in arguments
            ]
        )
    except ValueError as err:
        raise ToolError(str(err)) from err
    result["rule"] = (
        "DF-QuAD: agg(S) = 1 - prod(1 - v), agg(empty) = 0; "
        "sigma = tau -/+ movement by |agg(attackers) - agg(supporters)|; "
        "verdict = sigma(root) > 0.5 (exactly 0.5 is False)"
    )
    return result


@mcp.tool(annotations=PURE)
def score_ach(
    question: str,
    hypotheses: list[Hypothesis],
    evidence: list[Evidence],
    ratings: list[Rating],
) -> dict[str, Any]:
    """Rank competing hypotheses by least weighted inconsistency (Heuer's ACH).

    Every (evidence x hypothesis) pair must be rated exactly once with C
    (consistent), I (inconsistent), or N (neutral). Reports the ranking, ties,
    non-diagnostic evidence (rated the same everywhere — decoration), and the
    single cells whose change would swap ranks 1 and 2.
    """
    matrix = {
        "question": question,
        "hypotheses": [h.model_dump() for h in hypotheses],
        "evidence": [e.model_dump() for e in evidence],
        "ratings": [r.model_dump() for r in ratings],
    }
    try:
        result = ach.score(matrix)
    except ValueError as err:
        raise ToolError(str(err)) from err
    result["rule"] = (
        "inconsistency(H) = sum of evidence credibility over I-cells; "
        "survivor = lowest (least contradicted, not most supported)"
    )
    return result


@mcp.tool(annotations=PURE)
def aggregate_numeric(values: list[float]) -> dict[str, Any]:
    """Aggregate independent numeric judgments: median, spread, disagreement flag.

    Report downstream as "panel of n, median X, range [a, b]" — never a bare X.
    A flagged panel means underspecified or genuinely contested; do not average
    a split away.
    """
    try:
        result = panel.numeric(values)
    except ValueError as err:
        raise ToolError(str(err)) from err
    result["rule"] = "median is the headline; flag if range > 0.5 x max(|median|, 1) with n >= 3"
    return result


@mcp.tool(annotations=PURE)
def aggregate_vote(votes: list[str]) -> dict[str, Any]:
    """Aggregate independent categorical picks: plurality, share, tie/weak flag."""
    try:
        result = panel.vote(votes)
    except ValueError as err:
        raise ToolError(str(err)) from err
    result["rule"] = "plurality wins; flag on tie or winner share < 0.6 (a 3-2 split IS the answer)"
    return result


@mcp.tool(annotations=PURE)
def score_calibration(predictions: list[Prediction], today: str) -> dict[str, Any]:
    """Brier score and calibration bins for logged probability predictions.

    Pass `today` (ISO date) explicitly — the tool is pure and stateless.
    Resolved entries (outcome 0/1) are scored; pending ones past resolve_by are
    surfaced as overdue. Results are only as honest as the ledger they came
    from — label self-graded ledgers as such.
    """
    try:
        result = brier.report([p.model_dump() for p in predictions], today)
    except ValueError as err:
        raise ToolError(str(err)) from err
    result["rule"] = "Brier = mean((p - outcome)^2); bins compare stated p to hit rate"
    return result


@mcp.tool(annotations=PURE)
def combine_fermi(factors: list[Factor]) -> dict[str, Any]:
    """Combine Fermi-estimate factor ranges with interval arithmetic.

    Report the range, not just the point; the widest factor is where research
    effort narrows the estimate fastest.
    """
    try:
        result = fermi.combine([f.model_dump() for f in factors])
    except ValueError as err:
        raise ToolError(str(err)) from err
    result["rule"] = (
        "multiply [a,b]*[c,d]=[ac,bd]; divide [a,b]/[c,d]=[a/d,b/c]; "
        "point = product of geometric means"
    )
    return result


def main() -> None:
    """Console entry point (stdio transport)."""
    mcp.run()
