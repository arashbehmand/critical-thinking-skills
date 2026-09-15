"""Truth-maintenance impact over a recorded commitment dependency graph.

The input is the append-only record used by ``ct-consistency-log``: every
entry may depend on earlier entries and a later entry may supersede an earlier
one. Status follows justification-based truth maintenance (Doyle 1979): a
superseded entry is not live, and every claim depending directly or
transitively on a non-live premise is OUT.

Withdrawal impact is computed by removing each currently ACTIVE entry in turn
and repeating the status walk. The affected set is therefore exact *for the
recorded graph*. It is not a certificate about the reasoning: dependencies the
author failed to record are absent, and imagined dependencies remain present.

Kept in behavioral parity with
skills/ct-consistency-log/scripts/commitlog.py ``impact --json`` (pinned by
tests/test_parity.py) — change both together or neither.
"""

from typing import Any


def _validate(entries: list[dict[str, Any]]) -> None:
    ids = [str(entry.get("id") or "").strip() for entry in entries]
    if any(not entry_id for entry_id in ids):
        raise ValueError("every dependency entry needs a non-empty id")
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate dependency entry ids")
    for entry in entries:
        depends_on = entry.get("depends_on", [])
        if not isinstance(depends_on, list) or any(not isinstance(dep, str) for dep in depends_on):
            raise ValueError(f"{entry['id']}: depends_on must be a list of ids")
        if len(set(depends_on)) != len(depends_on):
            raise ValueError(f"{entry['id']}: duplicate ids in depends_on")
        if entry["id"] in depends_on:
            raise ValueError(f"{entry['id']}: an entry cannot depend directly on itself")


def statuses(entries: list[dict[str, Any]], withdrawn: str | None = None) -> dict[str, str]:
    """ACTIVE | SUPERSEDED | OUT, plus WITHDRAWN for a simulated removal."""
    _validate(entries)
    superseded = {str(entry["supersedes"]) for entry in entries if entry.get("supersedes")}
    known = {str(entry["id"]) for entry in entries}
    if withdrawn is not None and withdrawn not in known:
        raise ValueError(f"unknown withdrawn entry: {withdrawn}")
    status = {
        str(entry["id"]): "SUPERSEDED" if entry["id"] in superseded else "ACTIVE"
        for entry in entries
    }
    if withdrawn is not None:
        if status[withdrawn] != "ACTIVE":
            raise ValueError(f"cannot simulate withdrawal of non-active entry: {withdrawn}")
        status[withdrawn] = "WITHDRAWN"
    edges = {str(entry["id"]): list(entry.get("depends_on", [])) for entry in entries}

    changed = True
    while changed:
        changed = False
        for entry_id, parents in edges.items():
            if status[entry_id] != "ACTIVE":
                continue
            if any(parent not in known or status[parent] != "ACTIVE" for parent in parents):
                status[entry_id] = "OUT"
                changed = True
    return status


def analyze(entries: list[dict[str, Any]], targets: list[str] | None = None) -> dict[str, Any]:
    """Rank active entries by the live claims their hypothetical withdrawal knocks OUT."""
    base = statuses(entries)
    active = sorted(entry_id for entry_id, status in base.items() if status == "ACTIVE")
    target_ids = list(dict.fromkeys(targets or []))
    for target in target_ids:
        if target not in base:
            raise ValueError(f"unknown target entry: {target}")
        if base[target] != "ACTIVE":
            raise ValueError(f"target entry is not active: {target} ({base[target]})")

    rows: list[dict[str, Any]] = []
    target_impact: dict[str, list[str]] = {target: [] for target in target_ids}
    for candidate in active:
        trial = statuses(entries, withdrawn=candidate)
        affected = sorted(
            entry_id for entry_id in active if entry_id != candidate and trial[entry_id] == "OUT"
        )
        row = {"id": candidate, "n_affected": len(affected), "affected": affected}
        rows.append(row)
        for target in target_ids:
            if target in affected:
                target_impact[target].append(candidate)

    rows.sort(key=lambda row: (-int(row["n_affected"]), str(row["id"])))
    return {
        "statuses": base,
        "active": active,
        "withdrawal_impact": rows,
        "critical": [row for row in rows if row["n_affected"] > 0],
        "target_dependencies": target_impact,
    }
