"""Exact-value tests pin the math — hand-computed, per the whitepaper's doctrine."""

from typing import Any

import pytest

from ctmcp.core import ach, brier, dependencies, fermi, panel, qbaf

# --- qbaf: DF-QuAD ----------------------------------------------------------


def arg(
    arg_id: str, tau: float, parent: str | None = None, stance: str | None = None
) -> qbaf.Argument:
    return qbaf.Argument(id=arg_id, base_score=tau, parent_id=parent, stance=stance)


def test_qbaf_bare_root_keeps_tau() -> None:
    result = qbaf.evaluate([arg("claim", 0.7)])
    assert result["root_strength"] == 0.7
    assert result["verdict"] is True


def test_qbaf_exactly_half_is_false() -> None:
    assert qbaf.evaluate([arg("claim", 0.5)])["verdict"] is False


def test_qbaf_attacker_and_supporter_hand_computed() -> None:
    # s_att = 0.8, s_supp = 0.4 → σ = 0.5 − 0.5·(0.8 − 0.4) = 0.3
    result = qbaf.evaluate(
        [arg("claim", 0.5), arg("A1", 0.8, "claim", "con"), arg("S1", 0.4, "claim", "pro")]
    )
    assert result["root_strength"] == pytest.approx(0.3)
    assert result["strengths"]["A1"] == 0.8
    assert result["verdict"] is False


def test_qbaf_grandchild_weakens_attacker() -> None:
    # σ(A1) = 0.8 − 0.8·0.5 = 0.4; σ(claim) = 0.5 − 0.5·0.4 = 0.3
    result = qbaf.evaluate(
        [arg("claim", 0.5), arg("A1", 0.8, "claim", "con"), arg("A1.A1", 0.5, "A1", "con")]
    )
    assert result["strengths"]["A1"] == pytest.approx(0.4)
    assert result["root_strength"] == pytest.approx(0.3)


def test_qbaf_two_supporters_product_aggregation() -> None:
    # s_supp = 1 − (1−0.5)(1−0.5) = 0.75 → σ = 0.4 + 0.6·0.75 = 0.85
    result = qbaf.evaluate(
        [arg("claim", 0.4), arg("S1", 0.5, "claim", "pro"), arg("S2", 0.5, "claim", "pro")]
    )
    assert result["root_strength"] == pytest.approx(0.85)
    assert result["verdict"] is True


def test_qbaf_rejects_two_roots() -> None:
    with pytest.raises(ValueError, match="exactly one root"):
        qbaf.evaluate([arg("a", 0.5), arg("b", 0.5)])


def test_qbaf_rejects_unknown_parent() -> None:
    with pytest.raises(ValueError, match="unknown parent"):
        qbaf.evaluate([arg("claim", 0.5), arg("x", 0.5, "ghost", "pro")])


def test_qbaf_rejects_disconnected_cycle() -> None:
    with pytest.raises(ValueError, match="not connected"):
        qbaf.evaluate([arg("claim", 0.5), arg("a", 0.5, "b", "pro"), arg("b", 0.5, "a", "con")])


def test_qbaf_rejects_out_of_range_tau() -> None:
    with pytest.raises(ValueError, match="base_score"):
        qbaf.evaluate([arg("claim", 1.5)])


def test_qbaf_rejects_missing_stance() -> None:
    with pytest.raises(ValueError, match="stance"):
        qbaf.evaluate([arg("claim", 0.5), arg("x", 0.5, "claim", None)])


# --- ach --------------------------------------------------------------------

TOY_MATRIX: dict[str, Any] = {
    "question": "what explains the p99 latency spike at 14:02?",
    "hypotheses": [
        {"id": "H1", "text": "deploy 4812 regression"},
        {"id": "H2", "text": "traffic surge"},
        {"id": "H3", "text": "db index gone stale"},
    ],
    "evidence": [
        {"id": "E1", "text": "spike 2 min after deploy", "source": "grafana", "credibility": 3},
        {"id": "E2", "text": "request rate flat", "source": "grafana", "credibility": 3},
        {"id": "E3", "text": "slow-query log clean", "source": "db logs", "credibility": 2},
        {"id": "E4", "text": "rollback restored p99", "source": "grafana", "credibility": 3},
    ],
    "ratings": [
        {"evidence_id": "E1", "hypothesis_id": "H1", "rating": "C"},
        {"evidence_id": "E1", "hypothesis_id": "H2", "rating": "N"},
        {"evidence_id": "E1", "hypothesis_id": "H3", "rating": "N"},
        {"evidence_id": "E2", "hypothesis_id": "H1", "rating": "N"},
        {"evidence_id": "E2", "hypothesis_id": "H2", "rating": "I"},
        {"evidence_id": "E2", "hypothesis_id": "H3", "rating": "N"},
        {"evidence_id": "E3", "hypothesis_id": "H1", "rating": "N"},
        {"evidence_id": "E3", "hypothesis_id": "H2", "rating": "N"},
        {"evidence_id": "E3", "hypothesis_id": "H3", "rating": "I"},
        {"evidence_id": "E4", "hypothesis_id": "H1", "rating": "C"},
        {"evidence_id": "E4", "hypothesis_id": "H2", "rating": "I"},
        {"evidence_id": "E4", "hypothesis_id": "H3", "rating": "I"},
    ],
}


def test_ach_toy_matches_hand_computation() -> None:
    result = ach.score(TOY_MATRIX)
    assert result["scores"] == {"H1": 0, "H2": 6, "H3": 5}
    assert result["ranking"] == ["H1", "H3", "H2"]
    assert result["tied_top"] is False
    assert result["non_diagnostic_evidence"] == []
    assert result["rank_flip_cells"] == []  # gap 5 > max single-cell swing 3
    # No `origin` anywhere: every item is its own origin, so nothing collapses and
    # the scores are what they were before origins existed.
    assert result["origin_clusters"] == {}
    assert result["collapsed"] == []


def echo_matrix() -> dict[str, Any]:
    """One measurement against H1; one observation about H2, restated three times."""
    return {
        "question": "q",
        "hypotheses": [{"id": "H1", "text": "one"}, {"id": "H2", "text": "two"}],
        "evidence": [
            {"id": "E1", "text": "meter reading", "credibility": 3},
            {"id": "E2", "text": "shift log", "credibility": 2, "origin": "og-1"},
            {"id": "E3", "text": "summary of the shift log", "credibility": 2, "origin": "og-1"},
            {"id": "E4", "text": "ticket citing the summary", "credibility": 1, "origin": "og-1"},
        ],
        "ratings": [
            {"evidence_id": "E1", "hypothesis_id": "H1", "rating": "I"},
            {"evidence_id": "E1", "hypothesis_id": "H2", "rating": "N"},
            {"evidence_id": "E2", "hypothesis_id": "H1", "rating": "N"},
            {"evidence_id": "E2", "hypothesis_id": "H2", "rating": "I"},
            {"evidence_id": "E3", "hypothesis_id": "H1", "rating": "N"},
            {"evidence_id": "E3", "hypothesis_id": "H2", "rating": "I"},
            {"evidence_id": "E4", "hypothesis_id": "H1", "rating": "N"},
            {"evidence_id": "E4", "hypothesis_id": "H2", "rating": "I"},
        ],
    }


def test_ach_counts_an_origin_once() -> None:
    # H1 = 3 (E1, cred 3). H2's three items share og-1 → max(2, 2, 1) = 2, not 2+2+1 = 5.
    # Uncollapsed, H2 would score 5 and lose; collapsed it scores 2 and survives.
    result = ach.score(echo_matrix())
    assert result["scores"] == {"H1": 3, "H2": 2}
    assert result["ranking"] == ["H2", "H1"]
    assert result["origin_clusters"] == {"og-1": ["E2", "E3", "E4"]}
    assert result["collapsed"] == [
        "E2, E3, E4 → one origin (og-1); credibility counted once, not 3 times"
    ]


def test_ach_flip_cells_respect_origin_collapse() -> None:
    """No echo is load-bearing: a sibling still carries og-1 whichever one you change.

    Every flip is an E1 cell — the one item with an origin of its own. Changing any
    of E2/E3/E4 leaves og-1 contributing max(remaining I-rated members) = 2 to H2, so
    the ranking does not move, which is the honest answer: that cell never decided it.
    """
    flips = ach.score(echo_matrix())["rank_flip_cells"]
    assert flips == [
        "E1xH2: N->I puts H1 ahead",  # E1 is its own origin, so its 3 lands in full
        "E1xH1: I->C puts H1 ahead",
        "E1xH1: I->N puts H1 ahead",
    ]


def test_ach_empty_origin_string_means_stands_alone() -> None:
    m = echo_matrix()
    for e in m["evidence"]:
        e["origin"] = ""
    assert ach.score(m)["scores"] == {"H1": 3, "H2": 5}  # 2 + 2 + 1, counted separately


def small_matrix() -> dict[str, Any]:
    # H1 = 3 (E1 I, cred 3); H2 = 1 (E2 I, cred 1) → ranking [H2, H1]
    return {
        "question": "q",
        "hypotheses": [{"id": "H1", "text": "one"}, {"id": "H2", "text": "two"}],
        "evidence": [
            {"id": "E1", "text": "e1", "credibility": 3},
            {"id": "E2", "text": "e2", "credibility": 1},
        ],
        "ratings": [
            {"evidence_id": "E1", "hypothesis_id": "H1", "rating": "I"},
            {"evidence_id": "E1", "hypothesis_id": "H2", "rating": "C"},
            {"evidence_id": "E2", "hypothesis_id": "H1", "rating": "C"},
            {"evidence_id": "E2", "hypothesis_id": "H2", "rating": "I"},
        ],
    }


def test_ach_flip_cells_hand_computed() -> None:
    result = ach.score(small_matrix())
    assert result["ranking"] == ["H2", "H1"]
    assert result["rank_flip_cells"] == [
        "E1xH2: C->I puts H1 ahead",
        "E1xH1: I->C puts H1 ahead",
        "E1xH1: I->N puts H1 ahead",
    ]


def test_ach_tie_reported() -> None:
    m = small_matrix()
    m["evidence"][0]["credibility"] = 1  # H1 = 1 = H2
    assert ach.score(m)["tied_top"] is True


def test_ach_incomplete_matrix_rejected() -> None:
    m = small_matrix()
    m["ratings"].pop()
    with pytest.raises(ValueError, match="unrated"):
        ach.score(m)


# --- panel ------------------------------------------------------------------


def panel_draws() -> list[dict[str, Any]]:
    """values [6, 7, 4, 7, 5]; sorted [4, 5, 6, 7, 7], so the median 6 is draw 1."""
    return [
        {"value": 6, "source": "opus", "pedigree": "elicited"},
        {"value": 7, "source": "opus", "pedigree": "elicited"},
        {"value": 4, "source": "sonnet", "pedigree": "elicited"},
        {"value": 7, "source": "opus", "pedigree": "elicited"},
        {"value": 5, "source": "human", "pedigree": "given"},
    ]


VOTE_DRAWS: list[dict[str, Any]] = [
    {"choice": "A", "source": "opus"},
    {"choice": "B", "source": "opus"},
    {"choice": "A", "source": "sonnet"},
    {"choice": "A", "source": "opus"},
    {"choice": "C", "source": "human"},
]


def test_panel_numeric_hand_values() -> None:
    result = panel.numeric(panel_draws())
    assert result["median"] == 6
    assert result["mean"] == pytest.approx(5.8)
    assert result["range"] == 3
    assert result["disagreement"] is False  # 3 > 3 is false: strict inequality


def test_panel_numeric_flags_wide_spread() -> None:
    draws = [{"value": v, "source": "opus", "pedigree": "elicited"} for v in (2, 9, 3)]
    assert panel.numeric(draws)["disagreement"] is True


def test_panel_reports_who_supplied_the_draws() -> None:
    result = panel.numeric(panel_draws())
    assert result["composition"] == {"opus": 3, "sonnet": 1, "human": 1}
    assert result["distinct_sources"] == 3
    assert result["shared_source"] is False
    assert result["pedigree"] == {"given": 1, "elicited": 4}


def test_panel_of_one_model_says_it_cancels_noise_only() -> None:
    """Five draws from one model must not print like five independent sources."""
    draws = [{"value": v, "source": "opus", "pedigree": "elicited"} for v in (6, 7, 4, 7, 5)]
    result = panel.numeric(draws)
    assert result["shared_source"] is True
    assert "cancels noise, not shared bias" in result["stamp"]


def test_panel_refuses_an_invented_draw_at_the_median() -> None:
    draws = panel_draws()
    draws[0]["pedigree"] = "invented"  # value 6 — the median of [4, 5, 6, 7, 7]
    with pytest.raises(ValueError, match="refusing to compute"):
        panel.numeric(draws)


def test_panel_computes_an_invented_draw_away_from_the_median() -> None:
    """The median is the instrument that neutralises a wild draw; refusing there is theatre."""
    draws = panel_draws()
    draws[2]["pedigree"] = "invented"  # value 4 — the minimum, not the median
    result = panel.numeric(draws)
    assert result["median"] == 6
    assert "1 invented draw away from the median" in result["stamp"]
    assert "inside the reported range" in result["stamp"]


def test_panel_needs_a_named_source() -> None:
    draws = panel_draws()
    draws[1]["source"] = "  "
    with pytest.raises(ValueError, match="source is required"):
        panel.numeric(draws)


def test_panel_needs_a_pedigree() -> None:
    draws = panel_draws()
    del draws[1]["pedigree"]
    with pytest.raises(ValueError, match="pedigree is required"):
        panel.numeric(draws)


def test_panel_vote_plurality() -> None:
    result = panel.vote(VOTE_DRAWS)
    assert result["winner"] == "A"
    assert result["share"] == 0.6
    assert result["disagreement"] is False  # 0.6 < 0.6 is false: strict inequality
    assert result["composition"] == {"opus": 3, "sonnet": 1, "human": 1}


def test_panel_vote_tie() -> None:
    result = panel.vote([{"choice": "A", "source": "opus"}, {"choice": "B", "source": "sonnet"}])
    assert result["tie"] is True
    assert result["winner"] is None
    assert result["disagreement"] is True


def test_panel_needs_two() -> None:
    with pytest.raises(ValueError, match="at least 2"):
        panel.numeric([{"value": 5.0, "source": "opus", "pedigree": "elicited"}])


# --- brier ------------------------------------------------------------------

LEDGER: list[dict[str, Any]] = [
    {
        "id": "p-1",
        "date": "2026-06-01",
        "q": "CI stays green for 30 days",
        "p": 0.8,
        "resolve_by": "2026-07-01",
        "outcome": 1,
        "resolved_date": "2026-07-01",
        "resolved_by": "ci",
    },
    {
        "id": "p-2",
        "date": "2026-06-02",
        "q": "the migration lands this sprint",
        "p": 0.6,
        "resolve_by": "2026-09-01",
        "outcome": None,
    },
    {
        "id": "p-3",
        "date": "2026-06-03",
        "q": "the retry fix closes #88",
        "p": 0.3,
        "resolve_by": "2026-01-01",
        "outcome": None,
    },
    {
        "id": "p-4",
        "date": "2026-06-04",
        "q": "p99 stays under 200ms",
        "p": 0.9,
        "resolve_by": "2026-07-10",
        "outcome": 0,
        "resolved_date": "2026-07-10",
        "resolved_by": "self",
    },
    {  # resolved before the field existed — reported as unrecorded, never assumed
        "id": "p-5",
        "date": "2026-06-05",
        "q": "no rollback needed",
        "p": 0.7,
        "resolve_by": "2026-07-15",
        "outcome": 1,
        "resolved_date": "2026-07-15",
    },
]


def test_brier_hand_computed() -> None:
    entries: list[dict[str, Any]] = [
        {"id": "p-1", "p": 0.8, "resolve_by": "2026-07-01", "outcome": 1},
        {"id": "p-2", "p": 0.6, "resolve_by": "2026-09-01", "outcome": None},
        {"id": "p-3", "p": 0.3, "resolve_by": "2026-01-01", "outcome": None},
    ]
    result = brier.report(entries, today="2026-07-27")
    assert result["brier"] == pytest.approx(0.04)  # (0.8 − 1)²
    assert result["n_pending"] == 2
    assert result["overdue_ids"] == ["p-3"]
    assert result["bins"] == [{"lo": 0.8, "hi": 0.9, "n": 1, "stated_mean": 0.8, "hit_rate": 1.0}]


def test_brier_ledger_hand_computed() -> None:
    result = brier.report(LEDGER, today="2026-07-27")
    # resolved: p-1 (0.8, 1), p-4 (0.9, 0), p-5 (0.7, 1) → (0.04 + 0.81 + 0.09) / 3
    assert result["brier"] == pytest.approx(0.94 / 3)
    assert result["mean_p"] == pytest.approx(0.8)
    assert result["hit_rate"] == pytest.approx(2 / 3)
    assert result["overdue_ids"] == ["p-3"]


def test_brier_breaks_the_score_out_by_resolver() -> None:
    """A ledger the predictor graded themselves has to say so on its own face."""
    result = brier.report(LEDGER, today="2026-07-27")
    assert result["by_resolver"] == [
        {"resolver": "ci", "n": 1, "brier": pytest.approx(0.04)},
        {"resolver": "self", "n": 1, "brier": pytest.approx(0.81)},
        {"resolver": "unrecorded", "n": 1, "brier": pytest.approx(0.09)},
    ]
    assert result["n_self_resolved"] == 1


def test_brier_no_resolved_entries() -> None:
    result = brier.report(
        [{"id": "p-1", "p": 0.5, "resolve_by": "2099-01-01", "outcome": None}], today="2026-07-27"
    )
    assert result["brier"] is None
    assert result["bins"] == []
    assert result["by_resolver"] == []
    assert result["n_self_resolved"] == 0


def test_brier_rejects_bad_outcome() -> None:
    with pytest.raises(ValueError, match="outcome"):
        brier.report(
            [{"id": "x", "p": 0.5, "resolve_by": "2026-01-01", "outcome": 2}], "2026-07-27"
        )


# --- fermi ------------------------------------------------------------------

PIANO_FACTORS: list[dict[str, Any]] = [
    {"name": "US households", "low": 1.2e8, "high": 1.4e8, "pedigree": "sourced"},
    {
        "name": "share owning pianos",
        "low": 0.03,
        "high": 0.08,
        "op": "multiply",
        "pedigree": "elicited",
    },
    {
        "name": "tunings per piano per year",
        "low": 0.3,
        "high": 1.0,
        "op": "multiply",
        "pedigree": "elicited",
    },
    {
        "name": "tunings per tuner per year",
        "low": 600,
        "high": 1200,
        "op": "divide",
        "pedigree": "sourced",
    },
]


def test_fermi_piano_tuners() -> None:
    result = fermi.combine(PIANO_FACTORS)
    assert result["low"] == pytest.approx(900.0)  # 1.2e8·0.03·0.3/1200
    assert result["high"] == pytest.approx(1.4e8 * 0.08 * 1.0 / 600)
    assert result["widest_factor"] == "tunings per piano per year"


def test_fermi_load_bearing_is_uncertainty_not_magnitude() -> None:
    """log-spans .0669 / .4260 / .5229 / .3010, mean .3292 — the two guesses clear it."""
    assert fermi.combine(PIANO_FACTORS)["load_bearing"] == [
        "share owning pianos",
        "tunings per piano per year",
    ]


def test_fermi_refuses_an_invented_load_bearing_factor() -> None:
    factors = [dict(f) for f in PIANO_FACTORS]
    factors[2]["pedigree"] = "invented"  # tunings per piano — the widest factor
    with pytest.raises(ValueError, match="refusing to compute"):
        fermi.combine(factors)


def test_fermi_computes_an_invented_factor_that_carries_little_uncertainty() -> None:
    factors = [dict(f) for f in PIANO_FACTORS]
    factors[0]["pedigree"] = "invented"  # household count: log-span .0669, well under the bar
    result = fermi.combine(factors)
    assert result["pedigree"] == {"sourced": 1, "elicited": 2, "invented": 1}


def test_fermi_refuses_an_invented_point_estimate() -> None:
    """A point range asserts a precision nobody sourced, however narrow the span."""
    with pytest.raises(ValueError, match="asserting a precision nobody sourced"):
        fermi.combine(
            [
                {"name": "wide", "low": 1.0, "high": 100.0, "pedigree": "sourced"},
                {"name": "exact", "low": 8e9, "high": 8e9, "pedigree": "invented"},
            ]
        )


def test_fermi_divide_interval() -> None:
    result = fermi.combine(
        [
            {"name": "a", "low": 10, "high": 20, "pedigree": "given"},
            {"name": "b", "low": 2, "high": 4, "op": "divide", "pedigree": "given"},
        ]
    )
    assert result["low"] == pytest.approx(2.5)  # 10/4
    assert result["high"] == pytest.approx(10.0)  # 20/2


def test_fermi_needs_a_pedigree() -> None:
    with pytest.raises(ValueError, match="pedigree is required"):
        fermi.combine([{"name": "a", "low": 1, "high": 2}])


def test_fermi_rejects_nonpositive_bound() -> None:
    with pytest.raises(ValueError, match="0 < low"):
        fermi.combine([{"name": "a", "low": 0, "high": 1, "pedigree": "given"}])


# --- dependency truth maintenance ------------------------------------------

DEPENDENCY_LOG: list[dict[str, Any]] = [
    {"id": "c-1", "depends_on": []},
    {"id": "c-2", "depends_on": ["c-1"]},
    {"id": "c-3", "depends_on": ["c-2"]},
    {"id": "c-4", "depends_on": []},
    {"id": "c-5", "depends_on": ["c-1", "c-4"]},
]


def test_dependency_impact_is_transitive_and_hand_computed() -> None:
    result = dependencies.analyze(DEPENDENCY_LOG, targets=["c-3", "c-5"])
    assert result["statuses"] == {entry["id"]: "ACTIVE" for entry in DEPENDENCY_LOG}
    assert result["critical"] == [
        {"id": "c-1", "n_affected": 3, "affected": ["c-2", "c-3", "c-5"]},
        {"id": "c-2", "n_affected": 1, "affected": ["c-3"]},
        {"id": "c-4", "n_affected": 1, "affected": ["c-5"]},
    ]
    assert result["target_dependencies"] == {
        "c-3": ["c-1", "c-2"],
        "c-5": ["c-1", "c-4"],
    }


def test_dependency_status_propagates_a_supersession() -> None:
    entries = [*DEPENDENCY_LOG, {"id": "c-6", "depends_on": [], "supersedes": "c-1"}]
    assert dependencies.statuses(entries) == {
        "c-1": "SUPERSEDED",
        "c-2": "OUT",
        "c-3": "OUT",
        "c-4": "ACTIVE",
        "c-5": "OUT",
        "c-6": "ACTIVE",
    }


def test_dependency_status_treats_an_unknown_premise_as_out() -> None:
    assert dependencies.statuses([{"id": "c-1", "depends_on": ["missing"]}]) == {"c-1": "OUT"}


def test_dependency_analysis_rejects_duplicate_ids_and_nonactive_targets() -> None:
    with pytest.raises(ValueError, match="duplicate dependency entry ids"):
        dependencies.analyze([{"id": "c-1"}, {"id": "c-1"}])
    entries = [{"id": "c-1"}, {"id": "c-2", "supersedes": "c-1"}]
    with pytest.raises(ValueError, match="target entry is not active"):
        dependencies.analyze(entries, targets=["c-1"])
