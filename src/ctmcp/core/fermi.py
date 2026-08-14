"""Fermi-estimate factor combination with interval arithmetic.

multiply: [a, b] × [c, d] = [ac, bd];  divide: [a, b] / [c, d] = [a/d, b/c];
point estimate = combination of per-factor geometric means √(low·high).
All bounds must be positive with low ≤ high; the first factor's op is ignored.

Every factor carries a `pedigree` (see core/pedigree.py), because interval
arithmetic over guessed ranges is exact computation over quantities nobody
sourced, and the exactness is what makes the output persuasive.

A factor is **load-bearing** by a mechanical rule, not a judgment call:

  log10(high/low) share of the total at or above the average across factors,
  OR low == high — a point estimate asserts a precision nobody sourced.

An invented load-bearing factor is refused. The measure is *uncertainty
contributed*, not magnitude, because that is where an invented number does its
damage: the census-sized multiplier is the one somebody looked up, while the
guessed share is the one carrying a 3x range. It also lands the gate exactly
where `widest_factor` already tells the reader to go looking.

Kept in exact behavioral parity with skills/ct-question-tree/scripts/fermi.py
(pinned by tests/test_parity.py) — change both together or neither.
"""

import math
from typing import Any

from ctmcp.core import pedigree


def _geomean(low: float, high: float) -> float:
    return math.sqrt(low * high)


def _log_span(low: float, high: float) -> float:
    """Orders of magnitude of uncertainty this factor contributes."""
    return math.log10(high / low)


def combine(factors: list[dict[str, Any]]) -> dict[str, Any]:
    """Combined [low, high], geometric-mean point, spans, widest and load-bearing factors."""
    if not factors:
        raise ValueError("no factors given")

    names: list[str] = []
    bounds: list[tuple[float, float]] = []
    ops: list[str] = []
    tags: list[str] = []
    for i, f in enumerate(factors):
        name, f_low, f_high = str(f["name"]), float(f["low"]), float(f["high"])
        op = str(f.get("op", "multiply")) if i > 0 else "multiply"
        if not (0 < f_low <= f_high):
            raise ValueError(f"factor {name!r}: need 0 < low <= high, got [{f_low}, {f_high}]")
        if op not in ("multiply", "divide"):
            raise ValueError(f"factor {name!r}: op must be 'multiply' or 'divide', got {op!r}")
        names.append(name)
        bounds.append((f_low, f_high))
        ops.append(op)
        tags.append(pedigree.check(f.get("pedigree"), f"factor {name!r}"))

    log_spans = [_log_span(lo, hi) for lo, hi in bounds]
    bar = sum(log_spans) / len(log_spans)
    carries = [span >= bar or lo == hi for span, (lo, hi) in zip(log_spans, bounds, strict=True)]
    load_bearing = [n for n, bears in zip(names, carries, strict=True) if bears]
    for name, span, (lo, hi), tag, bears in zip(
        names, log_spans, bounds, tags, carries, strict=True
    ):
        if tag == "invented" and bears:
            why = (
                "is stated as a point estimate, asserting a precision nobody sourced"
                if lo == hi
                else f"contributes {span:.3g} of the estimate's {sum(log_spans):.3g} orders "
                f"of magnitude of uncertainty, at or above the {bar:.3g} average share, "
                "so it is load-bearing"
            )
            raise pedigree.refuse(f"factor {name!r}", why)

    low, high, point = 1.0, 1.0, 1.0
    spans: list[tuple[str, float]] = []
    for name, (f_low, f_high), op in zip(names, bounds, ops, strict=True):
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
        "load_bearing": load_bearing,
        "pedigree": pedigree.tally(tags),
        "stamp": (
            f"{len(names)} factors, inputs: {pedigree.phrase(tags)}; "
            f"load-bearing: {', '.join(load_bearing)}"
        ),
    }
