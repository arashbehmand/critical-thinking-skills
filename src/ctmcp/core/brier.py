"""Brier scoring and calibration bins for probability predictions (Brier 1950).

Brier = mean((p − outcome)²); 0 is perfect, 0.25 is a coin flip at p = 0.5.
Bins compare stated probability to observed frequency — the calibration
finding ("at 80–90% stated, it happened 56% of the time").

Pure: the caller passes the entries and `today` explicitly; nothing is read,
written, or resolved here. Entry shape (a superset is fine):
{id, p ∈ [0,1], resolve_by: ISO date, outcome: None | 0 | 1}.
"""

from typing import Any

BINS = ((0.0, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.01))


def report(entries: list[dict[str, Any]], today: str) -> dict[str, Any]:
    """Score resolved predictions and surface pending/overdue ones."""
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
    }
    if not resolved:
        return result

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
