"""ACH matrix scoring (Heuer 1999, *Psychology of Intelligence Analysis*, ch. 8).

inconsistency(H) = Σ evidence credibility over cells rated I, counted once per
ORIGIN; the survivor is the LEAST contradicted hypothesis, not the most supported
one. Non-diagnostic evidence is rated identically for every hypothesis.
Sensitivity reports the single-cell rating changes that would strictly swap
ranks 1 and 2.

Origins: evidence items may carry `origin`, naming the observation they trace
back to. Four restatements of one shift-log entry — the note, its copy in a
summary, a ticket citing it, an operator repeating it — are one observation, and
counting four independent credibility weights from them can manufacture a
confident wrong survivor out of a single source. A cluster contributes the
credibility of its best-evidenced I-rated member, once. Items with no `origin`
are their own origin, so a matrix that omits the field scores exactly as before.

Kept in exact behavioral parity with skills/ct-ach/scripts/ach_score.py
(pinned by tests/test_parity.py) — change both together or neither.
"""

from typing import Any

RATINGS = ("C", "I", "N")


def _validate(matrix: dict[str, Any]) -> None:
    h_ids = [h["id"] for h in matrix["hypotheses"]]
    e_ids = [e["id"] for e in matrix["evidence"]]
    if len(set(h_ids)) != len(h_ids) or len(set(e_ids)) != len(e_ids):
        raise ValueError("duplicate hypothesis or evidence ids")
    for e in matrix["evidence"]:
        if int(e["credibility"]) not in (1, 2, 3):
            raise ValueError(f"evidence {e['id']}: credibility must be 1, 2, or 3")
    seen: set[tuple[str, str]] = set()
    for r in matrix["ratings"]:
        key = (r["evidence_id"], r["hypothesis_id"])
        if r["evidence_id"] not in e_ids or r["hypothesis_id"] not in h_ids:
            raise ValueError(f"rating references unknown id: {key}")
        if r["rating"] not in RATINGS:
            raise ValueError(f"rating {key}: must be one of {RATINGS}, got {r['rating']!r}")
        if key in seen:
            raise ValueError(f"pair rated twice: {key}")
        seen.add(key)
    missing = [(e, h) for e in e_ids for h in h_ids if (e, h) not in seen]
    if missing:
        raise ValueError(f"unrated pairs: {missing} — every cell must be rated (N is allowed)")


def _cell_map(matrix: dict[str, Any]) -> dict[tuple[str, str], str]:
    return {(r["evidence_id"], r["hypothesis_id"]): r["rating"] for r in matrix["ratings"]}


def _origins(matrix: dict[str, Any]) -> dict[str, str]:
    """evidence id → origin id. An item with no `origin` is its own origin."""
    return {e["id"]: str(e.get("origin") or e["id"]) for e in matrix["evidence"]}


def _clusters(matrix: dict[str, Any]) -> dict[str, list[str]]:
    """Origins holding more than one item. Singletons are the default, so omitted."""
    origin = _origins(matrix)
    grouped: dict[str, list[str]] = {}
    for e in matrix["evidence"]:
        grouped.setdefault(origin[e["id"]], []).append(e["id"])
    return {name: ids for name, ids in grouped.items() if len(ids) > 1}


def _scores(matrix: dict[str, Any], cells: dict[tuple[str, str], str]) -> dict[str, int]:
    """Weighted inconsistency per hypothesis, counting each origin at most once."""
    cred = {e["id"]: int(e["credibility"]) for e in matrix["evidence"]}
    origin = _origins(matrix)
    scores: dict[str, int] = {}
    for h in matrix["hypotheses"]:
        per_origin: dict[str, int] = {}
        for e in matrix["evidence"]:
            if cells[(e["id"], h["id"])] == "I":
                key = origin[e["id"]]
                per_origin[key] = max(per_origin.get(key, 0), cred[e["id"]])
        scores[h["id"]] = sum(per_origin.values())
    return scores


def _diagnosticity(matrix: dict[str, Any], cells: dict[tuple[str, str], str]) -> dict[str, int]:
    """Distinct ratings an evidence item gives across hypotheses (1 = non-diagnostic)."""
    return {
        e["id"]: len({cells[(e["id"], h["id"])] for h in matrix["hypotheses"]})
        for e in matrix["evidence"]
    }


def _sensitivity(
    matrix: dict[str, Any], cells: dict[tuple[str, str], str], top: str, second: str
) -> list[str]:
    """Single-cell changes that would strictly put `second` ahead of `top`."""
    flips: list[str] = []
    for e in matrix["evidence"]:
        for h_id in (top, second):
            key = (e["id"], h_id)
            current = cells[key]
            for alt in RATINGS:
                if alt == current:
                    continue
                trial = dict(cells)
                trial[key] = alt
                s = _scores(matrix, trial)
                if s[second] < s[top]:
                    flips.append(f"{e['id']}x{h_id}: {current}->{alt} puts {second} ahead")
    return flips


def score(matrix: dict[str, Any]) -> dict[str, Any]:
    """Rank by weighted inconsistency; report ties, decoration, collapses, flip cells."""
    _validate(matrix)
    cells = _cell_map(matrix)
    s = _scores(matrix, cells)
    ranking = sorted(s, key=lambda h: s[h])
    diag = _diagnosticity(matrix, cells)
    non_diag = [e for e, d in diag.items() if d == 1]
    tie = len(ranking) > 1 and s[ranking[0]] == s[ranking[1]]
    flips = _sensitivity(matrix, cells, ranking[0], ranking[1]) if len(ranking) > 1 else []
    clusters = _clusters(matrix)
    return {
        "scores": s,
        "ranking": ranking,
        "tied_top": tie,
        "non_diagnostic_evidence": non_diag,
        "rank_flip_cells": flips,
        "origin_clusters": clusters,
        "collapsed": [
            f"{', '.join(ids)} → one origin ({name}); credibility counted once, "
            f"not {len(ids)} times"
            for name, ids in clusters.items()
        ],
    }
