"""Funnel arithmetic shared by every analysis module.

All ratios are recomputed from sums. Precomputed ratio columns in source data
are never averaged, because an average of ratios is not the ratio of totals.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd

SUM_COLS = [
    "spend",
    "impressions",
    "clicks",
    "conversions",
    "qualified_leads",
    "opportunities",
    "pipeline",
    "arr",
]


def safe_div(num: float, den: float) -> float | None:
    """Division that returns None instead of inf/NaN when the base is empty."""
    if den is None or num is None:
        return None
    if isinstance(den, float) and math.isnan(den):
        return None
    if den == 0:
        return None
    return float(num) / float(den)


def pct_change(new: float | None, old: float | None) -> float | None:
    """Percent change from old to new, or None when there is no base."""
    ratio = safe_div((new or 0) - (old or 0), old) if old else None
    return None if ratio is None else ratio * 100


def rates(t: dict[str, float]) -> dict[str, float | None]:
    """Derived funnel metrics from a dict of summed columns."""
    return {
        "ctr_pct": _scale(safe_div(t["clicks"], t["impressions"]), 100),
        "cpc": safe_div(t["spend"], t["clicks"]),
        "cvr_pct": _scale(safe_div(t["conversions"], t["clicks"]), 100),
        "cpl": safe_div(t["spend"], t["conversions"]),
        "ql_rate": safe_div(t["qualified_leads"], t["conversions"]),
        "cost_per_ql": safe_div(t["spend"], t["qualified_leads"]),
        "opp_rate": safe_div(t["opportunities"], t["qualified_leads"]),
        "cost_per_opp": safe_div(t["spend"], t["opportunities"]),
        "pipeline_per_dollar": safe_div(t["pipeline"], t["spend"]),
        "arr_per_dollar": safe_div(t["arr"], t["spend"]),
    }


def _scale(v: float | None, k: float) -> float | None:
    return None if v is None else v * k


def totals(df: pd.DataFrame) -> dict[str, Any]:
    """Sum the funnel columns of a frame and attach derived rates."""
    t = {c: float(df[c].sum()) for c in SUM_COLS if c in df.columns}
    for c in SUM_COLS:
        t.setdefault(c, 0.0)
    t.update(rates(t))
    t["campaigns"] = int(df["campaign_id"].nunique()) if "campaign_id" in df.columns else None
    return t


def summarize(df: pd.DataFrame, by: str | list[str]) -> pd.DataFrame:
    """Group, sum, and recompute rates. Sorted by spend, descending."""
    keys = [by] if isinstance(by, str) else list(by)
    cols = [c for c in SUM_COLS if c in df.columns]
    g = df.groupby(keys, observed=True)[cols].sum()
    g["campaigns"] = df.groupby(keys, observed=True)["campaign_id"].nunique()
    derived = pd.DataFrame([rates(row) for row in g.to_dict("records")], index=g.index)
    out = pd.concat([g, derived], axis=1).reset_index()
    total_spend = out["spend"].sum()
    total_pipe = out["pipeline"].sum()
    out["spend_share"] = out["spend"] / total_spend if total_spend else np.nan
    out["pipeline_share"] = out["pipeline"] / total_pipe if total_pipe else np.nan
    return out.sort_values("spend", ascending=False).reset_index(drop=True)


def to_jsonable(obj: Any) -> Any:
    """Recursively convert pandas/numpy values into plain JSON types."""
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [to_jsonable(v) for v in obj]
    if isinstance(obj, pd.DataFrame):
        return to_jsonable(obj.to_dict("records"))
    if isinstance(obj, pd.Series):
        return to_jsonable(obj.to_dict())
    if isinstance(obj, (pd.Timestamp,)):
        return None if pd.isna(obj) else obj.strftime("%Y-%m-%d")
    if isinstance(obj, pd.Period):
        return str(obj)
    if obj is pd.NaT:
        return None
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        f = float(obj)
        if math.isnan(f) or math.isinf(f):
            return None
        return round(f, 4)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if obj is pd.NA:
        return None
    return obj
