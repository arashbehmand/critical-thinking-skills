"""Append-only evidence ledger: claims tied to sources with quality grades.

JSONL entries: {id, date, claim, source, url?, grade A|B|C|D, note?, supersedes?}
Grades: A primary/measured, B reputable secondary, C weak, D memory/unsourced.
"naked" = grade D or empty source — visible in `report`, meant to be fixed, not hidden.
Corrections are new entries with --supersedes; lines are never edited.
"""

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any

GRADES = ("A", "B", "C", "D")


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


def next_id(entries: list[dict[str, Any]]) -> str:
    nums = [int(e["id"].split("-")[1]) for e in entries if e.get("id", "").startswith("ev-")]
    return f"ev-{max(nums, default=0) + 1}"


def active(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    superseded = {e["supersedes"] for e in entries if e.get("supersedes")}
    return [e for e in entries if e["id"] not in superseded]


def cmd_add(args: argparse.Namespace) -> None:
    path = Path(args.file)
    entries = read(path)
    if args.supersedes and args.supersedes not in {e["id"] for e in entries}:
        sys.exit(f"--supersedes {args.supersedes}: no such entry")
    entry = {
        "id": next_id(entries),
        "date": datetime.date.today().isoformat(),
        "claim": args.claim,
        "source": args.source,
        "grade": args.grade,
    }
    if args.url:
        entry["url"] = args.url
    if args.note:
        entry["note"] = args.note
    if args.supersedes:
        entry["supersedes"] = args.supersedes
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    naked = " (NAKED — source it, hedge it, or cut it)" if is_naked(entry) else ""
    print(f"added {entry['id']} grade {entry['grade']}{naked}")


def is_naked(e: dict[str, Any]) -> bool:
    return e.get("grade") == "D" or not e.get("source", "").strip()


def cmd_report(args: argparse.Namespace) -> None:
    entries = active(read(Path(args.file)))
    if not entries:
        print("ledger empty")
        return
    by_grade = {g: [e for e in entries if e.get("grade") == g] for g in GRADES}
    print(
        f"Active claims: {len(entries)}   " + "  ".join(f"{g}:{len(by_grade[g])}" for g in GRADES)
    )
    naked = [e for e in entries if is_naked(e)]
    if naked:
        print(f"\nNAKED CLAIMS ({len(naked)}) — stated as fact with nothing behind them:")
        for e in naked:
            print(f"  {e['id']}: {e['claim']}")
        print("Fix each: source it (supersede), hedge it in the text, or cut it.")
    else:
        print("No naked claims.")


def cmd_validate(args: argparse.Namespace) -> None:
    entries = read(Path(args.file))
    problems = []
    for e in entries:
        for field in ("id", "date", "claim", "grade"):
            if field not in e:
                problems.append(f"{e.get('id', '?')}: missing {field}")
        if e.get("grade") not in GRADES:
            problems.append(f"{e.get('id', '?')}: bad grade {e.get('grade')!r}")
    if problems:
        print("\n".join(problems))
        sys.exit(1)
    print(f"{len(entries)} entries OK")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="append a claim")
    p_add.add_argument("--file", required=True)
    p_add.add_argument("--claim", required=True)
    p_add.add_argument("--source", default="")
    p_add.add_argument("--grade", required=True, choices=GRADES)
    p_add.add_argument("--url")
    p_add.add_argument("--note")
    p_add.add_argument("--supersedes")
    p_add.set_defaults(func=cmd_add)

    p_rep = sub.add_parser("report", help="grade distribution + naked claims")
    p_rep.add_argument("--file", required=True)
    p_rep.set_defaults(func=cmd_report)

    p_val = sub.add_parser("validate", help="schema-check every line")
    p_val.add_argument("--file", required=True)
    p_val.set_defaults(func=cmd_validate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
