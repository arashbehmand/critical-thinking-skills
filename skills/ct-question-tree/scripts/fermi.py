"""Combine Fermi-estimate factor ranges with interval arithmetic.

Input JSON: {"factors": [{"name": str, "low": float, "high": float,
                          "op": "multiply" | "divide"}, ...]}
The first factor's "op" is ignored. All bounds must be positive and low <= high.

Rules applied (printed so a reader can check by hand):
  multiply: [a, b] * [c, d] = [a*c, b*d]
  divide:   [a, b] / [c, d] = [a/d, b/c]
  point estimate = combination of per-factor geometric means sqrt(low*high)
"""

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


def geomean(low: float, high: float) -> float:
    return math.sqrt(low * high)


def combine(factors: list[dict[str, Any]]) -> dict[str, Any]:
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
    result = combine(factors)

    if args.json:
        print(json.dumps(result, indent=2))
        return
    print(
        "Rule: multiply [a,b]*[c,d]=[ac,bd]; divide [a,b]/[c,d]=[a/d,b/c]; "
        "point = product of geometric means."
    )
    for f, s in zip(factors, result["factor_spans"], strict=True):
        op = f.get("op", "multiply")
        print(
            f"  {op:>8}  {s['name']}: [{fmt(f['low'])}, {fmt(f['high'])}]  "
            f"(span x{s['span_ratio']:.1f})"
        )
    print(
        f"Combined: [{fmt(result['low'])}, {fmt(result['high'])}]  "
        f"point ~ {fmt(result['point'])}  (overall span x{result['span_ratio']:.1f})"
    )
    print(
        f"Widest factor: {result['widest_factor']} — research effort narrows the range "
        "fastest there."
    )


if __name__ == "__main__":
    main()
