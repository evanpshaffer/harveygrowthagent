import pytest

from growth_agent.pipeline import build


@pytest.fixture(scope="session")
def result():
    """One full pipeline run on the sample data, shared by every test."""
    return build(source="csv")


@pytest.fixture()
def good_proposal():
    """A proposal that should pass every guardrail."""
    return {
        "proposal_id": "P-TEST",
        "title": "Webinar offer vs Demo offer on Google, Law Firm Enterprise",
        "hypothesis": "A webinar offer produces more pipeline per dollar than a demo offer for the same audience and message",
        "platform": "Google",
        "audience": "Law Firm - Enterprise",
        "region": "US",
        "control": {"label": "Control", "description": "Demo offer, ROI message", "objective": "Demo", "theme": "ROI", "creative_id": "CR001"},
        "variant": {"label": "Variant", "description": "Webinar offer, ROI message", "objective": "Webinar", "theme": "ROI", "creative_id": "CR001"},
        "primary_metric": "Pipeline per $",
        "guardrail_metrics": ["CPL", "CTR"],
        "daily_budget_per_arm": 750,
        "runtime_days": 28,
        "decision_rule": "Adopt webinar as the default Google offer if pipeline per dollar is at least 25% higher at day 42.",
        "evidence_ids": ["SIG.01", "SEG.platform_objective", "MIX.objective"],
        "retest_of": "E013",
    }
