"""Where live systems plug in.

NOT IMPLEMENTED. This file exists to show the seam, not to pretend it works.
Each adapter below names the system it would call and the canonical columns it
must return. None of them hold credentials or make network calls.

Going live means implementing these four methods. The analysis engine, the
guardrails, the MCP server and the brief do not change.
"""
from __future__ import annotations

import pandas as pd

from .base import DataSource

NOT_BUILT = (
    "Live connector not implemented in this prototype. "
    "Run with --source csv to use the sample datasets."
)


class LiveSource(DataSource):
    """Composes ad-platform and CRM adapters into the canonical tables.

    Planned mapping (to confirm against Harvey's actual stack):

    fetch_daily
        Spend, impressions and clicks per campaign per day from the Google
        Ads, LinkedIn Marketing and Meta Marketing reporting APIs (or a
        warehouse table that already lands them). Conversions, qualified
        leads, opportunities, pipeline and ARR joined from the CRM by campaign
        id. attribution_status derived from lead/opportunity age.

    fetch_campaigns
        Campaign metadata from each ad platform, lifetime outcomes from the
        CRM. Audience, theme and objective parsed from the naming convention
        and normalized with the same alias map the CSV connector uses.

    fetch_experiments
        The team's experiment log (sheet, Notion database or warehouse table).

    fetch_creatives
        The creative library or DAM export.
    """

    name = "live"
    is_synthetic = False

    def fetch_campaigns(self) -> pd.DataFrame:
        raise NotImplementedError(NOT_BUILT)

    def fetch_daily(self) -> pd.DataFrame:
        raise NotImplementedError(NOT_BUILT)

    def fetch_experiments(self) -> pd.DataFrame:
        raise NotImplementedError(NOT_BUILT)

    def fetch_creatives(self) -> pd.DataFrame:
        raise NotImplementedError(NOT_BUILT)
