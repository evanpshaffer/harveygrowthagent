"""Sample-data connector: reads the four CSVs from the take-home."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..config import CONFIG
from .base import DataSource

DEFAULT_DIR = Path(__file__).resolve().parents[2] / "data" / "sample"

# Source column -> canonical column. This mapping is the only place that knows
# what the sample files call things.
CAMPAIGN_COLUMNS = {
    "total_spend": "spend",
    "audience": "audience_raw",
    "normalized_audience": "audience",
}


def normalize_audience(raw: str | None) -> str | None:
    """Map an inconsistent audience label to its canonical form."""
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return None
    key = " ".join(str(raw).lower().replace("-", " ").split())
    if key in CONFIG.audience_aliases:
        return CONFIG.audience_aliases[key]
    return str(raw).strip()


class CsvSource(DataSource):
    name = "sample_csv"
    is_synthetic = True

    def __init__(self, directory: str | Path = DEFAULT_DIR):
        self.directory = Path(directory)

    def _read(self, filename: str) -> pd.DataFrame:
        path = self.directory / filename
        if not path.exists():
            raise FileNotFoundError(f"Expected sample file at {path}")
        return pd.read_csv(path)

    def fetch_campaigns(self) -> pd.DataFrame:
        df = self._read("campaign_summary.csv").rename(columns=CAMPAIGN_COLUMNS)
        # Use the source's cleaned label when it exists, otherwise normalize.
        if "audience" not in df.columns:
            df["audience"] = df["audience_raw"].map(normalize_audience)
        else:
            df["audience"] = df["audience"].fillna(df["audience_raw"].map(normalize_audience))
        return df

    def fetch_daily(self) -> pd.DataFrame:
        df = self._read("daily_campaign_performance.csv")
        df["audience"] = df["audience"].map(normalize_audience)
        return df

    def fetch_experiments(self) -> pd.DataFrame:
        return self._read("experiment_history.csv")

    def fetch_creatives(self) -> pd.DataFrame:
        return self._read("creative_library.csv")
