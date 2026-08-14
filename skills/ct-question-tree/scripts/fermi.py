"""Combine Fermi-estimate factor ranges with interval arithmetic.

Input JSON: {"factors": [{"name": str, "low": float, "high": float,
                          "op": "multiply" | "divide",
                          "pedigree": "given"|"sourced"|"elicited"|"invented"}, ...]}
The first factor's "op" is ignored. All bounds must be positive and low <= high.

Every factor names its pedigree, because interval arithmetic over guessed ranges is
exact computation over quantities nobody sourced, and the exactness is what makes the
output persuasive. An invented LOAD-BEARING factor is refused rather than computed and
disclaimed. The measure is uncertainty contributed, not magnitude, because that is where
an invented number does its damage: the census-sized multiplier is the one somebody
looked up, while the guessed share is the one carrying a 3x range.

Rules applied (printed so a reader can check by hand):
  multiply: [a, b] * [c, d] = [a*c, b*d]
  divide:   [a, b] / [c, d] = [a/d, b/c]
  point estimate = combination of per-factor geometric means sqrt(low*high)
  load-bearing = log10(high/low) share at or above the average across factors,
                 OR low == high (a point estimate asserts unsourced precision)

Kept in exact behavioral parity with src/ctmcp/core/fermi.py (pinned by
tests/test_parity.py) — change both together or neither.
"""

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

PEDIGREES = ("given", "sourced", "elicited", "invented")


def check_pedigree(value: object, where: str) -> str:
    tag = "" if value is None else str(value).strip()
    if not tag:
        raise ValueError(
            f"{where}: pedigree is required — one of {', '.join(PEDIGREES)}. "
            "Say where the number came from; 'invented' is an honest answer."
        )
    if tag not in PEDIGREES:
        raise ValueError(f"{where}: pedigree must be one of {', '.join(PEDIGREES)}, got {tag!r}")
    return tag


def refusal(what: str, why: str) -> ValueError:
    return ValueError(
        f"{what} is invented and {why} — refusing to compute. Supply it elicited "
        "(a fresh subagent that never saw your lean), sourced (a named external "
        "source), or given (handed to you) — or drop the estimate and report which "
        "quantity is missing. Computing it and disclaiming it is the failure mode "
        "this gate exists to stop."
    )


def tally(tags: list[str]) -> dict[str, int]:
    return {p: tags.count(p) for p in PEDIGREES if p in tags}


def phrase(tags: list[str]) -> str:
    return ", ".join(f"{count} {tag}" for tag, count in tally(tags).items())


def geomean(low: float, high: float) -> float:
    return math.sqrt(low * high)


def log_span(low: float, high: float) -> float:
    """Orders of magnitude of uncertainty this factor contributes."""
    return math.log10(high / low)


def combine(factors: list[dict[str, Any]]) -> dict[str, Any]:
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
        tags.append(check_pedigree(f.get("pedigree"), f"factor {name!r}"))

    log_spans = [log_span(lo, hi) for lo, hi in bounds]
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
            raise refusal(f"factor {name!r}", why)

    low, high, point = 1.0, 1.0, 1.0
    spans: list[tuple[str, float]] = []
    for name, (f_low, f_high), op in zip(names, bounds, ops, strict=True):
        if op == "multiply":
            low, high, point = low * f_low, high * f_high, point * geomean(f_low, f_high)
        else:
            low, high, point = low / f_high, high / f_low, point / geomean(f_low, f_high)
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
        "pedigree": tally(tags),
        "stamp": (
            f"{len(names)} factors, inputs: {phrase(tags)}; load-bearing: {', '.join(load_bearing)}"
        ),
    }


def fmt(x: float) -> str:
    return f"{x:,.4g}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", nargs="?", help="JSON file (default: read stdin)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    raw = Path(args.file).read_text() if args.file else sys.stdin.read()
    factors = json.loads(raw)["factors"]
    if not factors:
        sys.exit("no factors given")
    try:
        result = combine(factors)
    except ValueError as err:
        sys.exit(str(err))

    if args.json:
        print(json.dumps(result, indent=2))
        return
    print(
        "Rule: multiply [a,b]*[c,d]=[ac,bd]; divide [a,b]/[c,d]=[a/d,b/c]; "
        "point = product of geometric means."
    )
    for f, s in zip(factors, result["factor_spans"], strict=True):
        op = f.get("op", "multiply")
        bearing = " LOAD-BEARING" if s["name"] in result["load_bearing"] else ""
        print(
            f"  {op:>8}  {s['name']}: [{fmt(f['low'])}, {fmt(f['high'])}]  "
            f"(span x{s['span_ratio']:.1f}, {f['pedigree']}){bearing}"
        )
    print(
        f"Combined: [{fmt(result['low'])}, {fmt(result['high'])}]  "
        f"point ~ {fmt(result['point'])}  (overall span x{result['span_ratio']:.1f})"
    )
    print(f"Inputs: {result['stamp']}")
    print(
        f"Widest factor: {result['widest_factor']} — research effort narrows the range "
        "fastest there."
    )


if __name__ == "__main__":
    main()
