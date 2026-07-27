"""Append-only commitment log for long multi-step work.

JSONL entries: {id, ts, statement, tags: [..], supersedes?}
`pairs` emits candidate same-tag pairs of ACTIVE entries (not superseded) formatted for
a fresh-subagent contradiction review (template T8). The judgment stays with the
reviewer; this script only does the bookkeeping.
"""

import argparse
import datetime
import itertools
import json
import sys
from pathlib import Path
from typing import Any

PAIR_CAP = 100


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


def active(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    superseded = {e["supersedes"] for e in entries if e.get("supersedes")}
    return [e for e in entries if e["id"] not in superseded]


def cmd_add(args: argparse.Namespace) -> None:
    path = Path(args.file)
    entries = read(path)
    if args.supersedes and args.supersedes not in {e["id"] for e in entries}:
        sys.exit(f"--supersedes {args.supersedes}: no such entry")
    nums = [int(e["id"].split("-")[1]) for e in entries if e.get("id", "").startswith("c-")]
    entry: dict[str, Any] = {
        "id": f"c-{max(nums, default=0) + 1}",
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        "statement": args.statement,
        "tags": [t.strip() for t in args.tags.split(",") if t.strip()],
    }
    if args.supersedes:
        entry["supersedes"] = args.supersedes
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"logged {entry['id']} tags={','.join(entry['tags']) or '-'}")


def cmd_list(args: argparse.Namespace) -> None:
    entries = active(read(Path(args.file)))
    if args.tag:
        entries = [e for e in entries if args.tag in e.get("tags", [])]
    for e in entries:
        print(f"{e['id']} [{','.join(e.get('tags', []))}] {e['statement']}")
    print(f"({len(entries)} active)")


def cmd_pairs(args: argparse.Namespace) -> None:
    entries = active(read(Path(args.file)))
    if args.all:
        pairs = list(itertools.combinations(entries, 2))
    else:
        pairs = [
            (a, b)
            for a, b in itertools.combinations(entries, 2)
            if set(a.get("tags", [])) & set(b.get("tags", []))
        ]
    if not pairs:
        print("no candidate pairs (log fewer than 2 active entries, or no shared tags)")
        return
    shown = pairs[:PAIR_CAP]
    print("Candidate pairs for contradiction review (hand to a fresh subagent, T8):\n")
    for n, (a, b) in enumerate(shown, 1):
        print(f"{n}. [{a['id']}] {a['statement']}")
        print(f"   [{b['id']}] {b['statement']}")
    if len(pairs) > len(shown):
        print(
            f"\nTRUNCATED: {len(pairs) - len(shown)} more pairs not shown — "
            "review in batches; do not treat this list as complete."
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="append a commitment")
    p_add.add_argument("--file", required=True)
    p_add.add_argument("--statement", required=True)
    p_add.add_argument("--tags", default="")
    p_add.add_argument("--supersedes")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="show active commitments")
    p_list.add_argument("--file", required=True)
    p_list.add_argument("--tag")
    p_list.set_defaults(func=cmd_list)

    p_pairs = sub.add_parser("pairs", help="emit candidate pairs for review")
    p_pairs.add_argument("--file", required=True)
    p_pairs.add_argument("--all", action="store_true", help="all active pairs, not just same-tag")
    p_pairs.set_defaults(func=cmd_pairs)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
