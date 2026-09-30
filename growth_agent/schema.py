"""The canonical data contract.

Every connector, whether it reads a CSV or calls a live API, must return these
four tables in this shape. The analysis engine only ever sees canonical tables,
which is what makes the data source swappable.
"""
from __future__ import annotations

import pandas as pd

# column -> kind ("str", "num", "date"). All listed columns are required.
CAMPAIGNS = {
    "campaign_id": "str",
    "campaign_name": "str",
    "platform": "str",
    "region": "str",
    "audience_raw": "str",
    "audience": "str",
    "objective": "str",
    "theme": "str",
    "format": "str",
    "creative_id": "str",
    "cta": "str",
    "launch_date": "date",
    "end_date": "date",
    "daily_budget": "num",
    "linked_experiment_id": "str",
    "data_quality_flag": "str",
    "spend": "num",
    "impressions": "num",
    "clicks": "num",
    "conversions": "num",
    "qualified_leads": "num",
    "opportunities": "num",
    "pipeline": "num",
    "arr": "num",
}

DAILY = {
    "date": "date",
    "campaign_id": "str",
    "platform": "str",
    "audience": "str",
    "region": "str",
    "objective": "str",
    "theme": "str",
    "creative_id": "str",
    "creative_age_days": "num",
    "spend": "num",
    "impressions": "num",
    "clicks": "num",
    "conversions": "num",
    "qualified_leads": "num",
    "opportunities": "num",
    "pipeline": "num",
    "arr": "num",
    "attribution_status": "str",
    "data_quality_flag": "str",
}

EXPERIMENTS = {
    "experiment_id": "str",
    "start_date": "date",
    "platform": "str",
    "variable_tested": "str",
    "hypothesis": "str",
    "theme": "str",
    "result": "str",
    "lift_pct": "num",
    "confidence": "str",
    "runtime_days": "num",
    "sample_size": "num",
    "primary_metric": "str",
    "notes": "str",
}

CREATIVES = {
    "creative_id": "str",
    "theme": "str",
    "format": "str",
    "audience_group": "str",
    "primary_message": "str",
    "first_used_date": "date",
    "times_used": "num",
    "status": "str",
    "notes": "str",
}

TABLES = {
    "campaigns": (CAMPAIGNS, ["campaign_id"]),
    "daily": (DAILY, ["date", "campaign_id"]),
    "experiments": (EXPERIMENTS, ["experiment_id"]),
    "creatives": (CREATIVES, ["creative_id"]),
}

# Columns where a missing value is meaningful (CRM lag) and must be preserved
# as missing rather than filled with zero.
NULLABLE_NUMERIC = {"pipeline", "arr"}
# Spend and delivery can never be negative or missing.
NON_NEGATIVE = {"spend", "impressions", "clicks", "conversions", "qualified_leads", "opportunities"}


class SchemaError(ValueError):
    """Raised when a connector returns data that breaks the contract."""


def conform(table: str, df: pd.DataFrame) -> pd.DataFrame:
    """Validate and coerce a connector's output to the canonical contract.

    Fails loudly on structural problems (missing columns, duplicate keys,
    negative spend). Tolerates the imperfections the business expects
    (missing CRM values, blank flags) and preserves them for the quality audit.
    """
    spec, key = TABLES[table]
    missing = [c for c in spec if c not in df.columns]
    if missing:
        raise SchemaError(f"{table}: missing required columns {missing}")

    out = df[list(spec)].copy()
    for col, kind in spec.items():
        if kind == "date":
            out[col] = pd.to_datetime(out[col], errors="coerce")
        elif kind == "num":
            out[col] = pd.to_numeric(out[col], errors="coerce")
        else:
            out[col] = out[col].astype("object").where(out[col].notna(), None)
            out[col] = out[col].map(lambda v: v.strip() if isinstance(v, str) else v)
            out[col] = out[col].map(lambda v: None if v == "" else v)

    if out[key].isna().any().any():
        raise SchemaError(f"{table}: null values in key columns {key}")
    if out.duplicated(key).any():
        raise SchemaError(f"{table}: duplicate rows for key {key}")

    for col in NON_NEGATIVE & set(spec):
        if out[col].isna().any():
            raise SchemaError(f"{table}: {col} has missing values")
        if (out[col] < 0).any():
            raise SchemaError(f"{table}: {col} has negative values")

    return out.reset_index(drop=True)
