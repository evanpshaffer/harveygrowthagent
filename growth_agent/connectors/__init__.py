"""Connector registry. One line changes the data source for the whole agent."""
from __future__ import annotations

from .base import DataSource, Dataset
from .csv_source import CsvSource
from .live_source import LiveSource

SOURCES: dict[str, type[DataSource]] = {
    "csv": CsvSource,
    "live": LiveSource,
}


def get_source(name: str = "csv", **kwargs) -> DataSource:
    if name not in SOURCES:
        raise ValueError(f"Unknown source '{name}'. Available: {sorted(SOURCES)}")
    return SOURCES[name](**kwargs)


__all__ = ["DataSource", "Dataset", "CsvSource", "LiveSource", "get_source", "SOURCES"]
