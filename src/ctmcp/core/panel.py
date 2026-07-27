"""Mechanical aggregation of independent panel judgments.

numeric: the median is the headline (robust to one wild draw); disagreement is
flagged when range > 0.5 × max(|median|, 1) with n ≥ 3. vote: plurality winner;
flagged on a tie or winner share < 0.6. A flagged panel is a finding, not a
failure — report the split, do not average it away.

Kept in exact behavioral parity with skills/ct-panel/scripts/aggregate.py
(pinned by tests/test_parity.py) — change both together or neither.
"""

import statistics
from collections import Counter
from typing import Any


def numeric(values: list[float]) -> dict[str, Any]:
    """Median/spread statistics with the printed-rule disagreement flag."""
    if len(values) < 2:
        raise ValueError("need at least 2 values for a panel")
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
    }


def vote(values: list[str]) -> dict[str, Any]:
    """Plurality winner with tie / weak-plurality disagreement flag."""
    if len(values) < 2:
        raise ValueError("need at least 2 votes for a panel")
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
    }
