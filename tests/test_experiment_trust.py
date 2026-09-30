"""Evals: the agent does not learn from experiments that prove nothing."""
import pandas as pd
import pytest

from growth_agent.analysis.experiments import parse_hypothesis, score
from growth_agent.config import CONFIG


def _exp(result, eid):
    return next(e for e in result.experiments if e["experiment_id"] == eid)


@pytest.mark.parametrize("eid", ["E011", "E012", "E013"])
def test_planted_false_winners_are_rejected(result, eid):
    e = _exp(result, eid)
    assert e["tier"] == "rejected"
    assert e["usable_as_evidence"] is False


@pytest.mark.parametrize("eid", ["E012", "E013"])
def test_logged_wins_on_tiny_samples_are_overturned(result, eid):
    assert _exp(result, eid)["overturned"] is True


def test_rejection_does_not_depend_on_the_log_admitting_it(result):
    """The notes call these 'false winners'. The agent must not need that hint."""
    row = pd.Series(
        {"runtime_days": 4, "sample_size": 20, "primary_metric": "Pipeline per $", "confidence": "High",
         "platform": "Meta", "notes": "Clear winner, roll out everywhere."}
    )
    tier, reasons = score(row, CONFIG)
    assert tier == "rejected"
    assert any("4 days" in r for r in reasons) and any("sample of 20" in r for r in reasons)


def test_a_long_well_powered_test_on_ctr_is_still_only_directional():
    row = pd.Series(
        {"runtime_days": 35, "sample_size": 900, "primary_metric": "CTR", "confidence": "High", "platform": "Meta", "notes": ""}
    )
    tier, reasons = score(row, CONFIG)
    assert tier == "directional"
    assert "proxy" in reasons[0]


@pytest.mark.parametrize("eid", ["E001", "E014", "E005", "E016", "E017"])
def test_sound_experiments_are_trusted(result, eid):
    assert _exp(result, eid)["tier"] == "trusted"


def test_a_valid_repeat_is_linked_to_the_original(result):
    assert _exp(result, "E001")["replicates"] == ["E014"]
    assert _exp(result, "E014")["replicates"] == ["E001"]


def test_false_winner_on_offer_is_contradicted_by_settled_campaign_data(result):
    e = _exp(result, "E013")
    assert e["observed"]["verdict"] == "disagrees"
    assert e["observed"]["ratio_a_over_b"] < 0.5   # Demo returns under half of Webinar on Google


def test_inconsistent_metadata_lowers_trust(result):
    e = _exp(result, "E002")   # logged on Meta, notes talk about LinkedIn
    assert e["tier"] == "directional"
    assert any("LinkedIn" in r for r in e["reasons"])


@pytest.mark.parametrize(
    "text,expected",
    [
        ("ROI vs productivity messaging", ("theme", "ROI", "AI Productivity")),
        ("Demo vs webinar", ("objective", "Demo", "Webinar")),
        ("Talk to Sales vs Book Demo", ("cta", "Talk to Sales", "Book Demo")),
        ("Video vs static for In-House", ("format", "Video", "Static")),
        ("ROI vs productivity messaging - repeat", ("theme", "ROI", "AI Productivity")),
    ],
)
def test_hypotheses_are_read_into_testable_comparisons(text, expected):
    p = parse_hypothesis(text, CONFIG)
    assert (p["dimension"], p["a"], p["b"]) == expected


@pytest.mark.parametrize("text", ["Stock photo vs product UI", "CFO targeting vs legal leaders", "Max conversions vs target CPA"])
def test_hypotheses_outside_the_data_are_not_forced_into_a_comparison(text):
    assert parse_hypothesis(text, CONFIG) is None


def test_rejected_experiments_never_appear_as_support_for_a_signal(result):
    rejected = {f"EXP.{e['experiment_id']}" for e in result.experiments if not e["usable_as_evidence"]}
    for s in result.signals:
        if s["type"] in ("false_winner", "budget_moved_to_weaker_offer", "under_tested_theme"):
            continue  # these cite the rejected test as the problem, not as support
        assert not rejected & set(s["evidence_ids"]), s["id"]
