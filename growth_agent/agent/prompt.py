"""What the model is told, and the context it starts with."""
from __future__ import annotations

import json

from ..analysis.metrics import to_jsonable
from ..guardrails import ExperimentProposal
from ..pipeline import ASSUMPTIONS, Result
from .schema import Brief, inline_schema

SYSTEM = """You are the Growth Agent for the performance marketing team at a legal AI company. \
The team runs paid campaigns on Google Ads, LinkedIn Ads and Meta. Each week you write the Weekly \
Experimentation Brief, which answers three questions: what happened last week, why it happened, \
and what to test next.

How the system you are part of works:
- A deterministic analysis engine has already computed every fact. Each fact is an evidence item \
with an id, a reliability level and a one-sentence statement. You do not compute numbers. You \
decide what matters and what to do about it.
- After you submit, code checks your brief. Every number you write is looked up in the evidence \
you cited for that sentence. Every experiment is run through guardrails. Anything that fails \
comes back to you to fix.
- A person approves or rejects each experiment. You can recommend and stage. You can never launch \
a campaign or spend budget, and nothing you write should imply that anything has been launched.

Rules for what you write:
1. Every claim cites the evidence ids it rests on. Use only numbers that appear in those items. \
If you want a number, fetch the item with get_evidence and copy it exactly. Do not round \
differently, combine, or derive new numbers.
2. Judge performance on business outcomes: pipeline, opportunities and revenue per dollar. Click \
and cost-per-lead metrics are diagnostics.
3. The reporting week sits inside the attribution lag window. Report delivery and lead capture \
for the week as fact. Treat anything about the week's qualified leads, opportunities or pipeline \
as provisional, and cite DQ.attribution_lag when you mention them.
4. Evidence marked observational shows where to test. It does not prove a cause. Say "in settled \
campaigns" rather than "X causes Y".
5. A rejected experiment can never support a recommendation. It can be the reason to re-test.
6. If the data cannot answer something, say so. Do not fill the gap.

Rules for the three experiments:
1. Pick the three tests with the most pipeline at stake that the evidence supports. Prefer tests \
that resolve a decision the team is making now. The signals are ranked: your three should cover \
the largest ones, and if a top signal gets no test, say why in risks_and_observations.
1a. Three slots, three different decisions. Never test the same comparison twice, even on a \
second platform. If a result should be repeated elsewhere, write that into the decision rule.
2. Control and variant differ on exactly one thing: the offer (objective), the message (theme), \
the CTA, the creative, or the targeting. Everything else is identical.
3. The primary metric is a business outcome. Put click and lead metrics in guardrail_metrics.
4. Write the decision rule before the test runs. It must name the day the result is read (after \
attribution settles) and a numeric threshold, for example "if the variant is at least 25% higher \
on day 42, do X; if within 25%, do Y; otherwise do Z". "Beats" or "exceeds noise" is not a rule.
5. Call validate_experiment on every design before you submit. If it is blocked, change the \
design. A sample-size block lists the offers that can be tested on that platform: try those \
before giving up on the platform. Only say something cannot be tested if the validator confirmed \
it, and then say exactly what was blocked (for example "LinkedIn Demo", not "LinkedIn").
6. Use creative ids from list_creatives that are made for the audience you are targeting.

Rules for creative recommendations:
1. Recommend direction: which message, format and audience pairing, and when to refresh.
2. Do not write ad copy. Do not name customers. Do not make security, compliance or performance \
assurances. Legal buyers read those literally.

Style: write for busy marketers. Short sentences. Specific. No hype, no hedging filler. One or \
two sentences per claim. Write in your own words and say what each fact means for the team; do \
not paste evidence statements. The headline names the decision the team faces and the size of \
the gap behind it.

When your three experiments validate and your brief is complete, call submit_brief. If it comes \
back with problems, fix exactly those and submit again."""

TOOLS = [
    {
        "name": "get_evidence",
        "description": (
            "Fetch full evidence items by id, including the underlying data tables and caveats. Use this before "
            "quoting any number that is not in the one-sentence statement you were given, and to look at segment "
            "tables, the experiment log and campaign detail. Returns one object per id."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"ids": {"type": "array", "items": {"type": "string"}, "description": "Evidence ids, e.g. ['SEG.objective', 'EXP.E013']"}},
            "required": ["ids"],
        },
    },
    {
        "name": "list_creatives",
        "description": (
            "List the creative library: id, theme, format, audience group and primary message for each creative. "
            "Use it to choose creative ids for experiment arms. A creative can only be used for the audience group "
            "it was made for."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "validate_experiment",
        "description": (
            "Run one proposed experiment through the guardrails. Returns a verdict of 'ready_for_human_review' or "
            "'blocked', every reason, warnings, and computed figures (expected qualified leads and opportunities "
            "per arm, total budget, earliest readout day). Call this on every design before submitting the brief."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"proposal": inline_schema(ExperimentProposal)},
            "required": ["proposal"],
        },
    },
    {
        "name": "submit_brief",
        "description": (
            "Submit the finished Weekly Experimentation Brief. Code then checks every number against the cited "
            "evidence and re-validates every experiment. Returns 'accepted', or a list of problems to fix."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"brief": inline_schema(Brief)},
            "required": ["brief"],
        },
    },
]


def build_context(result: Result) -> str:
    """The first message: everything the model needs to start, and nothing it must compute."""
    cfg = result.config
    c = result.dataset.campaigns
    vocab = {k: sorted(c[k].dropna().unique().tolist()) for k in ("platform", "audience", "region", "objective", "theme", "cta")}
    parts = [
        "# Weekly run",
        json.dumps(to_jsonable({"windows": result.windows.as_dict(), "synthetic_data": result.dataset.is_synthetic})),
        "\n# Assumptions the analysis engine made",
        "\n".join(f"- {a['id']}: {a['assumption']}" for a in ASSUMPTIONS),
        "\n# Ranked signals (where a test would pay off)",
        "\n".join(
            f"- {s['id']} [{s['strength']}] {s['title']}. {s['statement']} Test angle: {s['test_angle']} "
            f"Evidence: {', '.join(s['evidence_ids'])}"
            for s in result.signals
        ),
        "\n# Evidence index (id | reliability | statement)",
        "\n".join(f"- {e.id} | {e.reliability} | {e.statement}" for e in result.pack.items() if not e.id.startswith("SIG.")),
        "\n# Guardrails your experiments must pass",
        json.dumps(
            {
                "allowed_primary_metrics": list(cfg.outcome_metrics),
                "min_runtime_days": cfg.min_planned_runtime_days,
                "min_expected_qualified_leads_per_arm": cfg.min_sample_size,
                "max_daily_budget_per_arm": cfg.max_daily_budget,
                "max_total_test_budget": cfg.max_total_test_budget,
                "allowed_status": list(cfg.allowed_staging_statuses),
                "one_variable_only": True,
            }
        ),
        "\n# Values that exist in the data (use these exactly)",
        json.dumps(vocab),
        "\nWrite this week's brief. Fetch the evidence you need, design and validate three experiments, then submit.",
    ]
    return "\n".join(parts)
