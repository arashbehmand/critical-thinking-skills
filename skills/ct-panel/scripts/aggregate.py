"""Aggregate independent panel judgments mechanically.

numeric mode: median is the headline (robust to one wild draw); disagreement is flagged
when range > 0.5 x max(|median|, 1) with n >= 3 — the threshold is printed, not hidden.
vote mode: plurality winner; flagged when the winner's share < 0.6 or there is a tie.

A flagged panel is a finding, not a failure: the question is underspecified or genuinely
contested. Report the split; do not average it away.
"""

import argparse
import json
import statistics
import sys
from collections import Counter


def numeric(values: list[float], as_json: bool) -> None:
    if len(values) < 2:
        sys.exit("need at least 2 values for a panel")
    med = statistics.median(values)
    spread = max(values) - min(values)
    threshold = 0.5 * max(abs(med), 1.0)
    flagged = len(values) >= 3 and spread > threshold
    result = {
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
    if as_json:
        print(json.dumps(result, indent=2))
        return
    print(f"n={result['n']}  values={result['values_sorted']}")
    print(
        f"median={med:g}  mean={result['mean']:.3g}  stdev={result['stdev']:.3g}  "
        f"range=[{result['min']:g}, {result['max']:g}]"
    )
    print(f"Rule: flag if range ({spread:g}) > 0.5 x max(|median|, 1) = {threshold:g}, n>=3.")
    if flagged:
        print(
            "HIGH DISAGREEMENT — underspecified question or genuine contest. "
            "Report the spread; consider ct-definition-pin, then rerun the whole panel."
        )
    else:
        print(
            f"Report as: panel of {result['n']}, median {med:g}, "
            f"range [{result['min']:g}, {result['max']:g}]"
        )


def vote(values: list[str], as_json: bool) -> None:
    if len(values) < 2:
        sys.exit("need at least 2 votes for a panel")
    counts = Counter(values)
    ranked = counts.most_common()
    winner, top = ranked[0]
    tie = len(ranked) > 1 and ranked[1][1] == top
    share = top / len(values)
    flagged = tie or share < 0.6
    result = {
        "n": len(values),
        "counts": dict(counts),
        "winner": None if tie else winner,
        "share": round(share, 3),
        "tie": tie,
        "disagreement": flagged,
    }
    if as_json:
        print(json.dumps(result, indent=2))
        return
    print(f"n={result['n']}  counts={result['counts']}")
    print("Rule: flag on tie or winner share < 0.6.")
    if tie:
        print("TIE — the panel does not decide. The split is the answer; report it.")
    elif flagged:
        print(f"WEAK PLURALITY — {winner} at {share:.0%}. Report the split, not just the winner.")
    else:
        print(f"Winner: {winner} ({share:.0%} of {result['n']})")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("numeric", "vote"), default="numeric")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("values", nargs="*", help="panel answers (or one per stdin line)")
    args = parser.parse_args()

    raw = args.values or [line.strip() for line in sys.stdin if line.strip()]
    if args.mode == "numeric":
        try:
            numeric([float(v) for v in raw], args.json)
        except ValueError as err:
            sys.exit(f"non-numeric value in numeric mode: {err}")
    else:
        vote(raw, args.json)


if __name__ == "__main__":
    main()
