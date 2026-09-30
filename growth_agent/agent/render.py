"""Turn a checked brief into the document the team reads."""
from __future__ import annotations

from ..pipeline import ASSUMPTIONS, Result
from .loop import AgentRun
from .schema import Claim


def _claim(c: Claim) -> str:
    return f"- {c.text} `[{', '.join(c.evidence_ids)}]`"


def _arm(arm) -> str:
    """The arm's description, plus any setting the description does not already mention."""
    said = arm.description.lower()
    bits = [b for b in (arm.objective, arm.theme, arm.cta, arm.creative_id, arm.targeting) if b and b.lower() not in said]
    return f"{arm.description} ({', '.join(bits)})" if bits else arm.description


def render_brief(run: AgentRun, result: Result) -> str:
    b, w, cfg = run.brief, result.windows.as_dict(), result.config
    out: list[str] = []
    add = out.append

    add("# Weekly Experimentation Brief")
    add("")
    add(f"**Week of {w['reporting_week'][0]} to {w['reporting_week'][1]}** · Performance Marketing · Google Ads, LinkedIn Ads, Meta")
    add("")
    if result.dataset.is_synthetic:
        add("> Synthetic sample data. Not Harvey performance.")
    if run.mode == "replay":
        add("> Replay of a recorded run for offline demos and tests. Not a live model run.")
    n = len(b.experiments)
    add(
        f"> **Nothing in this brief has been launched.** {n} experiment{'s are' if n != 1 else ' is'} staged as "
        f"draft{'s' if n != 1 else ''} and wait{'' if n != 1 else 's'} for a person to approve, edit or reject."
    )
    add("")
    add("## The headline")
    add("")
    add(f"{b.headline.text} `[{', '.join(b.headline.evidence_ids)}]`")

    add("\n## What happened last week\n")
    out.extend(_claim(c) for c in b.what_happened)

    add("\n## Why it happened\n")
    out.extend(_claim(c) for c in b.why)

    add("\n## The three experiments to run next\n")
    ranked = sorted(zip(b.experiments, run.verdicts), key=lambda pair: pair[0].rank)
    for e, v in ranked:
        p = e.proposal
        arms = v["computed"].get("arms", {})
        add(f"### {e.rank}. {p.title}\n")
        add(f"**Status: DRAFT, awaiting approval.** Guardrails: {v['verdict'].replace('_', ' ')}"
            + (f", {len(v['warnings'])} warning(s)." if v["warnings"] else "."))
        add("")
        add(f"**Hypothesis.** {p.hypothesis}")
        add("")
        add(f"**Why this test.** {e.rationale.text} `[{', '.join(e.rationale.evidence_ids)}]`")
        add("")
        add("| | |")
        add("|---|---|")
        add(f"| Where | {p.platform} · {p.audience} · {p.region} |")
        add(f"| Control | {_arm(p.control)} |")
        add(f"| Variant | {_arm(p.variant)} |")
        add(f"| The one thing that differs | {', '.join(v['computed'].get('differs_on', [])) or 'n/a'} |")
        add(f"| Primary metric | {p.primary_metric} |")
        add(f"| Guardrail metrics | {', '.join(p.guardrail_metrics) or 'none'} |")
        add(f"| Budget | ${p.daily_budget_per_arm:,.0f} per arm per day for {p.runtime_days} days (${v['computed'].get('total_budget', 0):,.0f} in total) |")
        if arms:
            add("| Expected volume | " + "; ".join(
                f"{name}: about {a['expected_qualified_leads']:,.0f} qualified leads, {a['expected_opportunities']:,.0f} opportunities"
                for name, a in arms.items()) + " |")
        add(f"| Earliest valid read | Day {v['computed'].get('earliest_readout_day')} (runtime plus {cfg.lead_maturity_days} days for attribution to settle) |")
        add(f"| Decision rule | {p.decision_rule} |")
        add(f"| Evidence | {', '.join(p.evidence_ids)} |")
        if p.retest_of:
            add(f"| Re-test of | {p.retest_of} |")
        add("")
        add(f"**What we learn either way.** {e.expected_learning}")
        for wmsg in v["warnings"]:
            add(f"\n- Guardrail warning ({wmsg['rule']}): {wmsg['message']}")
        add("")

    add("## Creative recommendations\n")
    out.extend(_claim(c) for c in b.creative_recommendations)

    add("\n## Risks and observations\n")
    out.extend(_claim(c) for c in b.risks_and_observations)

    add("\n## What the data cannot tell us yet\n")
    for eid in ("DQ.attribution_lag", "DQ.reconciliation", "DQ.daily_outcome_gaps"):
        e = result.pack.get(eid)
        add(f"- **{e.title}.** {e.statement} `[{eid}]`")

    add("\n## Assumptions\n")
    for a in ASSUMPTIONS:
        add(f"- **{a['id']}.** {a['assumption']}")

    add("\n## How this brief was produced and checked\n")
    n_claims = 1 + len(b.what_happened) + len(b.why) + len(b.creative_recommendations) + len(b.risks_and_observations) + len(b.experiments)
    add(f"- Facts: computed by the analysis engine from the `{result.dataset.source_name}` source. {len(result.pack.ids())} evidence items.")
    add(f"- Writing and experiment design: `{run.model}` ({run.mode} run), {run.turns} turns, {run.submit_attempts} submission{'s' if run.submit_attempts != 1 else ''} of the brief.")
    add(f"- Claim check: every number in {n_claims} claims was matched to the evidence it cites.")
    add(f"- Guardrails: {len(b.experiments)} experiments passed every rule. The best possible verdict is 'ready for human review'.")
    if run.held_back:
        add(f"- Held back: {len(run.held_back)} item(s) failed checks after {run.submit_attempts} attempts and were removed:")
        for h in run.held_back:
            add(f"  - {h['where']}: \"{h['text']}\" ({'; '.join(h['reasons'])})")
    else:
        add("- Held back: nothing. No claim or experiment was removed.")
    if run.mode == "live":
        cost = "n/a" if run.cost_usd is None else f"${run.cost_usd:.2f}"
        u = run.usage
        add(f"- Cost of this run: {cost} and {run.seconds:.0f} seconds. {u['input_tokens'] + u['cache_creation_input_tokens']:,} input tokens billed in full, "
            f"{u['cache_read_input_tokens']:,} read from cache, {u['output_tokens']:,} output.")
    else:
        add("- This is a replay of a recorded run, used for offline demos and tests. Run with an API key for a live brief.")
    add("\n### Agent steps\n")
    for t in run.trace:
        add(f"- Turn {t['turn']}: {t['event']}")
    add("")
    return "\n".join(out)
