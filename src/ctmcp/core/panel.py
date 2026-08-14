"""Mechanical aggregation of independent panel judgments.

numeric: the median is the headline (robust to one wild draw); disagreement is
flagged when range > 0.5 × max(|median|, 1) with n ≥ 3. vote: plurality winner;
flagged on a tie or winner share < 0.6. A flagged panel is a finding, not a
failure — report the split, do not average it away.

Every draw names its `source` (model family, or `human`). Five draws from one
model and three models plus a human must not print identically: a panel of one
model cancels *noise*, not shared bias, and a median of five answers wrong in
the same direction is still wrong. Composition is reported beside the median so
a reader can tell which panel they are looking at.

Numeric draws also carry a `pedigree` (see core/pedigree.py). The median is the
headline, so the load-bearing draws are mechanically the ones **at the median
position** — an invented draw there refuses; an invented outlier the median
already shrugs off computes, and the stamp says so. That asymmetry is the point:
the median is exactly the instrument that neutralises a wild draw, so refusing
there too would be theatre. `vote` takes no pedigree — a plurality count is not
exact arithmetic over a continuous quantity, which is where the gate belongs.

Kept in exact behavioral parity with skills/ct-panel/scripts/aggregate.py
(pinned by tests/test_parity.py) — change both together or neither.
"""

import statistics
from collections import Counter
from typing import Any

from ctmcp.core import pedigree


def _composition(draws: list[dict[str, Any]]) -> dict[str, int]:
    """Draws per source, in first-seen order. A nameless source is refused."""
    counts: dict[str, int] = {}
    for i, draw in enumerate(draws, 1):
        source = str(draw.get("source") or "").strip()
        if not source:
            raise ValueError(
                f"draw {i}: source is required — the model family, or 'human'. "
                "A panel that hides its composition reads as independent evidence."
            )
        counts[source] = counts.get(source, 0) + 1
    return counts


def _median_positions(values: list[float]) -> list[int]:
    """Indices, into the given order, of the draws that determine the median."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    n = len(values)
    return [order[n // 2]] if n % 2 else [order[n // 2 - 1], order[n // 2]]


def _stamp(composition: dict[str, int], tags: list[str], invented_off_median: int) -> str:
    """One line naming what this panel actually is, for the report to carry."""
    who = ", ".join(f"{src}x{count}" if count > 1 else src for src, count in composition.items())
    bias = (
        "cancels noise, not shared bias"
        if len(composition) == 1
        else f"{len(composition)} independent sources"
    )
    stamp = f"panel of {len(tags)} from {who} — {bias}"
    if tags:
        stamp += f"; inputs: {pedigree.phrase(tags)}"
    if invented_off_median:
        plural = "s" if invented_off_median > 1 else ""
        stamp += (
            f"; {invented_off_median} invented draw{plural} away from the median — "
            "no effect on the headline, but inside the reported range"
        )
    return stamp


def numeric(draws: list[dict[str, Any]]) -> dict[str, Any]:
    """Median/spread statistics, panel composition, and the pedigree gate.

    Each draw is {value, source, pedigree}. Refuses when an invented draw sits
    at the median position, which is the only place it could move the headline.
    """
    if len(draws) < 2:
        raise ValueError("need at least 2 values for a panel")
    composition = _composition(draws)
    values = [float(draw["value"]) for draw in draws]
    tags = [pedigree.check(draw.get("pedigree"), f"draw {i}") for i, draw in enumerate(draws, 1)]

    at_median = _median_positions(values)
    for i in at_median:
        if tags[i] == "invented":
            raise pedigree.refuse(
                f"panel draw {i + 1} (value {values[i]:g}, source {draws[i]['source']!r})",
                "sits at the median position, which is the reported headline",
            )
    invented_off_median = sum(
        1 for i, tag in enumerate(tags) if tag == "invented" and i not in at_median
    )

    med = statistics.median(values)
    spread = max(values) - min(values)
    threshold = 0.5 * max(abs(med), 1.0)
    flagged = len(values) >= 3 and spread > threshold
    return {
        "n": len(values),
        "values_sorted": sorted(values),
        "median": med,
        "mean": statistics.fmean(values),
        "stdev": statistics.stdev(values),
        "min": min(values),
        "max": max(values),
        "range": spread,
        "disagreement": flagged,
        "composition": composition,
        "distinct_sources": len(composition),
        "shared_source": len(composition) == 1,
        "pedigree": pedigree.tally(tags),
        "stamp": _stamp(composition, tags, invented_off_median),
    }


def vote(draws: list[dict[str, Any]]) -> dict[str, Any]:
    """Plurality winner, tie / weak-plurality flag, and who voted.

    Each draw is {choice, source}. No pedigree gate — a plurality count is not
    exact arithmetic over a continuous quantity.
    """
    if len(draws) < 2:
        raise ValueError("need at least 2 votes for a panel")
    composition = _composition(draws)
    values = [str(draw["choice"]) for draw in draws]
    counts = Counter(values)
    ranked = counts.most_common()
    winner, top = ranked[0]
    tie = len(ranked) > 1 and ranked[1][1] == top
    share = top / len(values)
    flagged = tie or share < 0.6
    return {
        "n": len(values),
        "counts": dict(counts),
        "winner": None if tie else winner,
        "share": round(share, 3),
        "tie": tie,
        "disagreement": flagged,
        "composition": composition,
        "distinct_sources": len(composition),
        "shared_source": len(composition) == 1,
        "stamp": _stamp(composition, [], 0),
    }
