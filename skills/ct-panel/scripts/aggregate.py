"""Aggregate independent panel judgments mechanically.

numeric mode: median is the headline (robust to one wild draw); disagreement is flagged
when range > 0.5 x max(|median|, 1) with n >= 3 — the threshold is printed, not hidden.
vote mode: plurality winner; flagged when the winner's share < 0.6 or there is a tie.

Every draw names its --source (the model family, or 'human'), because five draws from one
model and three models plus a human must not print identically: a panel of one model
cancels noise, not shared bias, and a median of five answers wrong in the same direction
is still wrong.

Numeric draws also name a --pedigree (given | sourced | elicited | invented). The median
is the headline, so the load-bearing draws are mechanically the ones AT the median
position: an invented draw there is refused, while an invented outlier the median
already shrugs off is computed and stamped. Refusing there too would be theatre — the
median is exactly the instrument that neutralises a wild draw. vote mode takes no
pedigree: a plurality count is not exact arithmetic over a continuous quantity.

A flagged panel is a finding, not a failure: the question is underspecified or genuinely
contested. Report the split; do not average it away.

Kept in exact behavioral parity with src/ctmcp/core/panel.py (pinned by
tests/test_parity.py) — change both together or neither.
"""

import argparse
import json
import statistics
import sys
from collections import Counter
from typing import Any

PEDIGREES = ("given", "sourced", "elicited", "invented")


def check_pedigree(value: str, where: str) -> str:
    tag = (value or "").strip()
    if not tag:
        sys.exit(
            f"{where}: pedigree is required — one of {', '.join(PEDIGREES)}. "
            "Say where the number came from; 'invented' is an honest answer."
        )
    if tag not in PEDIGREES:
        sys.exit(f"{where}: pedigree must be one of {', '.join(PEDIGREES)}, got {tag!r}")
    return tag


def refuse(what: str, why: str) -> None:
    sys.exit(
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


def composition(sources: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for i, raw in enumerate(sources, 1):
        source = (raw or "").strip()
        if not source:
            sys.exit(
                f"draw {i}: source is required — the model family, or 'human'. "
                "A panel that hides its composition reads as independent evidence."
            )
        counts[source] = counts.get(source, 0) + 1
    return counts


def median_positions(values: list[float]) -> list[int]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    n = len(values)
    return [order[n // 2]] if n % 2 else [order[n // 2 - 1], order[n // 2]]


def stamp(comp: dict[str, int], tags: list[str], invented_off_median: int) -> str:
    who = ", ".join(f"{src}x{count}" if count > 1 else src for src, count in comp.items())
    bias = (
        "cancels noise, not shared bias" if len(comp) == 1 else f"{len(comp)} independent sources"
    )
    text = f"panel of {len(tags)} from {who} — {bias}"
    if tags:
        text += f"; inputs: {phrase(tags)}"
    if invented_off_median:
        plural = "s" if invented_off_median > 1 else ""
        text += (
            f"; {invented_off_median} invented draw{plural} away from the median — "
            "no effect on the headline, but inside the reported range"
        )
    return text


def numeric(values: list[float], sources: list[str], pedigrees: list[str]) -> dict[str, Any]:
    if len(values) < 2:
        sys.exit("need at least 2 values for a panel")
    comp = composition(sources)
    tags = [check_pedigree(p, f"draw {i}") for i, p in enumerate(pedigrees, 1)]

    at_median = median_positions(values)
    for i in at_median:
        if tags[i] == "invented":
            refuse(
                f"panel draw {i + 1} (value {values[i]:g}, source {sources[i]!r})",
                "sits at the median position, which is the reported headline",
            )
    invented_off_median = sum(
        1 for i, tag in enumerate(tags) if tag == "invented" and i not in at_median
    )

    med = statistics.median(values)
    spread = max(values) - min(values)
    threshold = 0.5 * max(abs(med), 1.0)
    return {
        "n": len(values),
        "values_sorted": sorted(values),
        "median": med,
        "mean": statistics.fmean(values),
        "stdev": statistics.stdev(values),
        "min": min(values),
        "max": max(values),
        "range": spread,
        "disagreement": len(values) >= 3 and spread > threshold,
        "composition": comp,
        "distinct_sources": len(comp),
        "shared_source": len(comp) == 1,
        "pedigree": tally(tags),
        "stamp": stamp(comp, tags, invented_off_median),
    }


def vote(values: list[str], sources: list[str]) -> dict[str, Any]:
    if len(values) < 2:
        sys.exit("need at least 2 votes for a panel")
    comp = composition(sources)
    counts = Counter(values)
    ranked = counts.most_common()
    winner, top = ranked[0]
    tie = len(ranked) > 1 and ranked[1][1] == top
    share = top / len(values)
    return {
        "n": len(values),
        "counts": dict(counts),
        "winner": None if tie else winner,
        "share": round(share, 3),
        "tie": tie,
        "disagreement": tie or share < 0.6,
        "composition": comp,
        "distinct_sources": len(comp),
        "shared_source": len(comp) == 1,
        "stamp": stamp(comp, [], 0),
    }


def print_numeric(r: dict[str, Any]) -> None:
    print(f"n={r['n']}  values={r['values_sorted']}")
    print(
        f"median={r['median']:g}  mean={r['mean']:.3g}  stdev={r['stdev']:.3g}  "
        f"range=[{r['min']:g}, {r['max']:g}]"
    )
    threshold = 0.5 * max(abs(r["median"]), 1.0)
    print(f"Rule: flag if range ({r['range']:g}) > 0.5 x max(|median|, 1) = {threshold:g}, n>=3.")
    print(f"Panel: {r['stamp']}")
    if r["shared_source"]:
        print("  One source: this cancels noise only. Shared blind spots survive a median.")
    if r["disagreement"]:
        print(
            "HIGH DISAGREEMENT — underspecified question or genuine contest. "
            "Report the spread; consider ct-definition-pin, then rerun the whole panel."
        )
    else:
        print(
            f"Report as: panel of {r['n']}, median {r['median']:g}, "
            f"range [{r['min']:g}, {r['max']:g}]"
        )


def print_vote(r: dict[str, Any]) -> None:
    print(f"n={r['n']}  counts={r['counts']}")
    print("Rule: flag on tie or winner share < 0.6.")
    print(f"Panel: {r['stamp']}")
    if r["shared_source"]:
        print("  One source: this cancels noise only. Shared blind spots survive a plurality.")
    if r["tie"]:
        print("TIE — the panel does not decide. The split is the answer; report it.")
    elif r["disagreement"]:
        print(
            f"WEAK PLURALITY — {r['winner']} at {r['share']:.0%}. "
            "Report the split, not just the winner."
        )
    else:
        print(f"Winner: {r['winner']} ({r['share']:.0%} of {r['n']})")


def spread_flag(flag: str, raw: str, n: int) -> list[str]:
    """One value broadcast to every draw, or exactly n comma-separated values."""
    parts = [p.strip() for p in raw.split(",")]
    if len(parts) == 1:
        return parts * n
    if len(parts) != n:
        sys.exit(f"{flag}: give one value for all {n} draws, or exactly {n} comma-separated")
    return parts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("numeric", "vote"), default="numeric")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument(
        "--source",
        required=True,
        help="who supplied each draw: one value for all, or n comma-separated "
        "(model family, or 'human')",
    )
    parser.add_argument(
        "--pedigree",
        default="",
        help=f"numeric mode only, required: {' | '.join(PEDIGREES)} "
        "— one value for all, or n comma-separated",
    )
    parser.add_argument("values", nargs="*", help="panel answers (or one per stdin line)")
    args = parser.parse_args()

    raw = args.values or [line.strip() for line in sys.stdin if line.strip()]
    sources = spread_flag("--source", args.source, len(raw))

    if args.mode == "numeric":
        if not args.pedigree.strip():
            sys.exit(
                f"--pedigree is required in numeric mode: {' | '.join(PEDIGREES)}. "
                "Say where the numbers came from; 'invented' is an honest answer."
            )
        try:
            values = [float(v) for v in raw]
        except ValueError as err:
            sys.exit(f"non-numeric value in numeric mode: {err}")
        result = numeric(values, sources, spread_flag("--pedigree", args.pedigree, len(raw)))
        printer = print_numeric
    else:
        result = vote(raw, sources)
        printer = print_vote

    if args.json:
        print(json.dumps(result, indent=2))
        return
    printer(result)


if __name__ == "__main__":
    main()
