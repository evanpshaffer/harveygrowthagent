"""Deterministic analysis report.

This is the engine's own plain readout of the evidence pack, written without
any model call. It is the raw material for the Weekly Experimentation Brief,
and a way to inspect exactly what the reasoning layer will be given.
"""
from __future__ import annotations

from .pipeline import ASSUMPTIONS, Result


def _line(result: Result, eid: str) -> str:
    e = result.pack.get(eid)
    return f"- {e.statement} `[{eid}]`"


def render(result: Result) -> str:
    w = result.windows.as_dict()
    pack = result.pack
    out: list[str] = []
    add = out.append

    add("# Growth Agent: analysis report")
    add("")
    add(
        f"Reporting week **{w['reporting_week'][0]} to {w['reporting_week'][1]}**, compared with "
        f"{w['prior_week'][0]} to {w['prior_week'][1]}. Data source: `{result.dataset.source_name}`"
        + (" (synthetic sample data, not Harvey performance)." if result.dataset.is_synthetic else ".")
    )
    add("")
    add(
        "Every line ends with the id of the evidence item it came from. Numbers are computed by code, "
        "not written by a model. This report is the input to the Weekly Experimentation Brief, not the brief itself."
    )

    add("\n## 1. What happened last week\n")
    for eid in ["WEEK.totals", "WEEK.spend_bridge", "WEEK.same_store", "WEEK.by_platform", "WEEK.program_status"]:
        add(_line(result, eid))
    add("")
    add(f"What cannot be said yet: {pack.get('DQ.attribution_lag').statement} `[DQ.attribution_lag]`")

    add("\n### Campaigns live in the week\n")
    add("| Campaign | Platform | Offer | Theme | Audience | Days live | Spend | CTR | vs own baseline | Age (days) | Past fatigue point |")
    add("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in pack.get("WEEK.campaigns").data:
        delta = "n/a" if r["ctr_vs_baseline_pct"] is None else f"{r['ctr_vs_baseline_pct']:+.0f}%"
        add(
            f"| {r['campaign_id']} | {r['platform']} | {r['objective']} | {r['theme']} | {r['audience']} | "
            f"{r['days_live_in_week']} | ${r['spend']:,.0f} | {r['ctr_pct']:.2f}% | {delta} | {r['campaign_age_days']} | "
            f"{'yes' if r.get('past_fatigue_point') else 'no'} |"
        )

    add("\n## 2. Why it looks this way\n")
    for eid in [
        "BENCH.overall", "SEG.objective", "MIX.objective", "SEG.platform", "FUNNEL.platform", "ZERO.opportunities",
        "SEG.theme", "SEG.audience", "SEG.region", "FATIGUE.curve", "THEME.by_audience",
    ]:
        add(_line(result, eid))

    add("\n### Pipeline per dollar by platform and offer (settled campaigns)\n")
    po = pack.get("SEG.platform_objective").data
    offers = sorted(po["objective"].unique())
    add("| Platform | " + " | ".join(offers) + " |")
    add("|---|" + "---|" * len(offers))
    for plat, g in po.groupby("platform"):
        cells = g.set_index("objective")
        add(f"| {plat} | " + " | ".join(
            f"${cells.loc[o, 'pipeline_per_dollar']:,.0f} ({cells.loc[o, 'spend_share'] * 100:.0f}% of spend)" if o in cells.index else "n/a"
            for o in offers) + " |")

    add("\n## 3. What the experiment log can and cannot support\n")
    add(_line(result, "EXP.summary"))
    add("")
    add("| Test | Platform | Hypothesis | Logged | Days | Sample | Metric | Agent rating | Campaign data |")
    add("|---|---|---|---|---|---|---|---|---|")
    for e in result.experiments:
        add(
            f"| {e['experiment_id']} | {e['platform']} | {e['hypothesis']} | {e['logged_result']} {e['logged_lift_pct']:+.0f}% "
            f"({e['logged_confidence']}) | {e['runtime_days']} | {e['sample_size']} | {e['primary_metric']} | "
            f"**{e['tier']}** | {e['observed']['verdict']} |"
        )

    add("\n## 4. Ranked signals: where a test would pay off\n")
    add("Signals are inputs to experiment design, not experiments. Ranked by strength of evidence, then size.\n")
    for s in result.signals:
        add(f"**{s['rank']}. {s['title']}** ({s['strength']}) `[{s['id']}]`")
        add(f"{s['statement']}")
        add(f"- Test angle: {s['test_angle']}")
        for c in s["cautions"]:
            add(f"- Caution: {c}")
        add(f"- Evidence: {', '.join(s['evidence_ids'])}")
        add("")

    add("## 5. Creative\n")
    for eid in ["CREATIVE.gaps", "CREATIVE.performance"]:
        add(_line(result, eid))

    add("\n## 6. Data quality: what is wrong and how it is handled\n")
    for e in pack.items():
        if e.id.startswith("DQ."):
            add(f"- **{e.title}.** {e.statement} `[{e.id}]`")
            for c in e.caveats:
                add(f"  - {c}")

    add("\n## 7. Assumptions\n")
    for a in ASSUMPTIONS:
        add(f"- **{a['id']}.** {a['assumption']} *Why:* {a['why']} *If wrong:* {a['if_wrong']}")

    add("")
    return "\n".join(out)
