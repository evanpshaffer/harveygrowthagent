"""The data source is swappable, and bad data fails loudly."""
import pandas as pd
import pytest

from growth_agent import schema
from growth_agent.connectors import SOURCES, CsvSource, DataSource, get_source
from growth_agent.connectors.csv_source import normalize_audience
from growth_agent.pipeline import build


def test_csv_source_returns_the_four_canonical_tables():
    ds = CsvSource().load()
    assert list(ds.campaigns.columns) == list(schema.CAMPAIGNS)
    assert list(ds.daily.columns) == list(schema.DAILY)
    assert (len(ds.campaigns), len(ds.daily), len(ds.experiments), len(ds.creatives)) == (128, 5691, 18, 32)
    assert ds.is_synthetic


def test_missing_column_is_rejected():
    df = CsvSource().fetch_daily().drop(columns=["spend"])
    with pytest.raises(schema.SchemaError, match="missing required columns"):
        schema.conform("daily", df)


def test_negative_spend_is_rejected():
    df = CsvSource().fetch_daily()
    df.loc[0, "spend"] = -5
    with pytest.raises(schema.SchemaError, match="negative"):
        schema.conform("daily", df)


def test_duplicate_keys_are_rejected():
    df = CsvSource().fetch_campaigns()
    with pytest.raises(schema.SchemaError, match="duplicate"):
        schema.conform("campaigns", pd.concat([df, df.head(1)]))


def test_missing_crm_values_stay_missing():
    ds = CsvSource().load()
    assert ds.daily["pipeline"].isna().sum() == 45
    assert ds.daily["arr"].isna().sum() == 45


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("LF ENT", "Law Firm - Enterprise"),
        ("Law Firm MM", "Law Firm - Mid-Market"),
        ("IH MM", "In-House - Mid-Market"),
        ("Enterprise Legal", "In-House - Enterprise"),
        ("Law Firm - Enterprise", "Law Firm - Enterprise"),
    ],
)
def test_audience_labels_are_normalized(raw, expected):
    assert normalize_audience(raw) == expected


def test_analysis_only_sees_canonical_audiences(result):
    assert set(result.dataset.campaigns["audience"]) == {
        "Law Firm - Enterprise", "Law Firm - Mid-Market", "In-House - Enterprise", "In-House - Mid-Market",
    }


def test_live_source_is_honest_about_not_being_built():
    with pytest.raises(NotImplementedError):
        get_source("live").load()


def test_a_new_source_plugs_in_without_touching_analysis(result):
    """Swap the CSV connector for a different one and get the same answers."""

    class ShuffledSource(DataSource):
        name = "in_memory"
        is_synthetic = True
        _csv = CsvSource()

        def fetch_campaigns(self):
            return self._csv.fetch_campaigns().sample(frac=1, random_state=1)

        def fetch_daily(self):
            return self._csv.fetch_daily().sample(frac=1, random_state=1)

        def fetch_experiments(self):
            return self._csv.fetch_experiments()

        def fetch_creatives(self):
            return self._csv.fetch_creatives()

    SOURCES["in_memory"] = ShuffledSource
    try:
        other = build(source="in_memory")
    finally:
        SOURCES.pop("in_memory")
    assert other.dataset.source_name == "in_memory"
    assert [s["title"] for s in other.signals] == [s["title"] for s in result.signals]
    assert other.pack.get("SEG.objective").statement == result.pack.get("SEG.objective").statement
