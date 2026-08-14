"""Prediction ledger with Brier scoring and calibration bins.

JSONL entries: {id, date, q, p, resolve_by, outcome: null|0|1, resolved_date?,
resolved_by?, note?}
Immutability: p and q are never editable — there is no edit command, and resolve refuses
already-resolved entries. Brier = mean((p - outcome)^2); lower is better; 0.25 = coin
flip at p=0.5. Bins compare stated p to observed frequency: the calibration finding.

Every resolution records --resolved-by (self | ci | tracker | human | <name>) and the
report breaks the score out by resolver. This does not close the gap — you can still
write "ci" on a self-resolution — but it makes the gap MEASURABLE instead of merely
disclosed: a ledger whose resolutions are all `self` now says so on its own face
("Brier 0.18 across 22 predictions, 20 self-resolved") rather than reporting a bare
number. Resolutions written before the field existed report as `unrecorded`.

Kept in exact behavioral parity with src/ctmcp/core/brier.py for the `report` shape
(pinned by tests/test_parity.py) — change both together or neither.
"""

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any

BINS = ((0.0, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.01))
RESOLVERS = ("self", "ci", "tracker", "human")


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


def resolver(entry: dict[str, Any]) -> str:
    """Who recorded the outcome. Absent on older ledgers — name that, don't assume."""
    return str(entry.get("resolved_by") or "").strip() or "unrecorded"


def report(entries: list[dict[str, Any]], today: str) -> dict[str, Any]:
    """Score resolved predictions, break out by resolver, surface pending/overdue ones."""
    for e in entries:
        if not 0.0 <= float(e["p"]) <= 1.0:
            raise ValueError(f"{e.get('id', '?')}: p must be in [0, 1]")
        if e["outcome"] not in (None, 0, 1):
            raise ValueError(f"{e.get('id', '?')}: outcome must be null, 0, or 1")
    resolved = [e for e in entries if e["outcome"] is not None]
    pending = [e for e in entries if e["outcome"] is None]
    overdue_ids = [e["id"] for e in pending if str(e["resolve_by"]) < today]

    result: dict[str, Any] = {
        "n": len(entries),
        "n_resolved": len(resolved),
        "n_pending": len(pending),
        "overdue_ids": overdue_ids,
        "brier": None,
        "mean_p": None,
        "hit_rate": None,
        "bins": [],
        "n_self_resolved": 0,
        "by_resolver": [],
    }
    if not resolved:
        return result

    groups: dict[str, list[dict[str, Any]]] = {}
    for e in resolved:
        groups.setdefault(resolver(e), []).append(e)
    rows: list[dict[str, Any]] = [
        {
            "resolver": name,
            "n": len(group),
            "brier": sum((e["p"] - e["outcome"]) ** 2 for e in group) / len(group),
        }
        for name, group in groups.items()
    ]
    rows.sort(key=lambda row: (-int(row["n"]), str(row["resolver"])))
    result["by_resolver"] = rows
    result["n_self_resolved"] = len(groups.get("self", []))

    result["brier"] = sum((e["p"] - e["outcome"]) ** 2 for e in resolved) / len(resolved)
    result["mean_p"] = sum(e["p"] for e in resolved) / len(resolved)
    result["hit_rate"] = sum(e["outcome"] for e in resolved) / len(resolved)
    bins: list[dict[str, Any]] = []
    for lo, hi in BINS:
        in_bin = [e for e in resolved if lo <= e["p"] < hi]
        if not in_bin:
            continue
        bins.append(
            {
                "lo": lo,
                "hi": min(hi, 1.0),
                "n": len(in_bin),
                "stated_mean": sum(e["p"] for e in in_bin) / len(in_bin),
                "hit_rate": sum(e["outcome"] for e in in_bin) / len(in_bin),
            }
        )
    result["bins"] = bins
    return result


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
    who = args.resolved_by.strip()
    if not who:
        sys.exit(f"--resolved-by is required: {' | '.join(RESOLVERS)} | <name>")
    entry["outcome"] = args.outcome
    entry["resolved_date"] = datetime.date.today().isoformat()
    entry["resolved_by"] = who
    if args.note:
        entry["resolution_note"] = args.note
    write_all(path, entries)
    print(f"resolved {args.id}: outcome={args.outcome} by {who} (stated p was {entry['p']})")


def cmd_report(args: argparse.Namespace) -> None:
    entries = read(Path(args.file))
    today = args.today or datetime.date.today().isoformat()
    if not entries:
        if args.json:
            print(json.dumps(report([], today), indent=2))
            return
        print("no predictions logged")
        return
    try:
        r = report(entries, today)
    except ValueError as err:
        sys.exit(str(err))

    if args.json:
        print(json.dumps(r, indent=2))
        return

    by_id = {e["id"]: e for e in entries}
    print(f"predictions: {r['n']}  resolved: {r['n_resolved']}  pending: {r['n_pending']}")
    if r["overdue_ids"]:
        print(f"\nOVERDUE ({len(r['overdue_ids'])}) — resolve these before logging new ones:")
        for pid in r["overdue_ids"]:
            e = by_id[pid]
            print(f"  {pid} (by {e['resolve_by']}): {e['q']}")
    if not r["n_resolved"]:
        return

    print(f"\nBrier score: {r['brier']:.3f} (0 perfect, 0.25 = coin flip at p=0.5)")
    print(
        f"Overall: stated {r['mean_p']:.0%} on average, {r['hit_rate']:.0%} happened "
        f"({'over' if r['mean_p'] > r['hit_rate'] else 'under'}confident by "
        f"{abs(r['mean_p'] - r['hit_rate']):.0%})"
    )

    print("\nBy resolver — who recorded the outcome:")
    for row in r["by_resolver"]:
        print(f"  {row['resolver']:>10}: n={row['n']}  Brier {row['brier']:.3f}")
    share = r["n_self_resolved"] / r["n_resolved"]
    if share:
        print(
            f"  Report as: Brier {r['brier']:.2f} across {r['n_resolved']} predictions, "
            f"{r['n_self_resolved']} self-resolved ({share:.0%} graded by the predictor)."
        )
    if share == 1.0:
        print("  Every outcome was self-recorded. This measures consistency, not accuracy.")

    print("\nBy stated-probability bin:")
    for b in r["bins"]:
        print(
            f"  [{b['lo']:.0%}–{b['hi']:.0%}): n={b['n']}  "
            f"stated~{b['stated_mean']:.0%}  happened {b['hit_rate']:.0%}"
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
    p_res.add_argument(
        "--resolved-by",
        required=True,
        help=f"who observed it: {' | '.join(RESOLVERS)} | <name>. "
        "'self' is honest and is the point of recording it.",
    )
    p_res.add_argument("--note", help="the observation a stranger could check")
    p_res.set_defaults(func=cmd_resolve)

    p_rep = sub.add_parser("report", help="Brier score + calibration bins")
    p_rep.add_argument("--file", required=True)
    p_rep.add_argument("--json", action="store_true", help="machine-readable output")
    p_rep.add_argument("--today", default="", help="ISO date (default: today) — keeps it pure")
    p_rep.set_defaults(func=cmd_report)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
