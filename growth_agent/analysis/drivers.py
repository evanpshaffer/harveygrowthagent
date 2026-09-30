"""Why performance looks the way it does.

Efficiency findings use the campaign summary (the reconciled record) and only
campaigns whose attribution has settled. Every segment comparison is also
re-run inside platform and offer type, because those two factors dominate the
data and would otherwise masquerade as theme, audience or region effects.
"""
from __future__ import annotations

import pandas as pd

from ..config import Config
from ..connectors.base import Dataset
from ..evidence import EvidencePack
from .metrics import safe_div, summarize, totals
from .quality import immature_flag
from .windows import Windows

# Which other factors to hold constant when judging each dimension.
CONTROLS = {
    "platform": ["objective"],
    "objective": ["platform"],
    "theme": ["platform", "objective"],
    "audience": ["platform", "objective"],
    "region": ["platform", "objective"],
    "creative_id": ["platform", "objective"],
}


def benchmark(campaigns: pd.DataFrame) -> pd.DataFrame:
    """Campaigns with settled attribution: the only fair basis for efficiency."""
    return campaigns[~immature_flag(campaigns)].copy()


def adjusted_index(bench: pd.DataFrame, dim: str | list[str], controls: list[str], cfg: Config) -> pd.DataFrame:
    """Efficiency of each segment relative to like-for-like campaigns.

    Observed over expected. For every control cell (for example Google x
    Webinar) the segment's spend is multiplied by the cell's overall pipeline
    per dollar to get the pipeline that spend would normally produce. The
    index is the segment's actual pipeline divided by that expectation, so
    1.0 means "performs like comparable campaigns". Summing pipeline before
    dividing keeps near-zero cells (LinkedIn) from dominating the result.
    """
    dims = [dim] if isinstance(dim, str) else list(dim)
    if not controls:
        t = summarize(bench, dims)
        overall = totals(bench)["pipeline_per_dollar"]
        t["adjusted_index"] = t["pipeline_per_dollar"] / overall
        t["expected_pipeline"] = t["spend"] * overall
        t["cells_evaluated"], t["cells_above_benchmark"], t["direction"] = 1, (t["adjusted_index"] > 1).astype(int), "n/a"
        return t[dims + ["adjusted_index", "expected_pipeline", "cells_evaluated", "cells_above_benchmark", "direction"]]

    cell_bench = summarize(bench, controls).set_index(controls)["pipeline_per_dollar"].to_dict()
    cells = summarize(bench, controls + dims)
    keys = cells[controls].apply(tuple, axis=1) if len(controls) > 1 else cells[controls[0]]
    cells["expected_pipeline"] = cells["spend"] * keys.map(cell_bench)
    cells["ratio"] = cells["pipeline"] / cells["expected_pipeline"].where(cells["expected_pipeline"] > 0)

    rows = []
    for key, g in cells.groupby(dims, observed=True):
        solid = g[(g["spend"] >= cfg.min_segment_spend) & g["ratio"].notna()]
        above = int((solid["ratio"] > 1).sum())
        direction = "insufficient"
        if len(solid):
            direction = "above" if above == len(solid) else "below" if above == 0 else "mixed"
        row = dict(zip(dims, key if isinstance(key, tuple) else (key,)))
        row.update(
            {
                "adjusted_index": safe_div(g["pipeline"].sum(), g["expected_pipeline"].sum()),
                "expected_pipeline": float(g["expected_pipeline"].sum()),
                "cells_evaluated": int(len(solid)),
                "cells_above_benchmark": above,
                "direction": direction,
            }
        )
        rows.append(row)
    return pd.DataFrame(rows)


def segment_table(bench: pd.DataFrame, dim: str, cfg: Config) -> pd.DataFrame:
    """Raw efficiency by segment plus the like-for-like index."""
    t = summarize(bench, dim)
    overall = totals(bench)["pipeline_per_dollar"]
    t["raw_index"] = t["pipeline_per_dollar"] / overall
    t = t.merge(adjusted_index(bench, dim, CONTROLS[dim], cfg), on=dim, how="left")
    t["enough_data"] = (t["spend"] >= cfg.min_segment_spend) & (t["campaigns"] >= cfg.min_segment_campaigns)
    keep = [
        dim, "campaigns", "spend", "spend_share", "pipeline", "pipeline_share", "cpl", "ql_rate", "opp_rate",
        "cost_per_opp", "pipeline_per_dollar", "arr_per_dollar", "raw_index", "adjusted_index", "expected_pipeline",
        "direction", "cells_evaluated", "cells_above_benchmark", "enough_data",
    ]
    return t[keep]


def compare_arms(
    bench: pd.DataFrame,
    dim: str,
    a: str,
    b: str,
    platform: str | None = None,
    audience_group: str | None = None,
    cfg: Config | None = None,
) -> dict:
    """Observed efficiency of two values of one dimension, like for like.

    Holds platform and offer constant wherever the dimension allows it, so a
    theme or CTA is not credited with the channel it happened to run on.
    """
    from ..config import CONFIG

    cfg = cfg or CONFIG
    x = bench
    if platform:
        x = x[x["platform"] == platform]
    if audience_group:
        x = x[x["audience"].str.startswith(audience_group)]
    if dim == "format":
        x = x[x["platform"] != "Google"]  # Google's format field is an ad type

    controls = [k for k in ("platform", "objective") if k != dim and not (k == "platform" and platform)]
    idx = adjusted_index(x, dim, controls, cfg).set_index(dim)["adjusted_index"].to_dict() if len(x) else {}

    def arm(v: str) -> dict:
        t = totals(x[x[dim] == v])
        return {
            "value": v,
            "campaigns": t["campaigns"],
            "spend": t["spend"],
            "pipeline_per_dollar": t["pipeline_per_dollar"],
            "adjusted_index": idx.get(v),
        }

    ra, rb = arm(a), arm(b)
    return {
        "dimension": dim,
        "scope": {"platform": platform or "all", "audience_group": audience_group or "all"},
        "held_constant": controls,
        "a": ra,
        "b": rb,
        "ratio_a_over_b": safe_div(ra["adjusted_index"] or 0, rb["adjusted_index"] or 0),
    }


def _x(v: float | None) -> str:
    return "n/a" if v is None or pd.isna(v) else f"{v:.2f}x"


def why(ds: Dataset, w: Windows, cfg: Config, pack: EvidencePack) -> dict:
    c, d, cr = ds.campaigns, ds.daily, ds.creatives
    bench = benchmark(c)
    overall = totals(bench)
    caveat_obs = "Observational: campaigns were not randomized across segments. Use to decide what to test."
    caveat_scale = "Absolute pipeline-per-dollar values are synthetic. Read the ratios, not the dollars."

    pack.add(
        "BENCH.overall",
        "Benchmark population",
        (
            f"Efficiency benchmarks use {overall['campaigns']} campaigns with settled attribution "
            f"(${overall['spend']:,.0f} of spend, {int(overall['opportunities']):,} opportunities), blended "
            f"${overall['pipeline_per_dollar']:,.0f} of pipeline per dollar and ${overall['cost_per_opp']:,.0f} per opportunity. "
            f"{len(c) - overall['campaigns']} campaigns flagged immature are excluded."
        ),
        "campaign_summary",
        "final",
        data=overall,
        caveats=[caveat_scale],
    )

    # ---- Segment efficiency ---------------------------------------------------
    tables: dict[str, pd.DataFrame] = {}
    for dim in ["platform", "objective", "theme", "audience", "region"]:
        t = segment_table(bench, dim, cfg)
        tables[dim] = t
        ranked = t[t["enough_data"]].sort_values("adjusted_index", ascending=False)
        top, bottom = ranked.iloc[0], ranked.iloc[-1]
        controls = " x ".join(CONTROLS[dim])
        flat = cfg.gap_index_low < bottom["adjusted_index"] and top["adjusted_index"] < cfg.gap_index_high
        if flat:
            raw = t[t["enough_data"]]["raw_index"]
            statement = (
                f"No {dim} stands out once {controls} is held constant: like-for-like indexes run from "
                f"{_x(bottom['adjusted_index'])} ({bottom[dim]}) to {_x(top['adjusted_index'])} ({top[dim]}). "
                f"The raw spread of {_x(raw.min())} to {_x(raw.max())} comes from which platforms and offers each {dim} was given."
            )
        else:
            statement = (
                f"By {dim}, {top[dim]} returns ${top['pipeline_per_dollar']:,.0f} of pipeline per dollar "
                f"({_x(top['adjusted_index'])} comparable campaigns) on {top['spend_share'] * 100:.0f}% of spend, while "
                f"{bottom[dim]} returns ${bottom['pipeline_per_dollar']:,.0f} ({_x(bottom['adjusted_index'])}) on "
                f"{bottom['spend_share'] * 100:.0f}% of spend. {top[dim]} is above benchmark in "
                f"{top['cells_above_benchmark']} of {top['cells_evaluated']} {controls} cells with enough spend; "
                f"{bottom[dim]} is below in {bottom['cells_evaluated'] - bottom['cells_above_benchmark']} of {bottom['cells_evaluated']}."
            )
        pack.add(
            f"SEG.{dim}",
            f"Efficiency by {dim}",
            statement,
            "campaign_summary",
            "observational",
            data=t,
            caveats=[
                caveat_obs,
                caveat_scale,
                f"adjusted_index compares each segment with campaigns on the same {' and '.join(CONTROLS[dim])}.",
            ],
        )

    # ---- Platform x offer -------------------------------------------------------
    po = summarize(bench, ["platform", "objective"])
    pack.add(
        "SEG.platform_objective",
        "Efficiency by platform and offer",
        "; ".join(
            f"{r.platform} {r.objective}: ${r.pipeline_per_dollar:,.0f}/$ on ${r.spend:,.0f}"
            for r in po.sort_values(["platform", "objective"]).itertuples()
        )
        + ".",
        "campaign_summary",
        "observational",
        data=po[["platform", "objective", "campaigns", "spend", "spend_share", "opportunities", "cost_per_opp", "pipeline_per_dollar"]],
        caveats=[caveat_obs, caveat_scale],
    )

    # ---- Funnel shape by platform ------------------------------------------------
    fp = tables["platform"].set_index("platform")
    pack.add(
        "FUNNEL.platform",
        "Where each platform's funnel leaks",
        "; ".join(
            f"{p}: ${r['cpl']:,.0f} per lead, {r['ql_rate'] * 100:.0f}% qualify, {r['opp_rate'] * 100:.0f}% of those become "
            f"opportunities, ${r['cost_per_opp']:,.0f} per opportunity"
            for p, r in fp.sort_index().iterrows()
        )
        + ".",
        "campaign_summary",
        "observational",
        data=tables["platform"],
        caveats=[caveat_obs],
    )

    # ---- Are immature campaigns understated in the summary? ----------------------
    imm = c[immature_flag(c)]
    cell = summarize(bench, ["platform", "objective"]).set_index(["platform", "objective"])["pipeline_per_dollar"].to_dict()
    exp_pipe = sum(cell.get((r.platform, r.objective), 0) * r.spend for r in imm.itertuples())
    imm_index = safe_div(imm["pipeline"].sum(), exp_pipe)
    pack.add(
        "BENCH.immature_campaigns",
        "How far behind the immature campaigns are",
        (
            f"The {len(imm)} campaigns flagged immature (${imm['spend'].sum():,.0f} of spend) currently show "
            f"{_x(imm_index)} the pipeline of settled campaigns on the same platform and offer."
        ),
        "campaign_summary",
        "provisional",
        data={"campaigns": imm["campaign_id"].tolist(), "spend": float(imm["spend"].sum()), "index_vs_settled": imm_index},
        caveats=["These campaigns stay out of benchmarks until their attribution settles."],
    )

    # ---- Offer mix over time (spend is fully reconciled, so this is final) -------
    recent_start = w.as_of - pd.Timedelta(days=cfg.recent_weeks * 7 - 1)
    dd = d.assign(period=(d["date"] >= recent_start).map({True: "recent", False: "earlier"}))
    piv = dd.pivot_table(index=["platform", "objective"], columns="period", values="spend", aggfunc="sum", fill_value=0.0)
    piv = piv.div(piv.groupby(level=0).transform("sum")).mul(100).reset_index()
    piv["change_points"] = piv["recent"] - piv["earlier"]
    monthly = d.assign(month=d["date"].dt.strftime("%Y-%m")).pivot_table(
        index=["platform", "month"], columns="objective", values="spend", aggfunc="sum", fill_value=0.0
    )
    monthly = monthly.div(monthly.sum(axis=1), axis=0).mul(100).reset_index()
    shifts = piv[piv["change_points"].abs() >= cfg.mix_shift_points].sort_values("change_points")
    pack.add(
        "MIX.objective",
        "Offer mix shifted in the last eight weeks",
        (
            "; ".join(
                f"{r.platform} {r.objective} went from {r.earlier:.0f}% to {r.recent:.0f}% of platform spend"
                for r in shifts.itertuples()
            )
            + f" (last {cfg.recent_weeks} weeks versus everything earlier)."
        )
        if len(shifts)
        else f"No offer's share of platform spend moved more than {cfg.mix_shift_points:.0f} points in the last {cfg.recent_weeks} weeks.",
        "daily_campaign_performance",
        "final",
        data={"recent_window_start": recent_start, "shifts": piv, "monthly_share_pct": monthly},
    )

    # ---- Campaigns that produced nothing -------------------------------------------
    zero = bench[bench["opportunities"] == 0]
    zp = zero.groupby("platform").agg(campaigns=("campaign_id", "count"), spend=("spend", "sum")).reset_index()
    n_by_platform = bench.groupby("platform")["campaign_id"].count().to_dict()
    pack.add(
        "ZERO.opportunities",
        "Campaigns with zero opportunities",
        (
            f"{len(zero)} settled campaigns produced no opportunities on ${zero['spend'].sum():,.0f} of spend: "
            + ", ".join(f"{r.platform} {r.campaigns} of {n_by_platform[r.platform]} (${r.spend:,.0f})" for r in zp.itertuples())
            + ". By offer: " + ", ".join(f"{n} {k}" for k, n in zero["objective"].value_counts().items()) + "."
        ),
        "campaign_summary",
        "final",
        data={"by_platform": zp, "campaign_ids": zero["campaign_id"].tolist(), "by_objective": zero["objective"].value_counts().to_dict()},
        caveats=["Platform attribution can under-credit channels that influence enterprise deals without capturing the last touch."],
    )

    # ---- Creative fatigue, measured inside each campaign -----------------------------
    fat = fatigue(d, cfg)
    onset = fat["onset"]
    parts = []
    for p, o in onset.items():
        parts.append(
            f"{p} CTR shows no decay with age" if o is None
            else f"{p} CTR holds for {o['week'] - 1} weeks, then slips to {o['index_at_onset'] * 100:.0f}% of its launch "
                 f"level in week {o['week']} and {o['last_index'] * 100:.0f}% by week {o['last_week']}"
        )
    pack.add(
        "FATIGUE.curve",
        "When creative wears out",
        "; ".join(parts) + ".",
        "daily_campaign_performance",
        "final",
        data=fat,
        caveats=[
            "Index = a campaign's CTR in that week of age divided by its own CTR in its first two weeks.",
            "Measured within campaigns, so platform and audience mix cannot cause it (see DQ.creative_age).",
        ],
    )

    for row in pack.get("WEEK.campaigns").data:
        o = onset.get(row["platform"])
        row["past_fatigue_point"] = bool(o and row["campaign_age_days"] >= o["day"])

    # ---- Weekday pattern ---------------------------------------------------------------
    wk = d.assign(weekend=d["date"].dt.dayofweek >= 5).groupby("weekend").agg(
        spend=("spend", "sum"), rows=("spend", "size"), clicks=("clicks", "sum"), impressions=("impressions", "sum")
    )
    per_day = wk["spend"] / wk["rows"]
    ratio = safe_div(per_day.get(True, 0), per_day.get(False, 0))
    pack.add(
        "SEASON.weekday",
        "Weekday pattern",
        f"Weekend spend per campaign-day runs at {ratio * 100:.0f}% of weekday spend, so comparisons use full 7-day windows.",
        "daily_campaign_performance",
        "final",
        data={"weekend_vs_weekday_spend_ratio": ratio},
    )

    # ---- Creative: usage, gaps, and performance ------------------------------------------
    used = c.groupby("creative_id").agg(
        campaigns=("campaign_id", "count"), platforms=("platform", "nunique"),
        first_launch=("launch_date", "min"), last_end=("end_date", "max"),
    )
    lib = cr.set_index("creative_id").join(used)
    lib["exposure_days"] = (lib["last_end"] - lib["first_launch"]).dt.days + 1
    unused = lib[lib["campaigns"].isna()]
    cov = cr.groupby(["theme", "audience_group"])["format"].agg(lambda s: sorted(set(s))).reset_index()
    all_formats = sorted(cr["format"].unique())
    cov["missing_formats"] = cov["format"].map(lambda have: [f for f in all_formats if f not in have])
    gaps = cov[cov["missing_formats"].map(len) > 0]
    pack.add(
        "CREATIVE.gaps",
        "Unused creative and format gaps",
        (
            (f"{len(unused)} active creative has never run: " + ", ".join(
                f"{i} ({r['theme']}, {r['format']}, {r['audience_group']})" for i, r in unused.iterrows()) + ". ")
            if len(unused) else "Every active creative has run. "
        )
        + (
            "Format gaps: " + "; ".join(
                f"{r.theme} for {r.audience_group} has no {' or '.join(r.missing_formats)}" for r in gaps.itertuples()) + "."
            if len(gaps) else "Every theme has every format."
        ),
        "creative_library + campaign_summary",
        "final",
        data={"unused": unused.reset_index()[["creative_id", "theme", "format", "audience_group"]], "format_gaps": gaps},
    )

    ct = summarize(bench, "creative_id").merge(adjusted_index(bench, "creative_id", CONTROLS["creative_id"], cfg), on="creative_id")
    ct = ct.merge(cr[["creative_id", "theme", "format", "audience_group"]], on="creative_id")
    ct = ct.merge(lib[["exposure_days"]].reset_index(), on="creative_id")
    ct = ct[["creative_id", "theme", "format", "audience_group", "campaigns", "spend", "pipeline_per_dollar",
             "adjusted_index", "direction", "exposure_days"]].sort_values("adjusted_index", ascending=False)
    solid = ct[ct["spend"] >= cfg.min_segment_spend]
    best, worst = solid.iloc[0], solid.iloc[-1]
    pack.add(
        "CREATIVE.performance",
        "Creative performance, like for like",
        (
            f"Against campaigns on the same platform and offer, {best['creative_id']} ({best['theme']} {best['format']}, "
            f"{best['audience_group']}) performs best at {_x(best['adjusted_index'])} and {worst['creative_id']} "
            f"({worst['theme']} {worst['format']}, {worst['audience_group']}) worst at {_x(worst['adjusted_index'])}."
        ),
        "campaign_summary + creative_library",
        "observational",
        data=ct,
        caveats=[caveat_obs, "Most creatives ran in only a few campaigns. Treat single-creative differences as leads, not conclusions."],
    )

    # ---- Theme by audience ------------------------------------------------------------------
    ta = summarize(bench, ["theme", "audience"]).merge(
        adjusted_index(bench, ["theme", "audience"], ["platform", "objective"], cfg), on=["theme", "audience"]
    )
    ta = ta[["theme", "audience", "campaigns", "spend", "pipeline_per_dollar", "adjusted_index", "direction"]]
    ta_solid = ta[(ta["spend"] >= cfg.min_segment_spend) & (ta["campaigns"] >= cfg.min_segment_campaigns)].sort_values(
        "adjusted_index", ascending=False
    )
    pack.add(
        "THEME.by_audience",
        "Which message works for which audience",
        (
            "Strongest pairings against comparable campaigns: "
            + ", ".join(f"{r.theme} for {r.audience} ({_x(r.adjusted_index)})" for r in ta_solid.head(3).itertuples())
            + ". Weakest: "
            + ", ".join(f"{r.theme} for {r.audience} ({_x(r.adjusted_index)})" for r in ta_solid.tail(3).itertuples())
            + "."
        ),
        "campaign_summary",
        "observational",
        data=ta.sort_values(["theme", "audience"]),
        caveats=[caveat_obs, f"Only pairings with at least {cfg.min_segment_campaigns} campaigns and ${cfg.min_segment_spend:,.0f} of spend are named."],
    )

    return {"bench": bench, "tables": tables, "fatigue": fat}


def fatigue(daily: pd.DataFrame, cfg: Config) -> dict:
    """Within-campaign CTR decay by week of age, per platform."""
    d = daily.copy()
    d["age_week"] = (d["creative_age_days"] - 1) // 7 + 1
    base = d[d["creative_age_days"] <= cfg.fatigue_baseline_days].groupby("campaign_id")[["impressions", "clicks"]].sum()
    base_ctr = (base["clicks"] / base["impressions"]).to_dict()
    d["expected_clicks"] = d["impressions"] * d["campaign_id"].map(base_ctr)
    g = d.groupby(["platform", "age_week"]).agg(
        campaigns=("campaign_id", "nunique"), clicks=("clicks", "sum"),
        expected_clicks=("expected_clicks", "sum"), spend=("spend", "sum"),
    ).reset_index()
    g["ctr_index"] = g["clicks"] / g["expected_clicks"]
    g["evaluated"] = g["campaigns"] >= cfg.fatigue_min_campaigns

    onset: dict[str, dict | None] = {}
    exposure = []
    baseline_weeks = cfg.fatigue_baseline_days // 7
    for p, x in g.groupby("platform"):
        ev = x[x["evaluated"] & (x["age_week"] > baseline_weeks)].sort_values("age_week")
        found = None
        for i, row in enumerate(ev.itertuples()):
            rest = ev.iloc[i:]
            if (rest["ctr_index"] < cfg.fatigue_index_threshold).all():
                last = ev.iloc[-1]
                found = {
                    "week": int(row.age_week),
                    "day": int((row.age_week - 1) * 7 + 1),
                    "index_at_onset": float(row.ctr_index),
                    "last_week": int(last["age_week"]),
                    "last_index": float(last["ctr_index"]),
                }
                break
        onset[p] = found
        if found:
            late = d[(d["platform"] == p) & (d["age_week"] >= found["week"])]
            exposure.append(
                {
                    "platform": p,
                    "campaigns_past_onset": int(late["campaign_id"].nunique()),
                    "spend_past_onset": float(late["spend"].sum()),
                    "share_of_platform_spend": safe_div(late["spend"].sum(), d.loc[d["platform"] == p, "spend"].sum()),
                    "clicks_below_launch_rate": float(late["expected_clicks"].sum() - late["clicks"].sum()),
                }
            )
    return {"curve": g, "onset": onset, "exposure": exposure}
