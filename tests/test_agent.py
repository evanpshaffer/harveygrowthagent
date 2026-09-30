"""Evals for the reasoning layer: the model's output is checked, repaired or removed. Never trusted."""
import copy
import json
from pathlib import Path

import pytest

from growth_agent.agent.claims import check_claim, extract_numbers
from growth_agent.agent.loop import AgentError, ReplayClient, review, run_agent
from growth_agent.agent.prompt import TOOLS, build_context
from growth_agent.agent.render import render_brief

# A scripted run kept with the tests, so they do not depend on whatever the last live run produced.
FIXTURE = Path(__file__).resolve().parents[0] / "fixtures" / "scripted_run.json"


class ScriptedClient:
    """Stands in for the model: returns the given turns in order."""

    model, mode = "scripted", "replay"

    def __init__(self, turns):
        self.turns, self.calls = list(turns), []

    def create(self, **kwargs):
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})   # snapshot: the loop keeps appending
        blocks = self.turns.pop(0)
        return {"raw_content": blocks, "blocks": blocks, "stop_reason": "tool_use", "usage": {"input_tokens": 100, "output_tokens": 50}}


@pytest.fixture()
def good_brief():
    turns = json.loads(FIXTURE.read_text())["turns"]
    return copy.deepcopy(turns[-1]["blocks"][-1]["input"]["brief"])


def submit(brief, i=1):
    return [{"type": "tool_use", "id": f"t{i}", "name": "submit_brief", "input": {"brief": brief}}]


def wheres(rev):
    return {p["where"] for p in rev.problems}


# ---- the claim checker ----------------------------------------------------------

def test_numbers_are_extracted_without_mistaking_ids_or_dates_for_them():
    found = [raw for raw, _, _ in extract_numbers("Spend fell 53% to $17,013; E013 and CR021 (SIG.01) since Jun 24, 2026; 3.2x; $385k")]
    assert found == ["53%", "17,013", "3.2", "385k"]


def test_a_number_from_the_cited_evidence_passes(result):
    assert check_claim("Webinar returns 1.42x comparable campaigns and Demo 0.46x on 49% of spend.", ["SEG.objective"], result.pack) == []


def test_a_number_that_is_not_in_the_cited_evidence_is_caught(result):
    problems = check_claim("Webinar returns 1.9x comparable campaigns.", ["SEG.objective"], result.pack)
    assert problems and "1.9" in problems[0]


def test_a_real_number_cited_to_the_wrong_evidence_is_caught(result):
    assert check_claim("LinkedIn CTR is at 71% of launch level by week 10.", ["SEG.objective"], result.pack)
    assert check_claim("LinkedIn CTR is at 71% of launch level by week 10.", ["FATIGUE.curve"], result.pack) == []


# ---- reviewing a submitted brief ---------------------------------------------------

def test_the_recorded_brief_passes_review(result, good_brief):
    rev = review(good_brief, result)
    assert rev.accepted, rev.problems
    assert [v["verdict"] for v in rev.verdicts] == ["ready_for_human_review"] * 3


def test_a_wrong_number_is_located_to_the_exact_claim(result, good_brief):
    good_brief["what_happened"][0]["text"] = good_brief["what_happened"][0]["text"].replace("53%", "63%")
    assert wheres(review(good_brief, result)) == {"what_happened[0]"}


def test_invented_evidence_is_caught(result, good_brief):
    good_brief["why"][0]["evidence_ids"] = ["SEG.imaginary"]
    assert "why[0]" in wheres(review(good_brief, result))


def test_last_weeks_pipeline_cannot_be_stated_as_fact(result, good_brief):
    good_brief["what_happened"][1] = {"text": "Pipeline held steady last week.", "evidence_ids": ["WEEK.totals"]}
    rev = review(good_brief, result)
    assert any("provisional" in p["message"] for p in rev.problems if p["where"] == "what_happened[1]")


def test_unsupported_assurances_are_kept_out_of_creative_direction(result, good_brief):
    good_brief["creative_recommendations"][0] = {"text": "Lead with SOC 2 certified security.", "evidence_ids": ["SEG.theme"]}
    rev = review(good_brief, result)
    assert any("assurance" in p["message"] for p in rev.problems if p["where"] == "creative_recommendations[0]")


def test_a_blocked_experiment_blocks_the_brief(result, good_brief):
    good_brief["experiments"][0]["proposal"]["primary_metric"] = "CTR"
    rev = review(good_brief, result)
    assert any("outcome_metric" in p["message"] for p in rev.problems if p["where"] == "experiments[0]")


def test_the_same_comparison_cannot_take_two_of_the_three_slots(result, good_brief):
    clone = copy.deepcopy(good_brief["experiments"][0])
    clone.update(rank=2)
    clone["proposal"].update(proposal_id="DUP", platform="Meta")
    good_brief["experiments"][1] = clone
    rev = review(good_brief, result)
    assert any("same comparison" in p["message"] for p in rev.problems if p["where"] == "experiments[1]")


def test_a_brief_with_two_experiments_is_rejected(result, good_brief):
    good_brief["experiments"].pop()
    assert not review(good_brief, result).accepted


def test_garbage_is_rejected_not_crashed(result):
    assert not review({"headline": "hello"}, result).accepted
    assert not review(None, result).accepted


# ---- the loop --------------------------------------------------------------------------

def test_the_recorded_run_replays_end_to_end(result):
    run = run_agent(result, ReplayClient(str(FIXTURE)))
    assert len(run.brief.experiments) == 3 and run.held_back == []
    assert any("blocked" in t["event"] and "sample_size" in t["event"] for t in run.trace)   # the guardrails redirected a design mid-run
    text = render_brief(run, result)
    assert "Nothing in this brief has been launched" in text and "Not a live model run" in text


def test_a_rejected_brief_goes_back_to_the_model_and_the_fix_is_accepted(result, good_brief):
    bad = copy.deepcopy(good_brief)
    bad["experiments"][0]["proposal"]["primary_metric"] = "CTR"
    client = ScriptedClient([submit(bad, 1), submit(good_brief, 2)])
    run = run_agent(result, client)
    assert run.submit_attempts == 2 and run.held_back == []
    feedback = json.loads(client.calls[1]["messages"][-1]["content"][0]["content"])
    assert feedback["status"] == "needs_fixes" and "outcome_metric" in feedback["problems"][0]["message"]


def test_what_the_model_cannot_fix_is_removed_and_reported(result, good_brief):
    bad = copy.deepcopy(good_brief)
    bad["why"][0]["text"] = "Webinar returns 9.99x comparable campaigns."
    bad["experiments"][2]["proposal"]["runtime_days"] = 3
    run = run_agent(result, ScriptedClient([submit(bad, i) for i in (1, 2, 3)]))
    assert run.submit_attempts == 3
    assert {h["where"] for h in run.held_back} == {"why[0]", "experiments[2]"}
    assert len(run.brief.experiments) == 2 and len(run.verdicts) == 2
    assert all("9.99" not in c.text for c in run.brief.why)
    assert "Held back: 2 item(s)" in render_brief(run, result)


def test_a_model_that_never_submits_is_stopped(result):
    chatter = [[{"type": "text", "text": "Still thinking."}] for _ in range(result.config.max_agent_turns)]
    with pytest.raises(AgentError, match="did not produce"):
        run_agent(result, ScriptedClient(chatter))


def test_usage_is_counted_so_cost_per_run_is_known(result, good_brief):
    run = run_agent(result, ScriptedClient([submit(good_brief)]))
    assert run.usage["input_tokens"] == 100 and run.usage["output_tokens"] == 50


# ---- what the model is given ---------------------------------------------------------------

def test_the_model_has_no_tool_that_can_launch_or_spend():
    assert {t["name"] for t in TOOLS} == {"get_evidence", "list_creatives", "validate_experiment", "submit_brief"}


def test_tool_schemas_are_self_contained_and_complete():
    text = json.dumps(TOOLS)
    assert "$ref" not in text and "$defs" not in text
    proposal = TOOLS[2]["input_schema"]["properties"]["proposal"]
    assert {"title", "hypothesis", "control", "variant", "primary_metric", "decision_rule"} <= set(proposal["properties"])


def test_context_gives_statements_not_raw_tables(result):
    ctx = build_context(result)
    assert "SEG.objective | observational" in ctx and "SIG.01" in ctx
    assert len(ctx) < 40_000   # small enough that a run stays cheap
