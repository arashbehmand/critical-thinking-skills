"""Append-only commitment log with dependency edges, for long multi-step work.

JSONL entries: {id, ts, statement, tags: [..], depends_on: [ids], supersedes?}

Two different failures, two different sweeps, and both are needed:

  `pairs` emits candidate same-tag pairs of live entries for a fresh-subagent
  contradiction review (template T8). It catches "I said A at step 3 and not-A at
  step 40".

  `check` walks the dependency edges. It catches "I withdrew A at step 4 and step 19
  still rests on it" — a failure invisible in the output by construction, because a
  conclusion resting on a retracted premise looks exactly like a correct one.

Status is COMPUTED, never written: the log stays append-only (conventions §4).
SUPERSEDED = some later entry supersedes it. OUT = depends, transitively, on something
not live. ACTIVE = everything else. The walk deliberately over-marks when edges are
missing — silence is the safe failure here; false confidence is not.

The judgment stays with the reviewer; this script only does the bookkeeping.
"""

import argparse
import datetime
import itertools
import json
import sys
from pathlib import Path
from typing import Any

PAIR_CAP = 100

CAVEAT = (
    "Caveat: this record is model-authored, and this detects inconsistencies among "
    "recorded dependencies only. Dependencies never noticed are absent; dependencies "
    "imagined are present. Nothing here is a structural certificate — no minimum cut, "
    "no weakest link. It is exact about the record and says nothing about the reasoning."
)


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


def statuses(entries: list[dict[str, Any]]) -> dict[str, str]:
    """ACTIVE | SUPERSEDED | OUT per entry id, by transitive closure over depends_on.

    Conservative on purpose: an entry that depends on an id the log does not contain is
    marked OUT too, because an unresolvable premise is not a live one.
    """
    superseded = {e["supersedes"] for e in entries if e.get("supersedes")}
    known = {e["id"] for e in entries}
    status = {e["id"]: ("SUPERSEDED" if e["id"] in superseded else "ACTIVE") for e in entries}
    edges = {e["id"]: [d for d in e.get("depends_on", [])] for e in entries}

    # Repeat until nothing changes: OUT propagates along dependency edges, and the loop
    # terminates because a status only ever moves ACTIVE -> OUT.
    changed = True
    while changed:
        changed = False
        for entry_id, parents in edges.items():
            if status[entry_id] != "ACTIVE":
                continue
            if any(p not in known or status[p] != "ACTIVE" for p in parents):
                status[entry_id] = "OUT"
                changed = True
    return status


def live(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    status = statuses(entries)
    return [e for e in entries if status[e["id"]] == "ACTIVE"]


def _roots(entries: list[dict[str, Any]], entry_id: str, status: dict[str, str]) -> list[str]:
    """The not-live premises an OUT entry ultimately rests on."""
    edges = {e["id"]: list(e.get("depends_on", [])) for e in entries}
    known = set(edges)
    found: list[str] = []
    seen: set[str] = set()
    stack = list(edges.get(entry_id, []))
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        if current not in known:
            found.append(f"{current} (no such entry)")
        elif status[current] != "ACTIVE":
            found.append(current)
            stack.extend(edges[current])
    return sorted(set(found))


def _cycles(entries: list[dict[str, Any]]) -> list[list[str]]:
    """Circular support: a claim that, through the chain, rests on itself."""
    known = {e["id"] for e in entries}
    edges = {e["id"]: [d for d in e.get("depends_on", []) if d in known] for e in entries}
    found: list[list[str]] = []
    colour: dict[str, int] = dict.fromkeys(edges, 0)

    def walk(node: str, path: list[str]) -> None:
        colour[node] = 1
        for parent in edges[node]:
            if colour[parent] == 1:
                cycle = [*path[path.index(parent) :], parent]
                if cycle not in found:
                    found.append(cycle)
            elif colour[parent] == 0:
                walk(parent, [*path, parent])
        colour[node] = 2

    for node in edges:
        if colour[node] == 0:
            walk(node, [node])
    return found


def cmd_add(args: argparse.Namespace) -> None:
    path = Path(args.file)
    entries = read(path)
    known = {e["id"] for e in entries}
    if args.supersedes and args.supersedes not in known:
        sys.exit(f"--supersedes {args.supersedes}: no such entry")
    depends_on = [d.strip() for d in (args.depends_on or "").split(",") if d.strip()]
    for dep in depends_on:
        if dep not in known:
            sys.exit(f"--depends-on {dep}: no such entry (log the premise first)")
    nums = [int(e["id"].split("-")[1]) for e in entries if e.get("id", "").startswith("c-")]
    entry: dict[str, Any] = {
        "id": f"c-{max(nums, default=0) + 1}",
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        "statement": args.statement,
        "tags": [t.strip() for t in args.tags.split(",") if t.strip()],
        "depends_on": depends_on,
    }
    if args.supersedes:
        entry["supersedes"] = args.supersedes
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(
        f"logged {entry['id']} tags={','.join(entry['tags']) or '-'} "
        f"rests-on={','.join(depends_on) or '-'}"
    )
    if args.supersedes:
        # Superseding is the moment dependents fall over. Say so now, not at delivery.
        after = statuses(read(path))
        knocked = sorted(i for i, s in after.items() if s == "OUT")
        if knocked:
            print(f"  now OUT — re-derive or drop before delivering: {', '.join(knocked)}")


def cmd_list(args: argparse.Namespace) -> None:
    entries = read(Path(args.file))
    status = statuses(entries)
    shown = [e for e in entries if args.all or status[e["id"]] == "ACTIVE"]
    if args.tag:
        shown = [e for e in shown if args.tag in e.get("tags", [])]
    for e in shown:
        mark = "" if status[e["id"]] == "ACTIVE" else f" [{status[e['id']]}]"
        print(f"{e['id']} [{','.join(e.get('tags', []))}]{mark} {e['statement']}")
    counts = {s: sum(1 for v in status.values() if v == s) for s in ("ACTIVE", "SUPERSEDED", "OUT")}
    print(f"({counts['ACTIVE']} active, {counts['SUPERSEDED']} superseded, {counts['OUT']} out)")


def cmd_pairs(args: argparse.Namespace) -> None:
    entries = read(Path(args.file))
    status = statuses(entries)
    active = [e for e in entries if status[e["id"]] == "ACTIVE"]
    excluded = sum(1 for v in status.values() if v == "OUT")
    if args.all:
        pairs = list(itertools.combinations(active, 2))
    else:
        pairs = [
            (a, b)
            for a, b in itertools.combinations(active, 2)
            if set(a.get("tags", [])) & set(b.get("tags", []))
        ]
    if excluded:
        print(f"NOTE: {excluded} OUT entries excluded — run `check` and resolve them first.\n")
    if not pairs:
        print("no candidate pairs (fewer than 2 live entries, or no shared tags)")
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


def cmd_check(args: argparse.Namespace) -> None:
    entries = read(Path(args.file))
    if not entries:
        print("log empty")
        return
    status = statuses(entries)
    text = {e["id"]: e["statement"] for e in entries}

    out = [e for e in entries if status[e["id"]] == "OUT"]
    if out:
        print(f"OUT ({len(out)}) — resting on something withdrawn; re-derive or drop each:\n")
        for e in out:
            print(f"  {e['id']}: {e['statement']}")
            print(f"      rests on: {', '.join(_roots(entries, e['id'], status)) or '(unknown)'}")
    else:
        print("No OUT entries: every live claim rests on live premises.")

    cycles = _cycles(entries)
    if cycles:
        print(f"\nCIRCULAR SUPPORT ({len(cycles)}) — these support themselves:")
        for cycle in cycles:
            print(f"  {' -> '.join(cycle)}")

    dependents: dict[str, list[str]] = {}
    for e in entries:
        if status[e["id"]] != "ACTIVE":
            continue
        for dep in e.get("depends_on", []):
            dependents.setdefault(dep, []).append(e["id"])
    shared = {k: v for k, v in dependents.items() if len(v) >= args.fanout}
    if shared:
        print(f"\nSHARED PREMISES (>= {args.fanout} live claims each):")
        for premise, children in sorted(shared.items()):
            print(f"  {len(children)} claims rest on {premise}: {text.get(premise, '?')}")
            print(f"      {', '.join(children)}")
        print("  One retraction takes all of them. Check that premise first.")

    bare = [e["id"] for e in entries if not e.get("depends_on")]
    if len(bare) == len(entries) and len(entries) > 2:
        print(
            f"\nNo entry records a dependency ({len(entries)} entries). That is a "
            "transcript summary, not a dependency record — populate depends_on at "
            "write time, never by reconstructing at the end."
        )

    print(f"\n{CAVEAT}")
    if out:
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="append a commitment")
    p_add.add_argument("--file", required=True)
    p_add.add_argument("--statement", required=True)
    p_add.add_argument("--tags", default="")
    p_add.add_argument("--depends-on", default="", help="comma-separated ids this rests on")
    p_add.add_argument("--supersedes")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="show commitments and their status")
    p_list.add_argument("--file", required=True)
    p_list.add_argument("--tag")
    p_list.add_argument("--all", action="store_true", help="include superseded and OUT entries")
    p_list.set_defaults(func=cmd_list)

    p_pairs = sub.add_parser("pairs", help="emit candidate pairs for contradiction review")
    p_pairs.add_argument("--file", required=True)
    p_pairs.add_argument("--all", action="store_true", help="all live pairs, not just same-tag")
    p_pairs.set_defaults(func=cmd_pairs)

    p_check = sub.add_parser("check", help="walk dependencies: OUT, cycles, shared premises")
    p_check.add_argument("--file", required=True)
    p_check.add_argument("--fanout", type=int, default=3, help="shared-premise reporting threshold")
    p_check.set_defaults(func=cmd_check)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
