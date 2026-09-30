"""Opportunity signals: what the evidence says is worth testing.

A signal is not an experiment. It is a ranked, evidence-linked observation
("this segment underperforms like for like, in every cell, on a large share of
spend"). The reasoning layer turns signals into experiment designs, and the
guardrails check those designs. Keeping the three steps separate means the
model never decides what is true, only what to do about it.
"""
from __future__ import annotations

import pandas as pd

from ..config import Config
from ..connectors.base import Dataset
from ..evidence import EvidencePack
from .metrics import safe_div, summarize, totals
from .windows import Windows

STRENGTH_ORDER = {"strong": 0, "moderate": 1, "context": 2}


def _recent_share(d: pd.DataFrame, w: Windows, cfg: Config, dim: str, value: str) -> float | None:
    start = w.as_of - pd.Timedelta(days=cfg.recent_weeks * 7 - 1)
    recent = d[d["date"] >= start]
    if dim not in recent.columns:
        return None
    return safe_div(recent.loc[recent[dim] == value, "spend"].sum(), recent["spend"].sum())


def detect(ds: Dataset, w: Windows, cfg: Config, pack: EvidencePack, ctx: dict, exps: list[dict]) -> list[dict]:
    d, c = ds.daily, ds.campaigns
    bench: pd.DataFrame = ctx["bench"]
    tables: dict[str, pd.DataFrame] = ctx["tables"]
    total_pipeline = float(bench["pipeline"].sum())
    signals: list[dict] = []

    def related(dim: str, value: str) -> tuple[list[str], list[str]]:
        usable, rejected = [], []
        for e in exps:
            p = e["parsed"]
            if p and p["dimension"] == dim and value in (p["a"], p["b"]):
                (usable if e["usable_as_evidence"] else rejected).append(e["experiment_id"])
        return usable, rejected

    # 1. Segments that beat or trail comparable campaigns everywhere ------------
    for dim, t in tables.items():
        for r in t.itertuples():
            idx = r.adjusted_index
            if not r.enough_data or r.direction not in ("above", "below") or idx is None:
                continue
            if cfg.gap_index_low < idx < cfg.gap_index_high:
                continue
            value = getattr(r, dim)
            gap_share = safe_div(r.pipeline - r.expected_pipeline, total_pipeline)
            recent = _recent_share(d, w, cfg, dim, value)
            usable, rejected = related(dim, value)
            below = r.direction == "below"
            signals.append(
                {
                    "type": "segment_underperforms" if below else "segment_outperforms",
                    "title": f"{value} {'trails' if below else 'beats'} comparable campaigns",
                    "statement": (
                        f"{value} ({dim}) returns {idx:.2f}x the pipeline of comparable campaigns, "
                        f"{'below' if below else 'above'} benchmark in all {r.cells_evaluated} cells with enough spend. "
                        f"It takes {r.spend_share * 100:.0f}% of settled spend"
                        + (f" and {recent * 100:.0f}% of the last {cfg.recent_weeks} weeks' spend" if recent is not None else "")
                        + f". Like for like, that is pipeline worth {abs(gap_share) * 100:.0f}% of the program total "
                        f"{'not realized' if below else 'gained'} (modeled)."
                    ),
                    "evidence_ids": [f"SEG.{dim}", "SEG.platform_objective"] + [f"EXP.{i}" for i in usable],
                    "rejected_experiments_on_topic": rejected,
                    "strength": "strong" if r.cells_evaluated >= 3 else "moderate",
                    "size": abs(gap_share or 0),
                    "metrics": {
                        "dimension": dim,
                        "value": value,
                        "adjusted_index": idx,
                        "spend_share": r.spend_share,
                        "recent_spend_share": recent,
                        "pipeline_gap_share_modeled": gap_share,
                        "cells_evaluated": r.cells_evaluated,
                    },
                    "test_angle": (
                        f"Controlled test that moves budget away from {value} toward the stronger alternative, measured on pipeline per dollar."
                        if below
                        else f"Controlled test that scales {value} against the current mix, measured on pipeline per dollar."
                    ),
                    "cautions": ["Observational gap. Confirms where to test, not the size of the win."],
                }
            )

    # 2. Budget that moved toward a weaker offer ----------------------------------
    mix = pack.get("MIX.objective").data["shifts"]
    cell = summarize(bench, ["platform", "objective"]).set_index(["platform", "objective"])["pipeline_per_dollar"].to_dict()
    for platform, g in mix.groupby("platform"):
        up, down = g.loc[g["change_points"].idxmax()], g.loc[g["change_points"].idxmin()]
        if up["change_points"] < cfg.mix_shift_points or down["change_points"] > -cfg.mix_shift_points:
            continue
        ratio = safe_div(cell.get((platform, down["objective"]), 0), cell.get((platform, up["objective"]), 0))
        if ratio is None or ratio <= 1:
            continue
        false_winners = [
            e["experiment_id"]
            for e in exps
            if e["overturned"] and e["parsed"] and e["parsed"]["dimension"] == "objective"
            and e["platform"] == platform and e["parsed"]["a"] == up["objective"]
        ]
        signals.append(
            {
                "type": "budget_moved_to_weaker_offer",
                "title": f"{platform} budget moved from {down['objective']} to {up['objective']}",
                "statement": (
                    f"In the last {cfg.recent_weeks} weeks {platform} {down['objective']} fell from {down['earlier']:.0f}% to "
                    f"{down['recent']:.0f}% of platform spend while {up['objective']} rose from {up['earlier']:.0f}% to "
                    f"{up['recent']:.0f}%. In settled campaigns {platform} {down['objective']} returns {ratio:.1f}x the pipeline "
                    f"per dollar of {platform} {up['objective']}."
                    + (f" The only test favoring {up['objective']} ({', '.join(false_winners)}) is rejected as a false winner." if false_winners else "")
                ),
                "evidence_ids": ["MIX.objective", "SEG.platform_objective", "SEG.objective"] + [f"EXP.{i}" for i in false_winners],
                "rejected_experiments_on_topic": false_winners,
                "strength": "strong",
                "size": 1.0,  # ranked first: it is both the largest gap and the most recent decision
                "metrics": {
                    "platform": platform,
                    "offer_down": down["objective"],
                    "offer_up": up["objective"],
                    "share_down": [float(down["earlier"]), float(down["recent"])],
                    "share_up": [float(up["earlier"]), float(up["recent"])],
                    "efficiency_ratio": ratio,
                },
                "test_angle": f"Head-to-head {down['objective']} vs {up['objective']} on {platform}, same audience and theme, read on pipeline per dollar after attribution settles.",
                "cautions": ["The mix shift is a fact. Why it happened is not in the data."],
            }
        )

    # 3. Logged wins that should not drive decisions -------------------------------
    for e in exps:
        if not e["overturned"]:
            continue
        signals.append(
            {
                "type": "false_winner",
                "title": f"{e['experiment_id']} is logged as a {e['logged_result'].lower()} but is not a valid read",
                "statement": pack.get(f"EXP.{e['experiment_id']}").statement,
                "evidence_ids": [f"EXP.{e['experiment_id']}", "EXP.summary"],
                "rejected_experiments_on_topic": [e["experiment_id"]],
                "strength": "strong" if e["observed"]["verdict"] == "disagrees" else "moderate",
                "size": 0.5 if e["observed"]["verdict"] == "disagrees" else 0.1,
                "metrics": {"runtime_days": e["runtime_days"], "sample_size": e["sample_size"], "observed": e["observed"]["verdict"]},
                "test_angle": f"Re-run '{e['hypothesis']}' at full length and sample on an outcome metric before acting on it.",
                "cautions": ["Until re-run, this result should be removed from the team's list of learnings."],
            }
        )

    # 4. Learnings that need confirmation -----------------------------------------
    unconfirmed = []
    for e in exps:
        if e["tier"] == "rejected" or (e["replicates"] and e["tier"] == "trusted"):
            continue
        disagrees = e["observed"]["verdict"] == "disagrees"
        if e["tier"] == "directional" and (str(e["logged_result"]).lower() in ("win", "loss") or disagrees):
            unconfirmed.append({"experiment_id": e["experiment_id"], "hypothesis": e["hypothesis"], "why": "; ".join(e["reasons"]), "campaign_data": e["observed"]["verdict"]})
        elif e["tier"] == "trusted" and disagrees:
            unconfirmed.append({"experiment_id": e["experiment_id"], "hypothesis": e["hypothesis"], "why": "valid test, but settled campaign data points the other way", "campaign_data": "disagrees"})
    if unconfirmed:
        conflict = [u for u in unconfirmed if u["campaign_data"] == "disagrees"]
        signals.append(
            {
                "type": "unconfirmed_learnings",
                "title": "Learnings the team is relying on that are not confirmed",
                "statement": (
                    f"{len(unconfirmed)} experiments are usable only as direction ({', '.join(u['experiment_id'] for u in unconfirmed)}). "
                    f"Settled campaign data points the other way on {', '.join(u['experiment_id'] for u in conflict) or 'none'}."
                ),
                "evidence_ids": [f"EXP.{u['experiment_id']}" for u in unconfirmed],
                "rejected_experiments_on_topic": [],
                "strength": "moderate",
                "size": 0.05 * len(conflict),
                "metrics": {"experiments": unconfirmed},
                "test_angle": "A confirmation test for whichever of these the next quarter's plan depends on most.",
                "cautions": ["Disagreement with observational data is a reason to re-test, not proof the experiment was wrong."],
            }
        )

    # 5. Creative fatigue -----------------------------------------------------------
    fat = ctx["fatigue"]
    for x in fat["exposure"]:
        o = fat["onset"][x["platform"]]
        signals.append(
            {
                "type": "creative_fatigue",
                "title": f"{x['platform']} creative wears out after week {o['week'] - 1}",
                "statement": (
                    f"{x['platform']} CTR holds for {o['week'] - 1} weeks of a campaign's life and is at "
                    f"{o['last_index'] * 100:.0f}% of launch level by week {o['last_week']}. {x['campaigns_past_onset']} campaigns "
                    f"ran past that point, putting ${x['spend_past_onset']:,.0f} "
                    f"({x['share_of_platform_spend'] * 100:.0f}% of {x['platform']} spend) behind tired creative."
                ),
                "evidence_ids": ["FATIGUE.curve", "DQ.creative_age"],
                "rejected_experiments_on_topic": [],
                "strength": "strong",
                "size": (x["share_of_platform_spend"] or 0) * (1 - o["last_index"]) * 0.5,
                "metrics": {**x, "onset_week": o["week"], "onset_day": o["day"]},
                "test_angle": f"Rotate in a fresh creative at day {o['day'] - 1} versus letting the original run, on {x['platform']}.",
                "cautions": ["Fatigue is measured on CTR. Whether it carries through to pipeline is untested."],
            }
        )

    # 6. Lead quality ------------------------------------------------------------------
    pt = tables["platform"].set_index("platform")
    best_ql = pt["ql_rate"].max()
    for p, r in pt.iterrows():
        if r["ql_rate"] <= cfg.lead_quality_ratio * best_ql:
            flagged = int(c.loc[c["platform"] == p, "data_quality_flag"].fillna("").str.contains("low quality").sum())
            signals.append(
                {
                    "type": "lead_quality",
                    "title": f"{p} buys cheap leads that do not qualify",
                    "statement": (
                        f"{p} has the lowest cost per lead (${r['cpl']:,.0f}) but only {r['ql_rate'] * 100:.0f}% of its leads "
                        f"qualify, against {best_ql * 100:.0f}% on {pt['ql_rate'].idxmax()}. "
                        f"{flagged} of its campaigns carry the source's 'High volume / low quality' flag."
                    ),
                    "evidence_ids": ["FUNNEL.platform", "DQ.source_flags"] + [f"EXP.{e['experiment_id']}" for e in exps if e["usable_as_evidence"] and "targeted" in e["hypothesis"].lower()],
                    "rejected_experiments_on_topic": [],
                    "strength": "moderate",
                    "size": float(r["spend_share"]) * (1 - r["ql_rate"] / best_ql) * 0.2,
                    "metrics": {"platform": p, "cpl": r["cpl"], "ql_rate": r["ql_rate"], "best_ql_rate": best_ql, "flagged_campaigns": flagged},
                    "test_angle": f"Tighter targeting or a qualifying step on {p}, judged on cost per opportunity rather than cost per lead.",
                    "cautions": ["A lower lead volume is the expected and acceptable cost of this test."],
                }
            )

    # 7. Spend that produced nothing -----------------------------------------------------
    zero = pack.get("ZERO.opportunities").data
    for r in zero["by_platform"].itertuples():
        n = int((bench["platform"] == r.platform).sum())
        if r.campaigns / n < 0.25:
            continue
        signals.append(
            {
                "type": "zero_outcome_spend",
                "title": f"{r.campaigns} of {n} {r.platform} campaigns produced no opportunities",
                "statement": (
                    f"{r.campaigns} of {n} settled {r.platform} campaigns produced zero opportunities on ${r.spend:,.0f} of spend."
                ),
                "evidence_ids": ["ZERO.opportunities", "SEG.platform", "SEG.platform_objective"],
                "rejected_experiments_on_topic": [],
                "strength": "strong",
                "size": safe_div(r.spend, bench["spend"].sum()) or 0,
                "metrics": {"platform": r.platform, "campaigns": int(r.campaigns), "of": n, "spend": float(r.spend)},
                "test_angle": f"Holdout test of {r.platform}'s real contribution before cutting it, since last-touch attribution can hide influence on enterprise deals.",
                "cautions": ["Do not read this as 'turn the channel off'. Read it as 'prove what it contributes'."],
            }
        )

    # 8. Under-tested themes ---------------------------------------------------------------
    tt = tables["theme"].set_index("theme")
    flagged_themes = c.loc[c["data_quality_flag"].fillna("").str.contains("Under-tested"), "theme"].unique()
    for theme in flagged_themes:
        valid = [e["experiment_id"] for e in exps if e["theme"] == theme and e["usable_as_evidence"]]
        invalid = [e["experiment_id"] for e in exps if e["theme"] == theme and not e["usable_as_evidence"]]
        r = tt.loc[theme]
        gaps = pack.get("CREATIVE.gaps").data["format_gaps"]
        missing = sorted({f for row in gaps[gaps["theme"] == theme].itertuples() for f in row.missing_formats})
        signals.append(
            {
                "type": "under_tested_theme",
                "title": f"{theme} has never had a valid test",
                "statement": (
                    f"{theme} has {int(r['campaigns'])} settled campaigns on {r['spend_share'] * 100:.0f}% of spend and "
                    f"{len(valid)} valid experiments ({', '.join(invalid) or 'none'} rejected). Its campaigns return "
                    f"{r['adjusted_index']:.2f}x comparable campaigns"
                    + (f", and it exists only in {', '.join(sorted(ds.creatives.loc[ds.creatives['theme'] == theme, 'format'].unique()))} format" if missing else "")
                    + "."
                ),
                "evidence_ids": ["SEG.theme", "CREATIVE.gaps"] + [f"EXP.{i}" for i in invalid],
                "rejected_experiments_on_topic": invalid,
                "strength": "moderate",
                "size": 0.02,
                "metrics": {"theme": theme, "adjusted_index": r["adjusted_index"], "spend_share": r["spend_share"], "valid_experiments": len(valid), "missing_formats": missing},
                "test_angle": f"A small, properly powered read on {theme} before deciding whether to invest in more creative for it.",
                "cautions": [f"Current evidence says {theme} underperforms. This is an exploration bet, not a scaling bet." if r["adjusted_index"] < 1 else "Small base."],
            }
        )

    # 9. Creative that exists but has never run -----------------------------------------------
    unused = pack.get("CREATIVE.gaps").data["unused"]
    for r in unused.itertuples():
        signals.append(
            {
                "type": "unused_creative",
                "title": f"{r.creative_id} has never run",
                "statement": f"{r.creative_id} ({r.theme}, {r.format}, {r.audience_group}) is active in the library with zero campaigns.",
                "evidence_ids": ["CREATIVE.gaps", "THEME.by_audience"],
                "rejected_experiments_on_topic": [],
                "strength": "context",
                "size": 0.0,
                "metrics": {"creative_id": r.creative_id, "theme": r.theme, "format": r.format, "audience_group": r.audience_group},
                "test_angle": f"Use {r.creative_id} as the fresh variant in a rotation or format test for {r.audience_group} audiences.",
                "cautions": [],
            }
        )

    # 10. Nothing is scheduled -----------------------------------------------------------------
    status = pack.get("WEEK.program_status").data
    if not status["scheduled_after_as_of"]:
        signals.append(
            {
                "type": "clean_slate",
                "title": "No campaigns are scheduled past the reporting week",
                "statement": pack.get("WEEK.program_status").statement,
                "evidence_ids": ["WEEK.program_status", "WEEK.spend_bridge"],
                "rejected_experiments_on_topic": [],
                "strength": "context",
                "size": 0.0,
                "metrics": {"live_on_as_of": len(status["live_on_as_of"])},
                "test_angle": "Treat the next launches as the experiment slate. Every new campaign can carry a test cell at no extra cost.",
                "cautions": [],
            }
        )

    signals.sort(key=lambda s: (STRENGTH_ORDER[s["strength"]], -s["size"]))
    for i, s in enumerate(signals, 1):
        s["id"] = f"SIG.{i:02d}"
        s["rank"] = i
        pack.add(
            s["id"],
            s["title"],
            s["statement"],
            "derived from " + ", ".join(s["evidence_ids"]),
            "modeled" if s["type"].startswith("segment_") else "observational",
            data={k: s[k] for k in ("type", "strength", "metrics", "evidence_ids", "test_angle", "cautions", "rejected_experiments_on_topic")},
            caveats=s["cautions"],
        )
    return signals
