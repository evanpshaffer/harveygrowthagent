"""The integration layer's single interface.

The agent never imports pandas.read_csv or an ads SDK directly. It asks a
DataSource for four canonical tables. Replacing sample files with live systems
means writing a new DataSource, and nothing downstream changes.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import pandas as pd

from .. import schema


@dataclass
class Dataset:
    """The four canonical tables plus where they came from."""

    campaigns: pd.DataFrame
    daily: pd.DataFrame
    experiments: pd.DataFrame
    creatives: pd.DataFrame
    source_name: str
    is_synthetic: bool


class DataSource(ABC):
    """Contract every data source implements."""

    name: str = "unnamed"
    is_synthetic: bool = False

    @abstractmethod
    def fetch_campaigns(self) -> pd.DataFrame:
        """One row per campaign with lifetime, CRM-reconciled outcomes."""

    @abstractmethod
    def fetch_daily(self) -> pd.DataFrame:
        """One row per campaign per day."""

    @abstractmethod
    def fetch_experiments(self) -> pd.DataFrame:
        """One row per historical experiment."""

    @abstractmethod
    def fetch_creatives(self) -> pd.DataFrame:
        """One row per creative concept."""

    def load(self) -> Dataset:
        """Fetch everything and enforce the canonical contract."""
        return Dataset(
            campaigns=schema.conform("campaigns", self.fetch_campaigns()),
            daily=schema.conform("daily", self.fetch_daily()),
            experiments=schema.conform("experiments", self.fetch_experiments()),
            creatives=schema.conform("creatives", self.fetch_creatives()),
            source_name=self.name,
            is_synthetic=self.is_synthetic,
        )
