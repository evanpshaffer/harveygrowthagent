"""Data quality audit.

Runs before any analysis. Each check states what is wrong, how big it is, and
what the agent does about it, so imperfect data changes how confident the
agent is instead of silently changing its answers.
"""
from __future__ import annotations

import pandas as pd

from ..config import Config
from ..connectors.base import Dataset
from ..connectors.csv_source import normalize_audience
from ..evidence import EvidencePack
from .metrics import SUM_COLS, safe_div
from .windows import Windows


def _pct(v: float | None, digits: int = 0) -> str:
    return "n/a" if v is None else f"{v * 100:.{digits}f}%"


def immature_flag(campaigns: pd.DataFrame) -> pd.Series:
    """True for campaigns the source marks as having unsettled attribution."""
    return campaigns["data_quality_flag"].fillna("").str.contains("immature", case=False)


def lag_check(ds: Dataset, w: Windows, cfg: Config) -> dict:
    """Measure attribution lag inside the campaigns that span the boundary.

    Compares each campaign's own rates in the immature window against its own
    rates in the weeks just before, so campaign mix cannot explain the gap.
    """
    d = ds.daily
    base_start = w.immature_start - pd.Timedelta(days=cfg.baseline_days)
    imm = d[(d["date"] >= w.immature_start) & (d["date"] <= w.as_of)]
    ids = imm["campaign_id"].unique()
    base = d[(d["campaign_id"].isin(ids)) & (d["date"] >= base_start) & (d["date"] < w.immature_start)]

    def agg(x: pd.DataFrame) -> dict:
        return {
            "clicks": float(x["clicks"].sum()),
            "conversions": float(x["conversions"].sum()),
            "qualified_leads": float(x["qualified_leads"].sum()),
            "cvr_pct": (safe_div(x["conversions"].sum(), x["clicks"].sum()) or 0) * 100,
            "ql_rate": safe_div(x["qualified_leads"].sum(), x["conversions"].sum()),
        }

    a, b = agg(imm), agg(base)
    # Expected outcomes if each campaign had kept its own baseline rates.
    exp_conv = exp_ql = 0.0
    act_conv = act_ql = 0.0
    lower = comparable = 0
    for cid in ids:
        ai, bi = agg(imm[imm["campaign_id"] == cid]), agg(base[base["campaign_id"] == cid])
        if bi["clicks"] and bi["conversions"]:
            exp_conv += ai["clicks"] * bi["conversions"] / bi["clicks"]
            act_conv += ai["conversions"]
        if bi["conversions"] and bi["qualified_leads"]:
            exp_ql += ai["conversions"] * bi["qualified_leads"] / bi["conversions"]
            act_ql += ai["qualified_leads"]
            if ai["ql_rate"] is not None:
                comparable += 1
                lower += ai["ql_rate"] < bi["ql_rate"]
    return {
        "campaigns_checked": int(len(ids)),
        "campaigns_with_lower_ql_rate": int(lower),
        "campaigns_comparable": int(comparable),
        "immature": a,
        "baseline": b,
        "conversion_completeness": safe_div(act_conv, exp_conv),
        "ql_completeness": safe_div(act_ql, exp_ql),
    }


def audit(ds: Dataset, w: Windows, cfg: Config, pack: EvidencePack) -> None:
    c, d, e, cr = ds.campaigns, ds.daily, ds.experiments, ds.creatives

    # 1. Do the two performance tables agree? --------------------------------
    ratios = {col: safe_div(d[col].sum(), c[col].sum()) for col in SUM_COLS}
    delivery_ok = all(abs((ratios[k] or 0) - 1) < 0.001 for k in ("spend", "impressions", "clicks"))
    pack.add(
        "DQ.reconciliation",
        "Daily and summary files disagree on outcomes",
        (
            f"Spend, impressions and clicks {'reconcile exactly' if delivery_ok else 'do not reconcile'} "
            f"between the daily and summary tables, but the daily table carries only "
            f"{_pct(ratios['conversions'])} of conversions, {_pct(ratios['qualified_leads'])} of qualified leads, "
            f"{_pct(ratios['opportunities'])} of opportunities and {_pct(ratios['pipeline'], 1)} of pipeline."
        ),
        "campaign_summary + daily_campaign_performance",
        "data_quality",
        data={"daily_as_share_of_summary": ratios},
        caveats=[
            "Handling: lifetime efficiency (pipeline per dollar, cost per opportunity) comes from the campaign summary only.",
            "Handling: the daily table is used for delivery trends and for comparing a campaign with itself over time.",
            "Handling: outcome levels from the two tables are never combined in one calculation.",
            "Assumption A1: the summary is the CRM-reconciled record; daily outcomes are a partial same-day view.",
        ],
    )

    # 2. Campaigns whose daily outcome feed is empty -------------------------
    by_c = d.groupby("campaign_id")[["conversions", "opportunities"]].sum()
    j = c.set_index("campaign_id")[["platform", "conversions", "opportunities"]].join(by_c, rsuffix="_daily")
    no_conv = j[(j["conversions"] > 0) & (j["conversions_daily"] == 0)]
    no_opp = j[(j["opportunities"] > 0) & (j["opportunities_daily"] == 0)]
    pack.add(
        "DQ.daily_outcome_gaps",
        "Some campaigns have no daily outcome data at all",
        (
            f"{len(no_conv)} campaigns show zero conversions in the daily table while the summary credits them with "
            f"{int(no_conv['conversions'].sum()):,} ("
            + ", ".join(f"{n} on {k}" for k, n in no_conv["platform"].value_counts().items()) + "), and "
            f"{len(no_opp)} campaigns with opportunities in the summary show none in the daily table."
        ),
        "campaign_summary + daily_campaign_performance",
        "data_quality",
        data={
            "campaigns_missing_daily_conversions": sorted(no_conv.index.tolist()),
            "by_platform": no_conv["platform"].value_counts().to_dict(),
            "campaigns_missing_daily_opportunities": int(len(no_opp)),
        },
        caveats=["Handling: a zero in the daily outcome columns is treated as 'not reported', never as 'no result'."],
    )

    # 3. Missing CRM values ---------------------------------------------------
    miss = d[d["pipeline"].isna() | d["arr"].isna()]
    pack.add(
        "DQ.missing_crm",
        "Daily rows with missing CRM pipeline and ARR",
        (
            f"{len(miss)} of {len(d):,} daily rows ({_pct(safe_div(len(miss), len(d)), 1)}) across "
            f"{miss['campaign_id'].nunique()} campaigns have no pipeline or ARR value, covering "
            f"${miss['spend'].sum():,.0f} of spend and {int(miss['opportunities'].sum())} opportunities."
        ),
        "daily_campaign_performance",
        "data_quality",
        data={
            "rows": int(len(miss)),
            "campaigns": int(miss["campaign_id"].nunique()),
            "spend": float(miss["spend"].sum()),
            "opportunities_on_missing_rows": int(miss["opportunities"].sum()),
            "by_platform": miss["platform"].value_counts().to_dict(),
        },
        caveats=["Handling: missing values stay missing. They are excluded from pipeline rates and never filled with zero."],
    )

    # 4. Inconsistent audience labels ----------------------------------------
    messy = c[c["audience_raw"] != c["audience"]]
    ours = c["audience_raw"].map(normalize_audience)
    pack.add(
        "DQ.audience_labels",
        "Inconsistent audience labels",
        (
            f"{len(messy)} of {len(c)} campaigns use a non-standard audience label "
            f"({', '.join(sorted(messy['audience_raw'].unique().tolist()))}). The agent's alias map resolves "
            f"{int((ours == c['audience']).sum())} of {len(c)} campaigns to the same label as the source's cleaned field."
        ),
        "campaign_summary",
        "data_quality",
        data={"raw_to_canonical": messy.drop_duplicates("audience_raw").set_index("audience_raw")["audience"].to_dict()},
        caveats=["Handling: all analysis groups on the canonical label. An unknown label is surfaced, not guessed."],
    )

    # 5. Attribution lag ------------------------------------------------------
    lag = lag_check(ds, w, cfg)
    flagged = c[immature_flag(c)]
    pack.add(
        "DQ.attribution_lag",
        "Recent downstream data is incomplete",
        (
            f"Everything from {w.immature_start:%b %d} to {w.as_of:%b %d} is inside the attribution lag window "
            f"({w.immature_basis}). Measured against each campaign's own prior {cfg.baseline_days} days, conversions in "
            f"the window are {_pct(lag['conversion_completeness'])} of what their clicks would normally produce, but "
            f"qualified leads are only {_pct(lag['ql_completeness'])} of what their conversions would normally produce "
            f"({lag['campaigns_with_lower_ql_rate']} of {lag['campaigns_comparable']} comparable campaigns are below "
            f"their own baseline). Lead capture is current; qualification and everything after it is not. "
            f"{len(flagged)} campaigns carry the immature flag in the summary."
        ),
        "daily_campaign_performance + campaign_summary",
        "data_quality",
        data={**lag, "immature_campaign_ids": sorted(flagged["campaign_id"].tolist())},
        caveats=[
            "Handling: for the reporting week only spend, impressions, clicks and conversions are treated as final.",
            "Handling: qualified leads, opportunities and pipeline for the window are shown as provisional and never used to judge performance.",
            "Handling: campaigns flagged immature are excluded from efficiency benchmarks.",
        ],
    )

    # 6. Experiment links -----------------------------------------------------
    linked = c.dropna(subset=["linked_experiment_id"]).merge(
        e, left_on="linked_experiment_id", right_on="experiment_id", suffixes=("", "_exp")
    )
    exp_end = linked["start_date"] + pd.to_timedelta(linked["runtime_days"], unit="D")
    overlap = (linked["start_date"] <= linked["end_date"]) & (exp_end >= linked["launch_date"])
    plat_mismatch = linked["platform"] != linked["platform_exp"]
    pack.add(
        "DQ.experiment_links",
        "Campaign-to-experiment links are unreliable",
        (
            f"Of {len(linked)} campaigns linked to an experiment, {int(plat_mismatch.sum())} point to an experiment "
            f"that ran on a different platform and {int((~overlap).sum())} did not overlap the experiment's dates."
        ),
        "campaign_summary + experiment_history",
        "data_quality",
        data={
            "linked_campaigns": int(len(linked)),
            "platform_mismatch": int(plat_mismatch.sum()),
            "no_date_overlap": int((~overlap).sum()),
            "clean_links": int((~plat_mismatch & overlap).sum()),
        },
        caveats=["Handling: linked_experiment_id is not used to attribute campaign results to an experiment."],
    )

    # 7. Creative age means campaign age -------------------------------------
    m = d.merge(c[["campaign_id", "launch_date"]], on="campaign_id")
    same = ((m["date"] - m["launch_date"]).dt.days + 1 == m["creative_age_days"]).mean()
    use = c.groupby("creative_id").agg(
        campaigns=("campaign_id", "count"), first=("launch_date", "min"), last=("end_date", "max")
    )
    use["exposure_days"] = (use["last"] - use["first"]).dt.days + 1
    reused = use[use["campaigns"] > 1]
    pack.add(
        "DQ.creative_age",
        "creative_age_days measures campaign age, not creative exposure",
        (
            f"creative_age_days equals days since campaign launch in {_pct(same)} of rows and tops out at "
            f"{int(d['creative_age_days'].max())} days, yet {len(reused)} creatives ran in more than one campaign and "
            f"the most reused have been in market for up to {int(use['exposure_days'].max())} days."
        ),
        "daily_campaign_performance + campaign_summary + creative_library",
        "data_quality",
        data={
            "share_equal_to_campaign_age": float(same),
            "reused_creatives": int(len(reused)),
            "max_true_exposure_days": int(use["exposure_days"].max()),
        },
        caveats=["Handling: fatigue is measured within a campaign. True audience exposure to a reused creative is longer than the field suggests."],
    )

    # 8. Creative format mismatches -------------------------------------------
    f = c.merge(cr[["creative_id", "format"]], on="creative_id", suffixes=("", "_library"))
    mism = f[f["format"] != f["format_library"]]
    non_google = mism[mism["platform"] != "Google"]
    pack.add(
        "DQ.creative_format",
        "Campaign format does not always match the creative library",
        (
            f"{len(mism)} campaigns report a format that differs from their creative's library format. "
            f"{len(mism) - len(non_google)} are Google campaigns, where the field holds the ad type (RSA, Responsive Display) "
            f"rather than the creative format. {len(non_google)} are genuine mismatches on other platforms "
            f"({', '.join(non_google['campaign_id'].tolist()) or 'none'})."
        ),
        "campaign_summary + creative_library",
        "data_quality",
        data={"mismatched": int(len(mism)), "non_google": non_google["campaign_id"].tolist()},
        caveats=["Handling: format comparisons exclude Google."],
    )

    # 9. What the source itself flags ------------------------------------------
    tokens = (
        c["data_quality_flag"].dropna().str.split(";").explode().str.strip().value_counts().to_dict()
    )
    pack.add(
        "DQ.source_flags",
        "Flags carried in the source data",
        "Campaign-level flags in the summary: " + ", ".join(f"{k} ({v})" for k, v in tokens.items()) + ".",
        "campaign_summary",
        "data_quality",
        data=tokens,
    )
