"""Evals for the human checkpoint: nothing is staged without a recorded approval, and nothing staged can spend."""
import json
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from growth_agent.app import create_app
from growth_agent.approval import ApprovalDesk, DecisionRefused
from growth_agent.guardrails import validate
from growth_agent.staging import PLATFORMS, StagingRefused, proposal_hash

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "scripted_run.json"


@pytest.fixture()
def brief():
    return json.loads(FIXTURE.read_text())["turns"][-1]["blocks"][-1]["input"]["brief"]


@pytest.fixture()
def proposals(brief):
    return [e["proposal"] for e in brief["experiments"]]


@pytest.fixture()
def desk(result, tmp_path):
    return ApprovalDesk(result, tmp_path)


def test_nothing_can_be_staged_without_an_approval(desk, proposals):
    with pytest.raises(StagingRefused, match="No approval"):
        desk.stage(proposals[0])
    assert desk.staged() == {}


def test_a_rejected_experiment_cannot_be_staged(desk, proposals):
    desk.decide(proposals[0], "rejected", "Reviewer")
    with pytest.raises(StagingRefused):
        desk.stage(proposals[0])


def test_an_approval_covers_only_the_design_that_was_approved(desk, proposals):
    desk.decide(proposals[0], "approved", "Reviewer")
    changed = {**proposals[0], "daily_budget_per_arm": proposals[0]["daily_budget_per_arm"] + 100}
    with pytest.raises(StagingRefused, match="changed after it was approved"):
        desk.stage(changed)


def test_a_decision_needs_a_named_person(desk, proposals):
    with pytest.raises(DecisionRefused, match="named reviewer"):
        desk.decide(proposals[0], "approved", "   ")


def test_approving_stages_a_draft_that_cannot_spend(desk, proposals):
    desk.decide(proposals[0], "approved", "Reviewer", "Looks right")
    draft = desk.staged()[proposals[0]["proposal_id"]]
    assert draft["spends_money"] is False
    assert {c["status"] for c in draft["campaigns"]} == {"PAUSED"}
    assert [c["role"] for c in draft["campaigns"]] == ["control", "variant"]
    assert draft["approval"]["approved_by"] == "Reviewer"
    assert draft["approval"]["design_fingerprint"] == proposal_hash(proposals[0])


def test_no_platform_has_a_live_staging_status(result):
    for platform in PLATFORMS.values():
        assert platform["paused_status"] in result.config.allowed_staging_statuses
        assert platform["paused_status"] not in ("ACTIVE", "ENABLED", "LIVE")


def test_a_reviewer_edit_is_checked_by_the_guardrails_before_it_can_be_approved(desk, proposals):
    with pytest.raises(DecisionRefused) as err:
        desk.decide(proposals[0], "approved", "Reviewer", edits={"daily_budget_per_arm": 5000})
    assert {b["rule"] for b in err.value.blocks} == {"budget"}
    assert desk.log() == [] and desk.staged() == {}


def test_a_valid_edit_is_recorded_and_staged(desk, proposals):
    entry = desk.decide(proposals[0], "approved", "Reviewer", edits={"daily_budget_per_arm": 700})
    assert entry["edits"]["daily_budget_per_arm"]["to"] == 700
    draft = desk.staged()[proposals[0]["proposal_id"]]
    assert draft["campaigns"][0]["daily_budget_usd"] == 700


def test_only_budget_and_runtime_can_be_edited_at_approval(desk, proposals):
    with pytest.raises(DecisionRefused, match="cannot be edited"):
        desk.decide(proposals[0], "approved", "Reviewer", edits={"primary_metric": "CTR"})


def test_approved_tests_together_cannot_pass_the_slate_ceiling(desk, proposals):
    desk.decide(proposals[0], "approved", "Reviewer", edits={"daily_budget_per_arm": 1000})   # 56,000
    desk.decide(proposals[1], "approved", "Reviewer")                                          # 52,500
    with pytest.raises(DecisionRefused, match="ceiling"):
        desk.decide(proposals[2], "approved", "Reviewer")                                      # would pass 120,000


def test_reopening_withdraws_the_draft_and_keeps_the_history(desk, proposals):
    desk.decide(proposals[0], "approved", "Reviewer")
    desk.decide(proposals[0], "reopened", "Reviewer")
    assert desk.staged() == {}
    assert [e["decision"] for e in desk.log()] == ["approved", "reopened"]   # the log is appended to, never rewritten


# ---- through the web API, as the approval screen uses it ------------------------------

@pytest.fixture()
def client(result, tmp_path, brief):
    payload = {
        "brief": brief,
        "experiment_verdicts": [validate(e["proposal"], result) for e in brief["experiments"]],
        "held_back": [],
        "run": {"model": "scripted", "mode": "replay", "turns": 4, "submit_attempts": 1, "usage": {}, "cost_usd": None, "seconds": 0},
        "trace": [],
    }
    (tmp_path / "brief.json").write_text(json.dumps(payload, default=str))
    return TestClient(create_app(str(tmp_path)))


def test_the_screen_loads_the_brief_and_the_evidence_it_cites(client):
    state = client.get("/api/state").json()
    assert state["has_brief"] and state["decisions"] == {} and state["staged"] == {}
    assert "SEG.objective" in state["evidence"]
    assert client.get("/").status_code == 200
    assert client.get("/api/evidence/SEG.objective").json()["reliability"] == "observational"


def test_approving_through_the_api_stages_the_draft(client, proposals):
    pid = proposals[0]["proposal_id"]
    state = client.post("/api/decisions", json={"proposal_id": pid, "decision": "approved", "reviewer": "Reviewer"}).json()
    assert state["decisions"][pid]["decision"] == "approved" and state["staged"][pid]["status"] == "PAUSED"


def test_the_api_refuses_an_anonymous_or_blocked_approval(client, proposals):
    pid = proposals[0]["proposal_id"]
    assert client.post("/api/decisions", json={"proposal_id": pid, "decision": "approved", "reviewer": ""}).status_code == 400
    r = client.post("/api/decisions", json={"proposal_id": pid, "decision": "approved", "reviewer": "R", "edits": {"runtime_days": 3}})
    assert r.status_code == 400 and r.json()["blocks"]
    assert client.get("/api/state").json()["staged"] == {}


def test_the_api_has_no_route_that_launches(client):
    paths = {r.path for r in client.app.routes}
    assert paths == {"/", "/api/state", "/api/evidence/{eid}", "/api/preview", "/api/decisions"}
