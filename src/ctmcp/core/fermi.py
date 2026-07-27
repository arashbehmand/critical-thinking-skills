"""Fermi-estimate factor combination with interval arithmetic.

multiply: [a, b] × [c, d] = [ac, bd];  divide: [a, b] / [c, d] = [a/d, b/c];
point estimate = combination of per-factor geometric means √(low·high).
All bounds must be positive with low ≤ high; the first factor's op is ignored.

Kept in exact behavioral parity with skills/ct-question-tree/scripts/fermi.py
(pinned by tests/test_parity.py) — change both together or neither.
"""

import math
from typing import Any


def _geomean(low: float, high: float) -> float:
    return math.sqrt(low * high)


def combine(factors: list[dict[str, Any]]) -> dict[str, Any]:
    """Combined [low, high], geometric-mean point, per-factor spans, widest factor."""
    if not factors:
        raise ValueError("no factors given")
    low, high, point = 1.0, 1.0, 1.0
    spans: list[tuple[str, float]] = []
    for i, f in enumerate(factors):
        name, f_low, f_high = str(f["name"]), float(f["low"]), float(f["high"])
        op = str(f.get("op", "multiply")) if i > 0 else "multiply"
        if not (0 < f_low <= f_high):
            raise ValueError(f"factor {name!r}: need 0 < low <= high, got [{f_low}, {f_high}]")
        if op not in ("multiply", "divide"):
            raise ValueError(f"factor {name!r}: op must be 'multiply' or 'divide', got {op!r}")
        if op == "multiply":
            low, high, point = low * f_low, high * f_high, point * _geomean(f_low, f_high)
        else:
            low, high, point = low / f_high, high / f_low, point / _geomean(f_low, f_high)
        spans.append((name, f_high / f_low))
    widest = max(spans, key=lambda s: s[1])
    return {
        "low": low,
        "point": point,
        "high": high,
        "span_ratio": high / low,
        "factor_spans": [{"name": n, "span_ratio": r} for n, r in spans],
        "widest_factor": widest[0],
    }
