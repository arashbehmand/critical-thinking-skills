"""Draw evidence subsets for an ensemble of perspectives, then aggregate their verdicts.

The idea is bagging, borrowed from random forests. A forest works because each tree sees
a resample of the data and is still a competent predictor on it; the trees decorrelate
without becoming useless. Splitting the evidence down to one item per rater is the
opposite trade — maximum decorrelation, no competence, because no single reading lets you
notice that three unrelated metrics all point the same way.

So: every agent sees the whole question and every hypothesis, and a random SUBSET of the
evidence. Each returns a full verdict. The script then does two mechanical things:

  vote        plurality across subsets, with the spread reported rather than averaged away
  influence   for each evidence item, the winner's vote share among subsets that included
              it minus the share among subsets that left it out

`influence` is permutation importance. It answers the question a reader actually has —
what is this conclusion resting on? — and it is strictly more informative than flipping
one cell at a time, because it measures an item's effect on the *verdict* rather than on
an intermediate score.

**The script draws the subsets, never the model.** If the orchestrator chooses who sees
what, it is picking the jury. Draws are seeded and reproducible.

Stdlib only. No LLM calls: the perspectives are gathered by the host agent (template T10).
"""

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_N = 7
DEFAULT_RATE = 0.65
MAX_REDRAWS = 64

#: An item that appears in every subset, or in none, gets no influence score — there is
#: nothing to compare it against. The draw is retried until every item is both in and out.
MIN_SIDE = 1


def load_evidence(path: str) -> list[dict[str, Any]]:
    """Accept an ACH matrix.json, a bench instance.json, or a bare list of items."""
    raw = json.loads(Path(path).read_text())
    items = raw.get("evidence", raw) if isinstance(raw, dict) else raw
    if not isinstance(items, list) or not items:
        sys.exit(f"{path}: expected a non-empty 'evidence' list")
    out = []
    for n, item in enumerate(items, 1):
        if not isinstance(item, dict) or "id" not in item:
            sys.exit(f"{path}: evidence item {n} has no 'id'")
        out.append(item)
    ids = [i["id"] for i in out]
    if len(set(ids)) != len(ids):
        sys.exit("duplicate evidence ids")
    return out


def draw(ids: list[str], n: int, rate: float, seed: int) -> list[list[str]]:
    """`n` subsets, each a `rate` sample without replacement, every item in and out once.

    Without replacement rather than a true bootstrap: a duplicated evidence line in a
    prompt reads as corroboration, which is the exact error `ct-entailment` exists to
    stop. Sampling without replacement keeps each subset a plain, readable dossier.
    """
    size = max(2, round(len(ids) * rate))
    if size >= len(ids):
        sys.exit(f"--rate {rate} keeps every item; nothing would vary. Lower it.")
    for attempt in range(MAX_REDRAWS):
        rng = random.Random(f"ct-bag:{seed}:{attempt}")
        subsets = [sorted(rng.sample(ids, size), key=ids.index) for _ in range(n)]
        seen = Counter(i for s in subsets for i in s)
        if all(MIN_SIDE <= seen[i] <= n - MIN_SIDE for i in ids):
            return subsets
    sys.exit(
        f"could not cover every item both in and out in {MAX_REDRAWS} draws — "
        f"raise --n (currently {n}) or move --rate toward 0.5"
    )


def cmd_draw(args: argparse.Namespace) -> None:
    items = load_evidence(args.evidence)
    ids = [i["id"] for i in items]
    subsets = draw(ids, args.n, args.rate, args.seed)
    text = {i["id"]: i for i in items}
    result = {
        "seed": args.seed,
        "n": args.n,
        "rate": args.rate,
        "subset_size": len(subsets[0]),
        "subsets": [{"id": f"S{k + 1}", "evidence_ids": s} for k, s in enumerate(subsets)],
    }
    if args.json:
        print(json.dumps(result, indent=2))
        return

    print(
        f"Rule: {args.n} subsets, {len(subsets[0])} of {len(ids)} items each "
        f"({args.rate:.0%}), sampled without replacement, seed {args.seed}. "
        "Every item is included in at least one subset and left out of at least one, "
        "so every item gets an influence score."
    )
    print("\nGive each subset to a SEPARATE fresh agent (template T10), with the full")
    print("question and the full hypothesis list. Do not tell it about the other subsets.\n")
    for block in result["subsets"]:
        print(f"--- {block['id']} ---")
        for eid in block["evidence_ids"]:
            item = text[eid]
            source = f" ({item['source']})" if item.get("source") else ""
            print(f"  {eid}: {item.get('text', '')}{source}")
        print()


def aggregate(subsets: list[dict[str, Any]], verdicts: dict[str, str]) -> dict[str, Any]:
    """Plurality across perspectives, plus per-item influence on the winner."""
    used = [s for s in subsets if s["id"] in verdicts]
    if len(used) < 3:
        raise ValueError(f"need at least 3 returned verdicts, got {len(used)}")

    votes = [verdicts[s["id"]] for s in used]
    counts = Counter(votes)
    ranked = counts.most_common()
    winner, top = ranked[0]
    tie = len(ranked) > 1 and ranked[1][1] == top
    share = top / len(votes)

    ids = sorted({i for s in used for i in s["evidence_ids"]})
    influence: list[dict[str, Any]] = []
    for eid in ids:
        inside = [verdicts[s["id"]] for s in used if eid in s["evidence_ids"]]
        outside = [verdicts[s["id"]] for s in used if eid not in s["evidence_ids"]]
        if not inside or not outside:
            continue
        in_share = sum(1 for v in inside if v == winner) / len(inside)
        out_share = sum(1 for v in outside if v == winner) / len(outside)
        influence.append(
            {
                "evidence_id": eid,
                "n_in": len(inside),
                "n_out": len(outside),
                "in_share": round(in_share, 3),
                "out_share": round(out_share, 3),
                "influence": round(in_share - out_share, 3),
            }
        )
    influence.sort(key=lambda r: (-abs(float(r["influence"])), str(r["evidence_id"])))
    carrying = [r["evidence_id"] for r in influence if abs(float(r["influence"])) >= 0.5]
    return {
        "n": len(votes),
        "counts": dict(counts),
        "winner": None if tie else winner,
        "share": round(share, 3),
        "tie": tie,
        "disagreement": tie or share < 0.6,
        "influence": influence,
        "load_bearing": carrying,
    }


def cmd_aggregate(args: argparse.Namespace) -> None:
    drawn = json.loads(Path(args.draws).read_text())["subsets"]
    raw = json.loads(Path(args.verdicts).read_text())
    rows = raw.get("verdicts", raw) if isinstance(raw, dict) else raw
    verdicts = {r["subset_id"]: str(r["verdict"]) for r in rows}
    try:
        result = aggregate(drawn, verdicts)
    except ValueError as err:
        sys.exit(str(err))

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print(
        "Rule: plurality across perspectives; flag on a tie or winner share < 0.6. "
        "influence(e) = winner's share among subsets holding e, minus its share among "
        "subsets without e. |influence| >= 0.5 is load-bearing."
    )
    print(f"\nperspectives: {result['n']}   votes: {result['counts']}")
    if result["tie"]:
        print("TIE — the ensemble does not decide. Report the split; it is the finding.")
    elif result["disagreement"]:
        print(
            f"WEAK PLURALITY — {result['winner']} at {result['share']:.0%}. "
            "Report the split, not just the winner."
        )
    else:
        print(f"Winner: {result['winner']} ({result['share']:.0%} of {result['n']})")

    print("\nEvidence influence on the winner (most load-bearing first):")
    for row in result["influence"][:10]:
        mark = "  <-- load-bearing" if row["evidence_id"] in result["load_bearing"] else ""
        print(
            f"  {row['evidence_id']:>5}: {row['influence']:+.2f}  "
            f"(with it {row['in_share']:.0%} of {row['n_in']}, "
            f"without it {row['out_share']:.0%} of {row['n_out']}){mark}"
        )
    if result["load_bearing"]:
        print(
            f"\nThe verdict rests on {', '.join(result['load_bearing'])}. "
            "Check those first — and check them against their sources, not against "
            "each other."
        )
    else:
        print("\nNo single item carries the verdict; it survives leaving any one item out.")

    if result["influence"] and len(result["load_bearing"]) > len(result["influence"]) / 3:
        print(
            f"\nCAUTION: {len(result['load_bearing'])} of {len(result['influence'])} items "
            f"cleared the load-bearing threshold on only {result['n']} perspectives. With a "
            "small ensemble each share can take a handful of values, so influence is coarse "
            "and this list is longer than it should be. Trust the vote; re-run with --n 15 "
            "or more before trusting the ranking."
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_draw = sub.add_parser("draw", help="emit seeded evidence subsets, one per perspective")
    p_draw.add_argument("--evidence", required=True, help="matrix.json / instance.json / list")
    p_draw.add_argument("--n", type=int, default=DEFAULT_N, help=f"perspectives ({DEFAULT_N})")
    p_draw.add_argument(
        "--rate",
        type=float,
        default=DEFAULT_RATE,
        help=f"share of evidence each sees ({DEFAULT_RATE})",
    )
    p_draw.add_argument("--seed", type=int, default=0)
    p_draw.add_argument("--json", action="store_true")
    p_draw.set_defaults(func=cmd_draw)

    p_agg = sub.add_parser("aggregate", help="vote + per-item influence on the verdict")
    p_agg.add_argument("--draws", required=True, help="the --json output of `draw`")
    p_agg.add_argument("--verdicts", required=True, help="[{subset_id, verdict}, ...]")
    p_agg.add_argument("--json", action="store_true")
    p_agg.set_defaults(func=cmd_aggregate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
