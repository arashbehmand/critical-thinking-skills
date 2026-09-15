"""Bundled skill-script CLI behavior beyond the core parity tests.

`commitlog.py impact` has a core mirror pinned in `tests/test_parity.py`; its append-only
I/O and human reports do not. `origins.py` remains standalone bookkeeping. Both are driven
here through their real CLI.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parent.parent
ORIGINS = REPO / "skills/ct-entailment/scripts/origins.py"
COMMITLOG = REPO / "skills/ct-consistency-log/scripts/commitlog.py"


def run(script: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args], capture_output=True, text=True, check=False
    )


def run_json(script: Path, args: list[str]) -> Any:
    result = run(script, args)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> Path:
    path.write_text("".join(json.dumps(r) + "\n" for r in records))
    return path


# --- origins.py -------------------------------------------------------------


def test_origins_collapses_a_syndication_chain(tmp_path: Path) -> None:
    """Three coats, one observation: a reprint, a quoting chain, and the original."""
    records = [
        {
            "id": "en-1",
            "source": "Reuters",
            "url": "https://www.reuters.com/tech/chips-q2?utm_source=x",
            "quote": "Global shipments declined twelve percent in the second quarter.",
        },
        {
            "id": "en-2",
            "source": "The Verge",
            "url": "https://theverge.com/2026/chips",
            "quote": (
                "Reuters reports that global shipments declined twelve percent in the "
                "second quarter, citing preliminary data."
            ),
        },
        {"id": "en-3", "source": "Reuters wire", "url": "http://reuters.com/tech/chips-q2/"},
        {"id": "en-4", "source": "Company 10-Q", "url": "https://sec.gov/filing/10q-4471"},
    ]
    result = run_json(ORIGINS, [str(write_jsonl(tmp_path / "e.jsonl", records)), "--json"])
    assert result["document_count"] == 4
    assert result["distinct_origins"] == 2
    assert result["clusters"] == {"og-1": ["en-1", "en-2", "en-3"], "og-2": ["en-4"]}
    assert {j["rule"] for j in result["joins"]} == {"url", "quote"}


def test_origins_joins_on_identical_entity_sequences(tmp_path: Path) -> None:
    records = [
        {"id": "a", "source": "SIA report", "entities": ["SIA", "fab utilisation", "Q2 2026"]},
        {"id": "b", "source": "analyst note", "entities": ["sia", "Fab Utilisation", "q2 2026"]},
        {"id": "c", "source": "other", "entities": ["SIA"]},
    ]
    result = run_json(ORIGINS, [str(write_jsonl(tmp_path / "e.jsonl", records)), "--json"])
    # 'c' has one entity, below MIN_ENTITIES — a single shared name is not an origin.
    assert result["clusters"] == {"og-1": ["a", "b"], "og-2": ["c"]}


def test_origins_does_not_join_on_a_short_quote(tmp_path: Path) -> None:
    records = [
        {"id": "a", "source": "one", "quote": "shipments fell"},
        {"id": "b", "source": "two", "quote": "shipments fell sharply"},
    ]
    result = run_json(ORIGINS, [str(write_jsonl(tmp_path / "e.jsonl", records)), "--json"])
    assert result["distinct_origins"] == 2


def test_origins_reports_no_collapse_as_a_finding(tmp_path: Path) -> None:
    records = [
        {"id": "a", "source": "one", "url": "https://a.example/x"},
        {"id": "b", "source": "two", "url": "https://b.example/y"},
    ]
    path = write_jsonl(tmp_path / "e.jsonl", records)
    assert run_json(ORIGINS, [str(path), "--json"])["collapsed"] == []
    human = run(ORIGINS, [str(path)])
    assert "2 documents → 2 distinct origins" in human.stdout
    assert "what a check that is not running looks like" in human.stdout


def test_origins_accepts_a_json_array(tmp_path: Path) -> None:
    records = [
        {"id": "a", "source": "one", "url": "https://a.example/x"},
        {"id": "b", "source": "one", "url": "https://a.example/x"},
    ]
    path = tmp_path / "e.json"
    path.write_text(json.dumps(records))
    assert run_json(ORIGINS, [str(path), "--json"])["distinct_origins"] == 1


def test_origins_rejects_duplicate_ids(tmp_path: Path) -> None:
    records = [{"id": "a", "source": "one"}, {"id": "a", "source": "two"}]
    result = run(ORIGINS, [str(write_jsonl(tmp_path / "e.jsonl", records))])
    assert result.returncode != 0
    assert "duplicate record ids" in result.stderr


# --- commitlog.py: dependency edges and retraction propagation ---------------


def add(log: Path, statement: str, **flags: str) -> subprocess.CompletedProcess[str]:
    args = ["add", "--file", str(log), "--statement", statement]
    for key, value in flags.items():
        args += [f"--{key.replace('_', '-')}", value]
    result = run(COMMITLOG, args)
    assert result.returncode == 0, result.stderr
    return result


def chain(log: Path) -> None:
    """c-1 <- c-2 <- c-3, plus an unrelated c-4."""
    add(log, "retry budget is 3 attempts", tags="retries")
    add(log, "dead-letter queue drains hourly", tags="retries,queue", depends_on="c-1")
    add(log, "backfill window is 4h", tags="queue", depends_on="c-2")
    add(log, "metrics use OTLP", tags="telemetry")


def test_retraction_propagates_transitively(tmp_path: Path) -> None:
    log = tmp_path / "c.jsonl"
    chain(log)
    result = add(log, "retry budget is 5 attempts (load test)", tags="retries", supersedes="c-1")
    # c-2 rests on c-1 directly; c-3 rests on it through c-2.
    assert "now OUT" in result.stdout
    assert "c-2, c-3" in result.stdout

    listing = run(COMMITLOG, ["list", "--file", str(log), "--all"])
    assert "c-1 [retries] [SUPERSEDED]" in listing.stdout
    assert "c-2 [retries,queue] [OUT]" in listing.stdout
    assert "c-3 [queue] [OUT]" in listing.stdout
    assert "(2 active, 1 superseded, 2 out)" in listing.stdout


def test_check_names_the_withdrawn_premise_and_exits_nonzero(tmp_path: Path) -> None:
    log = tmp_path / "c.jsonl"
    chain(log)
    add(log, "retry budget is 5 attempts", tags="retries", supersedes="c-1")
    result = run(COMMITLOG, ["check", "--file", str(log)])
    assert result.returncode == 1, "an unresolved OUT entry must block the deliverable"
    assert "OUT (2)" in result.stdout
    assert "rests on: c-1" in result.stdout
    assert "model-authored" in result.stdout


def test_check_is_clean_before_any_retraction(tmp_path: Path) -> None:
    log = tmp_path / "c.jsonl"
    chain(log)
    result = run(COMMITLOG, ["check", "--file", str(log)])
    assert result.returncode == 0
    assert "every live claim rests on live premises" in result.stdout


def test_check_reports_shared_premises(tmp_path: Path) -> None:
    log = tmp_path / "c.jsonl"
    add(log, "the export is idempotent", tags="export")
    for n in range(3):
        add(log, f"step {n} can be retried safely", tags="export", depends_on="c-1")
    result = run(COMMITLOG, ["check", "--file", str(log)])
    assert "3 claims rest on c-1" in result.stdout
    assert "One retraction takes all of them" in result.stdout


def test_check_reports_circular_support(tmp_path: Path) -> None:
    log = tmp_path / "c.jsonl"
    add(log, "A holds", tags="x")
    add(log, "B holds because A does", tags="x", depends_on="c-1")
    # Hand-write the back-edge: `add` refuses forward references, and a cycle can only
    # arise from an edited log — which is exactly why `check` looks for one.
    entries = [json.loads(line) for line in log.read_text().splitlines()]
    entries[0]["depends_on"] = ["c-2"]
    log.write_text("".join(json.dumps(e) + "\n" for e in entries))
    result = run(COMMITLOG, ["check", "--file", str(log)])
    assert "CIRCULAR SUPPORT" in result.stdout


def test_check_flags_a_log_with_no_edges_at_all(tmp_path: Path) -> None:
    log = tmp_path / "c.jsonl"
    for n in range(4):
        add(log, f"decision {n}", tags="x")
    result = run(COMMITLOG, ["check", "--file", str(log)])
    assert "transcript summary, not a dependency record" in result.stdout


def test_pairs_excludes_out_entries_and_says_so(tmp_path: Path) -> None:
    log = tmp_path / "c.jsonl"
    chain(log)
    add(log, "retry budget is 5 attempts", tags="retries", supersedes="c-1")
    result = run(COMMITLOG, ["pairs", "--file", str(log)])
    assert "2 OUT entries excluded" in result.stdout
    assert "dead-letter queue drains hourly" not in result.stdout


def test_add_rejects_an_unknown_dependency(tmp_path: Path) -> None:
    log = tmp_path / "c.jsonl"
    add(log, "first", tags="x")
    result = run(COMMITLOG, ["add", "--file", str(log), "--statement", "b", "--depends-on", "c-9"])
    assert result.returncode != 0
    assert "no such entry" in result.stderr


def test_entry_depending_on_a_missing_id_is_out(tmp_path: Path) -> None:
    """Conservative by design: an unresolvable premise is not a live one."""
    log = tmp_path / "c.jsonl"
    add(log, "first", tags="x")
    entries = [json.loads(line) for line in log.read_text().splitlines()]
    entries[0]["depends_on"] = ["c-99"]
    log.write_text("".join(json.dumps(e) + "\n" for e in entries))
    result = run(COMMITLOG, ["check", "--file", str(log)])
    assert result.returncode == 1
    assert "c-99 (no such entry)" in result.stdout


def test_impact_ranks_transitive_recorded_blast_radius(tmp_path: Path) -> None:
    log = tmp_path / "c.jsonl"
    chain(log)
    result = run(COMMITLOG, ["impact", "--file", str(log), "--targets", "c-3"])
    assert result.returncode == 0
    assert "c-1: 2 affected — c-2, c-3" in result.stdout
    assert "c-2: 1 affected — c-3" in result.stdout
    assert "Recorded dependencies carrying c-3: c-1, c-2" in result.stdout
    assert "exact about the record" in result.stdout


def test_impact_refuses_a_nonactive_target(tmp_path: Path) -> None:
    log = tmp_path / "c.jsonl"
    chain(log)
    add(log, "retry budget is 5 attempts", tags="retries", supersedes="c-1")
    result = run(COMMITLOG, ["impact", "--file", str(log), "--targets", "c-3"])
    assert result.returncode != 0
    assert "target entry is not active" in result.stderr


# --- bag.py (ct-ensemble) ---------------------------------------------------

BAG = REPO / "skills/ct-ensemble/scripts/bag.py"


def evidence_file(path: Path, n: int = 10) -> Path:
    items = [
        {"id": f"E{i}", "text": f"metric {i} reads high", "source": "telemetry"}
        for i in range(1, n + 1)
    ]
    path.write_text(json.dumps({"evidence": items}))
    return path


def test_draw_is_deterministic_for_a_seed(tmp_path: Path) -> None:
    src = str(evidence_file(tmp_path / "e.json"))
    args = ["draw", "--evidence", src, "--n", "5", "--seed", "3", "--json"]
    assert run_json(BAG, args) == run_json(BAG, args)


def test_draw_varies_with_the_seed(tmp_path: Path) -> None:
    src = str(evidence_file(tmp_path / "e.json"))
    a = run_json(BAG, ["draw", "--evidence", src, "--n", "5", "--seed", "3", "--json"])
    b = run_json(BAG, ["draw", "--evidence", src, "--n", "5", "--seed", "4", "--json"])
    assert a["subsets"] != b["subsets"]


def test_every_item_is_both_included_and_left_out(tmp_path: Path) -> None:
    """Without this no item gets an influence score — there is nothing to compare."""
    src = str(evidence_file(tmp_path / "e.json", 12))
    drawn = run_json(BAG, ["draw", "--evidence", src, "--n", "7", "--seed", "1", "--json"])
    subsets = [set(s["evidence_ids"]) for s in drawn["subsets"]]
    for item in (f"E{i}" for i in range(1, 13)):
        assert any(item in s for s in subsets), f"{item} never included"
        assert any(item not in s for s in subsets), f"{item} never left out"


def test_draw_refuses_a_rate_that_keeps_everything(tmp_path: Path) -> None:
    src = str(evidence_file(tmp_path / "e.json"))
    result = run(BAG, ["draw", "--evidence", src, "--rate", "1.0"])
    assert result.returncode != 0
    assert "nothing would vary" in result.stderr


def test_influence_is_hand_computed(tmp_path: Path) -> None:
    """E1 is in S1+S2 (both H2) and out of S3 (H9): +1.0. E9 is in none, so absent."""
    draws = tmp_path / "d.json"
    draws.write_text(
        json.dumps(
            {
                "subsets": [
                    {"id": "S1", "evidence_ids": ["E1", "E2"]},
                    {"id": "S2", "evidence_ids": ["E1", "E3"]},
                    {"id": "S3", "evidence_ids": ["E2", "E3"]},
                ]
            }
        )
    )
    verdicts = tmp_path / "v.json"
    verdicts.write_text(
        json.dumps(
            [
                {"subset_id": "S1", "verdict": "H2"},
                {"subset_id": "S2", "verdict": "H2"},
                {"subset_id": "S3", "verdict": "H9"},
            ]
        )
    )
    out = run_json(BAG, ["aggregate", "--draws", str(draws), "--verdicts", str(verdicts), "--json"])
    assert out["winner"] == "H2"
    assert out["share"] == pytest.approx(2 / 3, abs=1e-3)
    rows = {r["evidence_id"]: r for r in out["influence"]}
    assert rows["E1"]["influence"] == 1.0  # in both winners, out of the dissenter
    assert rows["E2"]["influence"] == pytest.approx(-0.5)  # in S1(H2) + S3(H9), out of S2(H2)
    assert out["load_bearing"] == ["E1", "E2", "E3"]


def test_aggregate_flags_a_tie(tmp_path: Path) -> None:
    draws = tmp_path / "d.json"
    draws.write_text(
        json.dumps(
            {"subsets": [{"id": f"S{i}", "evidence_ids": ["E1", "E2"]} for i in (1, 2, 3, 4)]}
        )
    )
    verdicts = tmp_path / "v.json"
    verdicts.write_text(
        json.dumps(
            [
                {"subset_id": "S1", "verdict": "H1"},
                {"subset_id": "S2", "verdict": "H1"},
                {"subset_id": "S3", "verdict": "H2"},
                {"subset_id": "S4", "verdict": "H2"},
            ]
        )
    )
    out = run_json(BAG, ["aggregate", "--draws", str(draws), "--verdicts", str(verdicts), "--json"])
    assert out["tie"] is True
    assert out["winner"] is None
    assert out["disagreement"] is True


def test_aggregate_needs_at_least_three_perspectives(tmp_path: Path) -> None:
    draws = tmp_path / "d.json"
    draws.write_text(json.dumps({"subsets": [{"id": "S1", "evidence_ids": ["E1"]}]}))
    verdicts = tmp_path / "v.json"
    verdicts.write_text(json.dumps([{"subset_id": "S1", "verdict": "H1"}]))
    result = run(BAG, ["aggregate", "--draws", str(draws), "--verdicts", str(verdicts)])
    assert result.returncode != 0
    assert "at least 3" in result.stderr
