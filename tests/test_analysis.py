"""The engine reads the data the way a careful analyst would."""
from pathlib import Path

import pandas as pd
import pytest

DATA = Path(__file__).resolve().parents[1] / "data" / "sample"


def test_reporting_week_is_the_last_seven_days_of_data(result):
    w = result.windows.as_dict()
    assert w["reporting_week"] == ["2026-06-24", "2026-06-30"]
    assert w["prior_week"] == ["2026-06-17", "2026-06-23"]
    assert w["immature_from"] == "2026-06-17"


def test_delivery_reconciles_but_outcomes_do_not(result):
    r = result.pack.get("DQ.reconciliation").data["daily_as_share_of_summary"]
    assert r["spend"] == pytest.approx(1.0, abs=1e-4)
    assert r["clicks"] == pytest.approx(1.0, abs=1e-4)
    assert r["pipeline"] < 0.05


def test_last_week_pipeline_is_never_presented_as_final(result):
    week = result.pack.get("WEEK.totals").data
    for metric in ("qualified_leads", "opportunities", "pipeline"):
        assert week[metric]["reliability"] == "provisional"
    assert week["spend"]["reliability"] == "final"


def test_qualified_leads_in_the_lag_window_are_measured_as_incomplete(result):
    lag = result.pack.get("DQ.attribution_lag").data
    assert lag["conversion_completeness"] > 0.9   # lead capture is current
    assert lag["ql_completeness"] < 0.5           # qualification is not


def test_spend_drop_is_explained_by_campaigns_ending_not_performance(result):
    bridge = result.pack.get("WEEK.spend_bridge").data
    total = sum(g["change"] for g in bridge.values())
    assert bridge["ended_or_ending"]["change"] / total > 0.9
    assert abs(bridge["full_week"]["change"]) < 500


def test_webinar_beats_demo_on_every_platform(result):
    po = result.pack.get("SEG.platform_objective").data.set_index(["platform", "objective"])["pipeline_per_dollar"]
    for platform in ("Google", "LinkedIn", "Meta"):
        assert po[(platform, "Webinar")] > po[(platform, "Demo")]


def test_segment_numbers_match_an_independent_calculation(result):
    """Recompute LinkedIn's share of spend and pipeline straight from the CSV."""
    raw = pd.read_csv(DATA / "campaign_summary.csv")
    raw = raw[~raw["data_quality_flag"].fillna("").str.contains("immature")]
    li = raw[raw["platform"] == "LinkedIn"]
    row = result.pack.get("SEG.platform").data.set_index("platform").loc["LinkedIn"]
    assert row["spend_share"] == pytest.approx(li["total_spend"].sum() / raw["total_spend"].sum())
    assert row["pipeline_share"] == pytest.approx(li["pipeline"].sum() / raw["pipeline"].sum())
    assert row["pipeline_per_dollar"] == pytest.approx(li["pipeline"].sum() / li["total_spend"].sum())


def test_region_gap_is_recognized_as_a_mix_effect(result):
    t = result.pack.get("SEG.region").data.set_index("region")
    assert t.loc["DACH", "raw_index"] < 0.6                    # looks bad on the surface
    assert 0.8 < t.loc["DACH", "adjusted_index"] < 1.2         # is ordinary like for like
    assert not any(s["metrics"].get("dimension") == "region" for s in result.signals)


def test_immature_campaigns_are_kept_out_of_benchmarks(result):
    assert result.pack.get("BENCH.overall").data["campaigns"] == 114


def test_fatigue_is_found_on_paid_social_and_not_on_search(result):
    onset = result.pack.get("FATIGUE.curve").data["onset"]
    assert onset["Google"] is None
    assert onset["Meta"]["week"] == 7
    assert onset["LinkedIn"]["week"] == 8


def test_top_signal_is_the_offer_mix_shift_on_google(result):
    top = result.signals[0]
    assert top["type"] == "budget_moved_to_weaker_offer"
    assert top["metrics"]["platform"] == "Google"
    assert "EXP.E013" in top["evidence_ids"]


def test_every_signal_cites_evidence_that_exists(result):
    for s in result.signals:
        assert s["evidence_ids"], s["id"]
        for eid in s["evidence_ids"]:
            assert result.pack.has(eid), (s["id"], eid)


def test_evidence_pack_serializes_to_plain_json(result):
    import json

    payload = json.loads(json.dumps(result.to_dict()))
    assert payload["meta"]["synthetic_data"] is True
    assert {e["reliability"] for e in payload["evidence"]} <= set(payload["reliability_levels"])
