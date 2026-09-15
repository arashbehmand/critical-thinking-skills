"""Pure mathematical aggregator tools for critical-thinking recipes.

Every tool is a pure function of its inputs — hence readOnlyHint and
idempotentHint are True on all of them, deliberately. No tool makes an LLM
call: judgments arrive from the caller's side (the recipes have the host model
elicit them from fresh subagents), and each result echoes the rule it applied
so a reader can check it by hand. Validation errors are ToolErrors ("call
differently"); there is no server state of any kind.
"""

from pathlib import Path
from typing import Any, Literal

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.providers.skills import SkillsDirectoryProvider
from pydantic import BaseModel, Field

from ctmcp.core import ach, brier, dependencies, fermi, panel, qbaf

PURE = {"readOnlyHint": True, "idempotentHint": True}
SKILLS_DIRECTORY = Path(__file__).resolve().parents[3] / "skills"

mcp: FastMCP[None] = FastMCP(
    name="critical-thinking-mcp",
    instructions=(
        "Critical-thinking recipes plus pure deterministic aggregators. Read "
        "skill://critical-thinking/SKILL.md first: it silently routes the user's problem "
        "to the minimum useful act, including NO_SCAFFOLD, so do not ask the user to "
        "choose a technique. Then read only the selected skill and its supporting files. "
        "The tools are deterministic backends: recipes supply method, prompts, and "
        "receipts; judgments stay host-side, ideally in fresh contexts. No tool calls an "
        "LLM or keeps state. "
        "Honesty rule: these tools aggregate whatever they are given — when reporting "
        "results, separate external evidence, independent computation, and model-only "
        "structure or elicitation."
    ),
)
mcp.add_provider(SkillsDirectoryProvider(roots=SKILLS_DIRECTORY))


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
    origin: str = Field(
        default="",
        description=(
            "the observation this traces back to; items sharing an origin are one "
            "observation and are counted once. Omit when the item stands alone."
        ),
    )


class Rating(BaseModel):
    evidence_id: str
    hypothesis_id: str
    rating: Literal["C", "I", "N"]
    why: str = ""


Pedigree = Literal["given", "sourced", "elicited", "invented"]
PEDIGREE_DOC = (
    "where this number came from: 'given' (handed to you), 'sourced' (named external "
    "source), 'elicited' (fresh subagent that never saw your lean), 'invented' (you "
    "made it up). Required — 'invented' is an honest answer, and is refused only "
    "where it would move the headline."
)


class Draw(BaseModel):
    value: float
    source: str = Field(description="who supplied it: the model family, or 'human'")
    pedigree: Pedigree = Field(description=PEDIGREE_DOC)


class Vote(BaseModel):
    choice: str
    source: str = Field(description="who supplied it: the model family, or 'human'")


class Prediction(BaseModel):
    id: str
    p: float = Field(ge=0.0, le=1.0)
    resolve_by: str = Field(description="ISO date")
    outcome: Literal[0, 1] | None = Field(default=None, description="null while pending")
    q: str = ""
    resolved_by: str = Field(
        default="",
        description="who recorded the outcome: self | ci | tracker | human | <name>",
    )


class Factor(BaseModel):
    name: str
    low: float = Field(gt=0.0)
    high: float = Field(gt=0.0)
    op: Literal["multiply", "divide"] = "multiply"
    pedigree: Pedigree = Field(description=PEDIGREE_DOC)


class DependencyEntry(BaseModel):
    id: str
    depends_on: list[str] = Field(default_factory=list)
    supersedes: str | None = None


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
    (consistent), I (inconsistent), or N (neutral). Evidence items sharing an
    `origin` are one observation: the cluster contributes its best-evidenced
    I-rated member's credibility once, so four restatements of one source cannot
    outvote a single measurement. Reports the ranking, ties, collapsed origins,
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
        "inconsistency(H) = sum of evidence credibility over I-cells, counted once "
        "per origin (a cluster contributes its best-evidenced I-rated member); "
        "survivor = lowest (least contradicted, not most supported)"
    )
    return result


@mcp.tool(annotations=PURE)
def aggregate_numeric(draws: list[Draw]) -> dict[str, Any]:
    """Aggregate independent numeric judgments: median, spread, disagreement flag.

    Each draw names its `source` and its `pedigree`. Report downstream as "panel
    of n, median X, range [a, b]" — never a bare X — and carry the returned
    `stamp`, because five draws from one model are not five independent sources.
    A flagged panel means underspecified or genuinely contested; do not average
    a split away. Refuses when an invented draw sits at the median position.
    """
    try:
        result = panel.numeric([d.model_dump() for d in draws])
    except ValueError as err:
        raise ToolError(str(err)) from err
    result["rule"] = (
        "median is the headline; flag if range > 0.5 x max(|median|, 1) with n >= 3; "
        "load-bearing = the draw(s) at the median position — an invented draw there "
        "is refused, an invented draw elsewhere is computed and stamped"
    )
    return result


@mcp.tool(annotations=PURE)
def aggregate_vote(draws: list[Vote]) -> dict[str, Any]:
    """Aggregate independent categorical picks: plurality, share, tie/weak flag.

    Each draw names its `source`. No pedigree gate here — a plurality count is
    not exact arithmetic over a continuous quantity.
    """
    try:
        result = panel.vote([d.model_dump() for d in draws])
    except ValueError as err:
        raise ToolError(str(err)) from err
    result["rule"] = "plurality wins; flag on tie or winner share < 0.6 (a 3-2 split IS the answer)"
    return result


@mcp.tool(annotations=PURE)
def score_calibration(predictions: list[Prediction], today: str) -> dict[str, Any]:
    """Brier score and calibration bins for logged probability predictions.

    Pass `today` (ISO date) explicitly — the tool is pure and stateless.
    Resolved entries (outcome 0/1) are scored; pending ones past resolve_by are
    surfaced as overdue. Scores are broken out by `resolved_by`, so a ledger the
    predictor graded themselves reports that on its own face rather than as a
    bare number.
    """
    try:
        result = brier.report([p.model_dump() for p in predictions], today)
    except ValueError as err:
        raise ToolError(str(err)) from err
    result["rule"] = (
        "Brier = mean((p - outcome)^2); bins compare stated p to hit rate; "
        "by_resolver splits the score by who recorded each outcome "
        "(resolutions predating the field are reported as 'unrecorded')"
    )
    return result


@mcp.tool(annotations=PURE)
def combine_fermi(factors: list[Factor]) -> dict[str, Any]:
    """Combine Fermi-estimate factor ranges with interval arithmetic.

    Every factor names its `pedigree`. Report the range, not just the point; the
    widest factor is where research effort narrows the estimate fastest. Refuses
    when an invented factor is load-bearing — interval arithmetic over guessed
    ranges is exact computation over quantities nobody sourced, and the
    exactness is what makes the answer persuasive.
    """
    try:
        result = fermi.combine([f.model_dump() for f in factors])
    except ValueError as err:
        raise ToolError(str(err)) from err
    result["rule"] = (
        "multiply [a,b]*[c,d]=[ac,bd]; divide [a,b]/[c,d]=[a/d,b/c]; "
        "point = product of geometric means; load-bearing = |log10(geometric mean)| "
        "at or above the average across factors — an invented one there is refused"
    )
    return result


@mcp.tool(annotations=PURE)
def analyze_dependencies(
    entries: list[DependencyEntry], targets: list[str] | None = None
) -> dict[str, Any]:
    """Rank recorded commitments by the impact of withdrawing each one.

    Status follows append-only truth maintenance: superseded entries are not
    live, and every entry depending directly or transitively on a non-live
    premise is OUT. For each ACTIVE entry, simulate its withdrawal and report
    which other live entries fall. Optional `targets` names active conclusions
    whose recorded load-bearing dependencies should be listed.

    Exact about the supplied dependency graph, not about the underlying
    reasoning: missing or imagined edges remain the caller's responsibility.
    """
    try:
        result = dependencies.analyze(
            [entry.model_dump() for entry in entries], targets=targets or []
        )
    except ValueError as err:
        raise ToolError(str(err)) from err
    result["rule"] = (
        "truth maintenance (Doyle 1979): superseded or withdrawn premises are non-live; "
        "OUT propagates transitively; withdrawal impact counts ACTIVE dependents newly "
        "made OUT. Exact about recorded edges only — not a certificate of completeness."
    )
    return result


def main() -> None:
    """Console entry point (stdio transport)."""
    mcp.run()
