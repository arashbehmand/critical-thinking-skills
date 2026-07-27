"""Prediction ledger with Brier scoring and calibration bins.

JSONL entries: {id, date, q, p, resolve_by, outcome: null|0|1, resolved_date?, note?}
Immutability: p and q are never editable — there is no edit command, and resolve refuses
already-resolved entries. Brier = mean((p - outcome)^2); lower is better; 0.25 = coin
flip at p=0.5. Bins compare stated p to observed frequency: the calibration finding.
"""

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any

BINS = ((0.0, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.01))


def read(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries = []
    for n, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError as err:
            sys.exit(f"{path}:{n}: bad JSON ({err})")
    return entries


def write_all(path: Path, entries: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in entries))


def cmd_add(args: argparse.Namespace) -> None:
    if not 0.0 <= args.p <= 1.0:
        sys.exit("--p must be in [0, 1]")
    datetime.date.fromisoformat(args.resolve_by)  # validate format
    path = Path(args.file)
    entries = read(path)
    nums = [int(e["id"].split("-")[1]) for e in entries if e.get("id", "").startswith("p-")]
    entry: dict[str, Any] = {
        "id": f"p-{max(nums, default=0) + 1}",
        "date": datetime.date.today().isoformat(),
        "q": args.q,
        "p": args.p,
        "resolve_by": args.resolve_by,
        "outcome": None,
    }
    if args.note:
        entry["note"] = args.note
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"logged {entry['id']}: p={args.p} resolve by {args.resolve_by}")


def cmd_resolve(args: argparse.Namespace) -> None:
    path = Path(args.file)
    entries = read(path)
    matches = [e for e in entries if e["id"] == args.id]
    if not matches:
        sys.exit(f"no entry {args.id}")
    entry = matches[0]
    if entry["outcome"] is not None:
        sys.exit(f"{args.id} already resolved (outcome={entry['outcome']}) — immutable")
    entry["outcome"] = args.outcome
    entry["resolved_date"] = datetime.date.today().isoformat()
    if args.note:
        entry["resolution_note"] = args.note
    write_all(path, entries)
    print(f"resolved {args.id}: outcome={args.outcome} (stated p was {entry['p']})")


def cmd_report(args: argparse.Namespace) -> None:
    entries = read(Path(args.file))
    if not entries:
        print("no predictions logged")
        return
    resolved = [e for e in entries if e["outcome"] is not None]
    pending = [e for e in entries if e["outcome"] is None]
    today = datetime.date.today().isoformat()
    overdue = [e for e in pending if e["resolve_by"] < today]

    print(f"predictions: {len(entries)}  resolved: {len(resolved)}  pending: {len(pending)}")
    if overdue:
        print(f"\nOVERDUE ({len(overdue)}) — resolve these before logging new ones:")
        for e in overdue:
            print(f"  {e['id']} (by {e['resolve_by']}): {e['q']}")
    if not resolved:
        return

    brier = sum((e["p"] - e["outcome"]) ** 2 for e in resolved) / len(resolved)
    mean_p = sum(e["p"] for e in resolved) / len(resolved)
    hit = sum(e["outcome"] for e in resolved) / len(resolved)
    print(f"\nBrier score: {brier:.3f} (0 perfect, 0.25 = coin flip at p=0.5)")
    print(
        f"Overall: stated {mean_p:.0%} on average, {hit:.0%} happened "
        f"({'over' if mean_p > hit else 'under'}confident by {abs(mean_p - hit):.0%})"
    )
    print("\nBy stated-probability bin (self-graded — label it so when reporting):")
    for lo, hi in BINS:
        in_bin = [e for e in resolved if lo <= e["p"] < hi]
        if not in_bin:
            continue
        bp = sum(e["p"] for e in in_bin) / len(in_bin)
        bh = sum(e["outcome"] for e in in_bin) / len(in_bin)
        print(
            f"  [{lo:.0%}–{min(hi, 1.0):.0%}): n={len(in_bin)}  stated~{bp:.0%}  happened {bh:.0%}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="log a prediction")
    p_add.add_argument("--file", required=True)
    p_add.add_argument("--q", required=True, help="stranger-resolvable question")
    p_add.add_argument("--p", type=float, required=True)
    p_add.add_argument("--resolve-by", required=True, help="ISO date")
    p_add.add_argument("--note")
    p_add.set_defaults(func=cmd_add)

    p_res = sub.add_parser("resolve", help="record an outcome (once, immutably)")
    p_res.add_argument("--file", required=True)
    p_res.add_argument("--id", required=True)
    p_res.add_argument("--outcome", type=int, choices=(0, 1), required=True)
    p_res.add_argument("--note", help="the observation a stranger could check")
    p_res.set_defaults(func=cmd_resolve)

    p_rep = sub.add_parser("report", help="Brier score + calibration bins")
    p_rep.add_argument("--file", required=True)
    p_rep.set_defaults(func=cmd_report)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
