"""Score an ACH (analysis of competing hypotheses) matrix.

Input: matrix.json — see the ct-ach SKILL.md for the schema. Every
(evidence x hypothesis) pair must be rated exactly once with C, I, or N.

Rules applied (printed so a reader can check by hand):
  inconsistency(H) = sum of evidence credibility over cells rated I
  ranking: ascending inconsistency — the survivor is the LEAST contradicted
  hypothesis, not the most supported one (Heuer, ch. 8).
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


def scores(m: dict[str, Any], cells: dict[tuple[str, str], str]) -> dict[str, int]:
    cred = {e["id"]: int(e["credibility"]) for e in m["evidence"]}
    return {
        h["id"]: sum(cred[e["id"]] for e in m["evidence"] if cells[(e["id"], h["id"])] == "I")
        for h in m["hypotheses"]
    }


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

    result = {
        "scores": s,
        "ranking": ranking,
        "tied_top": tie,
        "non_diagnostic_evidence": non_diag,
        "rank_flip_cells": flips,
    }
    if args.json:
        print(json.dumps(result, indent=2))
        return

    print("Rule: inconsistency(H) = sum of credibility over I-cells; survivor = lowest.")
    print(f"\nQuestion: {m['question']}\n\nRanking (least inconsistent first):")
    texts = {h["id"]: h["text"] for h in m["hypotheses"]}
    for i, h in enumerate(ranking, 1):
        print(f"  {i}. {h} (inconsistency {s[h]}): {texts[h]}")
    if tie:
        print("\nTIED TOP — the matrix does not decide; name the evidence that would.")
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
