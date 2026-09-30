"""Runs the whole deterministic pipeline: load, audit, analyze, signal."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from . import __version__
from .analysis import drivers, experiments, performance, quality, signals
from .analysis.metrics import to_jsonable
from .analysis.windows import Windows, build_windows
from .config import CONFIG, Config
from .connectors import Dataset, get_source
from .evidence import RELIABILITY, EvidencePack

ASSUMPTIONS = [
    {
        "id": "A1",
        "assumption": "The campaign summary is the CRM-reconciled record of lifetime outcomes. The daily table is a partial, same-day view of outcomes.",
        "why": "Spend and clicks match exactly across the two tables but daily outcomes are a small fraction of summary outcomes.",
        "if_wrong": "If the daily table is the truth, every efficiency number in the brief is overstated and the first job is fixing the summary.",
    },
    {
        "id": "A2",
        "assumption": "'Last week' is the 7 days ending on the latest date in the data, compared with the 7 days before.",
        "why": "It is what a live weekly run would see. Full 7-day windows absorb the weekday pattern.",
        "if_wrong": "The window is defined in one function (build_windows). Nothing else changes.",
    },
    {
        "id": "A3",
        "assumption": "Anything the source flags as immature is excluded from performance judgments and efficiency benchmarks.",
        "why": "Qualified leads inside the window are about a quarter complete when measured against each campaign's own history.",
        "if_wrong": "If the lag is longer than the flag suggests, recent campaigns will look worse than they are for longer.",
    },
    {
        "id": "A4",
        "assumption": "Pipeline per dollar is the primary success metric, supported by cost per opportunity and ARR per dollar. CTR, CPC and cost per lead are diagnostics only.",
        "why": "The brief asks for qualified pipeline, opportunities and revenue over click metrics.",
        "if_wrong": "Change outcome_metrics in config. Rankings are recomputed.",
    },
    {
        "id": "A5",
        "assumption": "In the experiment log the first-named arm is the variant, so 'Win' on 'A vs B' means A beat B.",
        "why": "Every note in the log that names a winner is consistent with this reading.",
        "if_wrong": "The direction of each learning flips. Trust tiers do not change.",
    },
    {
        "id": "A6",
        "assumption": "Absolute dollar magnitudes are synthetic. Ratios between segments are the signal.",
        "why": "The data dictionary says the data is synthetic, and pipeline per dollar is implausibly high in absolute terms.",
        "if_wrong": "No change to rankings.",
    },
    {
        "id": "A7",
        "assumption": "An experiment needs at least 14 days and a sample of 100 to count as a read; a new test needs at least 28 days.",
        "why": "Two weekly cycles is the floor for any read, and pipeline outcomes need longer than lead outcomes.",
        "if_wrong": "These are defaults in config for the marketing lead to set.",
    },
    {
        "id": "A8",
        "assumption": "No proposed test may exceed the highest daily budget the team has already run, or a fixed total budget ceiling.",
        "why": "The agent should never ask for more exposure than the team has already chosen to take.",
        "if_wrong": "Raise the ceilings in config. Approval is still required for every launch.",
    },
]


@dataclass
class Result:
    dataset: Dataset
    windows: Windows
    pack: EvidencePack
    signals: list[dict]
    experiments: list[dict]
    config: Config

    def to_dict(self) -> dict:
        return to_jsonable(
            {
                "meta": {
                    "agent_version": __version__,
                    "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "source": self.dataset.source_name,
                    "synthetic_data": self.dataset.is_synthetic,
                    "rows": {
                        "campaigns": len(self.dataset.campaigns),
                        "daily": len(self.dataset.daily),
                        "experiments": len(self.dataset.experiments),
                        "creatives": len(self.dataset.creatives),
                    },
                },
                "windows": self.windows.as_dict(),
                "assumptions": ASSUMPTIONS,
                "reliability_levels": RELIABILITY,
                "signals": [
                    {k: s[k] for k in ("id", "rank", "type", "title", "statement", "strength", "evidence_ids", "test_angle", "cautions", "metrics")}
                    for s in self.signals
                ],
                "evidence": self.pack.as_list(),
            }
        )


def build(source: str = "csv", as_of: str | None = None, cfg: Config = CONFIG, **source_kwargs) -> Result:
    """Load data through the integration layer and produce the evidence pack.

    as_of re-windows the weekly read only. The campaign summary is a lifetime
    snapshot and cannot be rewound, so a historical as_of is for testing the
    windowing logic, not for reproducing a past brief.
    """
    ds = get_source(source, **source_kwargs).load()
    w = build_windows(ds.daily, cfg, as_of)
    pack = EvidencePack()
    quality.audit(ds, w, cfg, pack)
    performance.what_happened(ds, w, cfg, pack)
    ctx = drivers.why(ds, w, cfg, pack)
    exps = experiments.assess(ds, ctx["bench"], cfg, pack)
    sigs = signals.detect(ds, w, cfg, pack, ctx, exps)
    return Result(ds, w, pack, sigs, exps, cfg)
