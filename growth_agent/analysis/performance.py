"""What happened last week.

Reports only what the data can support for a week that sits entirely inside
the attribution lag window: delivery and lead capture are final, everything
further down the funnel is provisional.
"""
from __future__ import annotations

import pandas as pd

from ..config import Config
from ..connectors.base import Dataset
from ..evidence import EvidencePack
from .metrics import pct_change, safe_div, totals
from .windows import Windows

FINAL_METRICS = ["spend", "impressions", "clicks", "ctr_pct", "cpc", "conversions", "cpl"]
PROVISIONAL_METRICS = ["qualified_leads", "opportunities", "pipeline"]


def _fmt_change(v: float | None) -> str:
    return "n/a" if v is None else f"{v:+.0f}%"


def _money(v: float) -> str:
    """Signed dollars, written the way a person would: -$19,126."""
    return f"{'-' if v < 0 else '+'}${abs(v):,.0f}"


def _compare(this: pd.DataFrame, prior: pd.DataFrame) -> dict:
    a, b = totals(this), totals(prior)
    out = {}
    for m in FINAL_METRICS + PROVISIONAL_METRICS:
        out[m] = {
            "this_week": a[m],
            "prior_week": b[m],
            "change_pct": pct_change(a[m], b[m]),
            "reliability": "final" if m in FINAL_METRICS else "provisional",
        }
    out["campaigns"] = {"this_week": a["campaigns"], "prior_week": b["campaigns"]}
    return out


def what_happened(ds: Dataset, w: Windows, cfg: Config, pack: EvidencePack) -> None:
    d, c = ds.daily, ds.campaigns
    this, prior = d[w.in_week(d["date"])], d[w.in_prior(d["date"])]

    # ---- Headline totals ----------------------------------------------------
    head = _compare(this, prior)
    pack.add(
        "WEEK.totals",
        "Reporting week versus prior week",
        (
            f"In the week of {w.week_start:%b %d} to {w.week_end:%b %d}, {head['campaigns']['this_week']} campaigns "
            f"spent ${head['spend']['this_week']:,.0f} ({_fmt_change(head['spend']['change_pct'])} vs the prior week's "
            f"${head['spend']['prior_week']:,.0f} across {head['campaigns']['prior_week']} campaigns), producing "
            f"{int(head['clicks']['this_week']):,} clicks ({_fmt_change(head['clicks']['change_pct'])}) and "
            f"{int(head['conversions']['this_week'])} conversions ({_fmt_change(head['conversions']['change_pct'])})."
        ),
        "daily_campaign_performance",
        "final",
        data=head,
        caveats=[
            "Qualified leads, opportunities and pipeline for both weeks are provisional (see DQ.attribution_lag).",
            "Daily conversion counts are a partial view (see DQ.reconciliation). Week-over-week direction is valid; absolute levels are not comparable with the campaign summary.",
        ],
    )

    # ---- Why spend moved: the bridge ---------------------------------------
    days = lambda x: x.groupby("campaign_id")["date"].nunique()
    td, pd_ = days(this), days(prior)
    ids = sorted(set(td.index) | set(pd_.index))
    groups: dict[str, list[str]] = {"full_week": [], "ended_or_ending": [], "launched": []}
    for cid in ids:
        if td.get(cid, 0) == cfg.week_days and pd_.get(cid, 0) == cfg.week_days:
            groups["full_week"].append(cid)
        elif pd_.get(cid, 0) == 0:
            groups["launched"].append(cid)
        else:
            groups["ended_or_ending"].append(cid)

    bridge = {}
    for name, members in groups.items():
        a = float(this.loc[this["campaign_id"].isin(members), "spend"].sum())
        b = float(prior.loc[prior["campaign_id"].isin(members), "spend"].sum())
        bridge[name] = {"campaigns": members, "this_week": a, "prior_week": b, "change": a - b}
    total_change = head["spend"]["this_week"] - head["spend"]["prior_week"]
    ended_share = safe_div(bridge["ended_or_ending"]["change"], total_change)
    pack.add(
        "WEEK.spend_bridge",
        "Why spend changed",
        (
            f"Spend moved {_money(total_change)} week over week. {len(groups['ended_or_ending'])} campaigns that ended or "
            f"wound down account for {_money(bridge['ended_or_ending']['change'])} of it "
            f"({(ended_share or 0) * 100:.0f}%); the {len(groups['full_week'])} campaigns live all 14 days moved "
            f"{_money(bridge['full_week']['change'])}; {len(groups['launched'])} campaigns launched."
        ),
        "daily_campaign_performance",
        "final",
        data=bridge,
    )

    # ---- Like-for-like: campaigns live through both weeks -------------------
    fw = groups["full_week"]
    same = _compare(this[this["campaign_id"].isin(fw)], prior[prior["campaign_id"].isin(fw)])
    pack.add(
        "WEEK.same_store",
        "Like-for-like performance",
        (
            f"For the {len(fw)} campaigns live through both weeks, spend was {_fmt_change(same['spend']['change_pct'])}, "
            f"CTR moved from {same['ctr_pct']['prior_week']:.2f}% to {same['ctr_pct']['this_week']:.2f}% "
            f"({_fmt_change(same['ctr_pct']['change_pct'])}) and conversions went from "
            f"{int(same['conversions']['prior_week'])} to {int(same['conversions']['this_week'])}."
        ),
        "daily_campaign_performance",
        "final",
        data=same,
        caveats=["This is the fair read of week-over-week performance because it removes campaigns that ended."],
    )

    # ---- By platform ---------------------------------------------------------
    no_feed = set(pack.get("DQ.daily_outcome_gaps").data["campaigns_missing_daily_conversions"])
    rows = []
    for p in sorted(d["platform"].unique()):
        cmp = _compare(this[this["platform"] == p], prior[prior["platform"] == p])
        live_ids = set(this.loc[this["platform"] == p, "campaign_id"])
        rows.append(
            {
                "platform": p,
                "conversions_reported": not (live_ids and live_ids <= no_feed),
                "campaigns": cmp["campaigns"]["this_week"],
                "spend": cmp["spend"]["this_week"],
                "spend_change_pct": cmp["spend"]["change_pct"],
                "ctr_pct": cmp["ctr_pct"]["this_week"],
                "ctr_prior_pct": cmp["ctr_pct"]["prior_week"],
                "conversions": cmp["conversions"]["this_week"],
                "conversions_prior": cmp["conversions"]["prior_week"],
                "cpl": cmp["cpl"]["this_week"],
            }
        )
    pack.add(
        "WEEK.by_platform",
        "Reporting week by platform",
        "; ".join(
            f"{r['platform']}: ${r['spend']:,.0f} across {r['campaigns']} campaigns, CTR {r['ctr_pct']:.2f}%, "
            + (f"{int(r['conversions'])} conversions" if r["conversions_reported"] else "conversions not reported in the daily feed")
            for r in rows
        )
        + ".",
        "daily_campaign_performance",
        "final",
        data=rows,
        caveats=["A platform showing zero conversions may have no daily outcome feed (see DQ.daily_outcome_gaps)."],
    )

    # ---- Campaign detail -------------------------------------------------------
    base_start = w.prior_start - pd.Timedelta(days=cfg.baseline_days)
    meta = c.set_index("campaign_id")
    detail = []
    for cid in sorted(this["campaign_id"].unique()):
        x = this[this["campaign_id"] == cid]
        b = d[(d["campaign_id"] == cid) & (d["date"] >= base_start) & (d["date"] < w.week_start)]
        ctr = safe_div(x["clicks"].sum(), x["impressions"].sum())
        ctr_b = safe_div(b["clicks"].sum(), b["impressions"].sum())
        m = meta.loc[cid]
        detail.append(
            {
                "campaign_id": cid,
                "platform": m["platform"],
                "objective": m["objective"],
                "theme": m["theme"],
                "audience": m["audience"],
                "region": m["region"],
                "creative_id": m["creative_id"],
                "days_live_in_week": int(x["date"].nunique()),
                "spend": float(x["spend"].sum()),
                "ctr_pct": None if ctr is None else ctr * 100,
                "ctr_baseline_pct": None if ctr_b is None else ctr_b * 100,
                "ctr_vs_baseline_pct": pct_change(ctr, ctr_b),
                "conversions": int(x["conversions"].sum()),
                "campaign_age_days": int(x["creative_age_days"].max()),
                "end_date": m["end_date"],
                "source_flags": m["data_quality_flag"],
            }
        )
    pack.add(
        "WEEK.campaigns",
        "Campaigns live in the reporting week",
        f"{len(detail)} campaigns were live: " + ", ".join(
            f"{r['campaign_id']} ({r['platform']} {r['objective']}, {r['theme']})" for r in detail
        ) + ".",
        "daily_campaign_performance + campaign_summary",
        "final",
        data=detail,
        caveats=[f"CTR baseline is each campaign's own prior {cfg.baseline_days + cfg.week_days} days."],
    )

    # ---- Program status: is anything still running? ----------------------------
    live_on_last_day = sorted(d.loc[d["date"] == w.as_of, "campaign_id"].unique())
    running_after = c[c["end_date"] > w.as_of]
    objectives = meta.loc[[r["campaign_id"] for r in detail], "objective"].value_counts().to_dict()
    weekly = []
    end = w.as_of
    while end - pd.Timedelta(days=cfg.week_days - 1) >= d["date"].min():
        start = end - pd.Timedelta(days=cfg.week_days - 1)
        x = d[(d["date"] >= start) & (d["date"] <= end)]
        weekly.append(
            {"week_start": start, "week_end": end, "spend": float(x["spend"].sum()), "campaigns": int(x["campaign_id"].nunique())}
        )
        end = start - pd.Timedelta(days=1)
    weekly = weekly[::-1]
    peak = max(weekly, key=lambda r: r["spend"])
    pack.add(
        "WEEK.program_status",
        "The program is winding down",
        (
            f"{len(live_on_last_day)} campaigns were still live on {w.as_of:%b %d} and {len(running_after)} are scheduled "
            f"to run past it. Weekly spend is ${head['spend']['this_week']:,.0f}, down "
            f"{abs(pct_change(head['spend']['this_week'], peak['spend']) or 0):.0f}% from the peak week of "
            f"{peak['week_start']:%b %d} (${peak['spend']:,.0f}, {peak['campaigns']} campaigns). "
            f"The {len(detail)} campaigns live this week were "
            + ", ".join(f"{n} {k}" for k, n in objectives.items()) + "."
        ),
        "daily_campaign_performance + campaign_summary",
        "final",
        data={
            "live_on_as_of": live_on_last_day,
            "scheduled_after_as_of": running_after["campaign_id"].tolist(),
            "weekly_spend": weekly,
            "peak_week": peak,
            "objective_mix_this_week": objectives,
        },
        caveats=["With nothing scheduled, the next set of launches is a clean slate. What gets tested next is also what gets funded next."],
    )
