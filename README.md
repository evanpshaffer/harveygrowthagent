# Growth Agent

A prototype AI Growth Agent for a performance marketing team. It reads campaign
data from Google Ads, LinkedIn Ads and Meta, works out what happened, why, and
what to test next, and stages the next experiment for a human to approve.

Built for the Harvey Growth Engineer take-home. All data is synthetic sample
data and does not represent Harvey performance.

## Status

| Layer | State |
|---|---|
| Integration layer (connectors, canonical schema, MCP server) | Built, tested |
| Analysis engine (data quality, what happened, why, experiment trust, signals) | Built, tested |
| Guardrails (validator for proposed experiments) | Built, tested |
| Reasoning layer (model writes the brief and designs three experiments through tools) | Built, tested offline. Live run needs an API key |
| Claim checker (every number traced to cited evidence) | Built, tested |
| Approval UI and staged launch payloads | Next |
| Live API connectors | Interface defined, not implemented |

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env                  # then paste your ANTHROPIC_API_KEY into .env

python -m growth_agent.brief          # the full agent: writes out/brief.md and out/brief.json
python -m growth_agent.brief --replay examples/recorded_run.json   # same pipeline, no key, no cost

python -m growth_agent.run            # analysis only: out/evidence_pack.json and out/analysis_report.md
python -m pytest -q                   # 93 tests and evals
python -m growth_agent.run --validate examples/proposal_unsafe.json   # watch the guardrails block it
python mcp_server.py                  # expose everything as MCP tools
```

## How it works

```
  Google Ads   LinkedIn Ads   Meta   CRM   Experiment log   Creative library
        \           |          |      |          |               /
         +----------+----------+------+----------+--------------+
                                  |
                    INTEGRATION LAYER (connectors/)
        one DataSource interface -> four canonical tables, validated
             CsvSource (sample data today)  |  LiveSource (the seam)
                                  |
                    ANALYSIS ENGINE (analysis/)      deterministic, no model
   data quality audit -> what happened -> why -> experiment trust -> signals
                                  |
                       EVIDENCE PACK (evidence.py)
        every fact has an id, a reliability level, caveats and its data
                                  |
                    REASONING LAYER (agent/)          the only model step
   reads evidence through tools, designs experiments, tests each design
   against the guardrails, submits a structured brief citing evidence ids
                                  |
              CLAIM CHECK + GUARDRAILS (agent/claims.py, guardrails.py)
     every number looked up in the evidence it cites; every experiment
     re-validated; problems go back to the model; leftovers are removed
                                  |
                     HUMAN APPROVAL (next)  approve / edit / reject
                                  |
                 STAGED in the ad platform as DRAFT or PAUSED
```

The design rule: **code decides what is true, the model decides what to do
about it, code checks the model's answer, and a person decides whether it
runs.**

## Design decisions

1. **Numbers are computed, never generated.** The model never does arithmetic.
   It receives an evidence pack where every fact has an id, and it must cite
   ids. A claim without an id does not ship.
2. **Reliability is explicit.** Each evidence item is `final`, `provisional`,
   `observational`, `modeled` or `data_quality`. Last week's pipeline is
   provisional, so the agent does not judge last week on pipeline.
3. **Like-for-like before conclusions.** Platform and offer type dominate this
   data. Every segment comparison is re-run holding them constant (observed
   over expected). That is what shows DACH's weak numbers are a channel mix
   effect and not a region problem.
4. **The experiment log is a set of claims, not facts.** Each experiment is
   re-scored on runtime, sample and metric quality, then checked against
   settled campaign data. Three logged results are rejected.
5. **Signals, then experiments.** The engine produces ranked signals. The
   model designs experiments from them. The guardrails check the designs.
6. **Thresholds live in one file.** `growth_agent/config.py` holds every
   number with the reason for it.

## The reasoning layer

The model works through four tools: `get_evidence`, `list_creatives`,
`validate_experiment` and `submit_brief`. It has no tool that can launch or
spend. A run looks like this:

1. It starts with a compact context: the evidence index (one sentence per
   item), the ranked signals, the guardrail limits and the values that exist
   in the data. About 6,000 tokens. It pulls full tables only when it needs them.
2. It designs experiments and tests each one with `validate_experiment`. On
   the sample data a LinkedIn Demo test is blocked as underpowered within the
   budget ceiling, so the agent redesigns around offers LinkedIn can afford.
3. It submits the brief. Code then checks it:
   - **Claim check.** Every number in every sentence must appear in the
     evidence that sentence cites.
   - **Lag check.** Last week's qualified leads, opportunities and pipeline
     can only be mentioned as provisional.
   - **Assurance check.** Creative recommendations cannot contain compliance
     or guarantee language.
   - **Guardrails.** All three experiments are re-validated.
4. Problems go back to the model, up to three submissions. Anything still
   failing is removed from the brief and listed under "held back". Nothing
   unverified ships.

Every run reports its turns, tokens and cost at the bottom of the brief.
`examples/recorded_run.json` is a scripted recording used for tests and
offline demos. It is not a live run; `--record` replaces it with one.

## Imperfect data: what the agent found and does about it

| Problem | What the agent does |
|---|---|
| Daily and summary tables agree on spend but not on outcomes | Summary for efficiency, daily for timing, never mixed. Stated as assumption A1. |
| Last 14 days are inside the attribution lag | Measures the lag inside each campaign. Reports only delivery and lead capture as final. |
| 45 daily rows have no CRM pipeline value | Left missing. Never zero-filled. |
| Audience labels are inconsistent | Normalized through an alias map. Unknown labels are surfaced, not guessed. |
| Experiment "wins" on 3 to 5 days of data | Rejected. Cannot be cited as support. |
| Campaign-to-experiment links point at the wrong platform | Not used for attribution. |
| `creative_age_days` is really campaign age | Fatigue measured within campaign. Flagged. |

## Guardrails

A proposed experiment is blocked unless all of these hold:

| Rule | Why |
|---|---|
| `requires_human_approval` is true and status is DRAFT or PAUSED | The agent can stage. It cannot launch. |
| Primary metric is a business outcome | Pipeline, opportunities and revenue over CTR and CPC. |
| Platform, audience, region, offer, theme, CTA and creative all exist | No invented segments. |
| Creative is active and made for the target audience | No mismatched creative. |
| Control and variant differ on exactly one thing | A result must have one cause. |
| Daily and total budget are under the ceilings | Never more exposure than the team already takes. |
| Runtime is at least 28 days and expected sample clears the minimum | No more false winners. |
| A decision rule is written in advance | No deciding after the results are in. |
| Evidence ids exist, are settled, and are not rejected experiments | No claims built on noise. |
| The question is not already answered by a trusted test | No wasted budget. |
| The variant does not repeat a known loser | No relearning old lessons. |

The best possible verdict is `ready_for_human_review`. There is no verdict,
function or MCP tool that approves, launches or spends.

## Swapping sample data for live systems

Implement the four methods in `growth_agent/connectors/live_source.py` so they
return the canonical tables in `growth_agent/schema.py`, then run with
`--source live`. Nothing else changes. `tests/test_integration_layer.py` proves
this by swapping in a different source and getting identical output.

## MCP

`mcp_server.py` exposes the same data, evidence and guardrails as tools:
`get_campaigns`, `get_daily_performance`, `get_experiments`, `get_creatives`,
`list_evidence`, `get_evidence`, `get_signals`, `get_context`,
`validate_experiment_proposal`. The repo includes a `.mcp.json` so an MCP
client opened in this folder can connect to it.

## Layout

```
growth_agent/
  config.py            every threshold, with its reason
  schema.py            the canonical data contract
  connectors/          DataSource interface, CSV connector, live seam
  analysis/
    quality.py         data quality audit
    windows.py         reporting week and attribution lag window
    performance.py     what happened
    drivers.py         why (segments, mix, funnel, fatigue, creative)
    experiments.py     experiment trust scoring
    signals.py         ranked opportunity signals
  evidence.py          the evidence pack
  agent/
    prompt.py          system prompt, tools, starting context
    loop.py            agent loop, review, repair, live and replay clients
    claims.py          claim checker
    schema.py          the brief's structure
    render.py          brief.md
  brief.py             command line for the full agent
  guardrails.py        proposal validator
  pipeline.py          runs everything, holds the stated assumptions
  report.py            deterministic readout of the evidence pack
  run.py               command line
mcp_server.py          MCP tools
tests/                 93 tests and evals
examples/              sound and unsafe proposals, a recorded agent run
data/sample/           the four take-home CSVs
out/                   generated evidence pack, report and brief
```
