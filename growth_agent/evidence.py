"""The evidence pack: the only facts the agent is allowed to cite.

Every number that can appear in a brief is computed here by deterministic code
and given a stable id. The language model layer receives this pack and must
reference ids, which is what makes each claim traceable and checkable.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .analysis.metrics import to_jsonable

# How much weight a reader should put on an item.
RELIABILITY = {
    "final": "Settled data. Safe to act on.",
    "provisional": "Inside the attribution lag window. Will still change.",
    "observational": "A pattern across campaigns, not a controlled test. Shows where to test, not what is true.",
    "modeled": "An estimate from a stated formula. Not an observed result.",
    "data_quality": "A known problem with the data and how the agent handles it.",
}


@dataclass
class Evidence:
    id: str
    title: str
    statement: str
    source: str
    reliability: str
    data: Any = None
    caveats: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return to_jsonable(
            {
                "id": self.id,
                "title": self.title,
                "statement": self.statement,
                "source": self.source,
                "reliability": self.reliability,
                "caveats": self.caveats,
                "data": self.data,
            }
        )


class EvidencePack:
    def __init__(self) -> None:
        self._items: dict[str, Evidence] = {}

    def add(
        self,
        id: str,
        title: str,
        statement: str,
        source: str,
        reliability: str,
        data: Any = None,
        caveats: list[str] | None = None,
    ) -> str:
        if reliability not in RELIABILITY:
            raise ValueError(f"Unknown reliability '{reliability}'")
        if id in self._items:
            raise ValueError(f"Duplicate evidence id '{id}'")
        self._items[id] = Evidence(id, title, statement, source, reliability, data, caveats or [])
        return id

    def get(self, id: str) -> Evidence:
        return self._items[id]

    def has(self, id: str) -> bool:
        return id in self._items

    def ids(self) -> list[str]:
        return list(self._items)

    def items(self) -> list[Evidence]:
        return list(self._items.values())

    def as_list(self) -> list[dict]:
        return [e.as_dict() for e in self._items.values()]
