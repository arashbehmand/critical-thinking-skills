"""Exact-value tests pin the math — hand-computed, per the whitepaper's doctrine."""

from typing import Any

import pytest

from ctmcp.core import ach, brier, fermi, panel, qbaf

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


def test_panel_numeric_hand_values() -> None:
    result = panel.numeric([6, 7, 4, 7, 5])
    assert result["median"] == 6
    assert result["mean"] == pytest.approx(5.8)
    assert result["range"] == 3
    assert result["disagreement"] is False  # 3 > 3 is false: strict inequality


def test_panel_numeric_flags_wide_spread() -> None:
    assert panel.numeric([2, 9, 3])["disagreement"] is True


def test_panel_vote_plurality() -> None:
    result = panel.vote(["A", "B", "A", "A", "C"])
    assert result["winner"] == "A"
    assert result["share"] == 0.6
    assert result["disagreement"] is False  # 0.6 < 0.6 is false: strict inequality


def test_panel_vote_tie() -> None:
    result = panel.vote(["A", "B"])
    assert result["tie"] is True
    assert result["winner"] is None
    assert result["disagreement"] is True


def test_panel_needs_two() -> None:
    with pytest.raises(ValueError, match="at least 2"):
        panel.numeric([5.0])


# --- brier ------------------------------------------------------------------


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


def test_brier_no_resolved_entries() -> None:
    result = brier.report(
        [{"id": "p-1", "p": 0.5, "resolve_by": "2099-01-01", "outcome": None}], today="2026-07-27"
    )
    assert result["brier"] is None
    assert result["bins"] == []


def test_brier_rejects_bad_outcome() -> None:
    with pytest.raises(ValueError, match="outcome"):
        brier.report(
            [{"id": "x", "p": 0.5, "resolve_by": "2026-01-01", "outcome": 2}], "2026-07-27"
        )


# --- fermi ------------------------------------------------------------------

PIANO_FACTORS: list[dict[str, Any]] = [
    {"name": "US households", "low": 1.2e8, "high": 1.4e8},
    {"name": "share owning pianos", "low": 0.03, "high": 0.08, "op": "multiply"},
    {"name": "tunings per piano per year", "low": 0.3, "high": 1.0, "op": "multiply"},
    {"name": "tunings per tuner per year", "low": 600, "high": 1200, "op": "divide"},
]


def test_fermi_piano_tuners() -> None:
    result = fermi.combine(PIANO_FACTORS)
    assert result["low"] == pytest.approx(900.0)  # 1.2e8·0.03·0.3/1200
    assert result["high"] == pytest.approx(1.4e8 * 0.08 * 1.0 / 600)
    assert result["widest_factor"] == "tunings per piano per year"


def test_fermi_divide_interval() -> None:
    result = fermi.combine(
        [{"name": "a", "low": 10, "high": 20}, {"name": "b", "low": 2, "high": 4, "op": "divide"}]
    )
    assert result["low"] == pytest.approx(2.5)  # 10/4
    assert result["high"] == pytest.approx(10.0)  # 20/2


def test_fermi_rejects_nonpositive_bound() -> None:
    with pytest.raises(ValueError, match="0 < low"):
        fermi.combine([{"name": "a", "low": 0, "high": 1}])
