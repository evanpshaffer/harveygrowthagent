"""Claim checker: every number the model writes must exist in the evidence it cites.

The model is never trusted to do arithmetic or to remember a figure. This
module extracts each number from a sentence and looks for it in the cited
evidence items (their statements, caveats and data). A number that cannot be
found is reported back, and the claim does not ship until it is fixed.
"""
from __future__ import annotations

import re
from typing import Any, Iterable

from ..config import Config
from ..evidence import EvidencePack

# Things that look like numbers but are identifiers or dates.
IDS = re.compile(r"\b(?:[A-Z]{2,8}\.[A-Za-z0-9_.]*[A-Za-z0-9_]|E\d{3}|CR\d{3}|C\d{3}|A\d)\b")
DATES = re.compile(
    r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}(?:\s*(?:to|through|-)\s*\d{1,2})?(?:,\s*\d{4})?"
    r"|\b\d{4}-\d{2}-\d{2}\b|\b20\d{2}\b"
)
NUMBER = re.compile(r"(?<![\w.,])(\d[\d,]*(?:\.\d+)?)\s?(%|[kKmM]\b)?")
SCALE = {"k": 1e3, "K": 1e3, "m": 1e6, "M": 1e6}
DOWNSTREAM = re.compile(r"pipeline|opportunit|qualified lead|\barr\b|revenue", re.I)


def extract_numbers(text: str) -> list[tuple[str, float, int]]:
    """Return (as written, value, decimals) for each number in the text."""
    clean = DATES.sub(" ", IDS.sub(" ", text))
    out = []
    for m in NUMBER.finditer(clean):
        raw = m.group(1).rstrip(",")
        body = raw.replace(",", "")
        decimals = len(body.split(".")[1]) if "." in body else 0
        scale = SCALE.get(m.group(2) or "", 1.0)
        out.append((m.group(0).strip(), float(body) * scale, decimals if scale == 1.0 else -1))
    return out


def _numeric_leaves(node: Any) -> Iterable[float]:
    if isinstance(node, bool) or node is None:
        return
    if isinstance(node, (int, float)):
        yield float(node)
    elif isinstance(node, str):
        for _, value, _ in extract_numbers(node):
            yield value
    elif isinstance(node, dict):
        for v in node.values():
            yield from _numeric_leaves(v)
    elif isinstance(node, (list, tuple)):
        for v in node:
            yield from _numeric_leaves(v)


def evidence_numbers(pack: EvidencePack, ids: Iterable[str]) -> set[float]:
    """Every number that appears anywhere in the given evidence items."""
    values: set[float] = set()
    for eid in ids:
        if pack.has(eid):
            values.update(_numeric_leaves(pack.get(eid).as_dict()))
    return values


def context_numbers(cfg: Config, windows: dict) -> set[float]:
    """Numbers that are rules or dates rather than findings: thresholds and window lengths."""
    return {
        float(v)
        for v in (
            cfg.week_days, windows["immature_days"], cfg.min_runtime_days, cfg.min_sample_size,
            cfg.min_planned_runtime_days, cfg.max_daily_budget, cfg.max_total_test_budget,
            cfg.min_expected_opportunities, cfg.recent_weeks, cfg.baseline_days,
            cfg.min_planned_runtime_days + cfg.lead_maturity_days,   # the earliest valid read day
            cfg.max_slate_budget, cfg.max_submit_attempts,
        )
    }


def _matches(value: float, decimals: int, candidates: set[float]) -> bool:
    for c in candidates:
        for cand in (c, c * 100):  # a share stored as 0.49 may be written as 49%
            cand = abs(cand)
            if decimals < 0:  # written with k or M: allow 1% rounding
                if value and abs(cand - value) / value <= 0.01:
                    return True
            elif abs(cand - value) <= 0.5 * 10 ** (-decimals) + 1e-9:
                return True
    return False


def unverified_numbers(text: str, candidates: set[float]) -> list[str]:
    """Numbers in the text that do not appear in the candidate set."""
    return [raw for raw, value, decimals in extract_numbers(text) if not _matches(value, decimals, candidates)]


def check_claim(text: str, evidence_ids: list[str], pack: EvidencePack, extra: set[float] | None = None) -> list[str]:
    """Problems with one claim. Empty list means it can ship."""
    problems = []
    missing = [e for e in evidence_ids if not pack.has(e)]
    if missing:
        problems.append(f"cites evidence that does not exist: {', '.join(missing)}")
    bad = unverified_numbers(text, evidence_numbers(pack, evidence_ids) | (extra or set()))
    if bad:
        problems.append(
            f"these numbers are not in the cited evidence ({', '.join(evidence_ids)}): {', '.join(bad)}. "
            "Cite the item that contains them, or remove them."
        )
    return problems


def mentions_downstream(text: str) -> bool:
    return bool(DOWNSTREAM.search(text))
