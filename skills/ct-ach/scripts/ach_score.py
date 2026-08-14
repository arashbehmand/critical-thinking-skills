"""Score an ACH (analysis of competing hypotheses) matrix.

Input: matrix.json — see the ct-ach SKILL.md for the schema. Every
(evidence x hypothesis) pair must be rated exactly once with C, I, or N.

Rules applied (printed so a reader can check by hand):
  inconsistency(H) = sum of evidence credibility over cells rated I, counted once
  per origin.
  ranking: ascending inconsistency — the survivor is the LEAST contradicted
  hypothesis, not the most supported one (Heuer, ch. 8).
  origins: items sharing an `origin` are one observation. The cluster contributes
  its best-evidenced I-rated member's credibility, once. Four restatements of one
  shift-log entry would otherwise carry four independent weights and can
  manufacture a confident wrong survivor out of a single source. Items with no
  `origin` are their own origin, so an older matrix scores exactly as before.
  non-diagnostic evidence: rated identically for every hypothesis.
  sensitivity: single-cell rating changes that would swap ranks 1 and 2.
"""

import argparse
import json
import sys
from typing import Any

RATINGS = ("C", "I", "N")


def load(path: str) -> dict[str, Any]:
    with open(path) as f:
        m: dict[str, Any] = json.load(f)
    h_ids = [h["id"] for h in m["hypotheses"]]
    e_ids = [e["id"] for e in m["evidence"]]
    if len(set(h_ids)) != len(h_ids) or len(set(e_ids)) != len(e_ids):
        sys.exit("duplicate hypothesis or evidence ids")
    for e in m["evidence"]:
        if int(e["credibility"]) not in (1, 2, 3):
            sys.exit(f"evidence {e['id']}: credibility must be 1, 2, or 3")
    seen = set()
    for r in m["ratings"]:
        key = (r["evidence_id"], r["hypothesis_id"])
        if r["evidence_id"] not in e_ids or r["hypothesis_id"] not in h_ids:
            sys.exit(f"rating references unknown id: {key}")
        if r["rating"] not in RATINGS:
            sys.exit(f"rating {key}: must be one of {RATINGS}, got {r['rating']!r}")
        if key in seen:
            sys.exit(f"pair rated twice: {key}")
        seen.add(key)
    missing = [(e, h) for e in e_ids for h in h_ids if (e, h) not in seen]
    if missing:
        sys.exit(f"unrated pairs: {missing} — every cell must be rated (N is allowed)")
    return m


def cell_map(m: dict[str, Any]) -> dict[tuple[str, str], str]:
    return {(r["evidence_id"], r["hypothesis_id"]): r["rating"] for r in m["ratings"]}


def origins(m: dict[str, Any]) -> dict[str, str]:
    """evidence id → origin id. An item with no `origin` is its own origin."""
    return {e["id"]: str(e.get("origin") or e["id"]) for e in m["evidence"]}


def clusters(m: dict[str, Any]) -> dict[str, list[str]]:
    """Origins holding more than one item. Singletons are the default, so omitted."""
    origin = origins(m)
    grouped: dict[str, list[str]] = {}
    for e in m["evidence"]:
        grouped.setdefault(origin[e["id"]], []).append(e["id"])
    return {name: ids for name, ids in grouped.items() if len(ids) > 1}


def scores(m: dict[str, Any], cells: dict[tuple[str, str], str]) -> dict[str, int]:
    """Weighted inconsistency per hypothesis, counting each origin at most once."""
    cred = {e["id"]: int(e["credibility"]) for e in m["evidence"]}
    origin = origins(m)
    result: dict[str, int] = {}
    for h in m["hypotheses"]:
        per_origin: dict[str, int] = {}
        for e in m["evidence"]:
            if cells[(e["id"], h["id"])] == "I":
                key = origin[e["id"]]
                per_origin[key] = max(per_origin.get(key, 0), cred[e["id"]])
        result[h["id"]] = sum(per_origin.values())
    return result


def diagnosticity(m: dict[str, Any], cells: dict[tuple[str, str], str]) -> dict[str, int]:
    """Distinct ratings an evidence item gives across hypotheses (1 = non-diagnostic)."""
    return {
        e["id"]: len({cells[(e["id"], h["id"])] for h in m["hypotheses"]}) for e in m["evidence"]
    }


def sensitivity(
    m: dict[str, Any], cells: dict[tuple[str, str], str], top: str, second: str
) -> list[str]:
    """Single-cell changes that would strictly put `second` ahead of `top`."""
    flips: list[str] = []
    for e in m["evidence"]:
        for h_id in (top, second):
            key = (e["id"], h_id)
            current = cells[key]
            for alt in RATINGS:
                if alt == current:
                    continue
                trial = dict(cells)
                trial[key] = alt
                s = scores(m, trial)
                if s[second] < s[top]:
                    flips.append(f"{e['id']}x{h_id}: {current}->{alt} puts {second} ahead")
    return flips


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", help="matrix.json")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    m = load(args.file)
    cells = cell_map(m)
    s = scores(m, cells)
    ranking = sorted(s, key=lambda h: s[h])
    diag = diagnosticity(m, cells)
    non_diag = [e for e, d in diag.items() if d == 1]
    tie = len(ranking) > 1 and s[ranking[0]] == s[ranking[1]]
    flips = sensitivity(m, cells, ranking[0], ranking[1]) if len(ranking) > 1 else []

    cluster_map = clusters(m)
    result = {
        "scores": s,
        "ranking": ranking,
        "tied_top": tie,
        "non_diagnostic_evidence": non_diag,
        "rank_flip_cells": flips,
        "origin_clusters": cluster_map,
        "collapsed": [
            f"{', '.join(ids)} → one origin ({name}); credibility counted once, "
            f"not {len(ids)} times"
            for name, ids in cluster_map.items()
        ],
    }
    if args.json:
        print(json.dumps(result, indent=2))
        return

    print(
        "Rule: inconsistency(H) = sum of credibility over I-cells, counted once per "
        "origin; survivor = lowest."
    )
    print(f"\nQuestion: {m['question']}\n\nRanking (least inconsistent first):")
    texts = {h["id"]: h["text"] for h in m["hypotheses"]}
    for i, h in enumerate(ranking, 1):
        print(f"  {i}. {h} (inconsistency {s[h]}): {texts[h]}")
    if tie:
        print("\nTIED TOP — the matrix does not decide; name the evidence that would.")
    if result["collapsed"]:
        print(f"\nOrigins collapsed ({len(cluster_map)}):")
        for line in result["collapsed"]:
            print(f"  {line}")
        print("  Report distinct origins, never document counts.")
    if non_diag:
        print(f"\nNon-diagnostic evidence (same rating everywhere): {', '.join(non_diag)}")
        print("  These support every hypothesis equally — do not cite them for the winner.")
    if flips:
        print(f"\nSensitivity — single cells that would swap ranks 1<->2 ({len(flips)}):")
        for f in flips:
            print(f"  {f}")
        print("  Re-examine exactly these ratings and their evidence credibility first.")
    elif len(ranking) > 1 and not tie:
        print("\nNo single-cell change swaps ranks 1<->2 — the lead is robust at cell level.")


if __name__ == "__main__":
    main()
