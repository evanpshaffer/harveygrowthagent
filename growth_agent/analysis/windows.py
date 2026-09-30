"""Which dates count as 'last week', and which dates can be trusted."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ..config import Config


@dataclass(frozen=True)
class Windows:
    as_of: pd.Timestamp          # latest date in the data
    week_start: pd.Timestamp     # reporting week, inclusive
    week_end: pd.Timestamp
    prior_start: pd.Timestamp    # comparison week, inclusive
    prior_end: pd.Timestamp
    immature_start: pd.Timestamp  # first date whose downstream data is unsettled
    immature_basis: str          # "source flag" or "config fallback"

    def in_week(self, dates: pd.Series) -> pd.Series:
        return (dates >= self.week_start) & (dates <= self.week_end)

    def in_prior(self, dates: pd.Series) -> pd.Series:
        return (dates >= self.prior_start) & (dates <= self.prior_end)

    def is_mature(self, dates: pd.Series) -> pd.Series:
        return dates < self.immature_start

    def as_dict(self) -> dict:
        f = lambda d: d.strftime("%Y-%m-%d")
        return {
            "as_of": f(self.as_of),
            "reporting_week": [f(self.week_start), f(self.week_end)],
            "prior_week": [f(self.prior_start), f(self.prior_end)],
            "immature_from": f(self.immature_start),
            "immature_days": int((self.as_of - self.immature_start).days) + 1,
            "immature_basis": self.immature_basis,
        }


def build_windows(daily: pd.DataFrame, cfg: Config, as_of: str | None = None) -> Windows:
    """Derive the reporting and maturity windows from the data itself.

    as_of defaults to the latest date present, which is how the agent would
    behave on a live feed: it reports on the most recent complete 7 days it
    has been given.
    """
    end = pd.Timestamp(as_of) if as_of else daily["date"].max()
    week_start = end - pd.Timedelta(days=cfg.week_days - 1)
    prior_end = week_start - pd.Timedelta(days=1)
    prior_start = prior_end - pd.Timedelta(days=cfg.week_days - 1)

    flagged = daily.loc[
        (daily["attribution_status"].fillna("").str.lower() == "immature") & (daily["date"] <= end),
        "date",
    ]
    if len(flagged):
        immature_start, basis = flagged.min(), "source flag"
    else:
        immature_start = end - pd.Timedelta(days=cfg.lead_maturity_days - 1)
        basis = "config fallback"

    return Windows(end, week_start, end, prior_start, prior_end, immature_start, basis)
