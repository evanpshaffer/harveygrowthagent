"""The shape of the Weekly Experimentation Brief the model must submit."""
from __future__ import annotations

from pydantic import BaseModel, Field

from ..guardrails import ExperimentProposal


class Claim(BaseModel):
    """One statement in the brief, tied to the evidence that supports it."""

    text: str = Field(description="One or two plain sentences. Every number must appear in the cited evidence.")
    evidence_ids: list[str] = Field(min_length=1, description="Ids of the evidence items this statement rests on.")


class ExperimentRecommendation(BaseModel):
    rank: int = Field(ge=1, le=3, description="1 is the highest-impact test.")
    signal_id: str | None = Field(default=None, description="The signal this test responds to, e.g. SIG.01.")
    rationale: Claim = Field(description="Why this test, now. Cites evidence.")
    expected_learning: str = Field(description="The decision this test unlocks, whichever way it comes out.")
    proposal: ExperimentProposal


class Brief(BaseModel):
    headline: Claim = Field(description="The single most important thing for the team to know this week.")
    what_happened: list[Claim] = Field(min_length=2, max_length=5)
    why: list[Claim] = Field(min_length=2, max_length=5)
    experiments: list[ExperimentRecommendation] = Field(min_length=3, max_length=3)
    creative_recommendations: list[Claim] = Field(min_length=2, max_length=5)
    risks_and_observations: list[Claim] = Field(min_length=2, max_length=5)


def inline_schema(model: type[BaseModel]) -> dict:
    """JSON schema with $ref/$defs inlined, for use as a tool input schema."""
    schema = model.model_json_schema()
    defs = schema.pop("$defs", {})

    def walk(node):
        if isinstance(node, dict):
            if "$ref" in node:
                return walk(defs[node["$ref"].split("/")[-1]])
            # Drop pydantic's "title" annotations, but keep any real field that is named title.
            return {k: walk(v) for k, v in node.items() if not (k == "title" and isinstance(v, str))}
        if isinstance(node, list):
            return [walk(v) for v in node]
        return node

    return walk(schema)
