"""Minimal QBAF evaluation with DF-QuAD gradual semantics.

Clean-room from the formulas in Rago, Toni, Aurisicchio & Baroni (2016),
"Discontinuity-Free Decision Support with Quantitative Argumentation Debates"
(KR 2016), as used for claim verification by Freedman et al. (2024),
arXiv:2405.02079. Aggregation of the empty set is 0. The decision rule is
strict: σ(root) > 0.5 → True; exactly 0.5 → False.

The framework is a tree: each non-root argument names its parent and a stance
toward it — "pro" (support) or "con" (attack). Base scores τ ∈ [0, 1] are
supplied by the caller: this module aggregates, it does not elicit. Label the
sourcing of τ when reporting results (see AGENTS.md).
"""

from dataclasses import dataclass
from typing import Any

DECISION_THRESHOLD = 0.5
STANCES = ("pro", "con")


@dataclass(frozen=True)
class Argument:
    id: str
    base_score: float
    parent_id: str | None = None  # None → root
    stance: str | None = None  # "pro" | "con"; required iff non-root


def _agg(strengths: list[float]) -> float:
    """Product aggregation: agg(S) = 1 − Π(1 − v); agg(∅) = 0."""
    remainder = 1.0
    for v in strengths:
        remainder *= 1.0 - v
    return 1.0 - remainder


def _combine(tau: float, s_att: float, s_supp: float) -> float:
    """DF-QuAD influence: move τ toward 0 (net attack) or 1 (net support) by the gap."""
    if s_att >= s_supp:
        return tau - tau * (s_att - s_supp)
    return tau + (1.0 - tau) * (s_supp - s_att)


def _validate(arguments: list[Argument]) -> Argument:
    """Well-formedness: unique ids, one root, stances, τ range, tree connectivity."""
    if not arguments:
        raise ValueError("empty framework: at least a root argument is required")
    ids = [a.id for a in arguments]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate argument ids")
    by_id = {a.id: a for a in arguments}
    roots = [a for a in arguments if a.parent_id is None]
    if len(roots) != 1:
        raise ValueError(f"exactly one root required (parent_id=None), found {len(roots)}")
    root = roots[0]
    if root.stance is not None:
        raise ValueError("the root has no stance")
    for a in arguments:
        if not 0.0 <= a.base_score <= 1.0:
            raise ValueError(f"{a.id}: base_score must be in [0, 1], got {a.base_score}")
        if a.parent_id is not None:
            if a.parent_id not in by_id:
                raise ValueError(f"{a.id}: unknown parent {a.parent_id!r}")
            if a.stance not in STANCES:
                raise ValueError(f"{a.id}: stance must be 'pro' or 'con', got {a.stance!r}")
    reachable = {root.id}
    frontier = [root.id]
    children: dict[str, list[Argument]] = {a.id: [] for a in arguments}
    for a in arguments:
        if a.parent_id is not None:
            children[a.parent_id].append(a)
    while frontier:
        node = frontier.pop()
        for child in children[node]:
            reachable.add(child.id)
            frontier.append(child.id)
    orphans = set(ids) - reachable
    if orphans:
        raise ValueError(f"arguments not connected to the root: {sorted(orphans)}")
    return root


def evaluate(arguments: list[Argument]) -> dict[str, Any]:
    """Strengths for every argument and the strict verdict for the root.

    σ is a pure function of (tree, base scores) computed bottom-up; nothing is
    cached or stored between calls.
    """
    root = _validate(arguments)
    children: dict[str, list[Argument]] = {a.id: [] for a in arguments}
    for a in arguments:
        if a.parent_id is not None:
            children[a.parent_id].append(a)

    strengths: dict[str, float] = {}

    def sigma(arg: Argument) -> float:
        attackers = [sigma(c) for c in children[arg.id] if c.stance == "con"]
        supporters = [sigma(c) for c in children[arg.id] if c.stance == "pro"]
        strength = _combine(arg.base_score, _agg(attackers), _agg(supporters))
        strengths[arg.id] = strength
        return strength

    root_strength = sigma(root)
    return {
        "strengths": strengths,
        "root_id": root.id,
        "root_strength": root_strength,
        "verdict": root_strength > DECISION_THRESHOLD,
    }
