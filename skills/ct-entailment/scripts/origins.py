#!/usr/bin/env python3
"""Cluster sources by origin, so corroboration is counted in origins and not documents.

Four documents that all trace to one press release are one observation wearing four
coats. Counting them as four is the commonest way a research answer manufactures
confidence it has not earned — and it is invisible in the output, because four citations
look better than one either way.

Input: JSONL (or a JSON array) of records
    {id, claim?, source, url?, quote?, entities?}

Two records are joined when any of these hold, and the rule that fired is reported:

    url      normalised host+path match (scheme, www., query, fragment, trailing
             slash and AMP suffixes stripped) — syndication and reprints
    quote    one record's normalised quote contains the other's, at MIN_QUOTE_WORDS
             or more — quoting chains
    entity   identical ordered entity sequences of length >= MIN_ENTITIES — the same
             extraction restated
    source   normalised source labels match — the same outlet or document

Output: the partition, the distinct-origin count, and the document count. Report
distinct origins, never document counts.

The judgment this script does NOT make is whether a source *entails* the claim; that
is a separate narrow question for a fresh context (template T9). This is bookkeeping.
Stdlib only, no network, no LLM calls.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

MIN_QUOTE_WORDS = 6
MIN_ENTITIES = 2

_WS = re.compile(r"\s+")
_TRIM = re.compile(r"^[\W_]+|[\W_]+$")
_AMP = re.compile(r"(\.amp|/amp)$")


def normalise_url(url: str) -> str:
    """Host + path, lowercased, with the usual syndication decorations removed."""
    text = url.strip().lower()
    text = re.sub(r"^[a-z]+://", "", text)
    text = text.split("?", 1)[0].split("#", 1)[0]
    text = text.removeprefix("www.").rstrip("/")
    return _AMP.sub("", text)


def normalise_text(text: str) -> str:
    return _TRIM.sub("", _WS.sub(" ", text.strip().lower()))


def normalise_entities(entities: Any) -> tuple[str, ...]:
    if not isinstance(entities, list):
        return ()
    return tuple(normalise_text(str(e)) for e in entities)


class _Union:
    """Union-find over record ids, remembering why each join happened."""

    def __init__(self, ids: list[str]) -> None:
        self.parent = {i: i for i in ids}
        self.joins: list[dict[str, str]] = []

    def find(self, item: str) -> str:
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def join(self, a: str, b: str, rule: str, detail: str) -> None:
        root_a, root_b = self.find(a), self.find(b)
        if root_a == root_b:
            return
        self.parent[root_b] = root_a
        self.joins.append({"a": a, "b": b, "rule": rule, "detail": detail})


def cluster(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Partition records into origin clusters. Deterministic in input order."""
    ids = [str(r["id"]) for r in records]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate record ids")
    union = _Union(ids)

    for key, normalise in (("url", normalise_url), ("source", normalise_text)):
        seen: dict[str, str] = {}
        for record in records:
            raw = str(record.get(key) or "").strip()
            if not raw:
                continue
            token = normalise(raw)
            if not token:
                continue
            if token in seen:
                union.join(seen[token], str(record["id"]), key, token)
            else:
                seen[token] = str(record["id"])

    quotes = [(str(r["id"]), normalise_text(str(r.get("quote") or ""))) for r in records]
    quotes = [(i, q) for i, q in quotes if len(q.split()) >= MIN_QUOTE_WORDS]
    for n, (id_a, quote_a) in enumerate(quotes):
        for id_b, quote_b in quotes[n + 1 :]:
            if quote_a in quote_b or quote_b in quote_a:
                shorter = quote_a if len(quote_a) <= len(quote_b) else quote_b
                union.join(id_a, id_b, "quote", shorter)

    by_entities: dict[tuple[str, ...], str] = {}
    for record in records:
        entities = normalise_entities(record.get("entities"))
        if len(entities) < MIN_ENTITIES:
            continue
        if entities in by_entities:
            union.join(by_entities[entities], str(record["id"]), "entity", " | ".join(entities))
        else:
            by_entities[entities] = str(record["id"])

    groups: dict[str, list[str]] = {}
    for record_id in ids:
        groups.setdefault(union.find(record_id), []).append(record_id)

    clusters = {f"og-{n + 1}": members for n, (_, members) in enumerate(sorted(groups.items()))}
    return {
        "document_count": len(ids),
        "distinct_origins": len(clusters),
        "clusters": clusters,
        "collapsed": [
            f"{', '.join(members)} → one origin ({name})"
            for name, members in clusters.items()
            if len(members) > 1
        ],
        "joins": union.joins,
    }


def load(path: str) -> list[dict[str, Any]]:
    """Accept a JSON array or one JSON object per line."""
    text = Path(path).read_text().strip()
    if not text:
        sys.exit(f"{path}: empty")
    if text.lstrip().startswith("["):
        parsed = json.loads(text)
        if not isinstance(parsed, list):
            sys.exit(f"{path}: top-level JSON must be an array of records")
        return [dict(r) for r in parsed]
    records = []
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(dict(json.loads(line)))
        except json.JSONDecodeError as err:
            sys.exit(f"{path}:{n}: bad JSON ({err})")
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", help="JSONL or JSON array of {id, source, url?, quote?, entities?}")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    records = load(args.file)
    if not records:
        sys.exit("no records")
    try:
        result = cluster(records)
    except ValueError as err:
        sys.exit(str(err))

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print(
        "Rule: join on normalised url host+path, containing quotes "
        f"(>= {MIN_QUOTE_WORDS} words), identical entity sequences "
        f"(>= {MIN_ENTITIES}), or identical source labels."
    )
    print(
        f"\n{result['document_count']} documents → {result['distinct_origins']} distinct origins\n"
    )
    for name, members in result["clusters"].items():
        print(f"  {name}: {', '.join(members)}")
    if result["joins"]:
        print("\nWhy each join fired:")
        for join in result["joins"]:
            print(f"  {join['a']} + {join['b']} — {join['rule']}: {join['detail']}")
    if result["distinct_origins"] == result["document_count"]:
        print(
            "\nNo collapse. That is a legitimate finding — and it is also what a "
            "check that is not running looks like. Confirm the records carry url, "
            "quote, or entities before reporting independence."
        )
    else:
        print("\nCite distinct origins, not document counts.")


if __name__ == "__main__":
    main()
